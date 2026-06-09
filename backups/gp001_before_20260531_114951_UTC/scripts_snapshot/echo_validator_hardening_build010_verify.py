#!/usr/bin/env python3
"""Installed-state verifier for RMC-MEA-ECHO-VALIDATOR-HARDENING-BUILD-010."""
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

    from rmc_engine_v1.renderer.echo_validator import (  # noqa: WPS433
        BUILD_ID,
        VALID_STATUS,
        echo_validator_boundary,
        echo_validator_status,
    )

    boundary = echo_validator_boundary()
    status = echo_validator_status(forge_root=forge_root)
    canonical = status["mode_reports"]["explanation"]
    checks = {
        "build_id_locked": BUILD_ID == "RMC-MEA-ECHO-VALIDATOR-HARDENING-BUILD-010",
        "status_ok": status.get("status") == "OK",
        "canonical_explanation_echo_valid": canonical.get("accepted") is True,
        "canonical_valid_status": canonical.get("echo_status") == VALID_STATUS,
        "canonical_full_echo_score": canonical.get("echo_score_micro") == 1_000_000,
        "canonical_later_gate_only": canonical.get("eligible_for_later_approval_gate") is True and canonical.get("rendered_output_approved") is False,
        "valid_modes_exact": set(status.get("valid_preview_modes", [])) == {"explanation", "verification_result", "uncertain_result"},
        "template_repair_required_exact": set(status.get("template_repair_required_modes", [])) == {"decision", "warning", "next_step", "refusal"},
        "proof_debt_caveat_enforced": boundary.get("requires_proof_debt_in_rendered_language") is True,
        "uncertainty_enforced": boundary.get("requires_uncertainty_preservation") is True,
        "claim_upgrade_blocked": boundary.get("rejects_claim_upgrade") is True,
        "invented_evidence_blocked": boundary.get("rejects_invented_evidence") is True,
        "generic_echo_untouched": boundary.get("existing_generic_echo_validator_left_untouched") is True,
        "no_output_approval": boundary.get("approves_user_output") is False and status.get("approved_output") is False,
        "no_routes_or_ui": boundary.get("creates_http_routes") is False and boundary.get("modifies_ui") is False,
        "no_memory_or_state_writes": boundary.get("writes_files") is False and boundary.get("writes_mea_memory") is False and boundary.get("writes_rmc_output_memory") is False,
        "no_identity_contribution_ct_ledger": boundary.get("writes_identity_vault") is False and boundary.get("writes_contribution_economy") is False and boundary.get("mints_ct") is False and boundary.get("writes_ledgers") is False,
        "no_chroma_or_llm": boundary.get("writes_chroma") is False and boundary.get("calls_llm") is False,
    }
    passed = failed = 0
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        passed += int(ok)
        failed += int(not ok)

    print()
    print(json.dumps({
        "build_id": BUILD_ID,
        "canonical_preview_mode": status.get("canonical_preview_mode"),
        "canonical_echo_status": canonical.get("echo_status"),
        "canonical_echo_score_micro": canonical.get("echo_score_micro"),
        "canonical_eligible_for_later_approval_gate": canonical.get("eligible_for_later_approval_gate"),
        "approved_output": status.get("approved_output"),
        "valid_preview_modes": status.get("valid_preview_modes"),
        "template_repair_required_modes": status.get("template_repair_required_modes"),
        "template_repair_reason": "material_proof_debt_not_preserved_in_contract_and_rendered_text",
        "claim_status": "hypothesis",
        "required_next_action": "test_required",
        "proof_debt_text": "0.85",
        "boundary": boundary,
    }, indent=2, sort_keys=True))
    print()
    print(f"RESULT: RMC-MEA-ECHO-VALIDATOR-HARDENING-BUILD-010_VERIFY {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
