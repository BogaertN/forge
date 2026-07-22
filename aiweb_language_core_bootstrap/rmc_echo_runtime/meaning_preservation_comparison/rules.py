"""Closed deterministic Slice 43D comparison rules."""

from __future__ import annotations

from typing import Any

from .schema import (
    ComparisonCode,
    ComparisonExecutionStatus,
    DimensionValueSnapshot,
    FindingOutcome,
)


def unique_values(*groups: tuple[str, ...]) -> tuple[str, ...]:
    values: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for value in group:
            if value not in seen:
                seen.add(value)
                values.append(value)
    return tuple(values)


def source_objects(source: Any) -> dict[str, Any]:
    integration_input = source.integration_input
    integration_result = source.integration_result
    surface_input = integration_input.surface_realization_input
    surface_result = integration_input.surface_realization_result
    plan_input = surface_input.plan_input
    plan_result = surface_input.plan_result
    projection_input = plan_input.projection_input
    projection_result = plan_input.projection_result
    eligibility_input = projection_input.expression_eligibility_evaluation_input
    eligibility_result = projection_input.expression_eligibility_result
    selected_result = integration_input.source_selected_meaning_integration_result
    selected_record = selected_result.integrated_selected_meaning_record
    candidate = surface_result.expression_candidate
    outward = integration_result.governed_outward_meaning_record
    expression_link = integration_result.expression_link_record
    return {
        "integration_input": integration_input,
        "integration_result": integration_result,
        "surface_input": surface_input,
        "surface_result": surface_result,
        "plan_input": plan_input,
        "plan_result": plan_result,
        "projection_input": projection_input,
        "projection_result": projection_result,
        "eligibility_input": eligibility_input,
        "eligibility_result": eligibility_result,
        "selected_result": selected_result,
        "selected_record": selected_record,
        "candidate": candidate,
        "outward": outward,
        "expression_link": expression_link,
        "obligation_package": projection_result.obligation_package,
        "expression_plan": plan_result.expression_plan,
    }


def outcome_for_snapshots(
    source: DimensionValueSnapshot,
    proposed: DimensionValueSnapshot,
) -> FindingOutcome:
    if source.dimension is not proposed.dimension:
        return FindingOutcome.CONFLICTED
    if source.conflict_refs or proposed.conflict_refs:
        return FindingOutcome.CONFLICTED
    if not source.supported or not proposed.supported:
        return FindingOutcome.UNSUPPORTED
    if source.indeterminate_refs or proposed.indeterminate_refs:
        return FindingOutcome.INDETERMINATE
    if (
        not source.field_paths
        or not proposed.field_paths
        or not source.values
        or not proposed.values
    ):
        return FindingOutcome.MISSING
    if source.values == proposed.values:
        return FindingOutcome.PRESERVED
    return FindingOutcome.CHANGED


_STATUS_PRIORITY = (
    ComparisonCode.RAW_TEXT_PROHIBITED,
    ComparisonCode.REQUEST_TYPE_INVALID,
    ComparisonCode.REQUEST_ID_INVALID,
    ComparisonCode.REQUEST_OPERATION_INVALID,
    ComparisonCode.EXPLICIT_REQUEST_REQUIRED,
    ComparisonCode.SOURCE_ADMISSION_RESULT_TYPE_INVALID,
    ComparisonCode.SOURCE_NOT_ADMITTED,
    ComparisonCode.SOURCE_CLOSEOUT_TYPE_INVALID,
    ComparisonCode.UNSUPPORTED_VERSION,
    ComparisonCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
    ComparisonCode.MISSING_REQUIRED_VALUE,
    ComparisonCode.INCONSISTENT_ANCESTRY,
    ComparisonCode.SOURCE_ANCESTRY_INVALID,
)


_STATUS_BY_CODE = {
    ComparisonCode.SOURCE_NOT_ADMITTED:
        ComparisonExecutionStatus.HELD_SOURCE_NOT_ADMITTED,
    ComparisonCode.SOURCE_ADMISSION_RESULT_TYPE_INVALID:
        ComparisonExecutionStatus.HELD_SOURCE_NOT_ADMITTED,
    ComparisonCode.UNSUPPORTED_VERSION:
        ComparisonExecutionStatus.HELD_UNSUPPORTED_VERSION,
    ComparisonCode.RECOMPUTED_OR_FABRICATED_IDENTITY:
        ComparisonExecutionStatus.HELD_IDENTITY_INVALID,
    ComparisonCode.MISSING_REQUIRED_VALUE:
        ComparisonExecutionStatus.HELD_MISSING_REQUIRED_VALUE,
    ComparisonCode.INCONSISTENT_ANCESTRY:
        ComparisonExecutionStatus.HELD_INCONSISTENT_ANCESTRY,
    ComparisonCode.SOURCE_ANCESTRY_INVALID:
        ComparisonExecutionStatus.HELD_INCONSISTENT_ANCESTRY,
}


def status_for_codes(
    codes: tuple[ComparisonCode, ...],
) -> ComparisonExecutionStatus:
    code_set = set(codes)
    for code in _STATUS_PRIORITY:
        if code in code_set:
            return _STATUS_BY_CODE.get(
                code,
                ComparisonExecutionStatus.HELD_INVALID_REQUEST,
            )
    return ComparisonExecutionStatus.HELD_INVALID_REQUEST


__all__ = (
    "outcome_for_snapshots",
    "source_objects",
    "status_for_codes",
    "unique_values",
)
