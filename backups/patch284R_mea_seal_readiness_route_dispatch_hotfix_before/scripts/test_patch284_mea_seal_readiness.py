#!/usr/bin/env python3
"""Patch 284 behavior tests — MEA Seal Readiness Preview."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    SEAL_READINESS_PATCH_ID,
    SEAL_READINESS_APPROVAL_TOKEN,
    seal_readiness_boundary,
    seal_readiness_status,
    build_seal_readiness_preview,
    evaluate_seal_readiness_request,
)

passes = 0
fails = 0

def check(name: str, cond: bool, detail=None):
    global passes, fails
    if cond:
        passes += 1
        suffix = f" — {detail}" if detail is not None else ""
        print(f"  ✓ [PASS] {name}{suffix}")
    else:
        fails += 1
        suffix = f" — {detail}" if detail is not None else ""
        print(f"  ✗ [FAIL] {name}{suffix}")

print("PATCH 284 BEHAVIOR TESTS — MEA Seal Readiness Preview")
print(f"Forge root: {ROOT}")

check("patch_id_locked", SEAL_READINESS_PATCH_ID == "Patch 284 — MEA Seal Readiness Preview / Seal Readiness Report", SEAL_READINESS_PATCH_ID)
status = seal_readiness_status()
check("status_ok", status.get("status") == "OK")
check("status_approval_required", status.get("approval_required") is True)
check("status_token_locked", status.get("approval_token") == SEAL_READINESS_APPROVAL_TOKEN)
check("status_seal_route_unavailable", status.get("seal_route_available") is False)
check("status_candidate_sealing_inactive", status.get("candidate_sealing_active") is False)
check("status_memory_promotion_inactive", status.get("memory_promotion_active") is False)

b = seal_readiness_boundary()
check("boundary_non_mutating", b.get("non_mutating") is True)
check("boundary_creates_get_routes", b.get("creates_get_routes") is True)
check("boundary_creates_post_routes", b.get("creates_post_routes") is True)
check("boundary_requires_approval", b.get("requires_approval_token") is True)
for key in ["writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests", "commits_live_candidates", "seals_candidates", "promotes_to_memory", "renders_user_output", "mutates_existing_rmc_behavior", "mutates_launcher_behavior", "mutates_operator_console_ui", "seal_route_available", "memory_promotion_route_available"]:
    check(f"boundary_{key}_false", b.get(key) is False, b.get(key))

preview = build_seal_readiness_preview()
check("preview_status_ok", preview.get("status") == "OK")
check("preview_candidate_count_4", preview.get("candidate_count") == 4, preview.get("candidate_count"))
check("preview_ready_count_2", preview.get("seal_ready_preview_count") == 2, preview.get("seal_ready_preview_count"))
check("preview_blocked_count_2", preview.get("blocked_count") == 2, preview.get("blocked_count"))
check("preview_reference_count_1", preview.get("reference_only_count") == 1, preview.get("reference_only_count"))
check("preview_rejected_count_1", preview.get("rejected_count") == 1, preview.get("rejected_count"))
check("preview_best_candidate_hypothesis", preview.get("best_seal_ready_candidate_id") == "c_hypothesis_001", preview.get("best_seal_ready_candidate_id"))
check("preview_best_claim_hypothesis", preview.get("best_seal_ready_claim_status") == "hypothesis", preview.get("best_seal_ready_claim_status"))
check("preview_seal_execution_false", preview.get("seal_execution_permitted") is False)
check("preview_seal_route_unavailable", preview.get("seal_route_available") is False)
check("preview_memory_promotion_false", preview.get("memory_promotion_active") is False)
check("hard_law_hypothesis_remains_hypothesis", preview.get("hard_laws", {}).get("hypothesis_remains_hypothesis") is True)
check("hard_law_no_api_mea_seal", preview.get("hard_laws", {}).get("no_api_mea_seal_route") is True)

reports = {r["candidate_id"]: r for r in preview.get("seal_readiness_reports", [])}
check("report_ids_present", set(reports) == {"c_recall_001", "c_hypothesis_001", "c_branch_derive_001", "c_rejected_tamper_001"}, sorted(reports))
check("recall_not_sealable_reference", reports["c_recall_001"]["readiness_decision"] == "NOT_SEALABLE_REFERENCE_ONLY", reports["c_recall_001"]["readiness_decision"])
check("recall_not_ready", reports["c_recall_001"]["would_be_seal_ready"] is False)
check("hypothesis_ready_preview_only", reports["c_hypothesis_001"]["readiness_decision"] == "SEAL_READY_PREVIEW_ONLY", reports["c_hypothesis_001"]["readiness_decision"])
check("hypothesis_would_be_ready", reports["c_hypothesis_001"]["would_be_seal_ready"] is True)
check("hypothesis_no_execution", reports["c_hypothesis_001"]["seal_execution_permitted"] is False)
check("hypothesis_payload_preview", isinstance(reports["c_hypothesis_001"].get("future_seal_payload_preview"), dict))
check("hypothesis_payload_hash_64", isinstance(reports["c_hypothesis_001"].get("future_seal_payload_hash"), str) and len(reports["c_hypothesis_001"]["future_seal_payload_hash"]) == 64)
check("hypothesis_allowed_transitions", "future_memory_writer_must_still_require_sealed_manifest" in reports["c_hypothesis_001"]["future_seal_payload_preview"].get("allowed_next_transitions", []))
check("branch_bounded_ready", reports["c_branch_derive_001"]["readiness_decision"] == "BOUNDED_SEAL_READY_PREVIEW_ONLY", reports["c_branch_derive_001"]["readiness_decision"])
check("branch_would_be_ready", reports["c_branch_derive_001"]["would_be_seal_ready"] is True)
check("tamper_not_sealable", reports["c_rejected_tamper_001"]["readiness_decision"] == "NOT_SEALABLE_REJECTED", reports["c_rejected_tamper_001"]["readiness_decision"])
check("tamper_not_ready", reports["c_rejected_tamper_001"]["would_be_seal_ready"] is False)
check("all_execution_false", all(r.get("seal_execution_permitted") is False for r in reports.values()))
check("all_memory_inactive", all(r.get("memory_promotion_active") is False for r in reports.values()))

missing = evaluate_seal_readiness_request({"use_fixture": True})
check("missing_token_rejected", missing.get("status") == "REJECTED", missing)
check("missing_token_reason", missing.get("reason_code") == "approval_token_required")
check("missing_token_no_writes", missing.get("writes_files") is False and missing.get("writes_memory") is False)

approved = evaluate_seal_readiness_request({"approval_token": SEAL_READINESS_APPROVAL_TOKEN, "use_fixture": True})
check("approved_fixture_status_ok", approved.get("status") == "OK")
check("approved_fixture_accepted", approved.get("accepted") is True)
check("approved_fixture_preview_only", approved.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_fixture_ready_count_2", approved.get("seal_ready_preview_count") == 2, approved.get("seal_ready_preview_count"))
check("approved_fixture_no_seal", approved.get("seals_candidates") is False and approved.get("seal_execution_permitted") is False)
check("approved_fixture_no_memory", approved.get("promotes_to_memory") is False)

bad_hard = evaluate_seal_readiness_request({"approval_token": SEAL_READINESS_APPROVAL_TOKEN, "hard_gate_request": {"approval_token": "APPROVE_MEA_HARD_GATE_REPORT", "candidate_set_request": {"use_fixture": True, "approval_token": "BAD_TOKEN"}}})
check("bad_hard_gate_rejected", bad_hard.get("status") == "REJECTED", bad_hard.get("reason_code"))
check("bad_hard_gate_reason", bad_hard.get("reason_code") == "hard_gate_report_failed")

print(f"RESULT: PATCH_284_BEHAVIOR {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
