"""Transaction-safe, append-only Influence and Investment Ledger storage.

The canonical Memory Economy source requires the Influence Ledger to track validated CT
from work and the Investment Ledger to track money separately.  It also requires live,
user-facing, and immutable archive ledger surfaces.  This production foundation creates
those six separated surfaces in one SQLite transaction domain so a future authorized entry
cannot partially appear in only one required surface.

Installation creates empty storage only.  Future append methods are fully validated and
remain unusable without the corresponding future finalized-capsule mint authorization or
legal-reviewed investment authorization receipts.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping

from ..contracts.canonical_json import assert_utc_timestamp_z, canonical_json
from ..contracts.enums import ContractValueError

BUILD_ID = "CE-IV-LEDGER-CAPSULE-BUILD-001"
INTEGRATED_SECURITY_OVERLAY_BUILD_ID = "CE-INTEGRATED-MULTIUSER-CORE-BUILD-002"
LIVE_LEDGER_APPEND_GATE_ENABLED = False
LEDGER_SCHEMA_VERSION = "contribution_dual_ledger_sqlite_v1_build001"
LEDGER_MANIFEST_SCHEMA_VERSION = "contribution_dual_ledger_store_manifest_v1_build001"
INFLUENCE_ENTRY_SCHEMA_VERSION = "influence_ledger_entry_v1_build001"
INVESTMENT_ENTRY_SCHEMA_VERSION = "investment_ledger_entry_v1_build001"
LEDGER_INITIALIZE_APPROVAL_TOKEN = "APPROVE_CE_DUAL_LEDGER_EMPTY_STORAGE_INITIALIZATION_BUILD001"
EMPTY_CHAIN_HASH = hashlib.sha256(b"").hexdigest()
_INFLUENCE_TABLES = ("influence_live_entries", "influence_user_entries", "influence_archive_entries")
_INVESTMENT_TABLES = ("investment_live_entries", "investment_user_entries", "investment_archive_entries")
_ALL_ENTRY_TABLES = _INFLUENCE_TABLES + _INVESTMENT_TABLES


class LedgerStoreError(RuntimeError):
    """Raised when a dual-ledger integrity or authorization boundary fails."""


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _hash_payload(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _database_path(ledger_root: Path) -> Path:
    return Path(ledger_root).resolve() / "contribution_ledgers.db"


def _manifest_path(ledger_root: Path) -> Path:
    return Path(ledger_root).resolve() / "ledger_store_manifest.json"


def _reject_symlink_path(path: Path, label: str) -> None:
    if path.exists() and path.is_symlink():
        raise LedgerStoreError(f"refusing symlinked {label}: {path}")


def _ensure_root(ledger_root: Path) -> Path:
    root = Path(ledger_root).resolve()
    _reject_symlink_path(root, "ledger root")
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(root, 0o700)
    return root


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _reject_symlink_path(path, "ledger manifest")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    temporary = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, indent=2))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
        directory_fd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary.exists():
            temporary.unlink()


def _schema_sql() -> str:
    blocks = [
        "PRAGMA foreign_keys = ON;",
        """
        CREATE TABLE IF NOT EXISTS ledger_store_metadata (
            singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
            schema_version TEXT NOT NULL,
            build_id TEXT NOT NULL,
            storage_model TEXT NOT NULL CHECK (storage_model = 'sqlite_atomic_three_surface_separated_ledgers'),
            influence_entries_written_during_initialization INTEGER NOT NULL CHECK (influence_entries_written_during_initialization = 0),
            investment_entries_written_during_initialization INTEGER NOT NULL CHECK (investment_entries_written_during_initialization = 0),
            ct_minting_activated_during_initialization INTEGER NOT NULL CHECK (ct_minting_activated_during_initialization = 0),
            investment_processing_activated_during_initialization INTEGER NOT NULL CHECK (investment_processing_activated_during_initialization = 0),
            initialized_at_utc TEXT NOT NULL
        );
        """,
    ]
    influence_definition = """
        CREATE TABLE IF NOT EXISTS {table} (
            entry_id TEXT PRIMARY KEY,
            sequence_no INTEGER NOT NULL UNIQUE CHECK (sequence_no > 0),
            prior_entry_hash TEXT NOT NULL CHECK (length(prior_entry_hash) = 64),
            entry_hash TEXT NOT NULL UNIQUE CHECK (length(entry_hash) = 64),
            principal_id TEXT NOT NULL,
            capsule_id TEXT NOT NULL,
            capsule_top_level_hash TEXT NOT NULL CHECK (length(capsule_top_level_hash) = 64),
            mint_event_id TEXT NOT NULL,
            mint_event_hash TEXT NOT NULL CHECK (length(mint_event_hash) = 64),
            ct_minted_milli_ct INTEGER NOT NULL CHECK (ct_minted_milli_ct > 0),
            contribution_type TEXT NOT NULL CHECK (contribution_type IN ('CRT', 'CPT', 'BLD')),
            influence_type TEXT NOT NULL CHECK (influence_type IN ('direct', 'indirect', 'collaborative')),
            difficulty TEXT NOT NULL CHECK (difficulty IN ('light', 'standard', 'heavy', 'monument')),
            contributor_action_proof_hash TEXT NOT NULL CHECK (length(contributor_action_proof_hash) = 64),
            validator_id TEXT NOT NULL,
            timestamp_utc TEXT NOT NULL,
            authorization_receipt_hash TEXT NOT NULL CHECK (length(authorization_receipt_hash) = 64),
            schema_version TEXT NOT NULL
        );
    """
    investment_definition = """
        CREATE TABLE IF NOT EXISTS {table} (
            entry_id TEXT PRIMARY KEY,
            sequence_no INTEGER NOT NULL UNIQUE CHECK (sequence_no > 0),
            prior_entry_hash TEXT NOT NULL CHECK (length(prior_entry_hash) = 64),
            entry_hash TEXT NOT NULL UNIQUE CHECK (length(entry_hash) = 64),
            principal_id TEXT NOT NULL,
            investment_event_id TEXT NOT NULL,
            amount_minor_units INTEGER NOT NULL CHECK (amount_minor_units > 0),
            currency_code TEXT NOT NULL,
            verification_receipt_hash TEXT NOT NULL CHECK (length(verification_receipt_hash) = 64),
            timestamp_utc TEXT NOT NULL,
            authorization_receipt_hash TEXT NOT NULL CHECK (length(authorization_receipt_hash) = 64),
            creates_ct INTEGER NOT NULL CHECK (creates_ct = 0),
            schema_version TEXT NOT NULL
        );
    """
    for table in _INFLUENCE_TABLES:
        blocks.append(influence_definition.format(table=table))
    for table in _INVESTMENT_TABLES:
        blocks.append(investment_definition.format(table=table))
    for table in _ALL_ENTRY_TABLES:
        blocks.append(
            f"CREATE TRIGGER IF NOT EXISTS block_update_{table} BEFORE UPDATE ON {table} "
            f"BEGIN SELECT RAISE(ABORT, '{table} is append-only; append correction/nullification events instead'); END;"
        )
        blocks.append(
            f"CREATE TRIGGER IF NOT EXISTS block_delete_{table} BEFORE DELETE ON {table} "
            f"BEGIN SELECT RAISE(ABORT, '{table} cannot be deleted'); END;"
        )
    return "\n".join(blocks)


@contextmanager
def _transaction(database: Path) -> Iterator[sqlite3.Connection]:
    _reject_symlink_path(database, "ledger database")
    connection = sqlite3.connect(str(database))
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = FULL")
        connection.execute("PRAGMA busy_timeout = 5000")
        connection.execute("BEGIN IMMEDIATE")
        yield connection
        connection.commit()
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.close()


def _read_only_connection(database: Path) -> sqlite3.Connection:
    if not database.is_file() or database.is_symlink():
        raise LedgerStoreError(f"ledger database is missing or symlinked: {database}")
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _store_manifest(initialized_at_utc: str) -> dict[str, Any]:
    core = {
        "schema_version": LEDGER_MANIFEST_SCHEMA_VERSION,
        "build_id": BUILD_ID,
        "ledger_schema_version": LEDGER_SCHEMA_VERSION,
        "storage_model": "sqlite_atomic_three_surface_separated_ledgers",
        "storage_reason": "one local transaction boundary atomically maintains live, user, and immutable archive surfaces while permanently separating work-earned CT from money activity",
        "influence_ledger_surfaces": list(_INFLUENCE_TABLES),
        "investment_ledger_surfaces": list(_INVESTMENT_TABLES),
        "initialized_at_utc": initialized_at_utc,
        "initialization_writes_ledger_entries": False,
        "initialization_mints_ct": False,
        "initialization_records_money": False,
        "money_creates_ct": False,
        "ct_requires_finalized_validated_capsule": True,
        "append_only_triggers_required": True,
    }
    core["manifest_hash"] = _hash_payload(core)
    return core


def initialize_dual_ledger_store(
    ledger_root: Path,
    *,
    approval_token: str,
    initialized_at_utc: str = "2026-05-30T18:00:00Z",
) -> dict[str, Any]:
    """Create real empty ledger storage; this operation records no work and no money."""
    if approval_token != LEDGER_INITIALIZE_APPROVAL_TOKEN:
        raise LedgerStoreError("explicit empty dual-ledger initialization approval token is required")
    assert_utc_timestamp_z(initialized_at_utc, "initialized_at_utc")
    root = _ensure_root(ledger_root)
    database = _database_path(root)
    manifest_path = _manifest_path(root)
    manifest = _store_manifest(initialized_at_utc)
    _reject_symlink_path(database, "ledger database")
    schema_connection = sqlite3.connect(str(database))
    try:
        schema_connection.execute("PRAGMA foreign_keys = ON")
        schema_connection.execute("PRAGMA journal_mode = WAL")
        schema_connection.execute("PRAGMA synchronous = FULL")
        schema_connection.executescript("BEGIN IMMEDIATE;\n" + _schema_sql() + "\nCOMMIT;")
    except Exception:
        if schema_connection.in_transaction:
            schema_connection.rollback()
        raise
    finally:
        schema_connection.close()
    with _transaction(database) as connection:
        existing = connection.execute("SELECT * FROM ledger_store_metadata WHERE singleton_id = 1").fetchone()
        expected = (
            1, LEDGER_SCHEMA_VERSION, BUILD_ID, "sqlite_atomic_three_surface_separated_ledgers",
            0, 0, 0, 0, initialized_at_utc,
        )
        if existing is None:
            connection.execute(
                "INSERT INTO ledger_store_metadata (singleton_id, schema_version, build_id, storage_model, "
                "influence_entries_written_during_initialization, investment_entries_written_during_initialization, "
                "ct_minting_activated_during_initialization, investment_processing_activated_during_initialization, "
                "initialized_at_utc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                expected,
            )
            metadata_outcome = "inserted_empty_store_metadata"
        elif tuple(existing) == expected:
            metadata_outcome = "existing_empty_store_metadata_verified_idempotent_no_write"
        else:
            raise LedgerStoreError("existing ledger metadata conflicts with the authorized empty initialization")
    if manifest_path.exists():
        try:
            existing_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise LedgerStoreError("existing ledger manifest cannot be verified") from exc
        if existing_manifest != manifest:
            raise LedgerStoreError("existing ledger manifest conflicts with the authorized empty initialization")
        manifest_outcome = "existing_manifest_verified_idempotent_no_write"
    else:
        _atomic_write_json(manifest_path, manifest)
        manifest_outcome = "manifest_written"
    verification = verify_dual_ledger_store(root)
    return {
        "schema_version": "dual_ledger_initialization_receipt_v1_build001",
        "build_id": BUILD_ID,
        "operation": "initialize_empty_permanently_separated_ledgers",
        "metadata_outcome": metadata_outcome,
        "manifest_outcome": manifest_outcome,
        "ledger_entries_written": 0,
        "influence_entries_written": 0,
        "investment_entries_written": 0,
        "ct_minted_milli_ct": 0,
        "money_activity_recorded": False,
        "verification": verification,
    }


def _table_rows(connection: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    return [dict(row) for row in connection.execute(f"SELECT * FROM {table} ORDER BY sequence_no ASC").fetchall()]


def _verify_chain(rows: list[dict[str, Any]], *, investment: bool) -> None:
    prior = EMPTY_CHAIN_HASH
    for expected_sequence, row in enumerate(rows, start=1):
        if row["sequence_no"] != expected_sequence or row["prior_entry_hash"] != prior:
            raise LedgerStoreError("ledger sequence or prior-entry hash chain is invalid")
        unhashed = {key: value for key, value in row.items() if key != "entry_hash"}
        if _hash_payload(unhashed) != row["entry_hash"]:
            raise LedgerStoreError("ledger entry hash verification failed")
        if investment and row["creates_ct"] != 0:
            raise LedgerStoreError("Investment Ledger record attempted to create CT")
        prior = row["entry_hash"]


def verify_dual_ledger_store(ledger_root: Path) -> dict[str, Any]:
    """Verify three-surface equality, append-only protection, and ledger separation."""
    root = Path(ledger_root).resolve()
    database = _database_path(root)
    manifest_path = _manifest_path(root)
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise LedgerStoreError("dual-ledger store manifest is missing or symlinked")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LedgerStoreError("dual-ledger store manifest is unreadable") from exc
    manifest_core = {key: value for key, value in manifest.items() if key != "manifest_hash"}
    if not _is_sha256(manifest.get("manifest_hash")) or _hash_payload(manifest_core) != manifest["manifest_hash"]:
        raise LedgerStoreError("dual-ledger store manifest hash mismatch")
    connection = _read_only_connection(database)
    try:
        metadata = connection.execute("SELECT * FROM ledger_store_metadata WHERE singleton_id = 1").fetchone()
        if metadata is None or metadata["schema_version"] != LEDGER_SCHEMA_VERSION or metadata["build_id"] != BUILD_ID:
            raise LedgerStoreError("dual-ledger metadata is missing or uses an unapproved schema")
        if any(metadata[field] != 0 for field in (
            "influence_entries_written_during_initialization", "investment_entries_written_during_initialization",
            "ct_minting_activated_during_initialization", "investment_processing_activated_during_initialization",
        )):
            raise LedgerStoreError("ledger initialization metadata reports prohibited entry or activation behavior")
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        if not set(_ALL_ENTRY_TABLES).issubset(tables):
            raise LedgerStoreError("required separated ledger surface table is missing")
        triggers = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='trigger'").fetchall()}
        for table in _ALL_ENTRY_TABLES:
            if {f"block_update_{table}", f"block_delete_{table}"} - triggers:
                raise LedgerStoreError(f"append-only trigger protection is missing for {table}")
        influence = [_table_rows(connection, table) for table in _INFLUENCE_TABLES]
        investment = [_table_rows(connection, table) for table in _INVESTMENT_TABLES]
        for rows in influence:
            _verify_chain(rows, investment=False)
        for rows in investment:
            _verify_chain(rows, investment=True)
        if not (influence[0] == influence[1] == influence[2]):
            raise LedgerStoreError("Influence Ledger live/user/archive surfaces diverge")
        if not (investment[0] == investment[1] == investment[2]):
            raise LedgerStoreError("Investment Ledger live/user/archive surfaces diverge")
    finally:
        connection.close()
    return {
        "schema_version": "dual_ledger_store_verification_v1_build001",
        "build_id": BUILD_ID,
        "verified": True,
        "ledger_store_manifest_hash": manifest["manifest_hash"],
        "storage_model": manifest["storage_model"],
        "influence_ledger_surfaces": list(_INFLUENCE_TABLES),
        "investment_ledger_surfaces": list(_INVESTMENT_TABLES),
        "influence_entry_count": len(influence[0]),
        "investment_entry_count": len(investment[0]),
        "surfaces_atomic_and_equal": True,
        "append_only_protection_verified": True,
        "money_creates_ct": False,
        "ct_minting_performed_during_initialization": False,
        "investment_activity_recorded_during_initialization": False,
    }


def _authorization_hash(authorization: Mapping[str, Any]) -> str:
    return _hash_payload(authorization)


def _validate_influence_entry(entry: Mapping[str, Any], authorization: Mapping[str, Any]) -> dict[str, Any]:
    if authorization.get("schema_version") != "finalized_validated_capsule_ct_mint_authorization_receipt_v1":
        raise LedgerStoreError("Influence Ledger entry requires a finalized validated capsule CT mint authorization receipt")
    if authorization.get("authorization_type") != "finalized_validated_capsule_ct_mint_authorization_receipt" or authorization.get("authorized") is not True:
        raise LedgerStoreError("Influence Ledger entry authorization is absent or false")
    if entry.get("capsule_finalized") is not True or entry.get("breath_validation_status") != "validated" or entry.get("ct_minting_status") != "minted":
        raise LedgerStoreError("Influence Ledger entry requires finalized, validated, minted capsule state")
    if not isinstance(entry.get("ct_minted_milli_ct"), int) or isinstance(entry.get("ct_minted_milli_ct"), bool) or entry["ct_minted_milli_ct"] <= 0:
        raise LedgerStoreError("Influence Ledger CT value must be a positive integer milli-CT value")
    required = (
        "entry_id", "principal_id", "capsule_id", "capsule_top_level_hash", "mint_event_id", "mint_event_hash",
        "contribution_type", "influence_type", "difficulty", "contributor_action_proof_hash", "validator_id", "timestamp_utc",
    )
    if any(not entry.get(field) for field in required):
        raise LedgerStoreError("Influence Ledger entry is missing a required field")
    for field in ("capsule_top_level_hash", "mint_event_hash", "contributor_action_proof_hash"):
        if not _is_sha256(entry[field]):
            raise LedgerStoreError(f"Influence Ledger {field} must be a lowercase SHA-256 value")
    if entry["contribution_type"] not in {"CRT", "CPT", "BLD"} or entry["influence_type"] not in {"direct", "indirect", "collaborative"} or entry["difficulty"] not in {"light", "standard", "heavy", "monument"}:
        raise LedgerStoreError("Influence Ledger classification value is invalid")
    assert_utc_timestamp_z(entry["timestamp_utc"], "timestamp_utc")
    return {
        "schema_version": INFLUENCE_ENTRY_SCHEMA_VERSION,
        "entry_id": entry["entry_id"],
        "principal_id": entry["principal_id"],
        "capsule_id": entry["capsule_id"],
        "capsule_top_level_hash": entry["capsule_top_level_hash"],
        "mint_event_id": entry["mint_event_id"],
        "mint_event_hash": entry["mint_event_hash"],
        "ct_minted_milli_ct": entry["ct_minted_milli_ct"],
        "contribution_type": entry["contribution_type"],
        "influence_type": entry["influence_type"],
        "difficulty": entry["difficulty"],
        "contributor_action_proof_hash": entry["contributor_action_proof_hash"],
        "validator_id": entry["validator_id"],
        "timestamp_utc": entry["timestamp_utc"],
        "authorization_receipt_hash": _authorization_hash(authorization),
    }


def _validate_investment_entry(entry: Mapping[str, Any], authorization: Mapping[str, Any]) -> dict[str, Any]:
    if authorization.get("schema_version") != "legal_reviewed_investment_ledger_write_receipt_v1":
        raise LedgerStoreError("Investment Ledger entry requires a legal-reviewed write authorization receipt")
    if authorization.get("authorization_type") != "legal_reviewed_investment_ledger_write_receipt" or authorization.get("authorized") is not True:
        raise LedgerStoreError("Investment Ledger entry authorization is absent or false")
    if entry.get("creates_ct") is not False:
        raise LedgerStoreError("Investment Ledger activity must never create CT")
    required = ("entry_id", "principal_id", "investment_event_id", "currency_code", "verification_receipt_hash", "timestamp_utc")
    if any(not entry.get(field) for field in required):
        raise LedgerStoreError("Investment Ledger entry is missing a required field")
    if not isinstance(entry.get("amount_minor_units"), int) or isinstance(entry.get("amount_minor_units"), bool) or entry["amount_minor_units"] <= 0:
        raise LedgerStoreError("Investment Ledger amount must be a positive integer minor-unit value")
    if not _is_sha256(entry["verification_receipt_hash"]):
        raise LedgerStoreError("Investment Ledger verification receipt must be a lowercase SHA-256 value")
    assert_utc_timestamp_z(entry["timestamp_utc"], "timestamp_utc")
    return {
        "schema_version": INVESTMENT_ENTRY_SCHEMA_VERSION,
        "entry_id": entry["entry_id"],
        "principal_id": entry["principal_id"],
        "investment_event_id": entry["investment_event_id"],
        "amount_minor_units": entry["amount_minor_units"],
        "currency_code": entry["currency_code"],
        "verification_receipt_hash": entry["verification_receipt_hash"],
        "timestamp_utc": entry["timestamp_utc"],
        "authorization_receipt_hash": _authorization_hash(authorization),
        "creates_ct": 0,
    }


def _append_atomically(ledger_root: Path, *, tables: tuple[str, ...], payload: Mapping[str, Any]) -> dict[str, Any]:
    verify_dual_ledger_store(ledger_root)
    database = _database_path(Path(ledger_root).resolve())
    with _transaction(database) as connection:
        existing_primary = connection.execute(f"SELECT * FROM {tables[0]} WHERE entry_id = ?", (payload["entry_id"],)).fetchone()
        if existing_primary is not None:
            existing_record = dict(existing_primary)
            unhashed = {key: value for key, value in existing_record.items() if key not in {"entry_hash", "sequence_no", "prior_entry_hash"}}
            if unhashed != dict(payload):
                raise LedgerStoreError("existing ledger entry id conflicts with authorized record")
            return {
                "schema_version": "ledger_append_receipt_v1_build001",
                "build_id": BUILD_ID,
                "entry_id": existing_record["entry_id"],
                "entry_hash": existing_record["entry_hash"],
                "sequence_no": existing_record["sequence_no"],
                "surfaces_written": [],
                "outcome": "already_committed_idempotent_no_write",
                "verification": {"verified": True, "idempotent_existing_entry": True},
            }
        first_rows = _table_rows(connection, tables[0])
        sequence_no = len(first_rows) + 1
        prior_entry_hash = first_rows[-1]["entry_hash"] if first_rows else EMPTY_CHAIN_HASH
        body = {"sequence_no": sequence_no, "prior_entry_hash": prior_entry_hash, **dict(payload)}
        entry_hash = _hash_payload(body)
        record = {**body, "entry_hash": entry_hash}
        fields = tuple(record.keys())
        values = tuple(record[field] for field in fields)
        placeholders = ", ".join("?" for _ in fields)
        for table in tables:
            existing = connection.execute(f"SELECT * FROM {table} WHERE entry_id = ?", (record["entry_id"],)).fetchone()
            if existing is not None:
                if dict(existing) != record:
                    raise LedgerStoreError("existing ledger entry id conflicts with authorized record")
                continue
            connection.execute(f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})", values)
    verification = verify_dual_ledger_store(ledger_root)
    return {
        "schema_version": "ledger_append_receipt_v1_build001",
        "build_id": BUILD_ID,
        "entry_id": record["entry_id"],
        "entry_hash": entry_hash,
        "sequence_no": sequence_no,
        "surfaces_written": list(tables),
        "verification": verification,
    }


def append_authorized_influence_entry(ledger_root: Path, entry: Mapping[str, Any], authorization: Mapping[str, Any]) -> dict[str, Any]:
    """Denied until a later controlled CT-mint activation authorizes this economic write."""
    raise LedgerStoreError(
        "Influence Ledger append is disabled by CE-INTEGRATED-MULTIUSER-CORE-BUILD-002; "
        "a fabricated authorization receipt cannot activate CT history."
    )


def append_authorized_investment_entry(ledger_root: Path, entry: Mapping[str, Any], authorization: Mapping[str, Any]) -> dict[str, Any]:
    """Denied until a separately approved investment activation build authorizes this write."""
    raise LedgerStoreError(
        "Investment Ledger append is disabled by CE-INTEGRATED-MULTIUSER-CORE-BUILD-002; "
        "investment remains separate from CT and requires later explicit activation."
    )
