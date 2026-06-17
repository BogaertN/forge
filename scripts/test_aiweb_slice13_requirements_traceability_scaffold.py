#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
sys.path.insert(0, str(REPO))

from aiweb_requirements_traceability_scaffold.accepted_scope import (
    AcceptedScopeRecord,
    RollbackTriggerRecord,
    demo_accepted_scope_record,
    demo_rollback_trigger_record,
    validate_accepted_scope_record,
    validate_rollback_trigger_record,
)
from aiweb_requirements_traceability_scaffold.core import requirements_traceability_scope_record
from aiweb_requirements_traceability_scaffold.crosswalk import (
    RequirementTestCrosswalkRecord,
    demo_requirement_test_crosswalk_record,
    validate_requirement_test_crosswalk_record,
)
from aiweb_requirements_traceability_scaffold.receipt import (
    TraceabilityReceiptRecord,
    demo_traceability_receipt_record,
    validate_traceability_receipt_record,
)
from aiweb_requirements_traceability_scaffold.requirement import (
    RequirementIdentityRecord,
    demo_requirement_identity_record,
    validate_requirement_identity_record,
)
from aiweb_requirements_traceability_scaffold.verify import run_verification

passes: list[str] = []
failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if condition:
        passes.append(message)
    else:
        failures.append(message)


scope = requirements_traceability_scope_record()
check(scope["status"] == "requirements_traceability_scaffold_only", "scope is scaffold-only")
check(scope["runtime_effect"] == "none", "scope has no runtime effect")
check(scope["dependency_change"] == "none", "scope changes no dependency")
for key in (
    "represents_requirement_identities",
    "represents_requirement_to_test_crosswalks",
    "represents_test_class_mappings",
    "represents_verifier_gate_references",
    "represents_evidence_receipt_references",
    "represents_rollback_trigger_references",
    "represents_accepted_scope_records",
    "represents_result_packet_references",
    "represents_decision_record_references",
    "represents_implementation_slice_traceability_status",
    "preserves_prior_accepted_scope_boundaries",
):
    check(scope.get(key) is True, f"scope represents {key}")
for key in (
    "live_runtime_behavior",
    "capability_acceptance",
    "verifier_gate_replacement",
    "result_packet_bypass",
    "accepted_scope_widening",
    "release_authority",
    "production_readiness",
    "delivery_action",
    "action_authorization",
    "tool_invocation",
    "capability_route",
    "memory_write",
    "evidence_validation",
    "external_resource_admission",
    "final_meaning_selection",
    "selected_meaning",
    "truth_decision",
    "live_clarification",
    "user_facing_question_emission",
    "gp014_supersession",
    "gp015_repair",
    "gp015r1_installation",
    "model_authority",
    "vector_authority",
    "retrieval_authority",
):
    check(scope.get(key) is False, f"scope blocks {key}")
check(scope["gp014_status"] == "protected_not_superseded", "GP-014 remains protected")
check(scope["gp015_status"] == "failed_not_repaired", "GP-015 remains failed")
check(scope["gp015r1_status"] == "uninstalled_not_live", "GP-015R1 remains uninstalled")
check(scope["sanskrit_wordnet_status"] == "hold_unadmitted", "Sanskrit WordNet remains hold/unadmitted")

record_checks = (
    ("requirement identity validates", validate_requirement_identity_record(demo_requirement_identity_record()).ok),
    ("requirement-to-test crosswalk validates", validate_requirement_test_crosswalk_record(demo_requirement_test_crosswalk_record()).ok),
    ("traceability receipt validates", validate_traceability_receipt_record(demo_traceability_receipt_record()).ok),
    ("accepted scope validates", validate_accepted_scope_record(demo_accepted_scope_record()).ok),
    ("rollback trigger validates", validate_rollback_trigger_record(demo_rollback_trigger_record()).ok),
    ("requirement ID is stable", demo_requirement_identity_record().requirement_identity_id == demo_requirement_identity_record().expected_id()),
    ("crosswalk ID is stable", demo_requirement_test_crosswalk_record().crosswalk_id == demo_requirement_test_crosswalk_record().expected_id()),
    ("receipt ID is stable", demo_traceability_receipt_record().receipt_id == demo_traceability_receipt_record().expected_id()),
    ("accepted scope ID is stable", demo_accepted_scope_record().accepted_scope_id == demo_accepted_scope_record().expected_id()),
    ("rollback trigger ID is stable", demo_rollback_trigger_record().rollback_trigger_id == demo_rollback_trigger_record().expected_id()),
)
for label, ok in record_checks:
    check(ok, label)

