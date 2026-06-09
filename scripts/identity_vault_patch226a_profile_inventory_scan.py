#!/usr/bin/env python3
# identity_vault_patch226a_profile_inventory_scan.py
# Patch 226A — read-only inventory scan for existing Identity Vault user/agent profiles.
# Purpose: discover whether Nic already has user/agent profiles in canonical DB, legacy DB,
# or local profile/template files before creating any new draft profiles.

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

PATCH_ID = "patch226a_identity_vault_profile_inventory_scan"
REPORT_ROOT = Path("/home/nic/forge/memory/identity_vault_patch226a_profile_inventory_scan_v1")
IDENTITY_ROOT = Path("/home/nic/identity-vault")
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"

EXCLUDED_DIRS = {
    "node_modules", ".git", "data", "logs", "backups", "coverage", "dist", ".cache",
}
EXCLUDED_FILES = {
    ".env", ".env.local", ".env.production", ".env.development",
}
PROFILE_KEYWORDS = [
    "agent_id", "user_id", "operational_profile_json", "canonical_name",
    "spirit_name", "interaction_preferences", "meta_rules", "symbolic_signature",
    "capabilities", "limitations", "forbidden_actions", "session_state",
    "gilligan", "athena", "neo", "nic_bogaert", "manitou", "benishi",
]
SENSITIVE_KEY_PAT = re.compile(r"(secret|token|password|passwd|private[_-]?key|api[_-]?key|jwt|salt|hash)", re.I)


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def sha256_file(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def stat_metadata(path: Path) -> Dict[str, Any]:
    try:
        st = path.stat()
        return {
            "exists": True,
            "size": st.st_size,
            "mode": oct(stat.S_IMODE(st.st_mode)),
            "sha256": sha256_file(path),
        }
    except FileNotFoundError:
        return {"exists": False}


def redact_value(key: str, value: Any) -> Any:
    if SENSITIVE_KEY_PAT.search(str(key)):
        return "<REDACTED>"
    if isinstance(value, dict):
        return {k: redact_value(k, v) for k, v in list(value.items())[:40]}
    if isinstance(value, list):
        return [redact_value(key, v) for v in value[:20]]
    if isinstance(value, str):
        if len(value) > 500:
            return value[:500] + "...<TRUNCATED>"
        return value
    return value


def safe_row_preview(row: sqlite3.Row) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k in row.keys():
        v = row[k]
        if SENSITIVE_KEY_PAT.search(k):
            out[k] = "<REDACTED>"
        elif k == "operational_profile_json":
            try:
                parsed = json.loads(v or "{}")
                out[k] = {
                    "json_ok": True,
                    "keys": list(parsed.keys())[:50] if isinstance(parsed, dict) else [],
                    "agent_id": parsed.get("agent_id") if isinstance(parsed, dict) else None,
                    "user_id": parsed.get("user_id") if isinstance(parsed, dict) else None,
                    "canonical_name": parsed.get("canonical_name") if isinstance(parsed, dict) else None,
                    "profile_type_hint": "agent" if isinstance(parsed, dict) and "agent_id" in parsed else ("user" if isinstance(parsed, dict) and "user_id" in parsed else "unknown"),
                }
            except Exception as e:
                out[k] = {"json_ok": False, "error": type(e).__name__, "length": len(str(v or ""))}
        elif isinstance(v, str) and len(v) > 300:
            out[k] = v[:300] + "...<TRUNCATED>"
        else:
            out[k] = v
    return out


def sqlite_inventory(db_path: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "path": str(db_path),
        "exists": db_path.exists(),
        "opened_readonly": False,
        "ok": False,
        "tables": {},
        "profile_like_rows_total": 0,
    }
    if not db_path.exists():
        return result
    uri = f"file:{db_path}?mode=ro"
    try:
        con = sqlite3.connect(uri, uri=True)
        con.row_factory = sqlite3.Row
        result["opened_readonly"] = True
        table_rows = con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        for tr in table_rows:
            t = tr["name"]
            columns = [r["name"] for r in con.execute(f"PRAGMA table_info({t})").fetchall()]
            count = con.execute(f"SELECT COUNT(*) AS c FROM {t}").fetchone()["c"]
            preview: List[Dict[str, Any]] = []
            if t in {"agent_profiles", "user_profiles", "profiles", "session_state"} and count:
                rows = con.execute(f"SELECT * FROM {t} LIMIT 20").fetchall()
                preview = [safe_row_preview(r) for r in rows]
                result["profile_like_rows_total"] += count
            result["tables"][t] = {
                "columns": columns,
                "row_count": count,
                "preview_rows": preview,
            }
        con.close()
        result["ok"] = True
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    return result


def looks_like_profile_text(text: str) -> Tuple[bool, List[str]]:
    lowered = text.lower()
    hits = []
    for kw in PROFILE_KEYWORDS:
        if kw.lower() in lowered:
            hits.append(kw)
    return bool(hits), hits[:20]


def scan_profile_files(root: Path) -> Dict[str, Any]:
    result = {
        "root": str(root),
        "exists": root.exists(),
        "files_scanned": 0,
        "candidate_files": [],
        "skipped_large_files": 0,
    }
    if not root.exists():
        return result
    candidates = []
    allowed_suffixes = {".json", ".md", ".txt", ".js"}
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(root)
        parts = set(rel.parts)
        if parts & EXCLUDED_DIRS:
            continue
        if path.name in EXCLUDED_FILES or path.name.startswith(".env"):
            continue
        if path.suffix.lower() not in allowed_suffixes:
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > 2_000_000:
            result["skipped_large_files"] += 1
            continue
        result["files_scanned"] += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        matched, hits = looks_like_profile_text(text)
        if not matched:
            continue
        entry: Dict[str, Any] = {
            "path": str(path),
            "relative_path": str(rel),
            "size": size,
            "sha256": sha256_file(path),
            "keyword_hits": hits,
            "json_ok": False,
            "profile_type_hint": "unknown",
            "top_level_keys": [],
            "safe_preview": {},
        }
        if path.suffix.lower() == ".json":
            try:
                parsed = json.loads(text)
                entry["json_ok"] = True
                if isinstance(parsed, dict):
                    entry["top_level_keys"] = list(parsed.keys())[:50]
                    if "agent_id" in parsed:
                        entry["profile_type_hint"] = "agent"
                    elif "user_id" in parsed:
                        entry["profile_type_hint"] = "user"
                    entry["safe_preview"] = {
                        k: redact_value(k, parsed.get(k))
                        for k in ["agent_id", "user_id", "canonical_name", "spirit_name", "role", "version", "last_updated", "session_state"]
                        if k in parsed
                    }
            except Exception as e:
                entry["json_error"] = type(e).__name__
        else:
            # Short text preview around first hit.
            low = text.lower()
            idxs = [low.find(h.lower()) for h in hits if low.find(h.lower()) >= 0]
            idx = min(idxs) if idxs else 0
            start = max(0, idx - 160)
            end = min(len(text), idx + 360)
            entry["text_preview"] = text[start:end].replace("\n", " ")[:520]
        candidates.append(entry)
    result["candidate_files"] = candidates[:80]
    result["candidate_count"] = len(candidates)
    return result


def write_reports(report: Dict[str, Any], run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_dir / f"{report['timestamp']}_identity_vault_patch226a_profile_inventory_scan.json"
    md_path = run_dir / f"{report['timestamp']}_identity_vault_patch226a_profile_inventory_scan.md"
    latest_json = REPORT_ROOT / "latest_identity_vault_patch226a_profile_inventory_scan.json"
    latest_md = REPORT_ROOT / "latest_identity_vault_patch226a_profile_inventory_scan.md"

    json_text = json.dumps(report, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")

    md = []
    md.append("# Identity Vault Patch 226A Profile Inventory Scan")
    md.append("")
    md.append(f"Timestamp: `{report['timestamp']}`")
    md.append(f"Verdict: **{report['verdict']}**")
    md.append("")
    md.append("## Boundary")
    for b in report["boundary"]:
        md.append(f"- {b}")
    md.append("")
    md.append("## Database Inventory")
    for label in ["canonical_db", "legacy_db"]:
        inv = report[label]
        md.append(f"### {label}")
        md.append(f"- path: `{inv['path']}`")
        md.append(f"- exists: `{inv['exists']}` opened_readonly=`{inv.get('opened_readonly')}` ok=`{inv.get('ok')}`")
        md.append(f"- profile-like rows total: `{inv.get('profile_like_rows_total', 0)}`")
        for t, meta in inv.get("tables", {}).items():
            md.append(f"  - `{t}` rows=`{meta['row_count']}` columns=`{', '.join(meta['columns'])}`")
            previews = meta.get("preview_rows") or []
            if previews:
                md.append("    - safe preview rows:")
                for row in previews[:5]:
                    md.append(f"      - `{json.dumps(row, sort_keys=True)[:900]}`")
    md.append("")
    md.append("## Local Profile/Template File Candidates")
    fs = report["file_scan"]
    md.append(f"- files scanned: `{fs.get('files_scanned')}`")
    md.append(f"- candidate count: `{fs.get('candidate_count', 0)}`")
    for c in fs.get("candidate_files", [])[:25]:
        md.append(f"- `{c['relative_path']}` type_hint=`{c.get('profile_type_hint')}` hits=`{', '.join(c.get('keyword_hits', []))}` sha256=`{c.get('sha256')}`")
        if c.get("safe_preview"):
            md.append(f"  - safe_preview: `{json.dumps(c['safe_preview'], sort_keys=True)[:600]}`")
        elif c.get("text_preview"):
            md.append(f"  - text_preview: `{c['text_preview'][:500]}`")
    md.append("")
    md.append("## Findings")
    for f in report["findings"]:
        md.append(f"- **{f['level']}** `{f['code']}` — {f['message']}")
    md.append("")
    md.append("## Next Safe Step")
    md.append(report["next_safe_step"])
    md_text = "\n".join(md) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")

    report["paths"] = {
        "run_dir": str(run_dir),
        "report": str(md_path),
        "json": str(json_path),
        "latest_report": str(latest_md),
        "latest_json": str(latest_json),
    }


def main() -> int:
    ts = utc_stamp()
    run_dir = REPORT_ROOT / ts
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)

    before_env = stat_metadata(IDENTITY_ROOT / ".env")
    before_canonical = stat_metadata(CANONICAL_DB)
    before_legacy = stat_metadata(LEGACY_DB)

    canonical = sqlite_inventory(CANONICAL_DB)
    legacy = sqlite_inventory(LEGACY_DB)
    file_scan = scan_profile_files(IDENTITY_ROOT)

    after_env = stat_metadata(IDENTITY_ROOT / ".env")
    after_canonical = stat_metadata(CANONICAL_DB)
    after_legacy = stat_metadata(LEGACY_DB)

    canonical_rows = canonical.get("profile_like_rows_total", 0)
    legacy_rows = legacy.get("profile_like_rows_total", 0)
    candidate_count = file_scan.get("candidate_count", 0)

    findings = []
    if canonical_rows:
        findings.append({"level": "INFO", "code": "IV_CANONICAL_PROFILE_ROWS_FOUND", "message": f"Canonical database contains {canonical_rows} profile-like rows."})
    else:
        findings.append({"level": "INFO", "code": "IV_CANONICAL_PROFILE_ROWS_EMPTY", "message": "Canonical database has no profile-like rows yet."})
    if legacy_rows:
        findings.append({"level": "WARN", "code": "IV_LEGACY_PROFILE_ROWS_FOUND", "message": f"Legacy vault.db contains {legacy_rows} profile-like rows; review before creating replacement profiles."})
    if candidate_count:
        findings.append({"level": "INFO", "code": "IV_PROFILE_FILE_CANDIDATES_FOUND", "message": f"Found {candidate_count} local files that may contain user/agent profile structures or templates."})
    if before_env != after_env:
        findings.append({"level": "FAIL", "code": "IV_ENV_METADATA_CHANGED", "message": ".env metadata changed during read-only scan."})
    if before_canonical != after_canonical:
        findings.append({"level": "FAIL", "code": "IV_CANONICAL_DB_CHANGED", "message": "Canonical DB metadata/hash changed during read-only scan."})
    if before_legacy != after_legacy:
        findings.append({"level": "FAIL", "code": "IV_LEGACY_DB_CHANGED", "message": "Legacy DB metadata/hash changed during read-only scan."})

    fatal = any(f["level"] == "FAIL" for f in findings)
    verdict = "FAIL" if fatal else ("WARN" if legacy_rows else "PASS")
    if fatal:
        next_step = "Stop and inspect the changed safety snapshot before any profile migration or draft profile creation."
    elif legacy_rows or candidate_count:
        next_step = "Review this inventory. If existing profiles are valid, create a migration-preview patch that imports them as inactive draft operational_profile_json payloads; otherwise create fresh inactive draft profiles from the blueprint."
    else:
        next_step = "No existing profile rows/files were found. Next create inactive draft Gilligan/Athena/Neo profiles from the Identity Vault blueprint."

    report: Dict[str, Any] = {
        "timestamp": ts,
        "patch_id": PATCH_ID,
        "verdict": verdict,
        "boundary": [
            "This scan is read-only except for writing reports under Forge memory.",
            "It inventories canonical Identity Vault DB, legacy vault.db, and local profile/template candidate files.",
            "It does not read .env secret values.",
            "It does not modify Identity Vault databases, code, service contracts, Forge registry, RMC memory, or agent identity activation state.",
            "It redacts secret-like fields in previews.",
        ],
        "identity_root": str(IDENTITY_ROOT),
        "canonical_db": canonical,
        "legacy_db": legacy,
        "file_scan": file_scan,
        "safety_snapshots": {
            "env_unchanged": before_env == after_env,
            "canonical_db_unchanged": before_canonical == after_canonical,
            "legacy_db_unchanged": before_legacy == after_legacy,
            "env_secret_values_read": False,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
        },
        "findings": findings,
        "next_safe_step": next_step,
    }

    write_reports(report, run_dir)
    print("Identity Vault Patch 226A profile inventory scan complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {REPORT_ROOT / 'latest_identity_vault_patch226a_profile_inventory_scan.md'}")
    print(f"JSON report: {REPORT_ROOT / 'latest_identity_vault_patch226a_profile_inventory_scan.json'}")
    print(f"Verdict: {verdict}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
