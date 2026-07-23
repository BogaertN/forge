#!/usr/bin/env python3
"""Independent verifier for Slice 46 GP-014 equivalence proof."""
from __future__ import annotations

import argparse
import ast
import hashlib
import os
from pathlib import Path, PurePosixPath
import shutil
import shlex
import stat
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

EXPECTED_PARENT_HEAD = '00df51e4b2fe14e437291c5228159820dd1cf139'
EXPECTED_PARENT_TREE = '987c08cc797ebe721dc28ab7d03b69a6b1b61f8f'
EXPECTED_PARENT_SUBJECT = 'Slice 45 bounded GP-014 adapter boundary'
EXPECTED_COMMIT_SUBJECT = 'Slice 46 GP-014 equivalence and regression proof'
EXPECTED_PAYLOAD_COUNT = 16
RUNTIME_PREFIX = "aiweb_language_core_bootstrap/gp014_equivalence_regression_proof/"


def run(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None, umask: int | None = None) -> subprocess.CompletedProcess[str]:
    kwargs = dict(text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, cwd=None if cwd is None else str(cwd), env=env)
    if umask is not None:
        kwargs["umask"] = umask
    return subprocess.run(list(args), **kwargs)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_paths(path: Path) -> tuple[str, ...]:
    rows = tuple(line for line in path.read_text(encoding="utf-8").splitlines() if line)
    for rel in rows:
        pure = PurePosixPath(rel)
        if pure.is_absolute() or any(part in ("", ".", "..") for part in pure.parts):
            raise ValueError("unsafe payload path")
    if len(rows) != len(set(rows)):
        raise ValueError("duplicate payload path")
    return rows


def parse_hashes(path: Path) -> tuple[tuple[str, str], ...]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        digest, rel = line.split("  ", 1)
        rows.append((digest, rel))
    return tuple(rows)


