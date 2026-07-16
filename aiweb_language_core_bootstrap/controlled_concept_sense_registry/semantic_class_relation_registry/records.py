"""Static Slice 37E class, membership, relation-type, and lifecycle records."""

from __future__ import annotations

from dataclasses import replace
from typing import Final, TypeVar

from ..built_in_registry.records import ADMITTED_CONCEPTS, CURRENT_NAMESPACE
from ..governed_lifecycle.identity import (
    expected_resource_lineage_id,
    resource_id,
    with_expected_authority_id,
    with_expected_batch_id,
    with_expected_transition_id,
    with_recomputed_resource_id,
)
from ..governed_lifecycle.schema import (
    ConceptGovernanceBatch,
    ConceptLifecycleAuthorityRecord,
    ConceptLifecycleTransitionKind,
    ConceptLifecycleTransitionRecord,
    GovernedConceptResource,
)
from ..schema import (
    CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    ConceptLifecycleState,
    ConceptProvenanceReference,
    SemanticClassIdentity,
    SemanticRelationFamilyIdentity,
    SemanticRelationTypeIdentity,
)
from ..sense_term_mapping_registry.records import (
    GOVERNANCE_BATCH as SLICE37D_GOVERNANCE_BATCH,
)
from .authority import (
    MEMBERSHIP_DEFINITIONS,
    PROHIBITED_IMPLICATION_KINDS,
    RELATION_FAMILY_DEFINITIONS,
    RELATION_STATE_DEFINITIONS,
    RELATION_TYPE_DEFINITIONS,
    SEMANTIC_CLASS_DEFINITIONS,
    SLICE37E_COMMON_PROHIBITED_USES,
    SLICE37E_DECISION_OWNER_REF,
    SLICE37E_HUMAN_APPROVAL_REF,
    SLICE37E_PROHIBITED_AUTHORITIES,
    SLICE37E_SCOPE_TAGS,
)
from .identity import (
    with_expected_class_definition_id,
    with_expected_family_definition_id,
    with_expected_inverse_declaration_id,
    with_expected_membership_id,
    with_expected_prohibited_implication_id,
    with_expected_relation_state_policy_id,
    with_expected_relation_type_rule_id,
    with_expected_relation_version_id,
)
from .schema import (
    ConceptClassMembershipRule,
    InverseRelationDeclaration,
    ProhibitedImplicationRule,
    RelationFamilyDefinition,
    RelationStatePolicy,
    RelationTypeRule,
    RelationVersionIdentity,
    SemanticClassDefinition,
)


T = TypeVar("T", bound=GovernedConceptResource)


def _with_provenance_id(
    record: ConceptProvenanceReference,
) -> ConceptProvenanceReference:
    return replace(record, provenance_id=record.expected_id())


def _provenance(
    *,
    authority_section: str,
    source_reference: str,
    source_kind: str,
) -> ConceptProvenanceReference:
    return _with_provenance_id(
        ConceptProvenanceReference(
            provenance_id="",
            authority_document=(
                "Document 4 — RMC Concept Lexicon and Semantic Relation Graph v1"
            ),
            authority_section=authority_section,
            source_kind=source_kind,
            source_reference=source_reference,
            version="v1",
            non_llm_provenance=True,
            external_resource_admitted=False,
            runtime_loaded=False,
            prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
        )
    )


CLASS_PROVENANCE_RECORDS: Final[tuple[ConceptProvenanceReference, ...]] = tuple(
    _provenance(
        authority_section=item.authority_section,
        source_reference=item.source_reference,
        source_kind="semantic_class_definition_authority",
    )
    for item in SEMANTIC_CLASS_DEFINITIONS
)

MEMBERSHIP_PROVENANCE_RECORDS: Final[tuple[ConceptProvenanceReference, ...]] = tuple(
    _provenance(
        authority_section=item.authority_section,
        source_reference=item.source_reference,
        source_kind="explicit_concept_class_membership_authority",
    )
    for item in MEMBERSHIP_DEFINITIONS
)

RELATION_FAMILY_PROVENANCE_RECORDS: Final[
    tuple[ConceptProvenanceReference, ...]
] = tuple(
    _provenance(
        authority_section=item.authority_section,
        source_reference=item.source_reference,
        source_kind="semantic_relation_family_authority",
    )
    for item in RELATION_FAMILY_DEFINITIONS
)

