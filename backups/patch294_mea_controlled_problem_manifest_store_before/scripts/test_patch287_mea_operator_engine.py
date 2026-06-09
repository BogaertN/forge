#!/usr/bin/env python3
"""Patch 287 behavior tests — MEA Operator Engine Preview."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
passes = fails = 0

def check(name: str, cond: bool, detail: str = "") -> None:
    global passes, fails
    if cond:
        passes += 1
        print(f"  ✓ [PASS] {name}{' — '+detail if detail else ''}")
    else:
        fails += 1
        print(f"  ✗ [FAIL] {name}{' — '+detail if detail else ''}")

print("PATCH 287 BEHAVIOR TESTS — MEA Operator Engine Preview")
print(f"Forge root: {ROOT}")

from rmc_engine_v1.mea import (
    OPERATOR_ENGINE_PATCH_ID,
    OPERATOR_ENGINE_APPROVAL_TOKEN,
    operator_engine_status,
    operator_engine_boundary,
    build_operator_engine_preview,
    build_operator_engine_rejection_preview,
    evaluate_operator_engine_request,
    run_operator_preview,
    build_144hz_test_manifest,
    canonical_hash,
)

check("patch_id_locked", OPERATOR_ENGINE_PATCH_ID == "Patch 287 — MEA Operator Engine Preview", OPERATOR_ENGINE_PATCH_ID)
status = operator_engine_status()
check("status_ok", status.get("status") == "OK")
check("status_visible", status.get("operator_engine_visible") is True)
check("status_token_locked", status.get("approval_token") == OPERATOR_ENGINE_APPROVAL_TOKEN)
check("status_no_live_execution", status.get("live_operator_execution_active") is False)
check("status_no_draft_sealing", status.get("draft_sealing_active") is False)
check("status_no_rendering", status.get("draft_rendering_active") is False)
check("status_no_memory", status.get("memory_promotion_active") is False)

boundary = operator_engine_boundary()
for key in (
    "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault",
    "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests",
    "commits_live_candidates", "advances_live_manifest", "seals_candidates",
    "promotes_to_memory", "renders_user_output", "mutates_existing_rmc_behavior",
    "mutates_launcher_behavior", "mutates_operator_console_ui", "seal_route_available",
    "memory_promotion_route_available",
):
    check(f"boundary_{key}_false", boundary.get(key) is False, str(boundary.get(key)))
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_creates_post_routes", boundary.get("creates_post_routes") is True)
check("boundary_draft_not_candidate", boundary.get("draft_is_not_candidate") is True)

preview = build_operator_engine_preview()
check("preview_status_ok", preview.get("status") == "OK")
check("preview_draft_count_3", preview.get("draft_count") == 3, str(preview.get("draft_count")))
check("preview_executed_count_3", preview.get("executed_draft_count") == 3, str(preview.get("executed_draft_count")))
check("preview_no_seal", preview.get("candidate_sealing_active") is False)
check("preview_no_memory", preview.get("memory_promotion_active") is False)

ids = [d.get("operator_id") for d in preview.get("draft_results", [])]
check("preview_operator_ids", ids == ["noop_recall", "hypothesize", "branch"], str(ids))
for draft in preview.get("draft_results", []):
    op = draft.get("operator_id")
    check(f"{op}_is_draft", draft.get("is_draft") is True)
    check(f"{op}_not_candidate", draft.get("is_candidate") is False)
    check(f"{op}_not_verified", draft.get("verified") is False)
    check(f"{op}_not_sealed", draft.get("sealed") is False)
    check(f"{op}_not_renderable", draft.get("render_permitted") is False)
    check(f"{op}_no_memory", draft.get("memory_promotion_permitted") is False)
    check(f"{op}_hash_64", isinstance(draft.get("draft_hash"), str) and len(draft.get("draft_hash")) == 64)
    check(f"{op}_theta_hash_64", isinstance(draft.get("theta_hash"), str) and len(draft.get("theta_hash")) == 64)

parent = build_144hz_test_manifest()
noop = run_operator_preview(parent, "noop_recall")
check("noop_executed", noop.draft_executed is True)
check("noop_hash_equals_parent", noop.draft_hash == canonical_hash(parent))
check("noop_reference_not_candidate", noop.is_candidate is False)

hyp = run_operator_preview(parent, "hypothesize", {"hypothesis_id":"harmonic_from_90hz", "hypothesis_text":"144 Hz as harmonic hypothesis", "confidence":0.35})
check("hyp_executed", hyp.draft_executed is True)
check("hyp_changes_hash", hyp.draft_hash != canonical_hash(parent))
check("hyp_claim_status_not_verified", hyp.draft_manifest.get("claim_status") != "verified_claim")
check("hyp_draft_not_sealable", hyp.candidate_sealing_permitted is False)

unknown = run_operator_preview(parent, "made_up_operator")
check("unknown_operator_not_executed", unknown.draft_executed is False)
check("unknown_operator_error", bool(unknown.errors))

repeat = build_operator_engine_preview()
check("preview_hash_stability", [d.get("draft_hash") for d in preview.get("draft_results", [])] == [d.get("draft_hash") for d in repeat.get("draft_results", [])])
check("preview_id_stability", [d.get("draft_id") for d in preview.get("draft_results", [])] == [d.get("draft_id") for d in repeat.get("draft_results", [])])

reject = build_operator_engine_rejection_preview()
check("missing_token_rejected", reject.get("status") == "REJECTED")
check("missing_token_reason", reject.get("reason_code") == "approval_token_required")
check("missing_token_no_writes", reject.get("writes_files") is False and reject.get("writes_memory") is False)

gate_bad = evaluate_operator_engine_request({})
check("gate_empty_rejected", gate_bad.get("status") == "REJECTED")

gate_ok = evaluate_operator_engine_request({"approval_token": OPERATOR_ENGINE_APPROVAL_TOKEN})
check("gate_token_ok", gate_ok.get("status") == "OK")
check("gate_preview_only", gate_ok.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("gate_count_3", gate_ok.get("draft_count") == 3)
check("gate_no_seal", gate_ok.get("seals_candidates") is False)
check("gate_no_memory", gate_ok.get("promotes_to_memory") is False)

gate_single = evaluate_operator_engine_request({"approval_token": OPERATOR_ENGINE_APPROVAL_TOKEN, "operator_id":"branch", "theta_k":{"branch_label":"test", "branch_goal":"Test branch", "branch_unknown":"Test unknown"}})
check("gate_single_ok", gate_single.get("status") == "OK")
check("gate_single_preview_only", gate_single.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("gate_single_not_candidate", gate_single.get("draft_result", {}).get("is_candidate") is False)

print(f"RESULT: PATCH_287_BEHAVIOR {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
