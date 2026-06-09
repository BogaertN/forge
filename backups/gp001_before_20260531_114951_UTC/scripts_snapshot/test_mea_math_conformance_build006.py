#!/usr/bin/env python3
"""Behavior tests for MEA-DISCOVERY-KERNEL-MATH-CONFORMANCE-BUILD-006.

All tests are read-only. They run the deterministic forward conformance
contract, audit the historical preview path, and verify that the Build 005
memory record remains an immutable bounded hypothesis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix not in {".pyc", ".pyo"}):
        digest.update(f"{path.relative_to(root).as_posix()}\0{hashlib.sha256(path.read_bytes()).hexdigest()}\n".encode("utf-8"))
    return digest.hexdigest()


def contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(contains_float(item) for item in value)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", required=True, type=Path)
    args = parser.parse_args()
    forge_root = args.forge_root.expanduser().resolve()
    sys.path.insert(0, str(forge_root))

    from rmc_engine_v1.mea.fixed_point_math_contract import (  # noqa: WPS433
        ALL_TERMS,
        UNIT_SCALE,
        decimal_text_to_micro,
        fixed_point_boundary,
        score_terms_fixed_point,
    )
    from rmc_engine_v1.mea.evidence_tier_contract import (  # noqa: WPS433
        EvidenceItem,
        EvidenceTier,
        assess_evidence,
        canonical_144hz_hypothesis_evidence,
        evidence_contract_boundary,
    )
    from rmc_engine_v1.mea.fbsc_operator_crosswalk import (  # noqa: WPS433
        binding_for_glyph,
        crosswalk_boundary,
        crosswalk_report,
        phase_binding,
    )
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

    passed = 0
    failed = 0

    def check(name: str, result: bool, detail: object = None) -> None:
        nonlocal passed, failed
        if result:
            passed += 1
            print(f"  [PASS] {name}" + (f" - {detail}" if detail is not None else ""))
        else:
            failed += 1
            print(f"  [FAIL] {name}" + (f" - observed={detail!r}" if detail is not None else ""))

    print("MEA-DISCOVERY-KERNEL-MATH-CONFORMANCE-BUILD-006 BEHAVIOR TESTS — READ ONLY")

    runtime_state = forge_root / "runtime_state" / "mea_problem_manifest_store_v1"
    memory_ledger = forge_root / "memory" / "mea_manifest_memory_v1" / "hypothesis_test_required_records.jsonl"
    before_runtime = tree_hash(runtime_state)
    before_memory = tree_hash(memory_ledger.parent)

    boundary = build006_boundary()
    check("build_id_locked", boundary["build_id"] == "MEA-DISCOVERY-KERNEL-MATH-CONFORMANCE-BUILD-006")
    for key in (
        "writes_files", "writes_mea_memory", "writes_mea_runtime_state",
        "writes_identity_vault", "writes_contribution_economy", "mints_ct",
        "writes_ledgers", "writes_chroma", "calls_llm", "renders_user_output",
        "creates_http_routes", "modifies_ui",
    ):
        check(f"boundary_{key}_false", boundary[key] is False, boundary[key])
    check("forward_contract_installed", boundary["installs_forward_math_contract"] is True)
    check("historical_records_not_rewritten", boundary["rewrites_historical_records"] is False)

    numeric_boundary = fixed_point_boundary()
    check("fixed_point_integer_contract", numeric_boundary["governed_numeric_type"] == "integer_fixed_point_micro_units_only")
    check("new_float_governed_input_blocked", numeric_boundary["legacy_float_values_allowed_as_new_governed_input"] is False)
    check("decimal_conversion_exact", decimal_text_to_micro("0.550000") == 550_000)
    try:
        score_terms_fixed_point({term: 0.5 for term in ALL_TERMS})
        rejects_float = False
    except TypeError:
        rejects_float = True
    check("fixed_point_rejects_new_float_term_vector", rejects_float)

    evidence = canonical_144hz_hypothesis_evidence()
    check("canonical_evidence_support_045", evidence.aggregate_support_micro == 450_000, evidence.aggregate_support_micro)
    check("canonical_proof_debt_055", evidence.proof_debt_micro == 550_000, evidence.proof_debt_micro)
    check("internal_evidence_has_no_empirical_authority", evidence.empirical_authority_present is False)
    check("internal_evidence_blocks_verified_empirical_claim", evidence.verified_empirical_claim_permitted is False)
    check("evidence_permits_hypothesis_review", evidence.hypothesis_review_permitted is True)
    empirical = assess_evidence(
        (
            EvidenceItem(
                evidence_id="external_test",
                description="Independent measurement.",
                tier=EvidenceTier.EXTERNAL_EMPIRICAL_MEASUREMENT.value,
                support_micro=900_000,
                supports_empirical_fact=True,
                independently_verified=True,
            ),
        ),
        requested_claim_kind="empirical_substrate_frequency_claim",
    )
    check("qualifying_external_evidence_can_authorize_empirical_review", empirical.verified_empirical_claim_permitted is True)
    check("evidence_boundary_is_read_only", evidence_contract_boundary()["writes_files"] is False)

    crosswalk = crosswalk_report()
    check("phase_codex_binding_valid", crosswalk["fbsc_phase_codex_valid"] is True)
    check("phase5_bound_to_entropy", crosswalk["phase5_binding"]["normalized_phase_id"] == "Φ5", crosswalk["phase5_binding"])
    check("phase9_binding_available", phase_binding("Phi9")["normalized_phase_id"] == "Φ9")
    check("recursive_memory_operator_bound_to_build005", "build005" in binding_for_glyph("⧜").activation_status)
    check("seal_operator_bound_to_patch297", "patch297" in binding_for_glyph("⧙").activation_status)
    check("draft_candidate_composition_law_locked", "O_verify" in crosswalk["composition_law"])
    check("crosswalk_is_read_only", crosswalk_boundary()["writes_files"] is False)

    report = canonical_144hz_conformance_report()
    report_repeat = canonical_144hz_conformance_report()
    result = report["conformance_result"]
    terms = result["score_result"]["terms_micro"]
    info = report["candidate_observations"]["information_gain"]
    gates = {gate["gate_name"]: gate for gate in result["gate_vector"]}
    check("conformance_report_hash_stable", report["report_hash"] == report_repeat["report_hash"])
    check("corrected_information_gain_formula", report["information_gain_formula"].startswith("I(c_i)=ΔF+ΔQ+ΔX"))
    check("delta_f_is_zero_no_verified_fact_added", info["delta_f_verified_fact_gain_micro"] == 0)
    check("delta_q_records_bounded_unknown_narrowing", info["delta_q_unknown_reduction_micro"] == UNIT_SCALE)
    check("information_gain_is_positive_one_unit", info["information_gain_micro"] == UNIT_SCALE, info["information_gain_micro"])
    check("term_I_bound_to_information_gain", terms["I"] == info["information_gain_micro"])
    check("term_B_bound_to_evidence_debt", terms["B"] == evidence.proof_debt_micro)
    check("term_P_matches_canonical_test_threshold_input", terms["P"] == 880_000)
    check("term_D_matches_canonical_test_threshold_input", terms["D"] == 120_000)
    check("term_Omega_matches_partial_convergence", terms["Omega"] == 400_000)
    check("score_contract_contains_no_float", contains_float(result["score_result"]) is False)
    check("hypothesis_gates_pass", result["all_required_hypothesis_gates_passed"] is True)
    check("drift_gate_passes", gates["drift_gate"]["passed"] is True)
    check("phase_gate_passes", gates["phase_gate"]["passed"] is True)
    check("hypothesis_debt_gate_passes", gates["hypothesis_proof_debt_gate"]["passed"] is True)
    check("verified_claim_gate_fails", gates["verified_claim_proof_debt_gate"]["passed"] is False)
    check("classification_remains_hypothesis", result["epistemic_claim_status"] == "hypothesis")
    check("next_action_is_test_required", result["required_next_action"] == "test_required")
    check("scientific_truth_not_claimed_from_replay", result["replay_proves_reproducibility_only"] is True)
    check("verified_empirical_claim_blocked", result["verified_empirical_claim_permitted"] is False)

    recall = recall_control_case()
    check("zero_information_gain_is_recall", recall["epistemic_claim_status"] == "recall")
    check("recall_is_reference_only", recall["required_next_action"] == "reference_only")
    mutation = replay_mutation_control_case()
    check("theta_mutation_rejected", mutation["epistemic_claim_status"] == "rejected")
    check("theta_mutation_contained", mutation["required_next_action"] == "contain_or_reject")

    gaps = legacy_gap_audit()
    check("legacy_preview_not_rewritten", gaps["historical_preview_preserved"] is True)
    check("legacy_gap_detects_zero_information_gain", "legacy_hypothesis_path_has_information_gain_zero_and_status_adjustment" in gaps["gaps_detected"])
    check("legacy_gap_detects_fallback_rpun", "legacy_coherence_preview_uses_fallback_R_P_U_N" in gaps["gaps_detected"])
    check("legacy_claim_status_preserved", gaps["legacy_claim_status"] == "hypothesis")
    check("legacy_rpun_fallback_detected", set(gaps["legacy_fallback_terms"]) == {"R", "P", "U", "N"})

    live_audit = live_runtime_measurement_audit()
    actual_terms = live_audit["actual_terms_micro_from_current_runtime"]
    check("live_measurement_reads_actual_candidate", live_audit["measurement_kernel_evidence"]["reads_actual_candidate"] is True)
    check("live_measurement_reads_actual_phase_path", live_audit["measurement_kernel_evidence"]["reads_actual_phase_path"] is True)
    check("live_measurement_not_falsely_declared_conformant", live_audit["live_activation_permitted"] is False)
    check("live_measurement_detects_zero_information_gain", "information_gain_zero_blocks_discovery" in live_audit["conformance_failures"])
    check("live_measurement_detects_drift_failure", "measured_drift_exceeds_theta_D" in live_audit["conformance_failures"], actual_terms["D"])
    check("live_measurement_detects_proof_debt_failure", "legacy_proof_debt_exceeds_hypothesis_limit" in live_audit["conformance_failures"], actual_terms["B"])
    check("live_measurement_detects_missing_memory_resonance", "no_measured_memory_ancestry_resonance_bound" in live_audit["conformance_failures"])
    full_audit = build006_full_conformance_audit()
    check("full_audit_installs_contract_without_false_activation", full_audit["production_contract_installed"] is True and full_audit["active_legacy_pipeline_declared_conformant"] is False)

    historical = verify_historical_build005_record(memory_ledger)
    check("historical_build005_memory_present", historical["present"] is True)
    check("historical_build005_memory_untouched", historical["valid"] is True, historical)
    check("historical_build005_record_hash_preserved", historical["memory_record_hash"] == "c7961e88d1ae7c718662b4d8541c18948c63c3d2b374c9e95b7ee9338338fc99")
    check("runtime_state_never_mutated", tree_hash(runtime_state) == before_runtime)
    check("mea_memory_ledger_never_mutated", tree_hash(memory_ledger.parent) == before_memory)

    print(f"RESULT: MEA-DISCOVERY-KERNEL-MATH-CONFORMANCE-BUILD-006_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
