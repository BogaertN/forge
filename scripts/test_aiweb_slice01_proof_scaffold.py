#!/usr/bin/env python3
"""Deterministic behavior test for AI.Web Slice 1 proof scaffold."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


def main() -> int:
    repo = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else Path("/home/nic/forge")
    sys.path.insert(0, str(repo))

    from aiweb_proof_scaffold import build_receipt, sha256_file, validate_receipt, write_receipt
    from aiweb_proof_scaffold.schema import BLOCKED_AUTHORITIES, SCHEMA_VERSION, SLICE_ID

    failures = []
    passes = []

    try:
        receipt = build_receipt(
            receipt_type="slice01_behavior_test",
            status="PASS",
            target_repo=str(repo),
            head_commit="behavior-test-only",
            authority_basis=["Document 10 Slice 1", "Document 9 proof law"],
            fresh_packet_identity={"packet_id": "behavior-test-only"},
            changed_files=["aiweb_proof_scaffold/schema.py"],
            behavior_tests=[{"name": "receipt_roundtrip", "status": "PASS"}],
            verifier_gates=[{"name": "schema_validation", "status": "PASS"}],
            rollback={"required": False, "reason": "additive scaffold behavior test only"},
            accepted_scope={"claim": "Receipt scaffold behavior test only. No language authority accepted."},
            notes=["No memory, evidence, corpus, resource, delivery, UI, model, vector or action authority."],
        )
        passes.append("build_receipt returned a receipt")
    except Exception as exc:
        failures.append(f"build_receipt failed: {exc}")
        receipt = {}

    if receipt.get("schema_version") == SCHEMA_VERSION:
        passes.append("schema_version matches")
    else:
        failures.append("schema_version mismatch")

    if receipt.get("slice_id") == SLICE_ID:
        passes.append("slice_id matches")
    else:
        failures.append("slice_id mismatch")

    missing_blocked = [item for item in BLOCKED_AUTHORITIES if item not in receipt.get("blocked_authorities", [])]
    if not missing_blocked:
        passes.append("all blocked authorities preserved")
    else:
        failures.append("blocked authorities missing: " + ", ".join(missing_blocked))

    validation = validate_receipt(receipt)
    if not validation:
        passes.append("valid receipt passes validation")
    else:
        failures.append("valid receipt failed validation: " + "; ".join(validation))

    invalid = dict(receipt)
    invalid.pop("slice_id", None)
    invalid_failures = validate_receipt(invalid)
    if invalid_failures:
        passes.append("invalid receipt fails validation")
    else:
        failures.append("invalid receipt unexpectedly passed validation")

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "receipt.json"
        write_receipt(receipt, out)
        loaded = json.loads(out.read_text(encoding="utf-8"))
        if loaded.get("slice_id") == SLICE_ID:
            passes.append("write_receipt roundtrip works")
        else:
            failures.append("write_receipt roundtrip failed")
        digest = sha256_file(out)
        if len(digest) == 64 and all(c in "0123456789abcdef" for c in digest):
            passes.append("sha256_file returns valid hex digest")
        else:
            failures.append("sha256_file returned invalid digest")

    print("============================================================")
    print("AIWEB SLICE 1 PROOF SCAFFOLD BEHAVIOR TEST")
    print("============================================================")
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")
    if failures:
        print("VERDICT: FAIL - behavior test failed")
        return 1
    print("VERDICT: PASS - behavior test passed within Slice 1 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
