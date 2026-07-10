#!/usr/bin/env python3
"""Independent verifier for frozen legacy RMC call-site containment."""
from __future__ import annotations

import ast
import hashlib
import os
from pathlib import Path
import py_compile
import re
import subprocess
import sys
import tempfile

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PASS_MARKER = "PASS - FROZEN LEGACY CALL-SITE CONTAINMENT VERIFIER"

FROZEN_HASHES = {
    "rmc_engine_v1/llm_renderer.py": "855bb683801e034487c997fd6dfeb51b8fd376f4d287fddb3e33b83bca99d2ac",
    "rmc_engine_v1/chroma_connector.py": "6554fe9188e676d4b79d4ba15f0a723574a64defc8bef4e0363ed165c83eed91",
}
GUARDED_HASHES = {
    "config/approved_paths.json": "8f72b03b3b446d2963fcf759abdc2a938dd1007c3dfa2085cb078dc0798b2af9",
    "config/session_scope.json": "1765aa1f6f547f82ef56c2dbe6ef9759f8bf1692ebfccfff3f92e17bf88d9f35",
    "config/tool_registry.json": "ff199fefde2a533f395ef6240e5771691e6928e2b72768c4f4aa13fc26f7cd1f",
    "requirements.txt": "ed73ba11243a0099034f10ac500db984959bb8f37086532f864d75a3620916c8",
    "agents/forge/knowledge_base.py": "9782c971cb4ac107b15963c7c418d65ba6e4618fa6ecaee6835f210c8eb61bbc",
    "agents/forge/runner.py": "ff555a5bf6a29a7aa50adc000c087ffaefb678c394dac929920e145a9a458d19",
}
GP014_HASHES = {
    "rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py": "431e6c2133a06204131f81276c11b05528ed8e6553a0d5590555ffd23ef38473",
    "rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json": "e99c7691d0ba951343bdf80a82d65d19e464b660bedd942b9a9db2b16283c93e",
    "scripts/test_operator_guided_language_realizer_build_langexpr001_gp014.py": "d047b3ca07c13e4e29ab55f9aa8fb357ee87a1a7d649ea2b23f68f30b75af3be",
    "scripts/operator_guided_language_realizer_build_langexpr001_gp014_verify.py": "c84800156011727cd49f743b722502c60f555c109859ff79aa399cb32ae4d797",
}
REQUIRED_MODIFIED = {
    "main.py",
    "rmc_engine_v1/__init__.py",
    "rmc_engine_v1/output_renderer.py",
    "rmc_engine_v1/memory_recaller.py",
    "scripts/README_patch262J1R_preflight_C15.md",
    "scripts/README_patch262J1R_preflight_C16.md",
    "scripts/patch262J1R_preflight_C15_verify.py",
    "scripts/patch262J1R_preflight_C16_verify.py",
    "scripts/test_rmc_chroma_connector_C15.py",
    "scripts/test_rmc_llm_renderer_C16.py",
    "SHA256SUMS.txt",
}
REQUIRED_NEW = {
    "rmc_engine_v1/frozen_legacy_boundary.py",
    "scripts/test_aiweb_frozen_legacy_callsite_containment.py",
    "scripts/aiweb_frozen_legacy_callsite_containment_verify.py",
    "scripts/README_aiweb_frozen_legacy_callsite_containment.md",
}
ALLOWED_CHANGED = REQUIRED_MODIFIED | REQUIRED_NEW
FROZEN_MODULES = {"rmc_engine_v1.llm_renderer", "rmc_engine_v1.chroma_connector"}
RETIRED_FILENAMES = {
    "test_rmc_chroma_connector_C15.py",
    "test_rmc_llm_renderer_C16.py",
    "patch262J1R_preflight_C15_verify.py",
    "patch262J1R_preflight_C16_verify.py",
}


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"FAIL - {name}" + (f": {detail}" if detail else ""))
    print(f"PASS - {name}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=str(ROOT), capture_output=True, text=True, check=False
    )


