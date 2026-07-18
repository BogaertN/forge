"""Fail-closed independent validation for Slice 39E candidate sets."""

from __future__ import annotations

import re
from typing import Any

from ..candidate_semantic_content import (
    CandidateSemanticContentAssemblyResult,
    CandidateSemanticContentStatus,
    validate_assembly_result,
)
from .identity import (
    expected_alternative_reference_id,
    expected_candidate_set_digest,
    expected_candidate_set_id,
    expected_duplicate_group_id,
    expected_member_id,
    expected_profile_id,
    expected_result_id,
    expected_shared_ancestry_id,
)
from .schema import (
    DIGEST_ALGORITHM,
    SLICE39E_PROFILE_VERSION,
    SLICE39E_SCHEMA_VERSION,
    SLICE39E_SPEC_ID,
    SLICE39E_SPEC_VERSION,
    CandidateExactDuplicateGroup,
    CandidateMaterialAlternativeReference,
    CandidateMeaningSet,
    CandidateSetMember,
    CandidateSetPreservationResult,
    CandidateSetProfileIdentity,
    CandidateSetStatus,
    CandidateSetValidationCode,
    CandidateSetValidationError,
    CandidateSetValidationIssue,
    CandidateSetValidationReport,
    CandidateSharedAncestryReference,
)

_ID = re.compile(r"^[A-Za-z0-9_.:-]+$")
_SHA = re.compile(r"^[0-9a-f]{64}$")


def _issue(issues: list[CandidateSetValidationIssue], path: str, code: CandidateSetValidationCode, detail: str) -> None:
    issues.append(CandidateSetValidationIssue(path, code, detail))


def _report(issues: list[CandidateSetValidationIssue]) -> CandidateSetValidationReport:
    return CandidateSetValidationReport(tuple(issues))


def _identifier(value: Any, path: str, issues: list[CandidateSetValidationIssue]) -> None:
    if type(value) is not str or not value or _ID.fullmatch(value) is None:
        _issue(issues, path, CandidateSetValidationCode.INVALID_IDENTIFIER, "non-empty governed identifier required")


def _sha(value: Any, path: str, issues: list[CandidateSetValidationIssue]) -> None:
    if type(value) is not str or _SHA.fullmatch(value) is None:
        _issue(issues, path, CandidateSetValidationCode.INVALID_SHA256, "lowercase SHA-256 required")


def _tuple(value: Any, path: str, issues: list[CandidateSetValidationIssue]) -> tuple[Any, ...]:
    if type(value) is not tuple:
        _issue(issues, path, CandidateSetValidationCode.INVALID_TUPLE, "exact tuple required")
        return ()
    return value


def _ids(value: Any, path: str, issues: list[CandidateSetValidationIssue]) -> tuple[Any, ...]:
    items = _tuple(value, path, issues)
    for index, item in enumerate(items):
        _identifier(item, f"{path}[{index}]", issues)
    if len(items) != len(set(items)):
        _issue(issues, path, CandidateSetValidationCode.DUPLICATE_VALUE, "duplicate identifiers prohibited")
    return items


def _exact_bool(value: Any, expected: bool, path: str, issues: list[CandidateSetValidationIssue], code: CandidateSetValidationCode = CandidateSetValidationCode.INVALID_BOOLEAN) -> None:
    if type(value) is not bool or value is not expected:
        _issue(issues, path, code, f"exact {expected} required")


