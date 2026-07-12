"""Slice 19 RMC Echo Boundary Scaffold.

This package is intentionally boundary-only.
It does not implement RMC Echo validation, delivery, release, rendering, or output approval.
"""

from .authority import (
    ECHO_AUTHORITY_DENIALS,
    ECHO_AUTHORITY_LAYER,
    authority_decision_for_claim,
    build_authority_report,
)
from .boundary import (
    BOUNDARY_STATEMENTS,
    ECHO_RELATIONSHIP,
    IMPLEMENTATION_STATE,
    build_boundary_report,
    validate_boundary_report,
)
from .receipt import build_slice19_receipt
from .verify import verify_slice19_invariants

__all__ = [
    "BOUNDARY_STATEMENTS",
    "ECHO_AUTHORITY_DENIALS",
    "ECHO_AUTHORITY_LAYER",
    "ECHO_RELATIONSHIP",
    "IMPLEMENTATION_STATE",
    "authority_decision_for_claim",
    "build_authority_report",
    "build_boundary_report",
    "build_slice19_receipt",
    "validate_boundary_report",
    "verify_slice19_invariants",
]
