#!/usr/bin/env python3
"""Behavior and adversarial verification for Slice 36F."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import replace
import builtins
import json
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
    construct_candidate_resonant_phase_trails,
)
from aiweb_language_core_bootstrap.input_event_custody import (
    capture_input_event,
)
from aiweb_language_core_bootstrap.resonant_operator_candidate_binding import (
    bind_resonant_operator_candidates,
)
from aiweb_language_core_bootstrap.scope_attachment_reference_constraints import (
    ABSOLUTE_MAX_ACTIVE_CONTEXT_ENTRIES,
    ABSOLUTE_MAX_GOVERNED_SPANS_PER_OCCURRENCE,
    ABSOLUTE_MAX_REFERENCE_CANDIDATES,
    ABSOLUTE_MAX_SCOPE_OCCURRENCES,
    AttachmentStatus,
    AuthorityConversionGuard,
    ContextObjectKind,
    ContextOperationalStatus,
    ContextPositionTag,
    ReferenceAnalysisStatus,
    ScopeConstraintStatus,
    ScopeResponsibility,
    ScopeRuleActivationStatus,
    apply_scope_attachment_reference_constraints,
    authority_conversion_guards,
    build_active_context_entry,
    build_active_context_registry,
    build_default_scope_attachment_rules,
    build_default_scope_constraint_policy,
    build_scope_constraint_limits,
    default_scope_constraint_limits,
    validate_active_context_entry,
    validate_active_context_registry,
    validate_default_scope_attachment_rules,
    validate_governed_span_candidate,
    validate_reference_analysis,
    validate_reference_context_candidate,
    validate_scope_attachment_occurrence,
    validate_scope_attachment_reference_constraint_result,
    validate_scope_attachment_reference_constraint_set,
    validate_scope_attachment_rule,
    validate_scope_constrained_candidate_trail,
    validate_scope_constraint_limits,
    validate_scope_constraint_policy,
)
from aiweb_language_core_bootstrap.source_field_projection import (
    project_source_field,
)


checks = 0


def check(condition: object, label: str) -> None:
    global checks
    checks += 1
    if condition is not True:
        raise AssertionError(label)


def forbidden(*args: object, **kwargs: object) -> object:
    raise AssertionError("external side effect attempted")


def pipeline(
    text: str,
    sequence: int,
    *,
    context=None,
    requested_dependencies: tuple[str, ...] = (),
):
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
    check(binding.binding_set is not None, f"binding {sequence}")
    trails = construct_candidate_resonant_phase_trails(
        projection,
        binding,
    )
    result = apply_scope_attachment_reference_constraints(
        projection,
        binding,
        trails,
        active_context_registry=context,
        requested_context_dependencies=requested_dependencies,
    )
    return projection, binding, trails, result


policy = build_default_scope_constraint_policy()
limits = default_scope_constraint_limits()
rules = build_default_scope_attachment_rules()
guards = authority_conversion_guards()

check(policy.policy_id == policy.expected_id(), "policy stable identity")
check(validate_scope_constraint_policy(policy).ok, "policy validates")
check(policy.explicit_context_only, "explicit context only")
check(policy.active_context_must_be_immutable, "immutable context required")
check(policy.exact_reference_match_only, "exact reference match only")
check(policy.preserve_all_lawful_attachments, "all attachments preserved")
for field in (
    "select_attachment_authorized",
    "resolve_reference_authorized",
    "concept_authority_available",
    "predicate_authority_available",
    "capability_authority_available",
    "route_authority_available",
    "tool_authority_available",
    "memory_search_authorized",
    "file_search_authorized",
    "repository_history_search_authorized",
    "web_search_authorized",
    "embedding_authorized",
    "language_model_authorized",
    "similarity_authorized",
    "nearest_object_selection_authorized",
    "convenience_selection_authorized",
    "capability_influence_authorized",
):
    check(getattr(policy, field) is False, f"policy boundary {field}")

check(guards == tuple(AuthorityConversionGuard), "complete guard tuple")
check(len(guards) == 13, "thirteen authority conversions guarded")
check(
    policy.false_authority_conversions == guards,
    "policy installs every guard",
)

check(limits.limits_id == limits.expected_id(), "limits stable identity")
check(validate_scope_constraint_limits(limits).ok, "limits validate")
check(
    not validate_scope_constraint_limits(
        build_scope_constraint_limits(
            max_scope_occurrences=ABSOLUTE_MAX_SCOPE_OCCURRENCES + 1
        )
    ).ok,
    "scope occurrence overlimit rejected",
)
check(
    not validate_scope_constraint_limits(
        build_scope_constraint_limits(
            max_governed_spans_per_occurrence=(
                ABSOLUTE_MAX_GOVERNED_SPANS_PER_OCCURRENCE + 1
            )
        )
    ).ok,
    "governed span overlimit rejected",
)
check(
    not validate_scope_constraint_limits(
        build_scope_constraint_limits(
            max_active_context_entries=(
                ABSOLUTE_MAX_ACTIVE_CONTEXT_ENTRIES + 1
            )
        )
    ).ok,
    "context overlimit rejected",
)
check(
    not validate_scope_constraint_limits(
        build_scope_constraint_limits(
            max_reference_candidates=(
                ABSOLUTE_MAX_REFERENCE_CANDIDATES + 1
            )
        )
    ).ok,
    "reference overlimit rejected",
)

check(len(rules) == 21, "exact twenty-one scope rules")
check(validate_default_scope_attachment_rules().ok, "default rules validate")
check(len({rule.rule_id for rule in rules}) == 21, "rule IDs unique")
check(len({rule.rule_key for rule in rules}) == 21, "rule keys unique")
check(
    {rule.responsibility for rule in rules}
    == set(ScopeResponsibility),
    "every scope responsibility registered",
)
for index, rule in enumerate(rules):
    check(rule.rule_id == rule.expected_id(), f"rule stable {index}")
    check(validate_scope_attachment_rule(rule).ok, f"rule validates {index}")
    check(rule.exact_source_span_required, f"rule exact span {index}")
    check(rule.preserve_multiple_attachments, f"rule plurality {index}")
    check(rule.possible_parent_links_preserved, f"rule parent links {index}")
    check(rule.possible_child_links_preserved, f"rule child links {index}")
    check(rule.no_semantic_selection, f"rule no semantics {index}")
    check(rule.no_authority_conversion, f"rule no conversion {index}")

waiting = tuple(
    rule
    for rule in rules
    if rule.activation_status
    is ScopeRuleActivationStatus.REGISTERED_AWAITING_BINDING_AUTHORITY
)
check(len(waiting) == 9, "nine rules await binding authority")
for rule in waiting:
    check(
        not rule.operator_keys or rule.responsibility is ScopeResponsibility.PROPOSAL,
        f"waiting rule does not invent binding {rule.rule_key}",
    )

# Active context records are caller supplied, immutable, closed, and inert.
entry = build_active_context_entry(
    context_object_id="object.patch.accepted",
    object_kind=ContextObjectKind.PATCH,
    exact_identifiers=("PATCH-001",),
    exact_reference_forms=("it",),
    ordinal=1,
    position_tags=(ContextPositionTag.ABOVE,),
    operational_status=ContextOperationalStatus.ACCEPTED,
    source_event_ids=("context-event-1",),
)
check(entry.entry_id == entry.expected_id(), "context entry stable")
check(validate_active_context_entry(entry).ok, "context entry validates")
check(entry.caller_supplied and entry.immutable, "context entry immutable")
check(not entry.release_authorized, "context does not grant release")
registry = build_active_context_registry((entry,))
check(registry.registry_id == registry.expected_id(), "context registry stable")
check(validate_active_context_registry(registry).ok, "context registry validates")
check(registry.exact_entry_count == 1, "context count exact")
for field in (
    "automatic_memory_search",
    "automatic_file_search",
    "automatic_repository_history_search",
    "automatic_web_search",
    "similarity_search",
    "nearest_object_fallback",
    "capability_influence",
):
    check(getattr(registry, field) is False, f"context boundary {field}")

# Governing example.
projection, binding, trails, result = pipeline(
    "Do not install it.",
    1,
)
check(
    result.status is ScopeConstraintStatus.MISSING_CONTEXT_REFERENCE,
    "governing example missing explicit context",
)
check(result.constraint_set is not None, "governing set exists")
check(result.result_id == result.expected_id(), "governing result stable")
check(
    validate_scope_attachment_reference_constraint_result(
        result,
        projection,
        binding,
        trails,
    ).ok,
    "governing result validates",
)
constraint_set = result.constraint_set
assert constraint_set is not None
check(constraint_set.constraint_set_id == constraint_set.expected_id(), "set stable")
check(
    validate_scope_attachment_reference_constraint_set(
        constraint_set
    ).ok,
    "set validates",
)
check(constraint_set.constrained_trail_count == 8, "eight trails preserved")
check(constraint_set.scope_occurrence_count == 13, "thirteen scope occurrences")
check(constraint_set.reference_analysis_count == 1, "one reference analysis")
check(constraint_set.multiple_attachment_count == 7, "seven multiple attachments")
check(constraint_set.missing_context_reference_count == 1, "one missing context")
check(constraint_set.all_original_trails_preserved, "all trails preserved")
check(constraint_set.all_lawful_attachments_preserved, "all attachments preserved")
check(constraint_set.false_authority_conversion_count == 13, "all guards active")
check(constraint_set.selected_trail_id is None, "no selected trail")
check(constraint_set.selected_attachment_id is None, "no selected attachment")
check(constraint_set.resolved_reference_entry_id is None, "no resolved reference")

original_snapshots = {
    trail.phase_trail_id: json.dumps(
        trail.to_dict(),
        sort_keys=True,
        default=str,
    )
    for trail in trails.phase_trail_set.trails
}
seen_responsibilities = set()
multiple_fragments = set()
for trail_index, constrained in enumerate(constraint_set.constrained_trails):
    check(
        constrained.constrained_trail_id == constrained.expected_id(),
        f"constrained trail stable {trail_index}",
    )
    check(
        validate_scope_constrained_candidate_trail(constrained).ok,
        f"constrained trail validates {trail_index}",
    )
    check(constrained.original_trail_preserved, f"original preserved {trail_index}")
    check(not constrained.original_trail_mutated, f"original unmutated {trail_index}")
    check(constrained.candidate_only, f"candidate only {trail_index}")
    check(constrained.authority_guard_codes == guards, f"guards {trail_index}")
    check(
        json.dumps(
            next(
                trail
                for trail in trails.phase_trail_set.trails
                if trail.phase_trail_id == constrained.phase_trail_id
            ).to_dict(),
            sort_keys=True,
            default=str,
        )
        == original_snapshots[constrained.phase_trail_id],
        f"predecessor bytes unchanged {trail_index}",
    )
    for occurrence_index, occurrence in enumerate(
        constrained.scope_occurrences
    ):
        seen_responsibilities.add(occurrence.responsibility)
        check(
            occurrence.occurrence_id == occurrence.expected_id(),
            f"occurrence stable {trail_index}:{occurrence_index}",
        )
        check(
            validate_scope_attachment_occurrence(occurrence).ok,
            f"occurrence validates {trail_index}:{occurrence_index}",
        )
        check(
            occurrence.selected_attachment_id is None,
            f"no selected attachment {trail_index}:{occurrence_index}",
        )
        check(
            occurrence.authority_guard_codes == guards,
            f"occurrence guards {trail_index}:{occurrence_index}",
        )
        for span_index, span in enumerate(
            occurrence.possible_governed_spans
        ):
            check(
                span.governed_span_id == span.expected_id(),
                f"span stable {trail_index}:{occurrence_index}:{span_index}",
            )
            check(
                validate_governed_span_candidate(span).ok,
                f"span validates {trail_index}:{occurrence_index}:{span_index}",
            )
            check(span.candidate_only and not span.selected, "span candidate only")
            if occurrence.multiple_attachment:
                multiple_fragments.add(
                    "".join(span.exact_source_fragments)
                )
    for analysis in constrained.reference_analyses:
        check(
            analysis.status
            is ReferenceAnalysisStatus.MISSING_CONTEXT_REFERENCE,
            "reference remains missing context",
        )
        check(validate_reference_analysis(analysis).ok, "reference analysis validates")
        check(not analysis.reference_resolved, "reference unresolved")
        check(not analysis.memory_search_performed, "no memory search")
        check(not analysis.file_search_performed, "no file search")
        check(not analysis.web_search_performed, "no web search")
        check(not analysis.language_model_used, "no LLM")

check(
    {
        ScopeResponsibility.NEGATION,
        ScopeResponsibility.PROHIBITION,
        ScopeResponsibility.IMPERATIVE_SURFACE_FORM,
        ScopeResponsibility.REFERENCE,
        ScopeResponsibility.COMPLETION_CLAIMS,
    }.issubset(seen_responsibilities),
    "governing responsibilities represented",
)
check("install" in multiple_fragments, "action-like span preserved")
check("install it" in multiple_fragments, "combined governed span preserved")
check(
    all(
        not constrained.permission_inferred
        and not constrained.capability_authorized
        and not constrained.action_performed
        for constrained in constraint_set.constrained_trails
    ),
    "governing example creates no authority",
)

# Exact context produces candidates, never resolution.
_, _, _, one_result = pipeline(
    "it",
    2,
    context=registry,
)
one_set = one_result.constraint_set
assert one_set is not None
one_analysis = one_set.constrained_trails[0].reference_analyses[0]
check(
    one_analysis.status
    is ReferenceAnalysisStatus.ONE_SOURCE_SUPPORTED_REFERENCE_CANDIDATE,
    "one context candidate status",
)
check(one_analysis.candidate_count == 1, "one context candidate count")
check(not one_analysis.reference_resolved, "one candidate not resolution")
check(one_analysis.selected_context_entry_id is None, "one candidate not selected")
check(
    validate_reference_context_candidate(one_analysis.candidates[0]).ok,
    "one context candidate validates",
)

second_entry = build_active_context_entry(
    context_object_id="object.patch.second",
    object_kind=ContextObjectKind.PATCH,
    exact_reference_forms=("it",),
)
multi_registry = build_active_context_registry((entry, second_entry))
_, _, _, multi_result = pipeline(
    "it",
    3,
    context=multi_registry,
)
multi_analysis = (
    multi_result.constraint_set
    .constrained_trails[0]
    .reference_analyses[0]
)
check(
    multi_analysis.status
    is ReferenceAnalysisStatus.MULTIPLE_REFERENCE_CANDIDATES,
    "multiple context candidate status",
)
check(multi_analysis.candidate_count == 2, "multiple candidate count")
check(multi_analysis.multiple_candidates_preserved, "plurality preserved")
check(not multi_analysis.reference_resolved, "multiple candidates unresolved")

empty_registry = build_active_context_registry(())
_, _, _, unresolved_result = pipeline(
    "it",
    4,
    context=empty_registry,
)
unresolved_analysis = (
    unresolved_result.constraint_set
    .constrained_trails[0]
    .reference_analyses[0]
)
check(
    unresolved_analysis.status
    is ReferenceAnalysisStatus.UNRESOLVED_REFERENCE,
    "empty explicit context unresolved",
)

_, _, _, prohibited_result = pipeline(
    "it",
    5,
    context=registry,
    requested_dependencies=("memory", "filesystem", "web"),
)
prohibited_analysis = (
    prohibited_result.constraint_set
    .constrained_trails[0]
    .reference_analyses[0]
)
check(
    prohibited_result.status
    is ScopeConstraintStatus.PROHIBITED_CONTEXT_DEPENDENCY,
    "prohibited dependency result status",
)
check(
    prohibited_analysis.status
    is ReferenceAnalysisStatus.PROHIBITED_CONTEXT_DEPENDENCY,
    "prohibited dependency analysis status",
)
check(prohibited_analysis.candidate_count == 0, "prohibited gives no candidate")
check(not prohibited_result.memory_read_performed, "prohibited no memory read")
check(not prohibited_result.filesystem_read_performed, "prohibited no file read")
check(not prohibited_result.web_search_performed, "prohibited no web search")

# Quotation containment and reported-speech possibility remain candidates.
q_projection, q_binding, q_trails, q_result = pipeline(
    '"Alpha"',
    6,
)
q_set = q_result.constraint_set
assert q_set is not None
check(q_set.constrained_trail_count == 4, "quotation trails preserved")
check(q_set.scope_occurrence_count == 5, "quotation occurrence count")
q_responsibilities = [
    occurrence.responsibility
    for trail in q_set.constrained_trails
    for occurrence in trail.scope_occurrences
]
check(
    q_responsibilities.count(ScopeResponsibility.QUOTATION) == 4,
    "four quotation constraints",
)
check(
    q_responsibilities.count(ScopeResponsibility.REPORTED_SPEECH) == 1,
    "one reported-speech possibility",
)
for constrained in q_set.constrained_trails:
    for occurrence in constrained.scope_occurrences:
        check(
            occurrence.attachment_status
            is AttachmentStatus.SINGULAR_ATTACHMENT,
            "quotation singular interior",
        )
        check(
            "".join(
                occurrence.possible_governed_spans[0].exact_source_fragments
            )
            == "Alpha",
            "exact quotation interior",
        )
        check(
            AuthorityConversionGuard.
            QUOTED_INSTRUCTION_TO_ACTIVE_INSTRUCTION
            in occurrence.authority_guard_codes,
            "quoted instruction activation blocked",
        )
        check(not occurrence.action_performed, "quotation no action")

# Incomplete quotation stays malformed.
_, _, _, incomplete_result = pipeline(
    '"Alpha',
    7,
)
incomplete_set = incomplete_result.constraint_set
assert incomplete_set is not None
check(
    incomplete_result.status
    is ScopeConstraintStatus.MALFORMED_SCOPE_ATTACHMENT,
    "incomplete quote malformed",
)
incomplete_occurrence = (
    incomplete_set.constrained_trails[0].scope_occurrences[0]
)
check(
    incomplete_occurrence.attachment_status
    is AttachmentStatus.MALFORMED_ATTACHMENT,
    "malformed attachment status",
)
check(
    not incomplete_occurrence.possible_governed_spans,
    "no invented quote interior",
)

# Question surface never becomes command.
_, _, _, question_result = pipeline(
    "Is it?",
    8,
)
question_set = question_result.constraint_set
assert question_set is not None
question_responsibilities = {
    occurrence.responsibility
    for trail in question_set.constrained_trails
    for occurrence in trail.scope_occurrences
}
check(
    ScopeResponsibility.INTERROGATION in question_responsibilities,
    "interrogation surface preserved",
)
check(
    all(
        AuthorityConversionGuard.QUESTION_TO_COMMAND
        in occurrence.authority_guard_codes
        for trail in question_set.constrained_trails
        for occurrence in trail.scope_occurrences
    ),
    "question-to-command blocked",
)
check(
    all(
        not trail.permission_inferred and not trail.action_performed
        for trail in question_set.constrained_trails
    ),
    "question creates no permission or action",
)

# No candidate input gives a lawful zero.
zero_projection, zero_binding, zero_trails, zero_result = pipeline(
    "Hello",
    9,
)
check(
    zero_result.status
    is ScopeConstraintStatus.ZERO_SCOPE_CONSTRAINTS,
    "zero constraint status",
)
check(zero_result.constraint_set is not None, "zero set exists")
check(
    zero_result.constraint_set.constrained_trail_count == 0,
    "zero constrained trails",
)
check(
    validate_scope_attachment_reference_constraint_result(
        zero_result,
        zero_projection,
        zero_binding,
        zero_trails,
    ).ok,
    "zero result validates",
)

# Determinism across repeated runs.
for index, text in enumerate(
    (
        "Do not install it.",
        '"Alpha"',
        '"Alpha',
        "it",
        "Is it?",
        "Hello",
    ),
    start=20,
):
    first = pipeline(text, index)[3]
    second = pipeline(text, index)[3]
    check(first == second, f"deterministic result {text!r}")
    check(first.result_id == second.result_id, f"deterministic ID {text!r}")

# Tamper resistance.
bad_policy = replace(policy, memory_search_authorized=True)
check(
    not validate_scope_constraint_policy(bad_policy).ok,
    "tampered policy rejected",
)
bad_entry = replace(entry, release_authorized=True)
check(
    not validate_active_context_entry(bad_entry).ok,
    "release-authorized entry rejected",
)
bad_registry = replace(registry, automatic_file_search=True)
check(
    not validate_active_context_registry(bad_registry).ok,
    "automatic file search registry rejected",
)
bad_occurrence = replace(
    next(
        occurrence
        for trail in constraint_set.constrained_trails
        for occurrence in trail.scope_occurrences
    ),
    permission_inferred=True,
)
check(
    not validate_scope_attachment_occurrence(bad_occurrence).ok,
    "permission-bearing occurrence rejected",
)
bad_analysis = replace(one_analysis, reference_resolved=True)
check(
    not validate_reference_analysis(bad_analysis).ok,
    "resolved reference rejected",
)
bad_trail = replace(
    constraint_set.constrained_trails[0],
    selected_trail=True,
)
check(
    not validate_scope_constrained_candidate_trail(bad_trail).ok,
    "selected trail rejected",
)
bad_set = replace(constraint_set, concept_authority_available=True)
check(
    not validate_scope_attachment_reference_constraint_set(bad_set).ok,
    "concept authority rejected",
)
bad_result = replace(result, filesystem_read_performed=True)
check(
    not validate_scope_attachment_reference_constraint_result(
        bad_result
    ).ok,
    "filesystem read result rejected",
)

# Exercise every record repeatedly so mutation/count/id defects cannot hide.
for trail in constraint_set.constrained_trails:
    for _ in range(3):
        check(
            validate_scope_constrained_candidate_trail(trail).ok,
            "repeated constrained trail validation",
        )
    for occurrence in trail.scope_occurrences:
        for _ in range(3):
            check(
                validate_scope_attachment_occurrence(occurrence).ok,
                "repeated occurrence validation",
            )
        for span in occurrence.possible_governed_spans:
            for _ in range(3):
                check(
                    validate_governed_span_candidate(span).ok,
                    "repeated span validation",
                )
    for analysis in trail.reference_analyses:
        for _ in range(3):
            check(
                validate_reference_analysis(analysis).ok,
                "repeated reference validation",
            )

# Full no-authority surface.
for constrained_result in (
    result,
    one_result,
    multi_result,
    unresolved_result,
    prohibited_result,
    q_result,
    incomplete_result,
    question_result,
    zero_result,
):
    for field in (
        "filesystem_read_performed",
        "filesystem_write_performed",
        "repository_history_search_performed",
        "network_access_performed",
        "environment_access_performed",
        "memory_read_performed",
        "memory_write_performed",
        "web_search_performed",
        "embedding_performed",
        "language_model_used",
        "similarity_search_performed",
        "selected_trail",
        "selected_attachment",
        "reference_resolved",
        "selected_meaning",
        "concept_meaning_created",
        "predicate_role_assigned",
        "permission_inferred",
        "capability_authorized",
        "route_registration_performed",
        "tool_routing_performed",
        "action_performed",
        "delivery_performed",
        "release_authorized",
    ):
        check(
            getattr(constrained_result, field) is False,
            f"result authority boundary {field}",
        )

# Runtime remains pure when external access surfaces are blocked.
with ExitStack() as stack:
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(Path, "read_text", forbidden))
    stack.enter_context(patch.object(Path, "read_bytes", forbidden))
    stack.enter_context(patch.object(Path, "write_text", forbidden))
    stack.enter_context(patch.object(Path, "write_bytes", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    stack.enter_context(patch.object(os, "getenv", forbidden))
    protected = apply_scope_attachment_reference_constraints(
        projection,
        binding,
        trails,
    )
check(
    protected.status is ScopeConstraintStatus.MISSING_CONTEXT_REFERENCE,
    "side-effect blocked constraint application succeeds",
)

print("AI.WEB SLICE 36F BEHAVIOR TEST: PASS")
print(f"checks={checks}")
print(f"scope_rules={len(rules)}")
print(f"authority_conversion_guards={len(guards)}")
print(f"governing_example_constrained_trails={constraint_set.constrained_trail_count}")
print(f"governing_example_scope_occurrences={constraint_set.scope_occurrence_count}")
print("selected_attachments=0")
print("resolved_references=0")
print("concept_predicate_permission_capability_route_action_effects=0")
