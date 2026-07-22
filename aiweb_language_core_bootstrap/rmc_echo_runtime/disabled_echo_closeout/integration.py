"""Explicit accepted-fixture-only Slice 43H integration and closeout."""
from __future__ import annotations

from dataclasses import replace
from typing import Any

from ...meaning_structure_manifest.serialization import canonical_manifest_sha256
from .. import ECHO_DISPOSITION_VALUES
from .. import ACCEPTED_PARENT_HEAD as SLICE43A_ACCEPTED_PARENT_HEAD
from .. import EXPECTED_COMMIT_SUBJECT as SLICE43A_COMMIT_SUBJECT
from ..governed_lifecycle import SLICE43B_ACCEPTED_PARENT_HEAD, SLICE43B_SCHEMA_VERSION
from ..authorized_source_admission import (
    admit_authorized_meaning_and_proposed_expression,
    build_source_admission_request,
)
from ..meaning_preservation_comparison import (
    build_comparison_request,
    compare_meaning_preservation,
)
from ..drift_materiality_classification import (
    build_classification_request,
    classify_drift_and_materiality,
)
from ..echo_disposition import EchoDisposition, build_disposition_request, decide_echo_disposition
from ..msm_echo_validation_integration import build_integration_input, integrate_echo_validation_link
from .authority import (
    PRE_SLICE43_COMMIT, PRE_SLICE43_SUBJECT, PRE_SLICE43_TREE, REASON_DISABLED,
    REQUESTED_OPERATION, SLICE43_ACCEPTED_CHAIN, SLICE43_ACCEPTED_SCOPE,
    SLICE43_DEFERRED_SCOPE, SLICE43_INCREMENT_LABELS,
    SLICE43_PERMANENT_BOUNDARIES, SLICE43_PROHIBITED_AUTHORITY,
    SLICE43G_ACCEPTED_HEAD, SLICE43G_ACCEPTED_SUBJECT, SLICE43G_ACCEPTED_TREE,
    SLICE43H_ACCEPTANCE_RECORD_VERSION, SLICE43H_RECEIPT_VERSION,
    SLICE43H_ROLLBACK_METADATA_VERSION,
)
from .canonical import deterministic_digest, stable_identifier
from .fixtures import get_echo_closeout_fixture, is_exact_accepted_fixture
from .schema import (
    DisabledEchoCloseoutResult, DisabledEchoCloseoutState, EchoCloseoutFixture,
    EchoCloseoutInvocation, Slice43AcceptanceRecord, Slice43CloseoutStage,
    Slice43CloseoutStageReceipt, Slice43CloseoutStatus, Slice43RollbackMetadata,
)

EXPECTED_STAGE_CHAIN=(
    Slice43CloseoutStage.ISOLATED_BOOTSTRAP_BOUNDARY,
    Slice43CloseoutStage.ACCEPTED_SLICE43A_SCHEMA_AUTHORITY,
    Slice43CloseoutStage.ACCEPTED_SLICE43B_VALIDATION_LIFECYCLE,
    Slice43CloseoutStage.ACCEPTED_SLICE43C_SOURCE_ADMISSION,
    Slice43CloseoutStage.ACCEPTED_SLICE43D_PRESERVATION_COMPARISON,
    Slice43CloseoutStage.ACCEPTED_SLICE43E_DRIFT_CLASSIFICATION,
    Slice43CloseoutStage.ACCEPTED_SLICE43F_ECHO_DISPOSITION,
    Slice43CloseoutStage.ACCEPTED_SLICE43G_MSM_CUSTODY,
    Slice43CloseoutStage.SLICE43_CLOSEOUT,
)


def _with_id(namespace: str, value: Any, field: str):
    return replace(value, **{field: stable_identifier(namespace, replace(value, **{field:"pending"}))})


def build_disabled_echo_closeout_state(*, explicit_offline_developer_enable: bool=False) -> DisabledEchoCloseoutState:
    value=DisabledEchoCloseoutState(
        state_id="pending", enabled=explicit_offline_developer_enable,
        explicit_offline_developer_enable=explicit_offline_developer_enable,
        disabled_by_default=True, explicit_invocation_required=True,
        accepted_static_fixture_only=True, offline_only=True, read_only=True,
        in_memory_only=True, deterministic=True, exact_profile_bounded=True,
        source_preserving=True, rollback_safe=True,
        automatic_activation_allowed=False, arbitrary_input_allowed=False,
        route_allowed=False, api_allowed=False, network_allowed=False,
        filesystem_read_allowed=False, filesystem_write_allowed=False,
        memory_read_allowed=False, memory_write_allowed=False, tool_allowed=False,
        action_allowed=False, rendering_allowed=False, delivery_allowed=False,
        echoforge_allowed=False, llm_allowed=False, truth_authority_allowed=False,
        evidence_authority_allowed=False, permission_authority_allowed=False,
        execution_authority_allowed=False, slice44_allowed=False,
    )
    return _with_id("slice43h_disabled_echo_closeout_state",value,"state_id")


