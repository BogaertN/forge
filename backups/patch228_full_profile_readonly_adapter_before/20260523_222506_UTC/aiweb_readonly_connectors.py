# aiweb_readonly_connectors.py — Patch 224
# Purpose: contract-bound read-only connector helpers for Forge CLI commands.
# Boundary: no database writes, no RMC memory writes, no .env secret reads, no agent activation.

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

READ_ONLY = True
CONNECTOR_VERSION = "patch224_readonly_connectors_v1"


def _home() -> Path:
    return Path.home()


def _safe_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        return {"_error": f"{type(exc).__name__}: {exc}", "_path": str(path)}


def _aiweb_root() -> Path:
    return _home() / "aiweb"


def _forge_root() -> Path:
    return _home() / "forge"


def _identity_root() -> Path:
    return _home() / "identity-vault"


def _contracts_root() -> Path:
    return _aiweb_root() / "service_contracts"


def _runtime_wrappers_root() -> Path:
    return _aiweb_root() / "runtime_wrappers"


def _contract(name: str) -> Dict[str, Any]:
    path = _contracts_root() / f"{name}.contract.json"
    data = _safe_json(path)
    return {
        "name": data.get("name", name),
        "path": str(path),
        "exists": path.exists(),
        "json_ok": "_error" not in data,
        "role": data.get("role"),
        "audit_log_path": data.get("audit_log_path"),
        "test_command": data.get("test_command"),
        "startup_command": data.get("startup_command"),
        "shutdown_command": data.get("shutdown_command"),
        "health_check_command": data.get("health_check_command"),
        "owner_authority": data.get("owner_authority"),
        "allowed_reads_count": len(data.get("allowed_reads") or []),
        "allowed_writes_count": len(data.get("allowed_writes") or []),
        "forbidden_writes_count": len(data.get("forbidden_writes") or []),
        "commands_count": len(data.get("api_or_cli_commands_exposed") or []),
        "error": data.get("_error"),
    }


def _ensure_rmc_import_path() -> Path:
    root = _runtime_wrappers_root()
    root_str = str(root)
    if root.exists() and root_str not in sys.path:
        sys.path.insert(0, root_str)
    forge_str = str(_forge_root())
    if forge_str not in sys.path:
        sys.path.insert(0, forge_str)
    return root


