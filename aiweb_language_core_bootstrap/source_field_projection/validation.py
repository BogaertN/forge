"""Deterministic validation for Slice 36B projection records."""

from __future__ import annotations

import hashlib
import unicodedata

from ..input_event_custody import (
    CUSTODY_SCHEMA_VERSION,
    CUSTODY_SPEC_ID,
    CUSTODY_SPEC_VERSION,
)
from ..schema import ValidationReport, issue, stable_record_id
from .reconstruction import reconstruct_source_field
from .schema import (
    ABSOLUTE_MAX_PROJECTION_CODE_POINTS,
    ABSOLUTE_MAX_PROJECTION_OBSERVATIONS,
    GRAPHEME_PROFILE_ID,
    PROJECTION_SCHEMA_VERSION,
    PROJECTION_SPEC_ID,
    PROJECTION_SPEC_VERSION,
    SOURCE_FIELD_SCHEMA_ID,
    UNICODE_DATABASE_VERSION,
    GraphemeBoundaryStatus,
    GraphemeProfileStatus,
    SourceBoundaryRecord,
    SourceCodePointRecord,
    SourceFieldProjectionLimits,
    SourceFieldProjectionRecord,
    SourceFieldProjectionResult,
    SourceFieldProjectionStatus,
    SourceFieldReconstructionResult,
    SourceFieldSupportStatus,
    SourceObservationRecord,
)


def _report(issues: list[object]) -> ValidationReport:
    return ValidationReport(
        schema_version=PROJECTION_SCHEMA_VERSION,
        ok=not issues,
        issues=tuple(issues),
    )


def _base_issues(record: object) -> list[object]:
    issues: list[object] = []
    if getattr(record, "projection_spec_id", None) != PROJECTION_SPEC_ID:
        issues.append(issue("projection_spec_id", "projection_spec_id_mismatch"))
    if (
        getattr(record, "projection_spec_version", None)
        != PROJECTION_SPEC_VERSION
    ):
        issues.append(
            issue(
                "projection_spec_version",
                "projection_spec_version_mismatch",
            )
        )
    if getattr(record, "schema_version", None) != PROJECTION_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    return issues




def _expected_source_span_id(
    *,
    projection: SourceFieldProjectionRecord,
    code_point_start: int,
    code_point_end: int,
    utf8_byte_start: int,
    utf8_byte_end: int,
    exact_text: str,
) -> str:
    body = {
        "input_event_id": projection.source_event_id,
        "source_sha256": projection.source_sha256,
        "code_point_start": code_point_start,
        "code_point_end": code_point_end,
        "utf8_byte_start": utf8_byte_start,
        "utf8_byte_end": utf8_byte_end,
        "code_point_length": code_point_end - code_point_start,
        "utf8_byte_length": utf8_byte_end - utf8_byte_start,
        "span_sha256": hashlib.sha256(
            exact_text.encode("utf-8", "strict")
        ).hexdigest(),
        "is_root_span": (
            code_point_start == 0
            and code_point_end == projection.source_code_point_length
        ),
        "custody_spec_id": CUSTODY_SPEC_ID,
        "custody_spec_version": CUSTODY_SPEC_VERSION,
        "schema_version": CUSTODY_SCHEMA_VERSION,
    }
    return stable_record_id("source_span", body)


def validate_source_field_projection_limits(
    limits: object,
) -> ValidationReport:
    if type(limits) is not SourceFieldProjectionLimits:
        return _report([issue("limits", "invalid_record_type")])
    issues = _base_issues(limits)
    if limits.limits_id != limits.expected_id():
        issues.append(issue("limits_id", "stable_identifier_mismatch"))
    if type(limits.max_code_points) is not int:
        issues.append(issue("max_code_points", "invalid_exact_integer_type"))
    elif not 0 <= limits.max_code_points <= ABSOLUTE_MAX_PROJECTION_CODE_POINTS:
        issues.append(issue("max_code_points", "invalid_limit_range"))
    if type(limits.max_observations) is not int:
        issues.append(issue("max_observations", "invalid_exact_integer_type"))
    elif not 0 <= limits.max_observations <= ABSOLUTE_MAX_PROJECTION_OBSERVATIONS:
        issues.append(issue("max_observations", "invalid_limit_range"))
    return _report(issues)


