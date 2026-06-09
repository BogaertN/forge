#!/usr/bin/env python3
"""
Patch 226A.2 — Identity Vault Profile Inventory Reconcile
Read-only reconciliation scanner after Patch 226A.1 reported legacy profile rows but failed on a no-mutation predicate.
This script inspects canonical and legacy Identity Vault profile stores without writing DBs, creating profiles, or activating identities.
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
ENV_PATH = IDENTITY_ROOT / ".env"
RUN_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch226a2_profile_inventory_reconcile_v1"

MAX_TEXT = 900
MAX_ROWS = 5


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_UTC")


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_metadata(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    st = path.stat()
    return {
        "exists": True,
        "size": st.st_size,
        "mode": oct(stat.S_IMODE(st.st_mode)),
        "mtime_ns": st.st_mtime_ns,
    }


def open_readonly(path: Path) -> sqlite3.Connection:
    uri = f"file:{path}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def table_names(conn: sqlite3.Connection) -> List[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    return [r[0] for r in rows]


def table_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    rows = conn.execute(f"PRAGMA table_info({quote_ident(table)})").fetchall()
    return [r[1] for r in rows]


def quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def row_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {quote_ident(table)}").fetchone()[0])


def sanitize_value(value: Any) -> Any:
    if value is None or isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, bytes):
        return f"<bytes:{len(value)}>"
    text = str(value)
    # Do not expose obvious token/key/password looking values in profile-ish rows.
    if re.search(r"(secret|token|password|private[_-]?key|jwt|api[_-]?key)", text, re.I):
        return "<redacted:secret-like-value>"
    if len(text) > MAX_TEXT:
        return text[:MAX_TEXT] + f"...<truncated {len(text)-MAX_TEXT} chars>"
    return text


def maybe_json_summary(value: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(value, str):
        return None
    s = value.strip()
    if not (s.startswith("{") or s.startswith("[")):
        return None
    try:
        parsed = json.loads(s)
    except Exception:
        return {"json_like": True, "json_ok": False}
    if isinstance(parsed, dict):
        return {"json_like": True, "json_ok": True, "type": "object", "keys": sorted(list(parsed.keys()))[:80], "key_count": len(parsed)}
    if isinstance(parsed, list):
        return {"json_like": True, "json_ok": True, "type": "array", "length": len(parsed)}
    return {"json_like": True, "json_ok": True, "type": type(parsed).__name__}


def preview_rows(conn: sqlite3.Connection, table: str, limit: int = MAX_ROWS) -> List[Dict[str, Any]]:
    cols = table_columns(conn, table)
    if not cols:
        return []
    rows = conn.execute(f"SELECT * FROM {quote_ident(table)} LIMIT ?", (limit,)).fetchall()
    out: List[Dict[str, Any]] = []
    for row in rows:
        item: Dict[str, Any] = {}
        json_fields: Dict[str, Any] = {}
        for col, val in zip(cols, row):
            item[col] = sanitize_value(val)
            js = maybe_json_summary(val)
            if js:
                json_fields[col] = js
        if json_fields:
            item["_json_field_summaries"] = json_fields
        out.append(item)
    return out


def db_inventory(path: Path, preview_tables: Optional[List[str]] = None) -> Dict[str, Any]:
    result: Dict[str, Any] = {"path": str(path), "exists": path.exists(), "opened_readonly": False, "ok": False}
    if not path.exists():
        return result
    try:
        conn = open_readonly(path)
        result["opened_readonly"] = True
        tables = table_names(conn)
        result["tables"] = tables
        result["row_counts"] = {t: row_count(conn, t) for t in tables}
        result["schemas"] = {t: table_columns(conn, t) for t in tables}
        previews: Dict[str, Any] = {}
        for t in (preview_tables or tables):
            if t in tables:
                previews[t] = preview_rows(conn, t)
        result["previews"] = previews
        conn.close()
        result["ok"] = True
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    return result


def json_file_summary(path: Path) -> Dict[str, Any]:
    info = {"path": str(path.relative_to(IDENTITY_ROOT)), "size": path.stat().st_size, "sha16": sha256_file(path)[:16] if sha256_file(path) else None}
    try:
        text = path.read_text(encoding="utf-8")
        parsed = json.loads(text)
        info["json_ok"] = True
        if isinstance(parsed, dict):
            info["keys"] = sorted(parsed.keys())
            info["key_count"] = len(parsed)
            # Show safe identity hints only.
            for k in ["user_id", "agent_id", "canonical_name", "role", "version", "session_state"]:
                if k in parsed:
                    info[k] = sanitize_value(parsed[k])
        elif isinstance(parsed, list):
            info["type"] = "array"
            info["length"] = len(parsed)
        else:
            info["type"] = type(parsed).__name__
    except Exception as e:
        info["json_ok"] = False
        info["error"] = f"{type(e).__name__}: {e}"
    return info


def candidate_file_inventory() -> Dict[str, Any]:
    candidates: List[Dict[str, Any]] = []
    roots = [IDENTITY_ROOT / "templates", IDENTITY_ROOT / "data", IDENTITY_ROOT / "profiles", IDENTITY_ROOT / "agents"]
    patterns = ["*.json", "*.jsonl", "*.md"]
    for root in roots:
        if not root.exists():
            continue
        for pat in patterns:
            for p in sorted(root.rglob(pat)):
                if "node_modules" in p.parts:
                    continue
                rel = p.relative_to(IDENTITY_ROOT)
                label = "profile_candidate"
                name = p.name.lower()
                if "agent" in name:
                    label = "agent_profile_or_template_candidate"
                elif "user" in name or "profile" in name:
                    label = "user_profile_or_template_candidate"
                item: Dict[str, Any] = {"path": str(rel), "class": label, "size": p.stat().st_size, "sha16": sha256_file(p)[:16] if sha256_file(p) else None}
                if p.suffix.lower() == ".json":
                    item["json_summary"] = json_file_summary(p)
                candidates.append(item)
    return {"count": len(candidates), "items": candidates[:80]}


def make_report(data: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Identity Vault Patch 226A.2 Profile Inventory Reconcile")
    lines.append("")
    lines.append(f"Timestamp: `{data['timestamp']}`")
    lines.append(f"Verdict: **{data['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This reconcile is read-only except for writing reports under Forge memory.")
    lines.append("- It reads canonical and legacy SQLite databases through read-only connections.")
    lines.append("- It does not read `.env` secret values.")
    lines.append("- It does not write databases, create profiles, or activate identities.")
    lines.append("")
    lines.append("## Canonical Database")
    c = data["canonical"]
    lines.append(f"- path: `{c['path']}` exists=`{c.get('exists')}` opened_readonly=`{c.get('opened_readonly')}` ok=`{c.get('ok')}`")
    lines.append(f"- tables: `{', '.join(c.get('tables', []))}`")
    for t, n in c.get("row_counts", {}).items():
        lines.append(f"  - `{t}` rows: `{n}`")
    lines.append("")
    lines.append("## Legacy Database")
    l = data["legacy"]
    lines.append(f"- path: `{l['path']}` exists=`{l.get('exists')}` opened_readonly=`{l.get('opened_readonly')}` ok=`{l.get('ok')}`")
    lines.append(f"- tables: `{', '.join(l.get('tables', []))}`")
    for t, n in l.get("row_counts", {}).items():
        lines.append(f"  - `{t}` rows: `{n}`")
    lines.append("")
    lines.append("### Legacy Schemas")
    for t, cols in l.get("schemas", {}).items():
        lines.append(f"- `{t}` columns: `{', '.join(cols)}`")
    lines.append("")
    lines.append("### Legacy Profile / Session Preview")
    previews = l.get("previews", {})
    for t in ["profiles", "session_state"]:
        rows = previews.get(t, [])
        lines.append(f"- `{t}` preview rows returned: `{len(rows)}`")
        if rows:
            lines.append("```json")
            lines.append(json.dumps(rows, indent=2, ensure_ascii=False))
            lines.append("```")
    lines.append("")
    lines.append("## Candidate Profile / Template Files")
    cf = data["candidate_files"]
    lines.append(f"- candidate files found: `{cf['count']}`")
    for item in cf.get("items", []):
        lines.append(f"- `{item['path']}` class=`{item['class']}` size=`{item['size']}` sha16=`{item['sha16']}`")
        js = item.get("json_summary")
        if js:
            keys = js.get("keys")
            if keys:
                lines.append(f"  - json keys: `{', '.join(keys)}`")
            for hint in ["user_id", "agent_id", "canonical_name", "role", "version"]:
                if hint in js:
                    lines.append(f"  - {hint}: `{js[hint]}`")
    lines.append("")
    lines.append("## Safety Checks")
    for k, v in data["safety"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Findings")
    for f in data["findings"]:
        lines.append(f"- **{f['level']}** `{f['code']}` — {f['message']}")
    lines.append("")
    lines.append("## Recommended Next Safe Step")
    lines.append("Create a migration-preview patch that maps the legacy `user789` profile/session row into the new full operational_profile_json structure without writing it yet. Also compare `templates/user-template.json` and `templates/agent-template.json` against the Self-Hosted Identity Vault blueprint before any profile rows are created.")
    return "\n".join(lines) + "\n"


def main() -> int:
    ts = utc_stamp()
    run_dir = RUN_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    before = {
        "env_stat": stat_metadata(ENV_PATH),
        "canonical_sha": sha256_file(CANONICAL_DB),
        "legacy_sha": sha256_file(LEGACY_DB),
    }

    canonical = db_inventory(CANONICAL_DB, ["agent_profiles", "user_profiles", "session_state"])
    legacy = db_inventory(LEGACY_DB, ["profiles", "session_state"])
    candidate_files = candidate_file_inventory()

    after = {
        "env_stat": stat_metadata(ENV_PATH),
        "canonical_sha": sha256_file(CANONICAL_DB),
        "legacy_sha": sha256_file(LEGACY_DB),
    }

    legacy_profile_rows = legacy.get("row_counts", {}).get("profiles", 0) if legacy.get("ok") else 0
    legacy_session_rows = legacy.get("row_counts", {}).get("session_state", 0) if legacy.get("ok") else 0
    canonical_profile_rows = 0
    if canonical.get("ok"):
        canonical_profile_rows = canonical.get("row_counts", {}).get("agent_profiles", 0) + canonical.get("row_counts", {}).get("user_profiles", 0)

    safety = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before["env_stat"] == after["env_stat"],
        "canonical_db_sha_unchanged": before["canonical_sha"] == after["canonical_sha"],
        "legacy_db_sha_unchanged": before["legacy_sha"] == after["legacy_sha"],
        "database_write_performed": before["canonical_sha"] != after["canonical_sha"] or before["legacy_sha"] != after["legacy_sha"],
        "profiles_created": False,
        "agent_identity_activation_performed": False,
    }

    findings: List[Dict[str, str]] = []
    if canonical.get("ok"):
        findings.append({"level": "INFO", "code": "IV_CANONICAL_DB_READONLY_OK", "message": "Canonical Identity Vault database opened in read-only mode."})
    else:
        findings.append({"level": "FAIL", "code": "IV_CANONICAL_DB_READONLY_FAILED", "message": "Canonical database could not be inspected read-only."})
    if legacy_profile_rows or legacy_session_rows:
        findings.append({"level": "WARN", "code": "IV_LEGACY_PROFILE_ROWS_FOUND", "message": f"Legacy database contains profiles={legacy_profile_rows}, session_state={legacy_session_rows}; review/migration preview is needed before creating new profiles."})
    if canonical_profile_rows == 0:
        findings.append({"level": "INFO", "code": "IV_CANONICAL_PROFILE_ROWS_EMPTY", "message": "Canonical user_profiles and agent_profiles are currently empty."})
    else:
        findings.append({"level": "WARN", "code": "IV_CANONICAL_PROFILE_ROWS_PRESENT", "message": f"Canonical profile rows exist ({canonical_profile_rows}); review before inserts."})
    if candidate_files["count"]:
        findings.append({"level": "WARN", "code": "IV_PROFILE_CANDIDATE_FILES_FOUND", "message": f"Found {candidate_files['count']} local profile/template candidate files for review."})
    if safety["database_write_performed"] or not safety["env_stat_unchanged"]:
        findings.append({"level": "FAIL", "code": "IV_INVENTORY_RECONCILE_SAFETY_FAILED", "message": "A no-mutation safety check failed."})

    verdict = "FAIL" if any(f["level"] == "FAIL" for f in findings) else ("WARN" if any(f["level"] == "WARN" for f in findings) else "PASS")

    data = {
        "timestamp": ts,
        "verdict": verdict,
        "roots": {"identity_vault": str(IDENTITY_ROOT), "canonical_db": str(CANONICAL_DB), "legacy_db": str(LEGACY_DB)},
        "canonical": canonical,
        "legacy": legacy,
        "candidate_files": candidate_files,
        "safety": safety,
        "findings": findings,
    }

    json_path = run_dir / f"{ts}_identity_vault_patch226a2_profile_inventory_reconcile.json"
    md_path = run_dir / f"{ts}_identity_vault_patch226a2_profile_inventory_reconcile.md"
    latest_json = RUN_ROOT / "latest_identity_vault_patch226a2_profile_inventory_reconcile.json"
    latest_md = RUN_ROOT / "latest_identity_vault_patch226a2_profile_inventory_reconcile.md"

    json_text = json.dumps(data, indent=2, ensure_ascii=False)
    report = make_report(data)
    json_path.write_text(json_text, encoding="utf-8")
    md_path.write_text(report, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    latest_md.write_text(report, encoding="utf-8")

    print("Identity Vault Patch 226A.2 profile inventory reconcile complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {verdict}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
