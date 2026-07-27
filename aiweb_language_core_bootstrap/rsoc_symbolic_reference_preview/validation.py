"""Deterministic validation for RSOC reference-preview records."""

from __future__ import annotations

from ..schema import ValidationReport, issue
from .schema import (
    RsocOperatorReferenceNode,
    RsocReferenceDocument,
    RsocReferencePreviewResult,
    RsocReferencePreviewStatus,
    SourceCoverageKind,
    SourceCoverageSegment,
)


def validate_source_coverage_segment(value: object) -> ValidationReport:
    issues = []
    if type(value) is not SourceCoverageSegment:
        return ValidationReport("rsoc-reference-preview-validation-v1", False, (issue("segment", "invalid_type"),))
    if value.segment_id != value.expected_id():
        issues.append(issue("segment_id", "stable_id_mismatch"))
    if not 0 <= value.code_point_start < value.code_point_end:
        issues.append(issue("code_point_range", "invalid_range"))
    if not 0 <= value.utf8_byte_start < value.utf8_byte_end:
        issues.append(issue("utf8_byte_range", "invalid_range"))
    if value.utf8_hex != value.exact_text.encode("utf-8").hex():
        issues.append(issue("utf8_hex", "exact_source_mismatch"))
    if len(value.atom_ids) != value.code_point_end - value.code_point_start:
        issues.append(issue("atom_ids", "coverage_length_mismatch"))
    if value.kind is SourceCoverageKind.OPERATOR_REFERENCE and not value.operator_contract_id:
        issues.append(issue("operator_contract_id", "required_for_operator_reference"))
    if value.kind is not SourceCoverageKind.OPERATOR_REFERENCE and value.operator_contract_id:
        issues.append(issue("operator_contract_id", "forbidden_for_non_operator_segment"))
    return ValidationReport("rsoc-reference-preview-validation-v1", not issues, tuple(issues))


def validate_operator_reference_node(value: object) -> ValidationReport:
    issues = []
    if type(value) is not RsocOperatorReferenceNode:
        return ValidationReport("rsoc-reference-preview-validation-v1", False, (issue("reference", "invalid_type"),))
    if value.reference_id != value.expected_id():
        issues.append(issue("reference_id", "stable_id_mismatch"))
    for name in (
        "source_binding_performed",
        "operator_application_performed",
        "numeric_transform_performed",
        "entropy_mutation_performed",
        "phase_assignment_performed",
        "meaning_created",
        "permission_inferred",
    ):
        if getattr(value, name) is not False:
            issues.append(issue(name, "must_remain_false"))
    if value.exact_glyph_recognition_performed is not True:
        issues.append(issue("exact_glyph_recognition_performed", "must_remain_true"))
    if value.registry_reference_only is not True:
        issues.append(issue("registry_reference_only", "must_remain_true"))
    return ValidationReport("rsoc-reference-preview-validation-v1", not issues, tuple(issues))


def validate_reference_document(value: object) -> ValidationReport:
    issues = []
    if type(value) is not RsocReferenceDocument:
        return ValidationReport("rsoc-reference-preview-validation-v1", False, (issue("document", "invalid_type"),))
    if value.document_id != value.expected_id():
        issues.append(issue("document_id", "stable_id_mismatch"))
    if value.operator_reference_count != len(value.operator_reference_ids):
        issues.append(issue("operator_reference_count", "count_mismatch"))
    for name in (
        "composition_interpreted",
        "arguments_bound",
        "source_binding_performed",
        "operator_application_performed",
        "successor_field_created",
        "phase_assigned",
        "meaning_created",
    ):
        if getattr(value, name) is not False:
            issues.append(issue(name, "must_remain_false"))
    return ValidationReport("rsoc-reference-preview-validation-v1", not issues, tuple(issues))


def validate_reference_preview_result(value: object) -> ValidationReport:
    issues = []
    if type(value) is not RsocReferencePreviewResult:
        return ValidationReport("rsoc-reference-preview-validation-v1", False, (issue("result", "invalid_type"),))
    if value.result_id != value.expected_id():
        issues.append(issue("result_id", "stable_id_mismatch"))
    for segment in value.coverage:
        report = validate_source_coverage_segment(segment)
        issues.extend(report.issues)
    for reference in value.operator_references:
        report = validate_operator_reference_node(reference)
        issues.extend(report.issues)
    if value.recognized_operator_count != len(value.operator_references):
        issues.append(issue("recognized_operator_count", "count_mismatch"))
    ready = value.status is RsocReferencePreviewStatus.REFERENCE_PREVIEW_READY
    if value.ready is not ready:
        issues.append(issue("ready", "status_mismatch"))
    if ready and value.document is None:
        issues.append(issue("document", "required_when_ready"))
    if not ready and value.document is not None:
        issues.append(issue("document", "forbidden_when_held"))
    if value.document is not None:
        issues.extend(validate_reference_document(value.document).issues)
    boundary = value.boundary
    for name, state in vars_from_slots(boundary).items():
        if name in {"read_only", "registry_reference_only"}:
            if state is not True:
                issues.append(issue(f"boundary.{name}", "must_remain_true"))
        elif name == "exact_glyph_recognition_performed":
            if type(state) is not bool:
                issues.append(issue(f"boundary.{name}", "must_be_boolean"))
        elif state is not False:
            issues.append(issue(f"boundary.{name}", "must_remain_false"))
    if value.ready and boundary.exact_glyph_recognition_performed is not True:
        issues.append(issue("boundary.exact_glyph_recognition_performed", "must_be_true_when_ready"))
    return ValidationReport("rsoc-reference-preview-validation-v1", not issues, tuple(issues))


def vars_from_slots(value: object) -> dict[str, object]:
    return {name: getattr(value, name) for name in value.__dataclass_fields__}
