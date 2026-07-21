"""Fail-closed validation for Slice 42D preservation projection."""

from __future__ import annotations

import re
from typing import Any

from ..expression_eligibility import (
    SLICE42C_SCHEMA_VERSION,
    validate_evaluation_input as validate_slice42c_evaluation_input,
    validate_result as validate_slice42c_result,
)
from ..expression_eligibility.schema import (
    ExpressionEligibilityOutcome,
    ExpressionEligibilityResult,
)
from .authority import (
    SLICE42D_GOVERNING_AUTHORITY_REFS,
    SLICE42D_OBLIGATION_CATEGORY_NAMES,
    SLICE42D_PERMANENT_BOUNDARIES,
    SLICE42D_PROFILE_KEY,
    SLICE42D_PROFILE_VERSION,
    SLICE42D_PROHIBITED_AUTHORITY,
    SLICE42D_PROJECTION_AUTHORITY_KEY,
    SLICE42D_SCHEMA_VERSION,
)
from .identity import (
    expected_package_digest,
    expected_package_id,
    expected_record_id,
    expected_result_digest,
    expected_result_id,
)
from .projector import derive_obligation_values
from .schema import (
    ExpressionObligationPackage,
    PreservationObligationProjectionAuthorityRecord,
    PreservationObligationProjectionFinding,
    PreservationObligationProjectionFindingKind,
    PreservationObligationProjectionInput,
    PreservationObligationProjectionResult,
    PreservationObligationProjectionValidationCode as Code,
    PreservationObligationProjectionValidationError,
    PreservationObligationProjectionValidationIssue as Issue,
    PreservationObligationProjectionValidationReport as Report,
)


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/#@+\-]{0,1023}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _issue(path: str, code: Code, detail: str) -> Issue:
    return Issue(path=path, code=code, detail=detail)


def _report(issues: list[Issue]) -> Report:
    return Report(issues=tuple(issues))


def _validate_identifier(value: Any, path: str) -> list[Issue]:
    if type(value) is str and bool(_IDENTIFIER.fullmatch(value)):
        return []
    return [
        _issue(
            path,
            Code.INVALID_IDENTIFIER,
            "exact governed identifier required",
        )
    ]


def _validate_identifier_tuple(
    value: Any,
    path: str,
    *,
    allow_empty: bool,
) -> list[Issue]:
    if type(value) is not tuple:
        return [_issue(path, Code.TYPE_MISMATCH, "exact tuple required")]

    issues: list[Issue] = []
    if not allow_empty and not value:
        issues.append(
            _issue(path, Code.RECORD_INVALID, "non-empty tuple required")
        )
    if len(value) != len(set(value)):
        issues.append(
            _issue(
                path,
                Code.DUPLICATE_IDENTIFIER,
                "duplicate tuple values prohibited",
            )
        )

    for index, item in enumerate(value):
        issues.extend(
            _validate_identifier(item, f"{path}[{index}]")
        )
    return issues


def _expect_equal(
    issues: list[Issue],
    path: str,
    actual: Any,
    expected: Any,
    code: Code,
    detail: str,
) -> None:
    if actual != expected:
        issues.append(_issue(path, code, detail))


def _authority_downstream_true(
    value: PreservationObligationProjectionAuthorityRecord,
) -> tuple[str, ...]:
    names = (
        "governed_outward_meaning_construction_authorized",
        "expression_plan_construction_authorized",
        "surface_realization_authorized",
        "msm_v1_mutation_or_integration_authorized",
        "echo_validation_authorized",
        "delivery_authorized",
        "truth_evidence_permission_execution_authorized",
        "route_api_network_filesystem_memory_tool_action_authorized",
        "external_resource_or_model_authority",
        "gp014_supersession_authorized",
    )
    return tuple(
        name for name in names if getattr(value, name) is not False
    )


