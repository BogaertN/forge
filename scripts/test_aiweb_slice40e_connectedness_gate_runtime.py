#!/usr/bin/env python3
"""Behavior test for AI.Web Slice 40E connectedness-gate runtime."""
from __future__ import annotations

import argparse
from dataclasses import FrozenInstanceError, replace
import importlib
from pathlib import Path
import runpy
import sys


CORE_PACKAGE = "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime"
GOV_PACKAGE = f"{CORE_PACKAGE}.governed_lifecycle"
PACKAGE = f"{CORE_PACKAGE}.connectedness_gate"


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
        module.ConnectednessGateRuntimeProfile(
            profile_id="connectedness_profile:placeholder",
            profile_key="connectedness_exact_admitted_links",
            profile_version="v1.0.0",
            gate_profile_ref=bundle.review_record.profile.profile_id,
            gate_profile_version=bundle.review_record.profile.profile_version,
            governing_authority_refs=(
                "canonical_roadmap:slice40e",
                "document6:connectedness_gate:v1",
                "slice36:source_structural_trace:v1",
                "slice39:candidate_lineage:v1",
            ),
            permitted_assertion_kinds=tuple(module.ConnectednessAssertionKind),
            exact_admitted_connections_only=True,
            cooccurrence_connection_allowed=False,
            same_expression_connection_allowed=False,
            same_manifest_connection_allowed=False,
            implicit_transitivity_allowed=False,
            source_gap_bridge_allowed=False,
            ancestry_gap_bridge_allowed=False,
            scope_rewrite_allowed=False,
            attachment_reassignment_allowed=False,
            operator_trail_rewrite_allowed=False,
            predicate_frame_rewire_allowed=False,
            candidate_lineage_merge_allowed=False,
            raw_text_inspection_allowed=False,
            similarity_fallback_allowed=False,
            hidden_model_judgment_allowed=False,
            gate_composition_allowed=False,
            selected_meaning_allowed=False,
            route_tool_action_allowed=False,
        )
    )


