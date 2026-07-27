#!/usr/bin/env python3
"""LC-RMC phase parser compatibility-boundary behavior tests.

The predecessor B6R keyword classifier is intentionally retired. These tests
prove that only an admitted deterministic Language Core meaning receives an
RMC phase and that unsupported, ambiguous, and negated inputs stop.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.phase_parser import parse_phase, phase_parser_boundary  # noqa: E402


def _report(text: str) -> dict:
    return parse_phase(text, {"source_kind": "test_input"})


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"{name} failed" + (f": {detail}" if detail else ""))


def main() -> None:
    retired = _report("How do we correct projection drift before naming?")
    retired_state = retired.get("phase_state", {})
    check(
        "retired_keywords_do_not_create_phi2_or_phi6",
        retired.get("status") == "UNRESOLVED"
        and retired_state.get("phase_primary") is None,
        str(retired_state),
    )
    check(
        "retired_query_stops_before_rmc",
        retired_state.get("routing")
        == ["stop_before_rmc_meaning_admission"],
        str(retired_state),
    )
    check(
        "exact_source_span_boundary_reported",
        retired_state.get("token_boundary_mode")
        == "lc_rmc_001_exact_source_spans",
        str(retired_state),
    )

    inspect = _report("Inspect the current build status.")
    inspect_state = inspect.get("phase_state", {})
    check(
        "inspect_profile_binds_phi6",
        inspect.get("status") == "OK"
        and inspect_state.get("phase_primary") == "Φ6"
        and inspect_state.get("phase_path_hypothesis") == ["Φ6"],
        str(inspect_state),
    )

    report = _report("Report the repository state.")
    report_state = report.get("phase_state", {})
    check(
        "report_profile_binds_phi8",
        report.get("status") == "OK"
        and report_state.get("phase_primary") == "Φ8",
        str(report_state),
    )

    ambiguous = _report("Inspect the repository with the audit.")
    ambiguous_state = ambiguous.get("phase_state", {})
    check(
        "ambiguous_meaning_is_held",
        ambiguous.get("reason_code")
        == "LC_RMC_001_AMBIGUOUS_MEANING_HELD"
        and ambiguous_state.get("linguistic_candidate_count") == 2
        and ambiguous_state.get("phase_primary") is None,
        str(ambiguous_state),
    )

    negated = _report("Do not verify the packet checksum.")
    negated_state = negated.get("phase_state", {})
    check(
        "negated_action_is_held",
        negated.get("reason_code") == "LC_RMC_001_NEGATED_ACTION_HELD"
        and negated_state.get("negated") is True
        and negated_state.get("phase_primary") is None,
        str(negated_state),
    )

    unknown = _report("blargle florp zed zed")
    unknown_state = unknown.get("phase_state", {})
    check(
        "unknown_input_fails_closed_without_fallback",
        unknown.get("status") == "UNRESOLVED"
        and unknown.get("fallback_performed") is False
        and unknown_state.get("confidence") == 0.0,
        str(unknown_state),
    )

    boundary = phase_parser_boundary()
    for key in ["side_effect_free", "calls_llm", "queries_chroma", "writes_files", "writes_rmc_memory", "writes_identity_vault"]:
        value = boundary.get(key)
        expected = False if key != "side_effect_free" else True
        check(f"boundary_{key}", value is expected, f"got {value!r}, expected {expected!r}")

    print("RESULT: phase_parser_boundary_B6R_tests_pass=True")


if __name__ == "__main__":
    main()
