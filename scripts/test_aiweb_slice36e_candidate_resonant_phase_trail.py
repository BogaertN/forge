#!/usr/bin/env python3
"""Behavior and adversarial tests for Slice 36E."""

from __future__ import annotations

import builtins
from contextlib import ExitStack
from dataclasses import FrozenInstanceError, fields, replace
import os
from pathlib import Path
import socket
import sys
import urllib.request
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aiweb_language_core_bootstrap.candidate_resonant_phase_trail import (
    ABSOLUTE_MAX_PHASE_TRAILS,
    CandidateApplicationStatus,
    CandidateGrammarOperatorApplication,
    CandidatePhaseStatus,
    CandidateResonantPhaseTrail,
    CandidateSymbolicFieldState,
    PhaseTrailCompletionStatus,
    PhaseTrailConstructionStatus,
    PhaseTrailNonProgressReason,
    build_default_phase_trail_policy,
    build_phase_trail_limits,
    construct_candidate_resonant_phase_trails,
    default_phase_trail_limits,
    validate_candidate_grammar_operator_application,
    validate_candidate_resonant_phase_trail,
    validate_candidate_resonant_phase_trail_result,
    validate_candidate_resonant_phase_trail_set,
    validate_candidate_symbolic_field_state,
    validate_phase_trail_construction_limits,
    validate_phase_trail_construction_policy,
)
from aiweb_language_core_bootstrap.input_event_custody import capture_input_event
from aiweb_language_core_bootstrap.resonant_operator_candidate_binding import (
    bind_resonant_operator_candidates,
)
from aiweb_language_core_bootstrap.source_field_projection import (
    SourceFieldProjectionStatus,
    project_source_field,
)
from aiweb_language_core_bootstrap.symbolic_grammar_operator_registry import (
    GrammarOperatorEffect,
    build_default_symbolic_grammar_operator_registry,
)

checks = 0


def check(condition: bool, label: str) -> None:
    global checks
    if not condition:
        raise AssertionError(label)
    checks += 1


def forbidden(*args: object, **kwargs: object) -> object:
    raise AssertionError("external side effect attempted")


def pipeline(text: str, sequence: int):
    custody = capture_input_event(
        text,
        source_id="fixture.user",
        channel_id="fixture.chat",
        sequence_number=sequence,
    )
    check(custody.event is not None, f"custody event {sequence}")
    projection = project_source_field(custody.event)
    check(projection.projection is not None, f"projection {sequence}")
    binding = bind_resonant_operator_candidates(projection)
    check(binding.binding_set is not None, f"binding set {sequence}")
    trails = construct_candidate_resonant_phase_trails(projection, binding)
    return projection, binding, trails


registry = build_default_symbolic_grammar_operator_registry()
policy = build_default_phase_trail_policy()
limits = default_phase_trail_limits()

# Policy and limits are explicit, deterministic and closed.
check(policy.policy_id == policy.expected_id(), "policy stable id")
check(validate_phase_trail_construction_policy(policy).ok, "policy validates")
check(policy.single_binding_trails_required, "single trails required")
check(policy.explicit_parent_child_trails_allowed, "explicit pair allowed")
check(not policy.arbitrary_neighbor_composition_allowed, "no arbitrary composition")
check(not policy.competing_candidates_may_coapply, "no competitor coapplication")
check(policy.branch_every_allowed_effect, "all effects branched")
check(policy.branch_every_explicit_phase_affinity, "all affinities branched")
check(not policy.fixed_phase_sequence_required, "no fixed phase sequence")
check(policy.advisory_phase_affinity_only, "affinity advisory only")
check(policy.immutable_successor_required, "immutable successor required")
for name in (
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
):
    check(getattr(policy, name) is False, f"policy boundary {name}")
check(limits == default_phase_trail_limits(), "default limits deterministic")
check(limits.limits_id == limits.expected_id(), "limits stable id")
check(validate_phase_trail_construction_limits(limits).ok, "limits validate")
check(
    not validate_phase_trail_construction_limits(
        build_phase_trail_limits(max_trails=ABSOLUTE_MAX_PHASE_TRAILS + 1)
    ).ok,
    "oversize trail limit rejected",
)

