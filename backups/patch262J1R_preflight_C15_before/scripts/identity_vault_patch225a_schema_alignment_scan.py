#!/usr/bin/env python3
# identity_vault_patch225a_schema_alignment_scan.py
# Purpose: Read-only schema alignment scan for Identity Vault operational profile blueprint.
# Boundary: Writes reports only under /home/nic/forge/memory. Does not modify databases, .env,
# node_modules, Forge registry, RMC memory, service contracts, or agent identity activation state.

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

PATCH_ID = "patch225a_identity_vault_schema_alignment_scan"
REPORT_ROOT = Path.home() / "forge" / "memory" / "identity_vault_patch225a_schema_alignment_scan_v1"
FORGE_ROOT = Path.home() / "forge"
IDENTITY_ROOT = Path.home() / "identity-vault"
AIWEB_ROOT = Path.home() / "aiweb"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"
CONTRACT_DRAFT = IDENTITY_ROOT / "service_contracts" / "identity_vault_readonly_service_contract.draft.json"
AIWEB_CONTRACT = AIWEB_ROOT / "service_contracts" / "identity_vault.contract.json"

# Source of truth extracted from the Self-Hosted Identity Vault blueprint.
# These are the operational profile fields from the manual, not invented runtime fields.
USER_PROFILE_FIELDS = [
    "user_id",
    "canonical_name",
    "spirit_name",
    "project_affiliations",
    "identity_tags",
    "version",
    "last_updated",
    "project_context",
    "interaction_preferences",
    "meta_rules",
    "session_state",
]
USER_PROFILE_NESTED_FIELDS = {
    "project_context": ["current_project", "phase", "current_files", "active_collaborators", "subsystems", "goals"],
    "interaction_preferences": [
        "formality", "depth", "step_by_step", "beginner_friendly", "plain_language", "no_boxes",
        "pushback", "critique_mandatory", "confirmation_required", "formatting_rules",
    ],
    "meta_rules": [
        "recursive_feedback", "drift_tracking", "contradiction_alerts", "require_honest_pushback",
        "preserve_session_memory", "require_context_carryover", "log_all_exchanges",
        "always_explain_decisions", "safe_words", "forbidden_actions",
    ],
    "session_state": ["phase", "waiting_for", "last_feedback", "last_action", "timestamp"],
}

AGENT_PROFILE_FIELDS = [
    "agent_id",
    "canonical_name",
    "version",
    "last_updated",
    "role",
    "symbolic_signature",
    "description",
    "capabilities",
    "limitations",
    "persona",
    "voice_style",
    "quotes_or_character_inspiration",
    "special_style_notes",
    "permissions",
    "authority",
    "enforcement_rules",
    "forbidden_actions",
    "session_state",
    "last_action",
    "last_feedback",
    "log_fields",
    "timestamp",
]

# Acceptable columns that can hold structured JSON payloads if the DB chooses a blob strategy
# rather than one column per blueprint field.
JSON_CONTAINER_HINTS = {
    "profile_json", "profile", "payload", "data", "metadata", "json", "context_json",
    "settings", "config", "identity_json", "operational_identity", "agent_profile", "user_profile",
}

SAFE_CODE_FILES = [
    "db.js",
    "schemas.js",
    "server.js",
    "cli.js",
    "routes/agents.js",
    "routes/profiles.js",
    "routes/identity.js",
    "routes/api.js",
    "tests/server.test.js",
    "tests/db.canonical.test.js",
    "Design_Manual_System_Blueprint.md",
    "Identity_Vault_Pro.md",
    "README.md",
]

FORBIDDEN_TO_READ = {".env"}


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


def safe_stat(path: Path) -> Dict[str, Any]:
    try:
        st = path.stat()
        return {
            "exists": True,
            "size": st.st_size,
            "mode": oct(st.st_mode & 0o777),
            "sha256": sha256_file(path),
        }
    except FileNotFoundError:
        return {"exists": False}


def read_json(path: Path) -> Tuple[bool, Dict[str, Any], str | None]:
    try:
        return True, json.loads(path.read_text(encoding="utf-8")), None
    except Exception as e:
        return False, {}, f"{type(e).__name__}: {e}"


