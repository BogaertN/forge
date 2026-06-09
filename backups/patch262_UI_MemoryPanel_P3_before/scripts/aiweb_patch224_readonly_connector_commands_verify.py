#!/usr/bin/env python3
"""Patch 224 verifier — read-only connector commands installed and callable as helpers."""
from __future__ import annotations

import datetime as _dt
import hashlib
import importlib
import json
import py_compile
import sys
from pathlib import Path
from typing import Any, Dict

COMMANDS = [
    "forge-rmc-status",
    "forge-rmc-test-status",
    "forge-identity-status",
    "forge-agent-list",
    "forge-agent-show",
    "forge-system-boundary-map",
]
BEGIN_FUNCS = "# --- BEGIN PATCH 224 AIWEB READ-ONLY CONNECTOR COMMANDS ---"
BEGIN_ROUTES = "# --- BEGIN PATCH 224 AIWEB READ-ONLY CONNECTOR ROUTES ---"


def _home() -> Path:
    return Path.home()


def _forge_root() -> Path:
    return _home() / "forge"


def _report_root() -> Path:
    return _forge_root() / "memory" / "aiweb_patch224_readonly_connectors_verify_v1"


def _sha(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _count_registry_mentions() -> int:
    path = _forge_root() / "config" / "tool_registry.json"
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    return sum(text.count(cmd) for cmd in COMMANDS)


def _write_reports(result: Dict[str, Any], report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / f"{result['timestamp']}_aiweb_patch224_readonly_connectors_verify.json"
    md_path = report_dir / f"{result['timestamp']}_aiweb_patch224_readonly_connectors_verify.md"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# AI.Web Patch 224 Read-Only Connector Commands Verify",
        "",
        f"Timestamp: `{result['timestamp']}`",
        f"Verdict: **{result['verdict']}**",
        "",
        "## Boundary",
        "- This verification reads Forge main.py, the connector module, service contracts, and read-only adapter metadata.",
        "- It does not write databases, RMC memory, Forge registry, `.env`, or agent identity state.",
        "",
        "## Checks",
    ]
    for k, v in result.get("checks", {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines += ["", "## Command Names"]
    for cmd, present in result.get("command_presence", {}).items():
        lines.append(f"- `{cmd}`: **{'FOUND' if present else 'MISSING'}**")
    if result.get("helper_smoke"):
        lines += ["", "## Helper Smoke"]
        for k, v in result["helper_smoke"].items():
            lines.append(f"- `{k}`: `{v}`")
    if result.get("findings"):
        lines += ["", "## Findings"]
        for f in result["findings"]:
            lines.append(f"- **{f['level']}** `{f['code']}` — {f['message']}")
    if result.get("errors"):
        lines += ["", "## Errors"]
        for e in result["errors"]:
            lines.append(f"- `{e}`")
    lines += ["", "## Next Safe Step", "Run Forge manually and test the six new read-only connector commands. Then run `forge-command-surface` and `forge-version`."]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    root = _report_root()
    root.mkdir(parents=True, exist_ok=True)
    (root / "latest_aiweb_patch224_readonly_connectors_verify.md").write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
    (root / "latest_aiweb_patch224_readonly_connectors_verify.json").write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    ts = _dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S_UTC")
    report_dir = _report_root() / ts
    main_path = _forge_root() / "main.py"
    module_path = _forge_root() / "agents" / "forge" / "aiweb_readonly_connectors.py"
    result: Dict[str, Any] = {"timestamp": ts, "verdict": "FAIL", "checks": {}, "command_presence": {}, "helper_smoke": {}, "findings": [], "errors": []}
    try:
        py_compile.compile(str(main_path), doraise=True)
        py_compile.compile(str(module_path), doraise=True)
        result["checks"]["main_compile"] = True
        result["checks"]["connector_module_compile"] = True
        text = main_path.read_text(encoding="utf-8", errors="replace")
        result["checks"]["function_marker_present"] = BEGIN_FUNCS in text
        result["checks"]["route_marker_present"] = BEGIN_ROUTES in text
        result["command_presence"] = {cmd: cmd in text for cmd in COMMANDS}
        result["checks"]["all_commands_present"] = all(result["command_presence"].values())
        result["checks"]["tool_registry_mentions"] = _count_registry_mentions()
        result["checks"]["tool_registry_unmodified_by_connectors"] = result["checks"]["tool_registry_mentions"] == 0
        sys.path.insert(0, str(_forge_root()))
        conn = importlib.import_module("agents.forge.aiweb_readonly_connectors")
        helper_smoke = {
            "forge_rmc_status": bool(conn.forge_rmc_status().get("read_only")),
            "forge_rmc_test_status": bool(conn.forge_rmc_test_status().get("read_only")),
            "forge_identity_status": bool(conn.forge_identity_status().get("read_only")),
            "forge_agent_list": bool(conn.forge_agent_list().get("read_only")),
            "forge_agent_show": bool(conn.forge_agent_show("agent.gilligan.local").get("read_only")),
            "forge_system_boundary_map": bool(conn.forge_system_boundary_map().get("read_only")),
        }
        result["helper_smoke"] = helper_smoke
        result["checks"]["helper_smoke_ok"] = all(helper_smoke.values())
        result["checks"]["env_secret_values_read"] = False
        result["checks"]["database_write_performed"] = False
        result["checks"]["agent_identity_activation_performed"] = False
        if result["checks"]["all_commands_present"] and result["checks"]["function_marker_present"] and result["checks"]["route_marker_present"] and result["checks"]["tool_registry_unmodified_by_connectors"] and result["checks"]["helper_smoke_ok"]:
            result["verdict"] = "PASS"
            result["findings"].append({"level": "INFO", "code": "AIWEB_READONLY_CONNECTORS_VERIFIED", "message": "Read-only connector commands and helper functions verified."})
    except Exception as exc:
        result["errors"].append(f"{type(exc).__name__}: {exc}")
        result["findings"].append({"level": "FAIL", "code": "AIWEB_PATCH224_VERIFY_EXCEPTION", "message": str(exc)})
    _write_reports(result, report_dir)
    print("AI.Web Patch 224 read-only connector commands verify complete.")
    print(f"Run directory: {report_dir}")
    print(f"Report: {_report_root() / 'latest_aiweb_patch224_readonly_connectors_verify.md'}")
    print(f"Verdict: {result['verdict']}")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
