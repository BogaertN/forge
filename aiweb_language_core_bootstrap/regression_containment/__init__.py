"""Slice 34 bootstrap regression and containment acceptance boundary.

Importing this subpackage performs no evaluation, regression run, rollback,
network access, filesystem write, memory write, delivery, tool routing, action,
or authority grant.
"""

from .evaluator import (
    evaluate_bootstrap_containment,
    run_default_containment_evaluation,
    run_explicit_offline_containment_evaluation,
)
from .policy import (
    FLOW_IDENTITY_EXPECTATIONS,
    ONE_COMMAND_ROLLBACK_REQUIRED,
    PROHIBITED_AUTHORITY_CATEGORIES,
    REQUIRED_CONTAINMENT_GUARDS,
    REQUIRED_INHERITED_REGRESSION_COMMAND_COUNT,
    REQUIRED_PHASE_B_PRESERVATION_COMMAND_COUNT,
    REQUIRED_PRIOR_COMMAND_COUNT,
    SLICE34_COMMIT_SUBJECT,
    SLICE34_PARENT_HEAD,
    SLICE34_SCHEMA_VERSION,
    SLICE34_TITLE,
)
from .schema import (
    BootstrapContainmentEvaluation,
    BootstrapContainmentState,
    FlowContainmentProof,
    build_bootstrap_containment_evaluation,
    build_bootstrap_containment_state,
    build_flow_containment_proof,
    validate_bootstrap_containment_evaluation,
    validate_bootstrap_containment_state,
    validate_flow_containment_proof,
)

__all__ = (
    "BootstrapContainmentEvaluation",
    "BootstrapContainmentState",
    "FLOW_IDENTITY_EXPECTATIONS",
    "FlowContainmentProof",
    "ONE_COMMAND_ROLLBACK_REQUIRED",
    "PROHIBITED_AUTHORITY_CATEGORIES",
    "REQUIRED_CONTAINMENT_GUARDS",
    "REQUIRED_INHERITED_REGRESSION_COMMAND_COUNT",
    "REQUIRED_PHASE_B_PRESERVATION_COMMAND_COUNT",
    "REQUIRED_PRIOR_COMMAND_COUNT",
    "SLICE34_COMMIT_SUBJECT",
    "SLICE34_PARENT_HEAD",
    "SLICE34_SCHEMA_VERSION",
    "SLICE34_TITLE",
    "build_bootstrap_containment_evaluation",
    "build_bootstrap_containment_state",
    "build_flow_containment_proof",
    "evaluate_bootstrap_containment",
    "run_default_containment_evaluation",
    "run_explicit_offline_containment_evaluation",
    "validate_bootstrap_containment_evaluation",
    "validate_bootstrap_containment_state",
    "validate_flow_containment_proof",
)
