#!/usr/bin/env python3
"""
Patch 215 — Identity Vault Hygiene Plan

Read-only planning script. It inspects Identity Vault metadata and writes a hygiene plan,
canonical database recommendation, packaging exclusions, and a draft read-only service
contract under Forge memory.

It does NOT modify Identity Vault, .env, databases, node_modules, Forge tools, Forge registry,
RMC memory, AI.Web wrappers, or agent identity configuration.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sqlite3
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

FORGE_ROOT = Path.home() / "forge"
IDENTITY_VAULT_ROOT = Path.home() / "identity-vault"
MEMORY_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch215_hygiene_plan_v1"
LATEST_MD = MEMORY_ROOT / "latest_identity_vault_patch215_hygiene_plan.md"
LATEST_JSON = MEMORY_ROOT / "latest_identity_vault_patch215_hygiene_plan.json"
LATEST_CONTRACT = MEMORY_ROOT / "latest_identity_vault_readonly_service_contract_draft.json"

DATABASE_CANDIDATES = [
    IDENTITY_VAULT_ROOT / "data" / "identity_vault.db",
    IDENTITY_VAULT_ROOT / "vault.db",
]

SENSITIVE_CANDIDATES = [
    IDENTITY_VAULT_ROOT / ".env",
    IDENTITY_VAULT_ROOT / ".env.example",
]

PACKAGE_EXCLUSION_RULES = [
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


def sha256_file(path: Path) -> Optional[str]:
    try:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def stat_file(path: Path) -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "path": str(path),
        "relative_path": str(path.relative_to(Path.home())) if path.exists() else str(path),
        "exists": path.exists(),
    }
    if path.exists():
        st = path.stat()
        info.update(
            {
                "size": st.st_size,
                "mode": oct(st.st_mode & 0o777),
                "sha256": sha256_file(path),
            }
        )
    return info


def read_text_safe(path: Path, max_chars: int = 20000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except Exception:
        return ""


def load_json_safe(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def sqlite_summary(path: Path) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "ok": False,
        "tables": [],
        "row_counts": {},
        "schemas": {},
        "error": None,
    }
    if not path.exists():
        return summary
    try:
        uri = f"file:{path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        summary["tables"] = tables
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                summary["row_counts"][table] = cur.fetchone()[0]
            except Exception as e:
                summary["row_counts"][table] = f"ERROR: {e}"
            try:
                cur.execute(f"PRAGMA table_info({table})")
                summary["schemas"][table] = [
                    {"cid": row[0], "name": row[1], "type": row[2], "notnull": row[3], "default": row[4], "pk": row[5]}
                    for row in cur.fetchall()
                ]
            except Exception as e:
                summary["schemas"][table] = f"ERROR: {e}"
        conn.close()
        summary["ok"] = True
    except Exception as e:
        summary["error"] = str(e)
    return summary


def git_status(root: Path) -> Dict[str, Any]:
    if not (root / ".git").exists():
        return {"is_git_repo": False, "returncode": None, "stdout": "", "stderr": ""}
    try:
        proc = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
        return {
            "is_git_repo": True,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    except Exception as e:
        return {"is_git_repo": True, "returncode": None, "stdout": "", "stderr": str(e)}


def ignore_analysis(root: Path) -> Dict[str, Any]:
    gitignore = read_text_safe(root / ".gitignore")
    dockerignore = read_text_safe(root / ".dockerignore")
    combined = gitignore + "\n" + dockerignore
    return {
        "gitignore_exists": (root / ".gitignore").exists(),
        "dockerignore_exists": (root / ".dockerignore").exists(),
        "has_env_rule": ".env" in combined,
        "has_node_modules_rule": "node_modules" in combined,
        "has_db_rule": any(token in combined for token in ["*.db", "*.sqlite", "data/*.db", "vault.db"]),
        "recommended_rules": PACKAGE_EXCLUSION_RULES,
    }


def choose_canonical_database(db_summaries: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    primary = IDENTITY_VAULT_ROOT / "data" / "identity_vault.db"
    legacy = IDENTITY_VAULT_ROOT / "vault.db"
    primary_summary = db_summaries.get(str(primary), {})
    legacy_summary = db_summaries.get(str(legacy), {})

    reasons: List[str] = []
    if primary_summary.get("exists"):
        reasons.append("`data/identity_vault.db` already exists under the app data directory.")
    if {"agent_profiles", "user_profiles"}.issubset(set(primary_summary.get("tables", []))):
        reasons.append("It contains explicit `agent_profiles` and `user_profiles` tables needed for future agent identity boundaries.")
    if legacy_summary.get("exists"):
        reasons.append("`vault.db` appears to be a legacy root-level runtime database and should not be selected as the forward canonical path without migration review.")
    if set(legacy_summary.get("tables", [])) and not {"agent_profiles", "user_profiles"}.issubset(set(legacy_summary.get("tables", []))):
        reasons.append("The legacy database schema is narrower and lacks the newer identity tables visible in the data-directory database.")

    return {
        "canonical_database_path": str(primary),
        "legacy_database_path": str(legacy),
        "selection": "data/identity_vault.db",
        "status": "PLAN_ONLY_NOT_APPLIED",
        "reasons": reasons,
        "migration_rule": "Do not delete or move `vault.db`; treat it as a legacy migration candidate until a later backup + schema migration patch is approved.",
    }


def build_service_contract(canonical_db_path: str) -> Dict[str, Any]:
    return {
        "contract_name": "identity_vault_readonly_service_contract_draft",
        "version": "0.1.0-plan-only",
        "status": "DRAFT_NOT_ACTIVE",
        "service": "Identity Vault",
        "service_role": "Agent identity, permissions, profile metadata, and memory namespace pointers. It is not an agent runtime and not the shared memory store.",
        "controlled_by": "Forge",
        "root": str(IDENTITY_VAULT_ROOT),
        "canonical_database_path": canonical_db_path,
        "allowed_reads": [
            "package.json metadata",
            "README and documentation metadata",
            "SQLite schema and row counts using read-only connections",
            "agent profile metadata after explicit adapter approval",
            "identity-to-RMC namespace pointers after explicit adapter approval",
        ],
        "forbidden_reads": [
            ".env secret values",
            "raw tokens, private keys, JWT secrets, API keys, passwords",
            "full private memory payloads unless routed through approved RMC boundary",
        ],
        "allowed_writes": [],
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
    }


def build_plan() -> Dict[str, Any]:
    root = IDENTITY_VAULT_ROOT
    package_json = load_json_safe(root / "package.json")
    db_summaries = {str(p): sqlite_summary(p) for p in DATABASE_CANDIDATES}
    canonical = choose_canonical_database(db_summaries)
    contract = build_service_contract(canonical["canonical_database_path"])

    findings: List[Dict[str, str]] = []
    if (root / "node_modules").exists():
        findings.append({"level": "WARN", "code": "IV_NODE_MODULES_PRESENT", "message": "node_modules is present. Do not package it into patches or archives."})
    if (root / ".env").exists():
        findings.append({"level": "WARN", "code": "IV_ENV_PRESENT", "message": ".env exists. Do not package it. Rotate secrets if it was shared outside the local machine."})
    if sum(1 for p in DATABASE_CANDIDATES if p.exists()) > 1:
        findings.append({"level": "WARN", "code": "IV_MULTIPLE_DATABASES", "message": "Multiple SQLite databases exist. Use the plan-selected canonical DB and preserve the other as legacy until migration review."})
    ia = ignore_analysis(root)
    if not ia["has_db_rule"]:
        findings.append({"level": "INFO", "code": "IV_GITIGNORE_DB_RULE_MISSING", "message": "Database/runtime ignore rules should be added in a later hygiene patch."})

    plan_steps = [
        {
            "step": 1,
            "name": "Freeze Identity Vault before changes",
            "action": "Create timestamped backup of package.json, .gitignore, .dockerignore, database metadata, and both database files before any hygiene patch modifies files.",
            "write_status": "future patch only",
        },
        {
            "step": 2,
            "name": "Lock packaging exclusions",
            "action": "Update archive/patch packaging policy so `.env`, `node_modules/`, SQLite databases, logs, coverage, and runtime backups are never included in future patch tarballs.",
            "write_status": "future patch only",
        },
        {
            "step": 3,
            "name": "Select canonical database path",
            "action": "Treat `identity-vault/data/identity_vault.db` as canonical because it has the newer agent/user profile schema; keep `identity-vault/vault.db` as legacy migration candidate.",
            "write_status": "plan decision only",
        },
        {
            "step": 4,
            "name": "Prepare database migration review",
            "action": "Compare rows/schemas, export a migration preview if data exists, and refuse deletion until backup + verification exists.",
            "write_status": "future patch only",
        },
        {
            "step": 5,
            "name": "Create read-only service contract",
            "action": "Use the generated draft contract as the boundary for the future Forge Identity Vault adapter.",
            "write_status": "this script writes draft only under Forge memory",
        },
        {
            "step": 6,
            "name": "Build read-only adapter after hygiene",
            "action": "Forge may read identity metadata and RMC namespace pointers, but cannot activate identities or write Identity Vault state until a later approval gate.",
            "write_status": "future patch only",
        },
    ]

    return {
        "timestamp": utc_stamp(),
        "verdict": "PASS" if root.exists() else "FAIL",
        "boundary": {
            "read_only": True,
            "writes": [str(MEMORY_ROOT)],
            "does_not_modify": [
                "Identity Vault files",
                "Identity Vault databases",
                ".env",
                "node_modules",
                "Forge tools",
                "Forge registry",
                "RMC memory",
                "AI.Web wrappers",
                "agent identity configuration",
            ],
        },
        "root": {"path": str(root), "exists": root.exists()},
        "package": {
            "name": package_json.get("name"),
            "version": package_json.get("version"),
            "scripts": sorted(list((package_json.get("scripts") or {}).keys())),
        },
        "sensitive_files": [stat_file(p) for p in SENSITIVE_CANDIDATES if p.exists()],
        "database_files": [stat_file(p) for p in DATABASE_CANDIDATES if p.exists()],
        "database_summaries": db_summaries,
        "canonical_database_decision": canonical,
        "ignore_analysis": ia,
        "git_status": git_status(root),
        "findings": findings,
        "hygiene_plan": plan_steps,
        "service_contract_draft": contract,
        "next_safe_step": "Create a future hygiene patch that backs up Identity Vault, adds ignore/packaging rules, and writes the service contract as a draft file only. Do not activate agent identities yet.",
    }


def write_reports(plan: Dict[str, Any], run_dir: Path) -> Tuple[Path, Path, Path]:
    run_dir.mkdir(parents=True, exist_ok=True)
    MEMORY_ROOT.mkdir(parents=True, exist_ok=True)
    json_path = run_dir / f"{plan['timestamp']}_identity_vault_patch215_hygiene_plan.json"
    md_path = run_dir / f"{plan['timestamp']}_identity_vault_patch215_hygiene_plan.md"
    contract_path = run_dir / f"{plan['timestamp']}_identity_vault_readonly_service_contract_draft.json"

    json_path.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")
    contract_path.write_text(json.dumps(plan["service_contract_draft"], indent=2, sort_keys=True), encoding="utf-8")

    md = render_markdown(plan, json_path, contract_path)
    md_path.write_text(md, encoding="utf-8")

    LATEST_JSON.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")
    LATEST_CONTRACT.write_text(json.dumps(plan["service_contract_draft"], indent=2, sort_keys=True), encoding="utf-8")
    LATEST_MD.write_text(md, encoding="utf-8")
    return md_path, json_path, contract_path


def render_markdown(plan: Dict[str, Any], json_path: Path, contract_path: Path) -> str:
    lines: List[str] = []
    lines.append("# Identity Vault Patch 215 Hygiene Plan")
    lines.append("")
    lines.append(f"Timestamp: `{plan['timestamp']}`")
    lines.append(f"Verdict: **{plan['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This is a planning scan only.")
    lines.append("- It writes reports only under Forge memory.")
    for item in plan["boundary"]["does_not_modify"]:
        lines.append(f"- Does not modify: `{item}`")
    lines.append("")
    lines.append("## Root")
    lines.append(f"- root: `{plan['root']['path']}`")
    lines.append(f"- exists: `{plan['root']['exists']}`")
    lines.append("")
    lines.append("## Canonical Database Decision")
    c = plan["canonical_database_decision"]
    lines.append(f"- selected canonical path: `{c['canonical_database_path']}`")
    lines.append(f"- legacy path: `{c['legacy_database_path']}`")
    lines.append(f"- status: `{c['status']}`")
    for reason in c["reasons"]:
        lines.append(f"- reason: {reason}")
    lines.append(f"- migration rule: {c['migration_rule']}")
    lines.append("")
    lines.append("## Database Summary")
    for db_path, summary in plan["database_summaries"].items():
        lines.append(f"- `{db_path}` ok=`{summary.get('ok')}` exists=`{summary.get('exists')}`")
        lines.append(f"  - tables: `{', '.join(summary.get('tables') or [])}`")
        for table, count in (summary.get("row_counts") or {}).items():
            lines.append(f"  - `{table}` rows: `{count}`")
    lines.append("")
    lines.append("## Sensitive / Runtime File Policy")
    for sf in plan["sensitive_files"]:
        lines.append(f"- `{sf['relative_path']}` size=`{sf.get('size')}` mode=`{sf.get('mode')}` sha256=`{sf.get('sha256')}`")
    lines.append("- `.env` must never be packaged or printed.")
    lines.append("- `node_modules/` must never be packaged.")
    lines.append("- SQLite database files must not be packaged into patch tarballs unless a future backup/migration patch explicitly requires it and records approval.")
    lines.append("")
    lines.append("## Recommended Ignore / Packaging Exclusion Rules")
    for rule in plan["ignore_analysis"]["recommended_rules"]:
        lines.append(f"- `{rule}`")
    lines.append("")
    lines.append("## Findings")
    if plan["findings"]:
        for f in plan["findings"]:
            lines.append(f"- **{f['level']}** `{f['code']}` — {f['message']}")
    else:
        lines.append("- No hygiene warnings detected.")
    lines.append("")
    lines.append("## Hygiene Plan")
    for step in plan["hygiene_plan"]:
        lines.append(f"{step['step']}. **{step['name']}** — {step['action']} Status: `{step['write_status']}`")
    lines.append("")
    lines.append("## Read-Only Service Contract Draft")
    sc = plan["service_contract_draft"]
    lines.append(f"- contract: `{sc['contract_name']}`")
    lines.append(f"- version: `{sc['version']}`")
    lines.append(f"- status: `{sc['status']}`")
    lines.append(f"- role: {sc['service_role']}")
    lines.append("- allowed writes: none")
    lines.append("- future adapter rule: Forge may ask Identity Vault who an agent is, what permissions it has, and which RMC namespace it points to; Forge may not execute agents inside Identity Vault.")
    lines.append("")
    lines.append("## Output Files")
    lines.append(f"- JSON plan: `{json_path}`")
    lines.append(f"- service contract draft: `{contract_path}`")
    lines.append("")
    lines.append("## Next Safe Step")
    lines.append(plan["next_safe_step"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ts = utc_stamp()
    run_dir = MEMORY_ROOT / ts
    plan = build_plan()
    plan["timestamp"] = ts
    md_path, json_path, contract_path = write_reports(plan, run_dir)
    print("Identity Vault Patch 215 hygiene plan complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {LATEST_MD}")
    print(f"JSON plan: {LATEST_JSON}")
    print(f"Contract draft: {LATEST_CONTRACT}")
    print(f"Verdict: {plan['verdict']}")
    return 0 if plan["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