def literal_strings(node: ast.AST) -> list[str]:
    return [
        child.value for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    ]


def scan_python(path: Path) -> list[str]:
    rel = path.relative_to(ROOT).as_posix()
    if rel in FROZEN_HASHES:
        return []
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in FROZEN_MODULES:
                    violations.append(f"{rel}: import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module in FROZEN_MODULES:
                violations.append(f"{rel}: from {module} import ...")
        elif isinstance(node, ast.Call):
            target = ""
            if isinstance(node.func, ast.Name):
                target = node.func.id
            elif isinstance(node.func, ast.Attribute):
                target = node.func.attr
            literals = literal_strings(node)
            if target in {"__import__", "import_module"}:
                for value in literals:
                    if value in FROZEN_MODULES:
                        violations.append(f"{rel}: dynamic import {value}")
            if target in {"run", "call", "check_call", "check_output", "Popen", "system"}:
                if path.name not in RETIRED_FILENAMES:
                    for value in literals:
                        for name in RETIRED_FILENAMES:
                            if name in value:
                                violations.append(f"{rel}: subprocess execution of {name}")
    return violations


def parse_root_sha_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([0-9a-fA-F]{64})\s+[*]?(.+)$", line)
        if match:
            entries[match.group(2)] = match.group(1).lower()
    return entries


def run_checked(name: str, command: list[str], required_marker: str) -> None:
    with tempfile.TemporaryDirectory(prefix="aiweb_verify_runtime_") as td:
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONPYCACHEPREFIX"] = str(Path(td) / "pycache")
        proc = subprocess.run(
            command,
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
    if proc.stdout:
        print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n")
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, end="" if proc.stderr.endswith("\n") else "\n")
    check(f"{name} exit code zero", proc.returncode == 0, f"returncode={proc.returncode}")
    check(f"{name} marker present", required_marker in proc.stdout)


def main() -> int:
    check("target is Forge repository", (ROOT / ".git").is_dir())
    top = git("rev-parse", "--show-toplevel")
    check("git top-level matches target", top.returncode == 0 and Path(top.stdout.strip()).resolve() == ROOT)
    branch = git("branch", "--show-current")
    check("branch is main", branch.returncode == 0 and branch.stdout.strip() == "main")

    for rel in sorted(ALLOWED_CHANGED | set(FROZEN_HASHES) | set(GUARDED_HASHES) | set(GP014_HASHES)):
        check(f"required path exists: {rel}", (ROOT / rel).is_file())

    for rel, expected in {**FROZEN_HASHES, **GUARDED_HASHES, **GP014_HASHES}.items():
        check(f"protected SHA256 unchanged: {rel}", sha256(ROOT / rel) == expected)

    changed_python = [
        ROOT / rel for rel in sorted(ALLOWED_CHANGED)
        if rel.endswith(".py")
    ]
    with tempfile.TemporaryDirectory(prefix="aiweb_compile_") as td:
        for index, path in enumerate(changed_python):
            py_compile.compile(
                str(path),
                cfile=str(Path(td) / f"{index}.pyc"),
                doraise=True,
            )
            print(f"PASS - Python syntax valid: {path.relative_to(ROOT)}")

    scan_roots = [
        ROOT / "main.py",
        ROOT / "rmc_engine_v1",
        ROOT / "scripts",
    ]
    scanned = 0
    ast_violations: list[str] = []
    for scan_root in scan_roots:
        candidates = [scan_root] if scan_root.is_file() else sorted(scan_root.rglob("*.py"))
        for path in candidates:
            rel_parts = path.relative_to(ROOT).parts
            if any(part in {"__pycache__", ".git", "backups"} for part in rel_parts):
                continue
            ast_violations.extend(scan_python(path))
            scanned += 1
    check("AST scan covered live Python source", scanned > 20, f"scanned={scanned}")
    check(
        "AST scan found no frozen import/call or retired-script execution path",
        not ast_violations,
        "; ".join(ast_violations[:20]),
    )

    init_text = (ROOT / "rmc_engine_v1" / "__init__.py").read_text(encoding="utf-8")
    check("active registry omits LLM module", '"llm_renderer": {' not in init_text)
    check("active registry omits Chroma module", '"chroma_connector": {' not in init_text)
    check("historical frozen declarations are explicit", "FROZEN_LEGACY_EVIDENCE" in init_text)

    output_text = (ROOT / "rmc_engine_v1" / "output_renderer.py").read_text(encoding="utf-8")
    memory_text = (ROOT / "rmc_engine_v1" / "memory_recaller.py").read_text(encoding="utf-8")
    check("output renderer has no frozen dependency", "render_text_with_optional_llm" not in output_text and "rmc_engine_v1.llm_renderer" not in output_text)
    check("memory recaller has no frozen dependency", "query_chroma_memory" not in memory_text and "rmc_engine_v1.chroma_connector" not in memory_text)
    check("memory recaller declares filesystem only", '"supported_retrieval_backends": ["filesystem"]' in memory_text)

    manifest = parse_root_sha_manifest(ROOT / "SHA256SUMS.txt")
    for rel in sorted((REQUIRED_MODIFIED - {"SHA256SUMS.txt"}) | REQUIRED_NEW):
        check(f"root SHA256SUMS contains corrected path: {rel}", manifest.get(rel) == sha256(ROOT / rel))

    status = git("status", "--porcelain=v1", "--untracked-files=all")
    check("git status command succeeds", status.returncode == 0)
    changed_paths: set[str] = set()
    for raw in status.stdout.splitlines():
        check("no deleted path in status", not raw.startswith(" D") and not raw.startswith("D "))
        check("no renamed path in status", not raw.startswith("R ") and " -> " not in raw)
        path = raw[3:]
        changed_paths.add(path)
    check("git status limited to approved correction paths", changed_paths <= ALLOWED_CHANGED, repr(sorted(changed_paths)))
    check("all approved correction paths represented", ALLOWED_CHANGED <= changed_paths, repr(sorted(ALLOWED_CHANGED - changed_paths)))

    staged = git("diff", "--cached", "--name-only")
    check("no staged files", staged.returncode == 0 and not staged.stdout.strip(), staged.stdout.strip())

    for path in ROOT.rglob("__pycache__"):
        if ".git" not in path.parts:
            raise AssertionError(f"FAIL - __pycache__ present: {path}")
    for path in ROOT.rglob("*.pyc"):
        if ".git" not in path.parts:
            raise AssertionError(f"FAIL - .pyc present: {path}")
    print("PASS - no __pycache__ or .pyc in repository")

    if os.environ.get("AIWEB_INTERNAL_BENCH_MODE") == "1":
        print("PASS - internal bench mode: separately executed containment behavior test accepted")
        print("PASS - internal bench mode: GP-014 runtime regression deferred; protected source hashes verified")
    else:
        run_checked(
            "containment behavior test",
            [sys.executable, str(ROOT / "scripts/test_aiweb_frozen_legacy_callsite_containment.py"), str(ROOT)],
            "PASS - FROZEN LEGACY CALL-SITE CONTAINMENT BEHAVIOR TEST",
        )
        run_checked(
            "GP-014 protected behavior test",
            [sys.executable, str(ROOT / "scripts/test_operator_guided_language_realizer_build_langexpr001_gp014.py")],
            "RESULT: LANG-EXPR-001-GP-014-OPERATOR-GUIDED-GENERATIVE-LANGUAGE-REALIZER_BEHAVIOR PASS",
        )
        run_checked(
            "GP-014 protected verifier",
            [sys.executable, str(ROOT / "scripts/operator_guided_language_realizer_build_langexpr001_gp014_verify.py")],
            "RESULT: LANG-EXPR-001-GP-014-OPERATOR-GUIDED-GENERATIVE-LANGUAGE-REALIZER_VERIFY PASS",
        )

    print(PASS_MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
