#!/usr/bin/env python3
"""
forge/scripts/test_patch275_mea_foundation.py

Patch 275 behavior tests. Stdlib only. No writes, no shell commands, no LLM calls.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import List, Tuple


def find_forge_root(cli_value: str | None) -> Path:
    if cli_value:
        return Path(cli_value).expanduser().resolve()
    cwd = Path.cwd().resolve()
    if (cwd / "forge" / "main.py").exists():
        return (cwd / "forge").resolve()
    if (cwd / "main.py").exists() and (cwd / "rmc_engine_v1").exists():
        return cwd
    home_forge = Path.home() / "forge"
    if (home_forge / "main.py").exists():
        return home_forge.resolve()
    raise SystemExit("Could not locate Forge root")


def record(results: List[Tuple[str, str]], ok: bool, name: str, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    print(f"  {'✓' if ok else '✗'} [{status}] {name}" + (f" — {detail}" if detail else ""))
    results.append((status, name))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", default=None)
    args = parser.parse_args()
    forge = find_forge_root(args.forge_root)
    sys.path.insert(0, str(forge))

    from rmc_engine_v1.mea import (
        Assumption,
        ClaimStatus,
        MemoryRef,
        OutputPermission,
        PhaseState,
        build_144hz_test_manifest,
        build_manifest,
        canonical_hash,
        detect_unknowns,
        from_dict,
        foundation_boundary,
        kernel_foundation_probe,
        kernel_identity,
        build_foundation_kernel,
        to_dict,
        validate_manifest,
    )

    print("PATCH 275R BEHAVIOR TESTS — MEA Foundation Visibility")
    print(f"Forge root: {forge}")
    results: List[Tuple[str, str]] = []

    manifest = build_manifest(
        problem_id="unit_valid_manifest",
        goal="Determine whether the foundation schema is deterministic.",
        known_facts=["Patch 275 is a read-only MEA foundation patch."],
        unknowns=["Whether canonical hashes remain stable across timestamp differences."],
        constraints=["No writes."],
        assumptions=[Assumption(text="Schema validation is deterministic.", confidence=0.75)],
        success_conditions=["Two equivalent manifests produce the same hash."],
        failure_conditions=["A required field is missing."],
        phase_state=PhaseState.PHI5.value,
        proof_debt=0.40,
        claim_status=ClaimStatus.HYPOTHESIS.value,
        output_permissions=OutputPermission.SEALED.value,
        memory_ancestry=[MemoryRef(memory_key="mea_doc_v1", source="MEA Forge Discovery Kernel v1", relevance=0.9, evidence_tier="architecture")],
    )
    record(results, validate_manifest(manifest).valid, "valid_manifest_passes_validation")
    h1 = canonical_hash(manifest)
    clone_data = to_dict(manifest)
    clone_data["created_at"] = "2099-01-01T00:00:00+00:00"
    clone_data["updated_at"] = "2099-01-01T00:00:00+00:00"
    clone = from_dict(clone_data)
    h2 = canonical_hash(clone)
    record(results, h1 == h2, "canonical_hash_excludes_timestamps")
    record(results, len(h1) == 64 and all(c in "0123456789abcdef" for c in h1), "canonical_hash_hex_format")

    try:
        build_manifest(problem_id="bad_missing_unknowns", goal="Bad", known_facts=["Fact"], unknowns=[], success_conditions=["Done"])
        record(results, False, "missing_unknowns_rejected", "no exception")
    except ValueError:
        record(results, True, "missing_unknowns_rejected")

    try:
        build_manifest(problem_id="bad_verified", goal="Bad", known_facts=["Fact"], unknowns=["Unknown"], success_conditions=["Done"], claim_status=ClaimStatus.VERIFIED_CLAIM.value, proof_debt=0.55)
        record(results, False, "verified_claim_with_high_proof_debt_rejected", "no exception")
    except ValueError:
        record(results, True, "verified_claim_with_high_proof_debt_rejected")

    fixture = build_144hz_test_manifest()
    vector = detect_unknowns(fixture)
    vector_dict = vector.to_dict()
    record(results, fixture.problem_id == "144hz_substrate_status", "144hz_fixture_problem_id")
    record(results, fixture.claim_status == ClaimStatus.TEST_REQUIRED.value, "144hz_fixture_seed_status_test_required")
    record(results, fixture.output_permissions == OutputPermission.SEALED.value, "144hz_fixture_sealed")
    record(results, vector.unknown_count == 2, "144hz_unknown_vector_has_two_explicit_unknowns", str(vector.unknown_count))
    record(results, any("myelin" in item.lower() for item in vector.explicit_unknowns), "144hz_myelin_unknown_present")
    record(results, any("derived harmonic" in item.lower() for item in vector.explicit_unknowns), "144hz_harmonic_unknown_present")
    record(results, vector.unverified_count >= 1, "144hz_absence_of_measurement_flagged_unverified", str(vector.unverified_count))
    record(results, vector.weak_count >= 1, "144hz_high_proof_debt_flagged", str(vector.weak_count))
    record(results, vector_dict["has_errors"] is False, "144hz_manifest_no_errors")


    kernel = build_foundation_kernel()
    identity = kernel_identity()
    probe = kernel_foundation_probe()
    record(results, identity["kernel_name"] == "Forge Discovery Kernel", "kernel_identity_name_visible")
    record(results, identity["foundation_visible"] is True, "kernel_foundation_visible")
    record(results, identity["full_runtime_active"] is False, "kernel_full_runtime_not_overclaimed")
    record(results, identity["boundary"]["writes_files"] is False, "kernel_boundary_no_file_writes")
    record(results, identity["boundary"]["calls_llm"] is False, "kernel_boundary_no_llm")
    record(results, probe["test_fixture"]["problem_id"] == "144hz_substrate_status", "kernel_probe_144hz_fixture_visible")
    record(results, len(probe["test_fixture"]["manifest_hash"]) == 64, "kernel_probe_manifest_hash_64")
    inspected = kernel.inspect_manifest(fixture)
    record(results, inspected["problem_id"] == "144hz_substrate_status", "kernel_inspect_manifest_problem_id")
    record(results, inspected["unknown_vector"]["explicit_unknown_count"] == 2, "kernel_inspect_unknown_count_2")

    boundary = foundation_boundary()
    record(results, boundary["read_only"] is True, "boundary_read_only")
    record(results, boundary["writes_files"] is False, "boundary_no_file_writes")
    record(results, boundary["calls_llm"] is False, "boundary_no_llm")
    record(results, boundary["executes_shell"] is False, "boundary_no_shell")
    record(results, boundary["seal_or_write_routes"] is False, "boundary_no_seal_or_write_routes")

    passed = sum(1 for status, _ in results if status == "PASS")
    failed = sum(1 for status, _ in results if status == "FAIL")
    print(f"RESULT: PATCH_275R_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{len(results)} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
