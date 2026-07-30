"""Build one immutable output manifest from compiler, RMC, and Council evidence."""

from __future__ import annotations

from dataclasses import replace

from ..meaning_compiler_preview.compiler import compile_meaning_preview
from ..meaning_compiler_preview.registry import forge_seed_registry
from ..meaning_compiler_preview.schema import (
    CandidateWording,
    EchoStatus,
    MeaningCompilerPreviewResult,
    PreviewStatus,
)
from ..meaning_compiler_preview.semantic_contract import (
    build_semantic_contract_binding,
    semantic_contract_for_candidate,
)
from ..operator_council.council import convene_operator_council
from ..operator_council.schema import (
    CouncilDisposition,
    OperatorCouncilResult,
)
from .schema import (
    CONTROLLED_RESTATEMENT_TRANSITION,
    DEFINITION_RESPONSE_TRANSITION,
    GOVERNED_OUTPUT_SCHEMA_VERSION,
    ExactSemanticRole,
    GovernedOutputManifest,
    GovernedOutputValidationError,
    OutputPurpose,
    pure_output_boundary,
)


_DEFINITION_RESPONSE_SPEECH_ACT = "definition_response"
_DEFINITION_RESPONSE_PURPORT = "provide_governed_provisional_definition"
_DEFINITION_RESPONSE_FRAME = "definition_response"
_DEFINITION_RESPONSE_GRAMMAR_RULE = (
    "FORGE-GRAMMAR-V0-GOVERNED-DEFINITION-RESPONSE"
)


def _roles_for_candidate(candidate: object) -> tuple[ExactSemanticRole, ...]:
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


def _render_policy(selected: object) -> tuple[OutputPurpose, str, str]:
    if selected.speech_act == "definition_request":
        return (
            OutputPurpose.DEFINITION_ANSWER,
            "governed_provisional_definition",
            DEFINITION_RESPONSE_TRANSITION,
        )
    if selected.predicate_key == "compare":
        template = "comparison_request"
    elif selected.predicate_key == "be":
        template = "copula_statement"
    elif selected.speech_act == "request" and any(
        role.role_key == "actor" for role in selected.roles
    ):
        template = "modal_request"
    elif selected.speech_act == "request":
        template = "imperative_request"
    else:
        template = "simple_statement"
    return (
        OutputPurpose.CONTROLLED_RESTATEMENT_PREVIEW,
        template,
        CONTROLLED_RESTATEMENT_TRANSITION,
    )


def _expected_output_contract(selected: object, source_contract: object) -> object:
    if selected.speech_act != "definition_request":
        return source_contract
    return build_semantic_contract_binding(
        semantic_signature_ref=source_contract.semantic_signature_ref,
        speech_act=_DEFINITION_RESPONSE_SPEECH_ACT,
        purport=_DEFINITION_RESPONSE_PURPORT,
        negated=source_contract.negated,
        frame_key=_DEFINITION_RESPONSE_FRAME,
        grammar_rule_ref=_DEFINITION_RESPONSE_GRAMMAR_RULE,
        predicate_ref=source_contract.predicate_ref,
    )


def _adequate_resonances(
    result: MeaningCompilerPreviewResult,
    semantic_contract_ref: str,
) -> tuple[object, ...]:
    selected = result.selected_meaning
    if selected is None:
        return ()
    concepts = {role.concept_ref for role in selected.roles}
    relations = set(selected.relation_refs)
    predicate_relation = f"predicate:{selected.predicate_key}"
    return tuple(
        resonance
        for resonance in result.rmc_context.resonances
        if resonance.meaning_candidate_ref == selected.meaning_candidate_id
        and resonance.exact_semantic_contract_refs == (semantic_contract_ref,)
        and set(resonance.exact_concept_refs) == concepts
        and set(resonance.exact_relation_refs) == relations
        and predicate_relation in resonance.exact_relation_refs
    )


