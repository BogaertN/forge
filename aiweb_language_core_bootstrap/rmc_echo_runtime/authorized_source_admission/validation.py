"""Fail-closed exact accepted Slice 42 source validation for Slice 43C."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any

from ...meaning_structure_manifest.serialization import (
    canonical_manifest_sha256,
)
from ...outward_expression_runtime import expression_eligibility
from ...outward_expression_runtime import expression_plan_construction
from ...outward_expression_runtime import (
    msm_outward_expression_integration,
)
from ...outward_expression_runtime import (
    preservation_obligation_projection,
)
from ...outward_expression_runtime import surface_realization
from ...outward_expression_runtime.disabled_outward_expression_closeout import (
    DisabledOutwardExpressionCloseoutResult,
    Slice42CloseoutStatus,
    validate_result as validate_closeout_result,
)
from ..governed_lifecycle import (
    expected_record_id as expected_core_record_id,
    validate_record as validate_core_record,
)
from ..schema import (
    AuthorizedMeaningReferenceRecord,
    EchoValidationInputBoundaryRecord,
    ProposedExpressionReferenceRecord,
)
from .authority import (
    EXACT_ACCEPTED_ID_MAP,
    EXACT_REALIZED_TEXT_SHA256,
    EXACT_SOURCE_MANIFEST_SHA256,
    EXACT_SUCCESSOR_MANIFEST_SHA256,
    REQUESTED_OPERATION,
    SLICE43C_PROFILE_VERSION,
    SLICE43C_SCHEMA_VERSION,
)
from .identity import (
    expected_package_digest,
    expected_package_id,
    expected_record_id,
    expected_result_digest,
    expected_result_id,
)
from .schema import (
    AuthorizedMeaningAdmissionRecord,
    EchoValidationAdmissionPackage,
    ProposedExpressionAdmissionRecord,
    SourceAdmissionCode,
    SourceAdmissionIssue,
    SourceAdmissionRequest,
    SourceAdmissionResult,
    SourceAdmissionValidationReport,
)


def _issue(
    path: str,
    code: SourceAdmissionCode,
    detail: str,
) -> SourceAdmissionIssue:
    return SourceAdmissionIssue(path=path, code=code, detail=detail)


def _report(
    issues: list[SourceAdmissionIssue] | tuple[SourceAdmissionIssue, ...],
) -> SourceAdmissionValidationReport:
    unique: list[SourceAdmissionIssue] = []
    seen: set[tuple[str, str, str]] = set()
    for item in issues:
        key = (item.path, item.code.value, item.detail)
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return SourceAdmissionValidationReport(tuple(unique))


def _safe_attr(value: object, *path: str) -> Any:
    current = value
    for name in path:
        current = getattr(current, name)
    return current


def _source_objects(source: DisabledOutwardExpressionCloseoutResult) -> dict[str, Any]:
    integration_input = source.integration_input
    integration_result = source.integration_result
    assert integration_input is not None
    assert integration_result is not None
    surface_input = integration_input.surface_realization_input
    surface_result = integration_input.surface_realization_result
    plan_input = surface_input.plan_input
    plan_result = surface_input.plan_result
    projection_input = plan_input.projection_input
    projection_result = plan_input.projection_result
    eligibility_input = projection_input.expression_eligibility_evaluation_input
    eligibility_result = projection_input.expression_eligibility_result
    selected_result = integration_input.source_selected_meaning_integration_result
    selected_record = selected_result.integrated_selected_meaning_record
    candidate = surface_result.expression_candidate
    outward = integration_result.governed_outward_meaning_record
    expression_link = integration_result.expression_link_record
    return {
        "integration_input": integration_input,
        "integration_result": integration_result,
        "surface_input": surface_input,
        "surface_result": surface_result,
        "plan_input": plan_input,
        "plan_result": plan_result,
        "projection_input": projection_input,
        "projection_result": projection_result,
        "eligibility_input": eligibility_input,
        "eligibility_result": eligibility_result,
        "selected_result": selected_result,
        "selected_record": selected_record,
        "candidate": candidate,
        "outward": outward,
        "expression_link": expression_link,
    }


def validate_exact_source(
    source: object,
) -> SourceAdmissionValidationReport:
    issues: list[SourceAdmissionIssue] = []
    if type(source) is not DisabledOutwardExpressionCloseoutResult:
        return _report([
            _issue(
                "source",
                SourceAdmissionCode.SOURCE_TYPE_INVALID,
                "exact DisabledOutwardExpressionCloseoutResult required",
            )
        ])

    if source.status is not Slice42CloseoutStatus.COMPLETED:
        issues.append(_issue(
            "source.status",
            SourceAdmissionCode.SOURCE_NOT_COMPLETED,
            "exact completed Slice 42H closeout required",
        ))
    if source.result_id != EXACT_ACCEPTED_ID_MAP["slice42h_result"]:
        issues.append(_issue(
            "source.result_id",
            SourceAdmissionCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "result is not the exact accepted Slice 42H result",
        ))
    if source.fixture_id != EXACT_ACCEPTED_ID_MAP["slice42h_fixture"]:
        issues.append(_issue(
            "source.fixture_id",
            SourceAdmissionCode.SOURCE_NOT_ACCEPTED,
            "fixture is not the closed accepted Slice 42H fixture",
        ))
    if source.acceptance_record.record_id != EXACT_ACCEPTED_ID_MAP["slice42h_acceptance"]:
        issues.append(_issue(
            "source.acceptance_record.record_id",
            SourceAdmissionCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "acceptance record is not the exact accepted identity",
        ))
    if not source.acceptance_record.slice42_closed:
        issues.append(_issue(
            "source.acceptance_record.slice42_closed",
            SourceAdmissionCode.SOURCE_NOT_ACCEPTED,
            "Slice 42 acceptance record must be closed",
        ))
    if source.integration_input is None or source.integration_result is None:
        issues.append(_issue(
            "source.integration",
            SourceAdmissionCode.MISSING_REQUIRED_LINK,
            "Slice 42G input and result are both required",
        ))
        return _report(issues)

    try:
        objects = _source_objects(source)
    except (AttributeError, TypeError, AssertionError) as error:
        issues.append(_issue(
            "source",
            SourceAdmissionCode.MISSING_REQUIRED_LINK,
            f"required nested source record is missing: {error}",
        ))
        return _report(issues)

    integration_input = objects["integration_input"]
    integration_result = objects["integration_result"]
    surface_input = objects["surface_input"]
    surface_result = objects["surface_result"]
    plan_input = objects["plan_input"]
    plan_result = objects["plan_result"]
    projection_input = objects["projection_input"]
    projection_result = objects["projection_result"]
    eligibility_input = objects["eligibility_input"]
    eligibility_result = objects["eligibility_result"]
    selected_result = objects["selected_result"]
    selected_record = objects["selected_record"]
    candidate = objects["candidate"]
    outward = objects["outward"]
    expression_link = objects["expression_link"]

    version_checks = (
        ("source.schema_version", source.schema_version, "aiweb-slice42h-disabled-outward-expression-closeout-v1"),
        ("integration_input.schema_version", integration_input.schema_version, "aiweb-language-core-slice42g-msm-outward-expression-integration-v1"),
        ("integration_result.schema_version", integration_result.schema_version, "aiweb-language-core-slice42g-msm-outward-expression-integration-v1"),
        ("surface_input.schema_version", surface_input.schema_version, "aiweb-slice42f-deterministic-surface-realization-v1"),
        ("surface_result.schema_version", surface_result.schema_version, "aiweb-slice42f-deterministic-surface-realization-v1"),
        ("plan_input.schema_version", plan_input.schema_version, "aiweb-slice42e-controlled-expression-plan-construction-v1"),
        ("plan_result.schema_version", plan_result.schema_version, "aiweb-slice42e-controlled-expression-plan-construction-v1"),
        ("projection_input.schema_version", projection_input.schema_version, "aiweb-slice42d-preservation-obligation-projection-v1"),
        ("projection_result.schema_version", projection_result.schema_version, "aiweb-slice42d-preservation-obligation-projection-v1"),
        ("eligibility_input.schema_version", eligibility_input.schema_version, "aiweb-slice42c-authorized-meaning-admission-expression-eligibility-v1"),
        ("eligibility_result.schema_version", eligibility_result.schema_version, "aiweb-slice42c-authorized-meaning-admission-expression-eligibility-v1"),
        ("selected_result.schema_version", selected_result.schema_version, "aiweb-language-core-slice41e-msm-selected-meaning-integration-v1"),
        ("selected_record.schema_version", selected_record.schema_version, "MSM-v1"),
        ("outward.schema_version", outward.schema_version, "MSM-v1"),
        ("expression_link.schema_version", expression_link.schema_version, "MSM-v1"),
        ("candidate.schema_version", candidate.schema_version, "aiweb-slice42f-deterministic-surface-realization-v1"),
    )
    for path, observed, expected in version_checks:
        if observed != expected:
            issues.append(_issue(
                path,
                SourceAdmissionCode.UNSUPPORTED_VERSION,
                f"expected {expected!r}",
            ))

    id_checks = (
        ("integration_input.integration_input_id", integration_input.integration_input_id, "slice42g_input"),
        ("integration_result.result_id", integration_result.result_id, "slice42g_result"),
        ("integration_result.receipt.receipt_id", integration_result.receipt.receipt_id, "slice42g_receipt"),
        ("integration_result.source_manifest.manifest_id", integration_result.source_manifest.manifest_id, "source_manifest"),
        ("integration_result.successor_manifest.manifest_id", integration_result.successor_manifest.manifest_id, "successor_manifest"),
        ("selected_record.record_id", selected_record.record_id, "selected_meaning"),
        ("selected_record.selected_candidate_ref", selected_record.selected_candidate_ref, "selected_candidate"),
        ("outward.record_id", outward.record_id, "governed_outward_meaning"),
        ("expression_link.record_id", expression_link.record_id, "expression_link"),
        ("candidate.expression_candidate_id", candidate.expression_candidate_id, "expression_candidate"),
        ("surface_input.realization_input_id", surface_input.realization_input_id, "slice42f_input"),
        ("surface_result.result_id", surface_result.result_id, "slice42f_result"),
        ("surface_result.realization_receipt.realization_receipt_id", surface_result.realization_receipt.realization_receipt_id, "slice42f_receipt"),
        ("surface_result.realization_trace.realization_trace_id", surface_result.realization_trace.realization_trace_id, "slice42f_trace"),
        ("plan_result.expression_plan.expression_plan_id", plan_result.expression_plan.expression_plan_id, "slice42e_plan"),
        ("projection_result.obligation_package.obligation_package_id", projection_result.obligation_package.obligation_package_id, "slice42d_obligation"),
        ("eligibility_result.result_id", eligibility_result.result_id, "slice42c_result"),
        ("selected_result.companion.content_proof_ref", selected_result.companion.content_proof_ref, "selected_content_proof"),
        ("selected_result.authority_reference_record.record_id", selected_result.authority_reference_record.record_id, "selection_authority_reference"),
        ("integration_result.external_authority_reference_record.record_id", integration_result.external_authority_reference_record.record_id, "outward_authority_reference"),
        ("integration_result.selected_to_outward_trace.record_id", integration_result.selected_to_outward_trace.record_id, "selected_to_outward_trace"),
        ("integration_result.outward_to_expression_trace.record_id", integration_result.outward_to_expression_trace.record_id, "outward_to_expression_trace"),
    )
    for path, observed, key in id_checks:
        if observed != EXACT_ACCEPTED_ID_MAP[key]:
            issues.append(_issue(
                path,
                SourceAdmissionCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
                f"expected exact accepted identity {EXACT_ACCEPTED_ID_MAP[key]}",
            ))

    try:
        source_manifest_sha256 = canonical_manifest_sha256(
            integration_result.source_manifest
        )
        successor_manifest_sha256 = canonical_manifest_sha256(
            integration_result.successor_manifest
        )
    except Exception as error:
        issues.append(_issue(
            "source.manifests",
            SourceAdmissionCode.IDENTITY_MISMATCH,
            f"manifest digest calculation failed: {error}",
        ))
    else:
        if source_manifest_sha256 != EXACT_SOURCE_MANIFEST_SHA256:
            issues.append(_issue(
                "source_manifest.sha256",
                SourceAdmissionCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
                "source manifest digest is not the accepted digest",
            ))
        if successor_manifest_sha256 != EXACT_SUCCESSOR_MANIFEST_SHA256:
            issues.append(_issue(
                "successor_manifest.sha256",
                SourceAdmissionCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
                "successor manifest digest is not the accepted digest",
            ))

    successor = integration_result.successor_manifest
    selected_ids = tuple(item.record_id for item in successor.selected_governed_meanings)
    outward_ids = tuple(item.record_id for item in successor.governed_outward_meanings)
    link_ids = tuple(item.record_id for item in successor.expression_links)
    if EXACT_ACCEPTED_ID_MAP["selected_meaning"] not in selected_ids:
        issues.append(_issue(
            "successor_manifest.selected_governed_meanings",
            SourceAdmissionCode.MISSING_REQUIRED_LINK,
            "exact selected governed meaning is absent",
        ))
    if EXACT_ACCEPTED_ID_MAP["governed_outward_meaning"] not in outward_ids:
        issues.append(_issue(
            "successor_manifest.governed_outward_meanings",
            SourceAdmissionCode.MISSING_REQUIRED_LINK,
            "exact governed outward meaning is absent",
        ))
    if EXACT_ACCEPTED_ID_MAP["expression_link"] not in link_ids:
        issues.append(_issue(
            "successor_manifest.expression_links",
            SourceAdmissionCode.MISSING_REQUIRED_LINK,
            "exact MSM-v1 expression link is absent",
        ))
    if successor.validation_links:
        issues.append(_issue(
            "successor_manifest.validation_links",
            SourceAdmissionCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
            "Slice 43C source may not already contain a validation link",
        ))
    if successor.delivery_or_containment_links:
        issues.append(_issue(
            "successor_manifest.delivery_or_containment_links",
            SourceAdmissionCode.ALREADY_DELIVERED_CANDIDATE,
            "already-delivered or contained source is not admissible",
        ))

    if (
        expression_link.governed_outward_meaning_ref != outward.record_id
        or expression_link.expression_candidate_ref
        != candidate.expression_candidate_id
    ):
        issues.append(_issue(
            "expression_link",
            SourceAdmissionCode.ORPHAN_EXPRESSION,
            "expression link does not bind the exact outward meaning and candidate",
        ))
    if (
        outward.prior_selected_meaning_ref != selected_record.record_id
        or outward.lineage_id != selected_record.lineage_id
        or expression_link.lineage_id != selected_record.lineage_id
    ):
        issues.append(_issue(
            "source.lineage",
            SourceAdmissionCode.INCONSISTENT_ANCESTRY,
            "selected meaning, outward meaning and expression link lineage differ",
        ))
    if (
        integration_result.external_authority_reference_record.external_object_ref
        != candidate.expression_candidate_id
    ):
        issues.append(_issue(
            "external_authority_reference.external_object_ref",
            SourceAdmissionCode.ORPHAN_EXPRESSION,
            "candidate is not bound to the exact outward-expression authority reference",
        ))
    if candidate.realized_text_sha256 != EXACT_REALIZED_TEXT_SHA256:
        issues.append(_issue(
            "candidate.realized_text_sha256",
            SourceAdmissionCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
            "realized text digest is not the accepted digest",
        ))

    delivered_flags = (
        source.delivered,
        source.delivery_authorized,
        integration_result.delivered,
        integration_result.delivery_authorized,
        surface_result.delivered,
        surface_result.delivery_authorized,
        surface_result.expression_candidate.delivered,
        surface_result.expression_candidate.delivery_authorized,
        integration_result.receipt.delivery_authorized_or_performed,
    )
    if any(delivered_flags):
        issues.append(_issue(
            "source.delivery",
            SourceAdmissionCode.ALREADY_DELIVERED_CANDIDATE,
            "candidate is already delivered or delivery-authorized",
        ))

    realization_authority = surface_input.realization_authority_record
    if not (
        realization_authority.authority_active
        and realization_authority.surface_realization_authorized
        and realization_authority.expression_candidate_creation_authorized
        and candidate.expression_candidate_created
        and candidate.unvalidated_expression_candidate
        and not candidate.echo_approved
    ):
        issues.append(_issue(
            "source.candidate_authority",
            SourceAdmissionCode.UNAUTHORIZED_CANDIDATE,
            "exact candidate-creation authority and unvalidated state required",
        ))

    # Fail closed before expensive predecessor validators when a direct
    # exact-source, link, version, delivery, or authority violation is
    # already proven. This keeps hostile malformed inputs bounded.
    if issues:
        return _report(issues)

    predecessor_reports = (
        ("slice42h", validate_closeout_result(source)),
        ("slice42g.input", msm_outward_expression_integration.validate_integration_input(integration_input)),
        ("slice42g.result", msm_outward_expression_integration.validate_integration_result(integration_result, integration_input=integration_input)),
        ("slice42f.input", surface_realization.validate_surface_realization_input(surface_input)),
        ("slice42f.result", surface_realization.validate_surface_realization_result(surface_result, realization_input=surface_input)),
        ("slice42e.input", expression_plan_construction.validate_plan_input(plan_input)),
        ("slice42e.result", expression_plan_construction.validate_plan_result(plan_result, plan_input=plan_input)),
        ("slice42d.input", preservation_obligation_projection.validate_projection_input(projection_input)),
        ("slice42d.result", preservation_obligation_projection.validate_projection_result(projection_result, projection_input=projection_input)),
        ("slice42c.input", expression_eligibility.validate_evaluation_input(eligibility_input)),
        ("slice42c.result", expression_eligibility.validate_result(eligibility_result, evaluation_input=eligibility_input)),
    )
    for name, report in predecessor_reports:
        if not report.ok:
            issues.append(_issue(
                name,
                SourceAdmissionCode.PREDECESSOR_VALIDATION_FAILED,
                f"{len(report.issues)} predecessor validation issue(s)",
            ))

    if not (
        integration_result.exact_slice41e_chain_preserved
        and integration_result.exact_slice42f_candidate_preserved
        and integration_result.selected_meaning_preserved
        and integration_result.complete_successor_manifest_validated
        and integration_result.candidate_remains_unvalidated
        and source.complete_successor_manifest_validated
        and source.expression_candidate_remains_unvalidated
        and source.expression_link_custody_preserved
        and source.governed_outward_meaning_custody_preserved
    ):
        issues.append(_issue(
            "source.accepted_custody",
            SourceAdmissionCode.INCONSISTENT_ANCESTRY,
            "required accepted Slice 42 custody proofs are not all true",
        ))

    prohibited_flags = (
        source.echo_validation_performed,
        source.echo_approved,
        source.truth_determined,
        source.evidence_validated,
        source.permission_granted,
        source.execution_authorized,
        source.route_created,
        source.api_created,
        source.network_accessed,
        source.filesystem_write_performed,
        source.memory_write_performed,
        source.tool_invoked,
        source.action_performed,
        source.external_resource_loaded,
        source.language_model_used,
        source.embedding_used,
        source.vector_used,
        source.rag_used,
        source.semantic_similarity_used,
        source.neural_parser_used,
        source.hidden_classifier_used,
        source.gp014_superseded,
    )
    if any(prohibited_flags):
        issues.append(_issue(
            "source.prohibited_authority",
            SourceAdmissionCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
            "source contains a prohibited downstream authority consequence",
        ))

    return _report(issues)


def validate_request(
    request: object,
) -> SourceAdmissionValidationReport:
    issues: list[SourceAdmissionIssue] = []
    if type(request) is not SourceAdmissionRequest:
        return _report([
            _issue(
                "request",
                SourceAdmissionCode.REQUEST_TYPE_INVALID,
                "exact SourceAdmissionRequest required",
            )
        ])
    if request.schema_version != SLICE43C_SCHEMA_VERSION:
        issues.append(_issue(
            "request.schema_version",
            SourceAdmissionCode.UNSUPPORTED_VERSION,
            f"expected {SLICE43C_SCHEMA_VERSION}",
        ))
    if request.profile_version != SLICE43C_PROFILE_VERSION:
        issues.append(_issue(
            "request.profile_version",
            SourceAdmissionCode.UNSUPPORTED_VERSION,
            f"expected {SLICE43C_PROFILE_VERSION}",
        ))
    if request.requested_operation != REQUESTED_OPERATION:
        issues.append(_issue(
            "request.requested_operation",
            SourceAdmissionCode.REQUEST_OPERATION_INVALID,
            f"expected {REQUESTED_OPERATION}",
        ))
    if request.explicit_admission_request is not True:
        issues.append(_issue(
            "request.explicit_admission_request",
            SourceAdmissionCode.REQUEST_OPERATION_INVALID,
            "explicit admission request must be true",
        ))
    if request.raw_text is not None:
        issues.append(_issue(
            "request.raw_text",
            SourceAdmissionCode.RAW_TEXT_WITHOUT_ACCEPTED_ANCESTRY,
            "raw text is not an admissible Slice 43C input",
        ))
    try:
        expected = expected_record_id(request)
    except Exception as error:
        issues.append(_issue(
            "request.request_id",
            SourceAdmissionCode.REQUEST_ID_INVALID,
            f"request identity could not be calculated: {error}",
        ))
    else:
        if request.request_id != expected:
            issues.append(_issue(
                "request.request_id",
                SourceAdmissionCode.REQUEST_ID_INVALID,
                f"expected {expected}",
            ))
    # Fail closed before expensive predecessor validation when the request
    # envelope is already inadmissible. This prevents arbitrary raw text or
    # malformed requests from triggering traversal of accepted ancestry.
    if issues:
        return _report(issues)
    issues.extend(validate_exact_source(request.source_closeout_result).issues)
    return _report(issues)


def validate_admission_package(
    value: object,
) -> SourceAdmissionValidationReport:
    issues: list[SourceAdmissionIssue] = []
    if type(value) is not EchoValidationAdmissionPackage:
        return _report([
            _issue(
                "admission_package",
                SourceAdmissionCode.ADMISSION_RECORD_INVALID,
                "exact EchoValidationAdmissionPackage required",
            )
        ])
    try:
        if value.admission_package_digest != expected_package_digest(value):
            issues.append(_issue(
                "admission_package.admission_package_digest",
                SourceAdmissionCode.IDENTITY_MISMATCH,
                "package digest mismatch",
            ))
        if value.admission_package_id != expected_package_id(value):
            issues.append(_issue(
                "admission_package.admission_package_id",
                SourceAdmissionCode.IDENTITY_MISMATCH,
                "package identity mismatch",
            ))
    except Exception as error:
        issues.append(_issue(
            "admission_package",
            SourceAdmissionCode.IDENTITY_MISMATCH,
            f"package identity could not be calculated: {error}",
        ))

    for path, record in (
        ("authorized_meaning_reference", value.authorized_meaning_admission.authorized_meaning_reference),
        ("proposed_expression_reference", value.proposed_expression_admission.proposed_expression_reference),
        ("validation_input_boundary", value.validation_input_boundary),
    ):
        report = validate_core_record(record)
        if not report.ok:
            issues.append(_issue(
                path,
                SourceAdmissionCode.ADMISSION_RECORD_INVALID,
                f"{len(report.issues)} Slice 43B structural issue(s)",
            ))
        try:
            expected = expected_core_record_id(record)
        except Exception as error:
            issues.append(_issue(
                path,
                SourceAdmissionCode.IDENTITY_MISMATCH,
                f"core identity calculation failed: {error}",
            ))
        else:
            id_field = next(
                item.name
                for item in fields(record)
                if item.name.endswith("_id")
            )
            if getattr(record, id_field) != expected:
                issues.append(_issue(
                    path,
                    SourceAdmissionCode.IDENTITY_MISMATCH,
                    "core record identity mismatch",
                ))

    meaning = value.authorized_meaning_admission
    expression = value.proposed_expression_admission
    boundary = value.validation_input_boundary
    if boundary.authorized_meaning_reference != meaning.authorized_meaning_reference:
        issues.append(_issue(
            "validation_input_boundary.authorized_meaning_reference",
            SourceAdmissionCode.INCONSISTENT_ANCESTRY,
            "boundary does not contain the admitted meaning reference",
        ))
    if boundary.proposed_expression_reference != expression.proposed_expression_reference:
        issues.append(_issue(
            "validation_input_boundary.proposed_expression_reference",
            SourceAdmissionCode.INCONSISTENT_ANCESTRY,
            "boundary does not contain the admitted expression reference",
        ))
    if (
        meaning.authorized_meaning_reference.lineage_id
        != expression.proposed_expression_reference.lineage_id
    ):
        issues.append(_issue(
            "admission_package.lineage",
            SourceAdmissionCode.INCONSISTENT_ANCESTRY,
            "admitted meaning and expression lineages differ",
        ))
    required_true = (
        meaning.exact_accepted_ancestry_validated,
        meaning.identity_and_version_validated,
        meaning.source_admitted_for_later_comparison,
        expression.expression_candidate_authorized_for_admission,
        expression.exact_expression_link_validated,
        expression.exact_realization_identity_validated,
        expression.source_admitted_for_later_comparison,
        value.admitted_for_slice43d_comparison,
        value.exact_accepted_slice42_ancestry,
    )
    if not all(required_true):
        issues.append(_issue(
            "admission_package",
            SourceAdmissionCode.ADMISSION_RECORD_INVALID,
            "required admission proof booleans are not all true",
        ))
    prohibited = (
        meaning.raw_text_used,
        meaning.source_rewritten,
        meaning.alternatives_deleted,
        meaning.unresolved_conditions_resolved,
        expression.expression_candidate_already_delivered,
        expression.expression_candidate_echo_approved,
        expression.expression_rewritten,
        value.meaning_preservation_comparison_performed,
        value.validation_findings_created,
        value.drift_findings_created,
        value.materiality_decided,
        value.echo_disposition_decided,
        value.rejection_issued,
        value.containment_issued,
        value.msm_v1_modified_or_integrated,
        value.delivery_authorized_or_performed,
        value.truth_evidence_permission_execution_authority,
        value.route_api_network_filesystem_memory_tool_action_authority,
        value.model_or_similarity_authority_used,
        value.gp014_superseded,
    )
    if any(prohibited):
        issues.append(_issue(
            "admission_package",
            SourceAdmissionCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
            "admission package contains a prohibited performed consequence",
        ))
    return _report(issues)


def validate_result(
    value: object,
) -> SourceAdmissionValidationReport:
    issues: list[SourceAdmissionIssue] = []
    if type(value) is not SourceAdmissionResult:
        return _report([
            _issue(
                "result",
                SourceAdmissionCode.ADMISSION_RECORD_INVALID,
                "exact SourceAdmissionResult required",
            )
        ])
    try:
        if value.admission_result_digest != expected_result_digest(value):
            issues.append(_issue(
                "result.admission_result_digest",
                SourceAdmissionCode.IDENTITY_MISMATCH,
                "result digest mismatch",
            ))
        if value.admission_result_id != expected_result_id(value):
            issues.append(_issue(
                "result.admission_result_id",
                SourceAdmissionCode.IDENTITY_MISMATCH,
                "result identity mismatch",
            ))
    except Exception as error:
        issues.append(_issue(
            "result",
            SourceAdmissionCode.IDENTITY_MISMATCH,
            f"result identity could not be calculated: {error}",
        ))
    if value.source_admitted:
        if value.admission_package is None:
            issues.append(_issue(
                "result.admission_package",
                SourceAdmissionCode.ADMISSION_RECORD_INVALID,
                "admitted result requires an admission package",
            ))
        else:
            issues.extend(validate_admission_package(value.admission_package).issues)
        if value.rejection_codes:
            issues.append(_issue(
                "result.rejection_codes",
                SourceAdmissionCode.ADMISSION_RECORD_INVALID,
                "admitted result may not contain rejection codes",
            ))
    else:
        if value.admission_package is not None:
            issues.append(_issue(
                "result.admission_package",
                SourceAdmissionCode.ADMISSION_RECORD_INVALID,
                "held result may not contain an admission package",
            ))
        if not value.rejection_codes:
            issues.append(_issue(
                "result.rejection_codes",
                SourceAdmissionCode.ADMISSION_RECORD_INVALID,
                "held result requires at least one rejection code",
            ))
    prohibited = (
        value.raw_text_admitted,
        value.orphan_expression_admitted,
        value.recomputed_or_fabricated_identity_admitted,
        value.unsupported_version_admitted,
        value.missing_link_admitted,
        value.already_delivered_candidate_admitted,
        value.unauthorized_candidate_admitted,
        value.meaning_preservation_comparison_performed,
        value.drift_classification_performed,
        value.echo_disposition_decided,
        value.rejection_or_containment_issued,
        value.msm_v1_modified_or_integrated,
        value.delivered,
        value.downstream_authority_created,
        value.model_or_similarity_authority_used,
        value.gp014_superseded,
    )
    if any(prohibited):
        issues.append(_issue(
            "result",
            SourceAdmissionCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
            "result contains prohibited authority or rejected-source admission",
        ))
    return _report(issues)


__all__ = (
    "validate_admission_package",
    "validate_exact_source",
    "validate_request",
    "validate_result",
)
