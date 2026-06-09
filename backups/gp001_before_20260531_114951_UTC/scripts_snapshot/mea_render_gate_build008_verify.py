#!/usr/bin/env python3
"""Installed-state verifier for MEA-TO-RMC-RENDER-GATE-ADAPTER-BUILD-008."""
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

    from rmc_engine_v1.renderer.mea_render_gate import (  # noqa: WPS433
        BUILD_ID,
        PERMITTED_FUTURE_OUTPUT_MODE,
        build_historical_hypothesis_admission_request,
        evaluate_mea_render_admission_request,
        mea_render_gate_boundary,
        mea_render_gate_status,
    )

    boundary = mea_render_gate_boundary()
    status = mea_render_gate_status(forge_root=forge_root)
    request = build_historical_hypothesis_admission_request(forge_root=forge_root)
    admission = evaluate_mea_render_admission_request(request, forge_root=forge_root)
    packet = admission.get("render_admission_packet") or {}
    epistemic = packet.get("epistemic_boundary") or {}
    scope = packet.get("permitted_future_render_scope") or {}

    checks = {
        "boundary_read_only": boundary["read_only"] is True and boundary["writes_files"] is False,
        "build_id_locked": BUILD_ID == "MEA-TO-RMC-RENDER-GATE-ADAPTER-BUILD-008",
        "schema_separation_locked": boundary["schema_separation_rule"] == "MEA_problem_manifest_and_RMC_meaning_manifest_must_not_be_merged",
        "source_available": status.get("available") is True,
        "historical_claim_hypothesis": status.get("claim_status") == "hypothesis",
        "historical_proof_debt_preserved": status.get("proof_debt_micro") == 850_000,
        "historical_memory_record_bound": status.get("memory_record_hash") == "c7961e88d1ae7c718662b4d8541c18948c63c3d2b374c9e95b7ee9338338fc99",
        "admission_passes_only_for_qualified_hypothesis": admission.get("accepted") is True and admission.get("permitted_future_output_mode") == PERMITTED_FUTURE_OUTPUT_MODE,
        "seal_and_replay_verified": admission.get("seal_and_replay_verified") is True,
        "no_rmc_manifest_compiled": admission.get("rmc_meaning_manifest_compiled") is False,
        "no_render_performed": admission.get("render_performed") is False,
        "no_echo_validation_performed": admission.get("echo_validation_performed") is False,
        "adapter_packet_does_not_merge_schemas": packet.get("schemas_merged") is False,
        "hypothesis_boundary_preserved": epistemic.get("claim_status") == "hypothesis",
        "test_required_preserved": epistemic.get("required_next_action") == "test_required",
        "verified_claim_blocked": epistemic.get("may_render_as_verified_claim") is False,
        "empirical_fact_blocked": epistemic.get("may_render_as_empirical_fact") is False,
        "discovery_blocked": epistemic.get("may_render_as_discovery") is False,
        "lexicon_deferred": scope.get("semantic_lexicon_not_yet_invoked") is True,
        "surface_realizer_deferred": scope.get("surface_realizer_not_yet_invoked") is True,
        "echo_required_later": scope.get("echo_validation_required_after_future_rendering") is True,
        "no_routes_or_ui": boundary["creates_http_routes"] is False and boundary["modifies_ui"] is False,
        "no_writes_or_llm": all(boundary[key] is False for key in ("writes_mea_memory", "writes_rmc_output_memory", "writes_identity_vault", "writes_contribution_economy", "writes_chroma", "calls_llm")),
    }
    passed = failed = 0
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        passed += int(ok)
        failed += int(not ok)
    print()
    print(json.dumps({
        "build_id": BUILD_ID,
        "gate_status": admission.get("gate_status"),
        "historical_source_status": status.get("gate_status"),
        "candidate_id": status.get("candidate_id"),
        "claim_status": admission.get("claim_status"),
        "required_next_action": admission.get("required_next_action"),
        "proof_debt_text": admission.get("proof_debt_text"),
        "permitted_future_output_mode": admission.get("permitted_future_output_mode"),
        "admission_packet_hash": packet.get("admission_packet_hash"),
        "render_performed": admission.get("render_performed"),
        "echo_validation_performed": admission.get("echo_validation_performed"),
        "boundary": boundary,
    }, indent=2, sort_keys=True))
    print()
    print(f"RESULT: MEA-TO-RMC-RENDER-GATE-ADAPTER-BUILD-008_VERIFY {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
