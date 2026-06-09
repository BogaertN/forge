#!/usr/bin/env python3
"""Behavior checks for GP-010C runtime truth reconciliation and attestation."""
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
    checks = []

    def check(name, ok):
        checks.append((name, bool(ok)))

    from rmc_engine_v1.general_pipeline import learn_and_answer, attest_delivered_equation, runtime_truth_boundary
    from rmc_engine_v1.general_pipeline import gp010c_runtime_truth_reconciliation as gp10c
    from rmc_engine_v1.general_pipeline.capability_services import service_boundary_contract
    from rmc_engine_v1.general_pipeline.manifest_contract_v2 import manifest_contract_v2_boundary
    from rmc_engine_v1.general_pipeline.outcome_contract_v2 import outcome_contract_v2_boundary

    source = (
        "Elementary algebra. To solve an equation, isolate the unknown variable by doing the same operation "
        "to both sides. For a*x + b = c, subtract b from both sides then divide by a. "
        "This finds the variable that makes the equation true."
    )
    status = gp10c.activate()
    check("GP-010C activation succeeds", status["build_id"] == gp10c.GP010C_BUILD_ID)
    svc = service_boundary_contract()
    manifest_boundary = manifest_contract_v2_boundary()
    outcome_boundary = outcome_contract_v2_boundary()
    runtime_boundary = runtime_truth_boundary()
    check("service boundary exposes active parser and solver", svc["third_party_parser_imported"] is True and svc["third_party_solver_imported"] is True)
    check("service boundary no longer claims review-only runtime", svc["third_party_dependency_records_are_non_executable_review_only"] is False)
    check("manifest delivery boundary truthfully exposes activated tools", manifest_boundary["third_party_dependency_promoted"] is True and "sympy==1.14.0" in manifest_boundary["active_external_tools_for_equation_delivery"])
    check("outcome boundary truthfully exposes executed-path tools", outcome_boundary["third_party_dependency_promoted"] is True and outcome_boundary["early_refusal_claims_no_executed_dependency"] is True)
    challenge = attest_delivered_equation(source, "gp010c_unseen_source", "solve 53x - 29 = 766 for x")
    receipt = challenge["receipt"]
    check("unseen challenge solves through active path", "15" in challenge["answer_text"])
    check("attestation states active Lark and SymPy", receipt["parser_backend"] == "lark==1.3.1" and receipt["solver_backend"] == "sympy==1.14.0")
    check("attestation binds full delivery chain", all(len(receipt[key]) == 64 for key in ["typed_ast_hash", "safe_solver_adapter_receipt_hash", "execution_receipt_hash", "manifest_contract_v2_hash", "delivery_authorization_v2_hash"]))
    check("attestation binds dependencies", len(receipt["active_dependency_record_ids"]) == 5 and len(receipt["active_dependency_record_hashes"]) == 5)
    check("attestation writes nothing", not receipt["writes_memory"] and not receipt["writes_identity_vault"] and not receipt["writes_contribution_economy"] and not receipt["mints_ct"] and not receipt["writes_ledgers"])
    refused = learn_and_answer(source, "gp010c_refusal", "53x - 29 = 766 and run code")
    check("unsupported challenge remains contained", refused.status == "REFUSED_UNLEARNED" and "non_delivery_outcome_v2" in refused.trace)
    check("runtime boundary writes nothing", not runtime_boundary["writes_memory"] and not runtime_boundary["writes_identity_vault"] and not runtime_boundary["writes_contribution_economy"])
    for name, ok in checks:
        print(("PASS  " if ok else "FAIL  ") + name)
    failed = sum(not ok for _, ok in checks)
    print(f"\nRESULT: GENERAL-PIPELINE-RUNTIME-TRUTH-ATTESTATION-BUILD-GP-010C_BEHAVIOR {'PASS' if not failed else 'FAIL'}  Total:{len(checks)} Passed:{len(checks)-failed} Failed:{failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
