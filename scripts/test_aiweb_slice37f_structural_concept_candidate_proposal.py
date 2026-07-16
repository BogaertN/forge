#!/usr/bin/env python3
"""Behavior and adversarial verification for AI.Web Slice 37F."""

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
    derive_deterministic_structural_analysis,
)
from aiweb_language_core_bootstrap.input_event_custody import capture_input_event
from aiweb_language_core_bootstrap.resonant_operator_candidate_binding import (
    bind_resonant_operator_candidates,
)
from aiweb_language_core_bootstrap.scope_attachment_reference_constraints import (
    apply_scope_attachment_reference_constraints,
)
from aiweb_language_core_bootstrap.source_field_projection import project_source_field
from aiweb_language_core_bootstrap.structural_concept_candidate_proposal import (
    LexicalOccurrenceDisposition,
    ProposalResultStatus,
    SLICE37F_NON_AUTHORITY_BOUNDARIES,
    build_default_structural_concept_proposal_profile,
    propose_structural_concept_candidates,
    validate_concept_candidate,
    validate_lexical_occurrence,
    validate_proposal_profile,
    validate_proposal_result,
    validate_registry_snapshot,
    validate_sense_candidate,
    validate_structural_ancestry,
)


checks = 0


def check(condition: object, label: str) -> None:
    global checks
    checks += 1
    if condition is not True:
        raise AssertionError(label)


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
    check(binding.binding_set is not None, f"binding {sequence}")
    trails = construct_candidate_resonant_phase_trails(projection, binding)
    check(trails.phase_trail_set is not None, f"trails {sequence}")
    constraints = apply_scope_attachment_reference_constraints(
        projection,
        binding,
        trails,
    )
    check(constraints.constraint_set is not None, f"constraints {sequence}")
    structural = derive_deterministic_structural_analysis(
        custody,
        projection,
        binding,
        trails,
        constraints,
    )
    check(structural.structural_set is not None, f"structural set {sequence}")
    proposal = propose_structural_concept_candidates(
        custody,
        projection,
        structural,
    )
    return custody, projection, structural, proposal


profile = build_default_structural_concept_proposal_profile()
check(profile.profile_id == profile.expected_id(), "profile stable identity")
check(validate_proposal_profile(profile).ok, "profile validates")
for name in (
    "explicit_invocation_required",
    "offline_only",
    "standard_library_only",
    "deterministic",
    "immutable_records",
    "exact_source_preservation_required",
    "exact_case_sensitive_matching",
    "ascii_identifier_boundary_profile",
    "structural_result_consumption_allowed",
    "exact_term_lookup_allowed",
    "concept_candidate_proposal_allowed",
    "sense_candidate_proposal_allowed",
    "preserve_zero_one_many",
    "preserve_unresolved_alternatives",
    "explicit_unknown_required",
    "explicit_unsupported_required",
):
    check(getattr(profile, name) is True, f"profile true boundary {name}")
for name in (
    "normalization_allowed",
    "casefolding_allowed",
    "spelling_correction_allowed",
    "stemming_allowed",
    "synonym_expansion_allowed",
    "nearest_match_allowed",
    "frequency_ranking_allowed",
    "semantic_similarity_allowed",
    "model_inference_allowed",
    "dictionary_fallback_allowed",
    "candidate_meaning_creation_allowed",
    "selected_meaning_allowed",
    "selected_sense_allowed",
    "predicate_identity_allowed",
    "participant_role_assignment_allowed",
    "truth_determination_allowed",
    "evidence_validity_determination_allowed",
    "clarification_allowed",
    "permission_inference_allowed",
    "capability_routing_allowed",
    "tool_invocation_allowed",
    "action_execution_allowed",
    "memory_read_allowed",
    "memory_write_allowed",
    "outward_rendering_allowed",
    "delivery_allowed",
):
    check(getattr(profile, name) is False, f"profile false boundary {name}")
check(
    profile.non_authority_boundaries == SLICE37F_NON_AUTHORITY_BOUNDARIES,
    "profile boundary set exact",
)

