"""Immutable Slice 42A outward-expression runtime custody schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .authority import (
    EXPRESSION_ELIGIBILITY_CUSTODY_STATE_VALUES,
    EXPRESSION_PLAN_CUSTODY_STATE_VALUES,
    OUTWARD_MEANING_CUSTODY_STATE_VALUES,
    PERMANENT_OUTWARD_EXPRESSION_BOUNDARIES,
    PROHIBITED_AUTHORITY_PATHS,
    REALIZED_EXPRESSION_CUSTODY_STATE_VALUES,
)
from .identity import (
    EXPRESSION_ELIGIBILITY_STATUS_SCHEMA_ID,
    EXPRESSION_PLAN_BOUNDARY_SCHEMA_ID,
    EXPRESSION_PRESERVATION_OBLIGATION_CUSTODY_SCHEMA_ID,
    EXPRESSION_RECEIPT_BOUNDARY_SCHEMA_ID,
    EXPRESSION_TRACE_BOUNDARY_SCHEMA_ID,
    GOVERNED_OUTWARD_MEANING_BOUNDARY_SCHEMA_ID,
    OUTWARD_EXPRESSION_AUTHORITY_REQUIREMENT_SCHEMA_ID,
    OUTWARD_EXPRESSION_RUNTIME_SCHEMA_RECORD_SCHEMA_ID,
    REALIZED_EXPRESSION_BOUNDARY_SCHEMA_ID,
    SCHEMA_VERSION,
    SELECTED_MEANING_EXPRESSION_SOURCE_CUSTODY_SCHEMA_ID,
    SPEC_ID,
    SPEC_VERSION,
)


class ExpressionEligibilityCustodyState(str, Enum):
    NOT_EVALUATED = EXPRESSION_ELIGIBILITY_CUSTODY_STATE_VALUES[0]
    READY_FOR_LATER_EVALUATION = EXPRESSION_ELIGIBILITY_CUSTODY_STATE_VALUES[1]
    EVALUATION_DEFERRED = EXPRESSION_ELIGIBILITY_CUSTODY_STATE_VALUES[2]
    EVALUATION_UNAVAILABLE = EXPRESSION_ELIGIBILITY_CUSTODY_STATE_VALUES[3]


class OutwardMeaningCustodyState(str, Enum):
    NOT_CONSTRUCTED = OUTWARD_MEANING_CUSTODY_STATE_VALUES[0]
    READY_FOR_LATER_CONSTRUCTION = OUTWARD_MEANING_CUSTODY_STATE_VALUES[1]
    CONSTRUCTION_DEFERRED = OUTWARD_MEANING_CUSTODY_STATE_VALUES[2]
    CONSTRUCTION_UNAVAILABLE = OUTWARD_MEANING_CUSTODY_STATE_VALUES[3]


class ExpressionPlanCustodyState(str, Enum):
    NOT_CONSTRUCTED = EXPRESSION_PLAN_CUSTODY_STATE_VALUES[0]
    READY_FOR_LATER_PLANNING = EXPRESSION_PLAN_CUSTODY_STATE_VALUES[1]
    PLANNING_DEFERRED = EXPRESSION_PLAN_CUSTODY_STATE_VALUES[2]
    PLANNING_UNAVAILABLE = EXPRESSION_PLAN_CUSTODY_STATE_VALUES[3]


class RealizedExpressionCustodyState(str, Enum):
    NOT_REALIZED = REALIZED_EXPRESSION_CUSTODY_STATE_VALUES[0]
    READY_FOR_LATER_REALIZATION = REALIZED_EXPRESSION_CUSTODY_STATE_VALUES[1]
    REALIZATION_DEFERRED = REALIZED_EXPRESSION_CUSTODY_STATE_VALUES[2]
    REALIZATION_UNAVAILABLE = REALIZED_EXPRESSION_CUSTODY_STATE_VALUES[3]


@dataclass(frozen=True, slots=True)
class SelectedMeaningExpressionSourceCustodyRecord:
    source_custody_id: str
    slice41e_integration_input_ref: str
    slice41e_integration_result_ref: str
    slice41e_integration_receipt_ref: str
    source_manifest_ref: str
    successor_manifest_ref: str
    selected_governed_meaning_ref: str
    selected_candidate_ref: str
    selection_authority_reference_ref: str
    selection_eligibility_result_ref: str
    selection_decision_ref: str
    selection_trace_ref: str
    selection_receipt_ref: str
    content_proof_ref: str
    slice41f_acceptance_record_ref: str
    preserved_alternative_refs: tuple[str, ...]
    unresolved_alternative_refs: tuple[str, ...]
    ambiguity_ancestry_refs: tuple[str, ...]
    clarification_ancestry_refs: tuple[str, ...]
    inherited_limitation_refs: tuple[str, ...]
    blocked_consequence_refs: tuple[str, ...]
    refusal_relevant_refs: tuple[str, ...]
    authority_sensitive_distinction_refs: tuple[str, ...]
    preservation_class_refs: tuple[str, ...]
    exact_selected_meaning_chain_required: bool = field(default=True, init=False)
    selected_meaning_rewrite_allowed: bool = field(default=False, init=False)
    alternative_deletion_allowed: bool = field(default=False, init=False)
    unresolved_resolution_allowed: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=SELECTED_MEANING_EXPRESSION_SOURCE_CUSTODY_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class OutwardExpressionAuthorityRequirementRecord:
    authority_requirement_id: str
    selected_meaning_source_custody_ref: str
    required_outward_expression_authority_ref: str
    required_authority_scope_refs: tuple[str, ...]
    required_expression_purpose_refs: tuple[str, ...]
    required_predecessor_receipt_refs: tuple[str, ...]
    required_version_refs: tuple[str, ...]
    missing_authority_refs: tuple[str, ...]
    requirement_satisfied: bool = field(default=False, init=False)
    expression_authorized: bool = field(default=False, init=False)
    selected_meaning_alone_sufficient: bool = field(default=False, init=False)
    authority_inferred: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=OUTWARD_EXPRESSION_AUTHORITY_REQUIREMENT_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ExpressionPreservationObligationCustodyRecord:
    obligation_custody_id: str
    selected_meaning_source_custody_ref: str
    outward_expression_authority_requirement_ref: str
    active_scope_refs: tuple[str, ...]
    certainty_level_refs: tuple[str, ...]
    evidence_status_refs: tuple[str, ...]
    inherited_limitation_refs: tuple[str, ...]
    required_caveat_refs: tuple[str, ...]
    refusal_relevant_boundary_refs: tuple[str, ...]
    unresolved_condition_refs: tuple[str, ...]
    memory_authority_refs: tuple[str, ...]
    external_resource_status_refs: tuple[str, ...]
    delivery_authority_refs: tuple[str, ...]
    ambiguity_refs: tuple[str, ...]
    privacy_identity_boundary_refs: tuple[str, ...]
    preservation_class_refs: tuple[str, ...]
    projection_performed: bool = field(default=False, init=False)
    obligation_package_created: bool = field(default=False, init=False)
    scope_upgraded: bool = field(default=False, init=False)
    certainty_upgraded: bool = field(default=False, init=False)
    evidence_status_upgraded: bool = field(default=False, init=False)
    caveat_omitted: bool = field(default=False, init=False)
    refusal_softened: bool = field(default=False, init=False)
    unresolved_condition_resolved: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=EXPRESSION_PRESERVATION_OBLIGATION_CUSTODY_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ExpressionEligibilityStatusRecord:
    expression_eligibility_status_id: str
    selected_meaning_source_custody_ref: str
    outward_expression_authority_requirement_ref: str
    preservation_obligation_custody_ref: str
    custody_state: ExpressionEligibilityCustodyState
    status_reason_refs: tuple[str, ...]
    later_evaluator_ref: str | None
    eligibility_evaluated: bool = field(default=False, init=False)
    eligible_for_expression_planning: bool = field(default=False, init=False)
    held_determined: bool = field(default=False, init=False)
    blocked_determined: bool = field(default=False, init=False)
    refusal_preserving_determined: bool = field(default=False, init=False)
    unresolved_preserving_determined: bool = field(default=False, init=False)
    indeterminate_determined: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=EXPRESSION_ELIGIBILITY_STATUS_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class GovernedOutwardMeaningBoundaryRecord:
    governed_outward_meaning_boundary_id: str
    selected_meaning_source_custody_ref: str
    outward_expression_authority_requirement_ref: str
    expression_eligibility_status_ref: str
    preservation_obligation_custody_ref: str
    custody_state: OutwardMeaningCustodyState
    permitted_claim_refs: tuple[str, ...]
    required_qualification_refs: tuple[str, ...]
    prohibited_enlargement_refs: tuple[str, ...]
    external_dependency_refs: tuple[str, ...]
    ancestry_refs: tuple[str, ...]
    later_constructor_ref: str | None
    governed_outward_meaning_created: bool = field(default=False, init=False)
    selected_meaning_rewritten: bool = field(default=False, init=False)
    semantic_enrichment_performed: bool = field(default=False, init=False)
    semantic_deletion_performed: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=GOVERNED_OUTWARD_MEANING_BOUNDARY_SCHEMA_ID,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ExpressionPlanBoundaryRecord:
    expression_plan_boundary_id: str
    governed_outward_meaning_boundary_ref: str
    preservation_obligation_custody_ref: str
    custody_state: ExpressionPlanCustodyState
    ordering_constraint_refs: tuple[str, ...]
    modifier_custody_refs: tuple[str, ...]
    qualification_custody_refs: tuple[str, ...]
    caveat_custody_refs: tuple[str, ...]
    refusal_custody_refs: tuple[str, ...]
    unresolved_custody_refs: tuple[str, ...]
    ancestry_refs: tuple[str, ...]
    later_planner_ref: str | None
    expression_plan_created: bool = field(default=False, init=False)
    final_text_created: bool = field(default=False, init=False)
    lower_order_choice_overrode_semantics: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=EXPRESSION_PLAN_BOUNDARY_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class RealizedExpressionBoundaryRecord:
    realized_expression_boundary_id: str
    expression_plan_boundary_ref: str
    governed_outward_meaning_boundary_ref: str
    preservation_obligation_custody_ref: str
    custody_state: RealizedExpressionCustodyState
    expression_candidate_ref: str | None
    realized_text_sha256: str | None
    admitted_realization_rule_refs: tuple[str, ...]
    controlled_resource_refs: tuple[str, ...]
    realization_trace_ref: str | None
    realization_receipt_ref: str | None
    later_realizer_ref: str | None
    realization_performed: bool = field(default=False, init=False)
    human_readable_text_produced: bool = field(default=False, init=False)
    expression_candidate_created: bool = field(default=False, init=False)
    echo_validation_performed: bool = field(default=False, init=False)
    delivery_authorized: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=REALIZED_EXPRESSION_BOUNDARY_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class ExpressionTraceBoundaryRecord:
    expression_trace_boundary_id: str
    selected_meaning_source_custody_ref: str
    outward_expression_authority_requirement_ref: str
    preservation_obligation_custody_ref: str
    expression_eligibility_status_ref: str
    governed_outward_meaning_boundary_ref: str
    expression_plan_boundary_ref: str
    realized_expression_boundary_ref: str
    predecessor_trace_refs: tuple[str, ...]
    predecessor_receipt_refs: tuple[str, ...]
    authority_version_refs: tuple[tuple[str, str], ...]
    schema_version_refs: tuple[tuple[str, str], ...]
    trace_boundary_only: bool = field(default=True, init=False)
    trace_validated: bool = field(default=False, init=False)
    expression_trace_created: bool = field(default=False, init=False)
    expression_performed: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=EXPRESSION_TRACE_BOUNDARY_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class ExpressionReceiptBoundaryRecord:
    expression_receipt_boundary_id: str
    selected_meaning_source_custody_ref: str
    outward_expression_authority_requirement_ref: str
    expression_eligibility_status_ref: str
    governed_outward_meaning_boundary_ref: str
    expression_plan_boundary_ref: str
    realized_expression_boundary_ref: str
    expression_trace_boundary_ref: str
    required_law_refs: tuple[str, ...]
    prohibited_consequence_refs: tuple[str, ...]
    audit_note: str
    receipt_boundary_only: bool = field(default=True, init=False)
    receipt_validated: bool = field(default=False, init=False)
    expression_receipt_created: bool = field(default=False, init=False)
    expression_authorized: bool = field(default=False, init=False)
    echo_validated: bool = field(default=False, init=False)
    delivered: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=EXPRESSION_RECEIPT_BOUNDARY_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class OutwardExpressionRuntimeSchemaRecord:
    outward_expression_runtime_schema_record_id: str
    selected_meaning_source_custody: SelectedMeaningExpressionSourceCustodyRecord
    outward_expression_authority_requirement: OutwardExpressionAuthorityRequirementRecord
    preservation_obligation_custody: ExpressionPreservationObligationCustodyRecord
    expression_eligibility_status: ExpressionEligibilityStatusRecord
    governed_outward_meaning_boundary: GovernedOutwardMeaningBoundaryRecord
    expression_plan_boundary: ExpressionPlanBoundaryRecord
    realized_expression_boundary: RealizedExpressionBoundaryRecord
    expression_trace_boundary: ExpressionTraceBoundaryRecord
    expression_receipt_boundary: ExpressionReceiptBoundaryRecord
    permanent_boundaries: tuple[str, ...] = field(
        default=PERMANENT_OUTWARD_EXPRESSION_BOUNDARIES,
        init=False,
    )
    prohibited_authority_paths: tuple[str, ...] = field(
        default=PROHIBITED_AUTHORITY_PATHS,
        init=False,
    )
    schema_only: bool = field(default=True, init=False)
    versioned_companion: bool = field(default=True, init=False)
    deterministic_identity_calculated: bool = field(default=False, init=False)
    validation_performed: bool = field(default=False, init=False)
    canonical_serialization_performed: bool = field(default=False, init=False)
    lifecycle_transition_performed: bool = field(default=False, init=False)
    selected_meaning_chain_admitted: bool = field(default=False, init=False)
    outward_expression_authority_admitted: bool = field(default=False, init=False)
    expression_eligibility_evaluated: bool = field(default=False, init=False)
    preservation_obligations_projected: bool = field(default=False, init=False)
    governed_outward_meaning_created: bool = field(default=False, init=False)
    expression_plan_created: bool = field(default=False, init=False)
    expression_candidate_created: bool = field(default=False, init=False)
    human_readable_text_produced: bool = field(default=False, init=False)
    msm_v1_schema_modified: bool = field(default=False, init=False)
    msm_v1_automatic_migration_performed: bool = field(default=False, init=False)
    msm_v1_outward_meaning_integrated: bool = field(default=False, init=False)
    msm_v1_expression_link_integrated: bool = field(default=False, init=False)
    bootstrap_integration_enabled: bool = field(default=False, init=False)
    echo_validation_performed: bool = field(default=False, init=False)
    truth_determined: bool = field(default=False, init=False)
    evidence_validated: bool = field(default=False, init=False)
    permission_granted: bool = field(default=False, init=False)
    execution_authorized: bool = field(default=False, init=False)
    capability_availability_created: bool = field(default=False, init=False)
    route_created: bool = field(default=False, init=False)
    api_created: bool = field(default=False, init=False)
    tool_invoked: bool = field(default=False, init=False)
    action_performed: bool = field(default=False, init=False)
    memory_accessed: bool = field(default=False, init=False)
    memory_written: bool = field(default=False, init=False)
    filesystem_read_performed: bool = field(default=False, init=False)
    filesystem_write_performed: bool = field(default=False, init=False)
    network_access_performed: bool = field(default=False, init=False)
    external_resource_loaded: bool = field(default=False, init=False)
    rendered_for_delivery: bool = field(default=False, init=False)
    delivered: bool = field(default=False, init=False)
    language_model_used: bool = field(default=False, init=False)
    embedding_used: bool = field(default=False, init=False)
    vector_used: bool = field(default=False, init=False)
    rag_used: bool = field(default=False, init=False)
    semantic_similarity_used: bool = field(default=False, init=False)
    neural_parser_used: bool = field(default=False, init=False)
    hidden_classifier_used: bool = field(default=False, init=False)
    gp014_superseded: bool = field(default=False, init=False)
    spec_id: str = field(default=SPEC_ID, init=False)
    spec_version: str = field(default=SPEC_VERSION, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(
        default=OUTWARD_EXPRESSION_RUNTIME_SCHEMA_RECORD_SCHEMA_ID,
        init=False,
    )


__all__ = (
    "ExpressionEligibilityCustodyState",
    "ExpressionEligibilityStatusRecord",
    "ExpressionPlanBoundaryRecord",
    "ExpressionPlanCustodyState",
    "ExpressionPreservationObligationCustodyRecord",
    "ExpressionReceiptBoundaryRecord",
    "ExpressionTraceBoundaryRecord",
    "GovernedOutwardMeaningBoundaryRecord",
    "OutwardExpressionAuthorityRequirementRecord",
    "OutwardExpressionRuntimeSchemaRecord",
    "OutwardMeaningCustodyState",
    "RealizedExpressionBoundaryRecord",
    "RealizedExpressionCustodyState",
    "SelectedMeaningExpressionSourceCustodyRecord",
)
