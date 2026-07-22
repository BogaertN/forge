"""Deterministic Slice 43C authorized source admission."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from ...meaning_structure_manifest.serialization import (
    canonical_manifest_sha256,
)
from ...outward_expression_runtime.disabled_outward_expression_closeout import (
    DisabledOutwardExpressionCloseoutResult,
)
from ..governed_lifecycle import with_expected_id as with_expected_core_id
from ..schema import (
    AuthorizedMeaningReferenceRecord,
    EchoValidationInputBoundaryRecord,
    EchoValidationInputCustodyState,
    PreservationDimension,
    ProposedExpressionReferenceRecord,
)
from .authority import (
    REQUESTED_OPERATION,
    SLICE43C_PROFILE_VERSION,
    SLICE43C_SCHEMA_VERSION,
)
from .identity import (
    with_expected_id,
    with_expected_package_identity,
    with_expected_result_identity,
)
from .rules import status_for_codes
from .schema import (
    AuthorizedMeaningAdmissionRecord,
    EchoValidationAdmissionPackage,
    ProposedExpressionAdmissionRecord,
    SourceAdmissionCode,
    SourceAdmissionRequest,
    SourceAdmissionResult,
    SourceAdmissionStatus,
)
from .validation import (
    validate_admission_package,
    validate_request,
    validate_result,
)


def build_source_admission_request(
    source_closeout_result: DisabledOutwardExpressionCloseoutResult,
    *,
    raw_text: str | None = None,
) -> SourceAdmissionRequest:
    value = SourceAdmissionRequest(
        request_id="pending",
        source_closeout_result=source_closeout_result,
        requested_operation=REQUESTED_OPERATION,
        raw_text=raw_text,
        explicit_admission_request=True,
    )
    return with_expected_id(value)


def _source_objects(source: DisabledOutwardExpressionCloseoutResult) -> dict[str, Any]:
    integration_input = source.integration_input
    integration_result = source.integration_result
    assert integration_input is not None
    assert integration_result is not None
    selected_result = integration_input.source_selected_meaning_integration_result
    selected_package = (
        integration_input.source_selected_meaning_integration_input
        .selected_meaning_package
    )
    surface_input = integration_input.surface_realization_input
    surface_result = integration_input.surface_realization_result
    plan_input = surface_input.plan_input
    plan_result = surface_input.plan_result
    projection_input = plan_input.projection_input
    projection_result = plan_input.projection_result
    eligibility_result = projection_input.expression_eligibility_result
    selected = selected_result.integrated_selected_meaning_record
    candidate = surface_result.expression_candidate
    outward = integration_result.governed_outward_meaning_record
    link = integration_result.expression_link_record
    return locals()


def _unique(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group))


def _build_authorized_reference(objects: dict[str, Any]) -> AuthorizedMeaningReferenceRecord:
    integration_input = objects["integration_input"]
    integration_result = objects["integration_result"]
    selected_result = objects["selected_result"]
    selected_package = objects["selected_package"]
    plan_result = objects["plan_result"]
    projection_result = objects["projection_result"]
    eligibility_result = objects["eligibility_result"]
    selected = objects["selected"]
    outward = objects["outward"]

    plan = plan_result.expression_plan
    companion = integration_result.companion
    value = AuthorizedMeaningReferenceRecord(
        authorized_meaning_reference_id="pending",
        slice42g_integration_input_ref=integration_input.integration_input_id,
        slice42g_integration_result_ref=integration_result.result_id,
        slice42g_integration_receipt_ref=integration_result.receipt.receipt_id,
        slice42h_acceptance_record_ref=objects["source"].acceptance_record.record_id,
        source_manifest_ref=integration_result.source_manifest.manifest_id,
        successor_manifest_ref=integration_result.successor_manifest.manifest_id,
        lineage_id=selected.lineage_id,
        selected_governed_meaning_ref=selected.record_id,
        selected_candidate_ref=selected.selected_candidate_ref,
        selection_authority_reference_ref=(
            selected_result.authority_reference_record.record_id
        ),
        governed_outward_meaning_ref=outward.record_id,
        outward_expression_authority_ref=(
            integration_result.external_authority_reference_record.record_id
        ),
        expression_eligibility_result_ref=eligibility_result.result_id,
        preservation_obligation_package_ref=(
            projection_result.obligation_package.obligation_package_id
        ),
        expression_plan_ref=plan.expression_plan_id,
        selected_meaning_content_proof_ref=(
            selected_result.companion.content_proof_ref
        ),
        governed_outward_meaning_content_proof_ref=(
            integration_result.receipt.receipt_id
        ),
        preserved_alternative_refs=companion.preserved_alternative_refs,
        unresolved_condition_refs=companion.unresolved_condition_refs,
        inherited_limitation_refs=selected.inherited_limitations,
        required_qualification_refs=plan.required_qualification_refs,
        required_caveat_refs=plan.required_caveat_refs,
        refusal_relevant_boundary_refs=plan.refusal_relevant_boundary_refs,
        ambiguity_refs=plan.ambiguity_refs,
        privacy_identity_boundary_refs=plan.privacy_identity_boundary_refs,
        preservation_class_refs=tuple(
            item.value if hasattr(item, "value") else str(item)
            for item in outward.preservation_classes
        ),
        version_refs=_unique(
            integration_input.version_refs,
            plan.version_refs,
            objects["surface_input"].version_refs,
            ("MSM-v1", SLICE43C_SCHEMA_VERSION),
        ),
    )
    return with_expected_core_id(value)


def _build_proposed_reference(objects: dict[str, Any]) -> ProposedExpressionReferenceRecord:
    integration_input = objects["integration_input"]
    integration_result = objects["integration_result"]
    surface_input = objects["surface_input"]
    surface_result = objects["surface_result"]
    candidate = objects["candidate"]
    outward = objects["outward"]
    link = objects["link"]
    trace = surface_result.realization_trace
    receipt = surface_result.realization_receipt
    value = ProposedExpressionReferenceRecord(
        proposed_expression_reference_id="pending",
        slice42f_realization_input_ref=surface_input.realization_input_id,
        slice42f_realization_result_ref=surface_result.result_id,
        slice42f_realization_receipt_ref=receipt.realization_receipt_id,
        slice42g_integration_input_ref=integration_input.integration_input_id,
        slice42g_integration_result_ref=integration_result.result_id,
        slice42g_integration_receipt_ref=integration_result.receipt.receipt_id,
        successor_manifest_ref=integration_result.successor_manifest.manifest_id,
        lineage_id=outward.lineage_id,
        expression_link_ref=link.record_id,
        expression_candidate_ref=candidate.expression_candidate_id,
        realized_expression_ref=candidate.expression_candidate_id,
        expression_plan_ref=candidate.expression_plan_ref,
        governed_outward_meaning_ref=outward.record_id,
        preservation_obligation_package_ref=(
            objects["projection_result"].obligation_package.obligation_package_id
        ),
        realized_text_sha256=candidate.realized_text_sha256,
        realization_trace_ref=trace.realization_trace_id,
        realization_receipt_ref=receipt.realization_receipt_id,
        admitted_realization_rule_refs=(
            surface_input.realization_authority_record.admitted_rule_refs
        ),
        controlled_resource_refs=tuple(
            item.resource_record_id
            for item in surface_input.controlled_resource_bundle.records
        ),
        applied_rule_refs=candidate.applied_rule_refs,
        applied_resource_refs=candidate.applied_resource_refs,
        segment_refs=trace.segment_sha256s,
        version_refs=_unique(
            candidate.version_refs,
            integration_input.version_refs,
            ("MSM-v1", SLICE43C_SCHEMA_VERSION),
        ),
    )
    return with_expected_core_id(value)


def _build_package(
    request: SourceAdmissionRequest,
) -> EchoValidationAdmissionPackage:
    source = request.source_closeout_result
    objects = _source_objects(source)
    authorized_reference = _build_authorized_reference(objects)
    proposed_reference = _build_proposed_reference(objects)

    meaning_admission = with_expected_id(
        AuthorizedMeaningAdmissionRecord(
            admission_record_id="pending",
            request_ref=request.request_id,
            source_closeout_result_ref=source.result_id,
            source_acceptance_record_ref=source.acceptance_record.record_id,
            authorized_meaning_reference=authorized_reference,
            source_manifest_sha256=canonical_manifest_sha256(
                source.integration_result.source_manifest
            ),
            successor_manifest_sha256=canonical_manifest_sha256(
                source.integration_result.successor_manifest
            ),
            exact_accepted_ancestry_validated=True,
            identity_and_version_validated=True,
            source_admitted_for_later_comparison=True,
            raw_text_used=False,
            source_rewritten=False,
            alternatives_deleted=False,
            unresolved_conditions_resolved=False,
        )
    )
    expression_admission = with_expected_id(
        ProposedExpressionAdmissionRecord(
            admission_record_id="pending",
            request_ref=request.request_id,
            source_closeout_result_ref=source.result_id,
            proposed_expression_reference=proposed_reference,
            expression_candidate_authorized_for_admission=True,
            expression_candidate_already_delivered=False,
            expression_candidate_echo_approved=False,
            exact_expression_link_validated=True,
            exact_realization_identity_validated=True,
            source_admitted_for_later_comparison=True,
            expression_rewritten=False,
        )
    )
    boundary = EchoValidationInputBoundaryRecord(
        validation_input_boundary_id="pending",
        authorized_meaning_reference=authorized_reference,
        proposed_expression_reference=proposed_reference,
        custody_state=(
            EchoValidationInputCustodyState.READY_FOR_LATER_ADMISSION
        ),
        required_preservation_dimensions=tuple(PreservationDimension),
        predecessor_receipt_refs=(
            source.integration_result.receipt.receipt_id,
            source.integration_input.source_selected_meaning_integration_result.receipt.receipt_id,
            source.integration_input.surface_realization_result.realization_receipt.realization_receipt_id,
            source.acceptance_record.record_id,
            *(item.receipt_id for item in source.stage_receipts),
        ),
        authority_version_refs=(
            ("slice43c", SLICE43C_PROFILE_VERSION),
            ("slice42h", source.schema_version),
        ),
        schema_version_refs=(
            ("rmc_echo_runtime", authorized_reference.schema_version),
            ("slice43c", SLICE43C_SCHEMA_VERSION),
            ("msm", "MSM-v1"),
        ),
        later_admitter_ref=meaning_admission.admission_record_id,
    )
    boundary = with_expected_core_id(boundary)

    integration_result = source.integration_result
    source_trace_refs = (
        objects["selected_result"].semantic_transition_trace.record_id,
        integration_result.selected_to_outward_trace.record_id,
        integration_result.outward_to_expression_trace.record_id,
        objects["selected_result"].companion.selection_trace_ref,
        objects["selected_result"].companion.content_proof_ref,
        objects["selected_result"].receipt.receipt_id,
        integration_result.receipt.receipt_id,
        source.integration_input.surface_realization_result.realization_trace.realization_trace_id,
    )
    source_receipt_refs = (
        objects["selected_result"].receipt.receipt_id,
        source.integration_input.surface_realization_result.realization_receipt.realization_receipt_id,
        integration_result.receipt.receipt_id,
        source.acceptance_record.record_id,
        *(item.receipt_id for item in source.stage_receipts),
    )

    value = EchoValidationAdmissionPackage(
        admission_package_id="pending",
        admission_package_digest="0" * 64,
        request_ref=request.request_id,
        authorized_meaning_admission=meaning_admission,
        proposed_expression_admission=expression_admission,
        validation_input_boundary=boundary,
        source_closeout_result_ref=source.result_id,
        source_acceptance_record_ref=source.acceptance_record.record_id,
        source_manifest_ref=integration_result.source_manifest.manifest_id,
        successor_manifest_ref=integration_result.successor_manifest.manifest_id,
        source_trace_refs=tuple(dict.fromkeys(source_trace_refs)),
        source_receipt_refs=tuple(dict.fromkeys(source_receipt_refs)),
        required_preservation_dimension_values=tuple(
            item.value for item in PreservationDimension
        ),
        admitted_for_slice43d_comparison=True,
        exact_accepted_slice42_ancestry=True,
        duplicate_source_rejected=True,
        identity_collision_rejected=True,
        meaning_preservation_comparison_performed=False,
        validation_findings_created=False,
        drift_findings_created=False,
        materiality_decided=False,
        echo_disposition_decided=False,
        rejection_issued=False,
        containment_issued=False,
        msm_v1_modified_or_integrated=False,
        delivery_authorized_or_performed=False,
        truth_evidence_permission_execution_authority=False,
        route_api_network_filesystem_memory_tool_action_authority=False,
        model_or_similarity_authority_used=False,
        gp014_superseded=False,
    )
    return with_expected_package_identity(value)


def _held_result(
    request: object,
    codes: tuple[SourceAdmissionCode, ...],
    reason_refs: tuple[str, ...],
) -> SourceAdmissionResult:
    request_ref = (
        request.request_id
        if type(request) is SourceAdmissionRequest
        else "slice43c:unavailable-request"
    )
    source_ref = (
        request.source_closeout_result.result_id
        if (
            type(request) is SourceAdmissionRequest
            and hasattr(request.source_closeout_result, "result_id")
        )
        else "slice43c:unavailable-source"
    )
    value = SourceAdmissionResult(
        admission_result_id="pending",
        admission_result_digest="0" * 64,
        status=status_for_codes(codes),
        rejection_codes=codes,
        reason_refs=reason_refs,
        request_ref=request_ref,
        source_closeout_result_ref=source_ref,
        admission_package=None,
        source_admitted=False,
        exact_accepted_slice42_ancestry=False,
        selected_governed_meaning_admitted=False,
        governed_outward_meaning_admitted=False,
        realized_expression_candidate_admitted=False,
        msm_v1_expression_link_admitted=False,
        slice42_trace_and_custody_admitted=False,
        raw_text_admitted=False,
        orphan_expression_admitted=False,
        recomputed_or_fabricated_identity_admitted=False,
        unsupported_version_admitted=False,
        missing_link_admitted=False,
        already_delivered_candidate_admitted=False,
        unauthorized_candidate_admitted=False,
        meaning_preservation_comparison_performed=False,
        drift_classification_performed=False,
        echo_disposition_decided=False,
        rejection_or_containment_issued=False,
        msm_v1_modified_or_integrated=False,
        delivered=False,
        downstream_authority_created=False,
        model_or_similarity_authority_used=False,
        gp014_superseded=False,
    )
    return with_expected_result_identity(value)


def admit_authorized_meaning_and_proposed_expression(
    request: object,
) -> SourceAdmissionResult:
    report = validate_request(request)
    if not report.ok:
        codes = tuple(dict.fromkeys(item.code for item in report.issues))
        result = _held_result(
            request,
            codes,
            tuple(
                f"{item.path}:{item.code.value}:{item.detail}"
                for item in report.issues
            ),
        )
        assert validate_result(result).ok
        return result

    assert type(request) is SourceAdmissionRequest
    admission_package = _build_package(request)
    package_report = validate_admission_package(admission_package)
    if not package_report.ok:
        codes = tuple(dict.fromkeys(
            item.code for item in package_report.issues
        ))
        result = _held_result(
            request,
            codes,
            tuple(
                f"{item.path}:{item.code.value}:{item.detail}"
                for item in package_report.issues
            ),
        )
        assert validate_result(result).ok
        return result

    value = SourceAdmissionResult(
        admission_result_id="pending",
        admission_result_digest="0" * 64,
        status=SourceAdmissionStatus.ADMITTED,
        rejection_codes=(),
        reason_refs=(
            "slice43c:exact_accepted_slice42_ancestry",
            "slice43c:authorized_meaning_and_proposed_expression_admitted",
            "slice43d:meaning_preservation_comparison_still_required",
        ),
        request_ref=request.request_id,
        source_closeout_result_ref=request.source_closeout_result.result_id,
        admission_package=admission_package,
        source_admitted=True,
        exact_accepted_slice42_ancestry=True,
        selected_governed_meaning_admitted=True,
        governed_outward_meaning_admitted=True,
        realized_expression_candidate_admitted=True,
        msm_v1_expression_link_admitted=True,
        slice42_trace_and_custody_admitted=True,
        raw_text_admitted=False,
        orphan_expression_admitted=False,
        recomputed_or_fabricated_identity_admitted=False,
        unsupported_version_admitted=False,
        missing_link_admitted=False,
        already_delivered_candidate_admitted=False,
        unauthorized_candidate_admitted=False,
        meaning_preservation_comparison_performed=False,
        drift_classification_performed=False,
        echo_disposition_decided=False,
        rejection_or_containment_issued=False,
        msm_v1_modified_or_integrated=False,
        delivered=False,
        downstream_authority_created=False,
        model_or_similarity_authority_used=False,
        gp014_superseded=False,
    )
    result = with_expected_result_identity(value)
    result_report = validate_result(result)
    if not result_report.ok:
        raise RuntimeError(
            "constructed Slice 43C result failed self-validation: "
            + "; ".join(
                f"{item.path}:{item.code.value}"
                for item in result_report.issues
            )
        )
    return result


__all__ = (
    "admit_authorized_meaning_and_proposed_expression",
    "build_source_admission_request",
)
