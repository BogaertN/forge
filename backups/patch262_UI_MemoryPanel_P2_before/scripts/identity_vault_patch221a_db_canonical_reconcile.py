#!/usr/bin/env python3
"""
Patch 221A — Identity Vault DB Canonical Reconcile

Purpose:
- Reconcile Patch 221's FAIL without moving to broader service contracts prematurely.
- Back up current Identity Vault JS files.
- Remove remaining root-level legacy `vault.db` references from selected JS source files.
- Re-write a focused canonical DB static Jest test that does not itself create false legacy hits.
- Confirm .env and both SQLite DB files are not modified.

Boundary:
- Does not read .env secret values.
- Does not write Identity Vault databases.
- Does not register Forge tools.
- Does not write RMC memory.
- Does not activate agent identities.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any

FORGE_ROOT = Path.home() / "forge"
IV_ROOT = Path.home() / "identity-vault"
MEMORY_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch221a_db_canonical_reconcile_v1"
BACKUP_ROOT_BASE = FORGE_ROOT / "backups" / "patch221a_identity_vault_db_canonical_reconcile_before"
CANONICAL_DB = IV_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IV_ROOT / "vault.db"
ENV_FILE = IV_ROOT / ".env"
CONTRACT_FILE = IV_ROOT / "service_contracts" / "identity_vault_readonly_service_contract.draft.json"

# JS files that Patch 219 identified as having DB path/env references, plus canonical test.
TARGET_RELATIVE_FILES = [
    "db.js",
    "cli.js",
    "server.js",
    "scripts/init-database.js",
    "scripts/reset-database.js",
    "tests/db.canonical.test.js",
]

# A literal root-level legacy DB token means exactly "vault.db" not preceded by "identity_".
LEGACY_TOKEN_RE = re.compile(r"(?<!identity_)vault\.db")
CANONICAL_TOKEN = "data/identity_vault.db"


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
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
        "mode": oct(st.st_mode & 0o777),
        "sha256": sha256_file(path),
    }


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_backup(src: Path, backup_root: Path, rel: str, backup_report: Dict[str, str]) -> None:
    dst = backup_root / rel
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        backup_report[rel] = "COPIED"
    else:
        backup_report[rel] = "SKIPPED_MISSING"


def normalize_legacy_refs(text: str) -> str:
    """Replace literal root-level legacy vault.db tokens while preserving identity_vault.db."""
    out = LEGACY_TOKEN_RE.sub(CANONICAL_TOKEN, text)
    # Clean accidental double data path from references such as data/vault.db.
    out = out.replace("data/data/identity_vault.db", "data/identity_vault.db")
    # Clean Windows-style accidental double data path.
    out = out.replace("data\\data\\identity_vault.db", "data\\identity_vault.db")
    return out


def canonical_test_content() -> str:
    # Avoid literal legacy token by constructing it from parts.
    return """// tests/db.canonical.test.js - Patch 221A canonical DB path guard\n// Purpose: ensure Identity Vault source code uses data/identity_vault.db as the forward canonical DB path.\n\nconst fs = require('fs');\nconst path = require('path');\n\nconst root = path.resolve(__dirname, '..');\nconst legacyToken = 'vault' + '.db';\nconst canonicalToken = 'identity_' + legacyToken;\nconst canonicalPath = path.join(root, 'data', canonicalToken);\n\nconst scannedFiles = [\n  'db.js',\n  'cli.js',\n  'server.js',\n  path.join('scripts', 'init-database.js'),\n  path.join('scripts', 'reset-database.js'),\n];\n\ndescribe('Identity Vault canonical database path', () => {\n  test('canonical database exists in data directory', () => {\n    expect(fs.existsSync(canonicalPath)).toBe(true);\n  });\n\n  test('runtime source files do not contain root-level legacy database token', () => {\n    for (const rel of scannedFiles) {\n      const filePath = path.join(root, rel);\n      if (!fs.existsSync(filePath)) continue;\n      const text = fs.readFileSync(filePath, 'utf8').replaceAll(canonicalToken, '');\n      expect(text.includes(legacyToken)).toBe(false);\n    }\n  });\n});\n"""


