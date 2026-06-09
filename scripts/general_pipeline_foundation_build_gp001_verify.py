#!/usr/bin/env python3
"""Installed-state verifier for the General Learning-to-Answer Pipeline
(Build GP-001).

Run:
    .venv/bin/python scripts/general_pipeline_foundation_build_gp001_verify.py --forge-root "$HOME/forge"

Confirms the package is installed, imports against the real MEA engine, exposes
the expected surface, runs one full end-to-end answer, and proves the build's
boundaries (no route/UI/memory write is introduced by these modules).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXPECTED_MODULES = [
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

# These usage patterns must NOT appear in the new package: it must not open
# routes, write memory, call Chroma/Identity Vault, or mint CT in this build.
# We check for real import/call usage, not prose in boundary comments.
FORBIDDEN_TOKENS = [
    "@app.route",
    "import flask",
    "from flask",
    "import chromadb",
    "chromadb.",
    ".add_documents(",
    "requests.post",
    "requests.get",
    "open(",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", default=None)
    args = parser.parse_args()

    forge_root = Path(args.forge_root).expanduser() if args.forge_root else Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(forge_root))

    passed = 0
    failed = 0
    results = []

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            results.append(f"PASS  {name}")
        else:
            failed += 1
            results.append(f"FAIL  {name}")

    # 1) all modules present
    for rel in EXPECTED_MODULES:
        check(f"module present: {rel}", (forge_root / rel).is_file())

    # 2) imports against the real engine
    try:
        from rmc_engine_v1.general_pipeline import (
            learn_and_answer,
            GENERAL_PIPELINE_BUILD_ID,
            GENERAL_PIPELINE_SCHEMA_VERSION,
        )
        from rmc_engine_v1.mea.manifest_schema import ProblemManifest  # real engine
        check("imports against real MEA engine", True)
    except Exception as exc:  # pragma: no cover
        check(f"imports against real MEA engine ({exc})", False)
        print("\n".join(results))
        print(f"\nRESULT: GENERAL-PIPELINE-FOUNDATION-BUILD-GP-001_VERIFY FAIL  Total:{passed+failed} Passed:{passed} Failed:{failed}")
        return 1

    # 3) end-to-end answer
    book = (
        "Elementary arithmetic teaches how to add, subtract, multiply and divide whole numbers. "
        "Fractions and capacity: when part of a full container is removed, the change in the "
        "fraction full equals the amount removed divided by the whole capacity."
    )
    r = learn_and_answer(book, "elementary_math_book", "What is 7 times 12?")
    check("end-to-end arithmetic answered", r.status == "ANSWERED" and "84" in (r.answer_text or ""))

    r2 = learn_and_answer(
        book, "elementary_math_book",
        "A storage bin was 11/12 full. After 21 kilograms were removed, it was 2/3 full. What is the full capacity of the storage bin?",
    )
    check("end-to-end capacity answered (84 kg)", r2.status == "ANSWERED" and "84 kilograms" in (r2.answer_text or ""))

    # 4) refusal boundary
    r3 = learn_and_answer(book, "b", "What is the area of a rectangle 4 by 6?")
    check("unlearned question refused (no guessing)", r3.status == "REFUSED_UNLEARNED")

    # 5) forbidden usage patterns absent from package source (ignore comments/docstrings prose)
    pkg_dir = forge_root / "rmc_engine_v1" / "general_pipeline"
    code_lines = []
    for p in pkg_dir.glob("*.py"):
        for line in p.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            code_lines.append(line.lower())
    blob = "\n".join(code_lines)
    for tok in FORBIDDEN_TOKENS:
        check(f"boundary: package contains no {tok!r}", tok.lower() not in blob)

    # 6) Echo authority present (this build's core correction)
    check(
        "Echo approves faithful output (approval-gate authority)",
        r.trace.get("echo", {}).get("echo_status") == "ECHO_APPROVED_RENDERING_WITHIN_MANIFEST_SCOPE",
    )

    print("\n".join(results))
    total = passed + failed
    status = "PASS" if failed == 0 else "FAIL"
    print(f"\nBUILD_ID: {GENERAL_PIPELINE_BUILD_ID}")
    print(f"SCHEMA_VERSION: {GENERAL_PIPELINE_SCHEMA_VERSION}")
    print(f"\nRESULT: GENERAL-PIPELINE-FOUNDATION-BUILD-GP-001_VERIFY {status}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
