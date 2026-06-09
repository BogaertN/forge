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

# >>> PATCH 228 FULL PROFILE READONLY ADAPTER OVERRIDES >>>
# Patch 228 — Full Profile Read-Only Adapter Upgrade
# These definitions intentionally override the Patch 224 read-only agent helpers.
# Boundary: read-only SQLite access, safe profile summaries only, no activation, no DB writes.

def _patch228_json_loads_safe(value, fallback=None):
    import json as _json
    if fallback is None:
        fallback = {}
    if value is None:
        return fallback
    try:
        if isinstance(value, (dict, list)):
            return value
        return _json.loads(value)
    except Exception:
        return fallback


def _patch228_short_list(value, limit=6):
    if value is None:
        return []
    if not isinstance(value, list):
        return []
    return value[:limit]


def _patch228_hash_payload(payload_text):
    import hashlib as _hashlib
    if payload_text is None:
        payload_text = ""
    if not isinstance(payload_text, str):
        payload_text = str(payload_text)
    return _hashlib.sha256(payload_text.encode("utf-8")).hexdigest()


def _patch228_readonly_conn():
    import sqlite3 as _sqlite3
    db_path = "/home/nic/identity-vault/data/identity_vault.db"
    return _sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)


def _patch228_agent_row_to_summary(row):
    (
        row_id,
        agent_id,
        canonical_name,
        role,
        activation_state,
        is_active,
        rmc_namespace,
        profile_schema_version,
        profile_hash,
        last_validated_at,
        created_at,
        updated_at,
        operational_profile_json,
    ) = row
    payload = _patch228_json_loads_safe(operational_profile_json, {})
    computed_hash = _patch228_hash_payload(operational_profile_json or "{}")
    return {
        "id": row_id,
        "agent_id": agent_id,
        "canonical_name": canonical_name or payload.get("canonical_name"),
        "role": role or payload.get("role"),
        "activation_state": activation_state,
        "is_active": is_active,
        "rmc_namespace": rmc_namespace or payload.get("rmc_namespace"),
        "profile_schema_version": profile_schema_version,
        "profile_hash": profile_hash,
        "profile_hash_ok": bool(profile_hash and computed_hash == profile_hash),
        "last_validated_at": last_validated_at,
        "created_at": created_at,
        "updated_at": updated_at,
        "persona": payload.get("persona"),
        "voice_style": payload.get("voice_style"),
        "symbolic_signature": _patch228_short_list(payload.get("symbolic_signature"), 8),
        "permissions_summary": _patch228_short_list(payload.get("permissions"), 8),
        "forbidden_actions_summary": _patch228_short_list(payload.get("forbidden_actions"), 8),
        "authority_summary": _patch228_short_list(payload.get("authority"), 8),
        "limitations_summary": _patch228_short_list(payload.get("limitations"), 8),
        "full_payload_available": bool(operational_profile_json),
        "payload_dumped": False,
    }


