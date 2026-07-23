"""Explicit bounded adapter to the unchanged accepted GP-014 lane."""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from typing import Any

from .authority import (
    ADAPTER_SCOPE,
    GP014_ALLOWED_SOURCE_STATUSES,
    GP014_SUPPORTED_OPERATION_FAMILIES,
    REQUESTED_OPERATION,
    STATUS_COMPLETED_ANSWERED,
    STATUS_COMPLETED_CONTAINED,
    STATUS_CONTAINED_SOURCE_FAILURE,
    STATUS_HELD_GP014_IDENTITY,
    STATUS_HELD_GP014_RESULT,
    STATUS_HELD_INVALID_REQUEST,
    STATUS_HELD_INVALID_STATE,
    STATUS_REFUSED_DISABLED,
)
from .bindings import load_gp014_runtime_binding
from .canonical import question_sha256, stable_identifier
from .schema import Gp014AdapterReceipt, Gp014AdapterRequest, Gp014AdapterResult, Gp014AdapterState
from .validation import validate_request, validate_result, validate_state


def build_gp014_adapter_state(*, explicit_offline_developer_enable: bool = False) -> Gp014AdapterState:
    enabled = explicit_offline_developer_enable is True
    value = Gp014AdapterState(
        state_id="pending",
        enabled=enabled,
        explicit_offline_developer_enable=enabled,
        disabled_by_default=True,
        explicit_invocation_required=True,
        exact_question_forwarding_required=True,
        unchanged_gp014_required=True,
        existing_gp014_scope_only=True,
        deterministic=True,
        local_only=True,
        adapter_read_only=True,
        adapter_in_memory_only=True,
        runtime_registration_allowed=False,
        main_registration_allowed=False,
        route_allowed=False,
        api_allowed=False,
        ui_allowed=False,
        network_authority_added=False,
        filesystem_write_authority_added=False,
        memory_authority_added=False,
        evidence_authority_added=False,
        truth_authority_added=False,
        permission_authority_added=False,
        delivery_authority_added=False,
        tool_authority_added=False,
        action_authority_added=False,
        external_resource_authority_added=False,
        gp014_import_allowed=enabled,
        gp014_call_allowed=enabled,
        gp014_modification_allowed=False,
        gp014_supersession_allowed=False,
        gp015_reuse_allowed=False,
        production_ready=False,
        release_authorized=False,
    )
    return replace(value, state_id=value.expected_id())


def build_gp014_adapter_request(question: str) -> Gp014AdapterRequest:
    if not isinstance(question, str):
        raise TypeError("question must be text")
    value = Gp014AdapterRequest(
        request_id="pending",
        question=question,
        question_sha256=question_sha256(question),
        requested_operation=REQUESTED_OPERATION,
        adapter_scope=ADAPTER_SCOPE,
        explicit_invocation=True,
        preserve_question_byte_for_byte=True,
        permit_normalization_or_rewrite=False,
        permit_scope_broadening=False,
        permit_route_or_ui_use=False,
        permit_gp015_reuse=False,
    )
    return replace(value, request_id=value.expected_id())


