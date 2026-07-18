#!/usr/bin/env python3
"""Behavior and adversarial verification for AI.Web Slice 39C."""

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
    CANONICAL_FIELD_ORDERS,
    DEFAULT_CONSTRUCTION_PROFILE,
    SLICE39C_DEFERRED_SCOPE,
    SLICE39C_PERMANENT_BOUNDARIES,
    SLICE39C_REQUIRED_STAGES,
    CandidateMeaningConstructionProfileIdentity,
    CandidateMeaningPredecessorBindingResult,
    CandidateMeaningPredecessorCustody,
    OperatorCustodyReference,
    PredecessorCustodyReceipt,
    PredecessorCustodyStage,
    PredecessorCustodyStatus,
    PredecessorCustodyValidationCode,
    RegistryResourceCustodyReference,
    RegistryResourceKind,
    SourceSpanCustodyReference,
    StructuralRuleCustodyReference,
    bind_complete_predecessor_custody,
    canonical_record_mapping_39c,
    deterministic_digest,
    expected_binding_result_id,
    expected_custody_digest,
    expected_custody_id,
    expected_lineage_id,
    expected_operator_reference_id,
    expected_profile_id,
    expected_receipt_id,
    expected_registry_resource_reference_id,
    expected_source_span_reference_id,
    expected_structural_rule_reference_id,
    validate_binding_result,
    validate_construction_profile,
    validate_custody,
    validate_operator_reference,
    validate_receipt,
    validate_registry_resource_reference,
    validate_source_span_reference,
    validate_structural_rule_reference,
)

checks = 0
malformed_cases = 0
rejection_cases = 0


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
    constraints = apply_scope_attachment_reference_constraints(
        projection, binding, trails
    )
    check(constraints.constraint_set is not None, f"constraints {sequence}")
    structural = derive_deterministic_structural_analysis(
        custody, projection, binding, trails, constraints
    )
    check(structural.structural_set is not None, f"structural {sequence}")
    slice37 = propose_structural_concept_candidates(
        custody, projection, structural
    )
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
        rule_key=f"fixture.concept-admission.{root}",
        action_root_key=root,
        concept_id=concept.concept_id,
        sense_id=sense.sense_id,
        allowed_frame_keys=(frame_key,),
    )
    snapshot = build_compatibility_snapshot(
        rules=(rule,),
        registry_key=registry_key,
    )
    return propose_predicate_role_frame_candidates(
        slice37,
        compatibility_snapshot=snapshot,
    )


def assert_zero_authority(result: CandidateMeaningPredecessorBindingResult, label: str) -> None:
    for name in (
        "semantic_payload_constructed",
        "candidate_ranked",
        "candidate_selected",
        "gate_progression_created",
        "truth_determined",
        "evidence_validated",
        "permission_granted",
        "route_created",
        "action_performed",
        "memory_accessed",
        "rendered",
        "delivered",
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "external_resource_loaded",
        "language_model_used",
        "embedding_used",
        "semantic_similarity_used",
    ):
        check(getattr(result, name) is False, f"{label}: {name} false")
    if result.custody is not None:
        for name in (
            "cross_lineage_candidate_merge_performed",
            "generated_substitute_ancestry_used",
            "semantic_payload_constructed",
            "candidate_ranked",
            "candidate_selected",
            "gate_progression_created",
            "truth_determined",
            "evidence_validated",
            "permission_granted",
            "route_created",
            "action_performed",
            "memory_accessed",
            "rendered",
            "delivered",
        ):
            check(getattr(result.custody, name) is False, f"{label}: custody {name} false")


def assert_rejected(result, label: str, expected_code: PredecessorCustodyValidationCode | None = None) -> None:
    global rejection_cases
    rejection_cases += 1
    check(type(result) is CandidateMeaningPredecessorBindingResult, f"{label}: typed result")
    check(result.status is PredecessorCustodyStatus.PREDECESSOR_REJECTED, f"{label}: rejected")
    check(result.custody is None, f"{label}: no custody")
    check(bool(result.issues), f"{label}: issue preserved")
    check(validate_binding_result(result).ok, f"{label}: rejected result validates")
    if expected_code is not None:
        check(any(item.code is expected_code for item in result.issues), f"{label}: expected issue code")
    assert_zero_authority(result, label)


