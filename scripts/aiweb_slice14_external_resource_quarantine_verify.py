#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
sys.path.insert(0, str(REPO))

from aiweb_external_resource_quarantine_scaffold.verify import run_verification

passes, failures = run_verification(REPO)
print("=" * 60)
print("AIWEB SLICE 14 EXTERNAL RESOURCE QUARANTINE SCAFFOLD VERIFIER")
print("=" * 60)
print(f"Target repo: {REPO}")
print("PASSES:")
for item in passes:
    print(f"  PASS - {item}")
print("FAILURES:")
for item in failures:
    print(f"  FAIL - {item}")
if failures:
    print("VERDICT: FAIL - Slice 14 external resource quarantine scaffold verifier failed")
    sys.exit(1)
print("VERDICT: PASS - Slice 14 external resource quarantine scaffold verifier passed within Slice 14 scope")
