"""Deterministic identities for Slice 41E records."""
from __future__ import annotations

from dataclasses import replace

from ...meaning_structure_manifest import (
    ExternalAuthorityReferenceRecord,
    SelectedGovernedMeaningRecord,
    SemanticTransitionTraceRecord,
)
from ...meaning_structure_manifest.serialization import canonical_manifest_sha256
from .canonical import deterministic_digest, stable_identifier
from .schema import (
    MsmSelectedMeaningCustodyCompanionV1,
    MsmSelectedMeaningIntegrationAuthorityProfile,
    MsmSelectedMeaningIntegrationInput,
    MsmSelectedMeaningIntegrationReceiptV1,
    MsmSelectedMeaningIntegrationResult,
)


def expected_profile_id(value: MsmSelectedMeaningIntegrationAuthorityProfile) -> str:
    body = {name: getattr(value, name) for name in value.__dataclass_fields__ if name != "profile_id"}
    return stable_identifier("slice41e_authority_profile", body)


def with_expected_profile_id(value: MsmSelectedMeaningIntegrationAuthorityProfile) -> MsmSelectedMeaningIntegrationAuthorityProfile:
    return replace(value, profile_id=expected_profile_id(value))


def input_identity_body(value: MsmSelectedMeaningIntegrationInput) -> dict[str, object]:
    return {
        "source_gate_result": value.source_gate_integration_result.result_id,
        "source_manifest": value.source_gate_integration_result.successor_manifest_id,
        "slice40h_companion": value.source_gate_integration_result.companion.companion_id,
        "slice41d_input": value.selected_meaning_construction_input.construction_input_id,
        "slice41d_package": value.selected_meaning_package.package_id,
        "authority_profile": value.authority_profile.profile_id,
        "semantic_transition_reason": value.semantic_transition_reason,
        "version_refs": value.version_refs,
        "prohibited_requests": tuple(
            getattr(value, name)
            for name in (
                "msm_schema_rewrite_requested", "automatic_migration_requested",
                "candidate_deletion_requested", "non_selection_deletion_requested",
                "gate_custody_deletion_requested", "governed_result_requested",
                "outward_meaning_requested", "expression_link_requested",
                "validation_link_requested", "delivery_link_requested",
                "truth_claim_requested", "evidence_claim_requested",
                "permission_requested", "execution_requested", "route_requested",
                "tool_requested", "action_requested", "memory_access_requested",
                "memory_write_requested", "rendering_requested", "delivery_requested",
                "bootstrap_integration_requested",
            )
        ),
        "schema_version": value.schema_version,
    }


def expected_input_id(value: MsmSelectedMeaningIntegrationInput) -> str:
    return stable_identifier("slice41e_integration_input", input_identity_body(value))


def with_expected_input_id(value: MsmSelectedMeaningIntegrationInput) -> MsmSelectedMeaningIntegrationInput:
    return replace(value, integration_input_id=expected_input_id(value))


def expected_authority_reference_id(
    value: ExternalAuthorityReferenceRecord,
) -> str:
    return stable_identifier(
        "slice41e_selection_authority_reference",
        {
            "lineage_id": value.lineage_id,
            "authority_kind": value.authority_kind.value,
            "external_object_ref": value.external_object_ref,
            "semantic_relevance": value.semantic_relevance,
            "schema_version": value.schema_version,
        },
    )


def expected_selected_record_id(value: SelectedGovernedMeaningRecord) -> str:
    return stable_identifier(
        "slice41e_integrated_selected_governed_meaning",
        {
            "lineage_id": value.lineage_id,
            "selected_candidate_ref": value.selected_candidate_ref,
            "selection_authority_ref": value.selection_authority_ref,
            "communicative_act": value.communicative_act,
            "concept_refs": value.concept_refs,
            "relation_refs": value.relation_refs,
            "meaning_modifiers": value.meaning_modifiers,
            "inherited_limitations": value.inherited_limitations,
            "authority_sensitive_distinctions": value.authority_sensitive_distinctions,
            "preservation_classes": value.preservation_classes,
            "schema_version": value.schema_version,
        },
    )


