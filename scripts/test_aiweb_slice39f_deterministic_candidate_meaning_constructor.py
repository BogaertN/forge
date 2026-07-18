#!/usr/bin/env python3
"""Behavior and adversarial verification for AI.Web Slice 39F."""

from __future__ import annotations

import builtins
from contextlib import ExitStack
from dataclasses import FrozenInstanceError, replace
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
from aiweb_language_core_bootstrap.candidate_meaning_construction.governed_lifecycle import (
    validate_construction_receipt,
    validate_state_record,
)
from aiweb_language_core_bootstrap.candidate_meaning_construction.deterministic_constructor import (
    DEFAULT_CONSTRUCTOR_PROFILE,
    SLICE39F_PERMANENT_BOUNDARIES,
    SLICE39F_PROHIBITED_AUTHORITY,
    SLICE39F_REQUIRED_PATH,
    CandidateMeaningConstructorInput,
    CandidateMeaningConstructorStatus,
    CandidateMeaningConstructorValidationCode,
    construct_candidate_meanings,
    validate_constructed_record,
    validate_profile,
    validate_result,
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


def pipeline(text: str, sequence: int):
    custody = capture_input_event(text, source_id="fixture.user", channel_id="fixture.chat", sequence_number=sequence)
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
    check(bool(slice37.concept_candidates), f"concept candidates {sequence}")
    check(bool(slice37.sense_candidates), f"sense candidates {sequence}")
    return custody, projection, binding, trails, constraints, structural, slice37


def exact_slice38(slice37, *, root: str, registry_key: str):
    concept = slice37.concept_candidates[0]
    sense = slice37.sense_candidates[0]
    frame_key = {
        "inspect": "inspect_read_only",
        "request": "request_non_authorizing",
        "report": "report_attributed_content",
    }[root]
    rule = build_exact_compatibility_rule(
        rule_key=f"fixture.slice39f.{root}",
        action_root_key=root,
        concept_id=concept.concept_id,
        sense_id=sense.sense_id,
        allowed_frame_keys=(frame_key,),
    )
    snapshot = build_compatibility_snapshot(rules=(rule,), registry_key=registry_key)
    return propose_predicate_role_frame_candidates(slice37, compatibility_snapshot=snapshot)


def constructor_input(chain, slice38):
    return CandidateMeaningConstructorInput(
        custody=chain[0], projection=chain[1], binding=chain[2], trails=chain[3],
        constraints=chain[4], structural=chain[5], slice37=chain[6], slice38=slice38,
    )


def assert_no_downstream(result, label: str) -> None:
    for name in (
        "raw_text_inspected", "similarity_used", "nearest_known_fallback_used",
        "hidden_repair_used", "candidate_ranked", "candidate_selected",
        "ambiguity_resolved", "gate_outcome_created", "selected_meaning_created",
        "truth_determined", "evidence_validated", "permission_granted",
        "route_created", "action_performed", "memory_accessed", "rendered",
        "delivered", "filesystem_read_performed", "filesystem_write_performed",
        "network_access_performed", "external_resource_loaded", "language_model_used",
        "embedding_used", "vector_used", "rag_used", "semantic_similarity_used",
        "manifest_integrated", "bootstrap_integrated", "slice39_closeout_created",
    ):
        check(getattr(result, name) is False, f"{label}: {name} false")
    for constructed in result.constructed_records:
        state = constructed.candidate_meaning_state
        for name in (
            "accepted_meaning", "selected_meaning", "selected_sense", "selected_predicate",
            "selected_frame", "participant_assignment", "resolved_referent",
            "ambiguous_gate_disposition", "clarification_required", "refusal",
            "blocked_progression", "rejection", "evidence_validity", "truth",
            "verified_status", "permission", "capability_availability", "route",
            "invocation", "action", "memory_access", "rendering", "delivery",
            "external_resource_loading", "language_model_authority", "embedding_authority",
            "semantic_similarity_authority",
        ):
            check(getattr(state, name) is False, f"{label}: state {name} false")


def assert_rejected(result, label: str, code: CandidateMeaningConstructorValidationCode | None = None) -> None:
    global explicit_rejections
    explicit_rejections += 1
    check(result.status is CandidateMeaningConstructorStatus.REJECTED, f"{label}: rejected")
    check(not result.constructed_records, f"{label}: no states")
    check(bool(result.issues), f"{label}: issues preserved")
    check(validate_result(result).ok, f"{label}: rejection validates")
    if code is not None:
        check(any(item.code is code for item in result.issues), f"{label}: expected code")
    assert_no_downstream(result, label)


# Sealed profile and authority inventory.
check(validate_profile(DEFAULT_CONSTRUCTOR_PROFILE).ok, "default profile validates")
check(DEFAULT_CONSTRUCTOR_PROFILE.explicitly_invoked is True, "explicit invocation")
check(DEFAULT_CONSTRUCTOR_PROFILE.exact_input_types_required is True, "exact input types")
check(DEFAULT_CONSTRUCTOR_PROFILE.offline_only is True, "offline")
check(DEFAULT_CONSTRUCTOR_PROFILE.standard_library_only is True, "stdlib")
check(DEFAULT_CONSTRUCTOR_PROFILE.read_only is True, "read only")
check(DEFAULT_CONSTRUCTOR_PROFILE.deterministic is True, "deterministic")
check(DEFAULT_CONSTRUCTOR_PROFILE.in_memory_only is True, "in memory")
check(DEFAULT_CONSTRUCTOR_PROFILE.fail_closed is True, "fail closed")
check(DEFAULT_CONSTRUCTOR_PROFILE.raw_text_inspection_allowed is False, "no raw text inspection")
check(DEFAULT_CONSTRUCTOR_PROFILE.similarity_allowed is False, "no similarity")
check(DEFAULT_CONSTRUCTOR_PROFILE.nearest_known_fallback_allowed is False, "no nearest known")
check(DEFAULT_CONSTRUCTOR_PROFILE.hidden_repair_allowed is False, "no hidden repair")
check(DEFAULT_CONSTRUCTOR_PROFILE.required_path == SLICE39F_REQUIRED_PATH, "required path sealed")
check(DEFAULT_CONSTRUCTOR_PROFILE.permanent_boundaries == SLICE39F_PERMANENT_BOUNDARIES, "boundaries sealed")
check(DEFAULT_CONSTRUCTOR_PROFILE.prohibited_authority == SLICE39F_PROHIBITED_AUTHORITY, "prohibited authority sealed")

# Explicit zero candidate preservation.
zero = construct_candidate_meanings(())
check(zero.status is CandidateMeaningConstructorStatus.ZERO_CANDIDATES, "zero status")
check(zero.input_count == 0 and zero.unique_candidate_count == 0, "zero counts")
check(zero.candidate_set_result.zero_candidates_preserved is True, "zero set preserved")
check(validate_result(zero).ok, "zero result validates")
assert_no_downstream(zero, "zero")

# Exact one-candidate construction from accepted typed Slice 37/38 outputs.
chain = pipeline("Inspect Concept Admission.", 1)
inspect38 = exact_slice38(chain[-1], root="inspect", registry_key="fixture.slice39f.inspect")
one_input = constructor_input(chain, inspect38)
with ExitStack() as stack:
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    one = construct_candidate_meanings((one_input,))
check(one.status is CandidateMeaningConstructorStatus.CONSTRUCTED, "one constructed")
check(one.input_count == 1 and one.unique_candidate_count == 1, "one counts")
check(len(one.constructed_records) == 1 and len(one.construction_receipts) == 1, "one records")
record = one.constructed_records[0]
check(validate_constructed_record(record).ok, "constructed record validates")
check(validate_state_record(record.candidate_meaning_state).ok, "state validates")
check(validate_construction_receipt(
    record.construction_receipt,
    identity=record.candidate_meaning_state.identity,
    content=record.candidate_meaning_state.content,
    provenance=record.candidate_meaning_state.provenance,
).ok, "receipt validates")
check(record.candidate_meaning_state.provenance.source_event_id == chain[0].event.input_event_id, "source event preserved")
check(record.candidate_meaning_state.provenance.source_sha256 == chain[0].event.source_sha256, "source digest preserved")
check(record.exact_typed_predecessors_verified is True, "typed predecessors verified")
check(record.exact_ancestry_verified is True, "ancestry verified")
check(record.exact_snapshots_verified is True, "snapshots verified")
check(record.source_preserved is True, "source preserved")
check(validate_result(one).ok, "one result validates")
assert_no_downstream(one, "one")


# Accepted typed predecessor records may lawfully produce zero candidates.
zero_slice38 = propose_predicate_role_frame_candidates(chain[-1])
typed_zero_input = constructor_input(chain, zero_slice38)
typed_zero = construct_candidate_meanings((typed_zero_input,))
check(typed_zero.status is CandidateMeaningConstructorStatus.ZERO_CANDIDATES, "typed zero status")
check(typed_zero.input_count == 1 and typed_zero.unique_candidate_count == 0, "typed zero counts")
check(typed_zero.reason_code == "typed_predecessors_produced_zero_candidates", "typed zero reason")
check(typed_zero.source_event_ids == (chain[0].event.input_event_id,), "typed zero source event")
check(typed_zero.source_sha256s == (chain[0].event.source_sha256,), "typed zero source digest")
check(validate_result(typed_zero).ok, "typed zero validates")
assert_no_downstream(typed_zero, "typed zero")

# Deterministic repetition.
one_repeat = construct_candidate_meanings((one_input,))
check(one_repeat == one, "deterministic repeated construction")
check(one_repeat.result_id == one.result_id, "deterministic result identity")
check(one_repeat.constructed_records[0].candidate_meaning_state.state_id == record.candidate_meaning_state.state_id, "deterministic state identity")
check(one_repeat.construction_receipts[0].receipt_id == record.construction_receipt.receipt_id, "deterministic receipt identity")

# Multiple distinct candidates preserve independent states and alternatives.
report38 = exact_slice38(chain[-1], root="report", registry_key="fixture.slice39f.report")
report_input = constructor_input(chain, report38)
multi = construct_candidate_meanings((report_input, one_input))
multi_reversed = construct_candidate_meanings((one_input, report_input))
check(multi.status is CandidateMeaningConstructorStatus.CONSTRUCTED, "multi constructed")
check(multi.input_count == 2 and multi.unique_candidate_count == 2, "multi counts")
check(len(multi.constructed_records) == 2, "two states")
check(multi == multi_reversed, "input ordering cannot alter result")
check(multi.result_id == multi_reversed.result_id, "multi deterministic identity")
check(multi.candidate_set_result.multiple_candidates_preserved_independently is True, "multiple preserved")
for item in multi.constructed_records:
    check(bool(item.candidate_meaning_state.alternative_references), "alternative refs attached")
    check(item.candidate_meaning_state.ambiguous_gate_disposition is False, "no ambiguity outcome")
    check(validate_constructed_record(item).ok, "multi record validates")
check(validate_result(multi).ok, "multi result validates")
assert_no_downstream(multi, "multi")

# Exact duplicate occurrences remain in set custody without duplicate state identity.
duplicated = construct_candidate_meanings((one_input, one_input))
check(duplicated.status is CandidateMeaningConstructorStatus.CONSTRUCTED, "duplicate constructed")
check(duplicated.input_count == 2, "duplicate input count")
check(duplicated.unique_candidate_count == 1, "duplicate unique state count")
check(duplicated.exact_duplicate_occurrence_count == 1, "duplicate occurrence count")
check(len(duplicated.constructed_records) == 1, "duplicate does not fabricate second identity")
check(duplicated.constructed_records[0].duplicate_occurrence_count == 2, "duplicate custody count")
check(duplicated.candidate_set_result.exact_duplicate_detection_verified is True, "duplicate detection")
check(validate_result(duplicated).ok, "duplicate result validates")
assert_no_downstream(duplicated, "duplicate")

# Wrong top-level input and arbitrary raw text fail closed.
for bad in ("Inspect Concept Admission.", [one_input], {"input": one_input}, one_input, None, 7):
    malformed_cases += 1
    result = construct_candidate_meanings(bad)
    assert_rejected(result, f"bad top-level {type(bad).__name__}", CandidateMeaningConstructorValidationCode.TYPE_MISMATCH)

# Wrong tuple members fail closed.
for bad in ("raw text", object(), chain[6], inspect38, 1, None, (one_input,)):
    malformed_cases += 1
    result = construct_candidate_meanings((bad,))
    assert_rejected(result, f"bad member {type(bad).__name__}", CandidateMeaningConstructorValidationCode.TYPE_MISMATCH)

# Tampered exact typed predecessor fails closed rather than repairing.
tampered37 = replace(chain[6], source_sha256="0" * 64)
tampered_input = replace(one_input, slice37=tampered37)
malformed_cases += 1
assert_rejected(
    construct_candidate_meanings((tampered_input,)),
    "tampered predecessor",
    CandidateMeaningConstructorValidationCode.PREDECESSOR_REJECTED,
)


# Cross-source candidate inputs fail closed instead of silently merging lineages.
other_chain = pipeline("Inspect Concept Admission.", 2)
other38 = exact_slice38(other_chain[-1], root="inspect", registry_key="fixture.slice39f.other")
other_input = constructor_input(other_chain, other38)
malformed_cases += 1
assert_rejected(
    construct_candidate_meanings((one_input, other_input)),
    "cross source inputs",
    CandidateMeaningConstructorValidationCode.SOURCE_MISMATCH,
)

# Profile substitution is rejected.
malformed_profile = replace(DEFAULT_CONSTRUCTOR_PROFILE, hidden_repair_allowed=True)
malformed_cases += 1
assert_rejected(
    construct_candidate_meanings((one_input,), profile=malformed_profile),
    "profile substitution",
    CandidateMeaningConstructorValidationCode.PROFILE_MISMATCH,
)

# Frozen records.
try:
    one.constructed_records[0].deterministic_position = 99
except (FrozenInstanceError, AttributeError):
    check(True, "constructed record frozen")
else:
    check(False, "constructed record must be frozen")

print("AI.WEB SLICE 39F BEHAVIOR TEST: PASS")
print(f"check_count={checks}")
print(f"malformed_validation_cases={malformed_cases}")
print(f"explicit_rejection_cases={explicit_rejections}")
print("constructor_inputs=accepted_typed_slice37_slice38_records_only")
print("zero_candidate_states=0")
print("typed_zero_predecessor_inputs=1")
print("one_candidate_states=1")
print("multiple_candidate_states=2")
print("duplicate_occurrence_inputs=2")
print("duplicate_unique_candidate_states=1")
print("deterministic_construction_receipts=1")
print("exact_ancestry_verification=1")
print("exact_snapshot_verification=1")
print("source_preservation=1")
print("raw_text_inspection=0")
print("similarity_nearest_known_hidden_repair=0")
print("ranking_selection_ambiguity_resolution=0")
print("gate_outcome_selected_meaning=0")
print("truth_evidence_permission=0")
print("manifest_bootstrap_closeout=0")
print("route_action_memory_rendering_delivery=0")
print("filesystem_network_external_resource=0")
print("language_model_embedding_vector_rag_similarity=0")
