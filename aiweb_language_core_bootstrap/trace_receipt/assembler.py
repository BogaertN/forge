"""Explicit offline Slice 33 trace and receipt assembly.

The assembler runs one exact accepted Slice 31 or Slice 32 fixture flow and
returns an immutable in-memory trace/receipt bundle. It never persists the
records or grants authority.
"""

from __future__ import annotations

from ..bootstrap_adapter import (
    build_bootstrap_adapter_state,
    get_bootstrap_fixture,
    run_bootstrap_fixture,
    validate_bootstrap_adapter_result,
    validate_bootstrap_adapter_state,
    validate_bootstrap_fixture_record,
)
from ..component_loading import (
    build_component_loading_state,
    get_component_loading_fixture,
    run_component_loading_fixture,
    validate_component_loading_fixture_record,
    validate_component_loading_result,
    validate_component_loading_state,
)
from .flow_catalog import (
    build_expected_receipt,
    build_expected_trace,
    get_trace_flow,
)
from .schema import (
    ASSEMBLY_COMPLETED_REASON,
    ASSEMBLY_DISABLED_REASON,
    STATUS_COMPLETED,
    STATUS_HELD_INVALID_STATE,
    STATUS_HELD_RECEIPT_MISMATCH,
    STATUS_HELD_SOURCE_RESULT_MISMATCH,
    STATUS_HELD_TRACE_MISMATCH,
    STATUS_HELD_UNKNOWN_FLOW,
    STATUS_REFUSED_DISABLED,
    AcceptedTraceFlowSpec,
    TraceReceiptAssemblyResult,
    TraceReceiptAssemblyState,
    build_trace_receipt_assembly_result,
    validate_derivation_receipt_record,
    validate_derivation_trace_record,
    validate_trace_receipt_assembly_state,
)


def _result(
    *,
    flow_spec_id: str,
    flow_name: str,
    assembly_state_id: str,
    status: str,
    reason_code: str,
    trace=None,
    receipt=None,
) -> TraceReceiptAssemblyResult:
    return build_trace_receipt_assembly_result(
        flow_spec_id=flow_spec_id,
        flow_name=flow_name,
        assembly_state_id=assembly_state_id,
        status=status,
        reason_code=reason_code,
        trace=trace,
        receipt=receipt,
        deterministic=True,
        fixture_only=True,
        offline_only=True,
        read_only=True,
        persistent_side_effect_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        memory_write_performed=False,
        evidence_mutation_performed=False,
        external_resource_used=False,
        delivery_performed=False,
        tool_routing_performed=False,
        action_performed=False,
        component_invocation_performed=False,
        component_verifier_invocation_performed=False,
        gp014_imported=False,
        gp014_called=False,
        runtime_connection_performed=False,
    )


def _slice31_source_matches(spec: AcceptedTraceFlowSpec) -> bool:
    fixture = get_bootstrap_fixture(spec.fixture_name)
    if fixture is None:
        return False
    state = build_bootstrap_adapter_state(
        explicit_offline_developer_enable=spec.source_enabled,
    )
    if not validate_bootstrap_adapter_state(state).ok:
        return False
    if not validate_bootstrap_fixture_record(fixture).ok:
        return False
    result = run_bootstrap_fixture(fixture, adapter_state=state)
    if not validate_bootstrap_adapter_result(result).ok:
        return False
    if (
        fixture.fixture_id != spec.fixture_id
        or state.adapter_state_id != spec.source_state_id
        or result.result_id != spec.expected_source_result_id
        or result.status != spec.expected_source_status
        or result.reason_code != spec.expected_source_reason_code
    ):
        return False
    if any(
        (
            result.side_effects_performed,
            result.component_loading_performed,
            result.external_resource_used,
            result.memory_write_performed,
            result.evidence_mutation_performed,
            result.delivery_performed,
            result.tool_routing_performed,
            result.action_performed,
            result.runtime_connection_performed,
        )
    ):
        return False
    observation = result.observation
    if spec.expected_observation_id:
        if observation is None:
            return False
        return (
            observation.observation_id == spec.expected_observation_id
            and observation.authority_state_id
            == spec.expected_authority_state_id
            and observation.import_policy_id == spec.expected_import_policy_id
            and observation.bootstrap_boundary_id
            == spec.expected_bootstrap_boundary_id
            and observation.component_registry_id
            == spec.expected_component_registry_id
            and observation.component_count == 15
            and observation.component_loading_performed is False
            and observation.runtime_connection_performed is False
            and observation.persistent_side_effect_performed is False
        )
    return observation is None


