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
        print("usage: aiweb_slice16_selected_meaning_boundary_verify.py /home/nic/forge")
        return 2
    repo = Path(sys.argv[1]).resolve()
    _add_repo_to_path(repo)

    from aiweb_selected_meaning_boundary_scaffold.verify import run_verification

    passes, failures = run_verification(repo)
    print("=" * 60)
    print("AIWEB SLICE 16 SELECTED MEANING BOUNDARY SCAFFOLD VERIFIER")
    print("=" * 60)
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")
    if failures:
        print("VERDICT: FAIL - Slice 16 selected meaning scaffold verifier failed within Slice 16 scope")
        return 1
    print("VERDICT: PASS - Slice 16 selected meaning scaffold verifier passed within Slice 16 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
