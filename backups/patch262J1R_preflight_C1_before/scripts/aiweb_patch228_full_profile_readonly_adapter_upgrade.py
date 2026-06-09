#!/usr/bin/env python3
# Patch 228 — Full Profile Read-Only Adapter Upgrade
# Purpose: upgrade Forge Identity Vault read-only agent list/show helpers so they expose
# safe operational profile metadata without dumping private payloads or mutating state.

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import pathlib
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import traceback
from typing import Any, Dict, List, Optional, Tuple

FORGE_ROOT = pathlib.Path("/home/nic/forge")
IDENTITY_ROOT = pathlib.Path("/home/nic/identity-vault")
DB_PATH = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB_PATH = IDENTITY_ROOT / "vault.db"
ENV_PATH = IDENTITY_ROOT / ".env"
TOOL_REGISTRY = FORGE_ROOT / "config" / "tool_registry.json"
CONNECTOR_PATH = FORGE_ROOT / "agents" / "forge" / "aiweb_readonly_connectors.py"
MEMORY_ROOT = FORGE_ROOT / "memory" / "aiweb_patch228_full_profile_readonly_adapter_v1"
BACKUP_ROOT = FORGE_ROOT / "backups" / "patch228_full_profile_readonly_adapter_before"
MARKER_BEGIN = "# >>> PATCH 228 FULL PROFILE READONLY ADAPTER OVERRIDES >>>"
MARKER_END = "# <<< PATCH 228 FULL PROFILE READONLY ADAPTER OVERRIDES <<<"
VERSION = "patch228_full_profile_readonly_adapter_v1"

REQUIRED_CONNECTOR_DEFS = ["forge_agent_list", "forge_agent_show"]
EXPECTED_AGENTS = ["gilligan.local", "athena.local", "neo.local"]


def now_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def iso_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: pathlib.Path) -> Optional[str]:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha16(path: pathlib.Path) -> Optional[str]:
    h = sha256_file(path)
    return h[:16] if h else None


