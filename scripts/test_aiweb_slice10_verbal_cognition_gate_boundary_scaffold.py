#!/usr/bin/env python3
"""Behavior test for Slice 10 verbal cognition gate boundary scaffold."""

from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
sys.path.insert(0, str(REPO))

from aiweb_verbal_cognition_gate_boundary_scaffold import (
    ExpectancyBoundaryRecord,
    GateBoundaryRecord,
    GateOutcomeBoundaryRecord,
    GateStateBoundaryRecord,
    demo_ambiguity_state_record,
    demo_blocked_action_outcome_record,
    demo_blocked_action_state_record,
    demo_clarification_required_outcome_record,
    demo_clarification_required_state_record,
    demo_connectedness_record,
    demo_congruity_record,
    demo_deferred_state_record,
    demo_expectancy_record,
    demo_gate_boundary_record,
    demo_gate_outcome_record,
    demo_recoverable_purpose_record,
    demo_unknown_expectancy_record,
    demo_unknown_gate_boundary_record,
    demo_unknown_gate_outcome_record,
    demo_unsupported_state_record,
    validate_expectancy_record,
    validate_gate_boundary_record,
    validate_gate_outcome_record,
    validate_gate_state_record,
    verbal_cognition_gate_scope_record,
)
from aiweb_verbal_cognition_gate_boundary_scaffold.verify import run_verification

print("=" * 60)
print("AIWEB SLICE 10 VERBAL COGNITION GATE BOUNDARY SCAFFOLD BEHAVIOR TEST")
print("=" * 60)
print(f"Target repo: {REPO}")

passes = []
failures = []


def check(condition: bool, message: str) -> None:
    (passes if condition else failures).append(message)


scope = verbal_cognition_gate_scope_record()
check(scope["status"] == "verbal_cognition_gate_boundary_scaffold_only", "scope is scaffold-only")
check(scope["runtime_effect"] == "none", "scope has no runtime effect")
check(scope["dependency_change"] == "none", "scope changes no dependency")
check(scope["gate_identity_representation"] is True, "scope represents gate identity")
check(scope["gate_input_representation"] is True, "scope represents gate input")
check(scope["gate_outcome_representation"] is True, "scope represents gate outcome")

