"""Deterministic source-form spans without a token stream.

This scanner walks source characters and projects custody-bound source forms.
It does not normalize text, create model/subword units, or assign numeric IDs.
"""

from __future__ import annotations

import unicodedata

from ..input_event_custody import InputEventRecord, build_source_span
from ..schema import stable_record_id
from .schema import SourceForm, SourceFormKind


def _word_character(character: str) -> bool:
    category = unicodedata.category(character)
    return category.startswith("L") or category.startswith("M")


def _base_kind(text: str, index: int) -> SourceFormKind:
    character = text[index]
    if _word_character(character):
        return SourceFormKind.WORD
    if character.isdecimal():
        return SourceFormKind.NUMBER
    if character.isspace():
        return SourceFormKind.WHITESPACE
    if (
        character in ("'", "’", "-")
        and 0 < index < len(text) - 1
        and _word_character(text[index - 1])
        and _word_character(text[index + 1])
    ):
        return SourceFormKind.WORD
    if unicodedata.category(character).startswith("P"):
        return SourceFormKind.PUNCTUATION
    return SourceFormKind.SYMBOL


def build_source_forms(event: InputEventRecord) -> tuple[SourceForm, ...]:
    """Project exact character spans from an already captured input event."""

    if type(event) is not InputEventRecord:
        raise TypeError("event must be an InputEventRecord")
    text = event.exact_received_text
    boundaries: list[tuple[int, int, SourceFormKind]] = []
    index = 0
    while index < len(text):
        kind = _base_kind(text, index)
        end = index + 1
        if kind in (
            SourceFormKind.WORD,
            SourceFormKind.NUMBER,
            SourceFormKind.WHITESPACE,
        ):
            while end < len(text) and _base_kind(text, end) is kind:
                end += 1
        boundaries.append((index, end, kind))
        index = end

    forms: list[SourceForm] = []
    for start, end, kind in boundaries:
        span_result = build_source_span(
            event,
            code_point_start=start,
            code_point_end=end,
        )
        if not span_result.ok or span_result.span is None:
            raise ValueError("source form span could not be built")
        span = span_result.span
        body = {
            "source_span_id": span.span_id,
            "input_event_id": event.input_event_id,
            "kind": kind,
            "exact_text": text[start:end],
            "code_point_start": start,
            "code_point_end": end,
            "utf8_byte_start": span.utf8_byte_start,
            "utf8_byte_end": span.utf8_byte_end,
            "source_sha256": event.source_sha256,
        }
        forms.append(
            SourceForm(
                source_form_id=stable_record_id("source_form", body),
                **body,
            )
        )
    return tuple(forms)


__all__ = ("build_source_forms",)