def _compiler_council_issues(
    compiler_result: object,
    council_result: object,
) -> tuple[str, ...]:
    issues: list[str] = []
    if type(compiler_result) is not MeaningCompilerPreviewResult:
        return ("compiler_result_type_not_admitted",)
    try:
        replayed = compile_meaning_preview(
            compiler_result.source_text,
            rmc_snapshot=compiler_result.rmc_context.snapshot,
        )
    except Exception:
        return ("compiler_result_replay_failed",)
    if replayed != compiler_result:
        return ("compiler_result_not_exact_deterministic_replay",)

    result = compiler_result
    selected = result.selected_meaning
    wording = result.candidate_wording
    if result.status is not PreviewStatus.PREVIEW_READY:
        issues.append("compiler_result_not_preview_ready")
    if selected is None:
        issues.append("compiler_selected_meaning_required")
    if type(wording) is not CandidateWording:
        issues.append("compiler_candidate_wording_required")
    if (
        result.echo.status is not EchoStatus.PASS
        or result.echo.exact_signature_match is not True
        or result.echo.reparse_performed is not True
    ):
        issues.append("compiler_preview_echo_not_passed")
    if (
        result.echo.delivery_authorized is not False
        or (wording is not None and wording.delivery_authorized is not False)
        or result.boundary.delivery_performed is not False
        or result.receipt.delivery_performed is not False
    ):
        issues.append("compiler_delivery_authority_enabled")
    if issues or selected is None or wording is None:
        return tuple(issues)

    try:
        source_contract = semantic_contract_for_candidate(
            selected,
            result.frame_candidates,
        )
    except Exception:
        return ("compiler_selected_semantic_contract_invalid",)
    adequate = _adequate_resonances(result, source_contract.semantic_contract_id)
    if not adequate:
        issues.append("compiler_selected_meaning_lacks_complete_exact_rmc_support")

    if type(council_result) is not OperatorCouncilResult:
        issues.append("council_result_type_not_admitted")
        return tuple(issues)
    try:
        council_replay = convene_operator_council(council_result.evidence)
    except Exception:
        issues.append("council_result_replay_failed")
        return tuple(issues)
    if council_replay != council_result:
        issues.append("council_result_not_exact_deterministic_replay")
        return tuple(issues)

    council = council_result
    evidence = council.evidence
    expected_concepts = tuple(sorted({role.concept_ref for role in selected.roles}))
    expected_authority = tuple(
        sorted((result.boundary.boundary_id, result.receipt.receipt_id))
    )
    exact_bindings = (
        evidence.selected_meaning_ref == selected.meaning_candidate_id,
        evidence.semantic_signature == selected.semantic_signature,
        evidence.speech_act == selected.speech_act,
        evidence.purport == selected.purport,
        evidence.predicate_ref == selected.predicate_ref,
        evidence.concept_refs == expected_concepts,
        evidence.relation_refs == tuple(sorted(selected.relation_refs)),
        evidence.ancestry_refs == tuple(sorted(selected.ancestry_refs)),
        evidence.gate_receipt_refs
        == tuple(sorted(gate.gate_id for gate in selected.gates)),
        evidence.gates_passed is True,
        evidence.echo_receipt_ref == result.echo.echo_id,
        evidence.echo_status == EchoStatus.PASS.value,
        evidence.rmc_snapshot_ref == result.rmc_context.snapshot.snapshot_id,
        evidence.rmc_connection_status
        == result.rmc_context.snapshot.connection_status,
        evidence.authority_evidence_refs == expected_authority,
        evidence.selected_meaning_validated is True,
        evidence.exact_reference_resonance_only is True,
        evidence.read_only is True,
    )
    if not all(exact_bindings):
        issues.append("council_evidence_not_exact_compiler_projection")
    if (
        evidence.selected_meaning_support_status != "EXACT_SUPPORT"
        or source_contract.semantic_contract_id not in evidence.rmc_evidence_refs
        or not {
            resonance.resonance_id for resonance in adequate
        }.issubset(set(evidence.rmc_evidence_refs))
    ):
        issues.append("council_exact_rmc_support_not_bound")
    if evidence.contradiction_refs or evidence.uncertainty_refs:
        issues.append("council_unresolved_evidence_present")
    recommendation = council.recommendation
    if (
        recommendation.disposition
        is not CouncilDisposition.RECOMMEND_FOR_OPERATOR_REVIEW
        or recommendation.recommendation_only is not True
        or recommendation.operator_decision_required is not True
        or recommendation.executable is not False
        or recommendation.authoritative is not False
        or recommendation.material_dissent_present is not False
        or council.dissents
    ):
        issues.append("council_did_not_issue_clean_review_recommendation")
    if (
        council.receipt.recommendation_only is not True
        or council.receipt.operator_decision_required is not True
        or council.receipt.council_decision_authorized is not False
        or council.receipt.delivery_performed is not False
        or council.boundary.delivery_authority is not False
        or council.boundary.delivery_performed is not False
    ):
        issues.append("council_authority_boundary_invalid")
    return tuple(dict.fromkeys(issues))


