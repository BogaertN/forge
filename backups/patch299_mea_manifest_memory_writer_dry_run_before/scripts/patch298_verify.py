#!/usr/bin/env python3
"""Patch 298 verifier — MEA live trace replay verification.

No live state transition is executed. The behavior suite creates new commits
only in temporary directories and calls live replay against any installed
committed state as a read-only verification action.
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
    "rmc_engine_v1/mea/__init__.py",
    "rmc_engine_v1/mea/live_candidates.py",
    "rmc_engine_v1/mea/seal_transaction_preflight.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "rmc_engine_v1/mea/live_trace_replay.py",
    "scripts/README_298.md",
    "scripts/patch298_verify.py",
    "scripts/test_patch298_mea_live_trace_replay.py",
]

print("PATCH 298 VERIFIER — MEA Live Trace Replay Verification")
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
    LIVE_TRACE_REPLAY_APPROVAL_TOKEN,
    LIVE_TRACE_REPLAY_PATCH_ID,
    LIVE_TRACE_REPLAY_POST_ROUTE,
    LIVE_TRACE_REPLAY_SCHEMA_VERSION,
    live_trace_replay_boundary,
    rebuild_live_candidates_from_state_record,
    rebuild_transaction_objects_from_source_record,
)
from rmc_engine_v1.mea.discovery_kernel import build_foundation_kernel  # noqa: E402

add("patch_id_export", LIVE_TRACE_REPLAY_PATCH_ID == "Patch 298 — MEA Live Trace Replay Verification", LIVE_TRACE_REPLAY_PATCH_ID)
add("schema_export", LIVE_TRACE_REPLAY_SCHEMA_VERSION == "mea_live_trace_replay_v1_patch298", LIVE_TRACE_REPLAY_SCHEMA_VERSION)
add("route_export", LIVE_TRACE_REPLAY_POST_ROUTE == "/api/mea/replay")
add("approval_token_export", LIVE_TRACE_REPLAY_APPROVAL_TOKEN == "APPROVE_MEA_LIVE_TRACE_REPLAY")
add("candidate_rebuild_helper_exported", callable(rebuild_live_candidates_from_state_record))
add("transaction_rebuild_helper_exported", callable(rebuild_transaction_objects_from_source_record))

boundary = live_trace_replay_boundary()
add("boundary_replay_from_rollback_source", boundary.get("replays_from_rollback_embedded_source_state") is True)
add("boundary_rebuilds_candidate", boundary.get("rebuilds_candidate_from_source_state") is True)
add("boundary_recompiles_transaction", boundary.get("recompiles_transaction_from_source_state") is True)
for key in ("writes_files", "writes_mea_runtime_state", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal", "promotes_to_memory", "renders_user_output", "canonical_seal_route_available", "seal_route_available"):
    add(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))

replay_source = (FORGE_ROOT / "rmc_engine_v1/mea/live_trace_replay.py").read_text(encoding="utf-8")
add("runtime_requires_committed_target", '"committed_manifest_hash"' in replay_source and '"committed_state_content_hash"' in replay_source)
add("runtime_verifies_linked_artifacts", "_verify_linked_artifacts" in replay_source and "rollback_source_state_integrity_failed" in replay_source)
add("runtime_rebuilds_transaction", "rebuild_transaction_objects_from_source_record" in replay_source)
add("runtime_non_self_referential_binding_explicit", "non_self_referential_output_binding_declared" in replay_source)
for label, patterns in {
    "subprocess_execution": ("subprocess.", "import subprocess"),
    "os_system_execution": ("os.system",),
    "socket_io": ("socket.", "import socket"),
    "requests_network": ("import requests", "requests.get(", "requests.post("),
    "chromadb_access": ("import chromadb", "chromadb."),
    "identity_vault_access": ("identity_vault.", "identity_vault/", "from identity_vault", "import identity_vault"),
    "file_write_open_mode": (".write_text(", "_atomic_write_json", "open(\"w", "open('w"),
}.items():
    add(f"replay_runtime_forbidden_scan:{label}", not any(pattern in replay_source for pattern in patterns))

main_source = (FORGE_ROOT / "main.py").read_text(encoding="utf-8")
add("main_post_dispatch_replay", '_p281_req_path == "/api/mea/replay"' in main_source)
add("foundation_current_patch_298", '"current_patch": "Patch 298 — MEA Live Trace Replay Verification"' in main_source)
add("foundation_lists_replay_route", '"/api/mea/replay"' in main_source)
add("no_canonical_mea_seal_route", '_p281_req_path == "/api/mea/seal"' not in main_source)
identity = build_foundation_kernel().identity()
add("kernel_stage_patch298", identity.get("kernel_stage") == "live_trace_replay_verification_patch298", identity.get("kernel_stage"))
add("kernel_replay_visible", identity.get("live_trace_replay_active") is True and identity.get("live_trace_replay_non_mutating") is True)

behavior = subprocess.run(
    [sys.executable, str(FORGE_ROOT / "scripts/test_patch298_mea_live_trace_replay.py")],
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

print(f"RESULT: PATCH_298_VERIFY {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
raise SystemExit(0 if failed == 0 else 1)
