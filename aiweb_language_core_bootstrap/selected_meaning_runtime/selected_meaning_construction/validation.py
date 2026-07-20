"""Fail-closed validation for Slice 41D construction inputs and packages."""
from __future__ import annotations

from typing import Iterable

from ...meaning_structure_manifest import CandidateMeaningRecord, SelectedGovernedMeaningRecord
from ..eligibility_evaluation import (
    SelectionEligibilityOutcome,
    validate_evaluation_input,
    validate_result as validate_eligibility_result,
)
from .authority import SLICE41D_PERMANENT_BOUNDARIES, SLICE41D_PROHIBITED_AUTHORITY
from .canonical import canonical_json_bytes, deterministic_digest
from .identity import (
    expected_construction_input_id,
    expected_content_proof_id,
    expected_decision_id,
    expected_package_digest,
    expected_package_id,
    expected_preservation_id,
    expected_receipt_id,
    expected_selected_meaning_record_id,
    expected_trace_id,
)
from .schema import (
    APPROVED_SELECTED_MEANING_CONSTRUCTION_PROFILES,
    APPROVED_STRICT_PROFILE,
    PreservedAlternativeCandidateRecord,
    SelectedMeaningConstructionAuthorityProfile,
    SelectedMeaningConstructionInput,
    SelectedMeaningConstructionPackage,
    SelectedMeaningConstructionValidationCode,
    SelectedMeaningConstructionValidationError,
    SelectedMeaningConstructionValidationIssue,
    SelectedMeaningConstructionValidationReport,
    SelectedMeaningContentProof,
    SelectedMeaningDecisionRecord,
    SelectedMeaningSelectionReceiptRecord,
    SelectedMeaningSelectionTraceRecord,
)


def _issue(
    issues: list[SelectedMeaningConstructionValidationIssue],
    path: str,
    code: SelectedMeaningConstructionValidationCode,
    detail: str,
) -> None:
    issues.append(SelectedMeaningConstructionValidationIssue(path, code, detail))


def _report(
    issues: list[SelectedMeaningConstructionValidationIssue],
) -> SelectedMeaningConstructionValidationReport:
    return SelectedMeaningConstructionValidationReport(tuple(issues))


def _text(
    value: object,
    path: str,
    issues: list[SelectedMeaningConstructionValidationIssue],
) -> None:
    if not isinstance(value, str) or not value or value.strip() != value:
        _issue(
            issues,
            path,
            SelectedMeaningConstructionValidationCode.INVALID_IDENTIFIER,
            "must be non-empty trimmed text",
        )


