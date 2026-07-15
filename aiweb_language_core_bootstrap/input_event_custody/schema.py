"""Immutable schema records for Slice 36A input-event source custody.

The records in this module preserve source input and custody metadata only.
They do not tokenize, normalize, interpret, resolve, route, persist, or execute.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final
import unicodedata

from ..schema import stable_record_id

CUSTODY_SPEC_ID: Final[str] = "aiweb-input-event-source-custody"
CUSTODY_SPEC_VERSION: Final[str] = "aiweb-input-event-source-custody-v1"
CUSTODY_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-input-event-source-custody-v1"
)

DEFAULT_MAX_UTF8_BYTES: Final[int] = 262_144
DEFAULT_MAX_CODE_POINTS: Final[int] = 131_072
DEFAULT_MAX_RECORDED_CONDITIONS: Final[int] = 256
ABSOLUTE_MAX_UTF8_BYTES: Final[int] = 1_048_576
ABSOLUTE_MAX_CODE_POINTS: Final[int] = 262_144
ABSOLUTE_MAX_RECORDED_CONDITIONS: Final[int] = 4_096
MAX_IDENTITY_CODE_POINTS: Final[int] = 128
MAX_SEQUENCE_NUMBER: Final[int] = (1 << 63) - 1
UNICODE_DATABASE_VERSION: Final[str] = unicodedata.unidata_version


class InputCustodyStatus(str, Enum):
    """Closed status vocabulary for one custody attempt."""

    CAPTURED_SUPPORTED = "captured_supported_input"
    CAPTURED_UNSUPPORTED = "captured_unsupported_input"
    REJECTED_MALFORMED = "rejected_malformed_input"


class InputConditionCategory(str, Enum):
    """Whether a condition prevents capture or later progression."""

    MALFORMED = "malformed"
    UNSUPPORTED = "unsupported"


class InputConditionCode(str, Enum):
    """Closed deterministic condition vocabulary."""

    INVALID_LIMITS_TYPE = "invalid_limits_type"
    INVALID_LIMIT_TYPE = "invalid_limit_type"
    INVALID_LIMIT_RANGE = "invalid_limit_range"
    DECLARED_LIMIT_EXCEEDS_ABSOLUTE_MAXIMUM = (
        "declared_limit_exceeds_absolute_maximum"
    )
    INVALID_SOURCE_TYPE = "invalid_source_type"
    SOURCE_CONTAINS_LONE_SURROGATE = "source_contains_lone_surrogate"
    EMPTY_SOURCE_NOT_ALLOWED = "empty_source_not_allowed"
    CODE_POINT_LIMIT_EXCEEDED = "code_point_limit_exceeded"
    UTF8_BYTE_LIMIT_EXCEEDED = "utf8_byte_limit_exceeded"
    INVALID_SOURCE_ID = "invalid_source_id"
    INVALID_CHANNEL_ID = "invalid_channel_id"
    INVALID_SEQUENCE_NUMBER = "invalid_sequence_number"
    INVALID_CORRELATION_ID = "invalid_correlation_id"
    MISSING_SEQUENCE_AND_CORRELATION = "missing_sequence_and_correlation"
    UNSUPPORTED_CONTROL_CHARACTER = "unsupported_control_character"
    UNSUPPORTED_FORMAT_CHARACTER = "unsupported_format_character"
    UNSUPPORTED_PRIVATE_USE_CHARACTER = "unsupported_private_use_character"
    UNSUPPORTED_UNASSIGNED_CHARACTER = "unsupported_unassigned_character"
    UNSUPPORTED_NONCHARACTER = "unsupported_noncharacter"
    UNSUPPORTED_CONDITION_RECORDING_LIMIT_REACHED = (
        "unsupported_condition_recording_limit_reached"
    )
    INVALID_SPAN_EVENT_TYPE = "invalid_span_event_type"
    INVALID_SPAN_OFFSET_TYPE = "invalid_span_offset_type"
    INVALID_SPAN_BOUNDS = "invalid_span_bounds"


@dataclass(frozen=True, slots=True)
class InputCustodyLimits:
    """Caller-declared limits constrained by immutable hard ceilings."""

    limits_id: str
    max_utf8_bytes: int
    max_code_points: int
    max_recorded_conditions: int
    allow_empty: bool
    custody_spec_id: str = CUSTODY_SPEC_ID
    custody_spec_version: str = CUSTODY_SPEC_VERSION
    schema_version: str = CUSTODY_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("limits_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("input_custody_limits", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class InputConditionRecord:
    """Typed malformed or unsupported condition with exact source offsets."""

    condition_id: str
    input_event_id: str
    category: InputConditionCategory
    code: InputConditionCode
    field: str
    rule_id: str
    detail: str
    code_point_start: int | None
    code_point_end: int | None
    utf8_byte_start: int | None
    utf8_byte_end: int | None
    unicode_code_point: str
    custody_spec_id: str = CUSTODY_SPEC_ID
    custody_spec_version: str = CUSTODY_SPEC_VERSION
    schema_version: str = CUSTODY_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("condition_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("input_condition", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceSpanRecord:
    """Source-bound code-point and UTF-8 byte interval."""

    span_id: str
    input_event_id: str
    source_sha256: str
    code_point_start: int
    code_point_end: int
    utf8_byte_start: int
    utf8_byte_end: int
    code_point_length: int
    utf8_byte_length: int
    span_sha256: str
    is_root_span: bool
    custody_spec_id: str = CUSTODY_SPEC_ID
    custody_spec_version: str = CUSTODY_SPEC_VERSION
    schema_version: str = CUSTODY_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("span_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("source_span", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class InputEventRecord:
    """Exact immutable custody record for one successfully captured input."""

    input_event_id: str
    exact_received_text: str
    source_id: str
    channel_id: str
    sequence_number: int | None
    correlation_id: str | None
    utf8_byte_length: int
    code_point_length: int
    source_sha256: str
    utf8_boundary_offsets: tuple[int, ...]
    root_source_span_id: str
    limits_id: str
    custody_status: InputCustodyStatus
    malformed_condition_ids: tuple[str, ...]
    unsupported_condition_ids: tuple[str, ...]
    total_unsupported_condition_count: int
    source_preserved_exactly: bool
    normalization_performed: bool
    tokenization_performed: bool
    interpretation_performed: bool
    concept_lookup_performed: bool
    reference_resolution_performed: bool
    external_lookup_performed: bool
    unicode_database_version: str
    custody_spec_id: str = CUSTODY_SPEC_ID
    custody_spec_version: str = CUSTODY_SPEC_VERSION
    schema_version: str = CUSTODY_SCHEMA_VERSION

    def identity_body(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "channel_id": self.channel_id,
            "sequence_number": self.sequence_number,
            "correlation_id": self.correlation_id,
            "utf8_byte_length": self.utf8_byte_length,
            "code_point_length": self.code_point_length,
            "source_sha256": self.source_sha256,
            "limits_id": self.limits_id,
            "unicode_database_version": self.unicode_database_version,
            "custody_spec_id": self.custody_spec_id,
            "custody_spec_version": self.custody_spec_version,
            "schema_version": self.schema_version,
        }

    def expected_id(self) -> str:
        return stable_record_id("input_event", self.identity_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class InputEventCaptureResult:
    """Typed, exception-free public result for a custody attempt."""

    result_id: str
    status: InputCustodyStatus
    reason_code: str
    custody_created: bool
    structural_progression_allowed: bool
    malformed_input: bool
    unsupported_input: bool
    observed_utf8_byte_length: int | None
    observed_code_point_length: int | None
    observed_source_sha256: str
    limits: InputCustodyLimits | None
    event: InputEventRecord | None
    root_span: SourceSpanRecord | None
    conditions: tuple[InputConditionRecord, ...]
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    environment_access_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    route_registration_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    delivery_performed: bool
    custody_spec_id: str = CUSTODY_SPEC_ID
    custody_spec_version: str = CUSTODY_SPEC_VERSION
    schema_version: str = CUSTODY_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("input_event_capture_result", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceSpanBuildResult:
    """Typed result for constructing a non-interpreted source span."""

    result_id: str
    ok: bool
    reason_code: str
    span: SourceSpanRecord | None
    conditions: tuple[InputConditionRecord, ...]
    custody_spec_id: str = CUSTODY_SPEC_ID
    custody_spec_version: str = CUSTODY_SPEC_VERSION
    schema_version: str = CUSTODY_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("source_span_build_result", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
