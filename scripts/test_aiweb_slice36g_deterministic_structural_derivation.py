#!/usr/bin/env python3
"""Behavior and adversarial verification for Slice 36G."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import FrozenInstanceError, replace
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
from aiweb_language_core_bootstrap.deterministic_structural_derivation import (
    ABSOLUTE_MAX_GRAPH_EDGES_PER_CANDIDATE,
    ABSOLUTE_MAX_GRAPH_NODES_PER_CANDIDATE,
    ABSOLUTE_MAX_RULE_TRACES_PER_CANDIDATE,
    ABSOLUTE_MAX_SOURCE_RANGES_PER_CANDIDATE,
    ABSOLUTE_MAX_STRUCTURAL_CANDIDATES,
    StructuralCompletenessStatus,
    StructuralCoverageStatus,
    StructuralDerivationStatus,
    StructuralNonProgressReason,
    build_default_structural_derivation_policy,
    build_default_structural_derivation_rules,
    build_structural_derivation_limits,
    default_structural_derivation_limits,
    derive_deterministic_structural_analysis,
    validate_default_structural_derivation_rules,
    validate_deterministic_structural_derivation_result,
    validate_structural_analysis_candidate,
    validate_structural_analysis_candidate_set,
    validate_structural_derivation_limits,
    validate_structural_derivation_policy,
    validate_structural_derivation_rule,
    validate_structural_non_progress_result,
    validate_structural_operator_edge,
    validate_structural_operator_graph,
    validate_structural_operator_node,
    validate_structural_rule_application_trace,
    validate_structural_source_coverage_proof,
)
from aiweb_language_core_bootstrap.input_event_custody import (
    capture_input_event,
)
from aiweb_language_core_bootstrap.resonant_operator_candidate_binding import (
    bind_resonant_operator_candidates,
)
from aiweb_language_core_bootstrap.scope_attachment_reference_constraints import (
    ContextObjectKind,
    ReferenceAnalysisStatus,
    build_active_context_entry,
    build_active_context_registry,
    apply_scope_attachment_reference_constraints,
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
    trails = construct_candidate_resonant_phase_trails(projection, binding)
    check(trails.phase_trail_set is not None, f"trails {sequence}")
    constraints = apply_scope_attachment_reference_constraints(
        projection,
        binding,
        trails,
        active_context_registry=context,
        requested_context_dependencies=requested_dependencies,
    )
    check(constraints.constraint_set is not None, f"constraints {sequence}")
    result = derive_deterministic_structural_analysis(
        custody,
        projection,
        binding,
        trails,
        constraints,
    )
    return custody, projection, binding, trails, constraints, result


policy = build_default_structural_derivation_policy()
limits = default_structural_derivation_limits()
rules = build_default_structural_derivation_rules()

check(policy.policy_id == policy.expected_id(), "policy stable identity")
check(validate_structural_derivation_policy(policy).ok, "policy validates")
for name in (
    "deterministic_only",
    "exact_ancestry_required",
    "source_reconstruction_required",
    "preserve_all_structural_candidates",
    "preserve_all_non_progress_reasons",
    "preserve_scope_attachments",
    "preserve_reference_candidates",
):
    check(getattr(policy, name) is True, f"policy true boundary {name}")
for name in (
    "hidden_fallback_allowed",
    "candidate_meaning_authorized",
    "selected_meaning_authorized",
    "intended_meaning_selection_authorized",
    "concept_resolution_authorized",
    "sense_resolution_authorized",
    "predicate_identity_authorized",
    "participant_role_assignment_authorized",
    "truth_determination_authorized",
    "evidence_validity_determination_authorized",
    "clarification_question_authorized",
    "semantic_rejection_authorized",
    "permission_inference_authorized",
    "capability_selection_authorized",
    "route_creation_authorized",
    "tool_routing_authorized",
    "action_execution_authorized",
    "memory_read_authorized",
    "memory_write_authorized",
    "protected_memory_retrieval_authorized",
    "outward_rendering_authorized",
    "delivery_authorized",
):
    check(getattr(policy, name) is False, f"policy false boundary {name}")

check(limits.limits_id == limits.expected_id(), "limits stable identity")
check(validate_structural_derivation_limits(limits).ok, "limits validate")
for name, maximum in (
    ("max_structural_candidates", ABSOLUTE_MAX_STRUCTURAL_CANDIDATES),
    ("max_rule_traces_per_candidate", ABSOLUTE_MAX_RULE_TRACES_PER_CANDIDATE),
    ("max_graph_nodes_per_candidate", ABSOLUTE_MAX_GRAPH_NODES_PER_CANDIDATE),
    ("max_graph_edges_per_candidate", ABSOLUTE_MAX_GRAPH_EDGES_PER_CANDIDATE),
    ("max_source_ranges_per_candidate", ABSOLUTE_MAX_SOURCE_RANGES_PER_CANDIDATE),
):
    kwargs = {
        "max_structural_candidates": limits.max_structural_candidates,
        "max_rule_traces_per_candidate": limits.max_rule_traces_per_candidate,
        "max_graph_nodes_per_candidate": limits.max_graph_nodes_per_candidate,
        "max_graph_edges_per_candidate": limits.max_graph_edges_per_candidate,
        "max_source_ranges_per_candidate": limits.max_source_ranges_per_candidate,
    }
    kwargs[name] = maximum + 1
    check(
        not validate_structural_derivation_limits(
            build_structural_derivation_limits(**kwargs)
        ).ok,
        f"absolute limit rejected {name}",
    )

check(len(rules) == 10, "ten structural derivation rules")
check(validate_default_structural_derivation_rules().ok, "default rules validate")
for index, rule in enumerate(rules):
    check(rule.rule_id == rule.expected_id(), f"rule stable {index}")
    check(validate_structural_derivation_rule(rule).ok, f"rule validates {index}")
    check(not rule.creates_selected_meaning, f"rule no selected meaning {index}")
    check(not rule.asks_clarification_question, f"rule no clarification {index}")
    check(not rule.performs_semantic_rejection, f"rule no rejection {index}")
check(sum(rule.creates_structural_candidate for rule in rules) == 1, "one candidate construction rule")

# Governing example.
custody, projection, binding, trails, constraints, result = pipeline(
    "Do not install it.",
    1,
)
check(result.status is StructuralDerivationStatus.MULTIPLE_STRUCTURAL_CANDIDATES, "governing multiple status")
check(result.reason_code == "multiple_structural_candidates_preserved_without_selection", "governing reason")
check(result.result_id == result.expected_id(), "governing result stable")
check(result.structural_set is not None, "governing structural set")
check(
    validate_deterministic_structural_derivation_result(
        result,
        custody,
        projection,
        binding,
        trails,
        constraints,
    ).ok,
    "governing result validates",
)
structural_set = result.structural_set
assert structural_set is not None
check(structural_set.structural_set_id == structural_set.expected_id(), "set stable")
check(validate_structural_analysis_candidate_set(structural_set).ok, "set validates")
check(structural_set.candidate_count == 8, "eight structural candidates")
check(structural_set.structural_candidate_plurality_preserved, "plurality preserved")
check(structural_set.all_source_ancestry_preserved, "source ancestry preserved")
check(structural_set.all_source_reconstruction_proven, "reconstruction proven")
check(structural_set.all_phase_trails_preserved, "phase trails preserved")
check(structural_set.all_scope_occurrences_preserved, "scope preserved")
check(structural_set.all_attachment_candidates_preserved, "attachments preserved")
check(structural_set.all_reference_candidates_preserved, "references preserved")
check(structural_set.selected_structural_candidate_id is None, "no selected structure")
check(not structural_set.candidate_meaning_created, "no candidate meaning")
check(not structural_set.selected_meaning, "no selected meaning")
check(not structural_set.clarification_question_asked, "no clarification")
check(not structural_set.semantic_rejection_performed, "no semantic rejection")
check(structural_set.non_progress_result is not None, "explicit non-progress")
assert structural_set.non_progress_result is not None
check(validate_structural_non_progress_result(structural_set.non_progress_result).ok, "non-progress validates")
check(structural_set.non_progress_result.valid_result, "non-progress valid")
check(not structural_set.non_progress_result.guessed_to_avoid_non_progress, "no non-progress guess")
for required in (
    StructuralNonProgressReason.UNRESOLVED_REFERENCE,
    StructuralNonProgressReason.UNRESOLVED_OPERATOR_BINDING,
    StructuralNonProgressReason.MULTIPLE_STRUCTURAL_CANDIDATES,
    StructuralNonProgressReason.INCOMPLETE_OPERATOR_TRAIL,
):
    check(required in structural_set.aggregate_non_progress_reasons, f"governing reason {required.value}")

phase_snapshots = {
    item.phase_trail_id: json.dumps(item.to_dict(), sort_keys=True, default=str)
    for item in trails.phase_trail_set.trails
}
scope_snapshots = {
    item.constrained_trail_id: json.dumps(item.to_dict(), sort_keys=True, default=str)
    for item in constraints.constraint_set.constrained_trails
}
seen_unbound_install = False
for candidate_index, candidate in enumerate(structural_set.candidates):
    check(candidate.structural_candidate_id == candidate.expected_id(), f"candidate stable {candidate_index}")
    check(validate_structural_analysis_candidate(candidate).ok, f"candidate validates {candidate_index}")
    check(candidate.candidate_only, f"candidate only {candidate_index}")
    check(not candidate.selected_structure, f"candidate unselected {candidate_index}")
    check(candidate.exact_ancestry_complete, f"candidate ancestry {candidate_index}")
    check(candidate.source_reconstruction_proven, f"candidate reconstruction {candidate_index}")
    check(candidate.predecessor_records_preserved, f"candidate predecessor preserved {candidate_index}")
    check(
        json.dumps(candidate.phase_trail.to_dict(), sort_keys=True, default=str)
        == phase_snapshots[candidate.phase_trail_id],
        f"phase record unchanged {candidate_index}",
    )
    constrained = next(
        item
        for item in constraints.constraint_set.constrained_trails
        if item.constrained_trail_id == candidate.constrained_trail_id
    )
    check(
        json.dumps(constrained.to_dict(), sort_keys=True, default=str)
        == scope_snapshots[candidate.constrained_trail_id],
        f"scope predecessor unchanged {candidate_index}",
    )
    check(candidate.operator_graph.graph_id == candidate.operator_graph.expected_id(), f"graph stable {candidate_index}")
    check(validate_structural_operator_graph(candidate.operator_graph).ok, f"graph validates {candidate_index}")
    check(candidate.operator_graph.only_explicit_edges_created, f"explicit edges only {candidate_index}")
    check(not candidate.operator_graph.selected_graph, f"graph unselected {candidate_index}")
    for node_index, node in enumerate(candidate.operator_graph.nodes):
        check(node.node_id == node.expected_id(), f"node stable {candidate_index}:{node_index}")
        check(validate_structural_operator_node(node).ok, f"node validates {candidate_index}:{node_index}")
        check(node.candidate_only and not node.selected, f"node candidate {candidate_index}:{node_index}")
    for edge_index, edge in enumerate(candidate.operator_graph.edges):
        check(edge.edge_id == edge.expected_id(), f"edge stable {candidate_index}:{edge_index}")
        check(validate_structural_operator_edge(edge).ok, f"edge validates {candidate_index}:{edge_index}")
        check(edge.candidate_only and not edge.selected, f"edge candidate {candidate_index}:{edge_index}")
    check(candidate.source_coverage.coverage_proof_id == candidate.source_coverage.expected_id(), f"coverage stable {candidate_index}")
    check(validate_structural_source_coverage_proof(candidate.source_coverage).ok, f"coverage validates {candidate_index}")
    check(candidate.source_coverage.source_reconstruction_proven, f"coverage reconstruction {candidate_index}")
    check(candidate.source_coverage.reconstruction_hash_matches_custody, f"coverage hash {candidate_index}")
    for trace_index, trace in enumerate(candidate.rule_application_traces):
        check(trace.trace_id == trace.expected_id(), f"trace stable {candidate_index}:{trace_index}")
        check(validate_structural_rule_application_trace(trace).ok, f"trace validates {candidate_index}:{trace_index}")
        check(trace.trace_ordinal == trace_index, f"trace ordinal {candidate_index}:{trace_index}")
        check(trace.candidate_only and not trace.selected, f"trace candidate {candidate_index}:{trace_index}")
        check(not trace.semantic_authority, f"trace no semantics {candidate_index}:{trace_index}")
    check(
        candidate.attachment_alternative_ids
        == tuple(item.governed_span_id for item in candidate.attachment_candidates),
        f"attachment alternatives preserved {candidate_index}",
    )
    check(
        candidate.reference_alternative_ids
        == tuple(item.reference_candidate_id for item in candidate.reference_candidates),
        f"reference alternatives preserved {candidate_index}",
    )
    if any(
        "install" in "".join(signal.exact_source_fragments)
        for signal in candidate.unbound_structural_signals
    ):
        seen_unbound_install = True
    for name in (
        "candidate_meaning_created",
        "selected_meaning",
        "concept_resolved",
        "sense_resolved",
        "predicate_identity_created",
        "participant_roles_assigned",
        "truth_determined",
        "evidence_validity_determined",
        "clarification_question_asked",
        "semantic_rejection_performed",
        "permission_inferred",
        "capability_selected",
        "route_created",
        "tool_routing_performed",
        "memory_read_performed",
        "memory_write_performed",
        "protected_memory_retrieved",
        "action_performed",
        "outward_answer_rendered",
        "delivery_performed",
    ):
        check(getattr(candidate, name) is False, f"candidate boundary {candidate_index}:{name}")
check(seen_unbound_install, "unbound install signal preserved")

# Quotation ambiguity produces four candidates and conflict non-progress.
_, _, _, _, quote_constraints, quote_result = pipeline('"Alpha"', 2)
quote_set = quote_result.structural_set
assert quote_set is not None
check(quote_result.status is StructuralDerivationStatus.MULTIPLE_STRUCTURAL_CANDIDATES, "quote multiple")
check(quote_set.candidate_count == 4, "quote four candidates")
check(StructuralNonProgressReason.CONFLICTING_PHASE_TRAILS in quote_set.aggregate_non_progress_reasons, "quote conflict reason")
check(StructuralNonProgressReason.MULTIPLE_STRUCTURAL_CANDIDATES in quote_set.aggregate_non_progress_reasons, "quote multiple reason")
check(all(item.ambiguous for item in quote_set.candidates), "quote candidates ambiguous")
check(all(item.source_coverage.coverage_status is StructuralCoverageStatus.COMPLETE_SOURCE_COVERAGE for item in quote_set.candidates), "quote complete source coverage")
check(
    sum(len(item.scope_occurrences) for item in quote_set.candidates)
    == quote_constraints.constraint_set.scope_occurrence_count,
    "quote scope occurrence count preserved",
)

# Incomplete quotation remains malformed and never repaired.
_, _, _, _, incomplete_constraints, incomplete_result = pipeline('"Alpha', 3)
incomplete_set = incomplete_result.structural_set
assert incomplete_set is not None
check(incomplete_result.status is StructuralDerivationStatus.ONE_STRUCTURAL_CANDIDATE, "incomplete one candidate")
check(incomplete_set.candidate_count == 1, "incomplete count")
incomplete_candidate = incomplete_set.candidates[0]
check(incomplete_candidate.malformed, "incomplete malformed")
check(incomplete_candidate.incomplete, "incomplete flag")
check(incomplete_candidate.completeness_status is StructuralCompletenessStatus.MALFORMED_BOUNDED_STRUCTURE, "malformed completeness")
check(StructuralNonProgressReason.MALFORMED_SOURCE_STRUCTURE in incomplete_candidate.non_progress_reasons, "malformed reason")
check(StructuralNonProgressReason.INCOMPLETE_INPUT in incomplete_candidate.non_progress_reasons, "incomplete input reason")
check("Alpha" in incomplete_candidate.source_coverage.unconsumed_exact_fragments, "unconsumed malformed interior")
check(
    not any(
        occurrence.possible_governed_spans
        for occurrence in incomplete_constraints.constraint_set.constrained_trails[0].scope_occurrences
    ),
    "no invented quotation interior",
)

# Zero derivation is a valid result.
_, _, zero_binding, zero_trails, zero_constraints, zero_result = pipeline("hello", 4)
zero_set = zero_result.structural_set
assert zero_set is not None
check(zero_result.status is StructuralDerivationStatus.ZERO_STRUCTURAL_CANDIDATES, "zero status")
check(zero_set.candidate_count == 0, "zero count")
check(zero_set.non_progress_result is not None, "zero explicit non-progress")
check(zero_set.aggregate_non_progress_reasons == (StructuralNonProgressReason.NO_SUPPORTED_DERIVATION,), "zero no derivation reason")
check(zero_binding.binding_set.candidate_count == 0, "zero binding candidates")
check(zero_trails.phase_trail_set.trail_count == 0, "zero phase trails")
check(zero_constraints.constraint_set.constrained_trail_count == 0, "zero constrained trails")

# Explicit context creates candidates but does not resolve the reference.
entry = build_active_context_entry(
    context_object_id="object.patch.one",
    object_kind=ContextObjectKind.PATCH,
    exact_reference_forms=("it",),
)
registry = build_active_context_registry((entry,))
_, _, _, _, one_context_constraints, one_context_result = pipeline(
    "it",
    5,
    context=registry,
)
one_context_set = one_context_result.structural_set
assert one_context_set is not None
one_candidate = one_context_set.candidates[0]
check(one_context_constraints.constraint_set.constrained_trails[0].reference_analyses[0].status is ReferenceAnalysisStatus.ONE_SOURCE_SUPPORTED_REFERENCE_CANDIDATE, "one reference candidate predecessor")
check(len(one_candidate.reference_candidates) == 1, "one reference candidate preserved")
check(StructuralNonProgressReason.UNRESOLVED_REFERENCE in one_candidate.non_progress_reasons, "one reference still unresolved")
check(not one_candidate.reference_candidates[0].selected, "reference candidate unselected")
check(not one_candidate.reference_candidates[0].reference_resolved, "reference not resolved")

entry_two = build_active_context_entry(
    context_object_id="object.patch.two",
    object_kind=ContextObjectKind.PATCH,
    exact_reference_forms=("it",),
)
multiple_registry = build_active_context_registry((entry, entry_two))
_, _, _, _, multi_context_constraints, multi_context_result = pipeline(
    "it",
    6,
    context=multiple_registry,
)
multi_candidate = multi_context_result.structural_set.candidates[0]
check(multi_context_constraints.constraint_set.constrained_trails[0].reference_analyses[0].status is ReferenceAnalysisStatus.MULTIPLE_REFERENCE_CANDIDATES, "multiple reference predecessor")
check(len(multi_candidate.reference_candidates) == 2, "multiple references preserved")
check(multi_candidate.ambiguous, "multiple references ambiguous")
check(not any(item.selected for item in multi_candidate.reference_candidates), "no reference selected")

_, _, _, _, prohibited_constraints, prohibited_result = pipeline(
    "it",
    7,
    context=registry,
    requested_dependencies=("memory", "filesystem", "web"),
)
prohibited_set = prohibited_result.structural_set
assert prohibited_set is not None
check(StructuralNonProgressReason.PROHIBITED_CONTEXT_DEPENDENCY in prohibited_set.aggregate_non_progress_reasons, "prohibited dependency preserved")
check(prohibited_constraints.constraint_set.prohibited_context_dependency_count == 1, "prohibited predecessor count")
check(not prohibited_result.memory_read_performed, "prohibited no memory read")
check(not prohibited_result.filesystem_read_performed, "prohibited no file read")
check(not prohibited_result.web_search_performed, "prohibited no web search")

# Interrogation cannot become a command; suspended trail remains suspended.
_, _, _, _, _, question_result = pipeline("Is it?", 8)
question_set = question_result.structural_set
assert question_set is not None
check(question_set.candidate_count == 3, "question candidate count")
check(question_set.suspended_recursion_candidate_count == 1, "question suspension preserved")
check(StructuralNonProgressReason.RECURSION_SUSPENDED in question_set.aggregate_non_progress_reasons, "question suspension reason")
check(not question_result.permission_inferred, "question no permission")
check(not question_result.action_performed, "question no action")

# Records are frozen.
try:
    policy.deterministic_only = False
    raise AssertionError("policy mutation allowed")
except FrozenInstanceError:
    check(True, "policy frozen")
try:
    structural_set.candidates[0].selected_structure = True
    raise AssertionError("candidate mutation allowed")
except FrozenInstanceError:
    check(True, "candidate frozen")

# Validators reject tampering.
check(
    not validate_structural_derivation_policy(
        replace(policy, selected_meaning_authorized=True)
    ).ok,
    "policy tamper rejected",
)
check(
    not validate_structural_analysis_candidate(
        replace(structural_set.candidates[0], selected_meaning=True)
    ).ok,
    "candidate meaning tamper rejected",
)
check(
    not validate_structural_analysis_candidate_set(
        replace(structural_set, selected_structural_candidate_id="fake")
    ).ok,
    "set selection tamper rejected",
)
check(
    not validate_deterministic_structural_derivation_result(
        replace(result, clarification_question_asked=True)
    ).ok,
    "clarification tamper rejected",
)
check(
    not validate_structural_operator_graph(
        replace(structural_set.candidates[0].operator_graph, selected_graph=True)
    ).ok,
    "graph selection tamper rejected",
)
check(
    not validate_structural_source_coverage_proof(
        replace(
            structural_set.candidates[0].source_coverage,
            reconstruction_hash_matches_custody=False,
        )
    ).ok,
    "coverage proof tamper rejected",
)

# Invalid call types fail closed.
invalid = derive_deterministic_structural_analysis(
    None,
    None,
    None,
    None,
    None,
)
check(invalid.status is StructuralDerivationStatus.STRUCTURAL_DERIVATION_FAILED, "invalid type fails")
check(invalid.structural_set is None, "invalid type no set")
check(not invalid.candidate_meaning_created, "invalid type no meaning")

# Runtime performs no external I/O, memory, network, or process access.
with ExitStack() as stack:
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    stack.enter_context(patch.object(os, "system", forbidden))
    isolated = derive_deterministic_structural_analysis(
        custody,
        projection,
        binding,
        trails,
        constraints,
    )
check(isolated.result_id == result.result_id, "side-effect-isolated determinism")

# Repeated construction is byte-for-byte deterministic.
repeat = derive_deterministic_structural_analysis(
    custody,
    projection,
    binding,
    trails,
    constraints,
)
check(
    json.dumps(result.to_dict(), sort_keys=True, default=str)
    == json.dumps(repeat.to_dict(), sort_keys=True, default=str),
    "repeat deterministic",
)

# Broad authority assertions across every produced record.
for index, produced in enumerate((result, quote_result, incomplete_result, zero_result, one_context_result, multi_context_result, prohibited_result, question_result)):
    for name in (
        "filesystem_read_performed",
        "filesystem_write_performed",
        "repository_history_search_performed",
        "network_access_performed",
        "environment_access_performed",
        "memory_read_performed",
        "memory_write_performed",
        "protected_memory_retrieval_performed",
        "web_search_performed",
        "embedding_performed",
        "language_model_used",
        "similarity_search_performed",
        "candidate_meaning_created",
        "selected_meaning",
        "intended_meaning_selected",
        "concept_resolved",
        "sense_resolved",
        "predicate_identity_created",
        "participant_roles_assigned",
        "truth_determined",
        "evidence_validity_determined",
        "clarification_question_asked",
        "semantic_rejection_performed",
        "permission_inferred",
        "capability_selected",
        "route_registration_performed",
        "tool_routing_performed",
        "action_performed",
        "outward_answer_rendered",
        "delivery_performed",
    ):
        check(getattr(produced, name) is False, f"result boundary {index}:{name}")

print(f"checks={checks}")
print("AI.WEB SLICE 36G BEHAVIOR TEST: PASS")
