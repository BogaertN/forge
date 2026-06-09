#!/usr/bin/env python3
"""
Patch 228A — Full Profile Adapter Verification

Read-only verification of Forge's Identity Vault full-profile connector.
Writes reports only under Forge memory. Does not mutate Identity Vault,
RMC memory, Forge registry, templates, or agent activation state.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import importlib.util
import json
import os
import py_compile
import sqlite3
import stat
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

FORGE_ROOT = Path("/home/nic/forge")
AIWEB_ROOT = Path("/home/nic/aiweb")
IDENTITY_ROOT = Path("/home/nic/identity-vault")
RMC_WRAPPERS_ROOT = AIWEB_ROOT / "runtime_wrappers"
CONNECTOR_PATH = FORGE_ROOT / "agents" / "forge" / "aiweb_readonly_connectors.py"
TOOL_REGISTRY = FORGE_ROOT / "config" / "tool_registry.json"
CANONICAL_DB = IDENTITY_ROOT / "data" / "identity_vault.db"
LEGACY_DB = IDENTITY_ROOT / "vault.db"
ENV_PATH = IDENTITY_ROOT / ".env"
USER_TEMPLATE = IDENTITY_ROOT / "templates" / "user-template.json"
AGENT_TEMPLATE = IDENTITY_ROOT / "templates" / "agent-template.json"
REPORT_ROOT = FORGE_ROOT / "memory" / "aiweb_patch228a_full_profile_adapter_verification_v1"
EXPECTED_AGENTS = ["gilligan.local", "athena.local", "neo.local"]
EXPECTED_USER = "nic_bogaert"


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


def stat_metadata(path: Path) -> Optional[Dict[str, Any]]:
    try:
        st = path.stat()
    except FileNotFoundError:
        return None
    return {
        "exists": True,
        "size": st.st_size,
        "mtime_ns": st.st_mtime_ns,
        "mode": oct(stat.S_IMODE(st.st_mode)),
    }


def safe_json_load(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False, "json_ok": False, "error": "missing"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {"exists": True, "json_ok": True, "keys": sorted(data.keys()) if isinstance(data, dict) else []}
    except Exception as exc:
        return {"exists": True, "json_ok": False, "error": str(exc)}


def sqlite_readonly_counts(path: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {"path": str(path), "exists": path.exists(), "ok": False, "opened_readonly": False, "row_counts": {}, "tables": []}
    if not path.exists():
        return out
    try:
        uri = f"file:{path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        out["opened_readonly"] = True
        try:
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [r[0] for r in cur.fetchall()]
            out["tables"] = tables
            for table in tables:
                try:
                    out["row_counts"][table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                except Exception as exc:
                    out["row_counts"][table] = f"ERROR: {exc}"
            out["ok"] = True
        finally:
            conn.close()
    except Exception as exc:
        out["error"] = str(exc)
    return out


def load_connector() -> Tuple[Optional[Any], Dict[str, Any]]:
    info: Dict[str, Any] = {"connector_path": str(CONNECTOR_PATH), "exists": CONNECTOR_PATH.exists(), "compile_ok": False, "import_ok": False}
    if not CONNECTOR_PATH.exists():
        info["error"] = "connector missing"
        return None, info
    try:
        py_compile.compile(str(CONNECTOR_PATH), doraise=True)
        info["compile_ok"] = True
    except Exception as exc:
        info["compile_error"] = str(exc)
        return None, info
    try:
        spec = importlib.util.spec_from_file_location("aiweb_readonly_connectors_patch228a_verify", CONNECTOR_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError("could not create import spec")
        module = importlib.util.module_from_spec(spec)
        sys.modules["aiweb_readonly_connectors_patch228a_verify"] = module
        spec.loader.exec_module(module)
        info["import_ok"] = True
        info["functions"] = sorted([name for name in dir(module) if name.startswith("forge_")])
        return module, info
    except Exception as exc:
        info["import_error"] = str(exc)
        info["traceback_tail"] = traceback.format_exc().splitlines()[-8:]
        return None, info


def call_func(module: Any, name: str, *args: Any) -> Dict[str, Any]:
    if module is None or not hasattr(module, name):
        return {"ok": False, "error": f"missing function {name}"}
    try:
        result = getattr(module, name)(*args)
        if isinstance(result, dict):
            return result
        return {"ok": False, "error": "non-dict result", "result_type": type(result).__name__, "result_preview": repr(result)[:500]}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "traceback_tail": traceback.format_exc().splitlines()[-8:]}


def compact_agent_check(agent: Dict[str, Any]) -> Dict[str, Any]:
    required = [
        "agent_id", "canonical_name", "role", "activation_state", "is_active", "rmc_namespace",
        "profile_schema_version", "profile_hash", "profile_hash_ok", "profile_hash_method", "last_validated_at",
        "permissions_summary", "forbidden_actions_summary", "full_payload_available", "payload_dumped",
    ]
    missing = [k for k in required if k not in agent]
    forbidden_payload_keys = [k for k in ("operational_profile_json", "profile_payload", "payload") if k in agent]
    return {
        "agent_id": agent.get("agent_id"),
        "missing": missing,
        "activation_state": agent.get("activation_state"),
        "is_active": agent.get("is_active"),
        "rmc_namespace": agent.get("rmc_namespace"),
        "profile_hash_ok": agent.get("profile_hash_ok"),
        "profile_hash_method": agent.get("profile_hash_method"),
        "payload_dumped": agent.get("payload_dumped"),
        "forbidden_payload_keys": forbidden_payload_keys,
        "permissions_summary_count": len(agent.get("permissions_summary") or []),
        "forbidden_actions_summary_count": len(agent.get("forbidden_actions_summary") or []),
        "ok": (
            not missing
            and agent.get("activation_state") == "inactive_draft"
            and agent.get("is_active") == 0
            and isinstance(agent.get("rmc_namespace"), str)
            and agent.get("rmc_namespace", "").startswith("rmc/agents/")
            and agent.get("profile_hash_ok") is True
            and agent.get("profile_hash_method") == "json_sort_compact"
            and agent.get("payload_dumped") is False
            and not forbidden_payload_keys
        ),
    }


def main() -> int:
    timestamp = utc_stamp()
    run_dir = REPORT_ROOT / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    before = {
        "env_stat": stat_metadata(ENV_PATH),
        "canonical_db_sha": sha256_file(CANONICAL_DB),
        "legacy_db_sha": sha256_file(LEGACY_DB),
        "tool_registry_sha": sha256_file(TOOL_REGISTRY),
        "user_template_sha": sha256_file(USER_TEMPLATE),
        "agent_template_sha": sha256_file(AGENT_TEMPLATE),
        "rmc_fingerprint": sha256_file(RMC_WRAPPERS_ROOT / "rmc_orchestrator" / "rmc_orchestrator.py"),
    }

    report: Dict[str, Any] = {
        "timestamp": timestamp,
        "boundary": "read-only full profile adapter verification; no DB writes; no identity activation; no RMC writes",
        "connector": {},
        "calls": {},
        "checks": {},
        "database": {},
        "templates": {},
        "safety": {},
        "findings": [],
        "verdict": "FAIL",
    }

    module, connector_info = load_connector()
    report["connector"] = connector_info
    report["database"]["canonical"] = sqlite_readonly_counts(CANONICAL_DB)
    report["database"]["legacy"] = sqlite_readonly_counts(LEGACY_DB)
    report["templates"]["user"] = safe_json_load(USER_TEMPLATE)
    report["templates"]["agent"] = safe_json_load(AGENT_TEMPLATE)

    agent_list = call_func(module, "forge_agent_list")
    report["calls"]["forge_agent_list"] = agent_list
    show_results: Dict[str, Any] = {}
    for agent_id in EXPECTED_AGENTS:
        show_results[agent_id] = call_func(module, "forge_agent_show", agent_id)
    report["calls"]["forge_agent_show"] = show_results
    report["calls"]["forge_identity_status"] = call_func(module, "forge_identity_status")
    report["calls"]["forge_system_boundary_map"] = call_func(module, "forge_system_boundary_map")

    list_agents = agent_list.get("agents", []) if isinstance(agent_list, dict) else []
    list_agent_ids = [a.get("agent_id") for a in list_agents if isinstance(a, dict)]
    list_checks = [compact_agent_check(a) for a in list_agents if isinstance(a, dict) and a.get("agent_id") in EXPECTED_AGENTS]

    show_checks: List[Dict[str, Any]] = []
    for agent_id in EXPECTED_AGENTS:
        result = show_results.get(agent_id, {})
        agent = result.get("agent", {}) if isinstance(result, dict) else {}
        chk = compact_agent_check(agent if isinstance(agent, dict) else {})
        chk["found"] = result.get("found") if isinstance(result, dict) else False
        chk["call_ok"] = result.get("ok") if isinstance(result, dict) else False
        show_checks.append(chk)

    identity_status = report["calls"].get("forge_identity_status", {})
    boundary_map = report["calls"].get("forge_system_boundary_map", {})

    report["checks"] = {
        "agent_list_ok": agent_list.get("ok") is True,
        "agent_list_read_only": agent_list.get("read_only") is True,
        "agent_list_connector_version": agent_list.get("connector_version"),
        "agents_returned": agent_list.get("agents_returned"),
        "expected_agents_present": sorted(list_agent_ids) == sorted(EXPECTED_AGENTS),
        "list_agent_checks": list_checks,
        "show_agent_checks": show_checks,
        "all_list_profiles_ok": len(list_checks) == 3 and all(c.get("ok") for c in list_checks),
        "all_show_profiles_ok": len(show_checks) == 3 and all(c.get("ok") and c.get("found") and c.get("call_ok") for c in show_checks),
        "identity_status_ok": isinstance(identity_status, dict) and identity_status.get("ok") is True and identity_status.get("read_only") is True,
        "boundary_map_ok": isinstance(boundary_map, dict) and boundary_map.get("ok") is True and boundary_map.get("read_only") is True,
        "root_identity_vault_exists": isinstance(boundary_map, dict) and boundary_map.get("root_exists", {}).get("identity_vault") is True,
        "root_rmc_wrappers_exists": isinstance(boundary_map, dict) and boundary_map.get("root_exists", {}).get("rmc_wrappers") is True,
    }

    after = {
        "env_stat": stat_metadata(ENV_PATH),
        "canonical_db_sha": sha256_file(CANONICAL_DB),
        "legacy_db_sha": sha256_file(LEGACY_DB),
        "tool_registry_sha": sha256_file(TOOL_REGISTRY),
        "user_template_sha": sha256_file(USER_TEMPLATE),
        "agent_template_sha": sha256_file(AGENT_TEMPLATE),
        "rmc_fingerprint": sha256_file(RMC_WRAPPERS_ROOT / "rmc_orchestrator" / "rmc_orchestrator.py"),
    }

    safety = {
        "env_secret_values_read": False,
        "env_stat_unchanged": before["env_stat"] == after["env_stat"],
        "canonical_db_sha_unchanged": before["canonical_db_sha"] == after["canonical_db_sha"],
        "legacy_db_sha_unchanged": before["legacy_db_sha"] == after["legacy_db_sha"],
        "tool_registry_sha_unchanged": before["tool_registry_sha"] == after["tool_registry_sha"],
        "user_template_sha_unchanged": before["user_template_sha"] == after["user_template_sha"],
        "agent_template_sha_unchanged": before["agent_template_sha"] == after["agent_template_sha"],
        "rmc_fingerprint_unchanged": before["rmc_fingerprint"] == after["rmc_fingerprint"],
        "identity_vault_database_write_performed": False,
        "profiles_created": False,
        "agent_identity_activation_performed": False,
        "rmc_memory_write_performed": False,
        "forge_tool_registry_modified": False,
    }
    report["safety"] = safety

    ok = (
        connector_info.get("compile_ok") is True
        and connector_info.get("import_ok") is True
        and report["checks"].get("agent_list_ok") is True
        and report["checks"].get("agent_list_read_only") is True
        and report["checks"].get("expected_agents_present") is True
        and report["checks"].get("all_list_profiles_ok") is True
        and report["checks"].get("all_show_profiles_ok") is True
        and report["checks"].get("identity_status_ok") is True
        and report["checks"].get("boundary_map_ok") is True
        and all(v is True or k in {"env_secret_values_read", "identity_vault_database_write_performed", "profiles_created", "agent_identity_activation_performed", "rmc_memory_write_performed", "forge_tool_registry_modified"} for k, v in safety.items())
        and safety["env_secret_values_read"] is False
        and safety["identity_vault_database_write_performed"] is False
        and safety["profiles_created"] is False
        and safety["agent_identity_activation_performed"] is False
        and safety["rmc_memory_write_performed"] is False
        and safety["forge_tool_registry_modified"] is False
    )

    if ok:
        report["verdict"] = "PASS"
        report["findings"].append({"level": "INFO", "code": "PATCH228A_FULL_PROFILE_ADAPTER_VERIFIED", "message": "Forge read-only connector lists and shows all inactive full-profile summaries with valid hashes and no payload dumps."})
        report["findings"].append({"level": "INFO", "code": "PATCH228A_NO_MUTATION", "message": "Verification did not mutate DBs, templates, .env metadata, RMC wrappers, or Forge registry."})
    else:
        report["findings"].append({"level": "FAIL", "code": "PATCH228A_VERIFICATION_FAILED", "message": "One or more connector, full-profile, hash, or safety checks failed."})

    json_path = run_dir / f"{timestamp}_aiweb_patch228a_full_profile_adapter_verification.json"
    md_path = run_dir / f"{timestamp}_aiweb_patch228a_full_profile_adapter_verification.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    def yesno(value: Any) -> str:
        return "True" if value is True else "False" if value is False else str(value)

    md: List[str] = []
    md.append("# AI.Web Patch 228A Full Profile Adapter Verification")
    md.append("")
    md.append(f"Timestamp: `{timestamp}`")
    md.append(f"Verdict: **{report['verdict']}**")
    md.append("")
    md.append("## Boundary")
    md.append("- This patch independently verifies Forge's Identity Vault full-profile read-only adapter after Patch 228 and Patch 228A.1.")
    md.append("- It writes reports only under Forge memory.")
    md.append("- It does not write Identity Vault databases, create profiles, activate identities, read `.env` secret values, modify Forge registry, or write RMC memory.")
    md.append("")
    md.append("## Connector")
    md.append(f"- path: `{CONNECTOR_PATH}` exists=`{connector_info.get('exists')}`")
    md.append(f"- compile ok: `{connector_info.get('compile_ok')}`")
    md.append(f"- import ok: `{connector_info.get('import_ok')}`")
    md.append(f"- connector version from list: `{report['checks'].get('agent_list_connector_version')}`")
    md.append("")
    md.append("## Full Profile Checks")
    md.append(f"- agent list ok: `{report['checks'].get('agent_list_ok')}` read_only=`{report['checks'].get('agent_list_read_only')}` agents_returned=`{report['checks'].get('agents_returned')}`")
    md.append(f"- expected agents present: `{report['checks'].get('expected_agents_present')}`")
    for chk in show_checks:
        md.append(f"- `{chk.get('agent_id')}` found=`{chk.get('found')}` call_ok=`{chk.get('call_ok')}` activation_state=`{chk.get('activation_state')}` is_active=`{chk.get('is_active')}` hash_ok=`{chk.get('profile_hash_ok')}` hash_method=`{chk.get('profile_hash_method')}` payload_dumped=`{chk.get('payload_dumped')}` ok=`{chk.get('ok')}`")
    md.append(f"- all list profiles ok: `{report['checks'].get('all_list_profiles_ok')}`")
    md.append(f"- all show profiles ok: `{report['checks'].get('all_show_profiles_ok')}`")
    md.append("")
    md.append("## Identity / Boundary Commands")
    md.append(f"- forge_identity_status ok: `{report['checks'].get('identity_status_ok')}`")
    md.append(f"- forge_system_boundary_map ok: `{report['checks'].get('boundary_map_ok')}`")
    md.append(f"- identity_vault root exists: `{report['checks'].get('root_identity_vault_exists')}`")
    md.append(f"- rmc_wrappers root exists: `{report['checks'].get('root_rmc_wrappers_exists')}`")
    md.append("")
    md.append("## Database Read-Only Summary")
    md.append(f"- canonical: path=`{CANONICAL_DB}` ok=`{report['database']['canonical'].get('ok')}` opened_readonly=`{report['database']['canonical'].get('opened_readonly')}` rows=`{report['database']['canonical'].get('row_counts')}`")
    md.append(f"- legacy: path=`{LEGACY_DB}` ok=`{report['database']['legacy'].get('ok')}` opened_readonly=`{report['database']['legacy'].get('opened_readonly')}` rows=`{report['database']['legacy'].get('row_counts')}`")
    md.append("")
    md.append("## Safety Checks")
    for key, value in safety.items():
        md.append(f"- `{key}`: `{yesno(value)}`")
    md.append("")
    md.append("## Findings")
    for finding in report["findings"]:
        md.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    md.append("")
    if report["verdict"] == "PASS":
        md.append("## Next Safe Step")
        md.append("Move to Phase 4 planning: create Patch 229 as an RMC namespace scaffold preview only. Do not create folders or write memory yet.")
    else:
        md.append("## Next Safe Step")
        md.append("Do not move to RMC namespace scaffolding. Review failed fields in the JSON report first.")
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    latest_md = REPORT_ROOT / "latest_aiweb_patch228a_full_profile_adapter_verification.md"
    latest_json = REPORT_ROOT / "latest_aiweb_patch228a_full_profile_adapter_verification.json"
    latest_md.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
    latest_json.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")

    print("AI.Web Patch 228A full profile adapter verification complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"JSON report: {latest_json}")
    print(f"Verdict: {report['verdict']}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
