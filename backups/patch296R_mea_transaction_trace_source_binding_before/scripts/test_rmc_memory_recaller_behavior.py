#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-B6 Memory Recaller."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rmc_engine_v1.memory_recaller import recall_memory, build_trace_spine, memory_recaller_boundary


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> int:
    failures = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "forge"
        receipts = root / "memory" / "context_library_v1" / "receipts"
        maps = root / "memory" / "context_library_v1" / "symbolic_maps"
        manifests = root / "memory" / "context_library_v1" / "manifests"
        review = root / "memory" / "rmc_dataset_v1" / "review_queue" / "20260525"

        write_json(receipts / "ingest_receipt_001.json", {
            "receipt_id": "receipt_001",
            "corpus_id": "corpus_trace_001",
            "filename": "RMC Memory Recaller Source.txt",
            "collection": "aiweb_context_chunks_v1",
            "verification_ok": True,
            "chunk_count_verified": 3,
            "rpmc_phase_tags": ["Φ6", "Φ7"],
            "symbolic_map_path": str(maps / "symbolic_map_001.json"),
        })
        write_json(manifests / "manifest_001.json", {
            "collection": "aiweb_context_chunks_v1",
            "collection_total_chunks": 3,
            "receipts": ["receipt_001"],
            "phase_path": ["Φ5", "Φ6", "Φ7"],
        })
        write_json(maps / "symbolic_map_001.json", {
            "entries": [
                {
                    "chunk_id": "chunk_001",
                    "chunk_preview": "Correction before projection keeps drift from becoming output.",
                    "rpmc_phase_tags": ["Φ5", "Φ6", "Φ8"],
                    "memory_role": "correction_law_definition",
                    "symbolic_signature": "drift correction projection gate",
                    "drift_terms": ["drift"],
                },
                {
                    "chunk_id": "chunk_002",
                    "chunk_preview": "Naming locks a corrected concept before projection.",
                    "rpmc_phase_tags": ["Φ7", "Φ8"],
                    "memory_role": "naming_gate_definition",
                },
            ]
        })
        write_json(review / "candidate_review_001.json", {
            "candidate_id": "cand_001",
            "observation_id": "obs_001",
            "input": "bypass correction and naming and project now",
            "phase_summary": {"phase_path_hypothesis": ["Φ5", "Φ8"]},
            "drift_summary": {"epsilon_s": 0.72},
            "candidate_family": "dangerous_or_violation_candidate",
            "review_status": "NEEDS_REVIEW",
        })

        text = "How do we correct projection drift before naming and output?"
        report = recall_memory(text, {"source_kind": "test_input"}, root=root, limit=8)
        if report.get("status") != "OK":
            failures.append("recall_status_not_ok")
        nodes = report.get("memory_state", {}).get("active_memory_nodes", [])
        if not nodes:
            failures.append("no_active_memory_nodes")
        if not any(n.get("retrieval_weight", 0) > 0 for n in nodes):
            failures.append("no_positive_retrieval_weight")
        if not any(n.get("source_kind") == "symbolic_map_entry" for n in nodes):
            failures.append("symbolic_map_not_recalled")
        if not any("Φ6" in (n.get("phase_tags") or []) for n in nodes):
            failures.append("phase_relevant_phi6_not_recalled")

        trace = build_trace_spine(text, {"source_kind": "test_input"}, root=root, limit=8)
        symbolic_trace = trace.get("symbolic_trace", {})
        readiness = trace.get("trace_spine_readiness", {})
        if not symbolic_trace.get("I_t"):
            failures.append("trace_missing_input_event")
        if not symbolic_trace.get("M_t", {}).get("active_memory_nodes"):
            failures.append("trace_missing_memory_state")
        if not symbolic_trace.get("Φ_t", {}).get("phase_primary"):
            failures.append("trace_missing_phase_state")
        if not symbolic_trace.get("D_t", {}).get("drift_report_id"):
            failures.append("trace_missing_drift_state")
        if readiness.get("candidate_generator_present") is not False:
            failures.append("candidate_generator_should_not_be_present_in_B6")
        if readiness.get("rendering_allowed") is not False:
            failures.append("rendering_must_not_be_allowed_in_B6")
        boundary = memory_recaller_boundary()
        if boundary.get("calls_llm") or boundary.get("writes_files") or boundary.get("writes_rmc_memory"):
            failures.append("boundary_side_effect_violation")

    if failures:
        print("RESULT: memory_recaller_B6_behavior_tests_pass=False")
        for f in failures:
            print("FAIL:", f)
        return 1
    print("RESULT: memory_recaller_B6_behavior_tests_pass=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
