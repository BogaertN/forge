#!/usr/bin/env python3
"""
Patch 226 — Identity Vault Schema Migration Apply

Purpose:
  Apply the backed-up, minimal Identity Vault schema migration needed to align the
  live canonical SQLite database with the Self-Hosted Identity Vault operational
  profile blueprint.

Boundary:
  - Writes only to /home/nic/identity-vault/data/identity_vault.db schema.
  - Adds JSON payload/profile metadata columns and indexes only.
  - Does not create live agent profiles.
  - Does not activate identities.
  - Does not write RMC memory.
  - Does not modify Forge registry or service contracts.
  - Does not read .env secret values.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

PATCH_ID = "patch226_identity_vault_schema_migration_apply"
REPORT_ROOT_NAME = "identity_vault_patch226_schema_migration_apply_v1"

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
IDENTITY_ROOT = HOME / "identity-vault"
AIWEB_ROOT = HOME / "aiweb"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"
IDENTITY_DRAFT_CONTRACT = IDENTITY_ROOT / "service_contracts" / "identity_vault_readonly_service_contract.draft.json"
AIWEB_IDENTITY_CONTRACT = AIWEB_ROOT / "service_contracts" / "identity_vault.contract.json"
TOOL_REGISTRY = FORGE_ROOT / "config" / "tool_registry.json"
ENV_FILE = IDENTITY_ROOT / ".env"

AGENT_COLUMNS = [
    ("operational_profile_json", "TEXT NOT NULL DEFAULT '{}'", "Full Agent Operational Identity JSON payload matching the manual blueprint."),
    ("profile_schema_version", "TEXT NOT NULL DEFAULT '1.0.0-blueprint'", "Version of the operational identity payload schema."),
    ("rmc_namespace", "TEXT", "Read-only pointer to the agent-scoped RMC namespace. Not memory content."),
    ("activation_state", "TEXT NOT NULL DEFAULT 'inactive'", "inactive/draft/active lifecycle marker. Default must be inactive."),
    ("profile_hash", "TEXT", "Hash of operational_profile_json for tamper-evidence."),
    ("last_validated_at", "TEXT", "Timestamp of last schema/profile validation."),
]
USER_COLUMNS = [
    ("operational_profile_json", "TEXT NOT NULL DEFAULT '{}'", "Full User Operational Identity JSON payload matching the manual blueprint."),
    ("profile_schema_version", "TEXT NOT NULL DEFAULT '1.0.0-blueprint'", "Version of the operational identity payload schema."),
    ("profile_hash", "TEXT", "Hash of operational_profile_json for tamper-evidence."),
    ("last_validated_at", "TEXT", "Timestamp of last schema/profile validation."),
]
INDEXES = [
    ("idx_agent_profiles_agent_id", "agent_profiles", "agent_id"),
    ("idx_agent_profiles_activation_state", "agent_profiles", "activation_state"),
    ("idx_agent_profiles_rmc_namespace", "agent_profiles", "rmc_namespace"),
    ("idx_user_profiles_user_id", "user_profiles", "user_id"),
]


def utc_ts() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_no_content(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    st = path.stat()
    return {
        "exists": True,
        "size": st.st_size,
        "mode": oct(st.st_mode & 0o777),
        "mtime_ns": st.st_mtime_ns,
    }


def load_json(path: Path) -> Tuple[bool, Dict[str, Any] | None, str | None]:
    try:
        return True, json.loads(path.read_text(encoding="utf-8")), None
    except Exception as e:
        return False, None, f"{type(e).__name__}: {e}"


def sqlite_connect_rw(path: Path) -> sqlite3.Connection:
    # Use a direct file connection for schema migration. The database file is backed up first.
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def sqlite_connect_ro(path: Path) -> sqlite3.Connection:
    uri = f"file:{path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def table_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    return [str(row[1]) for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]


def table_counts(conn: sqlite3.Connection, tables: List[str]) -> Dict[str, int | str]:
    out: Dict[str, int | str] = {}
    for t in tables:
        try:
            out[t] = int(conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
        except Exception as e:
            out[t] = f"ERROR: {type(e).__name__}: {e}"
    return out


def list_tables(conn: sqlite3.Connection) -> List[str]:
    return [str(r[0]) for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]


def list_indexes(conn: sqlite3.Connection) -> List[str]:
    return [str(r[0]) for r in conn.execute("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name").fetchall()]


def backup_file(src: Path, dst: Path) -> Dict[str, Any]:
    if not src.exists():
        return {"source": str(src), "copied": False, "reason": "missing"}
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return {"source": str(src), "dest": str(dst), "copied": True, "sha256": sha256_file(dst)}


def build_report_md(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Identity Vault Patch 226 Schema Migration Apply")
    lines.append("")
    lines.append(f"Timestamp: `{report['timestamp']}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    for item in report["boundary"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Backup")
    lines.append(f"- backup root: `{report['backup_root']}`")
    for name, info in report["backup"].items():
        status = "COPIED" if info.get("copied") else f"SKIPPED ({info.get('reason','unknown')})"
        lines.append(f"- `{name}`: **{status}**")
    lines.append("")
    lines.append("## Migration Strategy")
    lines.append("- selected: `hybrid_json_payload_plus_indexed_core_columns`")
    lines.append("- Adds full operational profile JSON payload columns while preserving indexed lookup columns.")
    lines.append("- Defaults all lifecycle state to `inactive`.")
    lines.append("- Does not create live agent profiles or activate identities.")
    lines.append("")
    lines.append("## Database Before")
    lines.append(f"- canonical DB: `{report['canonical_db']}`")
    lines.append(f"- agent_profiles columns before: `{', '.join(report['before']['agent_columns'])}`")
    lines.append(f"- user_profiles columns before: `{', '.join(report['before']['user_columns'])}`")
    lines.append(f"- row counts before: `{report['before']['row_counts']}`")
    lines.append("")
    lines.append("## SQL Actions")
    for action in report["sql_actions"]:
        lines.append(f"- `{action['status']}` `{action['sql']}`")
    lines.append("")
    lines.append("## Database After")
    lines.append(f"- opened read-only after migration: `{report['after']['opened_readonly']}`")
    lines.append(f"- agent_profiles columns after: `{', '.join(report['after']['agent_columns'])}`")
    lines.append(f"- user_profiles columns after: `{', '.join(report['after']['user_columns'])}`")
    lines.append(f"- row counts after: `{report['after']['row_counts']}`")
    lines.append(f"- indexes after: `{', '.join(report['after']['indexes'])}`")
    lines.append("")
    lines.append("## Required Column Verification")
    lines.append(f"- agent required additions present: `{report['required_checks']['agent_required_present']}`")
    lines.append(f"- user required additions present: `{report['required_checks']['user_required_present']}`")
    lines.append(f"- required indexes present: `{report['required_checks']['indexes_present']}`")
    lines.append(f"- missing agent columns: `{report['required_checks']['missing_agent_columns']}`")
    lines.append(f"- missing user columns: `{report['required_checks']['missing_user_columns']}`")
    lines.append(f"- missing indexes: `{report['required_checks']['missing_indexes']}`")
    lines.append("")
    lines.append("## No Live Profile / Activation Check")
    lines.append(f"- agent rows before: `{report['no_live_profile_checks']['agent_rows_before']}`")
    lines.append(f"- agent rows after: `{report['no_live_profile_checks']['agent_rows_after']}`")
    lines.append(f"- user rows before: `{report['no_live_profile_checks']['user_rows_before']}`")
    lines.append(f"- user rows after: `{report['no_live_profile_checks']['user_rows_after']}`")
    lines.append(f"- live agent profiles created: `{report['no_live_profile_checks']['live_agent_profiles_created']}`")
    lines.append(f"- agent identity activation performed: `{report['safety']['agent_identity_activation_performed']}`")
    lines.append("")
    lines.append("## Safety Checks")
    for k, v in report["safety"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Findings")
    for f in report["findings"]:
        lines.append(f"- **{f['level']}** `{f['code']}` — {f['message']}")
    lines.append("")
    lines.append("## Next Safe Step")
    lines.append("Run a post-migration schema alignment verification. If it passes, create inactive draft Gilligan/Athena/Neo operational profile rows from the Identity Vault blueprint. Do not activate identities yet.")
    return "\n".join(lines) + "\n"


def main() -> int:
    ts = utc_ts()
    run_dir = FORGE_ROOT / "memory" / REPORT_ROOT_NAME / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    latest_md = FORGE_ROOT / "memory" / REPORT_ROOT_NAME / f"latest_{REPORT_ROOT_NAME.replace('_v1','')}.md"
    latest_json = FORGE_ROOT / "memory" / REPORT_ROOT_NAME / f"latest_{REPORT_ROOT_NAME.replace('_v1','')}.json"
    backup_root = FORGE_ROOT / "backups" / "patch226_identity_vault_schema_migration_before" / ts
    backup_root.mkdir(parents=True, exist_ok=True)

    boundary = [
        "This patch applies only the approved Identity Vault schema migration needed for full operational profile payload support.",
        "It backs up the canonical and legacy SQLite databases before migration.",
        "It adds JSON payload/profile metadata columns and indexes only.",
        "It does not create live agent profiles or activate identities.",
        "It does not modify .env, node_modules, Forge registry, service contracts, RMC memory, or AI.Web wrappers.",
        "It does not read .env secret values; only stat metadata is compared.",
    ]

    before_hashes = {
        "canonical_db": sha256_file(CANONICAL_DB),
        "legacy_db": sha256_file(LEGACY_DB),
        "identity_contract_draft": sha256_file(IDENTITY_DRAFT_CONTRACT),
        "aiweb_identity_contract": sha256_file(AIWEB_IDENTITY_CONTRACT),
        "tool_registry": sha256_file(TOOL_REGISTRY),
    }
    env_stat_before = stat_no_content(ENV_FILE)

    backup = {
        "canonical_db": backup_file(CANONICAL_DB, backup_root / "databases" / "data_identity_vault.db"),
        "legacy_db": backup_file(LEGACY_DB, backup_root / "databases" / "vault.db"),
        "identity_contract_draft": backup_file(IDENTITY_DRAFT_CONTRACT, backup_root / "contracts" / "identity_vault_readonly_service_contract.draft.json"),
        "aiweb_identity_contract": backup_file(AIWEB_IDENTITY_CONTRACT, backup_root / "contracts" / "identity_vault.contract.json"),
        "tool_registry": backup_file(TOOL_REGISTRY, backup_root / "forge" / "tool_registry.json"),
    }

    findings: List[Dict[str, str]] = []
    sql_actions: List[Dict[str, str]] = []
    verdict = "PASS"
    error = None

    before: Dict[str, Any] = {"agent_columns": [], "user_columns": [], "row_counts": {}}
    after: Dict[str, Any] = {"agent_columns": [], "user_columns": [], "row_counts": {}, "indexes": [], "opened_readonly": False}

    try:
        if not CANONICAL_DB.exists():
            raise RuntimeError(f"Canonical DB missing: {CANONICAL_DB}")
        conn = sqlite_connect_rw(CANONICAL_DB)
        try:
            tables = list_tables(conn)
            if "agent_profiles" not in tables or "user_profiles" not in tables:
                raise RuntimeError(f"Required tables missing. Tables={tables}")
            before["agent_columns"] = table_columns(conn, "agent_profiles")
            before["user_columns"] = table_columns(conn, "user_profiles")
            before["row_counts"] = table_counts(conn, ["agent_profiles", "user_profiles", "audit_logs", "feedback_logs", "session_state"])

            conn.execute("BEGIN IMMEDIATE")
            current_agent_cols = set(before["agent_columns"])
            current_user_cols = set(before["user_columns"])

            for col, spec, _desc in AGENT_COLUMNS:
                sql = f"ALTER TABLE agent_profiles ADD COLUMN {col} {spec}"
                if col in current_agent_cols:
                    sql_actions.append({"status": "SKIPPED_ALREADY_PRESENT", "sql": sql})
                else:
                    conn.execute(sql)
                    sql_actions.append({"status": "EXECUTED", "sql": sql})
                    current_agent_cols.add(col)

            for col, spec, _desc in USER_COLUMNS:
                sql = f"ALTER TABLE user_profiles ADD COLUMN {col} {spec}"
                if col in current_user_cols:
                    sql_actions.append({"status": "SKIPPED_ALREADY_PRESENT", "sql": sql})
                else:
                    conn.execute(sql)
                    sql_actions.append({"status": "EXECUTED", "sql": sql})
                    current_user_cols.add(col)

            for idx, table, col in INDEXES:
                sql = f"CREATE INDEX IF NOT EXISTS {idx} ON {table}({col})"
                conn.execute(sql)
                sql_actions.append({"status": "EXECUTED_OR_ALREADY_PRESENT", "sql": sql})

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        # Verify using read-only connection after migration.
        ro = sqlite_connect_ro(CANONICAL_DB)
        try:
            after["opened_readonly"] = True
            after["agent_columns"] = table_columns(ro, "agent_profiles")
            after["user_columns"] = table_columns(ro, "user_profiles")
            after["row_counts"] = table_counts(ro, ["agent_profiles", "user_profiles", "audit_logs", "feedback_logs", "session_state"])
            after["indexes"] = list_indexes(ro)
        finally:
            ro.close()

    except Exception as e:
        verdict = "FAIL"
        error = f"{type(e).__name__}: {e}"
        findings.append({"level": "FAIL", "code": "IV_SCHEMA_MIGRATION_EXCEPTION", "message": error})

    after_hashes = {
        "canonical_db": sha256_file(CANONICAL_DB),
        "legacy_db": sha256_file(LEGACY_DB),
        "identity_contract_draft": sha256_file(IDENTITY_DRAFT_CONTRACT),
        "aiweb_identity_contract": sha256_file(AIWEB_IDENTITY_CONTRACT),
        "tool_registry": sha256_file(TOOL_REGISTRY),
    }
    env_stat_after = stat_no_content(ENV_FILE)

    agent_required = [c[0] for c in AGENT_COLUMNS]
    user_required = [c[0] for c in USER_COLUMNS]
    required_indexes = [i[0] for i in INDEXES]
    missing_agent = [c for c in agent_required if c not in after.get("agent_columns", [])]
    missing_user = [c for c in user_required if c not in after.get("user_columns", [])]
    missing_indexes = [i for i in required_indexes if i not in after.get("indexes", [])]

    before_agent_count = before.get("row_counts", {}).get("agent_profiles", None)
    after_agent_count = after.get("row_counts", {}).get("agent_profiles", None)
    before_user_count = before.get("row_counts", {}).get("user_profiles", None)
    after_user_count = after.get("row_counts", {}).get("user_profiles", None)
    live_agent_profiles_created = (isinstance(before_agent_count, int) and isinstance(after_agent_count, int) and after_agent_count > before_agent_count)
    user_rows_created = (isinstance(before_user_count, int) and isinstance(after_user_count, int) and after_user_count > before_user_count)

    safety = {
        "env_secret_values_read": False,
        "env_stat_unchanged": env_stat_before == env_stat_after,
        "canonical_db_schema_changed_expected": before_hashes["canonical_db"] != after_hashes["canonical_db"],
        "legacy_db_unchanged": before_hashes["legacy_db"] == after_hashes["legacy_db"],
        "identity_contract_draft_unchanged": before_hashes["identity_contract_draft"] == after_hashes["identity_contract_draft"],
        "aiweb_identity_contract_unchanged": before_hashes["aiweb_identity_contract"] == after_hashes["aiweb_identity_contract"],
        "forge_tool_registry_modified": before_hashes["tool_registry"] != after_hashes["tool_registry"],
        "database_write_performed": bool(sql_actions and any(a["status"].startswith("EXECUTED") for a in sql_actions)),
        "database_content_rows_created": bool(live_agent_profiles_created or user_rows_created),
        "agent_identity_activation_performed": False,
        "schema_migration_executed": bool(sql_actions and any(a["status"] == "EXECUTED" for a in sql_actions)),
    }

    required_checks = {
        "agent_required_present": not missing_agent,
        "user_required_present": not missing_user,
        "indexes_present": not missing_indexes,
        "missing_agent_columns": missing_agent,
        "missing_user_columns": missing_user,
        "missing_indexes": missing_indexes,
    }
    no_live_profile_checks = {
        "agent_rows_before": before_agent_count,
        "agent_rows_after": after_agent_count,
        "user_rows_before": before_user_count,
        "user_rows_after": after_user_count,
        "live_agent_profiles_created": live_agent_profiles_created,
        "user_profiles_created": user_rows_created,
    }

    # Determine verdict strictly.
    blockers: List[Tuple[str, str]] = []
    if error:
        blockers.append(("IV_SCHEMA_MIGRATION_EXCEPTION", error))
    if missing_agent:
        blockers.append(("IV_AGENT_REQUIRED_COLUMNS_MISSING", str(missing_agent)))
    if missing_user:
        blockers.append(("IV_USER_REQUIRED_COLUMNS_MISSING", str(missing_user)))
    if missing_indexes:
        blockers.append(("IV_REQUIRED_INDEXES_MISSING", str(missing_indexes)))
    if not safety["env_stat_unchanged"]:
        blockers.append(("IV_ENV_STAT_CHANGED", ".env stat metadata changed unexpectedly"))
    if not safety["legacy_db_unchanged"]:
        blockers.append(("IV_LEGACY_DB_CHANGED", "legacy vault.db changed unexpectedly"))
    if not safety["identity_contract_draft_unchanged"] or not safety["aiweb_identity_contract_unchanged"]:
        blockers.append(("IV_CONTRACT_CHANGED", "identity contract changed unexpectedly"))
    if safety["forge_tool_registry_modified"]:
        blockers.append(("IV_FORGE_TOOL_REGISTRY_CHANGED", "Forge tool registry changed unexpectedly"))
    if safety["database_content_rows_created"]:
        blockers.append(("IV_PROFILE_ROWS_CREATED", "profile rows changed unexpectedly"))

    if blockers:
        verdict = "FAIL"
        for code, msg in blockers:
            findings.append({"level": "FAIL", "code": code, "message": msg})
    else:
        findings.append({"level": "INFO", "code": "IV_SCHEMA_MIGRATION_APPLIED", "message": "Operational profile JSON payload and metadata columns are present on canonical Identity Vault tables."})
        findings.append({"level": "INFO", "code": "IV_INDEXES_READY", "message": "Required lookup indexes are present for agent_id, activation_state, rmc_namespace, and user_id."})
        findings.append({"level": "INFO", "code": "IV_NO_PROFILE_ROWS_CREATED", "message": "Schema migration did not create live user or agent profile rows."})
        findings.append({"level": "INFO", "code": "IV_IDENTITIES_REMAIN_INACTIVE", "message": "No identity activation was performed."})

    report: Dict[str, Any] = {
        "timestamp": ts,
        "patch_id": PATCH_ID,
        "verdict": verdict,
        "boundary": boundary,
        "backup_root": str(backup_root),
        "backup": backup,
        "canonical_db": str(CANONICAL_DB),
        "legacy_db": str(LEGACY_DB),
        "before": before,
        "after": after,
        "sql_actions": sql_actions,
        "required_checks": required_checks,
        "no_live_profile_checks": no_live_profile_checks,
        "safety": safety,
        "hashes": {"before": before_hashes, "after": after_hashes},
        "env_stat": {"before": env_stat_before, "after": env_stat_after},
        "findings": findings,
    }

    json_path = run_dir / f"{ts}_{REPORT_ROOT_NAME.replace('_v1','')}.json"
    md_path = run_dir / f"{ts}_{REPORT_ROOT_NAME.replace('_v1','')}.md"
    json_text = json.dumps(report, indent=2, sort_keys=True)
    json_path.write_text(json_text + "\n", encoding="utf-8")
    latest_json.write_text(json_text + "\n", encoding="utf-8")
    md_text = build_report_md(report)
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")

    print("Identity Vault Patch 226 schema migration apply complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
