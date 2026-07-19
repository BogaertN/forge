"""Strict deterministic validation for Slice 40G gate composition."""
from __future__ import annotations

from collections import Counter
from dataclasses import fields
import re
from typing import Iterable

from ..schema import VerbalCognitionGateFamily
from ..governed_lifecycle.validation import validate_governance_bundle
from ..expectancy_gate.schema import ExpectancyOverallState
from ..expectancy_gate.validation import validate_result as validate_expectancy_result
from ..congruity_gate.schema import CongruityOverallState
from ..congruity_gate.validation import validate_result as validate_congruity_result
from ..connectedness_gate.schema import ConnectednessOverallState
from ..connectedness_gate.validation import validate_result as validate_connectedness_result
from ..recoverable_purpose_gate.schema import RecoverablePurposeOverallState
from ..recoverable_purpose_gate.validation import validate_result as validate_purpose_result
from .identity import (
    with_expected_assertion_id,
    with_expected_disposition_id,
    with_expected_evaluation_input_id,
    with_expected_finding_id,
    with_expected_profile_id,
    with_expected_result_identity,
)
from .schema import (
    DIGEST_ALGORITHM,
    SLICE40G_PROFILE_VERSION,
    SLICE40G_SCHEMA_VERSION,
    CandidateNonSelectionDisposition,
    GateCompositionAuthorityState,
    GateCompositionDispositionAssertion,
    GateCompositionDispositionKind,
    GateCompositionEvaluationInput,
    GateCompositionFinding,
    GateCompositionFindingKind,
    GateCompositionJudgment,
    GateCompositionResult,
    GateCompositionRuntimeProfile,
    GateCompositionStatus,
    GateCompositionValidationCode,
    GateCompositionValidationError,
    GateCompositionValidationIssue,
    GateCompositionValidationReport,
)

_ID_RE = re.compile(r"^[A-Za-z0-9_.:/-]+$")
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
_FAMILIES = (
    VerbalCognitionGateFamily.EXPECTANCY,
    VerbalCognitionGateFamily.CONGRUITY,
    VerbalCognitionGateFamily.CONNECTEDNESS,
    VerbalCognitionGateFamily.RECOVERABLE_PURPOSE,
)


def _issue(path: str, code: GateCompositionValidationCode, detail: str) -> GateCompositionValidationIssue:
    return GateCompositionValidationIssue(path=path, code=code, detail=detail)


def _report(issues: Iterable[GateCompositionValidationIssue]) -> GateCompositionValidationReport:
    return GateCompositionValidationReport(
        issues=tuple(sorted(issues, key=lambda item: (item.path, item.code.value, item.detail)))
    )


def _text(value: object, path: str, issues: list[GateCompositionValidationIssue]) -> None:
    if not isinstance(value, str) or not value or not _ID_RE.fullmatch(value):
        issues.append(_issue(path, GateCompositionValidationCode.INVALID_IDENTIFIER, "non-empty controlled identifier required"))


def _sha(value: object, path: str, issues: list[GateCompositionValidationIssue]) -> None:
    if not isinstance(value, str) or not _SHA_RE.fullmatch(value):
        issues.append(_issue(path, GateCompositionValidationCode.INVALID_SHA256, "lowercase SHA-256 required"))


def _tuple_text(value: object, path: str, issues: list[GateCompositionValidationIssue], allow_empty: bool = True) -> None:
    if not isinstance(value, tuple):
        issues.append(_issue(path, GateCompositionValidationCode.TYPE_MISMATCH, "tuple required"))
        return
    if not allow_empty and not value:
        issues.append(_issue(path, GateCompositionValidationCode.DISPOSITION_BASIS_REQUIRED, "non-empty tuple required"))
    seen = set()
    for index, item in enumerate(value):
        _text(item, f"{path}[{index}]", issues)
        if item in seen:
            issues.append(_issue(f"{path}[{index}]", GateCompositionValidationCode.DUPLICATE_ID, "duplicate identifier"))
        seen.add(item)


def _identity(actual: object, expected: object, field_name: str, path: str, issues: list[GateCompositionValidationIssue]) -> None:
    if getattr(actual, field_name, None) != getattr(expected, field_name, None):
        issues.append(_issue(path, GateCompositionValidationCode.IDENTITY_MISMATCH, "deterministic identity mismatch"))


