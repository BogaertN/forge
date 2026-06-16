"""
AI.Web Slice 5R1 — Implementation Ledger Continuity and Cycle Update Scaffold.

This package is a deterministic, local-only scaffold for representing and
validating ledger-continuity records and implementation-cycle update records.

It is not a live ledger writer.
It does not update Google Drive.
It does not accept prior slices by itself.
It does not create release or production-readiness authority.
"""

from .ledger import (
    LEDGER_SCHEMA_VERSION,
    LEDGER_ALLOWED_STATUS,
    LEDGER_BLOCKED_AUTHORITIES,
    build_ledger_continuity_record,
    unsafe_phrase,
    unsafe_phrase_catalog,
    validate_ledger_continuity_record,
)

from .cycle import (
    CYCLE_SCHEMA_VERSION,
    CYCLE_ALLOWED_STATUS,
    build_cycle_update_record,
    validate_cycle_update_record,
)

__all__ = [
    "LEDGER_SCHEMA_VERSION",
    "LEDGER_ALLOWED_STATUS",
    "LEDGER_BLOCKED_AUTHORITIES",
    "build_ledger_continuity_record",
    "unsafe_phrase",
    "unsafe_phrase_catalog",
    "validate_ledger_continuity_record",
    "CYCLE_SCHEMA_VERSION",
    "CYCLE_ALLOWED_STATUS",
    "build_cycle_update_record",
    "validate_cycle_update_record",
]
