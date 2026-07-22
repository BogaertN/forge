"""Deterministic validation for Slice 43F Echo disposition records."""

from __future__ import annotations

from ..schema import EchoDisposition
from ..drift_materiality_classification import (
    DriftClassificationExecutionStatus,
    DriftClassificationPackage,
    DriftClassificationResult,
    MaterialityState,
    validate_result as validate_classification_result,
)
from .authority import (
    ALL_FINDINGS_RETENTION_RULE_REF,
    DETERMINISTIC_ECHO_LAW_VIOLATION_DRIFT_KIND_VALUES,
    DISPOSITION_LAW_REF_MAP,
    NO_SILENT_DRIFT_REMOVAL_RULE_REF,
    PRECEDENCE_RULE_REF,
    REQUESTED_OPERATION,
    SLICE43F_PROFILE_VERSION,
    SLICE43F_SCHEMA_VERSION,
)
from .identity import (
    expected_package_digest,
    expected_package_id,
    expected_record_id,
    expected_result_digest,
    expected_result_id,
)
from .rules import (
    blocking_materiality_states,
    containment_law_refs,
    decide_disposition,
    disposition_law_refs,
    finding_refs_for_materiality,
    incomplete_authority_finding_refs,
    material_violation_finding_refs,
    preserved_ancestry_refs,
    rejection_law_refs,
    retained_drift_kinds,
    unique_values,
)
from .schema import (
    EchoContainmentRecord,
    EchoDispositionCode,
    EchoDispositionExecutionStatus,
    EchoDispositionIssue,
    EchoDispositionPackage,
    EchoDispositionRecord,
    EchoDispositionRequest,
    EchoDispositionResult,
    EchoDispositionState,
    EchoDispositionValidationReport,
    EchoRejectionRecord,
)


def _issue(
    path: str,
    code: EchoDispositionCode,
    detail: str,
) -> EchoDispositionIssue:
    return EchoDispositionIssue(path=path, code=code, detail=detail)


def _report(
    issues: list[EchoDispositionIssue],
) -> EchoDispositionValidationReport:
    return EchoDispositionValidationReport(issues=tuple(issues))


def _valid_identifier(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.strip() == value
        and ":" in value
        and "\n" not in value
        and "\r" not in value
    )


def _valid_string_tuple(value: object) -> bool:
    return (
        type(value) is tuple
        and all(_valid_identifier(item) for item in value)
        and len(value) == len(set(value))
    )


def _authority_zero_issues(
    record: object,
    path: str,
) -> list[EchoDispositionIssue]:
    names = (
        "candidate_rewritten_or_repaired",
        "drift_removed_downgraded_or_suppressed",
        "delivery_authorized_or_performed",
        "echoforge_called",
        "downstream_authority_created",
        "model_or_similarity_authority_used",
        "msm_v1_modified_or_integrated",
        "gp014_superseded",
        "truth_evidence_permission_execution_authority",
        "route_api_network_filesystem_memory_tool_action_authority",
    )
    issues: list[EchoDispositionIssue] = []
    for name in names:
        if hasattr(record, name) and getattr(record, name) is not False:
            issues.append(_issue(
                f"{path}.{name}",
                EchoDispositionCode.REPAIR_OR_DOWNSTREAM_AUTHORITY_PROHIBITED,
                "field must remain false",
            ))
    return issues


