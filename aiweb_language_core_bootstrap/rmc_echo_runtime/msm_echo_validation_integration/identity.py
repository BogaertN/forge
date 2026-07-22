"""Deterministic Slice 43G identities."""

from __future__ import annotations

from dataclasses import replace

from ...meaning_structure_manifest import (
    DeliveryContainmentLinkRecord,
    ExternalAuthorityReferenceRecord,
    SemanticTransitionTraceRecord,
    ValidationLinkRecord,
)
from ...meaning_structure_manifest.serialization import canonical_manifest_sha256
from .canonical import deterministic_digest, stable_identifier
from .schema import (
    MsmEchoValidationCustodyCompanionV1,
    MsmEchoValidationIntegrationInput,
    MsmEchoValidationIntegrationReceiptV1,
    MsmEchoValidationIntegrationResult,
)


def expected_input_id(value: MsmEchoValidationIntegrationInput) -> str:
    request_fields = tuple(
        (name, getattr(value, name))
        for name in value.__dataclass_fields__
        if name.endswith("_requested")
    )
    body = {
        "source_42g_input_ref": value.source_42g_input.integration_input_id,
        "source_42g_result_ref": value.source_42g_result.result_id,
        "source_42g_result_digest": value.source_42g_result.result_digest,
        "source_42g_successor_manifest_ref": (
            value.source_42g_result.successor_manifest.manifest_id
        ),
        "source_42g_successor_manifest_sha256": canonical_manifest_sha256(
            value.source_42g_result.successor_manifest
        ),
        "source_43e_result_ref": (
            value.source_43e_classification_result.classification_result_id
        ),
        "source_43e_result_digest": (
            value.source_43e_classification_result.classification_result_digest
        ),
        "source_43f_result_ref": (
            value.source_43f_disposition_result.disposition_result_id
        ),
        "source_43f_result_digest": (
            value.source_43f_disposition_result.disposition_result_digest
        ),
        "requested_operation": value.requested_operation,
        "explicit_integration_request": value.explicit_integration_request,
        "raw_text": value.raw_text,
        "validation_transition_reason": value.validation_transition_reason,
        "containment_transition_reason": value.containment_transition_reason,
        "request_fields": request_fields,
        "schema_version": value.schema_version,
        "profile_version": value.profile_version,
    }
    return stable_identifier("slice43g_integration_input", body)


def with_expected_input_id(value: MsmEchoValidationIntegrationInput):
    return replace(value, integration_input_id=expected_input_id(value))



def expected_authority_reference_id(value: ExternalAuthorityReferenceRecord) -> str:
    namespace = (
        "slice43g_echo_validation_authority_reference"
        if value.authority_kind.value == "rmc_echo_validator_receipt"
        else "slice43g_echo_containment_authority_reference"
    )
    return stable_identifier(
        namespace,
        {
            "lineage_id": value.lineage_id,
            "authority_kind": value.authority_kind.value,
            "external_object_ref": value.external_object_ref,
            "semantic_relevance": value.semantic_relevance,
            "schema_version": value.schema_version,
        },
    )

def expected_validation_link_id(value: ValidationLinkRecord) -> str:
    return stable_identifier(
        "slice43g_echo_validation_link",
        {
            "lineage_id": value.lineage_id,
            "expression_link_ref": value.expression_link_ref,
            "external_validation_receipt_ref": value.external_validation_receipt_ref,
            "external_validation_disposition": value.external_validation_disposition,
            "schema_version": value.schema_version,
        },
    )


def expected_containment_link_id(value: DeliveryContainmentLinkRecord) -> str:
    return stable_identifier(
        "slice43g_echo_containment_custody_link",
        {
            "lineage_id": value.lineage_id,
            "prior_link_ref": value.prior_link_ref,
            "disposition": value.disposition.value,
            "external_receipt_ref": value.external_receipt_ref,
            "schema_version": value.schema_version,
        },
    )


def expected_transition_trace_id(value: SemanticTransitionTraceRecord) -> str:
    namespace = (
        "slice43g_expression_to_validation_transition"
        if value.to_state.value == "validation_linked"
        else "slice43g_validation_to_containment_transition"
    )
    return stable_identifier(
        namespace,
        {
            "lineage_id": value.lineage_id,
            "from_record_ref": value.from_record_ref,
            "to_record_ref": value.to_record_ref,
            "from_state": value.from_state.value,
            "to_state": value.to_state.value,
            "transition_kind": value.transition_kind.value,
            "reason": value.reason,
            "authority_reference_ref": value.authority_reference_ref,
            "schema_version": value.schema_version,
        },
    )