# Canonical profile, shape and permanent boundary inventory.
check(validate_construction_profile(DEFAULT_CONSTRUCTION_PROFILE).ok, "profile validates")
check(DEFAULT_CONSTRUCTION_PROFILE.profile_id == expected_profile_id(DEFAULT_CONSTRUCTION_PROFILE), "profile exact identity")
check(DEFAULT_CONSTRUCTION_PROFILE.required_stages == SLICE39C_REQUIRED_STAGES, "all eight stages")
check(len(DEFAULT_CONSTRUCTION_PROFILE.required_stages) == 8, "eight required stages")
check(DEFAULT_CONSTRUCTION_PROFILE.cross_lineage_merge_allowed is False, "cross lineage closed")
check(DEFAULT_CONSTRUCTION_PROFILE.generated_substitute_ancestry_allowed is False, "substitute ancestry closed")
check(DEFAULT_CONSTRUCTION_PROFILE.semantic_payload_construction_allowed is False, "semantic construction closed")
check(DEFAULT_CONSTRUCTION_PROFILE.candidate_ranking_allowed is False, "ranking closed")
check(DEFAULT_CONSTRUCTION_PROFILE.candidate_selection_allowed is False, "selection closed")
check(DEFAULT_CONSTRUCTION_PROFILE.gate_progression_allowed is False, "gate progression closed")
check(DEFAULT_CONSTRUCTION_PROFILE.truth_evidence_permission_allowed is False, "truth evidence permission closed")
check(DEFAULT_CONSTRUCTION_PROFILE.route_action_memory_rendering_delivery_allowed is False, "downstream authority closed")
check(len(SLICE39C_PERMANENT_BOUNDARIES) >= 17, "permanent boundaries recorded")
check(len(SLICE39C_DEFERRED_SCOPE) >= 17, "deferred scope recorded")
check(len(CANONICAL_FIELD_ORDERS) == 9, "nine canonical record types")
for record_type, order in CANONICAL_FIELD_ORDERS.items():
    check(order == tuple(item.name for item in fields(record_type)), f"canonical order {record_type.__name__}")

# Real non-empty Slice 36 -> 37 -> 38 ancestry fixture.
chain = pipeline("Inspect Concept Admission.", 1)
slice38 = exact_slice38(chain[-1])
with ExitStack() as stack:
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    bound = bind_complete_predecessor_custody(*chain, slice38)
check(bound.status is PredecessorCustodyStatus.BOUND, "positive bound")
check(bound.reason_code == "complete_predecessor_custody_bound", "positive reason")
check(bound.issues == (), "positive no issues")
check(bound.custody is not None, "positive custody")
check(validate_binding_result(bound).ok, "positive result validates")
assert_zero_authority(bound, "positive")

custody = bound.custody
assert custody is not None
check(validate_custody(custody).ok, "custody validates")
check(bound.result_id == expected_binding_result_id(bound), "result identity")
check(custody.custody_id == expected_custody_id(custody), "custody identity")
check(custody.canonical_digest == expected_custody_digest(custody), "custody digest")
check(custody.custody_id.endswith(custody.canonical_digest), "custody ID/digest relation")
check(custody.lineage_id == expected_lineage_id(
    source_event_id=custody.provenance.source_event_id,
    source_sha256=custody.provenance.source_sha256,
    slice37_registry_snapshot_id=custody.provenance.slice37_registry_snapshot_id,
    slice38_registry_snapshot_id=custody.provenance.slice38_registry_snapshot_id,
    compatibility_registry_snapshot_id=custody.provenance.compatibility_registry_snapshot_id,
    construction_profile_id=custody.construction_profile.profile_id,
    construction_profile_version=custody.construction_profile.profile_version,
), "lineage identity")
check(bound.source_span_reference_count == 27, "27 exact source spans")
check(bound.structural_rule_reference_count == 17, "17 exact structural rules")
check(bound.operator_reference_count == 2, "2 exact operator candidates")
check(bound.registry_resource_reference_count == 22, "22 exact registry resources")
check(bound.stage_receipt_count == 8, "8 exact receipts")
check(tuple(item.stage for item in custody.stage_receipts) == tuple(PredecessorCustodyStage), "receipt stage chain")
check(tuple(item.stage_ordinal for item in custody.stage_receipts) == tuple(range(1, 9)), "receipt ordinals")
for index, receipt in enumerate(custody.stage_receipts):
    check(validate_receipt(receipt).ok, f"receipt {index} validates")
    check(receipt.receipt_id == expected_receipt_id(receipt), f"receipt {index} identity")
    expected_predecessors = () if index == 0 else (
        custody.stage_receipts[index - 1].output_record_id,
        custody.stage_receipts[index - 1].receipt_id,
    )
    check(receipt.predecessor_record_ids == expected_predecessors, f"receipt {index} exact predecessor chain")
