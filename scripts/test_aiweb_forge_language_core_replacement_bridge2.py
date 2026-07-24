#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, hashlib, importlib, json, sys
from pathlib import Path


def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()


def function_source(tree: ast.AST, text: str, name: str) -> str:
    lines=text.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name==name:
            return '\n'.join(lines[node.lineno-1:node.end_lineno])
    raise AssertionError(f'missing function: {name}')


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument('repository'); a=p.parse_args()
    repo=Path(a.repository).resolve(); sys.path.insert(0,str(repo))
    checks=[]
    def check(cond, label):
        if not cond: raise AssertionError(label)
        checks.append(label)
    main_path=repo/'main.py'; text=main_path.read_text(encoding='utf-8'); tree=ast.parse(text)
    planner=function_source(tree,text,'_p199_call_planner')
    session=function_source(tree,text,'run_session')
    operator=function_source(tree,text,'_p255_operator_llm_request_v1')
    orchestrator=function_source(tree,text,'cmd_forge_orchestrate')
    check('_p187_call_ollama' not in planner, 'planner_has_no_ollama_call')
    check('_flb2_unsupported_plan' in planner, 'planner_uses_bridge2_hold')
    check('agent.ask(user_input)' not in session, 'ordinary_agent_ask_removed')
    check('_flb2_unsupported' in session, 'ordinary_unsupported_hold_present')
    check('return None' not in orchestrator, 'orchestrator_no_agent_fallback_signal')
    check('"ollama_fallback_used": False' in operator, 'operator_no_ollama_fallback')
    check('"planner_called": False' in operator, 'operator_no_model_planner')
    check(text.count('agent.ask(question)') >= 2, 'explicit_diagnostic_analysis_lanes_preserved')
    check('_p187_call_ollama' in text, 'explicit_generation_llm_lanes_still_visible')
    agent=repo/'agents/forge/agent.py'
    check(agent.is_file(), 'agent_py_present')
    check(sha(agent)=='fc2b1aac19ffdfb79eff8d5d10d4a93c45a0c245668f878e75f5c2a384cb88ee', 'agent_py_preserved')
    bridge1={
      'forge_language_bridge_v1/__init__.py':'60bc1a0c5e36c903c85a9d05d6dcd3d26029a4da4912b3992a0c9277f265dd71',
      'forge_language_bridge_v1/interpreter.py':'4cba697a64bc82635b1d0e219e49a339db997c94d0325d2258d44ea7d61972a6',
      'forge_language_bridge_v1/schema.py':'8eb48886332a2ef198550fe8c25d5f5e877a9095db04be0c2578ab39690cbe30',
    }
    for rel,digest in bridge1.items(): check(sha(repo/rel)==digest, f'bridge1_preserved:{rel}')
    from forge_language_bridge_v2 import bridge_status, unsupported_plan, unsupported_request_decision
    decision=unsupported_request_decision('explain an unknown request', surface='test', reason='held')
    check(decision['handled'] is True, 'unsupported_handled')
    check(decision['status']=='UNSUPPORTED_HOLD', 'unsupported_status')
    check(decision['calls_llm'] is False, 'unsupported_no_llm')
    check(decision['executes_command'] is False, 'unsupported_no_command')
    check(decision['writes_files'] is False and decision['writes_memory'] is False, 'unsupported_no_writes')
    plan=unsupported_plan('build impossible thing', surface='test', reason='held')
    check(plan['impossible'] is True and plan['steps']==[], 'unsupported_plan_held')
    check(plan['_language_bridge']['calls_llm'] is False, 'unsupported_plan_no_llm')
    status=bridge_status()
    check(status['ordinary_interactive_agent_ask_fallback'] is False, 'ordinary_fallback_disabled')
    check(status['patch199_planner_ollama_fallback'] is False, 'planner_fallback_disabled')
    check(status['operator_console_interpretation_ollama_fallback'] is False, 'operator_fallback_disabled')
    check(status['full_language_replacement_claimed'] is False, 'no_full_replacement_claim')
    check(len(status['remaining_explicit_llm_lanes']) >= 7, 'remaining_lanes_visible')
    print('FORGE LANGUAGE BRIDGE 2 BEHAVIOR: PASS')
    print(f'checks_passed={len(checks)}')
    print('ordinary_interpretation_llm_fallback=0')
    print('patch199_planner_llm_fallback=0')
    print('operator_console_llm_fallback=0')
    print('explicit_generation_review_lanes_preserved=1')
    print('simulation_execution=0')
    print('source_writes=0')
    print('memory_writes=0')
    return 0

if __name__=='__main__': raise SystemExit(main())
