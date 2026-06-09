#!/usr/bin/env python3
"""Behavior tests for MEA-DISCOVERY-KERNEL-LIVE-TERM-BINDING-BUILD-007.

All tests are read-only. No historical state, JSONL record, Identity Vault,
Contribution Economy, UI, route, renderer, Chroma, or LLM surface is changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    if not root.exists():
        return digest.hexdigest()
    for path in sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and path_suffix_ok(p)):
        digest.update(f"{path.relative_to(root).as_posix()}\0{hashlib.sha256(path.read_bytes()).hexdigest()}\n".encode("utf-8"))
    return digest.hexdigest()


def path_suffix_ok(path: Path) -> bool:
    return path.suffix not in {".pyc", ".pyo"}


def contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(contains_float(v) for v in value)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", required=True, type=Path)
    args = parser.parse_args()
    forge_root = args.forge_root.expanduser().resolve()
    sys.path.insert(0, str(forge_root))

    from rmc_engine_v1.mea.fixed_point_math_contract import UNIT_SCALE  # noqa: WPS433
    from rmc_engine_v1.mea.live_term_binding import (  # noqa: WPS433
        BUILD_ID,
        build_forward_144hz_hypothesis_fixture,
        build_historical_live_binding_audit,
        evaluate_forward_candidate_terms,
        live_term_binding_boundary,
        verify_mea_manifest_memory_ledger,
    )
    from rmc_engine_v1.mea.measured_seal_gate import evaluate_measured_seal_readiness, measured_seal_gate_boundary  # noqa: WPS433

    passed = failed = 0
    def check(name: str, ok: bool, detail: object = None) -> None:
        nonlocal passed, failed
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail is not None else ""))
        passed += int(ok); failed += int(not ok)

    print("MEA-DISCOVERY-KERNEL-LIVE-TERM-BINDING-BUILD-007 BEHAVIOR TESTS — READ ONLY")
    state_root = forge_root / "runtime_state" / "mea_problem_manifest_store_v1"
    memory_root = forge_root / "memory" / "mea_manifest_memory_v1"
    before_state = tree_hash(state_root)
    before_memory = tree_hash(memory_root)

    boundary = live_term_binding_boundary()
    check("build_id_locked", BUILD_ID == "MEA-DISCOVERY-KERNEL-LIVE-TERM-BINDING-BUILD-007")
    for name in ("writes_files", "writes_mea_memory", "writes_mea_runtime_state", "writes_identity_vault", "writes_contribution_economy", "mints_ct", "writes_ledgers", "writes_chroma", "calls_llm", "renders_user_output", "creates_http_routes", "modifies_ui"):
        check(f"boundary_{name}_false", boundary[name] is False, boundary[name])
    check("history_preserved", boundary["historic_records_preserved"] is True)
    check("no_retroactive_scoring", boundary["historical_scoring_rewritten"] is False)
    check("R_requires_explicit_ancestry", boundary["future_candidates_require_explicit_memory_ancestry_for_R"] is True)
    check("K_requires_executed_trace", boundary["future_candidates_require_executed_operator_path_for_K"] is True)
    check("replay_not_truth", boundary["replay_proves_truth"] is False)

    ledger = verify_mea_manifest_memory_ledger(memory_root)
    check("build005_ledger_hash_chain_valid", ledger["valid"] is True, ledger.get("errors"))
    check("build005_ledger_exact_one_node", ledger["entry_count"] == 1, ledger["entry_count"])
    check("build005_record_hash_available", ledger["nodes"][0]["memory_record_hash"] == "c7961e88d1ae7c718662b4d8541c18948c63c3d2b374c9e95b7ee9338338fc99")

    historic = build_historical_live_binding_audit(forge_root)
    check("historical_status_preserved_hypothesis", historic["historical_claim_status"] == "hypothesis")
    check("historical_ancestry_was_empty", historic["historical_memory_ancestry_count"] == 0)
    check("historical_retroactive_R_forbidden", historic["retroactive_R_binding_permitted"] is False)
    check("historical_retroactive_rescore_forbidden", historic["retroactive_rescoring_permitted"] is False)
    check("memory_available_only_forward", historic["post_build005_memory_nodes_available_for_future_candidates"] == 1)

    parent, candidate, contract = build_forward_144hz_hypothesis_fixture(forge_root)
    result = evaluate_forward_candidate_terms(parent, candidate, contract, memory_root=memory_root)
    terms = result.terms_micro
    check("term_vector_complete", set(terms) == {"R", "P", "U", "N", "I", "Omega", "A", "D", "B", "K"})
    check("score_contract_has_no_float", contains_float(result.score_result) is False)
    check("R_measured_from_explicit_hash_bound_memory", terms["R"] == 300_000, terms["R"])
    check("P_measured_from_phi5_codex", terms["P"] == 880_000, terms["P"])
    check("I_measured_from_validated_unknown_narrowing", terms["I"] == UNIT_SCALE, terms["I"])
    check("Omega_measured_as_test_path_progress", terms["Omega"] == 400_000, terms["Omega"])
    check("A_preserves_goal_ancestry", terms["A"] == UNIT_SCALE, terms["A"])
    check("D_preserves_phi5_vigilance_without_overclaim", terms["D"] == 120_000, terms["D"])
    check("B_requires_registered_theory_evidence_not_request_only", terms["B"] == 850_000, terms["B"])
    check("unregistered_theory_source_rejected", "theory_source_registry_required:fbsc_90hz_internal_ancestry" in result.evidence_rejections)
    check("K_bound_to_executed_operator_path", terms["K"] == 280_000, terms["K"])
    check("hypothesis_status_remains", result.epistemic_claim_status == "hypothesis")
    check("next_action_is_test_required", result.required_next_action == "test_required")
    check("empirical_claim_not_authorized", result.evidence_assessment["verified_empirical_claim_permitted"] is False)
    check("explicit_ancestry_bound", result.explicit_memory_ancestry_bound is True)
    check("explicit_operator_trace_bound", result.explicit_operator_trace_bound is True)

    readiness = evaluate_measured_seal_readiness(result)
    check("forward_measured_gate_blocks_until_theory_evidence_registered", readiness.all_required_gates_passed is False)
    check("forward_candidate_not_sealable_without_source_registry", readiness.eligible_for_future_seal_transaction is False)
    check("seal_not_executed", readiness.seal_execution_performed is False)
    check("verified_empirical_claim_still_forbidden", readiness.verified_empirical_claim_permitted is False)

    tampered_contract = dict(contract)
    tampered_contract["memory_ancestry_bindings"] = [{"memory_record_hash": "0" * 64}]
    tampered = evaluate_forward_candidate_terms(parent, candidate, tampered_contract, memory_root=memory_root)
    tampered_gate = evaluate_measured_seal_readiness(tampered)
    check("tampered_memory_binding_sets_R_zero", tampered.terms_micro["R"] == 0)
    check("tampered_memory_binding_blocks_seal", tampered_gate.eligible_for_future_seal_transaction is False)

    no_trace_contract = dict(contract)
    no_trace_contract["executed_operator_path"] = []
    no_trace = evaluate_forward_candidate_terms(parent, candidate, no_trace_contract, memory_root=memory_root)
    no_trace_gate = evaluate_measured_seal_readiness(no_trace)
    check("missing_operator_trace_sets_K_zero", no_trace.terms_micro["K"] == 0)
    check("missing_operator_trace_blocks_seal", no_trace_gate.eligible_for_future_seal_transaction is False)

    no_replay_contract = dict(contract)
    no_replay_contract["replay_confirmed"] = False
    no_replay = evaluate_forward_candidate_terms(parent, candidate, no_replay_contract, memory_root=memory_root)
    no_replay_gate = evaluate_measured_seal_readiness(no_replay)
    check("missing_replay_sets_max_drift", no_replay.terms_micro["D"] == UNIT_SCALE)
    check("missing_replay_blocks_seal", no_replay_gate.eligible_for_future_seal_transaction is False)

    check("measured_seal_gate_read_only", measured_seal_gate_boundary()["writes_files"] is False)
    check("runtime_state_not_changed", tree_hash(state_root) == before_state)
    check("historical_memory_not_changed", tree_hash(memory_root) == before_memory)
    print(f"RESULT: MEA-DISCOVERY-KERNEL-LIVE-TERM-BINDING-BUILD-007_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
