"""Deterministic, reversible, non-semantic source-field projection.

Projection consumes one validated Slice 36A input-event record. It creates
code-point atoms, exact code-point/byte boundaries, and closed visible-source
observations. It does not group words, identify vocabulary, assign grammatical
roles, bind or apply RSOC operators, assign phases, or create meaning.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib
import unicodedata
from typing import Final

from ..input_event_custody import (
    CUSTODY_SCHEMA_VERSION,
    CUSTODY_SPEC_ID,
    CUSTODY_SPEC_VERSION,
    InputCustodyStatus,
    InputEventRecord,
    validate_input_event,
)
from ..resonant_language_operator_contract import (
    FieldEnvelopeBuildStatus,
    build_unprojected_language_field,
)
from ..schema import stable_record_id
from .schema import (
    ABSOLUTE_MAX_PROJECTION_CODE_POINTS,
    ABSOLUTE_MAX_PROJECTION_OBSERVATIONS,
    DEFAULT_MAX_PROJECTION_CODE_POINTS,
    DEFAULT_MAX_PROJECTION_OBSERVATIONS,
    GRAPHEME_PROFILE_ID,
    PROJECTION_RULESET_ID,
    PROJECTION_RULESET_VERSION,
    PROJECTION_SCHEMA_VERSION,
    PROJECTION_SPEC_ID,
    PROJECTION_SPEC_VERSION,
    SOURCE_FIELD_SCHEMA_ID,
    UNICODE_DATABASE_VERSION,
    GraphemeBoundaryStatus,
    GraphemeProfileStatus,
    SourceBoundaryRecord,
    SourceCodePointRecord,
    SourceFieldProjectionLimits,
    SourceFieldProjectionRecord,
    SourceFieldProjectionResult,
    SourceFieldProjectionStatus,
    SourceFieldSupportStatus,
    SourceObservationKind,
    SourceObservationRecord,
)

_DEFAULT_LIMITS_SENTINEL: Final[object] = object()
_ALLOWED_CONTROL_CHARACTERS: Final[frozenset[str]] = frozenset(
    ("\t", "\n", "\r")
)
_LINE_BREAK_CHARACTERS: Final[frozenset[str]] = frozenset(
    ("\n", "\r", "\u0085", "\u2028", "\u2029")
)
_DELIMITER_VALUES: Final[dict[str, str]] = {
    "(": "opening_parenthesis",
    ")": "closing_parenthesis",
    "[": "opening_bracket",
    "]": "closing_bracket",
    "{": "opening_brace",
    "}": "closing_brace",
}
_QUOTE_CHARACTERS: Final[frozenset[str]] = frozenset(
    (
        "'",
        '"',
        "`",
        "\u00ab",
        "\u00bb",
        "\u2018",
        "\u2019",
        "\u201a",
        "\u201b",
        "\u201c",
        "\u201d",
        "\u201e",
        "\u201f",
        "\u2039",
        "\u203a",
        "\u300c",
        "\u300d",
        "\u300e",
        "\u300f",
    )
)
_OPERATOR_LIKE_ASCII: Final[frozenset[str]] = frozenset(
    "+-*/%=<>|&^~!?:\\"
)

_RULE_CODE_POINT: Final[str] = "AIWEB-36B-CODEPOINT-001"
_RULE_BOUNDARY: Final[str] = "AIWEB-36B-BOUNDARY-001"
_RULE_GRAPHEME: Final[str] = "AIWEB-36B-GRAPHEME-ASCII-001"
_RULE_WHITESPACE: Final[str] = "AIWEB-36B-WHITESPACE-001"
_RULE_LINE: Final[str] = "AIWEB-36B-LINEBREAK-001"
_RULE_PARAGRAPH: Final[str] = "AIWEB-36B-PARAGRAPH-001"
_RULE_PUNCTUATION: Final[str] = "AIWEB-36B-PUNCTUATION-001"
_RULE_DELIMITER: Final[str] = "AIWEB-36B-DELIMITER-001"
_RULE_QUOTE: Final[str] = "AIWEB-36B-QUOTE-001"
_RULE_SYMBOL: Final[str] = "AIWEB-36B-SYMBOL-001"
_RULE_CONTROL: Final[str] = "AIWEB-36B-CONTROL-001"
_RULE_UNSUPPORTED: Final[str] = "AIWEB-36B-UNSUPPORTED-001"


def _exact_int(value: object) -> bool:
    return type(value) is int


def default_source_field_projection_limits() -> SourceFieldProjectionLimits:
    """Return the deterministic default projection limits."""

    body = {
        "max_code_points": DEFAULT_MAX_PROJECTION_CODE_POINTS,
        "max_observations": DEFAULT_MAX_PROJECTION_OBSERVATIONS,
        "projection_spec_id": PROJECTION_SPEC_ID,
        "projection_spec_version": PROJECTION_SPEC_VERSION,
        "schema_version": PROJECTION_SCHEMA_VERSION,
    }
    return SourceFieldProjectionLimits(
        limits_id=stable_record_id("source_field_projection_limits", body),
        **body,
    )


def build_source_field_projection_limits(
    *,
    max_code_points: object = DEFAULT_MAX_PROJECTION_CODE_POINTS,
    max_observations: object = DEFAULT_MAX_PROJECTION_OBSERVATIONS,
) -> SourceFieldProjectionLimits | None:
    """Build limits when values are exact integers within hard ceilings.

    ``None`` is returned for invalid values. Projection itself always returns a
    richer typed disposition when supplied an invalid limits object.
    """

    if not _exact_int(max_code_points) or not _exact_int(max_observations):
        return None
    if not 0 <= max_code_points <= ABSOLUTE_MAX_PROJECTION_CODE_POINTS:
        return None
    if not 0 <= max_observations <= ABSOLUTE_MAX_PROJECTION_OBSERVATIONS:
        return None
    body = {
        "max_code_points": max_code_points,
        "max_observations": max_observations,
        "projection_spec_id": PROJECTION_SPEC_ID,
        "projection_spec_version": PROJECTION_SPEC_VERSION,
        "schema_version": PROJECTION_SCHEMA_VERSION,
    }
    return SourceFieldProjectionLimits(
        limits_id=stable_record_id("source_field_projection_limits", body),
        **body,
    )


def _limits_issue_codes(limits: object) -> tuple[str, ...]:
    if type(limits) is not SourceFieldProjectionLimits:
        return ("invalid_projection_limits_type",)
    issues: list[str] = []
    if limits.projection_spec_id != PROJECTION_SPEC_ID:
        issues.append("projection_spec_id_mismatch")
    if limits.projection_spec_version != PROJECTION_SPEC_VERSION:
        issues.append("projection_spec_version_mismatch")
    if limits.schema_version != PROJECTION_SCHEMA_VERSION:
        issues.append("projection_schema_version_mismatch")
    if limits.limits_id != limits.expected_id():
        issues.append("projection_limits_id_mismatch")
    if not _exact_int(limits.max_code_points):
        issues.append("invalid_max_code_points_type")
    elif limits.max_code_points < 0:
        issues.append("invalid_max_code_points_range")
    elif limits.max_code_points > ABSOLUTE_MAX_PROJECTION_CODE_POINTS:
        issues.append("max_code_points_exceeds_absolute_maximum")
    if not _exact_int(limits.max_observations):
        issues.append("invalid_max_observations_type")
    elif limits.max_observations < 0:
        issues.append("invalid_max_observations_range")
    elif limits.max_observations > ABSOLUTE_MAX_PROJECTION_OBSERVATIONS:
        issues.append("max_observations_exceeds_absolute_maximum")
    return tuple(issues)


def _result(
    *,
    status: SourceFieldProjectionStatus,
    reason_code: str,
    projection_created: bool,
    structural_progression_allowed: bool,
    source_preserved_in_custody: bool,
    source_event_id: str,
    source_sha256: str,
    limits: SourceFieldProjectionLimits | None,
    projection: SourceFieldProjectionRecord | None,
    validation_issue_codes: tuple[str, ...],
) -> SourceFieldProjectionResult:
    body = {
        "status": status,
        "reason_code": reason_code,
        "projection_created": projection_created,
        "structural_progression_allowed": structural_progression_allowed,
        "source_preserved_in_custody": source_preserved_in_custody,
        "source_event_id": source_event_id,
        "source_sha256": source_sha256,
        "limits": limits,
        "projection": projection,
        "validation_issue_codes": validation_issue_codes,
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
        "projection_spec_id": PROJECTION_SPEC_ID,
        "projection_spec_version": PROJECTION_SPEC_VERSION,
        "schema_version": PROJECTION_SCHEMA_VERSION,
    }
    result = SourceFieldProjectionResult(
        result_id="",
        **body,
    )
    return replace(result, result_id=result.expected_id())


def _is_noncharacter(code_point: int) -> bool:
    return (
        0xFDD0 <= code_point <= 0xFDEF
        or (code_point & 0xFFFF) in {0xFFFE, 0xFFFF}
    )


def _unsupported_reason(character: str) -> str:
    code_point = ord(character)
    if _is_noncharacter(code_point):
        return "unsupported_noncharacter"
    category = unicodedata.category(character)
    if category == "Cc" and character not in _ALLOWED_CONTROL_CHARACTERS:
        return "unsupported_control_character"
    if category == "Cf":
        return "unsupported_format_character"
    if category == "Co":
        return "unsupported_private_use_character"
    if category == "Cn":
        return "unsupported_unassigned_character"
    return ""


def _span_id(
    event: InputEventRecord,
    start: int,
    end: int,
    cache: dict[tuple[int, int], str] | None = None,
) -> str:
    key = (start, end)
    if cache is not None and key in cache:
        return cache[key]
    if not 0 <= start <= end <= event.code_point_length:
        raise ValueError("source_span_construction_failed")
    byte_start = event.utf8_boundary_offsets[start]
    byte_end = event.utf8_boundary_offsets[end]
    exact_text = event.exact_received_text[start:end]
    body = {
        "input_event_id": event.input_event_id,
        "source_sha256": event.source_sha256,
        "code_point_start": start,
        "code_point_end": end,
        "utf8_byte_start": byte_start,
        "utf8_byte_end": byte_end,
        "code_point_length": end - start,
        "utf8_byte_length": byte_end - byte_start,
        "span_sha256": hashlib.sha256(
            exact_text.encode("utf-8", "strict")
        ).hexdigest(),
        "is_root_span": start == 0 and end == event.code_point_length,
        "custody_spec_id": CUSTODY_SPEC_ID,
        "custody_spec_version": CUSTODY_SPEC_VERSION,
        "schema_version": CUSTODY_SCHEMA_VERSION,
    }
    span_id = stable_record_id("source_span", body)
    if cache is not None:
        cache[key] = span_id
    return span_id


def _projection_identity(
    *,
    event: InputEventRecord,
    predecessor_result_id: str,
    predecessor_field_id: str | None,
    limits: SourceFieldProjectionLimits,
) -> dict[str, object]:
    return {
        "source_event_id": event.input_event_id,
        "source_sha256": event.source_sha256,
        "source_utf8_byte_length": event.utf8_byte_length,
        "source_code_point_length": event.code_point_length,
        "root_source_span_id": event.root_source_span_id,
        "predecessor_field_build_result_id": predecessor_result_id,
        "predecessor_field_envelope_id": predecessor_field_id,
        "limits_id": limits.limits_id,
        "projection_spec_id": PROJECTION_SPEC_ID,
        "projection_spec_version": PROJECTION_SPEC_VERSION,
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "source_field_schema_id": SOURCE_FIELD_SCHEMA_ID,
    }


def _atom_identity_body(
    *,
    projection_id: str,
    event: InputEventRecord,
    ordinal: int,
    character: str,
    source_span_id: str,
) -> dict[str, object]:
    start = ordinal
    end = ordinal + 1
    return {
        "projection_id": projection_id,
        "source_event_id": event.input_event_id,
        "ordinal": ordinal,
        "exact_text": character,
        "unicode_code_point": f"U+{ord(character):04X}",
        "utf8_hex": character.encode("utf-8", "strict").hex(),
        "code_point_start": start,
        "code_point_end": end,
        "utf8_byte_start": event.utf8_boundary_offsets[start],
        "utf8_byte_end": event.utf8_boundary_offsets[end],
        "source_span_id": source_span_id,
        "rule_id": _RULE_CODE_POINT,
        "rule_version": PROJECTION_RULESET_VERSION,
        "projection_spec_id": PROJECTION_SPEC_ID,
        "projection_spec_version": PROJECTION_SPEC_VERSION,
        "schema_version": PROJECTION_SCHEMA_VERSION,
    }


def _line_break_units(text: str) -> tuple[tuple[int, int, str], ...]:
    units: list[tuple[int, int, str]] = []
    index = 0
    while index < len(text):
        character = text[index]
        if character == "\r" and index + 1 < len(text) and text[index + 1] == "\n":
            units.append((index, index + 2, "crlf"))
            index += 2
            continue
        if character in _LINE_BREAK_CHARACTERS:
            values = {
                "\r": "carriage_return",
                "\n": "line_feed",
                "\u0085": "next_line",
                "\u2028": "line_separator",
                "\u2029": "paragraph_separator",
            }
            units.append((index, index + 1, values[character]))
        index += 1
    return tuple(units)


def _horizontal_whitespace(character: str) -> bool:
    return character.isspace() and character not in _LINE_BREAK_CHARACTERS


def _observation_drafts(
    *,
    event: InputEventRecord,
    atom_ids: tuple[str, ...],
    atom_support: tuple[SourceFieldSupportStatus, ...],
    span_cache: dict[tuple[int, int], str],
) -> list[dict[str, object]]:
    text = event.exact_received_text
    drafts: list[dict[str, object]] = []

    def add(
        *,
        kind: SourceObservationKind,
        value: str,
        start: int,
        end: int,
        repeat_count: int,
        rule_id: str,
    ) -> None:
        exact = text[start:end]
        support = (
            SourceFieldSupportStatus.UNSUPPORTED
            if any(
                item is SourceFieldSupportStatus.UNSUPPORTED
                for item in atom_support[start:end]
            )
            else SourceFieldSupportStatus.SUPPORTED
        )
        drafts.append(
            {
                "kind": kind,
                "observation_value": value,
                "exact_text": exact,
                "utf8_hex": exact.encode("utf-8", "strict").hex(),
                "code_point_start": start,
                "code_point_end": end,
                "utf8_byte_start": event.utf8_boundary_offsets[start],
                "utf8_byte_end": event.utf8_boundary_offsets[end],
                "source_span_id": _span_id(
                    event,
                    start,
                    end,
                    span_cache,
                ),
                "member_atom_ids": atom_ids[start:end],
                "repeat_count": repeat_count,
                "support_status": support,
                "semantic_authority": False,
                "operator_binding_authority": False,
                "rule_id": rule_id,
                "rule_version": PROJECTION_RULESET_VERSION,
            }
        )

    # Exact ASCII grapheme clusters. Non-ASCII boundaries are deliberately not
    # guessed because the standard library does not expose the complete UAX #29
    # property tables required for authoritative segmentation.
    index = 0
    while index < len(text):
        character = text[index]
        if ord(character) < 128:
            if character == "\r" and index + 1 < len(text) and text[index + 1] == "\n":
                add(
                    kind=SourceObservationKind.GRAPHEME_CLUSTER,
                    value="ascii_crlf_cluster",
                    start=index,
                    end=index + 2,
                    repeat_count=1,
                    rule_id=_RULE_GRAPHEME,
                )
                index += 2
                continue
            add(
                kind=SourceObservationKind.GRAPHEME_CLUSTER,
                value="ascii_single_code_point_cluster",
                start=index,
                end=index + 1,
                repeat_count=1,
                rule_id=_RULE_GRAPHEME,
            )
        index += 1

    for ordinal, character in enumerate(text):
        category = unicodedata.category(character)
        reason = _unsupported_reason(character)
        if reason:
            add(
                kind=SourceObservationKind.UNSUPPORTED_CODE_POINT,
                value=reason,
                start=ordinal,
                end=ordinal + 1,
                repeat_count=1,
                rule_id=_RULE_UNSUPPORTED,
            )
        if category == "Cc":
            add(
                kind=SourceObservationKind.CONTROL_CHARACTER,
                value=f"control_{ord(character):04x}",
                start=ordinal,
                end=ordinal + 1,
                repeat_count=1,
                rule_id=_RULE_CONTROL,
            )
        if character == "\t":
            add(
                kind=SourceObservationKind.TAB,
                value="horizontal_tab",
                start=ordinal,
                end=ordinal + 1,
                repeat_count=1,
                rule_id=_RULE_WHITESPACE,
            )
        elif _horizontal_whitespace(character):
            add(
                kind=SourceObservationKind.VISIBLE_WHITESPACE,
                value="horizontal_whitespace",
                start=ordinal,
                end=ordinal + 1,
                repeat_count=1,
                rule_id=_RULE_WHITESPACE,
            )
        if category.startswith("P"):
            add(
                kind=SourceObservationKind.PUNCTUATION_MARK,
                value=f"unicode_category_{category}",
                start=ordinal,
                end=ordinal + 1,
                repeat_count=1,
                rule_id=_RULE_PUNCTUATION,
            )
        if character in _DELIMITER_VALUES:
            add(
                kind=SourceObservationKind.DELIMITER_MARK,
                value=_DELIMITER_VALUES[character],
                start=ordinal,
                end=ordinal + 1,
                repeat_count=1,
                rule_id=_RULE_DELIMITER,
            )
        if character in _QUOTE_CHARACTERS or category in {"Pi", "Pf"}:
            add(
                kind=SourceObservationKind.QUOTATION_MARK,
                value="visible_quote_mark",
                start=ordinal,
                end=ordinal + 1,
                repeat_count=1,
                rule_id=_RULE_QUOTE,
            )
        if category.startswith("S") or character in _OPERATOR_LIKE_ASCII:
            add(
                kind=SourceObservationKind.OPERATOR_LIKE_SYMBOL,
                value="surface_symbol_only_not_rsoc_binding",
                start=ordinal,
                end=ordinal + 1,
                repeat_count=1,
                rule_id=_RULE_SYMBOL,
            )

    index = 0
    while index < len(text):
        if not _horizontal_whitespace(text[index]):
            index += 1
            continue
        end = index + 1
        while end < len(text) and _horizontal_whitespace(text[end]):
            end += 1
        if end - index >= 2:
            add(
                kind=SourceObservationKind.REPEATED_WHITESPACE,
                value="repeated_horizontal_whitespace",
                start=index,
                end=end,
                repeat_count=end - index,
                rule_id=_RULE_WHITESPACE,
            )
        index = end

    line_units = _line_break_units(text)
    for start, end, value in line_units:
        add(
            kind=SourceObservationKind.LINE_BREAK,
            value=value,
            start=start,
            end=end,
            repeat_count=1,
            rule_id=_RULE_LINE,
        )

    unit_index = 0
    while unit_index < len(line_units):
        start_unit = unit_index
        end_unit = unit_index
        while end_unit + 1 < len(line_units):
            between_start = line_units[end_unit][1]
            between_end = line_units[end_unit + 1][0]
            between = text[between_start:between_end]
            if all(_horizontal_whitespace(char) for char in between):
                end_unit += 1
            else:
                break
        if end_unit > start_unit:
            start = line_units[start_unit][0]
            end = line_units[end_unit][1]
            add(
                kind=SourceObservationKind.PARAGRAPH_BOUNDARY,
                value="two_or_more_line_breaks_with_horizontal_gap_only",
                start=start,
                end=end,
                repeat_count=end_unit - start_unit + 1,
                rule_id=_RULE_PARAGRAPH,
            )
        unit_index = max(unit_index + 1, end_unit + 1)

    drafts.sort(
        key=lambda item: (
            int(item["code_point_start"]),
            int(item["code_point_end"]),
            str(item["kind"].value),
            str(item["observation_value"]),
        )
    )
    return drafts


def project_source_field(
    input_event: object,
    *,
    limits: object = _DEFAULT_LIMITS_SENTINEL,
) -> SourceFieldProjectionResult:
    """Project exact source into a reversible, non-semantic source field."""

    effective_limits = (
        default_source_field_projection_limits()
        if limits is _DEFAULT_LIMITS_SENTINEL
        else limits
    )
    limit_issues = _limits_issue_codes(effective_limits)
    source_event_id = (
        input_event.input_event_id
        if type(input_event) is InputEventRecord
        else ""
    )
    source_sha256 = (
        input_event.source_sha256
        if type(input_event) is InputEventRecord
        else ""
    )
    source_preserved = type(input_event) is InputEventRecord

    if limit_issues:
        status = (
            SourceFieldProjectionStatus.SOURCE_FIELD_LIMIT_EXCEEDED
            if any("absolute_maximum" in code for code in limit_issues)
            else SourceFieldProjectionStatus.SOURCE_FIELD_MALFORMED
        )
        return _result(
            status=status,
            reason_code=limit_issues[0],
            projection_created=False,
            structural_progression_allowed=False,
            source_preserved_in_custody=source_preserved,
            source_event_id=source_event_id,
            source_sha256=source_sha256,
            limits=(
                effective_limits
                if type(effective_limits) is SourceFieldProjectionLimits
                else None
            ),
            projection=None,
            validation_issue_codes=limit_issues,
        )

    assert type(effective_limits) is SourceFieldProjectionLimits

    if type(input_event) is not InputEventRecord:
        return _result(
            status=SourceFieldProjectionStatus.SOURCE_FIELD_MALFORMED,
            reason_code="invalid_input_event_type",
            projection_created=False,
            structural_progression_allowed=False,
            source_preserved_in_custody=False,
            source_event_id="",
            source_sha256="",
            limits=effective_limits,
            projection=None,
            validation_issue_codes=("invalid_input_event_type",),
        )

    event_report = validate_input_event(input_event)
    if not event_report.ok:
        return _result(
            status=SourceFieldProjectionStatus.SOURCE_FIELD_MALFORMED,
            reason_code="invalid_input_event_record",
            projection_created=False,
            structural_progression_allowed=False,
            source_preserved_in_custody=True,
            source_event_id=input_event.input_event_id,
            source_sha256=input_event.source_sha256,
            limits=effective_limits,
            projection=None,
            validation_issue_codes=tuple(
                issue.code for issue in event_report.issues
            ),
        )

    if input_event.unicode_database_version != UNICODE_DATABASE_VERSION:
        return _result(
            status=(
                SourceFieldProjectionStatus.SOURCE_FIELD_PROJECTION_FAILED
            ),
            reason_code="unicode_database_version_mismatch",
            projection_created=False,
            structural_progression_allowed=False,
            source_preserved_in_custody=True,
            source_event_id=input_event.input_event_id,
            source_sha256=input_event.source_sha256,
            limits=effective_limits,
            projection=None,
            validation_issue_codes=("unicode_database_version_mismatch",),
        )

    if input_event.code_point_length > effective_limits.max_code_points:
        return _result(
            status=SourceFieldProjectionStatus.SOURCE_FIELD_LIMIT_EXCEEDED,
            reason_code="projection_code_point_limit_exceeded",
            projection_created=False,
            structural_progression_allowed=False,
            source_preserved_in_custody=True,
            source_event_id=input_event.input_event_id,
            source_sha256=input_event.source_sha256,
            limits=effective_limits,
            projection=None,
            validation_issue_codes=("projection_code_point_limit_exceeded",),
        )

    try:
        predecessor = build_unprojected_language_field(input_event)
        if input_event.custody_status is InputCustodyStatus.CAPTURED_SUPPORTED:
            if (
                predecessor.status
                is not FieldEnvelopeBuildStatus.CREATED_UNPROJECTED
                or predecessor.field is None
            ):
                raise ValueError("supported_predecessor_field_not_created")
            predecessor_field_id = predecessor.field.field_id
        elif input_event.custody_status is InputCustodyStatus.CAPTURED_UNSUPPORTED:
            if predecessor.status is not FieldEnvelopeBuildStatus.HELD_UNSUPPORTED_INPUT:
                raise ValueError("unsupported_predecessor_not_held")
            predecessor_field_id = None
        else:
            raise ValueError("unsupported_custody_status")

        identity = _projection_identity(
            event=input_event,
            predecessor_result_id=predecessor.result_id,
            predecessor_field_id=predecessor_field_id,
            limits=effective_limits,
        )
        projection_id = stable_record_id("source_field_projection", identity)

        span_cache: dict[tuple[int, int], str] = {}
        atom_identity_bodies: list[dict[str, object]] = []
        atom_ids: list[str] = []
        atom_support: list[SourceFieldSupportStatus] = []
        unsupported_reasons: list[str] = []
        for ordinal, character in enumerate(input_event.exact_received_text):
            span_id = _span_id(
                input_event,
                ordinal,
                ordinal + 1,
                span_cache,
            )
            atom_body = _atom_identity_body(
                projection_id=projection_id,
                event=input_event,
                ordinal=ordinal,
                character=character,
                source_span_id=span_id,
            )
            atom_identity_bodies.append(atom_body)
            atom_ids.append(stable_record_id("source_code_point", atom_body))
            reason = _unsupported_reason(character)
            unsupported_reasons.append(reason)
            atom_support.append(
                SourceFieldSupportStatus.UNSUPPORTED
                if reason
                else SourceFieldSupportStatus.SUPPORTED
            )

        unsupported_count = sum(bool(reason) for reason in unsupported_reasons)
        if unsupported_count != input_event.total_unsupported_condition_count:
            raise ValueError("unsupported_condition_count_mismatch")

        atoms: list[SourceCodePointRecord] = []
        for ordinal, atom_body in enumerate(atom_identity_bodies):
            character = input_event.exact_received_text[ordinal]
            atoms.append(
                SourceCodePointRecord(
                    atom_id=atom_ids[ordinal],
                    **atom_body,
                    general_category=unicodedata.category(character),
                    unicode_name=unicodedata.name(character, ""),
                    combining_class=unicodedata.combining(character),
                    support_status=atom_support[ordinal],
                    unsupported_reason_code=unsupported_reasons[ordinal],
                    previous_atom_id=(
                        atom_ids[ordinal - 1] if ordinal > 0 else None
                    ),
                    next_atom_id=(
                        atom_ids[ordinal + 1]
                        if ordinal + 1 < len(atom_ids)
                        else None
                    ),
                )
            )

        boundaries: list[SourceBoundaryRecord] = []
        text = input_event.exact_received_text
        for offset in range(input_event.code_point_length + 1):
            if offset in {0, input_event.code_point_length}:
                grapheme_status = GraphemeBoundaryStatus.EXACT_BOUNDARY
            else:
                previous = text[offset - 1]
                following = text[offset]
                if ord(previous) < 128 and ord(following) < 128:
                    grapheme_status = (
                        GraphemeBoundaryStatus.EXACT_NON_BOUNDARY
                        if previous == "\r" and following == "\n"
                        else GraphemeBoundaryStatus.EXACT_BOUNDARY
                    )
                else:
                    grapheme_status = GraphemeBoundaryStatus.UNAVAILABLE
            boundary_body = {
                "projection_id": projection_id,
                "source_event_id": input_event.input_event_id,
                "ordinal": offset,
                "code_point_offset": offset,
                "utf8_byte_offset": input_event.utf8_boundary_offsets[offset],
                "previous_atom_id": (
                    atom_ids[offset - 1] if offset > 0 else None
                ),
                "next_atom_id": (
                    atom_ids[offset] if offset < len(atom_ids) else None
                ),
                "grapheme_boundary_status": grapheme_status,
                "rule_id": _RULE_BOUNDARY,
                "rule_version": PROJECTION_RULESET_VERSION,
                "projection_spec_id": PROJECTION_SPEC_ID,
                "projection_spec_version": PROJECTION_SPEC_VERSION,
                "schema_version": PROJECTION_SCHEMA_VERSION,
            }
            boundaries.append(
                SourceBoundaryRecord(
                    boundary_id=stable_record_id(
                        "source_boundary",
                        boundary_body,
                    ),
                    **boundary_body,
                )
            )

        drafts = _observation_drafts(
            event=input_event,
            atom_ids=tuple(atom_ids),
            atom_support=tuple(atom_support),
            span_cache=span_cache,
        )
        if len(drafts) > effective_limits.max_observations:
            return _result(
                status=(
                    SourceFieldProjectionStatus.SOURCE_FIELD_LIMIT_EXCEEDED
                ),
                reason_code="projection_observation_limit_exceeded",
                projection_created=False,
                structural_progression_allowed=False,
                source_preserved_in_custody=True,
                source_event_id=input_event.input_event_id,
                source_sha256=input_event.source_sha256,
                limits=effective_limits,
                projection=None,
                validation_issue_codes=(
                    "projection_observation_limit_exceeded",
                ),
            )

        observations: list[SourceObservationRecord] = []
        for ordinal, draft in enumerate(drafts):
            body = {
                "projection_id": projection_id,
                "source_event_id": input_event.input_event_id,
                "ordinal": ordinal,
                **draft,
                "projection_spec_id": PROJECTION_SPEC_ID,
                "projection_spec_version": PROJECTION_SPEC_VERSION,
                "schema_version": PROJECTION_SCHEMA_VERSION,
            }
            observations.append(
                SourceObservationRecord(
                    observation_id=stable_record_id(
                        "source_observation",
                        body,
                    ),
                    **body,
                )
            )

        status = (
            SourceFieldProjectionStatus.SOURCE_FIELD_PARTIALLY_UNSUPPORTED
            if unsupported_count
            else SourceFieldProjectionStatus.SOURCE_FIELD_SUPPORTED
        )
        structural_progression_allowed = not unsupported_count
        complete_grapheme = all(
            item.grapheme_boundary_status
            is not GraphemeBoundaryStatus.UNAVAILABLE
            for item in boundaries
        )
        projection = SourceFieldProjectionRecord(
            projection_id=projection_id,
            source_event_id=input_event.input_event_id,
            source_sha256=input_event.source_sha256,
            source_utf8_byte_length=input_event.utf8_byte_length,
            source_code_point_length=input_event.code_point_length,
            root_source_span_id=input_event.root_source_span_id,
            predecessor_field_build_result_id=predecessor.result_id,
            predecessor_field_envelope_id=predecessor_field_id,
            limits_id=effective_limits.limits_id,
            status=status,
            code_points=tuple(atoms),
            boundaries=tuple(boundaries),
            observations=tuple(observations),
            code_point_count=len(atoms),
            boundary_count=len(boundaries),
            observation_count=len(observations),
            unsupported_code_point_count=unsupported_count,
            grapheme_profile_id=GRAPHEME_PROFILE_ID,
            grapheme_profile_status=(
                GraphemeProfileStatus.COMPLETE_EXACT_ASCII_PROFILE
                if complete_grapheme
                else GraphemeProfileStatus.PARTIAL_CODE_POINT_FALLBACK
            ),
            unicode_database_version=UNICODE_DATABASE_VERSION,
            source_coverage_complete=True,
            source_ordering_complete=True,
            source_adjacency_complete=True,
            exact_reconstruction_proven=False,
            reconstructed_source_sha256="",
            structural_progression_allowed=structural_progression_allowed,
            operator_application_available=False,
            source_text_replaced=False,
            normalization_performed=False,
            casefolding_performed=False,
            whitespace_collapse_performed=False,
            transliteration_performed=False,
            tokenization_performed=False,
            vocabulary_lookup_performed=False,
            part_of_speech_tagging_performed=False,
            concept_lookup_performed=False,
            predicate_binding_performed=False,
            reference_resolution_performed=False,
            operator_binding_performed=False,
            operator_application_performed=False,
            phase_assignment_performed=False,
            intention_inference_performed=False,
            meaning_created=False,
            legacy_runtime_consulted=False,
            filesystem_read_performed=False,
            filesystem_write_performed=False,
            network_access_performed=False,
            environment_access_performed=False,
            memory_read_performed=False,
            memory_write_performed=False,
            route_registration_performed=False,
            tool_routing_performed=False,
            action_performed=False,
            delivery_performed=False,
        )

        reconstructed = b"".join(
            bytes.fromhex(atom.utf8_hex) for atom in projection.code_points
        )
        reconstructed_hash = hashlib.sha256(reconstructed).hexdigest()
        if reconstructed_hash != input_event.source_sha256:
            raise ValueError("source_reconstruction_hash_mismatch")
        if reconstructed.decode("utf-8", "strict") != input_event.exact_received_text:
            raise ValueError("source_reconstruction_text_mismatch")
        projection = replace(
            projection,
            exact_reconstruction_proven=True,
            reconstructed_source_sha256=reconstructed_hash,
        )
        return _result(
            status=status,
            reason_code=(
                "source_field_projected_with_unsupported_code_points_held"
                if unsupported_count
                else "source_field_projected_exactly"
            ),
            projection_created=True,
            structural_progression_allowed=structural_progression_allowed,
            source_preserved_in_custody=True,
            source_event_id=input_event.input_event_id,
            source_sha256=input_event.source_sha256,
            limits=effective_limits,
            projection=projection,
            validation_issue_codes=(),
        )
    except (UnicodeError, ValueError, TypeError, OverflowError) as error:
        return _result(
            status=(
                SourceFieldProjectionStatus.SOURCE_FIELD_PROJECTION_FAILED
            ),
            reason_code=str(error) or "source_field_projection_failed",
            projection_created=False,
            structural_progression_allowed=False,
            source_preserved_in_custody=True,
            source_event_id=input_event.input_event_id,
            source_sha256=input_event.source_sha256,
            limits=effective_limits,
            projection=None,
            validation_issue_codes=(
                str(error) or "source_field_projection_failed",
            ),
        )