RELATION_TYPE_PROVENANCE_RECORDS: Final[
    tuple[ConceptProvenanceReference, ...]
] = tuple(
    _provenance(
        authority_section=item.authority_section,
        source_reference=item.source_reference,
        source_kind="semantic_relation_type_authority",
    )
    for item in RELATION_TYPE_DEFINITIONS
)

RELATION_STATE_PROVENANCE_RECORDS: Final[
    tuple[ConceptProvenanceReference, ...]
] = tuple(
    _provenance(
        authority_section=item.authority_section,
        source_reference=item.source_reference,
        source_kind="semantic_relation_state_policy_authority",
    )
    for item in RELATION_STATE_DEFINITIONS
)

INVERSE_PROVENANCE: Final[ConceptProvenanceReference] = _provenance(
    authority_section="Document 4, Sections 30.18–30.19",
    source_reference="document4:sections30.18-30.19:explicit-component-composition-inverse-pair",
    source_kind="explicit_inverse_relation_declaration_authority",
)

PROHIBITED_IMPLICATION_PROVENANCE: Final[ConceptProvenanceReference] = _provenance(
    authority_section="Document 4, Sections 23–31 and permanent authority boundaries",
    source_reference="document4:semantic-class-relation-prohibited-implications",
    source_kind="prohibited_semantic_implication_authority",
)

NEW_PROVENANCE_RECORDS: Final[tuple[ConceptProvenanceReference, ...]] = (
    *CLASS_PROVENANCE_RECORDS,
    *MEMBERSHIP_PROVENANCE_RECORDS,
    *RELATION_FAMILY_PROVENANCE_RECORDS,
    *RELATION_TYPE_PROVENANCE_RECORDS,
    *RELATION_STATE_PROVENANCE_RECORDS,
    INVERSE_PROVENANCE,
    PROHIBITED_IMPLICATION_PROVENANCE,
)


CONCEPT_BY_KEY: Final[dict[str, object]] = {
    item.concept_key: item for item in ADMITTED_CONCEPTS
}


def _class_identity(definition, provenance, *, version, state):
    return with_recomputed_resource_id(
        SemanticClassIdentity(
            semantic_class_id="",
            namespace_id=CURRENT_NAMESPACE.namespace_id,
            class_key=definition.class_key,
            label=definition.label,
            definition=definition.definition,
            parent_class_refs=(),
            version=version,
            lifecycle_state=state,
            provenance_ref=provenance.provenance_id,
            prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
        )
    )


def _family_identity(definition, provenance, *, version, state):
    return with_recomputed_resource_id(
        SemanticRelationFamilyIdentity(
            relation_family_id="",
            namespace_id=CURRENT_NAMESPACE.namespace_id,
            family_key=definition.family_key,
            label=definition.label,
            definition=definition.definition,
            version=version,
            lifecycle_state=state,
            provenance_ref=provenance.provenance_id,
            prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
        )
    )


def _three_stage(factory, definition, provenance):
    return (
        factory(
            definition,
            provenance,
            version="v1",
            state=ConceptLifecycleState.OBSERVED,
        ),
        factory(
            definition,
            provenance,
            version="v2",
            state=ConceptLifecycleState.CANDIDATE,
        ),
        factory(
            definition,
            provenance,
            version="v3",
            state=ConceptLifecycleState.ARCHITECTURE_ADMITTED,
        ),
    )


CLASS_HISTORIES: Final[tuple[tuple[SemanticClassIdentity, ...], ...]] = tuple(
    _three_stage(_class_identity, definition, provenance)
    for definition, provenance in zip(
        SEMANTIC_CLASS_DEFINITIONS,
        CLASS_PROVENANCE_RECORDS,
        strict=True,
    )
)
CURRENT_SEMANTIC_CLASSES: Final[tuple[SemanticClassIdentity, ...]] = tuple(
    history[-1] for history in CLASS_HISTORIES
)
SEMANTIC_CLASS_BY_KEY: Final[dict[str, SemanticClassIdentity]] = {
    definition.class_key: record
    for definition, record in zip(
        SEMANTIC_CLASS_DEFINITIONS,
        CURRENT_SEMANTIC_CLASSES,
        strict=True,
    )
}

