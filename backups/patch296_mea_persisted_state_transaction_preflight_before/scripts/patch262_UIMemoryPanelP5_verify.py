#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
checks: list[tuple[str, bool, str]] = []

def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append((name, condition, detail))
    print(f"[{'PASS' if condition else 'FAIL'}] {name}{(' :: ' + detail) if detail else ''}")

required = [
    "operator_console_src/RmcMemoryTab.tsx",
    "operator_console_src/rmc-panel-primitives.tsx",
    "operator_console_src/rmc-api-client.ts",
    "operator_console_src/rmc-ui-guards.ts",
    "operator_console_src/rmc-panel-health.ts",
    "operator_console_src/README_patch262_UIMemoryPanelP5.md",
    "scripts/test_rmc_memory_panel_p5_component_split.py",
    "scripts/patch262_UIMemoryPanelP5_verify.py",
    "SHA256SUMS.txt",
]
for rel in required:
    check(f"file_exists_{rel}", (ROOT / rel).exists(), rel)

sha_path = ROOT / "SHA256SUMS.txt"
sha_text = sha_path.read_text(encoding="utf-8") if sha_path.exists() else ""
check("sha_excludes_bad_artifacts", all(bad not in sha_text for bad in ["__pycache__", ".pyc", ".venv", "node_modules", "chroma_db", ".sqlite", ".db"]))

sha_ok = True
sha_detail = ""
if sha_path.exists():
    for raw in sha_text.splitlines():
        if not raw.strip():
            continue
        expected, rel = raw.split(maxsplit=1)
        rel = rel.lstrip("* ")
        f = ROOT / rel
        if not f.exists():
            sha_ok = False
            sha_detail = f"missing {rel}"
            break
        actual = hashlib.sha256(f.read_bytes()).hexdigest()
        if actual != expected:
            sha_ok = False
            sha_detail = f"hash mismatch {rel}"
            break
check("sha_manifest_hashes_ok", sha_ok, sha_detail)

panel = (ROOT / "operator_console_src/RmcMemoryTab.tsx").read_text(encoding="utf-8") if (ROOT / "operator_console_src/RmcMemoryTab.tsx").exists() else ""
prims = (ROOT / "operator_console_src/rmc-panel-primitives.tsx").read_text(encoding="utf-8") if (ROOT / "operator_console_src/rmc-panel-primitives.tsx").exists() else ""
check("panel_imports_primitives", "../lib/rmc-panel-primitives" in panel)
check("panel_no_inline_metric_component", "function Metric" not in panel)
check("panel_no_inline_route_availability", "function RouteAvailability" not in panel)
check("primitives_exports_metric", "export function Metric" in prims)
check("primitives_exports_review_queue_list", "export function ReviewQueueList" in prims)
check("primitives_ui_only_no_fetch", "fetch(" not in prims)
check("p3_guard_preserved", "evaluateGuardPromotionArmState" in panel and "buildGuardConfirmationPhrase" in panel)
check("p4_health_preserved", "makeEndpointHealth" in panel and "summarizeEndpointHealth" in panel)
check("llm_toggle_default_off_preserved", "const [llmEnabled, setLlmEnabled] = useState(false)" in panel)

compile_cmd = [sys.executable, "-m", "py_compile", str(ROOT / "scripts/test_rmc_memory_panel_p5_component_split.py")]
compiled = subprocess.run(compile_cmd, cwd=ROOT, capture_output=True, text=True)
check("py_compile_behavior_test", compiled.returncode == 0, (compiled.stderr or compiled.stdout).strip())

behavior = subprocess.run([sys.executable, str(ROOT / "scripts/test_rmc_memory_panel_p5_component_split.py")], cwd=ROOT, capture_output=True, text=True)
check("behavior_test_passes", behavior.returncode == 0 and "RESULT: rmc_memory_panel_p5_component_split_tests_pass=True" in behavior.stdout, behavior.stdout[-500:])

failed = [name for name, ok, _ in checks if not ok]
print("────────────────────────────────────────────────────────────────────────")
print(f"Total: {len(checks)}")
print(f"Passed: {len(checks)-len(failed)}")
print(f"Failed: {len(failed)}")
if failed:
    print("FAILED_CHECKS:", ", ".join(failed))
    print("RESULT: PATCH_262_UI_MEMORY_PANEL_P5_VERIFY_OK_FALSE")
    raise SystemExit(1)
print("RESULT: PATCH_262_UI_MEMORY_PANEL_P5_VERIFY_OK")