def _tuple_text(
    value: object,
    path: str,
    issues: list[SelectedMeaningConstructionValidationIssue],
    *,
    allow_empty: bool = True,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        _issue(
            issues,
            path,
            SelectedMeaningConstructionValidationCode.TYPE_MISMATCH,
            "must be a tuple",
        )
        return ()
    if not allow_empty and not value:
        _issue(
            issues,
            path,
            SelectedMeaningConstructionValidationCode.INVALID_IDENTIFIER,
            "must not be empty",
        )
    for index, item in enumerate(value):
        _text(item, f"{path}[{index}]", issues)
    if len(value) != len(set(value)):
        _issue(
            issues,
            path,
            SelectedMeaningConstructionValidationCode.DUPLICATE_ID,
            "duplicate values are prohibited",
        )
    return value if all(isinstance(item, str) for item in value) else ()


def _unique(*groups: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for group in groups:
        for value in group:
            if value not in seen:
                seen.add(value)
                ordered.append(value)
    return tuple(ordered)


def _expected_non_selected(value: SelectedMeaningConstructionInput) -> tuple[str, ...]:
    eligibility = value.eligibility_result
    evaluation = value.eligibility_evaluation_input
    candidate = value.selected_candidate_record
    companion = value.selected_candidate_companion
    excluded = {eligibility.candidate_meaning_ref, candidate.record_id, companion.candidate_meaning_id}
    return tuple(
        ref
        for ref in _unique(
            eligibility.preserved_alternative_candidate_refs,
            evaluation.alternative_candidate_custody.preserved_alternative_candidate_refs,
            evaluation.alternative_candidate_custody.non_selected_candidate_refs,
            evaluation.unresolved_state_custody.unresolved_candidate_refs,
        )
        if ref not in excluded
    )


def _expected_unresolved(value: SelectedMeaningConstructionInput) -> tuple[str, ...]:
    eligibility = value.eligibility_result
    unresolved = value.eligibility_evaluation_input.unresolved_state_custody
    return _unique(
        unresolved.unresolved_candidate_refs,
        eligibility.material_ambiguity_refs,
        eligibility.clarification_dependency_refs,
        eligibility.unsupported_refs,
        eligibility.conflicted_refs,
        eligibility.missing_authority_refs,
        eligibility.held_refs,
        eligibility.refusal_relevant_refs,
        eligibility.blocked_progression_refs,
    )


def _expected_ambiguity(value: SelectedMeaningConstructionInput) -> tuple[str, ...]:
    candidate = value.selected_candidate_record
    alternative = value.eligibility_evaluation_input.alternative_candidate_custody
    return _unique(
        value.ambiguity_ancestry_refs,
        candidate.ambiguity_reasons,
        alternative.material_ambiguity_refs,
        value.eligibility_result.material_ambiguity_refs,
    )


def _expected_clarification(value: SelectedMeaningConstructionInput) -> tuple[str, ...]:
    evaluation = value.eligibility_evaluation_input
    return _unique(
        value.clarification_ancestry_refs,
        evaluation.alternative_candidate_custody.clarification_relevant_refs,
        evaluation.unresolved_state_custody.clarification_dependency_refs,
        value.eligibility_result.clarification_dependency_refs,
    )


def _expected_inherited_limitations(
    value: SelectedMeaningConstructionInput,
) -> tuple[str, ...]:
    candidate = value.selected_candidate_record
    eligibility = value.eligibility_result
    custody = value.eligibility_evaluation_input.inherited_limitation_custody
    return _unique(
        candidate.ambiguity_reasons,
        candidate.unresolved_referents,
        eligibility.inherited_limitation_refs,
        custody.source_limitation_refs,
        custody.candidate_limitation_refs,
        custody.gate_limitation_refs,
        custody.effect_boundary_refs,
        custody.domain_sensitive_refs,
        custody.evidence_boundary_refs,
        custody.memory_boundary_refs,
        custody.privacy_boundary_refs,
        custody.delivery_boundary_refs,
        custody.execution_boundary_refs,
        custody.correction_ancestry_refs,
        custody.supersession_ancestry_refs,
        eligibility.blocked_progression_refs,
        eligibility.refusal_relevant_refs,
        eligibility.missing_authority_refs,
        eligibility.held_refs,
        eligibility.unsupported_refs,
        eligibility.conflicted_refs,
    )


def _expected_authority_sensitive(
    value: SelectedMeaningConstructionInput,
) -> tuple[str, ...]:
    custody = value.eligibility_evaluation_input.inherited_limitation_custody
    return _unique(
        value.selected_candidate_record.authority_sensitive_implications,
        custody.authority_sensitive_distinction_refs,
    )


def _expected_blocked(value: SelectedMeaningConstructionInput) -> tuple[str, ...]:
    evaluation = value.eligibility_evaluation_input
    eligibility = value.eligibility_result
    return _unique(
        eligibility.blocked_progression_refs,
        evaluation.unresolved_state_custody.blocked_progression_refs,
        evaluation.inherited_limitation_custody.effect_boundary_refs,
        evaluation.inherited_limitation_custody.execution_boundary_refs,
        evaluation.inherited_limitation_custody.delivery_boundary_refs,
    )


def _expected_refusal(value: SelectedMeaningConstructionInput) -> tuple[str, ...]:
    return _unique(
        value.eligibility_result.refusal_relevant_refs,
        value.eligibility_evaluation_input.unresolved_state_custody.refusal_relevant_refs,
    )


def _expected_alternative_kinds(
    value: SelectedMeaningConstructionInput,
) -> tuple[object, ...]:
    from .schema import PreservedAlternativeKind

    result = value.eligibility_result
    unresolved = value.eligibility_evaluation_input.unresolved_state_custody
    kinds = [PreservedAlternativeKind.NON_SELECTED]
    if unresolved.unresolved_candidate_refs:
        kinds.append(PreservedAlternativeKind.UNRESOLVED)
    if result.material_ambiguity_refs:
        kinds.append(PreservedAlternativeKind.MATERIAL_AMBIGUITY)
    if result.clarification_dependency_refs:
        kinds.append(PreservedAlternativeKind.CLARIFICATION_DEPENDENT)
    if result.unsupported_refs:
        kinds.append(PreservedAlternativeKind.UNSUPPORTED)
    if result.conflicted_refs:
        kinds.append(PreservedAlternativeKind.CONFLICTED)
    if result.held_refs:
        kinds.append(PreservedAlternativeKind.HELD)
    if result.refusal_relevant_refs:
        kinds.append(PreservedAlternativeKind.REFUSAL_RELEVANT)
    if result.blocked_progression_refs:
        kinds.append(PreservedAlternativeKind.BLOCKED_PROGRESSION)
    if value.eligibility_evaluation_input.alternative_candidate_custody.exact_duplicate_group_refs:
        kinds.append(PreservedAlternativeKind.EXACT_DUPLICATE)
    return tuple(kinds)


def _expected_unresolved_reasons(
    value: SelectedMeaningConstructionInput,
) -> tuple[str, ...]:
    result = value.eligibility_result
    return _unique(
        result.material_ambiguity_refs,
        result.clarification_dependency_refs,
        result.unsupported_refs,
        result.conflicted_refs,
        result.missing_authority_refs,
        result.held_refs,
        result.refusal_relevant_refs,
        result.blocked_progression_refs,
    )


def _candidate_semantic(candidate: CandidateMeaningRecord) -> dict[str, object]:
    return {
        "communicative_act": candidate.communicative_act,
        "concept_refs": candidate.concept_refs,
        "relation_refs": candidate.relation_refs,
        "meaning_modifiers": candidate.meaning_modifiers,
        "preservation_classes": candidate.preservation_classes,
    }


def _selected_semantic(selected: SelectedGovernedMeaningRecord) -> dict[str, object]:
    return {
        "communicative_act": selected.communicative_act,
        "concept_refs": selected.concept_refs,
        "relation_refs": selected.relation_refs,
        "meaning_modifiers": selected.meaning_modifiers,
        "preservation_classes": selected.preservation_classes,
    }


def _false_flags(
    value: object,
    names: Iterable[str],
    path: str,
    issues: list[SelectedMeaningConstructionValidationIssue],
) -> None:
    for name in names:
        if getattr(value, name, None) is not False:
            _issue(
                issues,
                f"{path}.{name}",
                SelectedMeaningConstructionValidationCode.DOWNSTREAM_AUTHORITY,
                "must be false",
            )


def validate_authority_profile(
    value: object,
) -> SelectedMeaningConstructionValidationReport:
    issues: list[SelectedMeaningConstructionValidationIssue] = []
    if not isinstance(value, SelectedMeaningConstructionAuthorityProfile):
        _issue(
            issues,
            "profile",
            SelectedMeaningConstructionValidationCode.TYPE_MISMATCH,
            "wrong authority-profile type",
        )
        return _report(issues)
    if value not in APPROVED_SELECTED_MEANING_CONSTRUCTION_PROFILES or value != APPROVED_STRICT_PROFILE:
        _issue(
            issues,
            "profile",
            SelectedMeaningConstructionValidationCode.PROFILE_NOT_APPROVED,
            "profile is not the exact approved Slice 41D profile",
        )
    for name in (
        "candidate_ranking_allowed",
        "confidence_scoring_allowed",
        "probability_ranking_allowed",
        "semantic_similarity_allowed",
        "nearest_known_substitution_allowed",
        "language_model_allowed",
        "hidden_classifier_allowed",
        "automatic_only_candidate_selection_allowed",
        "automatic_first_candidate_selection_allowed",
        "automatic_safest_candidate_selection_allowed",
        "msm_v1_mutation_allowed",
        "outward_meaning_allowed",
        "truth_evidence_permission_execution_allowed",
        "route_tool_action_memory_rendering_delivery_allowed",
    ):
        if getattr(value, name) is not False:
            _issue(
                issues,
                f"profile.{name}",
                SelectedMeaningConstructionValidationCode.PROHIBITED_STRATEGY,
                "must be false",
            )
    return _report(issues)


def validate_construction_input(
    value: object,
) -> SelectedMeaningConstructionValidationReport:
    issues: list[SelectedMeaningConstructionValidationIssue] = []
    if not isinstance(value, SelectedMeaningConstructionInput):
        _issue(
            issues,
            "input",
            SelectedMeaningConstructionValidationCode.TYPE_MISMATCH,
            "wrong construction-input type",
        )
        return _report(issues)

    profile_report = validate_authority_profile(value.authority_profile)
    issues.extend(profile_report.issues)
    eligibility_input_report = validate_evaluation_input(value.eligibility_evaluation_input)
    if not eligibility_input_report.ok:
        _issue(
            issues,
            "input.eligibility_evaluation_input",
            SelectedMeaningConstructionValidationCode.ELIGIBILITY_MISMATCH,
            "Slice 41C evaluation input is invalid",
        )
    eligibility_report = validate_eligibility_result(
        value.eligibility_result,
        evaluation_input=value.eligibility_evaluation_input,
    )
    if not eligibility_report.ok:
        _issue(
            issues,
            "input.eligibility_result",
            SelectedMeaningConstructionValidationCode.ELIGIBILITY_MISMATCH,
            "Slice 41C eligibility result is invalid for the supplied input",
        )

    result = value.eligibility_result
    evaluation = value.eligibility_evaluation_input
    candidate = value.selected_candidate_record
    companion = value.selected_candidate_companion
    if (
        result.outcome is not SelectionEligibilityOutcome.ELIGIBLE_FOR_SELECTED_MEANING_CONSTRUCTION
        or result.eligible_for_selected_meaning_construction is not True
        or result.eligibility_evaluated is not True
    ):
        _issue(
            issues,
            "input.eligibility_result.outcome",
            SelectedMeaningConstructionValidationCode.ELIGIBILITY_NOT_SUCCESSFUL,
            "exact successful Slice 41C eligibility is required",
        )
    if result.selection_performed or result.selected_meaning_created or result.msm_v1_modified:
        _issue(
            issues,
            "input.eligibility_result",
            SelectedMeaningConstructionValidationCode.DOWNSTREAM_AUTHORITY,
            "Slice 41C result must remain pre-selection and pre-MSM-mutation",
        )
    if result.candidate_meaning_ref != companion.candidate_meaning_id:
        _issue(
            issues,
            "input.selected_candidate_companion.candidate_meaning_id",
            SelectedMeaningConstructionValidationCode.CANDIDATE_MISMATCH,
            "candidate identity does not match eligibility result",
        )
    if result.manifest_candidate_record_ref != candidate.record_id:
        _issue(
            issues,
            "input.selected_candidate_record.record_id",
            SelectedMeaningConstructionValidationCode.CANDIDATE_MISMATCH,
            "manifest candidate record does not match eligibility result",
        )
    if result.manifest_candidate_companion_ref != companion.companion_id:
        _issue(
            issues,
            "input.selected_candidate_companion.companion_id",
            SelectedMeaningConstructionValidationCode.CANDIDATE_MISMATCH,
            "candidate companion does not match eligibility result",
        )
    if candidate.lineage_id != result.candidate_lineage_ref or companion.candidate_lineage_id != candidate.lineage_id:
        _issue(
            issues,
            "input.selected_candidate_record.lineage_id",
            SelectedMeaningConstructionValidationCode.LINEAGE_MISMATCH,
            "selected candidate lineage is not exact",
        )
    if evaluation.manifest_candidate_record != candidate or evaluation.manifest_candidate_companion != companion:
        _issue(
            issues,
            "input.eligibility_evaluation_input",
            SelectedMeaningConstructionValidationCode.CANDIDATE_MISMATCH,
            "selected candidate objects are not the exact Slice 41C objects",
        )

    _tuple_text(value.selection_reason_refs, "input.selection_reason_refs", issues, allow_empty=False)
    _tuple_text(value.ambiguity_ancestry_refs, "input.ambiguity_ancestry_refs", issues)
    _tuple_text(value.clarification_ancestry_refs, "input.clarification_ancestry_refs", issues)
    _tuple_text(value.trace_refs, "input.trace_refs", issues, allow_empty=False)
    _tuple_text(value.provenance_refs, "input.provenance_refs", issues, allow_empty=False)
    _tuple_text(value.version_refs, "input.version_refs", issues, allow_empty=False)

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
            "only_candidate_automatic_selection_used",
            "first_candidate_automatic_selection_used",
            "safest_candidate_automatic_selection_used",
            "alternative_erasure_requested",
            "unresolved_alternative_erasure_requested",
            "ambiguity_ancestry_erasure_requested",
            "clarification_ancestry_erasure_requested",
            "refusal_relevance_erasure_requested",
            "blocked_progression_erasure_requested",
            "msm_v1_mutation_requested",
            "outward_meaning_requested",
            "downstream_authority_requested",
        ),
        "input",
        issues,
    )

    if value.construction_input_id != expected_construction_input_id(value):
        _issue(
            issues,
            "input.construction_input_id",
            SelectedMeaningConstructionValidationCode.IDENTITY_MISMATCH,
            "construction input ID is not canonical",
        )
    return _report(issues)


