"""Fail-closed validation for Slice 42G integration records."""

from __future__ import annotations

from dataclasses import fields
import re
from typing import Any

from ...meaning_structure_manifest import (
    ExpressionLinkRecord,
    ExternalAuthorityKind,
    ExternalAuthorityReferenceRecord,
    GovernedOutwardMeaningRecord,
    MeaningStructureManifestV1,
    SemanticTransitionKind,
    SemanticTransitionTraceRecord,
)
from ...meaning_structure_manifest.serialization import canonical_manifest_sha256
from ...meaning_structure_manifest.validation import validate_manifest
from ...selected_meaning_runtime.msm_selected_meaning_integration import (
    MsmSelectedMeaningIntegrationInput,
    MsmSelectedMeaningIntegrationResult,
)
from ...selected_meaning_runtime.msm_selected_meaning_integration.validation import (
    validate_integration_input as validate_slice41e_input,
    validate_integration_result as validate_slice41e_result,
)
from ..surface_realization import (
    SurfaceRealizationInput,
    SurfaceRealizationResult,
    UnvalidatedExpressionCandidate,
)
from ..surface_realization.validation import (
    validate_surface_realization_input,
    validate_surface_realization_result,
)
from .authority import (
    DIGEST_ALGORITHM,
    SLICE42G_ADAPTER_DECISION,
    SLICE42G_ALLOWED_MSM_ADDITIONS,
    SLICE42G_COMPANION_VERSION,
    SLICE42G_GOVERNING_AUTHORITY_REFS,
    SLICE42G_PERMANENT_BOUNDARIES,
    SLICE42G_PROFILE_KEY,
    SLICE42G_PROFILE_VERSION,
    SLICE42G_PROHIBITED_AUTHORITY,
    SLICE42G_RECEIPT_VERSION,
    SLICE42G_REQUIRED_PATH,
    SLICE42G_REQUIRED_UNCHANGED_SECTIONS,
    SLICE42G_SCHEMA_VERSION,
    SLICE42G_SPEC_ID,
    SLICE42G_SPEC_VERSION,
)
from .identity import (
    expected_authority_reference_id,
    expected_companion_id,
    expected_expression_link_id,
    expected_input_id,
    expected_outward_meaning_id,
    expected_profile_id,
    expected_receipt_id,
    expected_result_digest,
    expected_result_id,
    expected_successor_manifest_id,
    expected_transition_trace_id,
)
from .schema import (
    MsmOutwardExpressionCustodyCompanionV1,
    MsmOutwardExpressionIntegrationAuthorityProfile,
    MsmOutwardExpressionIntegrationInput,
    MsmOutwardExpressionIntegrationReceiptV1,
    MsmOutwardExpressionIntegrationResult,
    MsmOutwardExpressionIntegrationValidationCode as Code,
    MsmOutwardExpressionIntegrationValidationError,
    MsmOutwardExpressionIntegrationValidationIssue as Issue,
    MsmOutwardExpressionIntegrationValidationReport as Report,
)

_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/#@+\-]{0,2047}$")


def _issue(
    issues: list[Issue],
    path: str,
    code: Code,
    detail: str,
) -> None:
    issues.append(Issue(path, code, detail))


def _report(issues: list[Issue]) -> Report:
    return Report(tuple(issues))


def _identifier(value: Any, path: str, issues: list[Issue]) -> None:
    if type(value) is not str or not _IDENTIFIER_RE.fullmatch(value):
        _issue(issues, path, Code.INVALID_IDENTIFIER, "bounded identifier required")


def _text(value: Any, path: str, issues: list[Issue]) -> None:
    if type(value) is not str or not value or value != value.strip():
        _issue(issues, path, Code.TYPE_MISMATCH, "non-empty trimmed text required")


def _identifiers(
    value: Any,
    path: str,
    issues: list[Issue],
    *,
    allow_empty: bool,
) -> None:
    if type(value) is not tuple:
        _issue(issues, path, Code.TYPE_MISMATCH, "tuple required")
        return
    if not allow_empty and not value:
        _issue(issues, path, Code.TYPE_MISMATCH, "non-empty tuple required")
    if len(value) != len(set(value)):
        _issue(issues, path, Code.DUPLICATE_ID, "duplicate values are not admitted")
    for index, item in enumerate(value):
        _identifier(item, f"{path}[{index}]", issues)


def _exact_bool(
    value: Any,
    expected: bool,
    path: str,
    issues: list[Issue],
) -> None:
    if type(value) is not bool or value is not expected:
        _issue(
            issues,
            path,
            Code.PROFILE_MISMATCH if path.startswith("profile") else Code.DOWNSTREAM_AUTHORITY,
            f"exact {expected} required",
        )


