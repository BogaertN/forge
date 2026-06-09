"""Controlled persistent write for the first governed Contribution Economy record.

CE-CONTROLLED-CONTRIBUTION-EVENT-BUILD-004 authorizes exactly one private,
identity-bound Contribution Event and exactly one non-finalized Memory Capsule
Candidate.  It does not validate a classification, finalize a capsule, mint CT,
or write either economic ledger.
"""
from __future__ import annotations

import gc
import hashlib
import json
import os
import sqlite3
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ..contracts.canonical_json import assert_utc_timestamp_z, canonical_json
from ..contracts.ct_reward_policy import calculate_reward_preview
from ..identity_vault.multiuser_authority import require_scopes, resolve_authority_receipt

BUILD_ID = "CE-CONTROLLED-CONTRIBUTION-EVENT-BUILD-004"
SCHEMA_VERSION = "ce_controlled_event_write_v1_build004"
EVENT_ID = "CE-EVT-000001"
CAPSULE_ID = "CE-CAP-CAND-000001"
PRINCIPAL_ID = "ivp_nic_bogaert_contribution_owner_v1"
ACTION_COMPLETED_AT_UTC = "2026-05-30T20:27:05Z"
PERSISTENCE_CONSENT_APPROVAL_TOKEN = "APPROVE_CE_EVT_000001_INTERNAL_PERSISTENCE_CONSENT_BUILD004"
CONTROLLED_WRITE_APPROVAL_TOKEN = "APPROVE_CE_EVT_000001_AND_CANDIDATE_CONTROLLED_WRITE_BUILD004"

EVIDENCE_ARTIFACTS = {
    "aiweb_ce_operator_surface_build003_normal_overlay_repack.tar.gz": "0b843e5544fd0761793e505d72a90558311c8a8be963a329ac65846328d148a5",
    "BUILD003_INSTALL_RESULTS_UPLOAD_20260530_202127_UTC.tar.gz": "ca94a1fe1994103c684a46767012cfd4db416a5da384fb4e8ec2e29811c7b7ee",
    "BUILD003_LIVE_ACTIVATION_RESULTS_20260530_202705_UTC.tar.gz": "2befbcd3dbbd31032c2a1af8a4ee91d2cbdf2e740dc9c78fbc85297f7bcdd915",
}


class ControlledEventWriteError(RuntimeError):
    """Raised when the bounded Build 004 write cannot be safely proven."""


@dataclass(frozen=True)
class Build004Paths:
    forge_root: Path
    identity_root: Path
    identity_database: Path
    core_database: Path
    identity_sql: Path
    core_sql: Path
    service_contract: Path

    @classmethod
    def from_roots(cls, forge_root: Path, identity_root: Path) -> "Build004Paths":
        forge = Path(forge_root).resolve()
        identity = Path(identity_root).resolve()
        return cls(
            forge_root=forge,
            identity_root=identity,
            identity_database=identity / "data" / "identity_vault.db",
            core_database=forge / "memory" / "contribution_economy_v1" / "core" / "contribution_economy_core.db",
            identity_sql=identity / "schema_extensions" / "contribution_economy_internal_persistence_consent_build004.sql",
            core_sql=forge / "contribution_economy_v1" / "controlled_writes" / "build004_core_extension.sql",
            service_contract=identity / "service_contracts" / "contribution_economy_controlled_persistence_build004.v1.json",
        )


def _hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_regular_file(path: Path, label: str) -> None:
    if not path.is_file() or path.is_symlink():
        raise ControlledEventWriteError(f"{label} is missing or not a regular file: {path}")


def _load_contract(paths: Build004Paths) -> dict[str, Any]:
    for path, label in ((paths.identity_database, "Identity Vault database"), (paths.core_database, "Contribution Economy core database"), (paths.identity_sql, "Identity Vault Build 004 SQL"), (paths.core_sql, "core Build 004 SQL"), (paths.service_contract, "Build 004 service contract")):
        _require_regular_file(path, label)
    contract = json.loads(paths.service_contract.read_text(encoding="utf-8"))
    if contract.get("schema_version") != "ce_controlled_persistence_service_contract_v1_build004" or contract.get("build_id") != BUILD_ID:
        raise ControlledEventWriteError("Build 004 service contract identity mismatch")
    if contract.get("event_scope_id") != EVENT_ID or contract.get("principal_id") != PRINCIPAL_ID:
        raise ControlledEventWriteError("Build 004 service contract is not locked to CE-EVT-000001 and the approved principal")
    if contract.get("identity_schema_extension_sha256") != _sha256_file(paths.identity_sql):
        raise ControlledEventWriteError("Identity Vault Build 004 schema checksum mismatch")
    if contract.get("core_schema_extension_sha256") != _sha256_file(paths.core_sql):
        raise ControlledEventWriteError("Contribution Economy core Build 004 schema checksum mismatch")
    for forbidden in ("raw_private_identity_export_allowed", "public_display_authorized", "economic_processing_authorized", "ct_minting_authorized", "investment_processing_authorized", "general_live_event_persistence_enabled"):
        if contract.get(forbidden) is not False:
            raise ControlledEventWriteError(f"Build 004 contract must keep {forbidden} false")
    return contract


