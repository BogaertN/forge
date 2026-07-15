#!/usr/bin/env python3
"""Behavior and adversarial tests for Slice 36A source custody."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import FrozenInstanceError, replace
import builtins
import hashlib
import os
from pathlib import Path
import socket
import subprocess
import sys
import unicodedata
import urllib.request
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aiweb_language_core_bootstrap.input_event_custody import (
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
    InputCustodyLimits,
    InputCustodyStatus,
    InputEventCaptureResult,
    InputEventRecord,
    SourceSpanRecord,
    build_input_custody_limits,
    build_source_span,
    capture_input_event,
    default_input_custody_limits,
    validate_input_condition,
    validate_input_custody_limits,
    validate_input_event,
    validate_input_event_capture_result,
    validate_source_span,
)

checks = 0


def check(condition: bool, label: str) -> None:
    global checks
    if not condition:
        raise AssertionError(label)
    checks += 1


def forbidden(*args, **kwargs):
    raise AssertionError("forbidden external side effect attempted")


# Constants and deterministic bounded limits.
check(CUSTODY_SPEC_ID == "aiweb-input-event-source-custody", "spec id exact")
check(CUSTODY_SPEC_VERSION.endswith("-v1"), "spec version exact")
check(CUSTODY_SCHEMA_VERSION.endswith("-v1"), "schema version exact")
check(UNICODE_DATABASE_VERSION == unicodedata.unidata_version, "unicode version bound")
check(DEFAULT_MAX_UTF8_BYTES < ABSOLUTE_MAX_UTF8_BYTES, "default byte bound below hard ceiling")
check(DEFAULT_MAX_CODE_POINTS < ABSOLUTE_MAX_CODE_POINTS, "default code-point bound below hard ceiling")
check(DEFAULT_MAX_RECORDED_CONDITIONS < ABSOLUTE_MAX_RECORDED_CONDITIONS, "default condition bound below hard ceiling")
check(MAX_IDENTITY_CODE_POINTS == 128, "identity bound exact")
check(MAX_SEQUENCE_NUMBER == (1 << 63) - 1, "sequence bound exact")

limits_a = default_input_custody_limits()
limits_b = default_input_custody_limits()
check(limits_a == limits_b, "default limits deterministic")
check(limits_a.limits_id == limits_a.expected_id(), "default limits id stable")
check(validate_input_custody_limits(limits_a).ok, "default limits valid")
check(limits_a.max_utf8_bytes == DEFAULT_MAX_UTF8_BYTES, "default byte limit exact")
check(limits_a.max_code_points == DEFAULT_MAX_CODE_POINTS, "default code-point limit exact")
check(limits_a.max_recorded_conditions == DEFAULT_MAX_RECORDED_CONDITIONS, "default condition limit exact")
check(limits_a.allow_empty is False, "empty disabled by default")

custom_limits = build_input_custody_limits(
    max_utf8_bytes=100,
    max_code_points=50,
    max_recorded_conditions=8,
    allow_empty=True,
)
check(type(custom_limits) is InputCustodyLimits, "custom limits built")
check(validate_input_custody_limits(custom_limits).ok, "custom limits valid")
check(build_input_custody_limits(max_utf8_bytes=True) is None, "bool byte limit rejected")
check(build_input_custody_limits(max_code_points=0) is None, "zero code-point limit rejected")
check(build_input_custody_limits(max_recorded_conditions=0) is None, "zero condition limit rejected")
check(build_input_custody_limits(max_utf8_bytes=ABSOLUTE_MAX_UTF8_BYTES + 1) is None, "oversize byte limit rejected")
check(build_input_custody_limits(max_code_points=ABSOLUTE_MAX_CODE_POINTS + 1) is None, "oversize code-point limit rejected")
check(build_input_custody_limits(max_recorded_conditions=ABSOLUTE_MAX_RECORDED_CONDITIONS + 1) is None, "oversize condition limit rejected")
check(build_input_custody_limits(allow_empty=1) is None, "non-bool allow_empty rejected")

# Exact source preservation, deterministic identity and exact UTF-8 boundaries.
source = "  Café\r\n\tA\u0301  🌍  "
source_bytes = source.encode("utf-8")
result_a = capture_input_event(
    source,
    source_id="user.nic",
    channel_id="chat.primary",
    sequence_number=7,
    correlation_id="conversation:alpha-1",
)
result_b = capture_input_event(
    source,
    source_id="user.nic",
    channel_id="chat.primary",
    sequence_number=7,
    correlation_id="conversation:alpha-1",
)
check(result_a == result_b, "capture deterministic")
check(type(result_a) is InputEventCaptureResult, "exact result type")
check(result_a.status is InputCustodyStatus.CAPTURED_SUPPORTED, "supported status exact")
check(result_a.custody_created is True, "custody created")
check(result_a.structural_progression_allowed is True, "supported input eligible")
check(result_a.malformed_input is False, "supported not malformed")
check(result_a.unsupported_input is False, "supported not unsupported")
check(result_a.conditions == (), "supported has no conditions")
check(type(result_a.event) is InputEventRecord, "event created")
check(type(result_a.root_span) is SourceSpanRecord, "root span created")
check(result_a.event.exact_received_text == source, "source exact")
check(result_a.event.exact_received_text.encode("utf-8") == source_bytes, "source bytes exact")
check(result_a.event.code_point_length == len(source), "code-point length exact")
check(result_a.event.utf8_byte_length == len(source_bytes), "byte length exact")
check(result_a.event.source_sha256 == hashlib.sha256(source_bytes).hexdigest(), "source hash exact")
check(result_a.observed_source_sha256 == result_a.event.source_sha256, "observed hash exact")
check(result_a.event.input_event_id == result_a.event.expected_id(), "event id stable")
check(result_a.result_id == result_a.expected_id(), "result id stable")
check(result_a.root_span.span_id == result_a.root_span.expected_id(), "root span id stable")
check(result_a.event.root_source_span_id == result_a.root_span.span_id, "root span referenced")
check(result_a.root_span.code_point_start == 0, "root code-point start")
check(result_a.root_span.code_point_end == len(source), "root code-point end")
check(result_a.root_span.utf8_byte_start == 0, "root byte start")
check(result_a.root_span.utf8_byte_end == len(source_bytes), "root byte end")
check(result_a.root_span.span_sha256 == result_a.event.source_sha256, "root span hash exact")
check(result_a.root_span.is_root_span is True, "root span marked")
check(len(result_a.event.utf8_boundary_offsets) == len(source) + 1, "boundary count exact")
check(result_a.event.utf8_boundary_offsets[0] == 0, "first boundary zero")
check(result_a.event.utf8_boundary_offsets[-1] == len(source_bytes), "last boundary byte length")
check(tuple(sorted(result_a.event.utf8_boundary_offsets)) == result_a.event.utf8_boundary_offsets, "boundaries monotonic")
check(result_a.event.source_preserved_exactly is True, "preservation flag true")
check(result_a.event.normalization_performed is False, "normalization false")
check(result_a.event.tokenization_performed is False, "tokenization false")
check(result_a.event.interpretation_performed is False, "interpretation false")
check(result_a.event.concept_lookup_performed is False, "concept lookup false")
check(result_a.event.reference_resolution_performed is False, "reference resolution false")
check(result_a.event.external_lookup_performed is False, "external lookup false")
check(result_a.event.unicode_database_version == UNICODE_DATABASE_VERSION, "event Unicode version exact")
check(validate_input_event(result_a.event).ok, "event validates")
check(validate_source_span(result_a.root_span, event=result_a.event).ok, "root span validates")
check(validate_input_event_capture_result(result_a).ok, "capture result validates")

# Same source with different custody metadata must not collapse identity.
sequence_changed = capture_input_event(source, source_id="user.nic", channel_id="chat.primary", sequence_number=8)
channel_changed = capture_input_event(source, source_id="user.nic", channel_id="chat.secondary", sequence_number=7)
source_changed = capture_input_event(source + "x", source_id="user.nic", channel_id="chat.primary", sequence_number=7)
check(sequence_changed.event.input_event_id != result_a.event.input_event_id, "sequence affects identity")
check(channel_changed.event.input_event_id != result_a.event.input_event_id, "channel affects identity")
check(source_changed.event.input_event_id != result_a.event.input_event_id, "source affects identity")

# Canonically similar Unicode must remain distinguishable; no normalization occurs.
composed = capture_input_event("é", source_id="user", channel_id="chat", sequence_number=1)
decomposed = capture_input_event("e\u0301", source_id="user", channel_id="chat", sequence_number=1)
check(composed.event.exact_received_text != decomposed.event.exact_received_text, "normalization variants remain distinct")
check(composed.event.source_sha256 != decomposed.event.source_sha256, "normalization hashes distinct")
check(composed.event.input_event_id != decomposed.event.input_event_id, "normalization ids distinct")

# Source spans preserve exact code-point and UTF-8 byte boundaries.
emoji_index = source.index("🌍")
emoji_span_result = build_source_span(
    result_a.event,
    code_point_start=emoji_index,
    code_point_end=emoji_index + 1,
)
check(emoji_span_result.ok, "emoji span built")
check(emoji_span_result.conditions == (), "emoji span no issues")
check(emoji_span_result.span.code_point_length == 1, "emoji code-point length one")
check(emoji_span_result.span.utf8_byte_length == 4, "emoji byte length four")
check(emoji_span_result.span.span_sha256 == hashlib.sha256("🌍".encode()).hexdigest(), "emoji span hash")
check(validate_source_span(emoji_span_result.span, event=result_a.event).ok, "emoji span validates")
empty_span_result = build_source_span(result_a.event, code_point_start=2, code_point_end=2)
check(empty_span_result.ok, "empty span lawful")
check(empty_span_result.span.code_point_length == 0, "empty span code-point length")
check(empty_span_result.span.utf8_byte_length == 0, "empty span byte length")
check(empty_span_result.span.span_sha256 == hashlib.sha256(b"").hexdigest(), "empty span hash")
invalid_span_type = build_source_span("not-event", code_point_start=0, code_point_end=0)
check(not invalid_span_type.ok, "invalid event typed failure")
check(invalid_span_type.conditions[0].code is InputConditionCode.INVALID_SPAN_EVENT_TYPE, "invalid event code")
invalid_span_offset = build_source_span(result_a.event, code_point_start=True, code_point_end=1)
check(not invalid_span_offset.ok, "bool span offset rejected")
check(invalid_span_offset.conditions[0].code is InputConditionCode.INVALID_SPAN_OFFSET_TYPE, "offset type code")
invalid_span_bounds = build_source_span(result_a.event, code_point_start=-1, code_point_end=1)
check(not invalid_span_bounds.ok, "negative span rejected")
check(invalid_span_bounds.conditions[0].code is InputConditionCode.INVALID_SPAN_BOUNDS, "bounds code")
reversed_span = build_source_span(result_a.event, code_point_start=3, code_point_end=2)
check(not reversed_span.ok, "reversed span rejected")
outside_span = build_source_span(result_a.event, code_point_start=0, code_point_end=len(source) + 1)
check(not outside_span.ok, "outside span rejected")

# Unsupported Unicode is preserved exactly but cannot progress.
unsupported_source = "A\x00B\u200bC\ue000D\ufdd0E\u0378F"
unsupported = capture_input_event(
    unsupported_source,
    source_id="user",
    channel_id="chat",
    sequence_number=2,
)
check(unsupported.status is InputCustodyStatus.CAPTURED_UNSUPPORTED, "unsupported status exact")
check(unsupported.custody_created is True, "unsupported custody created")
check(unsupported.structural_progression_allowed is False, "unsupported progression held")
check(unsupported.unsupported_input is True, "unsupported flag true")
check(unsupported.malformed_input is False, "unsupported not malformed")
check(unsupported.event.exact_received_text == unsupported_source, "unsupported source exact")
check(unsupported.event.source_sha256 == hashlib.sha256(unsupported_source.encode()).hexdigest(), "unsupported hash exact")
condition_codes = {condition.code for condition in unsupported.conditions}
check(InputConditionCode.UNSUPPORTED_CONTROL_CHARACTER in condition_codes, "control classified")
check(InputConditionCode.UNSUPPORTED_FORMAT_CHARACTER in condition_codes, "format classified")
check(InputConditionCode.UNSUPPORTED_PRIVATE_USE_CHARACTER in condition_codes, "private-use classified")
check(InputConditionCode.UNSUPPORTED_NONCHARACTER in condition_codes, "noncharacter classified")
check(InputConditionCode.UNSUPPORTED_UNASSIGNED_CHARACTER in condition_codes, "unassigned classified")
check(all(condition.category is InputConditionCategory.UNSUPPORTED for condition in unsupported.conditions), "unsupported categories exact")
check(all(condition.input_event_id == unsupported.event.input_event_id for condition in unsupported.conditions), "conditions event-bound")
check(all(validate_input_condition(condition).ok for condition in unsupported.conditions), "conditions validate")
check(unsupported.event.total_unsupported_condition_count == 5, "unsupported total exact")
check(len(unsupported.event.unsupported_condition_ids) == 5, "unsupported ids exact")
check(validate_input_event_capture_result(unsupported).ok, "unsupported result validates")
control_condition = next(c for c in unsupported.conditions if c.code is InputConditionCode.UNSUPPORTED_CONTROL_CHARACTER)
check(control_condition.code_point_start == 1, "control code-point start")
check(control_condition.code_point_end == 2, "control code-point end")
check(control_condition.utf8_byte_start == 1, "control byte start")
check(control_condition.utf8_byte_end == 2, "control byte end")
check(control_condition.unicode_code_point == "U+0000", "control Unicode label")

bounded_conditions = build_input_custody_limits(
    max_utf8_bytes=100,
    max_code_points=100,
    max_recorded_conditions=3,
    allow_empty=False,
)
condition_limited = capture_input_event(
    "\x00\x01\x02\x03\x04",
    source_id="user",
    channel_id="chat",
    sequence_number=3,
    limits=bounded_conditions,
)
check(condition_limited.status is InputCustodyStatus.CAPTURED_UNSUPPORTED, "condition-limited status")
check(condition_limited.event.total_unsupported_condition_count == 5, "condition-limited total exact")
check(len(condition_limited.conditions) == 3, "recorded conditions bounded")
check(condition_limited.conditions[-1].code is InputConditionCode.UNSUPPORTED_CONDITION_RECORDING_LIMIT_REACHED, "condition aggregate exact")

# Malformed caller values return typed deterministic results rather than exceptions.
malformed_cases = (
    (123, {"source_id": "user", "channel_id": "chat", "sequence_number": 1}, InputConditionCode.INVALID_SOURCE_TYPE),
    ([], {"source_id": "user", "channel_id": "chat", "sequence_number": 1}, InputConditionCode.INVALID_SOURCE_TYPE),
    ("", {"source_id": "user", "channel_id": "chat", "sequence_number": 1}, InputConditionCode.EMPTY_SOURCE_NOT_ALLOWED),
    ("x", {"source_id": "", "channel_id": "chat", "sequence_number": 1}, InputConditionCode.INVALID_SOURCE_ID),
    ("x", {"source_id": "user name", "channel_id": "chat", "sequence_number": 1}, InputConditionCode.INVALID_SOURCE_ID),
    ("x", {"source_id": "user", "channel_id": "", "sequence_number": 1}, InputConditionCode.INVALID_CHANNEL_ID),
    ("x", {"source_id": "user", "channel_id": "chat", "sequence_number": True}, InputConditionCode.INVALID_SEQUENCE_NUMBER),
    ("x", {"source_id": "user", "channel_id": "chat", "sequence_number": -1}, InputConditionCode.INVALID_SEQUENCE_NUMBER),
    ("x", {"source_id": "user", "channel_id": "chat", "sequence_number": MAX_SEQUENCE_NUMBER + 1}, InputConditionCode.INVALID_SEQUENCE_NUMBER),
    ("x", {"source_id": "user", "channel_id": "chat", "sequence_number": None}, InputConditionCode.MISSING_SEQUENCE_AND_CORRELATION),
    ("x", {"source_id": "user", "channel_id": "chat", "correlation_id": "bad value"}, InputConditionCode.INVALID_CORRELATION_ID),
)
for index, (case_source, kwargs, expected_code) in enumerate(malformed_cases):
    first = capture_input_event(case_source, **kwargs)
    second = capture_input_event(case_source, **kwargs)
    check(first == second, f"malformed deterministic {index}")
    check(first.status is InputCustodyStatus.REJECTED_MALFORMED, f"malformed status {index}")
    check(first.custody_created is False, f"malformed no event {index}")
    check(first.event is None and first.root_span is None, f"malformed records absent {index}")
    check(first.structural_progression_allowed is False, f"malformed progression held {index}")
    check(first.malformed_input is True, f"malformed flag {index}")
    check(any(condition.code is expected_code for condition in first.conditions), f"malformed code {index}")
    check(validate_input_event_capture_result(first).ok, f"malformed result valid {index}")

long_identity = "a" * (MAX_IDENTITY_CODE_POINTS + 1)
long_identity_result = capture_input_event("x", source_id=long_identity, channel_id="chat", sequence_number=1)
check(long_identity_result.status is InputCustodyStatus.REJECTED_MALFORMED, "long identity rejected")
check(any(c.code is InputConditionCode.INVALID_SOURCE_ID for c in long_identity_result.conditions), "long identity code")

surrogate_result = capture_input_event("a\ud800b", source_id="user", channel_id="chat", sequence_number=1)
check(surrogate_result.status is InputCustodyStatus.REJECTED_MALFORMED, "surrogate rejected")
check(any(c.code is InputConditionCode.SOURCE_CONTAINS_LONE_SURROGATE for c in surrogate_result.conditions), "surrogate code")
check(surrogate_result.observed_source_sha256 == "", "surrogate no false hash")

empty_allowed = capture_input_event(
    "",
    source_id="user",
    channel_id="chat",
    correlation_id="empty-event",
    limits=custom_limits,
)
check(empty_allowed.status is InputCustodyStatus.CAPTURED_SUPPORTED, "empty allowed by explicit limits")
check(empty_allowed.event.utf8_boundary_offsets == (0,), "empty boundary exact")
check(empty_allowed.root_span.code_point_length == 0, "empty root code-point length")

small_codepoint_limits = build_input_custody_limits(max_utf8_bytes=100, max_code_points=3, max_recorded_conditions=5)
codepoint_exceeded = capture_input_event("abcd", source_id="user", channel_id="chat", sequence_number=1, limits=small_codepoint_limits)
check(codepoint_exceeded.status is InputCustodyStatus.REJECTED_MALFORMED, "code-point limit rejected")
check(any(c.code is InputConditionCode.CODE_POINT_LIMIT_EXCEEDED for c in codepoint_exceeded.conditions), "code-point limit code")
check(codepoint_exceeded.observed_code_point_length == 4, "code-point observation exact")
check(codepoint_exceeded.observed_utf8_byte_length is None, "oversize code-point input not encoded")

small_byte_limits = build_input_custody_limits(max_utf8_bytes=3, max_code_points=10, max_recorded_conditions=5)
byte_exceeded = capture_input_event("🌍", source_id="user", channel_id="chat", sequence_number=1, limits=small_byte_limits)
check(byte_exceeded.status is InputCustodyStatus.REJECTED_MALFORMED, "byte limit rejected")
check(any(c.code is InputConditionCode.UTF8_BYTE_LIMIT_EXCEEDED for c in byte_exceeded.conditions), "byte limit code")
check(byte_exceeded.observed_utf8_byte_length == 4, "byte observation exact")
check(len(byte_exceeded.observed_source_sha256) == 64, "oversize byte input hashed exactly")

explicit_none_limits = capture_input_event("x", source_id="user", channel_id="chat", sequence_number=1, limits=None)
check(explicit_none_limits.status is InputCustodyStatus.REJECTED_MALFORMED, "explicit None limits rejected")
check(any(c.code is InputConditionCode.INVALID_LIMITS_TYPE for c in explicit_none_limits.conditions), "explicit None limits code")
invalid_limits = replace(limits_a, max_utf8_bytes=0)
invalid_limits_result = capture_input_event("x", source_id="user", channel_id="chat", sequence_number=1, limits=invalid_limits)
check(invalid_limits_result.status is InputCustodyStatus.REJECTED_MALFORMED, "tampered limits rejected")
check(any(c.code in {InputConditionCode.INVALID_LIMIT_RANGE, InputConditionCode.INVALID_LIMITS_TYPE} for c in invalid_limits_result.conditions), "tampered limits typed")

correlation_only = capture_input_event("x", source_id="user", channel_id="chat", correlation_id="correlation-only")
check(correlation_only.status is InputCustodyStatus.CAPTURED_SUPPORTED, "correlation-only accepted")
check(correlation_only.event.sequence_number is None, "correlation-only sequence absent")

# Validation rejects tampering and records are frozen.
tampered_event = replace(result_a.event, exact_received_text=result_a.event.exact_received_text + "x")
check(not validate_input_event(tampered_event).ok, "event source tampering rejected")
tampered_offsets = replace(result_a.event, utf8_boundary_offsets=(0,))
check(not validate_input_event(tampered_offsets).ok, "offset tampering rejected")
tampered_unicode_version = replace(result_a.event, unicode_database_version="0.0.0")
check(not validate_input_event(tampered_unicode_version).ok, "Unicode version tampering rejected")
tampered_result = replace(result_a, network_access_performed=True)
check(not validate_input_event_capture_result(tampered_result).ok, "network escalation rejected")
tampered_result_id = replace(result_a, result_id="bad")
check(not validate_input_event_capture_result(tampered_result_id).ok, "result id tampering rejected")
try:
    result_a.event.exact_received_text = "changed"  # type: ignore[misc]
except (FrozenInstanceError, AttributeError, TypeError):
    checks += 1
else:
    raise AssertionError("event is mutable")
try:
    result_a.status = InputCustodyStatus.REJECTED_MALFORMED  # type: ignore[misc]
except (FrozenInstanceError, AttributeError, TypeError):
    checks += 1
else:
    raise AssertionError("result is mutable")

# The enabled capture path must remain purely in-memory and offline.
with ExitStack() as stack:
    stack.enter_context(patch.object(Path, "read_text", forbidden))
    stack.enter_context(patch.object(Path, "read_bytes", forbidden))
    stack.enter_context(patch.object(Path, "write_text", forbidden))
    stack.enter_context(patch.object(Path, "write_bytes", forbidden))
    stack.enter_context(patch.object(builtins, "open", forbidden))
    stack.enter_context(patch.object(os, "getenv", forbidden))
    stack.enter_context(patch.object(os, "system", forbidden))
    stack.enter_context(patch.object(subprocess, "run", forbidden))
    stack.enter_context(patch.object(subprocess, "Popen", forbidden))
    stack.enter_context(patch.object(socket, "socket", forbidden))
    stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
    side_effect_probe = capture_input_event(
        "Offline exact source",
        source_id="fixture",
        channel_id="offline",
        sequence_number=99,
    )
check(side_effect_probe.status is InputCustodyStatus.CAPTURED_SUPPORTED, "side-effect trap capture passes")
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
    check(getattr(side_effect_probe, field_name) is False, f"result consequence false: {field_name}")

print("SLICE 36A BEHAVIOR TEST: PASS")
print(f"checks={checks}")
print(f"input_event_id={result_a.event.input_event_id}")
print(f"source_sha256={result_a.event.source_sha256}")
print(f"utf8_bytes={result_a.event.utf8_byte_length}")
print(f"code_points={result_a.event.code_point_length}")
print(f"unicode_database_version={UNICODE_DATABASE_VERSION}")
print("tokenization_interpretation_external_side_effects=0")
