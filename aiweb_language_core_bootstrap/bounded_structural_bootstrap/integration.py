"""Explicit disabled-by-default Slice 36 structural bootstrap integration.

This module connects the already accepted Slice 36A through Slice 36G records
inside the isolated language-core bootstrap. The path is never entered by raw
text alone. It requires an exact invocation record, an explicit enabled state,
and an exact static synthetic fixture. No approved caller catalog is installed.
"""

from __future__ import annotations

from typing import Final

from ..bootstrap_adapter import (
    build_bootstrap_adapter_state,
)
from ..boundary import build_bootstrap_boundary_bundle
from ..candidate_resonant_phase_trail import (
    PHASE_TRAIL_SCHEMA_VERSION,
    construct_candidate_resonant_phase_trails,
    validate_candidate_resonant_phase_trail_result,
)
from ..deterministic_structural_derivation import (
    STRUCTURAL_DERIVATION_SCHEMA_VERSION,
    derive_deterministic_structural_analysis,
    validate_deterministic_structural_derivation_result,
)
from ..input_event_custody import (
    CUSTODY_SCHEMA_VERSION,
    capture_input_event,
    validate_input_event_capture_result,
)
from ..resonant_operator_candidate_binding import (
    BINDING_SCHEMA_VERSION,
    bind_resonant_operator_candidates,
    validate_resonant_operator_candidate_binding_result,
)
from ..scope_attachment_reference_constraints import (
    SCOPE_CONSTRAINT_SCHEMA_VERSION,
    apply_scope_attachment_reference_constraints,
    build_active_context_registry,
    validate_active_context_registry,
    validate_scope_attachment_reference_constraint_result,
)
from ..schema import SCHEMA_VERSION as BOOTSTRAP_SCHEMA_VERSION
from ..schema import stable_record_id
from ..source_field_projection import (
    PROJECTION_SCHEMA_VERSION,
    project_source_field,
    validate_source_field_projection_result,
)
from ..symbolic_grammar_operator_registry import (
    REGISTRY_SCHEMA_VERSION,
    build_default_symbolic_grammar_operator_registry,
    validate_symbolic_grammar_operator_registry,
)
from ..verify import verify_bootstrap_boundary_bundle
from .fixtures import (
    get_bounded_structural_fixture,
    is_exact_accepted_bounded_structural_fixture,
)
from .schema import (
    PRE_SLICE36_COMMIT,
    PRE_SLICE36_TREE,
    SLICE36_ACCEPTED_CHAIN,
    SLICE36_ACCEPTED_SCOPE,
    SLICE36_DEFERRED_SCOPE,
    SLICE36_INCREMENT_LABELS,
    SLICE36_MATHEMATICAL_DIRECTION,
    SLICE36_PERMANENT_BOUNDARIES,
    SLICE36G_ACCEPTED_HEAD,
    SLICE36G_ACCEPTED_TREE,
    SLICE36H_COMMIT_SUBJECT,
    SLICE36H_SCHEMA_VERSION,
    SLICE36H_SPEC_ID,
    SLICE36H_SPEC_VERSION,
    BootstrapIntegrationStatus,
    BootstrapInvocationKind,
    BootstrapStage,
    BootstrapStageReceipt,
    BootstrapStageStatus,
    BoundedStructuralBootstrapInvocation,
    BoundedStructuralBootstrapResult,
    BoundedStructuralBootstrapState,
    BoundedStructuralFixtureRecord,
    Slice36AcceptanceRecord,
    Slice36RollbackMetadata,
)
from .validation import (
    validate_bootstrap_adapter_for_slice36h,
    validate_bounded_structural_bootstrap_invocation,
    validate_bounded_structural_bootstrap_state,
    validate_bounded_structural_fixture,
)


REQUESTED_OPERATION: Final[str] = "run_bounded_structural_analysis"
REASON_DISABLED: Final[str] = "explicit_offline_slice36_bootstrap_enable_required"
REASON_COMPLETED_CANDIDATES: Final[str] = (
    "exact_slice36_chain_completed_with_candidate_structures"
)
REASON_COMPLETED_NON_PROGRESS: Final[str] = (
    "exact_slice36_chain_completed_with_lawful_non_progress"
)


def _enum_value(value: object) -> str:
    return str(getattr(value, "value", value))