def validate_projection_authority_record(
    value: Any,
    *,
    projection_input: PreservationObligationProjectionInput | None = None,
) -> Report:
    if type(value) is not PreservationObligationProjectionAuthorityRecord:
        return _report(
            [
                _issue(
                    "projection_authority_record",
                    Code.TYPE_MISMATCH,
                    "exact PreservationObligationProjectionAuthorityRecord required",
                )
            ]
        )

    issues: list[Issue] = []

    for name in (
        "projection_authority_record_id",
        "authority_key",
        "authority_version",
        "expression_eligibility_evaluation_input_ref",
        "expression_eligibility_result_ref",
        "selected_meaning_source_custody_ref",
        "outward_expression_authority_requirement_ref",
        "outward_expression_authority_record_ref",
        "disposition_authority_ref",
        "projection_authority_receipt_ref",
    ):
        issues.extend(
            _validate_identifier(
                getattr(value, name),
                f"projection_authority_record.{name}",
            )
        )

    for name in (
        "projection_scope_refs",
        "predecessor_receipt_refs",
        "version_refs",
    ):
        issues.extend(
            _validate_identifier_tuple(
                getattr(value, name),
                f"projection_authority_record.{name}",
                allow_empty=False,
            )
        )

    if type(value.source_eligibility_outcome) is not ExpressionEligibilityOutcome:
        issues.append(
            _issue(
                "projection_authority_record.source_eligibility_outcome",
                Code.TYPE_MISMATCH,
                "exact ExpressionEligibilityOutcome required",
            )
        )

    if value.authority_key != SLICE42D_PROJECTION_AUTHORITY_KEY:
        issues.append(
            _issue(
                "projection_authority_record.authority_key",
                Code.PROJECTION_AUTHORITY_MISMATCH,
                "exact Slice 42D projection authority key required",
            )
        )

    if (
        value.profile_key != SLICE42D_PROFILE_KEY
        or value.profile_version != SLICE42D_PROFILE_VERSION
        or value.schema_version != SLICE42D_SCHEMA_VERSION
        or value.authority_version != SLICE42D_PROFILE_VERSION
    ):
        issues.append(
            _issue(
                "projection_authority_record.version",
                Code.INVALID_VERSION,
                "exact Slice 42D authority, profile, and schema versions required",
            )
        )

    if value.authority_active is not True:
        issues.append(
            _issue(
                "projection_authority_record.authority_active",
                Code.PROJECTION_AUTHORITY_MISSING,
                "active projection authority required",
            )
        )

    if value.preservation_obligation_projection_authorized is not True:
        issues.append(
            _issue(
                "projection_authority_record.preservation_obligation_projection_authorized",
                Code.PROJECTION_AUTHORITY_MISSING,
                "explicit preservation-obligation projection authority required",
            )
        )

    for name in _authority_downstream_true(value):
        issues.append(
            _issue(
                f"projection_authority_record.{name}",
                Code.DOWNSTREAM_AUTHORITY,
                "Slice 42D authority may grant projection only",
            )
        )

    if projection_input is not None:
        eligibility_input = (
            projection_input.expression_eligibility_evaluation_input
        )
        eligibility_result = projection_input.expression_eligibility_result
        source = eligibility_input.selected_meaning_source_custody
        requirement = (
            eligibility_input.outward_expression_authority_requirement
        )
        outward_authority = (
            eligibility_input.outward_expression_authority_record
        )

        expected_receipts = (
            source.slice41e_integration_receipt_ref,
            source.selection_receipt_ref,
            outward_authority.authority_receipt_ref,
        )
        expected_versions = (
            SLICE42C_SCHEMA_VERSION,
            SLICE42D_SCHEMA_VERSION,
            outward_authority.authority_version,
        )

        exact_values = {
            "expression_eligibility_evaluation_input_ref": (
                eligibility_input.evaluation_input_id
            ),
            "expression_eligibility_result_ref": eligibility_result.result_id,
            "selected_meaning_source_custody_ref": source.source_custody_id,
            "outward_expression_authority_requirement_ref": (
                requirement.authority_requirement_id
            ),
            "outward_expression_authority_record_ref": (
                outward_authority.authority_record_id
            ),
            "source_eligibility_outcome": eligibility_result.outcome,
            "projection_scope_refs": outward_authority.authority_scope_refs,
            "predecessor_receipt_refs": expected_receipts,
            "version_refs": expected_versions,
        }

        for name, expected in exact_values.items():
            code = (
                Code.PROJECTION_SCOPE_MISMATCH
                if name == "projection_scope_refs"
                else Code.PREDECESSOR_RECEIPT_MISMATCH
                if name == "predecessor_receipt_refs"
                else Code.PROJECTION_AUTHORITY_MISMATCH
            )
            _expect_equal(
                issues,
                f"projection_authority_record.{name}",
                getattr(value, name),
                expected,
                code,
                "exact Slice 42C-bound projection authority value required",
            )

    try:
        expected_id = expected_record_id(value)
        if value.projection_authority_record_id != expected_id:
            issues.append(
                _issue(
                    "projection_authority_record.projection_authority_record_id",
                    Code.IDENTITY_MISMATCH,
                    "deterministic identity mismatch",
                )
            )
    except Exception as error:
        issues.append(
            _issue(
                "projection_authority_record.projection_authority_record_id",
                Code.IDENTITY_MISMATCH,
                str(error),
            )
        )

    return _report(issues)