def _false_flags(value: object, names: tuple[str, ...], issues: list[GateCompositionValidationIssue], code: GateCompositionValidationCode) -> None:
    for name in names:
        if getattr(value, name) is not False:
            issues.append(_issue(name, code, "must be false"))


def _kind_basis(assertion: GateCompositionDispositionAssertion) -> tuple[str, ...]:
    mapping = {
        GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED: assertion.ambiguity_refs,
        GateCompositionDispositionKind.CLARIFICATION_RELEVANT: assertion.clarification_refs,
        GateCompositionDispositionKind.UNSUPPORTED: assertion.unsupported_refs,
        GateCompositionDispositionKind.REFUSAL_RELEVANT: assertion.refusal_relevance_refs,
        GateCompositionDispositionKind.HELD: assertion.hold_refs,
        GateCompositionDispositionKind.BLOCKED_PROGRESSION: assertion.blocked_progression_refs,
        GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW: assertion.later_selection_review_refs,
    }
    return mapping[assertion.disposition_kind]


def validate_profile(value: object) -> GateCompositionValidationReport:
    issues: list[GateCompositionValidationIssue] = []
    if not isinstance(value, GateCompositionRuntimeProfile):
        return _report((_issue("profile", GateCompositionValidationCode.TYPE_MISMATCH, "GateCompositionRuntimeProfile required"),))
    for name in ("profile_id", "profile_key"):
        _text(getattr(value, name), f"profile.{name}", issues)
    if value.profile_version != SLICE40G_PROFILE_VERSION or value.schema_version != SLICE40G_SCHEMA_VERSION:
        issues.append(_issue("profile.profile_version", GateCompositionValidationCode.INVALID_VERSION, "Slice 40G v1.0.0 profile required"))
    _tuple_text(value.governing_authority_refs, "profile.governing_authority_refs", issues, False)
    if value.permitted_disposition_kinds != tuple(GateCompositionDispositionKind):
        issues.append(_issue("profile.permitted_disposition_kinds", GateCompositionValidationCode.CROSS_RECORD_MISMATCH, "all and only seven canonical dispositions required"))
    for name in ("exact_family_results_required", "preserve_all_gate_results", "candidate_specific_composition_required"):
        if getattr(value, name) is not True:
            issues.append(_issue(f"profile.{name}", GateCompositionValidationCode.EXACT_FAMILY_RESULTS_REQUIRED, "must be true"))
    _false_flags(value, (
        "gate_substitution_allowed", "gate_outcome_erasure_allowed", "generic_flattening_allowed",
        "global_pass_generalization_allowed", "global_failure_generalization_allowed",
        "candidate_branch_erasure_allowed", "effect_boundary_rewrite_allowed",
        "domain_marker_erasure_allowed", "no_action_boundary_conversion_allowed",
        "automatic_ambiguity_allowed", "automatic_clarification_allowed",
        "automatic_refusal_allowed", "safest_candidate_selection_allowed",
        "selected_meaning_allowed", "downstream_authority_allowed",
    ), issues, GateCompositionValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED)
    _identity(value, with_expected_profile_id(value), "profile_id", "profile.profile_id", issues)
    return _report(issues)


