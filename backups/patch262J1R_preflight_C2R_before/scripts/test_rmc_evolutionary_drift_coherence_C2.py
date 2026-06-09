#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-C2."""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.evolutionary_drift_explorer import (
    evolutionary_drift_boundary,
    explore_evolutionary_drift,
    score_coherence,
)


def _candidate(candidate_id: str, kind: str, novelty: float, drift: float, phase_path: list[str], *, confidence: float = 0.75, allowed: bool = True):
    return {
        "candidate_id": candidate_id,
        "title": candidate_id,
        "candidate": f"meaning state {candidate_id}",
        "candidate_kind": kind,
        "meaning_state_not_sentence": True,
        "phase_target": phase_path[-1] if phase_path else "Φ6",
        "phase_path": phase_path,
        "memory_links": [{"memory_id": "mem1", "phase_tags": ["Φ5", "Φ6", "Φ7"], "retrieval_weight": 0.9}],
        "memory_support": {
            "memory_support_present": True,
            "active_memory_count": 3,
            "linked_memory_count": 2,
            "average_retrieval_weight": 0.84,
        },
        "confidence": confidence,
        "novelty": novelty,
        "drift": drift,
        "allowed_to_continue_to_scoring": allowed,
        "projection_allowed": False,
        "memory_write_allowed": False,
    }


def _sample_report(circuit: bool = False):
    if circuit:
        return {
            "status": "OK",
            "trace_id": "trace_circuit",
            "candidate_set_id": "ct_set_circuit",
            "candidate_generation_status": {"candidate_generation_allowed": False},
            "candidate_set": [_candidate("ct_blocked", "containment_correction_route", 0.0, 0.94, ["Φ5", "Φ6"], allowed=False)],
        }
    return {
        "status": "OK",
        "trace_id": "trace_ok",
        "candidate_set_id": "ct_set_ok",
        "candidate_generation_status": {"candidate_generation_allowed": True},
        "candidate_set": [
            _candidate("ct_direct", "direct_trace_candidate", 0.12, 0.21, ["Φ5", "Φ6", "Φ7"]),
            _candidate("ct_correction", "correction_candidate", 0.18, 0.24, ["Φ5", "Φ6", "Φ7", "Φ8"], confidence=0.86),
            _candidate("ct_evo", "bounded_evolutionary_candidate", 0.58, 0.28, ["Φ5", "Φ6", "Φ7"], confidence=0.68),
            _candidate("ct_bad", "bounded_evolutionary_candidate", 0.94, 0.72, ["Φ5", "Φ8"], confidence=0.44),
        ],
    }


def _check(name: str, condition: bool):
    if not condition:
        raise AssertionError(name)
    print(f"[PASS] {name}")


def main():
    boundary = evolutionary_drift_boundary()
    _check("boundary_read_only", boundary["writes_files"] is False and boundary["calls_llm"] is False)
    _check("boundary_stage", "Evolutionary Drift Explorer / E_t" in boundary["implements_rmc_stages"])

    evo = explore_evolutionary_drift(_sample_report(False))
    _check("evo_status_ok", evo["status"] == "OK")
    _check("E_t_present", evo["E_t_present"] is True)
    _check("branch_count", evo["E_t"]["branch_count"] >= 4)
    _check("bounded_branch_present", evo["E_t"]["bounded_branch_count"] >= 2)
    _check("bad_branch_blocked", any((not b["branch_allowed_to_score"]) and b.get("candidate_id") == "ct_bad" for b in evo["evolutionary_branches"]))
    _check("no_evo_rendering", evo["boundary"]["renders_final_language"] is False)

    scored = score_coherence(evo)
    _check("score_status_ok", scored["status"] == "OK")
    _check("S_t_present", scored["S_t_present"] is True)
    _check("scores_present", len(scored["candidate_scores"]) == 4)
    _check("selected_present", scored["selected_scored_candidate_preview"] is not None)
    _check("selected_not_bad", scored["selected_scored_candidate_preview"]["candidate_id"] != "ct_bad")
    _check("no_manifest_allowed", scored["S_t"]["manifest_allowed"] is False)
    _check("no_projection", scored["S_t"]["projection_allowed"] is False and scored["S_t"]["memory_write_allowed"] is False)

    blocked_evo = explore_evolutionary_drift(_sample_report(True))
    blocked_score = score_coherence(blocked_evo)
    _check("circuit_blocks_exploration", blocked_evo["E_t"]["exploration_allowed"] is False)
    _check("circuit_scores_zero", all(s["coherence_score"] == 0.0 for s in blocked_score["candidate_scores"]))

    print("RESULT: evolutionary_drift_coherence_C2_behavior_tests_pass=True")


if __name__ == "__main__":
    main()