def sqlite_readonly_summary(path: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "opened_readonly": False,
        "ok": False,
        "tables": [],
        "schemas": {},
        "row_counts": {},
        "error": None,
    }
    if not path.exists():
        result["error"] = "missing"
        return result
    try:
        uri = f"file:{path.as_posix()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        result["opened_readonly"] = True
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        result["tables"] = tables
        for table in tables:
            cur.execute(f"PRAGMA table_info({quote_ident(table)})")
            cols = []
            for row in cur.fetchall():
                # cid, name, type, notnull, dflt_value, pk
                cols.append({
                    "cid": row[0],
                    "name": row[1],
                    "type": row[2],
                    "notnull": bool(row[3]),
                    "default": row[4],
                    "pk": bool(row[5]),
                })
            result["schemas"][table] = cols
            try:
                cur.execute(f"SELECT COUNT(*) FROM {quote_ident(table)}")
                result["row_counts"][table] = cur.fetchone()[0]
            except Exception as e:
                result["row_counts"][table] = f"ERROR: {type(e).__name__}: {e}"
        conn.close()
        result["ok"] = True
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    return result


def quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def colnames(schema: List[Dict[str, Any]]) -> List[str]:
    return [c.get("name", "") for c in schema]


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def has_json_container(cols: List[str]) -> bool:
    norm = {normalize_name(c) for c in cols}
    if norm & JSON_CONTAINER_HINTS:
        return True
    return any(n.endswith("_json") or n.endswith("_data") or n.endswith("_payload") for n in norm)


def alignment_for_table(table_name: str, schema: List[Dict[str, Any]], required_fields: List[str], nested: Dict[str, List[str]] | None = None) -> Dict[str, Any]:
    cols = colnames(schema)
    norm_cols = {normalize_name(c): c for c in cols}
    exact_present = []
    missing = []
    for f in required_fields:
        nf = normalize_name(f)
        if nf in norm_cols:
            exact_present.append(f)
        else:
            missing.append(f)
    container = has_json_container(cols)
    nested_hits: Dict[str, Dict[str, Any]] = {}
    if nested:
        for parent, fields in nested.items():
            nested_hits[parent] = {
                "parent_column_present": normalize_name(parent) in norm_cols,
                "nested_fields": fields,
                "note": "Nested fields may be represented in JSON only if a parent/container column exists.",
            }
    representation_ready = len(missing) == 0 or container
    return {
        "table": table_name,
        "columns": cols,
        "column_count": len(cols),
        "required_fields_count": len(required_fields),
        "exact_required_fields_present_count": len(exact_present),
        "exact_required_fields_present": exact_present,
        "missing_required_fields": missing,
        "json_container_present": container,
        "representation_strategy_ready": representation_ready,
        "readiness_rule": "Ready if all blueprint fields exist as columns OR a clear JSON/profile payload container exists.",
        "nested_preview": nested_hits,
    }


def scan_code_references(root: Path) -> Dict[str, Any]:
    field_terms = sorted(set(USER_PROFILE_FIELDS + AGENT_PROFILE_FIELDS + [x for fields in USER_PROFILE_NESTED_FIELDS.values() for x in fields]))
    results: Dict[str, Any] = {
        "files_scanned": [],
        "field_hit_counts": {t: 0 for t in field_terms},
        "files_with_hits": {},
        "api_endpoint_hits": {},
        "dangerous_file_skipped": [],
    }
    endpoint_patterns = [
        "/operational-identity",
        "/agent-identity",
        "agent_profiles",
        "user_profiles",
        "agentProfile",
        "userProfile",
    ]
    for rel in SAFE_CODE_FILES:
        p = root / rel
        if p.name in FORBIDDEN_TO_READ:
            results["dangerous_file_skipped"].append(rel)
            continue
        if not p.exists() or not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            results["files_with_hits"][rel] = {"error": f"{type(e).__name__}: {e}"}
            continue
        results["files_scanned"].append(rel)
        hits = {}
        lower = text.lower()
        for term in field_terms:
            count = lower.count(term.lower())
            if count:
                hits[term] = count
                results["field_hit_counts"][term] += count
        ep_hits = {}
        for pat in endpoint_patterns:
            count = lower.count(pat.lower())
            if count:
                ep_hits[pat] = count
        if hits or ep_hits:
            results["files_with_hits"][rel] = {
                "field_hits": hits,
                "endpoint_hits": ep_hits,
            }
        for pat, count in ep_hits.items():
            results["api_endpoint_hits"][pat] = results["api_endpoint_hits"].get(pat, 0) + count
    # Keep report compact by listing missing-from-code terms too.
    results["fields_not_referenced_in_scanned_files"] = [k for k, v in results["field_hit_counts"].items() if v == 0]
    return results


