"""Fail-closed Slice 42F validation."""

from __future__ import annotations

import hashlib
from typing import Any, Iterable

from ..expression_plan_construction import (
    ExpressionPlanConstructionInput,
    ExpressionPlanConstructionResult,
    ExpressionPlanDisposition,
    assert_valid_plan_input,
    assert_valid_plan_result,
)
from .authority import (
    DIGEST_ALGORITHM,
    SLICE42F_ADMITTED_RULE_REFS,
    SLICE42F_GOVERNING_AUTHORITY_REFS,
    SLICE42F_PERMANENT_BOUNDARIES,
    SLICE42F_PROFILE_KEY,
    SLICE42F_PROFILE_VERSION,
    SLICE42F_PROHIBITED_AUTHORITY,
    SLICE42F_REALIZATION_AUTHORITY_KEY,
    SLICE42F_REQUIRED_TEMPLATE_KEYS,
    SLICE42F_RESOURCE_PROFILE_KEY,
    SLICE42F_RESOURCE_PROFILE_VERSION,
    SLICE42F_SCHEMA_VERSION,
)
from .identity import (
    expected_candidate_digest,
    expected_candidate_id,
    expected_record_id,
    expected_result_digest,
    expected_result_id,
)
from .realizer import applied_resource_records, build_realization_segments, determine_realization_disposition
from .schema import (
    ControlledRealizationResourceBundle,
    ControlledRealizationResourceKind,
    ControlledRealizationResourceRecord,
    SurfaceRealizationAuthorityRecord,
    SurfaceRealizationFinding,
    SurfaceRealizationFindingKind,
    SurfaceRealizationInput,
    SurfaceRealizationReceipt,
    SurfaceRealizationResult,
    SurfaceRealizationTrace,
    SurfaceRealizationValidationCode as Code,
    SurfaceRealizationValidationError,
    SurfaceRealizationValidationIssue as Issue,
    SurfaceRealizationValidationReport as Report,
    UnvalidatedExpressionCandidate,
)


def _issue(path: str, code: Code, detail: str) -> Issue:
    return Issue(path=path, code=code, detail=detail)


def _report(issues: Iterable[Issue]) -> Report:
    return Report(tuple(issues))


def _valid_identifier(value: Any) -> bool:
    return type(value) is str and bool(value) and value.strip() == value and "\n" not in value and "\r" not in value and "\x00" not in value


def _id(value: Any, path: str) -> list[Issue]:
    return [] if _valid_identifier(value) else [_issue(path, Code.INVALID_IDENTIFIER, "exact non-empty identifier required")]


def _ids(values: Any, path: str) -> list[Issue]:
    if type(values) is not tuple:
        return [_issue(path, Code.TYPE_MISMATCH, "exact tuple required")]
    issues: list[Issue] = []
    seen: set[str] = set()
    for index, value in enumerate(values):
        item_path = f"{path}[{index}]"
        item_issues = _id(value, item_path)
        issues.extend(item_issues)
        if item_issues:
            continue
        if value in seen:
            issues.append(
                _issue(
                    item_path,
                    Code.RECORD_INVALID,
                    "duplicate values prohibited",
                )
            )
        seen.add(value)
    return issues


def _same(actual: Any, expected: Any, path: str, code: Code) -> list[Issue]:
    return [] if actual == expected else [_issue(path, code, f"expected={expected!r} actual={actual!r}")]


def _schema(value: Any, path: str) -> list[Issue]:
    return _same(
        getattr(value, "schema_version", None),
        SLICE42F_SCHEMA_VERSION,
        path + ".schema_version",
        Code.INVALID_VERSION,
    )


def _exact_bool(value: Any, path: str) -> list[Issue]:
    return (
        []
        if type(value) is bool
        else [_issue(path, Code.TYPE_MISMATCH, "exact bool required")]
    )


def _ordered_unique(*groups: tuple[str, ...]) -> tuple[str, ...]:
    ordered: dict[str, None] = {}
    for group in groups:
        for item in group:
            ordered.setdefault(item, None)
    return tuple(ordered)


