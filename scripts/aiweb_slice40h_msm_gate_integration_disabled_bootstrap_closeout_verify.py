#!/usr/bin/env python3
"""Visible sequential verifier for AI.Web Slice 40H."""
from __future__ import annotations
import argparse, ast, hashlib, io, os, stat, subprocess, sys, tarfile, tempfile
from pathlib import Path, PurePosixPath
EXPECTED_BRANCH="main"
EXPECTED_HEAD="3f13618b6e60efdc5c3bfb7b89043c1b9d8a25aa"
EXPECTED_TREE="150d9568bd92d7ba98dc8ef02244bf01648732c4"
EXPECTED_SUBJECT="Slice 40G deterministic gate composition non-selection disposition runtime"
EXPECTED_COMMITTED_SUBJECT="Slice 40H MSM gate integration disabled bootstrap and Slice 40 closeout"
EXPECTED_PROTECTED_COUNT=570
EXPECTED_PAYLOAD_COUNT=17
CURRENT_TEST="scripts/test_aiweb_slice40h_msm_gate_integration_disabled_bootstrap_closeout.py"
PRE_SLICE39G_CONTEXT_TEST="scripts/test_aiweb_slice39b_39e_roadmap_continuity_correction.py"
SLICE38H_INHERITED_TEST="scripts/test_aiweb_slice38h_disabled_bootstrap_integration_closeout.py"
PRE_SLICE39G_CONTEXT_COMMIT="e311e8960b96eff2015b7773b92b16bf2f0dc6a3"
PARENT_CONTEXT_TEST="scripts/test_aiweb_slice40g_gate_composition_non_selection_disposition_runtime.py"
INHERITED_TESTS=('scripts/test_aiweb_slice40g_gate_composition_non_selection_disposition_runtime.py', 'scripts/test_aiweb_slice40f_recoverable_purpose_runtime.py', 'scripts/test_aiweb_slice40e_connectedness_gate_runtime.py', 'scripts/test_aiweb_slice40d_congruity_gate_runtime.py', 'scripts/test_aiweb_slice40c_expectancy_gate_runtime.py', 'scripts/test_aiweb_slice40b_deterministic_validation_identity_versioning_lifecycle.py', 'scripts/test_aiweb_slice40a_verbal_cognition_gate_core_schema.py', 'scripts/test_aiweb_slice39h_disabled_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice39g_meaning_structure_manifest_candidate_integration.py', 'scripts/test_aiweb_slice39f_deterministic_candidate_meaning_constructor.py', 'scripts/test_aiweb_slice39b_39e_roadmap_continuity_correction.py', 'scripts/test_aiweb_slice39e_candidate_set_alternative_preservation.py', 'scripts/test_aiweb_slice39d_candidate_semantic_content_assembly.py', 'scripts/test_aiweb_slice39c_complete_provenance_predecessor_custody.py', 'scripts/test_aiweb_slice39b_deterministic_validation_identity_versioning_lifecycle.py', 'scripts/test_aiweb_slice39a_candidate_meaning_core_schema.py', 'scripts/test_aiweb_slice38h_disabled_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice38g_predicate_role_frame_candidate_proposal.py', 'scripts/test_aiweb_slice38f_capability_family_references_effect_boundaries.py', 'scripts/test_aiweb_slice38e_predicate_frame_constraints_role_compatibility.py', 'scripts/test_aiweb_slice38d_participant_role_identity_registry.py', 'scripts/test_aiweb_slice38c_minimal_built_in_action_root_registry.py', 'scripts/test_aiweb_slice24_full_regression_acceptance_bundle_scaffold.py', 'scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py', 'scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py', 'scripts/test_aiweb_slice32_accepted_boundary_component_loading.py', 'scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py', 'scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py', 'scripts/test_aiweb_slice35a_meaning_structure_manifest_core_schema.py', 'scripts/test_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.py', 'scripts/test_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.py', 'scripts/test_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.py', 'scripts/test_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice36a_input_event_source_custody.py', 'scripts/test_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.py', 'scripts/test_aiweb_slice36b_deterministic_source_field_projection.py', 'scripts/test_aiweb_slice36c_symbolic_grammar_operator_registry.py', 'scripts/test_aiweb_slice36d_resonant_operator_candidate_binding.py', 'scripts/test_aiweb_slice36e_candidate_resonant_phase_trail.py', 'scripts/test_aiweb_slice36f_scope_attachment_reference_constraints.py', 'scripts/test_aiweb_slice36g_deterministic_structural_derivation.py', 'scripts/test_aiweb_slice36h_bounded_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice37a_controlled_concept_authority_schema.py', 'scripts/test_aiweb_slice37b_deterministic_validation_identity_lifecycle.py', 'scripts/test_aiweb_slice37c_minimal_built_in_concept_registry.py', 'scripts/test_aiweb_slice37d_controlled_sense_exact_term_mapping_registry.py', 'scripts/test_aiweb_slice37e_semantic_class_relation_registry.py', 'scripts/test_aiweb_slice37f_structural_concept_candidate_proposal.py', 'scripts/test_aiweb_slice37g_disabled_integration_closeout.py', 'scripts/test_aiweb_slice38a_action_root_predicate_schema.py', 'scripts/test_aiweb_slice38b_deterministic_validation_identity_versioning_lifecycle.py')
PAYLOAD_PATHS=()  # replaced below from exact file
class V:
 def __init__(self): self.passes=0; self.failures=[]
 def check(self,c,l): self.passes+=1 if c is True else 0; self.failures.append(l) if c is not True else None
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def git(r,*a): return subprocess.run(['git','-C',str(r),*a],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
def parse_manifest(p):
 out=[]; seen=set()
 for line in p.read_text().splitlines():
  if not line: continue
  d,n=line.split('  ',1); q=PurePosixPath(n)
  if q.is_absolute() or '..' in q.parts or n in seen or len(d)!=64: raise ValueError('manifest')
  seen.add(n); out.append((d,n))
 return tuple(out)
def select_python(r):
 p=r/'.venv/bin/python3'; return str(p) if p.is_file() else '/usr/bin/python3'
def run(command,cwd,env):
 p=subprocess.Popen(command,cwd=str(cwd),env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=1); out=[]
 for line in p.stdout: print(line,end=''); out.append(line)
 return p.wait(),''.join(out)
def run_commit_context(repository,relative,commit,python_executable,env,v):
 archive=subprocess.run(['git','-C',str(repository),'archive','--format=tar',commit,'aiweb_language_core_bootstrap','scripts'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
 if archive.returncode!=0: v.check(False,'pre-slice39g archive'); return 1,archive.stderr.decode(errors='replace')
 with tempfile.TemporaryDirectory(prefix='aiweb_slice40h_pre39g_') as td:
  root=Path(td)
  try:
   with tarfile.open(fileobj=io.BytesIO(archive.stdout),mode='r:') as h:
    members=h.getmembers()
    for m in members:
     q=PurePosixPath(m.name)
     if q.is_absolute() or '..' in q.parts or m.issym() or m.islnk(): raise ValueError(m.name)
    h.extractall(root,members=members)
  except Exception as e: v.check(False,'pre-slice39g extraction'); return 1,str(e)
  print('execution_context=accepted_pre_slice39g_source'); print('accepted_commit='+commit); print('source_only_repository='+str(root))
  return run([python_executable,'-B',str(root/relative),str(root)],root,env)
def run_source_only(repository,relative,python_executable,env,v):
 with tempfile.TemporaryDirectory(prefix='aiweb_slice40h_slice38h_') as td:
  root=Path(td)
  try:
   os.symlink(repository/'aiweb_language_core_bootstrap',root/'aiweb_language_core_bootstrap',target_is_directory=True)
   os.symlink(repository/'scripts',root/'scripts',target_is_directory=True)
  except OSError as e: v.check(False,'slice38h source view'); return 1,str(e)
  print('execution_context=accepted_slice38h_source_only'); print('source_only_repository='+str(root))
  return run([python_executable,'-B',str(root/relative),str(root)],root,env)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('repository',nargs='?',default='.'); ap.add_argument('--mode',choices=('source','applied','committed'),default='source'); a=ap.parse_args(); r=Path(a.repository).resolve(); v=V()
 paths=tuple(sorted(x for x in (r/'scripts/AIWEB_SLICE40H_EXACT_PAYLOAD_PATHS.txt').read_text().splitlines() if x))
 global PAYLOAD_PATHS; PAYLOAD_PATHS=paths
 protected=parse_manifest(r/'scripts/AIWEB_SLICE40H_PROTECTED_PREDECESSOR_SHA256SUMS.txt'); v.check(len(protected)==570,'protected count')
 for d,n in protected:
  p=r/n; v.check(p.is_file() and not p.is_symlink(),'protected exists '+n); v.check(p.is_file() and sha(p)==d,'protected hash '+n)
 v.check(len(paths)==17,'payload count')
 for n in paths:
  p=r/n; v.check(p.is_file() and not p.is_symlink(),'payload exists '+n); v.check(stat.S_IMODE(p.stat().st_mode)==(0o755 if n.startswith('scripts/test_') or n.startswith('scripts/aiweb_') else 0o644),'payload mode '+n)
 if a.mode!='source':
  branch=git(r,'branch','--show-current'); head=git(r,'rev-parse','HEAD'); tree=git(r,'rev-parse','HEAD^{tree}'); subject=git(r,'show','-s','--format=%s','HEAD'); staged=git(r,'diff','--cached','--name-only'); tracked=git(r,'diff','--name-only'); untracked=git(r,'ls-files','--others','--exclude-standard')
  if a.mode=='applied':
   v.check(branch.stdout.strip()==EXPECTED_BRANCH,'branch'); v.check(head.stdout.strip()==EXPECTED_HEAD,'head'); v.check(tree.stdout.strip()==EXPECTED_TREE,'tree'); v.check(subject.stdout.strip()==EXPECTED_SUBJECT,'subject'); v.check(not staged.stdout.strip(),'staged zero'); v.check(not tracked.stdout.strip(),'tracked zero'); v.check(tuple(sorted(untracked.stdout.splitlines()))==paths,'untracked exact')
  else:
   parent=git(r,'rev-parse','HEAD^'); committed=git(r,'diff-tree','--no-commit-id','--name-only','-r','HEAD')
   v.check(parent.stdout.strip()==EXPECTED_HEAD,'parent'); v.check(subject.stdout.strip()==EXPECTED_COMMITTED_SUBJECT,'committed subject'); v.check(tuple(sorted(committed.stdout.splitlines()))==paths,'committed paths'); v.check(not staged.stdout.strip() and not tracked.stdout.strip() and not untracked.stdout.strip(),'committed clean')
 tests=(CURRENT_TEST,) if a.mode=='source' else (CURRENT_TEST,*INHERITED_TESTS); py=select_python(r); env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'; env['PYTHONUNBUFFERED']='1'; env.pop('PYTHONPYCACHEPREFIX',None)
 current=''; failed=0
 for i,n in enumerate(tests,1):
  print(f'\n=== VISIBLE TEST {i} OF {len(tests)} ==='); print('path='+n); print('output_begins_below')
  if n==PRE_SLICE39G_CONTEXT_TEST: rc,out=run_commit_context(r,n,PRE_SLICE39G_CONTEXT_COMMIT,py,env,v)
  elif n==SLICE38H_INHERITED_TEST: rc,out=run_source_only(r,n,py,env,v)
  else: rc,out=run([py,'-B',str(r/n),str(r)],r,env)
  print('output_ended_above'); print('return_code='+str(rc)); v.check(rc==0,'test '+n); failed+=rc!=0
  if n==CURRENT_TEST: current=out
  if n==PARENT_CONTEXT_TEST: v.check('AI.WEB SLICE 40G GATE COMPOSITION BEHAVIOR TEST: PASS' in out,'Slice 40G context marker')
 markers=('AI.WEB SLICE 40H BEHAVIOR TEST: PASS','fixture_count=8','protected_predecessor_files=570','exact_payload_paths=17','four_gate_family_results_preserved=1','composition_result_preserved=1','msm_gate_companion_created=1','lawful_non_selection_projection=1','clarification_relevant_not_required=1','positive_selection_review_companion_only=1','refusal_relevant_not_outward_refusal=1','selected_meaning_created=0','slice40_closeout_record_created=1','slice41_started=0','stop_after_slice40=1')
 for x in markers: v.check(x in current,'marker '+x)
 print('\n=== SLICE 40H VERIFIER SUMMARY ==='); print('pass_count='+str(v.passes)); print('failure_count='+str(len(v.failures))); [print('FAIL: '+x) for x in v.failures]
 if v.failures or failed: print('SLICE 40H VISIBLE INDEPENDENT VERIFIER: FAIL'); return 1
 print('SLICE 40H VISIBLE INDEPENDENT VERIFIER: PASS'); print('protected_predecessor_files=570'); print('inherited_tests='+str(len(tests)-1)); print('visible_total_tests='+str(len(tests))); print('slice40h_files=17'); print('fixture_count=8'); print('four_gate_family_results_preserved=1'); print('composition_result_preserved=1'); print('msm_gate_companion_created=1'); print('lawful_non_selection_projection=1'); print('clarification_relevant_not_required=1'); print('positive_selection_review_companion_only=1'); print('refusal_relevant_not_outward_refusal=1'); print('selected_meaning_created=0'); print('slice40_closeout_record_created=1'); print('slice41_started=0'); print('stop_after_slice40=1'); print('hidden_test_workers=0'); print('test_output_suppression=0'); print('RESULT=PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
