"""Deterministic Slice 41B identity helpers."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from ..schema import (
    AlternativeCandidateCustodyRecord,
    GateCustodyReferenceRecord,
    InheritedLimitationCustodyRecord,
    SelectedMeaningDecisionStatusRecord,
    SelectedMeaningRuntimeSchemaRecord,
    SelectionAuthorityRequirementRecord,
    SelectionCandidateCustodyRecord,
    SelectionEligibilityStatusRecord,
    SelectionReceiptBoundaryRecord,
    SelectionTraceBoundaryRecord,
    UnresolvedStateCustodyRecord,
)
from .canonical import deterministic_record_digest, stable_identifier
from .schema import (
    SelectedMeaningGovernanceBundle,
    SelectedMeaningLifecycleRecord,
    SelectedMeaningLifecycleTransitionRecord,
    SelectedMeaningVersionCustody,
)


_ID_FIELDS: dict[type[Any], tuple[str, str]] = {
    SelectionCandidateCustodyRecord: (
        "selection_candidate_custody_id",
        "selection_candidate_custody",
    ),
    GateCustodyReferenceRecord: (
        "gate_custody_reference_id",
        "gate_custody_reference",
    ),
    SelectionAuthorityRequirementRecord: (
        "selection_authority_requirement_id",
        "selection_authority_requirement",
    ),
    AlternativeCandidateCustodyRecord: (
        "alternative_candidate_custody_id",
        "alternative_candidate_custody",
    ),
    UnresolvedStateCustodyRecord: (
        "unresolved_state_custody_id",
        "unresolved_state_custody",
    ),
    InheritedLimitationCustodyRecord: (
        "inherited_limitation_custody_id",
        "inherited_limitation_custody",
    ),
    SelectionEligibilityStatusRecord: (
        "selection_eligibility_status_id",
        "selection_eligibility_status",
    ),
    SelectedMeaningDecisionStatusRecord: (
        "selected_meaning_decision_status_id",
        "selected_meaning_decision_status",
    ),
    SelectionTraceBoundaryRecord: (
        "selection_trace_boundary_id",
        "selection_trace_boundary",
    ),
    SelectionReceiptBoundaryRecord: (
        "selection_receipt_boundary_id",
        "selection_receipt_boundary",
    ),
    SelectedMeaningRuntimeSchemaRecord: (
        "selected_meaning_runtime_schema_record_id",
        "selected_meaning_runtime_schema_record",
    ),
    SelectedMeaningVersionCustody: (
        "custody_id",
        "selected_meaning_version_custody",
    ),
    SelectedMeaningLifecycleRecord: (
        "lifecycle_record_id",
        "selected_meaning_lifecycle_record",
    ),
    SelectedMeaningLifecycleTransitionRecord: (
        "transition_id",
        "selected_meaning_lifecycle_transition",
    ),
}


def identity_field(record_type: type[Any]) -> str:
    try:
        return _ID_FIELDS[record_type][0]
    except KeyError as error:
        raise TypeError(f"unsupported identity record type: {record_type!r}") from error


def identity_namespace(record_type: type[Any]) -> str:
    try:
        return _ID_FIELDS[record_type][1]
    except KeyError as error:
        raise TypeError(f"unsupported identity record type: {record_type!r}") from error


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


def expected_selection_candidate_custody_id(
    record: SelectionCandidateCustodyRecord,
) -> str:
    return expected_record_id(record)


def expected_gate_custody_reference_id(
    record: GateCustodyReferenceRecord,
) -> str:
    return expected_record_id(record)


def expected_selection_authority_requirement_id(
    record: SelectionAuthorityRequirementRecord,
) -> str:
    return expected_record_id(record)


def expected_alternative_candidate_custody_id(
    record: AlternativeCandidateCustodyRecord,
) -> str:
    return expected_record_id(record)


def expected_unresolved_state_custody_id(
    record: UnresolvedStateCustodyRecord,
) -> str:
    return expected_record_id(record)


def expected_inherited_limitation_custody_id(
    record: InheritedLimitationCustodyRecord,
) -> str:
    return expected_record_id(record)


def expected_selection_eligibility_status_id(
    record: SelectionEligibilityStatusRecord,
) -> str:
    return expected_record_id(record)


def expected_selected_meaning_decision_status_id(
    record: SelectedMeaningDecisionStatusRecord,
) -> str:
    return expected_record_id(record)


def expected_selection_trace_boundary_id(
    record: SelectionTraceBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_selection_receipt_boundary_id(
    record: SelectionReceiptBoundaryRecord,
) -> str:
    return expected_record_id(record)


def expected_runtime_schema_record_id(
    record: SelectedMeaningRuntimeSchemaRecord,
) -> str:
    return expected_record_id(record)


def expected_version_custody_id(record: SelectedMeaningVersionCustody) -> str:
    return expected_record_id(record)


def expected_lifecycle_record_id(record: SelectedMeaningLifecycleRecord) -> str:
    return expected_record_id(record)


def expected_lifecycle_transition_id(
    record: SelectedMeaningLifecycleTransitionRecord,
) -> str:
    return expected_record_id(record)


def expected_bundle_digest(record: SelectedMeaningGovernanceBundle) -> str:
    return deterministic_record_digest(
        record,
        exclude_fields=("bundle_id", "bundle_digest"),
    )


def expected_bundle_id(record: SelectedMeaningGovernanceBundle) -> str:
    return f"selected_meaning_governance_bundle:{expected_bundle_digest(record)}"


def with_expected_bundle_identity(
    record: SelectedMeaningGovernanceBundle,
) -> SelectedMeaningGovernanceBundle:
    digest = expected_bundle_digest(record)
    return replace(
        record,
        bundle_digest=digest,
        bundle_id=f"selected_meaning_governance_bundle:{digest}",
    )


__all__ = (
    "expected_alternative_candidate_custody_id",
    "expected_bundle_digest",
    "expected_bundle_id",
    "expected_gate_custody_reference_id",
    "expected_inherited_limitation_custody_id",
    "expected_lifecycle_record_id",
    "expected_lifecycle_transition_id",
    "expected_record_id",
    "expected_runtime_schema_record_id",
    "expected_selected_meaning_decision_status_id",
    "expected_selection_authority_requirement_id",
    "expected_selection_candidate_custody_id",
    "expected_selection_eligibility_status_id",
    "expected_selection_receipt_boundary_id",
    "expected_selection_trace_boundary_id",
    "expected_unresolved_state_custody_id",
    "expected_version_custody_id",
    "identity_field",
    "identity_namespace",
    "with_expected_bundle_identity",
    "with_expected_id",
)
