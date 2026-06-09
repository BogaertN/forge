#!/usr/bin/env python3
"""Patch 299 behavior tests — MEA Manifest Memory Writer Dry-Run."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORGE_ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    MANIFEST_MEMORY_WRITER_APPROVAL_TOKEN,
    MANIFEST_MEMORY_WRITER_DRY_RUN_ROUTE,
    MANIFEST_MEMORY_WRITER_PATCH_ID,
    MANIFEST_MEMORY_WRITER_SCHEMA_VERSION,
    MANIFEST_MEMORY_WRITER_STATUS_ROUTE,
    evaluate_manifest_memory_writer_dry_run_request,
    manifest_memory_writer_boundary,
    manifest_memory_writer_status,
)

EXPECTED_MANIFEST_HASH = "852feb2c1491683bca39d89ee3d86e43e4f8fe9aecad2c403c9be70018c95a83"
EXPECTED_STATE_CONTENT_HASH = "a10f4d719dd1d7041f0b16f2c474c5a7bcbee972ed9411b7eaa48e3219c9dc0d"
EXPECTED_TRANSACTION_INTENT_HASH = "9ff10b208c0adc06dedff97a59415962f9786c20bc8d7bd18c877fd58a876691"
EXPECTED_CANDIDATE_HASH = "a27ce2e352839119f79f0742d63cdcd964c49321e3206ce24b89f333c8b90901"
EXPECTED_MEMORY_RECORD_HASH = "4cc7f39eb2c2110c282ab1ef43183826c7ea6d27b7f68b78164d708cfaa92115"

passed = 0
failed = 0


def check(name: str, condition: bool, detail: object | None = None) -> None:
    global passed, failed
    if condition:
        passed += 1
        suffix = f" — {detail}" if detail is not None else ""
        print(f"  ✓ [PASS] {name}{suffix}")
    else:
        failed += 1
        suffix = f" — observed={detail!r}" if detail is not None else ""
        print(f"  ✗ [FAIL] {name}{suffix}")


def hash_tree(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        hashes[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def make_request(status: dict[str, object]) -> dict[str, object]:
    return {
        "approval_token": MANIFEST_MEMORY_WRITER_APPROVAL_TOKEN,
        "transaction_id": status["transaction_id"],
        "transaction_intent_hash": status["transaction_intent_hash"],
        "candidate_id": status["candidate_id"],
        "candidate_hash": EXPECTED_CANDIDATE_HASH,
        "committed_manifest_hash": status["committed_manifest_hash"],
        "committed_state_content_hash": status["committed_state_content_hash"],
    }


def main() -> int:
    print("PATCH 299 BEHAVIOR TESTS — MEA Manifest Memory Writer Dry-Run")
    print(f"Forge root: {FORGE_ROOT}")
    boundary = manifest_memory_writer_boundary()
    check("patch_id_locked", MANIFEST_MEMORY_WRITER_PATCH_ID == "Patch 299 — MEA Manifest Memory Writer Dry-Run", MANIFEST_MEMORY_WRITER_PATCH_ID)
    check("schema_locked", MANIFEST_MEMORY_WRITER_SCHEMA_VERSION == "mea_manifest_memory_writer_dry_run_v1_patch299", MANIFEST_MEMORY_WRITER_SCHEMA_VERSION)
    check("status_route_locked", MANIFEST_MEMORY_WRITER_STATUS_ROUTE == "/api/mea/memory-writer/status")
    check("dry_run_route_locked", MANIFEST_MEMORY_WRITER_DRY_RUN_ROUTE == "/api/mea/memory-writer-dry-run")
    for key in (
        "writes_files", "writes_mea_runtime_state", "writes_memory", "writes_rmc_memory",
        "writes_jsonl_ledger", "writes_chroma", "writes_identity_vault", "calls_llm",
        "executes_shell", "performs_network_io", "commits_live_candidates",
        "advances_live_manifest", "seals_candidates", "executes_seal",
        "promotes_to_memory", "renders_user_output", "creates_memory_capsule",
        "mints_contribution_tokens", "canonical_seal_route_available", "seal_route_available",
    ):
        check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
    check("boundary_requires_replay", boundary.get("requires_live_trace_replay_verification") is True)
    check("boundary_rmc_writer_not_invoked", boundary.get("existing_rmc_memory_writer_invoked") is False)

    live_store = FORGE_ROOT / "runtime_state" / "mea_problem_manifest_store_v1"
    check("committed_source_store_available", (live_store / "current_problem_manifest.json").is_file(), live_store)
    if not (live_store / "current_problem_manifest.json").is_file():
        print(f"RESULT: PATCH_299_BEHAVIOR FAIL  Total:{passed+failed} Passed:{passed} Failed:{failed}")
        return 1

    with tempfile.TemporaryDirectory(prefix="patch299_mea_memory_preview_") as td:
        temp_store = Path(td) / "mea_problem_manifest_store_v1"
        shutil.copytree(live_store, temp_store)
        before = hash_tree(temp_store)

        status = manifest_memory_writer_status(store_root=temp_store)
        check("status_ok", status.get("status") == "OK", status.get("status"))
        check("status_dry_run_available", status.get("gate_status") == "DRY_RUN_AVAILABLE", status.get("gate_status"))
        check("status_source_integrity", status.get("source_state_integrity_verified") is True)
        check("status_manifest_bound", status.get("committed_manifest_hash") == EXPECTED_MANIFEST_HASH, status.get("committed_manifest_hash"))
        check("status_state_bound", status.get("committed_state_content_hash") == EXPECTED_STATE_CONTENT_HASH, status.get("committed_state_content_hash"))
        check("status_claim_hypothesis", status.get("claim_status") == "hypothesis", status.get("claim_status"))
        check("status_proof_debt_high_preserved", status.get("proof_debt") == 0.85, status.get("proof_debt"))
        check("status_no_rejected_draft_fabrication", status.get("rejected_draft_records_previewed") is False)

        rejection = evaluate_manifest_memory_writer_dry_run_request({}, store_root=temp_store)
        check("missing_token_rejected", rejection.get("reason_code") == "approval_token_required", rejection.get("reason_code"))
        check("rejection_no_write", rejection.get("writes_files") is False and rejection.get("writes_memory") is False)

        request = make_request(status)
        response = evaluate_manifest_memory_writer_dry_run_request(request, store_root=temp_store)
        preview = response.get("memory_record_preview") or {}
        check("dry_run_ready", response.get("gate_status") == "MEMORY_RECORD_DRY_RUN_READY_NO_WRITE", response.get("gate_status"))
        check("dry_run_replay_verified", response.get("replay_verified") is True and response.get("all_replay_checks_passed") is True)
        check("dry_run_candidate_hypothesis", response.get("candidate_id") == "cg_hypothesis_001" and response.get("claim_status") == "hypothesis")
        check("dry_run_proof_debt_preserved", response.get("proof_debt") == 0.85, response.get("proof_debt"))
        check("dry_run_memory_tier_bounded", response.get("memory_tier") == "hypothesis_test_required_record", response.get("memory_tier"))
        check("dry_run_not_verified_fact", response.get("verified_fact") is False and preview.get("claim_semantics", {}).get("verified_fact") is False)
        check("dry_run_manifest_hash_bound", response.get("committed_manifest_hash") == EXPECTED_MANIFEST_HASH)
        check("dry_run_transaction_hash_bound", response.get("transaction_intent_hash") == EXPECTED_TRANSACTION_INTENT_HASH)
        check("dry_run_candidate_hash_bound", response.get("candidate_hash") == EXPECTED_CANDIDATE_HASH)
        check("dry_run_record_hash_stable", response.get("memory_record_hash_stability_proven") is True)
        check("dry_run_record_hash_expected", response.get("memory_record_hash") == EXPECTED_MEMORY_RECORD_HASH, response.get("memory_record_hash"))
        check("dry_run_renderer_gated", preview.get("renderer_permission_boundary", {}).get("renderer_output_permitted") is False)
        check("dry_run_no_rejected_draft_fabrication", preview.get("rejected_draft_record_previews") == [])
        check("dry_run_rmc_writer_deferred", preview.get("existing_rmc_writer_compatibility", {}).get("status") == "adapter_boundary_defined_not_invoked")
        check("dry_run_no_actions", response.get("writes_files") is False and response.get("writes_memory") is False and response.get("promotes_to_memory") is False)

        repeat = evaluate_manifest_memory_writer_dry_run_request(request, store_root=temp_store)
        check("repeat_preview_hash_identical", repeat.get("memory_record_hash") == response.get("memory_record_hash"))
        check("repeat_preview_id_identical", repeat.get("memory_record_id") == response.get("memory_record_id"))

        wrong = dict(request)
        wrong["committed_manifest_hash"] = "0" * 64
        wrong_response = evaluate_manifest_memory_writer_dry_run_request(wrong, store_root=temp_store)
        check("wrong_target_rejected", wrong_response.get("reason_code") == "live_trace_replay_required", wrong_response.get("reason_code"))
        check("wrong_target_no_write", wrong_response.get("writes_files") is False and wrong_response.get("writes_memory") is False)

        after = hash_tree(temp_store)
        check("temp_state_immutability", before == after)

    core_writer = FORGE_ROOT / "rmc_engine_v1" / "memory_writer.py"
    check("existing_rmc_memory_writer_present", core_writer.is_file(), core_writer)
    if core_writer.is_file():
        core_text = core_writer.read_text(encoding="utf-8")
        check("existing_rmc_writer_dry_run_contract_present", "def plan_memory_write" in core_text)
        check("existing_rmc_writer_requires_echo_stage", "echo_validation_before_memory_write" in core_text)

    print(f"RESULT: PATCH_299_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{passed+failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
