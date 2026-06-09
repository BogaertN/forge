"""Read-only adapter from the current committed MEA record into capsule compatibility preview."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from rmc_engine_v1.mea.manifest_memory_writer import (
    MANIFEST_MEMORY_WRITER_APPROVAL_TOKEN,
    MANIFEST_MEMORY_WRITER_DRY_RUN_ROUTE,
    evaluate_manifest_memory_writer_dry_run_request,
)
from rmc_engine_v1.mea.problem_manifest_store import problem_manifest_store_status

from .mea_compatibility_preview import build_mea_capsule_compatibility_preview

BUILD_ID = "CE-IV-LEDGER-CAPSULE-BUILD-001"


def build_current_committed_mea_capsule_preview(*, forge_root: Path | None = None) -> dict[str, Any]:
    """Read current committed MEA evidence and return one deterministic in-memory preview."""
    root = Path(forge_root).resolve() if forge_root is not None else Path(__file__).resolve().parents[3]
    store_root = root / "runtime_state" / "mea_problem_manifest_store_v1"
    status = problem_manifest_store_status(store_root=store_root, endpoint="/api/mea/problem-manifest")
    if status.get("integrity_verified") is not True or not isinstance(status.get("stored_state"), dict):
        raise ValueError("current committed MEA state is not integrity verified")
    stored = status["stored_state"]
    request = {
        "approval_token": MANIFEST_MEMORY_WRITER_APPROVAL_TOKEN,
        "transaction_id": stored.get("transaction_id"),
        "transaction_intent_hash": stored.get("transaction_intent_hash"),
        "candidate_id": stored.get("candidate_id"),
        "candidate_hash": stored.get("candidate_hash"),
        "committed_manifest_hash": stored.get("manifest_hash"),
        "committed_state_content_hash": stored.get("state_content_hash"),
    }
    dry_run = evaluate_manifest_memory_writer_dry_run_request(
        request, store_root=store_root, endpoint=MANIFEST_MEMORY_WRITER_DRY_RUN_ROUTE
    )
    if dry_run.get("gate_status") != "MEMORY_RECORD_DRY_RUN_READY_NO_WRITE" or dry_run.get("accepted") is not True:
        raise ValueError("Patch 299 MEA memory-record evidence preview did not verify")
    preview_evidence = {
        "candidate_id": dry_run["candidate_id"],
        "candidate_hash": dry_run["candidate_hash"],
        "claim_status": dry_run["claim_status"],
        "proof_debt": dry_run["proof_debt"],
        "source_manifest_hash": dry_run["source_manifest_hash"],
        "source_state_content_hash": dry_run["source_state_content_hash"],
        "committed_manifest_hash": dry_run["committed_manifest_hash"],
        "committed_state_content_hash": dry_run["committed_state_content_hash"],
        "transaction_id": dry_run["memory_record_preview"]["transaction_id"],
        "transaction_intent_hash": dry_run["transaction_intent_hash"],
        "transaction_seal_packet_hash": dry_run["transaction_seal_packet_hash"],
        "transaction_audit_chain_hash": dry_run["transaction_audit_chain_hash"],
        "advance_receipt_hash": dry_run["advance_receipt_hash"],
        "rollback_record_hash": dry_run["rollback_record_hash"],
        "memory_record_id": dry_run["memory_record_id"],
        "memory_record_hash": dry_run["memory_record_hash"],
        "memory_tier": dry_run["memory_tier"],
        "replay_verified": dry_run["replay_verified"],
        "all_replay_checks_passed": dry_run["all_replay_checks_passed"],
        "source_state_integrity_verified": dry_run["source_state_integrity_verified"],
    }
    preview = build_mea_capsule_compatibility_preview(preview_evidence)
    return {
        "schema_version": "current_mea_capsule_compatibility_adapter_result_v1_build001",
        "build_id": BUILD_ID,
        "source_gate_status": dry_run["gate_status"],
        "capsule_compatibility_preview": preview,
        "preview_only": True,
        "writes_files": False,
        "writes_memory_capsule": False,
        "writes_ledgers": False,
        "writes_identity_vault": False,
        "writes_mea_state": False,
        "mints_ct": False,
        "calls_llm": False,
        "public_output_authorized": False,
    }
