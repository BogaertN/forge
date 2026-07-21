"""Public API for Slice 42E controlled expression-plan construction."""

from .authority import (
    DIGEST_ALGORITHM,
    SLICE42E_ACCEPTED_PARENT_HEAD,
    SLICE42E_ACCEPTED_PARENT_SUBJECT,
    SLICE42E_ACCEPTED_PARENT_TREE,
    SLICE42E_GOVERNING_AUTHORITY_REFS,
    SLICE42E_PERMANENT_BOUNDARIES,
    SLICE42E_PLAN_AUTHORITY_KEY,
    SLICE42E_PLAN_DISPOSITION_VALUES,
    SLICE42E_PROFILE_KEY,
    SLICE42E_PROFILE_VERSION,
    SLICE42E_PROHIBITED_AUTHORITY,
    SLICE42E_SCHEMA_VERSION,
    SLICE42E_SECTION_ORDER_VALUES,
    SLICE42E_SPEC_ID,
    SLICE42E_SPEC_VERSION,
)
from .canonical import (
    ExpressionPlanCanonicalizationError,
    canonical_json_bytes,
    deterministic_digest,
    stable_identifier,
)
from .identity import (
    expected_plan_digest,
    expected_plan_id,
    expected_record_id,
    expected_result_digest,
    expected_result_id,
    with_expected_id,
    with_expected_plan_identity,
    with_expected_result_identity,
)
from .planner import (
    build_plan_sections,
    construct_expression_plan,
    derive_plan_values,
    determine_plan_disposition,
    section_source_values,
    structural_order,
)
from .schema import (
    ControlledExpressionPlan,
    ExpressionPlanConstructionAuthorityRecord,
    ExpressionPlanConstructionFinding,
    ExpressionPlanConstructionFindingKind,
    ExpressionPlanConstructionInput,
    ExpressionPlanConstructionResult,
    ExpressionPlanConstructionValidationCode,
    ExpressionPlanConstructionValidationError,
    ExpressionPlanConstructionValidationIssue,
    ExpressionPlanConstructionValidationReport,
    ExpressionPlanDisposition,
    ExpressionPlanSection,
    ExpressionPlanSectionKind,
)
from .validation import (
    assert_valid_plan_input,
    assert_valid_plan_result,
    validate_expression_plan,
    validate_plan_authority_record,
    validate_plan_input,
    validate_plan_result,
)

__all__ = tuple(
    name
    for name in globals()
    if name.startswith("SLICE42E_")
    or name in {
        "DIGEST_ALGORITHM",
        "ControlledExpressionPlan",
        "ExpressionPlanCanonicalizationError",
        "ExpressionPlanConstructionAuthorityRecord",
        "ExpressionPlanConstructionFinding",
        "ExpressionPlanConstructionFindingKind",
        "ExpressionPlanConstructionInput",
        "ExpressionPlanConstructionResult",
        "ExpressionPlanConstructionValidationCode",
        "ExpressionPlanConstructionValidationError",
        "ExpressionPlanConstructionValidationIssue",
        "ExpressionPlanConstructionValidationReport",
        "ExpressionPlanDisposition",
        "ExpressionPlanSection",
        "ExpressionPlanSectionKind",
        "assert_valid_plan_input",
        "assert_valid_plan_result",
        "build_plan_sections",
        "canonical_json_bytes",
        "construct_expression_plan",
        "derive_plan_values",
        "deterministic_digest",
        "determine_plan_disposition",
        "expected_plan_digest",
        "expected_plan_id",
        "expected_record_id",
        "expected_result_digest",
        "expected_result_id",
        "section_source_values",
        "stable_identifier",
        "structural_order",
        "validate_expression_plan",
        "validate_plan_authority_record",
        "validate_plan_input",
        "validate_plan_result",
        "with_expected_id",
        "with_expected_plan_identity",
        "with_expected_result_identity",
    }
)
