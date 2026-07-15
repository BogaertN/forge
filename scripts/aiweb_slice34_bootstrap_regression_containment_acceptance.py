#!/usr/bin/env python3
"""Developer CLI for Slice 34 in-memory containment evaluation."""

from __future__ import annotations

from pathlib import Path
import sys

sys.dont_write_bytecode = True
REPO_ROOT = str(Path(__file__).resolve().parents[1])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import argparse
import json

from aiweb_language_core_bootstrap.regression_containment import (
    FLOW_IDENTITY_EXPECTATIONS,
    PROHIBITED_AUTHORITY_CATEGORIES,
    REQUIRED_CONTAINMENT_GUARDS,
    REQUIRED_INHERITED_REGRESSION_COMMAND_COUNT,
    REQUIRED_PHASE_B_PRESERVATION_COMMAND_COUNT,
    REQUIRED_PRIOR_COMMAND_COUNT,
    run_default_containment_evaluation,
    run_explicit_offline_containment_evaluation,
    validate_bootstrap_containment_evaluation,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-requirements", action="store_true")
    parser.add_argument(
        "--enable-offline-containment-evaluation",
        action="store_true",
    )
    args = parser.parse_args()

    if args.list_requirements:
        payload = {
            "flow_names": [item.flow_name for item in FLOW_IDENTITY_EXPECTATIONS],
            "containment_guard_ids": list(REQUIRED_CONTAINMENT_GUARDS),
            "prohibited_authority_categories": list(PROHIBITED_AUTHORITY_CATEGORIES),
            "inherited_regression_command_count": (
                REQUIRED_INHERITED_REGRESSION_COMMAND_COUNT
            ),
            "phase_b_preservation_command_count": (
                REQUIRED_PHASE_B_PRESERVATION_COMMAND_COUNT
            ),
            "total_prior_command_count": REQUIRED_PRIOR_COMMAND_COUNT,
            "one_command_rollback_required": True,
            "technical_acceptance_granted_by_runtime": False,
        }
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        return 0

    evaluation = (
        run_explicit_offline_containment_evaluation()
        if args.enable_offline_containment_evaluation
        else run_default_containment_evaluation()
    )
    report = validate_bootstrap_containment_evaluation(evaluation)
    print(json.dumps(evaluation.to_dict(), sort_keys=True, separators=(",", ":")))
    if not report.ok:
        return 1
    return 0 if evaluation.runtime_containment_passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