def validate_assertion(value: object) -> GateCompositionValidationReport:
    issues: list[GateCompositionValidationIssue] = []
    if not isinstance(value, GateCompositionDispositionAssertion):
        return _report((_issue("assertion", GateCompositionValidationCode.TYPE_MISMATCH, "GateCompositionDispositionAssertion required"),))
    for name in ("assertion_id", "candidate_input_ref", "candidate_branch_ref"):
        _text(getattr(value, name), f"assertion.{name}", issues)
    if not isinstance(value.disposition_kind, GateCompositionDispositionKind):
        issues.append(_issue("assertion.disposition_kind", GateCompositionValidationCode.TYPE_MISMATCH, "closed disposition kind required"))
    if not isinstance(value.authority_state, GateCompositionAuthorityState):
        issues.append(_issue("assertion.authority_state", GateCompositionValidationCode.AUTHORITY_STATE_INVALID, "closed authority state required"))
    if not isinstance(value.judgment, GateCompositionJudgment):
        issues.append(_issue("assertion.judgment", GateCompositionValidationCode.JUDGMENT_INVALID, "closed judgment required"))
    for name in (
        "gate_result_refs", "supporting_refs", "missing_authority_refs", "conflicting_refs",
        "ambiguity_refs", "clarification_refs", "unsupported_refs", "refusal_relevance_refs",
        "hold_refs", "blocked_progression_refs", "later_selection_review_refs",
        "later_authority_dependency_refs", "effect_boundary_refs", "domain_marker_refs",
        "no_action_boundary_refs", "trace_refs", "provenance_refs",
    ):
        _tuple_text(getattr(value, name), f"assertion.{name}", issues, name not in ("gate_result_refs", "trace_refs", "provenance_refs"))
    if value.candidate_specific is not True:
        issues.append(_issue("assertion.candidate_specific", GateCompositionValidationCode.CROSS_RECORD_MISMATCH, "candidate-specific assertion required"))
    if isinstance(value.authority_state, GateCompositionAuthorityState) and isinstance(value.judgment, GateCompositionJudgment):
        if value.authority_state is GateCompositionAuthorityState.ADMITTED:
            if value.judgment not in (GateCompositionJudgment.APPLIES, GateCompositionJudgment.DOES_NOT_APPLY):
                issues.append(_issue("assertion.judgment", GateCompositionValidationCode.JUDGMENT_INVALID, "admitted authority requires applies or does_not_apply"))
        elif value.judgment is not GateCompositionJudgment.NOT_EVALUATED:
            issues.append(_issue("assertion.judgment", GateCompositionValidationCode.JUDGMENT_INVALID, "non-admitted authority must remain not_evaluated"))
        if value.authority_state is GateCompositionAuthorityState.ABSENT and not value.missing_authority_refs:
            issues.append(_issue("assertion.missing_authority_refs", GateCompositionValidationCode.DISPOSITION_BASIS_REQUIRED, "absent authority must identify missing records"))
        if value.authority_state in (GateCompositionAuthorityState.AMBIGUOUS, GateCompositionAuthorityState.CONFLICTED) and not value.conflicting_refs:
            issues.append(_issue("assertion.conflicting_refs", GateCompositionValidationCode.DISPOSITION_BASIS_REQUIRED, "ambiguous or conflicted authority requires conflict refs"))
        if value.authority_state is GateCompositionAuthorityState.UNSUPPORTED and not value.unsupported_refs:
            issues.append(_issue("assertion.unsupported_refs", GateCompositionValidationCode.DISPOSITION_BASIS_REQUIRED, "unsupported authority requires exact unsupported refs"))
        if value.authority_state is GateCompositionAuthorityState.ADMITTED and value.judgment is GateCompositionJudgment.APPLIES:
            if not _kind_basis(value):
                issues.append(_issue("assertion.disposition_basis", GateCompositionValidationCode.DISPOSITION_BASIS_REQUIRED, "applied disposition requires exact kind-specific basis"))
    # Only the matching kind-specific basis may be populated for an applied assertion.
    if isinstance(value.disposition_kind, GateCompositionDispositionKind):
        basis_fields = {
            "ambiguity_refs": GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED,
            "clarification_refs": GateCompositionDispositionKind.CLARIFICATION_RELEVANT,
            "unsupported_refs": GateCompositionDispositionKind.UNSUPPORTED,
            "refusal_relevance_refs": GateCompositionDispositionKind.REFUSAL_RELEVANT,
            "hold_refs": GateCompositionDispositionKind.HELD,
            "blocked_progression_refs": GateCompositionDispositionKind.BLOCKED_PROGRESSION,
            "later_selection_review_refs": GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW,
        }
        for field_name, kind in basis_fields.items():
            if kind is not value.disposition_kind and getattr(value, field_name):
                issues.append(_issue(f"assertion.{field_name}", GateCompositionValidationCode.CROSS_RECORD_MISMATCH, "basis belongs to a different disposition kind"))
    if value.schema_version != SLICE40G_SCHEMA_VERSION:
        issues.append(_issue("assertion.schema_version", GateCompositionValidationCode.INVALID_VERSION, "Slice 40G schema required"))
    _identity(value, with_expected_assertion_id(value), "assertion_id", "assertion.assertion_id", issues)
    return _report(issues)