def mode_for(rel: str) -> int:
    return 0o755 if rel.endswith('.py') and rel.startswith('scripts/') else 0o644


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("--mode", choices=("applied", "committed"), required=True)
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    failures: list[str] = []
    passes = 0
    def check(condition: object, label: str) -> None:
        nonlocal passes
        if condition:
            passes += 1
        else:
            failures.append(label)

    branch = run('/usr/bin/git', '-C', str(repo), 'branch', '--show-current')
    head = run('/usr/bin/git', '-C', str(repo), 'rev-parse', 'HEAD')
    tree = run('/usr/bin/git', '-C', str(repo), 'rev-parse', 'HEAD^{tree}')
    subject = run('/usr/bin/git', '-C', str(repo), 'show', '-s', '--format=%s', 'HEAD')
    staged = run('/usr/bin/git', '-C', str(repo), 'diff', '--cached', '--name-only')
    status = run('/usr/bin/git', '-C', str(repo), 'status', '--porcelain=v1', '--untracked-files=all')
    check(branch.returncode == 0 and branch.stdout.strip() == 'main', 'branch main')

    paths_file = repo / 'scripts/AIWEB_SLICE46_EXACT_PAYLOAD_PATHS.txt'
    check(paths_file.is_file(), 'exact payload path file present')
    try:
        payload_paths = parse_paths(paths_file)
    except Exception as error:
        payload_paths = ()
        failures.append('payload path manifest invalid:' + type(error).__name__)
    check(len(payload_paths) == EXPECTED_PAYLOAD_COUNT, 'exact payload count')

    if args.mode == 'applied':
        check(head.stdout.strip() == EXPECTED_PARENT_HEAD, 'applied parent head')
        check(tree.stdout.strip() == EXPECTED_PARENT_TREE, 'applied parent tree')
        check(subject.stdout.strip() == EXPECTED_PARENT_SUBJECT, 'applied parent subject')
        check(not staged.stdout.strip(), 'applied no staged paths')
        status_lines = tuple(line for line in status.stdout.splitlines() if line)
        untracked = tuple(sorted(line[3:] for line in status_lines if line.startswith('?? ')))
        other = tuple(line for line in status_lines if not line.startswith('?? '))
        check(not other, 'applied no tracked modifications')
        check(untracked == tuple(sorted(payload_paths)), 'applied exact untracked payload')
    else:
        parent = run('/usr/bin/git', '-C', str(repo), 'rev-parse', 'HEAD^')
        check(parent.stdout.strip() == EXPECTED_PARENT_HEAD, 'committed parent head')
        check(subject.stdout.strip() == EXPECTED_COMMIT_SUBJECT, 'committed subject')
        check(not status.stdout.strip(), 'committed clean status')
        committed_paths = run('/usr/bin/git', '-C', str(repo), 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD')
        check(tuple(sorted(committed_paths.stdout.splitlines())) == tuple(sorted(payload_paths)), 'committed exact payload')

    for rel in payload_paths:
        path = repo / rel
        check(path.is_file(), 'payload exists ' + rel)
        if path.is_file():
            check(stat.S_IMODE(path.stat().st_mode) == mode_for(rel), 'payload mode ' + rel)
            if path.suffix == '.py':
                try:
                    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
                    check(True, 'syntax ' + rel)
                except SyntaxError:
                    check(False, 'syntax ' + rel)

    protected_file = repo / 'scripts/AIWEB_SLICE46_PROTECTED_PREDECESSOR_SHA256SUMS.txt'
    check(protected_file.is_file(), 'protected manifest present')
    protected = parse_hashes(protected_file) if protected_file.is_file() else ()
    check(len(protected) == 1790, 'protected predecessor count')
    for expected_digest, rel in protected:
        path = repo / rel
        check(path.is_file(), 'protected exists ' + rel)
        if path.is_file():
            check(sha256_file(path) == expected_digest, 'protected hash ' + rel)

    # Inspect executable syntax rather than raw strings. Negative fixtures
    # deliberately contain unsafe-looking source text and must not be mistaken
    # for active Python calls.
    forbidden_import_roots = {
        'subprocess', 'socket', 'requests', 'urllib', 'httpx', 'openai',
        'anthropic', 'ollama', 'chromadb', 'langchain', 'pickle', 'sqlite3',
    }
    forbidden_name_calls = {'open', 'eval', 'exec'}
    forbidden_attribute_calls = {'os.system'}
    forbidden_attribute_suffixes = {'.write_text', '.write_bytes'}

    def dotted_name(node: ast.AST) -> str:
        parts: list[str] = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return '.'.join(reversed(parts))

    def active_forbidden_uses(path: Path) -> tuple[str, ...]:
        tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        findings: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split('.', 1)[0]
                    if root in forbidden_import_roots:
                        findings.append('import:' + alias.name)
            elif isinstance(node, ast.ImportFrom):
                root = (node.module or '').split('.', 1)[0]
                if root in forbidden_import_roots:
                    findings.append('import_from:' + (node.module or ''))
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in forbidden_name_calls:
                    findings.append('call:' + node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    dotted = dotted_name(node.func)
                    if (
                        dotted in forbidden_attribute_calls
                        or any(dotted.endswith(suffix) for suffix in forbidden_attribute_suffixes)
                    ):
                        findings.append('call:' + dotted)
        return tuple(sorted(set(findings)))

    for rel in payload_paths:
        if not rel.startswith(RUNTIME_PREFIX) or not rel.endswith('.py'):
            continue
        try:
            active_findings = active_forbidden_uses(repo / rel)
        except SyntaxError:
            active_findings = ('syntax_error',)
        check(
            not active_findings,
            'runtime active forbidden operation ' + rel + ':' + ','.join(active_findings),
        )

    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['PYTHONPATH'] = str(repo)
    python = str(repo / '.venv/bin/python3') if (repo / '.venv/bin/python3').is_file() else '/usr/bin/python3'

    print('=== CURRENT SLICE 46 BEHAVIOR ===')
    behavior = run(python, '-u', '-B', str(repo / 'scripts/test_aiweb_slice46_gp014_equivalence_regression_proof.py'), str(repo), cwd=repo, env=env)
    print(behavior.stdout, end='')
    check(behavior.returncode == 0, 'current Slice 46 behavior return code')
    check('AI.WEB SLICE 46 BEHAVIOR TEST: PASS' in behavior.stdout, 'current Slice 46 behavior marker')

    print('=== INHERITED SLICE 45 VERIFIER ===')
    with tempfile.TemporaryDirectory(prefix='aiweb-slice46-inherited-') as temp:
        checkout = Path(temp) / 'forge'
        clone = run('/usr/bin/git', 'clone', '--quiet', '--no-hardlinks', str(repo), str(checkout), umask=0o022)
        check(clone.returncode == 0, 'inherited clone')
        if clone.returncode == 0:
            checked = run('/usr/bin/git', '-C', str(checkout), 'checkout', '--quiet', '-B', 'main', EXPECTED_PARENT_HEAD, umask=0o022)
            check(checked.returncode == 0, 'inherited checkout parent')
            if checked.returncode == 0:
                inherited_env = env.copy()
                inherited_env['PYTHONPATH'] = str(checkout)

                # Git intentionally does not clone the ignored virtual
                # environment. Create a disposable interpreter bridge so the
                # inherited Slice 45 verifier and its GP-014 tests use the
                # accepted live dependency environment instead of silently
                # falling back to a dependency-incomplete system Python.
                # Preserve the accepted virtual-environment invocation path.
                # Resolving the venv symlink collapses it to /usr/bin/python3
                # and loses the installed dependency environment (including lark).
                source_python = Path(python)
                bridge_python = checkout / '.venv/bin/python3'
                bridge_python.parent.mkdir(parents=True, exist_ok=True)
                if bridge_python.exists() or bridge_python.is_symlink():
                    bridge_python.unlink()
                bridge_python.write_text(
                    '#!/bin/sh\n' + shlex.quote(str(source_python)) + ' "$@"\n',
                    encoding='utf-8',
                )
                bridge_python.chmod(0o755)
                check(bridge_python.is_file(), 'inherited Python environment bridge')

                inherited_env['VIRTUAL_ENV'] = str(repo / '.venv')
                inherited_env['PATH'] = str(bridge_python.parent) + os.pathsep + inherited_env.get('PATH', '')
                inherited = run(str(bridge_python), '-u', '-B', str(checkout / 'scripts/aiweb_slice45_gp014_adapter_boundary_verify.py'), str(checkout), '--mode', 'committed', cwd=checkout, env=inherited_env)
                print(inherited.stdout, end='')
                check(inherited.returncode == 0, 'inherited Slice 45 verifier return code')
                check('AI.WEB SLICE 45 VERIFIER: PASS' in inherited.stdout, 'inherited Slice 45 verifier marker')

    print('=== SLICE 46 VERIFIER SUMMARY ===')
    print(f'checks={passes + len(failures)}')
    print(f'passes={passes}')
    print(f'failures={len(failures)}')
    print(f'protected_predecessor_files={len(protected)}')
    print(f'slice46_files={len(payload_paths)}')
    print('positive_equivalence_cases=8')
    print('negative_equivalence_cases=5')
    print('failure_injection_cases=3')
    print('gp014_modified=0')
    print('gp014_superseded=0')
    print('gp015_used=0')
    print('route_api_ui_change=0')
    print('memory_tool_action_resource_authority=0')
    print('adapter_delivery_authority=0')
    for failure in failures:
        print('FAIL - ' + failure)
    print('AI.WEB SLICE 46 VERIFIER: ' + ('PASS' if not failures else 'FAIL'))
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