def validate_profile(record: Any) -> CandidateSetValidationReport:
    issues: list[CandidateSetValidationIssue] = []
    if type(record) is not CandidateSetProfileIdentity:
        _issue(issues, "profile", CandidateSetValidationCode.TYPE_MISMATCH, "exact CandidateSetProfileIdentity required")
        return _report(issues)
    _identifier(record.profile_id, "profile.profile_id", issues)
    _identifier(record.profile_key, "profile.profile_key", issues)
    if record.profile_version != SLICE39E_PROFILE_VERSION:
        _issue(issues, "profile.profile_version", CandidateSetValidationCode.INVALID_VERSION, "canonical profile version required")
    for name in (
        "zero_one_many_preservation_required", "deterministic_ordering_required",
        "exact_duplicate_detection_required", "duplicate_occurrence_preservation_required",
        "material_alternative_references_required", "shared_ancestry_preservation_required",
        "candidate_specific_boundaries_required",
    ):
        _exact_bool(getattr(record, name), True, f"profile.{name}", issues)
    prohibited = (
        "ranking_allowed", "confidence_scoring_allowed", "preferred_candidate_allowed",
        "winner_selection_allowed", "nearest_candidate_allowed", "tie_breaking_allowed",
        "automatic_ambiguity_resolution_allowed", "ambiguous_meaning_state_creation_allowed",
        "gate_progression_allowed", "truth_evidence_permission_allowed",
        "route_action_memory_rendering_delivery_allowed",
    )
    for name in prohibited:
        _exact_bool(getattr(record, name), False, f"profile.{name}", issues, CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED)
    if record.spec_id != SLICE39E_SPEC_ID or record.spec_version != SLICE39E_SPEC_VERSION or record.schema_version != SLICE39E_SCHEMA_VERSION:
        _issue(issues, "profile", CandidateSetValidationCode.PROFILE_MISMATCH, "canonical specification identity required")
    if record.profile_id != expected_profile_id(record):
        _issue(issues, "profile.profile_id", CandidateSetValidationCode.IDENTITY_MISMATCH, "deterministic profile identity mismatch")
    return _report(issues)


def validate_member(record: Any) -> CandidateSetValidationReport:
    issues: list[CandidateSetValidationIssue] = []
    if type(record) is not CandidateSetMember:
        _issue(issues, "member", CandidateSetValidationCode.TYPE_MISMATCH, "exact CandidateSetMember required")
        return _report(issues)
    for name in (
        "member_id", "candidate_result_id", "candidate_assembly_id", "candidate_payload_id",
        "candidate_content_id", "lineage_id", "source_event_id",
    ):
        _identifier(getattr(record, name), f"member.{name}", issues)
    _sha(record.candidate_canonical_digest, "member.candidate_canonical_digest", issues)
    _sha(record.source_sha256, "member.source_sha256", issues)
    if type(record.deterministic_position) is not int or record.deterministic_position < 1:
        _issue(issues, "member.deterministic_position", CandidateSetValidationCode.INVALID_INTEGER, "positive exact integer required")
    if type(record.duplicate_occurrence_index) is not int or record.duplicate_occurrence_index < 1:
        _issue(issues, "member.duplicate_occurrence_index", CandidateSetValidationCode.INVALID_INTEGER, "positive exact integer required")
    for name in (
        "source_span_ids", "limitation_refs", "missing_role_refs", "conflicting_role_refs",
        "effect_boundary_refs", "capability_reference_refs",
    ):
        _ids(getattr(record, name), f"member.{name}", issues)
    _exact_bool(record.candidate_only, True, "member.candidate_only", issues)
    if type(record.exact_duplicate_detected) is not bool:
        _issue(issues, "member.exact_duplicate_detected", CandidateSetValidationCode.INVALID_BOOLEAN, "exact boolean required")
    for name, code in (
        ("ranked", CandidateSetValidationCode.RANKING_PROHIBITED),
        ("confidence_scored", CandidateSetValidationCode.CONFIDENCE_SCORING_PROHIBITED),
        ("preferred", CandidateSetValidationCode.PREFERENCE_PROHIBITED),
        ("selected", CandidateSetValidationCode.SELECTION_PROHIBITED),
        ("ambiguous_state_created", CandidateSetValidationCode.AMBIGUOUS_STATE_PROHIBITED),
    ):
        _exact_bool(getattr(record, name), False, f"member.{name}", issues, code)
    if record.schema_version != SLICE39E_SCHEMA_VERSION:
        _issue(issues, "member.schema_version", CandidateSetValidationCode.INVALID_VERSION, "canonical schema version required")
    if record.member_id != expected_member_id(record):
        _issue(issues, "member.member_id", CandidateSetValidationCode.IDENTITY_MISMATCH, "deterministic member identity mismatch")
    return _report(issues)


