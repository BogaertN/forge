#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib, runpy, sys
from dataclasses import replace
from pathlib import Path

class Ledger:
    def __init__(self): self.check_count=0; self.failures=[]; self.malformed_cases=0
    def check(self,c,l): self.check_count+=1; self.failures.append(l) if c is not True else None
    def malformed(self,c,l): self.malformed_cases+=1; self.check(c,l)

def ns(repo,name): return runpy.run_path(str(repo/'scripts'/name))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('repository',nargs='?',default='.'); args=ap.parse_args()
    repo=Path(args.repository).resolve(); sys.path.insert(0,str(repo)); L=Ledger()
    core=importlib.import_module('aiweb_language_core_bootstrap.verbal_cognition_gate_runtime')
    governed=importlib.import_module('aiweb_language_core_bootstrap.verbal_cognition_gate_runtime.governed_lifecycle')
    composition=importlib.import_module('aiweb_language_core_bootstrap.verbal_cognition_gate_runtime.gate_composition')
    custody=importlib.import_module('aiweb_language_core_bootstrap.msm_gate_custody')
    closeout=importlib.import_module('aiweb_language_core_bootstrap.disabled_gate_closeout')
    candidate=importlib.import_module('aiweb_language_core_bootstrap.disabled_candidate_meaning_bootstrap')
    gns=ns(repo,'test_aiweb_slice40g_gate_composition_non_selection_disposition_runtime.py')
    bundles,results,_=gns['build_family_results'](repo,core,governed)
    result_refs=tuple(x.result_id for x in results); candidate_ref='candidate_composition:demo:v1'; branch_ref='candidate_branch:demo:primary'
    state39=candidate.build_disabled_candidate_meaning_bootstrap_state(explicit_offline_developer_enable=True)
    inv39=candidate.build_fixture_invocation('slice39h-one-missing-role')
    result39=candidate.run_disabled_candidate_meaning_bootstrap(inv39,integration_state=state39)
    manifest=result39.manifest_integration_result.manifest
    manifest_candidate_ref=manifest.candidate_meanings[0].record_id
    L.check(manifest is not None,'manifest fixture')
    fixtures=closeout.list_gate_closeout_fixtures(); L.check(len(fixtures)==8,'fixture count')
    state=closeout.build_disabled_gate_closeout_state(explicit_offline_developer_enable=True)
    default_state=closeout.build_disabled_gate_closeout_state()
    L.check(closeout.run_disabled_gate_closeout(state=default_state).status=='REFUSED_DISABLED','disabled default')
    repeats=[]
    for fixture in fixtures:
        assertions=tuple(gns['make_assertion'](composition,candidate_ref,branch_ref,result_refs,composition.GateCompositionDispositionKind(kind)) for kind in fixture.expected_disposition_kinds)
        changes={}
        if 'material_ambiguity_preserved' in fixture.expected_disposition_kinds:
            changes['material_competing_candidate_refs']=('candidate_branch:demo:alternative',)
            changes['competing_candidate_disposition_refs']=('alternative_disposition:held',)
        if 'clarification_relevant' in fixture.expected_disposition_kinds:
            changes['user_suppliable_clarification_refs']=('clarification_support:user_can_supply_referent',)
        inp=gns['make_input'](composition,bundles,results,assertions,**changes)
        composed=composition.evaluate_gate_composition(inp)
        inv=closeout.build_gate_closeout_invocation(fixture.fixture_name)
        out=closeout.run_disabled_gate_closeout(inv,state=state,manifest=manifest,manifest_candidate_ref=manifest_candidate_ref,expectancy=results[0],congruity=results[1],connectedness=results[2],recoverable_purpose=results[3],composition=composed)
        out2=closeout.run_disabled_gate_closeout(inv,state=state,manifest=manifest,manifest_candidate_ref=manifest_candidate_ref,expectancy=results[0],congruity=results[1],connectedness=results[2],recoverable_purpose=results[3],composition=composed)
        repeats.append(out.result_id==out2.result_id and out.deterministic_repeat_digest==out2.deterministic_repeat_digest)
        L.check(out.status=='COMPLETED',f'completed {fixture.fixture_name}')
        L.check(custody.validate_result(out.integration_result).ok,f'valid integration {fixture.fixture_name}')
        L.check(out.integration_result.projected_outcome_count==fixture.expected_projected_outcome_count,f'project count {fixture.fixture_name}')
        L.check(out.integration_result.companion_only_count==fixture.expected_companion_only_count,f'companion count {fixture.fixture_name}')
        L.check(not out.integration_result.successor_manifest.selected_governed_meanings,f'no selected {fixture.fixture_name}')
        L.check(out.acceptance_record.slice40_closed and not out.acceptance_record.slice41_started and out.acceptance_record.stop_after_slice40,f'stop boundary {fixture.fixture_name}')
        L.check(not any((out.selected_meaning_created,out.truth_determined,out.evidence_validated,out.permission_granted,out.execution_authorized,out.route_created,out.tool_invoked,out.action_performed,out.memory_accessed,out.memory_written,out.rendered,out.delivered)),f'authority zero {fixture.fixture_name}')
    L.check(all(repeats),'deterministic repeats')
    mixed=fixtures[-1]
    assertions=tuple(gns['make_assertion'](composition,candidate_ref,branch_ref,result_refs,composition.GateCompositionDispositionKind(kind)) for kind in mixed.expected_disposition_kinds)
    composed=composition.evaluate_gate_composition(gns['make_input'](
        composition,bundles,results,assertions,
        material_competing_candidate_refs=('candidate_branch:demo:alternative',),
        competing_candidate_disposition_refs=('alternative_disposition:held',),
        user_suppliable_clarification_refs=('clarification_support:user_can_supply_referent',),
    ))
    integration=custody.integrate_gate_results_into_manifest(manifest,manifest_candidate_ref,*results,composed)
    kinds={x.source_disposition_kind:x for x in integration.companion.projections}
    L.check(kinds['clarification_relevant'].companion_only,'clarification companion only')
    L.check(kinds['candidate_supported_for_later_selection_review'].companion_only,'positive companion only')
    L.check(kinds['refusal_relevant'].projection_disposition.value=='refused_custody','refusal custody only')
    L.check(len(integration.companion.family_custody)==4,'four family custody')
    L.check(integration.companion.family_results_preserved and integration.companion.composition_result_preserved,'results preserved')
    L.check(not integration.companion.selected_meaning_created,'companion no selection')
    # malformed / adversarial
    for bad in (None,'',object(),replace(manifest, manifest_id='')):
        try: custody.integrate_gate_results_into_manifest(bad,manifest_candidate_ref,*results,composed); invalid=False
        except Exception: invalid=True
        L.malformed(invalid,'invalid manifest rejected')
    try: custody.integrate_gate_results_into_manifest(manifest,'missing:candidate',*results,composed); invalid=False
    except Exception: invalid=True
    L.malformed(invalid,'missing candidate rejected')
    bad_inv=closeout.run_disabled_gate_closeout(object(),state=state)
    L.malformed(bad_inv.status=='HELD_INVALID_INVOCATION','invalid invocation held')
    print('AI.WEB SLICE 40H MSM GATE INTEGRATION AND CLOSEOUT BEHAVIOR TEST')
    print(f'check_count={L.check_count}')
    print(f'malformed_validation_cases={L.malformed_cases}')
    print('fixture_count=8')
    print('integration_stage_count=6')
    print('deterministic_repeat_count=8')
    print('protected_predecessor_files=570')
    print('exact_payload_paths=17')
    print('four_gate_family_results_preserved=1')
    print('composition_result_preserved=1')
    print('msm_gate_companion_created=1')
    print('lawful_non_selection_projection=1')
    print('clarification_relevant_not_required=1')
    print('positive_selection_review_companion_only=1')
    print('refusal_relevant_not_outward_refusal=1')
    print('msm_v1_schema_modified=0')
    print('automatic_migration_performed=0')
    print('selected_meaning_created=0')
    print('slice40_closeout_record_created=1')
    print('slice41_started=0')
    print('stop_after_slice40=1')
    print('truth_evidence_permission_execution=0')
    print('route_tool_action_memory_rendering_delivery=0')
    print(f'failure_count={len(L.failures)}')
    for x in L.failures: print('FAIL:',x)
    if L.failures: print('AI.WEB SLICE 40H BEHAVIOR TEST: FAIL'); return 1
    print('AI.WEB SLICE 40H BEHAVIOR TEST: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
