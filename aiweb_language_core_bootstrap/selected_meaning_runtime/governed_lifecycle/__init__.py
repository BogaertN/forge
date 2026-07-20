"""Slice 41B deterministic validation and lifecycle custody exports."""

from .canonical import (
    CANONICAL_FIELD_ORDERS,
    SUPPORTED_RECORD_TYPES,
    SelectedMeaningCanonicalizationError,
    canonical_field_order,
    canonical_json_bytes,
    canonical_record_bytes,
    canonical_record_mapping,
    canonicalize_field_pairs,
    deterministic_digest,
    deterministic_record_digest,
    stable_identifier,
)
from .identity import (
    expected_alternative_candidate_custody_id,
    expected_bundle_digest,
    expected_bundle_id,
    expected_gate_custody_reference_id,
    expected_inherited_limitation_custody_id,
    expected_lifecycle_record_id,
    expected_lifecycle_transition_id,
    expected_record_id,
    expected_runtime_schema_record_id,
    expected_selected_meaning_decision_status_id,
    expected_selection_authority_requirement_id,
    expected_selection_candidate_custody_id,
    expected_selection_eligibility_status_id,
    expected_selection_receipt_boundary_id,
    expected_selection_trace_boundary_id,
    expected_unresolved_state_custody_id,
    expected_version_custody_id,
    identity_field,
    identity_namespace,
    with_expected_bundle_identity,
    with_expected_id,
)
from .lifecycle import assert_lifecycle_transition, evaluate_lifecycle_transition
from .rules import (
    SELECTED_MEANING_LIFECYCLE_TRANSITION_RULES,
    SelectedMeaningLifecycleTransitionRule,
    lifecycle_transition_allowed,
    lifecycle_transition_rule,
)
from .schema import (
    CANONICAL_FIELD_ORDER_VERSION,
    DIGEST_ALGORITHM,
    SLICE41B_ACCEPTED_PARENT_HEAD,
    SLICE41B_ACCEPTED_PARENT_SUBJECT,
    SLICE41B_ACCEPTED_PARENT_TREE,
    SLICE41B_SCHEMA_VERSION,
    SUPPORTED_RUNTIME_SCHEMA_VERSIONS,
    SUPPORTED_RUNTIME_SPEC_VERSIONS,
    SelectedMeaningGovernanceBundle,
    SelectedMeaningLifecycleDecision,
    SelectedMeaningLifecycleRecord,
    SelectedMeaningLifecycleStage,
    SelectedMeaningLifecycleTransitionKind,
    SelectedMeaningLifecycleTransitionRecord,
    SelectedMeaningValidationCode,
    SelectedMeaningValidationError,
    SelectedMeaningValidationIssue,
    SelectedMeaningValidationReport,
    SelectedMeaningVersionCustody,
)
from .validation import (
    assert_valid_governance_bundle,
    assert_valid_runtime_schema_record,
    assert_valid_version_custody,
    expected_predecessor_references,
    expected_record_schema_versions,
    validate_alternative_candidate_custody,
    validate_field_pairs,
    validate_gate_custody_reference,
    validate_governance_bundle,
    validate_identity_collection,
    validate_inherited_limitation_custody,
    validate_lifecycle_record,
    validate_lifecycle_transition_record,
    validate_runtime_schema_record,
    validate_selected_meaning_decision_status,
    validate_selection_authority_requirement,
    validate_selection_candidate_custody,
    validate_selection_eligibility_status,
    validate_selection_receipt_boundary,
    validate_selection_trace_boundary,
    validate_unresolved_state_custody,
    validate_version_custody,
)

__all__ = tuple(
    sorted(
        name
        for name in globals()
        if not name.startswith("_")
    )
)
