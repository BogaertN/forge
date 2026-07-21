"""Deterministic Slice 42C record identities."""
from __future__ import annotations
from dataclasses import replace
from typing import Any
from .canonical import deterministic_digest, stable_identifier
from .schema import (
    AuthorizedMeaningAdmissionRecord, ExpressionEligibilityEvaluationInput,
    ExpressionEligibilityFinding, ExpressionEligibilityResult,
    OutwardExpressionAuthorityRecord,
)

_ID_FIELDS = {
    OutwardExpressionAuthorityRecord: ("authority_record_id", "outward_expression_authority_record"),
    ExpressionEligibilityEvaluationInput: ("evaluation_input_id", "expression_eligibility_evaluation_input"),
    AuthorizedMeaningAdmissionRecord: ("admission_record_id", "authorized_meaning_admission_record"),
    ExpressionEligibilityFinding: ("finding_id", "expression_eligibility_finding"),
}

def expected_record_id(record: Any) -> str:
    try: field_name, namespace = _ID_FIELDS[type(record)]
    except KeyError as exc: raise TypeError(f"unsupported Slice 42C identity type: {type(record)!r}") from exc
    return stable_identifier(namespace, record, exclude_fields=(field_name,))

def with_expected_id(record: Any) -> Any:
    field_name, _ = _ID_FIELDS[type(record)]
    return replace(record, **{field_name: expected_record_id(record)})

def expected_result_digest(record: ExpressionEligibilityResult) -> str:
    return deterministic_digest(record, exclude_fields=("result_id", "result_digest"))

def expected_result_id(record: ExpressionEligibilityResult) -> str:
    return f"expression_eligibility_result:{expected_result_digest(record)}"

def with_expected_result_identity(record: ExpressionEligibilityResult) -> ExpressionEligibilityResult:
    digest = expected_result_digest(record)
    return replace(record, result_digest=digest, result_id=f"expression_eligibility_result:{digest}")

__all__ = ("expected_record_id", "expected_result_digest", "expected_result_id", "with_expected_id", "with_expected_result_identity")
