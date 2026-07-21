"""Deterministic identities for Slice 42G records."""

from __future__ import annotations

from dataclasses import replace

from ...meaning_structure_manifest import (
    ExpressionLinkRecord,
    ExternalAuthorityReferenceRecord,
    GovernedOutwardMeaningRecord,
    SemanticTransitionTraceRecord,
)
from ...meaning_structure_manifest.serialization import canonical_manifest_sha256
from .canonical import deterministic_digest, stable_identifier
from .schema import (
    MsmOutwardExpressionCustodyCompanionV1,
    MsmOutwardExpressionIntegrationAuthorityProfile,
    MsmOutwardExpressionIntegrationInput,
    MsmOutwardExpressionIntegrationReceiptV1,
    MsmOutwardExpressionIntegrationResult,
)


def expected_profile_id(
    value: MsmOutwardExpressionIntegrationAuthorityProfile,
) -> str:
    body = {
        name: getattr(value, name)
        for name in value.__dataclass_fields__
        if name != "profile_id"
    }
    return stable_identifier("slice42g_authority_profile", body)


def with_expected_profile_id(
    value: MsmOutwardExpressionIntegrationAuthorityProfile,
) -> MsmOutwardExpressionIntegrationAuthorityProfile:
    return replace(value, profile_id=expected_profile_id(value))


def input_identity_body(
    value: MsmOutwardExpressionIntegrationInput,
) -> dict[str, object]:
    prohibited_names = tuple(
        name
        for name in value.__dataclass_fields__
        if name.endswith("_requested")
    )
    return {
        "source_slice41e_input": (
            value.source_selected_meaning_integration_input.integration_input_id
        ),
        "source_slice41e_result": (
            value.source_selected_meaning_integration_result.result_id
        ),
        "source_manifest": value.source_manifest.manifest_id,
        "source_manifest_sha256": canonical_manifest_sha256(value.source_manifest),
        "surface_realization_input": value.surface_realization_input.realization_input_id,
        "surface_realization_result": value.surface_realization_result.result_id,
        "expression_candidate": value.expression_candidate.expression_candidate_id,
        "authority_profile": value.authority_profile.profile_id,
        "outward_transition_reason": value.outward_transition_reason,
        "expression_transition_reason": value.expression_transition_reason,
        "version_refs": value.version_refs,
        "prohibited_requests": tuple(
            (name, getattr(value, name)) for name in prohibited_names
        ),
        "schema_version": value.schema_version,
    }


def expected_input_id(value: MsmOutwardExpressionIntegrationInput) -> str:
    return stable_identifier("slice42g_integration_input", input_identity_body(value))


def with_expected_input_id(
    value: MsmOutwardExpressionIntegrationInput,
) -> MsmOutwardExpressionIntegrationInput:
    return replace(value, integration_input_id=expected_input_id(value))


def expected_authority_reference_id(
    value: ExternalAuthorityReferenceRecord,
) -> str:
    return stable_identifier(
        "slice42g_surface_realization_authority_reference",
        {
            "lineage_id": value.lineage_id,
            "authority_kind": value.authority_kind.value,
            "external_object_ref": value.external_object_ref,
            "semantic_relevance": value.semantic_relevance,
            "schema_version": value.schema_version,
        },
    )


def expected_outward_meaning_id(value: GovernedOutwardMeaningRecord) -> str:
    return stable_identifier(
        "slice42g_integrated_governed_outward_meaning",
        {
            "lineage_id": value.lineage_id,
            "outward_basis_refs": value.outward_basis_refs,
            "prior_selected_meaning_ref": value.prior_selected_meaning_ref,
            "permitted_claims": value.permitted_claims,
            "required_qualifications": value.required_qualifications,
            "prohibited_enlargements": value.prohibited_enlargements,
            "external_dependency_refs": value.external_dependency_refs,
            "preservation_classes": value.preservation_classes,
            "schema_version": value.schema_version,
        },
    )


def expected_expression_link_id(value: ExpressionLinkRecord) -> str:
    return stable_identifier(
        "slice42g_integrated_expression_link",
        {
            "lineage_id": value.lineage_id,
            "governed_outward_meaning_ref": value.governed_outward_meaning_ref,
            "expression_candidate_ref": value.expression_candidate_ref,
            "schema_version": value.schema_version,
        },
    )


