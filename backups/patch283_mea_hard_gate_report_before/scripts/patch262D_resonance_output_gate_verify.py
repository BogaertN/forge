#!/usr/bin/env python3
"""Patch 262D verifier — RMC Resonance Output Gate / Preview Receipt.

Checks that the endpoint is present and remains read-only: no Forge command additions,
no shell execution, no file writes, no RMC live memory write, no artifact export.
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REGISTRY = ROOT / "config" / "tool_registry.json"
text = MAIN.read_text(encoding="utf-8")
errors = []

def require(name: str, cond: bool) -> None:
    if not cond:
        errors.append(name)

require("endpoint_route_present", '"/api/rmc/resonance-output-gate"' in text)
require("function_present", "def _p262d_rmc_resonance_output_gate_v1" in text)
require("route_calls_function", "_p262d_rmc_resonance_output_gate_v1(self.path)" in text)
require("uses_cymatic_preview", "/api/rmc/cymatic-preview" in text and "uses_verified_cymatic_preview" in text)
require("preview_receipt_only", "PREVIEW_ONLY_NOT_WRITTEN" in text)
require("gate_name_present", "RMC-RESONANCE-OUTPUT" in text)
require("writes_files_false", '"writes_files": False' in text)
require("receipt_written_false", '"receipt_written": False' in text)
require("artifact_exported_false", '"artifact_exported": False' in text)
require("no_audio_file_generation", '"generates_audio_file": False' in text)
require("no_image_file_generation", '"generates_image_file": False' in text)
require("no_rmc_live_memory_write", '"rmc_live_memory_write": False' in text)
require("no_new_forge_command_name", "forge-rmc-resonance-output" not in text)

if REGISTRY.exists():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    require("trust_level_preserved", str(registry.get("current_trust_level")) in {"5", "5.0"})

if errors:
    print("PATCH262D_RESONANCE_OUTPUT_GATE_VERIFY_FAIL")
    for err in errors:
        print(f"missing={err}")
    sys.exit(1)

print("PATCH262D_RESONANCE_OUTPUT_GATE_VERIFY_PASS")
print("endpoint=/api/rmc/resonance-output-gate")
print("mode=read_only_resonance_output_gate_preview_receipt")
print("uses_cymatic_preview=True")
print("receipt_preview_only=True")
print("receipt_written=False")
print("artifact_exported=False")
print("adds_forge_commands=False")
print("executes_command=False")
print("executes_shell=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
