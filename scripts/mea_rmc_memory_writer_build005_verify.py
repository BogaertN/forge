#!/usr/bin/env python3
"""MEA-RMC-MEMORY-WRITER-BUILD-005 — installed-state readback verifier."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

EXPECTED_MANIFEST_HASH = "852feb2c1491683bca39d89ee3d86e43e4f8fe9aecad2c403c9be70018c95a83"
EXPECTED_SEAL_RECEIPT_HASH = "1066fac6e124cb1300a50f39aaaf42c987f310184902dee303615d897e843e52"
EXPECTED_PREVIEW_HASH = "4cc7f39eb2c2110c282ab1ef43183826c7ea6d27b7f68b78164d708cfaa92115"
EXPECTED_CANDIDATE_ID = "cg_hypothesis_001"


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix not in {".pyc", ".pyo"}):
        digest.update(f"{item.relative_to(root).as_posix()}\0{hashlib.sha256(item.read_bytes()).hexdigest()}\n".encode("utf-8"))
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", required=True, type=Path)
    parser.add_argument("--expected-mea-state-digest", default=None)
    args = parser.parse_args()
    forge_root = args.forge_root.expanduser().resolve()
    sys.path.insert(0, str(forge_root))
    from rmc_engine_v1.mea import controlled_memory_writer_status  # noqa: WPS433

    status = controlled_memory_writer_status(memory_root=forge_root / "memory" / "mea_manifest_memory_v1")
    memory_root = forge_root / "memory" / "mea_manifest_memory_v1"
    ledger = memory_root / "hypothesis_test_required_records.jsonl"
    entries = []
    if ledger.is_file():
        entries = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
    record = entries[0].get("memory_record", {}) if entries else {}
    source = record.get("source_binding", {}) if isinstance(record, dict) else {}
    preview = record.get("patch299_preview_binding", {}) if isinstance(record, dict) else {}
    receipt_files = sorted((memory_root / "receipts").glob("*_memory_write_receipt.json")) if (memory_root / "receipts").is_dir() else []
    receipt = json.loads(receipt_files[0].read_text(encoding="utf-8")) if len(receipt_files) == 1 else {}
    receipt_body = {key: value for key, value in receipt.items() if key != "receipt_hash"}
    receipt_hash_valid = bool(receipt) and hashlib.sha256(
        json.dumps(receipt_body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest() == receipt.get("receipt_hash")

    checks = {
        "status_ok": status.get("status") == "OK",
        "ledger_integrity_verified": status.get("ledger_verification", {}).get("valid") is True,
        "exactly_one_record": status.get("record_count") == 1 and len(entries) == 1,
        "record_schema_locked": record.get("schema_version") == "mea_manifest_memory_record_v1_build005",
        "record_candidate_locked": record.get("candidate_id") == EXPECTED_CANDIDATE_ID,
        "record_claim_is_hypothesis": record.get("claim_status") == "hypothesis",
        "record_proof_debt_preserved": record.get("proof_debt") == 0.85,
        "record_memory_tier_bounded": record.get("memory_tier") == "hypothesis_test_required_record",
        "record_not_verified_fact": record.get("claim_semantics", {}).get("verified_fact") is False,
        "sealed_manifest_hash_bound": source.get("sealed_manifest_hash") == EXPECTED_MANIFEST_HASH,
        "seal_receipt_hash_bound": source.get("seal_receipt_hash") == EXPECTED_SEAL_RECEIPT_HASH,
        "preview_hash_bound": preview.get("memory_writer_preview_hash") == EXPECTED_PREVIEW_HASH,
        "renderer_remains_blocked": record.get("renderer_permission_boundary", {}).get("renderer_output_permitted") is False,
        "chroma_blocked": record.get("storage_boundary", {}).get("writes_chroma") is False,
        "identity_vault_blocked": record.get("storage_boundary", {}).get("writes_identity_vault") is False,
        "contribution_economy_blocked": record.get("storage_boundary", {}).get("writes_contribution_economy") is False,
        "ct_blocked": record.get("storage_boundary", {}).get("mints_contribution_tokens") is False,
    }
    if args.expected_mea_state_digest:
        checks["mea_runtime_state_unchanged"] = tree_hash(forge_root / "runtime_state" / "mea_problem_manifest_store_v1") == args.expected_mea_state_digest

    passed = 0
    failed = 0
    for name, result in checks.items():
        print(f"  [{'PASS' if result else 'FAIL'}] {name}")
        if result:
            passed += 1
        else:
            failed += 1
    print(f"RESULT: MEA-RMC-MEMORY-WRITER-BUILD-005_VERIFY {'PASS' if not failed else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
