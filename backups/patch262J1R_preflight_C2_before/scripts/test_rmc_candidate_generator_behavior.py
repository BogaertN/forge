#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C Candidate Generator."""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.candidate_generator import generate_candidates, candidate_generator_boundary


def _sample_trace(circuit: bool = False):
    return {
        "status": "OK",
        "symbolic_trace": {
            "trace_id": "rmctrace_test_001",
            "I_t": {"event_id": "input_test_001", "raw_input_preview": "How do we correct projection drift before naming?"},
            "M_t": {
                "active_memory_nodes": [
                    {"memory_id": "mem1", "source_kind": "symbolic_map_entry", "phase_tags": ["Φ5", "Φ6"], "memory_role": "recursion_doctrine", "confidence": "medium_high", "retrieval_weight": 0.91},
                    {"memory_id": "mem2", "source_kind": "dataset_review_queue_item", "phase_tags": ["Φ7"], "memory_role": "dataset_candidate_example", "confidence": "review_required", "retrieval_weight": 0.62},
                ]
            },
            "Φ_t": {"phase_primary": "Φ6", "phase_secondary": ["Φ5", "Φ7", "Φ8"], "phase_path_hypothesis": ["Φ5", "Φ6", "Φ7", "Φ8"], "confidence": 0.854},
        },
        "resonance_summary": {"circuit_breaker_candidate": circuit, "projection_allowed": "conditional_after_gates"},
        "drift_report": {
            "drift_report_id": "drift_test_001",
            "epsilon_s": {"epsilon_s": 0.24, "sigma_res": 0.12, "D_score": 0.2, "phase_deviation_normalized": 0.1},
            "projection_status": "blocked_until_correction_and_naming" if not circuit else "blocked_circuit_breaker",
            "circuit_breaker": {"triggered": circuit},
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
    _check("boundary_stage", boundary["implements_rmc_stage"] == "Candidate Conclusion Generator / C_t")

    report = generate_candidates(_sample_trace(False))
    _check("status_ok", report["status"] == "OK")
    _check("candidate_set_id", str(report.get("candidate_set_id", "")).startswith("ct_set_"))
    _check("C_t_present", report["C_t_present"] is True)
    _check("generation_allowed", report["candidate_generation_status"]["candidate_generation_allowed"] is True)
    _check("candidate_count", len(report["candidate_set"]) >= 4)
    _check("no_rendering", report["boundary"]["renders_final_language"] is False)
    _check("no_memory_write", report["boundary"]["writes_rmc_memory"] is False)
    _check("has_correction_candidate", any(c["candidate_kind"] == "correction_candidate" for c in report["candidate_set"]))
    _check("has_memory_links", any(c.get("memory_links") for c in report["candidate_set"]))
    _check("candidate_not_sentence", all(c.get("meaning_state_not_sentence") is True for c in report["candidate_set"]))
    _check("projection_blocked", all(c.get("projection_allowed") is False for c in report["candidate_set"]))

    blocked = generate_candidates(_sample_trace(True))
    _check("circuit_blocks_generation", blocked["candidate_generation_status"]["candidate_generation_allowed"] is False)
    _check("circuit_returns_containment_candidate", len(blocked["candidate_set"]) == 1 and blocked["candidate_set"][0]["candidate_kind"] == "containment_correction_route")
    _check("circuit_candidate_not_scoreable", blocked["candidate_set"][0]["allowed_to_continue_to_scoring"] is False)

    print("RESULT: candidate_generator_C_behavior_tests_pass=True")


if __name__ == "__main__":
    main()
