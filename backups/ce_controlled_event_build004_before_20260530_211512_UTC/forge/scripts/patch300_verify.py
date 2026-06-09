#!/usr/bin/env python3
"""Patch 300 verifier - Contribution Economy contract foundation / no-write kernel."""
from __future__ import annotations

import ast
import hashlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True
FORGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORGE_ROOT))

PATCH_ID = "Patch 300 - Contribution Economy Contract Foundation / No-Write Schema and Policy Kernel"
EXPECTED_PATCH299_MAIN_SHA256 = "d47b17dd5044d2a230fc3dcbf782cae1ae1ae1fe683ef9081193eafe18d04bb4"
EXPECTED_PATCH299_MEA_TREE_SHA256 = "bfa843e25715e8ae2895e3390801f067f8d790a81fc3f6e725c825236991da1f"
EXPECTED_PATCH299_MEA_STATE_TREE_SHA256 = "5c56daeb4af84f0ac1d8605677cfd21b84a2ab0e3aeb00220d8fd7b6ee0c10f3"

REQUIRED = (
    "SHA256SUMS.txt",
    "contribution_economy_v1/__init__.py",
    "contribution_economy_v1/contracts/__init__.py",
    "contribution_economy_v1/contracts/enums.py",
    "contribution_economy_v1/contracts/canonical_json.py",
    "contribution_economy_v1/contracts/hashing.py",
    "contribution_economy_v1/contracts/ct_reward_policy.py",
    "contribution_economy_v1/contracts/identity_reference_schema.py",
    "contribution_economy_v1/contracts/contribution_event_schema.py",
    "contribution_economy_v1/contracts/capsule_schema.py",
    "contribution_economy_v1/contracts/validation_schema.py",
    "contribution_economy_v1/contracts/ledger_schema.py",
    "contribution_economy_v1/contracts/nullification_schema.py",
    "contribution_economy_v1/contracts/lifecycle.py",
    "scripts/README_300.md",
    "scripts/patch300_verify.py",
    "scripts/test_patch300_contribution_economy_contract_foundation.py",
)
RUNTIME_MODULES = tuple(rel for rel in REQUIRED if rel.startswith("contribution_economy_v1/") and rel.endswith(".py"))
ALLOWED_RUNTIME_IMPORT_ROOTS = frozenset({
    "__future__", "collections", "dataclasses", "datetime", "enum", "hashlib", "json", "re", "types", "typing",
})
PROHIBITED_RUNTIME_CALL_NAMES = frozenset({"open", "exec", "eval", "compile", "__import__"})
PROHIBITED_RUNTIME_CALL_ATTRIBUTES = frozenset({
    "open", "write", "write_text", "write_bytes", "unlink", "mkdir", "makedirs", "touch",
    "connect", "request", "urlopen", "run", "Popen", "system",
})
FORBIDDEN_RUNTIME_TOKENS = {
    "filesystem_open": "open(",
    "path_write_text": ".write_text(",
    "path_write_bytes": ".write_bytes(",
    "subprocess": "subprocess",
    "shell_execution": "os.system",
    "socket": "socket",
    "http_client": "http.client",
    "urllib": "urllib",
    "requests": "requests",
    "chromadb": "chromadb",
    "sqlite": "sqlite3",
    "rmc_import": "rmc_engine_v1",
    "identity_vault_from_import": "from identity_vault",
    "identity_vault_direct_import": "import identity_vault",
    "api_route_literal": "/api/",
    "fastapi": "FastAPI",
}

passed = 0
failed = 0


def check(name: str, condition: bool, detail: object | None = None) -> None:
    global passed, failed
    if condition:
        passed += 1
        suffix = f" - {detail}" if detail is not None else ""
        print(f"  [PASS] {name}{suffix}")
    else:
        failed += 1
        suffix = f" - observed={detail!r}" if detail is not None else ""
        print(f"  [FAIL] {name}{suffix}")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file() and "__pycache__" not in item.parts and path_suffix_ok(item)):
        relative = path.relative_to(root).as_posix()
        digest.update(f"{relative}\0{sha256_file(path)}\n".encode("utf-8"))
    return digest.hexdigest()


def path_suffix_ok(path: Path) -> bool:
    return path.suffix not in {".pyc", ".pyo"}


def verify_sha_manifest() -> bool:
    manifest = FORGE_ROOT / "SHA256SUMS.txt"
    if not manifest.is_file():
        return False
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(maxsplit=1)
        path = FORGE_ROOT / rel.strip().lstrip("*")
        if not path.is_file() or sha256_file(path) != digest:
            return False
    return True


