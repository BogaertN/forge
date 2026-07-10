from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import (
    NON_AUTHORITY_DISCLAIMER,
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    all_required_markers_present,
    check_false_only,
    issue,
    no_forbidden_markers_present,
    nonempty_text,
    stable_expression_id,
    tuple_of_text,
    unique_tuple,
)
from .expression_plan import ExpressionPlanRecord, validate_expression_plan_record
from .expression_preview import ExpressionPreviewRecord, validate_expression_preview_record
from .expression_source import ExpressionSourceRecord, validate_expression_source_record
from .preservation_contract import (
    ExpressionPreservationContractRecord,
    validate_expression_preservation_contract,
)


@dataclass(frozen=True)
class ExpressionFidelityRecord:
    expression_fidelity_id: str
    expression_source_id: str
    preservation_contract_id: str
    expression_plan_id: str
    expression_preview_id: str
    source_binding_pass: bool
    selected_meaning_binding_pass: bool
    negation_preservation_pass: bool
    condition_preservation_pass: bool
    modality_non_strengthening_pass: bool
    attribution_preservation_pass: bool
    scope_non_widening_pass: bool
    refusal_relevance_preservation_pass: bool
    uncertainty_preservation_pass: bool
    forbidden_claim_absence_pass: bool
    non_authority_disclaimer_pass: bool
    hard_gate_pass: bool
    failed_check_refs: Tuple[str, ...]
    evaluation_status: str = "deterministic_hard_gate_evaluation"
    version_tag: str = "v1"

    live_runtime_behavior: bool = False
    live_runtime_interpretation: bool = False
    truth_decision: bool = False
    proof_claim: bool = False
    authority_grant: bool = False
    acceptance_effect: bool = False
    permission_grant: bool = False
    action_authorization: bool = False
    tool_invocation: bool = False
    capability_route: bool = False
    delivery_action: bool = False
    execution_authority: bool = False
    output_approval: bool = False
    user_facing_output_authorized: bool = False
    memory_write: bool = False
    memory_authority: bool = False
    evidence_validation: bool = False
    corpus_authority: bool = False
    external_truth_authority: bool = False
    external_resource_admission: bool = False
    runtime_promotion: bool = False
    resource_fetch: bool = False
    resource_download: bool = False
    resource_ingestion: bool = False
    resource_parsing: bool = False
    resource_indexing: bool = False
    model_authority: bool = False
    vector_authority: bool = False
    retrieval_authority: bool = False
    similarity_authority: bool = False
    embedding_index_creation: bool = False
    rag_execution: bool = False
    training_authority: bool = False
    gp014_supersession: bool = False
    gp015_repair: bool = False
    gp015r1_installation: bool = False
    release_authority: bool = False
    production_readiness: bool = False

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "expression_source_id": self.expression_source_id,
            "preservation_contract_id": self.preservation_contract_id,
            "expression_plan_id": self.expression_plan_id,
            "expression_preview_id": self.expression_preview_id,
            "source_binding_pass": self.source_binding_pass,
            "selected_meaning_binding_pass": self.selected_meaning_binding_pass,
            "negation_preservation_pass": self.negation_preservation_pass,
            "condition_preservation_pass": self.condition_preservation_pass,
            "modality_non_strengthening_pass": self.modality_non_strengthening_pass,
            "attribution_preservation_pass": self.attribution_preservation_pass,
            "scope_non_widening_pass": self.scope_non_widening_pass,
            "refusal_relevance_preservation_pass": self.refusal_relevance_preservation_pass,
            "uncertainty_preservation_pass": self.uncertainty_preservation_pass,
            "forbidden_claim_absence_pass": self.forbidden_claim_absence_pass,
            "non_authority_disclaimer_pass": self.non_authority_disclaimer_pass,
            "hard_gate_pass": self.hard_gate_pass,
            "failed_check_refs": self.failed_check_refs,
            "evaluation_status": self.evaluation_status,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_expression_id("expression-fidelity", self.canonical_body())


def _dimension_pass(state: str, markers: Tuple[str, ...], preview_text: str) -> bool:
    if state == "explicit_not_applicable":
        return True
    return all_required_markers_present(preview_text, markers)


