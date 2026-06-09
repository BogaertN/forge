#!/usr/bin/env python3
"""Read-only verification of GP-006 registry supersession by GP-010B-R1."""
from __future__ import annotations
import argparse, sys
from pathlib import Path

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--forge-root', default=None); args=ap.parse_args(); root=Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]; sys.path.insert(0,str(root)); gp=root/'rmc_engine_v1/general_pipeline'; checks=[]
    def check(name, ok): checks.append((name,bool(ok)))
    from rmc_engine_v1.general_pipeline import gp010b_audited_tool_activation as act
    from rmc_engine_v1.general_pipeline.dependency_registry import dependency_boundary_contract, dependency_registry_hash, active_runtime_dependency_ids
    state=act.activate(); boundary=dependency_boundary_contract()
    for name in ['dependency_registry.py','typed_ast.py','safe_solver_adapters.py','gp010b_audited_tool_activation.py']:
        check(f'module present {name}', (gp/name).is_file())
    check('status registry hash stable', state['dependency_registry_hash']==dependency_registry_hash())
    check('review-only state explicitly superseded', boundary['supersedes_gp006_review_only_boundary'] is True)
    check('Lark and SymPy active in equation socket', len(active_runtime_dependency_ids('linear_equation_one_unknown'))==5)
    check('raw text barred from SymPy', boundary['raw_user_text_sent_to_sympy'] is False)
    dep=(gp/'dependency_registry.py').read_text(); typed=(gp/'typed_ast.py').read_text(); solver=(gp/'safe_solver_adapters.py').read_text()
    check('registry binds Lark audited hash', 'c629b661023a014c37da873b4ff58a817398d12635d3bbb2c5a03be7fe5d1e12' in dep)
    check('registry binds SymPy audited hash', 'e091cc3e99d2141a0ba2847328f5479b05d94a6635cb96148ccb3f34671bd8f5' in dep)
    check('Lark is actual parser import', 'from lark import Lark' in typed)
    check('SymPy is actual solver import', 'import sympy as sp' in solver)
    check('SymPy never parses raw text', 'parse_expr' not in solver and 'sympify' not in solver)
    check('no state/economy permission', not boundary['writes_memory'] and not boundary['writes_identity_vault'] and not boundary['writes_contribution_economy'] and not boundary['mints_ct'])
    for n,o in checks: print(('PASS  ' if o else 'FAIL  ')+n)
    failed=sum(not o for _,o in checks); print(f'\nRESULT: GP-006_SUPERSESSION_GP-010B-R1_VERIFY {"PASS" if not failed else "FAIL"}  Total:{len(checks)} Passed:{len(checks)-failed} Failed:{failed}')
    return 1 if failed else 0
if __name__=='__main__': raise SystemExit(main())
