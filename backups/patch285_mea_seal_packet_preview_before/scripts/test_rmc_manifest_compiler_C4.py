#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C4 manifest compiler."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.manifest_compiler import (  # noqa: E402
    compile_manifest,
    manifest_compiler_boundary,
    manifest_schema_contract,
)


def _assert(name: str, condition: bool, details: str = "") -> None:
    if not condition:
        raise AssertionError(f"[FAIL] {name} {details}".rstrip())
    print(f"[PASS] {name}")


def strong_c3r() -> dict:
    return {
        "status": "OK",
        "trace_id": "rmctrace_test_strong",
        "run_id": "c3run_test_strong",
        "score_set_id": "st_test_strong",
        "candidate_set_id": "ct_set_test_strong",
        "selected_candidate_id": "ct_test_strong",
        "chi_t_present": True,
        "N_t_present": True,
        "chi_t": {
            "chi_t_id": "chi_test_strong",
            "status": "correction_passes_stable_for_naming_dry_run",
            "correction_allowed": True,
            "candidate_id": "ct_test_strong",
            "candidate_validity_score": 0.78,
            "projection_gated_score": 0.0,
            "measured_inputs": {
                "epsilon_s": 0.22,
                "D_score": 0.34,
                "sigma_res": 0.09,
                "semantic_distance": 0.31,
                "memory_fit": 0.78,
                "novelty_delta": 0.24,
                "source_confidence": 0.91,
            },
            "quality_calibration": {
                "candidate_validity_score": 0.78,
                "projection_gated_score": 0.0,
                "novelty_budget": 0.55,
                "support_pressure": 0.18,
                "components": {
                    "memory_fit": 0.78,
                    "semantic_distance": 0.31,
                    "novelty_delta": 0.24,
                    "source_confidence": 0.91,
                    "epsilon_s": 0.22,
                    "D_score": 0.34,
                    "phase_validity": 0.92,
                },
            },
            "phase_repair": {
                "repaired_phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
                "repaired_phase_metrics": {
                    "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
                    "phase_indexes": [5, 6, 7, 8],
                    "transition_deltas": [0.125, 0.125, 0.125],
                    "average_delta_phi": 0.125,
                    "max_delta_phi": 0.125,
                    "phase_path_legal": True,
                    "phase_warnings": [],
                    "phase_validity_score": 0.92,
                },
            },
            "correction_math": {
                "post_correction_estimate": {
                    "sigma_res": 0.09,
                    "D_score": 0.24,
                    "delta_phi": 0.125,
                    "epsilon_s": 0.151667,
                    "formula": "post_epsilon_s = (sigma_res + corrected_D_score + corrected_delta_phi) / 3",
                }
            },
            "route_consistency": {
                "recommended_route": "route_to_naming_engine",
                "chi_t_action": "route_to_naming_engine",
                "route_consistent": True,
            },
        },
        "N_t": {
            "N_t_id": "nt_test_strong",
            "status": "naming_candidate_stable_internal_only",
            "naming_allowed": True,
            "stable_naming": True,
            "candidate_id": "ct_test_strong",
            "proposed_name": "Drift-Corrected Naming Trace",
            "machine_name": "drift_corrected_naming_trace",
            "definition": "Compile the corrected and named trace into a pre-language manifest object before any rendering.",
            "phase_role": "Φ7 naming after Φ6 correction",
            "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
            "allowed_use": ["internal_trace_label", "future_manifest_input_after_correction_and_coherence_validation"],
            "forbidden_use": ["final_language_rendering", "public_projection", "memory_write_as_truth"],
            "memory_tag_preview": "rmc/name/drift_corrected_naming_trace",
            "naming_confidence_report": {
                "naming_confidence": 0.79,
                "components": {
                    "candidate_validity_score": 0.78,
                    "post_stability": 0.848333,
                    "memory_fit": 0.78,
                    "semantic_distance": 0.31,
                    "novelty_delta": 0.24,
                    "source_confidence": 0.91,
                    "phase_validity": 0.92,
                },
            },
        },
        "source_coherence_scorer": {
            "trace_id": "rmctrace_test_strong",
            "candidate_set_id": "ct_set_test_strong",
            "score_set_id": "st_test_strong",
            "selected_candidate_meaning_state_preview": {
                "candidate_id": "ct_test_strong",
                "title": "Strong Manifest Candidate",
                "candidate": "Compile the corrected and named trace into a pre-language manifest object before any rendering.",
                "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
                "memory_links": [
                    {
                        "memory_id": "m_manifest_definition",
                        "source_kind": "reference_document",
                        "source_path": "RMC Section 3.6 Manifest",
                        "memory_role": "manifest_schema_source",
                        "phase_tags": ["Φ7", "Φ8"],
                        "confidence": 0.96,
                        "retrieval_weight": 0.88,
                    }
                ],
            },
            "selected_scored_candidate_preview": {
                "candidate_id": "ct_test_strong",
                "coherence_score": 0.74,
            },
        },
    }


