"""Fail-closed validation for Slice 42E controlled expression plans."""

from __future__ import annotations

import re
from typing import Any, Iterable

from ..expression_eligibility.schema import ExpressionEligibilityOutcome
from ..preservation_obligation_projection import (
    PreservationObligationProjectionInput,
    PreservationObligationProjectionResult,
    SLICE42D_SCHEMA_VERSION,
    validate_projection_input,
    validate_projection_result,
)
from .authority import (
    DIGEST_ALGORITHM,
    SLICE42E_GOVERNING_AUTHORITY_REFS,
    SLICE42E_PERMANENT_BOUNDARIES,
    SLICE42E_PLAN_AUTHORITY_KEY,
    SLICE42E_PROFILE_KEY,
    SLICE42E_PROFILE_VERSION,
    SLICE42E_PROHIBITED_AUTHORITY,
    SLICE42E_SCHEMA_VERSION,
    SLICE42E_SECTION_ORDER_VALUES,
)
from .identity import (
    expected_plan_digest,
    expected_plan_id,
    expected_record_id,
    expected_result_digest,
    expected_result_id,
)
from .planner import (
    build_plan_sections,
    derive_plan_values,
    determine_plan_disposition,
    structural_order,
)
from .schema import (
    ControlledExpressionPlan,
    ExpressionPlanConstructionAuthorityRecord,
    ExpressionPlanConstructionFinding,
    ExpressionPlanConstructionFindingKind,
    ExpressionPlanConstructionInput,
    ExpressionPlanConstructionResult,
    ExpressionPlanConstructionValidationCode as Code,
    ExpressionPlanConstructionValidationError,
    ExpressionPlanConstructionValidationIssue as Issue,
    ExpressionPlanConstructionValidationReport as Report,
    ExpressionPlanDisposition,
    ExpressionPlanSection,
    ExpressionPlanSectionKind,
)


def _issue(path: str, code: Code, detail: str) -> Issue:
    return Issue(path=path, code=code, detail=detail)


def _report(issues: Iterable[Issue]) -> Report:
    return Report(issues=tuple(issues))


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/#@+\-]{0,1023}$")


def _valid_identifier(value: Any) -> bool:
    return type(value) is str and bool(_IDENTIFIER.fullmatch(value))


def _validate_identifier(value: Any, path: str) -> list[Issue]:
    return [] if _valid_identifier(value) else [
        _issue(path, Code.INVALID_IDENTIFIER, "exact non-empty identifier required")
    ]


def _validate_identifier_tuple(
    value: Any,
    path: str,
    *,
    allow_empty: bool,
) -> list[Issue]:
    issues: list[Issue] = []
    if type(value) is not tuple:
        return [_issue(path, Code.TYPE_MISMATCH, "exact tuple required")]
    if not allow_empty and not value:
        issues.append(_issue(path, Code.INVALID_IDENTIFIER, "non-empty tuple required"))
    seen: set[str] = set()
    for index, item in enumerate(value):
        issues.extend(_validate_identifier(item, f"{path}[{index}]"))
        if type(item) is str:
            if item in seen:
                issues.append(
                    _issue(
                        f"{path}[{index}]",
                        Code.DUPLICATE_IDENTIFIER,
                        "duplicate references prohibited",
                    )
                )
            seen.add(item)
    return issues


def _equal(
    issues: list[Issue],
    path: str,
    actual: Any,
    expected: Any,
    code: Code,
    detail: str,
) -> None:
    if actual != expected:
        issues.append(_issue(path, code, detail))


def _expected_receipts(value: ExpressionPlanConstructionInput) -> tuple[str, ...]:
    package = value.projection_result.obligation_package
    receipt = (
        value.projection_input.projection_authority_record
        .projection_authority_receipt_ref
    )
    return tuple(dict.fromkeys(package.predecessor_receipt_refs + (receipt,)))


