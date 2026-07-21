"""Explicit fixture-only Slice 42H bootstrap integration and closeout."""
from __future__ import annotations

from dataclasses import replace
from typing import Final

from ...meaning_structure_manifest.serialization import canonical_manifest_sha256
from ..msm_outward_expression_integration import (
    MsmOutwardExpressionIntegrationInput,
    MsmOutwardExpressionIntegrationResult,
    integrate_outward_meaning_and_expression_link,
    validate_integration_input,
    validate_integration_result,
)
from .authority import (
    PRE_SLICE42_COMMIT,
    PRE_SLICE42_SUBJECT,
    PRE_SLICE42_TREE,
    REASON_DISABLED,
    REQUESTED_OPERATION,
    SLICE42_ACCEPTED_CHAIN,
    SLICE42_ACCEPTED_SCOPE,
    SLICE42_DEFERRED_SCOPE,
    SLICE42_INCREMENT_LABELS,
    SLICE42_PERMANENT_BOUNDARIES,
    SLICE42_PROHIBITED_AUTHORITY,
    SLICE42G_ACCEPTED_HEAD,
    SLICE42G_ACCEPTED_SUBJECT,
    SLICE42G_ACCEPTED_TREE,
    SLICE42H_ACCEPTANCE_RECORD_VERSION,
    SLICE42H_RECEIPT_VERSION,
    SLICE42H_ROLLBACK_METADATA_VERSION,
)
from .canonical import deterministic_digest, stable_identifier
from .fixtures import get_outward_expression_closeout_fixture, is_exact_accepted_fixture
from .schema import (
    DisabledOutwardExpressionCloseoutResult,
    DisabledOutwardExpressionCloseoutState,
    OutwardExpressionCloseoutFixture,
    OutwardExpressionCloseoutInvocation,
    Slice42AcceptanceRecord,
    Slice42CloseoutStage,
    Slice42CloseoutStageReceipt,
    Slice42CloseoutStatus,
    Slice42RollbackMetadata,
)

EXPECTED_STAGE_CHAIN: Final[tuple[Slice42CloseoutStage, ...]] = (
    Slice42CloseoutStage.ISOLATED_BOOTSTRAP_BOUNDARY,
    Slice42CloseoutStage.ACCEPTED_SLICE42A_SCHEMA_AUTHORITY,
    Slice42CloseoutStage.ACCEPTED_SLICE42B_VALIDATION_LIFECYCLE,
    Slice42CloseoutStage.ACCEPTED_SLICE42C_EXPRESSION_ELIGIBILITY,
    Slice42CloseoutStage.ACCEPTED_SLICE42D_PRESERVATION_OBLIGATIONS,
    Slice42CloseoutStage.ACCEPTED_SLICE42E_EXPRESSION_PLAN,
    Slice42CloseoutStage.ACCEPTED_SLICE42F_SURFACE_REALIZATION,
    Slice42CloseoutStage.ACCEPTED_SLICE42G_MSM_CUSTODY,
    Slice42CloseoutStage.SLICE42_CLOSEOUT,
)


def _with_id(namespace: str, value: object, field: str):
    return replace(
        value,
        **{
            field: stable_identifier(
                namespace,
                value,
                excluded_fields=(field,),
            )
        },
    )


def build_disabled_outward_expression_closeout_state(
    *, explicit_offline_developer_enable: bool = False,
) -> DisabledOutwardExpressionCloseoutState:
    enabled = explicit_offline_developer_enable is True
    draft = DisabledOutwardExpressionCloseoutState(
        state_id="placeholder",
        enabled=enabled,
        explicit_offline_developer_enable=enabled,
        disabled_by_default=True,
        explicit_invocation_required=True,
        accepted_static_fixture_only=True,
        offline_only=True,
        read_only=True,
        in_memory_only=True,
        deterministic=True,
        exact_profile_bounded=True,
        source_preserving=True,
        rollback_safe=True,
        automatic_activation_allowed=False,
        arbitrary_input_allowed=False,
        route_allowed=False,
        api_allowed=False,
        network_allowed=False,
        filesystem_read_allowed=False,
        filesystem_write_allowed=False,
        memory_read_allowed=False,
        memory_write_allowed=False,
        tool_allowed=False,
        action_allowed=False,
        rendering_allowed=False,
        delivery_allowed=False,
        echo_validation_allowed=False,
        truth_authority_allowed=False,
        evidence_authority_allowed=False,
        permission_authority_allowed=False,
        execution_authority_allowed=False,
        slice43_allowed=False,
    )
    return _with_id("slice42h_disabled_closeout_state", draft, "state_id")