def _tar_has_text(path: Path, needles: tuple[str, ...]) -> None:
    texts: list[str] = []
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile() or not member.name.endswith((".txt", ".json")):
                continue
            stream = archive.extractfile(member)
            if stream is not None:
                texts.append(stream.read().decode("utf-8", errors="replace"))
    joined = "\n".join(texts)
    missing = [needle for needle in needles if needle not in joined]
    if missing:
        raise ControlledEventWriteError(f"required evidence statements missing from {path.name}: {missing}")


def verify_evidence_artifacts(evidence_dir: Path) -> dict[str, Any]:
    root = Path(evidence_dir).resolve()
    if not root.is_dir() or root.is_symlink():
        raise ControlledEventWriteError("evidence directory is unavailable or symlinked")
    artifacts: list[dict[str, str]] = []
    for filename, expected_hash in EVIDENCE_ARTIFACTS.items():
        path = root / filename
        _require_regular_file(path, f"event evidence artifact {filename}")
        actual_hash = _sha256_file(path)
        if actual_hash != expected_hash:
            raise ControlledEventWriteError(f"evidence artifact checksum mismatch: {filename}")
        artifacts.append({"artifact_name": filename, "sha256": actual_hash})
    _tar_has_text(
        root / "BUILD003_INSTALL_RESULTS_UPLOAD_20260530_202127_UTC.tar.gz",
        (
            "RESULT: CE-OPERATOR-SURFACE-BUILD-003_BEHAVIOR PASS  Total:47 Passed:47 Failed:0",
            "RESULT: CE-OPERATOR-SURFACE-BUILD-003_VERIFY PASS  Total:11 Passed:11 Failed:0",
            "RESULT: PATCH_300_BEHAVIOR PASS  Total:117 Passed:117 Failed:0",
        ),
    )
    _tar_has_text(
        root / "BUILD003_LIVE_ACTIVATION_RESULTS_20260530_202705_UTC.tar.gz",
        ("RESULT: BUILD003_LIVE_ACTIVATION_VERIFY PASS",),
    )
    evidence_body = {
        "schema_version": "ce_event_evidence_manifest_v1_build004",
        "build_id": BUILD_ID,
        "event_id": EVENT_ID,
        "event_title": "Controlled live integration and activation of the Contribution Economy read-only operator surface in Forge",
        "source_system": "Forge",
        "source_artifact_class": "verified_runtime_integration_receipt_chain",
        "artifacts": artifacts,
        "verified_outcomes": [
            "Build 003 source overlay checksum matched its reviewed packet",
            "Build 003 Python and React production build completed",
            "Build 003 behavior tests passed 47 of 47",
            "Build 003 installed-state verifier passed 11 of 11",
            "Patch 300 foundational behavior invariants passed 117 of 117",
            "Build 003 live read-only activation verification passed",
        ],
        "action_completed_at_utc": ACTION_COMPLETED_AT_UTC,
    }
    evidence_hash = _hash(evidence_body)
    return {**evidence_body, "evidence_manifest_hash": evidence_hash}