def _expected_versions(value: ExpressionPlanConstructionInput) -> tuple[str, ...]:
    package = value.projection_result.obligation_package
    return tuple(
        dict.fromkeys(
            package.version_refs
            + (SLICE42D_SCHEMA_VERSION, SLICE42E_SCHEMA_VERSION)
        )
    )


def validate_plan_authority_record(
    value: Any,
    *,
    plan_input: ExpressionPlanConstructionInput | None = None,
) -> Report:
    if type(value) is not ExpressionPlanConstructionAuthorityRecord:
        return _report([
            _issue("planning_authority_record", Code.TYPE_MISMATCH, "exact authority record required")
        ])
    issues: list[Issue] = []
    for name in (
        "planning_authority_record_id",
        "authority_key",
        "authority_version",
        "projection_input_ref",
        "projection_result_ref",
        "obligation_package_ref",
        "selected_meaning_source_custody_ref",
        "outward_expression_authority_record_ref",
        "disposition_authority_ref",
        "planning_authority_receipt_ref",
        "profile_key",
        "profile_version",
        "schema_version",
    ):
        issues.extend(_validate_identifier(getattr(value, name), f"planning_authority_record.{name}"))
    for name in ("predecessor_receipt_refs", "version_refs"):
        issues.extend(_validate_identifier_tuple(getattr(value, name), f"planning_authority_record.{name}", allow_empty=False))
    _equal(issues, "planning_authority_record.authority_key", value.authority_key, SLICE42E_PLAN_AUTHORITY_KEY, Code.PLAN_AUTHORITY_MISMATCH, "exact Slice 42E authority key required")
    _equal(issues, "planning_authority_record.authority_version", value.authority_version, SLICE42E_PROFILE_VERSION, Code.INVALID_VERSION, "exact authority version required")
    _equal(issues, "planning_authority_record.profile_key", value.profile_key, SLICE42E_PROFILE_KEY, Code.INVALID_VERSION, "exact profile key required")
    _equal(issues, "planning_authority_record.profile_version", value.profile_version, SLICE42E_PROFILE_VERSION, Code.INVALID_VERSION, "exact profile version required")
    _equal(issues, "planning_authority_record.schema_version", value.schema_version, SLICE42E_SCHEMA_VERSION, Code.INVALID_VERSION, "exact schema version required")
    if value.authority_active is not True or value.expression_plan_construction_authorized is not True:
        issues.append(_issue("planning_authority_record", Code.PLAN_AUTHORITY_MISSING, "active explicit plan construction authority required"))
    downstream_false = (
        "governed_outward_meaning_construction_authorized",
        "surface_realization_authorized",
        "expression_candidate_creation_authorized",
        "msm_v1_mutation_or_integration_authorized",
        "echo_validation_authorized",
        "delivery_authorized",
        "truth_evidence_permission_execution_authorized",
        "route_api_network_filesystem_memory_tool_action_authorized",
        "external_resource_or_model_authority",
        "gp014_supersession_authorized",
    )
    for name in downstream_false:
        if getattr(value, name) is not False:
            issues.append(_issue(f"planning_authority_record.{name}", Code.DOWNSTREAM_AUTHORITY, "downstream authority must remain false"))
    if type(value.permitted_structural_order) is not tuple:
        issues.append(
            _issue(
                "planning_authority_record.permitted_structural_order",
                Code.TYPE_MISMATCH,
                "exact structural-order tuple required",
            )
        )
    elif not all(
        type(item) is ExpressionPlanSectionKind
        for item in value.permitted_structural_order
    ):
        issues.append(
            _issue(
                "planning_authority_record.permitted_structural_order",
                Code.TYPE_MISMATCH,
                "exact ExpressionPlanSectionKind members required",
            )
        )
    elif (
        tuple(item.value for item in value.permitted_structural_order)
        != SLICE42E_SECTION_ORDER_VALUES
    ):
        issues.append(
            _issue(
                "planning_authority_record.permitted_structural_order",
                Code.STRUCTURAL_ORDER_MISMATCH,
                "exact permitted order required",
            )
        )
    if plan_input is not None:
        projection_input = plan_input.projection_input
        projection_result = plan_input.projection_result
        package = projection_result.obligation_package
        expected_disposition = determine_plan_disposition(plan_input)
        exact = {
            "projection_input_ref": projection_input.projection_input_id,
            "projection_result_ref": projection_result.result_id,
            "obligation_package_ref": package.obligation_package_id,
            "selected_meaning_source_custody_ref": package.selected_meaning_source_custody_ref,
            "outward_expression_authority_record_ref": package.outward_expression_authority_record_ref,
            "source_eligibility_outcome": projection_result.source_eligibility_outcome,
            "permitted_disposition": expected_disposition,
            "predecessor_receipt_refs": _expected_receipts(plan_input),
            "version_refs": _expected_versions(plan_input),
        }
        for name, expected in exact.items():
            _equal(issues, f"planning_authority_record.{name}", getattr(value, name), expected, Code.PLAN_AUTHORITY_MISMATCH, "exact Slice 42D-bound authority value required")
        affirmative = expected_disposition is ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN
        containment = expected_disposition in (
            ExpressionPlanDisposition.BLOCKED_CONSEQUENCE_PLAN,
            ExpressionPlanDisposition.REFUSAL_PRESERVING_PLAN,
            ExpressionPlanDisposition.UNRESOLVED_PRESERVING_PLAN,
        )
        _equal(issues, "planning_authority_record.affirmative_meaning_plan_authorized", value.affirmative_meaning_plan_authorized, affirmative, Code.PLAN_AUTHORITY_MISMATCH, "affirmative authority must match governed disposition")
        _equal(issues, "planning_authority_record.containment_plan_authorized", value.containment_plan_authorized, containment, Code.PLAN_AUTHORITY_MISMATCH, "containment authority must match governed disposition")
    try:
        expected_id = expected_record_id(value)
        _equal(issues, "planning_authority_record.planning_authority_record_id", value.planning_authority_record_id, expected_id, Code.IDENTITY_MISMATCH, "deterministic identity mismatch")
    except Exception as error:
        issues.append(_issue("planning_authority_record.planning_authority_record_id", Code.IDENTITY_MISMATCH, str(error)))
    return _report(issues)


