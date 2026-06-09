#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C8 Gated Memory Writer Commit."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.memory_writer import (  # noqa: E402
    APPROVAL_TOKEN,
    commit_memory_write,
    gated_memory_writer_boundary,
    gated_memory_writer_schema_contract,
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
        "trace_id": "trace_test_good",
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
    boundary = gated_memory_writer_boundary()
    schema = gated_memory_writer_schema_contract()
    good_report = _strong_echo_report()
    dry_run = plan_memory_write(good_report)

    _assert("boundary_actual_writer", boundary.get("actual_writer_stage_present") is True and boundary.get("read_only") is False)
    _assert("schema_has_commit_formula", "W_t_commit" in schema.get("formula", ""))
    _assert("dry_run_ready", dry_run.get("status") == "OK" and dry_run.get("W_t_present") is True)

    with tempfile.TemporaryDirectory(prefix="rmc_c8_test_") as tmp:
        tmp_path = Path(tmp)
        no_approval = commit_memory_write(good_report, approval_token=None, memory_root=str(tmp_path))
        _assert("no_approval_refused", no_approval.get("status") == "REFUSED")
        _assert("no_approval_no_files", no_approval.get("actual_files_written") == [])
        _assert("no_approval_failure_code", no_approval.get("failure_code") == "RMC_MEMORY_WRITE_REQUIRES_EXPLICIT_APPROVAL")

        committed = commit_memory_write(good_report, approval_token=APPROVAL_TOKEN, memory_root=str(tmp_path))
        _assert("commit_status_ok", committed.get("status") == "OK")
        _assert("commit_present", committed.get("W_t_commit_present") is True)
        _assert("memory_write_committed", committed.get("memory_write_committed") is True)
        _assert("actual_files_written_nonempty", len(committed.get("actual_files_written") or []) == 3)
        _assert("writes_files_true", committed.get("writes_files") is True and committed.get("rmc_live_memory_write") is True)
        _assert("no_identity_or_canonical", committed.get("identity_vault_write") is False and committed.get("canonical_reference_write") is False)
        _assert("projection_still_false", committed.get("projection_allowed") is False and committed.get("public_output_projection") is False)

        for file_path in committed.get("actual_files_written") or []:
            path = Path(file_path).resolve()
            _assert(f"written_inside_root_{path.name}", tmp_path.resolve() == path or tmp_path.resolve() in path.parents)
            _assert(f"written_file_exists_{path.name}", path.exists())

        node_path = Path(committed["target_paths"]["memory_node"])
        receipt_path = Path(committed["target_paths"]["receipt"])
        index_path = Path(committed["target_paths"]["index"])
        node = json.loads(node_path.read_text(encoding="utf-8"))
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        index_lines = index_path.read_text(encoding="utf-8").splitlines()
        _assert("node_committed_status", node.get("write_status") == "committed_to_rmc_live_memory")
        _assert("receipt_commit_id_matches", receipt.get("commit_id") == committed.get("commit_id"))
        _assert("index_has_row", len(index_lines) == 1 and committed.get("commit_id") in index_lines[0])

        duplicate = commit_memory_write(good_report, approval_token=APPROVAL_TOKEN, memory_root=str(tmp_path))
        _assert("duplicate_refused", duplicate.get("status") == "REFUSED")
        _assert("duplicate_failure_code", duplicate.get("failure_code") == "RMC_MEMORY_WRITE_REFUSED_DUPLICATE")
        _assert("duplicate_no_files", duplicate.get("actual_files_written") == [])

    with tempfile.TemporaryDirectory(prefix="rmc_c8_weak_") as tmp2:
        weak = commit_memory_write(_weak_echo_report(), approval_token=APPROVAL_TOKEN, memory_root=tmp2)
        _assert("weak_upstream_refused", weak.get("status") == "REFUSED")
        _assert("weak_failure_code", weak.get("failure_code") == "RMC_MEMORY_WRITE_REFUSED_UPSTREAM_BLOCKED")
        _assert("weak_no_files", weak.get("actual_files_written") == [])

    print("RESULT: memory_writer_C8_behavior_tests_pass=True")


if __name__ == "__main__":
    main()