def _record_ids(records: Any) -> tuple[str, ...]:
    if type(records) is not tuple:
        return ()
    return tuple(
        item.record_id
        for item in records
        if hasattr(item, "record_id")
    )


def _nested_slice41e_pair(
    value: MsmOutwardExpressionIntegrationInput,
):
    closeout = (
        value.surface_realization_input
        .plan_input
        .projection_input
        .expression_eligibility_evaluation_input
        .selected_meaning_closeout_result
    )
    return closeout.integration_input, closeout.integration_result


def validate_authority_profile(value: Any) -> Report:
    issues: list[Issue] = []
    if type(value) is not MsmOutwardExpressionIntegrationAuthorityProfile:
        return Report((Issue("profile", Code.TYPE_MISMATCH, "exact profile type required"),))

    exact_values = {
        "profile_key": SLICE42G_PROFILE_KEY,
        "profile_version": SLICE42G_PROFILE_VERSION,
        "governing_authority_refs": SLICE42G_GOVERNING_AUTHORITY_REFS,
        "adapter_decision": SLICE42G_ADAPTER_DECISION,
        "required_path": SLICE42G_REQUIRED_PATH,
        "permanent_boundaries": SLICE42G_PERMANENT_BOUNDARIES,
        "prohibited_authority": SLICE42G_PROHIBITED_AUTHORITY,
        "allowed_msm_additions": SLICE42G_ALLOWED_MSM_ADDITIONS,
        "required_unchanged_sections": SLICE42G_REQUIRED_UNCHANGED_SECTIONS,
        "spec_id": SLICE42G_SPEC_ID,
        "spec_version": SLICE42G_SPEC_VERSION,
        "schema_version": SLICE42G_SCHEMA_VERSION,
    }
    for name, expected in exact_values.items():
        if getattr(value, name) != expected:
            _issue(issues, f"profile.{name}", Code.PROFILE_MISMATCH, "canonical profile value mismatch")

    true_names = (
        "exact_slice41e_input_required",
        "exact_slice41e_result_required",
        "exact_slice42f_input_required",
        "exact_slice42f_result_required",
        "exact_unvalidated_candidate_required",
        "existing_dormant_msm_records_required",
        "explicit_external_authority_reference_required",
        "immutable_successor_required",
        "selected_meaning_retention_required",
        "candidate_retention_required",
        "non_selection_retention_required",
        "alternative_unresolved_retention_required",
        "outward_meaning_record_allowed",
        "expression_link_record_allowed",
        "lifecycle_traces_required",
        "complete_successor_validation_required",
        "versioned_companion_required",
        "deterministic_receipt_required",
        "fail_closed",
    )
    false_names = (
        "msm_schema_rewrite_allowed",
        "automatic_migration_allowed",
        "source_manifest_mutation_allowed",
        "candidate_deletion_allowed",
        "non_selection_deletion_allowed",
        "selected_meaning_rewrite_allowed",
        "governed_result_creation_allowed",
        "validation_link_creation_allowed",
        "delivery_link_creation_allowed",
        "expression_candidate_rewrite_allowed",
        "echo_validation_allowed",
        "delivery_allowed",
        "truth_evidence_permission_execution_allowed",
        "route_tool_action_memory_filesystem_network_allowed",
        "external_resource_or_model_authority_allowed",
        "bootstrap_integration_allowed",
        "gp014_supersession_allowed",
    )
    for name in true_names:
        _exact_bool(getattr(value, name), True, f"profile.{name}", issues)
    for name in false_names:
        _exact_bool(getattr(value, name), False, f"profile.{name}", issues)

    _identifier(value.profile_id, "profile.profile_id", issues)
    try:
        expected = expected_profile_id(value)
    except Exception as error:
        _issue(issues, "profile.profile_id", Code.CANONICAL_MISMATCH, str(error))
    else:
        if value.profile_id != expected:
            _issue(issues, "profile.profile_id", Code.IDENTITY_MISMATCH, "profile ID mismatch")
    return _report(issues)


