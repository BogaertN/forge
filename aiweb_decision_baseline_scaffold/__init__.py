"""AI.Web Slice 4 decision and accepted-baseline scaffold.

This package is deterministic scaffolding only.  It does not accept any slice by
itself, does not authorize release, and does not create production readiness.
"""

from .decision import (
    DecisionRecord,
    DecisionValidation,
    build_decision_record,
    validate_decision_record,
)
from .baseline import (
    AcceptedBaselineUpdate,
    BaselineValidation,
    build_accepted_baseline_update,
    validate_accepted_baseline_update,
)

__all__ = [
    "AcceptedBaselineUpdate",
    "BaselineValidation",
    "DecisionRecord",
    "DecisionValidation",
    "build_accepted_baseline_update",
    "build_decision_record",
    "validate_accepted_baseline_update",
    "validate_decision_record",
]
