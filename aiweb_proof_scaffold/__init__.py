"""AI.Web Slice 1 proof scaffold.

This package provides deterministic receipt and manifest helpers for Slice 1 only.
It does not interpret language, validate evidence, write memory, ingest resources,
render UI, route actions, invoke models, or authorize delivery.
"""

from .schema import (
    SCHEMA_VERSION,
    SLICE_ID,
    SLICE_NAME,
    BLOCKED_AUTHORITIES,
    REQUIRED_RECEIPT_FIELDS,
    validate_receipt,
)
from .receipt import build_receipt, write_receipt, sha256_file, utc_now_iso
from .verify import verify_installation

__all__ = [
    "SCHEMA_VERSION",
    "SLICE_ID",
    "SLICE_NAME",
    "BLOCKED_AUTHORITIES",
    "REQUIRED_RECEIPT_FIELDS",
    "validate_receipt",
    "build_receipt",
    "write_receipt",
    "sha256_file",
    "utc_now_iso",
    "verify_installation",
]