# Ambiguous exact domain term preserves two concept and two sense candidates.
concept_custody, concept_projection, concept_structural, concept_result = pipeline(
    "concept",
    1,
)
check(
    concept_result.status is ProposalResultStatus.CANDIDATES_WITH_UNRESOLVED_STATES,
    "ambiguous status",
)
check(concept_result.lexical_occurrence_count == 1, "ambiguous occurrence count")
check(concept_result.concept_candidate_count == 2, "ambiguous concept count")
check(concept_result.sense_candidate_count == 2, "ambiguous sense count")
check(concept_result.explicit_unknown_count == 0, "ambiguous no unknown")
check(concept_result.explicit_unsupported_count == 0, "ambiguous no unsupported")
check(validate_proposal_result(concept_result).ok, "ambiguous result validates")
check(concept_result.result_id == concept_result.expected_id(), "ambiguous result stable")
check(validate_registry_snapshot(concept_result.registry_snapshot).ok, "snapshot validates")
check(concept_result.registry_snapshot.concept_count == 4, "snapshot concept count")
check(concept_result.registry_snapshot.sense_count == 5, "snapshot sense count")
check(concept_result.registry_snapshot.lexical_reference_count == 11, "snapshot lexical count")
check(concept_result.registry_snapshot.mapping_count == 10, "snapshot mapping count")
check(concept_result.registry_snapshot.semantic_class_count == 6, "snapshot class count")
check(concept_result.registry_snapshot.relation_family_count == 6, "snapshot family count")
check(concept_result.registry_snapshot.relation_type_count == 6, "snapshot relation type count")
check(concept_result.registry_snapshot.relation_instance_count == 0, "snapshot no relation instances")
occurrence = concept_result.lexical_occurrences[0]
check(validate_lexical_occurrence(occurrence).ok, "ambiguous occurrence validates")
check(occurrence.exact_source_text == "concept", "ambiguous exact source")
check(occurrence.code_point_start == 0 and occurrence.code_point_end == 7, "ambiguous code points")
check(occurrence.utf8_byte_start == 0 and occurrence.utf8_byte_end == 7, "ambiguous utf8 bytes")
check(len(occurrence.source_span_ids) == 7, "ambiguous source span ancestry")
check(occurrence.disposition is LexicalOccurrenceDisposition.AMBIGUOUS, "ambiguous disposition")
check(occurrence.candidate_order_is_ranked is False, "ambiguous no rank")
check(occurrence.selected_concept_id is None, "ambiguous no selected concept")
check(occurrence.selected_sense_id is None, "ambiguous no selected sense")
check(set(item.concept_key for item in concept_result.concept_candidates) == {
    "forge_controlled_concept_identity",
    "source_expression_form",
}, "ambiguous exact concept identities")
check(set(item.sense_key for item in concept_result.sense_candidates) == {
    "governed_semantic_resource_identity",
    "metalinguistic_expression_mention",
}, "ambiguous exact sense identities")
for index, candidate in enumerate(concept_result.concept_candidates):
    check(validate_concept_candidate(candidate).ok, f"concept candidate validates {index}")
    check(candidate.proposal_id == candidate.expected_id(), f"concept candidate stable {index}")
    check(candidate.candidate_only, f"concept candidate only {index}")
    check(not candidate.selected, f"concept candidate unselected {index}")
    check(len(candidate.unresolved_alternative_concept_ids) == 1, f"concept alternative preserved {index}")
for index, candidate in enumerate(concept_result.sense_candidates):
    check(validate_sense_candidate(candidate).ok, f"sense candidate validates {index}")
    check(candidate.proposal_id == candidate.expected_id(), f"sense candidate stable {index}")
    check(candidate.candidate_only, f"sense candidate only {index}")
    check(not candidate.selected, f"sense candidate unselected {index}")
    check(len(candidate.unresolved_alternative_sense_ids) == 1, f"sense alternative preserved {index}")

