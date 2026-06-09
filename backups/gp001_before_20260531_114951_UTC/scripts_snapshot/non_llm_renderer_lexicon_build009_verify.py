#!/usr/bin/env python3
"""Installed-state verifier for RMC-NON-LLM-RENDERER-AND-SEMANTIC-LEXICON-BUILD-009."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", required=True, type=Path)
    args = parser.parse_args()
    forge_root = args.forge_root.expanduser().resolve()
    sys.path.insert(0, str(forge_root))

    from rmc_engine_v1.renderer.semantic_lexicon import BUILD_ID, SUPPORTED_DELIVERY_MODES  # noqa: WPS433
    from rmc_engine_v1.renderer.renderer import (  # noqa: WPS433
        non_llm_renderer_boundary,
        non_llm_renderer_status,
        render_historical_hypothesis_preview,
    )

    boundary = non_llm_renderer_boundary()
    status = non_llm_renderer_status(forge_root=forge_root)
    previews = {
        mode: render_historical_hypothesis_preview(forge_root=forge_root, delivery_mode=mode)
        for mode in SUPPORTED_DELIVERY_MODES
    }
    explanation = previews["explanation"]
    p = explanation.get("render_preview") or {}
    contract = p.get("epistemic_contract") or {}
    text = p.get("rendered_text_preview", "")

    checks = {
        "build_id_locked": BUILD_ID == "RMC-NON-LLM-RENDERER-AND-SEMANTIC-LEXICON-BUILD-009",
        "status_ok": status.get("status") == "OK",
        "preview_available": status.get("qualified_hypothesis_preview_available") is True,
        "seven_modes_available": len(previews) == 7 and all(report.get("accepted") is True for report in previews.values()),
        "deterministic_renderer_not_llm": boundary.get("uses_free_form_generation") is False and boundary.get("calls_llm") is False,
        "build008_admission_is_only_entry": boundary.get("input_contract") == "accepted_Build008_MEA_render_admission_packet",
        "meaning_manifest_not_compiled": boundary.get("compiles_rmc_meaning_manifest") is False,
        "claim_is_hypothesis": contract.get("claim_status") == "hypothesis",
        "test_required_preserved": contract.get("required_next_action") == "test_required",
        "proof_debt_preserved": contract.get("proof_debt_micro") == 850_000,
        "verified_claim_blocked": contract.get("may_render_as_verified_claim") is False,
        "empirical_fact_blocked": contract.get("may_render_as_empirical_fact") is False,
        "discovery_blocked": contract.get("may_render_as_discovery") is False,
        "text_names_hypothesis": "hypothesis" in text,
        "text_names_test_requirement": "Testing is required" in text,
        "text_names_proof_debt": "0.85" in text,
        "render_is_preview_only": p.get("preview_status") == "UNAPPROVED_RENDER_PREVIEW_REQUIRES_BUILD010_ECHO_VALIDATION",
        "echo_validation_deferred": p.get("echo_validation_required") is True and p.get("echo_validation_performed") is False,
        "output_not_approved": p.get("approved_output") is False and p.get("user_facing_output_authorized") is False,
        "memory_write_not_allowed": p.get("memory_write_allowed") is False,
        "no_routes_or_ui": boundary.get("creates_http_routes") is False and boundary.get("modifies_ui") is False,
        "no_mea_or_rmc_write": boundary.get("writes_mea_memory") is False and boundary.get("writes_rmc_output_memory") is False,
        "no_identity_or_contribution_effect": boundary.get("writes_identity_vault") is False and boundary.get("writes_contribution_economy") is False and boundary.get("mints_ct") is False,
        "no_chroma": boundary.get("writes_chroma") is False,
        "no_public_output_approval": boundary.get("approves_user_output") is False and boundary.get("renders_public_output") is False,
    }

    passed = failed = 0
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        passed += int(ok)
        failed += int(not ok)

    print()
    print(json.dumps({
        "build_id": BUILD_ID,
        "status": status.get("status"),
        "preview_status": p.get("preview_status"),
        "delivery_modes": list(SUPPORTED_DELIVERY_MODES),
        "claim_status": contract.get("claim_status"),
        "required_next_action": contract.get("required_next_action"),
        "proof_debt_text": contract.get("proof_debt_text"),
        "render_preview_hash": p.get("render_preview_hash"),
        "render_report_hash": explanation.get("render_report_hash"),
        "rendered_text_preview": text,
        "echo_validation_required": p.get("echo_validation_required"),
        "echo_validation_performed": p.get("echo_validation_performed"),
        "approved_output": p.get("approved_output"),
        "boundary": boundary,
    }, indent=2, sort_keys=True))
    print()
    print(f"RESULT: RMC-NON-LLM-RENDERER-AND-SEMANTIC-LEXICON-BUILD-009_VERIFY {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