# Governing example.
projection_result, binding_result, result = pipeline("Do not install it.", 10)
trail_set = result.phase_trail_set
assert projection_result.projection is not None
assert binding_result.binding_set is not None
assert trail_set is not None
check(result.status is PhaseTrailConstructionStatus.MULTIPLE_PHASE_TRAILS, "example multiple status")
check(result.result_id == result.expected_id(), "result stable id")
check(trail_set.phase_trail_set_id == trail_set.expected_id(), "set stable id")
check(trail_set.trail_count == 8, "example eight lawful trails")
check(trail_set.candidate_plurality_preserved, "plurality preserved")
check(trail_set.immutable_successor_law_enforced, "successor law enforced")
check(not trail_set.fixed_phase_sequence_forced, "phase sequence not forced")
check(not trail_set.arbitrary_neighbor_composition_performed, "no arbitrary composition performed")
check(trail_set.selected_trail_id is None, "no selected trail")
check(
    validate_candidate_resonant_phase_trail_set(
        trail_set,
        binding_result=binding_result,
        registry=registry,
        policy=policy,
        limits=limits,
    ).ok,
    "example set validates",
)
check(
    validate_candidate_resonant_phase_trail_result(
        result,
        projection_result,
        binding_result,
        registry,
    ).ok,
    "example result validates",
)

candidate_by_id = {
    candidate.candidate_binding_id: candidate
    for candidate in binding_result.binding_set.candidates
}
operator_by_binding = {
    candidate.candidate_binding_id: candidate.candidate_operator_key
    for candidate in binding_result.binding_set.candidates
}

single_effects: dict[str, set[str]] = {}
compound_trails = []
for trail_index, trail in enumerate(trail_set.trails):
    check(trail.phase_trail_id == trail.expected_id(), f"trail stable id {trail_index}")
    check(
        validate_candidate_resonant_phase_trail(
            trail,
            binding_result=binding_result,
            registry=registry,
            policy=policy,
        ).ok,
        f"trail validates {trail_index}",
    )
    check(len(trail.states) == len(trail.applications) + 1, f"state chain length {trail_index}")
    check(trail.states[0].state_id == trail.initial_state_id, f"initial state link {trail_index}")
    check(trail.states[-1].state_id == trail.final_state_id, f"final state link {trail_index}")
    check(trail.recursive_depth == len(trail.applications), f"recursive depth {trail_index}")
    check(trail.immutable_transition_chain_complete, f"immutable chain {trail_index}")
    check(trail.source_ancestry_complete, f"source ancestry {trail_index}")
    check(trail.identity_field_preserved, f"identity preserved {trail_index}")
    check(trail.source_spans_preserved, f"spans preserved {trail_index}")
    check(trail.candidate_only and not trail.selected_trail, f"candidate only {trail_index}")
    check(trail.core_rsoc_operator_applications == 0, f"no RSOC application {trail_index}")
    if len(trail.participating_binding_ids) == 1:
        binding_id = trail.participating_binding_ids[0]
        single_effects.setdefault(operator_by_binding[binding_id], set()).add(
            trail.planned_effect_codes[0]
        )
    else:
        compound_trails.append(trail)
        check(len(trail.participating_binding_ids) == 2, f"only explicit pairs {trail_index}")
        check(
            [operator_by_binding[value] for value in trail.participating_binding_ids]
            == ["grammar_prohibition", "grammar_negation"],
            f"only explicit prohibition-negation pair {trail_index}",
        )
    initial_snapshot = trail.states[0].to_dict()
    for state_index, state in enumerate(trail.states):
        check(state.state_id == state.expected_id(), f"state stable id {trail_index}:{state_index}")
        check(validate_candidate_symbolic_field_state(state).ok, f"state validates {trail_index}:{state_index}")
        check(state.prior_state_mutated is False, f"state no mutation flag {trail_index}:{state_index}")
        check(state.core_rsoc_operator_application_count == 0, f"state no RSOC {trail_index}:{state_index}")
        check(state.identity_field_id == trail.states[0].identity_field_id, f"identity invariant {trail_index}:{state_index}")
        check(state.preserved_source_span_ids == trail.states[0].preserved_source_span_ids, f"span invariant {trail_index}:{state_index}")
        if state_index:
            check(state.predecessor_state_id == trail.states[state_index - 1].state_id, f"predecessor state {trail_index}:{state_index}")
            check(state.predecessor_application_id == trail.applications[state_index - 1].application_id, f"predecessor application {trail_index}:{state_index}")
    check(trail.states[0].to_dict() == initial_snapshot, f"initial state unchanged {trail_index}")
    for app_index, application in enumerate(trail.applications):
        candidate = candidate_by_id[application.candidate_binding_id]
        definition = next(
            value
            for value in registry.operators
            if value.operator_key == candidate.candidate_operator_key
        )
        check(application.application_id == application.expected_id(), f"application stable id {trail_index}:{app_index}")
        check(
            validate_candidate_grammar_operator_application(
                application,
                candidate=candidate,
                definition=definition,
                input_state=trail.states[app_index],
                successor_state=trail.states[app_index + 1],
            ).ok,
            f"application validates {trail_index}:{app_index}",
        )
        check(application.successor_created, f"successor created {trail_index}:{app_index}")
        check(not application.prior_state_mutated, f"no mutation {trail_index}:{app_index}")
        check(application.core_rsoc_operator_key is None, f"no RSOC key {trail_index}:{app_index}")
        check(not application.core_rsoc_operator_applied, f"no RSOC apply {trail_index}:{app_index}")
        check(not application.selected_phase, f"no selected phase {trail_index}:{app_index}")
        check(not application.selected_meaning, f"no meaning {trail_index}:{app_index}")
        check(not application.permission_inferred, f"no permission {trail_index}:{app_index}")
        check(not application.route_created, f"no route {trail_index}:{app_index}")
        check(not application.action_performed, f"no action {trail_index}:{app_index}")