def validate_disposition_inputs(
    request: EchoDispositionRequest,
    classification_result: DriftClassificationResult,
) -> EchoDispositionValidationReport:
    issues: list[EchoDispositionIssue] = []
    if type(request) is not EchoDispositionRequest:
        return _report([_issue(
            "request",
            EchoDispositionCode.REQUEST_TYPE_INVALID,
            "exact EchoDispositionRequest required",
        )])

    if request.request_id != expected_record_id(request):
        issues.append(_issue(
            "request.request_id",
            EchoDispositionCode.REQUEST_ID_INVALID,
            "request identifier mismatch",
        ))
    if request.requested_operation != REQUESTED_OPERATION:
        issues.append(_issue(
            "request.requested_operation",
            EchoDispositionCode.REQUEST_OPERATION_INVALID,
            "unsupported operation",
        ))
    if request.raw_text is not None:
        issues.append(_issue(
            "request.raw_text",
            EchoDispositionCode.RAW_TEXT_PROHIBITED,
            "raw text is prohibited",
        ))
    if request.explicit_disposition_request is not True:
        issues.append(_issue(
            "request.explicit_disposition_request",
            EchoDispositionCode.EXPLICIT_REQUEST_REQUIRED,
            "explicit disposition request required",
        ))
    if (
        request.schema_version != SLICE43F_SCHEMA_VERSION
        or request.profile_version != SLICE43F_PROFILE_VERSION
    ):
        issues.append(_issue(
            "request.version",
            EchoDispositionCode.UNSUPPORTED_VERSION,
            "unsupported Slice 43F schema or profile version",
        ))

    if type(classification_result) is not DriftClassificationResult:
        issues.append(_issue(
            "classification_result",
            EchoDispositionCode.CLASSIFICATION_RESULT_TYPE_INVALID,
            "exact Slice 43E classification result required",
        ))
        return _report(issues)

    classification_report = validate_classification_result(classification_result)
    if not classification_report.ok:
        identity_codes = {
            item.code.value for item in classification_report.issues
        }
        if "recomputed_or_fabricated_identity" in identity_codes:
            issues.append(_issue(
                "classification_result.identity",
                EchoDispositionCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
                "Slice 43E result, package or finding identity mismatch",
            ))
        else:
            issues.append(_issue(
                "classification_result",
                EchoDispositionCode.CLASSIFICATION_RESULT_INVALID,
                "Slice 43E result failed deterministic validation",
            ))

    package = classification_result.classification_package
    if (
        classification_result.status
        is not DriftClassificationExecutionStatus.FINDINGS_CREATED
        or classification_result.drift_classification_performed is not True
        or classification_result.materiality_findings_created is not True
    ):
        issues.append(_issue(
            "classification_result.status",
            EchoDispositionCode.CLASSIFICATION_NOT_READY,
            "Slice 43E findings-created result required",
        ))
    if package is None:
        issues.append(_issue(
            "classification_result.classification_package",
            EchoDispositionCode.CLASSIFICATION_PACKAGE_MISSING,
            "classification package required",
        ))
        return _report(issues)

    if request.classification_result_ref != classification_result.classification_result_id:
        issues.append(_issue(
            "request.classification_result_ref",
            EchoDispositionCode.INCONSISTENT_ANCESTRY,
            "request must reference the exact supplied Slice 43E result",
        ))
    if request.classification_package_ref != package.classification_package_id:
        issues.append(_issue(
            "request.classification_package_ref",
            EchoDispositionCode.INCONSISTENT_ANCESTRY,
            "request must reference the exact supplied Slice 43E package",
        ))
    if classification_result.classification_request_ref != package.classification_request_ref:
        issues.append(_issue(
            "classification_result.classification_request_ref",
            EchoDispositionCode.INCONSISTENT_ANCESTRY,
            "classification request custody mismatch",
        ))
    if package.classification_record_count != 13 or len(package.drift_findings) != 13:
        issues.append(_issue(
            "classification_result.classification_package.drift_findings",
            EchoDispositionCode.CLASSIFICATION_FINDING_INVALID,
            "exact thirteen Slice 43E classification findings required",
        ))
    finding_ids = tuple(item.drift_finding_id for item in package.drift_findings)
    if len(finding_ids) != len(set(finding_ids)):
        issues.append(_issue(
            "classification_result.classification_package.drift_findings",
            EchoDispositionCode.CLASSIFICATION_FINDING_INVALID,
            "duplicate finding identities prohibited",
        ))
    return _report(issues)