def validate_source_code_point_record(
    atom: object,
) -> ValidationReport:
    if type(atom) is not SourceCodePointRecord:
        return _report([issue("atom", "invalid_record_type")])
    issues = _base_issues(atom)
    if atom.atom_id != atom.expected_id():
        issues.append(issue("atom_id", "stable_identifier_mismatch"))
    if type(atom.ordinal) is not int or atom.ordinal < 0:
        issues.append(issue("ordinal", "invalid_ordinal"))
    if type(atom.exact_text) is not str or len(atom.exact_text) != 1:
        issues.append(issue("exact_text", "must_be_one_code_point"))
    else:
        expected_scalar = f"U+{ord(atom.exact_text):04X}"
        if atom.unicode_code_point != expected_scalar:
            issues.append(issue("unicode_code_point", "scalar_value_mismatch"))
        if atom.utf8_hex != atom.exact_text.encode("utf-8", "strict").hex():
            issues.append(issue("utf8_hex", "exact_utf8_mismatch"))
        if atom.general_category != unicodedata.category(atom.exact_text):
            issues.append(issue("general_category", "unicode_category_mismatch"))
        if atom.unicode_name != unicodedata.name(atom.exact_text, ""):
            issues.append(issue("unicode_name", "unicode_name_mismatch"))
        if atom.combining_class != unicodedata.combining(atom.exact_text):
            issues.append(issue("combining_class", "combining_class_mismatch"))
    if atom.code_point_end != atom.code_point_start + 1:
        issues.append(issue("code_point_end", "atom_width_must_equal_one"))
    if atom.utf8_byte_end <= atom.utf8_byte_start:
        issues.append(issue("utf8_byte_end", "invalid_utf8_interval"))
    if atom.support_status is SourceFieldSupportStatus.SUPPORTED:
        if atom.unsupported_reason_code:
            issues.append(issue("unsupported_reason_code", "must_be_empty"))
    elif not atom.unsupported_reason_code:
        issues.append(issue("unsupported_reason_code", "required_for_unsupported"))
    return _report(issues)


def validate_source_boundary_record(
    boundary: object,
) -> ValidationReport:
    if type(boundary) is not SourceBoundaryRecord:
        return _report([issue("boundary", "invalid_record_type")])
    issues = _base_issues(boundary)
    if boundary.boundary_id != boundary.expected_id():
        issues.append(issue("boundary_id", "stable_identifier_mismatch"))
    if type(boundary.ordinal) is not int or boundary.ordinal < 0:
        issues.append(issue("ordinal", "invalid_ordinal"))
    if boundary.code_point_offset != boundary.ordinal:
        issues.append(issue("code_point_offset", "boundary_ordinal_mismatch"))
    if type(boundary.utf8_byte_offset) is not int or boundary.utf8_byte_offset < 0:
        issues.append(issue("utf8_byte_offset", "invalid_utf8_byte_offset"))
    return _report(issues)


def validate_source_observation_record(
    observation: object,
) -> ValidationReport:
    if type(observation) is not SourceObservationRecord:
        return _report([issue("observation", "invalid_record_type")])
    issues = _base_issues(observation)
    if observation.observation_id != observation.expected_id():
        issues.append(issue("observation_id", "stable_identifier_mismatch"))
    if type(observation.ordinal) is not int or observation.ordinal < 0:
        issues.append(issue("ordinal", "invalid_ordinal"))
    if observation.code_point_end <= observation.code_point_start:
        issues.append(issue("code_point_end", "invalid_source_interval"))
    if observation.utf8_byte_end <= observation.utf8_byte_start:
        issues.append(issue("utf8_byte_end", "invalid_utf8_interval"))
    if observation.utf8_hex != observation.exact_text.encode("utf-8", "strict").hex():
        issues.append(issue("utf8_hex", "exact_utf8_mismatch"))
    if len(observation.member_atom_ids) != (
        observation.code_point_end - observation.code_point_start
    ):
        issues.append(issue("member_atom_ids", "source_width_mismatch"))
    if type(observation.repeat_count) is not int or observation.repeat_count < 1:
        issues.append(issue("repeat_count", "invalid_repeat_count"))
    if observation.semantic_authority is not False:
        issues.append(issue("semantic_authority", "must_remain_false"))
    if observation.operator_binding_authority is not False:
        issues.append(issue("operator_binding_authority", "must_remain_false"))
    return _report(issues)


