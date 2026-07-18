"""Immutable Slice 39D candidate semantic-content assembly records.

These records represent possible semantic content only.  They do not rank or
select candidates, assign participant roles, resolve referents, emit
clarification questions, evaluate gates, determine truth, validate evidence,
grant permission, create routes, invoke tools, perform actions, access memory,
render output, or deliver anything.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..schema import CandidateMeaningContent
from ..predecessor_custody.schema import CandidateMeaningPredecessorCustody


SLICE39D_ACCEPTED_PARENT_HEAD = "cc69a1fb092a9ed8d2d398a9ec6ae19643337a45"
SLICE39D_ACCEPTED_PARENT_TREE = "261e29410bc3bad50d6c0aecf3da2f9b5d9886be"
SLICE39D_ACCEPTED_PARENT_SUBJECT = (
    "Slice 39C complete provenance predecessor custody"
)
SLICE39D_SPEC_ID = "aiweb-slice39d-candidate-semantic-content-assembly"
SLICE39D_SPEC_VERSION = "aiweb-slice39d-candidate-semantic-content-assembly-v1"
SLICE39D_SCHEMA_VERSION = (
    "aiweb-language-core-slice39d-candidate-semantic-content-assembly-v1"
)
SLICE39D_PROFILE_VERSION = "v1.0.0"
DIGEST_ALGORITHM = "sha256"


class CandidateSemanticContentStatus(str, Enum):
    ASSEMBLED = "assembled"
    NO_CANDIDATE_CONTENT = "no_candidate_content"
    CONTENT_REJECTED = "content_rejected"


class CommunicativeForceCandidate(str, Enum):
    ASSERTION = "assertion"
    QUESTION = "question"
    REPORT = "report"
    REQUEST = "request"
    UNRESOLVED = "unresolved"


class ReferentCandidateKind(str, Enum):
    SOURCE = "source"
    COMPARISON_TARGET = "comparison_target"
    OTHER_CONTEXT_OBJECT = "other_context_object"
    UNRESOLVED = "unresolved"


class SemanticDistinctionKind(str, Enum):
    CONDITION = "condition"
    NEGATION = "negation"
    QUALIFICATION = "qualification"
    TEMPORAL = "temporal"
    STATUS = "status"
    SCOPE = "scope"
    ATTACHMENT = "attachment"
    LIMITATION = "limitation"
    MISSING_INFORMATION = "missing_information"
    CONFLICTING_INFORMATION = "conflicting_information"
    AUTHORITY_SENSITIVE_IMPLICATION = "authority_sensitive_implication"


class CandidateSemanticContentValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    REQUIRED_VALUE_MISSING = "required_value_missing"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    INVALID_SHA256 = "invalid_sha256"
    INVALID_ENUM = "invalid_enum"
    INVALID_TUPLE = "invalid_tuple"
    DUPLICATE_VALUE = "duplicate_value"
    IDENTITY_MISMATCH = "identity_mismatch"
    PROFILE_MISMATCH = "profile_mismatch"
    PREDECESSOR_CUSTODY_INVALID = "predecessor_custody_invalid"
    LINEAGE_MISMATCH = "lineage_mismatch"
    SOURCE_EVENT_MISMATCH = "source_event_mismatch"
    SOURCE_SPAN_MISMATCH = "source_span_mismatch"
    CONCEPT_REFERENCE_FABRICATED = "concept_reference_fabricated"
    SENSE_REFERENCE_FABRICATED = "sense_reference_fabricated"
    SEMANTIC_RELATION_REFERENCE_FABRICATED = "semantic_relation_reference_fabricated"
    ACTION_ROOT_REFERENCE_FABRICATED = "action_root_reference_fabricated"
    PREDICATE_REFERENCE_FABRICATED = "predicate_reference_fabricated"
    FRAME_REFERENCE_FABRICATED = "frame_reference_fabricated"
    ROLE_LAYOUT_REFERENCE_FABRICATED = "role_layout_reference_fabricated"
    REFERENT_REFERENCE_FABRICATED = "referent_reference_fabricated"
    EFFECT_BOUNDARY_REFERENCE_FABRICATED = "effect_boundary_reference_fabricated"
    CAPABILITY_REFERENCE_FABRICATED = "capability_reference_fabricated"
    MIXED_CANDIDATE_LINEAGE = "mixed_candidate_lineage"
    ROLE_ASSIGNMENT_PROHIBITED = "role_assignment_prohibited"
    RELATION_FACT_PROHIBITED = "relation_fact_prohibited"
    CLARIFICATION_EMISSION_PROHIBITED = "clarification_emission_prohibited"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"
    NONDETERMINISTIC_INPUT_PROHIBITED = "nondeterministic_input_prohibited"
    CONTENT_MAPPING_MISMATCH = "content_mapping_mismatch"


@dataclass(frozen=True, slots=True)
class CandidateSemanticContentValidationIssue:
    path: str
    code: CandidateSemanticContentValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class CandidateSemanticContentValidationReport:
    issues: tuple[CandidateSemanticContentValidationIssue, ...]
    schema_version: str = SLICE39D_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class CandidateSemanticContentValidationError(ValueError):
    def __init__(self, report: CandidateSemanticContentValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(summary or "Slice 39D candidate content rejected")


@dataclass(frozen=True, slots=True)
class CandidateSemanticContentProfileIdentity:
    profile_id: str
    profile_key: str
    profile_version: str
    exact_predecessor_custody_required: bool
    exact_candidate_identity_required: bool
    exact_registry_identity_required: bool
    exact_source_span_support_required: bool
    zero_one_many_preservation_required: bool
    communicative_force_plurality_allowed: bool
    semantic_relation_candidate_references_allowed: bool
    role_assignment_allowed: bool
    referent_resolution_allowed: bool
    clarification_question_emission_allowed: bool
    candidate_ranking_allowed: bool
    candidate_selection_allowed: bool
    gate_progression_allowed: bool
    truth_evidence_permission_allowed: bool
    route_action_memory_rendering_delivery_allowed: bool
    spec_id: str = SLICE39D_SPEC_ID
    spec_version: str = SLICE39D_SPEC_VERSION
    schema_version: str = SLICE39D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateCommunicativePurpose:
    purpose_id: str
    purpose_keys: tuple[str, ...]
    force_candidates: tuple[CommunicativeForceCandidate, ...]
    source_action_predicate_candidate_ids: tuple[str, ...]
    source_scope_occurrence_ids: tuple[str, ...]
    source_span_ids: tuple[str, ...]
    candidate_only: bool
    force_selected: bool
    gate_disposition_created: bool
    schema_version: str = SLICE39D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateRequestedActDescription:
    requested_act_id: str
    action_predicate_candidate_id: str
    action_root_id: str
    action_root_key: str
    action_root_version: str
    predicate_id: str
    predicate_key: str
    predicate_version: str
    frame_ids_and_versions: tuple[tuple[str, str], ...]
    role_layout_candidate_ids: tuple[str, ...]
    effect_boundary_ids_and_versions: tuple[tuple[str, str], ...]
    capability_reference_candidate_ids: tuple[str, ...]
    source_concept_candidate_ids: tuple[str, ...]
    source_sense_candidate_ids: tuple[str, ...]
    source_span_ids: tuple[str, ...]
    candidate_only: bool
    permission_granted: bool
    route_created: bool
    invocation_proposed: bool
    execution_performed: bool
    schema_version: str = SLICE39D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateSemanticRelationReference:
    reference_id: str
    relation_type_id: str
    relation_type_key: str
    relation_type_version: str
    relation_family_id: str
    source_concept_candidate_ids: tuple[str, ...]
    target_concept_candidate_ids: tuple[str, ...]
    source_record_ids: tuple[str, ...]
    source_span_ids: tuple[str, ...]
    candidate_only: bool
    relation_instance_asserted: bool
    truth_determined: bool
    evidence_validated: bool
    schema_version: str = SLICE39D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateReferentReference:
    referent_id: str
    kind: ReferentCandidateKind
    reference_analysis_id: str
    reference_candidate_id: str | None
    context_object_id: str | None
    exact_reference_form: str
    source_span_ids: tuple[str, ...]
    candidate_only: bool
    referent_resolved: bool
    selected: bool
    schema_version: str = SLICE39D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateSemanticDistinction:
    distinction_id: str
    kind: SemanticDistinctionKind
    distinction_code: str
    source_record_ids: tuple[str, ...]
    source_span_ids: tuple[str, ...]
    exact_source_fragments: tuple[str, ...]
    candidate_only: bool
    selected: bool
    outcome_created: bool
    schema_version: str = SLICE39D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateSemanticContentPayload:
    payload_id: str
    lineage_id: str
    communicative_purpose_ref: str
    communicative_force_candidates: tuple[CommunicativeForceCandidate, ...]
    requested_act_description_refs: tuple[str, ...]
    concept_candidate_refs: tuple[str, ...]
    sense_candidate_refs: tuple[str, ...]
    semantic_relation_candidate_refs: tuple[str, ...]
    action_root_candidate_refs: tuple[str, ...]
    predicate_candidate_refs: tuple[str, ...]
    frame_candidate_refs: tuple[str, ...]
    role_layout_candidate_refs: tuple[str, ...]
    referent_candidate_refs: tuple[str, ...]
    source_reference_refs: tuple[str, ...]
    comparison_target_reference_refs: tuple[str, ...]
    condition_refs: tuple[str, ...]
    negation_refs: tuple[str, ...]
    qualification_refs: tuple[str, ...]
    temporal_distinction_refs: tuple[str, ...]
    status_distinction_refs: tuple[str, ...]
    scope_refs: tuple[str, ...]
    attachment_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    missing_information_refs: tuple[str, ...]
    conflicting_information_refs: tuple[str, ...]
    authority_sensitive_implication_refs: tuple[str, ...]
    effect_boundary_refs: tuple[str, ...]
    capability_family_reference_refs: tuple[str, ...]
    candidate_only: bool
    selected_content: bool
    participant_assignments_created: bool
    referents_resolved: bool
    clarification_question_emitted: bool
    schema_version: str = SLICE39D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateSemanticContentAssembly:
    assembly_id: str
    lineage_id: str
    predecessor_custody: CandidateMeaningPredecessorCustody
    profile: CandidateSemanticContentProfileIdentity
    communicative_purpose: CandidateCommunicativePurpose
    requested_act_descriptions: tuple[CandidateRequestedActDescription, ...]
    semantic_relation_references: tuple[CandidateSemanticRelationReference, ...]
    referent_references: tuple[CandidateReferentReference, ...]
    distinctions: tuple[CandidateSemanticDistinction, ...]
    payload: CandidateSemanticContentPayload
    candidate_meaning_content: CandidateMeaningContent
    exact_predecessor_custody_verified: bool
    exact_candidate_references_verified: bool
    exact_registry_references_verified: bool
    exact_source_span_support_verified: bool
    zero_one_many_preserved: bool
    candidate_semantic_content_assembled: bool
    participant_assignments_created: bool
    referents_resolved: bool
    clarification_question_emitted: bool
    candidate_ranked: bool
    candidate_selected: bool
    gate_progression_created: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    route_created: bool
    action_performed: bool
    memory_accessed: bool
    rendered: bool
    delivered: bool
    canonical_digest: str
    digest_algorithm: str = DIGEST_ALGORITHM
    schema_version: str = SLICE39D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateSemanticContentAssemblyResult:
    result_id: str
    status: CandidateSemanticContentStatus
    reason_code: str
    assembly: CandidateSemanticContentAssembly | None
    issues: tuple[CandidateSemanticContentValidationIssue, ...]
    source_event_id: str
    source_sha256: str
    lineage_id: str
    communicative_force_candidate_count: int
    requested_act_description_count: int
    semantic_relation_reference_count: int
    referent_reference_count: int
    distinction_count: int
    candidate_semantic_content_assembled: bool
    participant_assignments_created: bool
    referents_resolved: bool
    clarification_question_emitted: bool
    candidate_ranked: bool
    candidate_selected: bool
    gate_progression_created: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    route_created: bool
    action_performed: bool
    memory_accessed: bool
    rendered: bool
    delivered: bool
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    external_resource_loaded: bool
    language_model_used: bool
    embedding_used: bool
    semantic_similarity_used: bool
    schema_version: str = SLICE39D_SCHEMA_VERSION
