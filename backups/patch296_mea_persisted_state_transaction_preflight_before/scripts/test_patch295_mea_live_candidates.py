#!/usr/bin/env python3
"""Patch 295 behavior tests — MEA Controlled Live Candidate API."""
from __future__ import annotations

import hashlib
import json
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


def file_hashes(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*")) if path.is_file()
    }


print("PATCH 295 BEHAVIOR TESTS — MEA Controlled Live Candidate API")
print(f"Forge root: {ROOT}")

from rmc_engine_v1.mea import (  # noqa: E402
    LIVE_CANDIDATES_FORMULA,
    LIVE_CANDIDATES_GET_ROUTE,
    LIVE_CANDIDATES_PATCH_ID,
    LIVE_CANDIDATES_SCHEMA_VERSION,
    PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN,
    build_live_candidates_payload,
    evaluate_problem_manifest_store_request,
    kernel_identity,
    live_candidates_boundary,
)

check("patch_id_locked", LIVE_CANDIDATES_PATCH_ID == "Patch 295 — MEA Controlled Live Candidate API", LIVE_CANDIDATES_PATCH_ID)
check("schema_locked", LIVE_CANDIDATES_SCHEMA_VERSION == "mea_live_candidates_v1_patch295", LIVE_CANDIDATES_SCHEMA_VERSION)
check("get_route_locked", LIVE_CANDIDATES_GET_ROUTE == "/api/mea/candidates")
check("formula_consumes_persisted_manifest", "C_live(M_t)" in LIVE_CANDIDATES_FORMULA and "Integrity(M_t)=true" in LIVE_CANDIDATES_FORMULA)
check("formula_no_commit", "commit=false" in LIVE_CANDIDATES_FORMULA)
check("formula_no_advance", "advance=false" in LIVE_CANDIDATES_FORMULA)
check("formula_no_seal", "seal=false" in LIVE_CANDIDATES_FORMULA)
check("formula_no_memory", "memory=false" in LIVE_CANDIDATES_FORMULA)

boundary = live_candidates_boundary()
for key in ["read_only", "non_mutating", "creates_get_routes", "reads_files", "reads_mea_runtime_state", "requires_persisted_state_integrity", "generates_candidates_from_persisted_manifest", "scores_candidates", "gates_candidates", "score_can_rank"]:
    check(f"boundary_{key}_true", boundary.get(key) is True, boundary.get(key))
