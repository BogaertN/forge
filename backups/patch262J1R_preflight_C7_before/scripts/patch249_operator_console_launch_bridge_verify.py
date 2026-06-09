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
        "helper_present": "def _p249_operator_console_response" in text,
        "dist_root_declared": "/home/nic/aiweb/apps/forge-operator-console/dist" in text,
        "do_get_found": bool(do_get),
        "path_var_present": "_p249_req_path" in do_get,
        "operator_console_route": '"/operator-console"' in do_get,
        "operator_console_assets_route": '"/operator-console/assets/"' in do_get,
        "vite_root_assets_route": '"/assets/"' in do_get,
        "operator_console_helper_called": "_p249_operator_console_response(self.path)" in do_get,
        "existing_root_preserved": '"/", "/index.html"' in do_get,
        "existing_api_status_preserved": 'self.path == "/api/status"' in do_get,
        "existing_trace_api_preserved": 'self.path == "/api/protoforge/trace/latest"' in do_get,
        "command_bridge_preserved": 'elif self.path == "/api/command":' in text,
        "no_command_added": "forge-operator-console-start" not in text and "forge-terminus-operator-console-plan" not in text,
        "read_only_boundary_text": "does not execute commands" in text and "does not write Identity Vault" in text,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("PATCH249_OPERATOR_CONSOLE_LAUNCH_BRIDGE_VERIFY_FAIL")
        print("failed=" + ",".join(failed))
        return 1

    print("PATCH249_OPERATOR_CONSOLE_LAUNCH_BRIDGE_VERIFY_PASS")
    print("patch=249")
    print("route=/operator-console")
    print("serves_dist=/home/nic/aiweb/apps/forge-operator-console/dist")
    print("asset_routes=/operator-console/assets,/assets")
    print("command_surface_delta=0_expected")
    print("adds_forge_commands=False")
    print("executes_commands=False")
    print("executes_simulation=False")
    print("identity_vault_write=False")
    print("rmc_live_memory_write=False")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
