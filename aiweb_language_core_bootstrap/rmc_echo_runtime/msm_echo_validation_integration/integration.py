"""Exact additive Slice 43G integration into an immutable MSM-v1 successor."""

from __future__ import annotations

from dataclasses import replace

from ...meaning_structure_manifest import (
    DeliveryContainmentKind,
    DeliveryContainmentLinkRecord,
    ExternalAuthorityKind,
    ExternalAuthorityReferenceRecord,
    SemanticTransitionKind,
    ValidationLinkRecord,
)
from ...meaning_structure_manifest.lifecycle import append_lifecycle_successor
from ...meaning_structure_manifest.serialization import canonical_manifest_sha256
from ..echo_disposition import EchoDisposition
from .authority import (
    CONTAINMENT_TRANSITION_REASON,
    REQUESTED_OPERATION,
    SLICE43G_COMPANION_VERSION,
    SLICE43G_RECEIPT_VERSION,
    VALIDATION_TRANSITION_REASON,
)
from .identity import (
    expected_authority_reference_id,
    expected_containment_link_id,
    expected_successor_manifest_id,
    expected_transition_trace_id,
    expected_validation_link_id,
    with_expected_companion_id,
    with_expected_input_id,
    with_expected_receipt_id,
    with_expected_result_identity,
)
from .rules import (
    authorized_trace_refs,
    containment_record_ref,
    exact_chain_is_proved,
    exact_disposition,
    rejection_record_ref,
    source_disposition_package,
    source_disposition_record,
    source_expression_candidate_ref,
    source_expression_link,
)
from .schema import (
    MsmEchoValidationCustodyCompanionV1,
    MsmEchoValidationIntegrationCode,
    MsmEchoValidationIntegrationInput,
    MsmEchoValidationIntegrationReceiptV1,
    MsmEchoValidationIntegrationResult,
    MsmEchoValidationIntegrationStatus,
)
from .validation import (
    assert_valid_integration_input,
    assert_valid_integration_result,
)


def build_integration_input(
    source_42g_input,
    source_42g_result,
    source_43e_classification_result,
    source_43f_disposition_result,
) -> MsmEchoValidationIntegrationInput:
    disposition = source_43f_disposition_result.disposition
    return with_expected_input_id(
        MsmEchoValidationIntegrationInput(
            integration_input_id="pending",
            source_42g_input=source_42g_input,
            source_42g_result=source_42g_result,
            source_43e_classification_result=source_43e_classification_result,
            source_43f_disposition_result=source_43f_disposition_result,
            requested_operation=REQUESTED_OPERATION,
            explicit_integration_request=True,
            raw_text=None,
            validation_transition_reason=VALIDATION_TRANSITION_REASON,
            containment_transition_reason=CONTAINMENT_TRANSITION_REASON,
            validation_link_creation_requested=True,
            containment_custody_requested=(
                disposition is EchoDisposition.CONTAINED
            ),
            rejection_custody_requested=(
                disposition is EchoDisposition.REJECTED
            ),
            delivery_link_creation_requested=False,
            candidate_rewrite_requested=False,
            drift_suppression_requested=False,
            delivery_requested=False,
            echoforge_requested=False,
            model_or_similarity_authority_requested=False,
            truth_evidence_permission_execution_requested=False,
            route_api_network_filesystem_memory_tool_action_requested=False,
            msm_schema_rewrite_requested=False,
            gp014_supersession_requested=False,
        )
    )


