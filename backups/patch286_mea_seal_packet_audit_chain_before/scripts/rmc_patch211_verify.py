#!/usr/bin/env python3
"""Patch 211 verifier: validates read-only Forge RMC wrapper file."""
from __future__ import annotations

import importlib.util
import json
import py_compile
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

HOME = Path.home()
FORGE = HOME / "forge"
AIWEB = HOME / "aiweb"
REPORT_ROOT = FORGE / "memory" / "rmc_patch211_readonly_wrapper_v1"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
RUN_DIR = REPORT_ROOT / STAMP
WRAPPER_PATH = FORGE / "agents" / "forge" / "rmc_tools.py"
REGISTRY_PATH = FORGE / "config" / "tool_registry.json"


def run(cmd: List[str], cwd: Path | None = None) -> Dict[str, Any]:
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def import_wrapper():
    spec = importlib.util.spec_from_file_location("forge_patch211_rmc_tools", WRAPPER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load spec for {WRAPPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def registry_rmc_mentions() -> int:
    if not REGISTRY_PATH.exists():
        return -1
    text = REGISTRY_PATH.read_text(encoding="utf-8", errors="replace").lower()
    return text.count("rmc") + text.count("recursive manifest")


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    report: Dict[str, Any] = {
        "timestamp": STAMP,
        "wrapper_path": str(WRAPPER_PATH),
        "verdict": "FAIL",
        "checks": {},
        "wrapper_smoke": {},
        "boundaries": {
            "registered_tools_modified": False,
            "gilligan_wired": False,
            "identity_vault_touched": False,
            "read_only_wrapper_only": True,
        },
    }

    failures: List[str] = []

    report["checks"]["wrapper_exists"] = WRAPPER_PATH.exists()
    if not WRAPPER_PATH.exists():
        failures.append(f"missing wrapper: {WRAPPER_PATH}")
    else:
        try:
            py_compile.compile(str(WRAPPER_PATH), doraise=True)
            report["checks"]["wrapper_compile"] = True
        except Exception as exc:
            report["checks"]["wrapper_compile"] = False
            report["checks"]["wrapper_compile_error"] = str(exc)
            failures.append("wrapper compile failed")

    before_mentions = registry_rmc_mentions()
    report["checks"]["tool_registry_exists"] = REGISTRY_PATH.exists()
    report["checks"]["tool_registry_rmc_mentions"] = before_mentions

    # Patch 211 must not register live RMC tools yet.
    if before_mentions not in (0, -1):
        failures.append("tool registry already contains RMC mentions; live registration boundary is not clean")

    required_runtime_paths = [
        AIWEB / "runtime_wrappers" / "phase_parser" / "phase_state_parser.py",
        AIWEB / "runtime_wrappers" / "drift_detection" / "drift_detector.py",
        AIWEB / "runtime_wrappers" / "echo_validator" / "echo_validator.py",
        AIWEB / "runtime_wrappers" / "rmc_orchestrator" / "rmc_orchestrator.py",
    ]
    runtime_presence = {str(p.relative_to(HOME)): p.exists() for p in required_runtime_paths}
    report["checks"]["runtime_presence"] = runtime_presence
    for rel, exists in runtime_presence.items():
        if not exists:
            failures.append(f"missing runtime dependency: {rel}")

    if not failures:
        try:
            module = import_wrapper()
            report["checks"]["wrapper_import"] = True
            report["checks"]["read_only_flag"] = bool(getattr(module, "RMC_READ_ONLY", False))
            if not report["checks"]["read_only_flag"]:
                failures.append("RMC_READ_ONLY flag is not true")

            sample_manifest = {
                "id": "patch211-verify",
                "phase": 6,
                "phase_name": "Grace",
                "conclusion": "Correct the loop before projection.",
                "confidence": 0.9,
                "novelty": 0.1,
                "drift_verdict": "ALLOW",
                "projection_status": "READY",
            }
            smoke = {
                "phase": module.rmc_phase_parse_preview("We need to verify the RMC wrapper before wiring tools."),
                "drift": module.rmc_drift_check_preview("This is drifting and trying to project now.", current_phase=5, phase_history=[1, 4, 5]),
                "echo": module.rmc_echo_validate_preview("Correct the loop before projection.", sample_manifest),
                "pipeline": module.rmc_pipeline_preview("Verify a read-only RMC preview trace."),
            }
            report["wrapper_smoke"] = smoke
            for name, result in smoke.items():
                if not isinstance(result, dict) or not result.get("ok"):
                    failures.append(f"smoke failed for {name}: {result}")
            if smoke.get("pipeline", {}).get("result", {}).get("accepted") is not True:
                failures.append("pipeline preview did not return accepted=True")
        except Exception as exc:
            report["checks"]["wrapper_import"] = False
            report["checks"]["wrapper_import_error"] = str(exc)
            failures.append(f"wrapper import/smoke failed: {exc}")

    # Verify the registry file did not change while the verifier ran.
    after_mentions = registry_rmc_mentions()
    report["checks"]["tool_registry_rmc_mentions_after"] = after_mentions
    if after_mentions != before_mentions:
        failures.append("tool registry RMC mention count changed during verification")

    report["failures"] = failures
    report["verdict"] = "PASS" if not failures else "FAIL"

    json_path = RUN_DIR / f"{STAMP}_rmc_patch211_readonly_wrapper.json"
    md_path = RUN_DIR / f"{STAMP}_rmc_patch211_readonly_wrapper.md"
    latest_path = REPORT_ROOT / "latest_rmc_patch211_readonly_wrapper.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    lines: List[str] = []
    lines.append("# RMC Patch 211 Read-Only Wrapper Verification Report")
    lines.append("")
    lines.append(f"Timestamp: `{STAMP}`")
    lines.append(f"Wrapper: `{WRAPPER_PATH}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append("")
    lines.append("## Boundary")
    lines.append("- Patch 211 creates `forge/agents/forge/rmc_tools.py` only as an importable wrapper.")
    lines.append("- It does not register Forge tools.")
    lines.append("- It does not wire Gilligan.")
    lines.append("- It does not touch Identity Vault, databases, or persistent RMC memory.")
    lines.append("")
    lines.append("## Checks")
    lines.append(f"- wrapper exists: `{report['checks'].get('wrapper_exists')}`")
    lines.append(f"- wrapper compile: `{report['checks'].get('wrapper_compile')}`")
    lines.append(f"- wrapper import: `{report['checks'].get('wrapper_import')}`")
    lines.append(f"- read-only flag: `{report['checks'].get('read_only_flag')}`")
    lines.append(f"- tool registry RMC mentions before: `{before_mentions}`")
    lines.append(f"- tool registry RMC mentions after: `{after_mentions}`")
    lines.append("")
    lines.append("## Runtime Dependencies")
    for rel, exists in runtime_presence.items():
        lines.append(f"- `{rel}`: **{'FOUND' if exists else 'MISSING'}**")
    lines.append("")
    lines.append("## Wrapper Smoke")
    for name, result in report.get("wrapper_smoke", {}).items():
        ok = result.get("ok") if isinstance(result, dict) else False
        lines.append(f"- `{name}`: **{'PASS' if ok else 'FAIL'}**")
        if name == "phase" and ok:
            res = result.get("result", {})
            lines.append(f"  - phase: `{res.get('phase_name')}` / `{res.get('phase_number') or res.get('phase_id')}`")
        if name == "drift" and ok:
            res = result.get("result", {})
            lines.append(f"  - verdict: `{res.get('verdict')}`")
        if name == "echo" and ok:
            res = result.get("result", {})
            lines.append(f"  - accepted: `{res.get('accepted')}` score: `{res.get('score')}`")
        if name == "pipeline" and ok:
            res = result.get("result", {})
            lines.append(f"  - accepted: `{res.get('accepted')}` phase: `{res.get('phase')}` echo: `{res.get('echo_score')}`")
    lines.append("")
    if failures:
        lines.append("## Failures")
        for failure in failures:
            lines.append(f"- {failure}")
        lines.append("")
    lines.append("## Next Safe Step")
    lines.append("If this passes, create Patch 212 to register the read-only RMC preview functions in Forge's tool surface. Still do not wire Gilligan personality yet.")
    lines.append("")

    md = "\n".join(lines)
    md_path.write_text(md, encoding="utf-8")
    latest_path.write_text(md, encoding="utf-8")

    print("RMC Patch 211 read-only wrapper verification complete.")
    print(f"Run directory: {RUN_DIR}")
    print(f"Report: {latest_path}")
    print(f"Verdict: {report['verdict']}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
