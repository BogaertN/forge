"""Public Slice 42G MSM outward-expression integration API."""

from .authority import (
    DIGEST_ALGORITHM,
    SLICE42G_ACCEPTED_PARENT_HEAD,
    SLICE42G_ACCEPTED_PARENT_SUBJECT,
    SLICE42G_ACCEPTED_PARENT_TREE,
    SLICE42G_ADAPTER_DECISION,
    SLICE42G_ALLOWED_MSM_ADDITIONS,
    SLICE42G_COMMIT_SUBJECT,
    SLICE42G_COMPANION_VERSION,
    SLICE42G_GOVERNING_AUTHORITY_REFS,
    SLICE42G_PERMANENT_BOUNDARIES,
    SLICE42G_PROFILE_KEY,
    SLICE42G_PROFILE_VERSION,
    SLICE42G_PROHIBITED_AUTHORITY,
    SLICE42G_RECEIPT_VERSION,
    SLICE42G_REQUIRED_PATH,
    SLICE42G_REQUIRED_UNCHANGED_SECTIONS,
    SLICE42G_SCHEMA_VERSION,
    SLICE42G_SPEC_ID,
    SLICE42G_SPEC_VERSION,
)
from .canonical import (
    MsmOutwardExpressionCanonicalizationError,
    canonical_json_bytes,
    canonical_value,
    deterministic_digest,
    stable_identifier,
)
from .identity import (
    expected_authority_reference_id,
    expected_companion_id,
    expected_expression_link_id,
    expected_input_id,
    expected_outward_meaning_id,
    expected_profile_id,
    expected_receipt_id,
    expected_result_digest,
    expected_result_id,
    expected_successor_manifest_id,
    expected_transition_trace_id,
    input_identity_body,
    result_identity_body,
    with_expected_companion_id,
    with_expected_input_id,
    with_expected_profile_id,
    with_expected_receipt_id,
    with_expected_result_identity,
)
from .integration import (
    build_expression_link,
    build_external_authority_reference,
    build_governed_outward_meaning,
    construct_successor_artifacts,
    derive_outward_meaning_fields,
    integrate_outward_meaning_and_expression_link,
)
from .schema import (
    APPROVED_STRICT_PROFILE as _UNBOUND_PROFILE,
    MsmOutwardExpressionCustodyCompanionV1,
    MsmOutwardExpressionIntegrationAuthorityProfile,
    MsmOutwardExpressionIntegrationInput,
    MsmOutwardExpressionIntegrationReceiptV1,
    MsmOutwardExpressionIntegrationResult,
    MsmOutwardExpressionIntegrationValidationCode,
    MsmOutwardExpressionIntegrationValidationError,
    MsmOutwardExpressionIntegrationValidationIssue,
    MsmOutwardExpressionIntegrationValidationReport,
)
from .validation import (
    assert_valid_integration_input,
    assert_valid_integration_result,
    validate_authority_profile,
    validate_integration_input,
    validate_integration_result,
)

APPROVED_STRICT_PROFILE = with_expected_profile_id(_UNBOUND_PROFILE)

__all__ = tuple(name for name in globals() if not name.startswith("_"))
