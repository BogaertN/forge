"""Immutable in-memory records for MeaningStructureManifest v1 Slice 35A.

These records are constructor-shape contracts only. They intentionally contain
no validation rules, transition authorization, serialization, deserialization,
migration, hashing helpers, filesystem access, persistence, routes, APIs, UI,
network access, model use, resource ingestion, tool invocation, or actions.

Identifiers and free-text semantic atoms are opaque values in Slice 35A. Their
validation and the controlled vocabularies assigned to later architecture
layers are outside this increment.
"""

from __future__ import annotations

from dataclasses import dataclass, field

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
from ._identity import PACKAGE_ID, SCHEMA_ID, SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class LineageRootRecord:
    lineage_id: str
    origin_kind: LineageOriginKind
    origin_ref: str
    direction: SemanticDirection
    record_kind: SemanticRecordKind = field(
        default=SemanticRecordKind.LINEAGE_ROOT, init=False
    )
    lifecycle_state: SemanticLifecycleState = field(
        default=SemanticLifecycleState.LINEAGE_ORIGIN,
        init=False,
    )
    schema_version: str = field(default=SCHEMA_VERSION, init=False)


@dataclass(frozen=True, slots=True)
class CandidateMeaningRecord:
    record_id: str
    lineage_id: str
    source_expression_ref: str
    communicative_act: str
    concept_refs: tuple[str, ...]
    relation_refs: tuple[str, ...]
    meaning_modifiers: tuple[str, ...]
    ambiguity_reasons: tuple[str, ...]
    unresolved_referents: tuple[str, ...]
    authority_sensitive_implications: tuple[str, ...]
    preservation_classes: tuple[SemanticPreservationClass, ...]
    record_kind: SemanticRecordKind = field(
        default=SemanticRecordKind.CANDIDATE_MEANING, init=False
    )
    lifecycle_state: SemanticLifecycleState = field(
        default=SemanticLifecycleState.CANDIDATE_MEANING,
        init=False,
    )
    schema_version: str = field(default=SCHEMA_VERSION, init=False)


@dataclass(frozen=True, slots=True)
class NonSelectionOutcomeRecord:
    record_id: str
    lineage_id: str
    outcome_kind: NonSelectionOutcomeKind
    candidate_refs: tuple[str, ...]
    reasons: tuple[str, ...]
    required_clarifications: tuple[str, ...]
    external_authority_refs: tuple[str, ...]
    record_kind: SemanticRecordKind = field(
        default=SemanticRecordKind.NON_SELECTION_OUTCOME, init=False
    )
    schema_version: str = field(default=SCHEMA_VERSION, init=False)

    @property
    def lifecycle_state(self) -> SemanticLifecycleState:
        return SemanticLifecycleState(self.outcome_kind.value)


@dataclass(frozen=True, slots=True)
class SelectedGovernedMeaningRecord:
    record_id: str
    lineage_id: str
    selected_candidate_ref: str
    selection_authority_ref: str
    communicative_act: str
    concept_refs: tuple[str, ...]
    relation_refs: tuple[str, ...]
    meaning_modifiers: tuple[str, ...]
    inherited_limitations: tuple[str, ...]
    authority_sensitive_distinctions: tuple[str, ...]
    preservation_classes: tuple[SemanticPreservationClass, ...]
    record_kind: SemanticRecordKind = field(
        default=SemanticRecordKind.SELECTED_GOVERNED_MEANING,
        init=False,
    )
    lifecycle_state: SemanticLifecycleState = field(
        default=SemanticLifecycleState.SELECTED_GOVERNED_MEANING,
        init=False,
    )
    schema_version: str = field(default=SCHEMA_VERSION, init=False)


@dataclass(frozen=True, slots=True)
class GovernedResultReferenceRecord:
    record_id: str
    lineage_id: str
    selected_meaning_ref: str
    external_authority_ref: str
    semantic_relevance: str
    record_kind: SemanticRecordKind = field(
        default=SemanticRecordKind.GOVERNED_RESULT_REFERENCE,
        init=False,
    )
    lifecycle_state: SemanticLifecycleState = field(
        default=SemanticLifecycleState.GOVERNED_RESULT_REFERENCED,
        init=False,
    )
    schema_version: str = field(default=SCHEMA_VERSION, init=False)