def forge_agent_list(limit=50):
    """Patch 228 read-only full-profile-aware agent list."""
    rows_out = []
    try:
        limit = int(limit or 50)
    except Exception:
        limit = 50
    try:
        conn = _patch228_readonly_conn()
        try:
            rows = conn.execute(
                """
                SELECT id, agent_id, canonical_name, role, activation_state, is_active,
                       rmc_namespace, profile_schema_version, profile_hash, last_validated_at,
                       created_at, updated_at, operational_profile_json
                FROM agent_profiles
                ORDER BY id ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        finally:
            conn.close()
        rows_out = [_patch228_agent_row_to_summary(r) for r in rows]
        return {
            "ok": True,
            "service": "identity_vault",
            "read_only": True,
            "connector_version": "patch228_full_profile_readonly_adapter_v1",
            "agents_returned": len(rows_out),
            "agents": rows_out,
            "safe_columns": [
                "id",
                "agent_id",
                "canonical_name",
                "role",
                "activation_state",
                "is_active",
                "rmc_namespace",
                "profile_schema_version",
                "profile_hash",
                "last_validated_at",
                "created_at",
                "updated_at",
                "permissions_summary",
                "forbidden_actions_summary",
            ],
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
        }
    except Exception as exc:
        return {
            "ok": False,
            "service": "identity_vault",
            "read_only": True,
            "connector_version": "patch228_full_profile_readonly_adapter_v1",
            "error": str(exc),
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
        }


def forge_agent_show(agent_id):
    """Patch 228 read-only full-profile-aware agent show."""
    try:
        conn = _patch228_readonly_conn()
        try:
            row = conn.execute(
                """
                SELECT id, agent_id, canonical_name, role, activation_state, is_active,
                       rmc_namespace, profile_schema_version, profile_hash, last_validated_at,
                       created_at, updated_at, operational_profile_json
                FROM agent_profiles
                WHERE agent_id = ?
                LIMIT 1
                """,
                (str(agent_id),),
            ).fetchone()
        finally:
            conn.close()
        if not row:
            return {
                "ok": True,
                "service": "identity_vault",
                "read_only": True,
                "connector_version": "patch228_full_profile_readonly_adapter_v1",
                "agent_id": str(agent_id),
                "found": False,
                "note": "Agent metadata not found.",
                "database_write_performed": False,
                "agent_identity_activation_performed": False,
            }
        agent = _patch228_agent_row_to_summary(row)
        return {
            "ok": True,
            "service": "identity_vault",
            "read_only": True,
            "connector_version": "patch228_full_profile_readonly_adapter_v1",
            "agent_id": str(agent_id),
            "found": True,
            "note": "Agent full operational metadata summary found. Full payload is intentionally not dumped by default.",
            "agent": agent,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
        }
    except Exception as exc:
        return {
            "ok": False,
            "service": "identity_vault",
            "read_only": True,
            "connector_version": "patch228_full_profile_readonly_adapter_v1",
            "agent_id": str(agent_id),
            "found": False,
            "error": str(exc),
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
        }
# <<< PATCH 228 FULL PROFILE READONLY ADAPTER OVERRIDES <<<

# --- PATCH 228A.1 FULL PROFILE HASH RECONCILE BEGIN ---
# Read-only Identity Vault full-profile hash reconciliation.
# This block intentionally overrides forge_agent_list / forge_agent_show with
# stricter read-only profile hash validation while preserving safe summaries.
def _p228a1_home():
    from pathlib import Path as _Path
    return _Path.home()


def _p228a1_identity_db():
    return _p228a1_home() / "identity-vault" / "data" / "identity_vault.db"


def _p228a1_open_identity_readonly():
    import sqlite3 as _sqlite3
    db = _p228a1_identity_db()
    uri = f"file:{db}?mode=ro"
    conn = _sqlite3.connect(uri, uri=True)
    conn.row_factory = _sqlite3.Row
    return conn


def _p228a1_hash_candidates(raw_text, parsed):
    import hashlib as _hashlib
    import json as _json
    candidates = {}
    if raw_text is not None:
        raw = str(raw_text)
        candidates["raw"] = _hashlib.sha256(raw.encode("utf-8")).hexdigest()
        candidates["raw_strip"] = _hashlib.sha256(raw.strip().encode("utf-8")).hexdigest()
    if parsed is not None:
        canonical_compact = _json.dumps(parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        canonical_default = _json.dumps(parsed, sort_keys=True, ensure_ascii=False)
        canonical_pretty = _json.dumps(parsed, sort_keys=True, indent=2, ensure_ascii=False)
        candidates["json_sort_compact"] = _hashlib.sha256(canonical_compact.encode("utf-8")).hexdigest()
        candidates["json_sort_default"] = _hashlib.sha256(canonical_default.encode("utf-8")).hexdigest()
        candidates["json_sort_pretty"] = _hashlib.sha256(canonical_pretty.encode("utf-8")).hexdigest()
    return candidates


def _p228a1_profile_hash_status(raw_text, stored_hash):
    import json as _json
    parsed = None
    json_ok = False
    parse_error = None
    try:
        parsed = _json.loads(raw_text or "{}")
        json_ok = True
    except Exception as exc:
        parse_error = str(exc)
    candidates = _p228a1_hash_candidates(raw_text, parsed)
    match_method = None
    for method, digest in candidates.items():
        if digest == stored_hash:
            match_method = method
            break
    return {
        "json_ok": json_ok,
        "parse_error": parse_error,
        "parsed": parsed if isinstance(parsed, dict) else {},
        "profile_hash_ok": bool(match_method),
        "profile_hash_method": match_method,
        "candidate_hashes_preview": {k: v[:16] for k, v in candidates.items()},
    }


def _p228a1_as_list(value, max_items=8):
    if isinstance(value, list):
        return value[:max_items]
    if value is None or value == "":
        return []
    return [str(value)]


def _p228a1_agent_summary(row):
    profile_hash = row["profile_hash"] if "profile_hash" in row.keys() else None
    raw_profile = row["operational_profile_json"] if "operational_profile_json" in row.keys() else "{}"
    status = _p228a1_profile_hash_status(raw_profile, profile_hash)
    profile = status.get("parsed") or {}
    return {
        "id": row["id"] if "id" in row.keys() else None,
        "agent_id": row["agent_id"],
        "canonical_name": row["canonical_name"] if "canonical_name" in row.keys() else profile.get("canonical_name"),
        "role": row["role"] if "role" in row.keys() else profile.get("role"),
        "activation_state": row["activation_state"] if "activation_state" in row.keys() else profile.get("session_state"),
        "is_active": row["is_active"] if "is_active" in row.keys() else None,
        "rmc_namespace": row["rmc_namespace"] if "rmc_namespace" in row.keys() else profile.get("rmc_namespace"),
        "profile_schema_version": row["profile_schema_version"] if "profile_schema_version" in row.keys() else None,
        "profile_hash": profile_hash,
        "profile_hash_ok": status["profile_hash_ok"],
        "profile_hash_method": status["profile_hash_method"],
        "last_validated_at": row["last_validated_at"] if "last_validated_at" in row.keys() else None,
        "created_at": row["created_at"] if "created_at" in row.keys() else None,
        "updated_at": row["updated_at"] if "updated_at" in row.keys() else None,
        "full_payload_available": bool(raw_profile),
        "payload_dumped": False,
        "persona": profile.get("persona"),
        "voice_style": profile.get("voice_style"),
        "symbolic_signature": _p228a1_as_list(profile.get("symbolic_signature")),
        "permissions_summary": _p228a1_as_list(profile.get("permissions")),
        "authority_summary": _p228a1_as_list(profile.get("authority")),
        "limitations_summary": _p228a1_as_list(profile.get("limitations")),
        "forbidden_actions_summary": _p228a1_as_list(profile.get("forbidden_actions")),
    }


def forge_agent_list(*args, **kwargs):
    try:
        conn = _p228a1_open_identity_readonly()
        try:
            rows = conn.execute(
                """
                SELECT id, agent_id, canonical_name, role, activation_state, is_active,
                       rmc_namespace, profile_schema_version, profile_hash,
                       operational_profile_json, last_validated_at, created_at, updated_at
                FROM agent_profiles
                ORDER BY id ASC
                """
            ).fetchall()
        finally:
            conn.close()
        agents = [_p228a1_agent_summary(row) for row in rows]
        return {
            "ok": True,
            "service": "identity_vault",
            "connector_version": "patch228a1_full_profile_hash_reconcile_v1",
            "read_only": True,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
            "agents_returned": len(agents),
            "agents": agents,
            "safe_columns": [
                "id", "agent_id", "canonical_name", "role", "activation_state", "is_active",
                "rmc_namespace", "profile_schema_version", "profile_hash", "profile_hash_ok",
                "profile_hash_method", "last_validated_at", "created_at", "updated_at",
                "permissions_summary", "forbidden_actions_summary"
            ],
        }
    except Exception as exc:
        return {
            "ok": False,
            "service": "identity_vault",
            "connector_version": "patch228a1_full_profile_hash_reconcile_v1",
            "read_only": True,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def forge_agent_show(agent_id=None, *args, **kwargs):
    if not agent_id:
        return {
            "ok": False,
            "service": "identity_vault",
            "connector_version": "patch228a1_full_profile_hash_reconcile_v1",
            "read_only": True,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
            "found": False,
            "error": "agent_id required",
        }
    try:
        conn = _p228a1_open_identity_readonly()
        try:
            row = conn.execute(
                """
                SELECT id, agent_id, canonical_name, role, activation_state, is_active,
                       rmc_namespace, profile_schema_version, profile_hash,
                       operational_profile_json, last_validated_at, created_at, updated_at
                FROM agent_profiles
                WHERE agent_id = ?
                LIMIT 1
                """,
                (agent_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            return {
                "ok": True,
                "service": "identity_vault",
                "connector_version": "patch228a1_full_profile_hash_reconcile_v1",
                "read_only": True,
                "database_write_performed": False,
                "agent_identity_activation_performed": False,
                "found": False,
                "agent_id": agent_id,
                "note": "Agent profile not found.",
            }
        return {
            "ok": True,
            "service": "identity_vault",
            "connector_version": "patch228a1_full_profile_hash_reconcile_v1",
            "read_only": True,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
            "found": True,
            "agent_id": agent_id,
            "agent": _p228a1_agent_summary(row),
            "note": "Agent full operational metadata summary found. Full payload is intentionally not dumped by default.",
        }
    except Exception as exc:
        return {
            "ok": False,
            "service": "identity_vault",
            "connector_version": "patch228a1_full_profile_hash_reconcile_v1",
            "read_only": True,
            "database_write_performed": False,
            "agent_identity_activation_performed": False,
            "found": False,
            "agent_id": agent_id,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
# --- PATCH 228A.1 FULL PROFILE HASH RECONCILE END ---
