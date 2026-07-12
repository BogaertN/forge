#!/usr/bin/env python3
"""Source behavior tests for Slice 23 dry-run harness scaffold."""

from __future__ import annotations

from pathlib import Path
import sys

REQUIRED_STEP_ORDER = (
    "input_text_fixture",
    "candidate_meaning_boundary",
    "concept_boundary",
    "predicate_frame_boundary",
    "verbal_gate_boundary",
    "selected_state_candidate_boundary",
    "expression_boundary",
    "read_only_inspection_reference",
)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))

    from aiweb_end_to_end_dry_run_harness_scaffold.authority import (
        DOWNSTREAM_FALSE_ONLY_FIELDS,
        REQUIRED_DRY_RUN_LAWS,
        REQUIRED_DRY_RUN_STEP_ORDER,
        build_authority_separation_record,
        validate_authority_separation_record,
    )
    from aiweb_end_to_end_dry_run_harness_scaffold.core import (
        build_demo_harness_record,
        validate_dry_run_harness_record,
    )
    from aiweb_end_to_end_dry_run_harness_scaffold.fixture import (
        BLOCKED_ACTION_FIXTURE_KEY,
        SAFE_DISPLAY_FIXTURE_KEY,
        build_default_fixtures,
    )
    from aiweb_end_to_end_dry_run_harness_scaffold.receipt import build_receipt, validate_receipt
    from aiweb_end_to_end_dry_run_harness_scaffold.verify import verify_slice23_boundary

    failures: list[str] = []

    if REQUIRED_DRY_RUN_STEP_ORDER != REQUIRED_STEP_ORDER:
        failures.append("required step order changed")

    authority = build_authority_separation_record()
    authority_report = validate_authority_separation_record(authority)
    if not authority_report.passed:
        failures.extend("authority:" + issue.field + ":" + issue.reason for issue in authority_report.issues)

    fixtures = build_default_fixtures()
    if tuple(f.fixture_key for f in fixtures) != (SAFE_DISPLAY_FIXTURE_KEY, BLOCKED_ACTION_FIXTURE_KEY):
        failures.append("fixture identity or order changed")
    if len({f.fixture_id for f in fixtures}) != 2:
        failures.append("fixture identifiers are not unique")
    if build_default_fixtures()[0].fixture_id != fixtures[0].fixture_id:
        failures.append("fixture identifiers are not deterministic")

    harness = build_demo_harness_record()
    harness_report = validate_dry_run_harness_record(harness)
    if not harness_report.passed:
        failures.extend("harness:" + issue.field + ":" + issue.reason for issue in harness_report.issues)

    for field_name in DOWNSTREAM_FALSE_ONLY_FIELDS:
        if bool(getattr(harness, field_name)):
            failures.append("harness authority flag became true: " + field_name)

    for path in harness.paths:
        if path.step_order != REQUIRED_STEP_ORDER:
            failures.append("path step order changed for " + path.fixture_key)
        if tuple(step.step_key for step in path.steps) != REQUIRED_STEP_ORDER:
            failures.append("step sequence changed for " + path.fixture_key)
        if not path.no_memory_write or not path.no_delivery or not path.no_action:
            failures.append("effect boundary changed for " + path.fixture_key)
        if path.fixture_key == BLOCKED_ACTION_FIXTURE_KEY and not path.blocked_before_memory_delivery_or_action:
            failures.append("blocked fixture did not stop before effects")

    receipt_a = build_receipt(harness)
    receipt_b = build_receipt(build_demo_harness_record())
    failures.extend(validate_receipt(receipt_a))
    if receipt_a.receipt_id != receipt_b.receipt_id:
        failures.append("receipt id unstable")
    if receipt_a.harness_digest != receipt_b.harness_digest:
        failures.append("receipt digest unstable")
    if receipt_a.dry_run_laws != REQUIRED_DRY_RUN_LAWS:
        failures.append("receipt law set changed")

    verifier_result = verify_slice23_boundary(repo, require_git_context=False)
    if not verifier_result.passed:
        failures.extend(verifier_result.failures)

    if failures:
        print("AIWEB SLICE 23 SOURCE BEHAVIOR TEST: FAIL")
        for failure in failures:
            print(" - " + failure)
        return 1

    print("AIWEB SLICE 23 SOURCE BEHAVIOR TEST: PASS")
    print("checked_step_count=" + str(len(REQUIRED_STEP_ORDER)))
    print("checked_fixture_count=" + str(len(fixtures)))
    print("checked_path_count=" + str(len(harness.paths)))
    print("receipt_id=" + receipt_a.receipt_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
