"""Deterministic Slice 41D selected-meaning package construction."""
from __future__ import annotations

from ...meaning_structure_manifest import SelectedGovernedMeaningRecord
from .authority import SLICE41D_PERMANENT_BOUNDARIES, SLICE41D_PROHIBITED_AUTHORITY
from .canonical import canonical_json_bytes, deterministic_digest
from .identity import (
    with_expected_content_proof_id,
    with_expected_decision_id,
    with_expected_package_identity,
    with_expected_preservation_id,
    with_expected_receipt_id,
    with_expected_selected_meaning_record_id,
    with_expected_trace_id,
)
from .schema import (
    PreservedAlternativeCandidateRecord,
    PreservedAlternativeKind,
    SelectedMeaningConstructionInput,
    SelectedMeaningConstructionPackage,
    SelectedMeaningContentProof,
    SelectedMeaningDecisionRecord,
    SelectedMeaningSelectionReceiptRecord,
    SelectedMeaningSelectionTraceRecord,
)
from .validation import assert_valid_construction_input, assert_valid_package


def _unique(*groups: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for group in groups:
        for value in group:
            if value not in seen:
                seen.add(value)
                result.append(value)
    return tuple(result)


def _semantic_mapping_from_candidate(candidate) -> dict[str, object]:
    return {
        "communicative_act": candidate.communicative_act,
        "concept_refs": candidate.concept_refs,
        "relation_refs": candidate.relation_refs,
        "meaning_modifiers": candidate.meaning_modifiers,
        "preservation_classes": candidate.preservation_classes,
    }


def _semantic_mapping_from_selected(selected) -> dict[str, object]:
    return {
        "communicative_act": selected.communicative_act,
        "concept_refs": selected.concept_refs,
        "relation_refs": selected.relation_refs,
        "meaning_modifiers": selected.meaning_modifiers,
        "preservation_classes": selected.preservation_classes,
    }


def _difference(left: tuple[object, ...], right: tuple[object, ...]) -> tuple[object, ...]:
    right_set = set(right)
    return tuple(item for item in left if item not in right_set)


def _alternative_kinds(value: SelectedMeaningConstructionInput) -> tuple[PreservedAlternativeKind, ...]:
    result = value.eligibility_result
    unresolved = value.eligibility_evaluation_input.unresolved_state_custody
    kinds: list[PreservedAlternativeKind] = [PreservedAlternativeKind.NON_SELECTED]
    if unresolved.unresolved_candidate_refs:
        kinds.append(PreservedAlternativeKind.UNRESOLVED)
    if result.material_ambiguity_refs:
        kinds.append(PreservedAlternativeKind.MATERIAL_AMBIGUITY)
    if result.clarification_dependency_refs:
        kinds.append(PreservedAlternativeKind.CLARIFICATION_DEPENDENT)
    if result.unsupported_refs:
        kinds.append(PreservedAlternativeKind.UNSUPPORTED)
    if result.conflicted_refs:
        kinds.append(PreservedAlternativeKind.CONFLICTED)
    if result.held_refs:
        kinds.append(PreservedAlternativeKind.HELD)
    if result.refusal_relevant_refs:
        kinds.append(PreservedAlternativeKind.REFUSAL_RELEVANT)
    if result.blocked_progression_refs:
        kinds.append(PreservedAlternativeKind.BLOCKED_PROGRESSION)
    if value.eligibility_evaluation_input.alternative_candidate_custody.exact_duplicate_group_refs:
        kinds.append(PreservedAlternativeKind.EXACT_DUPLICATE)
    return tuple(kinds)


def construct_selected_meaning_package(
    value: SelectedMeaningConstructionInput,
) -> SelectedMeaningConstructionPackage:
    """Construct exactly one selected-meaning package from a successful 41C result."""

    assert_valid_construction_input(value)
    evaluation_input = value.eligibility_evaluation_input
    eligibility = value.eligibility_result
    candidate = value.selected_candidate_record
    companion = value.selected_candidate_companion
    alternative_custody = evaluation_input.alternative_candidate_custody
    unresolved_custody = evaluation_input.unresolved_state_custody
    limitation_custody = evaluation_input.inherited_limitation_custody

    non_selected_refs = tuple(
        ref
        for ref in _unique(
            eligibility.preserved_alternative_candidate_refs,
            alternative_custody.preserved_alternative_candidate_refs,
            alternative_custody.non_selected_candidate_refs,
            unresolved_custody.unresolved_candidate_refs,
        )
        if ref not in {
            eligibility.candidate_meaning_ref,
            candidate.record_id,
            companion.candidate_meaning_id,
        }
    )

    unresolved_alternative_refs = _unique(
        unresolved_custody.unresolved_candidate_refs,
        eligibility.material_ambiguity_refs,
        eligibility.clarification_dependency_refs,
        eligibility.unsupported_refs,
        eligibility.conflicted_refs,
        eligibility.missing_authority_refs,
        eligibility.held_refs,
        eligibility.refusal_relevant_refs,
        eligibility.blocked_progression_refs,
    )
    ambiguity_ancestry_refs = _unique(
        value.ambiguity_ancestry_refs,
        candidate.ambiguity_reasons,
        alternative_custody.material_ambiguity_refs,
        eligibility.material_ambiguity_refs,
    )
    clarification_ancestry_refs = _unique(
        value.clarification_ancestry_refs,
        alternative_custody.clarification_relevant_refs,
        unresolved_custody.clarification_dependency_refs,
        eligibility.clarification_dependency_refs,
    )
    inherited_limitation_refs = _unique(
        candidate.ambiguity_reasons,
        candidate.unresolved_referents,
        eligibility.inherited_limitation_refs,
        limitation_custody.source_limitation_refs,
        limitation_custody.candidate_limitation_refs,
        limitation_custody.gate_limitation_refs,
        limitation_custody.effect_boundary_refs,
        limitation_custody.domain_sensitive_refs,
        limitation_custody.evidence_boundary_refs,
        limitation_custody.memory_boundary_refs,
        limitation_custody.privacy_boundary_refs,
        limitation_custody.delivery_boundary_refs,
        limitation_custody.execution_boundary_refs,
        limitation_custody.correction_ancestry_refs,
        limitation_custody.supersession_ancestry_refs,
        eligibility.blocked_progression_refs,
        eligibility.refusal_relevant_refs,
        eligibility.missing_authority_refs,
        eligibility.held_refs,
        eligibility.unsupported_refs,
        eligibility.conflicted_refs,
    )
    authority_sensitive_refs = _unique(
        candidate.authority_sensitive_implications,
        limitation_custody.authority_sensitive_distinction_refs,
    )
    blocked_consequence_refs = _unique(
        eligibility.blocked_progression_refs,
        unresolved_custody.blocked_progression_refs,
        limitation_custody.effect_boundary_refs,
        limitation_custody.execution_boundary_refs,
        limitation_custody.delivery_boundary_refs,
    )
    refusal_relevant_refs = _unique(
        eligibility.refusal_relevant_refs,
        unresolved_custody.refusal_relevant_refs,
    )

    decision = with_expected_decision_id(SelectedMeaningDecisionRecord(
        decision_id="placeholder",
        construction_input_ref=value.construction_input_id,
        eligibility_result_ref=eligibility.result_id,
        selected_candidate_ref=eligibility.candidate_meaning_ref,
        selected_candidate_lineage_ref=eligibility.candidate_lineage_ref,
        selected_manifest_candidate_record_ref=candidate.record_id,
        selected_manifest_candidate_companion_ref=companion.companion_id,
        selection_authority_profile_ref=value.authority_profile.profile_id,
        selection_reason_refs=value.selection_reason_refs,
        non_selected_candidate_refs=non_selected_refs,
        unresolved_alternative_refs=unresolved_alternative_refs,
        ambiguity_ancestry_refs=ambiguity_ancestry_refs,
        clarification_ancestry_refs=clarification_ancestry_refs,
        decision_performed=True,
        candidate_ranked=False,
        only_candidate_claimed=False,
        historical_candidate_exhaustiveness_claimed=False,
    ))

    selected = with_expected_selected_meaning_record_id(
        SelectedGovernedMeaningRecord(
            record_id="placeholder",
            lineage_id=candidate.lineage_id,
            selected_candidate_ref=candidate.record_id,
            selection_authority_ref=eligibility.result_id,
            communicative_act=candidate.communicative_act,
            concept_refs=candidate.concept_refs,
            relation_refs=candidate.relation_refs,
            meaning_modifiers=candidate.meaning_modifiers,
            inherited_limitations=inherited_limitation_refs,
            authority_sensitive_distinctions=candidate.authority_sensitive_implications,
            preservation_classes=candidate.preservation_classes,
        )
    )

    candidate_semantic = _semantic_mapping_from_candidate(candidate)
    selected_semantic = _semantic_mapping_from_selected(selected)
    candidate_digest = deterministic_digest(canonical_json_bytes(candidate_semantic))
    selected_digest = deterministic_digest(canonical_json_bytes(selected_semantic))
    added_concepts = _difference(selected.concept_refs, candidate.concept_refs)
    removed_concepts = _difference(candidate.concept_refs, selected.concept_refs)
    added_relations = _difference(selected.relation_refs, candidate.relation_refs)
    removed_relations = _difference(candidate.relation_refs, selected.relation_refs)
    added_modifiers = _difference(selected.meaning_modifiers, candidate.meaning_modifiers)
    removed_modifiers = _difference(candidate.meaning_modifiers, selected.meaning_modifiers)
    selected_classes = tuple(item.value for item in selected.preservation_classes)
    candidate_classes = tuple(item.value for item in candidate.preservation_classes)
    added_classes = _difference(selected_classes, candidate_classes)
    removed_classes = _difference(candidate_classes, selected_classes)
    content_exact = candidate_semantic == selected_semantic

    proof = with_expected_content_proof_id(SelectedMeaningContentProof(
        proof_id="placeholder",
        construction_input_ref=value.construction_input_id,
        selected_candidate_ref=candidate.record_id,
        selected_meaning_ref=selected.record_id,
        candidate_semantic_digest=candidate_digest,
        selected_semantic_digest=selected_digest,
        communicative_act_exact=selected.communicative_act == candidate.communicative_act,
        concept_refs_exact=selected.concept_refs == candidate.concept_refs,
        relation_refs_exact=selected.relation_refs == candidate.relation_refs,
        meaning_modifiers_exact=selected.meaning_modifiers == candidate.meaning_modifiers,
        preservation_classes_exact=selected.preservation_classes == candidate.preservation_classes,
        candidate_identity_exact=selected.selected_candidate_ref == candidate.record_id,
        candidate_lineage_exact=selected.lineage_id == candidate.lineage_id,
        added_concept_refs=tuple(added_concepts),
        removed_concept_refs=tuple(removed_concepts),
        added_relation_refs=tuple(added_relations),
        removed_relation_refs=tuple(removed_relations),
        added_meaning_modifiers=tuple(added_modifiers),
        removed_meaning_modifiers=tuple(removed_modifiers),
        added_preservation_classes=tuple(added_classes),
        removed_preservation_classes=tuple(removed_classes),
        semantic_content_exact=content_exact,
        semantic_enrichment_detected=bool(
            added_concepts or added_relations or added_modifiers or added_classes
        ),
        semantic_deletion_detected=bool(
            removed_concepts or removed_relations or removed_modifiers or removed_classes
        ),
    ))

    kinds = _alternative_kinds(value)
    unresolved_reasons = _unique(
        eligibility.material_ambiguity_refs,
        eligibility.clarification_dependency_refs,
        eligibility.unsupported_refs,
        eligibility.conflicted_refs,
        eligibility.missing_authority_refs,
        eligibility.held_refs,
        eligibility.refusal_relevant_refs,
        eligibility.blocked_progression_refs,
    )
    preserved = tuple(
        with_expected_preservation_id(PreservedAlternativeCandidateRecord(
            preservation_id="placeholder",
            construction_input_ref=value.construction_input_id,
            selected_candidate_ref=candidate.record_id,
            alternative_candidate_ref=alternative_ref,
            preservation_kinds=kinds,
            alternative_relationship_refs=alternative_custody.alternative_relationship_refs,
            disposition_refs=alternative_custody.alternative_disposition_refs,
            unresolved_reason_refs=unresolved_reasons,
            ambiguity_ancestry_refs=ambiguity_ancestry_refs,
            clarification_ancestry_refs=clarification_ancestry_refs,
            shared_ancestry_refs=alternative_custody.shared_ancestry_refs,
            exact_duplicate_group_refs=alternative_custody.exact_duplicate_group_refs,
            preserved_by_exact_reference=True,
            selected=False,
            deleted=False,
            ranked=False,
            confidence_scored=False,
        ))
        for alternative_ref in non_selected_refs
    )

    trace = with_expected_trace_id(SelectedMeaningSelectionTraceRecord(
        trace_id="placeholder",
        construction_input_ref=value.construction_input_id,
        decision_ref=decision.decision_id,
        eligibility_result_ref=eligibility.result_id,
        selected_candidate_ref=candidate.record_id,
        selected_meaning_ref=selected.record_id,
        gate_custody_ref=eligibility.msm_gate_custody_companion_ref,
        gate_composition_result_ref=eligibility.gate_composition_result_ref,
        authority_profile_ref=value.authority_profile.profile_id,
        content_proof_ref=proof.proof_id,
        preserved_alternative_refs=tuple(item.preservation_id for item in preserved),
        unresolved_alternative_refs=unresolved_alternative_refs,
        inherited_limitation_refs=inherited_limitation_refs,
        blocked_consequence_refs=blocked_consequence_refs,
        refusal_relevant_refs=refusal_relevant_refs,
        ambiguity_ancestry_refs=ambiguity_ancestry_refs,
        clarification_ancestry_refs=clarification_ancestry_refs,
        predecessor_trace_refs=_unique(eligibility.trace_refs, value.trace_refs),
        predecessor_receipt_refs=(
            evaluation_input.governance_bundle.runtime_schema_record.
            selection_receipt_boundary.selection_receipt_boundary_id,
        ),
        provenance_refs=_unique(eligibility.provenance_refs, value.provenance_refs),
        version_refs=_unique(value.version_refs,),
        deterministic=True,
        candidate_ranked=False,
        alternatives_erased=False,
    ))

    receipt = with_expected_receipt_id(SelectedMeaningSelectionReceiptRecord(
        receipt_id="placeholder",
        construction_input_ref=value.construction_input_id,
        decision_ref=decision.decision_id,
        selected_meaning_ref=selected.record_id,
        content_proof_ref=proof.proof_id,
        trace_ref=trace.trace_id,
        eligibility_result_ref=eligibility.result_id,
        selected_candidate_ref=candidate.record_id,
        preserved_alternative_refs=tuple(item.preservation_id for item in preserved),
        unresolved_alternative_refs=unresolved_alternative_refs,
        inherited_limitation_refs=inherited_limitation_refs,
        required_law_refs=SLICE41D_PERMANENT_BOUNDARIES,
        prohibited_consequence_refs=SLICE41D_PROHIBITED_AUTHORITY,
        deterministic=True,
        selected_meaning_constructed=True,
        msm_v1_modified=False,
        outward_meaning_created=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        rendered=False,
        delivered=False,
    ))

    package = SelectedMeaningConstructionPackage(
        package_id="placeholder",
        package_digest="0" * 64,
        construction_input_ref=value.construction_input_id,
        authority_profile_ref=value.authority_profile.profile_id,
        eligibility_result_ref=eligibility.result_id,
        selected_candidate_record=candidate,
        selected_candidate_companion=companion,
        decision_record=decision,
        selected_meaning_record=selected,
        content_proof=proof,
        preserved_alternatives=preserved,
        unresolved_alternative_refs=unresolved_alternative_refs,
        ambiguity_ancestry_refs=ambiguity_ancestry_refs,
        clarification_ancestry_refs=clarification_ancestry_refs,
        inherited_limitation_refs=inherited_limitation_refs,
        blocked_consequence_refs=blocked_consequence_refs,
        refusal_relevant_refs=refusal_relevant_refs,
        authority_sensitive_distinction_refs=authority_sensitive_refs,
        selection_trace=trace,
        selection_receipt=receipt,
        deterministic=True,
        exact_candidate_identity_preserved=True,
        exact_candidate_lineage_preserved=True,
        exact_semantic_content_preserved=content_exact,
        every_non_selected_candidate_preserved=(
            tuple(item.alternative_candidate_ref for item in preserved)
            == non_selected_refs
        ),
        unresolved_alternatives_preserved_separately=True,
        ambiguity_ancestry_preserved=True,
        clarification_ancestry_preserved=True,
        inherited_limitations_preserved=True,
        blocked_consequences_preserved=True,
        refusal_relevance_preserved=True,
        selected_meaning_created=True,
        candidate_ranked=False,
        alternatives_erased=False,
        msm_v1_modified=False,
        governed_outward_meaning_created=False,
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
        external_resource_loaded=False,
        language_model_used=False,
        hidden_classifier_used=False,
        confidence_scoring_used=False,
        probability_ranking_used=False,
        semantic_similarity_used=False,
        nearest_known_substitution_used=False,
        bootstrap_integration_enabled=False,
    )
    package = with_expected_package_identity(package)
    assert_valid_package(package, construction_input=value)
    return package


__all__ = ("construct_selected_meaning_package",)