def validate_plan_input(value: Any) -> Report:
    if type(value) is not ExpressionPlanConstructionInput:
        return _report([_issue("plan_input", Code.TYPE_MISMATCH, "exact plan input required")])
    issues: list[Issue] = []
    issues.extend(_validate_identifier(value.plan_input_id, "plan_input.plan_input_id"))
    for name in ("planning_reason_refs", "trace_refs", "provenance_refs", "version_refs"):
        issues.extend(_validate_identifier_tuple(getattr(value, name), f"plan_input.{name}", allow_empty=False))
    nested_state_valid = True
    if type(value.projection_input) is not PreservationObligationProjectionInput:
        issues.append(
            _issue(
                "plan_input.projection_input",
                Code.TYPE_MISMATCH,
                "exact Slice 42D projection input required",
            )
        )
        nested_state_valid = False
    else:
        projection_input_report = validate_projection_input(
            value.projection_input
        )
        for item in projection_input_report.issues:
            issues.append(
                _issue(
                    f"plan_input.projection_input.{item.path}",
                    Code.RECORD_INVALID,
                    item.detail,
                )
            )
        if not projection_input_report.ok:
            nested_state_valid = False

    if type(value.projection_result) is not PreservationObligationProjectionResult:
        issues.append(
            _issue(
                "plan_input.projection_result",
                Code.TYPE_MISMATCH,
                "exact Slice 42D projection result required",
            )
        )
        nested_state_valid = False
    elif type(value.projection_input) is PreservationObligationProjectionInput:
        projection_result_report = validate_projection_result(
            value.projection_result,
            projection_input=value.projection_input,
        )
        for item in projection_result_report.issues:
            issues.append(
                _issue(
                    f"plan_input.projection_result.{item.path}",
                    Code.RECORD_INVALID,
                    item.detail,
                )
            )
        if not projection_result_report.ok:
            nested_state_valid = False
        if (
            value.projection_result.preservation_obligations_projected
            is not True
            or value.projection_result.obligation_package_created is not True
        ):
            issues.append(
                _issue(
                    "plan_input.projection_result",
                    Code.SLICE42D_STATE_MISMATCH,
                    "exact completed Slice 42D projection required",
                )
            )
            nested_state_valid = False

    authority_report = validate_plan_authority_record(
        value.planning_authority_record,
        plan_input=value if nested_state_valid else None,
    )
    issues.extend(authority_report.issues)
    prohibited = (
        "obligation_omission_requested",
        "structural_reordering_requested",
        "modifier_omission_requested",
        "modifier_invention_requested",
        "qualification_omission_requested",
        "caveat_omission_requested",
        "refusal_softening_requested",
        "unresolved_resolution_requested",
        "ambiguity_erasure_requested",
        "unsupported_state_erasure_requested",
        "lower_order_override_requested",
        "selected_meaning_rewrite_requested",
        "human_readable_wording_requested",
        "downstream_authority_requested",
    )
    for name in prohibited:
        if getattr(value, name) is not False:
            issues.append(_issue(f"plan_input.{name}", Code.PROHIBITED_REQUEST, "prohibited plan request"))
    _equal(issues, "plan_input.version_refs", value.version_refs, (SLICE42D_SCHEMA_VERSION, SLICE42E_SCHEMA_VERSION), Code.INVALID_VERSION, "exact input versions required")
    try:
        _equal(issues, "plan_input.plan_input_id", value.plan_input_id, expected_record_id(value), Code.IDENTITY_MISMATCH, "deterministic identity mismatch")
    except Exception as error:
        issues.append(_issue("plan_input.plan_input_id", Code.IDENTITY_MISMATCH, str(error)))
    return _report(issues)


