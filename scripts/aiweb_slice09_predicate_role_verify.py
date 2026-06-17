#!/usr/bin/env python3
"""Command verifier for Slice 9 predicate-role frame boundary scaffold."""

from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
sys.path.insert(0, str(REPO))

from aiweb_predicate_role_boundary_scaffold.verify import run_verification

print("=" * 60)
print("AIWEB SLICE 9 PREDICATE-ROLE FRAME BOUNDARY SCAFFOLD VERIFIER")
print("=" * 60)
print(f"Target repo: {REPO}")
passes, failures = run_verification(REPO)
print("PASSES:")
for item in passes:
    print(f"  PASS - {item}")
print("FAILURES:")
for item in failures:
    print(f"  FAIL - {item}")
if failures:
    print("VERDICT: FAIL - Slice 9 predicate-role boundary scaffold verifier failed")
    raise SystemExit(1)
print("VERDICT: PASS - Slice 9 predicate-role boundary scaffold verifier passed within Slice 9 scope")
