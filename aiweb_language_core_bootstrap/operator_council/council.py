"""Pure deterministic deliberation for the recommendation-only Council."""

from __future__ import annotations

from dataclasses import replace
import hashlib

from ..schema import canonical_json
from .schema import (
    CouncilDisposition,
    CouncilDissent,
    CouncilMemberPosition,
    CouncilRecommendation,
    CouncilRole,
    CouncilStance,
    OperatorCouncilBoundary,
    OperatorCouncilDecisionReceipt,
    OperatorCouncilResult,
    SemanticRmcEvidenceEnvelope,
)
from .validation import coerce_evidence_envelope, validate_result_identities


_PARTICIPANT_ROLES = (
    CouncilRole.SEMANTIC_STEWARD,
    CouncilRole.RMC_WITNESS,
    CouncilRole.AUTHORITY_AUDITOR,
    CouncilRole.ADVERSARIAL_CHALLENGER,
    CouncilRole.SYNTHESIZER,
)
_MANDATORY_ROLES = frozenset(_PARTICIPANT_ROLES[:-1])
_QUORUM_THRESHOLD = 4
_CONCURRENCE_THRESHOLD = 4


def _position(
    *,
    evidence: SemanticRmcEvidenceEnvelope,
    role: CouncilRole,
    stance: CouncilStance,
    evidence_refs: tuple[str, ...],
    reason_codes: tuple[str, ...],
) -> CouncilMemberPosition:
    value = CouncilMemberPosition(
        position_id="pending",
        envelope_ref=evidence.envelope_id,
        role=role,
        stance=stance,
        evidence_refs=tuple(sorted(set(evidence_refs))),
        reason_codes=tuple(sorted(set(reason_codes))),
        material_dissent=stance is not CouncilStance.SUPPORT,
        independent_evaluation=True,
        recommendation_only=True,
        decision_authority=False,
    )
    return replace(value, position_id=value.expected_id())


def _semantic_steward_position(
    evidence: SemanticRmcEvidenceEnvelope,
) -> CouncilMemberPosition:
    reasons: list[str] = []
    if evidence.selected_meaning_validated is not True:
        reasons.append("selected_meaning_not_validated")
    if evidence.gates_passed is not True:
        reasons.append("semantic_gates_not_passed")
    if evidence.echo_status != "PASS":
        reasons.append("echo_not_passed")
    stance = CouncilStance.HOLD if reasons else CouncilStance.SUPPORT
    if not reasons:
        reasons.append("selected_semantic_meaning_supported")
    return _position(
        evidence=evidence,
        role=CouncilRole.SEMANTIC_STEWARD,
        stance=stance,
        evidence_refs=(
            evidence.selected_meaning_ref,
            evidence.semantic_signature,
            evidence.predicate_ref,
            evidence.echo_receipt_ref,
            *evidence.concept_refs,
            *evidence.relation_refs,
            *evidence.ancestry_refs,
            *evidence.gate_receipt_refs,
        ),
        reason_codes=tuple(reasons),
    )


def _rmc_witness_position(
    evidence: SemanticRmcEvidenceEnvelope,
) -> CouncilMemberPosition:
    if evidence.selected_meaning_support_status == "EXACT_SUPPORT":
        stance = CouncilStance.SUPPORT
        reasons = ("adequate_exact_reference_rmc_evidence_witnessed",)
    elif evidence.rmc_connection_status == "CONNECTED_STRUCTURED":
        stance = CouncilStance.HOLD
        reasons = ("rmc_structured_without_adequate_selected_meaning_support",)
    else:
        stance = CouncilStance.HOLD
        reasons = ("rmc_connected_empty",)
    return _position(
        evidence=evidence,
        role=CouncilRole.RMC_WITNESS,
        stance=stance,
        evidence_refs=(evidence.rmc_snapshot_ref, *evidence.rmc_evidence_refs),
        reason_codes=reasons,
    )


