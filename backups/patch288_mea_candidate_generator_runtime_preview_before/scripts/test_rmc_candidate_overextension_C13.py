#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C13 Candidate Overextension Check."""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.candidate_generator import generate_candidates, candidate_generator_boundary
from rmc_engine_v1.evolutionary_drift_explorer import explore_evolutionary_drift, score_coherence


def _trace(*, similar_memory: bool) -> dict:
    memory_content = (
        "Preserve the active input event phase path drift report and memory links as next candidate meaning state "
        "correction projection drift naming route through correction before projection"
        if similar_memory else
        "unrelated diesel maintenance invoice weather grocery list unrelated animal shelter calendar"
    )
    return {
        "status": "OK",
        "symbolic_trace": {
            "trace_id": "rmctrace_c13_001",
            "I_t": {
                "event_id": "input_c13_001",
                "raw_input_preview": "How do we correct projection drift before naming?",
            },
            "M_t": {
                "active_memory_nodes": [
                    {
                        "memory_id": "mem_c13_1",
                        "content": memory_content,
                        "source_kind": "stable_memory_test",
                        "phase_tags": ["Φ5", "Φ6", "Φ7", "Φ8"],
                        "memory_role": "candidate_overextension_test_anchor",
                        "confidence": "high",
                        "prior_drift_score": 0.0,
                        "retrieval_weight": 0.99,
                    },
                    {
                        "memory_id": "mem_c13_2",
                        "content": memory_content,
                        "source_kind": "stable_memory_test",
                        "phase_tags": ["Φ6", "Φ7"],
                        "memory_role": "candidate_overextension_test_anchor",
                        "confidence": "high",
                        "prior_drift_score": 0.0,
                        "retrieval_weight": 0.95,
                    },
                ]
            },
            "Φ_t": {
                "phase_primary": "Φ6",
                "phase_secondary": ["Φ5", "Φ7", "Φ8"],
                "phase_path_hypothesis": ["Φ5", "Φ6", "Φ7", "Φ8"],
                "confidence": 0.854,
            },
        },
        "resonance_summary": {"phase_vector": {"Φ5": 0.3, "Φ6": 0.7, "Φ7": 0.5, "Φ8": 0.2}},
        "drift_report": {
            "drift_report_id": "drift_c13_001",
            "epsilon_s": {"epsilon_s": 0.24, "sigma_res": 0.12, "D_score": 0.2, "phase_deviation_normalized": 0.1},
            "projection_status": "blocked_until_correction_and_naming",
            "circuit_breaker": {"triggered": False},
            "drift_classes": [{"drift_key": "semantic", "score": 0.22}, {"drift_key": "evolutionary", "score": 0.18}],
        },
    }


def _check(name: str, condition: bool):
    if not condition:
        raise AssertionError(name)
    print(f"[PASS] {name}")


def main():
    boundary = candidate_generator_boundary()
    _check("boundary_read_only", boundary["writes_files"] is False and boundary["calls_llm"] is False)
    _check("boundary_declares_overextension_gate", "overextension_gate" in boundary)

    over_report = generate_candidates(_trace(similar_memory=False))
    over_candidates = over_report["candidate_set"]
    _check("status_ok", over_report["status"] == "OK")
    _check("all_candidates_have_overextension_check", over_report["candidate_measurement_summary"]["all_candidates_have_overextension_check"] is True)
    _check("overextended_candidates_detected", over_report["candidate_measurement_summary"]["overextended_candidate_count"] >= 1)
    _check("overextended_has_N_c_N_max", all("N_c" in c and "N_max" in c for c in over_candidates))
    _check("overextended_reason_code", any("novelty_delta_exceeds_N_max" in (c.get("overextension_check") or {}).get("reason_codes", []) for c in over_candidates))
    _check("overextended_route_present", any(c.get("recommended_route") == "overextended_candidate_route_to_evolutionary_review_or_archive" for c in over_candidates))
    _check("overextended_not_renderable", all(c.get("projection_allowed") is False and c.get("memory_write_allowed") is False for c in over_candidates))

    evo = explore_evolutionary_drift(over_report)
    _check("explorer_sees_overextended_marker", any(((b.get("boundedness") or {}).get("candidate_overextended") is True) for b in evo.get("evolutionary_branches", [])))
    _check("explorer_routes_overextended", any(((b.get("boundedness") or {}).get("recommended_route") == "candidate_marked_overextended_route_to_review_or_archive") for b in evo.get("evolutionary_branches", [])))

    score = score_coherence(evo)
    _check("scorer_marks_overextended_unscoreable", any(s.get("candidate_overextended") is True and s.get("coherence_status") == "not_scoreable_due_to_overextended_novelty" for s in score.get("candidate_scores", [])))
    _check("overextended_score_zero", any(s.get("candidate_overextended") is True and s.get("coherence_score") == 0.0 for s in score.get("candidate_scores", [])))

    supported_report = generate_candidates(_trace(similar_memory=True))
    _check("supported_report_has_non_overextended_candidate", any(c.get("overextended") is False for c in supported_report.get("candidate_set", [])))
    _check("non_overextended_has_normal_route", any(c.get("overextended") is False and c.get("recommended_route") == "normal_candidate_to_evolutionary_drift_explorer" for c in supported_report.get("candidate_set", [])))

    print("RESULT: candidate_overextension_C13_behavior_tests_pass=True")


if __name__ == "__main__":
    main()
