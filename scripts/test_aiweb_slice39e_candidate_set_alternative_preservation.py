#!/usr/bin/env python3
"""Behavior and adversarial verification for AI.Web Slice 39E."""

from __future__ import annotations

import builtins
from contextlib import ExitStack
from dataclasses import FrozenInstanceError, fields, replace
from itertools import permutations
from pathlib import Path
import socket
import sys
import urllib.request
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aiweb_language_core_bootstrap.input_event_custody import capture_input_event
from aiweb_language_core_bootstrap.source_field_projection import project_source_field
from aiweb_language_core_bootstrap.resonant_operator_candidate_binding import bind_resonant_operator_candidates
from aiweb_language_core_bootstrap.candidate_resonant_phase_trail import construct_candidate_resonant_phase_trails
from aiweb_language_core_bootstrap.scope_attachment_reference_constraints import apply_scope_attachment_reference_constraints
from aiweb_language_core_bootstrap.deterministic_structural_derivation import derive_deterministic_structural_analysis
from aiweb_language_core_bootstrap.structural_concept_candidate_proposal import propose_structural_concept_candidates
from aiweb_language_core_bootstrap.predicate_role_frame_registry.predicate_role_frame_candidate_proposal import (
    build_compatibility_snapshot,
    build_exact_compatibility_rule,
    propose_predicate_role_frame_candidates,
)
from aiweb_language_core_bootstrap.candidate_meaning_construction.predecessor_custody import bind_complete_predecessor_custody
from aiweb_language_core_bootstrap.candidate_meaning_construction.candidate_semantic_content import (
    CandidateSemanticContentStatus,
    assemble_candidate_semantic_content,
)
from aiweb_language_core_bootstrap.candidate_meaning_construction.candidate_set_preservation import (
    CANONICAL_FIELD_ORDERS,
    DEFAULT_SET_PROFILE,
    SLICE39E_DEFERRED_SCOPE,
    SLICE39E_PERMANENT_BOUNDARIES,
    SLICE39E_REQUIRED_BEHAVIOR,
    CandidateExactDuplicateGroup,
    CandidateMaterialAlternativeReference,
    CandidateMeaningSet,
    CandidateSetMember,
    CandidateSetPreservationResult,
    CandidateSetStatus,
    CandidateSetValidationCode,
    CandidateSharedAncestryReference,
    canonical_record_mapping_39e,
    deterministic_digest,
    expected_candidate_set_digest,
    expected_candidate_set_id,
    expected_result_id,
    preserve_candidate_set,
    validate_alternative_reference,
    validate_candidate_set,
    validate_duplicate_group,
    validate_member,
    validate_preservation_result,
    validate_profile,
    validate_shared_ancestry,
)

checks = 0
malformed_cases = 0
explicit_rejections = 0


def check(condition: object, label: str) -> None:
    global checks
    checks += 1
    if condition is not True:
        raise AssertionError(label)


def forbidden(*args: object, **kwargs: object) -> object:
    raise AssertionError("external side effect attempted")


def pipeline(text: str, sequence: int, source_id: str = "fixture.user"):
    custody = capture_input_event(text, source_id=source_id, channel_id="fixture.chat", sequence_number=sequence)
    check(custody.event is not None, f"custody event {sequence}")
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
    slice37 = propose_structural_concept_candidates(custody, projection, structural)
    return custody, projection, binding, trails, constraints, structural, slice37


def candidate_for(chain, root: str, registry_key: str):
    concept = chain[-1].concept_candidates[0]
    sense = chain[-1].sense_candidates[0]
    frame_key = {
        "inspect": "inspect_read_only",
        "report": "report_attributed_content",
        "request": "request_non_authorizing",
    }[root]
    rule = build_exact_compatibility_rule(
        rule_key=f"fixture.set.{root}.{registry_key}",
        action_root_key=root,
        concept_id=concept.concept_id,
        sense_id=sense.sense_id,
        allowed_frame_keys=(frame_key,),
    )
    slice38 = propose_predicate_role_frame_candidates(
        chain[-1],
        compatibility_snapshot=build_compatibility_snapshot(rules=(rule,), registry_key=registry_key),
    )
    bound = bind_complete_predecessor_custody(*chain, slice38)
    result = assemble_candidate_semantic_content(bound, chain[4], chain[6], slice38)
    check(result.status is CandidateSemanticContentStatus.ASSEMBLED, f"{root} 39D assembled")
    check(result.assembly is not None, f"{root} assembly exists")
    return result


