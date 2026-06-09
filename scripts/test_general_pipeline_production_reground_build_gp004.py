#!/usr/bin/env python3
"""Behavior tests for GP-004 — strict parse boundary and capability registry.

Run:
    .venv/bin/python scripts/test_general_pipeline_production_reground_build_gp004.py --forge-root "$HOME/forge"

This test adds no state and no dependencies. It proves that the existing four
domains run under one deterministic registry, that unsupported input cannot be
partially interpreted as a smaller valid problem, that activation order no
longer alters registered authority, and that source text cannot install a
solver capability.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def run_isolated(forge_root: Path, body: str) -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(forge_root)
    proc = subprocess.run(
        [sys.executable, "-c", body],
        cwd=str(forge_root),
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"isolated check failed: {proc.stderr}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", default=None)
    args = parser.parse_args()
    forge_root = Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(forge_root))

    from rmc_engine_v1.general_pipeline import gp004_production_reground as gp4
    from rmc_engine_v1.general_pipeline import learn, answer_question, learn_and_answer
    from rmc_engine_v1.general_pipeline.capability_registry import (
        CapabilityContract,
        CapabilityRegistrationError,
        all_capability_contracts,
        boundary_contract,
        registry_hash,
    )
    from rmc_engine_v1.general_pipeline.domains import WholeNumberArithmeticDomain

    status = gp4.activate()

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

    expected_domains = [
        "fraction_change_capacity",
        "whole_number_arithmetic",
        "linear_equation_one_unknown",
        "multi_step_count_change",
    ]
    contracts = all_capability_contracts()
    check("central registry contains four existing domains", [c.domain_id for c in contracts] == expected_domains)
    check("all capability contracts require full input parsing", all(c.parser_policy == "full_input_required" for c in contracts))
    check("all capability contracts forbid memory writes", all(not c.memory_write_allowed for c in contracts))
    check("all capability contracts forbid Identity Vault writes", all(not c.identity_write_allowed for c in contracts))
    check("all capability contracts forbid CT minting", all(not c.ct_mint_allowed for c in contracts))
    check("all capability contracts forbid direct final output", all(not c.final_output_allowed for c in contracts))
    check("boundary reports no new language domain", boundary_contract()["adds_new_language_domain"] is False)
    check("boundary reports no corpus ingestion", boundary_contract()["adds_corpus_ingestion"] is False)
    check("boundary reports no third-party dependency", boundary_contract()["third_party_dependencies_added"] == [])

    # Positive unseen equation proof under the registered capability.
    solved = learn_and_answer(algebra_book, "algebra_book", "solve 11x + 17 = 105 for x")
    check("unseen supported equation solves to 8", solved.status == "ANSWERED" and "8" in (solved.answer_text or ""))
    check("unseen supported equation retains substitution check", "substituting" in (solved.answer_text or ""))
    check("answer trace contains registered capability contract", solved.trace.get("capability_contract", {}).get("capability_id") == "cap.math.linear_equation_one_unknown.v1")
    check("answer trace records full-input parser policy", solved.trace.get("parse_coverage") == "full_input_required")
    check("open manifest authorizes only bounded capability", solved.trace["open_manifest"]["allowed_tools"] == ["cap.math.linear_equation_one_unknown.v1"])
    check("answer has verified meaning then Echo approval", "meaning_manifest" in solved.trace and solved.trace["echo"]["approved_output"] is True)

    # Regression through the new registry.
    check("GP-001 arithmetic still works through registry", learn_and_answer(math_book, "m", "What is 7 times 12?").status == "ANSWERED")
    check("GP-001 capacity still works through registry", learn_and_answer(math_book, "m", "A storage bin was 11/12 full. After 21 kilograms were removed, it was 2/3 full. What is the full capacity of the storage bin?").status == "ANSWERED")
    check("GP-003 word problem still works through registry", learn_and_answer(wp_book, "wp", "Sam had 12 apples, bought 8 more, then gave away 5. How many apples does he have?").status == "ANSWERED")

    # Strict refusal boundary: previously vulnerable or unsupported forms.
    for bad_question in [
        "x + y = 10",
        "solve x + y = 10 for x",
        "2(x + 3) = 14",
        "x^2 = 9",
        "solve 3x + 5 = 20 for y",
        "solve 3x + 5 = 20 plus nonsense for x",
    ]:
        result = learn_and_answer(algebra_book, "algebra_book", bad_question)
        check(f"unsupported equation refused: {bad_question}", result.status == "REFUSED_UNLEARNED" and result.answer_text is None)

    strict_arithmetic = learn_and_answer(math_book, "m", "The bonus is 9. What is 7 times 12?")
    check("arithmetic refuses ignored leading content", strict_arithmetic.status == "REFUSED_UNLEARNED")

    strict_capacity = learn_and_answer(
        math_book, "m",
        "A storage bin was 11/12 full. After 21 kilograms were removed, it was 2/3 full. "
        "What is the full capacity of the storage bin? Then add 10."
    )
    check("capacity refuses ignored trailing instruction", strict_capacity.status == "REFUSED_UNLEARNED")

    strict_word = learn_and_answer(
        wp_book, "wp",
        "Sam had 12 apples, bought 8 more, then hid 4, then gave away 5. How many apples does he have?"
    )
    check("word problem refuses unparsed numeric event", strict_word.status == "REFUSED_UNLEARNED")

    # No source can install a solver: in a fresh process, equation source has no
    # equation authority before installed code activates GP-002.
    no_activation = run_isolated(
        forge_root,
        """
