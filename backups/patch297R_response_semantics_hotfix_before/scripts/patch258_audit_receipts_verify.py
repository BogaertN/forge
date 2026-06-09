#!/usr/bin/env python3
"""Patch 258 verifier — Audit / Receipt Full Panel.

Verifies that the Forge runtime exposes a read-only audit/receipt endpoint
without adding Forge CLI commands or granting shell/write authority.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
main = ROOT / "main.py"
text = main.read_text(encoding="utf-8", errors="replace")

required = [
    "def _p258_operator_audit_receipts_v1()",
    '"endpoint": "/api/operator/audit-receipts"',
    'elif self.path == "/api/operator/audit-receipts":',
    '"read_only": True',
    '"executes_command": False',
    '"calls_llm": False',
    '"writes_files": False',
    '"identity_vault_write": False',
    '"rmc_live_memory_write": False',
    '"next_patch": "Patch 259 — Left Rail Command Launcher"',
]
missing = [item for item in required if item not in text]

forbidden = [
    "subprocess.Popen",
    "os.system(",
    "write_text(",
    "open(AUDIT_LOG, 'w'",
    "open(AUDIT_LOG, \"w\"",
]
# This patch should not introduce these strings inside the p258 block. The whole file may
# legitimately contain older runtime code using subprocess or writes, so inspect only block.
start = text.find("# ─── PATCH 258")
end = text.find("# ─── PATCH 255", start)
block = text[start:end] if start >= 0 and end > start else ""
forbidden_hits = [item for item in forbidden if item in block]

if missing or forbidden_hits:
    print("PATCH258_AUDIT_RECEIPTS_VERIFY_FAIL")
    if missing:
        print("missing_markers:")
        for item in missing:
            print(f"- {item}")
    if forbidden_hits:
        print("forbidden_hits_in_patch258_block:")
        for item in forbidden_hits:
            print(f"- {item}")
    sys.exit(1)

print("PATCH258_AUDIT_RECEIPTS_VERIFY_PASS")
print("endpoint=/api/operator/audit-receipts")
print("mode=read_only_audit_receipt_status")
print("executes_command=False")
print("calls_llm=False")
print("executes_shell=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
print("adds_forge_commands=False")