# Parent references are intentionally represented only in the class definitions.
# They do not automatically create inherited class membership.
CLASS_DEFINITIONS: Final[tuple[SemanticClassDefinition, ...]] = tuple(
    with_expected_class_definition_id(
        SemanticClassDefinition(
            definition_id="",
            semantic_class_ref=record.semantic_class_id,
            class_level=definition.class_level,
            parent_class_refs=tuple(
                SEMANTIC_CLASS_BY_KEY[key].semantic_class_id
                for key in definition.parent_class_keys
            ),
            inclusion_rules=definition.inclusion_rules,
            exclusion_rules=definition.exclusion_rules,
            scope_tags=SLICE37E_SCOPE_TAGS,
            multiple_membership_permitted=definition.multiple_membership_permitted,
            class_membership_creates_authority=False,
            class_membership_creates_relation_instance=False,
            prohibited_implication_refs=(),
            provenance_ref=provenance.provenance_id,
            version="v1",
        )
    )
    for definition, record, provenance in zip(
        SEMANTIC_CLASS_DEFINITIONS,
        CURRENT_SEMANTIC_CLASSES,
        CLASS_PROVENANCE_RECORDS,
        strict=True,
    )
)

FAMILY_HISTORIES: Final[
    tuple[tuple[SemanticRelationFamilyIdentity, ...], ...]
] = tuple(
    _three_stage(_family_identity, definition, provenance)
    for definition, provenance in zip(
        RELATION_FAMILY_DEFINITIONS,
        RELATION_FAMILY_PROVENANCE_RECORDS,
        strict=True,
    )
)
CURRENT_RELATION_FAMILIES: Final[
    tuple[SemanticRelationFamilyIdentity, ...]
] = tuple(history[-1] for history in FAMILY_HISTORIES)
RELATION_FAMILY_BY_KEY: Final[dict[str, SemanticRelationFamilyIdentity]] = {
    definition.family_key: record
    for definition, record in zip(
        RELATION_FAMILY_DEFINITIONS,
        CURRENT_RELATION_FAMILIES,
        strict=True,
    )
}


def _relation_type_identity(definition, provenance, *, version, state):
    return with_recomputed_resource_id(
        SemanticRelationTypeIdentity(
            relation_type_id="",
            relation_family_id=(
                RELATION_FAMILY_BY_KEY[definition.family_key].relation_family_id
            ),
            namespace_id=CURRENT_NAMESPACE.namespace_id,
            relation_key=definition.relation_key,
            label=definition.label,
            definition=definition.definition,
            direction=definition.direction,
            domain_class_refs=tuple(
                SEMANTIC_CLASS_BY_KEY[key].semantic_class_id
                for key in definition.domain_class_keys
            ),
            range_class_refs=tuple(
                SEMANTIC_CLASS_BY_KEY[key].semantic_class_id
                for key in definition.range_class_keys
            ),
            # The inverse pair is governed by a separate declaration to avoid
            # circular identity hashes and to preserve declaration ancestry.
            inverse_relation_type_ref=None,
            version=version,
            lifecycle_state=state,
            provenance_ref=provenance.provenance_id,
            relation_instances_populated=False,
            prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
        )
    )


RELATION_TYPE_HISTORIES: Final[
    tuple[tuple[SemanticRelationTypeIdentity, ...], ...]
] = tuple(
    _three_stage(_relation_type_identity, definition, provenance)
    for definition, provenance in zip(
        RELATION_TYPE_DEFINITIONS,
        RELATION_TYPE_PROVENANCE_RECORDS,
        strict=True,
    )
)
CURRENT_RELATION_TYPES: Final[tuple[SemanticRelationTypeIdentity, ...]] = tuple(
    history[-1] for history in RELATION_TYPE_HISTORIES
)
RELATION_TYPE_BY_KEY: Final[dict[str, SemanticRelationTypeIdentity]] = {
    definition.relation_key: record
    for definition, record in zip(
        RELATION_TYPE_DEFINITIONS,
        CURRENT_RELATION_TYPES,
        strict=True,
    )
}


