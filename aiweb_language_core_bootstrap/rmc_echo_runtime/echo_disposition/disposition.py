"""Deterministic Slice 43F Echo disposition, rejection and containment."""

from __future__ import annotations

from ..schema import EchoDisposition
from ..drift_materiality_classification import (
    DriftClassificationPackage,
    DriftClassificationResult,
    MaterialityState,
)
from .authority import (
    ALL_FINDINGS_RETENTION_RULE_REF,
    DETERMINISTIC_ECHO_LAW_VIOLATION_DRIFT_KIND_VALUES,
    NO_SILENT_DRIFT_REMOVAL_RULE_REF,
    PRECEDENCE_RULE_REF,
    REQUESTED_OPERATION,
)
from .identity import (
    with_expected_id,
    with_expected_package_identity,
    with_expected_result_identity,
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
    status_for_codes,
    unique_values,
)
from .schema import (
    EchoContainmentRecord,
    EchoDispositionCode,
    EchoDispositionExecutionStatus,
    EchoDispositionPackage,
    EchoDispositionRecord,
    EchoDispositionRequest,
    EchoDispositionResult,
    EchoRejectionRecord,
)
from .validation import (
    validate_disposition_inputs,
    validate_result,
)


def build_disposition_request(
    classification_result: DriftClassificationResult,
) -> EchoDispositionRequest:
    package = classification_result.classification_package
    package_ref = (
        package.classification_package_id
        if package is not None
        else "missing-classification-package"
    )
    request = EchoDispositionRequest(
        request_id="",
        classification_result_ref=classification_result.classification_result_id,
        classification_package_ref=package_ref,
        requested_operation=REQUESTED_OPERATION,
        raw_text=None,
        explicit_disposition_request=True,
    )
    return with_expected_id(request)


def _held_result(
    request: object,
    classification_result: object,
    issue_codes: tuple[EchoDispositionCode, ...],
    reason_refs: tuple[str, ...],
) -> EchoDispositionResult:
    request_ref = getattr(request, "request_id", "invalid-request")
    result_ref = getattr(
        classification_result,
        "classification_result_id",
        "invalid-classification-result",
    )
    source_package = getattr(classification_result, "classification_package", None)
    package_ref = getattr(
        source_package,
        "classification_package_id",
        "invalid-classification-package",
    )
    result = EchoDispositionResult(
        disposition_result_id="",
        disposition_result_digest="",
        status=status_for_codes(issue_codes),
        issue_codes=issue_codes,
        reason_refs=reason_refs,
        disposition_request_ref=request_ref,
        classification_result_ref=result_ref,
        classification_package_ref=package_ref,
        disposition_package=None,
        disposition_decided=False,
        disposition=None,
        rejection_issued=False,
        containment_issued=False,
        classification_record_count=0,
        retained_finding_count=0,
        material_violation_finding_count=0,
        incomplete_authority_finding_count=0,
        candidate_rewritten_or_repaired=False,
        drift_removed_downgraded_or_suppressed=False,
        delivery_authorized_or_performed=False,
        echoforge_called=False,
        downstream_authority_created=False,
        model_or_similarity_authority_used=False,
        msm_v1_modified_or_integrated=False,
        gp014_superseded=False,
    )
    return with_expected_result_identity(result)


def _violation_kinds(
    package: DriftClassificationPackage,
    violation_refs: tuple[str, ...],
):
    selected = set(violation_refs)
    kinds = set()
    for finding in package.drift_findings:
        if finding.drift_finding_id in selected:
            kinds.update(finding.drift_kinds)
    registry = set(DETERMINISTIC_ECHO_LAW_VIOLATION_DRIFT_KIND_VALUES)
    ordered = retained_drift_kinds(package)
    return tuple(
        kind for kind in ordered if kind in kinds and kind.value in registry
    )


