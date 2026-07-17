#!/usr/bin/env python3
"""Behavior and adversarial validation test for Slice 38E."""

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

    from aiweb_language_core_bootstrap.predicate_role_frame_registry.predicate_frame_registry import (
        ADMITTED_PREDICATE_FRAME_KEYS,
        PREDICATE_FRAME_REGISTRY,
        PUBLIC_VALIDATORS,
        ROLE_LIFECYCLE_RULES,
        SLICE38E_DEFERRED_FRAME_FAMILIES,
        FrameCapabilityReferenceStatus,
        FrameRoleCardinality,
        FrameRoleRequirement,
        PredicateFrameLifecycleState,
        PredicateFrameStructuralState,
        PredicateFrameTransitionKind,
        all_admitted_frames,
        all_compatibility_rules,
        all_role_constraints,
        all_structural_state_policies,
        compatibility_by_id,
        constraint_by_id,
        contains_frame_id,
        expected_lineage_id,
        frame_by_id,
        frame_by_key,
        predicate_frame_registry,
        registry_manifest,
        structural_state_policy,
        transition_allowed,
        validate_registry,
        version_advances,
    )
    from aiweb_language_core_bootstrap.predicate_role_frame_registry.built_in_action_root_registry import (
        BUILT_IN_ACTION_ROOT_REGISTRY,
    )
    from aiweb_language_core_bootstrap.predicate_role_frame_registry.participant_role_registry import (
        PARTICIPANT_ROLE_REGISTRY,
    )
    from aiweb_language_core_bootstrap.controlled_concept_sense_registry.semantic_class_relation_registry import (
        SEMANTIC_CLASS_RELATION_REGISTRY,
    )

    checks = 0
    failures: list[str] = []
    malformed_cases = 0

    def check(condition: object, label: str) -> None:
        nonlocal checks
        checks += 1
        if condition is not True:
            failures.append(label)

    registry = predicate_frame_registry()
    check(registry is PREDICATE_FRAME_REGISTRY, "registry singleton")
    report = validate_registry(registry)
    check(report.ok, "registry validates")
    check(report.issues == (), "valid registry has no issues")
    check(registry_manifest() == registry.manifest, "manifest accessor")
    check(all_admitted_frames() == registry.admitted_frames, "frame accessor")
    check(all_role_constraints() == registry.role_constraints, "constraint accessor")
    check(all_compatibility_rules() == registry.compatibility_rules, "compatibility accessor")
    check(all_structural_state_policies() == registry.structural_state_policies, "state policy accessor")

    expected_frame_keys = (
        "inspect_read_only",
        "report_attributed_content",
        "request_non_authorizing",
        "verify_bounded_review",
        "simulate_non_live",
    )
    check(ADMITTED_PREDICATE_FRAME_KEYS == expected_frame_keys, "exact frame set")
    check(tuple(item.frame_key for item in registry.admitted_frames) == expected_frame_keys, "frame order")
    check(len(registry.admitted_frames) == 5, "frame count")
    check(len(registry.frame_histories) == 5, "history count")
    check(len(registry.role_constraints) == 55, "role constraint count")
    check(len(registry.compatibility_rules) == 55, "compatibility count")
    check(len(registry.structural_state_policies) == 6, "structural policy count")
    check(len(registry.transitions) == 5, "transition count")
    check(len(ROLE_LIFECYCLE_RULES) == 20, "lifecycle rule count")

    action_root_by_id = {
        item.action_root_id: item
        for item in BUILT_IN_ACTION_ROOT_REGISTRY.admitted_action_roots
    }
    predicate_by_id = {
        item.predicate_id: item
        for item in BUILT_IN_ACTION_ROOT_REGISTRY.admitted_predicates
    }
    role_by_id = {
        item.role_id: item
        for item in PARTICIPANT_ROLE_REGISTRY.admitted_roles
    }
    class_by_id = {
        item.semantic_class_id: item
        for item in SEMANTIC_CLASS_RELATION_REGISTRY.semantic_classes
    }

    expected_requirements = {
        "inspect_read_only": {
            "initiator": "optional", "actor": "optional", "action_subject": "required",
            "content": "prohibited", "source": "optional", "recipient": "prohibited",
            "instrument": "optional", "condition": "optional", "standard": "optional",
            "result": "optional", "output_target": "optional",
        },
        "report_attributed_content": {
            "initiator": "optional", "actor": "optional", "action_subject": "optional",
            "content": "required", "source": "optional", "recipient": "optional",
            "instrument": "optional", "condition": "optional", "standard": "optional",
            "result": "optional", "output_target": "optional",
        },
        "request_non_authorizing": {
            "initiator": "required", "actor": "optional", "action_subject": "optional",
            "content": "required", "source": "optional", "recipient": "conditional",
            "instrument": "optional", "condition": "optional", "standard": "optional",
            "result": "prohibited", "output_target": "optional",
        },
        "verify_bounded_review": {
            "initiator": "optional", "actor": "optional", "action_subject": "required",
            "content": "prohibited", "source": "conditional", "recipient": "prohibited",
            "instrument": "optional", "condition": "optional", "standard": "required",
            "result": "optional", "output_target": "optional",
        },
        "simulate_non_live": {
            "initiator": "optional", "actor": "optional", "action_subject": "required",
            "content": "optional", "source": "optional", "recipient": "prohibited",
            "instrument": "optional", "condition": "required", "standard": "conditional",
            "result": "optional", "output_target": "optional",
        },
    }

    for frame, history in zip(registry.admitted_frames, registry.frame_histories, strict=True):
        check(frame.lifecycle_state is PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED,
              f"{frame.frame_key} architecture admitted")
        check(frame.linked_action_root_id in action_root_by_id, f"{frame.frame_key} root admitted")
        check(frame.linked_predicate_id in predicate_by_id, f"{frame.frame_key} predicate admitted")
        check(action_root_by_id[frame.linked_action_root_id].action_root_key == frame.linked_action_root_key,
              f"{frame.frame_key} root key exact")
        check(predicate_by_id[frame.linked_predicate_id].predicate_key == frame.linked_predicate_key,
              f"{frame.frame_key} predicate key exact")
        check(frame.linked_action_root_key == frame.linked_predicate_key,
              f"{frame.frame_key} root predicate alignment")
        check(frame_by_id(frame.frame_id) == frame, f"{frame.frame_key} id lookup")
        check(frame_by_key(frame.namespace_id, frame.frame_key) == frame,
              f"{frame.frame_key} exact key lookup")
        check(contains_frame_id(frame.frame_id), f"{frame.frame_key} contains id")
        check(len(history) == 2, f"{frame.frame_key} history length")
        check(history[0].lifecycle_state is PredicateFrameLifecycleState.CANDIDATE,
              f"{frame.frame_key} candidate ancestry")
        check(history[1] == frame, f"{frame.frame_key} current ancestry")
        check(version_advances(history[0].version, history[1].version),
              f"{frame.frame_key} version advances")
        check(expected_lineage_id(history[0]) == expected_lineage_id(history[1]),
              f"{frame.frame_key} lineage stable")
        check(frame.structurally_complete_is_permission is False,
              f"{frame.frame_key} complete not permission")
        check(frame.occurrence_frame_selection_allowed is False,
              f"{frame.frame_key} no selection")
        check(frame.occurrence_role_assignment_allowed is False,
              f"{frame.frame_key} no role assignment")
        check(frame.frame_completion_allowed is False,
              f"{frame.frame_key} no occurrence completion")
        check(frame.capability_binding_allowed is False,
              f"{frame.frame_key} no capability binding")
        check(frame.gate_outcome_created is False, f"{frame.frame_key} no gate outcome")
        check(frame.execution_authorized is False, f"{frame.frame_key} no execution")
        check(frame.capability_reference_status is FrameCapabilityReferenceStatus.DEFERRED_TO_SLICE38F,
              f"{frame.frame_key} capability refs deferred")
        check(frame.capability_reference_refs == (), f"{frame.frame_key} no capability refs")

        constraints = tuple(item for item in registry.role_constraints if item.frame_key == frame.frame_key)
        compatibilities = tuple(item for item in registry.compatibility_rules if item.frame_key == frame.frame_key)
        check(len(constraints) == 11, f"{frame.frame_key} all 11 role constraints")
        check(len(compatibilities) == 11, f"{frame.frame_key} all 11 compatibility rules")
        check({item.role_id for item in constraints} == set(role_by_id), f"{frame.frame_key} exact role coverage")
        check({item.role_id for item in compatibilities} == set(role_by_id), f"{frame.frame_key} exact compatibility role coverage")

        actual_requirements = {item.role_key: item.requirement.value for item in constraints}
        check(actual_requirements == expected_requirements[frame.frame_key],
              f"{frame.frame_key} exact role requirements")

        partition = (
            frame.required_role_constraint_refs
            + frame.optional_role_constraint_refs
            + frame.prohibited_role_constraint_refs
            + frame.conditional_role_constraint_refs
        )
        check(len(partition) == 11, f"{frame.frame_key} partition count")
        check(set(partition) == {item.constraint_id for item in constraints},
              f"{frame.frame_key} exact partition")
        check(set(frame.role_cardinality_constraint_refs) == {item.constraint_id for item in constraints},
              f"{frame.frame_key} every role cardinality")
        check(frame.role_concept_compatibility_refs == tuple(item.compatibility_id for item in compatibilities),
              f"{frame.frame_key} compatibility refs exact")

        for constraint in constraints:
            check(constraint.role_id in role_by_id, f"{frame.frame_key}:{constraint.role_key} role admitted")
            check(role_by_id[constraint.role_id].role_key == constraint.role_key,
                  f"{frame.frame_key}:{constraint.role_key} role key exact")
            check(constraint_by_id(constraint.constraint_id) == constraint,
                  f"{frame.frame_key}:{constraint.role_key} constraint lookup")
            check(constraint.occurrence_assignment_allowed is False,
                  f"{frame.frame_key}:{constraint.role_key} no assignment")
            check(constraint.gate_outcome_created is False,
                  f"{frame.frame_key}:{constraint.role_key} no gate")
            check(constraint.authority_satisfied is False,
                  f"{frame.frame_key}:{constraint.role_key} no authority")
            check(constraint.capability_argument_created is False,
                  f"{frame.frame_key}:{constraint.role_key} no capability arg")
            check(constraint.execution_authorized is False,
                  f"{frame.frame_key}:{constraint.role_key} no execution")
            if constraint.requirement is FrameRoleRequirement.REQUIRED:
                check(constraint.cardinality in (FrameRoleCardinality.EXACTLY_ONE, FrameRoleCardinality.ONE_OR_MORE),
                      f"{frame.frame_key}:{constraint.role_key} required cardinality")
            if constraint.requirement is FrameRoleRequirement.CONDITIONAL:
                check(type(constraint.condition_key) is str and bool(constraint.condition_key),
                      f"{frame.frame_key}:{constraint.role_key} conditional trigger")
            else:
                check(constraint.condition_key is None,
                      f"{frame.frame_key}:{constraint.role_key} no hidden trigger")
            check(all(ref in role_by_id and ref != constraint.role_id for ref in constraint.co_required_role_ids),
                  f"{frame.frame_key}:{constraint.role_key} co-required refs")
            check(all(ref in role_by_id and ref != constraint.role_id for ref in constraint.conflicting_role_ids),
                  f"{frame.frame_key}:{constraint.role_key} conflict refs")

        for compatibility in compatibilities:
            check(compatibility_by_id(compatibility.compatibility_id) == compatibility,
                  f"{frame.frame_key}:{compatibility.role_key} compatibility lookup")
            check(compatibility.allowed_concept_refs == (),
                  f"{frame.frame_key}:{compatibility.role_key} no invented concept allowlist")
            check(bool(compatibility.allowed_semantic_class_refs),
                  f"{frame.frame_key}:{compatibility.role_key} review class refs present")
            check(all(ref in class_by_id for ref in compatibility.allowed_semantic_class_refs),
                  f"{frame.frame_key}:{compatibility.role_key} classes admitted")
            check(compatibility.semantic_class_membership_sufficient is False,
                  f"{frame.frame_key}:{compatibility.role_key} class not sufficient")
            check(compatibility.exact_concept_allowlist_required is True,
                  f"{frame.frame_key}:{compatibility.role_key} exact concept required")
            check(compatibility.unknown_if_exact_support_absent is True,
                  f"{frame.frame_key}:{compatibility.role_key} unknown preserved")
            check(compatibility.external_only_support_allowed is False,
                  f"{frame.frame_key}:{compatibility.role_key} no external-only support")
            check(compatibility.quarantined_support_allowed is False,
                  f"{frame.frame_key}:{compatibility.role_key} no quarantined support")
            check(compatibility.similarity_support_allowed is False,
                  f"{frame.frame_key}:{compatibility.role_key} no similarity")
            check(compatibility.occurrence_assignment_allowed is False,
                  f"{frame.frame_key}:{compatibility.role_key} no concept assignment")

    expected_states = tuple(PredicateFrameStructuralState)
    check(tuple(item.state for item in registry.structural_state_policies) == expected_states,
          "exact six structural states")
    for policy in registry.structural_state_policies:
        check(structural_state_policy(policy.state) == policy, f"{policy.state.value} state lookup")
        check(policy.gate_outcome_created is False, f"{policy.state.value} no gate outcome")
        check(policy.permission_created is False, f"{policy.state.value} no permission")
        check(policy.capability_binding_created is False, f"{policy.state.value} no capability")
        check(policy.execution_authorized is False, f"{policy.state.value} no execution")

    for transition in registry.transitions:
        check(transition_allowed(transition.from_state, transition.to_state, transition.transition_kind),
              f"transition allowed {transition.transition_id}")
        check(transition.prior_record_preserved is True, f"transition ancestry {transition.transition_id}")
        check(transition.automatic_transition is False, f"transition not automatic {transition.transition_id}")
        check(transition.frame_selection_performed is False, f"transition no selection {transition.transition_id}")
        check(transition.role_assignment_performed is False, f"transition no role assignment {transition.transition_id}")
        check(transition.capability_binding_performed is False, f"transition no capability {transition.transition_id}")
        check(transition.gate_outcome_created is False, f"transition no gate {transition.transition_id}")
        check(transition.runtime_authority_supplied is False, f"transition no runtime {transition.transition_id}")

    manifest = registry.manifest
    false_boundaries = (
        "source_term_lookup_installed", "occurrence_frame_selection_installed",
        "occurrence_role_assignment_installed", "candidate_meaning_creation_installed",
        "selected_meaning_installed", "gate_outcome_installed",
        "capability_reference_population_installed", "capability_routing_installed",
        "route_registration_installed", "tool_activation_installed", "action_execution_installed",
        "evidence_validation_installed", "memory_access_installed", "rendering_installed",
        "delivery_installed", "external_resource_loading_installed",
        "nearest_known_frame_substitution_installed", "semantic_similarity_installed",
        "llm_authority_installed",
    )
    for field_name in false_boundaries:
        check(getattr(manifest, field_name) is False, f"manifest boundary false {field_name}")
    check(manifest.registry_read_only is True, "registry read only")
    check(manifest.registry_closed is True, "registry closed")
    check(manifest.exact_identity_lookup_only is True, "exact lookup only")

    for candidate in (
        "Inspect_Read_Only", " inspect_read_only", "inspect_read_only ", "inspect",
        "read_only_inspection", "report", "request", "verify", "simulate",
        "nearest_frame", "inspect-read-only", "/tmp/frame", "frame:inspect_read_only",
    ):
        try:
            frame_by_key(registry.current_namespace.namespace_id, candidate)
        except KeyError:
            check(True, f"approximate frame lookup refused {candidate!r}")
        else:
            check(False, f"approximate frame lookup accepted {candidate!r}")

    for bad in (None, 0, False, (), [], {}, set(), object()):
        check(contains_frame_id(bad) is False, f"contains fails closed {type(bad).__name__}")
        try:
            frame_by_id(bad)  # type: ignore[arg-type]
        except TypeError:
            check(True, f"frame id exact type {type(bad).__name__}")
        else:
            check(False, f"frame id accepted {type(bad).__name__}")

    check(any("approval" in item for item in SLICE38E_DEFERRED_FRAME_FAMILIES), "approval frame deferred")
    check(any("installation" in item for item in SLICE38E_DEFERRED_FRAME_FAMILIES), "installation frame deferred")
    check(any("delivery" in item for item in SLICE38E_DEFERRED_FRAME_FAMILIES), "delivery frame deferred")
    check(any("memory" in item for item in SLICE38E_DEFERRED_FRAME_FAMILIES), "memory frame deferred")
    check(any("rollback" in item for item in SLICE38E_DEFERRED_FRAME_FAMILIES), "rollback frame deferred")

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
        registry.provenance_records[0],
        registry.current_namespace,
        registry.compatibility_rules[0],
        registry.role_constraints[0],
        registry.admitted_frames[0],
        registry.structural_state_policies[0],
        registry.authority_records[0],
        registry.transitions[0],
        registry.manifest,
    )
    validator_by_type = {
        type(registry.provenance_records[0]): PUBLIC_VALIDATORS[0],
        type(registry.current_namespace): PUBLIC_VALIDATORS[1],
        type(registry.compatibility_rules[0]): PUBLIC_VALIDATORS[2],
        type(registry.role_constraints[0]): PUBLIC_VALIDATORS[3],
        type(registry.admitted_frames[0]): PUBLIC_VALIDATORS[4],
        type(registry.structural_state_policies[0]): PUBLIC_VALIDATORS[5],
        type(registry.authority_records[0]): PUBLIC_VALIDATORS[6],
        type(registry.transitions[0]): PUBLIC_VALIDATORS[7],
        type(registry.manifest): PUBLIC_VALIDATORS[8],
    }
    invalid_field_values = (None, [], {}, set(), object(), ("nested", []))
    for record in representative_records:
        validator = validator_by_type[type(record)]
        for field in fields(record):
            if not field.init:
                continue
            for bad in invalid_field_values:
                if field.name in ("condition_key",) and bad is None:
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

    for field_name in (
        "admitted_frames", "frame_histories", "role_constraints", "compatibility_rules",
        "structural_state_policies", "authority_records", "transitions", "provenance_records",
    ):
        for bad in ([], {}, set(), ("bad", []), (object(),)):
            malformed_cases += 1
            try:
                malformed_registry = replace(registry, **{field_name: bad})
                malformed_report = validate_registry(malformed_registry)
            except Exception as error:
                failures.append(f"registry validator escaped {field_name}: {type(error).__name__}")
            else:
                check(malformed_report.ok is False, f"registry malformed {field_name} rejected")

    for constraint in registry.role_constraints:
        malformed_cases += 1
        bad = replace(constraint, co_required_role_ids=([],))  # type: ignore[arg-type]
        try:
            bad_report = PUBLIC_VALIDATORS[3](bad)
        except Exception as error:
            failures.append(f"constraint nested validator escaped: {type(error).__name__}")
        else:
            check(bad_report.ok is False, "nested co-required value rejected")

    for compatibility in registry.compatibility_rules:
        malformed_cases += 1
        bad = replace(compatibility, allowed_semantic_class_refs=({},))  # type: ignore[arg-type]
        try:
            bad_report = PUBLIC_VALIDATORS[2](bad)
        except Exception as error:
            failures.append(f"compatibility nested validator escaped: {type(error).__name__}")
        else:
            check(bad_report.ok is False, "nested semantic class ref rejected")

    check(transition_allowed(PredicateFrameLifecycleState.CANDIDATE,
                             PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED,
                             PredicateFrameTransitionKind.ARCHITECTURE_ADMIT),
          "candidate architecture admission allowed")
    check(not transition_allowed(PredicateFrameLifecycleState.UNKNOWN,
                                 PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED,
                                 PredicateFrameTransitionKind.ARCHITECTURE_ADMIT),
          "unknown direct admission prohibited")

    if failures:
        print("AI.WEB SLICE 38E BEHAVIOR TEST: FAIL")
        print(f"check_count={checks}")
        print(f"malformed_frame_cases={malformed_cases}")
        print(f"failure_count={len(failures)}")
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("AI.WEB SLICE 38E BEHAVIOR TEST: PASS")
    print(f"check_count={checks}")
    print(f"malformed_frame_cases={malformed_cases}")
    print("admitted_predicate_frames=5")
    print("frame_role_constraints=55")
    print("role_concept_compatibility_rules=55")
    print("structural_state_policies=6")
    print("frame_lifecycle_rules=20")
    print("frame_lifecycle_transitions=5")
    print("exact_concept_allowlists_populated=0")
    print("semantic_class_membership_sufficient=0")
    print("occurrence_frame_selection=0")
    print("occurrence_role_assignment=0")
    print("candidate_meaning_gate_outcome=0")
    print("capability_references_routes_tools_actions=0")
    print("evidence_memory_rendering_delivery=0")
    print("structurally_complete_is_permission=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
