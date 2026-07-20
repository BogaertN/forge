"""Exact additive Slice 41E integration into an immutable MSM-v1 successor."""
from __future__ import annotations

from dataclasses import replace

from ...meaning_structure_manifest import (
    ExternalAuthorityKind,
    ExternalAuthorityReferenceRecord,
    SelectedGovernedMeaningRecord,
    SemanticTransitionKind,
    SemanticTransitionTraceRecord,
)
from ...meaning_structure_manifest.lifecycle import append_lifecycle_successor
from ...meaning_structure_manifest.serialization import canonical_manifest_sha256
from .authority import (
    SLICE41E_COMPANION_VERSION,
    SLICE41E_RECEIPT_VERSION,
)
from .identity import (
    expected_authority_reference_id,
    expected_selected_record_id,
    expected_successor_manifest_id,
    expected_transition_trace_id,
    with_expected_companion_id,
    with_expected_receipt_id,
    with_expected_result_identity,
)
from .schema import (
    MsmSelectedMeaningCustodyCompanionV1,
    MsmSelectedMeaningIntegrationInput,
    MsmSelectedMeaningIntegrationReceiptV1,
    MsmSelectedMeaningIntegrationResult,
)
from .validation import (
    assert_valid_integration_input,
    assert_valid_integration_result,
)


def _candidate_ancestry(value: MsmSelectedMeaningIntegrationInput) -> tuple[str, ...]:
    package = value.selected_meaning_package
    companion = package.selected_candidate_companion
    return (
        package.selected_candidate_record.record_id,
        companion.companion_id,
        companion.candidate_meaning_id,
        companion.candidate_state_id,
        companion.candidate_identity_ref,
        companion.candidate_content_ref,
        companion.candidate_provenance_ref,
        companion.construction_receipt_ref,
        companion.construction_trace_reference_id,
        companion.provenance_reference_id,
        companion.limitation_reference_id,
        *companion.alternative_relationship_ids,
    )


def _gate_ancestry(value: MsmSelectedMeaningIntegrationInput) -> tuple[str, ...]:
    companion = value.slice40h_companion
    package = value.selected_meaning_package
    return (
        companion.companion_id,
        *(item.custody_id for item in companion.family_custody),
        *(item.result_id for item in companion.family_custody),
        companion.composition_result_id,
        *companion.composition_disposition_refs,
        package.selection_trace.gate_custody_ref,
        package.selection_trace.gate_composition_result_ref,
    )


