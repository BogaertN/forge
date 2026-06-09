#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C10 contract guardrails."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from rmc_engine_v1.echo_validator import ECHO_THRESHOLDS_BY_MODE, validate_echo  # noqa: E402
from rmc_engine_v1.manifest_compiler import compile_manifest, manifest_schema_contract  # noqa: E402
from rmc_engine_v1.measurement_kernel import stable_hash, stable_id  # noqa: E402
from rmc_engine_v1.output_renderer import render_manifest  # noqa: E402
from test_rmc_manifest_compiler_C4 import strong_c3r  # noqa: E402


def check(name: str, condition: bool, detail: str = "") -> bool:
    if condition:
        print(f"[PASS] {name}" + (f" :: {detail}" if detail else ""))
        return True
    print(f"[FAIL] {name}" + (f" :: {detail}" if detail else ""))
    return False


def direct_manifest(claim: str) -> dict:
    mu = {
        "claim": claim,
        "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
        "operator_path": [
            {"op": "χ_t", "status": "passed"},
            {"op": "N_t", "status": "passed"},
            {"op": "μ_t", "status": "compiled"},
        ],
        "memory_links": [
            {"memory_id": "m_c10_guard", "source": "C10 test", "phase": "Φ6", "confidence": 0.92},
        ],
        "confidence": 0.84,
        "novelty": 0.22,
        "drift_status": {
            "status": "corrected_or_bounded_for_manifest",
            "pre_epsilon_s": 0.31,
            "post_epsilon_s": 0.18,
            "memory_fit": 0.81,
            "semantic_distance": 0.19,
        },
        "projection_status": {
            "status": "internal_manifest_ready_for_renderer_echo_gate",
            "projection_ready": True,
            "projection_allowed_now": False,
            "renderer_required": True,
            "echo_validation_required": True,
            "memory_write_allowed_now": False,
        },
        "output_targets": [{"target": "text"}],
    }
    return {
        "status": "OK",
        "manifest_compilation_allowed": True,
        "manifest_id": stable_id("mut", mu),
        "manifest_symbol": "μ_t",
        "manifest_hash": stable_hash(mu),
        "μ_t": mu,
    }


def main() -> int:
    ok = True

    schema = manifest_schema_contract()
    ok &= check("projection_status_is_required", "projection_status" in schema.get("required_fields", []))

    compiled = compile_manifest(strong_c3r())
    packet = compiled.get("manifest_packet") or {}
    mu = packet.get("μ_t") or {}
    ok &= check("compiled_mu_has_projection_status", isinstance(mu.get("projection_status"), dict))
    ok &= check("projection_status_blocks_now", mu.get("projection_status", {}).get("projection_allowed_now") is False)

    missing_projection = copy.deepcopy(packet)
    missing_projection["μ_t"].pop("projection_status", None)
    blocked_missing = render_manifest(missing_projection, render_mode="text")
    ok &= check("renderer_blocks_mu_missing_projection_status", blocked_missing.get("status") == "BLOCKED" and "projection_status" in str(blocked_missing.get("blocked_render_candidate")))

    rendered = render_manifest(compiled, render_mode="text")
    validation = validate_echo(rendered)
    vt = validation.get("V_t") or {}
    ok &= check("text_echo_threshold_raised", vt.get("echo_threshold_key") == "text" and float(vt.get("echo_threshold", 0.0)) >= 0.82)
    ok &= check("text_echo_passes_when_manifest_preserved", validation.get("echo_validation_passed") is True)

    formal_rendered = render_manifest(compiled, render_mode="text", style_mode="formal")
    formal_validation = validate_echo(formal_rendered)
    formal_vt = formal_validation.get("V_t") or {}
    ok &= check("formal_text_threshold_uses_085", formal_vt.get("echo_threshold_key") == "formal_text" and abs(float(formal_vt.get("echo_threshold", 0.0)) - 0.85) < 1e-9)

    debug_rendered = render_manifest(compiled, render_mode="text", style_mode="internal_debug")
    debug_validation = validate_echo(debug_rendered)
    debug_vt = debug_validation.get("V_t") or {}
    ok &= check("debug_threshold_preserved_for_internal_mode", debug_vt.get("echo_threshold_key") == "internal_debug" and abs(float(debug_vt.get("echo_threshold", 0.0)) - 0.72) < 1e-9)

    json_rendered = render_manifest(compiled, render_mode="json_packet")
    json_validation = validate_echo(json_rendered)
    json_vt = json_validation.get("V_t") or {}
    ok &= check("json_packet_threshold_is_strict", json_vt.get("echo_threshold_key") == "json_packet" and abs(float(json_vt.get("echo_threshold", 0.0)) - 0.90) < 1e-9)

    forbidden = render_manifest(direct_manifest("This manifest says projection allowed before echo validation."), render_mode="text")
    ok &= check("forbidden_claims_blocked_by_renderer", forbidden.get("status") == "BLOCKED" and "forbidden_claims_present" in str(forbidden.get("blocked_render_candidate")))
    ok &= check("forbidden_claims_reported", "projection allowed" in str(forbidden.get("sentence_plan_validation", {}).get("forbidden_hits", [])).lower())

    allowed = render_manifest(direct_manifest("Preserve the corrected manifest as an internal draft awaiting echo validation."), render_mode="text")
    ok &= check("lawful_claim_renders", allowed.get("status") == "OK")
    ok &= check("sentence_plan_present", isinstance((allowed.get("render_packet") or {}).get("sentence_plan"), dict))
    ok &= check("sentence_plan_forbidden_claims_enforced", (allowed.get("render_packet") or {}).get("sentence_plan_validation", {}).get("forbidden_claims_enforced") is True)

    ok &= check("threshold_table_complete", {"formal_text", "text", "json_packet", "dashboard_state", "glyph_packet", "internal_debug"}.issubset(ECHO_THRESHOLDS_BY_MODE.keys()))

    print(f"RESULT: rmc_contract_guardrails_C10_behavior_tests_pass={bool(ok)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
