#!/usr/bin/env python3
"""Patch 226B — Identity Vault legacy profile/template migration preview.

Read-only scanner. It inventories legacy Identity Vault profile/session rows,
compares local templates to the Self-Hosted Identity Vault blueprint field set,
and writes a migration preview under Forge memory. It does not write any
Identity Vault database, create profiles, activate identities, or read .env
secret values.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import sqlite3
import stat
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
IDENTITY_ROOT = HOME / "identity-vault"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"
REPORT_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch226b_legacy_profile_migration_preview_v1"

USER_BLUEPRINT_FIELDS = [
    "user_id",
    "canonical_name",
    "spirit_name",
    "project_affiliations",
    "identity_tags",
    "version",
    "last_updated",
    "project_context",
    "interaction_preferences",
    "meta_rules",
    "session_state",
]

AGENT_BLUEPRINT_FIELDS = [
    "agent_id",
    "canonical_name",
    "version",
    "last_updated",
    "role",
    "symbolic_signature",
    "description",
    "capabilities",
    "limitations",
    "persona",
    "voice_style",
    "quotes_or_character_inspiration",
    "special_style_notes",
    "permissions",
    "authority",
    "enforcement_rules",
    "forbidden_actions",
    "session_state",
    "last_action",
    "last_feedback",
    "log_fields",
    "timestamp",
]


def utc_ts() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def stat_metadata(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False, "path": str(path)}
    st = path.stat()
    return {
        "exists": True,
        "path": str(path),
        "size": st.st_size,
        "mode": oct(stat.S_IMODE(st.st_mode)),
        "mtime_ns": st.st_mtime_ns,
    }


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ro_connect(db_path: Path) -> sqlite3.Connection:
    uri = f"file:{db_path}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def sqlite_summary(db_path: Path, preview_tables: List[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"path": str(db_path), "exists": db_path.exists(), "opened_readonly": False, "ok": False}
    if not db_path.exists():
        out["error"] = "missing"
        return out
    try:
        with ro_connect(db_path) as con:
            con.row_factory = sqlite3.Row
            out["opened_readonly"] = True
            tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
            out["tables"] = tables
            row_counts = {}
            schemas = {}
            previews = {}
            for table in tables:
                try:
                    row_counts[table] = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    schemas[table] = [r[1] for r in con.execute(f"PRAGMA table_info({table})")]
                except Exception as exc:  # pragma: no cover
                    row_counts[table] = f"ERROR: {exc}"
            for table in preview_tables:
                if table not in tables:
                    continue
                rows = []
                cols = schemas.get(table, [])
                safe_cols = [c for c in cols if c not in {"password", "secret", "token", "key"}]
                select_cols = ", ".join(safe_cols) if safe_cols else "*"
                for row in con.execute(f"SELECT {select_cols} FROM {table} LIMIT 10"):
                    item = dict(row)
                    if table == "profiles" and "data" in item:
                        item["data"] = classify_payload(str(item.get("data") or ""))
                    rows.append(item)
                previews[table] = rows
            out.update({"ok": True, "row_counts": row_counts, "schemas": schemas, "previews": previews})
    except Exception as exc:
        out["error"] = repr(exc)
    return out


def classify_payload(value: str) -> Dict[str, Any]:
    segments = value.split(":") if value else []
    hexish = bool(value) and all(re.fullmatch(r"[0-9a-fA-F]+", seg or "") for seg in segments)
    jsonish = False
    parsed_type = None
    if value.strip().startswith(("{", "[")):
        try:
            parsed = json.loads(value)
            jsonish = True
            parsed_type = type(parsed).__name__
        except Exception:
            jsonish = False
    return {
        "redacted": True,
        "length": len(value),
        "sha16": hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:16] if value else None,
        "colon_segment_count": len(segments),
        "segment_lengths": [len(s) for s in segments[:6]],
        "format_guess": "json_plaintext" if jsonish else ("colon_delimited_ciphertext_or_encoded_payload" if hexish and len(segments) >= 2 else "unknown_or_plaintext"),
        "json_type": parsed_type,
    }


def load_template(path: Path, required_fields: List[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"path": str(path), "exists": path.exists(), "json_ok": False}
    if not path.exists():
        return out
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        keys = sorted(data.keys()) if isinstance(data, dict) else []
        missing = [f for f in required_fields if f not in keys]
        present = [f for f in required_fields if f in keys]
        out.update({
            "json_ok": True,
            "top_level_keys": keys,
            "required_present": present,
            "required_missing": missing,
            "alignment": f"{len(present)}/{len(required_fields)}",
            "sha16": sha256_file(path)[:16] if sha256_file(path) else None,
        })
    except Exception as exc:
        out["error"] = repr(exc)
    return out


def build_migration_preview(legacy: Dict[str, Any]) -> Dict[str, Any]:
    profile_rows = legacy.get("previews", {}).get("profiles", []) or []
    session_rows = {row.get("id"): row for row in legacy.get("previews", {}).get("session_state", []) or []}
    previews = []
    for row in profile_rows:
        profile_id = row.get("id")
        payload = row.get("data") if isinstance(row.get("data"), dict) else classify_payload(str(row.get("data") or ""))
        row_type = row.get("type")
        session = session_rows.get(profile_id, {})
        if row_type == "user":
            mapped = {
                "target_table": "user_profiles",
                "target_lookup_id": profile_id,
                "write_status": "PREVIEW_ONLY_NOT_WRITTEN",
                "can_auto_migrate_full_profile": payload.get("format_guess") == "json_plaintext",
                "reason": "Legacy payload is encrypted/encoded or not safely readable as blueprint JSON; preserve source reference and create/verify profile manually unless app-level decryption is explicitly approved.",
                "suggested_core_fields": {
                    "user_id": profile_id,
                    "canonical_name": "",
                    "version": row.get("version") or "1.0.0",
                    "is_active": 0,
                    "profile_schema_version": "1.0.0-blueprint",
                },
                "suggested_operational_profile_json_skeleton": {
                    "user_id": profile_id,
                    "canonical_name": "",
                    "spirit_name": "",
                    "project_affiliations": [],
                    "identity_tags": [],
                    "version": row.get("version") or "1.0.0",
                    "last_updated": row.get("last_updated") or session.get("timestamp") or "",
                    "project_context": {
                        "current_project": "AI.Web",
                        "phase": session.get("phase") or "",
                        "current_files": [],
                        "active_collaborators": [],
                        "subsystems": ["Identity Vault", "Forge", "RMC"],
                        "goals": [],
                    },
                    "interaction_preferences": {},
                    "meta_rules": {},
                    "session_state": {
                        "phase": session.get("phase") or "",
                        "waiting_for": session.get("waiting_for") or "",
                        "last_feedback": session.get("last_feedback") or "",
                        "last_action": session.get("last_action") or "",
                        "timestamp": session.get("timestamp") or row.get("last_updated") or "",
                    },
                    "legacy_migration_reference": {
                        "source_database": str(LEGACY_DB),
                        "source_table": "profiles",
                        "source_id": profile_id,
                        "payload_format_guess": payload.get("format_guess"),
                        "payload_sha16": payload.get("sha16"),
                    },
                },
            }
        else:
            mapped = {
                "target_table": "unknown",
                "target_lookup_id": profile_id,
                "write_status": "PREVIEW_ONLY_NOT_WRITTEN",
                "can_auto_migrate_full_profile": False,
                "reason": f"Unsupported legacy profile type: {row_type}",
            }
        previews.append(mapped)
    return {"count": len(previews), "previews": previews}


def main() -> int:
    ts = utc_ts()
    run_dir = REPORT_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    latest_md = REPORT_ROOT / "latest_identity_vault_patch226b_legacy_profile_migration_preview.md"
    latest_json = REPORT_ROOT / "latest_identity_vault_patch226b_legacy_profile_migration_preview.json"

    before = {
        "env": stat_metadata(IDENTITY_ROOT / ".env"),
        "canonical_db_sha": sha256_file(CANONICAL_DB),
        "legacy_db_sha": sha256_file(LEGACY_DB),
    }

    canonical = sqlite_summary(CANONICAL_DB, ["agent_profiles", "user_profiles", "session_state"])
    legacy = sqlite_summary(LEGACY_DB, ["profiles", "session_state"])
    user_template = load_template(IDENTITY_ROOT / "templates" / "user-template.json", USER_BLUEPRINT_FIELDS)
    agent_template = load_template(IDENTITY_ROOT / "templates" / "agent-template.json", AGENT_BLUEPRINT_FIELDS)
    migration_preview = build_migration_preview(legacy)

    after = {
        "env": stat_metadata(IDENTITY_ROOT / ".env"),
        "canonical_db_sha": sha256_file(CANONICAL_DB),
        "legacy_db_sha": sha256_file(LEGACY_DB),
    }

    safety = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before["env"] == after["env"],
        "canonical_db_sha_unchanged": before["canonical_db_sha"] == after["canonical_db_sha"],
        "legacy_db_sha_unchanged": before["legacy_db_sha"] == after["legacy_db_sha"],
        "database_write_performed": False,
        "profiles_created": False,
        "agent_identity_activation_performed": False,
    }

    legacy_profile_count = (legacy.get("row_counts") or {}).get("profiles", 0) if legacy.get("ok") else 0
    encrypted_like = any(
        isinstance(row.get("data"), dict) and row["data"].get("format_guess") == "colon_delimited_ciphertext_or_encoded_payload"
        for row in (legacy.get("previews", {}).get("profiles", []) or [])
    )
    verdict = "WARN" if legacy_profile_count or encrypted_like else "PASS"
    if not all(safety.values()):
        verdict = "FAIL"

    report = {
        "timestamp": ts,
        "verdict": verdict,
        "boundary": {
            "read_only_except_reports": True,
            "env_secret_values_read": False,
            "database_writes": False,
            "profile_creation": False,
            "identity_activation": False,
        },
        "canonical": canonical,
        "legacy": legacy,
        "templates": {"user": user_template, "agent": agent_template},
        "migration_preview": migration_preview,
        "safety": safety,
    }

    (run_dir / f"{ts}_identity_vault_patch226b_legacy_profile_migration_preview.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    latest_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Identity Vault Patch 226B Legacy Profile Migration Preview")
    lines.append("")
    lines.append(f"Timestamp: `{ts}`")
    lines.append(f"Verdict: **{verdict}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This patch is read-only except for writing reports under Forge memory.")
    lines.append("- It reads canonical and legacy SQLite databases through read-only connections.")
    lines.append("- It does not read `.env` secret values.")
    lines.append("- It does not write databases, create profiles, or activate identities.")
    lines.append("")
    lines.append("## Canonical Database")
    lines.append(f"- path: `{CANONICAL_DB}` opened_readonly=`{canonical.get('opened_readonly')}` ok=`{canonical.get('ok')}`")
    lines.append(f"- row counts: `{canonical.get('row_counts')}`")
    lines.append("")
    lines.append("## Legacy Database")
    lines.append(f"- path: `{LEGACY_DB}` opened_readonly=`{legacy.get('opened_readonly')}` ok=`{legacy.get('ok')}`")
    lines.append(f"- row counts: `{legacy.get('row_counts')}`")
    if legacy.get("schemas"):
        lines.append("- schemas:")
        for table, cols in legacy["schemas"].items():
            lines.append(f"  - `{table}`: `{', '.join(cols)}`")
    lines.append("")
    lines.append("### Legacy Profile Preview")
    rows = legacy.get("previews", {}).get("profiles", []) or []
    if rows:
        lines.append("```json")
        lines.append(json.dumps(rows, indent=2))
        lines.append("```")
    else:
        lines.append("- No legacy profile rows found.")
    lines.append("")
    lines.append("## Template Alignment")
    lines.append(f"- user template exists=`{user_template.get('exists')}` json_ok=`{user_template.get('json_ok')}` alignment=`{user_template.get('alignment')}`")
    if user_template.get("required_missing"):
        lines.append(f"  - missing user blueprint fields: `{', '.join(user_template['required_missing'])}`")
    lines.append(f"- agent template exists=`{agent_template.get('exists')}` json_ok=`{agent_template.get('json_ok')}` alignment=`{agent_template.get('alignment')}`")
    if agent_template.get("required_missing"):
        lines.append(f"  - missing agent blueprint fields: `{', '.join(agent_template['required_missing'])}`")
    lines.append("")
    lines.append("## Migration Preview")
    lines.append(f"- preview records: `{migration_preview.get('count')}`")
    if migration_preview.get("previews"):
        lines.append("```json")
        lines.append(json.dumps(migration_preview["previews"], indent=2))
        lines.append("```")
    lines.append("")
    lines.append("## Safety Checks")
    for k, v in safety.items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Findings")
    if legacy_profile_count:
        lines.append(f"- **WARN** `IV_LEGACY_PROFILE_PRESENT` — Legacy Vault has `{legacy_profile_count}` profile row(s).")
    if encrypted_like:
        lines.append("- **WARN** `IV_LEGACY_PAYLOAD_NOT_PLAINTEXT_JSON` — Legacy payload appears encrypted/encoded, so this patch does not map private content into the canonical profile.")
    if user_template.get("json_ok"):
        lines.append("- **INFO** `IV_USER_TEMPLATE_READABLE` — Local user template is readable for draft creation.")
    if agent_template.get("json_ok"):
        lines.append("- **INFO** `IV_AGENT_TEMPLATE_READABLE` — Local agent template is readable for draft creation.")
    lines.append("- **INFO** `IV_NO_MUTATION` — No profiles were created and no identities were activated.")
    lines.append("")
    lines.append("## Recommended Next Safe Step")
    lines.append("If the legacy `user789` encrypted/encoded row is not useful, create inactive draft canonical profiles from the Identity Vault blueprint/templates: one Nic user profile and inactive Gilligan/Athena/Neo agent profiles. Preserve the legacy row as a migration reference only. Do not activate identities yet.")

    md = "\n".join(lines) + "\n"
    (run_dir / f"{ts}_identity_vault_patch226b_legacy_profile_migration_preview.md").write_text(md, encoding="utf-8")
    latest_md.write_text(md, encoding="utf-8")

    print("Identity Vault Patch 226B legacy profile migration preview complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {verdict}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
