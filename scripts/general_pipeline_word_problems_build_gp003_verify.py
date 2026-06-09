#!/usr/bin/env python3
"""Installed-state verifier for GP-003 — multi-step count-change word problems.

Run:
    .venv/bin/python scripts/general_pipeline_word_problems_build_gp003_verify.py --forge-root "$HOME/forge"

Confirms the new modules are present, activate cleanly with GP-002 against the
live engine, answer a word problem end to end, route with no collisions across
all loaded domains, preserve GP-001/GP-002 behavior, keep the honesty boundary,
and introduce no route/UI/memory-write/file-IO.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXPECTED_MODULES = [
    "rmc_engine_v1/general_pipeline/domains_wordproblems.py",
    "rmc_engine_v1/general_pipeline/gp003_word_problems.py",
]

PRIOR_FILES = [
    "rmc_engine_v1/general_pipeline/__init__.py",
    "rmc_engine_v1/general_pipeline/contracts.py",
    "rmc_engine_v1/general_pipeline/domains.py",
    "rmc_engine_v1/general_pipeline/source_compiler.py",
    "rmc_engine_v1/general_pipeline/manifest_builder.py",
    "rmc_engine_v1/general_pipeline/governed_gate.py",
    "rmc_engine_v1/general_pipeline/meaning_and_renderer.py",
    "rmc_engine_v1/general_pipeline/echo_approval.py",
    "rmc_engine_v1/general_pipeline/pipeline.py",
    "rmc_engine_v1/general_pipeline/domains_equations.py",
    "rmc_engine_v1/general_pipeline/gp002_linear_equations.py",
]

FORBIDDEN_TOKENS = [
    "@app.route", "import flask", "from flask", "import chromadb", "chromadb.",
    ".add_documents(", "requests.post", "requests.get", "open(",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", default=None)
    args = parser.parse_args()

    forge_root = Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(forge_root))

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

    for rel in EXPECTED_MODULES:
        check(f"module present: {rel}", (forge_root / rel).is_file())
    for rel in PRIOR_FILES:
        check(f"prior file present: {rel}", (forge_root / rel).is_file())

    try:
        from rmc_engine_v1.general_pipeline import gp002_linear_equations as gp2
        from rmc_engine_v1.general_pipeline import gp003_word_problems as gp3
        gp2.activate()
        gp3.activate()
        from rmc_engine_v1.general_pipeline import learn_and_answer
        from rmc_engine_v1.general_pipeline.domains import match_domain, all_domains
        from rmc_engine_v1.mea.manifest_schema import ProblemManifest  # real engine
        check("imports + activate (gp2+gp3) against real engine", True)
    except Exception as exc:  # pragma: no cover
        check(f"imports + activate against real engine ({exc})", False)
        print("\n".join(out))
        print(f"\nRESULT: GENERAL-PIPELINE-MULTISTEP-WORDPROBLEMS-BUILD-GP-003_VERIFY FAIL  Total:{passed+failed} Passed:{passed} Failed:{failed}")
        return 1

    wp_book = (
        "Elementary word problems about counting. A starting count changes when you buy, find, "
        "or receive more (increase) or give away, lose, sell, eat, borrow, or remove (decrease). "
        "Find how many remain altogether. Keywords: how many, total, remaining, left, count."
    )
    algebra_book = "Elementary algebra equation solve unknown variable both sides isolate."
    math_book = "Elementary arithmetic add subtract multiply divide whole numbers; fraction capacity full removed whole."

    r = learn_and_answer(wp_book, "wp_book", "Sam had 12 apples, bought 8 more, then gave away 5. How many apples does he have?")
    check("end-to-end word problem answered (15)", r.status == "ANSWERED" and r.domain == "multi_step_count_change" and "15" in (r.answer_text or ""))

    r2 = learn_and_answer(wp_book, "wp_book", "A shelf had 30 books. 12 were borrowed, then 6 were returned. How many books are on the shelf?")
    check("word problem with borrow/return (24)", r2.status == "ANSWERED" and "24" in (r2.answer_text or ""))

    routing = {
        "whole_number_arithmetic": "What is 7 times 12?",
        "fraction_change_capacity": "A storage bin was 11/12 full. After 21 kilograms were removed, it was 2/3 full. What is the full capacity of the storage bin?",
        "linear_equation_one_unknown": "solve 3x + 5 = 20 for x",
        "multi_step_count_change": "Sam had 12 apples, bought 8 more, then gave away 5. How many apples does he have?",
    }
    collisions = sum(1 for exp, q in routing.items() if (match_domain(q).domain_id if match_domain(q) else None) != exp)
    check("routing diagnostic: zero collisions", collisions == 0)
    check("four domains loaded", len(all_domains()) == 4)

    check("regression: arithmetic still works", "84" in (learn_and_answer(math_book, "m", "What is 7 times 12?").answer_text or ""))
    check("regression: equation still works", "5" in (learn_and_answer(algebra_book, "a", "solve 3x + 5 = 20 for x").answer_text or ""))

    check("unlearned refused (no guessing)", learn_and_answer(wp_book, "wp", "What is the area of a circle radius 3?").status == "REFUSED_UNLEARNED")

    pkg = forge_root / "rmc_engine_v1" / "general_pipeline"
    code = []
    for fn in ("domains_wordproblems.py", "gp003_word_problems.py"):
        for line in (pkg / fn).read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("#"):
                continue
            code.append(line.lower())
    blob = "\n".join(code)
    for tok in FORBIDDEN_TOKENS:
        check(f"boundary: no {tok!r}", tok.lower() not in blob)

    check("Echo approves word-problem output", r.trace.get("echo", {}).get("echo_status") == "ECHO_APPROVED_RENDERING_WITHIN_MANIFEST_SCOPE")

    print("\n".join(out))
    total = passed + failed
    status = "PASS" if failed == 0 else "FAIL"
    print(f"\nBUILD_ID: {gp3.GP003_BUILD_ID}")
    print(f"SCHEMA_VERSION: {gp3.GP003_SCHEMA_VERSION}")
    print(f"\nRESULT: GENERAL-PIPELINE-MULTISTEP-WORDPROBLEMS-BUILD-GP-003_VERIFY {status}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
