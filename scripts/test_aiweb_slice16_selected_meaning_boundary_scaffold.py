#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def _add_repo_to_path(repo: Path) -> None:
    text = str(repo)
    if text not in sys.path:
        sys.path.insert(0, text)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: test_aiweb_slice16_selected_meaning_boundary_scaffold.py /home/nic/forge")
        return 2
    repo = Path(sys.argv[1]).resolve()
    _add_repo_to_path(repo)

    from aiweb_selected_meaning_boundary_scaffold import (
        REQUIRED_PRIOR_BOUNDARIES,
        REQUIRED_SELECTION_LAWS,
        SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS,
        CandidateSelectionReferenceRecord,
        SelectionBasisRecord,
        SelectionConstraintRecord,
        SelectionReceiptRecord,
        SelectedMeaningStatusRecord,
        SelectionTraceRecord,
        demo_candidate_selection_reference_record,
        demo_non_selected_candidate_reference_record,
        demo_selection_basis_record,
        demo_selection_blocked_status_record,
        demo_selection_constraint_record,
        demo_selection_receipt_record,
        demo_selected_meaning_status_record,
        demo_selection_trace_record,
        selected_meaning_scope_record,
        validate_candidate_selection_reference_record,
        validate_selection_basis_record,
        validate_selection_constraint_record,
        validate_selection_receipt_record,
        validate_selected_meaning_status_record,
        validate_selection_trace_record,
    )
    from aiweb_selected_meaning_boundary_scaffold.verify import run_verification

    passes: list[str] = []
    failures: list[str] = []

    scope = selected_meaning_scope_record()
    scope_checks = (
        ("scope is scaffold-only", scope.get("scaffold_only") is True),
        ("scope has no runtime effect", scope.get("runtime_effect") == "none"),
        ("scope changes no dependency", scope.get("dependency_change") == "none"),
        ("scope represents selected meaning boundary", scope.get("represents_selected_meaning_boundary") is True),
        ("scope represents candidate selection reference", scope.get("represents_candidate_selection_reference") is True),
        ("scope represents selection basis reference", scope.get("represents_selection_basis_reference") is True),
        ("scope represents selection constraint reference", scope.get("represents_selection_constraint_reference") is True),
        ("scope represents selection trace reference", scope.get("represents_selection_trace_reference") is True),
        ("scope represents non-selected candidate reference", scope.get("represents_non_selected_candidate_reference") is True),
        ("scope represents selection confidence boundary", scope.get("represents_selection_confidence_boundary") is True),
        ("scope represents selection uncertainty boundary", scope.get("represents_selection_uncertainty_boundary") is True),
        ("scope represents selection refusal boundary", scope.get("represents_selection_refusal_boundary") is True),
        ("scope represents selection blocked boundary", scope.get("represents_selection_blocked_boundary") is True),
        ("scope represents selection receipt", scope.get("represents_selection_receipt") is True),
        ("scope carries required selection laws", tuple(scope.get("required_selection_laws", ())) == REQUIRED_SELECTION_LAWS),
        ("scope carries required prior boundaries", tuple(scope.get("required_prior_boundaries", ())) == REQUIRED_PRIOR_BOUNDARIES),
        ("GP-014 remains protected", scope.get("gp014_status") == "protected_not_superseded"),
        ("GP-015 remains failed", scope.get("gp015_status") == "failed_not_repaired"),
        ("GP-015R1 remains uninstalled", scope.get("gp015r1_status") == "uninstalled_not_live"),
        ("external resources remain unadmitted", scope.get("external_resource_status") == "unadmitted"),
    )
    for label, ok in scope_checks:
        (passes if ok else failures).append(label)

    for key in SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS:
        if scope.get(key) is False:
            passes.append(f"scope blocks {key}")
        else:
            failures.append(f"scope does not block {key}")

    for law in REQUIRED_SELECTION_LAWS:
        if law in scope.get("required_selection_laws", ()):
            passes.append(f"scope carries law {law}")
        else:
            failures.append(f"scope missing law {law}")

    record_checks = (
        ("candidate selection reference validates", validate_candidate_selection_reference_record(demo_candidate_selection_reference_record()).ok),
        ("non-selected candidate reference validates", validate_candidate_selection_reference_record(demo_non_selected_candidate_reference_record()).ok),
        ("selection basis validates", validate_selection_basis_record(demo_selection_basis_record()).ok),
        ("selection constraint validates", validate_selection_constraint_record(demo_selection_constraint_record()).ok),
        ("selected meaning status validates", validate_selected_meaning_status_record(demo_selected_meaning_status_record()).ok),
        ("selection blocked status validates", validate_selected_meaning_status_record(demo_selection_blocked_status_record()).ok),
        ("selection trace validates", validate_selection_trace_record(demo_selection_trace_record()).ok),
        ("selection receipt validates", validate_selection_receipt_record(demo_selection_receipt_record()).ok),
        ("candidate selection reference ID is stable", demo_candidate_selection_reference_record().selection_reference_id == demo_candidate_selection_reference_record().expected_id()),
        ("selection basis ID is stable", demo_selection_basis_record().selection_basis_id == demo_selection_basis_record().expected_id()),
        ("selection constraint ID is stable", demo_selection_constraint_record().selection_constraint_id == demo_selection_constraint_record().expected_id()),
        ("selected meaning status ID is stable", demo_selected_meaning_status_record().selected_meaning_id == demo_selected_meaning_status_record().expected_id()),
        ("selection trace ID is stable", demo_selection_trace_record().selection_trace_id == demo_selection_trace_record().expected_id()),
        ("selection receipt ID is stable", demo_selection_receipt_record().selection_receipt_id == demo_selection_receipt_record().expected_id()),
    )
    for label, ok in record_checks:
        (passes if ok else failures).append(label)

    rejection_checks = (
        ("selected meaning as truth rejected", not validate_selected_meaning_status_record(SelectedMeaningStatusRecord(**{**demo_selected_meaning_status_record().__dict__, "selection_as_truth": True})).ok),
        ("selected meaning as permission rejected", not validate_selected_meaning_status_record(SelectedMeaningStatusRecord(**{**demo_selected_meaning_status_record().__dict__, "selection_as_permission": True})).ok),
        ("selected meaning as delivery rejected", not validate_selection_receipt_record(SelectionReceiptRecord(**{**demo_selection_receipt_record().__dict__, "selection_as_delivery": True})).ok),
        ("selected meaning as execution rejected", not validate_selection_trace_record(SelectionTraceRecord(**{**demo_selection_trace_record().__dict__, "selection_as_execution": True})).ok),
        ("final meaning selection flag rejected", not validate_selected_meaning_status_record(SelectedMeaningStatusRecord(**{**demo_selected_meaning_status_record().__dict__, "final_meaning_selection": True})).ok),
        ("truth decision flag rejected", not validate_selection_receipt_record(SelectionReceiptRecord(**{**demo_selection_receipt_record().__dict__, "truth_decision": True})).ok),
        ("permission grant flag rejected", not validate_selection_receipt_record(SelectionReceiptRecord(**{**demo_selection_receipt_record().__dict__, "permission_grant": True})).ok),
        ("delivery action flag rejected", not validate_selection_receipt_record(SelectionReceiptRecord(**{**demo_selection_receipt_record().__dict__, "delivery_action": True})).ok),
        ("execution authority flag rejected", not validate_selection_receipt_record(SelectionReceiptRecord(**{**demo_selection_receipt_record().__dict__, "execution_authority": True})).ok),
        ("tool invocation flag rejected", not validate_candidate_selection_reference_record(CandidateSelectionReferenceRecord(**{**demo_candidate_selection_reference_record().__dict__, "tool_invocation": True})).ok),
        ("output rendering flag rejected", not validate_selected_meaning_status_record(SelectedMeaningStatusRecord(**{**demo_selected_meaning_status_record().__dict__, "output_rendering": True})).ok),
        ("memory write flag rejected", not validate_selected_meaning_status_record(SelectedMeaningStatusRecord(**{**demo_selected_meaning_status_record().__dict__, "memory_write": True})).ok),
        ("evidence validation flag rejected", not validate_selection_basis_record(SelectionBasisRecord(**{**demo_selection_basis_record().__dict__, "evidence_validation": True})).ok),
        ("external resource admission flag rejected", not validate_selection_constraint_record(SelectionConstraintRecord(**{**demo_selection_constraint_record().__dict__, "external_resource_admission": True})).ok),
        ("receipt delivery effect rejected", not validate_selection_receipt_record(SelectionReceiptRecord(**{**demo_selection_receipt_record().__dict__, "receipt_effect": "delivery_performed"})).ok),
        ("trace execution scope rejected", not validate_selection_trace_record(SelectionTraceRecord(**{**demo_selection_trace_record().__dict__, "trace_scope": "execution_trace"})).ok),
    )
    for label, ok in rejection_checks:
        (passes if ok else failures).append(label)

    verifier_passes, verifier_failures = run_verification(repo)
    if verifier_failures:
        failures.append("verifier sample checks failed")
        failures.extend(verifier_failures)
    else:
        passes.append("verifier sample checks pass")

    print("=" * 60)
    print("AIWEB SLICE 16 SELECTED MEANING BOUNDARY SCAFFOLD BEHAVIOR TEST")
    print("=" * 60)
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")

    if failures:
        print("VERDICT: FAIL - behavior test failed within Slice 16 scope")
        return 1
    print("VERDICT: PASS - behavior test passed within Slice 16 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
