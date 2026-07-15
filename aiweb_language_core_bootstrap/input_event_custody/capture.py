"""Deterministic source-custody capture for Slice 36A.

This module accepts one in-memory Python ``str`` and creates immutable custody
records. It performs strict UTF-8 encoding, exact hashing, offset accounting,
and closed unsupported-code-point classification. It does not tokenize,
normalize, interpret, resolve references, read external state, write state, or
activate any runtime consequence.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib
import re
import unicodedata
from typing import Final

from ..schema import (
    ValidationIssue,
    ValidationReport,
    issue,
    stable_record_id,
)
from .schema import (
    ABSOLUTE_MAX_CODE_POINTS,
    ABSOLUTE_MAX_RECORDED_CONDITIONS,
    ABSOLUTE_MAX_UTF8_BYTES,
    CUSTODY_SCHEMA_VERSION,
    CUSTODY_SPEC_ID,
    CUSTODY_SPEC_VERSION,
    DEFAULT_MAX_CODE_POINTS,
    DEFAULT_MAX_RECORDED_CONDITIONS,
    DEFAULT_MAX_UTF8_BYTES,
    MAX_IDENTITY_CODE_POINTS,
    MAX_SEQUENCE_NUMBER,
    UNICODE_DATABASE_VERSION,
    InputConditionCategory,
    InputConditionCode,
    InputConditionRecord,
    InputCustodyLimits,
    InputCustodyStatus,
    InputEventCaptureResult,
    InputEventRecord,
    SourceSpanBuildResult,
    SourceSpanRecord,
)

_IDENTITY_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}\Z"
)
_ALLOWED_CONTROL_CHARACTERS: Final[frozenset[str]] = frozenset(("\t", "\n", "\r"))
_RULE_LIMITS: Final[str] = "AIWEB-36A-LIMITS-001"
_RULE_METADATA: Final[str] = "AIWEB-36A-METADATA-001"
_RULE_UTF8: Final[str] = "AIWEB-36A-UTF8-001"
_RULE_SIZE: Final[str] = "AIWEB-36A-SIZE-001"
_RULE_UNICODE: Final[str] = "AIWEB-36A-UNICODE-001"
_RULE_SPAN: Final[str] = "AIWEB-36A-SPAN-001"
_DEFAULT_LIMITS_SENTINEL: Final[object] = object()
_REASON_CAPTURED_SUPPORTED: Final[str] = "exact_source_custody_captured"
_REASON_CAPTURED_UNSUPPORTED: Final[str] = (
    "exact_source_custody_captured_but_structural_progression_held"
)


def _exact_int(value: object) -> bool:
    return type(value) is int


def _build_limits_record(
    *,
    max_utf8_bytes: int,
    max_code_points: int,
    max_recorded_conditions: int,
    allow_empty: bool,
) -> InputCustodyLimits:
    body = {
        "max_utf8_bytes": max_utf8_bytes,
        "max_code_points": max_code_points,
        "max_recorded_conditions": max_recorded_conditions,
        "allow_empty": allow_empty,
        "custody_spec_id": CUSTODY_SPEC_ID,
        "custody_spec_version": CUSTODY_SPEC_VERSION,
        "schema_version": CUSTODY_SCHEMA_VERSION,
    }
    return InputCustodyLimits(
        limits_id=stable_record_id("input_custody_limits", body),
        **body,
    )


def default_input_custody_limits() -> InputCustodyLimits:
    """Return the immutable default bounded-input policy."""

    return _build_limits_record(
        max_utf8_bytes=DEFAULT_MAX_UTF8_BYTES,
        max_code_points=DEFAULT_MAX_CODE_POINTS,
        max_recorded_conditions=DEFAULT_MAX_RECORDED_CONDITIONS,
        allow_empty=False,
    )


def build_input_custody_limits(
    *,
    max_utf8_bytes: object = DEFAULT_MAX_UTF8_BYTES,
    max_code_points: object = DEFAULT_MAX_CODE_POINTS,
    max_recorded_conditions: object = DEFAULT_MAX_RECORDED_CONDITIONS,
    allow_empty: object = False,
) -> InputCustodyLimits | None:
    """Build limits when values are exact bounded primitive types.

    Invalid values return ``None``. The capture API converts that absence into
    typed malformed-input conditions instead of allowing a raw exception to
    escape.
    """

    if not _exact_int(max_utf8_bytes):
        return None
    if not _exact_int(max_code_points):
        return None
    if not _exact_int(max_recorded_conditions):
        return None
    if type(allow_empty) is not bool:
        return None
    if not 1 <= max_utf8_bytes <= ABSOLUTE_MAX_UTF8_BYTES:
        return None
    if not 1 <= max_code_points <= ABSOLUTE_MAX_CODE_POINTS:
        return None
    if not 1 <= max_recorded_conditions <= ABSOLUTE_MAX_RECORDED_CONDITIONS:
        return None
    return _build_limits_record(
        max_utf8_bytes=max_utf8_bytes,
        max_code_points=max_code_points,
        max_recorded_conditions=max_recorded_conditions,
        allow_empty=allow_empty,
    )


def _condition(
    *,
    input_event_id: str,
    category: InputConditionCategory,
    code: InputConditionCode,
    field: str,
    rule_id: str,
    detail: str = "",
    code_point_start: int | None = None,
    code_point_end: int | None = None,
    utf8_byte_start: int | None = None,
    utf8_byte_end: int | None = None,
    unicode_code_point: str = "",
) -> InputConditionRecord:
    body = {
        "input_event_id": input_event_id,
        "category": category,
        "code": code,
        "field": field,
        "rule_id": rule_id,
        "detail": detail,
        "code_point_start": code_point_start,
        "code_point_end": code_point_end,
        "utf8_byte_start": utf8_byte_start,
        "utf8_byte_end": utf8_byte_end,
        "unicode_code_point": unicode_code_point,
        "custody_spec_id": CUSTODY_SPEC_ID,
        "custody_spec_version": CUSTODY_SPEC_VERSION,
        "schema_version": CUSTODY_SCHEMA_VERSION,
    }
    return InputConditionRecord(
        condition_id=stable_record_id("input_condition", body),
        **body,
    )


def _limits_validation_issues(limits: object) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    if type(limits) is not InputCustodyLimits:
        return (issue("limits", InputConditionCode.INVALID_LIMITS_TYPE.value),)
    if limits.schema_version != CUSTODY_SCHEMA_VERSION:
        issues.append(issue("limits.schema_version", "unsupported_schema_version"))
    if limits.custody_spec_id != CUSTODY_SPEC_ID:
        issues.append(issue("limits.custody_spec_id", "custody_spec_id_mismatch"))
    if limits.custody_spec_version != CUSTODY_SPEC_VERSION:
        issues.append(
            issue("limits.custody_spec_version", "custody_spec_version_mismatch")
        )
    for field_name, value, hard_maximum in (
        ("max_utf8_bytes", limits.max_utf8_bytes, ABSOLUTE_MAX_UTF8_BYTES),
        ("max_code_points", limits.max_code_points, ABSOLUTE_MAX_CODE_POINTS),
        (
            "max_recorded_conditions",
            limits.max_recorded_conditions,
            ABSOLUTE_MAX_RECORDED_CONDITIONS,
        ),
    ):
        if not _exact_int(value):
            issues.append(issue(field_name, InputConditionCode.INVALID_LIMIT_TYPE.value))
        elif value < 1:
            issues.append(issue(field_name, InputConditionCode.INVALID_LIMIT_RANGE.value))
        elif value > hard_maximum:
            issues.append(
                issue(
                    field_name,
                    InputConditionCode.DECLARED_LIMIT_EXCEEDS_ABSOLUTE_MAXIMUM.value,
                )
            )
    if type(limits.allow_empty) is not bool:
        issues.append(issue("allow_empty", InputConditionCode.INVALID_LIMIT_TYPE.value))
    if limits.limits_id != limits.expected_id():
        issues.append(issue("limits_id", "stable_id_mismatch"))
    return tuple(issues)


def validate_input_custody_limits(limits: object) -> ValidationReport:
    issues = _limits_validation_issues(limits)
    return ValidationReport(
        schema_version=CUSTODY_SCHEMA_VERSION,
        ok=not issues,
        issues=issues,
    )


def _metadata_conditions(
    *,
    source_id: object,
    channel_id: object,
    sequence_number: object,
    correlation_id: object,
) -> list[InputConditionRecord]:
    conditions: list[InputConditionRecord] = []
    if (
        type(source_id) is not str
        or len(source_id) > MAX_IDENTITY_CODE_POINTS
        or _IDENTITY_PATTERN.fullmatch(source_id) is None
    ):
        conditions.append(
            _condition(
                input_event_id="",
                category=InputConditionCategory.MALFORMED,
                code=InputConditionCode.INVALID_SOURCE_ID,
                field="source_id",
                rule_id=_RULE_METADATA,
            )
        )
    if (
        type(channel_id) is not str
        or len(channel_id) > MAX_IDENTITY_CODE_POINTS
        or _IDENTITY_PATTERN.fullmatch(channel_id) is None
    ):
        conditions.append(
            _condition(
                input_event_id="",
                category=InputConditionCategory.MALFORMED,
                code=InputConditionCode.INVALID_CHANNEL_ID,
                field="channel_id",
                rule_id=_RULE_METADATA,
            )
        )
    if sequence_number is not None and (
        not _exact_int(sequence_number)
        or sequence_number < 0
        or sequence_number > MAX_SEQUENCE_NUMBER
    ):
        conditions.append(
            _condition(
                input_event_id="",
                category=InputConditionCategory.MALFORMED,
                code=InputConditionCode.INVALID_SEQUENCE_NUMBER,
                field="sequence_number",
                rule_id=_RULE_METADATA,
            )
        )
    if correlation_id is not None and (
        type(correlation_id) is not str
        or len(correlation_id) > MAX_IDENTITY_CODE_POINTS
        or _IDENTITY_PATTERN.fullmatch(correlation_id) is None
    ):
        conditions.append(
            _condition(
                input_event_id="",
                category=InputConditionCategory.MALFORMED,
                code=InputConditionCode.INVALID_CORRELATION_ID,
                field="correlation_id",
                rule_id=_RULE_METADATA,
            )
        )
    if sequence_number is None and correlation_id is None:
        conditions.append(
            _condition(
                input_event_id="",
                category=InputConditionCategory.MALFORMED,
                code=InputConditionCode.MISSING_SEQUENCE_AND_CORRELATION,
                field="sequence_number|correlation_id",
                rule_id=_RULE_METADATA,
            )
        )
    return conditions


def _rejection_result(
    *,
    conditions: tuple[InputConditionRecord, ...],
    limits: InputCustodyLimits | None,
    observed_utf8_byte_length: int | None,
    observed_code_point_length: int | None,
    observed_source_sha256: str,
) -> InputEventCaptureResult:
    reason_code = (
        conditions[0].code.value
        if conditions
        else InputConditionCode.INVALID_SOURCE_TYPE.value
    )
    body = {
        "status": InputCustodyStatus.REJECTED_MALFORMED,
        "reason_code": reason_code,
        "custody_created": False,
        "structural_progression_allowed": False,
        "malformed_input": True,
        "unsupported_input": False,
        "observed_utf8_byte_length": observed_utf8_byte_length,
        "observed_code_point_length": observed_code_point_length,
        "observed_source_sha256": observed_source_sha256,
        "limits": limits,
        "event": None,
        "root_span": None,
        "conditions": conditions,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "network_access_performed": False,
        "environment_access_performed": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "route_registration_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "delivery_performed": False,
        "custody_spec_id": CUSTODY_SPEC_ID,
        "custody_spec_version": CUSTODY_SPEC_VERSION,
        "schema_version": CUSTODY_SCHEMA_VERSION,
    }
    return InputEventCaptureResult(
        result_id=stable_record_id("input_event_capture_result", body),
        **body,
    )


def _is_noncharacter(code_point: int) -> bool:
    return (
        0xFDD0 <= code_point <= 0xFDEF
        or (code_point & 0xFFFF) in (0xFFFE, 0xFFFF)
    )


def _unsupported_code(
    character: str,
) -> InputConditionCode | None:
    code_point = ord(character)
    if _is_noncharacter(code_point):
        return InputConditionCode.UNSUPPORTED_NONCHARACTER
    category = unicodedata.category(character)
    if category == "Cc" and character not in _ALLOWED_CONTROL_CHARACTERS:
        return InputConditionCode.UNSUPPORTED_CONTROL_CHARACTER
    if category == "Cf":
        return InputConditionCode.UNSUPPORTED_FORMAT_CHARACTER
    if category == "Co":
        return InputConditionCode.UNSUPPORTED_PRIVATE_USE_CHARACTER
    if category == "Cn":
        return InputConditionCode.UNSUPPORTED_UNASSIGNED_CHARACTER
    return None


def _build_boundary_offsets(source_text: str) -> tuple[int, ...]:
    offsets = [0]
    total = 0
    for character in source_text:
        total += len(character.encode("utf-8", "strict"))
        offsets.append(total)
    return tuple(offsets)


def _build_span_record(
    *,
    event: InputEventRecord,
    code_point_start: int,
    code_point_end: int,
) -> SourceSpanRecord:
    byte_start = event.utf8_boundary_offsets[code_point_start]
    byte_end = event.utf8_boundary_offsets[code_point_end]
    source_slice = event.exact_received_text[code_point_start:code_point_end]
    span_bytes = source_slice.encode("utf-8", "strict")
    body = {
        "input_event_id": event.input_event_id,
        "source_sha256": event.source_sha256,
        "code_point_start": code_point_start,
        "code_point_end": code_point_end,
        "utf8_byte_start": byte_start,
        "utf8_byte_end": byte_end,
        "code_point_length": code_point_end - code_point_start,
        "utf8_byte_length": byte_end - byte_start,
        "span_sha256": hashlib.sha256(span_bytes).hexdigest(),
        "is_root_span": (
            code_point_start == 0 and code_point_end == event.code_point_length
        ),
        "custody_spec_id": CUSTODY_SPEC_ID,
        "custody_spec_version": CUSTODY_SPEC_VERSION,
        "schema_version": CUSTODY_SCHEMA_VERSION,
    }
    return SourceSpanRecord(
        span_id=stable_record_id("source_span", body),
        **body,
    )


def build_source_span(
    event: object,
    *,
    code_point_start: object,
    code_point_end: object,
) -> SourceSpanBuildResult:
    """Build an exact source span without tokenization or interpretation."""

    conditions: list[InputConditionRecord] = []
    if type(event) is not InputEventRecord:
        conditions.append(
            _condition(
                input_event_id="",
                category=InputConditionCategory.MALFORMED,
                code=InputConditionCode.INVALID_SPAN_EVENT_TYPE,
                field="event",
                rule_id=_RULE_SPAN,
            )
        )
    elif not _exact_int(code_point_start) or not _exact_int(code_point_end):
        conditions.append(
            _condition(
                input_event_id=event.input_event_id,
                category=InputConditionCategory.MALFORMED,
                code=InputConditionCode.INVALID_SPAN_OFFSET_TYPE,
                field="code_point_start|code_point_end",
                rule_id=_RULE_SPAN,
            )
        )
    elif not 0 <= code_point_start <= code_point_end <= event.code_point_length:
        conditions.append(
            _condition(
                input_event_id=event.input_event_id,
                category=InputConditionCategory.MALFORMED,
                code=InputConditionCode.INVALID_SPAN_BOUNDS,
                field="code_point_start|code_point_end",
                rule_id=_RULE_SPAN,
            )
        )

    span = None
    if not conditions and type(event) is InputEventRecord:
        span = _build_span_record(
            event=event,
            code_point_start=code_point_start,
            code_point_end=code_point_end,
        )
    reason_code = "source_span_built" if span is not None else conditions[0].code.value
    body = {
        "ok": span is not None,
        "reason_code": reason_code,
        "span": span,
        "conditions": tuple(conditions),
        "custody_spec_id": CUSTODY_SPEC_ID,
        "custody_spec_version": CUSTODY_SPEC_VERSION,
        "schema_version": CUSTODY_SCHEMA_VERSION,
    }
    return SourceSpanBuildResult(
        result_id=stable_record_id("source_span_build_result", body),
        **body,
    )


def capture_input_event(
    source_text: object,
    *,
    source_id: object,
    channel_id: object,
    sequence_number: object = None,
    correlation_id: object = None,
    limits: object = _DEFAULT_LIMITS_SENTINEL,
) -> InputEventCaptureResult:
    """Capture exact source input and return a typed immutable result.

    Invalid caller values, malformed Unicode, and size violations return a
    deterministic rejected result. Valid but unsupported Unicode is preserved
    exactly in a custody event while structural progression remains held.
    """

    effective_limits = (
        default_input_custody_limits()
        if limits is _DEFAULT_LIMITS_SENTINEL
        else limits
    )
    malformed: list[InputConditionRecord] = []

    limit_issues = _limits_validation_issues(effective_limits)
    if limit_issues:
        for limit_issue in limit_issues:
            code = InputConditionCode.INVALID_LIMITS_TYPE
            for candidate in InputConditionCode:
                if candidate.value == limit_issue.code:
                    code = candidate
                    break
            malformed.append(
                _condition(
                    input_event_id="",
                    category=InputConditionCategory.MALFORMED,
                    code=code,
                    field=limit_issue.field,
                    rule_id=_RULE_LIMITS,
                    detail=limit_issue.detail,
                )
            )
        effective_limits = None

    malformed.extend(
        _metadata_conditions(
            source_id=source_id,
            channel_id=channel_id,
            sequence_number=sequence_number,
            correlation_id=correlation_id,
        )
    )

    observed_code_points: int | None = None
    observed_bytes: int | None = None
    observed_hash = ""
    encoded = b""

    if type(source_text) is not str:
        malformed.append(
            _condition(
                input_event_id="",
                category=InputConditionCategory.MALFORMED,
                code=InputConditionCode.INVALID_SOURCE_TYPE,
                field="source_text",
                rule_id=_RULE_UTF8,
                detail=(
                    f"received_type={type(source_text).__module__}."
                    f"{type(source_text).__qualname__}"
                ),
            )
        )
    else:
        observed_code_points = len(source_text)
        if effective_limits is not None:
            if observed_code_points == 0 and not effective_limits.allow_empty:
                malformed.append(
                    _condition(
                        input_event_id="",
                        category=InputConditionCategory.MALFORMED,
                        code=InputConditionCode.EMPTY_SOURCE_NOT_ALLOWED,
                        field="source_text",
                        rule_id=_RULE_SIZE,
                    )
                )
            if observed_code_points > effective_limits.max_code_points:
                malformed.append(
                    _condition(
                        input_event_id="",
                        category=InputConditionCategory.MALFORMED,
                        code=InputConditionCode.CODE_POINT_LIMIT_EXCEEDED,
                        field="source_text",
                        rule_id=_RULE_SIZE,
                        detail=(
                            f"observed={observed_code_points};"
                            f"maximum={effective_limits.max_code_points}"
                        ),
                    )
                )
        if not any(
            condition.code == InputConditionCode.CODE_POINT_LIMIT_EXCEEDED
            for condition in malformed
        ):
            try:
                encoded = source_text.encode("utf-8", "strict")
            except UnicodeEncodeError as error:
                malformed.append(
                    _condition(
                        input_event_id="",
                        category=InputConditionCategory.MALFORMED,
                        code=InputConditionCode.SOURCE_CONTAINS_LONE_SURROGATE,
                        field="source_text",
                        rule_id=_RULE_UTF8,
                        detail=f"start={error.start};end={error.end}",
                        code_point_start=error.start,
                        code_point_end=error.end,
                    )
                )
            else:
                observed_bytes = len(encoded)
                observed_hash = hashlib.sha256(encoded).hexdigest()
                if (
                    effective_limits is not None
                    and observed_bytes > effective_limits.max_utf8_bytes
                ):
                    malformed.append(
                        _condition(
                            input_event_id="",
                            category=InputConditionCategory.MALFORMED,
                            code=InputConditionCode.UTF8_BYTE_LIMIT_EXCEEDED,
                            field="source_text",
                            rule_id=_RULE_SIZE,
                            detail=(
                                f"observed={observed_bytes};"
                                f"maximum={effective_limits.max_utf8_bytes}"
                            ),
                        )
                    )

    if malformed:
        return _rejection_result(
            conditions=tuple(malformed),
            limits=(
                effective_limits
                if type(effective_limits) is InputCustodyLimits
                else None
            ),
            observed_utf8_byte_length=observed_bytes,
            observed_code_point_length=observed_code_points,
            observed_source_sha256=observed_hash,
        )

    assert type(source_text) is str
    assert type(source_id) is str
    assert type(channel_id) is str
    assert type(effective_limits) is InputCustodyLimits
    assert observed_code_points is not None
    assert observed_bytes is not None

    identity_body = {
        "source_id": source_id,
        "channel_id": channel_id,
        "sequence_number": sequence_number,
        "correlation_id": correlation_id,
        "utf8_byte_length": observed_bytes,
        "code_point_length": observed_code_points,
        "source_sha256": observed_hash,
        "limits_id": effective_limits.limits_id,
        "unicode_database_version": UNICODE_DATABASE_VERSION,
        "custody_spec_id": CUSTODY_SPEC_ID,
        "custody_spec_version": CUSTODY_SPEC_VERSION,
        "schema_version": CUSTODY_SCHEMA_VERSION,
    }
    event_id = stable_record_id("input_event", identity_body)
    boundary_offsets = _build_boundary_offsets(source_text)

    unsupported: list[InputConditionRecord] = []
    total_unsupported = 0
    for index, character in enumerate(source_text):
        code = _unsupported_code(character)
        if code is None:
            continue
        total_unsupported += 1
        detail_capacity = max(0, effective_limits.max_recorded_conditions - 1)
        if len(unsupported) >= detail_capacity:
            continue
        byte_start = boundary_offsets[index]
        byte_end = boundary_offsets[index + 1]
        unsupported.append(
            _condition(
                input_event_id=event_id,
                category=InputConditionCategory.UNSUPPORTED,
                code=code,
                field="source_text",
                rule_id=_RULE_UNICODE,
                detail=f"unicode_category={unicodedata.category(character)}",
                code_point_start=index,
                code_point_end=index + 1,
                utf8_byte_start=byte_start,
                utf8_byte_end=byte_end,
                unicode_code_point=f"U+{ord(character):04X}",
            )
        )
    if total_unsupported > len(unsupported):
        unsupported.append(
            _condition(
                input_event_id=event_id,
                category=InputConditionCategory.UNSUPPORTED,
                code=(
                    InputConditionCode.UNSUPPORTED_CONDITION_RECORDING_LIMIT_REACHED
                ),
                field="source_text",
                rule_id=_RULE_UNICODE,
                detail=(
                    f"total={total_unsupported};"
                    f"recorded={len(unsupported)}"
                ),
            )
        )

    status = (
        InputCustodyStatus.CAPTURED_UNSUPPORTED
        if unsupported
        else InputCustodyStatus.CAPTURED_SUPPORTED
    )
    placeholder_event = InputEventRecord(
        input_event_id=event_id,
        exact_received_text=source_text,
        source_id=source_id,
        channel_id=channel_id,
        sequence_number=sequence_number,
        correlation_id=correlation_id,
        utf8_byte_length=observed_bytes,
        code_point_length=observed_code_points,
        source_sha256=observed_hash,
        utf8_boundary_offsets=boundary_offsets,
        root_source_span_id="",
        limits_id=effective_limits.limits_id,
        custody_status=status,
        malformed_condition_ids=(),
        unsupported_condition_ids=tuple(
            condition.condition_id for condition in unsupported
        ),
        total_unsupported_condition_count=total_unsupported,
        source_preserved_exactly=True,
        normalization_performed=False,
        tokenization_performed=False,
        interpretation_performed=False,
        concept_lookup_performed=False,
        reference_resolution_performed=False,
        external_lookup_performed=False,
        unicode_database_version=UNICODE_DATABASE_VERSION,
    )
    root_span = _build_span_record(
        event=placeholder_event,
        code_point_start=0,
        code_point_end=observed_code_points,
    )
    event = replace(placeholder_event, root_source_span_id=root_span.span_id)

    reason_code = (
        _REASON_CAPTURED_UNSUPPORTED
        if unsupported
        else _REASON_CAPTURED_SUPPORTED
    )
    body = {
        "status": status,
        "reason_code": reason_code,
        "custody_created": True,
        "structural_progression_allowed": not unsupported,
        "malformed_input": False,
        "unsupported_input": bool(unsupported),
        "observed_utf8_byte_length": observed_bytes,
        "observed_code_point_length": observed_code_points,
        "observed_source_sha256": observed_hash,
        "limits": effective_limits,
        "event": event,
        "root_span": root_span,
        "conditions": tuple(unsupported),
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "network_access_performed": False,
        "environment_access_performed": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "route_registration_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "delivery_performed": False,
        "custody_spec_id": CUSTODY_SPEC_ID,
        "custody_spec_version": CUSTODY_SPEC_VERSION,
        "schema_version": CUSTODY_SCHEMA_VERSION,
    }
    return InputEventCaptureResult(
        result_id=stable_record_id("input_event_capture_result", body),
        **body,
    )


def validate_input_condition(record: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not InputConditionRecord:
        issues.append(issue("record", "invalid_input_condition_type"))
    else:
        if record.schema_version != CUSTODY_SCHEMA_VERSION:
            issues.append(issue("schema_version", "unsupported_schema_version"))
        if record.condition_id != record.expected_id():
            issues.append(issue("condition_id", "stable_id_mismatch"))
        if type(record.category) is not InputConditionCategory:
            issues.append(issue("category", "invalid_condition_category"))
        if type(record.code) is not InputConditionCode:
            issues.append(issue("code", "invalid_condition_code"))
        if not record.field or not record.rule_id:
            issues.append(issue("field|rule_id", "required_non_empty_text"))
        offsets = (
            record.code_point_start,
            record.code_point_end,
            record.utf8_byte_start,
            record.utf8_byte_end,
        )
        if any(offset is not None and not _exact_int(offset) for offset in offsets):
            issues.append(issue("offsets", "invalid_offset_type"))
    return ValidationReport(
        schema_version=CUSTODY_SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def validate_source_span(record: object, *, event: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not SourceSpanRecord:
        issues.append(issue("record", "invalid_source_span_type"))
    elif type(event) is not InputEventRecord:
        issues.append(issue("event", "invalid_input_event_type"))
    else:
        if record.schema_version != CUSTODY_SCHEMA_VERSION:
            issues.append(issue("schema_version", "unsupported_schema_version"))
        if record.span_id != record.expected_id():
            issues.append(issue("span_id", "stable_id_mismatch"))
        if record.input_event_id != event.input_event_id:
            issues.append(issue("input_event_id", "input_event_reference_mismatch"))
        if record.source_sha256 != event.source_sha256:
            issues.append(issue("source_sha256", "source_hash_mismatch"))
        if not (
            0
            <= record.code_point_start
            <= record.code_point_end
            <= event.code_point_length
        ):
            issues.append(issue("code_point_bounds", "invalid_span_bounds"))
        else:
            expected = _build_span_record(
                event=event,
                code_point_start=record.code_point_start,
                code_point_end=record.code_point_end,
            )
            if record != expected:
                issues.append(issue("record", "source_span_content_mismatch"))
    return ValidationReport(
        schema_version=CUSTODY_SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def validate_input_event(record: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not InputEventRecord:
        issues.append(issue("record", "invalid_input_event_type"))
    else:
        if record.schema_version != CUSTODY_SCHEMA_VERSION:
            issues.append(issue("schema_version", "unsupported_schema_version"))
        if record.input_event_id != record.expected_id():
            issues.append(issue("input_event_id", "stable_id_mismatch"))
        try:
            encoded = record.exact_received_text.encode("utf-8", "strict")
        except UnicodeEncodeError:
            issues.append(issue("exact_received_text", "invalid_utf8_source"))
        else:
            if len(encoded) != record.utf8_byte_length:
                issues.append(issue("utf8_byte_length", "length_mismatch"))
            if len(record.exact_received_text) != record.code_point_length:
                issues.append(issue("code_point_length", "length_mismatch"))
            if hashlib.sha256(encoded).hexdigest() != record.source_sha256:
                issues.append(issue("source_sha256", "source_hash_mismatch"))
            if _build_boundary_offsets(record.exact_received_text) != record.utf8_boundary_offsets:
                issues.append(issue("utf8_boundary_offsets", "offset_map_mismatch"))
        if record.unicode_database_version != UNICODE_DATABASE_VERSION:
            issues.append(issue("unicode_database_version", "unicode_database_version_mismatch"))
        if record.malformed_condition_ids:
            issues.append(issue("malformed_condition_ids", "captured_event_cannot_be_malformed"))
        if record.custody_status == InputCustodyStatus.CAPTURED_SUPPORTED:
            if record.unsupported_condition_ids or record.total_unsupported_condition_count:
                issues.append(issue("unsupported_conditions", "supported_status_mismatch"))
        elif record.custody_status == InputCustodyStatus.CAPTURED_UNSUPPORTED:
            if not record.unsupported_condition_ids or record.total_unsupported_condition_count < 1:
                issues.append(issue("unsupported_conditions", "unsupported_status_mismatch"))
        else:
            issues.append(issue("custody_status", "captured_event_status_invalid"))
        for field_name in (
            "normalization_performed",
            "tokenization_performed",
            "interpretation_performed",
            "concept_lookup_performed",
            "reference_resolution_performed",
            "external_lookup_performed",
        ):
            if getattr(record, field_name) is not False:
                issues.append(issue(field_name, "must_remain_false"))
        if record.source_preserved_exactly is not True:
            issues.append(issue("source_preserved_exactly", "must_remain_true"))
    return ValidationReport(
        schema_version=CUSTODY_SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def validate_input_event_capture_result(record: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not InputEventCaptureResult:
        issues.append(issue("record", "invalid_capture_result_type"))
    else:
        if record.schema_version != CUSTODY_SCHEMA_VERSION:
            issues.append(issue("schema_version", "unsupported_schema_version"))
        if record.result_id != record.expected_id():
            issues.append(issue("result_id", "stable_id_mismatch"))
        for field_name in (
            "filesystem_read_performed",
            "filesystem_write_performed",
            "network_access_performed",
            "environment_access_performed",
            "memory_read_performed",
            "memory_write_performed",
            "route_registration_performed",
            "tool_routing_performed",
            "action_performed",
            "delivery_performed",
        ):
            if getattr(record, field_name) is not False:
                issues.append(issue(field_name, "must_remain_false"))
        for condition in record.conditions:
            report = validate_input_condition(condition)
            issues.extend(report.issues)
        if record.status == InputCustodyStatus.REJECTED_MALFORMED:
            if record.custody_created or record.event is not None or record.root_span is not None:
                issues.append(issue("custody_created", "malformed_result_must_not_create_event"))
            if not record.malformed_input or record.unsupported_input:
                issues.append(issue("status_flags", "malformed_status_flag_mismatch"))
            if record.structural_progression_allowed:
                issues.append(issue("structural_progression_allowed", "must_remain_false"))
        else:
            if type(record.limits) is not InputCustodyLimits:
                issues.append(issue("limits", "captured_result_requires_limits"))
            elif not validate_input_custody_limits(record.limits).ok:
                issues.append(issue("limits", "invalid_limits_record"))
            if type(record.event) is not InputEventRecord:
                issues.append(issue("event", "captured_result_requires_event"))
            elif not validate_input_event(record.event).ok:
                issues.append(issue("event", "invalid_input_event_record"))
            if type(record.root_span) is not SourceSpanRecord:
                issues.append(issue("root_span", "captured_result_requires_root_span"))
            elif type(record.event) is InputEventRecord:
                span_report = validate_source_span(record.root_span, event=record.event)
                if not span_report.ok:
                    issues.append(issue("root_span", "invalid_root_source_span"))
                if record.event.root_source_span_id != record.root_span.span_id:
                    issues.append(issue("root_span", "root_span_reference_mismatch"))
            if not record.custody_created or record.malformed_input:
                issues.append(issue("custody_created", "captured_status_flag_mismatch"))
            if record.status == InputCustodyStatus.CAPTURED_SUPPORTED:
                if record.unsupported_input or not record.structural_progression_allowed:
                    issues.append(issue("status_flags", "supported_status_flag_mismatch"))
            elif record.status == InputCustodyStatus.CAPTURED_UNSUPPORTED:
                if not record.unsupported_input or record.structural_progression_allowed:
                    issues.append(issue("status_flags", "unsupported_status_flag_mismatch"))
            else:
                issues.append(issue("status", "unknown_capture_status"))
    return ValidationReport(
        schema_version=CUSTODY_SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )
