"""Unprojected source-linked field envelope and typed application refusal.

Slice 36B0 defines the contract that Slice 36B will later populate. It does not
segment source, bind an operator, assign a phase, or create a successor field.
"""

from __future__ import annotations

from ..input_event_custody import (
    InputCustodyStatus,
    InputEventRecord,
    validate_input_event,
)
from ..schema import stable_record_id
from .registry import build_default_rsoc_operator_registry, operator_contract_for_key
from .schema import (
    CONTRACT_SCHEMA_VERSION,
    CONTRACT_SPEC_ID,
    CONTRACT_SPEC_VERSION,
    FIELD_SCHEMA_ID,
    FieldContainmentStatus,
    FieldEnvelopeBuildResult,
    FieldEnvelopeBuildStatus,
    FieldPhaseStatus,
    FieldProjectionStatus,
    FieldSupportStatus,
    OperatorApplicationDecision,
    OperatorApplicationStatus,
    ResonantLanguageFieldEnvelope,
)


def _build_result(
    *,
    status: FieldEnvelopeBuildStatus,
    reason_code: str,
    envelope_created: bool,
    structural_progression_allowed: bool,
    field: ResonantLanguageFieldEnvelope | None,
    validation_issue_codes: tuple[str, ...],
) -> FieldEnvelopeBuildResult:
    body = {
        "status": status,
        "reason_code": reason_code,
        "envelope_created": envelope_created,
        "structural_progression_allowed": structural_progression_allowed,
        "field": field,
        "validation_issue_codes": validation_issue_codes,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "network_access_performed": False,
        "environment_access_performed": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "route_registration_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "delivery_performed": False,
        "contract_spec_id": CONTRACT_SPEC_ID,
        "contract_spec_version": CONTRACT_SPEC_VERSION,
        "schema_version": CONTRACT_SCHEMA_VERSION,
    }
    return FieldEnvelopeBuildResult(
        result_id=stable_record_id("field_envelope_build_result", body),
        **body,
    )


def build_unprojected_language_field(
    input_event: object,
) -> FieldEnvelopeBuildResult:
    """Create only an inert field envelope from a valid supported 36A event."""

    if type(input_event) is not InputEventRecord:
        return _build_result(
            status=FieldEnvelopeBuildStatus.REJECTED_INVALID_INPUT_EVENT,
            reason_code="invalid_input_event_type",
            envelope_created=False,
            structural_progression_allowed=False,
            field=None,
            validation_issue_codes=("invalid_input_event_type",),
        )

    report = validate_input_event(input_event)
    if not report.ok:
        return _build_result(
            status=FieldEnvelopeBuildStatus.REJECTED_INVALID_INPUT_EVENT,
            reason_code="invalid_input_event_record",
            envelope_created=False,
            structural_progression_allowed=False,
            field=None,
            validation_issue_codes=tuple(issue.code for issue in report.issues),
        )

    if input_event.custody_status is not InputCustodyStatus.CAPTURED_SUPPORTED:
        return _build_result(
            status=FieldEnvelopeBuildStatus.HELD_UNSUPPORTED_INPUT,
            reason_code="unsupported_input_not_eligible_for_field_projection",
            envelope_created=False,
            structural_progression_allowed=False,
            field=None,
            validation_issue_codes=("unsupported_input",),
        )

    body = {
        "source_event_id": input_event.input_event_id,
        "source_sha256": input_event.source_sha256,
        "source_utf8_byte_length": input_event.utf8_byte_length,
        "source_code_point_length": input_event.code_point_length,
        "root_source_span_id": input_event.root_source_span_id,
        "predecessor_field_id": None,
        "applied_operator_trace_ids": (),
        "covered_source_span_ids": (),
        "unresolved_source_span_ids": (input_event.root_source_span_id,),
        "projection_status": FieldProjectionStatus.UNPROJECTED,
        "phase_status": FieldPhaseStatus.UNASSIGNED,
        "support_status": FieldSupportStatus.UNASSESSED,
        "containment_status": FieldContainmentStatus.NOT_CONTAINED,
        "rsoc_lineage_identity_assigned": False,
        "source_text_copied_or_replaced": False,
        "tokenization_performed": False,
        "operator_binding_performed": False,
        "operator_application_performed": False,
        "phase_assignment_performed": False,
        "concept_lookup_performed": False,
        "predicate_binding_performed": False,
        "meaning_created": False,
        "reference_resolution_performed": False,
        "legacy_runtime_consulted": False,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "network_access_performed": False,
        "environment_access_performed": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "route_registration_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "delivery_performed": False,
        "contract_spec_id": CONTRACT_SPEC_ID,
        "contract_spec_version": CONTRACT_SPEC_VERSION,
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "field_schema_id": FIELD_SCHEMA_ID,
    }
    field = ResonantLanguageFieldEnvelope(
        field_id=stable_record_id("resonant_language_field", body),
        **body,
    )
    return _build_result(
        status=FieldEnvelopeBuildStatus.CREATED_UNPROJECTED,
        reason_code="unprojected_field_contract_created",
        envelope_created=True,
        structural_progression_allowed=False,
        field=field,
        validation_issue_codes=(),
    )


def _application_decision(
    *,
    status: OperatorApplicationStatus,
    reason_code: str,
    requested_operator_key: str,
    field_id: str,
    operator_found: bool,
) -> OperatorApplicationDecision:
    body = {
        "status": status,
        "reason_code": reason_code,
        "requested_operator_key": requested_operator_key,
        "field_id": field_id,
        "operator_found": operator_found,
        "application_performed": False,
        "successor_field_created": False,
        "phase_assigned": False,
        "meaning_created": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "route_registration_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "delivery_performed": False,
        "contract_spec_id": CONTRACT_SPEC_ID,
        "contract_spec_version": CONTRACT_SPEC_VERSION,
        "schema_version": CONTRACT_SCHEMA_VERSION,
    }
    return OperatorApplicationDecision(
        decision_id=stable_record_id("operator_application_decision", body),
        **body,
    )


def evaluate_operator_application(
    field: object,
    operator_key: object,
) -> OperatorApplicationDecision:
    """Return a typed refusal because 36B0 installs contracts, not execution."""

    key = operator_key if type(operator_key) is str else ""
    if type(field) is not ResonantLanguageFieldEnvelope:
        return _application_decision(
            status=OperatorApplicationStatus.REFUSED_INVALID_FIELD,
            reason_code="invalid_resonant_language_field",
            requested_operator_key=key,
            field_id="",
            operator_found=False,
        )
    contract = operator_contract_for_key(
        key,
        build_default_rsoc_operator_registry(),
    )
    if contract is None:
        return _application_decision(
            status=OperatorApplicationStatus.REFUSED_UNKNOWN_OPERATOR,
            reason_code="unknown_rsoc_operator_key",
            requested_operator_key=key,
            field_id=field.field_id,
            operator_found=False,
        )
    return _application_decision(
        status=OperatorApplicationStatus.REFUSED_CONTRACT_ONLY,
        reason_code="operator_execution_not_installed_in_slice36b0",
        requested_operator_key=key,
        field_id=field.field_id,
        operator_found=True,
    )
