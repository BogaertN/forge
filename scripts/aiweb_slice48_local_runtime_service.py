#!/usr/bin/env python3
"""Explicit entry point for the Slice 48 local-only runtime service."""
from __future__ import annotations

import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from aiweb_language_core_bootstrap.local_runtime_service.control import cli_main


if __name__ == "__main__":
    raise SystemExit(cli_main(entry_script=Path(__file__).resolve()))
