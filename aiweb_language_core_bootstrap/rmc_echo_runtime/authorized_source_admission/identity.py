"""Deterministic identity helpers for Slice 43C admission records."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .canonical import deterministic_record_digest, stable_identifier
from .schema import (
    AuthorizedMeaningAdmissionRecord,
    EchoValidationAdmissionPackage,
    ProposedExpressionAdmissionRecord,
    SourceAdmissionRequest,
    SourceAdmissionResult,
)


_IDENTITY_FIELDS: dict[type[Any], tuple[str, str]] = {
    SourceAdmissionRequest: (
        "request_id",
        "slice43c_source_admission_request",
    ),
    AuthorizedMeaningAdmissionRecord: (
        "admission_record_id",
        "slice43c_authorized_meaning_admission",
    ),
    ProposedExpressionAdmissionRecord: (
        "admission_record_id",
        "slice43c_proposed_expression_admission",
    ),
}


def identity_field(record_type: type[Any]) -> str:
    try:
        return _IDENTITY_FIELDS[record_type][0]
    except KeyError as error:
        raise TypeError(
            f"unsupported Slice 43C identity type: {record_type!r}"
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
    record: EchoValidationAdmissionPackage,
) -> str:
    return deterministic_record_digest(
        record,
        exclude_fields=(
            "admission_package_id",
            "admission_package_digest",
        ),
    )


def expected_package_id(
    record: EchoValidationAdmissionPackage,
) -> str:
    return stable_identifier(
        "slice43c_echo_validation_admission_package",
        record,
        exclude_fields=(
            "admission_package_id",
            "admission_package_digest",
        ),
    )


def with_expected_package_identity(
    record: EchoValidationAdmissionPackage,
) -> EchoValidationAdmissionPackage:
    digest = expected_package_digest(record)
    with_digest = replace(record, admission_package_digest=digest)
    return replace(
        with_digest,
        admission_package_id=expected_package_id(with_digest),
    )


def expected_result_digest(record: SourceAdmissionResult) -> str:
    return deterministic_record_digest(
        record,
        exclude_fields=(
            "admission_result_id",
            "admission_result_digest",
        ),
    )


def expected_result_id(record: SourceAdmissionResult) -> str:
    return stable_identifier(
        "slice43c_source_admission_result",
        record,
        exclude_fields=(
            "admission_result_id",
            "admission_result_digest",
        ),
    )


def with_expected_result_identity(
    record: SourceAdmissionResult,
) -> SourceAdmissionResult:
    digest = expected_result_digest(record)
    with_digest = replace(record, admission_result_digest=digest)
    return replace(
        with_digest,
        admission_result_id=expected_result_id(with_digest),
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
