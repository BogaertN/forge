#!/usr/bin/env python3
"""Behavior tests for MEA-RMC-MEMORY-WRITER-BUILD-005.

Every mutation in this test suite occurs under a temporary memory directory.
The copied MEA source-state directory is hashed before and after the tests to
prove the writer never mutates the sealed manifest chain.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

EXPECTED_MANIFEST_HASH = "852feb2c1491683bca39d89ee3d86e43e4f8fe9aecad2c403c9be70018c95a83"
EXPECTED_RECEIPT_HASH = "1066fac6e124cb1300a50f39aaaf42c987f310184902dee303615d897e843e52"
EXPECTED_PREVIEW_HASH = "4cc7f39eb2c2110c282ab1ef43183826c7ea6d27b7f68b78164d708cfaa92115"


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix not in {".pyc", ".pyo"})
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", required=True, type=Path)
    args = parser.parse_args()
    forge_root = args.forge_root.expanduser().resolve()
    sys.path.insert(0, str(forge_root))
    from rmc_engine_v1.mea import (  # noqa: WPS433
        CONTROLLED_MEMORY_WRITER_APPROVAL_TOKEN,
        controlled_memory_writer_boundary,
        controlled_memory_writer_status,
        evaluate_controlled_manifest_memory_write_request,
    )

    passed = 0
    failed = 0

    def check(name: str, ok: bool, detail: object = None) -> None:
        nonlocal passed, failed
        if ok:
            passed += 1
            print(f"  [PASS] {name}" + (f" - {detail}" if detail is not None else ""))
        else:
            failed += 1
            print(f"  [FAIL] {name}" + (f" - observed={detail!r}" if detail is not None else ""))

    print("MEA-RMC-MEMORY-WRITER-BUILD-005 BEHAVIOR TESTS - TEMPORARY MEMORY WRITES ONLY")
    boundary = controlled_memory_writer_boundary()
    check("build_id_locked", boundary.get("build_id") == "MEA-RMC-MEMORY-WRITER-BUILD-005")
    check("requires_three_proof_bindings", boundary.get("required_bindings") == ["sealed_manifest_hash", "seal_receipt_hash", "memory_writer_preview_hash"])
    check("jsonl_write_enabled_only_here", boundary.get("writes_jsonl_ledger") is True)
    for key in (
        "writes_mea_runtime_state", "writes_rmc_output_memory", "invokes_rmc_renderer", "invokes_echo_validator",
        "writes_chroma", "writes_identity_vault", "writes_contribution_economy", "creates_memory_capsule",
        "mints_contribution_tokens", "writes_influence_ledger", "writes_investment_ledger", "calls_llm",
        "executes_shell", "performs_network_io", "renders_user_output",
    ):
        check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))

    live_store = forge_root / "runtime_state" / "mea_problem_manifest_store_v1"
    check("sealed_source_store_available", (live_store / "current_problem_manifest.json").is_file())
    with tempfile.TemporaryDirectory(prefix="build005_mea_memory_test_") as temp:
        temp_path = Path(temp)
        store = temp_path / "runtime_state" / "mea_problem_manifest_store_v1"
        memory = temp_path / "memory" / "mea_manifest_memory_v1"
        shutil.copytree(live_store, store)
        source_before = tree_hashes(store)
        request = {
            "approval_token": CONTROLLED_MEMORY_WRITER_APPROVAL_TOKEN,
            "sealed_manifest_hash": EXPECTED_MANIFEST_HASH,
            "seal_receipt_hash": EXPECTED_RECEIPT_HASH,
            "memory_writer_preview_hash": EXPECTED_PREVIEW_HASH,
        }
        rejected_memory = temp_path / "rejected_memory" / "mea_manifest_memory_v1"
        wrong_token = evaluate_controlled_manifest_memory_write_request({**request, "approval_token": "WRONG"}, store_root=store, memory_root=rejected_memory, now_utc="2026-05-30T22:00:00+00:00")
        check("wrong_token_rejected", wrong_token.get("reason_code") == "approval_token_required")
        check("wrong_token_no_store_created", not rejected_memory.exists())
        wrong_hash = evaluate_controlled_manifest_memory_write_request({**request, "memory_writer_preview_hash": "0" * 64}, store_root=store, memory_root=rejected_memory, now_utc="2026-05-30T22:00:00+00:00")
        check("wrong_preview_hash_rejected", wrong_hash.get("reason_code") == "memory_writer_preview_hash_mismatch")
        check("wrong_hash_no_store_created", not rejected_memory.exists())

        written = evaluate_controlled_manifest_memory_write_request(request, store_root=store, memory_root=memory, now_utc="2026-05-30T22:00:00+00:00")
        check("controlled_write_committed", written.get("gate_status") == "COMMITTED_APPEND_ONLY_JSONL_MEA_MEMORY_RECORD", written.get("gate_status"))
        ledger = memory / "hypothesis_test_required_records.jsonl"
        check("jsonl_ledger_created", ledger.is_file())
        status = controlled_memory_writer_status(memory_root=memory)
        check("ledger_status_valid", status.get("ledger_verification", {}).get("valid") is True)
        check("ledger_exactly_one_record", status.get("record_count") == 1, status.get("record_count"))
        entry = json.loads(ledger.read_text(encoding="utf-8").strip())
        record = entry["memory_record"]
        check("record_claim_hypothesis", record.get("claim_status") == "hypothesis")
        check("record_proof_debt_preserved", record.get("proof_debt") == 0.85)
        check("record_tier_bounded", record.get("memory_tier") == "hypothesis_test_required_record")
        check("record_preview_hash_bound", record.get("patch299_preview_binding", {}).get("memory_writer_preview_hash") == EXPECTED_PREVIEW_HASH)
        check("record_receipt_hash_bound", record.get("source_binding", {}).get("seal_receipt_hash") == EXPECTED_RECEIPT_HASH)
        check("record_seal_hash_bound", record.get("source_binding", {}).get("sealed_manifest_hash") == EXPECTED_MANIFEST_HASH)
        check("record_renderer_blocked", record.get("renderer_permission_boundary", {}).get("renderer_output_permitted") is False)
        check("record_forbidden_boundaries_blocked", all(record.get("storage_boundary", {}).get(k) is False for k in ("writes_rmc_output_memory", "writes_chroma", "writes_identity_vault", "writes_contribution_economy", "mints_contribution_tokens")))
        receipts = sorted((memory / "receipts").glob("*_memory_write_receipt.json"))
        check("exactly_one_write_receipt_created", len(receipts) == 1)
        receipt = json.loads(receipts[0].read_text(encoding="utf-8")) if len(receipts) == 1 else {}
        check("receipt_bound_to_entry", receipt.get("entry_hash") == entry.get("entry_hash"))
        memory_before_repeat = tree_hashes(memory)
        repeated = evaluate_controlled_manifest_memory_write_request(request, store_root=store, memory_root=memory, now_utc="2026-05-30T23:00:00+00:00")
        memory_after_repeat = tree_hashes(memory)
        check("repeat_is_idempotent_no_write", repeated.get("gate_status") == "CONTROLLED_MEA_MEMORY_RECORD_ALREADY_PERSISTED_IDEMPOTENT_NO_WRITE")
        check("repeat_does_not_change_content", memory_before_repeat == memory_after_repeat)
        check("source_state_never_mutated", source_before == tree_hashes(store))

        corrupt = temp_path / "corrupt" / "mea_manifest_memory_v1"
        shutil.copytree(memory, corrupt)
        ledger_path = corrupt / "hypothesis_test_required_records.jsonl"
        broken = json.loads(ledger_path.read_text(encoding="utf-8").strip())
        broken["memory_record"]["claim_status"] = "verified_claim"
        ledger_path.write_text(json.dumps(broken, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        rejected = evaluate_controlled_manifest_memory_write_request(request, store_root=store, memory_root=corrupt, now_utc="2026-05-30T23:00:00+00:00")
        check("tampered_ledger_rejected", rejected.get("reason_code") == "existing_ledger_integrity_failed", rejected.get("reason_code"))

    print(f"RESULT: MEA-RMC-MEMORY-WRITER-BUILD-005_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