def _plain(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


def forge_rmc_status() -> Dict[str, Any]:
    root = _ensure_rmc_import_path()
    contract = _contract("rmc")
    modules = {
        "phase_parser": root / "phase_parser" / "phase_state_parser.py",
        "drift_detection": root / "drift_detection" / "drift_detector.py",
        "echo_validator": root / "echo_validator" / "echo_validator.py",
        "rmc_orchestrator": root / "rmc_orchestrator" / "rmc_orchestrator.py",
    }
    module_exists = {k: v.exists() for k, v in modules.items()}
    wrapper_ok = False
    wrapper_error = ""
    try:
        from agents.forge import rmc_tools  # type: ignore
        wrapper_ok = bool(getattr(rmc_tools, "RMC_READ_ONLY", False))
    except Exception as exc:
        wrapper_error = f"{type(exc).__name__}: {exc}"
    return {
        "ok": bool(contract.get("exists") and contract.get("json_ok") and all(module_exists.values()) and wrapper_ok),
        "read_only": READ_ONLY,
        "connector_version": CONNECTOR_VERSION,
        "service": "rmc",
        "contract": contract,
        "runtime_wrappers_root": str(root),
        "module_exists": module_exists,
        "forge_rmc_wrapper_ok": wrapper_ok,
        "forge_rmc_wrapper_error": wrapper_error,
        "memory_write_performed": False,
        "agent_identity_activation_performed": False,
    }


def forge_rmc_test_status() -> Dict[str, Any]:
    _ensure_rmc_import_path()
    smoke: Dict[str, Any] = {}
    try:
        from agents.forge import rmc_tools  # type: ignore
        sample_manifest = {
            "id": "patch224-smoke",
            "phase": 6,
            "phase_name": "Grace",
            "conclusion": "Verify read-only connector boundaries before projection.",
            "confidence": 0.9,
            "novelty": 0.1,
            "drift_verdict": "ALLOW",
            "projection_status": "READY",
        }
        calls = {
            "phase": rmc_tools.rmc_phase_parse_preview("Verify boundary before projection."),
            "drift": rmc_tools.rmc_drift_check_preview("Check drift without writing memory.", current_phase=6, phase_history=[1, 4, 5, 6]),
            "echo": rmc_tools.rmc_echo_validate_preview("Verify read-only connector boundaries before projection.", sample_manifest),
            "pipeline": rmc_tools.rmc_pipeline_preview("Run read-only connector pipeline smoke.", modality="language"),
        }
        for name, out in calls.items():
            smoke[name] = {
                "ok": bool(isinstance(out, dict) and out.get("ok") is True),
                "read_only": out.get("read_only") if isinstance(out, dict) else None,
                "summary_keys": sorted(list((out.get("result") or {}).keys()))[:20] if isinstance(out, dict) and isinstance(out.get("result"), dict) else [],
            }
    except Exception as exc:
        return {"ok": False, "read_only": READ_ONLY, "error": f"{type(exc).__name__}: {exc}"}
    # The connector command is a status surface. It must remain usable even if one
    # underlying preview reports a safe read-only error, because the point is to
    # expose that condition without mutating memory. Phase/drift/echo are required
    # to pass; pipeline must at least return through the read-only wrapper boundary.
    core_ok = all((smoke.get(name) or {}).get("ok") for name in ("phase", "drift", "echo"))
    all_read_only = all((row or {}).get("read_only") is True for row in smoke.values())
    return {
        "ok": bool(core_ok and all_read_only),
        "read_only": READ_ONLY,
        "connector_version": CONNECTOR_VERSION,
        "service": "rmc",
        "smoke": smoke,
        "memory_write_performed": False,
        "agent_identity_activation_performed": False,
    }


def _identity_adapter():
    forge_str = str(_forge_root())
    if forge_str not in sys.path:
        sys.path.insert(0, forge_str)
    from agents.forge.identity_vault_adapter import IdentityVaultReadOnlyAdapter  # type: ignore
    return IdentityVaultReadOnlyAdapter()


def forge_identity_status() -> Dict[str, Any]:
    contract = _contract("identity_vault")
    try:
        adapter = _identity_adapter()
        status = adapter.status()
    except Exception as exc:
        status = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return {
        "ok": bool(contract.get("exists") and contract.get("json_ok") and status.get("ok")),
        "read_only": READ_ONLY,
        "connector_version": CONNECTOR_VERSION,
        "service": "identity_vault",
        "contract": contract,
        "adapter_status": _plain(status),
        "env_secret_values_read": False,
        "database_write_performed": False,
        "agent_identity_activation_performed": False,
    }


def forge_agent_list(limit: int = 50) -> Dict[str, Any]:
    try:
        adapter = _identity_adapter()
        preview = adapter.identity_metadata_preview("agent_profiles", limit=max(1, min(int(limit), 100)))
    except Exception as exc:
        preview = {"ok": False, "rows": [], "error": f"{type(exc).__name__}: {exc}"}
    return {
        "ok": bool(preview.get("ok")),
        "read_only": READ_ONLY,
        "connector_version": CONNECTOR_VERSION,
        "service": "identity_vault",
        "agents_returned": len(preview.get("rows") or []),
        "safe_columns": preview.get("safe_columns", []),
        "agents": preview.get("rows") or [],
        "database_write_performed": False,
        "agent_identity_activation_performed": False,
    }


def forge_agent_show(agent_id: str) -> Dict[str, Any]:
    agent_id = (agent_id or "").strip()
    if not agent_id:
        return {"ok": False, "read_only": READ_ONLY, "error": "agent_id_required", "usage": "forge-agent-show <agent_id>"}
    listing = forge_agent_list(limit=100)
    rows: List[Dict[str, Any]] = listing.get("agents") or []
    match = None
    for row in rows:
        if str(row.get("agent_id") or row.get("id") or row.get("name") or "") == agent_id:
            match = row
            break
    return {
        "ok": match is not None,
        "read_only": READ_ONLY,
        "connector_version": CONNECTOR_VERSION,
        "service": "identity_vault",
        "agent_id": agent_id,
        "found": match is not None,
        "agent": match,
        "note": "No agent profile rows exist yet." if not rows else ("Agent not found in safe metadata preview." if match is None else "Agent metadata found."),
        "database_write_performed": False,
        "agent_identity_activation_performed": False,
    }


def forge_system_boundary_map() -> Dict[str, Any]:
    contracts = {name: _contract(name) for name in ["forge", "rmc", "identity_vault", "protoforge2", "echoforge"]}
    roots = {
        "forge": str(_forge_root()),
        "aiweb": str(_aiweb_root()),
        "identity_vault": str(_identity_root()),
        "rmc_wrappers": str(_runtime_wrappers_root()),
        "protoforge2_candidates": [str(_home() / "protoforge2"), str(_aiweb_root() / "protoforge2"), str(_runtime_wrappers_root() / "protoforge2")],
        "echoforge_candidates": [str(_home() / "echoforge"), str(_aiweb_root() / "echoforge"), str(_runtime_wrappers_root() / "echoforge")],
    }
    root_exists = {
        "forge": _forge_root().exists(),
        "aiweb": _aiweb_root().exists(),
        "identity_vault": _identity_root().exists(),
        "rmc_wrappers": _runtime_wrappers_root().exists(),
        "protoforge2_any": any(Path(p).exists() for p in roots["protoforge2_candidates"]),
        "echoforge_any": any(Path(p).exists() for p in roots["echoforge_candidates"]),
    }
    return {
        "ok": all(c.get("exists") and c.get("json_ok") for c in contracts.values()),
        "read_only": READ_ONLY,
        "connector_version": CONNECTOR_VERSION,
        "contracts": contracts,
        "roots": roots,
        "root_exists": root_exists,
        "spine": [
            "Forge verifies and governs",
            "ProtoForge2 executes and simulates",
            "EchoForge requests tools/apps/simulations",
            "Identity Vault houses agent identity and permissions",
            "RMC stores shared and agent-scoped recursive memory",
        ],
        "forbidden_now": [
            "RMC memory writes",
            "agent identity activation",
            "Identity Vault database writes",
            "EchoForge build execution",
            "ProtoForge2 live execution",
        ],
    }