def _authority_auditor_position(
    evidence: SemanticRmcEvidenceEnvelope,
) -> CouncilMemberPosition:
    # Admission has already rejected every authority-bearing or side-effect
    # request.  This member witnesses that closed boundary independently.
    return _position(
        evidence=evidence,
        role=CouncilRole.AUTHORITY_AUDITOR,
        stance=CouncilStance.SUPPORT,
        evidence_refs=evidence.authority_evidence_refs,
        reason_codes=("authority_boundary_closed",),
    )


def _adversarial_challenger_position(
    evidence: SemanticRmcEvidenceEnvelope,
) -> CouncilMemberPosition:
    reasons: list[str] = []
    if evidence.contradiction_refs:
        reasons.append("contradiction_evidence_present")
    if evidence.uncertainty_refs:
        reasons.append("unresolved_uncertainty_present")
    if evidence.selected_meaning_validated is not True:
        reasons.append("selected_meaning_not_validated")
    if evidence.gates_passed is not True:
        reasons.append("semantic_gates_not_passed")
    if evidence.echo_status != "PASS":
        reasons.append("echo_not_passed")
    if evidence.selected_meaning_support_status != "EXACT_SUPPORT":
        reasons.append("rmc_support_absent")
    if evidence.contradiction_refs:
        stance = CouncilStance.OPPOSE
    elif reasons:
        stance = CouncilStance.HOLD
    else:
        stance = CouncilStance.SUPPORT
        reasons.append("no_adversarial_defect_found")
    return _position(
        evidence=evidence,
        role=CouncilRole.ADVERSARIAL_CHALLENGER,
        stance=stance,
        evidence_refs=(
            evidence.selected_meaning_ref,
            evidence.echo_receipt_ref,
            evidence.rmc_snapshot_ref,
            *evidence.gate_receipt_refs,
            *evidence.contradiction_refs,
            *evidence.uncertainty_refs,
        ),
        reason_codes=tuple(reasons),
    )


def _synthesizer_position(
    evidence: SemanticRmcEvidenceEnvelope,
    independent_positions: tuple[CouncilMemberPosition, ...],
) -> CouncilMemberPosition:
    stances = tuple(item.stance for item in independent_positions)
    if CouncilStance.OPPOSE in stances:
        stance = CouncilStance.HOLD
        reasons = ("member_opposition_requires_operator_review",)
    elif all(item is CouncilStance.SUPPORT for item in stances):
        stance = CouncilStance.SUPPORT
        reasons = ("independent_positions_converged",)
    else:
        stance = CouncilStance.HOLD
        reasons = ("member_hold_requires_more_evidence",)
    return _position(
        evidence=evidence,
        role=CouncilRole.SYNTHESIZER,
        stance=stance,
        evidence_refs=tuple(item.position_id for item in independent_positions),
        reason_codes=reasons,
    )


def _build_dissents(
    positions: tuple[CouncilMemberPosition, ...],
) -> tuple[CouncilDissent, ...]:
    values: list[CouncilDissent] = []
    for position in positions:
        if position.stance is CouncilStance.SUPPORT:
            continue
        value = CouncilDissent(
            dissent_id="pending",
            position_ref=position.position_id,
            role=position.role,
            severity=(
                "MATERIAL"
                if position.stance is CouncilStance.OPPOSE
                else "UNRESOLVED"
            ),
            reason_codes=position.reason_codes,
            evidence_refs=position.evidence_refs,
            resolved=False,
            blocks_recommendation=True,
        )
        values.append(replace(value, dissent_id=value.expected_id()))
    return tuple(values)


