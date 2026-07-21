"""Deterministic Slice 42B identity helpers."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from ..schema import (
    ExpressionEligibilityStatusRecord,
    ExpressionPlanBoundaryRecord,
    ExpressionPreservationObligationCustodyRecord,
    ExpressionReceiptBoundaryRecord,
    ExpressionTraceBoundaryRecord,
    GovernedOutwardMeaningBoundaryRecord,
    OutwardExpressionAuthorityRequirementRecord,
    OutwardExpressionRuntimeSchemaRecord,
    RealizedExpressionBoundaryRecord,
    SelectedMeaningExpressionSourceCustodyRecord,
)
from .canonical import deterministic_record_digest, stable_identifier
from .schema import (
    OutwardExpressionGovernanceBundle,
    OutwardExpressionLifecycleRecord,
    OutwardExpressionLifecycleTransitionRecord,
    OutwardExpressionVersionCustody,
)


_ID_FIELDS: dict[type[Any], tuple[str, str]] = {
    SelectedMeaningExpressionSourceCustodyRecord: (
        "source_custody_id",
        "outward_expression_source_custody",
    ),
    OutwardExpressionAuthorityRequirementRecord: (
        "authority_requirement_id",
        "outward_expression_authority_requirement",
    ),
    ExpressionPreservationObligationCustodyRecord: (
        "obligation_custody_id",
        "expression_preservation_obligation_custody",
    ),
    ExpressionEligibilityStatusRecord: (
        "expression_eligibility_status_id",
        "expression_eligibility_status",
    ),
    GovernedOutwardMeaningBoundaryRecord: (
        "governed_outward_meaning_boundary_id",
        "governed_outward_meaning_boundary",
    ),
    ExpressionPlanBoundaryRecord: (
        "expression_plan_boundary_id",
        "expression_plan_boundary",
    ),
    RealizedExpressionBoundaryRecord: (
        "realized_expression_boundary_id",
        "realized_expression_boundary",
    ),
    ExpressionTraceBoundaryRecord: (
        "expression_trace_boundary_id",
        "expression_trace_boundary",
    ),
    ExpressionReceiptBoundaryRecord: (
        "expression_receipt_boundary_id",
        "expression_receipt_boundary",
    ),
    OutwardExpressionRuntimeSchemaRecord: (
        "outward_expression_runtime_schema_record_id",
        "outward_expression_runtime_schema_record",
    ),
    OutwardExpressionVersionCustody: (
        "custody_id",
        "outward_expression_version_custody",
    ),
    OutwardExpressionLifecycleRecord: (
        "lifecycle_record_id",
        "outward_expression_lifecycle_record",
    ),
    OutwardExpressionLifecycleTransitionRecord: (
        "transition_id",
        "outward_expression_lifecycle_transition",
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


def expected_source_custody_id(
    record: SelectedMeaningExpressionSourceCustodyRecord,
) -> str:
    return expected_record_id(record)


def expected_authority_requirement_id(
    record: OutwardExpressionAuthorityRequirementRecord,
) -> str:
    return expected_record_id(record)


def expected_obligation_custody_id(
    record: ExpressionPreservationObligationCustodyRecord,
) -> str:
    return expected_record_id(record)


def expected_expression_eligibility_status_id(
    record: ExpressionEligibilityStatusRecord,
) -> str:
    return expected_record_id(record)


def expected_governed_outward_meaning_boundary_id(
    record: GovernedOutwardMeaningBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_expression_plan_boundary_id(
    record: ExpressionPlanBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_realized_expression_boundary_id(
    record: RealizedExpressionBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_expression_trace_boundary_id(
    record: ExpressionTraceBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_expression_receipt_boundary_id(
    record: ExpressionReceiptBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_runtime_schema_record_id(
    record: OutwardExpressionRuntimeSchemaRecord,
) -> str:
    return expected_record_id(record)


def expected_version_custody_id(
    record: OutwardExpressionVersionCustody,
) -> str:
    return expected_record_id(record)


def expected_lifecycle_record_id(
    record: OutwardExpressionLifecycleRecord,
) -> str:
    return expected_record_id(record)


def expected_lifecycle_transition_id(
    record: OutwardExpressionLifecycleTransitionRecord,
) -> str:
    return expected_record_id(record)


def expected_bundle_digest(record: OutwardExpressionGovernanceBundle) -> str:
    return deterministic_record_digest(
        record,
        exclude_fields=("bundle_id", "bundle_digest"),
    )


def expected_bundle_id(record: OutwardExpressionGovernanceBundle) -> str:
    return f"outward_expression_governance_bundle:{expected_bundle_digest(record)}"


def with_expected_bundle_identity(
    record: OutwardExpressionGovernanceBundle,
) -> OutwardExpressionGovernanceBundle:
    digest = expected_bundle_digest(record)
    return replace(
        record,
        bundle_digest=digest,
        bundle_id=f"outward_expression_governance_bundle:{digest}",
    )


__all__ = (
    "expected_authority_requirement_id",
    "expected_bundle_digest",
    "expected_bundle_id",
    "expected_expression_eligibility_status_id",
    "expected_expression_plan_boundary_id",
    "expected_expression_receipt_boundary_id",
    "expected_expression_trace_boundary_id",
    "expected_governed_outward_meaning_boundary_id",
    "expected_lifecycle_record_id",
    "expected_lifecycle_transition_id",
    "expected_obligation_custody_id",
    "expected_realized_expression_boundary_id",
    "expected_record_id",
    "expected_runtime_schema_record_id",
    "expected_source_custody_id",
    "expected_version_custody_id",
    "identity_field",
    "identity_namespace",
    "with_expected_bundle_identity",
    "with_expected_id",
)
