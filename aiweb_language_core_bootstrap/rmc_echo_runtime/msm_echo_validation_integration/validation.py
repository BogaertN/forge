"""Deterministic validation for Slice 43G integration."""

from __future__ import annotations

from typing import Any

from ...meaning_structure_manifest import DeliveryContainmentKind
from ...meaning_structure_manifest.serialization import canonical_manifest_sha256
from ...meaning_structure_manifest.validation import validate_manifest
from ...outward_expression_runtime.msm_outward_expression_integration import (
    MsmOutwardExpressionIntegrationInput,
    MsmOutwardExpressionIntegrationResult,
    expected_result_digest as expected_42g_result_digest,
    expected_result_id as expected_42g_result_id,
)
from ..drift_materiality_classification import (
    DriftClassificationResult,
    expected_result_digest as expected_43e_result_digest,
    expected_result_id as expected_43e_result_id,
)
from ..echo_disposition import (
    EchoDisposition,
    EchoDispositionResult,
    expected_result_digest as expected_43f_result_digest,
    expected_result_id as expected_43f_result_id,
)
from .authority import (
    PERMANENT_AUTHORITY_ZERO,
    REQUESTED_OPERATION,
    SLICE43G_PROFILE_VERSION,
    SLICE43G_SCHEMA_VERSION,
    VALIDATION_DISPOSITIONS,
)
from .identity import (
    expected_companion_id,
    expected_input_id,
    expected_receipt_id,
    expected_result_digest,
    expected_result_id,
)
from .rules import (
    containment_record_ref,
    exact_chain_is_proved,
    rejection_record_ref,
)
from .schema import (
    MsmEchoValidationIntegrationCode as Code,
    MsmEchoValidationIntegrationError,
    MsmEchoValidationIntegrationInput,
    MsmEchoValidationIntegrationIssue as Issue,
    MsmEchoValidationIntegrationReport as Report,
    MsmEchoValidationIntegrationResult,
    MsmEchoValidationIntegrationStatus,
)


def _issue(issues: list[Issue], path: str, code: Code, detail: str) -> None:
    issues.append(Issue(path, code, detail))


def _report(issues: list[Issue]) -> Report:
    return Report(tuple(issues))


