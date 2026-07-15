"""Slice 36B deterministic source-field projection.

Explicit import only. The package projects exact Slice 36A source custody into
reversible, non-semantic source records linked to the inert Slice 36B0 field
contract. Importing this package performs no projection and grants no operator,
phase, meaning, memory, route, tool, action, rendering, or delivery authority.
"""

from .projection import (
    build_source_field_projection_limits,
    default_source_field_projection_limits,
    project_source_field,
)
from .reconstruction import reconstruct_source_field
from .schema import (
    ABSOLUTE_MAX_PROJECTION_CODE_POINTS,
    ABSOLUTE_MAX_PROJECTION_OBSERVATIONS,
    DEFAULT_MAX_PROJECTION_CODE_POINTS,
    DEFAULT_MAX_PROJECTION_OBSERVATIONS,
    GRAPHEME_PROFILE_ID,
    PROJECTION_RULESET_ID,
    PROJECTION_RULESET_VERSION,
    PROJECTION_SCHEMA_VERSION,
    PROJECTION_SPEC_ID,
    PROJECTION_SPEC_VERSION,
    SOURCE_FIELD_SCHEMA_ID,
    UNICODE_DATABASE_VERSION,
    GraphemeBoundaryStatus,
    GraphemeProfileStatus,
    SourceBoundaryRecord,
    SourceCodePointRecord,
    SourceFieldProjectionLimits,
    SourceFieldProjectionRecord,
    SourceFieldProjectionResult,
    SourceFieldProjectionStatus,
    SourceFieldReconstructionResult,
    SourceFieldSupportStatus,
    SourceObservationKind,
    SourceObservationRecord,
)
from .validation import (
    validate_source_boundary_record,
    validate_source_code_point_record,
    validate_source_field_projection,
    validate_source_field_projection_limits,
    validate_source_field_projection_result,
    validate_source_field_reconstruction_result,
    validate_source_observation_record,
)

__all__ = (
    "ABSOLUTE_MAX_PROJECTION_CODE_POINTS",
    "ABSOLUTE_MAX_PROJECTION_OBSERVATIONS",
    "DEFAULT_MAX_PROJECTION_CODE_POINTS",
    "DEFAULT_MAX_PROJECTION_OBSERVATIONS",
    "GRAPHEME_PROFILE_ID",
    "PROJECTION_RULESET_ID",
    "PROJECTION_RULESET_VERSION",
    "PROJECTION_SCHEMA_VERSION",
    "PROJECTION_SPEC_ID",
    "PROJECTION_SPEC_VERSION",
    "SOURCE_FIELD_SCHEMA_ID",
    "UNICODE_DATABASE_VERSION",
    "GraphemeBoundaryStatus",
    "GraphemeProfileStatus",
    "SourceBoundaryRecord",
    "SourceCodePointRecord",
    "SourceFieldProjectionLimits",
    "SourceFieldProjectionRecord",
    "SourceFieldProjectionResult",
    "SourceFieldProjectionStatus",
    "SourceFieldReconstructionResult",
    "SourceFieldSupportStatus",
    "SourceObservationKind",
    "SourceObservationRecord",
    "build_source_field_projection_limits",
    "default_source_field_projection_limits",
    "project_source_field",
    "reconstruct_source_field",
    "validate_source_boundary_record",
    "validate_source_code_point_record",
    "validate_source_field_projection",
    "validate_source_field_projection_limits",
    "validate_source_field_projection_result",
    "validate_source_field_reconstruction_result",
    "validate_source_observation_record",
)
