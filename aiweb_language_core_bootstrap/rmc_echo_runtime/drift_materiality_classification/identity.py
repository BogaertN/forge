"""Deterministic identity helpers for Slice 43E classification records."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .canonical import deterministic_record_digest, stable_identifier
from .schema import (
    DriftClassificationPackage,
    DriftClassificationRequest,
    DriftClassificationResult,
    DriftMaterialityFinding,
)


_IDENTITY_FIELDS: dict[type[Any], tuple[str, str]] = {
    DriftClassificationRequest: (
        "request_id",
        "slice43e_drift_classification_request",
    ),
    DriftMaterialityFinding: (
        "drift_finding_id",
        "slice43e_drift_materiality_finding",
    ),
}


def identity_field(record_type: type[Any]) -> str:
    try:
        return _IDENTITY_FIELDS[record_type][0]
    except KeyError as error:
        raise TypeError(
            f"unsupported Slice 43E identity type: {record_type!r}"
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


def expected_package_digest(
    record: DriftClassificationPackage,
) -> str:
    return deterministic_record_digest(
        record,
        exclude_fields=(
            "classification_package_id",
            "classification_package_digest",
        ),
    )


def expected_package_id(
    record: DriftClassificationPackage,
) -> str:
    return stable_identifier(
        "slice43e_drift_classification_package",
        record,
        exclude_fields=(
            "classification_package_id",
            "classification_package_digest",
        ),
    )


def with_expected_package_identity(
    record: DriftClassificationPackage,
) -> DriftClassificationPackage:
    digest = expected_package_digest(record)
    with_digest = replace(record, classification_package_digest=digest)
    return replace(
        with_digest,
        classification_package_id=expected_package_id(with_digest),
    )


def expected_result_digest(
    record: DriftClassificationResult,
) -> str:
    return deterministic_record_digest(
        record,
        exclude_fields=(
            "classification_result_id",
            "classification_result_digest",
        ),
    )


def expected_result_id(
    record: DriftClassificationResult,
) -> str:
    return stable_identifier(
        "slice43e_drift_classification_result",
        record,
        exclude_fields=(
            "classification_result_id",
            "classification_result_digest",
        ),
    )


def with_expected_result_identity(
    record: DriftClassificationResult,
) -> DriftClassificationResult:
    digest = expected_result_digest(record)
    with_digest = replace(record, classification_result_digest=digest)
    return replace(
        with_digest,
        classification_result_id=expected_result_id(with_digest),
    )


__all__ = (
    "expected_package_digest",
    "expected_package_id",
    "expected_record_id",
    "expected_result_digest",
    "expected_result_id",
    "identity_field",
    "with_expected_id",
    "with_expected_package_identity",
    "with_expected_result_identity",
)