def compile_without_cache(relative_paths: Iterable[str]) -> None:
    for rel in relative_paths:
        source = (FORGE_ROOT / rel).read_text(encoding="utf-8")
        compile(source, rel, "exec")


def ast_runtime_safety(relative_path: str) -> tuple[bool, list[str]]:
    source = (FORGE_ROOT / relative_path).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=relative_path)
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root not in ALLOWED_RUNTIME_IMPORT_ROOTS:
                    violations.append(f"import:{alias.name}")
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            root = node.module.split(".", 1)[0]
            if root not in ALLOWED_RUNTIME_IMPORT_ROOTS:
                violations.append(f"import_from:{node.module}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in PROHIBITED_RUNTIME_CALL_NAMES:
                violations.append(f"call:{node.func.id}")
            elif isinstance(node.func, ast.Attribute) and node.func.attr in PROHIBITED_RUNTIME_CALL_ATTRIBUTES:
                violations.append(f"attribute_call:{node.func.attr}")
    return not violations, violations


def main() -> int:
    print("PATCH 300 VERIFIER - CONTRIBUTION ECONOMY CONTRACT FOUNDATION / NO-WRITE")
    print(f"Forge root: {FORGE_ROOT}")
    for rel in REQUIRED:
        check(f"required_file:{rel}", (FORGE_ROOT / rel).is_file())
    sha_text = (FORGE_ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8") if (FORGE_ROOT / "SHA256SUMS.txt").is_file() else ""
    check("sha_manifest_excludes_cache", "__pycache__" not in sha_text and ".pyc" not in sha_text)
    check("sha_manifest_matches_overlay", verify_sha_manifest())
    try:
        compile_without_cache(rel for rel in REQUIRED if rel.endswith(".py"))
        check("all_overlay_python_sources_compile", True)
    except Exception as exc:
        check("all_overlay_python_sources_compile", False, str(exc))

    main_sha = sha256_file(FORGE_ROOT / "main.py") if (FORGE_ROOT / "main.py").is_file() else "missing"
    mea_tree = tree_digest(FORGE_ROOT / "rmc_engine_v1" / "mea")
    mea_state_tree = tree_digest(FORGE_ROOT / "runtime_state" / "mea_problem_manifest_store_v1")
    check("patch299_main_py_unchanged", main_sha == EXPECTED_PATCH299_MAIN_SHA256, main_sha)
    check("patch299_mea_package_unchanged", mea_tree == EXPECTED_PATCH299_MEA_TREE_SHA256, mea_tree)
    check("patch299_mea_persisted_state_unchanged", mea_state_tree == EXPECTED_PATCH299_MEA_STATE_TREE_SHA256, mea_state_tree)
    main_text = (FORGE_ROOT / "main.py").read_text(encoding="utf-8")
    check("no_contribution_economy_api_route", "/api/contribution" not in main_text and "contribution_economy_v1" not in main_text)

    for rel in RUNTIME_MODULES:
        text = (FORGE_ROOT / rel).read_text(encoding="utf-8")
        for label, token in FORBIDDEN_RUNTIME_TOKENS.items():
            check(f"runtime_forbidden_scan:{rel}:{label}", token not in text)
        ast_ok, ast_violations = ast_runtime_safety(rel)
        check(f"runtime_ast_no_io_exec_or_external_import:{rel}", ast_ok, ast_violations)

    try:
        import contribution_economy_v1 as ce
        check("import_contribution_economy_package", True)
        check("package_patch_id", ce.PATCH_ID == PATCH_ID, ce.PATCH_ID)
        boundary = ce.kernel_identity()["boundary"]
        check("boundary_contract_only", boundary["contract_foundation_only"] is True)
        check("boundary_has_no_routes", boundary["routes_exposed"] is False)
        for key in (
            "writes_files", "writes_runtime_state", "writes_memory", "writes_jsonl_ledger",
            "writes_chroma", "writes_identity_vault", "creates_memory_capsule",
            "mints_contribution_tokens", "writes_influence_ledger", "writes_investment_ledger",
            "calls_llm", "executes_shell", "performs_network_io", "modifies_main_py", "modifies_mea",
        ):
            check(f"boundary_{key}_false", boundary[key] is False, boundary[key])
    except Exception as exc:
        check("import_contribution_economy_package", False, str(exc))

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    behavior = subprocess.run(
        [sys.executable, str(FORGE_ROOT / "scripts/test_patch300_contribution_economy_contract_foundation.py")],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    print(behavior.stdout, end="")
    if behavior.stderr:
        print(behavior.stderr, end="", file=sys.stderr)
    check("behavior_test_exit_0", behavior.returncode == 0, behavior.returncode)
    print(f"RESULT: PATCH_300_VERIFY {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
