#!/usr/bin/env python3
"""Patch 263S — AI.Web OS deferred lifecycle action runner.

This script is intentionally tiny and allowlist-only. It exists so the browser-facing
backend can return a confirmation response before a restart/stop action interrupts the
HTTP connection. It accepts only two actions: restart and shutdown.
"""

from __future__ import annotations

import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

FORGE_ROOT = Path('/home/nic/forge')
LOG_DIR = FORGE_ROOT / 'logs' / 'aiweb_os'
ALLOWLIST = {
    'restart': FORGE_ROOT / 'scripts' / 'aiweb-os-restart',
    'shutdown': FORGE_ROOT / 'scripts' / 'aiweb-os-stop',
}


def _log(message: str) -> None:
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).isoformat()
        with (LOG_DIR / 'lifecycle_actions.log').open('a', encoding='utf-8') as fh:
            fh.write(f'{stamp} patch263S {message}\n')
    except Exception:
        # Lifecycle action logging must never prevent the fixed action from running.
        pass


def main(argv: list[str]) -> int:
    action = argv[1] if len(argv) > 1 else ''
    if action not in ALLOWLIST:
        _log(f'REFUSED unsupported_action={action!r}')
        return 64

    wrapper = ALLOWLIST[action]
    if not wrapper.exists():
        _log(f'REFUSED missing_wrapper action={action} path={wrapper}')
        return 66

    _log(f'SCHEDULED action={action} wrapper={wrapper}')
    time.sleep(0.75)

    try:
        result = subprocess.run([str(wrapper)], cwd=str(FORGE_ROOT), text=True, capture_output=True, timeout=60, check=False)
        _log(f'COMPLETE action={action} returncode={result.returncode} stdout_tail={result.stdout[-400:].replace(chr(10), " | ")} stderr_tail={result.stderr[-400:].replace(chr(10), " | ")}')
        return int(result.returncode)
    except Exception as exc:
        _log(f'ERROR action={action} error={str(exc)[:500]}')
        return 70


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
