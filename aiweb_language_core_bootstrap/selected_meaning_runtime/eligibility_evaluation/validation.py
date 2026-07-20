"""Fail-closed validation for Slice 41C selection eligibility."""
from __future__ import annotations

from dataclasses import fields
from typing import Iterable

from ...candidate_meaning_construction.manifest_candidate_integration.schema import (
    CandidateMeaningManifestCompanionV1,
)
from ...meaning_structure_manifest import CandidateMeaningRecord
from ...meaning_structure_manifest.validation import validate_record as validate_msm_record
from ...msm_gate_custody.schema import GateFamilyName, MsmGateCustodyCompanionV1
from ...msm_gate_custody.validation import validate_companion
from ...verbal_cognition_gate_runtime.gate_composition.schema import (
    CandidateNonSelectionDisposition,
    GateCompositionDispositionKind,
    GateCompositionResult,
)
from ...verbal_cognition_gate_runtime.gate_composition.validation import (
    assert_valid_result as assert_valid_composition_result,
)
from ..governed_lifecycle.schema import SelectedMeaningLifecycleStage
from ..governed_lifecycle.validation import assert_valid_governance_bundle
from ..schema import SelectionEligibilityCustodyState
from .authority import SLICE41C_SCHEMA_VERSION
from .identity import (
    expected_evaluation_input_id,
    expected_finding_id,
    expected_result_digest,
    expected_result_id,
)
from .schema import (
    APPROVED_STRICT_PROFILE,
    SelectionEligibilityAuthorityProfile,
    SelectionEligibilityEvaluationInput,
    SelectionEligibilityFinding,
    SelectionEligibilityOutcome,
    SelectionEligibilityResult,
    SelectionEligibilityValidationCode,
    SelectionEligibilityValidationError,
    SelectionEligibilityValidationIssue,
    SelectionEligibilityValidationReport,
)


def _issue(
    path: str,
    code: SelectionEligibilityValidationCode,
    detail: str,
) -> SelectionEligibilityValidationIssue:
    return SelectionEligibilityValidationIssue(path, code, detail)


def _report(
    issues: Iterable[SelectionEligibilityValidationIssue],
) -> SelectionEligibilityValidationReport:
    return SelectionEligibilityValidationReport(tuple(issues))


def _text(value: object, path: str, issues: list[SelectionEligibilityValidationIssue]) -> None:
    if not isinstance(value, str) or not value or value.strip() != value:
        issues.append(_issue(path, SelectionEligibilityValidationCode.INVALID_IDENTIFIER, "non-empty trimmed string required"))


def _tuple_text(
    value: object,
    path: str,
    issues: list[SelectionEligibilityValidationIssue],
    *,
    allow_empty: bool = True,
) -> None:
    if not isinstance(value, tuple):
        issues.append(_issue(path, SelectionEligibilityValidationCode.TYPE_MISMATCH, "tuple required"))
        return
    if not allow_empty and not value:
        issues.append(_issue(path, SelectionEligibilityValidationCode.RECORD_INVALID, "non-empty tuple required"))
    if len(value) != len(set(value)):
        issues.append(_issue(path, SelectionEligibilityValidationCode.DUPLICATE_ID, "duplicate references are prohibited"))
    for index, item in enumerate(value):
        _text(item, f"{path}[{index}]", issues)


def _false_flags(
    value: object,
    names: tuple[str, ...],
    issues: list[SelectionEligibilityValidationIssue],
) -> None:
    for name in names:
        if getattr(value, name, None) is not False:
            issues.append(_issue(name, SelectionEligibilityValidationCode.PROHIBITED_STRATEGY, "must remain false"))