def build_outward_expression_closeout_invocation(
    fixture_name: str,
) -> OutwardExpressionCloseoutInvocation | None:
    fixture = get_outward_expression_closeout_fixture(fixture_name)
    if fixture is None:
        return None
    draft = OutwardExpressionCloseoutInvocation(
        invocation_id="placeholder",
        fixture_id=fixture.fixture_id,
        fixture_name=fixture.fixture_name,
        requested_operation=REQUESTED_OPERATION,
        explicit_offline_developer_enable=True,
        arbitrary_input_carried=False,
    )
    return _with_id(
        "slice42h_outward_expression_closeout_invocation",
        draft,
        "invocation_id",
    )


def build_slice42_rollback_metadata() -> Slice42RollbackMetadata:
    draft = Slice42RollbackMetadata(
        metadata_id="placeholder",
        metadata_version=SLICE42H_ROLLBACK_METADATA_VERSION,
        pre_slice42_commit=PRE_SLICE42_COMMIT,
        pre_slice42_tree=PRE_SLICE42_TREE,
        pre_slice42_subject=PRE_SLICE42_SUBJECT,
        accepted_slice42g_head=SLICE42G_ACCEPTED_HEAD,
        accepted_slice42g_tree=SLICE42G_ACCEPTED_TREE,
        accepted_slice42g_subject=SLICE42G_ACCEPTED_SUBJECT,
        recovery_requires_explicit_operator_action=True,
        complete_history_required=True,
        exact_tree_recovery_required=True,
        runtime_rollback_performed=False,
        repository_mutated=False,
    )
    return _with_id("slice42h_rollback_metadata", draft, "metadata_id")


def build_slice42_acceptance_record(
    rollback_metadata: Slice42RollbackMetadata | None = None,
    *, completed: bool = True,
) -> Slice42AcceptanceRecord:
    rollback = rollback_metadata or build_slice42_rollback_metadata()
    draft = Slice42AcceptanceRecord(
        record_id="placeholder",
        record_version=SLICE42H_ACCEPTANCE_RECORD_VERSION,
        accepted_increment_labels=SLICE42_INCREMENT_LABELS,
        accepted_chain=SLICE42_ACCEPTED_CHAIN,
        accepted_scope=SLICE42_ACCEPTED_SCOPE,
        deferred_scope=SLICE42_DEFERRED_SCOPE,
        permanent_boundaries=SLICE42_PERMANENT_BOUNDARIES,
        prohibited_authority=SLICE42_PROHIBITED_AUTHORITY,
        rollback_metadata_ref=rollback.metadata_id,
        slice42_closed=completed,
        slice43_started=False,
        stop_after_slice42=True,
        authorized_meaning_required=completed,
        selected_meaning_preserved=completed,
        scope_preserved=completed,
        certainty_preserved=completed,
        evidence_status_preserved=completed,
        caveats_preserved=completed,
        refusal_state_preserved=completed,
        unresolved_conditions_preserved=completed,
        deterministic_expression_candidate_created=completed,
        expression_candidate_remains_unvalidated=completed,
        echo_validation_performed=False,
        delivery_authority=False,
        truth_authority=False,
        evidence_authority=False,
        permission_authority=False,
        execution_authority=False,
        runtime_self_grants_acceptance=False,
        production_ready=False,
    )
    return _with_id("slice42_acceptance_record", draft, "record_id")


