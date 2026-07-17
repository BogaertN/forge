#!/usr/bin/env python3
"""Behavior and adversarial verification for AI.Web Slice 38G."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import fields, is_dataclass, replace
from enum import Enum
import builtins
from pathlib import Path
import socket
import sys
import urllib.request
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aiweb_language_core_bootstrap.candidate_resonant_phase_trail import construct_candidate_resonant_phase_trails
from aiweb_language_core_bootstrap.deterministic_structural_derivation import derive_deterministic_structural_analysis
from aiweb_language_core_bootstrap.input_event_custody import capture_input_event
from aiweb_language_core_bootstrap.resonant_operator_candidate_binding import bind_resonant_operator_candidates
from aiweb_language_core_bootstrap.scope_attachment_reference_constraints import apply_scope_attachment_reference_constraints
from aiweb_language_core_bootstrap.source_field_projection import project_source_field
from aiweb_language_core_bootstrap.structural_concept_candidate_proposal import propose_structural_concept_candidates
from aiweb_language_core_bootstrap.predicate_role_frame_registry.predicate_role_frame_candidate_proposal import (
    CANONICAL_COMPATIBILITY_RULING,
    CANONICAL_COMPATIBILITY_SNAPSHOT,
    DEFAULT_PROPOSAL_PROFILE,
    SLICE38G_NON_AUTHORITY_BOUNDARIES,
    SLICE38_REGISTRY_SNAPSHOT,
    CandidateProposalStatus,
    CandidateStructuralState,
    build_compatibility_conflict,
    build_compatibility_snapshot,
    build_exact_compatibility_rule,
    propose_predicate_role_frame_candidates,
    validate_action_candidate,
    validate_capability_candidate,
    validate_compatibility_snapshot,
    validate_conflict,
    validate_profile,
    validate_result,
    validate_role_layout_candidate,
    validate_rule,
    validate_slice38_snapshot,
)
from aiweb_language_core_bootstrap.predicate_role_frame_registry.predicate_role_frame_candidate_proposal.identity import with_expected_id

checks = 0
malformed_cases = 0


def check(condition: object, label: str) -> None:
    global checks
    checks += 1
    if condition is not True:
        raise AssertionError(label)


def forbidden(*args: object, **kwargs: object) -> object:
    raise AssertionError("external side effect attempted")


def pipeline(text: str, sequence: int):
    custody = capture_input_event(text, source_id="fixture.user", channel_id="fixture.chat", sequence_number=sequence)
    check(custody.event is not None, f"custody {sequence}")
    projection = project_source_field(custody.event)
    check(projection.projection is not None, f"projection {sequence}")
    binding = bind_resonant_operator_candidates(projection)
    check(binding.binding_set is not None, f"binding {sequence}")
    trails = construct_candidate_resonant_phase_trails(projection, binding)
    check(trails.phase_trail_set is not None, f"trails {sequence}")
    constraints = apply_scope_attachment_reference_constraints(projection, binding, trails)
    check(constraints.constraint_set is not None, f"constraints {sequence}")
    structural = derive_deterministic_structural_analysis(custody, projection, binding, trails, constraints)
    check(structural.structural_set is not None, f"structural {sequence}")
    source = propose_structural_concept_candidates(custody, projection, structural)
    return source


def assert_no_authority(result, label: str) -> None:
    for name in (
        "selected_predicate_created", "selected_frame_created",
        "selected_participant_assignment_created", "candidate_meaning_created",
        "selected_meaning_created", "permission_inferred", "tool_route_created",
        "tool_invoked", "action_performed", "memory_read_performed",
        "memory_write_performed", "delivered", "evidence_validity_determined",
        "truth_determined", "clarification_outcome_created", "refusal_outcome_created",
        "blocked_progression_outcome_created", "filesystem_read_performed",
        "filesystem_write_performed", "network_access_performed",
        "external_resource_loaded", "language_model_used", "embedding_used",
        "semantic_similarity_used",
    ):
        check(getattr(result, name) is False, f"{label} no authority {name}")
    check(result.candidate_order_is_ranked is False, f"{label} unranked")
    check(result.capability_non_invocation_boundary_preserved is True, f"{label} cap boundary")


# Canonical profile and exact accepted snapshots.
check(validate_profile(DEFAULT_PROPOSAL_PROFILE).ok, "profile validates")
check(DEFAULT_PROPOSAL_PROFILE.profile_id == DEFAULT_PROPOSAL_PROFILE.expected_id(), "profile stable")
check(DEFAULT_PROPOSAL_PROFILE.non_authority_boundaries == SLICE38G_NON_AUTHORITY_BOUNDARIES, "profile boundaries")
check(validate_slice38_snapshot(SLICE38_REGISTRY_SNAPSHOT).ok, "Slice38 snapshot validates")
check(SLICE38_REGISTRY_SNAPSHOT.snapshot_id == SLICE38_REGISTRY_SNAPSHOT.expected_id(), "Slice38 snapshot stable")
check(SLICE38_REGISTRY_SNAPSHOT.action_root_count == 5, "five roots")
check(SLICE38_REGISTRY_SNAPSHOT.predicate_count == 5, "five predicates")
check(SLICE38_REGISTRY_SNAPSHOT.participant_role_count == 11, "eleven roles")
check(SLICE38_REGISTRY_SNAPSHOT.predicate_frame_count == 5, "five frames")
check(SLICE38_REGISTRY_SNAPSHOT.frame_role_constraint_count == 55, "55 frame role constraints")
check(SLICE38_REGISTRY_SNAPSHOT.frame_role_concept_compatibility_count == 55, "55 compatibility records")
check(SLICE38_REGISTRY_SNAPSHOT.effect_boundary_count == 6, "six effect boundaries")
check(SLICE38_REGISTRY_SNAPSHOT.capability_family_count == 6, "six capabilities")
check(SLICE38_REGISTRY_SNAPSHOT.frame_effect_reference_count == 5, "five effect refs")
check(SLICE38_REGISTRY_SNAPSHOT.frame_capability_reference_count == 5, "five capability refs")
check(validate_compatibility_snapshot(CANONICAL_COMPATIBILITY_SNAPSHOT).ok, "canonical compatibility validates")
check(CANONICAL_COMPATIBILITY_SNAPSHOT.rule_count == 0, "canonical bridge closed")
check(CANONICAL_COMPATIBILITY_SNAPSHOT.conflict_count == 0, "canonical no conflicts")
check("No current Slice 37 concept or sense identity" in CANONICAL_COMPATIBILITY_RULING, "canonical ruling explicit")

# Source fixtures from accepted Slice 37F.
source_one = pipeline("Concept Admission", 1)
source_ambiguous = pipeline("concept", 2)
source_unknown = pipeline("mapping", 3)
source_unsupported = pipeline("sense", 4)

# Current canonical bridge must not guess an action root.
canonical = propose_predicate_role_frame_candidates(source_one)
check(validate_result(canonical).ok, "canonical result validates")
check(canonical.status is CandidateProposalStatus.EXPLICIT_UNSUPPORTED, "canonical unsupported")
check(canonical.reason_code == "no_exact_action_root_compatibility_rule", "canonical reason")
check(canonical.action_predicate_candidate_count == 0, "canonical no action candidate")
check(canonical.role_layout_candidate_count == 0, "canonical no layout")
check(canonical.capability_reference_candidate_count == 0, "canonical no cap")
check(canonical.source_slice37_result_id == source_one.result_id, "source result preserved")
check(canonical.source_event_id == source_one.source_event_id, "source event preserved")
check(canonical.source_sha256 == source_one.source_sha256, "source hash preserved")
check(canonical.structural_result_id == source_one.structural_result_id, "structural result preserved")
check(canonical.structural_set_id == source_one.structural_set_id, "structural set preserved")
check(canonical.slice37_registry_snapshot_id == source_one.registry_snapshot.snapshot_id, "Slice37 snapshot preserved")
check(canonical.structural_ancestry_ids == tuple(x.ancestry_id for x in source_one.structural_ancestries), "structural ancestry preserved")
check(canonical.concept_candidate_proposal_ids == tuple(x.proposal_id for x in source_one.concept_candidates), "concept ancestry preserved")
check(canonical.sense_candidate_proposal_ids == tuple(x.proposal_id for x in source_one.sense_candidates), "sense ancestry preserved")
assert_no_authority(canonical, "canonical")

# Explicit unknown and unsupported predecessor states stay explicit.
unknown = propose_predicate_role_frame_candidates(source_unknown)
check(validate_result(unknown).ok, "unknown validates")
check(unknown.status is CandidateProposalStatus.EXPLICIT_UNKNOWN, "unknown preserved")
check(bool(unknown.unknown_reasons), "unknown reason")
assert_no_authority(unknown, "unknown")
unsupported = propose_predicate_role_frame_candidates(source_unsupported)
check(validate_result(unsupported).ok, "unsupported validates")
check(unsupported.status is CandidateProposalStatus.EXPLICIT_UNSUPPORTED, "unsupported preserved")
check(bool(unsupported.unsupported_reasons), "unsupported reason")
assert_no_authority(unsupported, "unsupported")

concept = source_one.concept_candidates[0]
sense = source_one.sense_candidates[0]

# Exact synthetic compatibility proves the candidate-only positive lane.
inspect_rule = build_exact_compatibility_rule(
    rule_key="fixture.concept-admission.inspect",
    action_root_key="inspect",
    concept_id=concept.concept_id,
    sense_id=sense.sense_id,
    allowed_frame_keys=("inspect_read_only",),
)
check(validate_rule(inspect_rule).ok, "inspect rule validates")
inspect_snapshot = build_compatibility_snapshot(rules=(inspect_rule,), registry_key="fixture.inspect")
check(validate_compatibility_snapshot(inspect_snapshot).ok, "inspect snapshot validates")
with ExitStack() as stack:
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    inspect_result = propose_predicate_role_frame_candidates(source_one, compatibility_snapshot=inspect_snapshot)
check(validate_result(inspect_result).ok, "inspect result validates")
check(inspect_result.status is CandidateProposalStatus.STRUCTURALLY_INCOMPLETE, "inspect incomplete")
check(inspect_result.action_predicate_candidate_count == 1, "inspect one action candidate")
check(inspect_result.role_layout_candidate_count == 1, "inspect one layout")
check(inspect_result.capability_reference_candidate_count == 2, "inspect two cap refs")
check(inspect_result.missing_role_count > 0, "inspect missing roles")
check(inspect_result.action_predicate_candidates[0].action_root_key == "inspect", "inspect exact root")
check(inspect_result.action_predicate_candidates[0].predicate_key == "inspect", "inspect exact predicate")
check(inspect_result.action_predicate_candidates[0].frame_ids_and_versions[0][0] == inspect_result.role_layout_candidates[0].frame_id, "frame ancestry")
check(inspect_result.role_layout_candidates[0].structural_state is CandidateStructuralState.STRUCTURALLY_INCOMPLETE, "layout incomplete")
check(set(x.capability_family_key for x in inspect_result.capability_reference_candidates) == {"read_only_inspection", "source_comparison"}, "inspect cap refs exact")
for item in inspect_result.action_predicate_candidates:
    check(validate_action_candidate(item).ok, "action candidate validates")
for item in inspect_result.role_layout_candidates:
    check(validate_role_layout_candidate(item).ok, "layout validates")
for item in inspect_result.capability_reference_candidates:
    check(validate_capability_candidate(item).ok, "cap candidate validates")
assert_no_authority(inspect_result, "inspect")

# Request demonstrates a lawful zero-capability-reference candidate.
request_rule = build_exact_compatibility_rule(
    rule_key="fixture.concept-admission.request",
    action_root_key="request",
    concept_id=concept.concept_id,
    sense_id=sense.sense_id,
    allowed_frame_keys=("request_non_authorizing",),
)
request_snapshot = build_compatibility_snapshot(rules=(request_rule,), registry_key="fixture.request")
request_result = propose_predicate_role_frame_candidates(source_one, compatibility_snapshot=request_snapshot)
check(validate_result(request_result).ok, "request validates")
check(request_result.action_predicate_candidate_count == 1, "request one action")
check(request_result.role_layout_candidate_count == 1, "request one layout")
check(request_result.capability_reference_candidate_count == 0, "request zero cap refs")
check(request_result.action_predicate_candidates[0].action_root_key == "request", "request exact root")
assert_no_authority(request_result, "request")

# Multiple exact rules remain ambiguous and unranked.
report_rule = build_exact_compatibility_rule(
    rule_key="fixture.concept-admission.report",
    action_root_key="report",
    concept_id=concept.concept_id,
    sense_id=sense.sense_id,
    allowed_frame_keys=("report_attributed_content",),
)
ambiguous_snapshot = build_compatibility_snapshot(
    rules=(inspect_rule, report_rule), registry_key="fixture.ambiguous"
)
ambiguous_result = propose_predicate_role_frame_candidates(source_one, compatibility_snapshot=ambiguous_snapshot)
check(validate_result(ambiguous_result).ok, "ambiguous result validates")
check(ambiguous_result.status is CandidateProposalStatus.AMBIGUOUS, "ambiguous status")
check(ambiguous_result.action_predicate_candidate_count == 2, "two action candidates")
check(ambiguous_result.role_layout_candidate_count == 2, "two layouts")
check(ambiguous_result.unresolved_alternative_count == 2, "two alternatives")
check(set(x.action_root_key for x in ambiguous_result.action_predicate_candidates) == {"inspect", "report"}, "both exact roots")
assert_no_authority(ambiguous_result, "ambiguous")

# Registry-side conflict remains visible and non-operative.
conflict = build_compatibility_conflict(
    conflict_key="fixture.inspect-report-conflict",
    rules=(inspect_rule, report_rule),
    conflict_kind="exact_identity_competing_roots",
    reason="fixture preserves competing exact action-root rules without selection",
)
check(validate_conflict(conflict).ok, "conflict validates")
conflicted_snapshot = build_compatibility_snapshot(
    rules=(inspect_rule, report_rule), conflicts=(conflict,), registry_key="fixture.conflicted"
)
check(validate_compatibility_snapshot(conflicted_snapshot).ok, "conflicted snapshot validates")
conflicted_result = propose_predicate_role_frame_candidates(source_one, compatibility_snapshot=conflicted_snapshot)
check(validate_result(conflicted_result).ok, "conflicted result validates")
check(conflicted_result.status is CandidateProposalStatus.CONFLICTED, "conflicted status")
check(conflicted_result.unresolved_alternative_count == 2, "conflict alternatives")
check(all(x.structural_state is CandidateStructuralState.CONFLICTED for x in conflicted_result.action_predicate_candidates), "candidate conflicts preserved")
assert_no_authority(conflicted_result, "conflicted")

# Determinism and exact candidate order.
repeat = propose_predicate_role_frame_candidates(source_one, compatibility_snapshot=ambiguous_snapshot)
check(repeat == ambiguous_result, "deterministic equality")
check(repeat.result_id == ambiguous_result.result_id, "deterministic identity")
check(tuple(x.candidate_id for x in repeat.action_predicate_candidates) == tuple(x.candidate_id for x in ambiguous_result.action_predicate_candidates), "candidate order deterministic")

# Invalid public inputs fail closed without accepting malformed custody.
invalid_inputs = (None, 0, True, "bad", [], {}, object())
for index, value in enumerate(invalid_inputs):
    result = propose_predicate_role_frame_candidates(value)
    check(validate_result(result).ok, f"invalid source result validates {index}")
    check(result.status is CandidateProposalStatus.PREDECESSOR_REJECTED, f"invalid source rejected {index}")
    assert_no_authority(result, f"invalid source {index}")

bad_profile = replace(DEFAULT_PROPOSAL_PROFILE, selected_meaning_allowed=True)
bad_snapshot = replace(SLICE38_REGISTRY_SNAPSHOT, action_root_count=999)
bad_compat = replace(CANONICAL_COMPATIBILITY_SNAPSHOT, automatic_mapping_allowed=True)
for label, kwargs in (
    ("profile", {"profile": bad_profile}),
    ("snapshot", {"slice38_snapshot": bad_snapshot}),
    ("compat", {"compatibility_snapshot": bad_compat}),
):
    result = propose_predicate_role_frame_candidates(source_one, **kwargs)
    check(validate_result(result).ok, f"bad {label} fail-closed result validates")
    check(result.status is CandidateProposalStatus.PREDECESSOR_REJECTED, f"bad {label} rejected")
    assert_no_authority(result, f"bad {label}")

# Total malformed-field matrix. Every semantically malformed re-identified
# record must be rejected by its public validator without an exception.
def malformed_values(value):
    if isinstance(value, Enum):
        return (None, value.value, "", 1, [], {})
    if type(value) is bool:
        return (None, 0, 1, "false", [], {})
    if type(value) is str:
        return (None, 1, True, [], {}, object())
    if type(value) is int:
        return (None, True, -1, "1", [], {})
    if type(value) is tuple:
        return (None, [], {}, "tuple", 1, object())
    if value is None:
        return ([], {}, object(), 1, True, ())
    if is_dataclass(value):
        return (None, [], {}, "record", 1, object())
    return (None, [], {}, "bad", 1, object())


def exercise(record, validator, id_field: str, label: str) -> None:
    global malformed_cases
    for direct in invalid_inputs:
        malformed_cases += 1
        report = validator(direct)
        check(report.ok is False, f"{label} direct malformed rejected {malformed_cases}")
    for field in fields(record):
        if field.name == id_field:
            continue
        current = getattr(record, field.name)
        for bad in malformed_values(current):
            if bad == current:
                continue
            malformed_cases += 1
            mutated = replace(record, **{field.name: bad})
            try:
                mutated = with_expected_id(mutated, id_field)
            except Exception:
                pass
            report = validator(mutated)
            check(report.ok is False, f"{label}.{field.name} malformed rejected {malformed_cases}")

exercise(DEFAULT_PROPOSAL_PROFILE, validate_profile, "profile_id", "profile")
exercise(SLICE38_REGISTRY_SNAPSHOT, validate_slice38_snapshot, "snapshot_id", "slice38_snapshot")
exercise(inspect_rule, validate_rule, "rule_id", "rule")
exercise(conflict, validate_conflict, "conflict_id", "conflict")
exercise(conflicted_snapshot, validate_compatibility_snapshot, "snapshot_id", "compatibility_snapshot")
exercise(inspect_result.capability_reference_candidates[0], validate_capability_candidate, "candidate_id", "capability_candidate")
exercise(inspect_result.role_layout_candidates[0], validate_role_layout_candidate, "candidate_id", "role_layout")
exercise(inspect_result.action_predicate_candidates[0], validate_action_candidate, "candidate_id", "action_candidate")
exercise(inspect_result, validate_result, "result_id", "result")

# Explosive values may never escape a public validator.
class Explosive:
    def __hash__(self):
        raise RuntimeError("hash explosion")
    def __eq__(self, other):
        raise RuntimeError("equality explosion")
    def __str__(self):
        raise RuntimeError("string explosion")

for validator in (
    validate_profile, validate_slice38_snapshot, validate_rule, validate_conflict,
    validate_compatibility_snapshot, validate_capability_candidate,
    validate_role_layout_candidate, validate_action_candidate, validate_result,
):
    malformed_cases += 1
    report = validator(Explosive())
    check(report.ok is False, "explosive value fails closed")

print("AI.WEB SLICE 38G BEHAVIOR TEST: PASS")
print(f"check_count={checks}")
print(f"malformed_candidate_cases={malformed_cases}")
print("canonical_compatibility_rules=0")
print("canonical_compatibility_conflicts=0")
print("synthetic_action_predicate_candidates=2")
print("synthetic_role_layout_candidates=2")
print("zero_capability_reference_fixture=1")
print("multiple_capability_reference_fixture=1")
print("explicit_unknown_states=1")
print("explicit_unsupported_states=2")
print("structurally_incomplete_states=1")
print("ambiguous_states=1")
print("conflicted_states=1")
print("selected_predicate=0")
print("selected_frame=0")
print("selected_participant_assignment=0")
print("candidate_meaning=0")
print("selected_meaning=0")
print("permission_route_action_memory_delivery=0")
print("evidence_validity_truth=0")
print("clarification_refusal_blocked_progression=0")
print("filesystem_network_external_resource_llm_embedding_similarity=0")
