"""Fail-closed validation for Slice 40C expectancy evaluation."""

from __future__ import annotations

import re
from typing import Iterable

from ..governed_lifecycle import (
    GateLifecycleStage,
    validate_governance_bundle,
)
from ..schema import VerbalCognitionGateFamily
from .identity import (
    expected_result_digest,
    with_expected_evaluation_input_id,
    with_expected_finding_id,
    with_expected_observation_id,
    with_expected_profile_id,
    with_expected_requirement_id,
)
from .schema import (
    DIGEST_ALGORITHM,
    SLICE40C_PROFILE_VERSION,
    SLICE40C_SCHEMA_VERSION,
    ExpectancyAuthorityState,
    ExpectancyEvaluationInput,
    ExpectancyFinding,
    ExpectancyGateResult,
    ExpectancyGateRuntimeProfile,
    ExpectancyObservation,
    ExpectancyRequirement,
    ExpectancyRequirementKind,
    ExpectancyValidationCode,
    ExpectancyValidationError,
    ExpectancyValidationIssue,
    ExpectancyValidationReport,
)

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _issue(path: str, code: ExpectancyValidationCode, detail: str) -> ExpectancyValidationIssue:
    return ExpectancyValidationIssue(path=path, code=code, detail=detail)


def _ordered(issues: Iterable[ExpectancyValidationIssue]) -> ExpectancyValidationReport:
    return ExpectancyValidationReport(
        issues=tuple(sorted(issues, key=lambda item: (item.path, item.code.value, item.detail)))
    )


def _text(value: object, path: str, issues: list[ExpectancyValidationIssue]) -> None:
    if not isinstance(value, str) or not value or _IDENTIFIER.fullmatch(value) is None:
        issues.append(_issue(path, ExpectancyValidationCode.INVALID_IDENTIFIER, "non-empty controlled identifier required"))


def _tuple_ids(value: object, path: str, issues: list[ExpectancyValidationIssue], *, allow_empty: bool = True) -> None:
    if not isinstance(value, tuple) or (not allow_empty and not value):
        issues.append(_issue(path, ExpectancyValidationCode.TYPE_MISMATCH, "tuple of controlled identifiers required"))
        return
    if len(set(value)) != len(value):
        issues.append(_issue(path, ExpectancyValidationCode.DUPLICATE_ID, "duplicate tuple value"))
    for index, item in enumerate(value):
        _text(item, f"{path}[{index}]", issues)


def _identity_matches(actual: object, expected: object, field: str, path: str, issues: list[ExpectancyValidationIssue]) -> None:
    if getattr(actual, field) != getattr(expected, field):
        issues.append(_issue(path, ExpectancyValidationCode.IDENTITY_MISMATCH, "deterministic identity mismatch"))


def validate_profile(value: object) -> ExpectancyValidationReport:
    issues: list[ExpectancyValidationIssue] = []
    if not isinstance(value, ExpectancyGateRuntimeProfile):
        return _ordered((_issue("profile", ExpectancyValidationCode.TYPE_MISMATCH, "ExpectancyGateRuntimeProfile required"),))
    for name in ("profile_id", "profile_key", "gate_profile_ref"):
        _text(getattr(value, name), f"profile.{name}", issues)
    if value.profile_version != SLICE40C_PROFILE_VERSION or value.gate_profile_version != "v1.0.0":
        issues.append(_issue("profile.profile_version", ExpectancyValidationCode.INVALID_VERSION, "only v1.0.0 is admitted"))
    if value.schema_version != SLICE40C_SCHEMA_VERSION:
        issues.append(_issue("profile.schema_version", ExpectancyValidationCode.INVALID_VERSION, "Slice 40C schema version required"))
    _tuple_ids(value.governing_authority_refs, "profile.governing_authority_refs", issues, allow_empty=False)
    if value.permitted_requirement_kinds != tuple(ExpectancyRequirementKind):
        issues.append(_issue("profile.permitted_requirement_kinds", ExpectancyValidationCode.CROSS_RECORD_MISMATCH, "all and only the five Slice 40C requirement kinds are permitted"))
    required_true = ("exact_admitted_requirements_only",)
    required_false = (
        "raw_text_inspection_allowed", "hidden_context_allowed",
        "default_participant_inference_allowed", "unstated_referent_inference_allowed",
        "automatic_clarification_allowed", "gate_composition_allowed",
        "selected_meaning_allowed", "route_tool_action_allowed",
    )
    for name in required_true:
        if getattr(value, name) is not True:
            issues.append(_issue(f"profile.{name}", ExpectancyValidationCode.INVENTED_REQUIREMENT_PROHIBITED, "must be true"))
    for name in required_false:
        if getattr(value, name) is not False:
            issues.append(_issue(f"profile.{name}", ExpectancyValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED, "must be false"))
    _identity_matches(value, with_expected_profile_id(value), "profile_id", "profile.profile_id", issues)
    return _ordered(issues)