def _receipt(*, request_id: str, state_id: str, binding_identity_id: str | None = None, source_result: Any = None, gp014_imported: bool = False, gp014_called: bool = False) -> Gp014AdapterReceipt:
    source_status = getattr(source_result, "status", None) if source_result is not None else None
    source_hash = source_result.result_hash() if source_result is not None and callable(getattr(source_result, "result_hash", None)) else None
    question = getattr(source_result, "question", None) if source_result is not None else None
    trace = getattr(source_result, "trace", {}) if source_result is not None else {}
    if not isinstance(trace, dict):
        trace = {}
    operation_family = None
    compiled = trace.get("compiled_request")
    if isinstance(compiled, dict):
        candidate = compiled.get("operation_family")
        if isinstance(candidate, str):
            operation_family = candidate
    answer_text = getattr(source_result, "answer_text", None) if source_result is not None else None
    value = Gp014AdapterReceipt(
        receipt_id="pending",
        request_id=request_id,
        state_id=state_id,
        binding_identity_id=binding_identity_id,
        source_status=source_status if isinstance(source_status, str) else None,
        source_result_hash=source_hash,
        source_question_sha256=question_sha256(question) if isinstance(question, str) else None,
        operation_family=operation_family,
        answer_text_sha256=sha256(answer_text.encode("utf-8")).hexdigest() if isinstance(answer_text, str) else None,
        expression_realization_receipt_hash=trace.get("expression_realization_receipt_hash") if isinstance(trace.get("expression_realization_receipt_hash"), str) else None,
        echo_hash=trace.get("echo_hash") if isinstance(trace.get("echo_hash"), str) else None,
        delivery_authorization_v2_hash=trace.get("delivery_authorization_v2_hash") if isinstance(trace.get("delivery_authorization_v2_hash"), str) else None,
        question_forwarded_byte_for_byte=isinstance(question, str),
        source_result_returned_unchanged=source_result is not None,
        source_status_rewritten=False,
        source_answer_rewritten=False,
        source_trace_mutated=False,
        gp014_imported=gp014_imported,
        gp014_called=gp014_called,
        gp014_modified=False,
        gp014_superseded=False,
        gp015_used=False,
        main_modified_or_called=False,
        route_created_or_called=False,
        api_created_or_called=False,
        ui_created_or_called=False,
        network_authority_added=False,
        filesystem_write_authority_added=False,
        memory_authority_added=False,
        evidence_authority_added=False,
        truth_authority_added=False,
        permission_authority_added=False,
        delivery_authority_added_by_adapter=False,
        existing_gp014_delivery_receipt_observed=isinstance(trace.get("delivery_authorization_v2_hash"), str),
        tool_authority_added=False,
        action_authority_added=False,
        external_resource_authority_added=False,
        raw_exception_exposed=False,
    )
    return replace(value, receipt_id=value.expected_id())


def _result(*, status: str, reason_code: str, request: Any, state: Any, receipt: Gp014AdapterReceipt, binding_identity: Any = None, source_result: Any = None, adapter_completed: bool = False, source_answered: bool = False, source_contained: bool = False) -> Gp014AdapterResult:
    value = Gp014AdapterResult(
        result_id="pending",
        status=status,
        reason_code=reason_code,
        request_id=getattr(request, "request_id", None),
        state_id=getattr(state, "state_id", None),
        binding_identity=binding_identity,
        receipt=receipt,
        source_result=source_result,
        adapter_completed=adapter_completed,
        source_answered=source_answered,
        source_contained=source_contained,
    )
    value = replace(value, result_id=value.expected_id())
    return value


def _source_result_is_valid(source_result: Any, exact_question: str) -> bool:
    if source_result is None or not callable(getattr(source_result, "to_dict", None)) or not callable(getattr(source_result, "result_hash", None)):
        return False
    if getattr(source_result, "question", None) != exact_question:
        return False
    status = getattr(source_result, "status", None)
    if status not in GP014_ALLOWED_SOURCE_STATUSES:
        return False
    trace = getattr(source_result, "trace", None)
    if not isinstance(trace, dict):
        return False
    if status == "ANSWERED":
        required = (
            "compiled_request", "expression_realization_receipt", "expression_realization_receipt_hash",
            "rendered_text", "echo", "echo_hash", "delivery_authorization_v2",
            "delivery_authorization_v2_hash",
        )
        if any(key not in trace for key in required):
            return False
        compiled = trace["compiled_request"]
        realization = trace["expression_realization_receipt"]
        echo = trace["echo"]
        delivery = trace["delivery_authorization_v2"]
        if not all(isinstance(value, dict) for value in (compiled, realization, echo, delivery)):
            return False
        if compiled.get("operation_family") not in GP014_SUPPORTED_OPERATION_FAMILIES:
            return False
        if realization.get("selected_text") != trace.get("rendered_text") or realization.get("selected_text") != getattr(source_result, "answer_text", None):
            return False
        if realization.get("actual_echo_invoked") is not False or realization.get("delivery_authorized") is not False:
            return False
        if echo.get("approved_output") is not True or delivery.get("delivery_status") != "ECHO_APPROVED_DELIVERY_AUTHORIZED":
            return False
    elif "delivery_authorization_v2" in trace or "delivery_authorization_v2_hash" in trace:
        return False
    return True


