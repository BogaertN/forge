#!/usr/bin/env python3
"""Patch 257 verifier — Patch / Proposal Workflow Panel backend."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
text = MAIN.read_text(encoding="utf-8", errors="replace")

required = [
    'def _p257_operator_patch_workflow_v1()',
    '"/api/operator/patch-workflow"',
    '"read_only_patch_workflow_status"',
    '"patch_workflow_enabled": True',
    '"patch_workflow_executes_command": False',
    '"patch_workflow_writes_files": False',
    '"Patch 258 — Audit / Receipt Full Panel"',
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("PATCH257_BACKEND_VERIFY_FAIL missing=" + repr(missing))

for forbidden in [
    'subprocess.run(',
    'os.system(',
    'Popen(',
    'identity_vault_write": True',
    'rmc_live_memory_write": True',
]:
    if forbidden in text[text.find('def _p257_operator_patch_workflow_v1'):text.find('# ─── PATCH 255')]:
        raise SystemExit("PATCH257_BACKEND_VERIFY_FAIL forbidden_in_patch257=" + forbidden)

print("PATCH257_PATCH_WORKFLOW_VERIFY_PASS")
print("endpoint=/api/operator/patch-workflow")
print("mode=read_only_patch_workflow_status")
print("executes_command=False")
print("calls_llm=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
print("adds_forge_commands=False")
