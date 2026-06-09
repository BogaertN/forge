#!/usr/bin/env python3
"""Patch 291 behavior tests — MEA Seal Engine Dry-Run."""
from __future__ import annotations

import sys
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


print("PATCH 291 BEHAVIOR TESTS — MEA Seal Engine Dry-Run")
print(f"Forge root: {ROOT}")

from rmc_engine_v1.mea import (  # noqa: E402
    SEAL_ENGINE_PATCH_ID,
    SEAL_ENGINE_SCHEMA_VERSION,
    SEAL_ENGINE_STATUS_ROUTE,
    SEAL_ENGINE_DRY_RUN_ROUTE,
    SEAL_ENGINE_FORMULA,
    SEAL_ENGINE_ALGORITHM_REFERENCE,
    build_seal_engine_dry_run,
    seal_engine_status,
    seal_engine_boundary,
    kernel_identity,
)

check("patch_id_locked", SEAL_ENGINE_PATCH_ID == "Patch 291 — MEA Seal Engine Dry-Run", SEAL_ENGINE_PATCH_ID)
check("schema_locked", SEAL_ENGINE_SCHEMA_VERSION == "mea_seal_engine_dry_run_v1_patch291", SEAL_ENGINE_SCHEMA_VERSION)
check("status_route_locked", SEAL_ENGINE_STATUS_ROUTE == "/api/mea/seal-engine/status")
check("dry_run_route_locked", SEAL_ENGINE_DRY_RUN_ROUTE == "/api/mea/seal-engine-dry-run")
check("algorithm_reference_present", "Algorithm 4" in SEAL_ENGINE_ALGORITHM_REFERENCE)
check("formula_mentions_execution_false", "execution=false" in SEAL_ENGINE_FORMULA)

boundary = seal_engine_boundary()
for key in [
    "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault",
    "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests",
    "commits_live_candidates", "advances_live_manifest", "seals_candidates",
    "executes_seal", "promotes_to_memory", "renders_user_output", "mutates_operator_console_ui",
]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_dry_run_only", boundary.get("dry_run_only") is True)
check("boundary_no_post_routes", boundary.get("creates_post_routes") is False and boundary.get("post_routes") == [])
check("boundary_seal_route_unavailable", boundary.get("seal_route_available") is False)

status = seal_engine_status()
dry_run = build_seal_engine_dry_run()
objects = dry_run.get("seal_objects", [])
blocked = dry_run.get("blocked_candidates", [])
by_id = {obj.get("candidate_id"): obj for obj in objects}

check("status_ok", status.get("status") == "OK")
check("status_visible", status.get("seal_engine_visible") is True)
check("status_no_execution", status.get("seal_execution_permitted") is False)
check("status_no_seal_route", status.get("seal_route_available") is False)
check("status_no_memory", status.get("memory_write_active") is False and status.get("memory_promotion_active") is False)
check("dry_run_ok", dry_run.get("status") == "OK")
check("dry_run_type", dry_run.get("preview_type") == "mea_seal_engine_dry_run_no_execution")
check("dry_run_object_count_2", dry_run.get("seal_object_count") == 2, dry_run.get("seal_object_count"))
check("blocked_count_2", dry_run.get("blocked_candidate_count") == 2, dry_run.get("blocked_candidate_count"))
check("candidate_count_4", dry_run.get("candidate_count") == 4, dry_run.get("candidate_count"))
check("best_candidate_hypothesis", dry_run.get("best_dry_run_candidate_id") == "cg_hypothesis_001", dry_run.get("best_dry_run_candidate_id"))
check("best_claim_hypothesis", dry_run.get("best_dry_run_claim_status") == "hypothesis", dry_run.get("best_dry_run_claim_status"))
check("hash_stability", dry_run.get("seal_object_hash_stability_proven") is True)
check("dry_run_no_execution", dry_run.get("seal_execution_permitted") is False and dry_run.get("executed") is False)
check("dry_run_no_seal", dry_run.get("seals_candidates") is False and dry_run.get("candidate_sealing_active") is False)
check("dry_run_no_state_advance", dry_run.get("advances_live_manifest") is False and dry_run.get("live_manifest_advance_active") is False)
check("dry_run_no_memory", dry_run.get("writes_memory") is False and dry_run.get("memory_write_active") is False and dry_run.get("memory_promotion_active") is False)
check("normalized_packet_source", "normalizer" in str(dry_run.get("normalized_packet_source")))

