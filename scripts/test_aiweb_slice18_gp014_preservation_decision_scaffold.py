#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def _add_repo_to_path(repo: Path) -> None:
    text = str(repo)
    if text not in sys.path:
        sys.path.insert(0, text)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: test_aiweb_slice18_gp014_preservation_decision_scaffold.py /home/nic/forge")
        return 2
    repo = Path(sys.argv[1]).resolve()
    _add_repo_to_path(repo)

    from aiweb_gp014_preservation_decision_scaffold.verify import run_verification

    passes, failures = run_verification(repo)
    print("=" * 72)
    print("AIWEB SLICE 18 GP-014 PRESERVATION / WRAPPER DECISION TEST")
    print("=" * 72)
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")
    if failures:
        print("VERDICT: FAIL - Slice 18 GP-014 preservation decision boundary failed")
        return 1
    print("VERDICT: PASS - Slice 18 GP-014 preservation decision boundary passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
