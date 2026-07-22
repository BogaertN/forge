"""Deterministic Slice 43B identity helpers."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from ..schema import (
    AuthorizedMeaningReferenceRecord,
    DriftFindingBoundaryRecord,
    EchoContainmentBoundaryRecord,
    EchoDispositionBoundaryRecord,
    EchoReceiptBoundaryRecord,
    EchoRejectionBoundaryRecord,
    EchoTraceBoundaryRecord,
    EchoValidationInputBoundaryRecord,
    PreservationDimensionRequirementRecord,
    ProposedExpressionReferenceRecord,
    RmcEchoRuntimeSchemaRecord,
    ValidationFindingBoundaryRecord,
)
from .canonical import deterministic_record_digest, stable_identifier
from .schema import (
    RmcEchoGovernanceBundle,
    RmcEchoLifecycleRecord,
    RmcEchoLifecycleTransitionRecord,
    RmcEchoVersionCustody,
)


_ID_FIELDS: dict[type[Any], tuple[str, str]] = {
    AuthorizedMeaningReferenceRecord: (
        "authorized_meaning_reference_id",
        "rmc_echo_authorized_meaning_reference",
    ),
    ProposedExpressionReferenceRecord: (
        "proposed_expression_reference_id",
        "rmc_echo_proposed_expression_reference",
    ),
    EchoValidationInputBoundaryRecord: (
        "validation_input_boundary_id",
        "rmc_echo_validation_input_boundary",
    ),
    PreservationDimensionRequirementRecord: (
        "dimension_requirement_id",
        "rmc_echo_preservation_dimension_requirement",
    ),
    ValidationFindingBoundaryRecord: (
        "validation_finding_boundary_id",
        "rmc_echo_validation_finding_boundary",
    ),
    DriftFindingBoundaryRecord: (
        "drift_finding_boundary_id",
        "rmc_echo_drift_finding_boundary",
    ),
    EchoDispositionBoundaryRecord: (
        "echo_disposition_boundary_id",
        "rmc_echo_disposition_boundary",
    ),
    EchoRejectionBoundaryRecord: (
        "echo_rejection_boundary_id",
        "rmc_echo_rejection_boundary",
    ),
    EchoContainmentBoundaryRecord: (
        "echo_containment_boundary_id",
        "rmc_echo_containment_boundary",
    ),
    EchoTraceBoundaryRecord: (
        "echo_trace_boundary_id",
        "rmc_echo_trace_boundary",
    ),
    EchoReceiptBoundaryRecord: (
        "echo_receipt_boundary_id",
        "rmc_echo_receipt_boundary",
    ),
    RmcEchoRuntimeSchemaRecord: (
        "rmc_echo_runtime_schema_record_id",
        "rmc_echo_runtime_schema_record",
    ),
    RmcEchoVersionCustody: (
        "custody_id",
        "rmc_echo_version_custody",
    ),
    RmcEchoLifecycleRecord: (
        "lifecycle_record_id",
        "rmc_echo_lifecycle_record",
    ),
    RmcEchoLifecycleTransitionRecord: (
        "transition_id",
        "rmc_echo_lifecycle_transition",
    ),
}


def identity_field(record_type: type[Any]) -> str:
    try:
        return _ID_FIELDS[record_type][0]
    except KeyError as error:
        raise TypeError(
            f"unsupported identity record type: {record_type!r}"
        ) from error


def identity_namespace(record_type: type[Any]) -> str:
    try:
        return _ID_FIELDS[record_type][1]
    except KeyError as error:
        raise TypeError(
            f"unsupported identity record type: {record_type!r}"
        ) from error


def expected_record_id(record: Any) -> str:
    field_name = identity_field(type(record))
    return stable_identifier(
        identity_namespace(type(record)),
        record,
        exclude_fields=(field_name,),
    )


def with_expected_id(record: Any) -> Any:
    field_name = identity_field(type(record))
    return replace(record, **{field_name: expected_record_id(record)})


def expected_authorized_meaning_reference_id(
    record: AuthorizedMeaningReferenceRecord,
) -> str:
    return expected_record_id(record)


def expected_proposed_expression_reference_id(
    record: ProposedExpressionReferenceRecord,
) -> str:
    return expected_record_id(record)


def expected_validation_input_boundary_id(
    record: EchoValidationInputBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_dimension_requirement_id(
    record: PreservationDimensionRequirementRecord,
) -> str:
    return expected_record_id(record)


def expected_validation_finding_boundary_id(
    record: ValidationFindingBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_drift_finding_boundary_id(
    record: DriftFindingBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_echo_disposition_boundary_id(
    record: EchoDispositionBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_echo_rejection_boundary_id(
    record: EchoRejectionBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_echo_containment_boundary_id(
    record: EchoContainmentBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_echo_trace_boundary_id(
    record: EchoTraceBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_echo_receipt_boundary_id(
    record: EchoReceiptBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_runtime_schema_record_id(
    record: RmcEchoRuntimeSchemaRecord,
) -> str:
    return expected_record_id(record)


def expected_version_custody_id(
    record: RmcEchoVersionCustody,
) -> str:
    return expected_record_id(record)


def expected_lifecycle_record_id(
    record: RmcEchoLifecycleRecord,
) -> str:
    return expected_record_id(record)


def expected_lifecycle_transition_id(
    record: RmcEchoLifecycleTransitionRecord,
) -> str:
    return expected_record_id(record)


def expected_bundle_digest(record: RmcEchoGovernanceBundle) -> str:
    return deterministic_record_digest(
        record,
        exclude_fields=("bundle_id", "bundle_digest"),
    )


def expected_bundle_id(record: RmcEchoGovernanceBundle) -> str:
    return stable_identifier(
        "rmc_echo_governance_bundle",
        record,
        exclude_fields=("bundle_id", "bundle_digest"),
    )


def with_expected_bundle_identity(
    record: RmcEchoGovernanceBundle,
) -> RmcEchoGovernanceBundle:
    digest = expected_bundle_digest(record)
    with_digest = replace(record, bundle_digest=digest)
    return replace(with_digest, bundle_id=expected_bundle_id(with_digest))


__all__ = (
    "expected_authorized_meaning_reference_id",
    "expected_bundle_digest",
    "expected_bundle_id",
    "expected_dimension_requirement_id",
    "expected_drift_finding_boundary_id",
    "expected_echo_containment_boundary_id",
    "expected_echo_disposition_boundary_id",
    "expected_echo_receipt_boundary_id",
    "expected_echo_rejection_boundary_id",
    "expected_echo_trace_boundary_id",
    "expected_lifecycle_record_id",
    "expected_lifecycle_transition_id",
    "expected_proposed_expression_reference_id",
    "expected_record_id",
    "expected_runtime_schema_record_id",
    "expected_validation_finding_boundary_id",
    "expected_validation_input_boundary_id",
    "expected_version_custody_id",
    "identity_field",
    "identity_namespace",
    "with_expected_bundle_identity",
    "with_expected_id",
)