def validate_source_field_projection(
    projection: object,
) -> ValidationReport:
    if type(projection) is not SourceFieldProjectionRecord:
        return _report([issue("projection", "invalid_record_type")])
    issues = _base_issues(projection)
    if projection.source_field_schema_id != SOURCE_FIELD_SCHEMA_ID:
        issues.append(issue("source_field_schema_id", "field_schema_id_mismatch"))
    if projection.projection_id != projection.expected_id():
        issues.append(issue("projection_id", "stable_identifier_mismatch"))
    if projection.unicode_database_version != UNICODE_DATABASE_VERSION:
        issues.append(
            issue("unicode_database_version", "unicode_database_version_mismatch")
        )
    if projection.grapheme_profile_id != GRAPHEME_PROFILE_ID:
        issues.append(issue("grapheme_profile_id", "grapheme_profile_mismatch"))
    if projection.code_point_count != len(projection.code_points):
        issues.append(issue("code_point_count", "record_count_mismatch"))
    if projection.boundary_count != len(projection.boundaries):
        issues.append(issue("boundary_count", "record_count_mismatch"))
    if projection.observation_count != len(projection.observations):
        issues.append(issue("observation_count", "record_count_mismatch"))
    if projection.code_point_count != projection.source_code_point_length:
        issues.append(issue("code_point_count", "source_length_mismatch"))
    if projection.boundary_count != projection.code_point_count + 1:
        issues.append(issue("boundary_count", "must_equal_code_points_plus_one"))

    atom_ids = tuple(atom.atom_id for atom in projection.code_points)
    for ordinal, atom in enumerate(projection.code_points):
        issues.extend(validate_source_code_point_record(atom).issues)
        if atom.projection_id != projection.projection_id:
            issues.append(issue("code_points", "projection_identity_mismatch"))
        if atom.source_event_id != projection.source_event_id:
            issues.append(issue("code_points", "source_event_identity_mismatch"))
        expected_span_id = _expected_source_span_id(
            projection=projection,
            code_point_start=atom.code_point_start,
            code_point_end=atom.code_point_end,
            utf8_byte_start=atom.utf8_byte_start,
            utf8_byte_end=atom.utf8_byte_end,
            exact_text=atom.exact_text,
        )
        if atom.source_span_id != expected_span_id:
            issues.append(issue("code_points", "source_span_identity_mismatch"))
        if atom.ordinal != ordinal:
            issues.append(issue("code_points", "noncontiguous_atom_ordinal"))
        expected_previous = atom_ids[ordinal - 1] if ordinal > 0 else None
        expected_next = atom_ids[ordinal + 1] if ordinal + 1 < len(atom_ids) else None
        if atom.previous_atom_id != expected_previous:
            issues.append(issue("code_points", "previous_adjacency_mismatch"))
        if atom.next_atom_id != expected_next:
            issues.append(issue("code_points", "next_adjacency_mismatch"))
        if atom.code_point_start != ordinal or atom.code_point_end != ordinal + 1:
            issues.append(issue("code_points", "code_point_ordering_mismatch"))

    for ordinal, boundary in enumerate(projection.boundaries):
        issues.extend(validate_source_boundary_record(boundary).issues)
        if boundary.projection_id != projection.projection_id:
            issues.append(issue("boundaries", "projection_identity_mismatch"))
        if boundary.source_event_id != projection.source_event_id:
            issues.append(issue("boundaries", "source_event_identity_mismatch"))
        if boundary.ordinal != ordinal:
            issues.append(issue("boundaries", "noncontiguous_boundary_ordinal"))
        expected_byte_offset = (
            projection.code_points[ordinal].utf8_byte_start
            if ordinal < len(projection.code_points)
            else projection.source_utf8_byte_length
        )
        if boundary.utf8_byte_offset != expected_byte_offset:
            issues.append(issue("boundaries", "utf8_boundary_offset_mismatch"))
        expected_previous = atom_ids[ordinal - 1] if ordinal > 0 else None
        expected_next = atom_ids[ordinal] if ordinal < len(atom_ids) else None
        if boundary.previous_atom_id != expected_previous:
            issues.append(issue("boundaries", "previous_adjacency_mismatch"))
        if boundary.next_atom_id != expected_next:
            issues.append(issue("boundaries", "next_adjacency_mismatch"))

    for ordinal, observation in enumerate(projection.observations):
        issues.extend(validate_source_observation_record(observation).issues)
        if observation.projection_id != projection.projection_id:
            issues.append(issue("observations", "projection_identity_mismatch"))
        if observation.source_event_id != projection.source_event_id:
            issues.append(issue("observations", "source_event_identity_mismatch"))
        if observation.ordinal != ordinal:
            issues.append(issue("observations", "noncontiguous_observation_ordinal"))
        if not 0 <= observation.code_point_start < observation.code_point_end <= len(atom_ids):
            issues.append(issue("observations", "source_interval_out_of_bounds"))
        else:
            members = projection.code_points[
                observation.code_point_start : observation.code_point_end
            ]
            if observation.member_atom_ids != atom_ids[
                observation.code_point_start : observation.code_point_end
            ]:
                issues.append(issue("observations", "member_atom_identity_mismatch"))
            expected_text = "".join(item.exact_text for item in members)
            expected_byte_start = members[0].utf8_byte_start
            expected_byte_end = members[-1].utf8_byte_end
            if observation.exact_text != expected_text:
                issues.append(issue("observations", "exact_text_mismatch"))
            if observation.utf8_byte_start != expected_byte_start:
                issues.append(issue("observations", "utf8_byte_start_mismatch"))
            if observation.utf8_byte_end != expected_byte_end:
                issues.append(issue("observations", "utf8_byte_end_mismatch"))
            expected_span_id = _expected_source_span_id(
                projection=projection,
                code_point_start=observation.code_point_start,
                code_point_end=observation.code_point_end,
                utf8_byte_start=observation.utf8_byte_start,
                utf8_byte_end=observation.utf8_byte_end,
                exact_text=observation.exact_text,
            )
            if observation.source_span_id != expected_span_id:
                issues.append(issue("observations", "source_span_identity_mismatch"))

    observed_unsupported_count = sum(
        atom.support_status is SourceFieldSupportStatus.UNSUPPORTED
        for atom in projection.code_points
    )
    if projection.unsupported_code_point_count != observed_unsupported_count:
        issues.append(
            issue("unsupported_code_point_count", "unsupported_count_mismatch")
        )
    if projection.status is SourceFieldProjectionStatus.SOURCE_FIELD_SUPPORTED:
        if observed_unsupported_count:
            issues.append(issue("status", "supported_status_has_unsupported_atoms"))
        if projection.predecessor_field_envelope_id is None:
            issues.append(issue("predecessor_field_envelope_id", "required"))
        if projection.structural_progression_allowed is not True:
            issues.append(issue("structural_progression_allowed", "must_be_true"))
    elif projection.status is SourceFieldProjectionStatus.SOURCE_FIELD_PARTIALLY_UNSUPPORTED:
        if not observed_unsupported_count:
            issues.append(issue("status", "partial_status_requires_unsupported_atoms"))
        if projection.predecessor_field_envelope_id is not None:
            issues.append(
                issue("predecessor_field_envelope_id", "must_be_none_when_held")
            )
        if projection.structural_progression_allowed is not False:
            issues.append(issue("structural_progression_allowed", "must_remain_false"))
    else:
        issues.append(issue("status", "projection_record_has_noncreated_status"))

    unavailable = any(
        boundary.grapheme_boundary_status is GraphemeBoundaryStatus.UNAVAILABLE
        for boundary in projection.boundaries
    )
    expected_profile = (
        GraphemeProfileStatus.PARTIAL_CODE_POINT_FALLBACK
        if unavailable
        else GraphemeProfileStatus.COMPLETE_EXACT_ASCII_PROFILE
    )
    if projection.grapheme_profile_status is not expected_profile:
        issues.append(issue("grapheme_profile_status", "profile_status_mismatch"))

    for field_name in (
        "operator_application_available",
        "source_text_replaced",
        "normalization_performed",
        "casefolding_performed",
        "whitespace_collapse_performed",
        "transliteration_performed",
        "tokenization_performed",
        "vocabulary_lookup_performed",
        "part_of_speech_tagging_performed",
        "concept_lookup_performed",
        "predicate_binding_performed",
        "reference_resolution_performed",
        "operator_binding_performed",
        "operator_application_performed",
        "phase_assignment_performed",
        "intention_inference_performed",
        "meaning_created",
        "legacy_runtime_consulted",
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "environment_access_performed",
        "memory_read_performed",
        "memory_write_performed",
        "route_registration_performed",
        "tool_routing_performed",
        "action_performed",
        "delivery_performed",
    ):
        if getattr(projection, field_name) is not False:
            issues.append(issue(field_name, "must_remain_false"))
    for field_name in (
        "source_coverage_complete",
        "source_ordering_complete",
        "source_adjacency_complete",
        "exact_reconstruction_proven",
    ):
        if getattr(projection, field_name) is not True:
            issues.append(issue(field_name, "must_remain_true"))

    reconstruction = reconstruct_source_field(projection)
    if not reconstruction.ok:
        issues.append(issue("reconstruction", reconstruction.reason_code))
    if reconstruction.reconstructed_source_sha256 != projection.reconstructed_source_sha256:
        issues.append(issue("reconstructed_source_sha256", "proof_hash_mismatch"))
    return _report(issues)


