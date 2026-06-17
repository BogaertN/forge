"""Slice 13 requirements-to-test traceability scaffold.

This package represents traceability records only. It does not create live
runtime behavior, accept capability, replace verifier gates, bypass result
packets, widen accepted scope, or activate external authority.
"""

from .accepted_scope import (
    AcceptedScopeRecord,
    RollbackTriggerRecord,
    build_accepted_scope_record,
    build_rollback_trigger_record,
    demo_accepted_scope_record,
    demo_rollback_trigger_record,
    validate_accepted_scope_record,
    validate_rollback_trigger_record,
)
from .core import requirements_traceability_scope_record
from .crosswalk import (
    RequirementTestCrosswalkRecord,
    build_requirement_test_crosswalk_record,
    demo_requirement_test_crosswalk_record,
    validate_requirement_test_crosswalk_record,
)
from .receipt import (
    TraceabilityReceiptRecord,
    build_traceability_receipt_record,
    demo_traceability_receipt_record,
    validate_traceability_receipt_record,
)
from .requirement import (
    RequirementIdentityRecord,
    build_requirement_identity_record,
    demo_requirement_identity_record,
    validate_requirement_identity_record,
)

__all__ = [
    "AcceptedScopeRecord",
    "RollbackTriggerRecord",
    "TraceabilityReceiptRecord",
    "RequirementIdentityRecord",
    "RequirementTestCrosswalkRecord",
    "build_accepted_scope_record",
    "build_rollback_trigger_record",
    "build_traceability_receipt_record",
    "build_requirement_identity_record",
    "build_requirement_test_crosswalk_record",
    "demo_accepted_scope_record",
    "demo_rollback_trigger_record",
    "demo_traceability_receipt_record",
    "demo_requirement_identity_record",
    "demo_requirement_test_crosswalk_record",
    "requirements_traceability_scope_record",
    "validate_accepted_scope_record",
    "validate_rollback_trigger_record",
    "validate_traceability_receipt_record",
    "validate_requirement_identity_record",
    "validate_requirement_test_crosswalk_record",
]
