#!/usr/bin/env python3
"""Static verifier for Patch 235B — Athena Activation Verification."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REG = ROOT / "config" / "tool_registry.json"
text = MAIN.read_text(encoding="utf-8")
errors = []
required = [
    "PATCH235B_ATHENA_ACTIVATION_VERIFY_COMMANDS",
    "forge-agent-verify-athena-activation",
    "forge-agent-verify-athena-activation-report",
    "def cmd_forge_agent_verify_athena_activation(session_id: str) -> None:",
    "def cmd_forge_agent_verify_athena_activation_report(session_id: str) -> None:",
    "ATHENA_ACTIVATION_VERIFIED_ACTIVE_GOVERNED",
    "BLOCKED_ATHENA_ACTIVATION_VERIFICATION",
    "PATCH235A_REQUIRED",
    "athena_can_execute_tools_by_itself",
    "athena_can_read_secrets",
    "Verification patch writes no Identity Vault DB",
    "Verification patch writes no RMC memory",
    "Verification patch grants no secret reads",
    "neo.local",
    "gilligan.local",
    "aiweb_patch235b_athena_activation_verify_v1",
]
# PATCH235A_REQUIRED marker is represented by P235B_REQUIRED_235A_VERDICT.
required = [r if r != "PATCH235A_REQUIRED" else "P235B_REQUIRED_235A_VERDICT" for r in required]
for needle in required:
    if needle not in text:
        errors.append(f"missing main marker: {needle}")
idx_defs = text.find("# --- BEGIN PATCH 235B ATHENA ACTIVATION VERIFICATION ---")
idx_main = text.find('if __name__ == "__main__":\n    main()')
if not (0 <= idx_defs < idx_main):
    errors.append("Patch 235B definitions appear after runtime main() call")
idx_report_route = text.find('user_input.lower() == "forge-agent-verify-athena-activation-report"')
idx_action_route = text.find('user_input.lower() == "forge-agent-verify-athena-activation"')
if not (0 <= idx_action_route < idx_report_route):
    errors.append("Patch 235B action route should be before report route")
for bad in [
    '"identity_vault_database_written": True,',
    '"rmc_memory_written": True,',
    '"agent_identity_activation_performed": True,',
    '"autonomous_tool_execution_granted": True,',
    '"secret_reads_granted": True,',
    '"forge_bypass_granted": True,',
    '"patch_autonomy_granted": True,',
]:
    # These exact truth assignments must not appear inside the Patch 235B block.
    block = text[idx_defs:idx_main] if idx_defs >= 0 and idx_main >= 0 else text
    if bad in block:
        errors.append(f"forbidden Patch 235B marker: {bad}")
try:
    data = json.loads(REG.read_text(encoding="utf-8"))
    tools = data.get("tools", {})
    for cmd in ["forge-agent-verify-athena-activation", "forge-agent-verify-athena-activation-report"]:
        if cmd not in tools:
            errors.append(f"tool registry missing {cmd}")
    if data.get("current_trust_level") != 5.0:
        errors.append(f"unexpected trust level: {data.get('current_trust_level')!r}")
except Exception as exc:
    errors.append(f"registry parse failed: {type(exc).__name__}: {exc}")
if errors:
    print("PATCH235B_VERIFY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)
print("PATCH235B_VERIFY_PASS")
print("commands=forge-agent-verify-athena-activation, forge-agent-verify-athena-activation-report")
print("boundary=read-only verification; no Identity Vault DB write; no RMC memory write; no activation; no autonomous execution; no secret reads")
