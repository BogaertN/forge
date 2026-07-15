"""Immutable Slice 36B deterministic source-field projection records.

The records in this module preserve exact observable source structure only.
They do not tokenize language, identify vocabulary, assign grammatical roles,
bind RSOC operators, assign phases, create concepts or meanings, resolve
references, route tools, write memory, render output, or perform actions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final
import unicodedata

from ..input_event_custody import (
    ABSOLUTE_MAX_CODE_POINTS,
    DEFAULT_MAX_CODE_POINTS,
)
from ..schema import stable_record_id

PROJECTION_SPEC_ID: Final[str] = "aiweb-deterministic-source-field-projection"
PROJECTION_SPEC_VERSION: Final[str] = (
    "aiweb-deterministic-source-field-projection-v1"
)
PROJECTION_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-source-field-projection-v1"
)
SOURCE_FIELD_SCHEMA_ID: Final[str] = (
    "aiweb-source-preserving-resonant-language-field-v1"
)
PROJECTION_RULESET_ID: Final[str] = "aiweb-source-field-ruleset-36b"
PROJECTION_RULESET_VERSION: Final[str] = (
    "aiweb-source-field-ruleset-36b-v1"
)
GRAPHEME_PROFILE_ID: Final[str] = (
    "aiweb-exact-ascii-grapheme-boundary-profile-v1"
)
UNICODE_DATABASE_VERSION: Final[str] = unicodedata.unidata_version

DEFAULT_MAX_PROJECTION_CODE_POINTS: Final[int] = DEFAULT_MAX_CODE_POINTS
DEFAULT_MAX_PROJECTION_OBSERVATIONS: Final[int] = 524_288
ABSOLUTE_MAX_PROJECTION_CODE_POINTS: Final[int] = ABSOLUTE_MAX_CODE_POINTS
ABSOLUTE_MAX_PROJECTION_OBSERVATIONS: Final[int] = 2_097_152


class SourceFieldProjectionStatus(str, Enum):
    """Closed public result vocabulary required by Slice 36B."""

    SOURCE_FIELD_SUPPORTED = "SOURCE_FIELD_SUPPORTED"
    SOURCE_FIELD_PARTIALLY_UNSUPPORTED = (
        "SOURCE_FIELD_PARTIALLY_UNSUPPORTED"
    )
    SOURCE_FIELD_MALFORMED = "SOURCE_FIELD_MALFORMED"
    SOURCE_FIELD_LIMIT_EXCEEDED = "SOURCE_FIELD_LIMIT_EXCEEDED"
    SOURCE_FIELD_PROJECTION_FAILED = "SOURCE_FIELD_PROJECTION_FAILED"


class SourceFieldSupportStatus(str, Enum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"


class GraphemeBoundaryStatus(str, Enum):
    """Whether a code-point boundary is exact under the closed v1 profile."""

    EXACT_BOUNDARY = "exact_boundary"
    EXACT_NON_BOUNDARY = "exact_non_boundary"
    UNAVAILABLE = "unavailable"


class GraphemeProfileStatus(str, Enum):
    COMPLETE_EXACT_ASCII_PROFILE = "complete_exact_ascii_profile"
    PARTIAL_CODE_POINT_FALLBACK = "partial_code_point_fallback"


class SourceObservationKind(str, Enum):
    """Observable surface forms only; none carry semantic authority."""

    GRAPHEME_CLUSTER = "grapheme_cluster"
    VISIBLE_WHITESPACE = "visible_whitespace"
    REPEATED_WHITESPACE = "repeated_whitespace"
    TAB = "tab"
    LINE_BREAK = "line_break"
    PARAGRAPH_BOUNDARY = "paragraph_boundary"
    PUNCTUATION_MARK = "punctuation_mark"
    DELIMITER_MARK = "delimiter_mark"
    QUOTATION_MARK = "quotation_mark"
    OPERATOR_LIKE_SYMBOL = "operator_like_symbol"
    CONTROL_CHARACTER = "control_character"
    UNSUPPORTED_CODE_POINT = "unsupported_code_point"


@dataclass(frozen=True, slots=True)
class SourceFieldProjectionLimits:
    """Caller-declared projection bounds constrained by hard ceilings."""

    limits_id: str
    max_code_points: int
    max_observations: int
    projection_spec_id: str = PROJECTION_SPEC_ID
    projection_spec_version: str = PROJECTION_SPEC_VERSION
    schema_version: str = PROJECTION_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("limits_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "source_field_projection_limits",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceCodePointRecord:
    """One exact Unicode scalar and its source coordinates."""

    atom_id: str
    projection_id: str
    source_event_id: str
    ordinal: int
    exact_text: str
    unicode_code_point: str
    utf8_hex: str
    code_point_start: int
    code_point_end: int
    utf8_byte_start: int
    utf8_byte_end: int
    source_span_id: str
    general_category: str
    unicode_name: str
    combining_class: int
    support_status: SourceFieldSupportStatus
    unsupported_reason_code: str
    previous_atom_id: str | None
    next_atom_id: str | None
    rule_id: str
    rule_version: str
    projection_spec_id: str = PROJECTION_SPEC_ID
    projection_spec_version: str = PROJECTION_SPEC_VERSION
    schema_version: str = PROJECTION_SCHEMA_VERSION

    def identity_body(self) -> dict[str, object]:
        return {
            "projection_id": self.projection_id,
            "source_event_id": self.source_event_id,
            "ordinal": self.ordinal,
            "exact_text": self.exact_text,
            "unicode_code_point": self.unicode_code_point,
            "utf8_hex": self.utf8_hex,
            "code_point_start": self.code_point_start,
            "code_point_end": self.code_point_end,
            "utf8_byte_start": self.utf8_byte_start,
            "utf8_byte_end": self.utf8_byte_end,
            "source_span_id": self.source_span_id,
            "rule_id": self.rule_id,
            "rule_version": self.rule_version,
            "projection_spec_id": self.projection_spec_id,
            "projection_spec_version": self.projection_spec_version,
            "schema_version": self.schema_version,
        }

    def expected_id(self) -> str:
        return stable_record_id("source_code_point", self.identity_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceBoundaryRecord:
    """One exact code-point/byte boundary with conservative grapheme status."""

    boundary_id: str
    projection_id: str
    source_event_id: str
    ordinal: int
    code_point_offset: int
    utf8_byte_offset: int
    previous_atom_id: str | None
    next_atom_id: str | None
    grapheme_boundary_status: GraphemeBoundaryStatus
    rule_id: str
    rule_version: str
    projection_spec_id: str = PROJECTION_SPEC_ID
    projection_spec_version: str = PROJECTION_SPEC_VERSION
    schema_version: str = PROJECTION_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("boundary_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("source_boundary", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceObservationRecord:
    """A deterministic visible-source observation without meaning authority."""

    observation_id: str
    projection_id: str
    source_event_id: str
    ordinal: int
    kind: SourceObservationKind
    observation_value: str
    exact_text: str
    utf8_hex: str
    code_point_start: int
    code_point_end: int
    utf8_byte_start: int
    utf8_byte_end: int
    source_span_id: str
    member_atom_ids: tuple[str, ...]
    repeat_count: int
    support_status: SourceFieldSupportStatus
    semantic_authority: bool
    operator_binding_authority: bool
    rule_id: str
    rule_version: str
    projection_spec_id: str = PROJECTION_SPEC_ID
    projection_spec_version: str = PROJECTION_SPEC_VERSION
    schema_version: str = PROJECTION_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("observation_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("source_observation", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceFieldProjectionRecord:
    """Exact source projection linked to the immutable 36B0 root envelope."""

    projection_id: str
    source_event_id: str
    source_sha256: str
    source_utf8_byte_length: int
    source_code_point_length: int
    root_source_span_id: str
    predecessor_field_build_result_id: str
    predecessor_field_envelope_id: str | None
    limits_id: str
    status: SourceFieldProjectionStatus
    code_points: tuple[SourceCodePointRecord, ...]
    boundaries: tuple[SourceBoundaryRecord, ...]
    observations: tuple[SourceObservationRecord, ...]
    code_point_count: int
    boundary_count: int
    observation_count: int
    unsupported_code_point_count: int
    grapheme_profile_id: str
    grapheme_profile_status: GraphemeProfileStatus
    unicode_database_version: str
    source_coverage_complete: bool
    source_ordering_complete: bool
    source_adjacency_complete: bool
    exact_reconstruction_proven: bool
    reconstructed_source_sha256: str
    structural_progression_allowed: bool
    operator_application_available: bool
    source_text_replaced: bool
    normalization_performed: bool
    casefolding_performed: bool
    whitespace_collapse_performed: bool
    transliteration_performed: bool
    tokenization_performed: bool
    vocabulary_lookup_performed: bool
    part_of_speech_tagging_performed: bool
    concept_lookup_performed: bool
    predicate_binding_performed: bool
    reference_resolution_performed: bool
    operator_binding_performed: bool
    operator_application_performed: bool
    phase_assignment_performed: bool
    intention_inference_performed: bool
    meaning_created: bool
    legacy_runtime_consulted: bool
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
    projection_spec_id: str = PROJECTION_SPEC_ID
    projection_spec_version: str = PROJECTION_SPEC_VERSION
    schema_version: str = PROJECTION_SCHEMA_VERSION
    source_field_schema_id: str = SOURCE_FIELD_SCHEMA_ID

    def identity_body(self) -> dict[str, object]:
        return {
            "source_event_id": self.source_event_id,
            "source_sha256": self.source_sha256,
            "source_utf8_byte_length": self.source_utf8_byte_length,
            "source_code_point_length": self.source_code_point_length,
            "root_source_span_id": self.root_source_span_id,
            "predecessor_field_build_result_id": (
                self.predecessor_field_build_result_id
            ),
            "predecessor_field_envelope_id": (
                self.predecessor_field_envelope_id
            ),
            "limits_id": self.limits_id,
            "projection_spec_id": self.projection_spec_id,
            "projection_spec_version": self.projection_spec_version,
            "schema_version": self.schema_version,
            "source_field_schema_id": self.source_field_schema_id,
        }

    def expected_id(self) -> str:
        return stable_record_id("source_field_projection", self.identity_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceFieldProjectionResult:
    """Typed, exception-free public result for one projection attempt."""

    result_id: str
    status: SourceFieldProjectionStatus
    reason_code: str
    projection_created: bool
    structural_progression_allowed: bool
    source_preserved_in_custody: bool
    source_event_id: str
    source_sha256: str
    limits: SourceFieldProjectionLimits | None
    projection: SourceFieldProjectionRecord | None
    validation_issue_codes: tuple[str, ...]
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
    projection_spec_id: str = PROJECTION_SPEC_ID
    projection_spec_version: str = PROJECTION_SPEC_VERSION
    schema_version: str = PROJECTION_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reason_code": self.reason_code,
            "projection_created": self.projection_created,
            "structural_progression_allowed": (
                self.structural_progression_allowed
            ),
            "source_preserved_in_custody": self.source_preserved_in_custody,
            "source_event_id": self.source_event_id,
            "source_sha256": self.source_sha256,
            "limits_id": self.limits.limits_id if self.limits else "",
            "projection_id": (
                self.projection.projection_id if self.projection else ""
            ),
            "validation_issue_codes": self.validation_issue_codes,
            "filesystem_read_performed": self.filesystem_read_performed,
            "filesystem_write_performed": self.filesystem_write_performed,
            "network_access_performed": self.network_access_performed,
            "environment_access_performed": self.environment_access_performed,
            "memory_read_performed": self.memory_read_performed,
            "memory_write_performed": self.memory_write_performed,
            "route_registration_performed": self.route_registration_performed,
            "tool_routing_performed": self.tool_routing_performed,
            "action_performed": self.action_performed,
            "delivery_performed": self.delivery_performed,
            "projection_spec_id": self.projection_spec_id,
            "projection_spec_version": self.projection_spec_version,
            "schema_version": self.schema_version,
        }

    def expected_id(self) -> str:
        return stable_record_id(
            "source_field_projection_result",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceFieldReconstructionResult:
    """Typed proof that a projection reconstructs the exact original bytes."""

    result_id: str
    ok: bool
    reason_code: str
    projection_id: str
    reconstructed_text: str
    reconstructed_utf8_hex: str
    reconstructed_utf8_byte_length: int
    reconstructed_code_point_length: int
    reconstructed_source_sha256: str
    validation_issue_codes: tuple[str, ...]
    projection_spec_id: str = PROJECTION_SPEC_ID
    projection_spec_version: str = PROJECTION_SPEC_VERSION
    schema_version: str = PROJECTION_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "source_field_reconstruction_result",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
