#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C9."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.rmc_pipeline import build_pipeline_summary, pipeline_boundary


def check(name: str, condition: bool, failures: list[str]) -> None:
    if condition:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}")
        failures.append(name)


def strong_reports() -> dict:
    return {
        "phase_parser": {"status": "OK", "phase_state": {"phase_primary": "Φ6", "phase_path_hypothesis": ["Φ5", "Φ6", "Φ7", "Φ8"], "confidence": 0.91}},
        "memory_recaller": {"status": "OK", "active_memory_count": 4, "candidate_nodes_collected": 12, "retrieval_dimensions": ["semantic_relevance", "phase_relevance"]},
        "trace_spine": {"status": "OK", "I_t": {"id": "i"}, "M_t": {"id": "m"}, "rendering_allowed": False, "memory_write_allowed": False},
        "candidate_generator": {"status": "OK", "C_t": {"candidate_set": [1, 2]}, "candidate_generation_allowed": True, "renders_final_language": False, "memory_write_allowed": False},
        "evolutionary_drift_explorer": {"status": "OK", "E_t_present": True, "bounded_branch_count": 1, "measured_evolutionary_drift": {"epsilon_s": 0.2}},
        "coherence_scorer": {"status": "OK", "S_t_present": True, "candidate_scores": [1], "selected_scored_candidate_preview": {"id": "c"}, "manifest_allowed": False, "projection_allowed": False},
        "correction_naming": {"status": "OK", "chi_t_present": True, "N_t_present": True, "N_t": {"stable_naming": True, "naming_allowed": True, "naming_confidence_report": {"naming_confidence": 0.88}}, "chi_t": {"candidate_validity_score": 0.82, "projection_gated_score": 0.0, "recommended_route": "route_to_manifest_compiler"}},
        "manifest_compiler": {"status": "OK", "manifest_compilation_allowed": True, "manifest_packet": {"μ_t": {"claim": "x"}}, "renders_final_language": False, "memory_write_allowed": False, "manifest_preflight": {"manifest_readiness_score": 0.83}},
        "output_renderer": {"status": "OK", "rendering_allowed": True, "R_t_present": True, "render_packet": {"R_t": {"text": "x"}}, "approved_output": False, "projection_allowed": False, "memory_write_allowed": False},
        "echo_validator": {"status": "OK", "V_t_present": True, "echo_validation_passed": True, "echo_score": 0.91, "approved_output": False, "memory_write_allowed": False},
        "memory_writer_dry_run": {"status": "OK", "W_t_present": True, "memory_write_plan_allowed": True, "write_plan": {"write_eligibility": {"write_eligibility_score": 0.82}}, "actual_files_written": [], "memory_write_allowed": False},
        "gated_memory_writer": {"status": "NOT_ATTEMPTED", "memory_write_committed": False, "actual_files_written": [], "memory_write_allowed": False},
    }


def weak_reports() -> dict:
    reports = strong_reports()
    reports["correction_naming"] = {"status": "OK", "chi_t_present": True, "N_t_present": True, "N_t": {"stable_naming": False, "naming_allowed": False, "naming_confidence_report": {"naming_confidence": 0.26}}, "chi_t": {"candidate_validity_score": 0.19, "projection_gated_score": 0.0}}
    reports["manifest_compiler"] = {"status": "BLOCKED", "manifest_compilation_allowed": False, "manifest_packet": None, "blocked_manifest_candidate": {"reason_codes": ["naming_not_stable"]}, "manifest_preflight": {"manifest_readiness_score": 0.10}, "gate_classification": {"algorithm_failure": False, "gate_refusal": True, "read_only_refusal": False, "explanation": "blocked"}}
    reports["output_renderer"] = {"status": "BLOCKED", "rendering_allowed": False, "R_t_present": False, "blocked_render_candidate": {"reason_codes": ["manifest_packet_missing"]}}
    reports["echo_validator"] = {"status": "BLOCKED", "V_t_present": False, "echo_validation_passed": False, "blocked_echo_candidate": {"reason_codes": ["render_missing"]}}
    reports["memory_writer_dry_run"] = {"status": "BLOCKED", "W_t_present": False, "memory_write_plan_allowed": False, "blocked_write_candidate": {"reason_codes": ["echo_validation_failed"]}, "actual_files_written": []}
    return reports


def main() -> int:
    failures: list[str] = []
    boundary = pipeline_boundary()
    check("boundary_no_write_default", boundary["writes_files"] is False and boundary["writes_rmc_memory"] is False, failures)
    strong = build_pipeline_summary(strong_reports())
    check("strong_status_ok", strong["status"] == "OK", failures)
    check("strong_no_algorithm_failures", strong["gate_counts"]["algorithm_failure_count"] == 0, failures)
    check("strong_no_first_blocker", strong["first_blocker"] is None, failures)
    check("strong_no_files_written", strong["actual_files_written"] == [], failures)
    check("strong_stage_count", strong["gate_counts"]["stages_reported"] == 12, failures)
    weak = build_pipeline_summary(weak_reports())
    check("weak_status_blocked", weak["status"] == "BLOCKED", failures)
    check("weak_lawful_gate_refusal", weak["pipeline_verdict"] == "lawful_gate_refusal", failures)
    check("weak_first_blocker_correction_or_manifest", weak["first_blocker"]["stage"] in ("correction_naming", "manifest_compiler"), failures)
    check("weak_not_algorithm_failure", weak["gate_counts"]["algorithm_failure_count"] == 0, failures)
    check("weak_no_files_written", weak["actual_files_written"] == [], failures)
    included = build_pipeline_summary(strong_reports(), include_full_reports=True)
    check("include_full_reports_flag", included["source_reports_included"] is True and "source_stage_reports" in included, failures)
    if failures:
        print("RESULT: pipeline_summary_C9_behavior_tests_pass=False")
        return 1
    print("RESULT: pipeline_summary_C9_behavior_tests_pass=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
