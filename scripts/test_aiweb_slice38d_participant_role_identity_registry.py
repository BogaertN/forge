#!/usr/bin/env python3
"""Behavior and adversarial validation test for Slice 38D."""

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

    from aiweb_language_core_bootstrap.predicate_role_frame_registry.participant_role_registry import (
        ADMITTED_PARTICIPANT_ROLE_KEYS,
        PARTICIPANT_ROLE_REGISTRY,
        PUBLIC_VALIDATORS,
        ROLE_LIFECYCLE_RULES,
        SLICE38D_DEFERRED_ROLE_CANDIDATES,
        ParticipantRoleConflictRecord,
        ParticipantRoleCorrectionRecord,
        ParticipantRoleLifecycleState,
        all_admitted_roles,
        all_role_dependencies,
        all_role_relationships,
        contains_role_id,
        dependency_by_id,
        expected_lineage_id,
        participant_role_registry,
        registry_manifest,
        relationship_by_id,
        role_by_id,
        role_by_key,
        transition_allowed,
        validate_conflict,
        validate_correction,
        validate_registry,
        version_advances,
        with_expected_id,
    )
    from aiweb_language_core_bootstrap.predicate_role_frame_registry.participant_role_registry.records import (
        ADMISSION_AUTHORITY,
        PROVENANCE_RECORDS,
    )
    from aiweb_language_core_bootstrap.predicate_role_frame_registry.participant_role_registry.schema import (
        ParticipantRoleResourceKind,
        ParticipantRoleTransitionKind,
    )

    checks = 0
    failures: list[str] = []
    malformed_cases = 0

    def check(condition: object, label: str) -> None:
        nonlocal checks
        checks += 1
        if condition is not True:
            failures.append(label)

    registry = participant_role_registry()
    check(registry is PARTICIPANT_ROLE_REGISTRY, "registry singleton")
    report = validate_registry(registry)
    check(report.ok, "registry validates")
    check(report.issues == (), "valid registry has no issues")
    check(registry_manifest() == registry.manifest, "manifest accessor")
    check(all_admitted_roles() == registry.admitted_roles, "role accessor")
    check(all_role_dependencies() == registry.dependencies, "dependency accessor")
    check(all_role_relationships() == registry.relationships, "relationship accessor")

    expected_keys = (
        "initiator", "actor", "action_subject", "content", "source",
        "recipient", "instrument", "condition", "standard", "result",
        "output_target",
    )
    check(ADMITTED_PARTICIPANT_ROLE_KEYS == expected_keys, "exact admitted role set")
    check(tuple(role.role_key for role in registry.admitted_roles) == expected_keys,
          "registry role order")
    check(len(registry.admitted_roles) == 11, "role count")
    check(len(registry.dependencies) == 11, "dependency count")
    check(len(registry.relationships) == 5, "relationship count")
    check(len(registry.corrections) == 0, "no invented corrections")
    check(len(registry.conflicts) == 0, "no invented conflicts")
    check(len(registry.transitions) == 28, "transition count")
    check(len(ROLE_LIFECYCLE_RULES) == 20, "transition rule count")
    check("affected_entity" in SLICE38D_DEFERRED_ROLE_CANDIDATES,
          "affected entity deferred")
    check("location" in SLICE38D_DEFERRED_ROLE_CANDIDATES, "location deferred")

    for role, history, dependency in zip(
        registry.admitted_roles, registry.role_histories, registry.dependencies, strict=True
    ):
        check(len(history) == 2, f"{role.role_key} history length")
        check(history[0].lifecycle_state is ParticipantRoleLifecycleState.CANDIDATE,
              f"{role.role_key} candidate ancestry")
        check(history[1] == role, f"{role.role_key} current history")
        check(role.lifecycle_state is ParticipantRoleLifecycleState.ARCHITECTURE_ADMITTED,
              f"{role.role_key} architecture admitted")
        check(version_advances(history[0].version, history[1].version),
              f"{role.role_key} version advances")
        check(expected_lineage_id(history[0]) == expected_lineage_id(history[1]),
              f"{role.role_key} lineage stable")
        check(role.frame_dependency_required is True, f"{role.role_key} frame dependency")
        check(role.action_root_dependency_required is True, f"{role.role_key} root dependency")
        check(role.semantic_relation_separation_required is True,
              f"{role.role_key} semantic relation separation")
        check(role.grammar_separation_required is True, f"{role.role_key} grammar separation")
        check(role.occurrence_assignment_allowed is False,
              f"{role.role_key} no occurrence assignment")
        check(role.role_selection_allowed is False, f"{role.role_key} no selection")
        check(dependency.role_id == role.role_id, f"{role.role_key} dependency target")
        check(dependency.satisfied_by_role_identity is False,
              f"{role.role_key} identity does not satisfy dependency")
        check(dependency.satisfied_by_registry_membership is False,
              f"{role.role_key} membership does not satisfy dependency")
        check(dependency.runtime_authority_supplied is False,
              f"{role.role_key} dependency no runtime authority")
        check(role_by_id(role.role_id) == role, f"{role.role_key} exact id lookup")
        check(role_by_key(role.namespace_id, role.role_key) == role,
              f"{role.role_key} exact key lookup")
        check(contains_role_id(role.role_id), f"{role.role_key} contains id")
        check(dependency_by_id(dependency.dependency_id) == dependency,
              f"{role.role_key} dependency id lookup")

    distinction_pairs = {
        ("initiator", "actor"),
        ("action_subject", "content"),
        ("source", "standard"),
        ("recipient", "output_target"),
        ("standard", "result"),
    }
    role_key_by_id = {role.role_id: role.role_key for role in registry.admitted_roles}
    observed_pairs = set()
    for relationship in registry.relationships:
        observed_pairs.add((role_key_by_id[relationship.left_role_id],
                            role_key_by_id[relationship.right_role_id]))
        check(relationship.role_assignment_performed is False,
              f"{relationship.relationship_key} no assignment")
        check(relationship.frame_constraint_created is False,
              f"{relationship.relationship_key} no frame constraint")
        check(relationship_by_id(relationship.relationship_id) == relationship,
              f"{relationship.relationship_key} exact lookup")
    check(observed_pairs == distinction_pairs, "exact distinction pairs")

    for transition in registry.transitions:
        check(transition_allowed(transition.from_state, transition.to_state,
                                 transition.transition_kind),
              f"transition allowed {transition.transition_id}")
        check(transition.authority_record_ref == ADMISSION_AUTHORITY.authority_id,
              f"transition authority {transition.transition_id}")
        check(transition.prior_record_preserved is True,
              f"transition ancestry {transition.transition_id}")
        check(transition.automatic_transition is False,
              f"transition not automatic {transition.transition_id}")
        check(transition.in_place_mutation_performed is False,
              f"transition no mutation {transition.transition_id}")
        check(transition.nearest_known_substitution_performed is False,
              f"transition no nearest mapping {transition.transition_id}")
        check(transition.similarity_authority_used is False,
              f"transition no similarity {transition.transition_id}")
        check(transition.role_assignment_performed is False,
              f"transition no assignment {transition.transition_id}")
        check(transition.runtime_authority_supplied is False,
              f"transition no runtime authority {transition.transition_id}")

    manifest = registry.manifest
    false_boundaries = (
        "surface_form_lookup_allowed", "surface_normalization_allowed",
        "occurrence_role_assignment_installed", "concept_candidate_to_role_assignment_installed",
        "semantic_relation_to_role_conversion_installed", "source_span_to_actor_conversion_installed",
        "grammatical_position_to_role_conversion_installed",
        "nearest_known_role_substitution_installed", "semantic_similarity_installed",
        "predicate_frame_population_installed", "frame_completion_installed",
        "capability_reference_population_installed", "capability_routing_installed",
        "route_registration_installed", "tool_activation_installed", "action_execution_installed",
        "evidence_validation_installed", "memory_access_installed", "rendering_installed",
        "delivery_installed", "external_resource_loading_installed", "llm_authority_installed",
    )
    for field_name in false_boundaries:
        check(getattr(manifest, field_name) is False, f"manifest boundary false {field_name}")

    # Exact lookup only: no case folding, aliases, words, paths, or fuzzy substitutes.
    for candidate in (
        "Actor", " actor", "actor ", "actors", "performer", "agent", "subject",
        "object", "affected_entity", "location", "output target", "output-target",
        "recipient@example.com", "/tmp/source", "nearest_actor",
    ):
        try:
            role_by_key(registry.current_namespace.namespace_id, candidate)
        except KeyError:
            check(True, f"approximate lookup refused {candidate!r}")
        else:
            check(False, f"approximate lookup accepted {candidate!r}")

    for bad in (None, 0, False, (), [], {}, set(), object()):
        check(contains_role_id(bad) is False, f"contains fails closed {type(bad).__name__}")
        try:
            role_by_id(bad)  # type: ignore[arg-type]
        except TypeError:
            check(True, f"role id exact type {type(bad).__name__}")
        else:
            check(False, f"role id accepted {type(bad).__name__}")

    # The correction and conflict schemas are supported without inventing a live incident.
    source_role = registry.role_histories[0][0]
    target_role = registry.role_histories[0][1]
    correction = with_expected_id(
        ParticipantRoleCorrectionRecord(
            correction_id="",
            role_lineage_id=expected_lineage_id(target_role),
            source_role_id=source_role.role_id,
            target_role_id=target_role.role_id,
            source_version=source_role.version,
            target_version=target_role.version,
            corrected_fields=("definition",),
            reason="Synthetic shape-validation fixture only.",
            scope=("fixture:shape-validation",),
            non_scope=("live correction",),
            provenance_refs=tuple(item.provenance_id for item in PROVENANCE_RECORDS),
            authority_record_ref=ADMISSION_AUTHORITY.authority_id,
            prior_record_preserved=True,
            in_place_mutation_performed=False,
            runtime_authority_supplied=False,
            lifecycle_state=ParticipantRoleLifecycleState.ARCHITECTURE_ADMITTED,
        )
    )
    check(validate_correction(correction).ok, "valid correction shape supported")

    conflict = with_expected_id(
        ParticipantRoleConflictRecord(
            conflict_id="",
            conflict_key="fixture_role_conflict",
            role_refs=(registry.admitted_roles[0].role_id, registry.admitted_roles[1].role_id),
            conflict_kind="fixture_only",
            definition="Synthetic shape-validation fixture only.",
            scope=("fixture:shape-validation",),
            non_scope=("live conflict",),
            provenance_refs=tuple(item.provenance_id for item in PROVENANCE_RECORDS),
            authority_record_ref=ADMISSION_AUTHORITY.authority_id,
            resolved=False,
            resolution_ref=None,
            role_assignment_allowed=False,
            frame_use_allowed=False,
            capability_binding_allowed=False,
            runtime_authority_supplied=False,
            lifecycle_state=ParticipantRoleLifecycleState.CONFLICTED,
        )
    )
    check(validate_conflict(conflict).ok, "valid conflict shape supported")

    # Total fail-closed public validators across hostile values and malformed fields.
    hostile_values = (None, "", " ", 0, 1, False, True, [], {}, set(), object(), ("ok", []))
    for validator in PUBLIC_VALIDATORS:
        for hostile in hostile_values:
            malformed_cases += 1
            try:
                hostile_report = validator(hostile)
            except Exception as error:
                failures.append(f"validator escaped {validator.__name__}: {type(error).__name__}")
            else:
                check(hostile_report.ok is False,
                      f"validator rejects hostile {validator.__name__}:{type(hostile).__name__}")

    representative_records = (
        registry.current_namespace,
        registry.admitted_roles[0],
        registry.dependencies[0],
        registry.relationships[0],
        correction,
        conflict,
        ADMISSION_AUTHORITY,
        registry.transitions[0],
        registry.manifest,
    )
    validator_by_type = {
        type(registry.current_namespace): PUBLIC_VALIDATORS[1],
        type(registry.admitted_roles[0]): PUBLIC_VALIDATORS[2],
        type(registry.dependencies[0]): PUBLIC_VALIDATORS[3],
        type(registry.relationships[0]): PUBLIC_VALIDATORS[4],
        type(correction): PUBLIC_VALIDATORS[5],
        type(conflict): PUBLIC_VALIDATORS[6],
        type(ADMISSION_AUTHORITY): PUBLIC_VALIDATORS[7],
        type(registry.transitions[0]): PUBLIC_VALIDATORS[8],
        type(registry.manifest): PUBLIC_VALIDATORS[9],
    }
    invalid_field_values = (None, [], {}, set(), object(), ("nested", []))
    for record in representative_records:
        validator = validator_by_type[type(record)]
        for field in fields(record):
            if not field.init:
                continue
            for bad in invalid_field_values:
                if field.name == "resolution_ref" and bad is None:
                    continue
                malformed_cases += 1
                try:
                    malformed = replace(record, **{field.name: bad})
                    malformed_report = validator(malformed)
                except Exception as error:
                    failures.append(
                        f"malformed field escaped {type(record).__name__}.{field.name}: {type(error).__name__}"
                    )
                else:
                    check(malformed_report.ok is False,
                          f"malformed field rejected {type(record).__name__}.{field.name}")

    # Registry-level malformed nested values must never escape.
    for field_name in ("admitted_roles", "dependencies", "relationships", "transitions",
                       "provenance_records", "role_histories", "dependency_histories",
                       "relationship_histories"):
        for bad in ([], {}, set(), ("bad", []), (object(),)):
            malformed_cases += 1
            try:
                malformed_registry = replace(registry, **{field_name: bad})
                malformed_report = validate_registry(malformed_registry)
            except Exception as error:
                failures.append(f"registry validator escaped {field_name}: {type(error).__name__}")
            else:
                check(malformed_report.ok is False, f"registry malformed {field_name} rejected")

    check(transition_allowed(ParticipantRoleLifecycleState.CANDIDATE,
                             ParticipantRoleLifecycleState.ARCHITECTURE_ADMITTED,
                             ParticipantRoleTransitionKind.ARCHITECTURE_ADMIT),
          "candidate architecture admission allowed")
    check(not transition_allowed(ParticipantRoleLifecycleState.UNKNOWN,
                                 ParticipantRoleLifecycleState.ARCHITECTURE_ADMITTED,
                                 ParticipantRoleTransitionKind.ARCHITECTURE_ADMIT),
          "unknown direct admission prohibited")

    if failures:
        print("AI.WEB SLICE 38D BEHAVIOR TEST: FAIL")
        print(f"check_count={checks}")
        print(f"malformed_role_cases={malformed_cases}")
        print(f"failure_count={len(failures)}")
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("AI.WEB SLICE 38D BEHAVIOR TEST: PASS")
    print(f"check_count={checks}")
    print(f"malformed_role_cases={malformed_cases}")
    print("admitted_participant_roles=11")
    print("role_dependencies=11")
    print("role_relationships=5")
    print("active_corrections=0")
    print("active_conflicts=0")
    print("lifecycle_transition_rules=20")
    print("lifecycle_transitions=28")
    print("semantic_relation_to_role_conversion=0")
    print("concept_candidate_to_role_assignment=0")
    print("source_span_to_actor_conversion=0")
    print("grammatical_position_to_role_conversion=0")
    print("occurrence_role_assignment=0")
    print("predicate_frames_capabilities_routes_tools_actions=0")
    print("evidence_memory_rendering_delivery=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