def validate_rejection_record(
    record: EchoRejectionRecord,
    package: DriftClassificationPackage,
    disposition_record: EchoDispositionRecord,
) -> EchoDispositionValidationReport:
    issues: list[EchoDispositionIssue] = []
    if type(record) is not EchoRejectionRecord:
        return _report([_issue(
            "rejection_record",
            EchoDispositionCode.REJECTION_RECORD_INVALID,
            "exact EchoRejectionRecord required",
        )])
    expected_violations = material_violation_finding_refs(package)
    expected_all = tuple(item.drift_finding_id for item in package.drift_findings)
    expected_kinds = tuple(
        kind
        for kind in retained_drift_kinds(package)
        if kind.value in DETERMINISTIC_ECHO_LAW_VIOLATION_DRIFT_KIND_VALUES
    )
    expected_laws = rejection_law_refs(package, expected_violations)
    if record.rejection_id != expected_record_id(record):
        issues.append(_issue(
            "rejection_record.rejection_id",
            EchoDispositionCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "rejection identifier mismatch",
        ))
    if (
        record.disposition is not EchoDisposition.REJECTED
        or record.violation_finding_refs != expected_violations
        or record.violation_drift_kinds != expected_kinds
        or record.rejection_law_refs != expected_laws
        or record.retained_all_finding_refs != expected_all
        or record.preserved_ancestry_refs != preserved_ancestry_refs(package)
        or record.deterministic_echo_law_violation is not True
        or record.rejection_issued is not True
        or record.disposition_request_ref != disposition_record.disposition_request_ref
        or record.classification_result_ref != disposition_record.classification_result_ref
        or record.classification_package_ref != disposition_record.classification_package_ref
    ):
        issues.append(_issue(
            "rejection_record",
            EchoDispositionCode.REJECTION_RECORD_INVALID,
            "rejection record does not match deterministic material violation grounds",
        ))
    issues.extend(_authority_zero_issues(record, "rejection_record"))
    return _report(issues)


def validate_containment_record(
    record: EchoContainmentRecord,
    package: DriftClassificationPackage,
    disposition_record: EchoDispositionRecord,
) -> EchoDispositionValidationReport:
    issues: list[EchoDispositionIssue] = []
    if type(record) is not EchoContainmentRecord:
        return _report([_issue(
            "containment_record",
            EchoDispositionCode.CONTAINMENT_RECORD_INVALID,
            "exact EchoContainmentRecord required",
        )])
    incomplete = incomplete_authority_finding_refs(package)
    violations = material_violation_finding_refs(package)
    coexistence = bool(incomplete and violations)
    blocking = unique_values(incomplete, violations)
    expected_all = tuple(item.drift_finding_id for item in package.drift_findings)
    if record.containment_id != expected_record_id(record):
        issues.append(_issue(
            "containment_record.containment_id",
            EchoDispositionCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "containment identifier mismatch",
        ))
    if (
        record.disposition is not EchoDisposition.CONTAINED
        or record.blocking_finding_refs != blocking
        or record.incomplete_authority_finding_refs != incomplete
        or record.material_violation_finding_refs != violations
        or record.blocking_materiality_states
        != blocking_materiality_states(package, incomplete)
        or record.containment_law_refs
        != containment_law_refs(package, incomplete, coexistence=coexistence)
        or record.retained_all_finding_refs != expected_all
        or record.preserved_ancestry_refs != preserved_ancestry_refs(package)
        or record.incomplete_authority_blocks_progression is not True
        or record.coexistence_precedence_applied is not coexistence
        or record.containment_issued is not True
        or record.disposition_request_ref != disposition_record.disposition_request_ref
        or record.classification_result_ref != disposition_record.classification_result_ref
        or record.classification_package_ref != disposition_record.classification_package_ref
    ):
        issues.append(_issue(
            "containment_record",
            EchoDispositionCode.CONTAINMENT_RECORD_INVALID,
            "containment record does not match incomplete-authority grounds",
        ))
    issues.extend(_authority_zero_issues(record, "containment_record"))
    return _report(issues)


