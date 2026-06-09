#!/usr/bin/env python3
"""Behavior tests for GP-009 — Outcome Closure and Refusal Containment.

Run:
    .venv/bin/python scripts/test_general_pipeline_outcome_closure_build_gp009.py --forge-root "$HOME/forge"

GP-009 adds no domain and writes no state. It completes the existing-domain
migration by giving every modeled non-delivery path a typed, hash-bound,
in-memory containment receipt. Successful answers continue to use GP-008
DeliveryAuthorizationReceiptV2.
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

    from rmc_engine_v1.general_pipeline import learn, learn_and_answer, answer_question
    from rmc_engine_v1.general_pipeline import gp009_outcome_closure as gp9
    import rmc_engine_v1.general_pipeline.pipeline as pipeline_module
    from rmc_engine_v1.general_pipeline.governed_gate import GateResult
    from rmc_engine_v1.general_pipeline.outcome_contract_v2 import (
        NonDeliveryOutcomeReceiptV2,
        OutcomeContractV2BoundaryError,
        ROUTING_NO_DOMAIN,
        CAPABILITY_NOT_INSTALLED,
        SOURCE_AUTHORITY_NOT_PRESENT,
        PARSER_REFUSED,
        GOVERNED_GATE_BLOCKED,
        ECHO_REJECTED_DELIVERY,
        NO_HUMAN_TEXT_DELIVERY,
        IN_MEMORY_NON_DELIVERY_TRACE_ONLY,
        NO_PERSISTENT_MEMORY_WRITE,
        NO_IDENTITY_WRITE,
        NO_ECONOMIC_ACTION,
    )

    status = gp9.activate()

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
    word_book = (
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

    boundary = status["outcome_contract_v2_boundary"]
    check("GP-009 status exposes build id", status["build_id"] == "GENERAL-PIPELINE-OUTCOME-CLOSURE-REFUSAL-CONTAINMENT-BUILD-GP-009")
    check("boundary covers refusal", "REFUSED_UNLEARNED" in boundary["non_delivery_statuses_covered"])
    check("boundary covers gate block", "GATE_BLOCKED" in boundary["non_delivery_statuses_covered"])
    check("boundary covers Echo rejection", "ECHO_REJECTED" in boundary["non_delivery_statuses_covered"])
    check("boundary is in-memory only", boundary["in_memory_only"] is True)
    check("boundary forbids persistent memory", boundary["persistent_memory_write_allowed"] is False)
    check("boundary forbids Identity Vault writes", boundary["identity_vault_write_allowed"] is False)
    check("boundary forbids economy writes", boundary["contribution_economy_write_allowed"] is False)
    check("boundary adds no domain", boundary["new_domain_added"] is False)
    check("boundary truthfully reflects authorized executed-path dependencies", boundary["third_party_dependency_promoted"] is True and boundary["early_refusal_claims_no_executed_dependency"] is True)

    # Successful paths already migrated by GP-008 must remain delivery-authorized,
    # without inventing a non-delivery receipt.
    successful = [
        learn_and_answer(math_book, "math_book", "What is 7 times 12?"),
        learn_and_answer(math_book, "math_book", "A storage bin was 11/12 full. After 21 kilograms were removed, it was 2/3 full. What is the full capacity of the storage bin?"),
        learn_and_answer(algebra_book, "algebra_book", "solve 11x + 17 = 105 for x"),
        learn_and_answer(word_book, "word_book", "Sam had 12 apples, bought 8 more, then gave away 5. How many apples does he have?"),
    ]
    for idx, result in enumerate(successful, 1):
        check(f"successful domain {idx} answers", result.status == "ANSWERED" and bool(result.answer_text))
        check(f"successful domain {idx} retains GP-008 delivery receipt", "delivery_authorization_v2" in result.trace)
        check(f"successful domain {idx} exposes GP-009 outcome boundary", "outcome_contract_v2_boundary" in result.trace)
        check(f"successful domain {idx} has no containment receipt", "non_delivery_outcome_v2" not in result.trace)

    # Routing refusal: unsupported question must be traced, not a blank branch.
    unsupported = learn_and_answer(math_book, "math_book", "What colour is the moon?")
    u = unsupported.trace["non_delivery_outcome_v2"]
    check("unsupported question refused", unsupported.status == "REFUSED_UNLEARNED" and unsupported.answer_text is None)
    check("unsupported refusal receipt exists", u["stage"] == ROUTING_NO_DOMAIN)
    check("unsupported refusal forbids delivery", u["output_delivery_permission"] == NO_HUMAN_TEXT_DELIVERY)
    check("unsupported refusal has no invented capability", u["capability_contract_hash"] is None and u["execution_receipt_hash"] is None)
    check("unsupported refusal hash is deterministic", unsupported.result_hash() == learn_and_answer(math_book, "math_book", "What colour is the moon?").result_hash())

    # Full-input unsupported algebra remains refusal-contained.
    multivar = learn_and_answer(algebra_book, "algebra_book", "x + y = 10")
    check("unsupported multivariable equation refuses", multivar.status == "REFUSED_UNLEARNED")
    check("unsupported multivariable refusal is traced", multivar.trace["non_delivery_outcome_v2"]["stage"] == ROUTING_NO_DOMAIN)

    # Installed domain but source lacks authority: bind capability but no execution.
    poetry = learn("This text is poetry, not mathematical instruction.", "poetry")
    source_blocked = answer_question("What is 7 times 12?", poetry)
    s = source_blocked.trace["non_delivery_outcome_v2"]
    check("source-authority refusal status", source_blocked.status == "REFUSED_UNLEARNED")
    check("source-authority refusal stage", s["stage"] == SOURCE_AUTHORITY_NOT_PRESENT)
    check("source-authority refusal binds installed capability", s["capability_contract_hash"] is not None)
    check("source-authority refusal does not execute", s["execution_receipt_hash"] is None and s["open_mea_manifest_hash"] is None)

    # Defensive missing-capability path: matched parser cannot acquire execution authority.
    original_capability_lookup = pipeline_module.capability_for_domain
    pipeline_module.capability_for_domain = lambda _domain_id: None
    try:
        no_capability = learn_and_answer(math_book, "math_book", "What is 7 times 12?")
    finally:
        pipeline_module.capability_for_domain = original_capability_lookup
    nc = no_capability.trace["non_delivery_outcome_v2"]
    check("missing capability refuses", no_capability.status == "REFUSED_UNLEARNED")
    check("missing capability stage", nc["stage"] == CAPABILITY_NOT_INSTALLED)
    check("missing capability does not invent contract", nc["capability_contract_hash"] is None)

    # Defensive parse-failure path: a selected registered domain still cannot
    # execute if it fails full parsing.
    original_match = pipeline_module.match_domain
    class BrokenParser:
        domain_id = "whole_number_arithmetic"
        def parse(self, _question):
            return None
    pipeline_module.match_domain = lambda _question: BrokenParser()
    try:
        parse_refused = learn_and_answer(math_book, "math_book", "What is 7 times 12?")
    finally:
        pipeline_module.match_domain = original_match
    pr = parse_refused.trace["non_delivery_outcome_v2"]
    check("parse failure refuses", parse_refused.status == "REFUSED_UNLEARNED")
    check("parse failure stage", pr["stage"] == PARSER_REFUSED)
    check("parse failure binds installed capability", pr["capability_contract_hash"] is not None)
    check("parse failure does not execute", pr["execution_receipt_hash"] is None)

    # Governed gate block: computation exists, but no render authority may form.
    original_gate = pipeline_module.evaluate_gate
    pipeline_module.evaluate_gate = lambda _manifest, _solution, _source: GateResult(
        passed=False, reasons=["forced_gp009_gate_block"], vector_micro={}
    )
    try:
        gate_blocked = learn_and_answer(math_book, "math_book", "What is 7 times 12?")
    finally:
        pipeline_module.evaluate_gate = original_gate
    gb = gate_blocked.trace["non_delivery_outcome_v2"]
    check("forced gate path blocked", gate_blocked.status == "GATE_BLOCKED" and gate_blocked.answer_text is None)
    check("gate block receipt stage", gb["stage"] == GOVERNED_GATE_BLOCKED)
    check("gate block binds execution receipt", gb["execution_receipt_hash"] == gate_blocked.trace["capability_execution_receipt_hash"])
    check("gate block binds open MEA state", gb["open_mea_manifest_hash"] == gate_blocked.trace["open_manifest_hash"])
    check("gate block has no render contract", gb["manifest_contract_v2_hash"] is None and "manifest_contract_v2" not in gate_blocked.trace)

    # Echo rejection: a complete render-authority contract exists, but delivery
    # is explicitly contained and cannot receive delivery authorization.
    original_render = pipeline_module.render_with_manifest_contract_v2
    pipeline_module.render_with_manifest_contract_v2 = lambda _meaning, _contract: (
        "The result is 84. This answer is verified by exact arithmetic and proven scientifically."
    )
    try:
        echo_rejected = learn_and_answer(math_book, "math_book", "What is 7 times 12?")
    finally:
        pipeline_module.render_with_manifest_contract_v2 = original_render
    er = echo_rejected.trace["non_delivery_outcome_v2"]
    check("Echo rejection blocks answer", echo_rejected.status == "ECHO_REJECTED" and echo_rejected.answer_text is None)
    check("Echo rejection receipt stage", er["stage"] == ECHO_REJECTED_DELIVERY)
    check("Echo rejection binds render contract", er["manifest_contract_v2_hash"] == echo_rejected.trace["manifest_contract_v2_hash"])
    check("Echo rejection binds Echo receipt", er["echo_receipt_hash"] == echo_rejected.trace["echo_hash"])
    check("Echo rejection has no delivery authorization", "delivery_authorization_v2" not in echo_rejected.trace)

    # Every non-delivery receipt has the strict prohibited side-effect boundary.
    for label, result in [
        ("routing", unsupported),
        ("source", source_blocked),
        ("capability", no_capability),
        ("parse", parse_refused),
        ("gate", gate_blocked),
        ("echo", echo_rejected),
    ]:
        rec = result.trace["non_delivery_outcome_v2"]
        check(f"{label} containment is in-memory", rec["containment_destination"] == IN_MEMORY_NON_DELIVERY_TRACE_ONLY)
        check(f"{label} containment forbids memory write", rec["memory_permission"] == NO_PERSISTENT_MEMORY_WRITE)
        check(f"{label} containment forbids identity write", rec["identity_permission"] == NO_IDENTITY_WRITE)
        check(f"{label} containment forbids economic action", rec["economic_permission"] == NO_ECONOMIC_ACTION)
        check(f"{label} containment contributes no event refs", rec["contribution_event_refs"] == [])

    # Direct tamper-pressure on the receipt schema.
    valid = NonDeliveryOutcomeReceiptV2(**u)
    check("receipt round-trips through typed schema", valid.receipt_hash() == unsupported.trace["non_delivery_outcome_v2_hash"])

    tamper_changes = [
        ("delivery permission", {"output_delivery_permission": "HUMAN_TEXT_ALLOWED"}),
        ("persistent memory", {"memory_permission": "WRITE_ALLOWED"}),
        ("identity permission", {"identity_permission": "IDENTITY_WRITE_ALLOWED"}),
        ("economy permission", {"economic_permission": "CT_ALLOWED"}),
        ("fabricated execution evidence", {"execution_receipt_hash": "0" * 64}),
    ]
    for name, changes in tamper_changes:
        try:
            replace(valid, **changes)
        except OutcomeContractV2BoundaryError:
            rejected = True
        else:
            rejected = False
        check(f"receipt rejects tampered {name}", rejected)

    print("\n".join(lines))
    total = passed + failed
    outcome = "PASS" if failed == 0 else "FAIL"
    print("\nBUILD_ID: GENERAL-PIPELINE-OUTCOME-CLOSURE-REFUSAL-CONTAINMENT-BUILD-GP-009")
    print("SCHEMA_VERSION: general_pipeline_outcome_closure_refusal_containment_build_gp009")
    print(f"RESULT: GENERAL-PIPELINE-OUTCOME-CLOSURE-REFUSAL-CONTAINMENT-BUILD-GP-009_BEHAVIOR {outcome}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
