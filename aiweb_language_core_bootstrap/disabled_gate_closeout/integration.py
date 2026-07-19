"""Explicit disabled-bootstrap Slice 40 closeout integration."""
from __future__ import annotations
from dataclasses import asdict, replace
import hashlib, json
from ..schema import stable_record_id
from ..msm_gate_custody import integrate_gate_results_into_manifest
from .fixtures import get_gate_closeout_fixture, is_exact_accepted_fixture
from .schema import *

REQUESTED_OPERATION='integrate_accepted_slice40_gate_results_and_close_slice40'

def _id(namespace,value,field):
    body=asdict(value); body.pop(field,None); return replace(value,**{field:stable_record_id(namespace,body)})

def build_disabled_gate_closeout_state(*, explicit_offline_developer_enable=False):
    enabled=explicit_offline_developer_enable is True
    return _id('slice40h_closeout_state', DisabledGateCloseoutState(
        state_id='', enabled=enabled,
        explicit_offline_developer_enable=enabled,
        disabled_by_default=True, accepted_static_fixture_only=True,
        explicit_invocation_required=True, offline_only=True, read_only=True,
        in_memory_only=True, deterministic=True, route_allowed=False,
        api_allowed=False, network_allowed=False, filesystem_write_allowed=False,
        memory_write_allowed=False, tool_allowed=False, action_allowed=False,
        rendering_allowed=False, delivery_allowed=False,
        selected_meaning_allowed=False, slice41_allowed=False,
    ), 'state_id')

def build_gate_closeout_invocation(fixture_name):
    fixture=get_gate_closeout_fixture(fixture_name)
    if fixture is None: return None
    return _id('slice40h_closeout_invocation',GateCloseoutInvocation(
        '',fixture.fixture_id,fixture.fixture_name,REQUESTED_OPERATION,True), 'invocation_id')

def build_slice40_acceptance_record():
    return _id('slice40_acceptance_record',Slice40AcceptanceRecord(
        '',SLICE40_INCREMENT_LABELS,SLICE40_ACCEPTED_SCOPE,SLICE40_DEFERRED_SCOPE,
        True,False,True,False,False), 'record_id')

def _result(state,invocation,fixture,status,reason,integration=None):
    acceptance=build_slice40_acceptance_record()
    digest=hashlib.sha256(json.dumps({
        'state':state.state_id,'invocation':getattr(invocation,'invocation_id',''),
        'fixture':getattr(fixture,'fixture_id',''),'integration':getattr(integration,'result_id',''),
        'status':status,'reason':reason},sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return _id('slice40h_closeout_result', DisabledGateCloseoutResult(
        result_id='', status=status, reason_code=reason, state_id=state.state_id,
        invocation_id=getattr(invocation,'invocation_id',''),
        fixture_id=getattr(fixture,'fixture_id',''), integration_result=integration,
        acceptance_record=acceptance, deterministic_repeat_digest=digest,
        disabled_by_default=True, explicitly_invoked=invocation is not None,
        fixture_only=True, offline_only=True, read_only=True, in_memory_only=True,
        slice40_closeout_created=status=='COMPLETED', slice41_started=False,
        stop_after_slice40=True, selected_meaning_created=False,
        truth_determined=False, evidence_validated=False, permission_granted=False,
        execution_authorized=False, route_created=False, tool_invoked=False,
        action_performed=False, memory_accessed=False, memory_written=False,
        rendered=False, delivered=False,
    ), 'result_id')

def run_disabled_gate_closeout(invocation=None, *, state=None, manifest=None, manifest_candidate_ref='', expectancy=None, congruity=None, connectedness=None, recoverable_purpose=None, composition=None):
    state=build_disabled_gate_closeout_state() if state is None else state
    if type(state) is not DisabledGateCloseoutState: return _result(build_disabled_gate_closeout_state(),invocation,None,'HELD_INVALID_STATE','exact_state_required')
    if not state.enabled: return _result(state,invocation,None,'REFUSED_DISABLED','explicit_offline_developer_enable_required')
    if type(invocation) is not GateCloseoutInvocation or invocation.requested_operation!=REQUESTED_OPERATION:
        return _result(state,invocation,None,'HELD_INVALID_INVOCATION','exact_fixture_invocation_required')
    fixture=get_gate_closeout_fixture(invocation.fixture_name)
    if fixture is None or fixture.fixture_id!=invocation.fixture_id or not is_exact_accepted_fixture(fixture):
        return _result(state,invocation,fixture,'HELD_FIXTURE_NOT_ACCEPTED','exact_static_fixture_required')
    try:
        actual=tuple(x.disposition_kind.value for x in composition.dispositions)
        if actual != fixture.expected_disposition_kinds: return _result(state,invocation,fixture,'HELD_EXPECTATION_MISMATCH','exact_disposition_fixture_mismatch')
        integration=integrate_gate_results_into_manifest(manifest,manifest_candidate_ref,expectancy,congruity,connectedness,recoverable_purpose,composition)
        if integration.projected_outcome_count!=fixture.expected_projected_outcome_count or integration.companion_only_count!=fixture.expected_companion_only_count:
            return _result(state,invocation,fixture,'HELD_EXPECTATION_MISMATCH','exact_projection_expectation_mismatch',integration)
        return _result(state,invocation,fixture,'COMPLETED','slice40h_disabled_fixture_closeout_complete',integration)
    except (TypeError,ValueError,AttributeError):
        return _result(state,invocation,fixture,'HELD_INVALID_PREDECESSOR_OUTPUT','exact_accepted_slice40_results_required')
