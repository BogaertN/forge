"""Deterministic identity helpers for Slice 43F disposition records."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .canonical import deterministic_record_digest, stable_identifier
from .schema import (
    EchoContainmentRecord,
    EchoDispositionPackage,
    EchoDispositionRecord,
    EchoDispositionRequest,
    EchoDispositionResult,
    EchoRejectionRecord,
)


_IDENTITY_FIELDS: dict[type[Any], tuple[str, str]] = {
    EchoDispositionRequest: (
        "request_id",
        "slice43f_echo_disposition_request",
    ),
    EchoRejectionRecord: (
        "rejection_id",
        "slice43f_echo_rejection",
    ),
    EchoContainmentRecord: (
        "containment_id",
        "slice43f_echo_containment",
    ),
    EchoDispositionRecord: (
        "disposition_id",
        "slice43f_echo_disposition",
    ),
}


def identity_field(record_type: type[Any]) -> str:
    try:
        return _IDENTITY_FIELDS[record_type][0]
    except KeyError as error:
        raise TypeError(
            f"unsupported Slice 43F identity type: {record_type!r}"
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


def expected_package_digest(record: EchoDispositionPackage) -> str:
    return deterministic_record_digest(
        record,
        exclude_fields=(
            "disposition_package_id",
            "disposition_package_digest",
        ),
    )


def expected_package_id(record: EchoDispositionPackage) -> str:
    return stable_identifier(
        "slice43f_echo_disposition_package",
        record,
        exclude_fields=(
            "disposition_package_id",
            "disposition_package_digest",
        ),
    )


def with_expected_package_identity(
    record: EchoDispositionPackage,
) -> EchoDispositionPackage:
    digest = expected_package_digest(record)
    with_digest = replace(record, disposition_package_digest=digest)
    return replace(
        with_digest,
        disposition_package_id=expected_package_id(with_digest),
    )


def expected_result_digest(record: EchoDispositionResult) -> str:
    return deterministic_record_digest(
        record,
        exclude_fields=(
            "disposition_result_id",
            "disposition_result_digest",
        ),
    )


def expected_result_id(record: EchoDispositionResult) -> str:
    return stable_identifier(
        "slice43f_echo_disposition_result",
        record,
        exclude_fields=(
            "disposition_result_id",
            "disposition_result_digest",
        ),
    )


def with_expected_result_identity(
    record: EchoDispositionResult,
) -> EchoDispositionResult:
    digest = expected_result_digest(record)
    with_digest = replace(record, disposition_result_digest=digest)
    return replace(
        with_digest,
        disposition_result_id=expected_result_id(with_digest),
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