def assert_zero_authority(result: CandidateSetPreservationResult, label: str) -> None:
    for name in (
        "candidates_ranked", "confidence_scores_created", "preferred_candidate_created",
        "winner_selected", "nearest_candidate_selected", "tie_breaking_performed",
        "ambiguity_resolved", "ambiguous_meaning_state_created", "gate_progression_created",
        "truth_determined", "evidence_validated", "permission_granted", "route_created",
        "action_performed", "memory_accessed", "rendered", "delivered",
        "filesystem_read_performed", "filesystem_write_performed", "network_access_performed",
        "external_resource_loaded", "language_model_used", "embedding_used",
        "semantic_similarity_used",
    ):
        check(getattr(result, name) is False, f"{label}: result {name} false")
    if result.candidate_set is not None:
        for name in (
            "candidates_ranked", "confidence_scores_created", "preferred_candidate_created",
            "winner_selected", "nearest_candidate_selected", "tie_breaking_performed",
            "ambiguity_resolved", "ambiguous_meaning_state_created", "gate_progression_created",
            "truth_determined", "evidence_validated", "permission_granted", "route_created",
            "action_performed", "memory_accessed", "rendered", "delivered",
        ):
            check(getattr(result.candidate_set, name) is False, f"{label}: set {name} false")
        for member in result.candidate_set.members:
            check(member.ranked is False, f"{label}: member not ranked")
            check(member.confidence_scored is False, f"{label}: member no confidence")
            check(member.preferred is False, f"{label}: member not preferred")
            check(member.selected is False, f"{label}: member not selected")
            check(member.ambiguous_state_created is False, f"{label}: member no ambiguous state")
        for alternative in result.candidate_set.material_alternative_references:
            check(alternative.ambiguity_determined is False, f"{label}: alternative no ambiguity")
            check(alternative.ranked is False, f"{label}: alternative unranked")
            check(alternative.preferred is False, f"{label}: alternative not preferred")
            check(alternative.selected is False, f"{label}: alternative unselected")
            check(alternative.tie_broken is False, f"{label}: no tie break")


def assert_rejected(result: CandidateSetPreservationResult, label: str, expected: CandidateSetValidationCode | None = None) -> None:
    global explicit_rejections
    explicit_rejections += 1
    check(type(result) is CandidateSetPreservationResult, f"{label}: typed result")
    check(result.status is CandidateSetStatus.SET_REJECTED, f"{label}: rejected")
    check(result.candidate_set is None, f"{label}: no set")
    check(bool(result.issues), f"{label}: issues retained")
    report = validate_preservation_result(result)
    check(report.ok, f"{label}: rejection record validates {report.issues[:2]}")
    if expected is not None:
        check(any(item.code is expected for item in result.issues), f"{label}: expected code")
    assert_zero_authority(result, label)


# Closed authority profile and canonical schema.
check(validate_profile(DEFAULT_SET_PROFILE).ok, "profile validates")
for name in (
    "ranking_allowed", "confidence_scoring_allowed", "preferred_candidate_allowed",
    "winner_selection_allowed", "nearest_candidate_allowed", "tie_breaking_allowed",
    "automatic_ambiguity_resolution_allowed", "ambiguous_meaning_state_creation_allowed",
    "gate_progression_allowed", "truth_evidence_permission_allowed",
    "route_action_memory_rendering_delivery_allowed",
):
    check(getattr(DEFAULT_SET_PROFILE, name) is False, f"profile {name} false")
check(len(SLICE39E_REQUIRED_BEHAVIOR) >= 13, "required behavior inventory")
check(len(SLICE39E_PERMANENT_BOUNDARIES) >= 20, "permanent boundary inventory")
check(len(SLICE39E_DEFERRED_SCOPE) >= 15, "deferred scope inventory")
check(len(CANONICAL_FIELD_ORDERS) == 8, "eight canonical record types")
for record_type, order in CANONICAL_FIELD_ORDERS.items():
    check(order == tuple(item.name for item in fields(record_type)), f"canonical order {record_type.__name__}")

