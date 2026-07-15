"""Immutable candidate grammar-state transformations for Slice 36E.

This module applies only the structural effects already registered by Slice
36C to exact Slice 36D candidates. It does not invoke any of the ten RSOC core
operators. Every application creates a new successor record and preserves the
predecessor record unchanged.
"""

from __future__ import annotations

from collections.abc import Iterable

from ..resonant_operator_candidate_binding import (
    ResonantOperatorBindingCandidate,
)
from ..schema import stable_record_id
from ..symbolic_grammar_operator_registry import (
    GrammarOperatorDefinition,
    GrammarOperatorDriftEffectStatus,
    GrammarOperatorEffect,
)
from .schema import (
    CANDIDATE_APPLICATION_SCHEMA_ID,
    PHASE_TRAIL_SCHEMA_VERSION,
    PHASE_TRAIL_SPEC_ID,
    PHASE_TRAIL_SPEC_VERSION,
    SYMBOLIC_FIELD_STATE_SCHEMA_ID,
    CandidateApplicationStatus,
    CandidateGrammarOperatorApplication,
    CandidatePhaseStatus,
    CandidateSymbolicFieldState,
    PhaseTrailCompletionStatus,
)


def _unique_text(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value for value in values if value))


def build_initial_candidate_symbolic_state(
    *,
    phase_trail_id: str,
    phase_trail_set_id: str,
    source_event_id: str,
    source_sha256: str,
    projection_id: str,
    source_field_schema_id: str,
    binding_set_id: str,
    identity_field_id: str,
    participating_binding_ids: tuple[str, ...],
    preserved_source_span_ids: tuple[str, ...],
    unresolved_branch_ids: tuple[str, ...],
    conflict_branch_ids: tuple[str, ...],
) -> CandidateSymbolicFieldState:
    body = {
        "phase_trail_id": phase_trail_id,
        "phase_trail_set_id": phase_trail_set_id,
        "source_event_id": source_event_id,
        "projection_id": projection_id,
        "binding_set_id": binding_set_id,
        "predecessor_state_id": None,
        "predecessor_application_id": None,
        "state_ordinal": 0,
        "identity_field_id": identity_field_id,
        "participating_binding_ids": participating_binding_ids,
        "applied_binding_ids": (),
        "preserved_source_span_ids": preserved_source_span_ids,
        "candidate_phase_status": CandidatePhaseStatus.UNASSIGNED_INITIAL_STATE,
        "candidate_phase_values": (),
        "phase_ancestry": ((),),
        "recursive_depth": 0,
        "active_constraint_codes": (),
        "unresolved_branch_ids": unresolved_branch_ids,
        "conflict_branch_ids": conflict_branch_ids,
        "suspended_branch_ids": (),
        "containment_condition_codes": (),
        "drift_indicator_codes": (),
        "entropy_effect_codes": (),
        "completion_status": PhaseTrailCompletionStatus.OPEN_UNRESOLVED,
        "structural_progression_allowed": True,
        "contained": False,
        "suspended": False,
        "sealed": False,
        "rejected": False,
        "phase_trail_spec_id": PHASE_TRAIL_SPEC_ID,
        "phase_trail_spec_version": PHASE_TRAIL_SPEC_VERSION,
        "schema_version": PHASE_TRAIL_SCHEMA_VERSION,
        "state_schema_id": SYMBOLIC_FIELD_STATE_SCHEMA_ID,
    }
    state_id = stable_record_id("candidate_symbolic_field_state", body)
    return CandidateSymbolicFieldState(
        state_id=state_id,
        phase_trail_id=phase_trail_id,
        phase_trail_set_id=phase_trail_set_id,
        source_event_id=source_event_id,
        source_sha256=source_sha256,
        projection_id=projection_id,
        source_field_schema_id=source_field_schema_id,
        binding_set_id=binding_set_id,
        initial_state_id=state_id,
        predecessor_state_id=None,
        predecessor_application_id=None,
        state_ordinal=0,
        identity_field_id=identity_field_id,
        identity_field_preserved=True,
        participating_binding_ids=participating_binding_ids,
        applied_binding_ids=(),
        preserved_source_span_ids=preserved_source_span_ids,
        candidate_phase_status=CandidatePhaseStatus.UNASSIGNED_INITIAL_STATE,
        candidate_phase_values=(),
        phase_ancestry=((),),
        recursive_depth=0,
        active_constraint_codes=(),
        unresolved_branch_ids=unresolved_branch_ids,
        conflict_branch_ids=conflict_branch_ids,
        suspended_branch_ids=(),
        containment_condition_codes=(),
        drift_indicator_codes=(),
        entropy_effect_codes=(),
        completion_status=PhaseTrailCompletionStatus.OPEN_UNRESOLVED,
        structural_progression_allowed=True,
        contained=False,
        suspended=False,
        sealed=False,
        rejected=False,
        prior_state_mutated=False,
        core_rsoc_operator_application_count=0,
        selected_meaning=False,
        permission_inferred=False,
        route_created=False,
        tool_routing_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        action_performed=False,
        delivery_performed=False,
    )


