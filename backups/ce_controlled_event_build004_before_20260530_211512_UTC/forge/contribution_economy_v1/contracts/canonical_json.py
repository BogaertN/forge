"""Patch 300 - Deterministic canonical JSON encoding for contract-only objects."""
from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

from .enums import ContractValueError

_CANONICAL_TIMESTAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")


def assert_utc_timestamp_z(value: str | None, field_name: str, *, allow_none: bool = False) -> str | None:
    """Validate an ISO-8601 UTC timestamp expressed with an explicit Z suffix."""
    if value is None and allow_none:
        return None
    if not isinstance(value, str) or not _CANONICAL_TIMESTAMP_PATTERN.fullmatch(value):
        raise ContractValueError(f"{field_name} must be an ISO-8601 UTC timestamp with Z suffix")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractValueError(f"{field_name} is not a valid UTC timestamp") from exc
    if parsed.tzinfo != timezone.utc:
        raise ContractValueError(f"{field_name} must resolve to UTC")
    return value


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ContractValueError(f"floating-point values are forbidden in governed contract payloads: {path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_floats(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_floats(item, f"{path}[{index}]")


def _json_compatible(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_compatible(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_compatible(item) for item in value]
    if isinstance(value, list):
        return [_json_compatible(item) for item in value]
    return value


def canonical_json(payload: Mapping[str, Any], *, require_policy_version: bool = False) -> str:
    """Return compact canonical JSON for a governed contract-only payload.

    Null values remain explicit JSON null values; they are not discarded. Hashable
    governed payloads must carry a schema version. Reward-related payloads must
    additionally carry their policy version.
    """
    if not isinstance(payload, Mapping):
        raise ContractValueError("canonical payload must be a mapping")
    if not isinstance(payload.get("schema_version"), str) or not payload.get("schema_version"):
        raise ContractValueError("canonical payload must include schema_version")
    if require_policy_version and (
        not isinstance(payload.get("ct_reward_policy_version"), str)
        or not payload.get("ct_reward_policy_version")
    ):
        raise ContractValueError("reward-related canonical payload must include ct_reward_policy_version")
    _reject_floats(payload)
    compatible = _json_compatible(payload)
    return json.dumps(compatible, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def canonical_utf8_bytes(payload: Mapping[str, Any], *, require_policy_version: bool = False) -> bytes:
    """Return canonical UTF-8 bytes without writing or storing any record."""
    return canonical_json(payload, require_policy_version=require_policy_version).encode("utf-8")
