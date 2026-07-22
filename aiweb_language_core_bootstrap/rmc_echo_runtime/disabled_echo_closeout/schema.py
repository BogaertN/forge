"""Immutable Slice 43H disabled RMC Echo closeout records."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .authority import (
    SLICE43H_ACCEPTANCE_RECORD_VERSION,
    SLICE43H_RECEIPT_VERSION,
    SLICE43H_ROLLBACK_METADATA_VERSION,
    SLICE43H_SCHEMA_VERSION,
)


class Slice43CloseoutStatus(str, Enum):
    REFUSED_DISABLED = "REFUSED_DISABLED"
    HELD_INVALID_STATE = "HELD_INVALID_STATE"
    HELD_INVALID_INVOCATION = "HELD_INVALID_INVOCATION"
    HELD_FIXTURE_NOT_ACCEPTED = "HELD_FIXTURE_NOT_ACCEPTED"
    HELD_INVALID_PREDECESSOR_OUTPUT = "HELD_INVALID_PREDECESSOR_OUTPUT"
    HELD_EXPECTATION_MISMATCH = "HELD_EXPECTATION_MISMATCH"
    COMPLETED = "COMPLETED"


class Slice43CloseoutStage(str, Enum):
    ISOLATED_BOOTSTRAP_BOUNDARY = "isolated_bootstrap_boundary"
    ACCEPTED_SLICE43A_SCHEMA_AUTHORITY = "accepted_slice43a_schema_authority"
    ACCEPTED_SLICE43B_VALIDATION_LIFECYCLE = "accepted_slice43b_validation_lifecycle"
    ACCEPTED_SLICE43C_SOURCE_ADMISSION = "accepted_slice43c_source_admission"
    ACCEPTED_SLICE43D_PRESERVATION_COMPARISON = "accepted_slice43d_preservation_comparison"
    ACCEPTED_SLICE43E_DRIFT_CLASSIFICATION = "accepted_slice43e_drift_classification"
    ACCEPTED_SLICE43F_ECHO_DISPOSITION = "accepted_slice43f_echo_disposition"
    ACCEPTED_SLICE43G_MSM_CUSTODY = "accepted_slice43g_msm_custody"
    SLICE43_CLOSEOUT = "slice43_closeout"


class Slice43FixtureScenario(str, Enum):
    ACCEPTED_PASSED_ECHO_VALIDATION = "accepted_passed_echo_validation"


@dataclass(frozen=True, slots=True)
class DisabledEchoCloseoutState:
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
    echoforge_allowed: bool
    llm_allowed: bool
    truth_authority_allowed: bool
    evidence_authority_allowed: bool
    permission_authority_allowed: bool
    execution_authority_allowed: bool
    slice44_allowed: bool
    schema_version: str = SLICE43H_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class EchoCloseoutFixture:
    fixture_id: str
    fixture_name: str
    scenario: Slice43FixtureScenario
    expected_source_42h_result_id: str
    expected_source_42h_result_digest: str
    expected_source_42h_acceptance_record_id: str
    expected_source_42g_input_id: str
    expected_source_42g_result_id: str
    expected_source_42g_result_digest: str
    expected_43c_request_id: str
    expected_43c_result_id: str
    expected_43c_result_digest: str
    expected_43d_request_id: str
    expected_43d_result_id: str
    expected_43d_result_digest: str
    expected_43e_request_id: str
    expected_43e_result_id: str
    expected_43e_result_digest: str
    expected_43f_request_id: str
    expected_43f_result_id: str
    expected_43f_result_digest: str
    expected_43f_disposition: str
    expected_43g_input_id: str
    expected_43g_result_id: str
    expected_43g_result_digest: str
    expected_43g_source_manifest_id: str
    expected_43g_source_manifest_sha256: str
    expected_43g_successor_manifest_id: str
    expected_43g_successor_manifest_sha256: str
    expected_43g_validation_link_id: str
    expected_43g_companion_id: str
    expected_43g_receipt_id: str
    expected_dimension_finding_count: int
    expected_classification_record_count: int
    accepted_fixture: bool
    synthetic: bool
    explicit_invocation_only: bool
    offline_only: bool
    in_memory_only: bool
    deterministic: bool
    schema_version: str = SLICE43H_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class EchoCloseoutInvocation:
    invocation_id: str
    fixture_id: str
    fixture_name: str
    requested_operation: str
    explicit_offline_developer_enable: bool
    arbitrary_input_carried: bool
    schema_version: str = SLICE43H_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class Slice43CloseoutStageReceipt:
    receipt_id: str
    receipt_version: str
    stage: Slice43CloseoutStage
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
    echoforge_used: bool
    llm_used: bool
    schema_version: str = SLICE43H_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class Slice43RollbackMetadata:
    metadata_id: str
    metadata_version: str
    pre_slice43_commit: str
    pre_slice43_tree: str
    pre_slice43_subject: str
    accepted_slice43g_head: str
    accepted_slice43g_tree: str
    accepted_slice43g_subject: str
    recovery_requires_explicit_operator_action: bool
    complete_history_required: bool
    exact_tree_recovery_required: bool
    runtime_rollback_performed: bool
    repository_mutated: bool
    schema_version: str = SLICE43H_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class Slice43AcceptanceRecord:
    record_id: str
    record_version: str
    accepted_increment_labels: tuple[str, ...]
    accepted_chain: tuple[str, ...]
    accepted_scope: tuple[str, ...]
    deferred_scope: tuple[str, ...]
    permanent_boundaries: tuple[str, ...]
    prohibited_authority: tuple[str, ...]
    rollback_metadata_ref: str
    slice43_closed: bool
    stop_after_slice43: bool
    slice43a_through_43h_completed: bool
    authorized_meaning_required: bool
    proposed_expression_required: bool
    selected_meaning_preserved: bool
    scope_preserved: bool
    certainty_preserved: bool
    evidence_status_preserved: bool
    caveats_preserved: bool
    refusal_state_preserved: bool
    unresolved_conditions_preserved: bool
    material_drift_rejected_or_contained: bool
    echoforge_used: bool
    llm_used: bool
    delivery_authority: bool
    truth_authority: bool
    evidence_authority: bool
    permission_authority: bool
    execution_authority: bool
    slice44_started: bool
    runtime_self_grants_acceptance: bool
    production_ready: bool
    schema_version: str = SLICE43H_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class DisabledEchoCloseoutResult:
    result_id: str
    result_digest: str
    status: Slice43CloseoutStatus
    reason_code: str
    state_id: str
    invocation_id: str | None
    fixture_id: str | None
    source_42h_result: Any | None
    source_admission_request: Any | None
    source_admission_result: Any | None
    comparison_request: Any | None
    comparison_result: Any | None
    classification_request: Any | None
    classification_result: Any | None
    disposition_request: Any | None
    disposition_result: Any | None
    msm_integration_input: Any | None
    msm_integration_result: Any | None
    stage_receipts: tuple[Slice43CloseoutStageReceipt, ...]
    acceptance_record: Slice43AcceptanceRecord
    rollback_metadata: Slice43RollbackMetadata
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
    proposed_expression_required: bool
    selected_meaning_preserved: bool
    scope_preserved: bool
    certainty_preserved: bool
    evidence_status_preserved: bool
    caveats_preserved: bool
    refusal_state_preserved: bool
    unresolved_conditions_preserved: bool
    material_drift_rejected_or_contained: bool
    echoforge_used: bool
    llm_used: bool
    delivery_authority: bool
    truth_authority: bool
    evidence_authority: bool
    permission_authority: bool
    execution_authority: bool
    slice44_started: bool
    route_api_network_filesystem_memory_tool_action_authority: bool
    source_manifest_mutated: bool
    delivery_link_created: bool
    gp014_superseded: bool
    schema_version: str = SLICE43H_SCHEMA_VERSION


__all__ = tuple(name for name in globals() if not name.startswith("_"))