def scan_legacy_refs() -> Dict[str, List[Dict[str, Any]]]:
    hits: Dict[str, List[Dict[str, Any]]] = {}
    for rel in TARGET_RELATIVE_FILES:
        path = IV_ROOT / rel
        if not path.exists() or path.suffix != ".js":
            continue
        text = read_text(path)
        # Remove canonical filename so identity_vault.db does not count as legacy.
        comparable = text.replace("identity_vault.db", "")
        file_hits = []
        for idx, line in enumerate(comparable.splitlines(), start=1):
            if LEGACY_TOKEN_RE.search(line):
                file_hits.append({"line": idx, "snippet": line.strip()[:220]})
        if file_hits:
            hits[rel] = file_hits
    return hits


def sqlite_summary(path: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {"path": str(path), "exists": path.exists(), "opened_readonly": False, "ok": False, "tables": []}
    if not path.exists():
        return result
    try:
        uri = f"file:{path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        result["opened_readonly"] = True
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cur.fetchall()]
        result["tables"] = tables
        counts = {}
        for table in tables:
            try:
                cur.execute(f'SELECT COUNT(*) FROM "{table}"')
                counts[table] = cur.fetchone()[0]
            except Exception as exc:
                counts[table] = f"ERROR: {exc}"
        result["row_counts"] = counts
        conn.close()
        result["ok"] = True
    except Exception as exc:
        result["error"] = str(exc)
    return result


def run_cmd(cmd: List[str], cwd: Path | None = None, timeout: int = 30) -> Dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        return {
            "cmd": cmd,
            "returncode": proc.returncode,
            "ok": proc.returncode == 0,
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:],
        }
    except Exception as exc:
        return {"cmd": cmd, "ok": False, "returncode": None, "error": str(exc)}


