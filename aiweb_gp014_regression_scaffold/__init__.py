"""AI.Web Slice 2 GP-014 baseline preservation and regression scaffold.

This package is a deterministic proof scaffold only.
It does not implement language interpretation.
It does not replace, supersede, or modify GP-014 / LANG-EXPR-001.
"""

from .baseline import (
    BASELINE_SCHEMA_VERSION,
    GP014_BASELINE_IDENTITY,
    build_gp014_baseline_record,
    find_gp014_marker_files,
)
from .regression import (
    REGRESSION_SCHEMA_VERSION,
    build_regression_receipt,
    validate_regression_receipt,
)
from .verify import verify_slice02_gp014_regression_scaffold

__all__ = [
    "BASELINE_SCHEMA_VERSION",
    "GP014_BASELINE_IDENTITY",
    "REGRESSION_SCHEMA_VERSION",
    "build_gp014_baseline_record",
    "find_gp014_marker_files",
    "build_regression_receipt",
    "validate_regression_receipt",
    "verify_slice02_gp014_regression_scaffold",
]
