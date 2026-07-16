"""Stable-identity helpers for Slice 37F immutable records."""

from __future__ import annotations

from dataclasses import replace
from typing import TypeVar


T = TypeVar("T")


def with_expected_id(record: T) -> T:
    """Return a frozen-record copy carrying its deterministic expected ID."""

    field_names = (
        "proposal_id",
        "profile_id",
        "snapshot_id",
        "ancestry_id",
        "occurrence_id",
        "result_id",
    )
    for name in field_names:
        if hasattr(record, name):
            return replace(record, **{name: record.expected_id()})
    raise TypeError("record has no supported Slice 37F identity field")
