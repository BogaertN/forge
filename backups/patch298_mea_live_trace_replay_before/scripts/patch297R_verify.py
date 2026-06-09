#!/usr/bin/env python3
"""Patch 297R verifier — idempotent response action/state semantic separation.

No live state transition is executed. The behavior suite uses temporary state
for new commits and only the idempotent no-write path for an existing advanced
state when that state is present.
"""
from __future__ import annotations

import hashlib
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
    "rmc_engine_v1/mea/problem_manifest_store.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "rmc_engine_v1/mea/seal_transaction_commit.py",
    "scripts/README_297R.md",
    "scripts/patch297R_verify.py",
    "scripts/test_patch297R_mea_idempotent_response_semantics.py",
]

print("PATCH 297R VERIFIER — MEA Idempotent Response Action/State Semantic Separation Hotfix")
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
from rmc_engine_v1.mea.discovery_kernel import build_foundation_kernel  # noqa: E402

add("patch_id_export", TRANSACTION_COMMIT_PATCH_ID == "Patch 297R — MEA Idempotent Response Action/State Semantic Separation Hotfix", TRANSACTION_COMMIT_PATCH_ID)
add("schema_export", TRANSACTION_COMMIT_SCHEMA_VERSION == "mea_seal_transaction_commit_v1_patch297r", TRANSACTION_COMMIT_SCHEMA_VERSION)
add("route_preserved", TRANSACTION_COMMIT_POST_ROUTE == "/api/mea/seal-transaction-commit")
add("approval_token_preserved", TRANSACTION_COMMIT_APPROVAL_TOKEN == "APPROVE_MEA_SEAL_TRANSACTION_COMMIT")
boundary = transaction_commit_boundary()
add("boundary_semantics_separation", boundary.get("separates_invocation_actions_from_stored_state") is True)
add("boundary_idempotent_no_execution", boundary.get("idempotent_response_reports_no_new_transition_execution") is True)
for key in ("writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "promotes_to_memory", "renders_user_output", "canonical_seal_route_available", "seal_route_available"):
    add(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))

commit_source = (FORGE_ROOT / "rmc_engine_v1/mea/seal_transaction_commit.py").read_text(encoding="utf-8")
store_source = (FORGE_ROOT / "rmc_engine_v1/mea/problem_manifest_store.py").read_text(encoding="utf-8")
kernel_source = (FORGE_ROOT / "rmc_engine_v1/mea/discovery_kernel.py").read_text(encoding="utf-8")
add("runtime_idempotent_invocation_false", '"invocation_manifest_advance_executed": False' in commit_source and '"stored_live_manifest_advanced": record.get("live_manifest_advanced") is True' in commit_source)
add("runtime_success_invocation_explicit", '"invocation_manifest_advance_executed": True' in commit_source and '"stored_candidate_committed": True' in commit_source)
add("readback_route_vs_record_patch_separated", '"route_implementation_patch"' in store_source and '"response_contract_patch"' in store_source and '"stored_record_patch"' in store_source)
add("kernel_stale_capability_flags_repaired", '"live_candidate_commit_active": True' in kernel_source and '"live_manifest_advance_active": True' in kernel_source and '"sealing_active": True' in kernel_source)
for label, patterns in {
    "subprocess_execution": ("subprocess.", "import subprocess"),
    "os_system_execution": ("os.system",),
    "socket_io": ("socket.", "import socket"),
    "requests_network": ("import requests", "requests.get(", "requests.post("),
    "chromadb_access": ("import chromadb", "chromadb."),
    "identity_vault_access": ("identity_vault.", "identity_vault/", "from identity_vault", "import identity_vault"),
}.items():
    add(f"commit_runtime_forbidden_scan:{label}", not any(pattern in commit_source for pattern in patterns))

main_source = (FORGE_ROOT / "main.py").read_text(encoding="utf-8")
add("main_post_dispatch_preserved", '_p281_req_path == "/api/mea/seal-transaction-commit"' in main_source)
add("foundation_current_patch_hotfix", '"current_patch": "Patch 297R — MEA Idempotent Response Action/State Semantic Separation Hotfix"' in main_source)
add("foundation_mode_hotfix", '"mode": "mea_foundation_status_patch297r"' in main_source)
add("no_canonical_mea_seal_route", '"path":"/api/mea/seal"' not in main_source and '_p281_req_path == "/api/mea/seal"' not in main_source)
identity = build_foundation_kernel().identity()
add("kernel_identity_patch297r", identity.get("kernel_stage") == "controlled_atomic_commit_response_semantics_hotfix_patch297r", identity.get("kernel_stage"))

behavior = subprocess.run(
    [sys.executable, str(FORGE_ROOT / "scripts/test_patch297R_mea_idempotent_response_semantics.py")],
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

print(f"RESULT: PATCH_297R_VERIFY {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
raise SystemExit(0 if failed == 0 else 1)
