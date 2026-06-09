#!/usr/bin/env python3
"""Patch 296R behavior tests — source-bound persisted-state transaction preflight hotfix."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN,
    TRANSACTION_PREFLIGHT_APPROVAL_TOKEN,
    TRANSACTION_PREFLIGHT_PATCH_ID,
    TRANSACTION_PREFLIGHT_POST_ROUTE,
    TRANSACTION_PREFLIGHT_SCHEMA_VERSION,
    build_live_candidates_payload,
    build_seal_transaction_preflight_preview,
    evaluate_problem_manifest_store_request,
    evaluate_seal_transaction_preflight_request,
    kernel_identity,
    transaction_preflight_boundary,
)

PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: object = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✓ [PASS] {name}{suffix}")
    else:
        FAIL += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✗ [FAIL] {name}{suffix}")


def file_hashes(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*")) if path.is_file()
    }


def request_for(live: dict, candidate_id: str = "cg_hypothesis_001") -> dict:
    row = next(row for row in live["candidates"] if row["candidate_id"] == candidate_id)
    return {
        "approval_token": TRANSACTION_PREFLIGHT_APPROVAL_TOKEN,
        "source_manifest_hash": live["source_manifest_hash"],
        "source_state_content_hash": live["source_state_content_hash"],
        "candidate_id": candidate_id,
        "candidate_hash": row["candidate_hash"],
        "candidate_set_hash": live["candidate_set_hash"],
        "gate_report_hash": row["gate_report_hash"],
    }


def check_source_bound_payload(prefix: str, payload: dict, manifest_hash: str, state_hash: str) -> None:
    trace = payload["proposed_new_manifest"]["operator_history"][-1]
    check(f"{prefix}_accepted", payload.get("status") == "OK" and payload.get("gate_status") == "ACCEPTED_PREFLIGHT_ONLY")
    check(f"{prefix}_repair_declared", payload.get("transaction_trace_source_binding_repaired") is True)
    check(f"{prefix}_source_binding_verified", payload.get("transaction_trace_source_binding_verified") is True)
    check(f"{prefix}_trace_input_manifest_hash_bound", trace.get("input_manifest_hash") == manifest_hash, trace.get("input_manifest_hash"))
    check(f"{prefix}_trace_state_content_hash_bound", trace.get("parameters", {}).get("source_state_content_hash") == state_hash, trace.get("parameters", {}).get("source_state_content_hash"))
    check(f"{prefix}_trace_input_not_null", trace.get("input_manifest_hash") not in (None, "None", "null"))
    check(f"{prefix}_trace_state_not_null", trace.get("parameters", {}).get("source_state_content_hash") is not None)
    check(f"{prefix}_explicit_not_rank", payload.get("candidate_id") == "cg_hypothesis_001" and payload.get("highest_ranked_candidate_id") == "cg_branch_001")
    check(f"{prefix}_claim_remains_hypothesis", payload.get("claim_status") == "hypothesis")
    check(f"{prefix}_no_mutation", payload.get("writes_files") is False and payload.get("advances_live_manifest") is False and payload.get("executes_seal") is False and payload.get("writes_memory") is False)
    check(f"{prefix}_hash_stable", payload.get("transaction_hash_stability_proven") is True)


print("PATCH 296R BEHAVIOR TESTS — MEA Transaction Trace Source-Binding Hotfix")
print(f"Forge root: {ROOT}")
check("patch_id_locked", TRANSACTION_PREFLIGHT_PATCH_ID == "Patch 296R — MEA Transaction Trace Source-Binding Hotfix", TRANSACTION_PREFLIGHT_PATCH_ID)
check("schema_locked", TRANSACTION_PREFLIGHT_SCHEMA_VERSION == "mea_seal_transaction_preflight_v1_patch296r", TRANSACTION_PREFLIGHT_SCHEMA_VERSION)
check("route_preserved", TRANSACTION_PREFLIGHT_POST_ROUTE == "/api/mea/seal-transaction-preflight")

boundary = transaction_preflight_boundary()
for key in ["non_mutating", "requires_approval_token", "requires_explicit_candidate_selection", "requires_persisted_state_integrity", "uses_live_candidate_api_chain"]:
    check(f"boundary_{key}_true", boundary.get(key) is True, boundary.get(key))
for key in ["writes_files", "writes_mea_runtime_state", "writes_memory", "advances_live_manifest", "seals_candidates", "executes_seal", "promotes_to_memory", "seal_route_available"]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))

with tempfile.TemporaryDirectory(prefix="patch296r_state_") as tmp:
    store = Path(tmp) / "mea_problem_manifest_store_v1"
    seed = evaluate_problem_manifest_store_request(
        {"approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN, "operation": "seed", "use_fixture": True},
        store_root=store,
        now_utc="2026-05-30T00:00:00+00:00",
    )
    check("temp_seed_available", seed.get("gate_status") == "PERSISTED_INITIAL_SEED")
    live = build_live_candidates_payload(store_root=store)
    check("temp_candidates_from_state", live.get("source_state_integrity_verified") is True)
    before = file_hashes(store)
    approved = evaluate_seal_transaction_preflight_request(request_for(live), store_root=store)
    repeated = evaluate_seal_transaction_preflight_request(request_for(live), store_root=store)
    after = file_hashes(store)
    check_source_bound_payload("temp", approved, live["source_manifest_hash"], live["source_state_content_hash"])
    check("temp_repeat_intent_hash", approved.get("transaction_intent_hash") == repeated.get("transaction_intent_hash"))
    check("temp_repeat_manifest_hash", approved.get("proposed_new_manifest_hash") == repeated.get("proposed_new_manifest_hash"))
    check("temp_state_unchanged", before == after, sorted(after))

# Test directly against live persisted state when present.  This is read-only.
live_store = ROOT / "runtime_state" / "mea_problem_manifest_store_v1"
if (live_store / "current_problem_manifest.json").exists():
    live_before = file_hashes(live_store)
    live_candidates = build_live_candidates_payload(store_root=live_store)
    live_payload = evaluate_seal_transaction_preflight_request(request_for(live_candidates), store_root=live_store)
    live_after = file_hashes(live_store)
    check_source_bound_payload("live", live_payload, live_candidates["source_manifest_hash"], live_candidates["source_state_content_hash"])
    check("live_persisted_state_unchanged", live_before == live_after, sorted(live_after))
    check("live_repaired_proposed_hash_64", isinstance(live_payload.get("proposed_new_manifest_hash"), str) and len(live_payload["proposed_new_manifest_hash"]) == 64)
else:
    print("  - [SKIP] live persisted state not included in this test environment")

kernel = kernel_identity()
check("kernel_hotfix_stage", kernel.get("kernel_stage") == "persisted_state_transaction_preflight_source_binding_hotfix_patch296r", kernel.get("kernel_stage"))
check("kernel_no_real_seal", kernel.get("seal_route_available") is False)

print(f"RESULT: PATCH_296R_BEHAVIOR {'PASS' if FAIL == 0 else 'FAIL'}  Total:{PASS+FAIL} Passed:{PASS} Failed:{FAIL}")
sys.exit(0 if FAIL == 0 else 1)
