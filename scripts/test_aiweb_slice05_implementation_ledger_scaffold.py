#!/usr/bin/env python3
"""
AIWEB Slice 5R1 behavior test.

Runs deterministic behavior checks for the Implementation Ledger continuity and
cycle update scaffold.
"""

from __future__ import annotations

import sys
from pathlib import Path

def main() -> int:
    repo = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    sys.path.insert(0, str(repo))

    from aiweb_implementation_ledger_scaffold import (
        build_cycle_update_record,
        build_ledger_continuity_record,
        unsafe_phrase,
        validate_cycle_update_record,
        validate_ledger_continuity_record,
    )

    passes = []
    failures = []

    def check(condition: bool, message: str) -> None:
        if condition:
            passes.append("PASS - " + message)
        else:
            failures.append("FAIL - " + message)

    ledger = build_ledger_continuity_record(
        ledger_name="AIWEB_IMPLEMENTATION_LEDGER_v1",
        cycle_id="AIWEB-SLICE-05R1",
        slice_id="SLICE-05R1",
        source_repo="/home/nic/forge",
        source_branch="main",
        source_commit="f4479882840935a5e916bcbec94e07f902b022e6",
        working_tree_status="clean",
        packet_identities=[
            "AIWEB_SLICE05_NARROW_SOURCE_AUTHORITY_PACKET_20260616_222506_UTC.tar.gz",
            "AIWEB_SLICE05R1_REPAIR_PATCH_DESIGN_RECORD_20260616_UTC.tar.gz",
        ],
        source_freshness="fresh_source_authority_packet_inspected",
        implementation_cycle_status="designed",
        inherited_tests=[
            "slice01_behavior_test",
            "slice02_behavior_test",
            "slice03_behavior_test",
            "slice04_behavior_test",
        ],
        inherited_verifiers=[
            "slice01_verifier",
            "slice02_verifier",
            "slice03_verifier",
            "slice04_verifier",
        ],
        notes="local scaffold only",
        created_utc="2026-06-16T00:00:00Z",
    )
    ok, _ = validate_ledger_continuity_record(ledger)
    check(ok, "valid ledger continuity record passes")

    check(ledger["updates_live_ledger"] is False, "ledger record does not update live ledger")
    check(ledger["writes_google_drive"] is False, "ledger record does not write Google Drive")
    check(ledger["claims_production_ready"] is False, "ledger record does not claim prod readiness")

    bad_ledger = dict(ledger)
    bad_ledger["working_tree_status"] = "dirty"
    ok, _ = validate_ledger_continuity_record(bad_ledger)
    check(not ok, "dirty working tree ledger record fails")

    bad_ledger = dict(ledger)
    bad_ledger["updates_live_ledger"] = True
    ok, _ = validate_ledger_continuity_record(bad_ledger)
    check(not ok, "live ledger write claim fails")

    bad_ledger = dict(ledger)
    bad_ledger["notes"] = unsafe_phrase("prod_dash_ready")
    ok, _ = validate_ledger_continuity_record(bad_ledger)
    check(not ok, "prod readiness phrase in ledger record fails")

    bad_ledger = dict(ledger)
    bad_ledger["notes"] = unsafe_phrase("gp014_dash_sup")
    ok, _ = validate_ledger_continuity_record(bad_ledger)
    check(not ok, "GP-014 supersession text fails")

    cycle = build_cycle_update_record(
        cycle_id="AIWEB-SLICE-05R1",
        cycle_title="Implementation Ledger Continuity and Cycle Update Scaffold Repair",
        slice_id="SLICE-05R1",
        slice_name="Implementation Ledger Continuity and Cycle Update Scaffold Repair",
        cycle_status="verified_passed",
        source_commit="f4479882840935a5e916bcbec94e07f902b022e6",
        source_branch="main",
        working_tree_status="clean",
        source_packet="AIWEB_SLICE05_NARROW_SOURCE_AUTHORITY_PACKET_20260616_222506_UTC.tar.gz",
        patch_design_record="AIWEB_SLICE05R1_REPAIR_PATCH_DESIGN_RECORD_20260616_UTC.tar.gz",
        patch_packet="AIWEB_SLICE05R1_IMPLEMENTATION_LEDGER_SCAFFOLD_REPAIR_PATCH_PACKET_20260616_UTC.tar.gz",
        result_packet="AIWEB_SLICE05R1_IMPLEMENTATION_LEDGER_SCAFFOLD_REPAIR_RESULT_PACKET_PENDING.tar.gz",
        result_packet_sha256="pending_after_install",
        verifier_outputs=["slice05r1_verifier_output.txt"],
        behavior_test_outputs=["slice05r1_behavior_test_output.txt"],
        created_utc="2026-06-16T00:00:00Z",
    )
    ok, _ = validate_cycle_update_record(cycle)
    check(ok, "valid cycle update record passes")

    check(cycle["decision_record_required"] is True, "cycle update requires decision record")
    check(cycle["accepted_baseline_update_required"] is True, "cycle update requires accepted baseline update")
    check(cycle["production_readiness_status"] == "not_production_ready", "cycle update keeps prod readiness blocked")
    check(cycle["release_status"] == "not_released", "cycle update remains not released")
    check(cycle["public_delivery_status"] == "not_authorized", "cycle update keeps public delivery blocked")

    bad_cycle = dict(cycle)
    bad_cycle["claims_production_ready"] = True
    ok, _ = validate_cycle_update_record(bad_cycle)
    check(not ok, "prod readiness cycle claim fails")

    bad_cycle = dict(cycle)
    bad_cycle["authorizes_release"] = True
    ok, _ = validate_cycle_update_record(bad_cycle)
    check(not ok, "release grant cycle claim fails")

    bad_cycle = dict(cycle)
    bad_cycle["notes"] = unsafe_phrase("gp015r1_dash_inst")
    ok, _ = validate_cycle_update_record(bad_cycle)
    check(not ok, "GP-015R1 install text fails")

    bad_cycle = dict(cycle)
    bad_cycle["notes"] = unsafe_phrase("llm_auth_on")
    ok, _ = validate_cycle_update_record(bad_cycle)
    check(not ok, "LLM authority text fails")

    bad_cycle = dict(cycle)
    bad_cycle["cycle_status"] = "done"
    ok, _ = validate_cycle_update_record(bad_cycle)
    check(not ok, "uncontrolled cycle status fails")

    print("============================================================")
    print("AIWEB SLICE 5R1 IMPLEMENTATION LEDGER SCAFFOLD BEHAVIOR TEST")
    print("============================================================")
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in passes:
        print("  " + item)
    print("FAILURES:")
    for item in failures:
        print("  " + item)

    if failures:
        print("VERDICT: FAIL - behavior test failed")
        return 1

    print("VERDICT: PASS - behavior test passed within Slice 5R1 scope")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