def validate_requirement(value: object) -> ExpectancyValidationReport:
    issues: list[ExpectancyValidationIssue] = []
    if not isinstance(value, ExpectancyRequirement):
        return _ordered((_issue("requirement", ExpectancyValidationCode.TYPE_MISMATCH, "ExpectancyRequirement required"),))
    for name in ("requirement_id", "candidate_input_ref", "predicate_id", "frame_id", "requirement_key"):
        _text(getattr(value, name), f"requirement.{name}", issues)
    for name in ("predicate_version", "frame_version"):
        if getattr(value, name) != "v1.0.0":
            issues.append(_issue(f"requirement.{name}", ExpectancyValidationCode.INVALID_VERSION, "exact admitted v1.0.0 required"))
    for name in ("requirement_source_refs", "authority_refs", "subject_record_refs", "relation_refs"):
        _tuple_ids(getattr(value, name), f"requirement.{name}", issues, allow_empty=name in ("subject_record_refs", "relation_refs"))
    if not isinstance(value.minimum_count, int) or isinstance(value.minimum_count, bool) or value.minimum_count < 1:
        issues.append(_issue("requirement.minimum_count", ExpectancyValidationCode.COUNT_MISMATCH, "minimum_count must be a positive integer"))
    optional = value.requirement_kind is ExpectancyRequirementKind.OPTIONAL_DETAIL
    if value.required is optional:
        issues.append(_issue("requirement.required", ExpectancyValidationCode.CROSS_RECORD_MISMATCH, "optional detail must be non-required and all other kinds required"))
    if value.exact_admitted_requirement is not True:
        issues.append(_issue("requirement.exact_admitted_requirement", ExpectancyValidationCode.INVENTED_REQUIREMENT_PROHIBITED, "requirement must be supplied by exact admitted authority"))
    if value.schema_version != SLICE40C_SCHEMA_VERSION:
        issues.append(_issue("requirement.schema_version", ExpectancyValidationCode.INVALID_VERSION, "Slice 40C schema version required"))
    _identity_matches(value, with_expected_requirement_id(value), "requirement_id", "requirement.requirement_id", issues)
    return _ordered(issues)


def validate_observation(value: object) -> ExpectancyValidationReport:
    issues: list[ExpectancyValidationIssue] = []
    if not isinstance(value, ExpectancyObservation):
        return _ordered((_issue("observation", ExpectancyValidationCode.TYPE_MISMATCH, "ExpectancyObservation required"),))
    for name in ("observation_id", "requirement_ref", "candidate_input_ref"):
        _text(getattr(value, name), f"observation.{name}", issues)
    for name in ("observed_record_refs", "observed_relation_refs", "trace_refs", "provenance_refs"):
        _tuple_ids(getattr(value, name), f"observation.{name}", issues)
    if value.authority_state is not ExpectancyAuthorityState.ADMITTED and value.observed_count:
        issues.append(_issue("observation.authority_state", ExpectancyValidationCode.AUTHORITY_STATE_INVALID, "non-admitted authority cannot supply satisfying observations"))
    if value.schema_version != SLICE40C_SCHEMA_VERSION:
        issues.append(_issue("observation.schema_version", ExpectancyValidationCode.INVALID_VERSION, "Slice 40C schema version required"))
    _identity_matches(value, with_expected_observation_id(value), "observation_id", "observation.observation_id", issues)
    return _ordered(issues)


