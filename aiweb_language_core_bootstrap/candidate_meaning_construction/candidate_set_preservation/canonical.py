"""Deterministic canonicalization for Slice 39E candidate sets."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Mapping

from ..candidate_semantic_content.canonical import canonical_record_mapping_39d
from ..candidate_semantic_content.schema import CandidateSemanticContentAssemblyResult
from .schema import (
    CandidateExactDuplicateGroup,
    CandidateMaterialAlternativeReference,
    CandidateMeaningSet,
    CandidateSetMember,
    CandidateSetPreservationResult,
    CandidateSetProfileIdentity,
    CandidateSetValidationIssue,
    CandidateSharedAncestryReference,
)


class CandidateSetCanonicalizationError(ValueError):
    pass


SUPPORTED_RECORD_TYPES = (
    CandidateSetValidationIssue,
    CandidateSetProfileIdentity,
    CandidateSetMember,
    CandidateExactDuplicateGroup,
    CandidateSharedAncestryReference,
    CandidateMaterialAlternativeReference,
    CandidateMeaningSet,
    CandidateSetPreservationResult,
)

CANONICAL_FIELD_ORDERS: Mapping[type[Any], tuple[str, ...]] = {
    record_type: tuple(item.name for item in fields(record_type))
    for record_type in SUPPORTED_RECORD_TYPES
}


def canonical_field_order(record_type: type[Any]) -> tuple[str, ...]:
    try:
        return CANONICAL_FIELD_ORDERS[record_type]
    except KeyError as error:
        raise CandidateSetCanonicalizationError(
            f"unsupported Slice 39E record type: {record_type!r}"
        ) from error


def _normalize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, CandidateSemanticContentAssemblyResult):
        return {key: _normalize(item) for key, item in canonical_record_mapping_39d(value).items()}
    if is_dataclass(value) and not isinstance(value, type):
        order = canonical_field_order(type(value))
        return {name: _normalize(getattr(value, name)) for name in order}
    if isinstance(value, tuple):
        return [_normalize(item) for item in value]
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        if not all(type(key) is str for key in value):
            raise CandidateSetCanonicalizationError("canonical mappings require exact string keys")
        return {key: _normalize(value[key]) for key in sorted(value)}
    if value is None or type(value) in (str, bool, int):
        return value
    raise CandidateSetCanonicalizationError(
        f"unsupported canonical value type: {type(value).__name__}"
    )


def canonical_record_mapping_39e(record: Any, *, exclude_fields: tuple[str, ...] = ()) -> dict[str, Any]:
    order = canonical_field_order(type(record))
    excluded = set(exclude_fields)
    if excluded.difference(order):
        raise CandidateSetCanonicalizationError("unknown excluded field")
    return {name: _normalize(getattr(record, name)) for name in order if name not in excluded}


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


def deterministic_record_digest(record: Any, *, exclude_fields: tuple[str, ...] = ()) -> str:
    return deterministic_digest(canonical_record_mapping_39e(record, exclude_fields=exclude_fields))


def stable_identifier(prefix: str, value: Any) -> str:
    if type(prefix) is not str or not prefix:
        raise CandidateSetCanonicalizationError("identifier prefix must be non-empty exact text")
    return f"{prefix}:sha256:{deterministic_digest(value)}"


__all__ = (
    "CANONICAL_FIELD_ORDERS",
    "SUPPORTED_RECORD_TYPES",
    "CandidateSetCanonicalizationError",
    "canonical_field_order",
    "canonical_json_bytes",
    "canonical_record_mapping_39e",
    "deterministic_digest",
    "deterministic_record_digest",
    "stable_identifier",
)
