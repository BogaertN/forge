"""Slice 42C authorized meaning admission and expression eligibility API."""
from .authority import (
    DIGEST_ALGORITHM, SLICE42C_ACCEPTED_PARENT_HEAD, SLICE42C_ACCEPTED_PARENT_SUBJECT,
    SLICE42C_ACCEPTED_PARENT_TREE, SLICE42C_GOVERNING_AUTHORITY_REFS,
    SLICE42C_OUTCOME_VALUES, SLICE42C_PERMANENT_BOUNDARIES, SLICE42C_PROFILE_KEY,
    SLICE42C_PROFILE_VERSION, SLICE42C_PROHIBITED_AUTHORITY, SLICE42C_SCHEMA_VERSION,
    SLICE42C_SPEC_ID, SLICE42C_SPEC_VERSION,
)
from .canonical import ExpressionEligibilityCanonicalizationError, canonical_json_bytes, deterministic_digest, stable_identifier
from .evaluator import determine_outcome, evaluate_expression_eligibility
from .identity import expected_record_id, expected_result_digest, expected_result_id, with_expected_id, with_expected_result_identity
from .schema import (
    AuthorizedMeaningAdmissionRecord, ExpressionEligibilityEvaluationInput,
    ExpressionEligibilityFinding, ExpressionEligibilityFindingKind,
    ExpressionEligibilityOutcome, ExpressionEligibilityResult,
    ExpressionEligibilityValidationCode, ExpressionEligibilityValidationError,
    ExpressionEligibilityValidationIssue, ExpressionEligibilityValidationReport,
    OutwardExpressionAuthorityRecord,
)
from .validation import assert_valid_evaluation_input, assert_valid_result, validate_admission_record, validate_authority_record, validate_evaluation_input, validate_result

__all__ = (
    "AuthorizedMeaningAdmissionRecord", "DIGEST_ALGORITHM", "ExpressionEligibilityCanonicalizationError",
    "ExpressionEligibilityEvaluationInput", "ExpressionEligibilityFinding", "ExpressionEligibilityFindingKind",
    "ExpressionEligibilityOutcome", "ExpressionEligibilityResult", "ExpressionEligibilityValidationCode",
    "ExpressionEligibilityValidationError", "ExpressionEligibilityValidationIssue", "ExpressionEligibilityValidationReport",
    "OutwardExpressionAuthorityRecord", "SLICE42C_ACCEPTED_PARENT_HEAD", "SLICE42C_ACCEPTED_PARENT_SUBJECT",
    "SLICE42C_ACCEPTED_PARENT_TREE", "SLICE42C_GOVERNING_AUTHORITY_REFS", "SLICE42C_OUTCOME_VALUES",
    "SLICE42C_PERMANENT_BOUNDARIES", "SLICE42C_PROFILE_KEY", "SLICE42C_PROFILE_VERSION",
    "SLICE42C_PROHIBITED_AUTHORITY", "SLICE42C_SCHEMA_VERSION", "SLICE42C_SPEC_ID", "SLICE42C_SPEC_VERSION",
    "assert_valid_evaluation_input", "assert_valid_result", "canonical_json_bytes", "deterministic_digest",
    "determine_outcome", "evaluate_expression_eligibility", "expected_record_id", "expected_result_digest",
    "expected_result_id", "stable_identifier", "validate_admission_record", "validate_authority_record",
    "validate_evaluation_input", "validate_result", "with_expected_id", "with_expected_result_identity",
)
