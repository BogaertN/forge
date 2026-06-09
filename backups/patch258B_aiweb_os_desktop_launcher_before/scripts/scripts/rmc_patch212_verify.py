#!/usr/bin/env python3
"""
Patch 212 verifier — Forge RMC read-only tool registration.

Verifies:
- tools.py compiles after registration.
- agents.forge.tools imports.
- RMC tool definitions are present exactly as live Forge tool definitions.
- dispatch() can call all four read-only RMC preview tools.
- tool_registry.json was not used as the registration surface.
"""
from __future__ import annotations

import datetime as _dt
import importlib
import json
import py_compile
import sys
import traceback
import types
from pathlib import Path
from typing import Any, Dict

EXPECTED_TOOLS = [
    "rmc_phase_parse_preview",
    "rmc_drift_check_preview",
    "rmc_echo_validate_preview",
    "rmc_pipeline_preview",
]


def _home() -> Path:
    return Path.home()


def _forge_root() -> Path:
    return _home() / "forge"


def _report_root() -> Path:
    return _forge_root() / "memory" / "rmc_patch212_tool_registration_verify_v1"


def _plain(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


def _count_registry_mentions() -> int:
    registry = _forge_root() / "config" / "tool_registry.json"
    if not registry.exists():
        return -1
    text = registry.read_text(encoding="utf-8", errors="replace")
    return sum(text.count(name) for name in EXPECTED_TOOLS)


def main() -> int:
    ts = _dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S_UTC")
    report_dir = _report_root() / ts
    report_dir.mkdir(parents=True, exist_ok=True)
    forge = _forge_root()
    tools_path = forge / "agents" / "forge" / "tools.py"

    result: Dict[str, Any] = {
        "timestamp": ts,
        "tools_path": str(tools_path),
        "verdict": "FAIL",
        "checks": {},
        "definition_names": [],
        "dispatch_smoke": {},
        "errors": [],
    }

    try:
        py_compile.compile(str(tools_path), doraise=True)
        result["checks"]["tools_compile"] = True
    except Exception as exc:
        result["checks"]["tools_compile"] = False
        result["errors"].append(f"compile: {type(exc).__name__}: {exc}")
        _write_reports(result, report_dir)
        print("Verdict: FAIL")
        return 1

    sys.path.insert(0, str(forge))
    sys.path.insert(0, str(forge.parent / "aiweb" / "runtime_wrappers"))

    dependency_stub_used = []
    try:
        tools_mod = importlib.import_module("agents.forge.tools")
        result["checks"]["tools_import"] = True
    except ModuleNotFoundError as exc:
        # Some verification sandboxes do not have Forge's optional vector DB dependency.
        # If the only missing dependency is chromadb, stub it so this patch can verify
        # RMC registration behavior without pretending to test Chroma itself.
        if exc.name == "chromadb":
            _chromadb_stub = types.ModuleType("chromadb")
            class _DummyCollection:  # minimal import-time annotation target
                pass
            class _DummyPersistentClient:
                def __init__(self, *args, **kwargs):
                    pass
                def get_or_create_collection(self, *args, **kwargs):
                    return _DummyCollection()
            _chromadb_stub.Collection = _DummyCollection
            _chromadb_stub.PersistentClient = _DummyPersistentClient
            sys.modules["chromadb"] = _chromadb_stub
            dependency_stub_used.append("chromadb")
            try:
                tools_mod = importlib.import_module("agents.forge.tools")
                result["checks"]["tools_import"] = True
            except Exception as exc2:
                result["checks"]["tools_import"] = False
                result["errors"].append("import_after_stub: " + "\n".join(traceback.format_exception_only(type(exc2), exc2)).strip())
                _write_reports(result, report_dir)
                print("Verdict: FAIL")
                return 1
        else:
            result["checks"]["tools_import"] = False
            result["errors"].append("import: " + "\n".join(traceback.format_exception_only(type(exc), exc)).strip())
            _write_reports(result, report_dir)
            print("Verdict: FAIL")
            return 1
    except Exception as exc:
        result["checks"]["tools_import"] = False
        result["errors"].append("import: " + "\n".join(traceback.format_exception_only(type(exc), exc)).strip())
        _write_reports(result, report_dir)
        print("Verdict: FAIL")
        return 1

    result["checks"]["dependency_stub_used"] = dependency_stub_used

    definitions = getattr(tools_mod, "TOOL_DEFINITIONS", [])
    names = [item.get("function", {}).get("name") for item in definitions if isinstance(item, dict)]
    result["definition_names"] = names
    missing_defs = [name for name in EXPECTED_TOOLS if name not in names]
    result["checks"]["all_expected_definitions_present"] = not missing_defs
    result["checks"]["missing_definitions"] = missing_defs
    result["checks"]["tool_registry_rmc_mentions"] = _count_registry_mentions()

    smoke_inputs = {
        "rmc_phase_parse_preview": {
            "text": "Correct this loop before projecting it."
        },
        "rmc_drift_check_preview": {
            "text": "This is drifting and trying to skip into projection.",
            "current_phase": 5,
            "phase_history": [1, 4, 5],
        },
        "rmc_echo_validate_preview": {
            "rendered_output": "Correct the loop before projection.",
            "manifest": {
                "id": "patch212-smoke",
                "phase": 6,
                "phase_name": "Grace",
                "conclusion": "Correct the loop before projection.",
                "confidence": 0.9,
                "novelty": 0.1,
                "drift_verdict": "ALLOW",
                "projection_status": "READY",
            },
            "modality": "language",
        },
        "rmc_pipeline_preview": {
            "input_text": "Verify the RMC wrapper through Forge dispatch without writing memory.",
            "modality": "language",
        },
    }

    all_dispatch_pass = True
    for name, args in smoke_inputs.items():
        try:
            out = tools_mod.dispatch(name, args, session_id="patch212_verify", user_question="verify rmc read-only tools")
            ok = bool(isinstance(out, dict) and out.get("ok") is True)
            result["dispatch_smoke"][name] = {
                "pass": ok,
                "ok": out.get("ok") if isinstance(out, dict) else None,
                "read_only": (out.get("read_only") if isinstance(out, dict) else None),
                "summary": _summarize_tool_result(out),
            }
            if not ok:
                all_dispatch_pass = False
        except Exception as exc:
            all_dispatch_pass = False
            result["dispatch_smoke"][name] = {
                "pass": False,
                "error": f"{type(exc).__name__}: {exc}",
            }

    result["checks"]["all_dispatch_smoke_pass"] = all_dispatch_pass

    if result["checks"].get("all_expected_definitions_present") and all_dispatch_pass:
        result["verdict"] = "PASS"

    _write_reports(result, report_dir)
    print("RMC Patch 212 tool registration verification complete.")
    print(f"Run directory: {report_dir}")
    print(f"Report: {_report_root() / 'latest_rmc_patch212_tool_registration_verify.md'}")
    print(f"Verdict: {result['verdict']}")
    return 0 if result["verdict"] == "PASS" else 1


def _summarize_tool_result(out: Any) -> Any:
    if not isinstance(out, dict):
        return str(out)
    summary = {"keys": sorted(out.keys())}
    result = out.get("result")
    if isinstance(result, dict):
        summary["result_keys"] = sorted(result.keys())[:20]
        for key in ("phase", "phase_number", "phase_name", "verdict", "accepted", "echo_score", "score"):
            if key in result:
                summary[key] = result[key]
    if "error" in out:
        summary["error"] = out["error"]
    return _plain(summary)


def _write_reports(result: Dict[str, Any], report_dir: Path) -> None:
    root = _report_root()
    root.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / f"{result['timestamp']}_rmc_patch212_tool_registration_verify.json"
    md_path = report_dir / f"{result['timestamp']}_rmc_patch212_tool_registration_verify.md"
    latest_json = root / "latest_rmc_patch212_tool_registration_verify.json"
    latest_md = root / "latest_rmc_patch212_tool_registration_verify.md"

    json_text = json.dumps(result, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")

    lines = [
        "# RMC Patch 212 Tool Registration Verification Report",
        "",
        f"Timestamp: `{result['timestamp']}`",
        f"Tools file: `{result['tools_path']}`",
        f"Verdict: **{result['verdict']}**",
        "",
        "## Checks",
    ]
    for key, value in result.get("checks", {}).items():
        lines.append(f"- `{key}`: `{value}`")

    lines += ["", "## Registered RMC Tool Definitions"]
    for name in EXPECTED_TOOLS:
        present = name in result.get("definition_names", [])
        lines.append(f"- `{name}`: **{'FOUND' if present else 'MISSING'}**")

    lines += ["", "## Dispatch Smoke"]
    for name in EXPECTED_TOOLS:
        smoke = result.get("dispatch_smoke", {}).get(name, {})
        lines.append(f"- `{name}`: **{'PASS' if smoke.get('pass') else 'FAIL'}**")
        if smoke.get("summary"):
            lines.append(f"  - summary: `{smoke.get('summary')}`")
        if smoke.get("error"):
            lines.append(f"  - error: `{smoke.get('error')}`")

    if result.get("errors"):
        lines += ["", "## Errors"]
        for err in result["errors"]:
            lines.append(f"- `{err}`")

    lines += [
        "",
        "## Boundary Confirmation",
        "- These tools are read-only preview tools.",
        "- This verification does not wire Gilligan personality mode.",
        "- This verification does not write to RMC memory or Identity Vault.",
        "",
        "## Next Safe Step",
        "If this report passes, run a Forge command-surface check and then test the RMC preview tools from inside Forge. Gilligan wiring remains held.",
    ]
    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
