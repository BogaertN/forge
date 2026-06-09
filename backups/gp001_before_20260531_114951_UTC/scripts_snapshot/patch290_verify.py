#!/usr/bin/env python3
"""Patch 290 verifier — MEA True Gate Engine Extension Preview."""
from __future__ import annotations

import hashlib
import os
import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "main.py",
    "SHA256SUMS.txt",
    "rmc_engine_v1/mea/__init__.py",
    "rmc_engine_v1/mea/manifest_schema.py",
    "rmc_engine_v1/mea/candidate_generator.py",
    "rmc_engine_v1/mea/coherence_extension.py",
    "rmc_engine_v1/mea/gate_engine.py",
    "rmc_engine_v1/mea/discovery_kernel.py",
    "scripts/patch290_verify.py",
    "scripts/test_patch290_mea_gate_engine.py",
    "scripts/README_290.md",
]
NEW_GET_ROUTES = ["/api/mea/gate-engine/status", "/api/mea/gate-engine-preview"]
NEW_POST_ROUTES = ["/api/mea/gate-engine-gate"]
FORBIDDEN_RUNTIME_STRINGS = [
    "subprocess", "os.system", "open(", "requests", "urllib", "httpx", "sqlite3",
    "chromadb", "anthropic", "openai", "langchain", "socket", "Popen",
]

passes = 0
fails = 0


def check(name: str, cond: bool, detail: object = "") -> None:
    global passes, fails
    if cond:
        passes += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✓ [PASS] {name}{suffix}")
    else:
        fails += 1
        suffix = f" — {detail}" if detail not in ("", None) else ""
        print(f"  ✗ [FAIL] {name}{suffix}")


print("PATCH 290 VERIFIER — MEA True Gate Engine Extension Preview")
print(f"Forge root: {ROOT}")
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

for rel in REQUIRED_FILES:
    check(f"required_file:{rel}", (ROOT / rel).exists())

sha_ok = True
try:
    for line in (ROOT / "SHA256SUMS.txt").read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        digest, rel = line.split(maxsplit=1)
        rel = rel.strip().lstrip("*")
        path = ROOT / rel
        if not path.exists():
            print(f"    missing listed file: {rel}")
            sha_ok = False
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            print(f"    sha mismatch: {rel}")
            sha_ok = False
except Exception as exc:
    print(f"    sha check error: {exc}")
    sha_ok = False
check("sha256sums_match", sha_ok)

for rel in REQUIRED_FILES:
    if rel.endswith(".py"):
        try:
            py_compile.compile(str(ROOT / rel), doraise=True)
            check(f"py_compile:{rel}", True)
        except Exception as exc:
            check(f"py_compile:{rel}", False, str(exc)[:160])

runtime_text = (ROOT / "rmc_engine_v1/mea/gate_engine.py").read_text()
violations = [term for term in FORBIDDEN_RUNTIME_STRINGS if term in runtime_text]
check("runtime_boundary_scan:rmc_engine_v1/mea/gate_engine.py", not violations, "clean" if not violations else violations)

from rmc_engine_v1.mea import (  # noqa: E402
    GATE_ENGINE_APPROVAL_TOKEN,
    GATE_ENGINE_PATCH_ID,
    GATE_ENGINE_STATUS_ROUTE,
    GATE_ENGINE_PREVIEW_ROUTE,
    GATE_ENGINE_POST_ROUTE,
    build_gate_engine_preview,
    evaluate_gate_engine_request,
    gate_engine_boundary,
    gate_engine_status,
    kernel_identity,
)

check("patch_id_export", GATE_ENGINE_PATCH_ID == "Patch 290 — True MEA Gate Engine Extension Preview", GATE_ENGINE_PATCH_ID)
check("token_export", GATE_ENGINE_APPROVAL_TOKEN == "APPROVE_MEA_GATE_ENGINE_PREVIEW", GATE_ENGINE_APPROVAL_TOKEN)
check("route_export_status", GATE_ENGINE_STATUS_ROUTE == "/api/mea/gate-engine/status")
check("route_export_preview", GATE_ENGINE_PREVIEW_ROUTE == "/api/mea/gate-engine-preview")
check("route_export_post", GATE_ENGINE_POST_ROUTE == "/api/mea/gate-engine-gate")

boundary = gate_engine_boundary()
for key in [
    "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault",
    "calls_llm", "executes_shell", "performs_network_io", "seeds_live_manifests",
    "commits_live_candidates", "advances_live_manifest", "seals_candidates",
    "promotes_to_memory", "renders_user_output", "mutates_operator_console_ui",
]:
    check(f"boundary_{key}_false", boundary.get(key) is False, boundary.get(key))
check("boundary_non_mutating", boundary.get("non_mutating") is True)
check("boundary_score_cannot_override", boundary.get("score_can_override_gates") is False)

