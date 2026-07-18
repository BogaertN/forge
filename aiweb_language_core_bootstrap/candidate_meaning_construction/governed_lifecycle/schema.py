"""Slice 39B immutable governance records for candidate-meaning custody.

This subpackage is intentionally isolated from the accepted Slice 39A parent
package.  It adds pure deterministic identity, validation, version custody,
and lifecycle-law records without mutating the Slice 39A schema and without
installing a candidate constructor, gate engine, route, action, memory path,
renderer, or delivery path.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..schema import (
    CandidateMeaningAlternativeReference,
    CandidateMeaningConstructionReceipt,
    CandidateMeaningConstructionStatus,
    CandidateMeaningContent,
    CandidateMeaningIdentity,
    CandidateMeaningProvenance,
    CandidateMeaningState,
)


SLICE39B_ACCEPTED_PARENT_HEAD = "b01f9e190d2bc6dde39340bda9260aeaa02832d6"
SLICE39B_ACCEPTED_PARENT_TREE = "0c58df87d63cf06dba1f0c535db12b467d65910f"
SLICE39B_ACCEPTED_PARENT_SUBJECT = "Slice 39A candidate meaning core schema"
SLICE39B_SCHEMA_VERSION = "aiweb-slice39b-candidate-meaning-governance-v1"
CANONICAL_FIELD_ORDER_VERSION = "aiweb-slice39b-canonical-field-order-v1"
DIGEST_ALGORITHM = "sha256"


class CandidateMeaningLifecycleStage(str, Enum):
    SCHEMA_DECLARED = "schema_declared"
    PROVENANCE_BOUND = "provenance_bound"
    CONTENT_CONSTRUCTED = "content_constructed"
    CANDIDATE_SEALED = "candidate_sealed"
    CANDIDATE_SET_REFERENCED = "candidate_set_referenced"
    CONSTRUCTION_INCOMPLETE = "construction_incomplete"
    PREDECESSOR_INVALID = "predecessor_invalid"


class CandidateMeaningLifecycleTransitionKind(str, Enum):
    DECLARE_SCHEMA = "declare_schema"
    BIND_PROVENANCE = "bind_provenance"
    CONSTRUCT_CONTENT = "construct_content"
    SEAL_CANDIDATE = "seal_candidate"
    REFERENCE_CANDIDATE_SET = "reference_candidate_set"
    MARK_INCOMPLETE = "mark_incomplete"
    BLOCK_INVALID_PREDECESSOR = "block_invalid_predecessor"
    RESUME_CONSTRUCTION = "resume_construction"


class CandidateMeaningValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    REQUIRED_VALUE_MISSING = "required_value_missing"
    INVALID_TEXT = "invalid_text"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
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
    REGISTRY_SNAPSHOT_VERSION_MISMATCH = (
        "registry_snapshot_version_mismatch"
    )
    ANCESTRY_REQUIRED = "ancestry_required"
    REFERENCE_NOT_FOUND = "reference_not_found"
    STATUS_MISMATCH = "status_mismatch"
    LIFECYCLE_STAGE_INVALID = "lifecycle_stage_invalid"
    LIFECYCLE_TRANSITION_NOT_PERMITTED = (
        "lifecycle_transition_not_permitted"
    )
    LIFECYCLE_TRANSITION_KIND_MISMATCH = (
        "lifecycle_transition_kind_mismatch"
    )
    AUTOMATIC_TRANSITION_PROHIBITED = "automatic_transition_prohibited"
    GATE_PROGRESSION_PROHIBITED = "gate_progression_prohibited"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"
    NONDETERMINISTIC_INPUT_PROHIBITED = (
        "nondeterministic_input_prohibited"
    )
    DUPLICATE_RECORD_ID = "duplicate_record_id"
    DUPLICATE_LIFECYCLE_RECORD = "duplicate_lifecycle_record"
    DUPLICATE_TRANSITION_ID = "duplicate_transition_id"
    CANONICAL_DIGEST_MISMATCH = "canonical_digest_mismatch"


@dataclass(frozen=True, slots=True)
class CandidateMeaningValidationIssue:
    path: str
    code: CandidateMeaningValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class CandidateMeaningValidationReport:
    issues: tuple[CandidateMeaningValidationIssue, ...]
    schema_version: str = SLICE39B_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class CandidateMeaningValidationError(ValueError):
    """Raised when Slice 39B validation fails closed."""

    def __init__(self, report: CandidateMeaningValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(
            summary or "Slice 39B candidate-meaning validation failed"
        )


@dataclass(frozen=True, slots=True)
class CandidateMeaningVersionCustody:
    custody_id: str
    candidate_meaning_id: str
    candidate_version: str
    schema_version: str
    identity_schema_id: str
    content_schema_id: str
    provenance_schema_id: str
    alternative_reference_schema_id: str
    construction_receipt_schema_id: str
    state_schema_id: str
    construction_profile_id: str
    construction_profile_version: str
    slice37_registry_snapshot_id: str
    slice37_registry_snapshot_version: str
    slice38_registry_snapshot_id: str
    slice38_registry_snapshot_version: str
    compatibility_registry_snapshot_id: str
    compatibility_registry_snapshot_version: str
    canonical_field_order_version: str
    digest_algorithm: str
    non_llm_provenance: bool
    timestamps_in_identity: bool
    randomness_in_identity: bool
    process_identity_in_identity: bool
    filesystem_state_in_identity: bool
    environment_state_in_identity: bool
    hash_table_order_in_identity: bool
    runtime_authorized: bool
    gate_progression_authorized: bool
    action_authorized: bool
    memory_authorized: bool
    rendering_authorized: bool
    delivery_authorized: bool
    governance_schema_version: str = SLICE39B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateMeaningLifecycleRecord:
    lifecycle_record_id: str
    candidate_meaning_id: str
    stage: CandidateMeaningLifecycleStage
    construction_status: CandidateMeaningConstructionStatus
    identity_ref: str
    content_ref: str
    provenance_ref: str
    receipt_ref: str
    state_ref: str
    version_custody_ref: str
    candidate_set_reference_ids: tuple[str, ...]
    predecessor_lifecycle_record_ids: tuple[str, ...]
    reason_refs: tuple[str, ...]
    automatic_progression: bool
    gate_progression_created: bool
    selected_meaning_created: bool
    ambiguity_disposition_created: bool
    clarification_required_created: bool
    refusal_created: bool
    blocked_progression_created: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    route_created: bool
    invocation_created: bool
    action_performed: bool
    memory_accessed: bool
    rendered: bool
    delivered: bool
    schema_version: str = SLICE39B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateMeaningLifecycleTransitionRecord:
    transition_id: str
    candidate_meaning_id: str
    source_lifecycle_record_id: str
    target_lifecycle_record_id: str
    from_stage: CandidateMeaningLifecycleStage
    to_stage: CandidateMeaningLifecycleStage
    transition_kind: CandidateMeaningLifecycleTransitionKind
    version_custody_ref: str
    reason_refs: tuple[str, ...]
    predecessor_transition_refs: tuple[str, ...]
    automatic_transition: bool
    gate_progression_created: bool
    selected_meaning_created: bool
    ambiguity_disposition_created: bool
    clarification_required_created: bool
    refusal_created: bool
    blocked_progression_created: bool
    permission_granted: bool
    route_created: bool
    invocation_created: bool
    action_performed: bool
    memory_accessed: bool
    rendered: bool
    delivered: bool
    schema_version: str = SLICE39B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateMeaningLifecycleDecision:
    allowed: bool
    issues: tuple[CandidateMeaningValidationIssue, ...]
    candidate_meaning_id: str
    source_lifecycle_record_id: str
    target_lifecycle_record_id: str
    transition_id: str
    from_stage: CandidateMeaningLifecycleStage
    to_stage: CandidateMeaningLifecycleStage
    transition_kind: CandidateMeaningLifecycleTransitionKind
    schema_version: str = SLICE39B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CandidateMeaningGovernanceBundle:
    bundle_id: str
    identity: CandidateMeaningIdentity
    content: CandidateMeaningContent
    provenance: CandidateMeaningProvenance
    alternative_references: tuple[CandidateMeaningAlternativeReference, ...]
    construction_receipt: CandidateMeaningConstructionReceipt
    state: CandidateMeaningState
    version_custody: CandidateMeaningVersionCustody
    lifecycle_records: tuple[CandidateMeaningLifecycleRecord, ...]
    lifecycle_transitions: tuple[CandidateMeaningLifecycleTransitionRecord, ...]
    canonical_digest: str
    runtime_constructor_installed: bool
    candidate_ranking_installed: bool
    gate_engine_installed: bool
    selected_meaning_installed: bool
    route_installed: bool
    invocation_installed: bool
    action_installed: bool
    memory_installed: bool
    rendering_installed: bool
    delivery_installed: bool
    schema_version: str = SLICE39B_SCHEMA_VERSION