def integrate_selected_meaning_into_manifest(
    value: MsmSelectedMeaningIntegrationInput,
) -> MsmSelectedMeaningIntegrationResult:
    """Return one deterministic additive MSM-v1 successor.

    The accepted source manifest and all of its existing records remain
    immutable.  Exactly one selection-authority reference, one selected record,
    and one candidate-to-selected transition trace are appended.
    """
    assert_valid_integration_input(value)
    source = value.source_manifest
    package = value.selected_meaning_package
    candidate = package.selected_candidate_record

    authority = ExternalAuthorityReferenceRecord(
        record_id="placeholder",
        lineage_id=source.lineage_root.lineage_id,
        authority_kind=ExternalAuthorityKind.INVOCATION_EXECUTION_OR_VERIFICATION_RECEIPT,
        external_object_ref=package.selection_receipt.receipt_id,
        semantic_relevance="slice41d_selection_authority_receipt",
    )
    authority = replace(authority, record_id=expected_authority_reference_id(authority))

    dormant = package.selected_meaning_record
    selected = SelectedGovernedMeaningRecord(
        record_id="placeholder",
        lineage_id=dormant.lineage_id,
        selected_candidate_ref=dormant.selected_candidate_ref,
        selection_authority_ref=package.selection_receipt.receipt_id,
        communicative_act=dormant.communicative_act,
        concept_refs=dormant.concept_refs,
        relation_refs=dormant.relation_refs,
        meaning_modifiers=dormant.meaning_modifiers,
        inherited_limitations=dormant.inherited_limitations,
        authority_sensitive_distinctions=dormant.authority_sensitive_distinctions,
        preservation_classes=dormant.preservation_classes,
    )
    selected = replace(selected, record_id=expected_selected_record_id(selected))

    authority_manifest = replace(
        source,
        manifest_id="slice41e_authority_augmented:" + authority.record_id.rsplit(":", 1)[-1],
        external_authority_references=(*source.external_authority_references, authority),
    )
    provisional_trace_id = expected_transition_trace_id(
        SemanticTransitionTraceRecord(
            record_id="placeholder",
            lineage_id=source.lineage_root.lineage_id,
            from_record_ref=candidate.record_id,
            to_record_ref=selected.record_id,
            from_state=candidate.lifecycle_state,
            to_state=selected.lifecycle_state,
            transition_kind=SemanticTransitionKind.ANCESTRY,
            reason=value.semantic_transition_reason,
            authority_reference_ref=authority.record_id,
        )
    )
    appended = append_lifecycle_successor(
        authority_manifest,
        trace_record_id=provisional_trace_id,
        from_record_ref=candidate.record_id,
        successor=selected,
        transition_kind=SemanticTransitionKind.ANCESTRY,
        reason=value.semantic_transition_reason,
        authority_reference_ref=authority.record_id,
    )
    trace = appended.trace
    successor_id = expected_successor_manifest_id(source, selected, authority, trace, value)
    successor = replace(appended.manifest, manifest_id=successor_id)

    candidate_before = tuple(item.record_id for item in source.candidate_meanings)
    candidate_after = tuple(item.record_id for item in successor.candidate_meanings)
    non_selection_before = tuple(item.record_id for item in source.non_selection_outcomes)
    non_selection_after = tuple(item.record_id for item in successor.non_selection_outcomes)

    companion = with_expected_companion_id(MsmSelectedMeaningCustodyCompanionV1(
        companion_id="placeholder",
        companion_version=SLICE41E_COMPANION_VERSION,
        integration_input_ref=value.integration_input_id,
        source_manifest_id=source.manifest_id,
        successor_manifest_id=successor.manifest_id,
        lineage_id=source.lineage_root.lineage_id,
        selected_candidate_ref=candidate.record_id,
        dormant_selected_meaning_ref=dormant.record_id,
        integrated_selected_meaning_ref=selected.record_id,
        selection_eligibility_result_ref=package.eligibility_result_ref,
        selection_decision_ref=package.decision_record.decision_id,
        selection_trace_ref=package.selection_trace.trace_id,
        selection_receipt_ref=package.selection_receipt.receipt_id,
        content_proof_ref=package.content_proof.proof_id,
        selection_authority_reference_record_ref=authority.record_id,
        slice40h_companion_ref=value.slice40h_companion.companion_id,
        slice40h_custody_companion=value.slice40h_companion,
        candidate_refs_before=candidate_before,
        candidate_refs_after=candidate_after,
        non_selection_outcome_refs_before=non_selection_before,
        non_selection_outcome_refs_after=non_selection_after,
        source_external_authority_refs=tuple(item.record_id for item in source.external_authority_references),
        added_external_authority_refs=(authority.record_id,),
        source_transition_trace_refs=tuple(item.record_id for item in source.semantic_transition_traces),
        added_transition_trace_refs=(trace.record_id,),
        preserved_alternative_refs=tuple(item.preservation_id for item in package.preserved_alternatives),
        unresolved_alternative_refs=package.unresolved_alternative_refs,
        candidate_ancestry_refs=_candidate_ancestry(value),
        gate_ancestry_refs=_gate_ancestry(value),
        exact_adapter=True,
        lossless_custody=True,
        immutable_successor=True,
        selected_record_integrated=True,
        selection_authority_receipt_bound=True,
        candidate_ancestry_preserved=True,
        gate_ancestry_preserved=True,
        all_candidate_meanings_retained=candidate_before == candidate_after,
        all_non_selection_outcomes_retained=non_selection_before == non_selection_after,
        slice40h_companion_retained=True,
        complete_successor_manifest_validated=True,
        msm_schema_modified=False,
        automatic_migration_performed=False,
    ))

    receipt = with_expected_receipt_id(MsmSelectedMeaningIntegrationReceiptV1(
        receipt_id="placeholder",
        receipt_version=SLICE41E_RECEIPT_VERSION,
        integration_input_ref=value.integration_input_id,
        source_manifest_ref=source.manifest_id,
        successor_manifest_ref=successor.manifest_id,
        source_gate_integration_result_ref=value.source_gate_integration_result.result_id,
        slice40h_companion_ref=value.slice40h_companion.companion_id,
        slice41d_package_ref=package.package_id,
        slice41d_selection_receipt_ref=package.selection_receipt.receipt_id,
        selection_authority_reference_record_ref=authority.record_id,
        selected_candidate_ref=candidate.record_id,
        integrated_selected_meaning_ref=selected.record_id,
        semantic_transition_trace_ref=trace.record_id,
        source_manifest_sha256=canonical_manifest_sha256(source),
        successor_manifest_sha256=canonical_manifest_sha256(successor),
        candidate_count_before=len(source.candidate_meanings),
        candidate_count_after=len(successor.candidate_meanings),
        non_selection_count_before=len(source.non_selection_outcomes),
        non_selection_count_after=len(successor.non_selection_outcomes),
        selected_count_before=len(source.selected_governed_meanings),
        selected_count_after=len(successor.selected_governed_meanings),
        deterministic=True,
        immutable_successor_created=True,
        selected_meaning_integrated=True,
        complete_manifest_validated=True,
        candidates_retained=True,
        non_selection_outcomes_retained=True,
        slice40h_companion_retained=True,
        msm_schema_modified=False,
        governed_outward_meaning_created=False,
        expression_link_created=False,
        validation_link_created=False,
        delivery_link_created=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        route_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_accessed=False,
        memory_written=False,
        rendered=False,
        delivered=False,
    ))

    result = with_expected_result_identity(MsmSelectedMeaningIntegrationResult(
        result_id="placeholder",
        canonical_digest="0" * 64,
        integration_input_ref=value.integration_input_id,
        source_manifest=source,
        successor_manifest=successor,
        authority_reference_record=authority,
        integrated_selected_meaning_record=selected,
        semantic_transition_trace=trace,
        companion=companion,
        receipt=receipt,
        deterministic=True,
        additive_only=True,
        immutable_successor_created=True,
        exact_slice40h_custody_preserved=True,
        exact_slice41d_package_preserved=True,
        exact_selected_candidate_preserved=True,
        exact_selection_receipt_bound=True,
        candidate_and_gate_ancestry_preserved=True,
        all_candidate_meanings_retained=True,
        all_non_selection_outcomes_retained=True,
        complete_successor_manifest_validated=True,
        selected_meaning_integrated=True,
        msm_schema_modified=False,
        automatic_migration_performed=False,
        candidate_deleted=False,
        non_selection_outcome_deleted=False,
        gate_custody_deleted=False,
        governed_result_reference_created=False,
        governed_outward_meaning_created=False,
        expression_link_created=False,
        validation_link_created=False,
        delivery_link_created=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        capability_availability_created=False,
        route_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_accessed=False,
        memory_written=False,
        rendered=False,
        delivered=False,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        external_resource_loaded=False,
        language_model_used=False,
        embedding_used=False,
        vector_used=False,
        rag_used=False,
        semantic_similarity_used=False,
        bootstrap_integration_enabled=False,
    ))
    assert_valid_integration_result(result, integration_input=value)
    return result


__all__ = ("integrate_selected_meaning_into_manifest",)
