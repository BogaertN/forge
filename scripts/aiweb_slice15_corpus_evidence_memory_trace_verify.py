#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
sys.path.insert(0, str(REPO))

from aiweb_corpus_evidence_memory_trace_scaffold.verify import run_verification

passes, failures = run_verification(REPO)
print("=" * 60)
print("AIWEB SLICE 15 CORPUS / EVIDENCE / MEMORY / TRACE SEPARATION SCAFFOLD VERIFIER")
print("=" * 60)
print(f"Target repo: {REPO}")
print("PASSES:")
for item in passes:
    print(f"  PASS - {item}")
print("FAILURES:")
for item in failures:
    print(f"  FAIL - {item}")
if failures:
    print("VERDICT: FAIL - Slice 15 corpus/evidence/memory/trace scaffold verifier failed")
    sys.exit(1)
print("VERDICT: PASS - Slice 15 corpus/evidence/memory/trace scaffold verifier passed within Slice 15 scope")