def _stage_receipt(
    stage: Slice42CloseoutStage,
    stage_index: int,
    input_refs: tuple[str, ...],
    output_refs: tuple[str, ...],
) -> Slice42CloseoutStageReceipt:
    stage_digest = deterministic_digest(
        {
            "stage": stage.value,
            "stage_index": stage_index,
            "input_refs": input_refs,
            "output_refs": output_refs,
        }
    )
    draft = Slice42CloseoutStageReceipt(
        receipt_id="placeholder",
        receipt_version=SLICE42H_RECEIPT_VERSION,
        stage=stage,
        stage_index=stage_index,
        input_refs=input_refs,
        output_refs=output_refs,
        stage_digest=stage_digest,
        deterministic=True,
        source_preserved=True,
        offline_only=True,
        in_memory_only=True,
        route_created=False,
        api_created=False,
        network_accessed=False,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        tool_invoked=False,
        action_performed=False,
        rendered=False,
        echo_validated=False,
        delivered=False,
    )
    return _with_id("slice42h_closeout_stage_receipt", draft, "receipt_id")


def _build_stage_receipts(
    state: DisabledOutwardExpressionCloseoutState,
    invocation: OutwardExpressionCloseoutInvocation,
    integration_input: MsmOutwardExpressionIntegrationInput,
    integration_result: MsmOutwardExpressionIntegrationResult,
    acceptance_record: Slice42AcceptanceRecord,
) -> tuple[Slice42CloseoutStageReceipt, ...]:
    realization_input = integration_input.surface_realization_input
    realization_result = integration_input.surface_realization_result
    plan_input = realization_input.plan_input
    plan_result = realization_input.plan_result
    projection_input = plan_input.projection_input
    projection_result = plan_input.projection_result
    eligibility_input = projection_input.expression_eligibility_evaluation_input
    eligibility_result = projection_input.expression_eligibility_result

    refs: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
        ((state.state_id,), (invocation.invocation_id,)),
        (
            (
                eligibility_input.selected_meaning_source_custody.source_custody_id,
                eligibility_input.outward_expression_authority_requirement.authority_requirement_id,
            ),
            (eligibility_input.outward_expression_governance_bundle.bundle_id,),
        ),
        (
            (eligibility_input.outward_expression_governance_bundle.bundle_id,),
            (eligibility_input.evaluation_input_id,),
        ),
        ((eligibility_input.evaluation_input_id,), (eligibility_result.result_id,)),
        (
            (projection_input.projection_input_id, eligibility_result.result_id),
            (
                projection_result.result_id,
                projection_result.obligation_package.obligation_package_id,
            ),
        ),
        (
            (plan_input.plan_input_id, projection_result.result_id),
            (plan_result.result_id, plan_result.expression_plan.expression_plan_id),
        ),
        (
            (realization_input.realization_input_id, plan_result.result_id),
            (
                realization_result.result_id,
                realization_result.expression_candidate.expression_candidate_id,
            ),
        ),
        (
            (integration_input.integration_input_id, realization_result.result_id),
            (
                integration_result.result_id,
                integration_result.governed_outward_meaning_record.record_id,
                integration_result.expression_link_record.record_id,
            ),
        ),
        ((integration_result.result_id,), (acceptance_record.record_id,)),
    )
    return tuple(
        _stage_receipt(stage, index, input_refs, output_refs)
        for index, (stage, (input_refs, output_refs)) in enumerate(
            zip(EXPECTED_STAGE_CHAIN, refs, strict=True)
        )
    )


