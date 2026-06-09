#!/usr/bin/env python3
"""
Patch 274R — Legacy desktop launcher compatibility wrapper.

The old desktop icon used this file and opened a visible terminal / standalone
Terminus-style browser path. For final-product behavior this wrapper now delegates
to aiweb_os_appctl.py start so startup opens only the clean Operator Console app
window. The high-security Terminus shell stays hidden until opened inside the
Operator Console.

Boundary: no shell execution mode, no arbitrary command input, no browser tab open, no RMC
memory write, no Identity Vault write, no Chroma write, no LLM call.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

APPCTL = Path.home() / "forge" / "scripts" / "aiweb_os_appctl.py"


def main() -> int:
    if not APPCTL.exists():
        print(f"ERROR: appctl not found: {APPCTL}", file=sys.stderr)
        return 1
    result = subprocess.run([sys.executable, str(APPCTL), "start"], text=True)
    return int(result.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
