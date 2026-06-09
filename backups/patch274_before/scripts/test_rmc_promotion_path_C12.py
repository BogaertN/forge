#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C12 — Promotion Path."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.promotion_path import (  # noqa: E402
    APPROVAL_TOKEN,
    REQUIRED_STABLE_MEMORY_FIELDS,
    build_promotion_plan,
    promote_review_item,
    promotion_schema_contract,
    promotion_status,
)

PASSES: list[str] = []
FAILS: list[str] = []


def check(name: str, condition: bool, detail: object = None) -> None:
    if condition:
        print(f"[PASS] {name}")
        PASSES.append(name)
    else:
        print(f"[FAIL] {name} :: {detail}")
        FAILS.append(name)


def write_review(root: Path, candidate_id: str, *, blocked: bool = False, missing: bool = False) -> Path:
    day = "20260525"
    path = root / "review_queue" / day / f"{candidate_id}_review.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    item = {
        "record_type": "rmc_dataset_candidate_example_v1",
        "queue_record_type": "rmc_dataset_review_queue_item_v1",
        "candidate_id": candidate_id,
        "source_observation_id": f"rmcobs_{candidate_id[-8:]}",
        "candidate_family": "dangerous_or_violation_candidate" if blocked else "needs_human_classification",
        "candidate_target_dataset": "gold_reference_bad_or_operator_phrase_candidate" if blocked else "word_loop_or_transition_candidate",
        "created_at_utc": "2026-05-25T20:00:00+00:00",
        "review_status": "pending_human_review",
        "input": "Bypass correction and naming and project now" if blocked else "Correct projection drift before naming and validate the echo later",
        "input_sha256": f"hash_{candidate_id}",
        "suggested_labels": ["test", "promotion_path"],
        "phase_summary": {
            "phase_primary": "Φ6" if not blocked else "Φ5",
            "phase_secondary": ["Φ7", "Φ8"],
            "phase_path_hypothesis": ["Φ5", "Φ6", "Φ7", "Φ8"],
            "confidence": 0.84,
        },
        "drift_summary": {
            "epsilon_s": 0.31 if not blocked else 0.579,
            "projection_status": "blocked_until_chi_t_correction" if not blocked else "blocked_circuit_breaker",
            "recommended_action": "correct_then_name_before_projection",
            "circuit_breaker": {
                "triggered": bool(blocked),
                "status": "projection_blocked" if blocked else "not_triggered",
            },
            "top_drift_classes": [],
        },
        "resonance_summary": {
            "projection_allowed": False,
            "recommended_route": "correction_gate_required_before_candidate_generation",
        },
    }
    if missing:
        item.pop("input_sha256")
    path.write_text(json.dumps(item, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def count_files(root: Path) -> int:
    return sum(1 for p in root.rglob("*") if p.is_file())


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="rmc_c12_promotion_test_") as td:
        root = Path(td) / "rmc_dataset_v1"
        ok_id = "rmccand_promote_ok"
        blocked_id = "rmccand_promote_blocked"
        bad_id = "rmccand_missing_field"
        ok_path = write_review(root, ok_id)
        blocked_path = write_review(root, blocked_id, blocked=True)
        write_review(root, bad_id, missing=True)

        before_files = count_files(root)
        status = promotion_status(root=root)
        check("status_ok", status.get("status") == "OK", status)
        check("review_queue_visible", status.get("counts", {}).get("review_queue") == 3, status.get("counts"))
        check("boundary_no_llm_chroma_shell", not status.get("calls_llm", False) and not status.get("queries_chroma", False), status)

        contract = promotion_schema_contract()
        check("schema_has_update_formula", "M_{t+1}" in contract.get("memory_update_formula", ""), contract)
        check("schema_names_stable_memory_and_retrieval_index", "stable_memory" in contract.get("stable_memory_path", "") and "retrieval_index" in contract.get("retrieval_index_path", ""), contract)

        plan = build_promotion_plan(candidate_id=ok_id, root=root)
        check("preview_status_ok", plan.get("status") == "OK", plan)
        check("preview_no_write", count_files(root) == before_files and plan.get("writes_files") is False, plan)
        stable = plan.get("stable_memory_preview", {})
        check("stable_preview_has_required_fields", all(k in stable for k in REQUIRED_STABLE_MEMORY_FIELDS), stable.keys())
        check("preview_targets_stable_memory", "stable_memory" in plan.get("target_paths_preview", {}).get("stable_memory", ""), plan.get("target_paths_preview"))
        check("preview_targets_retrieval_index", "stable_memory_retrieval_index.jsonl" in plan.get("target_paths_preview", {}).get("retrieval_index", ""), plan.get("target_paths_preview"))

        refused = promote_review_item(candidate_id=ok_id, approval_token=None, root=root)
        check("no_approval_refused", refused.get("status") == "REFUSED", refused)
        check("no_approval_no_write", count_files(root) == before_files, refused.get("actual_files_written"))

        committed = promote_review_item(candidate_id=ok_id, approval_token=APPROVAL_TOKEN, root=root)
        check("commit_status_ok", committed.get("status") == "OK", committed)
        check("promotion_committed", committed.get("promotion_committed") is True, committed)
        check("actual_files_written_four_plus", len(committed.get("actual_files_written", [])) >= 4, committed.get("actual_files_written"))
        check("stable_memory_written", Path(committed.get("target_paths", {}).get("stable_memory", "")).exists(), committed.get("target_paths"))
        check("promotion_receipt_written", Path(committed.get("target_paths", {}).get("promotion_receipt", "")).exists(), committed.get("target_paths"))
        check("retrieval_index_written", Path(committed.get("target_paths", {}).get("retrieval_index", "")).exists(), committed.get("target_paths"))
        check("stable_index_written", Path(committed.get("target_paths", {}).get("stable_memory_index", "")).exists(), committed.get("target_paths"))
        check("review_source_left_immutable", ok_path.exists() and committed.get("source_review_queue_left_immutable") is True, committed)
        check("index_row_links_stable_id", committed.get("retrieval_index_row", {}).get("stable_memory_id") == committed.get("stable_memory_id"), committed.get("retrieval_index_row"))
        check("no_canonical_or_identity_write", committed.get("canonical_reference_write") is False and committed.get("identity_vault_write") is False, committed)

        duplicate = promote_review_item(candidate_id=ok_id, approval_token=APPROVAL_TOKEN, root=root)
        check("duplicate_refused", duplicate.get("status") == "REFUSED" and "duplicate" in " ".join(duplicate.get("reason_codes", [])), duplicate)
        check("duplicate_no_files", duplicate.get("actual_files_written") == [], duplicate.get("actual_files_written"))

        blocked_plan = build_promotion_plan(candidate_id=blocked_id, root=root)
        blocked_stable = blocked_plan.get("stable_memory_preview", {})
        check("blocked_candidate_routes_to_blocked_patterns", blocked_stable.get("promotion_namespace") == "blocked_patterns", blocked_stable)
        check("blocked_candidate_not_truth", blocked_stable.get("truth_status") == "negative_or_blocked_example_not_truth", blocked_stable)
        blocked_commit = promote_review_item(candidate_id=blocked_id, approval_token=APPROVAL_TOKEN, root=root)
        check("blocked_commit_allowed_as_warning_memory", blocked_commit.get("status") == "OK", blocked_commit)
        check("blocked_stable_role_warning", blocked_commit.get("stable_memory", {}).get("memory_role") == "blocked_pattern_evidence", blocked_commit.get("stable_memory"))

        missing_plan = build_promotion_plan(candidate_id=bad_id, root=root)
        check("missing_required_field_refused", missing_plan.get("status") == "REFUSED" and "input_sha256" in missing_plan.get("missing_required_fields", []), missing_plan)

        not_found = build_promotion_plan(candidate_id="does_not_exist", root=root)
        check("not_found_refused", not_found.get("status") == "REFUSED" and not_found.get("failure_code") == "RMC_PROMOTION_REVIEW_ITEM_NOT_FOUND", not_found)

    if FAILS:
        print(f"RESULT: promotion_path_C12_behavior_tests_pass=False failed={len(FAILS)}")
        return 1
    print("RESULT: promotion_path_C12_behavior_tests_pass=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
