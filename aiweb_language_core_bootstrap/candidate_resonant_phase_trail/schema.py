"""Immutable Slice 36E candidate resonant phase-trail records.

The records in this module preserve candidate structural transformations only.
They do not select a trail, select meaning, infer permission, activate an RSOC
core operator, route a capability, read or write memory, or perform an action.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ..schema import stable_record_id
from ..symbolic_grammar_operator_registry import GrammarOperatorEffect

PHASE_TRAIL_SPEC_ID: Final[str] = "aiweb-candidate-resonant-phase-trail"
PHASE_TRAIL_SPEC_VERSION: Final[str] = "aiweb-candidate-resonant-phase-trail-v1"
PHASE_TRAIL_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-candidate-resonant-phase-trail-v1"
)
PHASE_TRAIL_POLICY_SCHEMA_ID: Final[str] = (
    "aiweb-candidate-resonant-phase-trail-policy-v1"
)
PHASE_TRAIL_LIMITS_SCHEMA_ID: Final[str] = (
    "aiweb-candidate-resonant-phase-trail-limits-v1"
)
SYMBOLIC_FIELD_STATE_SCHEMA_ID: Final[str] = (
    "aiweb-candidate-symbolic-field-state-v1"
)
CANDIDATE_APPLICATION_SCHEMA_ID: Final[str] = (
    "aiweb-candidate-grammar-operator-application-v1"
)
PHASE_TRAIL_SCHEMA_ID: Final[str] = "aiweb-candidate-resonant-phase-trail-v1"
PHASE_TRAIL_SET_SCHEMA_ID: Final[str] = (
    "aiweb-candidate-resonant-phase-trail-set-v1"
)
PHASE_TRAIL_RESULT_SCHEMA_ID: Final[str] = (
    "aiweb-candidate-resonant-phase-trail-result-v1"
)

DEFAULT_MAX_PHASE_TRAILS: Final[int] = 16_384
DEFAULT_MAX_APPLICATIONS_PER_TRAIL: Final[int] = 32
ABSOLUTE_MAX_PHASE_TRAILS: Final[int] = 65_536
ABSOLUTE_MAX_APPLICATIONS_PER_TRAIL: Final[int] = 256

CANONICAL_ROADMAP_AUTHORITY_REF: Final[str] = (
    "AI.Web Forge Canonical Production Roadmap Slice 36E"
)
FBSC_VOLUME_II_AUTHORITY_REF: Final[str] = (
    "Frequency-Based Symbolic Calculus Volume II phase-bearing grammar operators"
)
RSOC_AUTHORITY_REF: Final[str] = (
    "Resonant Symbolic Operator Calculus pure successor-state discipline"
)
SLICE36B_AUTHORITY_REF: Final[str] = (
    "Slice 36B deterministic source-field projection"
)
SLICE36C_AUTHORITY_REF: Final[str] = (
    "Slice 36C symbolic grammar-operator registry"
)
SLICE36D_AUTHORITY_REF: Final[str] = (
    "Slice 36D resonant operator candidate binding"
)


class PhaseTrailConstructionStatus(str, Enum):
    ZERO_PHASE_TRAILS = "ZERO_PHASE_TRAILS"
    ONE_PHASE_TRAIL = "ONE_PHASE_TRAIL"
    MULTIPLE_PHASE_TRAILS = "MULTIPLE_PHASE_TRAILS"
    CONFLICTING_PHASE_TRAILS = "CONFLICTING_PHASE_TRAILS"
    INCOMPLETE_PHASE_TRAIL = "INCOMPLETE_PHASE_TRAIL"
    MALFORMED_PHASE_TRAIL = "MALFORMED_PHASE_TRAIL"
    UNSUPPORTED_OPERATOR_SEQUENCE = "UNSUPPORTED_OPERATOR_SEQUENCE"
    DRIFT_CONTAINED = "DRIFT_CONTAINED"
    RECURSION_SUSPENDED = "RECURSION_SUSPENDED"
    PHASE_TRAIL_LIMIT_EXCEEDED = "PHASE_TRAIL_LIMIT_EXCEEDED"
    PHASE_TRAIL_CONSTRUCTION_FAILED = "PHASE_TRAIL_CONSTRUCTION_FAILED"


class CandidatePhaseStatus(str, Enum):
    UNASSIGNED_INITIAL_STATE = "unassigned_initial_state"
    EXPLICIT_ADVISORY_CANDIDATE = "explicit_advisory_candidate"
    UNRESOLVED_NO_AUTHORIZED_AFFINITY = (
        "unresolved_no_authorized_affinity"
    )
    PRESERVED_PREDECESSOR_CANDIDATE = "preserved_predecessor_candidate"


class CandidateApplicationStatus(str, Enum):
    SUCCESSOR_CREATED = "successor_created"
    SUCCESSOR_CONTAINED = "successor_contained"
    SUCCESSOR_SUSPENDED = "successor_suspended"
    SUCCESSOR_REJECTED = "successor_rejected"
    DRIFT_CONTAINED = "drift_contained"


class PhaseTrailCompletionStatus(str, Enum):
    OPEN_UNRESOLVED = "open_unresolved"
    SEALED_UNPROVEN = "sealed_unproven"
    COMPLETE_CANDIDATE = "complete_candidate"
    CONTAINED_PRESERVED = "contained_preserved"
    SUSPENDED_PRESERVED = "suspended_preserved"
    REJECTED_NON_PROGRESS = "rejected_non_progress"


class PhaseTrailNonProgressReason(str, Enum):
    NONE = "none"
    NO_OPERATOR_CANDIDATES = "no_operator_candidates"
    SOURCE_PROGRESSION_HELD = "source_progression_held"
    NO_AUTHORIZED_OPERATOR_EFFECT = "no_authorized_operator_effect"
    COMPATIBILITY_OR_COMMUTATION_NOT_INSTALLED = (
        "compatibility_or_commutation_not_installed"
    )
    OPERATOR_EFFECT_REJECTED_PROGRESSION = (
        "operator_effect_rejected_progression"
    )
    OPERATOR_EFFECT_SUSPENDED_PROGRESSION = (
        "operator_effect_suspended_progression"
    )
    OPERATOR_EFFECT_CONTAINED_PROGRESSION = (
        "operator_effect_contained_progression"
    )
    PHASE_TRANSITION_LAW_NOT_INSTALLED = (
        "phase_transition_law_not_installed"
    )
    TRAIL_LIMIT_EXCEEDED = "trail_limit_exceeded"
    MALFORMED_INPUT = "malformed_input"


@dataclass(frozen=True, slots=True)
class PhaseTrailConstructionPolicy:
    policy_id: str
    policy_version: str
    single_binding_trails_required: bool
    explicit_parent_child_trails_allowed: bool
    arbitrary_neighbor_composition_allowed: bool
    competing_candidates_may_coapply: bool
    branch_every_allowed_effect: bool
    branch_every_explicit_phase_affinity: bool
    fixed_phase_sequence_required: bool
    advisory_phase_affinity_only: bool
    immutable_successor_required: bool
    prior_state_mutation_allowed: bool
    core_rsoc_operator_application_authorized: bool
    numeric_entropy_effect_authorized: bool
    automatic_trail_selection_authorized: bool
    meaning_selection_authorized: bool
    permission_authorized: bool
    route_authorized: bool
    tool_authorized: bool
    memory_authorized: bool
    action_authorized: bool
    delivery_authorized: bool
    source_authority_refs: tuple[str, ...]
    phase_trail_spec_id: str = PHASE_TRAIL_SPEC_ID
    phase_trail_spec_version: str = PHASE_TRAIL_SPEC_VERSION
    schema_version: str = PHASE_TRAIL_SCHEMA_VERSION
    policy_schema_id: str = PHASE_TRAIL_POLICY_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("policy_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("phase_trail_construction_policy", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PhaseTrailConstructionLimits:
    limits_id: str
    max_trails: int
    max_applications_per_trail: int
    phase_trail_spec_id: str = PHASE_TRAIL_SPEC_ID
    phase_trail_spec_version: str = PHASE_TRAIL_SPEC_VERSION
    schema_version: str = PHASE_TRAIL_SCHEMA_VERSION
    limits_schema_id: str = PHASE_TRAIL_LIMITS_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("limits_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("phase_trail_construction_limits", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CandidateSymbolicFieldState:
    state_id: str
    phase_trail_id: str
    phase_trail_set_id: str
    source_event_id: str
    source_sha256: str
    projection_id: str
    source_field_schema_id: str
    binding_set_id: str
    initial_state_id: str
    predecessor_state_id: str | None
    predecessor_application_id: str | None
    state_ordinal: int
    identity_field_id: str
    identity_field_preserved: bool
    participating_binding_ids: tuple[str, ...]
    applied_binding_ids: tuple[str, ...]
    preserved_source_span_ids: tuple[str, ...]
    candidate_phase_status: CandidatePhaseStatus
    candidate_phase_values: tuple[str, ...]
    phase_ancestry: tuple[tuple[str, ...], ...]
    recursive_depth: int
    active_constraint_codes: tuple[str, ...]
    unresolved_branch_ids: tuple[str, ...]
    conflict_branch_ids: tuple[str, ...]
    suspended_branch_ids: tuple[str, ...]
    containment_condition_codes: tuple[str, ...]
    drift_indicator_codes: tuple[str, ...]
    entropy_effect_codes: tuple[str, ...]
    completion_status: PhaseTrailCompletionStatus
    structural_progression_allowed: bool
    contained: bool
    suspended: bool
    sealed: bool
    rejected: bool
    prior_state_mutated: bool
    core_rsoc_operator_application_count: int
    selected_meaning: bool
    permission_inferred: bool
    route_created: bool
    tool_routing_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    action_performed: bool
    delivery_performed: bool
    phase_trail_spec_id: str = PHASE_TRAIL_SPEC_ID
    phase_trail_spec_version: str = PHASE_TRAIL_SPEC_VERSION
    schema_version: str = PHASE_TRAIL_SCHEMA_VERSION
    state_schema_id: str = SYMBOLIC_FIELD_STATE_SCHEMA_ID

    def identity_body(self) -> dict[str, object]:
        return {
            "phase_trail_id": self.phase_trail_id,
            "phase_trail_set_id": self.phase_trail_set_id,
            "source_event_id": self.source_event_id,
            "projection_id": self.projection_id,
            "binding_set_id": self.binding_set_id,
            "predecessor_state_id": self.predecessor_state_id,
            "predecessor_application_id": self.predecessor_application_id,
            "state_ordinal": self.state_ordinal,
            "identity_field_id": self.identity_field_id,
            "participating_binding_ids": self.participating_binding_ids,
            "applied_binding_ids": self.applied_binding_ids,
            "preserved_source_span_ids": self.preserved_source_span_ids,
            "candidate_phase_status": self.candidate_phase_status,
            "candidate_phase_values": self.candidate_phase_values,
            "phase_ancestry": self.phase_ancestry,
            "recursive_depth": self.recursive_depth,
            "active_constraint_codes": self.active_constraint_codes,
            "unresolved_branch_ids": self.unresolved_branch_ids,
            "conflict_branch_ids": self.conflict_branch_ids,
            "suspended_branch_ids": self.suspended_branch_ids,
            "containment_condition_codes": self.containment_condition_codes,
            "drift_indicator_codes": self.drift_indicator_codes,
            "entropy_effect_codes": self.entropy_effect_codes,
            "completion_status": self.completion_status,
            "structural_progression_allowed": self.structural_progression_allowed,
            "contained": self.contained,
            "suspended": self.suspended,
            "sealed": self.sealed,
            "rejected": self.rejected,
            "phase_trail_spec_id": self.phase_trail_spec_id,
            "phase_trail_spec_version": self.phase_trail_spec_version,
            "schema_version": self.schema_version,
            "state_schema_id": self.state_schema_id,
        }

    def expected_id(self) -> str:
        return stable_record_id("candidate_symbolic_field_state", self.identity_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CandidateGrammarOperatorApplication:
    application_id: str
    phase_trail_id: str
    phase_trail_set_id: str
    source_event_id: str
    projection_id: str
    binding_set_id: str
    application_ordinal: int
    candidate_binding_id: str
    candidate_operator_key: str
    candidate_operator_version: str
    candidate_operator_definition_id: str
    candidate_operator_family: str
    candidate_operator_glyph: str | None
    structural_effect: GrammarOperatorEffect
    input_state_id: str
    successor_state_id: str
    phase_before_status: CandidatePhaseStatus
    phase_before_values: tuple[str, ...]
    phase_after_status: CandidatePhaseStatus
    phase_after_values: tuple[str, ...]
    phase_transition_code: str
    source_span_ids: tuple[str, ...]
    transformation_ancestry_state_ids: tuple[str, ...]
    identity_field_id_before: str
    identity_field_id_after: str
    identity_field_preserved: bool
    source_spans_preserved: bool
    recursive_depth_before: int
    recursive_depth_after: int
    unresolved_branch_ids: tuple[str, ...]
    conflict_branch_ids: tuple[str, ...]
    suspended_branch_ids: tuple[str, ...]
    containment_condition_codes: tuple[str, ...]
    drift_indicator_codes: tuple[str, ...]
    entropy_effect_code: str
    application_status: CandidateApplicationStatus
    successor_created: bool
    prior_state_mutated: bool
    core_rsoc_operator_key: str | None
    core_rsoc_operator_applied: bool
    selected_phase: bool
    selected_meaning: bool
    permission_inferred: bool
    route_created: bool
    tool_routing_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    action_performed: bool
    delivery_performed: bool
    phase_trail_spec_id: str = PHASE_TRAIL_SPEC_ID
    phase_trail_spec_version: str = PHASE_TRAIL_SPEC_VERSION
    schema_version: str = PHASE_TRAIL_SCHEMA_VERSION
    application_schema_id: str = CANDIDATE_APPLICATION_SCHEMA_ID

    def identity_body(self) -> dict[str, object]:
        return {
            "phase_trail_id": self.phase_trail_id,
            "phase_trail_set_id": self.phase_trail_set_id,
            "application_ordinal": self.application_ordinal,
            "candidate_binding_id": self.candidate_binding_id,
            "candidate_operator_key": self.candidate_operator_key,
            "candidate_operator_version": self.candidate_operator_version,
            "candidate_operator_definition_id": self.candidate_operator_definition_id,
            "structural_effect": self.structural_effect,
            "input_state_id": self.input_state_id,
            "phase_before_status": self.phase_before_status,
            "phase_before_values": self.phase_before_values,
            "phase_after_status": self.phase_after_status,
            "phase_after_values": self.phase_after_values,
            "phase_transition_code": self.phase_transition_code,
            "source_span_ids": self.source_span_ids,
            "phase_trail_spec_id": self.phase_trail_spec_id,
            "phase_trail_spec_version": self.phase_trail_spec_version,
            "schema_version": self.schema_version,
            "application_schema_id": self.application_schema_id,
        }

    def expected_id(self) -> str:
        return stable_record_id("candidate_grammar_operator_application", self.identity_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CandidateResonantPhaseTrail:
    phase_trail_id: str
    phase_trail_set_id: str
    source_event_id: str
    source_sha256: str
    projection_id: str
    source_field_schema_id: str
    binding_set_id: str
    grammar_registry_id: str
    grammar_registry_version: str
    policy_id: str
    participating_binding_ids: tuple[str, ...]
    planned_effect_codes: tuple[str, ...]
    planned_phase_affinity_values: tuple[str, ...]
    initial_state_id: str
    states: tuple[CandidateSymbolicFieldState, ...]
    applications: tuple[CandidateGrammarOperatorApplication, ...]
    final_state_id: str
    unresolved_branch_ids: tuple[str, ...]
    conflict_branch_ids: tuple[str, ...]
    suspended_branch_ids: tuple[str, ...]
    containment_condition_codes: tuple[str, ...]
    drift_indicator_codes: tuple[str, ...]
    entropy_effect_codes: tuple[str, ...]
    completion_status: PhaseTrailCompletionStatus
    non_progress_reason: PhaseTrailNonProgressReason
    recursive_depth: int
    immutable_transition_chain_complete: bool
    source_ancestry_complete: bool
    identity_field_preserved: bool
    source_spans_preserved: bool
    candidate_only: bool
    selected_trail: bool
    core_rsoc_operator_applications: int
    selected_meaning: bool
    permission_inferred: bool
    route_created: bool
    tool_routing_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    action_performed: bool
    delivery_performed: bool
    phase_trail_spec_id: str = PHASE_TRAIL_SPEC_ID
    phase_trail_spec_version: str = PHASE_TRAIL_SPEC_VERSION
    schema_version: str = PHASE_TRAIL_SCHEMA_VERSION
    phase_trail_schema_id: str = PHASE_TRAIL_SCHEMA_ID

    def identity_body(self) -> dict[str, object]:
        return {
            "phase_trail_set_id": self.phase_trail_set_id,
            "source_event_id": self.source_event_id,
            "projection_id": self.projection_id,
            "binding_set_id": self.binding_set_id,
            "grammar_registry_id": self.grammar_registry_id,
            "grammar_registry_version": self.grammar_registry_version,
            "policy_id": self.policy_id,
            "participating_binding_ids": self.participating_binding_ids,
            "planned_effect_codes": self.planned_effect_codes,
            "planned_phase_affinity_values": self.planned_phase_affinity_values,
            "phase_trail_spec_id": self.phase_trail_spec_id,
            "phase_trail_spec_version": self.phase_trail_spec_version,
            "schema_version": self.schema_version,
            "phase_trail_schema_id": self.phase_trail_schema_id,
        }

    def expected_id(self) -> str:
        return stable_record_id("candidate_resonant_phase_trail", self.identity_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CandidateResonantPhaseTrailSet:
    phase_trail_set_id: str
    source_event_id: str
    source_sha256: str
    projection_id: str
    source_field_schema_id: str
    binding_set_id: str
    grammar_registry_id: str
    grammar_registry_version: str
    policy_id: str
    limits_id: str
    status: PhaseTrailConstructionStatus
    trails: tuple[CandidateResonantPhaseTrail, ...]
    trail_count: int
    complete_trail_count: int
    incomplete_trail_count: int
    conflicting_trail_count: int
    contained_trail_count: int
    suspended_trail_count: int
    rejected_trail_count: int
    unresolved_branch_count: int
    conflict_branch_count: int
    candidate_plurality_preserved: bool
    immutable_successor_law_enforced: bool
    fixed_phase_sequence_forced: bool
    arbitrary_neighbor_composition_performed: bool
    selected_trail_id: str | None
    selected_meaning: bool
    permission_authority_available: bool
    route_authority_available: bool
    tool_authority_available: bool
    memory_authority_available: bool
    action_authority_available: bool
    delivery_authority_available: bool
    hidden_fallback_allowed: bool
    phase_trail_spec_id: str = PHASE_TRAIL_SPEC_ID
    phase_trail_spec_version: str = PHASE_TRAIL_SPEC_VERSION
    schema_version: str = PHASE_TRAIL_SCHEMA_VERSION
    phase_trail_set_schema_id: str = PHASE_TRAIL_SET_SCHEMA_ID

    def identity_body(self) -> dict[str, object]:
        return {
            "source_event_id": self.source_event_id,
            "source_sha256": self.source_sha256,
            "projection_id": self.projection_id,
            "source_field_schema_id": self.source_field_schema_id,
            "binding_set_id": self.binding_set_id,
            "grammar_registry_id": self.grammar_registry_id,
            "grammar_registry_version": self.grammar_registry_version,
            "policy_id": self.policy_id,
            "limits_id": self.limits_id,
            "phase_trail_spec_id": self.phase_trail_spec_id,
            "phase_trail_spec_version": self.phase_trail_spec_version,
            "schema_version": self.schema_version,
            "phase_trail_set_schema_id": self.phase_trail_set_schema_id,
        }

    def expected_id(self) -> str:
        return stable_record_id("candidate_resonant_phase_trail_set", self.identity_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CandidateResonantPhaseTrailResult:
    result_id: str
    status: PhaseTrailConstructionStatus
    reason_code: str
    phase_trail_set_created: bool
    source_preserved_in_custody: bool
    source_event_id: str
    source_sha256: str
    projection_id: str
    binding_set_id: str
    grammar_registry_id: str
    policy: PhaseTrailConstructionPolicy | None
    limits: PhaseTrailConstructionLimits | None
    phase_trail_set: CandidateResonantPhaseTrailSet | None
    validation_issue_codes: tuple[str, ...]
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    environment_access_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    route_registration_performed: bool
    tool_routing_performed: bool
    core_rsoc_operator_application_performed: bool
    selected_trail: bool
    selected_phase: bool
    selected_meaning: bool
    permission_inferred: bool
    action_performed: bool
    delivery_performed: bool
    phase_trail_spec_id: str = PHASE_TRAIL_SPEC_ID
    phase_trail_spec_version: str = PHASE_TRAIL_SPEC_VERSION
    schema_version: str = PHASE_TRAIL_SCHEMA_VERSION
    result_schema_id: str = PHASE_TRAIL_RESULT_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reason_code": self.reason_code,
            "phase_trail_set_created": self.phase_trail_set_created,
            "source_preserved_in_custody": self.source_preserved_in_custody,
            "source_event_id": self.source_event_id,
            "source_sha256": self.source_sha256,
            "projection_id": self.projection_id,
            "binding_set_id": self.binding_set_id,
            "grammar_registry_id": self.grammar_registry_id,
            "policy_id": self.policy.policy_id if self.policy else "",
            "limits_id": self.limits.limits_id if self.limits else "",
            "phase_trail_set_id": (
                self.phase_trail_set.phase_trail_set_id
                if self.phase_trail_set else ""
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
            "core_rsoc_operator_application_performed": (
                self.core_rsoc_operator_application_performed
            ),
            "selected_trail": self.selected_trail,
            "selected_phase": self.selected_phase,
            "selected_meaning": self.selected_meaning,
            "permission_inferred": self.permission_inferred,
            "action_performed": self.action_performed,
            "delivery_performed": self.delivery_performed,
            "phase_trail_spec_id": self.phase_trail_spec_id,
            "phase_trail_spec_version": self.phase_trail_spec_version,
            "schema_version": self.schema_version,
            "result_schema_id": self.result_schema_id,
        }

    def expected_id(self) -> str:
        return stable_record_id("candidate_resonant_phase_trail_result", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
