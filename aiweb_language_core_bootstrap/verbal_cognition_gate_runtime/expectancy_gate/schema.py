"""Immutable Slice 40C expectancy-gate runtime records.

The records in this module describe deterministic evaluation of exact,
previously admitted predicate/frame requirements.  They do not construct
candidate meaning, repair missing structure, create clarification or refusal,
compose the four verbal-cognition gates, select meaning, or authorize any
route, tool, action, memory, rendering, delivery, evidence, or truth result.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..governed_lifecycle.schema import GateGovernanceBundle


SLICE40C_ACCEPTED_PARENT_HEAD = "5ad63716f4da2833a23758d083671a7ee92ae22a"
SLICE40C_ACCEPTED_PARENT_TREE = "77ac09bc0c10460918537094ddd1eef106ca5287"
SLICE40C_ACCEPTED_PARENT_SUBJECT = (
    "Slice 40B deterministic gate validation identity versioning lifecycle"
)
SLICE40C_SCHEMA_VERSION = "aiweb-slice40c-expectancy-gate-runtime-v1"
SLICE40C_PROFILE_VERSION = "v1.0.0"
DIGEST_ALGORITHM = "sha256"


class ExpectancyRequirementKind(str, Enum):
    REQUIRED_ROLE = "required_role"
    REQUIRED_RELATION = "required_relation"
    REQUIRED_COMPLEMENT = "required_complement"
    REQUIRED_PURPOSE_INFORMATION = "required_purpose_information"
    OPTIONAL_DETAIL = "optional_detail"


class ExpectancyAuthorityState(str, Enum):
    ADMITTED = "admitted"
    ABSENT = "absent"
    UNSUPPORTED = "unsupported"
    CONFLICTED = "conflicted"


class ExpectancyFindingKind(str, Enum):
    REQUIRED_ROLE_MISSING = "required_role_missing"
    REQUIRED_RELATION_MISSING = "required_relation_missing"
    REQUIRED_COMPLEMENT_MISSING = "required_complement_missing"
    REQUIRED_PURPOSE_INFORMATION_MISSING = (
        "required_purpose_information_missing"
    )
    OPTIONAL_DETAIL_OMITTED = "optional_detail_omitted"
    STRUCTURALLY_COMPLETE = "structurally_complete_for_expectancy"
    INDETERMINATE_REQUIRED_AUTHORITY_ABSENT = (
        "indeterminate_required_authority_absent"
    )


class ExpectancyOverallState(str, Enum):
    STRUCTURALLY_COMPLETE = "structurally_complete_for_expectancy"
    INCOMPLETE = "expectancy_incomplete"
    INDETERMINATE = "expectancy_indeterminate"


class ExpectancyValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    REQUIRED_VALUE_MISSING = "required_value_missing"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    INVALID_SHA256 = "invalid_sha256"
    DUPLICATE_ID = "duplicate_id"
    REFERENCE_NOT_FOUND = "reference_not_found"
    CROSS_RECORD_MISMATCH = "cross_record_mismatch"
    EXPECTANCY_FAMILY_REQUIRED = "expectancy_family_required"
    SEALED_GOVERNANCE_REQUIRED = "sealed_governance_required"
    GOVERNANCE_INVALID = "governance_invalid"
    AUTHORITY_STATE_INVALID = "authority_state_invalid"
    COUNT_MISMATCH = "count_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    RAW_TEXT_PROHIBITED = "raw_text_prohibited"
    INVENTED_REQUIREMENT_PROHIBITED = "invented_requirement_prohibited"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"


@dataclass(frozen=True, slots=True)
class ExpectancyValidationIssue:
    path: str
    code: ExpectancyValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class ExpectancyValidationReport:
    issues: tuple[ExpectancyValidationIssue, ...]
    schema_version: str = SLICE40C_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class ExpectancyValidationError(ValueError):
    def __init__(self, report: ExpectancyValidationReport) -> None:
        self.report = report
        message = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(message or "Slice 40C expectancy validation failed")


@dataclass(frozen=True, slots=True)
class ExpectancyGateRuntimeProfile:
    profile_id: str
    profile_key: str
    profile_version: str
    gate_profile_ref: str
    gate_profile_version: str
    governing_authority_refs: tuple[str, ...]
    permitted_requirement_kinds: tuple[ExpectancyRequirementKind, ...]
    exact_admitted_requirements_only: bool
    raw_text_inspection_allowed: bool
    hidden_context_allowed: bool
    default_participant_inference_allowed: bool
    unstated_referent_inference_allowed: bool
    automatic_clarification_allowed: bool
    gate_composition_allowed: bool
    selected_meaning_allowed: bool
    route_tool_action_allowed: bool
    schema_version: str = SLICE40C_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ExpectancyRequirement:
    requirement_id: str
    candidate_input_ref: str
    predicate_id: str
    predicate_version: str
    frame_id: str
    frame_version: str
    requirement_key: str
    requirement_kind: ExpectancyRequirementKind
    requirement_source_refs: tuple[str, ...]
    authority_refs: tuple[str, ...]
    subject_record_refs: tuple[str, ...]
    relation_refs: tuple[str, ...]
    minimum_count: int
    required: bool
    exact_admitted_requirement: bool
    schema_version: str = SLICE40C_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ExpectancyObservation:
    observation_id: str
    requirement_ref: str
    candidate_input_ref: str
    authority_state: ExpectancyAuthorityState
    observed_record_refs: tuple[str, ...]
    observed_relation_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    schema_version: str = SLICE40C_SCHEMA_VERSION

    @property
    def observed_count(self) -> int:
        return len(self.observed_record_refs) + len(self.observed_relation_refs)


@dataclass(frozen=True, slots=True)
class ExpectancyEvaluationInput:
    evaluation_input_id: str
    governance_bundle: GateGovernanceBundle
    runtime_profile: ExpectancyGateRuntimeProfile
    candidate_input_ref: str
    predicate_id: str
    predicate_version: str
    frame_id: str
    frame_version: str
    requirements: tuple[ExpectancyRequirement, ...]
    observations: tuple[ExpectancyObservation, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    raw_text_supplied: bool
    hidden_context_used: bool
    defaults_used: bool
    inferred_participants_created: bool
    inferred_referents_created: bool
    schema_version: str = SLICE40C_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ExpectancyFinding:
    finding_id: str
    evaluation_input_ref: str
    requirement_ref: str | None
    finding_kind: ExpectancyFindingKind
    authority_state: ExpectancyAuthorityState
    required_count: int
    observed_count: int
    supporting_record_refs: tuple[str, ...]
    supporting_relation_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    schema_version: str = SLICE40C_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ExpectancyGateResult:
    result_id: str
    evaluation_input_ref: str
    review_record_id: str
    gate_id: str
    gate_profile_id: str
    candidate_input_ref: str
    predicate_id: str
    predicate_version: str
    frame_id: str
    frame_version: str
    overall_state: ExpectancyOverallState
    findings: tuple[ExpectancyFinding, ...]
    requirement_count: int
    required_requirement_count: int
    satisfied_required_count: int
    missing_required_count: int
    optional_omitted_count: int
    indeterminate_count: int
    deterministic: bool
    exact_requirement_authority_preserved: bool
    candidate_structure_mutated: bool
    missing_role_filled: bool
    referent_invented: bool
    unstated_participant_inferred: bool
    clarification_required_created: bool
    rejection_created: bool
    refusal_relevant_created: bool
    blocked_progression_created: bool
    composed_gate_outcome_created: bool
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
    language_model_used: bool
    embedding_used: bool
    vector_used: bool
    rag_used: bool
    semantic_similarity_used: bool
    canonical_digest: str
    digest_algorithm: str = DIGEST_ALGORITHM
    schema_version: str = SLICE40C_SCHEMA_VERSION


__all__ = (
    "DIGEST_ALGORITHM",
    "SLICE40C_ACCEPTED_PARENT_HEAD",
    "SLICE40C_ACCEPTED_PARENT_SUBJECT",
    "SLICE40C_ACCEPTED_PARENT_TREE",
    "SLICE40C_PROFILE_VERSION",
    "SLICE40C_SCHEMA_VERSION",
    "ExpectancyAuthorityState",
    "ExpectancyEvaluationInput",
    "ExpectancyFinding",
    "ExpectancyFindingKind",
    "ExpectancyGateResult",
    "ExpectancyGateRuntimeProfile",
    "ExpectancyOverallState",
    "ExpectancyObservation",
    "ExpectancyRequirement",
    "ExpectancyRequirementKind",
    "ExpectancyValidationCode",
    "ExpectancyValidationError",
    "ExpectancyValidationIssue",
    "ExpectancyValidationReport",
)
