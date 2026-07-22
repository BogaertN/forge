"""Deterministic identity helpers for Slice 43D comparison records."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .canonical import deterministic_digest, deterministic_record_digest, stable_identifier
from .schema import (
    DimensionValueSnapshot,
    MeaningPreservationComparisonPackage,
    MeaningPreservationComparisonRequest,
    MeaningPreservationComparisonResult,
    MeaningPreservationFinding,
)


_IDENTITY_FIELDS: dict[type[Any], tuple[str, str]] = {
    MeaningPreservationComparisonRequest: (
        "request_id",
        "slice43d_meaning_preservation_comparison_request",
    ),
    DimensionValueSnapshot: (
        "snapshot_id",
        "slice43d_dimension_value_snapshot",
    ),
    MeaningPreservationFinding: (
        "finding_id",
        "slice43d_meaning_preservation_finding",
    ),
}


def identity_field(record_type: type[Any]) -> str:
    try:
        return _IDENTITY_FIELDS[record_type][0]
    except KeyError as error:
        raise TypeError(
            f"unsupported Slice 43D identity type: {record_type!r}"
        ) from error


def expected_record_id(record: Any) -> str:
    field_name, namespace = _IDENTITY_FIELDS[type(record)]
    return stable_identifier(
        namespace,
        record,
        exclude_fields=(field_name,),
    )


def with_expected_id(record: Any) -> Any:
    field_name = identity_field(type(record))
    return replace(record, **{field_name: expected_record_id(record)})


def expected_snapshot_value_digest(
    record: DimensionValueSnapshot,
) -> str:
    return deterministic_digest(
        b"\x00".join(value.encode("utf-8") for value in record.values)
    )


def with_expected_snapshot_identity(
    record: DimensionValueSnapshot,
) -> DimensionValueSnapshot:
    with_digest = replace(
        record,
        value_digest=expected_snapshot_value_digest(record),
    )
    return replace(
        with_digest,
        snapshot_id=expected_record_id(with_digest),
    )


def expected_package_digest(
    record: MeaningPreservationComparisonPackage,
) -> str:
    return deterministic_record_digest(
        record,
        exclude_fields=(
            "comparison_package_id",
            "comparison_package_digest",
        ),
    )


def expected_package_id(
    record: MeaningPreservationComparisonPackage,
) -> str:
    return stable_identifier(
        "slice43d_meaning_preservation_comparison_package",
        record,
        exclude_fields=(
            "comparison_package_id",
            "comparison_package_digest",
        ),
    )


def with_expected_package_identity(
    record: MeaningPreservationComparisonPackage,
) -> MeaningPreservationComparisonPackage:
    digest = expected_package_digest(record)
    with_digest = replace(record, comparison_package_digest=digest)
    return replace(
        with_digest,
        comparison_package_id=expected_package_id(with_digest),
    )


def expected_result_digest(
    record: MeaningPreservationComparisonResult,
) -> str:
    return deterministic_record_digest(
        record,
        exclude_fields=(
            "comparison_result_id",
            "comparison_result_digest",
        ),
    )


def expected_result_id(
    record: MeaningPreservationComparisonResult,
) -> str:
    return stable_identifier(
        "slice43d_meaning_preservation_comparison_result",
        record,
        exclude_fields=(
            "comparison_result_id",
            "comparison_result_digest",
        ),
    )


def with_expected_result_identity(
    record: MeaningPreservationComparisonResult,
) -> MeaningPreservationComparisonResult:
    digest = expected_result_digest(record)
    with_digest = replace(record, comparison_result_digest=digest)
    return replace(
        with_digest,
        comparison_result_id=expected_result_id(with_digest),
    )


__all__ = (
    "expected_package_digest",
    "expected_package_id",
    "expected_record_id",
    "expected_result_digest",
    "expected_result_id",
    "expected_snapshot_value_digest",
    "identity_field",
    "with_expected_id",
    "with_expected_package_identity",
    "with_expected_result_identity",
    "with_expected_snapshot_identity",
)
