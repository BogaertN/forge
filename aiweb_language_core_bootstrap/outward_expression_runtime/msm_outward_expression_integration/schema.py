"""Immutable Slice 42G MSM outward-expression integration records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ...meaning_structure_manifest import (
    ExpressionLinkRecord,
    ExternalAuthorityReferenceRecord,
    GovernedOutwardMeaningRecord,
    MeaningStructureManifestV1,
    SemanticTransitionTraceRecord,
)
from ...selected_meaning_runtime.msm_selected_meaning_integration import (
    MsmSelectedMeaningIntegrationInput,
    MsmSelectedMeaningIntegrationResult,
)
from ..surface_realization import (
    SurfaceRealizationInput,
    SurfaceRealizationResult,
    UnvalidatedExpressionCandidate,
)
from .authority import (
    DIGEST_ALGORITHM,
    SLICE42G_ADAPTER_DECISION,
    SLICE42G_ALLOWED_MSM_ADDITIONS,
    SLICE42G_COMPANION_VERSION,
    SLICE42G_GOVERNING_AUTHORITY_REFS,
    SLICE42G_PERMANENT_BOUNDARIES,
    SLICE42G_PROFILE_KEY,
    SLICE42G_PROFILE_VERSION,
    SLICE42G_PROHIBITED_AUTHORITY,
    SLICE42G_RECEIPT_VERSION,
    SLICE42G_REQUIRED_PATH,
    SLICE42G_REQUIRED_UNCHANGED_SECTIONS,
    SLICE42G_SCHEMA_VERSION,
    SLICE42G_SPEC_ID,
    SLICE42G_SPEC_VERSION,
)


class MsmOutwardExpressionIntegrationValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    PROFILE_MISMATCH = "profile_mismatch"
    SOURCE_CHAIN_INVALID = "source_chain_invalid"
    SOURCE_MANIFEST_INVALID = "source_manifest_invalid"
    SURFACE_REALIZATION_INVALID = "surface_realization_invalid"
    DORMANT_RECORD_MISMATCH = "dormant_record_mismatch"
    AUTHORITY_REFERENCE_MISMATCH = "authority_reference_mismatch"
    OUTWARD_MEANING_MISMATCH = "outward_meaning_mismatch"
    EXPRESSION_LINK_MISMATCH = "expression_link_mismatch"
    TRANSITION_MISMATCH = "transition_mismatch"
    RETENTION_MISMATCH = "retention_mismatch"
    SUCCESSOR_MANIFEST_INVALID = "successor_manifest_invalid"
    IDENTITY_MISMATCH = "identity_mismatch"
    DIGEST_MISMATCH = "digest_mismatch"
    DUPLICATE_ID = "duplicate_id"
    PROHIBITED_REQUEST = "prohibited_request"
    DOWNSTREAM_AUTHORITY = "downstream_authority"
    CANONICAL_MISMATCH = "canonical_mismatch"


@dataclass(frozen=True, slots=True)
class MsmOutwardExpressionIntegrationValidationIssue:
    path: str
    code: MsmOutwardExpressionIntegrationValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class MsmOutwardExpressionIntegrationValidationReport:
    issues: tuple[MsmOutwardExpressionIntegrationValidationIssue, ...]
    schema_version: str = SLICE42G_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class MsmOutwardExpressionIntegrationValidationError(ValueError):
    def __init__(
        self,
        report: MsmOutwardExpressionIntegrationValidationReport,
    ) -> None:
        self.report = report
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(detail or "Slice 42G MSM outward-expression integration failed")


@dataclass(frozen=True, slots=True)
class MsmOutwardExpressionIntegrationAuthorityProfile:
    profile_id: str
    profile_key: str
    profile_version: str
    governing_authority_refs: tuple[str, ...]
    exact_slice41e_input_required: bool
    exact_slice41e_result_required: bool
    exact_slice42f_input_required: bool
    exact_slice42f_result_required: bool
    exact_unvalidated_candidate_required: bool
    existing_dormant_msm_records_required: bool
    explicit_external_authority_reference_required: bool
    immutable_successor_required: bool
    selected_meaning_retention_required: bool
    candidate_retention_required: bool
    non_selection_retention_required: bool
    alternative_unresolved_retention_required: bool
    outward_meaning_record_allowed: bool
    expression_link_record_allowed: bool
    lifecycle_traces_required: bool
    complete_successor_validation_required: bool
    versioned_companion_required: bool
    deterministic_receipt_required: bool
    fail_closed: bool
    msm_schema_rewrite_allowed: bool
    automatic_migration_allowed: bool
    source_manifest_mutation_allowed: bool
    candidate_deletion_allowed: bool
    non_selection_deletion_allowed: bool
    selected_meaning_rewrite_allowed: bool
    governed_result_creation_allowed: bool
    validation_link_creation_allowed: bool
    delivery_link_creation_allowed: bool
    expression_candidate_rewrite_allowed: bool
    echo_validation_allowed: bool
    delivery_allowed: bool
    truth_evidence_permission_execution_allowed: bool
    route_tool_action_memory_filesystem_network_allowed: bool
    external_resource_or_model_authority_allowed: bool
    bootstrap_integration_allowed: bool
    gp014_supersession_allowed: bool
    adapter_decision: str = SLICE42G_ADAPTER_DECISION
    required_path: tuple[str, ...] = SLICE42G_REQUIRED_PATH
    permanent_boundaries: tuple[str, ...] = SLICE42G_PERMANENT_BOUNDARIES
    prohibited_authority: tuple[str, ...] = SLICE42G_PROHIBITED_AUTHORITY
    allowed_msm_additions: tuple[str, ...] = SLICE42G_ALLOWED_MSM_ADDITIONS
    required_unchanged_sections: tuple[str, ...] = SLICE42G_REQUIRED_UNCHANGED_SECTIONS
    spec_id: str = SLICE42G_SPEC_ID
    spec_version: str = SLICE42G_SPEC_VERSION
    schema_version: str = SLICE42G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class MsmOutwardExpressionIntegrationInput:
    integration_input_id: str
    source_selected_meaning_integration_input: MsmSelectedMeaningIntegrationInput
    source_selected_meaning_integration_result: MsmSelectedMeaningIntegrationResult
    surface_realization_input: SurfaceRealizationInput
    surface_realization_result: SurfaceRealizationResult
    authority_profile: MsmOutwardExpressionIntegrationAuthorityProfile
    outward_transition_reason: str
    expression_transition_reason: str
    version_refs: tuple[str, ...]
    msm_schema_rewrite_requested: bool
    automatic_migration_requested: bool
    source_manifest_mutation_requested: bool
    candidate_deletion_requested: bool
    non_selection_deletion_requested: bool
    selected_meaning_rewrite_requested: bool
    alternative_deletion_requested: bool
    unresolved_resolution_requested: bool
    governed_result_creation_requested: bool
    validation_link_creation_requested: bool
    delivery_link_creation_requested: bool
    expression_candidate_rewrite_requested: bool
    claim_strengthening_requested: bool
    certainty_upgrade_requested: bool
    evidence_status_upgrade_requested: bool
    caveat_omission_requested: bool
    refusal_softening_requested: bool
    ambiguity_erasure_requested: bool
    unsupported_state_erasure_requested: bool
    echo_validation_requested: bool
    delivery_requested: bool
    truth_evidence_permission_execution_requested: bool
    route_tool_action_memory_filesystem_network_requested: bool
    external_resource_or_model_authority_requested: bool
    bootstrap_integration_requested: bool
    gp014_supersession_requested: bool
    schema_version: str = SLICE42G_SCHEMA_VERSION

    @property
    def source_manifest(self) -> MeaningStructureManifestV1:
        return self.source_selected_meaning_integration_result.successor_manifest

    @property
    def expression_candidate(self) -> UnvalidatedExpressionCandidate:
        candidate = self.surface_realization_result.expression_candidate
        assert isinstance(candidate, UnvalidatedExpressionCandidate)
        return candidate


@dataclass(frozen=True, slots=True)
class MsmOutwardExpressionCustodyCompanionV1:
    companion_id: str
    companion_version: str
    integration_input_ref: str
    source_manifest_id: str
    source_manifest_sha256: str
    successor_manifest_id: str
    successor_manifest_sha256: str
    lineage_id: str
    selected_governed_meaning_ref: str
    surface_realization_input_ref: str
    surface_realization_result_ref: str
    expression_candidate_ref: str
    realization_trace_ref: str
    realization_receipt_ref: str
    external_authority_reference_record_ref: str
    integrated_governed_outward_meaning_ref: str
    integrated_expression_link_ref: str
    selected_to_outward_trace_ref: str
    outward_to_expression_trace_ref: str
    candidate_refs_before: tuple[str, ...]
    candidate_refs_after: tuple[str, ...]
    non_selection_refs_before: tuple[str, ...]
    non_selection_refs_after: tuple[str, ...]
    selected_refs_before: tuple[str, ...]
    selected_refs_after: tuple[str, ...]
    governed_result_refs_before: tuple[str, ...]
    governed_result_refs_after: tuple[str, ...]
    governed_outward_refs_before: tuple[str, ...]
    governed_outward_refs_after: tuple[str, ...]
    expression_link_refs_before: tuple[str, ...]
    expression_link_refs_after: tuple[str, ...]
    validation_link_refs_before: tuple[str, ...]
    validation_link_refs_after: tuple[str, ...]
    delivery_link_refs_before: tuple[str, ...]
    delivery_link_refs_after: tuple[str, ...]
    external_authority_refs_before: tuple[str, ...]
    external_authority_refs_after: tuple[str, ...]
    transition_trace_refs_before: tuple[str, ...]
    transition_trace_refs_after: tuple[str, ...]
    preserved_alternative_refs: tuple[str, ...]
    unresolved_condition_refs: tuple[str, ...]
    ancestry_refs: tuple[str, ...]
    exact_adapter: bool
    lossless_custody: bool
    immutable_successor: bool
    exact_slice41e_chain_preserved: bool
    exact_slice42f_candidate_preserved: bool
    selected_meaning_preserved: bool
    all_candidate_meanings_retained: bool
    all_non_selection_outcomes_retained: bool
    alternatives_and_unresolved_retained: bool
    governed_outward_meaning_integrated: bool
    expression_link_integrated: bool
    candidate_remains_unvalidated: bool
    complete_successor_manifest_validated: bool
    msm_schema_modified: bool
    automatic_migration_performed: bool
    schema_version: str = SLICE42G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class MsmOutwardExpressionIntegrationReceiptV1:
    receipt_id: str
    receipt_version: str
    integration_input_ref: str
    source_manifest_ref: str
    successor_manifest_ref: str
    source_slice41e_result_ref: str
    source_slice42f_result_ref: str
    source_slice42f_realization_receipt_ref: str
    selected_governed_meaning_ref: str
    expression_candidate_ref: str
    external_authority_reference_record_ref: str
    governed_outward_meaning_ref: str
    expression_link_ref: str
    selected_to_outward_trace_ref: str
    outward_to_expression_trace_ref: str
    source_manifest_sha256: str
    successor_manifest_sha256: str
    candidate_count_before: int
    candidate_count_after: int
    non_selection_count_before: int
    non_selection_count_after: int
    selected_count_before: int
    selected_count_after: int
    governed_result_count_before: int
    governed_result_count_after: int
    outward_meaning_count_before: int
    outward_meaning_count_after: int
    expression_link_count_before: int
    expression_link_count_after: int
    validation_link_count_before: int
    validation_link_count_after: int
    delivery_link_count_before: int
    delivery_link_count_after: int
    deterministic: bool
    additive_only: bool
    immutable_successor_created: bool
    complete_manifest_validated: bool
    selected_meaning_preserved: bool
    candidates_retained: bool
    non_selection_outcomes_retained: bool
    alternatives_and_unresolved_retained: bool
    governed_outward_meaning_integrated: bool
    expression_link_integrated: bool
    candidate_remains_unvalidated: bool
    msm_schema_modified: bool
    automatic_migration_performed: bool
    governed_result_reference_created: bool
    validation_link_created: bool
    delivery_link_created: bool
    echo_validated_or_approved: bool
    delivery_authorized_or_performed: bool
    truth_evidence_permission_execution: bool
    route_tool_action_memory_filesystem_network: bool
    external_resource_or_model_authority: bool
    bootstrap_integration_enabled: bool
    gp014_superseded: bool
    schema_version: str = SLICE42G_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class MsmOutwardExpressionIntegrationResult:
    result_id: str
    result_digest: str
    integration_input_ref: str
    source_manifest: MeaningStructureManifestV1
    successor_manifest: MeaningStructureManifestV1
    external_authority_reference_record: ExternalAuthorityReferenceRecord
    governed_outward_meaning_record: GovernedOutwardMeaningRecord
    expression_link_record: ExpressionLinkRecord
    selected_to_outward_trace: SemanticTransitionTraceRecord
    outward_to_expression_trace: SemanticTransitionTraceRecord
    companion: MsmOutwardExpressionCustodyCompanionV1
    receipt: MsmOutwardExpressionIntegrationReceiptV1
    deterministic: bool
    additive_only: bool
    immutable_successor_created: bool
    exact_slice41e_chain_preserved: bool
    exact_slice42f_candidate_preserved: bool
    dormant_msm_records_used: bool
    selected_meaning_preserved: bool
    all_candidate_meanings_retained: bool
    all_non_selection_outcomes_retained: bool
    alternatives_and_unresolved_retained: bool
    governed_outward_meaning_integrated: bool
    expression_link_integrated: bool
    complete_successor_manifest_validated: bool
    candidate_remains_unvalidated: bool
    msm_schema_modified: bool
    automatic_migration_performed: bool
    source_manifest_mutated: bool
    candidate_deleted: bool
    non_selection_outcome_deleted: bool
    selected_meaning_rewritten: bool
    governed_result_reference_created: bool
    validation_link_created: bool
    delivery_link_created: bool
    expression_candidate_rewritten: bool
    claim_strengthened: bool
    certainty_upgraded: bool
    evidence_status_upgraded: bool
    caveat_omitted: bool
    refusal_softened: bool
    ambiguity_erased: bool
    unsupported_state_erased: bool
    echo_validation_performed: bool
    echo_approved: bool
    delivery_authorized: bool
    delivered: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    route_or_api_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed_or_written: bool
    filesystem_or_network_accessed: bool
    external_resource_loaded: bool
    model_or_similarity_authority_used: bool
    bootstrap_integration_enabled: bool
    gp014_superseded: bool
    digest_algorithm: str = DIGEST_ALGORITHM
    schema_version: str = SLICE42G_SCHEMA_VERSION


APPROVED_STRICT_PROFILE = MsmOutwardExpressionIntegrationAuthorityProfile(
    profile_id="pending",
    profile_key=SLICE42G_PROFILE_KEY,
    profile_version=SLICE42G_PROFILE_VERSION,
    governing_authority_refs=SLICE42G_GOVERNING_AUTHORITY_REFS,
    exact_slice41e_input_required=True,
    exact_slice41e_result_required=True,
    exact_slice42f_input_required=True,
    exact_slice42f_result_required=True,
    exact_unvalidated_candidate_required=True,
    existing_dormant_msm_records_required=True,
    explicit_external_authority_reference_required=True,
    immutable_successor_required=True,
    selected_meaning_retention_required=True,
    candidate_retention_required=True,
    non_selection_retention_required=True,
    alternative_unresolved_retention_required=True,
    outward_meaning_record_allowed=True,
    expression_link_record_allowed=True,
    lifecycle_traces_required=True,
    complete_successor_validation_required=True,
    versioned_companion_required=True,
    deterministic_receipt_required=True,
    fail_closed=True,
    msm_schema_rewrite_allowed=False,
    automatic_migration_allowed=False,
    source_manifest_mutation_allowed=False,
    candidate_deletion_allowed=False,
    non_selection_deletion_allowed=False,
    selected_meaning_rewrite_allowed=False,
    governed_result_creation_allowed=False,
    validation_link_creation_allowed=False,
    delivery_link_creation_allowed=False,
    expression_candidate_rewrite_allowed=False,
    echo_validation_allowed=False,
    delivery_allowed=False,
    truth_evidence_permission_execution_allowed=False,
    route_tool_action_memory_filesystem_network_allowed=False,
    external_resource_or_model_authority_allowed=False,
    bootstrap_integration_allowed=False,
    gp014_supersession_allowed=False,
)


__all__ = tuple(name for name in globals() if not name.startswith("_"))
