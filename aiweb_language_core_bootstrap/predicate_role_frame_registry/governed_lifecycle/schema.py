"""Immutable Slice 38B predicate-governance records.

This subpackage extends the accepted Slice 38A record shapes with deterministic
validation, stable lineage identity, exact version compatibility, explicit
lifecycle-transition law, and collection-level integrity checks.  It does not
populate an action-root registry, interpret surface language, select a
predicate, assign roles, complete frames, bind capabilities, invoke routes,
execute actions, access memory, validate evidence, render output, or authorize
delivery.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final, TypeAlias

from ...schema import stable_record_id
from ..schema import (
    ActionRootIdentity,
    PredicateIdentity,
    PredicateLifecycleState,
    PredicateNamespaceIdentity,
    PredicateProvenanceReference,
    PredicateResourceKind,
)


SLICE38B_SPEC_ID: Final[str] = (
    "aiweb-slice38b-deterministic-validation-identity-versioning-lifecycle"
)
SLICE38B_SPEC_VERSION: Final[str] = (
    "aiweb-slice38b-deterministic-validation-identity-versioning-lifecycle-v1"
)
SLICE38B_SCHEMA_VERSION: Final[str] = (
    "aiweb-predicate-governance-lifecycle-schema-v1"
)
SLICE38B_ACCEPTED_PARENT_HEAD: Final[str] = (
    "2809966f62d172cf8660f9acb343a92813e87d2b"
)
SLICE38B_ACCEPTED_PARENT_TREE: Final[str] = (
    "b02d41d21c72e7eae3c39ce04e71286b1b5bcbb0"
)
SLICE38B_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 38A action-root and predicate-identity core schema"
)

GovernedPredicateResource: TypeAlias = (
    PredicateNamespaceIdentity | ActionRootIdentity | PredicateIdentity
)


class PredicateLifecycleTransitionKind(str, Enum):
    PROPOSAL = "proposal"
    REVIEW = "review"
    NEW_SUPPORT_REVIEW = "new_support_review"
    ADMISSION = "admission"
    ARCHITECTURE_ADMISSION = "architecture_admission"
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
    RELEASE_TO_REVIEW = "release_to_review"
    REJECTION = "rejection"
    WITHDRAWAL = "withdrawal"
    REOPEN_REVIEW = "reopen_review"
    CONFLICT_RESOLUTION = "conflict_resolution"


class PredicateGovernanceValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    REQUIRED_VALUE_MISSING = "required_value_missing"
    INVALID_TEXT = "invalid_text"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_NAMESPACE = "invalid_namespace"
    INVALID_VERSION = "invalid_version"
    VERSION_NOT_ADVANCING = "version_not_advancing"
    VERSION_INCOMPATIBLE = "version_incompatible"
    IDENTITY_MISMATCH = "identity_mismatch"
    LINEAGE_MISMATCH = "lineage_mismatch"
    SCHEMA_VERSION_MISMATCH = "schema_version_mismatch"
    RESOURCE_KIND_MISMATCH = "resource_kind_mismatch"
    PROVENANCE_REQUIRED = "provenance_required"
    PROVENANCE_NOT_FOUND = "provenance_not_found"
    PROVENANCE_INVALID = "provenance_invalid"
    SCOPE_REQUIRED = "scope_required"
    NON_SCOPE_REQUIRED = "non_scope_required"
    SCOPE_OVERLAP = "scope_overlap"
    SCOPE_EXPANSION = "scope_expansion"
    NON_SCOPE_NARROWING = "non_scope_narrowing"
    PROHIBITED_USE_REQUIRED = "prohibited_use_required"
    PROHIBITED_USE_REMOVED = "prohibited_use_removed"
    PERMITTED_USE_ADDED = "permitted_use_added"
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
    BLOCKED_REENTRY_REQUIRED = "blocked_reentry_required"
    PRIOR_RECORD_NOT_PRESERVED = "prior_record_not_preserved"
    AUTOMATIC_TRANSITION_PROHIBITED = "automatic_transition_prohibited"
    IN_PLACE_MUTATION_PROHIBITED = "in_place_mutation_prohibited"
    NEAREST_KNOWN_SUBSTITUTION_PROHIBITED = (
        "nearest_known_substitution_prohibited"
    )
    SIMILARITY_AUTHORITY_PROHIBITED = "similarity_authority_prohibited"
    RUNTIME_AUTHORITY_PROHIBITED = "runtime_authority_prohibited"
    IMPLEMENTATION_AUTHORITY_PROHIBITED = "implementation_authority_prohibited"
    REGISTRY_POPULATION_PROHIBITED = "registry_population_prohibited"
    DUPLICATE_RESOURCE_ID = "duplicate_resource_id"
    DUPLICATE_LINEAGE_VERSION = "duplicate_lineage_version"
    CONFLICTING_LINEAGE_VERSION = "conflicting_lineage_version"
    DUPLICATE_TRANSITION_ID = "duplicate_transition_id"
    DUPLICATE_AUTHORITY_ID = "duplicate_authority_id"
    DUPLICATE_PROVENANCE_ID = "duplicate_provenance_id"
    ORPHAN_RESOURCE_VERSION = "orphan_resource_version"
    MULTIPLE_INCOMING_TRANSITIONS = "multiple_incoming_transitions"
    MULTIPLE_OUTGOING_TRANSITIONS = "multiple_outgoing_transitions"
    REFERENCE_NOT_FOUND = "reference_not_found"
    REFERENCE_KIND_MISMATCH = "reference_kind_mismatch"
    CROSS_NAMESPACE_REFERENCE = "cross_namespace_reference"
    CURRENT_ACTIVE_CONFLICT = "current_active_conflict"
    EXACT_DUPLICATE_RECORD = "exact_duplicate_record"
    DUPLICATE_VALUE = "duplicate_value"
    HISTORICAL_ANCESTRY_REQUIRED = "historical_ancestry_required"
    UNKNOWN_STATE_PROMOTION_PROHIBITED = "unknown_state_promotion_prohibited"


@dataclass(frozen=True, slots=True)
class PredicateGovernanceValidationIssue:
    path: str
    code: PredicateGovernanceValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class PredicateGovernanceValidationReport:
    ok: bool
    issues: tuple[PredicateGovernanceValidationIssue, ...]
    schema_version: str = SLICE38B_SCHEMA_VERSION


class PredicateGovernanceValidationError(ValueError):
    """Raised when a Slice 38B governance check fails closed."""

    def __init__(self, report: PredicateGovernanceValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(
            summary or "Slice 38B predicate governance validation failed"
        )


@dataclass(frozen=True, slots=True)
class PredicateLifecycleAuthorityRecord:
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
    version_compatibility_review_complete: bool
    scope_non_scope_review_complete: bool
    provenance_review_complete: bool
    lifecycle_review_complete: bool
    non_llm_provenance: bool
    nearest_known_substitution_allowed: bool
    semantic_similarity_authority_allowed: bool
    runtime_authorized: bool
    implementation_authorized: bool
    registry_population_authorized: bool
    schema_version: str = SLICE38B_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("authority_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice38b_predicate_lifecycle_authority",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredicateLifecycleTransitionRecord:
    transition_id: str
    lineage_id: str
    resource_kind: PredicateResourceKind
    source_resource_id: str
    target_resource_id: str
    source_version: str
    target_version: str
    from_state: PredicateLifecycleState
    to_state: PredicateLifecycleState
    transition_kind: PredicateLifecycleTransitionKind
    authority_record_ref: str
    quarantine_cause_refs: tuple[str, ...]
    quarantine_release_requirement_refs: tuple[str, ...]
    resolved_quarantine_cause_refs: tuple[str, ...]
    superseding_resource_ref: str | None
    blocked_reentry_keys: tuple[str, ...]
    prior_disposition_transition_ref: str | None
    prior_record_preserved: bool
    automatic_transition: bool
    in_place_mutation_performed: bool
    nearest_known_substitution_performed: bool
    similarity_authority_used: bool
    schema_version: str = SLICE38B_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("transition_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice38b_predicate_lifecycle_transition",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredicateLifecycleTransitionRule:
    from_state: PredicateLifecycleState
    to_state: PredicateLifecycleState
    allowed_kinds: tuple[PredicateLifecycleTransitionKind, ...]
    authority_required: bool
    human_approval_required: bool
    conflict_review_required: bool
    unknown_review_required: bool
    dependency_review_required: bool
    purpose: str


@dataclass(frozen=True, slots=True)
class PredicateLifecycleTransitionDecision:
    allowed: bool
    issues: tuple[PredicateGovernanceValidationIssue, ...]
    source_resource_id: str
    target_resource_id: str
    transition_id: str
    lineage_id: str
    from_state: PredicateLifecycleState
    to_state: PredicateLifecycleState
    transition_kind: PredicateLifecycleTransitionKind
    schema_version: str = SLICE38B_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class PredicateGovernanceBatch:
    batch_id: str
    provenance_records: tuple[PredicateProvenanceReference, ...]
    resources: tuple[GovernedPredicateResource, ...]
    authority_records: tuple[PredicateLifecycleAuthorityRecord, ...]
    transitions: tuple[PredicateLifecycleTransitionRecord, ...]
    registry_population_installed: bool
    action_root_lookup_installed: bool
    predicate_selection_installed: bool
    nearest_known_mapping_installed: bool
    semantic_similarity_installed: bool
    capability_routing_installed: bool
    runtime_activation_installed: bool
    schema_version: str = SLICE38B_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("batch_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id(
            "slice38b_predicate_governance_batch",
            self.canonical_body(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
