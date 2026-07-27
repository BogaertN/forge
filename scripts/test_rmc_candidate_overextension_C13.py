#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C13 Candidate Overextension Check."""
from __future__ import annotations

import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.candidate_generator import generate_candidates, candidate_generator_boundary
from rmc_engine_v1.evolutionary_drift_explorer import explore_evolutionary_drift, score_coherence
from rmc_engine_v1.memory_recaller import build_trace_spine


def _trace(*, similar_memory: bool) -> dict:
    if similar_memory:
        memory_contents = [
            "Preserve the active input event, phase path, drift report, and memory links as the next candidate meaning state. Direct Trace-Preserving Candidate Provides the conservative candidate nearest to the current trace without claiming final language. direct_trace_candidate",
            "Route the meaning state through Φ6 correction before any naming or projection is considered. Correction-First Candidate The trace contains drift/correction pressure; lawful movement requires correction before naming and projection. correction_candidate",
            "Use the active memory set as ancestry support for the next meaning state while preserving source, phase, confidence, and drift relation. Memory-Anchored Candidate Memory is present and phase-related; the candidate keeps ancestry attached instead of relying on surface language. memory_anchored_candidate",
            "Explore one adjacent meaning branch while keeping memory ancestry, phase path, and drift budget visible. Bounded Evolutionary Drift Candidate Keeps novelty available without letting novelty bypass the trace or become approved output. bounded_evolutionary_candidate",
        ]
    else:
        memory_contents = [
            "unrelated diesel maintenance invoice weather grocery list",
            "unrelated animal shelter calendar",
        ]
    with tempfile.TemporaryDirectory() as temporary:
        trace = build_trace_spine(
            "Inspect the current build status.",
            {"source_kind": "candidate_overextension_test"},
            root=pathlib.Path(temporary) / "forge",
        )
    if trace.get("status") != "OK":
        raise AssertionError(trace)
    trace["symbolic_trace"]["M_t"]["active_memory_nodes"] = [
        {
            "memory_id": f"mem_c13_{index}",
            "content": content,
            "source_kind": "stable_memory_test",
            "phase_tags": ["Φ6"],
            "memory_role": "candidate_overextension_test_anchor",
            "confidence": "high",
            "prior_drift_score": 0.0,
            "retrieval_weight": 0.99,
        }
        for index, content in enumerate(memory_contents, start=1)
    ]
    trace["resonance_summary"] = {
        "phase_vector": {"Φ5": 0.3, "Φ6": 0.7, "Φ7": 0.5, "Φ8": 0.2}
    }
    trace["drift_report"] = {
        "drift_report_id": "drift_c13_001",
        "epsilon_s": {"epsilon_s": 0.24, "sigma_res": 0.12, "D_score": 0.2, "phase_deviation_normalized": 0.1},
        "projection_status": "blocked_until_correction_and_naming",
        "circuit_breaker": {"triggered": False},
        "drift_classes": [{"drift_key": "semantic", "score": 0.22}, {"drift_key": "evolutionary", "score": 0.18}],
    }
    return trace


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