check(custody.predecessor_result_ids == tuple(item.output_record_id for item in custody.stage_receipts), "result inventory equals receipts")
check(custody.provenance.predecessor_receipt_ids == tuple(item.receipt_id for item in custody.stage_receipts), "provenance receipt inventory")
check(custody.provenance.source_event_id == chain[0].event.input_event_id, "source event exact")
check(custody.provenance.source_sha256 == chain[0].event.source_sha256, "source checksum exact")
check(custody.provenance.root_source_span_id == chain[0].root_span.span_id, "root span exact")
check(sum(item.is_root_span for item in custody.source_span_references) == 1, "one root span")
check(tuple(item.span_id for item in custody.source_span_references) == custody.provenance.source_span_ids, "span inventory exact")
for item in custody.source_span_references:
    check(validate_source_span_reference(item).ok, f"span {item.span_id} validates")
    check(item.reference_id == expected_source_span_reference_id(item), f"span {item.span_id} identity")
for item in custody.structural_rule_references:
    check(validate_structural_rule_reference(item).ok, f"rule {item.trace_id} validates")
    check(item.reference_id == expected_structural_rule_reference_id(item), f"rule {item.trace_id} identity")
for item in custody.operator_references:
    check(validate_operator_reference(item).ok, f"operator {item.candidate_binding_id} validates")
    check(item.reference_id == expected_operator_reference_id(item), f"operator {item.candidate_binding_id} identity")
for item in custody.registry_resource_references:
    check(validate_registry_resource_reference(item).ok, f"resource {item.resource_id} validates")
    check(item.reference_id == expected_registry_resource_reference_id(item), f"resource {item.resource_id} identity")
check(frozenset(item.resource_kind for item in custody.registry_resource_references) == frozenset(RegistryResourceKind), "all registry resource kinds")
check(len([item for item in custody.registry_resource_references if item.resource_kind is RegistryResourceKind.PARTICIPANT_ROLE]) == 11, "all 11 role identities")
check(len([item for item in custody.registry_resource_references if item.resource_kind is RegistryResourceKind.CAPABILITY_FAMILY]) == 2, "two capability family identities")
check(canonical_record_mapping_39c(custody)["semantic_payload_constructed"] is False, "canonical no semantic payload")
check(len(deterministic_digest(canonical_record_mapping_39c(custody))) == 64, "canonical digest shape")

# Determinism: identical accepted records produce byte-identical custody.
repeat = bind_complete_predecessor_custody(*chain, slice38)
check(repeat == bound, "deterministic full equality")
check(repeat.result_id == bound.result_id, "deterministic result identity")
check(repeat.custody.custody_id == custody.custody_id, "deterministic custody identity")

# Exact zero-candidate predecessor stays explicit without fabricated ancestry.
canonical_slice38 = propose_predicate_role_frame_candidates(chain[-1])
empty = bind_complete_predecessor_custody(*chain, canonical_slice38)
check(empty.status is PredecessorCustodyStatus.NO_CANDIDATE_PREDECESSOR, "zero candidate explicit")
check(empty.reason_code == "no_slice38_candidate_predecessor", "zero candidate reason")
check(empty.custody is None, "zero candidate no custody")
check(empty.issues == (), "zero candidate no failure issue")
check(validate_binding_result(empty).ok, "zero candidate result validates")
assert_zero_authority(empty, "zero candidate")