def validate_disposition_record(
    record: EchoDispositionRecord,
    package: DriftClassificationPackage,
    rejection_record: EchoRejectionRecord | None,
    containment_record: EchoContainmentRecord | None,
) -> EchoDispositionValidationReport:
    issues: list[EchoDispositionIssue] = []
    if type(record) is not EchoDispositionRecord:
        return _report([_issue(
            "disposition_record",
            EchoDispositionCode.DISPOSITION_INVALID,
            "exact EchoDispositionRecord required",
        )])
    (
        expected_disposition,
        expected_state,
        violations,
        incomplete,
        all_pass,
        has_violation,
        blocked,
        coexistence,
    ) = decide_disposition(package)
    all_refs = tuple(item.drift_finding_id for item in package.drift_findings)
    no_drift = finding_refs_for_materiality(package, MaterialityState.NOT_APPLICABLE)
    non_material = finding_refs_for_materiality(package, MaterialityState.NON_MATERIAL)
    unsupported = finding_refs_for_materiality(package, MaterialityState.UNSUPPORTED)
    conflicted = finding_refs_for_materiality(package, MaterialityState.CONFLICTED)
    indeterminate = finding_refs_for_materiality(package, MaterialityState.INDETERMINATE)

    if record.disposition_id != expected_record_id(record):
        issues.append(_issue(
            "disposition_record.disposition_id",
            EchoDispositionCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "disposition identifier mismatch",
        ))
    expected_rejection_ref = (
        rejection_record.rejection_id if rejection_record is not None else None
    )
    expected_containment_ref = (
        containment_record.containment_id if containment_record is not None else None
    )
    exact = (
        record.disposition is expected_disposition,
        record.disposition_state is expected_state,
        record.all_finding_refs == all_refs,
        record.no_drift_finding_refs == no_drift,
        record.non_material_finding_refs == non_material,
        record.material_violation_finding_refs == violations,
        record.incomplete_authority_finding_refs == incomplete,
        record.unsupported_finding_refs == unsupported,
        record.conflicted_finding_refs == conflicted,
        record.indeterminate_finding_refs == indeterminate,
        record.retained_drift_kinds == retained_drift_kinds(package),
        record.disposition_law_refs == disposition_law_refs(expected_disposition),
        record.precedence_rule_ref == PRECEDENCE_RULE_REF,
        record.all_findings_retention_rule_ref == ALL_FINDINGS_RETENTION_RULE_REF,
        record.no_silent_drift_removal_rule_ref == NO_SILENT_DRIFT_REMOVAL_RULE_REF,
        record.all_material_preservation_obligations_pass is all_pass,
        record.deterministic_echo_law_violation is has_violation,
        record.incomplete_authority_blocks_progression is blocked,
        record.coexistence_precedence_applied is coexistence,
        record.rejection_record_ref == expected_rejection_ref,
        record.containment_record_ref == expected_containment_ref,
    )
    if not all(exact):
        issues.append(_issue(
            "disposition_record",
            EchoDispositionCode.DISPOSITION_INVALID,
            "disposition record does not match deterministic Slice 43F law",
        ))
    if expected_disposition is EchoDisposition.PASSED:
        if rejection_record is not None or containment_record is not None:
            issues.append(_issue(
                "disposition_record.custody",
                EchoDispositionCode.DISPOSITION_INVALID,
                "PASSED creates no rejection or containment record",
            ))
    elif expected_disposition is EchoDisposition.REJECTED:
        if rejection_record is None or containment_record is not None:
            issues.append(_issue(
                "disposition_record.custody",
                EchoDispositionCode.DISPOSITION_INVALID,
                "REJECTED requires rejection-only custody",
            ))
    else:
        if containment_record is None or rejection_record is not None:
            issues.append(_issue(
                "disposition_record.custody",
                EchoDispositionCode.DISPOSITION_INVALID,
                "CONTAINED requires containment-only custody",
            ))
    issues.extend(_authority_zero_issues(record, "disposition_record"))
    return _report(issues)