def _family_results(value: GateCompositionEvaluationInput):
    return (
        value.expectancy_result,
        value.congruity_result,
        value.connectedness_result,
        value.recoverable_purpose_result,
    )


def _all_positive(value: GateCompositionEvaluationInput) -> bool:
    return (
        value.expectancy_result.overall_state is ExpectancyOverallState.STRUCTURALLY_COMPLETE
        and value.congruity_result.overall_state is CongruityOverallState.COMPATIBLE
        and value.connectedness_result.overall_state is ConnectednessOverallState.CONNECTED
        and value.recoverable_purpose_result.overall_state is RecoverablePurposeOverallState.RECOVERABLE
    )


def validate_evaluation_input(value: object) -> GateCompositionValidationReport:
    issues: list[GateCompositionValidationIssue] = []
    if not isinstance(value, GateCompositionEvaluationInput):
        return _report((_issue("evaluation_input", GateCompositionValidationCode.TYPE_MISMATCH, "GateCompositionEvaluationInput required"),))
    for name in ("evaluation_input_id", "candidate_input_ref", "candidate_branch_ref"):
        _text(getattr(value, name), f"evaluation_input.{name}", issues)
    if value.candidate_version != "v1.0.0" or value.schema_version != SLICE40G_SCHEMA_VERSION:
        issues.append(_issue("evaluation_input.candidate_version", GateCompositionValidationCode.INVALID_VERSION, "v1.0.0 and Slice 40G schema required"))
    profile_report = validate_profile(value.runtime_profile)
    issues.extend(profile_report.issues)
    if not isinstance(value.governance_bundles, tuple) or len(value.governance_bundles) != 4:
        issues.append(_issue("evaluation_input.governance_bundles", GateCompositionValidationCode.EXACT_FAMILY_RESULTS_REQUIRED, "exactly four governance bundles required"))
    else:
        families = []
        for index, bundle in enumerate(value.governance_bundles):
            report = validate_governance_bundle(bundle)
            if not report.ok:
                issues.append(_issue(f"evaluation_input.governance_bundles[{index}]", GateCompositionValidationCode.GOVERNANCE_INVALID, "governance bundle invalid"))
                continue
            families.append(bundle.review_record.identity.gate_family)
            if not (
                bundle.validation_complete
                and bundle.provenance_validation_complete
                and bundle.schema_versions_known
                and bundle.gate_profile_version_known
            ):
                issues.append(_issue(f"evaluation_input.governance_bundles[{index}]", GateCompositionValidationCode.SEALED_GOVERNANCE_REQUIRED, "sealed governance required"))
        if tuple(families) != _FAMILIES:
            issues.append(_issue("evaluation_input.governance_bundles", GateCompositionValidationCode.CROSS_RECORD_MISMATCH, "governance bundles must be ordered expectancy, congruity, connectedness, recoverable_purpose"))
    validators = (
        validate_expectancy_result,
        validate_congruity_result,
        validate_connectedness_result,
        validate_purpose_result,
    )
    results = _family_results(value)
    for index, (result, validator) in enumerate(zip(results, validators)):
        if not validator(result).ok:
            issues.append(_issue(f"evaluation_input.family_results[{index}]", GateCompositionValidationCode.RESULT_INVALID, "family result failed its accepted validator"))
    result_ids = tuple(result.result_id for result in results)
    if len(set(result_ids)) != 4:
        issues.append(_issue("evaluation_input.family_results", GateCompositionValidationCode.DUPLICATE_ID, "four unique family result ids required"))
    _tuple_text(value.family_candidate_input_refs, "evaluation_input.family_candidate_input_refs", issues, False)
    if value.family_candidate_input_refs != tuple(result.candidate_input_ref for result in results):
        issues.append(_issue("evaluation_input.family_candidate_input_refs", GateCompositionValidationCode.CROSS_RECORD_MISMATCH, "exact ordered family candidate-input references required"))
    if isinstance(value.governance_bundles, tuple) and len(value.governance_bundles) == 4:
        for index, (bundle, result) in enumerate(zip(value.governance_bundles, results)):
            if result.review_record_id != bundle.review_record.review_record_id or result.gate_id != bundle.review_record.identity.gate_id or result.gate_profile_id != bundle.review_record.profile.profile_id:
                issues.append(_issue(f"evaluation_input.family_results[{index}]", GateCompositionValidationCode.CROSS_RECORD_MISMATCH, "family result must match its governance bundle"))
            if bundle.review_record.candidate_input.candidate_input_ref_id != result.candidate_input_ref:
                issues.append(_issue(f"evaluation_input.governance_bundles[{index}]", GateCompositionValidationCode.CROSS_RECORD_MISMATCH, "governance candidate must match its family result"))
    for name in (
        "candidate_branch_refs", "material_competing_candidate_refs", "competing_candidate_disposition_refs",
        "user_suppliable_clarification_refs", "effect_boundary_refs", "domain_marker_refs",
        "no_action_boundary_refs", "authority_boundary_refs", "later_authority_dependency_refs",
        "version_refs", "candidate_ancestry_refs", "trace_refs", "provenance_refs", "limitation_refs",
    ):
        _tuple_text(getattr(value, name), f"evaluation_input.{name}", issues, name not in ("candidate_branch_refs", "authority_boundary_refs", "version_refs", "candidate_ancestry_refs", "trace_refs", "provenance_refs", "limitation_refs"))
    if value.candidate_branch_ref not in value.candidate_branch_refs:
        issues.append(_issue("evaluation_input.candidate_branch_ref", GateCompositionValidationCode.REFERENCE_NOT_FOUND, "active branch must be in candidate_branch_refs"))
    if value.material_competing_candidate_refs and len(value.competing_candidate_disposition_refs) > len(value.material_competing_candidate_refs):
        issues.append(_issue("evaluation_input.competing_candidate_disposition_refs", GateCompositionValidationCode.COUNT_MISMATCH, "cannot exceed material competing candidates"))
    if not isinstance(value.disposition_assertions, tuple) or not value.disposition_assertions:
        issues.append(_issue("evaluation_input.disposition_assertions", GateCompositionValidationCode.DISPOSITION_BASIS_REQUIRED, "at least one candidate-specific disposition assertion required"))
    else:
        seen = set()
        for index, assertion in enumerate(value.disposition_assertions):
            issues.extend(validate_assertion(assertion).issues)
            if assertion.assertion_id in seen:
                issues.append(_issue(f"evaluation_input.disposition_assertions[{index}]", GateCompositionValidationCode.DUPLICATE_ID, "duplicate assertion id"))
            seen.add(assertion.assertion_id)
            if assertion.candidate_input_ref != value.candidate_input_ref or assertion.candidate_branch_ref != value.candidate_branch_ref:
                issues.append(_issue(f"evaluation_input.disposition_assertions[{index}]", GateCompositionValidationCode.CROSS_RECORD_MISMATCH, "assertion candidate or branch mismatch"))
            if any(ref not in result_ids for ref in assertion.gate_result_refs):
                issues.append(_issue(f"evaluation_input.disposition_assertions[{index}].gate_result_refs", GateCompositionValidationCode.REFERENCE_NOT_FOUND, "unknown family result reference"))
            if assertion.disposition_kind is GateCompositionDispositionKind.CLARIFICATION_RELEVANT and assertion.judgment is GateCompositionJudgment.APPLIES and not value.user_suppliable_clarification_refs:
                issues.append(_issue(f"evaluation_input.disposition_assertions[{index}]", GateCompositionValidationCode.AUTOMATIC_DISPOSITION_PROHIBITED, "clarification relevance requires explicit user-suppliable support refs"))
            if assertion.disposition_kind is GateCompositionDispositionKind.REFUSAL_RELEVANT and assertion.judgment is GateCompositionJudgment.APPLIES and not assertion.refusal_relevance_refs:
                issues.append(_issue(f"evaluation_input.disposition_assertions[{index}]", GateCompositionValidationCode.AUTOMATIC_DISPOSITION_PROHIBITED, "unsupported state cannot automatically become refusal relevance"))
            if assertion.disposition_kind is GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED and assertion.judgment is GateCompositionJudgment.APPLIES and not (assertion.ambiguity_refs and (value.material_competing_candidate_refs or value.congruity_result.overall_state is CongruityOverallState.AMBIGUOUS or value.connectedness_result.overall_state is ConnectednessOverallState.AMBIGUOUS or value.recoverable_purpose_result.overall_state is RecoverablePurposeOverallState.AMBIGUOUS)):
                issues.append(_issue(f"evaluation_input.disposition_assertions[{index}]", GateCompositionValidationCode.AUTOMATIC_DISPOSITION_PROHIBITED, "multiple candidates alone are not material ambiguity"))
            if assertion.disposition_kind is GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW and assertion.judgment is GateCompositionJudgment.APPLIES:
                if not _all_positive(value) or set(assertion.gate_result_refs) != set(result_ids):
                    issues.append(_issue(f"evaluation_input.disposition_assertions[{index}]", GateCompositionValidationCode.POSITIVE_DISPOSITION_INVALID, "positive selection-review disposition requires all four exact positive family results"))
    _false_flags(value, (
        "raw_text_used_as_selected_meaning", "gate_substitution_used", "gate_outcome_erased",
        "generic_flattening_used", "global_pass_generalized", "global_failure_generalized",
        "candidate_branch_erased", "effect_boundary_rewritten", "domain_marker_erased",
        "no_action_boundary_converted", "automatic_ambiguity_used", "automatic_clarification_used",
        "automatic_refusal_used", "safest_candidate_selected", "candidate_structure_mutated",
    ), issues, GateCompositionValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED)
    _identity(value, with_expected_evaluation_input_id(value), "evaluation_input_id", "evaluation_input.evaluation_input_id", issues)
    return _report(issues)


