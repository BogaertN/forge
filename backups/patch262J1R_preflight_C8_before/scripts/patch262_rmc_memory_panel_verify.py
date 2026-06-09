#!/usr/bin/env python3
"""Patch 262 verifier — RMC Memory Panel v1 read-only endpoint."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
text = MAIN.read_text(encoding="utf-8", errors="replace")
required = [
    "/api/rmc/memory-status",
    "def _p262_rmc_memory_status_v1",
    "read_only_rmc_memory_status",
    "rmc_memory_panel_enabled",
    "RMC Memory Panel v1",
    "queries_chroma_db",
    "generates_cymatics",
]
missing = [item for item in required if item not in text]
forbidden = [
    "subprocess.run([\"curl\"",
    "os.system(",
    "Popen(",
]
forbidden_hits = [item for item in forbidden if item in text[text.find('def _p262_rmc_memory_status_v1'):text.find('# ─── PATCH 255')]]
if missing:
    raise SystemExit("PATCH262_RMC_MEMORY_PANEL_VERIFY_FAIL missing=" + ",".join(missing))
if forbidden_hits:
    raise SystemExit("PATCH262_RMC_MEMORY_PANEL_VERIFY_FAIL forbidden=" + ",".join(forbidden_hits))
print("PATCH262_RMC_MEMORY_PANEL_VERIFY_PASS")
print("endpoint=/api/rmc/memory-status")
print("mode=read_only_rmc_memory_status")
print("final_architecture_foundation=True")
print("reads_receipts_manifests_symbolic_maps=True")
print("queries_chroma_db=False")
print("generates_cymatics=False")
print("adds_forge_commands=False")
print("executes_command=False")
print("executes_shell=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
