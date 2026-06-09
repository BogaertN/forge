#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT.parent
APP = HOME / "aiweb/apps/forge-operator-console/src"

RESULTS: list[tuple[str, bool, str]] = []

def check(name: str, condition: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(condition), detail))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

app = read(APP / "App.tsx")
types = read(APP / "api/types.ts")
tabs = read(APP / "shell/TopTabs.tsx")
client = read(APP / "lib/rmc-api-client.ts")
panel = read(APP / "tabs/RmcDeepDryRunTab.tsx")

check("T1_tab_type_added", "rmc_deep_dry_run" in types)
check("T1_tab_import_added", "import { RmcDeepDryRunTab }" in app)
check("T1_tab_renderer_added", "rmc_deep_dry_run: <RmcDeepDryRunTab />" in app)
check("T1_top_tab_added", "Deep Dry-Run" in tabs)

for key, route in {
    "deep_dry_run": "/api/rmc/deep-dry-run",
    "deep_pipeline_preflight": "/api/rmc/deep-pipeline-preflight",
    "protoforge2_drift_preview": "/api/rmc/protoforge2-drift-preview",
    "resurrection_preview": "/api/rmc/resurrection-preview",
    "containment_router": "/api/rmc/containment-router",
    "chi_correction_preview": "/api/rmc/chi-correction-preview",
}.items():
    check(f"T2_route_key_{key}", f"'{key}'" in client)
    check(f"T2_fallback_{key}", route in client)

for getter in [
    "getDeepDryRun",
    "getDeepPipelinePreflight",
    "getProtoForge2DriftPreview",
    "getResurrectionPreview",
    "getContainmentRouter",
    "getChiCorrectionPreview",
]:
    check(f"T3_getter_{getter}", getter in client)

check("T4_panel_component_export", "export function RmcDeepDryRunTab" in panel)
check("T4_panel_uses_manifest", "fetchRouteManifest(true)" in panel)
check("T4_panel_uses_deep_dry_run", "getDeepDryRun({ input })" in panel)
check("T4_panel_uses_preflight", "getDeepPipelinePreflight()" in panel)
check("T4_panel_uses_pf2", "getProtoForge2DriftPreview()" in panel)
check("T4_panel_uses_resurrection", "getResurrectionPreview()" in panel)
check("T4_panel_has_stage_list", "StageList" in panel and "stage_count" in panel)
check("T4_panel_has_final_route", "FinalRouteSection" in panel and "final_route" in panel)
check("T4_panel_has_forbidden_effects", "forbidden_effect_violations" in panel)
check("T4_panel_has_boundary_section", "DeepBoundarySection" in panel)

# Safety: UI must not directly call unsafe routes or browser shell-like behavior.
unsafe_terms = {
    "raw_fetch": "fetch(",
    "gated_memory_writer": "getGatedMemoryWriter",
    "memory_writer": "getMemoryWriter",
    "promotion_promote": "getPromotionPromote",
    "output_renderer": "getOutputRenderer",
    "window_open": "window.open",
    "local_storage_write": "localStorage.setItem",
    "eval": "eval(",
}
for label, term in unsafe_terms.items():
    check(f"T5_no_{label}", term not in panel)

check("T6_read_only_copy", "does not write files" in panel or "read-only" in panel.lower())
check("T6_no_projection_copy", "project" in panel.lower() and "projection" in panel.lower())
check("T6_no_identity_vault_copy", "Identity Vault" in panel)
check("T6_no_memory_commit_copy", "commit memory" in panel.lower() or "memory committed" in panel.lower())

# Staging files for the established Forge-to-React copy workflow.
STAGING = ROOT / "operator_console_src"
for path in [
    STAGING / "RmcDeepDryRunTab.tsx",
    STAGING / "rmc-api-client.ts",
    STAGING / "App.tsx",
    STAGING / "TopTabs.tsx",
    STAGING / "types.ts",
]:
    check(f"T7_staging_{path.name}", path.exists())

failed = [r for r in RESULTS if not r[1]]
print("PATCH 272 — DEEP DRY-RUN UI PANEL TESTS")
print("─" * 66)
for name, ok, detail in RESULTS:
    mark = "✓ [PASS]" if ok else "✗ [FAIL]"
    suffix = f" — {detail}" if detail else ""
    print(f"  {mark} {name}{suffix}")
print("─" * 66)
print(f"  Total: {len(RESULTS)}  Passed: {len(RESULTS)-len(failed)}  Failed: {len(failed)}")
print()
if failed:
    print("RESULT: patch272_tests=FAIL")
    sys.exit(1)
print("RESULT: patch272_tests=PASS")
