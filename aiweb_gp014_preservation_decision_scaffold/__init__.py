"""AI.Web Slice 18 GP-014 preservation / wrapper decision scaffold.

This package records GP-014 as preserved, protected, unsuperseded, and
referenced only. It is standard-library only and does not import, call, wrap,
modify, supersede, promote, or execute GP-014. It grants no general language,
concept, predicate, selected-meaning, full-RMC, renderer, output, delivery,
runtime, Echo, release, model, vector, retrieval, training, UI, memory, corpus,
or production authority.
"""

from .core import (
    BASE_HEAD,
    GP014_IDENTITY,
    GP014_PROTECTED_PATH_HASHES,
    GP014_RELATIONSHIP,
    GP014_STATUS,
    GP014_WRAPPER_DECISION,
    GP015_PROTECTED_PATH_HASHES,
    GP015_STATUS,
    REQUIRED_DECISION_LAWS,
    SCHEMA_VERSION,
    SOURCE_AUTHORITY_PACKET_SHA256,
    gp014_decision_scope_record,
)
from .gp014_reference import (
    GP014ReferenceRecord,
    build_gp014_reference_record,
    validate_gp014_reference_record,
    verify_gp014_reference_hashes,
)
from .wrapper_decision import (
    GP014WrapperDecisionRecord,
    build_gp014_wrapper_decision_record,
    validate_gp014_wrapper_decision_record,
)
from .preservation_receipt import (
    GP014PreservationReceiptRecord,
    build_gp014_preservation_receipt_record,
    validate_gp014_preservation_receipt_record,
)
from .verify import run_verification

__all__ = (
    "SCHEMA_VERSION",
    "BASE_HEAD",
    "SOURCE_AUTHORITY_PACKET_SHA256",
    "GP014_IDENTITY",
    "GP014_STATUS",
    "GP014_RELATIONSHIP",
    "GP014_WRAPPER_DECISION",
    "GP014_PROTECTED_PATH_HASHES",
    "GP015_STATUS",
    "GP015_PROTECTED_PATH_HASHES",
    "REQUIRED_DECISION_LAWS",
    "gp014_decision_scope_record",
    "GP014ReferenceRecord",
    "build_gp014_reference_record",
    "validate_gp014_reference_record",
    "verify_gp014_reference_hashes",
    "GP014WrapperDecisionRecord",
    "build_gp014_wrapper_decision_record",
    "validate_gp014_wrapper_decision_record",
    "GP014PreservationReceiptRecord",
    "build_gp014_preservation_receipt_record",
    "validate_gp014_preservation_receipt_record",
    "run_verification",
)
