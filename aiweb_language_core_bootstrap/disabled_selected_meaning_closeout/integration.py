"""Explicit fixture-only Slice 41F bootstrap integration and closeout."""
from __future__ import annotations

from dataclasses import replace
from typing import Final

from ..meaning_structure_manifest import NonSelectionOutcomeKind
from ..meaning_structure_manifest.serialization import canonical_manifest_sha256
from ..selected_meaning_runtime.msm_selected_meaning_integration import (
    MsmSelectedMeaningIntegrationInput,
    MsmSelectedMeaningIntegrationResult,
    integrate_selected_meaning_into_manifest,
    validate_integration_input,
    validate_integration_result,
)
from .authority import (
    PRE_SLICE41_COMMIT,
    PRE_SLICE41_SUBJECT,
    PRE_SLICE41_TREE,
    REASON_DISABLED,
    REQUESTED_OPERATION,
    SLICE41_ACCEPTED_CHAIN,
    SLICE41_ACCEPTED_SCOPE,
    SLICE41_DEFERRED_SCOPE,
    SLICE41_INCREMENT_LABELS,
    SLICE41_PERMANENT_BOUNDARIES,
    SLICE41_PROHIBITED_AUTHORITY,
    SLICE41E_ACCEPTED_HEAD,
    SLICE41E_ACCEPTED_SUBJECT,
    SLICE41E_ACCEPTED_TREE,
    SLICE41F_ACCEPTANCE_RECORD_VERSION,
    SLICE41F_RECEIPT_VERSION,
    SLICE41F_ROLLBACK_METADATA_VERSION,
)
from .canonical import deterministic_digest, stable_identifier
from .fixtures import (
    get_selected_meaning_closeout_fixture,
    is_exact_accepted_fixture,
)
from .schema import (
    DisabledSelectedMeaningCloseoutResult,
    DisabledSelectedMeaningCloseoutState,
    SelectedMeaningCloseoutFixture,
    SelectedMeaningCloseoutInvocation,
    Slice41AcceptanceRecord,
    Slice41CloseoutStage,
    Slice41CloseoutStageReceipt,
    Slice41CloseoutStatus,
    Slice41RollbackMetadata,
)