# Exact same-source candidate records with distinct governed content.
chain = pipeline("Inspect Concept Admission.", 1)
inspect_result = candidate_for(chain, "inspect", "fixture.set.inspect")
report_result = candidate_for(chain, "report", "fixture.set.report")
request_result = candidate_for(chain, "request", "fixture.set.request")
unique_candidates = (inspect_result, report_result, request_result)
check(len({item.result_id for item in unique_candidates}) == 3, "three exact unique candidate identities")
check(len({item.source_event_id for item in unique_candidates}) == 1, "one source event")
check(len({item.source_sha256 for item in unique_candidates}) == 1, "one source checksum")

# Zero candidates are represented by an immutable explicit set.
with ExitStack() as stack:
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    zero = preserve_candidate_set(())
check(zero.status is CandidateSetStatus.ZERO_CANDIDATES, "zero status")
check(zero.reason_code == "zero_candidates_preserved_explicitly", "zero reason")
check(zero.candidate_set is not None, "zero set exists")
check(zero.candidate_set.members == (), "zero members")
check(zero.candidate_set.candidate_results == (), "zero records")
check(zero.candidate_set.source_event_id is None, "zero source absent")
check(zero.zero_candidates_preserved is True, "zero preservation flag")
check(validate_preservation_result(zero).ok, "zero result validates")
check(validate_candidate_set(zero.candidate_set).ok, "zero set validates")
assert_zero_authority(zero, "zero")

# One candidate remains one candidate and is not selected by cardinality.
one = preserve_candidate_set((inspect_result,))
check(one.status is CandidateSetStatus.ONE_CANDIDATE, "one status")
check(one.input_candidate_count == 1, "one input count")
check(one.unique_candidate_count == 1, "one unique count")
check(one.one_candidate_preserved_without_selection is True, "one preserved flag")
check(one.candidate_set is not None, "one set")
check(len(one.candidate_set.members) == 1, "one member")
check(one.candidate_set.members[0].selected is False, "one not selected")
check(one.candidate_set.material_alternative_references == (), "one no alternatives")
check(one.candidate_set.exact_duplicate_groups == (), "one no duplicates")
check(validate_preservation_result(one).ok, "one validates")
assert_zero_authority(one, "one")

# Multiple candidates remain independent and deterministic under every input permutation.
multiple = preserve_candidate_set(unique_candidates)
check(multiple.status is CandidateSetStatus.MULTIPLE_CANDIDATES, "multiple status")
check(multiple.input_candidate_count == 3, "multiple input count")
check(multiple.unique_candidate_count == 3, "multiple unique count")
check(multiple.exact_duplicate_occurrence_count == 0, "multiple duplicate count")
check(multiple.alternative_reference_count == 3, "three pair alternatives")
check(multiple.multiple_candidates_preserved_independently is True, "multiple preservation flag")
check(multiple.candidate_set is not None, "multiple set")
check(validate_preservation_result(multiple).ok, "multiple validates")
check(multiple.candidate_set.candidate_set_id == expected_candidate_set_id(multiple.candidate_set), "set identity")
check(multiple.candidate_set.canonical_digest == expected_candidate_set_digest(multiple.candidate_set), "set digest")
check(multiple.result_id == expected_result_id(multiple), "result identity")
for ordering in permutations(unique_candidates):
    reordered = preserve_candidate_set(ordering)
    check(reordered == multiple, f"permutation deterministic {tuple(item.result_id[-6:] for item in ordering)}")
assert_zero_authority(multiple, "multiple")

# Candidate-specific limitation, missing-role, conflict, effect and capability custody.
by_result_id = {item.result_id: item for item in unique_candidates}
for member in multiple.candidate_set.members:
    source = by_result_id[member.candidate_result_id]
    assert source.assembly is not None
    content = source.assembly.candidate_meaning_content
    check(member.limitation_refs == content.limitations, "member limitations exact")
    check(member.missing_role_refs == content.missing_role_refs, "member missing roles exact")
    check(member.conflicting_role_refs == content.conflicting_role_refs, "member conflicts exact")
    check(member.effect_boundary_refs == content.effect_boundary_refs, "member effects exact")
    check(member.capability_reference_refs == content.capability_reference_candidate_refs, "member capabilities exact")
    check(member.source_span_ids == source.assembly.predecessor_custody.provenance.source_span_ids, "member source spans exact")
    check(validate_member(member).ok, "member validates")