PROHIBITED_IMPLICATIONS: Final[tuple[ProhibitedImplicationRule, ...]] = tuple(
    with_expected_prohibited_implication_id(
        ProhibitedImplicationRule(
            implication_rule_id="",
            implication_kind=kind,
            allowed=False,
            reason=(
                f"{kind.value} is prohibited. Slice 37E may organize semantic "
                "resources and evaluate relation-type eligibility only."
            ),
            provenance_ref=PROHIBITED_IMPLICATION_PROVENANCE.provenance_id,
        )
    )
    for kind in PROHIBITED_IMPLICATION_KINDS
)
PROHIBITED_IMPLICATION_BY_KIND: Final[dict[object, ProhibitedImplicationRule]] = {
    item.implication_kind: item for item in PROHIBITED_IMPLICATIONS
}
CLASS_MEMBERSHIP_PROHIBITED_REFS: Final[tuple[str, ...]] = tuple(
    PROHIBITED_IMPLICATION_BY_KIND[kind].implication_rule_id
    for kind in PROHIBITED_IMPLICATION_KINDS[:8]
)
RELATION_PROHIBITED_REFS: Final[tuple[str, ...]] = tuple(
    PROHIBITED_IMPLICATION_BY_KIND[kind].implication_rule_id
    for kind in PROHIBITED_IMPLICATION_KINDS[8:]
)

# Rebuild class definitions with the final prohibited implication references.
CLASS_DEFINITIONS = tuple(
    with_expected_class_definition_id(
        replace(
            record,
            definition_id="",
            prohibited_implication_refs=CLASS_MEMBERSHIP_PROHIBITED_REFS,
        )
    )
    for record in CLASS_DEFINITIONS
)

MEMBERSHIPS: Final[tuple[ConceptClassMembershipRule, ...]] = tuple(
    with_expected_membership_id(
        ConceptClassMembershipRule(
            membership_id="",
            concept_ref=CONCEPT_BY_KEY[definition.concept_key].concept_id,
            semantic_class_ref=(
                SEMANTIC_CLASS_BY_KEY[definition.class_key].semantic_class_id
            ),
            membership_basis=definition.membership_basis,
            scope_tags=SLICE37E_SCOPE_TAGS,
            version="v1",
            lifecycle_state=ConceptLifecycleState.ARCHITECTURE_ADMITTED,
            provenance_ref=provenance.provenance_id,
            creates_evidence_authority=False,
            creates_memory_authority=False,
            creates_permission_authority=False,
            creates_action_authority=False,
            creates_delivery_authority=False,
            creates_identity_authority=False,
            creates_runtime_authority=False,
            creates_economic_authority=False,
            creates_relation_instance=False,
            prohibited_implication_refs=CLASS_MEMBERSHIP_PROHIBITED_REFS,
        )
    )
    for definition, provenance in zip(
        MEMBERSHIP_DEFINITIONS,
        MEMBERSHIP_PROVENANCE_RECORDS,
        strict=True,
    )
)

RELATION_TYPES_BY_FAMILY_KEY: Final[dict[str, tuple[str, ...]]] = {
    family.family_key: tuple(
        RELATION_TYPE_BY_KEY[item.relation_key].relation_type_id
        for item in RELATION_TYPE_DEFINITIONS
        if item.family_key == family.family_key
    )
    for family in RELATION_FAMILY_DEFINITIONS
}

RELATION_FAMILY_DEFINITION_RECORDS: Final[
    tuple[RelationFamilyDefinition, ...]
] = tuple(
    with_expected_family_definition_id(
        RelationFamilyDefinition(
            definition_id="",
            relation_family_ref=record.relation_family_id,
            relationship_domain=definition.relationship_domain,
            eligible_resource_kinds=definition.eligible_resource_kinds,
            scope_tags=SLICE37E_SCOPE_TAGS,
            relation_type_refs=RELATION_TYPES_BY_FAMILY_KEY[definition.family_key],
            relation_instances_admitted=False,
            prohibited_implication_refs=RELATION_PROHIBITED_REFS,
            provenance_ref=provenance.provenance_id,
            version="v1",
        )
    )
    for definition, record, provenance in zip(
        RELATION_FAMILY_DEFINITIONS,
        CURRENT_RELATION_FAMILIES,
        RELATION_FAMILY_PROVENANCE_RECORDS,
        strict=True,
    )
)

