#!/usr/bin/env python3
"""Behavior and adversarial verification for AI.Web Slice 39G."""

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
from aiweb_language_core_bootstrap.resonant_operator_candidate_binding import (
    bind_resonant_operator_candidates,
)
from aiweb_language_core_bootstrap.candidate_resonant_phase_trail import (
    construct_candidate_resonant_phase_trails,
)
from aiweb_language_core_bootstrap.scope_attachment_reference_constraints import (
    apply_scope_attachment_reference_constraints,
)
from aiweb_language_core_bootstrap.deterministic_structural_derivation import (
    derive_deterministic_structural_analysis,
)
from aiweb_language_core_bootstrap.structural_concept_candidate_proposal import (
    propose_structural_concept_candidates,
)
from aiweb_language_core_bootstrap.predicate_role_frame_registry.predicate_role_frame_candidate_proposal import (
    build_compatibility_snapshot,
    build_exact_compatibility_rule,
    propose_predicate_role_frame_candidates,
)
from aiweb_language_core_bootstrap.meaning_structure_manifest import (
    CandidateMeaningRecord,
    MeaningStructureManifestV1,
)
from aiweb_language_core_bootstrap.meaning_structure_manifest.serialization import (
    deserialize_manifest,
    serialize_manifest,
)
from aiweb_language_core_bootstrap.meaning_structure_manifest.validation import (
    validate_manifest,
)
from aiweb_language_core_bootstrap.candidate_meaning_construction.deterministic_constructor import (
    CandidateMeaningConstructorInput,
    CandidateMeaningConstructorStatus,
    construct_candidate_meanings,
)
from aiweb_language_core_bootstrap.candidate_meaning_construction.manifest_candidate_integration import (
    DEFAULT_MANIFEST_INTEGRATION_PROFILE,
    SLICE39G_ADAPTER_DECISION,
    SLICE39G_ADAPTER_DECISION_REASONS,
    SLICE39G_PERMANENT_BOUNDARIES,
    SLICE39G_PROHIBITED_AUTHORITY,
    SLICE39G_REQUIRED_EMPTY_MANIFEST_SECTIONS,
    SLICE39G_REQUIRED_PATH,
    ManifestCandidateIntegrationStatus,
    ManifestCandidateIntegrationValidationCode,
    integrate_candidate_meanings_into_manifest,
    validate_integration_result,
    validate_profile,
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
    check(structural.structural_set is not None, f"structural {sequence}")
    slice37 = propose_structural_concept_candidates(
        custody,
        projection,
        structural,
    )
    check(bool(slice37.concept_candidates), f"concept candidates {sequence}")
    check(bool(slice37.sense_candidates), f"sense candidates {sequence}")
    return (
        custody,
        projection,
        binding,
        trails,
        constraints,
        structural,
        slice37,
    )


def exact_slice38(slice37, *, root: str, registry_key: str):
    concept = slice37.concept_candidates[0]
    sense = slice37.sense_candidates[0]
    frame_key = {
        "inspect": "inspect_read_only",
        "request": "request_non_authorizing",
        "report": "report_attributed_content",
    }[root]
    rule = build_exact_compatibility_rule(
        rule_key=f"fixture.slice39g.{root}",
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


def constructor_input(chain, slice38):
    return CandidateMeaningConstructorInput(
        custody=chain[0],
        projection=chain[1],
        binding=chain[2],
        trails=chain[3],
        constraints=chain[4],
        structural=chain[5],
        slice37=chain[6],
        slice38=slice38,
    )


def assert_empty_downstream(manifest: MeaningStructureManifestV1, label: str) -> None:
    for name in SLICE39G_REQUIRED_EMPTY_MANIFEST_SECTIONS:
        check(getattr(manifest, name) == (), f"{label}: {name} empty")


def assert_no_downstream(result, label: str) -> None:
    for name in (
        "existing_msm_schema_modified",
        "automatic_migration_performed",
        "non_selection_outcome_created",
        "selected_governed_meaning_created",
        "governed_result_reference_created",
        "governed_outward_meaning_created",
        "expression_link_created",
        "validation_link_created",
        "delivery_link_created",
        "gate_outcome_created",
        "selected_meaning_created",
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
        "vector_used",
        "rag_used",
        "semantic_similarity_used",
        "bootstrap_integrated",
        "slice39_closeout_created",
    ):
        check(getattr(result, name) is False, f"{label}: {name} false")
    if result.manifest is not None:
        assert_empty_downstream(result.manifest, label)


def assert_rejected(
    result,
    label: str,
    code: ManifestCandidateIntegrationValidationCode | None = None,
) -> None:
    global explicit_rejections
    explicit_rejections += 1
    check(
        result.status is ManifestCandidateIntegrationStatus.REJECTED,
        f"{label}: rejected",
    )
    check(result.manifest is None, f"{label}: no manifest")
    check(not result.companions, f"{label}: no companions")
    check(bool(result.issues), f"{label}: issues")
    check(validate_integration_result(result).ok, f"{label}: rejection validates")
    if code is not None:
        check(
            any(item.code is code for item in result.issues),
            f"{label}: expected code",
        )
    assert_no_downstream(result, label)


# Source-grounded decision: existing MSM-v1 candidate record is a projection,
# not a complete Slice 36-39F custody record.
candidate_fields = {item.name for item in fields(CandidateMeaningRecord)}
for missing_name in (
    "source_sha256",
    "source_span_ids",
    "operator_ancestry_ids",
    "phase_trail_ids",
    "registry_snapshot_ids",
    "construction_receipt_id",
    "limitation_reference_ids",
    "alternative_relationship_ids",
):
    check(missing_name not in candidate_fields, f"MSM-v1 lacks {missing_name}")
check(
    SLICE39G_ADAPTER_DECISION == "versioned_companion_required",
    "companion decision",
)
check(len(SLICE39G_ADAPTER_DECISION_REASONS) == 8, "decision reasons")
check(validate_profile(DEFAULT_MANIFEST_INTEGRATION_PROFILE).ok, "profile validates")
check(
    DEFAULT_MANIFEST_INTEGRATION_PROFILE.required_path
    == SLICE39G_REQUIRED_PATH,
    "required path sealed",
)
check(
    DEFAULT_MANIFEST_INTEGRATION_PROFILE.permanent_boundaries
    == SLICE39G_PERMANENT_BOUNDARIES,
    "boundaries sealed",
)
check(
    DEFAULT_MANIFEST_INTEGRATION_PROFILE.prohibited_authority
    == SLICE39G_PROHIBITED_AUTHORITY,
    "prohibited authority sealed",
)
check(
    DEFAULT_MANIFEST_INTEGRATION_PROFILE.versioned_companion_required is True,
    "companion required",
)
check(
    DEFAULT_MANIFEST_INTEGRATION_PROFILE.existing_msm_schema_modification_allowed
    is False,
    "no MSM schema modification",
)
check(
    DEFAULT_MANIFEST_INTEGRATION_PROFILE.automatic_migration_allowed is False,
    "no automatic migration",
)

# Zero candidate result without source lineage is preserved without inventing a
# manifest lineage.
zero_constructor = construct_candidate_meanings(())
zero = integrate_candidate_meanings_into_manifest(zero_constructor)
check(
    zero.status is ManifestCandidateIntegrationStatus.ZERO_CANDIDATES,
    "zero status",
)
check(zero.manifest is None, "zero without source has no invented manifest")
check(zero.reason_code == "zero_candidates_without_source_lineage_preserved", "zero reason")
check(validate_integration_result(zero).ok, "zero validates")
assert_no_downstream(zero, "zero")

# Construct accepted exact typed predecessor fixtures.
chain = pipeline("Inspect Concept Admission.", 1)
inspect38 = exact_slice38(
    chain[-1],
    root="inspect",
    registry_key="fixture.slice39g.inspect",
)
one_input = constructor_input(chain, inspect38)
one_constructor = construct_candidate_meanings((one_input,))
check(
    one_constructor.status is CandidateMeaningConstructorStatus.CONSTRUCTED,
    "one constructor result",
)

# Explicit side-effect containment.
with ExitStack() as stack:
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    one = integrate_candidate_meanings_into_manifest(one_constructor)

check(
    one.status is ManifestCandidateIntegrationStatus.INTEGRATED,
    "one integrated",
)
check(one.manifest is not None, "one manifest")
check(one.manifest_candidate_count == 1, "one candidate count")
check(len(one.companions) == 1, "one companion")
check(len(one.construction_trace_references) == 1, "one trace ref")
check(len(one.provenance_references) == 1, "one provenance ref")
check(len(one.limitation_references) == 1, "one limitation ref")
check(len(one.alternative_relationships) == 0, "one no alternatives")
check(len(one.manifest.external_authority_references) == 3, "one external refs")
check(len(one.manifest.semantic_transition_traces) == 1, "one transition trace")
check(validate_manifest(one.manifest).ok, "one MSM-v1 validates")
check(validate_integration_result(one).ok, "one integration validates")
check(one.versioned_companion_used is True, "one companion used")
check(one.lossless_companion_custody is True, "one lossless custody")
check(one.existing_msm_schema_modified is False, "one MSM unchanged")
check(one.automatic_migration_performed is False, "one no migration")
check(
    one.manifest.lineage_root.origin_ref
    == one_constructor.source_event_ids[0],
    "one source origin",
)
check(
    one.manifest.candidate_meanings[0].source_expression_ref
    == one.manifest.lineage_root.origin_ref,
    "one source expression custody",
)
check(
    one.companions[0].candidate_state_id
    == one_constructor.constructed_records[0].candidate_meaning_state.state_id,
    "one exact state custody",
)
check(
    one.provenance_references[0].source_sha256
    == one_constructor.source_sha256s[0],
    "one exact source checksum",
)
check(
    one.provenance_references[0].slice37_result_id
    == one_constructor.constructed_records[0].candidate_meaning_state.provenance.slice37_result_id,
    "one Slice 37 custody",
)
check(
    one.provenance_references[0].slice38_result_id
    == one_constructor.constructed_records[0].candidate_meaning_state.provenance.slice38_result_id,
    "one Slice 38 custody",
)
check(
    one.construction_trace_references[0].construction_receipt_id
    == one_constructor.construction_receipts[0].receipt_id,
    "one receipt custody",
)
check(
    one.limitation_references[0].clarification_required_created is False,
    "one no clarification outcome",
)
check(
    one.limitation_references[0].ambiguity_outcome_created is False,
    "one no ambiguity outcome",
)
assert_no_downstream(one, "one")

# Existing MSM-v1 canonical serialization remains valid and unchanged.
serialized = serialize_manifest(one.manifest)
restored = deserialize_manifest(serialized)
check(restored == one.manifest, "MSM-v1 canonical round trip")
check(serialize_manifest(restored) == serialized, "MSM-v1 canonical repeat")

# Deterministic repetition.
one_repeat = integrate_candidate_meanings_into_manifest(one_constructor)
check(one_repeat == one, "one deterministic repeat")
check(one_repeat.result_id == one.result_id, "one deterministic result id")
check(
    one_repeat.manifest.manifest_id == one.manifest.manifest_id,
    "one deterministic manifest id",
)

# Accepted typed predecessors may produce zero candidates while preserving
# source lineage in an empty candidate-side manifest.
zero_slice38 = propose_predicate_role_frame_candidates(chain[-1])
typed_zero_constructor = construct_candidate_meanings(
    (constructor_input(chain, zero_slice38),)
)
check(
    typed_zero_constructor.status
    is CandidateMeaningConstructorStatus.ZERO_CANDIDATES,
    "typed zero constructor",
)
typed_zero = integrate_candidate_meanings_into_manifest(typed_zero_constructor)
check(
    typed_zero.status is ManifestCandidateIntegrationStatus.ZERO_CANDIDATES,
    "typed zero integration",
)
check(typed_zero.manifest is not None, "typed zero manifest")
check(not typed_zero.manifest.candidate_meanings, "typed zero candidates empty")
check(validate_manifest(typed_zero.manifest).ok, "typed zero manifest validates")
check(validate_integration_result(typed_zero).ok, "typed zero validates")
assert_no_downstream(typed_zero, "typed zero")

# Multiple candidates preserve exact alternative relationships without an
# ambiguity disposition.
report38 = exact_slice38(
    chain[-1],
    root="report",
    registry_key="fixture.slice39g.report",
)
report_input = constructor_input(chain, report38)
multi_constructor = construct_candidate_meanings((report_input, one_input))
multi_constructor_reversed = construct_candidate_meanings((one_input, report_input))
check(multi_constructor == multi_constructor_reversed, "constructor order stable")
multi = integrate_candidate_meanings_into_manifest(multi_constructor)
multi_reversed = integrate_candidate_meanings_into_manifest(
    multi_constructor_reversed
)
check(
    multi.status is ManifestCandidateIntegrationStatus.INTEGRATED,
    "multi integrated",
)
check(multi == multi_reversed, "multi order stable")
check(multi.manifest_candidate_count == 2, "multi candidate count")
check(len(multi.companions) == 2, "multi companions")
check(len(multi.construction_trace_references) == 2, "multi traces")
check(len(multi.provenance_references) == 2, "multi provenance")
check(len(multi.limitation_references) == 2, "multi limitations")
check(len(multi.alternative_relationships) == 2, "multi directional alternatives")
check(
    len(multi.manifest.external_authority_references) == 8,
    "multi external refs",
)
check(len(multi.manifest.semantic_transition_traces) == 2, "multi MSM traces")
for relationship in multi.alternative_relationships:
    check(relationship.ranking_assigned is False, "multi no ranking")
    check(
        relationship.preferred_candidate_assigned is False,
        "multi no preference",
    )
    check(
        relationship.selected_alternative is False,
        "multi no selection",
    )
    check(
        relationship.ambiguous_gate_disposition_created is False,
        "multi no ambiguity outcome",
    )
check(validate_manifest(multi.manifest).ok, "multi manifest validates")
check(validate_integration_result(multi).ok, "multi validates")
assert_no_downstream(multi, "multi")

# Exact duplicate occurrences remain custody on one integrated candidate.
duplicate_constructor = construct_candidate_meanings((one_input, one_input))
duplicate = integrate_candidate_meanings_into_manifest(duplicate_constructor)
check(
    duplicate.status is ManifestCandidateIntegrationStatus.INTEGRATED,
    "duplicate integrated",
)
check(duplicate.manifest_candidate_count == 1, "duplicate one candidate")
check(
    duplicate.construction_trace_references[0].duplicate_occurrence_count == 2,
    "duplicate occurrence custody",
)
check(validate_integration_result(duplicate).ok, "duplicate validates")
assert_no_downstream(duplicate, "duplicate")

# Wrong top-level values fail closed.
for bad in (
    "raw text",
    [one_constructor],
    {"result": one_constructor},
    one_input,
    None,
    7,
):
    malformed_cases += 1
    result = integrate_candidate_meanings_into_manifest(bad)
    assert_rejected(
        result,
        f"bad top-level {type(bad).__name__}",
        ManifestCandidateIntegrationValidationCode.TYPE_MISMATCH,
    )

# A rejected Slice 39F result cannot enter MSM-v1 custody.
rejected_constructor = construct_candidate_meanings("raw text")
malformed_cases += 1
assert_rejected(
    integrate_candidate_meanings_into_manifest(rejected_constructor),
    "rejected constructor",
    ManifestCandidateIntegrationValidationCode.CONSTRUCTOR_RESULT_REJECTED,
)

# Tampered constructor result fails exact validation rather than being repaired.
tampered_constructor = replace(
    one_constructor,
    source_sha256s=("0" * 64,),
)
malformed_cases += 1
assert_rejected(
    integrate_candidate_meanings_into_manifest(tampered_constructor),
    "tampered constructor",
    ManifestCandidateIntegrationValidationCode.CONSTRUCTOR_RESULT_REJECTED,
)

# Profile substitution is rejected.
malformed_profile = replace(
    DEFAULT_MANIFEST_INTEGRATION_PROFILE,
    automatic_migration_allowed=True,
)
malformed_cases += 1
assert_rejected(
    integrate_candidate_meanings_into_manifest(
        one_constructor,
        profile=malformed_profile,
    ),
    "profile substitution",
    ManifestCandidateIntegrationValidationCode.PROFILE_MISMATCH,
)

# Result and companion identities detect post-construction tampering.
tampered_result = replace(one, selected_meaning_created=True)
check(
    not validate_integration_result(tampered_result).ok,
    "tampered result rejected",
)
tampered_companion = replace(one.companions[0], lossless_custody=False)
check(
    not validate_integration_result(
        replace(one, companions=(tampered_companion,))
    ).ok,
    "tampered companion rejected",
)

# Immutable records.
try:
    one.companions[0].candidate_state_id = "changed"
except (FrozenInstanceError, AttributeError):
    check(True, "companion frozen")
else:
    check(False, "companion must be frozen")

print("AI.WEB SLICE 39G BEHAVIOR TEST: PASS")
print(f"check_count={checks}")
print(f"malformed_validation_cases={malformed_cases}")
print(f"explicit_rejection_cases={explicit_rejections}")
print("adapter_decision=versioned_companion_required")
print("accepted_slice35_schema_modified=0")
print("automatic_migration=0")
print("zero_candidate_without_lineage_preserved=1")
print("typed_zero_candidate_manifest=1")
print("one_candidate_manifest_records=1")
print("multiple_candidate_manifest_records=2")
print("duplicate_occurrence_custody=2")
print("candidate_construction_traces=2")
print("candidate_provenance_references=2")
print("candidate_limitation_references=2")
print("candidate_alternative_relationships=2")
print("non_selection_gate_outcomes=0")
print("selected_governed_meanings=0")
print("governed_result_references=0")
print("governed_outward_meanings=0")
print("expression_validation_delivery_links=0")
print("gate_outcome_selected_meaning=0")
print("truth_evidence_permission=0")
print("bootstrap_closeout=0")
print("route_action_memory_rendering_delivery=0")
print("filesystem_network_external_resource=0")
print("language_model_embedding_vector_rag_similarity=0")
