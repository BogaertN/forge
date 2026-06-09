#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C14 real glyph renderer."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.glyph_renderer import (  # noqa: E402
    ENGINE_VERSION,
    GLYPH_PACKET_KIND,
    REQUIRED_GLYPH_PACKET_FIELDS,
    glyph_renderer_boundary,
    glyph_renderer_schema_contract,
    glyph_renderer_status,
    render_glyph_packet,
    render_phase_glyph,
)
from rmc_engine_v1.output_renderer import render_manifest  # noqa: E402
from rmc_engine_v1.manifest_compiler import compile_manifest  # noqa: E402


def _assert(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"[FAIL] {name} {detail}".rstrip())
    print(f"[PASS] {name}")


def _manifest_source() -> dict:
    claim = "Render a deterministic glyph packet from a corrected manifest trace."
    return {
        "status": "OK",
        "trace_id": "rmctrace_test_glyph_C14",
        "run_id": "c3run_test_glyph_C14",
        "score_set_id": "st_test_glyph_C14",
        "candidate_set_id": "ct_set_test_glyph_C14",
        "selected_candidate_id": "ct_test_glyph_C14",
        "chi_t_present": True,
        "N_t_present": True,
        "chi_t": {
            "status": "correction_passes_stable_for_naming_dry_run",
            "correction_allowed": True,
            "candidate_id": "ct_test_glyph_C14",
            "candidate_validity_score": 0.81,
            "projection_gated_score": 0.0,
            "measured_inputs": {
                "epsilon_s": 0.20,
                "D_score": 0.30,
                "sigma_res": 0.08,
                "semantic_distance": 0.28,
                "memory_fit": 0.82,
                "novelty_delta": 0.20,
                "source_confidence": 0.92,
            },
            "quality_calibration": {"candidate_validity_score": 0.81, "projection_gated_score": 0.0, "novelty_budget": 0.55},
            "phase_repair": {
                "repaired_phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
                "repaired_phase_metrics": {"phase_path_legal": True, "phase_validity_score": 0.94, "phase_warnings": []},
            },
            "correction_math": {"post_correction_estimate": {"epsilon_s": 0.143333}},
            "route_consistency": {
                "recommended_route": "route_to_naming_engine",
                "chi_t_action": "route_to_naming_engine",
                "route_consistent": True,
            },
        },
        "N_t": {
            "status": "naming_candidate_stable_internal_only",
            "naming_allowed": True,
            "stable_naming": True,
            "candidate_id": "ct_test_glyph_C14",
            "proposed_name": "Deterministic Glyph Packet",
            "machine_name": "deterministic_glyph_packet",
            "definition": claim,
            "phase_role": "Φ7 naming after Φ6 correction",
            "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
            "allowed_use": ["internal_trace_label", "glyph_packet_rendering"],
            "forbidden_use": ["public_projection", "memory_write_as_truth"],
            "naming_confidence_report": {"naming_confidence": 0.82, "components": {"memory_fit": 0.82, "phase_validity": 0.94}},
        },
        "source_coherence_scorer": {
            "trace_id": "rmctrace_test_glyph_C14",
            "selected_candidate_meaning_state_preview": {
                "candidate_id": "ct_test_glyph_C14",
                "candidate": claim,
                "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
                "memory_links": [{"memory_id": "m_glyph_codex", "source_path": "FBSC Phase Glyph Codex v2.5", "phase_tags": ["Φ7", "Φ8"], "confidence": 0.96}],
            },
            "selected_scored_candidate_preview": {"candidate_id": "ct_test_glyph_C14", "coherence_score": 0.76},
        },
    }


