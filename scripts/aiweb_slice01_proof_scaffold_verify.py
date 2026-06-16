#!/usr/bin/env python3
"""Command wrapper for AI.Web Slice 1 proof scaffold verifier."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    repo = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else Path("/home/nic/forge")
    sys.path.insert(0, str(repo))
    from aiweb_proof_scaffold.verify import main as verify_main
    return verify_main([str(repo)])


if __name__ == "__main__":
    raise SystemExit(main())
