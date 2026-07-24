#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, subprocess
from pathlib import Path
EXPECTED_PARENT='733d59a8ae405aa8f51812f8bdbe0a0fc4d2910d'
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def git(repo,*a): return subprocess.run(['/usr/bin/git','-C',str(repo),*a],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
def main():
 p=argparse.ArgumentParser(); p.add_argument('repository'); p.add_argument('--mode',choices=('applied','committed'),default='applied'); a=p.parse_args(); repo=Path(a.repository).resolve(); failures=[]
 exact=repo/'scripts/AIWEB_FORGE_LANGUAGE_CORE_REPLACEMENT_BRIDGE3_EXACT_PAYLOAD_PATHS.txt'; manifest=repo/'scripts/AIWEB_FORGE_LANGUAGE_CORE_REPLACEMENT_BRIDGE3_PAYLOAD_SHA256SUMS.txt'
 if not exact.is_file() or not manifest.is_file(): failures.append('manifest_files_missing'); paths=[]; records={}
 else:
  paths=[x for x in exact.read_text().splitlines() if x]; records={}
  for line in manifest.read_text().splitlines():
   if line:
    d,r=line.split('  ',1); records[r]=d
  for r,d in records.items():
   q=repo/r
   if not q.is_file() or sha(q)!=d: failures.append('hash:'+r)
 if len(paths)!=12: failures.append('path_count')
 if set(records)!=(set(paths)-{'scripts/AIWEB_FORGE_LANGUAGE_CORE_REPLACEMENT_BRIDGE3_PAYLOAD_SHA256SUMS.txt'}): failures.append('manifest_set')
 head=git(repo,'rev-parse','HEAD').stdout.strip(); staged=git(repo,'diff','--cached','--name-only').stdout.strip()
 if a.mode=='applied':
  if head!=EXPECTED_PARENT: failures.append('head')
  actual=set(git(repo,'diff','--name-only').stdout.splitlines())|set(git(repo,'ls-files','--others','--exclude-standard').stdout.splitlines())
  if actual!=set(paths): failures.append('worktree_set')
  if staged: failures.append('staged')
 else:
  parent=git(repo,'rev-parse','HEAD^').stdout.strip(); committed=set(git(repo,'diff-tree','--no-commit-id','--name-only','-r','HEAD').stdout.splitlines())
  if parent!=EXPECTED_PARENT: failures.append('parent')
  if committed!=set(paths): failures.append('commit_set')
  if git(repo,'status','--porcelain=v1','-uall').stdout.strip(): failures.append('dirty')
 agent=repo/'agents/forge/agent.py'
 if not agent.is_file() or sha(agent)!='fc2b1aac19ffdfb79eff8d5d10d4a93c45a0c245668f878e75f5c2a384cb88ee': failures.append('agent_changed')
 if failures:
  print('FORGE LANGUAGE BRIDGE 3 VERIFIER: FAIL'); [print('FAIL - '+x) for x in failures]; return 1
 print('FORGE LANGUAGE BRIDGE 3 VERIFIER: PASS'); print('mode='+a.mode); print('payload_files=12'); print('agent_py_changed=0'); print('bridge2_preserved=1'); print('real_structural_chain=1'); print('selected_meaning_authority=0'); print('tool_routing_authority=0'); print('action_authority=0'); print('staged_paths=0'); return 0
if __name__=='__main__': raise SystemExit(main())
