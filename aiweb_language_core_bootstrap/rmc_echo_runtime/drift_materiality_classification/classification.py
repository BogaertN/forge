"""Deterministic Slice 43E drift and materiality classification."""

from __future__ import annotations

from ..meaning_preservation_comparison import MeaningPreservationComparisonResult
from .authority import (
    DRIFT_KIND_VALUES,
    MATERIALITY_VALUES,
    REQUESTED_OPERATION,
)
from .identity import (
    with_expected_id,
    with_expected_package_identity,
    with_expected_result_identity,
)
from .rules import (
    classify_finding,
    materiality_rule_ref,
    status_for_codes,
    unique_values,
)
from .schema import (
    DriftClassificationCode,
    DriftClassificationExecutionStatus,
    DriftClassificationPackage,
    DriftClassificationRequest,
    DriftClassificationResult,
    DriftMaterialityFinding,
    MaterialityState,
)
from .validation import (
    validate_classification_inputs,
    validate_result,
)


def build_classification_request(
    comparison_result: MeaningPreservationComparisonResult,
) -> DriftClassificationRequest:
    package = comparison_result.comparison_package
    package_ref = (
        package.comparison_package_id
        if package is not None
        else "missing-comparison-package"
    )
    request = DriftClassificationRequest(
        request_id="",
        comparison_result_ref=comparison_result.comparison_result_id,
        comparison_package_ref=package_ref,
        requested_operation=REQUESTED_OPERATION,
        raw_text=None,
        explicit_classification_request=True,
    )
    return with_expected_id(request)


def _held_result(
    request: object,
    comparison_result: object,
    issue_codes: tuple[DriftClassificationCode, ...],
    reason_refs: tuple[str, ...],
) -> DriftClassificationResult:
    request_ref = getattr(request, "request_id", "invalid-request")
    result_ref = getattr(
        comparison_result,
        "comparison_result_id",
        "invalid-comparison-result",
    )
    source_package = getattr(comparison_result, "comparison_package", None)
    package_ref = getattr(
        source_package,
        "comparison_package_id",
        "invalid-comparison-package",
    )
    result = DriftClassificationResult(
        classification_result_id="",
        classification_result_digest="",
        status=status_for_codes(issue_codes),
        issue_codes=issue_codes,
        reason_refs=reason_refs,
        classification_request_ref=request_ref,
        comparison_result_ref=result_ref,
        comparison_package_ref=package_ref,
        classification_package=None,
        drift_classification_performed=False,
        materiality_findings_created=False,
        classification_record_count=0,
        drift_finding_count=0,
        material_finding_count=0,
        non_material_finding_count=0,
        not_applicable_finding_count=0,
        unsupported_finding_count=0,
        conflicted_finding_count=0,
        indeterminate_finding_count=0,
        aggregate_pass_rejected_contained_decided=False,
        echo_disposition_decided=False,
        rejection_or_containment_issued=False,
        text_repaired_or_rewritten=False,
        msm_v1_modified_or_integrated=False,
        delivered=False,
        downstream_authority_created=False,
        model_or_similarity_authority_used=False,
        gp014_superseded=False,
    )
    return with_expected_result_identity(result)


