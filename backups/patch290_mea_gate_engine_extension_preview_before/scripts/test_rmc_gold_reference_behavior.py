#!/usr/bin/env python3
"""Gold-reference fixture tests for Patch 262J1R-Preflight-B2."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.resonance_lexicon import analyze_resonance

GOLD = ROOT / "rmc_engine_v1" / "reference" / "gold_reference_v1.jsonl"


def load_rows(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main() -> int:
    rows = load_rows(GOLD)
    passed = 0
    failed: list[str] = []
    for row in rows:
        rid = row.get("id", "unknown")
        result = analyze_resonance(row.get("input", ""))
        try:
            if "expected_violation" in row:
                expected = bool(row["expected_violation"])
                actual = bool(result.get("violations"))
                assert actual == expected, f"expected_violation={expected}, actual={actual}"
            if "expected_circuit_breaker_candidate" in row:
                expected = bool(row["expected_circuit_breaker_candidate"])
                actual = bool(result.get("circuit_breaker_candidate"))
                assert actual == expected, f"expected_circuit_breaker_candidate={expected}, actual={actual}"
            if "expected_projection_allowed" in row and row["expected_projection_allowed"] is False:
                assert result.get("projection_allowed") is False, f"projection should be false, got {result.get('projection_allowed')!r}"
            if row.get("expected_syntactic_drift") is True:
                assert result.get("syntactic_firewall", {}).get("syntactic_drift") is True, "syntactic drift expected"
            passed += 1
        except Exception as exc:
            failed.append(f"{rid}: {exc}")
    if failed:
        print("FAILED GOLD REFERENCES:")
        for item in failed:
            print(" -", item)
        print(f"Total: {len(rows)}")
        print(f"Passed: {passed}")
        print(f"Failed: {len(failed)}")
        return 1
    print(f"Total: {len(rows)}")
    print(f"Passed: {passed}")
    print("Failed: 0")
    print("RESULT: gold_reference_B2_behavior_tests_pass=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
