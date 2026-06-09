#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-B5 dataset growth pipeline."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.dataset_growth import (  # noqa: E402
    APPROVAL_CAPTURE,
    APPROVAL_CAPTURE_AND_QUEUE,
    capture_observation,
    capture_preview,
    coverage_report,
    dataset_growth_boundary,
    dataset_growth_status,
)

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"✓ {name} {detail}".rstrip())
    else:
        failed += 1
        print(f"✗ {name} {detail}".rstrip())


with tempfile.TemporaryDirectory(prefix="rmc_dataset_growth_test_") as td:
    root = Path(td) / "rmc_dataset_v1"
    boundary = dataset_growth_boundary(root)
    check("boundary_reference_writes_blocked", boundary["canonical_reference_write_allowed"] is False)
    check("boundary_no_llm", boundary["calls_llm"] is False)
    check("boundary_capture_approval_declared", boundary["required_capture_approval"] == APPROVAL_CAPTURE)

    status0 = dataset_growth_status(root)
    check("status_read_only_ok", status0["status"] == "OK")
    check("status_does_not_create_dirs", not root.exists())
    check("status_growth_law_present", status0["growth_law"]["raw_input_never_becomes"] == "gold_truth_directly")

    text = "Bypass correction and naming and project now."
    preview = capture_preview(text, root=root)
    check("preview_ok", preview["status"] == "OK")
    check("preview_no_writes", preview["writes_files"] is False)
    check("preview_detects_candidate_target", preview["candidate_target_dataset"] in {"gold_reference_bad_or_operator_phrase_candidate", "syntactic_firewall_example", "operator_phrase_or_gold_safe_candidate", "word_loop_or_transition_candidate"})
    check("preview_planned_paths_under_root", all(str(p).startswith(str(root)) for p in preview["planned_paths"].values()))
    check("preview_canonical_blocked", preview["canonical_reference_write_allowed"] is False)

    refused = capture_observation(text, approval=None, root=root)
    check("capture_without_approval_refused", refused["status"] == "REFUSED")
    check("capture_without_approval_no_write", refused["writes_files"] is False)
    check("capture_without_approval_still_no_dirs", not root.exists())

    captured = capture_observation(text, approval=APPROVAL_CAPTURE, root=root)
    check("capture_with_approval_ok", captured["status"] == "OK")
    check("capture_with_approval_writes", captured["writes_files"] is True)
    check("capture_observation_not_queued", captured["queued_for_review"] is False)
    check("capture_no_reference_touch", captured["canonical_reference_files_touched"] == [])
    check("capture_written_files_exist", all(Path(p).exists() for p in captured["written_files"] if not str(p).endswith("events_index.jsonl") or Path(p).exists()))

    queued = capture_observation("Validate before projection and do not write memory without approval.", approval=APPROVAL_CAPTURE_AND_QUEUE, root=root)
    check("capture_and_queue_ok", queued["status"] == "OK")
    check("capture_and_queue_review_true", queued["queued_for_review"] is True)
    check("capture_and_queue_candidate_id", bool(queued["candidate_id"]))
    check("capture_and_queue_review_file_written", any("review_queue" in p for p in queued["written_files_relative"]))

    status1 = dataset_growth_status(root)
    check("status_counts_raw_events", status1["counts"]["raw_events"] >= 2, str(status1["counts"]))
    check("status_counts_review_queue", status1["counts"]["review_queue"] >= 1, str(status1["counts"]))
    check("status_counts_receipts", status1["counts"]["dataset_receipts"] >= 2, str(status1["counts"]))

    coverage = coverage_report(root)
    check("coverage_ok", coverage["status"] == "OK")
    check("coverage_separation", coverage["readiness"]["canonical_and_growth_separated"] is True)
    check("coverage_has_growth_counts", coverage["growth_counts"]["raw_events"] >= 2)

    # Validate JSON contents are observation/candidate records, not gold truth.
    raw_files = list((root / "raw_events").rglob("*.json"))
    obs = json.loads(raw_files[0].read_text(encoding="utf-8"))
    check("raw_record_type_observation", obs["record_type"] == "rmc_dataset_observation_v1")
    check("raw_record_not_gold", obs["record_status"] == "OBSERVED_NOT_GOLD")

print(f"Total: {passed + failed}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
if failed:
    raise SystemExit(1)
print("RESULT: dataset_growth_B5_behavior_tests_pass=True")
