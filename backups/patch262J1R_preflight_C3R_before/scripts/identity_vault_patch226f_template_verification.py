#!/usr/bin/env python3
# identity_vault_patch226f_template_verification.py
# Patch 226F — Identity Vault Template Verification
#
# Purpose:
#   Independently verify repaired Identity Vault user/agent JSON templates after Patch 226E.
#
# Boundary:
#   - Writes reports only under Forge memory.
#   - Does not write Identity Vault templates.
#   - Does not write Identity Vault databases.
#   - Does not create profiles.
#   - Does not activate identities.
#   - Does not read .env secret values.

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from typing import Any, Dict, List, Tuple


FORGE_ROOT = Path("/home/nic/forge")
IDENTITY_ROOT = Path("/home/nic/identity-vault")
USER_TEMPLATE = IDENTITY_ROOT / "templates" / "user-template.json"
AGENT_TEMPLATE = IDENTITY_ROOT / "templates" / "agent-template.json"
ENV_PATH = IDENTITY_ROOT / ".env"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"

MEMORY_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch226f_template_verification_v1"

USER_TEMPLATE_REQUIRED_ROOT = [
    "template_type",
    "target_table",
    "lookup_field",
    "indexed_columns",
    "defaults",
    "profile_schema_version",
    "required_fields",
    "safety_rules",
    "operational_profile_json",
]

AGENT_TEMPLATE_REQUIRED_ROOT = list(USER_TEMPLATE_REQUIRED_ROOT)

USER_OPERATIONAL_REQUIRED = [
    "user_id",
    "canonical_name",
    "version",
    "last_updated",
    "interaction_preferences",
    "meta_rules",
    "project_context",
    "session_state",
    "identity_tags",
    "project_affiliations",
    "legacy_migration_reference",
]

