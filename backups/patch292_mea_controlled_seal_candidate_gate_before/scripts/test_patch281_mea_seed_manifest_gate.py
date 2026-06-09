#!/usr/bin/env python3
"""Patch 281 behavior tests — controlled seed manifest gate."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

PATCH_ID = "Patch 281 — MEA Controlled Seed Manifest Gate"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

checks = []

def record(name: str, ok: bool, detail="") -> None:
    checks.append((name, ok, str(detail)[:400] if detail else ""))
    print(f"  {'✓ [PASS]' if ok else '✗ [FAIL]'} {name}" + (f" — {detail}" if detail else ""))


def summary() -> int:
    passed = sum(1 for _, ok, _ in checks if ok)
    failed = len(checks) - passed
    print(f"RESULT: PATCH_281_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{len(checks)} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1

from rmc_engine_v1.mea import (
    SEED_GATE_APPROVAL_TOKEN,
    build_144hz_test_manifest,
    build_seed_manifest_gate_preview,
    build_seed_manifest_gate_rejection_preview,
    clone_manifest_for_test,
    evaluate_seed_manifest_request,
    seed_manifest_gate_boundary,
    seed_manifest_gate_status,
)


def test_boundary():
    b = seed_manifest_gate_boundary()
    record("patch_id_locked", b.get("patch") == PATCH_ID, b.get("patch"))
    record("boundary_non_mutating", b.get("non_mutating") is True)
    record("boundary_creates_post_routes", b.get("creates_post_routes") is True)
    record("boundary_requires_approval", b.get("requires_approval_token") is True)
    for key in [
        "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell",
        "performs_network_io", "seeds_live_manifests", "seals_candidates", "promotes_to_memory", "renders_user_output",
        "mutates_existing_rmc_behavior", "mutates_launcher_behavior", "mutates_operator_console_ui",
    ]:
        record(f"boundary_{key}_false", b.get(key) is False)


def test_status_and_fixture_gate():
    status = seed_manifest_gate_status()
    record("status_ok", status.get("status") == "OK")
    record("status_post_route_visible", status.get("post_route") == "/api/mea/seed-manifest-gate")
    record("status_alias_route_visible", status.get("alias_route") == "/api/mea/problem-manifest-gate")
    record("status_live_seed_inactive", status.get("live_seed_commit_active") is False)

    rejection = build_seed_manifest_gate_rejection_preview()
    record("missing_token_rejected", rejection.get("accepted") is False)
    record("missing_token_reason", rejection.get("reason_code") == "approval_token_required")
    record("missing_token_no_writes", rejection.get("writes_files") is False and rejection.get("seeds_live_manifests") is False)

    accepted = build_seed_manifest_gate_preview()
    record("fixture_accepted", accepted.get("accepted") is True, accepted)
    record("fixture_preview_only", accepted.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
    record("fixture_unknown_count_2", accepted.get("explicit_unknown_count") == 2)
    record("fixture_high_proof_debt_preserved", abs(float(accepted.get("proof_debt")) - 0.85) < 1e-9)
    record("fixture_no_live_seed", accepted.get("seeds_live_manifests") is False)
    record("fixture_no_seal", accepted.get("seals_candidates") is False)
    record("fixture_no_memory_promotion", accepted.get("promotes_to_memory") is False)
    diag = accepted.get("diagnostic", {})
    record("fixture_self_claim_recall", diag.get("self_claim_status_classification", {}).get("claim_status") == "recall")


def test_custom_manifest_gates():
    base = clone_manifest_for_test(build_144hz_test_manifest())
    ok = evaluate_seed_manifest_request({"approval_token": SEED_GATE_APPROVAL_TOKEN, "manifest": base})
    record("custom_fixture_copy_accepted", ok.get("accepted") is True)

    no_unknown = copy.deepcopy(base)
    no_unknown["unknowns"] = []
    r = evaluate_seed_manifest_request({"approval_token": SEED_GATE_APPROVAL_TOKEN, "manifest": no_unknown})
    record("custom_missing_unknown_rejected", r.get("accepted") is False)
    record("custom_missing_unknown_gate_error", any("explicit unknown" in e for e in r.get("gate_errors", [])), r.get("gate_errors"))

    verified = copy.deepcopy(base)
    verified["claim_status"] = "verified_claim"
    verified["proof_debt"] = 0.85
    rv = evaluate_seed_manifest_request({"approval_token": SEED_GATE_APPROVAL_TOKEN, "manifest": verified})
    record("custom_verified_claim_rejected", rv.get("accepted") is False)
    record("custom_verified_claim_error", any("verified_claim" in e for e in rv.get("gate_errors", []) + rv.get("validation_errors", [])), rv)

    render_allowed = copy.deepcopy(base)
    render_allowed["output_permissions"] = "render_allowed"
    rr = evaluate_seed_manifest_request({"approval_token": SEED_GATE_APPROVAL_TOKEN, "manifest": render_allowed})
    record("custom_render_allowed_rejected", rr.get("accepted") is False)
    record("custom_render_allowed_error", any("output_permissions" in e for e in rr.get("gate_errors", [])), rr.get("gate_errors"))

    drifted = copy.deepcopy(base)
    drifted["drift_state"] = {"phase_deviation": 1.0, "symbolic_entropy": 1.0, "semantic_drift": 1.0, "constraint_violations": 1.0}
    rd = evaluate_seed_manifest_request({"approval_token": SEED_GATE_APPROVAL_TOKEN, "manifest": drifted})
    record("custom_drifted_seed_rejected", rd.get("accepted") is False)
    record("custom_drifted_error", any("drift" in e for e in rd.get("gate_errors", [])), rd.get("gate_errors"))

    malformed = evaluate_seed_manifest_request({"approval_token": SEED_GATE_APPROVAL_TOKEN, "manifest": "not an object"})
    record("malformed_manifest_rejected", malformed.get("accepted") is False)


def test_main_route_surface():
    text = (ROOT / "main.py").read_text()
    record("route_manifest_lists_post_seed_gate", '"route_key":"mea_seed_manifest_gate"' in text and '"method":"POST"' in text)
    record("route_manifest_lists_status", '"/api/mea/seed-manifest-gate/status"' in text)
    record("main_post_dispatch_seed_gate", '_p281_mea_seed_manifest_gate_post_v1' in text)
    record("main_no_seal_route", '"/api/mea/seal"' not in text)
    record("main_no_problem_manifest_live_route", '"/api/mea/problem-manifest"' not in text)


def main() -> int:
    print("PATCH 281 BEHAVIOR TESTS — MEA Controlled Seed Manifest Gate")
    print(f"Forge root: {ROOT}")
    test_boundary()
    test_status_and_fixture_gate()
    test_custom_manifest_gates()
    test_main_route_surface()
    return summary()

if __name__ == "__main__":
    raise SystemExit(main())
