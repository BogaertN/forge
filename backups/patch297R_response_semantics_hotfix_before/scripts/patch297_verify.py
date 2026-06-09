#!/usr/bin/env python3
"""Patch 297 verifier — controlled atomic seal / manifest advance commit.

All behavior execution uses temporary state roots; this verifier never calls the
live commit endpoint or mutates the operator's persisted MEA state.
"""
from __future__ import annotations

import hashlib
import importlib
import py_compile
import subprocess
import sys
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORGE_ROOT))

checks: list[tuple[str, bool, object | None]] = []


def add(name: str, condition: bool, detail: object | None = None) -> None:
    checks.append((name, bool(condition), detail))


required = [
    "main.py",
    "SHA256SUMS.txt",
    "rmc_engine_v1/mea/__init__.py",
    "rmc_engine_v1/mea/problem_manifest_store.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "rmc_engine_v1/mea/seal_transaction_preflight.py",
    "rmc_engine_v1/mea/seal_transaction_commit.py",
    "scripts/README_297.md",
    "scripts/patch297_verify.py",
    "scripts/test_patch297_mea_seal_transaction_commit.py",
]

print("PATCH 297 VERIFIER — MEA Controlled Atomic Seal / Manifest Advance Commit")
print("Forge root:", FORGE_ROOT)
for rel in required:
    add(f"required_file:{rel}", (FORGE_ROOT / rel).is_file())

sha_path = FORGE_ROOT / "SHA256SUMS.txt"
sha_ok = True
cache_clean = True
if sha_path.is_file():
    for raw in sha_path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        expected, rel = raw.split(None, 1)
        rel = rel.strip().lstrip("*")
        if "__pycache__" in rel or rel.endswith(".pyc"):
            cache_clean = False
        target = FORGE_ROOT / rel
        actual = hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None
        if actual != expected:
            sha_ok = False
add("sha_manifest_excludes_cache", cache_clean, "clean" if cache_clean else "cache path present")
add("sha256sums_match", sha_ok)

for rel in [x for x in required if x.endswith(".py")]:
    try:
        py_compile.compile(str(FORGE_ROOT / rel), doraise=True)
        add(f"py_compile:{rel}", True)
    except Exception as exc:
        add(f"py_compile:{rel}", False, str(exc)[:120])

from rmc_engine_v1.mea import (  # noqa: E402
    TRANSACTION_COMMIT_APPROVAL_TOKEN,
    TRANSACTION_COMMIT_PATCH_ID,
    TRANSACTION_COMMIT_POST_ROUTE,
    TRANSACTION_COMMIT_SCHEMA_VERSION,
    transaction_commit_boundary,
)

add("patch_id_export", TRANSACTION_COMMIT_PATCH_ID == "Patch 297 — MEA Controlled Atomic Seal / Manifest Advance Commit", TRANSACTION_COMMIT_PATCH_ID)
add("schema_export", TRANSACTION_COMMIT_SCHEMA_VERSION == "mea_seal_transaction_commit_v1_patch297", TRANSACTION_COMMIT_SCHEMA_VERSION)
add("route_export", TRANSACTION_COMMIT_POST_ROUTE == "/api/mea/seal-transaction-commit")
add("token_export", TRANSACTION_COMMIT_APPROVAL_TOKEN == "APPROVE_MEA_SEAL_TRANSACTION_COMMIT")

boundary = transaction_commit_boundary()
for key in ("writes_files", "writes_mea_runtime_state", "reruns_transaction_preflight_under_lock", "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal", "hypothesis_commit_only", "idempotent_same_transaction_no_write", "rejects_conflicting_replay"):
    add(f"boundary_{key}_true", boundary.get(key) is True, boundary.get(key))
for key in ("writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "promotes_to_memory", "renders_user_output", "canonical_seal_route_available", "seal_route_available", "score_can_select", "score_can_override_gates"):
    add(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))

module_source = (FORGE_ROOT / "rmc_engine_v1/mea/seal_transaction_commit.py").read_text(encoding="utf-8")
add("runtime_reruns_preflight", "evaluate_seal_transaction_preflight_request" in module_source)
add("runtime_locks_store", "_exclusive_store_lock" in module_source)
add("runtime_atomic_current_replacement", "_atomic_write_json(paths[\"current\"], record)" in module_source)
add("runtime_writes_rollback_record", "_build_rollback_record" in module_source and "restore_state_record" in module_source)
add("runtime_enforces_hypothesis_only", "_REQUIRED_CANDIDATE_ID = \"cg_hypothesis_001\"" in module_source and "_REQUIRED_CLAIM_STATUS = ClaimStatus.HYPOTHESIS.value" in module_source)
add("runtime_reports_partial_write_failure_honestly", "possible_prepared_artifacts_without_live_state_advance" in module_source)
for label, patterns in {
    "subprocess_execution": ("subprocess.", "import subprocess"),
    "os_system_execution": ("os.system",),
    "socket_io": ("socket.", "import socket"),
    "requests_network": ("import requests", "requests.get(", "requests.post("),
    "chromadb_access": ("import chromadb", "chromadb."),
    "identity_vault_access": ("identity_vault.", "identity_vault/", "from identity_vault", "import identity_vault"),
}.items():
    add(f"runtime_forbidden_scan:{label}", not any(pattern in module_source for pattern in patterns))

main_source = (FORGE_ROOT / "main.py").read_text(encoding="utf-8")
add("main_post_dispatch_commit", '_p281_req_path == "/api/mea/seal-transaction-commit"' in main_source)
add("route_catalog_commit", '"path":"/api/mea/seal-transaction-commit"' in main_source)
add("no_canonical_mea_seal_route", '"path":"/api/mea/seal"' not in main_source and '_p281_req_path == "/api/mea/seal"' not in main_source)
add("foundation_status_patch297", '"current_patch": "Patch 297 — MEA Controlled Atomic Seal / Manifest Advance Commit"' in main_source)
add("foundation_reports_commit", '"seal_transaction_commit": True' in main_source)

behavior = subprocess.run(
    [sys.executable, str(FORGE_ROOT / "scripts/test_patch297_mea_seal_transaction_commit.py")],
    cwd=str(FORGE_ROOT), capture_output=True, text=True, check=False,
)
print(behavior.stdout, end="")
if behavior.stderr:
    print(behavior.stderr, end="", file=sys.stderr)
add("behavior_test_exit_0", behavior.returncode == 0, f"returncode={behavior.returncode}")

passed = 0
failed = 0
for name, condition, detail in checks:
    if condition:
        passed += 1
        suffix = f" — {detail}" if detail is not None else ""
        print(f"  ✓ [PASS] {name}{suffix}")
    else:
        failed += 1
        suffix = f" — {detail}" if detail is not None else ""
        print(f"  ✗ [FAIL] {name}{suffix}")

print(f"RESULT: PATCH_297_VERIFY {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
raise SystemExit(0 if failed == 0 else 1)
