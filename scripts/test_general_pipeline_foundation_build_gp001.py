#!/usr/bin/env python3
"""Behavior tests for the General Learning-to-Answer Pipeline (Build GP-001).

Run:
    .venv/bin/python scripts/test_general_pipeline_foundation_build_gp001.py --forge-root "$HOME/forge"

These tests exercise the FULL motion end to end against the real MEA engine:
learn -> manifest -> exact execute -> governed gate -> seal -> render -> Echo.
They also prove the honest boundaries: unlearned questions are refused, a
zero-information result cannot seal, and a tampered rendering is rejected by Echo.
"""

from __future__ import annotations

import argparse
import sys
from fractions import Fraction
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", default=None)
    args = parser.parse_args()

    forge_root = Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(forge_root))

    from rmc_engine_v1.general_pipeline import (
        learn,
        learn_and_answer,
        answer_question,
        GENERAL_PIPELINE_BUILD_ID,
    )
    from rmc_engine_v1.general_pipeline.domains import match_domain
    from rmc_engine_v1.general_pipeline.governed_gate import evaluate_gate
    from rmc_engine_v1.general_pipeline.echo_approval import validate_and_approve
    from rmc_engine_v1.general_pipeline.meaning_and_renderer import compile_meaning
    from rmc_engine_v1.mea.manifest_schema import ClaimStatus, OutputPermission

    book = (
        "Elementary arithmetic teaches how to add, subtract, multiply and divide whole numbers. "
        "Fractions and capacity: when part of a full container is removed, the change in the "
        "fraction full equals the amount removed divided by the whole capacity."
    )

    passed = 0
    failed = 0
    results = []

    def check(name, condition):
        nonlocal passed, failed
        if condition:
            passed += 1
            results.append(f"PASS  {name}")
        else:
            failed += 1
            results.append(f"FAIL  {name}")

    # --- arithmetic domain ---
    for q, expect in [
        ("What is 7 times 12?", "84"),
        ("What is 45 plus 38?", "83"),
        ("What is 100 divided by 4?", "25"),
        ("What is 19 minus 6?", "13"),
        ("What is 6 times 9?", "54"),
    ]:
        r = learn_and_answer(book, "elementary_math_book", q)
        check(f"arithmetic '{q}' -> {expect}", r.status == "ANSWERED" and expect in (r.answer_text or ""))
        check(f"arithmetic '{q}' verified language", "verified by exact arithmetic" in (r.answer_text or ""))

    # --- fraction-change capacity domain ---
    for q, expect in [
        ("A storage bin was 11/12 full. After 21 kilograms were removed, it was 2/3 full. What is the full capacity of the storage bin?", "84"),
        ("A water tank is 3/5 full. After 18 liters are removed, it is 2/5 full. What is the full capacity of the tank?", "90"),
        ("A barrel was 7/8 full. After 20 gallons were removed, it was 3/8 full. What is the full capacity of the barrel?", "40"),
        ("A jar was 5/6 full. After 24 cups were removed, it was 1/3 full. What is the full capacity of the jar?", "48"),
    ]:
        r = learn_and_answer(book, "elementary_math_book", q)
        check(f"capacity '{expect}'", r.status == "ANSWERED" and expect in (r.answer_text or ""))
        check(f"capacity '{expect}' has verification", "difference is" in (r.answer_text or ""))
        check(f"capacity '{expect}' domain", r.domain == "fraction_change_capacity")

    # --- generative proof: different problems produce different sentences ---
    r1 = learn_and_answer(book, "b", "What is 7 times 12?")
    r2 = learn_and_answer(book, "b", "What is 45 plus 38?")
    check("renderings differ across problems", r1.answer_text != r2.answer_text)
    check("rendering not a fixed template (contains its own operands)", "7" in (r1.answer_text or "") and "45" in (r2.answer_text or ""))

    # --- honesty: refuse unlearned domain ---
    r = learn_and_answer(book, "b", "What is the area of a rectangle 4 by 6?")
    check("unlearned question refused", r.status == "REFUSED_UNLEARNED" and r.answer_text is None)

    # --- honesty: source that does not teach a domain grants no authority ---
    empty_source = learn("This text is about poetry and contains no math instruction.", "poetry_book")
    r = answer_question("What is 7 times 12?", empty_source)
    check("question refused when source lacks domain authority", r.status == "REFUSED_UNLEARNED")

    # --- gate: zero information gain cannot seal ---
    src = learn(book, "b")
    dom = match_domain("What is 7 times 12?")
    parsed = dom.parse("What is 7 times 12?")
    from rmc_engine_v1.general_pipeline.manifest_builder import build_problem_manifest
    manifest = build_problem_manifest(parsed, src)
    sol = dom.execute(parsed)
    sol.information_gain = 0  # force recall
    sol.verified = True
    gate = evaluate_gate(manifest, sol, src)
    check("zero information gain blocks seal", gate.passed is False and "zero_information_gain_is_recall_not_discovery" in gate.reasons)

    # --- gate: unverified cannot seal ---
    sol2 = dom.execute(parsed)
    sol2.verified = False
    sol2.information_gain = 1_000_000
    gate2 = evaluate_gate(manifest, sol2, src)
    check("unverified blocks seal", gate2.passed is False)

    # --- Echo: tampered (wrong) rendering is rejected ---
    r = learn_and_answer(book, "b", "What is 7 times 12?")
    meaning_dict = r.trace["meaning_manifest"]
    # rebuild a meaning object and tamper the rendered text
    from rmc_engine_v1.general_pipeline.contracts import MeaningManifest
    meaning = MeaningManifest(**meaning_dict)
    bad = validate_and_approve(meaning, "The answer is 999. Check: nonsense.")
    check("Echo rejects rendering missing the true answer", bad.approved_output is False)
    good = validate_and_approve(meaning, r.answer_text)
    check("Echo approves the faithful rendering", good.approved_output is True and good.echo_status == "ECHO_APPROVED_RENDERING_WITHIN_MANIFEST_SCOPE")

    # --- Echo: empirical overclaim rejected ---
    over = validate_and_approve(meaning, (r.answer_text or "") + " This is empirically confirmed as a law of nature.")
    check("Echo rejects empirical overclaim", over.approved_output is False)

    # --- sealed manifest is a real engine manifest in resolved/render-allowed state ---
    r = learn_and_answer(book, "b", "What is 6 times 9?")
    sealed = r.trace["sealed_manifest"]
    check("sealed claim_status resolved", sealed["claim_status"] == ClaimStatus.RESOLVED_MANIFEST.value)
    check("sealed output render_allowed", sealed["output_permissions"] == OutputPermission.RENDER_ALLOWED.value)
    check("sealed proof_debt zero", float(sealed["proof_debt"]) == 0.0)

    # --- determinism: same input, identical result hash ---
    a = learn_and_answer(book, "b", "What is 7 times 12?")
    b = learn_and_answer(book, "b", "What is 7 times 12?")
    check("pipeline deterministic (result hash stable)", a.result_hash() == b.result_hash())

    print("\n".join(results))
    total = passed + failed
    status = "PASS" if failed == 0 else "FAIL"
    print(f"\nRESULT: {GENERAL_PIPELINE_BUILD_ID}_BEHAVIOR {status}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