def _slice32_source_matches(spec: AcceptedTraceFlowSpec) -> bool:
    try:
        fixture = get_component_loading_fixture(spec.fixture_name)
    except KeyError:
        return False
    state = build_component_loading_state(enabled=spec.source_enabled)
    if not validate_component_loading_state(state).ok:
        return False
    if not validate_component_loading_fixture_record(fixture).ok:
        return False
    result = run_component_loading_fixture(fixture, loading_state=state)
    if not validate_component_loading_result(result).ok:
        return False
    loaded_names = tuple(item.package_name for item in result.loaded_components)
    loaded_ids = tuple(item.loaded_component_id for item in result.loaded_components)
    if (
        fixture.fixture_id != spec.fixture_id
        or state.loading_state_id != spec.source_state_id
        or result.loading_result_id != spec.expected_source_result_id
        or result.status != spec.expected_source_status
        or result.reason_code != spec.expected_source_reason_code
        or result.bootstrap_boundary_id != spec.expected_bootstrap_boundary_id
        or result.component_registry_id != spec.expected_component_registry_id
        or result.loaded_component_count != spec.expected_loaded_component_count
        or loaded_names != spec.expected_loaded_package_names
        or loaded_ids != spec.expected_loaded_component_ids
    ):
        return False
    if any(
        (
            result.component_invocation_performed,
            result.verifier_invocation_performed,
            result.dynamic_discovery_performed,
            result.hidden_fallback_used,
            result.network_access_performed,
            result.external_data_filesystem_read_performed,
            result.filesystem_write_performed,
            result.memory_write_performed,
            result.evidence_mutation_performed,
            result.external_resource_used,
            result.delivery_performed,
            result.tool_routing_performed,
            result.action_performed,
            result.gp014_imported,
            result.gp014_called,
            result.persistent_side_effect_performed,
            result.runtime_connection_performed,
        )
    ):
        return False
    return all(
        item.component_invoked is False
        and item.verifier_invoked is False
        and item.runtime_authority_granted is False
        and item.persistent_side_effect_performed is False
        and item.interface_verified is True
        for item in result.loaded_components
    )


def _source_flow_matches(spec: AcceptedTraceFlowSpec) -> bool:
    if spec.source_slice == "Slice 31":
        return _slice31_source_matches(spec)
    if spec.source_slice == "Slice 32":
        return _slice32_source_matches(spec)
    return False


def assemble_trace_receipt(
    flow_name: str,
    *,
    assembly_state: TraceReceiptAssemblyState,
) -> TraceReceiptAssemblyResult:
    """Run one exact fixture flow and assemble an in-memory trace and receipt."""

    spec = get_trace_flow(flow_name)
    if spec is None:
        return _result(
            flow_spec_id="",
            flow_name=flow_name,
            assembly_state_id=assembly_state.assembly_state_id,
            status=STATUS_HELD_UNKNOWN_FLOW,
            reason_code="flow_not_in_exact_static_catalog",
        )

    if not validate_trace_receipt_assembly_state(assembly_state).ok:
        return _result(
            flow_spec_id=spec.flow_spec_id,
            flow_name=spec.flow_name,
            assembly_state_id=assembly_state.assembly_state_id,
            status=STATUS_HELD_INVALID_STATE,
            reason_code="trace_receipt_assembly_state_validation_failed",
        )

    if not assembly_state.enabled:
        return _result(
            flow_spec_id=spec.flow_spec_id,
            flow_name=spec.flow_name,
            assembly_state_id=assembly_state.assembly_state_id,
            status=STATUS_REFUSED_DISABLED,
            reason_code=ASSEMBLY_DISABLED_REASON,
        )

    if not _source_flow_matches(spec):
        return _result(
            flow_spec_id=spec.flow_spec_id,
            flow_name=spec.flow_name,
            assembly_state_id=assembly_state.assembly_state_id,
            status=STATUS_HELD_SOURCE_RESULT_MISMATCH,
            reason_code="source_fixture_flow_did_not_match_accepted_identity",
        )

    trace = build_expected_trace(
        spec,
        assembly_state_id=assembly_state.assembly_state_id,
    )
    if not validate_derivation_trace_record(trace).ok:
        return _result(
            flow_spec_id=spec.flow_spec_id,
            flow_name=spec.flow_name,
            assembly_state_id=assembly_state.assembly_state_id,
            status=STATUS_HELD_TRACE_MISMATCH,
            reason_code="assembled_trace_did_not_match_accepted_identity",
        )

    receipt = build_expected_receipt(spec)
    if not validate_derivation_receipt_record(receipt).ok:
        return _result(
            flow_spec_id=spec.flow_spec_id,
            flow_name=spec.flow_name,
            assembly_state_id=assembly_state.assembly_state_id,
            status=STATUS_HELD_RECEIPT_MISMATCH,
            reason_code="assembled_receipt_did_not_match_accepted_identity",
        )

    return _result(
        flow_spec_id=spec.flow_spec_id,
        flow_name=spec.flow_name,
        assembly_state_id=assembly_state.assembly_state_id,
        status=STATUS_COMPLETED,
        reason_code=ASSEMBLY_COMPLETED_REASON,
        trace=trace,
        receipt=receipt,
    )
