#!/usr/bin/env python3
"""Behavior tests for GP-003 — multi-step count-change word problems.

Run:
    .venv/bin/python scripts/test_general_pipeline_word_problems_build_gp003.py --forge-root "$HOME/forge"

Covers the full motion for the new domain, a ROUTING DIAGNOSTIC across all four
loaded domains (no collisions), regression for GP-001 and GP-002, refusal of
unlearned questions, and the gate/Echo guards.
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
    from rmc_engine_v1.general_pipeline import gp003_word_problems as gp3
    gp2.activate()
    gp3.activate()
    from rmc_engine_v1.general_pipeline import learn_and_answer, answer_question, learn
    from rmc_engine_v1.general_pipeline.domains import match_domain
    from rmc_engine_v1.general_pipeline.contracts import MeaningManifest
    from rmc_engine_v1.general_pipeline.echo_approval import validate_and_approve
    from rmc_engine_v1.mea.manifest_schema import ClaimStatus, OutputPermission

    wp_book = (
        "Elementary word problems about counting. A word problem describes a starting count "
        "that changes. Buying, finding, receiving, or gaining more increases the total; giving "
        "away, losing, selling, eating, borrowing, or removing decreases it. To find how many "
        "remain altogether, apply each change in order. Keywords: how many, total, remaining, left, count."
    )
    algebra_book = "Elementary algebra equation solve unknown variable both sides isolate."
    math_book = "Elementary arithmetic add subtract multiply divide whole numbers; fraction capacity full removed whole."

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

    # --- word-problem domain ---
    for q, expect in [
        ("Sam had 12 apples, bought 8 more, then gave away 5. How many apples does he have?", "15"),
        ("There were 20 birds. 7 flew away and then 4 more landed. How many birds are there now?", "17"),
        ("A shelf had 30 books. 12 were borrowed, then 6 were returned. How many books are on the shelf?", "24"),
        ("Maria had 50 stickers. She gave away 10, lost 5, then found 3. How many stickers does she have?", "38"),
        ("A jar had 18 candies. 6 were eaten and 9 more were added. How many candies are there?", "21"),
    ]:
        r = learn_and_answer(wp_book, "wp_book", q)
        check(f"word problem -> {expect}", r.status == "ANSWERED" and r.domain == "multi_step_count_change" and expect in (r.answer_text or ""))
        check(f"word problem -> {expect} has check", "which matches the running total" in (r.answer_text or ""))
        check(f"word problem -> {expect} verified language", "verified by exact arithmetic" in (r.answer_text or ""))

    # --- clean rendering: neutral lead, no mangled article ---
    r = learn_and_answer(wp_book, "wp_book", "Sam had 12 apples, bought 8 more, then gave away 5. How many apples does he have?")
    check("word problem clean lead 'The answer is'", (r.answer_text or "").startswith("The answer is"))
    check("word problem no mangled article 'the an'", "the an " not in (r.answer_text or "").lower())

    # --- ROUTING DIAGNOSTIC: all four domains, no collisions ---
    routing = {
        "whole_number_arithmetic": ["What is 7 times 12?", "What is 45 plus 38?", "What is 19 minus 6?"],
        "fraction_change_capacity": ["A storage bin was 11/12 full. After 21 kilograms were removed, it was 2/3 full. What is the full capacity of the storage bin?"],
        "linear_equation_one_unknown": ["solve 3x + 5 = 20 for x", "4x = 28", "2y - 4 = 10"],
        "multi_step_count_change": ["Sam had 12 apples, bought 8 more, then gave away 5. How many apples does he have?"],
    }
    collisions = 0
    for expected, qs in routing.items():
        for q in qs:
            d = match_domain(q)
            got = d.domain_id if d else "NONE"
            if got != expected:
                collisions += 1
    check("routing diagnostic: zero collisions across 4 domains", collisions == 0)

    # --- regression: GP-001 + GP-002 still answer correctly ---
    check("regression arithmetic 84", "84" in (learn_and_answer(math_book, "m", "What is 7 times 12?").answer_text or ""))
    check("regression capacity 84 kg", "84 kilograms" in (learn_and_answer(math_book, "m", "A storage bin was 11/12 full. After 21 kilograms were removed, it was 2/3 full. What is the full capacity of the storage bin?").answer_text or ""))
    check("regression equation x=5", "5" in (learn_and_answer(algebra_book, "a", "solve 3x + 5 = 20 for x").answer_text or ""))

    # --- honesty: word problem refused if source lacks word-problem authority ---
    r = answer_question("Sam had 12 apples, bought 8 more, then gave away 5. How many apples does he have?", learn(algebra_book, "a"))
    check("word problem refused without source authority", r.status == "REFUSED_UNLEARNED")

    # --- honesty: still refuse genuinely unlearned ---
    r = learn_and_answer(wp_book, "wp", "What is the area of a circle radius 3?")
    check("unlearned still refused", r.status == "REFUSED_UNLEARNED")

    # --- gate + Echo on word problem ---
    r = learn_and_answer(wp_book, "wp", "Sam had 12 apples, bought 8 more, then gave away 5. How many apples does he have?")
    sealed = r.trace["sealed_manifest"]
    check("word problem seals resolved", sealed["claim_status"] == ClaimStatus.RESOLVED_MANIFEST.value)
    check("word problem render_allowed", sealed["output_permissions"] == OutputPermission.RENDER_ALLOWED.value)
    check("word problem Echo approved", r.trace["echo"]["echo_status"] == "ECHO_APPROVED_RENDERING_WITHIN_MANIFEST_SCOPE")
    meaning = MeaningManifest(**r.trace["meaning_manifest"])
    bad = validate_and_approve(meaning, "The answer is 999. Nonsense.")
    check("Echo rejects wrong word-problem rendering", bad.approved_output is False)

    # --- determinism + idempotent activation ---
    a = learn_and_answer(wp_book, "wp", "Sam had 12 apples, bought 8 more, then gave away 5. How many apples does he have?")
    b = learn_and_answer(wp_book, "wp", "Sam had 12 apples, bought 8 more, then gave away 5. How many apples does he have?")
    check("word problem deterministic", a.result_hash() == b.result_hash())
    check("activate() idempotent", gp3.activate() is False and gp3.is_active() is True)

    print("\n".join(out))
    total = passed + failed
    status = "PASS" if failed == 0 else "FAIL"
    print(f"\nRESULT: {gp3.GP003_BUILD_ID}_BEHAVIOR {status}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
