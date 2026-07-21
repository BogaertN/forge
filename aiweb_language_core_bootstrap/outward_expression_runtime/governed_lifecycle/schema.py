"""Slice 42B validation, identity, version, and lifecycle custody schema.

This module adds deterministic validation custody around the immutable Slice
42A outward-expression runtime schema.  It does not admit selected-meaning or
outward-expression authority, evaluate expression eligibility, project
preservation obligations, construct governed outward meaning, build an
expression plan, realize text, modify MSM-v1, perform Echo validation, enable
bootstrap integration, deliver output, write memory, route tools, execute
an action, load an external resource, use a model, or supersede GP-014.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..schema import OutwardExpressionRuntimeSchemaRecord


SLICE42B_ACCEPTED_PARENT_HEAD = "bf38d5dbefd27d6cc69f38f5053071316d1ded63"
SLICE42B_ACCEPTED_PARENT_TREE = "ce3232f0adef1de5b7488ff1ec10a919cd9b54af"
SLICE42B_ACCEPTED_PARENT_SUBJECT = (
    "Slice 42A outward expression runtime core schema and authority contract"
)
SLICE42B_SCHEMA_VERSION = (
    "aiweb-slice42b-outward-expression-runtime-governance-v1"
)
VALIDATION_PROFILE_VERSION = (
    "aiweb-slice42b-outward-expression-validation-profile-v1"
)
CANONICAL_FIELD_ORDER_VERSION = (
    "aiweb-slice42b-outward-expression-canonical-field-order-v1"
)
DIGEST_ALGORITHM = "sha256"
SUPPORTED_RUNTIME_SCHEMA_VERSIONS = (
    "aiweb-slice42a-outward-expression-runtime-core-schema-v1",
)
SUPPORTED_RUNTIME_SPEC_VERSIONS = ("v1.0.0",)
SUPPORTED_VALIDATION_PROFILE_VERSIONS = (VALIDATION_PROFILE_VERSION,)


class OutwardExpressionLifecycleStage(str, Enum):
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


class OutwardExpressionLifecycleTransitionKind(str, Enum):
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


class OutwardExpressionValidationCode(str, Enum):
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
    EXPRESSION_AUTHORITY_PROHIBITED = "expression_authority_prohibited"
    ELIGIBILITY_EVALUATION_PROHIBITED = "eligibility_evaluation_prohibited"
    PRESERVATION_PROJECTION_PROHIBITED = "preservation_projection_prohibited"
    OUTWARD_MEANING_CONSTRUCTION_PROHIBITED = (
        "outward_meaning_construction_prohibited"
    )
    EXPRESSION_PLAN_PROHIBITED = "expression_plan_prohibited"
    SURFACE_REALIZATION_PROHIBITED = "surface_realization_prohibited"
    MSM_INTEGRATION_PROHIBITED = "msm_integration_prohibited"
    ECHO_VALIDATION_PROHIBITED = "echo_validation_prohibited"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"
    NONDETERMINISTIC_INPUT_PROHIBITED = "nondeterministic_input_prohibited"


@dataclass(frozen=True, slots=True)
class OutwardExpressionValidationIssue:
    path: str
    code: OutwardExpressionValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class OutwardExpressionValidationReport:
    issues: tuple[OutwardExpressionValidationIssue, ...]
    schema_version: str = SLICE42B_SCHEMA_VERSION
    profile_version: str = VALIDATION_PROFILE_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class OutwardExpressionValidationError(ValueError):
    """Raised when Slice 42B validation fails closed."""

    def __init__(self, report: OutwardExpressionValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(
            summary or "Slice 42B outward-expression validation failed"
        )


@dataclass(frozen=True, slots=True)
class OutwardExpressionVersionCustody:
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
    selected_meaning_chain_admission_authorized: bool
    outward_expression_authority_admission_authorized: bool
    expression_eligibility_evaluation_authorized: bool
    preservation_obligation_projection_authorized: bool
    governed_outward_meaning_construction_authorized: bool
    expression_plan_construction_authorized: bool
    surface_realization_authorized: bool
    msm_v1_mutation_or_integration_authorized: bool
    echo_validation_authorized: bool
    bootstrap_integration_authorized: bool
    delivery_authorized: bool
    truth_evidence_permission_execution_authorized: bool
    route_api_network_filesystem_memory_tool_action_authorized: bool
    external_resource_authority: bool
    model_embedding_vector_rag_similarity_authority: bool
    gp014_supersession_authorized: bool
    governance_schema_version: str = SLICE42B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class OutwardExpressionLifecycleRecord:
    lifecycle_record_id: str
    runtime_schema_record_id: str
    version_custody_ref: str
    validation_profile_version: str
    stage: OutwardExpressionLifecycleStage
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
    structural_validity_grants_expression_authority: bool
    selected_meaning_chain_admitted: bool
    outward_expression_authority_admitted: bool
    expression_eligibility_evaluated: bool
    preservation_obligations_projected: bool
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
    schema_version: str = SLICE42B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class OutwardExpressionLifecycleTransitionRecord:
    transition_id: str
    runtime_schema_record_id: str
    source_lifecycle_record_id: str
    target_lifecycle_record_id: str
    from_stage: OutwardExpressionLifecycleStage
    to_stage: OutwardExpressionLifecycleStage
    transition_kind: OutwardExpressionLifecycleTransitionKind
    version_custody_ref: str
    validation_profile_version: str
    predecessor_transition_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    automatic_transition: bool
    structural_validity_grants_expression_authority: bool
    selected_meaning_chain_admitted: bool
    outward_expression_authority_admitted: bool
    expression_eligibility_evaluated: bool
    preservation_obligations_projected: bool
    governed_outward_meaning_created: bool
    expression_plan_created: bool
    surface_realization_performed: bool
    msm_v1_modified_or_integrated: bool
    echo_validation_performed: bool
    bootstrap_integration_enabled: bool
    delivered: bool
    truth_evidence_permission_execution_created: bool
    route_api_network_filesystem_memory_tool_action_created: bool
    external_resource_or_model_authority_created: bool
    gp014_superseded: bool
    schema_version: str = SLICE42B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class OutwardExpressionLifecycleDecision:
    allowed: bool
    issues: tuple[OutwardExpressionValidationIssue, ...]
    runtime_schema_record_id: str
    source_lifecycle_record_id: str
    target_lifecycle_record_id: str
    transition_id: str
    from_stage: OutwardExpressionLifecycleStage
    to_stage: OutwardExpressionLifecycleStage
    transition_kind: OutwardExpressionLifecycleTransitionKind
    schema_version: str = SLICE42B_SCHEMA_VERSION
    profile_version: str = VALIDATION_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class OutwardExpressionGovernanceBundle:
    bundle_id: str
    bundle_digest: str
    runtime_schema_record: OutwardExpressionRuntimeSchemaRecord
    version_custody: OutwardExpressionVersionCustody
    lifecycle_record: OutwardExpressionLifecycleRecord
    lifecycle_transitions: tuple[OutwardExpressionLifecycleTransitionRecord, ...]
    validation_only: bool
    immutable_successor_records: bool
    exact_predecessor_references_required: bool
    duplicate_and_collision_rejection_required: bool
    unknown_version_rejection_required: bool
    malformed_record_rejection_required: bool
    cross_record_consistency_required: bool
    structural_validity_grants_expression_authority: bool
    selected_meaning_chain_admitted: bool
    outward_expression_authority_admitted: bool
    expression_eligibility_evaluated: bool
    preservation_obligations_projected: bool
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
    schema_version: str = SLICE42B_SCHEMA_VERSION
    profile_version: str = VALIDATION_PROFILE_VERSION


__all__ = (
    "CANONICAL_FIELD_ORDER_VERSION",
    "DIGEST_ALGORITHM",
    "SLICE42B_ACCEPTED_PARENT_HEAD",
    "SLICE42B_ACCEPTED_PARENT_SUBJECT",
    "SLICE42B_ACCEPTED_PARENT_TREE",
    "SLICE42B_SCHEMA_VERSION",
    "SUPPORTED_RUNTIME_SCHEMA_VERSIONS",
    "SUPPORTED_RUNTIME_SPEC_VERSIONS",
    "SUPPORTED_VALIDATION_PROFILE_VERSIONS",
    "VALIDATION_PROFILE_VERSION",
    "OutwardExpressionGovernanceBundle",
    "OutwardExpressionLifecycleDecision",
    "OutwardExpressionLifecycleRecord",
    "OutwardExpressionLifecycleStage",
    "OutwardExpressionLifecycleTransitionKind",
    "OutwardExpressionLifecycleTransitionRecord",
    "OutwardExpressionValidationCode",
    "OutwardExpressionValidationError",
    "OutwardExpressionValidationIssue",
    "OutwardExpressionValidationReport",
    "OutwardExpressionVersionCustody",
)
