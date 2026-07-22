"""Strict deterministic validation for Slice 43E classification records."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
import re
from typing import Any

from ..meaning_preservation_comparison import (
    ComparisonExecutionStatus,
    FindingOutcome,
    MeaningPreservationComparisonResult,
    expected_package_digest as expected_comparison_package_digest,
    expected_package_id as expected_comparison_package_id,
    expected_record_id as expected_comparison_record_id,
    expected_result_digest as expected_comparison_result_digest,
    expected_result_id as expected_comparison_result_id,
    validate_result as validate_comparison_result,
)
from .authority import (
    CLASSIFICATION_RULE_REF_MAP,
    CLASSIFICATION_STATE_VALUES,
    DRIFT_KIND_VALUES,
    MATERIALITY_RULE_REF_MAP,
    MATERIALITY_VALUES,
    REQUESTED_OPERATION,
    SLICE43E_PROFILE_VERSION,
    SLICE43E_SCHEMA_VERSION,
)
from .identity import (
    expected_package_digest,
    expected_package_id,
    expected_record_id,
    expected_result_digest,
    expected_result_id,
)
from .schema import (
    DriftClassificationCode,
    DriftClassificationExecutionStatus,
    DriftClassificationIssue,
    DriftClassificationPackage,
    DriftClassificationRequest,
    DriftClassificationResult,
    DriftClassificationState,
    DriftClassificationValidationReport,
    DriftKind,
    DriftMaterialityFinding,
    MaterialityState,
)


_IDENTIFIER_RE = re.compile(r"^[a-z0-9][a-z0-9._:/-]*$")


def _issue(
    path: str,
    code: DriftClassificationCode,
    detail: str,
) -> DriftClassificationIssue:
    return DriftClassificationIssue(path=path, code=code, detail=detail)


def _report(
    issues: list[DriftClassificationIssue],
) -> DriftClassificationValidationReport:
    return DriftClassificationValidationReport(issues=tuple(issues))


def _valid_text(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.strip() == value
        and "\x00" not in value
    )


def _valid_identifier(value: object) -> bool:
    return _valid_text(value) and bool(_IDENTIFIER_RE.fullmatch(value))


def _valid_string_tuple(
    value: object,
    *,
    allow_empty: bool = True,
) -> bool:
    if type(value) is not tuple:
        return False
    if not allow_empty and not value:
        return False
    return (
        all(_valid_text(item) for item in value)
        and len(set(value)) == len(value)
    )


def _authority_zero_issues(
    record: object,
    prefix: str,
) -> list[DriftClassificationIssue]:
    issues: list[DriftClassificationIssue] = []
    zero_fields = (
        "aggregate_pass_rejected_contained_decided",
        "echo_disposition_decided",
        "rejection_or_containment_issued",
        "text_repaired_or_rewritten",
        "msm_v1_modified_or_integrated",
        "delivery_authorized_or_performed",
        "truth_evidence_permission_execution_authority",
        "route_api_network_filesystem_memory_tool_action_authority",
        "delivered",
        "downstream_authority_created",
        "model_or_similarity_authority_used",
        "gp014_superseded",
    )
    for field_name in zero_fields:
        if hasattr(record, field_name) and getattr(record, field_name) is not False:
            issues.append(_issue(
                f"{prefix}.{field_name}",
                DriftClassificationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
                "field must remain false in Slice 43E",
            ))
    return issues


def validate_classification_inputs(
    request: DriftClassificationRequest,
    comparison_result: MeaningPreservationComparisonResult,
) -> DriftClassificationValidationReport:
    issues: list[DriftClassificationIssue] = []

    if type(request) is not DriftClassificationRequest:
        return _report([_issue(
            "request",
            DriftClassificationCode.REQUEST_TYPE_INVALID,
            "exact DriftClassificationRequest required",
        )])

    if not _valid_identifier(request.request_id):
        issues.append(_issue(
            "request.request_id",
            DriftClassificationCode.REQUEST_ID_INVALID,
            "deterministic request identifier required",
        ))
    elif request.request_id != expected_record_id(request):
        issues.append(_issue(
            "request.request_id",
            DriftClassificationCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "request identifier does not match canonical record bytes",
        ))

    if request.requested_operation != REQUESTED_OPERATION:
        issues.append(_issue(
            "request.requested_operation",
            DriftClassificationCode.REQUEST_OPERATION_INVALID,
            "exact Slice 43E operation required",
        ))
    if request.raw_text is not None:
        issues.append(_issue(
            "request.raw_text",
            DriftClassificationCode.RAW_TEXT_PROHIBITED,
            "raw text is not a Slice 43E classification input",
        ))
    if request.explicit_classification_request is not True:
        issues.append(_issue(
            "request.explicit_classification_request",
            DriftClassificationCode.EXPLICIT_REQUEST_REQUIRED,
            "explicit classification request required",
        ))
    if (
        request.schema_version != SLICE43E_SCHEMA_VERSION
        or request.profile_version != SLICE43E_PROFILE_VERSION
    ):
        issues.append(_issue(
            "request.version",
            DriftClassificationCode.UNSUPPORTED_VERSION,
            "unsupported Slice 43E schema or profile version",
        ))

    if type(comparison_result) is not MeaningPreservationComparisonResult:
        issues.append(_issue(
            "comparison_result",
            DriftClassificationCode.COMPARISON_RESULT_TYPE_INVALID,
            "exact Slice 43D comparison result required",
        ))
        return _report(issues)

    comparison_report = validate_comparison_result(comparison_result)
    if not comparison_report.ok:
        issues.append(_issue(
            "comparison_result",
            DriftClassificationCode.COMPARISON_RESULT_INVALID,
            "Slice 43D result failed its own deterministic validation",
        ))

    package = comparison_result.comparison_package
    if (
        comparison_result.status is not ComparisonExecutionStatus.FINDINGS_CREATED
        or comparison_result.comparison_performed is not True
        or comparison_result.findings_created is not True
    ):
        issues.append(_issue(
            "comparison_result.status",
            DriftClassificationCode.COMPARISON_NOT_READY,
            "Slice 43D findings-created result required",
        ))
    if package is None:
        issues.append(_issue(
            "comparison_result.comparison_package",
            DriftClassificationCode.COMPARISON_PACKAGE_MISSING,
            "comparison package required",
        ))
        return _report(issues)

    if comparison_result.comparison_result_id != expected_comparison_result_id(
        comparison_result
    ) or comparison_result.comparison_result_digest != expected_comparison_result_digest(
        comparison_result
    ):
        issues.append(_issue(
            "comparison_result.identity",
            DriftClassificationCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "Slice 43D result identity mismatch",
        ))
    if package.comparison_package_id != expected_comparison_package_id(
        package
    ) or package.comparison_package_digest != expected_comparison_package_digest(
        package
    ):
        issues.append(_issue(
            "comparison_result.comparison_package.identity",
            DriftClassificationCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "Slice 43D package identity mismatch",
        ))

    for index, finding in enumerate(package.findings):
        if finding.finding_id != expected_comparison_record_id(finding):
            issues.append(_issue(
                f"comparison_result.comparison_package.findings[{index}]",
                DriftClassificationCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
                "Slice 43D finding identity mismatch",
            ))

    if request.comparison_result_ref != comparison_result.comparison_result_id:
        issues.append(_issue(
            "request.comparison_result_ref",
            DriftClassificationCode.INCONSISTENT_ANCESTRY,
            "request must reference the exact supplied Slice 43D result",
        ))
    if request.comparison_package_ref != package.comparison_package_id:
        issues.append(_issue(
            "request.comparison_package_ref",
            DriftClassificationCode.INCONSISTENT_ANCESTRY,
            "request must reference the exact supplied Slice 43D package",
        ))
    if comparison_result.comparison_request_ref != package.comparison_request_ref:
        issues.append(_issue(
            "comparison_result.comparison_request_ref",
            DriftClassificationCode.INCONSISTENT_ANCESTRY,
            "comparison request custody mismatch",
        ))
    if comparison_result.source_admission_result_ref != package.source_admission_result_ref:
        issues.append(_issue(
            "comparison_result.source_admission_result_ref",
            DriftClassificationCode.INCONSISTENT_ANCESTRY,
            "source admission custody mismatch",
        ))
    if comparison_result.source_closeout_result_ref != package.source_closeout_result_ref:
        issues.append(_issue(
            "comparison_result.source_closeout_result_ref",
            DriftClassificationCode.INCONSISTENT_ANCESTRY,
            "source closeout custody mismatch",
        ))

    return _report(issues)


def validate_finding(
    finding: DriftMaterialityFinding,
    comparison_finding: object | None = None,
) -> DriftClassificationValidationReport:
    issues: list[DriftClassificationIssue] = []
    if type(finding) is not DriftMaterialityFinding:
        return _report([_issue(
            "finding",
            DriftClassificationCode.CLASSIFICATION_INVALID,
            "exact DriftMaterialityFinding required",
        )])

    if finding.drift_finding_id != expected_record_id(finding):
        issues.append(_issue(
            "finding.drift_finding_id",
            DriftClassificationCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "finding identifier mismatch",
        ))

    for name in (
        "classification_request_ref",
        "comparison_result_ref",
        "comparison_package_ref",
        "comparison_finding_ref",
        "source_snapshot_ref",
        "proposed_snapshot_ref",
        "materiality_rule_ref",
    ):
        if not _valid_identifier(getattr(finding, name)):
            issues.append(_issue(
                f"finding.{name}",
                DriftClassificationCode.MISSING_REQUIRED_VALUE,
                "valid identifier required",
            ))

    if type(finding.drift_kinds) is not tuple:
        issues.append(_issue(
            "finding.drift_kinds",
            DriftClassificationCode.DRIFT_KIND_INVALID,
            "exact tuple required",
        ))
    else:
        values = tuple(item.value for item in finding.drift_kinds)
        if (
            any(type(item) is not DriftKind for item in finding.drift_kinds)
            or len(values) != len(set(values))
            or tuple(value for value in DRIFT_KIND_VALUES if value in set(values))
            != values
        ):
            issues.append(_issue(
                "finding.drift_kinds",
                DriftClassificationCode.DRIFT_KIND_INVALID,
                "drift kinds must be unique and registry ordered",
            ))

    if finding.classification_state.value not in CLASSIFICATION_STATE_VALUES:
        issues.append(_issue(
            "finding.classification_state",
            DriftClassificationCode.CLASSIFICATION_INVALID,
            "unsupported classification state",
        ))
    if finding.materiality.value not in MATERIALITY_VALUES:
        issues.append(_issue(
            "finding.materiality",
            DriftClassificationCode.MATERIALITY_INVALID,
            "unsupported materiality state",
        ))

    if not _valid_string_tuple(finding.source_values):
        issues.append(_issue(
            "finding.source_values",
            DriftClassificationCode.CLASSIFICATION_INVALID,
            "source values must be a unique string tuple",
        ))
    if not _valid_string_tuple(finding.proposed_values):
        issues.append(_issue(
            "finding.proposed_values",
            DriftClassificationCode.CLASSIFICATION_INVALID,
            "proposed values must be a unique string tuple",
        ))
    for name in (
        "source_field_paths",
        "proposed_field_paths",
        "comparison_evidence_refs",
        "comparison_trace_refs",
        "classification_rule_refs",
        "materiality_ground_refs",
        "ancestry_mismatch_refs",
    ):
        if not _valid_string_tuple(getattr(finding, name)):
            issues.append(_issue(
                f"finding.{name}",
                DriftClassificationCode.CLASSIFICATION_INVALID,
                "unique string tuple required",
            ))

    expected_rules = tuple(
        CLASSIFICATION_RULE_REF_MAP[item.value] for item in finding.drift_kinds
    )
    if finding.classification_rule_refs != expected_rules:
        issues.append(_issue(
            "finding.classification_rule_refs",
            DriftClassificationCode.CLASSIFICATION_INVALID,
            "classification rule refs must exactly match drift kinds",
        ))
    if finding.materiality_rule_ref != MATERIALITY_RULE_REF_MAP[
        finding.materiality.value
    ]:
        issues.append(_issue(
            "finding.materiality_rule_ref",
            DriftClassificationCode.MATERIALITY_INVALID,
            "materiality rule ref mismatch",
        ))

    state = finding.classification_state
    if state is DriftClassificationState.NO_DRIFT:
        if (
            finding.comparison_outcome is not FindingOutcome.PRESERVED
            or finding.drift_kinds
            or finding.materiality is not MaterialityState.NOT_APPLICABLE
        ):
            issues.append(_issue(
                "finding.classification_state",
                DriftClassificationCode.CLASSIFICATION_INVALID,
                "no-drift record must be preserved and not applicable",
            ))
    elif state is DriftClassificationState.CLASSIFICATION_UNSUPPORTED:
        if (
            finding.comparison_outcome is not FindingOutcome.UNSUPPORTED
            or finding.drift_kinds
            or finding.materiality is not MaterialityState.UNSUPPORTED
        ):
            issues.append(_issue(
                "finding.classification_state",
                DriftClassificationCode.CLASSIFICATION_INVALID,
                "unsupported record mismatch",
            ))
    elif state is DriftClassificationState.CLASSIFICATION_CONFLICTED:
        if (
            finding.comparison_outcome is not FindingOutcome.CONFLICTED
            or finding.drift_kinds
            or finding.materiality is not MaterialityState.CONFLICTED
        ):
            issues.append(_issue(
                "finding.classification_state",
                DriftClassificationCode.CLASSIFICATION_INVALID,
                "conflicted record mismatch",
            ))
    elif state is DriftClassificationState.CLASSIFICATION_INDETERMINATE:
        if finding.materiality is not MaterialityState.INDETERMINATE:
            issues.append(_issue(
                "finding.classification_state",
                DriftClassificationCode.CLASSIFICATION_INVALID,
                "indeterminate state requires indeterminate materiality",
            ))
    elif state is DriftClassificationState.DRIFT_CLASSIFIED:
        if not finding.drift_kinds:
            issues.append(_issue(
                "finding.drift_kinds",
                DriftClassificationCode.DRIFT_KIND_INVALID,
                "classified drift requires at least one admitted kind",
            ))
        if finding.materiality not in (
            MaterialityState.NON_MATERIAL,
            MaterialityState.MATERIAL,
            MaterialityState.INDETERMINATE,
        ):
            issues.append(_issue(
                "finding.materiality",
                DriftClassificationCode.MATERIALITY_INVALID,
                "classified drift materiality mismatch",
            ))

    if (
        finding.finding_only is not True
        or finding.schema_version != SLICE43E_SCHEMA_VERSION
        or finding.profile_version != SLICE43E_PROFILE_VERSION
    ):
        issues.append(_issue(
            "finding.boundary",
            DriftClassificationCode.CLASSIFICATION_INVALID,
            "finding-only and supported version boundary required",
        ))
    issues.extend(_authority_zero_issues(finding, "finding"))

    if comparison_finding is not None:
        expected_pairs = (
            ("comparison_finding_ref", "finding_id"),
            ("dimension", "dimension"),
            ("comparison_outcome", "outcome"),
            ("source_snapshot_ref", "source_snapshot.snapshot_id"),
            ("proposed_snapshot_ref", "proposed_snapshot.snapshot_id"),
            ("source_values", "source_snapshot.values"),
            ("proposed_values", "proposed_snapshot.values"),
            ("source_field_paths", "source_snapshot.field_paths"),
            ("proposed_field_paths", "proposed_snapshot.field_paths"),
            ("comparison_evidence_refs", "evidence_refs"),
            ("comparison_trace_refs", "trace_refs"),
        )
        observed = {
            "comparison_finding_ref": comparison_finding.finding_id,
            "dimension": comparison_finding.dimension,
            "comparison_outcome": comparison_finding.outcome,
            "source_snapshot_ref": comparison_finding.source_snapshot.snapshot_id,
            "proposed_snapshot_ref": comparison_finding.proposed_snapshot.snapshot_id,
            "source_values": comparison_finding.source_snapshot.values,
            "proposed_values": comparison_finding.proposed_snapshot.values,
            "source_field_paths": comparison_finding.source_snapshot.field_paths,
            "proposed_field_paths": comparison_finding.proposed_snapshot.field_paths,
            "comparison_evidence_refs": comparison_finding.evidence_refs,
            "comparison_trace_refs": comparison_finding.trace_refs,
        }
        for local_name, _ in expected_pairs:
            if getattr(finding, local_name) != observed[local_name]:
                issues.append(_issue(
                    f"finding.{local_name}",
                    DriftClassificationCode.INCONSISTENT_ANCESTRY,
                    "classification must preserve exact Slice 43D custody",
                ))

    return _report(issues)


def validate_package(
    package: DriftClassificationPackage,
    comparison_result: MeaningPreservationComparisonResult | None = None,
) -> DriftClassificationValidationReport:
    issues: list[DriftClassificationIssue] = []
    if type(package) is not DriftClassificationPackage:
        return _report([_issue(
            "package",
            DriftClassificationCode.PACKAGE_INVALID,
            "exact DriftClassificationPackage required",
        )])

    if (
        package.classification_package_id != expected_package_id(package)
        or package.classification_package_digest != expected_package_digest(package)
    ):
        issues.append(_issue(
            "package.identity",
            DriftClassificationCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "classification package identity mismatch",
        ))

    if package.admitted_drift_kind_values != DRIFT_KIND_VALUES:
        issues.append(_issue(
            "package.admitted_drift_kind_values",
            DriftClassificationCode.DRIFT_KIND_INVALID,
            "exact controlled drift-kind registry required",
        ))
    if package.materiality_values != MATERIALITY_VALUES:
        issues.append(_issue(
            "package.materiality_values",
            DriftClassificationCode.MATERIALITY_INVALID,
            "exact materiality registry required",
        ))

    findings = package.drift_findings
    if type(findings) is not tuple or package.classification_record_count != len(findings):
        issues.append(_issue(
            "package.drift_findings",
            DriftClassificationCode.PACKAGE_INVALID,
            "classification count mismatch",
        ))

    comparison_findings = ()
    if comparison_result is not None and comparison_result.comparison_package is not None:
        comparison_findings = comparison_result.comparison_package.findings
        if len(findings) != len(comparison_findings):
            issues.append(_issue(
                "package.drift_findings",
                DriftClassificationCode.INCONSISTENT_ANCESTRY,
                "one classification record per Slice 43D finding required",
            ))

    for index, finding in enumerate(findings):
        source_finding = (
            comparison_findings[index]
            if index < len(comparison_findings)
            else None
        )
        report = validate_finding(finding, source_finding)
        issues.extend(
            _issue(
                f"package.drift_findings[{index}].{item.path}",
                item.code,
                item.detail,
            )
            for item in report.issues
        )

    counts = {
        "drift_finding_count": sum(bool(item.drift_kinds) for item in findings),
        "material_finding_count": sum(
            item.materiality is MaterialityState.MATERIAL for item in findings
        ),
        "non_material_finding_count": sum(
            item.materiality is MaterialityState.NON_MATERIAL for item in findings
        ),
        "not_applicable_finding_count": sum(
            item.materiality is MaterialityState.NOT_APPLICABLE for item in findings
        ),
        "unsupported_finding_count": sum(
            item.materiality is MaterialityState.UNSUPPORTED for item in findings
        ),
        "conflicted_finding_count": sum(
            item.materiality is MaterialityState.CONFLICTED for item in findings
        ),
        "indeterminate_finding_count": sum(
            item.materiality is MaterialityState.INDETERMINATE for item in findings
        ),
    }
    for name, expected in counts.items():
        if getattr(package, name) != expected:
            issues.append(_issue(
                f"package.{name}",
                DriftClassificationCode.PACKAGE_INVALID,
                "count does not match findings",
            ))

    if (
        package.drift_classification_performed is not True
        or package.materiality_findings_created is not True
        or package.schema_version != SLICE43E_SCHEMA_VERSION
        or package.profile_version != SLICE43E_PROFILE_VERSION
    ):
        issues.append(_issue(
            "package.boundary",
            DriftClassificationCode.PACKAGE_INVALID,
            "classification/materiality and supported version boundary required",
        ))
    issues.extend(_authority_zero_issues(package, "package"))

    if comparison_result is not None:
        source_package = comparison_result.comparison_package
        if source_package is None:
            issues.append(_issue(
                "package.comparison_package_ref",
                DriftClassificationCode.COMPARISON_PACKAGE_MISSING,
                "source comparison package missing",
            ))
        else:
            exact = (
                package.comparison_result_ref == comparison_result.comparison_result_id,
                package.comparison_package_ref == source_package.comparison_package_id,
            )
            if not all(exact):
                issues.append(_issue(
                    "package.comparison_refs",
                    DriftClassificationCode.INCONSISTENT_ANCESTRY,
                    "classification package source refs mismatch",
                ))

    return _report(issues)


def validate_result(
    result: DriftClassificationResult,
    comparison_result: MeaningPreservationComparisonResult | None = None,
) -> DriftClassificationValidationReport:
    issues: list[DriftClassificationIssue] = []
    if type(result) is not DriftClassificationResult:
        return _report([_issue(
            "result",
            DriftClassificationCode.RESULT_INVALID,
            "exact DriftClassificationResult required",
        )])

    if (
        result.classification_result_id != expected_result_id(result)
        or result.classification_result_digest != expected_result_digest(result)
    ):
        issues.append(_issue(
            "result.identity",
            DriftClassificationCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "classification result identity mismatch",
        ))

    package = result.classification_package
    if result.status is DriftClassificationExecutionStatus.FINDINGS_CREATED:
        if (
            package is None
            or result.drift_classification_performed is not True
            or result.materiality_findings_created is not True
        ):
            issues.append(_issue(
                "result.status",
                DriftClassificationCode.RESULT_INVALID,
                "findings-created status requires classification package",
            ))
        else:
            package_report = validate_package(package, comparison_result)
            issues.extend(
                _issue(f"result.{item.path}", item.code, item.detail)
                for item in package_report.issues
            )
            for name in (
                "classification_record_count",
                "drift_finding_count",
                "material_finding_count",
                "non_material_finding_count",
                "not_applicable_finding_count",
                "unsupported_finding_count",
                "conflicted_finding_count",
                "indeterminate_finding_count",
            ):
                if getattr(result, name) != getattr(package, name):
                    issues.append(_issue(
                        f"result.{name}",
                        DriftClassificationCode.RESULT_INVALID,
                        "result/package count mismatch",
                    ))
    else:
        if (
            package is not None
            or result.drift_classification_performed
            or result.materiality_findings_created
            or any(
                getattr(result, name)
                for name in (
                    "classification_record_count",
                    "drift_finding_count",
                    "material_finding_count",
                    "non_material_finding_count",
                    "not_applicable_finding_count",
                    "unsupported_finding_count",
                    "conflicted_finding_count",
                    "indeterminate_finding_count",
                )
            )
        ):
            issues.append(_issue(
                "result.held_state",
                DriftClassificationCode.RESULT_INVALID,
                "held result must create no package or findings",
            ))

    if (
        result.schema_version != SLICE43E_SCHEMA_VERSION
        or result.profile_version != SLICE43E_PROFILE_VERSION
    ):
        issues.append(_issue(
            "result.version",
            DriftClassificationCode.UNSUPPORTED_VERSION,
            "unsupported result version",
        ))
    issues.extend(_authority_zero_issues(result, "result"))
    return _report(issues)


__all__ = (
    "validate_classification_inputs",
    "validate_finding",
    "validate_package",
    "validate_result",
)
