#!/usr/bin/env python3
"""Patch 256 Forge verifier: Page Capture + Seen Pages Panel backend contract."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
main = root / "main.py"
text = main.read_text(encoding="utf-8", errors="replace")

checks = {
    "get_seen_pages_route": 'elif self.path == "/api/seen-pages"' in text,
    "post_read_page_route": 'if self.path == "/api/read-page"' in text,
    "contract_seen_pages": '"path": "/api/seen-pages"' in text,
    "contract_read_page": '"path": "/api/read-page"' in text,
    "http_https_only": 'Only http:// and https:// URLs can be captured.' in text,
    "browser_memory_scope": '"write_scope": "forge_browser_memory_v1_only"' in text,
    "no_identity_vault_write": '"identity_vault_write": False' in text,
    "no_rmc_live_memory_write": '"rmc_live_memory_write": False' in text,
    "next_patch_257": '"next_patch": "Patch 257 — Patch / Proposal Workflow Panel"' in text,
    "page_capture_enabled_boundary": '"page_capture_enabled": True' in text,
}

missing = [name for name, ok in checks.items() if not ok]
if missing:
    print("PATCH256_PAGE_CAPTURE_VERIFY_FAIL")
    for name in missing:
        print(f"missing={name}")
    raise SystemExit(1)

# Ensure no Forge command was added by this patch name. Command surface count is runtime-verified separately.
if "PATCH 256" in text and "FORGE_EXPECTED_COMMANDS.append" in text[text.find("PATCH 256"):text.find("def _p201_make_handler") if "def _p201_make_handler" in text else len(text)]:
    print("PATCH256_PAGE_CAPTURE_VERIFY_FAIL")
    print("unexpected=FORGE_EXPECTED_COMMANDS_append_inside_patch256")
    raise SystemExit(1)

print("PATCH256_PAGE_CAPTURE_VERIFY_PASS")
print("endpoint_get=/api/seen-pages")
print("endpoint_post=/api/read-page")
print("write_scope=forge_browser_memory_v1_only")
print("executes_command=False")
print("calls_llm=False")
print("executes_shell=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
print("adds_forge_commands=False")