# Structural plurality and complete ancestry from a 36G multi-candidate result.
_, _, structural_source, structural_result = pipeline(
    "Do not Concept Admission.",
    2,
)
check(structural_result.status is ProposalResultStatus.CANDIDATES_PROPOSED, "one-to-one status")
check(structural_result.lexical_occurrence_count == 1, "one-to-one occurrence")
check(structural_result.concept_candidate_count == 1, "one-to-one concept")
check(structural_result.sense_candidate_count == 1, "one-to-one sense")
check(
    structural_result.structural_ancestry_count
    == structural_source.structural_set.candidate_count,
    "all structural candidates preserved",
)
check(structural_result.structural_ancestry_count > 1, "structural plurality fixture")
for index, ancestry in enumerate(structural_result.structural_ancestries):
    check(validate_structural_ancestry(ancestry).ok, f"ancestry validates {index}")
    check(ancestry.ancestry_id == ancestry.expected_id(), f"ancestry stable {index}")
    check(ancestry.structural_result_id == structural_source.result_id, f"ancestry result {index}")
    check(bool(ancestry.operator_graph_id), f"operator graph ancestry {index}")
    check(bool(ancestry.source_coverage_proof_id), f"coverage ancestry {index}")
    check(ancestry.candidate_only, f"ancestry candidate only {index}")
    check(not ancestry.selected_structure, f"ancestry unselected {index}")
check(
    tuple(item.structural_candidate_id for item in structural_result.structural_ancestries)
    == tuple(item.structural_candidate_id for item in structural_source.structural_set.candidates),
    "structural candidate order preserved",
)
check(
    structural_result.lexical_occurrences[0].exact_source_text == "Concept Admission",
    "multiword exact occurrence",
)
check(
    structural_result.concept_candidates[0].concept_key == "concept_admission",
    "one-to-one exact concept",
)
check(
    structural_result.sense_candidates[0].sense_key
    == "human_approved_semantic_admission_act",
    "one-to-one exact sense",
)

# Known lexical reference with no admitted mapping is explicit unknown.
_, _, _, unmapped = pipeline("mapping", 3)
check(unmapped.status is ProposalResultStatus.EXPLICIT_UNKNOWN, "unmapped result status")
check(unmapped.lexical_occurrence_count == 1, "unmapped occurrence")
check(unmapped.concept_candidate_count == 0, "unmapped no concepts")
check(unmapped.sense_candidate_count == 0, "unmapped no senses")
check(unmapped.explicit_unknown_count == 1, "unmapped unknown count")
check(unmapped.explicit_unsupported_count == 0, "unmapped unsupported count")
check(unmapped.lexical_occurrences[0].disposition is LexicalOccurrenceDisposition.UNMAPPED, "unmapped disposition")
check(unmapped.lexical_occurrences[0].explicit_unknown, "unmapped explicit unknown")

# Reviewed unsupported mapping remains unsupported, not unknown or rejected.
_, _, _, unsupported = pipeline("sense", 4)
check(unsupported.status is ProposalResultStatus.EXPLICIT_UNSUPPORTED, "unsupported status")
check(unsupported.lexical_occurrence_count == 1, "unsupported occurrence")
check(unsupported.concept_candidate_count == 0, "unsupported no concepts")
check(unsupported.sense_candidate_count == 0, "unsupported no senses")
check(unsupported.explicit_unknown_count == 0, "unsupported no unknown")
check(unsupported.explicit_unsupported_count == 1, "unsupported count")
check(unsupported.lexical_occurrences[0].disposition is LexicalOccurrenceDisposition.UNSUPPORTED, "unsupported disposition")
check(unsupported.lexical_occurrences[0].explicit_unsupported, "unsupported explicit flag")

# No exact controlled occurrence returns a first-class unknown result.
_, _, _, unknown = pipeline("banana", 5)
check(unknown.status is ProposalResultStatus.EXPLICIT_UNKNOWN, "no-match unknown status")
check(unknown.lexical_occurrence_count == 0, "no-match no occurrence")
check(unknown.explicit_unknown_count == 1, "no-match unknown count")
check(unknown.reason_code == "no_exact_controlled_lexical_occurrence", "no-match reason")

