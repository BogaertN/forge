"""Immutable Slice 39E candidate-set and alternative-preservation records.

This package preserves zero, one, or multiple exact Slice 39D candidate semantic
content records.  It does not rank, score, prefer, select, resolve ambiguity,
create an AmbiguousMeaningState, evaluate gates, determine truth or evidence,
grant permission, create routes, invoke tools, perform actions, access memory,
render output, or deliver anything.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..candidate_semantic_content.schema import CandidateSemanticContentAssemblyResult


SLICE39E_ACCEPTED_PARENT_HEAD = "6081cc15bd7f13b1471a12616350b1acfeda7cdd"
SLICE39E_ACCEPTED_PARENT_TREE = "f379b92f1258e3f6b0d675d690ba31f289774f3c"
SLICE39E_ACCEPTED_PARENT_SUBJECT = "Slice 39D candidate semantic content assembly"
SLICE39E_SPEC_ID = "aiweb-slice39e-candidate-set-alternative-preservation"
SLICE39E_SPEC_VERSION = "aiweb-slice39e-candidate-set-alternative-preservation-v1"
SLICE39E_SCHEMA_VERSION = "aiweb-language-core-slice39e-candidate-set-alternative-preservation-v1"
SLICE39E_PROFILE_VERSION = "v1.0.0"
DIGEST_ALGORITHM = "sha256"


class CandidateSetStatus(str, Enum):
    ZERO_CANDIDATES = "zero_candidates"
    ONE_CANDIDATE = "one_candidate"
    MULTIPLE_CANDIDATES = "multiple_candidates"
    SET_REJECTED = "set_rejected"


class CandidateSetValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_TUPLE = "invalid_tuple"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_SHA256 = "invalid_sha256"
    INVALID_VERSION = "invalid_version"
    INVALID_ENUM = "invalid_enum"
    INVALID_INTEGER = "invalid_integer"
    INVALID_BOOLEAN = "invalid_boolean"
    INVALID_ORDER = "invalid_order"
    DUPLICATE_VALUE = "duplicate_value"
    IDENTITY_MISMATCH = "identity_mismatch"
    PROFILE_MISMATCH = "profile_mismatch"
    CANDIDATE_RESULT_INVALID = "candidate_result_invalid"
    CANDIDATE_NOT_ASSEMBLED = "candidate_not_assembled"
    SOURCE_EVENT_MISMATCH = "source_event_mismatch"
    SOURCE_CHECKSUM_MISMATCH = "source_checksum_mismatch"
    MEMBER_MAPPING_MISMATCH = "member_mapping_mismatch"
    DUPLICATE_MAPPING_MISMATCH = "duplicate_mapping_mismatch"
    ALTERNATIVE_MAPPING_MISMATCH = "alternative_mapping_mismatch"
    SHARED_ANCESTRY_MISMATCH = "shared_ancestry_mismatch"
    COUNT_MISMATCH = "count_mismatch"
    SILENT_COLLAPSE_PROHIBITED = "silent_collapse_prohibited"
    RANKING_PROHIBITED = "ranking_prohibited"
    CONFIDENCE_SCORING_PROHIBITED = "confidence_scoring_prohibited"
    PREFERENCE_PROHIBITED = "preference_prohibited"
    SELECTION_PROHIBITED = "selection_prohibited"
    TIE_BREAKING_PROHIBITED = "tie_breaking_prohibited"
    AMBIGUITY_RESOLUTION_PROHIBITED = "ambiguity_resolution_prohibited"
    AMBIGUOUS_STATE_PROHIBITED = "ambiguous_state_prohibited"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"


@dataclass(frozen=True, slots=True)
class CandidateSetValidationIssue:
    path: str
    code: CandidateSetValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class CandidateSetValidationReport:
    issues: tuple[CandidateSetValidationIssue, ...]
    schema_version: str = SLICE39E_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class CandidateSetValidationError(ValueError):
    def __init__(self, report: CandidateSetValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}" for item in report.issues
        )
        super().__init__(summary or "Slice 39E candidate set rejected")


@dataclass(frozen=True, slots=True)
class CandidateSetProfileIdentity:
    profile_id: str
    profile_key: str
    profile_version: str
    zero_one_many_preservation_required: bool
    deterministic_ordering_required: bool
    exact_duplicate_detection_required: bool
    duplicate_occurrence_preservation_required: bool
    material_alternative_references_required: bool
    shared_ancestry_preservation_required: bool
    candidate_specific_boundaries_required: bool
    ranking_allowed: bool
    confidence_scoring_allowed: bool
    preferred_candidate_allowed: bool
    winner_selection_allowed: bool
    nearest_candidate_allowed: bool
    tie_breaking_allowed: bool
    automatic_ambiguity_resolution_allowed: bool
    ambiguous_meaning_state_creation_allowed: bool
    gate_progression_allowed: bool
    truth_evidence_permission_allowed: bool
    route_action_memory_rendering_delivery_allowed: bool
    spec_id: str = SLICE39E_SPEC_ID
    spec_version: str = SLICE39E_SPEC_VERSION
    schema_version: str = SLICE39E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateSetMember:
    member_id: str
    deterministic_position: int
    duplicate_occurrence_index: int
    candidate_result_id: str
    candidate_assembly_id: str
    candidate_payload_id: str
    candidate_content_id: str
    candidate_canonical_digest: str
    lineage_id: str
    source_event_id: str
    source_sha256: str
    source_span_ids: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    missing_role_refs: tuple[str, ...]
    conflicting_role_refs: tuple[str, ...]
    effect_boundary_refs: tuple[str, ...]
    capability_reference_refs: tuple[str, ...]
    candidate_only: bool
    exact_duplicate_detected: bool
    ranked: bool
    confidence_scored: bool
    preferred: bool
    selected: bool
    ambiguous_state_created: bool
    schema_version: str = SLICE39E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateExactDuplicateGroup:
    duplicate_group_id: str
    candidate_result_id: str
    canonical_candidate_digest: str
    primary_member_id: str
    duplicate_member_ids: tuple[str, ...]
    occurrence_count: int
    exact_duplicate: bool
    silently_collapsed: bool
    ranking_assigned: bool
    selected_candidate_assigned: bool
    schema_version: str = SLICE39E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateSharedAncestryReference:
    shared_ancestry_id: str
    member_ids: tuple[str, ...]
    source_event_id: str
    source_sha256: str
    lineage_ids: tuple[str, ...]
    shared_source_span_ids: tuple[str, ...]
    shared_structural_ancestry_ids: tuple[str, ...]
    shared_operator_definition_ids: tuple[str, ...]
    shared_concept_candidate_ids: tuple[str, ...]
    shared_sense_candidate_ids: tuple[str, ...]
    shared_action_predicate_candidate_ids: tuple[str, ...]
    shared_role_layout_candidate_ids: tuple[str, ...]
    shared_predecessor_receipt_ids: tuple[str, ...]
    ancestry_preserved: bool
    lineages_merged: bool
    schema_version: str = SLICE39E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateMaterialAlternativeReference:
    alternative_reference_id: str
    left_member_id: str
    right_member_id: str
    left_candidate_result_id: str
    right_candidate_result_id: str
    shared_ancestry_ref: str
    exact_difference_dimensions: tuple[str, ...]
    left_limitation_refs: tuple[str, ...]
    right_limitation_refs: tuple[str, ...]
    left_missing_role_refs: tuple[str, ...]
    right_missing_role_refs: tuple[str, ...]
    left_conflicting_role_refs: tuple[str, ...]
    right_conflicting_role_refs: tuple[str, ...]
    left_effect_boundary_refs: tuple[str, ...]
    right_effect_boundary_refs: tuple[str, ...]
    left_capability_reference_refs: tuple[str, ...]
    right_capability_reference_refs: tuple[str, ...]
    exact_duplicate: bool
    materially_distinct_by_exact_content: bool
    ambiguity_determined: bool
    ranked: bool
    preferred: bool
    selected: bool
    tie_broken: bool
    schema_version: str = SLICE39E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateMeaningSet:
    candidate_set_id: str
    status: CandidateSetStatus
    profile: CandidateSetProfileIdentity
    source_event_id: str | None
    source_sha256: str | None
    candidate_results: tuple[CandidateSemanticContentAssemblyResult, ...]
    members: tuple[CandidateSetMember, ...]
    exact_duplicate_groups: tuple[CandidateExactDuplicateGroup, ...]
    shared_ancestry_references: tuple[CandidateSharedAncestryReference, ...]
    material_alternative_references: tuple[CandidateMaterialAlternativeReference, ...]
    input_candidate_count: int
    unique_candidate_count: int
    exact_duplicate_occurrence_count: int
    alternative_reference_count: int
    deterministic_ordering_verified: bool
    exact_duplicate_detection_verified: bool
    duplicate_occurrences_preserved: bool
    shared_ancestry_preserved: bool
    candidate_specific_boundaries_preserved: bool
    candidates_ranked: bool
    confidence_scores_created: bool
    preferred_candidate_created: bool
    winner_selected: bool
    nearest_candidate_selected: bool
    tie_breaking_performed: bool
    ambiguity_resolved: bool
    ambiguous_meaning_state_created: bool
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
    schema_version: str = SLICE39E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateSetPreservationResult:
    result_id: str
    status: CandidateSetStatus
    reason_code: str
    candidate_set: CandidateMeaningSet | None
    issues: tuple[CandidateSetValidationIssue, ...]
    source_event_id: str | None
    source_sha256: str | None
    input_candidate_count: int
    unique_candidate_count: int
    exact_duplicate_occurrence_count: int
    alternative_reference_count: int
    zero_candidates_preserved: bool
    one_candidate_preserved_without_selection: bool
    multiple_candidates_preserved_independently: bool
    deterministic_ordering_verified: bool
    exact_duplicate_detection_verified: bool
    shared_ancestry_preserved: bool
    candidate_specific_boundaries_preserved: bool
    candidates_ranked: bool
    confidence_scores_created: bool
    preferred_candidate_created: bool
    winner_selected: bool
    nearest_candidate_selected: bool
    tie_breaking_performed: bool
    ambiguity_resolved: bool
    ambiguous_meaning_state_created: bool
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
    schema_version: str = SLICE39E_SCHEMA_VERSION