def build_echo_closeout_invocation(fixture_name: str) -> EchoCloseoutInvocation | None:
    fixture=get_echo_closeout_fixture(fixture_name)
    if fixture is None: return None
    value=EchoCloseoutInvocation(
        invocation_id="pending", fixture_id=fixture.fixture_id,
        fixture_name=fixture.fixture_name, requested_operation=REQUESTED_OPERATION,
        explicit_offline_developer_enable=True, arbitrary_input_carried=False,
    )
    return _with_id("slice43h_echo_closeout_invocation",value,"invocation_id")


def build_slice43_rollback_metadata() -> Slice43RollbackMetadata:
    value=Slice43RollbackMetadata(
        metadata_id="pending", metadata_version=SLICE43H_ROLLBACK_METADATA_VERSION,
        pre_slice43_commit=PRE_SLICE43_COMMIT, pre_slice43_tree=PRE_SLICE43_TREE,
        pre_slice43_subject=PRE_SLICE43_SUBJECT,
        accepted_slice43g_head=SLICE43G_ACCEPTED_HEAD,
        accepted_slice43g_tree=SLICE43G_ACCEPTED_TREE,
        accepted_slice43g_subject=SLICE43G_ACCEPTED_SUBJECT,
        recovery_requires_explicit_operator_action=True,
        complete_history_required=True, exact_tree_recovery_required=True,
        runtime_rollback_performed=False, repository_mutated=False,
    )
    return _with_id("slice43h_rollback_metadata",value,"metadata_id")


def build_slice43_acceptance_record(rollback_metadata: Slice43RollbackMetadata, *, completed: bool) -> Slice43AcceptanceRecord:
    value=Slice43AcceptanceRecord(
        record_id="pending", record_version=SLICE43H_ACCEPTANCE_RECORD_VERSION,
        accepted_increment_labels=SLICE43_INCREMENT_LABELS,
        accepted_chain=SLICE43_ACCEPTED_CHAIN, accepted_scope=SLICE43_ACCEPTED_SCOPE,
        deferred_scope=SLICE43_DEFERRED_SCOPE,
        permanent_boundaries=SLICE43_PERMANENT_BOUNDARIES,
        prohibited_authority=SLICE43_PROHIBITED_AUTHORITY,
        rollback_metadata_ref=rollback_metadata.metadata_id,
        slice43_closed=completed, stop_after_slice43=completed,
        slice43a_through_43h_completed=completed,
        authorized_meaning_required=completed, proposed_expression_required=completed,
        selected_meaning_preserved=completed, scope_preserved=completed,
        certainty_preserved=completed, evidence_status_preserved=completed,
        caveats_preserved=completed, refusal_state_preserved=completed,
        unresolved_conditions_preserved=completed,
        material_drift_rejected_or_contained=completed,
        echoforge_used=False, llm_used=False, delivery_authority=False,
        truth_authority=False, evidence_authority=False, permission_authority=False,
        execution_authority=False, slice44_started=False,
        runtime_self_grants_acceptance=False, production_ready=False,
    )
    return _with_id("slice43_acceptance_record",value,"record_id")


def _stage_receipt(stage: Slice43CloseoutStage, index: int, input_refs: tuple[str,...], output_refs: tuple[str,...]) -> Slice43CloseoutStageReceipt:
    value=Slice43CloseoutStageReceipt(
        receipt_id="pending", receipt_version=SLICE43H_RECEIPT_VERSION,
        stage=stage, stage_index=index, input_refs=input_refs, output_refs=output_refs,
        stage_digest="pending", deterministic=True, source_preserved=True,
        offline_only=True, in_memory_only=True, route_created=False,
        api_created=False, network_accessed=False, filesystem_read_performed=False,
        filesystem_write_performed=False, memory_read_performed=False,
        memory_write_performed=False, tool_invoked=False, action_performed=False,
        rendered=False, delivered=False, echoforge_used=False, llm_used=False,
    )
    digest=deterministic_digest(replace(value,receipt_id="pending",stage_digest="pending"))
    value=replace(value,stage_digest=digest)
    return _with_id("slice43h_stage_receipt",value,"receipt_id")