def _input_matches_fixture(
    fixture: OutwardExpressionCloseoutFixture,
    value: object,
) -> bool:
    if type(value) is not MsmOutwardExpressionIntegrationInput:
        return False
    if not validate_integration_input(value).ok:
        return False
    realization_input = value.surface_realization_input
    plan_input = realization_input.plan_input
    projection_input = plan_input.projection_input
    eligibility_input = projection_input.expression_eligibility_evaluation_input
    eligibility_result = projection_input.expression_eligibility_result
    projection_result = plan_input.projection_result
    plan_result = realization_input.plan_result
    return all(
        (
            value.integration_input_id == fixture.expected_slice42g_integration_input_id,
            eligibility_input.selected_meaning_source_custody.source_custody_id
            == fixture.expected_slice42a_source_custody_id,
            eligibility_input.outward_expression_authority_requirement.authority_requirement_id
            == fixture.expected_slice42a_authority_requirement_id,
            eligibility_input.outward_expression_governance_bundle.bundle_id
            == fixture.expected_slice42b_governance_bundle_id,
            eligibility_input.evaluation_input_id
            == fixture.expected_slice42c_evaluation_input_id,
            eligibility_result.result_id == fixture.expected_slice42c_result_id,
            projection_input.projection_input_id
            == fixture.expected_slice42d_projection_input_id,
            projection_result.result_id == fixture.expected_slice42d_result_id,
            projection_result.obligation_package.obligation_package_id
            == fixture.expected_obligation_package_id,
            plan_input.plan_input_id == fixture.expected_slice42e_plan_input_id,
            plan_result.result_id == fixture.expected_slice42e_result_id,
            plan_result.expression_plan.expression_plan_id
            == fixture.expected_expression_plan_id,
            realization_input.realization_input_id
            == fixture.expected_slice42f_realization_input_id,
            value.surface_realization_result.result_id
            == fixture.expected_slice42f_result_id,
            value.expression_candidate.expression_candidate_id
            == fixture.expected_expression_candidate_id,
        )
    )


def _result_matches_fixture(
    fixture: OutwardExpressionCloseoutFixture,
    integration_input: MsmOutwardExpressionIntegrationInput,
    result: object,
) -> bool:
    if type(result) is not MsmOutwardExpressionIntegrationResult:
        return False
    if not validate_integration_result(result, integration_input=integration_input).ok:
        return False
    source = result.source_manifest
    successor = result.successor_manifest
    return all(
        (
            result.result_id == fixture.expected_slice42g_result_id,
            result.result_digest == fixture.expected_slice42g_result_digest,
            source.manifest_id == fixture.expected_source_manifest_id,
            canonical_manifest_sha256(source) == fixture.expected_source_manifest_sha256,
            successor.manifest_id == fixture.expected_successor_manifest_id,
            canonical_manifest_sha256(successor) == fixture.expected_successor_manifest_sha256,
            result.governed_outward_meaning_record.prior_selected_meaning_ref
            == fixture.expected_selected_meaning_ref,
            result.governed_outward_meaning_record.record_id
            == fixture.expected_outward_meaning_ref,
            result.expression_link_record.record_id
            == fixture.expected_expression_link_ref,
            result.external_authority_reference_record.record_id
            == fixture.expected_external_authority_ref,
            result.companion.companion_id == fixture.expected_companion_id,
            result.receipt.receipt_id == fixture.expected_receipt_id,
            tuple(item.record_id for item in successor.candidate_meanings)
            == fixture.expected_candidate_refs,
            tuple(item.record_id for item in successor.non_selection_outcomes)
            == fixture.expected_non_selection_refs,
            result.companion.preserved_alternative_refs
            == fixture.expected_alternative_refs,
            result.companion.unresolved_condition_refs
            == fixture.expected_unresolved_refs,
            len(successor.candidate_meanings) == fixture.expected_candidate_count,
            len(successor.non_selection_outcomes) == fixture.expected_non_selection_count,
            len(successor.selected_governed_meanings) == fixture.expected_selected_count,
            len(successor.governed_outward_meanings)
            == fixture.expected_outward_meaning_count,
            len(successor.expression_links) == fixture.expected_expression_link_count,
            len(successor.validation_links) == fixture.expected_validation_link_count,
            len(successor.delivery_or_containment_links)
            == fixture.expected_delivery_link_count,
            result.selected_meaning_preserved,
            result.all_candidate_meanings_retained,
            result.all_non_selection_outcomes_retained,
            result.alternatives_and_unresolved_retained,
            result.complete_successor_manifest_validated,
            result.candidate_remains_unvalidated,
            not result.selected_meaning_rewritten,
            not result.candidate_deleted,
            not result.non_selection_outcome_deleted,
            not result.certainty_upgraded,
            not result.evidence_status_upgraded,
            not result.caveat_omitted,
            not result.refusal_softened,
            not result.echo_validation_performed,
            not result.delivery_authorized,
            not result.delivered,
            not result.truth_determined,
            not result.evidence_validated,
            not result.permission_granted,
            not result.execution_authorized,
            not result.route_or_api_created,
            not result.tool_invoked,
            not result.action_performed,
            not result.memory_accessed_or_written,
            not result.filesystem_or_network_accessed,
            not result.model_or_similarity_authority_used,
            not result.bootstrap_integration_enabled,
            not result.gp014_superseded,
        )
    )


