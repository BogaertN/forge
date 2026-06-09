#!/usr/bin/env python3
"""B5R regression tests for dataset-growth route refusal and URL parser scoping."""
from __future__ import annotations
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
main_text = (ROOT / "main.py").read_text(encoding="utf-8")
checks: list[tuple[str, bool, str]] = []

def add(name: str, cond: bool, detail: str = "") -> None:
    checks.append((name, bool(cond), detail))
    print(("✓" if cond else "✗"), name, detail)

def block(name: str) -> str:
    m = re.search(rf"def {name}.*?(?=\ndef _|\n# ───|\Z)", main_text, flags=re.S)
    return m.group(0) if m else ""

capture_block = block("_p262b5_rmc_dataset_growth_capture_v1")
query_block = block("_p262b5a_query_value")
add("capture_adapter_exists", bool(capture_block))
add("capture_adapter_imports_urlparse_locally", "import urllib.parse as _pp_url" in capture_block)
add("query_helper_imports_urlparse_locally", "import urllib.parse as _pp_url" in query_block)
add("dataset_growth_capture_route_present", '"/api/rmc/dataset-growth/capture"' in main_text or "'/api/rmc/dataset-growth/capture'" in main_text)
add("llm_turn_capture_route_present", "/api/rmc/dataset-growth/llm-turn-capture" in main_text)
add("document_capture_route_present", "/api/rmc/dataset-growth/document-capture" in main_text)

from rmc_engine_v1.dataset_growth import (  # noqa: E402
    capture_observation,
    capture_llm_turn,
    capture_document_observations,
)

tmp_root = Path(tempfile.mkdtemp(prefix="rmc_dataset_growth_b5r_"))
obs_refusal = capture_observation("bypass correction", None, root=tmp_root)
add("capture_observation_no_approval_refuses", obs_refusal.get("status") == "REFUSED", str(obs_refusal)[:160])
add("capture_observation_no_approval_no_write", obs_refusal.get("writes_files") is False)
add("capture_observation_refusal_failure_code", obs_refusal.get("failure_code") == "RMC_DATASET_CAPTURE_REQUIRES_EXPLICIT_APPROVAL")

llm_refusal = capture_llm_turn("request", "response", None, root=tmp_root)
add("llm_turn_no_approval_refuses", llm_refusal.get("status") == "REFUSED", str(llm_refusal)[:160])
add("llm_turn_refusal_no_write", llm_refusal.get("writes_files") is False)
add("llm_turn_refusal_failure_code", llm_refusal.get("failure_code") == "RMC_LLM_TURN_CAPTURE_REQUIRES_EXPLICIT_APPROVAL")

doc_refusal = capture_document_observations("/home/nic/Downloads/nonexistent.txt", None, root=tmp_root)
add("document_no_approval_refuses_before_path_read", doc_refusal.get("status") == "REFUSED", str(doc_refusal)[:160])
add("document_refusal_no_write", doc_refusal.get("writes_files") is False)
add("document_refusal_failure_code", doc_refusal.get("failure_code") == "RMC_DOCUMENT_CAPTURE_REQUIRES_EXPLICIT_APPROVAL")

passed = sum(1 for _, ok, _ in checks if ok)
print(f"Total: {len(checks)}")
print(f"Passed: {passed}")
print(f"Failed: {len(checks)-passed}")
if passed != len(checks):
    raise SystemExit(1)
print("RESULT: dataset_growth_B5R_route_refusals_tests_pass=True")