def validate_authority_profile(value: object) -> SelectionEligibilityValidationReport:
    issues: list[SelectionEligibilityValidationIssue] = []
    if not isinstance(value, SelectionEligibilityAuthorityProfile):
        return _report((_issue("profile", SelectionEligibilityValidationCode.TYPE_MISMATCH, "SelectionEligibilityAuthorityProfile required"),))
    if value != APPROVED_STRICT_PROFILE:
        issues.append(_issue("profile", SelectionEligibilityValidationCode.PROFILE_NOT_APPROVED, "profile must exactly equal the approved strict candidate-specific profile"))
    if value.schema_version != SLICE41C_SCHEMA_VERSION:
        issues.append(_issue("profile.schema_version", SelectionEligibilityValidationCode.INVALID_VERSION, "unknown profile schema version"))
    if tuple(value.permitted_outcomes) != tuple(SelectionEligibilityOutcome):
        issues.append(_issue("profile.permitted_outcomes", SelectionEligibilityValidationCode.PROFILE_NOT_APPROVED, "exact outcome set required"))
    _false_flags(
        value,
        (
            "candidate_ranking_allowed",
            "confidence_scoring_allowed",
            "probability_ranking_allowed",
            "semantic_similarity_allowed",
            "nearest_known_substitution_allowed",
            "language_model_allowed",
            "hidden_classifier_allowed",
            "automatic_only_candidate_eligibility_allowed",
            "automatic_first_candidate_eligibility_allowed",
            "automatic_safest_candidate_eligibility_allowed",
            "selected_meaning_construction_allowed",
            "msm_v1_mutation_allowed",
            "downstream_authority_allowed",
        ),
        issues,
    )
    return _report(issues)


def _validate_manifest_companion(
    value: object,
    issues: list[SelectionEligibilityValidationIssue],
) -> None:
    if not isinstance(value, CandidateMeaningManifestCompanionV1):
        issues.append(_issue("manifest_candidate_companion", SelectionEligibilityValidationCode.TYPE_MISMATCH, "CandidateMeaningManifestCompanionV1 required"))
        return
    for name in (
        "companion_id",
        "manifest_candidate_record_id",
        "candidate_meaning_id",
        "candidate_lineage_id",
        "candidate_state_id",
        "candidate_identity_ref",
        "candidate_content_ref",
        "candidate_provenance_ref",
        "construction_receipt_ref",
    ):
        _text(getattr(value, name), f"manifest_candidate_companion.{name}", issues)
    if not (value.exact_adapter and value.lossless_custody and value.candidate_side_only):
        issues.append(_issue("manifest_candidate_companion", SelectionEligibilityValidationCode.RECORD_INVALID, "exact lossless candidate-side companion required"))
    if value.selected_meaning_created or value.gate_outcome_created:
        issues.append(_issue("manifest_candidate_companion", SelectionEligibilityValidationCode.DOWNSTREAM_AUTHORITY, "predecessor companion contains prohibited outcome authority"))


def _family_map(value: MsmGateCustodyCompanionV1):
    return {record.family: record for record in value.family_custody}


