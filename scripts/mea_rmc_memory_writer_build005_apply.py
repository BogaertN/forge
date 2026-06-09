#!/usr/bin/env python3
"""MEA-RMC-MEMORY-WRITER-BUILD-005 — controlled JSONL memory write CLI.

This CLI is the only live write activation surface delivered by Build 005. It
requires the explicit operator token and all three proof-bindings requested by
the MEA memory writer design. It does not expose an HTTP mutation route.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Commit one proof-bound sealed MEA manifest memory record to Forge-owned JSONL.")
    parser.add_argument("--forge-root", required=True, type=Path)
    parser.add_argument("--sealed-manifest-hash", required=True)
    parser.add_argument("--seal-receipt-hash", required=True)
    parser.add_argument("--memory-writer-preview-hash", required=True)
    parser.add_argument("--approval-token", required=True)
    parser.add_argument("--write-effective-at-utc", required=True)
    args = parser.parse_args()

    forge_root = args.forge_root.expanduser().resolve()
    if not (forge_root / "rmc_engine_v1" / "mea" / "controlled_manifest_memory_writer.py").is_file():
        raise SystemExit(f"Build 005 writer module not installed under: {forge_root}")
    sys.path.insert(0, str(forge_root))

    from rmc_engine_v1.mea import evaluate_controlled_manifest_memory_write_request  # noqa: WPS433

    response = evaluate_controlled_manifest_memory_write_request(
        {
            "approval_token": args.approval_token,
            "sealed_manifest_hash": args.sealed_manifest_hash,
            "seal_receipt_hash": args.seal_receipt_hash,
            "memory_writer_preview_hash": args.memory_writer_preview_hash,
        },
        store_root=forge_root / "runtime_state" / "mea_problem_manifest_store_v1",
        memory_root=forge_root / "memory" / "mea_manifest_memory_v1",
        now_utc=args.write_effective_at_utc,
    )
    print(json.dumps(response, indent=2, sort_keys=True, ensure_ascii=False))
    if response.get("gate_status") not in {
        "COMMITTED_APPEND_ONLY_JSONL_MEA_MEMORY_RECORD",
        "CONTROLLED_MEA_MEMORY_RECORD_ALREADY_PERSISTED_IDEMPOTENT_NO_WRITE",
    }:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
