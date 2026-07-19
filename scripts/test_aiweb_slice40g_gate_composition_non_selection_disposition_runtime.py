#!/usr/bin/env python3
"""Behavior test for AI.Web Slice 40G gate composition runtime."""
from __future__ import annotations

import argparse
from dataclasses import FrozenInstanceError, fields, replace
import importlib
from pathlib import Path
import runpy
import sys

CORE_PACKAGE = "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime"
GOV_PACKAGE = f"{CORE_PACKAGE}.governed_lifecycle"
PACKAGE = f"{CORE_PACKAGE}.gate_composition"


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


def _namespace(repository: Path, name: str):
    return runpy.run_path(str(repository / "scripts" / name))


def build_family_results(repository, core, governed):
    make_bundle = _namespace(
        repository,
        "test_aiweb_slice40b_deterministic_validation_identity_versioning_lifecycle.py",
    )["make_bundle"]

    expectancy = importlib.import_module(f"{CORE_PACKAGE}.expectancy_gate")
    e_ns = _namespace(repository, "test_aiweb_slice40c_expectancy_gate_runtime.py")
    e_bundle = make_bundle(core, governed, core.VerbalCognitionGateFamily.EXPECTANCY)
    e_kinds = (
        expectancy.ExpectancyRequirementKind.REQUIRED_ROLE,
        expectancy.ExpectancyRequirementKind.REQUIRED_RELATION,
        expectancy.ExpectancyRequirementKind.REQUIRED_COMPLEMENT,
        expectancy.ExpectancyRequirementKind.REQUIRED_PURPOSE_INFORMATION,
    )
    e_requirements = tuple(
        e_ns["make_requirement"](expectancy, e_bundle, kind, kind.value)
        for kind in e_kinds
    ) + (
        e_ns["make_requirement"](
            expectancy,
            e_bundle,
            expectancy.ExpectancyRequirementKind.OPTIONAL_DETAIL,
            "optional_detail",
            required=False,
        ),
    )
    e_observations = tuple(
        e_ns["make_observation"](
            expectancy,
            e_bundle,
            item,
            count=1 if item.required else 0,
        )
        for item in e_requirements
    )
    e_input = e_ns["make_input"](
        expectancy, e_bundle, e_requirements, e_observations
    )
    e_result = expectancy.evaluate_expectancy(e_input)

    congruity = importlib.import_module(f"{CORE_PACKAGE}.congruity_gate")
    c_ns = _namespace(repository, "test_aiweb_slice40d_congruity_gate_runtime.py")
    c_bundle = make_bundle(core, governed, core.VerbalCognitionGateFamily.CONGRUITY)
    c_assertions = tuple(
        c_ns["make_assertion"](congruity, c_bundle, kind, kind.value)
        for kind in congruity.CongruityAssertionKind
    )
    c_observations = tuple(
        c_ns["make_observation"](congruity, c_bundle, item)
        for item in c_assertions
    )
    c_input = c_ns["make_input"](
        congruity, c_bundle, c_assertions, c_observations
    )
    c_result = congruity.evaluate_congruity(c_input)

    connectedness = importlib.import_module(f"{CORE_PACKAGE}.connectedness_gate")
    n_ns = _namespace(repository, "test_aiweb_slice40e_connectedness_gate_runtime.py")
    n_bundle = make_bundle(core, governed, core.VerbalCognitionGateFamily.CONNECTEDNESS)
    n_assertions = tuple(
        n_ns["make_assertion"](connectedness, n_bundle, kind, kind.value)
        for kind in connectedness.ConnectednessAssertionKind
    )
    n_observations = tuple(
        n_ns["make_observation"](connectedness, n_bundle, item)
        for item in n_assertions
    )
    n_input = n_ns["make_input"](
        connectedness, n_bundle, n_assertions, n_observations
    )
    n_result = connectedness.evaluate_connectedness(n_input)

    purpose = importlib.import_module(f"{CORE_PACKAGE}.recoverable_purpose_gate")
    p_ns = _namespace(repository, "test_aiweb_slice40f_recoverable_purpose_runtime.py")
    p_bundle = make_bundle(
        core, governed, core.VerbalCognitionGateFamily.RECOVERABLE_PURPOSE
    )
    p_assertions = tuple(
        p_ns["make_assertion"](
            purpose,
            p_bundle,
            kind,
            *purpose.PURPORT_DISTINCTION_PAIRS[kind],
        )
        for kind in purpose.PurportDistinctionKind
    )
    p_observations = tuple(
        p_ns["make_observation"](purpose, p_bundle, item)
        for item in p_assertions
    )
    p_input = p_ns["make_input"](
        purpose, p_bundle, p_assertions, p_observations
    )
    p_result = purpose.evaluate_recoverable_purpose(p_input)

    return (
        (e_bundle, c_bundle, n_bundle, p_bundle),
        (e_result, c_result, n_result, p_result),
        {
            "expectancy": (expectancy, e_ns, e_bundle, e_requirements, e_observations),
            "congruity": (congruity, c_ns, c_bundle, c_assertions, c_observations),
            "connectedness": (connectedness, n_ns, n_bundle, n_assertions, n_observations),
            "purpose": (purpose, p_ns, p_bundle, p_assertions, p_observations),
        },
    )


