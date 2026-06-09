#!/usr/bin/env python3
"""
Patch 226A.1 — Identity Vault Profile Inventory Scan Hotfix

Read-only inventory scanner for the existing Identity Vault profile state.
This hotfix replaces Patch 226A, which failed because `stat` was not imported.

Boundary:
- Reads canonical and legacy SQLite databases in read-only mode only.
- Does not read .env secret values.
- Does not write Identity Vault databases.
- Does not create profiles.
- Does not activate identities.
- Writes reports only under Forge memory.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import sqlite3
import stat
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

FORGE_ROOT = Path("/home/nic/forge")
IDENTITY_ROOT = Path("/home/nic/identity-vault")
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"
OUT_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch226a1_profile_inventory_scan_v1"
PATCH_NAME = "patch226a1_identity_vault_profile_inventory_scan_hotfix"

EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    "coverage",
    "dist",
    "build",
    "backups",
    "logs",
    ".cache",
}
EXCLUDE_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".lock", ".pem", ".key"}
PROFILE_NAME_HINTS = re.compile(
    r"(profile|identity|agent|user|gilligan|athena|neo|nic|template|vault)",
    re.IGNORECASE,
)
TEXT_SUFFIXES = {".json", ".md", ".txt", ".js", ".ts", ".yaml", ".yml"}
MAX_PREVIEW_CHARS = 500
MAX_ROWS = 10


def utc_ts() -> str:
    return _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_UTC")


def sha256_file(path: Path, max_bytes: Optional[int] = None) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        if max_bytes is None:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        else:
            h.update(f.read(max_bytes))
    return h.hexdigest()


def stat_metadata(path: Path, include_hash: bool = False) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False, "path": str(path)}
    st = path.stat()
    data: Dict[str, Any] = {
        "exists": True,
        "path": str(path),
        "size": st.st_size,
        "mode": oct(stat.S_IMODE(st.st_mode)),
        "mtime_ns": st.st_mtime_ns,
    }
    if include_hash and path.is_file():
        data["sha256"] = sha256_file(path)
    return data


def open_ro_sqlite(path: Path) -> sqlite3.Connection:
    uri = f"file:{path}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def safe_json_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (int, float, bool)):
        return value
    s = str(value)
    if len(s) > MAX_PREVIEW_CHARS:
        return s[:MAX_PREVIEW_CHARS] + f"...<truncated {len(s) - MAX_PREVIEW_CHARS} chars>"
    return s


def sqlite_table_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [r[1] for r in rows]


def sqlite_table_count(conn: sqlite3.Connection, table: str) -> int:
    row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    return int(row[0]) if row else 0


def sqlite_preview_rows(conn: sqlite3.Connection, table: str, preferred_cols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    cols = sqlite_table_columns(conn, table)
    if not cols:
        return []
    if preferred_cols:
        selected = [c for c in preferred_cols if c in cols]
        if not selected:
            selected = cols[:12]
    else:
        selected = cols[:12]
    quoted = ", ".join([f'"{c}"' for c in selected])
    rows = conn.execute(f"SELECT {quoted} FROM {table} LIMIT {MAX_ROWS}").fetchall()
    out = []
    for row in rows:
        out.append({col: safe_json_value(val) for col, val in zip(selected, row)})
    return out


def inspect_db(path: Path, label: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "label": label,
        "path": str(path),
        "exists": path.exists(),
        "opened_readonly": False,
        "ok": False,
        "error": None,
        "tables": [],
        "schemas": {},
        "row_counts": {},
        "previews": {},
    }
    if not path.exists():
        return result
    try:
        with open_ro_sqlite(path) as conn:
            result["opened_readonly"] = True
            tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
            result["tables"] = tables
            for table in tables:
                if table.startswith("sqlite_"):
                    continue
                cols = sqlite_table_columns(conn, table)
                result["schemas"][table] = cols
                try:
                    result["row_counts"][table] = sqlite_table_count(conn, table)
                except Exception as e:
                    result["row_counts"][table] = f"ERROR: {e}"
                lower_table = table.lower()
                if any(k in lower_table for k in ["profile", "session", "agent", "user"]):
                    preferred = [
                        "id",
                        "agent_id",
                        "user_id",
                        "profile_id",
                        "canonical_name",
                        "role",
                        "version",
                        "is_active",
                        "activation_state",
                        "rmc_namespace",
                        "created_at",
                        "updated_at",
                        "operational_profile_json",
                    ]
                    result["previews"][table] = sqlite_preview_rows(conn, table, preferred)
            result["ok"] = True
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
        result["traceback_tail"] = traceback.format_exc().splitlines()[-6:]
    return result


def classify_candidate(path: Path) -> str:
    name = path.name.lower()
    if "gilligan" in name:
        return "agent_candidate_gilligan"
    if "athena" in name:
        return "agent_candidate_athena"
    if "neo" in name:
        return "agent_candidate_neo"
    if "agent" in name:
        return "agent_profile_or_template_candidate"
    if "user" in name or "nic" in name:
        return "user_profile_or_template_candidate"
    if "profile" in name or "identity" in name:
        return "profile_or_identity_candidate"
    if "template" in name:
        return "template_candidate"
    return "general_vault_candidate"


def read_json_keys(path: Path) -> Dict[str, Any]:
    try:
        if path.suffix.lower() != ".json":
            return {"json_attempted": False}
        if path.stat().st_size > 2_000_000:
            return {"json_attempted": False, "reason": "too_large"}
        with path.open("r", encoding="utf-8", errors="replace") as f:
            obj = json.load(f)
        if isinstance(obj, dict):
            return {"json_attempted": True, "json_ok": True, "top_level_keys": sorted(list(obj.keys()))[:80]}
        if isinstance(obj, list):
            return {"json_attempted": True, "json_ok": True, "list_length": len(obj)}
        return {"json_attempted": True, "json_ok": True, "type": type(obj).__name__}
    except Exception as e:
        return {"json_attempted": True, "json_ok": False, "error": f"{type(e).__name__}: {e}"}


def scan_profile_candidate_files() -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    if not IDENTITY_ROOT.exists():
        return candidates
    for root, dirs, files in os.walk(IDENTITY_ROOT):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in files:
            p = root_path / fname
            rel = p.relative_to(IDENTITY_ROOT)
            if p.name in {".env"}:
                continue
            if p.suffix.lower() in EXCLUDE_SUFFIXES:
                continue
            if p.suffix.lower() not in TEXT_SUFFIXES:
                continue
            rel_s = str(rel)
            if not PROFILE_NAME_HINTS.search(rel_s):
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            item: Dict[str, Any] = {
                "path": str(p),
                "relative_path": rel_s,
                "size": st.st_size,
                "sha256_16": sha256_file(p, max_bytes=1024 * 1024)[:16] if p.is_file() else None,
                "classification": classify_candidate(p),
            }
            item.update(read_json_keys(p))
            candidates.append(item)
    candidates.sort(key=lambda x: (x["classification"], x["relative_path"]))
    return candidates[:200]


def md_code(obj: Any) -> str:
    return "```json\n" + json.dumps(obj, indent=2, sort_keys=True) + "\n```"


def render_report(report: Dict[str, Any]) -> str:
    canonical = report["databases"]["canonical"]
    legacy = report["databases"]["legacy"]
    candidates = report["profile_candidate_files"]
    lines: List[str] = []
    lines.append("# Identity Vault Patch 226A.1 Profile Inventory Scan")
    lines.append("")
    lines.append(f"Timestamp: `{report['timestamp']}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This hotfix replaces the failed Patch 226A scanner that missed `import stat`.")
    lines.append("- This scan is read-only except for writing reports under Forge memory.")
    lines.append("- It reads canonical and legacy SQLite databases through read-only connections.")
    lines.append("- It does not read `.env` secret values.")
    lines.append("- It does not write databases, create profiles, or activate identities.")
    lines.append("")
    lines.append("## Roots")
    lines.append(f"- Identity Vault root: `{IDENTITY_ROOT}` exists=`{IDENTITY_ROOT.exists()}`")
    lines.append(f"- Canonical DB: `{CANONICAL_DB}` exists=`{CANONICAL_DB.exists()}`")
    lines.append(f"- Legacy DB: `{LEGACY_DB}` exists=`{LEGACY_DB.exists()}`")
    lines.append("")
    lines.append("## Canonical Database Inventory")
    lines.append(f"- opened_readonly: `{canonical['opened_readonly']}` ok=`{canonical['ok']}`")
    lines.append(f"- tables: `{', '.join(canonical.get('tables', []))}`")
    if canonical.get("row_counts"):
        for t, c in canonical["row_counts"].items():
            lines.append(f"  - `{t}` rows: `{c}`")
    lines.append("")
    lines.append("### Canonical Profile Previews")
    if canonical.get("previews"):
        for table, rows in canonical["previews"].items():
            lines.append(f"- `{table}` preview rows returned: `{len(rows)}`")
            if rows:
                lines.append(md_code(rows))
    else:
        lines.append("- No profile/session preview rows available.")
    lines.append("")
    lines.append("## Legacy Database Inventory")
    lines.append(f"- opened_readonly: `{legacy['opened_readonly']}` ok=`{legacy['ok']}`")
    lines.append(f"- tables: `{', '.join(legacy.get('tables', []))}`")
    if legacy.get("row_counts"):
        for t, c in legacy["row_counts"].items():
            lines.append(f"  - `{t}` rows: `{c}`")
    lines.append("")
    lines.append("### Legacy Profile / Session Previews")
    if legacy.get("previews"):
        for table, rows in legacy["previews"].items():
            lines.append(f"- `{table}` preview rows returned: `{len(rows)}`")
            if rows:
                lines.append(md_code(rows))
    else:
        lines.append("- No legacy profile/session preview rows available.")
    lines.append("")
    lines.append("## Profile Candidate Files")
    lines.append(f"- candidate files found: `{len(candidates)}`")
    if candidates:
        by_class: Dict[str, int] = {}
        for c in candidates:
            by_class[c["classification"]] = by_class.get(c["classification"], 0) + 1
        for k, v in sorted(by_class.items()):
            lines.append(f"  - `{k}`: `{v}`")
        lines.append("")
        lines.append("### Candidate File List")
        for c in candidates[:60]:
            extra = ""
            if c.get("json_ok") and c.get("top_level_keys"):
                extra = f" keys=`{', '.join(c['top_level_keys'][:12])}`"
            lines.append(f"- `{c['relative_path']}` class=`{c['classification']}` size=`{c['size']}` sha16=`{c['sha256_16']}`{extra}")
    else:
        lines.append("- No local profile/template candidate files found outside excluded folders.")
    lines.append("")
    lines.append("## Safety Checks")
    for k, v in report["safety"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Findings")
    for f in report["findings"]:
        lines.append(f"- **{f['level']}** `{f['code']}` — {f['message']}")
    lines.append("")
    lines.append("## Recommended Next Safe Step")
    lines.append(report["next_safe_step"])
    lines.append("")
    return "\n".join(lines)


def write_latest(path: Path, latest: Path) -> None:
    latest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    ts = utc_ts()
    run_dir = OUT_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    before_env = stat_metadata(IDENTITY_ROOT / ".env", include_hash=False)
    before_canonical = stat_metadata(CANONICAL_DB, include_hash=True)
    before_legacy = stat_metadata(LEGACY_DB, include_hash=True)

    canonical = inspect_db(CANONICAL_DB, "canonical")
    legacy = inspect_db(LEGACY_DB, "legacy")
    candidates = scan_profile_candidate_files()

    after_env = stat_metadata(IDENTITY_ROOT / ".env", include_hash=False)
    after_canonical = stat_metadata(CANONICAL_DB, include_hash=True)
    after_legacy = stat_metadata(LEGACY_DB, include_hash=True)

    legacy_profile_rows = 0
    for t, c in legacy.get("row_counts", {}).items():
        if any(k in t.lower() for k in ["profile", "session"]):
            if isinstance(c, int):
                legacy_profile_rows += c

    canonical_profile_rows = 0
    for t in ["agent_profiles", "user_profiles"]:
        c = canonical.get("row_counts", {}).get(t, 0)
        if isinstance(c, int):
            canonical_profile_rows += c

    safety = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before_env == after_env,
        "canonical_db_sha_unchanged": before_canonical.get("sha256") == after_canonical.get("sha256"),
        "legacy_db_sha_unchanged": before_legacy.get("sha256") == after_legacy.get("sha256"),
        "database_write_performed": False,
        "agent_identity_activation_performed": False,
        "profiles_created": False,
    }

    findings: List[Dict[str, str]] = []
    if not canonical.get("ok"):
        findings.append({"level": "FAIL", "code": "IV_CANONICAL_DB_READONLY_FAILED", "message": str(canonical.get("error"))})
    else:
        findings.append({"level": "INFO", "code": "IV_CANONICAL_DB_READONLY_OK", "message": "Canonical Identity Vault database opened in read-only mode."})

    if legacy.get("ok") and legacy_profile_rows:
        findings.append({"level": "WARN", "code": "IV_LEGACY_PROFILE_ROWS_FOUND", "message": f"Legacy database contains {legacy_profile_rows} profile/session rows that may need migration review."})
    elif legacy.get("ok"):
        findings.append({"level": "INFO", "code": "IV_LEGACY_DB_READONLY_OK", "message": "Legacy database opened read-only; no profile/session rows detected."})
    elif legacy.get("exists"):
        findings.append({"level": "WARN", "code": "IV_LEGACY_DB_READONLY_FAILED", "message": str(legacy.get("error"))})

    if canonical_profile_rows:
        findings.append({"level": "WARN", "code": "IV_CANONICAL_PROFILE_ROWS_FOUND", "message": f"Canonical DB already contains {canonical_profile_rows} user/agent profile rows."})
    else:
        findings.append({"level": "INFO", "code": "IV_CANONICAL_PROFILE_ROWS_EMPTY", "message": "Canonical user_profiles and agent_profiles are currently empty."})

    if candidates:
        findings.append({"level": "WARN", "code": "IV_PROFILE_CANDIDATE_FILES_FOUND", "message": f"Found {len(candidates)} local profile/template candidate files for review."})
    else:
        findings.append({"level": "INFO", "code": "IV_NO_PROFILE_CANDIDATE_FILES_FOUND", "message": "No local profile/template candidate files found outside excluded folders."})

    if not all(safety.values()):
        findings.append({"level": "FAIL", "code": "IV_INVENTORY_SAFETY_CHECK_FAILED", "message": "A no-mutation safety check failed."})

    verdict = "PASS"
    if any(f["level"] == "FAIL" for f in findings):
        verdict = "FAIL"
    elif any(f["level"] == "WARN" for f in findings):
        verdict = "WARN"

    next_safe_step = (
        "Review the legacy DB previews and candidate files. If useful prior profiles exist, create a migration-preview patch "
        "that maps them into the new operational_profile_json structure without activation. If no useful profiles exist, "
        "create inactive draft Gilligan/Athena/Neo and Nic user profiles from the Identity Vault blueprint."
    )

    report: Dict[str, Any] = {
        "timestamp": ts,
        "patch": PATCH_NAME,
        "verdict": verdict,
        "databases": {"canonical": canonical, "legacy": legacy},
        "profile_candidate_files": candidates,
        "safety": safety,
        "findings": findings,
        "next_safe_step": next_safe_step,
    }

    json_path = run_dir / f"{ts}_identity_vault_patch226a1_profile_inventory_scan.json"
    md_path = run_dir / f"{ts}_identity_vault_patch226a1_profile_inventory_scan.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_report(report), encoding="utf-8")

    latest_json = OUT_ROOT / "latest_identity_vault_patch226a1_profile_inventory_scan.json"
    latest_md = OUT_ROOT / "latest_identity_vault_patch226a1_profile_inventory_scan.md"
    write_latest(json_path, latest_json)
    write_latest(md_path, latest_md)

    print("Identity Vault Patch 226A.1 profile inventory scan complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {verdict}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