def validate_expression_plan(
    value: Any,
    *,
    plan_input: ExpressionPlanConstructionInput,
) -> Report:
    if type(value) is not ControlledExpressionPlan:
        return _report([_issue("expression_plan", Code.TYPE_MISMATCH, "exact controlled plan required")])
    issues: list[Issue] = []
    input_report = validate_plan_input(plan_input)
    if not input_report.ok:
        return _report(
            _issue(
                f"expression_plan.input.{item.path}",
                Code.RECORD_INVALID,
                item.detail,
            )
            for item in input_report.issues
        )
    derived = derive_plan_values(plan_input)
    package = plan_input.projection_result.obligation_package
    authority = plan_input.planning_authority_record
    expected_sections = build_plan_sections(plan_input, derived)
    exact = {
        "plan_input_ref": plan_input.plan_input_id,
        "projection_result_ref": plan_input.projection_result.result_id,
        "obligation_package_ref": package.obligation_package_id,
        "planning_authority_record_ref": authority.planning_authority_record_id,
        "selected_meaning_source_custody_ref": package.selected_meaning_source_custody_ref,
        "outward_expression_authority_record_ref": package.outward_expression_authority_record_ref,
        "source_eligibility_outcome": package.source_eligibility_outcome,
        "disposition": derived["disposition"],
        "sections": expected_sections,
        "structural_order": structural_order(),
        "selected_meaning_refs": derived["selected_meaning_refs"],
        "active_scope_refs": derived["active_scope_refs"],
        "certainty_level_refs": derived["certainty_level_refs"],
        "evidence_status_refs": derived["evidence_status_refs"],
        "meaning_modifier_refs": derived["meaning_modifier_refs"],
        "inherited_limitation_refs": derived["inherited_limitation_refs"],
        "required_qualification_refs": derived["required_qualification_refs"],
        "required_caveat_refs": derived["required_caveat_refs"],
        "refusal_relevant_boundary_refs": derived["refusal_relevant_boundary_refs"],
        "unresolved_condition_refs": derived["unresolved_condition_refs"],
        "ambiguity_refs": derived["ambiguity_refs"],
        "unsupported_state_refs": derived["unsupported_state_refs"],
        "memory_authority_refs": derived["memory_authority_refs"],
        "external_resource_status_refs": derived["external_resource_status_refs"],
        "delivery_authority_refs": derived["delivery_authority_refs"],
        "privacy_identity_boundary_refs": derived["privacy_identity_boundary_refs"],
        "preservation_class_refs": derived["preservation_class_refs"],
        "ancestry_refs": derived["ancestry_refs"],
        "predecessor_receipt_refs": derived["predecessor_receipt_refs"],
        "trace_refs": derived["trace_refs"],
        "provenance_refs": derived["provenance_refs"],
        "version_refs": derived["version_refs"],
    }
    for name, expected in exact.items():
        code = Code.STRUCTURAL_ORDER_MISMATCH if name in ("sections", "structural_order") else Code.OBLIGATION_MISMATCH
        _equal(issues, f"expression_plan.{name}", getattr(value, name), expected, code, "exact derived plan value required")
    required_true = (
        "exact_slice42d_state_verified",
        "exact_plan_authority_verified",
        "all_slice42d_obligations_preserved",
        "structural_ordering_determined",
        "meaning_modifiers_preserved",
        "required_qualifications_preserved",
        "required_caveats_preserved",
        "refusal_boundaries_preserved",
        "higher_order_restrictions_dominant",
        "selected_meaning_ancestry_preserved",
        "expression_plan_created",
    )
    for name in required_true:
        if getattr(value, name) is not True:
            issues.append(_issue(f"expression_plan.{name}", Code.OBLIGATION_MISMATCH, "required preservation proof must be true"))
    disposition = derived["disposition"]
    disposition_flags = {
        "affirmative_claim_plan": disposition is ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN,
        "blocked_consequence_plan": disposition is ExpressionPlanDisposition.BLOCKED_CONSEQUENCE_PLAN,
        "refusal_preserving_plan": disposition is ExpressionPlanDisposition.REFUSAL_PRESERVING_PLAN,
        "unresolved_preserving_plan": disposition is ExpressionPlanDisposition.UNRESOLVED_PRESERVING_PLAN,
        "containment_plan_does_not_upgrade_source_eligibility": disposition is not ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN,
    }
    for name, expected in disposition_flags.items():
        _equal(issues, f"expression_plan.{name}", getattr(value, name), expected, Code.PLAN_DISPOSITION_MISMATCH, "disposition flag mismatch")
    _equal(issues, "expression_plan.source_planning_progression_eligible", value.source_planning_progression_eligible, package.planning_progression_eligible, Code.PLAN_DISPOSITION_MISMATCH, "source eligibility must be preserved")
    downstream_false = (
        "governed_outward_meaning_created",
        "human_readable_text_produced",
        "expression_candidate_created",
        "surface_realization_performed",
        "msm_v1_modified_or_integrated",
        "echo_validation_performed",
        "bootstrap_integration_enabled",
        "delivered",
        "truth_determined",
        "evidence_validated",
        "permission_granted",
        "execution_authorized",
        "route_or_api_created",
        "tool_invoked",
        "action_performed",
        "memory_accessed_or_written",
        "filesystem_or_network_accessed",
        "external_resource_loaded",
        "model_or_similarity_authority_used",
        "gp014_superseded",
    )
    for name in downstream_false:
        if getattr(value, name) is not False:
            issues.append(_issue(f"expression_plan.{name}", Code.DOWNSTREAM_AUTHORITY, "downstream state must remain false"))
    if value.digest_algorithm != DIGEST_ALGORITHM:
        issues.append(_issue("expression_plan.digest_algorithm", Code.DIGEST_MISMATCH, "sha256 required"))
    try:
        _equal(issues, "expression_plan.expression_plan_digest", value.expression_plan_digest, expected_plan_digest(value), Code.DIGEST_MISMATCH, "plan digest mismatch")
        _equal(issues, "expression_plan.expression_plan_id", value.expression_plan_id, expected_plan_id(value), Code.IDENTITY_MISMATCH, "plan identity mismatch")
    except Exception as error:
        issues.append(_issue("expression_plan", Code.CANONICAL_MISMATCH, str(error)))
    return _report(issues)