def make_profile(module):
    return module.with_expected_profile_id(
        module.GateCompositionRuntimeProfile(
            profile_id="gate_composition_profile:placeholder",
            profile_key="candidate_specific_preservation_composition",
            profile_version="v1.0.0",
            governing_authority_refs=(
                "canonical_roadmap:slice40g",
                "document6:section33:gate_composition",
                "document6:section31:non_selection",
                "slice40a:positive_selection_review_name_boundary",
            ),
            permitted_disposition_kinds=tuple(
                module.GateCompositionDispositionKind
            ),
            exact_family_results_required=True,
            preserve_all_gate_results=True,
            candidate_specific_composition_required=True,
            gate_substitution_allowed=False,
            gate_outcome_erasure_allowed=False,
            generic_flattening_allowed=False,
            global_pass_generalization_allowed=False,
            global_failure_generalization_allowed=False,
            candidate_branch_erasure_allowed=False,
            effect_boundary_rewrite_allowed=False,
            domain_marker_erasure_allowed=False,
            no_action_boundary_conversion_allowed=False,
            automatic_ambiguity_allowed=False,
            automatic_clarification_allowed=False,
            automatic_refusal_allowed=False,
            safest_candidate_selection_allowed=False,
            selected_meaning_allowed=False,
            downstream_authority_allowed=False,
        )
    )


