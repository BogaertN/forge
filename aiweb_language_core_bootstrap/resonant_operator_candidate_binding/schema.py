"""Immutable Slice 36D resonant operator-candidate binding records.

These records preserve deterministic candidate associations between exact
Slice 36B source spans and inert Slice 36C symbolic grammar-operator
definitions. A candidate association is not an applied operator occurrence,
selected meaning, permission, capability route, memory operation, or action.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ..schema import stable_record_id

BINDING_SPEC_ID: Final[str] = "aiweb-resonant-operator-candidate-binding"
BINDING_SPEC_VERSION: Final[str] = (
    "aiweb-resonant-operator-candidate-binding-v1"
)
BINDING_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-resonant-operator-candidate-binding-v1"
)
BINDING_RULE_SCHEMA_ID: Final[str] = (
    "aiweb-resonant-operator-proposal-rule-v1"
)
BINDING_RULESET_SCHEMA_ID: Final[str] = (
    "aiweb-resonant-operator-proposal-ruleset-v1"
)
BINDING_CANDIDATE_SCHEMA_ID: Final[str] = (
    "aiweb-resonant-operator-binding-candidate-v1"
)
UNBOUND_SIGNAL_SCHEMA_ID: Final[str] = (
    "aiweb-unbound-structural-signal-v1"
)
BINDING_SET_SCHEMA_ID: Final[str] = (
    "aiweb-resonant-operator-candidate-binding-set-v1"
)
BINDING_RESULT_SCHEMA_ID: Final[str] = (
    "aiweb-resonant-operator-candidate-binding-result-v1"
)
BINDING_LIMITS_SCHEMA_ID: Final[str] = (
    "aiweb-resonant-operator-candidate-binding-limits-v1"
)

RMC_SECTION_39_AUTHORITY_REF: Final[str] = (
    "RMC Language Law v1 Section 39 Lawful Candidate Structural Analysis"
)
RMC_SECTION_39_NEGATION_AUTHORITY_REF: Final[str] = (
    "RMC Language Law v1 Section 39.17 Explicit Negation Signals"
)
RMC_SECTION_39_ACTION_AUTHORITY_REF: Final[str] = (
    "RMC Language Law v1 Section 39.23 Action-Like Signals"
)
RMC_SECTION_39_CANDIDATE_AUTHORITY_REF: Final[str] = (
    "RMC Language Law v1 Sections 39.25-39.31 Candidate Formation"
)
RMC_SECTION_39_MISSING_SUPPORT_AUTHORITY_REF: Final[str] = (
    "RMC Language Law v1 Sections 39.32-39.38 Missing Support"
)
RMC_SECTION_39_PLURALITY_AUTHORITY_REF: Final[str] = (
    "RMC Language Law v1 Sections 39.39-39.43 Candidate Plurality"
)
RMC_DOCUMENT_5_BOUNDARY_REF: Final[str] = (
    "RMC Predicate-Role Frame Registry v1 retains action-root and role authority"
)
SLICE36B_SOURCE_AUTHORITY_REF: Final[str] = (
    "Slice 36B deterministic source-field projection"
)
SLICE36C_REGISTRY_AUTHORITY_REF: Final[str] = (
    "Slice 36C symbolic grammar-operator registry"
)

DEFAULT_MAX_BINDING_CANDIDATES: Final[int] = 8_192
DEFAULT_MAX_UNBOUND_SIGNALS: Final[int] = 8_192
ABSOLUTE_MAX_BINDING_CANDIDATES: Final[int] = 32_768
ABSOLUTE_MAX_UNBOUND_SIGNALS: Final[int] = 32_768
EXPECTED_DEFAULT_RULE_COUNT: Final[int] = 15


class CandidateBindingStatus(str, Enum):
    CANDIDATE_BINDINGS_SUPPORTED = "CANDIDATE_BINDINGS_SUPPORTED"
    CANDIDATE_BINDINGS_PARTIALLY_UNSUPPORTED = (
        "CANDIDATE_BINDINGS_PARTIALLY_UNSUPPORTED"
    )
    CANDIDATE_BINDINGS_NONE = "CANDIDATE_BINDINGS_NONE"
    CANDIDATE_BINDINGS_MALFORMED_SOURCE = (
        "CANDIDATE_BINDINGS_MALFORMED_SOURCE"
    )
    CANDIDATE_BINDINGS_LIMIT_EXCEEDED = (
        "CANDIDATE_BINDINGS_LIMIT_EXCEEDED"
    )
    CANDIDATE_BINDINGS_FAILED = "CANDIDATE_BINDINGS_FAILED"


class ProposalRuleKind(str, Enum):
    EXACT_WHOLE_UNIT = "exact_whole_unit"
    EXACT_INITIAL_SEQUENCE = "exact_initial_sequence"
    EXACT_TERMINAL_MARK = "exact_terminal_mark"
    EXACT_QUOTATION_PAIR = "exact_quotation_pair"
    EXACT_UNMATCHED_QUOTATION_OPEN = (
        "exact_unmatched_quotation_open"
    )


class ProposalOutputKind(str, Enum):
    OPERATOR_CANDIDATE = "operator_candidate"
    UNBOUND_STRUCTURAL_SIGNAL = "unbound_structural_signal"


class SourcePositionPolicy(str, Enum):
    ANYWHERE = "anywhere"
    INITIAL_NON_WHITESPACE = "initial_non_whitespace"
    TERMINAL_NON_WHITESPACE = "terminal_non_whitespace"
    QUOTATION_PAIR = "quotation_pair"
    UNMATCHED_QUOTATION_OPEN = "unmatched_quotation_open"


class SourceEdgePolicy(str, Enum):
    NONE = "none"
    UNICODE_WORD_EDGE = "unicode_word_edge"


class DeterministicConfidenceBasis(str, Enum):
    EXACT_OBSERVABLE_RULE_MATCH = "exact_observable_rule_match"
    EXACT_OBSERVABLE_RULE_MATCH_HELD_BY_PARTIAL_SOURCE = (
        "exact_observable_rule_match_held_by_partial_source"
    )


class CandidateSupportStatus(str, Enum):
    SUPPORTED_EXACT_RULE_MATCH = "supported_exact_rule_match"
    HELD_PARTIALLY_UNSUPPORTED_SOURCE = (
        "held_partially_unsupported_source"
    )


class NeighborCompatibilityStatus(str, Enum):
    UNRESOLVED_NO_COMPATIBILITY_TABLE = (
        "unresolved_no_compatibility_table"
    )


class StructuralSignalKind(str, Enum):
    ACTION_LIKE = "action_like"


@dataclass(frozen=True, slots=True)
class CandidateBindingLimits:
    limits_id: str
    max_candidates: int
    max_unbound_signals: int
    binding_spec_id: str = BINDING_SPEC_ID
    binding_spec_version: str = BINDING_SPEC_VERSION
    schema_version: str = BINDING_SCHEMA_VERSION
    limits_schema_id: str = BINDING_LIMITS_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("limits_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "candidate_binding_limits",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ResonantOperatorProposalRule:
    rule_id: str
    rule_key: str
    rule_version: str
    rule_kind: ProposalRuleKind
    output_kind: ProposalOutputKind
    candidate_operator_key: str | None
    candidate_operator_version: str | None
    candidate_operator_definition_id: str | None
    candidate_variant_code: str
    competition_group_code: str
    exact_forms: tuple[str, ...]
    exact_sequences: tuple[tuple[str, ...], ...]
    quotation_pairs: tuple[tuple[str, str], ...]
    position_policy: SourcePositionPolicy
    edge_policy: SourceEdgePolicy
    required_projection_status_values: tuple[str, ...]
    observable_condition_codes: tuple[str, ...]
    satisfied_prerequisite_codes: tuple[str, ...]
    missing_prerequisite_codes: tuple[str, ...]
    conflicting_evidence_codes: tuple[str, ...]
    structural_signal_kind: StructuralSignalKind | None
    possible_parent_rule_keys: tuple[str, ...]
    possible_child_rule_keys: tuple[str, ...]
    enabled: bool
    exact_match_required: bool
    source_span_required: bool
    normalization_authorized: bool
    casefolding_authorized: bool
    tokenization_authorized: bool
    phrase_frequency_authorized: bool
    statistical_scoring_authorized: bool
    embedding_authorized: bool
    vector_similarity_authorized: bool
    nearest_neighbor_authorized: bool
    language_model_authorized: bool
    memory_resemblance_authorized: bool
    web_search_authorized: bool
    hidden_parser_authorized: bool
    capability_influence_authorized: bool
    source_authority_refs: tuple[str, ...]
    binding_spec_id: str = BINDING_SPEC_ID
    binding_spec_version: str = BINDING_SPEC_VERSION
    schema_version: str = BINDING_SCHEMA_VERSION
    rule_schema_id: str = BINDING_RULE_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("rule_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "resonant_operator_proposal_rule",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ResonantOperatorProposalRuleSet:
    ruleset_id: str
    ruleset_version: str
    grammar_registry_id: str
    grammar_registry_version: str
    rules: tuple[ResonantOperatorProposalRule, ...]
    exact_rule_count: int
    closed_world: bool
    deterministic_only: bool
    rule_order_selects_winner: bool
    automatic_activation_authorized: bool
    operator_application_authorized: bool
    phase_assignment_authorized: bool
    meaning_selection_authorized: bool
    permission_authorized: bool
    route_authorized: bool
    action_authorized: bool
    hidden_fallback_allowed: bool
    binding_spec_id: str = BINDING_SPEC_ID
    binding_spec_version: str = BINDING_SPEC_VERSION
    schema_version: str = BINDING_SCHEMA_VERSION
    ruleset_schema_id: str = BINDING_RULESET_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("ruleset_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "resonant_operator_proposal_ruleset",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ResonantOperatorBindingCandidate:
    candidate_binding_id: str
    binding_set_id: str
    source_event_id: str
    projection_id: str
    source_field_schema_id: str
    root_source_span_id: str
    predecessor_field_build_result_id: str
    predecessor_field_envelope_id: str | None
    source_span_ids: tuple[str, ...]
    code_point_ranges: tuple[tuple[int, int], ...]
    utf8_byte_ranges: tuple[tuple[int, int], ...]
    exact_source_fragments: tuple[str, ...]
    candidate_operator_key: str
    candidate_operator_version: str
    candidate_operator_definition_id: str
    candidate_operator_family: str
    candidate_operator_glyph: str | None
    advisory_phase_affinity: tuple[str, ...]
    grammar_registry_id: str
    grammar_registry_version: str
    proposal_ruleset_id: str
    proposal_ruleset_version: str
    proposal_rule_id: str
    proposal_rule_key: str
    proposal_rule_version: str
    candidate_variant_code: str
    competition_group_instance: str
    observable_condition_codes: tuple[str, ...]
    satisfied_prerequisite_codes: tuple[str, ...]
    missing_prerequisite_codes: tuple[str, ...]
    conflicting_evidence_codes: tuple[str, ...]
    neighboring_candidate_binding_ids: tuple[str, ...]
    compatible_neighboring_candidate_binding_ids: tuple[str, ...]
    incompatible_neighboring_candidate_binding_ids: tuple[str, ...]
    neighbor_compatibility_status: NeighborCompatibilityStatus
    competing_candidate_binding_ids: tuple[str, ...]
    possible_parent_binding_ids: tuple[str, ...]
    possible_child_binding_ids: tuple[str, ...]
    confidence_basis: DeterministicConfidenceBasis
    support_status: CandidateSupportStatus
    unresolved: bool
    unsupported: bool
    malformed: bool
    candidate_association_created: bool
    operator_occurrence_created: bool
    operator_application_performed: bool
    phase_assignment_performed: bool
    meaning_selected: bool
    permission_inferred: bool
    route_created: bool
    tool_routing_performed: bool
    action_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    delivery_performed: bool
    binding_spec_id: str = BINDING_SPEC_ID
    binding_spec_version: str = BINDING_SPEC_VERSION
    schema_version: str = BINDING_SCHEMA_VERSION
    candidate_schema_id: str = BINDING_CANDIDATE_SCHEMA_ID

    def identity_body(self) -> dict[str, object]:
        return {
            "binding_set_id": self.binding_set_id,
            "source_event_id": self.source_event_id,
            "projection_id": self.projection_id,
            "source_span_ids": self.source_span_ids,
            "candidate_operator_key": self.candidate_operator_key,
            "candidate_operator_version": self.candidate_operator_version,
            "candidate_operator_definition_id": (
                self.candidate_operator_definition_id
            ),
            "grammar_registry_id": self.grammar_registry_id,
            "grammar_registry_version": self.grammar_registry_version,
            "proposal_ruleset_id": self.proposal_ruleset_id,
            "proposal_ruleset_version": self.proposal_ruleset_version,
            "proposal_rule_id": self.proposal_rule_id,
            "proposal_rule_key": self.proposal_rule_key,
            "proposal_rule_version": self.proposal_rule_version,
            "candidate_variant_code": self.candidate_variant_code,
            "competition_group_instance": self.competition_group_instance,
            "binding_spec_id": self.binding_spec_id,
            "binding_spec_version": self.binding_spec_version,
            "schema_version": self.schema_version,
            "candidate_schema_id": self.candidate_schema_id,
        }

    def expected_id(self) -> str:
        return stable_record_id(
            "resonant_operator_binding_candidate",
            self.identity_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class UnboundStructuralSignal:
    signal_id: str
    binding_set_id: str
    source_event_id: str
    projection_id: str
    source_span_ids: tuple[str, ...]
    code_point_ranges: tuple[tuple[int, int], ...]
    utf8_byte_ranges: tuple[tuple[int, int], ...]
    exact_source_fragments: tuple[str, ...]
    signal_kind: StructuralSignalKind
    signal_code: str
    proposal_rule_id: str
    proposal_rule_key: str
    proposal_rule_version: str
    observable_condition_codes: tuple[str, ...]
    satisfied_prerequisite_codes: tuple[str, ...]
    missing_prerequisite_codes: tuple[str, ...]
    conflicting_evidence_codes: tuple[str, ...]
    unresolved: bool
    unsupported: bool
    malformed: bool
    operator_candidate_created: bool
    predicate_role_assigned: bool
    capability_binding_created: bool
    route_created: bool
    action_performed: bool
    binding_spec_id: str = BINDING_SPEC_ID
    binding_spec_version: str = BINDING_SPEC_VERSION
    schema_version: str = BINDING_SCHEMA_VERSION
    signal_schema_id: str = UNBOUND_SIGNAL_SCHEMA_ID

    def identity_body(self) -> dict[str, object]:
        return {
            "binding_set_id": self.binding_set_id,
            "source_event_id": self.source_event_id,
            "projection_id": self.projection_id,
            "source_span_ids": self.source_span_ids,
            "signal_kind": self.signal_kind,
            "signal_code": self.signal_code,
            "proposal_rule_id": self.proposal_rule_id,
            "proposal_rule_key": self.proposal_rule_key,
            "proposal_rule_version": self.proposal_rule_version,
            "binding_spec_id": self.binding_spec_id,
            "binding_spec_version": self.binding_spec_version,
            "schema_version": self.schema_version,
            "signal_schema_id": self.signal_schema_id,
        }

    def expected_id(self) -> str:
        return stable_record_id(
            "unbound_structural_signal",
            self.identity_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ResonantOperatorCandidateBindingSet:
    binding_set_id: str
    source_event_id: str
    source_sha256: str
    projection_id: str
    source_field_schema_id: str
    grammar_registry_id: str
    grammar_registry_version: str
    proposal_ruleset_id: str
    proposal_ruleset_version: str
    status: CandidateBindingStatus
    candidates: tuple[ResonantOperatorBindingCandidate, ...]
    unbound_structural_signals: tuple[UnboundStructuralSignal, ...]
    candidate_count: int
    unbound_signal_count: int
    materially_competing_candidate_count: int
    candidate_plurality_preserved: bool
    source_mapping_complete: bool
    source_ancestry_complete: bool
    structural_progression_allowed: bool
    candidate_binding_available: bool
    operator_occurrence_available: bool
    operator_application_available: bool
    phase_assignment_available: bool
    meaning_selection_available: bool
    permission_authority_available: bool
    route_authority_available: bool
    tool_authority_available: bool
    action_authority_available: bool
    memory_authority_available: bool
    delivery_authority_available: bool
    hidden_fallback_allowed: bool
    binding_spec_id: str = BINDING_SPEC_ID
    binding_spec_version: str = BINDING_SPEC_VERSION
    schema_version: str = BINDING_SCHEMA_VERSION
    binding_set_schema_id: str = BINDING_SET_SCHEMA_ID

    def identity_body(self) -> dict[str, object]:
        return {
            "source_event_id": self.source_event_id,
            "source_sha256": self.source_sha256,
            "projection_id": self.projection_id,
            "source_field_schema_id": self.source_field_schema_id,
            "grammar_registry_id": self.grammar_registry_id,
            "grammar_registry_version": self.grammar_registry_version,
            "proposal_ruleset_id": self.proposal_ruleset_id,
            "proposal_ruleset_version": self.proposal_ruleset_version,
            "binding_spec_id": self.binding_spec_id,
            "binding_spec_version": self.binding_spec_version,
            "schema_version": self.schema_version,
            "binding_set_schema_id": self.binding_set_schema_id,
        }

    def expected_id(self) -> str:
        return stable_record_id(
            "resonant_operator_candidate_binding_set",
            self.identity_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ResonantOperatorCandidateBindingResult:
    result_id: str
    status: CandidateBindingStatus
    reason_code: str
    binding_set_created: bool
    source_preserved_in_custody: bool
    source_event_id: str
    source_sha256: str
    projection_id: str
    grammar_registry_id: str
    proposal_ruleset_id: str
    limits: CandidateBindingLimits | None
    binding_set: ResonantOperatorCandidateBindingSet | None
    validation_issue_codes: tuple[str, ...]
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    environment_access_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    route_registration_performed: bool
    tool_routing_performed: bool
    operator_application_performed: bool
    phase_assignment_performed: bool
    meaning_selected: bool
    permission_inferred: bool
    action_performed: bool
    delivery_performed: bool
    binding_spec_id: str = BINDING_SPEC_ID
    binding_spec_version: str = BINDING_SPEC_VERSION
    schema_version: str = BINDING_SCHEMA_VERSION
    result_schema_id: str = BINDING_RESULT_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reason_code": self.reason_code,
            "binding_set_created": self.binding_set_created,
            "source_preserved_in_custody": self.source_preserved_in_custody,
            "source_event_id": self.source_event_id,
            "source_sha256": self.source_sha256,
            "projection_id": self.projection_id,
            "grammar_registry_id": self.grammar_registry_id,
            "proposal_ruleset_id": self.proposal_ruleset_id,
            "limits_id": self.limits.limits_id if self.limits else "",
            "binding_set_id": (
                self.binding_set.binding_set_id if self.binding_set else ""
            ),
            "validation_issue_codes": self.validation_issue_codes,
            "filesystem_read_performed": self.filesystem_read_performed,
            "filesystem_write_performed": self.filesystem_write_performed,
            "network_access_performed": self.network_access_performed,
            "environment_access_performed": self.environment_access_performed,
            "memory_read_performed": self.memory_read_performed,
            "memory_write_performed": self.memory_write_performed,
            "route_registration_performed": self.route_registration_performed,
            "tool_routing_performed": self.tool_routing_performed,
            "operator_application_performed": (
                self.operator_application_performed
            ),
            "phase_assignment_performed": self.phase_assignment_performed,
            "meaning_selected": self.meaning_selected,
            "permission_inferred": self.permission_inferred,
            "action_performed": self.action_performed,
            "delivery_performed": self.delivery_performed,
            "binding_spec_id": self.binding_spec_id,
            "binding_spec_version": self.binding_spec_version,
            "schema_version": self.schema_version,
            "result_schema_id": self.result_schema_id,
        }

    def expected_id(self) -> str:
        return stable_record_id(
            "resonant_operator_candidate_binding_result",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