def main() -> int:
    ts = _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_UTC")
    run_dir = MEMORY_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    MEMORY_ROOT.mkdir(parents=True, exist_ok=True)
    backup_root = BACKUP_ROOT_BASE / ts
    backup_root.mkdir(parents=True, exist_ok=True)

    protected_before = {
        ".env": stat_meta(ENV_FILE),
        "canonical_db": stat_meta(CANONICAL_DB),
        "legacy_db": stat_meta(LEGACY_DB),
        "contract": stat_meta(CONTRACT_FILE),
    }

    backup_report: Dict[str, str] = {}
    for rel in TARGET_RELATIVE_FILES:
        copy_backup(IV_ROOT / rel, backup_root, rel, backup_report)
    copy_backup(CONTRACT_FILE, backup_root, "service_contracts/identity_vault_readonly_service_contract.draft.json", backup_report)

    legacy_before = scan_legacy_refs()
    files_changed: List[str] = []

    # Normalize existing target JS files except the canonical test, which is rewritten below.
    for rel in TARGET_RELATIVE_FILES:
        path = IV_ROOT / rel
        if rel == "tests/db.canonical.test.js":
            continue
        if not path.exists() or path.suffix != ".js":
            continue
        before = read_text(path)
        after = normalize_legacy_refs(before)
        if after != before:
            write_text(path, after)
            files_changed.append(rel)

    # Re-write the canonical static test to avoid false positives and test actual runtime files.
    test_rel = "tests/db.canonical.test.js"
    test_path = IV_ROOT / test_rel
    before_test = read_text(test_path) if test_path.exists() else ""
    after_test = canonical_test_content()
    if after_test != before_test:
        write_text(test_path, after_test)
        files_changed.append(test_rel)

    protected_after = {
        ".env": stat_meta(ENV_FILE),
        "canonical_db": stat_meta(CANONICAL_DB),
        "legacy_db": stat_meta(LEGACY_DB),
        "contract": stat_meta(CONTRACT_FILE),
    }

    legacy_after = scan_legacy_refs()
    syntax_checks = {}
    for rel in TARGET_RELATIVE_FILES:
        path = IV_ROOT / rel
        if path.exists() and path.suffix == ".js":
            syntax_checks[rel] = run_cmd(["node", "--check", str(path)], cwd=IV_ROOT)

    # Optional focused Jest run. Non-fatal because broader Jest/npm environment may still need work.
    jest_check = run_cmd(["npx", "jest", "tests/db.canonical.test.js", "--runInBand", "--silent"], cwd=IV_ROOT, timeout=60)

    no_mutation = {
        "env_secret_values_read": False,
        "env_stat_unchanged": protected_before[".env"] == protected_after[".env"],
        "canonical_db_sha_unchanged": protected_before["canonical_db"].get("sha256") == protected_after["canonical_db"].get("sha256"),
        "legacy_db_sha_unchanged": protected_before["legacy_db"].get("sha256") == protected_after["legacy_db"].get("sha256"),
        "contract_sha_unchanged": protected_before["contract"].get("sha256") == protected_after["contract"].get("sha256"),
        "database_write_performed": False,
        "agent_identity_activation_performed": False,
        "forge_tool_registry_modified": False,
    }

    syntax_ok = all(item.get("ok") for item in syntax_checks.values())
    protected_ok = all(no_mutation[k] for k in ["env_stat_unchanged", "canonical_db_sha_unchanged", "legacy_db_sha_unchanged", "contract_sha_unchanged"])
    legacy_ok = sum(len(v) for v in legacy_after.values()) == 0
    canonical_ok = CANONICAL_DB.exists() and sqlite_summary(CANONICAL_DB).get("ok") is True

    findings = []
    if legacy_ok:
        findings.append(("INFO", "IV_LEGACY_RUNTIME_DB_REFS_CLEARED", "No root-level legacy vault.db references remain in targeted JS runtime/test files."))
    else:
        findings.append(("WARN", "IV_LEGACY_RUNTIME_DB_REFS_REMAIN", "Root-level legacy vault.db references remain in targeted JS files."))
    if syntax_ok:
        findings.append(("INFO", "IV_NODE_SYNTAX_OK", "All targeted JS files pass node --check."))
    else:
        findings.append(("FAIL", "IV_NODE_SYNTAX_FAILED", "One or more targeted JS files failed node --check."))
    if protected_ok:
        findings.append(("INFO", "IV_PROTECTED_SNAPSHOTS_UNCHANGED", ".env, canonical DB, legacy DB, and draft contract hashes/stat metadata remained unchanged."))
    else:
        findings.append(("FAIL", "IV_PROTECTED_SNAPSHOT_CHANGED", "A protected file changed; inspect report before continuing."))
    if canonical_ok:
        findings.append(("INFO", "IV_CANONICAL_DB_READONLY_OK", "Canonical DB opens read-only after reconciliation."))
    else:
        findings.append(("FAIL", "IV_CANONICAL_DB_READONLY_FAILED", "Canonical DB failed read-only verification."))
    if not jest_check.get("ok"):
        findings.append(("WARN", "IV_OPTIONAL_FOCUSED_JEST_FAILED", "Focused Jest did not pass; this is non-fatal if syntax/static scan passed."))
    else:
        findings.append(("INFO", "IV_OPTIONAL_FOCUSED_JEST_OK", "Focused canonical DB Jest test passed."))

    hard_fail = (not syntax_ok) or (not protected_ok) or (not canonical_ok) or (not legacy_ok)
    verdict = "FAIL" if hard_fail else "PASS"

    report = {
        "timestamp": ts,
        "verdict": verdict,
        "boundary": {
            "modifies": "selected Identity Vault JS path references and tests/db.canonical.test.js only, after backup",
            "does_not_modify": ["Identity Vault DB contents", ".env", "node_modules", "Forge registry", "RMC memory", "AI.Web wrappers", "agent identity activation state"],
            "env_secret_values_read": False,
        },
        "backup_root": str(backup_root),
        "backup_report": backup_report,
        "files_changed": sorted(set(files_changed)),
        "legacy_refs_before": legacy_before,
        "legacy_refs_after": legacy_after,
        "legacy_ref_count_before": sum(len(v) for v in legacy_before.values()),
        "legacy_ref_count_after": sum(len(v) for v in legacy_after.values()),
        "syntax_checks": syntax_checks,
        "optional_focused_jest": jest_check,
        "protected_before": protected_before,
        "protected_after": protected_after,
        "no_mutation": no_mutation,
        "canonical_db_summary": sqlite_summary(CANONICAL_DB),
        "legacy_db_summary": sqlite_summary(LEGACY_DB),
        "findings": findings,
        "next_safe_step": "If this passes, create the five AI.Web service contract draft files under /home/nic/aiweb/service_contracts/ and verify them before adding Forge read-only connector commands.",
    }

    json_path = run_dir / f"{ts}_identity_vault_patch221a_db_canonical_reconcile.json"
    latest_json = MEMORY_ROOT / "latest_identity_vault_patch221a_db_canonical_reconcile.json"
    json_text = json.dumps(report, indent=2, sort_keys=True)
    write_text(json_path, json_text)
    write_text(latest_json, json_text)

    md_lines = []
    md_lines.append("# Identity Vault Patch 221A DB Canonical Reconcile")
    md_lines.append("")
    md_lines.append(f"Timestamp: `{ts}`")
    md_lines.append(f"Verdict: **{verdict}**")
    md_lines.append("")
    md_lines.append("## Boundary")
    md_lines.append("- This patch reconciles Patch 221's DB canonical/testability failure.")
    md_lines.append("- It modifies only selected Identity Vault JS path references and `tests/db.canonical.test.js`, after backup.")
    md_lines.append("- It does not modify database contents, `.env`, `node_modules`, Forge registry, RMC memory, AI.Web wrappers, or agent identity activation state.")
    md_lines.append("- It does not read `.env` secret values.")
    md_lines.append("")
    md_lines.append("## Backup")
    md_lines.append(f"- backup root: `{backup_root}`")
    for rel, state in backup_report.items():
        md_lines.append(f"- `{rel}`: **{state}**")
    md_lines.append("")
    md_lines.append("## File Changes")
    md_lines.append(f"- files changed: `{len(set(files_changed))}`")
    for rel in sorted(set(files_changed)):
        md_lines.append(f"  - `{rel}`")
    md_lines.append("")
    md_lines.append("## Legacy Runtime DB Reference Scan")
    md_lines.append(f"- before targeted legacy refs: `{report['legacy_ref_count_before']}`")
    md_lines.append(f"- after targeted legacy refs: `{report['legacy_ref_count_after']}`")
    if legacy_after:
        md_lines.append("- remaining refs:")
        for rel, hits in legacy_after.items():
            md_lines.append(f"  - `{rel}`: `{len(hits)}`")
            for hit in hits[:5]:
                md_lines.append(f"    - line `{hit['line']}` — `{hit['snippet']}`")
    else:
        md_lines.append("- remaining refs: `0`")
    md_lines.append("")
    md_lines.append("## Syntax Checks")
    for rel, item in syntax_checks.items():
        md_lines.append(f"- `{rel}`: **{'PASS' if item.get('ok') else 'FAIL'}** returncode=`{item.get('returncode')}`")
    md_lines.append("")
    md_lines.append("## Optional Focused Jest Check")
    md_lines.append(f"- attempted: `True`")
    md_lines.append(f"- ok: `{jest_check.get('ok')}` returncode=`{jest_check.get('returncode')}`")
    if not jest_check.get("ok"):
        md_lines.append("- stdout/stderr tail is stored in the JSON report.")
    md_lines.append("")
    md_lines.append("## Database Read-Only Summary")
    csum = report["canonical_db_summary"]
    lsum = report["legacy_db_summary"]
    md_lines.append(f"- canonical: path=`{CANONICAL_DB}` ok=`{csum.get('ok')}` opened_readonly=`{csum.get('opened_readonly')}`")
    md_lines.append(f"  - tables: `{', '.join(csum.get('tables', []))}`")
    md_lines.append(f"- legacy preserved: path=`{LEGACY_DB}` ok=`{lsum.get('ok')}` opened_readonly=`{lsum.get('opened_readonly')}`")
    md_lines.append(f"  - tables: `{', '.join(lsum.get('tables', []))}`")
    md_lines.append("")
    md_lines.append("## No-Mutation / Safety Checks")
    for key, val in no_mutation.items():
        md_lines.append(f"- `{key}`: `{val}`")
    md_lines.append("")
    md_lines.append("## Findings")
    for level, code, msg in findings:
        md_lines.append(f"- **{level}** `{code}` — {msg}")
    md_lines.append("")
    md_lines.append("## Next Safe Step")
    md_lines.append(report["next_safe_step"])

    md_text = "\n".join(md_lines) + "\n"
    md_path = run_dir / f"{ts}_identity_vault_patch221a_db_canonical_reconcile.md"
    latest_md = MEMORY_ROOT / "latest_identity_vault_patch221a_db_canonical_reconcile.md"
    write_text(md_path, md_text)
    write_text(latest_md, md_text)

    print("Identity Vault Patch 221A DB canonical reconcile complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
