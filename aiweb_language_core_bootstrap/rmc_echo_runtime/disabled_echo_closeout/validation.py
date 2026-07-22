"""Deterministic validation for Slice 43H closeout records."""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any

from .authority import (
    PRE_SLICE43_COMMIT, PRE_SLICE43_SUBJECT, PRE_SLICE43_TREE,
    REQUESTED_OPERATION, SLICE43_ACCEPTED_CHAIN, SLICE43_ACCEPTED_SCOPE,
    SLICE43_DEFERRED_SCOPE, SLICE43_INCREMENT_LABELS,
    SLICE43_PERMANENT_BOUNDARIES, SLICE43_PROHIBITED_AUTHORITY,
    SLICE43G_ACCEPTED_HEAD, SLICE43G_ACCEPTED_SUBJECT, SLICE43G_ACCEPTED_TREE,
    SLICE43H_ACCEPTANCE_RECORD_VERSION, SLICE43H_RECEIPT_VERSION,
    SLICE43H_ROLLBACK_METADATA_VERSION, SLICE43H_SCHEMA_VERSION,
)
from .canonical import deterministic_digest, stable_identifier
from .fixtures import is_exact_accepted_fixture
from .schema import (
    DisabledEchoCloseoutResult, DisabledEchoCloseoutState, EchoCloseoutFixture,
    EchoCloseoutInvocation, Slice43AcceptanceRecord, Slice43CloseoutStageReceipt,
    Slice43CloseoutStatus, Slice43RollbackMetadata,
)


class Slice43CloseoutValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    VERSION_MISMATCH = "version_mismatch"
    STATE_MISMATCH = "state_mismatch"
    FIXTURE_MISMATCH = "fixture_mismatch"
    INVOCATION_MISMATCH = "invocation_mismatch"
    PREDECESSOR_MISMATCH = "predecessor_mismatch"
    ACCEPTANCE_MISMATCH = "acceptance_mismatch"
    RECEIPT_MISMATCH = "receipt_mismatch"
    RESULT_MISMATCH = "result_mismatch"
    BOUNDARY_VIOLATION = "boundary_violation"