def validate_package(
    package: EchoDispositionPackage,
    classification_result: DriftClassificationResult,
) -> EchoDispositionValidationReport:
    issues: list[EchoDispositionIssue] = []
    if type(package) is not EchoDispositionPackage:
        return _report([_issue(
            "package",
            EchoDispositionCode.PACKAGE_INVALID,
            "exact EchoDispositionPackage required",
        )])
    source = classification_result.classification_package
    if source is None:
        return _report([_issue(
            "classification_result.classification_package",
            EchoDispositionCode.CLASSIFICATION_PACKAGE_MISSING,
            "source classification package required",
        )])
    if (
        package.disposition_package_id != expected_package_id(package)
        or package.disposition_package_digest != expected_package_digest(package)
    ):
        issues.append(_issue(
            "package.identity",
            EchoDispositionCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "disposition package identity mismatch",
        ))
    report = validate_disposition_record(
        package.disposition_record,
        source,
        package.rejection_record,
        package.containment_record,
    )
    issues.extend(
        _issue(f"package.{item.path}", item.code, item.detail)
        for item in report.issues
    )
    if package.rejection_record is not None:
        report = validate_rejection_record(
            package.rejection_record,
            source,
            package.disposition_record,
        )
        issues.extend(
            _issue(f"package.{item.path}", item.code, item.detail)
            for item in report.issues
        )
    if package.containment_record is not None:
        report = validate_containment_record(
            package.containment_record,
            source,
            package.disposition_record,
        )
        issues.extend(
            _issue(f"package.{item.path}", item.code, item.detail)
            for item in report.issues
        )

    all_count = len(source.drift_findings)
    no_drift_count = sum(
        item.materiality is MaterialityState.NOT_APPLICABLE
        for item in source.drift_findings
    )
    non_material_count = sum(
        item.materiality is MaterialityState.NON_MATERIAL
        for item in source.drift_findings
    )
    violation_count = len(material_violation_finding_refs(source))
    incomplete_count = len(incomplete_authority_finding_refs(source))
    expected = (
        package.disposition_request_ref
        == package.disposition_record.disposition_request_ref,
        package.classification_result_ref
        == classification_result.classification_result_id,
        package.classification_package_ref == source.classification_package_id,
        package.classification_record_count == all_count,
        package.no_drift_finding_count == no_drift_count,
        package.non_material_finding_count == non_material_count,
        package.material_violation_finding_count == violation_count,
        package.incomplete_authority_finding_count == incomplete_count,
        package.retained_finding_count == all_count,
        package.disposition_decided is True,
        package.rejection_issued
        is (package.disposition_record.disposition is EchoDisposition.REJECTED),
        package.containment_issued
        is (package.disposition_record.disposition is EchoDisposition.CONTAINED),
        package.schema_version == SLICE43F_SCHEMA_VERSION,
        package.profile_version == SLICE43F_PROFILE_VERSION,
    )
    if not all(expected):
        issues.append(_issue(
            "package",
            EchoDispositionCode.PACKAGE_INVALID,
            "package counts, refs or disposition flags mismatch",
        ))
    issues.extend(_authority_zero_issues(package, "package"))
    return _report(issues)


def validate_result(
    result: EchoDispositionResult,
    classification_result: DriftClassificationResult,
) -> EchoDispositionValidationReport:
    issues: list[EchoDispositionIssue] = []
    if type(result) is not EchoDispositionResult:
        return _report([_issue(
            "result",
            EchoDispositionCode.RESULT_INVALID,
            "exact EchoDispositionResult required",
        )])
    if (
        result.disposition_result_id != expected_result_id(result)
        or result.disposition_result_digest != expected_result_digest(result)
    ):
        issues.append(_issue(
            "result.identity",
            EchoDispositionCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "disposition result identity mismatch",
        ))
    package = result.disposition_package
    if result.status is EchoDispositionExecutionStatus.DISPOSITION_CREATED:
        if package is None or result.disposition_decided is not True:
            issues.append(_issue(
                "result.status",
                EchoDispositionCode.RESULT_INVALID,
                "created status requires disposition package",
            ))
        else:
            package_report = validate_package(package, classification_result)
            issues.extend(
                _issue(f"result.{item.path}", item.code, item.detail)
                for item in package_report.issues
            )
            exact = (
                result.disposition is package.disposition_record.disposition,
                result.rejection_issued is package.rejection_issued,
                result.containment_issued is package.containment_issued,
                result.classification_record_count
                == package.classification_record_count,
                result.retained_finding_count == package.retained_finding_count,
                result.material_violation_finding_count
                == package.material_violation_finding_count,
                result.incomplete_authority_finding_count
                == package.incomplete_authority_finding_count,
            )
            if not all(exact):
                issues.append(_issue(
                    "result",
                    EchoDispositionCode.RESULT_INVALID,
                    "result/package disposition summary mismatch",
                ))
    else:
        if (
            package is not None
            or result.disposition_decided
            or result.disposition is not None
            or result.rejection_issued
            or result.containment_issued
            or result.classification_record_count
            or result.retained_finding_count
            or result.material_violation_finding_count
            or result.incomplete_authority_finding_count
        ):
            issues.append(_issue(
                "result.held_state",
                EchoDispositionCode.RESULT_INVALID,
                "held result must create no disposition package or custody",
            ))
    if (
        result.schema_version != SLICE43F_SCHEMA_VERSION
        or result.profile_version != SLICE43F_PROFILE_VERSION
    ):
        issues.append(_issue(
            "result.version",
            EchoDispositionCode.UNSUPPORTED_VERSION,
            "unsupported result version",
        ))
    issues.extend(_authority_zero_issues(result, "result"))
    return _report(issues)


__all__ = (
    "validate_containment_record",
    "validate_disposition_inputs",
    "validate_disposition_record",
    "validate_package",
    "validate_rejection_record",
    "validate_result",
)