def _build_stage_receipts(source42h, request_c, result_c, request_d, result_d, request_e, result_e, request_f, result_f, input_g, result_g, acceptance):
    refs=(
        ((source42h.result_id,), ("disabled_offline_fixture_boundary",)),
        ((source42h.result_id,), (SLICE43A_ACCEPTED_PARENT_HEAD,SLICE43A_COMMIT_SUBJECT,*ECHO_DISPOSITION_VALUES)),
        ((SLICE43A_ACCEPTED_PARENT_HEAD,), (SLICE43B_ACCEPTED_PARENT_HEAD,SLICE43B_SCHEMA_VERSION)),
        ((request_c.request_id,), (result_c.admission_result_id,)),
        ((request_d.request_id,result_c.admission_result_id), (result_d.comparison_result_id,)),
        ((request_e.request_id,result_d.comparison_result_id), (result_e.classification_result_id,)),
        ((request_f.request_id,result_e.classification_result_id), (result_f.disposition_result_id,result_f.disposition.value)),
        ((input_g.integration_input_id,result_f.disposition_result_id), (result_g.result_id,result_g.successor_manifest.manifest_id)),
        ((result_g.result_id,), (acceptance.record_id,)),
    )
    return tuple(_stage_receipt(stage,index+1,*refs[index]) for index,stage in enumerate(EXPECTED_STAGE_CHAIN))


def _source_matches_fixture(fixture: EchoCloseoutFixture, source: Any) -> bool:
    try:
        return (
            source.result_id == fixture.expected_source_42h_result_id
            and source.result_digest == fixture.expected_source_42h_result_digest
            and source.acceptance_record.record_id == fixture.expected_source_42h_acceptance_record_id
            and source.integration_input.integration_input_id == fixture.expected_source_42g_input_id
            and source.integration_result.result_id == fixture.expected_source_42g_result_id
            and source.integration_result.result_digest == fixture.expected_source_42g_result_digest
            and source.status.value == "COMPLETED"
            and source.acceptance_record.slice42_closed is True
            and source.acceptance_record.slice43_started is False
        )
    except (AttributeError, TypeError):
        return False


def _chain_matches_fixture(fixture, request_c,result_c,request_d,result_d,request_e,result_e,request_f,result_f,input_g,result_g) -> bool:
    try:
        return (
            request_c.request_id == fixture.expected_43c_request_id
            and result_c.admission_result_id == fixture.expected_43c_result_id
            and result_c.admission_result_digest == fixture.expected_43c_result_digest
            and request_d.request_id == fixture.expected_43d_request_id
            and result_d.comparison_result_id == fixture.expected_43d_result_id
            and result_d.comparison_result_digest == fixture.expected_43d_result_digest
            and result_d.dimension_finding_count == fixture.expected_dimension_finding_count
            and request_e.request_id == fixture.expected_43e_request_id
            and result_e.classification_result_id == fixture.expected_43e_result_id
            and result_e.classification_result_digest == fixture.expected_43e_result_digest
            and result_e.classification_record_count == fixture.expected_classification_record_count
            and request_f.request_id == fixture.expected_43f_request_id
            and result_f.disposition_result_id == fixture.expected_43f_result_id
            and result_f.disposition_result_digest == fixture.expected_43f_result_digest
            and result_f.disposition.value == fixture.expected_43f_disposition
            and input_g.integration_input_id == fixture.expected_43g_input_id
            and result_g.result_id == fixture.expected_43g_result_id
            and result_g.result_digest == fixture.expected_43g_result_digest
            and result_g.source_manifest.manifest_id == fixture.expected_43g_source_manifest_id
            and canonical_manifest_sha256(result_g.source_manifest) == fixture.expected_43g_source_manifest_sha256
            and result_g.successor_manifest.manifest_id == fixture.expected_43g_successor_manifest_id
            and canonical_manifest_sha256(result_g.successor_manifest) == fixture.expected_43g_successor_manifest_sha256
            and result_g.validation_link_record.record_id == fixture.expected_43g_validation_link_id
            and result_g.companion.companion_id == fixture.expected_43g_companion_id
            and result_g.receipt.receipt_id == fixture.expected_43g_receipt_id
            and result_g.validation_disposition is EchoDisposition.PASSED
            and result_g.delivery_link_created is False
            and result_g.delivery_authorized_or_performed is False
        )
    except (AttributeError, TypeError):
        return False


