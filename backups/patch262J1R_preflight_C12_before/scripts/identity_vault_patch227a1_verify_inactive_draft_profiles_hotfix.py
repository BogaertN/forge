#!/usr/bin/env python3
"""
Patch 227A.1 — Identity Vault inactive draft profile verifier hotfix.

Purpose:
- Replaces failed Patch 227A verifier that crashed before writing a report.
- Verifies the four canonical Identity Vault profile rows written by Patch 227.
- Read-only against Identity Vault databases and templates.
- Writes reports only under Forge memory.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sqlite3
import stat
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

FORGE_ROOT = Path("/home/nic/forge")
IDENTITY_ROOT = Path("/home/nic/identity-vault")
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"
ENV_PATH = IDENTITY_ROOT / ".env"
TOOL_REGISTRY = FORGE_ROOT / "config" / "tool_registry.json"
USER_TEMPLATE = IDENTITY_ROOT / "templates" / "user-template.json"
AGENT_TEMPLATE = IDENTITY_ROOT / "templates" / "agent-template.json"

RUN_ROOT_BASE = FORGE_ROOT / "memory" / "identity_vault_patch227a1_inactive_profile_verify_v1"

EXPECTED_USER = "nic_bogaert"
EXPECTED_AGENTS = {
    "gilligan.local": "rmc/agents/gilligan.local",
    "athena.local": "rmc/agents/athena.local",
    "neo.local": "rmc/agents/neo.local",
}


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def iso_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_metadata(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    st = path.stat()
    return {
        "exists": True,
        "size": st.st_size,
        "mtime_ns": st.st_mtime_ns,
        "mode": oct(stat.S_IMODE(st.st_mode)),
    }


def connect_readonly(path: Path) -> sqlite3.Connection:
    uri = f"file:{path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def table_names(conn: sqlite3.Connection) -> List[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    return [r["name"] for r in rows]


def db_row_counts(conn: sqlite3.Connection) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for name in table_names(conn):
        try:
            counts[name] = int(conn.execute(f'SELECT COUNT(*) AS c FROM "{name}"').fetchone()["c"])
        except Exception:
            counts[name] = -1
    return counts


def columns_for(conn: sqlite3.Connection, table: str) -> List[str]:
    try:
        rows = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
        return [r["name"] for r in rows]
    except Exception:
        return []


def parse_json_text(text: Any) -> Tuple[bool, Optional[Any], str]:
    if text is None:
        return False, None, "value is None"
    if not isinstance(text, str):
        return False, None, f"value is not string: {type(text).__name__}"
    try:
        return True, json.loads(text), ""
    except Exception as exc:
        return False, None, str(exc)


def canonical_json_hash(obj: Any) -> str:
    data = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def pretty_json_hash(obj: Any) -> str:
    data = json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def raw_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def profile_hash_ok(stored_hash: Any, raw_text: str, obj: Any) -> bool:
    if not stored_hash or not isinstance(stored_hash, str):
        return False
    candidates = {
        raw_hash(raw_text),
        canonical_json_hash(obj),
        pretty_json_hash(obj),
    }
    return stored_hash in candidates


def pointer_only(ns: Any) -> bool:
    if not isinstance(ns, str) or not ns:
        return False
    if ns.startswith("/") or "\\" in ns or ".." in ns:
        return False
    if not ns.startswith("rmc/agents/"):
        return False
    return True


def template_check(path: Path, expected_type: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "json_ok": False,
        "template_type": None,
        "inactive_defaults_ok": False,
        "sha16": None,
        "error": None,
    }
    if not path.exists():
        result["error"] = "missing"
        return result
    result["sha16"] = (sha256_file(path) or "")[:16]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        result["json_ok"] = True
        result["template_type"] = data.get("template_type")
        defaults = data.get("defaults", {})
        result["inactive_defaults_ok"] = (
            defaults.get("is_active") == 0
            and defaults.get("activation_state") == "inactive_draft"
        )
        result["expected_type_ok"] = data.get("template_type") == expected_type
    except Exception as exc:
        result["error"] = str(exc)
    return result


def verify_user(row: Optional[sqlite3.Row]) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "user_id": EXPECTED_USER,
        "exists": row is not None,
        "ok": False,
        "issues": [],
    }
    if row is None:
        result["issues"].append("missing user row")
        return result

    rowd = dict(row)
    result.update({
        "canonical_name": rowd.get("canonical_name"),
        "version": rowd.get("version"),
        "is_active": rowd.get("is_active"),
        "profile_schema_version": rowd.get("profile_schema_version"),
        "profile_hash_present": bool(rowd.get("profile_hash")),
        "last_validated_at_present": bool(rowd.get("last_validated_at")),
    })

    ok_json, payload, err = parse_json_text(rowd.get("operational_profile_json"))
    result["operational_json_ok"] = ok_json
    if not ok_json:
        result["issues"].append(f"operational_profile_json invalid: {err}")
        payload = {}

    required = [
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
    missing = [k for k in required if k not in payload]
    result["required_missing"] = missing
    if missing:
        result["issues"].append(f"missing payload fields: {missing}")

    if rowd.get("user_id") != EXPECTED_USER:
        result["issues"].append("user_id mismatch")
    if rowd.get("is_active") != 0:
        result["issues"].append("is_active is not 0")

    if ok_json:
        result["hash_ok"] = profile_hash_ok(
            rowd.get("profile_hash"),
            rowd.get("operational_profile_json"),
            payload,
        )
        if not result["hash_ok"]:
            result["issues"].append("profile_hash mismatch")
    else:
        result["hash_ok"] = False

    result["ok"] = not result["issues"]
    return result


def verify_agent(row: Optional[sqlite3.Row], agent_id: str, expected_ns: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "agent_id": agent_id,
        "exists": row is not None,
        "ok": False,
        "issues": [],
    }
    if row is None:
        result["issues"].append("missing agent row")
        return result

    rowd = dict(row)
    result.update({
        "canonical_name": rowd.get("canonical_name"),
        "role": rowd.get("role"),
        "version": rowd.get("version"),
        "is_active": rowd.get("is_active"),
        "activation_state": rowd.get("activation_state"),
        "rmc_namespace": rowd.get("rmc_namespace"),
        "profile_schema_version": rowd.get("profile_schema_version"),
        "profile_hash_present": bool(rowd.get("profile_hash")),
        "last_validated_at_present": bool(rowd.get("last_validated_at")),
    })

    ok_json, payload, err = parse_json_text(rowd.get("operational_profile_json"))
    result["operational_json_ok"] = ok_json
    if not ok_json:
        result["issues"].append(f"operational_profile_json invalid: {err}")
        payload = {}

    required = [
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
    missing = [k for k in required if k not in payload]
    result["required_missing"] = missing
    if missing:
        result["issues"].append(f"missing payload fields: {missing}")

    if rowd.get("agent_id") != agent_id:
        result["issues"].append("agent_id mismatch")
    if rowd.get("is_active") != 0:
        result["issues"].append("is_active is not 0")
    if rowd.get("activation_state") != "inactive_draft":
        result["issues"].append("activation_state is not inactive_draft")
    if rowd.get("rmc_namespace") != expected_ns:
        result["issues"].append("rmc_namespace mismatch")
    result["rmc_pointer_only"] = pointer_only(rowd.get("rmc_namespace"))
    if not result["rmc_pointer_only"]:
        result["issues"].append("rmc_namespace is not pointer-only")

    if ok_json:
        payload_ns = payload.get("rmc_namespace")
        result["payload_rmc_namespace"] = payload_ns
        if payload.get("agent_id") != agent_id:
            result["issues"].append("payload agent_id mismatch")
        if payload_ns != expected_ns:
            result["issues"].append("payload rmc_namespace mismatch")
        result["hash_ok"] = profile_hash_ok(
            rowd.get("profile_hash"),
            rowd.get("operational_profile_json"),
            payload,
        )
        if not result["hash_ok"]:
            result["issues"].append("profile_hash mismatch")
    else:
        result["hash_ok"] = False

    result["ok"] = not result["issues"]
    return result


def possible_rmc_namespace_paths() -> Dict[str, List[str]]:
    roots = [
        Path("/home/nic/aiweb/rmc"),
        Path("/home/nic/forge/rmc"),
        Path("/home/nic/forge/memory/rmc"),
        Path("/home/nic/aiweb/memory/rmc"),
    ]
    hits: Dict[str, List[str]] = {}
    for agent_id, ns in EXPECTED_AGENTS.items():
        suffix = Path(*ns.split("/")[1:])  # agents/<id>
        found: List[str] = []
        for root in roots:
            candidate = root / suffix
            if candidate.exists():
                found.append(str(candidate))
        hits[agent_id] = found
    return hits


def write_reports(run_dir: Path, report: Dict[str, Any]) -> Tuple[Path, Path, Path, Path]:
    run_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_dir / f"{report['timestamp']}_identity_vault_patch227a1_inactive_profile_verify.json"
    md_path = run_dir / f"{report['timestamp']}_identity_vault_patch227a1_inactive_profile_verify.md"
    latest_json = RUN_ROOT_BASE / "latest_identity_vault_patch227a1_inactive_profile_verify.json"
    latest_md = RUN_ROOT_BASE / "latest_identity_vault_patch227a1_inactive_profile_verify.md"

    json_text = json.dumps(report, indent=2, sort_keys=True)
    json_path.write_text(json_text + "\n", encoding="utf-8")
    latest_json.write_text(json_text + "\n", encoding="utf-8")

    lines: List[str] = []
    lines.append("# Identity Vault Patch 227A.1 Inactive Draft Profile Verify")
    lines.append("")
    lines.append(f"Timestamp: `{report['timestamp']}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This hotfix replaces the failed Patch 227A verifier that crashed before writing a report.")
    lines.append("- It reads canonical Identity Vault profile rows through a read-only SQLite connection.")
    lines.append("- It writes reports only under Forge memory.")
    lines.append("- It does not write databases, create profiles, activate identities, read `.env` secret values, modify Forge registry, or write RMC memory.")
    lines.append("")
    lines.append("## Canonical Database")
    c = report["canonical"]
    lines.append(f"- path: `{c['path']}` opened_readonly=`{c['opened_readonly']}` ok=`{c['ok']}`")
    lines.append(f"- row counts: `{c.get('row_counts')}`")
    lines.append(f"- agent columns include operational fields: `{c.get('agent_columns_ok')}`")
    lines.append(f"- user columns include operational fields: `{c.get('user_columns_ok')}`")
    lines.append("")
    lines.append("## Template Gate")
    for name, t in report["templates"].items():
        lines.append(f"- `{name}` json_ok=`{t.get('json_ok')}` inactive_defaults_ok=`{t.get('inactive_defaults_ok')}` expected_type_ok=`{t.get('expected_type_ok')}` sha16=`{t.get('sha16')}`")
    lines.append("")
    lines.append("## Profile Verification")
    u = report["user_profile"]
    lines.append(f"- user `{EXPECTED_USER}` exists=`{u.get('exists')}` is_active=`{u.get('is_active')}` json_ok=`{u.get('operational_json_ok')}` hash_ok=`{u.get('hash_ok')}` ok=`{u.get('ok')}`")
    if u.get("issues"):
        lines.append(f"  - issues: `{u.get('issues')}`")
    for agent_id, a in report["agent_profiles"].items():
        lines.append(f"- agent `{agent_id}` exists=`{a.get('exists')}` activation_state=`{a.get('activation_state')}` is_active=`{a.get('is_active')}` rmc_namespace=`{a.get('rmc_namespace')}` pointer_only=`{a.get('rmc_pointer_only')}` hash_ok=`{a.get('hash_ok')}` ok=`{a.get('ok')}`")
        if a.get("issues"):
            lines.append(f"  - issues: `{a.get('issues')}`")
    lines.append("")
    lines.append("## RMC Namespace Path Check")
    lines.append("- Stored RMC namespaces are pointers only. This verifier does not create namespace folders.")
    for agent_id, hits in report["rmc_namespace_path_hits"].items():
        lines.append(f"- `{agent_id}` existing namespace dirs found: `{hits}`")
    lines.append("")
    lines.append("## Safety Checks")
    for k, v in report["safety"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Findings")
    for f in report["findings"]:
        lines.append(f"- **{f['level']}** `{f['code']}` — {f['message']}")
    lines.append("")
    lines.append("## Next Safe Step")
    if report["verdict"] == "PASS":
        lines.append("Manually test Forge commands: `forge-agent-list`, `forge-agent-show gilligan.local`, `forge-agent-show athena.local`, and `forge-agent-show neo.local`.")
    else:
        lines.append("Do not run Forge agent commands yet. Review the blocker findings first.")

    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")
    return md_path, json_path, latest_md, latest_json


def main() -> int:
    timestamp = utc_stamp()
    RUN_ROOT_BASE.mkdir(parents=True, exist_ok=True)
    run_dir = RUN_ROOT_BASE / timestamp

    before = {
        "env": stat_metadata(ENV_PATH),
        "canonical_db_sha": sha256_file(CANONICAL_DB),
        "legacy_db_sha": sha256_file(LEGACY_DB),
        "tool_registry_sha": sha256_file(TOOL_REGISTRY),
        "user_template_sha": sha256_file(USER_TEMPLATE),
        "agent_template_sha": sha256_file(AGENT_TEMPLATE),
    }

    report: Dict[str, Any] = {
        "timestamp": timestamp,
        "boundary": "read-only verification; reports only under Forge memory",
        "canonical": {"path": str(CANONICAL_DB), "exists": CANONICAL_DB.exists(), "opened_readonly": False, "ok": False},
        "legacy": {"path": str(LEGACY_DB), "exists": LEGACY_DB.exists(), "opened_readonly": False, "ok": False},
        "templates": {
            "user": template_check(USER_TEMPLATE, "user_operational_identity_template"),
            "agent": template_check(AGENT_TEMPLATE, "agent_operational_identity_template"),
        },
        "user_profile": {},
        "agent_profiles": {},
        "rmc_namespace_path_hits": {},
        "safety": {},
        "findings": [],
        "verdict": "FAIL",
    }

    try:
        with connect_readonly(CANONICAL_DB) as conn:
            report["canonical"]["opened_readonly"] = True
            report["canonical"]["ok"] = True
            report["canonical"]["tables"] = table_names(conn)
            report["canonical"]["row_counts"] = db_row_counts(conn)
            agent_cols = columns_for(conn, "agent_profiles")
            user_cols = columns_for(conn, "user_profiles")
            report["canonical"]["agent_columns"] = agent_cols
            report["canonical"]["user_columns"] = user_cols
            agent_needed = {"operational_profile_json", "profile_schema_version", "rmc_namespace", "activation_state", "profile_hash", "last_validated_at"}
            user_needed = {"operational_profile_json", "profile_schema_version", "profile_hash", "last_validated_at"}
            report["canonical"]["agent_columns_ok"] = agent_needed.issubset(set(agent_cols))
            report["canonical"]["user_columns_ok"] = user_needed.issubset(set(user_cols))

            user_row = conn.execute(
                "SELECT * FROM user_profiles WHERE user_id = ?",
                (EXPECTED_USER,),
            ).fetchone()
            report["user_profile"] = verify_user(user_row)

            for agent_id, ns in EXPECTED_AGENTS.items():
                row = conn.execute(
                    "SELECT * FROM agent_profiles WHERE agent_id = ?",
                    (agent_id,),
                ).fetchone()
                report["agent_profiles"][agent_id] = verify_agent(row, agent_id, ns)

    except Exception as exc:
        report["canonical"]["error"] = str(exc)

    try:
        with connect_readonly(LEGACY_DB) as conn:
            report["legacy"]["opened_readonly"] = True
            report["legacy"]["ok"] = True
            report["legacy"]["tables"] = table_names(conn)
            report["legacy"]["row_counts"] = db_row_counts(conn)
    except Exception as exc:
        report["legacy"]["error"] = str(exc)

    report["rmc_namespace_path_hits"] = possible_rmc_namespace_paths()

    after = {
        "env": stat_metadata(ENV_PATH),
        "canonical_db_sha": sha256_file(CANONICAL_DB),
        "legacy_db_sha": sha256_file(LEGACY_DB),
        "tool_registry_sha": sha256_file(TOOL_REGISTRY),
        "user_template_sha": sha256_file(USER_TEMPLATE),
        "agent_template_sha": sha256_file(AGENT_TEMPLATE),
    }

    report["safety"] = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before["env"] == after["env"],
        "canonical_db_sha_unchanged": before["canonical_db_sha"] == after["canonical_db_sha"],
        "legacy_db_sha_unchanged": before["legacy_db_sha"] == after["legacy_db_sha"],
        "tool_registry_sha_unchanged": before["tool_registry_sha"] == after["tool_registry_sha"],
        "user_template_sha_unchanged": before["user_template_sha"] == after["user_template_sha"],
        "agent_template_sha_unchanged": before["agent_template_sha"] == after["agent_template_sha"],
        "identity_vault_database_write_performed": before["canonical_db_sha"] != after["canonical_db_sha"],
        "identity_vault_template_write_performed": before["user_template_sha"] != after["user_template_sha"] or before["agent_template_sha"] != after["agent_template_sha"],
        "profiles_created": False,
        "agent_identity_activation_performed": any(
            a.get("is_active") != 0 or a.get("activation_state") != "inactive_draft"
            for a in report.get("agent_profiles", {}).values()
        ),
        "rmc_memory_write_performed": False,
        "forge_tool_registry_modified": before["tool_registry_sha"] != after["tool_registry_sha"],
    }

    findings: List[Dict[str, str]] = []
    def add(level: str, code: str, message: str) -> None:
        findings.append({"level": level, "code": code, "message": message})

    if report["canonical"].get("ok"):
        add("INFO", "IV_CANONICAL_DB_READONLY_OK", "Canonical Identity Vault database opened read-only.")
    else:
        add("FAIL", "IV_CANONICAL_DB_READONLY_FAILED", "Canonical Identity Vault database did not open read-only.")

    if report["templates"]["user"].get("json_ok") and report["templates"]["agent"].get("json_ok"):
        add("INFO", "IV_TEMPLATES_VALID", "User and agent templates remain valid JSON.")
    else:
        add("FAIL", "IV_TEMPLATE_INVALID", "One or more Identity Vault templates are invalid.")

    user_ok = bool(report.get("user_profile", {}).get("ok"))
    agents_ok = all(bool(a.get("ok")) for a in report.get("agent_profiles", {}).values())
    if user_ok and agents_ok:
        add("INFO", "IV_INACTIVE_DRAFT_PROFILES_VERIFIED", "Nic, Gilligan, Athena, and Neo profiles exist and validate as inactive draft records.")
    else:
        add("FAIL", "IV_INACTIVE_DRAFT_PROFILE_VERIFY_FAILED", "One or more required inactive draft profiles failed verification.")

    if all(a.get("rmc_pointer_only") for a in report.get("agent_profiles", {}).values()):
        add("INFO", "IV_RMC_POINTERS_ONLY", "Agent RMC namespace fields are pointer-only strings.")
    else:
        add("FAIL", "IV_RMC_POINTER_CHECK_FAILED", "One or more RMC namespace fields are not pointer-only.")

    if any(report["rmc_namespace_path_hits"].values()):
        add("WARN", "IV_RMC_NAMESPACE_DIRS_ALREADY_EXIST", "One or more matching RMC namespace directories already exist; this verifier did not create them.")
    else:
        add("INFO", "IV_NO_RMC_NAMESPACE_DIRS_FOUND", "No matching RMC namespace folders were found at checked roots; scaffolding remains a later phase.")

    safety_ok = (
        report["safety"]["env_stat_unchanged"]
        and report["safety"]["canonical_db_sha_unchanged"]
        and report["safety"]["legacy_db_sha_unchanged"]
        and report["safety"]["tool_registry_sha_unchanged"]
        and report["safety"]["user_template_sha_unchanged"]
        and report["safety"]["agent_template_sha_unchanged"]
        and not report["safety"]["agent_identity_activation_performed"]
        and not report["safety"]["identity_vault_database_write_performed"]
        and not report["safety"]["identity_vault_template_write_performed"]
        and not report["safety"]["forge_tool_registry_modified"]
    )
    if safety_ok:
        add("INFO", "IV_NO_MUTATION_VERIFIED", "Verification did not mutate templates, DBs, .env metadata, RMC memory, or Forge registry.")
    else:
        add("FAIL", "IV_NO_MUTATION_CHECK_FAILED", "One or more no-mutation checks failed.")

    report["findings"] = findings
    report["verdict"] = "PASS" if (
        report["canonical"].get("ok")
        and report["canonical"].get("agent_columns_ok")
        and report["canonical"].get("user_columns_ok")
        and report["templates"]["user"].get("json_ok")
        and report["templates"]["agent"].get("json_ok")
        and user_ok
        and agents_ok
        and safety_ok
    ) else "FAIL"

    md_path, json_path, latest_md, latest_json = write_reports(run_dir, report)

    print("Identity Vault Patch 227A.1 inactive profile verification complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {report['verdict']}")

    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
