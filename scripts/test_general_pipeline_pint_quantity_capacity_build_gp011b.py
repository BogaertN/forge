#!/usr/bin/env python3
"""Behavior tests for GP-011B active Pint quantity/capacity integration."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
from hypothesis import given, settings, strategies as st

CAPACITY_SOURCE = (
    "Fractions and capacity: when part of a full container is removed, the change in the "
    "fraction full equals the amount removed divided by the whole capacity."
)

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--forge-root", default=None); args=ap.parse_args()
    root=Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    checks=[]
    def check(name, ok): checks.append((name, bool(ok)))

    from rmc_engine_v1.general_pipeline import learn_and_answer, attest_delivered_capacity
    from rmc_engine_v1.general_pipeline import gp011b_pint_quantity_integration as gp011b
    from rmc_engine_v1.general_pipeline.dependency_registry import (
        active_runtime_dependency_ids, dependency_records_for_ids, dependency_boundary_contract
    )
    from rmc_engine_v1.general_pipeline.quantity_ast import quantity_ast_boundary_contract
    from rmc_engine_v1.general_pipeline.quantity_adapters import safe_quantity_adapter_boundary_contract

    state=gp011b.activate()
    versions=state["newly_installed_distribution_versions"]
    protected=state["protected_preexisting_reused_distribution_versions"]
    check("Pint integration activation succeeds", state["installation_exact"])
    check("Pint installed exact version", versions["pint"] == "0.25.3")
    check("Pint runtime transitive versions installed", versions["flexcache"] == "0.3" and versions["flexparser"] == "0.4" and versions["platformdirs"] == "4.10.0")
    check("typing_extensions exact pre-existing dependency reused", protected["typing_extensions"] == "4.15.0")
    dep_ids=active_runtime_dependency_ids("fraction_change_capacity")
    check("capacity service binds seven governed dependencies", len(dep_ids) == 7)
    records=dependency_records_for_ids(dep_ids)
    check("capacity service includes Pint", any("pint" in r.dependency_id for r in records))
    typing_record=next(r for r in records if "typing_extensions" in r.dependency_id)
    check("protected typing_extensions was not claimed installed by GP-011B", typing_record.installed_by_this_build is False and typing_record.installation_allowed is False)

    legacy=learn_and_answer(CAPACITY_SOURCE, "cap", "A storage bin was 11/12 full. After 21 kilograms were removed, it was 2/3 full. What is the full capacity of the storage bin?")
    check("legacy capacity answer remains correct", legacy.status == "ANSWERED" and "84 kilograms" in legacy.answer_text)
    check("legacy capacity now executes through Pint", legacy.trace["safe_quantity_adapter_receipt"]["quantity_backend"] == "pint==0.25.3")
    check("mass dimensionality recorded", legacy.trace["safe_quantity_adapter_receipt"]["dimensionality"] == "[mass]")
    check("capacity trace stores quantity AST", len(legacy.trace["quantity_ast_hash"]) == 64)
    check("Manifest Contract v2 binds quantity AST", legacy.trace["manifest_contract_v2"]["quantity_ast_hash"] == legacy.trace["quantity_ast_hash"])
    check("Echo still gates capacity delivery", legacy.trace["echo"]["approved_output"] is True and "delivery_authorization_v2_hash" in legacy.trace)

    mass_conversion=learn_and_answer(CAPACITY_SOURCE, "cap", "A tank was 3/4 full. After 21 kilograms were removed, it was 1/2 full. What is the full capacity of the tank in grams?")
    check("Pint mass conversion succeeds", mass_conversion.status == "ANSWERED" and "84000 grams" in mass_conversion.answer_text)
    volume_conversion=learn_and_answer(CAPACITY_SOURCE, "cap", "A tank was 3/4 full. After 21 liters were removed, it was 1/2 full. What is the full capacity of the tank in milliliters?")
    check("Pint volume conversion succeeds", volume_conversion.status == "ANSWERED" and "84000 milliliters" in volume_conversion.answer_text)
    check("volume dimensionality recorded", volume_conversion.trace["safe_quantity_adapter_receipt"]["dimensionality"] == "[length] ** 3")

    bad_length=learn_and_answer(CAPACITY_SOURCE, "cap", "A tank was 3/4 full. After 21 meters were removed, it was 1/2 full. What is the full capacity of the tank?")
    check("length quantity refused as non-capacity dimension", bad_length.status == "REFUSED_UNLEARNED" and bad_length.trace["non_delivery_outcome_v2"]["stage"] == "FULL_INPUT_PARSE_REFUSED" and "mass or volume" in bad_length.reasons[0])
    bad_conversion=learn_and_answer(CAPACITY_SOURCE, "cap", "A tank was 3/4 full. After 21 kilograms were removed, it was 1/2 full. What is the full capacity of the tank in liters?")
    check("incompatible dimensional conversion refused", bad_conversion.status == "REFUSED_UNLEARNED" and "incompatible" in bad_conversion.reasons[0])
    bad_rate=learn_and_answer(CAPACITY_SOURCE, "cap", "A tank was 3/4 full. After 21 kilograms/hour were removed, it was 1/2 full. What is the full capacity of the tank?")
    check("rate quantity refused for capacity", bad_rate.status == "REFUSED_UNLEARNED" and "mass or volume" in bad_rate.reasons[0])

    attested=attest_delivered_capacity(CAPACITY_SOURCE, "attested", "A jar was 5/6 full. After 24 cups were removed, it was 1/3 full. What is the full capacity of the jar in milliliters?")
    receipt=attested["receipt"]
    check("side-effect-free Pint attestation succeeds", receipt["status"] == "ACTIVE_PINT_QUANTITY_DELIVERY_ATTESTED")
    check("attestation binds Pint backend", receipt["quantity_backend"] == "pint==0.25.3")
    check("attestation binds receipt chain", all(len(receipt[k]) == 64 for k in ("quantity_ast_hash","safe_quantity_adapter_receipt_hash","execution_receipt_hash","manifest_contract_v2_hash","delivery_authorization_v2_hash")))
    check("attestation has no prohibited writes", not receipt["writes_memory"] and not receipt["writes_identity_vault"] and not receipt["writes_contribution_economy"] and not receipt["mints_ct"] and not receipt["writes_ledgers"])

    @settings(max_examples=60, derandomize=True, deadline=None, database=None)
    @given(
        removed=st.integers(min_value=1, max_value=500),
        unit_pair=st.sampled_from([("kilograms","grams"), ("liters","milliliters"), ("gallons","cups")]),
    )
    def unit_conversion_property(removed, unit_pair):
        source_unit, target_unit = unit_pair
        question=(f"A tank was 3/4 full. After {removed} {source_unit} were removed, it was 1/2 full. "
                  f"What is the full capacity of the tank in {target_unit}?")
        result=learn_and_answer(CAPACITY_SOURCE, "generated", question)
        assert result.status == "ANSWERED"
        assert result.trace["safe_quantity_adapter_receipt"]["quantity_backend"] == "pint==0.25.3"
        assert result.trace["solution"]["verified"] is True
        assert result.trace["echo"]["approved_output"] is True
    try:
        unit_conversion_property(); generated_valid=True
    except Exception as exc:
        print("PROPERTY FAILURE valid capacity:", exc); generated_valid=False
    check("Hypothesis validates 60 Pint quantity cases", generated_valid)

    @settings(max_examples=30, derandomize=True, deadline=None, database=None)
    @given(
        removed=st.integers(min_value=1, max_value=500),
        bad_pair=st.sampled_from([("kilograms","liters"), ("liters","grams"), ("meters","meters"), ("kilograms/hour","kilograms")]),
    )
    def refusal_property(removed, bad_pair):
        source_unit, target_unit = bad_pair
        question=(f"A tank was 3/4 full. After {removed} {source_unit} were removed, it was 1/2 full. "
                  f"What is the full capacity of the tank in {target_unit}?")
        result=learn_and_answer(CAPACITY_SOURCE, "generated", question)
        assert result.status == "REFUSED_UNLEARNED"
        assert result.trace["non_delivery_outcome_v2"]["output_delivery_permission"].startswith("NO_HUMAN_TEXT_DELIVERY")
    try:
        refusal_property(); generated_refusal=True
    except Exception as exc:
        print("PROPERTY FAILURE refusal:", exc); generated_refusal=False
    check("Hypothesis validates 30 dimensional-refusal cases", generated_refusal)

    qboundary=quantity_ast_boundary_contract()
    abound=safe_quantity_adapter_boundary_contract()
    dbound=dependency_boundary_contract()
    check("quantity boundary authorizes only mass and volume", qboundary["allowed_dimensionalities"] == ["[length] ** 3", "[mass]"])
    check("quantity adapter forbids raw expressions", abound["adapter_accepts_raw_user_expression"] is False)
    check("dependency registry truthfully declares Pint runtime service", "Pint==0.25.3" in dbound["third_party_components_imported_for_runtime_service"])
    check("no corpus, memory, identity or economy write", not dbound["adds_corpus_ingestion"] and not dbound["writes_memory"] and not dbound["writes_identity_vault"] and not dbound["writes_contribution_economy"] and not dbound["mints_ct"])

    for name, ok in checks: print(("PASS  " if ok else "FAIL  ") + name)
    failed=sum(not ok for _,ok in checks)
    print(f"\nRESULT: GENERAL-PIPELINE-PINT-QUANTITY-CAPACITY-INTEGRATION-BUILD-GP-011B_BEHAVIOR {'PASS' if not failed else 'FAIL'}  Total:{len(checks)} Passed:{len(checks)-failed} Failed:{failed}")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
