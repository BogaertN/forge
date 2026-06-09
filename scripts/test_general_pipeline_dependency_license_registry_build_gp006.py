#!/usr/bin/env python3
"""Supersession behavior tests for GP-006 authority after GP-010B-R1 activation."""
from __future__ import annotations
import argparse, sys
from pathlib import Path

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--forge-root', default=None); args=ap.parse_args()
    root=Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]; sys.path.insert(0,str(root))
    from rmc_engine_v1.general_pipeline import learn_and_answer
    from rmc_engine_v1.general_pipeline import gp010b_audited_tool_activation as act
    from rmc_engine_v1.general_pipeline.dependency_registry import all_dependency_records, dependency_boundary_contract, active_runtime_dependency_ids, active_testing_dependency_ids, dependency_records_for_ids, CANDIDATE_REVIEW, HOLD_LICENSE
    state=act.activate(); checks=[]
    def check(name, ok): checks.append((name,bool(ok)))
    records=all_dependency_records(); boundary=dependency_boundary_contract()
    check('activation has exact installed versions', state['installation_exact'])
    check('Lark version installed', state['installed_versions']['lark']=='1.3.1')
    check('SymPy version installed', state['installed_versions']['sympy']=='1.14.0')
    check('Hypothesis version installed', state['installed_versions']['hypothesis']=='6.155.1')
    check('equation service binds five dependencies', len(active_runtime_dependency_ids('linear_equation_one_unknown'))==5)
    check('capacity service binds governed Pint dependency path', len(active_runtime_dependency_ids('fraction_change_capacity'))==7)
    check('ordinary services retain base dependencies', len(active_runtime_dependency_ids())==2)
    check('test authority binds Hypothesis support only', len(active_testing_dependency_ids())==2)
    check('service dependencies authorized', all(r.service_binding_allowed for r in dependency_records_for_ids(active_runtime_dependency_ids('linear_equation_one_unknown'))))
    check('test dependencies not answer-service bound', all(not r.service_binding_allowed for r in dependency_records_for_ids(active_testing_dependency_ids())))
    check('remaining candidates are non-executable', all(not r.runtime_use_allowed for r in records if r.review_status==CANDIDATE_REVIEW))
    check('license holds remain blocked', all(not r.runtime_use_allowed for r in records if r.review_status==HOLD_LICENSE))
    check('boundary declares installed tools', boundary['third_party_components_installed']==['lark==1.3.1','sympy==1.14.0','hypothesis==6.155.1','mpmath==1.3.0','sortedcontainers==2.4.0','Pint==0.25.3','flexcache==0.3','flexparser==0.4','platformdirs==4.10.0'])
    check('boundary declares runtime service tools', boundary['third_party_components_imported_for_runtime_service']==['lark==1.3.1','sympy==1.14.0','Pint==0.25.3'])
    check('boundary forbids raw SymPy text', boundary['raw_user_text_sent_to_sympy'] is False)
    book='Elementary algebra. To solve an equation, isolate the unknown variable by doing the same operation to both sides. For a*x + b = c, subtract b from both sides then divide by a. This finds the variable that makes the equation true.'
    result=learn_and_answer(book,'alg','solve 11x + 17 = 105 for x')
    check('equation answers under activated dependencies', result.status=='ANSWERED' and '8' in result.answer_text)
    trace=result.trace
    dep_ids=[r['dependency_id'] for r in trace['active_dependency_records']]
    check('equation trace binds Lark', any('lark' in d for d in dep_ids))
    check('equation trace binds SymPy', any('sympy' in d for d in dep_ids))
    check('equation trace binds mpmath support', any('mpmath' in d for d in dep_ids))
    check('equation trace excludes Hypothesis answer binding', all('hypothesis' not in d for d in dep_ids))
    capacity_book='Fractions and capacity: when part of a full container is removed, the change in the fraction full equals the amount removed divided by the whole capacity.'
    capacity=learn_and_answer(capacity_book,'cap','A tank was 3/4 full. After 21 liters were removed, it was 1/2 full. What is the full capacity of the tank in milliliters?')
    check('capacity answers under activated Pint dependency', capacity.status=='ANSWERED' and '84000 milliliters' in capacity.answer_text)
    check('capacity trace binds Pint', capacity.trace['safe_quantity_adapter_receipt']['quantity_backend']=='pint==0.25.3')
    check('Echo remains final gate', trace['echo']['approved_output'] is True)
    check('no memory write', boundary['writes_memory'] is False)
    check('no Identity Vault write', boundary['writes_identity_vault'] is False)
    check('no economy or CT action', boundary['writes_contribution_economy'] is False and boundary['mints_ct'] is False)
    for name, ok in checks: print(('PASS  ' if ok else 'FAIL  ')+name)
    failed=sum(not ok for _,ok in checks); print(f'\nRESULT: GP-006_SUPERSEDED_BY_GP-010B-R1_AUTHORITY_TEST {"PASS" if not failed else "FAIL"}  Total:{len(checks)} Passed:{len(checks)-failed} Failed:{failed}')
    return 1 if failed else 0
if __name__=='__main__': raise SystemExit(main())