def _identity_schema_statements() -> tuple[str, ...]:
    return (
        "CREATE TABLE IF NOT EXISTS contributor_internal_persistence_consent_events_v1 (consent_event_id TEXT PRIMARY KEY,principal_id TEXT NOT NULL,event_scope_id TEXT NOT NULL,event_type TEXT NOT NULL CHECK (event_type IN ('internal_persistence_scope_grant','internal_persistence_scope_revocation')),internal_contribution_event_persistence_authorized INTEGER NOT NULL CHECK (internal_contribution_event_persistence_authorized IN (0,1)),internal_capsule_candidate_persistence_authorized INTEGER NOT NULL CHECK (internal_capsule_candidate_persistence_authorized IN (0,1)),public_display_authorized INTEGER NOT NULL CHECK (public_display_authorized=0),economic_processing_authorized INTEGER NOT NULL CHECK (economic_processing_authorized=0),ct_minting_authorized INTEGER NOT NULL CHECK (ct_minting_authorized=0),investment_processing_authorized INTEGER NOT NULL CHECK (investment_processing_authorized=0),authorization_basis TEXT NOT NULL,status TEXT NOT NULL CHECK (status IN ('active_internal_persistence_only','revoked')),effective_at_utc TEXT NOT NULL,prior_consent_event_hash TEXT,event_hash TEXT NOT NULL UNIQUE CHECK (length(event_hash)=64),schema_version TEXT NOT NULL,FOREIGN KEY (principal_id) REFERENCES contributor_principals(principal_id),UNIQUE(principal_id,event_scope_id,event_type))",
        "CREATE INDEX IF NOT EXISTS idx_internal_persistence_consent_principal_scope ON contributor_internal_persistence_consent_events_v1(principal_id,event_scope_id,effective_at_utc)",
        "CREATE TRIGGER IF NOT EXISTS block_update_internal_persistence_consent_events_v1 BEFORE UPDATE ON contributor_internal_persistence_consent_events_v1 BEGIN SELECT RAISE(ABORT, 'contributor_internal_persistence_consent_events_v1 is append-only'); END",
        "CREATE TRIGGER IF NOT EXISTS block_delete_internal_persistence_consent_events_v1 BEFORE DELETE ON contributor_internal_persistence_consent_events_v1 BEGIN SELECT RAISE(ABORT, 'contributor_internal_persistence_consent_events_v1 cannot be deleted'); END",
    )


def _core_schema_statements() -> tuple[str, ...]:
    return (
        "CREATE TABLE IF NOT EXISTS contribution_event_evidence_manifests_v1 (evidence_manifest_id TEXT PRIMARY KEY,event_id TEXT NOT NULL UNIQUE,evidence_manifest_hash TEXT NOT NULL UNIQUE CHECK (length(evidence_manifest_hash)=64),evidence_manifest_json TEXT NOT NULL,schema_version TEXT NOT NULL)",
        "CREATE TABLE IF NOT EXISTS controlled_write_authorizations_v1 (authorization_id TEXT PRIMARY KEY,event_id TEXT NOT NULL UNIQUE,capsule_id TEXT NOT NULL UNIQUE,principal_id TEXT NOT NULL,persistence_consent_event_hash TEXT NOT NULL CHECK (length(persistence_consent_event_hash)=64),approval_token_hash TEXT NOT NULL CHECK (length(approval_token_hash)=64),authorization_hash TEXT NOT NULL UNIQUE CHECK (length(authorization_hash)=64),status TEXT NOT NULL CHECK (status='consumed_single_controlled_write'),schema_version TEXT NOT NULL)",
        "CREATE TABLE IF NOT EXISTS contribution_event_payloads_v1 (event_id TEXT PRIMARY KEY,event_hash TEXT NOT NULL UNIQUE CHECK (length(event_hash)=64),event_payload_json TEXT NOT NULL,schema_version TEXT NOT NULL)",
        "CREATE TABLE IF NOT EXISTS memory_capsule_candidate_payloads_v1 (capsule_id TEXT PRIMARY KEY,top_level_hash TEXT NOT NULL UNIQUE CHECK (length(top_level_hash)=64),candidate_payload_json TEXT NOT NULL,schema_version TEXT NOT NULL)",
        "CREATE TABLE IF NOT EXISTS controlled_write_receipts_v1 (write_receipt_id TEXT PRIMARY KEY,event_id TEXT NOT NULL UNIQUE,capsule_id TEXT NOT NULL UNIQUE,principal_id TEXT NOT NULL,transaction_hash TEXT NOT NULL UNIQUE CHECK (length(transaction_hash)=64),receipt_json TEXT NOT NULL,status TEXT NOT NULL CHECK (status='committed_pending_validation_not_finalized_not_minted'),schema_version TEXT NOT NULL)",
        "CREATE TRIGGER IF NOT EXISTS block_update_evidence_manifests_v1 BEFORE UPDATE ON contribution_event_evidence_manifests_v1 BEGIN SELECT RAISE(ABORT, 'contribution_event_evidence_manifests_v1 is append-only'); END",
        "CREATE TRIGGER IF NOT EXISTS block_delete_evidence_manifests_v1 BEFORE DELETE ON contribution_event_evidence_manifests_v1 BEGIN SELECT RAISE(ABORT, 'contribution_event_evidence_manifests_v1 cannot be deleted'); END",
        "CREATE TRIGGER IF NOT EXISTS block_update_controlled_write_authorizations_v1 BEFORE UPDATE ON controlled_write_authorizations_v1 BEGIN SELECT RAISE(ABORT, 'controlled_write_authorizations_v1 is append-only'); END",
        "CREATE TRIGGER IF NOT EXISTS block_delete_controlled_write_authorizations_v1 BEFORE DELETE ON controlled_write_authorizations_v1 BEGIN SELECT RAISE(ABORT, 'controlled_write_authorizations_v1 cannot be deleted'); END",
        "CREATE TRIGGER IF NOT EXISTS block_update_contribution_event_payloads_v1 BEFORE UPDATE ON contribution_event_payloads_v1 BEGIN SELECT RAISE(ABORT, 'contribution_event_payloads_v1 is append-only'); END",
        "CREATE TRIGGER IF NOT EXISTS block_delete_contribution_event_payloads_v1 BEFORE DELETE ON contribution_event_payloads_v1 BEGIN SELECT RAISE(ABORT, 'contribution_event_payloads_v1 cannot be deleted'); END",
        "CREATE TRIGGER IF NOT EXISTS block_update_memory_capsule_candidate_payloads_v1 BEFORE UPDATE ON memory_capsule_candidate_payloads_v1 BEGIN SELECT RAISE(ABORT, 'memory_capsule_candidate_payloads_v1 is append-only'); END",
        "CREATE TRIGGER IF NOT EXISTS block_delete_memory_capsule_candidate_payloads_v1 BEFORE DELETE ON memory_capsule_candidate_payloads_v1 BEGIN SELECT RAISE(ABORT, 'memory_capsule_candidate_payloads_v1 cannot be deleted'); END",
        "CREATE TRIGGER IF NOT EXISTS block_update_controlled_write_receipts_v1 BEFORE UPDATE ON controlled_write_receipts_v1 BEGIN SELECT RAISE(ABORT, 'controlled_write_receipts_v1 is append-only'); END",
        "CREATE TRIGGER IF NOT EXISTS block_delete_controlled_write_receipts_v1 BEFORE DELETE ON controlled_write_receipts_v1 BEGIN SELECT RAISE(ABORT, 'controlled_write_receipts_v1 cannot be deleted'); END",
    )


