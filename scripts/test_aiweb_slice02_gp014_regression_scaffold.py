#!/usr/bin/env python3
"""Behavior smoke test for AI.Web Slice 2 GP-014 regression scaffold."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


def main() -> int:
    repo = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    sys.path.insert(0, str(repo))

    from aiweb_gp014_regression_scaffold.baseline import (
        GP014_BASELINE_IDENTITY,
        build_gp014_baseline_record,
        canonical_json as baseline_json,
        write_baseline_record,
    )
    from aiweb_gp014_regression_scaffold.regression import (
        build_regression_receipt,
        validate_regression_receipt,
        write_regression_receipt,
    )

    passes: list[str] = []
    failures: list[str] = []

    def check(condition: bool, label: str) -> None:
        if condition:
            passes.append(label)
        else:
            failures.append(label)

    discovered = ["docs/LANG-EXPR-001_GP-014_reference.txt"]
    baseline = build_gp014_baseline_record(repo, include_timestamp=False, discovered_files=discovered)
    check(baseline["baseline_identity"] == GP014_BASELINE_IDENTITY, "baseline identity matches")
    check(baseline["preservation_status"] == "preserved_not_superseded", "baseline status preserved")
    check(baseline["explicit_non_claims"]["gp014_superseded"] is False, "GP-014 supersession claim blocked")
    check(baseline["explicit_non_claims"]["gp014_replaced"] is False, "GP-014 replacement claim blocked")
    check("created_utc" not in baseline, "timestamp can be omitted for deterministic record")
    check(json.loads(baseline_json(baseline))["baseline_identity"] == GP014_BASELINE_IDENTITY, "baseline canonical JSON roundtrip works")

    changed = [
        "aiweb_gp014_regression_scaffold/__init__.py",
        "aiweb_gp014_regression_scaffold/baseline.py",
        "aiweb_gp014_regression_scaffold/regression.py",
        "aiweb_gp014_regression_scaffold/verify.py",
        "scripts/test_aiweb_slice02_gp014_regression_scaffold.py",
        "scripts/aiweb_slice02_gp014_regression_verify.py",
        "scripts/README_aiweb_slice02_gp014_regression_scaffold.md",
    ]
    receipt = build_regression_receipt(repo, baseline, changed_files=changed, include_timestamp=False)
    validation = validate_regression_receipt(receipt)
    check(validation["passed"] is True, "valid Slice 2 receipt passes validation")
    check(receipt["claims"]["gp014_superseded"] is False, "receipt blocks GP-014 supersession claim")
    check(receipt["claims"]["gp015_repaired"] is False, "receipt blocks GP-015 repair claim")

    bad_gp014 = build_regression_receipt(repo, baseline, changed_files=["core/GP-014_runtime.py"], include_timestamp=False)
    check(validate_regression_receipt(bad_gp014)["passed"] is False, "GP-014 touching receipt fails")

    bad_out_of_scope = build_regression_receipt(repo, baseline, changed_files=["random_file.py"], include_timestamp=False)
    check(validate_regression_receipt(bad_out_of_scope)["passed"] is False, "out-of-scope receipt fails")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        baseline_path = tmp_path / "baseline.json"
        receipt_path = tmp_path / "receipt.json"
        write_baseline_record(baseline_path, baseline)
        write_regression_receipt(receipt_path, receipt)
        check(baseline_path.is_file(), "write_baseline_record creates file")
        check(receipt_path.is_file(), "write_regression_receipt creates file")
        check(json.loads(baseline_path.read_text())["baseline_identity"] == GP014_BASELINE_IDENTITY, "baseline file JSON valid")
        check(json.loads(receipt_path.read_text())["slice_id"] == "SLICE-02", "receipt file JSON valid")

    print("============================================================")
    print("AIWEB SLICE 2 GP-014 REGRESSION SCAFFOLD BEHAVIOR TEST")
    print("============================================================")
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")
    if failures:
        print("VERDICT: FAIL - behavior test failure blocks acceptance")
        return 1
    print("VERDICT: PASS - behavior test passed within Slice 2 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
