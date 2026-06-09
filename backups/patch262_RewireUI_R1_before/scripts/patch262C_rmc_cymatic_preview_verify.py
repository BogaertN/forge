#!/usr/bin/env python3
"""Patch 262C verifier — RMC Cymatic Geometry / Browser Tone Preview.

Static verifier only. It checks that the endpoint and boundary markers exist in main.py.
It does not start Forge, execute shell from Forge, write memory, or touch Identity Vault.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
main = ROOT / "main.py"
text = main.read_text(encoding="utf-8", errors="replace")
checks = {
    "endpoint=/api/rmc/cymatic-preview": '"/api/rmc/cymatic-preview"' in text,
    "mode=read_only_cymatic_geometry_browser_tone_preview": "read_only_cymatic_geometry_browser_tone_preview" in text,
    "uses_phase_preview=True": "uses_verified_phase_preview" in text,
    "renders_svg_in_browser=True": "renders_svg_in_browser" in text,
    "browser_audio_preview_only=True": "browser_audio_preview_only" in text,
    "adds_forge_commands=False": "cmd_forge_rmc_cymatic_preview" not in text,
    "executes_command=False": '"executes_command": False' in text,
    "executes_shell=False": '"executes_shell": False' in text,
    "writes_files=False": '"writes_files": False' in text,
    "identity_vault_write=False": '"identity_vault_write": False' in text,
    "rmc_live_memory_write=False": '"rmc_live_memory_write": False' in text,
    "generates_audio_file=False": '"generates_audio_file": False' in text,
    "generates_image_file=False": '"generates_image_file": False' in text,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    print("PATCH262C_RMC_CYMATIC_PREVIEW_VERIFY_FAIL")
    for item in failed:
        print(f"missing={item}")
    sys.exit(1)
print("PATCH262C_RMC_CYMATIC_PREVIEW_VERIFY_PASS")
for item in checks:
    print(item)