def validate_finding(value: object) -> GateCompositionValidationReport:
    issues: list[GateCompositionValidationIssue] = []
    if not isinstance(value, GateCompositionFinding):
        return _report((_issue("finding", GateCompositionValidationCode.TYPE_MISMATCH, "GateCompositionFinding required"),))
    for name in ("finding_id", "evaluation_input_ref"):
        _text(getattr(value, name), f"finding.{name}", issues)
    if value.assertion_ref is not None:
        _text(value.assertion_ref, "finding.assertion_ref", issues)
    if not isinstance(value.finding_kind, GateCompositionFindingKind) or not isinstance(value.authority_state, GateCompositionAuthorityState) or not isinstance(value.judgment, GateCompositionJudgment):
        issues.append(_issue("finding", GateCompositionValidationCode.TYPE_MISMATCH, "closed finding, authority, and judgment enums required"))
    for name in ("gate_result_refs", "supporting_refs", "missing_authority_refs", "conflicting_refs", "reason_refs", "trace_refs", "provenance_refs"):
        _tuple_text(getattr(value, name), f"finding.{name}", issues, True)
    if value.schema_version != SLICE40G_SCHEMA_VERSION:
        issues.append(_issue("finding.schema_version", GateCompositionValidationCode.INVALID_VERSION, "Slice 40G schema required"))
    _identity(value, with_expected_finding_id(value), "finding_id", "finding.finding_id", issues)
    return _report(issues)


