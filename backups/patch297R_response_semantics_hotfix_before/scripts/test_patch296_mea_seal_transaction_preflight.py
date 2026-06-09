#!/usr/bin/env python3
"""Patch 296 behavior tests — MEA Persisted-State Seal / Advance Transaction Preflight."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN,
    TRANSACTION_PREFLIGHT_APPROVAL_TOKEN,
    TRANSACTION_PREFLIGHT_FORMULA,
    TRANSACTION_PREFLIGHT_PATCH_ID,
    TRANSACTION_PREFLIGHT_POST_ROUTE,
    TRANSACTION_PREFLIGHT_SCHEMA_VERSION,
    build_live_candidates_payload,
    build_seal_transaction_preflight_preview,
    evaluate_problem_manifest_store_request,
    evaluate_seal_transaction_preflight_request,
    kernel_identity,
    transaction_preflight_boundary,
)

passes = 0
fails = 0


def check(name: str, condition: bool, detail: object = "") -> None:
    global passes, fails
    if condition:
        passes += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✓ [PASS] {name}{suffix}")
    else:
        fails += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✗ [FAIL] {name}{suffix}")


def file_hashes(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*")) if p.is_file()
    }


def valid_request(live: dict, candidate_id: str = "cg_hypothesis_001") -> dict:
    row = next(item for item in live["candidates"] if item["candidate_id"] == candidate_id)
    return {
        "approval_token": TRANSACTION_PREFLIGHT_APPROVAL_TOKEN,
        "source_manifest_hash": live["source_manifest_hash"],
        "source_state_content_hash": live["source_state_content_hash"],
        "candidate_id": candidate_id,
        "candidate_hash": row["candidate_hash"],
        "candidate_set_hash": live["candidate_set_hash"],
        "gate_report_hash": row["gate_report_hash"],
    }


print("PATCH 296 BEHAVIOR TESTS — MEA Persisted-State Seal / Advance Transaction Preflight")
print(f"Forge root: {ROOT}")

check("patch_id_locked", TRANSACTION_PREFLIGHT_PATCH_ID == "Patch 296 — MEA Persisted-State Seal / Advance Transaction Preflight", TRANSACTION_PREFLIGHT_PATCH_ID)
check("schema_locked", TRANSACTION_PREFLIGHT_SCHEMA_VERSION == "mea_seal_transaction_preflight_v1_patch296", TRANSACTION_PREFLIGHT_SCHEMA_VERSION)
check("post_route_locked", TRANSACTION_PREFLIGHT_POST_ROUTE == "/api/mea/seal-transaction-preflight")
check("formula_integrity", "Integrity(M_t)" in TRANSACTION_PREFLIGHT_FORMULA)
check("formula_explicit_select", "ExplicitSelect(c*)" in TRANSACTION_PREFLIGHT_FORMULA)
check("formula_no_execution", all(term in TRANSACTION_PREFLIGHT_FORMULA for term in ["execute=false", "persist=false", "memory=false"]))

boundary = transaction_preflight_boundary()
for key in [
    "non_mutating", "creates_post_routes", "requires_approval_token", "requires_explicit_candidate_selection",
    "requires_source_manifest_hash_match", "requires_source_state_content_hash_match", "reads_files",
    "reads_mea_runtime_state", "requires_persisted_state_integrity", "generates_candidates_from_persisted_manifest",
    "uses_live_candidate_api_chain", "score_can_rank", "compiles_transaction_seal_packet_preview",
    "compiles_transaction_audit_chain_preview", "compiles_manifest_advance_preview", "compiles_receipt_preview",
    "compiles_rollback_preview", "future_mutation_patch_required",
]:
    check(f"boundary_{key}_true", boundary.get(key) is True, boundary.get(key))
for key in [
    "creates_get_routes", "score_can_select", "score_can_override_gates", "writes_files", "writes_mea_runtime_state",
    "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io",
    "seeds_live_manifests", "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal",
    "promotes_to_memory", "renders_user_output", "mutates_operator_console_ui", "seal_route_available",
    "memory_promotion_route_available",
]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
check("boundary_post_only", boundary.get("post_routes") == ["/api/mea/seal-transaction-preflight"] and boundary.get("get_routes") == [])

with tempfile.TemporaryDirectory(prefix="patch296_uninitialized_") as tmp:
    store = Path(tmp) / "state"
    no_token = evaluate_seal_transaction_preflight_request({}, store_root=store)
    check("missing_token_rejected_before_state", no_token.get("reason_code") == "approval_token_required", no_token.get("reason_code"))
    check("missing_token_no_store_created", not store.exists())
    incomplete = evaluate_seal_transaction_preflight_request({"approval_token": TRANSACTION_PREFLIGHT_APPROVAL_TOKEN}, store_root=store)
    check("missing_hashes_rejected", incomplete.get("reason_code") == "required_hash_fields_invalid", incomplete.get("reason_code"))
    check("missing_hashes_no_store_created", not store.exists())

with tempfile.TemporaryDirectory(prefix="patch296_state_") as tmp:
    store = Path(tmp) / "mea_problem_manifest_store_v1"
    seeded = evaluate_problem_manifest_store_request(
        {"approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN, "operation": "seed", "use_fixture": True},
        store_root=store,
        now_utc="2026-05-30T00:00:00+00:00",
    )
    check("seed_available_for_preflight", seeded.get("gate_status") == "PERSISTED_INITIAL_SEED", seeded.get("gate_status"))
    live = build_live_candidates_payload(store_root=store)
    check("live_candidates_from_persisted_state", live.get("status") == "OK" and live.get("source_state_integrity_verified") is True)
    check("live_candidate_count_4", live.get("candidate_count") == 4, live.get("candidate_count"))
    before = file_hashes(store)

    base = valid_request(live)
    no_token = evaluate_seal_transaction_preflight_request({k: v for k, v in base.items() if k != "approval_token"}, store_root=store)
    check("approved_surface_requires_token", no_token.get("reason_code") == "approval_token_required", no_token.get("reason_code"))
    wrong_route = evaluate_seal_transaction_preflight_request(base, store_root=store, endpoint="/api/mea/seal")
    check("route_mismatch_rejected", wrong_route.get("reason_code") == "route_mismatch" and wrong_route.get("route_mismatch_detected") is True, wrong_route.get("reason_code"))

    wrong_source = dict(base, source_manifest_hash="0" * 64)
    rejected_source = evaluate_seal_transaction_preflight_request(wrong_source, store_root=store)
    check("wrong_source_manifest_rejected", rejected_source.get("reason_code") == "source_manifest_hash_mismatch", rejected_source.get("reason_code"))

    wrong_state = dict(base, source_state_content_hash="0" * 64)
    rejected_state = evaluate_seal_transaction_preflight_request(wrong_state, store_root=store)
    check("wrong_source_state_rejected", rejected_state.get("reason_code") == "source_state_content_hash_mismatch", rejected_state.get("reason_code"))

    wrong_candidate = dict(base, candidate_hash="0" * 64)
    rejected_candidate = evaluate_seal_transaction_preflight_request(wrong_candidate, store_root=store)
    check("wrong_candidate_hash_rejected", rejected_candidate.get("reason_code") == "candidate_hash_mismatch", rejected_candidate.get("reason_code"))

    wrong_set = dict(base, candidate_set_hash="0" * 64)
    rejected_set = evaluate_seal_transaction_preflight_request(wrong_set, store_root=store)
    check("wrong_candidate_set_hash_rejected", rejected_set.get("reason_code") == "candidate_set_hash_mismatch", rejected_set.get("reason_code"))

    wrong_gate = dict(base, gate_report_hash="0" * 64)
    rejected_gate = evaluate_seal_transaction_preflight_request(wrong_gate, store_root=store)
    check("wrong_gate_report_hash_rejected", rejected_gate.get("reason_code") == "gate_report_hash_mismatch", rejected_gate.get("reason_code"))

    recall_request = valid_request(live, "cg_recall_001")
    rejected_recall = evaluate_seal_transaction_preflight_request(recall_request, store_root=store)
    check("recall_not_transaction_eligible", rejected_recall.get("reason_code") == "candidate_not_transaction_eligible", rejected_recall.get("reason_code"))

    tamper_request = valid_request(live, "cg_tamper_001")
    rejected_tamper = evaluate_seal_transaction_preflight_request(tamper_request, store_root=store)
    check("tamper_rejected", rejected_tamper.get("reason_code") in {"candidate_not_transaction_eligible", "tamper_or_containment_candidate_rejected"}, rejected_tamper.get("reason_code"))
    check("tamper_no_transaction", rejected_tamper.get("transaction_intent_created") is False)

    approved = evaluate_seal_transaction_preflight_request(base, store_root=store)
    repeated = evaluate_seal_transaction_preflight_request(base, store_root=store)
    after = file_hashes(store)
    check("hypothesis_preflight_ok", approved.get("status") == "OK" and approved.get("gate_status") == "ACCEPTED_PREFLIGHT_ONLY")
    check("hypothesis_status_preserved", approved.get("claim_status") == "hypothesis", approved.get("claim_status"))
    check("source_state_integrity_bound", approved.get("source_state_integrity_verified") is True)
    check("source_manifest_bound", approved.get("source_manifest_hash_matches_persisted_state") is True)
    check("source_state_hash_bound", approved.get("source_state_content_hash_matches_persisted_state") is True)
    check("candidate_generated_from_state", approved.get("candidate_generated_from_persisted_state") is True)
    check("candidate_hash_bound", approved.get("candidate_hash_matches_live_report") is True)
    check("gate_passed", approved.get("gate_engine_passed") is True)
    check("proof_debt_compatible", approved.get("proof_debt_compatible_with_claim_status") is True)
    check("replay_confirmed", approved.get("replay_confirmed") is True)
    check("no_tamper_or_route_mismatch", approved.get("tamper_detected") is False and approved.get("route_mismatch_detected") is False)
    check("explicit_hypothesis_not_auto_branch", approved.get("candidate_id") == "cg_hypothesis_001" and approved.get("highest_ranked_candidate_id") == "cg_branch_001" and approved.get("selection_basis") == "submitted_candidate_id_and_hash_not_rank")
    check("score_did_not_select", approved.get("score_did_not_select_candidate") is True and approved.get("ranked_candidate_auto_selected") is False)
    check("transaction_seal_packet_hash_64", isinstance(approved.get("transaction_seal_packet_hash"), str) and len(approved["transaction_seal_packet_hash"]) == 64)
    check("transaction_audit_chain_hash_64", isinstance(approved.get("transaction_audit_chain_hash"), str) and len(approved["transaction_audit_chain_hash"]) == 64)
    check("seal_packet_bound_to_source_state", approved.get("transaction_seal_packet_bound_to_persisted_state") is True)
    check("seal_packet_hash_in_audit_chain", approved.get("transaction_seal_packet_hash_matches_audit_chain") is True)
    check("proposed_manifest_bound_to_candidate", approved.get("proposed_manifest_bound_to_selected_candidate") is True)
    check("proposed_new_manifest_hash_64", isinstance(approved.get("proposed_new_manifest_hash"), str) and len(approved["proposed_new_manifest_hash"]) == 64)
    check("intent_hash_64", isinstance(approved.get("transaction_intent_hash"), str) and len(approved["transaction_intent_hash"]) == 64)
    check("receipt_hash_64", isinstance(approved.get("receipt_preview_hash"), str) and len(approved["receipt_preview_hash"]) == 64)
    check("receipt_bound_to_intent", approved.get("receipt_preview_bound_to_transaction_intent") is True)
    check("rollback_hash_64", isinstance(approved.get("rollback_preview_hash"), str) and len(approved["rollback_preview_hash"]) == 64)
    check("rollback_bound_to_source_state", approved.get("rollback_preview_bound_to_source_state") is True)
    check("transaction_hash_stability", approved.get("transaction_hash_stability_proven") is True)
    check("repeat_intent_hash", approved.get("transaction_intent_hash") == repeated.get("transaction_intent_hash"))
    check("repeat_proposed_manifest_hash", approved.get("proposed_new_manifest_hash") == repeated.get("proposed_new_manifest_hash"))
    proposed = approved.get("proposed_new_manifest", {})
    check("proposed_manifest_valid", approved.get("proposed_manifest_validation", {}).get("valid") is True)
    check("proposed_claim_hypothesis_not_fact", proposed.get("claim_status") == "hypothesis" and approved.get("claim_status_history_update", {}).get("claim_promotion_to_verified_fact") is False)
    check("proposed_proof_debt_preserved", proposed.get("proof_debt") == 0.85 and approved.get("proof_debt_update", {}).get("verified_claim_permitted") is False)
    check("proposed_adds_test_gap", _HYPOTHESIS_TEST_GAP in proposed.get("unknowns", []) if (_HYPOTHESIS_TEST_GAP := "Harmonic derivation path is opened but not sealed as empirical measurement.") else False)
    check("proposed_phase_path_records_phi5", proposed.get("phase_path") == ["Phi5"] and approved.get("phase_path_update", {}).get("phase_transition_executed") is False)
    check("proposed_history_appended", approved.get("operator_history_update", {}).get("before_count") == 0 and approved.get("operator_history_update", {}).get("after_count") == 1)
    semantics = approved.get("output_permission_interpretation", {})
    check("sealed_is_renderer_gate_not_seal", semantics.get("means_candidate_sealed") is False and semantics.get("means_seal_executed") is False and semantics.get("means_live_manifest_advanced") is False)
    check("no_mutation_or_memory", all(approved.get(key) is False for key in ["writes_files", "writes_mea_runtime_state", "writes_memory", "writes_chroma", "writes_identity_vault", "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal", "promotes_to_memory", "seal_route_available"]))
    check("state_immutable_after_preflight", before == after, sorted(after))

    branch_req = valid_request(live, "cg_branch_001")
    branch = evaluate_seal_transaction_preflight_request(branch_req, store_root=store)
    check("explicit_branch_preflight_allowed", branch.get("status") == "OK" and branch.get("claim_status") == "speculative_branch")
    check("branch_not_selected_by_rank_implicitly", branch.get("selection_basis") == "submitted_candidate_id_and_hash_not_rank" and branch.get("advances_live_manifest") is False)

    current = store / "current_problem_manifest.json"
    damaged = json.loads(current.read_text(encoding="utf-8"))
    damaged["manifest"]["claim_status"] = "verified_claim"
    current.write_text(json.dumps(damaged, sort_keys=True), encoding="utf-8")
    blocked = evaluate_seal_transaction_preflight_request(base, store_root=store)
    check("tampered_persisted_state_blocks_preflight", blocked.get("reason_code") == "persisted_source_state_blocked", blocked.get("reason_code"))
    check("tampered_state_no_intent", blocked.get("transaction_intent_created") is False and blocked.get("writes_files") is False)

kernel = kernel_identity()
check("kernel_stage_patch296", kernel.get("kernel_stage") == "persisted_state_transaction_preflight_patch296", kernel.get("kernel_stage"))
check("kernel_transaction_visible", kernel.get("transaction_preflight_visible") is True)
check("kernel_transaction_non_mutating", kernel.get("transaction_preflight_mutation_active") is False)
check("kernel_no_real_seal", kernel.get("seal_route_available") is False)

print(f"RESULT: PATCH_296_BEHAVIOR {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
