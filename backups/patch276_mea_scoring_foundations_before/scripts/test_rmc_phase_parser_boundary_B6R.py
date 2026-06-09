#!/usr/bin/env python3
"""Patch 262J1R-Preflight-B6R phase parser boundary behavior tests.

Purpose:
- prove exact/whole-word keyword matching
- prevent Φ2 keyword `or` from matching inside `before`
- verify correction-before-naming sequencing is parsed as Φ5→Φ6→Φ7/Φ8 context
- keep the phase parser side-effect free and low-confidence-aware
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.phase_parser import parse_phase, phase_parser_boundary  # noqa: E402


def _phase_state(text: str) -> dict:
    return parse_phase(text, {"source_kind": "test_input"}).get("phase_state", {})


def _candidate(state: dict, phase: str) -> dict:
    for item in state.get("phase_candidates", []):
        if item.get("phase") == phase:
            return item
    return {}


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"{name} failed" + (f": {detail}" if detail else ""))


def main() -> None:
    # The exact live regression from B6: `before` must not trigger keyword:or.
    state = _phase_state("How do we correct projection drift before naming?")
    phi2 = _candidate(state, "Φ2")
    phi2_evidence = phi2.get("evidence", [])
    check("before_does_not_emit_keyword_or", "keyword:or" not in phi2_evidence, str(phi2_evidence))
    check("primary_not_phi2_for_correction_drift_query", state.get("phase_primary") != "Φ2", str(state))
    check("primary_is_correction_for_correction_query", state.get("phase_primary") == "Φ6", str(state))
    check("path_contains_drift_correction_naming", all(p in state.get("phase_path_hypothesis", []) for p in ["Φ5", "Φ6", "Φ7"]), str(state.get("phase_path_hypothesis")))
    check("no_false_phase_skip_from_phi2_to_phi5", not any(w.get("from") == "Φ2" and w.get("to") == "Φ5" for w in state.get("transition_warnings", [])), str(state.get("transition_warnings")))
    check("boundary_mode_reported", state.get("token_boundary_mode") == "whole_word_keyword_matching_B6R", str(state))

    # Real polarity language should still detect Φ2.
    state2 = _phase_state("Compare either option or the opposite direction.")
    phi2b = _candidate(state2, "Φ2")
    check("real_or_still_detected", "keyword:or" in phi2b.get("evidence", []), str(phi2b))
    check("real_compare_primary_phi2", state2.get("phase_primary") == "Φ2", str(state2))

    # Sequencing language should support naming gate without false polarity.
    state3 = _phase_state("Do validation before naming the stable candidate.")
    phi2c = _candidate(state3, "Φ2")
    check("before_naming_no_false_or", "keyword:or" not in phi2c.get("evidence", []), str(phi2c))
    check("before_naming_supports_phi7", "Φ7" in state3.get("phase_path_hypothesis", []), str(state3))

    # Low-confidence/unclassified input must explicitly report review status.
    state4 = _phase_state("blargle florp zed zed")
    check("low_confidence_status_present", state4.get("confidence_status") in {"phase_review_required", "phase_confidence_acceptable"}, str(state4))
    check("unclassified_routes_as_seed_or_review", state4.get("confidence") <= 0.4, str(state4))

    boundary = phase_parser_boundary()
    for key in ["side_effect_free", "calls_llm", "queries_chroma", "writes_files", "writes_rmc_memory", "writes_identity_vault"]:
        value = boundary.get(key)
        expected = False if key != "side_effect_free" else True
        check(f"boundary_{key}", value is expected, f"got {value!r}, expected {expected!r}")

    print("RESULT: phase_parser_boundary_B6R_tests_pass=True")


if __name__ == "__main__":
    main()
