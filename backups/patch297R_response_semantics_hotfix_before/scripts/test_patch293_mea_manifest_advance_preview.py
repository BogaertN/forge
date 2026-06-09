#!/usr/bin/env python3
"""Patch 293 behavior tests — MEA Live Manifest Advance Preview."""
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


print("PATCH 293 BEHAVIOR TESTS — MEA Live Manifest Advance Preview")
print(f"Forge root: {ROOT}")

from rmc_engine_v1.mea import (  # noqa: E402
    MANIFEST_ADVANCE_PREVIEW_FORMULA,
    MANIFEST_ADVANCE_PREVIEW_PATCH_ID,
    MANIFEST_ADVANCE_PREVIEW_ROUTE,
    MANIFEST_ADVANCE_PREVIEW_SCHEMA_VERSION,
    build_manifest_advance_preview,
    kernel_identity,
    manifest_advance_preview_boundary,
)

check("patch_id_locked", MANIFEST_ADVANCE_PREVIEW_PATCH_ID == "Patch 293 — MEA Live Manifest Advance Preview", MANIFEST_ADVANCE_PREVIEW_PATCH_ID)
check("schema_locked", MANIFEST_ADVANCE_PREVIEW_SCHEMA_VERSION == "mea_manifest_advance_preview_v1_patch293", MANIFEST_ADVANCE_PREVIEW_SCHEMA_VERSION)
check("route_locked", MANIFEST_ADVANCE_PREVIEW_ROUTE == "/api/mea/manifest-advance-preview")
check("formula_transition", "M_(t+1)^preview" in MANIFEST_ADVANCE_PREVIEW_FORMULA)
check("formula_no_persistence", "persistence=false" in MANIFEST_ADVANCE_PREVIEW_FORMULA)

boundary = manifest_advance_preview_boundary()
for key in [
    "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault",
    "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests",
    "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal",
    "promotes_to_memory", "renders_user_output", "mutates_operator_console_ui",
]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
check("boundary_read_only", boundary.get("read_only") is True)
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_get_only", boundary.get("creates_get_routes") is True and boundary.get("creates_post_routes") is False)
check("boundary_consumes_response_preview", boundary.get("consumes_sealed_candidate_response_preview") is True)
check("boundary_hash_binding_deferred", boundary.get("output_hash_binding_deferred_until_persistence") is True)
check("boundary_no_real_seal", boundary.get("seal_route_available") is False)
check("boundary_no_live_manifest_route", boundary.get("live_problem_manifest_route_available") is False)

preview = build_manifest_advance_preview()
repeat = build_manifest_advance_preview()
check("preview_ok", preview.get("status") == "OK")
check("preview_type", preview.get("preview_type") == "mea_live_manifest_advance_preview_no_persistence")
check("selected_candidate_hypothesis", preview.get("selected_candidate_id") == "cg_hypothesis_001")
check("old_manifest_hash_64", isinstance(preview.get("old_manifest_hash"), str) and len(preview.get("old_manifest_hash")) == 64)
check("selected_candidate_hash_64", isinstance(preview.get("selected_candidate_hash"), str) and len(preview.get("selected_candidate_hash")) == 64)
check("selected_sealed_candidate_hash_64", isinstance(preview.get("selected_sealed_candidate_hash"), str) and len(preview.get("selected_sealed_candidate_hash")) == 64)
check("new_manifest_hash_64", isinstance(preview.get("new_manifest_hash"), str) and len(preview.get("new_manifest_hash")) == 64)
check("transition_preview_hash_64", isinstance(preview.get("transition_preview_hash"), str) and len(preview.get("transition_preview_hash")) == 64)
check("new_hash_differs_from_old", preview.get("new_manifest_hash") != preview.get("old_manifest_hash"))
check("parent_hash_matches", preview.get("old_manifest_hash_matches_candidate_parent") is True)
check("new_hash_stability", preview.get("new_manifest_hash_stability_proven") is True)
check("transition_hash_stability", preview.get("transition_preview_hash_stability_proven") is True)
check("repeat_new_hash", preview.get("new_manifest_hash") == repeat.get("new_manifest_hash"))
check("repeat_transition_hash", preview.get("transition_preview_hash") == repeat.get("transition_preview_hash"))

op = preview.get("operator_history_update", {})
check("operator_history_before_zero", op.get("before_count") == 0, op.get("before_count"))
check("operator_history_after_one", op.get("after_count") == 1, op.get("after_count"))
check("operator_history_appends_selection", op.get("appended_operator_id") == "select_sealed_candidate_preview")
check("operator_history_binds_selected_hash", op.get("selected_sealed_candidate_hash") == preview.get("selected_sealed_candidate_hash"))
check("operator_output_hash_binding_deferred", op.get("output_hash_binding_deferred_until_persistence") is True)

