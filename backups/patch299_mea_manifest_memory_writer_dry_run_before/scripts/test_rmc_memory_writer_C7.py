#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C7 Memory Writer Dry-Run."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.memory_writer import (  # noqa: E402
    memory_writer_boundary,
    memory_writer_schema_contract,
    plan_memory_write,
)


def _strong_echo_report(claim: str = "AI.Web compiles traceable meaning before rendering language") -> dict:
    mu = {
        "claim": claim,
        "phase_path": ["Φ5", "Φ6", "Φ7", "Φ8"],
        "operator_path": ["drift_check", "chi_t_correction", "naming_gate", "render_gate"],
        "memory_links": [
            {"memory_id": "m_rmc_manifest", "source": "RMC Section 3.6", "confidence": 0.93, "phase": "Φ7"},
            {"memory_id": "m_rmc_trace", "source": "RMC Axiom 1", "confidence": 0.91, "phase": "Φ6"},
            {"memory_id": "m_rmc_render", "source": "RMC Section 3.7", "confidence": 0.88, "phase": "Φ8"},
        ],
        "confidence": 0.88,
        "novelty": 0.42,
        "drift_status": {"status": "corrected_bounded_drift", "post_epsilon_s": 0.18, "pre_epsilon_s": 0.31},
        "output_targets": ["text", "json_packet", "memory_record"],
    }
    render_packet = {
        "rendered_output_id": "rt_test_good",
        "source_manifest_id": "mu_test_good",
        "render_mode": "text",
        "audience_profile": "developer",
        "style_mode": "precise",
        "R_t": (
            f"{claim}. Phase path Φ5 → Φ6 → Φ7 → Φ8 preserves drift_check, chi_t_correction, "
            "naming_gate, and render_gate. Drift status corrected_bounded_drift with epsilon 0.18. "
            "Confidence 0.88; novelty 0.42."
        ),
        "render_fidelity_precheck": {"passed": True},
        "echo_validation_required": True,
    }
    return {
        "status": "OK",
        "echo_run_id": "echo_test_good",
        "source_output_renderer": {
            "render_run_id": "render_test_good",
            "render_packet": render_packet,
            "source_manifest_packet": {"manifest_id": "mu_test_good", "μ_t": mu},
        },
        "V_t": {
            "echo_validation_id": "vt_test_good",
            "source_rendered_output_id": "rt_test_good",
            "source_manifest_id": "mu_test_good",
            "echo_score": 0.91,
            "echo_components": {
                "claim_preservation": 0.95,
                "phase_preservation": 1.0,
                "drift_preservation": 0.9,
                "metric_preservation": 0.9,
                "memory_preservation": 0.85,
                "operator_preservation": 1.0,
                "schema_integrity": 1.0,
            },
            "echo_validation_passed": True,
            "distortion_flags": [],
            "recommended_route": "route_to_memory_writer_dry_run",
        },
    }


def _weak_echo_report() -> dict:
    report = _strong_echo_report("Weak speculative branch")
    report["V_t"]["echo_score"] = 0.61
    report["V_t"]["echo_validation_passed"] = False
    report["V_t"]["distortion_flags"] = ["claim_changed", "drift_status_omitted"]
    return report


def _assert(name: str, condition: bool) -> None:
    if not condition:
        print(f"[FAIL] {name}")
        raise SystemExit(1)
    print(f"[PASS] {name}")


def main() -> None:
    boundary = memory_writer_boundary()
    schema = memory_writer_schema_contract()
    good = plan_memory_write(_strong_echo_report())
    weak = plan_memory_write(_weak_echo_report())
    missing = plan_memory_write({"status": "BLOCKED"})

    _assert("boundary_read_only", boundary.get("read_only") is True and boundary.get("writes_files") is False)
    _assert("schema_formula", "write_eligibility_formula" in schema)
    _assert("good_status_ok", good.get("status") == "OK")
    _assert("W_t_present", good.get("W_t_present") is True)
    _assert("plan_allowed", good.get("memory_write_plan_allowed") is True)
    _assert("actual_files_empty", good.get("actual_files_written") == [])
    _assert("no_live_write", good.get("writes_files") is False and good.get("rmc_live_memory_write") is False)
    _assert("write_plan_has_node", isinstance((good.get("write_plan") or {}).get("memory_node_preview"), dict))
    _assert("write_plan_has_feedback_object", isinstance((good.get("write_plan") or {}).get("feedback_object_preview"), dict))
    feedback = (good.get("write_plan") or {}).get("feedback_object_preview") or {}
    for field in ["feedback_id", "feedback_object_type", "feedback_kind", "source_manifest_id", "source_rendered_output_id", "source_echo_validation_id", "source_memory_node_id", "feedback_signal", "feedback_status", "retrieval_tags"]:
        _assert(f"feedback_field_{field}", field in feedback)
    _assert("feedback_is_first_class", feedback.get("feedback_object_type") == "rmc_feedback_t_v1" and "feedback_t" in (feedback.get("retrieval_tags") or []))
    _assert("feedback_no_fake_user_feedback", ((feedback.get("feedback_signal") or {}).get("user_feedback_present") is False))
    node = (good.get("write_plan") or {}).get("memory_node_preview") or {}
    for field in ["content", "source", "phase", "confidence", "ancestry", "prior_drift_score", "retrieval_weight", "tags"]:
        _assert(f"node_field_{field}", field in node)
    elig = ((good.get("write_plan") or {}).get("write_eligibility") or {})
    _assert("eligibility_formula_present", "formula" in elig)
    _assert("eligibility_threshold_passes", elig.get("passes_threshold") is True and elig.get("write_eligibility_score", 0) >= 0.72)
    _assert("target_preview_not_written", "absolute_path_preview" in ((good.get("write_plan") or {}).get("write_target_preview") or {}))
    _assert("receipt_preview_not_written", ((good.get("write_plan") or {}).get("receipt_preview") or {}).get("actual_files_written") == [])
    _assert("feedback_target_preview_present", "absolute_path_preview" in ((good.get("write_plan") or {}).get("feedback_target_preview") or {}))
    _assert("duplicate_preview_present", "duplicate_check_preview" in (good.get("write_plan") or {}))
    _assert("weak_blocked", weak.get("status") == "BLOCKED" and weak.get("W_t_present") is False)
    _assert("weak_reason_echo_failed", "echo_validation_failed" in ((weak.get("blocked_write_candidate") or {}).get("reason_codes") or []))
    _assert("missing_blocked", missing.get("status") == "BLOCKED" and missing.get("memory_write_plan_allowed") is False)
    _assert("missing_reason", "missing_echo_validation" in ((missing.get("blocked_write_candidate") or {}).get("reason_codes") or []))
    _assert("gate_classification_present", isinstance(good.get("gate_classification"), dict) and isinstance(weak.get("gate_classification"), dict))

    print("RESULT: memory_writer_C7_behavior_tests_pass=True")


if __name__ == "__main__":
    main()