# A lawful zero-capability candidate preserves exact empty capability ancestry.
request_slice38 = exact_slice38(chain[-1], root="request", registry_key="fixture.request")
request_bound = bind_complete_predecessor_custody(*chain, request_slice38)
check(request_bound.status is PredecessorCustodyStatus.BOUND, "request candidate bound")
check(request_bound.custody is not None, "request custody")
check(request_bound.custody.provenance.capability_reference_candidate_ids == (), "zero capability candidate preserved")
check(not any(item.resource_kind is RegistryResourceKind.CAPABILITY_FAMILY for item in request_bound.custody.registry_resource_references), "no substitute capability ancestry")
check(validate_binding_result(request_bound).ok, "request result validates")
assert_zero_authority(request_bound, "request")

# Lawful alternatives may share admitted registry resources without being
# collapsed, ranked, selected, or falsely classified as cross-lineage merging.
concept = chain[-1].concept_candidates[0]
sense = chain[-1].sense_candidates[0]
multiple_rules = (
    build_exact_compatibility_rule(
        rule_key="fixture.multiple.inspect",
        action_root_key="inspect",
        concept_id=concept.concept_id,
        sense_id=sense.sense_id,
        allowed_frame_keys=("inspect_read_only",),
    ),
    build_exact_compatibility_rule(
        rule_key="fixture.multiple.report",
        action_root_key="report",
        concept_id=concept.concept_id,
        sense_id=sense.sense_id,
        allowed_frame_keys=("report_attributed_content",),
    ),
)
multiple_snapshot = build_compatibility_snapshot(
    rules=multiple_rules,
    registry_key="fixture.multiple",
)
multiple_slice38 = propose_predicate_role_frame_candidates(
    chain[-1],
    compatibility_snapshot=multiple_snapshot,
)
multiple_bound = bind_complete_predecessor_custody(*chain, multiple_slice38)
check(multiple_bound.status is PredecessorCustodyStatus.BOUND, "multiple alternatives bound")
check(multiple_bound.issues == (), "multiple alternatives no issues")
check(multiple_bound.custody is not None, "multiple alternatives custody")
check(len(multiple_slice38.action_predicate_candidates) == 2, "two action alternatives preserved")
check(len(multiple_slice38.role_layout_candidates) == 2, "two role layouts preserved")
check(multiple_bound.custody.provenance.action_predicate_candidate_ids == tuple(
    item.candidate_id for item in multiple_slice38.action_predicate_candidates
), "all action alternatives retained")
check(multiple_bound.custody.provenance.role_layout_candidate_ids == tuple(
    item.candidate_id for item in multiple_slice38.role_layout_candidates
), "all role-layout alternatives retained")
shared_roles = tuple(
    item for item in multiple_bound.custody.registry_resource_references
    if item.resource_kind is RegistryResourceKind.PARTICIPANT_ROLE
    and len(item.source_candidate_ids) == 2
)
check(len(shared_roles) == 11, "shared admitted roles merge custody references only")
check(validate_binding_result(multiple_bound).ok, "multiple alternatives result validates")
assert_zero_authority(multiple_bound, "multiple alternatives")

# Exact public type failures are typed, exception-free and closed.
invalid_values = (None, 0, 1.0, True, "bad", (), [], {}, object())
for argument_index in range(9):
    for invalid in invalid_values:
        global_args = list(chain) + [slice38, DEFAULT_CONSTRUCTION_PROFILE]
        global_args[argument_index] = invalid
        result = bind_complete_predecessor_custody(*global_args[:8], construction_profile=global_args[8])
        malformed_cases += 1
        assert_rejected(result, f"invalid argument {argument_index} {type(invalid).__name__}", PredecessorCustodyValidationCode.TYPE_MISMATCH)

