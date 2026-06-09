#!/usr/bin/env python3
"""Supersession behavior tests: GP-007 socket now runs audited Lark/SymPy under GP-010B-R1."""
from __future__ import annotations
import argparse, sys
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--forge-root', default=None); args=ap.parse_args(); root=Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]; sys.path.insert(0,str(root)); checks=[]
    def check(name, ok): checks.append((name,bool(ok)))
    from rmc_engine_v1.general_pipeline import learn_and_answer
    from rmc_engine_v1.general_pipeline import gp010b_audited_tool_activation as activation
    from rmc_engine_v1.general_pipeline.domains_equations import LinearEquationOneUnknownDomain
    from rmc_engine_v1.general_pipeline.typed_ast import inspect_linear_equation_parse, parse_linear_equation_ast, require_ast_for_parsed_question, typed_ast_boundary_contract, TypedASTBoundaryError
    from rmc_engine_v1.general_pipeline.safe_solver_adapters import execute_with_safe_solver_adapter, safe_solver_adapter_boundary_contract, SafeSolverAdapterBoundaryError
    activation.activate()
    ast, receipt=inspect_linear_equation_parse('solve 11x + 17 = 105 for x')
    check('Lark parser accepts supported full equation', ast is not None and receipt.full_input_consumed)
    check('AST declares Lark backend', ast.to_dict()['parser_backend']=='lark==1.3.1')
    check('AST values exact', ast.coefficient==Fraction(11) and ast.constant_offset==Fraction(17) and ast.right_hand_value==Fraction(105))
    check('AST hash bound to receipt', receipt.ast_hash==ast.ast_hash())
    for q in ['x + y = 10','2(x + 3) = 14','x^2 = 9','sin(x) = 1','solve 3x + 5 = 20 for y','3x + 5 = 20 and graph it','3.5x + 2 = 9','0x + 2 = 2']:
        rejected, rr=inspect_linear_equation_parse(q); check(f'Lark refuses {q!r}', rejected is None and rr.status=='REFUSED')
    parsed=LinearEquationOneUnknownDomain().parse('solve 11x + 17 = 105 for x')
    check('parsed payload records Lark backend', parsed.metadata['parser_backend']=='lark==1.3.1')
    check('parsed payload reconstructs AST', require_ast_for_parsed_question(parsed).ast_hash()==ast.ast_hash())
    try: require_ast_for_parsed_question(replace(parsed, quantities={**parsed.quantities, 'c':Fraction(999)})); rejected=False
    except TypedASTBoundaryError: rejected=True
    check('typed AST rejects quantity tamper', rejected)
    adapter, executed_ast, solution, solver_receipt=execute_with_safe_solver_adapter(parsed)
    check('SymPy adapter solves unseen equation', solution.answer_value==Fraction(8) and solution.verified)
    check('receipt declares SymPy backend', solver_receipt.solver_backend=='sympy==1.14.0')
    check('receipt carries SymPy equation proof', 'Eq(11*x + 17, 105)' == solver_receipt.sympy_equation_repr)
    check('receipt binds AST hash', solver_receipt.typed_ast_hash==executed_ast.ast_hash())
    try: replace(solver_receipt, typed_ast_payload={**solver_receipt.typed_ast_payload, 'coefficient':'999'}); rejected=False
    except SafeSolverAdapterBoundaryError: rejected=True
    check('solver receipt rejects AST tamper', rejected)
    book='Elementary algebra. To solve an equation, isolate the unknown variable by doing the same operation to both sides. For a*x + b = c, subtract b from both sides then divide by a. This finds the variable that makes the equation true.'
    result=learn_and_answer(book,'alg','solve 11x + 17 = 105 for x')
    check('pipeline delivers verified answer', result.status=='ANSWERED' and 'The answer is 8.' in result.answer_text)
    check('pipeline stores SymPy receipt', result.trace['safe_solver_adapter_receipt']['solver_backend']=='sympy==1.14.0')
    check('Manifest v2 still present', 'manifest_contract_v2' in result.trace)
    check('Echo still approves delivery', result.trace['echo']['approved_output'] is True)
    pb=typed_ast_boundary_contract(); sb=safe_solver_adapter_boundary_contract()
    check('boundary truthfully names Lark', pb['third_party_parser_imported'] is True and pb['parser_backend']=='lark==1.3.1')
    check('boundary truthfully names SymPy', sb['third_party_solver_imported'] is True and sb['solver_backend']=='sympy==1.14.0')
    check('raw expression evaluation prohibited', pb['raw_expression_eval_allowed'] is False and sb['adapter_accepts_raw_user_expression'] is False)
    check('no new domain or persistence', not pb['adds_new_domain'] and not sb['writes_memory'] and not sb['writes_identity_vault'] and not sb['mints_ct'])
    for name, ok in checks: print(('PASS  ' if ok else 'FAIL  ')+name)
    failed=sum(not ok for _,ok in checks); print(f'\nRESULT: GP-007_SUPERSEDED_BY_GP-010B-R1_LARK_SYMPY_BEHAVIOR {"PASS" if not failed else "FAIL"}  Total:{len(checks)} Passed:{len(checks)-failed} Failed:{failed}')
    return 1 if failed else 0
if __name__=='__main__': raise SystemExit(main())