def _construct_records(authority: Mapping[str, Any], evidence: Mapping[str, Any], consent_at_utc: str, approval_token: str) -> dict[str, Any]:
    require_scopes(authority, "internal_attribution_reference_authorized", "capsule_candidate_reference_authorized")
    if authority.get("principal_id") != PRINCIPAL_ID or authority.get("raw_private_identity_exported") is not False:
        raise ControlledEventWriteError("controlled event requires the approved private Identity Vault principal only")
    if authority.get("consent_scope", {}).get("public_display_authorized") or authority.get("consent_scope", {}).get("economic_processing_authorized") or authority.get("consent_scope", {}).get("ct_minting_authorized"):
        raise ControlledEventWriteError("controlled event cannot execute with public or economic consent active")
    consent_at = assert_utc_timestamp_z(consent_at_utc, "consent_effective_at_utc")
    consent_body = {
        "schema_version": "identity_vault_internal_persistence_consent_event_v1_build004",
        "consent_event_id": "IV-CE-PERSIST-CONSENT-CE-EVT-000001",
        "principal_id": PRINCIPAL_ID,
        "event_scope_id": EVENT_ID,
        "event_type": "internal_persistence_scope_grant",
        "internal_contribution_event_persistence_authorized": True,
        "internal_capsule_candidate_persistence_authorized": True,
        "public_display_authorized": False,
        "economic_processing_authorized": False,
        "ct_minting_authorized": False,
        "investment_processing_authorized": False,
        "authorization_basis": "operator_locked_ce_evt_000001_private_internal_persistence_only",
        "status": "active_internal_persistence_only",
        "effective_at_utc": consent_at,
        "prior_consent_event_hash": authority.get("consent_event_hash"),
    }
    consent_hash = _hash(consent_body)
    resolution_body = {
        "schema_version": "ce_internal_persistence_consent_resolution_v1_build004",
        "principal_id": PRINCIPAL_ID,
        "base_consent_resolution_hash": authority.get("consent_resolution_hash"),
        "persistence_consent_event_hash": consent_hash,
        "event_scope_id": EVENT_ID,
        "internal_contribution_event_persistence_authorized": True,
        "internal_capsule_candidate_persistence_authorized": True,
        "economic_processing_authorized": False,
        "ct_minting_authorized": False,
        "public_display_authorized": False,
    }
    persistence_resolution_hash = _hash(resolution_body)
    action_payload = {
        "schema_version": "ce_locked_action_payload_manifest_v1_build004",
        "event_id": EVENT_ID,
        "event_title": evidence["event_title"],
        "principal_id": PRINCIPAL_ID,
        "identity_disclosure_class": "private_identity_vault_only",
        "action_type": "builder_runtime_integration_and_live_activation",
        "action_description": "The contributor initiated the requirement that the Contribution Economy be integrated into Forge main.py and the live React operator console, approved and applied the reviewed Build 003 overlay, executed verification tests, and activated the read-only Contribution Economy operator surface in the running AI.Web application.",
        "contribution_type_candidate": "BLD",
        "difficulty_class_candidate": "standard",
        "influence_type_candidate": "direct",
        "classification_status": "asserted_candidate_requires_evidence_validation",
        "source_system": "Forge",
        "source_artifact_class": "verified_runtime_integration_receipt_chain",
        "evidence_manifest_hash": evidence["evidence_manifest_hash"],
        "action_completed_at_utc": ACTION_COMPLETED_AT_UTC,
        "event_storage_scope": "internal_only",
        "public_attribution_authorized": False,
    }
    action_payload_hash = _hash(action_payload)
    proof_body = {
        "schema_version": "contributor_action_proof_body_v1_build004",
        "event_id": EVENT_ID,
        "principal_id": PRINCIPAL_ID,
        "persistence_consent_resolution_hash": persistence_resolution_hash,
        "action_payload_hash": action_payload_hash,
        "source_artifact_proof_hash": evidence["evidence_manifest_hash"],
        "contribution_type": "BLD",
        "difficulty_class": "standard",
        "influence_type": "direct",
        "classification_status": "asserted_candidate_requires_evidence_validation",
        "action_completed_at_utc": ACTION_COMPLETED_AT_UTC,
    }
    action_proof_hash = _hash(proof_body)
    event_body = {
        "schema_version": "contribution_event_persisted_candidate_v1_build004",
        "build_id": BUILD_ID,
        "event_id": EVENT_ID,
        "event_title": evidence["event_title"],
        "principal_id": PRINCIPAL_ID,
        "identity_disclosure_class": "private_identity_vault_only",
        "consent_resolution_hash": persistence_resolution_hash,
        "persistence_consent_event_hash": consent_hash,
        "action_type": "builder_runtime_integration_and_live_activation",
        "contribution_type": "BLD",
        "difficulty_class": "standard",
        "influence_type": "direct",
        "classification_status": "asserted_candidate_requires_evidence_validation",
        "action_payload_hash": action_payload_hash,
        "source_artifact_proof_hash": evidence["evidence_manifest_hash"],
        "contributor_action_proof_hash": action_proof_hash,
        "timestamp_utc": ACTION_COMPLETED_AT_UTC,
        "event_status": "persisted_pending_validation_not_finalized_not_minted",
        "action_payload": action_payload,
        "proof_body": proof_body,
        "validation_record_id": None,
        "capsule_finalization_authorized": False,
        "ct_minting_authorized": False,
        "ledger_write_authorized": False,
        "public_attribution_authorized": False,
    }
    event_hash = _hash(event_body)
    reward_preview = calculate_reward_preview("BLD", "standard", "direct").as_dict()
    candidate_body = {
        "schema_version": "memory_capsule_candidate_persisted_v1_build004",
        "build_id": BUILD_ID,
        "capsule_id": CAPSULE_ID,
        "capsule_status": "identity_bound_candidate_persisted_pending_validation_not_finalized",
        "finalized": False,
        "finalized_timestamp": None,
        "contribution_event_id": EVENT_ID,
        "contribution_event_hash": event_hash,
        "principal_id": PRINCIPAL_ID,
        "contributor_action_proof_hash": action_proof_hash,
        "proof_hash": action_proof_hash,
        "proof_hash_role": "contributor_action_proof_hash",
        "source_artifact_proof_hash": evidence["evidence_manifest_hash"],
        "validation_status": "pending_classification_evidence_validation",
        "validation_chain_reference": None,
        "ct_reward_calculation_preview_reference_only": reward_preview,
        "ct_minting_status": "blocked_not_validated_not_finalized_not_minted",
        "ct_minted_milli": 0,
        "influence_ledger_write_authorized": False,
        "investment_ledger_write_authorized": False,
        "public_output_authorized": False,
        "nullified": False,
        "nullification_reference": None,
    }
    candidate_hash = _hash(candidate_body)
    authorization_body = {
        "schema_version": "ce_controlled_write_authorization_v1_build004",
        "authorization_id": "CE-WRITE-AUTH-000001",
        "event_id": EVENT_ID,
        "capsule_id": CAPSULE_ID,
        "principal_id": PRINCIPAL_ID,
        "persistence_consent_event_hash": consent_hash,
        "approval_token_hash": hashlib.sha256(approval_token.encode("utf-8")).hexdigest(),
        "authorization_scope": "one_contribution_event_and_one_non_finalized_capsule_candidate_only",
        "forbidden_effects": ["validation_record", "capsule_finalization", "ct_mint", "influence_ledger", "investment_ledger", "public_attribution", "mea_write", "rmc_output_memory", "chroma"],
        "status": "consumed_single_controlled_write",
    }
    authorization_hash = _hash(authorization_body)
    receipt_body = {
        "schema_version": "ce_controlled_write_receipt_v1_build004",
        "write_receipt_id": "CE-WRITE-RECEIPT-000001",
        "build_id": BUILD_ID,
        "event_id": EVENT_ID,
        "event_hash": event_hash,
        "capsule_id": CAPSULE_ID,
        "capsule_top_level_hash": candidate_hash,
        "principal_id": PRINCIPAL_ID,
        "persistence_consent_event_hash": consent_hash,
        "evidence_manifest_hash": evidence["evidence_manifest_hash"],
        "authorization_hash": authorization_hash,
        "status": "committed_pending_validation_not_finalized_not_minted",
        "writes": {"identity_vault_internal_persistence_consent": 1, "identity_vault_audit_event": 1, "contribution_event": 1, "memory_capsule_candidate": 1},
        "blocked_effects": {"validation_record": True, "capsule_finalization": True, "ct_mint": True, "influence_ledger": True, "investment_ledger": True, "public_attribution": True, "mea_state": True, "rmc_output_memory": True, "chroma": True},
    }
    transaction_hash = _hash(receipt_body)
    return {
        "consent_body": consent_body, "consent_hash": consent_hash,
        "resolution_body": resolution_body, "persistence_resolution_hash": persistence_resolution_hash,
        "evidence": evidence, "action_payload": action_payload, "action_payload_hash": action_payload_hash,
        "event_body": event_body, "event_hash": event_hash,
        "candidate_body": candidate_body, "candidate_hash": candidate_hash,
        "authorization_body": authorization_body, "authorization_hash": authorization_hash,
        "receipt_body": receipt_body, "transaction_hash": transaction_hash,
    }


