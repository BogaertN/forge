"""AI.Web Slice 17 output/expression boundary scaffold.

This package is additive, deterministic, standard-library only, and grants no
runtime, truth, proof, authority, acceptance, permission, delivery, execution,
model, retrieval, memory, release, or production authority.
"""

from .core import (
    NON_AUTHORITY_DISCLAIMER,
    REQUIRED_EXPRESSION_LAWS,
    SCHEMA_VERSION,
    expression_scope_record,
)
from .expression_source import (
    ExpressionSourceRecord,
    build_expression_source_record,
    validate_expression_source_record,
)
from .preservation_contract import (
    ExpressionPreservationContractRecord,
    build_expression_preservation_contract,
    validate_expression_preservation_contract,
)
from .expression_plan import (
    ExpressionPlanRecord,
    build_expression_plan_record,
    validate_expression_plan_record,
)
from .expression_preview import (
    ExpressionPreviewRecord,
    render_expression_preview,
    validate_expression_preview_record,
)
from .fidelity import (
    ExpressionFidelityRecord,
    evaluate_expression_fidelity,
    validate_expression_fidelity_record,
)
from .expression_receipt import (
    ExpressionReceiptRecord,
    build_expression_receipt_record,
    validate_expression_receipt_record,
)

__all__ = (
    "SCHEMA_VERSION",
    "NON_AUTHORITY_DISCLAIMER",
    "REQUIRED_EXPRESSION_LAWS",
    "expression_scope_record",
    "ExpressionSourceRecord",
    "build_expression_source_record",
    "validate_expression_source_record",
    "ExpressionPreservationContractRecord",
    "build_expression_preservation_contract",
    "validate_expression_preservation_contract",
    "ExpressionPlanRecord",
    "build_expression_plan_record",
    "validate_expression_plan_record",
    "ExpressionPreviewRecord",
    "render_expression_preview",
    "validate_expression_preview_record",
    "ExpressionFidelityRecord",
    "evaluate_expression_fidelity",
    "validate_expression_fidelity_record",
    "ExpressionReceiptRecord",
    "build_expression_receipt_record",
    "validate_expression_receipt_record",
)
