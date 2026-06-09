#!/usr/bin/env python3
"""Installed-state verifier for GP-002 — one-unknown linear equations.

Run:
    .venv/bin/python scripts/general_pipeline_linear_equations_build_gp002_verify.py --forge-root "$HOME/forge"

Confirms the new modules are present, activate cleanly against the live engine,
answer an equation end to end, preserve GP-001 behavior, keep the honesty
boundary, and introduce no route/UI/memory-write/file-IO.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXPECTED_MODULES = [
    "rmc_engine_v1/general_pipeline/domains_equations.py",
    "rmc_engine_v1/general_pipeline/gp002_linear_equations.py",
]

GP001_FILES = [
    "rmc_engine_v1/general_pipeline/__init__.py",
    "rmc_engine_v1/general_pipeline/contracts.py",
    "rmc_engine_v1/general_pipeline/domains.py",
    "rmc_engine_v1/general_pipeline/source_compiler.py",
    "rmc_engine_v1/general_pipeline/manifest_builder.py",
    "rmc_engine_v1/general_pipeline/governed_gate.py",
    "rmc_engine_v1/general_pipeline/meaning_and_renderer.py",
    "rmc_engine_v1/general_pipeline/echo_approval.py",
    "rmc_engine_v1/general_pipeline/pipeline.py",
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

    # GP-001 files must still be present (untouched check is done by SHA file separately)
    for rel in GP001_FILES:
        check(f"GP-001 file present: {rel}", (forge_root / rel).is_file())

    try:
        from rmc_engine_v1.general_pipeline import gp002_linear_equations as gp2
        gp2.activate()
        from rmc_engine_v1.general_pipeline import learn_and_answer
        from rmc_engine_v1.mea.manifest_schema import ProblemManifest  # real engine
        check("imports + activate against real engine", True)
    except Exception as exc:  # pragma: no cover
        check(f"imports + activate against real engine ({exc})", False)
        print("\n".join(out))
        print(f"\nRESULT: GENERAL-PIPELINE-LINEAR-EQUATIONS-BUILD-GP-002_VERIFY FAIL  Total:{passed+failed} Passed:{passed} Failed:{failed}")
        return 1

    algebra_book = (
        "Elementary algebra. To solve an equation, isolate the unknown variable by doing the "
        "same operation to both sides. For a*x + b = c, subtract b then divide by a."
    )
    math_book = "Elementary arithmetic teaches add subtract multiply divide whole numbers; fraction capacity full removed whole."

    r = learn_and_answer(algebra_book, "algebra_book", "solve 3x + 5 = 20 for x")
    check("end-to-end equation answered (x=5)", r.status == "ANSWERED" and r.domain == "linear_equation_one_unknown" and " 5." in (r.answer_text or "") + " ")

    r2 = learn_and_answer(algebra_book, "algebra_book", "solve 2x + 3 = 8 for x")
    check("fractional equation answer (5/2)", r2.status == "ANSWERED" and "5/2" in (r2.answer_text or ""))

    # regression
    r3 = learn_and_answer(math_book, "math_book", "What is 7 times 12?")
    check("regression: arithmetic still works", r3.status == "ANSWERED" and "84" in (r3.answer_text or ""))

    # boundary: refusal
    r4 = learn_and_answer(algebra_book, "algebra_book", "What is the area of a circle radius 3?")
    check("unlearned refused (no guessing)", r4.status == "REFUSED_UNLEARNED")

    # boundary: forbidden usage absent (ignore comment lines)
    pkg = forge_root / "rmc_engine_v1" / "general_pipeline"
    code = []
    for p in (pkg / "domains_equations.py", pkg / "gp002_linear_equations.py"):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("#"):
                continue
            code.append(line.lower())
    blob = "\n".join(code)
    for tok in FORBIDDEN_TOKENS:
        check(f"boundary: no {tok!r}", tok.lower() not in blob)

    # Echo authority on equation
    check("Echo approves equation output", r.trace.get("echo", {}).get("echo_status") == "ECHO_APPROVED_RENDERING_WITHIN_MANIFEST_SCOPE")

    print("\n".join(out))
    total = passed + failed
    status = "PASS" if failed == 0 else "FAIL"
    print(f"\nBUILD_ID: {gp2.GP002_BUILD_ID}")
    print(f"SCHEMA_VERSION: {gp2.GP002_SCHEMA_VERSION}")
    print(f"\nRESULT: GENERAL-PIPELINE-LINEAR-EQUATIONS-BUILD-GP-002_VERIFY {status}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
