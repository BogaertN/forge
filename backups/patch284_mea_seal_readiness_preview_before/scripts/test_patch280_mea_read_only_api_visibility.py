#!/usr/bin/env python3
"""
forge/scripts/test_patch280_mea_read_only_api_visibility.py

Behavior tests for Patch 280 — MEA Read-Only API / Operator Console Visibility.
"""

from __future__ import annotations

import sys
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORGE_ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    API_PREVIEW_PATCH_ID,
    MEA_READ_ONLY_PREVIEW_ROUTES,
    api_preview_boundary,
    build_claim_status_preview,
    build_preview_payload,
    build_problem_manifest_preview,
    build_replay_preview,
    build_unknown_vector_preview,
    operator_console_visibility_manifest,
)


class Results:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def check(self, name: str, ok: bool, detail="") -> None:
        if ok:
            self.passed += 1
            suffix = f" — {detail}" if detail != "" else ""
            print(f"  ✓ [PASS] {name}{suffix}")
        else:
            self.failed += 1
            suffix = f" — {detail}" if detail != "" else ""
            print(f"  ✗ [FAIL] {name}{suffix}")


def assert_boundary(r: Results, prefix: str, boundary: dict) -> None:
    expectations = {
        "read_only": True,
        "get_routes_only": True,
        "creates_post_routes": False,
        "writes_files": False,
        "writes_memory": False,
        "writes_chroma": False,
        "writes_identity_vault": False,
        "calls_llm": False,
        "executes_shell": False,
        "performs_network_io": False,
        "seeds_live_manifests": False,
        "seals_candidates": False,
        "promotes_to_memory": False,
        "renders_user_output": False,
        "mutates_existing_rmc_behavior": False,
        "mutates_launcher_behavior": False,
        "mutates_operator_console_ui": False,
    }
    for key, expected in expectations.items():
        r.check(f"{prefix}_{key}", boundary.get(key) is expected, boundary.get(key))


def main() -> int:
    r = Results()
    print("PATCH 280 BEHAVIOR TESTS — MEA Read-Only API Visibility")
    print(f"Forge root: {FORGE_ROOT}")

    boundary = api_preview_boundary()
    r.check("patch_id_locked", API_PREVIEW_PATCH_ID == "Patch 280 — MEA Read-Only API / Operator Console Visibility", API_PREVIEW_PATCH_ID)
    assert_boundary(r, "api_boundary", boundary)

    visibility = operator_console_visibility_manifest()
    r.check("operator_console_visibility_has_four_routes", len(visibility.get("routes", [])) == 4, len(visibility.get("routes", [])))
    r.check("operator_console_visibility_backend_authority", "Forge backend" in visibility.get("authority", ""), visibility.get("authority"))
    r.check("operator_console_visibility_forbids_seal", "/api/mea/seal" in visibility.get("forbidden_routes", []))
    r.check("all_preview_routes_are_get", all(route.get("method") == "GET" for route in visibility.get("routes", [])), visibility.get("routes"))
    r.check("all_preview_routes_no_approval", all(route.get("requires_approval") is False for route in visibility.get("routes", [])), visibility.get("routes"))

    problem = build_problem_manifest_preview()
    r.check("problem_preview_status_ok", problem.get("status") == "OK", problem.get("status"))
    r.check("problem_preview_endpoint", problem.get("endpoint") == "/api/mea/problem-manifest-preview", problem.get("endpoint"))
    r.check("problem_preview_fixture", problem.get("problem_manifest", {}).get("problem_id") == "144hz_substrate_status")
    r.check("problem_preview_no_live_seed", problem.get("seeds_live_manifests") is False)
    r.check("problem_preview_hash_64", len(problem.get("manifest_hash", "")) == 64, problem.get("manifest_hash"))

    unknown = build_unknown_vector_preview()
    r.check("unknown_preview_status_ok", unknown.get("status") == "OK", unknown.get("status"))
    r.check("unknown_preview_endpoint", unknown.get("endpoint") == "/api/mea/unknown-vector-preview", unknown.get("endpoint"))
    r.check("unknown_preview_count_2", unknown.get("unknown_vector", {}).get("unknown_count") == 2, unknown.get("unknown_vector"))
    r.check("unknown_preview_unverified_gap", unknown.get("unknown_vector", {}).get("unverified_count") == 1, unknown.get("unknown_vector"))

    claim = build_claim_status_preview()
    r.check("claim_preview_status_ok", claim.get("status") == "OK", claim.get("status"))
    r.check("claim_preview_endpoint", claim.get("endpoint") == "/api/mea/claim-status-preview", claim.get("endpoint"))
    r.check("claim_preview_self_recall", claim.get("self_recall_classification", {}).get("claim_status") == "recall", claim.get("self_recall_classification"))
    r.check("claim_preview_144hz_hypothesis", claim.get("hypothesis_path_classification", {}).get("claim_status") == "hypothesis", claim.get("hypothesis_path_classification"))
    cannot = " ".join(claim.get("hypothesis_path_classification", {}).get("cannot_render_as", []))
    r.check("claim_preview_hypothesis_not_verified", "verified fact" in cannot, cannot)
    r.check("claim_preview_hard_laws", claim.get("hard_render_laws", {}).get("hypothesis_not_verified_claim") is True)

    replay = build_replay_preview()
    r.check("replay_preview_status_ok", replay.get("status") == "OK", replay.get("status"))
    r.check("replay_preview_endpoint", replay.get("endpoint") == "/api/mea/replay-preview", replay.get("endpoint"))
    r.check("replay_preview_noop_confirmed", replay.get("noop_replay", {}).get("replay_confirmed") is True, replay.get("noop_replay"))
    r.check("replay_preview_path_confirmed", replay.get("hypothesis_path_preview", {}).get("confirmed_replay", {}).get("replay_confirmed") is True)
    r.check("replay_preview_sealing_inactive", replay.get("sealing_active") is False)
    r.check("replay_preview_endpoint_no_seal", replay.get("sealing_permitted_by_endpoint") is False)

    for key, route in MEA_READ_ONLY_PREVIEW_ROUTES.items():
        payload = build_preview_payload(route, route)
        r.check(f"route_payload_ok:{key}", payload.get("status") == "OK", payload.get("status"))
        r.check(f"route_payload_read_only:{key}", payload.get("read_only") is True)
        r.check(f"route_payload_no_post:{key}", payload.get("creates_post_routes") is False)
        r.check(f"route_payload_no_writes:{key}", payload.get("writes_files") is False and payload.get("writes_memory") is False)

    unknown_payload = build_preview_payload("/api/mea/not-a-route", "/api/mea/not-a-route")
    r.check("unknown_route_rejected_cleanly", unknown_payload.get("status") == "UNKNOWN_ENDPOINT", unknown_payload)
    r.check("unknown_route_still_read_only", unknown_payload.get("read_only") is True)

    print(f"RESULT: PATCH_280_BEHAVIOR {'PASS' if r.failed == 0 else 'FAIL'}  Total:{r.passed + r.failed} Passed:{r.passed} Failed:{r.failed}")
    return 0 if r.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
