#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C11 Active Loop State."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from rmc_engine_v1.active_loop_state import (
    active_loop_boundary,
    active_loop_schema_contract,
    build_active_loop_state,
)


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"[FAIL] {name} :: {detail}")
    print(f"[PASS] {name}" + (f" :: {detail}" if detail else ""))


def make_memory_root() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="rmc_c11_loopstate_"))
    dataset = tmp / "memory" / "rmc_dataset_v1"
    for rel in [
        "raw_events/20260525",
        "dataset_receipts/20260525",
        "review_queue/20260525",
        "indexes",
    ]:
        (dataset / rel).mkdir(parents=True, exist_ok=True)
    (dataset / "raw_events/20260525/rmcobs_test.json").write_text(json.dumps({
        "event_id": "rmcobs_test",
        "content": "active loop state memory event",
        "phase": "Φ6",
    }), encoding="utf-8")
    (dataset / "dataset_receipts/20260525/rmcobs_test_receipt.json").write_text(json.dumps({
        "receipt_id": "rmcobs_test_receipt",
        "event_id": "rmcobs_test",
        "status": "captured",
    }), encoding="utf-8")
    (dataset / "review_queue/20260525/rmccand_test_review.json").write_text(json.dumps({
        "review_id": "rmccand_test_review",
        "candidate_id": "rmccand_test",
        "review_status": "pending",
    }), encoding="utf-8")
    (dataset / "indexes/events_index.jsonl").write_text(json.dumps({"event_id": "rmcobs_test"}) + "\n", encoding="utf-8")
    return tmp


def strong_pipeline() -> dict:
    return {
        "status": "OK",
        "pipeline_summary_id": "rmcpipe_strong",
        "pipeline_verdict": "pipeline_ready_no_commit_attempted",
        "first_blocker": None,
        "source_reports_included": True,
        "gate_counts": {
            "algorithm_failure_count": 0,
            "gate_refusal_count": 0,
            "actual_file_write_count": 0,
        },
        "actual_files_written": [],
        "memory_write_committed": False,
        "stage_summaries": [
            {"stage": "phase_parser", "status": "OK", "phase_primary": "Φ6", "phase_path_hypothesis": ["Φ4", "Φ6"], "confidence": 0.84},
            {"stage": "memory_recaller", "status": "OK", "active_memory_count": 2, "candidate_nodes_collected": 2},
            {"stage": "trace_spine", "status": "OK", "I_t_present": True, "M_t_present": True},
            {"stage": "candidate_generator", "status": "OK", "C_t_present": True, "candidate_count": 3},
            {"stage": "evolutionary_drift_explorer", "status": "OK", "E_t_present": True, "bounded_branch_count": 1},
            {"stage": "coherence_scorer", "status": "OK", "S_t_present": True, "selected_candidate_present": True, "manifest_allowed": True},
            {"stage": "correction_naming", "status": "OK", "chi_t_present": True, "N_t_present": True, "stable_naming": True},
            {"stage": "manifest_compiler", "status": "OK", "manifest_compilation_allowed": True, "manifest_packet_present": True, "manifest_readiness_score": 0.91},
            {"stage": "output_renderer", "status": "OK", "rendering_allowed": True, "R_t_present": True},
            {"stage": "echo_validator", "status": "OK", "V_t_present": True, "echo_validation_passed": True, "echo_score": 0.88},
            {"stage": "memory_writer_dry_run", "status": "OK", "W_t_present": True, "memory_write_plan_allowed": True, "write_eligibility_score": 0.83, "actual_files_written": []},
            {"stage": "gated_memory_writer", "status": "NOT_ATTEMPTED", "attempted": False, "memory_write_committed": False, "actual_files_written": []},
        ],
        "source_stage_reports": {
            "manifest_compiler": {"manifest_packet": {"μ_t": {
                "claim": "Active loop state should be reconstructed before persistence.",
                "phase_path": ["Φ4", "Φ6", "Φ7"],
                "operator_path": ["memory_fold", "correction", "naming"],
                "memory_links": [{"memory_id": "mem_test", "confidence": 0.9}],
                "confidence": 0.88,
                "novelty": 0.22,
                "drift_status": {"epsilon_s": 0.18},
                "output_targets": ["text"],
                "projection_status": "not_projected_until_echo_validation",
            }}},
            "output_renderer": {"render_packet": {"R_t": {
                "rendered_text": "Active loop state should be reconstructed before persistence.",
                "render_mode": "text",
            }}},
            "echo_validator": {"V_t": {
                "echo_score": 0.88,
                "echo_validation_passed": True,
                "recommended_route": "memory_writer_dry_run",
            }},
            "evolutionary_drift_explorer": {
                "archive_candidates": [{"candidate_id": "arch_1", "novelty_delta": 0.74, "epsilon_s": 0.44, "archive_reason": "promising_but_over_budget"}],
                "bounded_branches": [{"candidate_id": "bounded_1", "novelty_delta": 0.22, "epsilon_s": 0.18, "status": "bounded"}],
            },
        },
    }


