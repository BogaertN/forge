"""Immutable Slice 41F disabled selected-meaning closeout records."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..selected_meaning_runtime.msm_selected_meaning_integration.schema import (
    MsmSelectedMeaningIntegrationInput,
    MsmSelectedMeaningIntegrationResult,
)
from .authority import (
    SLICE41F_ACCEPTANCE_RECORD_VERSION,
    SLICE41F_RECEIPT_VERSION,
    SLICE41F_ROLLBACK_METADATA_VERSION,
    SLICE41F_SCHEMA_VERSION,
)


class Slice41CloseoutStatus(str, Enum):
    REFUSED_DISABLED = "REFUSED_DISABLED"
    HELD_INVALID_STATE = "HELD_INVALID_STATE"
    HELD_INVALID_INVOCATION = "HELD_INVALID_INVOCATION"
    HELD_FIXTURE_NOT_ACCEPTED = "HELD_FIXTURE_NOT_ACCEPTED"
    HELD_INVALID_PREDECESSOR_OUTPUT = "HELD_INVALID_PREDECESSOR_OUTPUT"
    HELD_EXPECTATION_MISMATCH = "HELD_EXPECTATION_MISMATCH"
    COMPLETED = "COMPLETED"


class Slice41CloseoutStage(str, Enum):
    ISOLATED_BOOTSTRAP_BOUNDARY = "isolated_bootstrap_boundary"
    ACCEPTED_SLICE40H_GATE_CUSTODY = "accepted_slice40h_gate_custody"
    ACCEPTED_SLICE41C_SELECTION_ELIGIBILITY = (
        "accepted_slice41c_selection_eligibility"
    )
    ACCEPTED_SLICE41D_SELECTED_MEANING = "accepted_slice41d_selected_meaning"
    ACCEPTED_SLICE41E_MSM_INTEGRATION = "accepted_slice41e_msm_integration"
    SLICE41_CLOSEOUT = "slice41_closeout"


class Slice41FixtureScenario(str, Enum):
    SELECTED_WITH_UNRESOLVED_ALTERNATIVE = (
        "selected_with_unresolved_alternative"
    )


@dataclass(frozen=True, slots=True)
class DisabledSelectedMeaningCloseoutState:
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
    truth_authority_allowed: bool
    evidence_authority_allowed: bool
    permission_authority_allowed: bool
    execution_authority_allowed: bool
    outward_expression_authority_allowed: bool
    slice42_allowed: bool
    schema_version: str = SLICE41F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SelectedMeaningCloseoutFixture:
    fixture_id: str
    fixture_name: str
    scenario: Slice41FixtureScenario
    expected_integration_input_id: str
    expected_source_manifest_id: str
    expected_source_manifest_sha256: str
    expected_successor_manifest_id: str
    expected_successor_manifest_sha256: str
    expected_integration_result_id: str
    expected_integration_result_digest: str
    expected_selected_candidate_ref: str
    expected_selection_receipt_ref: str
    expected_integrated_selected_meaning_ref: str
    expected_candidate_refs: tuple[str, ...]
    expected_non_selection_outcome_refs: tuple[str, ...]
    expected_source_candidate_count: int
    expected_source_non_selection_count: int
    expected_successor_selected_count: int
    expected_unresolved_outcome_count: int
    accepted_fixture: bool
    synthetic: bool
    explicit_invocation_only: bool
    offline_only: bool
    in_memory_only: bool
    deterministic: bool
    schema_version: str = SLICE41F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SelectedMeaningCloseoutInvocation:
    invocation_id: str
    fixture_id: str
    fixture_name: str
    requested_operation: str
    explicit_offline_developer_enable: bool
    arbitrary_input_carried: bool
    schema_version: str = SLICE41F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class Slice41CloseoutStageReceipt:
    receipt_id: str
    stage: Slice41CloseoutStage
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
    delivered: bool
    schema_version: str = SLICE41F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class Slice41RollbackMetadata:
    metadata_id: str
    metadata_version: str
    pre_slice41_commit: str
    pre_slice41_tree: str
    pre_slice41_subject: str
    accepted_slice41e_head: str
    accepted_slice41e_tree: str
    accepted_slice41e_subject: str
    recovery_requires_explicit_operator_action: bool
    complete_history_required: bool
    exact_tree_recovery_required: bool
    runtime_rollback_performed: bool
    repository_mutated: bool
    schema_version: str = SLICE41F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class Slice41AcceptanceRecord:
    record_id: str
    record_version: str
    accepted_increment_labels: tuple[str, ...]
    accepted_chain: tuple[str, ...]
    accepted_scope: tuple[str, ...]
    deferred_scope: tuple[str, ...]
    permanent_boundaries: tuple[str, ...]
    prohibited_authority: tuple[str, ...]
    rollback_metadata_ref: str
    slice41_closed: bool
    slice42_started: bool
    stop_after_slice41: bool
    selected_meaning_bounded_semantic_custody_only: bool
    alternatives_preserved: bool
    unresolved_state_preserved: bool
    truth_authority: bool
    evidence_authority: bool
    permission_authority: bool
    execution_authority: bool
    outward_expression_authority: bool
    runtime_self_grants_acceptance: bool
    production_ready: bool
    schema_version: str = SLICE41F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class DisabledSelectedMeaningCloseoutResult:
    result_id: str
    status: Slice41CloseoutStatus
    reason_code: str
    state_id: str
    invocation_id: str
    fixture_id: str
    integration_input: MsmSelectedMeaningIntegrationInput | None
    integration_result: MsmSelectedMeaningIntegrationResult | None
    stage_receipts: tuple[Slice41CloseoutStageReceipt, ...]
    acceptance_record: Slice41AcceptanceRecord
    rollback_metadata: Slice41RollbackMetadata
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
    selected_meaning_integrated: bool
    selected_meaning_bounded_semantic_custody_only: bool
    candidate_meanings_retained: bool
    non_selection_outcomes_retained: bool
    alternatives_preserved: bool
    unresolved_state_preserved: bool
    slice40h_custody_preserved: bool
    slice41d_construction_preserved: bool
    slice41e_integration_preserved: bool
    final_slice41_acceptance_record_created: bool
    slice42_started: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    outward_expression_authorized: bool
    governed_outward_meaning_created: bool
    expression_link_created: bool
    validation_link_created: bool
    delivery_link_created: bool
    capability_availability_created: bool
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
    delivered: bool
    language_model_used: bool
    embedding_used: bool
    vector_used: bool
    rag_used: bool
    semantic_similarity_used: bool
    schema_version: str = SLICE41F_SCHEMA_VERSION


__all__ = tuple(name for name in globals() if not name.startswith("_"))