# Individually valid records from another lineage cannot be merged.
other_chain = pipeline("Inspect Concept Admission.", 2, source_id="fixture.other")
other_slice38 = exact_slice38(other_chain[-1], registry_key="fixture.other.inspect")
for position, foreign in enumerate(other_chain + (other_slice38,)):
    mixed = list(chain) + [slice38]
    mixed[position] = foreign
    result = bind_complete_predecessor_custody(*mixed)
    assert_rejected(result, f"cross-lineage stage {position}")

# Explicit required rejection classes from the roadmap.
assert_rejected(
    bind_complete_predecessor_custody(None, *chain[1:], slice38),
    "missing predecessor",
    PredecessorCustodyValidationCode.TYPE_MISMATCH,
)
assert_rejected(
    bind_complete_predecessor_custody(*chain[:-1], other_chain[-1], slice38),
    "mismatched source event",
)

# Tampered predecessor records are rejected before custody can launder them.
tampered_binding_set = replace(
    chain[2].binding_set,
    candidates=(
        replace(chain[2].binding_set.candidates[0], source_span_ids=("source_span:fabricated",)),
    ) + chain[2].binding_set.candidates[1:],
)
tampered_binding = replace(chain[2], binding_set=tampered_binding_set)
assert_rejected(bind_complete_predecessor_custody(chain[0], chain[1], tampered_binding, *chain[3:], slice38), "fabricated source span")

tampered_ancestry = replace(chain[-1].structural_ancestries[0], source_event_id="input_event:foreign")
tampered_slice37 = replace(chain[-1], structural_ancestries=(tampered_ancestry,) + chain[-1].structural_ancestries[1:])
assert_rejected(bind_complete_predecessor_custody(*chain[:-1], tampered_slice37, slice38), "generated substitute ancestry")

layout = slice38.role_layout_candidates[0]
tampered_layout = replace(layout, required_roles=(("participant_role_identity:fabricated", "action_subject", "v1.1.0"),))
tampered_slice38 = replace(slice38, role_layout_candidates=(tampered_layout,))
assert_rejected(bind_complete_predecessor_custody(*chain, tampered_slice38), "fabricated role identity")

tampered_layout = replace(layout, frame_id="slice38e_predicate_frame:fabricated")
tampered_slice38 = replace(slice38, role_layout_candidates=(tampered_layout,))
assert_rejected(bind_complete_predecessor_custody(*chain, tampered_slice38), "fabricated frame identity")

report_slice38 = exact_slice38(chain[-1], root="report", registry_key="fixture.report")
mixed_snapshot_slice38 = replace(
    slice38,
    compatibility_registry_snapshot=report_slice38.compatibility_registry_snapshot,
)
assert_rejected(bind_complete_predecessor_custody(*chain, mixed_snapshot_slice38), "mixed registry snapshots")

# Frozen records cannot be mutated in place.
for record, field_name in (
    (DEFAULT_CONSTRUCTION_PROFILE, "profile_key"),
    (custody.source_span_references[0], "span_id"),
    (custody.structural_rule_references[0], "trace_id"),
    (custody.operator_references[0], "operator_key"),
    (custody.registry_resource_references[0], "resource_id"),
    (custody.stage_receipts[0], "output_record_id"),
    (custody, "lineage_id"),
    (bound, "reason_code"),
):
    try:
        setattr(record, field_name, "mutated")
    except (FrozenInstanceError, AttributeError, TypeError):
        check(True, f"frozen {type(record).__name__}")
    else:
        raise AssertionError(f"record unexpectedly mutable: {type(record).__name__}")

# Public validators reject malformed record kinds without exceptions.
validators = (
    validate_construction_profile,
    validate_source_span_reference,
    validate_structural_rule_reference,
    validate_operator_reference,
    validate_registry_resource_reference,
    validate_receipt,
    validate_custody,
    validate_binding_result,
)
for validator in validators:
    for invalid in invalid_values:
        malformed_cases += 1
        report = validator(invalid)
        check(report.ok is False, f"{validator.__name__} rejects {type(invalid).__name__}")
        check(bool(report.issues), f"{validator.__name__} preserves issue")

