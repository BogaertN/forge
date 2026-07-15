#!/usr/bin/env python3
"""Developer CLI for Slice 35E bounded MSM-v1 bootstrap integration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
REPO_ROOT = str(Path(__file__).resolve().parents[1])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from aiweb_language_core_bootstrap.meaning_structure_manifest.bootstrap_integration import (
    build_msm_bootstrap_integration_state,
    build_synthetic_msm_bootstrap_fixture,
    run_msm_bootstrap_integration,
    validate_msm_bootstrap_integration_result,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-requirements", action="store_true")
    parser.add_argument(
        "--enable-offline-msm-bootstrap-integration",
        action="store_true",
    )
    args = parser.parse_args()

    if args.list_requirements:
        payload = {
            "disabled_by_default": True,
            "explicit_enable_flag": "--enable-offline-msm-bootstrap-integration",
            "fixture_only": True,
            "offline_only": True,
            "read_only": True,
            "in_memory_only": True,
            "deterministic": True,
            "canonical_round_trip_required": True,
            "full_inherited_regression_required": True,
            "containment_proof_required": True,
            "rollback_proof_required": True,
            "runtime_acceptance_grant_allowed": False,
            "route_api_ui_allowed": False,
            "memory_evidence_resource_delivery_tool_action_allowed": False,
            "push_performed": False,
        }
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        return 0

    fixture = build_synthetic_msm_bootstrap_fixture()
    state = build_msm_bootstrap_integration_state(
        explicit_offline_developer_enable=(
            args.enable_offline_msm_bootstrap_integration
        )
    )
    result = run_msm_bootstrap_integration(
        fixture=fixture,
        integration_state=state,
    )
    report = validate_msm_bootstrap_integration_result(result)
    print(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":")))
    if not report.ok:
        return 1
    return 0 if result.bounded_integration_completed else 2


if __name__ == "__main__":
    raise SystemExit(main())