def validate_resource_bundle(value: Any) -> Report:
    issues: list[Issue] = []
    if not isinstance(value, ControlledRealizationResourceBundle):
        return _report([_issue("resource_bundle", Code.TYPE_MISMATCH, "wrong record type")])
    issues.extend(_schema(value, "resource_bundle"))
    issues.extend(_same(value.resource_bundle_id, expected_record_id(value), "resource_bundle.resource_bundle_id", Code.IDENTITY_MISMATCH))
    issues.extend(_same(value.profile_key, SLICE42F_RESOURCE_PROFILE_KEY, "resource_bundle.profile_key", Code.INVALID_VERSION))
    issues.extend(_same(value.profile_version, SLICE42F_RESOURCE_PROFILE_VERSION, "resource_bundle.profile_version", Code.INVALID_VERSION))
    issues.extend(_same(value.admitted_rule_refs, SLICE42F_ADMITTED_RULE_REFS, "resource_bundle.admitted_rule_refs", Code.RESOURCE_BUNDLE_MISMATCH))
    issues.extend(_id(value.resource_authority_receipt_ref, "resource_bundle.resource_authority_receipt_ref"))
    if type(value.records) is not tuple or not value.records:
        issues.append(_issue("resource_bundle.records", Code.RESOURCE_BUNDLE_MISMATCH, "non-empty exact tuple required"))
    else:
        keys: list[str] = []
        ids: list[str] = []
        for index, record in enumerate(value.records):
            path = f"resource_bundle.records[{index}]"
            if not isinstance(record, ControlledRealizationResourceRecord):
                issues.append(_issue(path, Code.TYPE_MISMATCH, "wrong resource record type"))
                continue
            keys.append(record.resource_key)
            ids.append(record.resource_record_id)
            issues.extend(_schema(record, path))
            issues.extend(_same(record.resource_record_id, expected_record_id(record), path + ".resource_record_id", Code.IDENTITY_MISMATCH))
            issues.extend(_id(record.resource_key, path + ".resource_key"))
            issues.extend(_id(record.authority_ref, path + ".authority_ref"))
            issues.extend(
                _same(
                    record.resource_version,
                    SLICE42F_RESOURCE_PROFILE_VERSION,
                    path + ".resource_version",
                    Code.INVALID_VERSION,
                )
            )
            if not isinstance(record.resource_kind, ControlledRealizationResourceKind):
                issues.append(
                    _issue(
                        path + ".resource_kind",
                        Code.TYPE_MISMATCH,
                        "controlled resource kind required",
                    )
                )
            if type(record.resource_text) is not str or not record.resource_text or record.resource_text.strip() != record.resource_text:
                issues.append(_issue(path + ".resource_text", Code.RECORD_INVALID, "exact non-empty trimmed text required"))
            valid_dispositions = (
                type(record.permitted_plan_dispositions) is tuple
                and bool(record.permitted_plan_dispositions)
                and all(
                    isinstance(item, ExpressionPlanDisposition)
                    for item in record.permitted_plan_dispositions
                )
            )
            if not valid_dispositions:
                issues.append(_issue(path + ".permitted_plan_dispositions", Code.RECORD_INVALID, "permitted exact dispositions required"))
            else:
                if len(record.permitted_plan_dispositions) != len(
                    set(record.permitted_plan_dispositions)
                ):
                    issues.append(
                        _issue(
                            path + ".permitted_plan_dispositions",
                            Code.RECORD_INVALID,
                            "duplicate dispositions prohibited",
                        )
                    )
            for flag_name in (
                "admitted",
                "deterministic",
                "external_resource",
                "model_generated",
            ):
                issues.extend(
                    _exact_bool(getattr(record, flag_name), path + "." + flag_name)
                )
            if (
                valid_dispositions
                and record.resource_kind
                is ControlledRealizationResourceKind.DISPOSITION_TEMPLATE
            ):
                if record.bound_selected_meaning_ref is not None:
                    issues.append(
                        _issue(
                            path + ".bound_selected_meaning_ref",
                            Code.RESOURCE_BUNDLE_MISMATCH,
                            "disposition template cannot bind selected meaning",
                        )
                    )
                if (
                    len(record.permitted_plan_dispositions) != 1
                    or record.resource_key
                    != "template:"
                    + record.permitted_plan_dispositions[0].value
                ):
                    issues.append(
                        _issue(
                            path,
                            Code.RESOURCE_BUNDLE_MISMATCH,
                            "template key must exactly match its single disposition",
                        )
                    )
            elif (
                valid_dispositions
                and record.resource_kind
                is ControlledRealizationResourceKind.AUTHORIZED_CLAIM_TEXT
            ):
                issues.extend(
                    _id(
                        record.bound_selected_meaning_ref,
                        path + ".bound_selected_meaning_ref",
                    )
                )
                if record.permitted_plan_dispositions != (
                    ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN,
                ):
                    issues.append(
                        _issue(
                            path + ".permitted_plan_dispositions",
                            Code.RESOURCE_BUNDLE_MISMATCH,
                            "authorized claim text is restricted to authorized plan",
                        )
                    )
            if not record.admitted or not record.deterministic or record.external_resource or record.model_generated:
                issues.append(_issue(path, Code.UNADMITTED_RESOURCE, "resource must be admitted deterministic internal and non-model"))
        if len(keys) != len(set(keys)) or len(ids) != len(set(ids)):
            issues.append(_issue("resource_bundle.records", Code.RESOURCE_BUNDLE_MISMATCH, "resource keys and ids must be unique"))
        template_keys = {r.resource_key for r in value.records if isinstance(r, ControlledRealizationResourceRecord) and r.resource_kind is ControlledRealizationResourceKind.DISPOSITION_TEMPLATE}
        if not set(SLICE42F_REQUIRED_TEMPLATE_KEYS).issubset(template_keys):
            issues.append(_issue("resource_bundle.records", Code.MISSING_TEMPLATE, "all governed disposition templates required"))
    for flag_name in (
        "deterministic",
        "external_resource_loaded",
        "model_or_similarity_authority_used",
    ):
        issues.extend(
            _exact_bool(
                getattr(value, flag_name),
                "resource_bundle." + flag_name,
            )
        )
    if not value.deterministic or value.external_resource_loaded or value.model_or_similarity_authority_used:
        issues.append(_issue("resource_bundle", Code.UNADMITTED_RESOURCE, "bundle must be deterministic internal and non-model"))
    return _report(issues)


