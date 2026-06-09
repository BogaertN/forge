#!/usr/bin/env python3
"""Patch 297R behavior tests — idempotent action/state response separation.

The committed-state checks call only the already-idempotent duplicate path and
prove that the included persisted state is unchanged. New commit behavior is
exercised only inside temporary state directories.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORGE_ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN,
    TRANSACTION_COMMIT_APPROVAL_TOKEN,
    TRANSACTION_COMMIT_PATCH_ID,
    TRANSACTION_COMMIT_POST_ROUTE,
    TRANSACTION_COMMIT_SCHEMA_VERSION,
    TRANSACTION_PREFLIGHT_APPROVAL_TOKEN,
    build_live_candidates_payload,
    evaluate_problem_manifest_store_request,
    evaluate_seal_transaction_commit_request,
    evaluate_seal_transaction_preflight_request,
    problem_manifest_store_status,
    transaction_commit_boundary,
)
from rmc_engine_v1.mea.discovery_kernel import build_foundation_kernel  # noqa: E402

passed = 0
failed = 0


def check(name: str, condition: bool, detail: object = None) -> None:
    global passed, failed
    if condition:
        passed += 1
        suffix = f" — {detail}" if detail is not None else ""
        print(f"  ✓ [PASS] {name}{suffix}")
    else:
        failed += 1
        suffix = f" — {detail}" if detail is not None else ""
        print(f"  ✗ [FAIL] {name}{suffix}")


def file_hashes(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(p for p in root.rglob("*") if p.is_file())
    }


def build_request(store: Path) -> tuple[dict, dict, dict]:
    live = build_live_candidates_payload(store_root=store)
    chosen = next(row for row in live["candidates"] if row["candidate_id"] == "cg_hypothesis_001")
    preflight = evaluate_seal_transaction_preflight_request({
        "approval_token": TRANSACTION_PREFLIGHT_APPROVAL_TOKEN,
        "source_manifest_hash": live["source_manifest_hash"],
        "source_state_content_hash": live["source_state_content_hash"],
        "candidate_id": chosen["candidate_id"],
        "candidate_hash": chosen["candidate_hash"],
        "candidate_set_hash": live["candidate_set_hash"],
        "gate_report_hash": chosen["gate_report_hash"],
    }, store_root=store)
    request = {
        "approval_token": TRANSACTION_COMMIT_APPROVAL_TOKEN,
        "source_manifest_hash": preflight["source_manifest_hash"],
        "source_state_content_hash": preflight["source_state_content_hash"],
        "candidate_id": preflight["candidate_id"],
        "candidate_hash": preflight["candidate_hash"],
        "candidate_set_hash": preflight["candidate_set_hash"],
        "gate_report_hash": preflight["transaction_seal_packet_preview"]["gate_report_hash"],
        "transaction_seal_packet_hash": preflight["transaction_seal_packet_hash"],
        "transaction_audit_chain_hash": preflight["transaction_audit_chain_hash"],
        "proposed_new_manifest_hash": preflight["proposed_new_manifest_hash"],
        "transaction_intent_hash": preflight["transaction_intent_hash"],
        "receipt_preview_hash": preflight["receipt_preview_hash"],
        "rollback_preview_hash": preflight["rollback_preview_hash"],
    }
    return request, live, preflight


print("PATCH 297R BEHAVIOR TESTS — MEA Idempotent Response Action/State Semantic Separation Hotfix")
print("Forge root:", FORGE_ROOT)

boundary = transaction_commit_boundary()
check("patch_id_locked", TRANSACTION_COMMIT_PATCH_ID == "Patch 297R — MEA Idempotent Response Action/State Semantic Separation Hotfix", TRANSACTION_COMMIT_PATCH_ID)
check("schema_locked", TRANSACTION_COMMIT_SCHEMA_VERSION == "mea_seal_transaction_commit_v1_patch297r", TRANSACTION_COMMIT_SCHEMA_VERSION)
check("route_preserved", TRANSACTION_COMMIT_POST_ROUTE == "/api/mea/seal-transaction-commit")
check("boundary_semantic_separation_true", boundary.get("separates_invocation_actions_from_stored_state") is True)
check("boundary_idempotent_reports_no_execution_true", boundary.get("idempotent_response_reports_no_new_transition_execution") is True)
for field in ["writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "promotes_to_memory", "renders_user_output", "canonical_seal_route_available", "seal_route_available"]:
    check(f"boundary_{field}_false", boundary.get(field) is False, boundary.get(field))

# Exercise a new commit and subsequent idempotent replay in temporary state only.
with tempfile.TemporaryDirectory(prefix="patch297r_temp_commit_") as temp:
    store = Path(temp) / "mea_problem_manifest_store_v1"
    seed = evaluate_problem_manifest_store_request({
        "approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN,
        "operation": "seed",
        "use_fixture": True,
        "source": "patch297r_temp_fixture_seed",
    }, store_root=store, now_utc="2026-05-30T00:00:00+00:00")
    check("temp_seed_available", seed.get("gate_status") == "PERSISTED_INITIAL_SEED", seed.get("gate_status"))
    request, _, preflight = build_request(store)
    committed = evaluate_seal_transaction_commit_request(request, store_root=store, now_utc="2026-05-30T01:00:00+00:00")
    check("temp_commit_ok", committed.get("gate_status") == "COMMITTED_ATOMIC_MANIFEST_ADVANCE", committed.get("gate_status"))
    check("temp_commit_invocation_executed", committed.get("invocation_candidate_commit_executed") is True and committed.get("invocation_manifest_advance_executed") is True and committed.get("invocation_seal_executed") is True)
    check("temp_commit_stored_state_true", committed.get("stored_candidate_committed") is True and committed.get("stored_live_manifest_advanced") is True and committed.get("stored_seal_executed") is True)
    check("temp_commit_manifest_preserved", committed.get("committed_manifest_hash") == preflight.get("proposed_new_manifest_hash"), committed.get("committed_manifest_hash"))
    before_repeat = file_hashes(store)
    repeated = evaluate_seal_transaction_commit_request(request, store_root=store, now_utc="2026-05-30T02:00:00+00:00")
    after_repeat = file_hashes(store)
    check("temp_repeat_idempotent", repeated.get("gate_status") == "ALREADY_COMMITTED_IDEMPOTENT_NO_WRITE", repeated.get("gate_status"))
    check("temp_repeat_invocation_actions_false", all(repeated.get(key) is False for key in ["commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal", "invocation_candidate_commit_executed", "invocation_manifest_advance_executed", "invocation_seal_executed"]))
    check("temp_repeat_stored_facts_true", repeated.get("stored_candidate_committed") is True and repeated.get("stored_live_manifest_advanced") is True and repeated.get("stored_seal_executed") is True)
    check("temp_repeat_no_file_change", before_repeat == after_repeat)
    readback = problem_manifest_store_status(store_root=store)
    check("temp_readback_route_owner", readback.get("route_implementation_patch") == "Patch 294 — MEA Controlled Problem Manifest Store", readback.get("route_implementation_patch"))
    check("temp_readback_contract_patch", readback.get("response_contract_patch") == TRANSACTION_COMMIT_PATCH_ID, readback.get("response_contract_patch"))
    check("temp_readback_stored_writer", readback.get("stored_record_patch") == TRANSACTION_COMMIT_PATCH_ID, readback.get("stored_record_patch"))
    check("temp_readback_invocation_no_action", readback.get("invocation_manifest_advance_executed") is False)
    check("temp_readback_stored_advance_true", readback.get("stored_live_manifest_advanced") is True)

# Against the installed committed live state: call only its already committed idempotent path.
live_store = FORGE_ROOT / "runtime_state" / "mea_problem_manifest_store_v1"
live_payload_file = FORGE_ROOT.parent / "receipts" / "patch297_commit_payload.json"
if live_store.exists() and live_payload_file.exists():
    live_status_before = problem_manifest_store_status(store_root=live_store)
    live_request = json.loads(live_payload_file.read_text(encoding="utf-8"))
    before = file_hashes(live_store)
    live_repeat = evaluate_seal_transaction_commit_request(live_request, store_root=live_store)
    after = file_hashes(live_store)
    check("packet_committed_state_integrity", live_status_before.get("integrity_verified") is True)
    check("packet_repeat_idempotent", live_repeat.get("gate_status") == "ALREADY_COMMITTED_IDEMPOTENT_NO_WRITE", live_repeat.get("gate_status"))
    check("packet_repeat_invocation_actions_false", live_repeat.get("commits_live_candidates") is False and live_repeat.get("advances_live_manifest") is False and live_repeat.get("executes_seal") is False)
    check("packet_repeat_stored_state_true", live_repeat.get("stored_candidate_committed") is True and live_repeat.get("stored_live_manifest_advanced") is True and live_repeat.get("stored_seal_executed") is True)
    check("packet_repeat_no_state_mutation", before == after)
    live_readback = problem_manifest_store_status(store_root=live_store)
    check("packet_readback_route_owner", live_readback.get("route_implementation_patch") == "Patch 294 — MEA Controlled Problem Manifest Store")
    check("packet_readback_contract_hotfix", live_readback.get("response_contract_patch") == TRANSACTION_COMMIT_PATCH_ID)
    check("packet_readback_stored_record_patch_preserved", live_readback.get("stored_record_patch") == "Patch 297 — MEA Controlled Atomic Seal / Manifest Advance Commit", live_readback.get("stored_record_patch"))
else:
    check("packet_live_fixture_optional_outside_packet_workspace", True, "not present during minimal overlay-only install tests")

identity = build_foundation_kernel().identity()
check("kernel_stage_hotfixed", identity.get("kernel_stage") == "controlled_atomic_commit_response_semantics_hotfix_patch297r", identity.get("kernel_stage"))
check("kernel_commit_capability_active", identity.get("live_candidate_commit_active") is True and identity.get("live_manifest_advance_active") is True and identity.get("sealing_active") is True)
check("kernel_persistence_scope_corrected", identity.get("manifest_persistence_scope") == "approved_initial_seed_and_controlled_single_hypothesis_advance_no_memory_promotion", identity.get("manifest_persistence_scope"))
check("kernel_memory_promotion_still_false", identity.get("memory_promotion_active") is False)

print(f"RESULT: PATCH_297R_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
raise SystemExit(0 if failed == 0 else 1)