def _expected_manifest(
    compiler_result: MeaningCompilerPreviewResult,
    council_result: OperatorCouncilResult,
) -> GovernedOutputManifest:
    selected = compiler_result.selected_meaning
    wording = compiler_result.candidate_wording
    assert selected is not None and wording is not None
    source_contract = semantic_contract_for_candidate(
        selected,
        compiler_result.frame_candidates,
    )
    purpose, template, transition = _render_policy(selected)
    expected_contract = _expected_output_contract(selected, source_contract)
    roles = _roles_for_candidate(selected)
    adequate = _adequate_resonances(
        compiler_result,
        source_contract.semantic_contract_id,
    )
    value = GovernedOutputManifest(
        manifest_id="pending",
        schema_version=GOVERNED_OUTPUT_SCHEMA_VERSION,
        status="READY_FOR_RENDER_PREVIEW",
        output_purpose=purpose,
        compiler_result_ref=compiler_result.result_id,
        compiler_receipt_ref=compiler_result.receipt.receipt_id,
        source_custody_ref=compiler_result.source_custody.custody_result_id,
        source_sha256=compiler_result.source_custody.source_sha256,
        registry_ref=forge_seed_registry().registry_id,
        selected_meaning_ref=selected.meaning_candidate_id,
        source_semantic_contract=source_contract,
        source_role_bindings=roles,
        source_relation_refs=tuple(sorted(selected.relation_refs)),
        meaning_gate_refs=tuple(gate.gate_id for gate in selected.gates),
        rmc_evaluation_ref=compiler_result.rmc_context.evaluation_id,
        rmc_snapshot_ref=compiler_result.rmc_context.snapshot.snapshot_id,
        rmc_resonance_refs=tuple(
            sorted(resonance.resonance_id for resonance in adequate)
        ),
        compiler_candidate_wording_ref=wording.wording_id,
        compiler_echo_ref=compiler_result.echo.echo_id,
        algebra_trace_refs=tuple(
            step.trace_step_id for step in compiler_result.algebra_trace
        ),
        compiler_stage_refs=tuple(
            stage.stage_id for stage in compiler_result.stages
        ),
        council_result_ref=council_result.result_id,
        council_evidence_ref=council_result.evidence.envelope_id,
        council_recommendation_ref=(
            council_result.recommendation.recommendation_id
        ),
        council_receipt_ref=council_result.receipt.receipt_id,
        council_disposition=council_result.recommendation.disposition.value,
        render_template_key=template,
        transition_rule_ref=transition,
        expected_output_semantic_contract=expected_contract,
        expected_output_role_bindings=roles,
        expected_output_relation_refs=tuple(sorted(selected.relation_refs)),
        answer_delivery_eligible=(purpose is OutputPurpose.DEFINITION_ANSWER),
        operator_review_required=True,
        council_recommendation_only=True,
        preview_only=True,
        delivery_authorized=False,
        delivery_performed=False,
        boundary=pure_output_boundary(),
    )
    return replace(value, manifest_id=value.expected_id())


def validate_governed_output_manifest(
    manifest: object,
    compiler_result: object,
    council_result: object,
) -> tuple[str, ...]:
    """Validate the complete manifest by replay, never by trusting its hashes."""

    if type(manifest) is not GovernedOutputManifest:
        return ("manifest_type_not_admitted",)
    issues = list(_compiler_council_issues(compiler_result, council_result))
    if issues:
        return tuple(issues)
    assert type(compiler_result) is MeaningCompilerPreviewResult
    assert type(council_result) is OperatorCouncilResult
    if manifest.manifest_id != manifest.expected_id():
        issues.append("manifest_content_identity_mismatch")
    try:
        expected = _expected_manifest(compiler_result, council_result)
    except Exception:
        issues.append("manifest_exact_projection_failed_closed")
        return tuple(dict.fromkeys(issues))
    if manifest != expected:
        issues.append("manifest_not_exact_evidence_projection")
    boundary = manifest.boundary
    if boundary != pure_output_boundary():
        issues.append("manifest_pure_boundary_mismatch")
    if (
        manifest.operator_review_required is not True
        or manifest.council_recommendation_only is not True
        or manifest.preview_only is not True
        or manifest.delivery_authorized is not False
        or manifest.delivery_performed is not False
    ):
        issues.append("manifest_authority_boundary_invalid")
    expected_answer_eligibility = (
        manifest.output_purpose is OutputPurpose.DEFINITION_ANSWER
    )
    if manifest.answer_delivery_eligible is not expected_answer_eligibility:
        issues.append("manifest_answer_eligibility_mismatch")
    return tuple(dict.fromkeys(issues))


def build_governed_output_manifest(
    compiler_result: object,
    council_result: object,
) -> GovernedOutputManifest:
    """Build a render-preview manifest only from replayable exact evidence."""

    issues = _compiler_council_issues(compiler_result, council_result)
    if issues:
        raise GovernedOutputValidationError(issues)
    assert type(compiler_result) is MeaningCompilerPreviewResult
    assert type(council_result) is OperatorCouncilResult
    manifest = _expected_manifest(compiler_result, council_result)
    issues = validate_governed_output_manifest(
        manifest,
        compiler_result,
        council_result,
    )
    if issues:
        raise GovernedOutputValidationError(issues)
    return manifest


__all__ = (
    "build_governed_output_manifest",
    "validate_governed_output_manifest",
)