def assert_valid_construction_input(value: object) -> None:
    report = validate_construction_input(value)
    if not report.ok:
        raise SelectedMeaningConstructionValidationError(report)


def _validate_decision(
    record: SelectedMeaningDecisionRecord,
    value: SelectedMeaningConstructionInput,
    issues: list[SelectedMeaningConstructionValidationIssue],
) -> None:
    candidate = value.selected_candidate_record
    companion = value.selected_candidate_companion
    eligibility = value.eligibility_result
    exact_fields = {
        "construction_input_ref": value.construction_input_id,
        "eligibility_result_ref": eligibility.result_id,
        "selected_candidate_ref": eligibility.candidate_meaning_ref,
        "selected_candidate_lineage_ref": candidate.lineage_id,
        "selected_manifest_candidate_record_ref": candidate.record_id,
        "selected_manifest_candidate_companion_ref": companion.companion_id,
        "selection_authority_profile_ref": value.authority_profile.profile_id,
        "selection_reason_refs": value.selection_reason_refs,
        "non_selected_candidate_refs": _expected_non_selected(value),
        "unresolved_alternative_refs": _expected_unresolved(value),
        "ambiguity_ancestry_refs": _expected_ambiguity(value),
        "clarification_ancestry_refs": _expected_clarification(value),
    }
    if record.decision_id != expected_decision_id(record):
        _issue(issues, "package.decision_record.decision_id", SelectedMeaningConstructionValidationCode.IDENTITY_MISMATCH, "decision ID mismatch")
    for name, expected in exact_fields.items():
        if getattr(record, name) != expected:
            _issue(issues, f"package.decision_record.{name}", SelectedMeaningConstructionValidationCode.CANONICAL_MISMATCH, "decision custody field is not exact")
    if record.decision_performed is not True or record.candidate_ranked is not False:
        _issue(issues, "package.decision_record", SelectedMeaningConstructionValidationCode.PROHIBITED_STRATEGY, "decision must be exact and unranked")
    if record.only_candidate_claimed or record.historical_candidate_exhaustiveness_claimed:
        _issue(issues, "package.decision_record", SelectedMeaningConstructionValidationCode.ALTERNATIVE_CUSTODY_MISMATCH, "must not claim the selected candidate was the only candidate ever")