check(single_effects["grammar_prohibition"] == {"constrain", "reject"}, "prohibition branches every effect")
check(single_effects["grammar_negation"] == {"constrain"}, "negation effect")
check(single_effects["grammar_reference"] == {"propose"}, "reference effect")
check(single_effects["grammar_boundary"] == {"constrain"}, "boundary effect")
check(single_effects["fbsc_loop_seal"] == {"seal"}, "loop seal effect")
check(len(compound_trails) == 2, "two parent-child effect branches")
check(
    {trail.planned_effect_codes for trail in compound_trails}
    == {("constrain", "constrain"), ("reject", "constrain")},
    "compound effect plurality",
)
reject_compound = next(
    trail for trail in compound_trails if trail.planned_effect_codes[0] == "reject"
)
check(len(reject_compound.applications) == 1, "reject stops successor progression")
check(
    reject_compound.participating_binding_ids[1]
    in reject_compound.suspended_branch_ids,
    "unapplied child preserved as suspended branch",
)
loop_trail = next(
    trail
    for trail in trail_set.trails
    if len(trail.participating_binding_ids) == 1
    and operator_by_binding[trail.participating_binding_ids[0]] == "fbsc_loop_seal"
)
check(loop_trail.applications[0].phase_after_values == ("Φ9",), "loop seal advisory phase")
check(
    loop_trail.applications[0].phase_after_status
    is CandidatePhaseStatus.EXPLICIT_ADVISORY_CANDIDATE,
    "phase remains candidate",
)
check(
    loop_trail.completion_status is PhaseTrailCompletionStatus.SEALED_UNPROVEN,
    "seal does not prove completion",
)
check(
    loop_trail.non_progress_reason
    is PhaseTrailNonProgressReason.PHASE_TRANSITION_LAW_NOT_INSTALLED,
    "seal non-progress reason",
)
for trail in trail_set.trails:
    keys = [operator_by_binding[value] for value in trail.participating_binding_ids]
    check(not ({"grammar_boundary", "fbsc_loop_seal"} <= set(keys)), "coincident terminal candidates not arbitrarily composed")
    check(not ({"grammar_reference", "grammar_boundary"} <= set(keys)), "neighbor candidates not arbitrarily composed")

