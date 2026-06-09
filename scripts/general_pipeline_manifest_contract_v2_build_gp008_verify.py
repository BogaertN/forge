#!/usr/bin/env python3
"""Static and live boundary verifier for GP-008 — Manifest Contract v2."""

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

    from rmc_engine_v1.general_pipeline import learn_and_answer
    from rmc_engine_v1.general_pipeline import gp008_manifest_contract_v2 as gp8
    from rmc_engine_v1.general_pipeline.manifest_contract_v2 import manifest_contract_v2_boundary

    gp8.activate()
    gp_dir = forge_root / "rmc_engine_v1" / "general_pipeline"
    scripts_dir = forge_root / "scripts"
    files_required = [
        "manifest_contract_v2.py",
        "gp008_manifest_contract_v2.py",
        "pipeline.py",
        "meaning_and_renderer.py",
        "echo_approval.py",
        "dependency_registry.py",
        "__init__.py",
    ]
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

    for fn in files_required:
        check(f"module present: {fn}", (gp_dir / fn).exists())
    check("behavior script present", (scripts_dir / "test_general_pipeline_manifest_contract_v2_build_gp008.py").exists())
    check("verifier script present", (scripts_dir / "general_pipeline_manifest_contract_v2_build_gp008_verify.py").exists())

    boundary = manifest_contract_v2_boundary()
    check("boundary truthfully records authorized dependency transition", boundary["third_party_dependency_promoted"] is True and boundary["runtime_tool_activation_transition"] == "SUPERSEDED_BY_GP010B_R1")
    expected_false = [
        "corpus_ingestion_added", "persistent_memory_write_allowed", "identity_vault_write_allowed",
        "contribution_economy_write_allowed", "ct_mint_allowed", "ledger_write_allowed",
        "new_domain_added",
    ]
    for key in expected_false:
        check(f"boundary false: {key}", boundary[key] is False)
    check("boundary requires source ancestry", boundary["requires_source_ancestry"] is True)
    check("boundary requires execution receipt", boundary["requires_capability_execution_receipt"] is True)
    check("boundary requires verification receipt", boundary["requires_verification_receipt"] is True)
    check("boundary requires sealed MEA", boundary["requires_sealed_mea_manifest"] is True)
    check("boundary requires meaning before render", boundary["requires_meaning_manifest_before_render"] is True)
    check("boundary requires Echo delivery", boundary["requires_echo_before_delivery"] is True)

    pipeline_text = (gp_dir / "pipeline.py").read_text(encoding="utf-8")
    contract_text = (gp_dir / "manifest_contract_v2.py").read_text(encoding="utf-8")
    render_text = (gp_dir / "meaning_and_renderer.py").read_text(encoding="utf-8")
    echo_text = (gp_dir / "echo_approval.py").read_text(encoding="utf-8")
    dependency_text = (gp_dir / "dependency_registry.py").read_text(encoding="utf-8")

    check("pipeline builds v2 before rendering", pipeline_text.index("build_manifest_contract_v2(") < pipeline_text.index("render_with_manifest_contract_v2("))
    check("pipeline renders only through v2 wrapper", "render_with_manifest_contract_v2(meaning, manifest_contract_v2)" in pipeline_text)
    check("pipeline Echo-validates through v2 wrapper", "validate_and_approve_v2(meaning, rendered, manifest_contract_v2)" in pipeline_text)
    check("pipeline creates delivery authorization after Echo", "finalize_echo_delivery(manifest_contract_v2, meaning, echo)" in pipeline_text)
    check("renderer wrapper requires authority", "require_render_authority(manifest_contract_v2, meaning)" in render_text)
    check("Echo wrapper requires authority", "require_render_authority(manifest_contract_v2, meaning)" in echo_text)
    check("Echo preserves prior public approval status", "echo_status=base.echo_status" in echo_text)
    check("v2 contract has claim type", "claim_type" in contract_text and "FORMAL_DERIVATION" in contract_text)
    check("v2 contract has source ancestry", "source_ancestry" in contract_text and "SourceAncestryReferenceV2" in contract_text)
    check("v2 contract has execution references", "execution_receipt_hash" in contract_text and "invocation_request_hash" in contract_text)
    check("v2 contract has verification receipt", "VerificationReceiptV2" in contract_text and "verification_receipt" in contract_text)
    check("v2 contract records rendering permission", "render_permissions" in contract_text and "delivery_requires_echo" in contract_text)
    check("v2 contract records no memory write", "NO_PERSISTENT_MEMORY_WRITE_GP008" in contract_text)
    check("v2 contract records no identity write", "NO_IDENTITY_VAULT_WRITE_GP008" in contract_text)
    check("v2 contract records no economic write", "NO_CONTRIBUTION_CT_OR_LEDGER_ACTION_GP008" in contract_text)
    check("v2 contract records no corpus ingestion", "NOT_CORPUS_INGESTED_GP008" in contract_text)
    check("v2 contract records no external provenance yet", "NO_EXTERNAL_PROVENANCE_LINK_GP008" in contract_text)
    check("dependency source binding advanced to GP-008", "BOUND_TO_INSTALLED_GP008_SOURCE_HASHES" in dependency_text)
    check("dependency source preserves GP-007 audit trail", "BOUND_TO_INSTALLED_GP007_SOURCE_HASHES" in dependency_text)

    forbidden_tokens = [
        "import sympy", "from sympy", "import lark", "from lark", "import pint", "from pint",
        "sqlite3.connect", "chromadb", "identity_vault", "mint_ct", "influence_ledger", "investment_ledger",
    ]
    combined = "\n".join((gp_dir / fn).read_text(encoding="utf-8").lower() for fn in ["manifest_contract_v2.py", "gp008_manifest_contract_v2.py"])
    for token in forbidden_tokens:
        # identity/economy terms may appear only as explicit negative boundary constants.
        if token in {"identity_vault", "mint_ct", "influence_ledger", "investment_ledger"}:
            check(f"boundary term not used as executable call: {token}", f"{token}(" not in combined and f".{token}(" not in combined)
        else:
            check(f"no forbidden dependency/use: {token}", token not in combined)

    algebra_book = (
        "Elementary algebra. To solve an equation, isolate the unknown variable by doing the same operation "
        "to both sides. For a*x + b = c, subtract b from both sides then divide by a. This finds the variable."
    )
    result = learn_and_answer(algebra_book, "algebra_book", "solve 11x + 17 = 105 for x")
    check("live equation answers under v2", result.status == "ANSWERED" and "8" in result.answer_text)
    check("live trace has v2 contract", "manifest_contract_v2" in result.trace)
    check("live trace has delivery authorization", "delivery_authorization_v2" in result.trace)
    check("live trace binds AST", result.trace["manifest_contract_v2"]["typed_ast_hash"] == result.trace["typed_ast_hash"])
    check("live trace keeps no economic action", result.trace["manifest_contract_v2"]["economic_permission"] == "NO_CONTRIBUTION_CT_OR_LEDGER_ACTION_GP008")

    print("\n".join(lines))
    total = passed + failed
    status = "PASS" if failed == 0 else "FAIL"
    print("\nBUILD_ID: GENERAL-PIPELINE-MANIFEST-CONTRACT-V2-BUILD-GP-008")
    print("SCHEMA_VERSION: general_pipeline_manifest_contract_v2_build_gp008")
    print(f"RESULT: GENERAL-PIPELINE-MANIFEST-CONTRACT-V2-BUILD-GP-008_VERIFY {status}  Total:{total} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
