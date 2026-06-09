#!/usr/bin/env python3
from __future__ import annotations

import copy
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.echo_validator import validate_echo, echo_validator_boundary, echo_validator_schema_contract
from rmc_engine_v1.measurement_kernel import stable_hash, stable_id


def _sample_mu():
    return {
        "claim": "Preserve the corrected phase path as an internal manifest before rendering.",
        "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
        "operator_path": ["drift_check", "chi_t_correction", "naming_gate", "render_gate"],
        "memory_links": [
            {"memory_id": "m_phase_gate", "source": "RMC axiom set", "phase": "Φ6", "confidence": 0.92},
            {"memory_id": "m_manifest_schema", "source": "Section 3.6", "phase": "Φ7", "confidence": 0.88},
        ],
        "confidence": 0.82,
        "novelty": 0.31,
        "drift_status": {
            "status": "corrected_bounded_drift",
            "pre_epsilon_s": 0.41,
            "post_epsilon_s": 0.22,
            "memory_fit": 0.74,
            "semantic_distance": 0.26,
        },
        "projection_status": {
            "status": "internal_manifest_ready_for_renderer_echo_gate",
            "projection_ready": True,
            "projection_allowed_now": False,
            "renderer_required": True,
            "echo_validation_required": True,
        },
        "output_targets": [{"target": "text"}],
    }


def _sample_manifest():
    mu = _sample_mu()
    return {
        "manifest_id": "mu_test_manifest_001",
        "manifest_symbol": "μ_t",
        "manifest_hash": stable_hash(mu),
        "μ_t": mu,
    }


def _sample_render_report():
    manifest = _sample_manifest()
    mu = manifest["μ_t"]
    text = (
        "Rendered output draft from μ_t: Preserve the corrected phase path as an internal manifest before rendering. "
        "Phase path: Φ5 → Φ6 → Φ7 → Φ8. "
        "Manifest confidence: 0.820. Novelty: 0.310. "
        "Drift status: corrected_bounded_drift; post-correction ε_s: 0.220. "
        "Memory links carried into this rendering: 2. "
        "Operators: drift_check, chi_t_correction, naming_gate, render_gate. "
        "This rendering awaits Echo Validator approval."
    )
    packet = {
        "rendered_output_id": stable_id("rt", {"text": text}),
        "render_symbol": "R_t",
        "source_manifest_id": manifest["manifest_id"],
        "source_manifest_hash": manifest["manifest_hash"],
        "render_mode": "text",
        "audience_profile": "operator",
        "style_mode": "standard",
        "R_t": text,
        "rendered_output_hash": stable_hash(text),
        "render_fidelity_precheck": {"fidelity_score": 0.94},
        "echo_validation_required": True,
        "approved_output": False,
        "projection_allowed": False,
        "memory_write_allowed": False,
    }
    return {
        "status": "OK",
        "rendering_allowed": True,
        "R_t_present": True,
        "render_packet": packet,
        "source_manifest_packet": manifest,
        "approved_output": False,
        "projection_allowed": False,
        "memory_write_allowed": False,
    }


def check(name, condition):
    if condition:
        print(f"[PASS] {name}")
        return True
    print(f"[FAIL] {name}")
    return False


def main() -> int:
    ok = True
    boundary = echo_validator_boundary()
    contract = echo_validator_schema_contract()
    good = validate_echo(_sample_render_report())

    ok &= check("boundary_read_only", boundary.get("writes_files") is False and boundary.get("writes_rmc_memory") is False)
    ok &= check("schema_formula", "echo_score_formula" in contract)
    ok &= check("good_status_ok", good.get("status") == "OK")
    ok &= check("V_t_present", good.get("V_t_present") is True and isinstance(good.get("V_t"), dict))
    ok &= check("echo_passed", good.get("echo_validation_passed") is True)
    ok &= check("score_range", 0.82 <= float(good.get("echo_score", 0)) <= 1.0)
    ok &= check("text_threshold_raised", float((good.get("V_t") or {}).get("echo_threshold", 0)) >= 0.82)
    ok &= check("components_present", "claim_preservation" in good.get("echo_components", {}))
    ok &= check("no_memory_write", good.get("memory_write_allowed") is False and good.get("approved_output") is False)
    ok &= check("next_route", good.get("recommended_route") == "route_to_memory_writer_dry_run")

    bad = _sample_render_report()
    bad["render_packet"] = copy.deepcopy(bad["render_packet"])
    bad["render_packet"]["R_t"] = "This is approved final output and projection allowed. Something unrelated."  # bad claim + forbidden approval
    bad["render_packet"]["rendered_output_hash"] = stable_hash(bad["render_packet"]["R_t"])
    bad_result = validate_echo(bad)
    ok &= check("bad_requires_repair", bad_result.get("status") == "ECHO_REPAIR_REQUIRED")
    ok &= check("bad_not_passed", bad_result.get("echo_validation_passed") is False)
    ok &= check("bad_hard_violation", bad_result.get("distortion_flags", {}).get("hard_violation") is True)
    ok &= check("bad_score_lower", float(bad_result.get("echo_score", 1)) < float(good.get("echo_score", 0)))

    blocked = validate_echo({"status": "BLOCKED", "rendering_allowed": False, "R_t_present": False})
    ok &= check("blocked_no_V_t", blocked.get("V_t_present") is False)
    ok &= check("blocked_reason", blocked.get("reason") in {"render_packet_missing_or_render_blocked", "R_t_not_present"})

    missing_mu = _sample_render_report()
    missing_mu.pop("source_manifest_packet", None)
    missing_mu["render_packet"].pop("source_manifest_packet", None)
    missing_result = validate_echo(missing_mu)
    ok &= check("missing_manifest_blocks", missing_result.get("status") == "BLOCKED")

    print(f"RESULT: echo_validator_C6_behavior_tests_pass={bool(ok)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