# Material quotation ambiguity produces separate conflicting branches.
quote_projection, quote_binding, quote_result = pipeline('"Alpha"', 20)
quote_set = quote_result.phase_trail_set
assert quote_set is not None and quote_binding.binding_set is not None
check(quote_result.status is PhaseTrailConstructionStatus.CONFLICTING_PHASE_TRAILS, "quote conflict status")
check(quote_set.trail_count == 4, "four quote trails")
check(quote_set.conflicting_trail_count == 4, "four conflicting trails")
check(quote_set.selected_trail_id is None, "quote no selected trail")
quote_variants = {
    candidate.candidate_binding_id: candidate.candidate_variant_code
    for candidate in quote_binding.binding_set.candidates
}
check(
    {quote_variants[trail.participating_binding_ids[0]] for trail in quote_set.trails}
    == {
        "possible_direct_quotation",
        "possible_quoted_name",
        "possible_quoted_title",
        "possible_literal_string",
    },
    "quote variants all preserved",
)
for trail in quote_set.trails:
    check(len(trail.participating_binding_ids) == 1, "competitors never coapply")
    check(trail.planned_effect_codes == ("contain",), "quote containment effect")
    check(trail.completion_status is PhaseTrailCompletionStatus.CONTAINED_PRESERVED, "quote contained state")
    check(len([value for value in trail.conflict_branch_ids if value.startswith("resonant_operator_binding_candidate:")]) == 3, "three competing branches retained")

# Incomplete quotation is incomplete, not materially conflicting or repaired.
incomplete_projection, incomplete_binding, incomplete_result = pipeline('"Alpha', 21)
incomplete_set = incomplete_result.phase_trail_set
assert incomplete_set is not None
check(incomplete_result.status is PhaseTrailConstructionStatus.INCOMPLETE_PHASE_TRAIL, "incomplete quote status")
check(incomplete_set.trail_count == 1, "incomplete quote one trail")
check(incomplete_set.conflicting_trail_count == 1, "conflicting evidence retained")
check(incomplete_set.conflict_branch_count >= 1, "incomplete evidence count")
check(not any(value.startswith("resonant_operator_binding_candidate:") for value in incomplete_set.trails[0].conflict_branch_ids), "no invented competing candidate")
check(incomplete_set.trails[0].completion_status is PhaseTrailCompletionStatus.CONTAINED_PRESERVED, "incomplete quote preserved contained")

# Suspension is preserved as a branch and never discarded.
question_projection, question_binding, question_result = pipeline("Why?", 30)
question_set = question_result.phase_trail_set
assert question_set is not None and question_binding.binding_set is not None
check(question_result.status is PhaseTrailConstructionStatus.MULTIPLE_PHASE_TRAILS, "question multiple trails")
check(question_set.trail_count == 2, "question two trails")
check(question_set.suspended_trail_count == 1, "one suspended trail")
suspended = next(
    trail
    for trail in question_set.trails
    if trail.completion_status is PhaseTrailCompletionStatus.SUSPENDED_PRESERVED
)
check(suspended.applications[0].structural_effect is GrammarOperatorEffect.SUSPEND, "suspension effect")
check(suspended.states[-1].suspended, "suspended state retained")
check(not suspended.states[-1].structural_progression_allowed, "suspended progression held")

# No candidate means no fabricated phase trail, including action-only signals.
for sequence, text in ((40, "ordinary surface"), (41, "install")):
    projection_i, binding_i, result_i = pipeline(text, sequence)
    current = result_i.phase_trail_set
    assert current is not None
    check(result_i.status is PhaseTrailConstructionStatus.ZERO_PHASE_TRAILS, f"zero status {text}")
    check(current.trail_count == 0 and current.trails == (), f"zero trails {text}")
    check(current.selected_trail_id is None, f"zero no selection {text}")
    check(
        validate_candidate_resonant_phase_trail_result(
            result_i,
            projection_i,
            binding_i,
            registry,
        ).ok,
        f"zero result validates {text}",
    )

# Unsupported source is held without partial trail output.
partial_projection, partial_binding, partial_result = pipeline("not \ue000.", 50)
check(
    partial_projection.status
    is SourceFieldProjectionStatus.SOURCE_FIELD_PARTIALLY_UNSUPPORTED,
    "partial source fixture",
)
check(
    partial_result.status
    is PhaseTrailConstructionStatus.UNSUPPORTED_OPERATOR_SEQUENCE,
    "partial source held",
)
check(partial_result.phase_trail_set is not None, "partial empty set retained")
check(partial_result.phase_trail_set.trail_count == 0, "partial no trails")

