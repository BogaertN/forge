"""MeaningStructureManifest v1 core schema contract.

Slice 35A provides immutable in-memory records and closed semantic distinctions
only. It does not validate record contents, authorize lifecycle transitions,
serialize data, persist state, connect the bootstrap, or create runtime
language authority.
"""

from ._enums import (
    DeliveryContainmentKind,
    ExternalAuthorityKind,
    LineageOriginKind,
    NonSelectionOutcomeKind,
    SemanticDirection,
    SemanticLifecycleState,
    SemanticPreservationClass,
    SemanticRecordKind,
    SemanticTransitionKind,
)
from ._identity import (
    AUTHORITY_DOCUMENT,
    PACKAGE_ID,
    PACKAGE_NAME,
    SCHEMA_ABBREVIATION,
    SCHEMA_ID,
    SCHEMA_NAME,
    SCHEMA_VERSION,
)
from ._records import (
    CandidateMeaningRecord,
    DeliveryContainmentLinkRecord,
    ExpressionLinkRecord,
    ExternalAuthorityReferenceRecord,
    GovernedOutwardMeaningRecord,
    GovernedResultReferenceRecord,
    LineageRootRecord,
    MeaningStructureManifestV1,
    NonSelectionOutcomeRecord,
    SelectedGovernedMeaningRecord,
    SemanticTransitionTraceRecord,
    ValidationLinkRecord,
)

__all__ = (
    "AUTHORITY_DOCUMENT",
    "CandidateMeaningRecord",
    "DeliveryContainmentKind",
    "DeliveryContainmentLinkRecord",
    "ExpressionLinkRecord",
    "ExternalAuthorityKind",
    "ExternalAuthorityReferenceRecord",
    "GovernedOutwardMeaningRecord",
    "GovernedResultReferenceRecord",
    "LineageOriginKind",
    "LineageRootRecord",
    "MeaningStructureManifestV1",
    "NonSelectionOutcomeKind",
    "NonSelectionOutcomeRecord",
    "PACKAGE_ID",
    "PACKAGE_NAME",
    "SCHEMA_ABBREVIATION",
    "SCHEMA_ID",
    "SCHEMA_NAME",
    "SCHEMA_VERSION",
    "SelectedGovernedMeaningRecord",
    "SemanticDirection",
    "SemanticLifecycleState",
    "SemanticPreservationClass",
    "SemanticRecordKind",
    "SemanticTransitionKind",
    "SemanticTransitionTraceRecord",
    "ValidationLinkRecord",
)