def validate_projection_input(value: Any) -> Report:
    if type(value) is not PreservationObligationProjectionInput:
        return _report(
            [
                _issue(
                    "projection_input",
                    Code.TYPE_MISMATCH,
                    "exact PreservationObligationProjectionInput required",
                )
            ]
        )

    issues: list[Issue] = []
    issues.extend(
        _validate_identifier(
            value.projection_input_id,
            "projection_input.projection_input_id",
        )
    )

    for name in (
        "projection_reason_refs",
        "trace_refs",
        "provenance_refs",
        "version_refs",
    ):
        issues.extend(
            _validate_identifier_tuple(
                getattr(value, name),
                f"projection_input.{name}",
                allow_empty=False,
            )
        )

    eligibility_input = value.expression_eligibility_evaluation_input
    eligibility_result = value.expression_eligibility_result

    slice42c_input_report = validate_slice42c_evaluation_input(
        eligibility_input
    )
    for issue in slice42c_input_report.issues:
        issues.append(
            _issue(
                f"projection_input.expression_eligibility_evaluation_input.{issue.path}",
                Code.RECORD_INVALID,
                issue.detail,
            )
        )

    slice42c_result_report = validate_slice42c_result(
        eligibility_result,
        evaluation_input=eligibility_input,
    )
    for issue in slice42c_result_report.issues:
        issues.append(
            _issue(
                f"projection_input.expression_eligibility_result.{issue.path}",
                Code.RECORD_INVALID,
                issue.detail,
            )
        )

    if type(eligibility_result) is not ExpressionEligibilityResult:
        issues.append(
            _issue(
                "projection_input.expression_eligibility_result",
                Code.TYPE_MISMATCH,
                "exact Slice 42C result required",
            )
        )
    else:
        if eligibility_result.selected_meaning_chain_admitted is not True:
            issues.append(
                _issue(
                    "projection_input.expression_eligibility_result.selected_meaning_chain_admitted",
                    Code.SLICE42C_STATE_MISMATCH,
                    "exact selected-meaning chain admission required",
                )
            )
        if eligibility_result.outward_expression_authority_admitted is not True:
            issues.append(
                _issue(
                    "projection_input.expression_eligibility_result.outward_expression_authority_admitted",
                    Code.SLICE42C_STATE_MISMATCH,
                    "exact outward-expression authority admission required",
                )
            )
        if eligibility_result.held_pending_authority is True:
            issues.append(
                _issue(
                    "projection_input.expression_eligibility_result.held_pending_authority",
                    Code.PROJECTION_AUTHORITY_MISSING,
                    "held Slice 42C authority state cannot enter projection",
                )
            )
        if eligibility_result.preservation_obligations_projected is not False:
            issues.append(
                _issue(
                    "projection_input.expression_eligibility_result.preservation_obligations_projected",
                    Code.SLICE42C_STATE_MISMATCH,
                    "predecessor must remain pre-projection",
                )
            )

    outward_authority = eligibility_input.outward_expression_authority_record
    if outward_authority.preservation_obligation_projection_authorized is not False:
        issues.append(
            _issue(
                "projection_input.expression_eligibility_evaluation_input.outward_expression_authority_record.preservation_obligation_projection_authorized",
                Code.DOWNSTREAM_AUTHORITY,
                "Slice 42C authority must not self-grant Slice 42D projection",
            )
        )

    issues.extend(
        validate_projection_authority_record(
            value.projection_authority_record,
            projection_input=value,
        ).issues
    )

    prohibited_requests = (
        "scope_expansion_requested",
        "certainty_upgrade_requested",
        "evidence_status_upgrade_requested",
        "limitation_omission_requested",
        "caveat_omission_requested",
        "refusal_softening_requested",
        "unresolved_resolution_requested",
        "ambiguity_erasure_requested",
        "unsupported_state_erasure_requested",
        "memory_authority_upgrade_requested",
        "external_resource_status_upgrade_requested",
        "delivery_authority_upgrade_requested",
        "selected_meaning_rewrite_requested",
        "downstream_authority_requested",
    )

    for name in prohibited_requests:
        actual = getattr(value, name)
        if type(actual) is not bool:
            issues.append(
                _issue(
                    f"projection_input.{name}",
                    Code.TYPE_MISMATCH,
                    "exact bool required",
                )
            )
        elif actual is not False:
            issues.append(
                _issue(
                    f"projection_input.{name}",
                    Code.PROHIBITED_REQUEST,
                    "prohibited projection request must remain false",
                )
            )

    # Current accepted sources carry no evidence validation, memory access or
    # write, external-resource load, delivery, or human-readable output.
    closeout = eligibility_input.selected_meaning_closeout_result
    selected_package = closeout.integration_input.selected_meaning_package
    negative_source_flags = (
        (closeout.evidence_validated, "closeout.evidence_validated"),
        (closeout.memory_read_performed, "closeout.memory_read_performed"),
        (closeout.memory_write_performed, "closeout.memory_write_performed"),
        (closeout.delivered, "closeout.delivered"),
        (selected_package.evidence_validated, "package.evidence_validated"),
        (selected_package.memory_accessed, "package.memory_accessed"),
        (selected_package.memory_written, "package.memory_written"),
        (selected_package.external_resource_loaded, "package.external_resource_loaded"),
        (selected_package.delivered, "package.delivered"),
        (eligibility_result.evidence_validated, "slice42c.evidence_validated"),
        (eligibility_result.memory_accessed_or_written, "slice42c.memory_accessed_or_written"),
        (eligibility_result.external_resource_loaded, "slice42c.external_resource_loaded"),
        (eligibility_result.delivered, "slice42c.delivered"),
        (eligibility_result.human_readable_text_produced, "slice42c.human_readable_text_produced"),
    )
    for actual, label in negative_source_flags:
        if actual is not False:
            issues.append(
                _issue(
                    f"projection_input.{label}",
                    Code.SLICE42C_STATE_MISMATCH,
                    "accepted predecessor status must remain false",
                )
            )

    try:
        expected_id = expected_record_id(value)
        if value.projection_input_id != expected_id:
            issues.append(
                _issue(
                    "projection_input.projection_input_id",
                    Code.IDENTITY_MISMATCH,
                    "deterministic identity mismatch",
                )
            )
    except Exception as error:
        issues.append(
            _issue(
                "projection_input.projection_input_id",
                Code.IDENTITY_MISMATCH,
                str(error),
            )
        )

    return _report(issues)


