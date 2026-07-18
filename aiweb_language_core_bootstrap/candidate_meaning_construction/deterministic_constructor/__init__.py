"""Slice 39F deterministic CandidateMeaning constructor exports."""

from .authority import (
    SLICE39F_CANDIDATE_VERSION,
    SLICE39F_PERMANENT_BOUNDARIES,
    SLICE39F_PROFILE_VERSION,
    SLICE39F_PROHIBITED_AUTHORITY,
    SLICE39F_REQUIRED_PATH,
    SLICE39F_SCHEMA_VERSION,
    SLICE39F_SPEC_ID,
    SLICE39F_SPEC_VERSION,
)
from .canonical import canonical_json_bytes, deterministic_digest, stable_identifier
from .constructor import DEFAULT_CONSTRUCTOR_PROFILE, construct_candidate_meanings
from .identity import (
    expected_constructed_record_id,
    expected_profile_id,
    expected_result_digest,
    expected_result_id,
)
from .schema import (
    CandidateMeaningConstructedRecord,
    CandidateMeaningConstructorInput,
    CandidateMeaningConstructorProfile,
    CandidateMeaningConstructorResult,
    CandidateMeaningConstructorStatus,
    CandidateMeaningConstructorValidationCode,
    CandidateMeaningConstructorValidationError,
    CandidateMeaningConstructorValidationIssue,
    CandidateMeaningConstructorValidationReport,
)
from .validation import assert_valid_result, validate_constructed_record, validate_profile, validate_result

__all__ = (
    "DEFAULT_CONSTRUCTOR_PROFILE",
    "SLICE39F_CANDIDATE_VERSION",
    "SLICE39F_PERMANENT_BOUNDARIES",
    "SLICE39F_PROFILE_VERSION",
    "SLICE39F_PROHIBITED_AUTHORITY",
    "SLICE39F_REQUIRED_PATH",
    "SLICE39F_SCHEMA_VERSION",
    "SLICE39F_SPEC_ID",
    "SLICE39F_SPEC_VERSION",
    "CandidateMeaningConstructedRecord",
    "CandidateMeaningConstructorInput",
    "CandidateMeaningConstructorProfile",
    "CandidateMeaningConstructorResult",
    "CandidateMeaningConstructorStatus",
    "CandidateMeaningConstructorValidationCode",
    "CandidateMeaningConstructorValidationError",
    "CandidateMeaningConstructorValidationIssue",
    "CandidateMeaningConstructorValidationReport",
    "assert_valid_result",
    "canonical_json_bytes",
    "construct_candidate_meanings",
    "deterministic_digest",
    "expected_constructed_record_id",
    "expected_profile_id",
    "expected_result_digest",
    "expected_result_id",
    "stable_identifier",
    "validate_constructed_record",
    "validate_profile",
    "validate_result",
)