def validate_plan_result(
    value: Any,
    *,
    plan_input: ExpressionPlanConstructionInput,
) -> Report:
    if type(value) is not ExpressionPlanConstructionResult:
        return _report([_issue("result", Code.TYPE_MISMATCH, "exact plan result required")])
    issues: list[Issue] = []
    input_report = validate_plan_input(plan_input)
    issues.extend(
        _issue(
            f"result.input.{item.path}",
            Code.RECORD_INVALID,
            item.detail,
        )
        for item in input_report.issues
    )
    if not input_report.ok:
        return _report(issues)
    disposition = determine_plan_disposition(plan_input)
    constructible = disposition in (
        ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN,
        ExpressionPlanDisposition.BLOCKED_CONSEQUENCE_PLAN,
        ExpressionPlanDisposition.REFUSAL_PRESERVING_PLAN,
        ExpressionPlanDisposition.UNRESOLVED_PRESERVING_PLAN,
    )
    _equal(issues, "result.plan_input_ref", value.plan_input_ref, plan_input.plan_input_id, Code.RECORD_INVALID, "input reference mismatch")
    _equal(issues, "result.source_eligibility_outcome", value.source_eligibility_outcome, plan_input.projection_result.source_eligibility_outcome, Code.PLAN_DISPOSITION_MISMATCH, "source outcome mismatch")
    _equal(issues, "result.disposition", value.disposition, disposition, Code.PLAN_DISPOSITION_MISMATCH, "disposition mismatch")
    _equal(issues, "result.expression_plan_created", value.expression_plan_created, constructible, Code.PLAN_DISPOSITION_MISMATCH, "plan creation state mismatch")
    if constructible:
        plan_report = validate_expression_plan(value.expression_plan, plan_input=plan_input)
        issues.extend(plan_report.issues)
    elif value.expression_plan is not None:
        issues.append(_issue("result.expression_plan", Code.PLAN_DISPOSITION_MISMATCH, "held or indeterminate state must not contain plan"))
    exact_flags = {
        "affirmative_claim_plan": disposition is ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN,
        "blocked_consequence_plan": disposition is ExpressionPlanDisposition.BLOCKED_CONSEQUENCE_PLAN,
        "refusal_preserving_plan": disposition is ExpressionPlanDisposition.REFUSAL_PRESERVING_PLAN,
        "unresolved_preserving_plan": disposition is ExpressionPlanDisposition.UNRESOLVED_PRESERVING_PLAN,
        "held_pending_authority": disposition is ExpressionPlanDisposition.HELD_PENDING_AUTHORITY,
        "indeterminate": disposition is ExpressionPlanDisposition.INDETERMINATE,
        "all_slice42d_obligations_preserved": constructible,
        "structural_ordering_determined": constructible,
        "lower_order_choice_overrode_semantics": False,
    }
    for name, expected in exact_flags.items():
        _equal(issues, f"result.{name}", getattr(value, name), expected, Code.PLAN_DISPOSITION_MISMATCH, "result flag mismatch")
    _equal(issues, "result.required_law_refs", value.required_law_refs, SLICE42E_GOVERNING_AUTHORITY_REFS, Code.OBLIGATION_MISMATCH, "governing law mismatch")
    _equal(issues, "result.permanent_boundaries", value.permanent_boundaries, SLICE42E_PERMANENT_BOUNDARIES, Code.OBLIGATION_MISMATCH, "boundary mismatch")
    _equal(issues, "result.prohibited_authority", value.prohibited_authority, SLICE42E_PROHIBITED_AUTHORITY, Code.OBLIGATION_MISMATCH, "prohibited authority mismatch")
    expected_finding_kinds = tuple(ExpressionPlanConstructionFindingKind)
    if type(value.findings) is not tuple:
        issues.append(
            _issue(
                "result.findings",
                Code.TYPE_MISMATCH,
                "exact findings tuple required",
            )
        )
        findings: tuple[Any, ...] = ()
    else:
        findings = value.findings
    actual_finding_kinds = tuple(
        item.finding_kind
        for item in findings
        if type(item) is ExpressionPlanConstructionFinding
    )
    _equal(issues, "result.findings", actual_finding_kinds, expected_finding_kinds, Code.FINDING_MISMATCH, "exact finding set and order required")
    finding_ids: set[str] = set()
    for index, finding in enumerate(findings):
        if type(finding) is not ExpressionPlanConstructionFinding:
            issues.append(_issue(f"result.findings[{index}]", Code.TYPE_MISMATCH, "exact finding required"))
            continue
        if finding.finding_id in finding_ids:
            issues.append(_issue(f"result.findings[{index}].finding_id", Code.DUPLICATE_IDENTIFIER, "duplicate finding id"))
        finding_ids.add(finding.finding_id)
        try:
            _equal(issues, f"result.findings[{index}].finding_id", finding.finding_id, expected_record_id(finding), Code.IDENTITY_MISMATCH, "finding identity mismatch")
        except Exception as error:
            issues.append(_issue(f"result.findings[{index}]", Code.CANONICAL_MISMATCH, str(error)))
    downstream_false = (
        "governed_outward_meaning_created",
        "human_readable_text_produced",
        "expression_candidate_created",
        "surface_realization_performed",
        "msm_v1_modified_or_integrated",
        "echo_validation_performed",
        "bootstrap_integration_enabled",
        "delivered",
        "truth_determined",
        "evidence_validated",
        "permission_granted",
        "execution_authorized",
        "route_or_api_created",
        "tool_invoked",
        "action_performed",
        "memory_accessed_or_written",
        "filesystem_or_network_accessed",
        "external_resource_loaded",
        "model_or_similarity_authority_used",
        "gp014_superseded",
    )
    for name in downstream_false:
        if getattr(value, name) is not False:
            issues.append(_issue(f"result.{name}", Code.DOWNSTREAM_AUTHORITY, "downstream state must remain false"))
    try:
        _equal(issues, "result.result_digest", value.result_digest, expected_result_digest(value), Code.DIGEST_MISMATCH, "result digest mismatch")
        _equal(issues, "result.result_id", value.result_id, expected_result_id(value), Code.IDENTITY_MISMATCH, "result identity mismatch")
    except Exception as error:
        issues.append(_issue("result", Code.CANONICAL_MISMATCH, str(error)))
    return _report(issues)


def assert_valid_plan_input(value: Any) -> None:
    report = validate_plan_input(value)
    if not report.ok:
        raise ExpressionPlanConstructionValidationError(report)


def assert_valid_plan_result(
    value: Any,
    *,
    plan_input: ExpressionPlanConstructionInput,
) -> None:
    report = validate_plan_result(value, plan_input=plan_input)
    if not report.ok:
        raise ExpressionPlanConstructionValidationError(report)


__all__ = (
    "assert_valid_plan_input",
    "assert_valid_plan_result",
    "validate_expression_plan",
    "validate_plan_authority_record",
    "validate_plan_input",
    "validate_plan_result",
)
