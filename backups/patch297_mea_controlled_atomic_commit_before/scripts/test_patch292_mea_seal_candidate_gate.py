#!/usr/bin/env python3
"""Patch 292 behavior tests — MEA Controlled Seal Candidate Gate."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

passes = 0
fails = 0


def check(name: str, cond: bool, detail: object = "") -> None:
    global passes, fails
    if cond:
        passes += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✓ [PASS] {name}{suffix}")
    else:
        fails += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✗ [FAIL] {name}{suffix}")

print("PATCH 292 BEHAVIOR TESTS — MEA Controlled Seal Candidate Gate")
print(f"Forge root: {ROOT}")

from rmc_engine_v1.mea import (  # noqa: E402
    SEAL_CANDIDATE_GATE_APPROVAL_TOKEN,
    SEAL_CANDIDATE_GATE_PATCH_ID,
    SEAL_CANDIDATE_GATE_POST_ROUTE,
    SEAL_CANDIDATE_GATE_SCHEMA_VERSION,
    build_seal_candidate_gate_preview,
    build_seal_candidate_gate_rejection_preview,
    build_seal_engine_dry_run,
    evaluate_seal_candidate_gate_request,
    kernel_identity,
    seal_candidate_gate_boundary,
)

check("patch_id_locked", SEAL_CANDIDATE_GATE_PATCH_ID == "Patch 292 — MEA Controlled Seal Candidate Gate", SEAL_CANDIDATE_GATE_PATCH_ID)
check("schema_locked", SEAL_CANDIDATE_GATE_SCHEMA_VERSION == "mea_seal_candidate_gate_v1_patch292", SEAL_CANDIDATE_GATE_SCHEMA_VERSION)
check("post_route_locked", SEAL_CANDIDATE_GATE_POST_ROUTE == "/api/mea/seal-candidate-gate")

boundary = seal_candidate_gate_boundary()
for key in [
    "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault",
    "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests",
    "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal",
    "promotes_to_memory", "renders_user_output", "mutates_operator_console_ui",
]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_creates_only_post", boundary.get("creates_post_routes") is True and boundary.get("creates_get_routes") is False)
check("boundary_requires_token", boundary.get("requires_approval_token") is True)
check("boundary_requires_candidate_hash", boundary.get("requires_candidate_hash_match") is True)
check("boundary_requires_packet_audit", boundary.get("requires_packet_hash_audit_match") is True)
check("boundary_response_only", boundary.get("sealed_candidate_object_response_only") is True)
check("boundary_no_real_seal_route", boundary.get("seal_route_available") is False)

# Source dry-run object values.
dry = build_seal_engine_dry_run()
objects = {obj.get("candidate_id"): obj for obj in dry.get("seal_objects", [])}
hyp = objects.get("cg_hypothesis_001", {})
branch = objects.get("cg_branch_001", {})
check("dry_run_source_object_count_2", dry.get("seal_object_count") == 2, dry.get("seal_object_count"))
check("hypothesis_source_exists", bool(hyp))
check("branch_source_exists", bool(branch))

rejected = build_seal_candidate_gate_rejection_preview()
check("missing_token_rejected", rejected.get("status") == "REJECTED")
check("missing_token_reason", rejected.get("reason_code") == "approval_token_required", rejected.get("reason_code"))
check("missing_token_no_writes", rejected.get("writes_files") is False and rejected.get("writes_memory") is False)
check("missing_token_no_seal", rejected.get("seals_candidates") is False and rejected.get("seal_execution_permitted") is False)
check("missing_token_no_memory", rejected.get("promotes_to_memory") is False)

wrong_hash = evaluate_seal_candidate_gate_request({
    "approval_token": SEAL_CANDIDATE_GATE_APPROVAL_TOKEN,
    "candidate_id": "cg_hypothesis_001",
    "candidate_hash": "0" * 64,
})
check("wrong_hash_rejected", wrong_hash.get("status") == "REJECTED")
check("wrong_hash_reason", wrong_hash.get("reason_code") == "candidate_hash_mismatch", wrong_hash.get("reason_code"))
check("wrong_hash_no_preview_object", wrong_hash.get("sealed_candidate_object_created") is False)
check("wrong_hash_no_state_change", wrong_hash.get("commits_live_candidates") is False and wrong_hash.get("advances_live_manifest") is False)

missing_hash = evaluate_seal_candidate_gate_request({"approval_token": SEAL_CANDIDATE_GATE_APPROVAL_TOKEN, "candidate_id": "cg_hypothesis_001"})
check("missing_hash_rejected", missing_hash.get("status") == "REJECTED")
check("missing_hash_reason", missing_hash.get("reason_code") == "candidate_hash_required", missing_hash.get("reason_code"))

recall_attempt = evaluate_seal_candidate_gate_request({
    "approval_token": SEAL_CANDIDATE_GATE_APPROVAL_TOKEN,
    "candidate_id": "cg_recall_001",
    "candidate_hash": "9f017ac76236ae7263b0805440106f9db94cae0603cb3275e0ba6f714f0f1ce0",
})
check("recall_not_seal_eligible", recall_attempt.get("status") == "REJECTED")
check("recall_reason", recall_attempt.get("reason_code") == "candidate_not_seal_eligible", recall_attempt.get("reason_code"))

accepted = build_seal_candidate_gate_preview("cg_hypothesis_001")
check("approved_ok", accepted.get("status") == "OK")
check("approved_preview_only", accepted.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_candidate_hypothesis", accepted.get("candidate_id") == "cg_hypothesis_001")
check("approved_claim_hypothesis", accepted.get("claim_status") == "hypothesis", accepted.get("claim_status"))
check("approved_hash_stability", accepted.get("sealed_candidate_preview_hash_stability_proven") is True)
check("approved_candidate_hash_match", accepted.get("candidate_hash_matches_packet") is True)
check("approved_packet_audit_match", accepted.get("seal_packet_hash_matches_audit_chain") is True)
check("approved_gate_engine_passed", accepted.get("gate_engine_passed") is True)
check("approved_claim_allowed", accepted.get("claim_status_allowed") is True)
check("approved_proof_debt_compatible", accepted.get("proof_debt_compatible_with_claim_status") is True)
check("approved_replay_confirmed", accepted.get("replay_confirmed") is True)
check("approved_no_tamper", accepted.get("tamper_detected") is False)
check("approved_no_route_mismatch", accepted.get("route_mismatch_detected") is False)
check("approved_no_live_seal", accepted.get("seals_candidates") is False and accepted.get("seal_execution_permitted") is False)
check("approved_no_commit", accepted.get("commits_live_candidates") is False)
check("approved_no_advance", accepted.get("advances_live_manifest") is False)
check("approved_no_memory", accepted.get("writes_memory") is False and accepted.get("promotes_to_memory") is False)
check("approved_no_llm_shell_network", accepted.get("calls_llm") is False and accepted.get("executes_shell") is False and accepted.get("performs_network_io") is False)

obj = accepted.get("sealed_candidate_object", {})
check("sealed_object_present", isinstance(obj, dict) and obj.get("sealed_candidate_object_created") is True)
check("sealed_object_response_only", obj.get("sealed_candidate_live") is False and obj.get("executed") is False)
check("sealed_object_hash_64", isinstance(obj.get("sealed_candidate_preview_hash"), str) and len(obj.get("sealed_candidate_preview_hash")) == 64)
check("sealed_object_candidate_hash_64", isinstance(obj.get("candidate_hash"), str) and len(obj.get("candidate_hash")) == 64)
check("sealed_object_packet_hash_64", isinstance(obj.get("seal_packet_hash"), str) and len(obj.get("seal_packet_hash")) == 64)
check("sealed_object_audit_hash_64", isinstance(obj.get("candidate_audit_chain_hash"), str) and len(obj.get("candidate_audit_chain_hash")) == 64)
check("sealed_object_remaining_unknowns", obj.get("remaining_unknown_count", 0) >= 2)
check("sealed_object_permissions", len(obj.get("output_permissions", [])) >= 2)
check("sealed_object_transitions", len(obj.get("allowed_next_transitions", [])) >= 2)
check("sealed_object_no_memory", obj.get("memory_write_permitted") is False and obj.get("memory_promotion_permitted") is False)

branch_accept = build_seal_candidate_gate_preview("cg_branch_001")
check("branch_approved_ok", branch_accept.get("status") == "OK")
check("branch_claim_allowed", branch_accept.get("claim_status") == "speculative_branch", branch_accept.get("claim_status"))
check("branch_no_live_seal", branch_accept.get("seals_candidates") is False and branch_accept.get("seal_execution_permitted") is False)
check("branch_no_memory", branch_accept.get("promotes_to_memory") is False)

repeat = build_seal_candidate_gate_preview("cg_hypothesis_001")
check("preview_hash_repeat", accepted.get("sealed_candidate_preview_hash") == repeat.get("sealed_candidate_preview_hash"))
check("audit_hash_repeat", accepted.get("candidate_audit_chain_hash") == repeat.get("candidate_audit_chain_hash"))

kernel = kernel_identity()
check("kernel_stage_patch292", kernel.get("kernel_stage") == "seal_candidate_gate_preview_patch292", kernel.get("kernel_stage"))
check("kernel_gate_visible", kernel.get("seal_candidate_gate_visible") is True)
check("kernel_no_real_seal", kernel.get("seal_route_available") is False)

print(f"RESULT: PATCH_292_BEHAVIOR {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
