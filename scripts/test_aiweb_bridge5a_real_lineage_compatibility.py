#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import runpy
import sys
from dataclasses import replace
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    sys.path.insert(0, str(repository))

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
    from aiweb_language_core_bootstrap.candidate_meaning_construction.deterministic_constructor import (
        CandidateMeaningConstructorInput,
        construct_candidate_meanings,
    )
    from aiweb_language_core_bootstrap.candidate_meaning_construction.manifest_candidate_integration import (
        integrate_candidate_meanings_into_manifest,
    )

    source_text = "Please inspect concept admission."
    action_root = "inspect"
    frame_key = "inspect_read_only"

    custody = capture_input_event(
        source_text,
        source_id="aiweb.bridge5a.integration.test",
        channel_id="aiweb.bridge5a.integration.test",
        sequence_number=0,
    )
    projection = project_source_field(custody.event)
    binding = bind_resonant_operator_candidates(projection)
    trails = construct_candidate_resonant_phase_trails(projection, binding)
    constraints = apply_scope_attachment_reference_constraints(
        projection, binding, trails
    )
    structural = derive_deterministic_structural_analysis(
        custody, projection, binding, trails, constraints
    )
    slice37 = propose_structural_concept_candidates(
        custody, projection, structural
    )

    compatibility_rules = []
    for concept_index, concept in enumerate(slice37.concept_candidates):
        for sense_index, sense in enumerate(slice37.sense_candidates):
            if sense.concept_id != concept.concept_id:
                continue
            compatibility_rules.append(
                build_exact_compatibility_rule(
                    rule_key=(
                        f"aiweb.bridge5a.integration.{action_root}."
                        f"{concept_index}.{sense_index}"
                    ),
                    action_root_key=action_root,
                    concept_id=concept.concept_id,
                    sense_id=sense.sense_id,
                    allowed_frame_keys=(frame_key,),
                )
            )

    if not compatibility_rules:
        print("FAIL - real candidate chain produced no compatibility rules")
        return 1

    snapshot = build_compatibility_snapshot(
        rules=tuple(compatibility_rules),
        registry_key=f"aiweb.bridge5a.integration.{action_root}",
    )
    slice38 = propose_predicate_role_frame_candidates(
        slice37,
        compatibility_snapshot=snapshot,
    )
    constructor_input = CandidateMeaningConstructorInput(
        custody=custody,
        projection=projection,
        binding=binding,
        trails=trails,
        constraints=constraints,
        structural=structural,
        slice37=slice37,
        slice38=slice38,
    )
    constructor_result = construct_candidate_meanings((constructor_input,))
    integration_result = integrate_candidate_meanings_into_manifest(
        constructor_result
    )

    manifest = integration_result.manifest
    if manifest is None or not integration_result.companions:
        print("FAIL - real Slice 39G integration did not produce exact custody")
        return 1

    manifest_candidate = manifest.candidate_meanings[0]
    manifest_companion = integration_result.companions[0]

    # This is the exact live distinction that the correction preserves.
    if manifest_candidate.lineage_id == manifest_companion.candidate_lineage_id:
        print("FAIL - fixture did not preserve the two distinct lineage domains")
        return 1

    gate_core = importlib.import_module(
        "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime"
    )
    gate_governed = importlib.import_module(
        "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime.governed_lifecycle"
    )
    composition = importlib.import_module(
        "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime.gate_composition"
    )
    gate_custody = importlib.import_module(
        "aiweb_language_core_bootstrap.msm_gate_custody"
    )
    selected_core = importlib.import_module(
        "aiweb_language_core_bootstrap.selected_meaning_runtime"
    )
    selected_governed = importlib.import_module(
        "aiweb_language_core_bootstrap.selected_meaning_runtime.governed_lifecycle"
    )
    eligibility = importlib.import_module(
        "aiweb_language_core_bootstrap.selected_meaning_runtime.eligibility_evaluation"
    )

    gate_helpers = runpy.run_path(
        str(
            repository
            / "scripts"
            / "test_aiweb_slice40g_gate_composition_non_selection_disposition_runtime.py"
        )
    )
    eligibility_helpers = runpy.run_path(
        str(
            repository
            / "scripts"
            / "test_aiweb_slice41c_selection_eligibility_evaluation_runtime.py"
        )
    )

    bundles, family_results, _ = gate_helpers["build_family_results"](
        repository,
        gate_core,
        gate_governed,
    )
    candidate_input_ref = manifest_companion.candidate_meaning_id
    candidate_branch_ref = (
        "candidate_branch:"
        + manifest_companion.candidate_meaning_id.rsplit(":", 1)[-1][:20]
    )
    result_refs = tuple(item.result_id for item in family_results)
    assertion = gate_helpers["make_assertion"](
        composition,
        candidate_input_ref,
        candidate_branch_ref,
        result_refs,
        composition.GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED,
    )
    composition_input = gate_helpers["make_input"](
        composition,
        bundles,
        family_results,
        (assertion,),
        material_competing_candidate_refs=("candidate_state:unresolved",),
    )
    composition_input = replace(
        composition_input,
        candidate_input_ref=candidate_input_ref,
        candidate_branch_ref=candidate_branch_ref,
        candidate_branch_refs=(candidate_branch_ref,),
    )
    composition_input = composition.with_expected_evaluation_input_id(
        composition_input
    )
    composition_result = composition.evaluate_gate_composition(
        composition_input
    )

    gate_integration = gate_custody.integrate_gate_results_into_manifest(
        manifest,
        manifest_candidate.record_id,
        *family_results,
        composition_result,
    )

    governance_bundle = eligibility_helpers["_governance_bundle"](
        selected_core,
        selected_governed,
        eligibility,
        gate_custody,
        manifest_candidate,
        manifest_companion,
        gate_integration.companion,
        composition_result,
        "materially_unresolved",
    )
    evaluation_input = eligibility_helpers["_evaluation_input"](
        eligibility,
        governance_bundle,
        manifest_candidate,
        manifest_companion,
        gate_integration.companion,
        composition_result,
        "materially_unresolved",
    )

    report = eligibility.validate_evaluation_input(evaluation_input)
    if not report.ok:
        for issue in report.issues:
            print(
                "FAIL - "
                f"{issue.path}:{issue.code.value}:{issue.detail}"
            )
        return 1

    result = eligibility.evaluate_selection_eligibility(evaluation_input)
    if (
        result.outcome
        is not eligibility.SelectionEligibilityOutcome.MATERIALLY_UNRESOLVED
    ):
        print(f"FAIL - unexpected eligibility outcome: {result.outcome}")
        return 1

    if any(
        (
            result.candidate_ranked,
            result.selection_performed,
            result.selected_meaning_created,
            result.msm_v1_modified,
            result.truth_determined,
            result.evidence_validated,
            result.permission_granted,
            result.execution_authorized,
            result.route_created,
            result.tool_invoked,
            result.action_performed,
            result.memory_accessed,
            result.memory_written,
            result.rendered,
            result.delivered,
            result.external_resource_loaded,
            result.language_model_used,
            result.hidden_classifier_used,
        )
    ):
        print("FAIL - downstream authority was created")
        return 1

    print("AI.WEB BRIDGE 5A REAL 39G-TO-41C LINEAGE COMPATIBILITY TEST: PASS")
    print("real_slice39g_candidate_record=1")
    print("real_slice39g_candidate_companion=1")
    print("manifest_lineage_domain_preserved=1")
    print("source_candidate_lineage_domain_preserved=1")
    print("lineage_domains_conflated=0")
    print("exact_record_companion_link=1")
    print("slice40h_gate_custody=1")
    print("slice41c_evaluation_input_valid=1")
    print("slice41c_outcome=materially_unresolved")
    print("selected_meaning_created=0")
    print("tool_routing=0")
    print("action_execution=0")
    print("memory_writes=0")
    print("llm_calls=0")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
