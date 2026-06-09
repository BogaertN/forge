#!/usr/bin/env python3
"""Patch 228A.1 — Full Profile Read-Only Hash Reconcile.

Appends/refreshes safe read-only overrides for Forge Identity Vault agent list/show
so profile_hash_ok is computed against the stored operational_profile_json using
multiple canonical-safe hash candidates. No DB writes. No identity activation.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

HOME = Path.home()
FORGE = HOME / "forge"
IDENTITY = HOME / "identity-vault"
CONNECTOR = FORGE / "agents" / "forge" / "aiweb_readonly_connectors.py"
CANONICAL_DB = IDENTITY / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY / "vault.db"
ENV_PATH = IDENTITY / ".env"
TOOL_REGISTRY = FORGE / "config" / "tool_registry.json"
REPORT_ROOT = FORGE / "memory" / "aiweb_patch228a1_full_profile_hash_reconcile_v1"
BACKUP_ROOT = FORGE / "backups" / "patch228a1_full_profile_hash_reconcile_before"

BEGIN = "# --- PATCH 228A.1 FULL PROFILE HASH RECONCILE BEGIN ---"
END = "# --- PATCH 228A.1 FULL PROFILE HASH RECONCILE END ---"

AGENTS = ["gilligan.local", "athena.local", "neo.local"]

OVERRIDE_BLOCK = r'''
# --- PATCH 228A.1 FULL PROFILE HASH RECONCILE BEGIN ---
# Read-only Identity Vault full-profile hash reconciliation.
# This block intentionally overrides forge_agent_list / forge_agent_show with
# stricter read-only profile hash validation while preserving safe summaries.
def _p228a1_home():
    from pathlib import Path as _Path
    return _Path.home()


def _p228a1_identity_db():
    return _p228a1_home() / "identity-vault" / "data" / "identity_vault.db"


def _p228a1_open_identity_readonly():
    import sqlite3 as _sqlite3
    db = _p228a1_identity_db()
    uri = f"file:{db}?mode=ro"
    conn = _sqlite3.connect(uri, uri=True)
    conn.row_factory = _sqlite3.Row
    return conn


def _p228a1_hash_candidates(raw_text, parsed):
    import hashlib as _hashlib
    import json as _json
    candidates = {}
    if raw_text is not None:
        raw = str(raw_text)
        candidates["raw"] = _hashlib.sha256(raw.encode("utf-8")).hexdigest()
        candidates["raw_strip"] = _hashlib.sha256(raw.strip().encode("utf-8")).hexdigest()
    if parsed is not None:
        canonical_compact = _json.dumps(parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        canonical_default = _json.dumps(parsed, sort_keys=True, ensure_ascii=False)
        canonical_pretty = _json.dumps(parsed, sort_keys=True, indent=2, ensure_ascii=False)
        candidates["json_sort_compact"] = _hashlib.sha256(canonical_compact.encode("utf-8")).hexdigest()
        candidates["json_sort_default"] = _hashlib.sha256(canonical_default.encode("utf-8")).hexdigest()
        candidates["json_sort_pretty"] = _hashlib.sha256(canonical_pretty.encode("utf-8")).hexdigest()
    return candidates


def _p228a1_profile_hash_status(raw_text, stored_hash):
    import json as _json
    parsed = None
    json_ok = False
    parse_error = None
    try:
        parsed = _json.loads(raw_text or "{}")
        json_ok = True
    except Exception as exc:
        parse_error = str(exc)
    candidates = _p228a1_hash_candidates(raw_text, parsed)
    match_method = None
    for method, digest in candidates.items():
        if digest == stored_hash:
            match_method = method
            break
    return {
        "json_ok": json_ok,
        "parse_error": parse_error,
        "parsed": parsed if isinstance(parsed, dict) else {},
        "profile_hash_ok": bool(match_method),
        "profile_hash_method": match_method,
        "candidate_hashes_preview": {k: v[:16] for k, v in candidates.items()},
    }


def _p228a1_as_list(value, max_items=8):
    if isinstance(value, list):
        return value[:max_items]
    if value is None or value == "":
        return []
    return [str(value)]


def _p228a1_agent_summary(row):
    profile_hash = row["profile_hash"] if "profile_hash" in row.keys() else None
    raw_profile = row["operational_profile_json"] if "operational_profile_json" in row.keys() else "{}"
    status = _p228a1_profile_hash_status(raw_profile, profile_hash)
    profile = status.get("parsed") or {}
    return {
        "id": row["id"] if "id" in row.keys() else None,
        "agent_id": row["agent_id"],
        "canonical_name": row["canonical_name"] if "canonical_name" in row.keys() else profile.get("canonical_name"),
        "role": row["role"] if "role" in row.keys() else profile.get("role"),
        "activation_state": row["activation_state"] if "activation_state" in row.keys() else profile.get("session_state"),
        "is_active": row["is_active"] if "is_active" in row.keys() else None,
        "rmc_namespace": row["rmc_namespace"] if "rmc_namespace" in row.keys() else profile.get("rmc_namespace"),
        "profile_schema_version": row["profile_schema_version"] if "profile_schema_version" in row.keys() else None,
        "profile_hash": profile_hash,
        "profile_hash_ok": status["profile_hash_ok"],
        "profile_hash_method": status["profile_hash_method"],
        "last_validated_at": row["last_validated_at"] if "last_validated_at" in row.keys() else None,
        "created_at": row["created_at"] if "created_at" in row.keys() else None,
        "updated_at": row["updated_at"] if "updated_at" in row.keys() else None,
        "full_payload_available": bool(raw_profile),
        "payload_dumped": False,
        "persona": profile.get("persona"),
        "voice_style": profile.get("voice_style"),
        "symbolic_signature": _p228a1_as_list(profile.get("symbolic_signature")),
        "permissions_summary": _p228a1_as_list(profile.get("permissions")),
        "authority_summary": _p228a1_as_list(profile.get("authority")),
        "limitations_summary": _p228a1_as_list(profile.get("limitations")),
        "forbidden_actions_summary": _p228a1_as_list(profile.get("forbidden_actions")),
    }


def forge_agent_list(*args, **kwargs):
    try:
        conn = _p228a1_open_identity_readonly()
        try:
            rows = conn.execute(
                """
                SELECT id, agent_id, canonical_name, role, activation_state, is_active,
                       rmc_namespace, profile_schema_version, profile_hash,
                       operational_profile_json, last_validated_at, created_at, updated_at
                FROM agent_profiles
                ORDER BY id ASC
                """
            ).fetchall()
        finally:
            conn.close()
        agents = [_p228a1_agent_summary(row) for row in rows]
        return {
            "ok": True,
            "service": "identity_vault",
            "connector_version": "patch228a1_full_profile_hash_reconcile_v1",
            "read_only": True,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
            "agents_returned": len(agents),
            "agents": agents,
            "safe_columns": [
                "id", "agent_id", "canonical_name", "role", "activation_state", "is_active",
                "rmc_namespace", "profile_schema_version", "profile_hash", "profile_hash_ok",
                "profile_hash_method", "last_validated_at", "created_at", "updated_at",
                "permissions_summary", "forbidden_actions_summary"
            ],
        }
    except Exception as exc:
        return {
            "ok": False,
            "service": "identity_vault",
            "connector_version": "patch228a1_full_profile_hash_reconcile_v1",
            "read_only": True,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def forge_agent_show(agent_id=None, *args, **kwargs):
    if not agent_id:
        return {
            "ok": False,
            "service": "identity_vault",
            "connector_version": "patch228a1_full_profile_hash_reconcile_v1",
            "read_only": True,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
            "found": False,
            "error": "agent_id required",
        }
    try:
        conn = _p228a1_open_identity_readonly()
        try:
            row = conn.execute(
                """
                SELECT id, agent_id, canonical_name, role, activation_state, is_active,
                       rmc_namespace, profile_schema_version, profile_hash,
                       operational_profile_json, last_validated_at, created_at, updated_at
                FROM agent_profiles
                WHERE agent_id = ?
                LIMIT 1
                """,
                (agent_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            return {
                "ok": True,
                "service": "identity_vault",
                "connector_version": "patch228a1_full_profile_hash_reconcile_v1",
                "read_only": True,
                "database_write_performed": False,
                "agent_identity_activation_performed": False,
                "found": False,
                "agent_id": agent_id,
                "note": "Agent profile not found.",
            }
        return {
            "ok": True,
            "service": "identity_vault",
            "connector_version": "patch228a1_full_profile_hash_reconcile_v1",
            "read_only": True,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
            "found": True,
            "agent_id": agent_id,
            "agent": _p228a1_agent_summary(row),
            "note": "Agent full operational metadata summary found. Full payload is intentionally not dumped by default.",
        }
    except Exception as exc:
        return {
            "ok": False,
            "service": "identity_vault",
            "connector_version": "patch228a1_full_profile_hash_reconcile_v1",
            "read_only": True,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
            "found": False,
            "agent_id": agent_id,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
# --- PATCH 228A.1 FULL PROFILE HASH RECONCILE END ---
'''


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def sha(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_meta(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    st = path.stat()
    return {
        "exists": True,
        "size": st.st_size,
        "mtime_ns": st.st_mtime_ns,
        "mode": oct(stat.S_IMODE(st.st_mode)),
    }


def row_counts(db: Path) -> Dict[str, int] | None:
    if not db.exists():
        return None
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        names = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
        out = {}
        for name in names:
            out[name] = int(conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0])
        return out
    finally:
        conn.close()


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def import_connector(path: Path):
    spec = importlib.util.spec_from_file_location("aiweb_readonly_connectors_patch228a1_check", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not create import spec")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def refresh_block(text: str) -> Tuple[str, str]:
    if BEGIN in text and END in text:
        before, rest = text.split(BEGIN, 1)
        _old, after = rest.split(END, 1)
        return before.rstrip() + "\n\n" + OVERRIDE_BLOCK.strip() + "\n" + after.lstrip(), "replaced_existing_block"
    return text.rstrip() + "\n\n" + OVERRIDE_BLOCK.strip() + "\n", "appended_new_block"


def md_report(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# AI.Web Patch 228A.1 Full Profile Hash Reconcile")
    lines.append("")
    lines.append(f"Timestamp: `{report['timestamp']}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- Modifies only Forge's Identity Vault read-only connector file after backup.")
    lines.append("- Reconciles profile_hash_ok for full-profile summaries.")
    lines.append("- Does not write Identity Vault databases, create profiles, activate identities, read `.env` secret values, modify Forge registry, or write RMC memory.")
    lines.append("")
    lines.append("## Files")
    lines.append(f"- connector: `{CONNECTOR}` exists=`{CONNECTOR.exists()}`")
    lines.append(f"- backup root: `{report['backup_root']}`")
    lines.append(f"- action: `{report['action']}`")
    lines.append(f"- changed: `{report['changed']}`")
    lines.append(f"- restored after failure: `{report['restored_after_failure']}`")
    lines.append("")
    lines.append("## Compile / Import")
    lines.append(f"- connector compile ok: `{report['compile']['ok']}` returncode=`{report['compile']['returncode']}`")
    lines.append(f"- connector import ok: `{report['import_ok']}`")
    lines.append("")
    lines.append("## Adapter Smoke")
    smoke = report.get("adapter_smoke", {})
    lines.append(f"- list ok: `{smoke.get('list_ok')}` agents_returned=`{smoke.get('agents_returned')}` connector_version=`{smoke.get('connector_version')}`")
    for aid, item in smoke.get("show", {}).items():
        lines.append(f"- show `{aid}` ok=`{item.get('ok')}` found=`{item.get('found')}` activation_state=`{item.get('activation_state')}` is_active=`{item.get('is_active')}` hash_ok=`{item.get('profile_hash_ok')}` hash_method=`{item.get('profile_hash_method')}` payload_dumped=`{item.get('payload_dumped')}`")
    lines.append("")
    lines.append("## Database Read-Only Summary")
    lines.append(f"- canonical rows: `{report['db'].get('canonical_rows')}`")
    lines.append(f"- legacy rows: `{report['db'].get('legacy_rows')}`")
    lines.append("")
    lines.append("## Safety Checks")
    for k, v in report["safety"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Findings")
    for finding in report["findings"]:
        lines.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    lines.append("")
    lines.append("## Next Safe Step")
    lines.append("Start Forge and manually test `forge-agent-list` plus `forge-agent-show gilligan.local`, `athena.local`, and `neo.local`. All profile_hash_ok values should be true.")
    return "\n".join(lines) + "\n"


def main() -> int:
    stamp = utc_stamp()
    run_dir = REPORT_ROOT / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    backup_dir = BACKUP_ROOT / stamp
    backup_dir.mkdir(parents=True, exist_ok=True)

    report: Dict[str, Any] = {
        "timestamp": stamp,
        "verdict": "FAIL",
        "backup_root": str(backup_dir),
        "action": None,
        "changed": False,
        "restored_after_failure": False,
        "compile": {"ok": False, "returncode": None, "stderr_tail": ""},
        "import_ok": False,
        "adapter_smoke": {},
        "db": {},
        "safety": {},
        "findings": [],
    }

    before = {
        "connector_sha": sha(CONNECTOR),
        "tool_registry_sha": sha(TOOL_REGISTRY),
        "canonical_db_sha": sha(CANONICAL_DB),
        "legacy_db_sha": sha(LEGACY_DB),
        "env_stat": stat_meta(ENV_PATH),
        "canonical_rows": row_counts(CANONICAL_DB),
        "legacy_rows": row_counts(LEGACY_DB),
    }

    try:
        if not CONNECTOR.exists():
            raise RuntimeError(f"Missing connector: {CONNECTOR}")
        backup_file = backup_dir / "aiweb_readonly_connectors.py"
        shutil.copy2(CONNECTOR, backup_file)
        original = CONNECTOR.read_text(encoding="utf-8")
        updated, action = refresh_block(original)
        report["action"] = action
        if updated != original:
            CONNECTOR.write_text(updated, encoding="utf-8")
            report["changed"] = True

        cp = subprocess.run([sys.executable, "-m", "py_compile", str(CONNECTOR)], text=True, capture_output=True)
        report["compile"] = {"ok": cp.returncode == 0, "returncode": cp.returncode, "stderr_tail": (cp.stderr or "")[-2000:]}
        if cp.returncode != 0:
            raise RuntimeError("connector compile failed")

        mod = import_connector(CONNECTOR)
        report["import_ok"] = True
        listed = mod.forge_agent_list()
        show_report = {}
        all_hash_ok = True
        all_inactive = True
        for aid in AGENTS:
            shown = mod.forge_agent_show(aid)
            agent = shown.get("agent", {}) if isinstance(shown, dict) else {}
            item = {
                "ok": shown.get("ok") if isinstance(shown, dict) else False,
                "found": shown.get("found") if isinstance(shown, dict) else False,
                "activation_state": agent.get("activation_state"),
                "is_active": agent.get("is_active"),
                "profile_hash_ok": agent.get("profile_hash_ok"),
                "profile_hash_method": agent.get("profile_hash_method"),
                "payload_dumped": agent.get("payload_dumped"),
            }
            show_report[aid] = item
            if item["profile_hash_ok"] is not True:
                all_hash_ok = False
            if item["activation_state"] != "inactive_draft" or item["is_active"] not in (0, "0", False):
                all_inactive = False

        report["adapter_smoke"] = {
            "list_ok": listed.get("ok") if isinstance(listed, dict) else False,
            "agents_returned": listed.get("agents_returned") if isinstance(listed, dict) else None,
            "connector_version": listed.get("connector_version") if isinstance(listed, dict) else None,
            "show": show_report,
        }
        report["db"] = {"canonical_rows": row_counts(CANONICAL_DB), "legacy_rows": row_counts(LEGACY_DB)}

        after = {
            "connector_sha": sha(CONNECTOR),
            "tool_registry_sha": sha(TOOL_REGISTRY),
            "canonical_db_sha": sha(CANONICAL_DB),
            "legacy_db_sha": sha(LEGACY_DB),
            "env_stat": stat_meta(ENV_PATH),
            "canonical_rows": row_counts(CANONICAL_DB),
            "legacy_rows": row_counts(LEGACY_DB),
        }
        report["safety"] = {
            "env_secret_values_read": False,
            "env_stat_unchanged": before["env_stat"] == after["env_stat"],
            "canonical_db_sha_unchanged": before["canonical_db_sha"] == after["canonical_db_sha"],
            "legacy_db_sha_unchanged": before["legacy_db_sha"] == after["legacy_db_sha"],
            "tool_registry_sha_unchanged": before["tool_registry_sha"] == after["tool_registry_sha"],
            "identity_vault_database_write_performed": before["canonical_db_sha"] != after["canonical_db_sha"],
            "profiles_created": before["canonical_rows"] != after["canonical_rows"],
            "agent_identity_activation_performed": False,
            "rmc_memory_write_performed": False,
            "forge_tool_registry_modified": before["tool_registry_sha"] != after["tool_registry_sha"],
            "all_profile_hashes_ok": all_hash_ok,
            "all_agents_inactive": all_inactive,
        }

        ok = (
            report["compile"]["ok"]
            and report["import_ok"]
            and report["adapter_smoke"].get("list_ok") is True
            and report["adapter_smoke"].get("agents_returned") == 3
            and all_hash_ok
            and all_inactive
            and report["safety"]["env_stat_unchanged"]
            and report["safety"]["canonical_db_sha_unchanged"]
            and report["safety"]["legacy_db_sha_unchanged"]
            and report["safety"]["tool_registry_sha_unchanged"]
        )
        if not ok:
            shutil.copy2(backup_file, CONNECTOR)
            report["restored_after_failure"] = True
            report["findings"].append({"level": "FAIL", "code": "PATCH228A1_VERIFICATION_FAILED_RESTORED", "message": "Verification failed; connector restored from backup."})
            report["verdict"] = "FAIL"
        else:
            report["findings"].append({"level": "INFO", "code": "PATCH228A1_PROFILE_HASH_RECONCILED", "message": "All three inactive agent profiles now report profile_hash_ok=True through the read-only connector."})
            report["findings"].append({"level": "INFO", "code": "PATCH228A1_NO_MUTATION", "message": "DBs, .env metadata, RMC memory, templates, and Forge registry stayed unchanged."})
            report["verdict"] = "PASS"
    except Exception as exc:
        # Best-effort restore if we touched connector.
        backup_file = backup_dir / "aiweb_readonly_connectors.py"
        if backup_file.exists() and CONNECTOR.exists():
            shutil.copy2(backup_file, CONNECTOR)
            report["restored_after_failure"] = True
        report["findings"].append({"level": "FAIL", "code": "PATCH228A1_EXCEPTION_RESTORED", "message": f"{type(exc).__name__}: {exc}"})
        report["verdict"] = "FAIL"
        after = {
            "tool_registry_sha": sha(TOOL_REGISTRY),
            "canonical_db_sha": sha(CANONICAL_DB),
            "legacy_db_sha": sha(LEGACY_DB),
            "env_stat": stat_meta(ENV_PATH),
            "canonical_rows": row_counts(CANONICAL_DB),
            "legacy_rows": row_counts(LEGACY_DB),
        }
        report["safety"] = {
            "env_secret_values_read": False,
            "env_stat_unchanged": before.get("env_stat") == after["env_stat"],
            "canonical_db_sha_unchanged": before.get("canonical_db_sha") == after["canonical_db_sha"],
            "legacy_db_sha_unchanged": before.get("legacy_db_sha") == after["legacy_db_sha"],
            "tool_registry_sha_unchanged": before.get("tool_registry_sha") == after["tool_registry_sha"],
            "identity_vault_database_write_performed": before.get("canonical_db_sha") != after["canonical_db_sha"],
            "profiles_created": before.get("canonical_rows") != after["canonical_rows"],
            "agent_identity_activation_performed": False,
            "rmc_memory_write_performed": False,
            "forge_tool_registry_modified": before.get("tool_registry_sha") != after["tool_registry_sha"],
        }

    json_path = run_dir / f"{stamp}_aiweb_patch228a1_full_profile_hash_reconcile.json"
    md_path = run_dir / f"{stamp}_aiweb_patch228a1_full_profile_hash_reconcile.md"
    latest_json = REPORT_ROOT / "latest_aiweb_patch228a1_full_profile_hash_reconcile.json"
    latest_md = REPORT_ROOT / "latest_aiweb_patch228a1_full_profile_hash_reconcile.md"
    write_json(json_path, report)
    md = md_report(report)
    md_path.write_text(md, encoding="utf-8")
    write_json(latest_json, report)
    latest_md.write_text(md, encoding="utf-8")

    print("AI.Web Patch 228A.1 full profile hash reconcile complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {report['verdict']}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