def validate_surface_realization_input(value: Any) -> Report:
    issues: list[Issue] = []
    if not isinstance(value, SurfaceRealizationInput):
        return _report([_issue("realization_input", Code.TYPE_MISMATCH, "wrong record type")])
    issues.extend(_schema(value, "realization_input"))
    if not isinstance(value.plan_input, ExpressionPlanConstructionInput):
        issues.append(
            _issue(
                "realization_input.plan_input",
                Code.TYPE_MISMATCH,
                "exact Slice 42E plan input required",
            )
        )
    if not isinstance(value.plan_result, ExpressionPlanConstructionResult):
        issues.append(
            _issue(
                "realization_input.plan_result",
                Code.TYPE_MISMATCH,
                "exact Slice 42E plan result required",
            )
        )
    if not isinstance(
        value.controlled_resource_bundle,
        ControlledRealizationResourceBundle,
    ):
        issues.append(
            _issue(
                "realization_input.controlled_resource_bundle",
                Code.TYPE_MISMATCH,
                "controlled resource bundle required",
            )
        )
    if not isinstance(
        value.realization_authority_record,
        SurfaceRealizationAuthorityRecord,
    ):
        issues.append(
            _issue(
                "realization_input.realization_authority_record",
                Code.TYPE_MISMATCH,
                "surface realization authority record required",
            )
        )
    if issues:
        return _report(issues)
    try:
        assert_valid_plan_input(value.plan_input)
        assert_valid_plan_result(value.plan_result, plan_input=value.plan_input)
    except Exception as error:
        issues.append(_issue("realization_input.plan_state", Code.SLICE42E_STATE_MISMATCH, str(error)))
        return _report(issues)
    issues.extend(_same(value.realization_input_id, expected_record_id(value), "realization_input.realization_input_id", Code.IDENTITY_MISMATCH))
    for name in ("realization_reason_refs", "trace_refs", "provenance_refs", "version_refs"):
        issues.extend(_ids(getattr(value, name), "realization_input." + name))
    issues.extend(validate_resource_bundle(value.controlled_resource_bundle).issues)
    authority = value.realization_authority_record
    plan = value.plan_result.expression_plan
    if not isinstance(authority, SurfaceRealizationAuthorityRecord):
        issues.append(_issue("realization_input.realization_authority_record", Code.TYPE_MISMATCH, "wrong authority type"))
    else:
        issues.extend(_schema(authority, "authority"))
        issues.extend(_same(authority.realization_authority_record_id, expected_record_id(authority), "authority.realization_authority_record_id", Code.IDENTITY_MISMATCH))
        issues.extend(_same(authority.authority_key, SLICE42F_REALIZATION_AUTHORITY_KEY, "authority.authority_key", Code.REALIZATION_AUTHORITY_MISMATCH))
        issues.extend(_same(authority.authority_version, SLICE42F_PROFILE_VERSION, "authority.authority_version", Code.INVALID_VERSION))
        issues.extend(_same(authority.profile_key, SLICE42F_PROFILE_KEY, "authority.profile_key", Code.INVALID_VERSION))
        issues.extend(_same(authority.profile_version, SLICE42F_PROFILE_VERSION, "authority.profile_version", Code.INVALID_VERSION))
        issues.extend(_same(authority.plan_input_ref, value.plan_input.plan_input_id, "authority.plan_input_ref", Code.REALIZATION_AUTHORITY_MISMATCH))
        issues.extend(_same(authority.plan_result_ref, value.plan_result.result_id, "authority.plan_result_ref", Code.REALIZATION_AUTHORITY_MISMATCH))
        issues.extend(_same(authority.expression_plan_ref, plan.expression_plan_id if plan else value.plan_result.result_id, "authority.expression_plan_ref", Code.REALIZATION_AUTHORITY_MISMATCH))
        issues.extend(_same(authority.selected_meaning_source_custody_ref, plan.selected_meaning_source_custody_ref if plan else value.plan_result.result_id, "authority.selected_meaning_source_custody_ref", Code.PRESERVATION_MISMATCH))
        issues.extend(_same(authority.source_plan_disposition, value.plan_result.disposition, "authority.source_plan_disposition", Code.DISPOSITION_MISMATCH))
        issues.extend(_same(authority.permitted_realization_disposition, determine_realization_disposition(value.plan_result.disposition), "authority.permitted_realization_disposition", Code.DISPOSITION_MISMATCH))
        issues.extend(_same(authority.admitted_rule_refs, SLICE42F_ADMITTED_RULE_REFS, "authority.admitted_rule_refs", Code.REALIZATION_AUTHORITY_MISMATCH))
        issues.extend(_same(authority.controlled_resource_bundle_ref, value.controlled_resource_bundle.resource_bundle_id, "authority.controlled_resource_bundle_ref", Code.RESOURCE_BUNDLE_MISMATCH))
        if plan is not None:
            issues.extend(_same(authority.predecessor_receipt_refs, plan.predecessor_receipt_refs, "authority.predecessor_receipt_refs", Code.PRESERVATION_MISMATCH))
            expected_versions = _ordered_unique(
                plan.version_refs,
                (value.plan_result.schema_version, SLICE42F_SCHEMA_VERSION),
            )
            issues.extend(_same(authority.version_refs, expected_versions, "authority.version_refs", Code.PRESERVATION_MISMATCH))
        issues.extend(_id(authority.disposition_authority_ref, "authority.disposition_authority_ref"))
        issues.extend(_id(authority.realization_authority_receipt_ref, "authority.realization_authority_receipt_ref"))
        authority_flags = (
            "authority_active",
            "surface_realization_authorized",
            "authorized_claim_realization_authorized",
            "containment_realization_authorized",
            "expression_candidate_creation_authorized",
            "governed_outward_meaning_construction_authorized",
            "msm_v1_mutation_or_integration_authorized",
            "echo_validation_authorized",
            "delivery_authorized",
            "truth_evidence_permission_execution_authorized",
            "route_api_network_filesystem_memory_tool_action_authorized",
            "external_resource_or_model_authority",
            "gp014_supersession_authorized",
        )
        for flag_name in authority_flags:
            issues.extend(_exact_bool(getattr(authority, flag_name), "authority." + flag_name))
        if not authority.authority_active or not authority.surface_realization_authorized or not authority.expression_candidate_creation_authorized:
            issues.append(_issue("authority", Code.REALIZATION_AUTHORITY_MISSING, "active explicit realization and candidate authority required"))
        if plan is not None:
            if plan.disposition is ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN and not authority.authorized_claim_realization_authorized:
                issues.append(_issue("authority.authorized_claim_realization_authorized", Code.REALIZATION_AUTHORITY_MISSING, "authorized claim realization permission required"))
            if plan.disposition is not ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN and not authority.containment_realization_authorized:
                issues.append(_issue("authority.containment_realization_authorized", Code.REALIZATION_AUTHORITY_MISSING, "containment realization permission required"))
        downstream = (
            authority.governed_outward_meaning_construction_authorized
            or authority.msm_v1_mutation_or_integration_authorized
            or authority.echo_validation_authorized
            or authority.delivery_authorized
            or authority.truth_evidence_permission_execution_authorized
            or authority.route_api_network_filesystem_memory_tool_action_authorized
            or authority.external_resource_or_model_authority
            or authority.gp014_supersession_authorized
        )
        if downstream:
            issues.append(_issue("authority", Code.DOWNSTREAM_AUTHORITY, "downstream authority must remain false"))
    request_names = (
        "free_form_generation_requested", "unadmitted_rule_requested",
        "unadmitted_resource_requested", "claim_invention_requested",
        "claim_strengthening_requested", "scope_expansion_requested",
        "certainty_upgrade_requested", "evidence_status_upgrade_requested",
        "limitation_omission_requested", "qualification_omission_requested",
        "caveat_omission_requested", "refusal_softening_requested",
        "unresolved_resolution_requested", "ambiguity_erasure_requested",
        "unsupported_state_erasure_requested", "selected_meaning_rewrite_requested",
        "downstream_authority_requested",
    )
    for name in request_names:
        issues.extend(
            _exact_bool(getattr(value, name), "realization_input." + name)
        )
    if any(getattr(value, name) for name in request_names):
        issues.append(_issue("realization_input", Code.PROHIBITED_REQUEST, "all prohibited requests must be false"))
    if plan is not None:
        template = tuple(r for r in value.controlled_resource_bundle.records if r.resource_key == f"template:{plan.disposition.value}")
        if len(template) != 1:
            issues.append(_issue("resource_bundle.records", Code.MISSING_TEMPLATE, "exact plan template required"))
        elif plan.disposition not in template[0].permitted_plan_dispositions:
            issues.append(_issue("resource_bundle.records", Code.RESOURCE_BUNDLE_MISMATCH, "template disposition mismatch"))
        if plan.disposition is ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN:
            claims = tuple(r for r in value.controlled_resource_bundle.records if r.resource_kind is ControlledRealizationResourceKind.AUTHORIZED_CLAIM_TEXT and r.bound_selected_meaning_ref == plan.selected_meaning_source_custody_ref)
            if len(claims) != 1:
                issues.append(_issue("resource_bundle.records", Code.MISSING_CLAIM_RESOURCE, "exact authorized claim resource required"))
    return _report(issues)


