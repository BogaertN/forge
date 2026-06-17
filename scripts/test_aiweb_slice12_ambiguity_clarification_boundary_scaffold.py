#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
sys.path.insert(0, str(REPO))

from aiweb_ambiguity_clarification_boundary_scaffold.clarification import (
    ClarificationRequirementBoundaryRecord,
    demo_clarification_blocked_record,
    demo_clarification_required_record,
    validate_clarification_requirement_record,
)
from aiweb_ambiguity_clarification_boundary_scaffold.state_boundary import (
    AmbiguityStateBoundaryRecord,
    ambiguity_clarification_scope_record,
    demo_ambiguity_state_record,
    demo_deferred_state_record,
    demo_unknown_state_record,
    demo_unsupported_state_record,
    validate_state_boundary_record,
)
from aiweb_ambiguity_clarification_boundary_scaffold.trace_state import (
    StateTraceBoundaryRecord,
    demo_state_trace_record,
    validate_state_trace_record,
)
from aiweb_ambiguity_clarification_boundary_scaffold.unknown_support import (
    UnknownSupportBoundaryRecord,
    demo_unknown_concept_record,
    demo_unsupported_resource_record,
    validate_unknown_support_record,
)
from aiweb_ambiguity_clarification_boundary_scaffold.verify import run_verification

passes: list[str] = []
failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if condition:
        passes.append(message)
    else:
        failures.append(message)

scope = ambiguity_clarification_scope_record()
check(scope["status"] == "ambiguity_clarification_boundary_scaffold_only", "scope is scaffold-only")
check(scope["runtime_effect"] == "none", "scope has no runtime effect")
check(scope["dependency_change"] == "none", "scope changes no dependency")
for key in (
    "represents_ambiguity",
    "represents_unknown",
    "represents_unsupported",
    "represents_clarification_required",
    "represents_incongruent",
    "represents_understood_but_blocked",
    "represents_deferred",
    "represents_no_action_safe_termination",
    "preserves_uncertainty_without_guessing",
    "references_slice10_gate_boundaries_only",
    "references_slice11_candidate_boundaries_only",
):
    check(scope.get(key) is True, f"scope represents {key}")
