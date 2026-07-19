"""Immutable deterministic Slice 40F intended-purport records.

Slice 40F recovers only the communicative act that is explicitly supported by
accepted candidate records and, when present, approved discourse ancestry,
authorized reference state, and exact active context. It never guesses hidden
intent, infers purpose from capability existence or conversation habit,
collapses multiple purposes, composes all verbal-cognition gates, creates a
candidate disposition, selects meaning, or authorizes downstream consequence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..governed_lifecycle.schema import GateGovernanceBundle


SLICE40F_ACCEPTED_PARENT_HEAD = "2727dc72cbaa436a7c31eec4bb916452c1261c8e"
SLICE40F_ACCEPTED_PARENT_TREE = "8a55315ab2a7a2f13a42e4cf26a60e908301c67a"
SLICE40F_ACCEPTED_PARENT_SUBJECT = (
    "Slice 40E deterministic connectedness gate runtime"
)
SLICE40F_SCHEMA_VERSION = (
    "aiweb-slice40f-intended-purport-recoverable-purpose-runtime-v1"
)
SLICE40F_PROFILE_VERSION = "v1.0.0"
DIGEST_ALGORITHM = "sha256"


class PurportDistinctionKind(str, Enum):
    MENTION_REQUEST = "mention_request"
    INSPECT_EXECUTE = "inspect_execute"
    PROPOSE_INSTALL = "propose_install"
    SIMULATE_ALTER_LIVE_STATE = "simulate_alter_live_state"
    REPORT_PROVE = "report_prove"
    RETRIEVE_MEMORY_WRITE_MEMORY = "retrieve_memory_write_memory"
    ASK_PERMISSION_POSSESS_PERMISSION = "ask_permission_possess_permission"
    VERIFY_REQUEST_VERIFIED_STATUS = "verify_request_verified_status"
    DELIVERY_MEANING_DELIVERY_AUTHORITY = (
        "delivery_meaning_delivery_authority"
    )


class CommunicativeActKind(str, Enum):
    MENTION = "mention"
    REQUEST = "request"
    INSPECT = "inspect"
    EXECUTE = "execute"
    PROPOSE = "propose"
    INSTALL = "install"
    SIMULATE = "simulate"
    ALTER_LIVE_STATE = "alter_live_state"
    REPORT = "report"
    PROVE = "prove"
    RETRIEVE_MEMORY = "retrieve_memory"
    WRITE_MEMORY = "write_memory"
    ASK_PERMISSION = "ask_permission"
    POSSESS_PERMISSION = "possess_permission"
    VERIFY_REQUEST = "verify_request"
    VERIFIED_STATUS = "verified_status"
    DELIVERY_MEANING = "delivery_meaning"
    DELIVERY_AUTHORITY = "delivery_authority"


PURPORT_DISTINCTION_PAIRS = {
    PurportDistinctionKind.MENTION_REQUEST: (
        CommunicativeActKind.MENTION,
        CommunicativeActKind.REQUEST,
    ),
    PurportDistinctionKind.INSPECT_EXECUTE: (
        CommunicativeActKind.INSPECT,
        CommunicativeActKind.EXECUTE,
    ),
    PurportDistinctionKind.PROPOSE_INSTALL: (
        CommunicativeActKind.PROPOSE,
        CommunicativeActKind.INSTALL,
    ),
    PurportDistinctionKind.SIMULATE_ALTER_LIVE_STATE: (
        CommunicativeActKind.SIMULATE,
        CommunicativeActKind.ALTER_LIVE_STATE,
    ),
    PurportDistinctionKind.REPORT_PROVE: (
        CommunicativeActKind.REPORT,
        CommunicativeActKind.PROVE,
    ),
    PurportDistinctionKind.RETRIEVE_MEMORY_WRITE_MEMORY: (
        CommunicativeActKind.RETRIEVE_MEMORY,
        CommunicativeActKind.WRITE_MEMORY,
    ),
    PurportDistinctionKind.ASK_PERMISSION_POSSESS_PERMISSION: (
        CommunicativeActKind.ASK_PERMISSION,
        CommunicativeActKind.POSSESS_PERMISSION,
    ),
    PurportDistinctionKind.VERIFY_REQUEST_VERIFIED_STATUS: (
        CommunicativeActKind.VERIFY_REQUEST,
        CommunicativeActKind.VERIFIED_STATUS,
    ),
    PurportDistinctionKind.DELIVERY_MEANING_DELIVERY_AUTHORITY: (
        CommunicativeActKind.DELIVERY_MEANING,
        CommunicativeActKind.DELIVERY_AUTHORITY,
    ),
}


class RecoverablePurposeAuthorityState(str, Enum):
    ADMITTED = "admitted"
    ABSENT = "absent"
    UNSUPPORTED = "unsupported"
    CONFLICTED = "conflicted"
    AMBIGUOUS = "ambiguous"


class RecoverablePurposeJudgment(str, Enum):
    RECOVERABLE = "recoverable"
    UNRECOVERABLE = "unrecoverable"
    NOT_EVALUATED = "not_evaluated"


class RecoverablePurposeFindingKind(str, Enum):
    RECOVERED_PURPOSE = "recovered_purpose"
    UNRECOVERABLE_PURPOSE = "unrecoverable_purpose"
    AMBIGUOUS_PURPOSE = "ambiguous_purpose"
    UNSUPPORTED_PURPOSE = "unsupported_purpose"
    CONFLICTED_PURPOSE = "conflicted_purpose"
    INDETERMINATE_AUTHORITY_ABSENT = "indeterminate_authority_absent"
    ALL_PURPOSE_ASSERTIONS_RECOVERED = "all_purpose_assertions_recovered"


class RecoverablePurposeOverallState(str, Enum):
    RECOVERABLE = "recoverable_purpose_recoverable"
    UNRECOVERABLE = "recoverable_purpose_unrecoverable"
    AMBIGUOUS = "recoverable_purpose_ambiguous"
    UNSUPPORTED = "recoverable_purpose_unsupported"
    CONFLICTED = "recoverable_purpose_conflicted"
    INDETERMINATE = "recoverable_purpose_indeterminate"


class RecoverablePurposeValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    INVALID_SHA256 = "invalid_sha256"
    DUPLICATE_ID = "duplicate_id"
    REFERENCE_NOT_FOUND = "reference_not_found"
    CROSS_RECORD_MISMATCH = "cross_record_mismatch"
    RECOVERABLE_PURPOSE_FAMILY_REQUIRED = "recoverable_purpose_family_required"
    SEALED_GOVERNANCE_REQUIRED = "sealed_governance_required"
    GOVERNANCE_INVALID = "governance_invalid"
    AUTHORITY_STATE_INVALID = "authority_state_invalid"
    JUDGMENT_INVALID = "judgment_invalid"
    COUNT_MISMATCH = "count_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    EXACT_PURPOSE_AUTHORITY_REQUIRED = "exact_purpose_authority_required"
    DISTINCTION_CONFLATION_PROHIBITED = "distinction_conflation_prohibited"
    UNAUTHORIZED_CONTEXT_PROHIBITED = "unauthorized_context_prohibited"
    HIDDEN_INTENT_PROHIBITED = "hidden_intent_prohibited"
    CAPABILITY_INFERENCE_PROHIBITED = "capability_inference_prohibited"
    CONVERSATION_HABIT_PROHIBITED = "conversation_habit_prohibited"
    AUTOMATIC_COLLAPSE_PROHIBITED = "automatic_collapse_prohibited"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"


@dataclass(frozen=True, slots=True)
class RecoverablePurposeValidationIssue:
    path: str
    code: RecoverablePurposeValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class RecoverablePurposeValidationReport:
    issues: tuple[RecoverablePurposeValidationIssue, ...]
    schema_version: str = SLICE40F_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class RecoverablePurposeValidationError(ValueError):
    def __init__(self, report: RecoverablePurposeValidationReport) -> None:
        self.report = report
        detail = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(
            detail or "Slice 40F recoverable-purpose validation failed"
        )


@dataclass(frozen=True, slots=True)
class RecoverablePurposeGateRuntimeProfile:
    profile_id: str
    profile_key: str
    profile_version: str
    gate_profile_ref: str
    gate_profile_version: str
    governing_authority_refs: tuple[str, ...]
    permitted_distinction_kinds: tuple[PurportDistinctionKind, ...]
    exact_candidate_records_required: bool
    approved_discourse_ancestry_only: bool
    authorized_reference_state_only: bool
    exact_active_context_only: bool
    hidden_intent_inference_allowed: bool
    capability_existence_inference_allowed: bool
    prior_conversation_habit_allowed: bool
    assistant_intuition_allowed: bool
    psychological_inference_allowed: bool
    emotional_interpretation_allowed: bool
    raw_text_only_inference_allowed: bool
    purpose_conflation_allowed: bool
    automatic_purpose_collapse_allowed: bool
    gate_composition_allowed: bool
    selected_meaning_allowed: bool
    route_tool_action_allowed: bool
    schema_version: str = SLICE40F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class RecoverablePurposeAssertion:
    assertion_id: str
    candidate_input_ref: str
    predicate_id: str
    predicate_version: str
    frame_id: str
    frame_version: str
    assertion_key: str
    distinction_kind: PurportDistinctionKind
    represented_act: CommunicativeActKind
    prohibited_conflation_act: CommunicativeActKind
    candidate_record_refs: tuple[str, ...]
    purpose_support_refs: tuple[str, ...]
    discourse_ancestry_refs: tuple[str, ...]
    authorized_reference_state_refs: tuple[str, ...]
    active_context_refs: tuple[str, ...]
    authority_refs: tuple[str, ...]
    exact_candidate_records: bool
    discourse_ancestry_authorized: bool
    reference_state_authorized: bool
    active_context_authorized: bool
    explicit_purpose_only: bool
    schema_version: str = SLICE40F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class RecoverablePurposeObservation:
    observation_id: str
    assertion_ref: str
    candidate_input_ref: str
    authority_state: RecoverablePurposeAuthorityState
    purpose_judgment: RecoverablePurposeJudgment
    supporting_refs: tuple[str, ...]
    missing_authority_refs: tuple[str, ...]
    conflicting_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    schema_version: str = SLICE40F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class RecoverablePurposeEvaluationInput:
    evaluation_input_id: str
    governance_bundle: GateGovernanceBundle
    runtime_profile: RecoverablePurposeGateRuntimeProfile
    candidate_input_ref: str
    predicate_id: str
    predicate_version: str
    frame_id: str
    frame_version: str
    assertions: tuple[RecoverablePurposeAssertion, ...]
    observations: tuple[RecoverablePurposeObservation, ...]
    candidate_record_refs: tuple[str, ...]
    discourse_ancestry_refs: tuple[str, ...]
    authorized_reference_state_refs: tuple[str, ...]
    active_context_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    raw_text_supplied: bool
    hidden_intent_inference_used: bool
    capability_existence_inference_used: bool
    prior_conversation_habit_used: bool
    assistant_intuition_used: bool
    psychological_inference_used: bool
    emotional_interpretation_used: bool
    raw_text_only_inference_used: bool
    purpose_conflation_used: bool
    automatic_purpose_collapse_used: bool
    unauthorized_context_used: bool
    candidate_structure_mutated: bool
    schema_version: str = SLICE40F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class RecoverablePurposeFinding:
    finding_id: str
    evaluation_input_ref: str
    assertion_ref: str | None
    finding_kind: RecoverablePurposeFindingKind
    distinction_kind: PurportDistinctionKind | None
    represented_act: CommunicativeActKind | None
    authority_state: RecoverablePurposeAuthorityState
    purpose_judgment: RecoverablePurposeJudgment
    supporting_refs: tuple[str, ...]
    missing_authority_refs: tuple[str, ...]
    conflicting_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    schema_version: str = SLICE40F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class RecoverablePurposeGateResult:
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
    overall_state: RecoverablePurposeOverallState
    findings: tuple[RecoverablePurposeFinding, ...]
    assertion_count: int
    recoverable_count: int
    unrecoverable_count: int
    ambiguous_count: int
    unsupported_count: int
    conflicted_count: int
    indeterminate_count: int
    deterministic: bool
    exact_purpose_authority_preserved: bool
    candidate_structure_mutated: bool
    hidden_intent_inference_used: bool
    capability_existence_inference_used: bool
    prior_conversation_habit_used: bool
    assistant_intuition_used: bool
    psychological_inference_used: bool
    emotional_interpretation_used: bool
    raw_text_only_inference_used: bool
    purpose_conflation_used: bool
    automatic_purpose_collapse_used: bool
    unauthorized_context_used: bool
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
    capability_availability_created: bool
    route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed: bool
    memory_written: bool
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
    schema_version: str = SLICE40F_SCHEMA_VERSION
