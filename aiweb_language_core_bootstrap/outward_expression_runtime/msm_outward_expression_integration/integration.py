"""Exact additive Slice 42G integration into an immutable MSM-v1 successor."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from ...meaning_structure_manifest import (
    ExpressionLinkRecord,
    ExternalAuthorityKind,
    ExternalAuthorityReferenceRecord,
    GovernedOutwardMeaningRecord,
    SemanticPreservationClass,
    SemanticTransitionKind,
    SemanticTransitionTraceRecord,
)
from ...meaning_structure_manifest.lifecycle import append_lifecycle_successor
from ...meaning_structure_manifest.serialization import canonical_manifest_sha256
from .authority import (
    SLICE42G_COMPANION_VERSION,
    SLICE42G_RECEIPT_VERSION,
)
from .canonical import stable_identifier
from .identity import (
    expected_authority_reference_id,
    expected_expression_link_id,
    expected_outward_meaning_id,
    expected_successor_manifest_id,
    expected_transition_trace_id,
    with_expected_companion_id,
    with_expected_receipt_id,
    with_expected_result_identity,
)
from .schema import (
    MsmOutwardExpressionCustodyCompanionV1,
    MsmOutwardExpressionIntegrationInput,
    MsmOutwardExpressionIntegrationReceiptV1,
    MsmOutwardExpressionIntegrationResult,
)


def _unique(*groups: Iterable[str]) -> tuple[str, ...]:
    ordered: dict[str, None] = {}
    for group in groups:
        for item in group:
            ordered.setdefault(item, None)
    return tuple(ordered)


def derive_outward_meaning_fields(
    value: MsmOutwardExpressionIntegrationInput,
) -> dict[str, object]:
    candidate = value.expression_candidate
    realization_result = value.surface_realization_result
    selected = (
        value.source_selected_meaning_integration_result
        .integrated_selected_meaning_record
    )
    affirmative = candidate.disposition.value == "authorized_expression_candidate"
    permitted_claims = _unique(
        candidate.selected_meaning_refs,
        candidate.active_scope_refs,
        (
            f"surface-realization-disposition:{candidate.disposition.value}",
            f"affirmative-claim-authorized:{str(affirmative).lower()}",
        ),
    )
    required_qualifications = _unique(
        candidate.certainty_level_refs,
        candidate.evidence_status_refs,
        candidate.meaning_modifier_refs,
        candidate.inherited_limitation_refs,
        candidate.required_qualification_refs,
        candidate.required_caveat_refs,
        candidate.refusal_relevant_boundary_refs,
        candidate.unresolved_condition_refs,
        candidate.ambiguity_refs,
        candidate.unsupported_state_refs,
        candidate.memory_authority_refs,
        candidate.external_resource_status_refs,
        candidate.delivery_authority_refs,
        candidate.privacy_identity_boundary_refs,
    )
    prohibited_enlargements = _unique(
        realization_result.permanent_boundaries,
        realization_result.prohibited_authority,
        (
            "expression-candidate:unvalidated",
            "echo-validation:not-performed",
            "delivery:not-authorized",
            "truth-evidence-permission-execution:not-granted",
        ),
    )
    preservation_classes = tuple(
        SemanticPreservationClass(item)
        for item in candidate.preservation_class_refs
    )
    return {
        "lineage_id": selected.lineage_id,
        "prior_selected_meaning_ref": selected.record_id,
        "permitted_claims": permitted_claims,
        "required_qualifications": required_qualifications,
        "prohibited_enlargements": prohibited_enlargements,
        "preservation_classes": preservation_classes,
    }


def build_external_authority_reference(
    value: MsmOutwardExpressionIntegrationInput,
) -> ExternalAuthorityReferenceRecord:
    source = value.source_manifest
    candidate = value.expression_candidate
    authority = ExternalAuthorityReferenceRecord(
        record_id="pending",
        lineage_id=source.lineage_root.lineage_id,
        authority_kind=ExternalAuthorityKind.RENDER_PREVIEW_OR_OUTPUT_OBJECT,
        external_object_ref=candidate.expression_candidate_id,
        semantic_relevance=(
            "slice42f_unvalidated_expression_candidate_custody_not_validation_or_delivery"
        ),
    )
    return replace(
        authority,
        record_id=expected_authority_reference_id(authority),
    )


def build_governed_outward_meaning(
    value: MsmOutwardExpressionIntegrationInput,
    authority: ExternalAuthorityReferenceRecord,
) -> GovernedOutwardMeaningRecord:
    selected = (
        value.source_selected_meaning_integration_result
        .integrated_selected_meaning_record
    )
    fields = derive_outward_meaning_fields(value)
    outward = GovernedOutwardMeaningRecord(
        record_id="pending",
        lineage_id=fields["lineage_id"],
        outward_basis_refs=(selected.record_id, authority.record_id),
        prior_selected_meaning_ref=fields["prior_selected_meaning_ref"],
        permitted_claims=fields["permitted_claims"],
        required_qualifications=fields["required_qualifications"],
        prohibited_enlargements=fields["prohibited_enlargements"],
        external_dependency_refs=(authority.record_id,),
        preservation_classes=fields["preservation_classes"],
    )
    return replace(
        outward,
        record_id=expected_outward_meaning_id(outward),
    )


def build_expression_link(
    value: MsmOutwardExpressionIntegrationInput,
    outward: GovernedOutwardMeaningRecord,
) -> ExpressionLinkRecord:
    expression = ExpressionLinkRecord(
        record_id="pending",
        lineage_id=outward.lineage_id,
        governed_outward_meaning_ref=outward.record_id,
        expression_candidate_ref=value.expression_candidate.expression_candidate_id,
    )
    return replace(
        expression,
        record_id=expected_expression_link_id(expression),
    )


def construct_successor_artifacts(
    value: MsmOutwardExpressionIntegrationInput,
):
    source = value.source_manifest
    selected = (
        value.source_selected_meaning_integration_result
        .integrated_selected_meaning_record
    )
    authority = build_external_authority_reference(value)
    outward = build_governed_outward_meaning(value, authority)
    expression = build_expression_link(value, outward)

    authority_manifest = replace(
        source,
        manifest_id=stable_identifier(
            "slice42g_authority_augmented_manifest",
            {
                "source_manifest_id": source.manifest_id,
                "authority_record_id": authority.record_id,
            },
        ),
        external_authority_references=(
            *source.external_authority_references,
            authority,
        ),
    )

    selected_trace_shape = SemanticTransitionTraceRecord(
        record_id="pending",
        lineage_id=source.lineage_root.lineage_id,
        from_record_ref=selected.record_id,
        to_record_ref=outward.record_id,
        from_state=selected.lifecycle_state,
        to_state=outward.lifecycle_state,
        transition_kind=SemanticTransitionKind.ANCESTRY,
        reason=value.outward_transition_reason,
        authority_reference_ref=authority.record_id,
    )
    selected_trace_id = expected_transition_trace_id(selected_trace_shape)
    selected_append = append_lifecycle_successor(
        authority_manifest,
        trace_record_id=selected_trace_id,
        from_record_ref=selected.record_id,
        successor=outward,
        transition_kind=SemanticTransitionKind.ANCESTRY,
        reason=value.outward_transition_reason,
        authority_reference_ref=authority.record_id,
    )

    expression_trace_shape = SemanticTransitionTraceRecord(
        record_id="pending",
        lineage_id=source.lineage_root.lineage_id,
        from_record_ref=outward.record_id,
        to_record_ref=expression.record_id,
        from_state=outward.lifecycle_state,
        to_state=expression.lifecycle_state,
        transition_kind=SemanticTransitionKind.ANCESTRY,
        reason=value.expression_transition_reason,
        authority_reference_ref=authority.record_id,
    )
    expression_trace_id = expected_transition_trace_id(expression_trace_shape)
    expression_append = append_lifecycle_successor(
        selected_append.manifest,
        trace_record_id=expression_trace_id,
        from_record_ref=outward.record_id,
        successor=expression,
        transition_kind=SemanticTransitionKind.ANCESTRY,
        reason=value.expression_transition_reason,
        authority_reference_ref=authority.record_id,
    )

    successor_id = expected_successor_manifest_id(
        source,
        authority,
        outward,
        expression,
        selected_append.trace,
        expression_append.trace,
        value,
    )
    successor = replace(
        expression_append.manifest,
        manifest_id=successor_id,
    )
    return (
        authority,
        outward,
        expression,
        selected_append.trace,
        expression_append.trace,
        successor,
    )


def _record_ids(records) -> tuple[str, ...]:
    return tuple(item.record_id for item in records)


def _preserved_alternative_refs(
    value: MsmOutwardExpressionIntegrationInput,
) -> tuple[str, ...]:
    source = value.source_manifest
    selected = (
        value.source_selected_meaning_integration_result
        .integrated_selected_meaning_record
    )
    candidate_alternatives = tuple(
        item.record_id
        for item in source.candidate_meanings
        if item.record_id != selected.selected_candidate_ref
    )
    non_selection = _record_ids(source.non_selection_outcomes)
    return _unique(candidate_alternatives, non_selection)


def _ancestry_refs(
    value: MsmOutwardExpressionIntegrationInput,
    authority: ExternalAuthorityReferenceRecord,
    outward: GovernedOutwardMeaningRecord,
    expression: ExpressionLinkRecord,
    selected_trace: SemanticTransitionTraceRecord,
    expression_trace: SemanticTransitionTraceRecord,
) -> tuple[str, ...]:
    selected_result = value.source_selected_meaning_integration_result
    candidate = value.expression_candidate
    realization_result = value.surface_realization_result
    trace = realization_result.realization_trace
    receipt = realization_result.realization_receipt
    assert trace is not None and receipt is not None
    return _unique(
        candidate.ancestry_refs,
        candidate.predecessor_receipt_refs,
        (
            selected_result.result_id,
            selected_result.receipt.receipt_id,
            selected_result.integrated_selected_meaning_record.record_id,
            realization_result.result_id,
            candidate.expression_candidate_id,
            trace.realization_trace_id,
            receipt.realization_receipt_id,
            authority.record_id,
            outward.record_id,
            expression.record_id,
            selected_trace.record_id,
            expression_trace.record_id,
        ),
    )


def integrate_outward_meaning_and_expression_link(
    value: MsmOutwardExpressionIntegrationInput,
) -> MsmOutwardExpressionIntegrationResult:
    """Return one exact additive immutable MSM-v1 successor."""

    from .validation import (
        assert_valid_integration_input,
        assert_valid_integration_result,
    )

    assert_valid_integration_input(value)
    source = value.source_manifest
    selected_result = value.source_selected_meaning_integration_result
    realization_result = value.surface_realization_result
    candidate = value.expression_candidate
    realization_trace = realization_result.realization_trace
    realization_receipt = realization_result.realization_receipt
    assert realization_trace is not None and realization_receipt is not None

    (
        authority,
        outward,
        expression,
        selected_trace,
        expression_trace,
        successor,
    ) = construct_successor_artifacts(value)

    companion = with_expected_companion_id(
        MsmOutwardExpressionCustodyCompanionV1(
            companion_id="pending",
            companion_version=SLICE42G_COMPANION_VERSION,
            integration_input_ref=value.integration_input_id,
            source_manifest_id=source.manifest_id,
            source_manifest_sha256=canonical_manifest_sha256(source),
            successor_manifest_id=successor.manifest_id,
            successor_manifest_sha256=canonical_manifest_sha256(successor),
            lineage_id=source.lineage_root.lineage_id,
            selected_governed_meaning_ref=(
                selected_result.integrated_selected_meaning_record.record_id
            ),
            surface_realization_input_ref=(
                value.surface_realization_input.realization_input_id
            ),
            surface_realization_result_ref=realization_result.result_id,
            expression_candidate_ref=candidate.expression_candidate_id,
            realization_trace_ref=realization_trace.realization_trace_id,
            realization_receipt_ref=realization_receipt.realization_receipt_id,
            external_authority_reference_record_ref=authority.record_id,
            integrated_governed_outward_meaning_ref=outward.record_id,
            integrated_expression_link_ref=expression.record_id,
            selected_to_outward_trace_ref=selected_trace.record_id,
            outward_to_expression_trace_ref=expression_trace.record_id,
            candidate_refs_before=_record_ids(source.candidate_meanings),
            candidate_refs_after=_record_ids(successor.candidate_meanings),
            non_selection_refs_before=_record_ids(source.non_selection_outcomes),
            non_selection_refs_after=_record_ids(successor.non_selection_outcomes),
            selected_refs_before=_record_ids(source.selected_governed_meanings),
            selected_refs_after=_record_ids(successor.selected_governed_meanings),
            governed_result_refs_before=_record_ids(source.governed_result_references),
            governed_result_refs_after=_record_ids(successor.governed_result_references),
            governed_outward_refs_before=_record_ids(source.governed_outward_meanings),
            governed_outward_refs_after=_record_ids(successor.governed_outward_meanings),
            expression_link_refs_before=_record_ids(source.expression_links),
            expression_link_refs_after=_record_ids(successor.expression_links),
            validation_link_refs_before=_record_ids(source.validation_links),
            validation_link_refs_after=_record_ids(successor.validation_links),
            delivery_link_refs_before=_record_ids(source.delivery_or_containment_links),
            delivery_link_refs_after=_record_ids(successor.delivery_or_containment_links),
            external_authority_refs_before=_record_ids(source.external_authority_references),
            external_authority_refs_after=_record_ids(successor.external_authority_references),
            transition_trace_refs_before=_record_ids(source.semantic_transition_traces),
            transition_trace_refs_after=_record_ids(successor.semantic_transition_traces),
            preserved_alternative_refs=_preserved_alternative_refs(value),
            unresolved_condition_refs=candidate.unresolved_condition_refs,
            ancestry_refs=_ancestry_refs(
                value,
                authority,
                outward,
                expression,
                selected_trace,
                expression_trace,
            ),
            exact_adapter=True,
            lossless_custody=True,
            immutable_successor=True,
            exact_slice41e_chain_preserved=True,
            exact_slice42f_candidate_preserved=True,
            selected_meaning_preserved=True,
            all_candidate_meanings_retained=True,
            all_non_selection_outcomes_retained=True,
            alternatives_and_unresolved_retained=True,
            governed_outward_meaning_integrated=True,
            expression_link_integrated=True,
            candidate_remains_unvalidated=True,
            complete_successor_manifest_validated=True,
            msm_schema_modified=False,
            automatic_migration_performed=False,
        )
    )

    receipt = with_expected_receipt_id(
        MsmOutwardExpressionIntegrationReceiptV1(
            receipt_id="pending",
            receipt_version=SLICE42G_RECEIPT_VERSION,
            integration_input_ref=value.integration_input_id,
            source_manifest_ref=source.manifest_id,
            successor_manifest_ref=successor.manifest_id,
            source_slice41e_result_ref=selected_result.result_id,
            source_slice42f_result_ref=realization_result.result_id,
            source_slice42f_realization_receipt_ref=(
                realization_receipt.realization_receipt_id
            ),
            selected_governed_meaning_ref=(
                selected_result.integrated_selected_meaning_record.record_id
            ),
            expression_candidate_ref=candidate.expression_candidate_id,
            external_authority_reference_record_ref=authority.record_id,
            governed_outward_meaning_ref=outward.record_id,
            expression_link_ref=expression.record_id,
            selected_to_outward_trace_ref=selected_trace.record_id,
            outward_to_expression_trace_ref=expression_trace.record_id,
            source_manifest_sha256=canonical_manifest_sha256(source),
            successor_manifest_sha256=canonical_manifest_sha256(successor),
            candidate_count_before=len(source.candidate_meanings),
            candidate_count_after=len(successor.candidate_meanings),
            non_selection_count_before=len(source.non_selection_outcomes),
            non_selection_count_after=len(successor.non_selection_outcomes),
            selected_count_before=len(source.selected_governed_meanings),
            selected_count_after=len(successor.selected_governed_meanings),
            governed_result_count_before=len(source.governed_result_references),
            governed_result_count_after=len(successor.governed_result_references),
            outward_meaning_count_before=len(source.governed_outward_meanings),
            outward_meaning_count_after=len(successor.governed_outward_meanings),
            expression_link_count_before=len(source.expression_links),
            expression_link_count_after=len(successor.expression_links),
            validation_link_count_before=len(source.validation_links),
            validation_link_count_after=len(successor.validation_links),
            delivery_link_count_before=len(source.delivery_or_containment_links),
            delivery_link_count_after=len(successor.delivery_or_containment_links),
            deterministic=True,
            additive_only=True,
            immutable_successor_created=True,
            complete_manifest_validated=True,
            selected_meaning_preserved=True,
            candidates_retained=True,
            non_selection_outcomes_retained=True,
            alternatives_and_unresolved_retained=True,
            governed_outward_meaning_integrated=True,
            expression_link_integrated=True,
            candidate_remains_unvalidated=True,
            msm_schema_modified=False,
            automatic_migration_performed=False,
            governed_result_reference_created=False,
            validation_link_created=False,
            delivery_link_created=False,
            echo_validated_or_approved=False,
            delivery_authorized_or_performed=False,
            truth_evidence_permission_execution=False,
            route_tool_action_memory_filesystem_network=False,
            external_resource_or_model_authority=False,
            bootstrap_integration_enabled=False,
            gp014_superseded=False,
        )
    )

    result = with_expected_result_identity(
        MsmOutwardExpressionIntegrationResult(
            result_id="pending",
            result_digest="0" * 64,
            integration_input_ref=value.integration_input_id,
            source_manifest=source,
            successor_manifest=successor,
            external_authority_reference_record=authority,
            governed_outward_meaning_record=outward,
            expression_link_record=expression,
            selected_to_outward_trace=selected_trace,
            outward_to_expression_trace=expression_trace,
            companion=companion,
            receipt=receipt,
            deterministic=True,
            additive_only=True,
            immutable_successor_created=True,
            exact_slice41e_chain_preserved=True,
            exact_slice42f_candidate_preserved=True,
            dormant_msm_records_used=True,
            selected_meaning_preserved=True,
            all_candidate_meanings_retained=True,
            all_non_selection_outcomes_retained=True,
            alternatives_and_unresolved_retained=True,
            governed_outward_meaning_integrated=True,
            expression_link_integrated=True,
            complete_successor_manifest_validated=True,
            candidate_remains_unvalidated=True,
            msm_schema_modified=False,
            automatic_migration_performed=False,
            source_manifest_mutated=False,
            candidate_deleted=False,
            non_selection_outcome_deleted=False,
            selected_meaning_rewritten=False,
            governed_result_reference_created=False,
            validation_link_created=False,
            delivery_link_created=False,
            expression_candidate_rewritten=False,
            claim_strengthened=False,
            certainty_upgraded=False,
            evidence_status_upgraded=False,
            caveat_omitted=False,
            refusal_softened=False,
            ambiguity_erased=False,
            unsupported_state_erased=False,
            echo_validation_performed=False,
            echo_approved=False,
            delivery_authorized=False,
            delivered=False,
            truth_determined=False,
            evidence_validated=False,
            permission_granted=False,
            execution_authorized=False,
            route_or_api_created=False,
            tool_invoked=False,
            action_performed=False,
            memory_accessed_or_written=False,
            filesystem_or_network_accessed=False,
            external_resource_loaded=False,
            model_or_similarity_authority_used=False,
            bootstrap_integration_enabled=False,
            gp014_superseded=False,
        )
    )
    assert_valid_integration_result(result, integration_input=value)
    return result


__all__ = (
    "build_expression_link",
    "build_external_authority_reference",
    "build_governed_outward_meaning",
    "construct_successor_artifacts",
    "derive_outward_meaning_fields",
    "integrate_outward_meaning_and_expression_link",
)
