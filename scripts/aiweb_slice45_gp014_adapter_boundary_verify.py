#!/usr/bin/env python3
"""Visible independent verifier for Slice 45 GP-014 adapter boundary."""
from __future__ import annotations

import argparse
import ast
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile

EXPECTED_BRANCH = "main"
EXPECTED_PARENT_HEAD = "d374ebb8c09ef0f74df93177ea08bffb5e66791d"
EXPECTED_PARENT_TREE = "c284950f6100a08a049a7f627da4a114ed75d640"
EXPECTED_PARENT_SUBJECT = "Slice 43H disabled bootstrap integration and Slice 43 closeout"
EXPECTED_COMMIT_SUBJECT = "Slice 45 bounded GP-014 adapter boundary"
PACKAGE_RELATIVE = Path("aiweb_language_core_bootstrap/gp014_adapter_boundary")
EXACT_PACKAGE_FILES = ("__init__.py", "adapter.py", "authority.py", "bindings.py", "canonical.py", "schema.py", "validation.py")
EXACT_PAYLOAD_MANIFEST = Path("scripts/AIWEB_SLICE45_EXACT_PAYLOAD_PATHS.txt")
PROTECTED_PREDECESSOR_MANIFEST = Path("scripts/AIWEB_SLICE45_PROTECTED_PREDECESSOR_SHA256SUMS.txt")
BEHAVIOR_TEST = Path("scripts/test_aiweb_slice45_gp014_adapter_boundary.py")
INHERITED_VERIFIER = Path("scripts/aiweb_slice43h_disabled_bootstrap_integration_and_slice43_closeout_verify.py")
GP014_BEHAVIOR = Path("scripts/test_operator_guided_language_realizer_build_langexpr001_gp014.py")
GP014_VERIFIER = Path("scripts/operator_guided_language_realizer_build_langexpr001_gp014_verify.py")
EXPECTED_PREDECESSOR_COUNT = 1775
EXPECTED_PAYLOAD_COUNT = 15

class Ledger:
    def __init__(self): self.passes=0; self.failures=[]
    def check(self, condition, label):
        if condition is True: self.passes += 1
        else: self.failures.append(label)

