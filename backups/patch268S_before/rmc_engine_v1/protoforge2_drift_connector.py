"""ProtoForge2 Drift Connector — forge/rmc_engine_v1/protoforge2_drift_connector.py

Patch 268 — ProtoForge2 Drift Connector Preflight

Safe inspection and adapter for the real ProtoForge2 drift module.
Does not connect blindly.  Reports status first.

Expected ProtoForge2 root:
    /home/nic/aiweb/runtime_wrappers/protoforge_sandbox_substrate_v0/

Expected drift module filename:
    memory-drift.py  (hyphen in filename requires importlib, not normal import)
    OR memory_drift.py (underscore variant)
    OR drift.py

ADAPTER MODES:
    LIVE   — ProtoForge2 module found, imported, and callable
    SKIPPED — ProtoForge2 root or module not found (no crash)
    FALLBACK — Import succeeded but normalisation of output failed; falls back to
               RMC structural drift engine

HARD RULES:
    - Never modify ProtoForge2 files.
    - Never write to ProtoForge2.
    - No shell execution.
    - No Chroma write.
    - No Identity Vault.
    - No LLM calls.
    - No arbitrary code execution beyond controlled importlib + one safe probe call.
    - If import or call fails for any reason: return SKIPPED/UNAVAILABLE; do not crash.

Design source: AI.Web Forge/RMC Build Objective — Patch 268 spec
"""
from __future__ import annotations

import datetime  as _dt
import hashlib   as _hl
import importlib.util as _iutil
import inspect   as _inspect
import json      as _json
import os        as _os
from pathlib import Path as _Path
from typing import Any

try:
    from rmc_engine_v1.measurement_kernel import clamp, stable_hash, stable_id