def weak_pipeline() -> dict:
    p = strong_pipeline()
    p["status"] = "BLOCKED"
    p["pipeline_verdict"] = "lawful_gate_refusal"
    p["first_blocker"] = {"stage": "echo_validator", "kind": "gate_refusal", "reason_codes": ["echo_not_validated"], "failure_code": None}
    p["gate_counts"] = {"algorithm_failure_count": 0, "gate_refusal_count": 2, "actual_file_write_count": 0}
    for s in p["stage_summaries"]:
        if s["stage"] == "echo_validator":
            s.update({"status": "BLOCKED", "echo_validation_passed": False, "gate_refusal": True, "reason_codes": ["echo_not_validated"]})
        if s["stage"] == "memory_writer_dry_run":
            s.update({"status": "BLOCKED", "memory_write_plan_allowed": False, "gate_refusal": True, "reason_codes": ["upstream_echo_failed"]})
    p["source_stage_reports"]["echo_validator"] = {"V_t": {"echo_score": 0.41, "echo_validation_passed": False, "recommended_route": "repair_render"}}
    return p


def algorithm_failure_pipeline() -> dict:
    p = strong_pipeline()
    p["status"] = "ERROR"
    p["pipeline_verdict"] = "algorithm_failure_detected"
    p["first_blocker"] = {"stage": "manifest_compiler", "kind": "algorithm_failure", "reason_codes": ["exception"], "failure_code": "TRACEBACK"}
    p["gate_counts"] = {"algorithm_failure_count": 1, "gate_refusal_count": 0, "actual_file_write_count": 0}
    for s in p["stage_summaries"]:
        if s["stage"] == "manifest_compiler":
            s.update({"status": "ERROR", "algorithm_failure": True, "failure_code": "TRACEBACK"})
    return p


def main() -> None:
    root = make_memory_root()
    boundary = active_loop_boundary()
    check("boundary_read_only", boundary["read_only"] is True and boundary["writes_files"] is False)
    check("boundary_no_llm_chroma_shell", not boundary["uses_llm"] and not boundary["queries_chroma"] and not boundary["executes_shell"])

    contract = active_loop_schema_contract()
    check("schema_has_required_L_t_fields", "current_loop_id" in contract["required_fields"] and "next_expected_step" in contract["required_fields"])

    before_files = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
    strong = build_active_loop_state(strong_pipeline(), forge_root=root)
    after_files = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
    check("strong_status_ok", strong["status"] == "OK")
    check("L_t_present", isinstance(strong.get("L_t"), dict))
    L = strong["L_t"]
    check("current_loop_id_present", str(L["current_loop_id"]).startswith("rmcloop_"))
    check("current_phase_present", L["current_phase"] == "Φ6")
    check("completed_stages_collected", len(L["completed_stages"]) >= 10)
    check("next_step_no_mutation", L["next_expected_step"]["may_mutate"] is False)
    check("last_valid_manifest_present", L["last_valid_manifest"] is not None)
    check("last_valid_render_present", L["last_valid_render"] is not None)
    check("last_valid_echo_present", L["last_valid_echo"] is not None)
    check("memory_surface_counts", L["memory_surface"]["raw_event_count"] == 1 and L["memory_surface"]["receipt_count"] == 1)
    check("review_queue_visible", L["memory_surface"]["review_queue_count"] == 1)
    check("continuity_strength_measured", L["user_session_continuity"]["continuity_strength"] > 0.6)
    check("read_only_no_file_change", before_files == after_files)

    weak = build_active_loop_state(weak_pipeline(), forge_root=root)
    check("weak_blocked_but_not_algorithm_failure", weak["status"] == "OK")
    check("weak_open_issue_present", weak["L_t"]["open_issues"][0]["stage"] == "echo_validator")
    check("weak_next_step_routes_to_repair", weak["L_t"]["next_expected_step"]["action"] == "repair_render_until_echo_preserves_manifest")
    check("weak_unresolved_branch_present", len(weak["L_t"]["unresolved_branches"]) >= 1)

    failed = build_active_loop_state(algorithm_failure_pipeline(), forge_root=root)
    check("algorithm_failure_blocks_state", failed["status"] == "BLOCKED")
    check("algorithm_failure_issue_critical", failed["L_t"]["open_issues"][0]["severity"] == "critical")

    empty = build_active_loop_state({}, forge_root=root)
    check("empty_report_returns_contract", isinstance(empty.get("L_t"), dict) and not empty.get("missing_required_fields"))
    check("empty_report_no_write", empty["writes_files"] is False and empty["memory_write_allowed"] is False)

    print("RESULT: active_loop_state_C11_behavior_tests_pass=True")


if __name__ == "__main__":
    main()
