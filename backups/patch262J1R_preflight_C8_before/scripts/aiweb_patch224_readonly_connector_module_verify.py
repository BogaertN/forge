#!/usr/bin/env python3
# identity/aiweb Patch 224 verifier
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import py_compile
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
MODULE_PATH = FORGE_ROOT / "agents" / "forge" / "aiweb_readonly_connectors.py"
REPORT_ROOT = FORGE_ROOT / "memory" / "aiweb_patch224_readonly_connector_module_v1"
EXPECTED_COMMANDS = [
    "forge-rmc-status",
    "forge-rmc-test-status",
    "forge-identity-status",
    "forge-agent-list",
    "forge-agent-show",
    "forge-system-boundary-map",
]


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("aiweb_readonly_connectors_patch224", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def write_reports(report: Dict[str, Any]) -> None:
    ts = report["timestamp"]
    run_dir = REPORT_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_dir / f"{ts}_aiweb_patch224_readonly_connector_module.json"
    md_path = run_dir / f"{ts}_aiweb_patch224_readonly_connector_module.md"
    latest_json = REPORT_ROOT / "latest_aiweb_patch224_readonly_connector_module.json"
    latest_md = REPORT_ROOT / "latest_aiweb_patch224_readonly_connector_module.md"

    json_text = json.dumps(report, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")

    lines = []
    lines.append("# AI.Web Patch 224 Read-Only Connector Module Verify")
    lines.append("")
    lines.append(f"Timestamp: `{ts}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    for item in report["boundary"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Module")
    lines.append(f"- path: `{report['module']['path']}`")
    lines.append(f"- exists: `{report['module']['exists']}`")
    lines.append(f"- sha256: `{report['module']['sha256']}`")
    lines.append(f"- compile_ok: `{report['module']['compile_ok']}`")
    lines.append(f"- import_ok: `{report['module']['import_ok']}`")
    lines.append(f"- read_only_constant: `{report['module']['read_only_constant']}`")
    lines.append(f"- connector_version: `{report['module']['connector_version']}`")
    lines.append("")
    lines.append("## Expected Connector Preview Commands")
    for cmd, ok in report["expected_commands"].items():
        lines.append(f"- `{cmd}`: **{'FOUND' if ok else 'MISSING'}**")
    lines.append("")
    lines.append("## Preview Smoke")
    for cmd, result in report["preview_smoke"].items():
        lines.append(f"- `{cmd}`: **{'PASS' if result.get('pass') else 'FAIL'}**")
        summary = result.get("summary")
        if summary:
            lines.append(f"  - summary: `{summary}`")
    lines.append("")
    lines.append("## No-Mutation / Safety")
    for key, value in report["safety"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Findings")
    for finding in report["findings"]:
        lines.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    lines.append("")
    lines.append("## Next Safe Step")
    lines.append("If this passes, create the Forge command-surface registration patch for the six read-only connector commands. No memory writes, app creation, or agent mutation.")
    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")


def main() -> int:
    ts = now()
    report: Dict[str, Any] = {
        "timestamp": ts,
        "verdict": "FAIL",
        "boundary": [
            "This verification imports and tests the staged AI.Web read-only connector module only.",
            "No Forge command registration is performed by this patch.",
            "No Identity Vault database writes are performed.",
            "No RMC memory writes are performed.",
            "No .env secret values are read.",
            "No agent identity activation is performed.",
        ],
        "module": {
            "path": str(MODULE_PATH),
            "exists": MODULE_PATH.exists(),
            "sha256": sha256(MODULE_PATH),
            "compile_ok": False,
            "import_ok": False,
            "read_only_constant": False,
            "connector_version": None,
        },
        "expected_commands": {},
        "preview_smoke": {},
        "safety": {
            "forge_tool_registry_modified": False,
            "database_write_performed": False,
            "rmc_memory_write_performed": False,
            "env_secret_values_read": False,
            "agent_identity_activation_performed": False,
            "command_surface_modified_by_this_patch": False,
        },
        "findings": [],
    }

    try:
        py_compile.compile(str(MODULE_PATH), doraise=True)
        report["module"]["compile_ok"] = True
    except Exception as exc:
        report["findings"].append({"level": "FAIL", "code": "AIWEB_CONNECTOR_MODULE_COMPILE_FAIL", "message": str(exc)})
        write_reports(report)
        print("AI.Web Patch 224 read-only connector module verification complete.")
        print(f"Report: {REPORT_ROOT/'latest_aiweb_patch224_readonly_connector_module.md'}")
        print("Verdict: FAIL")
        return 1

    try:
        mod = load_module(MODULE_PATH)
        report["module"]["import_ok"] = True
        report["module"]["read_only_constant"] = bool(getattr(mod, "READ_ONLY", False) is True)
        report["module"]["connector_version"] = getattr(mod, "CONNECTOR_VERSION", None)
        funcs = getattr(mod, "CONNECTOR_FUNCTIONS", {})
        report["expected_commands"] = {cmd: cmd in funcs for cmd in EXPECTED_COMMANDS}

        previews = [
            ("forge-rmc-status", []),
            ("forge-rmc-test-status", []),
            ("forge-identity-status", []),
            ("forge-agent-list", []),
            ("forge-agent-show", ["agent.gilligan.local"]),
            ("forge-system-boundary-map", []),
        ]
        for cmd, args in previews:
            try:
                result = mod.run_connector_preview(cmd, *args)
                ok = bool(result.get("read_only") is True and "function" in result)
                # agent-show may be not found because database is empty. That is still a pass if it stayed read-only.
                if cmd == "forge-agent-show":
                    ok = ok and result.get("agent_identity_activation_performed") is False
                summary = {
                    "ok": result.get("ok"),
                    "read_only": result.get("read_only"),
                    "keys": sorted(list(result.keys()))[:12],
                }
                if cmd == "forge-rmc-status":
                    summary["rmc_contract_ok"] = result.get("contract", {}).get("json_ok")
                if cmd == "forge-identity-status":
                    summary["identity_contract_ok"] = result.get("contract", {}).get("json_ok")
                    summary["canonical_db_ok"] = result.get("canonical_db", {}).get("ok")
                if cmd == "forge-agent-list":
                    summary["returned"] = result.get("returned")
                if cmd == "forge-system-boundary-map":
                    summary["contracts"] = sorted(result.get("contracts", {}).keys())
                report["preview_smoke"][cmd] = {"pass": ok, "summary": summary}
            except Exception as exc:
                report["preview_smoke"][cmd] = {"pass": False, "summary": {"error": str(exc)}}
    except Exception as exc:
        report["findings"].append({"level": "FAIL", "code": "AIWEB_CONNECTOR_MODULE_IMPORT_FAIL", "message": str(exc)})

    all_expected = all(report["expected_commands"].values()) if report["expected_commands"] else False
    all_smoke = all(item.get("pass") for item in report["preview_smoke"].values()) if report["preview_smoke"] else False
    ready = (
        report["module"]["compile_ok"]
        and report["module"]["import_ok"]
        and report["module"]["read_only_constant"]
        and all_expected
        and all_smoke
    )

    if ready:
        report["verdict"] = "PASS"
        report["findings"].append({
            "level": "INFO",
            "code": "AIWEB_READONLY_CONNECTOR_MODULE_READY",
            "message": "Connector preview module is importable, read-only, and all six preview functions smoke-tested."
        })
    else:
        report["verdict"] = "FAIL"
        if not all_expected:
            report["findings"].append({
                "level": "FAIL",
                "code": "AIWEB_CONNECTOR_COMMANDS_MISSING",
                "message": "One or more expected connector preview command names are missing from CONNECTOR_FUNCTIONS."
            })
        if not all_smoke:
            report["findings"].append({
                "level": "FAIL",
                "code": "AIWEB_CONNECTOR_SMOKE_FAIL",
                "message": "One or more read-only connector preview calls failed smoke testing."
            })

    write_reports(report)
    print("AI.Web Patch 224 read-only connector module verification complete.")
    print(f"Run directory: {REPORT_ROOT / ts}")
    print(f"Report: {REPORT_ROOT/'latest_aiweb_patch224_readonly_connector_module.md'}")
    print(f"JSON report: {REPORT_ROOT/'latest_aiweb_patch224_readonly_connector_module.json'}")
    print(f"Verdict: {report['verdict']}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
