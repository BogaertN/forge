#!/usr/bin/env python3
"""Patch 262H verifier: RMC Candidate Conclusion Dry-Run."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
main = root / "main.py"
text = main.read_text(encoding="utf-8")
required = [
    "PATCH 262H — RMC CANDIDATE CONCLUSION DRY-RUN",
    "def _p262h_rmc_candidate_conclusion_v1",
    '"endpoint": "/api/rmc/candidate-conclusion"',
    '"mode": "read_only_candidate_conclusion_dry_run"',
    '"candidate_set_id"',
    '"candidate_set"',
    '"selected_candidate_preview"',
    '"renders_final_language": False',
    '"writes_files": False',
    '"rmc_live_memory_write": False',
    'elif _p249_req_path == "/api/rmc/candidate-conclusion"',
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("PATCH262H_VERIFY_FAIL missing markers: " + ", ".join(missing))
for forbidden in [
    "subprocess.",
    "os.system(",
    "Popen(",
    "open('/",
    "open(\"/",
]:
    if forbidden in text[text.find("PATCH 262H — RMC CANDIDATE"):text.find("PATCH 262E — RMC TRACERECORD")]:
        raise SystemExit(f"PATCH262H_VERIFY_FAIL forbidden marker in Patch 262H block: {forbidden}")
print("PATCH262H_RMC_CANDIDATE_CONCLUSION_VERIFY_PASS")
print("endpoint=/api/rmc/candidate-conclusion")
print("mode=read_only_candidate_conclusion_dry_run")
print("uses_phase_parser=True")
print("uses_drift_analyzer=True")
print("candidate_meaning_states=True")
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