def validate_obligation_package(
    value: Any,
    *,
    projection_input: PreservationObligationProjectionInput | None = None,
) -> Report:
    if type(value) is not ExpressionObligationPackage:
        return _report(
            [
                _issue(
                    "obligation_package",
                    Code.TYPE_MISMATCH,
                    "exact ExpressionObligationPackage required",
                )
            ]
        )

    issues: list[Issue] = []

    for name in (
        "obligation_package_id",
        "projection_input_ref",
        "expression_eligibility_result_ref",
        "projection_authority_record_ref",
        "selected_meaning_source_custody_ref",
        "outward_expression_authority_requirement_ref",
        "outward_expression_authority_record_ref",
    ):
        issues.extend(
            _validate_identifier(
                getattr(value, name),
                f"obligation_package.{name}",
            )
        )

    if (
        type(value.obligation_package_digest) is not str
        or not _SHA256.fullmatch(value.obligation_package_digest)
    ):
        issues.append(
            _issue(
                "obligation_package.obligation_package_digest",
                Code.DIGEST_MISMATCH,
                "lowercase SHA-256 digest required",
            )
        )

    tuple_fields = (
        "selected_meaning_refs",
        "active_scope_refs",
        "certainty_level_refs",
        "evidence_status_refs",
        "inherited_limitation_refs",
        "required_caveat_refs",
        "refusal_relevant_boundary_refs",
        "unresolved_condition_refs",
        "ambiguity_refs",
        "unsupported_state_refs",
        "memory_authority_refs",
        "external_resource_status_refs",
        "delivery_authority_refs",
        "privacy_identity_boundary_refs",
        "preservation_class_refs",
        "predecessor_receipt_refs",
        "trace_refs",
        "provenance_refs",
        "version_refs",
    )
    required_nonempty = {
        "selected_meaning_refs",
        "active_scope_refs",
        "certainty_level_refs",
        "evidence_status_refs",
        "memory_authority_refs",
        "external_resource_status_refs",
        "delivery_authority_refs",
        "preservation_class_refs",
        "predecessor_receipt_refs",
        "trace_refs",
        "provenance_refs",
        "version_refs",
    }

    for name in tuple_fields:
        issues.extend(
            _validate_identifier_tuple(
                getattr(value, name),
                f"obligation_package.{name}",
                allow_empty=name not in required_nonempty,
            )
        )

    if projection_input is not None:
        eligibility_input = (
            projection_input.expression_eligibility_evaluation_input
        )
        eligibility_result = projection_input.expression_eligibility_result
        projection_authority = projection_input.projection_authority_record
        source = eligibility_input.selected_meaning_source_custody
        requirement = (
            eligibility_input.outward_expression_authority_requirement
        )
        outward_authority = (
            eligibility_input.outward_expression_authority_record
        )

        expected_refs = {
            "projection_input_ref": projection_input.projection_input_id,
            "expression_eligibility_result_ref": eligibility_result.result_id,
            "projection_authority_record_ref": (
                projection_authority.projection_authority_record_id
            ),
            "selected_meaning_source_custody_ref": source.source_custody_id,
            "outward_expression_authority_requirement_ref": (
                requirement.authority_requirement_id
            ),
            "outward_expression_authority_record_ref": (
                outward_authority.authority_record_id
            ),
            "source_eligibility_outcome": eligibility_result.outcome,
            "planning_progression_eligible": (
                eligibility_result.eligible_for_expression_planning
            ),
        }
        for name, expected in expected_refs.items():
            _expect_equal(
                issues,
                f"obligation_package.{name}",
                getattr(value, name),
                expected,
                Code.SLICE42C_STATE_MISMATCH,
                "exact Slice 42C predecessor reference or status required",
            )

        try:
            derived = derive_obligation_values(projection_input)
        except Exception as error:
            issues.append(
                _issue(
                    "obligation_package.derived_values",
                    Code.RECORD_INVALID,
                    str(error),
                )
            )
            derived = {}

        field_codes = {
            "selected_meaning_refs": Code.SELECTED_MEANING_MISMATCH,
            "active_scope_refs": Code.ACTIVE_SCOPE_MISMATCH,
            "certainty_level_refs": Code.CERTAINTY_MISMATCH,
            "evidence_status_refs": Code.EVIDENCE_STATUS_MISMATCH,
            "inherited_limitation_refs": Code.LIMITATION_MISMATCH,
            "required_caveat_refs": Code.CAVEAT_MISMATCH,
            "refusal_relevant_boundary_refs": (
                Code.REFUSAL_BOUNDARY_MISMATCH
            ),
            "unresolved_condition_refs": (
                Code.UNRESOLVED_CONDITION_MISMATCH
            ),
            "ambiguity_refs": Code.AMBIGUITY_MISMATCH,
            "unsupported_state_refs": Code.UNSUPPORTED_STATE_MISMATCH,
            "memory_authority_refs": Code.MEMORY_AUTHORITY_MISMATCH,
            "external_resource_status_refs": (
                Code.EXTERNAL_RESOURCE_STATUS_MISMATCH
            ),
            "delivery_authority_refs": Code.DELIVERY_AUTHORITY_MISMATCH,
            "privacy_identity_boundary_refs": Code.OBLIGATION_CATEGORY_MISMATCH,
            "preservation_class_refs": Code.OBLIGATION_CATEGORY_MISMATCH,
            "predecessor_receipt_refs": Code.PREDECESSOR_RECEIPT_MISMATCH,
            "trace_refs": Code.OBLIGATION_CATEGORY_MISMATCH,
            "provenance_refs": Code.OBLIGATION_CATEGORY_MISMATCH,
            "version_refs": Code.OBLIGATION_CATEGORY_MISMATCH,
        }
        for name, code in field_codes.items():
            if name in derived:
                _expect_equal(
                    issues,
                    f"obligation_package.{name}",
                    getattr(value, name),
                    derived[name],
                    code,
                    "exact deterministic projected value required",
                )

    required_true = (
        "exact_slice42c_state_verified",
        "exact_projection_authority_verified",
        "obligation_categories_separately_projected",
        "selected_meaning_preserved",
        "active_scope_preserved",
        "certainty_preserved",
        "evidence_status_preserved",
        "inherited_limitations_preserved",
        "required_caveats_preserved",
        "refusal_boundaries_preserved",
        "unresolved_conditions_preserved",
        "ambiguity_preserved",
        "unsupported_states_preserved",
        "memory_authority_preserved",
        "external_resource_status_preserved",
        "delivery_authority_preserved",
        "projection_performed",
        "obligation_package_created",
    )
    for name in required_true:
        if getattr(value, name) is not True:
            issues.append(
                _issue(
                    f"obligation_package.{name}",
                    Code.OBLIGATION_CATEGORY_MISMATCH,
                    "required projection proof flag must be true",
                )
            )

    required_false = (
        "scope_upgraded",
        "certainty_upgraded",
        "evidence_status_upgraded",
        "limitation_omitted",
        "caveat_omitted",
        "refusal_softened",
        "unresolved_condition_resolved",
        "ambiguity_erased",
        "unsupported_state_erased_or_guessed",
        "memory_authority_upgraded",
        "external_resource_status_upgraded",
        "delivery_authority_upgraded",
        "selected_meaning_rewritten",
        "human_readable_text_produced",
        "governed_outward_meaning_created",
        "expression_plan_created",
        "expression_candidate_created",
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
    for name in required_false:
        if getattr(value, name) is not False:
            issues.append(
                _issue(
                    f"obligation_package.{name}",
                    Code.DOWNSTREAM_AUTHORITY,
                    "projection must not create or upgrade downstream authority",
                )
            )

    try:
        if value.obligation_package_digest != expected_package_digest(value):
            issues.append(
                _issue(
                    "obligation_package.obligation_package_digest",
                    Code.CANONICAL_MISMATCH,
                    "canonical package digest mismatch",
                )
            )
        if value.obligation_package_id != expected_package_id(value):
            issues.append(
                _issue(
                    "obligation_package.obligation_package_id",
                    Code.IDENTITY_MISMATCH,
                    "deterministic package identity mismatch",
                )
            )
    except Exception as error:
        issues.append(
            _issue(
                "obligation_package.identity",
                Code.CANONICAL_MISMATCH,
                str(error),
            )
        )

    return _report(issues)


def validate_projection_result(
    value: Any,
    *,
    projection_input: PreservationObligationProjectionInput | None = None,
) -> Report:
    if type(value) is not PreservationObligationProjectionResult:
        return _report(
            [
                _issue(
                    "projection_result",
                    Code.TYPE_MISMATCH,
                    "exact PreservationObligationProjectionResult required",
                )
            ]
        )

    issues: list[Issue] = []

    if projection_input is not None:
        issues.extend(validate_projection_input(projection_input).issues)
        issues.extend(
            validate_obligation_package(
                value.obligation_package,
                projection_input=projection_input,
            ).issues
        )

        eligibility_result = projection_input.expression_eligibility_result
        expected_status = {
            "projection_input_ref": projection_input.projection_input_id,
            "source_eligibility_outcome": eligibility_result.outcome,
            "eligible_for_expression_planning": (
                eligibility_result.eligible_for_expression_planning
            ),
            "held_pending_authority": eligibility_result.held_pending_authority,
            "blocked": eligibility_result.blocked,
            "refusal_preserving": eligibility_result.refusal_preserving,
            "unresolved_preserving": eligibility_result.unresolved_preserving,
            "indeterminate": eligibility_result.indeterminate,
        }
        for name, expected in expected_status.items():
            _expect_equal(
                issues,
                f"projection_result.{name}",
                getattr(value, name),
                expected,
                Code.SLICE42C_STATE_MISMATCH,
                "exact Slice 42C disposition custody required",
            )
    else:
        issues.extend(validate_obligation_package(value.obligation_package).issues)

    issues.extend(
        _validate_identifier(value.result_id, "projection_result.result_id")
    )
    if type(value.result_digest) is not str or not _SHA256.fullmatch(
        value.result_digest
    ):
        issues.append(
            _issue(
                "projection_result.result_digest",
                Code.DIGEST_MISMATCH,
                "lowercase SHA-256 digest required",
            )
        )

    if value.required_law_refs != SLICE42D_GOVERNING_AUTHORITY_REFS:
        issues.append(
            _issue(
                "projection_result.required_law_refs",
                Code.OBLIGATION_CATEGORY_MISMATCH,
                "exact governing authority references required",
            )
        )
    if value.permanent_boundaries != SLICE42D_PERMANENT_BOUNDARIES:
        issues.append(
            _issue(
                "projection_result.permanent_boundaries",
                Code.OBLIGATION_CATEGORY_MISMATCH,
                "exact permanent boundaries required",
            )
        )
    if value.prohibited_authority != SLICE42D_PROHIBITED_AUTHORITY:
        issues.append(
            _issue(
                "projection_result.prohibited_authority",
                Code.OBLIGATION_CATEGORY_MISMATCH,
                "exact prohibited-authority list required",
            )
        )

    expected_finding_kinds = tuple(
        PreservationObligationProjectionFindingKind
    )
    actual_finding_kinds = tuple(
        finding.finding_kind for finding in value.findings
    )
    if actual_finding_kinds != expected_finding_kinds:
        issues.append(
            _issue(
                "projection_result.findings",
                Code.FINDING_MISMATCH,
                "exact ordered finding-kind set required",
            )
        )

    identifiers = [
        value.obligation_package.obligation_package_id,
        *(finding.finding_id for finding in value.findings),
    ]
    if len(identifiers) != len(set(identifiers)):
        issues.append(
            _issue(
                "projection_result.findings",
                Code.DUPLICATE_IDENTIFIER,
                "duplicate package or finding identifiers prohibited",
            )
        )

    for index, finding in enumerate(value.findings):
        path = f"projection_result.findings[{index}]"
        if type(finding) is not PreservationObligationProjectionFinding:
            issues.append(
                _issue(
                    path,
                    Code.TYPE_MISMATCH,
                    "exact finding record required",
                )
            )
            continue
        if finding.projection_input_ref != value.projection_input_ref:
            issues.append(
                _issue(
                    f"{path}.projection_input_ref",
                    Code.FINDING_MISMATCH,
                    "finding input reference mismatch",
                )
            )
        if (
            finding.obligation_package_ref
            != value.obligation_package.obligation_package_id
        ):
            issues.append(
                _issue(
                    f"{path}.obligation_package_ref",
                    Code.FINDING_MISMATCH,
                    "finding package reference mismatch",
                )
            )
        issues.extend(
            _validate_identifier_tuple(
                finding.basis_refs,
                f"{path}.basis_refs",
                allow_empty=False,
            )
        )
        issues.extend(
            _validate_identifier_tuple(
                finding.reason_refs,
                f"{path}.reason_refs",
                allow_empty=False,
            )
        )
        try:
            if finding.finding_id != expected_record_id(finding):
                issues.append(
                    _issue(
                        f"{path}.finding_id",
                        Code.IDENTITY_MISMATCH,
                        "deterministic finding identity mismatch",
                    )
                )
        except Exception as error:
            issues.append(
                _issue(
                    f"{path}.finding_id",
                    Code.IDENTITY_MISMATCH,
                    str(error),
                )
            )

    if value.preservation_obligations_projected is not True:
        issues.append(
            _issue(
                "projection_result.preservation_obligations_projected",
                Code.OBLIGATION_CATEGORY_MISMATCH,
                "successful result must record projection",
            )
        )
    if value.obligation_package_created is not True:
        issues.append(
            _issue(
                "projection_result.obligation_package_created",
                Code.OBLIGATION_CATEGORY_MISMATCH,
                "successful result must record package creation",
            )
        )

    downstream_false = (
        "governed_outward_meaning_created",
        "expression_plan_created",
        "expression_candidate_created",
        "human_readable_text_produced",
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
            issues.append(
                _issue(
                    f"projection_result.{name}",
                    Code.DOWNSTREAM_AUTHORITY,
                    "Slice 42D downstream authority must remain false",
                )
            )

    if len(SLICE42D_OBLIGATION_CATEGORY_NAMES) != 10:
        issues.append(
            _issue(
                "projection_result.obligation_categories",
                Code.OBLIGATION_CATEGORY_MISMATCH,
                "exact ten-category projection contract required",
            )
        )

    try:
        if value.result_digest != expected_result_digest(value):
            issues.append(
                _issue(
                    "projection_result.result_digest",
                    Code.CANONICAL_MISMATCH,
                    "canonical result digest mismatch",
                )
            )
        if value.result_id != expected_result_id(value):
            issues.append(
                _issue(
                    "projection_result.result_id",
                    Code.IDENTITY_MISMATCH,
                    "deterministic result identity mismatch",
                )
            )
    except Exception as error:
        issues.append(
            _issue(
                "projection_result.identity",
                Code.CANONICAL_MISMATCH,
                str(error),
            )
        )

    return _report(issues)


def assert_valid_projection_input(
    value: PreservationObligationProjectionInput,
) -> None:
    report = validate_projection_input(value)
    if not report.ok:
        raise PreservationObligationProjectionValidationError(report)


def assert_valid_projection_result(
    value: PreservationObligationProjectionResult,
    *,
    projection_input: PreservationObligationProjectionInput | None = None,
) -> None:
    report = validate_projection_result(
        value,
        projection_input=projection_input,
    )
    if not report.ok:
        raise PreservationObligationProjectionValidationError(report)


__all__ = (
    "assert_valid_projection_input",
    "assert_valid_projection_result",
    "validate_obligation_package",
    "validate_projection_authority_record",
    "validate_projection_input",
    "validate_projection_result",
)
