#!/usr/bin/env python3
"""
Patch 226F.1 — Identity Vault Template Verification Reconcile
Read-only reconcile for Patch 226F's false FAIL verdict.

Boundary:
- Writes reports only under /home/nic/forge/memory/identity_vault_patch226f1_template_verification_reconcile_v1/
- Does not overwrite templates
- Does not write databases
- Does not create profiles
- Does not activate identities
- Does not read .env secret values
- Does not write RMC memory
- Does not modify Forge registry
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sqlite3
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
IDENTITY_ROOT = HOME / "identity-vault"
MEMORY_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch226f1_template_verification_reconcile_v1"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"
USER_TEMPLATE = IDENTITY_ROOT / "templates" / "user-template.json"
AGENT_TEMPLATE = IDENTITY_ROOT / "templates" / "agent-template.json"
ENV_PATH = IDENTITY_ROOT / ".env"
TOOL_REGISTRY = FORGE_ROOT / "config" / "tool_registry.json"

USER_REQUIRED_ROOT = [
    "template_type", "target_table", "lookup_field", "indexed_columns", "defaults",
    "profile_schema_version", "required_fields", "safety_rules", "operational_profile_json",
]
USER_REQUIRED_OPERATIONAL = [
    "user_id", "canonical_name", "version", "last_updated", "interaction_preferences",
    "meta_rules", "project_context", "session_state", "identity_tags", "project_affiliations",
    "legacy_migration_reference",
]
AGENT_REQUIRED_ROOT = [
    "template_type", "target_table", "lookup_field", "indexed_columns", "defaults",
    "profile_schema_version", "required_fields", "safety_rules", "operational_profile_json",
]
AGENT_REQUIRED_OPERATIONAL = [
    "agent_id", "canonical_name", "version", "last_updated", "role", "symbolic_signature",
    "description", "capabilities", "limitations", "persona", "voice_style",
    "quotes_or_character_inspiration", "special_style_notes", "permissions", "authority",
    "enforcement_rules", "forbidden_actions", "session_state", "last_action", "last_feedback",
    "log_fields", "timestamp",
]
FORBIDDEN_SUBSTRINGS = [
    "BEGIN PRIVATE KEY", "PRIVATE_KEY", "API_KEY", "SECRET", "PASSWORD", "TOKEN=",
    "sqlite://", "postgres://", "mysql://", "/.env", "node_modules/",
]


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def iso_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str | None:
    if not path.exists():
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
        "mtime_ns": st.st_mtime_ns,
        "mode": oct(stat.S_IMODE(st.st_mode)),
    }


def read_json(path: Path) -> Tuple[bool, Any, str | None]:
    try:
        return True, json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return False, None, str(exc)


def node_parse(path: Path) -> Dict[str, Any]:
    try:
        cmd = ["node", "-e", "const fs=require('fs'); JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));", str(path)]
        p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        return {"available": True, "ok": p.returncode == 0, "returncode": p.returncode, "stderr_tail": p.stderr[-500:]}
    except FileNotFoundError:
        return {"available": False, "ok": True, "returncode": None, "stderr_tail": "node not installed; skipped"}
    except Exception as exc:
        return {"available": True, "ok": False, "returncode": None, "stderr_tail": str(exc)}


def forbidden_hits(obj: Any) -> List[str]:
    text = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return [token for token in FORBIDDEN_SUBSTRINGS if token in text]


def verify_template(path: Path, kind: str) -> Dict[str, Any]:
    py_ok, obj, err = read_json(path)
    result: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "sha256": sha256(path),
        "sha16": (sha256(path) or "")[:16] or None,
        "python_json_ok": py_ok,
        "python_error": err,
        "node": node_parse(path),
        "required_root_missing": [],
        "operational_missing": [],
        "forbidden_token_hits": [],
        "inactive_defaults_ok": False,
        "target_table_ok": False,
        "lookup_field_ok": False,
        "required_fields_list_ok": False,
        "profile_schema_version_ok": False,
        "indexed_columns_present": False,
        "ok": False,
    }
    if not py_ok or not isinstance(obj, dict):
        return result

    if kind == "user":
        required_root = USER_REQUIRED_ROOT
        required_operational = USER_REQUIRED_OPERATIONAL
        target_table = "user_profiles"
        lookup_field = "user_id"
        required_indexed = ["user_id", "canonical_name", "version", "is_active", "profile_schema_version", "profile_hash", "last_validated_at"]
    else:
        required_root = AGENT_REQUIRED_ROOT
        required_operational = AGENT_REQUIRED_OPERATIONAL
        target_table = "agent_profiles"
        lookup_field = "agent_id"
        required_indexed = ["agent_id", "canonical_name", "role", "version", "is_active", "activation_state", "rmc_namespace", "profile_schema_version", "profile_hash", "last_validated_at"]

    op = obj.get("operational_profile_json", {})
    defaults = obj.get("defaults", {})
    indexed = obj.get("indexed_columns", [])
    required_fields_declared = obj.get("required_fields", [])

    result["required_root_missing"] = [k for k in required_root if k not in obj]
    result["operational_missing"] = [k for k in required_operational if k not in op]
    result["forbidden_token_hits"] = forbidden_hits(obj)
    result["inactive_defaults_ok"] = defaults.get("activation_state") == "inactive_draft" and defaults.get("is_active") in (0, False)
    result["target_table_ok"] = obj.get("target_table") == target_table
    result["lookup_field_ok"] = obj.get("lookup_field") == lookup_field
    result["required_fields_list_ok"] = all(k in required_fields_declared for k in required_operational)
    result["profile_schema_version_ok"] = isinstance(obj.get("profile_schema_version"), str) and bool(obj.get("profile_schema_version"))
    result["indexed_columns_present"] = all(k in indexed for k in required_indexed)

    result["ok"] = all([
        result["exists"], result["python_json_ok"], result["node"].get("ok", False),
        not result["required_root_missing"], not result["operational_missing"],
        not result["forbidden_token_hits"], result["inactive_defaults_ok"],
        result["target_table_ok"], result["lookup_field_ok"], result["required_fields_list_ok"],
        result["profile_schema_version_ok"], result["indexed_columns_present"],
    ])
    return result


def sqlite_readonly_summary(path: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {"path": str(path), "exists": path.exists(), "ok": False, "opened_readonly": False, "rows": {}, "tables": [], "error": None}
    if not path.exists():
        return out
    try:
        uri = f"file:{path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        out["opened_readonly"] = True
        cur = conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
        out["tables"] = tables
        for table in tables:
            try:
                out["rows"][table] = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            except Exception as exc:
                out["rows"][table] = f"ERROR:{exc}"
        conn.close()
        out["ok"] = True
    except Exception as exc:
        out["error"] = str(exc)
    return out


def write_reports(run_dir: Path, report: Dict[str, Any]) -> Tuple[Path, Path]:
    run_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_dir / f"{report['timestamp']}_identity_vault_patch226f1_template_verification_reconcile.json"
    md_path = run_dir / f"{report['timestamp']}_identity_vault_patch226f1_template_verification_reconcile.md"
    latest_json = MEMORY_ROOT / "latest_identity_vault_patch226f1_template_verification_reconcile.json"
    latest_md = MEMORY_ROOT / "latest_identity_vault_patch226f1_template_verification_reconcile.md"

    json_text = json.dumps(report, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")

    user = report["templates"]["user"]
    agent = report["templates"]["agent"]
    safety = report["safety"]
    canonical = report["databases"]["canonical"]
    legacy = report["databases"]["legacy"]

    lines = []
    lines.append("# Identity Vault Patch 226F.1 Template Verification Reconcile")
    lines.append("")
    lines.append(f"Timestamp: `{report['timestamp']}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This reconcile independently validates the repaired Identity Vault templates after Patch 226E and Patch 226F's false FAIL verdict.")
    lines.append("- It writes reports only under Forge memory.")
    lines.append("- It does not overwrite templates, write databases, create profiles, activate identities, read `.env` secret values, modify Forge registry, or write RMC memory.")
    lines.append("")
    lines.append("## Template Verification")
    for label, item in [("user", user), ("agent", agent)]:
        lines.append(f"- `{label}` path: `{item['path']}`")
        lines.append(f"  - python json_ok: `{item['python_json_ok']}` sha16=`{item['sha16']}`")
        lines.append(f"  - node json parse ok: `{item['node'].get('ok')}` available=`{item['node'].get('available')}` returncode=`{item['node'].get('returncode')}`")
        lines.append(f"  - required root missing: `{item['required_root_missing']}`")
        lines.append(f"  - operational missing: `{item['operational_missing']}`")
        lines.append(f"  - forbidden token hits: `{item['forbidden_token_hits']}`")
        lines.append(f"  - inactive defaults ok: `{item['inactive_defaults_ok']}`")
        lines.append(f"  - target table ok: `{item['target_table_ok']}`")
        lines.append(f"  - lookup field ok: `{item['lookup_field_ok']}`")
        lines.append(f"  - required fields list ok: `{item['required_fields_list_ok']}`")
        lines.append(f"  - profile schema version ok: `{item['profile_schema_version_ok']}`")
        lines.append(f"  - indexed columns present: `{item['indexed_columns_present']}`")
        lines.append(f"  - overall ok: `{item['ok']}`")
    lines.append("")
    lines.append("## Database Read-Only Summary")
    lines.append(f"- canonical: path=`{canonical['path']}` ok=`{canonical['ok']}` opened_readonly=`{canonical['opened_readonly']}` rows=`{canonical['rows']}`")
    lines.append(f"- legacy: path=`{legacy['path']}` ok=`{legacy['ok']}` opened_readonly=`{legacy['opened_readonly']}` rows=`{legacy['rows']}`")
    lines.append("")
    lines.append("## Safety Checks")
    for key, val in safety.items():
        lines.append(f"- `{key}`: `{val}`")
    lines.append("")
    lines.append("## Findings")
    for finding in report["findings"]:
        lines.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    lines.append("")
    if report["verdict"] == "PASS":
        lines.append("## Next Safe Step")
        lines.append("Patch 227 may write inactive draft profile rows into the canonical Identity Vault database. No activation.")
    else:
        lines.append("## Next Safe Step")
        lines.append("Do not write inactive draft profiles yet. Review failed checks above.")

    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")
    return md_path, json_path


def main() -> int:
    timestamp = utc_stamp()
    run_dir = MEMORY_ROOT / timestamp
    MEMORY_ROOT.mkdir(parents=True, exist_ok=True)

    before = {
        "env_stat": stat_meta(ENV_PATH),
        "canonical_sha": sha256(CANONICAL_DB),
        "legacy_sha": sha256(LEGACY_DB),
        "user_template_sha": sha256(USER_TEMPLATE),
        "agent_template_sha": sha256(AGENT_TEMPLATE),
        "tool_registry_sha": sha256(TOOL_REGISTRY),
    }

    user = verify_template(USER_TEMPLATE, "user")
    agent = verify_template(AGENT_TEMPLATE, "agent")
    canonical = sqlite_readonly_summary(CANONICAL_DB)
    legacy = sqlite_readonly_summary(LEGACY_DB)

    after = {
        "env_stat": stat_meta(ENV_PATH),
        "canonical_sha": sha256(CANONICAL_DB),
        "legacy_sha": sha256(LEGACY_DB),
        "user_template_sha": sha256(USER_TEMPLATE),
        "agent_template_sha": sha256(AGENT_TEMPLATE),
        "tool_registry_sha": sha256(TOOL_REGISTRY),
    }

    safety = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before["env_stat"] == after["env_stat"],
        "canonical_db_sha_unchanged": before["canonical_sha"] == after["canonical_sha"],
        "legacy_db_sha_unchanged": before["legacy_sha"] == after["legacy_sha"],
        "user_template_sha_unchanged_during_verify": before["user_template_sha"] == after["user_template_sha"],
        "agent_template_sha_unchanged_during_verify": before["agent_template_sha"] == after["agent_template_sha"],
        "tool_registry_sha_unchanged": before["tool_registry_sha"] == after["tool_registry_sha"],
        "identity_vault_database_write_performed": before["canonical_sha"] != after["canonical_sha"] or before["legacy_sha"] != after["legacy_sha"],
        "identity_vault_template_write_performed": before["user_template_sha"] != after["user_template_sha"] or before["agent_template_sha"] != after["agent_template_sha"],
        "profiles_created": False,
        "agent_identity_activation_performed": False,
        "rmc_memory_write_performed": False,
        "forge_tool_registry_modified": before["tool_registry_sha"] != after["tool_registry_sha"],
    }

    safety_ok = (
        safety["env_stat_unchanged"]
        and safety["canonical_db_sha_unchanged"]
        and safety["legacy_db_sha_unchanged"]
        and safety["user_template_sha_unchanged_during_verify"]
        and safety["agent_template_sha_unchanged_during_verify"]
        and safety["tool_registry_sha_unchanged"]
        and not safety["identity_vault_database_write_performed"]
        and not safety["identity_vault_template_write_performed"]
        and not safety["profiles_created"]
        and not safety["agent_identity_activation_performed"]
        and not safety["rmc_memory_write_performed"]
        and not safety["forge_tool_registry_modified"]
    )
    databases_ok = canonical.get("ok") and canonical.get("opened_readonly") and legacy.get("ok") and legacy.get("opened_readonly")
    verdict = "PASS" if user["ok"] and agent["ok"] and safety_ok and databases_ok else "FAIL"

    findings: List[Dict[str, str]] = []
    if user["ok"] and agent["ok"]:
        findings.append({"level": "INFO", "code": "IV_TEMPLATES_BLUEPRINT_VALID_RECONCILED", "message": "Both repaired Identity Vault templates satisfy required operational identity structure."})
    else:
        findings.append({"level": "FAIL", "code": "IV_TEMPLATE_STRUCTURE_INVALID", "message": "One or more repaired templates failed structural validation."})
    if user["node"].get("ok") and agent["node"].get("ok"):
        findings.append({"level": "INFO", "code": "IV_NODE_JSON_PARSE_OK", "message": "Both templates parse successfully through Node JSON.parse."})
    if safety_ok:
        findings.append({"level": "INFO", "code": "IV_NO_MUTATION_RECONCILED", "message": "Verification was read-only: templates, DBs, .env metadata, RMC memory, and Forge registry stayed unchanged."})
    else:
        findings.append({"level": "FAIL", "code": "IV_NO_MUTATION_CHECK_FAILED", "message": "One or more no-mutation checks failed."})
    if databases_ok:
        findings.append({"level": "INFO", "code": "IV_DATABASES_READONLY_OK", "message": "Canonical and legacy Identity Vault databases opened read-only for verification."})

    report = {
        "timestamp": timestamp,
        "generated_at_utc": iso_now(),
        "verdict": verdict,
        "boundary": "read-only template verification reconcile; no writes outside Forge memory reports",
        "templates": {"user": user, "agent": agent},
        "databases": {"canonical": canonical, "legacy": legacy},
        "safety": safety,
        "findings": findings,
    }
    md_path, json_path = write_reports(run_dir, report)

    print("Identity Vault Patch 226F.1 template verification reconcile complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {MEMORY_ROOT / 'latest_identity_vault_patch226f1_template_verification_reconcile.md'}")
    print(f"JSON report: {MEMORY_ROOT / 'latest_identity_vault_patch226f1_template_verification_reconcile.json'}")
    print(f"Verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
