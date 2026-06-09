#!/usr/bin/env python3
"""Patch 226D — Identity Vault Template Repair Preview.

Read the current Identity Vault user/agent template files, diagnose JSON errors,
and write repaired JSON template previews under Forge memory only.

No Identity Vault files are modified. No database contents are read beyond hashing
and optional read-only open checks. No .env secret values are read.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sqlite3
import stat
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

FORGE_ROOT = Path("/home/nic/forge")
IDENTITY_ROOT = Path("/home/nic/identity-vault")
USER_TEMPLATE = IDENTITY_ROOT / "templates" / "user-template.json"
AGENT_TEMPLATE = IDENTITY_ROOT / "templates" / "agent-template.json"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"
ENV_PATH = IDENTITY_ROOT / ".env"
OUT_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch226d_template_repair_preview_v1"

AGENT_REQUIRED_FIELDS = [
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

USER_REQUIRED_FIELDS = [
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

FORBIDDEN_TEMPLATE_TOKENS = [
    ".env",
    "SECRET",
    "PASSWORD",
    "PRIVATE_KEY",
    "API_KEY",
    "TOKEN=",
    "DATABASE_URL",
    "BEGIN RSA",
    "BEGIN OPENSSH",
]


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def iso_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_metadata(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    st = path.stat()
    return {
        "exists": True,
        "size": st.st_size,
        "mtime_ns": st.st_mtime_ns,
        "mode": oct(stat.S_IMODE(st.st_mode)),
        "sha256": sha256_file(path) if path.is_file() else None,
    }


def safe_read_text(path: Path) -> Tuple[Optional[str], Optional[str]]:
    if not path.exists():
        return None, "missing"
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8", errors="replace"), "unicode_decode_replaced"
        except Exception as exc:  # pragma: no cover
            return None, repr(exc)
    except Exception as exc:
        return None, repr(exc)


def json_diagnose(path: Path) -> Dict[str, Any]:
    text, read_error = safe_read_text(path)
    info: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "read_error": read_error,
        "json_ok": False,
        "json_error": None,
        "error_line": None,
        "error_column": None,
        "line_context": [],
        "sha256": sha256_file(path),
        "size": path.stat().st_size if path.exists() else None,
    }
    if text is None:
        info["json_error"] = read_error or "unreadable"
        return info
    try:
        parsed = json.loads(text)
        info["json_ok"] = True
        info["parsed_type"] = type(parsed).__name__
        if isinstance(parsed, dict):
            info["top_level_keys"] = sorted(parsed.keys())
        return info
    except json.JSONDecodeError as exc:
        info["json_error"] = exc.msg
        info["error_line"] = exc.lineno
        info["error_column"] = exc.colno
        lines = text.splitlines()
        start = max(1, exc.lineno - 3)
        end = min(len(lines), exc.lineno + 3)
        context = []
        for lineno in range(start, end + 1):
            raw = lines[lineno - 1]
            context.append({
                "line": lineno,
                "text": raw[:240],
                "error_line": lineno == exc.lineno,
            })
        info["line_context"] = context
        return info
    except Exception as exc:
        info["json_error"] = repr(exc)
        return info


def readonly_db_summary(path: Path) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "opened_readonly": False,
        "ok": False,
        "tables": [],
        "row_counts": {},
        "error": None,
        "sha256": sha256_file(path),
    }
    if not path.exists():
        return summary
    try:
        uri = f"file:{path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        summary["opened_readonly"] = True
        cur = conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        summary["tables"] = tables
        for t in tables:
            try:
                cur.execute(f'SELECT COUNT(*) FROM "{t}"')
                summary["row_counts"][t] = cur.fetchone()[0]
            except Exception as exc:
                summary["row_counts"][t] = f"ERROR: {exc}"
        conn.close()
        summary["ok"] = True
    except Exception as exc:
        summary["error"] = repr(exc)
    return summary


def build_user_template_preview(ts_iso: str) -> Dict[str, Any]:
    return {
        "template_type": "user_operational_identity_template",
        "profile_schema_version": "1.0.0-blueprint",
        "target_table": "user_profiles",
        "lookup_field": "user_id",
        "required_fields": USER_REQUIRED_FIELDS,
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
        "defaults": {
            "is_active": 0,
            "activation_state": "inactive_draft",
            "version": "1.0.0-blueprint-draft",
        },
        "operational_profile_json": {
            "user_id": "{{user_id}}",
            "canonical_name": "{{canonical_name}}",
            "version": "1.0.0-blueprint-draft",
            "last_updated": ts_iso,
            "identity_tags": [],
            "interaction_preferences": {
                "step_by_step": True,
                "beginner_friendly": True,
                "plain_language": True,
                "pushback": True,
                "confirmation_required": True,
                "no_boxes": True,
            },
            "meta_rules": {
                "require_honest_pushback": True,
                "require_context_carryover": True,
                "forbidden_actions": [
                    "activate agent identities without approval",
                    "write to RMC memory without approval",
                    "read secret values",
                    "package secrets or dependency folders",
                ],
            },
            "project_context": {
                "current_project": "AI.Web bootstrap integration",
                "subsystems": ["Forge", "RMC", "Identity Vault", "ProtoForge2", "EchoForge"],
                "phase": "Identity Vault normalization",
                "goals": [],
            },
            "session_state": {
                "phase": "draft_inactive",
                "waiting_for": "manual review",
                "last_action": None,
                "last_feedback": None,
                "timestamp": ts_iso,
            },
            "project_affiliations": [],
            "legacy_migration_reference": {
                "status": "none_or_preserve_as_reference_only",
                "source_database": None,
                "source_id": None,
            },
        },
        "safety_rules": [
            "Template must not contain secret values.",
            "Template must not activate a profile.",
            "Template must not contain database connection strings.",
        ],
    }


def build_agent_template_preview(ts_iso: str) -> Dict[str, Any]:
    return {
        "template_type": "agent_operational_identity_template",
        "profile_schema_version": "1.0.0-blueprint",
        "target_table": "agent_profiles",
        "lookup_field": "agent_id",
        "required_fields": AGENT_REQUIRED_FIELDS,
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
        "defaults": {
            "is_active": 0,
            "activation_state": "inactive_draft",
            "version": "1.0.0-blueprint-draft",
        },
        "operational_profile_json": {
            "agent_id": "{{agent_id}}",
            "canonical_name": "{{canonical_name}}",
            "version": "1.0.0-blueprint-draft",
            "last_updated": ts_iso,
            "role": "{{role}}",
            "symbolic_signature": [],
            "description": "",
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
            "timestamp": ts_iso,
            "rmc_namespace": "rmc/agents/{{agent_id}}",
        },
        "safety_rules": [
            "Template must not contain secret values.",
            "Template must not activate an agent.",
            "Template must store memory pointers only, not live memory contents.",
        ],
    }


def validate_template_preview(template: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
    payload = template.get("operational_profile_json", {})
    missing = [k for k in required if k not in payload]
    rendered = json.dumps(template, indent=2, sort_keys=True)
    forbidden_hits = [tok for tok in FORBIDDEN_TEMPLATE_TOKENS if tok in rendered]
    json_roundtrip_ok = False
    error = None
    try:
        json.loads(rendered)
        json_roundtrip_ok = True
    except Exception as exc:
        error = repr(exc)
    return {
        "ok": not missing and not forbidden_hits and json_roundtrip_ok,
        "missing_required_fields": missing,
        "forbidden_token_hits": forbidden_hits,
        "json_roundtrip_ok": json_roundtrip_ok,
        "json_error": error,
        "sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
    }


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_report(path: Path, report: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("# Identity Vault Patch 226D Template Repair Preview")
    lines.append("")
    lines.append(f"Timestamp: `{report['timestamp']}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This patch previews repaired Identity Vault templates only.")
    lines.append("- It writes reports and preview JSON files only under Forge memory.")
    lines.append("- It does not overwrite Identity Vault template files.")
    lines.append("- It does not write Identity Vault databases, create profiles, activate identities, read `.env` secret values, modify Forge registry, or write RMC memory.")
    lines.append("")
    lines.append("## Source Templates")
    for key in ["user_template", "agent_template"]:
        diag = report["source_template_diagnostics"][key]
        lines.append(f"- `{diag['path']}` exists=`{diag['exists']}` json_ok=`{diag['json_ok']}` sha16=`{(diag.get('sha256') or '')[:16]}`")
        if not diag["json_ok"]:
            lines.append(f"  - error: `{diag.get('json_error')}` line=`{diag.get('error_line')}` column=`{diag.get('error_column')}`")
            if diag.get("line_context"):
                lines.append("  - context:")
                for ctx in diag["line_context"]:
                    marker = " <==" if ctx.get("error_line") else ""
                    safe = str(ctx.get("text", "")).replace("`", "'")
                    lines.append(f"    - L{ctx['line']}: `{safe}`{marker}")
    lines.append("")
    lines.append("## Repaired Preview Files")
    lines.append(f"- user preview: `{report['preview_files']['user_template_preview']}`")
    lines.append(f"- agent preview: `{report['preview_files']['agent_template_preview']}`")
    lines.append("")
    lines.append("## Preview Validation")
    uv = report["preview_validation"]["user_template"]
    av = report["preview_validation"]["agent_template"]
    lines.append(f"- user template preview valid: `{uv['ok']}` sha16=`{uv['sha256'][:16]}`")
    lines.append(f"  - missing required fields: `{uv['missing_required_fields']}`")
    lines.append(f"  - forbidden token hits: `{uv['forbidden_token_hits']}`")
    lines.append(f"- agent template preview valid: `{av['ok']}` sha16=`{av['sha256'][:16]}`")
    lines.append(f"  - missing required fields: `{av['missing_required_fields']}`")
    lines.append(f"  - forbidden token hits: `{av['forbidden_token_hits']}`")
    lines.append("")
    lines.append("## Database Read-Only Summary")
    can = report["databases"]["canonical"]
    leg = report["databases"]["legacy"]
    lines.append(f"- canonical: path=`{can['path']}` ok=`{can['ok']}` opened_readonly=`{can['opened_readonly']}` rows=`{can.get('row_counts', {})}`")
    lines.append(f"- legacy: path=`{leg['path']}` ok=`{leg['ok']}` opened_readonly=`{leg['opened_readonly']}` rows=`{leg.get('row_counts', {})}`")
    lines.append("")
    lines.append("## Safety Checks")
    for k, v in report["safety"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Findings")
    for finding in report["findings"]:
        lines.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    lines.append("")
    lines.append("## Next Safe Step")
    if report["verdict"] == "PASS":
        lines.append("Review the preview JSON files. If acceptable, create Patch 226E to back up and apply the repaired template files.")
    else:
        lines.append("Do not apply repaired templates yet. Review failed validation details first.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ts = utc_stamp()
    ts_iso = iso_now()
    run_dir = OUT_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    before = {
        "env": stat_metadata(ENV_PATH),
        "canonical_db_sha": sha256_file(CANONICAL_DB),
        "legacy_db_sha": sha256_file(LEGACY_DB),
        "user_template_sha": sha256_file(USER_TEMPLATE),
        "agent_template_sha": sha256_file(AGENT_TEMPLATE),
    }

    user_diag = json_diagnose(USER_TEMPLATE)
    agent_diag = json_diagnose(AGENT_TEMPLATE)
    user_preview = build_user_template_preview(ts_iso)
    agent_preview = build_agent_template_preview(ts_iso)
    user_validation = validate_template_preview(user_preview, USER_REQUIRED_FIELDS)
    agent_validation = validate_template_preview(agent_preview, AGENT_REQUIRED_FIELDS)

    user_preview_path = run_dir / f"{ts}_user_template_repaired_preview.json"
    agent_preview_path = run_dir / f"{ts}_agent_template_repaired_preview.json"
    write_json(user_preview_path, user_preview)
    write_json(agent_preview_path, agent_preview)

    canonical_summary = readonly_db_summary(CANONICAL_DB)
    legacy_summary = readonly_db_summary(LEGACY_DB)

    after = {
        "env": stat_metadata(ENV_PATH),
        "canonical_db_sha": sha256_file(CANONICAL_DB),
        "legacy_db_sha": sha256_file(LEGACY_DB),
        "user_template_sha": sha256_file(USER_TEMPLATE),
        "agent_template_sha": sha256_file(AGENT_TEMPLATE),
    }

    safety = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before["env"] == after["env"],
        "canonical_db_sha_unchanged": before["canonical_db_sha"] == after["canonical_db_sha"],
        "legacy_db_sha_unchanged": before["legacy_db_sha"] == after["legacy_db_sha"],
        "user_template_sha_unchanged": before["user_template_sha"] == after["user_template_sha"],
        "agent_template_sha_unchanged": before["agent_template_sha"] == after["agent_template_sha"],
        "identity_vault_database_write_performed": False,
        "identity_vault_template_write_performed": False,
        "profiles_created": False,
        "agent_identity_activation_performed": False,
        "rmc_memory_write_performed": False,
        "forge_tool_registry_modified": False,
    }

    findings: List[Dict[str, str]] = []
    if not user_diag["json_ok"]:
        findings.append({"level": "INFO", "code": "IV_USER_TEMPLATE_INVALID_JSON_CONFIRMED", "message": "Existing user-template.json is invalid JSON and needs repair before profile seeding."})
    else:
        findings.append({"level": "INFO", "code": "IV_USER_TEMPLATE_ALREADY_JSON", "message": "Existing user-template.json parses as JSON; preview still generated for blueprint alignment."})
    if not agent_diag["json_ok"]:
        findings.append({"level": "INFO", "code": "IV_AGENT_TEMPLATE_INVALID_JSON_CONFIRMED", "message": "Existing agent-template.json is invalid JSON and needs repair before profile seeding."})
    else:
        findings.append({"level": "INFO", "code": "IV_AGENT_TEMPLATE_ALREADY_JSON", "message": "Existing agent-template.json parses as JSON; preview still generated for blueprint alignment."})
    if user_validation["ok"] and agent_validation["ok"]:
        findings.append({"level": "INFO", "code": "IV_REPAIRED_TEMPLATE_PREVIEWS_VALID", "message": "Both repaired template previews are valid JSON and include required operational identity fields."})
    if all(safety.values()):
        findings.append({"level": "INFO", "code": "IV_NO_MUTATION_CONFIRMED", "message": "Databases, .env metadata, and source templates remained unchanged during preview."})

    verdict = "PASS" if user_validation["ok"] and agent_validation["ok"] and all(safety.values()) else "FAIL"
    if verdict != "PASS":
        findings.append({"level": "FAIL", "code": "IV_TEMPLATE_PREVIEW_VALIDATION_FAILED", "message": "Preview validation or no-mutation safety checks failed."})

    report: Dict[str, Any] = {
        "timestamp": ts,
        "verdict": verdict,
        "boundary": "preview only; writes only Forge memory reports/previews",
        "source_template_diagnostics": {
            "user_template": user_diag,
            "agent_template": agent_diag,
        },
        "preview_files": {
            "user_template_preview": str(user_preview_path),
            "agent_template_preview": str(agent_preview_path),
        },
        "preview_validation": {
            "user_template": user_validation,
            "agent_template": agent_validation,
        },
        "databases": {
            "canonical": canonical_summary,
            "legacy": legacy_summary,
        },
        "safety": safety,
        "findings": findings,
    }

    json_path = run_dir / f"{ts}_identity_vault_patch226d_template_repair_preview.json"
    md_path = run_dir / f"{ts}_identity_vault_patch226d_template_repair_preview.md"
    write_json(json_path, report)
    write_report(md_path, report)

    latest_json = OUT_ROOT / "latest_identity_vault_patch226d_template_repair_preview.json"
    latest_md = OUT_ROOT / "latest_identity_vault_patch226d_template_repair_preview.md"
    latest_user = OUT_ROOT / "latest_user_template_repaired_preview.json"
    latest_agent = OUT_ROOT / "latest_agent_template_repaired_preview.json"
    write_json(latest_json, report)
    write_report(latest_md, report)
    write_json(latest_user, user_preview)
    write_json(latest_agent, agent_preview)

    print("Identity Vault Patch 226D template repair preview complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"User preview: {latest_user}")
    print(f"Agent preview: {latest_agent}")
    print(f"Verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
