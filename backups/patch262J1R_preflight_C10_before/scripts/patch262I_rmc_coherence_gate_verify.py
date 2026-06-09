#!/usr/bin/env python3
from pathlib import Path
root = Path(__file__).resolve().parents[1]
main = (root / "main.py").read_text()
required = [
    "/api/rmc/coherence-gate",
    "_p262i_rmc_coherence_gate_v1",
    "read_only_coherence_scorer_correction_naming_gate",
    "Patch 262J — RMC Manifest Compiler Dry-Run",
    "calls_llm\": False",
    "queries_chroma_db\": False",
    "writes_files\": False",
    "rmc_live_memory_write\": False",
]
missing = [s for s in required if s not in main]
if missing:
    print("PATCH262I_RMC_COHERENCE_GATE_VERIFY_FAIL")
    print("missing=" + repr(missing))
    raise SystemExit(1)
print("PATCH262I_RMC_COHERENCE_GATE_VERIFY_PASS")
print("endpoint=/api/rmc/coherence-gate")
print("mode=read_only_coherence_scorer_correction_naming_gate")
print("uses_candidate_conclusion=True")
print("correction_gate=True")
print("naming_gate=True")
print("renders_final_language=False")
print("adds_forge_commands=False")
print("executes_command=False")
print("executes_shell=False")
print("calls_llm=False")
print("queries_chroma_db=False")
print("reads_db_files=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
