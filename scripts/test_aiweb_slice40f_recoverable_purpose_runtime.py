#!/usr/bin/env python3
"""Behavior test for AI.Web Slice 40F recoverable-purpose runtime."""
from __future__ import annotations

import argparse
from dataclasses import FrozenInstanceError, replace
import importlib
from pathlib import Path
import runpy
import sys


CORE_PACKAGE = "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime"
GOV_PACKAGE = f"{CORE_PACKAGE}.governed_lifecycle"
PACKAGE = f"{CORE_PACKAGE}.recoverable_purpose_gate"


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.failures: list[str] = []
        self.malformed_cases = 0

    def check(self, condition: bool, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)

    def malformed(self, condition: bool, label: str) -> None:
        self.malformed_cases += 1
        self.check(condition, label)


def make_profile(module, bundle):
    return module.with_expected_profile_id(
        module.RecoverablePurposeGateRuntimeProfile(
            profile_id="recoverable_purpose_profile:placeholder",
            profile_key="exact_intended_purport_authority",
            profile_version="v1.0.0",
            gate_profile_ref=bundle.review_record.profile.profile_id,
            gate_profile_version=bundle.review_record.profile.profile_version,
            governing_authority_refs=(
                "canonical_roadmap:slice40f",
                "document6:recoverable_purpose:v1",
                "document9:crosswalk_a010:v1",
                "slice39d:candidate_communicative_purpose:v1",
            ),
            permitted_distinction_kinds=tuple(
                module.PurportDistinctionKind
            ),
            exact_candidate_records_required=True,
            approved_discourse_ancestry_only=True,
            authorized_reference_state_only=True,
            exact_active_context_only=True,
            hidden_intent_inference_allowed=False,
            capability_existence_inference_allowed=False,
            prior_conversation_habit_allowed=False,
            assistant_intuition_allowed=False,
            psychological_inference_allowed=False,
            emotional_interpretation_allowed=False,
            raw_text_only_inference_allowed=False,
            purpose_conflation_allowed=False,
            automatic_purpose_collapse_allowed=False,
            gate_composition_allowed=False,
            selected_meaning_allowed=False,
            route_tool_action_allowed=False,
        )
    )


def make_assertion(module, bundle, kind, represented, conflated):
    key = kind.value
    return module.with_expected_assertion_id(
        module.RecoverablePurposeAssertion(
            assertion_id="recoverable_purpose_assertion:placeholder",
            candidate_input_ref=(
                bundle.review_record.candidate_input.candidate_input_ref_id
            ),
            predicate_id="predicate:inspect:v1",
            predicate_version="v1.0.0",
            frame_id="predicate_frame:inspect_target:v1",
            frame_version="v1.0.0",
            assertion_key=key,
            distinction_kind=kind,
            represented_act=represented,
            prohibited_conflation_act=conflated,
            candidate_record_refs=(
                f"candidate_purpose:{key}",
                f"candidate_requested_act:{key}",
            ),
            purpose_support_refs=(
                f"purpose_support:{key}",
                f"candidate_structure:{key}",
            ),
            discourse_ancestry_refs=(
                f"discourse_ancestry:{key}",
            ),
            authorized_reference_state_refs=(
                f"authorized_reference_state:{key}",
            ),
            active_context_refs=(
                f"active_context:{key}",
            ),
            authority_refs=(
                "document6:recoverable_purpose_authority:v1",
                f"accepted_purpose_authority:{key}:v1",
            ),
            exact_candidate_records=True,
            discourse_ancestry_authorized=True,
            reference_state_authorized=True,
            active_context_authorized=True,
            explicit_purpose_only=True,
        )
    )


