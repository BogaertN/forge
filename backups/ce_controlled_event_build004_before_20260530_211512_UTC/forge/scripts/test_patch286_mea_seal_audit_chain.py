#!/usr/bin/env python3
"""Patch 286 behavior tests — MEA Seal Packet Audit Chain / Hash Stability Ledger Preview."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    SEAL_AUDIT_CHAIN_PATCH_ID,
    SEAL_AUDIT_CHAIN_APPROVAL_TOKEN,
    seal_audit_chain_boundary,
    seal_audit_chain_status,
    build_seal_audit_chain_preview,
    evaluate_seal_audit_chain_request,
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


print("PATCH 286 BEHAVIOR TESTS — MEA Seal Packet Audit Chain")
print(f"Forge root: {ROOT}")

check("patch_id_locked", SEAL_AUDIT_CHAIN_PATCH_ID == "Patch 286 — MEA Seal Packet Audit Chain / Hash Stability Ledger Preview", SEAL_AUDIT_CHAIN_PATCH_ID)
status = seal_audit_chain_status()
check("status_ok", status.get("status") == "OK")
check("status_approval_required", status.get("approval_required") is True)
check("status_token_locked", status.get("approval_token") == SEAL_AUDIT_CHAIN_APPROVAL_TOKEN)
check("status_seal_route_unavailable", status.get("seal_route_available") is False)
check("status_candidate_sealing_inactive", status.get("candidate_sealing_active") is False)
check("status_memory_promotion_inactive", status.get("memory_promotion_active") is False)
for required in ["parent_manifest_hash", "candidate_hash", "hard_gate_report_hash", "seal_readiness_report_hash", "seal_packet_hash"]:
    check(f"status_required_link_field:{required}", required in status.get("required_link_fields", []))

b = seal_audit_chain_boundary()
check("boundary_non_mutating", b.get("non_mutating") is True)
check("boundary_creates_get_routes", b.get("creates_get_routes") is True)
check("boundary_creates_post_routes", b.get("creates_post_routes") is True)
check("boundary_requires_approval", b.get("requires_approval_token") is True)
for key in ["writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests", "commits_live_candidates", "advances_live_manifest", "seals_candidates", "promotes_to_memory", "renders_user_output", "mutates_existing_rmc_behavior", "mutates_launcher_behavior", "mutates_operator_console_ui", "seal_route_available", "memory_promotion_route_available"]:
    check(f"boundary_{key}_false", b.get(key) is False, b.get(key))

preview = build_seal_audit_chain_preview()
check("preview_status_ok", preview.get("status") == "OK")
check("preview_audit_link_count_2", preview.get("audit_link_count") == 2, preview.get("audit_link_count"))
check("preview_blocked_count_2", preview.get("blocked_audit_count") == 2, preview.get("blocked_audit_count"))
check("preview_best_candidate_hypothesis", preview.get("best_audit_candidate_id") == "c_hypothesis_001", preview.get("best_audit_candidate_id"))
check("preview_best_claim_hypothesis", preview.get("best_audit_claim_status") == "hypothesis", preview.get("best_audit_claim_status"))
check("preview_link_hashes_unique", preview.get("audit_link_hashes_unique") is True)
check("preview_link_hash_stability", preview.get("audit_link_hash_stability_proven") is True)
check("preview_packet_hash_stability", preview.get("packet_hash_stability_proven") is True)
check("preview_chain_hash_stability", preview.get("audit_chain_hash_stability_proven") is True)
check("preview_chain_hash_64", isinstance(preview.get("audit_chain_hash"), str) and len(preview["audit_chain_hash"]) == 64)
check("preview_seal_execution_false", preview.get("seal_execution_permitted") is False)
check("preview_seal_route_unavailable", preview.get("seal_route_available") is False)
check("preview_memory_promotion_false", preview.get("memory_promotion_active") is False)
check("hard_law_audit_not_seal", preview.get("hard_laws", {}).get("audit_chain_preview_is_not_seal") is True)
check("hard_law_no_api_mea_seal", preview.get("hard_laws", {}).get("no_api_mea_seal_route") is True)

links = {link["candidate_id"]: link for link in preview.get("audit_links", [])}
check("audit_ids_present", set(links) == {"c_hypothesis_001", "c_branch_derive_001"}, sorted(links))
hyp = links["c_hypothesis_001"]
check("hyp_link_hash_64", isinstance(hyp.get("audit_link_hash"), str) and len(hyp["audit_link_hash"]) == 64)
check("hyp_parent_hash_64", isinstance(hyp.get("parent_manifest_hash"), str) and len(hyp["parent_manifest_hash"]) == 64)
check("hyp_candidate_hash_64", isinstance(hyp.get("candidate_hash"), str) and len(hyp["candidate_hash"]) == 64)
check("hyp_hard_gate_hash_64", isinstance(hyp.get("hard_gate_report_hash"), str) and len(hyp["hard_gate_report_hash"]) == 64)
check("hyp_readiness_hash_64", isinstance(hyp.get("seal_readiness_report_hash"), str) and len(hyp["seal_readiness_report_hash"]) == 64)
check("hyp_packet_hash_64", isinstance(hyp.get("seal_packet_hash"), str) and len(hyp["seal_packet_hash"]) == 64)
check("hyp_claim_status_hypothesis", hyp.get("claim_status") == "hypothesis", hyp.get("claim_status"))
check("hyp_no_execution", hyp.get("seal_execution_permitted") is False)
check("hyp_no_memory", hyp.get("memory_promotion_permitted") is False)
check("hyp_link_hash_recomputed", hyp.get("link_hash_recomputed_matches") is True)

preview2 = build_seal_audit_chain_preview()
check("stable_chain_hash_repeat", preview2.get("audit_chain_hash") == preview.get("audit_chain_hash"))
check("stable_link_hash_list_repeat", preview2.get("audit_link_hashes") == preview.get("audit_link_hashes"))

missing = evaluate_seal_audit_chain_request({"use_fixture": True})
check("missing_token_rejected", missing.get("status") == "REJECTED", missing)
check("missing_token_reason", missing.get("reason_code") == "approval_token_required")
check("missing_token_no_writes", missing.get("writes_files") is False and missing.get("writes_memory") is False)

approved = evaluate_seal_audit_chain_request({"approval_token": SEAL_AUDIT_CHAIN_APPROVAL_TOKEN, "use_fixture": True})
check("approved_fixture_status_ok", approved.get("status") == "OK")
check("approved_fixture_accepted", approved.get("accepted") is True)
check("approved_fixture_preview_only", approved.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_fixture_link_count_2", approved.get("audit_link_count") == 2, approved.get("audit_link_count"))
check("approved_fixture_no_seal", approved.get("seals_candidates") is False and approved.get("seal_execution_permitted") is False)
check("approved_fixture_no_memory", approved.get("promotes_to_memory") is False)

bad_packet = evaluate_seal_audit_chain_request({"approval_token": SEAL_AUDIT_CHAIN_APPROVAL_TOKEN, "seal_packet_request": {"approval_token": "BAD_TOKEN", "use_fixture": True}})
check("bad_packet_rejected", bad_packet.get("status") == "REJECTED", bad_packet.get("reason_code"))
check("bad_packet_reason", bad_packet.get("reason_code") == "seal_packet_preview_failed")

print(f"RESULT: PATCH_286_BEHAVIOR {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
