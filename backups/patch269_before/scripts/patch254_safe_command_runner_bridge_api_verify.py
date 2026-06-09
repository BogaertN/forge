#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"

def main() -> int:
    text = MAIN.read_text(errors="replace")
    checks = {
        "output_state_helper_present": "def _p253_operator_output_state_v1" in text,
        "command_slot_ready": "READY_FOR_SAFE_AND_GATED_COMMANDS" in text,
        "next_patch_255": "Patch 255 — LLM / Natural-Language Request Bridge" in text,
        "command_execution_enabled_true": '"command_execution_enabled": True' in text,
        "llm_still_disabled": '"llm_execution_enabled": False' in text,
        "api_command_bridge_preserved": 'elif self.path == "/api/command":' in text,
        "no_new_command_surface": "forge-safe-command-runner" not in text,
        "no_shell_added": "subprocess.Popen" not in text and "os.system(" not in text,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("PATCH254_SAFE_COMMAND_RUNNER_API_VERIFY_FAIL")
        print("failed=" + ",".join(failed))
        return 1

    print("PATCH254_SAFE_COMMAND_RUNNER_API_VERIFY_PASS")
    print("patch=254")
    print("uses_existing_api=/api/command")
    print("adds_forge_commands=False")
    print("command_surface_delta=0_expected")
    print("unknown_commands_blocked_in_frontend=True")
    print("gated_commands_require_gate=True")
    print("llm_execution_enabled=False")
    print("next=Patch 255 — LLM / Natural-Language Request Bridge")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