def validate_disposition(value: object) -> GateCompositionValidationReport:
    issues: list[GateCompositionValidationIssue] = []
    if not isinstance(value, CandidateNonSelectionDisposition):
        return _report((_issue("disposition", GateCompositionValidationCode.TYPE_MISMATCH, "CandidateNonSelectionDisposition required"),))
    for name in ("disposition_id", "evaluation_input_ref", "assertion_ref", "candidate_input_ref", "candidate_branch_ref"):
        _text(getattr(value, name), f"disposition.{name}", issues)
    if not isinstance(value.disposition_kind, GateCompositionDispositionKind):
        issues.append(_issue("disposition.disposition_kind", GateCompositionValidationCode.TYPE_MISMATCH, "closed disposition kind required"))
    for name in ("gate_result_refs", "reason_refs", "later_authority_dependency_refs", "effect_boundary_refs", "domain_marker_refs", "no_action_boundary_refs", "trace_refs", "provenance_refs"):
        _tuple_text(getattr(value, name), f"disposition.{name}", issues, name not in ("gate_result_refs", "reason_refs", "trace_refs", "provenance_refs"))
    if value.non_selection_only is not True:
        issues.append(_issue("disposition.non_selection_only", GateCompositionValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED, "Slice 40G dispositions are non-selection only"))
    if value.schema_version != SLICE40G_SCHEMA_VERSION:
        issues.append(_issue("disposition.schema_version", GateCompositionValidationCode.INVALID_VERSION, "Slice 40G schema required"))
    _identity(value, with_expected_disposition_id(value), "disposition_id", "disposition.disposition_id", issues)
    return _report(issues)


