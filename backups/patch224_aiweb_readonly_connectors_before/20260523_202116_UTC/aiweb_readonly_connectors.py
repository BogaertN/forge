# aiweb_readonly_connectors.py — Patch 224
"""
Forge-side AI.Web read-only connector module.

Boundary:
- Read-only helper functions only.
- No Forge command registration in this patch.
- No Identity Vault database writes.
- No RMC memory writes.
- No agent identity activation.
- No .env secret reads.

These functions are intended to be registered later as Forge commands:
- forge-rmc-status
- forge-rmc-test-status
- forge-identity-status
- forge-agent-list
- forge-agent-show <agent_id>
- forge-system-boundary-map
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


CONNECTOR_VERSION = "0.1.0-readonly-staged"
READ_ONLY = True

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
AIWEB_ROOT = HOME / "aiweb"
IDENTITY_VAULT_ROOT = HOME / "identity-vault"
CONTRACT_ROOT = AIWEB_ROOT / "service_contracts"
RMC_WRAPPERS_ROOT = AIWEB_ROOT / "runtime_wrappers"
FORGE_AGENT_ROOT = FORGE_ROOT / "agents" / "forge"
IDENTITY_CONTRACT_DRAFT = IDENTITY_VAULT_ROOT / "service_contracts" / "identity_vault_readonly_service_contract.draft.json"
CANONICAL_IDENTITY_DB = IDENTITY_VAULT_ROOT / "data" / "identity_vault.db"
LEGACY_IDENTITY_DB = IDENTITY_VAULT_ROOT / "vault.db"

CONTRACT_FILES = {
    "forge": CONTRACT_ROOT / "forge.contract.json",
    "rmc": CONTRACT_ROOT / "rmc.contract.json",
    "identity_vault": CONTRACT_ROOT / "identity_vault.contract.json",
    "protoforge2": CONTRACT_ROOT / "protoforge2.contract.json",
    "echoforge": CONTRACT_ROOT / "echoforge.contract.json",
}

REQUIRED_CONTRACT_FIELDS = [
    "name",
    "role",
    "allowed_reads",
    "allowed_writes",
    "forbidden_writes",
    "api_or_cli_commands_exposed",
    "audit_log_path",
    "test_command",
    "startup_command",
    "shutdown_command",
    "health_check_command",
    "owner_authority",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def _safe_load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        return {"__error__": str(exc), "__path__": str(path)}


def _contract_status(name: str) -> Dict[str, Any]:
    path = CONTRACT_FILES[name]
    data = _safe_load_json(path) if path.exists() else {}
    missing = []
    if not data.get("__error__"):
        missing = [field for field in REQUIRED_CONTRACT_FIELDS if field not in data]
    return {
        "name": name,
        "path": str(path),
        "exists": path.exists(),
        "json_ok": bool(path.exists() and not data.get("__error__")),
        "missing_fields": missing,
        "contract_name": data.get("name"),
        "role": data.get("role"),
        "allowed_reads_count": len(data.get("allowed_reads", [])) if isinstance(data.get("allowed_reads"), list) else None,
        "allowed_writes_count": len(data.get("allowed_writes", [])) if isinstance(data.get("allowed_writes"), list) else None,
        "forbidden_writes_count": len(data.get("forbidden_writes", [])) if isinstance(data.get("forbidden_writes"), list) else None,
        "commands_count": len(data.get("api_or_cli_commands_exposed", [])) if isinstance(data.get("api_or_cli_commands_exposed"), list) else None,
        "audit_log_path": data.get("audit_log_path"),
        "health_check_command": data.get("health_check_command"),
        "owner_authority": data.get("owner_authority"),
        "error": data.get("__error__"),
    }


def _readonly_sqlite_summary(db_path: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "path": str(db_path),
        "exists": db_path.exists(),
        "opened_readonly": False,
        "ok": False,
        "tables": [],
        "row_counts": {},
        "error": None,
    }
    if not db_path.exists():
        result["error"] = "database_missing"
        return result
    try:
        uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        result["opened_readonly"] = True
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cur.fetchall()]
        result["tables"] = tables
        for table in tables:
            try:
                cur.execute(f'SELECT COUNT(*) FROM "{table}"')
                result["row_counts"][table] = int(cur.fetchone()[0])
            except Exception as exc:
                result["row_counts"][table] = f"ERROR: {exc}"
        conn.close()
        result["ok"] = True
    except Exception as exc:
        result["error"] = str(exc)
    return result


def _safe_agent_columns(db_path: Path, agent_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "db_path": str(db_path),
        "ok": False,
        "opened_readonly": False,
        "requested_agent_id": agent_id,
        "safe_columns": ["id", "agent_id", "role", "created_at", "updated_at"],
        "rows": [],
        "error": None,
    }
    if not db_path.exists():
        result["error"] = "database_missing"
        return result
    try:
        uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        result["opened_readonly"] = True
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agent_profiles'")
        if not cur.fetchone():
            result["error"] = "agent_profiles_missing"
            conn.close()
            return result

        cur.execute("PRAGMA table_info(agent_profiles)")
        existing_cols = {row[1] for row in cur.fetchall()}
        safe_cols = [col for col in result["safe_columns"] if col in existing_cols]
        result["safe_columns"] = safe_cols
        if not safe_cols:
            result["error"] = "no_safe_columns_available"
            conn.close()
            return result

        quoted_cols = ", ".join(f'"{col}"' for col in safe_cols)
        if agent_id:
            cur.execute(f'SELECT {quoted_cols} FROM agent_profiles WHERE agent_id = ? LIMIT 1', (agent_id,))
        else:
            cur.execute(f'SELECT {quoted_cols} FROM agent_profiles ORDER BY agent_id LIMIT ?', (int(limit),))
        result["rows"] = [dict(row) for row in cur.fetchall()]
        result["ok"] = True
        conn.close()
    except Exception as exc:
        result["error"] = str(exc)
    return result


def _latest_report_summary(glob_pattern: str) -> Dict[str, Any]:
    matches = sorted(FORGE_ROOT.glob(glob_pattern), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    if not matches:
        return {"found": False, "path": None, "first_lines": []}
    path = matches[0]
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        first_lines = text.splitlines()[:12]
    except Exception as exc:
        first_lines = [f"ERROR_READING_REPORT: {exc}"]
    return {"found": True, "path": str(path), "first_lines": first_lines}


def forge_rmc_status() -> Dict[str, Any]:
    """Read-only status for RMC wrapper/module boundary."""
    modules = [
        "phase_parser",
        "phase_state_parser",
        "drift_detection",
        "drift_arbitrator",
        "echo_validator",
        "echo_gate",
        "ancestral_memory",
        "manifest_compiler",
        "output_renderer",
        "rmc_orchestrator",
    ]
    module_status = {name: (RMC_WRAPPERS_ROOT / name).exists() for name in modules}
    return {
        "function": "forge_rmc_status",
        "ok": all(module_status.values()),
        "read_only": True,
        "connector_version": CONNECTOR_VERSION,
        "contract": _contract_status("rmc"),
        "wrappers_root": str(RMC_WRAPPERS_ROOT),
        "module_status": module_status,
        "forge_rmc_tools_file_exists": (FORGE_AGENT_ROOT / "rmc_tools.py").exists(),
        "timestamp": _now(),
    }


def forge_rmc_test_status() -> Dict[str, Any]:
    """Read-only summary of recent RMC verification reports."""
    return {
        "function": "forge_rmc_test_status",
        "ok": True,
        "read_only": True,
        "connector_version": CONNECTOR_VERSION,
        "reports": {
            "patch209_integrated": _latest_report_summary("memory/rmc_patch209_integrated_verify_v1/latest*.md"),
            "patch211_wrapper": _latest_report_summary("memory/rmc_patch211_readonly_wrapper_v1/latest*.md"),
            "patch212_registration": _latest_report_summary("memory/rmc_patch212_tool_registration_verify_v1/latest*.md"),
            "patch213_runtime_preview": _latest_report_summary("memory/rmc_patch213_forge_runtime_preview_v1/latest*.md"),
        },
        "timestamp": _now(),
    }


def forge_identity_status() -> Dict[str, Any]:
    """Read-only status for Identity Vault contract/DB boundary."""
    contract_status = _contract_status("identity_vault")
    draft = _safe_load_json(IDENTITY_CONTRACT_DRAFT) if IDENTITY_CONTRACT_DRAFT.exists() else {}
    canonical_summary = _readonly_sqlite_summary(CANONICAL_IDENTITY_DB)
    return {
        "function": "forge_identity_status",
        "ok": bool(contract_status.get("json_ok") and canonical_summary.get("ok")),
        "read_only": True,
        "connector_version": CONNECTOR_VERSION,
        "contract": contract_status,
        "draft_contract_exists": IDENTITY_CONTRACT_DRAFT.exists(),
        "draft_contract_status": draft.get("status"),
        "canonical_db": canonical_summary,
        "legacy_db_exists": LEGACY_IDENTITY_DB.exists(),
        "env_exists": (IDENTITY_VAULT_ROOT / ".env").exists(),
        "env_secret_values_read": False,
        "timestamp": _now(),
    }


def forge_agent_list(limit: int = 50) -> Dict[str, Any]:
    """Read-only safe-column preview of registered agent profiles."""
    agents = _safe_agent_columns(CANONICAL_IDENTITY_DB, limit=limit)
    return {
        "function": "forge_agent_list",
        "ok": agents.get("ok", False),
        "read_only": True,
        "connector_version": CONNECTOR_VERSION,
        "returned": len(agents.get("rows", [])),
        "agents": agents.get("rows", []),
        "safe_columns": agents.get("safe_columns", []),
        "error": agents.get("error"),
        "agent_identity_activation_performed": False,
        "timestamp": _now(),
    }


def forge_agent_show(agent_id: str) -> Dict[str, Any]:
    """Read-only safe-column preview of one agent profile by agent_id."""
    agent_id = (agent_id or "").strip()
    if not agent_id:
        return {
            "function": "forge_agent_show",
            "ok": False,
            "read_only": True,
            "error": "agent_id_required",
            "agent_identity_activation_performed": False,
            "timestamp": _now(),
        }
    agents = _safe_agent_columns(CANONICAL_IDENTITY_DB, agent_id=agent_id, limit=1)
    rows = agents.get("rows", [])
    return {
        "function": "forge_agent_show",
        "ok": bool(agents.get("ok") and rows),
        "read_only": True,
        "connector_version": CONNECTOR_VERSION,
        "agent_id": agent_id,
        "found": bool(rows),
        "agent": rows[0] if rows else None,
        "safe_columns": agents.get("safe_columns", []),
        "error": agents.get("error"),
        "agent_identity_activation_performed": False,
        "timestamp": _now(),
    }


def forge_system_boundary_map() -> Dict[str, Any]:
    """Read-only system boundary map from service contracts and known roots."""
    contracts = {name: _contract_status(name) for name in CONTRACT_FILES}
    roots = {
        "forge": {"path": str(FORGE_ROOT), "exists": FORGE_ROOT.exists()},
        "aiweb": {"path": str(AIWEB_ROOT), "exists": AIWEB_ROOT.exists()},
        "identity_vault": {"path": str(IDENTITY_VAULT_ROOT), "exists": IDENTITY_VAULT_ROOT.exists()},
        "rmc_wrappers": {"path": str(RMC_WRAPPERS_ROOT), "exists": RMC_WRAPPERS_ROOT.exists()},
        "protoforge2_candidates": [
            {"path": str(HOME / "protoforge2"), "exists": (HOME / "protoforge2").exists()},
            {"path": str(AIWEB_ROOT / "protoforge2"), "exists": (AIWEB_ROOT / "protoforge2").exists()},
            {"path": str(RMC_WRAPPERS_ROOT / "protoforge2"), "exists": (RMC_WRAPPERS_ROOT / "protoforge2").exists()},
        ],
        "echoforge_candidates": [
            {"path": str(HOME / "echoforge"), "exists": (HOME / "echoforge").exists()},
            {"path": str(AIWEB_ROOT / "echoforge"), "exists": (AIWEB_ROOT / "echoforge").exists()},
            {"path": str(RMC_WRAPPERS_ROOT / "echoforge"), "exists": (RMC_WRAPPERS_ROOT / "echoforge").exists()},
        ],
    }
    return {
        "function": "forge_system_boundary_map",
        "ok": all(c.get("json_ok") and not c.get("missing_fields") for c in contracts.values()),
        "read_only": True,
        "connector_version": CONNECTOR_VERSION,
        "contracts": contracts,
        "roots": roots,
        "spine": [
            "Forge verifies and governs.",
            "ProtoForge2 executes and simulates.",
            "EchoForge requests tools/apps/simulations.",
            "Identity Vault houses agent identity and permissions.",
            "RMC stores shared and agent-scoped recursive memory.",
        ],
        "no_memory_writes": True,
        "no_app_creation": True,
        "no_agent_mutation": True,
        "timestamp": _now(),
    }


CONNECTOR_FUNCTIONS = {
    "forge-rmc-status": forge_rmc_status,
    "forge-rmc-test-status": forge_rmc_test_status,
    "forge-identity-status": forge_identity_status,
    "forge-agent-list": forge_agent_list,
    "forge-agent-show": forge_agent_show,
    "forge-system-boundary-map": forge_system_boundary_map,
}


def run_connector_preview(command: str, *args: str) -> Dict[str, Any]:
    """Preview dispatcher for later Forge command registration."""
    fn = CONNECTOR_FUNCTIONS.get(command)
    if not fn:
        return {
            "function": "run_connector_preview",
            "ok": False,
            "read_only": True,
            "error": f"unknown_connector_command: {command}",
            "known": sorted(CONNECTOR_FUNCTIONS.keys()),
            "timestamp": _now(),
        }
    if command == "forge-agent-show":
        return fn(args[0] if args else "")
    return fn()


__all__ = [
    "CONNECTOR_VERSION",
    "READ_ONLY",
    "CONNECTOR_FUNCTIONS",
    "run_connector_preview",
    "forge_rmc_status",
    "forge_rmc_test_status",
    "forge_identity_status",
    "forge_agent_list",
    "forge_agent_show",
    "forge_system_boundary_map",
]
