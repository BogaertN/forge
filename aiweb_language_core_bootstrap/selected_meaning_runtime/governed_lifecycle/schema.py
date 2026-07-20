"""Slice 41B validation, identity, version, and lifecycle custody schema.

This module adds deterministic validation custody around the immutable Slice 41A
selected-meaning runtime schema.  It does not evaluate candidate eligibility,
re-evaluate gates, choose or rank candidates, resolve ambiguity, construct a
selected meaning, modify MSM-v1, enable bootstrap integration, render output,
write memory, route tools, execute actions, or deliver anything.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..schema import SelectedMeaningRuntimeSchemaRecord


SLICE41B_ACCEPTED_PARENT_HEAD = "9c9a9135d07991446a720b845611bf3c153db522"
SLICE41B_ACCEPTED_PARENT_TREE = "781a691f863aba4defc2dab12df192be6c18b075"
SLICE41B_ACCEPTED_PARENT_SUBJECT = (
    "Slice 41A selected meaning runtime core schema and authority contract"
)
SLICE41B_SCHEMA_VERSION = (
    "aiweb-slice41b-selected-meaning-runtime-governance-v1"
)
CANONICAL_FIELD_ORDER_VERSION = (
    "aiweb-slice41b-selected-meaning-canonical-field-order-v1"
)
DIGEST_ALGORITHM = "sha256"
SUPPORTED_RUNTIME_SCHEMA_VERSIONS = (
    "aiweb-selected-meaning-runtime-core-v1",
)
SUPPORTED_RUNTIME_SPEC_VERSIONS = (
    "aiweb-slice41a-selected-meaning-runtime-core-schema-v1",
)


class SelectedMeaningLifecycleStage(str, Enum):
    SCHEMA_DECLARED = "schema_declared"
    VERSION_BOUND = "version_bound"
    PREDECESSORS_BOUND = "predecessors_bound"
    CROSS_RECORD_VALIDATED = "cross_record_validated"
    RECORD_VALIDATED = "record_validated"
    RECORD_SEALED = "record_sealed"
    VALIDATION_INCOMPLETE = "validation_incomplete"
    UNKNOWN_VERSION_BLOCKED = "unknown_version_blocked"
    MALFORMED_RECORD_BLOCKED = "malformed_record_blocked"
    PREDECESSOR_INVALID_BLOCKED = "predecessor_invalid_blocked"
    IDENTITY_COLLISION_BLOCKED = "identity_collision_blocked"


class SelectedMeaningLifecycleTransitionKind(str, Enum):
    DECLARE_SCHEMA = "declare_schema"
    BIND_VERSION = "bind_version"
    BIND_PREDECESSORS = "bind_predecessors"
    VALIDATE_CROSS_RECORDS = "validate_cross_records"
    VALIDATE_RECORD = "validate_record"
    SEAL_RECORD = "seal_record"
    MARK_INCOMPLETE = "mark_incomplete"
    BLOCK_UNKNOWN_VERSION = "block_unknown_version"
    BLOCK_MALFORMED_RECORD = "block_malformed_record"
    BLOCK_INVALID_PREDECESSOR = "block_invalid_predecessor"
    BLOCK_IDENTITY_COLLISION = "block_identity_collision"
    RESUME_VALIDATION = "resume_validation"


class SelectedMeaningValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    REQUIRED_VALUE_MISSING = "required_value_missing"
    INVALID_TEXT = "invalid_text"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    UNKNOWN_VERSION = "unknown_version"
    INVALID_SHA256 = "invalid_sha256"
    INVALID_ENUM = "invalid_enum"
    INVALID_TUPLE = "invalid_tuple"
    DUPLICATE_TUPLE_VALUE = "duplicate_tuple_value"
    DUPLICATE_FIELD = "duplicate_field"
    UNKNOWN_FIELD = "unknown_field"
    MISSING_FIELD = "missing_field"
    FIELD_ORDER_MISMATCH = "field_order_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    IDENTITY_COLLISION = "identity_collision"
    DUPLICATE_RECORD_ID = "duplicate_record_id"
    CROSS_RECORD_IDENTITY_MISMATCH = "cross_record_identity_mismatch"
    SCHEMA_VERSION_MISMATCH = "schema_version_mismatch"
    SPEC_VERSION_MISMATCH = "spec_version_mismatch"
    PREDECESSOR_REFERENCE_MISMATCH = "predecessor_reference_mismatch"
    PREDECESSOR_REFERENCE_MISSING = "predecessor_reference_missing"
    REFERENCE_NOT_FOUND = "reference_not_found"
    CANONICAL_DIGEST_MISMATCH = "canonical_digest_mismatch"
    LIFECYCLE_STAGE_INVALID = "lifecycle_stage_invalid"
    LIFECYCLE_TRANSITION_NOT_PERMITTED = (
        "lifecycle_transition_not_permitted"
    )
    AUTOMATIC_TRANSITION_PROHIBITED = "automatic_transition_prohibited"
    ELIGIBILITY_EVALUATION_PROHIBITED = (
        "eligibility_evaluation_prohibited"
    )
    SELECTION_PROHIBITED = "selection_prohibited"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"
    NONDETERMINISTIC_INPUT_PROHIBITED = (
        "nondeterministic_input_prohibited"
    )


@dataclass(frozen=True, slots=True)
class SelectedMeaningValidationIssue:
    path: str
    code: SelectedMeaningValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class SelectedMeaningValidationReport:
    issues: tuple[SelectedMeaningValidationIssue, ...]
    schema_version: str = SLICE41B_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class SelectedMeaningValidationError(ValueError):
    """Raised when Slice 41B validation fails closed."""

    def __init__(self, report: SelectedMeaningValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(
            summary or "Slice 41B selected-meaning validation failed"
        )


@dataclass(frozen=True, slots=True)
class SelectedMeaningVersionCustody:
    custody_id: str
    runtime_schema_record_id: str
    runtime_schema_version: str
    runtime_schema_id: str
    runtime_spec_id: str
    runtime_spec_version: str
    record_schema_versions: tuple[tuple[str, str], ...]
    predecessor_references: tuple[tuple[str, str], ...]
    accepted_parent_head: str
    accepted_parent_tree: str
    accepted_parent_subject: str
    canonical_field_order_version: str
    digest_algorithm: str
    non_llm_provenance: bool
    timestamps_in_identity: bool
    randomness_in_identity: bool
    process_identity_in_identity: bool
    filesystem_state_in_identity: bool
    environment_state_in_identity: bool
    hash_table_order_in_identity: bool
    eligibility_evaluation_authorized: bool
    candidate_ranking_authorized: bool
    selection_authorized: bool
    selected_meaning_construction_authorized: bool
    msm_v1_mutation_authorized: bool
    bootstrap_integration_authorized: bool
    truth_evidence_permission_execution_authorized: bool
    route_tool_action_memory_rendering_delivery_authorized: bool
    governance_schema_version: str = SLICE41B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SelectedMeaningLifecycleRecord:
    lifecycle_record_id: str
    runtime_schema_record_id: str
    version_custody_ref: str
    stage: SelectedMeaningLifecycleStage
    predecessor_lifecycle_record_ids: tuple[str, ...]
    predecessor_reference_ids: tuple[str, ...]
    validation_issue_digest_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    automatic_progression: bool
    canonical_serialization_performed: bool
    deterministic_identity_validated: bool
    predecessor_references_validated: bool
    cross_record_consistency_validated: bool
    malformed_record_rejected: bool
    unknown_version_rejected: bool
    duplicate_record_rejected: bool
    identity_collision_rejected: bool
    eligibility_evaluated: bool
    gate_result_created: bool
    candidate_ranked: bool
    selection_performed: bool
    selected_meaning_created: bool
    msm_v1_modified: bool
    bootstrap_integration_enabled: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_written: bool
    rendered: bool
    delivered: bool
    schema_version: str = SLICE41B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SelectedMeaningLifecycleTransitionRecord:
    transition_id: str
    runtime_schema_record_id: str
    source_lifecycle_record_id: str
    target_lifecycle_record_id: str
    from_stage: SelectedMeaningLifecycleStage
    to_stage: SelectedMeaningLifecycleStage
    transition_kind: SelectedMeaningLifecycleTransitionKind
    version_custody_ref: str
    predecessor_transition_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    automatic_transition: bool
    eligibility_evaluated: bool
    candidate_ranked: bool
    selection_performed: bool
    selected_meaning_created: bool
    msm_v1_modified: bool
    bootstrap_integration_enabled: bool
    truth_evidence_permission_execution_created: bool
    route_tool_action_memory_rendering_delivery_created: bool
    schema_version: str = SLICE41B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SelectedMeaningLifecycleDecision:
    allowed: bool
    issues: tuple[SelectedMeaningValidationIssue, ...]
    runtime_schema_record_id: str
    source_lifecycle_record_id: str
    target_lifecycle_record_id: str
    transition_id: str
    from_stage: SelectedMeaningLifecycleStage
    to_stage: SelectedMeaningLifecycleStage
    transition_kind: SelectedMeaningLifecycleTransitionKind
    schema_version: str = SLICE41B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SelectedMeaningGovernanceBundle:
    bundle_id: str
    bundle_digest: str
    runtime_schema_record: SelectedMeaningRuntimeSchemaRecord
    version_custody: SelectedMeaningVersionCustody
    lifecycle_record: SelectedMeaningLifecycleRecord
    lifecycle_transitions: tuple[
        SelectedMeaningLifecycleTransitionRecord,
        ...,
    ]
    validation_only: bool
    immutable_successor_records: bool
    exact_predecessor_references_required: bool
    duplicate_and_collision_rejection_required: bool
    unknown_version_rejection_required: bool
    eligibility_evaluated: bool
    gate_result_created: bool
    candidate_ranked: bool
    selection_performed: bool
    selected_meaning_created: bool
    msm_v1_modified: bool
    bootstrap_integration_enabled: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_written: bool
    rendered: bool
    delivered: bool
    schema_version: str = SLICE41B_SCHEMA_VERSION


__all__ = (
    "CANONICAL_FIELD_ORDER_VERSION",
    "DIGEST_ALGORITHM",
    "SLICE41B_ACCEPTED_PARENT_HEAD",
    "SLICE41B_ACCEPTED_PARENT_SUBJECT",
    "SLICE41B_ACCEPTED_PARENT_TREE",
    "SLICE41B_SCHEMA_VERSION",
    "SUPPORTED_RUNTIME_SCHEMA_VERSIONS",
    "SUPPORTED_RUNTIME_SPEC_VERSIONS",
    "SelectedMeaningGovernanceBundle",
    "SelectedMeaningLifecycleDecision",
    "SelectedMeaningLifecycleRecord",
    "SelectedMeaningLifecycleStage",
    "SelectedMeaningLifecycleTransitionKind",
    "SelectedMeaningLifecycleTransitionRecord",
    "SelectedMeaningValidationCode",
    "SelectedMeaningValidationError",
    "SelectedMeaningValidationIssue",
    "SelectedMeaningValidationReport",
    "SelectedMeaningVersionCustody",
)
