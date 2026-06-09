# identity_vault_adapter.py — Forge Identity Vault Read-Only Adapter
# Purpose: Provide contract-bound, read-only metadata access to Identity Vault.
# Boundary: no writes, no .env reads, no agent activation, no RMC memory access.

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

ADAPTER_VERSION = "0.1.0-readonly"
READ_ONLY = True

SENSITIVE_COLUMN_MARKERS = (
    "secret",
    "password",
    "token",
    "key",
    "private",
    "jwt",
    "hash",
    "credential",
)

SAFE_METADATA_COLUMNS = {
    "id",
    "uuid",
    "agent_id",
    "user_id",
    "name",
    "display_name",
    "role",
    "type",
    "status",
    "active",
    "created_at",
    "updated_at",
    "profile_id",
    "namespace",
    "rmc_namespace",
    "memory_namespace",
    "permission_tier",
    "permissions",
}

REQUIRED_CONTRACT_FIELDS = {
    "contract_name",
    "status",
    "version",
    "controlled_by",
    "canonical_database_path",
    "allowed_reads",
    "allowed_writes",
    "forbidden_reads",
    "forbidden_writes",
    "future_adapter_rules",
    "activation_rule",
}


class IdentityVaultAdapterError(RuntimeError):
    """Raised when Identity Vault read-only boundary validation fails."""


def _home_root() -> Path:
    return Path.home()


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise IdentityVaultAdapterError(f"Expected JSON object at {path}")
    return data


def _is_sensitive_column(column_name: str) -> bool:
    lowered = column_name.lower()
    return any(marker in lowered for marker in SENSITIVE_COLUMN_MARKERS)


def _safe_columns(columns: List[str]) -> List[str]:
    safe: List[str] = []
    for column in columns:
        lowered = column.lower()
        if _is_sensitive_column(lowered):
            continue
        if lowered in SAFE_METADATA_COLUMNS or lowered.endswith("_id") or lowered.endswith("_at"):
            safe.append(column)
    return safe


def _sqlite_uri(path: Path) -> str:
    return f"file:{path}?mode=ro"