def _build_recommendation(
    evidence: SemanticRmcEvidenceEnvelope,
    positions: tuple[CouncilMemberPosition, ...],
    dissents: tuple[CouncilDissent, ...],
) -> CouncilRecommendation:
    support_roles = tuple(
        item.role for item in positions if item.stance is CouncilStance.SUPPORT
    )
    hold_roles = tuple(
        item.role for item in positions if item.stance is CouncilStance.HOLD
    )
    oppose_roles = tuple(
        item.role for item in positions if item.stance is CouncilStance.OPPOSE
    )
    participant_roles = tuple(item.role for item in positions)
    quorum_reached = len(participant_roles) >= _QUORUM_THRESHOLD
    concurrence_reached = len(support_roles) >= _CONCURRENCE_THRESHOLD
    mandatory_roles_satisfied = _MANDATORY_ROLES.issubset(support_roles)
    material_dissent_present = bool(dissents)
    may_recommend = (
        quorum_reached
        and concurrence_reached
        and mandatory_roles_satisfied
        and not material_dissent_present
    )
    if may_recommend:
        disposition = CouncilDisposition.RECOMMEND_FOR_OPERATOR_REVIEW
        reasons = (
            "deterministic_council_concurrence_reached",
            "operator_decision_still_required",
        )
    else:
        disposition = CouncilDisposition.HOLD_FOR_EVIDENCE
        reasons = tuple(
            sorted(
                {
                    "evidence_hold",
                    "operator_review_required",
                    *(reason for dissent in dissents for reason in dissent.reason_codes),
                }
            )
        )
    value = CouncilRecommendation(
        recommendation_id="pending",
        envelope_ref=evidence.envelope_id,
        disposition=disposition,
        participant_roles=participant_roles,
        support_roles=support_roles,
        hold_roles=hold_roles,
        oppose_roles=oppose_roles,
        quorum_threshold=_QUORUM_THRESHOLD,
        participant_count=len(participant_roles),
        quorum_reached=quorum_reached,
        concurrence_threshold=_CONCURRENCE_THRESHOLD,
        support_count=len(support_roles),
        concurrence_reached=concurrence_reached,
        mandatory_roles_satisfied=mandatory_roles_satisfied,
        material_dissent_present=material_dissent_present,
        reason_codes=reasons,
        recommendation_only=True,
        operator_decision_required=True,
        executable=False,
        authoritative=False,
    )
    return replace(value, recommendation_id=value.expected_id())


def _build_boundary() -> OperatorCouncilBoundary:
    value = OperatorCouncilBoundary(
        boundary_id="pending",
        deterministic=True,
        recommendation_only=True,
        selected_semantic_evidence_only=True,
        raw_text_accepted=False,
        tokenization_performed=False,
        model_called=False,
        embedding_used=False,
        vector_used=False,
        similarity_scoring_used=False,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        environment_access_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        tool_routing_performed=False,
        action_performed=False,
        delivery_performed=False,
        truth_authority=False,
        evidence_authority=False,
        permission_authority=False,
        decision_authority=False,
        tool_authority=False,
        action_authority=False,
        delivery_authority=False,
        memory_write_authority=False,
    )
    return replace(value, boundary_id=value.expected_id())