def evaluate_expression_fidelity(
    source: ExpressionSourceRecord,
    contract: ExpressionPreservationContractRecord,
    plan: ExpressionPlanRecord,
    preview: ExpressionPreviewRecord,
) -> ExpressionFidelityRecord:
    source_valid = validate_expression_source_record(source).ok
    contract_valid = validate_expression_preservation_contract(contract).ok
    plan_valid = validate_expression_plan_record(plan).ok
    preview_valid = validate_expression_preview_record(preview).ok

    source_binding_pass = (
        source_valid
        and contract_valid
        and plan_valid
        and preview_valid
        and contract.expression_source_id == source.expression_source_id
        and plan.expression_source_id == source.expression_source_id
        and preview.expression_source_id == source.expression_source_id
        and plan.preservation_contract_id == contract.preservation_contract_id
        and preview.preservation_contract_id == contract.preservation_contract_id
        and preview.expression_plan_id == plan.expression_plan_id
        and preview.preview_kind == plan.preview_kind
        and preview.template_id == plan.template_id
        and preview.preserved_qualifier_markers == plan.required_qualifier_markers
    )
    selected_meaning_binding_pass = (
        source.selected_meaning_id
        == contract.selected_meaning_id
        == plan.selected_meaning_id
        == preview.selected_meaning_id
        and source.selected_meaning_status
        == plan.selected_meaning_status
        == preview.selected_meaning_status
    )
    text = preview.preview_text
    negation_preservation_pass = _dimension_pass(
        contract.negation_state, contract.negation_markers, text
    )
    condition_preservation_pass = _dimension_pass(
        contract.condition_state, contract.condition_markers, text
    )
    modality_non_strengthening_pass = _dimension_pass(
        contract.modality_state, contract.modality_markers, text
    ) and no_forbidden_markers_present(text, contract.forbidden_modality_strengtheners)
    attribution_preservation_pass = _dimension_pass(
        contract.attribution_state, contract.attribution_markers, text
    )
    scope_non_widening_pass = _dimension_pass(
        contract.scope_state, contract.scope_markers, text
    ) and no_forbidden_markers_present(text, contract.forbidden_scope_wideners)
    refusal_relevance_preservation_pass = _dimension_pass(
        contract.refusal_relevance_state, contract.refusal_relevance_markers, text
    )
    uncertainty_preservation_pass = _dimension_pass(
        contract.uncertainty_state, contract.uncertainty_markers, text
    )
    forbidden_claim_absence_pass = no_forbidden_markers_present(
        text, contract.forbidden_claim_phrases
    )
    non_authority_disclaimer_pass = (
        contract.required_disclaimer == NON_AUTHORITY_DISCLAIMER
        and preview.disclaimer == NON_AUTHORITY_DISCLAIMER
        and NON_AUTHORITY_DISCLAIMER in text
    )

    checks = {
        "source_binding": source_binding_pass,
        "selected_meaning_binding": selected_meaning_binding_pass,
        "negation_preservation": negation_preservation_pass,
        "condition_preservation": condition_preservation_pass,
        "modality_non_strengthening": modality_non_strengthening_pass,
        "attribution_preservation": attribution_preservation_pass,
        "scope_non_widening": scope_non_widening_pass,
        "refusal_relevance_preservation": refusal_relevance_preservation_pass,
        "uncertainty_preservation": uncertainty_preservation_pass,
        "forbidden_claim_absence": forbidden_claim_absence_pass,
        "non_authority_disclaimer": non_authority_disclaimer_pass,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    hard_gate_pass = all(checks.values())
    body = {
        "expression_source_id": source.expression_source_id,
        "preservation_contract_id": contract.preservation_contract_id,
        "expression_plan_id": plan.expression_plan_id,
        "expression_preview_id": preview.expression_preview_id,
        "source_binding_pass": source_binding_pass,
        "selected_meaning_binding_pass": selected_meaning_binding_pass,
        "negation_preservation_pass": negation_preservation_pass,
        "condition_preservation_pass": condition_preservation_pass,
        "modality_non_strengthening_pass": modality_non_strengthening_pass,
        "attribution_preservation_pass": attribution_preservation_pass,
        "scope_non_widening_pass": scope_non_widening_pass,
        "refusal_relevance_preservation_pass": refusal_relevance_preservation_pass,
        "uncertainty_preservation_pass": uncertainty_preservation_pass,
        "forbidden_claim_absence_pass": forbidden_claim_absence_pass,
        "non_authority_disclaimer_pass": non_authority_disclaimer_pass,
        "hard_gate_pass": hard_gate_pass,
        "failed_check_refs": failed,
        "evaluation_status": "deterministic_hard_gate_evaluation",
        "version_tag": "v1",
    }
    return ExpressionFidelityRecord(
        expression_fidelity_id=stable_expression_id("expression-fidelity", body),
        **body,
    )


def validate_expression_fidelity_record(record: ExpressionFidelityRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in (
        "expression_fidelity_id",
        "expression_source_id",
        "preservation_contract_id",
        "expression_plan_id",
        "expression_preview_id",
        "evaluation_status",
    ):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.evaluation_status != "deterministic_hard_gate_evaluation":
        issues.append(issue("evaluation_status", "unsupported_evaluation_status"))
    if not tuple_of_text(record.failed_check_refs):
        issues.append(issue("failed_check_refs", "must_be_tuple_of_text"))
    elif not unique_tuple(record.failed_check_refs):
        issues.append(issue("failed_check_refs", "duplicate_entries_not_allowed"))
    booleans = (
        record.source_binding_pass,
        record.selected_meaning_binding_pass,
        record.negation_preservation_pass,
        record.condition_preservation_pass,
        record.modality_non_strengthening_pass,
        record.attribution_preservation_pass,
        record.scope_non_widening_pass,
        record.refusal_relevance_preservation_pass,
        record.uncertainty_preservation_pass,
        record.forbidden_claim_absence_pass,
        record.non_authority_disclaimer_pass,
    )
    expected_hard_gate = all(booleans)
    if record.hard_gate_pass is not expected_hard_gate:
        issues.append(issue("hard_gate_pass", "must_equal_all_mandatory_hard_checks"))
    if record.hard_gate_pass and record.failed_check_refs:
        issues.append(issue("failed_check_refs", "must_be_empty_when_hard_gate_passes"))
    if not record.hard_gate_pass and not record.failed_check_refs:
        issues.append(issue("failed_check_refs", "must_identify_failed_hard_checks"))
    if record.expression_fidelity_id != record.expected_id():
        issues.append(issue("expression_fidelity_id", "stable_identifier_mismatch"))
    check_false_only(record, issues, "expression_fidelity")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))