# Record-level adversarial mutations exercise identities, versions, ordering,
# duplicates, missing ancestry and authority-zero boundaries.
mutation_cases = []
span = custody.source_span_references[0]
mutation_cases.extend((
    (validate_source_span_reference, replace(span, reference_id="bad id")),
    (validate_source_span_reference, replace(span, span_id="bad id")),
    (validate_source_span_reference, replace(span, source_sha256="0")),
    (validate_source_span_reference, replace(span, code_point_end=span.code_point_start)),
    (validate_source_span_reference, replace(span, utf8_byte_end=span.utf8_byte_start)),
    (validate_source_span_reference, replace(span, observed_in_record_ids=())),
    (validate_source_span_reference, replace(span, observed_in_record_ids=(span.observed_in_record_ids[0],) * 2)),
))
rule = custody.structural_rule_references[0]
mutation_cases.extend((
    (validate_structural_rule_reference, replace(rule, reference_id="bad id")),
    (validate_structural_rule_reference, replace(rule, trace_id="bad id")),
    (validate_structural_rule_reference, replace(rule, derivation_rule_version="bad version")),
    (validate_structural_rule_reference, replace(rule, source_rule_ids_and_versions=(("bad id", "bad version"),))),
    (validate_structural_rule_reference, replace(rule, input_record_ids=("bad id",))),
    (validate_structural_rule_reference, replace(rule, source_span_ids=("bad id",))),
))
operator = custody.operator_references[0]
mutation_cases.extend((
    (validate_operator_reference, replace(operator, reference_id="bad id")),
    (validate_operator_reference, replace(operator, candidate_binding_id="bad id")),
    (validate_operator_reference, replace(operator, operator_version="bad version")),
    (validate_operator_reference, replace(operator, grammar_registry_version="bad version")),
    (validate_operator_reference, replace(operator, source_span_ids=())),
    (validate_operator_reference, replace(operator, phase_trail_ids=())),
    (validate_operator_reference, replace(operator, application_ids=())),
))
resource = custody.registry_resource_references[0]
mutation_cases.extend((
    (validate_registry_resource_reference, replace(resource, reference_id="bad id")),
    (validate_registry_resource_reference, replace(resource, resource_id="bad id")),
    (validate_registry_resource_reference, replace(resource, resource_version="bad version")),
    (validate_registry_resource_reference, replace(resource, registry_snapshot_id="bad id")),
    (validate_registry_resource_reference, replace(resource, source_candidate_ids=())),
    (validate_registry_resource_reference, replace(resource, source_candidate_ids=(resource.source_candidate_ids[0],) * 2)),
))
receipt = custody.stage_receipts[1]
mutation_cases.extend((
    (validate_receipt, replace(receipt, receipt_id="bad id")),
    (validate_receipt, replace(receipt, stage_ordinal=0)),
    (validate_receipt, replace(receipt, predecessor_record_ids=())),
    (validate_receipt, replace(receipt, output_record_id="bad id")),
    (validate_receipt, replace(receipt, source_sha256="0")),
    (validate_receipt, replace(receipt, exact_validation_passed=False)),
    (validate_receipt, replace(receipt, generated_substitute_ancestry_used=True)),
    (validate_receipt, replace(receipt, semantic_payload_constructed=True)),
    (validate_receipt, replace(receipt, gate_progression_created=True)),
    (validate_receipt, replace(receipt, delivered=True)),
))
for validator, malformed in mutation_cases:
    malformed_cases += 1
    report = validator(malformed)
    check(report.ok is False, f"mutation rejected {validator.__name__}")
    check(bool(report.issues), f"mutation issue {validator.__name__}")