unsafe_flags = (
    "live_runtime_behavior",
    "capability_acceptance",
    "verifier_gate_replacement",
    "result_packet_bypass",
    "accepted_scope_widening",
    "release_authority",
    "production_readiness",
    "delivery_action",
    "action_authorization",
    "tool_invocation",
    "capability_route",
    "memory_write",
    "evidence_validation",
    "external_resource_admission",
    "final_meaning_selection",
    "selected_meaning",
    "truth_decision",
    "live_clarification",
    "user_facing_question_emission",
    "gp014_supersession",
    "gp015_repair",
    "gp015r1_installation",
    "model_authority",
    "vector_authority",
    "retrieval_authority",
)
for field in unsafe_flags:
    record = RequirementIdentityRecord(**{**demo_requirement_identity_record().__dict__, field: True})
    check(not validate_requirement_identity_record(record).ok, f"requirement unsafe flag rejected: {field}")

for field in ("verifier_gate_replacement", "result_packet_bypass", "capability_acceptance"):
    record = RequirementTestCrosswalkRecord(**{**demo_requirement_test_crosswalk_record().__dict__, field: True})
    check(not validate_requirement_test_crosswalk_record(record).ok, f"crosswalk unsafe flag rejected: {field}")

for field in ("result_packet_bypass", "evidence_validation", "capability_acceptance", "accepted_scope_widening"):
    record = TraceabilityReceiptRecord(**{**demo_traceability_receipt_record().__dict__, field: True})
    check(not validate_traceability_receipt_record(record).ok, f"receipt unsafe flag rejected: {field}")

for field in ("accepted_scope_widening", "release_authority", "production_readiness", "capability_acceptance"):
    record = AcceptedScopeRecord(**{**demo_accepted_scope_record().__dict__, field: True})
    check(not validate_accepted_scope_record(record).ok, f"accepted scope unsafe flag rejected: {field}")

for field in ("release_authority", "tool_invocation", "memory_write", "external_resource_admission"):
    record = RollbackTriggerRecord(**{**demo_rollback_trigger_record().__dict__, field: True})
    check(not validate_rollback_trigger_record(record).ok, f"rollback unsafe flag rejected: {field}")

bad_crosswalk = RequirementTestCrosswalkRecord(**{**demo_requirement_test_crosswalk_record().__dict__, "test_class_refs": ("behavior_test", "unsupported_test_class")})
check(not validate_requirement_test_crosswalk_record(bad_crosswalk).ok, "unsupported test class rejected")
bad_receipt = TraceabilityReceiptRecord(**{**demo_traceability_receipt_record().__dict__, "result_packet_ref": ""})
check(not validate_traceability_receipt_record(bad_receipt).ok, "receipt cannot omit result packet reference")
bad_scope = AcceptedScopeRecord(**{**demo_accepted_scope_record().__dict__, "blocked_scope_items": ()})
check(not validate_accepted_scope_record(bad_scope).ok, "accepted scope cannot omit blocked-scope items")
bad_rollback = RollbackTriggerRecord(**{**demo_rollback_trigger_record().__dict__, "trigger_conditions": ()})
check(not validate_rollback_trigger_record(bad_rollback).ok, "rollback trigger cannot omit trigger conditions")

verify_passes, verify_failures = run_verification(REPO)
check(not verify_failures, "verifier sample checks pass")

print("=" * 60)
print("AIWEB SLICE 13 REQUIREMENTS-TO-TEST TRACEABILITY SCAFFOLD BEHAVIOR TEST")
print("=" * 60)
print(f"Target repo: {REPO}")
print("PASSES:")
for item in passes:
    print(f"  PASS - {item}")
print("FAILURES:")
for item in failures:
    print(f"  FAIL - {item}")
if failures:
    print("VERDICT: FAIL - behavior test failed within Slice 13 scope")
    sys.exit(1)
print("VERDICT: PASS - behavior test passed within Slice 13 scope")
