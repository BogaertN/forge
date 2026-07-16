"""Immutable Slice 36G structural-derivation records.

The records in this module are candidate-only. They preserve exact Slice
36A--36F ancestry and lawful non-progress without creating CandidateMeaning,
selected meaning, concept, predicate, truth, permission, capability, route,
tool, memory, action, rendering, delivery, or clarification authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum

from ..candidate_resonant_phase_trail import CandidateResonantPhaseTrail
from ..resonant_operator_candidate_binding import UnboundStructuralSignal
from ..scope_attachment_reference_constraints import (
    GovernedSpanCandidate,
    ReferenceAnalysis,
    ReferenceContextCandidate,
    ScopeAttachmentOccurrence,
)
from ..schema import stable_record_id


STRUCTURAL_DERIVATION_SPEC_ID = (
    "aiweb.slice36g.deterministic_structural_derivation"
)
STRUCTURAL_DERIVATION_SPEC_VERSION = "1.0.0"
STRUCTURAL_DERIVATION_SCHEMA_VERSION = "aiweb-slice36g-v1"

STRUCTURAL_POLICY_SCHEMA_ID = "aiweb.slice36g.structural_policy.v1"
STRUCTURAL_LIMITS_SCHEMA_ID = "aiweb.slice36g.structural_limits.v1"
STRUCTURAL_RULE_SCHEMA_ID = "aiweb.slice36g.structural_rule.v1"
STRUCTURAL_TRACE_SCHEMA_ID = "aiweb.slice36g.structural_trace.v1"
STRUCTURAL_NODE_SCHEMA_ID = "aiweb.slice36g.operator_node.v1"
STRUCTURAL_EDGE_SCHEMA_ID = "aiweb.slice36g.operator_edge.v1"
STRUCTURAL_GRAPH_SCHEMA_ID = "aiweb.slice36g.operator_graph.v1"
STRUCTURAL_COVERAGE_SCHEMA_ID = "aiweb.slice36g.source_coverage.v1"
STRUCTURAL_CANDIDATE_SCHEMA_ID = "aiweb.slice36g.structural_candidate.v1"
STRUCTURAL_NON_PROGRESS_SCHEMA_ID = "aiweb.slice36g.non_progress.v1"
STRUCTURAL_SET_SCHEMA_ID = "aiweb.slice36g.structural_set.v1"
STRUCTURAL_RESULT_SCHEMA_ID = "aiweb.slice36g.structural_result.v1"

DEFAULT_MAX_STRUCTURAL_CANDIDATES = 32768
DEFAULT_MAX_RULE_TRACES_PER_CANDIDATE = 65536
DEFAULT_MAX_GRAPH_NODES_PER_CANDIDATE = 32768
DEFAULT_MAX_GRAPH_EDGES_PER_CANDIDATE = 131072
DEFAULT_MAX_SOURCE_RANGES_PER_CANDIDATE = 262144

ABSOLUTE_MAX_STRUCTURAL_CANDIDATES = 262144
ABSOLUTE_MAX_RULE_TRACES_PER_CANDIDATE = 524288
ABSOLUTE_MAX_GRAPH_NODES_PER_CANDIDATE = 262144
ABSOLUTE_MAX_GRAPH_EDGES_PER_CANDIDATE = 1048576
ABSOLUTE_MAX_SOURCE_RANGES_PER_CANDIDATE = 1048576

CANONICAL_ROADMAP_AUTHORITY_REF = (
    "AI.Web Forge Canonical Production Roadmap v1.0:Slice36G"
)
RMC_LANGUAGE_LAW_AUTHORITY_REF = (
    "RMC Language Law v1:deterministic-structural-derivation"
)
SLICE36A_AUTHORITY_REF = "Slice36A:input-event-source-custody"
SLICE36B_AUTHORITY_REF = "Slice36B:deterministic-source-field-projection"
SLICE36C_AUTHORITY_REF = "Slice36C:symbolic-grammar-operator-registry"
SLICE36D_AUTHORITY_REF = "Slice36D:resonant-operator-candidate-binding"
SLICE36E_AUTHORITY_REF = "Slice36E:candidate-resonant-phase-trail"
SLICE36F_AUTHORITY_REF = "Slice36F:scope-attachment-reference-constraints"
SLICE39_AUTHORITY_REF = "Slice39:candidate-meaning-construction"
SLICE40_AUTHORITY_REF = "Slice40:gate-and-ambiguity-disposition"


class StructuralDerivationStatus(str, Enum):
    ZERO_STRUCTURAL_CANDIDATES = "ZERO_STRUCTURAL_CANDIDATES"
    ONE_STRUCTURAL_CANDIDATE = "ONE_STRUCTURAL_CANDIDATE"
    MULTIPLE_STRUCTURAL_CANDIDATES = "MULTIPLE_STRUCTURAL_CANDIDATES"
    STRUCTURAL_DERIVATION_LIMIT_EXCEEDED = (
        "STRUCTURAL_DERIVATION_LIMIT_EXCEEDED"
    )
    STRUCTURAL_DERIVATION_FAILED = "STRUCTURAL_DERIVATION_FAILED"


class StructuralCompletenessStatus(str, Enum):
    COMPLETE_BOUNDED_STRUCTURE = "complete_bounded_structure"
    AMBIGUOUS_BOUNDED_STRUCTURE = "ambiguous_bounded_structure"
    INCOMPLETE_BOUNDED_STRUCTURE = "incomplete_bounded_structure"
    MALFORMED_BOUNDED_STRUCTURE = "malformed_bounded_structure"
    UNSUPPORTED_BOUNDED_STRUCTURE = "unsupported_bounded_structure"
    DRIFT_CONTAINED_STRUCTURE = "drift_contained_structure"
    RECURSION_SUSPENDED_STRUCTURE = "recursion_suspended_structure"


class StructuralNonProgressReason(str, Enum):
    NONE = "NONE"
    UNRESOLVED_REFERENCE = "UNRESOLVED_REFERENCE"
    UNRESOLVED_OPERATOR_BINDING = "UNRESOLVED_OPERATOR_BINDING"
    UNSUPPORTED_SOURCE_STRUCTURE = "UNSUPPORTED_SOURCE_STRUCTURE"
    UNSUPPORTED_OPERATOR_SEQUENCE = "UNSUPPORTED_OPERATOR_SEQUENCE"
    MALFORMED_SOURCE_STRUCTURE = "MALFORMED_SOURCE_STRUCTURE"
    MULTIPLE_STRUCTURAL_CANDIDATES = "MULTIPLE_STRUCTURAL_CANDIDATES"
    CONFLICTING_PHASE_TRAILS = "CONFLICTING_PHASE_TRAILS"
    INCOMPLETE_INPUT = "INCOMPLETE_INPUT"
    INCOMPLETE_OPERATOR_TRAIL = "INCOMPLETE_OPERATOR_TRAIL"
    PROHIBITED_CONTEXT_DEPENDENCY = "PROHIBITED_CONTEXT_DEPENDENCY"
    DRIFT_CONTAINED = "DRIFT_CONTAINED"
    RECURSION_SUSPENDED = "RECURSION_SUSPENDED"
    NO_SUPPORTED_DERIVATION = "NO_SUPPORTED_DERIVATION"


class StructuralTraceLayer(str, Enum):
    SOURCE_CUSTODY = "source_custody"
    SOURCE_FIELD = "source_field"
    OPERATOR_BINDING = "operator_binding"
    PHASE_TRAIL = "phase_trail"
    SCOPE_ATTACHMENT = "scope_attachment"
    REFERENCE = "reference"
    SOURCE_COVERAGE = "source_coverage"
    SOURCE_RECONSTRUCTION = "source_reconstruction"
    STRUCTURAL_DERIVATION = "structural_derivation"
    NON_PROGRESS = "non_progress"


class StructuralTraceStatus(str, Enum):
    PRESERVED = "preserved"
    CANDIDATE_APPLIED = "candidate_applied"
    UNRESOLVED = "unresolved"
    UNSUPPORTED = "unsupported"
    MALFORMED = "malformed"
    CONTAINED = "contained"
    SUSPENDED = "suspended"


class StructuralEdgeKind(str, Enum):
    POSSIBLE_PARENT_CHILD = "possible_parent_child"
    APPLICATION_SEQUENCE = "application_sequence"
    COMPETING_CANDIDATES = "competing_candidates"


class StructuralCoverageStatus(str, Enum):
    COMPLETE_SOURCE_COVERAGE = "complete_source_coverage"
    PARTIAL_SOURCE_COVERAGE = "partial_source_coverage"
    NO_OPERATOR_DERIVATION_COVERAGE = "no_operator_derivation_coverage"


@dataclass(frozen=True, slots=True)
class StructuralDerivationPolicy:
    policy_id: str
    policy_version: str
    deterministic_only: bool
    exact_ancestry_required: bool
    source_reconstruction_required: bool
    preserve_all_structural_candidates: bool
    preserve_all_non_progress_reasons: bool
    preserve_scope_attachments: bool
    preserve_reference_candidates: bool
    hidden_fallback_allowed: bool
    candidate_meaning_authorized: bool
    selected_meaning_authorized: bool
    intended_meaning_selection_authorized: bool
    concept_resolution_authorized: bool
    sense_resolution_authorized: bool
    predicate_identity_authorized: bool
    participant_role_assignment_authorized: bool
    truth_determination_authorized: bool
    evidence_validity_determination_authorized: bool
    clarification_question_authorized: bool
    semantic_rejection_authorized: bool
    permission_inference_authorized: bool
    capability_selection_authorized: bool
    route_creation_authorized: bool
    tool_routing_authorized: bool
    action_execution_authorized: bool
    memory_read_authorized: bool
    memory_write_authorized: bool
    protected_memory_retrieval_authorized: bool
    outward_rendering_authorized: bool
    delivery_authorized: bool
    source_authority_refs: tuple[str, ...]
    structural_derivation_spec_id: str = STRUCTURAL_DERIVATION_SPEC_ID
    structural_derivation_spec_version: str = STRUCTURAL_DERIVATION_SPEC_VERSION
    schema_version: str = STRUCTURAL_DERIVATION_SCHEMA_VERSION
    policy_schema_id: str = STRUCTURAL_POLICY_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("policy_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("structural_derivation_policy", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StructuralDerivationLimits:
    limits_id: str
    max_structural_candidates: int
    max_rule_traces_per_candidate: int
    max_graph_nodes_per_candidate: int
    max_graph_edges_per_candidate: int
    max_source_ranges_per_candidate: int
    structural_derivation_spec_id: str = STRUCTURAL_DERIVATION_SPEC_ID
    structural_derivation_spec_version: str = STRUCTURAL_DERIVATION_SPEC_VERSION
    schema_version: str = STRUCTURAL_DERIVATION_SCHEMA_VERSION
    limits_schema_id: str = STRUCTURAL_LIMITS_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("limits_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("structural_derivation_limits", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StructuralDerivationRule:
    rule_id: str
    rule_key: str
    rule_version: str
    trace_layer: StructuralTraceLayer
    purpose_code: str
    exact_predecessor_record_required: bool
    creates_structural_candidate: bool
    creates_selected_meaning: bool
    asks_clarification_question: bool
    performs_semantic_rejection: bool
    source_authority_refs: tuple[str, ...]
    structural_derivation_spec_id: str = STRUCTURAL_DERIVATION_SPEC_ID
    structural_derivation_spec_version: str = STRUCTURAL_DERIVATION_SPEC_VERSION
    schema_version: str = STRUCTURAL_DERIVATION_SCHEMA_VERSION
    rule_schema_id: str = STRUCTURAL_RULE_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("rule_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("structural_derivation_rule", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StructuralRuleApplicationTrace:
    trace_id: str
    structural_candidate_id: str
    trace_ordinal: int
    trace_layer: StructuralTraceLayer
    trace_status: StructuralTraceStatus
    derivation_rule_id: str
    derivation_rule_key: str
    derivation_rule_version: str
    source_rule_ids: tuple[str, ...]
    source_rule_versions: tuple[str, ...]
    input_record_ids: tuple[str, ...]
    output_record_ids: tuple[str, ...]
    source_span_ids: tuple[str, ...]
    code_point_ranges: tuple[tuple[int, int], ...]
    reason_codes: tuple[str, ...]
    candidate_only: bool
    selected: bool
    semantic_authority: bool
    clarification_question_asked: bool
    semantic_rejection_performed: bool
    structural_derivation_spec_id: str = STRUCTURAL_DERIVATION_SPEC_ID
    structural_derivation_spec_version: str = STRUCTURAL_DERIVATION_SPEC_VERSION
    schema_version: str = STRUCTURAL_DERIVATION_SCHEMA_VERSION
    trace_schema_id: str = STRUCTURAL_TRACE_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("trace_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("structural_rule_application_trace", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StructuralOperatorNode:
    node_id: str
    structural_candidate_id: str
    candidate_binding_id: str
    candidate_operator_key: str
    candidate_operator_version: str
    candidate_operator_definition_id: str
    candidate_operator_family: str
    source_span_ids: tuple[str, ...]
    code_point_ranges: tuple[tuple[int, int], ...]
    utf8_byte_ranges: tuple[tuple[int, int], ...]
    exact_source_fragments: tuple[str, ...]
    phase_application_ids: tuple[str, ...]
    scope_occurrence_ids: tuple[str, ...]
    reference_analysis_ids: tuple[str, ...]
    possible_parent_binding_ids: tuple[str, ...]
    possible_child_binding_ids: tuple[str, ...]
    competing_binding_ids: tuple[str, ...]
    unresolved: bool
    unsupported: bool
    malformed: bool
    candidate_only: bool
    selected: bool
    concept_meaning_created: bool
    predicate_identity_created: bool
    structural_derivation_spec_id: str = STRUCTURAL_DERIVATION_SPEC_ID
    structural_derivation_spec_version: str = STRUCTURAL_DERIVATION_SPEC_VERSION
    schema_version: str = STRUCTURAL_DERIVATION_SCHEMA_VERSION
    node_schema_id: str = STRUCTURAL_NODE_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("node_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("structural_operator_node", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StructuralOperatorEdge:
    edge_id: str
    structural_candidate_id: str
    source_node_id: str
    target_node_id: str
    edge_kind: StructuralEdgeKind
    relationship_code: str
    evidence_record_ids: tuple[str, ...]
    candidate_only: bool
    selected: bool
    structural_derivation_spec_id: str = STRUCTURAL_DERIVATION_SPEC_ID
    structural_derivation_spec_version: str = STRUCTURAL_DERIVATION_SPEC_VERSION
    schema_version: str = STRUCTURAL_DERIVATION_SCHEMA_VERSION
    edge_schema_id: str = STRUCTURAL_EDGE_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("edge_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("structural_operator_edge", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StructuralOperatorGraph:
    graph_id: str
    structural_candidate_id: str
    nodes: tuple[StructuralOperatorNode, ...]
    edges: tuple[StructuralOperatorEdge, ...]
    node_count: int
    edge_count: int
    participating_binding_ids: tuple[str, ...]
    conflicting_binding_ids: tuple[str, ...]
    unresolved_binding_ids: tuple[str, ...]
    all_participating_bindings_represented: bool
    only_explicit_edges_created: bool
    candidate_only: bool
    selected_graph: bool
    structural_derivation_spec_id: str = STRUCTURAL_DERIVATION_SPEC_ID
    structural_derivation_spec_version: str = STRUCTURAL_DERIVATION_SPEC_VERSION
    schema_version: str = STRUCTURAL_DERIVATION_SCHEMA_VERSION
    graph_schema_id: str = STRUCTURAL_GRAPH_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("graph_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("structural_operator_graph", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StructuralSourceCoverageProof:
    coverage_proof_id: str
    structural_candidate_id: str
    source_event_id: str
    source_sha256: str
    projection_id: str
    source_code_point_length: int
    source_utf8_byte_length: int
    consumed_source_span_ids: tuple[str, ...]
    consumed_code_point_ranges: tuple[tuple[int, int], ...]
    consumed_utf8_byte_ranges: tuple[tuple[int, int], ...]
    unconsumed_source_span_ids: tuple[str, ...]
    unconsumed_code_point_ranges: tuple[tuple[int, int], ...]
    unconsumed_utf8_byte_ranges: tuple[tuple[int, int], ...]
    unconsumed_exact_fragments: tuple[str, ...]
    coverage_status: StructuralCoverageStatus
    source_coverage_complete: bool
    source_reconstruction_proven: bool
    reconstructed_source_sha256: str
    reconstruction_hash_matches_custody: bool
    exact_source_ancestry: bool
    structural_derivation_spec_id: str = STRUCTURAL_DERIVATION_SPEC_ID
    structural_derivation_spec_version: str = STRUCTURAL_DERIVATION_SPEC_VERSION
    schema_version: str = STRUCTURAL_DERIVATION_SCHEMA_VERSION
    coverage_schema_id: str = STRUCTURAL_COVERAGE_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("coverage_proof_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("structural_source_coverage", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StructuralAnalysisCandidate:
    structural_candidate_id: str
    structural_set_id: str
    source_event_id: str
    source_sha256: str
    custody_result_id: str
    input_event_id: str
    root_source_span_id: str
    projection_result_id: str
    projection_id: str
    binding_result_id: str
    binding_set_id: str
    phase_trail_result_id: str
    phase_trail_set_id: str
    constraint_result_id: str
    constraint_set_id: str
    constrained_trail_id: str
    phase_trail_id: str
    participating_binding_ids: tuple[str, ...]
    operator_graph: StructuralOperatorGraph
    phase_trail: CandidateResonantPhaseTrail
    rule_application_traces: tuple[StructuralRuleApplicationTrace, ...]
    source_coverage: StructuralSourceCoverageProof
    scope_occurrences: tuple[ScopeAttachmentOccurrence, ...]
    attachment_candidates: tuple[GovernedSpanCandidate, ...]
    reference_analyses: tuple[ReferenceAnalysis, ...]
    reference_candidates: tuple[ReferenceContextCandidate, ...]
    unbound_structural_signals: tuple[UnboundStructuralSignal, ...]
    unresolved_operator_span_ids: tuple[str, ...]
    conflicting_operator_binding_ids: tuple[str, ...]
    attachment_alternative_ids: tuple[str, ...]
    reference_alternative_ids: tuple[str, ...]
    incompleteness_reasons: tuple[str, ...]
    unsupported_reasons: tuple[str, ...]
    containment_reasons: tuple[str, ...]
    suspension_reasons: tuple[str, ...]
    non_progress_reasons: tuple[StructuralNonProgressReason, ...]
    completeness_status: StructuralCompletenessStatus
    structurally_complete: bool
    malformed: bool
    unsupported: bool
    ambiguous: bool
    incomplete: bool
    contained_drift: bool
    suspended_recursion: bool
    exact_ancestry_complete: bool
    source_reconstruction_proven: bool
    predecessor_records_preserved: bool
    candidate_only: bool
    selected_structure: bool
    candidate_meaning_created: bool
    selected_meaning: bool
    concept_resolved: bool
    sense_resolved: bool
    predicate_identity_created: bool
    participant_roles_assigned: bool
    truth_determined: bool
    evidence_validity_determined: bool
    clarification_question_asked: bool
    semantic_rejection_performed: bool
    permission_inferred: bool
    capability_selected: bool
    route_created: bool
    tool_routing_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    protected_memory_retrieved: bool
    action_performed: bool
    outward_answer_rendered: bool
    delivery_performed: bool
    structural_derivation_spec_id: str = STRUCTURAL_DERIVATION_SPEC_ID
    structural_derivation_spec_version: str = STRUCTURAL_DERIVATION_SPEC_VERSION
    schema_version: str = STRUCTURAL_DERIVATION_SCHEMA_VERSION
    candidate_schema_id: str = STRUCTURAL_CANDIDATE_SCHEMA_ID

    def identity_body(self) -> dict[str, object]:
        return {
            "structural_set_id": self.structural_set_id,
            "constrained_trail_id": self.constrained_trail_id,
            "phase_trail_id": self.phase_trail_id,
            "graph_id": self.operator_graph.graph_id,
            "coverage_proof_id": self.source_coverage.coverage_proof_id,
            "trace_ids": tuple(trace.trace_id for trace in self.rule_application_traces),
            "scope_occurrence_ids": tuple(item.occurrence_id for item in self.scope_occurrences),
            "attachment_candidate_ids": tuple(item.governed_span_id for item in self.attachment_candidates),
            "reference_analysis_ids": tuple(item.analysis_id for item in self.reference_analyses),
            "reference_candidate_ids": tuple(item.reference_candidate_id for item in self.reference_candidates),
            "unbound_signal_ids": tuple(item.signal_id for item in self.unbound_structural_signals),
            "non_progress_reasons": self.non_progress_reasons,
            "structural_derivation_spec_id": self.structural_derivation_spec_id,
            "structural_derivation_spec_version": self.structural_derivation_spec_version,
            "schema_version": self.schema_version,
            "candidate_schema_id": self.candidate_schema_id,
        }

    def expected_id(self) -> str:
        return stable_record_id(
            "structural_analysis_candidate_seed",
            {
                "structural_set_id": self.structural_set_id,
                "constrained_trail_id": self.constrained_trail_id,
                "phase_trail_id": self.phase_trail_id,
                "structural_derivation_spec_id": self.structural_derivation_spec_id,
                "structural_derivation_spec_version": self.structural_derivation_spec_version,
                "schema_version": self.schema_version,
            },
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StructuralNonProgressResult:
    non_progress_id: str
    structural_set_id: str
    source_event_id: str
    projection_id: str
    binding_set_id: str
    phase_trail_set_id: str
    constraint_set_id: str
    reasons: tuple[StructuralNonProgressReason, ...]
    primary_reason: StructuralNonProgressReason
    structural_candidate_ids: tuple[str, ...]
    blocking_record_ids: tuple[str, ...]
    unresolved_source_span_ids: tuple[str, ...]
    valid_result: bool
    guessed_to_avoid_non_progress: bool
    clarification_question_asked: bool
    semantic_rejection_performed: bool
    candidate_meaning_created: bool
    selected_meaning: bool
    structural_derivation_spec_id: str = STRUCTURAL_DERIVATION_SPEC_ID
    structural_derivation_spec_version: str = STRUCTURAL_DERIVATION_SPEC_VERSION
    schema_version: str = STRUCTURAL_DERIVATION_SCHEMA_VERSION
    non_progress_schema_id: str = STRUCTURAL_NON_PROGRESS_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("non_progress_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("structural_non_progress", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StructuralAnalysisCandidateSet:
    structural_set_id: str
    source_event_id: str
    source_sha256: str
    custody_result_id: str
    projection_result_id: str
    projection_id: str
    binding_result_id: str
    binding_set_id: str
    phase_trail_result_id: str
    phase_trail_set_id: str
    constraint_result_id: str
    constraint_set_id: str
    policy_id: str
    limits_id: str
    status: StructuralDerivationStatus
    candidates: tuple[StructuralAnalysisCandidate, ...]
    candidate_count: int
    complete_candidate_count: int
    ambiguous_candidate_count: int
    incomplete_candidate_count: int
    malformed_candidate_count: int
    unsupported_candidate_count: int
    contained_drift_candidate_count: int
    suspended_recursion_candidate_count: int
    aggregate_non_progress_reasons: tuple[StructuralNonProgressReason, ...]
    non_progress_result: StructuralNonProgressResult | None
    all_source_ancestry_preserved: bool
    all_source_reconstruction_proven: bool
    all_phase_trails_preserved: bool
    all_scope_occurrences_preserved: bool
    all_attachment_candidates_preserved: bool
    all_reference_candidates_preserved: bool
    structural_candidate_plurality_preserved: bool
    selected_structural_candidate_id: str | None
    candidate_meaning_created: bool
    selected_meaning: bool
    clarification_question_asked: bool
    semantic_rejection_performed: bool
    hidden_fallback_allowed: bool
    structural_derivation_spec_id: str = STRUCTURAL_DERIVATION_SPEC_ID
    structural_derivation_spec_version: str = STRUCTURAL_DERIVATION_SPEC_VERSION
    schema_version: str = STRUCTURAL_DERIVATION_SCHEMA_VERSION
    structural_set_schema_id: str = STRUCTURAL_SET_SCHEMA_ID

    def identity_body(self) -> dict[str, object]:
        return {
            "source_event_id": self.source_event_id,
            "source_sha256": self.source_sha256,
            "custody_result_id": self.custody_result_id,
            "projection_result_id": self.projection_result_id,
            "binding_result_id": self.binding_result_id,
            "phase_trail_result_id": self.phase_trail_result_id,
            "constraint_result_id": self.constraint_result_id,
            "policy_id": self.policy_id,
            "limits_id": self.limits_id,
            "structural_derivation_spec_id": self.structural_derivation_spec_id,
            "structural_derivation_spec_version": self.structural_derivation_spec_version,
            "schema_version": self.schema_version,
            "structural_set_schema_id": self.structural_set_schema_id,
        }

    def expected_id(self) -> str:
        return stable_record_id("structural_analysis_candidate_set", self.identity_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DeterministicStructuralDerivationResult:
    result_id: str
    status: StructuralDerivationStatus
    reason_code: str
    structural_set_created: bool
    explicit_non_progress_created: bool
    source_preserved_in_custody: bool
    source_event_id: str
    source_sha256: str
    projection_id: str
    binding_set_id: str
    phase_trail_set_id: str
    constraint_set_id: str
    policy: StructuralDerivationPolicy | None
    limits: StructuralDerivationLimits | None
    structural_set: StructuralAnalysisCandidateSet | None
    validation_issue_codes: tuple[str, ...]
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    repository_history_search_performed: bool
    network_access_performed: bool
    environment_access_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    protected_memory_retrieval_performed: bool
    web_search_performed: bool
    embedding_performed: bool
    language_model_used: bool
    similarity_search_performed: bool
    candidate_meaning_created: bool
    selected_meaning: bool
    intended_meaning_selected: bool
    concept_resolved: bool
    sense_resolved: bool
    predicate_identity_created: bool
    participant_roles_assigned: bool
    truth_determined: bool
    evidence_validity_determined: bool
    clarification_question_asked: bool
    semantic_rejection_performed: bool
    permission_inferred: bool
    capability_selected: bool
    route_registration_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    outward_answer_rendered: bool
    delivery_performed: bool
    structural_derivation_spec_id: str = STRUCTURAL_DERIVATION_SPEC_ID
    structural_derivation_spec_version: str = STRUCTURAL_DERIVATION_SPEC_VERSION
    schema_version: str = STRUCTURAL_DERIVATION_SCHEMA_VERSION
    result_schema_id: str = STRUCTURAL_RESULT_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reason_code": self.reason_code,
            "structural_set_created": self.structural_set_created,
            "explicit_non_progress_created": self.explicit_non_progress_created,
            "source_preserved_in_custody": self.source_preserved_in_custody,
            "source_event_id": self.source_event_id,
            "source_sha256": self.source_sha256,
            "projection_id": self.projection_id,
            "binding_set_id": self.binding_set_id,
            "phase_trail_set_id": self.phase_trail_set_id,
            "constraint_set_id": self.constraint_set_id,
            "policy_id": self.policy.policy_id if self.policy else "",
            "limits_id": self.limits.limits_id if self.limits else "",
            "structural_set_id": self.structural_set.structural_set_id if self.structural_set else "",
            "validation_issue_codes": self.validation_issue_codes,
            "filesystem_read_performed": self.filesystem_read_performed,
            "filesystem_write_performed": self.filesystem_write_performed,
            "repository_history_search_performed": self.repository_history_search_performed,
            "network_access_performed": self.network_access_performed,
            "environment_access_performed": self.environment_access_performed,
            "memory_read_performed": self.memory_read_performed,
            "memory_write_performed": self.memory_write_performed,
            "protected_memory_retrieval_performed": self.protected_memory_retrieval_performed,
            "web_search_performed": self.web_search_performed,
            "embedding_performed": self.embedding_performed,
            "language_model_used": self.language_model_used,
            "similarity_search_performed": self.similarity_search_performed,
            "candidate_meaning_created": self.candidate_meaning_created,
            "selected_meaning": self.selected_meaning,
            "intended_meaning_selected": self.intended_meaning_selected,
            "concept_resolved": self.concept_resolved,
            "sense_resolved": self.sense_resolved,
            "predicate_identity_created": self.predicate_identity_created,
            "participant_roles_assigned": self.participant_roles_assigned,
            "truth_determined": self.truth_determined,
            "evidence_validity_determined": self.evidence_validity_determined,
            "clarification_question_asked": self.clarification_question_asked,
            "semantic_rejection_performed": self.semantic_rejection_performed,
            "permission_inferred": self.permission_inferred,
            "capability_selected": self.capability_selected,
            "route_registration_performed": self.route_registration_performed,
            "tool_routing_performed": self.tool_routing_performed,
            "action_performed": self.action_performed,
            "outward_answer_rendered": self.outward_answer_rendered,
            "delivery_performed": self.delivery_performed,
            "structural_derivation_spec_id": self.structural_derivation_spec_id,
            "structural_derivation_spec_version": self.structural_derivation_spec_version,
            "schema_version": self.schema_version,
            "result_schema_id": self.result_schema_id,
        }

    def expected_id(self) -> str:
        return stable_record_id("deterministic_structural_derivation_result", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
