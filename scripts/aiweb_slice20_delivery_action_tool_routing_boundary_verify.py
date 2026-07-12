#!/usr/bin/env python3
"""Command-line verifier for Slice 20 delivery/action/tool-routing boundary."""

from __future__ import annotations

from pathlib import Path
import sys


def main(argv: list[str]) -> int:
    repo = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    repo_text = str(repo)
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)

    from aiweb_delivery_action_tool_routing_boundary_scaffold.verify import verify_slice20_boundary

    result = verify_slice20_boundary(repo)
    print(result.render())
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
