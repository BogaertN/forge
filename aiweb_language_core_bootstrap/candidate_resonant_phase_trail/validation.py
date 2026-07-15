"""Deterministic validation for Slice 36E phase-trail records."""

from __future__ import annotations

from ..resonant_operator_candidate_binding import (
    ResonantOperatorCandidateBindingResult,
)
from ..schema import ValidationReport, issue
from ..source_field_projection import SourceFieldProjectionResult
from ..symbolic_grammar_operator_registry import (
    GrammarOperatorEffect,
    SymbolicGrammarOperatorRegistry,
    grammar_operator_for_key,
)
from .schema import (
    ABSOLUTE_MAX_APPLICATIONS_PER_TRAIL,
    ABSOLUTE_MAX_PHASE_TRAILS,
    CANDIDATE_APPLICATION_SCHEMA_ID,
    PHASE_TRAIL_LIMITS_SCHEMA_ID,
    PHASE_TRAIL_POLICY_SCHEMA_ID,
    PHASE_TRAIL_RESULT_SCHEMA_ID,
    PHASE_TRAIL_SCHEMA_ID,
    PHASE_TRAIL_SCHEMA_VERSION,
    PHASE_TRAIL_SET_SCHEMA_ID,
    PHASE_TRAIL_SPEC_ID,
    PHASE_TRAIL_SPEC_VERSION,
    SYMBOLIC_FIELD_STATE_SCHEMA_ID,
    CandidateApplicationStatus,
    CandidateGrammarOperatorApplication,
    CandidatePhaseStatus,
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

_ALLOWED_PHASE_VALUES = frozenset(f"Φ{index}" for index in range(1, 10))


def _report(issues: list[object]) -> ValidationReport:
    return ValidationReport(
        schema_version=PHASE_TRAIL_SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def _base_issues(record: object) -> list[object]:
    issues: list[object] = []
    if getattr(record, "phase_trail_spec_id", None) != PHASE_TRAIL_SPEC_ID:
        issues.append(issue("phase_trail_spec_id", "phase_trail_spec_id_mismatch"))
    if (
        getattr(record, "phase_trail_spec_version", None)
        != PHASE_TRAIL_SPEC_VERSION
    ):
        issues.append(
            issue("phase_trail_spec_version", "phase_trail_spec_version_mismatch")
        )
    if getattr(record, "schema_version", None) != PHASE_TRAIL_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    return issues


def _all_false(record: object, names: tuple[str, ...]) -> list[object]:
    issues: list[object] = []
    for name in names:
        if getattr(record, name, None) is not False:
            issues.append(issue(name, "must_remain_false"))
    return issues


def _unique_text_tuple(
    value: object,
    *,
    field: str,
    allow_empty: bool = True,
) -> list[object]:
    issues: list[object] = []
    if type(value) is not tuple:
        return [issue(field, "tuple_required")]
    if not allow_empty and not value:
        issues.append(issue(field, "nonempty_tuple_required"))
    if any(type(item) is not str or not item for item in value):
        issues.append(issue(field, "nonempty_text_items_required"))
    if len(value) != len(set(value)):
        issues.append(issue(field, "duplicate_values"))
    return issues


def _phase_issues(
    status: object,
    values: object,
    *,
    prefix: str,
) -> list[object]:
    issues: list[object] = []
    if type(status) is not CandidatePhaseStatus:
        issues.append(issue(f"{prefix}_status", "invalid_phase_status"))
    if type(values) is not tuple:
        issues.append(issue(f"{prefix}_values", "tuple_required"))
        return issues
    if any(value not in _ALLOWED_PHASE_VALUES for value in values):
        issues.append(issue(f"{prefix}_values", "unsupported_phase_value"))
    if len(values) != len(set(values)):
        issues.append(issue(f"{prefix}_values", "duplicate_phase_value"))
    if status in {
        CandidatePhaseStatus.UNASSIGNED_INITIAL_STATE,
        CandidatePhaseStatus.UNRESOLVED_NO_AUTHORIZED_AFFINITY,
    } and values:
        issues.append(issue(f"{prefix}_values", "must_be_empty_for_status"))
    if status in {
        CandidatePhaseStatus.EXPLICIT_ADVISORY_CANDIDATE,
        CandidatePhaseStatus.PRESERVED_PREDECESSOR_CANDIDATE,
    } and not values:
        issues.append(issue(f"{prefix}_values", "nonempty_required_for_status"))
    return issues


def validate_phase_trail_construction_policy(
    policy: object,
) -> ValidationReport:
    if type(policy) is not PhaseTrailConstructionPolicy:
        return _report([issue("policy", "invalid_record_type")])
    issues = _base_issues(policy)
    if policy.policy_schema_id != PHASE_TRAIL_POLICY_SCHEMA_ID:
        issues.append(issue("policy_schema_id", "policy_schema_id_mismatch"))
    if policy.policy_id != policy.expected_id():
        issues.append(issue("policy_id", "stable_identifier_mismatch"))
    if policy.policy_version != "1.0.0":
        issues.append(issue("policy_version", "unsupported_policy_version"))
    for name in (
        "single_binding_trails_required",
        "explicit_parent_child_trails_allowed",
        "branch_every_allowed_effect",
        "branch_every_explicit_phase_affinity",
        "advisory_phase_affinity_only",
        "immutable_successor_required",
    ):
        if getattr(policy, name) is not True:
            issues.append(issue(name, "must_remain_true"))
    issues.extend(
        _all_false(
            policy,
            (
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
            ),
        )
    )
    issues.extend(
        _unique_text_tuple(
            policy.source_authority_refs,
            field="source_authority_refs",
            allow_empty=False,
        )
    )
    return _report(issues)


def validate_phase_trail_construction_limits(
    limits: object,
) -> ValidationReport:
    if type(limits) is not PhaseTrailConstructionLimits:
        return _report([issue("limits", "invalid_record_type")])
    issues = _base_issues(limits)
    if limits.limits_schema_id != PHASE_TRAIL_LIMITS_SCHEMA_ID:
        issues.append(issue("limits_schema_id", "limits_schema_id_mismatch"))
    if limits.limits_id != limits.expected_id():
        issues.append(issue("limits_id", "stable_identifier_mismatch"))
    if type(limits.max_trails) is not int or not (
        0 <= limits.max_trails <= ABSOLUTE_MAX_PHASE_TRAILS
    ):
        issues.append(issue("max_trails", "invalid_limit"))
    if type(limits.max_applications_per_trail) is not int or not (
        1
        <= limits.max_applications_per_trail
        <= ABSOLUTE_MAX_APPLICATIONS_PER_TRAIL
    ):
        issues.append(issue("max_applications_per_trail", "invalid_limit"))
    return _report(issues)


def validate_candidate_symbolic_field_state(
    state: object,
) -> ValidationReport:
    if type(state) is not CandidateSymbolicFieldState:
        return _report([issue("state", "invalid_record_type")])
    issues = _base_issues(state)
    if state.state_schema_id != SYMBOLIC_FIELD_STATE_SCHEMA_ID:
        issues.append(issue("state_schema_id", "state_schema_id_mismatch"))
    if state.state_id != state.expected_id():
        issues.append(issue("state_id", "stable_identifier_mismatch"))
    if type(state.state_ordinal) is not int or state.state_ordinal < 0:
        issues.append(issue("state_ordinal", "nonnegative_integer_required"))
    if type(state.recursive_depth) is not int or (
        state.recursive_depth != state.state_ordinal
    ):
        issues.append(issue("recursive_depth", "must_equal_state_ordinal"))
    if state.identity_field_preserved is not True:
        issues.append(issue("identity_field_preserved", "must_remain_true"))
    if not state.identity_field_id:
        issues.append(issue("identity_field_id", "required"))
    issues.extend(
        _unique_text_tuple(
            state.participating_binding_ids,
            field="participating_binding_ids",
            allow_empty=False,
        )
    )
    issues.extend(
        _unique_text_tuple(
            state.applied_binding_ids,
            field="applied_binding_ids",
            allow_empty=True,
        )
    )
    issues.extend(
        _unique_text_tuple(
            state.preserved_source_span_ids,
            field="preserved_source_span_ids",
            allow_empty=False,
        )
    )
    for field_name in (
        "active_constraint_codes",
        "unresolved_branch_ids",
        "conflict_branch_ids",
        "suspended_branch_ids",
        "containment_condition_codes",
        "drift_indicator_codes",
        "entropy_effect_codes",
    ):
        issues.extend(
            _unique_text_tuple(
                getattr(state, field_name),
                field=field_name,
                allow_empty=True,
            )
        )
    issues.extend(
        _phase_issues(
            state.candidate_phase_status,
            state.candidate_phase_values,
            prefix="candidate_phase",
        )
    )
    if type(state.phase_ancestry) is not tuple or not state.phase_ancestry:
        issues.append(issue("phase_ancestry", "nonempty_tuple_required"))
    elif state.phase_ancestry[-1] != state.candidate_phase_values:
        issues.append(issue("phase_ancestry", "final_phase_mismatch"))
    else:
        for index, values in enumerate(state.phase_ancestry):
            if type(values) is not tuple or any(
                value not in _ALLOWED_PHASE_VALUES for value in values
            ):
                issues.append(
                    issue(f"phase_ancestry[{index}]", "invalid_phase_values")
                )
    if state.state_ordinal == 0:
        if state.predecessor_state_id is not None:
            issues.append(issue("predecessor_state_id", "must_be_none_for_initial"))
        if state.predecessor_application_id is not None:
            issues.append(
                issue("predecessor_application_id", "must_be_none_for_initial")
            )
        if state.initial_state_id != state.state_id:
            issues.append(issue("initial_state_id", "must_equal_initial_state_id"))
        if state.applied_binding_ids:
            issues.append(issue("applied_binding_ids", "must_be_empty_for_initial"))
        if state.candidate_phase_status is not (
            CandidatePhaseStatus.UNASSIGNED_INITIAL_STATE
        ):
            issues.append(issue("candidate_phase_status", "initial_status_required"))
    else:
        if not state.predecessor_state_id or not state.predecessor_application_id:
            issues.append(issue("predecessor", "successor_predecessor_required"))
        if not state.applied_binding_ids:
            issues.append(issue("applied_binding_ids", "successor_application_required"))
        if not state.initial_state_id:
            issues.append(issue("initial_state_id", "required"))
    if any(
        binding_id not in state.participating_binding_ids
        for binding_id in state.applied_binding_ids
    ):
        issues.append(issue("applied_binding_ids", "not_participating"))
    terminal_flags = sum(
        bool(value)
        for value in (state.contained, state.suspended, state.sealed, state.rejected)
    )
    if terminal_flags > 1:
        issues.append(issue("terminal_flags", "mutually_exclusive"))
    if terminal_flags and state.structural_progression_allowed:
        issues.append(issue("structural_progression_allowed", "must_be_false_terminal"))
    if state.completion_status is PhaseTrailCompletionStatus.SUSPENDED_PRESERVED:
        if not state.suspended:
            issues.append(issue("suspended", "required_for_completion_status"))
    if state.completion_status is PhaseTrailCompletionStatus.CONTAINED_PRESERVED:
        if not state.contained:
            issues.append(issue("contained", "required_for_completion_status"))
    if state.completion_status is PhaseTrailCompletionStatus.REJECTED_NON_PROGRESS:
        if not state.rejected:
            issues.append(issue("rejected", "required_for_completion_status"))
    if state.completion_status is PhaseTrailCompletionStatus.SEALED_UNPROVEN:
        if not state.sealed:
            issues.append(issue("sealed", "required_for_completion_status"))
    if state.prior_state_mutated is not False:
        issues.append(issue("prior_state_mutated", "must_remain_false"))
    if state.core_rsoc_operator_application_count != 0:
        issues.append(
            issue("core_rsoc_operator_application_count", "must_remain_zero")
        )
    issues.extend(
        _all_false(
            state,
            (
                "selected_meaning",
                "permission_inferred",
                "route_created",
                "tool_routing_performed",
                "memory_read_performed",
                "memory_write_performed",
                "action_performed",
                "delivery_performed",
            ),
        )
    )
    return _report(issues)


def validate_candidate_grammar_operator_application(
    application: object,
    *,
    candidate: object = None,
    definition: object = None,
    input_state: object = None,
    successor_state: object = None,
) -> ValidationReport:
    if type(application) is not CandidateGrammarOperatorApplication:
        return _report([issue("application", "invalid_record_type")])
    issues = _base_issues(application)
    if application.application_schema_id != CANDIDATE_APPLICATION_SCHEMA_ID:
        issues.append(
            issue("application_schema_id", "application_schema_id_mismatch")
        )
    if application.application_id != application.expected_id():
        issues.append(issue("application_id", "stable_identifier_mismatch"))
    if type(application.application_ordinal) is not int or (
        application.application_ordinal < 0
    ):
        issues.append(issue("application_ordinal", "nonnegative_integer_required"))
    if type(application.structural_effect) is not GrammarOperatorEffect:
        issues.append(issue("structural_effect", "invalid_effect"))
    issues.extend(
        _phase_issues(
            application.phase_before_status,
            application.phase_before_values,
            prefix="phase_before",
        )
    )
    issues.extend(
        _phase_issues(
            application.phase_after_status,
            application.phase_after_values,
            prefix="phase_after",
        )
    )
    issues.extend(
        _unique_text_tuple(
            application.source_span_ids,
            field="source_span_ids",
            allow_empty=False,
        )
    )
    issues.extend(
        _unique_text_tuple(
            application.transformation_ancestry_state_ids,
            field="transformation_ancestry_state_ids",
            allow_empty=False,
        )
    )
    if application.identity_field_preserved is not True:
        issues.append(issue("identity_field_preserved", "must_remain_true"))
    if application.source_spans_preserved is not True:
        issues.append(issue("source_spans_preserved", "must_remain_true"))
    if application.identity_field_id_before != application.identity_field_id_after:
        issues.append(issue("identity_field_id_after", "identity_not_preserved"))
    if application.recursive_depth_after != application.recursive_depth_before + 1:
        issues.append(issue("recursive_depth_after", "must_increment_by_one"))
    if application.successor_created is not True:
        issues.append(issue("successor_created", "must_remain_true"))
    if application.prior_state_mutated is not False:
        issues.append(issue("prior_state_mutated", "must_remain_false"))
    if application.core_rsoc_operator_key is not None:
        issues.append(issue("core_rsoc_operator_key", "must_remain_none"))
    if application.core_rsoc_operator_applied is not False:
        issues.append(issue("core_rsoc_operator_applied", "must_remain_false"))
    issues.extend(
        _all_false(
            application,
            (
                "selected_phase",
                "selected_meaning",
                "permission_inferred",
                "route_created",
                "tool_routing_performed",
                "memory_read_performed",
                "memory_write_performed",
                "action_performed",
                "delivery_performed",
            ),
        )
    )
    if candidate is not None:
        if application.candidate_binding_id != getattr(
            candidate, "candidate_binding_id", None
        ):
            issues.append(issue("candidate_binding_id", "candidate_mismatch"))
        for field_name in (
            "candidate_operator_key",
            "candidate_operator_version",
            "candidate_operator_definition_id",
            "candidate_operator_family",
            "candidate_operator_glyph",
        ):
            if getattr(application, field_name) != getattr(candidate, field_name, None):
                issues.append(issue(field_name, "candidate_metadata_mismatch"))
        if application.source_span_ids != getattr(candidate, "source_span_ids", None):
            issues.append(issue("source_span_ids", "candidate_source_span_mismatch"))
    if definition is not None:
        if application.candidate_operator_key != getattr(
            definition, "operator_key", None
        ):
            issues.append(issue("candidate_operator_key", "definition_mismatch"))
        if application.structural_effect not in getattr(
            definition, "allowed_effects", ()
        ):
            issues.append(issue("structural_effect", "not_authorized_by_definition"))
        if application.entropy_effect_code != getattr(
            definition, "entropy_effect_code", None
        ):
            issues.append(issue("entropy_effect_code", "definition_mismatch"))
    if input_state is not None:
        if type(input_state) is not CandidateSymbolicFieldState:
            issues.append(issue("input_state", "invalid_record_type"))
        else:
            if application.input_state_id != input_state.state_id:
                issues.append(issue("input_state_id", "input_state_mismatch"))
            if application.phase_before_status is not input_state.candidate_phase_status:
                issues.append(issue("phase_before_status", "input_state_mismatch"))
            if application.phase_before_values != input_state.candidate_phase_values:
                issues.append(issue("phase_before_values", "input_state_mismatch"))
            if application.recursive_depth_before != input_state.recursive_depth:
                issues.append(issue("recursive_depth_before", "input_state_mismatch"))
    if successor_state is not None:
        if type(successor_state) is not CandidateSymbolicFieldState:
            issues.append(issue("successor_state", "invalid_record_type"))
        else:
            if application.successor_state_id != successor_state.state_id:
                issues.append(issue("successor_state_id", "successor_state_mismatch"))
            if successor_state.predecessor_state_id != application.input_state_id:
                issues.append(issue("successor_state", "predecessor_state_mismatch"))
            if successor_state.predecessor_application_id != application.application_id:
                issues.append(
                    issue("successor_state", "predecessor_application_mismatch")
                )
            if application.phase_after_status is not successor_state.candidate_phase_status:
                issues.append(issue("phase_after_status", "successor_state_mismatch"))
            if application.phase_after_values != successor_state.candidate_phase_values:
                issues.append(issue("phase_after_values", "successor_state_mismatch"))
            if application.recursive_depth_after != successor_state.recursive_depth:
                issues.append(issue("recursive_depth_after", "successor_state_mismatch"))
    return _report(issues)


def validate_candidate_resonant_phase_trail(
    trail: object,
    *,
    binding_result: object = None,
    registry: object = None,
    policy: object = None,
) -> ValidationReport:
    if type(trail) is not CandidateResonantPhaseTrail:
        return _report([issue("trail", "invalid_record_type")])
    issues = _base_issues(trail)
    if trail.phase_trail_schema_id != PHASE_TRAIL_SCHEMA_ID:
        issues.append(issue("phase_trail_schema_id", "phase_trail_schema_id_mismatch"))
    if trail.phase_trail_id != trail.expected_id():
        issues.append(issue("phase_trail_id", "stable_identifier_mismatch"))
    issues.extend(
        _unique_text_tuple(
            trail.participating_binding_ids,
            field="participating_binding_ids",
            allow_empty=False,
        )
    )
    if type(trail.planned_effect_codes) is not tuple or (
        len(trail.planned_effect_codes) != len(trail.participating_binding_ids)
    ):
        issues.append(issue("planned_effect_codes", "parallel_plan_required"))
    if type(trail.planned_phase_affinity_values) is not tuple or (
        len(trail.planned_phase_affinity_values)
        != len(trail.participating_binding_ids)
    ):
        issues.append(
            issue("planned_phase_affinity_values", "parallel_plan_required")
        )
    if type(trail.states) is not tuple or not trail.states:
        issues.append(issue("states", "nonempty_tuple_required"))
        return _report(issues)
    if type(trail.applications) is not tuple:
        issues.append(issue("applications", "tuple_required"))
        return _report(issues)
    if len(trail.states) != len(trail.applications) + 1:
        issues.append(issue("states", "successor_chain_length_mismatch"))
    if trail.initial_state_id != trail.states[0].state_id:
        issues.append(issue("initial_state_id", "initial_state_mismatch"))
    if trail.final_state_id != trail.states[-1].state_id:
        issues.append(issue("final_state_id", "final_state_mismatch"))
    if trail.recursive_depth != len(trail.applications):
        issues.append(issue("recursive_depth", "application_count_mismatch"))
    if not trail.immutable_transition_chain_complete:
        issues.append(issue("immutable_transition_chain_complete", "must_remain_true"))
    if not trail.source_ancestry_complete:
        issues.append(issue("source_ancestry_complete", "must_remain_true"))
    if not trail.identity_field_preserved:
        issues.append(issue("identity_field_preserved", "must_remain_true"))
    if not trail.source_spans_preserved:
        issues.append(issue("source_spans_preserved", "must_remain_true"))
    if trail.candidate_only is not True or trail.selected_trail is not False:
        issues.append(issue("candidate_only", "candidate_unselected_required"))
    if trail.core_rsoc_operator_applications != 0:
        issues.append(issue("core_rsoc_operator_applications", "must_remain_zero"))
    issues.extend(
        _all_false(
            trail,
            (
                "selected_meaning",
                "permission_inferred",
                "route_created",
                "tool_routing_performed",
                "memory_read_performed",
                "memory_write_performed",
                "action_performed",
                "delivery_performed",
            ),
        )
    )

    candidate_by_id = {}
    if type(binding_result) is ResonantOperatorCandidateBindingResult and (
        binding_result.binding_set is not None
    ):
        candidate_by_id = {
            candidate.candidate_binding_id: candidate
            for candidate in binding_result.binding_set.candidates
        }
        if trail.source_event_id != binding_result.binding_set.source_event_id:
            issues.append(issue("source_event_id", "binding_set_mismatch"))
        if trail.projection_id != binding_result.binding_set.projection_id:
            issues.append(issue("projection_id", "binding_set_mismatch"))
        if trail.binding_set_id != binding_result.binding_set.binding_set_id:
            issues.append(issue("binding_set_id", "binding_set_mismatch"))
        if any(
            binding_id not in candidate_by_id
            for binding_id in trail.participating_binding_ids
        ):
            issues.append(issue("participating_binding_ids", "unknown_binding"))
        if len(trail.participating_binding_ids) > 1:
            if len(trail.participating_binding_ids) != 2:
                issues.append(issue("participating_binding_ids", "only_explicit_pair_allowed"))
            else:
                parent = candidate_by_id.get(trail.participating_binding_ids[0])
                child = candidate_by_id.get(trail.participating_binding_ids[1])
                if parent is None or child is None:
                    issues.append(issue("participating_binding_ids", "unknown_pair"))
                elif (
                    child.candidate_binding_id not in parent.possible_child_binding_ids
                    or parent.candidate_binding_id
                    not in child.possible_parent_binding_ids
                ):
                    issues.append(issue("participating_binding_ids", "nonreciprocal_pair"))
                elif child.candidate_binding_id in parent.competing_candidate_binding_ids:
                    issues.append(issue("participating_binding_ids", "competing_pair_coapplied"))

    registry_record = registry if type(registry) is SymbolicGrammarOperatorRegistry else None
    policy_record = policy if type(policy) is PhaseTrailConstructionPolicy else None
    if registry_record is not None:
        if trail.grammar_registry_id != registry_record.registry_id:
            issues.append(issue("grammar_registry_id", "registry_mismatch"))
        if trail.grammar_registry_version != registry_record.registry_version:
            issues.append(issue("grammar_registry_version", "registry_mismatch"))
    if policy_record is not None and trail.policy_id != policy_record.policy_id:
        issues.append(issue("policy_id", "policy_mismatch"))

    initial_identity = trail.states[0].identity_field_id
    preserved_spans = trail.states[0].preserved_source_span_ids
    for index, state in enumerate(trail.states):
        report = validate_candidate_symbolic_field_state(state)
        issues.extend(
            issue(f"states[{index}].{item.field}", item.code, item.detail)
            for item in report.issues
        )
        if state.phase_trail_id != trail.phase_trail_id:
            issues.append(issue(f"states[{index}].phase_trail_id", "trail_mismatch"))
        if state.phase_trail_set_id != trail.phase_trail_set_id:
            issues.append(issue(f"states[{index}].phase_trail_set_id", "set_mismatch"))
        if state.initial_state_id != trail.initial_state_id:
            issues.append(issue(f"states[{index}].initial_state_id", "initial_mismatch"))
        if state.identity_field_id != initial_identity:
            issues.append(issue(f"states[{index}].identity_field_id", "identity_changed"))
        if state.preserved_source_span_ids != preserved_spans:
            issues.append(issue(f"states[{index}].preserved_source_span_ids", "spans_changed"))
        if index > 0:
            if state.predecessor_state_id != trail.states[index - 1].state_id:
                issues.append(issue(f"states[{index}].predecessor_state_id", "chain_mismatch"))
            if state.state_ordinal != index:
                issues.append(issue(f"states[{index}].state_ordinal", "ordinal_mismatch"))

    for index, application in enumerate(trail.applications):
        candidate = candidate_by_id.get(application.candidate_binding_id)
        definition = (
            grammar_operator_for_key(application.candidate_operator_key, registry_record)
            if registry_record is not None else None
        )
        report = validate_candidate_grammar_operator_application(
            application,
            candidate=candidate,
            definition=definition,
            input_state=trail.states[index],
            successor_state=trail.states[index + 1],
        )
        issues.extend(
            issue(f"applications[{index}].{item.field}", item.code, item.detail)
            for item in report.issues
        )
        if application.phase_trail_id != trail.phase_trail_id:
            issues.append(issue(f"applications[{index}].phase_trail_id", "trail_mismatch"))
        if application.application_ordinal != index:
            issues.append(issue(f"applications[{index}].application_ordinal", "ordinal_mismatch"))
        if application.candidate_binding_id != trail.participating_binding_ids[index]:
            issues.append(issue(f"applications[{index}].candidate_binding_id", "plan_order_mismatch"))
        if application.structural_effect.value != trail.planned_effect_codes[index]:
            issues.append(issue(f"applications[{index}].structural_effect", "plan_effect_mismatch"))
        planned_phase = trail.planned_phase_affinity_values[index]
        if planned_phase and planned_phase not in application.phase_after_values:
            issues.append(issue(f"applications[{index}].phase_after_values", "plan_phase_mismatch"))

    final = trail.states[-1]
    if trail.completion_status is not final.completion_status:
        issues.append(issue("completion_status", "final_state_mismatch"))
    for field_name in (
        "unresolved_branch_ids",
        "conflict_branch_ids",
        "suspended_branch_ids",
        "containment_condition_codes",
        "drift_indicator_codes",
        "entropy_effect_codes",
    ):
        if getattr(trail, field_name) != getattr(final, field_name):
            issues.append(issue(field_name, "final_state_mismatch"))
    if trail.non_progress_reason is PhaseTrailNonProgressReason.NONE and (
        final.unresolved_branch_ids or not final.structural_progression_allowed
    ):
        issues.append(issue("non_progress_reason", "reason_required"))
    return _report(issues)


def _expected_set_status(
    trails: tuple[CandidateResonantPhaseTrail, ...],
) -> PhaseTrailConstructionStatus:
    if not trails:
        return PhaseTrailConstructionStatus.ZERO_PHASE_TRAILS
    if any(
        any(
            value.startswith("resonant_operator_binding_candidate:")
            for value in trail.conflict_branch_ids
        )
        for trail in trails
    ):
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
            application.application_status is CandidateApplicationStatus.DRIFT_CONTAINED
            for application in trail.applications
        )
    ):
        return PhaseTrailConstructionStatus.DRIFT_CONTAINED
    return PhaseTrailConstructionStatus.INCOMPLETE_PHASE_TRAIL


