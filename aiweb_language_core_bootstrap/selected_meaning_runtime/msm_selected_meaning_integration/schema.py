"""Immutable Slice 41E MSM selected-meaning integration records."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ...meaning_structure_manifest import (
    ExternalAuthorityReferenceRecord,
    MeaningStructureManifestV1,
    SelectedGovernedMeaningRecord,
    SemanticTransitionTraceRecord,
)
from ...msm_gate_custody.schema import (
    MsmGateCustodyCompanionV1,
    MsmGateIntegrationResult,
)
from ..selected_meaning_construction.schema import (
    SelectedMeaningConstructionInput,
    SelectedMeaningConstructionPackage,
)
from .authority import (
    SLICE41E_ADAPTER_DECISION,
    SLICE41E_COMPANION_VERSION,
    SLICE41E_GOVERNING_AUTHORITY_REFS,
    SLICE41E_PERMANENT_BOUNDARIES,
    SLICE41E_PROFILE_KEY,
    SLICE41E_PROFILE_VERSION,
    SLICE41E_PROHIBITED_AUTHORITY,
    SLICE41E_RECEIPT_VERSION,
    SLICE41E_REQUIRED_EMPTY_SUCCESSOR_SECTIONS,
    SLICE41E_REQUIRED_PATH,
    SLICE41E_SCHEMA_VERSION,
    SLICE41E_SPEC_ID,
    SLICE41E_SPEC_VERSION,
)


class MsmSelectedMeaningIntegrationValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    PROFILE_MISMATCH = "profile_mismatch"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    SOURCE_GATE_RESULT_INVALID = "source_gate_result_invalid"
    SOURCE_MANIFEST_INVALID = "source_manifest_invalid"
    SLICE40H_CUSTODY_MISMATCH = "slice40h_custody_mismatch"
    SLICE41D_INPUT_INVALID = "slice41d_input_invalid"
    SLICE41D_PACKAGE_INVALID = "slice41d_package_invalid"
    CANDIDATE_MISMATCH = "candidate_mismatch"
    LINEAGE_MISMATCH = "lineage_mismatch"
    SELECTION_AUTHORITY_MISMATCH = "selection_authority_mismatch"
    SEMANTIC_CONTENT_MISMATCH = "semantic_content_mismatch"
    RETENTION_MISMATCH = "retention_mismatch"
    TRANSITION_MISMATCH = "transition_mismatch"
    SUCCESSOR_MANIFEST_INVALID = "successor_manifest_invalid"
    IDENTITY_MISMATCH = "identity_mismatch"
    DUPLICATE_ID = "duplicate_id"
    PROHIBITED_AUTHORITY = "prohibited_authority"
    DOWNSTREAM_AUTHORITY = "downstream_authority"
    CANONICAL_MISMATCH = "canonical_mismatch"


@dataclass(frozen=True, slots=True)
class MsmSelectedMeaningIntegrationValidationIssue:
    path: str
    code: MsmSelectedMeaningIntegrationValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class MsmSelectedMeaningIntegrationValidationReport:
    issues: tuple[MsmSelectedMeaningIntegrationValidationIssue, ...]
    schema_version: str = SLICE41E_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class MsmSelectedMeaningIntegrationValidationError(ValueError):
    def __init__(self, report: MsmSelectedMeaningIntegrationValidationReport) -> None:
        self.report = report
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(detail or "Slice 41E MSM selected-meaning integration failed")


@dataclass(frozen=True, slots=True)
class MsmSelectedMeaningIntegrationAuthorityProfile:
    profile_id: str
    profile_key: str
    profile_version: str
    governing_authority_refs: tuple[str, ...]
    exact_slice40h_result_required: bool
    exact_slice40h_companion_required: bool
    exact_slice41d_input_required: bool
    exact_slice41d_package_required: bool
    exact_selected_candidate_required: bool
    exact_selection_receipt_required: bool
    immutable_successor_required: bool
    lawful_lifecycle_transition_required: bool
    candidate_retention_required: bool
    non_selection_retention_required: bool
    gate_ancestry_retention_required: bool
    complete_successor_validation_required: bool
    versioned_companion_required: bool
    deterministic_receipt_required: bool
    fail_closed: bool
    msm_schema_rewrite_allowed: bool
    automatic_migration_allowed: bool
    candidate_deletion_allowed: bool
    non_selection_deletion_allowed: bool
    gate_custody_deletion_allowed: bool
    governed_result_allowed: bool
    outward_meaning_allowed: bool
    expression_link_allowed: bool
    validation_link_allowed: bool
    delivery_link_allowed: bool
    truth_evidence_allowed: bool
    permission_execution_allowed: bool
    route_tool_action_memory_rendering_delivery_allowed: bool
    bootstrap_integration_allowed: bool
    adapter_decision: str = SLICE41E_ADAPTER_DECISION
    required_path: tuple[str, ...] = SLICE41E_REQUIRED_PATH
    permanent_boundaries: tuple[str, ...] = SLICE41E_PERMANENT_BOUNDARIES
    prohibited_authority: tuple[str, ...] = SLICE41E_PROHIBITED_AUTHORITY
    required_empty_successor_sections: tuple[str, ...] = (
        SLICE41E_REQUIRED_EMPTY_SUCCESSOR_SECTIONS
    )
    spec_id: str = SLICE41E_SPEC_ID
    spec_version: str = SLICE41E_SPEC_VERSION
    schema_version: str = SLICE41E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class MsmSelectedMeaningIntegrationInput:
    integration_input_id: str
    source_gate_integration_result: MsmGateIntegrationResult
    selected_meaning_construction_input: SelectedMeaningConstructionInput
    selected_meaning_package: SelectedMeaningConstructionPackage
    authority_profile: MsmSelectedMeaningIntegrationAuthorityProfile
    semantic_transition_reason: str
    version_refs: tuple[str, ...]
    msm_schema_rewrite_requested: bool
    automatic_migration_requested: bool
    candidate_deletion_requested: bool
    non_selection_deletion_requested: bool
    gate_custody_deletion_requested: bool
    governed_result_requested: bool
    outward_meaning_requested: bool
    expression_link_requested: bool
    validation_link_requested: bool
    delivery_link_requested: bool
    truth_claim_requested: bool
    evidence_claim_requested: bool
    permission_requested: bool
    execution_requested: bool
    route_requested: bool
    tool_requested: bool
    action_requested: bool
    memory_access_requested: bool
    memory_write_requested: bool
    rendering_requested: bool
    delivery_requested: bool
    bootstrap_integration_requested: bool
    schema_version: str = SLICE41E_SCHEMA_VERSION

    @property
    def source_manifest(self) -> MeaningStructureManifestV1:
        value = self.source_gate_integration_result.successor_manifest
        assert isinstance(value, MeaningStructureManifestV1)
        return value

    @property
    def slice40h_companion(self) -> MsmGateCustodyCompanionV1:
        return self.source_gate_integration_result.companion


@dataclass(frozen=True, slots=True)
class MsmSelectedMeaningCustodyCompanionV1:
    companion_id: str
    companion_version: str
    integration_input_ref: str
    source_manifest_id: str
    successor_manifest_id: str
    lineage_id: str
    selected_candidate_ref: str
    dormant_selected_meaning_ref: str
    integrated_selected_meaning_ref: str
    selection_eligibility_result_ref: str
    selection_decision_ref: str
    selection_trace_ref: str
    selection_receipt_ref: str
    content_proof_ref: str
    selection_authority_reference_record_ref: str
    slice40h_companion_ref: str
    slice40h_custody_companion: MsmGateCustodyCompanionV1
    candidate_refs_before: tuple[str, ...]
    candidate_refs_after: tuple[str, ...]
    non_selection_outcome_refs_before: tuple[str, ...]
    non_selection_outcome_refs_after: tuple[str, ...]
    source_external_authority_refs: tuple[str, ...]
    added_external_authority_refs: tuple[str, ...]
    source_transition_trace_refs: tuple[str, ...]
    added_transition_trace_refs: tuple[str, ...]
    preserved_alternative_refs: tuple[str, ...]
    unresolved_alternative_refs: tuple[str, ...]
    candidate_ancestry_refs: tuple[str, ...]
    gate_ancestry_refs: tuple[str, ...]
    exact_adapter: bool
    lossless_custody: bool
    immutable_successor: bool
    selected_record_integrated: bool
    selection_authority_receipt_bound: bool
    candidate_ancestry_preserved: bool
    gate_ancestry_preserved: bool
    all_candidate_meanings_retained: bool
    all_non_selection_outcomes_retained: bool
    slice40h_companion_retained: bool
    complete_successor_manifest_validated: bool
    msm_schema_modified: bool
    automatic_migration_performed: bool
    schema_version: str = SLICE41E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class MsmSelectedMeaningIntegrationReceiptV1:
    receipt_id: str
    receipt_version: str
    integration_input_ref: str
    source_manifest_ref: str
    successor_manifest_ref: str
    source_gate_integration_result_ref: str
    slice40h_companion_ref: str
    slice41d_package_ref: str
    slice41d_selection_receipt_ref: str
    selection_authority_reference_record_ref: str
    selected_candidate_ref: str
    integrated_selected_meaning_ref: str
    semantic_transition_trace_ref: str
    source_manifest_sha256: str
    successor_manifest_sha256: str
    candidate_count_before: int
    candidate_count_after: int
    non_selection_count_before: int
    non_selection_count_after: int
    selected_count_before: int
    selected_count_after: int
    deterministic: bool
    immutable_successor_created: bool
    selected_meaning_integrated: bool
    complete_manifest_validated: bool
    candidates_retained: bool
    non_selection_outcomes_retained: bool
    slice40h_companion_retained: bool
    msm_schema_modified: bool
    governed_outward_meaning_created: bool
    expression_link_created: bool
    validation_link_created: bool
    delivery_link_created: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed: bool
    memory_written: bool
    rendered: bool
    delivered: bool
    schema_version: str = SLICE41E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class MsmSelectedMeaningIntegrationResult:
    result_id: str
    canonical_digest: str
    integration_input_ref: str
    source_manifest: MeaningStructureManifestV1
    successor_manifest: MeaningStructureManifestV1
    authority_reference_record: ExternalAuthorityReferenceRecord
    integrated_selected_meaning_record: SelectedGovernedMeaningRecord
    semantic_transition_trace: SemanticTransitionTraceRecord
    companion: MsmSelectedMeaningCustodyCompanionV1
    receipt: MsmSelectedMeaningIntegrationReceiptV1
    deterministic: bool
    additive_only: bool
    immutable_successor_created: bool
    exact_slice40h_custody_preserved: bool
    exact_slice41d_package_preserved: bool
    exact_selected_candidate_preserved: bool
    exact_selection_receipt_bound: bool
    candidate_and_gate_ancestry_preserved: bool
    all_candidate_meanings_retained: bool
    all_non_selection_outcomes_retained: bool
    complete_successor_manifest_validated: bool
    selected_meaning_integrated: bool
    msm_schema_modified: bool
    automatic_migration_performed: bool
    candidate_deleted: bool
    non_selection_outcome_deleted: bool
    gate_custody_deleted: bool
    governed_result_reference_created: bool
    governed_outward_meaning_created: bool
    expression_link_created: bool
    validation_link_created: bool
    delivery_link_created: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    capability_availability_created: bool
    route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed: bool
    memory_written: bool
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
    bootstrap_integration_enabled: bool
    digest_algorithm: str = "sha256"
    schema_version: str = SLICE41E_SCHEMA_VERSION


APPROVED_STRICT_PROFILE = MsmSelectedMeaningIntegrationAuthorityProfile(
    profile_id="pending",
    profile_key=SLICE41E_PROFILE_KEY,
    profile_version=SLICE41E_PROFILE_VERSION,
    governing_authority_refs=SLICE41E_GOVERNING_AUTHORITY_REFS,
    exact_slice40h_result_required=True,
    exact_slice40h_companion_required=True,
    exact_slice41d_input_required=True,
    exact_slice41d_package_required=True,
    exact_selected_candidate_required=True,
    exact_selection_receipt_required=True,
    immutable_successor_required=True,
    lawful_lifecycle_transition_required=True,
    candidate_retention_required=True,
    non_selection_retention_required=True,
    gate_ancestry_retention_required=True,
    complete_successor_validation_required=True,
    versioned_companion_required=True,
    deterministic_receipt_required=True,
    fail_closed=True,
    msm_schema_rewrite_allowed=False,
    automatic_migration_allowed=False,
    candidate_deletion_allowed=False,
    non_selection_deletion_allowed=False,
    gate_custody_deletion_allowed=False,
    governed_result_allowed=False,
    outward_meaning_allowed=False,
    expression_link_allowed=False,
    validation_link_allowed=False,
    delivery_link_allowed=False,
    truth_evidence_allowed=False,
    permission_execution_allowed=False,
    route_tool_action_memory_rendering_delivery_allowed=False,
    bootstrap_integration_allowed=False,
)

__all__ = tuple(name for name in globals() if not name.startswith("_"))
