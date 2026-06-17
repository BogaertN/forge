"""Slice 10 verbal cognition gate boundary scaffold.

This package exports inert record types and validators only.
"""

from .expectancy import (
    ExpectancyBoundaryRecord,
    demo_connectedness_record,
    demo_congruity_record,
    demo_expectancy_record,
    demo_recoverable_purpose_record,
    demo_unknown_expectancy_record,
    validate_expectancy_record,
)
from .gate_boundary import (
    SCHEMA_VERSION,
    SCOPE_STATUS,
    GateBoundaryRecord,
    ValidationIssue,
    ValidationReport,
    demo_gate_boundary_record,
    demo_unknown_gate_boundary_record,
    stable_boundary_id,
    validate_gate_boundary_record,
    verbal_cognition_gate_scope_record,
)
from .gate_outcome import (
    GateOutcomeBoundaryRecord,
    demo_blocked_action_outcome_record,
    demo_clarification_required_outcome_record,
    demo_gate_outcome_record,
    demo_unknown_gate_outcome_record,
    validate_gate_outcome_record,
)
from .state_boundary import (
    GateStateBoundaryRecord,
    demo_ambiguity_state_record,
    demo_blocked_action_state_record,
    demo_clarification_required_state_record,
    demo_deferred_state_record,
    demo_unsupported_state_record,
    validate_gate_state_record,
)

__all__ = [
    "SCHEMA_VERSION",
    "SCOPE_STATUS",
    "ValidationIssue",
    "ValidationReport",
    "GateBoundaryRecord",
    "GateOutcomeBoundaryRecord",
    "ExpectancyBoundaryRecord",
    "GateStateBoundaryRecord",
    "stable_boundary_id",
    "verbal_cognition_gate_scope_record",
    "validate_gate_boundary_record",
    "validate_gate_outcome_record",
    "validate_expectancy_record",
    "validate_gate_state_record",
    "demo_gate_boundary_record",
    "demo_unknown_gate_boundary_record",
    "demo_gate_outcome_record",
    "demo_clarification_required_outcome_record",
    "demo_blocked_action_outcome_record",
    "demo_unknown_gate_outcome_record",
    "demo_expectancy_record",
    "demo_congruity_record",
    "demo_connectedness_record",
    "demo_recoverable_purpose_record",
    "demo_unknown_expectancy_record",
    "demo_ambiguity_state_record",
    "demo_clarification_required_state_record",
    "demo_unsupported_state_record",
    "demo_blocked_action_state_record",
    "demo_deferred_state_record",
]
