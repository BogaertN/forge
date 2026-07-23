#!/usr/bin/env python3
"""Behavior test for Slice 47 GP-014 status decision and Phase D closeout."""
from __future__ import annotations
import argparse
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import sys

GP014_MODULES = (
    "rmc_engine_v1.general_pipeline.gp014_operator_guided_language_realizer",
    "rmc_engine_v1.general_pipeline.symbolic_math_language_vertical_slice",
    "rmc_engine_v1.general_pipeline.symbolic_math_operator_language_realizer",
)

class Ledger:
    def __init__(self) -> None:
        self.checks = 0
        self.failures: list[str] = []
    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            self.failures.append(label)
            print("FAIL: " + label)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_manifest(path: Path) -> tuple[tuple[str, str], ...]:
    rows: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        digest, relative = line.split("  ", 1)
        rows.append((digest, relative))
    return tuple(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    sys.path.insert(0, str(repo))
    ledger = Ledger()

    loaded_before = {name: name in sys.modules for name in GP014_MODULES}
    from aiweb_language_core_bootstrap.gp014_status_decision import (
        LAWFUL_STATUS_OUTCOMES, NEXT_LAWFUL_SLICE, SELECTED_STATUS_OUTCOME,
        build_slice47_decision_bundle, validate_bundle, validate_decision,
        validate_receipt, validate_closeout,
    )
    loaded_after = {name: name in sys.modules for name in GP014_MODULES}

    ledger.check(not any(loaded_before.values()), "GP-014 not loaded before Slice 47 import")
    ledger.check(not any(loaded_after.values()), "GP-014 not loaded by Slice 47 import")

    first = build_slice47_decision_bundle()
    second = build_slice47_decision_bundle()
    third = build_slice47_decision_bundle()
    ledger.check(first == second == third, "deterministic repeated bundle")
    ledger.check(first.bundle_id == first.expected_id(), "bundle identity")
    ledger.check(first.decision.decision_id == first.decision.expected_id(), "decision identity")
    ledger.check(first.receipt.receipt_id == first.receipt.expected_id(), "receipt identity")
    ledger.check(first.closeout.closeout_id == first.closeout.expected_id(), "closeout identity")
    ledger.check(validate_bundle(first).ok, "complete bundle validation")
    ledger.check(validate_decision(first.decision).ok, "decision validation")
    ledger.check(validate_receipt(first.receipt).ok, "receipt validation")
    ledger.check(validate_closeout(first.closeout).ok, "closeout validation")

    decision = first.decision
    ledger.check(SELECTED_STATUS_OUTCOME == "preserved_as_unchanged_bounded_lane", "single selected status")
    ledger.check(decision.selected_outcome == SELECTED_STATUS_OUTCOME, "record selected status")
    ledger.check(decision.lawful_outcomes == LAWFUL_STATUS_OUTCOMES, "five lawful outcomes recorded")
    ledger.check(len(decision.lawful_outcomes) == 5, "lawful outcome count")
    ledger.check(len(decision.rejected_outcomes) == 4, "rejected outcome count")
    ledger.check(set(decision.rejected_outcomes) == set(decision.lawful_outcomes) - {decision.selected_outcome}, "all non-selected outcomes rejected")
    ledger.check(decision.source_unchanged, "GP-014 source unchanged")
    ledger.check(decision.bounded_lane_preserved, "bounded lane preserved")
    ledger.check(decision.protected, "GP-014 protected")
    ledger.check(decision.adapter_exists, "separate adapter exists")
    ledger.check(not decision.adapter_is_general_interface, "adapter is not general interface")
    ledger.check(not decision.adapter_registered, "adapter remains unregistered")
    ledger.check(decision.equivalence_proof_accepted, "Slice 46 equivalence accepted")
    ledger.check(not decision.refactor_accepted, "refactor not accepted")
    ledger.check(not decision.replacement_accepted, "replacement not accepted")
    ledger.check(not decision.supersession_accepted, "supersession not accepted")
    ledger.check(not decision.gp014_modified, "GP-014 not modified")
    ledger.check(not decision.gp014_refactored, "GP-014 not refactored")
    ledger.check(not decision.gp014_replaced, "GP-014 not replaced")
    ledger.check(not decision.gp014_superseded, "GP-014 not superseded")
    ledger.check(not decision.gp015_used, "GP-015 not used")
    ledger.check(len(decision.evidence_references) == 4, "four exact evidence references")
    ledger.check(all(item.accepted for item in decision.evidence_references), "all evidence references accepted")

    receipt = first.receipt
    ledger.check(receipt.slice46_behavior_checks == 500 and receipt.slice46_behavior_failures == 0, "accepted Slice 46 behavior 500 of 500")
    ledger.check(receipt.slice46_verifier_checks == 3648 and receipt.slice46_verifier_failures == 0, "accepted Slice 46 verifier 3648 of 3648")
    ledger.check(receipt.exact_predecessor_files_protected == 59, "59 exact predecessor files protected")
    ledger.check(not receipt.staging_performed and not receipt.commit_performed, "receipt grants no staging or commit")

    closeout = first.closeout
    ledger.check(closeout.phase_d_complete, "Phase D complete")
    ledger.check(closeout.gp014_preserved and closeout.gp014_protected, "Phase D preserves and protects GP-014")
    ledger.check(not closeout.gp014_superseded, "Phase D does not supersede GP-014")
    ledger.check(closeout.next_lawful_slice == NEXT_LAWFUL_SLICE, "next lawful slice is Slice 48")
    ledger.check(not closeout.runtime_activation_authorized, "runtime activation not authorized")
    ledger.check(not closeout.route_or_api_authorized, "route and API not authorized")
    ledger.check(not closeout.production_ready and not closeout.release_authorized, "production and release not authorized")

    authority_fields = (
        "general_language_authority", "concept_authority", "predicate_authority",
        "selected_meaning_authority", "truth_authority", "evidence_authority",
        "permission_authority", "route_authority", "api_authority", "ui_authority",
        "network_authority", "filesystem_write_authority", "memory_authority",
        "resource_authority", "tool_authority", "action_authority",
        "delivery_authority", "release_authority", "production_authority",
    )
    for field in authority_fields:
        ledger.check(getattr(decision, field) is False, "authority remains false: " + field)

    malformed = (
        replace(decision, selected_outcome="wrapped_behind_general_interface"),
        replace(decision, lawful_outcomes=(decision.selected_outcome,)),
        replace(decision, rejected_outcomes=()),
        replace(decision, source_unchanged=False),
        replace(decision, bounded_lane_preserved=False),
        replace(decision, protected=False),
        replace(decision, adapter_is_general_interface=True),
        replace(decision, adapter_registered=True),
        replace(decision, refactor_accepted=True),
        replace(decision, replacement_accepted=True),
        replace(decision, supersession_accepted=True),
        replace(decision, gp014_modified=True),
        replace(decision, gp014_refactored=True),
        replace(decision, gp014_replaced=True),
        replace(decision, gp014_superseded=True),
        replace(decision, general_language_authority=True),
    )
    for index, bad in enumerate(malformed, start=1):
        ledger.check(not validate_decision(bad).ok, f"malformed decision rejected {index}")

    manifest = parse_manifest(repo / "scripts/AIWEB_SLICE47_PROTECTED_PREDECESSOR_SHA256SUMS.txt")
    ledger.check(len(manifest) == 59, "protected predecessor manifest count")
    for digest, relative in manifest:
        target = repo / relative
        ledger.check(target.is_file(), "protected predecessor exists: " + relative)
        if target.is_file():
            ledger.check(sha256_file(target) == digest, "protected predecessor hash: " + relative)

    output = os.environ.get("AIWEB_SLICE47_STATUS_OUTPUT")
    if output:
        Path(output).write_text(json.dumps(first.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("=== AI.WEB SLICE 47 STATUS DECISION SUMMARY ===")
    print("check_count=" + str(ledger.checks))
    print("failure_count=" + str(len(ledger.failures)))
    print("selected_outcome=" + decision.selected_outcome)
    print("lawful_outcome_count=" + str(len(decision.lawful_outcomes)))
    print("rejected_outcome_count=" + str(len(decision.rejected_outcomes)))
    print("evidence_reference_count=" + str(len(decision.evidence_references)))
    print("protected_predecessor_files=" + str(len(manifest)))
    print("gp014_source_unchanged=1")
    print("gp014_bounded_lane_preserved=1")
    print("gp014_adapter_exists=1")
    print("gp014_adapter_general_interface=0")
    print("gp014_refactored=0")
    print("gp014_replaced=0")
    print("gp014_superseded=0")
    print("phase_d_complete=1")
    print("next_lawful_slice=48")
    print("runtime_route_api_authority=0")
    print("memory_resource_tool_action_delivery_authority=0")
    print("production_release_authority=0")
    print("AI.WEB SLICE 47 BEHAVIOR TEST: " + ("PASS" if not ledger.failures else "FAIL"))
    return 0 if not ledger.failures else 1

if __name__ == "__main__":
    raise SystemExit(main())