def make_assertion(module, bundle, kind, key, *, left=None, right=None):
    return module.with_expected_assertion_id(
        module.ConnectednessAssertion(
            assertion_id="connectedness_assertion:placeholder",
            candidate_input_ref=(
                bundle.review_record.candidate_input.candidate_input_ref_id
            ),
            predicate_id="predicate:inspect:v1",
            predicate_version="v1.0.0",
            frame_id="predicate_frame:inspect_target:v1",
            frame_version="v1.0.0",
            assertion_key=key,
            assertion_kind=kind,
            left_record_ref=left or f"candidate_record:left:{key}",
            right_record_ref=right or f"candidate_record:right:{key}",
            connection_basis_refs=(
                f"connection_basis:{kind.value}:{key}",
                f"connection_trace:{kind.value}:{key}",
            ),
            assertion_source_refs=(
                f"slice36:structural_source:{key}",
                f"slice39:candidate_lineage:{key}",
                f"document6:connectedness:{key}",
            ),
            authority_refs=(
                "document6:connectedness_authority:v1",
                f"accepted_authority:{kind.value}:v1",
            ),
            exact_admitted_connection=True,
            same_expression_only=False,
            same_manifest_only=False,
            implicit_transitive_only=False,
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
    authority = authority or module.ConnectednessAuthorityState.ADMITTED
    if judgment is None:
        judgment = (
            module.ConnectednessJudgment.CONNECTED
            if authority is module.ConnectednessAuthorityState.ADMITTED
            else module.ConnectednessJudgment.NOT_EVALUATED
        )
    return module.with_expected_observation_id(
        module.ConnectednessObservation(
            observation_id="connectedness_observation:placeholder",
            assertion_ref=assertion.assertion_id,
            candidate_input_ref=(
                bundle.review_record.candidate_input.candidate_input_ref_id
            ),
            authority_state=authority,
            connection_judgment=judgment,
            supporting_refs=(
                (f"support:{assertion.assertion_key}",)
                if judgment is module.ConnectednessJudgment.CONNECTED
                else ()
            ),
            disconnection_refs=(
                (f"disconnect:{assertion.assertion_key}",)
                if judgment is module.ConnectednessJudgment.DISCONNECTED
                or authority is module.ConnectednessAuthorityState.CONFLICTED
                else ()
            ),
            trace_refs=(f"connectedness_trace:{assertion.assertion_key}",),
            provenance_refs=(
                f"connectedness_provenance:{assertion.assertion_key}",
            ),
        )
    )


def make_input(module, bundle, assertions, observations, **changes):
    value = module.ConnectednessEvaluationInput(
        evaluation_input_id="connectedness_evaluation_input:placeholder",
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
        trace_refs=(
            "slice36:source_field_trace",
            "slice39h:candidate_trace",
            "slice40b:sealed_governance_trace",
            "slice40d:congruity_trace",
        ),
        provenance_refs=(
            "slice39h:candidate_provenance",
            "slice40b:governance_provenance",
            "slice40d:congruity_provenance",
        ),
        limitation_refs=(
            "slice40e:no_cooccurrence_no_transitive_invention",
            "slice40e:no_composition_no_selection",
        ),
        raw_text_supplied=False,
        cooccurrence_only_connection_used=False,
        same_expression_only_connection_used=False,
        same_manifest_only_connection_used=False,
        implicit_transitive_connection_used=False,
        source_gap_bridged=False,
        ancestry_gap_bridged=False,
        scope_rewritten=False,
        attachment_reassigned=False,
        operator_trail_rewritten=False,
        predicate_frame_rewired=False,
        candidate_lineage_merged=False,
        similarity_fallback_used=False,
        hidden_model_judgment_used=False,
    )
    if changes:
        value = replace(value, **changes)
    return module.with_expected_evaluation_input_id(value)


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
        core.VerbalCognitionGateFamily.CONNECTEDNESS,
    )
    assertions = tuple(
        make_assertion(module, bundle, kind, kind.value)
        for kind in module.ConnectednessAssertionKind
    )
    observations = tuple(
        make_observation(module, bundle, assertion)
        for assertion in assertions
    )
    valid_input = make_input(module, bundle, assertions, observations)
    original_input = valid_input
    result = module.evaluate_connectedness(valid_input)

    ledger.check(
        module.SLICE40E_ACCEPTED_PARENT_HEAD
        == "b9b5e835e7506bc2b7849d3221b0328227add7fd",
        "accepted parent head",
    )
    ledger.check(
        module.SLICE40E_ACCEPTED_PARENT_TREE
        == "cd26ca5243fe76c0a7a12e2ee53e471538796eee",
        "accepted parent tree",
    )
    ledger.check(
        module.SLICE40E_ACCEPTED_PARENT_SUBJECT
        == "Slice 40D deterministic congruity gate runtime",
        "accepted parent subject",
    )
    ledger.check(module.validate_evaluation_input(valid_input).ok, "valid input")
    ledger.check(module.validate_result(result).ok, "valid result")
    ledger.check(valid_input == original_input, "input unchanged")
    ledger.check(
        result.overall_state is module.ConnectednessOverallState.CONNECTED,
        "connected overall",
    )
    ledger.check(result.assertion_count == 7, "assertion count")
    ledger.check(result.connected_count == 7, "connected count")
    ledger.check(result.disconnected_count == 0, "disconnected zero")
    ledger.check(
        module.ConnectednessFindingKind.ALL_ASSERTIONS_CONNECTED
        in tuple(finding.finding_kind for finding in result.findings),
        "all connected finding",
    )
    ledger.check(
        result == module.evaluate_connectedness(valid_input),
        "deterministic repeat",
    )
    for index in range(24):
        ledger.check(
            module.evaluate_connectedness(valid_input) == result,
            f"repeat determinism {index}",
        )

    for index, assertion in enumerate(assertions):
        altered = list(observations)
        altered[index] = make_observation(
            module,
            bundle,
            assertion,
            judgment=module.ConnectednessJudgment.DISCONNECTED,
        )
        item = module.evaluate_connectedness(
            make_input(module, bundle, assertions, altered)
        )
        ledger.check(
            item.overall_state is module.ConnectednessOverallState.DISCONNECTED,
            f"{assertion.assertion_kind.value} disconnected",
        )
        ledger.check(
            item.disconnected_count == 1,
            f"{assertion.assertion_kind.value} disconnected count",
        )
        exact = [
            finding
            for finding in item.findings
            if finding.assertion_ref == assertion.assertion_id
        ]
        ledger.check(
            len(exact) == 1
            and exact[0].finding_kind
            is module.ConnectednessFindingKind.DISCONNECTED_ASSERTION,
            f"{assertion.assertion_kind.value} exact finding",
        )
        ledger.check(
            not item.rejection_created
            and not item.clarification_required_created,
            f"{assertion.assertion_kind.value} no automatic disposition",
        )

    state_cases = (
        (
            module.ConnectednessAuthorityState.AMBIGUOUS,
            module.ConnectednessOverallState.AMBIGUOUS,
            module.ConnectednessFindingKind.AMBIGUOUS_ASSERTION,
        ),
        (
            module.ConnectednessAuthorityState.UNSUPPORTED,
            module.ConnectednessOverallState.UNSUPPORTED,
            module.ConnectednessFindingKind.UNSUPPORTED_ASSERTION,
        ),
        (
            module.ConnectednessAuthorityState.CONFLICTED,
            module.ConnectednessOverallState.CONFLICTED,
            module.ConnectednessFindingKind.CONFLICTED_ASSERTION,
        ),
        (
            module.ConnectednessAuthorityState.ABSENT,
            module.ConnectednessOverallState.INDETERMINATE,
            module.ConnectednessFindingKind.INDETERMINATE_AUTHORITY_ABSENT,
        ),
    )
    for state, overall, finding_kind in state_cases:
        altered = list(observations)
        altered[0] = make_observation(
            module,
            bundle,
            assertions[0],
            authority=state,
        )
        item = module.evaluate_connectedness(
            make_input(module, bundle, assertions, altered)
        )
        ledger.check(item.overall_state is overall, f"{state.value} overall")
        ledger.check(
            finding_kind
            in tuple(finding.finding_kind for finding in item.findings),
            f"{state.value} finding",
        )
        ledger.check(
            not item.clarification_required_created
            and not item.candidate_disposition_created,
            f"{state.value} no disposition",
        )

    # Exact A-B and B-C evidence must not invent A-C connection authority.
    first = make_assertion(
        module,
        bundle,
        module.ConnectednessAssertionKind.CANDIDATE_LINEAGE,
        "lineage_a_b",
        left="candidate_node:a",
        right="candidate_node:b",
    )
    second = make_assertion(
        module,
        bundle,
        module.ConnectednessAssertionKind.CANDIDATE_LINEAGE,
        "lineage_b_c",
        left="candidate_node:b",
        right="candidate_node:c",
    )
    transitive_input = make_input(
        module,
        bundle,
        (first, second),
        (
            make_observation(module, bundle, first),
            make_observation(module, bundle, second),
        ),
    )
    transitive_result = module.evaluate_connectedness(transitive_input)
    ledger.check(transitive_result.assertion_count == 2, "no invented A-C assertion")
    ledger.check(
        not transitive_result.implicit_transitive_connection_used,
        "no invented transitive connection",
    )
    ledger.check(
        all(
            finding.assertion_ref in (first.assertion_id, second.assertion_id, None)
            for finding in transitive_result.findings
        ),
        "findings limited to exact A-B and B-C assertions",
    )

    def rejected(call, label):
        try:
            call()
        except module.ConnectednessValidationError:
            ledger.malformed(True, label)
        except Exception:
            ledger.malformed(False, label + " wrong exception")
        else:
            ledger.malformed(False, label + " accepted")

    profile_false_flags = (
        "cooccurrence_connection_allowed",
        "same_expression_connection_allowed",
        "same_manifest_connection_allowed",
        "implicit_transitivity_allowed",
        "source_gap_bridge_allowed",
        "ancestry_gap_bridge_allowed",
        "scope_rewrite_allowed",
        "attachment_reassignment_allowed",
        "operator_trail_rewrite_allowed",
        "predicate_frame_rewire_allowed",
        "candidate_lineage_merge_allowed",
        "raw_text_inspection_allowed",
        "similarity_fallback_allowed",
        "hidden_model_judgment_allowed",
        "gate_composition_allowed",
        "selected_meaning_allowed",
        "route_tool_action_allowed",
    )
    for flag in profile_false_flags:
        bad_profile = replace(valid_input.runtime_profile, **{flag: True})
        bad_profile = module.with_expected_profile_id(bad_profile)
        rejected(
            lambda bad_profile=bad_profile: module.assert_valid_evaluation_input(
                module.with_expected_evaluation_input_id(
                    replace(valid_input, runtime_profile=bad_profile)
                )
            ),
            f"profile {flag}",
        )

    input_false_flags = (
        "raw_text_supplied",
        "cooccurrence_only_connection_used",
        "same_expression_only_connection_used",
        "same_manifest_only_connection_used",
        "implicit_transitive_connection_used",
        "source_gap_bridged",
        "ancestry_gap_bridged",
        "scope_rewritten",
        "attachment_reassigned",
        "operator_trail_rewritten",
        "predicate_frame_rewired",
        "candidate_lineage_merged",
        "similarity_fallback_used",
        "hidden_model_judgment_used",
    )
    for flag in input_false_flags:
        rejected(
            lambda flag=flag: module.assert_valid_evaluation_input(
                make_input(
                    module,
                    bundle,
                    assertions,
                    observations,
                    **{flag: True},
                )
            ),
            f"input {flag}",
        )

    rejected(
        lambda: module.assert_valid_evaluation_input(
            replace(valid_input, evaluation_input_id="bad id")
        ),
        "bad input id",
    )
    rejected(
        lambda: module.assert_valid_evaluation_input(
            module.with_expected_evaluation_input_id(
                replace(valid_input, predicate_version="v9")
            )
        ),
        "unknown predicate version",
    )
    rejected(
        lambda: module.assert_valid_evaluation_input(
            module.with_expected_evaluation_input_id(
                replace(valid_input, assertions=assertions + (assertions[0],))
            )
        ),
        "duplicate assertion",
    )
    rejected(
        lambda: module.assert_valid_evaluation_input(
            module.with_expected_evaluation_input_id(
                replace(valid_input, observations=observations[:-1])
            )
        ),
        "missing observation",
    )
    rejected(
        lambda: module.assert_valid_evaluation_input(
            module.with_expected_evaluation_input_id(
                replace(valid_input, observations=observations + (observations[0],))
            )
        ),
        "duplicate observation",
    )

    bad_assertion_changes = (
        ("exact_admitted_connection", False),
        ("same_expression_only", True),
        ("same_manifest_only", True),
        ("implicit_transitive_only", True),
        ("right_record_ref", assertions[0].left_record_ref),
        ("connection_basis_refs", ()),
    )
    for field_name, field_value in bad_assertion_changes:
        bad_assertion = module.with_expected_assertion_id(
            replace(assertions[0], **{field_name: field_value})
        )
        rejected(
            lambda bad_assertion=bad_assertion: module.assert_valid_evaluation_input(
                make_input(
                    module,
                    bundle,
                    (bad_assertion, *assertions[1:]),
                    observations,
                )
            ),
            f"assertion {field_name}",
        )

    bad_observation = module.with_expected_observation_id(
        replace(
            observations[0],
            authority_state=module.ConnectednessAuthorityState.ABSENT,
            connection_judgment=module.ConnectednessJudgment.CONNECTED,
        )
    )
    rejected(
        lambda: module.assert_valid_evaluation_input(
            make_input(
                module,
                bundle,
                assertions,
                (bad_observation, *observations[1:]),
            )
        ),
        "absent authority judgment",
    )
    connected_without_support = module.with_expected_observation_id(
        replace(observations[0], supporting_refs=())
    )
    rejected(
        lambda: module.assert_valid_evaluation_input(
            make_input(
                module,
                bundle,
                assertions,
                (connected_without_support, *observations[1:]),
            )
        ),
        "connected judgment without support",
    )
    disconnected_without_basis = module.with_expected_observation_id(
        replace(
            observations[0],
            connection_judgment=module.ConnectednessJudgment.DISCONNECTED,
            supporting_refs=(),
            disconnection_refs=(),
        )
    )
    rejected(
        lambda: module.assert_valid_evaluation_input(
            make_input(
                module,
                bundle,
                assertions,
                (disconnected_without_basis, *observations[1:]),
            )
        ),
        "disconnected judgment without basis",
    )

    congruity_bundle = make_bundle(
        core,
        governed,
        core.VerbalCognitionGateFamily.CONGRUITY,
    )
    rejected(
        lambda: module.assert_valid_evaluation_input(
            make_input(module, congruity_bundle, assertions, observations)
        ),
        "wrong gate family",
    )
    unsealed = replace(bundle, validation_complete=False)
    rejected(
        lambda: module.assert_valid_evaluation_input(
            make_input(module, unsealed, assertions, observations)
        ),
        "unsealed governance",
    )

    result_false_flags = (
        "candidate_structure_mutated",
        "cooccurrence_only_connection_used",
        "same_expression_only_connection_used",
        "same_manifest_only_connection_used",
        "implicit_transitive_connection_used",
        "source_gap_bridged",
        "ancestry_gap_bridged",
        "scope_rewritten",
        "attachment_reassigned",
        "operator_trail_rewritten",
        "predicate_frame_rewired",
        "candidate_lineage_merged",
        "similarity_fallback_used",
        "hidden_model_judgment_used",
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
        "route_created",
        "tool_invoked",
        "action_performed",
        "memory_accessed",
        "rendered",
        "delivered",
        "external_resource_loaded",
        "language_model_used",
        "embedding_used",
        "vector_used",
        "rag_used",
        "semantic_similarity_used",
    )
    for flag in result_false_flags:
        rejected(
            lambda flag=flag: module.assert_valid_result(
                module.with_expected_result_identity(
                    replace(
                        result,
                        **{flag: True},
                        canonical_digest="0" * 64,
                        result_id="connectedness_result:placeholder",
                    )
                )
            ),
            f"result {flag}",
        )

    rejected(
        lambda: module.assert_valid_result(replace(result, connected_count=6)),
        "count mismatch",
    )
    rejected(
        lambda: module.assert_valid_result(
            module.with_expected_result_identity(
                replace(
                    result,
                    overall_state=module.ConnectednessOverallState.DISCONNECTED,
                    canonical_digest="0" * 64,
                    result_id="connectedness_result:placeholder",
                )
            )
        ),
        "overall state mismatch",
    )
    rejected(
        lambda: module.assert_valid_result(
            module.with_expected_result_identity(
                replace(
                    result,
                    findings=result.findings[:-1],
                    canonical_digest="0" * 64,
                    result_id="connectedness_result:placeholder",
                )
            )
        ),
        "summary finding missing",
    )
    rejected(
        lambda: module.assert_valid_result(
            replace(result, canonical_digest="f" * 64)
        ),
        "digest mismatch",
    )

    try:
        result.overall_state = module.ConnectednessOverallState.DISCONNECTED
        ledger.check(False, "frozen result")
    except FrozenInstanceError:
        ledger.check(True, "frozen result")

    zero_flags = tuple(
        getattr(result, flag)
        for flag in result_false_flags
    )
    ledger.check(not any(zero_flags), "all downstream and invention flags zero")

    print("AI.WEB SLICE 40E CONNECTEDNESS GATE BEHAVIOR TEST")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print(f"assertion_kinds={len(module.ConnectednessAssertionKind)}")
    print(f"finding_kinds={len(module.ConnectednessFindingKind)}")
    print(f"overall_states={len(module.ConnectednessOverallState)}")
    print("connectedness_evaluator_installed=1")
    print("source_span_connectedness=1")
    print("structural_ancestry_connectedness=1")
    print("scope_connectedness=1")
    print("attachment_connectedness=1")
    print("operator_trail_connectedness=1")
    print("predicate_frame_connectedness=1")
    print("candidate_lineage_connectedness=1")
    print("connected_result=1")
    print("disconnected_result=1")
    print("ambiguous_result=1")
    print("unsupported_result=1")
    print("conflicted_result=1")
    print("indeterminate_result=1")
    print("same_expression_only_connection=0")
    print("same_manifest_only_connection=0")
    print("implicit_transitive_connection=0")
    print("source_gap_bridged=0")
    print("ancestry_gap_bridged=0")
    print("scope_rewritten=0")
    print("attachment_reassigned=0")
    print("operator_trail_rewritten=0")
    print("predicate_frame_rewired=0")
    print("candidate_lineage_merged=0")
    print("candidate_structure_mutated=0")
    print("similarity_fallback_used=0")
    print("hidden_model_judgment_used=0")
    print("clarification_required_created=0")
    print("rejection_created=0")
    print("composed_gate_outcome_created=0")
    print("candidate_disposition_created=0")
    print("selected_meaning_created=0")
    print("truth_evidence_permission_execution=0")
    print("route_tool_action_memory_rendering_delivery=0")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print(f"FAIL: {failure}")
    if ledger.failures:
        print("AI.WEB SLICE 40E CONNECTEDNESS GATE BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 40E CONNECTEDNESS GATE BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
