"""Deterministic identity helpers for Slice 41C."""
from __future__ import annotations

from dataclasses import replace

from .canonical import deterministic_record_digest, stable_identifier
from .schema import (
    SelectionEligibilityEvaluationInput,
    SelectionEligibilityFinding,
    SelectionEligibilityResult,
)


def expected_evaluation_input_id(record: SelectionEligibilityEvaluationInput) -> str:
    return stable_identifier(
        "selection_eligibility_evaluation_input",
        record,
        exclude_fields=("evaluation_input_id",),
    )


def with_expected_evaluation_input_id(
    record: SelectionEligibilityEvaluationInput,
) -> SelectionEligibilityEvaluationInput:
    return replace(record, evaluation_input_id=expected_evaluation_input_id(record))


def expected_finding_id(record: SelectionEligibilityFinding) -> str:
    return stable_identifier(
        "selection_eligibility_finding",
        record,
        exclude_fields=("finding_id",),
    )


def with_expected_finding_id(
    record: SelectionEligibilityFinding,
) -> SelectionEligibilityFinding:
    return replace(record, finding_id=expected_finding_id(record))


def expected_result_digest(record: SelectionEligibilityResult) -> str:
    return deterministic_record_digest(
        record,
        exclude_fields=("result_id", "canonical_digest"),
    )


def expected_result_id(record: SelectionEligibilityResult) -> str:
    return f"selection_eligibility_result:{expected_result_digest(record)}"


def with_expected_result_identity(
    record: SelectionEligibilityResult,
) -> SelectionEligibilityResult:
    digest = expected_result_digest(record)
    return replace(
        record,
        canonical_digest=digest,
        result_id=f"selection_eligibility_result:{digest}",
    )


__all__ = (
    "expected_evaluation_input_id",
    "expected_finding_id",
    "expected_result_digest",
    "expected_result_id",
    "with_expected_evaluation_input_id",
    "with_expected_finding_id",
    "with_expected_result_identity",
)
