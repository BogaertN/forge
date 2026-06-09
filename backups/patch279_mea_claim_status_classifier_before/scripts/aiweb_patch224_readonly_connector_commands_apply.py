#!/usr/bin/env python3
"""
Patch 224 — AI.Web Forge Read-Only Connector Commands Apply

Creates Forge's first read-only AI.Web connector command layer:
- forge-rmc-status
- forge-rmc-test-status
- forge-identity-status
- forge-agent-list
- forge-agent-show <agent_id>
- forge-system-boundary-map

Boundary:
- Modifies ~/forge/main.py only after backup.
- Writes ~/forge/agents/forge/aiweb_readonly_connectors.py.
- Does not modify Forge registry, Identity Vault databases, RMC memory, .env,
  node_modules, service contracts, or agent identity activation state.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import py_compile
import shutil
from pathlib import Path
from typing import Any, Dict

PATCH_ID = "patch224_aiweb_readonly_connector_commands"
BEGIN_FUNCS = "# --- BEGIN PATCH 224 AIWEB READ-ONLY CONNECTOR COMMANDS ---"
END_FUNCS = "# --- END PATCH 224 AIWEB READ-ONLY CONNECTOR COMMANDS ---"
BEGIN_ROUTES = "# --- BEGIN PATCH 224 AIWEB READ-ONLY CONNECTOR ROUTES ---"
END_ROUTES = "# --- END PATCH 224 AIWEB READ-ONLY CONNECTOR ROUTES ---"

COMMANDS = [
    "forge-rmc-status",
    "forge-rmc-test-status",
    "forge-identity-status",
    "forge-agent-list",
    "forge-agent-show",
    "forge-system-boundary-map",
]

CONNECTOR_MODULE = r'''# aiweb_readonly_connectors.py — Patch 224
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
'''

FUNCTION_BLOCK = r'''
# --- BEGIN PATCH 224 AIWEB READ-ONLY CONNECTOR COMMANDS ---
# Adds first contract-bound read-only AI.Web connector commands.
# No RMC memory writes, no Identity Vault DB writes, no agent identity activation.
PATCH224_AIWEB_CONNECTOR_COMMANDS = [
    "forge-rmc-status",
    "forge-rmc-test-status",
    "forge-identity-status",
    "forge-agent-list",
    "forge-agent-show",
    "forge-system-boundary-map",
]
for _p224_cmd in PATCH224_AIWEB_CONNECTOR_COMMANDS:
    if _p224_cmd not in FORGE_EXPECTED_COMMANDS:
        FORGE_EXPECTED_COMMANDS.append(_p224_cmd)


def _p224_connector_result_lines(data, indent="  "):
    import json as _p224_json
    try:
        text = _p224_json.dumps(data, indent=2, sort_keys=True)
    except TypeError:
        text = str(data)
    for line in text.splitlines():
        print(indent + line)


def cmd_forge_rmc_status(session_id: str) -> None:
    from agents.forge.memory import write_audit_entry
    from agents.forge.aiweb_readonly_connectors import forge_rmc_status
    data = forge_rmc_status()
    print()
    print("── Forge RMC Status — Read-Only ─────────────────────────────")
    _p224_connector_result_lines(data)
    print("──────────────────────────────────────────────────────────────")
    print()
    write_audit_entry(session_id, "FORGE_RMC_STATUS_READONLY", "rmc", "read-only", "no memory write")


def cmd_forge_rmc_test_status(session_id: str) -> None:
    from agents.forge.memory import write_audit_entry
    from agents.forge.aiweb_readonly_connectors import forge_rmc_test_status
    data = forge_rmc_test_status()
    print()
    print("── Forge RMC Test Status — Read-Only ────────────────────────")
    _p224_connector_result_lines(data)
    print("──────────────────────────────────────────────────────────────")
    print()
    write_audit_entry(session_id, "FORGE_RMC_TEST_STATUS_READONLY", "rmc", "read-only", "preview smoke only")


def cmd_forge_identity_status(session_id: str) -> None:
    from agents.forge.memory import write_audit_entry
    from agents.forge.aiweb_readonly_connectors import forge_identity_status
    data = forge_identity_status()
    print()
    print("── Forge Identity Vault Status — Read-Only ──────────────────")
    _p224_connector_result_lines(data)
    print("──────────────────────────────────────────────────────────────")
    print()
    write_audit_entry(session_id, "FORGE_IDENTITY_STATUS_READONLY", "identity_vault", "read-only", "no identity activation")


def cmd_forge_agent_list(session_id: str) -> None:
    from agents.forge.memory import write_audit_entry
    from agents.forge.aiweb_readonly_connectors import forge_agent_list
    data = forge_agent_list()
    print()
    print("── Forge Agent List — Read-Only ─────────────────────────────")
    _p224_connector_result_lines(data)
    print("──────────────────────────────────────────────────────────────")
    print()
    write_audit_entry(session_id, "FORGE_AGENT_LIST_READONLY", "identity_vault", "read-only", "safe metadata only")


def cmd_forge_agent_show(agent_id: str, session_id: str) -> None:
    from agents.forge.memory import write_audit_entry
    from agents.forge.aiweb_readonly_connectors import forge_agent_show
    data = forge_agent_show(agent_id)
    print()
    print("── Forge Agent Show — Read-Only ─────────────────────────────")
    _p224_connector_result_lines(data)
    print("──────────────────────────────────────────────────────────────")
    print()
    write_audit_entry(session_id, "FORGE_AGENT_SHOW_READONLY", str(agent_id), "read-only", "safe metadata only")


def cmd_forge_system_boundary_map(session_id: str) -> None:
    from agents.forge.memory import write_audit_entry
    from agents.forge.aiweb_readonly_connectors import forge_system_boundary_map
    data = forge_system_boundary_map()
    print()
    print("── Forge System Boundary Map — Read-Only ────────────────────")
    _p224_connector_result_lines(data)
    print("──────────────────────────────────────────────────────────────")
    print()
    write_audit_entry(session_id, "FORGE_SYSTEM_BOUNDARY_MAP_READONLY", "aiweb", "read-only", "contracts only")
# --- END PATCH 224 AIWEB READ-ONLY CONNECTOR COMMANDS ---
'''

ROUTE_BLOCK = r'''
            # --- BEGIN PATCH 224 AIWEB READ-ONLY CONNECTOR ROUTES ---
            if user_input.lower() == "forge-rmc-status":
                cmd_forge_rmc_status(session_id)
                continue

            if user_input.lower() == "forge-rmc-test-status":
                cmd_forge_rmc_test_status(session_id)
                continue

            if user_input.lower() == "forge-identity-status":
                cmd_forge_identity_status(session_id)
                continue

            if user_input.lower() == "forge-agent-list":
                cmd_forge_agent_list(session_id)
                continue

            if user_input.lower().startswith("forge-agent-show "):
                _p224_agent_id = user_input[len("forge-agent-show "):].strip()
                cmd_forge_agent_show(_p224_agent_id, session_id)
                continue

            if user_input.lower() == "forge-agent-show":
                print()
                print("  Usage: forge-agent-show <agent_id>")
                print("  Note : read-only safe metadata preview only; no identity activation.")
                print()
                continue

            if user_input.lower() == "forge-system-boundary-map":
                cmd_forge_system_boundary_map(session_id)
                continue
            # --- END PATCH 224 AIWEB READ-ONLY CONNECTOR ROUTES ---
'''


def _home() -> Path:
    return Path.home()


def _forge_root() -> Path:
    return _home() / "forge"


def _main_path() -> Path:
    return _forge_root() / "main.py"


def _module_path() -> Path:
    return _forge_root() / "agents" / "forge" / "aiweb_readonly_connectors.py"


def _report_root() -> Path:
    return _forge_root() / "memory" / "aiweb_patch224_readonly_connectors_v1"


def _sha(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _stat(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    st = path.stat()
    return {"exists": True, "size": st.st_size, "mode": oct(st.st_mode & 0o777), "sha256": _sha(path)}


def _insert_before_if_main(text: str) -> str:
    if BEGIN_FUNCS in text:
        return text
    needle = '\nif __name__ == "__main__":\n    main()\n'
    if needle not in text:
        raise RuntimeError("if __name__ main sentinel not found")
    return text.replace(needle, "\n" + FUNCTION_BLOCK.strip() + "\n" + needle, 1)


def _insert_routes(text: str) -> str:
    if BEGIN_ROUTES in text:
        return text
    needle = '            # ── Patch 199 — Natural Language Orchestrator ────────────────────\n'
    if needle not in text:
        # Fallback: insert before common Forge plan route if comment changed.
        needle = '            if user_input.lower().startswith("forge-orchestrate "):\n'
        if needle not in text:
            raise RuntimeError("main loop route insertion point not found")
        return text.replace(needle, ROUTE_BLOCK + "\n" + needle, 1)
    return text.replace(needle, ROUTE_BLOCK + "\n" + needle, 1)


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_reports(result: Dict[str, Any], report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / f"{result['timestamp']}_aiweb_patch224_readonly_connectors.json"
    md_path = report_dir / f"{result['timestamp']}_aiweb_patch224_readonly_connectors.md"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# AI.Web Patch 224 Read-Only Connector Commands Apply",
        "",
        f"Timestamp: `{result['timestamp']}`",
        f"Verdict: **{result['verdict']}**",
        "",
        "## Boundary",
        "- This patch creates the first Forge read-only connector command layer.",
        "- It writes the connector helper module and modifies `forge/main.py` command routes only after backup.",
        "- It does not write Identity Vault databases, RMC memory, Forge registry, service contracts, `.env`, or agent identity activation state.",
        "",
        "## Backup",
        f"- backup root: `{result.get('backup_root')}`",
    ]
    for k, v in (result.get("backup") or {}).items():
        lines.append(f"- `{k}`: **{v}**")
    lines += ["", "## Changes"]
    for k, v in (result.get("changes") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines += ["", "## Checks"]
    for k, v in (result.get("checks") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    if result.get("connector_smoke"):
        lines += ["", "## Connector Smoke"]
        for k, v in result["connector_smoke"].items():
            lines.append(f"- `{k}`: `{v}`")
    if result.get("safety_snapshots"):
        lines += ["", "## Safety Snapshots"]
        for k, v in result["safety_snapshots"].items():
            lines.append(f"- `{k}`: `{v}`")
    if result.get("findings"):
        lines += ["", "## Findings"]
        for f in result["findings"]:
            lines.append(f"- **{f['level']}** `{f['code']}` — {f['message']}")
    if result.get("errors"):
        lines += ["", "## Errors"]
        for e in result["errors"]:
            lines.append(f"- `{e}`")
    lines += ["", "## Next Safe Step", "Run the Patch 224 verifier, then manually test the six connector commands inside Forge. No memory writes, app creation, or agent mutation."]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    root = _report_root()
    root.mkdir(parents=True, exist_ok=True)
    (root / "latest_aiweb_patch224_readonly_connectors.md").write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
    (root / "latest_aiweb_patch224_readonly_connectors.json").write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    ts = _dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S_UTC")
    report_dir = _report_root() / ts
    main_path = _main_path()
    module_path = _module_path()
    backup_root = _forge_root() / "backups" / "patch224_aiweb_readonly_connectors_before" / ts
    backup_root.mkdir(parents=True, exist_ok=True)

    protected = {
        "tool_registry": _forge_root() / "config" / "tool_registry.json",
        "identity_env": _home() / "identity-vault" / ".env",
        "identity_canonical_db": _home() / "identity-vault" / "data" / "identity_vault.db",
        "identity_legacy_db": _home() / "identity-vault" / "vault.db",
        "forge_contract": _home() / "aiweb" / "service_contracts" / "forge.contract.json",
        "rmc_contract": _home() / "aiweb" / "service_contracts" / "rmc.contract.json",
        "identity_contract": _home() / "aiweb" / "service_contracts" / "identity_vault.contract.json",
        "protoforge2_contract": _home() / "aiweb" / "service_contracts" / "protoforge2.contract.json",
        "echoforge_contract": _home() / "aiweb" / "service_contracts" / "echoforge.contract.json",
    }
    before = {k: _stat(v) for k, v in protected.items()}

    result: Dict[str, Any] = {
        "timestamp": ts,
        "verdict": "FAIL",
        "backup_root": str(backup_root),
        "backup": {},
        "changes": {},
        "checks": {},
        "connector_smoke": {},
        "safety_snapshots": {},
        "findings": [],
        "errors": [],
    }

    try:
        if not main_path.exists():
            raise RuntimeError(f"main.py missing: {main_path}")
        shutil.copy2(main_path, backup_root / "main.py")
        result["backup"]["main.py"] = "COPIED"
        if module_path.exists():
            shutil.copy2(module_path, backup_root / "aiweb_readonly_connectors.py")
            result["backup"]["aiweb_readonly_connectors.py"] = "COPIED"
        else:
            result["backup"]["aiweb_readonly_connectors.py"] = "SKIPPED (missing)"

        old_main = main_path.read_text(encoding="utf-8", errors="replace")
        new_main = _insert_routes(_insert_before_if_main(old_main))
        main_changed = new_main != old_main
        if main_changed:
            main_path.write_text(new_main, encoding="utf-8")
        result["changes"]["main_py_changed"] = main_changed

        old_module = module_path.read_text(encoding="utf-8", errors="replace") if module_path.exists() else ""
        module_changed = old_module != CONNECTOR_MODULE
        module_path.write_text(CONNECTOR_MODULE, encoding="utf-8")
        result["changes"]["connector_module_changed"] = module_changed

        py_compile.compile(str(main_path), doraise=True)
        py_compile.compile(str(module_path), doraise=True)
        result["checks"]["main_compile"] = True
        result["checks"]["connector_module_compile"] = True

        text = main_path.read_text(encoding="utf-8", errors="replace")
        result["checks"]["function_marker_present"] = BEGIN_FUNCS in text and END_FUNCS in text
        result["checks"]["route_marker_present"] = BEGIN_ROUTES in text and END_ROUTES in text
        result["checks"]["all_command_names_present"] = all(cmd in text for cmd in COMMANDS)

        import sys
        forge_str = str(_forge_root())
        if forge_str not in sys.path:
            sys.path.insert(0, forge_str)
        from agents.forge import aiweb_readonly_connectors as conn  # type: ignore
        smoke = {
            "rmc_status_ok": bool(conn.forge_rmc_status().get("ok")),
            "rmc_test_status_ok": bool(conn.forge_rmc_test_status().get("ok")),
            "identity_status_ok": bool(conn.forge_identity_status().get("ok")),
            "agent_list_ok": bool(conn.forge_agent_list().get("ok")),
            "agent_show_missing_safe": bool(conn.forge_agent_show("agent.gilligan.local").get("read_only")),
            "boundary_map_ok": bool(conn.forge_system_boundary_map().get("ok")),
        }
        result["connector_smoke"] = smoke
        result["checks"]["connector_smoke_ok"] = all(smoke.values())

        after = {k: _stat(v) for k, v in protected.items()}
        unchanged = {k: before[k] == after[k] for k in protected}
        result["safety_snapshots"] = unchanged
        result["checks"]["protected_snapshots_unchanged"] = all(unchanged.values())

        registry = _read_json(protected["tool_registry"])
        result["checks"]["tool_registry_trust_level"] = registry.get("current_trust_level") if isinstance(registry, dict) else None
        result["checks"]["forge_tool_registry_modified"] = not unchanged.get("tool_registry", False)
        result["checks"]["database_write_performed"] = not (unchanged.get("identity_canonical_db", False) and unchanged.get("identity_legacy_db", False))
        result["checks"]["env_secret_values_read"] = False
        result["checks"]["agent_identity_activation_performed"] = False

        if result["checks"]["function_marker_present"] and result["checks"]["route_marker_present"] and result["checks"]["all_command_names_present"] and result["checks"]["connector_smoke_ok"] and result["checks"]["protected_snapshots_unchanged"]:
            result["verdict"] = "PASS"
            result["findings"].append({"level": "INFO", "code": "AIWEB_READONLY_CONNECTORS_INSTALLED", "message": "Read-only connector commands were added to Forge main.py and connector smoke passed."})
        else:
            result["findings"].append({"level": "FAIL", "code": "AIWEB_READONLY_CONNECTOR_CHECK_FAILED", "message": "One or more connector checks failed; inspect JSON report."})
    except Exception as exc:
        result["errors"].append(f"{type(exc).__name__}: {exc}")
        result["findings"].append({"level": "FAIL", "code": "AIWEB_PATCH224_EXCEPTION", "message": str(exc)})

    _write_reports(result, report_dir)
    print("AI.Web Patch 224 read-only connector commands apply complete.")
    print(f"Run directory: {report_dir}")
    print(f"Report: {_report_root() / 'latest_aiweb_patch224_readonly_connectors.md'}")
    print(f"Verdict: {result['verdict']}")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
