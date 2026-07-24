#!/usr/bin/env python3
"""Real Slice 38 registry-to-Slice 40 gate version-custody regression."""

from __future__ import annotations

import argparse
import importlib
import runpy
import sys
from dataclasses import replace
from pathlib import Path


def _real_slice38_pair(repository: Path):
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

    custody = capture_input_event(
        "Please inspect concept admission.",
        source_id="aiweb.bridge5b.version.custody.test",
        channel_id="aiweb.bridge5b.version.custody.test",
        sequence_number=0,
    )
    projection = project_source_field(custody.event)
    binding = bind_resonant_operator_candidates(projection)
    trails = construct_candidate_resonant_phase_trails(projection, binding)
    constraints = apply_scope_attachment_reference_constraints(
        projection,
        binding,
        trails,
    )
    structural = derive_deterministic_structural_analysis(
        custody,
        projection,
        binding,
        trails,
        constraints,
    )
    slice37 = propose_structural_concept_candidates(
        custody,
        projection,
        structural,
    )

    compatibility_rules = []
    for concept_index, concept in enumerate(slice37.concept_candidates):
        for sense_index, sense in enumerate(slice37.sense_candidates):
            if sense.concept_id != concept.concept_id:
                continue
            compatibility_rules.append(
                build_exact_compatibility_rule(
                    rule_key=(
                        "aiweb.bridge5b.version.inspect."
                        f"{concept_index}.{sense_index}"
                    ),
                    action_root_key="inspect",
                    concept_id=concept.concept_id,
                    sense_id=sense.sense_id,
                    allowed_frame_keys=("inspect_read_only",),
                )
            )

    if not compatibility_rules:
        raise AssertionError("real Slice 37 chain produced no exact compatibility rule")

    snapshot = build_compatibility_snapshot(
        rules=tuple(compatibility_rules),
        registry_key="aiweb.bridge5b.version.inspect",
    )
    slice38 = propose_predicate_role_frame_candidates(
        slice37,
        compatibility_snapshot=snapshot,
    )

    predicates = tuple(slice38.action_predicate_candidates)
    layouts = tuple(slice38.role_layout_candidates)
    if not predicates or not layouts:
        raise AssertionError("real Slice 38 chain produced no predicate/frame candidate")

    predicate = predicates[0]
    matching_layouts = tuple(
        item
        for item in layouts
        if item.predicate_id == predicate.predicate_id
        and item.action_root_id == predicate.action_root_id
        and (item.frame_id, item.frame_version) in predicate.frame_ids_and_versions
    )
    if not matching_layouts:
        raise AssertionError("real Slice 38 predicate has no exact linked role layout")

    layout = matching_layouts[0]
    return predicate, layout


def _replace_expectancy(module, helpers, bundle, pair):
    predicate, layout = pair
    kinds = tuple(module.ExpectancyRequirementKind)
    requirements = []
    observations = []
    for kind in kinds:
        requirement = helpers["make_requirement"](
            module,
            bundle,
            kind,
            kind.value,
            required=(kind is not module.ExpectancyRequirementKind.OPTIONAL_DETAIL),
        )
        requirement = module.with_expected_requirement_id(
            replace(
                requirement,
                predicate_id=predicate.predicate_id,
                predicate_version=predicate.predicate_version,
                frame_id=layout.frame_id,
                frame_version=layout.frame_version,
            )
        )
        observation = helpers["make_observation"](
            module,
            bundle,
            requirement,
            state=module.ExpectancyAuthorityState.ABSENT,
            count=0,
        )
        requirements.append(requirement)
        observations.append(observation)

    value = helpers["make_input"](
        module,
        bundle,
        tuple(requirements),
        tuple(observations),
    )
    return module.with_expected_evaluation_input_id(
        replace(
            value,
            predicate_id=predicate.predicate_id,
            predicate_version=predicate.predicate_version,
            frame_id=layout.frame_id,
            frame_version=layout.frame_version,
            requirements=tuple(requirements),
            observations=tuple(observations),
        )
    )


def _replace_congruity(module, helpers, bundle, pair):
    predicate, layout = pair
    assertions = []
    observations = []
    for kind in module.CongruityAssertionKind:
        assertion = helpers["make_assertion"](
            module,
            bundle,
            kind,
            kind.value,
        )
        assertion = module.with_expected_assertion_id(
            replace(
                assertion,
                predicate_id=predicate.predicate_id,
                predicate_version=predicate.predicate_version,
                frame_id=layout.frame_id,
                frame_version=layout.frame_version,
            )
        )
        observation = helpers["make_observation"](
            module,
            bundle,
            assertion,
            authority=module.CongruityAuthorityState.ABSENT,
            judgment=module.CongruityCompatibilityJudgment.NOT_EVALUATED,
        )
        assertions.append(assertion)
        observations.append(observation)

    value = helpers["make_input"](
        module,
        bundle,
        tuple(assertions),
        tuple(observations),
    )
    return module.with_expected_evaluation_input_id(
        replace(
            value,
            predicate_id=predicate.predicate_id,
            predicate_version=predicate.predicate_version,
            frame_id=layout.frame_id,
            frame_version=layout.frame_version,
            assertions=tuple(assertions),
            observations=tuple(observations),
        )
    )


