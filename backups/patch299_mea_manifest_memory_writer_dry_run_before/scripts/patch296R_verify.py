#!/usr/bin/env python3
"""Patch 296R verifier — MEA Transaction Trace Source-Binding Hotfix."""
from __future__ import annotations

import ast
import hashlib
import os
import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
PASS = 0
FAIL = 0

REQUIRED = [
    "main.py",
    "SHA256SUMS.txt",
    "rmc_engine_v1/mea/__init__.py",
    "rmc_engine_v1/mea/live_candidates.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "rmc_engine_v1/mea/seal_transaction_preflight.py",
    "scripts/README_296R.md",
    "scripts/patch296R_verify.py",
    "scripts/test_patch296R_mea_transaction_trace_source_binding.py",
]


def check(name: str, condition: bool, detail: object = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✓ [PASS] {name}{suffix}")
    else:
        FAIL += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✗ [FAIL] {name}{suffix}")


print("PATCH 296R VERIFIER — MEA Transaction Trace Source-Binding Hotfix")
print(f"Forge root: {ROOT}")
for rel in REQUIRED:
    check(f"required_file:{rel}", (ROOT / rel).exists())

sha_ok = True
cache_entries: list[str] = []
try:
    for line in (ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(maxsplit=1)
        rel = rel.strip().lstrip("*")
        if "__pycache__" in rel or rel.endswith(".pyc"):
            cache_entries.append(rel)
        path = ROOT / rel
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            sha_ok = False
            print(f"    invalid checksum entry: {rel}")
except Exception as exc:
    sha_ok = False
    print(f"    checksum parse error: {exc}")
check("sha_manifest_excludes_cache", not cache_entries, cache_entries if cache_entries else "clean")
check("sha256sums_match", sha_ok)

for rel in REQUIRED:
    if rel.endswith(".py"):
        try:
            py_compile.compile(str(ROOT / rel), doraise=True)
            check(f"py_compile:{rel}", True)
        except Exception as exc:
            check(f"py_compile:{rel}", False, str(exc)[:160])

runtime = (ROOT / "rmc_engine_v1/mea/seal_transaction_preflight.py").read_text(encoding="utf-8")
check("runtime_uses_persisted_manifest_hash_field", 'source_status.get("manifest_hash")' in runtime)
check("runtime_uses_persisted_state_content_hash_field", 'source_status.get("state_content_hash")' in runtime)
check("runtime_does_not_use_missing_source_manifest_field", 'source_status.get("source_manifest_hash")' not in runtime)
check("runtime_does_not_use_missing_source_state_field", 'source_status.get("source_state_content_hash")' not in runtime)
check("runtime_enforces_trace_binding", "proposed_trace_source_binding_failed" in runtime and "transaction_trace_source_binding_verified" in runtime)
check("runtime_remains_preflight_no_mutation", "execute=false; persist=false; memory=false" in runtime)

# Narrow AST boundary check: hotfix runtime must not acquire write or execution behavior.
prohibited_roots = {"subprocess", "sqlite3", "chromadb", "requests", "urllib", "socket"}
prohibited_calls = {"open", "os.system", "subprocess.run", "subprocess.Popen", "eval", "exec"}
violations: list[str] = []
tree = ast.parse(runtime)
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name.split(".", 1)[0] in prohibited_roots:
                violations.append("import:" + alias.name)
    if isinstance(node, ast.ImportFrom) and str(node.module or "").split(".", 1)[0] in prohibited_roots:
        violations.append("from:" + str(node.module))
    if isinstance(node, ast.Call):
        name = ""
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            name = node.func.value.id + "." + node.func.attr
        if name in prohibited_calls or name.endswith(".write_text") or name.endswith(".write_bytes"):
            violations.append("call:" + name)
check("runtime_boundary_scan_no_writes_shell_network_db", not violations, violations if violations else "clean")

from rmc_engine_v1.mea import (  # noqa: E402
    TRANSACTION_PREFLIGHT_PATCH_ID,
    TRANSACTION_PREFLIGHT_SCHEMA_VERSION,
    TRANSACTION_PREFLIGHT_POST_ROUTE,
    transaction_preflight_boundary,
    kernel_identity,
)
check("patch_id_export", TRANSACTION_PREFLIGHT_PATCH_ID == "Patch 296R — MEA Transaction Trace Source-Binding Hotfix", TRANSACTION_PREFLIGHT_PATCH_ID)
check("schema_export", TRANSACTION_PREFLIGHT_SCHEMA_VERSION == "mea_seal_transaction_preflight_v1_patch296r", TRANSACTION_PREFLIGHT_SCHEMA_VERSION)
check("route_preserved", TRANSACTION_PREFLIGHT_POST_ROUTE == "/api/mea/seal-transaction-preflight")
boundary = transaction_preflight_boundary()
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_no_file_writes", boundary.get("writes_files") is False)
check("boundary_no_manifest_advance", boundary.get("advances_live_manifest") is False)
check("boundary_no_seal", boundary.get("executes_seal") is False and boundary.get("seal_route_available") is False)
check("boundary_no_memory", boundary.get("writes_memory") is False and boundary.get("promotes_to_memory") is False)
check("kernel_hotfix_stage", kernel_identity().get("kernel_stage") == "persisted_state_transaction_preflight_source_binding_hotfix_patch296r")

main_text = (ROOT / "main.py").read_text(encoding="utf-8")
check("foundation_status_hotfix", '"current_patch": "Patch 296R — MEA Transaction Trace Source-Binding Hotfix"' in main_text)
check("same_preflight_route_dispatch", '_p281_req_path == "/api/mea/seal-transaction-preflight"' in main_text)
check("no_real_mea_seal_route", '"path":"/api/mea/seal"' not in main_text and '_p281_req_path == "/api/mea/seal"' not in main_text)

behavior = subprocess.run(
    [sys.executable, str(ROOT / "scripts/test_patch296R_mea_transaction_trace_source_binding.py")],
    cwd=str(ROOT), text=True, capture_output=True,
    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
)
print(behavior.stdout, end="")
if behavior.stderr:
    print(behavior.stderr[:500], end="")
check("behavior_test_exit_0", behavior.returncode == 0, f"returncode={behavior.returncode}")
print(f"RESULT: PATCH_296R_VERIFY {'PASS' if FAIL == 0 else 'FAIL'}  Total:{PASS+FAIL} Passed:{PASS} Failed:{FAIL}")
sys.exit(0 if FAIL == 0 else 1)
