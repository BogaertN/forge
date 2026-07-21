"""Deterministic identities for Slice 42D records and packages."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .canonical import deterministic_digest, stable_identifier
from .schema import (
    ExpressionObligationPackage,
    PreservationObligationProjectionAuthorityRecord,
    PreservationObligationProjectionFinding,
    PreservationObligationProjectionInput,
    PreservationObligationProjectionResult,
)


_ID_FIELDS: dict[type[Any], tuple[str, str]] = {
    PreservationObligationProjectionAuthorityRecord: (
        "projection_authority_record_id",
        "preservation_obligation_projection_authority_record",
    ),
    PreservationObligationProjectionInput: (
        "projection_input_id",
        "preservation_obligation_projection_input",
    ),
    PreservationObligationProjectionFinding: (
        "finding_id",
        "preservation_obligation_projection_finding",
    ),
}


def expected_record_id(record: Any) -> str:
    try:
        field_name, namespace = _ID_FIELDS[type(record)]
    except KeyError as error:
        raise TypeError(
            f"unsupported Slice 42D identity type: {type(record)!r}"
        ) from error

    return stable_identifier(
        namespace,
        record,
        exclude_fields=(field_name,),
    )


def with_expected_id(record: Any) -> Any:
    try:
        field_name, _ = _ID_FIELDS[type(record)]
    except KeyError as error:
        raise TypeError(
            f"unsupported Slice 42D identity type: {type(record)!r}"
        ) from error

    return replace(record, **{field_name: expected_record_id(record)})


def expected_package_digest(record: ExpressionObligationPackage) -> str:
    return deterministic_digest(
        record,
        exclude_fields=(
            "obligation_package_id",
            "obligation_package_digest",
        ),
    )


def expected_package_id(record: ExpressionObligationPackage) -> str:
    return f"expression_obligation_package:{expected_package_digest(record)}"


def with_expected_package_identity(
    record: ExpressionObligationPackage,
) -> ExpressionObligationPackage:
    digest = expected_package_digest(record)
    return replace(
        record,
        obligation_package_digest=digest,
        obligation_package_id=f"expression_obligation_package:{digest}",
    )


def expected_result_digest(
    record: PreservationObligationProjectionResult,
) -> str:
    return deterministic_digest(
        record,
        exclude_fields=("result_id", "result_digest"),
    )


def expected_result_id(
    record: PreservationObligationProjectionResult,
) -> str:
    return (
        "preservation_obligation_projection_result:"
        f"{expected_result_digest(record)}"
    )


def with_expected_result_identity(
    record: PreservationObligationProjectionResult,
) -> PreservationObligationProjectionResult:
    digest = expected_result_digest(record)
    return replace(
        record,
        result_digest=digest,
        result_id=f"preservation_obligation_projection_result:{digest}",
    )


__all__ = (
    "expected_package_digest",
    "expected_package_id",
    "expected_record_id",
    "expected_result_digest",
    "expected_result_id",
    "with_expected_id",
    "with_expected_package_identity",
    "with_expected_result_identity",
)