def expected_transition_trace_id(value: SemanticTransitionTraceRecord) -> str:
    return stable_identifier(
        "slice41e_candidate_to_selected_transition",
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
    selected: SelectedGovernedMeaningRecord,
    authority: ExternalAuthorityReferenceRecord,
    trace: SemanticTransitionTraceRecord,
    value: MsmSelectedMeaningIntegrationInput,
) -> str:
    return stable_identifier(
        "meaning_structure_manifest_slice41e_successor",
        {
            "source_manifest_id": source_manifest.manifest_id,
            "source_manifest_sha256": canonical_manifest_sha256(source_manifest),
            "selected_record_id": selected.record_id,
            "authority_record_id": authority.record_id,
            "trace_record_id": trace.record_id,
            "slice40h_companion_id": value.slice40h_companion.companion_id,
            "slice41d_package_id": value.selected_meaning_package.package_id,
            "slice41d_receipt_id": value.selected_meaning_package.selection_receipt.receipt_id,
            "candidate_refs": tuple(item.record_id for item in source_manifest.candidate_meanings),
            "non_selection_refs": tuple(item.record_id for item in source_manifest.non_selection_outcomes),
        },
    )


def expected_companion_id(value: MsmSelectedMeaningCustodyCompanionV1) -> str:
    body = {name: getattr(value, name) for name in value.__dataclass_fields__ if name != "companion_id"}
    return stable_identifier("slice41e_msm_selected_meaning_companion", body)


def with_expected_companion_id(value: MsmSelectedMeaningCustodyCompanionV1) -> MsmSelectedMeaningCustodyCompanionV1:
    return replace(value, companion_id=expected_companion_id(value))


def expected_receipt_id(value: MsmSelectedMeaningIntegrationReceiptV1) -> str:
    body = {name: getattr(value, name) for name in value.__dataclass_fields__ if name != "receipt_id"}
    return stable_identifier("slice41e_msm_selected_meaning_receipt", body)


def with_expected_receipt_id(value: MsmSelectedMeaningIntegrationReceiptV1) -> MsmSelectedMeaningIntegrationReceiptV1:
    return replace(value, receipt_id=expected_receipt_id(value))


def result_identity_body(value: MsmSelectedMeaningIntegrationResult) -> dict[str, object]:
    return {
        "integration_input_ref": value.integration_input_ref,
        "source_manifest_id": value.source_manifest.manifest_id,
        "source_manifest_sha256": canonical_manifest_sha256(value.source_manifest),
        "successor_manifest_id": value.successor_manifest.manifest_id,
        "successor_manifest_sha256": canonical_manifest_sha256(value.successor_manifest),
        "authority_reference_record": value.authority_reference_record.record_id,
        "integrated_selected_meaning_record": value.integrated_selected_meaning_record.record_id,
        "semantic_transition_trace": value.semantic_transition_trace.record_id,
        "companion": value.companion.companion_id,
        "receipt": value.receipt.receipt_id,
        "flags": tuple(
            getattr(value, name)
            for name in value.__dataclass_fields__
            if name not in {
                "result_id", "canonical_digest", "integration_input_ref",
                "source_manifest", "successor_manifest", "authority_reference_record",
                "integrated_selected_meaning_record", "semantic_transition_trace",
                "companion", "receipt", "digest_algorithm", "schema_version",
            }
        ),
        "schema_version": value.schema_version,
    }


def expected_result_digest(value: MsmSelectedMeaningIntegrationResult) -> str:
    return deterministic_digest(result_identity_body(value))


def expected_result_id(value: MsmSelectedMeaningIntegrationResult) -> str:
    return stable_identifier(
        "slice41e_msm_selected_meaning_integration_result",
        {**result_identity_body(value), "canonical_digest": value.canonical_digest},
    )


def with_expected_result_identity(value: MsmSelectedMeaningIntegrationResult) -> MsmSelectedMeaningIntegrationResult:
    digest = expected_result_digest(value)
    provisional = replace(value, canonical_digest=digest)
    return replace(provisional, result_id=expected_result_id(provisional))


__all__ = tuple(name for name in globals() if name.startswith("expected_") or name.startswith("with_expected_") or name == "result_identity_body")
