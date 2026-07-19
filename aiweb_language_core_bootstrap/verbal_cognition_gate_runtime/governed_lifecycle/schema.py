"""Slice 40B immutable governance records for verbal-cognition gate custody.

This subpackage extends the accepted Slice 40A schema with deterministic
canonicalization, strict validation, identity calculation, version custody,
and lifecycle law. It does not install or execute any gate-family evaluator
and it does not create any candidate disposition or selected meaning.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..schema import (
    VerbalCognitionGateFamily,
    VerbalCognitionGateReviewRecord,
)


SLICE40B_ACCEPTED_PARENT_HEAD = "09a0d20c91994b72edcd63c15780592d56394225"
SLICE40B_ACCEPTED_PARENT_TREE = "435de181f15b94824d1204a45d3f4c7d7f244f7b"
SLICE40B_ACCEPTED_PARENT_SUBJECT = (
    "Slice 40A verbal cognition gate core schema"
)
SLICE40B_SCHEMA_VERSION = "aiweb-slice40b-verbal-cognition-gate-governance-v1"
CANONICAL_FIELD_ORDER_VERSION = "aiweb-slice40b-canonical-field-order-v1"
DIGEST_ALGORITHM = "sha256"

SUPPORTED_GATE_VERSIONS = ("v1.0.0",)
SUPPORTED_GATE_PROFILE_VERSIONS = ("v1.0.0",)


class GateLifecycleStage(str, Enum):
    SCHEMA_DECLARED = "schema_declared"
    PROFILE_VERSION_BOUND = "profile_version_bound"
    CANDIDATE_REFERENCE_BOUND = "candidate_reference_bound"
    PROVENANCE_VALIDATED = "provenance_validated"
    RECORD_VALIDATED = "record_validated"
    RECORD_SEALED = "record_sealed"
    VALIDATION_INCOMPLETE = "validation_incomplete"
    UNKNOWN_VERSION_BLOCKED = "unknown_version_blocked"
    MALFORMED_RECORD_BLOCKED = "malformed_record_blocked"
    PROVENANCE_INVALID_BLOCKED = "provenance_invalid_blocked"


class GateLifecycleTransitionKind(str, Enum):
    DECLARE_SCHEMA = "declare_schema"
    BIND_PROFILE_VERSION = "bind_profile_version"
    BIND_CANDIDATE_REFERENCE = "bind_candidate_reference"
    VALIDATE_PROVENANCE = "validate_provenance"
    VALIDATE_RECORD = "validate_record"
    SEAL_RECORD = "seal_record"
    MARK_INCOMPLETE = "mark_incomplete"
    BLOCK_UNKNOWN_VERSION = "block_unknown_version"
    BLOCK_MALFORMED_RECORD = "block_malformed_record"
    BLOCK_INVALID_PROVENANCE = "block_invalid_provenance"
    RESUME_VALIDATION = "resume_validation"


class GateValidationCode(str, Enum):
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
    CROSS_RECORD_IDENTITY_MISMATCH = "cross_record_identity_mismatch"
    SCHEMA_VERSION_MISMATCH = "schema_version_mismatch"
    PROFILE_VERSION_MISMATCH = "profile_version_mismatch"
    GATE_VERSION_MISMATCH = "gate_version_mismatch"
    PROVENANCE_MISMATCH = "provenance_mismatch"
    REFERENCE_NOT_FOUND = "reference_not_found"
    LIFECYCLE_STAGE_INVALID = "lifecycle_stage_invalid"
    LIFECYCLE_TRANSITION_NOT_PERMITTED = (
        "lifecycle_transition_not_permitted"
    )
    LIFECYCLE_TRANSITION_KIND_MISMATCH = (
        "lifecycle_transition_kind_mismatch"
    )
    AUTOMATIC_TRANSITION_PROHIBITED = "automatic_transition_prohibited"
    GATE_EVALUATION_PROHIBITED = "gate_evaluation_prohibited"
    GATE_OUTCOME_PROHIBITED = "gate_outcome_prohibited"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"
    NONDETERMINISTIC_INPUT_PROHIBITED = (
        "nondeterministic_input_prohibited"
    )
    DUPLICATE_RECORD_ID = "duplicate_record_id"
    DUPLICATE_LIFECYCLE_RECORD = "duplicate_lifecycle_record"
    DUPLICATE_TRANSITION_ID = "duplicate_transition_id"
    CANONICAL_DIGEST_MISMATCH = "canonical_digest_mismatch"


@dataclass(frozen=True, slots=True)
class GateValidationIssue:
    path: str
    code: GateValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class GateValidationReport:
    issues: tuple[GateValidationIssue, ...]
    schema_version: str = SLICE40B_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class GateValidationError(ValueError):
    """Raised when Slice 40B validation fails closed."""

    def __init__(self, report: GateValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(
            summary or "Slice 40B verbal-cognition gate validation failed"
        )


@dataclass(frozen=True, slots=True)
class GateVersionCustody:
    custody_id: str
    review_record_id: str
    gate_id: str
    gate_version: str
    gate_profile_id: str
    gate_profile_version: str
    gate_family: VerbalCognitionGateFamily
    core_schema_version: str
    core_spec_version: str
    identity_schema_id: str
    profile_schema_id: str
    candidate_input_schema_id: str
    requirement_schema_id: str
    reason_ground_schema_id: str
    trace_schema_id: str
    provenance_schema_id: str
    limitation_schema_id: str
    review_record_schema_id: str
    governing_authority_versions: tuple[tuple[str, str], ...]
    predecessor_schema_versions: tuple[tuple[str, str], ...]
    canonical_field_order_version: str
    digest_algorithm: str
    non_llm_provenance: bool
    timestamps_in_identity: bool
    randomness_in_identity: bool
    process_identity_in_identity: bool
    filesystem_state_in_identity: bool
    environment_state_in_identity: bool
    hash_table_order_in_identity: bool
    runtime_evaluator_authorized: bool
    gate_evaluation_authorized: bool
    gate_outcome_authorized: bool
    selected_meaning_authorized: bool
    route_authorized: bool
    tool_authorized: bool
    action_authorized: bool
    memory_authorized: bool
    rendering_authorized: bool
    delivery_authorized: bool
    governance_schema_version: str = SLICE40B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class GateLifecycleRecord:
    lifecycle_record_id: str
    review_record_id: str
    gate_id: str
    gate_profile_id: str
    candidate_input_ref: str
    provenance_reference_id: str
    stage: GateLifecycleStage
    version_custody_ref: str
    predecessor_lifecycle_record_ids: tuple[str, ...]
    reason_refs: tuple[str, ...]
    automatic_progression: bool
    validation_performed: bool
    provenance_validation_performed: bool
    gate_evaluation_created: bool
    gate_outcome_created: bool
    candidate_disposition_created: bool
    selected_meaning_created: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed: bool
    rendered: bool
    delivered: bool
    external_resource_loaded: bool
    schema_version: str = SLICE40B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class GateLifecycleTransitionRecord:
    transition_id: str
    review_record_id: str
    source_lifecycle_record_id: str
    target_lifecycle_record_id: str
    from_stage: GateLifecycleStage
    to_stage: GateLifecycleStage
    transition_kind: GateLifecycleTransitionKind
    version_custody_ref: str
    reason_refs: tuple[str, ...]
    predecessor_transition_refs: tuple[str, ...]
    automatic_transition: bool
    gate_evaluation_created: bool
    gate_outcome_created: bool
    candidate_disposition_created: bool
    selected_meaning_created: bool
    permission_granted: bool
    execution_authorized: bool
    route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed: bool
    rendered: bool
    delivered: bool
    schema_version: str = SLICE40B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class GateLifecycleDecision:
    allowed: bool
    issues: tuple[GateValidationIssue, ...]
    review_record_id: str
    source_lifecycle_record_id: str
    target_lifecycle_record_id: str
    transition_id: str
    from_stage: GateLifecycleStage
    to_stage: GateLifecycleStage
    transition_kind: GateLifecycleTransitionKind
    schema_version: str = SLICE40B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class GateGovernanceBundle:
    bundle_id: str
    review_record: VerbalCognitionGateReviewRecord
    version_custody: GateVersionCustody
    lifecycle_records: tuple[GateLifecycleRecord, ...]
    lifecycle_transitions: tuple[GateLifecycleTransitionRecord, ...]
    canonical_digest: str
    validation_complete: bool
    provenance_validation_complete: bool
    schema_versions_known: bool
    gate_profile_version_known: bool
    runtime_evaluator_installed: bool
    gate_evaluation_performed: bool
    gate_outcome_created: bool
    candidate_disposition_created: bool
    selected_meaning_created: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed: bool
    rendered: bool
    delivered: bool
    external_resource_loaded: bool
    schema_version: str = SLICE40B_SCHEMA_VERSION