def classify_drift_and_materiality(
    request: object,
    comparison_result: object,
) -> DriftClassificationResult:
    report = validate_classification_inputs(request, comparison_result)
    if not report.ok:
        codes = tuple(dict.fromkeys(item.code for item in report.issues))
        reasons = tuple(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        return _held_result(request, comparison_result, codes, reasons)

    assert isinstance(request, DriftClassificationRequest)
    assert isinstance(comparison_result, MeaningPreservationComparisonResult)
    comparison_package = comparison_result.comparison_package
    assert comparison_package is not None

    findings: list[DriftMaterialityFinding] = []
    for source_finding in comparison_package.findings:
        (
            state,
            drift_kinds,
            materiality,
            classification_rules,
            grounds,
            ancestry_mismatches,
        ) = classify_finding(source_finding)
        finding = DriftMaterialityFinding(
            drift_finding_id="",
            classification_request_ref=request.request_id,
            comparison_result_ref=comparison_result.comparison_result_id,
            comparison_package_ref=comparison_package.comparison_package_id,
            comparison_finding_ref=source_finding.finding_id,
            dimension=source_finding.dimension,
            comparison_outcome=source_finding.outcome,
            classification_state=state,
            drift_kinds=drift_kinds,
            materiality=materiality,
            source_snapshot_ref=source_finding.source_snapshot.snapshot_id,
            proposed_snapshot_ref=source_finding.proposed_snapshot.snapshot_id,
            source_values=source_finding.source_snapshot.values,
            proposed_values=source_finding.proposed_snapshot.values,
            source_field_paths=source_finding.source_snapshot.field_paths,
            proposed_field_paths=source_finding.proposed_snapshot.field_paths,
            comparison_evidence_refs=source_finding.evidence_refs,
            comparison_trace_refs=source_finding.trace_refs,
            classification_rule_refs=classification_rules,
            materiality_rule_ref=materiality_rule_ref(materiality),
            materiality_ground_refs=grounds,
            ancestry_mismatch_refs=ancestry_mismatches,
            finding_only=True,
            text_repaired_or_rewritten=False,
            echo_disposition_decided=False,
            rejection_or_containment_issued=False,
            msm_v1_modified_or_integrated=False,
            delivery_authorized_or_performed=False,
            downstream_authority_created=False,
            model_or_similarity_authority_used=False,
            gp014_superseded=False,
        )
        findings.append(with_expected_id(finding))

    finding_tuple = tuple(findings)
    counts = {
        "drift_finding_count": sum(bool(item.drift_kinds) for item in finding_tuple),
        "material_finding_count": sum(
            item.materiality is MaterialityState.MATERIAL for item in finding_tuple
        ),
        "non_material_finding_count": sum(
            item.materiality is MaterialityState.NON_MATERIAL for item in finding_tuple
        ),
        "not_applicable_finding_count": sum(
            item.materiality is MaterialityState.NOT_APPLICABLE
            for item in finding_tuple
        ),
        "unsupported_finding_count": sum(
            item.materiality is MaterialityState.UNSUPPORTED for item in finding_tuple
        ),
        "conflicted_finding_count": sum(
            item.materiality is MaterialityState.CONFLICTED for item in finding_tuple
        ),
        "indeterminate_finding_count": sum(
            item.materiality is MaterialityState.INDETERMINATE
            for item in finding_tuple
        ),
    }
    package = DriftClassificationPackage(
        classification_package_id="",
        classification_package_digest="",
        classification_request_ref=request.request_id,
        comparison_result_ref=comparison_result.comparison_result_id,
        comparison_package_ref=comparison_package.comparison_package_id,
        drift_findings=finding_tuple,
        admitted_drift_kind_values=DRIFT_KIND_VALUES,
        materiality_values=MATERIALITY_VALUES,
        classification_record_count=len(finding_tuple),
        **counts,
        drift_classification_performed=True,
        materiality_findings_created=True,
        aggregate_pass_rejected_contained_decided=False,
        echo_disposition_decided=False,
        rejection_or_containment_issued=False,
        text_repaired_or_rewritten=False,
        msm_v1_modified_or_integrated=False,
        delivery_authorized_or_performed=False,
        truth_evidence_permission_execution_authority=False,
        route_api_network_filesystem_memory_tool_action_authority=False,
        model_or_similarity_authority_used=False,
        gp014_superseded=False,
    )
    package = with_expected_package_identity(package)

    result = DriftClassificationResult(
        classification_result_id="",
        classification_result_digest="",
        status=DriftClassificationExecutionStatus.FINDINGS_CREATED,
        issue_codes=(),
        reason_refs=(
            "slice43e:drift-and-materiality-findings-created",
            "slice43e:no-echo-disposition",
            "slice43e:no-text-repair",
        ),
        classification_request_ref=request.request_id,
        comparison_result_ref=comparison_result.comparison_result_id,
        comparison_package_ref=comparison_package.comparison_package_id,
        classification_package=package,
        drift_classification_performed=True,
        materiality_findings_created=True,
        classification_record_count=len(finding_tuple),
        **counts,
        aggregate_pass_rejected_contained_decided=False,
        echo_disposition_decided=False,
        rejection_or_containment_issued=False,
        text_repaired_or_rewritten=False,
        msm_v1_modified_or_integrated=False,
        delivered=False,
        downstream_authority_created=False,
        model_or_similarity_authority_used=False,
        gp014_superseded=False,
    )
    result = with_expected_result_identity(result)
    result_report = validate_result(result, comparison_result)
    if not result_report.ok:
        return _held_result(
            request,
            comparison_result,
            tuple(dict.fromkeys(item.code for item in result_report.issues)),
            tuple(
                f"{item.path}:{item.code.value}:{item.detail}"
                for item in result_report.issues
            ),
        )
    return result


__all__ = (
    "build_classification_request",
    "classify_drift_and_materiality",
)