def _build_result(
    state: DisabledOutwardExpressionCloseoutState,
    invocation: object,
    fixture: OutwardExpressionCloseoutFixture | None,
    status: Slice42CloseoutStatus,
    reason_code: str,
    *,
    integration_input: MsmOutwardExpressionIntegrationInput | None = None,
    integration_result: MsmOutwardExpressionIntegrationResult | None = None,
) -> DisabledOutwardExpressionCloseoutResult:
    completed = (
        status is Slice42CloseoutStatus.COMPLETED
        and integration_input is not None
        and integration_result is not None
    )
    rollback = build_slice42_rollback_metadata()
    acceptance = build_slice42_acceptance_record(rollback, completed=completed)
    actual_invocation = (
        invocation if type(invocation) is OutwardExpressionCloseoutInvocation else None
    )
    receipts = (
        _build_stage_receipts(
            state,
            actual_invocation,
            integration_input,
            integration_result,
            acceptance,
        )
        if completed and actual_invocation is not None
        else ()
    )
    repeat_digest = deterministic_digest(
        {
            "status": status.value,
            "reason_code": reason_code,
            "state_id": state.state_id,
            "invocation_id": actual_invocation.invocation_id if actual_invocation else "",
            "fixture_id": fixture.fixture_id if fixture else "",
            "integration_input_id": (
                integration_input.integration_input_id if integration_input else ""
            ),
            "integration_result_id": (
                integration_result.result_id if integration_result else ""
            ),
            "stage_receipts": receipts,
            "acceptance_record": acceptance,
            "rollback_metadata": rollback,
        }
    )
    draft = DisabledOutwardExpressionCloseoutResult(
        result_id="placeholder",
        result_digest="placeholder",
        status=status,
        reason_code=reason_code,
        state_id=state.state_id,
        invocation_id=actual_invocation.invocation_id if actual_invocation else "",
        fixture_id=fixture.fixture_id if fixture else "",
        integration_input=integration_input,
        integration_result=integration_result,
        stage_receipts=receipts,
        acceptance_record=acceptance,
        rollback_metadata=rollback,
        deterministic_repeat_digest=repeat_digest,
        disabled_by_default=True,
        explicitly_invoked=completed,
        accepted_static_fixture_only=True,
        offline_only=True,
        read_only=True,
        in_memory_only=True,
        deterministic=True,
        exact_stage_chain_complete=completed,
        stage_receipt_count=len(receipts),
        authorized_meaning_required=completed,
        selected_meaning_preserved=completed,
        scope_preserved=completed,
        certainty_preserved=completed,
        evidence_status_preserved=completed,
        caveats_preserved=completed,
        refusal_state_preserved=completed,
        unresolved_conditions_preserved=completed,
        deterministic_expression_candidate_created=completed,
        governed_outward_meaning_custody_preserved=completed,
        expression_link_custody_preserved=completed,
        complete_successor_manifest_validated=completed,
        expression_candidate_remains_unvalidated=completed,
        final_slice42_acceptance_record_created=completed,
        slice43_started=False,
        msm_v1_schema_modified=False,
        automatic_migration_performed=False,
        selected_meaning_rewritten=False,
        candidate_alternative_deleted=False,
        unresolved_state_resolved=False,
        certainty_upgraded=False,
        evidence_status_upgraded=False,
        caveat_omitted=False,
        refusal_softened=False,
        expression_candidate_rewritten=False,
        validation_link_created=False,
        delivery_link_created=False,
        echo_validation_performed=False,
        echo_approved=False,
        delivery_authorized=False,
        delivered=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        route_created=False,
        api_created=False,
        network_accessed=False,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        tool_invoked=False,
        action_performed=False,
        rendered=False,
        external_resource_loaded=False,
        language_model_used=False,
        embedding_used=False,
        vector_used=False,
        rag_used=False,
        semantic_similarity_used=False,
        neural_parser_used=False,
        hidden_classifier_used=False,
        gp014_superseded=False,
    )
    with_id = _with_id(
        "slice42h_disabled_outward_expression_closeout_result",
        draft,
        "result_id",
    )
    digest = deterministic_digest(
        replace(with_id, result_digest="placeholder")
    )
    return replace(with_id, result_digest=digest)


