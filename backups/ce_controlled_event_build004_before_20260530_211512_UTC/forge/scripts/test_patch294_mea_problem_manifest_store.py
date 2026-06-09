#!/usr/bin/env python3
"""Patch 294 behavior tests — MEA Controlled Problem Manifest Store."""
from __future__ import annotations

import copy
import json
import stat
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

passes = 0
fails = 0


def check(name: str, cond: bool, detail: object = "") -> None:
    global passes, fails
    if cond:
        passes += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✓ [PASS] {name}{suffix}")
    else:
        fails += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✗ [FAIL] {name}{suffix}")


print("PATCH 294 BEHAVIOR TESTS — MEA Controlled Problem Manifest Store")
print(f"Forge root: {ROOT}")

from rmc_engine_v1.mea import (  # noqa: E402
    PROBLEM_MANIFEST_GET_ROUTE,
    PROBLEM_MANIFEST_POST_ROUTE,
    PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN,
    PROBLEM_MANIFEST_STORE_FORMULA,
    PROBLEM_MANIFEST_STORE_PATCH_ID,
    PROBLEM_MANIFEST_STORE_SCHEMA_VERSION,
    build_144hz_test_manifest,
    canonical_hash,
    evaluate_problem_manifest_store_request,
    kernel_identity,
    output_permission_interpretation,
    problem_manifest_store_boundary,
    problem_manifest_store_status,
    to_dict,
)

check("patch_id_locked", PROBLEM_MANIFEST_STORE_PATCH_ID == "Patch 294 — MEA Controlled Problem Manifest Store", PROBLEM_MANIFEST_STORE_PATCH_ID)
check("schema_locked", PROBLEM_MANIFEST_STORE_SCHEMA_VERSION == "mea_problem_manifest_store_v1_patch294", PROBLEM_MANIFEST_STORE_SCHEMA_VERSION)
check("get_route_locked", PROBLEM_MANIFEST_GET_ROUTE == "/api/mea/problem-manifest")
check("post_route_locked", PROBLEM_MANIFEST_POST_ROUTE == "/api/mea/problem-manifest")
check("approval_token_locked", PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN == "APPROVE_MEA_PROBLEM_MANIFEST_STORE")
check("formula_initial_seed", "Store(M_0)" in PROBLEM_MANIFEST_STORE_FORMULA)
check("formula_no_advance", "advances_live_manifest=false" in PROBLEM_MANIFEST_STORE_FORMULA)
check("formula_no_memory", "writes_memory=false" in PROBLEM_MANIFEST_STORE_FORMULA)

boundary = problem_manifest_store_boundary()
for key in ["writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal", "promotes_to_memory", "renders_user_output", "mutates_operator_console_ui"]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
for key in ["writes_files", "writes_mea_runtime_state", "writes_atomic_state_record", "writes_audit_receipt", "writes_rollback_plan", "uses_file_lock", "seeds_live_manifests", "allows_initial_seed_only", "rejects_overwrite", "idempotent_same_manifest_no_write"]:
    check(f"boundary_{key}_true", boundary.get(key) is True, boundary.get(key))
check("boundary_has_get_route", boundary.get("get_routes") == ["/api/mea/problem-manifest"])
check("boundary_has_post_route", boundary.get("post_routes") == ["/api/mea/problem-manifest"])
check("boundary_no_seal_route", boundary.get("seal_route_available") is False)
check("boundary_downstream_not_wired", boundary.get("downstream_candidate_generation_reads_persisted_state") is False)

sem = output_permission_interpretation("sealed")
check("sealed_semantics_renderer_gate", sem.get("interpretation") == "renderer_gate_closed_until_a_later_valid_seal_and_echo_validation_path")
check("sealed_semantics_not_candidate_seal", sem.get("means_candidate_sealed") is False)
check("sealed_semantics_not_executed", sem.get("means_seal_executed") is False)
check("sealed_semantics_not_advance", sem.get("means_live_manifest_advanced") is False)
check("sealed_semantics_not_memory", sem.get("means_memory_promoted") is False)

