"""Deterministic identities for Slice 42E records and plans."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .canonical import deterministic_digest, stable_identifier
from .schema import (
    ControlledExpressionPlan,
    ExpressionPlanConstructionAuthorityRecord,
    ExpressionPlanConstructionFinding,
    ExpressionPlanConstructionInput,
    ExpressionPlanConstructionResult,
    ExpressionPlanSection,
)


_ID_FIELDS: dict[type[Any], tuple[str, str]] = {
    ExpressionPlanConstructionAuthorityRecord: (
        "planning_authority_record_id",
        "expression_plan_construction_authority_record",
    ),
    ExpressionPlanConstructionInput: (
        "plan_input_id",
        "expression_plan_construction_input",
    ),
    ExpressionPlanSection: (
        "section_id",
        "controlled_expression_plan_section",
    ),
    ExpressionPlanConstructionFinding: (
        "finding_id",
        "expression_plan_construction_finding",
    ),
}


def expected_record_id(record: Any) -> str:
    try:
        field_name, namespace = _ID_FIELDS[type(record)]
    except KeyError as error:
        raise TypeError(
            f"unsupported Slice 42E identity type: {type(record)!r}"
        ) from error
    return stable_identifier(namespace, record, exclude_fields=(field_name,))


def with_expected_id(record: Any) -> Any:
    try:
        field_name, _ = _ID_FIELDS[type(record)]
    except KeyError as error:
        raise TypeError(
            f"unsupported Slice 42E identity type: {type(record)!r}"
        ) from error
    return replace(record, **{field_name: expected_record_id(record)})


def expected_plan_digest(record: ControlledExpressionPlan) -> str:
    return deterministic_digest(
        record,
        exclude_fields=("expression_plan_id", "expression_plan_digest"),
    )


def expected_plan_id(record: ControlledExpressionPlan) -> str:
    return f"controlled_expression_plan:{expected_plan_digest(record)}"


def with_expected_plan_identity(
    record: ControlledExpressionPlan,
) -> ControlledExpressionPlan:
    digest = expected_plan_digest(record)
    return replace(
        record,
        expression_plan_digest=digest,
        expression_plan_id=f"controlled_expression_plan:{digest}",
    )


def expected_result_digest(
    record: ExpressionPlanConstructionResult,
) -> str:
    return deterministic_digest(
        record,
        exclude_fields=("result_id", "result_digest"),
    )


def expected_result_id(record: ExpressionPlanConstructionResult) -> str:
    return f"expression_plan_construction_result:{expected_result_digest(record)}"


def with_expected_result_identity(
    record: ExpressionPlanConstructionResult,
) -> ExpressionPlanConstructionResult:
    digest = expected_result_digest(record)
    return replace(
        record,
        result_digest=digest,
        result_id=f"expression_plan_construction_result:{digest}",
    )


__all__ = (
    "expected_plan_digest",
    "expected_plan_id",
    "expected_record_id",
    "expected_result_digest",
    "expected_result_id",
    "with_expected_id",
    "with_expected_plan_identity",
    "with_expected_result_identity",
)
