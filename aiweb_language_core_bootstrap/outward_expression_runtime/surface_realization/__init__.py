"""Public Slice 42F deterministic surface-realization API."""

from .authority import (
    DIGEST_ALGORITHM,
    SLICE42F_ACCEPTED_PARENT_HEAD,
    SLICE42F_ACCEPTED_PARENT_SUBJECT,
    SLICE42F_ACCEPTED_PARENT_TREE,
    SLICE42F_ADMITTED_RULE_REFS,
    SLICE42F_DISPOSITION_VALUES,
    SLICE42F_GOVERNING_AUTHORITY_REFS,
    SLICE42F_PERMANENT_BOUNDARIES,
    SLICE42F_PROFILE_KEY,
    SLICE42F_PROFILE_VERSION,
    SLICE42F_PROHIBITED_AUTHORITY,
    SLICE42F_REALIZATION_AUTHORITY_KEY,
    SLICE42F_REQUIRED_TEMPLATE_KEYS,
    SLICE42F_RESOURCE_PROFILE_KEY,
    SLICE42F_RESOURCE_PROFILE_VERSION,
    SLICE42F_SCHEMA_VERSION,
    SLICE42F_SPEC_ID,
    SLICE42F_SPEC_VERSION,
)
from .canonical import (
    SurfaceRealizationCanonicalizationError,
    canonical_json_bytes,
    deterministic_digest,
    stable_identifier,
)
from .identity import (
    expected_candidate_digest,
    expected_candidate_id,
    expected_record_id,
    expected_result_digest,
    expected_result_id,
    with_expected_candidate_identity,
    with_expected_id,
    with_expected_result_identity,
)
from .realizer import (
    applied_resource_records,
    build_realization_segments,
    determine_realization_disposition,
    realize_surface_expression,
)
from .schema import (
    ControlledRealizationResourceBundle,
    ControlledRealizationResourceKind,
    ControlledRealizationResourceRecord,
    SurfaceRealizationAuthorityRecord,
    SurfaceRealizationDisposition,
    SurfaceRealizationFinding,
    SurfaceRealizationFindingKind,
    SurfaceRealizationInput,
    SurfaceRealizationReceipt,
    SurfaceRealizationResult,
    SurfaceRealizationTrace,
    SurfaceRealizationValidationCode,
    SurfaceRealizationValidationError,
    SurfaceRealizationValidationIssue,
    SurfaceRealizationValidationReport,
    UnvalidatedExpressionCandidate,
)
from .validation import (
    assert_valid_surface_realization_input,
    assert_valid_surface_realization_result,
    validate_resource_bundle,
    validate_surface_realization_input,
    validate_surface_realization_result,
)

__all__ = tuple(name for name in globals() if not name.startswith("_"))
