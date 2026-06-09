"""Canonical multi-user contributor authority bridge for Identity Vault.

This module replaces founder-locked behavior for all future approved registrations while
preserving the existing Build 001 Nic principal exactly as stored.  It operates only on
Identity Vault's accepted ``user_profiles`` database schema and never exports raw identity
fields into Contribution Economy objects.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ..contracts.canonical_json import assert_utc_timestamp_z, canonical_json
from ..contracts.identity_reference_schema import reject_raw_private_identity
from ..integrated_core.policy import BUILD_ID, LIVE_POLICY

SCHEMA_VERSION = "identity_vault_multiuser_authority_bridge_v2_build002"
STATUS_EVENT_SCHEMA_VERSION = "identity_vault_principal_status_event_v2_build002"
CONSENT_EVENT_SCHEMA_VERSION = "identity_vault_consent_scope_event_v2_build002"
AUTHORITY_RECEIPT_SCHEMA_VERSION = "identity_vault_authority_resolution_receipt_v2_build002"
INITIALIZE_APPROVAL_TOKEN = "APPROVE_CE_MULTIUSER_AUTHORITY_SCHEMA_INITIALIZATION_BUILD002"
REGISTER_APPROVAL_TOKEN = "APPROVE_CE_REGISTER_EXISTING_IDENTITY_CONTRIBUTOR_BUILD002"
CONSENT_APPROVAL_TOKEN = "APPROVE_CE_APPEND_LIMITED_INTERNAL_CONSENT_EVENT_BUILD002"
STATUS_APPROVAL_TOKEN = "APPROVE_CE_APPEND_PRINCIPAL_STATUS_EVENT_BUILD002"
HASH_ALGORITHM = "sha256"
_ALLOWED_PRINCIPAL_TYPES = {"human_owner_builder", "human_contributor", "authorized_node"}
_ALLOWED_SAFE_SCOPE = {
    "local_identity_storage_authorized",
    "internal_attribution_reference_authorized",
    "capsule_candidate_reference_authorized",
}
_ALL_SCOPE_KEYS = (
    "local_identity_storage_authorized",
    "internal_attribution_reference_authorized",
    "capsule_candidate_reference_authorized",
    "public_display_authorized",
    "portability_authorized",
    "economic_processing_authorized",
    "ct_minting_authorized",
    "investment_processing_authorized",
)


class MultiUserAuthorityError(RuntimeError):
    """Raised when a multi-user identity/consent boundary cannot be proven safely."""


@dataclass(frozen=True)
class MultiUserAuthorityPaths:
    root: Path
    database: Path
    schema_extension: Path
    service_contract: Path
    manifests_root: Path

    @classmethod
    def from_root(cls, root: Path) -> "MultiUserAuthorityPaths":
        root = Path(root).resolve()
        return cls(
            root=root,
            database=root / "data" / "identity_vault.db",
            schema_extension=root / "schema_extensions" / "contribution_economy_multiuser_authority_v2.sql",
            service_contract=root / "service_contracts" / "contribution_economy_integrated_multiuser_core_build002.v1.json",
            manifests_root=root / "contributor_authority" / "principals_v2",
        )


def _hash_payload(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _connect(database: Path, *, read_only: bool = False) -> sqlite3.Connection:
    if not database.exists() or database.is_symlink():
        raise MultiUserAuthorityError(f"canonical Identity Vault database unavailable or symlinked: {database}")
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True) if read_only else sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    if not read_only:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = FULL")
        connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def _checkpoint_committed_wal(connection: sqlite3.Connection) -> None:
    """Flush committed SQLite WAL pages into the primary database before acknowledging success.

    Identity Vault snapshots and audit packets are copied as the canonical database file.
    A successful write operation must therefore not leave its only durable representation in
    an uncollected WAL sidecar.  This call occurs only after a commit has completed.
    """
    result = connection.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
    if result is not None and int(result[0]) != 0:
        raise MultiUserAuthorityError("Identity Vault WAL checkpoint could not complete safely")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise MultiUserAuthorityError(f"required service contract missing or symlinked: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise MultiUserAuthorityError("service contract must be a JSON object")
    return data


def _validate_contract(paths: MultiUserAuthorityPaths) -> dict[str, Any]:
    contract = _load_json(paths.service_contract)
    if contract.get("schema_version") != "ce_integrated_multiuser_identity_vault_service_contract_v1_build002":
        raise MultiUserAuthorityError("multi-user Identity Vault service contract schema mismatch")
    if contract.get("build_id") != BUILD_ID:
        raise MultiUserAuthorityError("multi-user Identity Vault service contract build mismatch")
    if contract.get("canonical_database_relative_path") != "data/identity_vault.db":
        raise MultiUserAuthorityError("service contract does not bind the canonical Identity Vault relative database path")
    if contract.get("schema_extension_relative_path") != "schema_extensions/contribution_economy_multiuser_authority_v2.sql":
        raise MultiUserAuthorityError("service contract does not bind the multi-user schema extension relative path")
    if _sha256_file(paths.schema_extension) != contract.get("schema_extension_sha256"):
        raise MultiUserAuthorityError("multi-user Identity Vault schema extension checksum mismatch")
    if contract.get("raw_private_identity_export_allowed") is not False:
        raise MultiUserAuthorityError("service contract must prohibit raw private identity export")
    if contract.get("live_economic_consent_activation_allowed") is not False:
        raise MultiUserAuthorityError("Build 002 service contract cannot authorize economic consent")
    return contract


def initialize_multiuser_authority_schema(identity_vault_root: Path, *, approval_token: str) -> dict[str, Any]:
    """Create the generic status/consent append-only schema; never enroll a person."""
    if approval_token != INITIALIZE_APPROVAL_TOKEN:
        raise MultiUserAuthorityError("multi-user authority schema initialization approval token mismatch")
    paths = MultiUserAuthorityPaths.from_root(identity_vault_root)
    _validate_contract(paths)
    sql = paths.schema_extension.read_text(encoding="utf-8")
    with _connect(paths.database) as connection:
        before_principals = connection.execute("SELECT COUNT(*) FROM contributor_principals").fetchone()[0]
        connection.executescript(sql)
        after_principals = connection.execute("SELECT COUNT(*) FROM contributor_principals").fetchone()[0]
        if before_principals != after_principals:
            raise MultiUserAuthorityError("schema initialization must not create or alter contributor principal rows")
        connection.commit()
        _checkpoint_committed_wal(connection)
    verification = verify_multiuser_authority_schema(identity_vault_root)
    return {
        "schema_version": "identity_vault_multiuser_schema_initialization_receipt_v1_build002",
        "build_id": BUILD_ID,
        "operation": "initialize_generic_append_only_multiuser_authority_schema",
        "creates_principal": False,
        "creates_consent_event": False,
        "creates_economic_authority": False,
        "verification": verification,
    }


def verify_multiuser_authority_schema(identity_vault_root: Path) -> dict[str, Any]:
    paths = MultiUserAuthorityPaths.from_root(identity_vault_root)
    _validate_contract(paths)
    required_tables = {"contributor_principal_status_events_v2", "contributor_consent_events_v2"}
    required_triggers = {
        "block_update_contributor_principal_status_events_v2",
        "block_delete_contributor_principal_status_events_v2",
        "block_update_contributor_consent_events_v2",
        "block_delete_contributor_consent_events_v2",
    }
    with _connect(paths.database, read_only=True) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        triggers = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='trigger'")}
        counts = {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in required_tables if table in tables}
    missing_tables = sorted(required_tables - tables)
    missing_triggers = sorted(required_triggers - triggers)
    return {
        "schema_version": "identity_vault_multiuser_schema_verification_receipt_v1_build002",
        "build_id": BUILD_ID,
        "verified": not missing_tables and not missing_triggers,
        "missing_tables": missing_tables,
        "missing_triggers": missing_triggers,
        "v2_row_counts": counts,
        "no_live_v2_identity_or_consent_rows_required_on_initialization": True,
    }


def _principal_row(connection: sqlite3.Connection, principal_id: str) -> dict[str, Any]:
    row = connection.execute(
        "SELECT principal_id, user_id, principal_type, authority_status, disclosure_class, "
        "pseudonymous_alias_id, source_user_profile_hash, schema_version, record_hash "
        "FROM contributor_principals WHERE principal_id = ?",
        (principal_id,),
    ).fetchone()
    if row is None:
        raise MultiUserAuthorityError("contributor principal does not exist")
    principal = dict(row)
    if principal["disclosure_class"] != "private_identity_vault_only":
        raise MultiUserAuthorityError("contributor principal is outside the private Identity Vault disclosure boundary")
    profile = connection.execute(
        "SELECT user_id, profile_hash FROM user_profiles WHERE user_id = ?", (principal["user_id"],)
    ).fetchone()
    if profile is None or profile["profile_hash"] != principal["source_user_profile_hash"]:
        raise MultiUserAuthorityError("contributor principal no longer binds to its source Identity Vault profile hash")
    return principal


def _latest_status(connection: sqlite3.Connection, principal: Mapping[str, Any]) -> dict[str, Any]:
    if "contributor_principal_status_events_v2" in {r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}:
        row = connection.execute(
            "SELECT status_event_id, authority_status, event_type, effective_at_utc, event_hash "
            "FROM contributor_principal_status_events_v2 WHERE principal_id = ? "
            "ORDER BY effective_at_utc DESC, status_event_id DESC LIMIT 1", (principal["principal_id"],)
        ).fetchone()
        if row is not None:
            return {**dict(row), "status_source": "v2_append_only_status_event"}
    legacy = "active" if principal["authority_status"] == "internal_contribution_authority_active" else "revoked"
    return {
        "status_event_id": None,
        "authority_status": legacy,
        "event_type": "legacy_build001_principal_genesis",
        "effective_at_utc": None,
        "event_hash": principal["record_hash"],
        "status_source": "build001_principal_record_fallback",
    }


def _latest_consent(connection: sqlite3.Connection, principal_id: str) -> dict[str, Any]:
    tables = {r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "contributor_consent_events_v2" in tables:
        row = connection.execute(
            "SELECT * FROM contributor_consent_events_v2 WHERE principal_id = ? "
            "ORDER BY effective_at_utc DESC, consent_event_id DESC LIMIT 1", (principal_id,)
        ).fetchone()
        if row is not None:
            result = dict(row)
            result["consent_source"] = "v2_append_only_consent_event"
            return result
    row = connection.execute(
        "SELECT * FROM contributor_consent_events WHERE principal_id = ? "
        "ORDER BY effective_at_utc DESC, consent_event_id DESC LIMIT 1", (principal_id,)
    ).fetchone()
    if row is None:
        raise MultiUserAuthorityError("contributor principal has no consent history")
    result = dict(row)
    result["consent_source"] = "build001_consent_event_fallback"
    return result


def resolve_authority_receipt(identity_vault_root: Path, principal_id: str) -> dict[str, Any]:
    """Return a safe opaque authority receipt consumable by Contribution Economy modules."""
    paths = MultiUserAuthorityPaths.from_root(identity_vault_root)
    reject_raw_private_identity({"principal_id": principal_id})
    with _connect(paths.database, read_only=True) as connection:
        principal = _principal_row(connection, principal_id)
        status = _latest_status(connection, principal)
        consent = _latest_consent(connection, principal_id)
    scope = {key: bool(consent[key]) for key in _ALL_SCOPE_KEYS}
    consent_status = str(consent.get("status"))
    authority_active = status["authority_status"] == "active"
    consent_active = consent_status in {"active", "active_limited_internal_consent"}
    receipt_body = {
        "schema_version": AUTHORITY_RECEIPT_SCHEMA_VERSION,
        "build_id": BUILD_ID,
        "principal_id": principal_id,
        "principal_type": principal["principal_type"],
        "disclosure_class": principal["disclosure_class"],
        "authority_active": authority_active,
        "status_source": status["status_source"],
        "status_event_hash": status["event_hash"],
        "consent_active": consent_active,
        "consent_source": consent["consent_source"],
        "consent_event_hash": consent["event_hash"],
        "consent_scope": scope,
        "raw_private_identity_exported": False,
    }
    receipt_hash = _hash_payload(receipt_body)
    return {**receipt_body, "consent_resolution_hash": receipt_hash}


def require_scopes(authority_receipt: Mapping[str, Any], *required_scopes: str) -> None:
    if authority_receipt.get("authority_active") is not True or authority_receipt.get("consent_active") is not True:
        raise MultiUserAuthorityError("contributor authority or consent is inactive")
    scope = authority_receipt.get("consent_scope")
    if not isinstance(scope, Mapping):
        raise MultiUserAuthorityError("authority receipt is missing consent scope")
    missing = [key for key in required_scopes if scope.get(key) is not True]
    if missing:
        raise MultiUserAuthorityError("required contributor consent scope not authorized: " + ", ".join(missing))


def _safe_internal_scope(requested: Mapping[str, Any]) -> dict[str, bool]:
    scope = {key: bool(requested.get(key, False)) for key in _ALL_SCOPE_KEYS}
    forbidden_true = [key for key in scope if key not in _ALLOWED_SAFE_SCOPE and scope[key]]
    if forbidden_true:
        raise MultiUserAuthorityError(
            "Build 002 cannot grant public, portable, economic, mint, or investment consent: " + ", ".join(forbidden_true)
        )
    if not all(scope[key] for key in _ALLOWED_SAFE_SCOPE):
        raise MultiUserAuthorityError("new internal contributor registration requires all three internal authority scopes")
    return scope


def _opaque_principal_id(user_id: str, profile_hash: str) -> str:
    digest = hashlib.sha256(f"{user_id}|{profile_hash}|{SCHEMA_VERSION}".encode("utf-8")).hexdigest()
    return f"ivp_{digest[:32]}"


def preview_existing_user_registration(identity_vault_root: Path, request: Mapping[str, Any]) -> dict[str, Any]:
    reject_raw_private_identity(request)
    user_id = str(request.get("user_id") or "").strip()
    principal_type = str(request.get("principal_type") or "human_contributor")
    timestamp = assert_utc_timestamp_z(request.get("effective_at_utc"), "effective_at_utc")
    if not user_id or principal_type not in _ALLOWED_PRINCIPAL_TYPES:
        raise MultiUserAuthorityError("registration requires an existing user_id and supported principal_type")
    scope = _safe_internal_scope(request.get("consent_scope", {}))
    paths = MultiUserAuthorityPaths.from_root(identity_vault_root)
    with _connect(paths.database, read_only=True) as connection:
        profile = connection.execute("SELECT user_id, profile_hash FROM user_profiles WHERE user_id = ?", (user_id,)).fetchone()
        if profile is None or not _is_sha256(profile["profile_hash"]):
            raise MultiUserAuthorityError("registration requires an existing canonical Identity Vault user profile with valid profile hash")
        existing = connection.execute("SELECT principal_id FROM contributor_principals WHERE user_id = ?", (user_id,)).fetchone()
    principal_id = existing["principal_id"] if existing else _opaque_principal_id(user_id, profile["profile_hash"])
    preview = {
        "schema_version": "identity_vault_registration_preview_v2_build002",
        "build_id": BUILD_ID,
        "principal_id": principal_id,
        "principal_type": principal_type,
        "source_user_profile_hash": profile["profile_hash"],
        "disclosure_class": "private_identity_vault_only",
        "effective_at_utc": timestamp,
        "consent_scope": scope,
        "existing_principal": existing is not None,
        "registration_persisted": False,
        "raw_private_identity_exported": False,
    }
    return {**preview, "preview_hash": _hash_payload(preview)}


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(payload), sort_keys=True, indent=2, ensure_ascii=False))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def register_existing_user_principal(identity_vault_root: Path, request: Mapping[str, Any], *, approval_token: str) -> dict[str, Any]:
    """Register one real pre-existing Vault user with internal-only consent; no economic activation."""
    if not LIVE_POLICY.register_approved_existing_identity_principal or approval_token != REGISTER_APPROVAL_TOKEN:
        raise MultiUserAuthorityError("approved existing-user principal registration authorization is required")
    paths = MultiUserAuthorityPaths.from_root(identity_vault_root)
    _validate_contract(paths)
    preview = preview_existing_user_registration(identity_vault_root, request)
    if preview["existing_principal"]:
        receipt = resolve_authority_receipt(identity_vault_root, preview["principal_id"])
        return {"schema_version": "identity_vault_registration_receipt_v2_build002", "build_id": BUILD_ID,
                "outcome": "existing_principal_resolved_idempotent_no_write", "authority_receipt": receipt}
    manifest = {
        "schema_version": "identity_vault_private_principal_manifest_v2_build002",
        "principal_id": preview["principal_id"],
        "principal_type": preview["principal_type"],
        "source_user_profile_hash": preview["source_user_profile_hash"],
        "disclosure_class": "private_identity_vault_only",
        "effective_at_utc": preview["effective_at_utc"],
        "consent_scope": preview["consent_scope"],
        "raw_private_identity_may_leave_identity_vault": False,
    }
    manifest_hash = _hash_payload(manifest)
    relative_manifest = f"contributor_authority/principals_v2/{preview['principal_id']}.authority.json"
    manifest_path = paths.root / relative_manifest
    if manifest_path.exists():
        raise MultiUserAuthorityError("authority manifest path already exists without an enrolled principal; operator review required")
    _atomic_json(manifest_path, manifest)
    principal_body = {
        "schema_version": "identity_vault_contributor_authority_v2_build002",
        "principal_id": preview["principal_id"], "user_id": str(request["user_id"]),
        "principal_type": preview["principal_type"], "authority_status": "internal_contribution_authority_active",
        "disclosure_class": "private_identity_vault_only", "pseudonymous_alias_id": None,
        "source_user_profile_hash": preview["source_user_profile_hash"], "authority_manifest_relative_path": relative_manifest,
        "authority_manifest_hash": manifest_hash, "identity_proof_hash": _hash_payload({"schema_version": "identity_proof_reference_v2_build002", "principal_id": preview["principal_id"], "source_user_profile_hash": preview["source_user_profile_hash"]}),
        "created_at_utc": preview["effective_at_utc"],
    }
    principal_hash = _hash_payload(principal_body)
    status_body = {"schema_version": STATUS_EVENT_SCHEMA_VERSION, "status_event_id": f"iv_status_{principal_hash[:24]}",
                   "principal_id": preview["principal_id"], "event_type": "authority_activation", "authority_status": "active",
                   "reason_code": "approved_existing_identity_registration", "prior_status_event_hash": None,
                   "effective_at_utc": preview["effective_at_utc"]}
    status_hash = _hash_payload(status_body)
    consent_body = {"schema_version": CONSENT_EVENT_SCHEMA_VERSION, "consent_event_id": f"iv_consent_v2_{principal_hash[:24]}",
                    "consent_record_id": f"iv_consent_record_v2_{principal_hash[:24]}", "principal_id": preview["principal_id"],
                    "event_type": "initial_scope_grant", **preview["consent_scope"], "authorization_basis": "explicit_operator_approved_internal_consent",
                    "status": "active", "effective_at_utc": preview["effective_at_utc"], "prior_consent_event_hash": None}
    consent_hash = _hash_payload(consent_body)
    try:
        with _connect(paths.database) as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("INSERT INTO contributor_principals (principal_id,user_id,principal_type,authority_status,disclosure_class,pseudonymous_alias_id,source_user_profile_hash,authority_manifest_relative_path,authority_manifest_hash,identity_proof_hash,schema_version,created_at_utc,record_hash) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                               (principal_body["principal_id"], principal_body["user_id"], principal_body["principal_type"], principal_body["authority_status"], principal_body["disclosure_class"], None, principal_body["source_user_profile_hash"], relative_manifest, manifest_hash, principal_body["identity_proof_hash"], principal_body["schema_version"], principal_body["created_at_utc"], principal_hash))
            connection.execute("INSERT INTO contributor_principal_status_events_v2 (status_event_id,principal_id,event_type,authority_status,reason_code,prior_status_event_hash,event_hash,effective_at_utc,schema_version) VALUES (?,?,?,?,?,?,?,?,?)",
                               (status_body["status_event_id"], status_body["principal_id"], status_body["event_type"], status_body["authority_status"], status_body["reason_code"], None, status_hash, status_body["effective_at_utc"], status_body["schema_version"]))
            connection.execute("INSERT INTO contributor_consent_events_v2 (consent_event_id,consent_record_id,principal_id,event_type,local_identity_storage_authorized,internal_attribution_reference_authorized,capsule_candidate_reference_authorized,public_display_authorized,portability_authorized,economic_processing_authorized,ct_minting_authorized,investment_processing_authorized,authorization_basis,status,effective_at_utc,prior_consent_event_hash,event_hash,schema_version) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                               (consent_body["consent_event_id"], consent_body["consent_record_id"], consent_body["principal_id"], consent_body["event_type"], *[int(consent_body[k]) for k in _ALL_SCOPE_KEYS], consent_body["authorization_basis"], consent_body["status"], consent_body["effective_at_utc"], None, consent_hash, consent_body["schema_version"]))
            prior_audit = connection.execute("SELECT event_hash FROM contributor_authority_audit_events WHERE principal_id = ? ORDER BY recorded_at_utc DESC, audit_event_id DESC LIMIT 1", (preview["principal_id"],)).fetchone()
            audit_payload = {"schema_version": "identity_vault_contributor_audit_event_v2_build002", "build_id": BUILD_ID, "event_type": "multiuser_principal_registered_internal_only", "principal_id": preview["principal_id"], "principal_record_hash": principal_hash, "status_event_hash": status_hash, "consent_event_hash": consent_hash, "recorded_at_utc": preview["effective_at_utc"]}
            audit_hash = _hash_payload(audit_payload)
            connection.execute("INSERT INTO contributor_authority_audit_events (audit_event_id,principal_id,event_type,event_payload_json,prior_audit_event_hash,event_hash,recorded_at_utc,schema_version) VALUES (?,?,?,?,?,?,?,?)", (f"iv_audit_v2_{audit_hash[:24]}", preview["principal_id"], "multiuser_principal_registered_internal_only", canonical_json(audit_payload), prior_audit["event_hash"] if prior_audit else None, audit_hash, preview["effective_at_utc"], "identity_vault_contributor_audit_event_v2_build002"))
            connection.commit()
            _checkpoint_committed_wal(connection)
    except Exception:
        if manifest_path.exists():
            manifest_path.unlink()
        raise
    return {"schema_version": "identity_vault_registration_receipt_v2_build002", "build_id": BUILD_ID,
            "outcome": "approved_existing_identity_registered_internal_only", "authority_receipt": resolve_authority_receipt(identity_vault_root, preview["principal_id"])}


def append_limited_internal_consent_event(identity_vault_root: Path, principal_id: str, request: Mapping[str, Any], *, approval_token: str) -> dict[str, Any]:
    if not LIVE_POLICY.append_limited_internal_consent_event or approval_token != CONSENT_APPROVAL_TOKEN:
        raise MultiUserAuthorityError("limited internal consent event approval is required")
    event_type = str(request.get("event_type") or "")
    if event_type not in {"scope_replacement", "scope_revocation"}:
        raise MultiUserAuthorityError("Build 002 consent append accepts scope_replacement or scope_revocation only")
    effective = assert_utc_timestamp_z(request.get("effective_at_utc"), "effective_at_utc")
    current = resolve_authority_receipt(identity_vault_root, principal_id)
    requested_scope = _safe_internal_scope(request.get("consent_scope", {})) if event_type != "scope_revocation" else {key: False for key in _ALL_SCOPE_KEYS}
    paths = MultiUserAuthorityPaths.from_root(identity_vault_root)
    body = {"schema_version": CONSENT_EVENT_SCHEMA_VERSION,
            "consent_event_id": f"iv_consent_v2_{hashlib.sha256((principal_id + effective + event_type).encode()).hexdigest()[:24]}",
            "consent_record_id": f"iv_consent_record_v2_{hashlib.sha256(principal_id.encode()).hexdigest()[:24]}",
            "principal_id": principal_id, "event_type": event_type, **requested_scope,
            "authorization_basis": "explicit_operator_approved_internal_consent_event", "status": "revoked" if event_type == "scope_revocation" else "active",
            "effective_at_utc": effective, "prior_consent_event_hash": current["consent_event_hash"]}
    event_hash = _hash_payload(body)
    with _connect(paths.database) as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("INSERT INTO contributor_consent_events_v2 (consent_event_id,consent_record_id,principal_id,event_type,local_identity_storage_authorized,internal_attribution_reference_authorized,capsule_candidate_reference_authorized,public_display_authorized,portability_authorized,economic_processing_authorized,ct_minting_authorized,investment_processing_authorized,authorization_basis,status,effective_at_utc,prior_consent_event_hash,event_hash,schema_version) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           (body["consent_event_id"], body["consent_record_id"], principal_id, event_type, *[int(body[k]) for k in _ALL_SCOPE_KEYS], body["authorization_basis"], body["status"], body["effective_at_utc"], body["prior_consent_event_hash"], event_hash, body["schema_version"]))
        prior_audit = connection.execute("SELECT event_hash FROM contributor_authority_audit_events WHERE principal_id = ? ORDER BY recorded_at_utc DESC, audit_event_id DESC LIMIT 1", (principal_id,)).fetchone()
        audit_payload = {"schema_version": "identity_vault_contributor_audit_event_v2_build002", "build_id": BUILD_ID, "event_type": "consent_scope_revoked" if event_type == "scope_revocation" else "consent_scope_replaced", "principal_id": principal_id, "consent_event_hash": event_hash, "recorded_at_utc": effective}
        audit_hash = _hash_payload(audit_payload)
        connection.execute("INSERT INTO contributor_authority_audit_events (audit_event_id,principal_id,event_type,event_payload_json,prior_audit_event_hash,event_hash,recorded_at_utc,schema_version) VALUES (?,?,?,?,?,?,?,?)", (f"iv_audit_v2_{audit_hash[:24]}", principal_id, audit_payload["event_type"], canonical_json(audit_payload), prior_audit["event_hash"] if prior_audit else None, audit_hash, effective, "identity_vault_contributor_audit_event_v2_build002"))
        connection.commit()
        _checkpoint_committed_wal(connection)
    return {"schema_version": "identity_vault_consent_append_receipt_v2_build002", "build_id": BUILD_ID,
            "event_hash": event_hash, "authority_receipt": resolve_authority_receipt(identity_vault_root, principal_id)}


def append_principal_status_event(identity_vault_root: Path, principal_id: str, *, event_type: str, reason_code: str, effective_at_utc: str, approval_token: str) -> dict[str, Any]:
    """Append a suspension, revocation, or restoration event without overwriting the principal genesis row."""
    if approval_token != STATUS_APPROVAL_TOKEN:
        raise MultiUserAuthorityError("principal status event approval is required")
    if event_type not in {"authority_suspension", "authority_revocation", "authority_restoration"}:
        raise MultiUserAuthorityError("unsupported principal status event type")
    effective = assert_utc_timestamp_z(effective_at_utc, "effective_at_utc")
    if not reason_code or not isinstance(reason_code, str):
        raise MultiUserAuthorityError("principal status event requires reason_code")
    current = resolve_authority_receipt(identity_vault_root, principal_id)
    status = {"authority_suspension": "suspended", "authority_revocation": "revoked", "authority_restoration": "active"}[event_type]
    paths = MultiUserAuthorityPaths.from_root(identity_vault_root)
    body = {"schema_version": STATUS_EVENT_SCHEMA_VERSION, "status_event_id": f"iv_status_v2_{hashlib.sha256((principal_id + effective + event_type).encode()).hexdigest()[:24]}", "principal_id": principal_id, "event_type": event_type, "authority_status": status, "reason_code": reason_code, "prior_status_event_hash": current["status_event_hash"], "effective_at_utc": effective}
    event_hash = _hash_payload(body)
    with _connect(paths.database) as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("INSERT INTO contributor_principal_status_events_v2 (status_event_id,principal_id,event_type,authority_status,reason_code,prior_status_event_hash,event_hash,effective_at_utc,schema_version) VALUES (?,?,?,?,?,?,?,?,?)", (body["status_event_id"], principal_id, event_type, status, reason_code, body["prior_status_event_hash"], event_hash, effective, body["schema_version"]))
        prior_audit = connection.execute("SELECT event_hash FROM contributor_authority_audit_events WHERE principal_id = ? ORDER BY recorded_at_utc DESC, audit_event_id DESC LIMIT 1", (principal_id,)).fetchone()
        audit_payload = {"schema_version": "identity_vault_contributor_audit_event_v2_build002", "build_id": BUILD_ID, "event_type": event_type, "principal_id": principal_id, "status_event_hash": event_hash, "recorded_at_utc": effective}
        audit_hash = _hash_payload(audit_payload)
        connection.execute("INSERT INTO contributor_authority_audit_events (audit_event_id,principal_id,event_type,event_payload_json,prior_audit_event_hash,event_hash,recorded_at_utc,schema_version) VALUES (?,?,?,?,?,?,?,?)", (f"iv_audit_v2_{audit_hash[:24]}", principal_id, event_type, canonical_json(audit_payload), prior_audit["event_hash"] if prior_audit else None, audit_hash, effective, "identity_vault_contributor_audit_event_v2_build002"))
        connection.commit()
        _checkpoint_committed_wal(connection)
    return {"schema_version": "identity_vault_status_append_receipt_v2_build002", "build_id": BUILD_ID, "event_hash": event_hash, "authority_receipt": resolve_authority_receipt(identity_vault_root, principal_id)}
