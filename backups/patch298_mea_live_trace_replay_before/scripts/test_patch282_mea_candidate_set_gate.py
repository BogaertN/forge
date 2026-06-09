#!/usr/bin/env python3
"""Patch 282 behavior tests — MEA Candidate Set Preview/Gate."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    CANDIDATE_SET_GATE_APPROVAL_TOKEN,
    CANDIDATE_SET_GATE_PATCH_ID,
    build_144hz_test_manifest,
    build_candidate_set_preview,
    candidate_set_gate_boundary,
    candidate_set_gate_status,
    evaluate_candidate_set_request,
    to_dict,
)

results: list[tuple[bool, str, str]] = []


def record(ok: bool, name: str, detail: object = "") -> None:
    details = "" if detail == "" else f" — {detail}"
    print(f"  {'✓ [PASS]' if ok else '✗ [FAIL]'} {name}{details}")
    results.append((ok, name, str(detail)[:240]))


def by_id(preview: dict) -> dict:
    return {c.get("candidate_id"): c for c in preview.get("candidates", [])}


def main() -> int:
    print("PATCH 282 BEHAVIOR TESTS — MEA Candidate Set Preview/Gate")
    print(f"Forge root: {ROOT}")

    boundary = candidate_set_gate_boundary()
    status = candidate_set_gate_status()
    preview = build_candidate_set_preview()
    candidates = by_id(preview)

    record(CANDIDATE_SET_GATE_PATCH_ID == "Patch 282 — MEA Candidate Set Preview/Gate", "patch_id_locked", CANDIDATE_SET_GATE_PATCH_ID)
    record(status.get("status") == "OK", "status_ok")
    record(status.get("approval_required") is True, "status_approval_required")
    record(status.get("approval_token") == CANDIDATE_SET_GATE_APPROVAL_TOKEN, "status_token_locked")
    record(status.get("live_candidate_commit_active") is False, "status_live_candidate_commit_inactive")
    record(status.get("candidate_sealing_active") is False, "status_candidate_sealing_inactive")
    record(status.get("memory_promotion_active") is False, "status_memory_promotion_inactive")

    record(boundary.get("non_mutating") is True, "boundary_non_mutating")
    record(boundary.get("creates_post_routes") is True, "boundary_creates_post_routes")
    record(boundary.get("requires_approval_token") is True, "boundary_requires_approval")
    for key in ("writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests", "seals_candidates", "promotes_to_memory", "renders_user_output", "mutates_existing_rmc_behavior", "mutates_launcher_behavior", "mutates_operator_console_ui"):
        record(boundary.get(key) is False, f"boundary_{key}_false", boundary.get(key))

    record(preview.get("status") == "OK", "preview_status_ok")
    record(preview.get("candidate_count") == 4, "preview_candidate_count_4", preview.get("candidate_count"))
    record(preview.get("accepted_preview_count") == 2, "preview_accepted_count_2", preview.get("accepted_preview_count"))
    record(preview.get("rejected_count") == 1, "preview_rejected_count_1", preview.get("rejected_count"))
    record(preview.get("reference_only_count") == 1, "preview_reference_count_1", preview.get("reference_only_count"))
    record(preview.get("best_candidate_id") == "c_hypothesis_001", "preview_best_candidate_hypothesis", preview.get("best_candidate_id"))
    record(preview.get("candidate_sealing_active") is False, "preview_sealing_inactive")
    record(preview.get("memory_promotion_active") is False, "preview_memory_promotion_inactive")

    recall = candidates.get("c_recall_001", {})
    hypothesis = candidates.get("c_hypothesis_001", {})
    branch = candidates.get("c_branch_derive_001", {})
    tamper = candidates.get("c_rejected_tamper_001", {})

    record(recall.get("gate_status") == "REFERENCE_ONLY", "recall_reference_only", recall.get("gate_status"))
    record(recall.get("claim_status_report", {}).get("claim_status") == "recall", "recall_claim_status")
    record("discovery" in " ".join(recall.get("claim_status_report", {}).get("cannot_render_as", [])), "recall_cannot_render_discovery")

    record(hypothesis.get("gate_status") == "ACCEPTED_PREVIEW_ONLY", "hypothesis_accepted_preview")
    record(hypothesis.get("claim_status_report", {}).get("claim_status") == "hypothesis", "hypothesis_claim_status")
    record(hypothesis.get("claim_status_report", {}).get("proof_debt") == 0.7, "hypothesis_proof_debt_070", hypothesis.get("claim_status_report", {}).get("proof_debt"))
    record("verified fact" in " ".join(hypothesis.get("claim_status_report", {}).get("cannot_render_as", [])), "hypothesis_cannot_render_verified")
    record(hypothesis.get("score_bundle", {}).get("information_gain", {}).get("information_gain", 0) > 0, "hypothesis_positive_information_gain", hypothesis.get("score_bundle", {}).get("information_gain", {}).get("information_gain"))
    record(hypothesis.get("replay_report", {}).get("replay_confirmed") is True, "hypothesis_replay_confirmed")

    record(branch.get("gate_status") == "ACCEPTED_PREVIEW_ONLY", "branch_accepted_preview", branch.get("gate_status"))
    record(branch.get("claim_status_report", {}).get("claim_status") in {"speculative_branch", "hypothesis", "test_required", "partial_resolution"}, "branch_status_bounded", branch.get("claim_status_report", {}).get("claim_status"))
    record(branch.get("candidate_sealing_permitted") is False, "branch_no_seal_permission")

    record(tamper.get("gate_status") == "REJECTED", "tamper_rejected", tamper.get("gate_status"))
    record(tamper.get("claim_status_report", {}).get("claim_status") == "rejected", "tamper_claim_rejected")
    record(tamper.get("replay_report", {}).get("tamper_detected") is True, "tamper_detected")
    record(tamper.get("claim_status_report", {}).get("user_visible") is False, "tamper_not_user_visible")

    record(all(c.get("candidate_sealing_permitted") is False for c in preview.get("candidates", [])), "all_candidates_no_seal_permission")
    record(all(c.get("memory_promotion_permitted") is False for c in preview.get("candidates", [])), "all_candidates_no_memory_promotion")

    reject = evaluate_candidate_set_request({"use_fixture": True})
    record(reject.get("status") == "REJECTED", "missing_token_rejected", reject)
    record(reject.get("reason_code") == "approval_token_required", "missing_token_reason")
    record(reject.get("writes_files") is False, "missing_token_no_writes")

    approved = evaluate_candidate_set_request({"approval_token": CANDIDATE_SET_GATE_APPROVAL_TOKEN, "use_fixture": True})
    record(approved.get("status") == "OK", "approved_fixture_status_ok")
    record(approved.get("accepted") is True, "approved_fixture_accepted")
    record(approved.get("gate_status") == "ACCEPTED_PREVIEW_ONLY", "approved_fixture_preview_only")
    record(approved.get("candidate_count") == 4, "approved_fixture_candidate_count_4")
    record(approved.get("seals_candidates") is False, "approved_fixture_no_seal")
    record(approved.get("promotes_to_memory") is False, "approved_fixture_no_memory_promotion")

    bad_seed = to_dict(build_144hz_test_manifest())
    bad_seed["unknowns"] = []
    bad = evaluate_candidate_set_request({
        "approval_token": CANDIDATE_SET_GATE_APPROVAL_TOKEN,
        "manifest": bad_seed,
        "source": "bad_missing_unknowns",
    })
    record(bad.get("status") == "REJECTED", "bad_seed_rejected")
    record(bad.get("reason_code") == "seed_manifest_gate_failed", "bad_seed_reason", bad.get("reason_code"))
    record(bad.get("candidate_count") == 0, "bad_seed_no_candidates")

    rendered_seed = to_dict(build_144hz_test_manifest())
    rendered_seed["output_permissions"] = "render_allowed"
    rendered = evaluate_candidate_set_request({
        "approval_token": CANDIDATE_SET_GATE_APPROVAL_TOKEN,
        "manifest": rendered_seed,
        "source": "bad_render_allowed_seed",
    })
    record(rendered.get("status") == "REJECTED", "render_allowed_seed_rejected")
    record(rendered.get("candidate_count") == 0, "render_allowed_seed_no_candidates")

    passed = sum(1 for ok, _, _ in results if ok)
    total = len(results)
    failed = total - passed
    print(f"RESULT: PATCH_282_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
