#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

ROOT = Path('/home/nic/forge')
APPCTL = ROOT / 'scripts' / 'aiweb_os_appctl.py'
DESKTOP = ROOT / 'desktop_entries' / 'aiweb-os-operator-console.desktop'

checks: list[tuple[str, bool, str]] = []

def check(name: str, cond: bool, detail: str = '') -> None:
    checks.append((name, cond, detail))
    print(('[PASS]' if cond else '[FAIL]'), name, detail)

text = APPCTL.read_text(encoding='utf-8') if APPCTL.exists() else ''
check('appctl_exists', APPCTL.exists(), str(APPCTL))
check('desktop_entry_exists', DESKTOP.exists(), str(DESKTOP))

try:
    subprocess.run([sys.executable, '-m', 'py_compile', str(APPCTL)], check=True, capture_output=True, text=True)
    check('appctl_py_compile', True)
except Exception as exc:
    check('appctl_py_compile', False, repr(exc))

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
    'Patch 263R',
    'single_instance_lock',
    'LOCK_FILE',
    'operator_window_already_open',
    'find_operator_window_pid',
    'focus_operator_window',
    'process_scan',
    'appctl.lock',
    'single_instance_lock_state',
    'operator_window_pid_source',
    'start requested while operator window already open',
    '--app=',
    '--user-data-dir=',
    'operator-console-chrome-profile',
    'External Forge backend stop is intentionally not implemented',
]
for term in required_terms:
    check(f'appctl_contains_{term}', term in text)

for forbidden in ['npm run dev', 'CAPTURE_RMC', 'APPROVE_RMC_PROMOTION', 'identity_vault', 'chromadb']:
    check(f'appctl_forbidden_absent_{forbidden}', forbidden not in text)

# Import the appctl module and behavior-test idempotent start without launching anything.
spec = importlib.util.spec_from_file_location('aiweb_os_appctl_test_mod', APPCTL)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)  # type: ignore[union-attr]

open_calls: list[str] = []
focus_calls: list[str] = []
build_calls: list[str] = []
backend_calls: list[str] = []

class DummyLock:
    def __enter__(self):
        return None
    def __exit__(self, exc_type, exc, tb):
        return False

def fake_status():
    return mod.ServiceStatus(
        backend_port_open=True,
        backend_owned=True,
        backend_supervisor_pid=111,
        forge_child_pid=112,
        operator_window_owned=True,
        operator_window_pid=222,
        operator_window_pid_source='pidfile',
        ui_root_exists=True,
        ui_dist_exists=True,
        chrome_available=True,
        npm_available=True,
        operator_url=mod.OPERATOR_URL,
        single_instance_lock_path=str(mod.LOCK_FILE),
        single_instance_lock_state='unlocked',
        logs=str(mod.LOG_ROOT),
    )

with mock.patch.object(mod, 'single_instance_lock', lambda: DummyLock()), \
     mock.patch.object(mod, 'build_react_if_needed', lambda force=False: build_calls.append(str(force)) or True), \
     mock.patch.object(mod, 'start_backend_if_needed', lambda: backend_calls.append('backend')), \
     mock.patch.object(mod, 'operator_window_already_open', lambda: True), \
     mock.patch.object(mod, 'open_operator_window', lambda: open_calls.append('open') or 999), \
     mock.patch.object(mod, 'focus_operator_window', lambda: focus_calls.append('focus') or True), \
     mock.patch.object(mod, 'status', fake_status):
    rc = mod.start(force_build=False, no_window=False)

check('start_existing_window_returns_ok', rc == 0)
check('start_existing_window_builds_once', build_calls == ['False'], str(build_calls))
check('start_existing_window_checks_backend', backend_calls == ['backend'], str(backend_calls))
check('start_existing_window_focuses_existing', focus_calls == ['focus'], str(focus_calls))
check('start_existing_window_does_not_open_duplicate', open_calls == [], str(open_calls))

# Behavior-test window detection with app profile in cmdline.
with mock.patch.object(mod, 'cmdline_for_pid', lambda pid: f'google-chrome --app={mod.OPERATOR_URL} --user-data-dir={mod.CHROME_PROFILE} --class={mod.APP_CLASS}'):
    check('operator_window_process_detection', mod.is_operator_window_process(333))

# Status command must remain callable without starting services.
try:
    res = subprocess.run([str(APPCTL), 'status', '--json'], check=True, capture_output=True, text=True, timeout=10)
    data = json.loads(res.stdout)
    check('status_json_callable', 'operator_url' in data and 'single_instance_lock_state' in data and 'operator_window_pid_source' in data)
except Exception as exc:
    check('status_json_callable', False, repr(exc))

failed = [name for name, ok, _ in checks if not ok]
print(f'Total: {len(checks)}')
print(f'Passed: {len(checks) - len(failed)}')
print(f'Failed: {len(failed)}')
if failed:
    print('FAILED_CHECKS:', ', '.join(failed))
    print('RESULT: patch263R_aiweb_os_single_instance_tests_pass=False')
    raise SystemExit(1)
print('RESULT: patch263R_aiweb_os_single_instance_tests_pass=True')
