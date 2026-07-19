"""Strict fail-closed validation for Slice 40B gate-governance records."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
import re
from typing import Any, Iterable

from ..authority import PERMANENT_GATE_CORE_BOUNDARIES
from ..identity import (
    CANDIDATE_INPUT_REFERENCE_SCHEMA_ID,
    GATE_IDENTITY_SCHEMA_ID,
    GATE_PROFILE_SCHEMA_ID,
    LIMITATION_REFERENCE_SCHEMA_ID,
    PROVENANCE_REFERENCE_SCHEMA_ID,
    REASON_GROUND_SCHEMA_ID,
    REQUIREMENT_REFERENCE_SCHEMA_ID,
    REVIEW_RECORD_SCHEMA_ID,
    SCHEMA_VERSION as CORE_SCHEMA_VERSION,
    SPEC_ID,
    SPEC_VERSION,
    TRACE_REFERENCE_SCHEMA_ID,
)
from ..schema import (
    GateCandidateInputReference,
    GateEvaluationState,
    GateLimitationReference,
    GateProvenanceReference,
    GateReasonGround,
    GateRequirementReference,
    GateTraceReference,
    VerbalCognitionGateFamily,
    VerbalCognitionGateIdentity,
    VerbalCognitionGateProfileIdentity,
    VerbalCognitionGateReviewRecord,
)
from .canonical import (
    GateCanonicalizationError,
    canonical_field_order,
    canonicalize_field_pairs,
)
from .identity import (
    expected_bundle_digest,
    expected_bundle_id,
    expected_candidate_input_reference_id,
    expected_gate_identity_id,
    expected_gate_profile_id,
    expected_lifecycle_record_id,
    expected_lifecycle_transition_id,
    expected_limitation_reference_id,
    expected_provenance_reference_id,
    expected_reason_ground_id,
    expected_requirement_reference_id,
    expected_review_record_id,
    expected_trace_reference_id,
    expected_version_custody_id,
)
from .rules import lifecycle_transition_allowed
from .schema import (
    CANONICAL_FIELD_ORDER_VERSION,
    DIGEST_ALGORITHM,
    SLICE40B_SCHEMA_VERSION,
    SUPPORTED_GATE_PROFILE_VERSIONS,
    SUPPORTED_GATE_VERSIONS,
    GateGovernanceBundle,
    GateLifecycleRecord,
    GateLifecycleStage,
    GateLifecycleTransitionKind,
    GateLifecycleTransitionRecord,
    GateValidationCode,
    GateValidationError,
    GateValidationIssue,
    GateValidationReport,
    GateVersionCustody,
)


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+\-]*$")
_SEMVER = re.compile(r"^v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_VERSION_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+\-]*$")


def _issue(path: str, code: GateValidationCode, detail: str) -> GateValidationIssue:
    return GateValidationIssue(path=path, code=code, detail=detail)


def _report(issues: Iterable[GateValidationIssue]) -> GateValidationReport:
    return GateValidationReport(
        issues=tuple(
            sorted(
                issues,
                key=lambda item: (item.path, item.code.value, item.detail),
            )
        )
    )


def _type_issue(path: str, expected: type[Any], value: Any) -> GateValidationIssue:
    return _issue(
        path,
        GateValidationCode.TYPE_MISMATCH,
        f"expected {expected.__name__}, received {type(value).__name__}",
    )


def _text_issues(
    value: Any,
    path: str,
    *,
    identifier: bool = False,
    version: bool = False,
    sha256: bool = False,
    allow_empty: bool = False,
) -> list[GateValidationIssue]:
    issues: list[GateValidationIssue] = []
    if type(value) is not str:
        return [_type_issue(path, str, value)]
    if not value:
        if allow_empty:
            return issues
        return [
            _issue(
                path,
                GateValidationCode.REQUIRED_VALUE_MISSING,
                "non-empty text is required",
            )
        ]
    if value != value.strip() or any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        issues.append(
            _issue(
                path,
                GateValidationCode.INVALID_TEXT,
                "leading, trailing, or control characters are prohibited",
            )
        )
    if not value.isascii():
        issues.append(
            _issue(
                path,
                GateValidationCode.INVALID_TEXT,
                "governance identifiers and versions must be ASCII",
            )
        )
    if len(value) > 512:
        issues.append(
            _issue(path, GateValidationCode.INVALID_TEXT, "value exceeds 512 characters")
        )
    if identifier and not _IDENTIFIER.fullmatch(value):
        issues.append(
            _issue(path, GateValidationCode.INVALID_IDENTIFIER, "invalid identifier syntax")
        )
    if version and not _SEMVER.fullmatch(value):
        issues.append(
            _issue(path, GateValidationCode.INVALID_VERSION, "expected vMAJOR.MINOR.PATCH")
        )
    if sha256 and not _SHA256.fullmatch(value):
        issues.append(
            _issue(path, GateValidationCode.INVALID_SHA256, "expected lower-case SHA-256")
        )
    return issues


def _enum_issues(value: Any, enum_type: type[Enum], path: str) -> list[GateValidationIssue]:
    if not isinstance(value, enum_type):
        return [
            _issue(
                path,
                GateValidationCode.INVALID_ENUM,
                f"expected {enum_type.__name__}",
            )
        ]
    return []


def _tuple_text_issues(
    value: Any,
    path: str,
    *,
    required: bool,
    identifiers: bool = True,
) -> list[GateValidationIssue]:
    issues: list[GateValidationIssue] = []
    if type(value) is not tuple:
        return [_type_issue(path, tuple, value)]
    if required and not value:
        issues.append(
            _issue(path, GateValidationCode.REQUIRED_VALUE_MISSING, "tuple must not be empty")
        )
    seen: set[str] = set()
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        issues.extend(
            _text_issues(item, item_path, identifier=identifiers)
        )
        if isinstance(item, str):
            if item in seen:
                issues.append(
                    _issue(
                        item_path,
                        GateValidationCode.DUPLICATE_TUPLE_VALUE,
                        f"duplicate value {item!r}",
                    )
                )
            seen.add(item)
    return issues


def _version_pair_issues(
    value: Any,
    path: str,
    *,
    required: bool,
) -> list[GateValidationIssue]:
    issues: list[GateValidationIssue] = []
    if type(value) is not tuple:
        return [_type_issue(path, tuple, value)]
    if required and not value:
        issues.append(
            _issue(path, GateValidationCode.REQUIRED_VALUE_MISSING, "version pairs required")
        )
    seen: set[str] = set()
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if type(item) is not tuple or len(item) != 2:
            issues.append(
                _issue(
                    item_path,
                    GateValidationCode.INVALID_TUPLE,
                    "expected (authority_or_schema_id, version) pair",
                )
            )
            continue
        key, version = item
        issues.extend(_text_issues(key, f"{item_path}[0]", identifier=True))
        issues.extend(_text_issues(version, f"{item_path}[1]"))
        if isinstance(version, str) and version and not _VERSION_TOKEN.fullmatch(version):
            issues.append(
                _issue(
                    f"{item_path}[1]",
                    GateValidationCode.INVALID_VERSION,
                    "invalid version token",
                )
            )
        if isinstance(key, str):
            if key in seen:
                issues.append(
                    _issue(
                        f"{item_path}[0]",
                        GateValidationCode.DUPLICATE_TUPLE_VALUE,
                        f"duplicate version key {key!r}",
                    )
                )
            seen.add(key)
    return issues


def _exact(value: Any, expected: Any, path: str, code: GateValidationCode) -> list[GateValidationIssue]:
    if value != expected:
        return [_issue(path, code, f"expected {expected!r}, received {value!r}")]
    return []


def _false_flags(record: Any, names: tuple[str, ...], path: str) -> list[GateValidationIssue]:
    issues: list[GateValidationIssue] = []
    for name in names:
        value = getattr(record, name)
        if type(value) is not bool:
            issues.append(_type_issue(f"{path}.{name}", bool, value))
        elif value:
            code = (
                GateValidationCode.NONDETERMINISTIC_INPUT_PROHIBITED
                if name in {
                    "timestamps_in_identity",
                    "randomness_in_identity",
                    "process_identity_in_identity",
                    "filesystem_state_in_identity",
                    "environment_state_in_identity",
                    "hash_table_order_in_identity",
                }
                else GateValidationCode.GATE_EVALUATION_PROHIBITED
                if "evaluation" in name
                else GateValidationCode.GATE_OUTCOME_PROHIBITED
                if "outcome" in name or "disposition" in name
                else GateValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
            )
            issues.append(
                _issue(f"{path}.{name}", code, "must remain false in Slice 40B")
            )
    return issues


def validate_field_pairs(
    record_type: type[Any],
    field_pairs: Iterable[tuple[str, Any]],
) -> GateValidationReport:
    issues: list[GateValidationIssue] = []
    observed = tuple(field_pairs)
    expected = canonical_field_order(record_type)
    names: list[str] = []
    for index, pair in enumerate(observed):
        if type(pair) is not tuple or len(pair) != 2 or type(pair[0]) is not str:
            issues.append(
                _issue(
                    f"field_pairs[{index}]",
                    GateValidationCode.INVALID_TUPLE,
                    "field pair must be a (str, value) tuple",
                )
            )
            continue
        names.append(pair[0])
    duplicates = {name for name in names if names.count(name) > 1}
    for name in sorted(duplicates):
        issues.append(_issue(name, GateValidationCode.DUPLICATE_FIELD, "duplicate field"))
    for name in sorted(set(names).difference(expected)):
        issues.append(_issue(name, GateValidationCode.UNKNOWN_FIELD, "unknown field"))
    for name in expected:
        if name not in names:
            issues.append(_issue(name, GateValidationCode.MISSING_FIELD, "field missing"))
    if not issues:
        try:
            canonical = canonicalize_field_pairs(record_type, observed)
        except GateCanonicalizationError as error:
            issues.append(
                _issue("field_pairs", GateValidationCode.FIELD_ORDER_MISMATCH, str(error))
            )
        else:
            if tuple(canonical) != expected:
                issues.append(
                    _issue(
                        "field_pairs",
                        GateValidationCode.FIELD_ORDER_MISMATCH,
                        "canonical field order mismatch",
                    )
                )
    return _report(issues)


def validate_gate_identity(record: Any) -> GateValidationReport:
    if not isinstance(record, VerbalCognitionGateIdentity):
        return _report((_type_issue("identity", VerbalCognitionGateIdentity, record),))
    issues: list[GateValidationIssue] = []
    issues.extend(_text_issues(record.gate_id, "identity.gate_id", identifier=True))
    issues.extend(_text_issues(record.gate_key, "identity.gate_key", identifier=True))
    issues.extend(_text_issues(record.gate_version, "identity.gate_version", version=True))
    if record.gate_version not in SUPPORTED_GATE_VERSIONS:
        issues.append(
            _issue(
                "identity.gate_version",
                GateValidationCode.UNKNOWN_VERSION,
                "gate version is not admitted by Slice 40B",
            )
        )
    issues.extend(_enum_issues(record.gate_family, VerbalCognitionGateFamily, "identity.gate_family"))
    issues.extend(_text_issues(record.gate_profile_ref, "identity.gate_profile_ref", identifier=True))
    issues.extend(_exact(record.spec_id, SPEC_ID, "identity.spec_id", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    issues.extend(_exact(record.spec_version, SPEC_VERSION, "identity.spec_version", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    issues.extend(_exact(record.schema_version, CORE_SCHEMA_VERSION, "identity.schema_version", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    issues.extend(_exact(record.identity_schema_id, GATE_IDENTITY_SCHEMA_ID, "identity.identity_schema_id", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    if record.gate_id != expected_gate_identity_id(record):
        issues.append(_issue("identity.gate_id", GateValidationCode.IDENTITY_MISMATCH, "deterministic gate identity mismatch"))
    return _report(issues)


def validate_gate_profile(record: Any) -> GateValidationReport:
    if not isinstance(record, VerbalCognitionGateProfileIdentity):
        return _report((_type_issue("profile", VerbalCognitionGateProfileIdentity, record),))
    issues: list[GateValidationIssue] = []
    issues.extend(_text_issues(record.profile_id, "profile.profile_id", identifier=True))
    issues.extend(_text_issues(record.profile_key, "profile.profile_key", identifier=True))
    issues.extend(_text_issues(record.profile_version, "profile.profile_version", version=True))
    if record.profile_version not in SUPPORTED_GATE_PROFILE_VERSIONS:
        issues.append(
            _issue(
                "profile.profile_version",
                GateValidationCode.UNKNOWN_VERSION,
                "gate profile version is not admitted by Slice 40B",
            )
        )
    issues.extend(_enum_issues(record.gate_family, VerbalCognitionGateFamily, "profile.gate_family"))
    issues.extend(_tuple_text_issues(record.governing_authority_refs, "profile.governing_authority_refs", required=True))
    issues.extend(_tuple_text_issues(record.required_schema_refs, "profile.required_schema_refs", required=True))
    if type(record.exact_profile_only) is not bool:
        issues.append(_type_issue("profile.exact_profile_only", bool, record.exact_profile_only))
    elif not record.exact_profile_only:
        issues.append(
            _issue("profile.exact_profile_only", GateValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED, "profile matching must remain exact")
        )
    issues.extend(_exact(record.schema_version, CORE_SCHEMA_VERSION, "profile.schema_version", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    issues.extend(_exact(record.profile_schema_id, GATE_PROFILE_SCHEMA_ID, "profile.profile_schema_id", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    if record.profile_id != expected_gate_profile_id(record):
        issues.append(_issue("profile.profile_id", GateValidationCode.IDENTITY_MISMATCH, "deterministic profile identity mismatch"))
    return _report(issues)


def validate_candidate_input(record: Any) -> GateValidationReport:
    if not isinstance(record, GateCandidateInputReference):
        return _report((_type_issue("candidate_input", GateCandidateInputReference, record),))
    issues: list[GateValidationIssue] = []
    required_ids = (
        "candidate_input_ref_id", "candidate_meaning_id", "candidate_state_id",
        "candidate_lineage_id", "candidate_identity_ref", "candidate_content_ref",
        "candidate_provenance_ref", "construction_receipt_ref",
    )
    for name in required_ids:
        issues.extend(_text_issues(getattr(record, name), f"candidate_input.{name}", identifier=True))
    for name in (
        "manifest_candidate_record_ref", "manifest_companion_ref",
        "construction_trace_ref", "limitation_reference_ref",
    ):
        value = getattr(record, name)
        if value is not None:
            issues.extend(_text_issues(value, f"candidate_input.{name}", identifier=True))
    issues.extend(_tuple_text_issues(record.alternative_relationship_refs, "candidate_input.alternative_relationship_refs", required=False))
    if record.candidate_only is not True:
        issues.append(_issue("candidate_input.candidate_only", GateValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED, "must remain candidate-only"))
    issues.extend(_false_flags(record, ("accepted_candidate", "selected_candidate"), "candidate_input"))
    issues.extend(_exact(record.schema_version, CORE_SCHEMA_VERSION, "candidate_input.schema_version", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    issues.extend(_exact(record.candidate_input_schema_id, CANDIDATE_INPUT_REFERENCE_SCHEMA_ID, "candidate_input.candidate_input_schema_id", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    if record.candidate_input_ref_id != expected_candidate_input_reference_id(record):
        issues.append(_issue("candidate_input.candidate_input_ref_id", GateValidationCode.IDENTITY_MISMATCH, "deterministic candidate input identity mismatch"))
    return _report(issues)


def validate_requirement(record: Any) -> GateValidationReport:
    if not isinstance(record, GateRequirementReference):
        return _report((_type_issue("requirement", GateRequirementReference, record),))
    issues: list[GateValidationIssue] = []
    for name in ("requirement_reference_id", "requirement_key", "candidate_input_ref"):
        issues.extend(_text_issues(getattr(record, name), f"requirement.{name}", identifier=True))
    issues.extend(_text_issues(record.requirement_version, "requirement.requirement_version", version=True))
    issues.extend(_enum_issues(record.gate_family, VerbalCognitionGateFamily, "requirement.gate_family"))
    issues.extend(_tuple_text_issues(record.subject_record_refs, "requirement.subject_record_refs", required=True))
    issues.extend(_tuple_text_issues(record.required_authority_refs, "requirement.required_authority_refs", required=True))
    issues.extend(_tuple_text_issues(record.required_record_refs, "requirement.required_record_refs", required=False))
    issues.extend(_tuple_text_issues(record.required_relation_refs, "requirement.required_relation_refs", required=False))
    issues.extend(_tuple_text_issues(record.limitation_refs, "requirement.limitation_refs", required=False))
    issues.extend(_false_flags(record, ("requirement_satisfied", "requirement_failed"), "requirement"))
    issues.extend(_exact(record.schema_version, CORE_SCHEMA_VERSION, "requirement.schema_version", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    issues.extend(_exact(record.requirement_schema_id, REQUIREMENT_REFERENCE_SCHEMA_ID, "requirement.requirement_schema_id", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    if record.requirement_reference_id != expected_requirement_reference_id(record):
        issues.append(_issue("requirement.requirement_reference_id", GateValidationCode.IDENTITY_MISMATCH, "deterministic requirement identity mismatch"))
    return _report(issues)


def validate_reason_ground(record: Any) -> GateValidationReport:
    if not isinstance(record, GateReasonGround):
        return _report((_type_issue("reason_ground", GateReasonGround, record),))
    issues: list[GateValidationIssue] = []
    for name in ("reason_ground_id", "reason_key", "candidate_input_ref"):
        issues.extend(_text_issues(getattr(record, name), f"reason_ground.{name}", identifier=True))
    issues.extend(_enum_issues(record.gate_family, VerbalCognitionGateFamily, "reason_ground.gate_family"))
    issues.extend(_tuple_text_issues(record.requirement_reference_ids, "reason_ground.requirement_reference_ids", required=True))
    for name in (
        "supporting_record_refs", "conflicting_record_refs", "missing_record_refs",
        "unknown_record_refs", "authority_refs", "limitation_refs",
    ):
        issues.extend(_tuple_text_issues(getattr(record, name), f"reason_ground.{name}", required=name == "authority_refs"))
    if not (
        record.supporting_record_refs
        or record.conflicting_record_refs
        or record.missing_record_refs
        or record.unknown_record_refs
    ):
        issues.append(_issue("reason_ground", GateValidationCode.REQUIRED_VALUE_MISSING, "at least one explicit reason-ground record is required"))
    issues.extend(_false_flags(record, ("reason_validated", "outcome_created"), "reason_ground"))
    issues.extend(_exact(record.schema_version, CORE_SCHEMA_VERSION, "reason_ground.schema_version", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    issues.extend(_exact(record.reason_ground_schema_id, REASON_GROUND_SCHEMA_ID, "reason_ground.reason_ground_schema_id", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    if record.reason_ground_id != expected_reason_ground_id(record):
        issues.append(_issue("reason_ground.reason_ground_id", GateValidationCode.IDENTITY_MISMATCH, "deterministic reason-ground identity mismatch"))
    return _report(issues)


def validate_trace_reference(record: Any) -> GateValidationReport:
    if not isinstance(record, GateTraceReference):
        return _report((_type_issue("trace", GateTraceReference, record),))
    issues: list[GateValidationIssue] = []
    issues.extend(_text_issues(record.trace_reference_id, "trace.trace_reference_id", identifier=True))
    issues.extend(_text_issues(record.candidate_input_ref, "trace.candidate_input_ref", identifier=True))
    for name in (
        "source_span_refs", "candidate_trace_refs", "construction_trace_refs",
        "structural_trace_refs", "concept_sense_trace_refs",
        "predicate_role_frame_trace_refs", "alternative_relationship_refs",
        "predecessor_receipt_refs",
    ):
        issues.extend(
            _tuple_text_issues(
                getattr(record, name),
                f"trace.{name}",
                required=name in ("source_span_refs", "candidate_trace_refs", "predecessor_receipt_refs"),
            )
        )
    issues.extend(_false_flags(record, ("trace_validated",), "trace"))
    issues.extend(_exact(record.schema_version, CORE_SCHEMA_VERSION, "trace.schema_version", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    issues.extend(_exact(record.trace_schema_id, TRACE_REFERENCE_SCHEMA_ID, "trace.trace_schema_id", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    if record.trace_reference_id != expected_trace_reference_id(record):
        issues.append(_issue("trace.trace_reference_id", GateValidationCode.IDENTITY_MISMATCH, "deterministic trace identity mismatch"))
    return _report(issues)


def validate_provenance_reference(record: Any) -> GateValidationReport:
    if not isinstance(record, GateProvenanceReference):
        return _report((_type_issue("provenance", GateProvenanceReference, record),))
    issues: list[GateValidationIssue] = []
    for name in (
        "provenance_reference_id", "candidate_input_ref", "source_event_id",
        "candidate_provenance_ref", "gate_profile_ref",
    ):
        issues.extend(_text_issues(getattr(record, name), f"provenance.{name}", identifier=True))
    issues.extend(_text_issues(record.source_sha256, "provenance.source_sha256", sha256=True))
    issues.extend(_tuple_text_issues(record.governing_document_refs, "provenance.governing_document_refs", required=True))
    issues.extend(_version_pair_issues(record.authority_version_refs, "provenance.authority_version_refs", required=True))
    issues.extend(_version_pair_issues(record.schema_version_refs, "provenance.schema_version_refs", required=True))
    issues.extend(_tuple_text_issues(record.external_resource_refs, "provenance.external_resource_refs", required=False))
    issues.extend(_false_flags(record, ("provenance_validated", "external_resource_loaded"), "provenance"))
    issues.extend(_exact(record.schema_version, CORE_SCHEMA_VERSION, "provenance.schema_version", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    issues.extend(_exact(record.provenance_schema_id, PROVENANCE_REFERENCE_SCHEMA_ID, "provenance.provenance_schema_id", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    if record.provenance_reference_id != expected_provenance_reference_id(record):
        issues.append(_issue("provenance.provenance_reference_id", GateValidationCode.IDENTITY_MISMATCH, "deterministic provenance identity mismatch"))
    return _report(issues)


def validate_limitation_reference(record: Any) -> GateValidationReport:
    if not isinstance(record, GateLimitationReference):
        return _report((_type_issue("limitation", GateLimitationReference, record),))
    issues: list[GateValidationIssue] = []
    for name in ("limitation_reference_id", "candidate_input_ref", "limitation_key"):
        issues.extend(_text_issues(getattr(record, name), f"limitation.{name}", identifier=True))
    issues.extend(_tuple_text_issues(record.reason_refs, "limitation.reason_refs", required=True))
    issues.extend(_tuple_text_issues(record.affected_requirement_refs, "limitation.affected_requirement_refs", required=False))
    issues.extend(_tuple_text_issues(record.later_authority_refs, "limitation.later_authority_refs", required=True))
    issues.extend(_false_flags(record, ("clarification_created", "blocked_progression_created"), "limitation"))
    issues.extend(_exact(record.schema_version, CORE_SCHEMA_VERSION, "limitation.schema_version", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    issues.extend(_exact(record.limitation_schema_id, LIMITATION_REFERENCE_SCHEMA_ID, "limitation.limitation_schema_id", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    if record.limitation_reference_id != expected_limitation_reference_id(record):
        issues.append(_issue("limitation.limitation_reference_id", GateValidationCode.IDENTITY_MISMATCH, "deterministic limitation identity mismatch"))
    return _report(issues)


_REVIEW_FALSE_FLAGS = (
    "runtime_evaluator_installed",
    "identity_calculated",
    "validation_performed",
    "lifecycle_transition_performed",
    "gate_evaluation_performed",
    "expectancy_result_created",
    "congruity_result_created",
    "connectedness_result_created",
    "recoverable_purpose_result_created",
    "gate_pass_created",
    "gate_failure_created",
    "gate_outcome_created",
    "ambiguity_disposition_created",
    "clarification_required_created",
    "unsupported_disposition_created",
    "refusal_relevant_disposition_created",
    "held_disposition_created",
    "blocked_progression_created",
    "positive_selection_review_disposition_created",
    "candidate_accepted",
    "candidate_rejected",
    "candidate_clarified",
    "selected_meaning_created",
    "truth_determined",
    "evidence_validated",
    "permission_granted",
    "execution_authorized",
    "capability_availability_created",
    "route_created",
    "tool_invoked",
    "action_performed",
    "memory_accessed",
    "rendered",
    "delivered",
    "external_resource_loaded",
    "language_model_used",
    "embedding_used",
    "vector_used",
    "rag_used",
    "semantic_similarity_used",
)


def validate_review_record(record: Any) -> GateValidationReport:
    if not isinstance(record, VerbalCognitionGateReviewRecord):
        return _report((_type_issue("review", VerbalCognitionGateReviewRecord, record),))
    issues: list[GateValidationIssue] = []
    issues.extend(_text_issues(record.review_record_id, "review.review_record_id", identifier=True))
    issues.extend(validate_gate_identity(record.identity).issues)
    issues.extend(validate_gate_profile(record.profile).issues)
    issues.extend(validate_candidate_input(record.candidate_input).issues)
    if type(record.requirement_references) is not tuple or not record.requirement_references:
        issues.append(_issue("review.requirement_references", GateValidationCode.REQUIRED_VALUE_MISSING, "at least one requirement is required"))
    else:
        for item in record.requirement_references:
            issues.extend(validate_requirement(item).issues)
    if type(record.reason_grounds) is not tuple or not record.reason_grounds:
        issues.append(_issue("review.reason_grounds", GateValidationCode.REQUIRED_VALUE_MISSING, "at least one reason ground is required"))
    else:
        for item in record.reason_grounds:
            issues.extend(validate_reason_ground(item).issues)
    issues.extend(_enum_issues(record.evaluation_state, GateEvaluationState, "review.evaluation_state"))
    if type(record.trace_references) is not tuple or not record.trace_references:
        issues.append(_issue("review.trace_references", GateValidationCode.REQUIRED_VALUE_MISSING, "at least one trace is required"))
    else:
        for item in record.trace_references:
            issues.extend(validate_trace_reference(item).issues)
    issues.extend(validate_provenance_reference(record.provenance_reference).issues)
    if type(record.limitation_references) is not tuple:
        issues.append(_type_issue("review.limitation_references", tuple, record.limitation_references))
    else:
        for item in record.limitation_references:
            issues.extend(validate_limitation_reference(item).issues)

    if record.identity.gate_family is not record.profile.gate_family:
        issues.append(_issue("review.profile.gate_family", GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "identity and profile gate families differ"))
    if record.identity.gate_profile_ref != record.profile.profile_id:
        issues.append(_issue("review.identity.gate_profile_ref", GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "identity does not reference exact profile"))
    candidate_ref = record.candidate_input.candidate_input_ref_id
    requirement_ids = {item.requirement_reference_id for item in record.requirement_references}
    if len(requirement_ids) != len(record.requirement_references):
        issues.append(_issue("review.requirement_references", GateValidationCode.DUPLICATE_RECORD_ID, "duplicate requirement identity"))
    for index, item in enumerate(record.requirement_references):
        if item.candidate_input_ref != candidate_ref:
            issues.append(_issue(f"review.requirement_references[{index}].candidate_input_ref", GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "requirement candidate reference mismatch"))
        if item.gate_family is not record.identity.gate_family:
            issues.append(_issue(f"review.requirement_references[{index}].gate_family", GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "requirement gate family mismatch"))
    reason_ids = {item.reason_ground_id for item in record.reason_grounds}
    if len(reason_ids) != len(record.reason_grounds):
        issues.append(_issue("review.reason_grounds", GateValidationCode.DUPLICATE_RECORD_ID, "duplicate reason-ground identity"))
    for index, item in enumerate(record.reason_grounds):
        if item.candidate_input_ref != candidate_ref:
            issues.append(_issue(f"review.reason_grounds[{index}].candidate_input_ref", GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "reason-ground candidate reference mismatch"))
        if item.gate_family is not record.identity.gate_family:
            issues.append(_issue(f"review.reason_grounds[{index}].gate_family", GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "reason-ground gate family mismatch"))
        for ref in item.requirement_reference_ids:
            if ref not in requirement_ids:
                issues.append(_issue(f"review.reason_grounds[{index}].requirement_reference_ids", GateValidationCode.REFERENCE_NOT_FOUND, f"unknown requirement {ref}"))
    trace_ids = {item.trace_reference_id for item in record.trace_references}
    if len(trace_ids) != len(record.trace_references):
        issues.append(_issue("review.trace_references", GateValidationCode.DUPLICATE_RECORD_ID, "duplicate trace identity"))
    for index, item in enumerate(record.trace_references):
        if item.candidate_input_ref != candidate_ref:
            issues.append(_issue(f"review.trace_references[{index}].candidate_input_ref", GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "trace candidate reference mismatch"))
    provenance = record.provenance_reference
    if provenance.candidate_input_ref != candidate_ref:
        issues.append(_issue("review.provenance_reference.candidate_input_ref", GateValidationCode.PROVENANCE_MISMATCH, "provenance candidate reference mismatch"))
    if provenance.gate_profile_ref != record.profile.profile_id:
        issues.append(_issue("review.provenance_reference.gate_profile_ref", GateValidationCode.PROVENANCE_MISMATCH, "provenance profile reference mismatch"))
    limitation_ids = {item.limitation_reference_id for item in record.limitation_references}
    if len(limitation_ids) != len(record.limitation_references):
        issues.append(_issue("review.limitation_references", GateValidationCode.DUPLICATE_RECORD_ID, "duplicate limitation identity"))
    for index, item in enumerate(record.limitation_references):
        if item.candidate_input_ref != candidate_ref:
            issues.append(_issue(f"review.limitation_references[{index}].candidate_input_ref", GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "limitation candidate reference mismatch"))
        for ref in item.affected_requirement_refs:
            if ref not in requirement_ids:
                issues.append(_issue(f"review.limitation_references[{index}].affected_requirement_refs", GateValidationCode.REFERENCE_NOT_FOUND, f"unknown requirement {ref}"))

    if record.permanent_boundaries != PERMANENT_GATE_CORE_BOUNDARIES:
        issues.append(_issue("review.permanent_boundaries", GateValidationCode.SCHEMA_VERSION_MISMATCH, "permanent boundary set changed"))
    if record.schema_only is not True or record.versioned_companion is not True:
        issues.append(_issue("review", GateValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED, "schema-only versioned-companion boundary must remain true"))
    issues.extend(_false_flags(record, _REVIEW_FALSE_FLAGS, "review"))
    issues.extend(_exact(record.schema_version, CORE_SCHEMA_VERSION, "review.schema_version", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    issues.extend(_exact(record.review_record_schema_id, REVIEW_RECORD_SCHEMA_ID, "review.review_record_schema_id", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    if record.review_record_id != expected_review_record_id(record):
        issues.append(_issue("review.review_record_id", GateValidationCode.IDENTITY_MISMATCH, "deterministic review identity mismatch"))
    return _report(issues)


_CUSTODY_FALSE_FLAGS = (
    "timestamps_in_identity",
    "randomness_in_identity",
    "process_identity_in_identity",
    "filesystem_state_in_identity",
    "environment_state_in_identity",
    "hash_table_order_in_identity",
    "runtime_evaluator_authorized",
    "gate_evaluation_authorized",
    "gate_outcome_authorized",
    "selected_meaning_authorized",
    "route_authorized",
    "tool_authorized",
    "action_authorized",
    "memory_authorized",
    "rendering_authorized",
    "delivery_authorized",
)


def validate_version_custody(
    record: Any,
    *,
    review_record: VerbalCognitionGateReviewRecord | None = None,
) -> GateValidationReport:
    if not isinstance(record, GateVersionCustody):
        return _report((_type_issue("version_custody", GateVersionCustody, record),))
    issues: list[GateValidationIssue] = []
    for name in ("custody_id", "review_record_id", "gate_id", "gate_profile_id"):
        issues.extend(_text_issues(getattr(record, name), f"version_custody.{name}", identifier=True))
    issues.extend(_text_issues(record.gate_version, "version_custody.gate_version", version=True))
    issues.extend(_text_issues(record.gate_profile_version, "version_custody.gate_profile_version", version=True))
    if record.gate_version not in SUPPORTED_GATE_VERSIONS:
        issues.append(_issue("version_custody.gate_version", GateValidationCode.UNKNOWN_VERSION, "unknown gate version"))
    if record.gate_profile_version not in SUPPORTED_GATE_PROFILE_VERSIONS:
        issues.append(_issue("version_custody.gate_profile_version", GateValidationCode.UNKNOWN_VERSION, "unknown gate profile version"))
    issues.extend(_enum_issues(record.gate_family, VerbalCognitionGateFamily, "version_custody.gate_family"))
    exact_values = (
        ("core_schema_version", CORE_SCHEMA_VERSION),
        ("core_spec_version", SPEC_VERSION),
        ("identity_schema_id", GATE_IDENTITY_SCHEMA_ID),
        ("profile_schema_id", GATE_PROFILE_SCHEMA_ID),
        ("candidate_input_schema_id", CANDIDATE_INPUT_REFERENCE_SCHEMA_ID),
        ("requirement_schema_id", REQUIREMENT_REFERENCE_SCHEMA_ID),
        ("reason_ground_schema_id", REASON_GROUND_SCHEMA_ID),
        ("trace_schema_id", TRACE_REFERENCE_SCHEMA_ID),
        ("provenance_schema_id", PROVENANCE_REFERENCE_SCHEMA_ID),
        ("limitation_schema_id", LIMITATION_REFERENCE_SCHEMA_ID),
        ("review_record_schema_id", REVIEW_RECORD_SCHEMA_ID),
        ("canonical_field_order_version", CANONICAL_FIELD_ORDER_VERSION),
        ("digest_algorithm", DIGEST_ALGORITHM),
        ("governance_schema_version", SLICE40B_SCHEMA_VERSION),
    )
    for name, expected in exact_values:
        issues.extend(_exact(getattr(record, name), expected, f"version_custody.{name}", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    issues.extend(_version_pair_issues(record.governing_authority_versions, "version_custody.governing_authority_versions", required=True))
    issues.extend(_version_pair_issues(record.predecessor_schema_versions, "version_custody.predecessor_schema_versions", required=True))
    if type(record.non_llm_provenance) is not bool:
        issues.append(_type_issue("version_custody.non_llm_provenance", bool, record.non_llm_provenance))
    elif not record.non_llm_provenance:
        issues.append(_issue("version_custody.non_llm_provenance", GateValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED, "non-LLM provenance must be explicit"))
    issues.extend(_false_flags(record, _CUSTODY_FALSE_FLAGS, "version_custody"))
    if review_record is not None:
        cross = (
            ("review_record_id", review_record.review_record_id),
            ("gate_id", review_record.identity.gate_id),
            ("gate_version", review_record.identity.gate_version),
            ("gate_profile_id", review_record.profile.profile_id),
            ("gate_profile_version", review_record.profile.profile_version),
            ("gate_family", review_record.identity.gate_family),
        )
        for name, expected in cross:
            if getattr(record, name) != expected:
                issues.append(_issue(f"version_custody.{name}", GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, f"must match review record value {expected!r}"))
    if record.custody_id != expected_version_custody_id(record):
        issues.append(_issue("version_custody.custody_id", GateValidationCode.IDENTITY_MISMATCH, "deterministic version custody identity mismatch"))
    return _report(issues)


_LIFECYCLE_FALSE_FLAGS = (
    "gate_evaluation_created",
    "gate_outcome_created",
    "candidate_disposition_created",
    "selected_meaning_created",
    "truth_determined",
    "evidence_validated",
    "permission_granted",
    "execution_authorized",
    "route_created",
    "tool_invoked",
    "action_performed",
    "memory_accessed",
    "rendered",
    "delivered",
    "external_resource_loaded",
)


def validate_lifecycle_record(record: Any) -> GateValidationReport:
    if not isinstance(record, GateLifecycleRecord):
        return _report((_type_issue("lifecycle_record", GateLifecycleRecord, record),))
    issues: list[GateValidationIssue] = []
    for name in (
        "lifecycle_record_id", "review_record_id", "gate_id",
        "gate_profile_id", "candidate_input_ref", "provenance_reference_id",
        "version_custody_ref",
    ):
        issues.extend(_text_issues(getattr(record, name), f"lifecycle_record.{name}", identifier=True))
    issues.extend(_enum_issues(record.stage, GateLifecycleStage, "lifecycle_record.stage"))
    issues.extend(_tuple_text_issues(record.predecessor_lifecycle_record_ids, "lifecycle_record.predecessor_lifecycle_record_ids", required=False))
    issues.extend(_tuple_text_issues(record.reason_refs, "lifecycle_record.reason_refs", required=True))
    if type(record.automatic_progression) is not bool:
        issues.append(_type_issue("lifecycle_record.automatic_progression", bool, record.automatic_progression))
    elif record.automatic_progression:
        issues.append(_issue("lifecycle_record.automatic_progression", GateValidationCode.AUTOMATIC_TRANSITION_PROHIBITED, "lifecycle progression must be explicit"))
    if type(record.validation_performed) is not bool:
        issues.append(_type_issue("lifecycle_record.validation_performed", bool, record.validation_performed))
    if type(record.provenance_validation_performed) is not bool:
        issues.append(_type_issue("lifecycle_record.provenance_validation_performed", bool, record.provenance_validation_performed))
    if record.stage in (GateLifecycleStage.RECORD_VALIDATED, GateLifecycleStage.RECORD_SEALED):
        if record.validation_performed is not True:
            issues.append(_issue("lifecycle_record.validation_performed", GateValidationCode.LIFECYCLE_STAGE_INVALID, "validated and sealed stages require validation custody"))
        if record.provenance_validation_performed is not True:
            issues.append(_issue("lifecycle_record.provenance_validation_performed", GateValidationCode.PROVENANCE_MISMATCH, "validated and sealed stages require provenance validation"))
    elif record.stage is GateLifecycleStage.PROVENANCE_VALIDATED:
        if record.provenance_validation_performed is not True:
            issues.append(_issue("lifecycle_record.provenance_validation_performed", GateValidationCode.PROVENANCE_MISMATCH, "provenance-validated stage requires exact validation"))
        if record.validation_performed:
            issues.append(_issue("lifecycle_record.validation_performed", GateValidationCode.LIFECYCLE_STAGE_INVALID, "full validation cannot precede record-validation stage"))
    elif record.validation_performed or record.provenance_validation_performed:
        issues.append(_issue("lifecycle_record", GateValidationCode.LIFECYCLE_STAGE_INVALID, "stage cannot claim validation already occurred"))
    issues.extend(_false_flags(record, _LIFECYCLE_FALSE_FLAGS, "lifecycle_record"))
    issues.extend(_exact(record.schema_version, SLICE40B_SCHEMA_VERSION, "lifecycle_record.schema_version", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    if record.lifecycle_record_id != expected_lifecycle_record_id(record):
        issues.append(_issue("lifecycle_record.lifecycle_record_id", GateValidationCode.IDENTITY_MISMATCH, "deterministic lifecycle identity mismatch"))
    return _report(issues)


_TRANSITION_FALSE_FLAGS = (
    "gate_evaluation_created",
    "gate_outcome_created",
    "candidate_disposition_created",
    "selected_meaning_created",
    "permission_granted",
    "execution_authorized",
    "route_created",
    "tool_invoked",
    "action_performed",
    "memory_accessed",
    "rendered",
    "delivered",
)


def validate_lifecycle_transition_record(record: Any) -> GateValidationReport:
    if not isinstance(record, GateLifecycleTransitionRecord):
        return _report((_type_issue("lifecycle_transition", GateLifecycleTransitionRecord, record),))
    issues: list[GateValidationIssue] = []
    for name in (
        "transition_id", "review_record_id", "source_lifecycle_record_id",
        "target_lifecycle_record_id", "version_custody_ref",
    ):
        issues.extend(_text_issues(getattr(record, name), f"lifecycle_transition.{name}", identifier=True))
    issues.extend(_enum_issues(record.from_stage, GateLifecycleStage, "lifecycle_transition.from_stage"))
    issues.extend(_enum_issues(record.to_stage, GateLifecycleStage, "lifecycle_transition.to_stage"))
    issues.extend(_enum_issues(record.transition_kind, GateLifecycleTransitionKind, "lifecycle_transition.transition_kind"))
    issues.extend(_tuple_text_issues(record.reason_refs, "lifecycle_transition.reason_refs", required=True))
    issues.extend(_tuple_text_issues(record.predecessor_transition_refs, "lifecycle_transition.predecessor_transition_refs", required=False))
    if type(record.automatic_transition) is not bool:
        issues.append(_type_issue("lifecycle_transition.automatic_transition", bool, record.automatic_transition))
    elif record.automatic_transition:
        issues.append(_issue("lifecycle_transition.automatic_transition", GateValidationCode.AUTOMATIC_TRANSITION_PROHIBITED, "automatic transition prohibited"))
    issues.extend(_false_flags(record, _TRANSITION_FALSE_FLAGS, "lifecycle_transition"))
    issues.extend(_exact(record.schema_version, SLICE40B_SCHEMA_VERSION, "lifecycle_transition.schema_version", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    if record.transition_id != expected_lifecycle_transition_id(record):
        issues.append(_issue("lifecycle_transition.transition_id", GateValidationCode.IDENTITY_MISMATCH, "deterministic transition identity mismatch"))
    return _report(issues)


_BUNDLE_FALSE_FLAGS = (
    "runtime_evaluator_installed",
    "gate_evaluation_performed",
    "gate_outcome_created",
    "candidate_disposition_created",
    "selected_meaning_created",
    "truth_determined",
    "evidence_validated",
    "permission_granted",
    "execution_authorized",
    "route_created",
    "tool_invoked",
    "action_performed",
    "memory_accessed",
    "rendered",
    "delivered",
    "external_resource_loaded",
)


def validate_governance_bundle(record: Any) -> GateValidationReport:
    if not isinstance(record, GateGovernanceBundle):
        return _report((_type_issue("bundle", GateGovernanceBundle, record),))
    issues: list[GateValidationIssue] = []
    issues.extend(_text_issues(record.bundle_id, "bundle.bundle_id", identifier=True))
    issues.extend(validate_review_record(record.review_record).issues)
    issues.extend(validate_version_custody(record.version_custody, review_record=record.review_record).issues)
    if type(record.lifecycle_records) is not tuple or not record.lifecycle_records:
        issues.append(_issue("bundle.lifecycle_records", GateValidationCode.REQUIRED_VALUE_MISSING, "lifecycle records required"))
        lifecycle_records: tuple[GateLifecycleRecord, ...] = ()
    else:
        lifecycle_records = record.lifecycle_records
        for item in lifecycle_records:
            issues.extend(validate_lifecycle_record(item).issues)
    if type(record.lifecycle_transitions) is not tuple:
        issues.append(_type_issue("bundle.lifecycle_transitions", tuple, record.lifecycle_transitions))
        lifecycle_transitions: tuple[GateLifecycleTransitionRecord, ...] = ()
    else:
        lifecycle_transitions = record.lifecycle_transitions
        for item in lifecycle_transitions:
            issues.extend(validate_lifecycle_transition_record(item).issues)

    lifecycle_by_id = {item.lifecycle_record_id: item for item in lifecycle_records}
    if len(lifecycle_by_id) != len(lifecycle_records):
        issues.append(_issue("bundle.lifecycle_records", GateValidationCode.DUPLICATE_LIFECYCLE_RECORD, "duplicate lifecycle identity"))
    transition_by_id = {item.transition_id: item for item in lifecycle_transitions}
    if len(transition_by_id) != len(lifecycle_transitions):
        issues.append(_issue("bundle.lifecycle_transitions", GateValidationCode.DUPLICATE_TRANSITION_ID, "duplicate transition identity"))

    review = record.review_record
    custody = record.version_custody
    for index, item in enumerate(lifecycle_records):
        prefix = f"bundle.lifecycle_records[{index}]"
        expected_pairs = (
            ("review_record_id", review.review_record_id),
            ("gate_id", review.identity.gate_id),
            ("gate_profile_id", review.profile.profile_id),
            ("candidate_input_ref", review.candidate_input.candidate_input_ref_id),
            ("provenance_reference_id", review.provenance_reference.provenance_reference_id),
            ("version_custody_ref", custody.custody_id),
        )
        for name, expected in expected_pairs:
            if getattr(item, name) != expected:
                issues.append(_issue(f"{prefix}.{name}", GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, f"must equal {expected!r}"))
        for predecessor in item.predecessor_lifecycle_record_ids:
            if predecessor not in lifecycle_by_id:
                issues.append(_issue(f"{prefix}.predecessor_lifecycle_record_ids", GateValidationCode.REFERENCE_NOT_FOUND, f"unknown lifecycle predecessor {predecessor}"))

    for index, item in enumerate(lifecycle_transitions):
        prefix = f"bundle.lifecycle_transitions[{index}]"
        source = lifecycle_by_id.get(item.source_lifecycle_record_id)
        target = lifecycle_by_id.get(item.target_lifecycle_record_id)
        if source is None:
            issues.append(_issue(f"{prefix}.source_lifecycle_record_id", GateValidationCode.REFERENCE_NOT_FOUND, "source lifecycle record not found"))
        if target is None:
            issues.append(_issue(f"{prefix}.target_lifecycle_record_id", GateValidationCode.REFERENCE_NOT_FOUND, "target lifecycle record not found"))
        if source is not None and target is not None:
            if item.review_record_id != review.review_record_id:
                issues.append(_issue(f"{prefix}.review_record_id", GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "transition review identity mismatch"))
            if item.from_stage is not source.stage or item.to_stage is not target.stage:
                issues.append(_issue(prefix, GateValidationCode.LIFECYCLE_STAGE_INVALID, "transition stage does not match source and target"))
            if not lifecycle_transition_allowed(source.stage, target.stage, item.transition_kind):
                issues.append(_issue(f"{prefix}.transition_kind", GateValidationCode.LIFECYCLE_TRANSITION_NOT_PERMITTED, "transition is not admitted by closed law"))
            if item.version_custody_ref != custody.custody_id:
                issues.append(_issue(f"{prefix}.version_custody_ref", GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH, "transition custody mismatch"))
            if target.stage is not GateLifecycleStage.SCHEMA_DECLARED and source.lifecycle_record_id not in target.predecessor_lifecycle_record_ids:
                issues.append(_issue(f"{prefix}.target_lifecycle_record_id", GateValidationCode.REFERENCE_NOT_FOUND, "target does not preserve source ancestry"))
        for predecessor in item.predecessor_transition_refs:
            if predecessor not in transition_by_id:
                issues.append(_issue(f"{prefix}.predecessor_transition_refs", GateValidationCode.REFERENCE_NOT_FOUND, f"unknown transition predecessor {predecessor}"))

    terminal_sealed = bool(lifecycle_records) and lifecycle_records[-1].stage is GateLifecycleStage.RECORD_SEALED
    expected_true = (
        ("validation_complete", terminal_sealed),
        ("provenance_validation_complete", terminal_sealed),
        ("schema_versions_known", True),
        ("gate_profile_version_known", True),
    )
    for name, expected in expected_true:
        value = getattr(record, name)
        if type(value) is not bool:
            issues.append(_type_issue(f"bundle.{name}", bool, value))
        elif value is not expected:
            issues.append(_issue(f"bundle.{name}", GateValidationCode.LIFECYCLE_STAGE_INVALID, f"expected {expected}"))
    issues.extend(_false_flags(record, _BUNDLE_FALSE_FLAGS, "bundle"))
    issues.extend(_text_issues(record.canonical_digest, "bundle.canonical_digest", sha256=True))
    issues.extend(_exact(record.schema_version, SLICE40B_SCHEMA_VERSION, "bundle.schema_version", GateValidationCode.SCHEMA_VERSION_MISMATCH))
    if record.canonical_digest != expected_bundle_digest(record):
        issues.append(_issue("bundle.canonical_digest", GateValidationCode.CANONICAL_DIGEST_MISMATCH, "canonical bundle digest mismatch"))
    if record.bundle_id != expected_bundle_id(record):
        issues.append(_issue("bundle.bundle_id", GateValidationCode.IDENTITY_MISMATCH, "deterministic bundle identity mismatch"))
    return _report(issues)


def _assert(report: GateValidationReport, record: Any) -> Any:
    if not report.ok:
        raise GateValidationError(report)
    return record


def assert_valid_review_record(record: VerbalCognitionGateReviewRecord) -> VerbalCognitionGateReviewRecord:
    return _assert(validate_review_record(record), record)


def assert_valid_version_custody(
    record: GateVersionCustody,
    *,
    review_record: VerbalCognitionGateReviewRecord | None = None,
) -> GateVersionCustody:
    return _assert(validate_version_custody(record, review_record=review_record), record)


def assert_valid_governance_bundle(record: GateGovernanceBundle) -> GateGovernanceBundle:
    return _assert(validate_governance_bundle(record), record)


__all__ = (
    "assert_valid_governance_bundle",
    "assert_valid_review_record",
    "assert_valid_version_custody",
    "validate_candidate_input",
    "validate_field_pairs",
    "validate_gate_identity",
    "validate_gate_profile",
    "validate_governance_bundle",
    "validate_lifecycle_record",
    "validate_lifecycle_transition_record",
    "validate_limitation_reference",
    "validate_provenance_reference",
    "validate_reason_ground",
    "validate_requirement",
    "validate_review_record",
    "validate_trace_reference",
    "validate_version_custody",
)
