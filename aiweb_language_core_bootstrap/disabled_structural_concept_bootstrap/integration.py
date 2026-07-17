"""Explicit disabled Slice 37G structural-to-concept bootstrap integration."""

from __future__ import annotations

from typing import Final

from ..bootstrap_adapter import (
    build_bootstrap_adapter_state,
    validate_bootstrap_adapter_state,
)
from ..boundary import build_bootstrap_boundary_bundle
from ..candidate_resonant_phase_trail import (
    construct_candidate_resonant_phase_trails,
    validate_candidate_resonant_phase_trail_result,
)
from ..deterministic_structural_derivation import (
    derive_deterministic_structural_analysis,
    validate_deterministic_structural_derivation_result,
)
from ..input_event_custody import (
    capture_input_event,
    validate_input_event_capture_result,
)
from ..resonant_operator_candidate_binding import (
    bind_resonant_operator_candidates,
    validate_resonant_operator_candidate_binding_result,
)
from ..scope_attachment_reference_constraints import (
    apply_scope_attachment_reference_constraints,
    validate_scope_attachment_reference_constraint_result,
)
from ..source_field_projection import (
    project_source_field,
    validate_source_field_projection_result,
)
from ..structural_concept_candidate_proposal import (
    ProposalResultStatus,
    build_default_structural_concept_proposal_profile,
    propose_structural_concept_candidates,
    validate_proposal_profile,
    validate_proposal_result,
)
from ..symbolic_grammar_operator_registry import (
    build_default_symbolic_grammar_operator_registry,
    validate_symbolic_grammar_operator_registry,
)
from ..verify import verify_bootstrap_boundary_bundle
from .fixtures import (
    get_disabled_structural_concept_fixture,
    is_exact_accepted_fixture,
)
from .schema import (
    PRE_SLICE37_COMMIT,
    PRE_SLICE37_TREE,
    SLICE37_ACCEPTED_CHAIN,
    SLICE37_ACCEPTED_SCOPE,
    SLICE37_DEFERRED_SCOPE,
    SLICE37_INCREMENT_LABELS,
    SLICE37_PERMANENT_BOUNDARIES,
    SLICE37F_ACCEPTED_HEAD,
    SLICE37F_ACCEPTED_TREE,
    SLICE37G_COMMIT_SUBJECT,
    DisabledStructuralConceptBootstrapResult,
    DisabledStructuralConceptBootstrapState,
    DisabledStructuralConceptFixture,
    DisabledStructuralConceptInvocation,
    IntegrationStage,
    IntegrationStageReceipt,
    IntegrationStatus,
    Slice37AcceptanceRecord,
    Slice37RollbackMetadata,
)
from .validation import (
    validate_acceptance_record,
    validate_fixture,
    validate_integration_state,
    validate_invocation,
    validate_rollback_metadata,
)


REQUESTED_OPERATION: Final[str] = (
    "run_disabled_structural_concept_candidate_proposal"
)
REASON_DISABLED: Final[str] = (
    "explicit_offline_slice37g_bootstrap_enable_required"
)


def build_disabled_structural_concept_bootstrap_state(
    *,
    explicit_offline_developer_enable: bool = False,
) -> DisabledStructuralConceptBootstrapState:
    enabled = explicit_offline_developer_enable is True
    body = {
        "enabled": enabled,
        "explicit_offline_developer_enable": enabled,
        "disabled_by_default": True,
        "explicit_invocation_required": True,
        "accepted_static_fixture_only": True,
        "offline_only": True,
        "standard_library_only": True,
        "deterministic": True,
        "read_only": True,
        "in_memory_only": True,
        "exact_profile_bounded": True,
        "source_preserving": True,
        "structural_ancestry_preserving": True,
        "registry_snapshot_preserving": True,
        "zero_one_many_preserving": True,
        "explicit_unknown_preserving": True,
        "explicit_unsupported_preserving": True,
        "rollback_safe": True,
        "automatic_activation_allowed": False,
        "arbitrary_text_invocation_allowed": False,
        "conventional_word_token_authority_allowed": False,
        "normalization_allowed": False,
        "semantic_similarity_allowed": False,
        "learned_model_allowed": False,
        "external_resource_loading_allowed": False,
        "filesystem_read_allowed": False,
        "filesystem_write_allowed": False,
        "network_allowed": False,
        "memory_read_allowed": False,
        "memory_write_allowed": False,
        "api_route_allowed": False,
        "capability_route_allowed": False,
        "tool_invocation_allowed": False,
        "action_allowed": False,
        "rendering_allowed": False,
        "delivery_allowed": False,
        "candidate_meaning_allowed": False,
        "selected_meaning_allowed": False,
        "selected_sense_allowed": False,
        "predicate_identity_allowed": False,
        "participant_role_allowed": False,
        "truth_allowed": False,
        "evidence_validity_allowed": False,
        "clarification_allowed": False,
        "permission_allowed": False,
        "runtime_self_acceptance_allowed": False,
        "release_authorized": False,
        "production_ready": False,
    }
    record = DisabledStructuralConceptBootstrapState(
        state_id="",
        **body,
    )
    return DisabledStructuralConceptBootstrapState(
        state_id=record.expected_id(),
        **body,
    )