def expected_transition_trace_id(
    value: SemanticTransitionTraceRecord,
) -> str:
    namespace = (
        "slice42g_selected_to_outward_transition"
        if value.to_state.value == "governed_outward_meaning"
        else "slice42g_outward_to_expression_transition"
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


def expected_successor_manifest_id(
    source_manifest,
    authority: ExternalAuthorityReferenceRecord,
    outward: GovernedOutwardMeaningRecord,
    expression: ExpressionLinkRecord,
    selected_trace: SemanticTransitionTraceRecord,
    expression_trace: SemanticTransitionTraceRecord,
    value: MsmOutwardExpressionIntegrationInput,
) -> str:
    return stable_identifier(
        "meaning_structure_manifest_slice42g_successor",
        {
            "source_manifest_id": source_manifest.manifest_id,
            "source_manifest_sha256": canonical_manifest_sha256(source_manifest),
            "source_slice41e_result": (
                value.source_selected_meaning_integration_result.result_id
            ),
            "source_slice42f_result": value.surface_realization_result.result_id,
            "surface_realization_receipt": (
                value.surface_realization_result.realization_receipt.realization_receipt_id
            ),
            "expression_candidate": value.expression_candidate.expression_candidate_id,
            "authority_record": authority.record_id,
            "outward_record": outward.record_id,
            "expression_link": expression.record_id,
            "selected_trace": selected_trace.record_id,
            "expression_trace": expression_trace.record_id,
            "candidate_refs": tuple(
                item.record_id for item in source_manifest.candidate_meanings
            ),
            "non_selection_refs": tuple(
                item.record_id for item in source_manifest.non_selection_outcomes
            ),
            "selected_refs": tuple(
                item.record_id for item in source_manifest.selected_governed_meanings
            ),
        },
    )


def expected_companion_id(value: MsmOutwardExpressionCustodyCompanionV1) -> str:
    body = {
        name: getattr(value, name)
        for name in value.__dataclass_fields__
        if name != "companion_id"
    }
    return stable_identifier("slice42g_msm_outward_expression_companion", body)


def with_expected_companion_id(
    value: MsmOutwardExpressionCustodyCompanionV1,
) -> MsmOutwardExpressionCustodyCompanionV1:
    return replace(value, companion_id=expected_companion_id(value))


def expected_receipt_id(
    value: MsmOutwardExpressionIntegrationReceiptV1,
) -> str:
    body = {
        name: getattr(value, name)
        for name in value.__dataclass_fields__
        if name != "receipt_id"
    }
    return stable_identifier("slice42g_msm_outward_expression_receipt", body)


def with_expected_receipt_id(
    value: MsmOutwardExpressionIntegrationReceiptV1,
) -> MsmOutwardExpressionIntegrationReceiptV1:
    return replace(value, receipt_id=expected_receipt_id(value))


def result_identity_body(
    value: MsmOutwardExpressionIntegrationResult,
) -> dict[str, object]:
    excluded = {
        "result_id",
        "result_digest",
        "source_manifest",
        "successor_manifest",
        "external_authority_reference_record",
        "governed_outward_meaning_record",
        "expression_link_record",
        "selected_to_outward_trace",
        "outward_to_expression_trace",
        "companion",
        "receipt",
        "digest_algorithm",
        "schema_version",
    }
    return {
        "integration_input_ref": value.integration_input_ref,
        "source_manifest_id": value.source_manifest.manifest_id,
        "source_manifest_sha256": canonical_manifest_sha256(value.source_manifest),
        "successor_manifest_id": value.successor_manifest.manifest_id,
        "successor_manifest_sha256": canonical_manifest_sha256(value.successor_manifest),
        "authority_record": value.external_authority_reference_record.record_id,
        "outward_record": value.governed_outward_meaning_record.record_id,
        "expression_link": value.expression_link_record.record_id,
        "selected_trace": value.selected_to_outward_trace.record_id,
        "expression_trace": value.outward_to_expression_trace.record_id,
        "companion": value.companion.companion_id,
        "receipt": value.receipt.receipt_id,
        "flags": tuple(
            (name, getattr(value, name))
            for name in value.__dataclass_fields__
            if name not in excluded
        ),
        "digest_algorithm": value.digest_algorithm,
        "schema_version": value.schema_version,
    }


def expected_result_digest(
    value: MsmOutwardExpressionIntegrationResult,
) -> str:
    return deterministic_digest(result_identity_body(value))


def expected_result_id(value: MsmOutwardExpressionIntegrationResult) -> str:
    return stable_identifier(
        "slice42g_msm_outward_expression_integration_result",
        {
            **result_identity_body(value),
            "result_digest": value.result_digest,
        },
    )


def with_expected_result_identity(
    value: MsmOutwardExpressionIntegrationResult,
) -> MsmOutwardExpressionIntegrationResult:
    digest = expected_result_digest(value)
    provisional = replace(value, result_digest=digest)
    return replace(provisional, result_id=expected_result_id(provisional))


__all__ = tuple(
    name
    for name in globals()
    if name.startswith("expected_")
    or name.startswith("with_expected_")
    or name in {"input_identity_body", "result_identity_body"}
)
