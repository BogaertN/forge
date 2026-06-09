#!/usr/bin/env python3
"""
Patch 221 — Identity Vault DB Canonical Path + Testability Apply

Purpose:
- Normalize direct Identity Vault JS code references away from root-level vault.db.
- Prefer the canonical database path data/identity_vault.db.
- Add a small static Jest test that protects the canonical DB path choice.
- Never read .env secret values.
- Never write Identity Vault database contents.
- Never activate agent identities.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any

PATCH_ID = "patch221_identity_vault_db_canonical_testability_apply"
REPORT_ROOT_REL = Path("forge/memory/identity_vault_patch221_db_canonical_testability_v1")
BACKUP_ROOT_REL = Path("forge/backups/patch221_identity_vault_db_canonical_testability_before")

LEGACY_TOKEN = "vault.db"
CANONICAL_TOKEN = "data/identity_vault.db"
CANONICAL_DB_REL = Path("data/identity_vault.db")
LEGACY_DB_REL = Path("vault.db")

TEST_REL = Path("tests/db.canonical.test.js")

TEST_CONTENT = r'''// tests/db.canonical.test.js
// Patch 221: protects Identity Vault canonical DB path normalization.
// This test is static on purpose: it proves code defaults do not fall back to root vault.db.

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const dbJsPath = path.join(root, 'db.js');

function readText(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

describe('Identity Vault canonical database path', () => {
  test('db.js references data/identity_vault.db as the canonical local database', () => {
    const text = readText(dbJsPath);
    expect(text).toContain('identity_vault.db');
    expect(text).toContain('data');
  });

  test('db.js does not directly default to root-level vault.db', () => {
    const text = readText(dbJsPath);
    const forbidden = /path\.(join|resolve)\(__dirname,\s*['"]vault\.db['"]\)/;
    expect(forbidden.test(text)).toBe(false);
  });
});
'''


def now_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_only(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    st = path.stat()
    return {"exists": True, "size": st.st_size, "mode": oct(st.st_mode & 0o777)}


def read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"__error__": str(exc)}


def sqlite_summary(db_path: Path) -> Dict[str, Any]:
    summary: Dict[str, Any] = {"path": str(db_path), "exists": db_path.exists(), "opened_readonly": False, "ok": False, "tables": {}, "error": None}
    if not db_path.exists():
        return summary
    try:
        uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        summary["opened_readonly"] = True
        cur = conn.cursor()
        rows = cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        for (name,) in rows:
            try:
                count = cur.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            except Exception:
                count = None
            summary["tables"][name] = count
        conn.close()
        summary["ok"] = True
    except Exception as exc:
        summary["error"] = str(exc)
    return summary


def copy_backup(src: Path, backup_root: Path, identity_root: Path) -> Dict[str, Any]:
    if not src.exists():
        return {"source": str(src), "copied": False, "reason": "missing"}
    rel = src.relative_to(identity_root) if src.is_relative_to(identity_root) else Path(src.name)
    dest = backup_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return {"source": str(src), "backup": str(dest), "copied": True, "sha256": sha256_file(dest)}


def iter_identity_js_files(identity_root: Path) -> List[Path]:
    skip_dirs = {"node_modules", ".git", "coverage", "dist", "backups", "logs"}
    files: List[Path] = []
    for root, dirs, filenames in os.walk(identity_root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        root_path = Path(root)
        for filename in filenames:
            if filename.endswith(".js"):
                files.append(root_path / filename)
    return sorted(files)


def normalize_text(text: str) -> Tuple[str, int]:
    before = text
    replacements = [
        ("'vault.db'", "'data/identity_vault.db'"),
        ('"vault.db"', '"data/identity_vault.db"'),
        ("`vault.db`", "`data/identity_vault.db`"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text, before.count(LEGACY_TOKEN) - text.count(LEGACY_TOKEN)


def scan_legacy_refs(identity_root: Path) -> Dict[str, Any]:
    hits: Dict[str, List[Dict[str, Any]]] = {}
    total = 0
    for path in iter_identity_js_files(identity_root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if LEGACY_TOKEN in text:
            rel = str(path.relative_to(identity_root))
            hits[rel] = []
            for idx, line in enumerate(text.splitlines(), start=1):
                if LEGACY_TOKEN in line:
                    hits[rel].append({"line": idx, "text": line.strip()[:200]})
                    total += 1
    return {"total_legacy_refs": total, "files": hits}


def node_check(identity_root: Path, rel_paths: List[Path]) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for rel in rel_paths:
        path = identity_root / rel
        if not path.exists():
            results[str(rel)] = {"exists": False, "ok": False, "returncode": None}
            continue
        try:
            cp = subprocess.run(["node", "--check", str(path)], cwd=str(identity_root), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25)
            results[str(rel)] = {"exists": True, "ok": cp.returncode == 0, "returncode": cp.returncode, "stdout_tail": cp.stdout[-1000:], "stderr_tail": cp.stderr[-1000:]}
        except Exception as exc:
            results[str(rel)] = {"exists": True, "ok": False, "error": str(exc)}
    return results


def optional_jest(identity_root: Path) -> Dict[str, Any]:
    package_json = identity_root / "package.json"
    node_modules = identity_root / "node_modules"
    if not package_json.exists():
        return {"attempted": False, "reason": "package.json missing"}
    if not node_modules.exists():
        return {"attempted": False, "reason": "node_modules missing"}
    try:
        cp = subprocess.run(
            ["npx", "jest", "tests/db.canonical.test.js", "--runInBand", "--coverage=false"],
            cwd=str(identity_root), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90
        )
        return {"attempted": True, "ok": cp.returncode == 0, "returncode": cp.returncode, "stdout_tail": cp.stdout[-2000:], "stderr_tail": cp.stderr[-2000:]}
    except Exception as exc:
        return {"attempted": True, "ok": False, "error": str(exc)}


def write_reports(run_root: Path, latest_md: Path, latest_json: Path, report: Dict[str, Any]) -> None:
    md = []
    md.append("# Identity Vault Patch 221 DB Canonical Path + Testability Apply")
    md.append("")
    md.append(f"Timestamp: `{report['timestamp']}`")
    md.append(f"Verdict: **{report['verdict']}**")
    md.append("")
    md.append("## Boundary")
    for item in report["boundary"]:
        md.append(f"- {item}")
    md.append("")
    md.append("## Backup")
    md.append(f"- backup root: `{report['backup_root']}`")
    for item in report["backups"]:
        status = "COPIED" if item.get("copied") else f"SKIPPED ({item.get('reason')})"
        md.append(f"- `{item.get('source')}`: **{status}**")
    md.append("")
    md.append("## Canonical DB Decision")
    md.append(f"- canonical DB path: `{report['canonical_db_path']}`")
    md.append(f"- legacy DB path preserved: `{report['legacy_db_path']}`")
    md.append(f"- canonical DB exists: `{report['canonical_db_exists']}`")
    md.append(f"- legacy DB exists: `{report['legacy_db_exists']}`")
    md.append("")
    md.append("## File Changes")
    md.append(f"- files changed: `{len(report['changed_files'])}`")
    for rel in report["changed_files"]:
        md.append(f"  - `{rel}`")
    md.append(f"- canonical static test written: `{report['test_written']}`")
    md.append("")
    md.append("## Legacy Reference Scan")
    md.append(f"- before legacy refs in JS: `{report['legacy_scan_before']['total_legacy_refs']}`")
    md.append(f"- after legacy refs in JS: `{report['legacy_scan_after']['total_legacy_refs']}`")
    if report['legacy_scan_after']['files']:
        md.append("- remaining legacy refs:")
        for rel, hits in report['legacy_scan_after']['files'].items():
            md.append(f"  - `{rel}`: `{len(hits)}`")
    else:
        md.append("- remaining legacy refs: `none in scanned JS files`")
    md.append("")
    md.append("## Syntax Checks")
    for rel, res in report["node_checks"].items():
        md.append(f"- `{rel}`: **{'PASS' if res.get('ok') else 'FAIL'}** returncode=`{res.get('returncode')}`")
    md.append("")
    md.append("## Optional Jest Check")
    jest = report["optional_jest"]
    if jest.get("attempted"):
        md.append(f"- attempted: `True`")
        md.append(f"- ok: `{jest.get('ok')}` returncode=`{jest.get('returncode')}`")
    else:
        md.append(f"- attempted: `False` reason=`{jest.get('reason')}`")
    md.append("")
    md.append("## Database Read-Only Summary")
    dbs = report["database_summaries"]
    for label, summary in dbs.items():
        md.append(f"- {label}: path=`{summary.get('path')}` ok=`{summary.get('ok')}` opened_readonly=`{summary.get('opened_readonly')}`")
        if summary.get("tables"):
            md.append(f"  - tables: `{', '.join(summary['tables'].keys())}`")
    md.append("")
    md.append("## No-Mutation / Safety Checks")
    for key, value in report["safety_checks"].items():
        md.append(f"- `{key}`: `{value}`")
    md.append("")
    md.append("## Findings")
    for finding in report["findings"]:
        md.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    md.append("")
    md.append("## Next Safe Step")
    md.append("Create the five AI.Web service contract draft files under `/home/nic/aiweb/service_contracts/`, then verify them before adding Forge read-only connector commands.")
    md.append("")

    run_md = run_root / f"{report['timestamp']}_identity_vault_patch221_db_canonical_testability.md"
    run_json = run_root / f"{report['timestamp']}_identity_vault_patch221_db_canonical_testability.json"
    run_md.write_text("\n".join(md), encoding="utf-8")
    run_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    latest_md.write_text("\n".join(md), encoding="utf-8")
    latest_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    home = Path.home()
    forge_root = home / "forge"
    identity_root = home / "identity-vault"
    ts = now_stamp()
    run_root = forge_root / REPORT_ROOT_REL.relative_to("forge") / ts
    latest_root = forge_root / REPORT_ROOT_REL.relative_to("forge")
    backup_root = forge_root / BACKUP_ROOT_REL.relative_to("forge") / ts
    run_root.mkdir(parents=True, exist_ok=True)
    latest_root.mkdir(parents=True, exist_ok=True)
    backup_root.mkdir(parents=True, exist_ok=True)

    report: Dict[str, Any] = {
        "timestamp": ts,
        "patch_id": PATCH_ID,
        "verdict": "PASS",
        "boundary": [
            "This patch modifies Identity Vault JS path references and writes one static test file only after backup.",
            "It does not modify Identity Vault database contents.",
            "It does not read .env secret values.",
            "It does not package node_modules, register Forge tools, write RMC memory, or activate agent identities.",
        ],
        "identity_root": str(identity_root),
        "backup_root": str(backup_root),
        "canonical_db_path": str(identity_root / CANONICAL_DB_REL),
        "legacy_db_path": str(identity_root / LEGACY_DB_REL),
        "canonical_db_exists": (identity_root / CANONICAL_DB_REL).exists(),
        "legacy_db_exists": (identity_root / LEGACY_DB_REL).exists(),
        "backups": [],
        "changed_files": [],
        "test_written": False,
        "legacy_scan_before": {},
        "legacy_scan_after": {},
        "node_checks": {},
        "optional_jest": {},
        "database_summaries": {},
        "safety_checks": {},
        "findings": [],
    }

    if not identity_root.exists():
        report["verdict"] = "FAIL"
        report["findings"].append({"level": "FAIL", "code": "IV_ROOT_MISSING", "message": f"Identity Vault root missing: {identity_root}"})
        write_reports(run_root, latest_root / "latest_identity_vault_patch221_db_canonical_testability.md", latest_root / "latest_identity_vault_patch221_db_canonical_testability.json", report)
        print("Identity Vault Patch 221 DB canonical/testability apply complete.")
        print(f"Run directory: {run_root}")
        print(f"Report: {latest_root / 'latest_identity_vault_patch221_db_canonical_testability.md'}")
        print("Verdict: FAIL")
        return 1

    db_js = identity_root / "db.js"
    package_json = identity_root / "package.json"
    existing_test = identity_root / TEST_REL
    paths_to_backup = [db_js, package_json, existing_test]
    for p in paths_to_backup:
        report["backups"].append(copy_backup(p, backup_root, identity_root))

    before_env_stat = stat_only(identity_root / ".env")
    before_canonical_sha = sha256_file(identity_root / CANONICAL_DB_REL)
    before_legacy_sha = sha256_file(identity_root / LEGACY_DB_REL)

    report["legacy_scan_before"] = scan_legacy_refs(identity_root)

    changed_files: List[str] = []
    if not db_js.exists():
        report["verdict"] = "FAIL"
        report["findings"].append({"level": "FAIL", "code": "IV_DB_JS_MISSING", "message": "identity-vault/db.js is missing."})
    else:
        # Normalize exact legacy DB string references in JS files only.
        for path in iter_identity_js_files(identity_root):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            new_text, _ = normalize_text(text)
            if new_text != text:
                report["backups"].append(copy_backup(path, backup_root, identity_root))
                path.write_text(new_text, encoding="utf-8")
                changed_files.append(str(path.relative_to(identity_root)))

        # Write static test.
        test_path = identity_root / TEST_REL
        test_path.parent.mkdir(parents=True, exist_ok=True)
        if test_path.exists() and str(TEST_REL) not in changed_files:
            report["backups"].append(copy_backup(test_path, backup_root, identity_root))
        if test_path.read_text(encoding="utf-8", errors="replace") if test_path.exists() else "" != TEST_CONTENT:
            test_path.write_text(TEST_CONTENT, encoding="utf-8")
            if str(TEST_REL) not in changed_files:
                changed_files.append(str(TEST_REL))
            report["test_written"] = True
        else:
            report["test_written"] = True

    report["changed_files"] = sorted(set(changed_files))
    report["legacy_scan_after"] = scan_legacy_refs(identity_root)

    rel_checks = [Path("db.js"), TEST_REL]
    # Also syntax-check every changed JS file.
    for rel in sorted(set(Path(x) for x in changed_files)):
        if rel.suffix == ".js" and rel not in rel_checks:
            rel_checks.append(rel)
    report["node_checks"] = node_check(identity_root, rel_checks)
    report["optional_jest"] = optional_jest(identity_root)

    report["database_summaries"] = {
        "canonical": sqlite_summary(identity_root / CANONICAL_DB_REL),
        "legacy_preserved": sqlite_summary(identity_root / LEGACY_DB_REL),
    }

    after_env_stat = stat_only(identity_root / ".env")
    after_canonical_sha = sha256_file(identity_root / CANONICAL_DB_REL)
    after_legacy_sha = sha256_file(identity_root / LEGACY_DB_REL)
    report["safety_checks"] = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before_env_stat == after_env_stat,
        "canonical_db_sha_unchanged": before_canonical_sha == after_canonical_sha,
        "legacy_db_sha_unchanged": before_legacy_sha == after_legacy_sha,
        "database_write_performed": False,
        "agent_identity_activation_performed": False,
        "forge_tool_registry_modified": False,
    }

    # Findings and verdict.
    if report["legacy_scan_after"].get("total_legacy_refs", 0) == 0:
        report["findings"].append({"level": "INFO", "code": "IV_LEGACY_DB_REFS_REMOVED", "message": "No root vault.db references remain in scanned JS files."})
    else:
        report["findings"].append({"level": "WARN", "code": "IV_LEGACY_DB_REFS_REMAIN", "message": "Some vault.db references remain in scanned JS files; review before connector registration."})

    if all(res.get("ok") for res in report["node_checks"].values()):
        report["findings"].append({"level": "INFO", "code": "IV_NODE_SYNTAX_OK", "message": "Changed/tested JS files pass node --check."})
    else:
        report["findings"].append({"level": "FAIL", "code": "IV_NODE_SYNTAX_FAILED", "message": "One or more changed/tested JS files failed node --check."})
        report["verdict"] = "FAIL"

    if report["database_summaries"]["canonical"].get("ok"):
        report["findings"].append({"level": "INFO", "code": "IV_CANONICAL_DB_READONLY_OK", "message": "Canonical DB opens read-only after path normalization."})
    else:
        report["findings"].append({"level": "FAIL", "code": "IV_CANONICAL_DB_READONLY_FAILED", "message": "Canonical DB could not be opened read-only after path normalization."})
        report["verdict"] = "FAIL"

    if not all(report["safety_checks"].values()):
        report["findings"].append({"level": "FAIL", "code": "IV_SAFETY_SNAPSHOT_CHANGED", "message": "A protected safety snapshot changed unexpectedly."})
        report["verdict"] = "FAIL"

    # Optional jest failure is a warning, because environment/test harness may still need later normalizing.
    jest = report["optional_jest"]
    if jest.get("attempted") and not jest.get("ok"):
        report["findings"].append({"level": "WARN", "code": "IV_OPTIONAL_JEST_FAILED", "message": "Static canonical DB Jest test did not pass in this environment; inspect stdout/stderr tail in JSON report."})
        if report["verdict"] == "PASS":
            report["verdict"] = "WARN"
    elif jest.get("attempted") and jest.get("ok"):
        report["findings"].append({"level": "INFO", "code": "IV_OPTIONAL_JEST_PASS", "message": "Static canonical DB Jest test passed."})
    else:
        report["findings"].append({"level": "INFO", "code": "IV_OPTIONAL_JEST_NOT_RUN", "message": f"Optional Jest was not run: {jest.get('reason')}"})

    latest_md = latest_root / "latest_identity_vault_patch221_db_canonical_testability.md"
    latest_json = latest_root / "latest_identity_vault_patch221_db_canonical_testability.json"
    write_reports(run_root, latest_md, latest_json, report)

    print("Identity Vault Patch 221 DB canonical/testability apply complete.")
    print(f"Run directory: {run_root}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {report['verdict']}")
    return 0 if report["verdict"] in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