def validate_evaluation_input(value: object) -> SelectionEligibilityValidationReport:
    issues: list[SelectionEligibilityValidationIssue] = []
    if not isinstance(value, SelectionEligibilityEvaluationInput):
        return _report((_issue("input", SelectionEligibilityValidationCode.TYPE_MISMATCH, "SelectionEligibilityEvaluationInput required"),))

    if value.schema_version != SLICE41C_SCHEMA_VERSION:
        issues.append(_issue("schema_version", SelectionEligibilityValidationCode.INVALID_VERSION, "unknown Slice 41C schema version"))
    _text(value.evaluation_input_id, "evaluation_input_id", issues)
    if value.evaluation_input_id != expected_evaluation_input_id(value):
        issues.append(_issue("evaluation_input_id", SelectionEligibilityValidationCode.IDENTITY_MISMATCH, "deterministic input identity mismatch"))

    try:
        assert_valid_governance_bundle(value.governance_bundle)
    except Exception as error:
        issues.append(_issue("governance_bundle", SelectionEligibilityValidationCode.RECORD_INVALID, str(error)))
    else:
        bundle = value.governance_bundle
        if bundle.lifecycle_record.stage is not SelectedMeaningLifecycleStage.RECORD_SEALED:
            issues.append(_issue("governance_bundle.lifecycle_record.stage", SelectionEligibilityValidationCode.RECORD_INVALID, "sealed Slice 41B lifecycle required"))
        if not bundle.validation_only or bundle.eligibility_evaluated:
            issues.append(_issue("governance_bundle", SelectionEligibilityValidationCode.RECORD_INVALID, "validated but unevaluated 41B bundle required"))

    if not isinstance(value.manifest_candidate_record, CandidateMeaningRecord):
        issues.append(_issue("manifest_candidate_record", SelectionEligibilityValidationCode.TYPE_MISMATCH, "CandidateMeaningRecord required"))
    else:
        msm_report = validate_msm_record(value.manifest_candidate_record)
        if not msm_report.ok:
            issues.append(_issue("manifest_candidate_record", SelectionEligibilityValidationCode.RECORD_INVALID, "MSM-v1 candidate record validation failed"))

    _validate_manifest_companion(value.manifest_candidate_companion, issues)

    if not isinstance(value.msm_gate_custody_companion, MsmGateCustodyCompanionV1):
        issues.append(_issue("msm_gate_custody_companion", SelectionEligibilityValidationCode.TYPE_MISMATCH, "MsmGateCustodyCompanionV1 required"))
    else:
        report = validate_companion(value.msm_gate_custody_companion)
        if not report.ok:
            issues.append(_issue("msm_gate_custody_companion", SelectionEligibilityValidationCode.RECORD_INVALID, "Slice 40H companion validation failed"))

    if not isinstance(value.gate_composition_result, GateCompositionResult):
        issues.append(_issue("gate_composition_result", SelectionEligibilityValidationCode.TYPE_MISMATCH, "GateCompositionResult required"))
    else:
        try:
            assert_valid_composition_result(value.gate_composition_result)
        except Exception as error:
            issues.append(_issue("gate_composition_result", SelectionEligibilityValidationCode.RECORD_INVALID, str(error)))

    profile_report = validate_authority_profile(value.authority_profile)
    issues.extend(profile_report.issues)

    for name in (
        "explicit_positive_support_refs",
        "explicit_not_eligible_refs",
        "authority_profile_refs",
        "trace_refs",
        "provenance_refs",
        "version_refs",
    ):
        _tuple_text(getattr(value, name), name, issues, allow_empty=name in ("explicit_positive_support_refs", "explicit_not_eligible_refs"))

    if value.authority_profile.profile_id not in value.authority_profile_refs:
        issues.append(_issue("authority_profile_refs", SelectionEligibilityValidationCode.PROFILE_NOT_APPROVED, "approved profile ID must be explicitly referenced"))

    if not isinstance(value.candidate_dispositions, tuple):
        issues.append(_issue("candidate_dispositions", SelectionEligibilityValidationCode.TYPE_MISMATCH, "tuple of CandidateNonSelectionDisposition records required"))
    elif not all(isinstance(item, CandidateNonSelectionDisposition) for item in value.candidate_dispositions):
        issues.append(_issue("candidate_dispositions", SelectionEligibilityValidationCode.TYPE_MISMATCH, "CandidateNonSelectionDisposition records required"))
    elif (
        isinstance(value.gate_composition_result, GateCompositionResult)
        and value.gate_composition_result.composition_status.value == "composition_complete"
        and not value.candidate_dispositions
    ):
        issues.append(_issue("candidate_dispositions", SelectionEligibilityValidationCode.DISPOSITION_MISMATCH, "completed composition requires explicit candidate-specific dispositions"))

    _false_flags(
        value,
        (
            "candidate_ranking_used",
            "confidence_scoring_used",
            "probability_ranking_used",
            "semantic_similarity_used",
            "nearest_known_substitution_used",
            "language_model_used",
            "hidden_classifier_used",
            "only_candidate_automatic_eligibility_used",
            "first_candidate_automatic_eligibility_used",
            "safest_candidate_automatic_eligibility_used",
            "refusal_relevance_erased",
            "blocked_progression_erased",
            "unresolved_alternatives_erased",
            "understood_meaning_converted_to_permission",
        ),
        issues,
    )

    if issues and not hasattr(value, "governance_bundle"):
        return _report(issues)

    try:
        runtime = value.governance_bundle.runtime_schema_record
        candidate = runtime.selection_candidate_custody
        gate = runtime.gate_custody_reference
        alternative = runtime.alternative_candidate_custody
        unresolved = runtime.unresolved_state_custody
        limitation = runtime.inherited_limitation_custody
        prior = runtime.selection_eligibility_status
        manifest_record = value.manifest_candidate_record
        manifest_companion = value.manifest_candidate_companion
        custody = value.msm_gate_custody_companion
        composition = value.gate_composition_result
    except Exception as error:
        issues.append(_issue("cross_records", SelectionEligibilityValidationCode.RECORD_INVALID, str(error)))
        return _report(issues)

    if (
        manifest_record.record_id != manifest_companion.manifest_candidate_record_id
        or manifest_record.lineage_id != manifest_companion.candidate_lineage_id
        or candidate.source_expression_ref != manifest_record.source_expression_ref
        or candidate.candidate_meaning_id != manifest_companion.candidate_meaning_id
        or candidate.candidate_state_id != manifest_companion.candidate_state_id
        or candidate.candidate_lineage_id != manifest_companion.candidate_lineage_id
        or candidate.manifest_candidate_record_ref != manifest_companion.manifest_candidate_record_id
        or candidate.manifest_candidate_companion_ref != manifest_companion.companion_id
        or candidate.candidate_identity_ref != manifest_companion.candidate_identity_ref
        or candidate.candidate_content_ref != manifest_companion.candidate_content_ref
        or candidate.candidate_provenance_ref != manifest_companion.candidate_provenance_ref
        or candidate.candidate_construction_receipt_ref != manifest_companion.construction_receipt_ref
    ):
        issues.append(_issue("candidate", SelectionEligibilityValidationCode.EXACT_CANDIDATE_MISMATCH, "41A custody and exact MSM candidate companion do not match"))

    if (
        custody.manifest_candidate_ref != manifest_companion.manifest_candidate_record_id
        or custody.candidate_input_ref != candidate.gate_candidate_input_ref
        or composition.candidate_input_ref != candidate.gate_candidate_input_ref
        or custody.candidate_input_ref != composition.candidate_input_ref
    ):
        issues.append(_issue("candidate_input_ref", SelectionEligibilityValidationCode.EXACT_CANDIDATE_MISMATCH, "candidate-specific gate ancestry mismatch"))

    if gate.msm_gate_custody_companion_ref != custody.companion_id:
        issues.append(_issue("gate_custody_reference.msm_gate_custody_companion_ref", SelectionEligibilityValidationCode.GATE_CUSTODY_MISMATCH, "exact Slice 40H companion reference required"))
    if gate.composition_result_ref != composition.result_id or custody.composition_result_id != composition.result_id:
        issues.append(_issue("composition_result_ref", SelectionEligibilityValidationCode.COMPOSITION_RESULT_MISMATCH, "exact Slice 40G result reference required"))
    if custody.composition_result_digest != composition.canonical_digest or custody.composition_status != composition.composition_status.value:
        issues.append(_issue("composition_result", SelectionEligibilityValidationCode.COMPOSITION_RESULT_MISMATCH, "Slice 40H preserved composition does not exactly match Slice 40G"))

    families = _family_map(custody) if isinstance(custody, MsmGateCustodyCompanionV1) else {}
    expected_family_ids = {
        GateFamilyName.EXPECTANCY: composition.expectancy_result_id,
        GateFamilyName.CONGRUITY: composition.congruity_result_id,
        GateFamilyName.CONNECTEDNESS: composition.connectedness_result_id,
        GateFamilyName.RECOVERABLE_PURPOSE: composition.recoverable_purpose_result_id,
    }
    expected_gate_refs = {
        GateFamilyName.EXPECTANCY: gate.expectancy_result_ref,
        GateFamilyName.CONGRUITY: gate.congruity_result_ref,
        GateFamilyName.CONNECTEDNESS: gate.connectedness_result_ref,
        GateFamilyName.RECOVERABLE_PURPOSE: gate.recoverable_purpose_result_ref,
    }
    if set(families) != set(GateFamilyName):
        issues.append(_issue("family_custody", SelectionEligibilityValidationCode.FAMILY_RESULT_MISMATCH, "exact four gate families required"))
    else:
        for family, expected in expected_family_ids.items():
            record = families[family]
            if record.result_id != expected or expected_gate_refs[family] != expected or not record.preserved_exactly:
                issues.append(_issue(f"family_custody.{family.value}", SelectionEligibilityValidationCode.FAMILY_RESULT_MISMATCH, "exact preserved family result mismatch"))

    composition_ids = tuple(item.disposition_id for item in composition.dispositions)
    disposition_ids = tuple(item.disposition_id for item in value.candidate_dispositions)
    if len(disposition_ids) != len(set(disposition_ids)):
        issues.append(_issue("candidate_dispositions", SelectionEligibilityValidationCode.DUPLICATE_ID, "duplicate disposition IDs"))
    if disposition_ids != composition_ids:
        issues.append(_issue("candidate_dispositions", SelectionEligibilityValidationCode.DISPOSITION_MISMATCH, "evaluation dispositions must exactly equal the ordered Slice 40G dispositions"))
    if tuple(gate.candidate_specific_disposition_refs) != disposition_ids:
        issues.append(_issue("gate_custody_reference.candidate_specific_disposition_refs", SelectionEligibilityValidationCode.DISPOSITION_MISMATCH, "41A candidate-specific disposition references must exactly match evaluation dispositions"))
    for index, disposition in enumerate(value.candidate_dispositions):
        if disposition.candidate_input_ref != candidate.gate_candidate_input_ref or disposition.candidate_branch_ref != composition.candidate_branch_ref or not disposition.non_selection_only:
            issues.append(_issue(f"candidate_dispositions[{index}]", SelectionEligibilityValidationCode.DISPOSITION_MISMATCH, "disposition is not exact candidate-specific non-selection custody"))

    positive_support_authority = {
        reference
        for disposition in value.candidate_dispositions
        if disposition.disposition_kind is GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW
        for reference in (disposition.disposition_id, *disposition.reason_refs)
    }
    if value.explicit_positive_support_refs and not set(value.explicit_positive_support_refs).issubset(positive_support_authority):
        issues.append(_issue("explicit_positive_support_refs", SelectionEligibilityValidationCode.DISPOSITION_MISMATCH, "positive support must resolve to the exact candidate-specific positive disposition or its reason records"))

    if alternative.selection_candidate_custody_ref != candidate.selection_candidate_custody_id:
        issues.append(_issue("alternative_candidate_custody", SelectionEligibilityValidationCode.ALTERNATIVE_CUSTODY_MISMATCH, "candidate reference mismatch"))
    if unresolved.selection_candidate_custody_ref != candidate.selection_candidate_custody_id:
        issues.append(_issue("unresolved_state_custody", SelectionEligibilityValidationCode.UNRESOLVED_CUSTODY_MISMATCH, "candidate reference mismatch"))
    if limitation.selection_candidate_custody_ref != candidate.selection_candidate_custody_id:
        issues.append(_issue("inherited_limitation_custody", SelectionEligibilityValidationCode.LIMITATION_CUSTODY_MISMATCH, "candidate reference mismatch"))
    if prior.selection_candidate_custody_ref != candidate.selection_candidate_custody_id or prior.custody_state is not SelectionEligibilityCustodyState.READY_FOR_LATER_EVALUATION or prior.eligibility_evaluated:
        issues.append(_issue("prior_eligibility_status", SelectionEligibilityValidationCode.RECORD_INVALID, "41A status must be ready and unevaluated"))

    requirement_profile_refs = {
        ref
        for requirement in runtime.selection_authority_requirements
        for ref in requirement.required_authority_profile_refs
    }
    if value.authority_profile.profile_id not in requirement_profile_refs:
        issues.append(_issue("selection_authority_requirements", SelectionEligibilityValidationCode.AUTHORITY_REQUIREMENT_MISMATCH, "approved profile must be required by exact candidate authority custody"))
    for index, requirement in enumerate(runtime.selection_authority_requirements):
        if requirement.selection_candidate_custody_ref != candidate.selection_candidate_custody_id or requirement.gate_custody_reference_ref != gate.gate_custody_reference_id:
            issues.append(_issue(f"selection_authority_requirements[{index}]", SelectionEligibilityValidationCode.AUTHORITY_REQUIREMENT_MISMATCH, "candidate or gate reference mismatch"))

    return _report(issues)