def _validate_content_proof(
    proof: SelectedMeaningContentProof,
    candidate: CandidateMeaningRecord,
    selected: SelectedGovernedMeaningRecord,
    construction_input: SelectedMeaningConstructionInput,
    issues: list[SelectedMeaningConstructionValidationIssue],
) -> None:
    if proof.proof_id != expected_content_proof_id(proof):
        _issue(issues, "package.content_proof.proof_id", SelectedMeaningConstructionValidationCode.IDENTITY_MISMATCH, "content proof ID mismatch")
    exact_refs = {
        "construction_input_ref": construction_input.construction_input_id,
        "selected_candidate_ref": candidate.record_id,
        "selected_meaning_ref": selected.record_id,
    }
    for name, expected in exact_refs.items():
        if getattr(proof, name) != expected:
            _issue(issues, f"package.content_proof.{name}", SelectedMeaningConstructionValidationCode.CANONICAL_MISMATCH, "content-proof custody field is not exact")
    candidate_mapping = _candidate_semantic(candidate)
    selected_mapping = _selected_semantic(selected)
    candidate_digest = deterministic_digest(canonical_json_bytes(candidate_mapping))
    selected_digest = deterministic_digest(canonical_json_bytes(selected_mapping))
    if proof.candidate_semantic_digest != candidate_digest or proof.selected_semantic_digest != selected_digest:
        _issue(issues, "package.content_proof", SelectedMeaningConstructionValidationCode.CANONICAL_MISMATCH, "semantic digest mismatch")
    if candidate_mapping != selected_mapping:
        _issue(issues, "package.selected_meaning_record", SelectedMeaningConstructionValidationCode.SEMANTIC_CONTENT_MISMATCH, "selected semantic content is not an exact copy")
    exact_flags = (
        proof.communicative_act_exact, proof.concept_refs_exact, proof.relation_refs_exact,
        proof.meaning_modifiers_exact, proof.preservation_classes_exact,
        proof.candidate_identity_exact, proof.candidate_lineage_exact,
        proof.semantic_content_exact,
    )
    if not all(flag is True for flag in exact_flags):
        _issue(issues, "package.content_proof", SelectedMeaningConstructionValidationCode.SEMANTIC_CONTENT_MISMATCH, "all exact-copy proof flags must be true")
    expected_empty_fields = (
        proof.added_concept_refs, proof.removed_concept_refs,
        proof.added_relation_refs, proof.removed_relation_refs,
        proof.added_meaning_modifiers, proof.removed_meaning_modifiers,
        proof.added_preservation_classes, proof.removed_preservation_classes,
    )
    if any(expected_empty_fields) or proof.semantic_enrichment_detected:
        _issue(issues, "package.content_proof", SelectedMeaningConstructionValidationCode.SEMANTIC_ENRICHMENT, "semantic enrichment is prohibited")
    if any(expected_empty_fields) or proof.semantic_deletion_detected:
        _issue(issues, "package.content_proof", SelectedMeaningConstructionValidationCode.SEMANTIC_DELETION, "semantic deletion is prohibited")