def _phase_after(
    current: CandidateSymbolicFieldState,
    phase_affinity: str | None,
) -> tuple[
    CandidatePhaseStatus,
    tuple[str, ...],
    str,
    tuple[str, ...],
    bool,
]:
    """Return status, values, transition code, drift codes, containment."""

    if phase_affinity is None:
        if current.candidate_phase_values:
            return (
                CandidatePhaseStatus.PRESERVED_PREDECESSOR_CANDIDATE,
                current.candidate_phase_values,
                "predecessor_phase_candidate_preserved_no_operator_affinity",
                (),
                False,
            )
        return (
            CandidatePhaseStatus.UNRESOLVED_NO_AUTHORIZED_AFFINITY,
            (),
            "operator_phase_affinity_undefined",
            (),
            False,
        )

    if (
        current.candidate_phase_values
        and phase_affinity not in current.candidate_phase_values
    ):
        return (
            CandidatePhaseStatus.EXPLICIT_ADVISORY_CANDIDATE,
            (phase_affinity,),
            "candidate_phase_change_contained_no_transition_law",
            (
                "candidate_phase_change_without_installed_transition_law",
            ),
            True,
        )

    return (
        CandidatePhaseStatus.EXPLICIT_ADVISORY_CANDIDATE,
        (phase_affinity,),
        "explicit_advisory_phase_affinity_preserved_as_candidate",
        (),
        False,
    )