with tempfile.TemporaryDirectory(prefix="patch294_store_test_") as tmp:
    store_root = Path(tmp) / "state"
    current = store_root / "current_problem_manifest.json"

    initial = problem_manifest_store_status(store_root=store_root)
    check("initial_uninitialized", initial.get("status") == "UNINITIALIZED")
    check("initial_no_file", initial.get("state_file_present") is False)
    check("initial_get_does_not_create_store", not store_root.exists())
    check("initial_read_no_writes", initial.get("writes_files") is False and initial.get("writes_memory") is False)

    no_token = evaluate_problem_manifest_store_request({"operation": "seed", "use_fixture": True}, store_root=store_root, now_utc="2026-05-30T00:00:00+00:00")
    check("missing_token_rejected", no_token.get("status") == "REJECTED")
    check("missing_token_reason", no_token.get("reason_code") == "approval_token_required", no_token.get("reason_code"))
    check("missing_token_no_store", not store_root.exists())
    check("missing_token_no_write", no_token.get("write_performed") is False and no_token.get("writes_files") is False)

    no_operation = evaluate_problem_manifest_store_request({"approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN, "use_fixture": True}, store_root=store_root, now_utc="2026-05-30T00:00:00+00:00")
    check("missing_operation_rejected", no_operation.get("reason_code") == "seed_operation_required", no_operation.get("reason_code"))
    check("missing_operation_no_store", not store_root.exists())

    denied_advance = evaluate_problem_manifest_store_request({"approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN, "operation": "seed", "use_fixture": True, "selected_candidate_id": "cg_hypothesis_001"}, store_root=store_root, now_utc="2026-05-30T00:00:00+00:00")
    check("candidate_advance_rejected", denied_advance.get("reason_code") == "manifest_advance_not_allowed", denied_advance.get("reason_code"))
    check("candidate_advance_no_store", not store_root.exists())

    approved = evaluate_problem_manifest_store_request({"approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN, "operation": "seed", "use_fixture": True, "source": "canonical_144hz_test_fixture"}, store_root=store_root, now_utc="2026-05-30T00:00:00+00:00")
    check("approved_ok", approved.get("status") == "OK")
    check("approved_persisted_initial_seed", approved.get("gate_status") == "PERSISTED_INITIAL_SEED", approved.get("gate_status"))
    check("approved_write_performed", approved.get("write_performed") is True)
    check("approved_atomic_write", approved.get("atomic_write_completed") is True)
    check("approved_manifest_hash_64", isinstance(approved.get("manifest_hash"), str) and len(approved.get("manifest_hash")) == 64)
    check("approved_state_hash_64", isinstance(approved.get("state_content_hash"), str) and len(approved.get("state_content_hash")) == 64)
    check("approved_receipt_hash_64", isinstance(approved.get("write_receipt_hash"), str) and len(approved.get("write_receipt_hash")) == 64)
    check("approved_rollback_hash_64", isinstance(approved.get("rollback_plan_hash"), str) and len(approved.get("rollback_plan_hash")) == 64)
    check("approved_claim_test_required", approved.get("claim_status") == "test_required", approved.get("claim_status"))
    check("approved_proof_debt_085", approved.get("proof_debt") == 0.85, approved.get("proof_debt"))
    check("approved_output_permission_sealed", approved.get("output_permissions") == "sealed", approved.get("output_permissions"))
    check("approved_output_not_executed", approved.get("output_permission_interpretation", {}).get("means_seal_executed") is False)
    check("approved_no_candidate_commit", approved.get("commits_live_candidates") is False)
    check("approved_no_manifest_advance", approved.get("advances_live_manifest") is False)
    check("approved_no_seal", approved.get("seals_candidates") is False and approved.get("seal_route_available") is False)
    check("approved_no_memory", approved.get("writes_memory") is False and approved.get("promotes_to_memory") is False)
    check("approved_state_file_created", current.exists())
    check("approved_receipt_dir_created", (store_root / "receipts").exists())
    check("approved_rollback_dir_created", (store_root / "rollback_plans").exists())
    check("approved_lock_exists", (store_root / ".store.lock").exists())
    check("state_file_mode_0600", stat.S_IMODE(current.stat().st_mode) == 0o600, oct(stat.S_IMODE(current.stat().st_mode)))
    check("store_dir_mode_0700", stat.S_IMODE(store_root.stat().st_mode) == 0o700, oct(stat.S_IMODE(store_root.stat().st_mode)))

    readback = problem_manifest_store_status(store_root=store_root)
    check("readback_ok", readback.get("status") == "OK")
    check("readback_initialized", readback.get("initialized") is True)
    check("readback_integrity_verified", readback.get("integrity_verified") is True, readback.get("integrity_errors"))
    check("readback_artifacts_verified", readback.get("verified", {}).get("linked_artifacts_verified") is True)
    check("readback_manifest_hash_match", readback.get("manifest_hash") == approved.get("manifest_hash"))
    check("readback_claim_test_required", readback.get("claim_status") == "test_required")
    check("readback_semantics_not_seal", readback.get("output_permission_interpretation", {}).get("means_candidate_sealed") is False)
    check("readback_no_advance", readback.get("advances_live_manifest") is False)
    check("readback_no_memory", readback.get("writes_memory") is False)

    before_files = sorted(str(p.relative_to(store_root)) for p in store_root.rglob("*") if p.is_file())
    idempotent = evaluate_problem_manifest_store_request({"approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN, "operation": "seed", "use_fixture": True}, store_root=store_root, now_utc="2026-05-30T00:00:01+00:00")
    after_files = sorted(str(p.relative_to(store_root)) for p in store_root.rglob("*") if p.is_file())
    check("idempotent_ok", idempotent.get("status") == "OK")
    check("idempotent_status", idempotent.get("gate_status") == "ALREADY_PRESENT_IDEMPOTENT_NO_WRITE", idempotent.get("gate_status"))
    check("idempotent_write_false", idempotent.get("write_performed") is False)
    check("idempotent_files_unchanged", before_files == after_files, after_files)
    check("idempotent_hash_same", idempotent.get("manifest_hash") == approved.get("manifest_hash"))

    custom = to_dict(build_144hz_test_manifest())
    custom["problem_id"] = "different_problem_state"
    custom["goal"] = "Different valid seed that must not overwrite live state."
    conflict = evaluate_problem_manifest_store_request({"approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN, "operation": "seed", "manifest": custom}, store_root=store_root, now_utc="2026-05-30T00:00:02+00:00")
    check("conflict_rejected", conflict.get("status") == "REJECTED")
    check("conflict_reason", conflict.get("reason_code") == "existing_manifest_conflict_no_overwrite", conflict.get("reason_code"))
    check("conflict_no_write", conflict.get("write_performed") is False)
    still_same = problem_manifest_store_status(store_root=store_root)
    check("conflict_preserves_original", still_same.get("manifest_hash") == approved.get("manifest_hash"))

    tampered = json.loads(current.read_text())
    tampered["manifest"]["claim_status"] = "verified_claim"
    current.write_text(json.dumps(tampered, sort_keys=True), encoding="utf-8")
    corrupted = problem_manifest_store_status(store_root=store_root)
    check("tamper_detected", corrupted.get("status") == "STATE_INTEGRITY_FAILED", corrupted.get("status"))
    check("tamper_integrity_false", corrupted.get("integrity_verified") is False)
    blocked_on_corrupt = evaluate_problem_manifest_store_request({"approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN, "operation": "seed", "use_fixture": True}, store_root=store_root, now_utc="2026-05-30T00:00:03+00:00")
    check("corrupt_state_blocks_write", blocked_on_corrupt.get("reason_code") == "existing_state_integrity_failed", blocked_on_corrupt.get("reason_code"))

with tempfile.TemporaryDirectory(prefix="patch294_symlink_test_") as tmp:
    root = Path(tmp) / "state"
    root.mkdir(parents=True)
    external = Path(tmp) / "outside.json"
    external.write_text("{}", encoding="utf-8")
    (root / "current_problem_manifest.json").symlink_to(external)
    symlink_status = problem_manifest_store_status(store_root=root)
    check("symlink_state_refused", symlink_status.get("status") == "STATE_INTEGRITY_FAILED", symlink_status.get("status"))
    check("symlink_state_integrity_false", symlink_status.get("integrity_verified") is False)

with tempfile.TemporaryDirectory(prefix="patch294_custom_test_") as tmp:
    store_root = Path(tmp) / "state"
    custom = to_dict(build_144hz_test_manifest())
    custom["problem_id"] = "valid_custom_seed"
    custom["goal"] = "Track a valid custom unresolved problem without promoting it."
    custom_result = evaluate_problem_manifest_store_request({"approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN, "operation": "seed", "manifest": custom}, store_root=store_root, now_utc="2026-05-30T00:00:00+00:00")
    check("custom_valid_seed_persists", custom_result.get("gate_status") == "PERSISTED_INITIAL_SEED", custom_result.get("gate_status"))
    check("custom_still_not_advanced", custom_result.get("advances_live_manifest") is False)

kernel = kernel_identity()
check("kernel_stage_patch294", kernel.get("kernel_stage") == "problem_manifest_store_patch294", kernel.get("kernel_stage"))
check("kernel_store_visible", kernel.get("problem_manifest_store_visible") is True)
check("kernel_persistence_initial_only", kernel.get("manifest_persistence_scope") == "controlled_initial_seed_only_no_candidate_advance")
check("kernel_writes_files_declared", kernel.get("boundary", {}).get("writes_files") is True)
check("kernel_seeds_live_declared", kernel.get("boundary", {}).get("seeds_live_manifests") is True)
check("kernel_no_live_candidate_advance", kernel.get("candidate_driven_manifest_advance_active") is False)
check("kernel_no_seal_route", kernel.get("seal_route_available") is False)

print(f"RESULT: PATCH_294_BEHAVIOR {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
