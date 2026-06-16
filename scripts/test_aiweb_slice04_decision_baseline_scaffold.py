#!/usr/bin/env python3
"""Behavior test for AI.Web Slice 4 decision/baseline scaffold."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: test_aiweb_slice04_decision_baseline_scaffold.py /home/nic/forge")
        return 2

    repo = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(repo))

    from aiweb_decision_baseline_scaffold.baseline import (
        ACCEPTED_BASELINE_STATUS,
        build_accepted_baseline_update,
        sample_accepted_baseline_update,
        validate_accepted_baseline_update,
    )
    from aiweb_decision_baseline_scaffold.decision import (
        NON_PRODUCTION_READY,
        NON_RELEASE_AUTHORIZED,
        build_decision_record,
        sample_accepted_decision,
        validate_decision_record,
    )
    from aiweb_decision_baseline_scaffold.verify import scaffold_samples_ok

    passes = []
    failures = []

    def check(name: str, condition: bool) -> None:
        if condition:
            passes.append(name)
        else:
            failures.append(name)

    accepted = sample_accepted_decision()
    accepted_validation = validate_decision_record(accepted)
    check("valid accepted-within-scope decision record passes", accepted_validation.ok)

    held = build_decision_record(
        record_id="AIWEB-DECISION-HELD-BEHAVIOR",
        slice_id="4",
        slice_name="Decision Record and Accepted Baseline Update Scaffold",
        decision_status="held",
        decision_scope="behavior held scope",
        source_head=accepted.source_head,
        decision_owner_status="held",
        decision_reasons=("source evidence missing",),
    )
    check("valid held decision record passes", validate_decision_record(held).ok)

    rejected = build_decision_record(
        record_id="AIWEB-DECISION-REJECTED-BEHAVIOR",
        slice_id="4",
        slice_name="Decision Record and Accepted Baseline Update Scaffold",
        decision_status="rejected",
        decision_scope="behavior rejected scope",
        source_head=accepted.source_head,
        decision_owner_status="rejected",
        decision_reasons=("verifier failed",),
    )
    check("valid rejected decision record passes", validate_decision_record(rejected).ok)

    baseline = sample_accepted_baseline_update(accepted)
    baseline_validation = validate_accepted_baseline_update(baseline, accepted)
    check("valid accepted baseline update passes", baseline_validation.ok)
    check("explicit non-production-ready status passes", accepted.production_readiness_status == NON_PRODUCTION_READY and accepted_validation.ok)
    check("explicit non-release status passes", accepted.release_status == NON_RELEASE_AUTHORIZED and accepted_validation.ok)
    check("links to result packet/checksum/verifier evidence are preserved",
          baseline.result_packet == accepted.result_packet
          and baseline.result_packet_sha256 == accepted.result_packet_sha256
          and bool(accepted.verifier_output)
          and bool(accepted.behavior_test_output))
    check("baseline source commit and accepted scope fields are preserved",
          baseline.accepted_source_head == accepted.source_head and bool(baseline.accepted_scope))

    missing_result = build_decision_record(
        record_id="AIWEB-DECISION-BAD-MISSING-RESULT",
        slice_id="4",
        slice_name="Decision Record and Accepted Baseline Update Scaffold",
        decision_status="accepted_within_scope",
        decision_scope="bad behavior scope",
        source_head=accepted.source_head,
        result_packet="",
        result_packet_sha256=accepted.result_packet_sha256,
        inspection_record=accepted.inspection_record,
        verifier_output=accepted.verifier_output,
        behavior_test_output=accepted.behavior_test_output,
        decision_owner_status="accepted_within_scope",
        public_claim_boundary=True,
    )
    check("accepted decision without result packet fails", not validate_decision_record(missing_result).ok)

    missing_owner = build_decision_record(
        record_id="AIWEB-DECISION-BAD-MISSING-OWNER",
        slice_id="4",
        slice_name="Decision Record and Accepted Baseline Update Scaffold",
        decision_status="accepted_within_scope",
        decision_scope="bad behavior scope",
        source_head=accepted.source_head,
        result_packet=accepted.result_packet,
        result_packet_sha256=accepted.result_packet_sha256,
        inspection_record=accepted.inspection_record,
        verifier_output=accepted.verifier_output,
        behavior_test_output=accepted.behavior_test_output,
        decision_owner_status="",
        public_claim_boundary=True,
    )
    check("accepted decision without decision owner status fails", not validate_decision_record(missing_owner).ok)

    current_baseline = build_accepted_baseline_update(
        baseline_id="AIWEB-BASELINE-BAD-CURRENT-ONLY",
        implementation_line="Forge/RMC language-core implementation line",
        baseline_status="current_baseline",
        accepted_source_head=accepted.source_head,
        decision_record_id=accepted.record_id,
        result_packet=accepted.result_packet,
        result_packet_sha256=accepted.result_packet_sha256,
        accepted_scope="bad behavior scope",
        public_claim_boundary=True,
        next_allowed_gate="Slice 5 Narrow Source Authority Packet",
    )
    check("current baseline without accepted baseline update fails",
          not validate_accepted_baseline_update(current_baseline, accepted).ok)

    bad_production = build_decision_record(
        record_id="AIWEB-DECISION-BAD-PRODUCTION",
        slice_id="4",
        slice_name="Decision Record and Accepted Baseline Update Scaffold",
        decision_status="accepted_within_scope",
        decision_scope="bad behavior scope",
        source_head=accepted.source_head,
        result_packet=accepted.result_packet,
        result_packet_sha256=accepted.result_packet_sha256,
        inspection_record=accepted.inspection_record,
        verifier_output=accepted.verifier_output,
        behavior_test_output=accepted.behavior_test_output,
        decision_owner_status="accepted_within_scope",
        public_claim_boundary=True,
        production_readiness_status="production_ready",
    )
    check("production-ready claim without production readiness decision fails", not validate_decision_record(bad_production).ok)

    bad_release = build_decision_record(
        record_id="AIWEB-DECISION-BAD-RELEASE",
        slice_id="4",
        slice_name="Decision Record and Accepted Baseline Update Scaffold",
        decision_status="accepted_within_scope",
        decision_scope="bad behavior scope",
        source_head=accepted.source_head,
        result_packet=accepted.result_packet,
        result_packet_sha256=accepted.result_packet_sha256,
        inspection_record=accepted.inspection_record,
        verifier_output=accepted.verifier_output,
        behavior_test_output=accepted.behavior_test_output,
        decision_owner_status="accepted_within_scope",
        public_claim_boundary=True,
        release_status="release_authorized",
    )
    check("released/public delivery claim without release decision fails", not validate_decision_record(bad_release).ok)

    for label, key in (
        ("GP-014 supersession claim fails", "gp014_supersession_claim"),
        ("GP-014 replacement claim fails", "gp014_replacement_claim"),
        ("GP-015 repair claim fails", "gp015_repair_claim"),
        ("GP-015R1 install claim fails", "gp015r1_install_claim"),
        ("LLM/model/vector authority claim fails", "model_vector_llm_authority_claim"),
        ("memory/evidence/corpus/external-resource authority claim fails", "memory_authority_claim"),
        ("UI/delivery/action-routing authority claim fails", "ui_authority_claim"),
    ):
        bad = build_decision_record(
            record_id=f"AIWEB-DECISION-BAD-{key}",
            slice_id="4",
            slice_name="Decision Record and Accepted Baseline Update Scaffold",
            decision_status="accepted_within_scope",
            decision_scope="bad behavior scope",
            source_head=accepted.source_head,
            result_packet=accepted.result_packet,
            result_packet_sha256=accepted.result_packet_sha256,
            inspection_record=accepted.inspection_record,
            verifier_output=accepted.verifier_output,
            behavior_test_output=accepted.behavior_test_output,
            decision_owner_status="accepted_within_scope",
            public_claim_boundary=True,
            authority_claims={key: True},
        )
        check(label, not validate_decision_record(bad).ok)

    check("accepted baseline status constant is preserved", ACCEPTED_BASELINE_STATUS == "accepted_baseline_update")
    check("verifier sample checks pass", scaffold_samples_ok())

    print("============================================================")
    print("AIWEB SLICE 4 DECISION BASELINE SCAFFOLD BEHAVIOR TEST")
    print("============================================================")
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")

    if failures:
        print("VERDICT: FAIL - behavior test failed within Slice 4 scope")
        return 1

    print("VERDICT: PASS - behavior test passed within Slice 4 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