def validate_integration_input(value: Any) -> Report:
    issues: list[Issue] = []
    if type(value) is not MsmEchoValidationIntegrationInput:
        return _report([Issue("integration_input", Code.TYPE_MISMATCH, "exact input type required")])

    if value.schema_version != SLICE43G_SCHEMA_VERSION or value.profile_version != SLICE43G_PROFILE_VERSION:
        _issue(issues, "integration_input.version", Code.INVALID_VERSION, "unsupported version")
    if value.requested_operation != REQUESTED_OPERATION:
        _issue(issues, "integration_input.requested_operation", Code.INVALID_TEXT, "wrong operation")
    if value.explicit_integration_request is not True or value.raw_text is not None:
        _issue(issues, "integration_input.request", Code.PROHIBITED_AUTHORITY, "explicit typed request with no raw text required")

    if type(value.source_42g_input) is not MsmOutwardExpressionIntegrationInput:
        _issue(issues, "integration_input.source_42g_input", Code.SOURCE_42G_INVALID, "exact Slice 42G input required")
    if type(value.source_42g_result) is not MsmOutwardExpressionIntegrationResult:
        _issue(issues, "integration_input.source_42g_result", Code.SOURCE_42G_INVALID, "exact Slice 42G result required")
    elif type(value.source_42g_input) is MsmOutwardExpressionIntegrationInput:
        result42 = value.source_42g_result
        if (
            result42.integration_input_ref
            != value.source_42g_input.integration_input_id
            or result42.result_id != expected_42g_result_id(result42)
            or result42.result_digest != expected_42g_result_digest(result42)
            or result42.complete_successor_manifest_validated is not True
            or result42.candidate_remains_unvalidated is not True
        ):
            _issue(issues, "integration_input.source_42g_result", Code.SOURCE_42G_INVALID, "Slice 42G identity or accepted custody flags invalid")

    if type(value.source_43e_classification_result) is not DriftClassificationResult:
        _issue(issues, "integration_input.source_43e_classification_result", Code.SOURCE_43E_INVALID, "exact Slice 43E result required")
    else:
        result43e = value.source_43e_classification_result
        if (
            result43e.classification_result_id != expected_43e_result_id(result43e)
            or result43e.classification_result_digest
            != expected_43e_result_digest(result43e)
            or result43e.classification_package is None
            or result43e.drift_classification_performed is not True
            or result43e.materiality_findings_created is not True
        ):
            _issue(issues, "integration_input.source_43e_classification_result", Code.SOURCE_43E_INVALID, "Slice 43E identity or accepted custody flags invalid")

    if type(value.source_43f_disposition_result) is not EchoDispositionResult:
        _issue(issues, "integration_input.source_43f_disposition_result", Code.SOURCE_43F_INVALID, "exact Slice 43F result required")
    elif type(value.source_43e_classification_result) is DriftClassificationResult:
        result43f = value.source_43f_disposition_result
        package43f = result43f.disposition_package
        if (
            result43f.disposition_result_id != expected_43f_result_id(result43f)
            or result43f.disposition_result_digest
            != expected_43f_result_digest(result43f)
            or package43f is None
            or result43f.disposition_decided is not True
            or result43f.classification_result_ref
            != value.source_43e_classification_result.classification_result_id
            or package43f.classification_result_ref
            != value.source_43e_classification_result.classification_result_id
        ):
            _issue(issues, "integration_input.source_43f_disposition_result", Code.SOURCE_43F_INVALID, "Slice 43F identity or accepted custody flags invalid")

    disposition = getattr(value.source_43f_disposition_result, "disposition", None)
    if (
        disposition is None
        or getattr(disposition, "value", None) not in VALIDATION_DISPOSITIONS
        or not getattr(value.source_43f_disposition_result, "disposition_decided", False)
    ):
        _issue(issues, "integration_input.disposition", Code.DISPOSITION_MISMATCH, "exact decided disposition required")

    if not exact_chain_is_proved(value):
        _issue(issues, "integration_input.source_chain", Code.SOURCE_CHAIN_MISMATCH, "42G expression and 43F validation ancestry do not match")

    source_manifest = value.source_42g_result.successor_manifest
    if not validate_manifest(source_manifest).ok:
        _issue(issues, "integration_input.source_manifest", Code.SOURCE_MANIFEST_INVALID, "source manifest invalid")
    if source_manifest.validation_links:
        _issue(issues, "integration_input.source_manifest.validation_links", Code.DORMANT_RECORD_MISMATCH, "accepted source must have no prior validation link")
    if source_manifest.delivery_or_containment_links:
        _issue(issues, "integration_input.source_manifest.delivery_or_containment_links", Code.DORMANT_RECORD_MISMATCH, "accepted source must have no prior delivery or containment link")

    expected_containment = disposition is EchoDisposition.CONTAINED
    expected_rejection = disposition is EchoDisposition.REJECTED
    if value.validation_link_creation_requested is not True:
        _issue(issues, "integration_input.validation_link_creation_requested", Code.VALIDATION_LINK_MISMATCH, "validation link must be requested")
    if value.containment_custody_requested is not expected_containment:
        _issue(issues, "integration_input.containment_custody_requested", Code.CONTAINMENT_CUSTODY_MISMATCH, "containment request must match disposition")
    if value.rejection_custody_requested is not expected_rejection:
        _issue(issues, "integration_input.rejection_custody_requested", Code.REJECTION_CUSTODY_MISMATCH, "rejection request must match disposition")
    if expected_containment and containment_record_ref(value) is None:
        _issue(issues, "integration_input.containment_record", Code.CONTAINMENT_CUSTODY_MISMATCH, "contained disposition requires exact containment record")
    if expected_rejection and rejection_record_ref(value) is None:
        _issue(issues, "integration_input.rejection_record", Code.REJECTION_CUSTODY_MISMATCH, "rejected disposition requires exact rejection record")

    prohibited = (
        value.delivery_link_creation_requested,
        value.candidate_rewrite_requested,
        value.drift_suppression_requested,
        value.delivery_requested,
        value.echoforge_requested,
        value.model_or_similarity_authority_requested,
        value.truth_evidence_permission_execution_requested,
        value.route_api_network_filesystem_memory_tool_action_requested,
        value.msm_schema_rewrite_requested,
        value.gp014_supersession_requested,
    )
    if any(item is not False for item in prohibited):
        _issue(issues, "integration_input.prohibited_requests", Code.PROHIBITED_AUTHORITY, "all prohibited requests must be false")

    try:
        expected = expected_input_id(value)
    except Exception as error:
        _issue(issues, "integration_input.integration_input_id", Code.IDENTITY_MISMATCH, str(error))
    else:
        if value.integration_input_id != expected:
            _issue(issues, "integration_input.integration_input_id", Code.IDENTITY_MISMATCH, "input identity mismatch")
    return _report(issues)


