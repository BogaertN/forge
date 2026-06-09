#!/usr/bin/env python3
"""Patch 283 behavior tests — MEA Hard Gate Report / Candidate Gate Engine Preview."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    HARD_GATE_REPORT_APPROVAL_TOKEN,
    HARD_GATE_REPORT_PATCH_ID,
    build_hard_gate_report_preview,
    build_hard_gate_report_gate_preview,
    build_hard_gate_report_rejection_preview,
    build_144hz_test_manifest,
    evaluate_hard_gate_report_request,
    hard_gate_report_boundary,
    hard_gate_report_status,
    to_dict,
)

results: list[tuple[bool, str, str]] = []


def record(ok: bool, name: str, detail: object = "") -> None:
    details = "" if detail == "" else f" — {detail}"
    print(f"  {'✓ [PASS]' if ok else '✗ [FAIL]'} {name}{details}")
    results.append((ok, name, str(detail)[:240]))


def by_id(report: dict) -> dict:
    return {c.get("candidate_id"): c for c in report.get("candidate_gate_reports", [])}


def main() -> int:
    print("PATCH 283R BEHAVIOR TESTS — MEA Hard Gate Report POST Dispatch Hotfix")
    print(f"Forge root: {ROOT}")

    boundary = hard_gate_report_boundary()
    status = hard_gate_report_status()
    report = build_hard_gate_report_preview()
    candidates = by_id(report)

    record(HARD_GATE_REPORT_PATCH_ID == "Patch 283R — MEA Hard Gate Report POST Dispatch Hotfix", "patch_id_locked_283R", HARD_GATE_REPORT_PATCH_ID)
    record(status.get("status") == "OK", "status_ok")
    record(status.get("approval_required") is True, "status_approval_required")
    record(status.get("approval_token") == HARD_GATE_REPORT_APPROVAL_TOKEN, "status_token_locked")
    record(status.get("live_candidate_commit_active") is False, "status_live_candidate_commit_inactive")
    record(status.get("candidate_sealing_active") is False, "status_candidate_sealing_inactive")
    record(status.get("memory_promotion_active") is False, "status_memory_promotion_inactive")

    record(boundary.get("non_mutating") is True, "boundary_non_mutating")
    record(boundary.get("creates_get_routes") is True, "boundary_creates_get_routes")
    record(boundary.get("creates_post_routes") is True, "boundary_creates_post_routes")
    record(boundary.get("requires_approval_token") is True, "boundary_requires_approval")
    for key in (
        "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault",
        "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests",
        "commits_live_candidates", "seals_candidates", "promotes_to_memory",
        "renders_user_output", "mutates_existing_rmc_behavior", "mutates_launcher_behavior",
        "mutates_operator_console_ui", "seal_route_available", "memory_promotion_route_available",
    ):
        record(boundary.get(key) is False, f"boundary_{key}_false", boundary.get(key))

    record(report.get("status") == "OK", "preview_status_ok")
    record(report.get("candidate_count") == 4, "preview_candidate_count_4", report.get("candidate_count"))
    record(report.get("selectable_preview_count") == 2, "preview_selectable_count_2", report.get("selectable_preview_count"))
    record(report.get("rejected_count") == 1, "preview_rejected_count_1", report.get("rejected_count"))
    record(report.get("reference_only_count") == 1, "preview_reference_count_1", report.get("reference_only_count"))
    record(report.get("best_candidate_id") == "c_hypothesis_001", "preview_best_candidate_hypothesis", report.get("best_candidate_id"))
    record(report.get("candidate_sealing_active") is False, "preview_sealing_inactive")
    record(report.get("memory_promotion_active") is False, "preview_memory_promotion_inactive")
    record(report.get("hard_laws", {}).get("hard_gates_override_preview_score") is True, "hard_law_gates_override_score")
    record(report.get("hard_laws", {}).get("seal_blocked_in_patch_283") is True, "hard_law_seal_blocked")

    recall = candidates.get("c_recall_001", {})
    hypothesis = candidates.get("c_hypothesis_001", {})
    branch = candidates.get("c_branch_derive_001", {})
    tamper = candidates.get("c_rejected_tamper_001", {})

    record(recall.get("hard_gate_decision") == "REFERENCE_ONLY", "recall_reference_only", recall.get("hard_gate_decision"))
    record(recall.get("hard_gate_passed") is False, "recall_not_selectable")
    record(recall.get("reference_only") is True, "recall_reference_flag")
    record(recall.get("gates_failed") == 0, "recall_safety_gates_pass")

    record(hypothesis.get("hard_gate_decision") == "PASS_PREVIEW_ONLY", "hypothesis_pass_preview", hypothesis.get("hard_gate_decision"))
    record(hypothesis.get("claim_status") == "hypothesis", "hypothesis_claim_status")
    record(hypothesis.get("selectable_preview") is True, "hypothesis_selectable_preview")
    record(hypothesis.get("gates_failed") == 0, "hypothesis_all_hard_gates_pass")
    record(hypothesis.get("seal_blocked") is True, "hypothesis_seal_blocked")
    record(hypothesis.get("memory_promotion_blocked") is True, "hypothesis_memory_blocked")

    record(branch.get("hard_gate_decision") == "PASS_BOUNDED_PREVIEW_ONLY", "branch_bounded_preview", branch.get("hard_gate_decision"))
    record(branch.get("claim_status") == "speculative_branch", "branch_speculative_status", branch.get("claim_status"))
    record(branch.get("selectable_preview") is True, "branch_selectable_preview")
    record(branch.get("seal_blocked") is True, "branch_seal_blocked")

    record(tamper.get("hard_gate_decision") == "REJECTED", "tamper_rejected", tamper.get("hard_gate_decision"))
    record(tamper.get("rejected") is True, "tamper_rejected_flag")
    record(tamper.get("gates_failed", 0) >= 1, "tamper_has_failed_gates", tamper.get("gates_failed"))
    gate_names = {g.get("gate_name"): g for g in tamper.get("gate_checks", [])}
    record(gate_names.get("replay_gate", {}).get("passed") is False, "tamper_replay_gate_failed")
    record(gate_names.get("tamper_gate", {}).get("passed") is False, "tamper_hash_gate_failed")

    record(all(c.get("candidate_sealing_permitted") is False for c in report.get("candidate_gate_reports", [])), "all_candidates_no_seal_permission")
    record(all(c.get("memory_promotion_permitted") is False for c in report.get("candidate_gate_reports", [])), "all_candidates_no_memory_promotion")

    rejected = evaluate_hard_gate_report_request({"use_fixture": True})
    record(rejected.get("status") == "REJECTED", "missing_token_rejected", rejected)
    record(rejected.get("reason_code") == "approval_token_required", "missing_token_reason")
    record(rejected.get("writes_files") is False, "missing_token_no_writes")

    approved = evaluate_hard_gate_report_request({"approval_token": HARD_GATE_REPORT_APPROVAL_TOKEN, "use_fixture": True})
    record(approved.get("status") == "OK", "approved_fixture_status_ok")
    record(approved.get("accepted") is True, "approved_fixture_accepted")
    record(approved.get("gate_status") == "ACCEPTED_PREVIEW_ONLY", "approved_fixture_preview_only")
    record(approved.get("candidate_count") == 4, "approved_fixture_candidate_count_4")
    record(approved.get("seals_candidates") is False, "approved_fixture_no_seal")
    record(approved.get("promotes_to_memory") is False, "approved_fixture_no_memory_promotion")

    main_text = (ROOT / "main.py").read_text(encoding="utf-8", errors="replace")
    record('_p283_mea_hard_gate_report_gate_post_v1(req, self.path)' in main_text, "main_post_dispatch_hard_gate")
    record('/api/mea/candidate-hard-gate' in main_text, "main_post_dispatch_alias_present")

    bad_seed = to_dict(build_144hz_test_manifest())
    bad_seed["unknowns"] = []
    bad = evaluate_hard_gate_report_request({
        "approval_token": HARD_GATE_REPORT_APPROVAL_TOKEN,
        "manifest": bad_seed,
        "source": "bad_missing_unknowns",
    })
    record(bad.get("status") == "REJECTED", "bad_seed_rejected")
    record(bad.get("reason_code") == "candidate_set_gate_failed", "bad_seed_reason", bad.get("reason_code"))
    record(bad.get("candidate_count") == 0, "bad_seed_no_candidates")

    passed = sum(1 for ok, _, _ in results if ok)
    total = len(results)
    failed = total - passed
    print(f"RESULT: PATCH_283R_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