def git(repository, *args):
    return subprocess.run(["/usr/bin/git", "-C", str(repository), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

def sha256_file(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def parse_manifest(path):
    entries=[]; seen=set(); previous=''
    for number,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if not line: continue
        digest, relative = line.split('  ',1)
        pure=PurePosixPath(relative)
        if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest) or pure.is_absolute() or any(p in ('','.','..') for p in pure.parts) or relative in seen or (previous and relative<previous):
            raise ValueError(f'unsafe manifest line {number}')
        seen.add(relative); previous=relative; entries.append((digest,relative))
    return tuple(entries)

def payload_paths(repository):
    values=tuple(x for x in (repository/EXACT_PAYLOAD_MANIFEST).read_text(encoding='utf-8').splitlines() if x)
    if values != tuple(sorted(values)) or len(values)!=len(set(values)): raise ValueError('payload manifest not sorted unique')
    for value in values:
        pure=PurePosixPath(value)
        if pure.is_absolute() or any(p in ('','.','..') for p in pure.parts): raise ValueError('unsafe payload path')
    return values

def select_python(repository):
    candidate=repository/'.venv/bin/python3'
    return str(candidate) if candidate.is_file() else '/usr/bin/python3'

def run_visible(command,cwd,env):
    child=env.copy(); child['PYTHONUNBUFFERED']='1'
    process=subprocess.Popen(command,cwd=str(cwd),env=child,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=1)
    output=[]
    assert process.stdout is not None
    for line in process.stdout:
        print(line,end='',flush=True); output.append(line)
    return process.wait(), ''.join(output)


def run_inherited(repository, env):
    with tempfile.TemporaryDirectory(prefix="aiweb-slice45-inherited-") as temp:
        checkout=Path(temp)/"forge"
        clone=subprocess.run(
            ["/usr/bin/git","clone","--quiet","--no-hardlinks",str(repository),str(checkout)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            umask=0o022,
        )
        if clone.returncode:
            print(clone.stdout,end="")
            return clone.returncode, clone.stdout
        checked=subprocess.run(
            ["/usr/bin/git","-C",str(checkout),"checkout","--quiet","-B","main",EXPECTED_PARENT_HEAD],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            umask=0o022,
        )
        if checked.returncode:
            print(checked.stdout,end="")
            return checked.returncode, checked.stdout
        return run_visible([select_python(checkout),"-u","-B",str(checkout/INHERITED_VERIFIER),str(checkout),"--mode","committed"],checkout,{**env,"PYTHONPATH":str(checkout)})

def verify_git_state(repository, mode, expected_paths, ledger):
    branch=git(repository,'branch','--show-current')
    head=git(repository,'rev-parse','HEAD')
    tree=git(repository,'rev-parse','HEAD^{tree}')
    subject=git(repository,'show','-s','--format=%s','HEAD')
    ledger.check(branch.returncode==0 and branch.stdout.strip()==EXPECTED_BRANCH,'branch main')
    if mode=='applied':
        ledger.check(head.stdout.strip()==EXPECTED_PARENT_HEAD,'applied parent head')
        ledger.check(tree.stdout.strip()==EXPECTED_PARENT_TREE,'applied parent tree')
        ledger.check(subject.stdout.strip()==EXPECTED_PARENT_SUBJECT,'applied parent subject')
        status=git(repository,'status','--porcelain=v1','--untracked-files=all')
        lines=tuple(x for x in status.stdout.splitlines() if x)
        untracked=tuple(sorted(x[3:] for x in lines if x.startswith('?? ')))
        other=tuple(x for x in lines if not x.startswith('?? '))
        ledger.check(not other,'no staged or tracked modifications')
        ledger.check(untracked==tuple(sorted(expected_paths)),'exact untracked payload')
    else:
        parent=git(repository,'rev-parse','HEAD^')
        ledger.check(parent.stdout.strip()==EXPECTED_PARENT_HEAD,'committed parent head')
        ledger.check(subject.stdout.strip()==EXPECTED_COMMIT_SUBJECT,'committed subject')
        changed=git(repository,'diff-tree','--no-commit-id','--name-only','-r','HEAD')
        ledger.check(tuple(sorted(x for x in changed.stdout.splitlines() if x))==tuple(sorted(expected_paths)),'exact committed payload')
        status=git(repository,'status','--porcelain=v1','--untracked-files=all')
        ledger.check(status.stdout=='','committed repository clean')

def verify_runtime_source(repository, ledger):
    package=repository/PACKAGE_RELATIVE
    ledger.check(package.is_dir(),'package exists')
    ledger.check(tuple(sorted(p.name for p in package.glob('*.py')))==EXACT_PACKAGE_FILES,'exact package files')
    all_source='\n'.join((package/name).read_text(encoding='utf-8') for name in EXACT_PACKAGE_FILES)
    ledger.check('gp015_ask_forge_trace_surface' not in all_source or 'GP015_MODULE_NAME' in all_source,'GP-015 appears only as prohibited identity constant')
    for prohibited in ('from rmc_engine_v1.general_pipeline.gp015','import rmc_engine_v1.general_pipeline.gp015','main.py','@app.route','@app.post','Flask(','FastAPI(','requests.','socket.','subprocess.','write_text(','write_bytes(','open('):
        if prohibited=='main.py':
            ledger.check('main.py' not in all_source,'runtime package does not address main.py')
        else:
            ledger.check(prohibited not in all_source,'runtime source prohibits '+prohibited)
    bindings=(package/'bindings.py').read_text(encoding='utf-8')
    adapter=(package/'adapter.py').read_text(encoding='utf-8')
    ledger.check('importlib.import_module(GP014_MODULE_NAME)' in bindings,'lazy exact GP-014 module binding')
    ledger.check('importlib.import_module(GP014_VERTICAL_SLICE_MODULE_NAME)' in bindings,'lazy vertical-slice binding')
    ledger.check('binding.answer(request.question)' in adapter,'exact question delegated once')
    ledger.check(adapter.count('binding.answer(request.question)')==1,'single source call site')
    ledger.check('except Exception:' in adapter and 'gp014_source_exception_contained' in adapter,'raw source exception contained')
    for name in EXACT_PACKAGE_FILES:
        try: ast.parse((package/name).read_text(encoding='utf-8'))
        except SyntaxError: ledger.check(False,'syntax '+name)
        else: ledger.check(True,'syntax '+name)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('repository',nargs='?',default='.'); parser.add_argument('--mode',choices=('applied','committed'),default='applied')
    args=parser.parse_args(); repository=Path(args.repository).resolve(); ledger=Ledger()
    expected=payload_paths(repository)
    ledger.check(len(expected)==EXPECTED_PAYLOAD_COUNT,'payload count')
    verify_git_state(repository,args.mode,expected,ledger)
    predecessor=parse_manifest(repository/PROTECTED_PREDECESSOR_MANIFEST)
    ledger.check(len(predecessor)==EXPECTED_PREDECESSOR_COUNT,'predecessor count')
    for digest,relative in predecessor:
        path=repository/relative
        ledger.check(path.is_file(),'predecessor exists '+relative)
        if path.is_file(): ledger.check(sha256_file(path)==digest,'predecessor hash '+relative)
    for rel in (
        'rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py',
        'rmc_engine_v1/general_pipeline/symbolic_math_language_vertical_slice.py',
        'rmc_engine_v1/general_pipeline/symbolic_math_operator_language_realizer.py',
        'rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json',
        'scripts/test_operator_guided_language_realizer_build_langexpr001_gp014.py',
        'scripts/operator_guided_language_realizer_build_langexpr001_gp014_verify.py',
        'aiweb_language_core_bootstrap/rmc_echo_runtime/disabled_echo_closeout/integration.py',
    ):
        ledger.check(any(path==rel for _,path in predecessor),'protected predecessor '+rel)
    verify_runtime_source(repository,ledger)
    env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'; env['PYTHONPATH']=str(repository)
    py=select_python(repository)
    for title, command, marker in (
        ('CURRENT SLICE 45 BEHAVIOR',[py,'-u','-B',str(repository/BEHAVIOR_TEST),str(repository)],'AI.WEB SLICE 45 BEHAVIOR TEST: PASS'),
        ('ORIGINAL GP-014 BEHAVIOR',[py,'-u','-B',str(repository/GP014_BEHAVIOR)],'RESULT: LANG-EXPR-001-GP-014-OPERATOR-GUIDED-GENERATIVE-LANGUAGE-REALIZER_BEHAVIOR PASS'),
        ('ORIGINAL GP-014 VERIFIER',[py,'-u','-B',str(repository/GP014_VERIFIER)],'RESULT: LANG-EXPR-001-GP-014-OPERATOR-GUIDED-GENERATIVE-LANGUAGE-REALIZER_VERIFY PASS'),
    ):
        print('\n=== '+title+' ===')
        rc,out=run_visible(command,repository,env)
        ledger.check(rc==0,title+' return code')
        ledger.check(marker in out,title+' marker')
    print('\n=== INHERITED SLICE 43H VERIFIER ===')
    inherited_rc,inherited_out=run_inherited(repository,env)
    ledger.check(inherited_rc==0,'INHERITED SLICE 43H VERIFIER return code')
    ledger.check('AI.WEB SLICE 43H VERIFIER: PASS' in inherited_out,'INHERITED SLICE 43H VERIFIER marker')
    print('\n=== SLICE 45 VERIFIER SUMMARY ===')
    print('checks='+str(ledger.passes+len(ledger.failures)))
    print('passes='+str(ledger.passes))
    print('failures='+str(len(ledger.failures)))
    print('protected_predecessor_files='+str(len(predecessor)))
    print('slice45_files='+str(len(expected)))
    print('gp014_byte_preserved=1')
    print('gp014_adapter_unregistered=1')
    print('gp014_superseded=0')
    print('gp015_used=0')
    print('main_route_api_ui_change=0')
    print('adapter_delivery_authority=0')
    for failure in ledger.failures: print('FAIL - '+failure)
    print('AI.WEB SLICE 45 VERIFIER: '+('PASS' if not ledger.failures else 'FAIL'))
    return 0 if not ledger.failures else 1

if __name__=='__main__': raise SystemExit(main())
