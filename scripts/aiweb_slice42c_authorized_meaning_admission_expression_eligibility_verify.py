#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, hashlib, os, stat, subprocess, sys, tempfile
from pathlib import Path

EXPECTED_HEAD='c00b192e08e15904a413aa6b0e79bd9c36f3f1b9'
EXPECTED_TREE='f6fbbb88fa80f22127a5a307b00b2ce4d7e677b5'
EXPECTED_SUBJECT='Slice 42B deterministic validation identity versioning lifecycle'
COMMIT_SUBJECT='Slice 42C authorized meaning admission and expression eligibility'
PAYLOAD=tuple(Path(x) for x in (Path(__file__).with_name('AIWEB_SLICE42C_EXACT_PAYLOAD_PATHS.txt').read_text().splitlines()) if x)
PROTECTED=Path(__file__).with_name('AIWEB_SLICE42C_PROTECTED_PREDECESSOR_SHA256SUMS.txt')

def run(cmd,cwd=None,env=None): return subprocess.run(cmd,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
def sha(path):
    h=hashlib.sha256();
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def git(repo,*args): return run(['git','-C',str(repo),*args])
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('repository',nargs='?',default='.'); ap.add_argument('--mode',choices=('applied','committed'),default='applied'); a=ap.parse_args(); repo=Path(a.repository).resolve()
    failures=[]; checks=0
    def check(ok,label):
        nonlocal checks; checks+=1
        if ok is not True: failures.append(label)
    check((repo/'.git').exists(),'git repository')
    check(git(repo,'branch','--show-current').stdout.strip()=='main','branch main')
    actual=set(Path(x) for x in git(repo,'ls-files','--others','--exclude-standard').stdout.splitlines() if x)
    staged=set(Path(x) for x in git(repo,'diff','--cached','--name-only').stdout.splitlines() if x)
    tracked=set(Path(x) for x in git(repo,'diff','--name-only').stdout.splitlines() if x)
    if a.mode=='applied':
        check(git(repo,'rev-parse','HEAD').stdout.strip()==EXPECTED_HEAD,'applied parent head')
        check(actual==set(PAYLOAD),'exact untracked payload')
        check(not staged,'no staged paths'); check(not tracked,'no tracked modifications')
    else:
        check(git(repo,'rev-parse','HEAD^').stdout.strip()==EXPECTED_HEAD,'committed parent head')
        check(git(repo,'show','-s','--format=%s','HEAD').stdout.strip()==COMMIT_SUBJECT,'commit subject')
        committed=set(Path(x) for x in git(repo,'diff-tree','--no-commit-id','--name-only','-r','HEAD').stdout.splitlines() if x)
        check(committed==set(PAYLOAD),'exact committed payload'); check(not actual and not staged and not tracked,'clean committed state')
    for line in PROTECTED.read_text().splitlines():
        digest, rel=line.split('  ',1); path=repo/rel
        check(path.is_file() and sha(path)==digest,'protected predecessor '+rel)
    for rel in PAYLOAD:
        path=repo/rel; check(path.is_file(),'payload exists '+rel.as_posix())
        expected=0o755 if rel.name.startswith(('test_','aiweb_slice42c_')) and rel.suffix=='.py' else 0o644
        check(stat.S_IMODE(path.stat().st_mode)==expected,'payload mode '+rel.as_posix())
    runtime=repo/'aiweb_language_core_bootstrap/outward_expression_runtime/expression_eligibility'
    forbidden_imports={'subprocess','socket','requests','urllib','http','pathlib','os','shutil','sqlite3','chromadb','torch','transformers'}
    for path in runtime.glob('*.py'):
        tree=ast.parse(path.read_text(),filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                names=[x.name.split('.')[0] for x in node.names] if isinstance(node,ast.Import) else [(node.module or '').split('.')[0]]
                check(not forbidden_imports.intersection(names),'forbidden runtime import '+path.name)
            check(not isinstance(node,ast.Call) or not isinstance(node.func,ast.Name) or node.func.id not in {'eval','exec','compile','open','input'},'forbidden runtime call '+path.name)
    env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'; env['PYTHONPYCACHEPREFIX']=tempfile.mkdtemp(prefix='aiweb42c_pycache_'); env['PYTHONPATH']=str(repo)
    test=run([sys.executable,'-B',str(repo/'scripts/test_aiweb_slice42c_authorized_meaning_admission_expression_eligibility.py'),str(repo)],cwd=repo,env=env)
    print('=== VISIBLE CURRENT TEST 1 OF 1 ==='); print(test.stdout,end=''); print(test.stderr,end='',file=sys.stderr); check(test.returncode==0,'current behavior test')
    prior_umask=os.umask(0o022)
    try:
        with tempfile.TemporaryDirectory(prefix='aiweb42c_parent_') as td:
            clone=Path(td)/'repo'; c=run(['git','clone','--no-hardlinks','--quiet',str(repo),str(clone)]); check(c.returncode==0,'parent clone')
            if c.returncode==0:
                co=git(clone,'checkout','--quiet','-B','main',EXPECTED_HEAD); check(co.returncode==0,'parent checkout on main')
                inherited=run([sys.executable,'-B',str(clone/'scripts/aiweb_slice42b_deterministic_validation_identity_versioning_lifecycle_verify.py'),str(clone),'--mode','committed'],cwd=clone,env=env)
                print('=== INHERITED VISIBLE VERIFIER: SLICE 42B ==='); print(inherited.stdout,end=''); print(inherited.stderr,end='',file=sys.stderr); check(inherited.returncode==0,'inherited Slice 42B verifier')
    finally: os.umask(prior_umask)
    print('=== SLICE 42C VERIFIER SUMMARY ==='); print('pass_count='+str(checks-len(failures))); print('failure_count='+str(len(failures))); print('protected_predecessor_files='+str(sum(1 for _ in PROTECTED.read_text().splitlines() if _))); print('slice42c_files='+str(len(PAYLOAD))); print('visible_total_tests=61'); print('selected_meaning_alone_grants_expression_authority=0'); print('structural_validity_grants_expression_authority=0'); print('preservation_obligations_projected=0'); print('expression_plan_or_text_created=0'); print('echo_validation_delivery_action=0'); print('model_or_similarity_authority=0'); print('gp014_superseded=0'); print('hidden_test_workers=0'); print('test_output_suppression=0')
    for failure in failures: print('FAIL: '+failure)
    print('RESULT='+('PASS' if not failures else 'FAIL')); return 0 if not failures else 1
if __name__=='__main__': raise SystemExit(main())
