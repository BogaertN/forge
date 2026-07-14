#!/usr/bin/env python3
"""Explicit offline developer command for Slice 32."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
REPO_ROOT = str(Path(__file__).resolve().parents[1])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from aiweb_language_core_bootstrap.component_loading import (
    FIXTURE_STATIC_COMPONENT_LOADING,
    STATUS_COMPLETED_STATIC_LOADING,
    build_component_loading_state,
    get_component_loading_fixture,
    list_component_loading_fixtures,
    run_component_loading_fixture,
)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description="AI.Web Slice 32 static component-loading fixture command",
    )
    value.add_argument("--list-fixtures", action="store_true")
    value.add_argument("--fixture", choices=(FIXTURE_STATIC_COMPONENT_LOADING,))
    value.add_argument(
        "--enable-offline-component-loading",
        action="store_true",
        help="Explicitly enable the fixture-only static component loader.",
    )
    return value


def main() -> int:
    args = parser().parse_args()
    if args.list_fixtures:
        print(
            json.dumps(
                [fixture.__dict__ if hasattr(fixture, "__dict__") else {
                    field: getattr(fixture, field)
                    for field in fixture.__dataclass_fields__
                } for fixture in list_component_loading_fixtures()],
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    if not args.fixture:
        parser().error("--fixture is required unless --list-fixtures is used")
    fixture = get_component_loading_fixture(args.fixture)
    state = build_component_loading_state(
        enabled=args.enable_offline_component_loading,
    )
    result = run_component_loading_fixture(fixture, loading_state=state)
    print(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":")))
    return 0 if result.status == STATUS_COMPLETED_STATIC_LOADING else 2


if __name__ == "__main__":
    raise SystemExit(main())