def validate_candidate_resonant_phase_trail_set(
    trail_set: object,
    *,
    binding_result: object = None,
    registry: object = None,
    policy: object = None,
    limits: object = None,
) -> ValidationReport:
    if type(trail_set) is not CandidateResonantPhaseTrailSet:
        return _report([issue("trail_set", "invalid_record_type")])
    issues = _base_issues(trail_set)
    if trail_set.phase_trail_set_schema_id != PHASE_TRAIL_SET_SCHEMA_ID:
        issues.append(issue("phase_trail_set_schema_id", "set_schema_id_mismatch"))
    if trail_set.phase_trail_set_id != trail_set.expected_id():
        issues.append(issue("phase_trail_set_id", "stable_identifier_mismatch"))
    if type(trail_set.trails) is not tuple:
        issues.append(issue("trails", "tuple_required"))
        return _report(issues)
    if trail_set.trail_count != len(trail_set.trails):
        issues.append(issue("trail_count", "count_mismatch"))
    if len({trail.phase_trail_id for trail in trail_set.trails}) != len(trail_set.trails):
        issues.append(issue("trails", "duplicate_trail_identity"))
    if trail_set.trails and trail_set.status != _expected_set_status(trail_set.trails):
        issues.append(issue("status", "status_mismatch"))
    if not trail_set.trails and trail_set.status not in {
        PhaseTrailConstructionStatus.ZERO_PHASE_TRAILS,
        PhaseTrailConstructionStatus.UNSUPPORTED_OPERATOR_SEQUENCE,
    }:
        issues.append(issue("status", "empty_set_status_mismatch"))
    expected_counts = {
        "complete_trail_count": sum(
            trail.completion_status is PhaseTrailCompletionStatus.COMPLETE_CANDIDATE
            for trail in trail_set.trails
        ),
        "incomplete_trail_count": sum(
            trail.completion_status in {
                PhaseTrailCompletionStatus.OPEN_UNRESOLVED,
                PhaseTrailCompletionStatus.SEALED_UNPROVEN,
            }
            for trail in trail_set.trails
        ),
        "conflicting_trail_count": sum(bool(trail.conflict_branch_ids) for trail in trail_set.trails),
        "contained_trail_count": sum(
            trail.completion_status is PhaseTrailCompletionStatus.CONTAINED_PRESERVED
            for trail in trail_set.trails
        ),
        "suspended_trail_count": sum(
            trail.completion_status is PhaseTrailCompletionStatus.SUSPENDED_PRESERVED
            for trail in trail_set.trails
        ),
        "rejected_trail_count": sum(
            trail.completion_status is PhaseTrailCompletionStatus.REJECTED_NON_PROGRESS
            for trail in trail_set.trails
        ),
        "unresolved_branch_count": len({
            value for trail in trail_set.trails for value in trail.unresolved_branch_ids
        }),
        "conflict_branch_count": len({
            value for trail in trail_set.trails for value in trail.conflict_branch_ids
        }),
    }
    for field_name, expected in expected_counts.items():
        if getattr(trail_set, field_name) != expected:
            issues.append(issue(field_name, "count_mismatch"))
    for name in (
        "candidate_plurality_preserved",
        "immutable_successor_law_enforced",
    ):
        if getattr(trail_set, name) is not True:
            issues.append(issue(name, "must_remain_true"))
    if trail_set.fixed_phase_sequence_forced is not False:
        issues.append(issue("fixed_phase_sequence_forced", "must_remain_false"))
    if trail_set.arbitrary_neighbor_composition_performed is not False:
        issues.append(
            issue("arbitrary_neighbor_composition_performed", "must_remain_false")
        )
    if trail_set.selected_trail_id is not None:
        issues.append(issue("selected_trail_id", "must_remain_none"))
    issues.extend(
        _all_false(
            trail_set,
            (
                "selected_meaning",
                "permission_authority_available",
                "route_authority_available",
                "tool_authority_available",
                "memory_authority_available",
                "action_authority_available",
                "delivery_authority_available",
                "hidden_fallback_allowed",
            ),
        )
    )
    if type(binding_result) is ResonantOperatorCandidateBindingResult and (
        binding_result.binding_set is not None
    ):
        binding_set = binding_result.binding_set
        for field_name in (
            "source_event_id",
            "source_sha256",
            "projection_id",
            "source_field_schema_id",
            "binding_set_id",
        ):
            if getattr(trail_set, field_name) != getattr(binding_set, field_name):
                issues.append(issue(field_name, "binding_set_mismatch"))
    if type(registry) is SymbolicGrammarOperatorRegistry:
        if trail_set.grammar_registry_id != registry.registry_id:
            issues.append(issue("grammar_registry_id", "registry_mismatch"))
        if trail_set.grammar_registry_version != registry.registry_version:
            issues.append(issue("grammar_registry_version", "registry_mismatch"))
    if type(policy) is PhaseTrailConstructionPolicy and trail_set.policy_id != policy.policy_id:
        issues.append(issue("policy_id", "policy_mismatch"))
    if type(limits) is PhaseTrailConstructionLimits:
        if trail_set.limits_id != limits.limits_id:
            issues.append(issue("limits_id", "limits_mismatch"))
        if trail_set.trail_count > limits.max_trails:
            issues.append(issue("trail_count", "limit_exceeded"))
    for index, trail in enumerate(trail_set.trails):
        if trail.phase_trail_set_id != trail_set.phase_trail_set_id:
            issues.append(issue(f"trails[{index}].phase_trail_set_id", "set_mismatch"))
        report = validate_candidate_resonant_phase_trail(
            trail,
            binding_result=binding_result,
            registry=registry,
            policy=policy,
        )
        issues.extend(
            issue(f"trails[{index}].{item.field}", item.code, item.detail)
            for item in report.issues
        )
    return _report(issues)