def _replace_connectedness(module, helpers, bundle, pair):
    predicate, layout = pair
    assertions = []
    observations = []
    for kind in module.ConnectednessAssertionKind:
        assertion = helpers["make_assertion"](
            module,
            bundle,
            kind,
            kind.value,
        )
        assertion = module.with_expected_assertion_id(
            replace(
                assertion,
                predicate_id=predicate.predicate_id,
                predicate_version=predicate.predicate_version,
                frame_id=layout.frame_id,
                frame_version=layout.frame_version,
            )
        )
        observation = helpers["make_observation"](
            module,
            bundle,
            assertion,
            authority=module.ConnectednessAuthorityState.ABSENT,
            judgment=module.ConnectednessJudgment.NOT_EVALUATED,
        )
        assertions.append(assertion)
        observations.append(observation)

    value = helpers["make_input"](
        module,
        bundle,
        tuple(assertions),
        tuple(observations),
    )
    return module.with_expected_evaluation_input_id(
        replace(
            value,
            predicate_id=predicate.predicate_id,
            predicate_version=predicate.predicate_version,
            frame_id=layout.frame_id,
            frame_version=layout.frame_version,
            assertions=tuple(assertions),
            observations=tuple(observations),
        )
    )


def _replace_recoverable(module, helpers, bundle, pair):
    predicate, layout = pair
    assertions = []
    observations = []
    for kind in module.PurportDistinctionKind:
        represented, conflated = module.PURPORT_DISTINCTION_PAIRS[kind]
        assertion = helpers["make_assertion"](
            module,
            bundle,
            kind,
            represented,
            conflated,
        )
        assertion = module.with_expected_assertion_id(
            replace(
                assertion,
                predicate_id=predicate.predicate_id,
                predicate_version=predicate.predicate_version,
                frame_id=layout.frame_id,
                frame_version=layout.frame_version,
            )
        )
        observation = helpers["make_observation"](
            module,
            bundle,
            assertion,
            authority=module.RecoverablePurposeAuthorityState.ABSENT,
            judgment=module.RecoverablePurposeJudgment.NOT_EVALUATED,
        )
        assertions.append(assertion)
        observations.append(observation)

    value = helpers["make_input"](
        module,
        bundle,
        tuple(assertions),
        tuple(observations),
    )
    return module.with_expected_evaluation_input_id(
        replace(
            value,
            predicate_id=predicate.predicate_id,
            predicate_version=predicate.predicate_version,
            frame_id=layout.frame_id,
            frame_version=layout.frame_version,
            assertions=tuple(assertions),
            observations=tuple(observations),
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    sys.path.insert(0, str(repository))

    pair = _real_slice38_pair(repository)
    predicate, layout = pair

    if predicate.predicate_version != "v1.3.0":
        print(f"FAIL - unexpected current predicate version: {predicate.predicate_version}")
        return 1
    if layout.frame_version != "v1.1.0":
        print(f"FAIL - unexpected current frame version: {layout.frame_version}")
        return 1

    from aiweb_language_core_bootstrap.predicate_role_frame_registry.built_in_action_root_registry.registry import (
        predicate_by_id,
    )
    from aiweb_language_core_bootstrap.predicate_role_frame_registry.predicate_frame_registry.registry import (
        all_admitted_frames,
        frame_by_id,
    )
    from aiweb_language_core_bootstrap.verbal_cognition_gate_runtime.predicate_frame_version_custody import (
        invalid_predicate_frame_version_fields,
    )

    registered_predicate = predicate_by_id(predicate.predicate_id)
    registered_frame = frame_by_id(layout.frame_id)
    if registered_predicate.version != predicate.predicate_version:
        print("FAIL - real Slice 38 predicate version lost registry custody")
        return 1
    if registered_frame.version != layout.frame_version:
        print("FAIL - real Slice 38 frame version lost registry custody")
        return 1
    if registered_frame.linked_predicate_id != registered_predicate.predicate_id:
        print("FAIL - real Slice 38 frame/predicate link is not exact")
        return 1

    if invalid_predicate_frame_version_fields(
        predicate_id=predicate.predicate_id,
        predicate_version=predicate.predicate_version,
        frame_id=layout.frame_id,
        frame_version=layout.frame_version,
    ):
        print("FAIL - exact current registry pair was rejected")
        return 1

    if invalid_predicate_frame_version_fields(
        predicate_id="predicate:inspect:v1",
        predicate_version="v1.0.0",
        frame_id="predicate_frame:inspect_target:v1",
        frame_version="v1.0.0",
    ):
        print("FAIL - frozen Slice 40 v1.0.0 compatibility was not preserved")
        return 1

    if not invalid_predicate_frame_version_fields(
        predicate_id=predicate.predicate_id,
        predicate_version="v9.9.9",
        frame_id=layout.frame_id,
        frame_version=layout.frame_version,
    ):
        print("FAIL - arbitrary predicate version was admitted")
        return 1

    wrong_frames = tuple(
        item
        for item in all_admitted_frames()
        if item.linked_predicate_id != predicate.predicate_id
    )
    if not wrong_frames:
        print("FAIL - no distinct admitted frame available for mismatch test")
        return 1
    wrong_frame = wrong_frames[0]
    if not invalid_predicate_frame_version_fields(
        predicate_id=predicate.predicate_id,
        predicate_version=predicate.predicate_version,
        frame_id=wrong_frame.frame_id,
        frame_version=wrong_frame.version,
    ):
        print("FAIL - cross-predicate current frame pair was admitted")
        return 1

    core = importlib.import_module(
        "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime"
    )
    governed = importlib.import_module(
        "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime.governed_lifecycle"
    )
    bundle_helpers = runpy.run_path(
        str(
            repository
            / "scripts"
            / "test_aiweb_slice40b_deterministic_validation_identity_versioning_lifecycle.py"
        )
    )
    make_bundle = bundle_helpers["make_bundle"]

    specifications = (
        (
            "expectancy",
            core.VerbalCognitionGateFamily.EXPECTANCY,
            "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime.expectancy_gate",
            "test_aiweb_slice40c_expectancy_gate_runtime.py",
            _replace_expectancy,
            "evaluate_expectancy",
            "INDETERMINATE",
        ),
        (
            "congruity",
            core.VerbalCognitionGateFamily.CONGRUITY,
            "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime.congruity_gate",
            "test_aiweb_slice40d_congruity_gate_runtime.py",
            _replace_congruity,
            "evaluate_congruity",
            "INDETERMINATE",
        ),
        (
            "connectedness",
            core.VerbalCognitionGateFamily.CONNECTEDNESS,
            "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime.connectedness_gate",
            "test_aiweb_slice40e_connectedness_gate_runtime.py",
            _replace_connectedness,
            "evaluate_connectedness",
            "INDETERMINATE",
        ),
        (
            "recoverable_purpose",
            core.VerbalCognitionGateFamily.RECOVERABLE_PURPOSE,
            "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime.recoverable_purpose_gate",
            "test_aiweb_slice40f_recoverable_purpose_runtime.py",
            _replace_recoverable,
            "evaluate_recoverable_purpose",
            "INDETERMINATE",
        ),
    )

    validated_families = []
    for (
        name,
        family,
        module_name,
        helper_name,
        constructor,
        evaluator_name,
        expected_state_name,
    ) in specifications:
        module = importlib.import_module(module_name)
        helpers = runpy.run_path(str(repository / "scripts" / helper_name))
        bundle = make_bundle(core, governed, family)
        evaluation_input = constructor(module, helpers, bundle, pair)
        input_report = module.validate_evaluation_input(evaluation_input)
        if not input_report.ok:
            for issue in input_report.issues:
                print(
                    "FAIL - "
                    f"{name}.input.{issue.path}:{issue.code.value}:{issue.detail}"
                )
            return 1

        result = getattr(module, evaluator_name)(evaluation_input)
        result_report = module.validate_result(result)
        if not result_report.ok:
            for issue in result_report.issues:
                print(
                    "FAIL - "
                    f"{name}.result.{issue.path}:{issue.code.value}:{issue.detail}"
                )
            return 1

        if getattr(result.overall_state, "name", "") != expected_state_name:
            print(
                f"FAIL - {name} outcome {result.overall_state!r} "
                f"was not {expected_state_name}"
            )
            return 1

        if any(
            bool(getattr(result, field, False))
            for field in (
                "selected_meaning_created",
                "permission_granted",
                "execution_authorized",
                "route_created",
                "tool_invoked",
                "action_performed",
                "memory_accessed",
                "memory_written",
                "rendered",
                "delivered",
                "external_resource_loaded",
                "language_model_used",
            )
        ):
            print(f"FAIL - {name} created downstream authority")
            return 1

        validated_families.append(name)

    print("AI.WEB BRIDGE 5B SLICE 38-TO-40 VERSION CUSTODY TEST: PASS")
    print(f"real_predicate_id={predicate.predicate_id}")
    print(f"real_predicate_version={predicate.predicate_version}")
    print(f"real_frame_id={layout.frame_id}")
    print(f"real_frame_version={layout.frame_version}")
    print("exact_registry_version_custody=1")
    print("exact_frame_predicate_link=1")
    print("legacy_v1_0_0_compatibility_preserved=1")
    print("arbitrary_versions_rejected=1")
    print("cross_predicate_frame_pair_rejected=1")
    print(f"gate_family_inputs_valid={len(validated_families)}")
    print(f"gate_family_results_indeterminate={len(validated_families)}")
    print("gate_composition_executed=0")
    print("msm_gate_custody_created=0")
    print("selection_eligibility_evaluated=0")
    print("selected_meaning_created=0")
    print("tool_routing=0")
    print("action_execution=0")
    print("memory_writes=0")
    print("llm_calls=0")
    print("simulation_executed=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