def validate_integration_result(
    value: Any,
    *,
    integration_input: MsmEchoValidationIntegrationInput,
) -> Report:
    issues = list(validate_integration_input(integration_input).issues)
    if issues:
        return _report(issues)
    if type(value) is not MsmEchoValidationIntegrationResult:
        return _report(issues + [Issue("result", Code.TYPE_MISMATCH, "exact result type required")])

    from .integration import construct_successor_artifacts
    expected = construct_successor_artifacts(integration_input)
    validation_authority, containment_authority, validation, validation_trace, containment, containment_trace, successor, _, _ = expected
    source = integration_input.source_42g_result.successor_manifest
    disposition = integration_input.source_43f_disposition_result.disposition

    if value.status is not MsmEchoValidationIntegrationStatus.SUCCESSOR_CREATED:
        _issue(issues, "result.status", Code.RESULT_INVALID, "successor-created status required")
    if value.source_manifest != source:
        _issue(issues, "result.source_manifest", Code.RETENTION_MISMATCH, "source manifest not preserved")
    if value.successor_manifest != successor:
        _issue(issues, "result.successor_manifest", Code.SUCCESSOR_MANIFEST_INVALID, "successor mismatch")
    if value.validation_link_record != validation:
        _issue(issues, "result.validation_link_record", Code.VALIDATION_LINK_MISMATCH, "validation link mismatch")
    if value.validation_transition_trace != validation_trace:
        _issue(issues, "result.validation_transition_trace", Code.TRACE_MISMATCH, "validation trace mismatch")
    if value.containment_link_record != containment:
        _issue(issues, "result.containment_link_record", Code.CONTAINMENT_CUSTODY_MISMATCH, "containment link mismatch")
    if value.containment_transition_trace != containment_trace:
        _issue(issues, "result.containment_transition_trace", Code.TRACE_MISMATCH, "containment trace mismatch")
    if value.validation_disposition is not disposition:
        _issue(issues, "result.validation_disposition", Code.DISPOSITION_MISMATCH, "disposition mismatch")
    if not validate_manifest(value.successor_manifest).ok:
        _issue(issues, "result.successor_manifest", Code.SUCCESSOR_MANIFEST_INVALID, "successor does not validate")

    unchanged = (
        "lineage_root",
        "candidate_meanings",
        "non_selection_outcomes",
        "selected_governed_meanings",
        "governed_result_references",
        "governed_outward_meanings",
        "expression_links",
        "package_id",
        "schema_id",
        "schema_version",
    )
    for name in unchanged:
        if getattr(source, name) != getattr(value.successor_manifest, name):
            _issue(issues, f"result.successor_manifest.{name}", Code.RETENTION_MISMATCH, "source custody changed")

    added_authority = value.successor_manifest.external_authority_references[
        len(source.external_authority_references):
    ]
    expected_authority = (
        (validation_authority, containment_authority)
        if containment_authority is not None
        else (validation_authority,)
    )
    if added_authority != expected_authority:
        _issue(issues, "result.successor_manifest.external_authority_references", Code.RETENTION_MISMATCH, "exact validation/containment authority references required")
    if value.validation_authority_reference_record != validation_authority:
        _issue(issues, "result.validation_authority_reference_record", Code.RETENTION_MISMATCH, "validation authority mismatch")
    if value.containment_authority_reference_record != containment_authority:
        _issue(issues, "result.containment_authority_reference_record", Code.RETENTION_MISMATCH, "containment authority mismatch")

    added_validation = value.successor_manifest.validation_links[len(source.validation_links):]
    if added_validation != (validation,):
        _issue(issues, "result.successor_manifest.validation_links", Code.VALIDATION_LINK_MISMATCH, "exactly one validation link must be added")
    added_custody = value.successor_manifest.delivery_or_containment_links[len(source.delivery_or_containment_links):]
    if disposition is EchoDisposition.CONTAINED:
        if added_custody != (containment,) or containment is None or containment.disposition is not DeliveryContainmentKind.CONTAINMENT_LINKED:
            _issue(issues, "result.successor_manifest.delivery_or_containment_links", Code.CONTAINMENT_CUSTODY_MISMATCH, "exact containment custody required")
    elif added_custody:
        _issue(issues, "result.successor_manifest.delivery_or_containment_links", Code.DELIVERY_LINK_PROHIBITED, "no delivery or false containment link allowed")

    if any(item.disposition is DeliveryContainmentKind.DELIVERY_LINKED for item in added_custody):
        _issue(issues, "result.successor_manifest.delivery_or_containment_links", Code.DELIVERY_LINK_PROHIBITED, "delivery link is prohibited")

    if value.companion is None or value.receipt is None:
        _issue(issues, "result.custody", Code.RESULT_INVALID, "companion and receipt required")
    else:
        if value.companion.companion_id != expected_companion_id(value.companion):
            _issue(issues, "result.companion.identity", Code.IDENTITY_MISMATCH, "companion identity mismatch")
        if value.receipt.receipt_id != expected_receipt_id(value.receipt):
            _issue(issues, "result.receipt.identity", Code.IDENTITY_MISMATCH, "receipt identity mismatch")
        if value.receipt.source_manifest_sha256 != canonical_manifest_sha256(source):
            _issue(issues, "result.receipt.source_manifest_sha256", Code.IDENTITY_MISMATCH, "source digest mismatch")
        if value.receipt.successor_manifest_sha256 != canonical_manifest_sha256(successor):
            _issue(issues, "result.receipt.successor_manifest_sha256", Code.IDENTITY_MISMATCH, "successor digest mismatch")

    if value.result_id != expected_result_id(value) or value.result_digest != expected_result_digest(value):
        _issue(issues, "result.identity", Code.IDENTITY_MISMATCH, "result identity mismatch")

    for name in PERMANENT_AUTHORITY_ZERO:
        if getattr(value, name) is not False:
            _issue(issues, f"result.{name}", Code.PROHIBITED_AUTHORITY, "permanent authority-zero boundary violated")
    return _report(issues)


def assert_valid_integration_input(value):
    report = validate_integration_input(value)
    if not report.ok:
        raise MsmEchoValidationIntegrationError(report)
    return value


def assert_valid_integration_result(value, *, integration_input):
    report = validate_integration_result(value, integration_input=integration_input)
    if not report.ok:
        raise MsmEchoValidationIntegrationError(report)
    return value


__all__ = (
    "assert_valid_integration_input",
    "assert_valid_integration_result",
    "validate_integration_input",
    "validate_integration_result",
)
