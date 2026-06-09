#!/usr/bin/env python3
"""Static and live verification for GP-004 production reground.

Run:
    .venv/bin/python scripts/general_pipeline_production_reground_build_gp004_verify.py --forge-root "$HOME/forge"

Verification is read-only: it imports modules, runs in-memory calls, and scans
the GP-004 General Pipeline source boundary for forbidden runtime side effects.
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

    gp_dir = forge_root / "rmc_engine_v1" / "general_pipeline"
    required = [
        "capability_registry.py",
        "domains.py",
        "source_compiler.py",
        "manifest_builder.py",
        "governed_gate.py",
        "pipeline.py",
        "domains_equations.py",
        "gp002_linear_equations.py",
        "domains_wordproblems.py",
        "gp003_word_problems.py",
        "gp004_production_reground.py",
    ]

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

    for filename in required:
        check(f"module present: rmc_engine_v1/general_pipeline/{filename}", (gp_dir / filename).is_file())

    try:
        from rmc_engine_v1.general_pipeline import gp004_production_reground as gp4
        from rmc_engine_v1.general_pipeline import learn_and_answer
        from rmc_engine_v1.general_pipeline.capability_registry import (
            all_capability_contracts,
            boundary_contract,
            capability_for_domain,
            registry_hash,
        )
        state = gp4.activate()
        imported = True
    except Exception as exc:
        imported = False
        out.append(f"FAIL  imports + GP-004 activation against real engine ({exc})")
        failed += 1
    else:
        check("imports + GP-004 activation against real MEA engine", imported)

    if imported:
        domains = [c.domain_id for c in all_capability_contracts()]
        check("four pre-existing domains registered centrally", domains == [
            "fraction_change_capacity",
            "whole_number_arithmetic",
            "linear_equation_one_unknown",
            "multi_step_count_change",
        ])
        check("registry snapshot hash stable", state["registry_hash"] == registry_hash())
        contract = capability_for_domain("linear_equation_one_unknown")
        check("equation capability is explicit and bounded", contract is not None and contract.parser_policy == "full_input_required")

        algebra = "Elementary algebra equation solve unknown variable both sides isolate."
        good = learn_and_answer(algebra, "a", "solve 11x + 17 = 105 for x")
        bad = learn_and_answer(algebra, "a", "x + y = 10")
        check("strict equation accepts supported unseen input", good.status == "ANSWERED" and "8" in (good.answer_text or ""))
        check("strict equation refuses former partial-match defect", bad.status == "REFUSED_UNLEARNED" and bad.answer_text is None)
        check("output carries verified meaning path", good.trace.get("echo", {}).get("approved_output") is True and "meaning_manifest" in good.trace)

        boundary = boundary_contract()
        check("boundary: in memory only", boundary["in_memory_only"] is True)
        check("boundary: no memory write", boundary["writes_memory"] is False)
        check("boundary: no Identity Vault write", boundary["writes_identity_vault"] is False)
        check("boundary: no Contribution Economy write", boundary["writes_contribution_economy"] is False)
        check("boundary: no CT mint", boundary["mints_ct"] is False)
        check("boundary: no corpus ingestion", boundary["adds_corpus_ingestion"] is False)
        check("boundary: no new spelling/language domain", boundary["adds_new_language_domain"] is False)
        check("boundary: no new third-party dependencies", boundary["third_party_dependencies_added"] == [])

    combined = "\n".join((gp_dir / name).read_text(encoding="utf-8") for name in required)
    forbidden_runtime_tokens = [
        "@app.route",
        "import flask",
        "from flask",
        "import chromadb",
        "chromadb.",
        ".add_documents(",
        "requests.post",
        "requests.get",
        "subprocess.",
        "os.system",
        "open(",
        "Path.write_text",
        "Path.write_bytes",
    ]
    for token in forbidden_runtime_tokens:
        check(f"boundary source has no forbidden runtime token {token!r}", token not in combined)

    gp2_text = (gp_dir / "gp002_linear_equations.py").read_text(encoding="utf-8")
    gp3_text = (gp_dir / "gp003_word_problems.py").read_text(encoding="utf-8")
    source_text = (gp_dir / "source_compiler.py").read_text(encoding="utf-8")
    domains_text = (gp_dir / "domains.py").read_text(encoding="utf-8")
    check("old GP-002 compiler monkey patch removed", "_wrapped_compile_source" not in gp2_text)
    check("old GP-003 compiler monkey patch removed", "_wrapped_compile_source" not in gp3_text)
    check("old mutable _DOMAINS list removed", "_DOMAINS" not in domains_text)
    check("source compiler uses centralized installed contracts", "all_capability_contracts" in source_text)
    check("source compiler does not register capability", "register_capability" not in source_text)

    print("\n".join(out))
    total = passed + failed
    result_status = "PASS" if failed == 0 else "FAIL"
    print(f"\nBUILD_ID: GENERAL-PIPELINE-PRODUCTION-REGROUND-BUILD-GP-004")
    print(f"SCHEMA_VERSION: general_pipeline_capability_registry_v1_build_gp004")
    print(f"RESULT: GENERAL-PIPELINE-PRODUCTION-REGROUND-BUILD-GP-004_VERIFY {result_status}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
