#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

EXPECTED_BASE_HEAD = "cf2d5dc94113a857d0ffd53dd4710534df1aa55e"
EXPECTED_BASE_PARENT = "3b640f380b8633ce93143d178dcbee143503f03d"
EXPECTED_BASE_SUBJECT = "Slice 17 output expression boundary scaffold"

ALLOWED_NEW_PATHS = (
    "aiweb_gp014_preservation_decision_scaffold/__init__.py",
    "aiweb_gp014_preservation_decision_scaffold/core.py",
    "aiweb_gp014_preservation_decision_scaffold/gp014_reference.py",
    "aiweb_gp014_preservation_decision_scaffold/wrapper_decision.py",
    "aiweb_gp014_preservation_decision_scaffold/preservation_receipt.py",
    "aiweb_gp014_preservation_decision_scaffold/verify.py",
    "scripts/README_aiweb_slice18_gp014_preservation_decision_scaffold.md",
    "scripts/aiweb_slice18_gp014_preservation_decision_verify.py",
    "scripts/test_aiweb_slice18_gp014_preservation_decision_scaffold.py",
)

PROTECTED_HASHES = {
    "rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py": "431e6c2133a06204131f81276c11b05528ed8e6553a0d5590555ffd23ef38473",
    "rmc_engine_v1/general_pipeline/symbolic_math_operator_language_realizer.py": "f1f2486504bb987d705efee70d775c1549d3597f5153d30e87cbf11f38bedf1a",
    "rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json": "e99c7691d0ba951343bdf80a82d65d19e464b660bedd942b9a9db2b16283c93e",
    "scripts/test_operator_guided_language_realizer_build_langexpr001_gp014.py": "d047b3ca07c13e4e29ab55f9aa8fb357ee87a1a7d649ea2b23f68f30b75af3be",
    "scripts/operator_guided_language_realizer_build_langexpr001_gp014_verify.py": "c84800156011727cd49f743b722502c60f555c109859ff79aa399cb32ae4d797",
    "rmc_engine_v1/general_pipeline/gp015_ask_forge_trace_surface.py": "9449cdac60047d6d9dd4522e0d4128b72dd86485db225c21203dfd234ba53453",
    "aiweb_output_expression_boundary_scaffold/__init__.py": "35f61a64a3eeb1cac5ed5a2640540025f4d46b0486cc338ecc1ffdd30e932183",
}

FORBIDDEN_IMPORT_PREFIXES = (
    "rmc_engine_v1.general_pipeline.gp014_operator_guided_language_realizer",
    "rmc_engine_v1.general_pipeline.symbolic_math_operator_language_realizer",
    "rmc_engine_v1.general_pipeline.gp015_ask_forge_trace_surface",
    "rmc_engine_v1.renderer",
    "rmc_engine_v1.llm_renderer",
    "rmc_engine_v1.chroma_connector",
    "aiweb_output_expression_boundary_scaffold",
    "openai",
    "anthropic",
    "chromadb",
    "langchain",
    "faiss",
    "sklearn",
    "sentence_transformers",
    "transformers",
    "torch",
    "tensorflow",
    "requests",
    "httpx",
    "urllib",
    "socket",
    "sqlite3",
    "ollama",
    "llama_cpp",
)


def _run_git(repo: Path, *args: str) -> Tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except FileNotFoundError:
        return 127, "GIT_NOT_FOUND"
    return proc.returncode, proc.stdout.rstrip("\n")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _status_path(line: str) -> str:
    cleaned = line[3:] if len(line) > 3 else line
    if " -> " in cleaned:
        cleaned = cleaned.split(" -> ", 1)[1]
    return cleaned.strip()


def _status_lines(repo: Path) -> List[str]:
    code, output = _run_git(repo, "status", "--short")
    if code != 0:
        return [output or "GIT_STATUS_FAILED"]
    lines: List[str] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        path = _status_path(line)
        if "__pycache__/" in path or path.endswith((".pyc", ".pyo")):
            continue
        lines.append(line)
    return lines


def _imports(path: Path) -> List[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def _is_forbidden_import(name: str) -> bool:
    root = name.split(".")[0]
    if root in {prefix.split(".")[0] for prefix in FORBIDDEN_IMPORT_PREFIXES if "." not in prefix}:
        return True
    return any(name == prefix or name.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES)


def _check(label: str, condition: bool, passes: List[str], failures: List[str]) -> None:
    (passes if condition else failures).append(label)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: aiweb_slice18_gp014_preservation_decision_verify.py /home/nic/forge")
        return 2
    repo = Path(sys.argv[1]).resolve()
    passes: List[str] = []
    failures: List[str] = []

    _check("repository path exists", repo.is_dir(), passes, failures)
    _check("repository has .git directory", (repo / ".git").exists(), passes, failures)

    code, head = _run_git(repo, "rev-parse", "HEAD")
    _check("HEAD is readable", code == 0 and bool(head), passes, failures)
    if code == 0:
        _check("HEAD remains accepted Slice 17 base before commit", head == EXPECTED_BASE_HEAD, passes, failures)
    code, parent = _run_git(repo, "rev-parse", "HEAD^")
    _check("parent remains accepted Slice 17 parent before commit", code == 0 and parent == EXPECTED_BASE_PARENT, passes, failures)
    code, subject = _run_git(repo, "log", "-1", "--pretty=%s")
    _check("subject remains Slice 17 base before commit", code == 0 and subject == EXPECTED_BASE_SUBJECT, passes, failures)

    for rel_path in ALLOWED_NEW_PATHS:
        _check(f"required Slice 18 path exists: {rel_path}", (repo / rel_path).is_file(), passes, failures)

    status_lines = _status_lines(repo)
    for line in status_lines:
        rel_path = _status_path(line)
        _check(f"status path allowed: {rel_path}", rel_path in ALLOWED_NEW_PATHS or rel_path.rstrip("/") == "aiweb_gp014_preservation_decision_scaffold", passes, failures)

    for rel_path, expected_hash in PROTECTED_HASHES.items():
        target = repo / rel_path
        _check(f"protected path exists: {rel_path}", target.is_file(), passes, failures)
        if target.is_file():
            _check(f"protected path hash unchanged: {rel_path}", _sha256_file(target) == expected_hash, passes, failures)
        _check(f"protected path not dirty in git status: {rel_path}", all(_status_path(line) != rel_path for line in status_lines), passes, failures)

    for rel_path in ALLOWED_NEW_PATHS:
        if not rel_path.endswith(".py"):
            continue
        target = repo / rel_path
        if not target.is_file():
            continue
        try:
            compile(target.read_text(encoding="utf-8"), str(target), "exec")
            _check(f"Python syntax valid: {rel_path}", True, passes, failures)
        except SyntaxError:
            _check(f"Python syntax valid: {rel_path}", False, passes, failures)
            continue
        names = _imports(target)
        _check(f"no forbidden imports: {rel_path}", not any(_is_forbidden_import(name) for name in names), passes, failures)

    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    try:
        from aiweb_gp014_preservation_decision_scaffold.verify import run_verification

        behavior_passes, behavior_failures = run_verification(repo)
        _check("behavior verifier import and run succeeded", not behavior_failures, passes, failures)
        for item in behavior_passes:
            passes.append("behavior: " + item)
        for item in behavior_failures:
            failures.append("behavior: " + item)
    except Exception as exc:
        failures.append(f"behavior verifier raised: {exc}")

    print("=" * 72)
    print("AIWEB SLICE 18 GP-014 PRESERVATION DECISION PATCH VERIFY")
    print("=" * 72)
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")
    if failures:
        print("VERDICT: FAIL")
        return 1
    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
