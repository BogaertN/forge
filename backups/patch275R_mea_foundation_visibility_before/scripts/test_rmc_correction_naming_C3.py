#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C3 Correction + Naming Engine."""
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


def measured(epsilon=0.52, d_score=0.62, semantic_distance=0.72, memory_fit=0.64, circuit=False, path=None):
    path = path or ["Φ5", "Φ8"]
    return {
        "measurement_kernel_version": "rmc_measurement_kernel_v1_patch262J1R_preflight_C2R",
        "epsilon_s": epsilon,
        "D_score": d_score,
        "sigma_res": 0.16,
        "semantic_distance": semantic_distance,
        "memory_fit": memory_fit,
        "novelty_delta": 0.44,
        "source_confidence": 0.77,
        "circuit_breaker": circuit,
        "chi_t_required": epsilon > 0.35 or circuit,
        "chi_t_action": "route_to_correction_engine",
        "phase_metrics": {
            "phase_path": path,
            "phase_path_legal": False if path == ["Φ5", "Φ8"] else True,
            "max_delta_phi": 0.375,
            "phase_validity_score": 0.32 if path == ["Φ5", "Φ8"] else 0.92,
        },
    }


def report(circuit=False):
    m = measured(circuit=circuit)
    return {
        "status": "OK",
        "stage": "Coherence Scorer",
        "trace_id": "trace_test",
        "candidate_set_id": "ct_set_test",
        "score_set_id": "st_test",
        "candidate_scores": [
            {
                "candidate_id": "ct_bad_phase",
                "title": "Projection Drift Repair Candidate",
                "candidate_kind": "correction_candidate",
                "coherence_score": 0.61 if not circuit else 0.0,
                "coherence_status": "coherence_candidate_requires_correction_or_more_memory",
                "measured_evolutionary_drift": m,
                "score_components": {
                    "operator_legality": 0.82,
                    "conflict_penalty": 0.10,
                    "projection_gate_penalty": 0.35,
                    "formula": "test formula",
                },
                "allowed_to_continue_to_correction_engine": not circuit,
                "allowed_to_continue_to_naming_engine": False,
                "allowed_to_continue_to_manifest_compiler": False,
            }
        ],
        "selected_scored_candidate_preview": {
            "candidate_id": "ct_bad_phase",
            "title": "Projection Drift Repair Candidate",
            "candidate_kind": "correction_candidate",
            "coherence_score": 0.61 if not circuit else 0.0,
            "coherence_status": "coherence_candidate_requires_correction_or_more_memory",
            "measured_evolutionary_drift": m,
            "score_components": {
                "operator_legality": 0.82,
                "conflict_penalty": 0.10,
                "projection_gate_penalty": 0.35,
                "formula": "test formula",
            },
            "allowed_to_continue_to_correction_engine": not circuit,
        },
        "selected_candidate_meaning_state_preview": {
            "candidate_id": "ct_bad_phase",
            "title": "Projection Drift Repair Candidate",
            "candidate": "Correct projection drift before naming or projection.",
            "candidate_kind": "correction_candidate",
            "phase_path": ["Φ5", "Φ8"],
            "allowed_to_continue_to_scoring": not circuit,
        },
    }


def main() -> int:
    failures: list[str] = []
    b = correction_naming_boundary()
    check("boundary_read_only", b.get("writes_files") is False and b.get("renders_final_language") is False, failures)
    check("boundary_uses_measurement_kernel", b.get("uses_measurement_kernel") is True, failures)
    result = run_correction_and_naming(report(False))
    check("status_ok", result.get("status") == "OK", failures)
    check("chi_present", result.get("chi_t_present") is True and isinstance(result.get("chi_t"), dict), failures)
    check("N_present", result.get("N_t_present") is True and isinstance(result.get("N_t"), dict), failures)
    chi = result.get("chi_t") or {}
    nt = result.get("N_t") or {}
    check("phase_repair_inserts_correction_naming", chi.get("phase_repair", {}).get("repaired_phase_path") == ["Φ5", "Φ6", "Φ7", "Φ8"], failures)
    check("post_epsilon_formula_present", "formula" in (chi.get("correction_math", {}).get("post_correction_estimate") or {}), failures)
    pre_eps = (chi.get("correction_math", {}).get("pre_correction") or {}).get("epsilon_s", 0)
    post_eps = (chi.get("correction_math", {}).get("post_correction_estimate") or {}).get("epsilon_s", 1)
    check("correction_reduces_or_bounds_epsilon", float(post_eps) <= float(pre_eps), failures)
    check("naming_not_projection", nt.get("projection_allowed_after_naming") is False and result.get("projection_allowed") is False, failures)
    check("naming_has_identity_fields", bool(nt.get("proposed_name")) and bool(nt.get("memory_tag_preview")) and bool(nt.get("forbidden_use")), failures)
    check("no_manifest_allowed", result.get("manifest_allowed") is False and nt.get("manifest_allowed_after_naming") is False, failures)
    blocked = run_correction_and_naming(report(True))
    check("circuit_blocks_projection", blocked.get("chi_t", {}).get("status") == "blocked_by_circuit_breaker_route_to_containment", failures)
    check("circuit_blocks_naming", blocked.get("N_t", {}).get("naming_allowed") is False, failures)
    if failures:
        print("RESULT: correction_naming_C3_behavior_tests_pass=False")
        return 1
    print("RESULT: correction_naming_C3_behavior_tests_pass=True")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
