#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path('/home/nic/forge')
APPCTL = ROOT / 'scripts' / 'aiweb_os_appctl.py'
DESKTOP = ROOT / 'desktop_entries' / 'aiweb-os-operator-console.desktop'
INSTALL = ROOT / 'scripts' / 'install_aiweb_os_operator_console_desktop.sh'
WRAPPERS = [ROOT / 'scripts' / f'aiweb-os-{name}' for name in ('start','stop','status','restart')]

checks: list[tuple[str, bool, str]] = []

def check(name: str, cond: bool, detail: str = '') -> None:
    checks.append((name, cond, detail))
    print(('[PASS]' if cond else '[FAIL]'), name, detail)

text = APPCTL.read_text(encoding='utf-8') if APPCTL.exists() else ''
check('appctl_exists', APPCTL.exists(), str(APPCTL))
check('desktop_entry_exists', DESKTOP.exists(), str(DESKTOP))
check('install_script_exists', INSTALL.exists(), str(INSTALL))
for w in WRAPPERS:
    check(f'wrapper_exists_{w.name}', w.exists(), str(w))

# Syntax / py_compile
try:
    subprocess.run([sys.executable, '-m', 'py_compile', str(APPCTL)], check=True, capture_output=True, text=True)
    check('appctl_py_compile', True)
except Exception as exc:
    check('appctl_py_compile', False, repr(exc))

# AST-level safety: no shell=True.
try:
    tree = ast.parse(text)
    shell_true = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    shell_true.append(node.lineno)
    check('no_shell_true', not shell_true, str(shell_true))
except Exception as exc:
    check('ast_parse', False, repr(exc))

required_terms = [
    'npm run build',
    'source_newer_than_dist',
    'supervise',
    'pty.fork',
    'forge-ui-start',
    '--app=',
    '--user-data-dir=',
    'operator-console-chrome-profile',
    'port_open',
    'backend_owned',
    'External Forge backend stop is intentionally not implemented',
]
for term in required_terms:
    check(f'appctl_contains_{term}', term in text)

for forbidden in ['npm run dev', 'CAPTURE_RMC', 'APPROVE_RMC_PROMOTION', 'identity_vault', 'chromadb']:
    check(f'appctl_forbidden_absent_{forbidden}', forbidden not in text)

desk = DESKTOP.read_text(encoding='utf-8') if DESKTOP.exists() else ''
check('desktop_terminal_false', 'Terminal=false' in desk)
check('desktop_exec_appctl_start', 'Exec=/home/nic/forge/scripts/aiweb_os_appctl.py start' in desk)
check('desktop_clean_name', 'Name=AI.Web OS Operator Console' in desk)

for w in WRAPPERS:
    wt = w.read_text(encoding='utf-8') if w.exists() else ''
    check(f'wrapper_execs_appctl_{w.name}', 'aiweb_os_appctl.py' in wt and 'exec ' in wt)

# Status command must be callable without starting services.
try:
    res = subprocess.run([str(APPCTL), 'status', '--json'], check=True, capture_output=True, text=True, timeout=10)
    check('status_json_callable', 'operator_url' in res.stdout and 'backend_port_open' in res.stdout)
except Exception as exc:
    check('status_json_callable', False, repr(exc))

failed = [name for name, ok, _ in checks if not ok]
print(f'Total: {len(checks)}')
print(f'Passed: {len(checks) - len(failed)}')
print(f'Failed: {len(failed)}')
if failed:
    print('FAILED_CHECKS:', ', '.join(failed))
    print('RESULT: patch263_aiweb_os_desktop_orchestrator_tests_pass=False')
    raise SystemExit(1)
print('RESULT: patch263_aiweb_os_desktop_orchestrator_tests_pass=True')
