#!/usr/bin/env python3
"""Read-only structural verification of GP-007 socket after GP-010B-R1 tool activation."""
from __future__ import annotations
import argparse, sys
from pathlib import Path

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--forge-root', default=None); args=ap.parse_args(); root=Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]; sys.path.insert(0,str(root)); gp=root/'rmc_engine_v1/general_pipeline'; checks=[]
    def check(name, ok): checks.append((name,bool(ok)))
    from rmc_engine_v1.general_pipeline import gp010b_audited_tool_activation as activation
    from rmc_engine_v1.general_pipeline.typed_ast import inspect_linear_equation_parse, typed_ast_boundary_contract
    from rmc_engine_v1.general_pipeline.safe_solver_adapters import safe_solver_adapter_boundary_contract
    from rmc_engine_v1.general_pipeline import learn_and_answer
    state=activation.activate(); pb=typed_ast_boundary_contract(); sb=safe_solver_adapter_boundary_contract()
    check('tool installation exact', state['installation_exact'])
    check('Lark parser imported and declared', pb['parser_backend']=='lark==1.3.1' and pb['third_party_parser_imported'])
    check('SymPy solver imported and declared', sb['solver_backend']=='sympy==1.14.0' and sb['third_party_solver_imported'])
    check('Lark rejects multiple-variable equation', inspect_linear_equation_parse('x + y = 10')[0] is None)
    check('Lark rejects unsupported parentheses', inspect_linear_equation_parse('2(x + 3) = 14')[0] is None)
    typed=(gp/'typed_ast.py').read_text(); solver=(gp/'safe_solver_adapters.py').read_text(); services=(gp/'capability_services.py').read_text()
    check('source imports Lark', 'from lark import Lark' in typed)
    check('source imports SymPy', 'import sympy as sp' in solver)
    check('solver source contains no raw parse call', 'parse_expr' not in solver and 'sympify' not in solver and 'eval(' not in solver)
    check('service validates per-domain dependency bindings', 'validate_service_dependency_binding(self.dependency_record_ids, self.domain_id)' in services)
    book='Elementary algebra. To solve an equation, isolate the unknown variable by doing the same operation to both sides. For a*x + b = c, subtract b from both sides then divide by a. This finds the variable that makes the equation true.'
    result=learn_and_answer(book,'alg','solve 11x + 17 = 105 for x')
    check('live trace records parser backend', result.trace['parsed_question']['metadata']['parser_backend']=='lark==1.3.1')
    check('live trace records solver backend', result.trace['safe_solver_adapter_receipt']['solver_backend']=='sympy==1.14.0')
    check('live trace reaches Manifest Contract v2', 'manifest_contract_v2_hash' in result.trace)
    check('live trace reaches Echo authorization', result.trace['echo']['approved_output'] is True)
    check('no memory/identity/economy authority', not sb['writes_memory'] and not sb['writes_identity_vault'] and not sb['writes_contribution_economy'] and not sb['mints_ct'])
    for n,o in checks: print(('PASS  ' if o else 'FAIL  ')+n)
    failed=sum(not o for _,o in checks); print(f'\nRESULT: GP-007_SUPERSESSION_GP-010B-R1_VERIFY {"PASS" if not failed else "FAIL"}  Total:{len(checks)} Passed:{len(checks)-failed} Failed:{failed}')
    return 1 if failed else 0
if __name__=='__main__': raise SystemExit(main())
