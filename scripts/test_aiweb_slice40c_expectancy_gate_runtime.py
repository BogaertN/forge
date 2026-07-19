#!/usr/bin/env python3
"""Behavior test for AI.Web Slice 40C expectancy-gate runtime."""

from __future__ import annotations

import argparse
from dataclasses import FrozenInstanceError, replace
import importlib
from pathlib import Path
import runpy
import sys


CORE_PACKAGE = "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime"
GOV_PACKAGE = f"{CORE_PACKAGE}.governed_lifecycle"
PACKAGE = f"{CORE_PACKAGE}.expectancy_gate"


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.failures: list[str] = []
        self.malformed_cases = 0

    def check(self, condition: object, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)

    def malformed(self, condition: object, label: str) -> None:
        self.malformed_cases += 1
        self.check(condition, label)


def make_profile(core, module, bundle):
    return module.with_expected_profile_id(
        module.ExpectancyGateRuntimeProfile(
            profile_id="expectancy_profile:placeholder",
            profile_key="expectancy_exact_admitted_frame_requirements",
            profile_version="v1.0.0",
            gate_profile_ref=bundle.review_record.profile.profile_id,
            gate_profile_version=bundle.review_record.profile.profile_version,
            governing_authority_refs=(
                "canonical_roadmap:slice40c",
                "document6:expectancy_gate:v1",
            ),
            permitted_requirement_kinds=tuple(module.ExpectancyRequirementKind),
            exact_admitted_requirements_only=True,
            raw_text_inspection_allowed=False,
            hidden_context_allowed=False,
            default_participant_inference_allowed=False,
            unstated_referent_inference_allowed=False,
            automatic_clarification_allowed=False,
            gate_composition_allowed=False,
            selected_meaning_allowed=False,
            route_tool_action_allowed=False,
        )
    )


def make_requirement(module, bundle, kind, key, *, required=True, minimum_count=1):
    return module.with_expected_requirement_id(
        module.ExpectancyRequirement(
            requirement_id="expectancy_requirement:placeholder",
            candidate_input_ref=bundle.review_record.candidate_input.candidate_input_ref_id,
            predicate_id="predicate:inspect:v1",
            predicate_version="v1.0.0",
            frame_id="predicate_frame:inspect_target:v1",
            frame_version="v1.0.0",
            requirement_key=key,
            requirement_kind=kind,
            requirement_source_refs=(
                "slice38e:predicate_frame:inspect_target:v1",
                f"slice40c:requirement:{key}",
            ),
            authority_refs=(
                "document5:predicate_role_frame_registry:v1",
                "document6:expectancy_gate:v1",
            ),
            subject_record_refs=(f"candidate_subject:{key}",),
            relation_refs=(f"candidate_relation:{key}",),
            minimum_count=minimum_count,
            required=required,
            exact_admitted_requirement=True,
        )
    )


def make_observation(module, bundle, requirement, *, state=None, count=1):
    authority_state = state or module.ExpectancyAuthorityState.ADMITTED
    records = tuple(
        f"observed_record:{requirement.requirement_key}:{index}"
        for index in range(count)
    ) if authority_state is module.ExpectancyAuthorityState.ADMITTED else ()
    return module.with_expected_observation_id(
        module.ExpectancyObservation(
            observation_id="expectancy_observation:placeholder",
            requirement_ref=requirement.requirement_id,
            candidate_input_ref=bundle.review_record.candidate_input.candidate_input_ref_id,
            authority_state=authority_state,
            observed_record_refs=records,
            observed_relation_refs=(),
            trace_refs=(f"expectancy_trace:{requirement.requirement_key}",),
            provenance_refs=(f"expectancy_provenance:{requirement.requirement_key}",),
        )
    )


