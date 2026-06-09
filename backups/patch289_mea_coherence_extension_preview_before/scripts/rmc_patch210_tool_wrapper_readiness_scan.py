#!/usr/bin/env python3
"""
Patch 210 — Forge RMC Tool Wrapper Readiness Scan

Read-only scanner for preparing Forge-side RMC tool wrappers.
It inspects the live Forge framework and AI.Web RMC runtime wrappers,
proves import readiness, checks basic callable surfaces, and writes an
auditable readiness report.

This script does not modify Forge tools, Forge agent code, AI.Web wrappers,
Identity Vault, databases, or Gilligan wiring.
"""

from __future__ import annotations

import datetime as _dt
import importlib
import inspect
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
AIWEB_ROOT = HOME / "aiweb"
RUNTIME_WRAPPERS = AIWEB_ROOT / "runtime_wrappers"
REPORT_ROOT = FORGE_ROOT / "memory" / "rmc_patch210_tool_wrapper_readiness_v1"

REQUIRED_FORGE_FILES = {
    "agent": FORGE_ROOT / "agents" / "forge" / "agent.py",
    "tools": FORGE_ROOT / "agents" / "forge" / "tools.py",
    "memory": FORGE_ROOT / "agents" / "forge" / "memory.py",
    "context_builder": FORGE_ROOT / "agents" / "forge" / "context_builder.py",
    "tool_registry": FORGE_ROOT / "config" / "tool_registry.json",
}

REQUIRED_IMPORTS = [
    ("phase_parser.phase_state_parser", "PhaseStateParser"),
    ("phase_state_parser.phase_state_parser", "PhaseStateParser"),
    ("drift_detection.drift_detector", "DriftArbitrator"),
    ("drift_arbitrator.drift_arbitrator", "DriftArbitrator"),
    ("echo_validator.echo_validator", "EchoGate"),
    ("echo_gate.echo_gate", "EchoGate"),
    ("rmc_orchestrator.rmc_orchestrator", "RMCOrchestrator"),
]

OPTIONAL_IMPORTS = [
    ("ancestral_memory.ancestral_memory", None),
    ("manifest_compiler.manifest_compiler", None),
    ("output_renderer.output_renderer", None),
]

PROPOSED_READ_ONLY_TOOLS = [
    {
        "name": "rmc_phase_parse_preview",
        "purpose": "Parse supplied text into a phase-state preview without writing memory.",
        "required_module": "phase_parser.phase_state_parser",
        "required_class": "PhaseStateParser",
        "write_scope": "none",
    },
    {
        "name": "rmc_drift_check_preview",
        "purpose": "Check supplied text/phase context for drift risk without applying correction or writing memory.",
        "required_module": "drift_detection.drift_detector",
        "required_class": "DriftArbitrator",
        "write_scope": "none",
    },
    {
        "name": "rmc_echo_validate_preview",
        "purpose": "Compare a rendered output against a manifest-like object without writing memory.",
        "required_module": "echo_validator.echo_validator",
        "required_class": "EchoGate",
        "write_scope": "none",
    },
    {
        "name": "rmc_orchestrator_preview",
        "purpose": "Run a dry preview through RMC orchestration and return trace/manifest/rendering status only.",
        "required_module": "rmc_orchestrator.rmc_orchestrator",
        "required_class": "RMCOrchestrator",
        "write_scope": "none unless the live orchestrator already writes internally; must be verified before enabling",
    },
]