expected = {
    "cg_hypothesis_001": "hypothesis",
    "cg_branch_001": "speculative_branch",
}
for cid, claim_status in expected.items():
    obj = by_id.get(cid, {})
    check(f"seal_object_exists:{cid}", bool(obj))
    check(f"seal_status_dry_run:{cid}", obj.get("seal_status") == "DRY_RUN_ONLY_NOT_EXECUTED", obj.get("seal_status"))
    check(f"claim_preserved:{cid}", obj.get("claim_status") == claim_status, obj.get("claim_status"))
    check(f"hash_64:{cid}", isinstance(obj.get("seal_object_hash"), str) and len(obj.get("seal_object_hash")) == 64)
    check(f"candidate_hash_64:{cid}", isinstance(obj.get("candidate_hash"), str) and len(obj.get("candidate_hash")) == 64)
    check(f"gate_report_hash_64:{cid}", isinstance(obj.get("gate_report_hash"), str) and len(obj.get("gate_report_hash")) == 64)
    check(f"packet_hash_64:{cid}", isinstance(obj.get("normalized_packet_hash"), str) and len(obj.get("normalized_packet_hash")) == 64)
    check(f"packet_embedded:{cid}", isinstance(obj.get("normalized_packet"), dict) and obj.get("normalized_packet", {}).get("packet_hash") == obj.get("normalized_packet_hash"))
    check(f"gate_results_present:{cid}", isinstance(obj.get("gate_results"), dict) and obj.get("gate_results", {}).get("candidate_id") == cid)
    check(f"proof_debt_preserved:{cid}", obj.get("proof_debt") == 0.85, obj.get("proof_debt"))
    check(f"remaining_unknowns_present:{cid}", obj.get("remaining_unknown_count", 0) >= 2, obj.get("remaining_unknown_count"))
    check(f"output_permissions_present:{cid}", len(obj.get("output_permissions", [])) >= 2)
    check(f"allowed_transitions_present:{cid}", len(obj.get("allowed_next_transitions", [])) >= 2)
    check(f"algorithm_reference:{cid}", "Algorithm 4" in obj.get("rmc_algorithm_reference", ""))
    check(f"execution_false:{cid}", obj.get("seal_execution_permitted") is False and obj.get("executed") is False)
    check(f"sealed_false:{cid}", obj.get("sealed_candidate") is False)
    check(f"commit_false:{cid}", obj.get("live_candidate_commit_permitted") is False)
    check(f"advance_false:{cid}", obj.get("live_manifest_advance_permitted") is False)
    check(f"memory_write_false:{cid}", obj.get("memory_write_permitted") is False)
    check(f"memory_promotion_false:{cid}", obj.get("memory_promotion_permitted") is False)
    check(f"seal_route_unavailable:{cid}", obj.get("seal_route_available") is False)

blocked_ids = {b.get("candidate_id") for b in blocked}
check("recall_blocked", "cg_recall_001" in blocked_ids)
check("tamper_blocked", "cg_tamper_001" in blocked_ids)
for b in blocked:
    cid = b.get("candidate_id")
    check(f"blocked_no_execution:{cid}", b.get("seal_execution_permitted") is False)
    check(f"blocked_no_memory:{cid}", b.get("memory_write_permitted") is False)

repeat = build_seal_engine_dry_run()
check("collection_hash_repeat", repeat.get("dry_run_collection_hash") == dry_run.get("dry_run_collection_hash"))
for obj, obj2 in zip(objects, repeat.get("seal_objects", [])):
    check(f"object_hash_repeat:{obj.get('candidate_id')}", obj.get("seal_object_hash") == obj2.get("seal_object_hash"))

kernel = kernel_identity()
check("kernel_stage_patch291", kernel.get("kernel_stage") == "seal_engine_dry_run_patch291", kernel.get("kernel_stage"))
check("kernel_seal_engine_visible", kernel.get("seal_engine_visible") is True)
check("kernel_no_real_seal", kernel.get("seal_route_available") is False)

print(f"RESULT: PATCH_291_BEHAVIOR {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
