"""AI.Web Slice 23 end-to-end dry-run harness scaffold."""

from .authority import (
    DOWNSTREAM_FALSE_ONLY_FIELDS,
    EXPECTED_COMMIT_SUBJECT,
    REQUIRED_DRY_RUN_LAWS,
    REQUIRED_DRY_RUN_STEP_ORDER,
    SCHEMA_VERSION,
    SLICE_ID,
    SLICE_TITLE,
    build_authority_separation_record,
    validate_authority_separation_record,
)
from .core import build_demo_harness_record, validate_dry_run_harness_record
from .fixture import build_default_fixtures
from .receipt import build_receipt, validate_receipt

__all__ = (
    "DOWNSTREAM_FALSE_ONLY_FIELDS",
    "EXPECTED_COMMIT_SUBJECT",
    "REQUIRED_DRY_RUN_LAWS",
    "REQUIRED_DRY_RUN_STEP_ORDER",
    "SCHEMA_VERSION",
    "SLICE_ID",
    "SLICE_TITLE",
    "build_authority_separation_record",
    "build_default_fixtures",
    "build_demo_harness_record",
    "build_receipt",
    "validate_authority_separation_record",
    "validate_dry_run_harness_record",
    "validate_receipt",
)
