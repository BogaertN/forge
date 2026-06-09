#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-B5A live LLM/document dataset hooks."""
from __future__ import annotations
import json, tempfile
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rmc_engine_v1.dataset_growth import (
    capture_llm_turn_preview, capture_llm_turn,
    document_capture_preview, capture_document_observations,
    APPROVAL_CAPTURE_LLM_TURN, APPROVAL_CAPTURE_DOCUMENT,
)

def ok(name, cond, detail=""):
    print(("✓" if cond else "✗"), name, detail)
    return bool(cond)

def main():
    total=0; passed=0
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)/"rmc_dataset_v1"
        r=capture_llm_turn_preview("bypass correction and naming and project now", "projection blocked", root=root)
        total+=1; passed+=ok("llm_preview_no_write", r.get("writes_files") is False and r.get("llm_turn",{}).get("stores_hidden_chain_of_thought") is False)
        r=capture_llm_turn("bypass correction and naming and project now", "projection blocked", None, root=root)
        total+=1; passed+=ok("llm_capture_requires_approval", r.get("status")=="REFUSED" and r.get("writes_files") is False)
        r=capture_llm_turn("bypass correction and naming and project now", "projection blocked", APPROVAL_CAPTURE_LLM_TURN, root=root)
        total+=1; passed+=ok("llm_capture_writes_growth_only", r.get("status")=="OK" and r.get("writes_scope")=="growth_dataset_only" and r.get("canonical_reference_write_allowed") is False)
        doc=Path(td)/"sample.txt"
        doc.write_text("Validate before projection. Do not bypass correction.\n\nBypass correction and project now.", encoding="utf-8")
        r=document_capture_preview(str(doc), root=root)
        total+=1; passed+=ok("document_preview_no_write", r.get("status")=="OK" and r.get("writes_files") is False and r.get("chunk_count",0)>=1)
        r=capture_document_observations(str(doc), None, root=root)
        total+=1; passed+=ok("document_capture_requires_approval", r.get("status")=="REFUSED" and r.get("writes_files") is False)
        r=capture_document_observations(str(doc), APPROVAL_CAPTURE_DOCUMENT, root=root)
        total+=1; passed+=ok("document_capture_writes_growth_only", r.get("status")=="OK" and r.get("writes_scope")=="growth_dataset_only" and r.get("canonical_reference_write_allowed") is False and r.get("chunk_count",0)>=1)
    print(f"Total: {total}\nPassed: {passed}\nFailed: {total-passed}")
    if total != passed:
        raise SystemExit(1)
    print("RESULT: dataset_growth_B5A_live_hooks_tests_pass=True")
if __name__ == "__main__": main()