def build_bounded_structural_bootstrap_state(
    *,
    explicit_offline_developer_enable: bool = False,
) -> BoundedStructuralBootstrapState:
    enabled = explicit_offline_developer_enable is True
    body = {
        "enabled": enabled,
        "explicit_offline_developer_enable": enabled,
        "disabled_by_default": True,
        "explicit_invocation_required": True,
        "accepted_fixture_only": True,
        "approved_caller_path_defined": True,
        "approved_caller_catalog_installed": False,
        "offline_only": True,
        "standard_library_only": True,
        "deterministic": True,
        "read_only": True,
        "in_memory_only": True,
        "source_preserving": True,
        "operator_trace_preserving": True,
        "phase_trace_preserving": True,
        "bounded_supported_profile_only": True,
        "non_llm": True,
        "rollback_safe": True,
        "raw_text_alone_allowed": False,
        "arbitrary_input_allowed": False,
        "automatic_activation_allowed": False,
        "hidden_fallback_parser_allowed": False,
        "conventional_nlp_authority_allowed": False,
        "external_linguistic_resource_loading_allowed": False,
        "filesystem_search_allowed": False,
        "filesystem_read_allowed": False,
        "filesystem_write_allowed": False,
        "repository_history_search_allowed": False,
        "network_allowed": False,
        "web_access_allowed": False,
        "environment_lookup_allowed": False,
        "memory_read_allowed": False,
        "memory_write_allowed": False,
        "protected_memory_retrieval_allowed": False,
        "llm_allowed": False,
        "embedding_allowed": False,
        "vector_database_allowed": False,
        "semantic_similarity_allowed": False,
        "learned_parser_allowed": False,
        "neural_classifier_allowed": False,
        "rag_allowed": False,
        "main_connection_allowed": False,
        "api_route_allowed": False,
        "capability_route_allowed": False,
        "tool_activation_allowed": False,
        "action_execution_allowed": False,
        "outward_rendering_allowed": False,
        "evidence_validation_allowed": False,
        "delivery_authorization_allowed": False,
        "candidate_meaning_allowed": False,
        "selected_meaning_allowed": False,
        "concept_resolution_allowed": False,
        "predicate_authority_allowed": False,
        "participant_role_authority_allowed": False,
        "permission_inference_allowed": False,
        "capability_authority_allowed": False,
        "release_authorized": False,
        "production_ready": False,
        "spec_id": SLICE36H_SPEC_ID,
        "spec_version": SLICE36H_SPEC_VERSION,
        "schema_version": SLICE36H_SCHEMA_VERSION,
    }
    return BoundedStructuralBootstrapState(
        state_id=stable_record_id(
            "slice36_bounded_structural_bootstrap_state",
            body,
        ),
        **body,
    )


def build_slice36_rollback_metadata() -> Slice36RollbackMetadata:
    body = {
        "pre_slice36_commit": PRE_SLICE36_COMMIT,
        "pre_slice36_tree": PRE_SLICE36_TREE,
        "accepted_parent_head": SLICE36G_ACCEPTED_HEAD,
        "accepted_parent_tree": SLICE36G_ACCEPTED_TREE,
        "expected_closeout_commit_subject": SLICE36H_COMMIT_SUBJECT,
        "exact_commit_checkout_required": True,
        "exact_tree_match_required": True,
        "separate_recovery_clone_required": True,
        "git_object_verification_required": True,
        "live_repository_mutation_authorized": False,
        "runtime_rollback_execution_authorized": False,
        "rollback_proof_external_to_runtime": True,
        "schema_version": SLICE36H_SCHEMA_VERSION,
    }
    return Slice36RollbackMetadata(
        rollback_id=stable_record_id(
            "slice36_rollback_metadata",
            body,
        ),
        **body,
    )


def build_slice36_acceptance_record(
    *,
    rollback_metadata: Slice36RollbackMetadata | None = None,
) -> Slice36AcceptanceRecord:
    rollback = rollback_metadata or build_slice36_rollback_metadata()
    body = {
        "decision_owner": "Nicholas Jacob Bogaert / AI.Web",
        "accepted_increment_labels": SLICE36_INCREMENT_LABELS,
        "accepted_chain": SLICE36_ACCEPTED_CHAIN,
        "permanent_boundaries": SLICE36_PERMANENT_BOUNDARIES,
        "mathematical_direction": SLICE36_MATHEMATICAL_DIRECTION,
        "accepted_scope": SLICE36_ACCEPTED_SCOPE,
        "deferred_scope": SLICE36_DEFERRED_SCOPE,
        "rollback_metadata_id": rollback.rollback_id,
        "accepted_parent_head": SLICE36G_ACCEPTED_HEAD,
        "accepted_parent_tree": SLICE36G_ACCEPTED_TREE,
        "pre_slice36_commit": PRE_SLICE36_COMMIT,
        "pre_slice36_tree": PRE_SLICE36_TREE,
        "disabled_by_default": True,
        "explicitly_invoked_only": True,
        "offline_only": True,
        "deterministic": True,
        "source_preserving": True,
        "no_public_runtime_authority": True,
        "no_selected_meaning_authority": True,
        "no_action_authority": True,
        "no_delivery_authority": True,
        "runtime_self_grants_acceptance": False,
        "decision_owner_acceptance_required": True,
        "release_authorized": False,
        "production_ready": False,
        "spec_id": SLICE36H_SPEC_ID,
        "spec_version": SLICE36H_SPEC_VERSION,
        "schema_version": SLICE36H_SCHEMA_VERSION,
    }
    return Slice36AcceptanceRecord(
        acceptance_record_id=stable_record_id(
            "slice36_acceptance_record",
            body,
        ),
        **body,
    )