def make_assertion(module, candidate_ref, branch_ref, result_refs, kind, *, authority=None, judgment=None):
    authority = authority or module.GateCompositionAuthorityState.ADMITTED
    judgment = judgment or (
        module.GateCompositionJudgment.APPLIES
        if authority is module.GateCompositionAuthorityState.ADMITTED
        else module.GateCompositionJudgment.NOT_EVALUATED
    )
    bases = {
        "ambiguity_refs": (),
        "clarification_refs": (),
        "unsupported_refs": (),
        "refusal_relevance_refs": (),
        "hold_refs": (),
        "blocked_progression_refs": (),
        "later_selection_review_refs": (),
    }
    field_map = {
        module.GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED: "ambiguity_refs",
        module.GateCompositionDispositionKind.CLARIFICATION_RELEVANT: "clarification_refs",
        module.GateCompositionDispositionKind.UNSUPPORTED: "unsupported_refs",
        module.GateCompositionDispositionKind.REFUSAL_RELEVANT: "refusal_relevance_refs",
        module.GateCompositionDispositionKind.HELD: "hold_refs",
        module.GateCompositionDispositionKind.BLOCKED_PROGRESSION: "blocked_progression_refs",
        module.GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW: "later_selection_review_refs",
    }
    if judgment is module.GateCompositionJudgment.APPLIES:
        bases[field_map[kind]] = (f"disposition_basis:{kind.value}",)
    if authority is module.GateCompositionAuthorityState.UNSUPPORTED:
        bases["unsupported_refs"] = ("unsupported_authority:composition",)
        kind = module.GateCompositionDispositionKind.UNSUPPORTED
    return module.with_expected_assertion_id(
        module.GateCompositionDispositionAssertion(
            assertion_id="gate_composition_assertion:placeholder",
            candidate_input_ref=candidate_ref,
            candidate_branch_ref=branch_ref,
            disposition_kind=kind,
            authority_state=authority,
            judgment=judgment,
            gate_result_refs=tuple(result_refs),
            supporting_refs=(f"composition_support:{kind.value}",),
            missing_authority_refs=(
                ("missing_authority:composition",)
                if authority is module.GateCompositionAuthorityState.ABSENT
                else ()
            ),
            conflicting_refs=(
                ("conflicting_authority:composition",)
                if authority in (
                    module.GateCompositionAuthorityState.AMBIGUOUS,
                    module.GateCompositionAuthorityState.CONFLICTED,
                )
                else ()
            ),
            ambiguity_refs=bases["ambiguity_refs"],
            clarification_refs=bases["clarification_refs"],
            unsupported_refs=bases["unsupported_refs"],
            refusal_relevance_refs=bases["refusal_relevance_refs"],
            hold_refs=bases["hold_refs"],
            blocked_progression_refs=bases["blocked_progression_refs"],
            later_selection_review_refs=bases["later_selection_review_refs"],
            later_authority_dependency_refs=(
                "later_authority:document7_or_10",
            ) if kind in (
                module.GateCompositionDispositionKind.HELD,
                module.GateCompositionDispositionKind.BLOCKED_PROGRESSION,
            ) else (),
            effect_boundary_refs=("effect_boundary:no_action",),
            domain_marker_refs=("domain_marker:software_sensitive",),
            no_action_boundary_refs=("boundary:no_action",),
            trace_refs=(f"composition_trace:{kind.value}",),
            provenance_refs=(f"composition_provenance:{kind.value}",),
            candidate_specific=True,
        )
    )


def make_input(module, bundles, results, assertions, **changes):
    candidate_ref = "candidate_composition:demo:v1"
    branch_ref = "candidate_branch:demo:primary"
    value = module.GateCompositionEvaluationInput(
        evaluation_input_id="gate_composition_evaluation_input:placeholder",
        governance_bundles=tuple(bundles),
        runtime_profile=make_profile(module),
        candidate_input_ref=candidate_ref,
        candidate_branch_ref=branch_ref,
        candidate_version="v1.0.0",
        expectancy_result=results[0],
        congruity_result=results[1],
        connectedness_result=results[2],
        recoverable_purpose_result=results[3],
        disposition_assertions=tuple(assertions),
        family_candidate_input_refs=tuple(item.candidate_input_ref for item in results),
        candidate_branch_refs=(branch_ref,),
        material_competing_candidate_refs=(),
        competing_candidate_disposition_refs=(),
        user_suppliable_clarification_refs=(),
        effect_boundary_refs=("effect_boundary:no_action",),
        domain_marker_refs=("domain_marker:software_sensitive",),
        no_action_boundary_refs=("boundary:no_action",),
        authority_boundary_refs=(
            "authority_boundary:meaning_not_action",
            "authority_boundary:gate_supported_not_selected",
        ),
        later_authority_dependency_refs=("later_authority:slice41_selected_meaning",),
        version_refs=(
            "version:expectancy:v1",
            "version:congruity:v1",
            "version:connectedness:v1",
            "version:recoverable_purpose:v1",
            "version:composition:v1",
        ),
        candidate_ancestry_refs=(
            "slice39:candidate_ancestry",
            "slice40c_to_40f:family_result_ancestry",
        ),
        trace_refs=("slice40g:composition_trace",),
        provenance_refs=("slice40g:composition_provenance",),
        limitation_refs=(
            "slice40g:non_selection_only",
            "slice40g:no_downstream_authority",
        ),
        raw_text_used_as_selected_meaning=False,
        gate_substitution_used=False,
        gate_outcome_erased=False,
        generic_flattening_used=False,
        global_pass_generalized=False,
        global_failure_generalized=False,
        candidate_branch_erased=False,
        effect_boundary_rewritten=False,
        domain_marker_erased=False,
        no_action_boundary_converted=False,
        automatic_ambiguity_used=False,
        automatic_clarification_used=False,
        automatic_refusal_used=False,
        safest_candidate_selected=False,
        candidate_structure_mutated=False,
    )
    if changes:
        value = replace(value, **changes)
    return module.with_expected_evaluation_input_id(value)


