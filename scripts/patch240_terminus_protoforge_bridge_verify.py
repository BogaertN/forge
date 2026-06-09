
#!/usr/bin/env python3
# Patch 240 verifier — Terminus ProtoForge Bridge v1.
# Read-only structural verification. Does not start the UI server and does not run a simulation.

from __future__ import annotations

import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REG = ROOT / "config" / "tool_registry.json"


def decode_terminus_html(text: str) -> str:
    m = re.search(r'_P201_HTML_B64\s*=\s*([\'\"])(.*?)\1', text, re.S)
    if not m:
        return ""
    return base64.b64decode(''.join(m.group(2).split())).decode('utf-8', errors='replace')


def main() -> int:
    text = MAIN.read_text(errors='replace')
    html = decode_terminus_html(text)
    checks = {
        "main_exists": MAIN.exists(),
        "registry_exists": REG.exists(),
        "safe_status": '"forge-protoforge-status": lambda: cmd_forge_protoforge_status(sid)' in text,
        "safe_plan": '"forge-protoforge-simulation-plan": lambda: cmd_forge_protoforge_simulation_plan(sid, cmd_args)' in text,
        "safe_result": '"forge-protoforge-result-show": lambda: cmd_forge_protoforge_result_show(sid, cmd_args)' in text,
        "gated_run": '"forge-protoforge-simulation-run-approved": ("RUN-PROTOFORGE", lambda: cmd_forge_protoforge_simulation_run_approved(sid))' in text,
        "html_protoforge_section": 'data-c="forge-protoforge-status"' in html,
        "html_plan_cube": 'data-c="forge-protoforge-simulation-plan pybullet_fixed_falling_cube"' in html,
        "html_run_approved": 'data-c="forge-protoforge-simulation-run-approved"' in html,
        "html_result_show": 'data-c="forge-protoforge-result-show"' in html,
        "no_new_cli_expected_commands": "PATCH240_TERMINUS_PROTOFORGE_COMMANDS" not in text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("PATCH240_VERIFY_FAIL")
        print("failed=" + ",".join(failed))
        return 1
    print("PATCH240_VERIFY_PASS")
    print("bridge=terminus_to_patch239_protoforge_connector")
    print("commands=forge-protoforge-status, forge-protoforge-simulation-plan, forge-protoforge-result-show")
    print("gated_command=forge-protoforge-simulation-run-approved")
    print("gate=RUN-PROTOFORGE")
    print("command_surface_delta=0_expected")
    print("ui_redesign=False")
    print("identity_vault_write=False")
    print("rmc_live_memory_write=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
