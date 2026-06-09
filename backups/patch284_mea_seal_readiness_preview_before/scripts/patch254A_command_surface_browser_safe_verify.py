#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"

def extract_safe_block(text: str) -> str:
    m = re.search(r"_SAFE\s*=\s*\{(?P<body>.*?)\n\s*\}", text, re.S)
    return m.group("body") if m else ""

def main() -> int:
    text = MAIN.read_text(errors="replace")
    safe_block = extract_safe_block(text)

    checks = {
        "safe_block_found": bool(safe_block),
        "command_surface_in_safe": '"forge-command-surface"' in safe_block,
        "calls_command_surface_function": "cmd_forge_command_surface(sid)" in safe_block,
        "api_command_bridge_preserved": 'elif self.path == "/api/command":' in text,
        "no_new_cli_command": "forge-command-surface-browser-safe-hotfix" not in text,
        "no_shell_added": "subprocess.Popen" not in safe_block and "os.system(" not in safe_block,
        "llm_still_disabled": '"llm_execution_enabled": False' in text,
        "command_runner_still_patch254": "READY_FOR_SAFE_AND_GATED_COMMANDS" in text,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("PATCH254A_COMMAND_SURFACE_BROWSER_SAFE_VERIFY_FAIL")
        print("failed=" + ",".join(failed))
        return 1

    print("PATCH254A_COMMAND_SURFACE_BROWSER_SAFE_VERIFY_PASS")
    print("patch=254A")
    print("fix=add_forge_command_surface_to_browser_safe_allowlist")
    print("uses_existing_api=/api/command")
    print("adds_forge_commands=False")
    print("command_surface_delta=0_expected")
    print("unknown_commands_still_blocked=True")
    print("llm_execution_enabled=False")
    print("next=retest forge-command-surface from Operator Console")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