# Limits reject the full construction without truncating or selecting.
limited = construct_candidate_resonant_phase_trails(
    quote_projection,
    quote_binding,
    limits=build_phase_trail_limits(max_trails=3),
)
check(
    limited.status is PhaseTrailConstructionStatus.PHASE_TRAIL_LIMIT_EXCEEDED,
    "trail limit status",
)
check(not limited.phase_trail_set_created and limited.phase_trail_set is None, "limit no partial set")

# Malformed predecessor records remain typed failures.
malformed_projection = construct_candidate_resonant_phase_trails(object(), binding_result)
check(malformed_projection.status is PhaseTrailConstructionStatus.MALFORMED_PHASE_TRAIL, "malformed projection typed")
malformed_binding = construct_candidate_resonant_phase_trails(projection_result, object())
check(malformed_binding.status is PhaseTrailConstructionStatus.MALFORMED_PHASE_TRAIL, "malformed binding typed")
malformed_policy = construct_candidate_resonant_phase_trails(
    projection_result,
    binding_result,
    policy=object(),
)
check(malformed_policy.status is PhaseTrailConstructionStatus.MALFORMED_PHASE_TRAIL, "malformed policy typed")

# Determinism, frozen records and tamper detection.
repeat_a = construct_candidate_resonant_phase_trails(projection_result, binding_result)
repeat_b = construct_candidate_resonant_phase_trails(projection_result, binding_result)
check(repeat_a == repeat_b, "construction deterministic")
try:
    repeat_a.status = PhaseTrailConstructionStatus.PHASE_TRAIL_CONSTRUCTION_FAILED
    check(False, "result frozen")
except (FrozenInstanceError, AttributeError):
    check(True, "result frozen")
first_trail = repeat_a.phase_trail_set.trails[0]
tampered_state = replace(first_trail.states[-1], identity_field_id="altered")
check(not validate_candidate_symbolic_field_state(tampered_state).ok, "state tamper rejected")
tampered_application = replace(first_trail.applications[0], core_rsoc_operator_applied=True)
check(not validate_candidate_grammar_operator_application(tampered_application).ok, "RSOC tamper rejected")
tampered_trail = replace(first_trail, selected_trail=True)
check(not validate_candidate_resonant_phase_trail(tampered_trail).ok, "trail selection tamper rejected")
tampered_set = replace(repeat_a.phase_trail_set, selected_trail_id="fake")
check(not validate_candidate_resonant_phase_trail_set(tampered_set).ok, "set selection tamper rejected")

# No numeric confidence or entropy mutation surface is introduced.
for cls in (
    CandidateSymbolicFieldState,
    CandidateGrammarOperatorApplication,
    CandidateResonantPhaseTrail,
):
    for field in fields(cls):
        check(field.name not in {"score", "probability", "likelihood", "confidence_score", "rank"}, f"no score field {cls.__name__}.{field.name}")
        check(field.type is not float, f"no float field {cls.__name__}.{field.name}")

# Construction does not consult files, network, environment, memory or hidden services.
with ExitStack() as stack:
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(Path, "read_text", forbidden))
    stack.enter_context(patch.object(Path, "read_bytes", forbidden))
    stack.enter_context(patch.object(Path, "write_text", forbidden))
    stack.enter_context(patch.object(Path, "write_bytes", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    stack.enter_context(patch.object(os, "getenv", forbidden))
    protected = construct_candidate_resonant_phase_trails(
        projection_result,
        binding_result,
    )
check(protected.status is PhaseTrailConstructionStatus.MULTIPLE_PHASE_TRAILS, "side-effect blocked construction succeeds")

# Every result remains structurally candidate-only and no-action safe.
for sequence, text in enumerate((
    "Do not install it.",
    '"Name"?',
    "This!",
    "run that.",
    "not not it.",
), 100):
    projection_i, binding_i, result_i = pipeline(text, sequence)
    check(result_i.source_event_id == projection_i.source_event_id, f"source event preserved {sequence}")
    check(result_i.source_sha256 == projection_i.source_sha256, f"source hash preserved {sequence}")
    for name in (
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
    ):
        check(getattr(result_i, name) is False, f"result authority false {sequence} {name}")

print(f"SLICE 36E BEHAVIOR TEST: PASS ({checks} checks)")
