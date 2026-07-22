"""Slice 43B deterministic validation, identity, version, and lifecycle schema.

This additive companion governs the immutable Slice 43A RMC Echo schema. It
validates structure and exact internal custody only. It does not admit Slice 42
sources, compare meaning preservation, classify drift, decide an Echo
disposition, issue rejection or containment, repair expression text, integrate
MSM-v1, deliver output, use a model, route a tool, perform an action, or
supersede GP-014.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..schema import RmcEchoRuntimeSchemaRecord


SLICE43B_ACCEPTED_PARENT_HEAD = "32719319e3df8dcde42f3ececcb14863d2c541b8"
SLICE43B_ACCEPTED_PARENT_TREE = "d84b9a8e9f612d1ed461bb3785aef52d2acabbef"
SLICE43B_ACCEPTED_PARENT_SUBJECT = (
    "Slice 43A RMC Echo core schema and authority boundary"
)
SLICE43B_SCHEMA_VERSION = "aiweb-slice43b-rmc-echo-governance-v1"
VALIDATION_PROFILE_VERSION = "aiweb-slice43b-rmc-echo-validation-profile-v1"
CANONICAL_FIELD_ORDER_VERSION = (
    "aiweb-slice43b-rmc-echo-canonical-field-order-v1"
)
DIGEST_ALGORITHM = "sha256"
SUPPORTED_RUNTIME_SCHEMA_VERSIONS = (
    "aiweb-slice43a-rmc-echo-core-schema-v1",
)
SUPPORTED_RUNTIME_SPEC_VERSIONS = ("v1.0.0",)
SUPPORTED_VALIDATION_PROFILE_VERSIONS = (VALIDATION_PROFILE_VERSION,)


class RmcEchoLifecycleStage(str, Enum):
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
    DUPLICATE_RECORD_BLOCKED = "duplicate_record_blocked"
    IDENTITY_COLLISION_BLOCKED = "identity_collision_blocked"


class RmcEchoLifecycleTransitionKind(str, Enum):
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
    BLOCK_DUPLICATE_RECORD = "block_duplicate_record"
    BLOCK_IDENTITY_COLLISION = "block_identity_collision"
    RESUME_VALIDATION = "resume_validation"


class RmcEchoValidationCode(str, Enum):
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
    PROFILE_VERSION_MISMATCH = "profile_version_mismatch"
    PREDECESSOR_REFERENCE_MISMATCH = "predecessor_reference_mismatch"
    PREDECESSOR_REFERENCE_MISSING = "predecessor_reference_missing"
    REFERENCE_NOT_FOUND = "reference_not_found"
    CANONICAL_DIGEST_MISMATCH = "canonical_digest_mismatch"
    LIFECYCLE_STAGE_INVALID = "lifecycle_stage_invalid"
    LIFECYCLE_TRANSITION_NOT_PERMITTED = "lifecycle_transition_not_permitted"
    AUTOMATIC_TRANSITION_PROHIBITED = "automatic_transition_prohibited"
    SOURCE_ADMISSION_PROHIBITED = "source_admission_prohibited"
    MEANING_COMPARISON_PROHIBITED = "meaning_comparison_prohibited"
    DRIFT_CLASSIFICATION_PROHIBITED = "drift_classification_prohibited"
    DISPOSITION_DECISION_PROHIBITED = "disposition_decision_prohibited"
    REJECTION_OR_CONTAINMENT_PROHIBITED = (
        "rejection_or_containment_prohibited"
    )
    EXPRESSION_REPAIR_PROHIBITED = "expression_repair_prohibited"
    MSM_INTEGRATION_PROHIBITED = "msm_integration_prohibited"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"
    NONDETERMINISTIC_INPUT_PROHIBITED = "nondeterministic_input_prohibited"


@dataclass(frozen=True, slots=True)
class RmcEchoValidationIssue:
    path: str
    code: RmcEchoValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class RmcEchoValidationReport:
    issues: tuple[RmcEchoValidationIssue, ...]
    schema_version: str = SLICE43B_SCHEMA_VERSION
    profile_version: str = VALIDATION_PROFILE_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class RmcEchoValidationError(ValueError):
    """Raised when Slice 43B validation fails closed."""

    def __init__(self, report: RmcEchoValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(summary or "Slice 43B RMC Echo validation failed")


@dataclass(frozen=True, slots=True)
class RmcEchoVersionCustody:
    custody_id: str
    runtime_schema_record_id: str
    runtime_schema_version: str
    runtime_schema_id: str
    runtime_spec_id: str
    runtime_spec_version: str
    validation_profile_version: str
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
    slice42_source_admission_authorized: bool
    meaning_preservation_comparison_authorized: bool
    validation_finding_construction_authorized: bool
    drift_classification_authorized: bool
    materiality_decision_authorized: bool
    echo_disposition_decision_authorized: bool
    rejection_or_containment_issuance_authorized: bool
    expression_repair_authorized: bool
    msm_v1_mutation_or_integration_authorized: bool
    bootstrap_integration_authorized: bool
    delivery_authorized: bool
    truth_evidence_permission_execution_authorized: bool
    route_api_network_filesystem_memory_tool_action_authorized: bool
    external_resource_authority: bool
    model_embedding_vector_rag_similarity_authority: bool
    gp014_supersession_authorized: bool
    governance_schema_version: str = SLICE43B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class RmcEchoLifecycleRecord:
    lifecycle_record_id: str
    runtime_schema_record_id: str
    version_custody_ref: str
    validation_profile_version: str
    stage: RmcEchoLifecycleStage
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
    structural_validity_grants_echo_authority: bool
    slice42_sources_admitted: bool
    meaning_preservation_comparison_performed: bool
    validation_findings_created: bool
    drift_findings_created: bool
    materiality_decided: bool
    echo_disposition_decided: bool
    rejection_issued: bool
    containment_issued: bool
    expression_repaired: bool
    msm_v1_modified_or_integrated: bool
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
    schema_version: str = SLICE43B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class RmcEchoLifecycleTransitionRecord:
    transition_id: str
    runtime_schema_record_id: str
    source_lifecycle_record_id: str
    target_lifecycle_record_id: str
    from_stage: RmcEchoLifecycleStage
    to_stage: RmcEchoLifecycleStage
    transition_kind: RmcEchoLifecycleTransitionKind
    version_custody_ref: str
    validation_profile_version: str
    predecessor_transition_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    automatic_transition: bool
    structural_validity_grants_echo_authority: bool
    slice42_source_admission_authorized: bool
    meaning_preservation_comparison_authorized: bool
    drift_classification_authorized: bool
    disposition_decision_authorized: bool
    rejection_or_containment_authorized: bool
    expression_repair_authorized: bool
    msm_v1_integration_authorized: bool
    delivery_authorized: bool
    downstream_authority_authorized: bool
    model_or_similarity_authority_used: bool
    gp014_supersession_authorized: bool
    schema_version: str = SLICE43B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class RmcEchoLifecycleDecision:
    allowed: bool
    issues: tuple[RmcEchoValidationIssue, ...]
    runtime_schema_record_id: str
    source_lifecycle_record_id: str
    target_lifecycle_record_id: str
    transition_id: str
    from_stage: RmcEchoLifecycleStage
    to_stage: RmcEchoLifecycleStage
    transition_kind: RmcEchoLifecycleTransitionKind


@dataclass(frozen=True, slots=True)
class RmcEchoGovernanceBundle:
    bundle_id: str
    bundle_digest: str
    runtime_schema_record: RmcEchoRuntimeSchemaRecord
    version_custody: RmcEchoVersionCustody
    lifecycle_records: tuple[RmcEchoLifecycleRecord, ...]
    lifecycle_transitions: tuple[RmcEchoLifecycleTransitionRecord, ...]
    validation_only: bool
    immutable_successor_records: bool
    exact_predecessor_references_required: bool
    duplicate_and_collision_rejection_required: bool
    unknown_version_rejection_required: bool
    malformed_record_rejection_required: bool
    cross_record_consistency_required: bool
    structural_validity_grants_echo_authority: bool
    slice42_sources_admitted: bool
    meaning_preservation_comparison_performed: bool
    validation_findings_created: bool
    drift_findings_created: bool
    materiality_decided: bool
    echo_disposition_decided: bool
    rejection_issued: bool
    containment_issued: bool
    expression_repaired: bool
    msm_v1_modified_or_integrated: bool
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
    schema_version: str = SLICE43B_SCHEMA_VERSION
    profile_version: str = VALIDATION_PROFILE_VERSION


__all__ = (
    "CANONICAL_FIELD_ORDER_VERSION",
    "DIGEST_ALGORITHM",
    "SLICE43B_ACCEPTED_PARENT_HEAD",
    "SLICE43B_ACCEPTED_PARENT_SUBJECT",
    "SLICE43B_ACCEPTED_PARENT_TREE",
    "SLICE43B_SCHEMA_VERSION",
    "SUPPORTED_RUNTIME_SCHEMA_VERSIONS",
    "SUPPORTED_RUNTIME_SPEC_VERSIONS",
    "SUPPORTED_VALIDATION_PROFILE_VERSIONS",
    "VALIDATION_PROFILE_VERSION",
    "RmcEchoGovernanceBundle",
    "RmcEchoLifecycleDecision",
    "RmcEchoLifecycleRecord",
    "RmcEchoLifecycleStage",
    "RmcEchoLifecycleTransitionKind",
    "RmcEchoLifecycleTransitionRecord",
    "RmcEchoValidationCode",
    "RmcEchoValidationError",
    "RmcEchoValidationIssue",
    "RmcEchoValidationReport",
    "RmcEchoVersionCustody",
)
