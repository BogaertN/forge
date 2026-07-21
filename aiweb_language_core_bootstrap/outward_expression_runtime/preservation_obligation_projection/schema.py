"""Immutable Slice 42D preservation-obligation projection records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..expression_eligibility.schema import (
    ExpressionEligibilityEvaluationInput,
    ExpressionEligibilityOutcome,
    ExpressionEligibilityResult,
)
from .authority import (
    DIGEST_ALGORITHM,
    SLICE42D_PERMANENT_BOUNDARIES,
    SLICE42D_PROFILE_KEY,
    SLICE42D_PROFILE_VERSION,
    SLICE42D_PROHIBITED_AUTHORITY,
    SLICE42D_SCHEMA_VERSION,
)


class PreservationObligationProjectionFindingKind(str, Enum):
    EXACT_SLICE42C_STATE_CONFIRMED = "exact_slice42c_state_confirmed"
    EXPLICIT_PROJECTION_AUTHORITY_CONFIRMED = (
        "explicit_projection_authority_confirmed"
    )
    SELECTED_MEANING_PRESERVED = "selected_meaning_preserved"
    ACTIVE_SCOPE_PRESERVED = "active_scope_preserved"
    CERTAINTY_AND_EVIDENCE_STATUS_PRESERVED = (
        "certainty_and_evidence_status_preserved"
    )
    LIMITATIONS_AND_CAVEATS_PRESERVED = (
        "limitations_and_caveats_preserved"
    )
    REFUSAL_BOUNDARIES_PRESERVED = "refusal_boundaries_preserved"
    UNRESOLVED_AMBIGUITY_PRESERVED = "unresolved_ambiguity_preserved"
    UNSUPPORTED_STATE_PRESERVED = "unsupported_state_preserved"
    MEMORY_AUTHORITY_STATUS_PRESERVED = (
        "memory_authority_status_preserved"
    )
    EXTERNAL_RESOURCE_STATUS_PRESERVED = (
        "external_resource_status_preserved"
    )
    DELIVERY_AUTHORITY_STATUS_PRESERVED = (
        "delivery_authority_status_preserved"
    )


class PreservationObligationProjectionValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    RECORD_INVALID = "record_invalid"
    IDENTITY_MISMATCH = "identity_mismatch"
    DIGEST_MISMATCH = "digest_mismatch"
    SLICE42C_STATE_MISMATCH = "slice42c_state_mismatch"
    PROJECTION_AUTHORITY_MISMATCH = "projection_authority_mismatch"
    PROJECTION_AUTHORITY_MISSING = "projection_authority_missing"
    PROJECTION_SCOPE_MISMATCH = "projection_scope_mismatch"
    PREDECESSOR_RECEIPT_MISMATCH = "predecessor_receipt_mismatch"
    OBLIGATION_CATEGORY_MISMATCH = "obligation_category_mismatch"
    SELECTED_MEANING_MISMATCH = "selected_meaning_mismatch"
    ACTIVE_SCOPE_MISMATCH = "active_scope_mismatch"
    CERTAINTY_MISMATCH = "certainty_mismatch"
    EVIDENCE_STATUS_MISMATCH = "evidence_status_mismatch"
    LIMITATION_MISMATCH = "limitation_mismatch"
    CAVEAT_MISMATCH = "caveat_mismatch"
    REFUSAL_BOUNDARY_MISMATCH = "refusal_boundary_mismatch"
    UNRESOLVED_CONDITION_MISMATCH = "unresolved_condition_mismatch"
    AMBIGUITY_MISMATCH = "ambiguity_mismatch"
    UNSUPPORTED_STATE_MISMATCH = "unsupported_state_mismatch"
    MEMORY_AUTHORITY_MISMATCH = "memory_authority_mismatch"
    EXTERNAL_RESOURCE_STATUS_MISMATCH = (
        "external_resource_status_mismatch"
    )
    DELIVERY_AUTHORITY_MISMATCH = "delivery_authority_mismatch"
    FINDING_MISMATCH = "finding_mismatch"
    DUPLICATE_IDENTIFIER = "duplicate_identifier"
    PROHIBITED_REQUEST = "prohibited_request"
    DOWNSTREAM_AUTHORITY = "downstream_authority"
    CANONICAL_MISMATCH = "canonical_mismatch"


@dataclass(frozen=True, slots=True)
class PreservationObligationProjectionValidationIssue:
    path: str
    code: PreservationObligationProjectionValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class PreservationObligationProjectionValidationReport:
    issues: tuple[PreservationObligationProjectionValidationIssue, ...]
    schema_version: str = SLICE42D_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class PreservationObligationProjectionValidationError(ValueError):
    def __init__(
        self,
        report: PreservationObligationProjectionValidationReport,
    ) -> None:
        self.report = report
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(
            detail or "Slice 42D preservation-obligation validation failed"
        )


@dataclass(frozen=True, slots=True)
class PreservationObligationProjectionAuthorityRecord:
    projection_authority_record_id: str
    authority_key: str
    authority_version: str
    expression_eligibility_evaluation_input_ref: str
    expression_eligibility_result_ref: str
    selected_meaning_source_custody_ref: str
    outward_expression_authority_requirement_ref: str
    outward_expression_authority_record_ref: str
    source_eligibility_outcome: ExpressionEligibilityOutcome
    projection_scope_refs: tuple[str, ...]
    predecessor_receipt_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    disposition_authority_ref: str
    projection_authority_receipt_ref: str
    authority_active: bool
    preservation_obligation_projection_authorized: bool
    governed_outward_meaning_construction_authorized: bool
    expression_plan_construction_authorized: bool
    surface_realization_authorized: bool
    msm_v1_mutation_or_integration_authorized: bool
    echo_validation_authorized: bool
    delivery_authorized: bool
    truth_evidence_permission_execution_authorized: bool
    route_api_network_filesystem_memory_tool_action_authorized: bool
    external_resource_or_model_authority: bool
    gp014_supersession_authorized: bool
    profile_key: str = SLICE42D_PROFILE_KEY
    profile_version: str = SLICE42D_PROFILE_VERSION
    schema_version: str = SLICE42D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class PreservationObligationProjectionInput:
    projection_input_id: str
    expression_eligibility_evaluation_input: (
        ExpressionEligibilityEvaluationInput
    )
    expression_eligibility_result: ExpressionEligibilityResult
    projection_authority_record: (
        PreservationObligationProjectionAuthorityRecord
    )
    projection_reason_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    scope_expansion_requested: bool
    certainty_upgrade_requested: bool
    evidence_status_upgrade_requested: bool
    limitation_omission_requested: bool
    caveat_omission_requested: bool
    refusal_softening_requested: bool
    unresolved_resolution_requested: bool
    ambiguity_erasure_requested: bool
    unsupported_state_erasure_requested: bool
    memory_authority_upgrade_requested: bool
    external_resource_status_upgrade_requested: bool
    delivery_authority_upgrade_requested: bool
    selected_meaning_rewrite_requested: bool
    downstream_authority_requested: bool
    schema_version: str = SLICE42D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ExpressionObligationPackage:
    obligation_package_id: str
    obligation_package_digest: str
    projection_input_ref: str
    expression_eligibility_result_ref: str
    projection_authority_record_ref: str
    selected_meaning_source_custody_ref: str
    outward_expression_authority_requirement_ref: str
    outward_expression_authority_record_ref: str
    source_eligibility_outcome: ExpressionEligibilityOutcome
    selected_meaning_refs: tuple[str, ...]
    active_scope_refs: tuple[str, ...]
    certainty_level_refs: tuple[str, ...]
    evidence_status_refs: tuple[str, ...]
    inherited_limitation_refs: tuple[str, ...]
    required_caveat_refs: tuple[str, ...]
    refusal_relevant_boundary_refs: tuple[str, ...]
    unresolved_condition_refs: tuple[str, ...]
    ambiguity_refs: tuple[str, ...]
    unsupported_state_refs: tuple[str, ...]
    memory_authority_refs: tuple[str, ...]
    external_resource_status_refs: tuple[str, ...]
    delivery_authority_refs: tuple[str, ...]
    privacy_identity_boundary_refs: tuple[str, ...]
    preservation_class_refs: tuple[str, ...]
    predecessor_receipt_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    exact_slice42c_state_verified: bool
    exact_projection_authority_verified: bool
    obligation_categories_separately_projected: bool
    selected_meaning_preserved: bool
    active_scope_preserved: bool
    certainty_preserved: bool
    evidence_status_preserved: bool
    inherited_limitations_preserved: bool
    required_caveats_preserved: bool
    refusal_boundaries_preserved: bool
    unresolved_conditions_preserved: bool
    ambiguity_preserved: bool
    unsupported_states_preserved: bool
    memory_authority_preserved: bool
    external_resource_status_preserved: bool
    delivery_authority_preserved: bool
    planning_progression_eligible: bool
    projection_performed: bool
    obligation_package_created: bool
    scope_upgraded: bool
    certainty_upgraded: bool
    evidence_status_upgraded: bool
    limitation_omitted: bool
    caveat_omitted: bool
    refusal_softened: bool
    unresolved_condition_resolved: bool
    ambiguity_erased: bool
    unsupported_state_erased_or_guessed: bool
    memory_authority_upgraded: bool
    external_resource_status_upgraded: bool
    delivery_authority_upgraded: bool
    selected_meaning_rewritten: bool
    human_readable_text_produced: bool
    governed_outward_meaning_created: bool
    expression_plan_created: bool
    expression_candidate_created: bool
    msm_v1_modified_or_integrated: bool
    echo_validation_performed: bool
    bootstrap_integration_enabled: bool
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
    gp014_superseded: bool
    digest_algorithm: str = DIGEST_ALGORITHM
    schema_version: str = SLICE42D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class PreservationObligationProjectionFinding:
    finding_id: str
    projection_input_ref: str
    obligation_package_ref: str
    finding_kind: PreservationObligationProjectionFindingKind
    basis_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    schema_version: str = SLICE42D_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class PreservationObligationProjectionResult:
    result_id: str
    result_digest: str
    projection_input_ref: str
    obligation_package: ExpressionObligationPackage
    findings: tuple[PreservationObligationProjectionFinding, ...]
    required_law_refs: tuple[str, ...]
    permanent_boundaries: tuple[str, ...]
    prohibited_authority: tuple[str, ...]
    source_eligibility_outcome: ExpressionEligibilityOutcome
    eligible_for_expression_planning: bool
    held_pending_authority: bool
    blocked: bool
    refusal_preserving: bool
    unresolved_preserving: bool
    indeterminate: bool
    preservation_obligations_projected: bool
    obligation_package_created: bool
    governed_outward_meaning_created: bool
    expression_plan_created: bool
    expression_candidate_created: bool
    human_readable_text_produced: bool
    msm_v1_modified_or_integrated: bool
    echo_validation_performed: bool
    bootstrap_integration_enabled: bool
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
    gp014_superseded: bool
    digest_algorithm: str = DIGEST_ALGORITHM
    schema_version: str = SLICE42D_SCHEMA_VERSION


# Retain the accepted Slice 42A boundary vocabularies in the live result.
DEFAULT_PERMANENT_BOUNDARIES = SLICE42D_PERMANENT_BOUNDARIES
DEFAULT_PROHIBITED_AUTHORITY = SLICE42D_PROHIBITED_AUTHORITY


__all__ = (
    "ExpressionObligationPackage",
    "PreservationObligationProjectionAuthorityRecord",
    "PreservationObligationProjectionFinding",
    "PreservationObligationProjectionFindingKind",
    "PreservationObligationProjectionInput",
    "PreservationObligationProjectionResult",
    "PreservationObligationProjectionValidationCode",
    "PreservationObligationProjectionValidationError",
    "PreservationObligationProjectionValidationIssue",
    "PreservationObligationProjectionValidationReport",
)
