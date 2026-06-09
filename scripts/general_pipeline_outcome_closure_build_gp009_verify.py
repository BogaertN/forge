#!/usr/bin/env python3
"""Static and live boundary verifier for GP-009 — Outcome Closure and Refusal Containment."""

from __future__ import annotations

import argparse
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

    status = gp9.activate()
    gp_dir = forge_root / "rmc_engine_v1" / "general_pipeline"
    scripts_dir = forge_root / "scripts"

    required = [
        gp_dir / "outcome_contract_v2.py",
        gp_dir / "gp009_outcome_closure.py",
        gp_dir / "pipeline.py",
        gp_dir / "__init__.py",
        scripts_dir / "test_general_pipeline_outcome_closure_build_gp009.py",
        scripts_dir / "general_pipeline_outcome_closure_build_gp009_verify.py",
        scripts_dir / "README_general_pipeline_outcome_closure_build_gp009.md",
        scripts_dir / "MEA_GENERAL_PIPELINE_BUILD_GP009_DELIVERY_MANIFEST.json",
    ]

    passed = 0
    failed = 0
    lines = []

    def check(name: str, condition: bool) -> None:
        nonlocal passed, failed
        if condition:
            passed += 1
            lines.append(("PASS  " if condition else "FAIL  ") + name)
        else:
            failed += 1
            lines.append("FAIL  " + name)

    for path in required:
        check(f"required file exists: {path.name}", path.is_file())

    boundary = status["outcome_contract_v2_boundary"]
    check("activation identifies GP-009", status["build_id"] == "GENERAL-PIPELINE-OUTCOME-CLOSURE-REFUSAL-CONTAINMENT-BUILD-GP-009")
    check("activation carries GP-008 prior status", status["gp008_status"]["build_id"] == "GENERAL-PIPELINE-MANIFEST-CONTRACT-V2-BUILD-GP-008")
    check("boundary identifies non-delivery purpose", "non-delivery" in boundary["purpose"])
    check("boundary reuses GP-008 success receipt", boundary["answered_path_receipt"] == "DeliveryAuthorizationReceiptV2_from_GP008")
    check("boundary covers exactly three non-delivery statuses", set(boundary["non_delivery_statuses_covered"]) == {"REFUSED_UNLEARNED", "GATE_BLOCKED", "ECHO_REJECTED"})
    check("boundary has traced refusals", boundary["refusal_has_trace_receipt"] is True)
    check("boundary has traced gate blocks", boundary["blocked_execution_has_containment_receipt"] is True)
    check("boundary has traced Echo rejections", boundary["echo_rejection_has_containment_receipt"] is True)
    check("boundary remains non-persistent", boundary["containment_is_persistent_storage"] is False and boundary["in_memory_only"] is True)
    check("boundary adds no corpus", boundary["corpus_ingestion_added"] is False)
    check("boundary forbids memory", boundary["persistent_memory_write_allowed"] is False)
    check("boundary forbids identity", boundary["identity_vault_write_allowed"] is False)
    check("boundary forbids economy", boundary["contribution_economy_write_allowed"] is False and boundary["ct_mint_allowed"] is False and boundary["ledger_write_allowed"] is False)
    check("boundary adds no domain but truthfully reports authorized dependency transition", boundary["new_domain_added"] is False and boundary["third_party_dependency_promoted"] is True and boundary["runtime_tool_activation_transition"] == "SUPERSEDED_BY_GP010B_R1")

    outcome_text = (gp_dir / "outcome_contract_v2.py").read_text(encoding="utf-8")
    pipeline_text = (gp_dir / "pipeline.py").read_text(encoding="utf-8")
    activation_text = (gp_dir / "gp009_outcome_closure.py").read_text(encoding="utf-8")
    combined_new = outcome_text + activation_text

    check("outcome contract defines typed receipt", "class NonDeliveryOutcomeReceiptV2" in outcome_text)
    check("outcome contract defines strict boundary error", "class OutcomeContractV2BoundaryError" in outcome_text)
    check("outcome contract binds refusal builder", "def build_early_refusal_receipt" in outcome_text)
    check("outcome contract binds gate-block builder", "def build_gate_blocked_receipt" in outcome_text)
    check("outcome contract binds Echo-rejection builder", "def build_echo_rejected_receipt" in outcome_text)
    check("outcome contract forbids text delivery", "NO_HUMAN_TEXT_DELIVERY_GP009" in outcome_text)
    check("outcome contract forbids memory write", "NO_PERSISTENT_MEMORY_WRITE_GP009" in outcome_text)
    check("outcome contract forbids identity write", "NO_IDENTITY_VAULT_WRITE_GP009" in outcome_text)
    check("outcome contract forbids economy action", "NO_CONTRIBUTION_CT_OR_LEDGER_ACTION_GP009" in outcome_text)
    check("pipeline attaches non-delivery receipts", "_non_delivery_trace" in pipeline_text and "non_delivery_outcome_v2" in pipeline_text)
    check("pipeline traces routing refusal", "stage=ROUTING_NO_DOMAIN" in pipeline_text)
    check("pipeline traces missing capability", "stage=CAPABILITY_NOT_INSTALLED" in pipeline_text)
    check("pipeline traces missing source support", "stage=SOURCE_AUTHORITY_NOT_PRESENT" in pipeline_text)
    check("pipeline traces defensive parse failure", "stage=PARSER_REFUSED" in pipeline_text)
    check("pipeline traces blocked gate", "build_gate_blocked_receipt" in pipeline_text)
    check("pipeline traces rejected Echo", "build_echo_rejected_receipt" in pipeline_text)
    check("pipeline keeps GP-008 delivery authorization", "finalize_echo_delivery" in pipeline_text and "delivery_authorization_v2" in pipeline_text)

    forbidden_tokens = [
        "sqlite3.connect",
        "open(",
        "write_text(",
        "write_bytes(",
        "jsonl",
        "identity_vault",
        "contribution_economy",
        "mint_ct",
        "ledger_write",
        "import sympy",
        "import lark",
        "import pint",
        "import z3",
    ]
    # Constants legitimately include negative Identity/Economy boundary names;
    # check executable call-shaped tokens only.
    executable_forbidden = [
        "sqlite3.connect",
        ".write_text(",
        ".write_bytes(",
        "open(",
    ]
    for token in executable_forbidden:
        check(f"new GP-009 runtime has no prohibited executable token {token!r}", token not in combined_new)
    import_lines = {
        line.strip().lower()
        for line in combined_new.splitlines()
        if line.strip().startswith(("import ", "from "))
    }
    for package in ("sympy", "lark", "pint", "z3"):
        promoted = any(
            line == f"import {package}" or line.startswith(f"from {package} ") or line.startswith(f"import {package}.")
            for line in import_lines
        )
        check(f"new GP-009 runtime does not import third-party candidate {package!r}", not promoted)

    math_book = (
        "Elementary arithmetic teaches how to add, subtract, multiply and divide whole numbers. "
        "Fractions and capacity: when part of a full container is removed, the change in the "
        "fraction full equals the amount removed divided by the whole capacity."
    )
    solved = learn_and_answer(math_book, "math_book", "What is 7 times 12?")
    check("live answer remains delivered", solved.status == "ANSWERED" and "84" in (solved.answer_text or ""))
    check("live answer retains GP-008 delivery receipt", "delivery_authorization_v2" in solved.trace)
    check("live answer exposes outcome boundary", "outcome_contract_v2_boundary" in solved.trace)
    check("live answer is not marked non-delivery", "non_delivery_outcome_v2" not in solved.trace)

    refused = learn_and_answer(math_book, "math_book", "What colour is the moon?")
    check("live unsupported input refuses", refused.status == "REFUSED_UNLEARNED" and refused.answer_text is None)
    check("live unsupported refusal has receipt", refused.trace["non_delivery_outcome_v2"]["stage"] == "ROUTING_NO_SUPPORTED_DOMAIN")
    check("live unsupported refusal does not invent manifest contract", "manifest_contract_v2" not in refused.trace)

    poetry = learn("This text is poetry and contains no arithmetic teaching.", "poetry")
    source_refused = answer_question("What is 7 times 12?", poetry)
    check("live missing source support is traced", source_refused.trace["non_delivery_outcome_v2"]["stage"] == "SOURCE_SUPPORT_NOT_PRESENT")
    check("live missing source support executes nothing", source_refused.trace["non_delivery_outcome_v2"]["execution_receipt_hash"] is None)

    original_gate = pipeline_module.evaluate_gate
    pipeline_module.evaluate_gate = lambda _manifest, _solution, _source: GateResult(
        passed=False, reasons=["forced_verifier_gate_block"], vector_micro={}
    )
    try:
        gate = learn_and_answer(math_book, "math_book", "What is 7 times 12?")
    finally:
        pipeline_module.evaluate_gate = original_gate
    check("live gate block has containment receipt", gate.status == "GATE_BLOCKED" and gate.trace["non_delivery_outcome_v2"]["stage"] == "GOVERNED_GATE_BLOCKED")
    check("live gate block cannot claim render contract", "manifest_contract_v2" not in gate.trace)

    original_render = pipeline_module.render_with_manifest_contract_v2
    pipeline_module.render_with_manifest_contract_v2 = lambda _meaning, _contract: (
        "The result is 84. This answer is verified by exact arithmetic and proven scientifically."
    )
    try:
        echo = learn_and_answer(math_book, "math_book", "What is 7 times 12?")
    finally:
        pipeline_module.render_with_manifest_contract_v2 = original_render
    check("live Echo rejection has containment receipt", echo.status == "ECHO_REJECTED" and echo.trace["non_delivery_outcome_v2"]["stage"] == "ECHO_REJECTED_DELIVERY")
    check("live Echo rejection receives no delivery receipt", "delivery_authorization_v2" not in echo.trace)

    print("\n".join(lines))
    total = passed + failed
    outcome = "PASS" if failed == 0 else "FAIL"
    print("\nBUILD_ID: GENERAL-PIPELINE-OUTCOME-CLOSURE-REFUSAL-CONTAINMENT-BUILD-GP-009")
    print("SCHEMA_VERSION: general_pipeline_outcome_closure_refusal_containment_build_gp009")
    print(f"RESULT: GENERAL-PIPELINE-OUTCOME-CLOSURE-REFUSAL-CONTAINMENT-BUILD-GP-009_VERIFY {outcome}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
