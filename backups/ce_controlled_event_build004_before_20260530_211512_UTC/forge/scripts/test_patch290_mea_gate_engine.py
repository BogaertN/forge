#!/usr/bin/env python3
"""Patch 290 behavior tests — MEA True Gate Engine Extension Preview."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    GATE_ENGINE_APPROVAL_TOKEN,
    GATE_ENGINE_PATCH_ID,
    build_gate_engine_preview,
    build_gate_engine_rejection_preview,
    evaluate_gate_engine_request,
    gate_engine_boundary,
    gate_engine_status,
)

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


print("PATCH 290 BEHAVIOR TESTS — MEA True Gate Engine Extension Preview")
print(f"Forge root: {ROOT}")

status = gate_engine_status()
boundary = gate_engine_boundary()
preview = build_gate_engine_preview()
reports = {r.get("candidate_id"): r for r in preview.get("gate_reports", [])}

check("patch_id_locked", GATE_ENGINE_PATCH_ID == "Patch 290 — True MEA Gate Engine Extension Preview", GATE_ENGINE_PATCH_ID)
check("status_ok", status.get("status") == "OK")
check("status_visible", status.get("gate_engine_visible") is True)
check("status_candidate_count_4", status.get("candidate_count") == 4, status.get("candidate_count"))
check("status_hash_stability", status.get("gate_report_hash_stability_proven") is True)
check("status_score_cannot_override", status.get("score_can_override_gates") is False)
check("status_no_seal", status.get("candidate_sealing_active") is False)
check("status_no_memory", status.get("memory_promotion_active") is False)

for key in [
    "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault",
    "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests",
    "commits_live_candidates", "advances_live_manifest", "seals_candidates",
    "promotes_to_memory", "renders_user_output", "mutates_operator_console_ui",
]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_requires_token", boundary.get("requires_approval_token") is True)
check("boundary_score_cannot_override", boundary.get("score_can_override_gates") is False)

check("preview_status_ok", preview.get("status") == "OK")
check("preview_candidate_count_4", preview.get("candidate_count") == 4, preview.get("candidate_count"))
check("preview_gate_report_count_4", preview.get("gate_report_count") == 4, preview.get("gate_report_count"))
check("preview_selectable_count_2", preview.get("selectable_preview_count") == 2, preview.get("selectable_preview_count"))
check("preview_reference_count_1", preview.get("reference_only_count") == 1, preview.get("reference_only_count"))
check("preview_rejected_count_1", preview.get("rejected_count") == 1, preview.get("rejected_count"))
check("preview_hash_stability", preview.get("gate_report_hash_stability_proven") is True)
check("preview_score_cannot_override", preview.get("score_can_override_gates") is False)
check("preview_no_live_commit", preview.get("live_candidate_commit_active") is False)
check("preview_no_seal", preview.get("candidate_sealing_active") is False and preview.get("seals_candidates") is False)
check("preview_no_memory", preview.get("memory_promotion_active") is False and preview.get("promotes_to_memory") is False)

expected = {
    "cg_recall_001": ("recall", "REFERENCE_ONLY", False, True, True),
    "cg_hypothesis_001": ("hypothesis", "PASS_PREVIEW_ONLY", True, False, True),
    "cg_branch_001": ("speculative_branch", "PASS_BOUNDED_PREVIEW_ONLY", True, False, True),
    "cg_tamper_001": ("rejected", "REJECTED", False, False, False),
}
for cid, (claim, decision, selectable, reference, visible) in expected.items():
    report = reports.get(cid, {})
    check(f"report_exists:{cid}", bool(report))
    check(f"claim_preserved:{cid}", report.get("claim_status") == claim, report.get("claim_status"))
    check(f"decision:{cid}", report.get("decision") == decision, report.get("decision"))
    check(f"selectable:{cid}", report.get("selectable_preview") is selectable, report.get("selectable_preview"))
    check(f"reference_only:{cid}", report.get("reference_only") is reference, report.get("reference_only"))
    check(f"user_visible:{cid}", report.get("user_visible") is visible, report.get("user_visible"))
    check(f"seal_blocked:{cid}", report.get("seal_blocked") is True)
    check(f"memory_blocked:{cid}", report.get("memory_promotion_blocked") is True)
    check(f"score_no_override:{cid}", report.get("score_can_override_gate") is False)
    check(f"hash_64:{cid}", isinstance(report.get("gate_report_hash"), str) and len(report.get("gate_report_hash")) == 64)

# Gate vectors include every named gate and block seal/memory by construction.
for cid, report in reports.items():
    gates = {g.get("gate_name"): g for g in report.get("gate_vector", [])}
    for gate_name in [
        "replay_gate", "tamper_hash_gate", "proof_debt_gate", "convergence_gate",
        "information_gain_gate", "drift_gate", "phase_gate", "claim_status_gate",
        "render_scope_gate", "seal_permission_gate", "memory_permission_gate",
    ]:
        check(f"gate_present:{cid}:{gate_name}", gate_name in gates)
    check(f"seal_gate_false:{cid}", gates.get("seal_permission_gate", {}).get("passed") is False)
    check(f"memory_gate_false:{cid}", gates.get("memory_permission_gate", {}).get("passed") is False)

# Determinism.
preview2 = build_gate_engine_preview()
reports2 = {r.get("candidate_id"): r for r in preview2.get("gate_reports", [])}
check("preview_hash_repeat", preview.get("gate_report_hash") == preview2.get("gate_report_hash"))
for cid, report in reports.items():
    check(f"report_hash_repeat:{cid}", report.get("gate_report_hash") == reports2.get(cid, {}).get("gate_report_hash"))

# Token gate behavior.
rejection = build_gate_engine_rejection_preview()
check("rejection_status", rejection.get("status") == "REJECTED")
check("rejection_reason", rejection.get("reason_code") == "approval_token_required")
check("rejection_no_writes", rejection.get("writes_files") is False and rejection.get("writes_memory") is False)
check("rejection_no_seal", rejection.get("seals_candidates") is False)
check("rejection_no_memory", rejection.get("promotes_to_memory") is False)

missing = evaluate_gate_engine_request({})
check("missing_token_rejected", missing.get("status") == "REJECTED")
check("missing_token_reason", missing.get("reason_code") == "approval_token_required")
check("missing_token_no_commit", missing.get("commits_live_candidates") is False)
check("missing_token_no_seal", missing.get("seals_candidates") is False)
check("missing_token_no_memory", missing.get("promotes_to_memory") is False)

approved = evaluate_gate_engine_request({"approval_token": GATE_ENGINE_APPROVAL_TOKEN})
check("approved_ok", approved.get("status") == "OK")
check("approved_preview_only", approved.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_count_4", approved.get("candidate_count") == 4, approved.get("candidate_count"))
check("approved_no_commit", approved.get("commits_live_candidates") is False)
check("approved_no_seal", approved.get("seals_candidates") is False)
check("approved_no_memory", approved.get("promotes_to_memory") is False)
check("approved_score_cannot_override", approved.get("score_can_override_gates") is False)

print(f"RESULT: PATCH_290_BEHAVIOR {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
