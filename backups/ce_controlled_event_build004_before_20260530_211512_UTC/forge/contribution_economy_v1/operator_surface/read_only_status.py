"""Read-only Contribution Economy operator status surface for Forge UI.

CE-OPERATOR-SURFACE-BUILD-003 exposes only a safe visibility adapter over the
already installed Contribution Economy / Identity Vault / MEA boundaries.

This module:
- opens SQLite databases in read-only, query-only mode;
- returns counts and deny-gate states, never private identity rows;
- projects the existing MEA compatibility preview into a safe operator summary;
- creates no Contribution Events, capsules, validation rows, CT, or ledger rows;
- performs no file, database, network, shell, model, or Chroma writes.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Mapping

from ..capsules.current_mea_adapter import build_current_committed_mea_capsule_preview
from ..gates.economic_gates import gate_manifest
from ..integrated_core.policy import BUILD_ID as INTEGRATED_CORE_BUILD_ID

BUILD_ID = "CE-OPERATOR-SURFACE-BUILD-003"
STATUS_SCHEMA_VERSION = "ce_operator_surface_status_v1_build003"
MEA_PREVIEW_SCHEMA_VERSION = "ce_operator_surface_mea_preview_v1_build003"
API_CONTRACT = "forge_operator_console_api_v1"

_IDENTITY_TABLES = (
    "contributor_principals",
    "contributor_consent_events",
    "contributor_authority_audit_events",
    "contributor_principal_status_events_v2",
    "contributor_consent_events_v2",
)
_LEDGER_DATA_TABLES = (
    "influence_live_entries",
    "influence_user_entries",
    "influence_archive_entries",
    "investment_live_entries",
    "investment_user_entries",
    "investment_archive_entries",
)
_CORE_DATA_TABLES = (
    "contribution_events",
    "memory_capsule_candidates",
    "capsule_validation_records",
    "capsule_finalization_receipts",
    "ct_mint_events",
    "nullification_correction_events",
)


class OperatorSurfaceReadError(RuntimeError):
    """Raised when a read-only operator status cannot be verified safely."""


def _read_only_connection(path: Path) -> sqlite3.Connection:
    database = Path(path).resolve()
    if not database.is_file():
        raise OperatorSurfaceReadError(f"required operator-visible database is missing: {database.name}")
    # Build 003 reads only checkpointed primary-database state. ``immutable=1`` prevents
    # SQLite from creating WAL/SHM sidecars while the operator surface is observing state.
    # Any later authorized writer must checkpoint committed pages before this surface is
    # permitted to represent the newly committed state.
    connection = sqlite3.connect(f"file:{database}?mode=ro&immutable=1", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_multiuser_authority_schema_read_only(identity_root: Path) -> dict[str, Any]:
    """Verify the Build 002 Identity Vault bridge without permitting SQLite sidecar writes."""
    root = Path(identity_root).resolve()
    database = root / "data" / "identity_vault.db"
    schema_extension = root / "schema_extensions" / "contribution_economy_multiuser_authority_v2.sql"
    service_contract = root / "service_contracts" / "contribution_economy_integrated_multiuser_core_build002.v1.json"
    if not service_contract.is_file() or service_contract.is_symlink():
        raise OperatorSurfaceReadError("required Identity Vault service contract is missing")
    if not schema_extension.is_file() or schema_extension.is_symlink():
        raise OperatorSurfaceReadError("required Identity Vault schema extension is missing")
    contract = json.loads(service_contract.read_text(encoding="utf-8"))
    if contract.get("schema_version") != "ce_integrated_multiuser_identity_vault_service_contract_v1_build002":
        raise OperatorSurfaceReadError("Identity Vault service contract schema mismatch")
    if contract.get("build_id") != INTEGRATED_CORE_BUILD_ID:
        raise OperatorSurfaceReadError("Identity Vault service contract build mismatch")
    if contract.get("schema_extension_sha256") != _sha256_file(schema_extension):
        raise OperatorSurfaceReadError("Identity Vault schema extension checksum mismatch")
    if contract.get("raw_private_identity_export_allowed") is not False:
        raise OperatorSurfaceReadError("Identity Vault service contract does not prohibit private identity export")
    if contract.get("live_economic_consent_activation_allowed") is not False:
        raise OperatorSurfaceReadError("Identity Vault service contract improperly authorizes economic consent")
    required_tables = {"contributor_principal_status_events_v2", "contributor_consent_events_v2"}
    required_triggers = {
        "block_update_contributor_principal_status_events_v2",
        "block_delete_contributor_principal_status_events_v2",
        "block_update_contributor_consent_events_v2",
        "block_delete_contributor_consent_events_v2",
    }
    with _read_only_connection(database) as connection:
        tables = {str(row[0]) for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        triggers = {str(row[0]) for row in connection.execute("SELECT name FROM sqlite_master WHERE type='trigger'").fetchall()}
        counts = {table: int(connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]) for table in required_tables if table in tables}
    missing_tables = sorted(required_tables - tables)
    missing_triggers = sorted(required_triggers - triggers)
    return {
        "schema_version": "identity_vault_multiuser_schema_verification_receipt_v1_build002",
        "build_id": INTEGRATED_CORE_BUILD_ID,
        "verified": not missing_tables and not missing_triggers,
        "missing_tables": missing_tables,
        "missing_triggers": missing_triggers,
        "v2_row_counts": counts,
        "read_consistency_model": "checkpointed_primary_database_immutable_read",
        "requires_writer_checkpoint_before_visibility": True,
    }


def _safe_table_counts(path: Path, tables: Iterable[str]) -> dict[str, Any]:
    required = tuple(tables)
    with _read_only_connection(path) as connection:
        existing = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        missing = sorted(set(required) - existing)
        counts = {
            table: int(connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])
            for table in required
            if table in existing
        }
    return {
        "required_tables_present": not missing,
        "missing_tables": missing,
        "row_counts": counts,
    }


def _identity_authority_summary(identity_database: Path) -> dict[str, Any]:
    counts = _safe_table_counts(identity_database, _IDENTITY_TABLES)
    with _read_only_connection(identity_database) as connection:
        principal_total = int(connection.execute("SELECT COUNT(*) FROM contributor_principals").fetchone()[0])
        private_only = int(
            connection.execute(
                "SELECT COUNT(*) FROM contributor_principals WHERE disclosure_class = ?",
                ("private_identity_vault_only",),
            ).fetchone()[0]
        )
        public_scope_grants = int(
            connection.execute(
                "SELECT COUNT(*) FROM contributor_consent_events WHERE public_display_authorized != 0"
            ).fetchone()[0]
        )
        economic_scope_grants = int(
            connection.execute(
                "SELECT COUNT(*) FROM contributor_consent_events "
                "WHERE economic_processing_authorized != 0 OR ct_minting_authorized != 0 "
                "OR investment_processing_authorized != 0"
            ).fetchone()[0]
        )
        if "contributor_consent_events_v2" in counts["row_counts"]:
            public_scope_grants += int(
                connection.execute(
                    "SELECT COUNT(*) FROM contributor_consent_events_v2 WHERE public_display_authorized != 0"
                ).fetchone()[0]
            )
            economic_scope_grants += int(
                connection.execute(
                    "SELECT COUNT(*) FROM contributor_consent_events_v2 "
                    "WHERE economic_processing_authorized != 0 OR ct_minting_authorized != 0 "
                    "OR investment_processing_authorized != 0"
                ).fetchone()[0]
            )
    return {
        "registered_principal_count": principal_total,
        "private_identity_vault_only_principal_count": private_only,
        "all_principals_private_only": principal_total == private_only,
        "public_display_authorization_event_count": public_scope_grants,
        "economic_authorization_event_count": economic_scope_grants,
        "raw_private_identity_exported": False,
        "tables": counts,
    }


def _ledger_summary(ledger_database: Path) -> dict[str, Any]:
    counts = _safe_table_counts(ledger_database, _LEDGER_DATA_TABLES)
    influence_counts = {
        key: value for key, value in counts["row_counts"].items()
        if key.startswith("influence_")
    }
    investment_counts = {
        key: value for key, value in counts["row_counts"].items()
        if key.startswith("investment_")
    }
    return {
        "tables": counts,
        "influence_row_counts": influence_counts,
        "investment_row_counts": investment_counts,
        "influence_total_entries": sum(influence_counts.values()),
        "investment_total_entries": sum(investment_counts.values()),
        "ct_mint_records_created_by_investment": False,
        "money_creates_ct": False,
        "ledgers_permanently_separate": True,
    }


def _core_store_summary(core_database: Path) -> dict[str, Any]:
    counts = _safe_table_counts(core_database, _CORE_DATA_TABLES)
    with _read_only_connection(core_database) as connection:
        metadata_row = connection.execute(
            "SELECT live_event_persistence_enabled, capsule_finalization_enabled, "
            "ct_minting_enabled, ledger_write_enabled "
            "FROM core_store_metadata WHERE singleton_id=1"
        ).fetchone()
    metadata = dict(metadata_row) if metadata_row else {}
    return {
        "tables": counts,
        "row_counts": counts["row_counts"],
        "total_governed_records": sum(counts["row_counts"].values()),
        "live_event_persistence_enabled": bool(metadata.get("live_event_persistence_enabled", False)),
        "capsule_finalization_enabled": bool(metadata.get("capsule_finalization_enabled", False)),
        "ct_minting_enabled": bool(metadata.get("ct_minting_enabled", False)),
        "ledger_write_enabled": bool(metadata.get("ledger_write_enabled", False)),
    }


def _read_only_boundary() -> dict[str, Any]:
    return {
        "read_only": True,
        "ui_is_authority": False,
        "forge_governs": True,
        "identity_vault_authorizes": True,
        "executes_command": False,
        "executes_shell": False,
        "calls_llm": False,
        "performs_network_io": False,
        "writes_files": False,
        "writes_identity_vault": False,
        "writes_contribution_events": False,
        "writes_memory_capsules": False,
        "writes_validation_records": False,
        "finalizes_capsules": False,
        "mints_ct": False,
        "writes_influence_ledger": False,
        "writes_investment_ledger": False,
        "writes_mea_state": False,
        "writes_rmc_output_memory": False,
        "writes_chroma": False,
        "public_identity_disclosure": False,
    }


def build_operator_status(*, forge_root: Path, identity_vault_root: Path) -> dict[str, Any]:
    """Return the safe, read-only integrated Contribution Economy operator status."""
    forge = Path(forge_root).resolve()
    identity_root = Path(identity_vault_root).resolve()
    identity_database = identity_root / "data" / "identity_vault.db"
    ledger_database = forge / "memory" / "contribution_economy_v1" / "ledgers" / "contribution_ledgers.db"
    core_database = forge / "memory" / "contribution_economy_v1" / "core" / "contribution_economy_core.db"

    authority_schema = _verify_multiuser_authority_schema_read_only(identity_root)
    identity = _identity_authority_summary(identity_database)
    ledgers = _ledger_summary(ledger_database)
    core = _core_store_summary(core_database)
    gates = gate_manifest()

    healthy = (
        authority_schema.get("verified") is True
        and identity["tables"]["required_tables_present"]
        and identity["all_principals_private_only"]
        and identity["public_display_authorization_event_count"] == 0
        and identity["economic_authorization_event_count"] == 0
        and ledgers["tables"]["required_tables_present"]
        and core["tables"]["required_tables_present"]
        and not core["live_event_persistence_enabled"]
        and not core["capsule_finalization_enabled"]
        and not core["ct_minting_enabled"]
        and not core["ledger_write_enabled"]
        and gates.get("capsule_finalization_enabled") is False
        and gates.get("ct_minting_enabled") is False
        and gates.get("influence_ledger_writes_enabled") is False
        and gates.get("investment_ledger_writes_enabled") is False
    )

    return {
        "status": "OK" if healthy else "ATTENTION_REQUIRED",
        "schema_version": STATUS_SCHEMA_VERSION,
        "api_contract": API_CONTRACT,
        "endpoint": "/api/contribution-economy/status",
        "build_id": BUILD_ID,
        "read_only": True,
        "read_consistency": {
            "model": "checkpointed_primary_database_immutable_read",
            "creates_sqlite_sidecars": False,
            "requires_writer_checkpoint_before_visibility": True,
        },
        "installed_layers": {
            "contract_kernel": "Patch 300 — deterministic contract and milli-CT policy",
            "identity_and_dual_ledger_foundation": "CE-IV-LEDGER-CAPSULE-BUILD-001",
            "integrated_multiuser_core": "CE-INTEGRATED-MULTIUSER-CORE-BUILD-002",
            "operator_surface": BUILD_ID,
        },
        "identity_authority": identity,
        "identity_authority_schema": {
            "verified": authority_schema.get("verified") is True,
            "v2_row_counts": authority_schema.get("v2_row_counts", {}),
            "missing_tables": authority_schema.get("missing_tables", []),
            "missing_triggers": authority_schema.get("missing_triggers", []),
        },
        "integrated_core": core,
        "ledgers": ledgers,
        "economic_gates": gates,
        "source_artifact_bridge": {
            "mea_capsule_preview_endpoint": "/api/contribution-economy/mea-capsule-preview",
            "mea_artifact_is_contribution_action_proof": False,
            "mea_hypothesis_is_validated_contribution": False,
        },
        "operator_visibility": {
            "read_only_routes_enabled": True,
            "read_only_routes": [
                "/api/contribution-economy/status",
                "/api/contribution-economy/mea-capsule-preview",
            ],
            "contribution_mutation_routes_enabled": False,
            "build002_core_mutation_routes_remain_disabled": True,
            "visibility_activation_scope": "Build 003 read-only operator visibility only",
        },
        "boundary": _read_only_boundary(),
    }


def build_mea_capsule_preview_status(*, forge_root: Path) -> dict[str, Any]:
    """Return a reduced safe view of the existing MEA compatibility preview."""
    adapter = build_current_committed_mea_capsule_preview(forge_root=Path(forge_root).resolve())
    preview = adapter["capsule_compatibility_preview"]
    return {
        "status": "OK",
        "schema_version": MEA_PREVIEW_SCHEMA_VERSION,
        "api_contract": API_CONTRACT,
        "endpoint": "/api/contribution-economy/mea-capsule-preview",
        "build_id": BUILD_ID,
        "read_only": True,
        "preview": {
            "capsule_id": preview["capsule_id"],
            "capsule_status": preview["capsule_status"],
            "claim_status": preview["claim_status"],
            "finalized": preview["finalized"],
            "source_system": preview["source_system"],
            "source_manifest_hash": preview["source_manifest_hash"],
            "seal_packet_hash": preview["seal_packet_hash"],
            "source_artifact_proof_hash": preview["source_artifact_proof_hash"],
            "proof_hash": preview["proof_hash"],
            "proof_hash_role": preview["proof_hash_role"],
            "top_level_hash": preview["top_level_hash"],
            "contributor_binding_status": preview["contributor_binding_status"],
            "contributors_count": len(preview["contributors"]),
            "breath_validation_status": preview["breath_validation"]["status"],
            "ct_minting_status": preview["ct_minting_status"],
            "persistence_authorized": preview["persistence_authorized"],
            "influence_ledger_write_authorized": preview["influence_ledger_write_authorized"],
            "investment_ledger_write_authorized": preview["investment_ledger_write_authorized"],
            "public_output_authorized": preview["public_output_authorized"],
            "integrity_rule": preview["integrity_rule"],
        },
        "boundary": _read_only_boundary(),
    }
