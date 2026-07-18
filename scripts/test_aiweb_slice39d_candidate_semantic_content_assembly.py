#!/usr/bin/env python3
"""Behavior and adversarial verification for AI.Web Slice 39D."""

from __future__ import annotations

import builtins
from contextlib import ExitStack
from dataclasses import FrozenInstanceError, fields, replace
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
from aiweb_language_core_bootstrap.candidate_meaning_construction.predecessor_custody import (
    PredecessorCustodyStatus,
    bind_complete_predecessor_custody,
)
from aiweb_language_core_bootstrap.candidate_meaning_construction.candidate_semantic_content import (
    CANONICAL_FIELD_ORDERS,
    DEFAULT_CONTENT_PROFILE,
    SLICE39D_CONTENT_FAMILIES,
    SLICE39D_DEFERRED_SCOPE,
    SLICE39D_PERMANENT_BOUNDARIES,
    CandidateSemanticContentAssemblyResult,
    CandidateSemanticContentStatus,
    CandidateSemanticContentValidationCode,
    CommunicativeForceCandidate,
    SemanticDistinctionKind,
    assemble_candidate_semantic_content,
    canonical_record_mapping_39d,
    deterministic_digest,
    expected_assembly_digest,
    expected_assembly_id,
    expected_result_id,
    make_semantic_relation_candidate_reference,
    validate_assembly,
    validate_assembly_result,
    validate_profile,
    validate_semantic_relation_reference,
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
    custody = capture_input_event(
        text,
        source_id=source_id,
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
    constraints = apply_scope_attachment_reference_constraints(projection, binding, trails)
    check(constraints.constraint_set is not None, f"constraints {sequence}")
    structural = derive_deterministic_structural_analysis(
        custody, projection, binding, trails, constraints
    )
    check(structural.structural_set is not None, f"structural {sequence}")
    slice37 = propose_structural_concept_candidates(custody, projection, structural)
    return custody, projection, binding, trails, constraints, structural, slice37


def exact_slice38(slice37, *, root: str = "inspect", registry_key: str = "fixture.inspect"):
    concept = slice37.concept_candidates[0]
    sense = slice37.sense_candidates[0]
    frame_key = {
        "inspect": "inspect_read_only",
        "request": "request_non_authorizing",
        "report": "report_attributed_content",
    }[root]
    rule = build_exact_compatibility_rule(
        rule_key=f"fixture.content.{root}",
        action_root_key=root,
        concept_id=concept.concept_id,
        sense_id=sense.sense_id,
        allowed_frame_keys=(frame_key,),
    )
    snapshot = build_compatibility_snapshot(rules=(rule,), registry_key=registry_key)
    return propose_predicate_role_frame_candidates(
        slice37, compatibility_snapshot=snapshot
    )


def bind_chain(chain, slice38):
    return bind_complete_predecessor_custody(*chain, slice38)


def assemble_chain(chain, slice38, *, relations=()):
    bound = bind_chain(chain, slice38)
    return bound, assemble_candidate_semantic_content(
        bound, chain[4], chain[6], slice38,
        semantic_relation_references=relations,
    )


def assert_zero_downstream(result: CandidateSemanticContentAssemblyResult, label: str) -> None:
    for name in (
        "participant_assignments_created", "referents_resolved",
        "clarification_question_emitted", "candidate_ranked",
        "candidate_selected", "gate_progression_created", "truth_determined",
        "evidence_validated", "permission_granted", "route_created",
        "action_performed", "memory_accessed", "rendered", "delivered",
        "filesystem_read_performed", "filesystem_write_performed",
        "network_access_performed", "external_resource_loaded",
        "language_model_used", "embedding_used", "semantic_similarity_used",
    ):
        check(getattr(result, name) is False, f"{label}: result {name} false")
    if result.assembly is not None:
        for name in (
            "participant_assignments_created", "referents_resolved",
            "clarification_question_emitted", "candidate_ranked",
            "candidate_selected", "gate_progression_created", "truth_determined",
            "evidence_validated", "permission_granted", "route_created",
            "action_performed", "memory_accessed", "rendered", "delivered",
        ):
            check(getattr(result.assembly, name) is False, f"{label}: assembly {name} false")
        check(result.assembly.payload.participant_assignments_created is False, f"{label}: payload no assignment")
        check(result.assembly.payload.clarification_question_emitted is False, f"{label}: payload no clarification")
        check(result.assembly.candidate_meaning_content.selected_content is False, f"{label}: content not selected")
        check(result.assembly.candidate_meaning_content.truth_determined is False, f"{label}: content no truth")
        check(result.assembly.candidate_meaning_content.evidence_validity_determined is False, f"{label}: content no evidence")
        check(result.assembly.candidate_meaning_content.permission_inferred is False, f"{label}: content no permission")


def assert_rejected(result, label: str, expected: CandidateSemanticContentValidationCode | None = None) -> None:
    global explicit_rejections
    explicit_rejections += 1
    check(type(result) is CandidateSemanticContentAssemblyResult, f"{label}: typed result")
    check(result.status is CandidateSemanticContentStatus.CONTENT_REJECTED, f"{label}: rejected")
    check(result.assembly is None, f"{label}: no assembly")
    check(bool(result.issues), f"{label}: issue retained")
    check(validate_assembly_result(result).ok, f"{label}: rejection record validates")
    if expected is not None:
        check(any(item.code is expected for item in result.issues), f"{label}: expected code")
    assert_zero_downstream(result, label)


# Profile, immutable shape, content inventory and permanent boundaries.
check(validate_profile(DEFAULT_CONTENT_PROFILE).ok, "canonical profile validates")
check(DEFAULT_CONTENT_PROFILE.role_assignment_allowed is False, "role assignment prohibited")
check(DEFAULT_CONTENT_PROFILE.referent_resolution_allowed is False, "referent resolution prohibited")
check(DEFAULT_CONTENT_PROFILE.clarification_question_emission_allowed is False, "clarification emission prohibited")
check(DEFAULT_CONTENT_PROFILE.candidate_ranking_allowed is False, "ranking prohibited")
check(DEFAULT_CONTENT_PROFILE.candidate_selection_allowed is False, "selection prohibited")
check(DEFAULT_CONTENT_PROFILE.gate_progression_allowed is False, "gate progression prohibited")
check(DEFAULT_CONTENT_PROFILE.truth_evidence_permission_allowed is False, "truth evidence permission prohibited")
check(DEFAULT_CONTENT_PROFILE.route_action_memory_rendering_delivery_allowed is False, "downstream prohibited")
check(len(SLICE39D_CONTENT_FAMILIES) >= 24, "content family inventory")
check(len(SLICE39D_PERMANENT_BOUNDARIES) >= 20, "permanent boundaries")
check(len(SLICE39D_DEFERRED_SCOPE) >= 15, "deferred scope")
check(len(CANONICAL_FIELD_ORDERS) == 10, "ten canonical record types")
for record_type, order in CANONICAL_FIELD_ORDERS.items():
    check(order == tuple(item.name for item in fields(record_type)), f"canonical order {record_type.__name__}")

# Real non-empty candidate content over exact Slice 36 -> 37 -> 38 -> 39C custody.
chain = pipeline("Inspect Concept Admission.", 1)
slice38 = exact_slice38(chain[-1])
with ExitStack() as stack:
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    bound, result = assemble_chain(chain, slice38)
check(bound.status is PredecessorCustodyStatus.BOUND, "positive custody bound")
check(result.status is CandidateSemanticContentStatus.ASSEMBLED, "positive assembled")
check(result.reason_code == "candidate_semantic_content_assembled", "positive reason")
check(result.issues == (), "positive no issues")
check(result.assembly is not None, "positive assembly")
check(validate_assembly_result(result).ok, "positive result validates")
assert_zero_downstream(result, "positive")
assembly = result.assembly
assert assembly is not None
check(validate_assembly(assembly).ok, "assembly validates")
check(assembly.predecessor_custody == bound.custody, "exact custody retained")
check(assembly.lineage_id == bound.custody.lineage_id, "exact lineage retained")
check(assembly.assembly_id == expected_assembly_id(assembly), "assembly identity")
check(assembly.canonical_digest == expected_assembly_digest(assembly), "assembly digest")
check(result.result_id == expected_result_id(result), "result identity")
check(len(deterministic_digest(canonical_record_mapping_39d(assembly))) == 64, "canonical digest shape")
check(assembly.candidate_meaning_content.content_id.startswith("candidate_content:sha256:"), "39A content identity")
check(assembly.payload.candidate_only is True, "payload candidate only")
check(assembly.payload.role_layout_candidate_refs == bound.custody.provenance.role_layout_candidate_ids, "role layouts are references")
check(assembly.payload.action_root_candidate_refs == bound.custody.provenance.action_predicate_candidate_ids, "action candidates exact")
check(assembly.payload.predicate_candidate_refs == bound.custody.provenance.action_predicate_candidate_ids, "predicate candidates exact")
check(assembly.payload.capability_family_reference_refs == bound.custody.provenance.capability_reference_candidate_ids, "capability candidates exact")
check(bool(assembly.payload.effect_boundary_refs), "effect boundary carried")
check(bool(assembly.payload.missing_information_refs), "missing information recorded")
check(assembly.payload.clarification_question_emitted is False, "missing information does not emit clarification")
check(len(assembly.requested_act_descriptions) == 1, "requested act description")
check(assembly.requested_act_descriptions[0].permission_granted is False, "requested act no permission")
check(assembly.requested_act_descriptions[0].route_created is False, "requested act no route")
check(assembly.requested_act_descriptions[0].execution_performed is False, "requested act no execution")
check(CommunicativeForceCandidate.REQUEST in assembly.communicative_purpose.force_candidates, "request force candidate")

# Determinism and immutability.
repeat = assemble_candidate_semantic_content(bound, chain[4], chain[6], slice38)
check(repeat == result, "deterministic full equality")
check(repeat.result_id == result.result_id, "deterministic result id")
try:
    assembly.lineage_id = "mutated"  # type: ignore[misc]
    raise AssertionError("assembly mutation unexpectedly succeeded")
except (FrozenInstanceError, AttributeError):
    check(True, "assembly immutable")

# Closed force candidates: question, report, request and assertion remain possible, never selected.
fixtures = (
    ("Is Concept Admission accepted?", "inspect", CommunicativeForceCandidate.QUESTION),
    ("Report Concept Admission.", "report", CommunicativeForceCandidate.REPORT),
    ("Request Concept Admission.", "request", CommunicativeForceCandidate.REQUEST),
)
for index, (text, root, expected_force) in enumerate(fixtures, start=10):
    fixture_chain = pipeline(text, index)
    fixture_slice38 = exact_slice38(fixture_chain[-1], root=root, registry_key=f"fixture.{root}.{index}")
    fixture_bound, fixture_result = assemble_chain(fixture_chain, fixture_slice38)
    check(fixture_bound.status is PredecessorCustodyStatus.BOUND, f"{root} bound")
    check(fixture_result.status is CandidateSemanticContentStatus.ASSEMBLED, f"{root} assembled")
    check(expected_force in fixture_result.assembly.communicative_purpose.force_candidates, f"{root} force")
    check(fixture_result.assembly.communicative_purpose.force_selected is False, f"{root} not selected")
    check(fixture_result.assembly.communicative_purpose.gate_disposition_created is False, f"{root} no gate")
    assert_zero_downstream(fixture_result, root)

# Negation is preserved as candidate content, not converted into a decision.
neg_chain = pipeline("Do not inspect Concept Admission.", 20)
neg_slice38 = exact_slice38(neg_chain[-1], registry_key="fixture.negation")
neg_bound, neg_result = assemble_chain(neg_chain, neg_slice38)
check(neg_bound.status is PredecessorCustodyStatus.BOUND, "negation bound")
check(neg_result.status is CandidateSemanticContentStatus.ASSEMBLED, "negation assembled")
check(bool(neg_result.assembly.payload.negation_refs), "negation retained")
check(any(item.kind is SemanticDistinctionKind.NEGATION for item in neg_result.assembly.distinctions), "negation distinction")
assert_zero_downstream(neg_result, "negation")

# A semantic relation is a candidate relation-type reference only, never a graph fact.
concept_candidate_id = bound.custody.provenance.concept_candidate_proposal_ids[0]
relation = make_semantic_relation_candidate_reference(
    relation_type_key="representation_relevant_to",
    source_concept_candidate_ids=(concept_candidate_id,),
    target_concept_candidate_ids=(concept_candidate_id,),
    source_record_ids=(bound.custody.provenance.structural_result_id,),
    source_span_ids=(bound.custody.provenance.root_source_span_id,),
)
check(validate_semantic_relation_reference(relation).ok, "relation reference validates")
check(relation.candidate_only is True, "relation candidate only")
check(relation.relation_instance_asserted is False, "no relation fact")
check(relation.truth_determined is False, "relation no truth")
check(relation.evidence_validated is False, "relation no evidence")
relation_result = assemble_candidate_semantic_content(
    bound, chain[4], chain[6], slice38,
    semantic_relation_references=(relation,),
)
check(relation_result.status is CandidateSemanticContentStatus.ASSEMBLED, "relation assembly")
check(relation_result.assembly.semantic_relation_references == (relation,), "relation exact")
check(relation_result.assembly.payload.semantic_relation_candidate_refs == (relation.reference_id,), "relation payload mapping")
assert_zero_downstream(relation_result, "relation")

# Zero candidate remains explicit; no content or substitute ancestry is generated.
zero_slice38 = propose_predicate_role_frame_candidates(chain[-1])
zero_bound, zero_result = assemble_chain(chain, zero_slice38)
check(zero_bound.status is PredecessorCustodyStatus.NO_CANDIDATE_PREDECESSOR, "zero predecessor explicit")
check(zero_result.status is CandidateSemanticContentStatus.NO_CANDIDATE_CONTENT, "zero content explicit")
check(zero_result.assembly is None, "zero no assembly")
check(zero_result.issues == (), "zero no issues")
check(validate_assembly_result(zero_result).ok, "zero result validates")
assert_zero_downstream(zero_result, "zero")

# Lawful alternatives remain independent; none is ranked or selected.
concept = chain[-1].concept_candidates[0]
sense = chain[-1].sense_candidates[0]
rules = (
    build_exact_compatibility_rule(
        rule_key="fixture.multiple.inspect", action_root_key="inspect",
        concept_id=concept.concept_id, sense_id=sense.sense_id,
        allowed_frame_keys=("inspect_read_only",),
    ),
    build_exact_compatibility_rule(
        rule_key="fixture.multiple.report", action_root_key="report",
        concept_id=concept.concept_id, sense_id=sense.sense_id,
        allowed_frame_keys=("report_attributed_content",),
    ),
)
multi_slice38 = propose_predicate_role_frame_candidates(
    chain[-1], compatibility_snapshot=build_compatibility_snapshot(
        rules=rules, registry_key="fixture.multiple"
    )
)
multi_bound, multi_result = assemble_chain(chain, multi_slice38)
check(multi_bound.status is PredecessorCustodyStatus.BOUND, "alternatives bound")
check(multi_result.status is CandidateSemanticContentStatus.ASSEMBLED, "alternatives assembled")
check(len(multi_result.assembly.requested_act_descriptions) == 2, "two acts preserved")
check(len(multi_result.assembly.payload.action_root_candidate_refs) == 2, "two action candidates preserved")
check(len(multi_result.assembly.payload.role_layout_candidate_refs) == 2, "two role layouts preserved")
check(multi_result.assembly.candidate_ranked is False, "alternatives unranked")
check(multi_result.assembly.candidate_selected is False, "alternatives unselected")
assert_zero_downstream(multi_result, "alternatives")

# Public constructor rejects wrong exact types without throwing or creating authority.
invalid_values = (None, 0, 1.0, True, "bad", (), [], {}, object())
valid_args = [bound, chain[4], chain[6], slice38]
for argument_index in range(4):
    for invalid in invalid_values:
        args = list(valid_args)
        args[argument_index] = invalid
        rejected = assemble_candidate_semantic_content(*args)
        malformed_cases += 1
        assert_rejected(rejected, f"invalid argument {argument_index} {type(invalid).__name__}", CandidateSemanticContentValidationCode.TYPE_MISMATCH)
for invalid in invalid_values:
    rejected = assemble_candidate_semantic_content(bound, chain[4], chain[6], slice38, profile=invalid)
    malformed_cases += 1
    assert_rejected(rejected, f"invalid profile {type(invalid).__name__}", CandidateSemanticContentValidationCode.TYPE_MISMATCH)
for invalid in (None, 0, True, "bad", [], {}, object()):
    rejected = assemble_candidate_semantic_content(bound, chain[4], chain[6], slice38, semantic_relation_references=invalid)
    malformed_cases += 1
    assert_rejected(rejected, f"invalid relation tuple {type(invalid).__name__}", CandidateSemanticContentValidationCode.INVALID_TUPLE)

# Cross-lineage inputs are rejected rather than merged.
other_chain = pipeline("Inspect Concept Admission.", 30, source_id="fixture.other")
other_slice38 = exact_slice38(other_chain[-1], registry_key="fixture.other")
other_bound = bind_chain(other_chain, other_slice38)
assert_rejected(
    assemble_candidate_semantic_content(other_bound, chain[4], chain[6], slice38),
    "cross-lineage custody",
)
assert_rejected(
    assemble_candidate_semantic_content(bound, other_chain[4], chain[6], slice38),
    "cross-lineage constraints",
)
assert_rejected(
    assemble_candidate_semantic_content(bound, chain[4], other_chain[6], slice38),
    "cross-lineage concepts",
)
assert_rejected(
    assemble_candidate_semantic_content(bound, chain[4], chain[6], other_slice38),
    "cross-lineage predicate candidates",
)

# Fabricated relation references are rejected at assembly boundary.
fabricated_relations = (
    replace(relation, source_concept_candidate_ids=("slice37f_concept_candidate:fabricated",)),
    replace(relation, target_concept_candidate_ids=("slice37f_concept_candidate:fabricated",)),
    replace(relation, source_span_ids=("source_span:fabricated",)),
    replace(relation, relation_type_id="semantic_relation_type:fabricated"),
    replace(relation, relation_instance_asserted=True),
    replace(relation, truth_determined=True),
    replace(relation, evidence_validated=True),
)
for index, bad_relation in enumerate(fabricated_relations):
    rejected = assemble_candidate_semantic_content(
        bound, chain[4], chain[6], slice38,
        semantic_relation_references=(bad_relation,),
    )
    assert_rejected(rejected, f"fabricated relation {index}")

# A valid assembly cannot be laundered after creation: identity, mapping and
# downstream-authority mutations are caught by the independent validator.
assembly_mutations = (
    replace(assembly, assembly_id="candidate_semantic_content_assembly:sha256:" + "0" * 64),
    replace(assembly, canonical_digest="0" * 64),
    replace(assembly, lineage_id="candidate_predecessor_lineage:sha256:" + "0" * 64),
    replace(assembly, participant_assignments_created=True),
    replace(assembly, referents_resolved=True),
    replace(assembly, clarification_question_emitted=True),
    replace(assembly, candidate_ranked=True),
    replace(assembly, candidate_selected=True),
    replace(assembly, gate_progression_created=True),
    replace(assembly, truth_determined=True),
    replace(assembly, evidence_validated=True),
    replace(assembly, permission_granted=True),
    replace(assembly, route_created=True),
    replace(assembly, action_performed=True),
    replace(assembly, memory_accessed=True),
    replace(assembly, rendered=True),
    replace(assembly, delivered=True),
    replace(assembly, payload=replace(assembly.payload, participant_assignments_created=True)),
    replace(assembly, payload=replace(assembly.payload, clarification_question_emitted=True)),
    replace(assembly, payload=replace(assembly.payload, concept_candidate_refs=("slice37f_concept_candidate:fabricated",))),
    replace(assembly, payload=replace(assembly.payload, role_layout_candidate_refs=("slice38g_role_layout_candidate:fabricated",))),
    replace(assembly, payload=replace(assembly.payload, frame_candidate_refs=("slice38g_role_layout_candidate:fabricated",))),
    replace(assembly, payload=replace(assembly.payload, effect_boundary_refs=("slice38f_effect_boundary:fabricated",))),
    replace(assembly, payload=replace(assembly.payload, capability_family_reference_refs=("slice38g_capability_reference_candidate:fabricated",))),
)
for index, mutated in enumerate(assembly_mutations):
    malformed_cases += 1
    check(not validate_assembly(mutated).ok, f"assembly mutation {index} rejected")

# Result count, lineage, status and authority mutations are rejected.
result_mutations = (
    replace(result, result_id="candidate_semantic_content_result:sha256:" + "0" * 64),
    replace(result, source_event_id="input_event:foreign"),
    replace(result, source_sha256="0" * 64),
    replace(result, lineage_id="candidate_predecessor_lineage:sha256:" + "0" * 64),
    replace(result, communicative_force_candidate_count=999),
    replace(result, requested_act_description_count=999),
    replace(result, semantic_relation_reference_count=999),
    replace(result, distinction_count=999),
    replace(result, participant_assignments_created=True),
    replace(result, clarification_question_emitted=True),
    replace(result, candidate_selected=True),
    replace(result, gate_progression_created=True),
    replace(result, truth_determined=True),
    replace(result, permission_granted=True),
    replace(result, action_performed=True),
    replace(result, filesystem_read_performed=True),
    replace(result, filesystem_write_performed=True),
    replace(result, network_access_performed=True),
    replace(result, external_resource_loaded=True),
    replace(result, language_model_used=True),
    replace(result, embedding_used=True),
    replace(result, semantic_similarity_used=True),
)
for index, mutated in enumerate(result_mutations):
    malformed_cases += 1
    check(not validate_assembly_result(mutated).ok, f"result mutation {index} rejected")

# Canonical mappings are stable and closed over all public records.
records = (
    DEFAULT_CONTENT_PROFILE,
    assembly.communicative_purpose,
    *assembly.requested_act_descriptions,
    *assembly.semantic_relation_references,
    *assembly.referent_references,
    *assembly.distinctions,
    assembly.payload,
    assembly,
    result,
)
for item in records:
    first = canonical_record_mapping_39d(item)
    second = canonical_record_mapping_39d(item)
    check(first == second, f"canonical mapping stable {type(item).__name__}")
    check(deterministic_digest(first) == deterministic_digest(second), f"canonical digest stable {type(item).__name__}")

print("AI.WEB SLICE 39D BEHAVIOR TEST: PASS")
print(f"check_count={checks}")
print(f"malformed_validation_cases={malformed_cases}")
print(f"explicit_rejection_cases={explicit_rejections}")
print(f"content_families={len(SLICE39D_CONTENT_FAMILIES)}")
print(f"canonical_record_types={len(CANONICAL_FIELD_ORDERS)}")
print(f"communicative_force_candidates={len(assembly.communicative_purpose.force_candidates)}")
print(f"requested_act_descriptions={len(assembly.requested_act_descriptions)}")
print(f"semantic_relation_candidate_references={relation_result.semantic_relation_reference_count}")
print(f"referent_candidates={len(assembly.referent_references)}")
print(f"semantic_distinctions={len(assembly.distinctions)}")
print(f"role_layout_candidate_references={len(assembly.payload.role_layout_candidate_refs)}")
print(f"effect_boundary_references={len(assembly.payload.effect_boundary_refs)}")
print(f"capability_family_references={len(assembly.payload.capability_family_reference_refs)}")
print("participant_assignments_created=0")
print("clarification_question_emitted=0")
print("candidate_ranking_selection=0")
print("gate_progression=0")
print("truth_evidence_permission=0")
print("route_action_memory_rendering_delivery=0")
print("filesystem_network_external_resource=0")
print("language_model_embedding_similarity=0")