EXPECTED_STAGE_CHAIN: Final[tuple[Slice41CloseoutStage, ...]] = (
    Slice41CloseoutStage.ISOLATED_BOOTSTRAP_BOUNDARY,
    Slice41CloseoutStage.ACCEPTED_SLICE40H_GATE_CUSTODY,
    Slice41CloseoutStage.ACCEPTED_SLICE41C_SELECTION_ELIGIBILITY,
    Slice41CloseoutStage.ACCEPTED_SLICE41D_SELECTED_MEANING,
    Slice41CloseoutStage.ACCEPTED_SLICE41E_MSM_INTEGRATION,
    Slice41CloseoutStage.SLICE41_CLOSEOUT,
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


def build_disabled_selected_meaning_closeout_state(
    *,
    explicit_offline_developer_enable: bool = False,
) -> DisabledSelectedMeaningCloseoutState:
    enabled = explicit_offline_developer_enable is True
    draft = DisabledSelectedMeaningCloseoutState(
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
        truth_authority_allowed=False,
        evidence_authority_allowed=False,
        permission_authority_allowed=False,
        execution_authority_allowed=False,
        outward_expression_authority_allowed=False,
        slice42_allowed=False,
    )
    return _with_id("slice41f_disabled_closeout_state", draft, "state_id")


def build_selected_meaning_closeout_invocation(
    fixture_name: str,
) -> SelectedMeaningCloseoutInvocation | None:
    fixture = get_selected_meaning_closeout_fixture(fixture_name)
    if fixture is None:
        return None
    draft = SelectedMeaningCloseoutInvocation(
        invocation_id="placeholder",
        fixture_id=fixture.fixture_id,
        fixture_name=fixture.fixture_name,
        requested_operation=REQUESTED_OPERATION,
        explicit_offline_developer_enable=True,
        arbitrary_input_carried=False,
    )
    return _with_id(
        "slice41f_selected_meaning_closeout_invocation",
        draft,
        "invocation_id",
    )


def build_slice41_rollback_metadata() -> Slice41RollbackMetadata:
    draft = Slice41RollbackMetadata(
        metadata_id="placeholder",
        metadata_version=SLICE41F_ROLLBACK_METADATA_VERSION,
        pre_slice41_commit=PRE_SLICE41_COMMIT,
        pre_slice41_tree=PRE_SLICE41_TREE,
        pre_slice41_subject=PRE_SLICE41_SUBJECT,
        accepted_slice41e_head=SLICE41E_ACCEPTED_HEAD,
        accepted_slice41e_tree=SLICE41E_ACCEPTED_TREE,
        accepted_slice41e_subject=SLICE41E_ACCEPTED_SUBJECT,
        recovery_requires_explicit_operator_action=True,
        complete_history_required=True,
        exact_tree_recovery_required=True,
        runtime_rollback_performed=False,
        repository_mutated=False,
    )
    return _with_id("slice41f_rollback_metadata", draft, "metadata_id")


def build_slice41_acceptance_record(
    rollback_metadata: Slice41RollbackMetadata | None = None,
    *,
    completed: bool = True,
) -> Slice41AcceptanceRecord:
    rollback = rollback_metadata or build_slice41_rollback_metadata()
    draft = Slice41AcceptanceRecord(
        record_id="placeholder",
        record_version=SLICE41F_ACCEPTANCE_RECORD_VERSION,
        accepted_increment_labels=SLICE41_INCREMENT_LABELS,
        accepted_chain=SLICE41_ACCEPTED_CHAIN,
        accepted_scope=SLICE41_ACCEPTED_SCOPE,
        deferred_scope=SLICE41_DEFERRED_SCOPE,
        permanent_boundaries=SLICE41_PERMANENT_BOUNDARIES,
        prohibited_authority=SLICE41_PROHIBITED_AUTHORITY,
        rollback_metadata_ref=rollback.metadata_id,
        slice41_closed=completed,
        slice42_started=False,
        stop_after_slice41=True,
        selected_meaning_bounded_semantic_custody_only=True,
        alternatives_preserved=completed,
        unresolved_state_preserved=completed,
        truth_authority=False,
        evidence_authority=False,
        permission_authority=False,
        execution_authority=False,
        outward_expression_authority=False,
        runtime_self_grants_acceptance=False,
        production_ready=False,
    )
    return _with_id("slice41_acceptance_record", draft, "record_id")


def _stage_receipt(
    stage: Slice41CloseoutStage,
    stage_index: int,
    input_refs: tuple[str, ...],
    output_refs: tuple[str, ...],
) -> Slice41CloseoutStageReceipt:
    stage_digest = deterministic_digest(
        {
            "stage": stage.value,
            "stage_index": stage_index,
            "input_refs": input_refs,
            "output_refs": output_refs,
        }
    )
    draft = Slice41CloseoutStageReceipt(
        receipt_id="placeholder",
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
        delivered=False,
    )
    return _with_id("slice41f_closeout_stage_receipt", draft, "receipt_id")


def _build_stage_receipts(
    state: DisabledSelectedMeaningCloseoutState,
    invocation: SelectedMeaningCloseoutInvocation,
    fixture: SelectedMeaningCloseoutFixture,
    integration_input: MsmSelectedMeaningIntegrationInput,
    integration_result: MsmSelectedMeaningIntegrationResult,
    acceptance_record: Slice41AcceptanceRecord,
    rollback_metadata: Slice41RollbackMetadata,
) -> tuple[Slice41CloseoutStageReceipt, ...]:
    gate_result = integration_input.source_gate_integration_result
    construction_input = integration_input.selected_meaning_construction_input
    construction_package = integration_input.selected_meaning_package
    eligibility_input = construction_input.eligibility_evaluation_input
    eligibility_result = construction_input.eligibility_result

    receipts = (
        _stage_receipt(
            Slice41CloseoutStage.ISOLATED_BOOTSTRAP_BOUNDARY,
            1,
            (state.state_id, invocation.invocation_id, fixture.fixture_id),
            (integration_input.integration_input_id,),
        ),
        _stage_receipt(
            Slice41CloseoutStage.ACCEPTED_SLICE40H_GATE_CUSTODY,
            2,
            (
                gate_result.result_id,
                gate_result.companion.companion_id,
            ),
            (
                gate_result.successor_manifest_id,
                gate_result.companion.composition_result_id,
            ),
        ),
        _stage_receipt(
            Slice41CloseoutStage.ACCEPTED_SLICE41C_SELECTION_ELIGIBILITY,
            3,
            (eligibility_input.evaluation_input_id,),
            (eligibility_result.result_id,),
        ),
        _stage_receipt(
            Slice41CloseoutStage.ACCEPTED_SLICE41D_SELECTED_MEANING,
            4,
            (construction_input.construction_input_id,),
            (
                construction_package.package_id,
                construction_package.selection_receipt.receipt_id,
            ),
        ),
        _stage_receipt(
            Slice41CloseoutStage.ACCEPTED_SLICE41E_MSM_INTEGRATION,
            5,
            (integration_input.integration_input_id,),
            (
                integration_result.result_id,
                integration_result.successor_manifest.manifest_id,
                integration_result.companion.companion_id,
                integration_result.receipt.receipt_id,
            ),
        ),
        _stage_receipt(
            Slice41CloseoutStage.SLICE41_CLOSEOUT,
            6,
            (
                integration_result.receipt.receipt_id,
                rollback_metadata.metadata_id,
            ),
            (acceptance_record.record_id,),
        ),
    )
    assert tuple(item.stage for item in receipts) == EXPECTED_STAGE_CHAIN
    return receipts


def _unresolved_outcome_count(
    integration_input: MsmSelectedMeaningIntegrationInput,
) -> int:
    return sum(
        1
        for item in integration_input.source_manifest.non_selection_outcomes
        if item.outcome_kind is NonSelectionOutcomeKind.UNRESOLVED
    )


def _input_matches_fixture(
    fixture: SelectedMeaningCloseoutFixture,
    integration_input: object,
) -> bool:
    if type(integration_input) is not MsmSelectedMeaningIntegrationInput:
        return False
    report = validate_integration_input(integration_input)
    if not report.ok:
        return False
    package = integration_input.selected_meaning_package
    source = integration_input.source_manifest
    candidate_refs = tuple(item.record_id for item in source.candidate_meanings)
    outcome_refs = tuple(item.record_id for item in source.non_selection_outcomes)
    return all(
        (
            integration_input.integration_input_id
            == fixture.expected_integration_input_id,
            source.manifest_id == fixture.expected_source_manifest_id,
            canonical_manifest_sha256(source)
            == fixture.expected_source_manifest_sha256,
            package.selected_candidate_record.record_id
            == fixture.expected_selected_candidate_ref,
            package.selection_receipt.receipt_id
            == fixture.expected_selection_receipt_ref,
            candidate_refs == fixture.expected_candidate_refs,
            outcome_refs == fixture.expected_non_selection_outcome_refs,
            len(source.candidate_meanings)
            == fixture.expected_source_candidate_count,
            len(source.non_selection_outcomes)
            == fixture.expected_source_non_selection_count,
            _unresolved_outcome_count(integration_input)
            == fixture.expected_unresolved_outcome_count,
            package.every_non_selected_candidate_preserved is True,
            package.unresolved_alternatives_preserved_separately is True,
            package.alternatives_erased is False,
            package.msm_v1_modified is False,
            package.governed_outward_meaning_created is False,
            package.bootstrap_integration_enabled is False,
        )
    )


def _result_matches_fixture(
    fixture: SelectedMeaningCloseoutFixture,
    integration_input: MsmSelectedMeaningIntegrationInput,
    integration_result: MsmSelectedMeaningIntegrationResult,
) -> bool:
    report = validate_integration_result(
        integration_result,
        integration_input=integration_input,
    )
    if not report.ok:
        return False
    successor = integration_result.successor_manifest
    source = integration_input.source_manifest
    candidate_refs = tuple(item.record_id for item in successor.candidate_meanings)
    outcome_refs = tuple(item.record_id for item in successor.non_selection_outcomes)
    unresolved_count = sum(
        1
        for item in successor.non_selection_outcomes
        if item.outcome_kind is NonSelectionOutcomeKind.UNRESOLVED
    )
    return all(
        (
            integration_result.result_id
            == fixture.expected_integration_result_id,
            integration_result.canonical_digest
            == fixture.expected_integration_result_digest,
            successor.manifest_id == fixture.expected_successor_manifest_id,
            integration_result.receipt.successor_manifest_sha256
            == fixture.expected_successor_manifest_sha256,
            integration_result.integrated_selected_meaning_record.record_id
            == fixture.expected_integrated_selected_meaning_ref,
            integration_result.integrated_selected_meaning_record.selected_candidate_ref
            == fixture.expected_selected_candidate_ref,
            integration_result.receipt.slice41d_selection_receipt_ref
            == fixture.expected_selection_receipt_ref,
            candidate_refs == fixture.expected_candidate_refs,
            outcome_refs == fixture.expected_non_selection_outcome_refs,
            successor.candidate_meanings == source.candidate_meanings,
            successor.non_selection_outcomes == source.non_selection_outcomes,
            len(successor.selected_governed_meanings)
            == fixture.expected_successor_selected_count,
            unresolved_count == fixture.expected_unresolved_outcome_count,
            integration_result.selected_meaning_integrated is True,
            integration_result.all_candidate_meanings_retained is True,
            integration_result.all_non_selection_outcomes_retained is True,
            integration_result.exact_slice40h_custody_preserved is True,
            integration_result.exact_slice41d_package_preserved is True,
            integration_result.msm_schema_modified is False,
            integration_result.governed_outward_meaning_created is False,
            integration_result.expression_link_created is False,
            integration_result.validation_link_created is False,
            integration_result.delivery_link_created is False,
            integration_result.truth_determined is False,
            integration_result.evidence_validated is False,
            integration_result.permission_granted is False,
            integration_result.execution_authorized is False,
            integration_result.route_created is False,
            integration_result.tool_invoked is False,
            integration_result.action_performed is False,
            integration_result.memory_written is False,
            integration_result.rendered is False,
            integration_result.delivered is False,
            integration_result.bootstrap_integration_enabled is False,
        )
    )


def _build_result(
    state: DisabledSelectedMeaningCloseoutState,
    invocation: object,
    fixture: SelectedMeaningCloseoutFixture | None,
    status: Slice41CloseoutStatus,
    reason_code: str,
    *,
    integration_input: MsmSelectedMeaningIntegrationInput | None = None,
    integration_result: MsmSelectedMeaningIntegrationResult | None = None,
) -> DisabledSelectedMeaningCloseoutResult:
    completed = (
        status is Slice41CloseoutStatus.COMPLETED
        and type(invocation) is SelectedMeaningCloseoutInvocation
        and type(fixture) is SelectedMeaningCloseoutFixture
        and type(integration_input) is MsmSelectedMeaningIntegrationInput
        and type(integration_result) is MsmSelectedMeaningIntegrationResult
    )
    rollback_metadata = build_slice41_rollback_metadata()
    acceptance_record = build_slice41_acceptance_record(
        rollback_metadata,
        completed=completed,
    )
    receipts = (
        _build_stage_receipts(
            state,
            invocation,
            fixture,
            integration_input,
            integration_result,
            acceptance_record,
            rollback_metadata,
        )
        if completed
        else ()
    )
    candidate_retained = bool(
        completed and integration_result.all_candidate_meanings_retained
    )
    outcomes_retained = bool(
        completed and integration_result.all_non_selection_outcomes_retained
    )
    alternatives_preserved = bool(
        completed
        and candidate_retained
        and integration_input.selected_meaning_package.every_non_selected_candidate_preserved
        and len(integration_result.successor_manifest.candidate_meanings) > 1
    )
    unresolved_preserved = bool(
        completed
        and outcomes_retained
        and _unresolved_outcome_count(integration_input) > 0
        and sum(
            1
            for item in integration_result.successor_manifest.non_selection_outcomes
            if item.outcome_kind is NonSelectionOutcomeKind.UNRESOLVED
        )
        == _unresolved_outcome_count(integration_input)
    )
    digest = deterministic_digest(
        {
            "state_id": state.state_id,
            "invocation_id": getattr(invocation, "invocation_id", ""),
            "fixture_id": getattr(fixture, "fixture_id", ""),
            "status": status.value,
            "reason_code": reason_code,
            "integration_input_id": getattr(
                integration_input,
                "integration_input_id",
                "",
            ),
            "integration_result_id": getattr(
                integration_result,
                "result_id",
                "",
            ),
            "acceptance_record_id": acceptance_record.record_id,
            "rollback_metadata_id": rollback_metadata.metadata_id,
            "stage_receipt_ids": tuple(item.receipt_id for item in receipts),
        }
    )
    draft = DisabledSelectedMeaningCloseoutResult(
        result_id="placeholder",
        status=status,
        reason_code=reason_code,
        state_id=state.state_id,
        invocation_id=getattr(invocation, "invocation_id", ""),
        fixture_id=getattr(fixture, "fixture_id", ""),
        integration_input=integration_input if completed else None,
        integration_result=integration_result if completed else None,
        stage_receipts=receipts,
        acceptance_record=acceptance_record,
        rollback_metadata=rollback_metadata,
        deterministic_repeat_digest=digest,
        disabled_by_default=True,
        explicitly_invoked=type(invocation) is SelectedMeaningCloseoutInvocation,
        accepted_static_fixture_only=True,
        offline_only=True,
        read_only=True,
        in_memory_only=True,
        deterministic=True,
        exact_stage_chain_complete=(
            completed
            and tuple(item.stage for item in receipts) == EXPECTED_STAGE_CHAIN
        ),
        stage_receipt_count=len(receipts),
        selected_meaning_integrated=bool(
            completed and integration_result.selected_meaning_integrated
        ),
        selected_meaning_bounded_semantic_custody_only=completed,
        candidate_meanings_retained=candidate_retained,
        non_selection_outcomes_retained=outcomes_retained,
        alternatives_preserved=alternatives_preserved,
        unresolved_state_preserved=unresolved_preserved,
        slice40h_custody_preserved=bool(
            completed and integration_result.exact_slice40h_custody_preserved
        ),
        slice41d_construction_preserved=bool(
            completed and integration_result.exact_slice41d_package_preserved
        ),
        slice41e_integration_preserved=completed,
        final_slice41_acceptance_record_created=completed,
        slice42_started=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        outward_expression_authorized=False,
        governed_outward_meaning_created=False,
        expression_link_created=False,
        validation_link_created=False,
        delivery_link_created=False,
        capability_availability_created=False,
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
        delivered=False,
        language_model_used=False,
        embedding_used=False,
        vector_used=False,
        rag_used=False,
        semantic_similarity_used=False,
    )
    return _with_id(
        "slice41f_disabled_selected_meaning_closeout_result",
        draft,
        "result_id",
    )


def run_disabled_selected_meaning_closeout(
    invocation: object = None,
    *,
    state: object = None,
    integration_input: object = None,
) -> DisabledSelectedMeaningCloseoutResult:
    actual_state = (
        build_disabled_selected_meaning_closeout_state()
        if state is None
        else state
    )
    if type(actual_state) is not DisabledSelectedMeaningCloseoutState:
        return _build_result(
            build_disabled_selected_meaning_closeout_state(),
            invocation,
            None,
            Slice41CloseoutStatus.HELD_INVALID_STATE,
            "exact_closeout_state_required",
        )
    if not actual_state.enabled:
        return _build_result(
            actual_state,
            invocation,
            None,
            Slice41CloseoutStatus.REFUSED_DISABLED,
            REASON_DISABLED,
        )
    if (
        type(invocation) is not SelectedMeaningCloseoutInvocation
        or invocation.requested_operation != REQUESTED_OPERATION
        or invocation.explicit_offline_developer_enable is not True
        or invocation.arbitrary_input_carried is not False
    ):
        return _build_result(
            actual_state,
            invocation,
            None,
            Slice41CloseoutStatus.HELD_INVALID_INVOCATION,
            "exact_fixture_invocation_required",
        )
    fixture = get_selected_meaning_closeout_fixture(invocation.fixture_name)
    if (
        fixture is None
        or fixture.fixture_id != invocation.fixture_id
        or not is_exact_accepted_fixture(fixture)
    ):
        return _build_result(
            actual_state,
            invocation,
            fixture,
            Slice41CloseoutStatus.HELD_FIXTURE_NOT_ACCEPTED,
            "exact_accepted_static_fixture_required",
        )
    if not _input_matches_fixture(fixture, integration_input):
        return _build_result(
            actual_state,
            invocation,
            fixture,
            Slice41CloseoutStatus.HELD_INVALID_PREDECESSOR_OUTPUT,
            "exact_accepted_slice41e_integration_input_required",
        )
    assert type(integration_input) is MsmSelectedMeaningIntegrationInput
    try:
        integration_result = integrate_selected_meaning_into_manifest(
            integration_input
        )
    except (TypeError, ValueError, AttributeError, AssertionError):
        return _build_result(
            actual_state,
            invocation,
            fixture,
            Slice41CloseoutStatus.HELD_INVALID_PREDECESSOR_OUTPUT,
            "slice41e_integration_failed_closed",
        )
    if not _result_matches_fixture(
        fixture,
        integration_input,
        integration_result,
    ):
        return _build_result(
            actual_state,
            invocation,
            fixture,
            Slice41CloseoutStatus.HELD_EXPECTATION_MISMATCH,
            "exact_slice41e_fixture_result_mismatch",
        )
    return _build_result(
        actual_state,
        invocation,
        fixture,
        Slice41CloseoutStatus.COMPLETED,
        "slice41f_disabled_fixture_closeout_complete",
        integration_input=integration_input,
        integration_result=integration_result,
    )


__all__ = (
    "EXPECTED_STAGE_CHAIN",
    "build_disabled_selected_meaning_closeout_state",
    "build_selected_meaning_closeout_invocation",
    "build_slice41_acceptance_record",
    "build_slice41_rollback_metadata",
    "run_disabled_selected_meaning_closeout",
)