def validate_surface_realization_result(value: Any, *, realization_input: SurfaceRealizationInput) -> Report:
    input_report = validate_surface_realization_input(realization_input)
    issues: list[Issue] = list(input_report.issues)
    if not isinstance(realization_input, SurfaceRealizationInput):
        return _report(issues)
    if not input_report.ok:
        return _report(issues)
    if not isinstance(value, SurfaceRealizationResult):
        return _report(issues + [_issue("result", Code.TYPE_MISMATCH, "wrong record type")])
    issues.extend(_schema(value, "result"))
    issues.extend(_same(value.digest_algorithm, DIGEST_ALGORITHM, "result.digest_algorithm", Code.INVALID_VERSION))
    issues.extend(_same(value.result_id, expected_result_id(value), "result.result_id", Code.IDENTITY_MISMATCH))
    issues.extend(_same(value.result_digest, expected_result_digest(value), "result.result_digest", Code.DIGEST_MISMATCH))
    issues.extend(_same(value.realization_input_ref, realization_input.realization_input_id, "result.realization_input_ref", Code.PRESERVATION_MISMATCH))
    issues.extend(_same(value.required_law_refs, SLICE42F_GOVERNING_AUTHORITY_REFS, "result.required_law_refs", Code.PRESERVATION_MISMATCH))
    issues.extend(_same(value.permanent_boundaries, SLICE42F_PERMANENT_BOUNDARIES, "result.permanent_boundaries", Code.PRESERVATION_MISMATCH))
    issues.extend(_same(value.prohibited_authority, SLICE42F_PROHIBITED_AUTHORITY, "result.prohibited_authority", Code.PRESERVATION_MISMATCH))
    issues.extend(_same(value.source_plan_disposition, realization_input.plan_result.disposition, "result.source_plan_disposition", Code.DISPOSITION_MISMATCH))
    issues.extend(_same(value.disposition, determine_realization_disposition(realization_input.plan_result.disposition), "result.disposition", Code.DISPOSITION_MISMATCH))
    plan = realization_input.plan_result.expression_plan
    candidate = value.expression_candidate
    constructible = plan is not None and value.disposition.value.endswith("expression_candidate")
    if constructible:
        if not isinstance(candidate, UnvalidatedExpressionCandidate):
            return _report(issues + [_issue("result.expression_candidate", Code.TYPE_MISMATCH, "candidate required")])
        expected_segments = build_realization_segments(realization_input)
        expected_text = " ".join(expected_segments)
        expected_text_hash = hashlib.sha256(expected_text.encode("utf-8")).hexdigest()
        issues.extend(_schema(candidate, "candidate"))
        issues.extend(_same(candidate.digest_algorithm, DIGEST_ALGORITHM, "candidate.digest_algorithm", Code.INVALID_VERSION))
        issues.extend(_same(candidate.expression_candidate_id, expected_candidate_id(candidate), "candidate.expression_candidate_id", Code.IDENTITY_MISMATCH))
        issues.extend(_same(candidate.expression_candidate_digest, expected_candidate_digest(candidate), "candidate.expression_candidate_digest", Code.DIGEST_MISMATCH))
        issues.extend(_same(candidate.realization_input_ref, realization_input.realization_input_id, "candidate.realization_input_ref", Code.PRESERVATION_MISMATCH))
        issues.extend(_same(candidate.plan_result_ref, realization_input.plan_result.result_id, "candidate.plan_result_ref", Code.PRESERVATION_MISMATCH))
        issues.extend(_same(candidate.expression_plan_ref, plan.expression_plan_id, "candidate.expression_plan_ref", Code.PRESERVATION_MISMATCH))
        issues.extend(_same(candidate.realization_authority_record_ref, realization_input.realization_authority_record.realization_authority_record_id, "candidate.realization_authority_record_ref", Code.PRESERVATION_MISMATCH))
        issues.extend(_same(candidate.controlled_resource_bundle_ref, realization_input.controlled_resource_bundle.resource_bundle_id, "candidate.controlled_resource_bundle_ref", Code.PRESERVATION_MISMATCH))
        issues.extend(_same(candidate.selected_meaning_source_custody_ref, plan.selected_meaning_source_custody_ref, "candidate.selected_meaning_source_custody_ref", Code.PRESERVATION_MISMATCH))
        issues.extend(_same(candidate.source_plan_disposition, plan.disposition, "candidate.source_plan_disposition", Code.DISPOSITION_MISMATCH))
        issues.extend(_same(candidate.disposition, value.disposition, "candidate.disposition", Code.DISPOSITION_MISMATCH))
        issues.extend(_same(candidate.realized_text, expected_text, "candidate.realized_text", Code.TEXT_MISMATCH))
        issues.extend(_same(candidate.segments, expected_segments, "candidate.segments", Code.TEXT_MISMATCH))
        issues.extend(_same(candidate.realized_text_sha256, expected_text_hash, "candidate.realized_text_sha256", Code.TEXT_HASH_MISMATCH))
        exact_fields = (
            "selected_meaning_refs", "active_scope_refs", "certainty_level_refs",
            "evidence_status_refs", "meaning_modifier_refs", "inherited_limitation_refs",
            "required_qualification_refs", "required_caveat_refs",
            "refusal_relevant_boundary_refs", "unresolved_condition_refs",
            "ambiguity_refs", "unsupported_state_refs", "memory_authority_refs",
            "external_resource_status_refs", "delivery_authority_refs",
            "privacy_identity_boundary_refs", "preservation_class_refs",
            "ancestry_refs", "predecessor_receipt_refs",
        )
        for name in exact_fields:
            issues.extend(_same(getattr(candidate, name), getattr(plan, name), "candidate." + name, Code.PRESERVATION_MISMATCH))
        issues.extend(_same(candidate.applied_rule_refs, SLICE42F_ADMITTED_RULE_REFS, "candidate.applied_rule_refs", Code.PRESERVATION_MISMATCH))
        issues.extend(_same(candidate.applied_resource_refs, tuple(r.resource_record_id for r in applied_resource_records(realization_input)), "candidate.applied_resource_refs", Code.RESOURCE_BUNDLE_MISMATCH))
        issues.extend(_same(candidate.trace_refs, _ordered_unique(plan.trace_refs, realization_input.trace_refs), "candidate.trace_refs", Code.PRESERVATION_MISMATCH))
        issues.extend(_same(candidate.provenance_refs, _ordered_unique(plan.provenance_refs, realization_input.provenance_refs), "candidate.provenance_refs", Code.PRESERVATION_MISMATCH))
        issues.extend(_same(candidate.version_refs, _ordered_unique(plan.version_refs, realization_input.version_refs), "candidate.version_refs", Code.PRESERVATION_MISMATCH))
        required_true = (
            candidate.exact_slice42e_plan_verified, candidate.exact_realization_authority_verified,
            candidate.admitted_rules_only, candidate.controlled_resources_only,
            candidate.authorized_claim_not_strengthened, candidate.certainty_not_upgraded,
            candidate.evidence_status_not_upgraded, candidate.deterministic_surface_realization_performed,
            candidate.human_readable_text_produced, candidate.expression_candidate_created,
            candidate.unvalidated_expression_candidate,
        )
        if not all(required_true):
            issues.append(_issue("candidate", Code.PRESERVATION_MISMATCH, "required realization proof flags must be true"))
        issues.extend(_same(candidate.caveats_visible, bool(plan.required_caveat_refs), "candidate.caveats_visible", Code.PRESERVATION_MISMATCH))
        issues.extend(_same(candidate.unresolved_states_visible, bool(plan.unresolved_condition_refs or plan.ambiguity_refs or plan.unsupported_state_refs), "candidate.unresolved_states_visible", Code.PRESERVATION_MISMATCH))
        issues.extend(_same(candidate.refusal_language_produced, plan.disposition in (ExpressionPlanDisposition.BLOCKED_CONSEQUENCE_PLAN, ExpressionPlanDisposition.REFUSAL_PRESERVING_PLAN), "candidate.refusal_language_produced", Code.PRESERVATION_MISMATCH))
        forbidden_true = (
            candidate.echo_validation_performed, candidate.echo_approved,
            candidate.delivery_authorized, candidate.delivered,
            candidate.governed_outward_meaning_created, candidate.msm_v1_modified_or_integrated,
            candidate.truth_determined, candidate.evidence_validated, candidate.permission_granted,
            candidate.execution_authorized, candidate.route_or_api_created, candidate.tool_invoked,
            candidate.action_performed, candidate.memory_accessed_or_written,
            candidate.filesystem_or_network_accessed, candidate.external_resource_loaded,
            candidate.model_or_similarity_authority_used, candidate.gp014_superseded,
        )
        if any(forbidden_true):
            issues.append(_issue("candidate", Code.DOWNSTREAM_AUTHORITY, "candidate downstream flags must remain false"))
        trace = value.realization_trace
        receipt = value.realization_receipt
        if trace is None:
            issues.append(_issue("result.realization_trace", Code.TRACE_MISMATCH, "trace required"))
        elif not isinstance(trace, SurfaceRealizationTrace):
            return _report(issues + [_issue("result.realization_trace", Code.TYPE_MISMATCH, "trace record required")])
        else:
            issues.extend(_schema(trace, "trace"))
            issues.extend(_same(trace.realization_trace_id, expected_record_id(trace), "trace.realization_trace_id", Code.IDENTITY_MISMATCH))
            issues.extend(_same(trace.realization_input_ref, realization_input.realization_input_id, "trace.realization_input_ref", Code.TRACE_MISMATCH))
            issues.extend(_same(trace.expression_plan_ref, plan.expression_plan_id, "trace.expression_plan_ref", Code.TRACE_MISMATCH))
            issues.extend(_same(trace.expression_candidate_ref, candidate.expression_candidate_id, "trace.expression_candidate_ref", Code.TRACE_MISMATCH))
            issues.extend(_same(trace.realized_text_sha256, candidate.realized_text_sha256, "trace.realized_text_sha256", Code.TRACE_MISMATCH))
            issues.extend(_same(trace.segment_sha256s, tuple(hashlib.sha256(item.encode("utf-8")).hexdigest() for item in candidate.segments), "trace.segment_sha256s", Code.TRACE_MISMATCH))
            for name in ("applied_rule_refs", "applied_resource_refs", "ancestry_refs", "predecessor_receipt_refs", "provenance_refs", "version_refs"):
                issues.extend(_same(getattr(trace, name), getattr(candidate, name), "trace." + name, Code.TRACE_MISMATCH))
            issues.extend(_same(trace.predecessor_trace_refs, candidate.trace_refs, "trace.predecessor_trace_refs", Code.TRACE_MISMATCH))
            for flag_name in ("deterministic", "semantic_strengthening_detected", "certainty_upgrade_detected", "evidence_upgrade_detected", "omission_detected"):
                issues.extend(_exact_bool(getattr(trace, flag_name), "trace." + flag_name))
            if not trace.deterministic or trace.semantic_strengthening_detected or trace.certainty_upgrade_detected or trace.evidence_upgrade_detected or trace.omission_detected:
                issues.append(_issue("trace", Code.TRACE_MISMATCH, "trace proof flags invalid"))
        if receipt is None:
            issues.append(_issue("result.realization_receipt", Code.RECEIPT_MISMATCH, "receipt required"))
        elif not isinstance(receipt, SurfaceRealizationReceipt):
            return _report(issues + [_issue("result.realization_receipt", Code.TYPE_MISMATCH, "receipt record required")])
        else:
            issues.extend(_schema(receipt, "receipt"))
            issues.extend(_same(receipt.realization_receipt_id, expected_record_id(receipt), "receipt.realization_receipt_id", Code.IDENTITY_MISMATCH))
            issues.extend(_same(receipt.realization_input_ref, realization_input.realization_input_id, "receipt.realization_input_ref", Code.RECEIPT_MISMATCH))
            issues.extend(_same(receipt.expression_plan_ref, plan.expression_plan_id, "receipt.expression_plan_ref", Code.RECEIPT_MISMATCH))
            issues.extend(_same(receipt.expression_candidate_ref, candidate.expression_candidate_id, "receipt.expression_candidate_ref", Code.RECEIPT_MISMATCH))
            issues.extend(_same(receipt.realization_trace_ref, trace.realization_trace_id if trace else "", "receipt.realization_trace_ref", Code.RECEIPT_MISMATCH))
            issues.extend(_same(receipt.realization_authority_record_ref, realization_input.realization_authority_record.realization_authority_record_id, "receipt.realization_authority_record_ref", Code.RECEIPT_MISMATCH))
            issues.extend(_same(receipt.controlled_resource_bundle_ref, realization_input.controlled_resource_bundle.resource_bundle_id, "receipt.controlled_resource_bundle_ref", Code.RECEIPT_MISMATCH))
            issues.extend(_same(receipt.realized_text_sha256, candidate.realized_text_sha256, "receipt.realized_text_sha256", Code.RECEIPT_MISMATCH))
            issues.extend(_same(receipt.required_law_refs, SLICE42F_GOVERNING_AUTHORITY_REFS, "receipt.required_law_refs", Code.RECEIPT_MISMATCH))
            issues.extend(_same(receipt.prohibited_consequence_refs, SLICE42F_PROHIBITED_AUTHORITY, "receipt.prohibited_consequence_refs", Code.RECEIPT_MISMATCH))
            for flag_name in ("deterministic", "surface_realization_performed", "expression_candidate_created", "unvalidated_expression_candidate", "echo_validated", "echo_approved", "delivery_authorized", "delivered"):
                issues.extend(_exact_bool(getattr(receipt, flag_name), "receipt." + flag_name))
            if not receipt.deterministic or not receipt.surface_realization_performed or not receipt.expression_candidate_created or not receipt.unvalidated_expression_candidate:
                issues.append(_issue("receipt", Code.RECEIPT_MISMATCH, "receipt proof flags invalid"))
            if receipt.echo_validated or receipt.echo_approved or receipt.delivery_authorized or receipt.delivered:
                issues.append(_issue("receipt", Code.DOWNSTREAM_AUTHORITY, "receipt cannot grant Echo or delivery"))
    else:
        if candidate is not None or value.realization_trace is not None or value.realization_receipt is not None:
            issues.append(_issue("result", Code.PRESERVATION_MISMATCH, "held or indeterminate result must not create candidate trace or receipt"))
    expected_bool = constructible
    result_flag_names = (
        "surface_realization_performed", "human_readable_text_produced",
        "expression_candidate_created", "refusal_language_produced",
        "authorized_claim_not_strengthened", "certainty_not_upgraded",
        "evidence_status_not_upgraded", "caveats_and_unresolved_states_visible",
        "deterministic_trace_created", "deterministic_receipt_created",
        "unvalidated_expression_candidate", "held_pending_authority",
        "indeterminate", "governed_outward_meaning_created",
        "msm_v1_modified_or_integrated", "echo_validation_performed",
        "echo_approved", "delivery_authorized", "delivered",
        "truth_determined", "evidence_validated", "permission_granted",
        "execution_authorized", "route_or_api_created", "tool_invoked",
        "action_performed", "memory_accessed_or_written",
        "filesystem_or_network_accessed", "external_resource_loaded",
        "model_or_similarity_authority_used", "gp014_superseded",
    )
    for name in result_flag_names:
        issues.extend(_exact_bool(getattr(value, name), "result." + name))
    for name in (
        "surface_realization_performed", "human_readable_text_produced",
        "expression_candidate_created", "authorized_claim_not_strengthened",
        "certainty_not_upgraded", "evidence_status_not_upgraded",
        "caveats_and_unresolved_states_visible", "deterministic_trace_created",
        "deterministic_receipt_created", "unvalidated_expression_candidate",
    ):
        issues.extend(_same(getattr(value, name), expected_bool, "result." + name, Code.PRESERVATION_MISMATCH))
    issues.extend(_same(value.refusal_language_produced, bool(candidate and candidate.refusal_language_produced), "result.refusal_language_produced", Code.PRESERVATION_MISMATCH))
    issues.extend(_same(value.held_pending_authority, value.disposition.value == "held_pending_authority", "result.held_pending_authority", Code.PRESERVATION_MISMATCH))
    issues.extend(_same(value.indeterminate, value.disposition.value == "indeterminate", "result.indeterminate", Code.PRESERVATION_MISMATCH))
    if any((
        value.governed_outward_meaning_created, value.msm_v1_modified_or_integrated,
        value.echo_validation_performed, value.echo_approved, value.delivery_authorized,
        value.delivered, value.truth_determined, value.evidence_validated,
        value.permission_granted, value.execution_authorized, value.route_or_api_created,
        value.tool_invoked, value.action_performed, value.memory_accessed_or_written,
        value.filesystem_or_network_accessed, value.external_resource_loaded,
        value.model_or_similarity_authority_used, value.gp014_superseded,
    )):
        issues.append(_issue("result", Code.DOWNSTREAM_AUTHORITY, "result downstream flags must remain false"))
    expected_finding_kinds = tuple(SurfaceRealizationFindingKind)
    if type(value.findings) is not tuple or len(value.findings) != 8:
        issues.append(_issue("result.findings", Code.FINDING_MISMATCH, "exact eight findings required"))
    else:
        issues.extend(_same(tuple(finding.finding_kind for finding in value.findings if isinstance(finding, SurfaceRealizationFinding)), expected_finding_kinds, "result.findings.kinds", Code.FINDING_MISMATCH))
        for index, finding in enumerate(value.findings):
            path = f"result.findings[{index}]"
            if not isinstance(finding, SurfaceRealizationFinding):
                issues.append(_issue(path, Code.TYPE_MISMATCH, "finding record required"))
                continue
            issues.extend(_schema(finding, path))
            issues.extend(_same(finding.finding_id, expected_record_id(finding), path + ".finding_id", Code.IDENTITY_MISMATCH))
            issues.extend(_same(finding.realization_input_ref, realization_input.realization_input_id, path + ".realization_input_ref", Code.FINDING_MISMATCH))
            issues.extend(_same(finding.expression_candidate_ref, candidate.expression_candidate_id if candidate else None, path + ".expression_candidate_ref", Code.FINDING_MISMATCH))
            issues.extend(_ids(finding.basis_refs, path + ".basis_refs"))
            issues.extend(_ids(finding.reason_refs, path + ".reason_refs"))
            issues.extend(_same(finding.trace_refs, realization_input.trace_refs, path + ".trace_refs", Code.FINDING_MISMATCH))
            issues.extend(_same(finding.provenance_refs, realization_input.provenance_refs, path + ".provenance_refs", Code.FINDING_MISMATCH))
    return _report(issues)


def assert_valid_surface_realization_input(value: Any) -> None:
    report = validate_surface_realization_input(value)
    if not report.ok:
        raise SurfaceRealizationValidationError(report)


def assert_valid_surface_realization_result(value: Any, *, realization_input: SurfaceRealizationInput) -> None:
    report = validate_surface_realization_result(value, realization_input=realization_input)
    if not report.ok:
        raise SurfaceRealizationValidationError(report)


__all__ = (
    "assert_valid_surface_realization_input",
    "assert_valid_surface_realization_result",
    "validate_resource_bundle",
    "validate_surface_realization_input",
    "validate_surface_realization_result",
)
