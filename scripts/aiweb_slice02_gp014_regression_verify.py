#!/usr/bin/env python3
"""Command-line verifier for AI.Web Slice 2 GP-014 regression scaffold."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    repo = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    sys.path.insert(0, str(repo))

    from aiweb_gp014_regression_scaffold.verify import verify_slice02_gp014_regression_scaffold

    result = verify_slice02_gp014_regression_scaffold(repo)

    print("============================================================")
    print("AIWEB SLICE 2 GP-014 REGRESSION SCAFFOLD VERIFIER")
    print("============================================================")
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in result["passes"]:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in result["failures"]:
        print(f"  FAIL - {item}")
    if result["passed"]:
        print("VERDICT: PASS - Slice 2 GP-014 regression scaffold verifier passed within Slice 2 scope")
        return 0
    print("VERDICT: FAIL - mandatory verifier failure blocks acceptance")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
