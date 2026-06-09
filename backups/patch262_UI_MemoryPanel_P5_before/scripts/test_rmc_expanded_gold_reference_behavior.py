#!/usr/bin/env python3
"""Expanded gold-reference behavior tests for Patch 262J1R-Preflight-B4."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.resonance_lexicon import analyze_resonance

GOLD = ROOT / "rmc_engine_v1" / "reference" / "gold_reference_v1.jsonl"


def load_rows() -> list[dict]:
    rows = []
    for line in GOLD.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main() -> int:
    rows = load_rows()
    failed: list[str] = []
    passed = 0
    for row in rows:
        rid = row.get("id", "unknown")
        result = analyze_resonance(row.get("input", ""))
        try:
            if "expected_violation" in row:
                assert bool(result.get("violations")) == bool(row["expected_violation"]), f"violation mismatch: {result.get('violations')}"
            if "expected_circuit_breaker_candidate" in row:
                assert bool(result.get("circuit_breaker_candidate")) == bool(row["expected_circuit_breaker_candidate"]), f"circuit mismatch: {result.get('circuit_breaker_candidate')}"
            if row.get("expected_projection_allowed") is False:
                assert result.get("projection_allowed") is False, f"projection should be false, got {result.get('projection_allowed')!r}"
            if "expected_syntactic_drift" in row:
                assert bool(result.get("syntactic_firewall", {}).get("syntactic_drift")) == bool(row["expected_syntactic_drift"]), "syntactic drift mismatch"
            passed += 1
        except Exception as exc:
            failed.append(f"{rid}: {exc}")
    if failed:
        print("FAILED EXPANDED GOLD REFERENCES:")
        for item in failed[:80]:
            print(" -", item)
        print(f"Total: {len(rows)}")
        print(f"Passed: {passed}")
        print(f"Failed: {len(failed)}")
        return 1
    print(f"Total: {len(rows)}")
    print(f"Passed: {passed}")
    print("Failed: 0")
    print("RESULT: expanded_gold_reference_B4_behavior_tests_pass=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