def _result_digest(
    *,
    evidence: SemanticRmcEvidenceEnvelope,
    positions: tuple[CouncilMemberPosition, ...],
    dissents: tuple[CouncilDissent, ...],
    recommendation: CouncilRecommendation,
    boundary: OperatorCouncilBoundary,
) -> str:
    payload = {
        "envelope_ref": evidence.envelope_id,
        "position_refs": tuple(item.position_id for item in positions),
        "dissent_refs": tuple(item.dissent_id for item in dissents),
        "recommendation_ref": recommendation.recommendation_id,
        "boundary_ref": boundary.boundary_id,
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _build_receipt(
    *,
    evidence: SemanticRmcEvidenceEnvelope,
    positions: tuple[CouncilMemberPosition, ...],
    dissents: tuple[CouncilDissent, ...],
    recommendation: CouncilRecommendation,
    boundary: OperatorCouncilBoundary,
) -> OperatorCouncilDecisionReceipt:
    value = OperatorCouncilDecisionReceipt(
        receipt_id="pending",
        result_digest=_result_digest(
            evidence=evidence,
            positions=positions,
            dissents=dissents,
            recommendation=recommendation,
            boundary=boundary,
        ),
        envelope_ref=evidence.envelope_id,
        recommendation_ref=recommendation.recommendation_id,
        position_refs=tuple(item.position_id for item in positions),
        dissent_refs=tuple(item.dissent_id for item in dissents),
        decision_kind="recommendation_only_disposition",
        deterministic=True,
        input_validated=True,
        output_validated=True,
        recommendation_only=True,
        operator_decision_required=True,
        council_decision_authorized=False,
        writes_performed=False,
        tools_invoked=False,
        action_performed=False,
        delivery_performed=False,
    )
    return replace(value, receipt_id=value.expected_id())


def _validate_contract(result: OperatorCouncilResult) -> tuple[str, ...]:
    issues = list(validate_result_identities(result))
    if tuple(item.role for item in result.positions) != _PARTICIPANT_ROLES:
        issues.append("result:role_order_or_membership_invalid")
    if len({item.role for item in result.positions}) != len(_PARTICIPANT_ROLES):
        issues.append("result:duplicate_council_role")
    if result.recommendation.recommendation_only is not True:
        issues.append("result:recommendation_only_not_preserved")
    if result.recommendation.operator_decision_required is not True:
        issues.append("result:operator_decision_not_required")
    if result.recommendation.executable or result.recommendation.authoritative:
        issues.append("result:recommendation_gained_authority")
    boundary = result.boundary
    forbidden_boundary_true = (
        boundary.raw_text_accepted,
        boundary.tokenization_performed,
        boundary.model_called,
        boundary.embedding_used,
        boundary.vector_used,
        boundary.similarity_scoring_used,
        boundary.filesystem_read_performed,
        boundary.filesystem_write_performed,
        boundary.network_access_performed,
        boundary.environment_access_performed,
        boundary.memory_read_performed,
        boundary.memory_write_performed,
        boundary.tool_routing_performed,
        boundary.action_performed,
        boundary.delivery_performed,
        boundary.truth_authority,
        boundary.evidence_authority,
        boundary.permission_authority,
        boundary.decision_authority,
        boundary.tool_authority,
        boundary.action_authority,
        boundary.delivery_authority,
        boundary.memory_write_authority,
    )
    if any(forbidden_boundary_true):
        issues.append("result:forbidden_boundary_capability_enabled")
    receipt = result.receipt
    if (
        receipt.council_decision_authorized
        or receipt.writes_performed
        or receipt.tools_invoked
        or receipt.action_performed
        or receipt.delivery_performed
    ):
        issues.append("result:receipt_records_forbidden_side_effect")
    return tuple(issues)


def convene_operator_council(
    evidence_envelope: object,
) -> OperatorCouncilResult:
    """Return a deterministic recommendation from admitted semantic evidence.

    This is the sole adapter entry point.  It performs no parsing, model call,
    retrieval, I/O, tool invocation, action, delivery, or memory write.
    Invalid or authority-bearing envelopes raise ``CouncilValidationError``
    before any Council position is constructed.
    """

    evidence = coerce_evidence_envelope(evidence_envelope)
    independent = (
        _semantic_steward_position(evidence),
        _rmc_witness_position(evidence),
        _authority_auditor_position(evidence),
        _adversarial_challenger_position(evidence),
    )
    positions = (*independent, _synthesizer_position(evidence, independent))
    dissents = _build_dissents(positions)
    recommendation = _build_recommendation(evidence, positions, dissents)
    boundary = _build_boundary()
    receipt = _build_receipt(
        evidence=evidence,
        positions=positions,
        dissents=dissents,
        recommendation=recommendation,
        boundary=boundary,
    )
    result = OperatorCouncilResult(
        result_id="pending",
        evidence=evidence,
        positions=positions,
        dissents=dissents,
        recommendation=recommendation,
        boundary=boundary,
        receipt=receipt,
    )
    result = replace(result, result_id=result.expected_id())
    issues = _validate_contract(result)
    if issues:
        raise RuntimeError("operator_council_output_invalid:" + ";".join(issues))
    return result


__all__ = ("convene_operator_council",)
