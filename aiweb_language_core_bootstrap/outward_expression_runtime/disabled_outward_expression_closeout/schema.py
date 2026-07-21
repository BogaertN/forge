"""Immutable Slice 42H disabled outward-expression closeout records."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..msm_outward_expression_integration.schema import (
    MsmOutwardExpressionIntegrationInput,
    MsmOutwardExpressionIntegrationResult,
)
from .authority import (
    SLICE42H_ACCEPTANCE_RECORD_VERSION,
    SLICE42H_RECEIPT_VERSION,
    SLICE42H_ROLLBACK_METADATA_VERSION,
    SLICE42H_SCHEMA_VERSION,
)


class Slice42CloseoutStatus(str, Enum):
    REFUSED_DISABLED = "REFUSED_DISABLED"
    HELD_INVALID_STATE = "HELD_INVALID_STATE"
    HELD_INVALID_INVOCATION = "HELD_INVALID_INVOCATION"
    HELD_FIXTURE_NOT_ACCEPTED = "HELD_FIXTURE_NOT_ACCEPTED"
    HELD_INVALID_PREDECESSOR_OUTPUT = "HELD_INVALID_PREDECESSOR_OUTPUT"
    HELD_EXPECTATION_MISMATCH = "HELD_EXPECTATION_MISMATCH"
    COMPLETED = "COMPLETED"


class Slice42CloseoutStage(str, Enum):
    ISOLATED_BOOTSTRAP_BOUNDARY = "isolated_bootstrap_boundary"
    ACCEPTED_SLICE42A_SCHEMA_AUTHORITY = "accepted_slice42a_schema_authority"
    ACCEPTED_SLICE42B_VALIDATION_LIFECYCLE = "accepted_slice42b_validation_lifecycle"
    ACCEPTED_SLICE42C_EXPRESSION_ELIGIBILITY = "accepted_slice42c_expression_eligibility"
    ACCEPTED_SLICE42D_PRESERVATION_OBLIGATIONS = "accepted_slice42d_preservation_obligations"
    ACCEPTED_SLICE42E_EXPRESSION_PLAN = "accepted_slice42e_expression_plan"
    ACCEPTED_SLICE42F_SURFACE_REALIZATION = "accepted_slice42f_surface_realization"
    ACCEPTED_SLICE42G_MSM_CUSTODY = "accepted_slice42g_msm_custody"
    SLICE42_CLOSEOUT = "slice42_closeout"


class Slice42FixtureScenario(str, Enum):
    BLOCKED_EXPRESSION_WITH_UNRESOLVED_ALTERNATIVE = (
        "blocked_expression_with_unresolved_alternative"
    )


@dataclass(frozen=True, slots=True)
class DisabledOutwardExpressionCloseoutState:
    state_id: str
    enabled: bool
    explicit_offline_developer_enable: bool
    disabled_by_default: bool
    explicit_invocation_required: bool
    accepted_static_fixture_only: bool
    offline_only: bool
    read_only: bool
    in_memory_only: bool
    deterministic: bool
    exact_profile_bounded: bool
    source_preserving: bool
    rollback_safe: bool
    automatic_activation_allowed: bool
    arbitrary_input_allowed: bool
    route_allowed: bool
    api_allowed: bool
    network_allowed: bool
    filesystem_read_allowed: bool
    filesystem_write_allowed: bool
    memory_read_allowed: bool
    memory_write_allowed: bool
    tool_allowed: bool
    action_allowed: bool
    rendering_allowed: bool
    delivery_allowed: bool
    echo_validation_allowed: bool
    truth_authority_allowed: bool
    evidence_authority_allowed: bool
    permission_authority_allowed: bool
    execution_authority_allowed: bool
    slice43_allowed: bool
    schema_version: str = SLICE42H_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class OutwardExpressionCloseoutFixture:
    fixture_id: str
    fixture_name: str
    scenario: Slice42FixtureScenario
    expected_slice42a_source_custody_id: str
    expected_slice42a_authority_requirement_id: str
    expected_slice42b_governance_bundle_id: str
    expected_slice42c_evaluation_input_id: str
    expected_slice42c_result_id: str
    expected_slice42d_projection_input_id: str
    expected_slice42d_result_id: str
    expected_obligation_package_id: str
    expected_slice42e_plan_input_id: str
    expected_slice42e_result_id: str
    expected_expression_plan_id: str
    expected_slice42f_realization_input_id: str
    expected_slice42f_result_id: str
    expected_expression_candidate_id: str
    expected_slice42g_integration_input_id: str
    expected_slice42g_result_id: str
    expected_slice42g_result_digest: str
    expected_source_manifest_id: str
    expected_source_manifest_sha256: str
    expected_successor_manifest_id: str
    expected_successor_manifest_sha256: str
    expected_selected_meaning_ref: str
    expected_outward_meaning_ref: str
    expected_expression_link_ref: str
    expected_external_authority_ref: str
    expected_companion_id: str
    expected_receipt_id: str
    expected_candidate_refs: tuple[str, ...]
    expected_non_selection_refs: tuple[str, ...]
    expected_alternative_refs: tuple[str, ...]
    expected_unresolved_refs: tuple[str, ...]
    expected_candidate_count: int
    expected_non_selection_count: int
    expected_selected_count: int
    expected_outward_meaning_count: int
    expected_expression_link_count: int
    expected_validation_link_count: int
    expected_delivery_link_count: int
    accepted_fixture: bool
    synthetic: bool
    explicit_invocation_only: bool
    offline_only: bool
    in_memory_only: bool
    deterministic: bool
    schema_version: str = SLICE42H_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class OutwardExpressionCloseoutInvocation:
    invocation_id: str
    fixture_id: str
    fixture_name: str
    requested_operation: str
    explicit_offline_developer_enable: bool
    arbitrary_input_carried: bool
    schema_version: str = SLICE42H_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class Slice42CloseoutStageReceipt:
    receipt_id: str
    receipt_version: str
    stage: Slice42CloseoutStage
    stage_index: int
    input_refs: tuple[str, ...]
    output_refs: tuple[str, ...]
    stage_digest: str
    deterministic: bool
    source_preserved: bool
    offline_only: bool
    in_memory_only: bool
    route_created: bool
    api_created: bool
    network_accessed: bool
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    tool_invoked: bool
    action_performed: bool
    rendered: bool
    echo_validated: bool
    delivered: bool
    schema_version: str = SLICE42H_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class Slice42RollbackMetadata:
    metadata_id: str
    metadata_version: str
    pre_slice42_commit: str
    pre_slice42_tree: str
    pre_slice42_subject: str
    accepted_slice42g_head: str
    accepted_slice42g_tree: str
    accepted_slice42g_subject: str
    recovery_requires_explicit_operator_action: bool
    complete_history_required: bool
    exact_tree_recovery_required: bool
    runtime_rollback_performed: bool
    repository_mutated: bool
    schema_version: str = SLICE42H_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class Slice42AcceptanceRecord:
    record_id: str
    record_version: str
    accepted_increment_labels: tuple[str, ...]
    accepted_chain: tuple[str, ...]
    accepted_scope: tuple[str, ...]
    deferred_scope: tuple[str, ...]
    permanent_boundaries: tuple[str, ...]
    prohibited_authority: tuple[str, ...]
    rollback_metadata_ref: str
    slice42_closed: bool
    slice43_started: bool
    stop_after_slice42: bool
    authorized_meaning_required: bool
    selected_meaning_preserved: bool
    scope_preserved: bool
    certainty_preserved: bool
    evidence_status_preserved: bool
    caveats_preserved: bool
    refusal_state_preserved: bool
    unresolved_conditions_preserved: bool
    deterministic_expression_candidate_created: bool
    expression_candidate_remains_unvalidated: bool
    echo_validation_performed: bool
    delivery_authority: bool
    truth_authority: bool
    evidence_authority: bool
    permission_authority: bool
    execution_authority: bool
    runtime_self_grants_acceptance: bool
    production_ready: bool
    schema_version: str = SLICE42H_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class DisabledOutwardExpressionCloseoutResult:
    result_id: str
    result_digest: str
    status: Slice42CloseoutStatus
    reason_code: str
    state_id: str
    invocation_id: str
    fixture_id: str
    integration_input: MsmOutwardExpressionIntegrationInput | None
    integration_result: MsmOutwardExpressionIntegrationResult | None
    stage_receipts: tuple[Slice42CloseoutStageReceipt, ...]
    acceptance_record: Slice42AcceptanceRecord
    rollback_metadata: Slice42RollbackMetadata
    deterministic_repeat_digest: str
    disabled_by_default: bool
    explicitly_invoked: bool
    accepted_static_fixture_only: bool
    offline_only: bool
    read_only: bool
    in_memory_only: bool
    deterministic: bool
    exact_stage_chain_complete: bool
    stage_receipt_count: int
    authorized_meaning_required: bool
    selected_meaning_preserved: bool
    scope_preserved: bool
    certainty_preserved: bool
    evidence_status_preserved: bool
    caveats_preserved: bool
    refusal_state_preserved: bool
    unresolved_conditions_preserved: bool
    deterministic_expression_candidate_created: bool
    governed_outward_meaning_custody_preserved: bool
    expression_link_custody_preserved: bool
    complete_successor_manifest_validated: bool
    expression_candidate_remains_unvalidated: bool
    final_slice42_acceptance_record_created: bool
    slice43_started: bool
    msm_v1_schema_modified: bool
    automatic_migration_performed: bool
    selected_meaning_rewritten: bool
    candidate_alternative_deleted: bool
    unresolved_state_resolved: bool
    certainty_upgraded: bool
    evidence_status_upgraded: bool
    caveat_omitted: bool
    refusal_softened: bool
    expression_candidate_rewritten: bool
    validation_link_created: bool
    delivery_link_created: bool
    echo_validation_performed: bool
    echo_approved: bool
    delivery_authorized: bool
    delivered: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    route_created: bool
    api_created: bool
    network_accessed: bool
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    tool_invoked: bool
    action_performed: bool
    rendered: bool
    external_resource_loaded: bool
    language_model_used: bool
    embedding_used: bool
    vector_used: bool
    rag_used: bool
    semantic_similarity_used: bool
    neural_parser_used: bool
    hidden_classifier_used: bool
    gp014_superseded: bool
    schema_version: str = SLICE42H_SCHEMA_VERSION


__all__ = tuple(name for name in globals() if not name.startswith("_"))