def main() -> int:
    boundary = glyph_renderer_boundary()
    schema = glyph_renderer_schema_contract()
    _assert("engine_version_C14", ENGINE_VERSION.endswith("C14"))
    _assert("boundary_read_only", boundary.get("writes_files") is False and boundary.get("writes_rmc_memory") is False)
    _assert("boundary_no_llm_chroma_shell", boundary.get("uses_llm") is False and boundary.get("queries_chroma") is False and boundary.get("executes_shell") is False)
    _assert("image_generation_not_authority", boundary.get("image_generation_is_authority") is False and schema.get("image_generation_policy", {}).get("generated_images_cannot_create_authoritative_phase_meaning") is True)

    status = glyph_renderer_status()
    _assert("status_ok", status.get("status") == "OK")
    _assert("status_has_nine_phases", status.get("phase_count") == 9)

    seeds = set()
    for i in range(1, 10):
        phase = f"Φ{i}"
        result = render_phase_glyph(phase)
        packet = result.get("glyph_packet") or {}
        _assert(f"{phase}_renders", result.get("status") == "OK" and packet.get("glyph_packet_kind") == GLYPH_PACKET_KIND)
        _assert(f"{phase}_svg_present", "<svg" in str(packet.get("glyph_svg")) and phase in str(packet.get("glyph_svg")))
        _assert(f"{phase}_color_present", str(packet.get("color_hex", "")).startswith("#"))
        _assert(f"{phase}_seed_present", bool(packet.get("glyph_seed")))
        seeds.add(packet.get("glyph_seed"))
    _assert("seeds_are_phase_distinct", len(seeds) == 9)

    direct_a = render_glyph_packet({"phase_path": ["Φ5", "Φ6", "Φ7"]}, render_mode="composite_glyph")
    direct_b = render_glyph_packet({"phase_path": ["Φ5", "Φ6", "Φ7"]}, render_mode="composite_glyph")
    packet_a = direct_a.get("glyph_packet") or {}
    packet_b = direct_b.get("glyph_packet") or {}
    _assert("composite_status_ok", direct_a.get("status") == "OK")
    _assert("composite_phase_path_preserved", packet_a.get("phase_path") == ["Φ5", "Φ6", "Φ7"])
    _assert("composite_seed_deterministic", packet_a.get("glyph_seed") == packet_b.get("glyph_seed"))
    _assert("composite_svg_contains_three_phases", str(packet_a.get("glyph_svg", "")).count('class="glyph-phase') == 3)

    cold = render_glyph_packet({"phase_path": ["Φ5"]}, render_mode="cold_storage_glyph")
    _assert("cold_storage_visual_state", (cold.get("glyph_packet") or {}).get("visual_state") == "cold_storage")
    drift = render_glyph_packet({"phase_path": ["Φ8"]}, render_mode="drift_state_glyph")
    _assert("drift_visual_state", (drift.get("glyph_packet") or {}).get("visual_state") == "drift")

    invalid = render_phase_glyph("Φ10")
    _assert("invalid_phase_blocks", invalid.get("status") == "BLOCKED" and invalid.get("failure_code") == "invalid_phase_id")

    manifest = compile_manifest(_manifest_source())
    _assert("manifest_ok", manifest.get("status") == "OK")
    glyph_result = render_glyph_packet(manifest, render_mode="phase_path_glyph")
    glyph_packet = glyph_result.get("glyph_packet") or {}
    _assert("manifest_glyph_ok", glyph_result.get("status") == "OK")
    for field in REQUIRED_GLYPH_PACKET_FIELDS:
        _assert(f"packet_field_{field}", field in glyph_packet)
    _assert("source_manifest_id_preserved", glyph_packet.get("source_manifest_id") == (manifest.get("manifest_packet") or {}).get("manifest_id"))
    _assert("phase_path_from_mu", glyph_packet.get("phase_path") == ["Φ5", "Φ6", "Φ7", "Φ8"])
    _assert("echo_validation_ready", glyph_packet.get("echo_validation_ready") is True)
    _assert("no_memory_write", glyph_packet.get("memory_write_allowed") is False and glyph_packet.get("writes_files") is False)

    rendered = render_manifest(manifest, render_mode="glyph_packet")
    rendered_packet = rendered.get("R_t") or {}
    _assert("output_renderer_uses_real_glyph", rendered_packet.get("glyph_packet_kind") == GLYPH_PACKET_KIND)
    _assert("output_renderer_svg_present", "<svg" in str(rendered_packet.get("glyph_svg")))
    _assert("output_renderer_not_placeholder", "fbsc_phase_glyph::" not in str(rendered_packet))

    print("RESULT: glyph_renderer_C14_behavior_tests_pass=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