def build_slice37_rollback_metadata() -> Slice37RollbackMetadata:
    body = {
        "pre_slice37_commit": PRE_SLICE37_COMMIT,
        "pre_slice37_tree": PRE_SLICE37_TREE,
        "accepted_parent_head": SLICE37F_ACCEPTED_HEAD,
        "accepted_parent_tree": SLICE37F_ACCEPTED_TREE,
        "expected_closeout_commit_subject": SLICE37G_COMMIT_SUBJECT,
        "exact_commit_checkout_required": True,
        "exact_tree_match_required": True,
        "separate_recovery_clone_required": True,
        "git_object_verification_required": True,
        "live_repository_mutation_authorized": False,
        "runtime_rollback_execution_authorized": False,
        "rollback_proof_external_to_runtime": True,
    }
    record = Slice37RollbackMetadata(
        rollback_id="",
        **body,
    )
    return Slice37RollbackMetadata(
        rollback_id=record.expected_id(),
        **body,
    )


def build_slice37_acceptance_record(
    *,
    rollback_metadata: Slice37RollbackMetadata | None = None,
) -> Slice37AcceptanceRecord:
    rollback = rollback_metadata or build_slice37_rollback_metadata()
    body = {
        "decision_owner": "Nicholas Jacob Bogaert / AI.Web",
        "accepted_increment_labels": SLICE37_INCREMENT_LABELS,
        "accepted_chain": SLICE37_ACCEPTED_CHAIN,
        "permanent_boundaries": SLICE37_PERMANENT_BOUNDARIES,
        "accepted_scope": SLICE37_ACCEPTED_SCOPE,
        "deferred_scope": SLICE37_DEFERRED_SCOPE,
        "rollback_metadata_id": rollback.rollback_id,
        "accepted_parent_head": SLICE37F_ACCEPTED_HEAD,
        "accepted_parent_tree": SLICE37F_ACCEPTED_TREE,
        "pre_slice37_commit": PRE_SLICE37_COMMIT,
        "pre_slice37_tree": PRE_SLICE37_TREE,
        "disabled_by_default": True,
        "explicitly_invoked_only": True,
        "offline_only": True,
        "deterministic": True,
        "read_only": True,
        "exact_profile_bounded": True,
        "source_preserving": True,
        "no_public_runtime_authority": True,
        "no_selected_meaning_authority": True,
        "no_action_authority": True,
        "no_memory_authority": True,
        "no_route_authority": True,
        "no_delivery_authority": True,
        "runtime_self_grants_acceptance": False,
        "decision_owner_acceptance_required": True,
        "release_authorized": False,
        "production_ready": False,
    }
    record = Slice37AcceptanceRecord(
        acceptance_record_id="",
        **body,
    )
    return Slice37AcceptanceRecord(
        acceptance_record_id=record.expected_id(),
        **body,
    )