# Shared ancestry is explicit and never merges lineages.
check(len(multiple.candidate_set.shared_ancestry_references) == 1, "one shared ancestry record")
shared = multiple.candidate_set.shared_ancestry_references[0]
check(validate_shared_ancestry(shared).ok, "shared ancestry validates")
check(shared.source_event_id == inspect_result.source_event_id, "shared source event")
check(shared.source_sha256 == inspect_result.source_sha256, "shared source checksum")
check(shared.member_ids == tuple(item.member_id for item in multiple.candidate_set.members), "shared member mapping")
check(shared.ancestry_preserved is True, "ancestry preserved")
check(shared.lineages_merged is False, "lineages not merged")
check(bool(shared.shared_source_span_ids), "shared source spans retained")

# Material alternative means exact governed record difference, not ambiguity.
for alternative in multiple.candidate_set.material_alternative_references:
    check(validate_alternative_reference(alternative).ok, "alternative validates")
    check(alternative.exact_duplicate is False, "alternative not duplicate")
    check(alternative.materially_distinct_by_exact_content is True, "alternative exact distinction")
    check(bool(alternative.exact_difference_dimensions), "difference dimensions retained")
    check(alternative.shared_ancestry_ref == shared.shared_ancestry_id, "alternative shared ancestry ref")
    check(alternative.ambiguity_determined is False, "alternative not ambiguity decision")

# Exact duplicates remain visible as occurrences and an explicit duplicate group.
duplicated = preserve_candidate_set((inspect_result, report_result, inspect_result, request_result, inspect_result))
check(duplicated.status is CandidateSetStatus.MULTIPLE_CANDIDATES, "duplicate set status")
check(duplicated.input_candidate_count == 5, "duplicate input count")
check(duplicated.unique_candidate_count == 3, "duplicate unique count")
check(duplicated.exact_duplicate_occurrence_count == 2, "duplicate occurrence count")
check(len(duplicated.candidate_set.members) == 5, "all duplicate occurrences preserved")
check(len(duplicated.candidate_set.candidate_results) == 3, "unique exact records stored")
check(len(duplicated.candidate_set.exact_duplicate_groups) == 1, "one duplicate group")
duplicate_group = duplicated.candidate_set.exact_duplicate_groups[0]
check(validate_duplicate_group(duplicate_group).ok, "duplicate group validates")
check(duplicate_group.occurrence_count == 3, "three inspect occurrences")
check(len(duplicate_group.duplicate_member_ids) == 2, "two duplicate member refs")
check(duplicate_group.silently_collapsed is False, "duplicates not silently collapsed")
inspect_members = tuple(item for item in duplicated.candidate_set.members if item.candidate_result_id == inspect_result.result_id)
check(tuple(item.duplicate_occurrence_index for item in inspect_members) == (1, 2, 3), "duplicate indexes deterministic")
check(all(item.exact_duplicate_detected for item in inspect_members), "duplicate detection marked")
check(duplicated.alternative_reference_count == 3, "duplicates do not create false alternatives")
check(validate_preservation_result(duplicated).ok, "duplicate set validates")
check(preserve_candidate_set(tuple(reversed((inspect_result, report_result, inspect_result, request_result, inspect_result)))) == duplicated, "duplicate ordering independent")
assert_zero_authority(duplicated, "duplicated")

# Constructor rejects wrong exact input and profile types without throwing.
invalid_values = (None, 0, 1.0, True, "bad", [], {}, object())
for invalid in invalid_values:
    rejected = preserve_candidate_set(invalid)
    malformed_cases += 1
    assert_rejected(rejected, f"invalid tuple {type(invalid).__name__}", CandidateSetValidationCode.INVALID_TUPLE)
for invalid in invalid_values:
    rejected = preserve_candidate_set((invalid,))
    malformed_cases += 1
    assert_rejected(rejected, f"invalid member {type(invalid).__name__}", CandidateSetValidationCode.TYPE_MISMATCH)
for invalid in invalid_values:
    rejected = preserve_candidate_set((), profile=invalid)
    malformed_cases += 1
    assert_rejected(rejected, f"invalid profile {type(invalid).__name__}", CandidateSetValidationCode.TYPE_MISMATCH)

