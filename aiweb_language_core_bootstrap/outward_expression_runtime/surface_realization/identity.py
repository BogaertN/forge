"""Deterministic identities for Slice 42F surface realization."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .canonical import deterministic_digest, stable_identifier
from .schema import (
    ControlledRealizationResourceBundle,
    ControlledRealizationResourceRecord,
    SurfaceRealizationAuthorityRecord,
    SurfaceRealizationFinding,
    SurfaceRealizationInput,
    SurfaceRealizationReceipt,
    SurfaceRealizationResult,
    SurfaceRealizationTrace,
    UnvalidatedExpressionCandidate,
)


_RECORD_NAMESPACES = {
    ControlledRealizationResourceRecord: "surface-realization-resource",
    ControlledRealizationResourceBundle: "surface-realization-resource-bundle",
    SurfaceRealizationAuthorityRecord: "surface-realization-authority",
    SurfaceRealizationInput: "surface-realization-input",
    SurfaceRealizationFinding: "surface-realization-finding",
    SurfaceRealizationTrace: "surface-realization-trace",
    SurfaceRealizationReceipt: "surface-realization-receipt",
}


def expected_record_id(record: Any) -> str:
    namespace = _RECORD_NAMESPACES.get(type(record))
    if namespace is None:
        raise TypeError(f"unsupported Slice 42F record: {type(record).__name__}")
    id_field = next(
        name
        for name in record.__dataclass_fields__
        if name.endswith("_id")
    )
    return stable_identifier(namespace, record, exclude_fields=(id_field,))


def with_expected_id(record: Any) -> Any:
    id_field = next(
        name
        for name in record.__dataclass_fields__
        if name.endswith("_id")
    )
    return replace(record, **{id_field: expected_record_id(record)})


def expected_candidate_digest(record: UnvalidatedExpressionCandidate) -> str:
    return deterministic_digest(
        record,
        exclude_fields=("expression_candidate_id", "expression_candidate_digest"),
    )


def expected_candidate_id(record: UnvalidatedExpressionCandidate) -> str:
    return "unvalidated-expression-candidate:" + expected_candidate_digest(record)


def with_expected_candidate_identity(
    record: UnvalidatedExpressionCandidate,
) -> UnvalidatedExpressionCandidate:
    digest = expected_candidate_digest(record)
    return replace(
        record,
        expression_candidate_id="unvalidated-expression-candidate:" + digest,
        expression_candidate_digest=digest,
    )


def expected_result_digest(record: SurfaceRealizationResult) -> str:
    return deterministic_digest(record, exclude_fields=("result_id", "result_digest"))


def expected_result_id(record: SurfaceRealizationResult) -> str:
    return "surface-realization-result:" + expected_result_digest(record)


def with_expected_result_identity(
    record: SurfaceRealizationResult,
) -> SurfaceRealizationResult:
    digest = expected_result_digest(record)
    return replace(
        record,
        result_id="surface-realization-result:" + digest,
        result_digest=digest,
    )


__all__ = (
    "expected_candidate_digest",
    "expected_candidate_id",
    "expected_record_id",
    "expected_result_digest",
    "expected_result_id",
    "with_expected_candidate_identity",
    "with_expected_id",
    "with_expected_result_identity",
)