def _validate_preserved_alternatives(
    records: tuple[PreservedAlternativeCandidateRecord, ...],
    value: SelectedMeaningConstructionInput,
    issues: list[SelectedMeaningConstructionValidationIssue],
) -> None:
    expected = _expected_non_selected(value)
    observed = tuple(item.alternative_candidate_ref for item in records if isinstance(item, PreservedAlternativeCandidateRecord))
    if observed != expected:
        _issue(issues, "package.preserved_alternatives", SelectedMeaningConstructionValidationCode.ALTERNATIVE_CUSTODY_MISMATCH, "every non-selected candidate must be preserved exactly once and in deterministic order")
    if len(observed) != len(set(observed)):
        _issue(issues, "package.preserved_alternatives", SelectedMeaningConstructionValidationCode.DUPLICATE_ID, "duplicate alternative refs")
    custody = value.eligibility_evaluation_input.alternative_candidate_custody
    exact_shared = {
        "construction_input_ref": value.construction_input_id,
        "selected_candidate_ref": value.selected_candidate_record.record_id,
        "preservation_kinds": _expected_alternative_kinds(value),
        "alternative_relationship_refs": custody.alternative_relationship_refs,
        "disposition_refs": custody.alternative_disposition_refs,
        "unresolved_reason_refs": _expected_unresolved_reasons(value),
        "ambiguity_ancestry_refs": _expected_ambiguity(value),
        "clarification_ancestry_refs": _expected_clarification(value),
        "shared_ancestry_refs": custody.shared_ancestry_refs,
        "exact_duplicate_group_refs": custody.exact_duplicate_group_refs,
    }
    for index, record in enumerate(records):
        if not isinstance(record, PreservedAlternativeCandidateRecord):
            _issue(issues, f"package.preserved_alternatives[{index}]", SelectedMeaningConstructionValidationCode.TYPE_MISMATCH, "wrong preservation record type")
            continue
        if record.preservation_id != expected_preservation_id(record):
            _issue(issues, f"package.preserved_alternatives[{index}].preservation_id", SelectedMeaningConstructionValidationCode.IDENTITY_MISMATCH, "preservation ID mismatch")
        for name, expected_value in exact_shared.items():
            if getattr(record, name) != expected_value:
                _issue(issues, f"package.preserved_alternatives[{index}].{name}", SelectedMeaningConstructionValidationCode.ALTERNATIVE_CUSTODY_MISMATCH, "alternative custody field is not exact")
        if index < len(expected) and record.alternative_candidate_ref != expected[index]:
            _issue(issues, f"package.preserved_alternatives[{index}].alternative_candidate_ref", SelectedMeaningConstructionValidationCode.ALTERNATIVE_CUSTODY_MISMATCH, "alternative candidate reference is not exact")
        if record.selected or record.deleted or record.ranked or record.confidence_scored or not record.preserved_by_exact_reference:
            _issue(issues, f"package.preserved_alternatives[{index}]", SelectedMeaningConstructionValidationCode.ALTERNATIVE_ERASED, "alternative must remain exact, unselected, undeleted, unranked, and unscored")