# A 39D no-candidate result is not laundered into a set member; zero is an empty tuple.
zero_slice38 = propose_predicate_role_frame_candidates(chain[-1])
zero_bound = bind_complete_predecessor_custody(*chain, zero_slice38)
zero_39d = assemble_candidate_semantic_content(zero_bound, chain[4], chain[6], zero_slice38)
check(zero_39d.status is CandidateSemanticContentStatus.NO_CANDIDATE_CONTENT, "39D zero fixture")
assert_rejected(preserve_candidate_set((zero_39d,)), "39D zero as member", CandidateSetValidationCode.CANDIDATE_NOT_ASSEMBLED)

# Candidate sets cannot mix source events, even when surface text is identical.
other_chain = pipeline("Inspect Concept Admission.", 30, source_id="fixture.other")
other_result = candidate_for(other_chain, "inspect", "fixture.set.other")
assert_rejected(preserve_candidate_set((inspect_result, other_result)), "cross-source set", CandidateSetValidationCode.SOURCE_EVENT_MISMATCH)

# Immutable records.
try:
    multiple.candidate_set.status = CandidateSetStatus.ONE_CANDIDATE  # type: ignore[misc]
    raise AssertionError("set mutation unexpectedly succeeded")
except (FrozenInstanceError, AttributeError):
    check(True, "set immutable")

# Independent validators reject identity, count, mapping and authority mutations.
base_set = multiple.candidate_set
assert base_set is not None
member = base_set.members[0]
member_mutations = (
    replace(member, member_id="candidate_set_member:sha256:" + "0" * 64),
    replace(member, deterministic_position=0),
    replace(member, candidate_result_id="candidate_semantic_content_result:sha256:" + "0" * 64),
    replace(member, limitation_refs=("fabricated:limitation",)),
    replace(member, missing_role_refs=("fabricated:missing",)),
    replace(member, conflicting_role_refs=("fabricated:conflict",)),
    replace(member, effect_boundary_refs=("fabricated:effect",)),
    replace(member, capability_reference_refs=("fabricated:capability",)),
    replace(member, ranked=True),
    replace(member, confidence_scored=True),
    replace(member, preferred=True),
    replace(member, selected=True),
    replace(member, ambiguous_state_created=True),
)
for index, mutated in enumerate(member_mutations):
    malformed_cases += 1
    check(not validate_member(mutated).ok, f"member mutation {index} rejected")

alternative = base_set.material_alternative_references[0]
alternative_mutations = (
    replace(alternative, alternative_reference_id="candidate_material_alternative:sha256:" + "0" * 64),
    replace(alternative, exact_difference_dimensions=()),
    replace(alternative, exact_duplicate=True),
    replace(alternative, materially_distinct_by_exact_content=False),
    replace(alternative, ambiguity_determined=True),
    replace(alternative, ranked=True),
    replace(alternative, preferred=True),
    replace(alternative, selected=True),
    replace(alternative, tie_broken=True),
)
for index, mutated in enumerate(alternative_mutations):
    malformed_cases += 1
    check(not validate_alternative_reference(mutated).ok, f"alternative mutation {index} rejected")

set_mutations = (
    replace(base_set, candidate_set_id="candidate_meaning_set:sha256:" + "0" * 64),
    replace(base_set, canonical_digest="0" * 64),
    replace(base_set, status=CandidateSetStatus.ONE_CANDIDATE),
    replace(base_set, members=tuple(reversed(base_set.members))),
    replace(base_set, input_candidate_count=999),
    replace(base_set, unique_candidate_count=999),
    replace(base_set, exact_duplicate_occurrence_count=999),
    replace(base_set, alternative_reference_count=999),
    replace(base_set, deterministic_ordering_verified=False),
    replace(base_set, exact_duplicate_detection_verified=False),
    replace(base_set, duplicate_occurrences_preserved=False),
    replace(base_set, shared_ancestry_preserved=False),
    replace(base_set, candidate_specific_boundaries_preserved=False),
    replace(base_set, candidates_ranked=True),
    replace(base_set, confidence_scores_created=True),
    replace(base_set, preferred_candidate_created=True),
    replace(base_set, winner_selected=True),
    replace(base_set, nearest_candidate_selected=True),
    replace(base_set, tie_breaking_performed=True),
    replace(base_set, ambiguity_resolved=True),
    replace(base_set, ambiguous_meaning_state_created=True),
    replace(base_set, gate_progression_created=True),
    replace(base_set, truth_determined=True),
    replace(base_set, evidence_validated=True),
    replace(base_set, permission_granted=True),
    replace(base_set, route_created=True),
    replace(base_set, action_performed=True),
    replace(base_set, memory_accessed=True),
    replace(base_set, rendered=True),
    replace(base_set, delivered=True),
)
for index, mutated in enumerate(set_mutations):
    malformed_cases += 1
    check(not validate_candidate_set(mutated).ok, f"set mutation {index} rejected")

