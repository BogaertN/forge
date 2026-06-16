"""AI.Web Slice 3 controlled status vocabulary and claim discipline scaffold.

This package is deterministic scaffolding only. It does not authorize release,
production readiness, GP-014 supersession, GP-015 repair, GP-015R1 install,
general language authority, UI authority, delivery, memory, evidence, corpus,
external resources, action routing, LLM authority, vector authority, or model
authority.
"""

from .claims import ClaimEvidence, ClaimRecord, ClaimValidation, validate_claim
from .vocabulary import (
    BLOCKED_AUTHORITY_CLAIMS,
    SCHEMA_VERSION,
    STATUS_DEFINITIONS,
    StatusDefinition,
    get_status_definition,
    list_status_keys,
)

__all__ = [
    "BLOCKED_AUTHORITY_CLAIMS",
    "ClaimEvidence",
    "ClaimRecord",
    "ClaimValidation",
    "SCHEMA_VERSION",
    "STATUS_DEFINITIONS",
    "StatusDefinition",
    "get_status_definition",
    "list_status_keys",
    "validate_claim",
]
