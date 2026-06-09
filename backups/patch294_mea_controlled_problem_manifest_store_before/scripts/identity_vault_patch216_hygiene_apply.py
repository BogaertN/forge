#!/usr/bin/env python3
"""
Patch 216 — Identity Vault Hygiene Apply

Purpose:
- Backup Identity Vault metadata and databases before hygiene changes.
- Add local runtime / packaging exclusions to .gitignore and .dockerignore.
- Write a DRAFT read-only Identity Vault service contract file.
- Produce a report under Forge memory.

This patch does NOT:
- Activate agent identities.
- Modify Identity Vault databases.
- Print .env contents or secret values.
- Modify Forge tool registry or RMC memory.
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

FORGE_ROOT = Path.home() / "forge"
IDENTITY_ROOT = Path.home() / "identity-vault"
MEMORY_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch216_hygiene_apply_v1"
BACKUP_ROOT = FORGE_ROOT / "backups" / "patch216_identity_vault_hygiene_before"
CONTRACT_DIR = IDENTITY_ROOT / "service_contracts"
CONTRACT_PATH = CONTRACT_DIR / "identity_vault_readonly_service_contract.draft.json"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"

GITIGNORE_MARKER_BEGIN = "# BEGIN FORGE PATCH216 IDENTITY VAULT LOCAL RUNTIME EXCLUSIONS"
GITIGNORE_MARKER_END = "# END FORGE PATCH216 IDENTITY VAULT LOCAL RUNTIME EXCLUSIONS"
DOCKERIGNORE_MARKER_BEGIN = "# BEGIN FORGE PATCH216 IDENTITY VAULT DOCKER/PACKAGING EXCLUSIONS"
DOCKERIGNORE_MARKER_END = "# END FORGE PATCH216 IDENTITY VAULT DOCKER/PACKAGING EXCLUSIONS"

IGNORE_RULES = [
    ".env",
    ".env.*",
    "!.env.example",
    "node_modules/",
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "data/*.db",
    "data/*.sqlite",
    "data/*.sqlite3",
    "backups/",
    "logs/",
    "coverage/",
    "dist/",
]


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_meta(path: Path, root: Path = Path.home()) -> Dict[str, Any]:
    rel = str(path.relative_to(root)) if path.exists() and str(path).startswith(str(root)) else str(path)
    if not path.exists():
        return {"path": rel, "exists": False}
    st = path.stat()
    return {
        "path": rel,
        "exists": True,
        "size": st.st_size,
        "mode": oct(st.st_mode & 0o777),
        "sha256": sha256_file(path),
    }


def readonly_sqlite_summary(db_path: Path) -> Dict[str, Any]:
    summary: Dict[str, Any] = {"path": str(db_path), "exists": db_path.exists(), "ok": False, "tables": [], "row_counts": {}}
    if not db_path.exists():
        return summary
    try:
        uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        summary["tables"] = tables
        for table in tables:
            # table names are sourced from sqlite_master; quote defensively.
            safe_table = table.replace('"', '""')
            cur.execute(f'SELECT COUNT(*) FROM "{safe_table}"')
            summary["row_counts"][table] = int(cur.fetchone()[0])
        conn.close()
        summary["ok"] = True
    except Exception as exc:  # pragma: no cover - operational reporting
        summary["error"] = repr(exc)
    return summary


def copy_if_exists(src: Path, dst_root: Path, label: str) -> Dict[str, Any]:
    entry = {"label": label, "source": str(src), "exists": src.exists(), "copied": False}
    if not src.exists():
        return entry
    dst = dst_root / label
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)
    entry.update({"copied": True, "backup_path": str(dst), "sha256": sha256_file(dst) if dst.is_file() else None})
    return entry


def replace_or_append_managed_block(path: Path, begin: str, end: str, rules: List[str]) -> Dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    block = "\n".join([begin, *rules, end]) + "\n"
    had_begin = begin in old
    had_end = end in old
    changed = False

    if had_begin and had_end:
        start = old.index(begin)
        stop = old.index(end, start) + len(end)
        new = old[:start] + block.rstrip("\n") + old[stop:]
        if not new.endswith("\n"):
            new += "\n"
        changed = new != old
    else:
        sep = "" if old.endswith("\n") or old == "" else "\n"
        new = old + sep + "\n" + block if old.strip() else block
        changed = True

    if changed:
        path.write_text(new, encoding="utf-8")

    return {
        "path": str(path),
        "exists_after": path.exists(),
        "had_begin_before": had_begin,
        "had_end_before": had_end,
        "changed": changed,
        "begin_after": begin in path.read_text(encoding="utf-8"),
        "end_after": end in path.read_text(encoding="utf-8"),
        "rules_after": {rule: (rule in path.read_text(encoding="utf-8")) for rule in rules},
    }


def build_contract(timestamp: str) -> Dict[str, Any]:
    return {
        "contract_name": "identity_vault_readonly_service_contract_draft",
        "version": "0.1.1-draft-file",
        "status": "DRAFT_NOT_ACTIVE",
        "created_by_patch": "patch216_identity_vault_hygiene_apply",
        "created_at_utc": timestamp,
        "service": "Identity Vault",
        "root": str(IDENTITY_ROOT),
        "controlled_by": "Forge",
        "canonical_database_path": str(CANONICAL_DB),
        "service_role": "Agent identity, permissions, profile metadata, and memory namespace pointers. It is not an agent runtime and not the shared memory store.",
        "allowed_reads": [
            "package.json metadata",
            "README and documentation metadata",
            "SQLite schema and row counts using read-only connections",
            "agent profile metadata after explicit adapter approval",
            "identity-to-RMC namespace pointers after explicit adapter approval",
        ],
        "allowed_writes": [],
        "forbidden_reads": [
            ".env secret values",
            "raw tokens, private keys, JWT secrets, API keys, passwords",
            "full private memory payloads unless routed through approved RMC boundary",
        ],
        "forbidden_writes": [
            "Identity Vault databases",
            ".env",
            "node_modules",
            "agent identity state",
            "RMC memory",
            "Forge tool registry",
        ],
        "future_adapter_rules": [
            "Forge may ask Identity Vault who an agent is.",
            "Forge may ask what permissions an agent has.",
            "Forge may ask which RMC namespace belongs to an agent.",
            "Forge may not execute agents inside Identity Vault.",
            "Forge may not let Identity Vault directly call tools or write memory.",
        ],
        "audit_requirement": "Every future Identity Vault read must be logged by Forge with timestamp, requested identity, purpose, and result metadata; never log secret values.",
        "activation_rule": "This contract is a draft file only. It becomes active only after a later Forge adapter patch explicitly loads and verifies it.",
    }


def write_report(report: Dict[str, Any], run_dir: Path) -> Tuple[Path, Path, Path]:
    ts = report["timestamp"]
    json_path = run_dir / f"{ts}_identity_vault_patch216_hygiene_apply.json"
    md_path = run_dir / f"{ts}_identity_vault_patch216_hygiene_apply.md"
    latest_json = MEMORY_ROOT / "latest_identity_vault_patch216_hygiene_apply.json"
    latest_md = MEMORY_ROOT / "latest_identity_vault_patch216_hygiene_apply.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    latest_json.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Identity Vault Patch 216 Hygiene Apply Report")
    lines.append("")
    lines.append(f"Timestamp: `{ts}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    for item in report["boundary"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Backup")
    lines.append(f"- backup root: `{report['backup_root']}`")
    for entry in report["backups"]:
        status = "COPIED" if entry.get("copied") else "MISSING/SKIPPED"
        lines.append(f"- `{entry['label']}`: **{status}**")
    lines.append("")
    lines.append("## Database Read-Only Summary")
    for db in report["database_summary"]:
        lines.append(f"- `{db['path']}` ok=`{db.get('ok')}` exists=`{db.get('exists')}`")
        if db.get("tables"):
            lines.append(f"  - tables: `{', '.join(db['tables'])}`")
            for table, count in db.get("row_counts", {}).items():
                lines.append(f"  - `{table}` rows: `{count}`")
    lines.append("")
    lines.append("## Ignore Hygiene")
    lines.append(f"- `.gitignore` changed: `{report['gitignore_update'].get('changed')}`")
    lines.append(f"- `.dockerignore` changed: `{report['dockerignore_update'].get('changed')}`")
    lines.append(f"- managed `.gitignore` block present: `{report['gitignore_update'].get('begin_after') and report['gitignore_update'].get('end_after')}`")
    lines.append(f"- managed `.dockerignore` block present: `{report['dockerignore_update'].get('begin_after') and report['dockerignore_update'].get('end_after')}`")
    lines.append("")
    lines.append("## Service Contract Draft")
    lines.append(f"- path: `{report['contract_path']}`")
    lines.append(f"- exists: `{report['contract_exists']}`")
    lines.append(f"- status: `{report['contract_status']}`")
    lines.append(f"- active: `False` — draft only")
    lines.append("")
    lines.append("## Sensitive / Runtime Files")
    for meta in report["sensitive_runtime_metadata"]:
        lines.append(f"- `{meta['path']}` exists=`{meta.get('exists')}` size=`{meta.get('size')}` mode=`{meta.get('mode')}` sha256=`{meta.get('sha256')}`")
    lines.append("")
    lines.append("## Findings")
    for finding in report["findings"]:
        lines.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    lines.append("")
    lines.append("## Next Safe Step")
    lines.append("Create a read-only Identity Vault adapter scan that imports the draft contract and proves Forge can read identity metadata boundaries without reading secrets, writing databases, or activating agent identities.")
    lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    latest_md.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
    return md_path, json_path, latest_md


def main() -> int:
    ts = utc_stamp()
    run_dir = MEMORY_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    backup_dir = BACKUP_ROOT / ts
    backup_dir.mkdir(parents=True, exist_ok=True)

    report: Dict[str, Any] = {
        "timestamp": ts,
        "verdict": "PASS",
        "identity_root": str(IDENTITY_ROOT),
        "backup_root": str(backup_dir),
        "boundary": [
            "This patch performs approved hygiene only.",
            "It backs up Identity Vault metadata and both SQLite database files before changes.",
            "It updates ignore/packaging exclusion rules only.",
            "It writes a DRAFT read-only service contract file only.",
            "It does not modify Identity Vault database contents.",
            "It does not print or copy .env secret values into reports.",
            "It does not modify Forge registry, RMC memory, AI.Web wrappers, or agent identity activation state.",
        ],
        "backups": [],
        "database_summary": [],
        "sensitive_runtime_metadata": [],
        "findings": [],
    }

    if not IDENTITY_ROOT.exists():
        report["verdict"] = "FAIL"
        report["findings"].append({"level": "ERROR", "code": "IV_ROOT_MISSING", "message": f"Identity Vault root missing: {IDENTITY_ROOT}"})
        write_report(report, run_dir)
        print("Identity Vault Patch 216 hygiene apply complete.")
        print(f"Run directory: {run_dir}")
        print(f"Report: {MEMORY_ROOT / 'latest_identity_vault_patch216_hygiene_apply.md'}")
        print("Verdict: FAIL")
        return 1

    # Backup metadata files and database files. Do NOT copy .env.
    backup_targets = [
        (IDENTITY_ROOT / "package.json", "metadata/package.json"),
        (IDENTITY_ROOT / "package-lock.json", "metadata/package-lock.json"),
        (IDENTITY_ROOT / ".gitignore", "metadata/.gitignore"),
        (IDENTITY_ROOT / ".dockerignore", "metadata/.dockerignore"),
        (CANONICAL_DB, "databases/data_identity_vault.db"),
        (LEGACY_DB, "databases/vault.db"),
    ]
    for src, label in backup_targets:
        report["backups"].append(copy_if_exists(src, backup_dir, label))

    # Metadata only for sensitive/runtime files. Do not print or copy .env contents.
    for path in [IDENTITY_ROOT / ".env", IDENTITY_ROOT / ".env.example", CANONICAL_DB, LEGACY_DB]:
        report["sensitive_runtime_metadata"].append(file_meta(path))

    # Read-only database schema summaries before/after hygiene (databases are not modified).
    for db in [CANONICAL_DB, LEGACY_DB]:
        report["database_summary"].append(readonly_sqlite_summary(db))

    # Update ignore files with managed blocks.
    report["gitignore_update"] = replace_or_append_managed_block(
        IDENTITY_ROOT / ".gitignore", GITIGNORE_MARKER_BEGIN, GITIGNORE_MARKER_END, IGNORE_RULES
    )
    report["dockerignore_update"] = replace_or_append_managed_block(
        IDENTITY_ROOT / ".dockerignore", DOCKERIGNORE_MARKER_BEGIN, DOCKERIGNORE_MARKER_END, IGNORE_RULES
    )

    # Write draft contract. Draft only, not active.
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    contract = build_contract(ts)
    CONTRACT_PATH.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report["contract_path"] = str(CONTRACT_PATH)
    report["contract_exists"] = CONTRACT_PATH.exists()
    report["contract_status"] = contract["status"]
    report["contract_sha256"] = sha256_file(CONTRACT_PATH)

    # Findings.
    if (IDENTITY_ROOT / "node_modules").exists():
        report["findings"].append({"level": "INFO", "code": "IV_NODE_MODULES_PRESENT_BUT_IGNORED", "message": "node_modules is still present locally, but ignore rules now explicitly exclude it from packaging."})
    if (IDENTITY_ROOT / ".env").exists():
        report["findings"].append({"level": "WARN", "code": "IV_ENV_PRESENT_LOCAL_ONLY", "message": ".env still exists locally. This patch does not remove it. Ensure it is never packaged; rotate secrets if previously shared outside the machine."})
    if CANONICAL_DB.exists() and LEGACY_DB.exists():
        report["findings"].append({"level": "INFO", "code": "IV_MULTIPLE_DBS_PRESERVED", "message": "Both databases were preserved and backed up. Canonical path remains data/identity_vault.db; legacy vault.db remains migration candidate."})

    # Verify core postconditions.
    post_ok = True
    for update_key in ["gitignore_update", "dockerignore_update"]:
        update = report[update_key]
        if not (update.get("begin_after") and update.get("end_after") and all(update.get("rules_after", {}).values())):
            post_ok = False
            report["findings"].append({"level": "ERROR", "code": f"{update_key.upper()}_POSTCHECK_FAILED", "message": "Managed ignore block or expected rules missing after patch."})
    if not CONTRACT_PATH.exists():
        post_ok = False
        report["findings"].append({"level": "ERROR", "code": "IV_CONTRACT_DRAFT_MISSING", "message": "Draft service contract was not written."})
    if not post_ok:
        report["verdict"] = "FAIL"

    md_path, json_path, latest_md = write_report(report, run_dir)
    print("Identity Vault Patch 216 hygiene apply complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {MEMORY_ROOT / 'latest_identity_vault_patch216_hygiene_apply.json'}")
    print(f"Contract draft: {CONTRACT_PATH}")
    print(f"Verdict: {report['verdict']}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
