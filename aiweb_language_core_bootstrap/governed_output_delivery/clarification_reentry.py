"""Governed ordinary-language clarification re-entry and immutable receipts."""

from __future__ import annotations

from dataclasses import replace

from ..meaning_compiler_preview.clarification import (
    GovernedClarificationRequest,
    validate_governed_clarification_request,
)
from ..meaning_compiler_preview.compiler import compile_meaning_preview
from ..meaning_compiler_preview.schema import (
    EchoStatus,
    MeaningCompilerPreviewResult,
    PreviewStatus,
)
from ..meaning_compiler_preview.semantic_contract import (
    semantic_contract_for_candidate,
)
from .schema import (
    GOVERNED_OUTPUT_SCHEMA_VERSION,
    ClarificationReentryReceipt,
    ClarificationReentryResult,
    ClarificationReentryStatus,
    GovernedOutputValidationError,
    pure_output_boundary,
)


def _option_role_key(option: object) -> tuple[tuple[str, str, str], ...]:
    return tuple(
        sorted(
            (
                role.role_key,
                role.concept_ref,
                role.sense_ref,
            )
            for role in option.roles
        )
    )


def _candidate_role_key(candidate: object) -> tuple[tuple[str, str, str], ...]:
    return tuple(
        sorted(
            (
                role.role_key,
                role.concept_ref,
                role.sense_ref,
            )
            for role in candidate.roles
        )
    )


def _clarified_result_issues(
    clarified_result: object,
    original_result: MeaningCompilerPreviewResult,
) -> tuple[str, ...]:
    if type(clarified_result) is not MeaningCompilerPreviewResult:
        return ("clarified_compiler_result_type_not_admitted",)
    try:
        replayed = compile_meaning_preview(
            clarified_result.source_text,
            rmc_snapshot=original_result.rmc_context.snapshot,
        )
    except Exception:
        return ("clarified_compiler_result_replay_failed",)
    if replayed != clarified_result:
        return ("clarified_compiler_result_not_exact_replay",)
    if (
        clarified_result.rmc_context.snapshot.snapshot_id
        != original_result.rmc_context.snapshot.snapshot_id
    ):
        return ("clarified_rmc_snapshot_changed",)
    return ()


def _matching_options(
    request: GovernedClarificationRequest,
    clarified_result: MeaningCompilerPreviewResult,
) -> tuple[object, ...]:
    selected = clarified_result.selected_meaning
    if selected is None:
        return ()
    contract = semantic_contract_for_candidate(
        selected,
        clarified_result.frame_candidates,
    )
    role_key = _candidate_role_key(selected)
    return tuple(
        option
        for option in request.options
        if option.semantic_contract_ref == contract.semantic_contract_id
        and option.semantic_signature_ref == selected.semantic_signature
        and _option_role_key(option) == role_key
    )


def _reentry_disposition(
    request: GovernedClarificationRequest,
    clarified_result: MeaningCompilerPreviewResult,
) -> tuple[ClarificationReentryStatus, tuple[str, ...], object | None]:
    admitted = tuple(
        candidate
        for candidate in clarified_result.meaning_candidates
        if candidate.all_gates_passed
    )
    if (
        clarified_result.status is not PreviewStatus.PREVIEW_READY
        or clarified_result.selected_meaning is None
        or clarified_result.echo.status is not EchoStatus.PASS
    ):
        return (
            ClarificationReentryStatus.HELD,
            ("clarified_meaning_not_preview_ready",),
            None,
        )
    if len(admitted) != 1 or admitted[0] != clarified_result.selected_meaning:
        return (
            ClarificationReentryStatus.HELD,
            ("clarified_meaning_not_unique_gate_admitted",),
            None,
        )
    matches = _matching_options(request, clarified_result)
    if not matches:
        return (
            ClarificationReentryStatus.HELD,
            ("clarified_meaning_not_original_alternative",),
            None,
        )
    if len(matches) != 1:
        return (
            ClarificationReentryStatus.HELD,
            ("clarified_meaning_matches_multiple_original_alternatives",),
            None,
        )
    return (
        ClarificationReentryStatus.ACCEPTED,
        ("clarified_meaning_matches_one_original_alternative",),
        matches[0],
    )


