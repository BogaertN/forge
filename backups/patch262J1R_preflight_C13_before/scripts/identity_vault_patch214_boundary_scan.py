#!/usr/bin/env python3
"""
Patch 214 — Identity Vault Boundary Scan
Read-only scanner for Identity Vault integration readiness.

This script does not modify Identity Vault, databases, Forge tools, Forge registry,
RMC memory, or agent identity configuration. It only writes a report under Forge memory.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

FORGE_ROOT = Path.home() / "forge"
IDENTITY_VAULT_ROOT = Path.home() / "identity-vault"
REPORT_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch214_boundary_scan_v1"
LATEST_MD = REPORT_ROOT / "latest_identity_vault_patch214_boundary_scan.md"
LATEST_JSON = REPORT_ROOT / "latest_identity_vault_patch214_boundary_scan.json"

SENSITIVE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".npmrc",
    "id_rsa",
    "id_ed25519",
}

DB_EXTENSIONS = {".db", ".sqlite", ".sqlite3"}
NODE_LOCK_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml"}


def now_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def sha256_file(path: Path, max_bytes: Optional[int] = None) -> Optional[str]:
    try:
        h = hashlib.sha256()
        with path.open("rb") as f:
            if max_bytes is None:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            else:
                remaining = max_bytes
                while remaining > 0:
                    chunk = f.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    h.update(chunk)
                    remaining -= len(chunk)
        return h.hexdigest()
    except Exception:
        return None


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(Path.home()))
    except Exception:
        return str(path)


def safe_file_meta(path: Path) -> Dict[str, Any]:
    meta: Dict[str, Any] = {
        "path": rel(path),
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
    }
    try:
        st = path.stat()
        meta.update({
            "size_bytes": st.st_size,
            "mtime": _dt.datetime.fromtimestamp(st.st_mtime, _dt.timezone.utc).isoformat(),
            "mode_octal": oct(st.st_mode & 0o777),
        })
        if path.is_file() and st.st_size <= 5_000_000:
            meta["sha256"] = sha256_file(path)
        elif path.is_file():
            meta["sha256_first_5mb"] = sha256_file(path, max_bytes=5_000_000)
    except Exception as exc:
        meta["stat_error"] = f"{type(exc).__name__}: {exc}"
    return meta


def read_json_safe(path: Path) -> Tuple[Optional[Any], Optional[str]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def scan_tree(root: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "root": rel(root),
        "root_exists": root.exists(),
        "top_level_entries": [],
        "important_files": {},
        "sensitive_hits": [],
        "database_hits": [],
        "node_modules_present": False,
        "runtime_dirs": [],
        "large_dirs_present": [],
        "package_json": None,
        "lock_files": [],
        "gitignore": None,
    }
    if not root.exists():
        return result

    try:
        result["top_level_entries"] = sorted(p.name for p in root.iterdir())
    except Exception as exc:
        result["top_level_error"] = f"{type(exc).__name__}: {exc}"

    for name in ["package.json", "server.js", "app.js", "index.js", "README.md", ".gitignore", ".env", ".env.example"]:
        p = root / name
        if p.exists():
            result["important_files"][name] = safe_file_meta(p)

    pkg = root / "package.json"
    if pkg.exists():
        data, err = read_json_safe(pkg)
        if err:
            result["package_json"] = {"parse_error": err}
        elif isinstance(data, dict):
            scripts = data.get("scripts") if isinstance(data.get("scripts"), dict) else {}
            deps = data.get("dependencies") if isinstance(data.get("dependencies"), dict) else {}
            dev_deps = data.get("devDependencies") if isinstance(data.get("devDependencies"), dict) else {}
            result["package_json"] = {
                "name": data.get("name"),
                "version": data.get("version"),
                "scripts": sorted(scripts.keys()),
                "dependency_names": sorted(deps.keys()),
                "dev_dependency_names": sorted(dev_deps.keys()),
            }
        else:
            result["package_json"] = {"parse_error": "package.json did not parse as object"}

    gitignore = root / ".gitignore"
    if gitignore.exists() and gitignore.is_file():
        try:
            content = gitignore.read_text(encoding="utf-8", errors="replace")
            result["gitignore"] = {
                "has_env_rule": any(line.strip() in {".env", ".env*"} for line in content.splitlines()),
                "has_node_modules_rule": any("node_modules" in line for line in content.splitlines()),
                "has_db_rule": any(token in content for token in ["*.db", "*.sqlite", "*.sqlite3", "data/"]),
            }
        except Exception as exc:
            result["gitignore"] = {"read_error": f"{type(exc).__name__}: {exc}"}

    for lock_name in NODE_LOCK_FILES:
        p = root / lock_name
        if p.exists():
            result["lock_files"].append(safe_file_meta(p))

    node_modules = root / "node_modules"
    result["node_modules_present"] = node_modules.exists()
    if node_modules.exists():
        result["large_dirs_present"].append(rel(node_modules))

    for name in ["data", "logs", "uploads", "tmp", "dist", "build", "coverage"]:
        p = root / name
        if p.exists() and p.is_dir():
            result["runtime_dirs"].append(rel(p))
            if name in {"dist", "build", "coverage"}:
                result["large_dirs_present"].append(rel(p))

    for p in root.rglob("*"):
        try:
            if any(part == "node_modules" for part in p.parts):
                continue
            name = p.name
            lower = name.lower()
            if name in SENSITIVE_NAMES or lower.startswith(".env"):
                result["sensitive_hits"].append(safe_file_meta(p))
            if p.is_file() and p.suffix.lower() in DB_EXTENSIONS:
                result["database_hits"].append(safe_file_meta(p))
        except Exception:
            continue

    result["sensitive_hits"].sort(key=lambda x: x.get("path", ""))
    result["database_hits"].sort(key=lambda x: x.get("path", ""))
    return result


def sqlite_schema_summary(db_path: Path) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "path": rel(db_path),
        "read_attempted": True,
        "ok": False,
        "tables": [],
        "views": [],
        "row_counts": {},
        "error": None,
    }
    # Read-only URI. mode=ro prevents creation or modification.
    uri = f"file:{db_path}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True, timeout=1)
        try:
            cur = conn.execute("SELECT type, name FROM sqlite_master WHERE type IN ('table','view') ORDER BY type, name")
            objects = cur.fetchall()
            summary["tables"] = [name for typ, name in objects if typ == "table"]
            summary["views"] = [name for typ, name in objects if typ == "view"]
            for table in summary["tables"]:
                if table.startswith("sqlite_"):
                    continue
                try:
                    count = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                    summary["row_counts"][table] = count
                except Exception as exc:
                    summary["row_counts"][table] = f"COUNT_ERROR:{type(exc).__name__}"
            summary["ok"] = True
        finally:
            conn.close()
    except Exception as exc:
        summary["error"] = f"{type(exc).__name__}: {exc}"
    return summary


def run_command(cmd: List[str], cwd: Optional[Path] = None) -> Dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        return {
            "cmd": cmd,
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-4000:],
            "stderr_tail": proc.stderr[-4000:],
        }
    except Exception as exc:
        return {"cmd": cmd, "error": f"{type(exc).__name__}: {exc}"}


def git_status(root: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {"is_git_repo": False, "status_checked": False}
    if not (root / ".git").exists():
        return result
    result["is_git_repo"] = True
    status = run_command(["git", "status", "--short"], cwd=root)
    result["status_checked"] = True
    result["status"] = status
    return result


def classify_findings(scan: Dict[str, Any], db_summaries: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    if not scan.get("root_exists"):
        findings.append({"severity": "BLOCKER", "code": "IV_ROOT_MISSING", "finding": "Identity Vault root was not found at ~/identity-vault."})
        return findings
    if scan.get("node_modules_present"):
        findings.append({"severity": "WARN", "code": "IV_NODE_MODULES_PRESENT", "finding": "node_modules is present and should not be packaged into future patches."})
    sens = scan.get("sensitive_hits", [])
    if any(Path(item.get("path", "")).name == ".env" for item in sens):
        findings.append({"severity": "WARN", "code": "IV_ENV_PRESENT", "finding": ".env is present. Do not package it; rotate secrets if it was shared outside the machine."})
    db_hits = scan.get("database_hits", [])
    if len(db_hits) > 1:
        findings.append({"severity": "WARN", "code": "IV_MULTIPLE_DATABASES", "finding": f"Multiple database files found ({len(db_hits)}). A canonical database path must be selected before integration."})
    elif len(db_hits) == 0:
        findings.append({"severity": "WARN", "code": "IV_NO_DATABASE_FOUND", "finding": "No SQLite database files found; confirm whether Identity Vault stores state elsewhere."})
    bad_db = [d for d in db_summaries if not d.get("ok")]
    if bad_db:
        findings.append({"severity": "WARN", "code": "IV_DB_SCHEMA_READ_ISSUE", "finding": f"{len(bad_db)} database file(s) could not be read as SQLite in read-only mode."})
    gitignore = scan.get("gitignore") or {}
    if isinstance(gitignore, dict):
        if not gitignore.get("has_env_rule"):
            findings.append({"severity": "WARN", "code": "IV_GITIGNORE_ENV_RULE_MISSING", "finding": ".gitignore does not clearly ignore .env files."})
        if not gitignore.get("has_node_modules_rule"):
            findings.append({"severity": "WARN", "code": "IV_GITIGNORE_NODE_MODULES_RULE_MISSING", "finding": ".gitignore does not clearly ignore node_modules."})
        if not gitignore.get("has_db_rule"):
            findings.append({"severity": "INFO", "code": "IV_GITIGNORE_DB_RULE_MISSING", "finding": ".gitignore does not clearly ignore local database/runtime state files."})
    if not findings:
        findings.append({"severity": "INFO", "code": "IV_NO_IMMEDIATE_BOUNDARY_WARNINGS", "finding": "No immediate boundary warning was detected by this read-only scan."})
    return findings


def render_md(report: Dict[str, Any]) -> str:
    scan = report["identity_vault_scan"]
    lines: List[str] = []
    lines.append("# Identity Vault Patch 214 Boundary Scan Report")
    lines.append("")
    lines.append(f"Timestamp: `{report['timestamp']}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This scan is read-only except for writing this report under Forge memory.")
    lines.append("- It does not modify Identity Vault, databases, Forge tools, Forge registry, RMC memory, AI.Web wrappers, or agent identity configuration.")
    lines.append("- It does not print `.env` contents or secret values; it records only metadata and hashes.")
    lines.append("")
    lines.append("## Root")
    lines.append(f"- root: `{scan.get('root')}`")
    lines.append(f"- exists: `{scan.get('root_exists')}`")
    lines.append(f"- node_modules present: `{scan.get('node_modules_present')}`")
    lines.append(f"- sensitive hits: `{len(scan.get('sensitive_hits', []))}`")
    lines.append(f"- database hits: `{len(scan.get('database_hits', []))}`")
    lines.append("")
    lines.append("## Top-Level Entries")
    if scan.get("top_level_entries"):
        for item in scan["top_level_entries"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none found or root missing")
    lines.append("")
    lines.append("## Package Summary")
    pkg = scan.get("package_json")
    if isinstance(pkg, dict):
        lines.append(f"- name: `{pkg.get('name')}`")
        lines.append(f"- version: `{pkg.get('version')}`")
        lines.append(f"- scripts: `{', '.join(pkg.get('scripts', [])) if pkg.get('scripts') else 'none'}`")
        lines.append(f"- dependencies: `{', '.join(pkg.get('dependency_names', [])) if pkg.get('dependency_names') else 'none'}`")
        lines.append(f"- dev dependencies: `{', '.join(pkg.get('dev_dependency_names', [])) if pkg.get('dev_dependency_names') else 'none'}`")
    else:
        lines.append("- package.json not found or not parsed")
    lines.append("")
    lines.append("## Sensitive / Runtime Files Detected")
    for item in scan.get("sensitive_hits", []):
        lines.append(f"- `{item.get('path')}` size=`{item.get('size_bytes')}` mode=`{item.get('mode_octal')}` sha256=`{item.get('sha256')}`")
    if not scan.get("sensitive_hits"):
        lines.append("- none")
    lines.append("")
    lines.append("## Database Files Detected")
    for item in scan.get("database_hits", []):
        lines.append(f"- `{item.get('path')}` size=`{item.get('size_bytes')}` mode=`{item.get('mode_octal')}` sha256=`{item.get('sha256') or item.get('sha256_first_5mb')}`")
    if not scan.get("database_hits"):
        lines.append("- none")
    lines.append("")
    lines.append("## SQLite Read-Only Schema Summary")
    for db in report.get("sqlite_schema_summaries", []):
        lines.append(f"- `{db.get('path')}` ok=`{db.get('ok')}`")
        if db.get("error"):
            lines.append(f"  - error: `{db.get('error')}`")
        lines.append(f"  - tables: `{', '.join(db.get('tables', [])) if db.get('tables') else 'none'}`")
        if db.get("row_counts"):
            for table, count in db["row_counts"].items():
                lines.append(f"  - `{table}` rows: `{count}`")
    if not report.get("sqlite_schema_summaries"):
        lines.append("- no database schema summaries")
    lines.append("")
    lines.append("## Git / Ignore Hygiene")
    gitignore = scan.get("gitignore")
    if isinstance(gitignore, dict):
        for key, value in gitignore.items():
            lines.append(f"- `{key}`: `{value}`")
    else:
        lines.append("- `.gitignore` not found or not parsed")
    git = report.get("git_status", {})
    lines.append(f"- git repo: `{git.get('is_git_repo')}`")
    if git.get("status_checked"):
        status = git.get("status", {})
        lines.append(f"- git status returncode: `{status.get('returncode')}`")
        if status.get("stdout_tail"):
            lines.append("```text")
            lines.append(status.get("stdout_tail", "").rstrip())
            lines.append("```")
    lines.append("")
    lines.append("## Findings")
    for finding in report.get("findings", []):
        lines.append(f"- **{finding.get('severity')}** `{finding.get('code')}` — {finding.get('finding')}")
    lines.append("")
    lines.append("## Next Safe Step")
    lines.append("If this report is understood, create the next patch as an Identity Vault hygiene plan, not an integration patch. The plan should choose the canonical database path, exclude node_modules and .env from future packaging, and prepare a read-only service contract. Do not activate agent identities yet.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ts = now_stamp()
    run_dir = REPORT_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    scan = scan_tree(IDENTITY_VAULT_ROOT)
    db_summaries: List[Dict[str, Any]] = []
    for item in scan.get("database_hits", []):
        p = Path.home() / item["path"] if not item["path"].startswith("/") else Path(item["path"])
        # item path is relative to home, e.g. identity-vault/data/foo.db
        if not p.exists():
            p = Path("/") / item["path"]
        if p.exists():
            db_summaries.append(sqlite_schema_summary(p))

    report: Dict[str, Any] = {
        "timestamp": ts,
        "verdict": "PASS" if scan.get("root_exists") else "WARN",
        "boundary": {
            "read_only": True,
            "writes_only_under": rel(REPORT_ROOT),
            "does_not_read_env_values": True,
            "does_not_modify_identity_vault": True,
            "does_not_modify_databases": True,
            "does_not_activate_agent_identities": True,
        },
        "identity_vault_scan": scan,
        "sqlite_schema_summaries": db_summaries,
        "git_status": git_status(IDENTITY_VAULT_ROOT),
    }
    report["findings"] = classify_findings(scan, db_summaries)

    json_text = json.dumps(report, indent=2, sort_keys=True)
    md_text = render_md(report)
    json_path = run_dir / f"{ts}_identity_vault_patch214_boundary_scan.json"
    md_path = run_dir / f"{ts}_identity_vault_patch214_boundary_scan.md"
    json_path.write_text(json_text + "\n", encoding="utf-8")
    md_path.write_text(md_text + "\n", encoding="utf-8")
    LATEST_JSON.write_text(json_text + "\n", encoding="utf-8")
    LATEST_MD.write_text(md_text + "\n", encoding="utf-8")

    print("Identity Vault Patch 214 boundary scan complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {LATEST_MD}")
    print(f"Verdict: {report['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