def expected_successor_manifest_id(source, successor, value) -> str:
    return stable_identifier(
        "meaning_structure_manifest_slice43g_successor",
        {
            "source_manifest_id": source.manifest_id,
            "source_manifest_sha256": canonical_manifest_sha256(source),
            "source_42g_result": value.source_42g_result.result_id,
            "source_43e_result": (
                value.source_43e_classification_result.classification_result_id
            ),
            "source_43f_result": (
                value.source_43f_disposition_result.disposition_result_id
            ),
            "validation_link_refs": tuple(
                item.record_id for item in successor.validation_links
            ),
            "delivery_or_containment_refs": tuple(
                item.record_id for item in successor.delivery_or_containment_links
            ),
            "transition_trace_refs": tuple(
                item.record_id for item in successor.semantic_transition_traces
            ),
        },
    )


def expected_companion_id(value: MsmEchoValidationCustodyCompanionV1) -> str:
    body = {
        name: getattr(value, name)
        for name in value.__dataclass_fields__
        if name != "companion_id"
    }
    return stable_identifier("slice43g_msm_echo_validation_companion", body)


def with_expected_companion_id(value):
    return replace(value, companion_id=expected_companion_id(value))


def expected_receipt_id(value: MsmEchoValidationIntegrationReceiptV1) -> str:
    body = {
        name: getattr(value, name)
        for name in value.__dataclass_fields__
        if name != "receipt_id"
    }
    return stable_identifier("slice43g_msm_echo_validation_receipt", body)


def with_expected_receipt_id(value):
    return replace(value, receipt_id=expected_receipt_id(value))


def result_identity_body(value: MsmEchoValidationIntegrationResult):
    return {
        "integration_input_ref": value.integration_input_ref,
        "source_manifest_id": value.source_manifest.manifest_id,
        "source_manifest_sha256": canonical_manifest_sha256(value.source_manifest),
        "successor_manifest_id": value.successor_manifest.manifest_id,
        "successor_manifest_sha256": canonical_manifest_sha256(
            value.successor_manifest
        ),
        "validation_authority_ref": (
            None
            if value.validation_authority_reference_record is None
            else value.validation_authority_reference_record.record_id
        ),
        "containment_authority_ref": (
            None
            if value.containment_authority_reference_record is None
            else value.containment_authority_reference_record.record_id
        ),
        "validation_link_ref": (
            None
            if value.validation_link_record is None
            else value.validation_link_record.record_id
        ),
        "validation_trace_ref": (
            None
            if value.validation_transition_trace is None
            else value.validation_transition_trace.record_id
        ),
        "containment_link_ref": (
            None
            if value.containment_link_record is None
            else value.containment_link_record.record_id
        ),
        "containment_trace_ref": (
            None
            if value.containment_transition_trace is None
            else value.containment_transition_trace.record_id
        ),
        "companion_ref": (
            None if value.companion is None else value.companion.companion_id
        ),
        "receipt_ref": None if value.receipt is None else value.receipt.receipt_id,
        "validation_disposition": value.validation_disposition,
        "flags": tuple(
            (name, getattr(value, name))
            for name in value.__dataclass_fields__
            if name
            not in {
                "result_id",
                "result_digest",
                "source_manifest",
                "successor_manifest",
                "validation_authority_reference_record",
                "containment_authority_reference_record",
                "validation_link_record",
                "validation_transition_trace",
                "containment_link_record",
                "containment_transition_trace",
                "companion",
                "receipt",
            }
        ),
    }


def expected_result_digest(value: MsmEchoValidationIntegrationResult) -> str:
    return deterministic_digest(result_identity_body(value))


def expected_result_id(value: MsmEchoValidationIntegrationResult) -> str:
    return f"slice43g_msm_echo_validation_integration_result:{expected_result_digest(value)}"


def with_expected_result_identity(value):
    digest = expected_result_digest(value)
    return replace(
        value,
        result_digest=digest,
        result_id=f"slice43g_msm_echo_validation_integration_result:{digest}",
    )


__all__ = tuple(name for name in globals() if not name.startswith("_"))
