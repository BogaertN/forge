#!/usr/bin/env python3
"""Command wrapper for Slice 6 verifier."""

from __future__ import annotations

import sys
from pathlib import Path


def _add_repo_to_path(repo: Path) -> None:
    repo_text = str(repo.resolve())
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)


def main() -> int:
    repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    _add_repo_to_path(repo)
    from aiweb_authority_scanner_scaffold.verify import main as verify_main

    return verify_main([str(repo)])


if __name__ == "__main__":
    raise SystemExit(main())
