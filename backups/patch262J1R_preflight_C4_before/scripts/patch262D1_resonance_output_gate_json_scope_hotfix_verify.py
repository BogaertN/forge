#!/usr/bin/env python3
"""
Patch 262D1 verifier: RMC resonance output gate JSON scope hotfix.
Checks that the preview receipt ID helper no longer depends on do_GET-local _j.
"""
from pathlib import Path
import re

ROOT = Path.home() / "forge"
MAIN = ROOT / "main.py"
text = MAIN.read_text(encoding="utf-8")

required = [
    "def _p262d_rmc_receipt_preview_id(cymatic_preview: dict) -> str:",
    "import json as _p262d_json",
    "_p262d_json.dumps(basis, sort_keys=True, ensure_ascii=False)",
    "def _p262d_rmc_resonance_output_gate_v1(raw_path: str) -> dict:",
    'elif _p249_req_path == "/api/rmc/resonance-output-gate":',
    "_p262d_rmc_resonance_output_gate_v1(self.path)",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("PATCH262D1_VERIFY_FAIL missing=" + repr(missing))

match = re.search(
    r"def _p262d_rmc_receipt_preview_id\(cymatic_preview: dict\) -> str:\n(?P<body>.*?)(?=\n\ndef )",
    text,
    re.S,
)
if not match:
    raise SystemExit("PATCH262D1_VERIFY_FAIL helper_not_found")
body = match.group("body")
if "_j.dumps" in body:
    raise SystemExit("PATCH262D1_VERIFY_FAIL helper_still_uses_do_get_local__j")

print("PATCH262D1_RESONANCE_OUTPUT_GATE_JSON_SCOPE_HOTFIX_VERIFY_PASS")
print("endpoint=/api/rmc/resonance-output-gate")
print("fix=local_json_import_inside_receipt_preview_id")
print("reason=remove_NameError__j_not_defined")
print("adds_forge_commands=False")
print("executes_command=False")
print("executes_shell=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
