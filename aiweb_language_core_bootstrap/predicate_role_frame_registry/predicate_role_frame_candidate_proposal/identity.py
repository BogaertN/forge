"""Deterministic identity helpers for Slice 38G immutable records."""

from __future__ import annotations

from dataclasses import replace
from typing import TypeVar


T = TypeVar("T")


def with_expected_id(record: T, field_name: str) -> T:
    """Return *record* with its canonical identifier installed.

    The record must expose ``expected_id`` and the named identifier field.
    This helper never mutates the supplied immutable record.
    """

    expected = record.expected_id()  # type: ignore[attr-defined]
    return replace(record, **{field_name: expected})