def build_fixture_bootstrap_invocation(
    fixture_name: str,
) -> BoundedStructuralBootstrapInvocation | None:
    fixture = get_bounded_structural_fixture(fixture_name)
    if fixture is None:
        return None
    body = {
        "invocation_kind": BootstrapInvocationKind.SYNTHETIC_FIXTURE,
        "fixture_name": fixture.fixture_name,
        "fixture_id": fixture.fixture_id,
        "approved_caller_id": "",
        "explicit_invocation": True,
        "requested_operation": REQUESTED_OPERATION,
        "raw_text_carried_by_invocation": False,
        "schema_version": SLICE36H_SCHEMA_VERSION,
    }
    return BoundedStructuralBootstrapInvocation(
        invocation_id=stable_record_id(
            "slice36_bounded_structural_bootstrap_invocation",
            body,
        ),
        **body,
    )


def build_uninstalled_approved_caller_invocation(
    *,
    approved_caller_id: str,
) -> BoundedStructuralBootstrapInvocation:
    body = {
        "invocation_kind": BootstrapInvocationKind.APPROVED_CALLER,
        "fixture_name": "",
        "fixture_id": "",
        "approved_caller_id": approved_caller_id,
        "explicit_invocation": True,
        "requested_operation": REQUESTED_OPERATION,
        "raw_text_carried_by_invocation": False,
        "schema_version": SLICE36H_SCHEMA_VERSION,
    }
    return BoundedStructuralBootstrapInvocation(
        invocation_id=stable_record_id(
            "slice36_bounded_structural_bootstrap_invocation",
            body,
        ),
        **body,
    )


def _stage_receipt(
    *,
    state: BoundedStructuralBootstrapState,
    invocation: BoundedStructuralBootstrapInvocation,
    stage_ordinal: int,
    stage: BootstrapStage,
    predecessor_stage: str,
    predecessor_record_id: str,
    predecessor_schema_version: str,
    predecessor_exact_type: str,
    expected_predecessor_schema_version: str,
    supporting_record_ids: tuple[str, ...],
    output_record_id: str,
    output_schema_version: str,
    output_exact_type: str,
    source_event_id: str,
    source_sha256: str,
    candidate_only: bool,
) -> BootstrapStageReceipt:
    body = {
        "invocation_id": invocation.invocation_id,
        "state_id": state.state_id,
        "stage_ordinal": stage_ordinal,
        "stage": stage,
        "stage_status": BootstrapStageStatus.COMPLETED,
        "reason_code": f"{stage.value}_completed_with_exact_predecessor",
        "predecessor_stage": predecessor_stage,
        "predecessor_record_id": predecessor_record_id,
        "predecessor_schema_version": predecessor_schema_version,
        "predecessor_exact_type": predecessor_exact_type,
        "expected_predecessor_schema_version": expected_predecessor_schema_version,
        "predecessor_identity_verified": True,
        "predecessor_version_verified": True,
        "supporting_record_ids": supporting_record_ids,
        "output_record_id": output_record_id,
        "output_schema_version": output_schema_version,
        "output_exact_type": output_exact_type,
        "output_validation_passed": True,
        "stage_completed": True,
        "stage_skipped": False,
        "source_event_id": source_event_id,
        "source_sha256": source_sha256,
        "source_ancestry_preserved": True,
        "candidate_only": candidate_only,
        "interpretation_performed": False,
        "semantic_classification_performed": False,
        "core_rsoc_operator_application_performed": False,
        "selected_meaning_created": False,
        "evidence_validation_performed": False,
        "filesystem_search_performed": False,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "repository_history_search_performed": False,
        "network_access_performed": False,
        "web_access_performed": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "route_registration_performed": False,
        "capability_route_performed": False,
        "tool_activation_performed": False,
        "action_performed": False,
        "outward_rendering_performed": False,
        "delivery_authorized": False,
        "spec_id": SLICE36H_SPEC_ID,
        "spec_version": SLICE36H_SPEC_VERSION,
        "schema_version": SLICE36H_SCHEMA_VERSION,
    }
    return BootstrapStageReceipt(
        receipt_id=stable_record_id(
            "slice36_bounded_structural_stage_receipt",
            body,
        ),
        **body,
    )


