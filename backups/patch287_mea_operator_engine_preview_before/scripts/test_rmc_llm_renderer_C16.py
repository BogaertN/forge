#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C16 optional LLM renderer."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.echo_validator import validate_echo  # noqa: E402
from rmc_engine_v1.llm_renderer import (  # noqa: E402
    llm_renderer_boundary,
    llm_renderer_schema_contract,
    normalize_llm_toggle,
    validate_model_endpoint,
)
from rmc_engine_v1.manifest_compiler import compile_manifest  # noqa: E402
from rmc_engine_v1.output_renderer import render_manifest, renderer_boundary, renderer_schema_contract  # noqa: E402


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"[FAIL] {name} {detail}".rstrip())
    print(f"[PASS] {name}")


def strong_c3r(claim: str = "Render the corrected trace from the manifest while preserving echo validation and blocking unsupported projection.") -> dict:
    return {
        "status": "OK",
        "trace_id": "rmctrace_test_llm_renderer_strong",
        "run_id": "c3run_test_llm_renderer_strong",
        "score_set_id": "st_test_llm_renderer_strong",
        "candidate_set_id": "ct_set_test_llm_renderer_strong",
        "selected_candidate_id": "ct_test_llm_renderer_strong",
        "chi_t_present": True,
        "N_t_present": True,
        "chi_t": {
            "chi_t_id": "chi_test_llm_renderer_strong",
            "status": "correction_passes_stable_for_naming_dry_run",
            "correction_allowed": True,
            "candidate_id": "ct_test_llm_renderer_strong",
            "candidate_validity_score": 0.82,
            "projection_gated_score": 0.0,
            "measured_inputs": {
                "epsilon_s": 0.19,
                "D_score": 0.28,
                "sigma_res": 0.08,
                "semantic_distance": 0.27,
                "memory_fit": 0.84,
                "novelty_delta": 0.21,
                "source_confidence": 0.93,
            },
            "quality_calibration": {
                "candidate_validity_score": 0.82,
                "projection_gated_score": 0.0,
                "novelty_budget": 0.55,
                "support_pressure": 0.12,
                "components": {
                    "memory_fit": 0.84,
                    "semantic_distance": 0.27,
                    "novelty_delta": 0.21,
                    "source_confidence": 0.93,
                    "epsilon_s": 0.19,
                    "D_score": 0.28,
                    "phase_validity": 0.94,
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
                    "phase_validity_score": 0.94,
                },
            },
            "correction_math": {
                "post_correction_estimate": {
                    "sigma_res": 0.08,
                    "D_score": 0.18,
                    "delta_phi": 0.125,
                    "epsilon_s": 0.128333,
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
            "N_t_id": "nt_test_llm_renderer_strong",
            "status": "naming_candidate_stable_internal_only",
            "naming_allowed": True,
            "stable_naming": True,
            "candidate_id": "ct_test_llm_renderer_strong",
            "proposed_name": "Optional LLM Renderer Boundary Trace",
            "machine_name": "optional_llm_renderer_boundary_trace",
            "definition": claim,
            "phase_role": "Φ7 naming after Φ6 correction",
            "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
            "allowed_use": ["internal_trace_label", "future_manifest_input_after_correction_and_coherence_validation"],
            "forbidden_use": ["public_projection", "memory_write_as_truth"],
            "memory_tag_preview": "rmc/name/optional_llm_renderer_boundary_trace",
            "naming_confidence_report": {
                "naming_confidence": 0.83,
                "components": {
                    "candidate_validity_score": 0.82,
                    "post_stability": 0.871667,
                    "memory_fit": 0.84,
                    "semantic_distance": 0.27,
                    "novelty_delta": 0.21,
                    "source_confidence": 0.93,
                    "phase_validity": 0.94,
                },
            },
        },
        "source_coherence_scorer": {
            "trace_id": "rmctrace_test_llm_renderer_strong",
            "candidate_set_id": "ct_set_test_llm_renderer_strong",
            "score_set_id": "st_test_llm_renderer_strong",
            "selected_candidate_meaning_state_preview": {
                "candidate_id": "ct_test_llm_renderer_strong",
                "title": "Strong Optional LLM Renderer Candidate",
                "candidate": claim,
                "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
                "memory_links": [
                    {
                        "memory_id": "m_optional_llm_renderer_definition",
                        "source_kind": "reference_document",
                        "source_path": "RMC Output Renderer Optional Layer",
                        "memory_role": "render_schema_source",
                        "phase_tags": ["Φ7", "Φ8"],
                        "confidence": 0.97,
                        "retrieval_weight": 0.90,
                    }
                ],
            },
            "selected_scored_candidate_preview": {
                "candidate_id": "ct_test_llm_renderer_strong",
                "coherence_score": 0.80,
            },
        },
    }


def fake_llm_good(payload: dict) -> dict:
    prompt = payload.get("prompt", "")
    assert "SENTENCE_PLAN_JSON" in prompt
    return {
        "response": (
            "Rendered output draft from μ_t: Render the corrected trace from the manifest while preserving echo validation "
            "and blocking unsupported projection. Phase path: Φ5 → Φ6 → Φ7 → Φ8. Manifest confidence: 0.827. "
            "Novelty: 0.210. Drift status: corrected_or_bounded_for_manifest. This is awaiting Echo Validator approval, "
            "not a memory write or final projection."
        )
    }


def fake_llm_forbidden(payload: dict) -> dict:
    return {"response": "This is approved final output with projection allowed and memory write allowed."}


def main() -> int:
    boundary = llm_renderer_boundary()
    schema = llm_renderer_schema_contract()
    renderer_b = renderer_boundary()
    renderer_s = renderer_schema_contract()
    check("llm_boundary_default_off", boundary["default_enabled"] is False and boundary["toggle_required"] is True)
    check("llm_boundary_no_writes", boundary["writes_files"] is False and boundary["writes_rmc_memory"] is False)
    check("llm_boundary_local_endpoint_only", boundary["approved_endpoint_policy"] == "local_http_loopback_only_C16")
    check("llm_schema_contract", schema["default_path"] == "deterministic_template_renderer")
    check("renderer_advertises_optional_llm", renderer_b.get("optional_llm_renderer_available") is True and renderer_s["optional_llm_renderer"]["default_enabled"] is False)
    check("toggle_on", normalize_llm_toggle("on") is True and normalize_llm_toggle("true") is True)
    check("toggle_off", normalize_llm_toggle("off") is False and normalize_llm_toggle(None) is False)
    check("endpoint_missing_refused", validate_model_endpoint("")["approved"] is False)
    check("endpoint_remote_refused", validate_model_endpoint("http://example.com/api/generate")["approved"] is False)
    check("endpoint_local_approved", validate_model_endpoint("http://localhost:11434/api/generate")["approved"] is True)

    manifest = compile_manifest(strong_c3r())
    check("manifest_ok", manifest.get("status") == "OK")

    default_render = render_manifest(manifest, render_mode="text")
    check("default_render_ok", default_render.get("status") == "OK")
    check("default_no_llm", default_render.get("llm_renderer_used") is False and (default_render.get("llm_render_attempt") or {}).get("status") == "SKIPPED")
    check("default_echo_required", default_render.get("echo_validation_required") is True and default_render.get("approved_output") is False)

    missing_endpoint = render_manifest(manifest, render_mode="text", llm_renderer_enabled=True)
    check("enabled_missing_endpoint_blocks", missing_endpoint.get("status") == "BLOCKED" and (missing_endpoint.get("llm_render_attempt") or {}).get("failure_code") == "LLM_RENDERER_ENDPOINT_MISSING")

    remote_endpoint = render_manifest(manifest, render_mode="text", llm_renderer_enabled=True, model_endpoint="http://example.com/api/generate")
    check("remote_endpoint_blocks", remote_endpoint.get("status") == "BLOCKED" and (remote_endpoint.get("llm_render_attempt") or {}).get("failure_code") == "LLM_RENDERER_ENDPOINT_HOST_REFUSED")

    llm_render = render_manifest(
        manifest,
        render_mode="text",
        llm_renderer_enabled=True,
        model_endpoint="http://localhost:11434/api/generate",
        model="qwen3:8b",
        llm_client=fake_llm_good,
    )
    check("llm_render_ok", llm_render.get("status") == "OK")
    check("llm_used", llm_render.get("llm_renderer_used") is True and (llm_render.get("llm_render_attempt") or {}).get("calls_llm") is True)
    check("llm_sentence_guard_passed", (llm_render.get("sentence_plan_validation") or {}).get("passed") is True)
    check("llm_still_not_approved", llm_render.get("approved_output") is False and llm_render.get("memory_write_allowed") is False)
    echo = validate_echo(llm_render)
    check("llm_subject_to_echo", echo.get("status") == "OK" and echo.get("echo_validation_passed") in (True, False) and echo.get("memory_write_allowed") is False)

    forbidden = render_manifest(
        manifest,
        render_mode="text",
        llm_renderer_enabled=True,
        model_endpoint="http://localhost:11434/api/generate",
        llm_client=fake_llm_forbidden,
    )
    check("forbidden_llm_output_blocked", forbidden.get("status") == "BLOCKED" and "forbidden_claim" in str(forbidden.get("sentence_plan_validation")))
    check("forbidden_no_memory_write", forbidden.get("memory_write_allowed") is False and forbidden.get("projection_allowed") is False)

    json_render = render_manifest(manifest, render_mode="json_packet", llm_renderer_enabled=True, model_endpoint="http://localhost:11434/api/generate", llm_client=fake_llm_good)
    check("non_text_mode_does_not_use_llm", json_render.get("status") == "OK" and json_render.get("llm_renderer_used") is False)

    print("RESULT: llm_renderer_C16_behavior_tests_pass=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