def run_gp014_adapter(request: Any = None, *, state: Any = None) -> Gp014AdapterResult:
    actual_state = build_gp014_adapter_state() if state is None else state
    state_report = validate_state(actual_state)
    request_id = getattr(request, "request_id", "invalid_request")
    state_id = getattr(actual_state, "state_id", "invalid_state")
    if not state_report.ok:
        receipt = _receipt(request_id=request_id, state_id=state_id)
        return _result(status=STATUS_HELD_INVALID_STATE, reason_code="adapter_state_validation_failed", request=request, state=actual_state, receipt=receipt)

    request_report = validate_request(request)
    if not request_report.ok:
        receipt = _receipt(request_id=request_id, state_id=state_id)
        return _result(status=STATUS_HELD_INVALID_REQUEST, reason_code="adapter_request_validation_failed", request=request, state=actual_state, receipt=receipt)

    if not actual_state.enabled:
        receipt = _receipt(request_id=request.request_id, state_id=actual_state.state_id)
        return _result(status=STATUS_REFUSED_DISABLED, reason_code="explicit_offline_developer_enable_required", request=request, state=actual_state, receipt=receipt)

    try:
        binding = load_gp014_runtime_binding()
    except Exception:
        receipt = _receipt(request_id=request.request_id, state_id=actual_state.state_id)
        return _result(status=STATUS_HELD_GP014_IDENTITY, reason_code="gp014_exact_binding_unavailable", request=request, state=actual_state, receipt=receipt)

    try:
        source_result = binding.answer(request.question)
    except Exception:
        receipt = _receipt(request_id=request.request_id, state_id=actual_state.state_id, binding_identity_id=binding.identity.identity_id, gp014_imported=True, gp014_called=True)
        return _result(status=STATUS_CONTAINED_SOURCE_FAILURE, reason_code="gp014_source_exception_contained", request=request, state=actual_state, receipt=receipt, binding_identity=binding.identity)

    if not _source_result_is_valid(source_result, request.question):
        receipt = _receipt(request_id=request.request_id, state_id=actual_state.state_id, binding_identity_id=binding.identity.identity_id, source_result=source_result, gp014_imported=True, gp014_called=True)
        return _result(status=STATUS_HELD_GP014_RESULT, reason_code="gp014_result_validation_failed", request=request, state=actual_state, receipt=receipt, binding_identity=binding.identity, source_result=source_result)

    receipt = _receipt(request_id=request.request_id, state_id=actual_state.state_id, binding_identity_id=binding.identity.identity_id, source_result=source_result, gp014_imported=True, gp014_called=True)
    answered = source_result.status == "ANSWERED"
    result = _result(
        status=STATUS_COMPLETED_ANSWERED if answered else STATUS_COMPLETED_CONTAINED,
        reason_code="unchanged_gp014_result_exposed" if answered else "unchanged_gp014_containment_exposed",
        request=request,
        state=actual_state,
        receipt=receipt,
        binding_identity=binding.identity,
        source_result=source_result,
        adapter_completed=True,
        source_answered=answered,
        source_contained=not answered,
    )
    if not validate_result(result).ok:
        held_receipt = _receipt(request_id=request.request_id, state_id=actual_state.state_id, binding_identity_id=binding.identity.identity_id, source_result=source_result, gp014_imported=True, gp014_called=True)
        return _result(status=STATUS_HELD_GP014_RESULT, reason_code="adapter_result_validation_failed", request=request, state=actual_state, receipt=held_receipt, binding_identity=binding.identity, source_result=source_result)
    return result


__all__ = ("build_gp014_adapter_request", "build_gp014_adapter_state", "run_gp014_adapter")