def validate_duplicate_group(record: Any) -> CandidateSetValidationReport:
    issues: list[CandidateSetValidationIssue] = []
    if type(record) is not CandidateExactDuplicateGroup:
        _issue(issues, "duplicate", CandidateSetValidationCode.TYPE_MISMATCH, "exact CandidateExactDuplicateGroup required")
        return _report(issues)
    for name in ("duplicate_group_id", "candidate_result_id", "primary_member_id"):
        _identifier(getattr(record, name), f"duplicate.{name}", issues)
    _sha(record.canonical_candidate_digest, "duplicate.canonical_candidate_digest", issues)
    duplicate_ids = _ids(record.duplicate_member_ids, "duplicate.duplicate_member_ids", issues)
    if not duplicate_ids:
        _issue(issues, "duplicate.duplicate_member_ids", CandidateSetValidationCode.DUPLICATE_MAPPING_MISMATCH, "at least one duplicate member required")
    if type(record.occurrence_count) is not int or record.occurrence_count != len(duplicate_ids) + 1:
        _issue(issues, "duplicate.occurrence_count", CandidateSetValidationCode.COUNT_MISMATCH, "occurrence count must include primary plus duplicates")
    _exact_bool(record.exact_duplicate, True, "duplicate.exact_duplicate", issues)
    _exact_bool(record.silently_collapsed, False, "duplicate.silently_collapsed", issues, CandidateSetValidationCode.SILENT_COLLAPSE_PROHIBITED)
    _exact_bool(record.ranking_assigned, False, "duplicate.ranking_assigned", issues, CandidateSetValidationCode.RANKING_PROHIBITED)
    _exact_bool(record.selected_candidate_assigned, False, "duplicate.selected_candidate_assigned", issues, CandidateSetValidationCode.SELECTION_PROHIBITED)
    if record.schema_version != SLICE39E_SCHEMA_VERSION:
        _issue(issues, "duplicate.schema_version", CandidateSetValidationCode.INVALID_VERSION, "canonical schema version required")
    if record.duplicate_group_id != expected_duplicate_group_id(record):
        _issue(issues, "duplicate.duplicate_group_id", CandidateSetValidationCode.IDENTITY_MISMATCH, "deterministic duplicate identity mismatch")
    return _report(issues)


def validate_shared_ancestry(record: Any) -> CandidateSetValidationReport:
    issues: list[CandidateSetValidationIssue] = []
    if type(record) is not CandidateSharedAncestryReference:
        _issue(issues, "ancestry", CandidateSetValidationCode.TYPE_MISMATCH, "exact CandidateSharedAncestryReference required")
        return _report(issues)
    _identifier(record.shared_ancestry_id, "ancestry.shared_ancestry_id", issues)
    _identifier(record.source_event_id, "ancestry.source_event_id", issues)
    _sha(record.source_sha256, "ancestry.source_sha256", issues)
    for name in (
        "member_ids", "lineage_ids", "shared_source_span_ids", "shared_structural_ancestry_ids",
        "shared_operator_definition_ids", "shared_concept_candidate_ids", "shared_sense_candidate_ids",
        "shared_action_predicate_candidate_ids", "shared_role_layout_candidate_ids",
        "shared_predecessor_receipt_ids",
    ):
        _ids(getattr(record, name), f"ancestry.{name}", issues)
    _exact_bool(record.ancestry_preserved, True, "ancestry.ancestry_preserved", issues)
    _exact_bool(record.lineages_merged, False, "ancestry.lineages_merged", issues, CandidateSetValidationCode.SHARED_ANCESTRY_MISMATCH)
    if record.schema_version != SLICE39E_SCHEMA_VERSION:
        _issue(issues, "ancestry.schema_version", CandidateSetValidationCode.INVALID_VERSION, "canonical schema version required")
    if record.shared_ancestry_id != expected_shared_ancestry_id(record):
        _issue(issues, "ancestry.shared_ancestry_id", CandidateSetValidationCode.IDENTITY_MISMATCH, "deterministic shared ancestry identity mismatch")
    return _report(issues)


