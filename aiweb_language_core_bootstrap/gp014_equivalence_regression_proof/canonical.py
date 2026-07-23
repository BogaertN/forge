"""Canonical serialization and identity helpers for Slice 46."""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Iterable


def canonical_value(value: Any) -> Any:
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): canonical_value(value[key]) for key in sorted(value, key=lambda item: str(item))}
    if isinstance(value, (tuple, list)):
        return [canonical_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        rows = [canonical_value(item) for item in value]
        return sorted(rows, key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if callable(getattr(value, "to_dict", None)):
        return canonical_value(value.to_dict())
    return repr(value)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(canonical_value(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def deterministic_digest(value: Any) -> str:
    return sha256(canonical_json_bytes(value)).hexdigest()


def stable_identifier(namespace: str, value: Any, *, excluded_fields: Iterable[str] = ()) -> str:
    excluded = frozenset(excluded_fields)
    body = canonical_value(value)
    if isinstance(body, dict):
        body = {key: val for key, val in body.items() if key not in excluded}
    return f"{namespace}:{deterministic_digest(body)}"


def text_sha256(value: str | None) -> str | None:
    if value is None:
        return None
    return sha256(value.encode("utf-8")).hexdigest()


__all__ = ("canonical_value", "canonical_json_bytes", "deterministic_digest", "stable_identifier", "text_sha256")
