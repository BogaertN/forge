"""Read-only in-memory Phase B bootstrap containment evaluator.

The evaluator checks exact accepted Slice 33 flow identities. It intentionally
does not execute the inherited regression matrix or rollback. Those operations
remain external, reviewable proof duties of the Slice 34 installer/verifier.
"""

from __future__ import annotations

from ..trace_receipt import (
    assemble_trace_receipt,
    build_trace_receipt_assembly_state,
    validate_trace_receipt_assembly_result,
)
from .policy import (
    FLOW_IDENTITY_EXPECTATIONS,
    REASON_COMPLETED,
    REASON_DISABLED,
    REQUIRED_CONTAINMENT_GUARDS,
    REQUIRED_INHERITED_REGRESSION_COMMAND_COUNT,
    REQUIRED_PHASE_B_PRESERVATION_COMMAND_COUNT,
    REQUIRED_PRIOR_COMMAND_COUNT,
    STATUS_COMPLETED,
    STATUS_HELD_FLOW_MISMATCH,
    STATUS_HELD_INVALID_STATE,
    STATUS_REFUSED_DISABLED,
)
from .schema import (
    BootstrapContainmentEvaluation,
    BootstrapContainmentState,
    build_bootstrap_containment_evaluation,
    build_bootstrap_containment_state,
    build_flow_containment_proof,
    validate_bootstrap_containment_state,
    validate_flow_containment_proof,
)


def _evaluation(
    *,
    state: BootstrapContainmentState,
    status: str,
    reason_code: str,
    flow_proofs=(),
    runtime_containment_passed: bool = False,
) -> BootstrapContainmentEvaluation:
    return build_bootstrap_containment_evaluation(
        state_id=state.state_id,
        status=status,
        reason_code=reason_code,
        flow_proofs=tuple(flow_proofs),
        required_flow_count=len(FLOW_IDENTITY_EXPECTATIONS),
        validated_flow_count=len(tuple(flow_proofs)),
        containment_guard_ids=REQUIRED_CONTAINMENT_GUARDS,
        runtime_containment_passed=runtime_containment_passed,
        inherited_regression_required=True,
        inherited_regression_command_count=REQUIRED_INHERITED_REGRESSION_COMMAND_COUNT,
        phase_b_preservation_required=True,
        phase_b_preservation_command_count=REQUIRED_PHASE_B_PRESERVATION_COMMAND_COUNT,
        total_prior_command_count=REQUIRED_PRIOR_COMMAND_COUNT,
        inherited_regression_executed_by_runtime=False,
        phase_b_preservation_executed_by_runtime=False,
        one_command_rollback_required=True,
        rollback_executed_by_runtime=False,
        technical_acceptance_granted=False,
        acceptance_widened=False,
        general_language_claim_made=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        runtime_memory_write_performed=False,
        evidence_mutation_performed=False,
        external_resource_used=False,
        component_invocation_performed=False,
        component_verifier_invocation_performed=False,
        gp014_imported=False,
        gp014_called=False,
        delivery_performed=False,
        tool_routing_performed=False,
        action_performed=False,
        runtime_connection_performed=False,
        release_authorized=False,
        production_ready=False,
    )


def _proof_from_result(expectation, result):
    trace = result.trace
    receipt = result.receipt
    if trace is None or receipt is None:
        return None
    exact_identity_match = all(
        (
            result.flow_spec_id == expectation.flow_spec_id,
            result.assembly_result_id == expectation.assembly_result_id,
            trace.trace_id == expectation.trace_id,
            receipt.receipt_id == expectation.receipt_id,
            receipt.verdict == expectation.verdict,
            trace.loaded_component_count == expectation.loaded_component_count,
            trace.loaded_component_set_digest
            == expectation.loaded_component_set_digest,
        )
    )
    proof = build_flow_containment_proof(
        flow_name=expectation.flow_name,
        flow_spec_id=result.flow_spec_id,
        assembly_result_id=result.assembly_result_id,
        trace_id=trace.trace_id,
        receipt_id=receipt.receipt_id,
        verdict=receipt.verdict,
        loaded_component_count=trace.loaded_component_count,
        loaded_component_set_digest=trace.loaded_component_set_digest,
        source_result_validated=receipt.source_result_validated,
        deterministic=result.deterministic,
        fixture_only=result.fixture_only,
        offline_only=result.offline_only,
        read_only=result.read_only,
        persistent_side_effect_performed=result.persistent_side_effect_performed,
        filesystem_write_performed=result.filesystem_write_performed,
        network_access_performed=result.network_access_performed,
        runtime_memory_write_performed=result.memory_write_performed,
        evidence_mutation_performed=result.evidence_mutation_performed,
        external_resource_used=result.external_resource_used,
        component_invocation_performed=result.component_invocation_performed,
        component_verifier_invocation_performed=(
            result.component_verifier_invocation_performed
        ),
        gp014_imported=result.gp014_imported,
        gp014_called=result.gp014_called,
        delivery_performed=result.delivery_performed,
        tool_routing_performed=result.tool_routing_performed,
        action_performed=result.action_performed,
        runtime_connection_performed=result.runtime_connection_performed,
        exact_identity_match=exact_identity_match,
    )
    return proof


def evaluate_bootstrap_containment(
    *,
    containment_state: BootstrapContainmentState,
) -> BootstrapContainmentEvaluation:
    state_report = validate_bootstrap_containment_state(containment_state)
    if not state_report.ok:
        return _evaluation(
            state=containment_state,
            status=STATUS_HELD_INVALID_STATE,
            reason_code="bootstrap_containment_state_validation_failed",
        )
    if not containment_state.enabled:
        return _evaluation(
            state=containment_state,
            status=STATUS_REFUSED_DISABLED,
            reason_code=REASON_DISABLED,
        )

    assembly_state = build_trace_receipt_assembly_state(
        explicit_offline_developer_enable=True
    )
    proofs = []
    for expectation in FLOW_IDENTITY_EXPECTATIONS:
        result = assemble_trace_receipt(
            expectation.flow_name,
            assembly_state=assembly_state,
        )
        if not validate_trace_receipt_assembly_result(result).ok:
            return _evaluation(
                state=containment_state,
                status=STATUS_HELD_FLOW_MISMATCH,
                reason_code="slice33_result_validation_failed",
                flow_proofs=proofs,
            )
        proof = _proof_from_result(expectation, result)
        if proof is None or not validate_flow_containment_proof(proof).ok:
            return _evaluation(
                state=containment_state,
                status=STATUS_HELD_FLOW_MISMATCH,
                reason_code="slice33_exact_flow_identity_mismatch",
                flow_proofs=proofs,
            )
        proofs.append(proof)

    return _evaluation(
        state=containment_state,
        status=STATUS_COMPLETED,
        reason_code=REASON_COMPLETED,
        flow_proofs=tuple(proofs),
        runtime_containment_passed=True,
    )


def run_default_containment_evaluation() -> BootstrapContainmentEvaluation:
    return evaluate_bootstrap_containment(
        containment_state=build_bootstrap_containment_state()
    )


def run_explicit_offline_containment_evaluation() -> BootstrapContainmentEvaluation:
    return evaluate_bootstrap_containment(
        containment_state=build_bootstrap_containment_state(
            explicit_offline_developer_enable=True
        )
    )