def _expected_receipt(
    original_result: MeaningCompilerPreviewResult,
    request: GovernedClarificationRequest,
    clarified_result: MeaningCompilerPreviewResult,
    matched_option: object,
) -> ClarificationReentryReceipt:
    selected = clarified_result.selected_meaning
    assert selected is not None
    contract = semantic_contract_for_candidate(
        selected,
        clarified_result.frame_candidates,
    )
    value = ClarificationReentryReceipt(
        receipt_id="pending",
        schema_version=GOVERNED_OUTPUT_SCHEMA_VERSION,
        status="CLARIFICATION_REENTRY_ACCEPTED",
        clarification_request_ref=request.clarification_request_id,
        original_compiler_result_ref=original_result.result_id,
        original_compiler_receipt_ref=original_result.receipt.receipt_id,
        original_source_custody_ref=(
            original_result.source_custody.custody_result_id
        ),
        original_source_sha256=original_result.source_custody.source_sha256,
        original_rmc_evaluation_ref=original_result.rmc_context.evaluation_id,
        original_rmc_snapshot_ref=(
            original_result.rmc_context.snapshot.snapshot_id
        ),
        original_option_refs=tuple(option.option_id for option in request.options),
        original_alternative_meaning_refs=(
            request.alternative_meaning_refs
        ),
        original_alternative_semantic_contract_refs=tuple(
            option.semantic_contract_ref for option in request.options
        ),
        clarified_compiler_result_ref=clarified_result.result_id,
        clarified_compiler_receipt_ref=clarified_result.receipt.receipt_id,
        clarified_source_custody_ref=(
            clarified_result.source_custody.custody_result_id
        ),
        clarified_source_sha256=clarified_result.source_custody.source_sha256,
        clarified_rmc_evaluation_ref=clarified_result.rmc_context.evaluation_id,
        clarified_rmc_snapshot_ref=(
            clarified_result.rmc_context.snapshot.snapshot_id
        ),
        clarified_selected_meaning_ref=selected.meaning_candidate_id,
        matched_option_ref=matched_option.option_id,
        matched_original_meaning_ref=matched_option.meaning_candidate_ref,
        matched_semantic_contract_ref=contract.semantic_contract_id,
        all_original_alternatives_preserved=True,
        clarification_response_consumed=True,
        compiler_selection_performed=True,
        operator_option_selection_performed=False,
        answer_delivery_authorized=False,
        answer_delivery_performed=False,
        action_performed=False,
        tool_routing_performed=False,
        memory_write_performed=False,
        boundary=pure_output_boundary(),
    )
    return replace(value, receipt_id=value.expected_id())


def validate_clarification_reentry_receipt(
    receipt: object,
    original_result: object,
    clarification_request: object,
    clarified_result: object,
) -> tuple[str, ...]:
    """Replay both compiler results and require one exact original alternative."""

    if type(receipt) is not ClarificationReentryReceipt:
        return ("clarification_reentry_receipt_type_not_admitted",)
    if type(original_result) is not MeaningCompilerPreviewResult:
        return ("original_compiler_result_type_not_admitted",)
    if type(clarification_request) is not GovernedClarificationRequest:
        return ("clarification_request_type_not_admitted",)
    issues = list(
        validate_governed_clarification_request(
            clarification_request,
            original_result,
        )
    )
    if issues:
        return tuple(issues)
    issues.extend(_clarified_result_issues(clarified_result, original_result))
    if issues:
        return tuple(dict.fromkeys(issues))
    assert type(clarified_result) is MeaningCompilerPreviewResult
    status, _reasons, matched = _reentry_disposition(
        clarification_request,
        clarified_result,
    )
    if status is not ClarificationReentryStatus.ACCEPTED or matched is None:
        issues.append("clarified_result_not_receipt_eligible")
        return tuple(dict.fromkeys(issues))
    if receipt.receipt_id != receipt.expected_id():
        issues.append("clarification_reentry_receipt_identity_mismatch")
    try:
        expected = _expected_receipt(
            original_result,
            clarification_request,
            clarified_result,
            matched,
        )
    except Exception:
        issues.append("clarification_reentry_receipt_projection_failed_closed")
        return tuple(dict.fromkeys(issues))
    if receipt != expected:
        issues.append("clarification_reentry_receipt_not_exact_projection")
    if (
        receipt.all_original_alternatives_preserved is not True
        or receipt.clarification_response_consumed is not True
        or receipt.compiler_selection_performed is not True
        or receipt.operator_option_selection_performed is not False
        or receipt.answer_delivery_authorized is not False
        or receipt.answer_delivery_performed is not False
        or receipt.action_performed is not False
        or receipt.tool_routing_performed is not False
        or receipt.memory_write_performed is not False
        or receipt.boundary != pure_output_boundary()
    ):
        issues.append("clarification_reentry_receipt_authority_boundary_invalid")
    return tuple(dict.fromkeys(issues))