def _invalid(value, validator) -> bool:
    try:
        return not validator(value).ok
    except Exception:
        return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    sys.path.insert(0, str(repository))

    core = importlib.import_module(CORE_PACKAGE)
    governed = importlib.import_module(GOV_PACKAGE)
    module = importlib.import_module(PACKAGE)
    ledger = Ledger()

    bundles, results, family = build_family_results(repository, core, governed)
    candidate_ref = "candidate_composition:demo:v1"
    branch_ref = "candidate_branch:demo:primary"
    result_refs = tuple(item.result_id for item in results)
    positive_assertion = make_assertion(
        module,
        candidate_ref,
        branch_ref,
        result_refs,
        module.GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW,
    )
    valid_input = make_input(module, bundles, results, (positive_assertion,))
    original_input = valid_input
    result = module.evaluate_gate_composition(valid_input)

    ledger.check(module.SLICE40G_ACCEPTED_PARENT_HEAD == "8dd471f4e20024a3b64e5eb9ffac39815090fb39", "accepted parent head")
    ledger.check(module.SLICE40G_ACCEPTED_PARENT_TREE == "1d8b5ac529f6af78e17d69c264aabc4471481909", "accepted parent tree")
    ledger.check(module.SLICE40G_ACCEPTED_PARENT_SUBJECT == "Slice 40F deterministic intended-purport recoverable-purpose runtime", "accepted parent subject")
    ledger.check(module.validate_profile(valid_input.runtime_profile).ok, "valid profile")
    ledger.check(module.validate_evaluation_input(valid_input).ok, "valid composition input")
    ledger.check(module.validate_result(result).ok, "valid composition result")
    ledger.check(valid_input == original_input, "input not mutated")
    ledger.check(result.composition_status is module.GateCompositionStatus.COMPOSED, "composition complete")
    ledger.check(result.family_results_preserved and result.family_result_count == 4, "all family results preserved")
    ledger.check(result.later_selection_review_count == 1, "positive review disposition")
    ledger.check(result.positive_selection_review_disposition_created, "positive flag")
    ledger.check(not result.selected_meaning_created, "positive disposition not selected meaning")
    ledger.check(not result.candidate_accepted, "positive disposition not acceptance")
    ledger.check(result.result_id.endswith(result.canonical_digest), "result identity digest")
    ledger.check(module.evaluate_gate_composition(valid_input) == result, "deterministic repeat")
    for _ in range(20):
        ledger.check(module.evaluate_gate_composition(valid_input) == result, "repeat determinism")

    ledger.check(result.expectancy_result_id == results[0].result_id and result.expectancy_result_digest == results[0].canonical_digest, "expectancy preserved")
    ledger.check(result.congruity_result_id == results[1].result_id and result.congruity_result_digest == results[1].canonical_digest, "congruity preserved")
    ledger.check(result.connectedness_result_id == results[2].result_id and result.connectedness_result_digest == results[2].canonical_digest, "connectedness preserved")
    ledger.check(result.recoverable_purpose_result_id == results[3].result_id and result.recoverable_purpose_result_digest == results[3].canonical_digest, "purpose preserved")
    ledger.check(tuple(module.GateCompositionDispositionKind) == (
        module.GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED,
        module.GateCompositionDispositionKind.CLARIFICATION_RELEVANT,
        module.GateCompositionDispositionKind.UNSUPPORTED,
        module.GateCompositionDispositionKind.REFUSAL_RELEVANT,
        module.GateCompositionDispositionKind.HELD,
        module.GateCompositionDispositionKind.BLOCKED_PROGRESSION,
        module.GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW,
    ), "exact seven dispositions")

    disposition_results = {}
    for kind in module.GateCompositionDispositionKind:
        assertion = make_assertion(module, candidate_ref, branch_ref, result_refs, kind)
        changes = {}
        if kind is module.GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED:
            changes["material_competing_candidate_refs"] = ("candidate_branch:demo:alternative",)
        if kind is module.GateCompositionDispositionKind.CLARIFICATION_RELEVANT:
            changes["user_suppliable_clarification_refs"] = ("clarification_support:user_can_supply_referent",)
        item_input = make_input(module, bundles, results, (assertion,), **changes)
        item_result = module.evaluate_gate_composition(item_input)
        disposition_results[kind] = item_result
        ledger.check(len(item_result.dispositions) == 1, f"one disposition {kind.value}")
        ledger.check(item_result.dispositions[0].disposition_kind is kind, f"exact disposition {kind.value}")
        ledger.check(item_result.dispositions[0].non_selection_only, f"non-selection only {kind.value}")
        ledger.check(not item_result.selected_meaning_created, f"no selection {kind.value}")

    all_assertions = tuple(
        make_assertion(module, candidate_ref, branch_ref, result_refs, kind)
        for kind in module.GateCompositionDispositionKind
    )
    all_input = make_input(
        module,
        bundles,
        results,
        all_assertions,
        material_competing_candidate_refs=("candidate_branch:demo:alternative",),
        competing_candidate_disposition_refs=("alternative_disposition:held",),
        user_suppliable_clarification_refs=("clarification_support:user_can_supply_referent",),
    )
    all_result = module.evaluate_gate_composition(all_input)
    ledger.check(len(all_result.dispositions) == 7, "all seven dispositions preserved")
    ledger.check(all_result.material_ambiguity_preserved, "material ambiguity preserved")
    ledger.check(all_result.clarification_relevant_created, "clarification relevant")
    ledger.check(all_result.unsupported_disposition_created, "unsupported disposition")
    ledger.check(all_result.refusal_relevant_disposition_created, "refusal relevant")
    ledger.check(all_result.held_disposition_created, "held disposition")
    ledger.check(all_result.blocked_progression_created, "blocked progression")
    ledger.check(all_result.positive_selection_review_disposition_created, "positive review disposition preserved")
    ledger.check(not all_result.candidate_rejected and not all_result.candidate_clarified, "dispositions do not perform rejection or clarification")

    held_assertion = make_assertion(module, candidate_ref, branch_ref, result_refs, module.GateCompositionDispositionKind.HELD)
    multi_input = make_input(module, bundles, results, (held_assertion,), material_competing_candidate_refs=("candidate_branch:demo:alternative",))
    multi_result = module.evaluate_gate_composition(multi_input)
    ledger.check(not multi_result.material_ambiguity_preserved, "multiple candidates not automatic ambiguity")

    e_module, e_ns, e_bundle, e_requirements, e_observations = family["expectancy"]
    changed_obs = list(e_observations)
    changed_obs[0] = e_ns["make_observation"](e_module, e_bundle, e_requirements[0], count=0)
    incomplete_result = e_module.evaluate_expectancy(e_ns["make_input"](e_module, e_bundle, e_requirements, changed_obs))
    incomplete_results = (incomplete_result, results[1], results[2], results[3])
    incomplete_held_assertion = make_assertion(
        module,
        candidate_ref,
        branch_ref,
        tuple(item.result_id for item in incomplete_results),
        module.GateCompositionDispositionKind.HELD,
    )
    incomplete_input = make_input(
        module, bundles, incomplete_results, (incomplete_held_assertion,)
    )
    incomplete_composed = module.evaluate_gate_composition(incomplete_input)
    ledger.check(not incomplete_composed.clarification_relevant_created, "missing role not automatic clarification")

    unsupported_only = disposition_results[module.GateCompositionDispositionKind.UNSUPPORTED]
    ledger.check(not unsupported_only.refusal_relevant_disposition_created, "unsupported not automatic refusal")
    refusal_only = disposition_results[module.GateCompositionDispositionKind.REFUSAL_RELEVANT]
    ledger.check(not refusal_only.rendered and not refusal_only.delivered and not refusal_only.candidate_rejected, "refusal relevance not outward refusal")

    blocked_assertion = make_assertion(module, candidate_ref, branch_ref, result_refs, module.GateCompositionDispositionKind.BLOCKED_PROGRESSION)
    positive_blocked_input = make_input(module, bundles, results, (positive_assertion, blocked_assertion))
    positive_blocked = module.evaluate_gate_composition(positive_blocked_input)
    ledger.check(positive_blocked.later_selection_review_count == 1 and positive_blocked.blocked_progression_count == 1, "understood meaning and blocked consequence coexist")
    ledger.check(not positive_blocked.execution_authorized and not positive_blocked.action_performed, "understanding not action")

    state_cases = (
        (module.GateCompositionAuthorityState.AMBIGUOUS, module.GateCompositionStatus.AMBIGUOUS_AUTHORITY),
        (module.GateCompositionAuthorityState.UNSUPPORTED, module.GateCompositionStatus.UNSUPPORTED_AUTHORITY),
        (module.GateCompositionAuthorityState.CONFLICTED, module.GateCompositionStatus.CONFLICTED_AUTHORITY),
        (module.GateCompositionAuthorityState.ABSENT, module.GateCompositionStatus.INDETERMINATE_AUTHORITY),
    )
    for authority, expected_status in state_cases:
        assertion = make_assertion(module, candidate_ref, branch_ref, result_refs, module.GateCompositionDispositionKind.HELD, authority=authority, judgment=module.GateCompositionJudgment.NOT_EVALUATED)
        state_input = make_input(module, bundles, results, (assertion,))
        state_result = module.evaluate_gate_composition(state_input)
        ledger.check(state_result.composition_status is expected_status, f"status {authority.value}")
        ledger.check(not state_result.dispositions, f"no disposition without admitted authority {authority.value}")

    for instance, name in ((valid_input, "input"), (result, "result"), (positive_assertion, "assertion"), (result.dispositions[0], "disposition")):
        try:
            setattr(instance, fields(instance)[0].name, "mutated")
            immutable = False
        except (FrozenInstanceError, AttributeError, TypeError):
            immutable = True
        ledger.check(immutable, f"immutable {name}")

    malformed = []
    profile = valid_input.runtime_profile
    for field_name in (
        "gate_substitution_allowed", "gate_outcome_erasure_allowed", "generic_flattening_allowed",
        "global_pass_generalization_allowed", "global_failure_generalization_allowed",
        "candidate_branch_erasure_allowed", "effect_boundary_rewrite_allowed", "domain_marker_erasure_allowed",
        "no_action_boundary_conversion_allowed", "automatic_ambiguity_allowed", "automatic_clarification_allowed",
        "automatic_refusal_allowed", "safest_candidate_selection_allowed", "selected_meaning_allowed", "downstream_authority_allowed",
    ):
        malformed.append((replace(profile, **{field_name: True}), module.validate_profile, f"profile {field_name}"))
    for field_name in (
        "raw_text_used_as_selected_meaning", "gate_substitution_used", "gate_outcome_erased", "generic_flattening_used",
        "global_pass_generalized", "global_failure_generalized", "candidate_branch_erased", "effect_boundary_rewritten",
        "domain_marker_erased", "no_action_boundary_converted", "automatic_ambiguity_used", "automatic_clarification_used",
        "automatic_refusal_used", "safest_candidate_selected", "candidate_structure_mutated",
    ):
        malformed.append((replace(valid_input, **{field_name: True}), module.validate_evaluation_input, f"input {field_name}"))
    malformed.extend((
        (replace(valid_input, governance_bundles=valid_input.governance_bundles[:3]), module.validate_evaluation_input, "three bundles"),
        (replace(valid_input, governance_bundles=tuple(reversed(valid_input.governance_bundles))), module.validate_evaluation_input, "wrong bundle order"),
        (replace(valid_input, family_candidate_input_refs=()), module.validate_evaluation_input, "missing family candidate refs"),
        (replace(valid_input, candidate_branch_refs=()), module.validate_evaluation_input, "missing branch"),
        (replace(valid_input, disposition_assertions=()), module.validate_evaluation_input, "missing assertions"),
        (replace(valid_input, candidate_version="v2"), module.validate_evaluation_input, "bad candidate version"),
        (replace(valid_input, evaluation_input_id="bad"), module.validate_evaluation_input, "bad input identity"),
        (replace(positive_assertion, gate_result_refs=("unknown:result",)), module.validate_assertion, "unknown result ref shape"),
        (replace(positive_assertion, later_selection_review_refs=()), module.validate_assertion, "missing positive basis"),
        (replace(positive_assertion, candidate_specific=False), module.validate_assertion, "not candidate specific"),
        (replace(positive_assertion, judgment=module.GateCompositionJudgment.NOT_EVALUATED), module.validate_assertion, "admitted not evaluated"),
        (replace(positive_assertion, assertion_id="bad"), module.validate_assertion, "bad assertion identity"),
        (replace(positive_assertion, ambiguity_refs=("wrong:basis",)), module.validate_assertion, "wrong basis family"),
    ))
    # Result authority and mutation flags must fail closed.
    for field_name in (
        "candidate_accepted", "candidate_rejected", "candidate_clarified", "selected_meaning_created",
        "truth_determined", "evidence_validated", "permission_granted", "execution_authorized",
        "capability_availability_created", "route_created", "tool_invoked", "action_performed",
        "memory_accessed", "memory_written", "rendered", "delivered", "external_resource_loaded",
        "language_model_used", "embedding_used", "vector_used", "rag_used", "semantic_similarity_used",
        "raw_text_used_as_selected_meaning", "gate_substitution_used", "gate_outcome_erased", "generic_flattening_used",
        "global_pass_generalized", "global_failure_generalized", "candidate_branch_erased", "effect_boundary_rewritten",
        "domain_marker_erased", "no_action_boundary_converted", "automatic_ambiguity_used", "automatic_clarification_used",
        "automatic_refusal_used", "safest_candidate_selected", "candidate_structure_mutated",
    ):
        malformed.append((replace(result, **{field_name: True}), module.validate_result, f"result {field_name}"))
    malformed.extend((
        (replace(result, family_result_count=3), module.validate_result, "three family results"),
        (replace(result, applied_disposition_count=0), module.validate_result, "bad applied count"),
        (replace(result, later_selection_review_count=0), module.validate_result, "bad positive count"),
        (replace(result, composition_status=module.GateCompositionStatus.CONFLICTED_AUTHORITY), module.validate_result, "bad status"),
        (replace(result, family_results_preserved=False), module.validate_result, "family results erased"),
        (replace(result, result_id="bad"), module.validate_result, "bad result id"),
        (replace(result, canonical_digest="0" * 64), module.validate_result, "bad result digest"),
    ))

    for value, validator, label in malformed:
        ledger.malformed(_invalid(value, validator), label)

    print("AI.WEB SLICE 40G GATE COMPOSITION BEHAVIOR TEST")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print(f"disposition_kinds={len(tuple(module.GateCompositionDispositionKind))}")
    print(f"finding_kinds={len(tuple(module.GateCompositionFindingKind))}")
    print(f"composition_statuses={len(tuple(module.GateCompositionStatus))}")
    print("gate_composition_evaluator_installed=1")
    print("all_four_gate_results_preserved=1")
    print("no_gate_substitution=1")
    print("composition_by_preservation_not_collapse=1")
    print("material_ambiguity_preserved=1")
    print("clarification_relevant=1")
    print("unsupported_disposition=1")
    print("refusal_relevant=1")
    print("held_disposition=1")
    print("blocked_progression=1")
    print("candidate_supported_for_later_selection_review=1")
    print("multiple_candidates_automatic_ambiguity=0")
    print("missing_role_automatic_clarification=0")
    print("unsupported_automatic_refusal=0")
    print("refusal_relevant_outward_refusal=0")
    print("gate_supported_candidate_selected_meaning=0")
    print("candidate_structure_mutated=0")
    print("truth_evidence_permission_execution=0")
    print("route_tool_action_memory_rendering_delivery=0")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print(f"FAIL: {failure}")
    if ledger.failures:
        print("AI.WEB SLICE 40G GATE COMPOSITION BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 40G GATE COMPOSITION BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