def run_disabled_outward_expression_closeout(
    invocation: object = None,
    *,
    state: object = None,
    integration_input: object = None,
) -> DisabledOutwardExpressionCloseoutResult:
    actual_state = (
        build_disabled_outward_expression_closeout_state()
        if state is None
        else state
    )
    if type(actual_state) is not DisabledOutwardExpressionCloseoutState:
        return _build_result(
            build_disabled_outward_expression_closeout_state(),
            invocation,
            None,
            Slice42CloseoutStatus.HELD_INVALID_STATE,
            "exact_closeout_state_required",
        )
    if not actual_state.enabled:
        return _build_result(
            actual_state,
            invocation,
            None,
            Slice42CloseoutStatus.REFUSED_DISABLED,
            REASON_DISABLED,
        )
    if (
        type(invocation) is not OutwardExpressionCloseoutInvocation
        or invocation.requested_operation != REQUESTED_OPERATION
        or invocation.explicit_offline_developer_enable is not True
        or invocation.arbitrary_input_carried is not False
    ):
        return _build_result(
            actual_state,
            invocation,
            None,
            Slice42CloseoutStatus.HELD_INVALID_INVOCATION,
            "exact_fixture_invocation_required",
        )
    fixture = get_outward_expression_closeout_fixture(invocation.fixture_name)
    if (
        fixture is None
        or fixture.fixture_id != invocation.fixture_id
        or not is_exact_accepted_fixture(fixture)
    ):
        return _build_result(
            actual_state,
            invocation,
            fixture,
            Slice42CloseoutStatus.HELD_FIXTURE_NOT_ACCEPTED,
            "exact_accepted_static_fixture_required",
        )
    if not _input_matches_fixture(fixture, integration_input):
        return _build_result(
            actual_state,
            invocation,
            fixture,
            Slice42CloseoutStatus.HELD_INVALID_PREDECESSOR_OUTPUT,
            "exact_accepted_slice42g_integration_input_required",
        )
    assert type(integration_input) is MsmOutwardExpressionIntegrationInput
    try:
        integration_result = integrate_outward_meaning_and_expression_link(
            integration_input
        )
    except (TypeError, ValueError, AttributeError, AssertionError):
        return _build_result(
            actual_state,
            invocation,
            fixture,
            Slice42CloseoutStatus.HELD_INVALID_PREDECESSOR_OUTPUT,
            "slice42g_integration_failed_closed",
        )
    if not _result_matches_fixture(fixture, integration_input, integration_result):
        return _build_result(
            actual_state,
            invocation,
            fixture,
            Slice42CloseoutStatus.HELD_EXPECTATION_MISMATCH,
            "exact_slice42g_fixture_result_mismatch",
        )
    return _build_result(
        actual_state,
        invocation,
        fixture,
        Slice42CloseoutStatus.COMPLETED,
        "slice42h_disabled_fixture_closeout_complete",
        integration_input=integration_input,
        integration_result=integration_result,
    )


__all__ = (
    "EXPECTED_STAGE_CHAIN",
    "build_disabled_outward_expression_closeout_state",
    "build_outward_expression_closeout_invocation",
    "build_slice42_acceptance_record",
    "build_slice42_rollback_metadata",
    "run_disabled_outward_expression_closeout",
)
