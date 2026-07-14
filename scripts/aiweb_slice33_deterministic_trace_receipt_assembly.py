#!/usr/bin/env python3
"""Offline developer command for Slice 33 trace and receipt assembly."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
REPO_ROOT = str(Path(__file__).resolve().parents[1])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from aiweb_language_core_bootstrap.trace_receipt import (
    STATUS_COMPLETED,
    STATUS_REFUSED_DISABLED,
    assemble_trace_receipt,
    build_trace_receipt_assembly_state,
    list_trace_flows,
    validate_trace_receipt_assembly_result,
)


def _json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Assemble a deterministic in-memory Slice 33 derivation trace and "
            "receipt for one exact offline fixture flow."
        )
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list-flows", action="store_true")
    group.add_argument("--flow")
    parser.add_argument(
        "--enable-offline-trace-receipt",
        action="store_true",
        help="Explicitly enable read-only fixture execution and assembly.",
    )
    args = parser.parse_args()

    if args.list_flows:
        print(_json([flow.to_dict() for flow in list_trace_flows()]))
        return 0

    state = build_trace_receipt_assembly_state(
        explicit_offline_developer_enable=args.enable_offline_trace_receipt,
    )
    result = assemble_trace_receipt(args.flow, assembly_state=state)
    print(_json(result.to_dict()))

    if result.status == STATUS_COMPLETED:
        return 0 if validate_trace_receipt_assembly_result(result).ok else 4
    if result.status == STATUS_REFUSED_DISABLED:
        return 2
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
