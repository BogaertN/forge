#!/usr/bin/env python3
"""Visible behavior and adversarial test for AI.Web Slice 43D."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import importlib
from pathlib import Path
import runpy
import sys


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.malformed_cases = 0
        self.explicit_outcome_cases = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)

    def malformed(self, condition: object, label: str) -> None:
        self.malformed_cases += 1
        self.check(condition, label)

    def outcome_case(self, condition: object, label: str) -> None:
        self.explicit_outcome_cases += 1
        self.check(condition, label)


def build_exact_slice42_source(repository: Path):
    helper = runpy.run_path(
        str(
            repository
            / "scripts"
            / "test_aiweb_slice43c_authorized_meaning_proposed_expression_admission.py"
        )
    )
    return helper["build_exact_slice42_source"](repository)


def main() -> int:
    repository = Path(
        sys.argv[1] if len(sys.argv) == 2 else "/home/nic/forge"
    ).resolve()
    if len(sys.argv) > 2:
        raise SystemExit(
            "usage: test_aiweb_slice43d_meaning_preservation_comparison.py "
            "[REPOSITORY]"
        )
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))

    ledger = Ledger()
    admission = importlib.import_module(
        "aiweb_language_core_bootstrap.rmc_echo_runtime."
        "authorized_source_admission"
    )
    comparison = importlib.import_module(
        "aiweb_language_core_bootstrap.rmc_echo_runtime."
        "meaning_preservation_comparison"
    )

    _, _, source = build_exact_slice42_source(repository)
    source_request = admission.build_source_admission_request(source)
    source_result = (
        admission.admit_authorized_meaning_and_proposed_expression(
            source_request
        )
    )

    ledger.check(
        comparison.SLICE43D_ACCEPTED_PARENT_HEAD
        == "6f2cbafc18ef9eff259bca038d189f1bbe7fc4c6",
        "exact accepted Slice 43C parent",
    )
    ledger.check(
        comparison.SLICE43D_ACCEPTED_PARENT_TREE
        == "c378cb1cd0be715160a9f919ea01815799ee4f56",
        "exact accepted Slice 43C parent tree",
    )
    ledger.check(
        comparison.SLICE43D_COMMIT_SUBJECT
        == "Slice 43D deterministic meaning-preservation comparison findings",
        "exact commit subject",
    )
    ledger.check(
        len(comparison.COMPARISON_DIMENSION_VALUES) == 13,
        "exact thirteen comparison dimensions",
    )
    ledger.check(
        len(comparison.FINDING_OUTCOME_VALUES) == 6,
        "exact six finding outcomes",
    )
    ledger.check(
        len(comparison.PERMANENT_AUTHORITY_ZERO) == 10,
        "ten authority-zero boundaries",
    )
    ledger.check(
        source_result.status is admission.SourceAdmissionStatus.ADMITTED,
        "exact Slice 43C result admitted",
    )
    ledger.check(
        source_result.admission_result_id
        == comparison.EXACT_ACCEPTED_SLICE43C_ID_MAP["result"],
        "exact accepted Slice 43C result identity",
    )

    request = comparison.build_comparison_request(source_result, source)
    ledger.check(
        request.request_id == comparison.expected_record_id(request),
        "comparison request deterministic identity",
    )
    ledger.check(request.raw_text is None, "comparison request has no raw text")
    ledger.check(
        request.explicit_comparison_request is True,
        "comparison request is explicit",
    )
    input_report = comparison.validate_comparison_inputs(
        request,
        source_result,
        source,
    )
    ledger.check(input_report.ok, "exact comparison input validates")

    first = comparison.compare_meaning_preservation(
        request,
        source_result,
        source,
    )
    ledger.check(
        first.status
        is comparison.ComparisonExecutionStatus.FINDINGS_CREATED,
        "findings-created operational status",
    )
    ledger.check(first.comparison_performed is True, "comparison performed")
    ledger.check(first.findings_created is True, "findings created")
    ledger.check(
        first.dimension_finding_count == 13,
        "thirteen dimension findings created",
    )
    ledger.check(
        first.preserved_finding_count == 13,
        "accepted fixture has thirteen preserved findings",
    )
    ledger.check(first.changed_finding_count == 0, "no changed findings")
    ledger.check(first.missing_finding_count == 0, "no missing findings")
    ledger.check(
        first.unsupported_finding_count == 0,
        "no unsupported findings",
    )
    ledger.check(first.conflicted_finding_count == 0, "no conflicted findings")
    ledger.check(
        first.indeterminate_finding_count == 0,
        "no indeterminate findings",
    )
    ledger.check(first.comparison_package is not None, "comparison package")
    package = first.comparison_package
    assert package is not None
    ledger.check(package.finding_count == 13, "package finding count")
    ledger.check(
        package.comparison_dimension_values
        == comparison.COMPARISON_DIMENSION_VALUES,
        "exact ordered dimension registry",
    )
    ledger.check(
        package.comparison_package_id
        == comparison.expected_package_id(package),
        "comparison package deterministic identity",
    )
    ledger.check(
        package.comparison_package_digest
        == comparison.expected_package_digest(package),
        "comparison package deterministic digest",
    )
    ledger.check(
        first.comparison_result_id
        == comparison.expected_result_id(first),
        "comparison result deterministic identity",
    )
    ledger.check(
        first.comparison_result_digest
        == comparison.expected_result_digest(first),
        "comparison result deterministic digest",
    )
    ledger.check(
        comparison.validate_result(first).ok,
        "comparison result validates",
    )

    expected_dimensions = tuple(
        comparison.MeaningPreservationDimension(value)
        for value in comparison.COMPARISON_DIMENSION_VALUES
    )
    ledger.check(
        tuple(item.dimension for item in package.findings)
        == expected_dimensions,
        "one exact finding for each ordered dimension",
    )
    for finding in package.findings:
        ledger.check(
            finding.outcome is comparison.FindingOutcome.PRESERVED,
            f"{finding.dimension.value} preserved",
        )
        ledger.check(
            finding.source_snapshot.values
            == finding.proposed_snapshot.values,
            f"{finding.dimension.value} exact normalized values",
        )
        ledger.check(
            finding.exact_value_equality is True,
            f"{finding.dimension.value} equality recorded",
        )
        ledger.check(
            finding.finding_only is True,
            f"{finding.dimension.value} finding only",
        )
        ledger.check(
            comparison.validate_finding(finding).ok,
            f"{finding.dimension.value} finding validates",
        )

    ledger.check(
        comparison.expected_result_id(first) == first.comparison_result_id,
        "deterministic result identity recomputation",
    )
    ledger.check(
        comparison.expected_package_id(package)
        == package.comparison_package_id,
        "deterministic package identity recomputation",
    )

    dimension = comparison.MeaningPreservationDimension.SCOPE
    source_snapshot = comparison.make_dimension_snapshot(
        dimension=dimension,
        side=comparison.SnapshotSide.SOURCE,
        field_paths=("source.scope",),
        values=("scope:a",),
    )
    preserved_snapshot = comparison.make_dimension_snapshot(
        dimension=dimension,
        side=comparison.SnapshotSide.PROPOSED_EXPRESSION,
        field_paths=("proposed.scope",),
        values=("scope:a",),
    )
    changed_snapshot = comparison.make_dimension_snapshot(
        dimension=dimension,
        side=comparison.SnapshotSide.PROPOSED_EXPRESSION,
        field_paths=("proposed.scope",),
        values=("scope:b",),
    )
    missing_snapshot = comparison.make_dimension_snapshot(
        dimension=dimension,
        side=comparison.SnapshotSide.PROPOSED_EXPRESSION,
        field_paths=("proposed.scope",),
        values=(),
    )
    unsupported_snapshot = comparison.make_dimension_snapshot(
        dimension=dimension,
        side=comparison.SnapshotSide.PROPOSED_EXPRESSION,
        field_paths=("proposed.scope",),
        values=("scope:a",),
        supported=False,
    )
    conflicted_snapshot = comparison.make_dimension_snapshot(
        dimension=dimension,
        side=comparison.SnapshotSide.PROPOSED_EXPRESSION,
        field_paths=("proposed.scope",),
        values=("scope:a",),
        conflict_refs=("conflict:scope",),
    )
    indeterminate_snapshot = comparison.make_dimension_snapshot(
        dimension=dimension,
        side=comparison.SnapshotSide.PROPOSED_EXPRESSION,
        field_paths=("proposed.scope",),
        values=("scope:a",),
        indeterminate_refs=("indeterminate:scope",),
    )

    def outcome(proposed):
        return comparison.build_dimension_finding(
            comparison_request_ref=request.request_id,
            source_admission_result_ref=source_result.admission_result_id,
            validation_input_boundary_ref=(
                package.validation_input_boundary_ref
            ),
            source_snapshot=source_snapshot,
            proposed_snapshot=proposed,
        ).outcome

    ledger.outcome_case(
        outcome(preserved_snapshot) is comparison.FindingOutcome.PRESERVED,
        "explicit preserved outcome",
    )
    ledger.outcome_case(
        outcome(changed_snapshot) is comparison.FindingOutcome.CHANGED,
        "explicit changed outcome",
    )
    ledger.outcome_case(
        outcome(missing_snapshot) is comparison.FindingOutcome.MISSING,
        "explicit missing outcome",
    )
    ledger.outcome_case(
        outcome(unsupported_snapshot)
        is comparison.FindingOutcome.UNSUPPORTED,
        "explicit unsupported outcome",
    )
    ledger.outcome_case(
        outcome(conflicted_snapshot) is comparison.FindingOutcome.CONFLICTED,
        "explicit conflicted outcome",
    )
    ledger.outcome_case(
        outcome(indeterminate_snapshot)
        is comparison.FindingOutcome.INDETERMINATE,
        "explicit indeterminate outcome",
    )

    raw_text_request = replace(request, raw_text="arbitrary raw text")
    raw_text_result = comparison.compare_meaning_preservation(
        raw_text_request,
        source_result,
        source,
    )
    ledger.malformed(
        raw_text_result.status
        is comparison.ComparisonExecutionStatus.HELD_INVALID_REQUEST,
        "raw text held",
    )
    ledger.malformed(
        raw_text_result.comparison_package is None,
        "raw text creates no findings package",
    )

    wrong_ref_request = replace(
        request,
        source_closeout_result_ref="slice42h-result:fabricated",
    )
    wrong_ref_request = replace(
        wrong_ref_request,
        request_id=comparison.expected_record_id(wrong_ref_request),
    )
    wrong_ref_result = comparison.compare_meaning_preservation(
        wrong_ref_request,
        source_result,
        source,
    )
    ledger.malformed(
        wrong_ref_result.status
        is comparison.ComparisonExecutionStatus.HELD_INCONSISTENT_ANCESTRY,
        "mismatched ancestry held",
    )

    unsupported_request = replace(
        request,
        schema_version="aiweb-slice43d-unsupported-v999",
    )
    unsupported_request = replace(
        unsupported_request,
        request_id=comparison.expected_record_id(unsupported_request),
    )
    unsupported_result = comparison.compare_meaning_preservation(
        unsupported_request,
        source_result,
        source,
    )
    ledger.malformed(
        unsupported_result.status
        is comparison.ComparisonExecutionStatus.HELD_UNSUPPORTED_VERSION,
        "unsupported version held",
    )

    fabricated_source_result = replace(
        source_result,
        admission_result_id="slice43c_source_admission_result:fabricated",
    )
    fabricated_result = comparison.compare_meaning_preservation(
        request,
        fabricated_source_result,
        source,
    )
    ledger.malformed(
        fabricated_result.status
        is comparison.ComparisonExecutionStatus.HELD_IDENTITY_INVALID,
        "fabricated Slice 43C identity held",
    )

    try:
        first.status = comparison.ComparisonExecutionStatus.HELD_INVALID_REQUEST
    except FrozenInstanceError:
        immutable = True
    else:
        immutable = False
    ledger.check(immutable, "comparison result immutable")

    authority_zero_fields = (
        "aggregate_pass_rejected_contained_decided",
        "drift_classification_performed",
        "materiality_decided",
        "echo_disposition_decided",
        "rejection_or_containment_issued",
        "expression_rewritten",
        "msm_v1_modified_or_integrated",
        "delivered",
        "downstream_authority_created",
        "model_or_similarity_authority_used",
        "gp014_superseded",
    )
    for field_name in authority_zero_fields:
        ledger.check(
            getattr(first, field_name) is False,
            f"result authority zero: {field_name}",
        )
    package_zero_fields = (
        "aggregate_pass_rejected_contained_decided",
        "drift_classification_performed",
        "materiality_decided",
        "echo_disposition_decided",
        "rejection_or_containment_issued",
        "expression_rewritten",
        "msm_v1_modified_or_integrated",
        "delivery_authorized_or_performed",
        "truth_evidence_permission_execution_authority",
        "route_api_network_filesystem_memory_tool_action_authority",
        "model_or_similarity_authority_used",
        "gp014_superseded",
    )
    for field_name in package_zero_fields:
        ledger.check(
            getattr(package, field_name) is False,
            f"package authority zero: {field_name}",
        )

    print("=== AI.WEB SLICE 43D BEHAVIOR TEST ===")
    print(f"repository={repository}")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print(f"explicit_finding_outcome_cases={ledger.explicit_outcome_cases}")
    print(f"comparison_dimensions={len(comparison.COMPARISON_DIMENSION_VALUES)}")
    print(f"finding_outcomes={len(comparison.FINDING_OUTCOME_VALUES)}")
    print("semantic_content_compared=1")
    print("communicative_purpose_compared=1")
    print("claim_status_compared=1")
    print("scope_compared=1")
    print("certainty_compared=1")
    print("evidence_status_compared=1")
    print("caveats_and_limitations_compared=1")
    print("refusal_state_compared=1")
    print("unresolved_conditions_compared=1")
    print("action_status_compared=1")
    print("memory_status_compared=1")
    print("delivery_status_compared=1")
    print("required_next_step_or_hold_status_compared=1")
    print(f"dimension_findings_created={first.dimension_finding_count}")
    print(f"preserved_findings={first.preserved_finding_count}")
    print(f"changed_findings={first.changed_finding_count}")
    print(f"missing_findings={first.missing_finding_count}")
    print(f"unsupported_findings={first.unsupported_finding_count}")
    print(f"conflicted_findings={first.conflicted_finding_count}")
    print(f"indeterminate_findings={first.indeterminate_finding_count}")
    print("aggregate_pass_rejected_contained_decided=0")
    print("drift_classification_or_materiality=0")
    print("echo_disposition_rejection_containment=0")
    print("expression_repair_or_rewrite=0")
    print("msm_v1_modified_or_integrated=0")
    print("delivery_or_downstream_authority=0")
    print("model_or_similarity_authority=0")
    print("gp014_superseded=0")
    print(f"failure_count={len(ledger.failures)}")
    if ledger.failures:
        for failure in ledger.failures:
            print(f"FAILURE: {failure}")
        print("AI.WEB SLICE 43D BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 43D BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
