"""Deterministic Slice 36E candidate phase-trail construction.

Construction is closed over validated Slice 36D candidates and the inert Slice
36C registry. It enumerates candidates; it never selects a winner. Arbitrary
neighboring candidates are not composed because no compatibility or
commutation table is installed. Only reciprocal parent/child links explicitly
preserved by Slice 36D may form a multi-application trail.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Final

from ..resonant_operator_candidate_binding import (
    CandidateBindingStatus,
    ResonantOperatorBindingCandidate,
    ResonantOperatorCandidateBindingResult,
    build_default_resonant_operator_proposal_ruleset,
    validate_resonant_operator_candidate_binding_result,
)
from ..schema import stable_record_id
from ..source_field_projection import (
    SourceFieldProjectionResult,
    validate_source_field_projection_result,
)
from ..symbolic_grammar_operator_registry import (
    GrammarOperatorDefinition,
    GrammarOperatorEffect,
    GrammarOperatorPhaseAffinityStatus,
    SymbolicGrammarOperatorRegistry,
    build_default_symbolic_grammar_operator_registry,
    grammar_operator_for_key,
    validate_symbolic_grammar_operator_registry,
)
from .schema import (
    ABSOLUTE_MAX_APPLICATIONS_PER_TRAIL,
    ABSOLUTE_MAX_PHASE_TRAILS,
    CANONICAL_ROADMAP_AUTHORITY_REF,
    DEFAULT_MAX_APPLICATIONS_PER_TRAIL,
    DEFAULT_MAX_PHASE_TRAILS,
    FBSC_VOLUME_II_AUTHORITY_REF,
    PHASE_TRAIL_LIMITS_SCHEMA_ID,
    PHASE_TRAIL_POLICY_SCHEMA_ID,
    PHASE_TRAIL_RESULT_SCHEMA_ID,
    PHASE_TRAIL_SCHEMA_ID,
    PHASE_TRAIL_SCHEMA_VERSION,
    PHASE_TRAIL_SET_SCHEMA_ID,
    PHASE_TRAIL_SPEC_ID,
    PHASE_TRAIL_SPEC_VERSION,
    RSOC_AUTHORITY_REF,
    SLICE36B_AUTHORITY_REF,
    SLICE36C_AUTHORITY_REF,
    SLICE36D_AUTHORITY_REF,
    CandidateGrammarOperatorApplication,
    CandidateResonantPhaseTrail,
    CandidateResonantPhaseTrailResult,
    CandidateResonantPhaseTrailSet,
    CandidateSymbolicFieldState,
    PhaseTrailCompletionStatus,
    PhaseTrailConstructionLimits,
    PhaseTrailConstructionPolicy,
    PhaseTrailConstructionStatus,
    PhaseTrailNonProgressReason,
)
from .transition import (
    apply_candidate_grammar_operator,
    build_initial_candidate_symbolic_state,
)

_POLICY_VERSION: Final[str] = "1.0.0"
_DEFAULT_SENTINEL = object()


@dataclass(frozen=True, slots=True)
class _PlannedApplication:
    candidate: ResonantOperatorBindingCandidate
    definition: GrammarOperatorDefinition
    effect: GrammarOperatorEffect
    phase_affinity: str | None

    def key(self) -> tuple[str, str, str]:
        return (
            self.candidate.candidate_binding_id,
            self.effect.value,
            self.phase_affinity or "",
        )


def build_default_phase_trail_policy() -> PhaseTrailConstructionPolicy:
    body = {
        "policy_version": _POLICY_VERSION,
        "single_binding_trails_required": True,
        "explicit_parent_child_trails_allowed": True,
        "arbitrary_neighbor_composition_allowed": False,
        "competing_candidates_may_coapply": False,
        "branch_every_allowed_effect": True,
        "branch_every_explicit_phase_affinity": True,
        "fixed_phase_sequence_required": False,
        "advisory_phase_affinity_only": True,
        "immutable_successor_required": True,
        "prior_state_mutation_allowed": False,
        "core_rsoc_operator_application_authorized": False,
        "numeric_entropy_effect_authorized": False,
        "automatic_trail_selection_authorized": False,
        "meaning_selection_authorized": False,
        "permission_authorized": False,
        "route_authorized": False,
        "tool_authorized": False,
        "memory_authorized": False,
        "action_authorized": False,
        "delivery_authorized": False,
        "source_authority_refs": (
            CANONICAL_ROADMAP_AUTHORITY_REF,
            FBSC_VOLUME_II_AUTHORITY_REF,
            RSOC_AUTHORITY_REF,
            SLICE36B_AUTHORITY_REF,
            SLICE36C_AUTHORITY_REF,
            SLICE36D_AUTHORITY_REF,
        ),
        "phase_trail_spec_id": PHASE_TRAIL_SPEC_ID,
        "phase_trail_spec_version": PHASE_TRAIL_SPEC_VERSION,
        "schema_version": PHASE_TRAIL_SCHEMA_VERSION,
        "policy_schema_id": PHASE_TRAIL_POLICY_SCHEMA_ID,
    }
    return PhaseTrailConstructionPolicy(
        policy_id=stable_record_id("phase_trail_construction_policy", body),
        **body,
    )


def build_phase_trail_limits(
    *,
    max_trails: int = DEFAULT_MAX_PHASE_TRAILS,
    max_applications_per_trail: int = DEFAULT_MAX_APPLICATIONS_PER_TRAIL,
) -> PhaseTrailConstructionLimits:
    body = {
        "max_trails": max_trails,
        "max_applications_per_trail": max_applications_per_trail,
        "phase_trail_spec_id": PHASE_TRAIL_SPEC_ID,
        "phase_trail_spec_version": PHASE_TRAIL_SPEC_VERSION,
        "schema_version": PHASE_TRAIL_SCHEMA_VERSION,
        "limits_schema_id": PHASE_TRAIL_LIMITS_SCHEMA_ID,
    }
    return PhaseTrailConstructionLimits(
        limits_id=stable_record_id("phase_trail_construction_limits", body),
        **body,
    )


def default_phase_trail_limits() -> PhaseTrailConstructionLimits:
    return build_phase_trail_limits()


def _policy_issues(policy: object) -> tuple[str, ...]:
    if type(policy) is not PhaseTrailConstructionPolicy:
        return ("invalid_phase_trail_policy_type",)
    issues: list[str] = []
    if policy.policy_id != policy.expected_id():
        issues.append("phase_trail_policy_id_mismatch")
    required_true = (
        "single_binding_trails_required",
        "explicit_parent_child_trails_allowed",
        "branch_every_allowed_effect",
        "branch_every_explicit_phase_affinity",
        "advisory_phase_affinity_only",
        "immutable_successor_required",
    )
    required_false = (
        "arbitrary_neighbor_composition_allowed",
        "competing_candidates_may_coapply",
        "fixed_phase_sequence_required",
        "prior_state_mutation_allowed",
        "core_rsoc_operator_application_authorized",
        "numeric_entropy_effect_authorized",
        "automatic_trail_selection_authorized",
        "meaning_selection_authorized",
        "permission_authorized",
        "route_authorized",
        "tool_authorized",
        "memory_authorized",
        "action_authorized",
        "delivery_authorized",
    )
    for name in required_true:
        if getattr(policy, name, None) is not True:
            issues.append(f"phase_trail_policy_{name}_must_be_true")
    for name in required_false:
        if getattr(policy, name, None) is not False:
            issues.append(f"phase_trail_policy_{name}_must_be_false")
    return tuple(issues)


def _limits_issues(limits: object) -> tuple[str, ...]:
    if type(limits) is not PhaseTrailConstructionLimits:
        return ("invalid_phase_trail_limits_type",)
    issues: list[str] = []
    if limits.limits_id != limits.expected_id():
        issues.append("phase_trail_limits_id_mismatch")
    if type(limits.max_trails) is not int or not (
        0 <= limits.max_trails <= ABSOLUTE_MAX_PHASE_TRAILS
    ):
        issues.append("invalid_max_phase_trails")
    if type(limits.max_applications_per_trail) is not int or not (
        1 <= limits.max_applications_per_trail
        <= ABSOLUTE_MAX_APPLICATIONS_PER_TRAIL
    ):
        issues.append("invalid_max_applications_per_trail")
    return tuple(issues)


def _result(
    *,
    status: PhaseTrailConstructionStatus,
    reason_code: str,
    phase_trail_set_created: bool,
    source_preserved_in_custody: bool,
    source_event_id: str,
    source_sha256: str,
    projection_id: str,
    binding_set_id: str,
    grammar_registry_id: str,
    policy: PhaseTrailConstructionPolicy | None,
    limits: PhaseTrailConstructionLimits | None,
    phase_trail_set: CandidateResonantPhaseTrailSet | None,
    validation_issue_codes: tuple[str, ...],
) -> CandidateResonantPhaseTrailResult:
    body = {
        "status": status,
        "reason_code": reason_code,
        "phase_trail_set_created": phase_trail_set_created,
        "source_preserved_in_custody": source_preserved_in_custody,
        "source_event_id": source_event_id,
        "source_sha256": source_sha256,
        "projection_id": projection_id,
        "binding_set_id": binding_set_id,
        "grammar_registry_id": grammar_registry_id,
        "policy_id": policy.policy_id if policy else "",
        "limits_id": limits.limits_id if limits else "",
        "phase_trail_set_id": (
            phase_trail_set.phase_trail_set_id if phase_trail_set else ""
        ),
        "validation_issue_codes": validation_issue_codes,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "network_access_performed": False,
        "environment_access_performed": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "route_registration_performed": False,
        "tool_routing_performed": False,
        "core_rsoc_operator_application_performed": False,
        "selected_trail": False,
        "selected_phase": False,
        "selected_meaning": False,
        "permission_inferred": False,
        "action_performed": False,
        "delivery_performed": False,
        "phase_trail_spec_id": PHASE_TRAIL_SPEC_ID,
        "phase_trail_spec_version": PHASE_TRAIL_SPEC_VERSION,
        "schema_version": PHASE_TRAIL_SCHEMA_VERSION,
        "result_schema_id": PHASE_TRAIL_RESULT_SCHEMA_ID,
    }
    return CandidateResonantPhaseTrailResult(
        result_id=stable_record_id("candidate_resonant_phase_trail_result", body),
        status=status,
        reason_code=reason_code,
        phase_trail_set_created=phase_trail_set_created,
        source_preserved_in_custody=source_preserved_in_custody,
        source_event_id=source_event_id,
        source_sha256=source_sha256,
        projection_id=projection_id,
        binding_set_id=binding_set_id,
        grammar_registry_id=grammar_registry_id,
        policy=policy,
        limits=limits,
        phase_trail_set=phase_trail_set,
        validation_issue_codes=validation_issue_codes,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        environment_access_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        route_registration_performed=False,
        tool_routing_performed=False,
        core_rsoc_operator_application_performed=False,
        selected_trail=False,
        selected_phase=False,
        selected_meaning=False,
        permission_inferred=False,
        action_performed=False,
        delivery_performed=False,
    )


def _phase_branches(definition: GrammarOperatorDefinition) -> tuple[str | None, ...]:
    if (
        definition.phase_affinity_status
        is GrammarOperatorPhaseAffinityStatus.EXPLICIT_ADVISORY_ONLY
        and definition.phase_affinity
    ):
        return tuple(definition.phase_affinity)
    return (None,)


def _candidate_options(
    candidate: ResonantOperatorBindingCandidate,
    registry: SymbolicGrammarOperatorRegistry,
) -> tuple[_PlannedApplication, ...]:
    definition = grammar_operator_for_key(candidate.candidate_operator_key, registry)
    if definition is None:
        return ()
    return tuple(
        _PlannedApplication(candidate, definition, effect, phase)
        for effect, phase in product(
            definition.allowed_effects,
            _phase_branches(definition),
        )
    )


def _build_plans(
    candidates: tuple[ResonantOperatorBindingCandidate, ...],
    registry: SymbolicGrammarOperatorRegistry,
) -> tuple[tuple[_PlannedApplication, ...], ...] | None:
    by_id = {candidate.candidate_binding_id: candidate for candidate in candidates}
    options = {
        candidate.candidate_binding_id: _candidate_options(candidate, registry)
        for candidate in candidates
    }
    if any(not value for value in options.values()):
        return None

    plans: dict[tuple[tuple[str, str, str], ...], tuple[_PlannedApplication, ...]] = {}

    # Every candidate remains independently visible.
    for candidate in candidates:
        for option in options[candidate.candidate_binding_id]:
            plans[(option.key(),)] = (option,)

    # Only reciprocal parent/child links are composable in Slice 36E.
    for parent in candidates:
        for child_id in sorted(parent.possible_child_binding_ids):
            child = by_id.get(child_id)
            if child is None:
                return None
            if parent.candidate_binding_id not in child.possible_parent_binding_ids:
                return None
            if child_id in parent.competing_candidate_binding_ids:
                continue
            for parent_option, child_option in product(
                options[parent.candidate_binding_id],
                options[child_id],
            ):
                plan = (parent_option, child_option)
                plans[tuple(item.key() for item in plan)] = plan

    return tuple(plans[key] for key in sorted(plans))


def _trail_set_identity(
    *,
    source_event_id: str,
    source_sha256: str,
    projection_id: str,
    source_field_schema_id: str,
    binding_set_id: str,
    grammar_registry_id: str,
    grammar_registry_version: str,
    policy_id: str,
    limits_id: str,
) -> dict[str, object]:
    return {
        "source_event_id": source_event_id,
        "source_sha256": source_sha256,
        "projection_id": projection_id,
        "source_field_schema_id": source_field_schema_id,
        "binding_set_id": binding_set_id,
        "grammar_registry_id": grammar_registry_id,
        "grammar_registry_version": grammar_registry_version,
        "policy_id": policy_id,
        "limits_id": limits_id,
        "phase_trail_spec_id": PHASE_TRAIL_SPEC_ID,
        "phase_trail_spec_version": PHASE_TRAIL_SPEC_VERSION,
        "schema_version": PHASE_TRAIL_SCHEMA_VERSION,
        "phase_trail_set_schema_id": PHASE_TRAIL_SET_SCHEMA_ID,
    }


def _empty_set(
    *,
    status: PhaseTrailConstructionStatus,
    binding_result: ResonantOperatorCandidateBindingResult,
    registry: SymbolicGrammarOperatorRegistry,
    policy: PhaseTrailConstructionPolicy,
    limits: PhaseTrailConstructionLimits,
) -> CandidateResonantPhaseTrailSet:
    binding_set = binding_result.binding_set
    assert binding_set is not None
    identity = _trail_set_identity(
        source_event_id=binding_set.source_event_id,
        source_sha256=binding_set.source_sha256,
        projection_id=binding_set.projection_id,
        source_field_schema_id=binding_set.source_field_schema_id,
        binding_set_id=binding_set.binding_set_id,
        grammar_registry_id=registry.registry_id,
        grammar_registry_version=registry.registry_version,
        policy_id=policy.policy_id,
        limits_id=limits.limits_id,
    )
    return CandidateResonantPhaseTrailSet(
        phase_trail_set_id=stable_record_id(
            "candidate_resonant_phase_trail_set", identity
        ),
        source_event_id=binding_set.source_event_id,
        source_sha256=binding_set.source_sha256,
        projection_id=binding_set.projection_id,
        source_field_schema_id=binding_set.source_field_schema_id,
        binding_set_id=binding_set.binding_set_id,
        grammar_registry_id=registry.registry_id,
        grammar_registry_version=registry.registry_version,
        policy_id=policy.policy_id,
        limits_id=limits.limits_id,
        status=status,
        trails=(),
        trail_count=0,
        complete_trail_count=0,
        incomplete_trail_count=0,
        conflicting_trail_count=0,
        contained_trail_count=0,
        suspended_trail_count=0,
        rejected_trail_count=0,
        unresolved_branch_count=0,
        conflict_branch_count=0,
        candidate_plurality_preserved=True,
        immutable_successor_law_enforced=True,
        fixed_phase_sequence_forced=False,
        arbitrary_neighbor_composition_performed=False,
        selected_trail_id=None,
        selected_meaning=False,
        permission_authority_available=False,
        route_authority_available=False,
        tool_authority_available=False,
        memory_authority_available=False,
        action_authority_available=False,
        delivery_authority_available=False,
        hidden_fallback_allowed=False,
    )


def _source_spans(plan: tuple[_PlannedApplication, ...]) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            span_id
            for item in plan
            for span_id in item.candidate.source_span_ids
        )
    )


def _initial_unresolved(plan: tuple[_PlannedApplication, ...]) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            code
            for item in plan
            for code in item.candidate.missing_prerequisite_codes
        )
    )


def _initial_conflicts(plan: tuple[_PlannedApplication, ...]) -> tuple[str, ...]:
    participating = {item.candidate.candidate_binding_id for item in plan}
    return tuple(
        dict.fromkeys(
            value
            for item in plan
            for value in (
                *item.candidate.competing_candidate_binding_ids,
                *item.candidate.conflicting_evidence_codes,
            )
            if value not in participating
        )
    )


def _non_progress_reason(
    final_state: CandidateSymbolicFieldState,
    applications: tuple[CandidateGrammarOperatorApplication, ...],
) -> PhaseTrailNonProgressReason:
    if final_state.rejected:
        return PhaseTrailNonProgressReason.OPERATOR_EFFECT_REJECTED_PROGRESSION
    if final_state.suspended:
        return PhaseTrailNonProgressReason.OPERATOR_EFFECT_SUSPENDED_PROGRESSION
    if final_state.contained:
        if any(
            application.application_status.value == "drift_contained"
            for application in applications
        ):
            return PhaseTrailNonProgressReason.PHASE_TRANSITION_LAW_NOT_INSTALLED
        return PhaseTrailNonProgressReason.OPERATOR_EFFECT_CONTAINED_PROGRESSION
    if final_state.sealed and final_state.completion_status is not (
        PhaseTrailCompletionStatus.COMPLETE_CANDIDATE
    ):
        return PhaseTrailNonProgressReason.PHASE_TRANSITION_LAW_NOT_INSTALLED
    if final_state.unresolved_branch_ids:
        return PhaseTrailNonProgressReason.COMPATIBILITY_OR_COMMUTATION_NOT_INSTALLED
    return PhaseTrailNonProgressReason.NONE


def _build_trail(
    *,
    plan: tuple[_PlannedApplication, ...],
    phase_trail_set_id: str,
    binding_result: ResonantOperatorCandidateBindingResult,
    registry: SymbolicGrammarOperatorRegistry,
    policy: PhaseTrailConstructionPolicy,
) -> CandidateResonantPhaseTrail:
    binding_set = binding_result.binding_set
    assert binding_set is not None

    participating = tuple(item.candidate.candidate_binding_id for item in plan)
    effect_codes = tuple(item.effect.value for item in plan)
    phase_values = tuple(item.phase_affinity or "" for item in plan)
    trail_identity = {
        "phase_trail_set_id": phase_trail_set_id,
        "source_event_id": binding_set.source_event_id,
        "projection_id": binding_set.projection_id,
        "binding_set_id": binding_set.binding_set_id,
        "grammar_registry_id": registry.registry_id,
        "grammar_registry_version": registry.registry_version,
        "policy_id": policy.policy_id,
        "participating_binding_ids": participating,
        "planned_effect_codes": effect_codes,
        "planned_phase_affinity_values": phase_values,
        "phase_trail_spec_id": PHASE_TRAIL_SPEC_ID,
        "phase_trail_spec_version": PHASE_TRAIL_SPEC_VERSION,
        "schema_version": PHASE_TRAIL_SCHEMA_VERSION,
        "phase_trail_schema_id": PHASE_TRAIL_SCHEMA_ID,
    }
    phase_trail_id = stable_record_id(
        "candidate_resonant_phase_trail", trail_identity
    )
    identity_field_id = stable_record_id(
        "candidate_symbolic_identity_field",
        {
            "source_event_id": binding_set.source_event_id,
            "projection_id": binding_set.projection_id,
            "binding_set_id": binding_set.binding_set_id,
            "participating_binding_ids": participating,
            "phase_trail_spec_version": PHASE_TRAIL_SPEC_VERSION,
        },
    )
    initial = build_initial_candidate_symbolic_state(
        phase_trail_id=phase_trail_id,
        phase_trail_set_id=phase_trail_set_id,
        source_event_id=binding_set.source_event_id,
        source_sha256=binding_set.source_sha256,
        projection_id=binding_set.projection_id,
        source_field_schema_id=binding_set.source_field_schema_id,
        binding_set_id=binding_set.binding_set_id,
        identity_field_id=identity_field_id,
        participating_binding_ids=participating,
        preserved_source_span_ids=_source_spans(plan),
        unresolved_branch_ids=_initial_unresolved(plan),
        conflict_branch_ids=_initial_conflicts(plan),
    )

    states: list[CandidateSymbolicFieldState] = [initial]
    applications: list[CandidateGrammarOperatorApplication] = []
    current = initial
    for index, item in enumerate(plan):
        if not current.structural_progression_allowed:
            break
        remaining = tuple(
            later.candidate.candidate_binding_id
            for later in plan[index + 1 :]
        )
        application, successor = apply_candidate_grammar_operator(
            current_state=current,
            candidate=item.candidate,
            definition=item.definition,
            structural_effect=item.effect,
            phase_affinity=item.phase_affinity,
            remaining_binding_ids=remaining,
        )
        applications.append(application)
        states.append(successor)
        current = successor

    applications_tuple = tuple(applications)
    states_tuple = tuple(states)
    return CandidateResonantPhaseTrail(
        phase_trail_id=phase_trail_id,
        phase_trail_set_id=phase_trail_set_id,
        source_event_id=binding_set.source_event_id,
        source_sha256=binding_set.source_sha256,
        projection_id=binding_set.projection_id,
        source_field_schema_id=binding_set.source_field_schema_id,
        binding_set_id=binding_set.binding_set_id,
        grammar_registry_id=registry.registry_id,
        grammar_registry_version=registry.registry_version,
        policy_id=policy.policy_id,
        participating_binding_ids=participating,
        planned_effect_codes=effect_codes,
        planned_phase_affinity_values=phase_values,
        initial_state_id=initial.state_id,
        states=states_tuple,
        applications=applications_tuple,
        final_state_id=current.state_id,
        unresolved_branch_ids=current.unresolved_branch_ids,
        conflict_branch_ids=current.conflict_branch_ids,
        suspended_branch_ids=current.suspended_branch_ids,
        containment_condition_codes=current.containment_condition_codes,
        drift_indicator_codes=current.drift_indicator_codes,
        entropy_effect_codes=current.entropy_effect_codes,
        completion_status=current.completion_status,
        non_progress_reason=_non_progress_reason(current, applications_tuple),
        recursive_depth=current.recursive_depth,
        immutable_transition_chain_complete=(
            len(states_tuple) == len(applications_tuple) + 1
        ),
        source_ancestry_complete=True,
        identity_field_preserved=all(
            state.identity_field_id == identity_field_id
            and state.identity_field_preserved
            for state in states_tuple
        ),
        source_spans_preserved=all(
            state.preserved_source_span_ids == initial.preserved_source_span_ids
            for state in states_tuple
        ),
        candidate_only=True,
        selected_trail=False,
        core_rsoc_operator_applications=0,
        selected_meaning=False,
        permission_inferred=False,
        route_created=False,
        tool_routing_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        action_performed=False,
        delivery_performed=False,
    )


def _has_material_candidate_conflict(
    trail: CandidateResonantPhaseTrail,
) -> bool:
    return any(
        value.startswith("resonant_operator_binding_candidate:")
        for value in trail.conflict_branch_ids
    )


def _status_for_trails(
    trails: tuple[CandidateResonantPhaseTrail, ...],
) -> PhaseTrailConstructionStatus:
    if not trails:
        return PhaseTrailConstructionStatus.ZERO_PHASE_TRAILS
    if any(_has_material_candidate_conflict(trail) for trail in trails):
        return PhaseTrailConstructionStatus.CONFLICTING_PHASE_TRAILS
    if len(trails) > 1:
        return PhaseTrailConstructionStatus.MULTIPLE_PHASE_TRAILS
    trail = trails[0]
    if trail.completion_status is PhaseTrailCompletionStatus.COMPLETE_CANDIDATE:
        return PhaseTrailConstructionStatus.ONE_PHASE_TRAIL
    if trail.completion_status is PhaseTrailCompletionStatus.SUSPENDED_PRESERVED:
        return PhaseTrailConstructionStatus.RECURSION_SUSPENDED
    if (
        trail.completion_status is PhaseTrailCompletionStatus.CONTAINED_PRESERVED
        and any(
            application.application_status.value == "drift_contained"
            for application in trail.applications
        )
    ):
        return PhaseTrailConstructionStatus.DRIFT_CONTAINED
    return PhaseTrailConstructionStatus.INCOMPLETE_PHASE_TRAIL


def _make_set(
    *,
    trails: tuple[CandidateResonantPhaseTrail, ...],
    status: PhaseTrailConstructionStatus,
    binding_result: ResonantOperatorCandidateBindingResult,
    registry: SymbolicGrammarOperatorRegistry,
    policy: PhaseTrailConstructionPolicy,
    limits: PhaseTrailConstructionLimits,
) -> CandidateResonantPhaseTrailSet:
    binding_set = binding_result.binding_set
    assert binding_set is not None
    identity = _trail_set_identity(
        source_event_id=binding_set.source_event_id,
        source_sha256=binding_set.source_sha256,
        projection_id=binding_set.projection_id,
        source_field_schema_id=binding_set.source_field_schema_id,
        binding_set_id=binding_set.binding_set_id,
        grammar_registry_id=registry.registry_id,
        grammar_registry_version=registry.registry_version,
        policy_id=policy.policy_id,
        limits_id=limits.limits_id,
    )
    unresolved_ids = {
        value for trail in trails for value in trail.unresolved_branch_ids
    }
    conflict_ids = {
        value for trail in trails for value in trail.conflict_branch_ids
    }
    return CandidateResonantPhaseTrailSet(
        phase_trail_set_id=stable_record_id(
            "candidate_resonant_phase_trail_set", identity
        ),
        source_event_id=binding_set.source_event_id,
        source_sha256=binding_set.source_sha256,
        projection_id=binding_set.projection_id,
        source_field_schema_id=binding_set.source_field_schema_id,
        binding_set_id=binding_set.binding_set_id,
        grammar_registry_id=registry.registry_id,
        grammar_registry_version=registry.registry_version,
        policy_id=policy.policy_id,
        limits_id=limits.limits_id,
        status=status,
        trails=trails,
        trail_count=len(trails),
        complete_trail_count=sum(
            trail.completion_status is PhaseTrailCompletionStatus.COMPLETE_CANDIDATE
            for trail in trails
        ),
        incomplete_trail_count=sum(
            trail.completion_status
            in {
                PhaseTrailCompletionStatus.OPEN_UNRESOLVED,
                PhaseTrailCompletionStatus.SEALED_UNPROVEN,
            }
            for trail in trails
        ),
        conflicting_trail_count=sum(bool(trail.conflict_branch_ids) for trail in trails),
        contained_trail_count=sum(
            trail.completion_status is PhaseTrailCompletionStatus.CONTAINED_PRESERVED
            for trail in trails
        ),
        suspended_trail_count=sum(
            trail.completion_status is PhaseTrailCompletionStatus.SUSPENDED_PRESERVED
            for trail in trails
        ),
        rejected_trail_count=sum(
            trail.completion_status is PhaseTrailCompletionStatus.REJECTED_NON_PROGRESS
            for trail in trails
        ),
        unresolved_branch_count=len(unresolved_ids),
        conflict_branch_count=len(conflict_ids),
        candidate_plurality_preserved=True,
        immutable_successor_law_enforced=True,
        fixed_phase_sequence_forced=False,
        arbitrary_neighbor_composition_performed=False,
        selected_trail_id=None,
        selected_meaning=False,
        permission_authority_available=False,
        route_authority_available=False,
        tool_authority_available=False,
        memory_authority_available=False,
        action_authority_available=False,
        delivery_authority_available=False,
        hidden_fallback_allowed=False,
    )


def construct_candidate_resonant_phase_trails(
    projection_result: object,
    binding_result: object,
    *,
    registry: object = None,
    policy: object = _DEFAULT_SENTINEL,
    limits: object = _DEFAULT_SENTINEL,
) -> CandidateResonantPhaseTrailResult:
    """Construct every trail supported by the closed Slice 36E policy."""

    selected_registry = (
        registry
        if registry is not None
        else build_default_symbolic_grammar_operator_registry()
    )
    selected_policy = (
        build_default_phase_trail_policy()
        if policy is _DEFAULT_SENTINEL
        else policy
    )
    selected_limits = (
        default_phase_trail_limits()
        if limits is _DEFAULT_SENTINEL
        else limits
    )

    policy_issues = _policy_issues(selected_policy)
    limits_issues = _limits_issues(selected_limits)
    if policy_issues or limits_issues:
        return _result(
            status=PhaseTrailConstructionStatus.MALFORMED_PHASE_TRAIL,
            reason_code="invalid_phase_trail_policy_or_limits",
            phase_trail_set_created=False,
            source_preserved_in_custody=False,
            source_event_id="",
            source_sha256="",
            projection_id="",
            binding_set_id="",
            grammar_registry_id=getattr(selected_registry, "registry_id", ""),
            policy=(
                selected_policy
                if type(selected_policy) is PhaseTrailConstructionPolicy
                else None
            ),
            limits=(
                selected_limits
                if type(selected_limits) is PhaseTrailConstructionLimits
                else None
            ),
            phase_trail_set=None,
            validation_issue_codes=(*policy_issues, *limits_issues),
        )

    assert type(selected_policy) is PhaseTrailConstructionPolicy
    assert type(selected_limits) is PhaseTrailConstructionLimits

    if type(projection_result) is not SourceFieldProjectionResult:
        return _result(
            status=PhaseTrailConstructionStatus.MALFORMED_PHASE_TRAIL,
            reason_code="invalid_source_field_projection_result",
            phase_trail_set_created=False,
            source_preserved_in_custody=False,
            source_event_id="",
            source_sha256="",
            projection_id="",
            binding_set_id="",
            grammar_registry_id=getattr(selected_registry, "registry_id", ""),
            policy=selected_policy,
            limits=selected_limits,
            phase_trail_set=None,
            validation_issue_codes=("invalid_source_field_projection_result_type",),
        )
    if type(binding_result) is not ResonantOperatorCandidateBindingResult:
        return _result(
            status=PhaseTrailConstructionStatus.MALFORMED_PHASE_TRAIL,
            reason_code="invalid_candidate_binding_result",
            phase_trail_set_created=False,
            source_preserved_in_custody=projection_result.source_preserved_in_custody,
            source_event_id=projection_result.source_event_id,
            source_sha256=projection_result.source_sha256,
            projection_id=(
                projection_result.projection.projection_id
                if projection_result.projection else ""
            ),
            binding_set_id="",
            grammar_registry_id=getattr(selected_registry, "registry_id", ""),
            policy=selected_policy,
            limits=selected_limits,
            phase_trail_set=None,
            validation_issue_codes=("invalid_candidate_binding_result_type",),
        )
    if type(selected_registry) is not SymbolicGrammarOperatorRegistry:
        return _result(
            status=PhaseTrailConstructionStatus.MALFORMED_PHASE_TRAIL,
            reason_code="invalid_grammar_registry",
            phase_trail_set_created=False,
            source_preserved_in_custody=binding_result.source_preserved_in_custody,
            source_event_id=binding_result.source_event_id,
            source_sha256=binding_result.source_sha256,
            projection_id=binding_result.projection_id,
            binding_set_id=(
                binding_result.binding_set.binding_set_id
                if binding_result.binding_set else ""
            ),
            grammar_registry_id="",
            policy=selected_policy,
            limits=selected_limits,
            phase_trail_set=None,
            validation_issue_codes=("invalid_grammar_registry_type",),
        )

    projection_report = validate_source_field_projection_result(projection_result)
    registry_report = validate_symbolic_grammar_operator_registry(selected_registry)
    projection = projection_result.projection
    ruleset = build_default_resonant_operator_proposal_ruleset(selected_registry)
    binding_report = (
        validate_resonant_operator_candidate_binding_result(
            binding_result,
            projection,
            selected_registry,
            ruleset,
        )
        if projection is not None
        else None
    )
    validation_codes = tuple(
        f"projection:{item.field}:{item.code}"
        for item in projection_report.issues
    ) + tuple(
        f"registry:{item.field}:{item.code}"
        for item in registry_report.issues
    ) + tuple(
        f"binding:{item.field}:{item.code}"
        for item in (binding_report.issues if binding_report else ())
    )
    if (
        not projection_report.ok
        or not registry_report.ok
        or binding_report is None
        or not binding_report.ok
        or projection is None
        or binding_result.binding_set is None
    ):
        return _result(
            status=PhaseTrailConstructionStatus.MALFORMED_PHASE_TRAIL,
            reason_code="predecessor_validation_failed",
            phase_trail_set_created=False,
            source_preserved_in_custody=binding_result.source_preserved_in_custody,
            source_event_id=binding_result.source_event_id,
            source_sha256=binding_result.source_sha256,
            projection_id=binding_result.projection_id,
            binding_set_id=(
                binding_result.binding_set.binding_set_id
                if binding_result.binding_set else ""
            ),
            grammar_registry_id=selected_registry.registry_id,
            policy=selected_policy,
            limits=selected_limits,
            phase_trail_set=None,
            validation_issue_codes=validation_codes or ("missing_predecessor_record",),
        )

    binding_set = binding_result.binding_set
    if binding_set.grammar_registry_id != selected_registry.registry_id:
        return _result(
            status=PhaseTrailConstructionStatus.MALFORMED_PHASE_TRAIL,
            reason_code="binding_registry_identity_mismatch",
            phase_trail_set_created=False,
            source_preserved_in_custody=True,
            source_event_id=binding_set.source_event_id,
            source_sha256=binding_set.source_sha256,
            projection_id=binding_set.projection_id,
            binding_set_id=binding_set.binding_set_id,
            grammar_registry_id=selected_registry.registry_id,
            policy=selected_policy,
            limits=selected_limits,
            phase_trail_set=None,
            validation_issue_codes=("binding_registry_identity_mismatch",),
        )

    if not binding_set.candidates:
        empty = _empty_set(
            status=PhaseTrailConstructionStatus.ZERO_PHASE_TRAILS,
            binding_result=binding_result,
            registry=selected_registry,
            policy=selected_policy,
            limits=selected_limits,
        )
        return _result(
            status=empty.status,
            reason_code="no_operator_candidates",
            phase_trail_set_created=True,
            source_preserved_in_custody=True,
            source_event_id=binding_set.source_event_id,
            source_sha256=binding_set.source_sha256,
            projection_id=binding_set.projection_id,
            binding_set_id=binding_set.binding_set_id,
            grammar_registry_id=selected_registry.registry_id,
            policy=selected_policy,
            limits=selected_limits,
            phase_trail_set=empty,
            validation_issue_codes=(),
        )

    if not binding_set.structural_progression_allowed:
        empty = _empty_set(
            status=PhaseTrailConstructionStatus.UNSUPPORTED_OPERATOR_SEQUENCE,
            binding_result=binding_result,
            registry=selected_registry,
            policy=selected_policy,
            limits=selected_limits,
        )
        return _result(
            status=empty.status,
            reason_code="source_or_binding_progression_held",
            phase_trail_set_created=True,
            source_preserved_in_custody=True,
            source_event_id=binding_set.source_event_id,
            source_sha256=binding_set.source_sha256,
            projection_id=binding_set.projection_id,
            binding_set_id=binding_set.binding_set_id,
            grammar_registry_id=selected_registry.registry_id,
            policy=selected_policy,
            limits=selected_limits,
            phase_trail_set=empty,
            validation_issue_codes=(),
        )

    plans = _build_plans(binding_set.candidates, selected_registry)
    if plans is None or any(
        len(plan) > selected_limits.max_applications_per_trail
        for plan in (plans or ())
    ):
        return _result(
            status=PhaseTrailConstructionStatus.UNSUPPORTED_OPERATOR_SEQUENCE,
            reason_code="operator_definition_or_explicit_sequence_unavailable",
            phase_trail_set_created=False,
            source_preserved_in_custody=True,
            source_event_id=binding_set.source_event_id,
            source_sha256=binding_set.source_sha256,
            projection_id=binding_set.projection_id,
            binding_set_id=binding_set.binding_set_id,
            grammar_registry_id=selected_registry.registry_id,
            policy=selected_policy,
            limits=selected_limits,
            phase_trail_set=None,
            validation_issue_codes=("unsupported_operator_sequence",),
        )
    if len(plans) > selected_limits.max_trails:
        return _result(
            status=PhaseTrailConstructionStatus.PHASE_TRAIL_LIMIT_EXCEEDED,
            reason_code="phase_trail_limit_exceeded_no_partial_result",
            phase_trail_set_created=False,
            source_preserved_in_custody=True,
            source_event_id=binding_set.source_event_id,
            source_sha256=binding_set.source_sha256,
            projection_id=binding_set.projection_id,
            binding_set_id=binding_set.binding_set_id,
            grammar_registry_id=selected_registry.registry_id,
            policy=selected_policy,
            limits=selected_limits,
            phase_trail_set=None,
            validation_issue_codes=("phase_trail_limit_exceeded",),
        )

    set_identity = _trail_set_identity(
        source_event_id=binding_set.source_event_id,
        source_sha256=binding_set.source_sha256,
        projection_id=binding_set.projection_id,
        source_field_schema_id=binding_set.source_field_schema_id,
        binding_set_id=binding_set.binding_set_id,
        grammar_registry_id=selected_registry.registry_id,
        grammar_registry_version=selected_registry.registry_version,
        policy_id=selected_policy.policy_id,
        limits_id=selected_limits.limits_id,
    )
    phase_trail_set_id = stable_record_id(
        "candidate_resonant_phase_trail_set", set_identity
    )
    trails = tuple(
        _build_trail(
            plan=plan,
            phase_trail_set_id=phase_trail_set_id,
            binding_result=binding_result,
            registry=selected_registry,
            policy=selected_policy,
        )
        for plan in plans
    )
    status = _status_for_trails(trails)
    trail_set = _make_set(
        trails=trails,
        status=status,
        binding_result=binding_result,
        registry=selected_registry,
        policy=selected_policy,
        limits=selected_limits,
    )
    return _result(
        status=status,
        reason_code="candidate_phase_trails_constructed_without_selection",
        phase_trail_set_created=True,
        source_preserved_in_custody=True,
        source_event_id=binding_set.source_event_id,
        source_sha256=binding_set.source_sha256,
        projection_id=binding_set.projection_id,
        binding_set_id=binding_set.binding_set_id,
        grammar_registry_id=selected_registry.registry_id,
        policy=selected_policy,
        limits=selected_limits,
        phase_trail_set=trail_set,
        validation_issue_codes=(),
    )
