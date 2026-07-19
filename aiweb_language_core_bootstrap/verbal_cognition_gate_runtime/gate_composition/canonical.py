"""Canonical serialization and stable identity helpers for Slice 40G."""
from __future__ import annotations

from dataclasses import fields, is_dataclass, replace
from enum import Enum
import hashlib
import json
from typing import Any


class GateCompositionCanonicalizationError(ValueError):
    pass


def _normalize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _normalize(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, tuple):
        return [_normalize(item) for item in value]
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise GateCompositionCanonicalizationError(
                "canonical mappings require string keys"
            )
        return {key: _normalize(value[key]) for key in sorted(value)}
    if value is None or type(value) in (str, bool, int):
        return value
    raise GateCompositionCanonicalizationError(
        f"unsupported canonical value type: {type(value).__name__}"
    )


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        _normalize(value),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=False,
        allow_nan=False,
    ).encode("utf-8")


def deterministic_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def stable_identifier(prefix: str, value: Any) -> str:
    if not isinstance(prefix, str) or not prefix:
        raise GateCompositionCanonicalizationError(
            "identifier prefix must be non-empty text"
        )
    return f"{prefix}:sha256:{deterministic_digest(value)}"


def with_expected_id(record: Any, field_name: str, prefix: str) -> Any:
    if not is_dataclass(record) or isinstance(record, type):
        raise GateCompositionCanonicalizationError("record must be a dataclass")
    names = tuple(field.name for field in fields(record))
    if field_name not in names:
        raise GateCompositionCanonicalizationError(
            f"unknown identity field: {field_name}"
        )
    payload = {
        field.name: _normalize(getattr(record, field.name))
        for field in fields(record)
        if field.name != field_name
    }
    return replace(record, **{field_name: stable_identifier(prefix, payload)})
