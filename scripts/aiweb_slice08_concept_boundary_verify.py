#!/usr/bin/env python3
"""Command verifier for Slice 8 concept boundary scaffold."""

from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
sys.path.insert(0, str(REPO))

from aiweb_concept_boundary_scaffold.verify import run_verification

print("============================================================")
print("AIWEB SLICE 8 CONCEPT LAYER AND SEMANTIC RELATION BOUNDARY SCAFFOLD VERIFIER")
print("============================================================")
print(f"Target repo: {REPO}")
passes, failures = run_verification(REPO)
print("PASSES:")
for item in passes:
    print(f"  PASS - {item}")
print("FAILURES:")
for item in failures:
    print(f"  FAIL - {item}")
if failures:
    print("VERDICT: FAIL - Slice 8 concept boundary scaffold verifier failed")
    raise SystemExit(1)
print("VERDICT: PASS - Slice 8 concept boundary scaffold verifier passed within Slice 8 scope")
