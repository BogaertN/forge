"""Slice 12 ambiguity / unknown / clarification state boundary scaffold.

This package is deterministic and boundary-only. It represents uncertainty
states and clarification requirements without asking live questions, selecting
meaning, deciding truth, authorizing action, routing tools, writing memory,
validating evidence, admitting external resources, or invoking model authority.
"""

from .state_boundary import (
    AmbiguityStateBoundaryRecord,
    ambiguity_clarification_scope_record,
    build_state_boundary_record,
    demo_ambiguity_state_record,
    demo_deferred_state_record,
    demo_unknown_state_record,
    demo_unsupported_state_record,
    validate_state_boundary_record,
)
from .clarification import (
    ClarificationRequirementBoundaryRecord,
    build_clarification_requirement_record,
    demo_clarification_blocked_record,
    demo_clarification_required_record,
    validate_clarification_requirement_record,
)
from .unknown_support import (
    UnknownSupportBoundaryRecord,
    build_unknown_support_record,
    demo_unknown_concept_record,
    demo_unsupported_resource_record,
    validate_unknown_support_record,
)
from .trace_state import (
    StateTraceBoundaryRecord,
    build_state_trace_record,
    demo_state_trace_record,
    validate_state_trace_record,
)
from .verify import run_verification

__all__ = [
    "AmbiguityStateBoundaryRecord",
    "ClarificationRequirementBoundaryRecord",
    "UnknownSupportBoundaryRecord",
    "StateTraceBoundaryRecord",
    "ambiguity_clarification_scope_record",
    "build_state_boundary_record",
    "build_clarification_requirement_record",
    "build_unknown_support_record",
    "build_state_trace_record",
    "demo_ambiguity_state_record",
    "demo_deferred_state_record",
    "demo_unknown_state_record",
    "demo_unsupported_state_record",
    "demo_clarification_blocked_record",
    "demo_clarification_required_record",
    "demo_unknown_concept_record",
    "demo_unsupported_resource_record",
    "demo_state_trace_record",
    "validate_state_boundary_record",
    "validate_clarification_requirement_record",
    "validate_unknown_support_record",
    "validate_state_trace_record",
    "run_verification",
]
