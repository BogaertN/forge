#!/usr/bin/env python3
"""Behavior tests for MEA-TO-RMC-RENDER-GATE-ADAPTER-BUILD-008.

All tests are read-only against live Forge state.  Tamper/rejection tests copy
the MEA state and memory store into temporary directories and never mutate live
runtime state or the Build 005 JSONL memory record.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix not in {".pyc", ".pyo"}):
        digest.update(f"{path.relative_to(root).as_posix()}\0{hashlib.sha256(path.read_bytes()).hexdigest()}\n".encode("utf-8"))
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", required=True, type=Path)
    args = parser.parse_args()
    forge_root = args.forge_root.expanduser().resolve()
    sys.path.insert(0, str(forge_root))

    from rmc_engine_v1.renderer.mea_render_gate import (  # noqa: WPS433
        ADAPTER_PACKET_SCHEMA_VERSION,
        BUILD_ID,
        PERMITTED_FUTURE_OUTPUT_MODE,
        SOURCE_KIND,
        build_historical_hypothesis_admission_request,
        evaluate_mea_render_admission_request,
        mea_render_gate_boundary,
        mea_render_gate_status,
    )

    passed = failed = 0
    def check(name: str, ok: bool, detail: object = None) -> None:
        nonlocal passed, failed
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail is not None else ""))
        passed += int(ok)
        failed += int(not ok)

    print("MEA-TO-RMC-RENDER-GATE-ADAPTER-BUILD-008 BEHAVIOR TESTS — READ ONLY / NO RENDER")
    runtime_root = forge_root / "runtime_state" / "mea_problem_manifest_store_v1"
    memory_root = forge_root / "memory" / "mea_manifest_memory_v1"
    before_runtime = tree_hash(runtime_root)
    before_memory = tree_hash(memory_root)

    boundary = mea_render_gate_boundary()
    check("build_id_locked", BUILD_ID == "MEA-TO-RMC-RENDER-GATE-ADAPTER-BUILD-008")
    check("adapter_schema_locked", ADAPTER_PACKET_SCHEMA_VERSION == "mea_render_admission_packet_v1_build008")
    for key in (
        "creates_http_routes", "modifies_ui", "compiles_rmc_meaning_manifest",
        "invokes_rmc_renderer", "invokes_echo_validator", "renders_user_output",
        "approves_user_output", "writes_files", "writes_mea_memory",
        "writes_mea_runtime_state", "writes_rmc_output_memory",
        "writes_identity_vault", "writes_contribution_economy", "mints_ct",
        "writes_ledgers", "writes_chroma", "calls_llm", "executes_shell",
        "performs_network_io",
    ):
        check(f"boundary_{key}_false", boundary[key] is False, boundary[key])
    check("schema_separation_enforced", boundary["schema_separation_rule"] == "MEA_problem_manifest_and_RMC_meaning_manifest_must_not_be_merged")
    check("qualified_hypothesis_only", boundary["permits_only_qualified_hypothesis_explanation"] is True)
    check("historical_not_forward_reseal", boundary["forward_seal_eligibility_required_for_historical_record"] is False)

    status = mea_render_gate_status(forge_root=forge_root)
    check("historical_source_status_ok", status["status"] == "OK")
    check("historical_source_available", status["available"] is True)
    check("historical_candidate_locked", status["candidate_id"] == "cg_hypothesis_001")
    check("historical_claim_hypothesis", status["claim_status"] == "hypothesis")
    check("historical_proof_debt_preserved_text", status["proof_debt_text"] == "0.85")
    check("historical_proof_debt_preserved_micro", status["proof_debt_micro"] == 850_000)
    check("historical_record_hash_locked", status["memory_record_hash"] == "c7961e88d1ae7c718662b4d8541c18948c63c3d2b374c9e95b7ee9338338fc99")

    request = build_historical_hypothesis_admission_request(forge_root=forge_root)
    check("request_source_kind_sealed_memory", request["source_kind"] == SOURCE_KIND)
    check("request_output_mode_qualified_only", request["requested_output_mode"] == PERMITTED_FUTURE_OUTPUT_MODE)
    response = evaluate_mea_render_admission_request(request, forge_root=forge_root)
    packet = response.get("render_admission_packet") or {}
    epistemic = packet.get("epistemic_boundary") or {}
    render_scope = packet.get("permitted_future_render_scope") or {}
    check("admission_accepted", response["accepted"] is True, response.get("gate_status"))
    check("admission_gate_status", response["gate_status"] == "MEA_TO_RMC_RENDER_ADMITTED_QUALIFIED_HYPOTHESIS_ONLY_NO_RENDER")
    check("admission_does_not_render", response["render_performed"] is False)
    check("admission_does_not_compile_rmc_manifest", response["rmc_meaning_manifest_compiled"] is False)
    check("admission_does_not_echo_validate", response["echo_validation_performed"] is False)
    check("adapter_does_not_merge_schemas", packet.get("schemas_merged") is False)
    check("adapter_source_hash_bound", packet["source_binding"]["sealed_manifest_hash"] == status["sealed_manifest_hash"])
    check("adapter_memory_hash_bound", packet["source_binding"]["memory_record_hash"] == status["memory_record_hash"])
    check("adapter_historical_seal_verified", packet["historical_seal_and_replay_proof"]["already_sealed_historical_record"] is True)
    check("adapter_replay_verified", packet["historical_seal_and_replay_proof"]["replay_verified"] is True)
    check("adapter_requests_no_new_seal", packet["historical_seal_and_replay_proof"]["new_seal_requested"] is False)
    check("adapter_claim_preserved", epistemic["claim_status"] == "hypothesis")
    check("adapter_test_required_preserved", epistemic["required_next_action"] == "test_required")
    check("adapter_proof_debt_preserved", epistemic["proof_debt_micro"] == 850_000)
    check("adapter_verified_claim_blocked", epistemic["may_render_as_verified_claim"] is False)
    check("adapter_empirical_fact_blocked", epistemic["may_render_as_empirical_fact"] is False)
    check("adapter_discovery_blocked", epistemic["may_render_as_discovery"] is False)
    check("adapter_future_scope_qualified_only", render_scope["permitted_future_output_mode"] == PERMITTED_FUTURE_OUTPUT_MODE)
    check("adapter_semantic_lexicon_deferred", render_scope["semantic_lexicon_not_yet_invoked"] is True)
    check("adapter_surface_realizer_deferred", render_scope["surface_realizer_not_yet_invoked"] is True)
    check("adapter_echo_required_later", render_scope["echo_validation_required_after_future_rendering"] is True)
    check("adapter_hash_present", isinstance(packet.get("admission_packet_hash"), str) and len(packet["admission_packet_hash"]) == 64)

    def rejection(name: str, update: dict, expected_reason: str) -> None:
        mutated = deepcopy(request)
        mutated.update(update)
        rejected = evaluate_mea_render_admission_request(mutated, forge_root=forge_root)
        check(name, rejected.get("accepted") is False and rejected.get("reason_code") == expected_reason, rejected.get("reason_code"))

    rejection("draft_rejected", {"source_kind": "draft"}, "draft_source_not_render_admissible")
    rejection("unverified_candidate_rejected", {"source_kind": "unverified_candidate"}, "unverified_candidate_not_render_admissible")
    rejection("rejected_candidate_rejected", {"source_kind": "rejected_candidate"}, "rejected_candidate_not_render_admissible")
    rejection("wrong_seal_hash_rejected", {"sealed_manifest_hash": "0" * 64}, "render_source_hash_binding_mismatch")
    rejection("wrong_receipt_hash_rejected", {"seal_receipt_hash": "0" * 64}, "render_source_hash_binding_mismatch")
    rejection("wrong_memory_hash_rejected", {"memory_record_hash": "0" * 64}, "render_source_hash_binding_mismatch")
    rejection("verified_claim_upgrade_rejected", {"requested_claim_status": "verified_claim", "present_as_verified_claim": True}, "hypothesis_as_verified_claim_blocked")
    rejection("empirical_fact_upgrade_rejected", {"present_as_empirical_fact": True}, "hypothesis_as_empirical_fact_blocked")
    rejection("discovery_upgrade_rejected", {"present_as_discovery": True}, "hypothesis_as_discovery_blocked")
    rejection("recall_as_discovery_rejected", {"requested_claim_status": "recall", "present_as_discovery": True}, "recall_as_discovery_blocked")
    rejection("invented_evidence_rejected", {"additional_evidence_claims": ["published evidence not in manifest"]}, "invented_evidence_claims_blocked")
    rejection("uncertainty_omission_rejected", {"preserve_uncertainty": False}, "render_admission_semantics_violation")
    rejection("proof_debt_reduction_rejected", {"requested_proof_debt_text": "0.10"}, "render_admission_semantics_violation")
    rejection("missing_test_required_rejected", {"include_required_next_action": False}, "render_admission_semantics_violation")
    rejection("unauthorized_output_mode_rejected", {"requested_output_mode": "verification_result"}, "render_admission_semantics_violation")
    rejection("renderer_invocation_requested_rejected", {"render_user_output": True}, "render_admission_semantics_violation")
    rejection("manifest_compilation_requested_rejected", {"compile_rmc_meaning_manifest": True}, "render_admission_semantics_violation")

    with tempfile.TemporaryDirectory(prefix="build008_tamper_") as tmp:
        temp_root = Path(tmp) / "forge"
        temp_state = temp_root / "runtime_state" / "mea_problem_manifest_store_v1"
        temp_memory = temp_root / "memory" / "mea_manifest_memory_v1"
        temp_state.parent.mkdir(parents=True)
        temp_memory.parent.mkdir(parents=True)
        shutil.copytree(runtime_root, temp_state)
        shutil.copytree(memory_root, temp_memory)
        state_file = temp_state / "current_problem_manifest.json"
        state_obj = json.loads(state_file.read_text(encoding="utf-8"))
        state_obj["claim_status"] = "verified_claim"
        state_file.write_text(json.dumps(state_obj, indent=2), encoding="utf-8")
        tampered = evaluate_mea_render_admission_request(request, forge_root=temp_root)
        check("tampered_sealed_state_rejected", tampered.get("accepted") is False and tampered.get("reason_code") == "historical_sealed_source_verification_failed", tampered.get("reason_code"))

    with tempfile.TemporaryDirectory(prefix="build008_memory_tamper_") as tmp:
        temp_root = Path(tmp) / "forge"
        temp_state = temp_root / "runtime_state" / "mea_problem_manifest_store_v1"
        temp_memory = temp_root / "memory" / "mea_manifest_memory_v1"
        temp_state.parent.mkdir(parents=True)
        temp_memory.parent.mkdir(parents=True)
        shutil.copytree(runtime_root, temp_state)
        shutil.copytree(memory_root, temp_memory)
        ledger = temp_memory / "hypothesis_test_required_records.jsonl"
        row = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        row["memory_record"]["claim_status"] = "verified_claim"
        ledger.write_text(json.dumps(row, sort_keys=True) + "\n", encoding="utf-8")
        tampered = evaluate_mea_render_admission_request(request, forge_root=temp_root)
        check("tampered_memory_record_rejected", tampered.get("accepted") is False and tampered.get("reason_code") == "historical_sealed_source_verification_failed", tampered.get("reason_code"))

    after_runtime = tree_hash(runtime_root)
    after_memory = tree_hash(memory_root)
    check("runtime_state_unchanged", after_runtime == before_runtime)
    check("mea_memory_unchanged", after_memory == before_memory)
    print(f"RESULT: MEA-TO-RMC-RENDER-GATE-ADAPTER-BUILD-008_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