def construct_successor_artifacts(value: MsmEchoValidationIntegrationInput):
    source = value.source_42g_result.successor_manifest
    expression = source_expression_link(value)
    disposition_result = value.source_43f_disposition_result
    package = source_disposition_package(value)
    disposition_record = source_disposition_record(value)
    disposition = exact_disposition(value)

    validation_authority = ExternalAuthorityReferenceRecord(
        record_id="pending",
        lineage_id=source.lineage_root.lineage_id,
        authority_kind=ExternalAuthorityKind.RMC_ECHO_VALIDATOR_RECEIPT,
        external_object_ref=disposition_result.disposition_result_id,
        semantic_relevance=(
            "slice43f_exact_echo_disposition_receipt_for_slice43g_validation_custody"
        ),
    )
    validation_authority = replace(
        validation_authority,
        record_id=expected_authority_reference_id(validation_authority),
    )
    source_with_authority = replace(
        source,
        external_authority_references=(
            *source.external_authority_references,
            validation_authority,
        ),
    )

    validation = ValidationLinkRecord(
        record_id="pending",
        lineage_id=source.lineage_root.lineage_id,
        expression_link_ref=expression.record_id,
        external_validation_receipt_ref=disposition_result.disposition_result_id,
        external_validation_disposition=disposition.value,
    )
    validation = replace(
        validation,
        record_id=expected_validation_link_id(validation),
    )

    validation_probe = append_lifecycle_successor(
        source_with_authority,
        trace_record_id="slice43g-validation-trace-probe",
        from_record_ref=expression.record_id,
        successor=validation,
        transition_kind=SemanticTransitionKind.ANCESTRY,
        reason=value.validation_transition_reason,
        authority_reference_ref=validation_authority.record_id,
    )
    validation_trace = replace(
        validation_probe.trace,
        record_id=expected_transition_trace_id(validation_probe.trace),
    )
    validation_append = append_lifecycle_successor(
        source_with_authority,
        trace_record_id=validation_trace.record_id,
        from_record_ref=expression.record_id,
        successor=validation,
        transition_kind=SemanticTransitionKind.ANCESTRY,
        reason=value.validation_transition_reason,
        authority_reference_ref=validation_authority.record_id,
    )
    successor = validation_append.manifest
    containment_authority = None
    containment = None
    containment_trace = None

    if disposition is EchoDisposition.CONTAINED:
        containment_ref = containment_record_ref(value)
        if containment_ref is None:
            raise ValueError("CONTAINED disposition requires exact containment record")
        containment_authority = ExternalAuthorityReferenceRecord(
            record_id="pending",
            lineage_id=source.lineage_root.lineage_id,
            authority_kind=ExternalAuthorityKind.DELIVERY_OR_CONTAINMENT_RECEIPT,
            external_object_ref=containment_ref,
            semantic_relevance=(
                "slice43f_exact_containment_record_for_slice43g_containment_custody"
            ),
        )
        containment_authority = replace(
            containment_authority,
            record_id=expected_authority_reference_id(containment_authority),
        )
        successor = replace(
            successor,
            external_authority_references=(
                *successor.external_authority_references,
                containment_authority,
            ),
        )
        containment = DeliveryContainmentLinkRecord(
            record_id="pending",
            lineage_id=source.lineage_root.lineage_id,
            prior_link_ref=validation.record_id,
            disposition=DeliveryContainmentKind.CONTAINMENT_LINKED,
            external_receipt_ref=containment_ref,
        )
        containment = replace(
            containment,
            record_id=expected_containment_link_id(containment),
        )
        containment_probe = append_lifecycle_successor(
            successor,
            trace_record_id="slice43g-containment-trace-probe",
            from_record_ref=validation.record_id,
            successor=containment,
            transition_kind=SemanticTransitionKind.CONTAINMENT,
            reason=value.containment_transition_reason,
            authority_reference_ref=containment_authority.record_id,
        )
        containment_trace = replace(
            containment_probe.trace,
            record_id=expected_transition_trace_id(containment_probe.trace),
        )
        containment_append = append_lifecycle_successor(
            successor,
            trace_record_id=containment_trace.record_id,
            from_record_ref=validation.record_id,
            successor=containment,
            transition_kind=SemanticTransitionKind.CONTAINMENT,
            reason=value.containment_transition_reason,
            authority_reference_ref=containment_authority.record_id,
        )
        successor = containment_append.manifest

    successor = replace(
        successor,
        manifest_id=expected_successor_manifest_id(source, successor, value),
    )
    return (
        validation_authority,
        containment_authority,
        validation,
        validation_trace,
        containment,
        containment_trace,
        successor,
        package,
        disposition_record,
    )


