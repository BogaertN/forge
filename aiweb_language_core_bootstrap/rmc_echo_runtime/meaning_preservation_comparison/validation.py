"""Fail-closed Slice 43D comparison validation."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
import re
from typing import Any

from ...outward_expression_runtime.disabled_outward_expression_closeout import (
    DisabledOutwardExpressionCloseoutResult,
)
from ..authorized_source_admission import (
    SourceAdmissionResult,
    SourceAdmissionStatus,
    validate_exact_source,
    validate_result as validate_source_admission_result,
)
from .authority import (
    COMPARISON_DIMENSION_VALUES,
    DIGEST_ALGORITHM,
    EXACT_ACCEPTED_SLICE43C_ID_MAP,
    REQUESTED_OPERATION,
    SLICE43D_PROFILE_VERSION,
    SLICE43D_SCHEMA_VERSION,
)
from .identity import (
    expected_package_digest,
    expected_package_id,
    expected_record_id,
    expected_result_digest,
    expected_result_id,
    expected_snapshot_value_digest,
)
from .rules import outcome_for_snapshots, source_objects
from .schema import (
    ComparisonCode,
    ComparisonExecutionStatus,
    ComparisonIssue,
    ComparisonValidationReport,
    DimensionValueSnapshot,
    FindingOutcome,
    MeaningPreservationComparisonPackage,
    MeaningPreservationComparisonRequest,
    MeaningPreservationComparisonResult,
    MeaningPreservationDimension,
    MeaningPreservationFinding,
    SnapshotSide,
)


_IDENTIFIER_RE = re.compile(r"^[a-zA-Z0-9_.-]+:[^\s]+$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _issue(
    path: str,
    code: ComparisonCode,
    detail: str,
) -> ComparisonIssue:
    return ComparisonIssue(path=path, code=code, detail=detail)


def _report(
    issues: list[ComparisonIssue] | tuple[ComparisonIssue, ...],
) -> ComparisonValidationReport:
    unique: list[ComparisonIssue] = []
    seen: set[tuple[str, str, str]] = set()
    for item in issues:
        key = (item.path, item.code.value, item.detail)
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return ComparisonValidationReport(tuple(unique))


def _valid_text(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.strip() == value
        and "\x00" not in value
    )


def _valid_identifier(value: object) -> bool:
    return _valid_text(value) and _IDENTIFIER_RE.fullmatch(value) is not None


def _valid_string_tuple(
    value: object,
    *,
    allow_empty: bool = True,
) -> bool:
    if type(value) is not tuple:
        return False
    if not allow_empty and not value:
        return False
    if not all(_valid_text(item) for item in value):
        return False
    return len(value) == len(set(value))


def _authority_zero_issues(
    record: object,
    *,
    path: str,
) -> list[ComparisonIssue]:
    issues: list[ComparisonIssue] = []
    prohibited_true_fields = (
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
        "delivered",
        "downstream_authority_created",
        "drift_classified",
    )
    for field_name in prohibited_true_fields:
        if hasattr(record, field_name) and getattr(record, field_name) is not False:
            issues.append(_issue(
                f"{path}.{field_name}",
                ComparisonCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
                "field must remain exact false in Slice 43D",
            ))
    return issues


def validate_comparison_inputs(
    request: object,
    source_admission_result: object,
    source_closeout_result: object,
) -> ComparisonValidationReport:
    issues: list[ComparisonIssue] = []

    if type(request) is not MeaningPreservationComparisonRequest:
        return _report([
            _issue(
                "request",
                ComparisonCode.REQUEST_TYPE_INVALID,
                "exact MeaningPreservationComparisonRequest required",
            )
        ])
    if request.request_id != expected_record_id(request):
        issues.append(_issue(
            "request.request_id",
            ComparisonCode.REQUEST_ID_INVALID,
            "request identity does not match canonical content",
        ))
    if request.requested_operation != REQUESTED_OPERATION:
        issues.append(_issue(
            "request.requested_operation",
            ComparisonCode.REQUEST_OPERATION_INVALID,
            f"expected {REQUESTED_OPERATION!r}",
        ))
    if request.raw_text is not None:
        issues.append(_issue(
            "request.raw_text",
            ComparisonCode.RAW_TEXT_PROHIBITED,
            "comparison consumes admitted typed custody only",
        ))
    if request.explicit_comparison_request is not True:
        issues.append(_issue(
            "request.explicit_comparison_request",
            ComparisonCode.EXPLICIT_REQUEST_REQUIRED,
            "explicit comparison request is required",
        ))
    if (
        request.schema_version != SLICE43D_SCHEMA_VERSION
        or request.profile_version != SLICE43D_PROFILE_VERSION
    ):
        issues.append(_issue(
            "request.version",
            ComparisonCode.UNSUPPORTED_VERSION,
            "unsupported Slice 43D request version",
        ))

    # Fail closed before traversing the accepted Slice 42 ancestry when the
    # lightweight request envelope is already invalid. This prevents malformed
    # requests from triggering expensive predecessor validation.
    if issues:
        return _report(issues)

    if type(source_admission_result) is not SourceAdmissionResult:
        issues.append(_issue(
            "source_admission_result",
            ComparisonCode.SOURCE_ADMISSION_RESULT_TYPE_INVALID,
            "exact Slice 43C SourceAdmissionResult required",
        ))
    else:
        if (
            source_admission_result.admission_result_id
            != EXACT_ACCEPTED_SLICE43C_ID_MAP["result"]
        ):
            return _report([
                _issue(
                    "source_admission_result.admission_result_id",
                    ComparisonCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
                    "result is not the exact accepted Slice 43C identity",
                )
            ])
        predecessor_report = validate_source_admission_result(
            source_admission_result
        )
        if not predecessor_report.ok:
            issues.append(_issue(
                "source_admission_result",
                ComparisonCode.SOURCE_NOT_ADMITTED,
                "Slice 43C result failed its accepted validator",
            ))
        if source_admission_result.status is not SourceAdmissionStatus.ADMITTED:
            issues.append(_issue(
                "source_admission_result.status",
                ComparisonCode.SOURCE_NOT_ADMITTED,
                "exact admitted Slice 43C result required",
            ))
        package = source_admission_result.admission_package
        if package is None:
            issues.append(_issue(
                "source_admission_result.admission_package",
                ComparisonCode.MISSING_REQUIRED_VALUE,
                "admitted comparison source package is required",
            ))
        else:
            exact_checks = (
                (
                    "source_admission_result.admission_package.admission_package_id",
                    package.admission_package_id,
                    "package",
                ),
                (
                    "source_admission_result.admission_package."
                    "authorized_meaning_admission.admission_record_id",
                    package.authorized_meaning_admission.admission_record_id,
                    "authorized_meaning_admission",
                ),
                (
                    "source_admission_result.admission_package."
                    "proposed_expression_admission.admission_record_id",
                    package.proposed_expression_admission.admission_record_id,
                    "proposed_expression_admission",
                ),
                (
                    "source_admission_result.admission_package."
                    "validation_input_boundary.validation_input_boundary_id",
                    package.validation_input_boundary.validation_input_boundary_id,
                    "validation_input_boundary",
                ),
            )
            for path, observed, key in exact_checks:
                if observed != EXACT_ACCEPTED_SLICE43C_ID_MAP[key]:
                    issues.append(_issue(
                        path,
                        ComparisonCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
                        "not the exact accepted Slice 43C identity",
                    ))
            if package.admitted_for_slice43d_comparison is not True:
                issues.append(_issue(
                    "source_admission_result.admission_package."
                    "admitted_for_slice43d_comparison",
                    ComparisonCode.SOURCE_NOT_ADMITTED,
                    "Slice 43C did not admit this source for comparison",
                ))

    if type(source_closeout_result) is not DisabledOutwardExpressionCloseoutResult:
        issues.append(_issue(
            "source_closeout_result",
            ComparisonCode.SOURCE_CLOSEOUT_TYPE_INVALID,
            "exact accepted Slice 42H closeout result required",
        ))
    else:
        source_report = validate_exact_source(source_closeout_result)
        if not source_report.ok:
            issues.append(_issue(
                "source_closeout_result",
                ComparisonCode.SOURCE_ANCESTRY_INVALID,
                "Slice 42 ancestry failed exact Slice 43C source validation",
            ))
        try:
            objects = source_objects(source_closeout_result)
        except (AttributeError, TypeError, AssertionError) as error:
            issues.append(_issue(
                "source_closeout_result",
                ComparisonCode.MISSING_REQUIRED_VALUE,
                f"required nested source record missing: {error}",
            ))
        else:
            required = (
                "selected_record",
                "candidate",
                "outward",
                "expression_link",
                "obligation_package",
                "expression_plan",
            )
            for name in required:
                if objects.get(name) is None:
                    issues.append(_issue(
                        f"source_closeout_result.{name}",
                        ComparisonCode.MISSING_REQUIRED_VALUE,
                        "required comparison predecessor missing",
                    ))

    if (
        type(source_admission_result) is SourceAdmissionResult
        and type(source_closeout_result)
        is DisabledOutwardExpressionCloseoutResult
    ):
        if (
            request.source_admission_result_ref
            != source_admission_result.admission_result_id
        ):
            issues.append(_issue(
                "request.source_admission_result_ref",
                ComparisonCode.INCONSISTENT_ANCESTRY,
                "request does not bind the supplied admission result",
            ))
        if (
            request.source_closeout_result_ref
            != source_closeout_result.result_id
        ):
            issues.append(_issue(
                "request.source_closeout_result_ref",
                ComparisonCode.INCONSISTENT_ANCESTRY,
                "request does not bind the supplied closeout result",
            ))
        if (
            source_admission_result.source_closeout_result_ref
            != source_closeout_result.result_id
        ):
            issues.append(_issue(
                "source_admission_result.source_closeout_result_ref",
                ComparisonCode.INCONSISTENT_ANCESTRY,
                "Slice 43C result and Slice 42 source do not match",
            ))
        package = source_admission_result.admission_package
        if (
            package is not None
            and package.source_closeout_result_ref
            != source_closeout_result.result_id
        ):
            issues.append(_issue(
                "source_admission_result.admission_package."
                "source_closeout_result_ref",
                ComparisonCode.INCONSISTENT_ANCESTRY,
                "admission package and Slice 42 source do not match",
            ))

    return _report(issues)


def validate_snapshot(
    snapshot: object,
) -> ComparisonValidationReport:
    issues: list[ComparisonIssue] = []
    if type(snapshot) is not DimensionValueSnapshot:
        return _report([
            _issue(
                "snapshot",
                ComparisonCode.SNAPSHOT_INVALID,
                "exact DimensionValueSnapshot required",
            )
        ])
    if snapshot.snapshot_id != expected_record_id(snapshot):
        issues.append(_issue(
            "snapshot.snapshot_id",
            ComparisonCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "snapshot identity mismatch",
        ))
    if (
        not _SHA256_RE.fullmatch(snapshot.value_digest)
        or snapshot.value_digest != expected_snapshot_value_digest(snapshot)
    ):
        issues.append(_issue(
            "snapshot.value_digest",
            ComparisonCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "snapshot value digest mismatch",
        ))
    if type(snapshot.dimension) is not MeaningPreservationDimension:
        issues.append(_issue(
            "snapshot.dimension",
            ComparisonCode.DIMENSION_INVALID,
            "exact comparison dimension required",
        ))
    if type(snapshot.side) is not SnapshotSide:
        issues.append(_issue(
            "snapshot.side",
            ComparisonCode.SNAPSHOT_INVALID,
            "exact snapshot side required",
        ))
    for field_name, value, allow_empty in (
        ("field_paths", snapshot.field_paths, True),
        ("values", snapshot.values, True),
        ("evidence_refs", snapshot.evidence_refs, True),
        ("trace_refs", snapshot.trace_refs, True),
        ("conflict_refs", snapshot.conflict_refs, True),
        ("indeterminate_refs", snapshot.indeterminate_refs, True),
    ):
        if not _valid_string_tuple(value, allow_empty=allow_empty):
            issues.append(_issue(
                f"snapshot.{field_name}",
                ComparisonCode.SNAPSHOT_INVALID,
                "exact duplicate-free tuple of normalized strings required",
            ))
    if type(snapshot.supported) is not bool:
        issues.append(_issue(
            "snapshot.supported",
            ComparisonCode.SNAPSHOT_INVALID,
            "supported must be exact bool",
        ))
    if snapshot.conflict_refs and snapshot.indeterminate_refs:
        issues.append(_issue(
            "snapshot",
            ComparisonCode.SNAPSHOT_INVALID,
            "conflicted and indeterminate custody may not be conflated",
        ))
    if (
        snapshot.schema_version != SLICE43D_SCHEMA_VERSION
        or snapshot.profile_version != SLICE43D_PROFILE_VERSION
        or snapshot.digest_algorithm != DIGEST_ALGORITHM
    ):
        issues.append(_issue(
            "snapshot.version",
            ComparisonCode.UNSUPPORTED_VERSION,
            "unsupported snapshot version",
        ))
    return _report(issues)


def validate_finding(
    finding: object,
) -> ComparisonValidationReport:
    issues: list[ComparisonIssue] = []
    if type(finding) is not MeaningPreservationFinding:
        return _report([
            _issue(
                "finding",
                ComparisonCode.FINDING_INVALID,
                "exact MeaningPreservationFinding required",
            )
        ])
    if finding.finding_id != expected_record_id(finding):
        issues.append(_issue(
            "finding.finding_id",
            ComparisonCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "finding identity mismatch",
        ))
    source_report = validate_snapshot(finding.source_snapshot)
    proposed_report = validate_snapshot(finding.proposed_snapshot)
    issues.extend(source_report.issues)
    issues.extend(proposed_report.issues)
    if (
        finding.source_snapshot.side is not SnapshotSide.SOURCE
        or finding.proposed_snapshot.side
        is not SnapshotSide.PROPOSED_EXPRESSION
    ):
        issues.append(_issue(
            "finding.snapshots",
            ComparisonCode.FINDING_INVALID,
            "source and proposed snapshot sides are required",
        ))
    if (
        finding.dimension is not finding.source_snapshot.dimension
        or finding.dimension is not finding.proposed_snapshot.dimension
    ):
        issues.append(_issue(
            "finding.dimension",
            ComparisonCode.FINDING_INVALID,
            "finding and snapshot dimensions must match exactly",
        ))
    expected_outcome = outcome_for_snapshots(
        finding.source_snapshot,
        finding.proposed_snapshot,
    )
    if finding.outcome is not expected_outcome:
        issues.append(_issue(
            "finding.outcome",
            ComparisonCode.FINDING_INVALID,
            "finding outcome does not follow deterministic comparison law",
        ))
    if finding.exact_value_equality is not (
        bool(finding.source_snapshot.values)
        and finding.source_snapshot.values
        == finding.proposed_snapshot.values
    ):
        issues.append(_issue(
            "finding.exact_value_equality",
            ComparisonCode.FINDING_INVALID,
            "exact equality flag mismatch",
        ))
    if finding.required_value_missing is not (
        not finding.source_snapshot.values
        or not finding.proposed_snapshot.values
    ):
        issues.append(_issue(
            "finding.required_value_missing",
            ComparisonCode.FINDING_INVALID,
            "missing-value flag mismatch",
        ))
    if finding.finding_only is not True:
        issues.append(_issue(
            "finding.finding_only",
            ComparisonCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
            "Slice 43D records findings only",
        ))
    issues.extend(_authority_zero_issues(finding, path="finding"))
    if (
        finding.schema_version != SLICE43D_SCHEMA_VERSION
        or finding.profile_version != SLICE43D_PROFILE_VERSION
    ):
        issues.append(_issue(
            "finding.version",
            ComparisonCode.UNSUPPORTED_VERSION,
            "unsupported finding version",
        ))
    return _report(issues)


def validate_package(
    package: object,
) -> ComparisonValidationReport:
    issues: list[ComparisonIssue] = []
    if type(package) is not MeaningPreservationComparisonPackage:
        return _report([
            _issue(
                "package",
                ComparisonCode.PACKAGE_INVALID,
                "exact comparison package required",
            )
        ])
    if (
        package.comparison_package_id != expected_package_id(package)
        or package.comparison_package_digest != expected_package_digest(package)
    ):
        issues.append(_issue(
            "package.identity",
            ComparisonCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "comparison package identity mismatch",
        ))
    if package.source_admission_result_ref != EXACT_ACCEPTED_SLICE43C_ID_MAP["result"]:
        issues.append(_issue(
            "package.source_admission_result_ref",
            ComparisonCode.INCONSISTENT_ANCESTRY,
            "package must bind the exact accepted Slice 43C result",
        ))
    if package.source_admission_package_ref != EXACT_ACCEPTED_SLICE43C_ID_MAP["package"]:
        issues.append(_issue(
            "package.source_admission_package_ref",
            ComparisonCode.INCONSISTENT_ANCESTRY,
            "package must bind the exact accepted Slice 43C package",
        ))
    if (
        package.validation_input_boundary_ref
        != EXACT_ACCEPTED_SLICE43C_ID_MAP["validation_input_boundary"]
    ):
        issues.append(_issue(
            "package.validation_input_boundary_ref",
            ComparisonCode.INCONSISTENT_ANCESTRY,
            "package must bind the exact admitted input boundary",
        ))
    expected_dimensions = tuple(
        MeaningPreservationDimension(value)
        for value in COMPARISON_DIMENSION_VALUES
    )
    observed_dimensions = tuple(item.dimension for item in package.findings)
    if (
        package.finding_count != len(COMPARISON_DIMENSION_VALUES)
        or len(package.findings) != len(COMPARISON_DIMENSION_VALUES)
        or package.comparison_dimension_values != COMPARISON_DIMENSION_VALUES
        or observed_dimensions != expected_dimensions
        or len(set(observed_dimensions)) != len(observed_dimensions)
    ):
        issues.append(_issue(
            "package.findings",
            ComparisonCode.PACKAGE_INVALID,
            "exact ordered 13-dimension finding set required",
        ))
    for index, finding in enumerate(package.findings):
        report = validate_finding(finding)
        for item in report.issues:
            issues.append(_issue(
                f"package.findings[{index}].{item.path}",
                item.code,
                item.detail,
            ))
    if package.comparison_performed is not True or package.findings_created is not True:
        issues.append(_issue(
            "package.comparison",
            ComparisonCode.PACKAGE_INVALID,
            "comparison and finding creation must be recorded",
        ))
    issues.extend(_authority_zero_issues(package, path="package"))
    if (
        package.schema_version != SLICE43D_SCHEMA_VERSION
        or package.profile_version != SLICE43D_PROFILE_VERSION
        or package.digest_algorithm != DIGEST_ALGORITHM
    ):
        issues.append(_issue(
            "package.version",
            ComparisonCode.UNSUPPORTED_VERSION,
            "unsupported comparison package version",
        ))
    return _report(issues)


def validate_result(
    result: object,
) -> ComparisonValidationReport:
    issues: list[ComparisonIssue] = []
    if type(result) is not MeaningPreservationComparisonResult:
        return _report([
            _issue(
                "result",
                ComparisonCode.RESULT_INVALID,
                "exact comparison result required",
            )
        ])
    if (
        result.comparison_result_id != expected_result_id(result)
        or result.comparison_result_digest != expected_result_digest(result)
    ):
        issues.append(_issue(
            "result.identity",
            ComparisonCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "comparison result identity mismatch",
        ))
    if result.status is ComparisonExecutionStatus.FINDINGS_CREATED:
        if result.comparison_package is None:
            issues.append(_issue(
                "result.comparison_package",
                ComparisonCode.RESULT_INVALID,
                "findings-created result requires comparison package",
            ))
        else:
            report = validate_package(result.comparison_package)
            issues.extend(report.issues)
            findings = result.comparison_package.findings
            counts = {
                outcome: sum(item.outcome is outcome for item in findings)
                for outcome in FindingOutcome
            }
            expected_counts = (
                len(findings),
                counts[FindingOutcome.PRESERVED],
                counts[FindingOutcome.CHANGED],
                counts[FindingOutcome.MISSING],
                counts[FindingOutcome.UNSUPPORTED],
                counts[FindingOutcome.CONFLICTED],
                counts[FindingOutcome.INDETERMINATE],
            )
            observed_counts = (
                result.dimension_finding_count,
                result.preserved_finding_count,
                result.changed_finding_count,
                result.missing_finding_count,
                result.unsupported_finding_count,
                result.conflicted_finding_count,
                result.indeterminate_finding_count,
            )
            if observed_counts != expected_counts:
                issues.append(_issue(
                    "result.finding_counts",
                    ComparisonCode.RESULT_INVALID,
                    "finding counts do not match exact findings",
                ))
        if (
            result.issue_codes
            or result.comparison_performed is not True
            or result.findings_created is not True
        ):
            issues.append(_issue(
                "result.status",
                ComparisonCode.RESULT_INVALID,
                "findings-created result carries invalid operational state",
            ))
    else:
        if (
            result.comparison_package is not None
            or result.comparison_performed
            or result.findings_created
            or result.dimension_finding_count
            or result.preserved_finding_count
            or result.changed_finding_count
            or result.missing_finding_count
            or result.unsupported_finding_count
            or result.conflicted_finding_count
            or result.indeterminate_finding_count
        ):
            issues.append(_issue(
                "result.held_state",
                ComparisonCode.RESULT_INVALID,
                "held result may not claim comparison findings",
            ))
    issues.extend(_authority_zero_issues(result, path="result"))
    if (
        result.schema_version != SLICE43D_SCHEMA_VERSION
        or result.profile_version != SLICE43D_PROFILE_VERSION
        or result.digest_algorithm != DIGEST_ALGORITHM
    ):
        issues.append(_issue(
            "result.version",
            ComparisonCode.UNSUPPORTED_VERSION,
            "unsupported comparison result version",
        ))
    return _report(issues)


__all__ = (
    "validate_comparison_inputs",
    "validate_finding",
    "validate_package",
    "validate_result",
    "validate_snapshot",
)
