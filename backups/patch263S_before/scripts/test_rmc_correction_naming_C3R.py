#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C3R.

C3R proves correction/naming is using measured values, not pretty labels:
- candidate validity is separated from projection-gated score
- high semantic distance / novelty lowers naming confidence
- route and chi_t_action cannot conflict
- stable naming requires real support, not just phase words
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.correction_naming_engine import run_correction_and_naming, correction_naming_boundary


def check(name: str, ok: bool, failures: list[str]) -> None:
    if ok:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}")
        failures.append(name)


def measured(*, epsilon=0.30, d_score=0.42, semantic_distance=0.45, memory_fit=0.78, novelty=0.28, source=0.86, circuit=False, path=None):
    path = path or ["Φ5", "Φ6", "Φ7", "Φ8"]
    return {
        "measurement_kernel_version": "rmc_measurement_kernel_v1_patch262J1R_preflight_C2R",
        "epsilon_s": epsilon,
        "D_score": d_score,
        "sigma_res": 0.12,
        "semantic_distance": semantic_distance,
        "memory_fit": memory_fit,
        "novelty_delta": novelty,
        "source_confidence": source,
        "circuit_breaker": circuit,
        "chi_t_required": epsilon > 0.35 or circuit,
        "chi_t_action": "route_to_correction_engine" if epsilon > 0.35 else "monitor_without_projection",
        "phase_metrics": {
            "phase_path": path,
            "phase_indexes": [int(p.replace("Φ", "")) for p in path],
            "transition_deltas": [0.125] * max(0, len(path) - 1),
            "average_delta_phi": 0.125,
            "max_delta_phi": 0.125 if path != ["Φ5", "Φ8"] else 0.375,
            "phase_path_legal": False if path == ["Φ5", "Φ8"] else True,
            "phase_warnings": ["illegal_projection_skip"] if path == ["Φ5", "Φ8"] else [],
            "phase_validity_score": 0.30 if path == ["Φ5", "Φ8"] else 0.92,
        },
    }


def report(meas: dict, score=0.0, title="Trace Correction Naming Gate", candidate_text="Correct projection drift through trace, memory, and naming before projection."):
    selected = {
        "candidate_id": "ct_calibrated",
        "title": title,
        "candidate_kind": "naming_candidate",
        "coherence_score": score,
        "coherence_status": "projection_gated_not_manifest_ready",
        "measured_evolutionary_drift": meas,
        "score_components": {
            "operator_legality": 0.84,
            "utility_fit": 0.74,
            "conflict_penalty": 0.06,
            "projection_gate_penalty": 0.22,
            "formula": "test formula",
        },
        "allowed_to_continue_to_correction_engine": not meas.get("circuit_breaker"),
        "allowed_to_continue_to_naming_engine": False,
        "allowed_to_continue_to_manifest_compiler": False,
    }
    return {
        "status": "OK",
        "stage": "Coherence Scorer",
        "trace_id": "trace_c3r_test",
        "candidate_set_id": "ct_set_c3r_test",
        "score_set_id": "st_c3r_test",
        "candidate_scores": [selected],
        "selected_scored_candidate_preview": selected,
        "selected_candidate_meaning_state_preview": {
            "candidate_id": "ct_calibrated",
            "title": title,
            "candidate": candidate_text,
            "candidate_kind": "naming_candidate",
            "phase_path": meas.get("phase_metrics", {}).get("phase_path", []),
            "memory_links": ["Section 5.4 Drift Analyzer", "Section 5.5 Candidate Conclusion Generator"],
            "allowed_to_continue_to_scoring": not meas.get("circuit_breaker"),
        },
        "source_evolutionary_drift": {
            "source_candidate_conclusion": {
                "source_trace_spine": {
                    "input_event": {"raw_input_preview": "How do we correct projection drift before naming?"}
                }
            }
        },
    }


def main() -> int:
    failures: list[str] = []
    boundary = correction_naming_boundary()
    check("boundary_read_only", boundary.get("writes_files") is False and boundary.get("renders_final_language") is False, failures)
    check("boundary_c3r_engine", "C3R" in boundary.get("note", "") or "v2" in boundary.get("engine_version", ""), failures)

    strong = run_correction_and_naming(report(measured()))
    chi = strong.get("chi_t", {})
    nt = strong.get("N_t", {})
    check("status_ok", strong.get("status") == "OK", failures)
    check("score_separation_present", "candidate_validity_score" in chi and "projection_gated_score" in chi, failures)
    check("projection_gated_can_be_zero_without_zero_validity", float(chi.get("projection_gated_score", 1)) == 0.0 and float(chi.get("candidate_validity_score", 0)) > 0.20, failures)
    check("route_consistent", chi.get("route_consistency", {}).get("route_consistent") is True and chi.get("recommended_route") == chi.get("chi_t_action"), failures)
    check("naming_derived_from_candidate", bool(nt.get("name_derivation", {}).get("selected_terms")) and nt.get("name_derivation", {}).get("derived_from_candidate_text") is True, failures)
    check("stable_or_allowed_with_support", nt.get("naming_allowed") is True and nt.get("stable_naming") is True, failures)

    weak_meas = measured(semantic_distance=0.91, memory_fit=0.38, novelty=0.88, d_score=0.58, epsilon=0.36)
    weak = run_correction_and_naming(report(weak_meas, candidate_text="Invent a far speculative projection with weak memory support."))
    weak_chi = weak.get("chi_t", {})
    weak_nt = weak.get("N_t", {})
    strong_conf = float((nt.get("naming_confidence_report") or {}).get("naming_confidence", 0.0))
    weak_conf = float((weak_nt.get("naming_confidence_report") or {}).get("naming_confidence", 1.0))
    check("high_semantic_novelty_penalizes_naming", weak_conf < strong_conf, failures)
    check("weak_support_not_stable", weak_nt.get("stable_naming") is False, failures)
    check("weak_route_not_conflicting", weak_chi.get("route_consistency", {}).get("route_consistent") is True, failures)

    bad_path = run_correction_and_naming(report(measured(path=["Φ5", "Φ8"]), candidate_text="Project drift now without correction."))
    bad_chi = bad_path.get("chi_t", {})
    check("illegal_phase_repaired", bad_chi.get("phase_repair", {}).get("repaired_phase_path") == ["Φ5", "Φ6", "Φ7", "Φ8"], failures)

    circuit = run_correction_and_naming(report(measured(circuit=True, epsilon=0.91, d_score=0.95)))
    check("circuit_blocks_naming", circuit.get("N_t", {}).get("naming_allowed") is False, failures)
    check("circuit_route_consistent", circuit.get("chi_t", {}).get("recommended_route") == "route_to_containment_circuit_breaker" and circuit.get("chi_t", {}).get("chi_t_action") == "route_to_containment_circuit_breaker", failures)

    if failures:
        print("RESULT: correction_naming_C3R_behavior_tests_pass=False")
        return 1
    print("RESULT: correction_naming_C3R_behavior_tests_pass=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