def apply_candidate_grammar_operator(
    *,
    current_state: CandidateSymbolicFieldState,
    candidate: ResonantOperatorBindingCandidate,
    definition: GrammarOperatorDefinition,
    structural_effect: GrammarOperatorEffect,
    phase_affinity: str | None,
    remaining_binding_ids: tuple[str, ...] = (),
) -> tuple[CandidateGrammarOperatorApplication, CandidateSymbolicFieldState]:
    """Create one immutable successor from one candidate application.

    The caller must supply a validated candidate, definition, and current state.
    This function still enforces the local authority boundary and refuses to
    mutate or activate core RSOC machinery.
    """

    if structural_effect not in definition.allowed_effects:
        raise ValueError("structural effect is not authorized by operator definition")
    if candidate.candidate_operator_key != definition.operator_key:
        raise ValueError("candidate and definition operator identities differ")
    if candidate.candidate_operator_version != definition.operator_version:
        raise ValueError("candidate and definition versions differ")
    if candidate.candidate_operator_definition_id != definition.definition_id:
        raise ValueError("candidate and definition record identities differ")
    if not current_state.structural_progression_allowed:
        raise ValueError("current state does not permit further structural progression")

    (
        phase_after_status,
        phase_after_values,
        phase_transition_code,
        phase_drift_codes,
        phase_change_contained,
    ) = _phase_after(current_state, phase_affinity)

    unresolved = list(current_state.unresolved_branch_ids)
    unresolved.extend(candidate.missing_prerequisite_codes)
    if phase_affinity is None:
        unresolved.append(
            f"operator_phase_affinity_undefined:{candidate.candidate_binding_id}"
        )
    if candidate.neighbor_compatibility_status.value.endswith(
        "no_compatibility_table"
    ):
        unresolved.append(
            f"neighbor_compatibility_unresolved:{candidate.candidate_binding_id}"
        )

    conflicts = list(current_state.conflict_branch_ids)
    conflicts.extend(candidate.competing_candidate_binding_ids)
    conflicts.extend(candidate.conflicting_evidence_codes)

    suspended_branches = list(current_state.suspended_branch_ids)
    containment = list(current_state.containment_condition_codes)
    drift = list(current_state.drift_indicator_codes)
    drift.extend(phase_drift_codes)
    if (
        definition.drift_effect_status
        is GrammarOperatorDriftEffectStatus.DOCUMENTED_ADVISORY_ONLY
    ):
        drift.append(definition.drift_effect_code)

    entropy = list(current_state.entropy_effect_codes)
    entropy.append(definition.entropy_effect_code)
    constraints = list(current_state.active_constraint_codes)
    constraints.append(
        f"candidate_effect:{candidate.candidate_operator_key}:{structural_effect.value}"
    )

    contained = current_state.contained or phase_change_contained
    suspended = current_state.suspended
    sealed = current_state.sealed
    rejected = current_state.rejected
    progression_allowed = True
    completion = PhaseTrailCompletionStatus.OPEN_UNRESOLVED
    application_status = CandidateApplicationStatus.SUCCESSOR_CREATED

    if phase_change_contained:
        containment.append("phase_change_held_without_installed_transition_law")
        suspended_branches.extend(remaining_binding_ids)
        progression_allowed = False
        contained = True
        completion = PhaseTrailCompletionStatus.CONTAINED_PRESERVED
        application_status = CandidateApplicationStatus.DRIFT_CONTAINED
    elif structural_effect is GrammarOperatorEffect.SUSPEND:
        suspended_branches.extend(remaining_binding_ids)
        suspended_branches.append(candidate.candidate_binding_id)
        progression_allowed = False
        suspended = True
        completion = PhaseTrailCompletionStatus.SUSPENDED_PRESERVED
        application_status = CandidateApplicationStatus.SUCCESSOR_SUSPENDED
    elif structural_effect is GrammarOperatorEffect.CONTAIN:
        containment.append(
            f"candidate_containment:{candidate.candidate_binding_id}"
        )
        suspended_branches.extend(remaining_binding_ids)
        progression_allowed = False
        contained = True
        completion = PhaseTrailCompletionStatus.CONTAINED_PRESERVED
        application_status = CandidateApplicationStatus.SUCCESSOR_CONTAINED
    elif structural_effect is GrammarOperatorEffect.REJECT:
        suspended_branches.extend(remaining_binding_ids)
        progression_allowed = False
        rejected = True
        completion = PhaseTrailCompletionStatus.REJECTED_NON_PROGRESS
        application_status = CandidateApplicationStatus.SUCCESSOR_REJECTED
    elif structural_effect is GrammarOperatorEffect.SEAL:
        suspended_branches.extend(remaining_binding_ids)
        progression_allowed = False
        sealed = True
        completion = PhaseTrailCompletionStatus.SEALED_UNPROVEN

    application_ordinal = current_state.state_ordinal
    application_identity = {
        "phase_trail_id": current_state.phase_trail_id,
        "phase_trail_set_id": current_state.phase_trail_set_id,
        "application_ordinal": application_ordinal,
        "candidate_binding_id": candidate.candidate_binding_id,
        "candidate_operator_key": candidate.candidate_operator_key,
        "candidate_operator_version": candidate.candidate_operator_version,
        "candidate_operator_definition_id": candidate.candidate_operator_definition_id,
        "structural_effect": structural_effect,
        "input_state_id": current_state.state_id,
        "phase_before_status": current_state.candidate_phase_status,
        "phase_before_values": current_state.candidate_phase_values,
        "phase_after_status": phase_after_status,
        "phase_after_values": phase_after_values,
        "phase_transition_code": phase_transition_code,
        "source_span_ids": candidate.source_span_ids,
        "phase_trail_spec_id": PHASE_TRAIL_SPEC_ID,
        "phase_trail_spec_version": PHASE_TRAIL_SPEC_VERSION,
        "schema_version": PHASE_TRAIL_SCHEMA_VERSION,
        "application_schema_id": CANDIDATE_APPLICATION_SCHEMA_ID,
    }
    application_id = stable_record_id(
        "candidate_grammar_operator_application",
        application_identity,
    )

    successor_body = {
        "phase_trail_id": current_state.phase_trail_id,
        "phase_trail_set_id": current_state.phase_trail_set_id,
        "source_event_id": current_state.source_event_id,
        "projection_id": current_state.projection_id,
        "binding_set_id": current_state.binding_set_id,
        "predecessor_state_id": current_state.state_id,
        "predecessor_application_id": application_id,
        "state_ordinal": current_state.state_ordinal + 1,
        "identity_field_id": current_state.identity_field_id,
        "participating_binding_ids": current_state.participating_binding_ids,
        "applied_binding_ids": _unique_text(
            (*current_state.applied_binding_ids, candidate.candidate_binding_id)
        ),
        "preserved_source_span_ids": current_state.preserved_source_span_ids,
        "candidate_phase_status": phase_after_status,
        "candidate_phase_values": phase_after_values,
        "phase_ancestry": (
            *current_state.phase_ancestry,
            phase_after_values,
        ),
        "recursive_depth": current_state.recursive_depth + 1,
        "active_constraint_codes": _unique_text(constraints),
        "unresolved_branch_ids": _unique_text(unresolved),
        "conflict_branch_ids": _unique_text(conflicts),
        "suspended_branch_ids": _unique_text(suspended_branches),
        "containment_condition_codes": _unique_text(containment),
        "drift_indicator_codes": _unique_text(drift),
        "entropy_effect_codes": _unique_text(entropy),
        "completion_status": completion,
        "structural_progression_allowed": progression_allowed,
        "contained": contained,
        "suspended": suspended,
        "sealed": sealed,
        "rejected": rejected,
        "phase_trail_spec_id": PHASE_TRAIL_SPEC_ID,
        "phase_trail_spec_version": PHASE_TRAIL_SPEC_VERSION,
        "schema_version": PHASE_TRAIL_SCHEMA_VERSION,
        "state_schema_id": SYMBOLIC_FIELD_STATE_SCHEMA_ID,
    }
    successor_id = stable_record_id(
        "candidate_symbolic_field_state",
        successor_body,
    )
    successor = CandidateSymbolicFieldState(
        state_id=successor_id,
        phase_trail_id=current_state.phase_trail_id,
        phase_trail_set_id=current_state.phase_trail_set_id,
        source_event_id=current_state.source_event_id,
        source_sha256=current_state.source_sha256,
        projection_id=current_state.projection_id,
        source_field_schema_id=current_state.source_field_schema_id,
        binding_set_id=current_state.binding_set_id,
        initial_state_id=current_state.initial_state_id,
        predecessor_state_id=current_state.state_id,
        predecessor_application_id=application_id,
        state_ordinal=current_state.state_ordinal + 1,
        identity_field_id=current_state.identity_field_id,
        identity_field_preserved=True,
        participating_binding_ids=current_state.participating_binding_ids,
        applied_binding_ids=_unique_text(
            (*current_state.applied_binding_ids, candidate.candidate_binding_id)
        ),
        preserved_source_span_ids=current_state.preserved_source_span_ids,
        candidate_phase_status=phase_after_status,
        candidate_phase_values=phase_after_values,
        phase_ancestry=(*current_state.phase_ancestry, phase_after_values),
        recursive_depth=current_state.recursive_depth + 1,
        active_constraint_codes=_unique_text(constraints),
        unresolved_branch_ids=_unique_text(unresolved),
        conflict_branch_ids=_unique_text(conflicts),
        suspended_branch_ids=_unique_text(suspended_branches),
        containment_condition_codes=_unique_text(containment),
        drift_indicator_codes=_unique_text(drift),
        entropy_effect_codes=_unique_text(entropy),
        completion_status=completion,
        structural_progression_allowed=progression_allowed,
        contained=contained,
        suspended=suspended,
        sealed=sealed,
        rejected=rejected,
        prior_state_mutated=False,
        core_rsoc_operator_application_count=0,
        selected_meaning=False,
        permission_inferred=False,
        route_created=False,
        tool_routing_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        action_performed=False,
        delivery_performed=False,
    )

    application = CandidateGrammarOperatorApplication(
        application_id=application_id,
        phase_trail_id=current_state.phase_trail_id,
        phase_trail_set_id=current_state.phase_trail_set_id,
        source_event_id=current_state.source_event_id,
        projection_id=current_state.projection_id,
        binding_set_id=current_state.binding_set_id,
        application_ordinal=application_ordinal,
        candidate_binding_id=candidate.candidate_binding_id,
        candidate_operator_key=candidate.candidate_operator_key,
        candidate_operator_version=candidate.candidate_operator_version,
        candidate_operator_definition_id=(
            candidate.candidate_operator_definition_id
        ),
        candidate_operator_family=candidate.candidate_operator_family,
        candidate_operator_glyph=candidate.candidate_operator_glyph,
        structural_effect=structural_effect,
        input_state_id=current_state.state_id,
        successor_state_id=successor.state_id,
        phase_before_status=current_state.candidate_phase_status,
        phase_before_values=current_state.candidate_phase_values,
        phase_after_status=phase_after_status,
        phase_after_values=phase_after_values,
        phase_transition_code=phase_transition_code,
        source_span_ids=candidate.source_span_ids,
        transformation_ancestry_state_ids=tuple(
            dict.fromkeys(
                state_id
                for state_id in (
                    current_state.initial_state_id,
                    current_state.predecessor_state_id,
                    current_state.state_id,
                )
                if state_id
            )
        ),
        identity_field_id_before=current_state.identity_field_id,
        identity_field_id_after=successor.identity_field_id,
        identity_field_preserved=True,
        source_spans_preserved=True,
        recursive_depth_before=current_state.recursive_depth,
        recursive_depth_after=successor.recursive_depth,
        unresolved_branch_ids=successor.unresolved_branch_ids,
        conflict_branch_ids=successor.conflict_branch_ids,
        suspended_branch_ids=successor.suspended_branch_ids,
        containment_condition_codes=successor.containment_condition_codes,
        drift_indicator_codes=successor.drift_indicator_codes,
        entropy_effect_code=definition.entropy_effect_code,
        application_status=application_status,
        successor_created=True,
        prior_state_mutated=False,
        core_rsoc_operator_key=None,
        core_rsoc_operator_applied=False,
        selected_phase=False,
        selected_meaning=False,
        permission_inferred=False,
        route_created=False,
        tool_routing_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        action_performed=False,
        delivery_performed=False,
    )
    return application, successor
