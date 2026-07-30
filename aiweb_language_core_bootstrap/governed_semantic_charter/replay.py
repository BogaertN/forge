"""Pure semantic replay and proposed-scope evaluation for the charter."""

from __future__ import annotations

from dataclasses import replace
import hashlib

from ..meaning_compiler_preview import compile_meaning_preview
from ..meaning_compiler_preview.schema import FrameCandidate, MeaningCandidate
from .charter import PROPOSED_SEMANTIC_CHARTER
from .schema import (
    CharterReplayCaseResult,
    CharterReplayResult,
    CharterReplayStatus,
    CharterSourceDisposition,
    CharterSourceEvaluation,
    ProposedConstructionContract,
    ProposedSemanticCharter,
    SemanticReplayFixture,
)
from .validation import assert_valid_semantic_charter


def _enum_value(value: object) -> str:
    return str(getattr(value, "value", value))


def _case_result(
    fixture: SemanticReplayFixture,
    construction: ProposedConstructionContract,
    compiler_result: object | None = None,
) -> CharterReplayCaseResult:
    reasons: list[str] = []
    if compiler_result is None:
        try:
            compiler_result = compile_meaning_preview(fixture.exact_source_text)
        except Exception:
            compiler_result = None
            reasons.append("compiler_exception_contained")

    compiler_result_ref = ""
    observed_status = ""
    observed_echo_status = ""
    observed_candidate_ref = ""
    observed_signature = ""
    construction_matched = False
    semantic_identity_matched = False
    exact_reference_sets_matched = False

    if compiler_result is None:
        reasons.append("compiler_result_unavailable")
    else:
        compiler_result_ref = str(getattr(compiler_result, "result_id", ""))
        observed_status = _enum_value(getattr(compiler_result, "status", ""))
        echo = getattr(compiler_result, "echo", None)
        observed_echo_status = _enum_value(getattr(echo, "status", ""))
        selected = getattr(compiler_result, "selected_meaning", None)
        frames = getattr(compiler_result, "frame_candidates", ())
        frame = frames[0] if type(frames) is tuple and len(frames) == 1 else None

        if type(frame) is FrameCandidate:
            construction_matched = (
                frame.grammar_rule_id == construction.grammar_rule_id
                and frame.frame_key == construction.frame_key
                and frame.speech_act == construction.speech_act
                and frame.purport == construction.purport
                and frame.predicate_key == construction.predicate_key
                and frame.predicate_ref == construction.predicate_ref
                and frame.negated is construction.negated
                and tuple(
                    binding.role_key for binding in frame.role_bindings
                )
                == construction.effective_role_keys
                and frame.complete is True
            )
        if not construction_matched:
            reasons.append("construction_contract_mismatch")

        if type(selected) is MeaningCandidate:
            observed_candidate_ref = selected.meaning_candidate_id
            observed_signature = selected.semantic_signature
            observed_role_keys = tuple(role.role_key for role in selected.roles)
            observed_concepts = tuple(
                sorted({role.concept_ref for role in selected.roles})
            )
            observed_senses = tuple(
                sorted({role.sense_ref for role in selected.roles})
            )
            semantic_identity_matched = (
                selected.meaning_candidate_id
                == fixture.expected_meaning_candidate_ref
                and selected.semantic_signature
                == fixture.expected_semantic_signature
                and selected.predicate_ref == fixture.expected_predicate_ref
                and selected.negated is fixture.expected_negated
                and selected.frame_candidate_ref
                == getattr(frame, "frame_candidate_id", "")
            )
            exact_reference_sets_matched = (
                observed_role_keys == fixture.expected_role_keys
                and observed_concepts == fixture.expected_concept_refs
                and observed_senses == fixture.expected_sense_refs
                and selected.relation_refs == fixture.expected_relation_refs
                and selected.all_gates_passed is True
                and selected.selection_authority is False
            )
        if not semantic_identity_matched:
            reasons.append("semantic_identity_replay_mismatch")
        if not exact_reference_sets_matched:
            reasons.append("exact_reference_set_replay_mismatch")

        if observed_status != fixture.expected_compiler_status:
            reasons.append("compiler_status_mismatch")
        if observed_echo_status != fixture.expected_echo_status:
            reasons.append("echo_status_mismatch")
        if echo is None or getattr(echo, "exact_signature_match", False) is not True:
            reasons.append("echo_signature_not_exact")
        if echo is not None and getattr(echo, "delivery_authorized", False) is not False:
            reasons.append("echo_delivery_boundary_open")
        wording = getattr(compiler_result, "candidate_wording", None)
        if wording is None:
            reasons.append("candidate_wording_missing")
        elif getattr(wording, "delivery_authorized", False) is not False:
            reasons.append("wording_delivery_boundary_open")

    passed = not reasons
    value = CharterReplayCaseResult(
        case_result_id="pending",
        fixture_ref=fixture.fixture_id,
        compiler_result_ref=compiler_result_ref,
        observed_meaning_candidate_ref=observed_candidate_ref,
        observed_semantic_signature=observed_signature,
        observed_compiler_status=observed_status,
        observed_echo_status=observed_echo_status,
        construction_matched=construction_matched,
        semantic_identity_matched=semantic_identity_matched,
        exact_reference_sets_matched=exact_reference_sets_matched,
        passed=passed,
        reason_codes=tuple(sorted(set(reasons))),
        operator_approval_granted=False,
        runtime_authority=False,
    )
    return replace(value, case_result_id=value.expected_id())


