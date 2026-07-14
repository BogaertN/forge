#!/usr/bin/env python3
"""Explicit offline developer command for the Slice 31 fixture adapter."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.dont_write_bytecode = True

REPO_ROOT = str(Path(__file__).resolve().parents[1])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from aiweb_language_core_bootstrap.bootstrap_adapter import (
    FIXTURE_DISABLED_DEFAULT,
    FIXTURE_EXPLICIT_OFFLINE_INSPECTION,
    STATUS_COMPLETED_INSPECTION,
    build_bootstrap_adapter_state,
    get_bootstrap_fixture,
    list_bootstrap_fixtures,
    run_bootstrap_fixture,
)
from aiweb_language_core_bootstrap.schema import canonical_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run one accepted synthetic Slice 31 fixture entirely offline. "
            "No file input, free-form text, component loading, route, network, "
            "memory, delivery, tool, or action authority is available."
        )
    )
    parser.add_argument(
        "--list-fixtures",
        action="store_true",
        help="Print the exact built-in fixture catalog and stop.",
    )
    parser.add_argument(
        "--fixture",
        choices=(
            FIXTURE_DISABLED_DEFAULT,
            FIXTURE_EXPLICIT_OFFLINE_INSPECTION,
        ),
        help="Exact governed synthetic fixture name.",
    )
    parser.add_argument(
        "--enable-offline-fixture-adapter",
        action="store_true",
        help=(
            "Explicitly enable only the in-memory offline fixture adapter for "
            "this process. It does not load a registered component."
        ),
    )
    return parser


def main(argv: tuple[str, ...] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_fixtures:
        print(
            canonical_json(
                tuple(fixture.to_dict() for fixture in list_bootstrap_fixtures())
            )
        )
        return 0

    if not args.fixture:
        print(
            canonical_json(
                {
                    "status": "refused_missing_fixture",
                    "reason_code": "exact_fixture_name_required",
                    "side_effects_performed": False,
                }
            )
        )
        return 2

    fixture = get_bootstrap_fixture(args.fixture)
    if fixture is None:
        print(
            canonical_json(
                {
                    "status": "held_fixture_not_accepted",
                    "reason_code": "fixture_not_in_exact_static_catalog",
                    "side_effects_performed": False,
                }
            )
        )
        return 2

    state = build_bootstrap_adapter_state(
        explicit_offline_developer_enable=(
            args.enable_offline_fixture_adapter
        )
    )
    result = run_bootstrap_fixture(
        fixture,
        adapter_state=state,
    )
    print(canonical_json(result))

    if result.status == fixture.expected_result_status:
        return 0
    if result.status == STATUS_COMPLETED_INSPECTION:
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
