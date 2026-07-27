#!/usr/bin/env python3
"""Static and live-adapter verification for the Symbolic Language Lab."""

from __future__ import annotations

import ast
from pathlib import Path
import sys

FORGE = Path(__file__).resolve().parents[1]
UI = Path("/home/nic/aiweb/apps/forge-operator-console")
if str(FORGE) not in sys.path:
    sys.path.insert(0, str(FORGE))

from rmc_engine_v1.symbolic_language_lab import (
    build_symbolic_language_preview_response,
)

checks: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append((name, bool(condition), detail))


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


required = {
    "schema": FORGE / "aiweb_language_core_bootstrap/rsoc_symbolic_reference_preview/schema.py",
    "recognition": FORGE / "aiweb_language_core_bootstrap/rsoc_symbolic_reference_preview/recognition.py",
    "validation": FORGE / "aiweb_language_core_bootstrap/rsoc_symbolic_reference_preview/validation.py",
    "adapter": FORGE / "rmc_engine_v1/symbolic_language_lab.py",
    "behavior_test": FORGE / "scripts/test_aiweb_rsoc_symbolic_reference_preview.py",
    "readme": FORGE / "scripts/README_aiweb_rsoc_symbolic_reference_preview.md",
    "tab": UI / "src/tabs/SymbolicLanguageLabTab.tsx",
    "client": UI / "src/lib/rmc-api-client.ts",
    "types": UI / "src/api/types.ts",
    "app": UI / "src/App.tsx",
    "tabs": UI / "src/shell/TopTabs.tsx",
    "theme": UI / "src/styles/theme.css",
    "dist": UI / "dist/index.html",
}
for label, path in required.items():
    check(f"required file {label}", path.is_file(), str(path))

for label in ("schema", "recognition", "validation", "adapter"):
    try:
        ast.parse(read(required[label]))
        check(f"Python AST compiles {label}", True)
    except Exception as error:
        check(f"Python AST compiles {label}", False, str(error))

main = read(FORGE / "main.py")
tab = read(required["tab"])
client = read(required["client"])
types = read(required["types"])
app = read(required["app"])
tabs = read(required["tabs"])
theme = read(required["theme"])

check("manifest POST route", '"route_key":"symbolic_language_preview","method":"POST"' in main)
check("manifest exact endpoint", '"path":"/api/rmc/symbolic-language-preview"' in main)
check("POST handler branch", 'if _p281_req_path == "/api/rmc/symbolic-language-preview":' in main)
check("bounded adapter invoked", "_symbolic_language_preview_api_v1(req)" in main)
check("existing GP-015 route retained", 'elif self.path == "/api/operator/ask-forge/math-trace":' in main)

check("tab ID type registered", "| 'symbolic_language_lab'" in types)
check("tab imported", "SymbolicLanguageLabTab" in app)
check("tab rendered", "symbolic_language_lab: <SymbolicLanguageLabTab />" in app)
check("tab visible", "Symbolic Language Lab" in tabs)
check("client route key", "| 'symbolic_language_preview'" in client)
check("client fallback path", "symbolic_language_preview: '/api/rmc/symbolic-language-preview'" in client)
check("client uses POST", "method: 'POST'" in client and "JSON.stringify({ source_text: sourceText })" in client)
check("tab uses canonical client", "inspectSymbolicLanguage" in tab)
check("tab has no raw fetch", "fetch(" not in tab)
check("tab does not trim source", ".trim(" not in tab)
check("tab does not normalize source", ".normalize(" not in tab)
check("tab requires explicit click", "Inspect exact source" in tab and "onClick={inspectSource}" in tab)
check("tab displays grammar boundary", "Current Grammar Boundary" in tab)
check("tab displays zero authority", "Zero-Authority Proof" in tab)
check("theme scoped", ".symbolic-language-lab" in theme and ".symbolic-source-input" in theme)

response = build_symbolic_language_preview_response(
    {"source_text": "⟁ ⧧ ⧒ ⧀ ⧙ ⧜ χ(t) R̂ Ĉ Ê"}
)
preview = response.get("reference_preview", {})
boundary = response.get("boundary", {})
check("sample response ready", response.get("status") == "OK")
check("sample recognizes ten", preview.get("recognized_operator_count") == 10)
check("sample exact reconstruction", response.get("projection", {}).get("exact_reconstruction_proven") is True)
check("sample no tokenization", response.get("source", {}).get("tokenization_performed") is False)
check("sample no normalization", response.get("source", {}).get("normalization_performed") is False)
check("sample no application", boundary.get("operator_application_performed") is False)
check("sample no memory write", boundary.get("memory_write_performed") is False)
check("sample no delivery", boundary.get("delivery_performed") is False)

failed = 0
print("RSOC SYMBOLIC REFERENCE PREVIEW VERIFY")
print("─" * 60)
for name, ok, detail in checks:
    print(f"  {'✓' if ok else '✗'} [{'PASS' if ok else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}")
    failed += 0 if ok else 1
print("─" * 60)
print(f"  Total: {len(checks)}  Passed: {len(checks) - failed}  Failed: {failed}")
print()
print("RESULT: " + ("RSOC_SYMBOLIC_REFERENCE_PREVIEW_OK" if not failed else "RSOC_SYMBOLIC_REFERENCE_PREVIEW_FAIL"))
raise SystemExit(1 if failed else 0)
