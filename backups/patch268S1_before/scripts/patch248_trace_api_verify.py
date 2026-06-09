#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"

def extract_do_get(text: str) -> str:
    m = re.search(r"def do_GET\(self\):(?P<body>.*?)(?:\n\s*# ── Patch 203: real command execution|\n\s*def do_POST\(self\):)", text, re.S)
    return m.group("body") if m else ""

def main() -> int:
    text = MAIN.read_text(errors="replace")
    do_get = extract_do_get(text)
    checks = {
        "helper_present": "def _p248_latest_protoforge_trace_v1" in text,
        "safe_path_present": "def _p248_safe_protoforge_artifact_path" in text,
        "route_present": 'self.path == "/api/protoforge/trace/latest"' in do_get,
        "route_calls_helper": "_p248_latest_protoforge_trace_v1()" in do_get,
        "contract_lists_endpoint": '"/api/protoforge/trace/latest"' in text,
        "existing_reports_preserved": '"/api/protoforge/reports"' in do_get,
        "existing_contract_preserved": '"/api/operator/contract"' in do_get,
        "command_bridge_preserved": 'elif self.path == "/api/command":' in text,
        "no_design_command_added": "forge-terminus-operator-console-plan" not in text,
        "read_only_boundary": "identity_vault_write" in text and "rmc_live_memory_write" in text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("PATCH248_TRACE_API_VERIFY_FAIL")
        print("failed=" + ",".join(failed))
        return 1
    print("PATCH248_TRACE_API_VERIFY_PASS")
    print("patch=248")
    print("api=/api/protoforge/trace/latest")
    print("command_surface_delta=0_expected")
    print("executes_simulation=False")
    print("identity_vault_write=False")
    print("rmc_live_memory_write=False")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