def _create_schema_and_prepare_atomic_databases(paths: Build004Paths) -> None:
    # Schema migration is idempotent and creates no contribution/economic rows. The later
    # identity/core record inserts occur together in one attached-database transaction.
    identity = sqlite3.connect(paths.identity_database)
    core = sqlite3.connect(paths.core_database)
    try:
        for connection in (identity, core):
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchall()
            connection.execute("PRAGMA journal_mode=DELETE").fetchall()
        identity.executescript(paths.identity_sql.read_text(encoding="utf-8"))
        core.executescript(paths.core_sql.read_text(encoding="utf-8"))
        identity.commit()
        core.commit()
    finally:
        identity.close()
        core.close()


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return canonical_json(payload)


def _read_payload(connection: sqlite3.Connection, table: str, key_field: str, key: str, json_field: str) -> dict[str, Any] | None:
    row = connection.execute(f"SELECT {json_field} FROM {table} WHERE {key_field} = ?", (key,)).fetchone()
    return json.loads(row[0]) if row else None


def read_locked_event_state(forge_root: Path, identity_root: Path) -> dict[str, Any]:
    paths = Build004Paths.from_roots(forge_root, identity_root)
    if not paths.identity_database.exists() or not paths.core_database.exists():
        raise ControlledEventWriteError("Build 004 databases are unavailable")
    identity = sqlite3.connect(f"file:{paths.identity_database}?mode=ro&immutable=1", uri=True)
    core = sqlite3.connect(f"file:{paths.core_database}?mode=ro&immutable=1", uri=True)
    try:
        identity.row_factory = sqlite3.Row
        core.row_factory = sqlite3.Row
        tables = {row[0] for row in core.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        identity_tables = {row[0] for row in identity.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "controlled_write_receipts_v1" not in tables or "contributor_internal_persistence_consent_events_v1" not in identity_tables:
            return {"schema_version": "ce_controlled_event_state_v1_build004", "build_id": BUILD_ID, "event_id": EVENT_ID, "persisted": False}
        event = _read_payload(core, "contribution_event_payloads_v1", "event_id", EVENT_ID, "event_payload_json")
        candidate = _read_payload(core, "memory_capsule_candidate_payloads_v1", "capsule_id", CAPSULE_ID, "candidate_payload_json")
        receipt = _read_payload(core, "controlled_write_receipts_v1", "event_id", EVENT_ID, "receipt_json")
        consent = identity.execute("SELECT event_hash, status FROM contributor_internal_persistence_consent_events_v1 WHERE principal_id=? AND event_scope_id=?", (PRINCIPAL_ID, EVENT_ID)).fetchone()
        return {
            "schema_version": "ce_controlled_event_state_v1_build004", "build_id": BUILD_ID, "event_id": EVENT_ID,
            "persisted": bool(event and candidate and receipt and consent), "event": event, "candidate": candidate,
            "write_receipt": receipt, "persistence_consent_event_hash": consent["event_hash"] if consent else None,
            "persistence_consent_status": consent["status"] if consent else None,
        }
    finally:
        identity.close(); core.close()


def apply_locked_event_write(*, forge_root: Path, identity_root: Path, evidence_dir: Path, consent_effective_at_utc: str, persistence_consent_approval_token: str, controlled_write_approval_token: str) -> dict[str, Any]:
    if persistence_consent_approval_token != PERSISTENCE_CONSENT_APPROVAL_TOKEN:
        raise ControlledEventWriteError("Build 004 internal persistence consent approval token mismatch")
    if controlled_write_approval_token != CONTROLLED_WRITE_APPROVAL_TOKEN:
        raise ControlledEventWriteError("Build 004 controlled write approval token mismatch")
    paths = Build004Paths.from_roots(forge_root, identity_root)
    _load_contract(paths)
    evidence = verify_evidence_artifacts(evidence_dir)
    authority = resolve_authority_receipt(paths.identity_root, PRINCIPAL_ID)
    # Build 002 authority resolution uses SQLite context managers without explicit close;
    # collect any released read-only connection before upgrading journal mode for the
    # controlled attached-database transaction.
    gc.collect()
    records = _construct_records(authority, evidence, consent_effective_at_utc, controlled_write_approval_token)
    _create_schema_and_prepare_atomic_databases(paths)

    existing = read_locked_event_state(paths.forge_root, paths.identity_root)
    if existing.get("persisted"):
        if existing["event"].get("event_id") != EVENT_ID or existing["candidate"].get("capsule_id") != CAPSULE_ID:
            raise ControlledEventWriteError("existing Build 004 state conflicts with locked event identity")
        return {"schema_version": "ce_controlled_write_apply_receipt_v1_build004", "build_id": BUILD_ID, "outcome": "existing_locked_event_verified_idempotent_no_write", "state": existing}

    identity = sqlite3.connect(paths.identity_database)
    identity.row_factory = sqlite3.Row
    try:
        identity.execute("PRAGMA foreign_keys=ON")
        identity.execute("PRAGMA synchronous=FULL")
        identity.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchall()
        identity.execute("PRAGMA journal_mode=DELETE").fetchall()
        identity.execute("ATTACH DATABASE ? AS core", (str(paths.core_database),))
        identity.execute("PRAGMA core.journal_mode=DELETE").fetchall()
        identity.execute("BEGIN IMMEDIATE")
        if identity.execute("SELECT 1 FROM core.contribution_events WHERE event_id=?", (EVENT_ID,)).fetchone():
            raise ControlledEventWriteError("CE-EVT-000001 already exists without complete Build 004 state")
        if identity.execute("SELECT 1 FROM contributor_internal_persistence_consent_events_v1 WHERE principal_id=? AND event_scope_id=?", (PRINCIPAL_ID, EVENT_ID)).fetchone():
            raise ControlledEventWriteError("persistence consent exists without complete Build 004 event state")
        consent = records["consent_body"]
        identity.execute(
            "INSERT INTO contributor_internal_persistence_consent_events_v1 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (consent["consent_event_id"], consent["principal_id"], consent["event_scope_id"], consent["event_type"], 1, 1, 0, 0, 0, 0, consent["authorization_basis"], consent["status"], consent["effective_at_utc"], consent["prior_consent_event_hash"], records["consent_hash"], consent["schema_version"]),
        )
        prior_audit = identity.execute("SELECT event_hash FROM contributor_authority_audit_events WHERE principal_id=? ORDER BY recorded_at_utc DESC, audit_event_id DESC LIMIT 1", (PRINCIPAL_ID,)).fetchone()
        audit_body = {
            "schema_version": "identity_vault_contributor_audit_event_v1_build004", "build_id": BUILD_ID,
            "event_type": "internal_event_capsule_persistence_scope_grant", "principal_id": PRINCIPAL_ID,
            "event_scope_id": EVENT_ID, "persistence_consent_event_hash": records["consent_hash"],
            "recorded_at_utc": consent["effective_at_utc"],
        }
        audit_hash = _hash(audit_body)
        identity.execute(
            "INSERT INTO contributor_authority_audit_events (audit_event_id,principal_id,event_type,event_payload_json,prior_audit_event_hash,event_hash,recorded_at_utc,schema_version) VALUES (?,?,?,?,?,?,?,?)",
            ("iv_audit_build004_" + audit_hash[:24], PRINCIPAL_ID, audit_body["event_type"], _canonical_json(audit_body), prior_audit["event_hash"] if prior_audit else None, audit_hash, consent["effective_at_utc"], audit_body["schema_version"]),
        )
        evidence_manifest_id = "CE-EVIDENCE-MANIFEST-000001"
        identity.execute(
            "INSERT INTO core.contribution_event_evidence_manifests_v1 VALUES (?,?,?,?,?)",
            (evidence_manifest_id, EVENT_ID, records["evidence"]["evidence_manifest_hash"], _canonical_json(records["evidence"]), records["evidence"]["schema_version"]),
        )
        auth = records["authorization_body"]
        identity.execute(
            "INSERT INTO core.controlled_write_authorizations_v1 VALUES (?,?,?,?,?,?,?,?,?)",
            (auth["authorization_id"], EVENT_ID, CAPSULE_ID, PRINCIPAL_ID, records["consent_hash"], auth["approval_token_hash"], records["authorization_hash"], auth["status"], auth["schema_version"]),
        )
        event = records["event_body"]
        identity.execute(
            "INSERT INTO core.contribution_events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (EVENT_ID, records["event_hash"], PRINCIPAL_ID, records["persistence_resolution_hash"], records["event_body"]["contributor_action_proof_hash"], records["action_payload_hash"], records["evidence"]["evidence_manifest_hash"], "BLD", "direct", "standard", ACTION_COMPLETED_AT_UTC, event["event_status"], event["schema_version"]),
        )
        identity.execute("INSERT INTO core.contribution_event_payloads_v1 VALUES (?,?,?,?)", (EVENT_ID, records["event_hash"], _canonical_json(event), event["schema_version"]))
        candidate = {**records["candidate_body"], "top_level_hash": records["candidate_hash"]}
        identity.execute(
            "INSERT INTO core.memory_capsule_candidates VALUES (?,?,?,?,?,?,?,?,?,?)",
            (CAPSULE_ID, records["candidate_hash"], records["event_hash"], PRINCIPAL_ID, event["contributor_action_proof_hash"], records["evidence"]["evidence_manifest_hash"], candidate["validation_status"], 0, candidate["capsule_status"], candidate["schema_version"]),
        )
        identity.execute("INSERT INTO core.memory_capsule_candidate_payloads_v1 VALUES (?,?,?,?)", (CAPSULE_ID, records["candidate_hash"], _canonical_json(candidate), candidate["schema_version"]))
        receipt = records["receipt_body"]
        identity.execute(
            "INSERT INTO core.controlled_write_receipts_v1 VALUES (?,?,?,?,?,?,?,?)",
            (receipt["write_receipt_id"], EVENT_ID, CAPSULE_ID, PRINCIPAL_ID, records["transaction_hash"], _canonical_json({**receipt, "transaction_hash": records["transaction_hash"]}), receipt["status"], receipt["schema_version"]),
        )
        if identity.execute("SELECT COUNT(*) FROM core.capsule_validation_records").fetchone()[0] != 0 or identity.execute("SELECT COUNT(*) FROM core.ct_mint_events").fetchone()[0] != 0:
            raise ControlledEventWriteError("forbidden core records detected during controlled write")
        identity.commit()
    except Exception:
        identity.rollback()
        raise
    finally:
        try:
            identity.execute("DETACH DATABASE core")
        except sqlite3.Error:
            pass
        identity.close()
    for database in (paths.identity_database, paths.core_database):
        fd = os.open(database, os.O_RDONLY)
        try: os.fsync(fd)
        finally: os.close(fd)
    state = read_locked_event_state(paths.forge_root, paths.identity_root)
    if not state.get("persisted"):
        raise ControlledEventWriteError("controlled write committed but readback verification failed")
    return {"schema_version": "ce_controlled_write_apply_receipt_v1_build004", "build_id": BUILD_ID, "outcome": "ce_evt_000001_and_candidate_committed", "transaction_hash": records["transaction_hash"], "state": state}
