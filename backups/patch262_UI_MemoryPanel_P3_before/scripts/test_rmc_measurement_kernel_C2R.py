#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C2R measurement kernel."""
from __future__ import annotations

import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.measurement_kernel import (
    coherence_components,
    measure_candidate,
    normalized_shannon_entropy,
    phase_path_metrics,
    semantic_distance,
    structure_delta,
    structure_signature,
    symbolic_epsilon,
    tokens,
)


def _check(name: str, condition: bool):
    if not condition:
        raise AssertionError(name)
    print(f"[PASS] {name}")


def _trace():
    return {
        "resonance_summary": {"phase_vector": {"Φ1": 0.06, "Φ5": 0.27, "Φ6": 0.195, "Φ7": 0.06, "Φ8": 0.225}},
        "phase_report": {"phase_state": {"phase_primary": "Φ6", "phase_path_hypothesis": ["Φ5", "Φ6", "Φ7", "Φ8"], "confidence": 0.854}},
        "memory_recall": {
            "memory_state": {
                "active_memory_nodes": [
                    {
                        "memory_id": "mem_correction",
                        "content_summary": "projection drift requires correction before naming and projection; phase path Φ5 Φ6 Φ7 Φ8",
                        "phase_tags": ["Φ5", "Φ6", "Φ7", "Φ8"],
                        "memory_role": "correction_doctrine",
                        "confidence": "high",
                        "retrieval_weight": 0.91,
                        "prior_drift_score": 0.12,
                        "source_path": "memory/context_library_v1/symbolic_maps/example.json",
                    },
                    {
                        "memory_id": "mem_unrelated",
                        "content_summary": "unrelated dashboard color settings",
                        "phase_tags": ["Φ1"],
                        "confidence": "medium",
                        "retrieval_weight": 0.22,
                        "prior_drift_score": 0.25,
                    },
                ]
            }
        },
    }


def main():
    toks = tokens("before correction or naming")
    _check("whole_word_token_before", "before" in toks)
    _check("or_not_inside_before", toks.count("or") == 1)
    _check("entropy_varies", normalized_shannon_entropy("drift drift drift") < normalized_shannon_entropy("drift correction naming projection"))

    sig_a = structure_signature({"a": 1, "b": {"c": []}})
    sig_b = structure_signature({"a": 1, "x": [1, 2, 3]})
    _check("structure_signature_hash", isinstance(sig_a.get("structure_hash"), str) and len(sig_a["structure_hash"]) == 16)
    _check("structure_delta_positive", structure_delta(sig_a, sig_b) > 0.0)

    near = semantic_distance("correct projection drift before naming", "projection drift requires correction before naming")
    far = semantic_distance("correct projection drift before naming", "cook dinner and wash truck")
    _check("semantic_distance_changes", near < far)

    legal = phase_path_metrics(["Φ5", "Φ6", "Φ7", "Φ8"])
    illegal = phase_path_metrics(["Φ5", "Φ8"])
    _check("phase_legal_true", legal["phase_path_legal"] is True)
    _check("phase_illegal_false", illegal["phase_path_legal"] is False)
    _check("phase_delta_changes", illegal["max_delta_phi"] >= legal["max_delta_phi"])

    eps = symbolic_epsilon(0.10, 0.20, 0.30, 3)
    _check("epsilon_formula", math.isclose(eps, 0.20, rel_tol=0, abs_tol=1e-9))

    candidate = {
        "candidate_id": "ct_test",
        "title": "Correction Candidate",
        "candidate": "Route projection drift through correction before naming and projection.",
        "candidate_kind": "correction_candidate",
        "phase_target": "Φ6",
        "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
        "allowed_to_continue_to_scoring": True,
    }
    m = measure_candidate(candidate, _trace())
    _check("measurement_reads_memory", m["reads_actual_memory_nodes"] is True)
    _check("measurement_reads_phase", m["reads_actual_phase_path"] is True)
    _check("measurement_reads_resonance", m["reads_actual_resonance_vector"] is True)
    _check("measurement_has_epsilon", 0.0 <= m["epsilon_s"] <= 1.0)
    _check("measurement_has_memory_fit", m["memory_fit"] > 0.0)
    _check("measurement_bounded_key", "bounded_evolutionary_drift" in m)
    comp = coherence_components(candidate, m)
    _check("coherence_formula_present", "formula" in comp)
    _check("coherence_score_range", 0.0 <= comp["coherence_score"] <= 1.0)

    bad = dict(candidate)
    bad["candidate_id"] = "ct_bad"
    bad["phase_path"] = ["Φ5", "Φ8"]
    mbad = measure_candidate(bad, _trace())
    _check("illegal_phase_triggers_circuit", mbad["circuit_breaker"] is True)
    _check("illegal_phase_requires_chi", mbad["chi_t_required"] is True)

    print("RESULT: measurement_kernel_C2R_behavior_tests_pass=True")


if __name__ == "__main__":
    main()