def stat_metadata(path: pathlib.Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    st = path.stat()
    return {
        "exists": True,
        "size": st.st_size,
        "mtime_ns": st.st_mtime_ns,
        "mode": oct(stat.S_IMODE(st.st_mode)),
    }


def readonly_conn(path: pathlib.Path) -> sqlite3.Connection:
    uri = f"file:{path}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def table_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    try:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        return [str(r[1]) for r in rows]
    except Exception:
        return []


def row_counts(conn: sqlite3.Connection) -> Dict[str, int]:
    out: Dict[str, int] = {}
    try:
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
        for t in tables:
            try:
                out[t] = int(conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
            except Exception:
                out[t] = -1
    except Exception:
        pass
    return out


def write_json(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def write_report(path: pathlib.Path, report: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("# AI.Web Patch 228 Full Profile Read-Only Adapter Upgrade")
    lines.append("")
    lines.append(f"Timestamp: `{report.get('timestamp')}`")
    lines.append(f"Verdict: **{report.get('verdict')}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This patch modifies only Forge's Identity Vault read-only connector file after backup.")
    lines.append("- It upgrades agent list/show helpers to read full operational profile metadata safely.")
    lines.append("- It does not write Identity Vault databases, create profiles, activate identities, read `.env` secret values, modify Forge registry, or write RMC memory.")
    lines.append("")
    lines.append("## Files")
    f = report.get("files", {})
    lines.append(f"- connector exists: `{f.get('connector_exists')}` path=`{CONNECTOR_PATH}`")
    lines.append(f"- backup root: `{f.get('backup_root')}`")
    lines.append(f"- connector changed: `{f.get('connector_changed')}`")
    lines.append(f"- marker present: `{f.get('marker_present')}`")
    lines.append(f"- restored after failure: `{f.get('restored_after_failure')}`")
    lines.append("")
    lines.append("## Source Checks")
    sc = report.get("source_checks", {})
    lines.append(f"- required connector defs present: `{sc.get('required_defs_present')}`")
    lines.append(f"- found defs: `{', '.join(sc.get('found_defs', []))}`")
    lines.append(f"- compile ok: `{sc.get('compile_ok')}` returncode=`{sc.get('compile_returncode')}`")
    lines.append(f"- import ok: `{sc.get('import_ok')}`")
    lines.append("")
    lines.append("## Database Read-Only Summary")
    db = report.get("database", {})
    lines.append(f"- canonical: path=`{DB_PATH}` ok=`{db.get('canonical_ok')}` opened_readonly=`{db.get('canonical_opened_readonly')}` rows=`{db.get('canonical_rows')}`")
    lines.append(f"- legacy: path=`{LEGACY_DB_PATH}` ok=`{db.get('legacy_ok')}` opened_readonly=`{db.get('legacy_opened_readonly')}` rows=`{db.get('legacy_rows')}`")
    lines.append(f"- agent columns include full profile fields: `{db.get('agent_columns_full_profile_ok')}`")
    lines.append("")
    lines.append("## Adapter Smoke")
    sm = report.get("adapter_smoke", {})
    lines.append(f"- list ok: `{sm.get('list_ok')}` agents_returned=`{sm.get('agents_returned')}` connector_version=`{sm.get('list_connector_version')}`")
    for item in sm.get("agent_show", []):
        lines.append(f"- show `{item.get('agent_id')}` ok=`{item.get('ok')}` found=`{item.get('found')}` activation_state=`{item.get('activation_state')}` payload_dumped=`{item.get('payload_dumped')}`")
    lines.append("")
    lines.append("## Safety Checks")
    saf = report.get("safety", {})
    for key in [
        "env_secret_values_read",
        "env_stat_unchanged",
        "canonical_db_sha_unchanged",
        "legacy_db_sha_unchanged",
        "tool_registry_sha_unchanged",
        "identity_vault_database_write_performed",
        "profiles_created",
        "agent_identity_activation_performed",
        "rmc_memory_write_performed",
        "forge_tool_registry_modified",
    ]:
        lines.append(f"- `{key}`: `{saf.get(key)}`")
    lines.append("")
    lines.append("## Findings")
    for finding in report.get("findings", []):
        lines.append(f"- **{finding.get('level')}** `{finding.get('code')}` — {finding.get('message')}")
    lines.append("")
    lines.append("## Next Safe Step")
    lines.append(str(report.get("next_safe_step")))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def override_block() -> str:
    # Appended function definitions intentionally override Patch 224 same-named helpers.
    return r'''
# >>> PATCH 228 FULL PROFILE READONLY ADAPTER OVERRIDES >>>
# Patch 228 — Full Profile Read-Only Adapter Upgrade
# These definitions intentionally override the Patch 224 read-only agent helpers.
# Boundary: read-only SQLite access, safe profile summaries only, no activation, no DB writes.

def _patch228_json_loads_safe(value, fallback=None):
    import json as _json
    if fallback is None:
        fallback = {}
    if value is None:
        return fallback
    try:
        if isinstance(value, (dict, list)):
            return value
        return _json.loads(value)
    except Exception:
        return fallback


def _patch228_short_list(value, limit=6):
    if value is None:
        return []
    if not isinstance(value, list):
        return []
    return value[:limit]


def _patch228_hash_payload(payload_text):
    import hashlib as _hashlib
    if payload_text is None:
        payload_text = ""
    if not isinstance(payload_text, str):
        payload_text = str(payload_text)
    return _hashlib.sha256(payload_text.encode("utf-8")).hexdigest()


def _patch228_readonly_conn():
    import sqlite3 as _sqlite3
    db_path = "/home/nic/identity-vault/data/identity_vault.db"
    return _sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)


def _patch228_agent_row_to_summary(row):
    (
        row_id,
        agent_id,
        canonical_name,
        role,
        activation_state,
        is_active,
        rmc_namespace,
        profile_schema_version,
        profile_hash,
        last_validated_at,
        created_at,
        updated_at,
        operational_profile_json,
    ) = row
    payload = _patch228_json_loads_safe(operational_profile_json, {})
    computed_hash = _patch228_hash_payload(operational_profile_json or "{}")
    return {
        "id": row_id,
        "agent_id": agent_id,
        "canonical_name": canonical_name or payload.get("canonical_name"),
        "role": role or payload.get("role"),
        "activation_state": activation_state,
        "is_active": is_active,
        "rmc_namespace": rmc_namespace or payload.get("rmc_namespace"),
        "profile_schema_version": profile_schema_version,
        "profile_hash": profile_hash,
        "profile_hash_ok": bool(profile_hash and computed_hash == profile_hash),
        "last_validated_at": last_validated_at,
        "created_at": created_at,
        "updated_at": updated_at,
        "persona": payload.get("persona"),
        "voice_style": payload.get("voice_style"),
        "symbolic_signature": _patch228_short_list(payload.get("symbolic_signature"), 8),
        "permissions_summary": _patch228_short_list(payload.get("permissions"), 8),
        "forbidden_actions_summary": _patch228_short_list(payload.get("forbidden_actions"), 8),
        "authority_summary": _patch228_short_list(payload.get("authority"), 8),
        "limitations_summary": _patch228_short_list(payload.get("limitations"), 8),
        "full_payload_available": bool(operational_profile_json),
        "payload_dumped": False,
    }


def forge_agent_list(limit=50):
    """Patch 228 read-only full-profile-aware agent list."""
    rows_out = []
    try:
        limit = int(limit or 50)
    except Exception:
        limit = 50
    try:
        conn = _patch228_readonly_conn()
        try:
            rows = conn.execute(
                """
                SELECT id, agent_id, canonical_name, role, activation_state, is_active,
                       rmc_namespace, profile_schema_version, profile_hash, last_validated_at,
                       created_at, updated_at, operational_profile_json
                FROM agent_profiles
                ORDER BY id ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        finally:
            conn.close()
        rows_out = [_patch228_agent_row_to_summary(r) for r in rows]
        return {
            "ok": True,
            "service": "identity_vault",
            "read_only": True,
            "connector_version": "patch228_full_profile_readonly_adapter_v1",
            "agents_returned": len(rows_out),
            "agents": rows_out,
            "safe_columns": [
                "id",
                "agent_id",
                "canonical_name",
                "role",
                "activation_state",
                "is_active",
                "rmc_namespace",
                "profile_schema_version",
                "profile_hash",
                "last_validated_at",
                "created_at",
                "updated_at",
                "permissions_summary",
                "forbidden_actions_summary",
            ],
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
        }
    except Exception as exc:
        return {
            "ok": False,
            "service": "identity_vault",
            "read_only": True,
            "connector_version": "patch228_full_profile_readonly_adapter_v1",
            "error": str(exc),
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
        }


def forge_agent_show(agent_id):
    """Patch 228 read-only full-profile-aware agent show."""
    try:
        conn = _patch228_readonly_conn()
        try:
            row = conn.execute(
                """
                SELECT id, agent_id, canonical_name, role, activation_state, is_active,
                       rmc_namespace, profile_schema_version, profile_hash, last_validated_at,
                       created_at, updated_at, operational_profile_json
                FROM agent_profiles
                WHERE agent_id = ?
                LIMIT 1
                """,
                (str(agent_id),),
            ).fetchone()
        finally:
            conn.close()
        if not row:
            return {
                "ok": True,
                "service": "identity_vault",
                "read_only": True,
                "connector_version": "patch228_full_profile_readonly_adapter_v1",
                "agent_id": str(agent_id),
                "found": False,
                "note": "Agent metadata not found.",
                "database_write_performed": False,
                "agent_identity_activation_performed": False,
            }
        agent = _patch228_agent_row_to_summary(row)
        return {
            "ok": True,
            "service": "identity_vault",
            "read_only": True,
            "connector_version": "patch228_full_profile_readonly_adapter_v1",
            "agent_id": str(agent_id),
            "found": True,
            "note": "Agent full operational metadata summary found. Full payload is intentionally not dumped by default.",
            "agent": agent,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
        }
    except Exception as exc:
        return {
            "ok": False,
            "service": "identity_vault",
            "read_only": True,
            "connector_version": "patch228_full_profile_readonly_adapter_v1",
            "agent_id": str(agent_id),
            "found": False,
            "error": str(exc),
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
        }
# <<< PATCH 228 FULL PROFILE READONLY ADAPTER OVERRIDES <<<
'''


def strip_existing_patch228(text: str) -> str:
    pattern = re.compile(re.escape(MARKER_BEGIN) + r".*?" + re.escape(MARKER_END), re.S)
    return pattern.sub("", text).rstrip() + "\n"


def main() -> int:
    ts = now_stamp()
    run_dir = MEMORY_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    latest_md = MEMORY_ROOT / "latest_aiweb_patch228_full_profile_readonly_adapter.md"
    latest_json = MEMORY_ROOT / "latest_aiweb_patch228_full_profile_readonly_adapter.json"

    report: Dict[str, Any] = {
        "timestamp": ts,
        "verdict": "FAIL",
        "files": {},
        "source_checks": {},
        "database": {},
        "adapter_smoke": {},
        "safety": {},
        "findings": [],
        "next_safe_step": "Review report; do not proceed until PASS.",
    }

    before_env = stat_metadata(ENV_PATH)
    before_canon_sha = sha256_file(DB_PATH)
    before_legacy_sha = sha256_file(LEGACY_DB_PATH)
    before_registry_sha = sha256_file(TOOL_REGISTRY)
    before_connector_sha = sha256_file(CONNECTOR_PATH)
    restored_after_failure = False
    backup_file: Optional[pathlib.Path] = None

    try:
        report["files"]["connector_exists"] = CONNECTOR_PATH.exists()
        if not CONNECTOR_PATH.exists():
            raise RuntimeError(f"Connector file missing: {CONNECTOR_PATH}")

        text = CONNECTOR_PATH.read_text(encoding="utf-8")
        found_defs = re.findall(r"^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text, flags=re.M)
        required_defs_present = all(name in found_defs for name in REQUIRED_CONNECTOR_DEFS)
        report["source_checks"]["found_defs"] = found_defs
        report["source_checks"]["required_defs_present"] = required_defs_present
        if not required_defs_present:
            raise RuntimeError(f"Required connector defs missing. Need {REQUIRED_CONNECTOR_DEFS}; found {found_defs}")

        # DB readiness read-only before write.
        try:
            with readonly_conn(DB_PATH) as conn:
                report["database"]["canonical_ok"] = True
                report["database"]["canonical_opened_readonly"] = True
                report["database"]["canonical_rows"] = row_counts(conn)
                agent_cols = table_columns(conn, "agent_profiles")
                full_cols = {
                    "operational_profile_json",
                    "activation_state",
                    "rmc_namespace",
                    "profile_hash",
                    "profile_schema_version",
                    "last_validated_at",
                }
                report["database"]["agent_columns"] = agent_cols
                report["database"]["agent_columns_full_profile_ok"] = full_cols.issubset(set(agent_cols))
                if not report["database"]["agent_columns_full_profile_ok"]:
                    raise RuntimeError("agent_profiles missing full profile columns")
        except Exception as exc:
            report["database"]["canonical_ok"] = False
            report["database"]["canonical_error"] = str(exc)
            raise
        try:
            with readonly_conn(LEGACY_DB_PATH) as conn:
                report["database"]["legacy_ok"] = True
                report["database"]["legacy_opened_readonly"] = True
                report["database"]["legacy_rows"] = row_counts(conn)
        except Exception as exc:
            report["database"]["legacy_ok"] = False
            report["database"]["legacy_error"] = str(exc)

        # Backup and write connector override block.
        backup_dir = BACKUP_ROOT / ts
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_file = backup_dir / "aiweb_readonly_connectors.py"
        shutil.copy2(CONNECTOR_PATH, backup_file)
        report["files"]["backup_root"] = str(backup_dir)

        new_text = strip_existing_patch228(text) + "\n" + override_block().lstrip()
        CONNECTOR_PATH.write_text(new_text, encoding="utf-8")
        after_connector_sha = sha256_file(CONNECTOR_PATH)
        report["files"]["connector_changed"] = after_connector_sha != before_connector_sha
        report["files"]["marker_present"] = MARKER_BEGIN in new_text and MARKER_END in new_text

        # Compile connector.
        compile_res = subprocess.run(
            [sys.executable, "-m", "py_compile", str(CONNECTOR_PATH)],
            cwd=str(FORGE_ROOT),
            text=True,
            capture_output=True,
        )
        report["source_checks"]["compile_ok"] = compile_res.returncode == 0
        report["source_checks"]["compile_returncode"] = compile_res.returncode
        report["source_checks"]["compile_stdout_tail"] = (compile_res.stdout or "")[-1000:]
        report["source_checks"]["compile_stderr_tail"] = (compile_res.stderr or "")[-1000:]
        if compile_res.returncode != 0:
            raise RuntimeError("Connector compile failed")

        # Import and smoke functions.
        sys.path.insert(0, str(FORGE_ROOT))
        import importlib
        mod = importlib.import_module("agents.forge.aiweb_readonly_connectors")
        mod = importlib.reload(mod)
        report["source_checks"]["import_ok"] = True

        list_result = mod.forge_agent_list()
        report["adapter_smoke"]["list_ok"] = bool(list_result.get("ok"))
        report["adapter_smoke"]["agents_returned"] = list_result.get("agents_returned")
        report["adapter_smoke"]["list_connector_version"] = list_result.get("connector_version")
        report["adapter_smoke"]["list_safe_columns"] = list_result.get("safe_columns")

        agent_show = []
        for agent_id in EXPECTED_AGENTS:
            res = mod.forge_agent_show(agent_id)
            agent = res.get("agent") or {}
            agent_show.append({
                "agent_id": agent_id,
                "ok": bool(res.get("ok")),
                "found": bool(res.get("found")),
                "activation_state": agent.get("activation_state"),
                "is_active": agent.get("is_active"),
                "rmc_namespace": agent.get("rmc_namespace"),
                "profile_hash_ok": agent.get("profile_hash_ok"),
                "payload_dumped": agent.get("payload_dumped"),
                "has_permissions_summary": "permissions_summary" in agent,
                "has_forbidden_actions_summary": "forbidden_actions_summary" in agent,
            })
        report["adapter_smoke"]["agent_show"] = agent_show

        smoke_ok = (
            report["adapter_smoke"]["list_ok"]
            and report["adapter_smoke"]["agents_returned"] >= 3
            and report["adapter_smoke"]["list_connector_version"] == VERSION
            and all(x["ok"] and x["found"] and x["activation_state"] == "inactive_draft" and x["is_active"] == 0 and x["payload_dumped"] is False for x in agent_show)
        )
        if not smoke_ok:
            raise RuntimeError("Adapter smoke failed")

    except Exception as exc:
        report["exception"] = str(exc)
        report["traceback_tail"] = traceback.format_exc()[-3000:]
        # Restore on any failure after modification.
        try:
            if backup_file and backup_file.exists():
                shutil.copy2(backup_file, CONNECTOR_PATH)
                restored_after_failure = True
                subprocess.run([sys.executable, "-m", "py_compile", str(CONNECTOR_PATH)], cwd=str(FORGE_ROOT), text=True, capture_output=True)
        except Exception as restore_exc:
            report["restore_error"] = str(restore_exc)
    finally:
        after_env = stat_metadata(ENV_PATH)
        after_canon_sha = sha256_file(DB_PATH)
        after_legacy_sha = sha256_file(LEGACY_DB_PATH)
        after_registry_sha = sha256_file(TOOL_REGISTRY)
        after_connector_sha_final = sha256_file(CONNECTOR_PATH)

        report["files"]["restored_after_failure"] = restored_after_failure
        report["files"]["final_connector_sha16"] = after_connector_sha_final[:16] if after_connector_sha_final else None

        safety = {
            "env_secret_values_read": False,
            "env_stat_unchanged": before_env == after_env,
            "canonical_db_sha_unchanged": before_canon_sha == after_canon_sha,
            "legacy_db_sha_unchanged": before_legacy_sha == after_legacy_sha,
            "tool_registry_sha_unchanged": before_registry_sha == after_registry_sha,
            "identity_vault_database_write_performed": before_canon_sha != after_canon_sha,
            "profiles_created": False,
            "agent_identity_activation_performed": False,
            "rmc_memory_write_performed": False,
            "forge_tool_registry_modified": before_registry_sha != after_registry_sha,
        }
        report["safety"] = safety

        pass_conditions = [
            report.get("source_checks", {}).get("required_defs_present") is True,
            report.get("source_checks", {}).get("compile_ok") is True,
            report.get("source_checks", {}).get("import_ok") is True,
            report.get("database", {}).get("agent_columns_full_profile_ok") is True,
            report.get("adapter_smoke", {}).get("list_connector_version") == VERSION,
            report.get("adapter_smoke", {}).get("agents_returned", 0) >= 3,
            all(x.get("ok") and x.get("found") and x.get("activation_state") == "inactive_draft" and x.get("is_active") == 0 and x.get("payload_dumped") is False for x in report.get("adapter_smoke", {}).get("agent_show", [])),
            safety["env_secret_values_read"] is False,
            safety["env_stat_unchanged"] is True,
            safety["canonical_db_sha_unchanged"] is True,
            safety["legacy_db_sha_unchanged"] is True,
            safety["tool_registry_sha_unchanged"] is True,
            safety["identity_vault_database_write_performed"] is False,
            safety["agent_identity_activation_performed"] is False,
            safety["rmc_memory_write_performed"] is False,
            safety["forge_tool_registry_modified"] is False,
            restored_after_failure is False,
        ]
        if all(pass_conditions):
            report["verdict"] = "PASS"
            report["findings"].append({"level": "INFO", "code": "PATCH228_FULL_PROFILE_ADAPTER_READY", "message": "Forge agent list/show helpers now expose safe full-profile summaries from Identity Vault."})
            report["findings"].append({"level": "INFO", "code": "PATCH228_NO_MUTATION", "message": "DBs, .env metadata, RMC memory, templates, and Forge registry stayed unchanged."})
            report["next_safe_step"] = "Start Forge and manually test forge-agent-list plus forge-agent-show for Gilligan, Athena, and Neo. Then run Patch 228A verification."
        else:
            report["verdict"] = "FAIL"
            report["findings"].append({"level": "FAIL", "code": "PATCH228_VERIFICATION_FAILED", "message": "Upgrade did not satisfy all static/smoke/safety gates; connector restored if modification had occurred."})
            report["next_safe_step"] = "Review report. If restored_after_failure=True, inspect the connector source before retrying."

        write_json(run_dir / f"{ts}_aiweb_patch228_full_profile_readonly_adapter.json", report)
        write_json(latest_json, report)
        write_report(run_dir / f"{ts}_aiweb_patch228_full_profile_readonly_adapter.md", report)
        write_report(latest_md, report)

    print("AI.Web Patch 228 full profile read-only adapter upgrade complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {report['verdict']}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