def validate_result(value: object) -> GateCompositionValidationReport:
    issues: list[GateCompositionValidationIssue] = []
    if not isinstance(value, GateCompositionResult):
        return _report((_issue("result", GateCompositionValidationCode.TYPE_MISMATCH, "GateCompositionResult required"),))
    for name in (
        "result_id", "evaluation_input_ref", "candidate_input_ref", "candidate_branch_ref",
        "expectancy_result_id", "expectancy_candidate_input_ref", "congruity_result_id", "congruity_candidate_input_ref",
        "connectedness_result_id", "connectedness_candidate_input_ref", "recoverable_purpose_result_id", "recoverable_purpose_candidate_input_ref",
    ):
        _text(getattr(value, name), f"result.{name}", issues)
    for name in ("expectancy_result_digest", "congruity_result_digest", "connectedness_result_digest", "recoverable_purpose_result_digest", "canonical_digest"):
        _sha(getattr(value, name), f"result.{name}", issues)
    if value.digest_algorithm != DIGEST_ALGORITHM or value.schema_version != SLICE40G_SCHEMA_VERSION:
        issues.append(_issue("result.schema_version", GateCompositionValidationCode.INVALID_VERSION, "Slice 40G SHA-256 result required"))
    if not isinstance(value.composition_status, GateCompositionStatus):
        issues.append(_issue("result.composition_status", GateCompositionValidationCode.TYPE_MISMATCH, "closed composition status required"))
    if not isinstance(value.dispositions, tuple) or not isinstance(value.findings, tuple):
        issues.append(_issue("result", GateCompositionValidationCode.TYPE_MISMATCH, "tuple dispositions and findings required"))
    else:
        for item in value.dispositions:
            issues.extend(validate_disposition(item).issues)
        for item in value.findings:
            issues.extend(validate_finding(item).issues)
        if len({item.disposition_id for item in value.dispositions}) != len(value.dispositions):
            issues.append(_issue("result.dispositions", GateCompositionValidationCode.DUPLICATE_ID, "duplicate disposition id"))
        if len({item.finding_id for item in value.findings}) != len(value.findings):
            issues.append(_issue("result.findings", GateCompositionValidationCode.DUPLICATE_ID, "duplicate finding id"))
    count_fields = (
        value.applied_disposition_count, value.not_applied_count, value.ambiguous_authority_count,
        value.unsupported_authority_count, value.conflicted_authority_count, value.indeterminate_authority_count,
    )
    if any(type(item) is not int or item < 0 for item in (value.assertion_count, *count_fields)):
        issues.append(_issue("result.counts", GateCompositionValidationCode.TYPE_MISMATCH, "non-negative integer counts required"))
    if sum(count_fields) != value.assertion_count:
        issues.append(_issue("result.assertion_count", GateCompositionValidationCode.COUNT_MISMATCH, "authority/judgment counts must cover every assertion"))
    if value.applied_disposition_count != len(value.dispositions):
        issues.append(_issue("result.applied_disposition_count", GateCompositionValidationCode.COUNT_MISMATCH, "applied count must equal disposition count"))
    disposition_counts = Counter(item.disposition_kind for item in value.dispositions)
    expected_counts = {
        GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED: value.material_ambiguity_count,
        GateCompositionDispositionKind.CLARIFICATION_RELEVANT: value.clarification_relevant_count,
        GateCompositionDispositionKind.UNSUPPORTED: value.unsupported_disposition_count,
        GateCompositionDispositionKind.REFUSAL_RELEVANT: value.refusal_relevant_count,
        GateCompositionDispositionKind.HELD: value.held_count,
        GateCompositionDispositionKind.BLOCKED_PROGRESSION: value.blocked_progression_count,
        GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW: value.later_selection_review_count,
    }
    for kind, count in expected_counts.items():
        if disposition_counts[kind] != count:
            issues.append(_issue(f"result.{kind.value}_count", GateCompositionValidationCode.COUNT_MISMATCH, "disposition-kind count mismatch"))
    if not any(item.finding_kind is GateCompositionFindingKind.ALL_FAMILY_RESULTS_PRESERVED for item in value.findings):
        issues.append(_issue("result.findings", GateCompositionValidationCode.EXACT_FAMILY_RESULTS_REQUIRED, "all-family-results-preserved finding required"))
    required_true = (
        "deterministic", "family_results_preserved", "candidate_branches_preserved", "effect_boundaries_preserved",
        "domain_markers_preserved", "no_action_boundaries_preserved", "candidate_ancestry_preserved", "version_discipline_preserved",
    )
    for name in required_true:
        if getattr(value, name) is not True:
            issues.append(_issue(f"result.{name}", GateCompositionValidationCode.OUTCOME_ERASURE_PROHIBITED, "must be true"))
    if value.family_result_count != 4:
        issues.append(_issue("result.family_result_count", GateCompositionValidationCode.EXACT_FAMILY_RESULTS_REQUIRED, "exactly four family results required"))
    booleans = {
        "material_ambiguity_preserved": bool(value.material_ambiguity_count),
        "clarification_relevant_created": bool(value.clarification_relevant_count),
        "unsupported_disposition_created": bool(value.unsupported_disposition_count),
        "refusal_relevant_disposition_created": bool(value.refusal_relevant_count),
        "held_disposition_created": bool(value.held_count),
        "blocked_progression_created": bool(value.blocked_progression_count),
        "positive_selection_review_disposition_created": bool(value.later_selection_review_count),
    }
    for name, expected in booleans.items():
        if getattr(value, name) is not expected:
            issues.append(_issue(f"result.{name}", GateCompositionValidationCode.COUNT_MISMATCH, "disposition flag/count mismatch"))
    _false_flags(value, (
        "candidate_accepted", "candidate_rejected", "candidate_clarified", "selected_meaning_created",
        "truth_determined", "evidence_validated", "permission_granted", "execution_authorized",
        "capability_availability_created", "route_created", "tool_invoked", "action_performed",
        "memory_accessed", "memory_written", "rendered", "delivered", "external_resource_loaded",
        "language_model_used", "embedding_used", "vector_used", "rag_used", "semantic_similarity_used",
        "raw_text_used_as_selected_meaning", "gate_substitution_used", "gate_outcome_erased",
        "generic_flattening_used", "global_pass_generalized", "global_failure_generalized",
        "candidate_branch_erased", "effect_boundary_rewritten", "domain_marker_erased",
        "no_action_boundary_converted", "automatic_ambiguity_used", "automatic_clarification_used",
        "automatic_refusal_used", "safest_candidate_selected", "candidate_structure_mutated",
    ), issues, GateCompositionValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED)
    expected_status = GateCompositionStatus.COMPOSED
    if value.conflicted_authority_count:
        expected_status = GateCompositionStatus.CONFLICTED_AUTHORITY
    elif value.unsupported_authority_count:
        expected_status = GateCompositionStatus.UNSUPPORTED_AUTHORITY
    elif value.ambiguous_authority_count:
        expected_status = GateCompositionStatus.AMBIGUOUS_AUTHORITY
    elif value.indeterminate_authority_count:
        expected_status = GateCompositionStatus.INDETERMINATE_AUTHORITY
    if value.composition_status is not expected_status:
        issues.append(_issue("result.composition_status", GateCompositionValidationCode.CROSS_RECORD_MISMATCH, "composition status precedence mismatch"))
    _identity(value, with_expected_result_identity(value), "result_id", "result.result_id", issues)
    if with_expected_result_identity(value).canonical_digest != value.canonical_digest:
        issues.append(_issue("result.canonical_digest", GateCompositionValidationCode.IDENTITY_MISMATCH, "canonical digest mismatch"))
    return _report(issues)


def assert_valid_evaluation_input(value: GateCompositionEvaluationInput) -> GateCompositionEvaluationInput:
    report = validate_evaluation_input(value)
    if not report.ok:
        raise GateCompositionValidationError(report)
    return value


def assert_valid_result(value: GateCompositionResult) -> GateCompositionResult:
    report = validate_result(value)
    if not report.ok:
        raise GateCompositionValidationError(report)
    return value