AGENT_OPERATIONAL_REQUIRED = [
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

# Do not flag ordinary safety text like "do not read secrets".
# Only flag concrete secret-access mechanisms, credential names, or token patterns.
FORBIDDEN_PATTERNS = [
    ".env",
    "process.env",
    "DATABASE_URL",
    "PRIVATE_KEY",
    "PUBLIC KEY-----",
    "BEGIN RSA",
    "BEGIN OPENSSH",
    "API_KEY",
    "SECRET_KEY",
    "ACCESS_TOKEN",
    "REFRESH_TOKEN",
    "PASSWORD=",
    "DB_PASSWORD",
    "sk-",
    "xoxb-",
    "ghp_",
    "gho_",
    "ghu_",
    "github_pat_",
    "sqlite://",
    "postgres://",
    "mysql://",
]


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def iso_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_memory_run_dir() -> Tuple[str, Path]:
    stamp = utc_stamp()
    run_dir = MEMORY_ROOT / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    return stamp, run_dir


def file_sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha16(path: Path) -> str | None:
    s = file_sha256(path)
    return s[:16] if s else None


def stat_metadata(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    st = path.stat()
    return {
        "exists": True,
        "size": st.st_size,
        "mtime_ns": st.st_mtime_ns,
        "mode": oct(st.st_mode & 0o777),
    }


def read_json(path: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "json_ok": False,
        "error": None,
        "data": None,
        "sha16": sha16(path),
    }
    if not path.exists():
        out["error"] = "missing"
        return out
    try:
        out["data"] = json.loads(path.read_text(encoding="utf-8"))
        out["json_ok"] = True
    except Exception as e:
        out["error"] = str(e)
    return out


def node_json_parse(path: Path) -> Dict[str, Any]:
    result = {
        "attempted": True,
        "available": True,
        "ok": False,
        "returncode": None,
        "stdout_tail": "",
        "stderr_tail": "",
    }
    code = (
        "const fs=require('fs');"
        "const p=process.argv[1];"
        "JSON.parse(fs.readFileSync(p,'utf8'));"
        "console.log('NODE_JSON_PARSE_OK '+p);"
    )
    try:
        proc = subprocess.run(
            ["node", "-e", code, str(path)],
            text=True,
            capture_output=True,
            timeout=15,
        )
        result["returncode"] = proc.returncode
        result["ok"] = proc.returncode == 0
        result["stdout_tail"] = (proc.stdout or "")[-1000:]
        result["stderr_tail"] = (proc.stderr or "")[-1000:]
    except FileNotFoundError:
        result["available"] = False
        result["ok"] = False
        result["stderr_tail"] = "node executable not found"
    except Exception as e:
        result["stderr_tail"] = repr(e)
    return result


def missing_keys(mapping: Dict[str, Any], keys: List[str]) -> List[str]:
    return [k for k in keys if k not in mapping]


def scan_forbidden_tokens(obj: Any) -> List[str]:
    text = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    hits: List[str] = []
    for pat in FORBIDDEN_PATTERNS:
        if pat in text:
            hits.append(pat)
    return sorted(set(hits))


def validate_template(kind: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
    data = parsed.get("data") if parsed.get("json_ok") else None
    if not isinstance(data, dict):
        return {
            "ok": False,
            "root_missing": ["<template not parsed as object>"],
            "operational_missing": [],
            "forbidden_token_hits": [],
            "inactive_defaults_ok": False,
            "target_table_ok": False,
            "lookup_field_ok": False,
            "required_fields_list_ok": False,
            "profile_schema_version_ok": False,
            "indexed_columns_present": False,
        }

    if kind == "user":
        required_root = USER_TEMPLATE_REQUIRED_ROOT
        required_op = USER_OPERATIONAL_REQUIRED
        expected_target = "user_profiles"
        expected_lookup = "user_id"
    else:
        required_root = AGENT_TEMPLATE_REQUIRED_ROOT
        required_op = AGENT_OPERATIONAL_REQUIRED
        expected_target = "agent_profiles"
        expected_lookup = "agent_id"

    op = data.get("operational_profile_json")
    if not isinstance(op, dict):
        op = {}

    defaults = data.get("defaults") if isinstance(data.get("defaults"), dict) else {}
    required_fields = data.get("required_fields")

    root_missing = missing_keys(data, required_root)
    operational_missing = missing_keys(op, required_op)

    inactive_defaults_ok = (
        defaults.get("is_active") == 0
        and defaults.get("activation_state") == "inactive_draft"
        and str(defaults.get("version", "")).startswith("1.0.0")
    )

    target_table_ok = data.get("target_table") == expected_target
    lookup_field_ok = data.get("lookup_field") == expected_lookup
    required_fields_list_ok = isinstance(required_fields, list) and set(required_op).issubset(set(required_fields))
    profile_schema_version_ok = isinstance(data.get("profile_schema_version"), str) and bool(data.get("profile_schema_version"))
    indexed_columns_present = isinstance(data.get("indexed_columns"), list) and expected_lookup in data.get("indexed_columns", [])

    forbidden_hits = scan_forbidden_tokens(data)

    ok = (
        parsed.get("json_ok") is True
        and not root_missing
        and not operational_missing
        and not forbidden_hits
        and inactive_defaults_ok
        and target_table_ok
        and lookup_field_ok
        and required_fields_list_ok
        and profile_schema_version_ok
        and indexed_columns_present
    )

    return {
        "ok": ok,
        "root_missing": root_missing,
        "operational_missing": operational_missing,
        "forbidden_token_hits": forbidden_hits,
        "inactive_defaults_ok": inactive_defaults_ok,
        "target_table_ok": target_table_ok,
        "lookup_field_ok": lookup_field_ok,
        "required_fields_list_ok": required_fields_list_ok,
        "profile_schema_version_ok": profile_schema_version_ok,
        "indexed_columns_present": indexed_columns_present,
    }


def read_sqlite_readonly(path: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "opened_readonly": False,
        "ok": False,
        "tables": [],
        "rows": {},
        "error": None,
    }
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
                count = cur.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                out["rows"][table] = count
            except Exception as e:
                out["rows"][table] = f"ERROR: {e}"
        conn.close()
        out["ok"] = True
    except Exception as e:
        out["error"] = str(e)
    return out


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(path: Path, report: Dict[str, Any]) -> None:
    user = report["templates"]["user"]
    agent = report["templates"]["agent"]
    safety = report["safety"]
    canonical = report["databases"]["canonical"]
    legacy = report["databases"]["legacy"]

    lines = []
    lines.append("# Identity Vault Patch 226F Template Verification")
    lines.append("")
    lines.append(f"Timestamp: `{report['timestamp']}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This patch independently verifies the repaired Identity Vault templates after Patch 226E.")
    lines.append("- It writes reports only under Forge memory.")
    lines.append("- It does not overwrite templates, write databases, create profiles, activate identities, read `.env` secret values, modify Forge registry, or write RMC memory.")
    lines.append("")
    lines.append("## Template Verification")
    for label, item in [("user", user), ("agent", agent)]:
        parsed = item["parsed"]
        validation = item["validation"]
        node = item["node_parse"]
        lines.append(f"- `{label}` path: `{parsed['path']}`")
        lines.append(f"  - python json_ok: `{parsed['json_ok']}` sha16=`{parsed['sha16']}`")
        lines.append(f"  - node json parse ok: `{node['ok']}` available=`{node['available']}` returncode=`{node['returncode']}`")
        lines.append(f"  - required root missing: `{validation['root_missing']}`")
        lines.append(f"  - operational missing: `{validation['operational_missing']}`")
        lines.append(f"  - forbidden token hits: `{validation['forbidden_token_hits']}`")
        lines.append(f"  - inactive defaults ok: `{validation['inactive_defaults_ok']}`")
        lines.append(f"  - target table ok: `{validation['target_table_ok']}`")
        lines.append(f"  - lookup field ok: `{validation['lookup_field_ok']}`")
        lines.append(f"  - required fields list ok: `{validation['required_fields_list_ok']}`")
        lines.append(f"  - profile schema version ok: `{validation['profile_schema_version_ok']}`")
        lines.append(f"  - indexed columns present: `{validation['indexed_columns_present']}`")
    lines.append("")
    lines.append("## Database Read-Only Summary")
    lines.append(f"- canonical: path=`{canonical['path']}` ok=`{canonical['ok']}` opened_readonly=`{canonical['opened_readonly']}` rows=`{canonical.get('rows')}`")
    lines.append(f"- legacy: path=`{legacy['path']}` ok=`{legacy['ok']}` opened_readonly=`{legacy['opened_readonly']}` rows=`{legacy.get('rows')}`")
    lines.append("")
    lines.append("## Safety Checks")
    for k, v in safety.items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Findings")
    for finding in report["findings"]:
        lines.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    lines.append("")
    lines.append("## Next Safe Step")
    if report["verdict"] == "PASS":
        lines.append("Proceed to Patch 227 to write inactive draft Identity Vault profiles. Do not activate identities.")
    else:
        lines.append("Do not write inactive draft profiles yet. Fix the listed template or safety blockers first.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    stamp, run_dir = ensure_memory_run_dir()

    before = {
        "env_stat": stat_metadata(ENV_PATH),
        "canonical_sha": file_sha256(CANONICAL_DB),
        "legacy_sha": file_sha256(LEGACY_DB),
        "user_template_sha": file_sha256(USER_TEMPLATE),
        "agent_template_sha": file_sha256(AGENT_TEMPLATE),
        "tool_registry_sha": file_sha256(FORGE_ROOT / "config" / "tool_registry.json"),
    }

    user_parsed = read_json(USER_TEMPLATE)
    agent_parsed = read_json(AGENT_TEMPLATE)

    user_validation = validate_template("user", user_parsed)
    agent_validation = validate_template("agent", agent_parsed)

    user_node = node_json_parse(USER_TEMPLATE)
    agent_node = node_json_parse(AGENT_TEMPLATE)

    canonical = read_sqlite_readonly(CANONICAL_DB)
    legacy = read_sqlite_readonly(LEGACY_DB)

    after = {
        "env_stat": stat_metadata(ENV_PATH),
        "canonical_sha": file_sha256(CANONICAL_DB),
        "legacy_sha": file_sha256(LEGACY_DB),
        "user_template_sha": file_sha256(USER_TEMPLATE),
        "agent_template_sha": file_sha256(AGENT_TEMPLATE),
        "tool_registry_sha": file_sha256(FORGE_ROOT / "config" / "tool_registry.json"),
    }

    canonical_rows_before_after_ok = True
    legacy_rows_before_after_ok = True
    # This verifier does not snapshot row counts before/after because it opens DBs read-only once.
    # SHA checks prove no DB file content changed during this run.

    safety = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before["env_stat"] == after["env_stat"],
        "canonical_db_sha_unchanged": before["canonical_sha"] == after["canonical_sha"],
        "legacy_db_sha_unchanged": before["legacy_sha"] == after["legacy_sha"],
        "user_template_sha_unchanged_during_verify": before["user_template_sha"] == after["user_template_sha"],
        "agent_template_sha_unchanged_during_verify": before["agent_template_sha"] == after["agent_template_sha"],
        "tool_registry_sha_unchanged": before["tool_registry_sha"] == after["tool_registry_sha"],
        "identity_vault_database_write_performed": False,
        "identity_vault_template_write_performed": False,
        "profiles_created": False,
        "agent_identity_activation_performed": False,
        "rmc_memory_write_performed": False,
        "forge_tool_registry_modified": False,
    }

    findings: List[Dict[str, str]] = []
    if user_validation["ok"] and agent_validation["ok"]:
        findings.append({"level": "INFO", "code": "IV_TEMPLATES_BLUEPRINT_VALID", "message": "Both repaired Identity Vault templates satisfy required operational identity structure."})
    else:
        findings.append({"level": "FAIL", "code": "IV_TEMPLATE_BLUEPRINT_VALIDATION_FAILED", "message": "One or more templates are missing required fields or contain forbidden tokens."})

    if user_node["ok"] and agent_node["ok"]:
        findings.append({"level": "INFO", "code": "IV_NODE_JSON_PARSE_OK", "message": "Both templates parse successfully through Node JSON.parse."})
    else:
        findings.append({"level": "FAIL", "code": "IV_NODE_JSON_PARSE_FAILED", "message": "One or more templates failed Node JSON.parse."})

    if all(safety.values()):
        findings.append({"level": "INFO", "code": "IV_NO_MUTATION_CONFIRMED", "message": "No database, template, .env, RMC, profile, activation, or registry mutation occurred during verification."})
    else:
        findings.append({"level": "FAIL", "code": "IV_NO_MUTATION_CHECK_FAILED", "message": "One or more no-mutation checks failed."})

    if canonical.get("ok") and canonical.get("opened_readonly") and legacy.get("ok") and legacy.get("opened_readonly"):
        findings.append({"level": "INFO", "code": "IV_DATABASES_READONLY_OK", "message": "Canonical and legacy Identity Vault databases opened read-only for verification."})
    else:
        findings.append({"level": "FAIL", "code": "IV_DATABASE_READONLY_CHECK_FAILED", "message": "One or more Identity Vault databases failed read-only verification."})

    pass_conditions = [
        user_parsed["json_ok"],
        agent_parsed["json_ok"],
        user_validation["ok"],
        agent_validation["ok"],
        user_node["ok"],
        agent_node["ok"],
        canonical.get("ok") is True,
        legacy.get("ok") is True,
        all(safety.values()),
    ]

    verdict = "PASS" if all(pass_conditions) else "FAIL"

    # Avoid embedding full template data in the report JSON; this is a verification result.
    report = {
        "timestamp": stamp,
        "generated_at_utc": iso_utc(),
        "verdict": verdict,
        "boundary": "verify repaired templates only; write reports only; no DB/template/profile/activation/RMC mutations",
        "templates": {
            "user": {
                "parsed": {k: v for k, v in user_parsed.items() if k != "data"},
                "validation": user_validation,
                "node_parse": user_node,
            },
            "agent": {
                "parsed": {k: v for k, v in agent_parsed.items() if k != "data"},
                "validation": agent_validation,
                "node_parse": agent_node,
            },
        },
        "databases": {
            "canonical": canonical,
            "legacy": legacy,
        },
        "safety": safety,
        "findings": findings,
    }

    json_path = run_dir / f"{stamp}_identity_vault_patch226f_template_verification.json"
    md_path = run_dir / f"{stamp}_identity_vault_patch226f_template_verification.md"
    latest_json = MEMORY_ROOT / "latest_identity_vault_patch226f_template_verification.json"
    latest_md = MEMORY_ROOT / "latest_identity_vault_patch226f_template_verification.md"

    write_json(json_path, report)
    write_markdown(md_path, report)
    write_json(latest_json, report)
    write_markdown(latest_md, report)

    print("Identity Vault Patch 226F template verification complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
