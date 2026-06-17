#!/usr/bin/env python3
"""Behavior test for Slice 11 candidate meaning boundary scaffold."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys


def _repo_from_argv() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    return Path.cwd().resolve()


def main() -> int:
    repo = _repo_from_argv()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))

    from aiweb_candidate_meaning_boundary_scaffold import (
        candidate_meaning_scope_record,
        demo_candidate_meaning_record,
        demo_candidate_competition_set_record,
        demo_derived_structure_custody_record,
        demo_missing_support_boundary_record,
        demo_no_action_candidate_record,
        demo_no_missing_support_boundary_record,
        demo_source_expression_custody_record,
        demo_unsupported_candidate_record,
        validate_candidate_competition_set_record,
        validate_candidate_meaning_record,
        validate_derived_structure_custody_record,
        validate_missing_support_boundary_record,
        validate_source_expression_custody_record,
    )
    from aiweb_candidate_meaning_boundary_scaffold.verify import run_verification

    passes: list[str] = []
    failures: list[str] = []

    def check(condition: bool, label: str) -> None:
        if condition:
            passes.append(label)
        else:
            failures.append(label)

    scope = candidate_meaning_scope_record()
    check(scope["status"] == "candidate_meaning_boundary_scaffold_only", "scope is scaffold-only")
    check(scope["runtime_effect"] == "none", "scope has no runtime effect")
    check(scope["dependency_change"] == "none", "scope changes no dependency")
    for key in (
        "represents_source_expression_custody",
        "represents_derived_structure_custody",
        "represents_source_grounded_candidate_meaning",
        "represents_competing_candidate_separation",
        "represents_missing_support",
        "represents_no_action_safe_candidate_state",
        "references_slice7_meaning_and_law_trace_boundaries_only",
        "references_slice8_concept_boundaries_only",
        "references_slice9_predicate_role_boundaries_only",
        "references_slice10_gate_boundaries_only",
    ):
        check(scope[key] is True, f"scope represents {key}")
    for key in (
        "live_runtime_interpretation",
        "selected_meaning",
        "final_meaning_selection",
        "truth_decision",
        "permission_grant",
        "action_authorization",
        "tool_invocation",
        "capability_route",
        "delivery_action",
        "memory_write",
        "evidence_validation",
        "external_resource_admission",
        "expression_rendering",
        "production_readiness",
        "release_authority",
    ):
        check(scope[key] is False, f"scope blocks {key}")
    check(scope["gp014_status"] == "protected_not_superseded", "GP-014 remains protected")
    check(scope["gp015_status"] == "failed_not_repaired", "GP-015 remains failed")
    check(scope["gp015r1_status"] == "uninstalled_not_live", "GP-015R1 remains uninstalled")
    check(scope["sanskrit_wordnet_status"] == "hold_unadmitted", "Sanskrit WordNet remains hold/unadmitted")

    source = demo_source_expression_custody_record()
    derived = demo_derived_structure_custody_record()
    support = demo_missing_support_boundary_record()
    no_support = demo_no_missing_support_boundary_record()
    candidate = demo_candidate_meaning_record()
    no_action = demo_no_action_candidate_record()
    unsupported = demo_unsupported_candidate_record()
    competition = demo_candidate_competition_set_record()

    check(validate_source_expression_custody_record(source).ok, "source expression custody validates")
    check(validate_derived_structure_custody_record(derived).ok, "derived structure custody validates")
    check(validate_missing_support_boundary_record(support).ok, "missing support validates")
    check(validate_missing_support_boundary_record(no_support).ok, "no-missing-support validates")
    check(validate_candidate_meaning_record(candidate).ok, "candidate meaning validates")
    check(validate_candidate_meaning_record(no_action).ok, "no-action candidate validates")
    check(validate_candidate_meaning_record(unsupported).ok, "unsupported candidate validates")
    check(validate_candidate_competition_set_record(competition).ok, "candidate competition set validates")

    check(source.source_expression_id == source.expected_id(), "source expression ID is stable")
    check(derived.derived_structure_id == derived.expected_id(), "derived structure ID is stable")
    check(support.support_boundary_id == support.expected_id(), "support boundary ID is stable")
    check(candidate.candidate_meaning_id == candidate.expected_id(), "candidate meaning ID is stable")
    check(competition.competition_set_id == competition.expected_id(), "competition set ID is stable")
    check(competition.unresolved_selection_boundary is True, "competition does not select candidate")
    check(competition.no_action_safe is True, "competition remains no-action safe")

    unsafe_candidate_fields = (
        "live_runtime_interpretation",
        "selected_meaning",
        "final_meaning_selection",
        "truth_decision",
        "permission_grant",
        "action_authorization",
        "tool_invocation",
        "capability_route",
        "delivery_action",
        "memory_write",
        "evidence_validation",
        "external_resource_admission",
        "expression_rendering",
        "production_readiness",
        "release_authority",
    )
    for field in unsafe_candidate_fields:
        bad = replace(candidate, **{field: True})
        check(not validate_candidate_meaning_record(bad).ok, f"candidate unsafe flag rejected: {field}")

    check(not validate_candidate_meaning_record(replace(candidate, no_action_safe=False)).ok, "candidate no-action flag cannot be disabled")
    check(not validate_candidate_competition_set_record(replace(competition, candidate_selection=True)).ok, "competition selection flag is rejected")
    check(not validate_candidate_competition_set_record(replace(competition, candidate_ranking=True)).ok, "competition ranking flag is rejected")
    check(not validate_candidate_competition_set_record(replace(competition, unresolved_selection_boundary=False)).ok, "competition unresolved boundary cannot be cleared")
    check(not validate_missing_support_boundary_record(replace(support, evidence_validation=True)).ok, "support evidence flag is rejected")
    check(not validate_derived_structure_custody_record(replace(derived, gate_resolution=True)).ok, "derived gate-resolution flag is rejected")
    check(not validate_source_expression_custody_record(replace(source, source_rewrite_authority=True)).ok, "source rewrite flag is rejected")

    verifier_passes, verifier_failures = run_verification(repo)
    check(not verifier_failures, "verifier sample checks pass")

    print("=" * 60)
    print("AIWEB SLICE 11 CANDIDATE MEANING BOUNDARY SCAFFOLD BEHAVIOR TEST")
    print("=" * 60)
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")
    if failures:
        print("VERDICT: FAIL - behavior test failed within Slice 11 scope")
        return 1
    print("VERDICT: PASS - behavior test passed within Slice 11 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