def validate_evaluation_input(value: object) -> ExpectancyValidationReport:
    issues: list[ExpectancyValidationIssue] = []
    if not isinstance(value, ExpectancyEvaluationInput):
        return _ordered((_issue("input", ExpectancyValidationCode.TYPE_MISMATCH, "ExpectancyEvaluationInput required"),))
    _text(value.evaluation_input_id, "input.evaluation_input_id", issues)
    for name in ("candidate_input_ref", "predicate_id", "frame_id"):
        _text(getattr(value, name), f"input.{name}", issues)
    for name in ("predicate_version", "frame_version"):
        if getattr(value, name) != "v1.0.0":
            issues.append(_issue(f"input.{name}", ExpectancyValidationCode.INVALID_VERSION, "exact admitted v1.0.0 required"))
    for name in ("trace_refs", "provenance_refs", "limitation_refs"):
        _tuple_ids(getattr(value, name), f"input.{name}", issues, allow_empty=name == "limitation_refs")
    issues.extend(validate_profile(value.runtime_profile).issues)
    governance = validate_governance_bundle(value.governance_bundle)
    if not governance.ok:
        issues.append(_issue("input.governance_bundle", ExpectancyValidationCode.GOVERNANCE_INVALID, "Slice 40B governance bundle must validate"))
    review = value.governance_bundle.review_record
    if review.identity.gate_family is not VerbalCognitionGateFamily.EXPECTANCY:
        issues.append(_issue("input.governance_bundle.review_record.identity.gate_family", ExpectancyValidationCode.EXPECTANCY_FAMILY_REQUIRED, "expectancy gate family required"))
    if not value.governance_bundle.lifecycle_records or value.governance_bundle.lifecycle_records[-1].stage is not GateLifecycleStage.RECORD_SEALED:
        issues.append(_issue("input.governance_bundle.lifecycle_records", ExpectancyValidationCode.SEALED_GOVERNANCE_REQUIRED, "sealed Slice 40B custody required"))
    if value.runtime_profile.gate_profile_ref != review.profile.profile_id:
        issues.append(_issue("input.runtime_profile.gate_profile_ref", ExpectancyValidationCode.CROSS_RECORD_MISMATCH, "runtime profile must bind the governed gate profile"))
    if value.candidate_input_ref != review.candidate_input.candidate_input_ref_id:
        issues.append(_issue("input.candidate_input_ref", ExpectancyValidationCode.CROSS_RECORD_MISMATCH, "candidate reference must match governed review"))
    requirement_ids = [item.requirement_id for item in value.requirements]
    observation_refs = [item.requirement_ref for item in value.observations]
    if not value.requirements:
        issues.append(_issue("input.requirements", ExpectancyValidationCode.REQUIRED_VALUE_MISSING, "at least one admitted requirement is required"))
    if len(set(requirement_ids)) != len(requirement_ids):
        issues.append(_issue("input.requirements", ExpectancyValidationCode.DUPLICATE_ID, "duplicate requirement id"))
    if len(set(observation_refs)) != len(observation_refs):
        issues.append(_issue("input.observations", ExpectancyValidationCode.DUPLICATE_ID, "one observation per requirement required"))
    if set(requirement_ids) != set(observation_refs):
        issues.append(_issue("input.observations", ExpectancyValidationCode.REFERENCE_NOT_FOUND, "observations must cover all and only declared requirements"))
    for index, requirement in enumerate(value.requirements):
        report = validate_requirement(requirement)
        issues.extend(_issue(f"input.requirements[{index}].{item.path}", item.code, item.detail) for item in report.issues)
        if requirement.candidate_input_ref != value.candidate_input_ref or requirement.predicate_id != value.predicate_id or requirement.frame_id != value.frame_id:
            issues.append(_issue(f"input.requirements[{index}]", ExpectancyValidationCode.CROSS_RECORD_MISMATCH, "requirement candidate, predicate, and frame must match evaluation input"))
    for index, observation in enumerate(value.observations):
        report = validate_observation(observation)
        issues.extend(_issue(f"input.observations[{index}].{item.path}", item.code, item.detail) for item in report.issues)
        if observation.candidate_input_ref != value.candidate_input_ref:
            issues.append(_issue(f"input.observations[{index}].candidate_input_ref", ExpectancyValidationCode.CROSS_RECORD_MISMATCH, "observation candidate must match evaluation input"))
    for name in ("raw_text_supplied", "hidden_context_used", "defaults_used", "inferred_participants_created", "inferred_referents_created"):
        if getattr(value, name) is not False:
            code = ExpectancyValidationCode.RAW_TEXT_PROHIBITED if name == "raw_text_supplied" else ExpectancyValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
            issues.append(_issue(f"input.{name}", code, "must remain false"))
    if value.schema_version != SLICE40C_SCHEMA_VERSION:
        issues.append(_issue("input.schema_version", ExpectancyValidationCode.INVALID_VERSION, "Slice 40C schema version required"))
    _identity_matches(value, with_expected_evaluation_input_id(value), "evaluation_input_id", "input.evaluation_input_id", issues)
    return _ordered(issues)


def assert_valid_evaluation_input(value: ExpectancyEvaluationInput) -> ExpectancyEvaluationInput:
    report = validate_evaluation_input(value)
    if not report.ok:
        raise ExpectancyValidationError(report)
    return value


