"""Public Slice 38H disabled predicate-role-frame bootstrap surface.

Importing this package activates nothing.  Execution requires an explicitly
enabled offline state and one exact accepted synthetic fixture invocation.
"""

from .fixtures import (
    FIXTURE_AMBIGUOUS_UNSUPPORTED,
    FIXTURE_CANDIDATE_UNSUPPORTED,
    FIXTURE_EXPLICIT_UNKNOWN,
    FIXTURE_EXPLICIT_UNSUPPORTED,
    FIXTURE_NO_MATCH_UNKNOWN,
    get_disabled_predicate_role_frame_fixture,
    is_exact_accepted_fixture,
    list_disabled_predicate_role_frame_fixtures,
)
from .integration import (
    REASON_DISABLED,
    REQUESTED_OPERATION,
    build_disabled_predicate_role_frame_bootstrap_state,
    build_fixture_invocation,
    build_slice38_acceptance_record,
    build_slice38_rollback_metadata,
    run_disabled_predicate_role_frame_bootstrap,
)
from .schema import (
    PRE_SLICE38_COMMIT,
    PRE_SLICE38_TREE,
    SLICE38_ACCEPTED_CHAIN,
    SLICE38_ACCEPTED_SCOPE,
    SLICE38_DEFERRED_SCOPE,
    SLICE38_INCREMENT_LABELS,
    SLICE38_PERMANENT_BOUNDARIES,
    SLICE38G_ACCEPTED_HEAD,
    SLICE38G_ACCEPTED_SUBJECT,
    SLICE38G_ACCEPTED_TREE,
    SLICE38H_COMMIT_SUBJECT,
    SLICE38H_SCHEMA_VERSION,
    SLICE38H_SPEC_ID,
    SLICE38H_SPEC_VERSION,
    CloseoutIntegrationStage,
    CloseoutIntegrationStatus,
    CloseoutStageReceipt,
    DisabledPredicateRoleFrameBootstrapResult,
    DisabledPredicateRoleFrameBootstrapState,
    DisabledPredicateRoleFrameFixture,
    DisabledPredicateRoleFrameInvocation,
    Slice38AcceptanceRecord,
    Slice38RollbackMetadata,
)
from .validation import (
    PUBLIC_VALIDATORS,
    ValidationReport,
    validate_acceptance_record,
    validate_fixture,
    validate_integration_result,
    validate_integration_state,
    validate_invocation,
    validate_rollback_metadata,
    validate_stage_receipt,
)

__all__ = (
    "PRE_SLICE38_COMMIT", "PRE_SLICE38_TREE", "SLICE38_ACCEPTED_CHAIN",
    "SLICE38_ACCEPTED_SCOPE", "SLICE38_DEFERRED_SCOPE",
    "SLICE38_INCREMENT_LABELS", "SLICE38_PERMANENT_BOUNDARIES",
    "SLICE38G_ACCEPTED_HEAD", "SLICE38G_ACCEPTED_SUBJECT",
    "SLICE38G_ACCEPTED_TREE", "SLICE38H_COMMIT_SUBJECT",
    "SLICE38H_SCHEMA_VERSION", "SLICE38H_SPEC_ID", "SLICE38H_SPEC_VERSION",
    "CloseoutIntegrationStage", "CloseoutIntegrationStatus",
    "CloseoutStageReceipt", "DisabledPredicateRoleFrameBootstrapResult",
    "DisabledPredicateRoleFrameBootstrapState", "DisabledPredicateRoleFrameFixture",
    "DisabledPredicateRoleFrameInvocation", "FIXTURE_AMBIGUOUS_UNSUPPORTED",
    "FIXTURE_CANDIDATE_UNSUPPORTED", "FIXTURE_EXPLICIT_UNKNOWN",
    "FIXTURE_EXPLICIT_UNSUPPORTED", "FIXTURE_NO_MATCH_UNKNOWN",
    "PUBLIC_VALIDATORS", "REASON_DISABLED", "REQUESTED_OPERATION",
    "Slice38AcceptanceRecord", "Slice38RollbackMetadata", "ValidationReport",
    "build_disabled_predicate_role_frame_bootstrap_state",
    "build_fixture_invocation", "build_slice38_acceptance_record",
    "build_slice38_rollback_metadata", "get_disabled_predicate_role_frame_fixture",
    "is_exact_accepted_fixture", "list_disabled_predicate_role_frame_fixtures",
    "run_disabled_predicate_role_frame_bootstrap", "validate_acceptance_record",
    "validate_fixture", "validate_integration_result", "validate_integration_state",
    "validate_invocation", "validate_rollback_metadata", "validate_stage_receipt",
)