import json
from rmc_engine_v1.general_pipeline import learn
from rmc_engine_v1.general_pipeline.capability_registry import registry_snapshot
src = learn("Elementary algebra equation solve unknown variable both sides isolate.", "a")
print(json.dumps({"domains": [c["domain_id"] for c in registry_snapshot()["capabilities"]], "has_equation_procedure": src.supports_domain("linear_equation_one_unknown")}, sort_keys=True))
""",
    )
    check("source cannot install equation capability", "linear_equation_one_unknown" not in no_activation["domains"])
    check("source cannot compile uninstalled equation procedure", no_activation["has_equation_procedure"] is False)

    # Activation-order determinism in clean processes.
    order_a = run_isolated(
        forge_root,
        """
import json
from rmc_engine_v1.general_pipeline import gp002_linear_equations as gp2, gp003_word_problems as gp3, learn
from rmc_engine_v1.general_pipeline.capability_registry import registry_hash, registry_snapshot
gp2.activate(); gp3.activate()
src = learn("equation solve unknown variable both sides isolate. word problem how many total count remaining.", "combo")
print(json.dumps({"hash": registry_hash(), "domains": [c["domain_id"] for c in registry_snapshot()["capabilities"]], "procedures": [p.domain for p in src.procedures]}, sort_keys=True))
""",
    )
    order_b = run_isolated(
        forge_root,
        """
import json
from rmc_engine_v1.general_pipeline import gp002_linear_equations as gp2, gp003_word_problems as gp3, learn
from rmc_engine_v1.general_pipeline.capability_registry import registry_hash, registry_snapshot
gp3.activate(); gp2.activate()
src = learn("equation solve unknown variable both sides isolate. word problem how many total count remaining.", "combo")
print(json.dumps({"hash": registry_hash(), "domains": [c["domain_id"] for c in registry_snapshot()["capabilities"]], "procedures": [p.domain for p in src.procedures]}, sort_keys=True))
""",
    )
    check("activation order produces identical registry hash", order_a["hash"] == order_b["hash"])
    check("activation order produces identical domain order", order_a["domains"] == order_b["domains"] == expected_domains)
    check("activation order produces identical source procedures", order_a["procedures"] == order_b["procedures"])

    first_hash = registry_hash()
    gp4.activate()
    check("repeated GP-004 activation is deterministic", registry_hash() == first_hash)

    # Conflicting replacement is rejected: code cannot replace domain ownership.
    conflict_rejected = False
    try:
        from rmc_engine_v1.general_pipeline.capability_registry import register_capability
        register_capability(
            CapabilityContract(
                capability_id="cap.invalid.replacement.v1",
                domain_id="whole_number_arithmetic",
                domain_factory=WholeNumberArithmeticDomain,
                relation_text="invalid replacement",
                source_fingerprints=("invalid",),
                min_fingerprint_hits=1,
            )
        )
    except CapabilityRegistrationError:
        conflict_rejected = True
    check("registry rejects competing capability for an existing domain", conflict_rejected)

    print("\n".join(out))
    total = passed + failed
    result_status = "PASS" if failed == 0 else "FAIL"
    print(f"\nBUILD_ID: {status['build_id']}")
    print(f"SCHEMA_VERSION: {status['schema_version']}")
    print(f"RESULT: GENERAL-PIPELINE-PRODUCTION-REGROUND-BUILD-GP-004_BEHAVIOR {result_status}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
