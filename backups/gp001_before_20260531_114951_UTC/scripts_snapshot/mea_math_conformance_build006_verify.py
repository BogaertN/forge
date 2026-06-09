#!/usr/bin/env python3
"""Installed-state verifier for MEA-DISCOVERY-KERNEL-MATH-CONFORMANCE-BUILD-006.

This verifier is read-only. It confirms that the deterministic conformance
contract is installed, the canonical 144 Hz calculation returns a bounded
hypothesis with test-required action, the historical Build 005 JSONL record
remains intact, and no runtime-state or economic memory is written.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", required=True, type=Path)
    args = parser.parse_args()
    forge_root = args.forge_root.expanduser().resolve()
    sys.path.insert(0, str(forge_root))

    from rmc_engine_v1.mea.fixed_point_math_contract import fixed_point_boundary  # noqa: WPS433
    from rmc_engine_v1.mea.evidence_tier_contract import canonical_144hz_hypothesis_evidence  # noqa: WPS433
    from rmc_engine_v1.mea.fbsc_operator_crosswalk import crosswalk_report  # noqa: WPS433
    from rmc_engine_v1.mea.math_conformance import (  # noqa: WPS433
        build006_boundary,
        canonical_144hz_conformance_report,
        legacy_gap_audit,
        live_runtime_measurement_audit,
        build006_full_conformance_audit,
        recall_control_case,
        replay_mutation_control_case,
        verify_historical_build005_record,
    )

    boundary = build006_boundary()
    numeric = fixed_point_boundary()
    report = canonical_144hz_conformance_report()
    result = report["conformance_result"]
    terms = result["score_result"]["terms_micro"]
    evidence = canonical_144hz_hypothesis_evidence()
    crosswalk = crosswalk_report()
    legacy = legacy_gap_audit()
    live_audit = live_runtime_measurement_audit()
    full_audit = build006_full_conformance_audit()
    recall = recall_control_case()
    replay_mutation = replay_mutation_control_case()
    memory = verify_historical_build005_record(
        forge_root / "memory" / "mea_manifest_memory_v1" / "hypothesis_test_required_records.jsonl"
    )

    checks = {
        "status_read_only": boundary["writes_files"] is False and boundary["writes_mea_memory"] is False,
        "build_id_locked": boundary["build_id"] == "MEA-DISCOVERY-KERNEL-MATH-CONFORMANCE-BUILD-006",
        "fixed_point_contract_active": numeric["governed_numeric_type"] == "integer_fixed_point_micro_units_only",
        "canonical_report_hash_present": len(report["report_hash"]) == 64,
        "information_gain_corrected": report["information_gain_formula"].startswith("I(c_i)=ΔF+ΔQ+ΔX"),
        "information_gain_positive": terms["I"] == 1_000_000,
        "proof_debt_locked_to_evidence": terms["B"] == 550_000 and evidence.proof_debt_micro == 550_000,
        "phase_gate_observed": terms["P"] == 880_000,
        "drift_gate_observed": terms["D"] == 120_000,
        "convergence_observed": terms["Omega"] == 400_000,
        "claim_is_hypothesis": result["epistemic_claim_status"] == "hypothesis",
        "next_action_test_required": result["required_next_action"] == "test_required",
        "verified_empirical_claim_blocked": result["verified_empirical_claim_permitted"] is False,
        "replay_not_truth": result["replay_proves_reproducibility_only"] is True,
        "recall_control_proves_non_regurgitation": recall["epistemic_claim_status"] == "recall",
        "replay_mutation_blocks_seal_path": replay_mutation["epistemic_claim_status"] == "rejected",
        "fbsc_crosswalk_valid": crosswalk["fbsc_phase_codex_valid"] is True,
        "build005_memory_record_preserved": memory.get("valid") is True,
        "legacy_fallback_gap_detected": "legacy_coherence_preview_uses_fallback_R_P_U_N" in legacy["gaps_detected"],
        "legacy_history_not_rewritten": legacy["historical_preview_preserved"] is True,
        "actual_live_measurement_audit_executed": live_audit["measurement_kernel_evidence"]["reads_actual_candidate"] is True,
        "actual_live_path_not_falsely_certified": live_audit["live_activation_permitted"] is False,
        "actual_live_gaps_identified": len(live_audit["conformance_failures"]) >= 4,
        "contract_installed_migration_still_gated": full_audit["production_contract_installed"] is True and full_audit["active_legacy_pipeline_declared_conformant"] is False,
    }

    passed = 0
    failed = 0
    for name, result_value in checks.items():
        print(f"  [{'PASS' if result_value else 'FAIL'}] {name}")
        if result_value:
            passed += 1
        else:
            failed += 1

    print()
    print(json.dumps({
        "build_id": boundary["build_id"],
        "epistemic_claim_status": result["epistemic_claim_status"],
        "required_next_action": result["required_next_action"],
        "proof_debt_micro": terms["B"],
        "information_gain_micro": terms["I"],
        "score_hash": result["score_result"]["score_hash"],
        "report_hash": report["report_hash"],
        "historical_memory_record_hash": memory.get("memory_record_hash"),
        "legacy_gaps_detected": legacy["gaps_detected"],
        "actual_live_measurement_conformance_failures": live_audit["conformance_failures"],
        "active_legacy_pipeline_declared_conformant": live_audit["live_activation_permitted"],
        "boundary": boundary,
    }, indent=2, sort_keys=True))
    print()
    print(f"RESULT: MEA-DISCOVERY-KERNEL-MATH-CONFORMANCE-BUILD-006_VERIFY {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