def make_observation(
    module,
    bundle,
    assertion,
    *,
    authority=None,
    judgment=None,
):
    authority = authority or module.RecoverablePurposeAuthorityState.ADMITTED
    if judgment is None:
        judgment = (
            module.RecoverablePurposeJudgment.RECOVERABLE
            if authority is module.RecoverablePurposeAuthorityState.ADMITTED
            else module.RecoverablePurposeJudgment.NOT_EVALUATED
        )
    return module.with_expected_observation_id(
        module.RecoverablePurposeObservation(
            observation_id="recoverable_purpose_observation:placeholder",
            assertion_ref=assertion.assertion_id,
            candidate_input_ref=(
                bundle.review_record.candidate_input.candidate_input_ref_id
            ),
            authority_state=authority,
            purpose_judgment=judgment,
            supporting_refs=(
                (f"support:{assertion.assertion_key}",)
                if judgment
                is module.RecoverablePurposeJudgment.RECOVERABLE
                else ()
            ),
            missing_authority_refs=(
                (f"missing_authority:{assertion.assertion_key}",)
                if authority
                is module.RecoverablePurposeAuthorityState.ABSENT
                or judgment
                is module.RecoverablePurposeJudgment.UNRECOVERABLE
                else ()
            ),
            conflicting_refs=(
                (f"conflict:{assertion.assertion_key}",)
                if authority
                in (
                    module.RecoverablePurposeAuthorityState.CONFLICTED,
                    module.RecoverablePurposeAuthorityState.AMBIGUOUS,
                )
                else ()
            ),
            trace_refs=(
                f"recoverable_purpose_trace:{assertion.assertion_key}",
            ),
            provenance_refs=(
                f"recoverable_purpose_provenance:{assertion.assertion_key}",
            ),
        )
    )


def make_input(module, bundle, assertions, observations, **changes):
    candidate_refs = tuple(
        ref
        for assertion in assertions
        for ref in assertion.candidate_record_refs
    )
    ancestry_refs = tuple(
        ref
        for assertion in assertions
        for ref in assertion.discourse_ancestry_refs
    )
    reference_refs = tuple(
        ref
        for assertion in assertions
        for ref in assertion.authorized_reference_state_refs
    )
    context_refs = tuple(
        ref
        for assertion in assertions
        for ref in assertion.active_context_refs
    )
    value = module.RecoverablePurposeEvaluationInput(
        evaluation_input_id=(
            "recoverable_purpose_evaluation_input:placeholder"
        ),
        governance_bundle=bundle,
        runtime_profile=make_profile(module, bundle),
        candidate_input_ref=(
            bundle.review_record.candidate_input.candidate_input_ref_id
        ),
        predicate_id="predicate:inspect:v1",
        predicate_version="v1.0.0",
        frame_id="predicate_frame:inspect_target:v1",
        frame_version="v1.0.0",
        assertions=tuple(assertions),
        observations=tuple(observations),
        candidate_record_refs=candidate_refs,
        discourse_ancestry_refs=ancestry_refs,
        authorized_reference_state_refs=reference_refs,
        active_context_refs=context_refs,
        trace_refs=(
            "slice39d:candidate_purpose_trace",
            "slice39h:candidate_lineage_trace",
            "slice40b:sealed_governance_trace",
        ),
        provenance_refs=(
            "slice39h:candidate_provenance",
            "slice40b:governance_provenance",
        ),
        limitation_refs=(
            "slice40f:no_hidden_intent",
            "slice40f:no_purpose_conflation",
            "slice40f:no_composition_no_selection",
        ),
        raw_text_supplied=False,
        hidden_intent_inference_used=False,
        capability_existence_inference_used=False,
        prior_conversation_habit_used=False,
        assistant_intuition_used=False,
        psychological_inference_used=False,
        emotional_interpretation_used=False,
        raw_text_only_inference_used=False,
        purpose_conflation_used=False,
        automatic_purpose_collapse_used=False,
        unauthorized_context_used=False,
        candidate_structure_mutated=False,
    )
    if changes:
        value = replace(value, **changes)
    return module.with_expected_evaluation_input_id(value)