def decide_echo_disposition(
    request: object,
    classification_result: object,
) -> EchoDispositionResult:
    report = validate_disposition_inputs(request, classification_result)
    if not report.ok:
        codes = tuple(dict.fromkeys(item.code for item in report.issues))
        reasons = tuple(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        return _held_result(request, classification_result, codes, reasons)

    assert isinstance(request, EchoDispositionRequest)
    assert isinstance(classification_result, DriftClassificationResult)
    source_package = classification_result.classification_package
    assert source_package is not None

    (
        disposition,
        disposition_state,
        violation_refs,
        incomplete_refs,
        all_material_pass,
        deterministic_violation,
        incomplete_blocks,
        coexistence,
    ) = decide_disposition(source_package)

    all_refs = tuple(
        item.drift_finding_id for item in source_package.drift_findings
    )
    no_drift_refs = finding_refs_for_materiality(
        source_package,
        MaterialityState.NOT_APPLICABLE,
    )
    non_material_refs = finding_refs_for_materiality(
        source_package,
        MaterialityState.NON_MATERIAL,
    )
    unsupported_refs = finding_refs_for_materiality(
        source_package,
        MaterialityState.UNSUPPORTED,
    )
    conflicted_refs = finding_refs_for_materiality(
        source_package,
        MaterialityState.CONFLICTED,
    )
    indeterminate_refs = finding_refs_for_materiality(
        source_package,
        MaterialityState.INDETERMINATE,
    )
    ancestry_refs = preserved_ancestry_refs(source_package)

    rejection_record = None
    containment_record = None
    if disposition is EchoDisposition.REJECTED:
        rejection_record = EchoRejectionRecord(
            rejection_id="",
            disposition_request_ref=request.request_id,
            classification_result_ref=classification_result.classification_result_id,
            classification_package_ref=source_package.classification_package_id,
            disposition=EchoDisposition.REJECTED,
            violation_finding_refs=violation_refs,
            violation_drift_kinds=_violation_kinds(source_package, violation_refs),
            rejection_law_refs=rejection_law_refs(source_package, violation_refs),
            retained_all_finding_refs=all_refs,
            preserved_ancestry_refs=ancestry_refs,
            deterministic_echo_law_violation=True,
            rejection_issued=True,
            candidate_rewritten_or_repaired=False,
            drift_removed_downgraded_or_suppressed=False,
            delivery_authorized_or_performed=False,
            echoforge_called=False,
            model_or_similarity_authority_used=False,
            downstream_authority_created=False,
            msm_v1_modified_or_integrated=False,
            gp014_superseded=False,
        )
        rejection_record = with_expected_id(rejection_record)
    elif disposition is EchoDisposition.CONTAINED:
        containment_record = EchoContainmentRecord(
            containment_id="",
            disposition_request_ref=request.request_id,
            classification_result_ref=classification_result.classification_result_id,
            classification_package_ref=source_package.classification_package_id,
            disposition=EchoDisposition.CONTAINED,
            blocking_finding_refs=unique_values(incomplete_refs, violation_refs),
            incomplete_authority_finding_refs=incomplete_refs,
            material_violation_finding_refs=violation_refs,
            blocking_materiality_states=blocking_materiality_states(
                source_package,
                incomplete_refs,
            ),
            containment_law_refs=containment_law_refs(
                source_package,
                incomplete_refs,
                coexistence=coexistence,
            ),
            retained_all_finding_refs=all_refs,
            preserved_ancestry_refs=ancestry_refs,
            incomplete_authority_blocks_progression=True,
            coexistence_precedence_applied=coexistence,
            containment_issued=True,
            candidate_rewritten_or_repaired=False,
            drift_removed_downgraded_or_suppressed=False,
            delivery_authorized_or_performed=False,
            echoforge_called=False,
            model_or_similarity_authority_used=False,
            downstream_authority_created=False,
            msm_v1_modified_or_integrated=False,
            gp014_superseded=False,
        )
        containment_record = with_expected_id(containment_record)

    disposition_record = EchoDispositionRecord(
        disposition_id="",
        disposition_request_ref=request.request_id,
        classification_result_ref=classification_result.classification_result_id,
        classification_package_ref=source_package.classification_package_id,
        disposition=disposition,
        disposition_state=disposition_state,
        all_finding_refs=all_refs,
        no_drift_finding_refs=no_drift_refs,
        non_material_finding_refs=non_material_refs,
        material_violation_finding_refs=violation_refs,
        incomplete_authority_finding_refs=incomplete_refs,
        unsupported_finding_refs=unsupported_refs,
        conflicted_finding_refs=conflicted_refs,
        indeterminate_finding_refs=indeterminate_refs,
        retained_drift_kinds=retained_drift_kinds(source_package),
        disposition_law_refs=disposition_law_refs(disposition),
        precedence_rule_ref=PRECEDENCE_RULE_REF,
        all_findings_retention_rule_ref=ALL_FINDINGS_RETENTION_RULE_REF,
        no_silent_drift_removal_rule_ref=NO_SILENT_DRIFT_REMOVAL_RULE_REF,
        all_material_preservation_obligations_pass=all_material_pass,
        deterministic_echo_law_violation=deterministic_violation,
        incomplete_authority_blocks_progression=incomplete_blocks,
        coexistence_precedence_applied=coexistence,
        rejection_record_ref=(
            rejection_record.rejection_id
            if rejection_record is not None
            else None
        ),
        containment_record_ref=(
            containment_record.containment_id
            if containment_record is not None
            else None
        ),
        candidate_rewritten_or_repaired=False,
        drift_removed_downgraded_or_suppressed=False,
        delivery_authorized_or_performed=False,
        echoforge_called=False,
        model_or_similarity_authority_used=False,
        downstream_authority_created=False,
        msm_v1_modified_or_integrated=False,
        gp014_superseded=False,
    )
    disposition_record = with_expected_id(disposition_record)

    package = EchoDispositionPackage(
        disposition_package_id="",
        disposition_package_digest="",
        disposition_request_ref=request.request_id,
        classification_result_ref=classification_result.classification_result_id,
        classification_package_ref=source_package.classification_package_id,
        disposition_record=disposition_record,
        rejection_record=rejection_record,
        containment_record=containment_record,
        classification_record_count=len(all_refs),
        no_drift_finding_count=len(no_drift_refs),
        non_material_finding_count=len(non_material_refs),
        material_violation_finding_count=len(violation_refs),
        incomplete_authority_finding_count=len(incomplete_refs),
        retained_finding_count=len(all_refs),
        disposition_decided=True,
        rejection_issued=disposition is EchoDisposition.REJECTED,
        containment_issued=disposition is EchoDisposition.CONTAINED,
        candidate_rewritten_or_repaired=False,
        drift_removed_downgraded_or_suppressed=False,
        delivery_authorized_or_performed=False,
        truth_evidence_permission_execution_authority=False,
        route_api_network_filesystem_memory_tool_action_authority=False,
        echoforge_called=False,
        downstream_authority_created=False,
        model_or_similarity_authority_used=False,
        msm_v1_modified_or_integrated=False,
        gp014_superseded=False,
    )
    package = with_expected_package_identity(package)

    result = EchoDispositionResult(
        disposition_result_id="",
        disposition_result_digest="",
        status=EchoDispositionExecutionStatus.DISPOSITION_CREATED,
        issue_codes=(),
        reason_refs=(
            f"slice43f:disposition:{disposition.value}",
            *disposition_law_refs(disposition),
            ALL_FINDINGS_RETENTION_RULE_REF,
            NO_SILENT_DRIFT_REMOVAL_RULE_REF,
        ),
        disposition_request_ref=request.request_id,
        classification_result_ref=classification_result.classification_result_id,
        classification_package_ref=source_package.classification_package_id,
        disposition_package=package,
        disposition_decided=True,
        disposition=disposition,
        rejection_issued=disposition is EchoDisposition.REJECTED,
        containment_issued=disposition is EchoDisposition.CONTAINED,
        classification_record_count=len(all_refs),
        retained_finding_count=len(all_refs),
        material_violation_finding_count=len(violation_refs),
        incomplete_authority_finding_count=len(incomplete_refs),
        candidate_rewritten_or_repaired=False,
        drift_removed_downgraded_or_suppressed=False,
        delivery_authorized_or_performed=False,
        echoforge_called=False,
        downstream_authority_created=False,
        model_or_similarity_authority_used=False,
        msm_v1_modified_or_integrated=False,
        gp014_superseded=False,
    )
    result = with_expected_result_identity(result)
    result_report = validate_result(result, classification_result)
    if not result_report.ok:
        return _held_result(
            request,
            classification_result,
            tuple(dict.fromkeys(item.code for item in result_report.issues)),
            tuple(
                f"{item.path}:{item.code.value}:{item.detail}"
                for item in result_report.issues
            ),
        )
    return result


__all__ = (
    "build_disposition_request",
    "decide_echo_disposition",
)