def weak_c3r() -> dict:
    data = strong_c3r()
    data["trace_id"] = "rmctrace_test_weak"
    data["chi_t"]["candidate_validity_score"] = 0.19
    data["chi_t"]["measured_inputs"]["semantic_distance"] = 0.86
    data["chi_t"]["measured_inputs"]["memory_fit"] = 0.51
    data["chi_t"]["measured_inputs"]["novelty_delta"] = 0.82
    data["chi_t"]["quality_calibration"]["candidate_validity_score"] = 0.19
    data["chi_t"]["quality_calibration"]["support_pressure"] = 0.71
    data["chi_t"]["quality_calibration"]["components"]["semantic_distance"] = 0.86
    data["chi_t"]["quality_calibration"]["components"]["memory_fit"] = 0.51
    data["chi_t"]["quality_calibration"]["components"]["novelty_delta"] = 0.82
    data["N_t"]["stable_naming"] = False
    data["N_t"]["naming_allowed"] = False
    data["N_t"]["naming_confidence_report"]["naming_confidence"] = 0.26
    return data


def illegal_phase_c3r() -> dict:
    data = strong_c3r()
    data["trace_id"] = "rmctrace_test_illegal_phase"
    data["chi_t"]["phase_repair"]["repaired_phase_path"] = ["Φ5", "Φ8"]
    data["chi_t"]["phase_repair"]["repaired_phase_metrics"]["phase_path"] = ["Φ5", "Φ8"]
    data["chi_t"]["phase_repair"]["repaired_phase_metrics"]["phase_indexes"] = [5, 8]
    data["chi_t"]["phase_repair"]["repaired_phase_metrics"]["phase_path_legal"] = False
    data["chi_t"]["phase_repair"]["repaired_phase_metrics"]["phase_warnings"] = ["illegal_skip_phi5_to_phi8"]
    data["N_t"]["phase_path"] = ["Φ5", "Φ8"]
    data["N_t"]["stable_naming"] = True
    data["N_t"]["naming_allowed"] = True
    return data


def main() -> int:
    boundary = manifest_compiler_boundary()
    schema = manifest_schema_contract()
    _assert("boundary_read_only", boundary.get("writes_files") is False and boundary.get("renders_final_language") is False)
    _assert("schema_required_fields", set(schema.get("required_fields", [])) == {"claim", "phase_path", "operator_path", "memory_links", "confidence", "novelty", "drift_status", "projection_status", "output_targets"})

    strong = compile_manifest(strong_c3r())
    _assert("strong_status_ok", strong.get("status") == "OK")
    _assert("strong_mu_present", strong.get("μ_t_present") is True)
    packet = strong.get("manifest_packet") or {}
    mu = packet.get("μ_t") or {}
    _assert("manifest_has_required_fields", set(schema["required_fields"]).issubset(mu.keys()))
    _assert("manifest_projection_status_required", isinstance(mu.get("projection_status"), dict) and "projection_allowed_now" in mu.get("projection_status", {}))
    _assert("manifest_claim_from_candidate", "pre-language manifest" in str(mu.get("claim")))
    _assert("manifest_phase_order", mu.get("phase_path") == ["Φ5", "Φ6", "Φ7", "Φ8"])
    _assert("manifest_operator_path", any(op.get("op") == "μ_t" and op.get("status") == "compiled" for op in mu.get("operator_path", [])))
    _assert("manifest_memory_links", len(mu.get("memory_links", [])) >= 1)
    _assert("manifest_no_rendering", packet.get("renders_final_language") is False and strong.get("memory_write_allowed") is False)
    _assert("readiness_score_real", 0.62 <= float((strong.get("manifest_preflight") or {}).get("readiness", {}).get("manifest_readiness_score", 0.0)) <= 1.0)

    weak = compile_manifest(weak_c3r())
    _assert("weak_blocked", weak.get("status") == "BLOCKED" and weak.get("manifest_compilation_allowed") is False)
    reasons = (weak.get("manifest_preflight") or {}).get("blocked_reasons", [])
    _assert("weak_reasons", "stable_naming" in reasons and "candidate_validity_strong" in reasons)
    _assert("weak_has_blocked_candidate", bool(weak.get("blocked_manifest_candidate")))

    illegal = compile_manifest(illegal_phase_c3r())
    illegal_reasons = (illegal.get("manifest_preflight") or {}).get("blocked_reasons", [])
    _assert("illegal_phase_blocked", illegal.get("status") == "BLOCKED")
    _assert("illegal_phase_reason", "phase_path_legal" in illegal_reasons or "phase6_and_7_before_projection_if_projection_requested" in illegal_reasons)

    empty = compile_manifest({})
    _assert("empty_blocked", empty.get("status") == "BLOCKED")
    _assert("empty_no_mu", empty.get("μ_t_present") is False)

    print("RESULT: manifest_compiler_C4_behavior_tests_pass=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
