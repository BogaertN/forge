#!/usr/bin/env python3
"""
forge/scripts/test_patch278_mea_replay_engine.py

Patch 278 behavior tests — MEA Replay Engine.
These tests prove deterministic replay can confirm or reject candidate hashes
without seeding live manifests, sealing candidates, writing memory, or calling
external systems.
"""

from __future__ import annotations

import sys
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORGE_ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    ClaimStatus,
    OutputPermission,
    REPLAY_LAW_FORMULA,
    build_144hz_test_manifest,
    build_default_operator_registry,
    canonical_hash,
    apply_registered_operator,
    operator_registry_summary,
    operator_registry_boundary,
    replay_candidate,
    replay_operator_path,
    replay_engine_boundary,
    validate_operator_parameters,
)


class Results:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        if ok:
            self.passed += 1
            print(f"  ✓ [PASS] {name}{' — ' + detail if detail else ''}")
        else:
            self.failed += 1
            print(f"  ✗ [FAIL] {name}{' — ' + detail if detail else ''}")


def main() -> int:
    r = Results()
    print("PATCH 278 BEHAVIOR TESTS — MEA Replay Engine")
    print(f"Forge root: {FORGE_ROOT}")

    parent = build_144hz_test_manifest()
    registry = build_default_operator_registry()
    summary = operator_registry_summary()

    r.check("replay_law_formula_locked", REPLAY_LAW_FORMULA == "Replay(H(M_t), O_k, theta_k) = H(c_i)")
    r.check("registry_operator_count_minimum", summary.get("operator_count", 0) >= 14, str(summary.get("operator_count")))
    r.check("registry_has_branch", registry.has_operator("branch"))
    r.check("registry_has_hypothesize", registry.has_operator("hypothesize"))
    r.check("registry_has_derive", registry.has_operator("derive"))
    r.check("registry_external_search_not_replayable", registry.get("external_search").replayable is False)
    r.check("registry_llm_generate_not_replayable", registry.get("llm_generate").replayable is False)

    missing_params = validate_operator_parameters("hypothesize", {})
    valid_params = validate_operator_parameters(
        "hypothesize",
        {
            "hypothesis_id": "harmonic_from_90hz",
            "hypothesis_text": "144 Hz is a harmonic hypothesis derived from 90 Hz via the golden ratio relation.",
            "confidence": 0.35,
        },
    )
    extra_params = validate_operator_parameters("hypothesize", {"hypothesis_id": "x", "unexpected": True})
    r.check("parameter_validation_missing_required_rejected", missing_params.valid is False, str(missing_params.to_dict()))
    r.check("parameter_validation_valid_hypothesis_passes", valid_params.valid is True, str(valid_params.to_dict()))
    r.check("parameter_validation_extra_parameter_rejected", extra_params.valid is False, str(extra_params.to_dict()))

    noop_expected = canonical_hash(parent)
    noop_replay = replay_candidate(parent, "noop_recall", {}, expected_candidate_hash=noop_expected)
    r.check("noop_replay_confirmed", noop_replay.replay_confirmed is True, str(noop_replay.to_dict()))
    r.check("noop_replay_hash_match", noop_replay.hash_match is True)
    r.check("noop_replay_sealing_permitted_by_replay", noop_replay.sealing_permitted_by_replay is True)

    theta = {
        "hypothesis_id": "harmonic_from_90hz",
        "hypothesis_text": "144 Hz is a harmonic hypothesis derived from 90 Hz via the golden ratio relation.",
        "confidence": 0.35,
    }
    candidate = apply_registered_operator(parent, "hypothesize", theta)
    expected_hash = canonical_hash(candidate)
    replay_ok = replay_candidate(parent, "hypothesize", theta, expected_candidate_hash=expected_hash)
    r.check("hypothesis_replay_confirmed", replay_ok.replay_confirmed is True, str(replay_ok.to_dict()))
    r.check("hypothesis_candidate_status_hypothesis", replay_ok.candidate_manifest.get("claim_status") == ClaimStatus.HYPOTHESIS.value)
    r.check("hypothesis_candidate_output_sealed", replay_ok.candidate_manifest.get("output_permissions") == OutputPermission.SEALED.value)
    r.check("hypothesis_replay_candidate_hash_expected", replay_ok.produced_candidate_hash == expected_hash)

    mutated_theta = dict(theta)
    mutated_theta["hypothesis_text"] = "144 Hz is already empirically verified in myelin."
    replay_tampered = replay_candidate(parent, "hypothesize", mutated_theta, expected_candidate_hash=expected_hash)
    r.check("mutated_theta_hash_mismatch_detected", replay_tampered.tamper_detected is True, str(replay_tampered.to_dict()))
    r.check("mutated_theta_not_confirmed", replay_tampered.replay_confirmed is False)
    r.check("mutated_theta_no_seal_permission", replay_tampered.sealing_permitted_by_replay is False)

    preview_only = replay_candidate(parent, "hypothesize", theta)
    r.check("preview_without_expected_hash_executes", preview_only.replay_executed is True)
    r.check("preview_without_expected_hash_not_confirmed", preview_only.replay_confirmed is False)
    r.check("preview_without_expected_hash_no_seal_permission", preview_only.sealing_permitted_by_replay is False)

    unknown = replay_candidate(parent, "made_up_operator", {}, expected_candidate_hash=expected_hash)
    r.check("unknown_operator_rejected", unknown.operator_registered is False and unknown.replay_confirmed is False, str(unknown.to_dict()))
    non_replayable = replay_candidate(parent, "external_search", {}, expected_candidate_hash=expected_hash)
    r.check("non_replayable_operator_rejected", non_replayable.operator_replayable is False and non_replayable.replay_confirmed is False, str(non_replayable.to_dict()))

    path_calls = [
        {"operator_id": "branch", "theta_k": {"branch_label": "substrate-vs-harmonic", "branch_unknown": "Whether 144 Hz is a substrate frequency or derived harmonic."}},
        {"operator_id": "hypothesize", "theta_k": theta},
        {"operator_id": "derive", "theta_k": {"derived_fact": "144 Hz remains hypothesis-bound until direct measurement or a sealed derivation chain exists.", "proof_debt_delta": 0.05}},
    ]
    path_preview = replay_operator_path(parent, path_calls)
    path_expected = path_preview.produced_final_hash
    path_confirmed = replay_operator_path(parent, path_calls, expected_final_hash=path_expected)
    r.check("operator_path_preview_executed", path_preview.replay_executed is True, str(path_preview.to_dict()))
    r.check("operator_path_confirmed", path_confirmed.replay_confirmed is True, str(path_confirmed.to_dict()))
    r.check("operator_path_step_count", len(path_confirmed.steps) == 3, str(len(path_confirmed.steps)))

    boundary_checks = [
        ("registry", operator_registry_boundary()),
        ("replay", replay_engine_boundary()),
    ]
    for label, boundary in boundary_checks:
        r.check(f"{label}_boundary_read_only", boundary.get("read_only") is True)
        r.check(f"{label}_boundary_no_writes_files", boundary.get("writes_files") is False)
        r.check(f"{label}_boundary_no_writes_memory", boundary.get("writes_memory") is False)
        r.check(f"{label}_boundary_no_writes_chroma", boundary.get("writes_chroma") is False)
        r.check(f"{label}_boundary_no_writes_identity_vault", boundary.get("writes_identity_vault") is False)
        r.check(f"{label}_boundary_no_calls_llm", boundary.get("calls_llm") is False)
        r.check(f"{label}_boundary_no_executes_shell", boundary.get("executes_shell") is False)
        r.check(f"{label}_boundary_no_creates_post_routes", boundary.get("creates_post_routes") is False)
        r.check(f"{label}_boundary_no_seeds_live_manifests", boundary.get("seeds_live_manifests") is False)
        r.check(f"{label}_boundary_no_seals_candidates", boundary.get("seals_candidates") is False)
        r.check(f"{label}_boundary_no_promotes_to_memory", boundary.get("promotes_to_memory") is False)

    total = r.passed + r.failed
    print(f"RESULT: PATCH_278_BEHAVIOR {'PASS' if r.failed == 0 else 'FAIL'}  Total:{total} Passed:{r.passed} Failed:{r.failed}")
    return 0 if r.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
