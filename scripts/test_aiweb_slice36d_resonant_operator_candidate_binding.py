#!/usr/bin/env python3
"""Behavior and adversarial tests for Slice 36D."""

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

from aiweb_language_core_bootstrap.input_event_custody import (
    capture_input_event,
)
from aiweb_language_core_bootstrap.resonant_operator_candidate_binding import (
    ABSOLUTE_MAX_BINDING_CANDIDATES,
    CandidateBindingStatus,
    CandidateSupportStatus,
    DeterministicConfidenceBasis,
    EXPECTED_DEFAULT_RULE_COUNT,
    ProposalOutputKind,
    ResonantOperatorBindingCandidate,
    StructuralSignalKind,
    bind_resonant_operator_candidates,
    build_candidate_binding_limits,
    build_default_resonant_operator_proposal_ruleset,
    default_candidate_binding_limits,
    validate_candidate_binding_limits,
    validate_resonant_operator_binding_candidate,
    validate_resonant_operator_candidate_binding_result,
    validate_resonant_operator_candidate_binding_set,
    validate_resonant_operator_proposal_rule,
    validate_resonant_operator_proposal_ruleset,
    validate_unbound_structural_signal,
)
from aiweb_language_core_bootstrap.source_field_projection import (
    SourceFieldProjectionStatus,
    project_source_field,
)
from aiweb_language_core_bootstrap.symbolic_grammar_operator_registry import (
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


def project(text: str, sequence: int):
    custody = capture_input_event(
        text,
        source_id="fixture.user",
        channel_id="fixture.chat",
        sequence_number=sequence,
    )
    check(custody.event is not None, f"custody event {sequence}")
    projection = project_source_field(custody.event)
    check(projection.projection is not None, f"projection {sequence}")
    return projection


def bind(text: str, sequence: int):
    projection_result = project(text, sequence)
    result = bind_resonant_operator_candidates(projection_result)
    check(result.binding_set is not None, f"binding set {sequence}")
    return projection_result, result


registry = build_default_symbolic_grammar_operator_registry()
ruleset = build_default_resonant_operator_proposal_ruleset(registry)

# Closed deterministic rule authority.
check(ruleset.ruleset_id == ruleset.expected_id(), "ruleset stable id")
check(ruleset.exact_rule_count == EXPECTED_DEFAULT_RULE_COUNT == 15, "exact rule count")
check(ruleset.closed_world, "ruleset closed world")
check(ruleset.deterministic_only, "ruleset deterministic only")
check(not ruleset.rule_order_selects_winner, "rule order does not select winner")
check(validate_resonant_operator_proposal_ruleset(ruleset, registry).ok, "ruleset validates")
check(len({rule.rule_id for rule in ruleset.rules}) == 15, "rule ids unique")
check(len({rule.rule_key for rule in ruleset.rules}) == 15, "rule keys unique")
for index, rule in enumerate(ruleset.rules):
    check(rule.rule_id == rule.expected_id(), f"rule stable id {index}")
    check(validate_resonant_operator_proposal_rule(rule, registry).ok, f"rule validates {index}")
    check(rule.enabled and rule.exact_match_required and rule.source_span_required, f"rule exact contract {index}")
    for name in (
        "normalization_authorized",
        "casefolding_authorized",
        "tokenization_authorized",
        "phrase_frequency_authorized",
        "statistical_scoring_authorized",
        "embedding_authorized",
        "vector_similarity_authorized",
        "nearest_neighbor_authorized",
        "language_model_authorized",
        "memory_resemblance_authorized",
        "web_search_authorized",
        "hidden_parser_authorized",
        "capability_influence_authorized",
    ):
        check(getattr(rule, name) is False, f"rule prohibited mechanism {index} {name}")

# Limits are deterministic and typed.
limits_a = default_candidate_binding_limits()
limits_b = default_candidate_binding_limits()
check(limits_a == limits_b, "default limits deterministic")
check(limits_a.limits_id == limits_a.expected_id(), "limits stable id")
check(validate_candidate_binding_limits(limits_a).ok, "limits validate")
zero_limits = build_candidate_binding_limits(max_candidates=0, max_unbound_signals=0)
check(validate_candidate_binding_limits(zero_limits).ok, "zero limits valid")
invalid_limits = build_candidate_binding_limits(
    max_candidates=ABSOLUTE_MAX_BINDING_CANDIDATES + 1
)
check(not validate_candidate_binding_limits(invalid_limits).ok, "oversize limits rejected")

# Governing example.
projection_result, result = bind("Do not install it.", 10)
projection = projection_result.projection
binding_set = result.binding_set
assert projection is not None and binding_set is not None
check(result.status is CandidateBindingStatus.CANDIDATE_BINDINGS_SUPPORTED, "example supported")
check(result.result_id == result.expected_id(), "example result stable id")
check(binding_set.binding_set_id == binding_set.expected_id(), "binding set stable id")
check(binding_set.candidate_count == 5, "example five candidates")
check(binding_set.unbound_signal_count == 1, "example one unbound signal")
check(binding_set.structural_progression_allowed, "example structural progression")
check(validate_resonant_operator_candidate_binding_set(binding_set, projection, registry, ruleset).ok, "example binding set validates")
check(validate_resonant_operator_candidate_binding_result(result, projection, registry, ruleset).ok, "example result validates")

by_key = {}
for candidate in binding_set.candidates:
    by_key.setdefault(candidate.candidate_operator_key, []).append(candidate)
    check(candidate.candidate_binding_id == candidate.expected_id(), "candidate stable id")
    check(validate_resonant_operator_binding_candidate(candidate, projection, registry, ruleset).ok, "candidate validates")
    check(candidate.unresolved, "candidate unresolved")
    check(candidate.candidate_association_created, "candidate association created")
    check(not candidate.operator_occurrence_created, "no operator occurrence")
    check(not candidate.operator_application_performed, "no operator application")
    check(not candidate.phase_assignment_performed, "no phase assignment")
    check(not candidate.meaning_selected, "no meaning")
    check(not candidate.permission_inferred, "no permission")
    check(not candidate.route_created, "no route")
    check(not candidate.action_performed, "no action")
    check(candidate.confidence_basis is DeterministicConfidenceBasis.EXACT_OBSERVABLE_RULE_MATCH, "exact confidence basis")
    check(candidate.support_status is CandidateSupportStatus.SUPPORTED_EXACT_RULE_MATCH, "exact support status")

check(set(by_key) == {"grammar_prohibition", "grammar_negation", "grammar_reference", "grammar_boundary", "fbsc_loop_seal"}, "example exact operator keys")
check(by_key["grammar_negation"][0].exact_source_fragments == ("not",), "negation exact span")
check(by_key["grammar_reference"][0].exact_source_fragments == ("it",), "reference exact span")
check(by_key["grammar_prohibition"][0].exact_source_fragments == ("Do", "not"), "prohibition exact multi-span")
check(by_key["grammar_prohibition"][0].possible_child_binding_ids == (by_key["grammar_negation"][0].candidate_binding_id,), "prohibition child candidate")
check(by_key["grammar_negation"][0].possible_parent_binding_ids == (by_key["grammar_prohibition"][0].candidate_binding_id,), "negation parent candidate")

signal = binding_set.unbound_structural_signals[0]
check(signal.signal_kind is StructuralSignalKind.ACTION_LIKE, "install action-like only")
check(signal.exact_source_fragments == ("install",), "install exact signal span")
check(signal.operator_candidate_created is False, "install not grammar operator")
check(signal.predicate_role_assigned is False, "install no predicate role")
check(signal.capability_binding_created is False, "install no capability")
check(signal.route_created is False and signal.action_performed is False, "install no route or action")
check("document5_action_root_support_missing" in signal.missing_prerequisite_codes, "Document 5 support missing")
check(validate_unbound_structural_signal(signal, projection, ruleset).ok, "unbound signal validates")

# Material quotation plurality must remain visible.
quote_projection_result, quote_result = bind('"Alpha"', 20)
quote_projection = quote_projection_result.projection
quote_set = quote_result.binding_set
assert quote_projection is not None and quote_set is not None
check(quote_set.candidate_count == 4, "four quote candidates")
check(quote_set.materially_competing_candidate_count == 4, "all quote candidates materially competing")
check({value.candidate_variant_code for value in quote_set.candidates} == {"possible_direct_quotation", "possible_quoted_name", "possible_quoted_title", "possible_literal_string"}, "quote variants preserved")
for value in quote_set.candidates:
    check(len(value.competing_candidate_binding_ids) == 3, "quote alternatives linked")
    check("materially_competing_candidate_present" in value.conflicting_evidence_codes, "quote conflict recorded")
    check(value.exact_source_fragments == ('"', '"'), "quote marks exact spans")

# Incomplete quotation is a candidate, not repaired or guessed.
incomplete_projection_result, incomplete_result = bind('"Alpha', 21)
incomplete_set = incomplete_result.binding_set
assert incomplete_set is not None
check(incomplete_set.candidate_count == 1, "incomplete quote one candidate")
check(incomplete_set.candidates[0].candidate_variant_code == "possible_incomplete_quotation", "incomplete quote variant")
check("closing_quotation_boundary_missing" in incomplete_set.candidates[0].missing_prerequisite_codes, "missing close recorded")

# Exact boundaries prevent substring overreach.
for sequence, text in enumerate(("notebook", "Nottingham", "itinerary", "Do notary.", "cannot", "installation"), 30):
    _, value = bind(text, sequence)
    current = value.binding_set
    assert current is not None
    check(all(candidate.candidate_operator_key not in {"grammar_negation", "grammar_reference", "grammar_prohibition"} for candidate in current.candidates), f"no substring overreach {text}")

# Negation outside initial do-not is not promoted to prohibition.
_, middle_result = bind("I did not say install it.", 40)
middle_set = middle_result.binding_set
assert middle_set is not None
check(any(value.candidate_operator_key == "grammar_negation" for value in middle_set.candidates), "middle negation candidate")
check(not any(value.candidate_operator_key == "grammar_prohibition" for value in middle_set.candidates), "middle no prohibition")
check(any(value.exact_source_fragments == ("install",) for value in middle_set.unbound_structural_signals), "middle action signal")

# Terminal exact marks can lawfully create multiple structural candidates.
for sequence, text, expected in (
    (50, "Done.", {"grammar_boundary", "fbsc_loop_seal"}),
    (51, "Stop!", {"grammar_boundary", "fbsc_loop_seal"}),
    (52, "Why?", {"grammar_boundary", "grammar_uncertainty"}),
):
    _, value = bind(text, sequence)
    current = value.binding_set
    assert current is not None
    check({candidate.candidate_operator_key for candidate in current.candidates} == expected, f"terminal candidates {text}")

# Zero candidates and action-only signals are lawful non-selection results.
_, none_result = bind("ordinary surface", 60)
none_set = none_result.binding_set
assert none_set is not None
check(none_result.status is CandidateBindingStatus.CANDIDATE_BINDINGS_NONE, "zero candidate status")
check(none_set.candidate_count == 0, "zero candidates")
check(not none_set.structural_progression_allowed, "zero candidates no progression")
_, action_only_result = bind("install", 61)
action_only_set = action_only_result.binding_set
assert action_only_set is not None
check(action_only_set.candidate_count == 0, "action-only no grammar candidate")
check(action_only_set.unbound_signal_count == 1, "action-only signal preserved")
check(action_only_result.status is CandidateBindingStatus.CANDIDATE_BINDINGS_NONE, "action-only remains no binding")

# Partial unsupported source is preserved and holds candidates from progression.
partial_projection_result = project("not \ue000.", 70)
check(partial_projection_result.status is SourceFieldProjectionStatus.SOURCE_FIELD_PARTIALLY_UNSUPPORTED, "partial source fixture")
partial_result = bind_resonant_operator_candidates(partial_projection_result)
partial_projection = partial_projection_result.projection
partial_set = partial_result.binding_set
assert partial_projection is not None and partial_set is not None
check(partial_result.status is CandidateBindingStatus.CANDIDATE_BINDINGS_PARTIALLY_UNSUPPORTED, "partial binding status")
check(not partial_set.structural_progression_allowed, "partial source held")
for value in partial_set.candidates:
    check(value.unsupported, "partial candidate unsupported flag")
    check(value.support_status is CandidateSupportStatus.HELD_PARTIALLY_UNSUPPORTED_SOURCE, "partial support held")
    check(value.confidence_basis is DeterministicConfidenceBasis.EXACT_OBSERVABLE_RULE_MATCH_HELD_BY_PARTIAL_SOURCE, "partial exact held confidence")
check(validate_resonant_operator_candidate_binding_result(partial_result, partial_projection, registry, ruleset).ok, "partial result validates")

# Limits halt candidate construction rather than truncate or choose winners.
limited_result = bind_resonant_operator_candidates(
    quote_projection_result,
    limits=build_candidate_binding_limits(max_candidates=3, max_unbound_signals=10),
)
check(limited_result.status is CandidateBindingStatus.CANDIDATE_BINDINGS_LIMIT_EXCEEDED, "candidate limit status")
check(not limited_result.binding_set_created and limited_result.binding_set is None, "candidate limit no partial set")
action_limited_result = bind_resonant_operator_candidates(
    project("install", 71),
    limits=build_candidate_binding_limits(max_candidates=10, max_unbound_signals=0),
)
check(action_limited_result.status is CandidateBindingStatus.CANDIDATE_BINDINGS_LIMIT_EXCEEDED, "signal limit status")

# Malformed inputs remain typed results.
malformed = bind_resonant_operator_candidates(object())
check(malformed.status is CandidateBindingStatus.CANDIDATE_BINDINGS_MALFORMED_SOURCE, "malformed input status")
check(not malformed.binding_set_created, "malformed no set")
invalid_limit_result = bind_resonant_operator_candidates(project("not", 72), limits=object())
check(invalid_limit_result.status is CandidateBindingStatus.CANDIDATE_BINDINGS_LIMIT_EXCEEDED, "invalid limits typed")

# Stable identities, frozen records and tamper detection.
repeat_a = bind_resonant_operator_candidates(projection_result)
repeat_b = bind_resonant_operator_candidates(projection_result)
check(repeat_a == repeat_b, "binding deterministic")
try:
    repeat_a.status = CandidateBindingStatus.CANDIDATE_BINDINGS_FAILED
    check(False, "result frozen")
except (FrozenInstanceError, AttributeError):
    check(True, "result frozen")
tampered = replace(binding_set.candidates[0], exact_source_fragments=("altered",))
check(not validate_resonant_operator_binding_candidate(tampered, projection, registry, ruleset).ok, "candidate tamper rejected")
tampered_set = replace(binding_set, candidate_count=999)
check(not validate_resonant_operator_candidate_binding_set(tampered_set, projection, registry, ruleset).ok, "set tamper rejected")
tampered_rule = replace(ruleset.rules[0], embedding_authorized=True)
check(not validate_resonant_operator_proposal_rule(tampered_rule, registry).ok, "embedding authorization tamper rejected")

# No numeric/statistical confidence surface exists.
for field in fields(ResonantOperatorBindingCandidate):
    check(field.name not in {"score", "probability", "likelihood", "confidence_score", "rank"}, f"no scoring field {field.name}")
    check(field.type is not float, f"no float field {field.name}")

# Closed rule forms remain exact and do not normalize case beyond enumerated forms.
_, mixed_case_result = bind("dO nOt install it.", 80)
mixed_case_set = mixed_case_result.binding_set
assert mixed_case_set is not None
check(not any(value.candidate_operator_key in {"grammar_negation", "grammar_prohibition"} for value in mixed_case_set.candidates), "unlisted mixed case not normalized")

# No external side effects are consulted by binding.
with ExitStack() as stack:
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(Path, "read_text", forbidden))
    stack.enter_context(patch.object(Path, "read_bytes", forbidden))
    stack.enter_context(patch.object(Path, "write_text", forbidden))
    stack.enter_context(patch.object(Path, "write_bytes", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    stack.enter_context(patch.object(os, "getenv", forbidden))
    protected = bind_resonant_operator_candidates(projection_result)
check(protected.status is CandidateBindingStatus.CANDIDATE_BINDINGS_SUPPORTED, "side-effect blocked execution succeeds")

# Every produced binding preserves source IDs and never creates authority effects.
for sequence, text in enumerate((
    "Do not install it.",
    '"Name"?',
    "This!",
    "run that.",
    "not not it.",
), 100):
    projection_result_i, result_i = bind(text, sequence)
    projection_i = projection_result_i.projection
    set_i = result_i.binding_set
    assert projection_i is not None and set_i is not None
    check(set_i.source_event_id == projection_i.source_event_id, f"source event preserved {sequence}")
    check(set_i.source_sha256 == projection_i.source_sha256, f"source hash preserved {sequence}")
    check(set_i.projection_id == projection_i.projection_id, f"projection ancestry preserved {sequence}")
    for name in (
        "operator_occurrence_available",
        "operator_application_available",
        "phase_assignment_available",
        "meaning_selection_available",
        "permission_authority_available",
        "route_authority_available",
        "tool_authority_available",
        "action_authority_available",
        "memory_authority_available",
        "delivery_authority_available",
        "hidden_fallback_allowed",
    ):
        check(getattr(set_i, name) is False, f"authority remains false {sequence} {name}")

print(f"SLICE 36D BEHAVIOR TEST: PASS ({checks} checks)")