@dataclass(frozen=True, slots=True)
class Slice43CloseoutValidationIssue:
    path: str
    code: Slice43CloseoutValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class Slice43CloseoutValidationReport:
    issues: tuple[Slice43CloseoutValidationIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues


class Slice43CloseoutValidationError(ValueError):
    pass


def _report(issues):
    return Slice43CloseoutValidationReport(tuple(issues))


def _issue(issues, path, code, detail):
    issues.append(Slice43CloseoutValidationIssue(path, code, detail))


def validate_state(value: Any) -> Slice43CloseoutValidationReport:
    issues=[]
    if type(value) is not DisabledEchoCloseoutState:
        _issue(issues,"state",Slice43CloseoutValidationCode.TYPE_MISMATCH,"exact type required"); return _report(issues)
    wanted=stable_identifier("slice43h_disabled_echo_closeout_state", replace(value,state_id="pending"))
    if value.state_id != wanted: _issue(issues,"state.state_id",Slice43CloseoutValidationCode.IDENTITY_MISMATCH,"deterministic identity mismatch")
    if value.schema_version != SLICE43H_SCHEMA_VERSION: _issue(issues,"state.schema_version",Slice43CloseoutValidationCode.VERSION_MISMATCH,"schema version mismatch")
    for name in ("disabled_by_default","explicit_invocation_required","accepted_static_fixture_only","offline_only","read_only","in_memory_only","deterministic","exact_profile_bounded","source_preserving","rollback_safe"):
        if getattr(value,name) is not True: _issue(issues,f"state.{name}",Slice43CloseoutValidationCode.STATE_MISMATCH,"must be true")
    for name in ("automatic_activation_allowed","arbitrary_input_allowed","route_allowed","api_allowed","network_allowed","filesystem_read_allowed","filesystem_write_allowed","memory_read_allowed","memory_write_allowed","tool_allowed","action_allowed","rendering_allowed","delivery_allowed","echoforge_allowed","llm_allowed","truth_authority_allowed","evidence_authority_allowed","permission_authority_allowed","execution_authority_allowed","slice44_allowed"):
        if getattr(value,name) is not False: _issue(issues,f"state.{name}",Slice43CloseoutValidationCode.BOUNDARY_VIOLATION,"must be false")
    if value.enabled is not value.explicit_offline_developer_enable: _issue(issues,"state.enabled",Slice43CloseoutValidationCode.STATE_MISMATCH,"enable fields must agree")
    return _report(issues)


def validate_fixture(value: Any) -> Slice43CloseoutValidationReport:
    issues=[]
    if type(value) is not EchoCloseoutFixture:
        _issue(issues,"fixture",Slice43CloseoutValidationCode.TYPE_MISMATCH,"exact type required"); return _report(issues)
    if not is_exact_accepted_fixture(value): _issue(issues,"fixture",Slice43CloseoutValidationCode.FIXTURE_MISMATCH,"closed registry membership required")
    if value.schema_version != SLICE43H_SCHEMA_VERSION: _issue(issues,"fixture.schema_version",Slice43CloseoutValidationCode.VERSION_MISMATCH,"schema version mismatch")
    for name in ("accepted_fixture","synthetic","explicit_invocation_only","offline_only","in_memory_only","deterministic"):
        if getattr(value,name) is not True: _issue(issues,f"fixture.{name}",Slice43CloseoutValidationCode.FIXTURE_MISMATCH,"must be true")
    for name in value.__dataclass_fields__:
        if name.startswith("expected_") and (name.endswith("_id") or name.endswith("_digest") or name.endswith("_sha256")) and not getattr(value,name):
            _issue(issues,f"fixture.{name}",Slice43CloseoutValidationCode.FIXTURE_MISMATCH,"non-empty exact value required")
    return _report(issues)


def validate_invocation(value: Any) -> Slice43CloseoutValidationReport:
    issues=[]
    if type(value) is not EchoCloseoutInvocation:
        _issue(issues,"invocation",Slice43CloseoutValidationCode.TYPE_MISMATCH,"exact type required"); return _report(issues)
    wanted=stable_identifier("slice43h_echo_closeout_invocation", replace(value,invocation_id="pending"))
    if value.invocation_id != wanted: _issue(issues,"invocation.invocation_id",Slice43CloseoutValidationCode.IDENTITY_MISMATCH,"deterministic identity mismatch")
    if value.requested_operation != REQUESTED_OPERATION: _issue(issues,"invocation.requested_operation",Slice43CloseoutValidationCode.INVOCATION_MISMATCH,"exact operation required")
    if value.explicit_offline_developer_enable is not True: _issue(issues,"invocation.explicit_offline_developer_enable",Slice43CloseoutValidationCode.INVOCATION_MISMATCH,"explicit enable required")
    if value.arbitrary_input_carried is not False: _issue(issues,"invocation.arbitrary_input_carried",Slice43CloseoutValidationCode.BOUNDARY_VIOLATION,"arbitrary input prohibited")
    if value.schema_version != SLICE43H_SCHEMA_VERSION: _issue(issues,"invocation.schema_version",Slice43CloseoutValidationCode.VERSION_MISMATCH,"schema version mismatch")
    return _report(issues)


def validate_rollback_metadata(value: Any) -> Slice43CloseoutValidationReport:
    issues=[]
    if type(value) is not Slice43RollbackMetadata:
        _issue(issues,"rollback",Slice43CloseoutValidationCode.TYPE_MISMATCH,"exact type required"); return _report(issues)
    wanted=stable_identifier("slice43h_rollback_metadata", replace(value,metadata_id="pending"))
    if value.metadata_id != wanted: _issue(issues,"rollback.metadata_id",Slice43CloseoutValidationCode.IDENTITY_MISMATCH,"identity mismatch")
    expected={"metadata_version":SLICE43H_ROLLBACK_METADATA_VERSION,"pre_slice43_commit":PRE_SLICE43_COMMIT,"pre_slice43_tree":PRE_SLICE43_TREE,"pre_slice43_subject":PRE_SLICE43_SUBJECT,"accepted_slice43g_head":SLICE43G_ACCEPTED_HEAD,"accepted_slice43g_tree":SLICE43G_ACCEPTED_TREE,"accepted_slice43g_subject":SLICE43G_ACCEPTED_SUBJECT}
    for name,wanted_value in expected.items():
        if getattr(value,name) != wanted_value: _issue(issues,f"rollback.{name}",Slice43CloseoutValidationCode.PREDECESSOR_MISMATCH,"exact predecessor metadata required")
    for name in ("recovery_requires_explicit_operator_action","complete_history_required","exact_tree_recovery_required"):
        if getattr(value,name) is not True: _issue(issues,f"rollback.{name}",Slice43CloseoutValidationCode.PREDECESSOR_MISMATCH,"must be true")
    for name in ("runtime_rollback_performed","repository_mutated"):
        if getattr(value,name) is not False: _issue(issues,f"rollback.{name}",Slice43CloseoutValidationCode.BOUNDARY_VIOLATION,"must be false")
    return _report(issues)


def validate_acceptance_record(value: Any) -> Slice43CloseoutValidationReport:
    issues=[]
    if type(value) is not Slice43AcceptanceRecord:
        _issue(issues,"acceptance",Slice43CloseoutValidationCode.TYPE_MISMATCH,"exact type required"); return _report(issues)
    wanted=stable_identifier("slice43_acceptance_record", replace(value,record_id="pending"))
    if value.record_id != wanted: _issue(issues,"acceptance.record_id",Slice43CloseoutValidationCode.IDENTITY_MISMATCH,"identity mismatch")
    if value.record_version != SLICE43H_ACCEPTANCE_RECORD_VERSION: _issue(issues,"acceptance.record_version",Slice43CloseoutValidationCode.VERSION_MISMATCH,"record version mismatch")
    exact={"accepted_increment_labels":SLICE43_INCREMENT_LABELS,"accepted_chain":SLICE43_ACCEPTED_CHAIN,"accepted_scope":SLICE43_ACCEPTED_SCOPE,"deferred_scope":SLICE43_DEFERRED_SCOPE,"permanent_boundaries":SLICE43_PERMANENT_BOUNDARIES,"prohibited_authority":SLICE43_PROHIBITED_AUTHORITY}
    for name,wanted_value in exact.items():
        if getattr(value,name) != wanted_value: _issue(issues,f"acceptance.{name}",Slice43CloseoutValidationCode.ACCEPTANCE_MISMATCH,"exact tuple required")
    if value.slice43_closed:
        for name in ("stop_after_slice43","slice43a_through_43h_completed","authorized_meaning_required","proposed_expression_required","selected_meaning_preserved","scope_preserved","certainty_preserved","evidence_status_preserved","caveats_preserved","refusal_state_preserved","unresolved_conditions_preserved","material_drift_rejected_or_contained"):
            if getattr(value,name) is not True: _issue(issues,f"acceptance.{name}",Slice43CloseoutValidationCode.ACCEPTANCE_MISMATCH,"must be true for closeout")
    for name in ("echoforge_used","llm_used","delivery_authority","truth_authority","evidence_authority","permission_authority","execution_authority","slice44_started","runtime_self_grants_acceptance","production_ready"):
        if getattr(value,name) is not False: _issue(issues,f"acceptance.{name}",Slice43CloseoutValidationCode.BOUNDARY_VIOLATION,"must be false")
    return _report(issues)


def validate_stage_receipt(value: Any) -> Slice43CloseoutValidationReport:
    issues=[]
    if type(value) is not Slice43CloseoutStageReceipt:
        _issue(issues,"receipt",Slice43CloseoutValidationCode.TYPE_MISMATCH,"exact type required"); return _report(issues)
    body=replace(value,receipt_id="pending",stage_digest="pending")
    expected_digest=deterministic_digest(body)
    if value.stage_digest != expected_digest: _issue(issues,"receipt.stage_digest",Slice43CloseoutValidationCode.IDENTITY_MISMATCH,"digest mismatch")
    expected_id=stable_identifier("slice43h_stage_receipt", replace(value,receipt_id="pending"))
    if value.receipt_id != expected_id: _issue(issues,"receipt.receipt_id",Slice43CloseoutValidationCode.IDENTITY_MISMATCH,"identity mismatch")
    if value.receipt_version != SLICE43H_RECEIPT_VERSION: _issue(issues,"receipt.receipt_version",Slice43CloseoutValidationCode.VERSION_MISMATCH,"version mismatch")
    for name in ("deterministic","source_preserved","offline_only","in_memory_only"):
        if getattr(value,name) is not True: _issue(issues,f"receipt.{name}",Slice43CloseoutValidationCode.RECEIPT_MISMATCH,"must be true")
    for name in ("route_created","api_created","network_accessed","filesystem_read_performed","filesystem_write_performed","memory_read_performed","memory_write_performed","tool_invoked","action_performed","rendered","delivered","echoforge_used","llm_used"):
        if getattr(value,name) is not False: _issue(issues,f"receipt.{name}",Slice43CloseoutValidationCode.BOUNDARY_VIOLATION,"must be false")
    return _report(issues)


def validate_result(value: Any) -> Slice43CloseoutValidationReport:
    issues=[]
    if type(value) is not DisabledEchoCloseoutResult:
        _issue(issues,"result",Slice43CloseoutValidationCode.TYPE_MISMATCH,"exact type required"); return _report(issues)
    if value.schema_version != SLICE43H_SCHEMA_VERSION: _issue(issues,"result.schema_version",Slice43CloseoutValidationCode.VERSION_MISMATCH,"schema version mismatch")
    issues.extend(validate_acceptance_record(value.acceptance_record).issues)
    issues.extend(validate_rollback_metadata(value.rollback_metadata).issues)
    for receipt in value.stage_receipts: issues.extend(validate_stage_receipt(receipt).issues)
    if value.stage_receipt_count != len(value.stage_receipts): _issue(issues,"result.stage_receipt_count",Slice43CloseoutValidationCode.RESULT_MISMATCH,"count mismatch")
    for name in ("disabled_by_default","accepted_static_fixture_only","offline_only","read_only","in_memory_only","deterministic"):
        if getattr(value,name) is not True: _issue(issues,f"result.{name}",Slice43CloseoutValidationCode.RESULT_MISMATCH,"must be true")
    for name in ("echoforge_used","llm_used","delivery_authority","truth_authority","evidence_authority","permission_authority","execution_authority","slice44_started","route_api_network_filesystem_memory_tool_action_authority","source_manifest_mutated","delivery_link_created","gp014_superseded"):
        if getattr(value,name) is not False: _issue(issues,f"result.{name}",Slice43CloseoutValidationCode.BOUNDARY_VIOLATION,"must be false")
    if value.status is Slice43CloseoutStatus.COMPLETED:
        if value.stage_receipt_count != 9 or not value.exact_stage_chain_complete: _issue(issues,"result.stage_receipts",Slice43CloseoutValidationCode.RESULT_MISMATCH,"exact nine-stage chain required")
        for name in ("explicitly_invoked","authorized_meaning_required","proposed_expression_required","selected_meaning_preserved","scope_preserved","certainty_preserved","evidence_status_preserved","caveats_preserved","refusal_state_preserved","unresolved_conditions_preserved","material_drift_rejected_or_contained"):
            if getattr(value,name) is not True: _issue(issues,f"result.{name}",Slice43CloseoutValidationCode.RESULT_MISMATCH,"must be true for completed closeout")
        if value.disposition_result is None or getattr(value.disposition_result,"disposition",None).value != "PASSED": _issue(issues,"result.disposition_result",Slice43CloseoutValidationCode.RESULT_MISMATCH,"exact PASSED fixture required")
        if value.msm_integration_result is None or getattr(value.msm_integration_result,"delivery_link_created",True) is not False: _issue(issues,"result.msm_integration_result",Slice43CloseoutValidationCode.BOUNDARY_VIOLATION,"delivery link prohibited")
    body={"status":value.status.value,"reason_code":value.reason_code,"state_id":value.state_id,"invocation_id":value.invocation_id,"fixture_id":value.fixture_id,"stage_receipts":[r.receipt_id for r in value.stage_receipts],"acceptance_record":value.acceptance_record.record_id,"rollback_metadata":value.rollback_metadata.metadata_id,"source_42h_result":getattr(value.source_42h_result,"result_id",None),"source_admission_result":getattr(value.source_admission_result,"admission_result_id",None),"comparison_result":getattr(value.comparison_result,"comparison_result_id",None),"classification_result":getattr(value.classification_result,"classification_result_id",None),"disposition_result":getattr(value.disposition_result,"disposition_result_id",None),"msm_integration_result":getattr(value.msm_integration_result,"result_id",None),"deterministic_repeat_digest":value.deterministic_repeat_digest,"booleans":{name:getattr(value,name) for name in ("disabled_by_default","explicitly_invoked","accepted_static_fixture_only","offline_only","read_only","in_memory_only","deterministic","exact_stage_chain_complete","authorized_meaning_required","proposed_expression_required","selected_meaning_preserved","scope_preserved","certainty_preserved","evidence_status_preserved","caveats_preserved","refusal_state_preserved","unresolved_conditions_preserved","material_drift_rejected_or_contained","echoforge_used","llm_used","delivery_authority","truth_authority","evidence_authority","permission_authority","execution_authority","slice44_started","route_api_network_filesystem_memory_tool_action_authority","source_manifest_mutated","delivery_link_created","gp014_superseded")}}
    digest=deterministic_digest(body)
    if value.result_digest != digest: _issue(issues,"result.result_digest",Slice43CloseoutValidationCode.IDENTITY_MISMATCH,"result digest mismatch")
    if value.result_id != f"slice43h_disabled_echo_closeout_result:{digest}": _issue(issues,"result.result_id",Slice43CloseoutValidationCode.IDENTITY_MISMATCH,"result identity mismatch")
    return _report(issues)


def assert_valid_result(value: Any) -> None:
    report=validate_result(value)
    if not report.ok:
        raise Slice43CloseoutValidationError("; ".join(f"{issue.path}:{issue.code.value}:{issue.detail}" for issue in report.issues))

PUBLIC_VALIDATORS=(validate_state,validate_fixture,validate_invocation,validate_rollback_metadata,validate_acceptance_record,validate_stage_receipt,validate_result)
__all__ = tuple(name for name in globals() if not name.startswith("_"))
