#!/usr/bin/env python3
"""Patch 297 behavior tests — controlled atomic seal/manifest advance commit.

Tests operate only in temporary directories. They never mutate the live Forge
MEA state store unless a human separately calls the live commit endpoint.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

FORGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORGE_ROOT))

import rmc_engine_v1.mea.seal_transaction_commit as commit_module  # noqa: E402

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
    result = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        result[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def build_request(store: Path, candidate_id: str = "cg_hypothesis_001") -> tuple[dict, dict, dict]:
    live = build_live_candidates_payload(store_root=store)
    chosen = next(row for row in live["candidates"] if row["candidate_id"] == candidate_id)
    preflight = evaluate_seal_transaction_preflight_request({
        "approval_token": TRANSACTION_PREFLIGHT_APPROVAL_TOKEN,
        "source_manifest_hash": live["source_manifest_hash"],
        "source_state_content_hash": live["source_state_content_hash"],
        "candidate_id": candidate_id,
        "candidate_hash": chosen["candidate_hash"],
        "candidate_set_hash": live["candidate_set_hash"],
        "gate_report_hash": chosen["gate_report_hash"],
    }, store_root=store)
    req = {
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
    return req, live, preflight


print("PATCH 297 BEHAVIOR TESTS — MEA Controlled Atomic Seal / Manifest Advance Commit")
print("Forge root:", FORGE_ROOT)

boundary = transaction_commit_boundary()
check("patch_id_locked", TRANSACTION_COMMIT_PATCH_ID == "Patch 297 — MEA Controlled Atomic Seal / Manifest Advance Commit", TRANSACTION_COMMIT_PATCH_ID)
check("schema_locked", TRANSACTION_COMMIT_SCHEMA_VERSION == "mea_seal_transaction_commit_v1_patch297", TRANSACTION_COMMIT_SCHEMA_VERSION)
check("route_locked", TRANSACTION_COMMIT_POST_ROUTE == "/api/mea/seal-transaction-commit")
for field in ["requires_approval_token", "requires_explicit_candidate_selection", "requires_full_repaired_preflight_binding", "reruns_transaction_preflight_under_lock", "hypothesis_commit_only", "writes_files", "writes_mea_runtime_state", "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal", "uses_file_lock", "idempotent_same_transaction_no_write", "rejects_conflicting_replay"]:
    check(f"boundary_{field}_true", boundary.get(field) is True, boundary.get(field))
for field in ["writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "promotes_to_memory", "renders_user_output", "canonical_seal_route_available", "seal_route_available", "memory_promotion_route_available", "score_can_select", "score_can_override_gates"]:
    check(f"boundary_{field}_false", boundary.get(field) is False, boundary.get(field))

with tempfile.TemporaryDirectory(prefix="patch297_no_token_") as temp:
    store = Path(temp) / "store"
    response = evaluate_seal_transaction_commit_request({}, store_root=store)
    check("missing_token_rejected", response.get("reason_code") == "approval_token_required", response.get("reason_code"))
    check("missing_token_creates_no_store", not store.exists())

with tempfile.TemporaryDirectory(prefix="patch297_failure_truth_") as temp:
    store = Path(temp) / "mea_problem_manifest_store_v1"
    evaluate_problem_manifest_store_request({
        "approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN,
        "operation": "seed",
        "use_fixture": True,
        "source": "patch297_failure_fixture_seed",
    }, store_root=store, now_utc="2026-05-30T00:00:00+00:00")
    req, _, _ = build_request(store)
    original_atomic = commit_module._atomic_write_json
    def fail_current_only(path, payload):
        if path.name == "current_problem_manifest.json":
            raise RuntimeError("injected atomic current-state replacement failure")
        return original_atomic(path, payload)
    with patch.object(commit_module, "_atomic_write_json", side_effect=fail_current_only):
        failed_commit = commit_module.evaluate_seal_transaction_commit_request(req, store_root=store)
    failure_status = problem_manifest_store_status(store_root=store)
    check("injected_failure_reported", failed_commit.get("reason_code") == "atomic_commit_write_failed_requires_review", failed_commit.get("reason_code"))
    check("injected_failure_reports_artifact_writes_honestly", failed_commit.get("writes_files") is True and failed_commit.get("operator_review_required") is True)
    check("injected_failure_does_not_advance_current", failure_status.get("claim_status") == "test_required" and failure_status.get("stored_live_manifest_advanced") is False)

with tempfile.TemporaryDirectory(prefix="patch297_runtime_") as temp:
    store = Path(temp) / "mea_problem_manifest_store_v1"
    seed = evaluate_problem_manifest_store_request({
        "approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN,
        "operation": "seed",
        "use_fixture": True,
        "source": "patch297_behavior_fixture_seed",
    }, store_root=store, now_utc="2026-05-30T00:00:00+00:00")
    check("fixture_seed_available", seed.get("gate_status") == "PERSISTED_INITIAL_SEED", seed.get("gate_status"))
    req, live, preflight = build_request(store)
    check("preflight_source_binding_verified", preflight.get("transaction_trace_source_binding_verified") is True)
    check("preflight_claim_hypothesis", preflight.get("claim_status") == "hypothesis", preflight.get("claim_status"))
    check("preflight_highest_rank_not_selection", preflight.get("highest_ranked_candidate_id") == "cg_branch_001" and preflight.get("candidate_id") == "cg_hypothesis_001")

    bad = dict(req)
    bad["transaction_intent_hash"] = "0" * 64
    before_bad = file_hashes(store)
    rejected_bad = evaluate_seal_transaction_commit_request(bad, store_root=store)
    check("wrong_transaction_hash_rejected", rejected_bad.get("reason_code") == "submitted_transaction_hash_mismatch", rejected_bad.get("reason_code"))
    check("wrong_transaction_hash_no_mutation", file_hashes(store) == before_bad)

    branch_req, _, branch_preflight = build_request(store, "cg_branch_001")
    check("branch_preflight_exists_before_commit", branch_preflight.get("status") == "OK")
    before_branch = file_hashes(store)
    rejected_branch = evaluate_seal_transaction_commit_request(branch_req, store_root=store)
    check("branch_commit_blocked", rejected_branch.get("reason_code") == "hypothesis_candidate_required", rejected_branch.get("reason_code"))
    check("branch_commit_no_mutation", file_hashes(store) == before_branch)

    before_commit = file_hashes(store)
    committed = evaluate_seal_transaction_commit_request(req, store_root=store, now_utc="2026-05-30T01:00:00+00:00")
    after_commit = file_hashes(store)
    check("commit_ok", committed.get("gate_status") == "COMMITTED_ATOMIC_MANIFEST_ADVANCE", committed.get("gate_status"))
    check("commit_writes_expected_state", committed.get("write_performed") is True and committed.get("atomic_write_completed") is True)
    check("commit_flags_true", committed.get("selected_candidate_committed") is True and committed.get("advances_live_manifest") is True and committed.get("executes_seal") is True)
    check("commit_keeps_memory_blocked", committed.get("writes_memory") is False and committed.get("promotes_to_memory") is False)
    check("commit_no_canonical_seal_route", committed.get("canonical_seal_route_available") is False and committed.get("seal_route_available") is False)
    check("commit_changes_store", after_commit != before_commit)
    check("commit_manifest_is_preflight_manifest", committed.get("committed_manifest_hash") == preflight.get("proposed_new_manifest_hash"), committed.get("committed_manifest_hash"))

    status = problem_manifest_store_status(store_root=store)
    record = status["stored_state"]
    core = record["state_core"]
    trace = record["manifest"]["operator_history"][-1]
    check("readback_integrity_verified", status.get("integrity_verified") is True)
    check("readback_is_advanced_state", status.get("stored_state_kind") == "mea_problem_manifest_committed_advance_state", status.get("stored_state_kind"))
    check("readback_stored_flags", status.get("stored_candidate_committed") is True and status.get("stored_seal_executed") is True and status.get("stored_live_manifest_advanced") is True)
    check("readback_claim_hypothesis", status.get("claim_status") == "hypothesis", status.get("claim_status"))
    check("readback_proof_debt_unchanged", status.get("proof_debt") == 0.85, status.get("proof_debt"))
    check("readback_manifest_bound", status.get("manifest_hash") == preflight.get("proposed_new_manifest_hash"))
    check("trace_input_source_bound", trace.get("input_manifest_hash") == preflight.get("source_manifest_hash"), trace.get("input_manifest_hash"))
    check("trace_state_source_bound", trace.get("parameters", {}).get("source_state_content_hash") == preflight.get("source_state_content_hash"), trace.get("parameters", {}).get("source_state_content_hash"))
    check("record_transaction_bound", core.get("transaction_binding", {}).get("transaction_intent_hash") == preflight.get("transaction_intent_hash"))
    check("renderer_still_gated", record.get("output_permission_interpretation", {}).get("means_candidate_sealed") is False and core.get("persistence_scope", {}).get("renderer_output_permitted") is False)
    check("advance_receipt_exists", (store / record["write_receipt_relpath"]).exists())
    check("rollback_record_exists", (store / record["rollback_plan_relpath"]).exists())
    rollback = json.loads((store / record["rollback_plan_relpath"]).read_text())
    check("rollback_embeds_source_record", rollback.get("restore_state_record", {}).get("manifest_hash") == preflight.get("source_manifest_hash"))
    check("rollback_not_executed", rollback.get("rollback_performed") is False)

    before_repeat = file_hashes(store)
    repeat = evaluate_seal_transaction_commit_request(req, store_root=store, now_utc="2026-05-30T02:00:00+00:00")
    after_repeat = file_hashes(store)
    check("repeat_is_idempotent", repeat.get("gate_status") == "ALREADY_COMMITTED_IDEMPOTENT_NO_WRITE", repeat.get("gate_status"))
    check("repeat_writes_nothing", repeat.get("write_performed") is False and repeat.get("writes_files") is False)
    check("repeat_changes_no_files", before_repeat == after_repeat)

    conflict = dict(req)
    conflict["transaction_intent_hash"] = "f" * 64
    conflict["proposed_new_manifest_hash"] = "e" * 64
    before_conflict = file_hashes(store)
    rejected_conflict = evaluate_seal_transaction_commit_request(conflict, store_root=store)
    check("conflicting_replay_rejected", rejected_conflict.get("reason_code") == "conflicting_advanced_state_exists", rejected_conflict.get("reason_code"))
    check("conflicting_replay_changes_no_files", file_hashes(store) == before_conflict)

print(f"RESULT: PATCH_297_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
raise SystemExit(0 if failed == 0 else 1)
