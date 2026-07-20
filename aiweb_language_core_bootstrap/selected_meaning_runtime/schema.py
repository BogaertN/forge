"""Immutable Slice 41A selected-meaning runtime core schema contracts.

This module defines schema shapes and non-outcome custody states only.  It does
not calculate identities, validate records, enforce lifecycle transitions,
evaluate selection eligibility, choose or rank a candidate, discard
alternatives, resolve ambiguity, construct SelectedGovernedMeaningRecord,
modify MeaningStructureManifest v1, enable bootstrap integration, create
governed outward meaning, or create truth, evidence, proof, permission,
execution, route, tool, action, memory, rendering, delivery, or
external-resource authority.

All predecessor relationships are opaque exact references.  Slice 41A does not
import or execute the Slice 39 candidate constructor, Slice 40 gate runtime,
Slice 40H MSM gate adapter, or the dormant MSM-v1 selected-meaning record.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .authority import PERMANENT_SELECTED_MEANING_BOUNDARIES
from .identity import (
    ALTERNATIVE_CANDIDATE_CUSTODY_SCHEMA_ID,
    GATE_CUSTODY_REFERENCE_SCHEMA_ID,
    INHERITED_LIMITATION_CUSTODY_SCHEMA_ID,
    SCHEMA_VERSION,
    SELECTED_MEANING_DECISION_STATUS_SCHEMA_ID,
    SELECTED_MEANING_RUNTIME_SCHEMA_RECORD_SCHEMA_ID,
    SELECTION_AUTHORITY_REQUIREMENT_SCHEMA_ID,
    SELECTION_CANDIDATE_CUSTODY_SCHEMA_ID,
    SELECTION_ELIGIBILITY_STATUS_SCHEMA_ID,
    SELECTION_RECEIPT_BOUNDARY_SCHEMA_ID,
    SELECTION_TRACE_BOUNDARY_SCHEMA_ID,
    SPEC_ID,
    SPEC_VERSION,
    UNRESOLVED_STATE_CUSTODY_SCHEMA_ID,
)


class SelectionEligibilityCustodyState(str, Enum):
    """Schema-only eligibility custody states.

    These values describe whether later Slice 41C evaluation may occur.  They
    are not eligible, ineligible, accepted, rejected, selected, clarified,
    ambiguous, unsupported, held, blocked, or final decision outcomes.
    """

    NOT_EVALUATED = "not_evaluated"
    READY_FOR_LATER_EVALUATION = "ready_for_later_evaluation"
    EVALUATION_DEFERRED = "evaluation_deferred"
    EVALUATION_UNAVAILABLE = "evaluation_unavailable"


class SelectedMeaningDecisionCustodyState(str, Enum):
    """Schema-only selected-meaning decision custody states.

    These values describe whether later Slice 41D decision and construction
    work may occur.  They do not select a candidate or create selected meaning.
    """

    NOT_DECIDED = "not_decided"
    READY_FOR_LATER_DECISION = "ready_for_later_decision"
    DECISION_DEFERRED = "decision_deferred"
    DECISION_UNAVAILABLE = "decision_unavailable"


@dataclass(frozen=True, slots=True)
class SelectionCandidateCustodyRecord:
    selection_candidate_custody_id: str
    candidate_meaning_id: str
    candidate_state_id: str
    candidate_lineage_id: str
    source_expression_ref: str
    manifest_candidate_record_ref: str
    manifest_candidate_companion_ref: str
    candidate_identity_ref: str
    candidate_content_ref: str
    candidate_provenance_ref: str
    candidate_construction_receipt_ref: str
    candidate_set_ref: str
    candidate_set_member_ref: str
    candidate_lifecycle_ref: str
    gate_candidate_input_ref: str
    predecessor_receipt_refs: tuple[str, ...]
    candidate_only: bool = field(default=True, init=False)
    selection_candidate_reference_only: bool = field(default=True, init=False)
    candidate_eligibility_evaluated: bool = field(default=False, init=False)
    candidate_ranked: bool = field(default=False, init=False)
    candidate_selected: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=SELECTION_CANDIDATE_CUSTODY_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class GateCustodyReferenceRecord:
    gate_custody_reference_id: str
    selection_candidate_custody_ref: str
    msm_gate_custody_companion_ref: str
    expectancy_family_custody_ref: str
    congruity_family_custody_ref: str
    connectedness_family_custody_ref: str
    recoverable_purpose_family_custody_ref: str
    expectancy_result_ref: str
    congruity_result_ref: str
    connectedness_result_ref: str
    recoverable_purpose_result_ref: str
    composition_result_ref: str
    composition_disposition_refs: tuple[str, ...]
    candidate_specific_disposition_refs: tuple[str, ...]
    gate_profile_refs: tuple[str, ...]
    gate_trace_refs: tuple[str, ...]
    gate_provenance_refs: tuple[str, ...]
    gate_limitation_refs: tuple[str, ...]
    exact_candidate_match_required: bool = field(default=True, init=False)
    all_four_gate_families_required: bool = field(default=True, init=False)
    composition_required: bool = field(default=True, init=False)
    gate_results_preserved_exactly: bool = field(default=True, init=False)
    gate_results_re_evaluated: bool = field(default=False, init=False)
    composition_recomputed: bool = field(default=False, init=False)
    selection_performed: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=GATE_CUSTODY_REFERENCE_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class SelectionAuthorityRequirementRecord:
    selection_authority_requirement_id: str
    requirement_key: str
    requirement_version: str
    selection_candidate_custody_ref: str
    gate_custody_reference_ref: str
    governing_document_refs: tuple[str, ...]
    required_authority_profile_refs: tuple[str, ...]
    required_candidate_state_refs: tuple[str, ...]
    required_gate_disposition_refs: tuple[str, ...]
    required_alternative_custody_refs: tuple[str, ...]
    required_unresolved_custody_refs: tuple[str, ...]
    required_limitation_custody_refs: tuple[str, ...]
    required_predecessor_receipt_refs: tuple[str, ...]
    deferred_authority_refs: tuple[str, ...]
    requirement_satisfied: bool = field(default=False, init=False)
    requirement_failed: bool = field(default=False, init=False)
    authority_granted: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=SELECTION_AUTHORITY_REQUIREMENT_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class AlternativeCandidateCustodyRecord:
    alternative_candidate_custody_id: str
    selection_candidate_custody_ref: str
    candidate_set_ref: str
    preserved_alternative_candidate_refs: tuple[str, ...]
    non_selected_candidate_refs: tuple[str, ...]
    alternative_relationship_refs: tuple[str, ...]
    alternative_disposition_refs: tuple[str, ...]
    material_ambiguity_refs: tuple[str, ...]
    clarification_relevant_refs: tuple[str, ...]
    shared_ancestry_refs: tuple[str, ...]
    exact_duplicate_group_refs: tuple[str, ...]
    alternatives_preserved: bool = field(default=True, init=False)
    alternatives_ranked: bool = field(default=False, init=False)
    confidence_scores_created: bool = field(default=False, init=False)
    preferred_candidate_created: bool = field(default=False, init=False)
    alternatives_discarded: bool = field(default=False, init=False)
    ambiguity_resolved: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=ALTERNATIVE_CANDIDATE_CUSTODY_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class UnresolvedStateCustodyRecord:
    unresolved_state_custody_id: str
    selection_candidate_custody_ref: str
    unresolved_candidate_refs: tuple[str, ...]
    unknown_refs: tuple[str, ...]
    unsupported_refs: tuple[str, ...]
    conflicted_refs: tuple[str, ...]
    clarification_dependency_refs: tuple[str, ...]
    held_refs: tuple[str, ...]
    blocked_progression_refs: tuple[str, ...]
    refusal_relevant_refs: tuple[str, ...]
    missing_authority_refs: tuple[str, ...]
    missing_structure_refs: tuple[str, ...]
    deferred_dependency_refs: tuple[str, ...]
    unresolved_state_preserved: bool = field(default=True, init=False)
    unresolved_state_resolved: bool = field(default=False, init=False)
    clarification_emitted: bool = field(default=False, init=False)
    refusal_issued: bool = field(default=False, init=False)
    progression_authorized: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=UNRESOLVED_STATE_CUSTODY_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class InheritedLimitationCustodyRecord:
    inherited_limitation_custody_id: str
    selection_candidate_custody_ref: str
    source_limitation_refs: tuple[str, ...]
    candidate_limitation_refs: tuple[str, ...]
    gate_limitation_refs: tuple[str, ...]
    effect_boundary_refs: tuple[str, ...]
    domain_sensitive_refs: tuple[str, ...]
    authority_sensitive_distinction_refs: tuple[str, ...]
    evidence_boundary_refs: tuple[str, ...]
    memory_boundary_refs: tuple[str, ...]
    privacy_boundary_refs: tuple[str, ...]
    delivery_boundary_refs: tuple[str, ...]
    execution_boundary_refs: tuple[str, ...]
    correction_ancestry_refs: tuple[str, ...]
    supersession_ancestry_refs: tuple[str, ...]
    limitations_preserved: bool = field(default=True, init=False)
    limitations_released: bool = field(default=False, init=False)
    scope_enlarged: bool = field(default=False, init=False)
    authority_enlarged: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=INHERITED_LIMITATION_CUSTODY_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class SelectionEligibilityStatusRecord:
    selection_eligibility_status_id: str
    selection_candidate_custody_ref: str
    gate_custody_reference_ref: str
    selection_authority_requirement_refs: tuple[str, ...]
    alternative_candidate_custody_ref: str
    unresolved_state_custody_ref: str
    inherited_limitation_custody_ref: str
    custody_state: SelectionEligibilityCustodyState
    status_reason_refs: tuple[str, ...]
    later_evaluator_ref: str | None
    eligibility_evaluated: bool = field(default=False, init=False)
    eligible_for_selected_meaning_construction: bool = field(
        default=False,
        init=False,
    )
    not_eligible_determined: bool = field(default=False, init=False)
    candidate_ranked: bool = field(default=False, init=False)
    candidate_selected: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=SELECTION_ELIGIBILITY_STATUS_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class SelectedMeaningDecisionStatusRecord:
    selected_meaning_decision_status_id: str
    selection_candidate_custody_ref: str
    selection_eligibility_status_ref: str
    custody_state: SelectedMeaningDecisionCustodyState
    decision_reason_refs: tuple[str, ...]
    later_constructor_ref: str | None
    decision_performed: bool = field(default=False, init=False)
    candidate_selected: bool = field(default=False, init=False)
    selected_meaning_created: bool = field(default=False, init=False)
    msm_v1_modified: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=SELECTED_MEANING_DECISION_STATUS_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class SelectionTraceBoundaryRecord:
    selection_trace_boundary_id: str
    selection_candidate_custody_ref: str
    gate_custody_reference_ref: str
    selection_authority_requirement_refs: tuple[str, ...]
    alternative_candidate_custody_ref: str
    unresolved_state_custody_ref: str
    inherited_limitation_custody_ref: str
    selection_eligibility_status_ref: str
    selected_meaning_decision_status_ref: str
    source_trace_refs: tuple[str, ...]
    candidate_trace_refs: tuple[str, ...]
    gate_trace_refs: tuple[str, ...]
    composition_trace_refs: tuple[str, ...]
    predecessor_receipt_refs: tuple[str, ...]
    authority_version_refs: tuple[tuple[str, str], ...]
    schema_version_refs: tuple[tuple[str, str], ...]
    trace_boundary_only: bool = field(default=True, init=False)
    trace_validated: bool = field(default=False, init=False)
    selection_trace_created: bool = field(default=False, init=False)
    selection_performed: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=SELECTION_TRACE_BOUNDARY_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class SelectionReceiptBoundaryRecord:
    selection_receipt_boundary_id: str
    selection_candidate_custody_ref: str
    selection_eligibility_status_ref: str
    selected_meaning_decision_status_ref: str
    selection_trace_boundary_ref: str
    required_law_refs: tuple[str, ...]
    prohibited_consequence_refs: tuple[str, ...]
    audit_note: str
    receipt_boundary_only: bool = field(default=True, init=False)
    receipt_validated: bool = field(default=False, init=False)
    selection_receipt_created: bool = field(default=False, init=False)
    selected_meaning_created: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=SELECTION_RECEIPT_BOUNDARY_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class SelectedMeaningRuntimeSchemaRecord:
    selected_meaning_runtime_schema_record_id: str
    selection_candidate_custody: SelectionCandidateCustodyRecord
    gate_custody_reference: GateCustodyReferenceRecord
    selection_authority_requirements: tuple[
        SelectionAuthorityRequirementRecord,
        ...,
    ]
    alternative_candidate_custody: AlternativeCandidateCustodyRecord
    unresolved_state_custody: UnresolvedStateCustodyRecord
    inherited_limitation_custody: InheritedLimitationCustodyRecord
    selection_eligibility_status: SelectionEligibilityStatusRecord
    selected_meaning_decision_status: SelectedMeaningDecisionStatusRecord
    selection_trace_boundary: SelectionTraceBoundaryRecord
    selection_receipt_boundary: SelectionReceiptBoundaryRecord
    permanent_boundaries: tuple[str, ...] = field(
        default=PERMANENT_SELECTED_MEANING_BOUNDARIES,
        init=False,
    )
    schema_only: bool = field(default=True, init=False)
    versioned_companion: bool = field(default=True, init=False)
    deterministic_identity_calculated: bool = field(default=False, init=False)
    validation_performed: bool = field(default=False, init=False)
    canonical_serialization_performed: bool = field(default=False, init=False)
    lifecycle_transition_performed: bool = field(default=False, init=False)
    selection_eligibility_evaluated: bool = field(default=False, init=False)
    candidate_ranked: bool = field(default=False, init=False)
    alternatives_discarded: bool = field(default=False, init=False)
    ambiguity_resolved: bool = field(default=False, init=False)
    selection_decision_performed: bool = field(default=False, init=False)
    selected_meaning_created: bool = field(default=False, init=False)
    msm_v1_schema_modified: bool = field(default=False, init=False)
    msm_v1_automatic_migration_performed: bool = field(
        default=False,
        init=False,
    )
    bootstrap_integration_enabled: bool = field(default=False, init=False)
    governed_outward_meaning_created: bool = field(default=False, init=False)
    truth_determined: bool = field(default=False, init=False)
    evidence_validated: bool = field(default=False, init=False)
    proof_claim_created: bool = field(default=False, init=False)
    permission_granted: bool = field(default=False, init=False)
    execution_authorized: bool = field(default=False, init=False)
    capability_availability_created: bool = field(default=False, init=False)
    route_created: bool = field(default=False, init=False)
    tool_invoked: bool = field(default=False, init=False)
    action_performed: bool = field(default=False, init=False)
    memory_accessed: bool = field(default=False, init=False)
    memory_written: bool = field(default=False, init=False)
    rendered: bool = field(default=False, init=False)
    delivered: bool = field(default=False, init=False)
    external_resource_loaded: bool = field(default=False, init=False)
    language_model_used: bool = field(default=False, init=False)
    embedding_used: bool = field(default=False, init=False)
    vector_used: bool = field(default=False, init=False)
    rag_used: bool = field(default=False, init=False)
    semantic_similarity_used: bool = field(default=False, init=False)
    spec_id: str = field(default=SPEC_ID, init=False)
    spec_version: str = field(default=SPEC_VERSION, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=SELECTED_MEANING_RUNTIME_SCHEMA_RECORD_SCHEMA_ID,
        init=False,
    )
