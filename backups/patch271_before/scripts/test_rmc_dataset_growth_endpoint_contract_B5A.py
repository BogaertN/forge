#!/usr/bin/env python3
"""Static endpoint contract tests for Patch 262J1R-Preflight-B5A."""
from __future__ import annotations
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
main=(ROOT/"main.py").read_text(encoding="utf-8")
checks={
"llm_turn_preview_endpoint":"/api/rmc/dataset-growth/llm-turn-preview" in main,
"llm_turn_capture_endpoint":"/api/rmc/dataset-growth/llm-turn-capture" in main,
"document_preview_endpoint":"/api/rmc/dataset-growth/document-preview" in main,
"document_capture_endpoint":"/api/rmc/dataset-growth/document-capture" in main,
"operator_llm_has_capture_hook":"dataset_growth_capture" in main and "capture_llm_turn" in main,
"operator_llm_requires_approval":"CAPTURE_RMC_LLM_TURN" in main,
"canonical_never_mutated":"canonical_reference_write_allowed" in main,
}
failed=[]
for k,v in checks.items():
 print(("✓" if v else "✗"), k)
 if not v: failed.append(k)
print(f"Total: {len(checks)}\nPassed: {len(checks)-len(failed)}\nFailed: {len(failed)}")
if failed: raise SystemExit(1)
print("RESULT: dataset_growth_B5A_endpoint_contract_tests_pass=True")