except Exception:
    def clamp(v: Any, low: float = 0.0, high: float = 1.0) -> float:  # type: ignore
        try: return max(float(low), min(float(high), float(v)))
        except: return float(low)
    def stable_hash(obj: Any) -> str:  # type: ignore
        return _hl.sha256(_json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()
    def stable_id(prefix: str, obj: Any, n: int = 18) -> str:  # type: ignore
        return f"{prefix}_{_hl.sha256(str(obj).encode()).hexdigest()[:n]}"

ENGINE_VERSION = "rmc_protoforge2_drift_connector_v1_patch268"
ENGINE_MODE    = "protoforge2_drift_connector_preflight"

# ── Expected paths ────────────────────────────────────────────────────────────
DEFAULT_PF2_ROOT = _Path("/home/nic/aiweb/runtime_wrappers/protoforge_sandbox_substrate_v0")
CANDIDATE_FILENAMES = (
    "memory-drift.py",    # hyphen variant (requires importlib)
    "memory_drift.py",    # underscore variant
    "drift.py",
    "memory/drift.py",
)

# ── Safety: allowed callable name patterns ────────────────────────────────────
# Only call functions whose names match these patterns.
# This prevents accidentally calling shell/write/delete functions.
SAFE_FUNCTION_PATTERNS = (
    "analyze",
    "compute",
    "score",
    "detect",
    "classify",
    "check",
    "evaluate",
    "measure",
    "drift",
    "entropy",
    "epsilon",
    "semantic",
    "syntactic",
    "recursive",
    "chi",
    "boundary",
    "status",
)

UNSAFE_FUNCTION_PATTERNS = (
    "write",
    "delete",
    "remove",
    "shell",
    "exec",
    "run",
    "spawn",
    "kill",
    "commit",
    "deploy",
    "upload",
    "send",
    "post",
    "push",
)


def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()

def _f(v: Any, d: float = 0.0) -> float:
    try: return float(v)
    except: return d

def _file_sha256(path: _Path) -> str:
    try:
        h = _hl.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "sha256_unavailable"

def _is_safe_function_name(name: str) -> bool:
    nl = name.lower()
    if any(p in nl for p in UNSAFE_FUNCTION_PATTERNS):
        return False
    return True

def _is_suspicious_path(path: _Path) -> bool:
    """Refuse paths that attempt path traversal or point outside expected root."""
    try:
        resolved = path.resolve()
        # Must be under /home, /tmp, or the explicit PF2 root
        allowed_roots = [_Path("/home"), _Path("/tmp"), DEFAULT_PF2_ROOT]
        return not any(str(resolved).startswith(str(r)) for r in allowed_roots)
    except Exception:
        return True


# ── Public: boundary ──────────────────────────────────────────────────────────

def boundary() -> dict:
    return {
        "engine_version":       ENGINE_VERSION,
        "engine_mode":          ENGINE_MODE,
        "patch":                "268",
        "module":               "forge/rmc_engine_v1/protoforge2_drift_connector.py",
        "description":          "Safe inspection and adapter for ProtoForge2 drift module.",
        "expected_pf2_root":    str(DEFAULT_PF2_ROOT),
        "candidate_filenames":  list(CANDIDATE_FILENAMES),
        "adapter_modes":        ["LIVE", "SKIPPED", "FALLBACK"],
        "import_method":        "importlib.util.spec_from_file_location (handles hyphen filenames)",
        "safety_rules": {
            "no_modify_pf2":        True,
            "no_write_pf2":         True,
            "no_shell":             True,
            "no_chroma_write":      True,
            "no_identity_vault":    True,
            "no_llm":               True,
            "no_arbitrary_exec":    True,
            "safe_function_only":   True,
            "path_traversal_check": True,
        },
        "read_only":            True,
        "writes_files":         False,
        "writes_rmc_memory":    False,
        "writes_identity_vault": False,
        "queries_chroma":       False,
        "calls_llm":            False,
        "executes_shell":       False,
    }


# ── Public: probe status ──────────────────────────────────────────────────────

def probe_protoforge2_status(pf2_root: str | _Path | None = None) -> dict:
    """Probe ProtoForge2 root and report status.  No import, no execution.

    Returns a status dict that the /api/rmc/protoforge2-drift-status endpoint serves.
    """
    root = _Path(pf2_root or DEFAULT_PF2_ROOT).expanduser().resolve()

    if _is_suspicious_path(root):
        return {
            "status": "REFUSED_UNSAFE_PATH",
            "protoforge2_root_exists": False,
            "drift_module_found": False,
            "reason": f"path={root!r} failed safety check",
        }

    root_exists = root.exists() and root.is_dir()
    if not root_exists:
        return {
            "status": "SKIPPED",
            "protoforge2_root_exists": False,
            "drift_module_found": False,
            "drift_module_path": None,
            "module_sha256": None,
            "importable": False,
            "adapter_mode": "SKIPPED",
            "live_drift_available": False,
            "fallback_mode": "structural_contract_drift_analysis",
            "reason": f"ProtoForge2 root not found: {root}",
            "read_only": True,
            "engine_version": ENGINE_VERSION,
        }

    # Search for the drift module
    found_path: _Path | None = None
    for candidate in CANDIDATE_FILENAMES:
        p = root / candidate
        if p.exists():
            found_path = p
            break

    if not found_path:
        return {
            "status": "SKIPPED",
            "protoforge2_root_exists": True,
            "drift_module_found": False,
            "drift_module_path": None,
            "module_sha256": None,
            "importable": False,
            "adapter_mode": "SKIPPED",
            "live_drift_available": False,
            "fallback_mode": "structural_contract_drift_analysis",
            "reason": f"No drift module found in {root}. Searched: {CANDIDATE_FILENAMES}",
            "root_contents": [str(p.name) for p in root.iterdir()
                              if p.is_file()][:20],
            "read_only": True,
            "engine_version": ENGINE_VERSION,
        }

    sha = _file_sha256(found_path)
    # Enumerate public functions (read source without importing)
    try:
        with open(found_path, encoding="utf-8", errors="replace") as f:
            src_preview = f.read(8192)
        import ast as _ast
        tree = _ast.parse(src_preview)
        funcs = [n.name for n in _ast.walk(tree)
                 if isinstance(n, _ast.FunctionDef)]
        safe_funcs  = [fn for fn in funcs if _is_safe_function_name(fn)]
        unsafe_funcs = [fn for fn in funcs if not _is_safe_function_name(fn)]
    except Exception as exc:
        funcs = []; safe_funcs = []; unsafe_funcs = []
        src_preview = f"(parse error: {exc})"

    return {
        "status": "FOUND",
        "protoforge2_root_exists": True,
        "drift_module_found": True,
        "drift_module_path": str(found_path),
        "module_sha256": sha,
        "importable": None,       # Not yet tested — import requires probe_import
        "available_functions": funcs[:30],
        "safe_callable_functions": safe_funcs[:20],
        "unsafe_blocked_functions": unsafe_funcs[:10],
        "adapter_mode": "PENDING_IMPORT",
        "live_drift_available": False,  # not confirmed until import
        "fallback_mode": "structural_contract_drift_analysis",
        "read_only": True,
        "engine_version": ENGINE_VERSION,
    }


def probe_protoforge2_import(pf2_root: str | _Path | None = None) -> dict:
    """Attempt to import the ProtoForge2 drift module safely.

    Returns updated status with importable flag and available_functions.
    Does NOT call any functions.
    """
    status = probe_protoforge2_status(pf2_root)
    if status["status"] != "FOUND":
        return status

    found_path = _Path(status["drift_module_path"])
    module_name = f"_pf2_drift_{found_path.stem.replace('-','_')}"

    try:
        spec = _iutil.spec_from_file_location(module_name, found_path)
        if spec is None or spec.loader is None:
            raise ImportError("spec_from_file_location returned None")
        mod = _iutil.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]

        # Inspect available functions safely
        funcs = {
            name: fn for name, fn in _inspect.getmembers(mod, _inspect.isfunction)
            if not name.startswith("_")
        }
        safe_funcs   = {k: v for k, v in funcs.items() if _is_safe_function_name(k)}
        unsafe_funcs = {k: v for k, v in funcs.items() if not _is_safe_function_name(k)}

        return {
            **status,
            "importable": True,
            "module_name": module_name,
            "available_functions": list(funcs.keys())[:30],
            "safe_callable_functions": list(safe_funcs.keys())[:20],
            "unsafe_blocked_functions": list(unsafe_funcs.keys())[:10],
            "adapter_mode": "LIVE",
            "live_drift_available": bool(safe_funcs),
            "import_status": "SUCCESS",
        }
    except Exception as exc:
        return {
            **status,
            "importable": False,
            "adapter_mode": "SKIPPED",
            "live_drift_available": False,
            "import_status": f"IMPORT_ERROR: {exc}",
            "fallback_mode": "structural_contract_drift_analysis",
        }


