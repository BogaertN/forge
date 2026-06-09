#!/usr/bin/env python3
"""Print the current MEA Memory Capsule compatibility preview; performs no writes."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", type=Path, required=True)
    args = parser.parse_args()
    forge_root = args.forge_root.resolve()
    sys.path.insert(0, str(forge_root))
    from contribution_economy_v1.capsules import build_current_committed_mea_capsule_preview
    print(json.dumps(build_current_committed_mea_capsule_preview(forge_root=forge_root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
