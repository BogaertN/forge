#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path('/home/nic/forge')
FILES = [
    'scripts/aiweb_os_appctl.py',
    'scripts/aiweb-os-start',
    'scripts/aiweb-os-stop',
    'scripts/aiweb-os-status',
    'scripts/aiweb-os-restart',
    'scripts/install_aiweb_os_operator_console_desktop.sh',
    'scripts/README_patch263_aiweb_os_desktop_orchestrator.md',
    'scripts/test_patch263_aiweb_os_desktop_orchestrator.py',
    'scripts/patch263_aiweb_os_desktop_orchestrator_verify.py',
    'desktop_entries/aiweb-os-operator-console.desktop',
    'SHA256SUMS.txt',
]
checks: list[tuple[str, bool, str]] = []

def check(name: str, cond: bool, detail: str = '') -> None:
    checks.append((name, cond, detail))
    print(('[PASS]' if cond else '[FAIL]'), name, detail)

for rel in FILES:
    check(f'file_exists_{rel}', (ROOT / rel).exists(), rel)

sha = ROOT / 'SHA256SUMS.txt'
if sha.exists():
    bad = [line for line in sha.read_text(encoding='utf-8').splitlines() if any(x in line for x in ['__pycache__', '.pyc', '.venv', 'node_modules', 'chroma_db', '.sqlite', '.db'])]
    check('sha_excludes_bad_artifacts', not bad, str(bad[:3]))
    try:
        res = subprocess.run(['sha256sum', '-c', 'SHA256SUMS.txt'], cwd=str(ROOT), text=True, capture_output=True, timeout=20)
        check('sha_manifest_hashes_ok', res.returncode == 0, res.stdout[-300:] + res.stderr[-300:])
    except Exception as exc:
        check('sha_manifest_hashes_ok', False, repr(exc))

try:
    subprocess.run([sys.executable, '-m', 'py_compile', str(ROOT / 'scripts/aiweb_os_appctl.py'), str(ROOT / 'scripts/test_patch263_aiweb_os_desktop_orchestrator.py')], check=True, capture_output=True, text=True)
    check('py_compile_scripts', True)
except Exception as exc:
    check('py_compile_scripts', False, repr(exc))

try:
    res = subprocess.run([str(ROOT / 'scripts/test_patch263_aiweb_os_desktop_orchestrator.py')], cwd=str(ROOT), text=True, capture_output=True, timeout=20)
    check('behavior_test_passes', res.returncode == 0, res.stdout[-500:] + res.stderr[-500:])
except Exception as exc:
    check('behavior_test_passes', False, repr(exc))

failed = [name for name, ok, _ in checks if not ok]
print('─' * 72)
print(f'Total: {len(checks)}')
print(f'Passed: {len(checks) - len(failed)}')
print(f'Failed: {len(failed)}')
if failed:
    print('FAILED_CHECKS:', ', '.join(failed))
    print('RESULT: PATCH263_AIWEB_OS_DESKTOP_ORCHESTRATOR_VERIFY_OK_FALSE')
    raise SystemExit(1)
print('RESULT: PATCH263_AIWEB_OS_DESKTOP_ORCHESTRATOR_VERIFY_OK')