custody_mutations = (
    replace(custody, custody_id="bad id"),
    replace(custody, lineage_id="bad id"),
    replace(custody, source_span_references=()),
    replace(custody, source_span_references=tuple(reversed(custody.source_span_references))),
    replace(custody, structural_rule_references=()),
    replace(custody, operator_references=()),
    replace(custody, registry_resource_references=()),
    replace(custody, stage_receipts=()),
    replace(custody, predecessor_result_ids=()),
    replace(custody, exact_source_event_match=False),
    replace(custody, exact_source_checksum_match=False),
    replace(custody, exact_source_spans_verified=False),
    replace(custody, exact_structural_ancestry_verified=False),
    replace(custody, exact_operator_ancestry_verified=False),
    replace(custody, exact_phase_trail_ancestry_verified=False),
    replace(custody, exact_scope_attachment_reference_ancestry_verified=False),
    replace(custody, exact_registry_snapshots_verified=False),
    replace(custody, exact_resource_versions_verified=False),
    replace(custody, zero_one_many_preserved=False),
    replace(custody, cross_lineage_candidate_merge_performed=True),
    replace(custody, generated_substitute_ancestry_used=True),
    replace(custody, semantic_payload_constructed=True),
    replace(custody, candidate_ranked=True),
    replace(custody, candidate_selected=True),
    replace(custody, gate_progression_created=True),
    replace(custody, truth_determined=True),
    replace(custody, evidence_validated=True),
    replace(custody, permission_granted=True),
    replace(custody, route_created=True),
    replace(custody, action_performed=True),
    replace(custody, memory_accessed=True),
    replace(custody, rendered=True),
    replace(custody, delivered=True),
    replace(custody, canonical_digest="0" * 64),
)
for malformed in custody_mutations:
    malformed_cases += 1
    report = validate_custody(malformed)
    check(report.ok is False, "custody mutation rejected")
    check(bool(report.issues), "custody mutation issue")

result_mutations = (
    replace(bound, result_id="bad id"),
    replace(bound, source_event_id="input_event:foreign"),
    replace(bound, source_sha256="0" * 64),
    replace(bound, source_span_reference_count=0),
    replace(bound, structural_rule_reference_count=0),
    replace(bound, operator_reference_count=0),
    replace(bound, registry_resource_reference_count=0),
    replace(bound, stage_receipt_count=0),
    replace(bound, semantic_payload_constructed=True),
    replace(bound, candidate_ranked=True),
    replace(bound, candidate_selected=True),
    replace(bound, gate_progression_created=True),
    replace(bound, truth_determined=True),
    replace(bound, evidence_validated=True),
    replace(bound, permission_granted=True),
    replace(bound, route_created=True),
    replace(bound, action_performed=True),
    replace(bound, memory_accessed=True),
    replace(bound, rendered=True),
    replace(bound, delivered=True),
    replace(bound, filesystem_read_performed=True),
    replace(bound, filesystem_write_performed=True),
    replace(bound, network_access_performed=True),
    replace(bound, external_resource_loaded=True),
    replace(bound, language_model_used=True),
    replace(bound, embedding_used=True),
    replace(bound, semantic_similarity_used=True),
)
for malformed in result_mutations:
    malformed_cases += 1
    report = validate_binding_result(malformed)
    check(report.ok is False, "result mutation rejected")
    check(bool(report.issues), "result mutation issue")

print("AI.WEB SLICE 39C BEHAVIOR TEST: PASS")
print(f"check_count={checks}")
print(f"malformed_validation_cases={malformed_cases}")
print(f"explicit_rejection_cases={rejection_cases}")
print(f"source_span_references={bound.source_span_reference_count}")
print(f"structural_rule_references={bound.structural_rule_reference_count}")
print(f"operator_references={bound.operator_reference_count}")
print(f"registry_resource_references={bound.registry_resource_reference_count}")
print(f"stage_receipts={bound.stage_receipt_count}")
print(f"registry_resource_kinds={len(RegistryResourceKind)}")
print(f"construction_profile_version={DEFAULT_CONSTRUCTION_PROFILE.profile_version}")
print("semantic_payload_constructed=0")
print("candidate_ranking_selection=0")
print("gate_progression=0")
print("truth_evidence_permission=0")
print("route_action_memory_rendering_delivery=0")
print("filesystem_network_external_resource=0")
print("language_model_embedding_similarity=0")
