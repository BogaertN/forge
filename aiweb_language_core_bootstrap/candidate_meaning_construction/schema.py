"""Immutable Slice 39A candidate-meaning constructor-shape contracts.

Slice 39A defines record shapes and construction-only status vocabulary.  It
does not calculate identities, validate records, authorize lifecycle
transitions, construct candidate meanings, rank alternatives, adapt records
into MeaningStructureManifest v1, select meaning, evaluate gates, determine
truth, validate evidence, grant permission, create routes, invoke tools,
perform actions, access memory, render output, or deliver anything.

The versioned records below are companion records to the accepted Slice 35
MeaningStructureManifest v1 CandidateMeaningRecord.  Slice 39A does not modify
or supersede that record.  A future bounded adapter decision belongs to Slice
39G after the complete Slice 39 record family is accepted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .authority import PERMANENT_CANDIDATE_MEANING_BOUNDARIES
from .identity import (
    ALTERNATIVE_REFERENCE_SCHEMA_ID,
    CONSTRUCTION_RECEIPT_SCHEMA_ID,
    CONTENT_SCHEMA_ID,
    IDENTITY_SCHEMA_ID,
    PROVENANCE_SCHEMA_ID,
    SCHEMA_VERSION,
    SPEC_ID,
    SPEC_VERSION,
    STATE_SCHEMA_ID,
)


class CandidateMeaningConstructionStatus(str, Enum):
    """Closed construction-only states owned by Slice 39."""

    CONSTRUCTED = "constructed"
    CONSTRUCTION_INCOMPLETE = "construction_incomplete"
    CONSTRUCTION_UNKNOWN = "construction_unknown"
    CONSTRUCTION_UNSUPPORTED = "construction_unsupported"
    CONSTRUCTION_CONFLICTED = "construction_conflicted"
    PREDECESSOR_INVALID = "predecessor_invalid"


@dataclass(frozen=True, slots=True)
class CandidateMeaningIdentity:
    """Versioned identity fields without identity-calculation authority."""

    candidate_meaning_id: str
    candidate_key: str
    candidate_version: str
    lineage_id: str
    construction_profile_id: str
    construction_profile_version: str
    spec_id: str = field(default=SPEC_ID, init=False)
    spec_version: str = field(default=SPEC_VERSION, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    identity_schema_id: str = field(default=IDENTITY_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class CandidateMeaningContent:
    """Candidate-only semantic content references.

    All values remain candidate references or explicit limitations.  This
    record does not admit selected concepts, selected predicates, selected
    frames, participant assignments, resolved referents, evidence status,
    truth, permission, or execution authority.
    """

    content_id: str
    communicative_act_candidate: str | None
    concept_candidate_refs: tuple[str, ...]
    sense_candidate_refs: tuple[str, ...]
    semantic_relation_candidate_refs: tuple[str, ...]
    action_root_predicate_candidate_refs: tuple[str, ...]
    frame_candidate_refs: tuple[str, ...]
    role_layout_candidate_refs: tuple[str, ...]
    referent_candidate_refs: tuple[str, ...]
    capability_reference_candidate_refs: tuple[str, ...]
    effect_boundary_refs: tuple[str, ...]
    meaning_modifiers: tuple[str, ...]
    limitations: tuple[str, ...]
    unresolved_referent_refs: tuple[str, ...]
    missing_role_refs: tuple[str, ...]
    conflicting_role_refs: tuple[str, ...]
    unsupported_reason_refs: tuple[str, ...]
    unknown_reason_refs: tuple[str, ...]
    authority_sensitive_implications: tuple[str, ...]
    preservation_class_refs: tuple[str, ...]
    candidate_only: bool = field(default=True, init=False)
    selected_content: bool = field(default=False, init=False)
    evidence_validity_determined: bool = field(default=False, init=False)
    truth_determined: bool = field(default=False, init=False)
    permission_inferred: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    content_schema_id: str = field(default=CONTENT_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class CandidateMeaningProvenance:
    """Complete provenance slots required by later Slice 39 increments.

    Slice 39A only defines the immutable shape.  Slice 39C will own exact
    predecessor binding and validation.
    """

    provenance_id: str
    source_event_id: str
    source_sha256: str
    input_event_id: str
    root_source_span_id: str
    source_span_ids: tuple[str, ...]
    projection_id: str
    structural_result_id: str
    structural_set_id: str
    structural_candidate_ids: tuple[str, ...]
    structural_ancestry_ids: tuple[str, ...]
    constrained_trail_ids: tuple[str, ...]
    phase_trail_ids: tuple[str, ...]
    operator_graph_ids: tuple[str, ...]
    operator_node_ids: tuple[str, ...]
    operator_definition_ids: tuple[str, ...]
    operator_keys_and_versions: tuple[tuple[str, str], ...]
    scope_occurrence_ids: tuple[str, ...]
    attachment_candidate_ids: tuple[str, ...]
    reference_analysis_ids: tuple[str, ...]
    reference_candidate_ids: tuple[str, ...]
    slice37_result_id: str
    slice37_registry_snapshot_id: str
    concept_candidate_proposal_ids: tuple[str, ...]
    sense_candidate_proposal_ids: tuple[str, ...]
    concept_ids_and_versions: tuple[tuple[str, str], ...]
    sense_ids_and_versions: tuple[tuple[str, str], ...]
    slice38_result_id: str
    slice38_registry_snapshot_id: str
    compatibility_registry_snapshot_id: str
    action_predicate_candidate_ids: tuple[str, ...]
    role_layout_candidate_ids: tuple[str, ...]
    capability_reference_candidate_ids: tuple[str, ...]
    predecessor_receipt_ids: tuple[str, ...]
    source_ancestry_preserved: bool
    operator_ancestry_preserved: bool
    phase_trail_ancestry_preserved: bool
    scope_attachment_ancestry_preserved: bool
    registry_snapshots_preserved: bool
    candidate_only: bool = field(default=True, init=False)
    selected_ancestry: bool = field(default=False, init=False)
    external_resource_loaded: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    provenance_schema_id: str = field(
        default=PROVENANCE_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class CandidateMeaningAlternativeReference:
    """Reference between possible meanings without ranking or selection."""

    alternative_reference_id: str
    source_candidate_meaning_id: str
    alternative_candidate_meaning_id: str
    alternative_kind: str
    shared_ancestry_refs: tuple[str, ...]
    differing_content_refs: tuple[str, ...]
    unresolved_reason_refs: tuple[str, ...]
    candidate_only: bool = field(default=True, init=False)
    ranking_assigned: bool = field(default=False, init=False)
    preferred_candidate_assigned: bool = field(default=False, init=False)
    selected_alternative: bool = field(default=False, init=False)
    ambiguous_gate_disposition_created: bool = field(
        default=False,
        init=False,
    )
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    alternative_reference_schema_id: str = field(
        default=ALTERNATIVE_REFERENCE_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class CandidateMeaningConstructionReceipt:
    """Construction-custody receipt shape without construction runtime."""

    receipt_id: str
    candidate_meaning_id: str
    identity_ref: str
    content_ref: str
    provenance_ref: str
    alternative_reference_ids: tuple[str, ...]
    predecessor_record_ids: tuple[str, ...]
    construction_profile_id: str
    construction_profile_version: str
    status: CandidateMeaningConstructionStatus
    status_reason_refs: tuple[str, ...]
    deterministic_construction_required: bool
    source_preservation_required: bool
    immutable_record_set_required: bool
    candidate_only: bool = field(default=True, init=False)
    accepted_meaning_created: bool = field(default=False, init=False)
    selected_meaning_created: bool = field(default=False, init=False)
    gate_outcome_created: bool = field(default=False, init=False)
    evidence_validity_determined: bool = field(default=False, init=False)
    truth_determined: bool = field(default=False, init=False)
    permission_inferred: bool = field(default=False, init=False)
    capability_availability_created: bool = field(default=False, init=False)
    route_created: bool = field(default=False, init=False)
    invocation_proposed: bool = field(default=False, init=False)
    tool_invoked: bool = field(default=False, init=False)
    action_performed: bool = field(default=False, init=False)
    memory_accessed: bool = field(default=False, init=False)
    rendered: bool = field(default=False, init=False)
    delivered: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    construction_receipt_schema_id: str = field(
        default=CONSTRUCTION_RECEIPT_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class CandidateMeaningState:
    """Aggregate candidate-meaning state owned by Slice 39.

    The aggregate is immutable and schema-only in Slice 39A.  It cannot be
    initialized with any downstream authority flag because those fields are
    fixed, non-init defaults.
    """

    state_id: str
    identity: CandidateMeaningIdentity
    content: CandidateMeaningContent
    provenance: CandidateMeaningProvenance
    alternative_references: tuple[CandidateMeaningAlternativeReference, ...]
    construction_status: CandidateMeaningConstructionStatus
    construction_receipt: CandidateMeaningConstructionReceipt
    status_reason_refs: tuple[str, ...]
    unresolved_alternative_refs: tuple[str, ...]
    missing_role_refs: tuple[str, ...]
    conflicting_role_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    permanent_boundaries: tuple[str, ...] = field(
        default=PERMANENT_CANDIDATE_MEANING_BOUNDARIES,
        init=False,
    )
    schema_only: bool = field(default=True, init=False)
    runtime_constructor_installed: bool = field(default=False, init=False)
    candidate_only: bool = field(default=True, init=False)
    accepted_meaning: bool = field(default=False, init=False)
    selected_meaning: bool = field(default=False, init=False)
    selected_sense: bool = field(default=False, init=False)
    selected_predicate: bool = field(default=False, init=False)
    selected_frame: bool = field(default=False, init=False)
    participant_assignment: bool = field(default=False, init=False)
    resolved_referent: bool = field(default=False, init=False)
    ambiguous_gate_disposition: bool = field(default=False, init=False)
    clarification_required: bool = field(default=False, init=False)
    refusal: bool = field(default=False, init=False)
    blocked_progression: bool = field(default=False, init=False)
    rejection: bool = field(default=False, init=False)
    evidence_validity: bool = field(default=False, init=False)
    truth: bool = field(default=False, init=False)
    verified_status: bool = field(default=False, init=False)
    permission: bool = field(default=False, init=False)
    capability_availability: bool = field(default=False, init=False)
    route: bool = field(default=False, init=False)
    invocation: bool = field(default=False, init=False)
    action: bool = field(default=False, init=False)
    memory_access: bool = field(default=False, init=False)
    rendering: bool = field(default=False, init=False)
    delivery: bool = field(default=False, init=False)
    external_resource_loading: bool = field(default=False, init=False)
    language_model_authority: bool = field(default=False, init=False)
    embedding_authority: bool = field(default=False, init=False)
    semantic_similarity_authority: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    state_schema_id: str = field(default=STATE_SCHEMA_ID, init=False)
