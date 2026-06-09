#!/usr/bin/env python3
"""Behavior tests for GP-005 — Forge-owned capability service contracts.

Run:
    .venv/bin/python scripts/test_general_pipeline_capability_services_build_gp005.py --forge-root "$HOME/forge"

This test is in-memory only. It proves that capability execution travels
through immutable service contracts, canonical invocation requests, and
execution receipts while the existing gate/RMC/Echo authority chain remains
intact.
"""

from __future__ import annotations

import argparse
from dataclasses import FrozenInstanceError, replace
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", default=None)
    args = parser.parse_args()
    forge_root = Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(forge_root))

    from rmc_engine_v1.general_pipeline import learn_and_answer
    from rmc_engine_v1.general_pipeline import gp005_capability_services as gp5
    from rmc_engine_v1.general_pipeline.capability_services import (
        CapabilityServiceBoundaryError,
        all_service_contracts,
        build_execution_request,
        execute_request,
        service_boundary_contract,
        service_contract_for_domain,
        service_registry_hash,
    )
    from rmc_engine_v1.general_pipeline.domains_equations import LinearEquationOneUnknownDomain

    status = gp5.activate()
    algebra_book = (
        "Elementary algebra. To solve an equation, isolate the unknown variable by doing the "
        "same operation to both sides. For a*x + b = c, subtract b from both sides then divide "
        "by a. This finds the variable that makes the equation true."
    )
    math_book = (
        "Elementary arithmetic teaches how to add, subtract, multiply and divide whole numbers. "
        "Fractions and capacity: when part of a full container is removed, the change in the "
        "fraction full equals the amount removed divided by the whole capacity."
    )
    wp_book = (
        "Elementary word problems about counting. A word problem describes a starting count "
        "that changes. Buying, finding, receiving, or gaining more increases the total; giving "
        "away, losing, selling, eating, borrowing, or removing decreases it. To find how many "
        "remain altogether, apply each change in order. Keywords: how many, total, remaining, left, count."
    )

    passed = 0
    failed = 0
    out = []

    def check(name: str, condition: bool) -> None:
        nonlocal passed, failed
        if condition:
            passed += 1
            out.append(f"PASS  {name}")
        else:
            failed += 1
            out.append(f"FAIL  {name}")

    services = all_service_contracts()
    expected_domains = [
        "fraction_change_capacity",
        "whole_number_arithmetic",
        "linear_equation_one_unknown",
        "multi_step_count_change",
    ]
    check("four capability service contracts derived from installed capability registry", [s.domain_id for s in services] == expected_domains)
    check("GP-005 status carries deterministic service registry hash", status["service_registry_hash"] == service_registry_hash())
    check("all services are Forge-owned", all(s.authority_owner == "forge" for s in services))
    check("all services require Forge-bound requests", all(s.invocation_policy == "forge_pipeline_bound_request_only" for s in services))
    check("all services retain no side effects", all(s.side_effect_policy == "none" for s in services))
    check("all services forbid memory writes", all(not s.memory_write_allowed for s in services))
    check("all services forbid Identity Vault writes", all(not s.identity_write_allowed for s in services))
    check("all services forbid Contribution Economy writes", all(not s.contribution_economy_write_allowed for s in services))
    check("all services forbid CT minting", all(not s.ct_mint_allowed for s in services))
    check("all services forbid direct rendering", all(not s.render_output_allowed for s in services))
    check("all services forbid Echo approval", all(not s.echo_approval_allowed for s in services))

    equation_service = service_contract_for_domain("linear_equation_one_unknown")
    check("equation service contract exists", equation_service is not None)
    check("equation service is bound to equation capability", equation_service is not None and equation_service.capability_id == "cap.math.linear_equation_one_unknown.v1")
    try:
        equation_service.authority_owner = "external"  # type: ignore[misc]
    except (FrozenInstanceError, AttributeError):
        immutable = True
    else:
        immutable = False
    check("service contract is immutable", immutable)

    result = learn_and_answer(algebra_book, "algebra_book", "solve 11x + 17 = 105 for x")
    trace = result.trace
    service_trace = trace.get("capability_service_contract", {})
    request_trace = trace.get("capability_invocation_request", {})
    receipt_trace = trace.get("capability_execution_receipt", {})
    check("supported equation still answers through service boundary", result.status == "ANSWERED" and "8" in (result.answer_text or ""))
    check("answer trace includes service contract", service_trace.get("service_id") == "svc.forge.linear_equation_one_unknown.executor.v1")
    check("answer trace includes invocation request", request_trace.get("operation") == "execute_exact_solution")
    check("invocation attests full-input parse", request_trace.get("parser_attestation") == "full_input_consumed_by_registered_parser")
    check("answer trace includes execution receipt", receipt_trace.get("execution_status") == "VERIFIED_EXECUTION_COMPLETE")
    check("receipt observes verified solution", receipt_trace.get("solution_verified_observed") is True)
    check("receipt observes no side effects", receipt_trace.get("side_effects_observed") == "none")
    check("receipt retains gate authority", receipt_trace.get("gate_authority_retained") is True)
    check("receipt retains renderer authority", receipt_trace.get("renderer_authority_retained") is True)
    check("receipt retains Echo authority", receipt_trace.get("echo_authority_retained") is True)
    check("service contract hash binds request", request_trace.get("service_contract_hash") == trace.get("capability_service_contract_hash"))
    check("request hash binds execution receipt", receipt_trace.get("request_hash") == trace.get("capability_invocation_request_hash"))
    check("answer remains Echo-approved after service execution", trace.get("echo", {}).get("approved_output") is True)

    # Canonical request tamper rejection: code cannot substitute a different
    # capability identity after the parser accepted a question.
    parsed = LinearEquationOneUnknownDomain().parse("solve 11x + 17 = 105 for x")
    request = build_execution_request(parsed)
    tampered = replace(request, capability_id="cap.math.fake.v999")
    try:
        execute_request(tampered, parsed)
    except CapabilityServiceBoundaryError:
        rejected_tamper = True
    else:
        rejected_tamper = False
    check("tampered capability invocation request is rejected", rejected_tamper)

    # Determinism and regressions.
    same = learn_and_answer(algebra_book, "algebra_book", "solve 11x + 17 = 105 for x")
    check("service-mediated result hash deterministic", result.result_hash() == same.result_hash())
    check("execution receipt deterministic", trace.get("capability_execution_receipt_hash") == same.trace.get("capability_execution_receipt_hash"))
    check("GP-001 arithmetic still answers through service boundary", learn_and_answer(math_book, "m", "What is 7 times 12?").status == "ANSWERED")
    check("GP-001 capacity still answers through service boundary", learn_and_answer(math_book, "m", "A storage bin was 11/12 full. After 21 kilograms were removed, it was 2/3 full. What is the full capacity of the storage bin?").status == "ANSWERED")
    check("GP-003 word problem still answers through service boundary", learn_and_answer(wp_book, "wp", "Sam had 12 apples, bought 8 more, then gave away 5. How many apples does he have?").status == "ANSWERED")

    boundary = service_boundary_contract()
    check("boundary records service is not an agent", boundary["service_model"] == "forge_owned_bounded_executor_not_agent")
    check("boundary records no direct domain execution in answering pipeline", boundary["direct_domain_execution_in_pipeline_allowed"] is False)
    check("boundary records no new domain", boundary["adds_new_domain"] is False)
    check("boundary records no corpus ingestion", boundary["adds_corpus_ingestion"] is False)
    check("boundary records GP-005 historical no-dependency origin", boundary["third_party_dependencies_added_during_original_gp005"] == [])
    check("boundary truthfully records activated external equation and capacity backends", boundary["third_party_dependencies_added"] == ["lark==1.3.1", "sympy==1.14.0", "mpmath==1.3.0", "Pint==0.25.3", "flexcache==0.3", "flexparser==0.4", "platformdirs==4.10.0"] and boundary["third_party_parser_imported"] is True and boundary["third_party_solver_imported"] is True)
    check("boundary records no memory write", boundary["writes_memory"] is False)
    check("boundary records no Identity Vault write", boundary["writes_identity_vault"] is False)
    check("boundary records no Contribution Economy write", boundary["writes_contribution_economy"] is False)
    check("boundary records no CT mint", boundary["mints_ct"] is False)

    print("\n".join(out))
    total = passed + failed
    result_status = "PASS" if failed == 0 else "FAIL"
    print(f"\nBUILD_ID: {gp5.GP005_BUILD_ID}")
    print(f"SCHEMA_VERSION: {gp5.GP005_SCHEMA_VERSION}")
    print(f"RESULT: GENERAL-PIPELINE-CAPABILITY-SERVICE-CONTRACTS-BUILD-GP-005_BEHAVIOR {result_status}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
