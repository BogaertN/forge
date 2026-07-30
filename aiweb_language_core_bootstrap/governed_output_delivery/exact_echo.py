"""Exact symbolic decode and Echo for deterministic rendered candidates."""

from __future__ import annotations

from dataclasses import replace

from ..meaning_compiler_preview.compiler import compile_meaning_preview
from ..meaning_compiler_preview.schema import (
    LexicalCandidateKind,
    MeaningCompilerPreviewResult,
)
from ..meaning_compiler_preview.semantic_contract import (
    semantic_contract_for_candidate,
)
from ..operator_council.schema import OperatorCouncilResult
from .renderer import validate_rendered_output_candidate
from .schema import (
    CONTROLLED_RESTATEMENT_TRANSITION,
    DEFINITION_RESPONSE_TRANSITION,
    GOVERNED_OUTPUT_SCHEMA_VERSION,
    DecodedOutput,
    ExactEchoStatus,
    ExactOutputEcho,
    ExactSemanticRole,
    GovernedOutputManifest,
    GovernedOutputValidationError,
    RenderedOutputCandidate,
    pure_output_boundary,
)


def _semantic_roles(candidate: object) -> tuple[ExactSemanticRole, ...]:
    values: list[ExactSemanticRole] = []
    for role in candidate.roles:
        value = ExactSemanticRole(
            role_id="pending",
            role_key=role.role_key,
            concept_ref=role.concept_ref,
            sense_ref=role.sense_ref,
        )
        values.append(replace(value, role_id=value.expected_id()))
    return tuple(
        sorted(
            values,
            key=lambda item: (item.role_key, item.concept_ref, item.sense_ref),
        )
    )


def _decode_rendered_text(rendered_output: RenderedOutputCandidate) -> DecodedOutput:
    """Decode through the public compiler without trusting its final selection."""

    decoded_result = compile_meaning_preview(rendered_output.text)
    admitted = tuple(
        candidate
        for candidate in decoded_result.meaning_candidates
        if candidate.all_gates_passed
    )
    unknown_refs = tuple(
        sorted(
            {
                reference
                for lexical in decoded_result.lexical_candidates
                if lexical.kind is LexicalCandidateKind.UNKNOWN
                for reference in lexical.source_form_refs
            }
        )
    )
    decoded_candidate = admitted[0] if len(admitted) == 1 else None
    contract = None
    roles: tuple[ExactSemanticRole, ...] = ()
    relations: tuple[str, ...] = ()
    gates: tuple[str, ...] = ()
    candidate_unknowns: tuple[str, ...] = ()
    if decoded_candidate is not None:
        contract = semantic_contract_for_candidate(
            decoded_candidate,
            decoded_result.frame_candidates,
        )
        roles = _semantic_roles(decoded_candidate)
        relations = tuple(sorted(decoded_candidate.relation_refs))
        gates = tuple(gate.gate_id for gate in decoded_candidate.gates)
        candidate_unknowns = tuple(sorted(decoded_candidate.unknown_source_form_refs))
    all_unknowns = tuple(sorted(set(unknown_refs) | set(candidate_unknowns)))
    full_coverage = (
        decoded_candidate is not None
        and not all_unknowns
        and decoded_result.source_custody.source_preserved_exactly is True
        and decoded_result.source_custody.structural_progression_allowed is True
        and all(gate.passed is True for gate in decoded_candidate.gates)
    )
    value = DecodedOutput(
        decoded_output_id="pending",
        schema_version=GOVERNED_OUTPUT_SCHEMA_VERSION,
        rendered_output_ref=rendered_output.rendered_output_id,
        rendered_text_sha256=rendered_output.text_sha256,
        decoder_compiler_result_ref=decoded_result.result_id,
        decoder_source_custody_ref=decoded_result.source_custody.custody_result_id,
        admitted_candidate_count=len(admitted),
        decoded_meaning_ref=(
            decoded_candidate.meaning_candidate_id
            if decoded_candidate is not None
            else ""
        ),
        decoded_semantic_contract=contract,
        decoded_role_bindings=roles,
        decoded_relation_refs=relations,
        decoded_gate_refs=gates,
        unknown_source_form_refs=all_unknowns,
        unique_gate_admitted_decode=(decoded_candidate is not None),
        full_source_coverage=full_coverage,
        deterministic=True,
        boundary=pure_output_boundary(),
    )
    return replace(value, decoded_output_id=value.expected_id())


def _transition_admitted(
    manifest: GovernedOutputManifest,
    decoded: DecodedOutput,
) -> bool:
    source = manifest.source_semantic_contract
    actual = decoded.decoded_semantic_contract
    expected = manifest.expected_output_semantic_contract
    if actual is None:
        return False
    if manifest.transition_rule_ref == DEFINITION_RESPONSE_TRANSITION:
        return (
            source.speech_act == "definition_request"
            and source.purport == "request_provisional_definition"
            and expected.speech_act == "definition_response"
            and expected.purport == "provide_governed_provisional_definition"
            and expected.frame_key == "definition_response"
            and expected.grammar_rule_ref
            == "FORGE-GRAMMAR-V0-GOVERNED-DEFINITION-RESPONSE"
            and source.semantic_signature_ref == expected.semantic_signature_ref
            and source.negated is expected.negated
            and source.predicate_ref == expected.predicate_ref
            and actual == expected
        )
    if manifest.transition_rule_ref == CONTROLLED_RESTATEMENT_TRANSITION:
        return source == expected and actual == expected
    return False