def validate_alternative_reference(record: Any) -> CandidateSetValidationReport:
    issues: list[CandidateSetValidationIssue] = []
    if type(record) is not CandidateMaterialAlternativeReference:
        _issue(issues, "alternative", CandidateSetValidationCode.TYPE_MISMATCH, "exact CandidateMaterialAlternativeReference required")
        return _report(issues)
    for name in (
        "alternative_reference_id", "left_member_id", "right_member_id",
        "left_candidate_result_id", "right_candidate_result_id", "shared_ancestry_ref",
    ):
        _identifier(getattr(record, name), f"alternative.{name}", issues)
    dimensions = _tuple(record.exact_difference_dimensions, "alternative.exact_difference_dimensions", issues)
    if not dimensions or not all(type(item) is str and item for item in dimensions):
        _issue(issues, "alternative.exact_difference_dimensions", CandidateSetValidationCode.ALTERNATIVE_MAPPING_MISMATCH, "at least one exact difference dimension required")
    if tuple(sorted(set(dimensions))) != tuple(sorted(dimensions)):
        _issue(issues, "alternative.exact_difference_dimensions", CandidateSetValidationCode.INVALID_ORDER, "unique deterministic difference dimensions required")
    for name in (
        "left_limitation_refs", "right_limitation_refs", "left_missing_role_refs", "right_missing_role_refs",
        "left_conflicting_role_refs", "right_conflicting_role_refs", "left_effect_boundary_refs",
        "right_effect_boundary_refs", "left_capability_reference_refs", "right_capability_reference_refs",
    ):
        _ids(getattr(record, name), f"alternative.{name}", issues)
    _exact_bool(record.exact_duplicate, False, "alternative.exact_duplicate", issues)
    _exact_bool(record.materially_distinct_by_exact_content, True, "alternative.materially_distinct_by_exact_content", issues)
    for name, code in (
        ("ambiguity_determined", CandidateSetValidationCode.AMBIGUITY_RESOLUTION_PROHIBITED),
        ("ranked", CandidateSetValidationCode.RANKING_PROHIBITED),
        ("preferred", CandidateSetValidationCode.PREFERENCE_PROHIBITED),
        ("selected", CandidateSetValidationCode.SELECTION_PROHIBITED),
        ("tie_broken", CandidateSetValidationCode.TIE_BREAKING_PROHIBITED),
    ):
        _exact_bool(getattr(record, name), False, f"alternative.{name}", issues, code)
    if record.schema_version != SLICE39E_SCHEMA_VERSION:
        _issue(issues, "alternative.schema_version", CandidateSetValidationCode.INVALID_VERSION, "canonical schema version required")
    if record.alternative_reference_id != expected_alternative_reference_id(record):
        _issue(issues, "alternative.alternative_reference_id", CandidateSetValidationCode.IDENTITY_MISMATCH, "deterministic alternative identity mismatch")
    return _report(issues)


def _extend(issues: list[CandidateSetValidationIssue], report: CandidateSetValidationReport, prefix: str) -> None:
    for item in report.issues:
        issues.append(CandidateSetValidationIssue(f"{prefix}.{item.path}", item.code, item.detail))