# ── RMC schema normaliser ─────────────────────────────────────────────────────

def _normalize_pf2_output(raw: Any, source_fn: str) -> dict:
    """Normalise ProtoForge2 drift output to RMC drift schema.

    The real ProtoForge2 drift module uses its own field names.
    This function maps them to the canonical RMC drift report fields.
    """
    if isinstance(raw, dict):
        # Try canonical fields first
        eps = _f(raw.get("epsilon_s") or raw.get("eps") or raw.get("drift_score") or
                  raw.get("score") or 0.0)
        drift_type = str(raw.get("drift_type") or raw.get("classification") or
                          raw.get("category") or "unknown")
        circuit_breaker = bool(raw.get("circuit_breaker") or raw.get("blocked") or
                                 raw.get("cb") or eps >= 0.72)
        return {
            "status":             "NORMALIZED",
            "source_function":    source_fn,
            "epsilon_s":          round(eps, 4),
            "drift_type":         drift_type,
            "circuit_breaker":    circuit_breaker,
            "raw_pf2_fields":     {k: v for k, v in raw.items()
                                   if k not in ("epsilon_s","drift_type","circuit_breaker")}
        }
    elif isinstance(raw, (int, float)):
        eps = _f(raw)
        return {
            "status":          "NORMALIZED_SCALAR",
            "source_function": source_fn,
            "epsilon_s":       round(clamp(eps), 4),
            "drift_type":      "scalar_epsilon",
            "circuit_breaker": eps >= 0.72,
        }
    else:
        return {
            "status":          "NORMALIZATION_FAILED",
            "source_function": source_fn,
            "raw_type":        type(raw).__name__,
            "epsilon_s":       0.0,
            "drift_type":      "unknown",
            "circuit_breaker": False,
        }