def validate_clarification_reentry_result(
    result: object,
    original_result: object,
    clarification_request: object,
) -> tuple[str, ...]:
    if type(result) is not ClarificationReentryResult:
        return ("clarification_reentry_result_type_not_admitted",)
    if type(original_result) is not MeaningCompilerPreviewResult:
        return ("original_compiler_result_type_not_admitted",)
    if type(clarification_request) is not GovernedClarificationRequest:
        return ("clarification_request_type_not_admitted",)
    issues = list(
        validate_governed_clarification_request(
            clarification_request,
            original_result,
        )
    )
    issues.extend(
        _clarified_result_issues(
            result.clarified_compiler_result,
            original_result,
        )
    )
    if issues:
        return tuple(dict.fromkeys(issues))
    status, reasons, matched = _reentry_disposition(
        clarification_request,
        result.clarified_compiler_result,
    )
    if result.result_id != result.expected_id():
        issues.append("clarification_reentry_result_identity_mismatch")
    if result.status is not status or result.reason_codes != reasons:
        issues.append("clarification_reentry_disposition_mismatch")
    if result.clarification_request_ref != clarification_request.clarification_request_id:
        issues.append("clarification_reentry_request_binding_mismatch")
    if status is ClarificationReentryStatus.ACCEPTED:
        if result.receipt is None or matched is None:
            issues.append("accepted_clarification_reentry_receipt_required")
        else:
            issues.extend(
                validate_clarification_reentry_receipt(
                    result.receipt,
                    original_result,
                    clarification_request,
                    result.clarified_compiler_result,
                )
            )
    elif result.receipt is not None:
        issues.append("held_clarification_reentry_receipt_forbidden")
    expected_selection = status is ClarificationReentryStatus.ACCEPTED
    if (
        result.live_clarification_session_started is not True
        or result.clarification_response_consumed is not True
        or result.compiler_selection_performed is not expected_selection
        or result.operator_option_selection_performed is not False
        or result.answer_delivery_authorized is not False
        or result.answer_delivery_performed is not False
        or result.action_performed is not False
        or result.tool_routing_performed is not False
        or result.memory_write_performed is not False
        or result.boundary != pure_output_boundary()
    ):
        issues.append("clarification_reentry_result_authority_boundary_invalid")
    return tuple(dict.fromkeys(issues))


def build_clarification_reentry(
    original_result: object,
    clarification_request: object,
    clarified_source_text: object,
) -> ClarificationReentryResult:
    """Recompile a new complete source; never consume an option ID as meaning."""

    if type(original_result) is not MeaningCompilerPreviewResult:
        raise GovernedOutputValidationError(
            ("original_compiler_result_type_not_admitted",)
        )
    if type(clarification_request) is not GovernedClarificationRequest:
        raise GovernedOutputValidationError(
            ("clarification_request_type_not_admitted",)
        )
    original_issues = validate_governed_clarification_request(
        clarification_request,
        original_result,
    )
    if original_issues:
        raise GovernedOutputValidationError(original_issues)
    if type(clarified_source_text) is not str:
        raise GovernedOutputValidationError(
            ("clarified_source_text_must_be_exact_text",)
        )
    clarified_result = compile_meaning_preview(
        clarified_source_text,
        rmc_snapshot=original_result.rmc_context.snapshot,
    )
    clarified_issues = _clarified_result_issues(
        clarified_result,
        original_result,
    )
    if clarified_issues:
        raise GovernedOutputValidationError(clarified_issues)
    status, reasons, matched = _reentry_disposition(
        clarification_request,
        clarified_result,
    )
    receipt = (
        _expected_receipt(
            original_result,
            clarification_request,
            clarified_result,
            matched,
        )
        if status is ClarificationReentryStatus.ACCEPTED and matched is not None
        else None
    )
    value = ClarificationReentryResult(
        result_id="pending",
        schema_version=GOVERNED_OUTPUT_SCHEMA_VERSION,
        status=status,
        reason_codes=reasons,
        clarification_request_ref=(
            clarification_request.clarification_request_id
        ),
        clarified_compiler_result=clarified_result,
        receipt=receipt,
        live_clarification_session_started=True,
        clarification_response_consumed=True,
        compiler_selection_performed=(
            status is ClarificationReentryStatus.ACCEPTED
        ),
        operator_option_selection_performed=False,
        answer_delivery_authorized=False,
        answer_delivery_performed=False,
        action_performed=False,
        tool_routing_performed=False,
        memory_write_performed=False,
        boundary=pure_output_boundary(),
    )
    result = replace(value, result_id=value.expected_id())
    issues = validate_clarification_reentry_result(
        result,
        original_result,
        clarification_request,
    )
    if issues:
        raise GovernedOutputValidationError(issues)
    return result


__all__ = (
    "build_clarification_reentry",
    "validate_clarification_reentry_receipt",
    "validate_clarification_reentry_result",
)
