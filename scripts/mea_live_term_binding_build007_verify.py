#!/usr/bin/env python3
"""Installed-state verifier for MEA-DISCOVERY-KERNEL-LIVE-TERM-BINDING-BUILD-007."""
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
    from rmc_engine_v1.mea.live_term_binding import build_forward_144hz_hypothesis_fixture, build_historical_live_binding_audit, evaluate_forward_candidate_terms, live_term_binding_boundary, verify_mea_manifest_memory_ledger
    from rmc_engine_v1.mea.measured_seal_gate import evaluate_measured_seal_readiness

    boundary = live_term_binding_boundary()
    memory_root = forge_root / "memory" / "mea_manifest_memory_v1"
    ledger = verify_mea_manifest_memory_ledger(memory_root)
    historic = build_historical_live_binding_audit(forge_root)
    parent, candidate, contract = build_forward_144hz_hypothesis_fixture(forge_root)
    measured = evaluate_forward_candidate_terms(parent, candidate, contract, memory_root=memory_root)
    gate = evaluate_measured_seal_readiness(measured)
    terms = measured.terms_micro
    checks = {
        "boundary_read_only": boundary["writes_files"] is False and boundary["writes_mea_memory"] is False,
        "history_preservation_locked": boundary["historic_records_preserved"] is True and boundary["historical_scoring_rewritten"] is False,
        "ledger_verified": ledger["valid"] is True and ledger["entry_count"] == 1,
        "historical_record_not_retroactively_bound": historic["retroactive_R_binding_permitted"] is False,
        "forward_R_explicitly_bound": terms["R"] == 300_000 and measured.explicit_memory_ancestry_bound is True,
        "forward_P_phase_codex_bound": terms["P"] == 880_000,
        "forward_I_unknown_narrowing_bound": terms["I"] == 1_000_000,
        "forward_Omega_test_path_bound": terms["Omega"] == 400_000,
        "forward_D_bounded": terms["D"] == 120_000,
        "forward_B_blocks_unregistered_theory_evidence": terms["B"] == 850_000,
        "unregistered_theory_source_rejected": "theory_source_registry_required:fbsc_90hz_internal_ancestry" in measured.evidence_rejections,
        "forward_K_operator_trace_bound": terms["K"] == 280_000,
        "hypothesis_not_promoted": measured.epistemic_claim_status == "hypothesis",
        "test_required_preserved": measured.required_next_action == "test_required",
        "empirical_truth_blocked": measured.evidence_assessment["verified_empirical_claim_permitted"] is False,
        "measured_gates_block_until_theory_source_is_registered": gate.all_required_gates_passed is False,
        "seal_not_executed": gate.seal_execution_performed is False,
        "renderer_not_activated": boundary["renders_user_output"] is False,
        "no_routes_or_ui": boundary["creates_http_routes"] is False and boundary["modifies_ui"] is False,
    }
    passed = failed = 0
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        passed += int(ok); failed += int(not ok)
    print()
    print(json.dumps({
        "build_id": boundary["build_id"],
        "historical_audit": historic,
        "forward_term_binding_result_hash": measured.result_hash,
        "forward_terms_micro": terms,
        "forward_score_hash": measured.score_result["score_hash"],
        "forward_seal_readiness_hash": gate.result_hash,
        "forward_seal_eligibility": gate.eligible_for_future_seal_transaction,
        "seal_execution_performed": gate.seal_execution_performed,
        "claim_status": measured.epistemic_claim_status,
        "required_next_action": measured.required_next_action,
        "verified_empirical_claim_permitted": measured.evidence_assessment["verified_empirical_claim_permitted"],
        "boundary": boundary,
    }, indent=2, sort_keys=True))
    print()
    print(f"RESULT: MEA-DISCOVERY-KERNEL-LIVE-TERM-BINDING-BUILD-007_VERIFY {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
