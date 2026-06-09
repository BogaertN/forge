#!/usr/bin/env python3
"""Patch 209 integrated RMC verification.

Checks that missing modules are installed into ~/aiweb/runtime_wrappers and that
S19AK orchestrator now runs as a unified pipeline. Writes JSON/Markdown reports.
"""
from __future__ import annotations

import json
import os
import py_compile
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

HOME = Path.home()
FORGE = HOME / "forge"
AIWEB = HOME / "aiweb"
WRAPPERS = AIWEB / "runtime_wrappers"
OUT_ROOT = FORGE / "memory" / "rmc_patch209_integrated_verify_v1"

MODULE_FILES = [
    WRAPPERS / "phase_parser" / "phase_state_parser.py",
    WRAPPERS / "phase_state_parser" / "phase_state_parser.py",
    WRAPPERS / "drift_detection" / "drift_detector.py",
    WRAPPERS / "drift_arbitrator" / "drift_arbitrator.py",
    WRAPPERS / "echo_validator" / "echo_validator.py",
    WRAPPERS / "echo_gate" / "echo_gate.py",
    WRAPPERS / "rmc_orchestrator" / "rmc_orchestrator.py",
]

TESTS = [
    WRAPPERS / "phase_parser" / "test_phase_state_parser.py",
    WRAPPERS / "drift_detection" / "test_drift_detector.py",
    WRAPPERS / "echo_validator" / "test_echo_validator.py",
    WRAPPERS / "rmc_orchestrator" / "test_rmc_orchestrator.py",
]


def run(cmd: List[str], cwd: Path | None = None) -> Dict:
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {
        "cmd": cmd,
        "cwd": str(cwd) if cwd else None,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-6000:],
        "stderr": proc.stderr[-6000:],
    }


def compile_checks() -> List[Dict]:
    rows = []
    for path in MODULE_FILES:
        row = {"path": str(path.relative_to(HOME)) if path.exists() else str(path), "exists": path.exists(), "pass": False, "error": ""}
        if path.exists():
            try:
                py_compile.compile(str(path), doraise=True)
                row["pass"] = True
            except Exception as exc:
                row["error"] = str(exc)
        rows.append(row)
    return rows


def import_smoke() -> Dict:
    code = f"""
import sys
from pathlib import Path
base = Path(r'{WRAPPERS}')
sys.path.insert(0, str(base))
from phase_parser.phase_state_parser import PhaseStateParser
from phase_state_parser.phase_state_parser import PhaseStateParser as PhaseStateParserCompat
from drift_detection.drift_detector import DriftArbitrator
from drift_arbitrator.drift_arbitrator import DriftArbitrator as DriftArbitratorCompat
from echo_validator.echo_validator import EchoGate
from echo_gate.echo_gate import EchoGate as EchoGateCompat
from rmc_orchestrator.rmc_orchestrator import RMCOrchestrator, RMCResult
rmc = RMCOrchestrator()
r = rmc.process('Hello, starting a new project')
assert isinstance(r, RMCResult)
assert r.phase == 1
assert r.accepted is True
print('IMPORT_SMOKE_PASS', r.summary())
"""
    return run([sys.executable, "-c", code])


def run_tests() -> List[Dict]:
    results = []
    for test_path in TESTS:
        if not test_path.exists():
            results.append({"path": str(test_path.relative_to(HOME)), "exists": False, "returncode": 99, "stdout": "", "stderr": "missing test"})
            continue
        results.append(run([sys.executable, test_path.name], cwd=test_path.parent) | {"path": str(test_path.relative_to(HOME)), "exists": True})
    return results


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    run_dir = OUT_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    compiles = compile_checks()
    smoke = import_smoke()
    tests = run_tests()

    verdict = (
        all(row["pass"] for row in compiles)
        and smoke["returncode"] == 0
        and all(t["returncode"] == 0 for t in tests)
    )

    report = {
        "timestamp": ts,
        "wrappers": str(WRAPPERS),
        "verdict": "PASS" if verdict else "FAIL",
        "compile_checks": compiles,
        "import_smoke": smoke,
        "tests": tests,
        "next_safe_step": "Create a read-only Forge RMC tool-wrapper scan; do not wire Gilligan yet." if verdict else "Stop and inspect failing stdout/stderr before continuing.",
    }

    json_path = run_dir / f"{ts}_rmc_patch209_integrated_verify.json"
    md_path = run_dir / f"{ts}_rmc_patch209_integrated_verify.md"
    latest = OUT_ROOT / "latest_rmc_patch209_integrated_verify.md"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# RMC Patch 209 Integrated Verification Report",
        "",
        f"Timestamp: `{ts}`",
        f"Wrappers: `{WRAPPERS}`",
        f"Verdict: **{report['verdict']}**",
        "",
        "## Compile Checks",
    ]
    for row in compiles:
        status = "PASS" if row["pass"] else "FAIL"
        lines.append(f"- `{row['path']}`: **{status}**")
        if row.get("error"):
            lines.append(f"  - error: `{row['error']}`")
    lines += ["", "## Import Smoke", f"- returncode: `{smoke['returncode']}`"]
    if smoke["stdout"].strip():
        lines.append("```text")
        lines.append(smoke["stdout"].strip())
        lines.append("```")
    if smoke["stderr"].strip():
        lines.append("stderr:")
        lines.append("```text")
        lines.append(smoke["stderr"].strip())
        lines.append("```")
    lines += ["", "## Unit / Integration Tests"]
    for t in tests:
        status = "PASS" if t["returncode"] == 0 else "FAIL"
        lines.append(f"- `{t['path']}`: **{status}** returncode=`{t['returncode']}`")
        if t["returncode"] != 0:
            if t.get("stdout"):
                lines.append("  - stdout:")
                lines.append("```text")
                lines.append(t["stdout"].strip())
                lines.append("```")
            if t.get("stderr"):
                lines.append("  - stderr:")
                lines.append("```text")
                lines.append(t["stderr"].strip())
                lines.append("```")
    lines += ["", "## Next Safe Step", report["next_safe_step"], ""]

    md = "\n".join(lines)
    md_path.write_text(md, encoding="utf-8")
    latest.write_text(md, encoding="utf-8")

    print("RMC Patch 209 integrated verification complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest}")
    print(f"Verdict: {report['verdict']}")
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
