#!/usr/bin/env python3
"""Patch 288 behavior tests — MEA Candidate Generator Runtime Preview."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rmc_engine_v1.mea import (
    CANDIDATE_GENERATOR_PATCH_ID,
    CANDIDATE_GENERATOR_APPROVAL_TOKEN,
    candidate_generator_status,
    candidate_generator_boundary,
    build_candidate_generator_preview,
    evaluate_candidate_generator_request,
)

passed = 0
failed = 0

def check(name: str, cond: bool, detail: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✓ [PASS] {name}{' — ' + detail if detail else ''}")
    else:
        failed += 1
        print(f"  ✗ [FAIL] {name}{' — ' + detail if detail else ''}")

print("PATCH 288 BEHAVIOR TESTS — MEA Candidate Generator Runtime Preview")
print(f"Forge root: {ROOT}")

check("patch_id_locked", CANDIDATE_GENERATOR_PATCH_ID == "Patch 288 — MEA Candidate Generator Runtime Preview")
check("token_locked", CANDIDATE_GENERATOR_APPROVAL_TOKEN == "APPROVE_MEA_CANDIDATE_GENERATOR_PREVIEW")

status = candidate_generator_status()
check("status_ok", status.get("status") == "OK")
check("status_visible", status.get("candidate_generator_visible") is True)
check("status_no_live_commit", status.get("live_candidate_commit_active") is False)
check("status_no_seal", status.get("candidate_sealing_active") is False)
check("status_no_memory", status.get("memory_promotion_active") is False)

boundary = candidate_generator_boundary()
for key in ["writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests", "commits_live_candidates", "advances_live_manifest", "seals_candidates", "promotes_to_memory", "renders_user_output"]:
    check(f"boundary_{key}_false", boundary.get(key) is False, str(boundary.get(key)))
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_requires_token", boundary.get("requires_approval_token") is True)

preview = build_candidate_generator_preview()
check("preview_status_ok", preview.get("status") == "OK")
check("candidate_count_4", preview.get("candidate_count") == 4, str(preview.get("candidate_count")))
check("generated_candidate_count_4", preview.get("generated_candidate_count") == 4)
check("failed_verification_count_1", preview.get("failed_verification_count") == 1, str(preview.get("failed_verification_count")))
check("containment_preview_count_1", preview.get("containment_preview_count") == 1, str(preview.get("containment_preview_count")))
check("drafts_from_operator_engine", preview.get("drafts_generated_by_operator_engine") is True)
check("verification_applied", preview.get("verification_operators_applied") is True)
check("hash_stability", preview.get("candidate_hashes_stable") is True)
check("no_seal_preview", preview.get("seals_candidates") is False and preview.get("candidate_sealing_active") is False)
check("no_memory_preview", preview.get("promotes_to_memory") is False and preview.get("memory_promotion_active") is False)

cands = {c["candidate_id"]: c for c in preview.get("candidates", [])}
for cid in ("cg_recall_001", "cg_hypothesis_001", "cg_branch_001", "cg_tamper_001"):
    check(f"candidate_exists:{cid}", cid in cands)

recall = cands["cg_recall_001"]
check("recall_status", recall.get("claim_status") == "recall", str(recall.get("claim_status")))
check("recall_reference_only", recall.get("reference_only") is True)
check("recall_not_discovery", recall.get("selectable_preview") is False)
check("recall_no_seal", recall.get("candidate_sealing_permitted") is False)
check("recall_no_memory", recall.get("memory_promotion_permitted") is False)

hyp = cands["cg_hypothesis_001"]
check("hypothesis_status", hyp.get("claim_status") == "hypothesis", str(hyp.get("claim_status")))
check("hypothesis_not_verified", hyp.get("claim_status") != "verified_claim")
check("hypothesis_selectable_preview", hyp.get("selectable_preview") is True)
check("hypothesis_no_seal", hyp.get("candidate_sealing_permitted") is False)
check("hypothesis_no_memory", hyp.get("memory_promotion_permitted") is False)
check("hypothesis_no_verified_render", hyp.get("render_permission") == "preview_only_no_verified_language", str(hyp.get("render_permission")))

branch = cands["cg_branch_001"]
check("branch_status", branch.get("claim_status") == "speculative_branch", str(branch.get("claim_status")))
check("branch_not_verified", branch.get("claim_status") != "verified_claim")
check("branch_no_seal", branch.get("candidate_sealing_permitted") is False)

tamper = cands["cg_tamper_001"]
check("tamper_rejected", tamper.get("claim_status") == "rejected", str(tamper.get("claim_status")))
check("tamper_not_visible", tamper.get("user_visible") is False)
check("tamper_containment", tamper.get("containment_preview") is True)
check("tamper_replay_gate_failed", any(g.get("check_name") == "check_replay" and g.get("passed") is False for g in tamper.get("verification_gates", [])))

preview2 = build_candidate_generator_preview()
cands2 = {c["candidate_id"]: c for c in preview2.get("candidates", [])}
for cid, item in cands.items():
    check(f"deterministic_candidate_hash:{cid}", item.get("candidate_hash") == cands2.get(cid, {}).get("candidate_hash"))

missing = evaluate_candidate_generator_request({})
check("missing_token_rejected", missing.get("status") == "REJECTED")
check("missing_token_reason", missing.get("reason_code") == "approval_token_required")
check("missing_token_no_writes", missing.get("writes_files") is False and missing.get("writes_memory") is False)

approved = evaluate_candidate_generator_request({"approval_token": CANDIDATE_GENERATOR_APPROVAL_TOKEN})
check("approved_ok", approved.get("status") == "OK")
check("approved_preview_only", approved.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_count_4", approved.get("candidate_count") == 4)
check("approved_no_commit", approved.get("commits_live_candidates") is False)
check("approved_no_seal", approved.get("seals_candidates") is False)
check("approved_no_memory", approved.get("promotes_to_memory") is False)

print(f"RESULT: PATCH_288_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
sys.exit(0 if failed == 0 else 1)