def validate_candidate_resonant_phase_trail_result(
    result: object,
    projection_result: object,
    binding_result: object,
    registry: object,
) -> ValidationReport:
    if type(result) is not CandidateResonantPhaseTrailResult:
        return _report([issue("result", "invalid_record_type")])
    issues = _base_issues(result)
    if result.result_schema_id != PHASE_TRAIL_RESULT_SCHEMA_ID:
        issues.append(issue("result_schema_id", "result_schema_id_mismatch"))
    if result.result_id != result.expected_id():
        issues.append(issue("result_id", "stable_identifier_mismatch"))
    issues.extend(
        _all_false(
            result,
            (
                "filesystem_read_performed",
                "filesystem_write_performed",
                "network_access_performed",
                "environment_access_performed",
                "memory_read_performed",
                "memory_write_performed",
                "route_registration_performed",
                "tool_routing_performed",
                "core_rsoc_operator_application_performed",
                "selected_trail",
                "selected_phase",
                "selected_meaning",
                "permission_inferred",
                "action_performed",
                "delivery_performed",
            ),
        )
    )
    if result.policy is not None:
        report = validate_phase_trail_construction_policy(result.policy)
        issues.extend(
            issue(f"policy.{item.field}", item.code, item.detail)
            for item in report.issues
        )
    if result.limits is not None:
        report = validate_phase_trail_construction_limits(result.limits)
        issues.extend(
            issue(f"limits.{item.field}", item.code, item.detail)
            for item in report.issues
        )
    if type(projection_result) is SourceFieldProjectionResult:
        if result.source_event_id and result.source_event_id != projection_result.source_event_id:
            issues.append(issue("source_event_id", "projection_result_mismatch"))
        if result.source_sha256 and result.source_sha256 != projection_result.source_sha256:
            issues.append(issue("source_sha256", "projection_result_mismatch"))
    if type(binding_result) is ResonantOperatorCandidateBindingResult:
        if result.binding_set_id and binding_result.binding_set is not None and (
            result.binding_set_id != binding_result.binding_set.binding_set_id
        ):
            issues.append(issue("binding_set_id", "binding_result_mismatch"))
    if type(registry) is SymbolicGrammarOperatorRegistry and result.grammar_registry_id:
        if result.grammar_registry_id != registry.registry_id:
            issues.append(issue("grammar_registry_id", "registry_mismatch"))
    if result.phase_trail_set_created:
        if result.phase_trail_set is None:
            issues.append(issue("phase_trail_set", "required_when_created"))
        elif result.policy is None or result.limits is None:
            issues.append(issue("phase_trail_set", "policy_and_limits_required"))
        else:
            report = validate_candidate_resonant_phase_trail_set(
                result.phase_trail_set,
                binding_result=binding_result,
                registry=registry,
                policy=result.policy,
                limits=result.limits,
            )
            issues.extend(
                issue(f"phase_trail_set.{item.field}", item.code, item.detail)
                for item in report.issues
            )
            if result.status is not result.phase_trail_set.status:
                issues.append(issue("status", "trail_set_status_mismatch"))
    elif result.phase_trail_set is not None:
        issues.append(issue("phase_trail_set", "must_be_none_when_not_created"))
    if result.status in {
        PhaseTrailConstructionStatus.MALFORMED_PHASE_TRAIL,
        PhaseTrailConstructionStatus.PHASE_TRAIL_LIMIT_EXCEEDED,
        PhaseTrailConstructionStatus.PHASE_TRAIL_CONSTRUCTION_FAILED,
    } and result.phase_trail_set_created:
        issues.append(issue("phase_trail_set_created", "must_be_false_for_status"))
    return _report(issues)
