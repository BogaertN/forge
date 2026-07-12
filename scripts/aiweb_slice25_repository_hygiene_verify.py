#!/usr/bin/env python3
"""Repository verifier CLI for AI.Web Slice 25."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aiweb_repository_hygiene_scaffold.verify import verify_slice25_boundary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Slice 25 repository-hygiene boundary."
    )
    parser.add_argument("repo", help="Forge repository root")
    parser.add_argument(
        "--state",
        required=True,
        choices=("structure", "applied", "committed"),
        help="Expected repository state",
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    result = verify_slice25_boundary(
        repo,
        state=args.state,
        require_live_repo_identity=args.state in {"applied", "committed"},
        check_protected_files=args.state in {"applied", "committed"},
    )

    print("AIWEB SLICE 25 REPOSITORY HYGIENE VERIFIER")
    print("slice=Slice 25")
    print("title=Dirty-State Disposition and Repository Hygiene Decision")
    print(f"target_repo={repo}")
    print(f"expected_state={result.state}")
    print(f"checked_file_count={len(result.checked_files)}")

    if result.failures:
        print("FAILURES:")
        for failure in result.failures:
            print(f"- {failure}")
        print("VERDICT: FAIL")
        return 1

    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