def build_fixture_invocation(
    fixture_name: str,
) -> DisabledStructuralConceptInvocation | None:
    fixture = get_disabled_structural_concept_fixture(fixture_name)
    if fixture is None:
        return None
    profile = build_default_structural_concept_proposal_profile()
    body = {
        "fixture_name": fixture.fixture_name,
        "fixture_id": fixture.fixture_id,
        "profile_id": profile.profile_id,
        "explicit_invocation": True,
        "requested_operation": REQUESTED_OPERATION,
        "raw_text_carried_by_invocation": False,
    }
    record = DisabledStructuralConceptInvocation(
        invocation_id="",
        **body,
    )
    return DisabledStructuralConceptInvocation(
        invocation_id=record.expected_id(),
        **body,
    )


def _boundary_is_exact_and_inert(
    bundle: object,
    adapter_state: object,
) -> bool:
    try:
        report = verify_bootstrap_boundary_bundle(bundle)
        authority = bundle.authority
        boundary = bundle.boundary
    except (AttributeError, TypeError):
        return False
    return bool(
        report.ok
        and validate_bootstrap_adapter_state(adapter_state).ok
        and adapter_state.enabled is True
        and adapter_state.explicit_offline_developer_enable is True
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


def _receipt(
    *,
    state: DisabledStructuralConceptBootstrapState,
    invocation: DisabledStructuralConceptInvocation,
    fixture: DisabledStructuralConceptFixture,
    stage_ordinal: int,
    stage: IntegrationStage,
    predecessor_record_ids: tuple[str, ...],
    output: object,
    output_record_id: str,
    output_schema_version: str,
    source_event_id: str,
    source_sha256: str,
    candidate_only: bool,
) -> IntegrationStageReceipt:
    body = {
        "state_id": state.state_id,
        "invocation_id": invocation.invocation_id,
        "fixture_id": fixture.fixture_id,
        "stage_ordinal": stage_ordinal,
        "stage": stage,
        "predecessor_record_ids": predecessor_record_ids,
        "output_record_id": output_record_id,
        "output_schema_version": output_schema_version,
        "output_exact_type": type(output).__name__,
        "output_validation_passed": True,
        "source_event_id": source_event_id,
        "source_sha256": source_sha256,
        "source_ancestry_preserved": True,
        "candidate_only": candidate_only,
        "selected_meaning_created": False,
        "truth_determined": False,
        "permission_inferred": False,
        "memory_accessed": False,
        "route_created": False,
        "tool_invoked": False,
        "action_performed": False,
        "rendered": False,
        "delivered": False,
    }
    record = IntegrationStageReceipt(
        receipt_id="",
        **body,
    )
    return IntegrationStageReceipt(
        receipt_id=record.expected_id(),
        **body,
    )


def _status_for_proposal(status: ProposalResultStatus) -> IntegrationStatus:
    if status is ProposalResultStatus.CANDIDATES_PROPOSED:
        return IntegrationStatus.COMPLETED_CANDIDATES
    if status is ProposalResultStatus.CANDIDATES_WITH_UNRESOLVED_STATES:
        return IntegrationStatus.COMPLETED_UNRESOLVED
    if status is ProposalResultStatus.EXPLICIT_UNKNOWN:
        return IntegrationStatus.COMPLETED_EXPLICIT_UNKNOWN
    if status is ProposalResultStatus.EXPLICIT_UNSUPPORTED:
        return IntegrationStatus.COMPLETED_EXPLICIT_UNSUPPORTED
    if status is ProposalResultStatus.EXPLICIT_UNKNOWN_AND_UNSUPPORTED:
        return IntegrationStatus.COMPLETED_UNRESOLVED
    return IntegrationStatus.HELD_STAGE_OUTPUT


def _result(
    *,
    state: DisabledStructuralConceptBootstrapState,
    profile: object,
    invocation: object = None,
    fixture: object = None,
    status: IntegrationStatus,
    reason_code: str,
    bundle: object = None,
    adapter_state: object = None,
    stage_receipts: tuple[IntegrationStageReceipt, ...] = (),
    custody_result: object = None,
    projection_result: object = None,
    grammar_registry: object = None,
    binding_result: object = None,
    phase_trail_result: object = None,
    constraint_result: object = None,
    structural_result: object = None,
    proposal_result: object = None,
) -> DisabledStructuralConceptBootstrapResult:
    rollback = build_slice37_rollback_metadata()
    acceptance = build_slice37_acceptance_record(
        rollback_metadata=rollback,
    )
    proposal = proposal_result if hasattr(proposal_result, "result_id") else None
    body = {
        "state_id": state.state_id,
        "invocation_id": getattr(invocation, "invocation_id", ""),
        "fixture_id": getattr(fixture, "fixture_id", ""),
        "status": status,
        "reason_code": reason_code,
        "bootstrap_authority_state_id": getattr(
            getattr(bundle, "authority", None),
            "authority_state_id",
            "",
        ),
        "bootstrap_boundary_id": getattr(
            getattr(bundle, "boundary", None),
            "bootstrap_boundary_id",
            "",
        ),
        "bootstrap_adapter_state_id": getattr(
            adapter_state,
            "adapter_state_id",
            "",
        ),
        "proposal_profile_id": getattr(profile, "profile_id", ""),
        "registry_snapshot_id": getattr(
            getattr(proposal, "registry_snapshot", None),
            "snapshot_id",
            "",
        ),
        "stage_receipts": stage_receipts,
        "stage_receipt_count": len(stage_receipts),
        "exact_stage_chain_complete": len(stage_receipts) == 8,
        "source_event_id": getattr(
            getattr(custody_result, "event", None),
            "input_event_id",
            "",
        ),
        "source_sha256": getattr(
            getattr(custody_result, "event", None),
            "source_sha256",
            "",
        ),
        "custody_result": custody_result,
        "projection_result": projection_result,
        "grammar_registry": grammar_registry,
        "binding_result": binding_result,
        "phase_trail_result": phase_trail_result,
        "constraint_result": constraint_result,
        "structural_result": structural_result,
        "proposal_result": proposal,
        "profile": profile,
        "acceptance_record": acceptance,
        "rollback_metadata": rollback,
        "lexical_occurrence_count": getattr(proposal, "lexical_occurrence_count", 0),
        "concept_candidate_count": getattr(proposal, "concept_candidate_count", 0),
        "sense_candidate_count": getattr(proposal, "sense_candidate_count", 0),
        "explicit_unknown_count": getattr(proposal, "explicit_unknown_count", 0),
        "explicit_unsupported_count": getattr(
            proposal,
            "explicit_unsupported_count",
            0,
        ),
        "disabled_by_default": True,
        "explicitly_invoked": getattr(invocation, "explicit_invocation", False),
        "offline_only": True,
        "standard_library_only": True,
        "deterministic": True,
        "read_only": True,
        "in_memory_only": True,
        "exact_profile_bounded": True,
        "source_preserved": True,
        "structural_ancestry_preserved": True,
        "registry_snapshot_preserved": proposal is not None,
        "zero_one_many_preserved": proposal is not None,
        "candidate_meaning_created": False,
        "selected_meaning_created": False,
        "selected_sense_created": False,
        "predicate_identity_created": False,
        "participant_roles_assigned": False,
        "truth_determined": False,
        "evidence_validity_determined": False,
        "clarification_asked": False,
        "permission_inferred": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "api_route_created": False,
        "capability_route_created": False,
        "tool_invoked": False,
        "action_performed": False,
        "outward_rendered": False,
        "delivered": False,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "network_access_performed": False,
        "external_resource_loaded": False,
        "language_model_used": False,
        "embedding_used": False,
        "semantic_similarity_used": False,
        "technical_acceptance_granted_by_runtime": False,
        "release_authorized": False,
        "production_ready": False,
    }
    record = DisabledStructuralConceptBootstrapResult(
        result_id="",
        **body,
    )
    return DisabledStructuralConceptBootstrapResult(
        result_id=record.expected_id(),
        **body,
    )


def run_disabled_structural_concept_bootstrap(
    invocation: object = None,
    *,
    integration_state: object = None,
    profile: object = None,
) -> DisabledStructuralConceptBootstrapResult:
    """Run the exact accepted fixture chain only after explicit enablement."""

    state = (
        integration_state
        if integration_state is not None
        else build_disabled_structural_concept_bootstrap_state()
    )
    default_profile = build_default_structural_concept_proposal_profile()
    active_profile = profile if profile is not None else default_profile

    if not validate_integration_state(state).ok:
        safe_state = (
            state
            if type(state) is DisabledStructuralConceptBootstrapState
            else build_disabled_structural_concept_bootstrap_state()
        )
        return _result(
            state=safe_state,
            profile=default_profile,
            invocation=invocation,
            status=IntegrationStatus.HELD_INVALID_STATE,
            reason_code="exact_slice37g_integration_state_required",
        )
    assert type(state) is DisabledStructuralConceptBootstrapState

    if not state.enabled:
        return _result(
            state=state,
            profile=default_profile,
            invocation=invocation,
            status=IntegrationStatus.REFUSED_DISABLED,
            reason_code=REASON_DISABLED,
        )

    if not validate_invocation(invocation).ok:
        return _result(
            state=state,
            profile=default_profile,
            invocation=invocation,
            status=IntegrationStatus.HELD_INVALID_INVOCATION,
            reason_code="exact_versioned_fixture_invocation_required",
        )
    assert type(invocation) is DisabledStructuralConceptInvocation

    fixture = get_disabled_structural_concept_fixture(invocation.fixture_name)
    if (
        fixture is None
        or fixture.fixture_id != invocation.fixture_id
        or not is_exact_accepted_fixture(fixture)
        or not validate_fixture(fixture).ok
    ):
        return _result(
            state=state,
            profile=default_profile,
            invocation=invocation,
            fixture=fixture,
            status=IntegrationStatus.HELD_FIXTURE_NOT_ACCEPTED,
            reason_code="exact_static_slice37g_fixture_required",
        )

    if (
        type(active_profile) is not type(default_profile)
        or active_profile != default_profile
        or invocation.profile_id != default_profile.profile_id
        or not validate_proposal_profile(active_profile).ok
    ):
        return _result(
            state=state,
            profile=default_profile,
            invocation=invocation,
            fixture=fixture,
            status=IntegrationStatus.HELD_INVALID_PROFILE,
            reason_code="exact_slice37f_default_profile_required",
        )

    bundle = build_bootstrap_boundary_bundle()
    adapter_state = build_bootstrap_adapter_state(
        explicit_offline_developer_enable=True
    )
    if not _boundary_is_exact_and_inert(bundle, adapter_state):
        return _result(
            state=state,
            profile=active_profile,
            invocation=invocation,
            fixture=fixture,
            status=IntegrationStatus.HELD_INVALID_BOOTSTRAP_BOUNDARY,
            reason_code="isolated_bootstrap_boundary_validation_failed",
            bundle=bundle,
            adapter_state=adapter_state,
        )

    receipts: list[IntegrationStageReceipt] = []

    custody = capture_input_event(
        fixture.exact_source_text,
        source_id=fixture.source_id,
        channel_id=fixture.channel_id,
        sequence_number=fixture.sequence_number,
        correlation_id=f"slice37g-{fixture.sequence_number:03d}",
    )
    if (
        not validate_input_event_capture_result(custody).ok
        or custody.event is None
    ):
        return _result(
            state=state,
            profile=active_profile,
            invocation=invocation,
            fixture=fixture,
            status=IntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice36a_custody_output_invalid",
            bundle=bundle,
            adapter_state=adapter_state,
            custody_result=custody,
        )
    event = custody.event
    receipts.append(
        _receipt(
            state=state,
            invocation=invocation,
            fixture=fixture,
            stage_ordinal=1,
            stage=IntegrationStage.INPUT_CUSTODY,
            predecessor_record_ids=(invocation.invocation_id,),
            output=custody,
            output_record_id=custody.result_id,
            output_schema_version=custody.schema_version,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            candidate_only=False,
        )
    )

    projection = project_source_field(event)
    if (
        not validate_source_field_projection_result(projection).ok
        or projection.projection is None
    ):
        return _result(
            state=state,
            profile=active_profile,
            invocation=invocation,
            fixture=fixture,
            status=IntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice36b_projection_output_invalid",
            bundle=bundle,
            adapter_state=adapter_state,
            stage_receipts=tuple(receipts),
            custody_result=custody,
            projection_result=projection,
        )
    receipts.append(
        _receipt(
            state=state,
            invocation=invocation,
            fixture=fixture,
            stage_ordinal=2,
            stage=IntegrationStage.SOURCE_FIELD_PROJECTION,
            predecessor_record_ids=(custody.result_id,),
            output=projection,
            output_record_id=projection.result_id,
            output_schema_version=projection.schema_version,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            candidate_only=False,
        )
    )

    registry = build_default_symbolic_grammar_operator_registry()
    if not validate_symbolic_grammar_operator_registry(registry).ok:
        return _result(
            state=state,
            profile=active_profile,
            invocation=invocation,
            fixture=fixture,
            status=IntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice36c_operator_registry_invalid",
            bundle=bundle,
            adapter_state=adapter_state,
            stage_receipts=tuple(receipts),
            custody_result=custody,
            projection_result=projection,
            grammar_registry=registry,
        )
    receipts.append(
        _receipt(
            state=state,
            invocation=invocation,
            fixture=fixture,
            stage_ordinal=3,
            stage=IntegrationStage.OPERATOR_REGISTRY,
            predecessor_record_ids=(projection.result_id,),
            output=registry,
            output_record_id=registry.registry_id,
            output_schema_version=registry.schema_version,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            candidate_only=False,
        )
    )

    binding = bind_resonant_operator_candidates(
        projection,
        registry=registry,
    )
    if not validate_resonant_operator_candidate_binding_result(
        binding,
        projection,
        registry,
    ).ok:
        return _result(
            state=state,
            profile=active_profile,
            invocation=invocation,
            fixture=fixture,
            status=IntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice36d_binding_output_invalid",
            bundle=bundle,
            adapter_state=adapter_state,
            stage_receipts=tuple(receipts),
            custody_result=custody,
            projection_result=projection,
            grammar_registry=registry,
            binding_result=binding,
        )
    receipts.append(
        _receipt(
            state=state,
            invocation=invocation,
            fixture=fixture,
            stage_ordinal=4,
            stage=IntegrationStage.OPERATOR_CANDIDATE_BINDING,
            predecessor_record_ids=(projection.result_id, registry.registry_id),
            output=binding,
            output_record_id=binding.result_id,
            output_schema_version=binding.schema_version,
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
    if not validate_candidate_resonant_phase_trail_result(
        trails,
        projection,
        binding,
        registry,
    ).ok:
        return _result(
            state=state,
            profile=active_profile,
            invocation=invocation,
            fixture=fixture,
            status=IntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice36e_phase_trail_output_invalid",
            bundle=bundle,
            adapter_state=adapter_state,
            stage_receipts=tuple(receipts),
            custody_result=custody,
            projection_result=projection,
            grammar_registry=registry,
            binding_result=binding,
            phase_trail_result=trails,
        )
    receipts.append(
        _receipt(
            state=state,
            invocation=invocation,
            fixture=fixture,
            stage_ordinal=5,
            stage=IntegrationStage.PHASE_TRAIL_CONSTRUCTION,
            predecessor_record_ids=(binding.result_id, registry.registry_id),
            output=trails,
            output_record_id=trails.result_id,
            output_schema_version=trails.schema_version,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            candidate_only=True,
        )
    )

    constraints = apply_scope_attachment_reference_constraints(
        projection,
        binding,
        trails,
    )
    if not validate_scope_attachment_reference_constraint_result(
        constraints,
        projection,
        binding,
        trails,
    ).ok:
        return _result(
            state=state,
            profile=active_profile,
            invocation=invocation,
            fixture=fixture,
            status=IntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice36f_constraint_output_invalid",
            bundle=bundle,
            adapter_state=adapter_state,
            stage_receipts=tuple(receipts),
            custody_result=custody,
            projection_result=projection,
            grammar_registry=registry,
            binding_result=binding,
            phase_trail_result=trails,
            constraint_result=constraints,
        )
    receipts.append(
        _receipt(
            state=state,
            invocation=invocation,
            fixture=fixture,
            stage_ordinal=6,
            stage=IntegrationStage.SCOPE_REFERENCE_CONSTRAINTS,
            predecessor_record_ids=(projection.result_id, binding.result_id, trails.result_id),
            output=constraints,
            output_record_id=constraints.result_id,
            output_schema_version=constraints.schema_version,
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
    if not validate_deterministic_structural_derivation_result(
        structural,
        custody,
        projection,
        binding,
        trails,
        constraints,
    ).ok:
        return _result(
            state=state,
            profile=active_profile,
            invocation=invocation,
            fixture=fixture,
            status=IntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice36g_structural_output_invalid",
            bundle=bundle,
            adapter_state=adapter_state,
            stage_receipts=tuple(receipts),
            custody_result=custody,
            projection_result=projection,
            grammar_registry=registry,
            binding_result=binding,
            phase_trail_result=trails,
            constraint_result=constraints,
            structural_result=structural,
        )
    receipts.append(
        _receipt(
            state=state,
            invocation=invocation,
            fixture=fixture,
            stage_ordinal=7,
            stage=IntegrationStage.STRUCTURAL_DERIVATION,
            predecessor_record_ids=(
                custody.result_id,
                projection.result_id,
                binding.result_id,
                trails.result_id,
                constraints.result_id,
            ),
            output=structural,
            output_record_id=structural.result_id,
            output_schema_version=structural.schema_version,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            candidate_only=True,
        )
    )

    proposal = propose_structural_concept_candidates(
        custody,
        projection,
        structural,
        profile=active_profile,
    )
    if not validate_proposal_result(proposal).ok:
        return _result(
            state=state,
            profile=active_profile,
            invocation=invocation,
            fixture=fixture,
            status=IntegrationStatus.HELD_STAGE_OUTPUT,
            reason_code="slice37f_proposal_output_invalid",
            bundle=bundle,
            adapter_state=adapter_state,
            stage_receipts=tuple(receipts),
            custody_result=custody,
            projection_result=projection,
            grammar_registry=registry,
            binding_result=binding,
            phase_trail_result=trails,
            constraint_result=constraints,
            structural_result=structural,
            proposal_result=proposal,
        )
    receipts.append(
        _receipt(
            state=state,
            invocation=invocation,
            fixture=fixture,
            stage_ordinal=8,
            stage=IntegrationStage.CONCEPT_SENSE_PROPOSAL,
            predecessor_record_ids=(
                structural.result_id,
                active_profile.profile_id,
                proposal.registry_snapshot.snapshot_id,
            ),
            output=proposal,
            output_record_id=proposal.result_id,
            output_schema_version=proposal.schema_version,
            source_event_id=event.input_event_id,
            source_sha256=event.source_sha256,
            candidate_only=True,
        )
    )

    actual = (
        proposal.status.value,
        proposal.lexical_occurrence_count,
        proposal.concept_candidate_count,
        proposal.sense_candidate_count,
        proposal.explicit_unknown_count,
        proposal.explicit_unsupported_count,
    )
    expected = (
        fixture.expected_proposal_status,
        fixture.expected_lexical_occurrence_count,
        fixture.expected_concept_candidate_count,
        fixture.expected_sense_candidate_count,
        fixture.expected_unknown_count,
        fixture.expected_unsupported_count,
    )
    if actual != expected:
        return _result(
            state=state,
            profile=active_profile,
            invocation=invocation,
            fixture=fixture,
            status=IntegrationStatus.HELD_EXPECTATION_MISMATCH,
            reason_code="exact_fixture_expectation_mismatch",
            bundle=bundle,
            adapter_state=adapter_state,
            stage_receipts=tuple(receipts),
            custody_result=custody,
            projection_result=projection,
            grammar_registry=registry,
            binding_result=binding,
            phase_trail_result=trails,
            constraint_result=constraints,
            structural_result=structural,
            proposal_result=proposal,
        )

    return _result(
        state=state,
        profile=active_profile,
        invocation=invocation,
        fixture=fixture,
        status=_status_for_proposal(proposal.status),
        reason_code="exact_slice36_to_slice37_candidate_chain_completed",
        bundle=bundle,
        adapter_state=adapter_state,
        stage_receipts=tuple(receipts),
        custody_result=custody,
        projection_result=projection,
        grammar_registry=registry,
        binding_result=binding,
        phase_trail_result=trails,
        constraint_result=constraints,
        structural_result=structural,
        proposal_result=proposal,
    )


__all__ = (
    "REASON_DISABLED",
    "REQUESTED_OPERATION",
    "build_disabled_structural_concept_bootstrap_state",
    "build_fixture_invocation",
    "build_slice37_acceptance_record",
    "build_slice37_rollback_metadata",
    "run_disabled_structural_concept_bootstrap",
)
