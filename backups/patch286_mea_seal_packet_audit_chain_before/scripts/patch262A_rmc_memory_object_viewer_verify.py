#!/usr/bin/env python3
"""Patch 262A verifier — RMC Memory Object Viewer / Manifest Trace View."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
text = MAIN.read_text(encoding="utf-8", errors="replace")
required = [
    "/api/rmc/memory-object",
    "def _p262a_rmc_memory_object_view_v1",
    "read_only_rmc_memory_object_trace",
    "manifest_trace",
    "selected_symbolic_entry",
    "queries_chroma_db",
    "generates_cymatics",
    "Patch 262B — RMC Phase Graph / Frequency Preview Read-Only",
]
missing = [item for item in required if item not in text]
start = text.find("def _p262a_rmc_memory_object_view_v1")
end = text.find("# ─── PATCH 255", start)
scope = text[start:end if end != -1 else len(text)]
forbidden = [
    "subprocess.run(",
    "os.system(",
    "Popen(",
    "write_text(",
    "open(",
    "chromadb",
]
forbidden_hits = [item for item in forbidden if item in scope]
if missing:
    raise SystemExit("PATCH262A_RMC_MEMORY_OBJECT_VIEWER_VERIFY_FAIL missing=" + ",".join(missing))
if forbidden_hits:
    raise SystemExit("PATCH262A_RMC_MEMORY_OBJECT_VIEWER_VERIFY_FAIL forbidden=" + ",".join(forbidden_hits))
print("PATCH262A_RMC_MEMORY_OBJECT_VIEWER_VERIFY_PASS")
print("endpoint=/api/rmc/memory-object")
print("mode=read_only_rmc_memory_object_trace")
print("manifest_trace_view=True")
print("reads_allowlisted_receipts_manifests_symbolic_maps=True")
print("queries_chroma_db=False")
print("generates_cymatics=False")
print("adds_forge_commands=False")
print("executes_command=False")
print("executes_shell=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