def validate_candidate_set(record: Any) -> CandidateSetValidationReport:
    issues: list[CandidateSetValidationIssue] = []
    if type(record) is not CandidateMeaningSet:
        _issue(issues, "set", CandidateSetValidationCode.TYPE_MISMATCH, "exact CandidateMeaningSet required")
        return _report(issues)
    _identifier(record.candidate_set_id, "set.candidate_set_id", issues)
    if type(record.status) is not CandidateSetStatus or record.status is CandidateSetStatus.SET_REJECTED:
        _issue(issues, "set.status", CandidateSetValidationCode.INVALID_ENUM, "accepted set status required")
    _extend(issues, validate_profile(record.profile), "set")
    candidate_results = _tuple(record.candidate_results, "set.candidate_results", issues)
    result_ids: list[str] = []
    for index, result in enumerate(candidate_results):
        if type(result) is not CandidateSemanticContentAssemblyResult:
            _issue(issues, f"set.candidate_results[{index}]", CandidateSetValidationCode.TYPE_MISMATCH, "exact Slice 39D result required")
            continue
        if not validate_assembly_result(result).ok or result.status is not CandidateSemanticContentStatus.ASSEMBLED or result.assembly is None:
            _issue(issues, f"set.candidate_results[{index}]", CandidateSetValidationCode.CANDIDATE_RESULT_INVALID, "valid assembled Slice 39D result required")
        result_ids.append(result.result_id)
    if len(result_ids) != len(set(result_ids)):
        _issue(issues, "set.candidate_results", CandidateSetValidationCode.DUPLICATE_VALUE, "unique candidate result records required")
    members = _tuple(record.members, "set.members", issues)
    for index, member in enumerate(members):
        _extend(issues, validate_member(member), f"set.members[{index}]")
    duplicates = _tuple(record.exact_duplicate_groups, "set.exact_duplicate_groups", issues)
    for index, duplicate in enumerate(duplicates):
        _extend(issues, validate_duplicate_group(duplicate), f"set.exact_duplicate_groups[{index}]")
    ancestry = _tuple(record.shared_ancestry_references, "set.shared_ancestry_references", issues)
    for index, item in enumerate(ancestry):
        _extend(issues, validate_shared_ancestry(item), f"set.shared_ancestry_references[{index}]")
    alternatives = _tuple(record.material_alternative_references, "set.material_alternative_references", issues)
    for index, item in enumerate(alternatives):
        _extend(issues, validate_alternative_reference(item), f"set.material_alternative_references[{index}]")
    if record.source_event_id is None:
        if record.source_sha256 is not None or record.input_candidate_count != 0:
            _issue(issues, "set.source_event_id", CandidateSetValidationCode.SOURCE_EVENT_MISMATCH, "source identity absent only for zero set")
    else:
        _identifier(record.source_event_id, "set.source_event_id", issues)
        _sha(record.source_sha256, "set.source_sha256", issues)
    for name in (
        "input_candidate_count", "unique_candidate_count", "exact_duplicate_occurrence_count",
        "alternative_reference_count",
    ):
        if type(getattr(record, name)) is not int or getattr(record, name) < 0:
            _issue(issues, f"set.{name}", CandidateSetValidationCode.INVALID_INTEGER, "non-negative exact integer required")
    required_true = (
        "deterministic_ordering_verified", "exact_duplicate_detection_verified",
        "duplicate_occurrences_preserved", "shared_ancestry_preserved",
        "candidate_specific_boundaries_preserved",
    )
    for name in required_true:
        _exact_bool(getattr(record, name), True, f"set.{name}", issues)
    prohibited = (
        ("candidates_ranked", CandidateSetValidationCode.RANKING_PROHIBITED),
        ("confidence_scores_created", CandidateSetValidationCode.CONFIDENCE_SCORING_PROHIBITED),
        ("preferred_candidate_created", CandidateSetValidationCode.PREFERENCE_PROHIBITED),
        ("winner_selected", CandidateSetValidationCode.SELECTION_PROHIBITED),
        ("nearest_candidate_selected", CandidateSetValidationCode.SELECTION_PROHIBITED),
        ("tie_breaking_performed", CandidateSetValidationCode.TIE_BREAKING_PROHIBITED),
        ("ambiguity_resolved", CandidateSetValidationCode.AMBIGUITY_RESOLUTION_PROHIBITED),
        ("ambiguous_meaning_state_created", CandidateSetValidationCode.AMBIGUOUS_STATE_PROHIBITED),
        ("gate_progression_created", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("truth_determined", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("evidence_validated", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("permission_granted", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("route_created", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("action_performed", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("memory_accessed", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("rendered", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("delivered", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
    )
    for name, code in prohibited:
        _exact_bool(getattr(record, name), False, f"set.{name}", issues, code)
    if record.digest_algorithm != DIGEST_ALGORITHM:
        _issue(issues, "set.digest_algorithm", CandidateSetValidationCode.INVALID_VERSION, "sha256 required")
    _sha(record.canonical_digest, "set.canonical_digest", issues)
    if record.schema_version != SLICE39E_SCHEMA_VERSION:
        _issue(issues, "set.schema_version", CandidateSetValidationCode.INVALID_VERSION, "canonical schema version required")
    if record.candidate_set_id != expected_candidate_set_id(record):
        _issue(issues, "set.candidate_set_id", CandidateSetValidationCode.IDENTITY_MISMATCH, "deterministic set identity mismatch")
    if record.canonical_digest != expected_candidate_set_digest(record):
        _issue(issues, "set.canonical_digest", CandidateSetValidationCode.IDENTITY_MISMATCH, "deterministic set digest mismatch")

    # Independent deterministic reconstruction proves ordering, duplicate,
    # alternative, shared-ancestry and candidate-specific mappings.
    if not issues:
        from .preservation import preserve_candidate_set
        by_id = {item.result_id: item for item in candidate_results}
        reconstructed_occurrences: list[CandidateSemanticContentAssemblyResult] = []
        for member in sorted(members, key=lambda item: item.deterministic_position):
            result = by_id.get(member.candidate_result_id)
            if result is None:
                _issue(issues, "set.members", CandidateSetValidationCode.MEMBER_MAPPING_MISMATCH, "member result reference missing")
                break
            reconstructed_occurrences.append(result)
        if not issues:
            rebuilt = preserve_candidate_set(tuple(reconstructed_occurrences), profile=record.profile)
            if rebuilt.candidate_set != record:
                _issue(issues, "set", CandidateSetValidationCode.MEMBER_MAPPING_MISMATCH, "deterministic candidate-set reconstruction mismatch")
    return _report(issues)


def validate_preservation_result(record: Any) -> CandidateSetValidationReport:
    issues: list[CandidateSetValidationIssue] = []
    if type(record) is not CandidateSetPreservationResult:
        _issue(issues, "result", CandidateSetValidationCode.TYPE_MISMATCH, "exact CandidateSetPreservationResult required")
        return _report(issues)
    _identifier(record.result_id, "result.result_id", issues)
    if type(record.status) is not CandidateSetStatus:
        _issue(issues, "result.status", CandidateSetValidationCode.INVALID_ENUM, "closed status required")
    if type(record.reason_code) is not str or not record.reason_code:
        _issue(issues, "result.reason_code", CandidateSetValidationCode.INVALID_IDENTIFIER, "non-empty reason code required")
    _tuple(record.issues, "result.issues", issues)
    for name in (
        "input_candidate_count", "unique_candidate_count", "exact_duplicate_occurrence_count",
        "alternative_reference_count",
    ):
        if type(getattr(record, name)) is not int or getattr(record, name) < 0:
            _issue(issues, f"result.{name}", CandidateSetValidationCode.INVALID_INTEGER, "non-negative exact integer required")
    if record.status is CandidateSetStatus.SET_REJECTED:
        if record.candidate_set is not None or not record.issues:
            _issue(issues, "result", CandidateSetValidationCode.CANDIDATE_RESULT_INVALID, "rejected result requires issues and no set")
    else:
        _extend(issues, validate_candidate_set(record.candidate_set), "result")
        if record.issues:
            _issue(issues, "result.issues", CandidateSetValidationCode.CANDIDATE_RESULT_INVALID, "accepted result must have no issues")
        if record.candidate_set is not None:
            for name in (
                "source_event_id", "source_sha256", "input_candidate_count", "unique_candidate_count",
                "exact_duplicate_occurrence_count", "alternative_reference_count",
            ):
                if getattr(record, name) != getattr(record.candidate_set, name):
                    _issue(issues, f"result.{name}", CandidateSetValidationCode.COUNT_MISMATCH, "result/set mapping mismatch")
    expected_state_flags = {
        "zero_candidates_preserved": record.status is CandidateSetStatus.ZERO_CANDIDATES,
        "one_candidate_preserved_without_selection": record.status is CandidateSetStatus.ONE_CANDIDATE,
        "multiple_candidates_preserved_independently": record.status is CandidateSetStatus.MULTIPLE_CANDIDATES,
    }
    for name, expected in expected_state_flags.items():
        _exact_bool(getattr(record, name), expected, f"result.{name}", issues)
    for name in (
        "deterministic_ordering_verified", "exact_duplicate_detection_verified",
        "shared_ancestry_preserved", "candidate_specific_boundaries_preserved",
    ):
        _exact_bool(getattr(record, name), record.status is not CandidateSetStatus.SET_REJECTED, f"result.{name}", issues)
    for name, code in (
        ("candidates_ranked", CandidateSetValidationCode.RANKING_PROHIBITED),
        ("confidence_scores_created", CandidateSetValidationCode.CONFIDENCE_SCORING_PROHIBITED),
        ("preferred_candidate_created", CandidateSetValidationCode.PREFERENCE_PROHIBITED),
        ("winner_selected", CandidateSetValidationCode.SELECTION_PROHIBITED),
        ("nearest_candidate_selected", CandidateSetValidationCode.SELECTION_PROHIBITED),
        ("tie_breaking_performed", CandidateSetValidationCode.TIE_BREAKING_PROHIBITED),
        ("ambiguity_resolved", CandidateSetValidationCode.AMBIGUITY_RESOLUTION_PROHIBITED),
        ("ambiguous_meaning_state_created", CandidateSetValidationCode.AMBIGUOUS_STATE_PROHIBITED),
        ("gate_progression_created", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("truth_determined", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("evidence_validated", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("permission_granted", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("route_created", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("action_performed", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("memory_accessed", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("rendered", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("delivered", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("filesystem_read_performed", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("filesystem_write_performed", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("network_access_performed", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("external_resource_loaded", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("language_model_used", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("embedding_used", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
        ("semantic_similarity_used", CandidateSetValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED),
    ):
        _exact_bool(getattr(record, name), False, f"result.{name}", issues, code)
    if record.schema_version != SLICE39E_SCHEMA_VERSION:
        _issue(issues, "result.schema_version", CandidateSetValidationCode.INVALID_VERSION, "canonical schema version required")
    if record.result_id != expected_result_id(record):
        _issue(issues, "result.result_id", CandidateSetValidationCode.IDENTITY_MISMATCH, "deterministic result identity mismatch")
    return _report(issues)


def assert_valid_candidate_set(record: Any) -> None:
    report = validate_candidate_set(record)
    if not report.ok:
        raise CandidateSetValidationError(report)


def assert_valid_preservation_result(record: Any) -> None:
    report = validate_preservation_result(record)
    if not report.ok:
        raise CandidateSetValidationError(report)


__all__ = (
    "assert_valid_candidate_set",
    "assert_valid_preservation_result",
    "validate_alternative_reference",
    "validate_candidate_set",
    "validate_duplicate_group",
    "validate_member",
    "validate_preservation_result",
    "validate_profile",
    "validate_shared_ancestry",
)
