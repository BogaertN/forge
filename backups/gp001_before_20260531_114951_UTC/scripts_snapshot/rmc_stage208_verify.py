#!/usr/bin/env python3
"""
Patch 208 staged RMC module verifier.

Runs compile checks, unit tests, compatibility imports, and a miniature
phase→drift→echo smoke test without moving anything into live runtime paths.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "forge"
STAGE = ROOT / "staged_rmc_modules" / "patch208_missing_rmc_modules"
REPORT_ROOT = ROOT / "memory" / "rmc_stage208_verification_v1"

MODULE_TESTS = [
    ("phase_parser", "test_phase_state_parser.py"),
    ("drift_detection", "test_drift_detector.py"),
    ("echo_validator", "test_echo_validator.py"),
]

PY_FILES = [
    STAGE / "phase_parser" / "phase_state_parser.py",
    STAGE / "drift_detection" / "drift_detector.py",
    STAGE / "echo_validator" / "echo_validator.py",
    STAGE / "phase_state_parser" / "phase_state_parser.py",
    STAGE / "drift_arbitrator" / "drift_arbitrator.py",
    STAGE / "echo_gate" / "echo_gate.py",
]


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True)


def main() -> int:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    run_dir = REPORT_ROOT / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "timestamp": timestamp,
        "stage": str(STAGE),
        "compile": [],
        "tests": [],
        "compatibility_imports": {},
        "smoke": {},
        "verdict": "UNKNOWN",
    }

    if not STAGE.exists():
        report["verdict"] = "FAIL"
        report["error"] = f"stage path missing: {STAGE}"
        _write_reports(run_dir, report)
        print(f"FAIL: stage path missing: {STAGE}")
        return 1

    for py_file in PY_FILES:
        proc = run([sys.executable, "-m", "py_compile", str(py_file)])
        report["compile"].append({
            "file": str(py_file.relative_to(ROOT)),
            "returncode": proc.returncode,
            "stderr": proc.stderr,
        })

    for module_dir, test_name in MODULE_TESTS:
        proc = run([sys.executable, test_name], cwd=STAGE / module_dir)
        (run_dir / f"{module_dir}_stdout.txt").write_text(proc.stdout, encoding="utf-8")
        (run_dir / f"{module_dir}_stderr.txt").write_text(proc.stderr, encoding="utf-8")
        report["tests"].append({
            "module": module_dir,
            "test": test_name,
            "returncode": proc.returncode,
            "stdout_file": f"{module_dir}_stdout.txt",
            "stderr_file": f"{module_dir}_stderr.txt",
        })

    # Compatibility imports using isolated sys.path order.
    sys.path.insert(0, str(STAGE))
    try:
        from phase_parser.phase_state_parser import PhaseStateParser
        from drift_detection.drift_detector import DriftArbitrator
        from echo_validator.echo_validator import EchoGate
        from phase_state_parser.phase_state_parser import PhaseStateParser as PhaseStateParserCompat
        from drift_arbitrator.drift_arbitrator import DriftArbitrator as DriftArbitratorCompat
        from echo_gate.echo_gate import EchoGate as EchoGateCompat
        report["compatibility_imports"] = {
            "phase_parser.phase_state_parser": PhaseStateParser.__name__,
            "drift_detection.drift_detector": DriftArbitrator.__name__,
            "echo_validator.echo_validator": EchoGate.__name__,
            "phase_state_parser.phase_state_parser": PhaseStateParserCompat.__name__,
            "drift_arbitrator.drift_arbitrator": DriftArbitratorCompat.__name__,
            "echo_gate.echo_gate": EchoGateCompat.__name__,
        }

        parser = PhaseStateParser()
        phase = parser.parse("fix the missing RMC modules correctly")
        drift = DriftArbitrator().evaluate(
            text="fix the missing RMC modules correctly",
            current_phase=phase["phase_id"],
            phase_history=[4, 5],
        )
        manifest = {
            "id": "stage208",
            "phase": phase["phase_id"],
            "phase_name": phase["phase_name"],
            "conclusion": "Fix the missing RMC modules correctly",
            "confidence": 0.9,
            "drift_verdict": drift["verdict"],
            "projection_status": "READY" if drift["verdict"] != "BLOCK" else "BLOCKED",
            "claim_type": "instruction",
        }
        output = "Correction applied: Fix the missing RMC modules correctly"
        if drift["verdict"] == "WARN":
            output = "[note: drift detected] " + output
        if drift["verdict"] == "BLOCK":
            output = "[output blocked — drift severity too high to render]"
        accepted, score, note = EchoGate().validate(manifest, output)
        report["smoke"] = {
            "phase": phase,
            "drift_verdict": drift["verdict"],
            "echo_accepted": accepted,
            "echo_score": score,
            "echo_note": note,
        }
    except Exception as exc:
        report["compatibility_imports_error"] = repr(exc)

    compile_ok = all(item["returncode"] == 0 for item in report["compile"])
    tests_ok = all(item["returncode"] == 0 for item in report["tests"])
    smoke_ok = bool(report.get("smoke", {}).get("echo_accepted"))
    report["verdict"] = "PASS" if compile_ok and tests_ok and smoke_ok else "FAIL"

    _write_reports(run_dir, report)
    latest = REPORT_ROOT / "latest_rmc_stage208_verification.md"
    latest.write_text(_markdown(report), encoding="utf-8")

    print("RMC Stage 208 verification complete.")
    print(f"Run directory: {run_dir}")
    print(f"Report: {latest}")
    print(f"Verdict: {report['verdict']}")
    return 0 if report["verdict"] == "PASS" else 1


def _write_reports(run_dir: Path, report: dict):
    (run_dir / "rmc_stage208_verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (run_dir / "rmc_stage208_verification.md").write_text(_markdown(report), encoding="utf-8")


def _markdown(report: dict) -> str:
    lines = [
        "# RMC Stage 208 Verification Report",
        "",
        f"Timestamp: `{report.get('timestamp')}`",
        f"Stage: `{report.get('stage')}`",
        f"Verdict: **{report.get('verdict')}**",
        "",
        "## Compile Checks",
    ]
    for item in report.get("compile", []):
        status = "PASS" if item.get("returncode") == 0 else "FAIL"
        lines.append(f"- `{item.get('file')}`: **{status}**")
    lines.append("")
    lines.append("## Unit Tests")
    for item in report.get("tests", []):
        status = "PASS" if item.get("returncode") == 0 else "FAIL"
        lines.append(f"- `{item.get('module')}/{item.get('test')}`: **{status}**")
    lines.append("")
    lines.append("## Compatibility Imports")
    for key, value in report.get("compatibility_imports", {}).items():
        lines.append(f"- `{key}` → `{value}`")
    if report.get("compatibility_imports_error"):
        lines.append(f"- ERROR: `{report['compatibility_imports_error']}`")
    lines.append("")
    lines.append("## Smoke Test")
    smoke = report.get("smoke", {})
    if smoke:
        lines.append(f"- phase: `{smoke.get('phase', {}).get('phase_name')}` / `{smoke.get('phase', {}).get('phase_id')}`")
        lines.append(f"- drift verdict: `{smoke.get('drift_verdict')}`")
        lines.append(f"- echo accepted: `{smoke.get('echo_accepted')}`")
        lines.append(f"- echo score: `{smoke.get('echo_score')}`")
        lines.append(f"- note: `{smoke.get('echo_note')}`")
    else:
        lines.append("- smoke test did not complete")
    lines.append("")
    lines.append("## Next Safe Step")
    lines.append("If this report passes, create the next patch to copy staged modules into `~/aiweb/runtime_wrappers/` and run the integrated RMC orchestrator test. Do not wire Gilligan yet.")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