def validate_finding(value: object) -> ExpectancyValidationReport:
    issues: list[ExpectancyValidationIssue] = []
    if not isinstance(value, ExpectancyFinding):
        return _ordered((_issue("finding", ExpectancyValidationCode.TYPE_MISMATCH, "ExpectancyFinding required"),))
    for name in ("finding_id", "evaluation_input_ref"):
        _text(getattr(value, name), f"finding.{name}", issues)
    if value.requirement_ref is not None:
        _text(value.requirement_ref, "finding.requirement_ref", issues)
    for name in ("supporting_record_refs", "supporting_relation_refs", "trace_refs", "provenance_refs", "reason_refs"):
        _tuple_ids(getattr(value, name), f"finding.{name}", issues, allow_empty=True)
    if min(value.required_count, value.observed_count) < 0:
        issues.append(_issue("finding.counts", ExpectancyValidationCode.COUNT_MISMATCH, "counts cannot be negative"))
    _identity_matches(value, with_expected_finding_id(value), "finding_id", "finding.finding_id", issues)
    return _ordered(issues)


def validate_result(value: object) -> ExpectancyValidationReport:
    issues: list[ExpectancyValidationIssue] = []
    if not isinstance(value, ExpectancyGateResult):
        return _ordered((_issue("result", ExpectancyValidationCode.TYPE_MISMATCH, "ExpectancyGateResult required"),))
    for name in ("result_id", "evaluation_input_ref", "review_record_id", "gate_id", "gate_profile_id", "candidate_input_ref", "predicate_id", "frame_id"):
        _text(getattr(value, name), f"result.{name}", issues)
    for index, finding in enumerate(value.findings):
        report = validate_finding(finding)
        issues.extend(_issue(f"result.findings[{index}].{item.path}", item.code, item.detail) for item in report.issues)
    if value.requirement_count != value.required_requirement_count + sum(1 for item in value.findings if item.finding_kind.value == "optional_detail_omitted") and value.optional_omitted_count == 0:
        pass
    for name in ("requirement_count", "required_requirement_count", "satisfied_required_count", "missing_required_count", "optional_omitted_count", "indeterminate_count"):
        if not isinstance(getattr(value, name), int) or getattr(value, name) < 0:
            issues.append(_issue(f"result.{name}", ExpectancyValidationCode.COUNT_MISMATCH, "non-negative integer required"))
    if value.digest_algorithm != DIGEST_ALGORITHM or _SHA256.fullmatch(value.canonical_digest) is None:
        issues.append(_issue("result.canonical_digest", ExpectancyValidationCode.INVALID_SHA256, "canonical SHA-256 required"))
    if value.canonical_digest != expected_result_digest(value):
        issues.append(_issue("result.canonical_digest", ExpectancyValidationCode.IDENTITY_MISMATCH, "result digest mismatch"))
    if value.result_id != f"expectancy_result:sha256:{value.canonical_digest}":
        issues.append(_issue("result.result_id", ExpectancyValidationCode.IDENTITY_MISMATCH, "result id mismatch"))
    must_true = ("deterministic", "exact_requirement_authority_preserved")
    must_false = (
        "candidate_structure_mutated", "missing_role_filled", "referent_invented",
        "unstated_participant_inferred", "clarification_required_created", "rejection_created",
        "refusal_relevant_created", "blocked_progression_created", "composed_gate_outcome_created",
        "candidate_disposition_created", "selected_meaning_created", "truth_determined",
        "evidence_validated", "permission_granted", "execution_authorized", "route_created",
        "tool_invoked", "action_performed", "memory_accessed", "rendered", "delivered",
        "external_resource_loaded", "language_model_used", "embedding_used", "vector_used",
        "rag_used", "semantic_similarity_used",
    )
    for name in must_true:
        if getattr(value, name) is not True:
            issues.append(_issue(f"result.{name}", ExpectancyValidationCode.CROSS_RECORD_MISMATCH, "must be true"))
    for name in must_false:
        if getattr(value, name) is not False:
            issues.append(_issue(f"result.{name}", ExpectancyValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED, "must remain false"))
    return _ordered(issues)


def assert_valid_result(value: ExpectancyGateResult) -> ExpectancyGateResult:
    report = validate_result(value)
    if not report.ok:
        raise ExpectancyValidationError(report)
    return value


__all__ = (
    "assert_valid_evaluation_input", "assert_valid_result", "validate_evaluation_input",
    "validate_finding", "validate_observation", "validate_profile", "validate_requirement",
    "validate_result",
)
