#!/usr/bin/env python3
"""Behavior test for AI.Web Slice 3 controlled status/claim scaffold."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: test_aiweb_slice03_status_claim_scaffold.py /home/nic/forge")
        return 2

    repo = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(repo))

    from aiweb_status_claim_scaffold.claims import ClaimEvidence, ClaimRecord, validate_claim
    from aiweb_status_claim_scaffold.verify import sample_claim_checks_ok, vocabulary_shape_ok
    from aiweb_status_claim_scaffold.vocabulary import get_status_definition, list_status_keys

    passes = []
    failures = []

    def check(name: str, condition: bool) -> None:
        if condition:
            passes.append(name)
        else:
            failures.append(name)

    check("controlled status vocabulary is present", vocabulary_shape_ok())
    check("status keys are deterministic", tuple(sorted(list_status_keys())) == list_status_keys())
    check("production_ready definition requires production_readiness_decision",
          "production_readiness_decision" in get_status_definition("production_ready").required_evidence)

    accepted_evidence = ClaimEvidence(
        {
            "fresh_source_packet": True,
            "source_inspection": True,
            "patch_design": True,
            "backup": True,
            "installation_record": True,
            "changed_file_manifest": True,
            "tests_recorded": True,
            "tests_passed": True,
            "verifier_recorded": True,
            "verifiers_passed": True,
            "result_packet": True,
            "decision_record": True,
            "public_claim_boundary": True,
        }
    )

    valid_accepted = ClaimRecord(
        claimed_status="accepted_within_scope",
        claim_text="Slice accepted within scope only.",
        scope="Slice 3 behavior test",
        evidence=accepted_evidence,
        public_claim=True,
    )
    check("valid accepted-within-scope claim passes", validate_claim(valid_accepted).ok)

    missing_decision = ClaimRecord(
        claimed_status="accepted_within_scope",
        claim_text="Slice accepted within scope only.",
        scope="Slice 3 behavior test",
        evidence=ClaimEvidence({k: v for k, v in accepted_evidence.values.items() if k != "decision_record"}),
        public_claim=True,
    )
    check("accepted claim without decision record fails", not validate_claim(missing_decision).ok)

    bad_production = ClaimRecord(
        claimed_status="verified_within_scope",
        claim_text="This is production-ready.",
        scope="Slice 3 behavior test",
        evidence=ClaimEvidence({"verifier_recorded": True, "verifiers_passed": True}),
        production_claim=True,
    )
    check("production-ready overclaim fails", not validate_claim(bad_production).ok)

    valid_production = ClaimRecord(
        claimed_status="production_ready",
        claim_text="Production-ready by explicit decision.",
        scope="production readiness test scope",
        evidence=ClaimEvidence(
            {
                "production_readiness_decision": True,
                "release_decision": True,
                "result_packet": True,
                "decision_record": True,
                "public_claim_boundary": True,
            }
        ),
        production_claim=True,
        release_claim=True,
        public_claim=True,
    )
    check("production-ready with explicit decision passes", validate_claim(valid_production).ok)

    bad_gp014 = ClaimRecord(
        claimed_status="accepted_within_scope",
        claim_text="GP-014 is superseded.",
        scope="Slice 3 behavior test",
        evidence=accepted_evidence,
        authority_claims={"gp014_supersession_claim": True},
    )
    check("GP-014 supersession claim fails", not validate_claim(bad_gp014).ok)

    bad_public = ClaimRecord(
        claimed_status="verified_within_scope",
        claim_text="Verified within scope.",
        scope="Slice 3 behavior test",
        evidence=ClaimEvidence({"verifier_recorded": True, "verifiers_passed": True}),
        public_claim=True,
    )
    check("public claim without accepted/release status fails", not validate_claim(bad_public).ok)

    check("verifier sample checks pass", sample_claim_checks_ok())

    print("============================================================")
    print("AIWEB SLICE 3 STATUS CLAIM SCAFFOLD BEHAVIOR TEST")
    print("============================================================")
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")

    if failures:
        print("VERDICT: FAIL - behavior test failed within Slice 3 scope")
        return 1

    print("VERDICT: PASS - behavior test passed within Slice 3 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
