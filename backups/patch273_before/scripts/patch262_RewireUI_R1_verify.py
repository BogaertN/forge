#!/usr/bin/env python3
"""Patch 262-RewireUI-R1 verifier."""
from pathlib import Path
import hashlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CHECKS = []

def record(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{(' :: ' + detail) if detail else ''}")

def text(path):
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""

files = [
    ROOT / "main.py",
    ROOT / "operator_console_src" / "rmc-api-client.ts",
    ROOT / "operator_console_src" / "rmc-api-client.js",
    ROOT / "scripts" / "test_rmc_route_manifest_RewireUI_R1.py",
    ROOT / "scripts" / "patch262_RewireUI_R1_verify.py",
    ROOT / "scripts" / "README_patch262_RewireUI_R1.md",
    ROOT / "SHA256SUMS.txt",
]

for f in files:
    record(f"file_exists_{f.relative_to(ROOT)}", f.exists(), str(f.relative_to(ROOT)))

main = text(ROOT / "main.py")
client = text(ROOT / "operator_console_src" / "rmc-api-client.ts")
sha = text(ROOT / "SHA256SUMS.txt")

record("api_contract_version_rewireui_R1", "1.1.0-RewireUI-R1" in main)
record("route_manifest_function_present", "_p262z_rmc_route_manifest_v1" in main)
record("route_manifest_dispatch_present", 'elif _p249_req_path == "/api/rmc/route-manifest"' in main)
record("route_manifest_contains_llm_renderer", "/api/rmc/llm-renderer/status" in main)
record("route_manifest_contains_glyph_routes", "/api/rmc/glyph-renderer/status" in main and "/api/rmc/phase-glyph" in main and "/api/rmc/glyph-packet" in main)
record("route_manifest_contains_promotion_routes", "/api/rmc/promotion-path/status" in main and "/api/rmc/promotion-path/preview" in main and "/api/rmc/promotion-path/promote" in main)
record("promotion_token_correct", "APPROVE_RMC_PROMOTION" in main and "APPROVE_PROMOTE_MEMORY" not in main)
record("react_client_route_manifest_cache", "routeManifestCache" in client and "fetchRouteManifest" in client)
record("react_client_llm_renderer_exports", "getLlmRendererStatus" in client and "getOutputRenderer" in client and "model_endpoint" in client)
record("react_client_glyph_exports", "getGlyphRendererStatus" in client and "getPhaseGlyph" in client and "getGlyphPacket" in client)
record("react_client_promotion_exports", "getPromotionStatus" in client and "getPromotionPreview" in client)
record("sha_excludes_pycache_pyc_venv_node_modules", all(x not in sha for x in ["__pycache__", ".pyc", ".venv", "node_modules", "dist", "build"]))

# SHA validation from ROOT.
if (ROOT / "SHA256SUMS.txt").exists:
    proc = subprocess.run(["sha256sum", "-c", "SHA256SUMS.txt"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    record("sha_manifest_hashes_ok", proc.returncode == 0, proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "")

proc = subprocess.run([sys.executable, "-m", "py_compile", "main.py", "scripts/test_rmc_route_manifest_RewireUI_R1.py", "scripts/patch262_RewireUI_R1_verify.py"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
record("py_compile_changed_files", proc.returncode == 0, proc.stdout.strip()[:240])

proc = subprocess.run([sys.executable, "scripts/test_rmc_route_manifest_RewireUI_R1.py"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
record("scripts_test_rmc_route_manifest_RewireUI_R1.py_passes", proc.returncode == 0, proc.stdout.strip()[-500:])

failed = [c for c in CHECKS if not c[1]]
print("─" * 72)
print(f"Total: {len(CHECKS)}")
print(f"Passed: {len(CHECKS) - len(failed)}")
print(f"Failed: {len(failed)}")
if failed:
    print("RESULT: PATCH_262_REWIREUI_R1_VERIFY_FAILED")
    sys.exit(1)
print("RESULT: PATCH_262_REWIREUI_R1_VERIFY_OK")