# Exact matching is case-sensitive and never normalizes.
_, _, _, wrong_case = pipeline("Concept", 6)
check(wrong_case.status is ProposalResultStatus.EXPLICIT_UNKNOWN, "wrong case unknown")
check(wrong_case.lexical_occurrence_count == 0, "wrong case no normalized match")
_, _, _, padded = pipeline(" concept ", 7)
check(padded.lexical_occurrence_count == 1, "delimited exact match")
check(padded.lexical_occurrences[0].code_point_start == 1, "delimited exact start")

# ASCII identifier boundary prevents substring promotion.
_, _, _, internal = pipeline("concept_admission", 8)
check(internal.lexical_occurrence_count == 1, "internal identifier one occurrence")
check(internal.lexical_occurrences[0].exact_source_text == "concept_admission", "internal identifier exact")
check(internal.concept_candidate_count == 1, "internal identifier one concept")
check(internal.concept_candidates[0].concept_key == "concept_admission", "no substring concept promotion")
_, _, _, prefixed = pipeline("preconcept", 9)
check(prefixed.lexical_occurrence_count == 0, "identifier prefix blocks substring")

# Repeated exact occurrences remain separate and unranked.
_, _, _, repeated = pipeline("concept concept", 10)
check(repeated.lexical_occurrence_count == 2, "repeated occurrence count")
check(repeated.concept_candidate_count == 4, "repeated concept candidates")
check(repeated.sense_candidate_count == 4, "repeated sense candidates")
check(repeated.lexical_occurrences[0].code_point_start == 0, "repeat first start")
check(repeated.lexical_occurrences[1].code_point_start == 8, "repeat second start")
check(repeated.lexical_occurrences[0].occurrence_id != repeated.lexical_occurrences[1].occurrence_id, "repeat distinct identities")
check(not repeated.candidate_order_is_ranked, "repeat no ranking")

# Explicit profile limits are honored without fallback.
en_only = replace(profile, profile_id="", language_tags=("en",))
en_only = replace(en_only, profile_id=en_only.expected_id())
check(validate_proposal_profile(en_only).ok, "custom en profile validates")
_, _, internal_structural, _ = pipeline("concept_admission", 11)
# Rebuild exact predecessor records for custom profile.
custom_custody = capture_input_event("concept_admission", source_id="fixture.user", channel_id="fixture.chat", sequence_number=12)
custom_projection = project_source_field(custom_custody.event)
custom_binding = bind_resonant_operator_candidates(custom_projection)
custom_trails = construct_candidate_resonant_phase_trails(custom_projection, custom_binding)
custom_constraints = apply_scope_attachment_reference_constraints(custom_projection, custom_binding, custom_trails)
custom_structural = derive_deterministic_structural_analysis(custom_custody, custom_projection, custom_binding, custom_trails, custom_constraints)
custom_result = propose_structural_concept_candidates(custom_custody, custom_projection, custom_structural, profile=en_only)
check(custom_result.status is ProposalResultStatus.EXPLICIT_UNKNOWN, "profile excludes internal language")
check(custom_result.lexical_occurrence_count == 0, "profile no language fallback")

# Invalid profile tampering fails before proposal.
try:
    propose_structural_concept_candidates(
        concept_custody,
        concept_projection,
        concept_structural,
        profile=replace(profile, selected_sense_allowed=True),
    )
    raise AssertionError("invalid profile accepted")
except ValueError:
    check(True, "invalid profile rejected")

# Mismatched predecessor ancestry fails closed and creates no candidates.
other_custody = capture_input_event("concept", source_id="fixture.other", channel_id="fixture.chat", sequence_number=99)
mismatch = propose_structural_concept_candidates(
    other_custody,
    concept_projection,
    concept_structural,
)
check(mismatch.status is ProposalResultStatus.PREDECESSOR_REJECTED, "mismatch rejected")
check(mismatch.reason_code == "predecessor_ancestry_mismatch", "mismatch reason")
check(mismatch.lexical_occurrence_count == 0, "mismatch no occurrence")
check(mismatch.concept_candidate_count == 0, "mismatch no concept")
check(mismatch.sense_candidate_count == 0, "mismatch no sense")
check(mismatch.explicit_unsupported_count == 1, "mismatch explicit unsupported")
check(validate_proposal_result(mismatch).ok, "mismatch result validates")

