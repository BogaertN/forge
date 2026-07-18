"""Immutable exact-input records for the Slice 39F constructor."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ...candidate_resonant_phase_trail import CandidateResonantPhaseTrailResult
from ...deterministic_structural_derivation import DeterministicStructuralDerivationResult
from ...input_event_custody import InputEventCaptureResult
from ...resonant_operator_candidate_binding import ResonantOperatorCandidateBindingResult
from ...scope_attachment_reference_constraints import ScopeAttachmentReferenceConstraintResult
from ...source_field_projection import SourceFieldProjectionResult
from ...structural_concept_candidate_proposal import StructuralConceptCandidateProposalResult
from ...predicate_role_frame_registry.predicate_role_frame_candidate_proposal import (
    PredicateRoleFrameCandidateProposalResult,
)
from ..candidate_semantic_content import (
    CandidateSemanticContentAssembly,
    CandidateSemanticRelationReference,
)
from ..candidate_set_preservation import CandidateSetMember, CandidateSetPreservationResult
from ..predecessor_custody import CandidateMeaningPredecessorCustody
from ..schema import CandidateMeaningConstructionReceipt, CandidateMeaningState
from .authority import (
    SLICE39F_PERMANENT_BOUNDARIES,
    SLICE39F_PROFILE_VERSION,
    SLICE39F_PROHIBITED_AUTHORITY,
    SLICE39F_REQUIRED_PATH,
    SLICE39F_SCHEMA_VERSION,
    SLICE39F_SPEC_ID,
    SLICE39F_SPEC_VERSION,
)


class CandidateMeaningConstructorStatus(str, Enum):
    CONSTRUCTED = "constructed"
    ZERO_CANDIDATES = "zero_candidates"
    REJECTED = "rejected"


class CandidateMeaningConstructorValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    PROFILE_MISMATCH = "profile_mismatch"
    PREDECESSOR_REJECTED = "predecessor_rejected"
    CONTENT_ASSEMBLY_REJECTED = "content_assembly_rejected"
    CANDIDATE_SET_REJECTED = "candidate_set_rejected"
    SOURCE_MISMATCH = "source_mismatch"
    SNAPSHOT_MISMATCH = "snapshot_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    COUNT_MISMATCH = "count_mismatch"
    DOWNSTREAM_AUTHORITY = "downstream_authority"
    CANONICAL_MISMATCH = "canonical_mismatch"


@dataclass(frozen=True, slots=True)
class CandidateMeaningConstructorValidationIssue:
    path: str
    code: CandidateMeaningConstructorValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class CandidateMeaningConstructorProfile:
    profile_id: str
    profile_key: str
    profile_version: str
    explicitly_invoked: bool
    exact_input_types_required: bool
    offline_only: bool
    standard_library_only: bool
    read_only: bool
    deterministic: bool
    in_memory_only: bool
    source_preserving: bool
    fail_closed: bool
    raw_text_inspection_allowed: bool
    similarity_allowed: bool
    nearest_known_fallback_allowed: bool
    hidden_repair_allowed: bool
    ranking_allowed: bool
    selection_allowed: bool
    ambiguity_resolution_allowed: bool
    gate_outcome_allowed: bool
    manifest_integration_allowed: bool
    bootstrap_integration_allowed: bool
    truth_evidence_permission_allowed: bool
    route_action_memory_rendering_delivery_allowed: bool
    required_path: tuple[str, ...] = SLICE39F_REQUIRED_PATH
    permanent_boundaries: tuple[str, ...] = SLICE39F_PERMANENT_BOUNDARIES
    prohibited_authority: tuple[str, ...] = SLICE39F_PROHIBITED_AUTHORITY
    spec_id: str = SLICE39F_SPEC_ID
    spec_version: str = SLICE39F_SPEC_VERSION
    schema_version: str = SLICE39F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateMeaningConstructorInput:
    custody: InputEventCaptureResult
    projection: SourceFieldProjectionResult
    binding: ResonantOperatorCandidateBindingResult
    trails: CandidateResonantPhaseTrailResult
    constraints: ScopeAttachmentReferenceConstraintResult
    structural: DeterministicStructuralDerivationResult
    slice37: StructuralConceptCandidateProposalResult
    slice38: PredicateRoleFrameCandidateProposalResult
    semantic_relation_references: tuple[CandidateSemanticRelationReference, ...] = ()


@dataclass(frozen=True, slots=True)
class CandidateMeaningConstructedRecord:
    record_id: str
    candidate_result_id: str
    predecessor_custody: CandidateMeaningPredecessorCustody
    semantic_content_assembly: CandidateSemanticContentAssembly
    candidate_set_member: CandidateSetMember
    candidate_meaning_state: CandidateMeaningState
    construction_receipt: CandidateMeaningConstructionReceipt
    deterministic_position: int
    duplicate_occurrence_count: int
    exact_typed_predecessors_verified: bool
    exact_ancestry_verified: bool
    exact_snapshots_verified: bool
    source_preserved: bool
    schema_version: str = SLICE39F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateMeaningConstructorResult:
    result_id: str
    status: CandidateMeaningConstructorStatus
    reason_code: str
    profile: CandidateMeaningConstructorProfile
    candidate_set_result: CandidateSetPreservationResult
    constructed_records: tuple[CandidateMeaningConstructedRecord, ...]
    construction_receipts: tuple[CandidateMeaningConstructionReceipt, ...]
    issues: tuple[CandidateMeaningConstructorValidationIssue, ...]
    input_count: int
    unique_candidate_count: int
    exact_duplicate_occurrence_count: int
    source_event_ids: tuple[str, ...]
    source_sha256s: tuple[str, ...]
    explicitly_invoked: bool
    exact_input_types_verified: bool
    exact_ancestry_verified: bool
    exact_snapshots_verified: bool
    source_preserved: bool
    offline: bool
    standard_library_only: bool
    read_only: bool
    deterministic: bool
    in_memory_only: bool
    fail_closed: bool
    raw_text_inspected: bool
    similarity_used: bool
    nearest_known_fallback_used: bool
    hidden_repair_used: bool
    candidate_ranked: bool
    candidate_selected: bool
    ambiguity_resolved: bool
    gate_outcome_created: bool
    selected_meaning_created: bool
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
    vector_used: bool
    rag_used: bool
    semantic_similarity_used: bool
    manifest_integrated: bool
    bootstrap_integrated: bool
    slice39_closeout_created: bool
    canonical_digest: str
    digest_algorithm: str = "sha256"
    schema_version: str = SLICE39F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateMeaningConstructorValidationReport:
    issues: tuple[CandidateMeaningConstructorValidationIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues


class CandidateMeaningConstructorValidationError(ValueError):
    def __init__(self, report: CandidateMeaningConstructorValidationReport):
        self.report = report
        super().__init__("Slice 39F constructor validation failed")


__all__ = (
    "CandidateMeaningConstructedRecord",
    "CandidateMeaningConstructorInput",
    "CandidateMeaningConstructorProfile",
    "CandidateMeaningConstructorResult",
    "CandidateMeaningConstructorStatus",
    "CandidateMeaningConstructorValidationCode",
    "CandidateMeaningConstructorValidationError",
    "CandidateMeaningConstructorValidationIssue",
    "CandidateMeaningConstructorValidationReport",
)