def validate_source_field_projection_result(
    result: object,
) -> ValidationReport:
    if type(result) is not SourceFieldProjectionResult:
        return _report([issue("result", "invalid_record_type")])
    issues = _base_issues(result)
    if result.result_id != result.expected_id():
        issues.append(issue("result_id", "stable_identifier_mismatch"))
    if result.projection_created:
        issues.extend(validate_source_field_projection(result.projection).issues)
        if result.projection is None:
            issues.append(issue("projection", "required_when_created"))
    elif result.projection is not None:
        issues.append(issue("projection", "must_be_none_when_not_created"))
    if result.projection_created and result.source_preserved_in_custody is not True:
        issues.append(issue("source_preserved_in_custody", "must_be_true"))
    if result.structural_progression_allowed:
        if result.status is not SourceFieldProjectionStatus.SOURCE_FIELD_SUPPORTED:
            issues.append(issue("structural_progression_allowed", "status_mismatch"))
    for field_name in (
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "environment_access_performed",
        "memory_read_performed",
        "memory_write_performed",
        "route_registration_performed",
        "tool_routing_performed",
        "action_performed",
        "delivery_performed",
    ):
        if getattr(result, field_name) is not False:
            issues.append(issue(field_name, "must_remain_false"))
    return _report(issues)


def validate_source_field_reconstruction_result(
    result: object,
) -> ValidationReport:
    if type(result) is not SourceFieldReconstructionResult:
        return _report([issue("result", "invalid_record_type")])
    issues = _base_issues(result)
    if result.result_id != result.expected_id():
        issues.append(issue("result_id", "stable_identifier_mismatch"))
    if result.ok and result.validation_issue_codes:
        issues.append(issue("validation_issue_codes", "must_be_empty_when_ok"))
    if not result.ok and not result.validation_issue_codes:
        issues.append(issue("validation_issue_codes", "required_when_not_ok"))
    return _report(issues)