def node_check(path: Path) -> Dict[str, Any]:
    import subprocess
    if not path.exists():
        return {"exists": False, "ok": False, "returncode": None, "stderr_tail": "missing"}
    try:
        cp = subprocess.run(["node", "--check", str(path)], cwd=str(path.parent), text=True, capture_output=True, timeout=20)
        return {"exists": True, "ok": cp.returncode == 0, "returncode": cp.returncode, "stderr_tail": cp.stderr[-2000:]}
    except Exception as e:
        return {"exists": True, "ok": False, "returncode": None, "stderr_tail": f"{type(e).__name__}: {e}"}


def make_report(data: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Identity Vault Patch 225A Operational Profile Schema Alignment Scan")
    lines.append("")
    lines.append(f"Timestamp: `{data['timestamp']}`")
    lines.append(f"Verdict: **{data['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    for item in data["boundary"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Blueprint Source")
    lines.append("- Source: Self-Hosted Identity Vault design manual, Operational Identity Profiles section.")
    lines.append(f"- required user profile fields: `{len(USER_PROFILE_FIELDS)}`")
    lines.append(f"- required agent profile fields: `{len(AGENT_PROFILE_FIELDS)}`")
    lines.append("- This scan uses the manual's user/agent operational identity structures as the comparison baseline.")
    lines.append("")
    lines.append("## Roots")
    for k, v in data["roots"].items():
        lines.append(f"- {k}: `{v}`")
    lines.append("")
    lines.append("## Contract Baseline")
    cb = data["contract_baseline"]
    for k, v in cb.items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Canonical Database Read-Only Summary")
    db = data["canonical_db"]
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
    lines.append("## Live Schema Alignment")
    for key in ["agent_alignment", "user_alignment"]:
        a = data[key]
        lines.append(f"### `{a['table']}`")
        lines.append(f"- columns: `{', '.join(a['columns'])}`")
        lines.append(f"- exact blueprint fields present: `{a['exact_required_fields_present_count']}/{a['required_fields_count']}`")
        lines.append(f"- json/profile container present: `{a['json_container_present']}`")
        lines.append(f"- representation strategy ready: `{a['representation_strategy_ready']}`")
        missing = a["missing_required_fields"]
        if missing:
            lines.append("- missing required blueprint fields:")
            for m in missing:
                lines.append(f"  - `{m}`")
        else:
            lines.append("- missing required blueprint fields: none")
        lines.append("")
    lines.append("## Code / API Reference Scan")
    cr = data["code_reference_scan"]
    lines.append(f"- files scanned: `{len(cr['files_scanned'])}`")
    for f in cr["files_scanned"]:
        lines.append(f"  - `{f}`")
    lines.append("- API/table endpoint hits:")
    for k, v in sorted(cr.get("api_endpoint_hits", {}).items()):
        lines.append(f"  - `{k}`: `{v}`")
    not_ref = cr.get("fields_not_referenced_in_scanned_files", [])
    lines.append(f"- blueprint fields not referenced in scanned code/docs: `{len(not_ref)}`")
    if not_ref:
        for t in not_ref[:60]:
            lines.append(f"  - `{t}`")
        if len(not_ref) > 60:
            lines.append(f"  - ... `{len(not_ref) - 60}` more")
    lines.append("")
    lines.append("## JS Syntax Checks")
    for rel, chk in data["syntax_checks"].items():
        lines.append(f"- `{rel}`: **{'PASS' if chk.get('ok') else 'WARN'}** returncode=`{chk.get('returncode')}` exists=`{chk.get('exists')}`")
    lines.append("")
    lines.append("## Safety Checks")
    for k, v in data["safety"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Findings")
    for finding in data["findings"]:
        lines.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    lines.append("")
    lines.append("## Recommended Next Safe Step")
    lines.append(data["next_safe_step"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ts = now_stamp()
    run_dir = REPORT_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    before = {
        "env": safe_stat(IDENTITY_ROOT / ".env"),
        "canonical_db": safe_stat(CANONICAL_DB),
        "legacy_db": safe_stat(LEGACY_DB),
        "identity_contract_draft": safe_stat(CONTRACT_DRAFT),
        "aiweb_identity_contract": safe_stat(AIWEB_CONTRACT),
    }

    contract_ok, contract, contract_err = read_json(CONTRACT_DRAFT)
    aiweb_contract_ok, aiweb_contract, aiweb_contract_err = read_json(AIWEB_CONTRACT)
    db_summary = sqlite_readonly_summary(CANONICAL_DB)
    schemas = db_summary.get("schemas", {}) if db_summary.get("ok") else {}
    agent_schema = schemas.get("agent_profiles", [])
    user_schema = schemas.get("user_profiles", [])

    agent_alignment = alignment_for_table("agent_profiles", agent_schema, AGENT_PROFILE_FIELDS)
    user_alignment = alignment_for_table("user_profiles", user_schema, USER_PROFILE_FIELDS, USER_PROFILE_NESTED_FIELDS)
    code_scan = scan_code_references(IDENTITY_ROOT)

    syntax_targets = ["db.js", "server.js", "cli.js", "schemas.js", "tests/db.canonical.test.js", "tests/server.test.js"]
    syntax_checks = {rel: node_check(IDENTITY_ROOT / rel) for rel in syntax_targets if (IDENTITY_ROOT / rel).exists()}

    after = {
        "env": safe_stat(IDENTITY_ROOT / ".env"),
        "canonical_db": safe_stat(CANONICAL_DB),
        "legacy_db": safe_stat(LEGACY_DB),
        "identity_contract_draft": safe_stat(CONTRACT_DRAFT),
        "aiweb_identity_contract": safe_stat(AIWEB_CONTRACT),
    }

    safety = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before["env"] == after["env"],
        "canonical_db_sha_unchanged": before["canonical_db"].get("sha256") == after["canonical_db"].get("sha256"),
        "legacy_db_sha_unchanged": before["legacy_db"].get("sha256") == after["legacy_db"].get("sha256"),
        "identity_contract_draft_unchanged": before["identity_contract_draft"].get("sha256") == after["identity_contract_draft"].get("sha256"),
        "aiweb_identity_contract_unchanged": before["aiweb_identity_contract"].get("sha256") == after["aiweb_identity_contract"].get("sha256"),
        "database_write_performed": False,
        "agent_identity_activation_performed": False,
        "forge_tool_registry_modified": False,
    }

    findings: List[Dict[str, str]] = []
    if not db_summary.get("ok"):
        findings.append({"level": "FAIL", "code": "IV_CANONICAL_DB_READONLY_FAILED", "message": "Canonical Identity Vault DB could not be opened read-only."})
    if "agent_profiles" not in db_summary.get("tables", []):
        findings.append({"level": "FAIL", "code": "IV_AGENT_PROFILES_TABLE_MISSING", "message": "agent_profiles table is missing from canonical database."})
    if "user_profiles" not in db_summary.get("tables", []):
        findings.append({"level": "FAIL", "code": "IV_USER_PROFILES_TABLE_MISSING", "message": "user_profiles table is missing from canonical database."})

    if not agent_alignment["representation_strategy_ready"]:
        findings.append({"level": "WARN", "code": "IV_AGENT_PROFILE_SCHEMA_THIN", "message": "agent_profiles cannot yet represent the full Agent Operational Identity blueprint as columns or a clear JSON payload container."})
    else:
        findings.append({"level": "INFO", "code": "IV_AGENT_PROFILE_SCHEMA_REPRESENTABLE", "message": "agent_profiles appears capable of representing the manual's Agent Operational Identity blueprint."})

    if not user_alignment["representation_strategy_ready"]:
        findings.append({"level": "WARN", "code": "IV_USER_PROFILE_SCHEMA_THIN", "message": "user_profiles cannot yet represent the full User Operational Identity blueprint as columns or a clear JSON payload container."})
    else:
        findings.append({"level": "INFO", "code": "IV_USER_PROFILE_SCHEMA_REPRESENTABLE", "message": "user_profiles appears capable of representing the manual's User Operational Identity blueprint."})

    if not contract_ok:
        findings.append({"level": "WARN", "code": "IV_DRAFT_CONTRACT_READ_FAILED", "message": f"Identity Vault draft contract could not be read: {contract_err}"})
    if not aiweb_contract_ok:
        findings.append({"level": "WARN", "code": "AIWEB_IDENTITY_CONTRACT_READ_FAILED", "message": f"AI.Web identity_vault contract could not be read: {aiweb_contract_err}"})

    for k, unchanged in safety.items():
        if k.endswith("unchanged") and not unchanged:
            findings.append({"level": "FAIL", "code": "IV_PROTECTED_SNAPSHOT_CHANGED", "message": f"Protected snapshot changed during read-only scan: {k}"})
    if not safety["env_secret_values_read"]:
        findings.append({"level": "INFO", "code": "IV_ENV_NOT_READ", "message": ".env exists locally if present, but this scan did not read secret values."})

    fail = any(f["level"] == "FAIL" for f in findings)
    warn = any(f["level"] == "WARN" for f in findings)
    verdict = "FAIL" if fail else ("WARN" if warn else "PASS")

    next_safe_step = (
        "Create a schema migration plan patch before running the bootstrap handshake. The plan should decide whether Identity Vault should store full operational profiles as JSON payload columns, normalized profile tables, or both. Do not create live agent profiles or activate identities until the schema can represent the manual's profile structure."
        if warn or fail else
        "Schema alignment is ready. Next, create inactive draft agent/user profile seed plan and only then rerun the bootstrap handshake dry-run."
    )

    data: Dict[str, Any] = {
        "timestamp": ts,
        "patch_id": PATCH_ID,
        "verdict": verdict,
        "boundary": [
            "This scan is read-only except for writing reports under Forge memory.",
            "It compares the live Identity Vault SQLite schema to the Self-Hosted Identity Vault operational profile blueprint.",
            "It does not modify Identity Vault code, databases, .env, node_modules, Forge registry, service contracts, RMC memory, or agent identity activation state.",
            "It does not read .env secret values.",
        ],
        "roots": {
            "forge_root": str(FORGE_ROOT),
            "identity_vault_root": str(IDENTITY_ROOT),
            "aiweb_root": str(AIWEB_ROOT),
            "canonical_db": str(CANONICAL_DB),
            "legacy_db_preserved": str(LEGACY_DB),
            "identity_contract_draft": str(CONTRACT_DRAFT),
            "aiweb_identity_contract": str(AIWEB_CONTRACT),
        },
        "contract_baseline": {
            "identity_contract_draft_exists": CONTRACT_DRAFT.exists(),
            "identity_contract_draft_loaded": contract_ok,
            "identity_contract_draft_status": contract.get("status") if contract_ok else None,
            "identity_contract_draft_version": contract.get("version") if contract_ok else None,
            "aiweb_identity_contract_exists": AIWEB_CONTRACT.exists(),
            "aiweb_identity_contract_loaded": aiweb_contract_ok,
            "aiweb_identity_contract_name": aiweb_contract.get("name") if aiweb_contract_ok else None,
        },
        "manual_blueprint_baseline": {
            "user_profile_fields": USER_PROFILE_FIELDS,
            "user_profile_nested_fields": USER_PROFILE_NESTED_FIELDS,
            "agent_profile_fields": AGENT_PROFILE_FIELDS,
        },
        "canonical_db": db_summary,
        "agent_alignment": agent_alignment,
        "user_alignment": user_alignment,
        "code_reference_scan": code_scan,
        "syntax_checks": syntax_checks,
        "safety": safety,
        "findings": findings,
        "next_safe_step": next_safe_step,
    }

    report = make_report(data)
    json_path = run_dir / f"{ts}_identity_vault_patch225a_schema_alignment_scan.json"
    md_path = run_dir / f"{ts}_identity_vault_patch225a_schema_alignment_scan.md"
    latest_json = REPORT_ROOT / "latest_identity_vault_patch225a_schema_alignment_scan.json"
    latest_md = REPORT_ROOT / "latest_identity_vault_patch225a_schema_alignment_scan.md"
    json_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(report, encoding="utf-8")
    latest_json.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    latest_md.write_text(report, encoding="utf-8")

    print("Identity Vault Patch 225A operational profile schema alignment scan complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {verdict}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