def integrate_echo_validation_link(
    value: MsmEchoValidationIntegrationInput,
) -> MsmEchoValidationIntegrationResult:
    assert_valid_integration_input(value)
    (
        validation_authority,
        containment_authority,
        validation,
        validation_trace,
        containment,
        containment_trace,
        successor,
        package,
        disposition_record,
    ) = construct_successor_artifacts(value)
    source = value.source_42g_result.successor_manifest
    disposition = exact_disposition(value)
    rejection_ref = rejection_record_ref(value)
    containment_ref = containment_record_ref(value)
    trace_refs = authorized_trace_refs(value)

    companion = with_expected_companion_id(
        MsmEchoValidationCustodyCompanionV1(
            companion_id="pending",
            companion_version=SLICE43G_COMPANION_VERSION,
            integration_input_ref=value.integration_input_id,
            source_manifest_ref=source.manifest_id,
            successor_manifest_ref=successor.manifest_id,
            source_expression_link_ref=source_expression_link(value).record_id,
            source_expression_candidate_ref=source_expression_candidate_ref(value),
            source_43e_classification_result_ref=(
                value.source_43e_classification_result.classification_result_id
            ),
            source_43f_disposition_result_ref=(
                value.source_43f_disposition_result.disposition_result_id
            ),
            source_43f_disposition_package_ref=package.disposition_package_id,
            source_43f_disposition_record_ref=disposition_record.disposition_id,
            validation_authority_reference_ref=validation_authority.record_id,
            containment_authority_reference_ref=(
                None if containment_authority is None else containment_authority.record_id
            ),
            exact_validation_link_ref=validation.record_id,
            exact_validation_disposition=disposition,
            validation_trace_ref=validation_trace.record_id,
            rejection_record_ref=rejection_ref,
            containment_record_ref=containment_ref,
            containment_link_ref=(
                None if containment is None else containment.record_id
            ),
            containment_trace_ref=(
                None if containment_trace is None else containment_trace.record_id
            ),
            authorized_trace_refs=trace_refs,
            source_validation_link_refs=tuple(
                item.record_id for item in source.validation_links
            ),
            successor_validation_link_refs=tuple(
                item.record_id for item in successor.validation_links
            ),
            source_delivery_or_containment_refs=tuple(
                item.record_id for item in source.delivery_or_containment_links
            ),
            successor_delivery_or_containment_refs=tuple(
                item.record_id
                for item in successor.delivery_or_containment_links
            ),
            immutable_successor=True,
            additive_only=True,
            exact_chain_proved=exact_chain_is_proved(value),
            dormant_validation_record_used=True,
            rejection_custody_preserved=(
                disposition is not EchoDisposition.REJECTED
                or rejection_ref is not None
            ),
            containment_custody_preserved=(
                disposition is not EchoDisposition.CONTAINED
                or (
                    containment_ref is not None
                    and containment is not None
                    and containment_trace is not None
                )
            ),
            delivery_link_created=False,
            source_manifest_mutated=False,
        )
    )

    receipt = with_expected_receipt_id(
        MsmEchoValidationIntegrationReceiptV1(
            receipt_id="pending",
            receipt_version=SLICE43G_RECEIPT_VERSION,
            integration_input_ref=value.integration_input_id,
            source_manifest_ref=source.manifest_id,
            successor_manifest_ref=successor.manifest_id,
            source_manifest_sha256=canonical_manifest_sha256(source),
            successor_manifest_sha256=canonical_manifest_sha256(successor),
            validation_authority_reference_ref=validation_authority.record_id,
            containment_authority_reference_ref=(
                None if containment_authority is None else containment_authority.record_id
            ),
            validation_link_ref=validation.record_id,
            validation_disposition=disposition,
            validation_receipt_ref=(
                value.source_43f_disposition_result.disposition_result_id
            ),
            validation_trace_ref=validation_trace.record_id,
            rejection_record_ref=rejection_ref,
            containment_record_ref=containment_ref,
            containment_link_ref=(
                None if containment is None else containment.record_id
            ),
            containment_trace_ref=(
                None if containment_trace is None else containment_trace.record_id
            ),
            authorized_trace_refs=trace_refs,
            delivery_link_created=False,
            delivery_authorized_or_performed=False,
            candidate_rewritten_or_repaired=False,
            drift_removed_downgraded_or_suppressed=False,
            echoforge_called=False,
            model_or_similarity_authority_used=False,
            truth_evidence_permission_execution_authority=False,
            route_api_network_filesystem_memory_tool_action_authority=False,
            msm_schema_modified=False,
            gp014_superseded=False,
        )
    )

    result = with_expected_result_identity(
        MsmEchoValidationIntegrationResult(
            result_id="pending",
            result_digest="pending",
            status=MsmEchoValidationIntegrationStatus.SUCCESSOR_CREATED,
            issue_codes=(),
            reason_refs=(
                f"slice43g:validation-disposition:{disposition.value}",
                "slice43g:immutable-additive-msm-successor",
                "slice43g:no-delivery-link",
            ),
            integration_input_ref=value.integration_input_id,
            source_manifest=source,
            successor_manifest=successor,
            validation_authority_reference_record=validation_authority,
            containment_authority_reference_record=containment_authority,
            validation_link_record=validation,
            validation_transition_trace=validation_trace,
            containment_link_record=containment,
            containment_transition_trace=containment_trace,
            companion=companion,
            receipt=receipt,
            validation_disposition=disposition,
            immutable_successor_created=True,
            additive_only=True,
            exact_chain_proved=True,
            validation_link_created=True,
            rejection_custody_preserved=(
                disposition is not EchoDisposition.REJECTED
                or rejection_ref is not None
            ),
            containment_custody_preserved=(
                disposition is not EchoDisposition.CONTAINED
                or containment is not None
            ),
            delivery_link_created=False,
            delivery_authorized_or_performed=False,
            candidate_rewritten_or_repaired=False,
            drift_removed_downgraded_or_suppressed=False,
            echoforge_called=False,
            model_or_similarity_authority_used=False,
            truth_evidence_permission_execution_authority=False,
            route_api_network_filesystem_memory_tool_action_authority=False,
            msm_schema_modified=False,
            gp014_superseded=False,
        )
    )
    assert_valid_integration_result(result, integration_input=value)
    return result


__all__ = (
    "build_integration_input",
    "construct_successor_artifacts",
    "integrate_echo_validation_link",
)
