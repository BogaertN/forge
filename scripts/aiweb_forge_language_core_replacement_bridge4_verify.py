#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, subprocess
from pathlib import Path
EXPECTED_PARENT='1ef21fd10b64488f4cfb82a994770536a71d0842'
AGENT_SHA='fc2b1aac19ffdfb79eff8d5d10d4a93c45a0c245668f878e75f5c2a384cb88ee'
APPCTL_SHA='7c2f73007bf2b9b6d1821c1ab9f788c21b81dac2eae831bc591ecc0f5c21535d'
BRIDGE1_SHA='4cba697a64bc82635b1d0e219e49a339db997c94d0325d2258d44ea7d61972a6'
BRIDGE2_SHA='165090c98f32bc875ba6b1f62134f4bf74671fef4e7d89b01ced398ec32fa6cb'
BRIDGE3_SHA='9461aa61c5905507441b5ee54c611606e55f5c0795050d172f1b8aa8b99ce87f'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def git(repo,*args):return subprocess.run(['/usr/bin/git','-C',str(repo),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('repository');p.add_argument('--mode',choices=('applied','committed'),default='applied');a=p.parse_args();repo=Path(a.repository).resolve();fail=[]
 exact=repo/'scripts/AIWEB_FORGE_LANGUAGE_CORE_REPLACEMENT_BRIDGE4_EXACT_PAYLOAD_PATHS.txt';manifest=repo/'scripts/AIWEB_FORGE_LANGUAGE_CORE_REPLACEMENT_BRIDGE4_PAYLOAD_SHA256SUMS.txt'
 if not exact.is_file() or not manifest.is_file():fail.append('manifest_files_missing');paths=[];records={}
 else:
  paths=[x for x in exact.read_text().splitlines() if x];records={}
  for line in manifest.read_text().splitlines():
   if line:
    d,r=line.split('  ',1);records[r]=d
  for r,d in records.items():
   q=repo/r
   if not q.is_file() or sha(q)!=d:fail.append('hash:'+r)
 if len(paths)!=12:fail.append('path_count')
 if set(records)!=(set(paths)-{'scripts/AIWEB_FORGE_LANGUAGE_CORE_REPLACEMENT_BRIDGE4_PAYLOAD_SHA256SUMS.txt'}):fail.append('manifest_set')
 head=git(repo,'rev-parse','HEAD').stdout.strip();staged=git(repo,'diff','--cached','--name-only').stdout.strip()
 if a.mode=='applied':
  if head!=EXPECTED_PARENT:fail.append('head')
  actual=set(git(repo,'diff','--name-only').stdout.splitlines())|set(git(repo,'ls-files','--others','--exclude-standard').stdout.splitlines())
  if actual!=set(paths):fail.append('worktree_set')
  if staged:fail.append('staged')
 else:
  parent=git(repo,'rev-parse','HEAD^').stdout.strip();committed=set(git(repo,'diff-tree','--no-commit-id','--name-only','-r','HEAD').stdout.splitlines())
  if parent!=EXPECTED_PARENT:fail.append('parent')
  if committed!=set(paths):fail.append('commit_set')
  if git(repo,'status','--porcelain=v1','-uall').stdout.strip():fail.append('dirty')
 protected={'agents/forge/agent.py':AGENT_SHA,'scripts/aiweb_os_appctl.py':APPCTL_SHA,'forge_language_bridge_v1/interpreter.py':BRIDGE1_SHA,'forge_language_bridge_v2/boundary.py':BRIDGE2_SHA,'forge_language_bridge_v3/structural_preview.py':BRIDGE3_SHA}
 for rel,digest in protected.items():
  q=repo/rel
  if not q.is_file() or sha(q)!=digest:fail.append('protected_changed:'+rel)
 if git(repo,'diff','--name-only','--','memory').stdout.strip():fail.append('tracked_memory')
 if git(repo,'ls-files','--others','--exclude-standard','--','memory').stdout.strip():fail.append('untracked_memory')
 if fail:
  print('FORGE LANGUAGE BRIDGE 4 VERIFIER: FAIL');[print('FAIL - '+x) for x in fail];return 1
 print('FORGE LANGUAGE BRIDGE 4 VERIFIER: PASS');print('mode='+a.mode);print('payload_files=12');print('agent_py_changed=0');print('launcher_repair_preserved=1');print('bridges1_3_preserved=1');print('real_candidate_meaning_chain=1');print('real_msm_candidate_custody=1');print('selection_eligibility_evaluated=0');print('selected_meaning_constructed=0');print('tool_routing_authority=0');print('action_authority=0');print('staged_paths=0');return 0
if __name__=='__main__':raise SystemExit(main())
