"""Immutable Slice 42E controlled expression-plan records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..expression_eligibility.schema import ExpressionEligibilityOutcome
from ..preservation_obligation_projection.schema import (
    PreservationObligationProjectionInput,
    PreservationObligationProjectionResult,
)
from .authority import (
    DIGEST_ALGORITHM,
    SLICE42E_PROFILE_KEY,
    SLICE42E_PROFILE_VERSION,
    SLICE42E_SCHEMA_VERSION,
)


class ExpressionPlanDisposition(str, Enum):
    AUTHORIZED_MEANING_PLAN = "authorized_meaning_plan"
    BLOCKED_CONSEQUENCE_PLAN = "blocked_consequence_plan"
    REFUSAL_PRESERVING_PLAN = "refusal_preserving_plan"
    UNRESOLVED_PRESERVING_PLAN = "unresolved_preserving_plan"
    HELD_PENDING_AUTHORITY = "held_pending_authority"
    INDETERMINATE = "indeterminate"


class ExpressionPlanSectionKind(str, Enum):
    GOVERNING_DISPOSITION = "governing_disposition"
    SELECTED_MEANING = "selected_meaning"
    ACTIVE_SCOPE = "active_scope"
    CERTAINTY = "certainty"
    EVIDENCE_STATUS = "evidence_status"
    MEANING_MODIFIERS = "meaning_modifiers"
    INHERITED_LIMITATIONS = "inherited_limitations"
    REQUIRED_QUALIFICATIONS = "required_qualifications"
    REQUIRED_CAVEATS = "required_caveats"
    REFUSAL_BOUNDARIES = "refusal_boundaries"
    UNRESOLVED_CONDITIONS = "unresolved_conditions"
    AMBIGUITY = "ambiguity"
    UNSUPPORTED_STATES = "unsupported_states"
    MEMORY_AUTHORITY = "memory_authority"
    EXTERNAL_RESOURCE_STATUS = "external_resource_status"
    DELIVERY_AUTHORITY = "delivery_authority"
    PRIVACY_IDENTITY_BOUNDARIES = "privacy_identity_boundaries"


class ExpressionPlanConstructionFindingKind(str, Enum):
    EXACT_SLICE42D_STATE_CONFIRMED = "exact_slice42d_state_confirmed"
    EXPLICIT_PLAN_AUTHORITY_CONFIRMED = "explicit_plan_authority_confirmed"
    OBLIGATIONS_PRESERVED = "obligations_preserved"
    STRUCTURAL_ORDER_DETERMINED = "structural_order_determined"
    MODIFIERS_QUALIFICATIONS_CAVEATS_REFUSAL_PRESERVED = (
        "modifiers_qualifications_caveats_refusal_preserved"
    )
    HIGHER_ORDER_RESTRICTIONS_DOMINANT = (
        "higher_order_restrictions_dominant"
    )
    SELECTED_MEANING_ANCESTRY_PRESERVED = (
        "selected_meaning_ancestry_preserved"
    )
    NON_REALIZATION_BOUNDARY_CONFIRMED = (
        "non_realization_boundary_confirmed"
    )


class ExpressionPlanConstructionValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    RECORD_INVALID = "record_invalid"
    IDENTITY_MISMATCH = "identity_mismatch"
    DIGEST_MISMATCH = "digest_mismatch"
    SLICE42D_STATE_MISMATCH = "slice42d_state_mismatch"
    PLAN_AUTHORITY_MISSING = "plan_authority_missing"
    PLAN_AUTHORITY_MISMATCH = "plan_authority_mismatch"
    PLAN_DISPOSITION_MISMATCH = "plan_disposition_mismatch"
    STRUCTURAL_ORDER_MISMATCH = "structural_order_mismatch"
    SECTION_MISMATCH = "section_mismatch"
    OBLIGATION_MISMATCH = "obligation_mismatch"
    MODIFIER_MISMATCH = "modifier_mismatch"
    QUALIFICATION_MISMATCH = "qualification_mismatch"
    ANCESTRY_MISMATCH = "ancestry_mismatch"
    FINDING_MISMATCH = "finding_mismatch"
    DUPLICATE_IDENTIFIER = "duplicate_identifier"
    PROHIBITED_REQUEST = "prohibited_request"
    DOWNSTREAM_AUTHORITY = "downstream_authority"
    CANONICAL_MISMATCH = "canonical_mismatch"


@dataclass(frozen=True, slots=True)
class ExpressionPlanConstructionValidationIssue:
    path: str
    code: ExpressionPlanConstructionValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class ExpressionPlanConstructionValidationReport:
    issues: tuple[ExpressionPlanConstructionValidationIssue, ...]
    schema_version: str = SLICE42E_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class ExpressionPlanConstructionValidationError(ValueError):
    def __init__(
        self,
        report: ExpressionPlanConstructionValidationReport,
    ) -> None:
        self.report = report
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(detail or "Slice 42E plan validation failed")


@dataclass(frozen=True, slots=True)
class ExpressionPlanConstructionAuthorityRecord:
    planning_authority_record_id: str
    authority_key: str
    authority_version: str
    projection_input_ref: str
    projection_result_ref: str
    obligation_package_ref: str
    selected_meaning_source_custody_ref: str
    outward_expression_authority_record_ref: str
    source_eligibility_outcome: ExpressionEligibilityOutcome
    permitted_disposition: ExpressionPlanDisposition
    permitted_structural_order: tuple[ExpressionPlanSectionKind, ...]
    predecessor_receipt_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    disposition_authority_ref: str
    planning_authority_receipt_ref: str
    authority_active: bool
    expression_plan_construction_authorized: bool
    affirmative_meaning_plan_authorized: bool
    containment_plan_authorized: bool
    governed_outward_meaning_construction_authorized: bool
    surface_realization_authorized: bool
    expression_candidate_creation_authorized: bool
    msm_v1_mutation_or_integration_authorized: bool
    echo_validation_authorized: bool
    delivery_authorized: bool
    truth_evidence_permission_execution_authorized: bool
    route_api_network_filesystem_memory_tool_action_authorized: bool
    external_resource_or_model_authority: bool
    gp014_supersession_authorized: bool
    profile_key: str = SLICE42E_PROFILE_KEY
    profile_version: str = SLICE42E_PROFILE_VERSION
    schema_version: str = SLICE42E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ExpressionPlanConstructionInput:
    plan_input_id: str
    projection_input: PreservationObligationProjectionInput
    projection_result: PreservationObligationProjectionResult
    planning_authority_record: ExpressionPlanConstructionAuthorityRecord
    planning_reason_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    obligation_omission_requested: bool
    structural_reordering_requested: bool
    modifier_omission_requested: bool
    modifier_invention_requested: bool
    qualification_omission_requested: bool
    caveat_omission_requested: bool
    refusal_softening_requested: bool
    unresolved_resolution_requested: bool
    ambiguity_erasure_requested: bool
    unsupported_state_erasure_requested: bool
    lower_order_override_requested: bool
    selected_meaning_rewrite_requested: bool
    human_readable_wording_requested: bool
    downstream_authority_requested: bool
    schema_version: str = SLICE42E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ExpressionPlanSection:
    section_id: str
    plan_input_ref: str
    section_kind: ExpressionPlanSectionKind
    precedence_index: int
    source_refs: tuple[str, ...]
    required_for_plan_custody: bool
    omission_prohibited: bool
    lower_order_override_prohibited: bool
    human_readable_text_present: bool
    schema_version: str = SLICE42E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ControlledExpressionPlan:
    expression_plan_id: str
    expression_plan_digest: str
    plan_input_ref: str
    projection_result_ref: str
    obligation_package_ref: str
    planning_authority_record_ref: str
    selected_meaning_source_custody_ref: str
    outward_expression_authority_record_ref: str
    source_eligibility_outcome: ExpressionEligibilityOutcome
    disposition: ExpressionPlanDisposition
    sections: tuple[ExpressionPlanSection, ...]
    structural_order: tuple[ExpressionPlanSectionKind, ...]
    selected_meaning_refs: tuple[str, ...]
    active_scope_refs: tuple[str, ...]
    certainty_level_refs: tuple[str, ...]
    evidence_status_refs: tuple[str, ...]
    meaning_modifier_refs: tuple[str, ...]
    inherited_limitation_refs: tuple[str, ...]
    required_qualification_refs: tuple[str, ...]
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
    ancestry_refs: tuple[str, ...]
    predecessor_receipt_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    exact_slice42d_state_verified: bool
    exact_plan_authority_verified: bool
    all_slice42d_obligations_preserved: bool
    structural_ordering_determined: bool
    meaning_modifiers_preserved: bool
    required_qualifications_preserved: bool
    required_caveats_preserved: bool
    refusal_boundaries_preserved: bool
    higher_order_restrictions_dominant: bool
    selected_meaning_ancestry_preserved: bool
    source_planning_progression_eligible: bool
    affirmative_claim_plan: bool
    blocked_consequence_plan: bool
    refusal_preserving_plan: bool
    unresolved_preserving_plan: bool
    containment_plan_does_not_upgrade_source_eligibility: bool
    expression_plan_created: bool
    governed_outward_meaning_created: bool
    human_readable_text_produced: bool
    expression_candidate_created: bool
    surface_realization_performed: bool
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
    schema_version: str = SLICE42E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ExpressionPlanConstructionFinding:
    finding_id: str
    plan_input_ref: str
    expression_plan_ref: str | None
    finding_kind: ExpressionPlanConstructionFindingKind
    basis_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    schema_version: str = SLICE42E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ExpressionPlanConstructionResult:
    result_id: str
    result_digest: str
    plan_input_ref: str
    expression_plan: ControlledExpressionPlan | None
    findings: tuple[ExpressionPlanConstructionFinding, ...]
    required_law_refs: tuple[str, ...]
    permanent_boundaries: tuple[str, ...]
    prohibited_authority: tuple[str, ...]
    source_eligibility_outcome: ExpressionEligibilityOutcome
    disposition: ExpressionPlanDisposition
    expression_plan_created: bool
    affirmative_claim_plan: bool
    blocked_consequence_plan: bool
    refusal_preserving_plan: bool
    unresolved_preserving_plan: bool
    held_pending_authority: bool
    indeterminate: bool
    all_slice42d_obligations_preserved: bool
    structural_ordering_determined: bool
    lower_order_choice_overrode_semantics: bool
    governed_outward_meaning_created: bool
    human_readable_text_produced: bool
    expression_candidate_created: bool
    surface_realization_performed: bool
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
    schema_version: str = SLICE42E_SCHEMA_VERSION


__all__ = (
    "ControlledExpressionPlan",
    "ExpressionPlanConstructionAuthorityRecord",
    "ExpressionPlanConstructionFinding",
    "ExpressionPlanConstructionFindingKind",
    "ExpressionPlanConstructionInput",
    "ExpressionPlanConstructionResult",
    "ExpressionPlanConstructionValidationCode",
    "ExpressionPlanConstructionValidationError",
    "ExpressionPlanConstructionValidationIssue",
    "ExpressionPlanConstructionValidationReport",
    "ExpressionPlanDisposition",
    "ExpressionPlanSection",
    "ExpressionPlanSectionKind",
)
