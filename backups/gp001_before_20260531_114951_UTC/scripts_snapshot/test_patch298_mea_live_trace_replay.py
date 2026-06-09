#!/usr/bin/env python3
"""Patch 298 behavior tests — MEA live trace replay verification.

Patch 298 is verification-only. New committed-state setup is created only under
temporary directories. When an installed committed live state exists, the test
calls only the no-write replay route function and proves file hashes unchanged.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORGE_ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    LIVE_TRACE_REPLAY_APPROVAL_TOKEN,
    LIVE_TRACE_REPLAY_PATCH_ID,
    LIVE_TRACE_REPLAY_POST_ROUTE,
    LIVE_TRACE_REPLAY_SCHEMA_VERSION,
    PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN,
    TRANSACTION_COMMIT_APPROVAL_TOKEN,
    TRANSACTION_PREFLIGHT_APPROVAL_TOKEN,
    build_live_candidates_payload,
    evaluate_live_trace_replay_request,
    evaluate_problem_manifest_store_request,
    evaluate_seal_transaction_commit_request,
    evaluate_seal_transaction_preflight_request,
    live_trace_replay_boundary,
    problem_manifest_store_status,
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
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(x for x in root.rglob("*") if x.is_file())
    }


def create_committed_store(store: Path) -> tuple[dict, dict]:
    seed = evaluate_problem_manifest_store_request({
        "approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN,
        "operation": "seed",
        "use_fixture": True,
        "source": "patch298_temp_fixture_seed",
    }, store_root=store, now_utc="2026-05-30T00:00:00+00:00")
    live = build_live_candidates_payload(store_root=store)
    chosen = next(c for c in live["candidates"] if c["candidate_id"] == "cg_hypothesis_001")
    preflight = evaluate_seal_transaction_preflight_request({
        "approval_token": TRANSACTION_PREFLIGHT_APPROVAL_TOKEN,
        "source_manifest_hash": live["source_manifest_hash"],
        "source_state_content_hash": live["source_state_content_hash"],
        "candidate_id": chosen["candidate_id"],
        "candidate_hash": chosen["candidate_hash"],
        "candidate_set_hash": live["candidate_set_hash"],
        "gate_report_hash": chosen["gate_report_hash"],
    }, store_root=store)
    commit_req = {
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
    commit = evaluate_seal_transaction_commit_request(commit_req, store_root=store, now_utc="2026-05-30T01:00:00+00:00")
    return seed, commit


def replay_request_from_status(status: dict) -> dict:
    record = status["stored_state"]
    return {
        "approval_token": LIVE_TRACE_REPLAY_APPROVAL_TOKEN,
        "transaction_id": record["transaction_id"],
        "transaction_intent_hash": record["transaction_intent_hash"],
        "candidate_id": record["candidate_id"],
        "candidate_hash": record["candidate_hash"],
        "committed_manifest_hash": record["manifest_hash"],
        "committed_state_content_hash": record["state_content_hash"],
    }


print("PATCH 298 BEHAVIOR TESTS — MEA Live Trace Replay Verification")
print("Forge root:", FORGE_ROOT)

boundary = live_trace_replay_boundary()
check("patch_id_locked", LIVE_TRACE_REPLAY_PATCH_ID == "Patch 298 — MEA Live Trace Replay Verification", LIVE_TRACE_REPLAY_PATCH_ID)
check("schema_locked", LIVE_TRACE_REPLAY_SCHEMA_VERSION == "mea_live_trace_replay_v1_patch298", LIVE_TRACE_REPLAY_SCHEMA_VERSION)
check("route_locked", LIVE_TRACE_REPLAY_POST_ROUTE == "/api/mea/replay")
check("boundary_verification_only", boundary.get("non_mutating") is True and boundary.get("replays_from_rollback_embedded_source_state") is True)
for field in ["writes_files", "writes_mea_runtime_state", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal", "promotes_to_memory", "renders_user_output", "canonical_seal_route_available", "seal_route_available"]:
    check(f"boundary_{field}_false", boundary.get(field) is False, boundary.get(field))

with tempfile.TemporaryDirectory(prefix="patch298_temp_replay_") as temp:
    store = Path(temp) / "mea_problem_manifest_store_v1"
    seed, commit = create_committed_store(store)
    check("temp_seed_persisted", seed.get("gate_status") == "PERSISTED_INITIAL_SEED", seed.get("gate_status"))
    check("temp_commit_available", commit.get("gate_status") == "COMMITTED_ATOMIC_MANIFEST_ADVANCE", commit.get("gate_status"))
    status = problem_manifest_store_status(store_root=store)
    req = replay_request_from_status(status)
    before = file_hashes(store)
    missing_token = evaluate_live_trace_replay_request({}, store_root=store)
    check("missing_token_rejected", missing_token.get("reason_code") == "approval_token_required", missing_token.get("reason_code"))
    mismatch_req = dict(req, committed_manifest_hash="0" * 64)
    mismatch = evaluate_live_trace_replay_request(mismatch_req, store_root=store)
    check("wrong_target_rejected", mismatch.get("reason_code") == "submitted_replay_target_mismatch", mismatch.get("reason_code"))
    replay = evaluate_live_trace_replay_request(req, store_root=store)
    after = file_hashes(store)
    check("temp_replay_verified", replay.get("gate_status") == "REPLAY_VERIFIED_NO_MUTATION", replay.get("gate_status"))
    check("temp_replay_all_checks", replay.get("all_replay_checks_passed") is True)
    check("temp_candidate_hash_replayed", replay.get("candidate_hash") == replay.get("replayed_candidate_hash"), replay.get("replayed_candidate_hash"))
    check("temp_manifest_hash_replayed", replay.get("committed_manifest_hash") == replay.get("replayed_manifest_hash"), replay.get("replayed_manifest_hash"))
    check("temp_transaction_hash_replayed", replay.get("transaction_intent_hash") == replay.get("replayed_transaction_intent_hash"), replay.get("replayed_transaction_intent_hash"))
    check("temp_no_invocation_transition", replay.get("advances_live_manifest") is False and replay.get("executes_seal") is False and replay.get("commits_live_candidates") is False)
    check("temp_stored_transition_retained", replay.get("stored_live_manifest_advanced") is True and replay.get("stored_seal_executed") is True and replay.get("stored_candidate_committed") is True)
    check("temp_no_state_mutation", before == after)
    # Tamper a copy of the receipt after all positive no-write checks; replay must refuse it.
    tampered_store = Path(temp) / "tampered_store"
    shutil.copytree(store, tampered_store)
    tampered_status = problem_manifest_store_status(store_root=tampered_store)
    receipt_path = Path(tampered_status["verified"]["write_receipt_path"])
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["claim_status"] = "verified_claim"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    tampered = evaluate_live_trace_replay_request(req, store_root=tampered_store)
    check("tampered_receipt_rejected", tampered.get("reason_code") == "committed_state_integrity_failed", tampered.get("reason_code"))

live_store = FORGE_ROOT / "runtime_state" / "mea_problem_manifest_store_v1"
if live_store.exists():
    live_status = problem_manifest_store_status(store_root=live_store)
    if live_status.get("integrity_verified") is True and live_status.get("stored_state_kind") == "mea_problem_manifest_committed_advance_state":
        live_before = file_hashes(live_store)
        live_replay = evaluate_live_trace_replay_request(replay_request_from_status(live_status), store_root=live_store)
        live_after = file_hashes(live_store)
        check("live_replay_verified", live_replay.get("gate_status") == "REPLAY_VERIFIED_NO_MUTATION", live_replay.get("gate_status"))
        check("live_replay_candidate", live_replay.get("candidate_id") == "cg_hypothesis_001")
        check("live_replay_claim_hypothesis", live_replay.get("claim_status") == "hypothesis")
        check("live_replay_proof_debt_unchanged", live_replay.get("proof_debt") == 0.85)
        check("live_replay_no_memory", live_replay.get("stored_memory_written") is False and live_replay.get("stored_memory_promoted") is False)
        check("live_replay_no_state_mutation", live_before == live_after)
    else:
        check("live_committed_state_optional_when_not_advanced", True, "no verified committed advance state in active root")
else:
    check("live_committed_state_optional_outside_install", True, "no runtime_state folder in overlay-only workspace")

identity = build_foundation_kernel().identity()
check("kernel_patch298_stage", identity.get("kernel_stage") == "live_trace_replay_verification_patch298", identity.get("kernel_stage"))
check("kernel_replay_route_visible", identity.get("live_trace_replay_post_route") == "/api/mea/replay")
check("kernel_replay_non_mutating", identity.get("live_trace_replay_non_mutating") is True)
check("kernel_memory_promotion_false", identity.get("memory_promotion_active") is False)

print(f"RESULT: PATCH_298_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
raise SystemExit(0 if failed == 0 else 1)
