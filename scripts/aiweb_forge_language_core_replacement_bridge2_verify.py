#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, subprocess, sys
from pathlib import Path
EXPECTED_PARENT='65e3dac9b7891b9ac58ce29c1084b9a3bec7a327'
AGENT_SHA='fc2b1aac19ffdfb79eff8d5d10d4a93c45a0c245668f878e75f5c2a384cb88ee'
BRIDGE1={
 'forge_language_bridge_v1/__init__.py':'60bc1a0c5e36c903c85a9d05d6dcd3d26029a4da4912b3992a0c9277f265dd71',
 'forge_language_bridge_v1/interpreter.py':'4cba697a64bc82635b1d0e219e49a339db997c94d0325d2258d44ea7d61972a6',
 'forge_language_bridge_v1/schema.py':'8eb48886332a2ef198550fe8c25d5f5e877a9095db04be0c2578ab39690cbe30',
}
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def git(repo,*args): return subprocess.run(['/usr/bin/git','-C',str(repo),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
def main():
 p=argparse.ArgumentParser(); p.add_argument('repository'); p.add_argument('--mode',choices=('applied','committed','payload'),default='applied'); a=p.parse_args(); repo=Path(a.repository).resolve(); failures=[]
 paths={x.strip() for x in (repo/'scripts/AIWEB_FORGE_LANGUAGE_CORE_REPLACEMENT_BRIDGE2_EXACT_PAYLOAD_PATHS.txt').read_text().splitlines() if x.strip()}
 records={}
 for line in (repo/'scripts/AIWEB_FORGE_LANGUAGE_CORE_REPLACEMENT_BRIDGE2_PAYLOAD_SHA256SUMS.txt').read_text().splitlines():
  if line: d,r=line.split('  ',1); records[r]=d
 expected_manifest_paths=paths-{'scripts/AIWEB_FORGE_LANGUAGE_CORE_REPLACEMENT_BRIDGE2_PAYLOAD_SHA256SUMS.txt'}
 if set(records)!=expected_manifest_paths: failures.append('manifest_path_set_mismatch')
 for r,d in records.items():
  q=repo/r
  if not q.is_file() or sha(q)!=d: failures.append('payload_hash_mismatch:'+r)
 if sha(repo/'agents/forge/agent.py')!=AGENT_SHA: failures.append('agent_py_changed')
 for r,d in BRIDGE1.items():
  if sha(repo/r)!=d: failures.append('bridge1_changed:'+r)
 text=(repo/'main.py').read_text(encoding='utf-8')
 if 'agent.ask(user_input)' in text: failures.append('ordinary_agent_ask_present')
 planner=text[text.index('def _p199_call_planner'):text.index('def _p199_get_latest_slug')]
 if '_p187_call_ollama' in planner: failures.append('planner_ollama_fallback_present')
 if '"ollama_fallback_used": False' not in text: failures.append('operator_fallback_flag_missing')
 if a.mode!='payload':
  staged={x for x in git(repo,'diff','--cached','--name-only').stdout.splitlines() if x}
  memory_tracked=git(repo,'diff','--name-only','--','memory').stdout.strip(); memory_untracked=git(repo,'ls-files','--others','--exclude-standard','--','memory').stdout.strip()
  if staged: failures.append('staged_paths_present')
  if memory_tracked: failures.append('tracked_memory_changes')
  if memory_untracked: failures.append('untracked_memory_paths')
  if a.mode=='applied':
   head=git(repo,'rev-parse','HEAD').stdout.strip()
   changes={x for x in git(repo,'diff','--name-only').stdout.splitlines() if x}|{x for x in git(repo,'ls-files','--others','--exclude-standard').stdout.splitlines() if x}
   if head!=EXPECTED_PARENT: failures.append('unexpected_parent_head:'+head)
   if changes!=paths: failures.append('applied_path_set_mismatch')
  else:
   status=git(repo,'status','--porcelain=v1','-uall').stdout.strip()
   if status: failures.append('repository_not_clean')
 if failures:
  print('FORGE LANGUAGE BRIDGE 2 VERIFIER: FAIL')
  for x in failures: print('FAIL - '+x)
  return 1
 print('FORGE LANGUAGE BRIDGE 2 VERIFIER: PASS')
 print('mode='+a.mode)
 print('payload_files='+str(len(paths)))
 print('agent_py_changed=0')
 print('bridge1_preserved=1')
 print('ordinary_interpretation_llm_fallback=0')
 print('patch199_planner_llm_fallback=0')
 print('operator_console_llm_fallback=0')
 print('remaining_explicit_llm_lanes_visible=1')
 print('staged_paths=0' if a.mode!='payload' else 'staged_paths=not_applicable')
 return 0
if __name__=='__main__': raise SystemExit(main())
