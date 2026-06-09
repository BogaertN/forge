#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-B5A."""
from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def add(name, cond, detail=""):
 checks.append((name,bool(cond),detail))
 print(f"[{'PASS' if cond else 'FAIL'}] {name}"+(f" :: {detail}" if detail else ""))

def run(script):
 p=subprocess.run([sys.executable, str(ROOT/"scripts"/script)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
 return p.returncode==0, p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""
print("PATCH 262J1R-PREFLIGHT-B5A VERIFY")
print("─"*72)
for rel in [
 "rmc_engine_v1/dataset_growth.py",
 "scripts/test_rmc_dataset_growth_live_hooks.py",
 "scripts/test_rmc_dataset_growth_endpoint_contract_B5A.py",
]: add("file_exists_"+rel.replace('/','_'), (ROOT/rel).exists(), rel)
text=(ROOT/"rmc_engine_v1"/"dataset_growth.py").read_text(encoding="utf-8")
add("dataset_growth_has_llm_turn_capture", "capture_llm_turn" in text and "CAPTURE_RMC_LLM_TURN" in text)
add("dataset_growth_has_document_capture", "capture_document_observations" in text and "CAPTURE_RMC_DOCUMENT_OBSERVATIONS" in text)
add("dataset_growth_canonical_write_protected", "canonical_reference_write_allowed" in text)
main=(ROOT/"main.py").read_text(encoding="utf-8")
add("main_has_llm_turn_endpoints", "/api/rmc/dataset-growth/llm-turn-preview" in main and "/api/rmc/dataset-growth/llm-turn-capture" in main)
add("main_has_document_endpoints", "/api/rmc/dataset-growth/document-preview" in main and "/api/rmc/dataset-growth/document-capture" in main)
add("operator_llm_request_has_capture_hook", "dataset_growth_capture" in main and "capture_llm_turn" in main)
for script in [
 "test_rmc_dataset_growth_live_hooks.py",
 "test_rmc_dataset_growth_endpoint_contract_B5A.py",
 "test_rmc_dataset_growth_behavior.py",
 "test_rmc_dataset_growth_endpoint_contract.py",
 "test_rmc_lexicon_production_coverage.py",
 "test_rmc_resonance_codex_integration.py",
 "test_rmc_drift_engine_behavior.py",
 "test_rmc_phase_parser_behavior.py",
 "test_rmc_coherence_math_behavior.py",
]:
 ok,last=run(script); add(script+"_passes", ok, last)
print("─"*72)
passed=sum(1 for _,ok,_ in checks if ok)
print(f"Total: {len(checks)}")
print(f"Passed: {passed}")
print(f"Failed: {len(checks)-passed}")
if passed!=len(checks): raise SystemExit(1)
print("RESULT: PATCH_262J1R_PREFLIGHT_B5A_VERIFY_OK")