status = preview.get("claim_status_history_update", {})
check("claim_before_test_required", status.get("before") == "test_required", status.get("before"))
check("claim_after_hypothesis", status.get("proposed_after") == "hypothesis", status.get("proposed_after"))
check("claim_never_upgraded_verified", status.get("claim_promotion_to_verified_fact") is False)

unknowns = preview.get("unknown_vector_update", {})
check("unknown_count_before_2", unknowns.get("before_count") == 2, unknowns.get("before_count"))
check("unknown_count_after_3", unknowns.get("proposed_after_count") == 3, unknowns.get("proposed_after_count"))
check("unknown_resolution_zero", unknowns.get("resolved_unknown_count") == 0, unknowns.get("resolved_unknown_count"))
check("unknown_adds_test_required_gap", len(unknowns.get("added_unknowns", [])) == 1, unknowns.get("added_unknowns"))
check("unknown_does_not_claim_evidence", unknowns.get("evidence_resolution_claimed") is False)

proof = preview.get("proof_debt_update", {})
check("proof_before_085", proof.get("before") == 0.85, proof.get("before"))
check("proof_after_085", proof.get("proposed_after") == 0.85, proof.get("proposed_after"))
check("proof_delta_zero", proof.get("delta") == 0.0, proof.get("delta"))
check("proof_no_evidence_added", proof.get("evidence_added") is False)
check("proof_never_verified", proof.get("verified_claim_permitted") is False)

phase = preview.get("phase_path_update", {})
check("phase_before_empty", phase.get("before") == [], phase.get("before"))
check("phase_after_records_phi5", phase.get("proposed_after") == ["Phi5"], phase.get("proposed_after"))
check("phase_state_unchanged", phase.get("phase_state_before") == "Phi5" and phase.get("phase_state_after") == "Phi5")
check("phase_not_executed", phase.get("phase_transition_executed") is False)

old_manifest = preview.get("old_manifest_preview", {})
new_manifest = preview.get("new_manifest_preview", {})
check("future_manifest_valid", preview.get("new_manifest_validation", {}).get("valid") is True)
check("known_facts_not_invented", old_manifest.get("known_facts") == new_manifest.get("known_facts"))
check("future_manifest_hypothesis", new_manifest.get("claim_status") == "hypothesis", new_manifest.get("claim_status"))
check("future_output_stays_sealed", new_manifest.get("output_permissions") == "sealed", new_manifest.get("output_permissions"))
check("future_proof_preserved", new_manifest.get("proof_debt") == 0.85, new_manifest.get("proof_debt"))
check("future_unknowns_three", len(new_manifest.get("unknowns", [])) == 3)
check("future_operator_history_one", len(new_manifest.get("operator_history", [])) == 1)

for key in [
    "selected_sealed_candidate_live", "seal_execution_permitted", "seals_candidates",
    "commits_live_candidates", "advances_live_manifest", "persistence_permitted", "persisted",
    "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm",
    "executes_shell", "performs_network_io", "renders_user_output", "promotes_to_memory",
    "seal_route_available", "live_problem_manifest_route_available",
]:
    check(f"preview_{key}_false", preview.get(key) is False, preview.get(key))
check("preview_output_hash_binding_deferred", preview.get("output_hash_binding_deferred_until_persistence") is True)

branch = build_manifest_advance_preview("cg_branch_001")
check("branch_preview_ok", branch.get("status") == "OK")
check("branch_claim_speculative", branch.get("claim_status_history_update", {}).get("proposed_after") == "speculative_branch")
check("branch_no_persistence", branch.get("advances_live_manifest") is False and branch.get("writes_memory") is False)
check("branch_hash_stable", branch.get("new_manifest_hash_stability_proven") is True)

kernel = kernel_identity()
check("kernel_stage_patch293", kernel.get("kernel_stage") == "manifest_advance_preview_patch293", kernel.get("kernel_stage"))
check("kernel_manifest_advance_visible", kernel.get("manifest_advance_preview_visible") is True)
check("kernel_manifest_advance_inactive", kernel.get("live_manifest_advance_active") is False)
check("kernel_manifest_persistence_inactive", kernel.get("manifest_persistence_active") is False)
check("kernel_no_real_seal", kernel.get("seal_route_available") is False)

print(f"RESULT: PATCH_293_BEHAVIOR {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