def _expected_echo(
    rendered_output: RenderedOutputCandidate,
    manifest: GovernedOutputManifest,
) -> ExactOutputEcho:
    decoded = _decode_rendered_text(rendered_output)
    actual_contract = decoded.decoded_semantic_contract
    expected_contract = manifest.expected_output_semantic_contract
    contract_match = actual_contract == expected_contract
    role_match = (
        decoded.decoded_role_bindings
        == manifest.expected_output_role_bindings
    )
    relation_match = (
        decoded.decoded_relation_refs
        == manifest.expected_output_relation_refs
    )
    transition_ok = _transition_admitted(manifest, decoded)
    reasons: list[str] = []
    if not decoded.unique_gate_admitted_decode:
        reasons.append("decoded_meaning_not_unique")
    if not decoded.full_source_coverage:
        reasons.append("decoded_source_coverage_incomplete")
    if not contract_match:
        reasons.append("decoded_semantic_contract_mismatch")
    if not role_match:
        reasons.append("decoded_semantic_roles_mismatch")
    if not relation_match:
        reasons.append("decoded_semantic_relations_mismatch")
    if not transition_ok:
        reasons.append("output_transition_not_admitted")
    passed = not reasons
    if passed:
        reasons.append("exact_symbolic_transition_preserved")
    value = ExactOutputEcho(
        echo_id="pending",
        schema_version=GOVERNED_OUTPUT_SCHEMA_VERSION,
        status=ExactEchoStatus.PASS if passed else ExactEchoStatus.REJECT,
        reason_codes=tuple(reasons),
        manifest_ref=manifest.manifest_id,
        rendered_output_ref=rendered_output.rendered_output_id,
        decoded_output=decoded,
        source_semantic_contract_ref=(
            manifest.source_semantic_contract.semantic_contract_id
        ),
        expected_output_semantic_contract_ref=(
            expected_contract.semantic_contract_id
        ),
        decoded_output_semantic_contract_ref=(
            actual_contract.semantic_contract_id
            if actual_contract is not None
            else ""
        ),
        transition_rule_ref=manifest.transition_rule_ref,
        transition_admitted=transition_ok,
        exact_contract_match=contract_match,
        exact_role_match=role_match,
        exact_relation_match=relation_match,
        unique_decode=decoded.unique_gate_admitted_decode,
        full_source_coverage=decoded.full_source_coverage,
        answer_delivery_eligible=(
            passed and rendered_output.answer_delivery_eligible
        ),
        operator_approval_required=True,
        answer_delivery_authorized=False,
        answer_delivery_performed=False,
        boundary=pure_output_boundary(),
    )
    return replace(value, echo_id=value.expected_id())


def validate_exact_output_echo(
    echo: object,
    rendered_output: object,
    manifest: object,
    compiler_result: object,
    council_result: object,
) -> tuple[str, ...]:
    """Validate a full-contract Echo by rerendering and decoding again."""

    if type(echo) is not ExactOutputEcho:
        return ("exact_echo_type_not_admitted",)
    issues = list(
        validate_rendered_output_candidate(
            rendered_output,
            manifest,
            compiler_result,
            council_result,
        )
    )
    if issues:
        return tuple(issues)
    assert type(rendered_output) is RenderedOutputCandidate
    assert type(manifest) is GovernedOutputManifest
    assert type(compiler_result) is MeaningCompilerPreviewResult
    assert type(council_result) is OperatorCouncilResult
    if echo.echo_id != echo.expected_id():
        issues.append("exact_echo_content_identity_mismatch")
    try:
        expected = _expected_echo(rendered_output, manifest)
    except Exception:
        issues.append("exact_symbolic_decode_failed_closed")
        return tuple(dict.fromkeys(issues))
    if echo != expected:
        issues.append("exact_echo_not_exact_decode_projection")
    if echo.decoded_output.decoded_output_id != echo.decoded_output.expected_id():
        issues.append("decoded_output_content_identity_mismatch")
    if (
        echo.operator_approval_required is not True
        or echo.answer_delivery_authorized is not False
        or echo.answer_delivery_performed is not False
        or echo.boundary != pure_output_boundary()
        or echo.decoded_output.boundary != pure_output_boundary()
    ):
        issues.append("exact_echo_authority_boundary_invalid")
    if echo.answer_delivery_eligible is not (
        echo.status is ExactEchoStatus.PASS
        and rendered_output.answer_delivery_eligible
    ):
        issues.append("exact_echo_answer_eligibility_mismatch")
    return tuple(dict.fromkeys(issues))


def build_exact_output_echo(
    rendered_output: object,
    manifest: object,
    compiler_result: object,
    council_result: object,
) -> ExactOutputEcho:
    """Decode and compare one canonical renderer output without delivering it."""

    rendered_issues = validate_rendered_output_candidate(
        rendered_output,
        manifest,
        compiler_result,
        council_result,
    )
    if rendered_issues:
        raise GovernedOutputValidationError(rendered_issues)
    assert type(rendered_output) is RenderedOutputCandidate
    assert type(manifest) is GovernedOutputManifest
    echo = _expected_echo(rendered_output, manifest)
    issues = validate_exact_output_echo(
        echo,
        rendered_output,
        manifest,
        compiler_result,
        council_result,
    )
    if issues:
        raise GovernedOutputValidationError(issues)
    return echo


__all__ = (
    "build_exact_output_echo",
    "validate_exact_output_echo",
)
