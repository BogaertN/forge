#!/usr/bin/env python3
# identity_vault_patch217_adapter_readiness_scan.py
# Purpose: Read-only readiness scan for a future Forge -> Identity Vault adapter.
# Boundary: This script reads only approved metadata, draft contract fields, and SQLite schema/counts.
# It does not read .env secret values, write databases, activate identities, or register Forge tools.

from __future__ import annotations

import datetime as _dt
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple

PATCH_NAME = "patch217_identity_vault_adapter_readiness_scan"
MEMORY_DIR_NAME = "identity_vault_patch217_adapter_readiness_scan_v1"
CONTRACT_REL = "service_contracts/identity_vault_readonly_service_contract.draft.json"

EXPECTED_CONTRACT_NAME = "identity_vault_readonly_service_contract_draft"
EXPECTED_STATUS = "DRAFT_NOT_ACTIVE"
EXPECTED_VERSION_PREFIX = "0.1."

MANAGED_GITIGNORE_MARKER = "AI.WEB IDENTITY VAULT LOCAL RUNTIME EXCLUSIONS"
MANAGED_DOCKERIGNORE_MARKER = "AI.WEB IDENTITY VAULT LOCAL RUNTIME EXCLUSIONS"


def now_stamp() -> str:
    return _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_UTC")


def read_json(path: Path) -> Tuple[bool, Dict[str, Any] | None, str | None]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return True, json.load(f), None
    except Exception as exc:  # intentionally broad: report, do not crash early
        return False, None, f"{type(exc).__name__}: {exc}"


def file_stat_metadata(path: Path, label: str) -> Dict[str, Any]:
    # Important: this uses stat only. It does not open/read file contents.
    exists = path.exists()
    data: Dict[str, Any] = {
        "label": label,
        "path": str(path),
        "exists": exists,
        "content_read": False,
    }
    if exists:
        st = path.stat()
        data.update({
            "size": st.st_size,
            "mode": oct(st.st_mode & 0o777),
            "mtime_utc": _dt.datetime.fromtimestamp(st.st_mtime, _dt.UTC).isoformat(),
        })
    return data


def read_text_if_safe(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def sqlite_readonly_summary(db_path: Path) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "path": str(db_path),
        "exists": db_path.exists(),
        "ok": False,
        "opened_readonly": False,
        "tables": [],
        "table_columns": {},
        "row_counts": {},
        "error": None,
    }
    if not db_path.exists():
        summary["error"] = "database_missing"
        return summary

    try:
        uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        summary["opened_readonly"] = True
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cur.fetchall()]
            summary["tables"] = tables
            for table in tables:
                # table names come from sqlite_master; still quote defensively.
                quoted = '"' + table.replace('"', '""') + '"'
                cur.execute(f"PRAGMA table_info({quoted})")
                columns = [
                    {
                        "cid": row[0],
                        "name": row[1],
                        "type": row[2],
                        "notnull": row[3],
                        "default_present": row[4] is not None,
                        "pk": row[5],
                    }
                    for row in cur.fetchall()
                ]
                summary["table_columns"][table] = columns
                cur.execute(f"SELECT COUNT(*) FROM {quoted}")
                summary["row_counts"][table] = cur.fetchone()[0]
            summary["ok"] = True
        finally:
            conn.close()
    except Exception as exc:
        summary["error"] = f"{type(exc).__name__}: {exc}"
    return summary


