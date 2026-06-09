#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C5 output renderer."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.manifest_compiler import compile_manifest  # noqa: E402
from rmc_engine_v1.output_renderer import (  # noqa: E402
    render_manifest,
    renderer_boundary,
    renderer_schema_contract,
)


def _assert(name: str, condition: bool, details: str = "") -> None:
    if not condition:
        raise AssertionError(f"[FAIL] {name} {details}".rstrip())
    print(f"[PASS] {name}")


def strong_c3r(claim: str = "Compile the corrected and named trace into a pre-language manifest object before any rendering.") -> dict:
    return {
        "status": "OK",
        "trace_id": "rmctrace_test_render_strong",
        "run_id": "c3run_test_render_strong",
        "score_set_id": "st_test_render_strong",
        "candidate_set_id": "ct_set_test_render_strong",
        "selected_candidate_id": "ct_test_render_strong",
        "chi_t_present": True,
        "N_t_present": True,
        "chi_t": {
            "chi_t_id": "chi_test_render_strong",
            "status": "correction_passes_stable_for_naming_dry_run",
            "correction_allowed": True,
            "candidate_id": "ct_test_render_strong",
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
            "N_t_id": "nt_test_render_strong",
            "status": "naming_candidate_stable_internal_only",
            "naming_allowed": True,
            "stable_naming": True,
            "candidate_id": "ct_test_render_strong",
            "proposed_name": "Drift-Corrected Rendering Trace",
            "machine_name": "drift_corrected_rendering_trace",
            "definition": claim,
            "phase_role": "Φ7 naming after Φ6 correction",
            "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
            "allowed_use": ["internal_trace_label", "future_manifest_input_after_correction_and_coherence_validation"],
            "forbidden_use": ["public_projection", "memory_write_as_truth"],
            "memory_tag_preview": "rmc/name/drift_corrected_rendering_trace",
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
            "trace_id": "rmctrace_test_render_strong",
            "candidate_set_id": "ct_set_test_render_strong",
            "score_set_id": "st_test_render_strong",
            "selected_candidate_meaning_state_preview": {
                "candidate_id": "ct_test_render_strong",
                "title": "Strong Render Manifest Candidate",
                "candidate": claim,
                "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
                "memory_links": [
                    {
                        "memory_id": "m_manifest_rendering_definition",
                        "source_kind": "reference_document",
                        "source_path": "RMC Section 3.7 Rendering",
                        "memory_role": "render_schema_source",
                        "phase_tags": ["Φ7", "Φ8"],
                        "confidence": 0.96,
                        "retrieval_weight": 0.88,
                    }
                ],
            },
            "selected_scored_candidate_preview": {
                "candidate_id": "ct_test_render_strong",
                "coherence_score": 0.74,
            },
        },
    }


def weak_c3r() -> dict:
    data = strong_c3r()
    data["trace_id"] = "rmctrace_test_render_weak"
    data["chi_t"]["candidate_validity_score"] = 0.19
    data["chi_t"]["quality_calibration"]["candidate_validity_score"] = 0.19
    data["chi_t"]["measured_inputs"]["semantic_distance"] = 0.86
    data["chi_t"]["measured_inputs"]["memory_fit"] = 0.51
    data["chi_t"]["measured_inputs"]["novelty_delta"] = 0.82
    data["N_t"]["stable_naming"] = False
    data["N_t"]["naming_allowed"] = False
    data["N_t"]["naming_confidence_report"]["naming_confidence"] = 0.26
    return data


def main() -> int:
    boundary = renderer_boundary()
    schema = renderer_schema_contract()
    _assert("boundary_read_only", boundary.get("writes_files") is False and boundary.get("writes_rmc_memory") is False)
    _assert("schema_formula", schema.get("render_formula") == "R_t = ρ(μ_t, a, s)")

    manifest = compile_manifest(strong_c3r())
    _assert("source_manifest_ok", manifest.get("status") == "OK" and bool(manifest.get("manifest_packet")))
    rendered = render_manifest(manifest, audience_profile="operator", style_mode="standard", render_mode="text")
    _assert("render_status_ok", rendered.get("status") == "OK")
    _assert("R_t_present", rendered.get("R_t_present") is True and bool(rendered.get("R_t")))
    packet = rendered.get("render_packet") or {}
    _assert("source_manifest_id_preserved", packet.get("source_manifest_id") == (manifest.get("manifest_packet") or {}).get("manifest_id"))
    _assert("render_claim_preserved", "pre-language manifest" in str(rendered.get("R_t")))
    _assert("render_phase_preserved", "Φ5" in str(rendered.get("R_t")) and "Φ8" in str(rendered.get("R_t")))
    fidelity = (packet.get("render_fidelity_precheck") or {}).get("fidelity_score", 0.0)
    _assert("fidelity_measured", 0.75 <= float(fidelity) <= 1.0)
    _assert("no_approval_before_echo", rendered.get("approved_output") is False and rendered.get("echo_validation_required") is True)
    _assert("no_memory_write", rendered.get("memory_write_allowed") is False)

    json_render = render_manifest(manifest, render_mode="json_packet")
    _assert("json_packet_render", isinstance(json_render.get("R_t"), dict) and json_render["R_t"].get("packet_kind") == "rmc_rendered_json_packet_v1")
    dash_render = render_manifest(manifest, render_mode="dashboard_state")
    _assert("dashboard_render", isinstance(dash_render.get("R_t"), dict) and dash_render["R_t"].get("dashboard_card_kind") == "rmc_manifest_render_state_v1")
    glyph_render = render_manifest(manifest, render_mode="glyph_packet")
    _assert("glyph_render", isinstance(glyph_render.get("R_t"), dict) and glyph_render["R_t"].get("glyph_packet_kind") == "rmc_phase_glyph_render_packet_v1")

    weak_manifest = compile_manifest(weak_c3r())
    blocked = render_manifest(weak_manifest, render_mode="text")
    _assert("blocked_manifest_does_not_render", blocked.get("status") == "BLOCKED" and blocked.get("R_t_present") is False)
    _assert("blocked_has_diagnostics", bool(blocked.get("blocked_render_candidate")))

    changed_manifest = compile_manifest(strong_c3r("Render a different corrected manifest claim for hash-change testing."))
    changed = render_manifest(changed_manifest, render_mode="text")
    _assert("render_hash_changes_with_claim", (changed.get("render_packet") or {}).get("rendered_output_hash") != packet.get("rendered_output_hash"))

    bad_direct = {"manifest_symbol": "μ_t", "μ_t": {"claim": "missing fields"}}
    bad = render_manifest(bad_direct)
    _assert("missing_mu_fields_block", bad.get("status") == "BLOCKED" and "missing_required_fields" in str(bad.get("blocked_render_candidate")))

    print("RESULT: output_renderer_C5_behavior_tests_pass=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
