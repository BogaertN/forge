#!/usr/bin/env python3
"""
Patch 226E — Identity Vault Template Apply

Backs up and replaces malformed Identity Vault JSON templates with valid
operational identity templates. This patch only writes the two template files
under /home/nic/identity-vault/templates after backup. It does not write any
Identity Vault databases, create profiles, activate identities, read .env
secret values, modify Forge registry, or write RMC memory.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import shutil
import sqlite3
import stat
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
IDENTITY_ROOT = HOME / "identity-vault"
TEMPLATE_ROOT = IDENTITY_ROOT / "templates"
USER_TEMPLATE = TEMPLATE_ROOT / "user-template.json"
AGENT_TEMPLATE = TEMPLATE_ROOT / "agent-template.json"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"
ENV_PATH = IDENTITY_ROOT / ".env"
TOOL_REGISTRY = FORGE_ROOT / "config" / "tool_registry.json"

MEMORY_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch226e_template_apply_v1"
BACKUP_ROOT_BASE = FORGE_ROOT / "backups" / "patch226e_identity_vault_templates_before"

USER_REQUIRED = [
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

AGENT_REQUIRED = [
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


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_UTC")


def iso_now() -> str:
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_metadata(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    st = path.stat()
    return {
        "exists": True,
        "size": st.st_size,
        "mtime_ns": st.st_mtime_ns,
        "mode": oct(stat.S_IMODE(st.st_mode)),
    }


def json_status(path: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {"path": str(path), "exists": path.exists(), "json_ok": False}
    if not path.exists():
        return result
    try:
        result["data"] = json.loads(path.read_text(encoding="utf-8"))
        result["json_ok"] = True
    except Exception as exc:  # noqa: BLE001 - report only
        result["error"] = str(exc)
    return result


def readonly_table_counts(db_path: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {"path": str(db_path), "exists": db_path.exists(), "ok": False, "opened_readonly": False, "rows": {}}
    if not db_path.exists():
        return out
    try:
        uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        out["opened_readonly"] = True
        cur = conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
        for table in tables:
            try:
                cur.execute(f'SELECT COUNT(*) FROM "{table}"')
                out["rows"][table] = cur.fetchone()[0]
            except Exception as exc:  # noqa: BLE001
                out["rows"][table] = f"ERR:{exc}"
        conn.close()
        out["ok"] = True
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)
    return out


def user_template(now: str) -> Dict[str, Any]:
    return {
        "template_type": "user_operational_identity_template",
        "target_table": "user_profiles",
        "lookup_field": "user_id",
        "profile_schema_version": "1.0.0-blueprint",
        "defaults": {
            "activation_state": "inactive_draft",
            "is_active": 0,
            "version": "1.0.0-blueprint-draft",
        },
        "indexed_columns": [
            "user_id",
            "canonical_name",
            "version",
            "is_active",
            "created_at",
            "updated_at",
            "profile_schema_version",
            "profile_hash",
            "last_validated_at",
        ],
        "required_fields": USER_REQUIRED,
        "operational_profile_json": {
            "user_id": "{{user_id}}",
            "canonical_name": "{{canonical_name}}",
            "spirit_name": None,
            "version": "1.0.0-blueprint-draft",
            "last_updated": now,
            "identity_tags": [],
            "project_affiliations": [],
            "interaction_preferences": {
                "step_by_step": True,
                "beginner_friendly": True,
                "plain_language": True,
                "pushback": True,
                "confirmation_required": True,
                "no_boxes": True,
            },
            "meta_rules": {
                "require_context_carryover": True,
                "require_honest_pushback": True,
                "forbidden_actions": [
                    "activate agent identities without approval",
                    "write to RMC memory without approval",
                    "read secret values",
                    "package secrets or dependency folders",
                ],
            },
            "project_context": {
                "current_project": "AI.Web bootstrap integration",
                "phase": "Identity Vault normalization",
                "subsystems": ["Forge", "RMC", "Identity Vault", "ProtoForge2", "EchoForge"],
                "goals": [],
            },
            "session_state": {
                "phase": "draft_inactive",
                "waiting_for": "manual review",
                "last_feedback": None,
                "last_action": None,
                "timestamp": now,
            },
            "legacy_migration_reference": {
                "source_database": None,
                "source_id": None,
                "status": "none_or_preserve_as_reference_only",
            },
        },
        "safety_rules": [
            "Template must not contain credential values.",
            "Template must not activate a profile.",
            "Template must not contain database connection strings.",
        ],
    }


def agent_template(now: str) -> Dict[str, Any]:
    return {
        "template_type": "agent_operational_identity_template",
        "target_table": "agent_profiles",
        "lookup_field": "agent_id",
        "profile_schema_version": "1.0.0-blueprint",
        "defaults": {
            "activation_state": "inactive_draft",
            "is_active": 0,
            "version": "1.0.0-blueprint-draft",
        },
        "indexed_columns": [
            "agent_id",
            "canonical_name",
            "role",
            "version",
            "is_active",
            "activation_state",
            "rmc_namespace",
            "profile_schema_version",
            "profile_hash",
            "last_validated_at",
        ],
        "required_fields": AGENT_REQUIRED,
        "operational_profile_json": {
            "agent_id": "{{agent_id}}",
            "canonical_name": "{{canonical_name}}",
            "version": "1.0.0-blueprint-draft",
            "last_updated": now,
            "role": "{{role}}",
            "description": "",
            "symbolic_signature": [],
            "capabilities": [],
            "limitations": [
                "cannot activate itself",
                "cannot bypass Forge",
                "cannot read secrets",
                "cannot write memory without approval",
            ],
            "persona": "",
            "voice_style": "",
            "quotes_or_character_inspiration": [],
            "special_style_notes": [],
            "permissions": [],
            "authority": [],
            "enforcement_rules": [
                "Forge approval gates control actions",
                "RMC memory writes require explicit approval",
                "Identity remains inactive until approved",
            ],
            "forbidden_actions": [
                "self-activation",
                "secret reading",
                "database writes without approved migration",
                "unapproved tool execution",
                "memory mutation without approval",
            ],
            "session_state": "inactive_draft",
            "last_action": None,
            "last_feedback": None,
            "log_fields": [],
            "timestamp": now,
            "rmc_namespace": "rmc/agents/{{agent_id}}",
        },
        "safety_rules": [
            "Template must not contain credential values.",
            "Template must not activate an agent.",
            "Template must store memory pointers only, not live memory contents.",
        ],
    }


def validate_template(data: Dict[str, Any], required: List[str], kind: str) -> Dict[str, Any]:
    profile = data.get("operational_profile_json", {})
    missing = [k for k in required if k not in profile]
    text = json.dumps(data, sort_keys=True)
    forbidden_tokens = [".env", "DATABASE_URL", "PRIVATE_KEY", "BEGIN RSA", "BEGIN OPENSSH", "sk-"]
    forbidden_hits = [tok for tok in forbidden_tokens if tok in text]
    defaults = data.get("defaults", {})
    inactive_ok = defaults.get("is_active") == 0 and defaults.get("activation_state") == "inactive_draft"
    return {
        "kind": kind,
        "json_ok": True,
        "required_missing": missing,
        "forbidden_token_hits": forbidden_hits,
        "inactive_defaults_ok": inactive_ok,
        "ok": not missing and not forbidden_hits and inactive_ok,
    }


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    ts = utc_stamp()
    now = iso_now()
    run_dir = MEMORY_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    MEMORY_ROOT.mkdir(parents=True, exist_ok=True)
    backup_root = BACKUP_ROOT_BASE / ts
    backup_root.mkdir(parents=True, exist_ok=True)

    before = {
        "env_stat": stat_metadata(ENV_PATH),
        "canonical_db_sha": sha256(CANONICAL_DB),
        "legacy_db_sha": sha256(LEGACY_DB),
        "tool_registry_sha": sha256(TOOL_REGISTRY),
        "user_template_sha": sha256(USER_TEMPLATE),
        "agent_template_sha": sha256(AGENT_TEMPLATE),
        "user_template_json": json_status(USER_TEMPLATE),
        "agent_template_json": json_status(AGENT_TEMPLATE),
    }

    backups: Dict[str, Any] = {}
    for src in (USER_TEMPLATE, AGENT_TEMPLATE):
        if src.exists():
            dest = backup_root / src.name
            shutil.copy2(src, dest)
            backups[str(src)] = str(dest)
        else:
            backups[str(src)] = "MISSING_NOT_COPIED"

    user_data = user_template(now)
    agent_data = agent_template(now)
    user_validation = validate_template(user_data, USER_REQUIRED, "user")
    agent_validation = validate_template(agent_data, AGENT_REQUIRED, "agent")

    wrote_templates = False
    if user_validation["ok"] and agent_validation["ok"]:
        write_json(USER_TEMPLATE, user_data)
        write_json(AGENT_TEMPLATE, agent_data)
        wrote_templates = True

    after = {
        "env_stat": stat_metadata(ENV_PATH),
        "canonical_db_sha": sha256(CANONICAL_DB),
        "legacy_db_sha": sha256(LEGACY_DB),
        "tool_registry_sha": sha256(TOOL_REGISTRY),
        "user_template_sha": sha256(USER_TEMPLATE),
        "agent_template_sha": sha256(AGENT_TEMPLATE),
        "user_template_json": json_status(USER_TEMPLATE),
        "agent_template_json": json_status(AGENT_TEMPLATE),
        "canonical_db": readonly_table_counts(CANONICAL_DB),
        "legacy_db": readonly_table_counts(LEGACY_DB),
    }

    safety = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before["env_stat"] == after["env_stat"],
        "canonical_db_sha_unchanged": before["canonical_db_sha"] == after["canonical_db_sha"],
        "legacy_db_sha_unchanged": before["legacy_db_sha"] == after["legacy_db_sha"],
        "tool_registry_sha_unchanged": before["tool_registry_sha"] == after["tool_registry_sha"],
        "identity_vault_database_write_performed": before["canonical_db_sha"] != after["canonical_db_sha"],
        "profiles_created": False,
        "agent_identity_activation_performed": False,
        "rmc_memory_write_performed": False,
        "forge_tool_registry_modified": before["tool_registry_sha"] != after["tool_registry_sha"],
        "user_template_write_performed": before["user_template_sha"] != after["user_template_sha"],
        "agent_template_write_performed": before["agent_template_sha"] != after["agent_template_sha"],
    }

    final_user_parse_ok = after["user_template_json"].get("json_ok") is True
    final_agent_parse_ok = after["agent_template_json"].get("json_ok") is True
    intended_template_writes_ok = safety["user_template_write_performed"] and safety["agent_template_write_performed"]
    no_forbidden_mutation_ok = (
        safety["env_stat_unchanged"]
        and safety["canonical_db_sha_unchanged"]
        and safety["legacy_db_sha_unchanged"]
        and safety["tool_registry_sha_unchanged"]
        and not safety["identity_vault_database_write_performed"]
        and not safety["profiles_created"]
        and not safety["agent_identity_activation_performed"]
        and not safety["rmc_memory_write_performed"]
        and not safety["forge_tool_registry_modified"]
    )

    verdict = "PASS" if (
        wrote_templates
        and user_validation["ok"]
        and agent_validation["ok"]
        and final_user_parse_ok
        and final_agent_parse_ok
        and intended_template_writes_ok
        and no_forbidden_mutation_ok
    ) else "FAIL"

    findings: List[Tuple[str, str, str]] = []
    if before["user_template_json"].get("json_ok") is False:
        findings.append(("INFO", "IV_USER_TEMPLATE_INVALID_BEFORE", "Existing user template was invalid JSON before apply."))
    if before["agent_template_json"].get("json_ok") is False:
        findings.append(("INFO", "IV_AGENT_TEMPLATE_INVALID_BEFORE", "Existing agent template was invalid JSON before apply."))
    if final_user_parse_ok and final_agent_parse_ok:
        findings.append(("INFO", "IV_REPAIRED_TEMPLATES_JSON_VALID", "Both applied Identity Vault templates parse as valid JSON."))
    if user_validation["ok"] and agent_validation["ok"]:
        findings.append(("INFO", "IV_TEMPLATE_BLUEPRINT_FIELDS_OK", "Both templates include required operational identity fields and inactive defaults."))
    if no_forbidden_mutation_ok:
        findings.append(("INFO", "IV_NO_FORBIDDEN_MUTATION", "DBs, .env metadata, RMC memory, and Forge registry stayed unchanged."))
    if verdict != "PASS":
        findings.append(("FAIL", "IV_TEMPLATE_APPLY_FAILED", "Template apply or verification failed; restore from backup if needed."))

    report = {
        "timestamp": ts,
        "boundary": "write repaired Identity Vault template files only after backup; no DB/profile/activation/RMC writes",
        "verdict": verdict,
        "paths": {
            "user_template": str(USER_TEMPLATE),
            "agent_template": str(AGENT_TEMPLATE),
            "backup_root": str(backup_root),
            "run_dir": str(run_dir),
        },
        "before": {k: v for k, v in before.items() if not str(k).endswith("_json")},
        "source_json_before": {
            "user": {k: v for k, v in before["user_template_json"].items() if k != "data"},
            "agent": {k: v for k, v in before["agent_template_json"].items() if k != "data"},
        },
        "backups": backups,
        "validations": {"user": user_validation, "agent": agent_validation},
        "after": {k: v for k, v in after.items() if not str(k).endswith("_json")},
        "source_json_after": {
            "user": {k: v for k, v in after["user_template_json"].items() if k != "data"},
            "agent": {k: v for k, v in after["agent_template_json"].items() if k != "data"},
        },
        "safety": safety,
        "findings": findings,
    }

    json_path = run_dir / f"{ts}_identity_vault_patch226e_template_apply.json"
    latest_json = MEMORY_ROOT / "latest_identity_vault_patch226e_template_apply.json"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    latest_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    md_lines = [
        "# Identity Vault Patch 226E Template Apply",
        "",
        f"Timestamp: `{ts}`",
        f"Verdict: **{verdict}**",
        "",
        "## Boundary",
        "- This patch backs up and replaces the two malformed Identity Vault template JSON files only.",
        "- It does not write Identity Vault databases, create profiles, activate identities, read `.env` secret values, modify Forge registry, or write RMC memory.",
        "",
        "## Backups",
        f"- backup root: `{backup_root}`",
        f"- user template backup: `{backups.get(str(USER_TEMPLATE))}`",
        f"- agent template backup: `{backups.get(str(AGENT_TEMPLATE))}`",
        "",
        "## Source Template State Before",
        f"- user: json_ok=`{before['user_template_json'].get('json_ok')}` sha16=`{(before['user_template_sha'] or '')[:16]}` error=`{before['user_template_json'].get('error')}`",
        f"- agent: json_ok=`{before['agent_template_json'].get('json_ok')}` sha16=`{(before['agent_template_sha'] or '')[:16]}` error=`{before['agent_template_json'].get('error')}`",
        "",
        "## Applied Template Validation",
        f"- user template json_ok=`{final_user_parse_ok}` sha16=`{(after['user_template_sha'] or '')[:16]}` required_missing=`{user_validation['required_missing']}` forbidden_token_hits=`{user_validation['forbidden_token_hits']}` inactive_defaults_ok=`{user_validation['inactive_defaults_ok']}`",
        f"- agent template json_ok=`{final_agent_parse_ok}` sha16=`{(after['agent_template_sha'] or '')[:16]}` required_missing=`{agent_validation['required_missing']}` forbidden_token_hits=`{agent_validation['forbidden_token_hits']}` inactive_defaults_ok=`{agent_validation['inactive_defaults_ok']}`",
        "",
        "## Database Read-Only Summary",
        f"- canonical: path=`{CANONICAL_DB}` ok=`{after['canonical_db'].get('ok')}` opened_readonly=`{after['canonical_db'].get('opened_readonly')}` rows=`{after['canonical_db'].get('rows')}`",
        f"- legacy: path=`{LEGACY_DB}` ok=`{after['legacy_db'].get('ok')}` opened_readonly=`{after['legacy_db'].get('opened_readonly')}` rows=`{after['legacy_db'].get('rows')}`",
        "",
        "## Safety Checks",
    ]
    for k, v in safety.items():
        md_lines.append(f"- `{k}`: `{v}`")
    md_lines.extend(["", "## Findings"])
    for level, code, message in findings:
        md_lines.append(f"- **{level}** `{code}` — {message}")
    md_lines.extend(["", "## Next Safe Step"])
    if verdict == "PASS":
        md_lines.append("Run Patch 226F as an independent template verification before writing inactive draft profiles.")
    else:
        md_lines.append(f"Review this report. Restore templates from `{backup_root}` if needed before continuing.")
    md_text = "\n".join(md_lines) + "\n"
    md_path = run_dir / f"{ts}_identity_vault_patch226e_template_apply.md"
    latest_md = MEMORY_ROOT / "latest_identity_vault_patch226e_template_apply.md"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")

    print("Identity Vault Patch 226E template apply complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