def _invalid(module, value, validator) -> bool:
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
    make_bundle = runpy.run_path(
        str(
            repository
            / "scripts/test_aiweb_slice40b_deterministic_validation_identity_versioning_lifecycle.py"
        )
    )["make_bundle"]

    ledger = Ledger()
    bundle = make_bundle(
        core,
        governed,
        core.VerbalCognitionGateFamily.RECOVERABLE_PURPOSE,
    )
    assertions = tuple(
        make_assertion(module, bundle, kind, *module.PURPORT_DISTINCTION_PAIRS[kind])
        for kind in module.PurportDistinctionKind
    )
    observations = tuple(
        make_observation(module, bundle, assertion)
        for assertion in assertions
    )
    valid_input = make_input(module, bundle, assertions, observations)
    result = module.evaluate_recoverable_purpose(valid_input)

    ledger.check(
        module.SLICE40F_ACCEPTED_PARENT_HEAD
        == "2727dc72cbaa436a7c31eec4bb916452c1261c8e",
        "accepted parent head",
    )
    ledger.check(
        module.SLICE40F_ACCEPTED_PARENT_TREE
        == "8a55315ab2a7a2f13a42e4cf26a60e908301c67a",
        "accepted parent tree",
    )
    ledger.check(
        module.SLICE40F_ACCEPTED_PARENT_SUBJECT
        == "Slice 40E deterministic connectedness gate runtime",
        "accepted parent subject",
    )
    ledger.check(
        module.validate_evaluation_input(valid_input).ok,
        "valid input validates",
    )
    ledger.check(module.validate_result(result).ok, "valid result validates")
    ledger.check(
        result.overall_state
        is module.RecoverablePurposeOverallState.RECOVERABLE,
        "recoverable state",
    )
    ledger.check(
        result.recoverable_count == len(assertions),
        "all assertions recoverable",
    )
    ledger.check(
        any(
            item.finding_kind
            is module.RecoverablePurposeFindingKind
            .ALL_PURPOSE_ASSERTIONS_RECOVERED
            for item in result.findings
        ),
        "summary finding",
    )
    ledger.check(
        result.result_id.endswith(result.canonical_digest),
        "result identity and digest align",
    )
    ledger.check(
        module.evaluate_recoverable_purpose(valid_input) == result,
        "deterministic repeat",
    )

    for kind in module.PurportDistinctionKind:
        ledger.check(
            kind in {item.distinction_kind for item in assertions},
            f"distinction present {kind.value}",
        )
    expected_distinctions = {
        module.PurportDistinctionKind.MENTION_REQUEST: (
            module.CommunicativeActKind.MENTION,
            module.CommunicativeActKind.REQUEST,
        ),
        module.PurportDistinctionKind.INSPECT_EXECUTE: (
            module.CommunicativeActKind.INSPECT,
            module.CommunicativeActKind.EXECUTE,
        ),
        module.PurportDistinctionKind.PROPOSE_INSTALL: (
            module.CommunicativeActKind.PROPOSE,
            module.CommunicativeActKind.INSTALL,
        ),
        module.PurportDistinctionKind.SIMULATE_ALTER_LIVE_STATE: (
            module.CommunicativeActKind.SIMULATE,
            module.CommunicativeActKind.ALTER_LIVE_STATE,
        ),
        module.PurportDistinctionKind.REPORT_PROVE: (
            module.CommunicativeActKind.REPORT,
            module.CommunicativeActKind.PROVE,
        ),
        module.PurportDistinctionKind.RETRIEVE_MEMORY_WRITE_MEMORY: (
            module.CommunicativeActKind.RETRIEVE_MEMORY,
            module.CommunicativeActKind.WRITE_MEMORY,
        ),
        module.PurportDistinctionKind.ASK_PERMISSION_POSSESS_PERMISSION: (
            module.CommunicativeActKind.ASK_PERMISSION,
            module.CommunicativeActKind.POSSESS_PERMISSION,
        ),
        module.PurportDistinctionKind.VERIFY_REQUEST_VERIFIED_STATUS: (
            module.CommunicativeActKind.VERIFY_REQUEST,
            module.CommunicativeActKind.VERIFIED_STATUS,
        ),
        module.PurportDistinctionKind.DELIVERY_MEANING_DELIVERY_AUTHORITY: (
            module.CommunicativeActKind.DELIVERY_MEANING,
            module.CommunicativeActKind.DELIVERY_AUTHORITY,
        ),
    }
    ledger.check(
        module.PURPORT_DISTINCTION_PAIRS == expected_distinctions,
        "exact distinction map",
    )

    state_cases = (
        (
            module.RecoverablePurposeAuthorityState.ADMITTED,
            module.RecoverablePurposeJudgment.UNRECOVERABLE,
            module.RecoverablePurposeOverallState.UNRECOVERABLE,
        ),
        (
            module.RecoverablePurposeAuthorityState.AMBIGUOUS,
            module.RecoverablePurposeJudgment.NOT_EVALUATED,
            module.RecoverablePurposeOverallState.AMBIGUOUS,
        ),
        (
            module.RecoverablePurposeAuthorityState.UNSUPPORTED,
            module.RecoverablePurposeJudgment.NOT_EVALUATED,
            module.RecoverablePurposeOverallState.UNSUPPORTED,
        ),
        (
            module.RecoverablePurposeAuthorityState.CONFLICTED,
            module.RecoverablePurposeJudgment.NOT_EVALUATED,
            module.RecoverablePurposeOverallState.CONFLICTED,
        ),
        (
            module.RecoverablePurposeAuthorityState.ABSENT,
            module.RecoverablePurposeJudgment.NOT_EVALUATED,
            module.RecoverablePurposeOverallState.INDETERMINATE,
        ),
    )
    observed_states = {result.overall_state}
    for authority, judgment, expected in state_cases:
        changed_observation = make_observation(
            module,
            bundle,
            assertions[0],
            authority=authority,
            judgment=judgment,
        )
        changed = make_input(
            module,
            bundle,
            assertions,
            (changed_observation, *observations[1:]),
        )
        changed_result = module.evaluate_recoverable_purpose(changed)
        observed_states.add(changed_result.overall_state)
        ledger.check(
            changed_result.overall_state is expected,
            f"state {expected.value}",
        )
    ledger.check(
        observed_states == set(module.RecoverablePurposeOverallState),
        "all overall states exercised",
    )

    # Immutable records.
    for value, field_name, replacement_value in (
        (assertions[0], "assertion_key", "changed"),
        (observations[0], "supporting_refs", ("changed",)),
        (valid_input, "candidate_input_ref", "changed"),
        (result, "candidate_input_ref", "changed"),
    ):
        try:
            setattr(value, field_name, replacement_value)
            frozen = False
        except (FrozenInstanceError, AttributeError):
            frozen = True
        ledger.check(frozen, f"frozen {type(value).__name__}")

    # Profile negative cases.
    profile = valid_input.runtime_profile
    for name in (
        "hidden_intent_inference_allowed",
        "capability_existence_inference_allowed",
        "prior_conversation_habit_allowed",
        "assistant_intuition_allowed",
        "psychological_inference_allowed",
        "emotional_interpretation_allowed",
        "raw_text_only_inference_allowed",
        "purpose_conflation_allowed",
        "automatic_purpose_collapse_allowed",
        "gate_composition_allowed",
        "selected_meaning_allowed",
        "route_tool_action_allowed",
    ):
        invalid = module.with_expected_profile_id(
            replace(profile, **{name: True})
        )
        ledger.malformed(
            _invalid(module, invalid, module.validate_profile),
            f"profile rejects {name}",
        )
    for name in (
        "exact_candidate_records_required",
        "approved_discourse_ancestry_only",
        "authorized_reference_state_only",
        "exact_active_context_only",
    ):
        invalid = module.with_expected_profile_id(
            replace(profile, **{name: False})
        )
        ledger.malformed(
            _invalid(module, invalid, module.validate_profile),
            f"profile requires {name}",
        )
    profile_variants = (
        replace(profile, profile_id="wrong"),
        module.with_expected_profile_id(
            replace(profile, profile_version="v2.0.0")
        ),
        module.with_expected_profile_id(
            replace(profile, governing_authority_refs=())
        ),
        module.with_expected_profile_id(
            replace(
                profile,
                permitted_distinction_kinds=tuple(
                    list(module.PurportDistinctionKind)[:-1]
                ),
            )
        ),
    )
    for index, invalid in enumerate(profile_variants):
        ledger.malformed(
            _invalid(module, invalid, module.validate_profile),
            f"profile variant {index}",
        )

    # Assertion negative cases.
    assertion = assertions[0]
    assertion_variants = (
        replace(assertion, assertion_id="wrong"),
        module.with_expected_assertion_id(
            replace(assertion, predicate_version="v2.0.0")
        ),
        module.with_expected_assertion_id(
            replace(assertion, candidate_record_refs=())
        ),
        module.with_expected_assertion_id(
            replace(assertion, purpose_support_refs=())
        ),
        module.with_expected_assertion_id(
            replace(assertion, authority_refs=())
        ),
        module.with_expected_assertion_id(
            replace(assertion, exact_candidate_records=False)
        ),
        module.with_expected_assertion_id(
            replace(assertion, explicit_purpose_only=False)
        ),
        module.with_expected_assertion_id(
            replace(
                assertion,
                prohibited_conflation_act=assertion.represented_act,
            )
        ),
        module.with_expected_assertion_id(
            replace(
                assertion,
                prohibited_conflation_act=(
                    module.CommunicativeActKind.EXECUTE
                ),
            )
        ),
        module.with_expected_assertion_id(
            replace(assertion, discourse_ancestry_authorized=False)
        ),
        module.with_expected_assertion_id(
            replace(assertion, reference_state_authorized=False)
        ),
        module.with_expected_assertion_id(
            replace(assertion, active_context_authorized=False)
        ),
        module.with_expected_assertion_id(
            replace(
                assertion,
                discourse_ancestry_refs=(),
                discourse_ancestry_authorized=True,
            )
        ),
        module.with_expected_assertion_id(
            replace(
                assertion,
                authorized_reference_state_refs=(),
                reference_state_authorized=True,
            )
        ),
        module.with_expected_assertion_id(
            replace(
                assertion,
                active_context_refs=(),
                active_context_authorized=True,
            )
        ),
    )
    for index, invalid in enumerate(assertion_variants):
        ledger.malformed(
            _invalid(module, invalid, module.validate_assertion),
            f"assertion variant {index}",
        )

    # Observation negative cases.
    observation = observations[0]
    observation_variants = (
        replace(observation, observation_id="wrong"),
        module.with_expected_observation_id(
            replace(observation, supporting_refs=())
        ),
        module.with_expected_observation_id(
            replace(
                observation,
                authority_state=(
                    module.RecoverablePurposeAuthorityState.ABSENT
                ),
                purpose_judgment=(
                    module.RecoverablePurposeJudgment.RECOVERABLE
                ),
                supporting_refs=("invalid_support",),
                missing_authority_refs=(),
            )
        ),
        module.with_expected_observation_id(
            replace(
                observation,
                purpose_judgment=(
                    module.RecoverablePurposeJudgment.UNRECOVERABLE
                ),
                supporting_refs=(),
                missing_authority_refs=(),
                conflicting_refs=(),
            )
        ),
        module.with_expected_observation_id(
            replace(
                observation,
                authority_state=(
                    module.RecoverablePurposeAuthorityState.CONFLICTED
                ),
                purpose_judgment=(
                    module.RecoverablePurposeJudgment.NOT_EVALUATED
                ),
                supporting_refs=(),
                conflicting_refs=(),
            )
        ),
        module.with_expected_observation_id(
            replace(observation, trace_refs=())
        ),
        module.with_expected_observation_id(
            replace(observation, provenance_refs=())
        ),
    )
    for index, invalid in enumerate(observation_variants):
        ledger.malformed(
            _invalid(module, invalid, module.validate_observation),
            f"observation variant {index}",
        )

    # Evaluation-input boundary and mismatch cases.
    input_flags = (
        "hidden_intent_inference_used",
        "capability_existence_inference_used",
        "prior_conversation_habit_used",
        "assistant_intuition_used",
        "psychological_inference_used",
        "emotional_interpretation_used",
        "raw_text_only_inference_used",
        "purpose_conflation_used",
        "automatic_purpose_collapse_used",
        "unauthorized_context_used",
        "candidate_structure_mutated",
        "raw_text_supplied",
    )
    for name in input_flags:
        invalid = module.with_expected_evaluation_input_id(
            replace(valid_input, **{name: True})
        )
        ledger.malformed(
            _invalid(module, invalid, module.validate_evaluation_input),
            f"input rejects {name}",
        )
    duplicate_assertions = (assertions[0], assertions[0], *assertions[1:])
    duplicate_observations = (
        observations[0],
        observations[0],
        *observations[1:],
    )
    input_variants = (
        replace(valid_input, evaluation_input_id="wrong"),
        module.with_expected_evaluation_input_id(
            replace(valid_input, assertions=())
        ),
        module.with_expected_evaluation_input_id(
            replace(valid_input, observations=())
        ),
        module.with_expected_evaluation_input_id(
            replace(valid_input, assertions=duplicate_assertions)
        ),
        module.with_expected_evaluation_input_id(
            replace(valid_input, observations=duplicate_observations)
        ),
        module.with_expected_evaluation_input_id(
            replace(valid_input, observations=observations[:-1])
        ),
        module.with_expected_evaluation_input_id(
            replace(valid_input, candidate_record_refs=())
        ),
        module.with_expected_evaluation_input_id(
            replace(valid_input, trace_refs=())
        ),
        module.with_expected_evaluation_input_id(
            replace(valid_input, provenance_refs=())
        ),
        module.with_expected_evaluation_input_id(
            replace(valid_input, limitation_refs=())
        ),
    )
    for index, invalid in enumerate(input_variants):
        ledger.malformed(
            _invalid(module, invalid, module.validate_evaluation_input),
            f"input variant {index}",
        )

    bad_family_bundle = make_bundle(
        core,
        governed,
        core.VerbalCognitionGateFamily.CONNECTEDNESS,
    )
    bad_family_input = module.with_expected_evaluation_input_id(
        replace(
            valid_input,
            governance_bundle=bad_family_bundle,
            runtime_profile=make_profile(module, bad_family_bundle),
            candidate_input_ref=(
                bad_family_bundle.review_record.candidate_input
                .candidate_input_ref_id
            ),
        )
    )
    ledger.malformed(
        _invalid(
            module,
            bad_family_input,
            module.validate_evaluation_input,
        ),
        "recoverable-purpose family required",
    )

    # Result tamper cases.
    result_variants = (
        replace(result, result_id="wrong"),
        replace(result, canonical_digest="0" * 64),
        replace(
            result,
            overall_state=(
                module.RecoverablePurposeOverallState.UNRECOVERABLE
            ),
        ),
        replace(result, assertion_count=result.assertion_count + 1),
        replace(result, recoverable_count=result.recoverable_count - 1),
        replace(result, deterministic=False),
        replace(result, exact_purpose_authority_preserved=False),
        replace(result, selected_meaning_created=True),
        replace(result, permission_granted=True),
        replace(result, memory_written=True),
        replace(result, hidden_intent_inference_used=True),
        replace(result, capability_existence_inference_used=True),
        replace(result, purpose_conflation_used=True),
    )
    for index, invalid in enumerate(result_variants):
        ledger.malformed(
            _invalid(module, invalid, module.validate_result),
            f"result variant {index}",
        )

    # Every consequence-bearing field remains false.
    boundary_fields = (
        "candidate_structure_mutated",
        "hidden_intent_inference_used",
        "capability_existence_inference_used",
        "prior_conversation_habit_used",
        "assistant_intuition_used",
        "psychological_inference_used",
        "emotional_interpretation_used",
        "raw_text_only_inference_used",
        "purpose_conflation_used",
        "automatic_purpose_collapse_used",
        "unauthorized_context_used",
        "clarification_required_created",
        "rejection_created",
        "refusal_relevant_created",
        "blocked_progression_created",
        "composed_gate_outcome_created",
        "candidate_disposition_created",
        "selected_meaning_created",
        "truth_determined",
        "evidence_validated",
        "permission_granted",
        "execution_authorized",
        "capability_availability_created",
        "route_created",
        "tool_invoked",
        "action_performed",
        "memory_accessed",
        "memory_written",
        "rendered",
        "delivered",
        "external_resource_loaded",
        "language_model_used",
        "embedding_used",
        "vector_used",
        "rag_used",
        "semantic_similarity_used",
    )
    for name in boundary_fields:
        ledger.check(
            getattr(result, name) is False,
            f"result boundary false {name}",
        )

    print("AI.WEB SLICE 40F RECOVERABLE PURPOSE BEHAVIOR TEST")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print(f"distinction_kinds={len(module.PurportDistinctionKind)}")
    print(f"communicative_act_kinds={len(module.CommunicativeActKind)}")
    print(f"finding_kinds={len(module.RecoverablePurposeFindingKind)}")
    print(f"overall_states={len(module.RecoverablePurposeOverallState)}")
    print("recoverable_purpose_evaluator_installed=1")
    print("mention_not_request=1")
    print("inspect_not_execute=1")
    print("propose_not_install=1")
    print("simulate_not_alter_live_state=1")
    print("report_not_prove=1")
    print("retrieve_memory_not_write_memory=1")
    print("ask_permission_not_possess_permission=1")
    print("verify_request_not_verified_status=1")
    print("delivery_meaning_not_delivery_authority=1")
    print("recoverable_result=1")
    print("unrecoverable_result=1")
    print("ambiguous_result=1")
    print("unsupported_result=1")
    print("conflicted_result=1")
    print("indeterminate_result=1")
    print("exact_candidate_records_used=1")
    print("approved_discourse_ancestry_only=1")
    print("authorized_reference_state_only=1")
    print("exact_active_context_only=1")
    print("hidden_intent_inference_used=0")
    print("capability_existence_inference_used=0")
    print("prior_conversation_habit_used=0")
    print("assistant_intuition_used=0")
    print("psychological_inference_used=0")
    print("emotional_interpretation_used=0")
    print("raw_text_only_inference_used=0")
    print("purpose_conflation_used=0")
    print("automatic_purpose_collapse_used=0")
    print("candidate_structure_mutated=0")
    print("clarification_required_created=0")
    print("rejection_created=0")
    print("composed_gate_outcome_created=0")
    print("candidate_disposition_created=0")
    print("selected_meaning_created=0")
    print("truth_evidence_permission_execution=0")
    print("route_tool_action_memory_rendering_delivery=0")
    print(f"failure_count={len(ledger.failures)}")
    if ledger.failures:
        for failure in ledger.failures:
            print(f"FAIL: {failure}")
        return 1
    print(
        "AI.WEB SLICE 40F RECOVERABLE PURPOSE BEHAVIOR TEST: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