def assert_valid_evaluation_input(
    value: SelectionEligibilityEvaluationInput,
) -> SelectionEligibilityEvaluationInput:
    report = validate_evaluation_input(value)
    if not report.ok:
        raise SelectionEligibilityValidationError(report)
    return value


def validate_finding(value: object) -> SelectionEligibilityValidationReport:
    issues: list[SelectionEligibilityValidationIssue] = []
    if not isinstance(value, SelectionEligibilityFinding):
        return _report((_issue("finding", SelectionEligibilityValidationCode.TYPE_MISMATCH, "SelectionEligibilityFinding required"),))
    for name in ("finding_id", "evaluation_input_ref", "candidate_meaning_ref"):
        _text(getattr(value, name), name, issues)
    for name in ("basis_refs", "reason_refs", "trace_refs", "provenance_refs"):
        _tuple_text(getattr(value, name), name, issues)
    if value.finding_id != expected_finding_id(value):
        issues.append(_issue("finding_id", SelectionEligibilityValidationCode.IDENTITY_MISMATCH, "finding identity mismatch"))
    if value.schema_version != SLICE41C_SCHEMA_VERSION:
        issues.append(_issue("schema_version", SelectionEligibilityValidationCode.INVALID_VERSION, "unknown finding schema version"))
    return _report(issues)