# Invalid public call types fail closed without exceptions or candidates.
invalid = propose_structural_concept_candidates(None, None, None)
check(invalid.status is ProposalResultStatus.PREDECESSOR_REJECTED, "invalid type rejected")
check(invalid.reason_code == "invalid_custody_result_type", "invalid type reason")
check(invalid.lexical_occurrence_count == 0, "invalid no occurrences")
check(invalid.concept_candidate_count == 0, "invalid no concepts")
check(invalid.sense_candidate_count == 0, "invalid no senses")
check(validate_proposal_result(invalid).ok, "invalid result validates")

# Records are frozen.
try:
    concept_result.selected_meaning_created = True
    raise AssertionError("result mutation allowed")
except FrozenInstanceError:
    check(True, "result frozen")
try:
    concept_result.concept_candidates[0].selected = True
    raise AssertionError("candidate mutation allowed")
except FrozenInstanceError:
    check(True, "candidate frozen")

# Validators reject authority or identity tampering.
check(not validate_proposal_profile(replace(profile, semantic_similarity_allowed=True)).ok, "profile similarity tamper")
check(not validate_proposal_result(replace(concept_result, selected_meaning_created=True)).ok, "selected meaning tamper")
check(not validate_proposal_result(replace(concept_result, candidate_order_is_ranked=True)).ok, "ranking tamper")
check(not validate_concept_candidate(replace(concept_result.concept_candidates[0], selected=True)).ok, "concept selection tamper")
check(not validate_sense_candidate(replace(concept_result.sense_candidates[0], selected_sense_created=True)).ok, "sense selection tamper")
check(not validate_lexical_occurrence(replace(occurrence, selected_concept_id="fake")).ok, "occurrence selection tamper")
check(not validate_registry_snapshot(replace(concept_result.registry_snapshot, relation_instance_count=1)).ok, "relation instance tamper")

# Runtime performs no filesystem, network, process, model, memory, action, or delivery I/O.
with ExitStack() as stack:
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    stack.enter_context(patch.object(os, "system", forbidden))
    isolated = propose_structural_concept_candidates(
        concept_custody,
        concept_projection,
        concept_structural,
    )
check(isolated.result_id == concept_result.result_id, "side-effect isolated determinism")

# Repeated construction is byte-for-byte deterministic.
repeat = propose_structural_concept_candidates(
    concept_custody,
    concept_projection,
    concept_structural,
)
check(
    json.dumps(concept_result.to_dict(), sort_keys=True, default=str)
    == json.dumps(repeat.to_dict(), sort_keys=True, default=str),
    "repeat byte deterministic",
)

# Complete non-authority assertion on every representative result.
for result_index, result in enumerate((
    concept_result,
    structural_result,
    unmapped,
    unsupported,
    unknown,
    wrong_case,
    internal,
    repeated,
    custom_result,
    mismatch,
    invalid,
)):
    for name in (
        "candidate_order_is_ranked",
        "candidate_meaning_created",
        "selected_meaning_created",
        "selected_sense_created",
        "predicate_identity_created",
        "participant_roles_assigned",
        "truth_determined",
        "evidence_validity_determined",
        "clarification_asked",
        "permission_inferred",
        "capability_route_created",
        "tool_invoked",
        "action_performed",
        "memory_read_performed",
        "memory_write_performed",
        "outward_rendered",
        "delivered",
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "external_resource_loaded",
        "language_model_used",
        "embedding_used",
        "semantic_similarity_used",
    ):
        check(getattr(result, name) is False, f"result authority boundary {result_index}:{name}")

print("AI.WEB SLICE 37F BEHAVIOR TEST: PASS")
print(f"check_count={checks}")
print("profile_count=1")
print("registry_snapshot_count=1")
print("ambiguous_concept_candidates=2")
print("ambiguous_sense_candidates=2")
print("exact_unknown_states=2")
print("exact_unsupported_states=1")
print("candidate_meaning_selected_meaning_selected_sense=0")
print("predicate_roles_truth_evidence_clarification=0")
print("permission_routes_tools_actions_memory_rendering_delivery=0")