def make_input(module, bundle, requirements, observations):
    return module.with_expected_evaluation_input_id(
        module.ExpectancyEvaluationInput(
            evaluation_input_id="expectancy_evaluation_input:placeholder",
            governance_bundle=bundle,
            runtime_profile=make_profile(None, module, bundle),
            candidate_input_ref=bundle.review_record.candidate_input.candidate_input_ref_id,
            predicate_id="predicate:inspect:v1",
            predicate_version="v1.0.0",
            frame_id="predicate_frame:inspect_target:v1",
            frame_version="v1.0.0",
            requirements=tuple(requirements),
            observations=tuple(observations),
            trace_refs=("slice39h:candidate_trace", "slice40b:sealed_governance_trace"),
            provenance_refs=("slice39h:candidate_provenance", "slice40b:governance_provenance"),
            limitation_refs=("slice40c:no_clarification_no_selection",),
            raw_text_supplied=False,
            hidden_context_used=False,
            defaults_used=False,
            inferred_participants_created=False,
            inferred_referents_created=False,
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    sys.path.insert(0, str(repository))

    core = importlib.import_module(CORE_PACKAGE)
    gov = importlib.import_module(GOV_PACKAGE)
    module = importlib.import_module(PACKAGE)
    fixture_namespace = runpy.run_path(
        str(repository / "scripts/test_aiweb_slice40b_deterministic_validation_identity_versioning_lifecycle.py")
    )
    make_bundle = fixture_namespace["make_bundle"]
    ledger = Ledger()

    bundle = make_bundle(core, gov, core.VerbalCognitionGateFamily.EXPECTANCY)
    kinds = (
        module.ExpectancyRequirementKind.REQUIRED_ROLE,
        module.ExpectancyRequirementKind.REQUIRED_RELATION,
        module.ExpectancyRequirementKind.REQUIRED_COMPLEMENT,
        module.ExpectancyRequirementKind.REQUIRED_PURPOSE_INFORMATION,
    )
    requirements = tuple(
        make_requirement(module, bundle, kind, kind.value)
        for kind in kinds
    ) + (
        make_requirement(
            module,
            bundle,
            module.ExpectancyRequirementKind.OPTIONAL_DETAIL,
            "optional_detail",
            required=False,
        ),
    )
    observations = tuple(
        make_observation(module, bundle, item, count=1 if item.required else 0)
        for item in requirements
    )
    valid_input = make_input(module, bundle, requirements, observations)
    original_input = valid_input
    result = module.evaluate_expectancy(valid_input)

    ledger.check(module.SLICE40C_ACCEPTED_PARENT_HEAD == "5ad63716f4da2833a23758d083671a7ee92ae22a", "accepted parent head")
    ledger.check(module.SLICE40C_ACCEPTED_PARENT_TREE == "77ac09bc0c10460918537094ddd1eef106ca5287", "accepted parent tree")
    ledger.check(module.validate_evaluation_input(valid_input).ok, "valid input")
    ledger.check(module.validate_result(result).ok, "valid result")
    ledger.check(valid_input == original_input, "candidate input not mutated")
    ledger.check(result.overall_state is module.ExpectancyOverallState.STRUCTURALLY_COMPLETE, "structurally complete")
    ledger.check(result.requirement_count == 5, "five requirements")
    ledger.check(result.required_requirement_count == 4, "four required")
    ledger.check(result.satisfied_required_count == 4, "four required satisfied")
    ledger.check(result.missing_required_count == 0, "no required missing")
    ledger.check(result.optional_omitted_count == 1, "optional omitted preserved")
    ledger.check(result.indeterminate_count == 0, "no indeterminate")
    finding_kinds = tuple(item.finding_kind for item in result.findings)
    ledger.check(module.ExpectancyFindingKind.OPTIONAL_DETAIL_OMITTED in finding_kinds, "optional omission finding")
    ledger.check(module.ExpectancyFindingKind.STRUCTURALLY_COMPLETE in finding_kinds, "complete finding")
    ledger.check(result == module.evaluate_expectancy(valid_input), "deterministic repeat")
    for _ in range(20):
        ledger.check(module.evaluate_expectancy(valid_input) == result, "repeat determinism")

    missing_map = {
        module.ExpectancyRequirementKind.REQUIRED_ROLE: module.ExpectancyFindingKind.REQUIRED_ROLE_MISSING,
        module.ExpectancyRequirementKind.REQUIRED_RELATION: module.ExpectancyFindingKind.REQUIRED_RELATION_MISSING,
        module.ExpectancyRequirementKind.REQUIRED_COMPLEMENT: module.ExpectancyFindingKind.REQUIRED_COMPLEMENT_MISSING,
        module.ExpectancyRequirementKind.REQUIRED_PURPOSE_INFORMATION: module.ExpectancyFindingKind.REQUIRED_PURPOSE_INFORMATION_MISSING,
    }
    for index, requirement in enumerate(requirements[:4]):
        altered = list(observations)
        altered[index] = make_observation(module, bundle, requirement, count=0)
        item_input = make_input(module, bundle, requirements, altered)
        item_result = module.evaluate_expectancy(item_input)
        ledger.check(item_result.overall_state is module.ExpectancyOverallState.INCOMPLETE, f"{requirement.requirement_kind.value} incomplete")
        ledger.check(item_result.missing_required_count == 1, f"{requirement.requirement_kind.value} missing count")
        ledger.check(missing_map[requirement.requirement_kind] in tuple(f.finding_kind for f in item_result.findings), f"{requirement.requirement_kind.value} exact finding")
        ledger.check(not item_result.clarification_required_created, f"{requirement.requirement_kind.value} no automatic clarification")

    for state in (
        module.ExpectancyAuthorityState.ABSENT,
        module.ExpectancyAuthorityState.UNSUPPORTED,
        module.ExpectancyAuthorityState.CONFLICTED,
    ):
        altered = list(observations)
        altered[0] = make_observation(module, bundle, requirements[0], state=state, count=0)
        item_result = module.evaluate_expectancy(make_input(module, bundle, requirements, altered))
        ledger.check(item_result.overall_state is module.ExpectancyOverallState.INDETERMINATE, f"{state.value} indeterminate")
        ledger.check(item_result.indeterminate_count == 1, f"{state.value} count")
        ledger.check(module.ExpectancyFindingKind.INDETERMINATE_REQUIRED_AUTHORITY_ABSENT in tuple(f.finding_kind for f in item_result.findings), f"{state.value} finding")

    boundary_false = (
        "candidate_structure_mutated", "missing_role_filled", "referent_invented",
        "unstated_participant_inferred", "clarification_required_created", "rejection_created",
        "refusal_relevant_created", "blocked_progression_created", "composed_gate_outcome_created",
        "candidate_disposition_created", "selected_meaning_created", "truth_determined",
        "evidence_validated", "permission_granted", "execution_authorized", "route_created",
        "tool_invoked", "action_performed", "memory_accessed", "rendered", "delivered",
        "external_resource_loaded", "language_model_used", "embedding_used", "vector_used",
        "rag_used", "semantic_similarity_used",
    )
    for name in boundary_false:
        ledger.check(getattr(result, name) is False, f"boundary false {name}")

    # Frozen records.
    for record, field_name in (
        (valid_input.runtime_profile, "profile_key"),
        (requirements[0], "requirement_key"),
        (observations[0], "requirement_ref"),
        (valid_input, "predicate_id"),
        (result, "predicate_id"),
    ):
        try:
            setattr(record, field_name, "mutated")
            frozen = False
        except (FrozenInstanceError, AttributeError):
            frozen = True
        ledger.check(frozen, f"frozen {type(record).__name__}")

    malformed = []
    malformed.append(replace(valid_input, raw_text_supplied=True))
    malformed.append(replace(valid_input, hidden_context_used=True))
    malformed.append(replace(valid_input, defaults_used=True))
    malformed.append(replace(valid_input, inferred_participants_created=True))
    malformed.append(replace(valid_input, inferred_referents_created=True))
    malformed.append(replace(valid_input, predicate_version="v2.0.0"))
    malformed.append(replace(valid_input, frame_version="v2.0.0"))
    malformed.append(replace(valid_input, requirements=()))
    malformed.append(replace(valid_input, observations=valid_input.observations[:-1]))
    malformed.append(replace(valid_input, observations=valid_input.observations + (valid_input.observations[0],)))
    malformed.append(replace(valid_input, candidate_input_ref="candidate_input:wrong"))
    malformed.append(replace(valid_input, evaluation_input_id="expectancy_evaluation_input:wrong"))
    malformed.append(replace(valid_input, runtime_profile=replace(valid_input.runtime_profile, automatic_clarification_allowed=True)))
    malformed.append(replace(valid_input, runtime_profile=replace(valid_input.runtime_profile, gate_composition_allowed=True)))
    malformed.append(replace(valid_input, runtime_profile=replace(valid_input.runtime_profile, selected_meaning_allowed=True)))
    malformed.append(replace(valid_input, runtime_profile=replace(valid_input.runtime_profile, route_tool_action_allowed=True)))
    malformed.append(replace(valid_input, runtime_profile=replace(valid_input.runtime_profile, raw_text_inspection_allowed=True)))
    malformed.append(replace(valid_input, runtime_profile=replace(valid_input.runtime_profile, hidden_context_allowed=True)))
    malformed.append(replace(valid_input, requirements=(replace(requirements[0], exact_admitted_requirement=False),) + requirements[1:]))
    malformed.append(replace(valid_input, requirements=(replace(requirements[0], minimum_count=0),) + requirements[1:]))
    malformed.append(replace(valid_input, requirements=(replace(requirements[0], required=False),) + requirements[1:]))
    malformed.append(replace(valid_input, requirements=(replace(requirements[-1], required=True),) + requirements[:-1]))
    malformed.append(replace(valid_input, observations=(replace(observations[0], authority_state=module.ExpectancyAuthorityState.ABSENT),) + observations[1:]))

    other_bundle = make_bundle(core, gov, core.VerbalCognitionGateFamily.CONGRUITY)
    malformed.append(replace(valid_input, governance_bundle=other_bundle))
    unsealed = replace(bundle, lifecycle_records=bundle.lifecycle_records[:-1])
    malformed.append(replace(valid_input, governance_bundle=unsealed))

    for index, bad in enumerate(malformed):
        report = module.validate_evaluation_input(bad)
        ledger.malformed(not report.ok, f"malformed input {index} rejected")
        try:
            module.evaluate_expectancy(bad)
            rejected = False
        except module.ExpectancyValidationError:
            rejected = True
        ledger.malformed(rejected, f"malformed input {index} evaluator fail closed")

    bad_results = (
        replace(result, selected_meaning_created=True),
        replace(result, clarification_required_created=True),
        replace(result, missing_role_filled=True),
        replace(result, result_id="expectancy_result:wrong"),
        replace(result, canonical_digest="f" * 64),
        replace(result, language_model_used=True),
    )
    for index, bad in enumerate(bad_results):
        ledger.malformed(not module.validate_result(bad).ok, f"malformed result {index} rejected")

    print("AI.WEB SLICE 40C EXPECTANCY GATE BEHAVIOR TEST")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print(f"requirement_kinds={len(tuple(module.ExpectancyRequirementKind))}")
    print(f"finding_kinds={len(tuple(module.ExpectancyFindingKind))}")
    print(f"overall_states={len(tuple(module.ExpectancyOverallState))}")
    print("required_role_missing=1")
    print("required_relation_missing=1")
    print("required_complement_missing=1")
    print("required_purpose_information_missing=1")
    print("optional_detail_omitted=1")
    print("structurally_complete_for_gate=1")
    print("indeterminate_required_authority_absent=1")
    print("candidate_structure_mutated=0")
    print("missing_role_filled=0")
    print("referent_invented=0")
    print("unstated_participant_inferred=0")
    print("clarification_required_created=0")
    print("composed_gate_outcome_created=0")
    print("candidate_disposition_created=0")
    print("selected_meaning_created=0")
    print("truth_evidence_permission_execution=0")
    print("route_tool_action_memory_rendering_delivery=0")
    print(f"failure_count={len(ledger.failures)}")
    if ledger.failures:
        for failure in ledger.failures:
            print(f"FAILURE={failure}")
        print("AI.WEB SLICE 40C EXPECTANCY GATE BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 40C EXPECTANCY GATE BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