def _result(
    *,
    state: BoundedStructuralBootstrapState,
    invocation: object | None,
    status: BootstrapIntegrationStatus,
    reason_code: str,
    fixture: BoundedStructuralFixtureRecord | None = None,
    bootstrap_authority_state_id: str = "",
    bootstrap_boundary_id: str = "",
    component_registry_id: str = "",
    import_policy_id: str = "",
    bootstrap_adapter_state_id: str = "",
    stage_receipts: tuple[BootstrapStageReceipt, ...] = (),
    source_event_id: str = "",
    source_sha256: str = "",
    source_reconstruction_proven: bool = False,
    final_structural_candidate_count: int = 0,
    final_non_progress_reasons: tuple[str, ...] = (),
    custody_result: object | None = None,
    projection_result: object | None = None,
    grammar_registry: object | None = None,
    binding_result: object | None = None,
    phase_trail_result: object | None = None,
    constraint_result: object | None = None,
    structural_result: object | None = None,
) -> BoundedStructuralBootstrapResult:
    rollback = build_slice36_rollback_metadata()
    acceptance = build_slice36_acceptance_record(rollback_metadata=rollback)
    invocation_id = getattr(invocation, "invocation_id", "")
    explicit = bool(
        type(invocation) is BoundedStructuralBootstrapInvocation
        and invocation.explicit_invocation
    )
    completed = status in {
        BootstrapIntegrationStatus.COMPLETED_STRUCTURAL_CANDIDATES,
        BootstrapIntegrationStatus.COMPLETED_LAWFUL_NON_PROGRESS,
    }
    body = {
        "state_id": state.state_id,
        "invocation_id": invocation_id,
        "fixture_id": fixture.fixture_id if fixture is not None else getattr(invocation, "fixture_id", ""),
        "status": status,
        "reason_code": reason_code,
        "bootstrap_schema_version": BOOTSTRAP_SCHEMA_VERSION,
        "bootstrap_authority_state_id": bootstrap_authority_state_id,
        "bootstrap_boundary_id": bootstrap_boundary_id,
        "component_registry_id": component_registry_id,
        "import_policy_id": import_policy_id,
        "bootstrap_adapter_state_id": bootstrap_adapter_state_id,
        "stage_receipts": stage_receipts,
        "stage_receipt_count": len(stage_receipts),
        "completed_stage_count": sum(receipt.stage_completed for receipt in stage_receipts),
        "exact_stage_chain_complete": completed and len(stage_receipts) == 7,
        "no_stage_skipped": completed and all(not receipt.stage_skipped for receipt in stage_receipts),
        "source_event_id": source_event_id,
        "source_sha256": source_sha256,
        "source_reconstruction_proven": source_reconstruction_proven,
        "all_predecessor_records_exact": completed and all(
            receipt.predecessor_identity_verified for receipt in stage_receipts
        ),
        "all_predecessor_versions_exact": completed and all(
            receipt.predecessor_version_verified for receipt in stage_receipts
        ),
        "final_structural_candidate_count": final_structural_candidate_count,
        "final_non_progress_reasons": final_non_progress_reasons,
        "custody_result": custody_result,
        "projection_result": projection_result,
        "grammar_registry": grammar_registry,
        "binding_result": binding_result,
        "phase_trail_result": phase_trail_result,
        "constraint_result": constraint_result,
        "structural_result": structural_result,
        "acceptance_record": acceptance,
        "rollback_metadata": rollback,
        "disabled_by_default": True,
        "explicitly_invoked": explicit,
        "fixture_only": True,
        "offline_only": True,
        "standard_library_only": True,
        "deterministic": True,
        "read_only": True,
        "in_memory_only": True,
        "raw_text_alone_activated": False,
        "hidden_fallback_parser_used": False,
        "conventional_nlp_authority_used": False,
        "external_linguistic_resource_loaded": False,
        "filesystem_search_performed": False,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "repository_history_search_performed": False,
        "network_access_performed": False,
        "web_access_performed": False,
        "environment_lookup_performed": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "protected_memory_retrieval_performed": False,
        "llm_used": False,
        "embedding_used": False,
        "vector_database_used": False,
        "semantic_similarity_used": False,
        "learned_parser_used": False,
        "neural_classifier_used": False,
        "rag_used": False,
        "api_route_activated": False,
        "capability_route_activated": False,
        "tool_activated": False,
        "action_executed": False,
        "outward_rendering_performed": False,
        "evidence_validation_performed": False,
        "candidate_meaning_created": False,
        "selected_meaning_created": False,
        "concept_resolved": False,
        "predicate_identity_created": False,
        "participant_roles_assigned": False,
        "permission_inferred": False,
        "capability_authorized": False,
        "delivery_authorized": False,
        "technical_acceptance_granted_by_runtime": False,
        "release_authorized": False,
        "production_ready": False,
        "spec_id": SLICE36H_SPEC_ID,
        "spec_version": SLICE36H_SPEC_VERSION,
        "schema_version": SLICE36H_SCHEMA_VERSION,
    }
    record = BoundedStructuralBootstrapResult(
        result_id="",
        **body,
    )
    return BoundedStructuralBootstrapResult(
        result_id=record.expected_id(),
        **body,
    )


