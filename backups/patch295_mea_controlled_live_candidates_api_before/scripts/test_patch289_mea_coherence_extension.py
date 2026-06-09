#!/usr/bin/env python3
"""Patch 289 behavior tests — MEA Coherence Scorer Extension Preview."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rmc_engine_v1.mea.coherence_extension import (
    COHERENCE_EXTENSION_APPROVAL_TOKEN,
    COHERENCE_EXTENSION_PATCH_ID,
    build_coherence_extension_preview,
    build_coherence_extension_rejection_preview,
    coherence_extension_boundary,
    coherence_extension_status,
    evaluate_coherence_extension_request,
)

passes = 0
fails = 0

def check(name: str, condition: bool, detail: object = "") -> None:
    global passes, fails
    if condition:
        passes += 1
        print(f"  ✓ [PASS] {name}{' — ' + str(detail) if detail != '' else ''}")
    else:
        fails += 1
        print(f"  ✗ [FAIL] {name}{' — ' + str(detail) if detail != '' else ''}")

print("PATCH 289 BEHAVIOR TESTS — MEA Coherence Extension Preview")
print(f"Forge root: {ROOT}")

status = coherence_extension_status()
check("patch_id_locked", status.get("current_patch") == COHERENCE_EXTENSION_PATCH_ID, status.get("current_patch"))
check("status_ok", status.get("status") == "OK")
check("status_visible", status.get("coherence_extension_visible") is True)
check("status_score_can_rank", status.get("score_can_rank") is True)
check("status_score_cannot_override_gates", status.get("score_can_override_gates") is False)
check("status_no_seal", status.get("candidate_sealing_active") is False and status.get("seal_route_available") is False)
check("status_no_memory", status.get("memory_promotion_active") is False)
check("status_rmc_fallback_terms", set(status.get("fallback_terms", [])) == {"R", "P", "U", "N"})
check("status_mea_terms", set(status.get("uses_mea_terms", [])) == {"I", "Omega", "A", "D", "B", "K"})

boundary = coherence_extension_boundary()
for key in (
    "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault",
    "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests",
    "commits_live_candidates", "advances_live_manifest", "seals_candidates",
    "promotes_to_memory", "renders_user_output", "mutates_operator_console_ui",
):
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_token_required", boundary.get("requires_approval_token") is True)
check("boundary_score_cannot_override", boundary.get("score_can_override_gates") is False)

preview = build_coherence_extension_preview()
check("preview_status_ok", preview.get("status") == "OK")
check("candidate_count_4", preview.get("candidate_count") == 4, preview.get("candidate_count"))
check("score_hash_stability", preview.get("score_hash_stability_proven") is True)
check("score_can_rank", preview.get("score_can_rank") is True)
check("score_cannot_override_gates", preview.get("score_can_override_gates") is False)
check("score_cannot_promote_claim", preview.get("score_can_promote_claim_status") is False)
check("score_cannot_render", preview.get("score_can_permit_render") is False)
check("score_cannot_seal", preview.get("score_can_permit_seal") is False)
check("score_cannot_promote_memory", preview.get("score_can_promote_memory") is False)
check("preview_no_live_commit", preview.get("live_candidate_commit_active") is False)
check("preview_no_seal", preview.get("candidate_sealing_active") is False and preview.get("seals_candidates") is False)
check("preview_no_memory", preview.get("memory_promotion_active") is False and preview.get("promotes_to_memory") is False)
check("candidate_generator_source", preview.get("candidate_generator_preview_summary", {}).get("drafts_generated_by_operator_engine") is True)
check("verification_applied", preview.get("candidate_generator_preview_summary", {}).get("verification_operators_applied") is True)

scores = {item.get("candidate_id"): item for item in preview.get("scored_candidates", [])}
for cid in ("cg_recall_001", "cg_hypothesis_001", "cg_branch_001", "cg_tamper_001"):
    check(f"score_exists:{cid}", cid in scores)
    item = scores.get(cid, {})
    check(f"candidate_score_can_rank:{cid}", item.get("score_can_rank") is True)
    check(f"candidate_score_cannot_override:{cid}", item.get("score_can_override_gate") is False)
    check(f"candidate_gate_override_blocked:{cid}", item.get("gate_override_blocked") is True)
    check(f"candidate_claim_preserved:{cid}", item.get("original_claim_status_preserved") is True)
    check(f"candidate_no_claim_promotion:{cid}", item.get("claim_status_after_score") == item.get("claim_status"))
    check(f"candidate_no_seal_by_score:{cid}", item.get("score_can_permit_seal") is False)
    check(f"candidate_no_memory_by_score:{cid}", item.get("score_can_promote_memory") is False)
    check(f"score_hash_64:{cid}", isinstance(item.get("score_hash"), str) and len(item.get("score_hash")) == 64)

recall = scores.get("cg_recall_001", {})
check("recall_status_preserved", recall.get("claim_status") == "recall", recall.get("claim_status"))
check("recall_reference_only", recall.get("reference_only") is True)
check("recall_not_rank_eligible", recall.get("rank_eligible") is False)
check("recall_effective_score_zero", recall.get("effective_rank_score") == 0.0, recall.get("effective_rank_score"))
check("recall_not_discovery_reason", recall.get("ranking_block_reason") == "reference_only_recall_not_discovery", recall.get("ranking_block_reason"))

hyp = scores.get("cg_hypothesis_001", {})
check("hypothesis_status_preserved", hyp.get("claim_status") == "hypothesis", hyp.get("claim_status"))
check("hypothesis_not_verified", hyp.get("claim_status_after_score") != "verified_claim", hyp.get("claim_status_after_score"))
check("hypothesis_high_debt_blocks_verified", float(hyp.get("proof_debt_penalty", 0.0)) >= 0.20)
check("hypothesis_score_does_not_seal", hyp.get("score_can_permit_seal") is False)

branch = scores.get("cg_branch_001", {})
check("branch_status_preserved", branch.get("claim_status") == "speculative_branch", branch.get("claim_status"))
check("branch_not_verified", branch.get("claim_status_after_score") != "verified_claim")
check("branch_score_does_not_seal", branch.get("score_can_permit_seal") is False)

tamper = scores.get("cg_tamper_001", {})
check("tamper_rejected", tamper.get("claim_status") == "rejected", tamper.get("claim_status"))
check("tamper_gate_failed", tamper.get("candidate_gate_failed") is True)
check("tamper_not_rank_eligible", tamper.get("rank_eligible") is False)
check("tamper_effective_score_zero", tamper.get("effective_rank_score") == 0.0, tamper.get("effective_rank_score"))
check("tamper_score_cannot_rescue", tamper.get("ranking_block_reason") == "hard_gate_failed_or_rejected", tamper.get("ranking_block_reason"))

rejected = build_coherence_extension_rejection_preview()
check("missing_token_rejected", rejected.get("status") == "REJECTED")
check("missing_token_reason", rejected.get("reason_code") == "approval_token_required")
check("missing_token_no_writes", rejected.get("writes_files") is False and rejected.get("writes_memory") is False)
check("missing_token_score_cannot_override", rejected.get("score_can_override_gate") is False)

bad = evaluate_coherence_extension_request({})
check("empty_request_rejected", bad.get("status") == "REJECTED")
check("empty_request_no_seal", bad.get("seals_candidates") is False)

approved = evaluate_coherence_extension_request({"approval_token": COHERENCE_EXTENSION_APPROVAL_TOKEN})
check("approved_ok", approved.get("status") == "OK")
check("approved_preview_only", approved.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_count_4", approved.get("candidate_count") == 4)
check("approved_no_commit", approved.get("commits_live_candidates") is False)
check("approved_no_seal", approved.get("seals_candidates") is False)
check("approved_no_memory", approved.get("promotes_to_memory") is False)
check("approved_score_cannot_override", approved.get("score_can_override_gates") is False)

print(f"RESULT: PATCH_289_BEHAVIOR {'PASS' if fails == 0 else 'FAIL'}  Total:{passes + fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
