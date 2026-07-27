"""Token-free, reference-only RSOC glyph preview.

This package is intentionally absent from the bootstrap package root.  Import
it explicitly.  Recognition creates no operator, phase, meaning, memory,
route, tool, action, or delivery authority.
"""

from .recognition import (
    build_reference_boundary,
    build_reference_preview_limits,
    default_reference_preview_limits,
    preview_rsoc_operator_references,
)
from .schema import (
    ABSOLUTE_MAX_COVERAGE_SEGMENTS,
    ABSOLUTE_MAX_OPERATOR_REFERENCES,
    DEFAULT_MAX_COVERAGE_SEGMENTS,
    DEFAULT_MAX_OPERATOR_REFERENCES,
    REFERENCE_PREVIEW_SCHEMA_VERSION,
    REFERENCE_PREVIEW_SPEC_ID,
    REFERENCE_PREVIEW_SPEC_VERSION,
    REFERENCE_RECOGNITION_RULESET_ID,
    RsocOperatorReferenceNode,
    RsocReferenceBoundary,
    RsocReferenceDocument,
    RsocReferencePreviewLimits,
    RsocReferencePreviewResult,
    RsocReferencePreviewStatus,
    SourceCoverageKind,
    SourceCoverageSegment,
)
from .validation import (
    validate_operator_reference_node,
    validate_reference_document,
    validate_reference_preview_result,
    validate_source_coverage_segment,
)

__all__ = (
    "ABSOLUTE_MAX_COVERAGE_SEGMENTS",
    "ABSOLUTE_MAX_OPERATOR_REFERENCES",
    "DEFAULT_MAX_COVERAGE_SEGMENTS",
    "DEFAULT_MAX_OPERATOR_REFERENCES",
    "REFERENCE_PREVIEW_SCHEMA_VERSION",
    "REFERENCE_PREVIEW_SPEC_ID",
    "REFERENCE_PREVIEW_SPEC_VERSION",
    "REFERENCE_RECOGNITION_RULESET_ID",
    "RsocOperatorReferenceNode",
    "RsocReferenceBoundary",
    "RsocReferenceDocument",
    "RsocReferencePreviewLimits",
    "RsocReferencePreviewResult",
    "RsocReferencePreviewStatus",
    "SourceCoverageKind",
    "SourceCoverageSegment",
    "build_reference_boundary",
    "build_reference_preview_limits",
    "default_reference_preview_limits",
    "preview_rsoc_operator_references",
    "validate_operator_reference_node",
    "validate_reference_document",
    "validate_reference_preview_result",
    "validate_source_coverage_segment",
)
