"""Explicit fixture-only Slice 38H integration.

This module composes the accepted Slice 37G disabled bootstrap with the
accepted Slice 38G proposal function.  It creates immutable candidate or
non-progress records only.  It never performs selection, routing, invocation,
action, memory, rendering, delivery, evidence validation or truth judgment.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Final

from ..disabled_structural_concept_bootstrap import (
    build_disabled_structural_concept_bootstrap_state,
    build_fixture_invocation as build_slice37_fixture_invocation,
    run_disabled_structural_concept_bootstrap,
    validate_integration_result as validate_slice37_integration_result,
)
from ..predicate_role_frame_registry.predicate_role_frame_candidate_proposal import (
    CANONICAL_COMPATIBILITY_SNAPSHOT,
    DEFAULT_PROPOSAL_PROFILE,
    SLICE38_REGISTRY_SNAPSHOT,
    CandidateProposalStatus,
    propose_predicate_role_frame_candidates,
    validate_result as validate_slice38_result,
)
from .fixtures import (
    get_disabled_predicate_role_frame_fixture,
    is_exact_accepted_fixture,
)
from .schema import (
    PRE_SLICE38_COMMIT,
    PRE_SLICE38_TREE,
    SLICE38_ACCEPTED_CHAIN,
    SLICE38_ACCEPTED_SCOPE,
    SLICE38_DEFERRED_SCOPE,
    SLICE38_INCREMENT_LABELS,
    SLICE38_PERMANENT_BOUNDARIES,
    SLICE38G_ACCEPTED_HEAD,
    SLICE38G_ACCEPTED_SUBJECT,
    SLICE38G_ACCEPTED_TREE,
    SLICE38H_COMMIT_SUBJECT,
    CloseoutIntegrationStage,
    CloseoutIntegrationStatus,
    CloseoutStageReceipt,
    DisabledPredicateRoleFrameBootstrapResult,
    DisabledPredicateRoleFrameBootstrapState,
    DisabledPredicateRoleFrameInvocation,
    Slice38AcceptanceRecord,
    Slice38RollbackMetadata,
)


REQUESTED_OPERATION: Final[str] = (
    "run_exact_slice37_to_slice38_candidate_fixture_chain"
)
REASON_DISABLED: Final[str] = (
    "slice38h_disabled_by_default_explicit_offline_enable_required"
)


def _with_expected_id(record: object, field: str):
    return replace(record, **{field: record.expected_id()})


def build_disabled_predicate_role_frame_bootstrap_state(
    *,
    explicit_offline_developer_enable: bool = False,
) -> DisabledPredicateRoleFrameBootstrapState:
    enabled = explicit_offline_developer_enable is True
    draft = DisabledPredicateRoleFrameBootstrapState(
        state_id="",
        enabled=enabled,
        explicit_offline_developer_enable=enabled,
        disabled_by_default=True,
        explicit_invocation_required=True,
        accepted_static_fixture_only=True,
        offline_only=True,
        standard_library_only=True,
        deterministic=True,
        read_only=True,
        in_memory_only=True,
        exact_profile_bounded=True,
        source_preserving=True,
        structural_ancestry_preserving=True,
        operator_ancestry_preserving=True,
        phase_trail_ancestry_preserving=True,
        scope_attachment_ancestry_preserving=True,
        registry_snapshot_preserving=True,
        zero_one_many_preserving=True,
        explicit_non_progress_preserving=True,
        rollback_safe=True,
        automatic_activation_allowed=False,
        arbitrary_text_invocation_allowed=False,
        normalization_allowed=False,
        nearest_known_substitution_allowed=False,
        semantic_similarity_allowed=False,
        learned_model_allowed=False,
        external_resource_loading_allowed=False,
        filesystem_read_allowed=False,
        filesystem_write_allowed=False,
        network_allowed=False,
        memory_read_allowed=False,
        memory_write_allowed=False,
        api_route_allowed=False,
        capability_route_allowed=False,
        invocation_allowed=False,
        tool_allowed=False,
        action_allowed=False,
        rendering_allowed=False,
        delivery_allowed=False,
        selected_predicate_allowed=False,
        selected_frame_allowed=False,
        selected_participant_assignment_allowed=False,
        candidate_meaning_allowed=False,
        selected_meaning_allowed=False,
        clarification_allowed=False,
        refusal_allowed=False,
        blocked_progression_allowed=False,
        truth_allowed=False,
        evidence_validity_allowed=False,
        permission_allowed=False,
        runtime_self_acceptance_allowed=False,
        release_authorized=False,
        production_ready=False,
    )
    return _with_expected_id(draft, "state_id")


def build_slice38_rollback_metadata() -> Slice38RollbackMetadata:
    draft = Slice38RollbackMetadata(
        rollback_id="",
        pre_slice38_commit=PRE_SLICE38_COMMIT,
        pre_slice38_tree=PRE_SLICE38_TREE,
        accepted_parent_head=SLICE38G_ACCEPTED_HEAD,
        accepted_parent_tree=SLICE38G_ACCEPTED_TREE,
        accepted_parent_subject=SLICE38G_ACCEPTED_SUBJECT,
        expected_closeout_commit_subject=SLICE38H_COMMIT_SUBJECT,
        exact_commit_checkout_required=True,
        exact_tree_match_required=True,
        separate_recovery_clone_required=True,
        git_object_verification_required=True,
        live_repository_mutation_authorized=False,
        runtime_rollback_execution_authorized=False,
        rollback_proof_external_to_runtime=True,
    )
    return _with_expected_id(draft, "rollback_id")


def build_slice38_acceptance_record(
    rollback_metadata: Slice38RollbackMetadata | None = None,
) -> Slice38AcceptanceRecord:
    rollback = rollback_metadata or build_slice38_rollback_metadata()
    draft = Slice38AcceptanceRecord(
        acceptance_record_id="",
        decision_owner="Nicholas Jacob Bogaert / AI.Web",
        accepted_increment_labels=SLICE38_INCREMENT_LABELS,
        accepted_chain=SLICE38_ACCEPTED_CHAIN,
        permanent_boundaries=SLICE38_PERMANENT_BOUNDARIES,
        accepted_scope=SLICE38_ACCEPTED_SCOPE,
        deferred_scope=SLICE38_DEFERRED_SCOPE,
        rollback_metadata_id=rollback.rollback_id,
        accepted_parent_head=SLICE38G_ACCEPTED_HEAD,
        accepted_parent_tree=SLICE38G_ACCEPTED_TREE,
        pre_slice38_commit=PRE_SLICE38_COMMIT,
        pre_slice38_tree=PRE_SLICE38_TREE,
        disabled_by_default=True,
        explicitly_invoked_only=True,
        fixture_only=True,
        offline_only=True,
        deterministic=True,
        read_only=True,
        exact_profile_bounded=True,
        source_preserving=True,
        no_selected_predicate_authority=True,
        no_selected_frame_authority=True,
        no_selected_participant_authority=True,
        no_candidate_meaning_authority=True,
        no_selected_meaning_authority=True,
        no_permission_authority=True,
        no_route_authority=True,
        no_action_authority=True,
        no_memory_authority=True,
        no_delivery_authority=True,
        runtime_self_grants_acceptance=False,
        decision_owner_acceptance_required=True,
        release_authorized=False,
        production_ready=False,
    )
    return _with_expected_id(draft, "acceptance_record_id")


def build_fixture_invocation(
    fixture_name: str,
) -> DisabledPredicateRoleFrameInvocation | None:
    fixture = get_disabled_predicate_role_frame_fixture(fixture_name)
    if fixture is None:
        return None
    draft = DisabledPredicateRoleFrameInvocation(
        invocation_id="",
        fixture_name=fixture.fixture_name,
        fixture_id=fixture.fixture_id,
        proposal_profile_id=DEFAULT_PROPOSAL_PROFILE.profile_id,
        compatibility_snapshot_id=CANONICAL_COMPATIBILITY_SNAPSHOT.snapshot_id,
        slice38_registry_snapshot_id=SLICE38_REGISTRY_SNAPSHOT.snapshot_id,
        explicit_invocation=True,
        requested_operation=REQUESTED_OPERATION,
        raw_text_carried_by_invocation=False,
    )
    return _with_expected_id(draft, "invocation_id")


def _receipt(
    *,
    state: DisabledPredicateRoleFrameBootstrapState,
    invocation: DisabledPredicateRoleFrameInvocation,
    fixture_id: str,
    ordinal: int,
    stage: CloseoutIntegrationStage,
    predecessors: tuple[str, ...],
    output: object,
    output_id: str,
    output_schema_version: str,
    source_event_id: str,
    source_sha256: str,
) -> CloseoutStageReceipt:
    draft = CloseoutStageReceipt(
        receipt_id="",
        state_id=state.state_id,
        invocation_id=invocation.invocation_id,
        fixture_id=fixture_id,
        stage_ordinal=ordinal,
        stage=stage,
        predecessor_record_ids=predecessors,
        output_record_id=output_id,
        output_schema_version=output_schema_version,
        output_exact_type=type(output).__name__,
        output_validation_passed=True,
        source_event_id=source_event_id,
        source_sha256=source_sha256,
        source_ancestry_preserved=True,
        candidate_only=True,
        selected_predicate_created=False,
        selected_frame_created=False,
        selected_participant_assignment_created=False,
        candidate_meaning_created=False,
        selected_meaning_created=False,
        permission_inferred=False,
        route_created=False,
        invocation_proposed=False,
        tool_invoked=False,
        action_performed=False,
        memory_accessed=False,
        rendered=False,
        delivered=False,
        evidence_validity_determined=False,
        truth_determined=False,
    )
    return _with_expected_id(draft, "receipt_id")


def _safe_text(value: object, field: str) -> str:
    found = getattr(value, field, "")
    return found if type(found) is str else ""


def _result(
    *,
    state: DisabledPredicateRoleFrameBootstrapState,
    invocation: object,
    fixture_id: str = "",
    status: CloseoutIntegrationStatus,
    reason_code: str,
    receipts: tuple[CloseoutStageReceipt, ...] = (),
    slice37_result: object = None,
    slice38_result: object = None,
) -> DisabledPredicateRoleFrameBootstrapResult:
    rollback = build_slice38_rollback_metadata()
    acceptance = build_slice38_acceptance_record(rollback)
    valid_37 = validate_slice37_integration_result(slice37_result).ok
    valid_38 = validate_slice38_result(slice38_result).ok
    source_event_id = _safe_text(slice37_result, "source_event_id")
    source_sha256 = _safe_text(slice37_result, "source_sha256")
    body = dict(
        state_id=state.state_id,
        invocation_id=_safe_text(invocation, "invocation_id"),
        fixture_id=fixture_id,
        status=status,
        reason_code=reason_code,
        stage_receipts=receipts,
        stage_receipt_count=len(receipts),
        exact_stage_chain_complete=len(receipts) == 2,
        source_event_id=source_event_id,
        source_sha256=source_sha256,
        slice37_result=slice37_result if valid_37 else None,
        slice38_result=slice38_result if valid_38 else None,
        acceptance_record=acceptance,
        rollback_metadata=rollback,
        action_predicate_candidate_count=(
            getattr(slice38_result, "action_predicate_candidate_count", 0)
            if valid_38 else 0
        ),
        role_layout_candidate_count=(
            getattr(slice38_result, "role_layout_candidate_count", 0)
            if valid_38 else 0
        ),
        capability_reference_candidate_count=(
            getattr(slice38_result, "capability_reference_candidate_count", 0)
            if valid_38 else 0
        ),
        unresolved_alternative_count=(
            getattr(slice38_result, "unresolved_alternative_count", 0)
            if valid_38 else 0
        ),
        missing_role_count=(
            getattr(slice38_result, "missing_role_count", 0)
            if valid_38 else 0
        ),
        conflicting_role_count=(
            getattr(slice38_result, "conflicting_role_count", 0)
            if valid_38 else 0
        ),
        disabled_by_default=True,
        explicitly_invoked=(
            getattr(invocation, "explicit_invocation", False) is True
        ),
        fixture_only=True,
        offline_only=True,
        standard_library_only=True,
        deterministic=True,
        read_only=True,
        in_memory_only=True,
        exact_profile_bounded=True,
        source_preserved=valid_37,
        structural_ancestry_preserved=valid_38,
        operator_ancestry_preserved=valid_38,
        phase_trail_ancestry_preserved=valid_38,
        scope_attachment_ancestry_preserved=valid_38,
        registry_snapshots_preserved=valid_38,
        zero_one_many_preserved=valid_38,
        selected_predicate_created=False,
        selected_frame_created=False,
        selected_participant_assignment_created=False,
        candidate_meaning_created=False,
        selected_meaning_created=False,
        clarification_outcome_created=False,
        refusal_outcome_created=False,
        blocked_progression_outcome_created=False,
        permission_inferred=False,
        capability_availability_created=False,
        route_created=False,
        invocation_proposed=False,
        tool_invoked=False,
        action_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        outward_rendered=False,
        delivered=False,
        evidence_validity_determined=False,
        truth_determined=False,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        external_resource_loaded=False,
        language_model_used=False,
        embedding_used=False,
        semantic_similarity_used=False,
        technical_acceptance_granted_by_runtime=False,
        release_authorized=False,
        production_ready=False,
    )
    draft = DisabledPredicateRoleFrameBootstrapResult(result_id="", **body)
    return _with_expected_id(draft, "result_id")


def run_disabled_predicate_role_frame_bootstrap(
    invocation: object = None,
    *,
    integration_state: object = None,
    proposal_profile: object = None,
) -> DisabledPredicateRoleFrameBootstrapResult:
    """Run only the exact accepted fixture chain after explicit enablement."""

    from .validation import (
        validate_fixture,
        validate_integration_result,
        validate_integration_state,
        validate_invocation,
    )

    default_state = build_disabled_predicate_role_frame_bootstrap_state()
    state = integration_state if integration_state is not None else default_state

    if not validate_integration_state(state).ok:
        safe_state = (
            state
            if type(state) is DisabledPredicateRoleFrameBootstrapState
            else default_state
        )
        return _result(
            state=safe_state,
            invocation=invocation,
            status=CloseoutIntegrationStatus.HELD_INVALID_STATE,
            reason_code="exact_slice38h_integration_state_required",
        )
    assert type(state) is DisabledPredicateRoleFrameBootstrapState

    if not state.enabled:
        return _result(
            state=state,
            invocation=invocation,
            status=CloseoutIntegrationStatus.REFUSED_DISABLED,
            reason_code=REASON_DISABLED,
        )

    if not validate_invocation(invocation).ok:
        return _result(
            state=state,
            invocation=invocation,
            status=CloseoutIntegrationStatus.HELD_INVALID_INVOCATION,
            reason_code="exact_versioned_slice38h_fixture_invocation_required",
        )
    assert type(invocation) is DisabledPredicateRoleFrameInvocation

    fixture = get_disabled_predicate_role_frame_fixture(invocation.fixture_name)
    if (
        fixture is None
        or fixture.fixture_id != invocation.fixture_id
        or not is_exact_accepted_fixture(fixture)
        or not validate_fixture(fixture).ok
    ):
        return _result(
            state=state,
            invocation=invocation,
            fixture_id=getattr(fixture, "fixture_id", ""),
            status=CloseoutIntegrationStatus.HELD_FIXTURE_NOT_ACCEPTED,
            reason_code="exact_static_slice38h_fixture_required",
        )

    if (
        proposal_profile is not None
        and proposal_profile != DEFAULT_PROPOSAL_PROFILE
    ) or (
        invocation.proposal_profile_id != DEFAULT_PROPOSAL_PROFILE.profile_id
        or invocation.compatibility_snapshot_id
        != CANONICAL_COMPATIBILITY_SNAPSHOT.snapshot_id
        or invocation.slice38_registry_snapshot_id
        != SLICE38_REGISTRY_SNAPSHOT.snapshot_id
    ):
        return _result(
            state=state,
            invocation=invocation,
            fixture_id=fixture.fixture_id,
            status=CloseoutIntegrationStatus.HELD_INVALID_PROFILE,
            reason_code="exact_slice38g_default_profile_and_canonical_snapshots_required",
        )

    slice37_invocation = build_slice37_fixture_invocation(
        fixture.slice37_fixture_name
    )
    slice37_state = build_disabled_structural_concept_bootstrap_state(
        explicit_offline_developer_enable=True
    )
    slice37_result = run_disabled_structural_concept_bootstrap(
        slice37_invocation,
        integration_state=slice37_state,
    )
    if not validate_slice37_integration_result(slice37_result).ok:
        return _result(
            state=state,
            invocation=invocation,
            fixture_id=fixture.fixture_id,
            status=CloseoutIntegrationStatus.HELD_INVALID_PREDECESSOR_OUTPUT,
            reason_code="slice37g_integration_output_invalid",
        )

    source_event_id = slice37_result.source_event_id
    source_sha256 = slice37_result.source_sha256
    receipt37 = _receipt(
        state=state,
        invocation=invocation,
        fixture_id=fixture.fixture_id,
        ordinal=1,
        stage=CloseoutIntegrationStage.SLICE37_DISABLED_BOOTSTRAP,
        predecessors=(invocation.invocation_id,),
        output=slice37_result,
        output_id=slice37_result.result_id,
        output_schema_version=slice37_result.schema_version,
        source_event_id=source_event_id,
        source_sha256=source_sha256,
    )

    slice38_result = propose_predicate_role_frame_candidates(
        slice37_result.proposal_result,
        compatibility_snapshot=CANONICAL_COMPATIBILITY_SNAPSHOT,
        profile=DEFAULT_PROPOSAL_PROFILE,
        slice38_snapshot=SLICE38_REGISTRY_SNAPSHOT,
    )
    if not validate_slice38_result(slice38_result).ok:
        return _result(
            state=state,
            invocation=invocation,
            fixture_id=fixture.fixture_id,
            status=CloseoutIntegrationStatus.HELD_INVALID_PREDECESSOR_OUTPUT,
            reason_code="slice38g_candidate_output_invalid",
            receipts=(receipt37,),
            slice37_result=slice37_result,
        )

    receipt38 = _receipt(
        state=state,
        invocation=invocation,
        fixture_id=fixture.fixture_id,
        ordinal=2,
        stage=CloseoutIntegrationStage.SLICE38_CANDIDATE_PROPOSAL,
        predecessors=(slice37_result.result_id,),
        output=slice38_result,
        output_id=slice38_result.result_id,
        output_schema_version=slice38_result.schema_version,
        source_event_id=source_event_id,
        source_sha256=source_sha256,
    )

    expectations_match = (
        slice37_result.status.value == fixture.expected_slice37_status
        and slice38_result.status.value == fixture.expected_slice38_status
        and slice38_result.action_predicate_candidate_count
        == fixture.expected_action_predicate_candidate_count
        and slice38_result.role_layout_candidate_count
        == fixture.expected_role_layout_candidate_count
        and slice38_result.capability_reference_candidate_count
        == fixture.expected_capability_reference_candidate_count
    )
    if not expectations_match:
        return _result(
            state=state,
            invocation=invocation,
            fixture_id=fixture.fixture_id,
            status=CloseoutIntegrationStatus.HELD_EXPECTATION_MISMATCH,
            reason_code="exact_fixture_expectation_mismatch",
            receipts=(receipt37, receipt38),
            slice37_result=slice37_result,
            slice38_result=slice38_result,
        )

    if slice38_result.status is CandidateProposalStatus.EXPLICIT_UNKNOWN:
        status = CloseoutIntegrationStatus.COMPLETED_EXPLICIT_UNKNOWN
    elif slice38_result.status is CandidateProposalStatus.EXPLICIT_UNSUPPORTED:
        status = CloseoutIntegrationStatus.COMPLETED_EXPLICIT_UNSUPPORTED
    else:
        status = CloseoutIntegrationStatus.HELD_EXPECTATION_MISMATCH

    result = _result(
        state=state,
        invocation=invocation,
        fixture_id=fixture.fixture_id,
        status=status,
        reason_code="exact_slice37_to_slice38_candidate_chain_completed",
        receipts=(receipt37, receipt38),
        slice37_result=slice37_result,
        slice38_result=slice38_result,
    )
    if not validate_integration_result(result).ok:
        return _result(
            state=state,
            invocation=invocation,
            fixture_id=fixture.fixture_id,
            status=CloseoutIntegrationStatus.HELD_INVALID_PREDECESSOR_OUTPUT,
            reason_code="slice38h_result_self_validation_failed",
            receipts=(receipt37, receipt38),
            slice37_result=slice37_result,
            slice38_result=slice38_result,
        )
    return result
