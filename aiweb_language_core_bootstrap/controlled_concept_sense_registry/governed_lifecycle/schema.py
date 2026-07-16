"""Immutable Slice 37B validation, identity, and lifecycle records.

This subpackage extends the accepted Slice 37A schema with deterministic
validation and lifecycle-law records only.  It does not populate a concept
registry, perform lookup, map a source occurrence, select a sense, create a
semantic relation instance, consume Slice 36 structure, create CandidateMeaning,
access memory, register a route, invoke a tool, render output, or authorize
delivery or action.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final, TypeAlias

from ...schema import stable_record_id
from ..schema import (
    ConceptLifecycleState,
    ConceptNamespaceIdentity,
    ConceptProvenanceReference,
    ConceptResourceKind,
    ControlledConceptIdentity,
    ControlledLexicalReference,
    ControlledSenseIdentity,
    SemanticClassIdentity,
    SemanticRelationFamilyIdentity,
    SemanticRelationTypeIdentity,
    TermConceptMappingIdentity,
)


SLICE37B_SPEC_ID: Final[str] = (
    "aiweb-slice37b-deterministic-validation-identity-lifecycle-law"
)
SLICE37B_SPEC_VERSION: Final[str] = (
    "aiweb-slice37b-deterministic-validation-identity-lifecycle-law-v1"
)
SLICE37B_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-concept-governance-lifecycle-schema-v1"
)
SLICE37B_ACCEPTED_PARENT_HEAD: Final[str] = (
    "432d38eb8829dbf18c05d95e909a69df80229c18"
)
SLICE37B_ACCEPTED_PARENT_TREE: Final[str] = (
    "b0f472458c221ba8f553c3ac170beb254f226e35"
)
SLICE37B_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 37A controlled concept authority schema contract"
)

GovernedConceptResource: TypeAlias = (
    ConceptNamespaceIdentity
    | ControlledConceptIdentity
    | ControlledSenseIdentity
    | ControlledLexicalReference
    | TermConceptMappingIdentity
    | SemanticClassIdentity
    | SemanticRelationFamilyIdentity
    | SemanticRelationTypeIdentity
)


class ConceptLifecycleTransitionKind(str, Enum):
    OBSERVATION_REVIEW = "observation_review"
    NEW_SUPPORT_REVIEW = "new_support_review"
    ADMISSION = "admission"
    ARCHITECTURE_ADMISSION = "architecture_admission"
    OPERATIONAL_BOUNDING = "operational_bounding"
    DEFERMENT = "deferment"
    MARK_UNKNOWN = "mark_unknown"
    MARK_UNRESOLVED = "mark_unresolved"
    MARK_AMBIGUOUS = "mark_ambiguous"
    MARK_UNSUPPORTED = "mark_unsupported"
    MARK_CONFLICTED = "mark_conflicted"
    CORRECTION = "correction"
    DEPRECATION = "deprecation"
    SUPERSESSION = "supersession"
    QUARANTINE = "quarantine"
    CONTINUE_QUARANTINE = "continue_quarantine"
    RELEASE_FROM_QUARANTINE = "release_from_quarantine"
    REJECTION = "rejection"
    REOPEN_REVIEW = "reopen_review"
    CONFLICT_RESOLUTION = "conflict_resolution"
    HISTORICAL_ONLY = "historical_only"


class ConceptGovernanceValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    REQUIRED_VALUE_MISSING = "required_value_missing"
    INVALID_TEXT = "invalid_text"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_NAMESPACE = "invalid_namespace"
    INVALID_VERSION = "invalid_version"
    VERSION_NOT_ADVANCING = "version_not_advancing"
    IDENTITY_MISMATCH = "identity_mismatch"
    LINEAGE_MISMATCH = "lineage_mismatch"
    SCHEMA_VERSION_MISMATCH = "schema_version_mismatch"
    RESOURCE_KIND_MISMATCH = "resource_kind_mismatch"
    PROVENANCE_REQUIRED = "provenance_required"
    PROVENANCE_NOT_FOUND = "provenance_not_found"
    PROVENANCE_INVALID = "provenance_invalid"
    SCOPE_REQUIRED = "scope_required"
    SCOPE_EXPANSION = "scope_expansion"
    PROHIBITED_USE_REQUIRED = "prohibited_use_required"
    LIFECYCLE_STATE_INVALID = "lifecycle_state_invalid"
    TRANSITION_NOT_PERMITTED = "transition_not_permitted"
    TRANSITION_KIND_MISMATCH = "transition_kind_mismatch"
    AUTHORITY_RECORD_NOT_FOUND = "authority_record_not_found"
    AUTHORITY_BINDING_MISMATCH = "authority_binding_mismatch"
    HUMAN_APPROVAL_REQUIRED = "human_approval_required"
    NON_LLM_PROVENANCE_REQUIRED = "non_llm_provenance_required"
    REVIEW_INCOMPLETE = "review_incomplete"
    UNRESOLVED_DEPENDENCY = "unresolved_dependency"
    ADMISSION_HISTORY_REQUIRED = "admission_history_required"
    QUARANTINE_CAUSE_REQUIRED = "quarantine_cause_required"
    QUARANTINE_RELEASE_REQUIREMENT_REQUIRED = (
        "quarantine_release_requirement_required"
    )
    QUARANTINE_CAUSE_UNRESOLVED = "quarantine_cause_unresolved"
    SUPERSEDING_RESOURCE_REQUIRED = "superseding_resource_required"
    SUPERSEDING_RESOURCE_INVALID = "superseding_resource_invalid"
    REJECTION_SCOPE_REQUIRED = "rejection_scope_required"
    BLOCKED_REENTRY_REQUIRED = "blocked_reentry_required"
    VERIFIED_SCOPE_REQUIRED = "verified_scope_required"
    PRIOR_RECORD_NOT_PRESERVED = "prior_record_not_preserved"
    AUTOMATIC_TRANSITION_PROHIBITED = "automatic_transition_prohibited"
    RUNTIME_AUTHORITY_PROHIBITED = "runtime_authority_prohibited"
    IMPLEMENTATION_AUTHORITY_PROHIBITED = "implementation_authority_prohibited"
    REGISTRY_POPULATION_PROHIBITED = "registry_population_prohibited"
    DUPLICATE_RESOURCE_ID = "duplicate_resource_id"
    DUPLICATE_LINEAGE_VERSION = "duplicate_lineage_version"
    CONFLICTING_LINEAGE_VERSION = "conflicting_lineage_version"
    DUPLICATE_TRANSITION_ID = "duplicate_transition_id"
    ORPHAN_RESOURCE_VERSION = "orphan_resource_version"
    MULTIPLE_INCOMING_TRANSITIONS = "multiple_incoming_transitions"
    MULTIPLE_OUTGOING_TRANSITIONS = "multiple_outgoing_transitions"
    REFERENCE_NOT_FOUND = "reference_not_found"
    REFERENCE_KIND_MISMATCH = "reference_kind_mismatch"
    CURRENT_ACTIVE_CONFLICT = "current_active_conflict"
    EXACT_DUPLICATE_RECORD = "exact_duplicate_record"
    DUPLICATE_VALUE = "duplicate_value"
    EXTERNAL_RESOURCE_AUTHORITY_PROHIBITED = (
        "external_resource_authority_prohibited"
    )
    HISTORICAL_ANCESTRY_REQUIRED = "historical_ancestry_required"


@dataclass(frozen=True, slots=True)
class ConceptGovernanceValidationIssue:
    path: str
    code: ConceptGovernanceValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class ConceptGovernanceValidationReport:
    ok: bool
    issues: tuple[ConceptGovernanceValidationIssue, ...]
    schema_version: str = SLICE37B_SCHEMA_VERSION


class ConceptGovernanceValidationError(ValueError):
    """Raised when a Slice 37B governance check fails closed."""

    def __init__(self, report: ConceptGovernanceValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(
            summary or "Slice 37B concept governance validation failed"
        )


@dataclass(frozen=True, slots=True)
class ConceptLifecycleAuthorityRecord:
    authority_id: str
    authority_provenance_ref: str
    decision_owner_ref: str
    human_approval_ref: str
    human_approved: bool
    reason: str
    scope: tuple[str, ...]
    affected_record_refs: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    unresolved_dependency_refs: tuple[str, ...]
    missing_authority_refs: tuple[str, ...]
    conflict_review_complete: bool
    unknown_state_review_complete: bool
    later_dependency_review_complete: bool
    non_llm_provenance: bool
    external_resource_decision_ref: str | None
    runtime_authorized: bool
    implementation_authorized: bool
    registry_population_authorized: bool
    schema_version: str = SLICE37B_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("authority_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37b_concept_lifecycle_authority",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ConceptLifecycleTransitionRecord:
    transition_id: str
    lineage_id: str
    resource_kind: ConceptResourceKind
    source_resource_id: str
    target_resource_id: str
    source_version: str
    target_version: str
    from_state: ConceptLifecycleState
    to_state: ConceptLifecycleState
    transition_kind: ConceptLifecycleTransitionKind
    authority_record_ref: str
    quarantine_cause_refs: tuple[str, ...]
    quarantine_release_requirement_refs: tuple[str, ...]
    resolved_quarantine_cause_refs: tuple[str, ...]
    superseding_resource_ref: str | None
    blocked_reentry_keys: tuple[str, ...]
    verified_scope_refs: tuple[str, ...]
    prior_disposition_transition_ref: str | None
    historical_only_after_transition: bool
    prior_record_preserved: bool
    automatic_transition: bool
    schema_version: str = SLICE37B_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("transition_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37b_concept_lifecycle_transition",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ConceptLifecycleTransitionRule:
    from_state: ConceptLifecycleState
    to_state: ConceptLifecycleState
    allowed_kinds: tuple[ConceptLifecycleTransitionKind, ...]
    authority_required: bool
    human_approval_required: bool
    conflict_review_required: bool
    unknown_review_required: bool
    dependency_review_required: bool
    purpose: str


@dataclass(frozen=True, slots=True)
class ConceptLifecycleTransitionDecision:
    allowed: bool
    issues: tuple[ConceptGovernanceValidationIssue, ...]
    source_resource_id: str
    target_resource_id: str
    transition_id: str
    lineage_id: str
    from_state: ConceptLifecycleState
    to_state: ConceptLifecycleState
    transition_kind: ConceptLifecycleTransitionKind
    schema_version: str = SLICE37B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ConceptGovernanceBatch:
    batch_id: str
    provenance_records: tuple[ConceptProvenanceReference, ...]
    resources: tuple[GovernedConceptResource, ...]
    authority_records: tuple[ConceptLifecycleAuthorityRecord, ...]
    transitions: tuple[ConceptLifecycleTransitionRecord, ...]
    registry_population_installed: bool
    lookup_installed: bool
    occurrence_mapping_installed: bool
    sense_selection_installed: bool
    relation_instance_population_installed: bool
    structural_integration_installed: bool
    runtime_activation_installed: bool
    schema_version: str = SLICE37B_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("batch_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice37b_concept_governance_batch",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