def validate_contract(contract: Dict[str, Any] | None, contract_path: Path, identity_root: Path) -> Dict[str, Any]:
    checks: Dict[str, Any] = {
        "contract_exists": contract_path.exists(),
        "contract_loaded": contract is not None,
        "contract_name_ok": False,
        "status_ok": False,
        "version_ok": False,
        "controlled_by_forge": False,
        "allowed_writes_empty": False,
        "canonical_db_path_ok": False,
        "forbidden_reads_present": False,
        "forbidden_writes_present": False,
        "future_rules_present": False,
        "activation_rule_present": False,
        "overall_ok": False,
        "issues": [],
    }
    if contract is None:
        checks["issues"].append("contract_not_loaded")
        return checks

    checks["contract_name_ok"] = contract.get("contract_name") == EXPECTED_CONTRACT_NAME
    checks["status_ok"] = contract.get("status") == EXPECTED_STATUS
    checks["version_ok"] = str(contract.get("version", "")).startswith(EXPECTED_VERSION_PREFIX)
    checks["controlled_by_forge"] = contract.get("controlled_by") == "Forge"
    checks["allowed_writes_empty"] = contract.get("allowed_writes") == []
    canonical = contract.get("canonical_database_path")
    checks["canonical_db_path_ok"] = canonical == str(identity_root / "data" / "identity_vault.db")
    forbidden_reads = contract.get("forbidden_reads") or []
    forbidden_writes = contract.get("forbidden_writes") or []
    future_rules = contract.get("future_adapter_rules") or []
    checks["forbidden_reads_present"] = any(".env" in str(x) for x in forbidden_reads)
    checks["forbidden_writes_present"] = any("Identity Vault databases" in str(x) for x in forbidden_writes)
    checks["future_rules_present"] = len(future_rules) >= 5
    checks["activation_rule_present"] = bool(contract.get("activation_rule"))

    for key, value in checks.items():
        if key.endswith("_ok") or key in {
            "contract_exists",
            "contract_loaded",
            "controlled_by_forge",
            "allowed_writes_empty",
            "forbidden_reads_present",
            "forbidden_writes_present",
            "future_rules_present",
            "activation_rule_present",
        }:
            if value is not True:
                checks["issues"].append(key)
    checks["overall_ok"] = not checks["issues"]
    return checks


