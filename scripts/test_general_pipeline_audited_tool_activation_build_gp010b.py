#!/usr/bin/env python3
"""Behavior + property tests for GP-010B-R1 audited active tools."""
from __future__ import annotations
import argparse, sys
from fractions import Fraction
from pathlib import Path
from hypothesis import given, settings, strategies as st
ALGEBRA = "Elementary algebra. To solve an equation, isolate the unknown variable by doing the same operation to both sides. For a*x + b = c, subtract b from both sides then divide by a. This finds the variable that makes the equation true."

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--forge-root', default=None); args=ap.parse_args(); root=Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]; sys.path.insert(0,str(root)); checks=[]
    def check(name, ok): checks.append((name,bool(ok)))
    from rmc_engine_v1.general_pipeline import learn_and_answer
    from rmc_engine_v1.general_pipeline import gp010b_audited_tool_activation as act
    from rmc_engine_v1.general_pipeline.dependency_registry import active_runtime_dependency_ids, active_testing_dependency_ids, validate_testing_dependency_binding
    from rmc_engine_v1.general_pipeline.typed_ast import inspect_linear_equation_parse
    state=act.activate()
    check('exact dependency versions present', state['installation_exact'])
    check('Lark active version', state['installed_versions']['lark']=='1.3.1')
    check('SymPy active version', state['installed_versions']['sympy']=='1.14.0')
    check('Hypothesis active version', state['installed_versions']['hypothesis']=='6.155.1')
    validate_testing_dependency_binding(active_testing_dependency_ids()); check('Hypothesis testing authority is bounded', True)
    result=learn_and_answer(ALGEBRA,'alg','solve 11x + 17 = 105 for x')
    check('unseen equation answered', result.status=='ANSWERED' and result.trace['solution']['answer_value']=='8')
    check('Lark recorded in AST', result.trace['typed_ast_boundary']['parser_backend']=='lark==1.3.1')
    check('SymPy recorded in receipt', result.trace['safe_solver_adapter_receipt']['solver_backend']=='sympy==1.14.0')
    check('SymPy computed expected symbolic proof', result.trace['safe_solver_adapter_receipt']['sympy_equation_repr']=='Eq(11*x + 17, 105)')
    check('equation service binds audited external dependencies', len(active_runtime_dependency_ids('linear_equation_one_unknown'))==5)
    check('Manifest Contract v2 remains required', 'manifest_contract_v2_hash' in result.trace)
    check('Echo delivery remains required', result.trace['echo']['approved_output'] is True and 'delivery_authorization_v2_hash' in result.trace)
    check('two-variable input refused', learn_and_answer(ALGEBRA,'alg','x + y = 10').status=='REFUSED_UNLEARNED')
    check('quadratic input refused', learn_and_answer(ALGEBRA,'alg','x^2 = 9').status=='REFUSED_UNLEARNED')
    check('trailing instruction refused', learn_and_answer(ALGEBRA,'alg','3x + 5 = 20 and graph it').status=='REFUSED_UNLEARNED')

    coefficients=st.integers(min_value=-50,max_value=50).filter(lambda n:n != 0)
    integers=st.integers(min_value=-250,max_value=250)
    variables=st.sampled_from(['x','y','q','z'])
    @settings(max_examples=120, derandomize=True, deadline=None, database=None)
    @given(a=coefficients,b=integers,c=integers,var=variables)
    def property_valid_equation(a, b, c, var):
        sign='+' if b >= 0 else '-'
        text=f'{a}{var} {sign} {abs(b)} = {c}' if b else f'{a}{var} = {c}'
        output=learn_and_answer(ALGEBRA,'alg',text)
        assert output.status=='ANSWERED'
        assert output.trace['solution']['answer_value']==str(Fraction(c-b,a).numerator) if Fraction(c-b,a).denominator==1 else output.trace['solution']['answer_value']==f'{Fraction(c-b,a).numerator}/{Fraction(c-b,a).denominator}'
        assert output.trace['solution']['verified'] is True
        assert output.trace['safe_solver_adapter_receipt']['solver_backend']=='sympy==1.14.0'
        assert output.trace['echo']['approved_output'] is True
    try: property_valid_equation(); valid_ok=True
    except Exception as exc: valid_ok=False; print('PROPERTY FAILURE valid equation:', exc)
    check('Hypothesis validates 120 generated exact equations', valid_ok)

    @settings(max_examples=60, derandomize=True, deadline=None, database=None)
    @given(a=coefficients,b=integers,c=integers,var=variables,extra=st.sampled_from(['+ y','+ q','and graph it','+ z']))
    def property_refusal(a,b,c,var,extra):
        text=f'{a}{var} + {b} = {c} {extra}'
        output=learn_and_answer(ALGEBRA,'alg',text)
        assert output.status=='REFUSED_UNLEARNED'
        assert output.trace['non_delivery_outcome_v2']['output_delivery_permission'].startswith('NO_HUMAN_TEXT_DELIVERY')
    try: property_refusal(); refusal_ok=True
    except Exception as exc: refusal_ok=False; print('PROPERTY FAILURE refusal:', exc)
    check('Hypothesis validates 60 generated refusal attacks', refusal_ok)

    no_source=learn_and_answer('This text has no algebra procedure.','no_authority','solve 11x + 17 = 105 for x')
    check('source still cannot authorize tool execution', no_source.status=='REFUSED_UNLEARNED' and 'non_delivery_outcome_v2' in no_source.trace)
    boundary=state['dependency_boundary']
    check('no corpus added', boundary['adds_corpus_ingestion'] is False)
    check('no memory/identity/economy write', not boundary['writes_memory'] and not boundary['writes_identity_vault'] and not boundary['writes_contribution_economy'] and not boundary['mints_ct'])
    for name,ok in checks: print(('PASS  ' if ok else 'FAIL  ')+name)
    failed=sum(not ok for _,ok in checks); print(f'\nRESULT: GENERAL-PIPELINE-AUDITED-TOOL-ACTIVATION-BUILD-GP-010B-R1_BEHAVIOR {"PASS" if not failed else "FAIL"}  Total:{len(checks)} Passed:{len(checks)-failed} Failed:{failed}')
    return 1 if failed else 0
if __name__=='__main__': raise SystemExit(main())