def _identity_body(value: DisabledEchoCloseoutResult) -> dict[str,Any]:
    names=("disabled_by_default","explicitly_invoked","accepted_static_fixture_only","offline_only","read_only","in_memory_only","deterministic","exact_stage_chain_complete","authorized_meaning_required","proposed_expression_required","selected_meaning_preserved","scope_preserved","certainty_preserved","evidence_status_preserved","caveats_preserved","refusal_state_preserved","unresolved_conditions_preserved","material_drift_rejected_or_contained","echoforge_used","llm_used","delivery_authority","truth_authority","evidence_authority","permission_authority","execution_authority","slice44_started","route_api_network_filesystem_memory_tool_action_authority","source_manifest_mutated","delivery_link_created","gp014_superseded")
    return {"status":value.status.value,"reason_code":value.reason_code,"state_id":value.state_id,"invocation_id":value.invocation_id,"fixture_id":value.fixture_id,"source_42h_result":getattr(value.source_42h_result,"result_id",None),"source_admission_result":getattr(value.source_admission_result,"admission_result_id",None),"comparison_result":getattr(value.comparison_result,"comparison_result_id",None),"classification_result":getattr(value.classification_result,"classification_result_id",None),"disposition_result":getattr(value.disposition_result,"disposition_result_id",None),"msm_integration_result":getattr(value.msm_integration_result,"result_id",None),"stage_receipts":[r.receipt_id for r in value.stage_receipts],"acceptance_record":value.acceptance_record.record_id,"rollback_metadata":value.rollback_metadata.metadata_id,"deterministic_repeat_digest":value.deterministic_repeat_digest,"booleans":{name:getattr(value,name) for name in names}}


def _build_result(state, invocation, fixture, status, reason, *, source=None, request_c=None,result_c=None,request_d=None,result_d=None,request_e=None,result_e=None,request_f=None,result_f=None,input_g=None,result_g=None):
    completed=status is Slice43CloseoutStatus.COMPLETED
    rollback=build_slice43_rollback_metadata()
    acceptance=build_slice43_acceptance_record(rollback,completed=completed)
    receipts=() if not completed else _build_stage_receipts(source,request_c,result_c,request_d,result_d,request_e,result_e,request_f,result_f,input_g,result_g,acceptance)
    repeat=deterministic_digest({"source":getattr(source,"result_id",None),"chain":[getattr(x,"request_id",getattr(x,"integration_input_id",None)) for x in (request_c,request_d,request_e,request_f,input_g)],"results":[getattr(x,"admission_result_id",getattr(x,"comparison_result_id",getattr(x,"classification_result_id",getattr(x,"disposition_result_id",getattr(x,"result_id",None))))) for x in (result_c,result_d,result_e,result_f,result_g)],"receipts":[r.receipt_id for r in receipts]})
    value=DisabledEchoCloseoutResult(
        result_id="pending", result_digest="pending", status=status, reason_code=reason,
        state_id=state.state_id, invocation_id=getattr(invocation,"invocation_id",None),
        fixture_id=getattr(fixture,"fixture_id",None), source_42h_result=source,
        source_admission_request=request_c, source_admission_result=result_c,
        comparison_request=request_d, comparison_result=result_d,
        classification_request=request_e, classification_result=result_e,
        disposition_request=request_f, disposition_result=result_f,
        msm_integration_input=input_g, msm_integration_result=result_g,
        stage_receipts=receipts, acceptance_record=acceptance,
        rollback_metadata=rollback, deterministic_repeat_digest=repeat,
        disabled_by_default=True, explicitly_invoked=completed,
        accepted_static_fixture_only=True, offline_only=True, read_only=True,
        in_memory_only=True, deterministic=True,
        exact_stage_chain_complete=completed and tuple(r.stage for r in receipts)==EXPECTED_STAGE_CHAIN,
        stage_receipt_count=len(receipts), authorized_meaning_required=completed,
        proposed_expression_required=completed, selected_meaning_preserved=completed,
        scope_preserved=completed, certainty_preserved=completed,
        evidence_status_preserved=completed, caveats_preserved=completed,
        refusal_state_preserved=completed, unresolved_conditions_preserved=completed,
        material_drift_rejected_or_contained=completed, echoforge_used=False,
        llm_used=False, delivery_authority=False, truth_authority=False,
        evidence_authority=False, permission_authority=False, execution_authority=False,
        slice44_started=False,
        route_api_network_filesystem_memory_tool_action_authority=False,
        source_manifest_mutated=False, delivery_link_created=False,
        gp014_superseded=False,
    )
    digest=deterministic_digest(_identity_body(value))
    return replace(value,result_id=f"slice43h_disabled_echo_closeout_result:{digest}",result_digest=digest)