def validate_result(
    value: object,
    *,
    evaluation_input: SelectionEligibilityEvaluationInput | None = None,
) -> SelectionEligibilityValidationReport:
    issues: list[SelectionEligibilityValidationIssue] = []
    if not isinstance(value, SelectionEligibilityResult):
        return _report((_issue("result", SelectionEligibilityValidationCode.TYPE_MISMATCH, "SelectionEligibilityResult required"),))
    for name in (
        "result_id",
        "evaluation_input_ref",
        "selection_candidate_custody_ref",
        "candidate_meaning_ref",
        "candidate_lineage_ref",
        "manifest_candidate_record_ref",
        "manifest_candidate_companion_ref",
        "msm_gate_custody_companion_ref",
        "gate_composition_result_ref",
        "authority_profile_ref",
        "canonical_digest",
    ):
        _text(getattr(value, name), name, issues)
    if value.schema_version != SLICE41C_SCHEMA_VERSION:
        issues.append(_issue("schema_version", SelectionEligibilityValidationCode.INVALID_VERSION, "unknown result schema version"))
    if value.result_id != expected_result_id(value) or value.canonical_digest != expected_result_digest(value):
        issues.append(_issue("result_identity", SelectionEligibilityValidationCode.IDENTITY_MISMATCH, "deterministic result identity mismatch"))
    if len(value.findings) != len({item.finding_id for item in value.findings}):
        issues.append(_issue("findings", SelectionEligibilityValidationCode.DUPLICATE_ID, "duplicate finding IDs"))
    for index, finding in enumerate(value.findings):
        report = validate_finding(finding)
        for issue in report.issues:
            issues.append(_issue(f"findings[{index}].{issue.path}", issue.code, issue.detail))
    if not all((value.deterministic, value.candidate_specific, value.exact_msm_candidate_verified, value.exact_slice40h_companion_verified, value.all_four_gate_results_verified, value.exact_slice40g_composition_verified, value.approved_authority_profile_verified, value.alternatives_preserved, value.unresolved_states_preserved, value.refusal_relevance_preserved, value.blocked_progression_preserved, value.inherited_limitations_preserved, value.eligibility_evaluated)):
        issues.append(_issue("result", SelectionEligibilityValidationCode.RECORD_INVALID, "required verification and preservation flags must be true"))
    _false_flags(
        value,
        (
            "candidate_ranked",
            "selection_performed",
            "selected_meaning_created",
            "msm_v1_modified",
            "bootstrap_integration_enabled",
            "truth_determined",
            "evidence_validated",
            "permission_granted",
            "execution_authorized",
            "route_created",
            "tool_invoked",
            "action_performed",
            "memory_accessed",
            "memory_written",
            "rendered",
            "delivered",
            "external_resource_loaded",
            "language_model_used",
            "hidden_classifier_used",
            "confidence_scoring_used",
            "probability_ranking_used",
            "semantic_similarity_used",
            "nearest_known_substitution_used",
            "only_candidate_automatic_eligibility_used",
            "first_candidate_automatic_eligibility_used",
            "safest_candidate_automatic_eligibility_used",
            "refusal_relevance_erased",
            "blocked_progression_erased",
            "unresolved_alternatives_erased",
            "understood_meaning_converted_to_permission",
        ),
        issues,
    )
    if value.eligible_for_selected_meaning_construction != (value.outcome is SelectionEligibilityOutcome.ELIGIBLE_FOR_SELECTED_MEANING_CONSTRUCTION):
        issues.append(_issue("eligible_for_selected_meaning_construction", SelectionEligibilityValidationCode.OUTCOME_MISMATCH, "eligibility flag must exactly match outcome"))

    if evaluation_input is not None:
        input_report = validate_evaluation_input(evaluation_input)
        if not input_report.ok:
            issues.append(_issue("evaluation_input", SelectionEligibilityValidationCode.RECORD_INVALID, "supplied input is invalid"))
        else:
            from .evaluator import determine_outcome
            expected_outcome = determine_outcome(evaluation_input)
            candidate = evaluation_input.selection_candidate_custody
            composition = evaluation_input.gate_composition_result
            expected_dispositions = tuple(item.disposition_id for item in evaluation_input.candidate_dispositions)
            if value.outcome is not expected_outcome:
                issues.append(_issue("outcome", SelectionEligibilityValidationCode.OUTCOME_MISMATCH, "result outcome does not match deterministic rules"))
            expected_refs = (
                value.evaluation_input_ref == evaluation_input.evaluation_input_id,
                value.selection_candidate_custody_ref == candidate.selection_candidate_custody_id,
                value.candidate_meaning_ref == candidate.candidate_meaning_id,
                value.candidate_lineage_ref == candidate.candidate_lineage_id,
                value.manifest_candidate_record_ref == candidate.manifest_candidate_record_ref,
                value.manifest_candidate_companion_ref == evaluation_input.manifest_candidate_companion.companion_id,
                value.msm_gate_custody_companion_ref == evaluation_input.msm_gate_custody_companion.companion_id,
                value.gate_composition_result_ref == composition.result_id,
                value.authority_profile_ref == evaluation_input.authority_profile.profile_id,
                value.preserved_disposition_refs == expected_dispositions,
                value.explicit_positive_support_refs == evaluation_input.explicit_positive_support_refs,
                value.explicit_not_eligible_refs == evaluation_input.explicit_not_eligible_refs,
            )
            if not all(expected_refs):
                issues.append(_issue("cross_record_refs", SelectionEligibilityValidationCode.RECORD_INVALID, "result does not preserve exact input references"))
    return _report(issues)


def assert_valid_result(
    value: SelectionEligibilityResult,
    *,
    evaluation_input: SelectionEligibilityEvaluationInput | None = None,
) -> SelectionEligibilityResult:
    report = validate_result(value, evaluation_input=evaluation_input)
    if not report.ok:
        raise SelectionEligibilityValidationError(report)
    return value


__all__ = (
    "assert_valid_evaluation_input",
    "assert_valid_result",
    "validate_authority_profile",
    "validate_evaluation_input",
    "validate_finding",
    "validate_result",
)
