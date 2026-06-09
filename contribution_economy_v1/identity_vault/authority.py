"""Controlled contributor-authority extension for the canonical AI.Web Identity Vault.

This module is intentionally separate from the older read-only Forge adapter and from the
legacy Identity Vault ``profiles`` implementation.  It targets only the accepted canonical
SQLite database containing ``user_profiles`` and ``agent_profiles``.  It binds the already
existing inactive Nic profile to an append-only contributor principal and limited internal
consent record.  It never updates the existing user profile or any agent profile.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ..contracts.canonical_json import assert_utc_timestamp_z, canonical_json
from ..contracts.enums import ContractValueError
from ..contracts.identity_reference_schema import reject_raw_private_identity

BUILD_ID = "CE-IV-LEDGER-CAPSULE-BUILD-001"
IDENTITY_AUTHORITY_SCHEMA_VERSION = "identity_vault_contributor_authority_v1_build001"
CONSENT_EVENT_SCHEMA_VERSION = "identity_vault_contributor_consent_event_v1_build001"
AUDIT_EVENT_SCHEMA_VERSION = "identity_vault_contributor_authority_audit_event_v1_build001"
APPLY_APPROVAL_TOKEN = "APPROVE_CE_IDENTITY_VAULT_AND_DUAL_LEDGER_FOUNDATION_BUILD001"
EXPECTED_USER_ID = "nic_bogaert"
EXPECTED_EXISTING_PROFILE_HASH = "59412c799a127fbf78ea4abdba241b2cbadf5cad36e7adf7c13924f1507d32f0"
EXPECTED_EXISTING_IS_ACTIVE = 0
EXPECTED_PRINCIPAL_ID = "ivp_nic_bogaert_contribution_owner_v1"
EXPECTED_CONSENT_RECORD_ID = "iv_consent_nic_bogaert_contribution_internal_v1"
EXPECTED_CONSENT_EVENT_ID = "iv_consent_event_nic_bogaert_initial_internal_v1"
EXPECTED_AUDIT_EVENT_ID = "iv_audit_nic_bogaert_contribution_authority_registration_v1"
EXPECTED_DISCLOSURE_CLASS = "private_identity_vault_only"
HASH_ALGORITHM = "sha256"
_EXPECTED_SCOPE = {
    "local_identity_storage_authorized": True,
    "internal_attribution_reference_authorized": True,
    "capsule_candidate_reference_authorized": True,
    "public_display_authorized": False,
    "portability_authorized": False,
    "economic_processing_authorized": False,
    "ct_minting_authorized": False,
    "investment_processing_authorized": False,
}
_EXPECTED_TRIGGERS = {
    "block_update_contributor_principals",
    "block_delete_contributor_principals",
    "block_update_contributor_consent_events",
    "block_delete_contributor_consent_events",
    "block_update_contributor_authority_audit_events",
    "block_delete_contributor_authority_audit_events",
}


class IdentityAuthorityError(RuntimeError):
    """Raised when the protected Identity Vault contributor boundary cannot be proven."""


@dataclass(frozen=True)
class AuthorityPaths:
    database: Path
    contract: Path
    schema_extension: Path
    authority_manifest: Path

    @classmethod
    def from_identity_vault_root(cls, root: Path) -> "AuthorityPaths":
        root = Path(root).resolve()
        return cls(
            database=root / "data" / "identity_vault.db",
            contract=root / "service_contracts" / "contribution_economy_contributor_authority_contract.v1.json",
            schema_extension=root / "schema_extensions" / "contribution_economy_identity_authority_v1.sql",
            authority_manifest=root / "contributor_authority" / "nic_bogaert_contributor_authority_manifest.v1.json",
        )


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _hash_payload(payload: Mapping[str, Any]) -> str:
    return _sha256_bytes(canonical_json(payload).encode("utf-8"))


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise IdentityAuthorityError(f"required {label} file is missing or symlinked: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IdentityAuthorityError(f"required {label} file is unreadable: {path}") from exc
    if not isinstance(value, dict):
        raise IdentityAuthorityError(f"required {label} file must contain one JSON object")
    return value


def _validate_contract(paths: AuthorityPaths) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = _load_json(paths.contract, "Identity Vault contributor authority contract")
    manifest = _load_json(paths.authority_manifest, "Identity Vault contributor authority manifest")
    if contract.get("build_id") != BUILD_ID:
        raise IdentityAuthorityError("Identity Vault contributor contract build_id mismatch")
    if contract.get("approval_token") != APPLY_APPROVAL_TOKEN:
        raise IdentityAuthorityError("Identity Vault contributor contract approval-token declaration mismatch")
    expected_paths = {
        "canonical_database_path": str(paths.database),
        "schema_extension_path": str(paths.schema_extension),
        "authority_manifest_path": str(paths.authority_manifest),
    }
    for field, expected in expected_paths.items():
        if contract.get(field) != expected:
            raise IdentityAuthorityError(f"Identity Vault contributor contract {field} does not bind this install root")
    if not paths.database.is_file() or paths.database.is_symlink():
        raise IdentityAuthorityError("canonical Identity Vault database is missing or symlinked")
    if _sha256_file(paths.schema_extension) != contract.get("schema_extension_sha256"):
        raise IdentityAuthorityError("Identity Vault schema extension hash mismatch")
    if _sha256_file(paths.authority_manifest) != contract.get("authority_manifest_sha256"):
        raise IdentityAuthorityError("Identity Vault authority manifest hash mismatch")
    binding = contract.get("expected_existing_profile_binding")
    if not isinstance(binding, dict) or binding != {
        "is_active": EXPECTED_EXISTING_IS_ACTIVE,
        "must_not_be_modified": True,
        "profile_hash": EXPECTED_EXISTING_PROFILE_HASH,
        "user_id": EXPECTED_USER_ID,
    }:
        raise IdentityAuthorityError("existing Nic Identity Vault profile binding is not the accepted immutable binding")
    if contract.get("allowed_consent_scope") != _EXPECTED_SCOPE:
        raise IdentityAuthorityError("Identity Vault contributor contract consent scope differs from approved limited scope")
    if manifest.get("principal_id") != EXPECTED_PRINCIPAL_ID or manifest.get("user_profile_reference") != EXPECTED_USER_ID:
        raise IdentityAuthorityError("private authority manifest does not bind the approved Nic principal")
    if manifest.get("disclosure_class") != EXPECTED_DISCLOSURE_CLASS:
        raise IdentityAuthorityError("private authority manifest disclosure class must remain private")
    if manifest.get("authority_status") != "internal_contribution_authority_active":
        raise IdentityAuthorityError("private authority manifest authority state is not the approved internal state")
    assert_utc_timestamp_z(manifest.get("issued_at_utc"), "issued_at_utc")
    scope = manifest.get("initial_consent_scope")
    if not isinstance(scope, dict):
        raise IdentityAuthorityError("private authority manifest must contain the initial consent scope")
    for key, expected in _EXPECTED_SCOPE.items():
        if scope.get(key) is not expected:
            raise IdentityAuthorityError(f"private authority manifest consent value is not approved: {key}")
    if scope.get("consent_record_id") != EXPECTED_CONSENT_RECORD_ID or scope.get("consent_event_id") != EXPECTED_CONSENT_EVENT_ID:
        raise IdentityAuthorityError("private authority manifest consent identifiers are not approved")
    if scope.get("status") != "active_limited_internal_consent":
        raise IdentityAuthorityError("private authority manifest consent status is not the approved limited state")
    privacy = manifest.get("privacy_boundary")
    if not isinstance(privacy, dict) or privacy.get("raw_private_identity_may_leave_identity_vault") is not False:
        raise IdentityAuthorityError("private authority manifest must prohibit raw identity from leaving Identity Vault")
    if privacy.get("public_capsule_identity_disclosure_authorized") is not False:
        raise IdentityAuthorityError("private authority manifest must prohibit public capsule identity disclosure")
    return contract, manifest


def _connect(database: Path, *, read_only: bool) -> sqlite3.Connection:
    if read_only:
        connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    else:
        connection = sqlite3.connect(str(database))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    if not read_only:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = FULL")
        connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def _get_exact_existing_user_row(connection: sqlite3.Connection) -> dict[str, Any]:
    required_table = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='user_profiles'"
    ).fetchone()
    if required_table is None:
        raise IdentityAuthorityError("canonical user_profiles table does not exist")
    row = connection.execute(
        "SELECT user_id, profile_hash, is_active FROM user_profiles WHERE user_id = ?",
        (EXPECTED_USER_ID,),
    ).fetchone()
    if row is None:
        raise IdentityAuthorityError("existing nic_bogaert Identity Vault profile does not exist")
    found = dict(row)
    if found != {
        "user_id": EXPECTED_USER_ID,
        "profile_hash": EXPECTED_EXISTING_PROFILE_HASH,
        "is_active": EXPECTED_EXISTING_IS_ACTIVE,
    }:
        raise IdentityAuthorityError("existing nic_bogaert Identity Vault profile changed from the accepted inactive binding")
    return found


def _principal_row(manifest_hash: str, manifest: Mapping[str, Any]) -> dict[str, Any]:
    body = {
        "schema_version": IDENTITY_AUTHORITY_SCHEMA_VERSION,
        "principal_id": EXPECTED_PRINCIPAL_ID,
        "user_id": EXPECTED_USER_ID,
        "principal_type": "human_owner_builder",
        "authority_status": "internal_contribution_authority_active",
        "disclosure_class": EXPECTED_DISCLOSURE_CLASS,
        "pseudonymous_alias_id": manifest.get("pseudonymous_alias_id"),
        "source_user_profile_hash": EXPECTED_EXISTING_PROFILE_HASH,
        "authority_manifest_relative_path": "contributor_authority/nic_bogaert_contributor_authority_manifest.v1.json",
        "authority_manifest_hash": manifest_hash,
        "created_at_utc": manifest["issued_at_utc"],
    }
    identity_proof_payload = {
        "schema_version": "identity_vault_contributor_identity_proof_v1_build001",
        "principal_id": body["principal_id"],
        "user_id": body["user_id"],
        "source_user_profile_hash": body["source_user_profile_hash"],
        "authority_manifest_hash": manifest_hash,
        "disclosure_class": body["disclosure_class"],
    }
    body["identity_proof_hash"] = _hash_payload(identity_proof_payload)
    body["record_hash"] = _hash_payload(body)
    return body


def _consent_row(principal: Mapping[str, Any], manifest: Mapping[str, Any]) -> dict[str, Any]:
    scope = manifest["initial_consent_scope"]
    body = {
        "schema_version": CONSENT_EVENT_SCHEMA_VERSION,
        "consent_event_id": EXPECTED_CONSENT_EVENT_ID,
        "consent_record_id": EXPECTED_CONSENT_RECORD_ID,
        "principal_id": EXPECTED_PRINCIPAL_ID,
        "event_type": "initial_scope_grant",
        "local_identity_storage_authorized": 1,
        "internal_attribution_reference_authorized": 1,
        "capsule_candidate_reference_authorized": 1,
        "public_display_authorized": 0,
        "portability_authorized": 0,
        "economic_processing_authorized": 0,
        "ct_minting_authorized": 0,
        "investment_processing_authorized": 0,
        "authorization_basis": manifest["authorization_basis"],
        "status": scope["status"],
        "effective_at_utc": manifest["issued_at_utc"],
        "prior_consent_event_hash": None,
        "principal_record_hash": principal["record_hash"],
    }
    body["event_hash"] = _hash_payload(body)
    body.pop("principal_record_hash")
    return body


def _audit_row(principal: Mapping[str, Any], consent: Mapping[str, Any], manifest: Mapping[str, Any]) -> dict[str, Any]:
    event_payload = {
        "schema_version": "identity_vault_contributor_authority_audit_payload_v1_build001",
        "build_id": BUILD_ID,
        "principal_id": EXPECTED_PRINCIPAL_ID,
        "principal_record_hash": principal["record_hash"],
        "consent_event_hash": consent["event_hash"],
        "source_user_profile_hash": EXPECTED_EXISTING_PROFILE_HASH,
        "identity_vault_profile_modified": False,
        "agent_profile_modified": False,
        "public_disclosure_authorized": False,
        "economic_processing_authorized": False,
        "ct_minting_authorized": False,
        "investment_processing_authorized": False,
        "reason": manifest["authorization_basis"],
    }
    event_payload_json = canonical_json(event_payload)
    body = {
        "schema_version": AUDIT_EVENT_SCHEMA_VERSION,
        "audit_event_id": EXPECTED_AUDIT_EVENT_ID,
        "principal_id": EXPECTED_PRINCIPAL_ID,
        "event_type": "contributor_authority_registered_limited_internal_consent",
        "event_payload_json": event_payload_json,
        "prior_audit_event_hash": None,
        "recorded_at_utc": manifest["issued_at_utc"],
    }
    body["event_hash"] = _hash_payload(body)
    return body


def _row_for_sql(row: Mapping[str, Any], ordered_fields: tuple[str, ...]) -> tuple[Any, ...]:
    return tuple(row.get(field) for field in ordered_fields)


def _assert_existing_or_insert(
    connection: sqlite3.Connection,
    *,
    table: str,
    id_column: str,
    id_value: str,
    expected: Mapping[str, Any],
    fields: tuple[str, ...],
) -> str:
    current = connection.execute(
        f"SELECT {', '.join(fields)} FROM {table} WHERE {id_column} = ?", (id_value,)
    ).fetchone()
    if current is not None:
        actual = {field: current[index] for index, field in enumerate(fields)}
        if actual != {field: expected.get(field) for field in fields}:
            raise IdentityAuthorityError(f"existing append-only {table} record conflicts with approved identity authority record")
        return "existing_verified_idempotent_no_write"
    placeholders = ", ".join("?" for _ in fields)
    connection.execute(
        f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})",
        _row_for_sql(expected, fields),
    )
    return "inserted"


def apply_nic_contributor_authority(
    identity_vault_root: Path,
    *,
    approval_token: str,
) -> dict[str, Any]:
    """Apply exactly one explicitly approved limited contributor-authority binding for Nic."""
    if approval_token != APPLY_APPROVAL_TOKEN:
        raise IdentityAuthorityError("explicit Identity Vault contributor-authority approval token is required")
    paths = AuthorityPaths.from_identity_vault_root(identity_vault_root)
    _contract, manifest = _validate_contract(paths)
    schema_text = paths.schema_extension.read_text(encoding="utf-8")
    manifest_hash = _sha256_file(paths.authority_manifest)
    principal = _principal_row(manifest_hash, manifest)
    consent = _consent_row(principal, manifest)
    audit = _audit_row(principal, consent, manifest)
    principal_fields = (
        "principal_id", "user_id", "principal_type", "authority_status", "disclosure_class",
        "pseudonymous_alias_id", "source_user_profile_hash", "authority_manifest_relative_path",
        "authority_manifest_hash", "identity_proof_hash", "schema_version", "created_at_utc", "record_hash",
    )
    consent_fields = (
        "consent_event_id", "consent_record_id", "principal_id", "event_type",
        "local_identity_storage_authorized", "internal_attribution_reference_authorized",
        "capsule_candidate_reference_authorized", "public_display_authorized", "portability_authorized",
        "economic_processing_authorized", "ct_minting_authorized", "investment_processing_authorized",
        "authorization_basis", "status", "effective_at_utc", "prior_consent_event_hash", "event_hash", "schema_version",
    )
    audit_fields = (
        "audit_event_id", "principal_id", "event_type", "event_payload_json", "prior_audit_event_hash",
        "event_hash", "recorded_at_utc", "schema_version",
    )
    connection = _connect(paths.database, read_only=False)
    try:
        _get_exact_existing_user_row(connection)
        connection.executescript("BEGIN IMMEDIATE;\n" + schema_text + "\nCOMMIT;")
        connection.execute("BEGIN IMMEDIATE")
        outcomes = {
            "principal": _assert_existing_or_insert(
                connection, table="contributor_principals", id_column="principal_id",
                id_value=EXPECTED_PRINCIPAL_ID, expected=principal, fields=principal_fields,
            ),
            "consent": _assert_existing_or_insert(
                connection, table="contributor_consent_events", id_column="consent_event_id",
                id_value=EXPECTED_CONSENT_EVENT_ID, expected=consent, fields=consent_fields,
            ),
            "audit": _assert_existing_or_insert(
                connection, table="contributor_authority_audit_events", id_column="audit_event_id",
                id_value=EXPECTED_AUDIT_EVENT_ID, expected=audit, fields=audit_fields,
            ),
        }
        connection.commit()
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.close()
    verification = verify_nic_contributor_authority(identity_vault_root)
    return {
        "schema_version": "identity_vault_contributor_authority_apply_receipt_v1_build001",
        "build_id": BUILD_ID,
        "operation": "controlled_identity_vault_contributor_authority_apply",
        "outcomes": outcomes,
        "principal_id": EXPECTED_PRINCIPAL_ID,
        "consent_record_id": EXPECTED_CONSENT_RECORD_ID,
        "consent_event_id": EXPECTED_CONSENT_EVENT_ID,
        "audit_event_id": EXPECTED_AUDIT_EVENT_ID,
        "existing_user_profile_modified": False,
        "agent_profiles_modified": False,
        "public_disclosure_authorized": False,
        "economic_processing_authorized": False,
        "ct_minting_authorized": False,
        "verification": verification,
    }


def verify_nic_contributor_authority(identity_vault_root: Path) -> dict[str, Any]:
    """Read back and verify the append-only contributor authority without exposing private profile data."""
    paths = AuthorityPaths.from_identity_vault_root(identity_vault_root)
    _contract, manifest = _validate_contract(paths)
    expected_principal = _principal_row(_sha256_file(paths.authority_manifest), manifest)
    expected_consent = _consent_row(expected_principal, manifest)
    expected_audit = _audit_row(expected_principal, expected_consent, manifest)
    connection = _connect(paths.database, read_only=True)
    try:
        existing_user = _get_exact_existing_user_row(connection)
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
        expected_tables = {"contributor_principals", "contributor_consent_events", "contributor_authority_audit_events"}
        if not expected_tables.issubset(tables):
            raise IdentityAuthorityError("contributor authority tables are not fully installed")
        triggers = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='trigger'").fetchall()
        }
        if not _EXPECTED_TRIGGERS.issubset(triggers):
            raise IdentityAuthorityError("append-only contributor authority triggers are not fully installed")
        checks = (
            ("contributor_principals", "principal_id", EXPECTED_PRINCIPAL_ID, expected_principal),
            ("contributor_consent_events", "consent_event_id", EXPECTED_CONSENT_EVENT_ID, expected_consent),
            ("contributor_authority_audit_events", "audit_event_id", EXPECTED_AUDIT_EVENT_ID, expected_audit),
        )
        for table, id_column, id_value, expected in checks:
            row = connection.execute(f"SELECT * FROM {table} WHERE {id_column} = ?", (id_value,)).fetchone()
            if row is None:
                raise IdentityAuthorityError(f"required append-only record is missing: {table}")
            actual = dict(row)
            for key, value in expected.items():
                if actual.get(key) != value:
                    raise IdentityAuthorityError(f"approved append-only record differs from expected record: {table}.{key}")
        consent_count = connection.execute(
            "SELECT COUNT(*) FROM contributor_consent_events WHERE principal_id = ?", (EXPECTED_PRINCIPAL_ID,)
        ).fetchone()[0]
        principal_count = connection.execute(
            "SELECT COUNT(*) FROM contributor_principals WHERE principal_id = ?", (EXPECTED_PRINCIPAL_ID,)
        ).fetchone()[0]
    finally:
        connection.close()
    result = {
        "schema_version": "identity_vault_contributor_authority_verification_v1_build001",
        "build_id": BUILD_ID,
        "verified": True,
        "principal_id": EXPECTED_PRINCIPAL_ID,
        "user_profile_reference": EXPECTED_USER_ID,
        "existing_user_profile_hash": existing_user["profile_hash"],
        "existing_user_profile_is_active": bool(existing_user["is_active"]),
        "existing_user_profile_modified": False,
        "principal_record_hash": expected_principal["record_hash"],
        "identity_proof_hash": expected_principal["identity_proof_hash"],
        "consent_event_hash": expected_consent["event_hash"],
        "authority_audit_event_hash": expected_audit["event_hash"],
        "principal_record_count": int(principal_count),
        "consent_event_count": int(consent_count),
        "consent_scope": dict(_EXPECTED_SCOPE),
        "raw_private_identity_exported": False,
        "public_disclosure_authorized": False,
        "economic_processing_authorized": False,
        "ct_minting_authorized": False,
        "investment_processing_authorized": False,
        "agent_profiles_modified": False,
    }
    reject_raw_private_identity(result)
    return result