status = gate_engine_status()
preview = build_gate_engine_preview()
reports = {r.get("candidate_id"): r for r in preview.get("gate_reports", [])}
check("status_ok", status.get("status") == "OK")
check("status_visible", status.get("gate_engine_visible") is True)
check("status_patch290", status.get("current_patch") == GATE_ENGINE_PATCH_ID, status.get("current_patch"))
check("status_no_seal", status.get("candidate_sealing_active") is False)
check("status_no_memory", status.get("memory_promotion_active") is False)
check("preview_ok", preview.get("status") == "OK")
check("preview_candidate_count_4", preview.get("candidate_count") == 4, preview.get("candidate_count"))
check("preview_gate_report_count_4", preview.get("gate_report_count") == 4, preview.get("gate_report_count"))
check("preview_selectable_count_2", preview.get("selectable_preview_count") == 2, preview.get("selectable_preview_count"))
check("preview_reference_count_1", preview.get("reference_only_count") == 1, preview.get("reference_only_count"))
check("preview_rejected_count_1", preview.get("rejected_count") == 1, preview.get("rejected_count"))
check("preview_hash_stability", preview.get("gate_report_hash_stability_proven") is True)
check("preview_score_no_override", preview.get("score_can_override_gates") is False)
check("preview_no_seal", preview.get("seals_candidates") is False and preview.get("candidate_sealing_active") is False)
check("preview_no_memory", preview.get("promotes_to_memory") is False and preview.get("memory_promotion_active") is False)

expected_decisions = {
    "cg_recall_001": "REFERENCE_ONLY",
    "cg_hypothesis_001": "PASS_PREVIEW_ONLY",
    "cg_branch_001": "PASS_BOUNDED_PREVIEW_ONLY",
    "cg_tamper_001": "REJECTED",
}
for cid, decision in expected_decisions.items():
    report = reports.get(cid, {})
    check(f"report_exists:{cid}", bool(report))
    check(f"decision:{cid}", report.get("decision") == decision, report.get("decision"))
    check(f"seal_blocked:{cid}", report.get("seal_blocked") is True)
    check(f"memory_blocked:{cid}", report.get("memory_promotion_blocked") is True)
    check(f"score_no_override:{cid}", report.get("score_can_override_gate") is False)
    check(f"gate_hash_64:{cid}", isinstance(report.get("gate_report_hash"), str) and len(report.get("gate_report_hash")) == 64)

missing = evaluate_gate_engine_request({})
approved = evaluate_gate_engine_request({"approval_token": GATE_ENGINE_APPROVAL_TOKEN})
check("missing_token_rejected", missing.get("status") == "REJECTED")
check("missing_token_reason", missing.get("reason_code") == "approval_token_required")
check("missing_token_no_writes", missing.get("writes_files") is False and missing.get("writes_memory") is False)
check("approved_status_ok", approved.get("status") == "OK")
check("approved_preview_only", approved.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
check("approved_no_seal", approved.get("seals_candidates") is False)
check("approved_no_memory", approved.get("promotes_to_memory") is False)
check("approved_score_no_override", approved.get("score_can_override_gates") is False)

kernel = kernel_identity()
check("kernel_stage_patch290", kernel.get("kernel_stage") == "gate_engine_preview_patch290", kernel.get("kernel_stage"))
check("kernel_gate_engine_visible", kernel.get("gate_engine_visible") is True)
check("kernel_sealing_inactive", kernel.get("sealing_active") is False)

main_text = (ROOT / "main.py").read_text()
for route in NEW_GET_ROUTES + NEW_POST_ROUTES:
    check(f"new_route:{route}", route in main_text)
check("main_get_dispatch_gate_status", "_p290_mea_gate_engine_status_v1" in main_text and '"/api/mea/gate-engine/status"' in main_text)
check("main_get_dispatch_gate_preview", "_p290_mea_gate_engine_preview_v1" in main_text and '"/api/mea/gate-engine-preview"' in main_text)
check("main_post_dispatch_gate_engine", "_p290_mea_gate_engine_gate_post_v1" in main_text and '"/api/mea/gate-engine-gate"' in main_text)
check("foundation_status_patch290", '"mode": "mea_foundation_status_patch290"' in main_text and '"current_patch": "Patch 290 — True MEA Gate Engine Extension Preview"' in main_text)
check("foundation_reports_gate_engine", '"gate_engine": {' in main_text)
check("no_real_mea_seal_route", '"/api/mea/seal"' not in main_text)
check("no_live_candidates_route", '"/api/mea/candidates"' not in main_text)
check("no_live_problem_manifest_route", '"/api/mea/problem-manifest"' not in main_text)

behavior = subprocess.run([sys.executable, str(ROOT / "scripts/test_patch290_mea_gate_engine.py")], cwd=str(ROOT), text=True, capture_output=True)
print(behavior.stdout, end="")
if behavior.stderr:
    print(behavior.stderr[:500], end="")
check("behavior_test_exit_0", behavior.returncode == 0, f"returncode={behavior.returncode}")

print(f"RESULT: PATCH_290_VERIFY {'PASS' if fails == 0 else 'FAIL'}  Total:{passes+fails} Passed:{passes} Failed:{fails}")
sys.exit(0 if fails == 0 else 1)