for key in ["creates_post_routes", "writes_files", "writes_mea_runtime_state", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests", "commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal", "promotes_to_memory", "renders_user_output", "mutates_operator_console_ui", "score_can_override_gates", "seal_route_available", "memory_promotion_route_available"]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
check("boundary_get_only", boundary.get("get_routes") == ["/api/mea/candidates"] and boundary.get("post_routes") == [])

with tempfile.TemporaryDirectory(prefix="patch295_uninitialized_") as tmp:
    empty_store = Path(tmp) / "mea_problem_manifest_store_v1"
    blocked = build_live_candidates_payload(store_root=empty_store)
    check("uninitialized_blocked", blocked.get("status") == "SOURCE_STATE_BLOCKED", blocked.get("status"))
    check("uninitialized_reason", blocked.get("reason_code") == "persisted_manifest_uninitialized", blocked.get("reason_code"))
    check("uninitialized_candidate_count_zero", blocked.get("candidate_count") == 0)
    check("uninitialized_no_generation", blocked.get("candidate_generation_executed") is False)
    check("uninitialized_read_creates_no_store", not empty_store.exists())
    check("uninitialized_no_writes", blocked.get("writes_files") is False and blocked.get("writes_memory") is False)

with tempfile.TemporaryDirectory(prefix="patch295_live_state_") as tmp:
    store_root = Path(tmp) / "mea_problem_manifest_store_v1"
    seeded = evaluate_problem_manifest_store_request(
        {
            "approval_token": PROBLEM_MANIFEST_STORE_APPROVAL_TOKEN,
            "operation": "seed",
            "use_fixture": True,
            "source": "caller_invocation_source_that_patch294_does_not_store_separately",
        },
        store_root=store_root,
        now_utc="2026-05-30T00:00:00+00:00",
    )
    check("fixture_seed_persisted", seeded.get("gate_status") == "PERSISTED_INITIAL_SEED", seeded.get("gate_status"))
    before_hashes = file_hashes(store_root)
    preview = build_live_candidates_payload(store_root=store_root)
    repeat = build_live_candidates_payload(store_root=store_root)
    after_hashes = file_hashes(store_root)
    check("preview_ok", preview.get("status") == "OK")
    check("preview_read_only", preview.get("writes_files") is False and preview.get("writes_memory") is False)
    check("preview_consumes_persisted_state", preview.get("reads_persisted_mea_state") is True and preview.get("candidate_generation_source") == "verified_persisted_problem_manifest_patch294")
    check("preview_source_integrity_verified", preview.get("source_state_integrity_verified") is True)
    check("preview_source_manifest_hash_matches_seed", preview.get("source_manifest_hash") == seeded.get("manifest_hash"))
    check("preview_source_state_hash_matches_seed", preview.get("source_state_content_hash") == seeded.get("state_content_hash"))
    check("preview_parent_binding", preview.get("source_manifest_hash_matches_generated_parent") is True)
    check("preview_candidate_count_4", preview.get("candidate_count") == 4, preview.get("candidate_count"))
    check("preview_generator_chain", preview.get("drafts_generated_by_operator_engine") is True and preview.get("verification_operators_applied") is True)
    check("preview_scoring_and_gating_chain", preview.get("coherence_extension_applied") is True and preview.get("gate_engine_applied") is True)
    check("preview_candidate_set_hash_64", isinstance(preview.get("candidate_set_hash"), str) and len(preview.get("candidate_set_hash")) == 64)
    check("preview_candidate_set_hash_stable", preview.get("candidate_set_hash_stability_proven") is True and preview.get("candidate_set_hash") == repeat.get("candidate_set_hash"))
    check("preview_candidate_hashes_stable", preview.get("candidate_hashes_stable") is True)
    candidates = {row["candidate_id"]: row for row in preview.get("candidates", [])}
    recall = candidates.get("cg_recall_001", {})
    hypothesis = candidates.get("cg_hypothesis_001", {})
    branch = candidates.get("cg_branch_001", {})
    tamper = candidates.get("cg_tamper_001", {})
    check("recall_status", recall.get("claim_status") == "recall", recall.get("claim_status"))
    check("recall_reference_only", recall.get("gate_decision") == "REFERENCE_ONLY" and recall.get("reference_only") is True)
    check("recall_not_discovery", recall.get("discovery_claim") is not True and recall.get("candidate_commit_permitted") is False)
    check("hypothesis_status", hypothesis.get("claim_status") == "hypothesis", hypothesis.get("claim_status"))
    check("hypothesis_preview_gate", hypothesis.get("gate_decision") == "PASS_PREVIEW_ONLY")
    check("hypothesis_not_verified", hypothesis.get("claim_status") != "verified_claim" and hypothesis.get("seal_execution_permitted") is False)
    check("branch_status", branch.get("claim_status") == "speculative_branch", branch.get("claim_status"))
    check("branch_bounded_preview", branch.get("gate_decision") == "PASS_BOUNDED_PREVIEW_ONLY")
    check("tamper_rejected", tamper.get("claim_status") == "rejected" and tamper.get("gate_decision") == "REJECTED")
    check("tamper_containment_not_user_visible", tamper.get("containment_preview") is True and tamper.get("user_visible") is False)
    check("highest_rank_reported_not_selected", preview.get("highest_ranked_candidate_id") == "cg_branch_001" and preview.get("highest_ranked_claim_status") == "speculative_branch", preview.get("highest_ranked_candidate_id"))
    check("ranking_does_not_select", preview.get("ranking_executed_for_preview_only") is True and preview.get("selection_executed") is False and preview.get("selected_candidate_id") is None)
    check("score_cannot_override_gates", preview.get("score_can_override_gates") is False and tamper.get("effective_rank_score") == 0.0)
    check("no_commit_advance_seal_memory", all(preview.get(key) is False for key in ["commits_live_candidates", "advances_live_manifest", "seals_candidates", "executes_seal", "promotes_to_memory", "writes_memory"]))
    provenance = preview.get("persisted_state_provenance", {})
    check("provenance_canonical_source_reported", provenance.get("canonical_manifest_source") == "canonical_144hz_test_fixture", provenance.get("canonical_manifest_source"))
    check("provenance_request_source_not_inferred", provenance.get("requested_invocation_source_persisted") is False and provenance.get("requested_invocation_source") is None)
    check("provenance_limitation_explicit", "does not infer" in str(provenance.get("provenance_limitation", "")))
    semantics = preview.get("output_permission_interpretation", {})
    check("sealed_semantics_not_candidate_seal", semantics.get("means_candidate_sealed") is False)
    check("sealed_semantics_not_advance", semantics.get("means_live_manifest_advanced") is False)
    check("route_read_does_not_mutate_store", before_hashes == after_hashes, sorted(after_hashes))

    current = store_root / "current_problem_manifest.json"
    corrupted = json.loads(current.read_text(encoding="utf-8"))
    corrupted["manifest"]["claim_status"] = "verified_claim"
    current.write_text(json.dumps(corrupted, sort_keys=True), encoding="utf-8")
    tampered_read = build_live_candidates_payload(store_root=store_root)
    check("tampered_store_blocks_candidate_read", tampered_read.get("status") == "SOURCE_STATE_BLOCKED", tampered_read.get("status"))
    check("tampered_store_reason", tampered_read.get("reason_code") == "persisted_manifest_integrity_failed", tampered_read.get("reason_code"))
    check("tampered_store_generates_nothing", tampered_read.get("candidate_generation_executed") is False and tampered_read.get("candidate_count") == 0)
    check("tampered_store_no_downstream_write", tampered_read.get("writes_files") is False and tampered_read.get("writes_memory") is False)

kernel = kernel_identity()
check("kernel_stage_patch295", kernel.get("kernel_stage") == "controlled_live_candidates_patch295", kernel.get("kernel_stage"))
check("kernel_live_candidates_visible", kernel.get("live_candidates_visible") is True)
check("kernel_reads_persisted_state", kernel.get("downstream_candidate_generation_reads_persisted_state") is True)
check("kernel_state_store_write_remains_declared", kernel.get("boundary", {}).get("writes_files") is True)
check("kernel_candidate_commit_inactive", kernel.get("candidate_driven_manifest_advance_active") is False)
check("kernel_no_seal_route", kernel.get("seal_route_available") is False)

print(f"RESULT: PATCH_295_BEHAVIOR {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
