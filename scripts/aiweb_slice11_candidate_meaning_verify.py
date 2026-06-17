#!/usr/bin/env python3
"""CLI verifier for Slice 11 candidate meaning boundary scaffold."""

from __future__ import annotations

from pathlib import Path
import sys


def main() -> int:
    repo = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from aiweb_candidate_meaning_boundary_scaffold.verify import run_verification

    passes, failures = run_verification(repo)
    print("=" * 60)
    print("AIWEB SLICE 11 CANDIDATE MEANING BOUNDARY SCAFFOLD VERIFIER")
    print("=" * 60)
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")
    if failures:
        print("VERDICT: FAIL - Slice 11 candidate meaning boundary scaffold verifier failed")
        return 1
    print("VERDICT: PASS - Slice 11 candidate meaning boundary scaffold verifier passed within Slice 11 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
