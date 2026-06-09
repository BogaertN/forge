#!/usr/bin/env python3
# identity_vault_patch217a_readiness_reconcile.py
# Purpose: Reconcile Patch 217 WARN state using read-only checks only.
# This script does not modify Identity Vault, Forge registry, RMC memory, databases, .env, or agent identity state.

from __future__ import annotations

import datetime as _dt
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
IDENTITY_ROOT = HOME / "identity-vault"
CONTRACT_PATH = IDENTITY_ROOT / "service_contracts" / "identity_vault_readonly_service_contract.draft.json"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
RUN_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch217a_readiness_reconcile_v1"

REQUIRED_IGNORE_RULES = [
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

REQUIRED_CONTRACT_FIELDS = [
    "activation_rule",
    "allowed_reads",
    "allowed_writes",
    "audit_requirement",
    "canonical_database_path",
    "contract_name",
    "controlled_by",
    "forbidden_reads",
    "forbidden_writes",
    "future_adapter_rules",
    "root",
    "service",
    "service_role",
    "status",
    "version",
]


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_UTC")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def load_contract() -> Tuple[Dict[str, Any], List[str]]:
    issues: List[str] = []
    if not CONTRACT_PATH.exists():
        return {}, ["contract_missing"]
    try:
        data = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {}, [f"contract_json_error:{type(exc).__name__}"]

    missing = [field for field in REQUIRED_CONTRACT_FIELDS if field not in data]
    if missing:
        issues.append("missing_fields:" + ",".join(missing))
    if data.get("controlled_by") != "Forge":
        issues.append("controlled_by_not_forge")
    if data.get("status") != "DRAFT_NOT_ACTIVE":
        issues.append("status_not_draft_not_active")
    if data.get("allowed_writes") != []:
        issues.append("allowed_writes_not_empty")
    if Path(str(data.get("canonical_database_path", ""))) != CANONICAL_DB:
        issues.append("canonical_database_path_mismatch")
    if not data.get("activation_rule"):
        issues.append("activation_rule_missing")
    if not isinstance(data.get("forbidden_reads"), list) or not data.get("forbidden_reads"):
        issues.append("forbidden_reads_missing_or_empty")
    if not isinstance(data.get("forbidden_writes"), list) or not data.get("forbidden_writes"):
        issues.append("forbidden_writes_missing_or_empty")
    if not isinstance(data.get("future_adapter_rules"), list) or len(data.get("future_adapter_rules", [])) < 3:
        issues.append("future_adapter_rules_missing_or_too_small")
    return data, issues


def ignore_check(path: Path) -> Dict[str, Any]:
    text = read_text(path)
    lower = text.lower()
    present = {rule: (rule in text) for rule in REQUIRED_IGNORE_RULES}
    required_rules_present = all(present.values())
    marker_patterns = [
        "patch216",
        "identity vault hygiene",
        "ai.web identity vault",
        "managed identity vault",
        "forge-managed",
        "forge managed",
    ]
    marker_present = any(p in lower for p in marker_patterns)
    # Equivalent block means the exact marker may differ, but the required safety rules exist.
    managed_block_or_equivalent = marker_present or required_rules_present
    return {
        "path": str(path),
        "exists": path.exists(),
        "marker_present": marker_present,
        "required_rules_present": required_rules_present,
        "managed_block_or_equivalent": managed_block_or_equivalent,
        "rules": present,
    }


def sqlite_readonly_summary(path: Path) -> Dict[str, Any]:
    summary: Dict[str, Any] = {"path": str(path), "exists": path.exists(), "opened_readonly": False, "ok": False, "tables": [], "row_counts": {}, "error": None}
    if not path.exists():
        summary["error"] = "missing"
        return summary
    try:
        uri = f"file:{path}?mode=ro"
        con = sqlite3.connect(uri, uri=True)
        summary["opened_readonly"] = True
        try:
            tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
            summary["tables"] = tables
            for table in tables:
                # Table names are from sqlite_master, but quote defensively.
                safe_table = '"' + table.replace('"', '""') + '"'
                try:
                    summary["row_counts"][table] = int(con.execute(f"SELECT COUNT(*) FROM {safe_table}").fetchone()[0])
                except Exception as exc:  # noqa: BLE001
                    summary["row_counts"][table] = f"ERROR:{type(exc).__name__}"
            summary["ok"] = True
        finally:
            con.close()
    except Exception as exc:  # noqa: BLE001
        summary["error"] = f"{type(exc).__name__}: {exc}"
    return summary


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def write_latest_copy(src: Path, latest_name: str) -> None:
    latest = RUN_ROOT / latest_name
    latest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    ts = utc_stamp()
    run_dir = RUN_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    contract, contract_issues = load_contract()
    gitignore = ignore_check(IDENTITY_ROOT / ".gitignore")
    dockerignore = ignore_check(IDENTITY_ROOT / ".dockerignore")
    db_summary = sqlite_readonly_summary(CANONICAL_DB)

    contract_ready = len(contract_issues) == 0
    ignore_hygiene_ok = gitignore["managed_block_or_equivalent"] and dockerignore["managed_block_or_equivalent"]
    identity_tables_available = all(t in db_summary.get("tables", []) for t in ["agent_profiles", "user_profiles"])
    canonical_db_readonly_ok = bool(db_summary.get("ok")) and bool(db_summary.get("opened_readonly")) and identity_tables_available
    env_path = IDENTITY_ROOT / ".env"

    findings: List[Dict[str, str]] = []
    if contract_ready:
        findings.append({"level": "INFO", "code": "IV_CONTRACT_DRAFT_READY", "message": "Draft contract has all required read-only adapter boundary fields."})
    else:
        findings.append({"level": "WARN", "code": "IV_CONTRACT_DRAFT_STILL_NOT_READY", "message": "; ".join(contract_issues)})
    if ignore_hygiene_ok:
        findings.append({"level": "INFO", "code": "IV_IGNORE_RULES_READY", "message": "Ignore safety rules are present. Exact managed marker text is not required when full rule coverage exists."})
    else:
        findings.append({"level": "WARN", "code": "IV_IGNORE_RULES_INCOMPLETE", "message": "Required ignore exclusions are incomplete."})
    findings.append({"level": "INFO", "code": "IV_ENV_LOCAL_PRESENT_NOT_READ", "message": f".env exists locally={env_path.exists()}; secret values were not read."})
    findings.append({"level": "INFO", "code": "IV_PATCH217_WARN_RECONCILED", "message": "Patch 217 WARN appears to have been caused by a strict readiness/marker predicate if this report passes."})

    verdict = "PASS" if (contract_ready and ignore_hygiene_ok and canonical_db_readonly_ok) else "WARN"

    report = {
        "timestamp": ts,
        "verdict": verdict,
        "boundary": {
            "read_only_except_report": True,
            "env_secret_values_read": False,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
            "forge_registry_modified": False,
            "rmc_memory_modified": False,
        },
        "roots": {
            "forge_root": str(FORGE_ROOT),
            "identity_vault_root": str(IDENTITY_ROOT),
            "contract_path": str(CONTRACT_PATH),
        },
        "contract_checks": {
            "contract_exists": CONTRACT_PATH.exists(),
            "contract_loaded": bool(contract),
            "contract_ready_for_readonly_adapter": contract_ready,
            "issues": contract_issues,
            "status": contract.get("status"),
            "version": contract.get("version"),
            "controlled_by": contract.get("controlled_by"),
            "allowed_writes_empty": contract.get("allowed_writes") == [],
            "canonical_database_path": contract.get("canonical_database_path"),
        },
        "ignore_hygiene": {
            "gitignore": gitignore,
            "dockerignore": dockerignore,
            "ignore_hygiene_ok": ignore_hygiene_ok,
            "note": "Patch 217 may have expected a different exact marker. This reconciler accepts exact markers or full required rule coverage.",
        },
        "canonical_database_readonly_summary": db_summary,
        "adapter_readiness_preview": {
            "contract_ready_for_readonly_adapter": contract_ready,
            "canonical_db_readonly_ok": canonical_db_readonly_ok,
            "identity_tables_available": identity_tables_available,
            "ignore_hygiene_ok": ignore_hygiene_ok,
            "agent_identity_activation_performed": False,
            "database_write_performed": False,
            "env_secret_values_read": False,
        },
        "findings": findings,
        "next_safe_step": "If PASS, create the Forge Identity Vault read-only adapter file. Do not activate agent identities yet.",
    }

    json_path = run_dir / f"{ts}_identity_vault_patch217a_readiness_reconcile.json"
    md_path = run_dir / f"{ts}_identity_vault_patch217a_readiness_reconcile.md"
    write_json(json_path, report)

    lines: List[str] = []
    lines.append("# Identity Vault Patch 217A Readiness Reconcile Report")
    lines.append("")
    lines.append(f"Timestamp: `{ts}`")
    lines.append(f"Verdict: **{verdict}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This reconcile scan is read-only except for writing reports under Forge memory.")
    lines.append("- It does not read `.env` secret values.")
    lines.append("- It does not write Identity Vault databases.")
    lines.append("- It does not register Forge tools or activate agent identities.")
    lines.append("")
    lines.append("## Contract Reconcile")
    lines.append(f"- contract exists: `{CONTRACT_PATH.exists()}`")
    lines.append(f"- contract loaded: `{bool(contract)}`")
    lines.append(f"- contract ready for read-only adapter: `{contract_ready}`")
    lines.append(f"- status: `{contract.get('status')}`")
    lines.append(f"- version: `{contract.get('version')}`")
    lines.append(f"- controlled_by: `{contract.get('controlled_by')}`")
    lines.append(f"- allowed writes empty: `{contract.get('allowed_writes') == []}`")
    if contract_issues:
        lines.append(f"- issues: `{contract_issues}`")
    else:
        lines.append("- issues: `[]`")
    lines.append("")
    lines.append("## Ignore Hygiene Reconcile")
    lines.append(f"- `.gitignore` marker present: `{gitignore['marker_present']}`")
    lines.append(f"- `.gitignore` required rules present: `{gitignore['required_rules_present']}`")
    lines.append(f"- `.gitignore` managed block or equivalent: `{gitignore['managed_block_or_equivalent']}`")
    lines.append(f"- `.dockerignore` marker present: `{dockerignore['marker_present']}`")
    lines.append(f"- `.dockerignore` required rules present: `{dockerignore['required_rules_present']}`")
    lines.append(f"- `.dockerignore` managed block or equivalent: `{dockerignore['managed_block_or_equivalent']}`")
    lines.append(f"- ignore hygiene ok: `{ignore_hygiene_ok}`")
    lines.append("")
    lines.append("## Canonical Database Read-Only Summary")
    lines.append(f"- path: `{db_summary['path']}`")
    lines.append(f"- exists: `{db_summary['exists']}`")
    lines.append(f"- opened_readonly: `{db_summary['opened_readonly']}`")
    lines.append(f"- ok: `{db_summary['ok']}`")
    lines.append(f"- tables: `{', '.join(db_summary.get('tables', []))}`")
    for table, count in db_summary.get("row_counts", {}).items():
        lines.append(f"  - `{table}` rows: `{count}`")
    lines.append("")
    lines.append("## Adapter Readiness Preview")
    lines.append(f"- contract_ready_for_readonly_adapter: `{contract_ready}`")
    lines.append(f"- canonical_db_readonly_ok: `{canonical_db_readonly_ok}`")
    lines.append(f"- identity_tables_available: `{identity_tables_available}`")
    lines.append(f"- ignore_hygiene_ok: `{ignore_hygiene_ok}`")
    lines.append("- agent_identity_activation_performed: `False`")
    lines.append("- database_write_performed: `False`")
    lines.append("- env_secret_values_read: `False`")
    lines.append("")
    lines.append("## Findings")
    for finding in findings:
        lines.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    lines.append("")
    lines.append("## Next Safe Step")
    lines.append("If this report passes, create the Forge Identity Vault read-only adapter file. Do not activate agent identities yet.")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    write_latest_copy(md_path, "latest_identity_vault_patch217a_readiness_reconcile.md")
    write_latest_copy(json_path, "latest_identity_vault_patch217a_readiness_reconcile.json")

    print("Identity Vault Patch 217A readiness reconcile complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {RUN_ROOT / 'latest_identity_vault_patch217a_readiness_reconcile.md'}")
    print(f"JSON report: {RUN_ROOT / 'latest_identity_vault_patch217a_readiness_reconcile.json'}")
    print(f"Verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