@dataclass(frozen=True, slots=True)
class GovernedOutwardMeaningRecord:
    record_id: str
    lineage_id: str
    outward_basis_refs: tuple[str, ...]
    prior_selected_meaning_ref: str | None
    permitted_claims: tuple[str, ...]
    required_qualifications: tuple[str, ...]
    prohibited_enlargements: tuple[str, ...]
    external_dependency_refs: tuple[str, ...]
    preservation_classes: tuple[SemanticPreservationClass, ...]
    record_kind: SemanticRecordKind = field(
        default=SemanticRecordKind.GOVERNED_OUTWARD_MEANING,
        init=False,
    )
    lifecycle_state: SemanticLifecycleState = field(
        default=SemanticLifecycleState.GOVERNED_OUTWARD_MEANING,
        init=False,
    )
    schema_version: str = field(default=SCHEMA_VERSION, init=False)


@dataclass(frozen=True, slots=True)
class ExpressionLinkRecord:
    record_id: str
    lineage_id: str
    governed_outward_meaning_ref: str
    expression_candidate_ref: str
    record_kind: SemanticRecordKind = field(
        default=SemanticRecordKind.EXPRESSION_LINK, init=False
    )
    lifecycle_state: SemanticLifecycleState = field(
        default=SemanticLifecycleState.EXPRESSION_LINKED,
        init=False,
    )
    schema_version: str = field(default=SCHEMA_VERSION, init=False)


@dataclass(frozen=True, slots=True)
class ValidationLinkRecord:
    record_id: str
    lineage_id: str
    expression_link_ref: str
    external_validation_receipt_ref: str
    external_validation_disposition: str
    record_kind: SemanticRecordKind = field(
        default=SemanticRecordKind.VALIDATION_LINK, init=False
    )
    lifecycle_state: SemanticLifecycleState = field(
        default=SemanticLifecycleState.VALIDATION_LINKED,
        init=False,
    )
    schema_version: str = field(default=SCHEMA_VERSION, init=False)


@dataclass(frozen=True, slots=True)
class DeliveryContainmentLinkRecord:
    record_id: str
    lineage_id: str
    prior_link_ref: str
    disposition: DeliveryContainmentKind
    external_receipt_ref: str
    record_kind: SemanticRecordKind = field(
        default=SemanticRecordKind.DELIVERY_OR_CONTAINMENT_LINK,
        init=False,
    )
    schema_version: str = field(default=SCHEMA_VERSION, init=False)

    @property
    def lifecycle_state(self) -> SemanticLifecycleState:
        return SemanticLifecycleState(self.disposition.value)


@dataclass(frozen=True, slots=True)
class ExternalAuthorityReferenceRecord:
    record_id: str
    lineage_id: str
    authority_kind: ExternalAuthorityKind
    external_object_ref: str
    semantic_relevance: str
    record_kind: SemanticRecordKind = field(
        default=SemanticRecordKind.EXTERNAL_AUTHORITY_REFERENCE,
        init=False,
    )
    schema_version: str = field(default=SCHEMA_VERSION, init=False)


@dataclass(frozen=True, slots=True)
class SemanticTransitionTraceRecord:
    record_id: str
    lineage_id: str
    from_record_ref: str
    to_record_ref: str
    from_state: SemanticLifecycleState
    to_state: SemanticLifecycleState
    transition_kind: SemanticTransitionKind
    reason: str
    authority_reference_ref: str | None
    record_kind: SemanticRecordKind = field(
        default=SemanticRecordKind.SEMANTIC_TRANSITION_TRACE,
        init=False,
    )
    schema_version: str = field(default=SCHEMA_VERSION, init=False)


@dataclass(frozen=True, slots=True)
class MeaningStructureManifestV1:
    manifest_id: str
    lineage_root: LineageRootRecord
    candidate_meanings: tuple[CandidateMeaningRecord, ...]
    non_selection_outcomes: tuple[NonSelectionOutcomeRecord, ...]
    selected_governed_meanings: tuple[SelectedGovernedMeaningRecord, ...]
    governed_result_references: tuple[GovernedResultReferenceRecord, ...]
    governed_outward_meanings: tuple[GovernedOutwardMeaningRecord, ...]
    expression_links: tuple[ExpressionLinkRecord, ...]
    validation_links: tuple[ValidationLinkRecord, ...]
    delivery_or_containment_links: tuple[DeliveryContainmentLinkRecord, ...]
    external_authority_references: tuple[ExternalAuthorityReferenceRecord, ...]
    semantic_transition_traces: tuple[SemanticTransitionTraceRecord, ...]
    record_kind: SemanticRecordKind = field(
        default=SemanticRecordKind.MEANING_STRUCTURE_MANIFEST, init=False
    )
    package_id: str = field(default=PACKAGE_ID, init=False)
    schema_id: str = field(default=SCHEMA_ID, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
