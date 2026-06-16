"""AI.Web Slice 6 scanner scaffold.

This package is deterministic, local, and additive.
It creates scan records only. It does not grant runtime power.
"""

from .catalog import (
    SCHEMA_VERSION,
    assembled_unsafe_catalog,
    scanner_scope_record,
)
from .scanner import (
    Finding,
    ScanReport,
    scan_text,
    scan_file,
    scan_paths,
)

__all__ = [
    "SCHEMA_VERSION",
    "assembled_unsafe_catalog",
    "scanner_scope_record",
    "Finding",
    "ScanReport",
    "scan_text",
    "scan_file",
    "scan_paths",
]
