#!/usr/bin/env python3
"""Patch 281 verifier — MEA Controlled Seed Manifest Gate."""
from __future__ import annotations

import hashlib
import py_compile
import sys
from pathlib import Path

PATCH_ID = "Patch 281 — MEA Controlled Seed Manifest Gate"
ROOT = Path(__file__).resolve().parents[1]

checks = []

def record(name: str, ok: bool, detail: str = "") -> None:
    checks.append((name, ok, detail))
    mark = "✓ [PASS]" if ok else "✗ [FAIL]"
    suffix = f" — {detail}" if detail else ""
    print(f"  {mark} {name}{suffix}")


def fail_fast_summary() -> int:
    passed = sum(1 for _, ok, _ in checks if ok)
    failed = len(checks) - passed
    print(f"RESULT: PATCH_281_VERIFY {'PASS' if failed == 0 else 'FAIL'}  Total:{len(checks)} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def check_required_files() -> None:
    required = [
        "main.py",
        "rmc_engine_v1/mea/__init__.py",
        "rmc_engine_v1/mea/manifest_schema.py",
        "rmc_engine_v1/mea/unknown_detector.py",
        "rmc_engine_v1/mea/proof_debt_scorer.py",
        "rmc_engine_v1/mea/information_gain_scorer.py",
        "rmc_engine_v1/mea/convergence_scorer.py",
        "rmc_engine_v1/mea/goal_ancestry_scorer.py",
        "rmc_engine_v1/mea/operator_cost_scorer.py",
        "rmc_engine_v1/mea/operator_registry.py",
        "rmc_engine_v1/mea/replay_engine.py",
        "rmc_engine_v1/mea/claim_status_classifier.py",
        "rmc_engine_v1/mea/api_preview.py",
        "rmc_engine_v1/mea/seed_manifest_gate.py",
        "rmc_engine_v1/mea/discovery_kernel.py",
        "scripts/patch281_verify.py",
        "scripts/test_patch281_mea_seed_manifest_gate.py",
        "scripts/README_281.md",
        "SHA256SUMS.txt",
    ]
    for rel in required:
        record(f"required_file:{rel}", (ROOT / rel).exists())


def check_sha256sums() -> None:
    sums = ROOT / "SHA256SUMS.txt"
    ok = True
    missing = []
    mismatch = []
    for line in sums.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        digest, rel = line.split(None, 1)
        rel = rel.strip().lstrip("*")
        path = ROOT / rel
        if not path.exists():
            ok = False; missing.append(rel); continue
        actual = sha256(path)
        if actual != digest:
            ok = False; mismatch.append(rel)
    detail = "all listed files match" if ok else f"missing={missing} mismatch={mismatch}"
    record("sha256sums_match", ok, detail)


def check_py_compile() -> None:
    targets = [
        "main.py",
        *[str(p.relative_to(ROOT)) for p in sorted((ROOT / "rmc_engine_v1/mea").glob("*.py"))],
        "scripts/patch281_verify.py",
        "scripts/test_patch281_mea_seed_manifest_gate.py",
    ]
    for rel in targets:
        try:
            py_compile.compile(str(ROOT / rel), doraise=True)
            record(f"py_compile:{rel}", True)
        except Exception as exc:
            record(f"py_compile:{rel}", False, str(exc)[:200])


def check_runtime_boundary_scan() -> None:
    forbidden = [
        "subprocess.", "os.system", "Popen(", "requests.", "urllib.request", "open(", ".write(", "sqlite3", "chromadb",
    ]
    targets = [
        ROOT / "rmc_engine_v1/mea/seed_manifest_gate.py",
        ROOT / "rmc_engine_v1/mea/discovery_kernel.py",
    ]
    for target in targets:
        text = target.read_text()
        hits = [x for x in forbidden if x in text]
        # seed module may not write/open/exec/network. No exceptions needed.
        record(f"runtime_boundary_scan:{target.relative_to(ROOT)}", not hits, "clean" if not hits else ",".join(hits))


def check_imports_and_semantics() -> None:
    sys.path.insert(0, str(ROOT))
    from rmc_engine_v1.mea import (
        SEED_GATE_PATCH_ID,
        SEED_GATE_APPROVAL_TOKEN,
        SEED_GATE_POST_ROUTE,
        SEED_GATE_STATUS_ROUTE,
        SEED_GATE_ALIAS_ROUTE,
        build_144hz_test_manifest,
        build_seed_manifest_gate_preview,
        build_seed_manifest_gate_rejection_preview,
        evaluate_seed_manifest_request,
        seed_manifest_gate_boundary,
        seed_manifest_gate_status,
        to_dict,
    )

    record("patch281_id_export", SEED_GATE_PATCH_ID == PATCH_ID, SEED_GATE_PATCH_ID)
    record("seed_gate_token_export", SEED_GATE_APPROVAL_TOKEN == "APPROVE_MEA_SEED_MANIFEST_GATE")
    record("seed_gate_post_route", SEED_GATE_POST_ROUTE == "/api/mea/seed-manifest-gate")
    record("seed_gate_status_route", SEED_GATE_STATUS_ROUTE == "/api/mea/seed-manifest-gate/status")
    record("seed_gate_alias_route", SEED_GATE_ALIAS_ROUTE == "/api/mea/problem-manifest-gate")

    boundary = seed_manifest_gate_boundary()
    record("seed_boundary_non_mutating", boundary.get("non_mutating") is True)
    record("seed_boundary_requires_token", boundary.get("requires_approval_token") is True)
    for key in ["writes_files","writes_memory","writes_chroma","writes_identity_vault","calls_llm","executes_shell","performs_network_io","seeds_live_manifests","seals_candidates","promotes_to_memory"]:
        record(f"seed_boundary_no_{key}", boundary.get(key) is False)

    status = seed_manifest_gate_status()
    record("seed_status_ok", status.get("status") == "OK")
    record("seed_status_live_commit_inactive", status.get("live_seed_commit_active") is False)

    rejection = build_seed_manifest_gate_rejection_preview()
    record("seed_missing_token_rejected", rejection.get("accepted") is False and rejection.get("reason_code") == "approval_token_required")

    accepted = build_seed_manifest_gate_preview()
    record("seed_fixture_accepted_preview_only", accepted.get("accepted") is True and accepted.get("gate_status") == "ACCEPTED_PREVIEW_ONLY")
    record("seed_fixture_no_live_commit", accepted.get("seeds_live_manifests") is False)
    record("seed_fixture_not_sealed_candidate", accepted.get("seals_candidates") is False)
    record("seed_fixture_unknown_count_2", accepted.get("explicit_unknown_count") == 2, str(accepted.get("explicit_unknown_count")))
    record("seed_fixture_hash_64", len(str(accepted.get("manifest_hash", ""))) == 64)

    manifest = to_dict(build_144hz_test_manifest())
    manifest["unknowns"] = []
    missing_unknowns = evaluate_seed_manifest_request({"approval_token": SEED_GATE_APPROVAL_TOKEN, "manifest": manifest})
    record("seed_rejects_missing_unknowns", missing_unknowns.get("accepted") is False and any("explicit unknown" in e for e in missing_unknowns.get("gate_errors", [])))

    verified = to_dict(build_144hz_test_manifest())
    verified["claim_status"] = "verified_claim"
    verified["proof_debt"] = 0.85
    verified_bad = evaluate_seed_manifest_request({"approval_token": SEED_GATE_APPROVAL_TOKEN, "manifest": verified})
    record("seed_rejects_verified_claim_seed", verified_bad.get("accepted") is False and any("verified_claim" in e for e in verified_bad.get("gate_errors", [])))


def check_main_routes() -> None:
    source = (ROOT / "main.py").read_text()
    preserved = [
        "/api/rmc/deep-dry-run",
        "/api/rmc/deep-pipeline-preflight",
        "/api/rmc/protoforge2-drift-preview",
        "/api/rmc/resurrection-preview",
        "/api/rmc/containment-router",
        "/api/rmc/chi-correction-preview",
        "/api/rmc/route-manifest",
        "/api/aiweb-os/lifecycle-manifest",
        "/api/aiweb-os/status",
        "/api/aiweb-os/logs",
        "/api/aiweb-os/build-manifest",
        "/api/mea/foundation-status",
        "/api/mea/problem-manifest-preview",
        "/api/mea/unknown-vector-preview",
        "/api/mea/claim-status-preview",
        "/api/mea/replay-preview",
    ]
    for route in preserved:
        record(f"preserved_route:{route}", route in source)
    record("new_get_route:/api/mea/seed-manifest-gate/status", '"/api/mea/seed-manifest-gate/status"' in source)
    record("new_post_route:/api/mea/seed-manifest-gate", '"/api/mea/seed-manifest-gate"' in source and 'method":"POST"' in source)
    record("alias_post_route:/api/mea/problem-manifest-gate", '"/api/mea/problem-manifest-gate"' in source)
    record("no_mea_seal_route", '"/api/mea/seal"' not in source)
    record("no_live_problem_manifest_route", '"/api/mea/problem-manifest"' not in source)


def main() -> int:
    print("PATCH 281 VERIFIER — MEA Controlled Seed Manifest Gate")
    print(f"Forge root: {ROOT}")
    check_required_files()
    check_sha256sums()
    check_py_compile()
    check_runtime_boundary_scan()
    check_imports_and_semantics()
    check_main_routes()
    return fail_fast_summary()

if __name__ == "__main__":
    raise SystemExit(main())