def validate_integration_input(value: Any) -> Report:
    issues: list[Issue] = []
    if type(value) is not MsmOutwardExpressionIntegrationInput:
        return Report((Issue("integration_input", Code.TYPE_MISMATCH, "exact input type required"),))

    issues.extend(validate_authority_profile(value.authority_profile).issues)
    _identifier(value.integration_input_id, "integration_input.integration_input_id", issues)
    _text(value.outward_transition_reason, "integration_input.outward_transition_reason", issues)
    _text(value.expression_transition_reason, "integration_input.expression_transition_reason", issues)
    _identifiers(value.version_refs, "integration_input.version_refs", issues, allow_empty=False)
    if value.schema_version != SLICE42G_SCHEMA_VERSION:
        _issue(issues, "integration_input.schema_version", Code.INVALID_VERSION, "unknown Slice 42G schema version")

    if type(value.source_selected_meaning_integration_input) is not MsmSelectedMeaningIntegrationInput:
        _issue(issues, "integration_input.source_selected_meaning_integration_input", Code.TYPE_MISMATCH, "exact Slice 41E input required")
    else:
        try:
            source_input_report = validate_slice41e_input(value.source_selected_meaning_integration_input)
        except Exception as error:
            _issue(issues, "integration_input.source_selected_meaning_integration_input", Code.SOURCE_CHAIN_INVALID, f"Slice 41E input validation raised: {error}")
        else:
            if not source_input_report.ok:
                _issue(issues, "integration_input.source_selected_meaning_integration_input", Code.SOURCE_CHAIN_INVALID, "Slice 41E input validation failed")

    if type(value.source_selected_meaning_integration_result) is not MsmSelectedMeaningIntegrationResult:
        _issue(issues, "integration_input.source_selected_meaning_integration_result", Code.TYPE_MISMATCH, "exact Slice 41E result required")
    elif type(value.source_selected_meaning_integration_input) is MsmSelectedMeaningIntegrationInput:
        try:
            source_result_report = validate_slice41e_result(
                value.source_selected_meaning_integration_result,
                integration_input=value.source_selected_meaning_integration_input,
            )
        except Exception as error:
            _issue(issues, "integration_input.source_selected_meaning_integration_result", Code.SOURCE_CHAIN_INVALID, f"Slice 41E result validation raised: {error}")
        else:
            if not source_result_report.ok:
                _issue(issues, "integration_input.source_selected_meaning_integration_result", Code.SOURCE_CHAIN_INVALID, "Slice 41E result validation failed")

    if type(value.surface_realization_input) is not SurfaceRealizationInput:
        _issue(issues, "integration_input.surface_realization_input", Code.TYPE_MISMATCH, "exact Slice 42F input required")
    else:
        try:
            surface_input_report = validate_surface_realization_input(value.surface_realization_input)
        except Exception as error:
            _issue(issues, "integration_input.surface_realization_input", Code.SURFACE_REALIZATION_INVALID, f"Slice 42F input validation raised: {error}")
        else:
            if not surface_input_report.ok:
                _issue(issues, "integration_input.surface_realization_input", Code.SURFACE_REALIZATION_INVALID, "Slice 42F input validation failed")

    if type(value.surface_realization_result) is not SurfaceRealizationResult:
        _issue(issues, "integration_input.surface_realization_result", Code.TYPE_MISMATCH, "exact Slice 42F result required")
    elif type(value.surface_realization_input) is SurfaceRealizationInput:
        try:
            surface_result_report = validate_surface_realization_result(
                value.surface_realization_result,
                realization_input=value.surface_realization_input,
            )
        except Exception as error:
            _issue(issues, "integration_input.surface_realization_result", Code.SURFACE_REALIZATION_INVALID, f"Slice 42F result validation raised: {error}")
        else:
            if not surface_result_report.ok:
                _issue(issues, "integration_input.surface_realization_result", Code.SURFACE_REALIZATION_INVALID, "Slice 42F result validation failed")

    if (
        type(value.surface_realization_input) is SurfaceRealizationInput
        and type(value.source_selected_meaning_integration_input) is MsmSelectedMeaningIntegrationInput
        and type(value.source_selected_meaning_integration_result) is MsmSelectedMeaningIntegrationResult
    ):
        try:
            nested_input, nested_result = _nested_slice41e_pair(value)
        except Exception as error:
            _issue(issues, "integration_input.source_chain", Code.SOURCE_CHAIN_INVALID, f"could not resolve nested Slice 41E chain: {error}")
        else:
            if nested_input != value.source_selected_meaning_integration_input:
                _issue(issues, "integration_input.source_selected_meaning_integration_input", Code.SOURCE_CHAIN_INVALID, "Slice 42F ancestry does not carry the exact supplied Slice 41E input")
            if nested_result != value.source_selected_meaning_integration_result:
                _issue(issues, "integration_input.source_selected_meaning_integration_result", Code.SOURCE_CHAIN_INVALID, "Slice 42F ancestry does not carry the exact supplied Slice 41E result")

    source = value.source_manifest
    if type(source) is not MeaningStructureManifestV1:
        _issue(issues, "integration_input.source_manifest", Code.TYPE_MISMATCH, "exact MSM-v1 source manifest required")
    else:
        try:
            manifest_report = validate_manifest(source)
        except Exception as error:
            _issue(issues, "integration_input.source_manifest", Code.SOURCE_MANIFEST_INVALID, f"MSM-v1 validation raised: {error}")
        else:
            if not manifest_report.ok:
                _issue(issues, "integration_input.source_manifest", Code.SOURCE_MANIFEST_INVALID, "source manifest validation failed")
        selected = value.source_selected_meaning_integration_result.integrated_selected_meaning_record
        if selected not in source.selected_governed_meanings:
            _issue(issues, "integration_input.source_manifest.selected_governed_meanings", Code.SOURCE_CHAIN_INVALID, "exact integrated selected meaning is absent")
        if source.governed_outward_meanings:
            _issue(issues, "integration_input.source_manifest.governed_outward_meanings", Code.DORMANT_RECORD_MISMATCH, "Slice 41E source must not already contain outward meanings")
        if source.expression_links:
            _issue(issues, "integration_input.source_manifest.expression_links", Code.DORMANT_RECORD_MISMATCH, "Slice 41E source must not already contain expression links")
        if source.validation_links or source.delivery_or_containment_links:
            _issue(issues, "integration_input.source_manifest", Code.DOWNSTREAM_AUTHORITY, "validation and delivery sections must remain empty before Slice 42G")

    candidate = value.surface_realization_result.expression_candidate
    if type(candidate) is not UnvalidatedExpressionCandidate:
        _issue(issues, "integration_input.surface_realization_result.expression_candidate", Code.TYPE_MISMATCH, "exact unvalidated expression candidate required")
    else:
        selected_ref = value.source_selected_meaning_integration_result.integrated_selected_meaning_record.record_id
        if selected_ref not in candidate.selected_meaning_refs:
            _issue(issues, "integration_input.surface_realization_result.expression_candidate.selected_meaning_refs", Code.SOURCE_CHAIN_INVALID, "candidate does not preserve the integrated selected meaning reference")
        exact_true = (
            "unvalidated_expression_candidate",
            "exact_slice42e_plan_verified",
            "exact_realization_authority_verified",
            "admitted_rules_only",
            "controlled_resources_only",
            "authorized_claim_not_strengthened",
            "certainty_not_upgraded",
            "evidence_status_not_upgraded",
            "caveats_visible",
            "unresolved_states_visible",
            "deterministic_surface_realization_performed",
            "human_readable_text_produced",
            "expression_candidate_created",
        )
        for name in exact_true:
            _exact_bool(getattr(candidate, name), True, f"integration_input.expression_candidate.{name}", issues)
        exact_false = (
            "echo_validation_performed",
            "echo_approved",
            "delivery_authorized",
            "delivered",
            "governed_outward_meaning_created",
            "msm_v1_modified_or_integrated",
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
        for name in exact_false:
            _exact_bool(getattr(candidate, name), False, f"integration_input.expression_candidate.{name}", issues)

    request_names = tuple(
        name for name in value.__dataclass_fields__ if name.endswith("_requested")
    )
    for name in request_names:
        _exact_bool(getattr(value, name), False, f"integration_input.{name}", issues)

    try:
        expected = expected_input_id(value)
    except Exception as error:
        _issue(issues, "integration_input.integration_input_id", Code.CANONICAL_MISMATCH, str(error))
    else:
        if value.integration_input_id != expected:
            _issue(issues, "integration_input.integration_input_id", Code.IDENTITY_MISMATCH, "input ID mismatch")
    return _report(issues)


def validate_integration_result(
    value: Any,
    *,
    integration_input: MsmOutwardExpressionIntegrationInput,
) -> Report:
    issues: list[Issue] = list(validate_integration_input(integration_input).issues)
    if type(integration_input) is not MsmOutwardExpressionIntegrationInput:
        return _report(issues)
    if issues:
        return _report(issues)
    if type(value) is not MsmOutwardExpressionIntegrationResult:
        return _report(issues + [Issue("result", Code.TYPE_MISMATCH, "exact result type required")])

    from .integration import construct_successor_artifacts, derive_outward_meaning_fields

    source = integration_input.source_manifest
    candidate = integration_input.expression_candidate
    selected = integration_input.source_selected_meaning_integration_result.integrated_selected_meaning_record
    try:
        expected_artifacts = construct_successor_artifacts(integration_input)
    except Exception as error:
        _issue(issues, "result", Code.CANONICAL_MISMATCH, f"expected successor construction raised: {error}")
        return _report(issues)
    expected_authority, expected_outward, expected_expression, expected_selected_trace, expected_expression_trace, expected_successor = expected_artifacts

    if value.schema_version != SLICE42G_SCHEMA_VERSION:
        _issue(issues, "result.schema_version", Code.INVALID_VERSION, "unknown Slice 42G schema version")
    if value.digest_algorithm != DIGEST_ALGORITHM:
        _issue(issues, "result.digest_algorithm", Code.INVALID_VERSION, "digest algorithm mismatch")
    if value.integration_input_ref != integration_input.integration_input_id:
        _issue(issues, "result.integration_input_ref", Code.CANONICAL_MISMATCH, "input reference mismatch")
    if value.source_manifest != source:
        _issue(issues, "result.source_manifest", Code.CANONICAL_MISMATCH, "source manifest was not preserved exactly")
    if value.external_authority_reference_record != expected_authority:
        _issue(issues, "result.external_authority_reference_record", Code.AUTHORITY_REFERENCE_MISMATCH, "authority record mismatch")
    if value.governed_outward_meaning_record != expected_outward:
        _issue(issues, "result.governed_outward_meaning_record", Code.OUTWARD_MEANING_MISMATCH, "outward meaning record mismatch")
    if value.expression_link_record != expected_expression:
        _issue(issues, "result.expression_link_record", Code.EXPRESSION_LINK_MISMATCH, "expression link record mismatch")
    if value.selected_to_outward_trace != expected_selected_trace:
        _issue(issues, "result.selected_to_outward_trace", Code.TRANSITION_MISMATCH, "selected-to-outward trace mismatch")
    if value.outward_to_expression_trace != expected_expression_trace:
        _issue(issues, "result.outward_to_expression_trace", Code.TRANSITION_MISMATCH, "outward-to-expression trace mismatch")
    if value.successor_manifest != expected_successor:
        _issue(issues, "result.successor_manifest", Code.CANONICAL_MISMATCH, "successor manifest mismatch")

    try:
        manifest_report = validate_manifest(value.successor_manifest)
    except Exception as error:
        _issue(issues, "result.successor_manifest", Code.SUCCESSOR_MANIFEST_INVALID, f"manifest validation raised: {error}")
    else:
        if not manifest_report.ok:
            _issue(issues, "result.successor_manifest", Code.SUCCESSOR_MANIFEST_INVALID, "complete successor manifest validation failed")

    successor = value.successor_manifest
    exact_unchanged = (
        ("lineage_root", source.lineage_root, successor.lineage_root),
        ("candidate_meanings", source.candidate_meanings, successor.candidate_meanings),
        ("non_selection_outcomes", source.non_selection_outcomes, successor.non_selection_outcomes),
        ("selected_governed_meanings", source.selected_governed_meanings, successor.selected_governed_meanings),
        ("governed_result_references", source.governed_result_references, successor.governed_result_references),
        ("validation_links", source.validation_links, successor.validation_links),
        ("delivery_or_containment_links", source.delivery_or_containment_links, successor.delivery_or_containment_links),
        ("package_id", source.package_id, successor.package_id),
        ("schema_id", source.schema_id, successor.schema_id),
        ("schema_version", source.schema_version, successor.schema_version),
    )
    for name, before, after in exact_unchanged:
        if before != after:
            _issue(issues, f"result.successor_manifest.{name}", Code.RETENTION_MISMATCH, "source section changed")
    if successor.governed_outward_meanings != (*source.governed_outward_meanings, expected_outward):
        _issue(issues, "result.successor_manifest.governed_outward_meanings", Code.OUTWARD_MEANING_MISMATCH, "exact single outward addition required")
    if successor.expression_links != (*source.expression_links, expected_expression):
        _issue(issues, "result.successor_manifest.expression_links", Code.EXPRESSION_LINK_MISMATCH, "exact single expression-link addition required")
    if successor.external_authority_references != (*source.external_authority_references, expected_authority):
        _issue(issues, "result.successor_manifest.external_authority_references", Code.AUTHORITY_REFERENCE_MISMATCH, "exact single authority addition required")
    if successor.semantic_transition_traces != (*source.semantic_transition_traces, expected_selected_trace, expected_expression_trace):
        _issue(issues, "result.successor_manifest.semantic_transition_traces", Code.TRANSITION_MISMATCH, "exact two transition traces required")

    outward_fields = derive_outward_meaning_fields(integration_input)
    outward = value.governed_outward_meaning_record
    if outward.record_id != expected_outward_meaning_id(outward):
        _issue(issues, "result.governed_outward_meaning_record.record_id", Code.IDENTITY_MISMATCH, "outward record ID mismatch")
    if outward.prior_selected_meaning_ref != selected.record_id:
        _issue(issues, "result.governed_outward_meaning_record.prior_selected_meaning_ref", Code.OUTWARD_MEANING_MISMATCH, "selected meaning ancestry mismatch")
    if selected.record_id not in outward.outward_basis_refs:
        _issue(issues, "result.governed_outward_meaning_record.outward_basis_refs", Code.OUTWARD_MEANING_MISMATCH, "selected meaning basis missing")
    if outward.permitted_claims != outward_fields["permitted_claims"]:
        _issue(issues, "result.governed_outward_meaning_record.permitted_claims", Code.OUTWARD_MEANING_MISMATCH, "permitted claims mismatch")
    if outward.required_qualifications != outward_fields["required_qualifications"]:
        _issue(issues, "result.governed_outward_meaning_record.required_qualifications", Code.OUTWARD_MEANING_MISMATCH, "qualification custody mismatch")
    if outward.prohibited_enlargements != outward_fields["prohibited_enlargements"]:
        _issue(issues, "result.governed_outward_meaning_record.prohibited_enlargements", Code.OUTWARD_MEANING_MISMATCH, "prohibited enlargement custody mismatch")
    if outward.preservation_classes != outward_fields["preservation_classes"]:
        _issue(issues, "result.governed_outward_meaning_record.preservation_classes", Code.OUTWARD_MEANING_MISMATCH, "preservation classes mismatch")

    expression = value.expression_link_record
    if expression.record_id != expected_expression_link_id(expression):
        _issue(issues, "result.expression_link_record.record_id", Code.IDENTITY_MISMATCH, "expression-link ID mismatch")
    if expression.governed_outward_meaning_ref != outward.record_id:
        _issue(issues, "result.expression_link_record.governed_outward_meaning_ref", Code.EXPRESSION_LINK_MISMATCH, "outward meaning reference mismatch")
    if expression.expression_candidate_ref != candidate.expression_candidate_id:
        _issue(issues, "result.expression_link_record.expression_candidate_ref", Code.EXPRESSION_LINK_MISMATCH, "expression candidate reference mismatch")

    authority = value.external_authority_reference_record
    if authority.record_id != expected_authority_reference_id(authority):
        _issue(issues, "result.external_authority_reference_record.record_id", Code.IDENTITY_MISMATCH, "authority record ID mismatch")
    if authority.authority_kind is not ExternalAuthorityKind.RENDER_PREVIEW_OR_OUTPUT_OBJECT:
        _issue(issues, "result.external_authority_reference_record.authority_kind", Code.AUTHORITY_REFERENCE_MISMATCH, "render-preview custody kind required")
    if authority.external_object_ref != candidate.expression_candidate_id:
        _issue(issues, "result.external_authority_reference_record.external_object_ref", Code.AUTHORITY_REFERENCE_MISMATCH, "authority must bind exact unvalidated candidate")

    for trace, expected, path in (
        (value.selected_to_outward_trace, expected_selected_trace, "result.selected_to_outward_trace"),
        (value.outward_to_expression_trace, expected_expression_trace, "result.outward_to_expression_trace"),
    ):
        if trace.record_id != expected_transition_trace_id(trace):
            _issue(issues, path + ".record_id", Code.IDENTITY_MISMATCH, "trace ID mismatch")
        if trace.transition_kind is not SemanticTransitionKind.ANCESTRY:
            _issue(issues, path + ".transition_kind", Code.TRANSITION_MISMATCH, "ancestry transition required")
        if trace != expected:
            _issue(issues, path, Code.TRANSITION_MISMATCH, "trace content mismatch")

    expected_successor_id = expected_successor_manifest_id(
        source,
        expected_authority,
        expected_outward,
        expected_expression,
        expected_selected_trace,
        expected_expression_trace,
        integration_input,
    )
    if successor.manifest_id != expected_successor_id:
        _issue(issues, "result.successor_manifest.manifest_id", Code.IDENTITY_MISMATCH, "successor manifest ID mismatch")

    companion = value.companion
    if type(companion) is not MsmOutwardExpressionCustodyCompanionV1:
        _issue(issues, "result.companion", Code.TYPE_MISMATCH, "exact companion type required")
    else:
        if companion.companion_version != SLICE42G_COMPANION_VERSION:
            _issue(issues, "result.companion.companion_version", Code.INVALID_VERSION, "companion version mismatch")
        if companion.companion_id != expected_companion_id(companion):
            _issue(issues, "result.companion.companion_id", Code.IDENTITY_MISMATCH, "companion ID mismatch")
        companion_exact = {
            "integration_input_ref": integration_input.integration_input_id,
            "source_manifest_id": source.manifest_id,
            "source_manifest_sha256": canonical_manifest_sha256(source),
            "successor_manifest_id": successor.manifest_id,
            "successor_manifest_sha256": canonical_manifest_sha256(successor),
            "selected_governed_meaning_ref": selected.record_id,
            "surface_realization_input_ref": integration_input.surface_realization_input.realization_input_id,
            "surface_realization_result_ref": integration_input.surface_realization_result.result_id,
            "expression_candidate_ref": candidate.expression_candidate_id,
            "external_authority_reference_record_ref": authority.record_id,
            "integrated_governed_outward_meaning_ref": outward.record_id,
            "integrated_expression_link_ref": expression.record_id,
            "selected_to_outward_trace_ref": value.selected_to_outward_trace.record_id,
            "outward_to_expression_trace_ref": value.outward_to_expression_trace.record_id,
        }
        for name, expected in companion_exact.items():
            if getattr(companion, name) != expected:
                _issue(issues, f"result.companion.{name}", Code.CANONICAL_MISMATCH, "companion field mismatch")
        before_after = (
            ("candidate_refs", _record_ids(source.candidate_meanings), _record_ids(successor.candidate_meanings)),
            ("non_selection_refs", _record_ids(source.non_selection_outcomes), _record_ids(successor.non_selection_outcomes)),
            ("selected_refs", _record_ids(source.selected_governed_meanings), _record_ids(successor.selected_governed_meanings)),
            ("governed_result_refs", _record_ids(source.governed_result_references), _record_ids(successor.governed_result_references)),
            ("governed_outward_refs", _record_ids(source.governed_outward_meanings), _record_ids(successor.governed_outward_meanings)),
            ("expression_link_refs", _record_ids(source.expression_links), _record_ids(successor.expression_links)),
            ("validation_link_refs", _record_ids(source.validation_links), _record_ids(successor.validation_links)),
            ("delivery_link_refs", _record_ids(source.delivery_or_containment_links), _record_ids(successor.delivery_or_containment_links)),
            ("external_authority_refs", _record_ids(source.external_authority_references), _record_ids(successor.external_authority_references)),
            ("transition_trace_refs", _record_ids(source.semantic_transition_traces), _record_ids(successor.semantic_transition_traces)),
        )
        for prefix, before, after in before_after:
            if getattr(companion, prefix + "_before") != before:
                _issue(issues, f"result.companion.{prefix}_before", Code.RETENTION_MISMATCH, "before custody mismatch")
            if getattr(companion, prefix + "_after") != after:
                _issue(issues, f"result.companion.{prefix}_after", Code.RETENTION_MISMATCH, "after custody mismatch")
        true_names = (
            "exact_adapter", "lossless_custody", "immutable_successor",
            "exact_slice41e_chain_preserved", "exact_slice42f_candidate_preserved",
            "selected_meaning_preserved", "all_candidate_meanings_retained",
            "all_non_selection_outcomes_retained", "alternatives_and_unresolved_retained",
            "governed_outward_meaning_integrated", "expression_link_integrated",
            "candidate_remains_unvalidated", "complete_successor_manifest_validated",
        )
        for name in true_names:
            _exact_bool(getattr(companion, name), True, f"result.companion.{name}", issues)
        for name in ("msm_schema_modified", "automatic_migration_performed"):
            _exact_bool(getattr(companion, name), False, f"result.companion.{name}", issues)

    receipt = value.receipt
    if type(receipt) is not MsmOutwardExpressionIntegrationReceiptV1:
        _issue(issues, "result.receipt", Code.TYPE_MISMATCH, "exact receipt type required")
    else:
        if receipt.receipt_version != SLICE42G_RECEIPT_VERSION:
            _issue(issues, "result.receipt.receipt_version", Code.INVALID_VERSION, "receipt version mismatch")
        if receipt.receipt_id != expected_receipt_id(receipt):
            _issue(issues, "result.receipt.receipt_id", Code.IDENTITY_MISMATCH, "receipt ID mismatch")
        if receipt.source_manifest_sha256 != canonical_manifest_sha256(source):
            _issue(issues, "result.receipt.source_manifest_sha256", Code.DIGEST_MISMATCH, "source digest mismatch")
        if receipt.successor_manifest_sha256 != canonical_manifest_sha256(successor):
            _issue(issues, "result.receipt.successor_manifest_sha256", Code.DIGEST_MISMATCH, "successor digest mismatch")
        count_pairs = (
            ("candidate", source.candidate_meanings, successor.candidate_meanings),
            ("non_selection", source.non_selection_outcomes, successor.non_selection_outcomes),
            ("selected", source.selected_governed_meanings, successor.selected_governed_meanings),
            ("governed_result", source.governed_result_references, successor.governed_result_references),
            ("outward_meaning", source.governed_outward_meanings, successor.governed_outward_meanings),
            ("expression_link", source.expression_links, successor.expression_links),
            ("validation_link", source.validation_links, successor.validation_links),
            ("delivery_link", source.delivery_or_containment_links, successor.delivery_or_containment_links),
        )
        for prefix, before, after in count_pairs:
            if getattr(receipt, prefix + "_count_before") != len(before):
                _issue(issues, f"result.receipt.{prefix}_count_before", Code.RETENTION_MISMATCH, "before count mismatch")
            if getattr(receipt, prefix + "_count_after") != len(after):
                _issue(issues, f"result.receipt.{prefix}_count_after", Code.RETENTION_MISMATCH, "after count mismatch")
        true_names = (
            "deterministic", "additive_only", "immutable_successor_created",
            "complete_manifest_validated", "selected_meaning_preserved",
            "candidates_retained", "non_selection_outcomes_retained",
            "alternatives_and_unresolved_retained", "governed_outward_meaning_integrated",
            "expression_link_integrated", "candidate_remains_unvalidated",
        )
        false_names = (
            "msm_schema_modified", "automatic_migration_performed",
            "governed_result_reference_created", "validation_link_created",
            "delivery_link_created", "echo_validated_or_approved",
            "delivery_authorized_or_performed", "truth_evidence_permission_execution",
            "route_tool_action_memory_filesystem_network",
            "external_resource_or_model_authority", "bootstrap_integration_enabled",
            "gp014_superseded",
        )
        for name in true_names:
            _exact_bool(getattr(receipt, name), True, f"result.receipt.{name}", issues)
        for name in false_names:
            _exact_bool(getattr(receipt, name), False, f"result.receipt.{name}", issues)

    true_result_names = (
        "deterministic", "additive_only", "immutable_successor_created",
        "exact_slice41e_chain_preserved", "exact_slice42f_candidate_preserved",
        "dormant_msm_records_used", "selected_meaning_preserved",
        "all_candidate_meanings_retained", "all_non_selection_outcomes_retained",
        "alternatives_and_unresolved_retained", "governed_outward_meaning_integrated",
        "expression_link_integrated", "complete_successor_manifest_validated",
        "candidate_remains_unvalidated",
    )
    false_result_names = (
        "msm_schema_modified", "automatic_migration_performed", "source_manifest_mutated",
        "candidate_deleted", "non_selection_outcome_deleted", "selected_meaning_rewritten",
        "governed_result_reference_created", "validation_link_created", "delivery_link_created",
        "expression_candidate_rewritten", "claim_strengthened", "certainty_upgraded",
        "evidence_status_upgraded", "caveat_omitted", "refusal_softened",
        "ambiguity_erased", "unsupported_state_erased", "echo_validation_performed",
        "echo_approved", "delivery_authorized", "delivered", "truth_determined",
        "evidence_validated", "permission_granted", "execution_authorized",
        "route_or_api_created", "tool_invoked", "action_performed",
        "memory_accessed_or_written", "filesystem_or_network_accessed",
        "external_resource_loaded", "model_or_similarity_authority_used",
        "bootstrap_integration_enabled", "gp014_superseded",
    )
    for name in true_result_names:
        _exact_bool(getattr(value, name), True, f"result.{name}", issues)
    for name in false_result_names:
        _exact_bool(getattr(value, name), False, f"result.{name}", issues)

    try:
        expected_digest = expected_result_digest(value)
        expected_id = expected_result_id(value)
    except Exception as error:
        _issue(issues, "result", Code.CANONICAL_MISMATCH, str(error))
    else:
        if value.result_digest != expected_digest:
            _issue(issues, "result.result_digest", Code.DIGEST_MISMATCH, "result digest mismatch")
        if value.result_id != expected_id:
            _issue(issues, "result.result_id", Code.IDENTITY_MISMATCH, "result ID mismatch")
    return _report(issues)


def assert_valid_integration_input(
    value: MsmOutwardExpressionIntegrationInput,
) -> None:
    report = validate_integration_input(value)
    if not report.ok:
        raise MsmOutwardExpressionIntegrationValidationError(report)


def assert_valid_integration_result(
    value: MsmOutwardExpressionIntegrationResult,
    *,
    integration_input: MsmOutwardExpressionIntegrationInput,
) -> None:
    report = validate_integration_result(value, integration_input=integration_input)
    if not report.ok:
        raise MsmOutwardExpressionIntegrationValidationError(report)


__all__ = (
    "assert_valid_integration_input",
    "assert_valid_integration_result",
    "validate_authority_profile",
    "validate_integration_input",
    "validate_integration_result",
)
