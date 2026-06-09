#!/usr/bin/env python3
"""Patch 285 behavior tests — MEA Seal Packet Preview / Future Seal Payload Normalizer."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    SEAL_PACKET_PATCH_ID,
    SEAL_PACKET_APPROVAL_TOKEN,
    seal_packet_boundary,
    seal_packet_status,
    build_seal_packet_preview,
    evaluate_seal_packet_request,
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


print("PATCH 285 BEHAVIOR TESTS — MEA Seal Packet Preview")
print(f"Forge root: {ROOT}")

check("patch_id_locked", SEAL_PACKET_PATCH_ID == "Patch 285 — MEA Seal Packet Preview / Future Seal Payload Normalizer", SEAL_PACKET_PATCH_ID)
status = seal_packet_status()
check("status_ok", status.get("status") == "OK")
check("status_approval_required", status.get("approval_required") is True)
check("status_token_locked", status.get("approval_token") == SEAL_PACKET_APPROVAL_TOKEN)
check("status_seal_route_unavailable", status.get("seal_route_available") is False)
check("status_candidate_sealing_inactive", status.get("candidate_sealing_active") is False)
check("status_memory_promotion_inactive", status.get("memory_promotion_active") is False)
check("status_required_fields_present", "packet_hash" in status.get("required_packet_fields", []))

b = seal_packet_boundary()
check("boundary_non_mutating", b.get("non_mutating") is True)
check("boundary_creates_get_routes", b.get("creates_get_routes") is True)
check("boundary_creates_post_routes", b.get("creates_post_routes") is True)
check("boundary_requires_approval", b.get("requires_approval_token") is True)
for key in ["writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests", "commits_live_candidates", "seals_candidates", "promotes_to_memory", "renders_user_output", "mutates_existing_rmc_behavior", "mutates_launcher_behavior", "mutates_operator_console_ui", "seal_route_available", "memory_promotion_route_available"]:
    check(f"boundary_{key}_false", b.get(key) is False, b.get(key))

preview = build_seal_packet_preview()
check("preview_status_ok", preview.get("status") == "OK")
check("preview_packet_count_2", preview.get("packet_preview_count") == 2, preview.get("packet_preview_count"))
check("preview_blocked_count_2", preview.get("blocked_packet_count") == 2, preview.get("blocked_packet_count"))
check("preview_best_candidate_hypothesis", preview.get("best_packet_candidate_id") == "c_hypothesis_001", preview.get("best_packet_candidate_id"))
check("preview_best_claim_hypothesis", preview.get("best_packet_claim_status") == "hypothesis", preview.get("best_packet_claim_status"))
check("preview_hashes_unique", preview.get("packet_hashes_unique") is True)
check("preview_hash_stability", preview.get("packet_hash_stability_proven") is True)
check("preview_seal_execution_false", preview.get("seal_execution_permitted") is False)
check("preview_seal_route_unavailable", preview.get("seal_route_available") is False)
check("preview_memory_promotion_false", preview.get("memory_promotion_active") is False)
check("hard_law_packet_not_seal", preview.get("hard_laws", {}).get("seal_packet_preview_is_not_seal") is True)
check("hard_law_no_api_mea_seal", preview.get("hard_laws", {}).get("no_api_mea_seal_route") is True)
check("hard_law_hypothesis_remains", preview.get("hard_laws", {}).get("hypothesis_packet_remains_hypothesis") is True)

packets = {p["source_candidate_id"]: p for p in preview.get("seal_packets", [])}
check("packet_ids_present", set(packets) == {"c_hypothesis_001", "c_branch_derive_001"}, sorted(packets))
hyp = packets["c_hypothesis_001"]
body = hyp.get("packet_body", {})
check("hyp_packet_status_preview_only", hyp.get("packet_status") == "NORMALIZED_PREVIEW_ONLY")
check("hyp_packet_hash_64", isinstance(hyp.get("packet_hash"), str) and len(hyp["packet_hash"]) == 64)
check("hyp_packet_hash_matches_body", hyp.get("packet_hash") == body.get("packet_hash"))
check("hyp_hash_recomputed_matches", hyp.get("hash_recomputed_matches") is True)
check("hyp_claim_status_hypothesis", body.get("claim_status") == "hypothesis", body.get("claim_status"))
check("hyp_parent_hash_64", isinstance(body.get("parent_hash"), str) and len(body["parent_hash"]) == 64)
check("hyp_candidate_hash_64", isinstance(body.get("candidate_hash"), str) and len(body["candidate_hash"]) == 64)
check("hyp_hard_gate_hash_64", isinstance(body.get("hard_gate_report_hash"), str) and len(body["hard_gate_report_hash"]) == 64)
check("hyp_readiness_hash_64", isinstance(body.get("seal_readiness_report_hash"), str) and len(body["seal_readiness_report_hash"]) == 64)
check("hyp_future_payload_hash_64", isinstance(body.get("future_seal_payload_hash"), str) and len(body["future_seal_payload_hash"]) == 64)
check("hyp_output_permissions_preview_only", body.get("output_permissions") == "sealed_manifest_preview_only")
check("hyp_allowed_transition_memory_writer", "future_memory_writer_must_still_require_sealed_manifest" in body.get("allowed_next_transitions", []))
check("hyp_no_execution", body.get("seal_execution_permitted") is False and hyp.get("seal_execution_permitted") is False)
check("hyp_no_memory", body.get("memory_promotion_permitted") is False and hyp.get("memory_promotion_permitted") is False)

branch = packets["c_branch_derive_001"]
check("branch_packet_preview_only", branch.get("packet_status") == "NORMALIZED_PREVIEW_ONLY")
check("branch_packet_hash_64", isinstance(branch.get("packet_hash"), str) and len(branch["packet_hash"]) == 64)
check("branch_claim_status_speculative", branch.get("packet_body", {}).get("claim_status") == "speculative_branch", branch.get("packet_body", {}).get("claim_status"))

blocked_ids = {item.get("candidate_id") for item in preview.get("blocked_packet_reasons", [])}
check("blocked_recall_and_tamper", blocked_ids == {"c_recall_001", "c_rejected_tamper_001"}, sorted(blocked_ids))

preview2 = build_seal_packet_preview()
check("stable_preview_best_hash_repeat", preview2.get("best_packet_hash") == preview.get("best_packet_hash"))
check("stable_packet_hash_list_repeat", preview2.get("packet_hashes") == preview.get("packet_hashes"))

missing = evaluate_seal_packet_request({"use_fixture": True})
check("missing_token_rejected", missing.get("status") == "REJECTED", missing)
check("missing_token_reason", missing.get("reason_code") == "approval_token_required")
check("missing_token_no_writes", missing.get("writes_files") is False and missing.get("writes_memory") is False)

approved = evaluate_seal_packet_request({"approval_token": SEAL_PACKET_APPROVAL_TOKEN, "use_fixture": True})
check("approved_fixture_status_ok", approved.get("status") == "OK")
check("approved_fixture_accepted", approved.get("accepted") is True)
check("approved_fixture_preview_only", approved.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_fixture_packet_count_2", approved.get("packet_preview_count") == 2, approved.get("packet_preview_count"))
check("approved_fixture_no_seal", approved.get("seals_candidates") is False and approved.get("seal_execution_permitted") is False)
check("approved_fixture_no_memory", approved.get("promotes_to_memory") is False)

bad_ready = evaluate_seal_packet_request({"approval_token": SEAL_PACKET_APPROVAL_TOKEN, "seal_readiness_request": {"approval_token": "BAD_TOKEN", "use_fixture": True}})
check("bad_readiness_rejected", bad_ready.get("status") == "REJECTED", bad_ready.get("reason_code"))
check("bad_readiness_reason", bad_ready.get("reason_code") == "seal_readiness_failed")

print(f"RESULT: PATCH_285_BEHAVIOR {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
