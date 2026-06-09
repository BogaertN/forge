#!/usr/bin/env python3
"""Behavior tests for GP-002 — one-unknown linear equations.

Run:
    .venv/bin/python scripts/test_general_pipeline_linear_equations_build_gp002.py --forge-root "$HOME/forge"

Exercises the full motion for the new domain end to end, proves GP-001 still
works (regression), proves refusal of unlearned questions, and proves the
governed gate / Echo guards still hold for equations.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", default=None)
    args = parser.parse_args()

    forge_root = Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(forge_root))

    from rmc_engine_v1.general_pipeline import gp002_linear_equations as gp2
    gp2.activate()
    from rmc_engine_v1.general_pipeline import learn_and_answer, answer_question, learn
    from rmc_engine_v1.general_pipeline.echo_approval import validate_and_approve
    from rmc_engine_v1.general_pipeline.contracts import MeaningManifest
    from rmc_engine_v1.mea.manifest_schema import ClaimStatus, OutputPermission

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

    passed = 0
    failed = 0
    out = []

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            out.append(f"PASS  {name}")
        else:
            failed += 1
            out.append(f"FAIL  {name}")

    # --- equation domain, multiple forms ---
    for q, expect in [
        ("solve 3x + 5 = 20 for x", "5"),
        ("2y - 4 = 10", "7"),
        ("x + 7 = 12", "5"),
        ("4x = 28", "7"),
        ("solve 2x + 3 = 8 for x", "5/2"),
        ("5x + 10 = 0", "-2"),
    ]:
        r = learn_and_answer(algebra_book, "algebra_book", q)
        check(f"equation '{q}' -> {expect}", r.status == "ANSWERED" and r.domain == "linear_equation_one_unknown" and expect in (r.answer_text or ""))
        check(f"equation '{q}' has substitution check", "substituting" in (r.answer_text or ""))
        check(f"equation '{q}' verified language", "verified by exact arithmetic" in (r.answer_text or ""))

    # --- clean wording guarantees ---
    r = learn_and_answer(algebra_book, "algebra_book", "2y - 4 = 10")
    check("no double-negative 'subtract -'", "subtract -" not in (r.answer_text or "").lower())
    r2 = learn_and_answer(algebra_book, "algebra_book", "4x = 28")
    check("no spurious '+ 0' in pure-coefficient eq", "+ 0" not in (r2.answer_text or ""))

    # --- regression: GP-001 domains still work ---
    r = learn_and_answer(math_book, "math_book", "What is 7 times 12?")
    check("regression: arithmetic still answers 84", r.status == "ANSWERED" and "84" in (r.answer_text or "") and r.domain == "whole_number_arithmetic")
    r = learn_and_answer(math_book, "math_book", "A storage bin was 11/12 full. After 21 kilograms were removed, it was 2/3 full. What is the full capacity of the storage bin?")
    check("regression: capacity still answers 84 kg", r.status == "ANSWERED" and "84 kilograms" in (r.answer_text or ""))

    # --- honesty: equation question refused if source does not teach equations ---
    r = answer_question("solve 3x + 5 = 20 for x", learn(math_book, "math_book"))
    check("equation refused when source lacks algebra authority", r.status == "REFUSED_UNLEARNED")

    # --- honesty: unlearned domain still refused ---
    r = learn_and_answer(algebra_book, "algebra_book", "What is the area of a circle radius 3?")
    check("unlearned question still refused", r.status == "REFUSED_UNLEARNED")

    # --- governed gate + Echo still active for equations ---
    r = learn_and_answer(algebra_book, "algebra_book", "solve 3x + 5 = 20 for x")
    sealed = r.trace["sealed_manifest"]
    check("equation seals to resolved_manifest", sealed["claim_status"] == ClaimStatus.RESOLVED_MANIFEST.value)
    check("equation seals render_allowed", sealed["output_permissions"] == OutputPermission.RENDER_ALLOWED.value)
    check("equation Echo approved", r.trace["echo"]["echo_status"] == "ECHO_APPROVED_RENDERING_WITHIN_MANIFEST_SCOPE")

    meaning = MeaningManifest(**r.trace["meaning_manifest"])
    bad = validate_and_approve(meaning, "The answer is 999. Nonsense.")
    check("Echo rejects wrong equation rendering", bad.approved_output is False)

    # --- determinism ---
    a = learn_and_answer(algebra_book, "algebra_book", "solve 3x + 5 = 20 for x")
    b = learn_and_answer(algebra_book, "algebra_book", "solve 3x + 5 = 20 for x")
    check("equation pipeline deterministic", a.result_hash() == b.result_hash())

    # --- idempotent activation ---
    check("activate() idempotent", gp2.activate() is False and gp2.is_active() is True)

    print("\n".join(out))
    total = passed + failed
    status = "PASS" if failed == 0 else "FAIL"
    print(f"\nRESULT: {gp2.GP002_BUILD_ID}_BEHAVIOR {status}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
