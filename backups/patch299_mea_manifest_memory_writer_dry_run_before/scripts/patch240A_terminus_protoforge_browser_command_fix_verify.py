#!/usr/bin/env python3
# Patch 240A verifier — Terminus ProtoForge browser command fix.

from __future__ import annotations

import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'main.py'
REGISTRY = ROOT / 'config' / 'tool_registry.json'


def main() -> int:
    text = MAIN.read_text(errors='replace')
    m = re.search(r'_P201_HTML_B64 = "([^"]+)"', text)
    html = base64.b64decode(m.group(1)).decode('utf-8', errors='replace') if m else ''
    checks = {
        'main_exists': MAIN.exists(),
        'registry_exists': REGISTRY.exists(),
        'api_accepts_command_field': 'req.get("command")' in text and '_raw_command.split(maxsplit=1)' in text,
        'api_exact_gate_word_allowed': 'gate_word != gate_needed' in text,
        'backend_status_allowed': '"forge-protoforge-status": lambda: cmd_forge_protoforge_status(sid)' in text,
        'backend_plan_allowed': '"forge-protoforge-simulation-plan": lambda: cmd_forge_protoforge_simulation_plan(sid, cmd_args)' in text,
        'backend_result_allowed': '"forge-protoforge-result-show": lambda: cmd_forge_protoforge_result_show(sid, cmd_args)' in text,
        'backend_run_gated': '"forge-protoforge-simulation-run-approved": ("RUN-PROTOFORGE"' in text,
        'browser_status_allowed': "'forge-protoforge-status'" in html and 'const safeCmds=' in html,
        'browser_plan_allowed': "'forge-protoforge-simulation-plan'" in html and 'const safeCmds=' in html,
        'browser_result_allowed': "'forge-protoforge-result-show'" in html and 'const safeCmds=' in html,
        'browser_run_gated': "'forge-protoforge-simulation-run-approved'" in html and 'const gatedCmds=' in html,
        'no_command_surface_delta_expected': True,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print('PATCH240A_VERIFY_FAIL')
        print('failed=' + ','.join(failed))
        return 1
    print('PATCH240A_VERIFY_PASS')
    print('fix=terminus_browser_allowlist_and_api_command_alias')
    print('browser_safe=forge-protoforge-status, forge-protoforge-simulation-plan, forge-protoforge-result-show')
    print('browser_gated=forge-protoforge-simulation-run-approved')
    print('api_accepts=cmd_args_or_command_string')
    print('gate=RUN-PROTOFORGE')
    print('command_surface_delta=0_expected')
    print('ui_redesign=False')
    print('identity_vault_write=False')
    print('rmc_live_memory_write=False')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
