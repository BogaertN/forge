"""Immutable Slice 40A verbal-cognition gate core schema contracts.

This module defines record shapes only.  It does not calculate identities,
validate records, evaluate a gate family, compose outcomes, create ambiguity or
clarification dispositions, reject or hold candidates, select meaning, modify
MeaningStructureManifest v1, or create truth, evidence, permission, route,
execution, memory, rendering, delivery, or external-resource authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .authority import PERMANENT_GATE_CORE_BOUNDARIES
from .identity import (
    CANDIDATE_INPUT_REFERENCE_SCHEMA_ID,
    GATE_IDENTITY_SCHEMA_ID,
    GATE_PROFILE_SCHEMA_ID,
    LIMITATION_REFERENCE_SCHEMA_ID,
    PROVENANCE_REFERENCE_SCHEMA_ID,
    REASON_GROUND_SCHEMA_ID,
    REQUIREMENT_REFERENCE_SCHEMA_ID,
    REVIEW_RECORD_SCHEMA_ID,
    SCHEMA_VERSION,
    SPEC_ID,
    SPEC_VERSION,
    TRACE_REFERENCE_SCHEMA_ID,
)


class VerbalCognitionGateFamily(str, Enum):
    """The four approved Document 6 gate families."""

    EXPECTANCY = "expectancy"
    CONGRUITY = "congruity"
    CONNECTEDNESS = "connectedness"
    RECOVERABLE_PURPOSE = "recoverable_purpose"


class GateEvaluationState(str, Enum):
    """Schema-only evaluation custody states.

    These values describe whether later evaluation may occur.  They are not
    gate-family findings and are not pass, fail, acceptance, rejection,
    clarification, ambiguity, unsupported, refusal, hold, or selection states.
    """

    NOT_EVALUATED = "not_evaluated"
    READY_FOR_LATER_EVALUATION = "ready_for_later_evaluation"
    EVALUATION_DEFERRED = "evaluation_deferred"
    EVALUATION_UNAVAILABLE = "evaluation_unavailable"


@dataclass(frozen=True, slots=True)
class VerbalCognitionGateIdentity:
    gate_id: str
    gate_key: str
    gate_version: str
    gate_family: VerbalCognitionGateFamily
    gate_profile_ref: str
    spec_id: str = field(default=SPEC_ID, init=False)
    spec_version: str = field(default=SPEC_VERSION, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    identity_schema_id: str = field(
        default=GATE_IDENTITY_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class VerbalCognitionGateProfileIdentity:
    profile_id: str
    profile_key: str
    profile_version: str
    gate_family: VerbalCognitionGateFamily
    governing_authority_refs: tuple[str, ...]
    required_schema_refs: tuple[str, ...]
    exact_profile_only: bool
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    profile_schema_id: str = field(
        default=GATE_PROFILE_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class GateCandidateInputReference:
    candidate_input_ref_id: str
    candidate_meaning_id: str
    candidate_state_id: str
    candidate_lineage_id: str
    candidate_identity_ref: str
    candidate_content_ref: str
    candidate_provenance_ref: str
    construction_receipt_ref: str
    manifest_candidate_record_ref: str | None
    manifest_companion_ref: str | None
    construction_trace_ref: str | None
    limitation_reference_ref: str | None
    alternative_relationship_refs: tuple[str, ...]
    candidate_only: bool = field(default=True, init=False)
    accepted_candidate: bool = field(default=False, init=False)
    selected_candidate: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    candidate_input_schema_id: str = field(
        default=CANDIDATE_INPUT_REFERENCE_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class GateRequirementReference:
    requirement_reference_id: str
    gate_family: VerbalCognitionGateFamily
    requirement_key: str
    requirement_version: str
    candidate_input_ref: str
    subject_record_refs: tuple[str, ...]
    required_authority_refs: tuple[str, ...]
    required_record_refs: tuple[str, ...]
    required_relation_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    requirement_satisfied: bool = field(default=False, init=False)
    requirement_failed: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    requirement_schema_id: str = field(
        default=REQUIREMENT_REFERENCE_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class GateReasonGround:
    reason_ground_id: str
    gate_family: VerbalCognitionGateFamily
    reason_key: str
    candidate_input_ref: str
    requirement_reference_ids: tuple[str, ...]
    supporting_record_refs: tuple[str, ...]
    conflicting_record_refs: tuple[str, ...]
    missing_record_refs: tuple[str, ...]
    unknown_record_refs: tuple[str, ...]
    authority_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    reason_validated: bool = field(default=False, init=False)
    outcome_created: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    reason_ground_schema_id: str = field(
        default=REASON_GROUND_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class GateTraceReference:
    trace_reference_id: str
    candidate_input_ref: str
    source_span_refs: tuple[str, ...]
    candidate_trace_refs: tuple[str, ...]
    construction_trace_refs: tuple[str, ...]
    structural_trace_refs: tuple[str, ...]
    concept_sense_trace_refs: tuple[str, ...]
    predicate_role_frame_trace_refs: tuple[str, ...]
    alternative_relationship_refs: tuple[str, ...]
    predecessor_receipt_refs: tuple[str, ...]
    trace_validated: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    trace_schema_id: str = field(
        default=TRACE_REFERENCE_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class GateProvenanceReference:
    provenance_reference_id: str
    candidate_input_ref: str
    source_event_id: str
    source_sha256: str
    candidate_provenance_ref: str
    gate_profile_ref: str
    governing_document_refs: tuple[str, ...]
    authority_version_refs: tuple[tuple[str, str], ...]
    schema_version_refs: tuple[tuple[str, str], ...]
    external_resource_refs: tuple[str, ...]
    provenance_validated: bool = field(default=False, init=False)
    external_resource_loaded: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    provenance_schema_id: str = field(
        default=PROVENANCE_REFERENCE_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class GateLimitationReference:
    limitation_reference_id: str
    candidate_input_ref: str
    limitation_key: str
    reason_refs: tuple[str, ...]
    affected_requirement_refs: tuple[str, ...]
    later_authority_refs: tuple[str, ...]
    clarification_created: bool = field(default=False, init=False)
    blocked_progression_created: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    limitation_schema_id: str = field(
        default=LIMITATION_REFERENCE_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class VerbalCognitionGateReviewRecord:
    review_record_id: str
    identity: VerbalCognitionGateIdentity
    profile: VerbalCognitionGateProfileIdentity
    candidate_input: GateCandidateInputReference
    requirement_references: tuple[GateRequirementReference, ...]
    reason_grounds: tuple[GateReasonGround, ...]
    evaluation_state: GateEvaluationState
    trace_references: tuple[GateTraceReference, ...]
    provenance_reference: GateProvenanceReference
    limitation_references: tuple[GateLimitationReference, ...]
    permanent_boundaries: tuple[str, ...] = field(
        default=PERMANENT_GATE_CORE_BOUNDARIES,
        init=False,
    )
    schema_only: bool = field(default=True, init=False)
    versioned_companion: bool = field(default=True, init=False)
    runtime_evaluator_installed: bool = field(default=False, init=False)
    identity_calculated: bool = field(default=False, init=False)
    validation_performed: bool = field(default=False, init=False)
    lifecycle_transition_performed: bool = field(default=False, init=False)
    gate_evaluation_performed: bool = field(default=False, init=False)
    expectancy_result_created: bool = field(default=False, init=False)
    congruity_result_created: bool = field(default=False, init=False)
    connectedness_result_created: bool = field(default=False, init=False)
    recoverable_purpose_result_created: bool = field(default=False, init=False)
    gate_pass_created: bool = field(default=False, init=False)
    gate_failure_created: bool = field(default=False, init=False)
    gate_outcome_created: bool = field(default=False, init=False)
    ambiguity_disposition_created: bool = field(default=False, init=False)
    clarification_required_created: bool = field(default=False, init=False)
    unsupported_disposition_created: bool = field(default=False, init=False)
    refusal_relevant_disposition_created: bool = field(default=False, init=False)
    held_disposition_created: bool = field(default=False, init=False)
    blocked_progression_created: bool = field(default=False, init=False)
    positive_selection_review_disposition_created: bool = field(
        default=False,
        init=False,
    )
    candidate_accepted: bool = field(default=False, init=False)
    candidate_rejected: bool = field(default=False, init=False)
    candidate_clarified: bool = field(default=False, init=False)
    selected_meaning_created: bool = field(default=False, init=False)
    truth_determined: bool = field(default=False, init=False)
    evidence_validated: bool = field(default=False, init=False)
    permission_granted: bool = field(default=False, init=False)
    execution_authorized: bool = field(default=False, init=False)
    capability_availability_created: bool = field(default=False, init=False)
    route_created: bool = field(default=False, init=False)
    tool_invoked: bool = field(default=False, init=False)
    action_performed: bool = field(default=False, init=False)
    memory_accessed: bool = field(default=False, init=False)
    rendered: bool = field(default=False, init=False)
    delivered: bool = field(default=False, init=False)
    external_resource_loaded: bool = field(default=False, init=False)
    language_model_used: bool = field(default=False, init=False)
    embedding_used: bool = field(default=False, init=False)
    vector_used: bool = field(default=False, init=False)
    rag_used: bool = field(default=False, init=False)
    semantic_similarity_used: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    review_record_schema_id: str = field(
        default=REVIEW_RECORD_SCHEMA_ID,
        init=False,
    )