def now_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def read_json(path: Path) -> Optional[Any]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def public_surface(obj: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {"type": type(obj).__name__, "methods": []}
    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            attr = getattr(obj, name)
        except Exception:
            continue
        if callable(attr):
            try:
                sig = str(inspect.signature(attr))
            except Exception:
                sig = "<signature unavailable>"
            result["methods"].append({"name": name, "signature": sig})
    return result


def module_surface(module: Any) -> Dict[str, Any]:
    classes: List[Dict[str, str]] = []
    functions: List[Dict[str, str]] = []
    for name, value in vars(module).items():
        if name.startswith("_"):
            continue
        if inspect.isclass(value):
            classes.append({"name": name, "module": getattr(value, "__module__", "")})
        elif inspect.isfunction(value):
            try:
                sig = str(inspect.signature(value))
            except Exception:
                sig = "<signature unavailable>"
            functions.append({"name": name, "signature": sig})
    return {"classes": classes, "functions": functions}


def try_import(module_name: str, class_name: Optional[str] = None) -> Dict[str, Any]:
    record: Dict[str, Any] = {
        "module": module_name,
        "class": class_name,
        "import_ok": False,
        "class_ok": None,
        "instantiation_ok": None,
        "surface": None,
        "error": None,
    }
    try:
        module = importlib.import_module(module_name)
        record["import_ok"] = True
        record["module_file"] = str(getattr(module, "__file__", ""))
        record["module_surface"] = module_surface(module)
        if class_name:
            klass = getattr(module, class_name)
            record["class_ok"] = True
            try:
                inst = klass()
                record["instantiation_ok"] = True
                record["surface"] = public_surface(inst)
            except Exception as exc:
                record["instantiation_ok"] = False
                record["error"] = f"Instantiation failed: {exc}"
        return record
    except Exception as exc:
        record["error"] = "".join(traceback.format_exception_only(type(exc), exc)).strip()
        return record


def inspect_tool_registry(path: Path) -> Dict[str, Any]:
    data = read_json(path)
    result: Dict[str, Any] = {"path": str(path), "exists": path.exists(), "current_trust_level": None, "rmc_mentions": 0}
    if data is not None:
        # Registry shape has shifted across patches, so search broadly.
        text = json.dumps(data, sort_keys=True)
        result["rmc_mentions"] = text.lower().count("rmc") + text.lower().count("recursive manifest")
        if isinstance(data, dict):
            result["current_trust_level"] = data.get("current_trust_level")
            if result["current_trust_level"] is None:
                for value in data.values():
                    if isinstance(value, dict) and "current_trust_level" in value:
                        result["current_trust_level"] = value.get("current_trust_level")
                        break
    return result


def grep_file(path: Path, needles: List[str]) -> Dict[str, Any]:
    result = {"path": str(path), "exists": path.exists(), "hits": {needle: 0 for needle in needles}}
    if not path.exists():
        return result
    try:
        text = path.read_text(errors="replace")
    except Exception as exc:
        result["error"] = str(exc)
        return result
    lower = text.lower()
    for needle in needles:
        result["hits"][needle] = lower.count(needle.lower())
    return result


def write_reports(report: Dict[str, Any], run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_dir / f"{report['timestamp']}_rmc_patch210_tool_wrapper_readiness.json"
    md_path = run_dir / f"{report['timestamp']}_rmc_patch210_tool_wrapper_readiness.md"
    latest_path = REPORT_ROOT / "latest_rmc_patch210_tool_wrapper_readiness.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True))

    lines: List[str] = []
    lines.append("# RMC Patch 210 Tool Wrapper Readiness Report")
    lines.append("")
    lines.append(f"Timestamp: `{report['timestamp']}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Read-Only Boundary")
    lines.append("- This scan did not modify Forge tools, Forge agent code, AI.Web wrappers, Identity Vault, databases, or Gilligan wiring.")
    lines.append("- This scan only inspected files/imports and wrote this report under Forge memory.")
    lines.append("")
    lines.append("## Forge Framework")
    for key, item in report["forge_framework"].items():
        if isinstance(item, dict):
            lines.append(f"- `{key}`: `{item.get('exists')}` — `{item.get('path')}`")
    reg = report["tool_registry"]
    lines.append(f"- tool registry trust level: `{reg.get('current_trust_level')}`")
    lines.append(f"- existing RMC-related registry mentions: `{reg.get('rmc_mentions')}`")
    lines.append("")
    lines.append("## Required RMC Imports")
    for item in report["required_imports"]:
        status = "PASS" if item.get("import_ok") and (not item.get("class") or item.get("class_ok")) else "FAIL"
        lines.append(f"- `{item['module']}` → `{item.get('class')}`: **{status}**")
        if item.get("instantiation_ok") is not None:
            lines.append(f"  - instantiation: `{item.get('instantiation_ok')}`")
        if item.get("error"):
            lines.append(f"  - error: `{item['error']}`")
    lines.append("")
    lines.append("## Optional Existing RMC Module Imports")
    for item in report["optional_imports"]:
        status = "PASS" if item.get("import_ok") else "WARN"
        lines.append(f"- `{item['module']}`: **{status}**")
        if item.get("error"):
            lines.append(f"  - error: `{item['error']}`")
    lines.append("")
    lines.append("## Proposed Read-Only Forge Tool Wrappers")
    for tool in report["proposed_read_only_tools"]:
        lines.append(f"- `{tool['name']}`")
        lines.append(f"  - purpose: {tool['purpose']}")
        lines.append(f"  - required: `{tool['required_module']}` / `{tool['required_class']}`")
        lines.append(f"  - write scope: {tool['write_scope']}")
    lines.append("")
    lines.append("## RMC Mentions in Forge Code")
    for key, item in report["forge_code_mentions"].items():
        lines.append(f"- `{key}`")
        for needle, count in item.get("hits", {}).items():
            lines.append(f"  - `{needle}`: `{count}`")
    lines.append("")
    lines.append("## Next Safe Step")
    lines.append(report["next_safe_step"])
    lines.append("")

    text = "\n".join(lines)
    md_path.write_text(text)
    latest_path.write_text(text)


def main() -> int:
    timestamp = now_stamp()
    run_dir = REPORT_ROOT / timestamp
    if str(RUNTIME_WRAPPERS) not in sys.path:
        sys.path.insert(0, str(RUNTIME_WRAPPERS))

    forge_framework = {
        key: {"path": str(path), "exists": path.exists()} for key, path in REQUIRED_FORGE_FILES.items()
    }

    required = [try_import(module, klass) for module, klass in REQUIRED_IMPORTS]
    optional = [try_import(module, klass) for module, klass in OPTIONAL_IMPORTS]
    registry = inspect_tool_registry(REQUIRED_FORGE_FILES["tool_registry"])
    forge_mentions = {
        key: grep_file(path, ["rmc", "recursive manifest", "phase_parse", "drift", "echo", "gilligan"])
        for key, path in REQUIRED_FORGE_FILES.items()
        if key in {"agent", "tools", "memory", "context_builder"}
    }

    required_pass = all(item.get("import_ok") and (not item.get("class") or item.get("class_ok")) for item in required)
    forge_pass = all(item["exists"] for key, item in forge_framework.items() if key != "tool_registry")
    registry_pass = forge_framework["tool_registry"]["exists"]

    verdict = "PASS" if required_pass and forge_pass and registry_pass else "HOLD"
    next_step = (
        "If this report passes, create Patch 211 to add a read-only `agents/forge/rmc_tools.py` wrapper and a standalone verifier. "
        "Do not register RMC tools in the live Forge dispatch surface until the wrapper itself passes import and no-write smoke tests."
        if verdict == "PASS"
        else "Hold integration. Fix missing imports or Forge framework files before writing any Forge RMC tool wrapper."
    )

    report: Dict[str, Any] = {
        "timestamp": timestamp,
        "home": str(HOME),
        "forge_root": str(FORGE_ROOT),
        "runtime_wrappers": str(RUNTIME_WRAPPERS),
        "verdict": verdict,
        "forge_framework": forge_framework,
        "tool_registry": registry,
        "required_imports": required,
        "optional_imports": optional,
        "forge_code_mentions": forge_mentions,
        "proposed_read_only_tools": PROPOSED_READ_ONLY_TOOLS,
        "next_safe_step": next_step,
    }
    write_reports(report, run_dir)
    print("RMC Patch 210 tool-wrapper readiness scan complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {REPORT_ROOT / 'latest_rmc_patch210_tool_wrapper_readiness.md'}")
    print(f"Verdict: {verdict}")
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
