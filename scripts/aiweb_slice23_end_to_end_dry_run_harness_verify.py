#!/usr/bin/env python3
"""Command-line verifier wrapper for Slice 23 dry-run harness scaffold."""

from __future__ import annotations

from pathlib import Path
import sys


def main() -> int:
    repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    if str(repo.resolve()) not in sys.path:
        sys.path.insert(0, str(repo.resolve()))

    from aiweb_end_to_end_dry_run_harness_scaffold.verify import verify_slice23_boundary

    result = verify_slice23_boundary(repo, require_git_context=True)
    print(result.render())
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