for key in (
    "live_gate_evaluation",
    "gate_resolution",
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

check(scope["sanskrit_wordnet_status"] == "hold_unadmitted", "Sanskrit WordNet remains hold/unadmitted")
check(scope["gp014_status"] == "protected_prior_scope", "GP-014 remains protected")
check(scope["gp015_status"] == "failed_not_repaired", "GP-015 remains failed")
check(scope["gp015r1_status"] == "not_installed", "GP-015R1 remains uninstalled")

gate = demo_gate_boundary_record()
unknown_gate = demo_unknown_gate_boundary_record()
outcome = demo_gate_outcome_record()
clarification = demo_clarification_required_outcome_record()
blocked_outcome = demo_blocked_action_outcome_record()
unknown_outcome = demo_unknown_gate_outcome_record()
expectancy = demo_expectancy_record()
congruity = demo_congruity_record()
connectedness = demo_connectedness_record()
recoverable = demo_recoverable_purpose_record()
unknown_expectancy = demo_unknown_expectancy_record()
ambiguity_state = demo_ambiguity_state_record()
clarification_state = demo_clarification_required_state_record()
unsupported_state = demo_unsupported_state_record()
blocked_state = demo_blocked_action_state_record()
deferred_state = demo_deferred_state_record()

check(validate_gate_boundary_record(gate).passed, "gate boundary validates")
check(validate_gate_boundary_record(unknown_gate).passed, "unknown gate boundary validates")
check(unknown_gate.unknown_state == "unknown_boundary", "unknown gate remains unknown")

check(validate_gate_outcome_record(outcome).passed, "gate outcome validates")
check(validate_gate_outcome_record(clarification).passed, "clarification outcome validates")
check(validate_gate_outcome_record(blocked_outcome).passed, "blocked action outcome validates")
check(validate_gate_outcome_record(unknown_outcome).passed, "unknown outcome validates")

check(validate_expectancy_record(expectancy).passed, "expectancy boundary validates")
check(validate_expectancy_record(congruity).passed, "congruity boundary validates")
check(validate_expectancy_record(connectedness).passed, "connectedness boundary validates")
check(validate_expectancy_record(recoverable).passed, "recoverable purpose boundary validates")
check(validate_expectancy_record(unknown_expectancy).passed, "unknown expectancy validates")

check(validate_gate_state_record(ambiguity_state).passed, "ambiguity state validates")
check(validate_gate_state_record(clarification_state).passed, "clarification-required state validates")
check(validate_gate_state_record(unsupported_state).passed, "unsupported state validates")
check(validate_gate_state_record(blocked_state).passed, "blocked-action state validates")
check(validate_gate_state_record(deferred_state).passed, "deferred state validates")

check(gate.boundary_id() == demo_gate_boundary_record().boundary_id(), "gate ID is stable")
check(outcome.boundary_id() == demo_gate_outcome_record().boundary_id(), "outcome ID is stable")
check(expectancy.boundary_id() == demo_expectancy_record().boundary_id(), "expectancy ID is stable")
check(ambiguity_state.boundary_id() == demo_ambiguity_state_record().boundary_id(), "state ID is stable")

for field_name in (
    "live_gate_evaluation",
    "gate_resolution",
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
    unsafe = GateBoundaryRecord(
        gate_key=f"unsafe_{field_name}",
        gate_type="verbal_cognition_gate_boundary",
        gate_stage="pre_selection_boundary",
        namespace="aiweb:core",
        gate_input_refs=("unsafe_input",),
        predicate_frame_refs=("unsafe_predicate",),
        concept_boundary_refs=("unsafe_concept",),
        provenance_tag="slice10_negative",
        version_tag="v1",
        **{field_name: True},
    )
    check(not validate_gate_boundary_record(unsafe).passed, f"gate unsafe flag rejected: {field_name}")

unsafe_outcome_cases = (
    ("selected_meaning", "selected meaning remains blocked"),
    ("truth_decision", "truth decision remains blocked"),
    ("permission_grant", "permission grant remains blocked"),
    ("action_authorization", "action flag remains blocked"),
    ("tool_invocation", "tool flag remains blocked"),
    ("delivery_action", "delivery step remains blocked"),
    ("memory_write", "memory write remains blocked"),
    ("evidence_validation", "evidence validation remains blocked"),
    ("external_resource_admission", "external resource admission remains blocked"),
)
for field_name, label in unsafe_outcome_cases:
    unsafe = GateOutcomeBoundaryRecord(
        outcome_key=f"unsafe_{field_name}",
        gate_key="unsafe_gate",
        outcome_type="recognized_boundary",
        namespace="aiweb:core",
        reason_boundary_refs=("unsafe_reason",),
        required_next_boundary="unsafe_next",
        provenance_tag="slice10_negative",
        version_tag="v1",
        **{field_name: True},
    )
    check(not validate_gate_outcome_record(unsafe).passed, f"outcome unsafe flag rejected: {label}")

unsafe_expectancy = ExpectancyBoundaryRecord(
    expectancy_key="unsafe_expectancy_decision",
    gate_key="unsafe_gate",
    expectancy_type="expectancy_present_boundary",
    namespace="aiweb:core",
    input_boundary_refs=("unsafe_input",),
    reason_boundary_refs=("unsafe_reason",),
    provenance_tag="slice10_negative",
    version_tag="v1",
    expectancy_decision=True,
)
check(not validate_expectancy_record(unsafe_expectancy).passed, "expectancy decision flag is rejected")

unsafe_state = GateStateBoundaryRecord(
    state_key="unsafe_state_resolution",
    gate_key="unsafe_gate",
    state_type="ambiguity_state_boundary",
    namespace="aiweb:core",
    severity_boundary="requires_future_boundary",
    reason_boundary_refs=("unsafe_reason",),
    required_future_boundary="unsafe_future",
    provenance_tag="slice10_negative",
    version_tag="v1",
    state_resolution=True,
)
check(not validate_gate_state_record(unsafe_state).passed, "state resolution flag is rejected")

verifier_passes, verifier_failures = run_verification(REPO)
check(not verifier_failures, "verifier sample checks pass")

print("PASSES:")
for item in passes:
    print(f"  PASS - {item}")
print("FAILURES:")
for item in failures:
    print(f"  FAIL - {item}")
if failures:
    print("VERDICT: FAIL - behavior test failed")
    raise SystemExit(1)
print("VERDICT: PASS - behavior test passed within Slice 10 scope")
