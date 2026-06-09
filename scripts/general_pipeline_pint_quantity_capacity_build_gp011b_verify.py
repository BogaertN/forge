#!/usr/bin/env python3
"""Structural/live verifier for GP-011B active Pint integration."""
from __future__ import annotations
import argparse, sys
from pathlib import Path

CAPACITY_SOURCE = "Fractions and capacity: when part of a full container is removed, the change in the fraction full equals the amount removed divided by the whole capacity."

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--forge-root", default=None); args=ap.parse_args()
    root=Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root)); gp=root/"rmc_engine_v1/general_pipeline"; checks=[]
    def check(name, ok): checks.append((name, bool(ok)))
    required=[
        "quantity_ast.py", "quantity_adapters.py", "quantity_runtime_attestation_gp011b.py",
        "gp011b_pint_quantity_integration.py", "dependency_registry.py", "domains.py",
        "capability_services.py", "manifest_contract_v2.py", "pipeline.py",
    ]
    for name in required: check(f"module present {name}", (gp/name).is_file())
    from rmc_engine_v1.general_pipeline import learn_and_answer, attest_delivered_capacity
    from rmc_engine_v1.general_pipeline import gp011b_pint_quantity_integration as gp011b
    from rmc_engine_v1.general_pipeline.dependency_registry import active_runtime_dependency_ids, dependency_boundary_contract
    state=gp011b.activate(); boundary=dependency_boundary_contract()
    check("exact Pint dependency installation/reuse boundary", state["installation_exact"] is True)
    check("Pint is active runtime service", "Pint==0.25.3" in boundary["third_party_components_imported_for_runtime_service"])
    check("typing_extensions is protected reused dependency", boundary["preexisting_dependency_reused_without_replacement"] == ["typing_extensions==4.15.0"])
    check("capacity dependency path includes Pint runtime chain", len(active_runtime_dependency_ids("fraction_change_capacity")) == 7)
    answer=learn_and_answer(CAPACITY_SOURCE, "verify", "A tank was 3/4 full. After 21 liters were removed, it was 1/2 full. What is the full capacity of the tank in milliliters?")
    check("live capacity answers with Pint conversion", answer.status=="ANSWERED" and "84000 milliliters" in answer.answer_text)
    check("live receipt names Pint", answer.trace["safe_quantity_adapter_receipt"]["quantity_backend"]=="pint==0.25.3")
    check("live receipt contains dimensionality", answer.trace["safe_quantity_adapter_receipt"]["dimensionality"]=="[length] ** 3")
    check("Manifest Contract carries quantity proof", len(answer.trace["manifest_contract_v2"]["quantity_ast_hash"])==64 and len(answer.trace["manifest_contract_v2"]["safe_quantity_adapter_receipt_hash"])==64)
    check("Echo remains final delivery gate", answer.trace["echo"]["approved_output"] is True and "delivery_authorization_v2_hash" in answer.trace)
    refused=learn_and_answer(CAPACITY_SOURCE, "verify", "A tank was 3/4 full. After 21 kilograms were removed, it was 1/2 full. What is the full capacity of the tank in liters?")
    check("dimensional mismatch is contained", refused.status=="REFUSED_UNLEARNED" and refused.trace["non_delivery_outcome_v2"]["stage"]=="FULL_INPUT_PARSE_REFUSED")
    att=attest_delivered_capacity(CAPACITY_SOURCE, "verify", "A bin was 11/12 full. After 21 kilograms were removed, it was 2/3 full. What is the full capacity of the bin?")
    check("attestation binds live Pint chain", att["receipt"]["quantity_backend"]=="pint==0.25.3" and len(att["receipt_hash"])==64)
    combined="\n".join((gp/name).read_text(encoding="utf-8") for name in ["quantity_ast.py","quantity_adapters.py","quantity_runtime_attestation_gp011b.py"])
    check("Pint is imported only in quantity boundary modules", "import pint" in combined)
    check("quantity boundary forbids arbitrary expression evaluation", "arbitrary_expression_evaluation_allowed" in (gp/"quantity_ast.py").read_text(encoding="utf-8"))
    check("no raw eval in quantity modules", "eval(" not in combined and "exec(" not in combined)
    check("no persistence or economy token in quantity execution", "sqlite3.connect" not in combined and "chromadb" not in combined and "mint_ct(" not in combined)
    for name,ok in checks: print(("PASS  " if ok else "FAIL  ")+name)
    failed=sum(not ok for _,ok in checks)
    print(f"\nRESULT: GENERAL-PIPELINE-PINT-QUANTITY-CAPACITY-INTEGRATION-BUILD-GP-011B_VERIFY {'PASS' if not failed else 'FAIL'}  Total:{len(checks)} Passed:{len(checks)-failed} Failed:{failed}")
    return 1 if failed else 0
if __name__=="__main__": raise SystemExit(main())
