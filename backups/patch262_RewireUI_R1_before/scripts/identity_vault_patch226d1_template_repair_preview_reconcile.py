#!/usr/bin/env python3
"""
Patch 226D.1 — Identity Vault Template Repair Preview Reconcile

Read-only reconcile for Patch 226D. It validates the repaired template preview JSON
files that Patch 226D already produced, confirms the real Identity Vault template
files were not overwritten, confirms databases/.env were not mutated during this
reconcile run, and writes a Forge-memory report only.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sqlite3
import stat
from pathlib import Path
from typing import Any, Dict, List, Tuple

FORGE_ROOT = Path("/home/nic/forge")
IDENTITY_ROOT = Path("/home/nic/identity-vault")
PREVIEW_ROOT = FORGE_ROOT / "memory" / "identity_vault_patch226d_template_repair_preview_v1"
RUN_ROOT_BASE = FORGE_ROOT / "memory" / "identity_vault_patch226d1_template_repair_preview_reconcile_v1"

USER_TEMPLATE = IDENTITY_ROOT / "templates" / "user-template.json"
AGENT_TEMPLATE = IDENTITY_ROOT / "templates" / "agent-template.json"
USER_PREVIEW = PREVIEW_ROOT / "latest_user_template_repaired_preview.json"
AGENT_PREVIEW = PREVIEW_ROOT / "latest_agent_template_repaired_preview.json"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"
ENV_PATH = IDENTITY_ROOT / ".env"
TOOL_REGISTRY = FORGE_ROOT / "config" / "tool_registry.json"

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

FORBIDDEN_TOKENS = [
    "BEGIN PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
    "OPENAI_API_KEY",
    "GITHUB_TOKEN",
    "DATABASE_URL",
    "PASSWORD=",
    "SECRET=",
    "TOKEN=",
    "identity_vault.db?",
    "vault.db?",
]


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.UTC).strftime("%Y%m%d_%H%M%S_UTC")


def iso_now() -> str:
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_path(path: Path) -> str | None:
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


def load_json(path: Path) -> Tuple[bool, Any, str | None]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return True, json.load(f), None
    except Exception as exc:  # noqa: BLE001
        return False, None, str(exc)


def json_status(path: Path) -> Dict[str, Any]:
    ok, obj, err = load_json(path)
    out = {
        "path": str(path),
        "exists": path.exists(),
        "json_ok": ok,
        "error": err,
        "sha16": (sha256_path(path) or "")[:16] if path.exists() else None,
    }
    if ok and isinstance(obj, dict):
        out["top_keys"] = sorted(obj.keys())
    return out


def validate_template_preview(path: Path, template_type: str, required: List[str]) -> Dict[str, Any]:
    ok, obj, err = load_json(path)
    result: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "json_ok": ok,
        "error": err,
        "template_type_expected": template_type,
        "sha16": (sha256_path(path) or "")[:16] if path.exists() else None,
        "required_missing": list(required),
        "forbidden_token_hits": [],
        "ok": False,
    }
    if not ok or not isinstance(obj, dict):
        return result

    payload = obj.get("operational_profile_json")
    if not isinstance(payload, dict):
        result["error"] = "operational_profile_json missing or not an object"
        return result

    result["template_type_found"] = obj.get("template_type")
    result["profile_schema_version"] = obj.get("profile_schema_version")
    result["target_table"] = obj.get("target_table")
    result["lookup_field"] = obj.get("lookup_field")
    result["required_missing"] = [k for k in required if k not in payload]

    raw = json.dumps(obj, sort_keys=True)
    hits = [tok for tok in FORBIDDEN_TOKENS if tok in raw]
    result["forbidden_token_hits"] = hits

    defaults = obj.get("defaults", {}) if isinstance(obj.get("defaults"), dict) else {}
    inactive_ok = defaults.get("is_active") == 0 and defaults.get("activation_state") == "inactive_draft"
    result["inactive_defaults_ok"] = inactive_ok

    result["ok"] = (
        obj.get("template_type") == template_type
        and not result["required_missing"]
        and not hits
        and inactive_ok
        and obj.get("profile_schema_version") == "1.0.0-blueprint"
    )
    return result


def sqlite_counts_readonly(db: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {"path": str(db), "exists": db.exists(), "opened_readonly": False, "ok": False, "rows": {}}
    if not db.exists():
        return out
    try:
        uri = f"file:{db}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        out["opened_readonly"] = True
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        out["tables"] = tables
        for table in tables:
            try:
                cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
                out["rows"][table] = cur.fetchone()[0]
            except Exception as exc:  # noqa: BLE001
                out["rows"][table] = f"ERROR: {exc}"
        conn.close()
        out["ok"] = True
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)
    return out


def main() -> int:
    ts = utc_stamp()
    run_dir = RUN_ROOT_BASE / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    before = {
        "env_meta": stat_meta(ENV_PATH),
        "canonical_db_sha": sha256_path(CANONICAL_DB),
        "legacy_db_sha": sha256_path(LEGACY_DB),
        "user_template_sha": sha256_path(USER_TEMPLATE),
        "agent_template_sha": sha256_path(AGENT_TEMPLATE),
        "tool_registry_sha": sha256_path(TOOL_REGISTRY),
    }

    source_user = json_status(USER_TEMPLATE)
    source_agent = json_status(AGENT_TEMPLATE)
    user_preview = validate_template_preview(USER_PREVIEW, "user_operational_identity_template", USER_REQUIRED)
    agent_preview = validate_template_preview(AGENT_PREVIEW, "agent_operational_identity_template", AGENT_REQUIRED)
    canonical = sqlite_counts_readonly(CANONICAL_DB)
    legacy = sqlite_counts_readonly(LEGACY_DB)

    after = {
        "env_meta": stat_meta(ENV_PATH),
        "canonical_db_sha": sha256_path(CANONICAL_DB),
        "legacy_db_sha": sha256_path(LEGACY_DB),
        "user_template_sha": sha256_path(USER_TEMPLATE),
        "agent_template_sha": sha256_path(AGENT_TEMPLATE),
        "tool_registry_sha": sha256_path(TOOL_REGISTRY),
    }

    safety = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before["env_meta"] == after["env_meta"],
        "canonical_db_sha_unchanged": before["canonical_db_sha"] == after["canonical_db_sha"],
        "legacy_db_sha_unchanged": before["legacy_db_sha"] == after["legacy_db_sha"],
        "user_template_sha_unchanged": before["user_template_sha"] == after["user_template_sha"],
        "agent_template_sha_unchanged": before["agent_template_sha"] == after["agent_template_sha"],
        "tool_registry_sha_unchanged": before["tool_registry_sha"] == after["tool_registry_sha"],
        "identity_vault_database_write_performed": False,
        "identity_vault_template_write_performed": False,
        "profiles_created": False,
        "agent_identity_activation_performed": False,
        "rmc_memory_write_performed": False,
        "forge_tool_registry_modified": False,
    }

    source_invalid_confirmed = source_user["exists"] and not source_user["json_ok"] and source_agent["exists"] and not source_agent["json_ok"]
    preview_ok = bool(user_preview["ok"] and agent_preview["ok"])
    safety_ok = all(safety.values())
    db_ok = bool(canonical.get("ok") and legacy.get("ok"))
    verdict = "PASS" if (source_invalid_confirmed and preview_ok and safety_ok and db_ok) else "FAIL"

    findings: List[Dict[str, str]] = []
    if source_invalid_confirmed:
        findings.append({"level": "INFO", "code": "IV_SOURCE_TEMPLATES_INVALID_CONFIRMED", "message": "Existing Identity Vault templates remain invalid JSON and were not overwritten."})
    else:
        findings.append({"level": "WARN", "code": "IV_SOURCE_TEMPLATE_STATE_UNEXPECTED", "message": "Source templates were not both invalid as expected; review before apply."})
    if preview_ok:
        findings.append({"level": "INFO", "code": "IV_REPAIRED_TEMPLATE_PREVIEWS_RECONCILED", "message": "Both repaired preview JSON files are valid and satisfy blueprint required fields."})
    else:
        findings.append({"level": "FAIL", "code": "IV_REPAIRED_TEMPLATE_PREVIEWS_NOT_READY", "message": "At least one repaired preview is invalid or missing required fields."})
    if safety_ok:
        findings.append({"level": "INFO", "code": "IV_NO_MUTATION_CONFIRMED", "message": "Databases, templates, .env metadata, and Forge registry remained unchanged during reconcile."})
    else:
        findings.append({"level": "FAIL", "code": "IV_NO_MUTATION_CHECK_FAILED", "message": "One or more no-mutation checks failed."})

    report = {
        "timestamp": ts,
        "boundary": "read-only reconcile; no template apply; no database writes; no identity activation",
        "source_templates": {"user": source_user, "agent": source_agent},
        "preview_validation": {"user": user_preview, "agent": agent_preview},
        "canonical_db": canonical,
        "legacy_db": legacy,
        "safety": safety,
        "findings": findings,
        "verdict": verdict,
    }

    json_path = run_dir / f"{ts}_identity_vault_patch226d1_template_repair_preview_reconcile.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    latest_json = RUN_ROOT_BASE / "latest_identity_vault_patch226d1_template_repair_preview_reconcile.json"
    latest_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Identity Vault Patch 226D.1 Template Repair Preview Reconcile")
    lines.append("")
    lines.append(f"Timestamp: `{ts}`")
    lines.append(f"Verdict: **{verdict}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This reconcile validates Patch 226D preview outputs only.")
    lines.append("- It writes reports only under Forge memory.")
    lines.append("- It does not overwrite Identity Vault templates.")
    lines.append("- It does not write databases, create profiles, activate identities, read `.env` secret values, modify Forge registry, or write RMC memory.")
    lines.append("")
    lines.append("## Source Template State")
    for label, item in [("user", source_user), ("agent", source_agent)]:
        lines.append(f"- {label}: path=`{item['path']}` exists=`{item['exists']}` json_ok=`{item['json_ok']}` sha16=`{item.get('sha16')}`")
        if item.get("error"):
            lines.append(f"  - error: `{item['error']}`")
    lines.append("")
    lines.append("## Repaired Preview Validation")
    for label, item in [("user", user_preview), ("agent", agent_preview)]:
        lines.append(f"- {label}: exists=`{item['exists']}` json_ok=`{item['json_ok']}` ok=`{item['ok']}` sha16=`{item.get('sha16')}`")
        lines.append(f"  - required_missing: `{item.get('required_missing')}`")
        lines.append(f"  - forbidden_token_hits: `{item.get('forbidden_token_hits')}`")
        lines.append(f"  - inactive_defaults_ok: `{item.get('inactive_defaults_ok')}`")
    lines.append("")
    lines.append("## Database Read-Only Summary")
    lines.append(f"- canonical: path=`{canonical.get('path')}` ok=`{canonical.get('ok')}` opened_readonly=`{canonical.get('opened_readonly')}` rows=`{canonical.get('rows')}`")
    lines.append(f"- legacy: path=`{legacy.get('path')}` ok=`{legacy.get('ok')}` opened_readonly=`{legacy.get('opened_readonly')}` rows=`{legacy.get('rows')}`")
    lines.append("")
    lines.append("## Safety Checks")
    for k, v in safety.items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Findings")
    for f in findings:
        lines.append(f"- **{f['level']}** `{f['code']}` — {f['message']}")
    lines.append("")
    lines.append("## Next Safe Step")
    if verdict == "PASS":
        lines.append("Create Patch 226E to back up and apply the repaired template files exactly as previewed. Do not write profiles or activate identities yet.")
    else:
        lines.append("Do not apply templates yet. Review the failed reconcile details first.")

    md = "\n".join(lines) + "\n"
    md_path = run_dir / f"{ts}_identity_vault_patch226d1_template_repair_preview_reconcile.md"
    md_path.write_text(md, encoding="utf-8")
    latest_md = RUN_ROOT_BASE / "latest_identity_vault_patch226d1_template_repair_preview_reconcile.md"
    latest_md.write_text(md, encoding="utf-8")

    print("Identity Vault Patch 226D.1 template repair preview reconcile complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
