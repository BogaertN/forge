#!/usr/bin/env python3
"""Behavior tests for GP-008 — Manifest Contract v2.

Run:
    .venv/bin/python scripts/test_general_pipeline_manifest_contract_v2_build_gp008.py --forge-root "$HOME/forge"

GP-008 adds no domain and writes no state. It requires a separate, hash-bound
RMC trace envelope between sealed MEA state / compiled meaning and delivered
language in the production pipeline.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", default=None)
    args = parser.parse_args()
    forge_root = Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(forge_root))

    from rmc_engine_v1.general_pipeline import learn, learn_and_answer
    from rmc_engine_v1.general_pipeline import gp008_manifest_contract_v2 as gp8
    from rmc_engine_v1.general_pipeline.capability_registry import capability_for_domain
    from rmc_engine_v1.general_pipeline.capability_services import execute_registered_capability
    from rmc_engine_v1.general_pipeline.domains import match_domain
    from rmc_engine_v1.general_pipeline.echo_approval import validate_and_approve_v2, EchoResult
    from rmc_engine_v1.general_pipeline.governed_gate import evaluate_gate, apply_seal, GateResult
    from rmc_engine_v1.general_pipeline.manifest_builder import build_problem_manifest
    from rmc_engine_v1.general_pipeline.meaning_and_renderer import compile_meaning, render_with_manifest_contract_v2
    from rmc_engine_v1.general_pipeline.manifest_contract_v2 import (
        FORMAL_DERIVATION,
        IN_MEMORY_GOVERNED_SOURCE,
        IN_MEMORY_REJECTION_ONLY,
        MANIFEST_CONTRACT_V2_SCHEMA,
        NO_ECONOMIC_ACTION,
        NO_EXTERNAL_PROVENANCE_LINK,
        NO_IDENTITY_WRITE,
        NO_PERSISTENT_MEMORY_WRITE,
        NOT_CORPUS_INGESTED,
        RENDER_AFTER_ECHO,
        ManifestContractV2BoundaryError,
        SourceAncestryReferenceV2,
        build_manifest_contract_v2,
        finalize_echo_delivery,
    )
    from rmc_engine_v1.mea.manifest_schema import canonical_hash as mea_hash

    math_book = (
        "Elementary arithmetic teaches how to add, subtract, multiply and divide whole numbers. "
        "Fractions and capacity: when part of a full container is removed, the change in the "
        "fraction full equals the amount removed divided by the whole capacity."
    )
    algebra_book = (
        "Elementary algebra. To solve an equation, isolate the unknown variable by doing the "
        "same operation to both sides. For a*x + b = c, subtract b from both sides then divide "
        "by a. This finds the variable that makes the equation true."
    )
    wp_book = (
        "Elementary word problems about counting. A word problem describes a starting count "
        "that changes. Buying, finding, receiving, or gaining more increases the total; giving "
        "away, losing, selling, eating, borrowing, or removing decreases it. To find how many "
        "remain altogether, apply each change in order. Keywords: how many, total, remaining, left, count."
    )

    passed = 0
    failed = 0
    lines = []

    def check(name: str, condition: bool) -> None:
        nonlocal passed, failed
        if condition:
            passed += 1
            lines.append(f"PASS  {name}")
        else:
            failed += 1
            lines.append(f"FAIL  {name}")

    activation = gp8.activate()
    boundary = activation["manifest_contract_v2_boundary"]
    check("GP-008 activation exposes build id", activation["build_id"] == gp8.GP008_BUILD_ID)
    check("GP-008 activation exposes schema", activation["schema_version"] == gp8.GP008_SCHEMA_VERSION)
    check("GP-008 boundary keeps MEA separate", "MEA ProblemManifest remains separate" in boundary["layer"])
    check("GP-008 boundary requires source ancestry", boundary["requires_source_ancestry"] is True)
    check("GP-008 boundary requires verification receipt", boundary["requires_verification_receipt"] is True)
    check("GP-008 boundary requires Echo before delivery", boundary["requires_echo_before_delivery"] is True)
    check("GP-008 boundary adds no corpus ingestion", boundary["corpus_ingestion_added"] is False)
    check("GP-008 boundary adds no memory write", boundary["persistent_memory_write_allowed"] is False)
    check("GP-008 boundary adds no Identity Vault write", boundary["identity_vault_write_allowed"] is False)
    check("GP-008 boundary adds no Contribution Economy write", boundary["contribution_economy_write_allowed"] is False)
    check("GP-008 boundary adds no CT mint", boundary["ct_mint_allowed"] is False)
    check("GP-008 boundary adds no ledger write", boundary["ledger_write_allowed"] is False)
    check("GP-008 boundary adds no new domain", boundary["new_domain_added"] is False)
    check("GP-008 boundary truthfully reflects authorized GP-010B-R1 dependency transition", boundary["third_party_dependency_promoted"] is True and boundary["runtime_tool_activation_transition"] == "SUPERSEDED_BY_GP010B_R1")

    arithmetic = learn_and_answer(math_book, "elementary_math_book", "What is 7 times 12?")
    check("arithmetic remains answered", arithmetic.status == "ANSWERED" and "84" in arithmetic.answer_text)
    check("arithmetic trace now contains v2 contract", "manifest_contract_v2" in arithmetic.trace)
    a_contract = arithmetic.trace["manifest_contract_v2"]
    check("v2 contract schema is explicit", a_contract["schema_version"] == MANIFEST_CONTRACT_V2_SCHEMA)
    check("v2 claim type formal derivation", a_contract["claim_type"] == FORMAL_DERIVATION)
    check("v2 claim status bound to sealed manifest", a_contract["claim_status"] == arithmetic.trace["sealed_manifest"]["claim_status"])
    check("v2 meaning hash bound", a_contract["meaning_manifest_hash"] == arithmetic.trace["meaning_hash"])
    check("v2 execution receipt hash bound", a_contract["execution_receipt_hash"] == arithmetic.trace["capability_execution_receipt_hash"])
    check("v2 invocation request hash bound", a_contract["invocation_request_hash"] == arithmetic.trace["capability_invocation_request_hash"])
    check("v2 capability hash bound", a_contract["capability_contract_hash"] == arithmetic.trace["capability_contract_hash"])
    check("v2 service hash bound", a_contract["service_contract_hash"] == arithmetic.trace["capability_service_contract_hash"])
    check("v2 open MEA hash bound", a_contract["open_mea_manifest_hash"] == arithmetic.trace["open_manifest_hash"])
    check("v2 sealed MEA hash bound", a_contract["sealed_mea_manifest_hash"] == arithmetic.trace["sealed_manifest_hash"])
    check("v2 verification reports gate passage", a_contract["verification_receipt"]["gate_passed"] is True)
    check("v2 verification reports exact result", a_contract["verification_receipt"]["solution_verified"] is True)
    check("v2 authority basis complete", len(a_contract["authority_basis"]) == 6 and "rmc:meaning_bound_before_render" in a_contract["authority_basis"])
    check("v2 source ancestry exists", len(a_contract["source_ancestry"]) == 1)
    source_ref = a_contract["source_ancestry"][0]
    check("v2 source is in-memory support not corpus", source_ref["authority_class"] == IN_MEMORY_GOVERNED_SOURCE and source_ref["corpus_state"] == NOT_CORPUS_INGESTED)
    check("v2 source has no external provenance link", source_ref["external_provenance_state"] == NO_EXTERNAL_PROVENANCE_LINK)
    check("v2 output permission Echo-gated", a_contract["render_permissions"] == [RENDER_AFTER_ECHO] and a_contract["delivery_requires_echo"] is True)
    check("v2 persistent memory remains forbidden", a_contract["memory_permission"] == NO_PERSISTENT_MEMORY_WRITE)
    check("v2 identity write remains forbidden", a_contract["identity_permission"] == NO_IDENTITY_WRITE)
    check("v2 economic write remains forbidden", a_contract["economic_permission"] == NO_ECONOMIC_ACTION and a_contract["contribution_event_refs"] == [])
    check("v2 containment remains in memory", a_contract["containment_destination"] == IN_MEMORY_REJECTION_ONLY)
    check("Echo records v2 validation", arithmetic.trace["echo"]["checks"]["manifest_contract_v2_valid"] is True)
    check("delivery authorization exists after Echo", "delivery_authorization_v2" in arithmetic.trace)
    delivery = arithmetic.trace["delivery_authorization_v2"]
    check("delivery authorization binds contract hash", delivery["manifest_contract_v2_hash"] == arithmetic.trace["manifest_contract_v2_hash"])
    check("delivery authorization binds Echo hash", delivery["echo_receipt_hash"] == arithmetic.trace["echo_hash"])
    check("delivery authorization side-effect free", delivery["side_effects_observed"] == "none")

    equation = learn_and_answer(algebra_book, "algebra_book", "solve 11x + 17 = 105 for x")
    check("equation remains answered", equation.status == "ANSWERED" and "8" in equation.answer_text)
    e_contract = equation.trace["manifest_contract_v2"]
    check("equation v2 binds typed AST", e_contract["typed_ast_hash"] == equation.trace["typed_ast_hash"] and e_contract["typed_ast_hash"] is not None)
    check("equation v2 binds safe-adapter receipt", e_contract["safe_solver_adapter_receipt_hash"] == equation.trace["safe_solver_adapter_receipt_hash"])

    word_problem = learn_and_answer(wp_book, "word_problem_book", "Sam had 12 apples, bought 8 more, and gave away 5. How many apples does Sam have now?")
    check("word problem remains answered", word_problem.status == "ANSWERED" and "15" in word_problem.answer_text)
    check("non-migrated word problem has v2 contract", "manifest_contract_v2" in word_problem.trace)
    check("non-adapter path honestly has no AST link", word_problem.trace["manifest_contract_v2"]["typed_ast_hash"] is None and word_problem.trace["manifest_contract_v2"]["safe_solver_adapter_receipt_hash"] is None)

    repeated = learn_and_answer(algebra_book, "algebra_book", "solve 11x + 17 = 105 for x")
    check("v2 pipeline output deterministic", equation.result_hash() == repeated.result_hash())
    unlearned = learn_and_answer(math_book, "elementary_math_book", "What is the area of a rectangle 4 by 6?")
    check("unlearned refusal does not invent v2 authority", unlearned.status == "REFUSED_UNLEARNED" and "manifest_contract_v2" not in unlearned.trace)

    # Create real component objects to exercise tamper and blocked-construction paths.
    src = learn(algebra_book, "algebra_book")
    domain = match_domain("solve 11x + 17 = 105 for x")
    parsed = domain.parse("solve 11x + 17 = 105 for x")
    open_manifest = build_problem_manifest(parsed, src)
    capability = capability_for_domain(parsed.domain)
    service, invocation, solution, exec_receipt = execute_registered_capability(parsed)
    gate = evaluate_gate(open_manifest, solution, src)
    sealed = apply_seal(open_manifest, solution)
    meaning = compile_meaning(sealed, parsed, solution, src.procedure_for_domain(parsed.domain).source_ref)
    contract = build_manifest_contract_v2(
        source=src, parsed=parsed, solution=solution, capability=capability, service=service,
        invocation=invocation, execution_receipt=exec_receipt, gate=gate,
        open_mea_manifest_hash=mea_hash(open_manifest), sealed_mea_manifest=sealed,
        sealed_mea_manifest_hash=mea_hash(sealed), meaning=meaning,
    )
    check("direct v2 builder returns stable contract", contract.contract_hash() == contract.contract_hash())
    check("direct v2 renderer accepts complete contract", "8" in render_with_manifest_contract_v2(meaning, contract))

    try:
        render_with_manifest_contract_v2(meaning, replace(contract, meaning_manifest_hash="tampered"))
    except ManifestContractV2BoundaryError:
        wrong_meaning_blocked = True
    else:
        wrong_meaning_blocked = False
    check("renderer blocks tampered meaning binding", wrong_meaning_blocked)

    for name, change in [
        ("claim type", {"claim_type": "empirical_claim"}),
        ("memory permission", {"memory_permission": "WRITE_ALLOWED"}),
        ("identity permission", {"identity_permission": "IDENTITY_WRITE_ALLOWED"}),
        ("economic permission", {"economic_permission": "CT_MINT_ALLOWED"}),
        ("contribution event", {"contribution_event_refs": ("ce_fake",)}),
        ("containment destination", {"containment_destination": "PERSISTENT_GHOST_LOOP"}),
    ]:
        try:
            replace(contract, **change)
        except ManifestContractV2BoundaryError:
            rejected = True
        else:
            rejected = False
        check(f"v2 rejects widened {name}", rejected)

    try:
        SourceAncestryReferenceV2(
            source_id="s", source_hash="h", raw_text_hash="r", procedure_id="p",
            source_ref="source", domain_id="linear_equation_one_unknown",
            corpus_state="APPROVED_CORPUS",
        )
    except ManifestContractV2BoundaryError:
        corpus_claim_blocked = True
    else:
        corpus_claim_blocked = False
    check("v2 refuses false corpus-ingestion claim", corpus_claim_blocked)

    rejected_echo = validate_and_approve_v2(meaning, "The answer is 999. Check: false.", contract)
    check("v2 Echo still rejects incorrect rendering", rejected_echo.approved_output is False)
    try:
        finalize_echo_delivery(contract, meaning, rejected_echo)
    except ManifestContractV2BoundaryError:
        delivery_blocked = True
    else:
        delivery_blocked = False
    check("delivery cannot authorize Echo-rejected output", delivery_blocked)

    blocked_gate = GateResult(passed=False, reasons=["forced_test_block"], vector_micro={})
    try:
        build_manifest_contract_v2(
            source=src, parsed=parsed, solution=solution, capability=capability, service=service,
            invocation=invocation, execution_receipt=exec_receipt, gate=blocked_gate,
            open_mea_manifest_hash=mea_hash(open_manifest), sealed_mea_manifest=sealed,
            sealed_mea_manifest_hash=mea_hash(sealed), meaning=meaning,
        )
    except ManifestContractV2BoundaryError:
        failed_gate_blocked = True
    else:
        failed_gate_blocked = False
    check("v2 cannot form after failed governed gate", failed_gate_blocked)

    print("\n".join(lines))
    total = passed + failed
    status = "PASS" if failed == 0 else "FAIL"
    print("\nBUILD_ID: GENERAL-PIPELINE-MANIFEST-CONTRACT-V2-BUILD-GP-008")
    print("SCHEMA_VERSION: general_pipeline_manifest_contract_v2_build_gp008")
    print(f"RESULT: GENERAL-PIPELINE-MANIFEST-CONTRACT-V2-BUILD-GP-008_BEHAVIOR {status}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