@dataclass(frozen=True)
class IdentityVaultReadOnlyAdapter:
    """Read-only contract adapter for Identity Vault.

    This adapter intentionally does not register Forge tools and does not activate
    identities. It is a narrow reader for contract metadata, package metadata,
    SQLite schema/row counts, and safe identity metadata previews.
    """

    forge_root: Path = Path.home() / "forge"
    identity_vault_root: Path = Path.home() / "identity-vault"
    contract_path: Optional[Path] = None

    def __post_init__(self) -> None:
        if self.contract_path is None:
            object.__setattr__(
                self,
                "contract_path",
                self.identity_vault_root
                / "service_contracts"
                / "identity_vault_readonly_service_contract.draft.json",
            )

    def boundary(self) -> Dict[str, Any]:
        return {
            "adapter_version": ADAPTER_VERSION,
            "read_only": READ_ONLY,
            "forge_root": str(self.forge_root),
            "identity_vault_root": str(self.identity_vault_root),
            "contract_path": str(self.contract_path),
            "forbidden_operations": [
                "read .env secret values",
                "write Identity Vault databases",
                "write Forge registry",
                "write RMC memory",
                "activate agent identities",
                "execute agents inside Identity Vault",
            ],
        }

    def load_contract(self) -> Dict[str, Any]:
        contract = _read_json(Path(self.contract_path))
        return contract

    def validate_contract(self) -> Dict[str, Any]:
        contract = self.load_contract()
        missing = sorted(REQUIRED_CONTRACT_FIELDS.difference(contract.keys()))
        allowed_writes = contract.get("allowed_writes")
        forbidden_reads = contract.get("forbidden_reads") or []
        forbidden_writes = contract.get("forbidden_writes") or []
        future_rules = contract.get("future_adapter_rules") or []
        ok = (
            not missing
            and contract.get("controlled_by") == "Forge"
            and contract.get("status") in {"DRAFT_NOT_ACTIVE", "ACTIVE_READONLY"}
            and allowed_writes == []
            and bool(forbidden_reads)
            and bool(forbidden_writes)
            and bool(future_rules)
        )
        return {
            "ok": ok,
            "missing_fields": missing,
            "contract_name": contract.get("contract_name"),
            "status": contract.get("status"),
            "version": contract.get("version"),
            "controlled_by": contract.get("controlled_by"),
            "allowed_writes_empty": allowed_writes == [],
            "canonical_database_path": contract.get("canonical_database_path"),
        }

    def package_metadata(self) -> Dict[str, Any]:
        package_path = self.identity_vault_root / "package.json"
        package = _read_json(package_path)
        scripts = package.get("scripts", {})
        dependencies = package.get("dependencies", {})
        dev_dependencies = package.get("devDependencies", {})
        return {
            "name": package.get("name"),
            "version": package.get("version"),
            "description": package.get("description"),
            "scripts": sorted(scripts.keys()) if isinstance(scripts, dict) else [],
            "dependency_count": len(dependencies) if isinstance(dependencies, dict) else 0,
            "dev_dependency_count": len(dev_dependencies) if isinstance(dev_dependencies, dict) else 0,
        }

    def canonical_database_path(self) -> Path:
        contract = self.load_contract()
        path_value = contract.get("canonical_database_path")
        if not path_value:
            raise IdentityVaultAdapterError("Contract missing canonical_database_path")
        return Path(path_value)

    def database_schema_summary(self) -> Dict[str, Any]:
        db_path = self.canonical_database_path()
        if not db_path.exists():
            return {"ok": False, "exists": False, "path": str(db_path), "tables": [], "row_counts": {}}

        uri = _sqlite_uri(db_path)
        tables: List[str] = []
        row_counts: Dict[str, int] = {}
        columns: Dict[str, List[str]] = {}
        with sqlite3.connect(uri, uri=True) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            for table in tables:
                safe_table = table.replace('"', '""')
                cursor.execute(f'SELECT COUNT(*) FROM "{safe_table}"')
                row_counts[table] = int(cursor.fetchone()[0])
                cursor.execute(f'PRAGMA table_info("{safe_table}")')
                columns[table] = [row[1] for row in cursor.fetchall()]
        return {
            "ok": True,
            "exists": True,
            "opened_readonly": True,
            "path": str(db_path),
            "tables": tables,
            "row_counts": row_counts,
            "columns": columns,
        }

    def identity_metadata_preview(self, table: str = "agent_profiles", limit: int = 25) -> Dict[str, Any]:
        if table not in {"agent_profiles", "user_profiles"}:
            raise IdentityVaultAdapterError("Only agent_profiles and user_profiles metadata previews are allowed")
        if limit < 1 or limit > 100:
            raise IdentityVaultAdapterError("Limit must be between 1 and 100")

        schema = self.database_schema_summary()
        if not schema.get("ok"):
            return {"ok": False, "table": table, "rows": [], "safe_columns": [], "reason": "database_unavailable"}
        if table not in schema.get("tables", []):
            return {"ok": False, "table": table, "rows": [], "safe_columns": [], "reason": "table_missing"}

        columns = schema.get("columns", {}).get(table, [])
        safe_columns = _safe_columns(columns)
        if not safe_columns:
            return {"ok": True, "table": table, "rows": [], "safe_columns": [], "reason": "no_safe_metadata_columns"}

        select_clause = ", ".join(f'"{column.replace(chr(34), chr(34)*2)}"' for column in safe_columns)
        safe_table = table.replace('"', '""')
        db_path = self.canonical_database_path()
        with sqlite3.connect(_sqlite_uri(db_path), uri=True) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f'SELECT {select_clause} FROM "{safe_table}" LIMIT ?', (limit,))
            rows = [dict(row) for row in cursor.fetchall()]
        return {
            "ok": True,
            "table": table,
            "safe_columns": safe_columns,
            "row_count_returned": len(rows),
            "rows": rows,
        }

    def status(self) -> Dict[str, Any]:
        contract_status = self.validate_contract()
        package = self.package_metadata()
        schema = self.database_schema_summary()
        agent_preview = self.identity_metadata_preview("agent_profiles", limit=10)
        user_preview = self.identity_metadata_preview("user_profiles", limit=10)
        return {
            "ok": bool(contract_status.get("ok") and schema.get("ok")),
            "adapter_version": ADAPTER_VERSION,
            "read_only": READ_ONLY,
            "contract": contract_status,
            "package": package,
            "database": {
                "path": schema.get("path"),
                "opened_readonly": schema.get("opened_readonly", False),
                "tables": schema.get("tables", []),
                "row_counts": schema.get("row_counts", {}),
            },
            "identity_metadata_preview": {
                "agent_profiles": {
                    "ok": agent_preview.get("ok"),
                    "safe_columns": agent_preview.get("safe_columns", []),
                    "row_count_returned": agent_preview.get("row_count_returned", 0),
                },
                "user_profiles": {
                    "ok": user_preview.get("ok"),
                    "safe_columns": user_preview.get("safe_columns", []),
                    "row_count_returned": user_preview.get("row_count_returned", 0),
                },
            },
            "agent_identity_activation_performed": False,
            "database_write_performed": False,
            "env_secret_values_read": False,
        }


def get_identity_vault_status() -> Dict[str, Any]:
    """Convenience function for verifier scripts. Read-only."""
    return IdentityVaultReadOnlyAdapter().status()


def get_identity_vault_contract_summary() -> Dict[str, Any]:
    """Convenience function for future Forge wrapper tests. Read-only."""
    adapter = IdentityVaultReadOnlyAdapter()
    return {
        "boundary": adapter.boundary(),
        "contract": adapter.validate_contract(),
    }