def run_disabled_echo_closeout(invocation: Any=None, *, state: Any=None, source_42h_result: Any=None) -> DisabledEchoCloseoutResult:
    actual_state=build_disabled_echo_closeout_state() if state is None else state
    if type(actual_state) is not DisabledEchoCloseoutState:
        return _build_result(build_disabled_echo_closeout_state(),invocation,None,Slice43CloseoutStatus.HELD_INVALID_STATE,"exact_closeout_state_required")
    if not actual_state.enabled:
        return _build_result(actual_state,invocation,None,Slice43CloseoutStatus.REFUSED_DISABLED,REASON_DISABLED)
    if type(invocation) is not EchoCloseoutInvocation or invocation.requested_operation != REQUESTED_OPERATION or invocation.explicit_offline_developer_enable is not True or invocation.arbitrary_input_carried is not False:
        return _build_result(actual_state,invocation,None,Slice43CloseoutStatus.HELD_INVALID_INVOCATION,"exact_fixture_invocation_required")
    fixture=get_echo_closeout_fixture(invocation.fixture_name)
    if fixture is None or fixture.fixture_id != invocation.fixture_id or not is_exact_accepted_fixture(fixture):
        return _build_result(actual_state,invocation,fixture,Slice43CloseoutStatus.HELD_FIXTURE_NOT_ACCEPTED,"exact_accepted_static_fixture_required")
    if not _source_matches_fixture(fixture,source_42h_result):
        return _build_result(actual_state,invocation,fixture,Slice43CloseoutStatus.HELD_INVALID_PREDECESSOR_OUTPUT,"exact_accepted_slice42h_result_required",source=source_42h_result)
    try:
        request_c=build_source_admission_request(source_42h_result)
        result_c=admit_authorized_meaning_and_proposed_expression(request_c)
        request_d=build_comparison_request(result_c,source_42h_result)
        result_d=compare_meaning_preservation(request_d,result_c,source_42h_result)
        request_e=build_classification_request(result_d)
        result_e=classify_drift_and_materiality(request_e,result_d)
        request_f=build_disposition_request(result_e)
        result_f=decide_echo_disposition(request_f,result_e)
        input_g=build_integration_input(source_42h_result.integration_input,source_42h_result.integration_result,result_e,result_f)
        result_g=integrate_echo_validation_link(input_g)
    except (TypeError,ValueError,AttributeError,AssertionError):
        return _build_result(actual_state,invocation,fixture,Slice43CloseoutStatus.HELD_INVALID_PREDECESSOR_OUTPUT,"slice43_chain_failed_closed",source=source_42h_result)
    if not _chain_matches_fixture(fixture,request_c,result_c,request_d,result_d,request_e,result_e,request_f,result_f,input_g,result_g):
        return _build_result(actual_state,invocation,fixture,Slice43CloseoutStatus.HELD_EXPECTATION_MISMATCH,"exact_slice43_fixture_result_mismatch",source=source_42h_result,request_c=request_c,result_c=result_c,request_d=request_d,result_d=result_d,request_e=request_e,result_e=result_e,request_f=request_f,result_f=result_f,input_g=input_g,result_g=result_g)
    return _build_result(actual_state,invocation,fixture,Slice43CloseoutStatus.COMPLETED,"slice43h_disabled_fixture_closeout_complete",source=source_42h_result,request_c=request_c,result_c=result_c,request_d=request_d,result_d=result_d,request_e=request_e,result_e=result_e,request_f=request_f,result_f=result_f,input_g=input_g,result_g=result_g)


__all__=("EXPECTED_STAGE_CHAIN","build_disabled_echo_closeout_state","build_echo_closeout_invocation","build_slice43_acceptance_record","build_slice43_rollback_metadata","run_disabled_echo_closeout")
