"""Immutable deterministic Slice 40E connectedness-gate records.

Slice 40E evaluates only exact connection assertions admitted by accepted
source-span, structural-ancestry, scope, attachment, operator-trail,
predicate/frame, and candidate-lineage authority.  Co-occurrence in one source
expression or manifest is never sufficient connection authority.  This slice
does not invent transitive links, rewrite candidate structure, compose all
verbal-cognition gates, create a candidate disposition, select meaning, or
authorize downstream consequence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..governed_lifecycle.schema import GateGovernanceBundle


SLICE40E_ACCEPTED_PARENT_HEAD = "b9b5e835e7506bc2b7849d3221b0328227add7fd"
SLICE40E_ACCEPTED_PARENT_TREE = "cd26ca5243fe76c0a7a12e2ee53e471538796eee"
SLICE40E_ACCEPTED_PARENT_SUBJECT = "Slice 40D deterministic congruity gate runtime"
SLICE40E_SCHEMA_VERSION = "aiweb-slice40e-connectedness-gate-runtime-v1"
SLICE40E_PROFILE_VERSION = "v1.0.0"
DIGEST_ALGORITHM = "sha256"


class ConnectednessAssertionKind(str, Enum):
    """The seven connection families named by the canonical Slice 40E plan."""

    SOURCE_SPAN = "source_span"
    STRUCTURAL_ANCESTRY = "structural_ancestry"
    SCOPE = "scope"
    ATTACHMENT = "attachment"
    OPERATOR_TRAIL = "operator_trail"
    PREDICATE_FRAME = "predicate_frame"
    CANDIDATE_LINEAGE = "candidate_lineage"


class ConnectednessAuthorityState(str, Enum):
    ADMITTED = "admitted"
    ABSENT = "absent"
    UNSUPPORTED = "unsupported"
    CONFLICTED = "conflicted"
    AMBIGUOUS = "ambiguous"


class ConnectednessJudgment(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    NOT_EVALUATED = "not_evaluated"


class ConnectednessFindingKind(str, Enum):
    CONNECTED_ASSERTION = "connected_assertion"
    DISCONNECTED_ASSERTION = "disconnected_assertion"
    AMBIGUOUS_ASSERTION = "ambiguous_assertion"
    UNSUPPORTED_ASSERTION = "unsupported_assertion"
    CONFLICTED_ASSERTION = "conflicted_assertion"
    INDETERMINATE_AUTHORITY_ABSENT = "indeterminate_authority_absent"
    ALL_ASSERTIONS_CONNECTED = "all_assertions_connected"


class ConnectednessOverallState(str, Enum):
    CONNECTED = "connectedness_connected"
    DISCONNECTED = "connectedness_disconnected"
    AMBIGUOUS = "connectedness_ambiguous"
    UNSUPPORTED = "connectedness_unsupported"
    CONFLICTED = "connectedness_conflicted"
    INDETERMINATE = "connectedness_indeterminate"


class ConnectednessValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    INVALID_SHA256 = "invalid_sha256"
    DUPLICATE_ID = "duplicate_id"
    REFERENCE_NOT_FOUND = "reference_not_found"
    CROSS_RECORD_MISMATCH = "cross_record_mismatch"
    CONNECTEDNESS_FAMILY_REQUIRED = "connectedness_family_required"
    SEALED_GOVERNANCE_REQUIRED = "sealed_governance_required"
    GOVERNANCE_INVALID = "governance_invalid"
    AUTHORITY_STATE_INVALID = "authority_state_invalid"
    JUDGMENT_INVALID = "judgment_invalid"
    COUNT_MISMATCH = "count_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    EXACT_CONNECTION_AUTHORITY_REQUIRED = "exact_connection_authority_required"
    CO_OCCURRENCE_AUTHORITY_PROHIBITED = "co_occurrence_authority_prohibited"
    INVENTED_TRANSITIVITY_PROHIBITED = "invented_transitivity_prohibited"
    REWRITE_PROHIBITED = "rewrite_prohibited"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"


@dataclass(frozen=True, slots=True)
class ConnectednessValidationIssue:
    path: str
    code: ConnectednessValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class ConnectednessValidationReport:
    issues: tuple[ConnectednessValidationIssue, ...]
    schema_version: str = SLICE40E_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class ConnectednessValidationError(ValueError):
    def __init__(self, report: ConnectednessValidationReport) -> None:
        self.report = report
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(detail or "Slice 40E connectedness validation failed")


@dataclass(frozen=True, slots=True)
class ConnectednessGateRuntimeProfile:
    profile_id: str
    profile_key: str
    profile_version: str
    gate_profile_ref: str
    gate_profile_version: str
    governing_authority_refs: tuple[str, ...]
    permitted_assertion_kinds: tuple[ConnectednessAssertionKind, ...]
    exact_admitted_connections_only: bool
    cooccurrence_connection_allowed: bool
    same_expression_connection_allowed: bool
    same_manifest_connection_allowed: bool
    implicit_transitivity_allowed: bool
    source_gap_bridge_allowed: bool
    ancestry_gap_bridge_allowed: bool
    scope_rewrite_allowed: bool
    attachment_reassignment_allowed: bool
    operator_trail_rewrite_allowed: bool
    predicate_frame_rewire_allowed: bool
    candidate_lineage_merge_allowed: bool
    raw_text_inspection_allowed: bool
    similarity_fallback_allowed: bool
    hidden_model_judgment_allowed: bool
    gate_composition_allowed: bool
    selected_meaning_allowed: bool
    route_tool_action_allowed: bool
    schema_version: str = SLICE40E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ConnectednessAssertion:
    assertion_id: str
    candidate_input_ref: str
    predicate_id: str
    predicate_version: str
    frame_id: str
    frame_version: str
    assertion_key: str
    assertion_kind: ConnectednessAssertionKind
    left_record_ref: str
    right_record_ref: str
    connection_basis_refs: tuple[str, ...]
    assertion_source_refs: tuple[str, ...]
    authority_refs: tuple[str, ...]
    exact_admitted_connection: bool
    same_expression_only: bool
    same_manifest_only: bool
    implicit_transitive_only: bool
    schema_version: str = SLICE40E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ConnectednessObservation:
    observation_id: str
    assertion_ref: str
    candidate_input_ref: str
    authority_state: ConnectednessAuthorityState
    connection_judgment: ConnectednessJudgment
    supporting_refs: tuple[str, ...]
    disconnection_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    schema_version: str = SLICE40E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ConnectednessEvaluationInput:
    evaluation_input_id: str
    governance_bundle: GateGovernanceBundle
    runtime_profile: ConnectednessGateRuntimeProfile
    candidate_input_ref: str
    predicate_id: str
    predicate_version: str
    frame_id: str
    frame_version: str
    assertions: tuple[ConnectednessAssertion, ...]
    observations: tuple[ConnectednessObservation, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    raw_text_supplied: bool
    cooccurrence_only_connection_used: bool
    same_expression_only_connection_used: bool
    same_manifest_only_connection_used: bool
    implicit_transitive_connection_used: bool
    source_gap_bridged: bool
    ancestry_gap_bridged: bool
    scope_rewritten: bool
    attachment_reassigned: bool
    operator_trail_rewritten: bool
    predicate_frame_rewired: bool
    candidate_lineage_merged: bool
    similarity_fallback_used: bool
    hidden_model_judgment_used: bool
    schema_version: str = SLICE40E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ConnectednessFinding:
    finding_id: str
    evaluation_input_ref: str
    assertion_ref: str | None
    finding_kind: ConnectednessFindingKind
    assertion_kind: ConnectednessAssertionKind | None
    authority_state: ConnectednessAuthorityState
    connection_judgment: ConnectednessJudgment
    supporting_refs: tuple[str, ...]
    disconnection_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    schema_version: str = SLICE40E_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ConnectednessGateResult:
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
    overall_state: ConnectednessOverallState
    findings: tuple[ConnectednessFinding, ...]
    assertion_count: int
    connected_count: int
    disconnected_count: int
    ambiguous_count: int
    unsupported_count: int
    conflicted_count: int
    indeterminate_count: int
    deterministic: bool
    exact_connection_authority_preserved: bool
    candidate_structure_mutated: bool
    cooccurrence_only_connection_used: bool
    same_expression_only_connection_used: bool
    same_manifest_only_connection_used: bool
    implicit_transitive_connection_used: bool
    source_gap_bridged: bool
    ancestry_gap_bridged: bool
    scope_rewritten: bool
    attachment_reassigned: bool
    operator_trail_rewritten: bool
    predicate_frame_rewired: bool
    candidate_lineage_merged: bool
    similarity_fallback_used: bool
    hidden_model_judgment_used: bool
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
    schema_version: str = SLICE40E_SCHEMA_VERSION
