#!/usr/bin/env python3
"""Structural/live verifier for GP-010B-R1 active Lark/SymPy/Hypothesis integration."""
from __future__ import annotations
import argparse, sys
from pathlib import Path

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--forge-root', default=None); args=ap.parse_args(); root=Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]; sys.path.insert(0,str(root)); gp=root/'rmc_engine_v1/general_pipeline'; checks=[]
    def check(name, ok): checks.append((name,bool(ok)))
    required=['dependency_registry.py','typed_ast.py','safe_solver_adapters.py','capability_services.py','pipeline.py','manifest_contract_v2.py','outcome_contract_v2.py','gp010b_audited_tool_activation.py']
    for name in required: check(f'module present {name}', (gp/name).is_file())
    from rmc_engine_v1.general_pipeline import gp010b_audited_tool_activation as act, learn_and_answer
    from rmc_engine_v1.general_pipeline.dependency_registry import dependency_boundary_contract, active_runtime_dependency_ids, active_testing_dependency_ids
    state=act.activate(); b=dependency_boundary_contract()
    check('exact versions installed', state['installation_exact'])
    check('runtime tool imports are declared', b['third_party_components_imported_for_runtime_service']==['lark==1.3.1','sympy==1.14.0','Pint==0.25.3'])
    check('test tool import is declared', b['third_party_components_imported_for_verification_only']==['hypothesis==6.155.1'])
    check('equation service has bounded tool dependency path', len(active_runtime_dependency_ids('linear_equation_one_unknown'))==5)
    check('capacity service has bounded Pint dependency path', len(active_runtime_dependency_ids('fraction_change_capacity'))==7)
    check('Hypothesis not in answer service path', all('hypothesis' not in d for d in active_runtime_dependency_ids('linear_equation_one_unknown')))
    check('Hypothesis in test path', any('hypothesis' in d for d in active_testing_dependency_ids()))
    typed=(gp/'typed_ast.py').read_text(); solver=(gp/'safe_solver_adapters.py').read_text(); dep=(gp/'dependency_registry.py').read_text(); cap=(gp/'capability_services.py').read_text()
    check('Lark imported by typed AST', 'from lark import Lark' in typed)
    check('SymPy imported by safe solver', 'import sympy as sp' in solver)
    check('SymPy raw parser forbidden by source', 'parse_expr' not in solver and 'sympify' not in solver and 'eval(' not in solver)
    check('audited wheel hashes embedded for Lark', 'c629b661023a014c37da873b4ff58a817398d12635d3bbb2c5a03be7fe5d1e12' in dep)
    check('audited wheel hashes embedded for SymPy', 'e091cc3e99d2141a0ba2847328f5479b05d94a6635cb96148ccb3f34671bd8f5' in dep)
    check('service validates dependency per domain', 'validate_service_dependency_binding(self.dependency_record_ids, self.domain_id)' in cap)
    book='Elementary algebra. To solve an equation, isolate the unknown variable by doing the same operation to both sides. For a*x + b = c, subtract b from both sides then divide by a. This finds the variable that makes the equation true.'
    ans=learn_and_answer(book,'alg','solve 11x + 17 = 105 for x')
    check('live answer delivered', ans.status=='ANSWERED' and '8' in ans.answer_text)
    check('live trace includes Lark AST backend', ans.trace['typed_ast_boundary']['parser_backend']=='lark==1.3.1')
    check('live trace includes SymPy solver backend', ans.trace['safe_solver_adapter_receipt']['solver_backend']=='sympy==1.14.0')
    check('live trace includes delivery authorization', 'delivery_authorization_v2_hash' in ans.trace)
    refuse=learn_and_answer(book,'alg','x + y = 10')
    check('live unsupported input has containment receipt', refuse.status=='REFUSED_UNLEARNED' and 'non_delivery_outcome_v2_hash' in refuse.trace)
    check('no forbidden subsystem writes', not b['writes_memory'] and not b['writes_identity_vault'] and not b['writes_contribution_economy'] and not b['writes_ledgers'] and not b['mints_ct'])
    for name,ok in checks: print(('PASS  ' if ok else 'FAIL  ')+name)
    failed=sum(not ok for _,ok in checks); print(f'\nRESULT: GENERAL-PIPELINE-AUDITED-TOOL-ACTIVATION-BUILD-GP-010B-R1_VERIFY {"PASS" if not failed else "FAIL"}  Total:{len(checks)} Passed:{len(checks)-failed} Failed:{failed}')
    return 1 if failed else 0
if __name__=='__main__': raise SystemExit(main())