COMPONENT = RELATION_TYPE_BY_KEY["conceptual_component_of"]
COMPOSITION = RELATION_TYPE_BY_KEY["conceptually_composed_of"]
INVERSE_DECLARATIONS: Final[tuple[InverseRelationDeclaration, ...]] = (
    with_expected_inverse_declaration_id(
        InverseRelationDeclaration(
            declaration_id="",
            relation_type_ref=COMPONENT.relation_type_id,
            inverse_relation_type_ref=COMPOSITION.relation_type_id,
            explicitly_authorized=True,
            reciprocal_pair=True,
            creates_relation_instance=False,
            source_reference=(
                "Document 4 Sections 30.18 and 30.19 separately establish the "
                "conceptual-component and conceptual-composition families, with "
                "Section 30.19 describing composition as inverse-facing to component."
            ),
            provenance_ref=INVERSE_PROVENANCE.provenance_id,
            version="v1",
        )
    ),
)
INVERSE_DECLARATION = INVERSE_DECLARATIONS[0]

RELATION_TYPE_RULES: Final[tuple[RelationTypeRule, ...]] = tuple(
    with_expected_relation_type_rule_id(
        RelationTypeRule(
            rule_id="",
            relation_type_ref=record.relation_type_id,
            permitted_domain_class_refs=record.domain_class_refs,
            permitted_range_class_refs=record.range_class_refs,
            direction=definition.direction,
            symmetry=definition.symmetry,
            inverse_declaration_ref=(
                INVERSE_DECLARATION.declaration_id
                if definition.inverse_relation_key is not None
                else None
            ),
            scope_tags=SLICE37E_SCOPE_TAGS,
            sense_bounded_participation_required=(
                definition.sense_bounded_participation_required
            ),
            status_sensitive=definition.status_sensitive,
            ancestry_sensitive=definition.ancestry_sensitive,
            conditional=definition.conditional,
            relation_instances_admitted=False,
            truth_determined=False,
            evidence_sufficiency_determined=False,
            verified_status_applied=False,
            implementation_determined=False,
            prohibited_implication_refs=RELATION_PROHIBITED_REFS,
            provenance_ref=provenance.provenance_id,
            version="v1",
        )
    )
    for definition, record, provenance in zip(
        RELATION_TYPE_DEFINITIONS,
        CURRENT_RELATION_TYPES,
        RELATION_TYPE_PROVENANCE_RECORDS,
        strict=True,
    )
)

RELATION_VERSIONS: Final[tuple[RelationVersionIdentity, ...]] = tuple(
    with_expected_relation_version_id(
        RelationVersionIdentity(
            relation_version_id="",
            relation_type_ref=history[-1].relation_type_id,
            relation_lineage_ref=expected_resource_lineage_id(history[-1]),
            current_version=history[-1].version,
            predecessor_version_refs=tuple(
                item.relation_type_id for item in history[:-1]
            ),
            current=True,
            provenance_ref=history[-1].provenance_ref,
        )
    )
    for history in RELATION_TYPE_HISTORIES
)

RELATION_STATE_POLICIES: Final[tuple[RelationStatePolicy, ...]] = tuple(
    with_expected_relation_state_policy_id(
        RelationStatePolicy(
            state_policy_id="",
            state_kind=definition.state_kind,
            definition=definition.definition,
            permitted_uses=definition.permitted_uses,
            prohibited_repairs=definition.prohibited_repairs,
            creates_relation_instance=False,
            determines_truth=False,
            authorizes_consequence=False,
            provenance_ref=provenance.provenance_id,
            version="v1",
        )
    )
    for definition, provenance in zip(
        RELATION_STATE_DEFINITIONS,
        RELATION_STATE_PROVENANCE_RECORDS,
        strict=True,
    )
)


def _authority(source, target, provenance, *, final):
    return with_expected_authority_id(
        ConceptLifecycleAuthorityRecord(
            authority_id="",
            authority_provenance_ref=provenance.provenance_id,
            decision_owner_ref=SLICE37E_DECISION_OWNER_REF,
            human_approval_ref=SLICE37E_HUMAN_APPROVAL_REF,
            human_approved=True,
            reason=(
                "Preserve one explicit Slice 37E semantic-class, relation-family, "
                "or relation-type lifecycle transition without runtime authority."
            ),
            scope=(target.namespace_id,),
            affected_record_refs=(resource_id(source), resource_id(target)),
            prohibited_uses=SLICE37E_COMMON_PROHIBITED_USES,
            unresolved_dependency_refs=(),
            missing_authority_refs=(),
            conflict_review_complete=final,
            unknown_state_review_complete=final,
            later_dependency_review_complete=final,
            non_llm_provenance=True,
            external_resource_decision_ref=None,
            runtime_authorized=False,
            implementation_authorized=False,
            registry_population_authorized=False,
        )
    )