result_mutations = (
    replace(multiple, result_id="candidate_set_preservation_result:sha256:" + "0" * 64),
    replace(multiple, status=CandidateSetStatus.ONE_CANDIDATE),
    replace(multiple, input_candidate_count=999),
    replace(multiple, unique_candidate_count=999),
    replace(multiple, alternative_reference_count=999),
    replace(multiple, candidates_ranked=True),
    replace(multiple, confidence_scores_created=True),
    replace(multiple, preferred_candidate_created=True),
    replace(multiple, winner_selected=True),
    replace(multiple, nearest_candidate_selected=True),
    replace(multiple, tie_breaking_performed=True),
    replace(multiple, ambiguity_resolved=True),
    replace(multiple, ambiguous_meaning_state_created=True),
    replace(multiple, gate_progression_created=True),
    replace(multiple, truth_determined=True),
    replace(multiple, evidence_validated=True),
    replace(multiple, permission_granted=True),
    replace(multiple, route_created=True),
    replace(multiple, action_performed=True),
    replace(multiple, filesystem_read_performed=True),
    replace(multiple, filesystem_write_performed=True),
    replace(multiple, network_access_performed=True),
    replace(multiple, external_resource_loaded=True),
    replace(multiple, language_model_used=True),
    replace(multiple, embedding_used=True),
    replace(multiple, semantic_similarity_used=True),
)
for index, mutated in enumerate(result_mutations):
    malformed_cases += 1
    check(not validate_preservation_result(mutated).ok, f"result mutation {index} rejected")

# Canonical mappings remain stable for every public record type.
records = (
    DEFAULT_SET_PROFILE,
    *duplicated.candidate_set.members,
    *duplicated.candidate_set.exact_duplicate_groups,
    *duplicated.candidate_set.shared_ancestry_references,
    *duplicated.candidate_set.material_alternative_references,
    duplicated.candidate_set,
    duplicated,
)
for item in records:
    first = canonical_record_mapping_39e(item)
    second = canonical_record_mapping_39e(item)
    check(first == second, f"canonical stable {type(item).__name__}")
    check(deterministic_digest(first) == deterministic_digest(second), f"digest stable {type(item).__name__}")

print("AI.WEB SLICE 39E BEHAVIOR TEST: PASS")
print(f"check_count={checks}")
print(f"malformed_validation_cases={malformed_cases}")
print(f"explicit_rejection_cases={explicit_rejections}")
print(f"required_behavior_count={len(SLICE39E_REQUIRED_BEHAVIOR)}")
print(f"canonical_record_types={len(CANONICAL_FIELD_ORDERS)}")
print(f"zero_candidate_sets={1 if zero.status is CandidateSetStatus.ZERO_CANDIDATES else 0}")
print(f"one_candidate_sets={1 if one.status is CandidateSetStatus.ONE_CANDIDATE else 0}")
print(f"multiple_candidate_members={multiple.input_candidate_count}")
print(f"unique_candidates={multiple.unique_candidate_count}")
print(f"exact_duplicate_occurrences={duplicated.exact_duplicate_occurrence_count}")
print(f"material_alternative_references={multiple.alternative_reference_count}")
print(f"shared_ancestry_references={len(multiple.candidate_set.shared_ancestry_references)}")
print("candidate_specific_limitations_missing_roles_conflicts_effects_capabilities=1")
print("ranking_confidence_preference_selection=0")
print("nearest_candidate_tie_breaking=0")
print("ambiguity_resolution_ambiguous_state=0")
print("gate_progression=0")
print("truth_evidence_permission=0")
print("route_action_memory_rendering_delivery=0")
print("filesystem_network_external_resource=0")
print("language_model_embedding_similarity=0")
