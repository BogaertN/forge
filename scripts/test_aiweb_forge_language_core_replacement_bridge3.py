#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

def main() -> int:
 p=argparse.ArgumentParser(); p.add_argument('repository'); a=p.parse_args(); repo=Path(a.repository).resolve(); sys.path.insert(0,str(repo))
 from forge_language_bridge_v3 import structural_preview_decision, structural_preview_plan, bridge_status
 checks=[]
 def check(name,ok,detail=''): checks.append((name,bool(ok),detail))
 for i,text in enumerate(("explain the latest repair", "what can Forge do?", "Do not install it.", "build an unknown resonance device")):
  d=structural_preview_decision(text,surface='test',reason='test')
  check(f'{i}.handled',d.get('handled') is True,d)
  check(f'{i}.no_llm',d.get('calls_llm') is False,d)
  check(f'{i}.no_command',d.get('executes_command') is False,d)
  check(f'{i}.no_write',d.get('writes_files') is False and d.get('writes_memory') is False,d)
  check(f'{i}.no_selection',d.get('selected_meaning') is False,d)
  check(f'{i}.chain',isinstance(d.get('structural_preview'),dict),d)
  p1=structural_preview_plan(text,surface='test_plan',reason='test')
  check(f'{i}.plan_held',p1.get('impossible') is True and p1.get('steps')==[],p1)
 status=bridge_status()
 check('status.v3',status.get('bridge_version')=='forge_language_bridge_v3',status)
 check('status.structural',status.get('deterministic_structural_derivation_connected') is True,status)
 check('status.no_selection',status.get('selected_meaning_authority') is False,status)
 main_text=(repo/'main.py').read_text(encoding='utf-8')
 check('main.v3_cli','_flb3_structural_preview(' in main_text)
 check('main.v3_plan','_flb3_structural_plan(' in main_text)
 check('main.status','record = _flb3_status()' in main_text)
 failed=[x for x in checks if not x[1]]
 if failed:
  print('FORGE LANGUAGE BRIDGE 3 BEHAVIOR: FAIL')
  for n,_,d in failed: print('FAIL -',n,repr(d)[:1000])
  return 1
 print('FORGE LANGUAGE BRIDGE 3 BEHAVIOR: PASS')
 print('checks_passed='+str(len(checks)))
 print('real_structural_chain=1')
 print('covered_requests_call_llm=0')
 print('selected_meaning=0')
 print('tool_routing=0')
 print('action_execution=0')
 print('source_writes=0')
 print('memory_writes=0')
 return 0
if __name__=='__main__': raise SystemExit(main())