def _transition(source, target, authority, *, kind):
    return with_expected_transition_id(
        ConceptLifecycleTransitionRecord(
            transition_id="",
            lineage_id=expected_resource_lineage_id(source),
            resource_kind=source.resource_kind,
            source_resource_id=resource_id(source),
            target_resource_id=resource_id(target),
            source_version=source.version,
            target_version=target.version,
            from_state=source.lifecycle_state,
            to_state=target.lifecycle_state,
            transition_kind=kind,
            authority_record_ref=authority.authority_id,
            quarantine_cause_refs=(),
            quarantine_release_requirement_refs=(),
            resolved_quarantine_cause_refs=(),
            superseding_resource_ref=None,
            blocked_reentry_keys=(),
            verified_scope_refs=(),
            prior_disposition_transition_ref=None,
            historical_only_after_transition=False,
            prior_record_preserved=True,
            automatic_transition=False,
        )
    )


def _history_governance(history, provenance):
    observed, candidate, admitted = history
    first_authority = _authority(observed, candidate, provenance, final=False)
    final_authority = _authority(candidate, admitted, provenance, final=True)
    return (
        (first_authority, final_authority),
        (
            _transition(
                observed,
                candidate,
                first_authority,
                kind=ConceptLifecycleTransitionKind.OBSERVATION_REVIEW,
            ),
            _transition(
                candidate,
                admitted,
                final_authority,
                kind=ConceptLifecycleTransitionKind.ARCHITECTURE_ADMISSION,
            ),
        ),
    )


NEW_HISTORY_PROVENANCE_GROUPS = (
    *zip(CLASS_HISTORIES, CLASS_PROVENANCE_RECORDS, strict=True),
    *zip(FAMILY_HISTORIES, RELATION_FAMILY_PROVENANCE_RECORDS, strict=True),
    *zip(RELATION_TYPE_HISTORIES, RELATION_TYPE_PROVENANCE_RECORDS, strict=True),
)
NEW_GOVERNANCE_GROUPS = tuple(
    _history_governance(history, provenance)
    for history, provenance in NEW_HISTORY_PROVENANCE_GROUPS
)
NEW_AUTHORITIES: Final[tuple[ConceptLifecycleAuthorityRecord, ...]] = tuple(
    item for authorities, _ in NEW_GOVERNANCE_GROUPS for item in authorities
)
NEW_TRANSITIONS: Final[tuple[ConceptLifecycleTransitionRecord, ...]] = tuple(
    item for _, transitions in NEW_GOVERNANCE_GROUPS for item in transitions
)
NEW_RESOURCES: Final[tuple[GovernedConceptResource, ...]] = tuple(
    item
    for history, _ in NEW_HISTORY_PROVENANCE_GROUPS
    for item in history
)

GOVERNANCE_BATCH: Final[ConceptGovernanceBatch] = with_expected_batch_id(
    ConceptGovernanceBatch(
        batch_id="",
        provenance_records=(
            *SLICE37D_GOVERNANCE_BATCH.provenance_records,
            *NEW_PROVENANCE_RECORDS,
        ),
        resources=(
            *SLICE37D_GOVERNANCE_BATCH.resources,
            *NEW_RESOURCES,
        ),
        authority_records=(
            *SLICE37D_GOVERNANCE_BATCH.authority_records,
            *NEW_AUTHORITIES,
        ),
        transitions=(
            *SLICE37D_GOVERNANCE_BATCH.transitions,
            *NEW_TRANSITIONS,
        ),
        registry_population_installed=False,
        lookup_installed=False,
        occurrence_mapping_installed=False,
        sense_selection_installed=False,
        relation_instance_population_installed=False,
        structural_integration_installed=False,
        runtime_activation_installed=False,
    )
)
