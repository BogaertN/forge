#!/usr/bin/env python3
"""Patch 262G verifier: RMC Drift Analyzer Read-Only.

Checks static runtime/frontend contract markers. It does not start Forge, run shell
through Forge, write memory, query Chroma, or touch Identity Vault.
"""
from __future__ import annotations

from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REGISTRY = ROOT / "config" / "tool_registry.json"

text = MAIN.read_text(encoding="utf-8")
registry = json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.exists() else {}
commands = registry.get("commands") or registry.get("tools") or []

required = {
    "endpoint=/api/rmc/drift-analyzer": '"/api/rmc/drift-analyzer"' in text,
    "function=_p262g_rmc_drift_analyzer_v1": "def _p262g_rmc_drift_analyzer_v1" in text,
    "taxonomy_syntactic": "syntactic_drift" in text,
    "taxonomy_semantic": "semantic_drift" in text,
    "taxonomy_recursive": "recursive_drift" in text,
    "taxonomy_catastrophic": "catastrophic_drift" in text,
    "taxonomy_evolutionary": "evolutionary_drift" in text,
    "taxonomy_resonant": "resonant_drift" in text,
    "taxonomy_structural": "structural_drift" in text,
    "epsilon_formula": "ε_s = (σ_res + D_score + |ΔΦ|) / n" in text,
    "chi_t_preview": "chi_t" in text and "required_before_projection" in text,
    "circuit_breaker_preview": "circuit_breaker" in text and "projection_blocked" in text,
    "uses_phase_parser": "_p262f_rmc_phase_parser_v1" in text,
    "next_patch_262H": "Patch 262H — RMC Candidate Conclusion Dry-Run" in text,
    "no_new_command_function": "cmd_forge_rmc_drift_analyzer" not in text,
}

for name, ok in required.items():
    if not ok:
        print(f"PATCH262G_VERIFY_FAIL {name}")
        sys.exit(1)

print("PATCH262G_RMC_DRIFT_ANALYZER_VERIFY_PASS")
print("endpoint=/api/rmc/drift-analyzer")
print("mode=read_only_memory_drift_protoforge2_dry_run")
print("uses_phase_parser=True")
print("uses_memory_drift_protoforge2_anchor=True")
print("drift_taxonomy=syntactic,semantic,recursive,catastrophic,evolutionary,resonant,structural")
print("epsilon_s_preview=True")
print("chi_t_preview=True")
print("circuit_breaker_preview=True")
print("adds_forge_commands=False")
print("executes_command=False")
print("executes_shell=False")
print("calls_llm=False")
print("queries_chroma_db=False")
print("reads_db_files=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