def _boundary_is_exact_and_inert(bundle: object) -> bool:
    try:
        report = verify_bootstrap_boundary_bundle(bundle)
        authority = bundle.authority
        boundary = bundle.boundary
    except (AttributeError, TypeError):
        return False
    return bool(
        report.ok
        and authority.enabled is False
        and authority.disabled_by_default is True
        and authority.fixture_only is True
        and authority.offline_only is True
        and authority.deterministic is True
        and authority.runtime_connected is False
        and authority.components_loaded is False
        and boundary.component_loading is False
        and boundary.main_connection is False
        and boundary.route_connection is False
        and boundary.ui_connection is False
        and boundary.persistent_side_effect is False
        and boundary.runtime_effect == "none"
        and boundary.dependency_effect == "none"
    )


def run_bounded_structural_bootstrap(
    invocation: object = None,
    *,
    integration_state: object = None,
) -> BoundedStructuralBootstrapResult:
    """Run the exact bounded chain only after explicit fixture authorization."""

    state = (
        integration_state
        if integration_state is not None
        else build_bounded_structural_bootstrap_state()
    )
    if not validate_bounded_structural_bootstrap_state(state).ok:
        if type(state) is not BoundedStructuralBootstrapState:
            state = build_bounded_structural_bootstrap_state()
        return _result(
            state=state,
            invocation=invocation,
            status=BootstrapIntegrationStatus.HELD_INVALID_STATE,
            reason_code="bounded_structural_bootstrap_state_validation_failed",
        )

    if not state.enabled:
        return _result(
            state=state,
            invocation=invocation,
            status=BootstrapIntegrationStatus.REFUSED_DISABLED,
            reason_code=REASON_DISABLED,
        )

    invocation_report = validate_bounded_structural_bootstrap_invocation(invocation)
    if not invocation_report.ok:
        return _result(
            state=state,
            invocation=invocation,
            status=BootstrapIntegrationStatus.HELD_INVALID_INVOCATION,
            reason_code="exact_versioned_invocation_record_required",
        )
    assert type(invocation) is BoundedStructuralBootstrapInvocation

    if invocation.invocation_kind is BootstrapInvocationKind.APPROVED_CALLER:
        return _result(
            state=state,
            invocation=invocation,
            status=(
                BootstrapIntegrationStatus.
                HELD_APPROVED_CALLER_CATALOG_NOT_INSTALLED
            ),
            reason_code="approved_caller_catalog_deferred_not_installed",
        )

    fixture = get_bounded_structural_fixture(invocation.fixture_name)
    if (
        fixture is None
        or fixture.fixture_id != invocation.fixture_id
        or not is_exact_accepted_bounded_structural_fixture(fixture)
        or not validate_bounded_structural_fixture(fixture).ok
    ):
        return _result(
            state=state,
            invocation=invocation,
            status=BootstrapIntegrationStatus.HELD_FIXTURE_NOT_ACCEPTED,
            reason_code="exact_static_synthetic_fixture_required",
        )

    bundle = build_bootstrap_boundary_bundle()
    adapter_state = build_bootstrap_adapter_state(
        explicit_offline_developer_enable=True
    )
    if (
        not _boundary_is_exact_and_inert(bundle)
        or not validate_bootstrap_adapter_for_slice36h(adapter_state).ok
    ):
        return _result(
            state=state,
            invocation=invocation,
            fixture=fixture,
            status=BootstrapIntegrationStatus.HELD_INVALID_BOOTSTRAP_BOUNDARY,
            reason_code="isolated_disabled_bootstrap_boundary_validation_failed",
        )

    boundary_kwargs = {
        "bootstrap_authority_state_id": bundle.authority.authority_state_id,
        "bootstrap_boundary_id": bundle.boundary.bootstrap_boundary_id,
        "component_registry_id": bundle.registry.registry_id,
        "import_policy_id": bundle.import_policy.import_policy_id,
        "bootstrap_adapter_state_id": adapter_state.adapter_state_id,
    }
    receipts: list[BootstrapStageReceipt] = []

    custody = capture_input_event(
        fixture.exact_source_text,
        source_id=fixture.source_id,
        channel_id=fixture.channel_id,
        sequence_number=fixture.sequence_number,
        correlation_id=fixture.correlation_id,
    )
    if (
        not validate_input_event_capture_result(custody).ok
        or custody.event is None
        or _enum_value(custody.status) != fixture.expected_custody_status
    ):
        return _result(
            state=state,
            invocation=invocation,
            fixture=fixture,
            status=BootstrapIntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice36a_custody_output_validation_failed",
            stage_receipts=tuple(receipts),
            custody_result=custody,
            **boundary_kwargs,
        )
    event = custody.event
    receipts.append(
        _stage_receipt(
            state=state,
            invocation=invocation,
            stage_ordinal=1,
            stage=BootstrapStage.INPUT_CUSTODY,
            predecessor_stage="explicit_fixture_invocation",
            predecessor_record_id=invocation.invocation_id,
            predecessor_schema_version=invocation.schema_version,
            predecessor_exact_type=type(invocation).__name__,
            expected_predecessor_schema_version=SLICE36H_SCHEMA_VERSION,
            supporting_record_ids=(fixture.fixture_id,),
            output_record_id=custody.result_id,
            output_schema_version=custody.schema_version,
            output_exact_type=type(custody).__name__,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            candidate_only=False,
        )
    )

    projection = project_source_field(event)
    if (
        not validate_source_field_projection_result(projection).ok
        or projection.projection is None
        or _enum_value(projection.status) != fixture.expected_projection_status
        or projection.source_event_id != event.input_event_id
        or projection.source_sha256 != event.source_sha256
    ):
        return _result(
            state=state,
            invocation=invocation,
            fixture=fixture,
            status=BootstrapIntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice36b_projection_output_validation_failed",
            stage_receipts=tuple(receipts),
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            custody_result=custody,
            projection_result=projection,
            **boundary_kwargs,
        )
    receipts.append(
        _stage_receipt(
            state=state,
            invocation=invocation,
            stage_ordinal=2,
            stage=BootstrapStage.SOURCE_FIELD_PROJECTION,
            predecessor_stage=BootstrapStage.INPUT_CUSTODY.value,
            predecessor_record_id=custody.result_id,
            predecessor_schema_version=custody.schema_version,
            predecessor_exact_type=type(custody).__name__,
            expected_predecessor_schema_version=CUSTODY_SCHEMA_VERSION,
            supporting_record_ids=(event.input_event_id, event.root_source_span_id),
            output_record_id=projection.result_id,
            output_schema_version=projection.schema_version,
            output_exact_type=type(projection).__name__,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            candidate_only=False,
        )
    )

    registry = build_default_symbolic_grammar_operator_registry()
    if not validate_symbolic_grammar_operator_registry(registry).ok:
        return _result(
            state=state,
            invocation=invocation,
            fixture=fixture,
            status=BootstrapIntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice36c_registry_validation_failed",
            stage_receipts=tuple(receipts),
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            custody_result=custody,
            projection_result=projection,
            grammar_registry=registry,
            **boundary_kwargs,
        )
    receipts.append(
        _stage_receipt(
            state=state,
            invocation=invocation,
            stage_ordinal=3,
            stage=BootstrapStage.OPERATOR_REGISTRY,
            predecessor_stage=BootstrapStage.SOURCE_FIELD_PROJECTION.value,
            predecessor_record_id=projection.result_id,
            predecessor_schema_version=projection.schema_version,
            predecessor_exact_type=type(projection).__name__,
            expected_predecessor_schema_version=PROJECTION_SCHEMA_VERSION,
            supporting_record_ids=(projection.projection.projection_id,),
            output_record_id=registry.registry_id,
            output_schema_version=registry.schema_version,
            output_exact_type=type(registry).__name__,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            candidate_only=False,
        )
    )

    binding = bind_resonant_operator_candidates(
        projection,
        registry=registry,
    )
    if (
        not validate_resonant_operator_candidate_binding_result(
            binding,
            projection,
            registry,
        ).ok
        or binding.binding_set is None
        or _enum_value(binding.status) != fixture.expected_binding_status
        or binding.projection_id != projection.projection.projection_id
        or binding.grammar_registry_id != registry.registry_id
    ):
        return _result(
            state=state,
            invocation=invocation,
            fixture=fixture,
            status=BootstrapIntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice36d_binding_output_validation_failed",
            stage_receipts=tuple(receipts),
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            custody_result=custody,
            projection_result=projection,
            grammar_registry=registry,
            binding_result=binding,
            **boundary_kwargs,
        )
    receipts.append(
        _stage_receipt(
            state=state,
            invocation=invocation,
            stage_ordinal=4,
            stage=BootstrapStage.OPERATOR_CANDIDATE_BINDING,
            predecessor_stage=BootstrapStage.OPERATOR_REGISTRY.value,
            predecessor_record_id=registry.registry_id,
            predecessor_schema_version=registry.schema_version,
            predecessor_exact_type=type(registry).__name__,
            expected_predecessor_schema_version=REGISTRY_SCHEMA_VERSION,
            supporting_record_ids=(projection.result_id, projection.projection.projection_id),
            output_record_id=binding.result_id,
            output_schema_version=binding.schema_version,
            output_exact_type=type(binding).__name__,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            candidate_only=True,
        )
    )

    trails = construct_candidate_resonant_phase_trails(
        projection,
        binding,
        registry=registry,
    )
    if (
        not validate_candidate_resonant_phase_trail_result(
            trails,
            projection,
            binding,
            registry,
        ).ok
        or trails.phase_trail_set is None
        or _enum_value(trails.status) != fixture.expected_phase_trail_status
        or trails.binding_set_id != binding.binding_set.binding_set_id
    ):
        return _result(
            state=state,
            invocation=invocation,
            fixture=fixture,
            status=BootstrapIntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice36e_phase_trail_output_validation_failed",
            stage_receipts=tuple(receipts),
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            custody_result=custody,
            projection_result=projection,
            grammar_registry=registry,
            binding_result=binding,
            phase_trail_result=trails,
            **boundary_kwargs,
        )
    receipts.append(
        _stage_receipt(
            state=state,
            invocation=invocation,
            stage_ordinal=5,
            stage=BootstrapStage.PHASE_TRAIL_CONSTRUCTION,
            predecessor_stage=BootstrapStage.OPERATOR_CANDIDATE_BINDING.value,
            predecessor_record_id=binding.result_id,
            predecessor_schema_version=binding.schema_version,
            predecessor_exact_type=type(binding).__name__,
            expected_predecessor_schema_version=BINDING_SCHEMA_VERSION,
            supporting_record_ids=(
                binding.binding_set.binding_set_id,
                registry.registry_id,
                projection.result_id,
            ),
            output_record_id=trails.result_id,
            output_schema_version=trails.schema_version,
            output_exact_type=type(trails).__name__,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            candidate_only=True,
        )
    )

    active_context = build_active_context_registry()
    if not validate_active_context_registry(active_context).ok:
        return _result(
            state=state,
            invocation=invocation,
            fixture=fixture,
            status=BootstrapIntegrationStatus.HELD_STAGE_PREDECESSOR,
            reason_code="slice36f_explicit_empty_context_registry_validation_failed",
            stage_receipts=tuple(receipts),
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            custody_result=custody,
            projection_result=projection,
            grammar_registry=registry,
            binding_result=binding,
            phase_trail_result=trails,
            **boundary_kwargs,
        )
    constraints = apply_scope_attachment_reference_constraints(
        projection,
        binding,
        trails,
        active_context_registry=active_context,
        requested_context_dependencies=fixture.requested_context_dependencies,
    )
    if (
        not validate_scope_attachment_reference_constraint_result(
            constraints,
            projection,
            binding,
            trails,
        ).ok
        or constraints.constraint_set is None
        or _enum_value(constraints.status) != fixture.expected_constraint_status
        or constraints.phase_trail_set_id != trails.phase_trail_set.phase_trail_set_id
    ):
        return _result(
            state=state,
            invocation=invocation,
            fixture=fixture,
            status=BootstrapIntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice36f_constraint_output_validation_failed",
            stage_receipts=tuple(receipts),
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            custody_result=custody,
            projection_result=projection,
            grammar_registry=registry,
            binding_result=binding,
            phase_trail_result=trails,
            constraint_result=constraints,
            **boundary_kwargs,
        )
    receipts.append(
        _stage_receipt(
            state=state,
            invocation=invocation,
            stage_ordinal=6,
            stage=BootstrapStage.SCOPE_REFERENCE_CONSTRAINTS,
            predecessor_stage=BootstrapStage.PHASE_TRAIL_CONSTRUCTION.value,
            predecessor_record_id=trails.result_id,
            predecessor_schema_version=trails.schema_version,
            predecessor_exact_type=type(trails).__name__,
            expected_predecessor_schema_version=PHASE_TRAIL_SCHEMA_VERSION,
            supporting_record_ids=(
                trails.phase_trail_set.phase_trail_set_id,
                active_context.registry_id,
                binding.result_id,
                projection.result_id,
            ),
            output_record_id=constraints.result_id,
            output_schema_version=constraints.schema_version,
            output_exact_type=type(constraints).__name__,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            candidate_only=True,
        )
    )

    structural = derive_deterministic_structural_analysis(
        custody,
        projection,
        binding,
        trails,
        constraints,
    )
    structural_report = validate_deterministic_structural_derivation_result(
        structural,
        custody,
        projection,
        binding,
        trails,
        constraints,
    )
    if (
        not structural_report.ok
        or structural.structural_set is None
        or _enum_value(structural.status) != fixture.expected_structural_status
        or structural.constraint_set_id != constraints.constraint_set.constraint_set_id
    ):
        return _result(
            state=state,
            invocation=invocation,
            fixture=fixture,
            status=BootstrapIntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice36g_structural_output_validation_failed",
            stage_receipts=tuple(receipts),
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            custody_result=custody,
            projection_result=projection,
            grammar_registry=registry,
            binding_result=binding,
            phase_trail_result=trails,
            constraint_result=constraints,
            structural_result=structural,
            **boundary_kwargs,
        )
    structural_set = structural.structural_set
    non_progress_reasons = tuple(
        reason.value for reason in structural_set.aggregate_non_progress_reasons
    )
    if (
        structural_set.candidate_count != fixture.expected_structural_candidate_count
        or non_progress_reasons != fixture.expected_non_progress_reasons
        or not structural_set.all_source_ancestry_preserved
        or not structural_set.all_source_reconstruction_proven
        or not structural_set.all_phase_trails_preserved
        or structural_set.selected_structural_candidate_id is not None
        or structural_set.candidate_meaning_created
        or structural_set.selected_meaning
        or structural_set.clarification_question_asked
        or structural_set.semantic_rejection_performed
    ):
        return _result(
            state=state,
            invocation=invocation,
            fixture=fixture,
            status=BootstrapIntegrationStatus.HELD_EXPECTATION_MISMATCH,
            reason_code="exact_static_fixture_structural_expectation_mismatch",
            stage_receipts=tuple(receipts),
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            source_reconstruction_proven=structural_set.all_source_reconstruction_proven,
            final_structural_candidate_count=structural_set.candidate_count,
            final_non_progress_reasons=non_progress_reasons,
            custody_result=custody,
            projection_result=projection,
            grammar_registry=registry,
            binding_result=binding,
            phase_trail_result=trails,
            constraint_result=constraints,
            structural_result=structural,
            **boundary_kwargs,
        )
    receipts.append(
        _stage_receipt(
            state=state,
            invocation=invocation,
            stage_ordinal=7,
            stage=BootstrapStage.STRUCTURAL_DERIVATION,
            predecessor_stage=BootstrapStage.SCOPE_REFERENCE_CONSTRAINTS.value,
            predecessor_record_id=constraints.result_id,
            predecessor_schema_version=constraints.schema_version,
            predecessor_exact_type=type(constraints).__name__,
            expected_predecessor_schema_version=SCOPE_CONSTRAINT_SCHEMA_VERSION,
            supporting_record_ids=(
                constraints.constraint_set.constraint_set_id,
                trails.result_id,
                binding.result_id,
                projection.result_id,
                custody.result_id,
            ),
            output_record_id=structural.result_id,
            output_schema_version=structural.schema_version,
            output_exact_type=type(structural).__name__,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            candidate_only=True,
        )
    )

    status = (
        BootstrapIntegrationStatus.COMPLETED_LAWFUL_NON_PROGRESS
        if structural_set.candidate_count == 0
        else BootstrapIntegrationStatus.COMPLETED_STRUCTURAL_CANDIDATES
    )
    reason = (
        REASON_COMPLETED_NON_PROGRESS
        if status is BootstrapIntegrationStatus.COMPLETED_LAWFUL_NON_PROGRESS
        else REASON_COMPLETED_CANDIDATES
    )
    return _result(
        state=state,
        invocation=invocation,
        fixture=fixture,
        status=status,
        reason_code=reason,
        stage_receipts=tuple(receipts),
        source_event_id=event.input_event_id,
        source_sha256=event.source_sha256,
        source_reconstruction_proven=structural_set.all_source_reconstruction_proven,
        final_structural_candidate_count=structural_set.candidate_count,
        final_non_progress_reasons=non_progress_reasons,
        custody_result=custody,
        projection_result=projection,
        grammar_registry=registry,
        binding_result=binding,
        phase_trail_result=trails,
        constraint_result=constraints,
        structural_result=structural,
        **boundary_kwargs,
    )


__all__ = (
    "REASON_COMPLETED_CANDIDATES",
    "REASON_COMPLETED_NON_PROGRESS",
    "REASON_DISABLED",
    "REQUESTED_OPERATION",
    "build_bounded_structural_bootstrap_state",
    "build_fixture_bootstrap_invocation",
    "build_slice36_acceptance_record",
    "build_slice36_rollback_metadata",
    "build_uninstalled_approved_caller_invocation",
    "run_bounded_structural_bootstrap",
)