def validate_package(
    value: object,
    *,
    construction_input: SelectedMeaningConstructionInput | None = None,
) -> SelectedMeaningConstructionValidationReport:
    issues: list[SelectedMeaningConstructionValidationIssue] = []
    if not isinstance(value, SelectedMeaningConstructionPackage):
        _issue(issues, "package", SelectedMeaningConstructionValidationCode.TYPE_MISMATCH, "wrong package type")
        return _report(issues)
    if construction_input is None:
        _issue(issues, "construction_input", SelectedMeaningConstructionValidationCode.TYPE_MISMATCH, "exact construction input is required")
        return _report(issues)
    input_report = validate_construction_input(construction_input)
    issues.extend(input_report.issues)

    candidate = construction_input.selected_candidate_record
    companion = construction_input.selected_candidate_companion
    selected = value.selected_meaning_record
    if value.selected_candidate_record != candidate or value.selected_candidate_companion != companion:
        _issue(issues, "package.selected_candidate_record", SelectedMeaningConstructionValidationCode.CANDIDATE_MISMATCH, "package does not preserve exact selected candidate and companion")
    if not isinstance(selected, SelectedGovernedMeaningRecord):
        _issue(issues, "package.selected_meaning_record", SelectedMeaningConstructionValidationCode.TYPE_MISMATCH, "wrong selected meaning record type")
    else:
        if selected.record_id != expected_selected_meaning_record_id(selected):
            _issue(issues, "package.selected_meaning_record.record_id", SelectedMeaningConstructionValidationCode.IDENTITY_MISMATCH, "selected meaning ID mismatch")
        if selected.selected_candidate_ref != candidate.record_id:
            _issue(issues, "package.selected_meaning_record.selected_candidate_ref", SelectedMeaningConstructionValidationCode.CANDIDATE_MISMATCH, "selected candidate reference mismatch")
        if selected.lineage_id != candidate.lineage_id:
            _issue(issues, "package.selected_meaning_record.lineage_id", SelectedMeaningConstructionValidationCode.LINEAGE_MISMATCH, "selected lineage mismatch")
        if selected.selection_authority_ref != construction_input.eligibility_result.result_id:
            _issue(issues, "package.selected_meaning_record.selection_authority_ref", SelectedMeaningConstructionValidationCode.ELIGIBILITY_MISMATCH, "selection authority must be exact 41C result")
        if selected.authority_sensitive_distinctions != candidate.authority_sensitive_implications:
            _issue(issues, "package.selected_meaning_record.authority_sensitive_distinctions", SelectedMeaningConstructionValidationCode.SEMANTIC_CONTENT_MISMATCH, "candidate authority-sensitive distinctions must be copied exactly")

    if value.construction_input_ref != construction_input.construction_input_id:
        _issue(issues, "package.construction_input_ref", SelectedMeaningConstructionValidationCode.IDENTITY_MISMATCH, "construction input ref mismatch")
    if value.eligibility_result_ref != construction_input.eligibility_result.result_id:
        _issue(issues, "package.eligibility_result_ref", SelectedMeaningConstructionValidationCode.ELIGIBILITY_MISMATCH, "eligibility result ref mismatch")
    if value.authority_profile_ref != construction_input.authority_profile.profile_id:
        _issue(issues, "package.authority_profile_ref", SelectedMeaningConstructionValidationCode.PROFILE_NOT_APPROVED, "profile ref mismatch")

    _validate_decision(value.decision_record, construction_input, issues)
    if isinstance(selected, SelectedGovernedMeaningRecord):
        _validate_content_proof(value.content_proof, candidate, selected, construction_input, issues)
    _validate_preserved_alternatives(value.preserved_alternatives, construction_input, issues)

    if value.selection_trace.trace_id != expected_trace_id(value.selection_trace):
        _issue(issues, "package.selection_trace.trace_id", SelectedMeaningConstructionValidationCode.TRACE_MISMATCH, "trace ID mismatch")
    if value.selection_receipt.receipt_id != expected_receipt_id(value.selection_receipt):
        _issue(issues, "package.selection_receipt.receipt_id", SelectedMeaningConstructionValidationCode.RECEIPT_MISMATCH, "receipt ID mismatch")
    if value.selection_trace.content_proof_ref != value.content_proof.proof_id or value.selection_receipt.content_proof_ref != value.content_proof.proof_id:
        _issue(issues, "package.selection_trace.content_proof_ref", SelectedMeaningConstructionValidationCode.TRACE_MISMATCH, "content proof linkage mismatch")
    if value.selection_receipt.trace_ref != value.selection_trace.trace_id:
        _issue(issues, "package.selection_receipt.trace_ref", SelectedMeaningConstructionValidationCode.RECEIPT_MISMATCH, "receipt trace linkage mismatch")
    preservation_ids = tuple(item.preservation_id for item in value.preserved_alternatives)
    if value.selection_trace.preserved_alternative_refs != preservation_ids or value.selection_receipt.preserved_alternative_refs != preservation_ids:
        _issue(issues, "package.selection_trace.preserved_alternative_refs", SelectedMeaningConstructionValidationCode.ALTERNATIVE_CUSTODY_MISMATCH, "trace and receipt must reference every preserved alternative")

    expected_top_level = {
        "unresolved_alternative_refs": _expected_unresolved(construction_input),
        "ambiguity_ancestry_refs": _expected_ambiguity(construction_input),
        "clarification_ancestry_refs": _expected_clarification(construction_input),
        "inherited_limitation_refs": _expected_inherited_limitations(construction_input),
        "blocked_consequence_refs": _expected_blocked(construction_input),
        "refusal_relevant_refs": _expected_refusal(construction_input),
        "authority_sensitive_distinction_refs": _expected_authority_sensitive(construction_input),
    }
    for name, expected in expected_top_level.items():
        if getattr(value, name) != expected:
            _issue(issues, f"package.{name}", SelectedMeaningConstructionValidationCode.CANONICAL_MISMATCH, "package custody field is not exact")

    if isinstance(selected, SelectedGovernedMeaningRecord):
        if selected.inherited_limitations != expected_top_level["inherited_limitation_refs"]:
            _issue(issues, "package.selected_meaning_record.inherited_limitations", SelectedMeaningConstructionValidationCode.CANONICAL_MISMATCH, "selected meaning inherited limitations are not exact")

    trace_expected = {
        "construction_input_ref": construction_input.construction_input_id,
        "decision_ref": value.decision_record.decision_id,
        "eligibility_result_ref": construction_input.eligibility_result.result_id,
        "selected_candidate_ref": candidate.record_id,
        "selected_meaning_ref": selected.record_id if isinstance(selected, SelectedGovernedMeaningRecord) else "",
        "gate_custody_ref": construction_input.eligibility_result.msm_gate_custody_companion_ref,
        "gate_composition_result_ref": construction_input.eligibility_result.gate_composition_result_ref,
        "authority_profile_ref": construction_input.authority_profile.profile_id,
        "content_proof_ref": value.content_proof.proof_id,
        "preserved_alternative_refs": preservation_ids,
        "unresolved_alternative_refs": expected_top_level["unresolved_alternative_refs"],
        "inherited_limitation_refs": expected_top_level["inherited_limitation_refs"],
        "blocked_consequence_refs": expected_top_level["blocked_consequence_refs"],
        "refusal_relevant_refs": expected_top_level["refusal_relevant_refs"],
        "ambiguity_ancestry_refs": expected_top_level["ambiguity_ancestry_refs"],
        "clarification_ancestry_refs": expected_top_level["clarification_ancestry_refs"],
        "predecessor_trace_refs": _unique(construction_input.eligibility_result.trace_refs, construction_input.trace_refs),
        "predecessor_receipt_refs": (construction_input.eligibility_evaluation_input.governance_bundle.runtime_schema_record.selection_receipt_boundary.selection_receipt_boundary_id,),
        "provenance_refs": _unique(construction_input.eligibility_result.provenance_refs, construction_input.provenance_refs),
        "version_refs": construction_input.version_refs,
    }
    for name, expected in trace_expected.items():
        if getattr(value.selection_trace, name) != expected:
            _issue(issues, f"package.selection_trace.{name}", SelectedMeaningConstructionValidationCode.TRACE_MISMATCH, "trace custody field is not exact")
    if value.selection_trace.deterministic is not True or value.selection_trace.candidate_ranked is not False or value.selection_trace.alternatives_erased is not False:
        _issue(issues, "package.selection_trace", SelectedMeaningConstructionValidationCode.TRACE_MISMATCH, "trace boundary flags are not exact")

    receipt_expected = {
        "construction_input_ref": construction_input.construction_input_id,
        "decision_ref": value.decision_record.decision_id,
        "selected_meaning_ref": selected.record_id if isinstance(selected, SelectedGovernedMeaningRecord) else "",
        "content_proof_ref": value.content_proof.proof_id,
        "trace_ref": value.selection_trace.trace_id,
        "eligibility_result_ref": construction_input.eligibility_result.result_id,
        "selected_candidate_ref": candidate.record_id,
        "preserved_alternative_refs": preservation_ids,
        "unresolved_alternative_refs": expected_top_level["unresolved_alternative_refs"],
        "inherited_limitation_refs": expected_top_level["inherited_limitation_refs"],
        "required_law_refs": SLICE41D_PERMANENT_BOUNDARIES,
        "prohibited_consequence_refs": SLICE41D_PROHIBITED_AUTHORITY,
    }
    for name, expected in receipt_expected.items():
        if getattr(value.selection_receipt, name) != expected:
            _issue(issues, f"package.selection_receipt.{name}", SelectedMeaningConstructionValidationCode.RECEIPT_MISMATCH, "receipt custody field is not exact")
    if value.selection_receipt.deterministic is not True or value.selection_receipt.selected_meaning_constructed is not True:
        _issue(issues, "package.selection_receipt", SelectedMeaningConstructionValidationCode.RECEIPT_MISMATCH, "receipt positive flags are not exact")
    _false_flags(
        value.selection_receipt,
        ("msm_v1_modified", "outward_meaning_created", "truth_determined", "evidence_validated", "permission_granted", "execution_authorized", "rendered", "delivered"),
        "package.selection_receipt",
        issues,
    )

    true_flags = (
        "deterministic",
        "exact_candidate_identity_preserved",
        "exact_candidate_lineage_preserved",
        "exact_semantic_content_preserved",
        "every_non_selected_candidate_preserved",
        "unresolved_alternatives_preserved_separately",
        "ambiguity_ancestry_preserved",
        "clarification_ancestry_preserved",
        "inherited_limitations_preserved",
        "blocked_consequences_preserved",
        "refusal_relevance_preserved",
        "selected_meaning_created",
    )
    for name in true_flags:
        if getattr(value, name) is not True:
            _issue(issues, f"package.{name}", SelectedMeaningConstructionValidationCode.CANONICAL_MISMATCH, "must be true")
    _false_flags(
        value,
        (
            "candidate_ranked",
            "alternatives_erased",
            "msm_v1_modified",
            "governed_outward_meaning_created",
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
            "bootstrap_integration_enabled",
        ),
        "package",
        issues,
    )
    if value.package_digest != expected_package_digest(value) or value.package_id != expected_package_id(value):
        _issue(issues, "package.package_id", SelectedMeaningConstructionValidationCode.IDENTITY_MISMATCH, "package identity mismatch")
    return _report(issues)


def assert_valid_package(
    value: object,
    *,
    construction_input: SelectedMeaningConstructionInput,
) -> None:
    report = validate_package(value, construction_input=construction_input)
    if not report.ok:
        raise SelectedMeaningConstructionValidationError(report)


__all__ = (
    "assert_valid_construction_input",
    "assert_valid_package",
    "validate_authority_profile",
    "validate_construction_input",
    "validate_package",
)