for key in (
    "live_runtime_interpretation",
    "live_clarification",
    "user_facing_question_emission",
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
    check(scope.get(key) is False, f"scope blocks {key}")
check(scope["gp014_status"] == "protected_not_superseded", "GP-014 remains protected")
check(scope["gp015_status"] == "failed_not_repaired", "GP-015 remains failed")
check(scope["gp015r1_status"] == "uninstalled_not_live", "GP-015R1 remains uninstalled")
check(scope["sanskrit_wordnet_status"] == "hold_unadmitted", "Sanskrit WordNet remains hold/unadmitted")

state_records = (
    ("ambiguity state validates", demo_ambiguity_state_record()),
    ("unknown state validates", demo_unknown_state_record()),
    ("unsupported state validates", demo_unsupported_state_record()),
    ("deferred state validates", demo_deferred_state_record()),
)
for label, record in state_records:
    check(validate_state_boundary_record(record).ok, label)

clarification_records = (
    ("clarification-required boundary validates", demo_clarification_required_record()),
    ("clarification-blocked boundary validates", demo_clarification_blocked_record()),
)
for label, record in clarification_records:
    check(validate_clarification_requirement_record(record).ok, label)

unknown_records = (
    ("unknown concept boundary validates", demo_unknown_concept_record()),
    ("unsupported resource boundary validates", demo_unsupported_resource_record()),
)
for label, record in unknown_records:
    check(validate_unknown_support_record(record).ok, label)

trace_record = demo_state_trace_record()
check(validate_state_trace_record(trace_record).ok, "state trace boundary validates")

check(demo_ambiguity_state_record().state_boundary_id == demo_ambiguity_state_record().expected_id(), "state ID is stable")
check(demo_clarification_required_record().clarification_boundary_id == demo_clarification_required_record().expected_id(), "clarification ID is stable")
check(demo_unknown_concept_record().unknown_boundary_id == demo_unknown_concept_record().expected_id(), "unknown-support ID is stable")
check(demo_state_trace_record().trace_state_id == demo_state_trace_record().expected_id(), "trace-state ID is stable")

unsafe_state_flags = (
    "live_runtime_interpretation",
    "live_clarification",
    "user_facing_question_emission",
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
for field in unsafe_state_flags:
    record = AmbiguityStateBoundaryRecord(**{**demo_ambiguity_state_record().__dict__, field: True})
    check(not validate_state_boundary_record(record).ok, f"state unsafe flag rejected: {field}")

unsafe_clarification_flags = (
    "live_clarification",
    "user_facing_question_emission",
    "clarification_bypasses_external_authority",
    "memory_write",
    "delivery_action",
    "tool_invocation",
    "action_authorization",
    "evidence_validation",
    "external_resource_admission",
    "selected_meaning",
    "truth_decision",
)
for field in unsafe_clarification_flags:
    record = ClarificationRequirementBoundaryRecord(**{**demo_clarification_required_record().__dict__, field: True})
    check(not validate_clarification_requirement_record(record).ok, f"clarification unsafe flag rejected: {field}")

unsafe_unknown_flags = (
    "guess_substitution",
    "silent_repair",
    "external_resource_admission",
    "concept_resolution",
    "role_resolution",
    "gate_resolution",
    "selected_meaning",
    "truth_decision",
    "tool_invocation",
    "action_authorization",
    "memory_write",
    "evidence_validation",
)
for field in unsafe_unknown_flags:
    record = UnknownSupportBoundaryRecord(**{**demo_unknown_concept_record().__dict__, field: True})
    check(not validate_unknown_support_record(record).ok, f"unknown unsafe flag rejected: {field}")

unsafe_trace_flags = (
    "evidence_validation",
    "memory_write",
    "delivery_action",
    "external_resource_admission",
    "implementation_action",
    "selected_meaning",
    "truth_decision",
)
for field in unsafe_trace_flags:
    record = StateTraceBoundaryRecord(**{**demo_state_trace_record().__dict__, field: True})
    check(not validate_state_trace_record(record).ok, f"trace unsafe flag rejected: {field}")

bad_state = AmbiguityStateBoundaryRecord(**{**demo_ambiguity_state_record().__dict__, "uncertainty_preserved": False})
check(not validate_state_boundary_record(bad_state).ok, "state cannot clear uncertainty preservation")
bad_unknown = UnknownSupportBoundaryRecord(**{**demo_unknown_concept_record().__dict__, "no_guess": False})
check(not validate_unknown_support_record(bad_unknown).ok, "unknown cannot disable no-guess rule")
bad_clarification = ClarificationRequirementBoundaryRecord(**{**demo_clarification_required_record().__dict__, "trace_required": False})
check(not validate_clarification_requirement_record(bad_clarification).ok, "clarification cannot disable trace requirement")
bad_trace = StateTraceBoundaryRecord(**{**demo_state_trace_record().__dict__, "trace_integrity_required": False})
check(not validate_state_trace_record(bad_trace).ok, "trace cannot disable integrity requirement")

verify_passes, verify_failures = run_verification(REPO)
check(not verify_failures, "verifier sample checks pass")

print("=" * 60)
print("AIWEB SLICE 12 AMBIGUITY / UNKNOWN / CLARIFICATION BOUNDARY SCAFFOLD BEHAVIOR TEST")
print("=" * 60)
print(f"Target repo: {REPO}")
print("PASSES:")
for item in passes:
    print(f"  PASS - {item}")
print("FAILURES:")
for item in failures:
    print(f"  FAIL - {item}")
if failures:
    print("VERDICT: FAIL - behavior test failed within Slice 12 scope")
    sys.exit(1)
print("VERDICT: PASS - behavior test passed within Slice 12 scope")
