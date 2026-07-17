#!/usr/bin/env python3
"""Behavior and adversarial validation test for Slice 38F."""

from __future__ import annotations

import argparse
from dataclasses import fields, replace
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default="/home/nic/forge")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    sys.path.insert(0, str(repository))

    from aiweb_language_core_bootstrap.predicate_role_frame_registry.capability_family_reference_registry import (
        ADMITTED_CAPABILITY_FAMILY_KEYS,
        ADMITTED_EFFECT_BOUNDARY_KEYS,
        CAPABILITY_FAMILY_REFERENCE_REGISTRY,
        CAPABILITY_REFERENCE_LIFECYCLE_RULES,
        DEFERRED_CAPABILITY_FAMILY_KEYS,
        FRAMES_WITHOUT_CAPABILITY_REFERENCE,
        PUBLIC_VALIDATORS,
        UNBOUND_CAPABILITY_FAMILY_KEYS,
        CapabilityAvailabilityStatus,
        CapabilityReferenceLifecycleState,
        CapabilityReferenceMode,
        CapabilityReferenceValidationError,
        EffectBoundaryClass,
        all_capability_families,
        all_compatibility_records,
        all_effect_boundaries,
        all_frame_capability_references,
        all_frame_effect_references,
        assert_valid,
        capability_family_by_id,
        capability_family_by_key,
        capability_family_reference_registry,
        compatibility_by_id,
        contains_capability_family_id,
        contains_effect_boundary_id,
        effect_boundary_by_id,
        effect_boundary_by_key,
        expected_lineage_id,
        frame_capability_reference_by_id,
        frame_capability_references_for_frame,
        frame_effect_reference_by_id,
        frame_effect_reference_for_frame,
        registry_manifest,
        transition_allowed,
        validate_registry,
        version_advances,
    )
    from aiweb_language_core_bootstrap.predicate_role_frame_registry.capability_family_reference_registry import records as rec
    from aiweb_language_core_bootstrap.predicate_role_frame_registry.predicate_frame_registry import (
        PREDICATE_FRAME_REGISTRY,
    )

    checks = 0
    failures: list[str] = []
    malformed_cases = 0

    def check(condition: object, label: str) -> None:
        nonlocal checks
        checks += 1
        if condition is not True:
            failures.append(label)

    registry = capability_family_reference_registry()
    check(registry is CAPABILITY_FAMILY_REFERENCE_REGISTRY, "registry singleton")
    report = validate_registry(registry)
    check(report.ok, "canonical registry validates")
    check(report.issues == (), "canonical registry has no issues")
    assert_valid(report)
    assert_valid(registry)

    check(registry_manifest() == registry.manifest, "manifest accessor")
    check(all_effect_boundaries() == registry.effect_boundaries, "effect accessor")
    check(all_capability_families() == registry.capability_families, "family accessor")
    check(all_frame_effect_references() == registry.frame_effect_references, "frame effect accessor")
    check(all_frame_capability_references() == registry.frame_capability_references, "frame capability accessor")
    check(all_compatibility_records() == registry.compatibility_records, "compatibility accessor")

    expected_effects = (
        "no_action",
        "read_only",
        "communicative_only",
        "verification_review_only",
        "simulation_only",
        "protected_mathematical_output_only",
    )
    expected_families = (
        "read_only_inspection",
        "source_comparison",
        "draft_preparation",
        "verification_review",
        "non_live_simulation",
        "protected_mathematical_operation",
    )
    expected_deferred = (
        "memory_request",
        "software_change_proposal",
        "delivery_request",
    )
    expected_effect_by_frame = {
        "inspect_read_only": "read_only",
        "report_attributed_content": "communicative_only",
        "request_non_authorizing": "no_action",
        "verify_bounded_review": "verification_review_only",
        "simulate_non_live": "simulation_only",
    }
    expected_capability_by_frame = {
        "inspect_read_only": ("read_only_inspection", "source_comparison"),
        "report_attributed_content": ("draft_preparation",),
        "request_non_authorizing": (),
        "verify_bounded_review": ("verification_review",),
        "simulate_non_live": ("non_live_simulation",),
    }
    expected_family_effect = {
        "read_only_inspection": "read_only",
        "source_comparison": "read_only",
        "draft_preparation": "communicative_only",
        "verification_review": "verification_review_only",
        "non_live_simulation": "simulation_only",
        "protected_mathematical_operation": "protected_mathematical_output_only",
    }

    check(ADMITTED_EFFECT_BOUNDARY_KEYS == expected_effects, "exact effect keys")
    check(ADMITTED_CAPABILITY_FAMILY_KEYS == expected_families, "exact family keys")
    check(DEFERRED_CAPABILITY_FAMILY_KEYS == expected_deferred, "exact deferred keys")
    check(FRAMES_WITHOUT_CAPABILITY_REFERENCE == ("request_non_authorizing",), "exact frame with no capability reference")
    check(UNBOUND_CAPABILITY_FAMILY_KEYS == ("protected_mathematical_operation",), "exact unbound family")
    check(tuple(item.effect_boundary_key for item in registry.effect_boundaries) == expected_effects, "effect order")
    check(tuple(item.capability_family_key for item in registry.capability_families) == expected_families, "family order")
    check(len(registry.effect_boundaries) == 6, "effect count")
    check(len(registry.capability_families) == 6, "family count")
    check(len(registry.frame_effect_references) == 5, "frame effect count")
    check(len(registry.frame_capability_references) == 5, "frame capability count")
    check(len(registry.compatibility_records) == 6, "compatibility count")
    check(len(registry.transitions) == 28, "transition count")
    check(len(registry.provenance_records) == 4, "provenance count")
    check(len(registry.authority_records) == 1, "authority count")
    check(len(CAPABILITY_REFERENCE_LIFECYCLE_RULES) == 19, "lifecycle rule count")

    frame_by_id = {item.frame_id: item for item in PREDICATE_FRAME_REGISTRY.admitted_frames}
    frame_by_key = {item.frame_key: item for item in PREDICATE_FRAME_REGISTRY.admitted_frames}
    effect_by_id = {item.effect_boundary_id: item for item in registry.effect_boundaries}
    family_by_id = {item.capability_family_id: item for item in registry.capability_families}
    frame_effect_by_key = {item.frame_key: item for item in registry.frame_effect_references}

    for effect, history in zip(registry.effect_boundaries, registry.effect_boundary_histories, strict=True):
        check(effect.lifecycle_state is CapabilityReferenceLifecycleState.ARCHITECTURE_ADMITTED, f"effect admitted {effect.effect_boundary_key}")
        check(effect.effect_class.value == effect.effect_boundary_key, f"effect class exact {effect.effect_boundary_key}")
        check(effect_boundary_by_id(effect.effect_boundary_id) == effect, f"effect id lookup {effect.effect_boundary_key}")
        check(effect_boundary_by_key(effect.namespace_id, effect.effect_boundary_key) == effect, f"effect key lookup {effect.effect_boundary_key}")
        check(contains_effect_boundary_id(effect.effect_boundary_id), f"effect contains {effect.effect_boundary_key}")
        check(len(history) == 2, f"effect history length {effect.effect_boundary_key}")
        check(history[0].lifecycle_state is CapabilityReferenceLifecycleState.CANDIDATE, f"effect candidate ancestry {effect.effect_boundary_key}")
        check(history[1] == effect, f"effect current ancestry {effect.effect_boundary_key}")
        check(version_advances(history[0].version, history[1].version), f"effect version advances {effect.effect_boundary_key}")
        check(expected_lineage_id(history[0]) == expected_lineage_id(history[1]), f"effect lineage stable {effect.effect_boundary_key}")
        for name in (
            "permission_satisfied", "capability_available", "route_resolved",
            "capability_invoked", "execution_performed", "evidence_validated",
            "memory_authority_supplied", "delivery_authorized",
            "external_resource_admitted", "implementation_performed",
        ):
            check(getattr(effect, name) is False, f"effect authority zero {effect.effect_boundary_key}.{name}")

    for family, history in zip(registry.capability_families, registry.capability_family_histories, strict=True):
        check(family.lifecycle_state is CapabilityReferenceLifecycleState.ARCHITECTURE_ADMITTED, f"family admitted {family.capability_family_key}")
        check(capability_family_by_id(family.capability_family_id) == family, f"family id lookup {family.capability_family_key}")
        check(capability_family_by_key(family.namespace_id, family.capability_family_key) == family, f"family key lookup {family.capability_family_key}")
        check(contains_capability_family_id(family.capability_family_id), f"family contains {family.capability_family_key}")
        check(len(history) == 2, f"family history length {family.capability_family_key}")
        check(history[0].lifecycle_state is CapabilityReferenceLifecycleState.CANDIDATE, f"family candidate ancestry {family.capability_family_key}")
        check(history[1] == family, f"family current ancestry {family.capability_family_key}")
        check(version_advances(history[0].version, history[1].version), f"family version advances {family.capability_family_key}")
        check(expected_lineage_id(history[0]) == expected_lineage_id(history[1]), f"family lineage stable {family.capability_family_key}")
        check(len(family.supported_effect_boundary_refs) == 1, f"family one effect boundary {family.capability_family_key}")
        check(effect_by_id[family.supported_effect_boundary_refs[0]].effect_boundary_key == expected_family_effect[family.capability_family_key], f"family effect exact {family.capability_family_key}")
        for name in (
            "installed", "available", "route_registered", "invocation_contract_installed",
            "runtime_loaded", "tool_bound", "external_resource_loaded",
            "implementation_authorized",
        ):
            check(getattr(family, name) is False, f"family authority zero {family.capability_family_key}.{name}")

    for reference, history in zip(registry.frame_effect_references, registry.frame_effect_reference_histories, strict=True):
        check(reference.frame_id in frame_by_id, f"frame effect frame exists {reference.frame_key}")
        check(frame_by_id[reference.frame_id].frame_key == reference.frame_key, f"frame effect frame key exact {reference.frame_key}")
        check(reference.effect_boundary_id in effect_by_id, f"frame effect boundary exists {reference.frame_key}")
        check(effect_by_id[reference.effect_boundary_id].effect_boundary_key == expected_effect_by_frame[reference.frame_key], f"frame effect exact {reference.frame_key}")
        check(frame_effect_reference_by_id(reference.frame_effect_reference_id) == reference, f"frame effect id lookup {reference.frame_key}")
        check(frame_effect_reference_for_frame(reference.frame_id) == reference, f"frame effect frame lookup {reference.frame_key}")
        check(len(history) == 2, f"frame effect history length {reference.frame_key}")
        check(history[0].lifecycle_state is CapabilityReferenceLifecycleState.CANDIDATE, f"frame effect candidate ancestry {reference.frame_key}")
        check(history[1] == reference, f"frame effect current ancestry {reference.frame_key}")
        check(version_advances(history[0].version, history[1].version), f"frame effect version advances {reference.frame_key}")
        check(expected_lineage_id(history[0]) == expected_lineage_id(history[1]), f"frame effect lineage stable {reference.frame_key}")
        for name in (
            "frame_selected", "effect_permission_satisfied", "capability_available",
            "route_resolved", "invocation_proposed", "invocation_authorized",
            "execution_performed", "result_verified",
        ):
            check(getattr(reference, name) is False, f"frame effect authority zero {reference.frame_key}.{name}")

    for reference, history in zip(registry.frame_capability_references, registry.frame_capability_reference_histories, strict=True):
        check(reference.frame_id in frame_by_id, f"frame capability frame exists {reference.frame_key}")
        check(reference.capability_family_id in family_by_id, f"frame capability family exists {reference.capability_family_key}")
        check(reference.frame_effect_reference_id == frame_effect_by_key[reference.frame_key].frame_effect_reference_id, f"frame capability effect ref exact {reference.frame_key}:{reference.capability_family_key}")
        check(reference.effect_boundary_id == frame_effect_by_key[reference.frame_key].effect_boundary_id, f"frame capability effect boundary exact {reference.frame_key}:{reference.capability_family_key}")
        check(frame_capability_reference_by_id(reference.frame_capability_reference_id) == reference, f"frame capability id lookup {reference.frame_key}:{reference.capability_family_key}")
        check(reference.availability_status is CapabilityAvailabilityStatus.NOT_PROVEN, f"availability not proven {reference.frame_key}:{reference.capability_family_key}")
        check(len(history) == 2, f"frame capability history length {reference.frame_key}:{reference.capability_family_key}")
        check(history[0].lifecycle_state is CapabilityReferenceLifecycleState.CANDIDATE, f"frame capability candidate ancestry {reference.frame_key}:{reference.capability_family_key}")
        check(history[1] == reference, f"frame capability current ancestry {reference.frame_key}:{reference.capability_family_key}")
        check(version_advances(history[0].version, history[1].version), f"frame capability version advances {reference.frame_key}:{reference.capability_family_key}")
        check(expected_lineage_id(history[0]) == expected_lineage_id(history[1]), f"frame capability lineage stable {reference.frame_key}:{reference.capability_family_key}")
        for name in (
            "capability_available", "route_available", "invocation_proposed",
            "invocation_authorized", "arguments_constructed", "permission_granted",
            "execution_performed", "result_verified", "tool_bound",
            "memory_operation_performed", "delivery_performed",
            "external_resource_admitted", "implementation_performed",
        ):
            check(getattr(reference, name) is False, f"frame capability authority zero {reference.frame_key}:{reference.capability_family_key}.{name}")
        for name in (
            "route_identity", "invocation_identity", "argument_bundle_id",
            "permission_id", "execution_receipt_id",
        ):
            check(getattr(reference, name) is None, f"frame capability identifier absent {reference.frame_key}:{reference.capability_family_key}.{name}")

    for frame_key, expected_keys in expected_capability_by_frame.items():
        frame = frame_by_key[frame_key]
        actual = frame_capability_references_for_frame(frame.frame_id)
        check(tuple(item.capability_family_key for item in actual) == expected_keys, f"exact frame capability set {frame_key}")

    for compatibility, history in zip(registry.compatibility_records, registry.compatibility_histories, strict=True):
        check(compatibility.capability_family_id in family_by_id, f"compatibility family exists {compatibility.capability_family_key}")
        check(compatibility.effect_boundary_id in effect_by_id, f"compatibility effect exists {compatibility.capability_family_key}")
        check(compatibility.effect_boundary_key == expected_family_effect[compatibility.capability_family_key], f"compatibility exact effect {compatibility.capability_family_key}")
        check(compatibility_by_id(compatibility.compatibility_id) == compatibility, f"compatibility lookup {compatibility.capability_family_key}")
        check(len(history) == 2, f"compatibility history length {compatibility.capability_family_key}")
        check(history[0].lifecycle_state is CapabilityReferenceLifecycleState.CANDIDATE, f"compatibility candidate ancestry {compatibility.capability_family_key}")
        check(history[1] == compatibility, f"compatibility current ancestry {compatibility.capability_family_key}")
        check(version_advances(history[0].version, history[1].version), f"compatibility version advances {compatibility.capability_family_key}")
        check(expected_lineage_id(history[0]) == expected_lineage_id(history[1]), f"compatibility lineage stable {compatibility.capability_family_key}")
        check(compatibility.proves_capability_availability is False, f"compatibility no availability {compatibility.capability_family_key}")
        check(compatibility.creates_route is False, f"compatibility no route {compatibility.capability_family_key}")
        check(compatibility.authorizes_invocation is False, f"compatibility no invocation {compatibility.capability_family_key}")
        check(compatibility.authorizes_execution is False, f"compatibility no execution {compatibility.capability_family_key}")
        check(compatibility.satisfies_permission is False, f"compatibility no permission {compatibility.capability_family_key}")

    for transition in registry.transitions:
        check(transition_allowed(transition.from_state, transition.to_state, transition.transition_kind), f"transition allowed {transition.transition_id}")
        check(transition.human_approval is True, f"transition human approved {transition.transition_id}")
        check(transition.automatic_transition is False, f"transition not automatic {transition.transition_id}")
        check(transition.prior_record_preserved is True, f"transition preserves prior {transition.transition_id}")
        check(transition.in_place_mutation_performed is False, f"transition no mutation {transition.transition_id}")
        check(transition.capability_availability_created is False, f"transition no availability {transition.transition_id}")
        check(transition.route_created is False, f"transition no route {transition.transition_id}")
        check(transition.invocation_created is False, f"transition no invocation {transition.transition_id}")
        check(transition.execution_created is False, f"transition no execution {transition.transition_id}")

    manifest = registry.manifest
    check(manifest.effect_boundary_count == 6, "manifest effect count")
    check(manifest.capability_family_count == 6, "manifest family count")
    check(manifest.frame_effect_reference_count == 5, "manifest frame effect count")
    check(manifest.frame_capability_reference_count == 5, "manifest frame capability count")
    check(manifest.compatibility_count == 6, "manifest compatibility count")
    check(manifest.transition_count == 28, "manifest transition count")
    check(manifest.active_correction_count == 0, "manifest corrections zero")
    check(manifest.active_conflict_count == 0, "manifest conflicts zero")
    check(manifest.registry_read_only is True, "manifest read only")
    check(manifest.registry_closed is True, "manifest closed")
    check(manifest.exact_identity_lookup_only is True, "manifest exact identity lookup")
    for name in (
        "source_term_lookup_installed", "occurrence_frame_selection_installed",
        "occurrence_role_assignment_installed", "candidate_meaning_creation_installed",
        "selected_meaning_installed", "gate_outcome_installed",
        "capability_availability_registry_installed", "route_registry_installed",
        "invocation_registry_installed", "argument_builder_installed",
        "tool_activation_installed", "action_execution_installed",
        "evidence_validation_installed", "memory_access_installed",
        "rendering_installed", "delivery_installed",
        "external_resource_loading_installed", "implementation_installed",
        "default_capability_reference_installed", "nearest_known_substitution_installed",
        "semantic_similarity_installed", "llm_authority_installed",
    ):
        check(getattr(manifest, name) is False, f"manifest authority zero {name}")

    # Exact lookup surfaces must refuse normalization, approximation and malformed inputs.
    lookup_bad_values = (None, True, False, 0, 1, (), [], {}, object(), "", " ", "unknown", "READ_ONLY", "read-only", "read_only ")
    for value in lookup_bad_values:
        check(effect_boundary_by_id(value) is None, f"effect id lookup rejects {type(value).__name__}:{value!r}")
        check(capability_family_by_id(value) is None, f"family id lookup rejects {type(value).__name__}:{value!r}")
        check(frame_effect_reference_by_id(value) is None, f"frame effect id lookup rejects {type(value).__name__}:{value!r}")
        check(frame_capability_reference_by_id(value) is None, f"frame capability id lookup rejects {type(value).__name__}:{value!r}")
        check(compatibility_by_id(value) is None, f"compatibility id lookup rejects {type(value).__name__}:{value!r}")
        check(frame_effect_reference_for_frame(value) is None, f"frame effect frame lookup rejects {type(value).__name__}:{value!r}")
        check(frame_capability_references_for_frame(value) == (), f"frame capability frame lookup rejects {type(value).__name__}:{value!r}")
        check(not contains_effect_boundary_id(value), f"effect contains rejects {type(value).__name__}:{value!r}")
        check(not contains_capability_family_id(value), f"family contains rejects {type(value).__name__}:{value!r}")
        for second in ("read_only", None, [], {}):
            check(effect_boundary_by_key(value, second) is None, f"effect key lookup rejects malformed pair")
            check(capability_family_by_key(value, second) is None, f"family key lookup rejects malformed pair")

    # Every public validator must return a failed report rather than raise on arbitrary input.
    arbitrary_values = (None, True, False, 0, 1, -1, 3.14, "", "x", (), ("x",), [], ["x"], {}, {"x": "y"}, object())
    for validator in PUBLIC_VALIDATORS:
        for value in arbitrary_values:
            malformed_cases += 1
            try:
                malformed_report = validator(value)
            except Exception as error:
                failures.append(f"validator escaped exception {validator.__name__}:{type(value).__name__}:{type(error).__name__}")
                continue
            check(malformed_report.ok is False, f"validator rejects arbitrary {validator.__name__}:{type(value).__name__}")
            check(bool(malformed_report.issues), f"validator reports issue {validator.__name__}:{type(value).__name__}")

    canonical_records = (
        (rec.PROVENANCE_RECORDS[0], PUBLIC_VALIDATORS[0]),
        (rec.CURRENT_NAMESPACE, PUBLIC_VALIDATORS[1]),
        (rec.EFFECT_BOUNDARIES[0], PUBLIC_VALIDATORS[2]),
        (rec.CAPABILITY_FAMILIES[0], PUBLIC_VALIDATORS[3]),
        (rec.FRAME_EFFECT_REFERENCES[0], PUBLIC_VALIDATORS[4]),
        (rec.FRAME_CAPABILITY_REFERENCES[0], PUBLIC_VALIDATORS[5]),
        (rec.COMPATIBILITY_RECORDS[0], PUBLIC_VALIDATORS[6]),
        (rec.ADMISSION_AUTHORITY, PUBLIC_VALIDATORS[7]),
        (rec.TRANSITIONS[0], PUBLIC_VALIDATORS[8]),
        (rec.MANIFEST, PUBLIC_VALIDATORS[9]),
    )
    mutation_values = (
        None, True, False, 0, 1, -1, 3.14, "", " ", "unknown-value",
        (), ("duplicate", "duplicate"), [], ["x"], {}, {"x": "y"}, object(),
    )
    for canonical, validator in canonical_records:
        for field in fields(canonical):
            original = getattr(canonical, field.name)
            for value in mutation_values:
                try:
                    if type(value) is type(original) and value == original:
                        continue
                except Exception:
                    pass
                malformed_cases += 1
                try:
                    mutated = replace(canonical, **{field.name: value})
                    malformed_report = validator(mutated)
                except Exception as error:
                    failures.append(f"validator escaped mutation {type(canonical).__name__}.{field.name}:{type(value).__name__}:{type(error).__name__}")
                    continue
                check(malformed_report.ok is False, f"mutation rejected {type(canonical).__name__}.{field.name}:{type(value).__name__}")
                check(bool(malformed_report.issues), f"mutation issue {type(canonical).__name__}.{field.name}:{type(value).__name__}")

    # Registry-level nested and collection mutations must also fail closed.
    registry_mutations = {
        "manifest": None,
        "current_namespace": None,
        "effect_boundaries": (),
        "effect_boundary_histories": (),
        "capability_families": (),
        "capability_family_histories": (),
        "frame_effect_references": (),
        "frame_effect_reference_histories": (),
        "frame_capability_references": (),
        "frame_capability_reference_histories": (),
        "compatibility_records": (),
        "compatibility_histories": (),
        "authority_records": (),
        "transitions": (),
        "provenance_records": (),
    }
    for field_name, value in registry_mutations.items():
        malformed_cases += 1
        try:
            malformed_report = validate_registry(replace(registry, **{field_name: value}))
        except Exception as error:
            failures.append(f"registry validator escaped {field_name}:{type(error).__name__}")
            continue
        check(malformed_report.ok is False, f"registry mutation rejected {field_name}")
        check(bool(malformed_report.issues), f"registry mutation issue {field_name}")

    try:
        assert_valid(validate_registry(None))
    except CapabilityReferenceValidationError:
        check(True, "assert_valid rejects invalid report")
    else:
        check(False, "assert_valid must raise on invalid report")

    # Explicit non-collapse laws.
    check(all(not item.capability_available for item in registry.frame_capability_references), "capability reference not availability")
    check(all(not item.route_available and item.route_identity is None for item in registry.frame_capability_references), "availability not route")
    check(all(not item.invocation_proposed and item.invocation_identity is None for item in registry.frame_capability_references), "route not invocation")
    check(all(not item.invocation_authorized for item in registry.frame_capability_references), "invocation proposal not authorization")
    check(all(not item.execution_performed for item in registry.frame_capability_references), "invocation proposal not execution")
    check(all(not item.permission_granted and item.permission_id is None for item in registry.frame_capability_references), "frame completion not permission")
    check(all(not item.arguments_constructed and item.argument_bundle_id is None for item in registry.frame_capability_references), "reference not argument construction")
    check(all(not item.memory_operation_performed for item in registry.frame_capability_references), "reference not memory operation")
    check(all(not item.delivery_performed for item in registry.frame_capability_references), "reference not delivery")
    check(all(not item.external_resource_admitted for item in registry.frame_capability_references), "reference not external resource admission")
    check(all(not item.implementation_performed for item in registry.frame_capability_references), "reference not implementation")

    if failures:
        print("AI.WEB SLICE 38F BEHAVIOR TEST: FAIL")
        print(f"check_count={checks}")
        print(f"malformed_capability_reference_cases={malformed_cases}")
        print(f"failure_count={len(failures)}")
        for failure in failures[:200]:
            print(f"FAIL: {failure}")
        return 1

    print("AI.WEB SLICE 38F BEHAVIOR TEST: PASS")
    print(f"check_count={checks}")
    print(f"malformed_capability_reference_cases={malformed_cases}")
    print(f"effect_boundaries={len(registry.effect_boundaries)}")
    print(f"capability_families={len(registry.capability_families)}")
    print(f"frame_effect_references={len(registry.frame_effect_references)}")
    print(f"frame_capability_references={len(registry.frame_capability_references)}")
    print(f"capability_effect_compatibility_records={len(registry.compatibility_records)}")
    print(f"deferred_capability_families={len(DEFERRED_CAPABILITY_FAMILY_KEYS)}")
    print(f"frames_without_capability_reference={len(FRAMES_WITHOUT_CAPABILITY_REFERENCE)}")
    print(f"unbound_capability_families={len(UNBOUND_CAPABILITY_FAMILY_KEYS)}")
    print(f"lifecycle_transition_rules={len(CAPABILITY_REFERENCE_LIFECYCLE_RULES)}")
    print(f"lifecycle_transitions={len(registry.transitions)}")
    print("capability_reference_is_availability=0")
    print("capability_availability_is_route=0")
    print("route_is_invocation=0")
    print("invocation_proposal_is_execution=0")
    print("frame_completion_is_permission=0")
    print("argument_construction=0")
    print("memory_delivery_external_resource_implementation=0")
    print("routes_tools_actions_execution=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
