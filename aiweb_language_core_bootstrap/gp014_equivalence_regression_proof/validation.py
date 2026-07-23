"""Fail-closed validation for Slice 46 proof records."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .authority import (
    EXPECTED_FAILURE_INJECTION_CASES,
    EXPECTED_NEGATIVE_CASES,
    EXPECTED_POSITIVE_CASES,
    EXPECTED_TOTAL_EQUIVALENCE_CASES,
)
from .schema import BoundaryFailureResult, EquivalenceCaseResult, EquivalenceFixture, EquivalenceProofReport


class ValidationCode(str, Enum):
    TYPE = "type"
    IDENTITY = "identity"
    CONTENT = "content"
    COUNT = "count"
    AUTHORITY = "authority"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    path: str
    code: ValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class ValidationReport:
    issues: tuple[ValidationIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues


def _issue(rows: list[ValidationIssue], path: str, code: ValidationCode, detail: str) -> None:
    rows.append(ValidationIssue(path, code, detail))


def validate_fixture(value: Any) -> ValidationReport:
    rows: list[ValidationIssue] = []
    if not isinstance(value, EquivalenceFixture):
        _issue(rows, "fixture", ValidationCode.TYPE, "wrong record type")
    else:
        if value.fixture_id != value.expected_id():
            _issue(rows, "fixture.fixture_id", ValidationCode.IDENTITY, "identity mismatch")
        if not value.question or value.expected_class not in {"ANSWERED", "CONTAINED"}:
            _issue(rows, "fixture", ValidationCode.CONTENT, "invalid fixture")
    return ValidationReport(tuple(rows))


def validate_case(value: Any) -> ValidationReport:
    rows: list[ValidationIssue] = []
    if not isinstance(value, EquivalenceCaseResult):
        _issue(rows, "case", ValidationCode.TYPE, "wrong record type")
    else:
        if value.case_id != value.expected_id():
            _issue(rows, "case.case_id", ValidationCode.IDENTITY, "identity mismatch")
        if value.dimension_count != len(value.dimension_results) or value.dimension_count == 0:
            _issue(rows, "case.dimension_count", ValidationCode.COUNT, "dimension count mismatch")
        if not value.all_dimensions_equivalent:
            _issue(rows, "case.dimensions", ValidationCode.CONTENT, "equivalence failed")
        if not value.direct_replay_deterministic or not value.adapter_replay_deterministic:
            _issue(rows, "case.replay", ValidationCode.CONTENT, "replay was not deterministic")
        if not value.request_forwarded_byte_for_byte or not value.adapter_source_returned_unchanged:
            _issue(rows, "case.adapter", ValidationCode.CONTENT, "adapter did not preserve source")
        if value.adapter_added_authority or value.gp014_modified or value.gp014_superseded or value.gp015_used:
            _issue(rows, "case.authority", ValidationCode.AUTHORITY, "prohibited authority detected")
        if not value.delivery_equivalent_within_source_scope:
            _issue(rows, "case.delivery", ValidationCode.CONTENT, "delivery behavior differed")
    return ValidationReport(tuple(rows))


def validate_boundary_failure(value: Any) -> ValidationReport:
    rows: list[ValidationIssue] = []
    if not isinstance(value, BoundaryFailureResult):
        _issue(rows, "boundary_failure", ValidationCode.TYPE, "wrong record type")
    else:
        if value.failure_id != value.expected_id():
            _issue(rows, "boundary_failure.failure_id", ValidationCode.IDENTITY, "identity mismatch")
        if not value.passed or value.raw_marker_exposed or value.raw_exception_exposed_flag:
            _issue(rows, "boundary_failure", ValidationCode.CONTENT, "failure was not contained")
        if not value.deterministic_replay:
            _issue(rows, "boundary_failure.replay", ValidationCode.CONTENT, "failure replay not deterministic")
    return ValidationReport(tuple(rows))


def validate_report(value: Any) -> ValidationReport:
    rows: list[ValidationIssue] = []
    if not isinstance(value, EquivalenceProofReport):
        _issue(rows, "report", ValidationCode.TYPE, "wrong record type")
        return ValidationReport(tuple(rows))
    if value.report_id != value.expected_id():
        _issue(rows, "report.report_id", ValidationCode.IDENTITY, "identity mismatch")
    if value.positive_case_count != EXPECTED_POSITIVE_CASES:
        _issue(rows, "report.positive_case_count", ValidationCode.COUNT, "positive count mismatch")
    if value.negative_case_count != EXPECTED_NEGATIVE_CASES:
        _issue(rows, "report.negative_case_count", ValidationCode.COUNT, "negative count mismatch")
    if value.total_case_count != EXPECTED_TOTAL_EQUIVALENCE_CASES or len(value.cases) != EXPECTED_TOTAL_EQUIVALENCE_CASES:
        _issue(rows, "report.total_case_count", ValidationCode.COUNT, "case count mismatch")
    if len(value.boundary_failures) != EXPECTED_FAILURE_INJECTION_CASES:
        _issue(rows, "report.boundary_failures", ValidationCode.COUNT, "failure injection count mismatch")
    for index, case in enumerate(value.cases):
        for issue in validate_case(case).issues:
            _issue(rows, f"report.cases[{index}].{issue.path}", issue.code, issue.detail)
    for index, failure in enumerate(value.boundary_failures):
        for issue in validate_boundary_failure(failure).issues:
            _issue(rows, f"report.boundary_failures[{index}].{issue.path}", issue.code, issue.detail)
    required = (
        value.all_cases_equivalent,
        value.all_replays_deterministic,
        value.all_boundary_failures_contained,
        value.accepted_input_equivalent,
        value.computation_equivalent,
        value.expression_equivalent,
        value.validation_equivalent,
        value.accepted_failure_behavior_equivalent,
        value.no_gp014_modification,
        value.no_gp014_supersession,
        value.no_gp015_reuse,
        value.no_route_api_ui_authority,
        value.no_memory_tool_action_resource_authority,
        value.no_adapter_delivery_authority,
    )
    if not all(required):
        _issue(rows, "report.acceptance", ValidationCode.CONTENT, "required proof field false")
    if value.gp014_imported_before_explicit_enable or value.disabled_adapter_called_gp014 or value.invalid_request_called_gp014:
        _issue(rows, "report.import_boundary", ValidationCode.AUTHORITY, "GP-014 crossed pre-enable boundary")
    if value.gp015_loaded_after and not value.gp015_loaded_before:
        _issue(rows, "report.gp015", ValidationCode.AUTHORITY, "GP-015 loaded during proof")
    if value.production_ready or value.release_authorized:
        _issue(rows, "report.scope", ValidationCode.AUTHORITY, "proof cannot claim release")
    return ValidationReport(tuple(rows))


__all__ = (
    "ValidationCode", "ValidationIssue", "ValidationReport",
    "validate_fixture", "validate_case", "validate_boundary_failure", "validate_report",
)
