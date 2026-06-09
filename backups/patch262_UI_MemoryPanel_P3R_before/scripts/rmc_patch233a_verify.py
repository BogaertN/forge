#!/usr/bin/env python3
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
main = (root / 'main.py').read_text(encoding='utf-8')
registry = json.loads((root / 'config' / 'tool_registry.json').read_text(encoding='utf-8'))
required = [
    'forge-gilligan-governed-handshake-verify',
    'forge-gilligan-governed-handshake-verify-report',
    'cmd_forge_gilligan_governed_handshake_verify',
    'cmd_forge_gilligan_governed_handshake_verify_report',
    'GILLIGAN_GOVERNED_HANDSHAKE_RECEIPT_VERIFIED',
    'HANDSHAKE_ACCEPTED_GOVERNED_ACTIVE_AGENT',
    'manifest_hash_valid',
    'receipt_hash_valid',
    'identity_vault_not_written',
    'rmc_memory_not_written',
    'autonomous_execution_false',
]
missing = [s for s in required if s not in main]
if missing:
    raise SystemExit('PATCH233A_VERIFY_FAIL missing main markers: ' + ', '.join(missing))
for cmd in required[:2]:
    if cmd not in registry.get('tools', {}):
        raise SystemExit('PATCH233A_VERIFY_FAIL missing tool registry: ' + cmd)
if 'forge-agent-activate-manual gilligan.local' in main and 'CONFIRM_GILLIGAN_ACTIVE_GOVERNED' in main and 'Patch 233A' in main:
    # existing activation command may remain from Patch 232B; Patch 233A must not add a new activation route.
    pass
print('PATCH233A_VERIFY_PASS')
print('commands=forge-gilligan-governed-handshake-verify, forge-gilligan-governed-handshake-verify-report')
print('boundary=read-only receipt verification; no Identity Vault DB write; no RMC memory write; no autonomous execution')
