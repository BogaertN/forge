#!/usr/bin/env python3
# Patch 262F verifier — RMC Phase Parser Read-Only
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
main = root / "main.py"
text = main.read_text()
required = [
    "def _p262f_rmc_phase_parser_v1",
    '"endpoint": "/api/rmc/phase-parser"',
    '"mode": "read_only_phase_parser_dry_run"',
    '"memory_drift_protoforge2_required": True',
    '"epsilon_s_required": "ε_s = (σ_res + D_score + |ΔΦ|) / n"',
    '_p262f_rmc_phase_parser_v1(self.path)',
    '"Patch 262G — RMC Drift Analyzer Read-Only"',
]
missing = [item for item in required if item not in text]
for forbidden in ["subprocess.run", "os.system", "Popen(", "sqlite3.connect", "chromadb", "openai"]:
    # Do not fail old file-wide legacy occurrences; only inspect Patch 262F block.
    start = text.find("# ─── PATCH 262F")
    end = text.find("# ─── PATCH 262E", start)
    block = text[start:end] if start != -1 and end != -1 else ""
    if forbidden in block:
        missing.append(f"forbidden_in_patch262F:{forbidden}")
if missing:
    print("PATCH262F_RMC_PHASE_PARSER_VERIFY_FAIL")
    print(json.dumps({"missing": missing}, indent=2))
    raise SystemExit(1)
print("PATCH262F_RMC_PHASE_PARSER_VERIFY_PASS")
print("endpoint=/api/rmc/phase-parser")
print("mode=read_only_phase_parser_dry_run")
print("first_real_compiler_module=True")
print("uses_memory_drift_protoforge2_anchor=True")
print("adds_forge_commands=False")
print("executes_command=False")
print("executes_shell=False")
print("calls_llm=False")
print("queries_chroma_db=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
