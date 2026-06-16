#!/usr/bin/env python3
"""CLI wrapper for Slice 7 scaffold verification."""

from pathlib import Path
import sys

REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
sys.path.insert(0, str(REPO))

from aiweb_meaning_law_trace_scaffold.verify import main

raise SystemExit(main([str(REPO)]))
