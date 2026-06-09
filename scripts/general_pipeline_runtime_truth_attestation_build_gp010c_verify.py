#!/usr/bin/env python3
"""Structural/live checks for GP-010C truthful active-tool attestation."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forge-root", default=None)
    args = ap.parse_args()
    root = Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    gp = root / "rmc_engine_v1/general_pipeline"
    checks = []

    def check(name, ok):
        checks.append((name, bool(ok)))

    for filename in [
        "runtime_truth_attestation_gp010c.py",
        "gp010c_runtime_truth_reconciliation.py",
        "capability_services.py",
        "manifest_contract_v2.py",
        "outcome_contract_v2.py",
    ]:
        check(f"module present {filename}", (gp / filename).is_file())

    from rmc_engine_v1.general_pipeline.runtime_truth_attestation_gp010c import attest_delivered_equation, runtime_truth_boundary

    source = (
        "Elementary algebra. To solve an equation, isolate the unknown variable by doing the same operation "
        "to both sides. For a*x + b = c, subtract b from both sides then divide by a. "
        "This finds the variable that makes the equation true."
    )
    result = attest_delivered_equation(source, "gp010c_verify_source", "solve 97x + 31 = 1001 for x")
    check("challenge answer uses non-fixture exact result", "10" in result["answer_text"])
    check("receipt hash is SHA-256", len(result["receipt_hash"]) == 64)
    check("receipt claims real active tools", result["receipt"]["parser_backend"] == "lark==1.3.1" and result["receipt"]["solver_backend"] == "sympy==1.14.0")
    boundary = runtime_truth_boundary()
    check("truth reconciled across all boundary surfaces", boundary["service_boundary_truthful"] and boundary["manifest_boundary_truthful"] and boundary["outcome_boundary_truthful"])
    combined = "\n".join((gp / filename).read_text() for filename in ["runtime_truth_attestation_gp010c.py", "capability_services.py", "manifest_contract_v2.py", "outcome_contract_v2.py"])
    check("stale live review-only assertion removed from service boundary", '"third_party_dependency_records_are_non_executable_review_only": True' not in combined)
    check("stale no-promotion live assertions removed from downstream boundaries", '"third_party_dependency_promoted": False' not in combined)
    attestation_text = (gp / "runtime_truth_attestation_gp010c.py").read_text()
    check("no write or economy operation introduced", "open(" not in attestation_text and "Path.write" not in attestation_text)
    for name, ok in checks:
        print(("PASS  " if ok else "FAIL  ") + name)
    failed = sum(not ok for _, ok in checks)
    print(f"\nRESULT: GENERAL-PIPELINE-RUNTIME-TRUTH-ATTESTATION-BUILD-GP-010C_VERIFY {'PASS' if not failed else 'FAIL'}  Total:{len(checks)} Passed:{len(checks)-failed} Failed:{failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
