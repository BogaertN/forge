"""Immutable Slice 39G MSM-v1 candidate-integration records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ...meaning_structure_manifest import MeaningStructureManifestV1
from ..deterministic_constructor import CandidateMeaningConstructorResult
from ..schema import CandidateMeaningConstructionStatus
from .authority import (
    SLICE39G_ADAPTER_DECISION,
    SLICE39G_ADAPTER_DECISION_REASONS,
    SLICE39G_COMPANION_VERSION,
    SLICE39G_PERMANENT_BOUNDARIES,
    SLICE39G_PROFILE_VERSION,
    SLICE39G_PROHIBITED_AUTHORITY,
    SLICE39G_REQUIRED_EMPTY_MANIFEST_SECTIONS,
    SLICE39G_REQUIRED_PATH,
    SLICE39G_SCHEMA_VERSION,
    SLICE39G_SPEC_ID,
    SLICE39G_SPEC_VERSION,
)


class ManifestCandidateIntegrationStatus(str, Enum):
    INTEGRATED = "integrated"
    ZERO_CANDIDATES = "zero_candidates"
    REJECTED = "rejected"


class ManifestCandidateIntegrationValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    PROFILE_MISMATCH = "profile_mismatch"
    CONSTRUCTOR_RESULT_REJECTED = "constructor_result_rejected"
    SOURCE_LINEAGE_MISMATCH = "source_lineage_mismatch"
    UNKNOWN_PRESERVATION_CLASS = "unknown_preservation_class"
    IDENTITY_MISMATCH = "identity_mismatch"
    COUNT_MISMATCH = "count_mismatch"
    MANIFEST_INVALID = "manifest_invalid"
    COMPANION_INVALID = "companion_invalid"
    REFERENCE_MISMATCH = "reference_mismatch"
    REQUIRED_SECTION_NOT_EMPTY = "required_section_not_empty"
    DOWNSTREAM_AUTHORITY = "downstream_authority"
    CANONICAL_MISMATCH = "canonical_mismatch"


@dataclass(frozen=True, slots=True)
class ManifestCandidateIntegrationValidationIssue:
    path: str
    code: ManifestCandidateIntegrationValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class ManifestCandidateIntegrationProfile:
    profile_id: str
    profile_key: str
    profile_version: str
    explicitly_invoked: bool
    exact_slice39f_result_required: bool
    exact_msm_v1_schema_required: bool
    versioned_companion_required: bool
    existing_msm_schema_modification_allowed: bool
    automatic_migration_allowed: bool
    candidate_side_only: bool
    offline_only: bool
    standard_library_only: bool
    read_only: bool
    deterministic: bool
    in_memory_only: bool
    source_preserving: bool
    fail_closed: bool
    gate_outcome_allowed: bool
    selected_meaning_allowed: bool
    governed_result_allowed: bool
    outward_meaning_allowed: bool
    expression_validation_delivery_allowed: bool
    bootstrap_integration_allowed: bool
    slice39_closeout_allowed: bool
    truth_evidence_permission_allowed: bool
    route_action_memory_rendering_delivery_allowed: bool
    adapter_decision: str = SLICE39G_ADAPTER_DECISION
    adapter_decision_reasons: tuple[str, ...] = SLICE39G_ADAPTER_DECISION_REASONS
    required_path: tuple[str, ...] = SLICE39G_REQUIRED_PATH
    required_empty_manifest_sections: tuple[str, ...] = (
        SLICE39G_REQUIRED_EMPTY_MANIFEST_SECTIONS
    )
    permanent_boundaries: tuple[str, ...] = SLICE39G_PERMANENT_BOUNDARIES
    prohibited_authority: tuple[str, ...] = SLICE39G_PROHIBITED_AUTHORITY
    spec_id: str = SLICE39G_SPEC_ID
    spec_version: str = SLICE39G_SPEC_VERSION
    schema_version: str = SLICE39G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateConstructionTraceReferenceV1:
    trace_reference_id: str
    manifest_candidate_record_id: str
    candidate_meaning_id: str
    candidate_lineage_id: str
    candidate_state_id: str
    constructor_record_id: str
    constructor_result_id: str
    construction_receipt_id: str
    deterministic_position: int
    duplicate_occurrence_count: int
    exact_typed_predecessors_verified: bool
    exact_ancestry_verified: bool
    exact_snapshots_verified: bool
    source_preserved: bool
    schema_version: str = SLICE39G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateProvenanceReferenceV1:
    provenance_reference_id: str
    manifest_candidate_record_id: str
    candidate_meaning_id: str
    candidate_lineage_id: str
    candidate_provenance_id: str
    predecessor_custody_id: str
    source_event_id: str
    source_sha256: str
    input_event_id: str
    root_source_span_id: str
    slice37_result_id: str
    slice37_registry_snapshot_id: str
    slice38_result_id: str
    slice38_registry_snapshot_id: str
    compatibility_registry_snapshot_id: str
    predecessor_result_ids: tuple[str, ...]
    predecessor_receipt_ids: tuple[str, ...]
    source_span_reference_ids: tuple[str, ...]
    structural_rule_reference_ids: tuple[str, ...]
    operator_reference_ids: tuple[str, ...]
    registry_resource_reference_ids: tuple[str, ...]
    exact_ancestry_verified: bool
    exact_snapshots_verified: bool
    source_preserved: bool
    schema_version: str = SLICE39G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateLimitationReferenceV1:
    limitation_reference_id: str
    manifest_candidate_record_id: str
    candidate_meaning_id: str
    candidate_lineage_id: str
    construction_status: CandidateMeaningConstructionStatus
    status_reason_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    unresolved_alternative_refs: tuple[str, ...]
    unresolved_referent_refs: tuple[str, ...]
    missing_role_refs: tuple[str, ...]
    conflicting_role_refs: tuple[str, ...]
    unsupported_reason_refs: tuple[str, ...]
    unknown_reason_refs: tuple[str, ...]
    authority_sensitive_implication_refs: tuple[str, ...]
    candidate_only: bool
    clarification_required_created: bool
    ambiguity_outcome_created: bool
    refusal_created: bool
    schema_version: str = SLICE39G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateAlternativeRelationshipV1:
    relationship_id: str
    source_manifest_candidate_record_id: str
    alternative_manifest_candidate_record_id: str
    source_candidate_meaning_id: str
    alternative_candidate_meaning_id: str
    source_alternative_reference_id: str
    alternative_kind: str
    shared_ancestry_refs: tuple[str, ...]
    differing_content_refs: tuple[str, ...]
    unresolved_reason_refs: tuple[str, ...]
    candidate_only: bool
    ranking_assigned: bool
    preferred_candidate_assigned: bool
    selected_alternative: bool
    ambiguous_gate_disposition_created: bool
    schema_version: str = SLICE39G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateMeaningManifestCompanionV1:
    companion_id: str
    companion_version: str
    manifest_candidate_record_id: str
    candidate_meaning_id: str
    candidate_lineage_id: str
    candidate_state_id: str
    candidate_identity_ref: str
    candidate_content_ref: str
    candidate_provenance_ref: str
    construction_receipt_ref: str
    construction_trace_reference_id: str
    provenance_reference_id: str
    limitation_reference_id: str
    alternative_relationship_ids: tuple[str, ...]
    exact_adapter: bool
    lossless_custody: bool
    candidate_side_only: bool
    selected_meaning_created: bool
    gate_outcome_created: bool
    schema_version: str = SLICE39G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ManifestCandidateIntegrationResult:
    result_id: str
    status: ManifestCandidateIntegrationStatus
    reason_code: str
    profile: ManifestCandidateIntegrationProfile
    constructor_result_id: str
    manifest: MeaningStructureManifestV1 | None
    companions: tuple[CandidateMeaningManifestCompanionV1, ...]
    construction_trace_references: tuple[CandidateConstructionTraceReferenceV1, ...]
    provenance_references: tuple[CandidateProvenanceReferenceV1, ...]
    limitation_references: tuple[CandidateLimitationReferenceV1, ...]
    alternative_relationships: tuple[CandidateAlternativeRelationshipV1, ...]
    issues: tuple[ManifestCandidateIntegrationValidationIssue, ...]
    source_event_ids: tuple[str, ...]
    source_sha256s: tuple[str, ...]
    input_candidate_count: int
    manifest_candidate_count: int
    explicitly_invoked: bool
    exact_constructor_result_verified: bool
    exact_msm_v1_verified: bool
    versioned_companion_used: bool
    lossless_companion_custody: bool
    candidate_side_only: bool
    manifest_integrated: bool
    existing_msm_schema_modified: bool
    automatic_migration_performed: bool
    non_selection_outcome_created: bool
    selected_governed_meaning_created: bool
    governed_result_reference_created: bool
    governed_outward_meaning_created: bool
    expression_link_created: bool
    validation_link_created: bool
    delivery_link_created: bool
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
    bootstrap_integrated: bool
    slice39_closeout_created: bool
    canonical_digest: str
    digest_algorithm: str = "sha256"
    schema_version: str = SLICE39G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ManifestCandidateIntegrationValidationReport:
    issues: tuple[ManifestCandidateIntegrationValidationIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues


class ManifestCandidateIntegrationValidationError(ValueError):
    def __init__(self, report: ManifestCandidateIntegrationValidationReport):
        self.report = report
        super().__init__("Slice 39G manifest candidate integration validation failed")


__all__ = (
    "CandidateAlternativeRelationshipV1",
    "CandidateConstructionTraceReferenceV1",
    "CandidateLimitationReferenceV1",
    "CandidateMeaningManifestCompanionV1",
    "CandidateProvenanceReferenceV1",
    "ManifestCandidateIntegrationProfile",
    "ManifestCandidateIntegrationResult",
    "ManifestCandidateIntegrationStatus",
    "ManifestCandidateIntegrationValidationCode",
    "ManifestCandidateIntegrationValidationError",
    "ManifestCandidateIntegrationValidationIssue",
    "ManifestCandidateIntegrationValidationReport",
)