def replay_semantic_charter(
    charter: object = PROPOSED_SEMANTIC_CHARTER,
) -> CharterReplayResult:
    """Replay all eight exact fixtures without approving the proposal."""

    approved_shape = assert_valid_semantic_charter(charter)
    constructions = {
        item.construction_id: item for item in approved_shape.constructions
    }
    cases = tuple(
        _case_result(fixture, constructions[fixture.construction_ref])
        for fixture in approved_shape.replay_fixtures
    )
    passed = len(cases) == 8 and all(item.passed for item in cases)
    reasons = () if passed else ("one_or_more_semantic_replays_held",)
    value = CharterReplayResult(
        replay_id="pending",
        charter_ref=approved_shape.charter_id,
        status=(CharterReplayStatus.PASS if passed else CharterReplayStatus.HELD),
        case_results=cases,
        reason_codes=reasons,
        deterministic=True,
        validation_only=True,
        operator_approval_granted=False,
        charter_activated=False,
        filesystem_write_performed=False,
        memory_write_performed=False,
        route_registration_performed=False,
        tool_routing_performed=False,
        action_performed=False,
        delivery_performed=False,
    )
    return replace(value, replay_id=value.expected_id())


def evaluate_source_against_charter(
    source_text: object,
    charter: object = PROPOSED_SEMANTIC_CHARTER,
) -> CharterSourceEvaluation:
    """Classify one source against the proposal without activating it."""

    approved_shape = assert_valid_semantic_charter(charter)
    if type(source_text) is not str:
        value = CharterSourceEvaluation(
            evaluation_id="pending",
            charter_ref=approved_shape.charter_id,
            source_sha256="",
            disposition=CharterSourceDisposition.INVALID_INPUT,
            fixture_ref="",
            compiler_result_ref="",
            compiler_status="",
            compiler_reason_codes=("source_text_must_be_exact_text",),
            meaning_candidate_count=0,
            selected_meaning_ref="",
            proposed_match_only=False,
            operator_approval_granted=False,
            runtime_authority=False,
            memory_write_performed=False,
            action_performed=False,
            delivery_performed=False,
        )
        return replace(value, evaluation_id=value.expected_id())

    source_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    fixture = next(
        (
            item
            for item in approved_shape.replay_fixtures
            if item.exact_source_text == source_text
        ),
        None,
    )
    try:
        compiler_result = compile_meaning_preview(source_text)
    except Exception:
        compiler_result = None

    compiler_ref = str(getattr(compiler_result, "result_id", ""))
    compiler_status = _enum_value(getattr(compiler_result, "status", ""))
    compiler_reasons = tuple(getattr(compiler_result, "reasons", ()))
    meanings = getattr(compiler_result, "meaning_candidates", ())
    meaning_count = len(meanings) if type(meanings) is tuple else 0
    selected = getattr(compiler_result, "selected_meaning", None)
    selected_ref = (
        selected.meaning_candidate_id
        if type(selected) is MeaningCandidate
        else ""
    )

    if fixture is not None:
        construction = next(
            item
            for item in approved_shape.constructions
            if item.construction_id == fixture.construction_ref
        )
        case = _case_result(fixture, construction, compiler_result)
        disposition = (
            CharterSourceDisposition.MATCHED_PROPOSED_FIXTURE
            if case.passed
            else CharterSourceDisposition.HELD_REPLAY_MISMATCH
        )
        evaluation_reasons = case.reason_codes
    elif (
        compiler_result is not None
        and selected is None
        and meaning_count > 1
        and "ambiguous_meaning_requires_clarification" in compiler_reasons
    ):
        disposition = CharterSourceDisposition.HELD_AMBIGUOUS
        evaluation_reasons = compiler_reasons
    else:
        disposition = CharterSourceDisposition.OUTSIDE_PROPOSED_CHARTER
        evaluation_reasons = tuple(
            dict.fromkeys((*compiler_reasons, "exact_source_not_in_proposed_charter"))
        )

    value = CharterSourceEvaluation(
        evaluation_id="pending",
        charter_ref=approved_shape.charter_id,
        source_sha256=source_hash,
        disposition=disposition,
        fixture_ref=fixture.fixture_id if fixture is not None else "",
        compiler_result_ref=compiler_ref,
        compiler_status=compiler_status,
        compiler_reason_codes=evaluation_reasons,
        meaning_candidate_count=meaning_count,
        selected_meaning_ref=selected_ref,
        proposed_match_only=fixture is not None,
        operator_approval_granted=False,
        runtime_authority=False,
        memory_write_performed=False,
        action_performed=False,
        delivery_performed=False,
    )
    return replace(value, evaluation_id=value.expected_id())


__all__ = ("evaluate_source_against_charter", "replay_semantic_charter")