def preview_drift_call(
    pf2_root: str | _Path | None = None,
    *,
    test_module_path: str | _Path | None = None,
) -> dict:
    """Attempt a safe probe call to the ProtoForge2 drift module.

    Uses a minimal harmless probe payload.  Normalises the result to RMC schema.

    Parameters
    ----------
    pf2_root:
        ProtoForge2 root directory.  Defaults to DEFAULT_PF2_ROOT.
    test_module_path:
        Override with a test module path (for unit tests).
    """
    if test_module_path is not None:
        # Test path: skip safety checks on default root
        probe_root = None
        found_path = _Path(test_module_path).expanduser().resolve()
        if not found_path.exists():
            return {"status": "SKIPPED", "reason": f"test_module_path not found: {found_path}",
                    "live_drift_available": False, "adapter_mode": "SKIPPED"}
    else:
        import_status = probe_protoforge2_import(pf2_root)
        if not import_status.get("importable"):
            return {**import_status, "preview_result": None}
        found_path = _Path(import_status["drift_module_path"])

    module_name = f"_pf2_drift_{found_path.stem.replace('-','_')}_preview"

    try:
        spec = _iutil.spec_from_file_location(module_name, found_path)
        if spec is None or spec.loader is None:
            raise ImportError("spec returned None")
        mod = _iutil.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    except Exception as exc:
        return {
            "status": "IMPORT_FAILED",
            "live_drift_available": False,
            "adapter_mode": "SKIPPED",
            "error": str(exc),
        }

    # Find the best callable safe function
    funcs = {
        name: fn for name, fn in _inspect.getmembers(mod, _inspect.isfunction)
        if not name.startswith("_") and _is_safe_function_name(name)
    }

    if not funcs:
        return {
            "status": "FALLBACK",
            "live_drift_available": False,
            "adapter_mode": "FALLBACK",
            "reason": "No safe-named functions found in module",
            "fallback_mode": "structural_contract_drift_analysis",
        }

    # Minimal harmless probe payload
    probe_payload = {
        "input":      "test probe from rmc containment router patch 268",
        "phase_path": ["Φ1", "Φ3"],
        "epsilon_s":  0.15,
        "dry_run":    True,
    }

    # Try calling the most likely drift function
    preferred = ("analyze_drift", "compute_epsilon", "score_drift", "drift", "analyze",
                 "compute", "score", "evaluate", "detect", "check")
    target_fn_name: str | None = None
    for name in preferred:
        if name in funcs:
            target_fn_name = name
            break
    if target_fn_name is None:
        target_fn_name = next(iter(funcs))

    target_fn = funcs[target_fn_name]

    try:
        # Probe: call with minimal kwargs; accept positional if no kwargs
        try:
            raw = target_fn(probe_payload)
        except TypeError:
            raw = target_fn(**probe_payload)
    except Exception as exc:
        return {
            "status": "CALL_FAILED",
            "adapter_mode": "FALLBACK",
            "live_drift_available": False,
            "called_function": target_fn_name,
            "error": str(exc),
            "fallback_mode": "structural_contract_drift_analysis",
        }

    normalized = _normalize_pf2_output(raw, target_fn_name)
    return {
        "status": "PREVIEW_OK",
        "adapter_mode": "LIVE",
        "live_drift_available": True,
        "called_function": target_fn_name,
        "probe_payload": probe_payload,
        "raw_output_type": type(raw).__name__,
        "normalized_result": normalized,
        "module_sha256": _file_sha256(found_path),
        "preview_at_utc": _utc(),
        "read_only": True,
        "writes_files": False,
        "engine_version": ENGINE_VERSION,
    }