def list_allowed_identity_metadata(contract: Dict[str, Any] | None, package_json: Dict[str, Any] | None, db_summary: Dict[str, Any]) -> Dict[str, Any]:
    # This intentionally returns only boundary metadata, not agent row values.
    return {
        "service": (contract or {}).get("service", "Identity Vault"),
        "service_role": (contract or {}).get("service_role"),
        "canonical_database_path": (contract or {}).get("canonical_database_path"),
        "package": {
            "name": (package_json or {}).get("name"),
            "version": (package_json or {}).get("version"),
            "script_names": sorted(list(((package_json or {}).get("scripts") or {}).keys())),
        },
        "db_tables": db_summary.get("tables", []),
        "db_row_counts": db_summary.get("row_counts", {}),
        "identity_tables_present": {
            "agent_profiles": "agent_profiles" in db_summary.get("tables", []),
            "user_profiles": "user_profiles" in db_summary.get("tables", []),
        },
    }


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def write_markdown(path: Path, report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append("# Identity Vault Patch 217 Adapter Readiness Scan")
    lines.append("")
    lines.append(f"Timestamp: `{report['timestamp']}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    for item in report["boundary"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Roots")
    lines.append(f"- Forge root: `{report['forge_root']}`")
    lines.append(f"- Identity Vault root: `{report['identity_root']}`")
    lines.append(f"- Contract path: `{report['contract_path']}`")
    lines.append("")
    lines.append("## Contract Checks")
    checks = report["contract_checks"]
    for key in [
        "contract_exists", "contract_loaded", "contract_name_ok", "status_ok", "version_ok",
        "controlled_by_forge", "allowed_writes_empty", "canonical_db_path_ok",
        "forbidden_reads_present", "forbidden_writes_present", "future_rules_present",
        "activation_rule_present", "overall_ok",
    ]:
        lines.append(f"- `{key}`: `{checks.get(key)}`")
    if checks.get("issues"):
        lines.append(f"- issues: `{', '.join(checks['issues'])}`")
    else:
        lines.append("- issues: `none`")
    lines.append("")
    lines.append("## Sensitive File Handling")
    for item in report["sensitive_file_metadata"]:
        lines.append(f"- `{item['label']}` exists=`{item['exists']}` content_read=`{item['content_read']}`")
        if item.get("exists"):
            lines.append(f"  - size=`{item.get('size')}` mode=`{item.get('mode')}`")
    lines.append("- `.env` secret values were not read, printed, copied, hashed, or exported by this scan.")
    lines.append("")
    lines.append("## Ignore Hygiene Check")
    ignore = report["ignore_hygiene"]
    lines.append(f"- `.gitignore` managed block present: `{ignore['gitignore_managed_block_present']}`")
    lines.append(f"- `.dockerignore` managed block present: `{ignore['dockerignore_managed_block_present']}`")
    lines.append(f"- required gitignore rules present: `{ignore['required_gitignore_rules_present']}`")
    lines.append(f"- required dockerignore rules present: `{ignore['required_dockerignore_rules_present']}`")
    lines.append("")
    lines.append("## Canonical Database Read-Only Summary")
    db = report["canonical_db_readonly_summary"]
    lines.append(f"- path: `{db['path']}`")
    lines.append(f"- exists: `{db['exists']}`")
    lines.append(f"- opened_readonly: `{db['opened_readonly']}`")
    lines.append(f"- ok: `{db['ok']}`")
    if db.get("error"):
        lines.append(f"- error: `{db['error']}`")
    lines.append(f"- tables: `{', '.join(db.get('tables', []))}`")
    for table, count in db.get("row_counts", {}).items():
        lines.append(f"  - `{table}` rows: `{count}`")
    lines.append("")
    lines.append("## Adapter Readiness Preview")
    adapter = report["adapter_readiness"]
    for key, value in adapter.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Allowed Metadata Preview")
    meta = report["allowed_identity_metadata_preview"]
    lines.append(f"- service: `{meta.get('service')}`")
    lines.append(f"- package name: `{meta.get('package', {}).get('name')}`")
    lines.append(f"- package version: `{meta.get('package', {}).get('version')}`")
    lines.append(f"- identity tables present: `{meta.get('identity_tables_present')}`")
    lines.append(f"- row counts: `{meta.get('db_row_counts')}`")
    lines.append("")
    lines.append("## Findings")
    if report["findings"]:
        for finding in report["findings"]:
            lines.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    else:
        lines.append("- **INFO** `IV_ADAPTER_READINESS_CLEAN` — No blocking findings detected.")
    lines.append("")
    lines.append("## Next Safe Step")
    lines.append("Create a future Forge Identity Vault read-only adapter file that loads this draft contract and exposes read-only metadata functions only. Do not activate agent identities yet.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    home = Path.home()
    forge_root = home / "forge"
    identity_root = home / "identity-vault"
    timestamp = now_stamp()
    run_dir = forge_root / "memory" / MEMORY_DIR_NAME / timestamp
    latest_md = forge_root / "memory" / MEMORY_DIR_NAME / f"latest_{MEMORY_DIR_NAME.replace('_v1', '')}.md"
    latest_json = forge_root / "memory" / MEMORY_DIR_NAME / f"latest_{MEMORY_DIR_NAME.replace('_v1', '')}.json"

    contract_path = identity_root / CONTRACT_REL
    package_path = identity_root / "package.json"
    gitignore_path = identity_root / ".gitignore"
    dockerignore_path = identity_root / ".dockerignore"

    contract_ok, contract, contract_err = read_json(contract_path)
    pkg_ok, package_json, pkg_err = read_json(package_path)

    canonical_db = Path((contract or {}).get("canonical_database_path", str(identity_root / "data" / "identity_vault.db")))
    db_summary = sqlite_readonly_summary(canonical_db)
    contract_checks = validate_contract(contract if contract_ok else None, contract_path, identity_root)

    gitignore_text = read_text_if_safe(gitignore_path)
    dockerignore_text = read_text_if_safe(dockerignore_path)
    required_rules = [".env", "node_modules/", "*.db", "data/*.db"]
    ignore_hygiene = {
        "gitignore_exists": gitignore_path.exists(),
        "dockerignore_exists": dockerignore_path.exists(),
        "gitignore_managed_block_present": MANAGED_GITIGNORE_MARKER in gitignore_text,
        "dockerignore_managed_block_present": MANAGED_DOCKERIGNORE_MARKER in dockerignore_text,
        "required_gitignore_rules_present": all(rule in gitignore_text for rule in required_rules),
        "required_dockerignore_rules_present": all(rule in dockerignore_text for rule in required_rules),
    }

    sensitive_file_metadata = [
        file_stat_metadata(identity_root / ".env", ".env"),
        file_stat_metadata(identity_root / ".env.example", ".env.example"),
    ]

    allowed_metadata = list_allowed_identity_metadata(contract if contract_ok else None, package_json if pkg_ok else None, db_summary)

    adapter_readiness = {
        "contract_ready_for_readonly_adapter": contract_checks["overall_ok"],
        "canonical_db_readonly_ok": bool(db_summary.get("ok") and db_summary.get("opened_readonly")),
        "identity_tables_available": bool("agent_profiles" in db_summary.get("tables", []) and "user_profiles" in db_summary.get("tables", [])),
        "package_metadata_available": bool(pkg_ok),
        "ignore_hygiene_ok": bool(ignore_hygiene["gitignore_managed_block_present"] and ignore_hygiene["dockerignore_managed_block_present"]),
        "agent_identity_activation_performed": False,
        "database_write_performed": False,
        "env_secret_values_read": False,
    }

    findings: List[Dict[str, str]] = []
    if not contract_ok:
        findings.append({"level": "ERROR", "code": "IV_CONTRACT_LOAD_FAILED", "message": contract_err or "Contract failed to load."})
    if not contract_checks["overall_ok"]:
        findings.append({"level": "WARN", "code": "IV_CONTRACT_DRAFT_NOT_READY", "message": "Draft contract is missing one or more expected boundary fields."})
    if not db_summary.get("ok"):
        findings.append({"level": "ERROR", "code": "IV_CANONICAL_DB_READONLY_FAILED", "message": db_summary.get("error") or "Canonical database read-only scan failed."})
    if not adapter_readiness["identity_tables_available"]:
        findings.append({"level": "WARN", "code": "IV_IDENTITY_TABLES_MISSING", "message": "Expected agent_profiles and user_profiles tables were not both present."})
    if not ignore_hygiene["required_gitignore_rules_present"]:
        findings.append({"level": "WARN", "code": "IV_GITIGNORE_RULES_INCOMPLETE", "message": "Required local runtime exclusion rules were not all found in .gitignore."})
    if not ignore_hygiene["required_dockerignore_rules_present"]:
        findings.append({"level": "WARN", "code": "IV_DOCKERIGNORE_RULES_INCOMPLETE", "message": "Required local runtime exclusion rules were not all found in .dockerignore."})
    if (identity_root / ".env").exists():
        findings.append({"level": "INFO", "code": "IV_ENV_LOCAL_PRESENT_NOT_READ", "message": ".env exists locally; this scan recorded stat metadata only and did not read secret values."})

    hard_fail = any(f["level"] == "ERROR" for f in findings)
    readiness_ok = all([
        adapter_readiness["contract_ready_for_readonly_adapter"],
        adapter_readiness["canonical_db_readonly_ok"],
        adapter_readiness["identity_tables_available"],
        adapter_readiness["package_metadata_available"],
        adapter_readiness["ignore_hygiene_ok"],
    ])
    verdict = "PASS" if readiness_ok and not hard_fail else ("WARN" if not hard_fail else "FAIL")

    report: Dict[str, Any] = {
        "timestamp": timestamp,
        "patch": PATCH_NAME,
        "verdict": verdict,
        "forge_root": str(forge_root),
        "identity_root": str(identity_root),
        "contract_path": str(contract_path),
        "boundary": [
            "This scan is read-only except for writing reports under Forge memory.",
            "It reads the draft service contract and approved package/database metadata only.",
            "It opens the canonical SQLite database in read-only mode for schema and row counts only.",
            "It does not read .env secret values, write databases, register tools, or activate agent identities.",
        ],
        "contract_load": {"ok": contract_ok, "error": contract_err},
        "package_load": {"ok": pkg_ok, "error": pkg_err},
        "contract_checks": contract_checks,
        "sensitive_file_metadata": sensitive_file_metadata,
        "ignore_hygiene": ignore_hygiene,
        "canonical_db_readonly_summary": db_summary,
        "allowed_identity_metadata_preview": allowed_metadata,
        "adapter_readiness": adapter_readiness,
        "findings": findings,
        "outputs": {
            "run_dir": str(run_dir),
            "latest_markdown": str(latest_md),
            "latest_json": str(latest_json),
        },
    }

    run_dir.mkdir(parents=True, exist_ok=True)
    run_json = run_dir / f"{timestamp}_identity_vault_patch217_adapter_readiness_scan.json"
    run_md = run_dir / f"{timestamp}_identity_vault_patch217_adapter_readiness_scan.md"
    write_json(run_json, report)
    write_json(latest_json, report)
    write_markdown(run_md, report)
    write_markdown(latest_md, report)

    print("Identity Vault Patch 217 adapter readiness scan complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {verdict}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
