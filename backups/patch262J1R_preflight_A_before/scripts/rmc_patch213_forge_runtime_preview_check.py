#!/usr/bin/env python3
"""
Patch 213 - Forge RMC Runtime Preview Check

Purpose:
  Read-only verification that Forge's command/tool surface survived Patch 212 and
  that the registered RMC preview tools are reachable from Forge's tool layer.

Boundaries:
  - Does not modify Forge tools, main.py, tool_registry.json, Identity Vault, RMC memory,
    AI.Web wrappers, or agent identity configuration.
  - Writes only a verification report under:
      ~/forge/memory/rmc_patch213_forge_runtime_preview_v1/

This script intentionally avoids starting an interactive Forge session. It inspects and imports
Forge's tool layer in-process, then calls read-only preview functions only.
"""

from __future__ import annotations

import datetime as _dt
import importlib
import inspect
import json
import os
import py_compile
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

EXPECTED_TOOLS = [
    "rmc_phase_parse_preview",
    "rmc_drift_check_preview",
    "rmc_echo_validate_preview",
    "rmc_pipeline_preview",
]


def _now_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def _home() -> Path:
    return Path.home()


def _forge_root() -> Path:
    return _home() / "forge"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def _safe_compile(path: Path) -> Tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, ""
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _summarize_result(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        result = value.get("result", value)
        summary: Dict[str, Any] = {
            "keys": sorted(list(value.keys()))[:32],
        }
        if isinstance(result, dict):
            summary["result_keys"] = sorted(list(result.keys()))[:40]
            for key in [
                "phase",
                "phase_id",
                "phase_number",
                "phase_name",
                "verdict",
                "accepted",
                "echo_score",
                "drift_verdict",
                "projection_status",
                "read_only",
                "ok",
            ]:
                if key in result:
                    summary[key] = result[key]
                elif key in value:
                    summary[key] = value[key]
        else:
            summary["result_type"] = type(result).__name__
        return summary
    return {"type": type(value).__name__, "repr": repr(value)[:300]}


def _call_with_flexible_args(func: Callable[..., Any], tool_name: str) -> Tuple[bool, Any, str]:
    """Call a preview function without assuming exact signature."""
    cases = {
        "rmc_phase_parse_preview": [
            ({"text": "We need correction before projection. Return this loop through Grace."},),
            ("We need correction before projection. Return this loop through Grace.",),
        ],
        "rmc_drift_check_preview": [
            ({"text": "Jump from collapse straight into public projection.", "phase_number": 5, "phase_history": [4, 5]},),
            ("Jump from collapse straight into public projection.", 5, [4, 5]),
            ("Jump from collapse straight into public projection.",),
        ],
        "rmc_echo_validate_preview": [
            ({
                "rendered_output": "Correction is required before projection.",
                "manifest": {
                    "claim": "Correction is required before projection.",
                    "phase": 6,
                    "drift_status": "bounded",
                    "output_targets": ["text"],
                },
            },),
            (
                "Correction is required before projection.",
                {
                    "claim": "Correction is required before projection.",
                    "phase": 6,
                    "drift_status": "bounded",
                    "output_targets": ["text"],
                },
            ),
        ],
        "rmc_pipeline_preview": [
            ({"input_text": "We need correction before projection and a trace before output.", "modality": "text"},),
            ("We need correction before projection and a trace before output.",),
        ],
    }

    last_err = ""
    for args in cases.get(tool_name, [tuple()]):
        try:
            return True, func(*args), ""
        except TypeError as exc:
            last_err = f"TypeError: {exc}"
        except Exception as exc:
            return False, None, f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
    return False, None, last_err or "No call case succeeded."


def _find_callable_in_tools(tools_mod: Any, tool_name: str) -> Tuple[bool, Any, str]:
    # Direct callable exported by agents.forge.tools
    candidate = getattr(tools_mod, tool_name, None)
    if callable(candidate):
        return True, candidate, "direct_callable"

    # Mapping-style registries commonly used by tool dispatch systems.
    for attr in [
        "TOOL_FUNCTIONS",
        "TOOL_HANDLERS",
        "TOOL_DISPATCH",
        "FUNCTIONS",
        "DISPATCH_TABLE",
        "AVAILABLE_TOOLS",
    ]:
        mapping = getattr(tools_mod, attr, None)
        if isinstance(mapping, dict) and callable(mapping.get(tool_name)):
            return True, mapping[tool_name], f"mapping:{attr}"

    # If no callable is exposed, the tool may only be reachable by Forge's LLM dispatch loop.
    return False, None, "not_found_as_direct_callable_or_mapping"


def _scan_tool_definitions_object(tools_mod: Any) -> Dict[str, bool]:
    found = {name: False for name in EXPECTED_TOOLS}
    for attr in ["TOOL_DEFINITIONS", "TOOLS", "TOOL_SCHEMA", "TOOL_SCHEMAS", "FUNCTION_DEFINITIONS"]:
        obj = getattr(tools_mod, attr, None)
        if obj is None:
            continue
        try:
            blob = json.dumps(obj, sort_keys=True, default=str)
        except Exception:
            blob = repr(obj)
        for name in EXPECTED_TOOLS:
            if name in blob:
                found[name] = True
    return found


def main() -> int:
    home = _home()
    forge = _forge_root()
    ts = _now_stamp()
    out_root = forge / "memory" / "rmc_patch213_forge_runtime_preview_v1"
    run_dir = out_root / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    report_json = run_dir / f"{ts}_rmc_patch213_forge_runtime_preview.json"
    report_md = run_dir / f"{ts}_rmc_patch213_forge_runtime_preview.md"
    latest_md = out_root / "latest_rmc_patch213_forge_runtime_preview.md"

    main_py = forge / "main.py"
    tools_py = forge / "agents" / "forge" / "tools.py"
    rmc_tools_py = forge / "agents" / "forge" / "rmc_tools.py"
    registry_json = forge / "config" / "tool_registry.json"

    data: Dict[str, Any] = {
        "timestamp": ts,
        "boundary": {
            "read_only": True,
            "writes_only_report": str(out_root),
            "does_not_modify": [
                "agents/forge/tools.py",
                "agents/forge/rmc_tools.py",
                "main.py",
                "config/tool_registry.json",
                "identity-vault",
                "aiweb/runtime_wrappers",
                "persistent RMC memory",
                "agent identity configuration",
            ],
        },
        "paths": {
            "forge": str(forge),
            "main_py": str(main_py),
            "tools_py": str(tools_py),
            "rmc_tools_py": str(rmc_tools_py),
            "tool_registry": str(registry_json),
        },
        "checks": {},
        "command_surface": {},
        "tool_definitions": {},
        "tool_runtime": {},
        "manual_next_test": [],
        "errors": [],
    }

    # Existence and compile checks.
    data["checks"]["forge_exists"] = forge.exists()
    data["checks"]["main_exists"] = main_py.exists()
    data["checks"]["tools_exists"] = tools_py.exists()
    data["checks"]["rmc_tools_exists"] = rmc_tools_py.exists()
    data["checks"]["registry_exists"] = registry_json.exists()

    for label, path in [("tools_compile", tools_py), ("rmc_tools_compile", rmc_tools_py)]:
        ok, err = _safe_compile(path)
        data["checks"][label] = ok
        if err:
            data["errors"].append({label: err})

    # Command surface check by text only; we do not start interactive Forge here.
    main_text = _read_text(main_py)
    tools_text = _read_text(tools_py)
    data["command_surface"] = {
        "forge_command_surface_mentioned": "forge-command-surface" in main_text,
        "forge_version_mentioned": "forge-version" in main_text,
        "rmc_preview_tool_names_mentioned_in_tools_py": {name: (name in tools_text) for name in EXPECTED_TOOLS},
        "patch212_markers_present": {
            "begin_marker": "PATCH 212" in tools_text or "RMC READ-ONLY" in tools_text.upper(),
            "all_expected_tool_names": all(name in tools_text for name in EXPECTED_TOOLS),
        },
    }

    # Registry should remain untouched by RMC tool names at this stage.
    registry_text = _read_text(registry_json)
    data["checks"]["tool_registry_rmc_mentions"] = sum(registry_text.count(name) for name in EXPECTED_TOOLS)
    reg_obj = _load_json(registry_json)
    if isinstance(reg_obj, dict):
        data["checks"]["tool_registry_trust_level"] = reg_obj.get("current_trust_level")

    # Import and runtime calls through Forge's tool layer where exposed.
    try:
        sys.path.insert(0, str(forge))
        tools_mod = importlib.import_module("agents.forge.tools")
        rmc_mod = importlib.import_module("agents.forge.rmc_tools")
        data["checks"]["tools_import"] = True
        data["checks"]["rmc_tools_import"] = True

        data["tool_definitions"] = _scan_tool_definitions_object(tools_mod)

        for name in EXPECTED_TOOLS:
            entry: Dict[str, Any] = {}
            found, func, route = _find_callable_in_tools(tools_mod, name)
            entry["forge_tool_layer_route"] = route
            entry["callable_from_tools_module"] = found

            if found:
                ok, result, err = _call_with_flexible_args(func, name)
                entry["runtime_call_via_tools_module"] = ok
                if ok:
                    entry["summary"] = _summarize_result(result)
                else:
                    entry["error"] = err
            else:
                # Fallback: prove the underlying read-only wrapper still works.
                fallback_func = getattr(rmc_mod, name, None)
                entry["fallback_wrapper_callable"] = callable(fallback_func)
                if callable(fallback_func):
                    ok, result, err = _call_with_flexible_args(fallback_func, name)
                    entry["runtime_call_via_rmc_wrapper"] = ok
                    if ok:
                        entry["summary"] = _summarize_result(result)
                    else:
                        entry["error"] = err
                else:
                    entry["error"] = "No callable found in agents.forge.tools or agents.forge.rmc_tools."

            data["tool_runtime"][name] = entry

    except Exception as exc:
        data["checks"]["tools_import"] = False
        data["errors"].append({"import_runtime": f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"})

    # Manual interactive instructions to run after this report, not executed by script.
    data["manual_next_test"] = [
        "cd ~/forge",
        "source .venv/bin/activate",
        "python main.py",
        "Select the usual safe project scope when Forge asks, commonly /home/nic/aiweb or /home/nic/forge_test_project.",
        "Run: forge-command-surface",
        "Confirm the command count did not regress and the new RMC preview tools appear if Forge lists tool names.",
        "Exit Forge cleanly after the check.",
    ]

    # Verdict conditions.
    expected_defs_ok = all(data.get("tool_definitions", {}).get(name, False) for name in EXPECTED_TOOLS)
    runtime_ok = True
    for name in EXPECTED_TOOLS:
        entry = data["tool_runtime"].get(name, {})
        runtime_ok = runtime_ok and bool(entry.get("runtime_call_via_tools_module") or entry.get("runtime_call_via_rmc_wrapper"))

    command_surface_ok = bool(data["command_surface"].get("forge_command_surface_mentioned"))
    compile_ok = bool(data["checks"].get("tools_compile")) and bool(data["checks"].get("rmc_tools_compile"))
    registry_ok = data["checks"].get("tool_registry_rmc_mentions") == 0

    verdict = compile_ok and expected_defs_ok and runtime_ok and command_surface_ok and registry_ok
    data["verdict"] = "PASS" if verdict else "FAIL"
    data["verdict_components"] = {
        "compile_ok": compile_ok,
        "expected_definitions_ok": expected_defs_ok,
        "runtime_preview_calls_ok": runtime_ok,
        "command_surface_mention_ok": command_surface_ok,
        "tool_registry_still_unmodified_by_rmc": registry_ok,
    }

    report_json.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    lines: List[str] = []
    lines.append("# RMC Patch 213 Forge Runtime Preview Report")
    lines.append("")
    lines.append(f"Timestamp: `{ts}`")
    lines.append(f"Verdict: **{data['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- This script is read-only except for writing this report under Forge memory.")
    lines.append("- It does not modify Forge tools, Forge registry, AI.Web wrappers, Identity Vault, databases, RMC memory, or agent identity configuration.")
    lines.append("")
    lines.append("## Verdict Components")
    for k, v in data["verdict_components"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Command Surface Check")
    for k, v in data["command_surface"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Registry Boundary")
    lines.append(f"- `tool_registry_rmc_mentions`: `{data['checks'].get('tool_registry_rmc_mentions')}`")
    lines.append(f"- `tool_registry_trust_level`: `{data['checks'].get('tool_registry_trust_level')}`")
    lines.append("")
    lines.append("## RMC Tool Definitions")
    for name in EXPECTED_TOOLS:
        status = "FOUND" if data.get("tool_definitions", {}).get(name) else "MISSING"
        lines.append(f"- `{name}`: **{status}**")
    lines.append("")
    lines.append("## Runtime Preview Calls")
    for name in EXPECTED_TOOLS:
        entry = data["tool_runtime"].get(name, {})
        ok = entry.get("runtime_call_via_tools_module") or entry.get("runtime_call_via_rmc_wrapper")
        status = "PASS" if ok else "FAIL"
        route = entry.get("forge_tool_layer_route")
        lines.append(f"- `{name}`: **{status}** route=`{route}`")
        if "summary" in entry:
            lines.append(f"  - summary: `{entry['summary']}`")
        if "error" in entry:
            lines.append(f"  - error: `{entry['error']}`")
    lines.append("")
    lines.append("## Manual Forge Interactive Check")
    lines.append("Run this after the script passes, because this script does not start interactive Forge by itself:")
    lines.append("")
    lines.append("```bash")
    lines.append("cd ~/forge")
    lines.append("source .venv/bin/activate")
    lines.append("python main.py")
    lines.append("# Select your usual safe project scope when Forge asks.")
    lines.append("# Then run:")
    lines.append("forge-command-surface")
    lines.append("# Then exit Forge cleanly.")
    lines.append("```")
    lines.append("")
    lines.append("## Next Safe Step")
    if verdict:
        lines.append("If this passes and the manual Forge command-surface check shows no regression, create the Identity Vault boundary scan. Do not activate agent identities yet.")
    else:
        lines.append("Do not proceed. Review the FAIL component above and restore from Patch 212 backup if needed.")

    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    latest_md.write_text(report_md.read_text(encoding="utf-8"), encoding="utf-8")

    print("RMC Patch 213 Forge runtime preview check complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest_md}")
    print(f"Verdict: {data['verdict']}")
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
