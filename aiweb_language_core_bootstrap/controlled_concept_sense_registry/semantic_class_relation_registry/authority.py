"""Human-approved Slice 37E semantic-class and relation-type authority.

The closed set is derived from the four admitted Slice 37C concepts, the five
Slice 37D senses, the exact post-Slice-37D source packet, and Document 4.  It is
not derived from a general ontology, an external taxonomy, lexical similarity,
embeddings, a model, graph completion, or relation extraction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from ..schema import RelationDirection
from .schema import (
    ProhibitedImplicationKind,
    RelationStateKind,
    RelationSymmetry,
    SemanticClassLevel,
)


SLICE37E_DECISION_OWNER_REF: Final[str] = "nicholas-jacob-bogaert"
SLICE37E_HUMAN_APPROVAL_REF: Final[str] = (
    "aiweb-slice37e-decision-owner-semantic-class-relation-type-"
    "closed-set-and-application-authorization"
)

SLICE37E_SCOPE_TAGS: Final[tuple[str, ...]] = (
    "namespace:aiweb:language-core:concept-registry",
    "domain:forge-language-core",
    "slice:37e",
    "layer:structural-semantic-organization",
)

SLICE37E_PROHIBITED_AUTHORITIES: Final[tuple[str, ...]] = (
    "semantic class is not concept definition",
    "semantic class is not authority class",
    "class membership is not evidence authority",
    "class membership is not memory authority",
    "class membership is not permission or action authority",
    "class membership is not delivery authority",
    "class membership is not identity authority",
    "class membership is not runtime authority",
    "class membership is not economic authority",
    "semantic relation family is not relation fact",
    "semantic relation type is not relation fact",
    "relation eligibility is not a relation instance",
    "relation instance is not truth",
    "source relation is not source reliability",
    "evidence relation is not evidence validity",
    "verification relation is not verified status",
    "status relation is not status application",
    "architecture relation is not implementation",
    "class or relation is not automatic inheritance",
    "registry availability is not structural integration",
    "registry availability is not CandidateMeaning authority",
)

SLICE37E_COMMON_PROHIBITED_USES: Final[tuple[str, ...]] = (
    "create or infer a relation instance",
    "assert a relation fact",
    "determine truth or falsity",
    "determine source reliability",
    "validate evidence or evidence sufficiency",
    "apply verification or implementation status",
    "select an occurrence-level concept or sense",
    "construct CandidateMeaning or selected meaning",
    "consume or alter Slice 36 structure",
    "infer class membership by parent, label, term, or resemblance",
    "infer relation type by lexical similarity or graph completion",
    "import an external class system or ontology",
    "use an LLM, embedding, vector, RAG, neural parser, or learned classifier",
    "authorize permission, action, tool, memory, identity, delivery, or economics",
    "register routes, activate runtime, render language, or deliver output",
)

SLICE37E_REGISTRY_AUTHORITY_LIMITATIONS: Final[tuple[str, ...]] = (
    "the closed class set organizes only the four admitted Slice 37C concepts",
    "membership is explicit and never inferred through inheritance",
    "multiple class membership is permitted only where explicitly recorded",
    "relation families and types are structural categories only",
    "domain and range checks establish type eligibility only",
    "the inverse declaration does not create either reciprocal relation fact",
    "symmetric relation type does not assert any symmetric relation instance",
    "unknown, unsupported, conflicted, and prohibited-expansion states are first class",
    "zero relation instances are populated by Slice 37E",
    "structural-to-concept proposal remains deferred to Slice 37F",
)


@dataclass(frozen=True, slots=True)
class SemanticClassDefinitionAuthority:
    class_key: str
    label: str
    definition: str
    class_level: SemanticClassLevel
    inclusion_rules: tuple[str, ...]
    exclusion_rules: tuple[str, ...]
    parent_class_keys: tuple[str, ...]
    multiple_membership_permitted: bool
    authority_section: str
    source_reference: str


@dataclass(frozen=True, slots=True)
class MembershipDefinitionAuthority:
    concept_key: str
    class_key: str
    membership_basis: tuple[str, ...]
    authority_section: str
    source_reference: str


@dataclass(frozen=True, slots=True)
class RelationFamilyDefinitionAuthority:
    family_key: str
    label: str
    definition: str
    relationship_domain: str
    eligible_resource_kinds: tuple[str, ...]
    authority_section: str
    source_reference: str


@dataclass(frozen=True, slots=True)
class RelationTypeDefinitionAuthority:
    relation_key: str
    family_key: str
    label: str
    definition: str
    domain_class_keys: tuple[str, ...]
    range_class_keys: tuple[str, ...]
    direction: RelationDirection
    symmetry: RelationSymmetry
    inverse_relation_key: str | None
    sense_bounded_participation_required: bool
    status_sensitive: bool
    ancestry_sensitive: bool
    conditional: bool
    authority_section: str
    source_reference: str


@dataclass(frozen=True, slots=True)
class RelationStateDefinitionAuthority:
    state_kind: RelationStateKind
    definition: str
    permitted_uses: tuple[str, ...]
    prohibited_repairs: tuple[str, ...]
    authority_section: str
    source_reference: str


ALL_CLASS_KEYS: Final[tuple[str, ...]] = (
    "type_or_category_concept",
    "expression_representation_communication_concept",
    "occurrence_event_or_change_concept",
    "action_type_concept",
    "state_or_condition_concept",
    "unknown_unclassified_or_foundationally_unsupported_concept",
)

SEMANTIC_CLASS_DEFINITIONS: Final[
    tuple[SemanticClassDefinitionAuthority, ...]
] = (
    SemanticClassDefinitionAuthority(
        class_key="type_or_category_concept",
        label="Type or Category Concept",
        definition=(
            "A foundational semantic class for governed concepts whose bounded "
            "meaning identifies a type, category, or semantic-resource kind."
        ),
        class_level=SemanticClassLevel.FOUNDATIONAL,
        inclusion_rules=(
            "the concept definition identifies a governed type or category",
            "membership is supported by the admitted concept definition",
        ),
        exclusion_rules=(
            "visible term form alone is insufficient",
            "membership does not create concept or identity authority",
        ),
        parent_class_keys=(),
        multiple_membership_permitted=True,
        authority_section="Document 4, Section 24 — Foundational Semantic-Class Families",
        source_reference="document4:section24:type-or-category-concept-family",
    ),
    SemanticClassDefinitionAuthority(
        class_key="expression_representation_communication_concept",
        label="Expression, Representation or Communication Concept",
        definition=(
            "A foundational semantic class for governed concepts concerning "
            "expression form, representation, communication, or semantic carriage."
        ),
        class_level=SemanticClassLevel.FOUNDATIONAL,
        inclusion_rules=(
            "the concept definition concerns preserved expression or representation",
            "membership remains separate from interpretation and rendering",
        ),
        exclusion_rules=(
            "membership does not select what an occurrence means",
            "membership does not validate or deliver an expression",
        ),
        parent_class_keys=(),
        multiple_membership_permitted=True,
        authority_section="Document 4, Section 24 — Foundational Semantic-Class Families",
        source_reference="document4:section24:expression-representation-communication-family",
    ),
    SemanticClassDefinitionAuthority(
        class_key="occurrence_event_or_change_concept",
        label="Occurrence, Event or Change Concept",
        definition=(
            "A foundational semantic class for governed concepts whose bounded "
            "meaning concerns an occurrence, event, transition, or change."
        ),
        class_level=SemanticClassLevel.FOUNDATIONAL,
        inclusion_rules=(
            "the concept definition identifies an occurrence or state transition",
            "the occurrence remains semantic structure rather than proof it occurred",
        ),
        exclusion_rules=(
            "membership does not assert that an event happened",
            "membership does not create runtime transition authority",
        ),
        parent_class_keys=(),
        multiple_membership_permitted=True,
        authority_section="Document 4, Section 24 — Foundational Semantic-Class Families",
        source_reference="document4:section24:occurrence-event-change-family",
    ),
    SemanticClassDefinitionAuthority(
        class_key="action_type_concept",
        label="Action-Type Concept",
        definition=(
            "A specialized semantic class for governed concepts that identify a "
            "kind of act or operation without supplying intent, roles, permission, "
            "capability, execution, or proof that an act occurred."
        ),
        class_level=SemanticClassLevel.SPECIALIZED,
        inclusion_rules=(
            "the admitted concept definition identifies an act or operation type",
            "classification remains non-operative and non-permissive",
        ),
        exclusion_rules=(
            "membership does not create a predicate or participant-role frame",
            "membership does not authorize execution or capability use",
        ),
        parent_class_keys=("occurrence_event_or_change_concept",),
        multiple_membership_permitted=True,
        authority_section="Document 4, Section 26 — Action-Type Concept Class Family",
        source_reference="document4:section26:action-type-concept-family",
    ),
    SemanticClassDefinitionAuthority(
        class_key="state_or_condition_concept",
        label="State or Condition Concept",
        definition=(
            "A foundational semantic class for governed concepts whose bounded "
            "meaning identifies a state, condition, or unresolved condition."
        ),
        class_level=SemanticClassLevel.FOUNDATIONAL,
        inclusion_rules=(
            "the concept definition identifies a semantic state or condition",
            "state membership remains distinct from status application",
        ),
        exclusion_rules=(
            "membership does not establish external status",
            "membership does not resolve the represented condition",
        ),
        parent_class_keys=(),
        multiple_membership_permitted=True,
        authority_section="Document 4, Section 24 — Foundational Semantic-Class Families",
        source_reference="document4:section24:state-condition-family",
    ),
    SemanticClassDefinitionAuthority(
        class_key="unknown_unclassified_or_foundationally_unsupported_concept",
        label="Unknown, Unclassified or Foundationally Unsupported Concept",
        definition=(
            "A foundational semantic class preserving concepts whose bounded "
            "meaning concerns unknown, unclassified, or unsupported semantic status."
        ),
        class_level=SemanticClassLevel.FOUNDATIONAL,
        inclusion_rules=(
            "the concept definition explicitly preserves missing semantic support",
            "unknown or unsupported status remains visible without repair by inference",
        ),
        exclusion_rules=(
            "membership does not admit an unknown concept",
            "membership does not convert missing support into rejection or truth",
        ),
        parent_class_keys=(),
        multiple_membership_permitted=True,
        authority_section="Document 4, Section 24 — Foundational Semantic-Class Families",
        source_reference="document4:section24:unknown-unclassified-unsupported-family",
    ),
)

MEMBERSHIP_DEFINITIONS: Final[tuple[MembershipDefinitionAuthority, ...]] = (
    MembershipDefinitionAuthority(
        concept_key="forge_controlled_concept_identity",
        class_key="type_or_category_concept",
        membership_basis=(
            "the concept identifies a governed semantic-resource identity type",
            "the admitted definition is categorical rather than occurrence-level",
        ),
        authority_section="Document 4, Sections 23–24",
        source_reference="slice37c:forge-controlled-concept-identity:class-review",
    ),
    MembershipDefinitionAuthority(
        concept_key="source_expression_form",
        class_key="expression_representation_communication_concept",
        membership_basis=(
            "the concept identifies exact source-bound expression form",
            "the class preserves representation without interpretation",
        ),
        authority_section="Document 4, Sections 23–24",
        source_reference="slice37c:source-expression-form:class-review",
    ),
    MembershipDefinitionAuthority(
        concept_key="concept_admission",
        class_key="occurrence_event_or_change_concept",
        membership_basis=(
            "admission is represented as a governed semantic transition event",
            "membership does not assert that any particular admission occurred",
        ),
        authority_section="Document 4, Sections 23–24",
        source_reference="slice37c:concept-admission:event-class-review",
    ),
    MembershipDefinitionAuthority(
        concept_key="concept_admission",
        class_key="action_type_concept",
        membership_basis=(
            "admission identifies a bounded kind of human-governed act",
            "classification supplies no permission, capability, or execution",
        ),
        authority_section="Document 4, Section 26",
        source_reference="slice37c:concept-admission:action-type-class-review",
    ),
    MembershipDefinitionAuthority(
        concept_key="unknown_concept_condition",
        class_key="state_or_condition_concept",
        membership_basis=(
            "the concept identifies a semantic condition of missing admitted support",
            "membership preserves rather than resolves the condition",
        ),
        authority_section="Document 4, Sections 23–24",
        source_reference="slice37c:unknown-concept-condition:state-class-review",
    ),
    MembershipDefinitionAuthority(
        concept_key="unknown_concept_condition",
        class_key="unknown_unclassified_or_foundationally_unsupported_concept",
        membership_basis=(
            "the concept explicitly represents an unknown-support condition",
            "multiple membership is explicit and does not imply hierarchy inheritance",
        ),
        authority_section="Document 4, Section 24",
        source_reference="slice37c:unknown-concept-condition:unknown-class-review",
    ),
)

RELATION_FAMILY_DEFINITIONS: Final[
    tuple[RelationFamilyDefinitionAuthority, ...]
] = (
    RelationFamilyDefinitionAuthority(
        family_key="controlled_semantic_distinction",
        label="Controlled Semantic Distinction",
        definition="Structural family for preserving materially distinct governed meanings.",
        relationship_domain="controlled concept differentiation",
        eligible_resource_kinds=("concept_identity",),
        authority_section="Document 4, Section 30",
        source_reference="document4:section30:controlled-semantic-distinction",
    ),
    RelationFamilyDefinitionAuthority(
        family_key="bounded_non_equivalence",
        label="Bounded Non-Equivalence",
        definition="Structural family for explicit non-equivalence within stated scope.",
        relationship_domain="bounded concept non-equivalence",
        eligible_resource_kinds=("concept_identity",),
        authority_section="Document 4, Section 30",
        source_reference="document4:section30:bounded-non-equivalence",
    ),
    RelationFamilyDefinitionAuthority(
        family_key="conceptual_component",
        label="Conceptual Component",
        definition=(
            "Structural family for explicit relations in which one governed "
            "concept is a bounded semantic component of another conceptual structure."
        ),
        relationship_domain="controlled conceptual component structure",
        eligible_resource_kinds=("concept_identity",),
        authority_section=(
            "Document 4, Section 30.18 — Conceptual Component Relation Family"
        ),
        source_reference="document4:section30.18:conceptual-component-family",
    ),
    RelationFamilyDefinitionAuthority(
        family_key="conceptual_composition",
        label="Conceptual Composition",
        definition=(
            "Structural family for explicit relations in which a broader governed "
            "conceptual structure is composed of bounded component meanings."
        ),
        relationship_domain="controlled conceptual composition",
        eligible_resource_kinds=("concept_identity",),
        authority_section=(
            "Document 4, Section 30.19 — Conceptual Composition Relation Family"
        ),
        source_reference="document4:section30.19:conceptual-composition-family",
    ),
    RelationFamilyDefinitionAuthority(
        family_key="state_relevance",
        label="State Relevance",
        definition="Structural family for representing that a state concept is relevant to another concept.",
        relationship_domain="state or condition relevance",
        eligible_resource_kinds=("concept_identity",),
        authority_section="Document 4, Section 30",
        source_reference="document4:section30:state-relevance",
    ),
    RelationFamilyDefinitionAuthority(
        family_key="representation_relevance",
        label="Representation Relevance",
        definition="Structural family for representing expression or representation relevance.",
        relationship_domain="expression and representation relevance",
        eligible_resource_kinds=("concept_identity",),
        authority_section="Document 4, Sections 30–31",
        source_reference="document4:sections30-31:representation-relevance",
    ),
)

RELATION_TYPE_DEFINITIONS: Final[tuple[RelationTypeDefinitionAuthority, ...]] = (
    RelationTypeDefinitionAuthority(
        relation_key="materially_distinct_from",
        family_key="controlled_semantic_distinction",
        label="Materially Distinct From",
        definition="Type eligibility for two governed concept meanings to remain materially distinct.",
        domain_class_keys=ALL_CLASS_KEYS,
        range_class_keys=ALL_CLASS_KEYS,
        direction=RelationDirection.SYMMETRIC,
        symmetry=RelationSymmetry.SYMMETRIC,
        inverse_relation_key=None,
        sense_bounded_participation_required=True,
        status_sensitive=False,
        ancestry_sensitive=True,
        conditional=True,
        authority_section="Document 4, Section 30",
        source_reference="document4:section30:materially-distinct-type",
    ),
    RelationTypeDefinitionAuthority(
        relation_key="not_equivalent_within_scope",
        family_key="bounded_non_equivalence",
        label="Not Equivalent Within Scope",
        definition="Type eligibility for explicit bounded non-equivalence without global negation.",
        domain_class_keys=ALL_CLASS_KEYS,
        range_class_keys=ALL_CLASS_KEYS,
        direction=RelationDirection.SYMMETRIC,
        symmetry=RelationSymmetry.SYMMETRIC,
        inverse_relation_key=None,
        sense_bounded_participation_required=True,
        status_sensitive=True,
        ancestry_sensitive=True,
        conditional=True,
        authority_section="Document 4, Section 30",
        source_reference="document4:section30:bounded-non-equivalence-type",
    ),
    RelationTypeDefinitionAuthority(
        relation_key="conceptual_component_of",
        family_key="conceptual_component",
        label="Conceptual Component Of",
        definition="Directed type eligibility for one concept to be a bounded conceptual component of another.",
        domain_class_keys=ALL_CLASS_KEYS,
        range_class_keys=ALL_CLASS_KEYS,
        direction=RelationDirection.DIRECTED,
        symmetry=RelationSymmetry.ASYMMETRIC,
        inverse_relation_key="conceptually_composed_of",
        sense_bounded_participation_required=True,
        status_sensitive=False,
        ancestry_sensitive=True,
        conditional=True,
        authority_section="Document 4, Section 30.18",
        source_reference="document4:section30.18:conceptual-component-type",
    ),
    RelationTypeDefinitionAuthority(
        relation_key="conceptually_composed_of",
        family_key="conceptual_composition",
        label="Conceptually Composed Of",
        definition="Directed inverse-facing type eligibility for a concept to be composed of another concept.",
        domain_class_keys=ALL_CLASS_KEYS,
        range_class_keys=ALL_CLASS_KEYS,
        direction=RelationDirection.DIRECTED,
        symmetry=RelationSymmetry.ASYMMETRIC,
        inverse_relation_key="conceptual_component_of",
        sense_bounded_participation_required=True,
        status_sensitive=False,
        ancestry_sensitive=True,
        conditional=True,
        authority_section="Document 4, Section 30.19",
        source_reference="document4:section30.19:conceptual-composition-type",
    ),
    RelationTypeDefinitionAuthority(
        relation_key="state_relevant_to",
        family_key="state_relevance",
        label="State Relevant To",
        definition="Directed type eligibility for a state or condition concept to be structurally relevant to another concept.",
        domain_class_keys=(
            "state_or_condition_concept",
            "unknown_unclassified_or_foundationally_unsupported_concept",
        ),
        range_class_keys=ALL_CLASS_KEYS,
        direction=RelationDirection.DIRECTED,
        symmetry=RelationSymmetry.ASYMMETRIC,
        inverse_relation_key=None,
        sense_bounded_participation_required=True,
        status_sensitive=True,
        ancestry_sensitive=True,
        conditional=True,
        authority_section="Document 4, Section 30",
        source_reference="document4:section30:state-relevance-type",
    ),
    RelationTypeDefinitionAuthority(
        relation_key="representation_relevant_to",
        family_key="representation_relevance",
        label="Representation Relevant To",
        definition="Directed type eligibility for an expression or representation concept to be structurally relevant to another concept.",
        domain_class_keys=("expression_representation_communication_concept",),
        range_class_keys=ALL_CLASS_KEYS,
        direction=RelationDirection.DIRECTED,
        symmetry=RelationSymmetry.ASYMMETRIC,
        inverse_relation_key=None,
        sense_bounded_participation_required=True,
        status_sensitive=True,
        ancestry_sensitive=True,
        conditional=True,
        authority_section="Document 4, Sections 30–31",
        source_reference="document4:sections30-31:representation-relevance-type",
    ),
)

RELATION_STATE_DEFINITIONS: Final[tuple[RelationStateDefinitionAuthority, ...]] = (
    RelationStateDefinitionAuthority(
        state_kind=RelationStateKind.UNKNOWN,
        definition="The requested relation type or participating governed resource is not known in the closed registry.",
        permitted_uses=("preserve missing relation identity", "return an exact fail-closed state"),
        prohibited_repairs=("guess a relation type", "import an ontology", "select a nearest relation"),
        authority_section="Document 4, Sections 29–31",
        source_reference="document4:unknown-relation-state",
    ),
    RelationStateDefinitionAuthority(
        state_kind=RelationStateKind.UNSUPPORTED,
        definition="The requested structural relation lacks an admitted type or permitted domain/range basis.",
        permitted_uses=("preserve missing support", "block relation-instance construction"),
        prohibited_repairs=("infer support from labels", "treat common usage as authority"),
        authority_section="Document 4, Sections 29–31",
        source_reference="document4:unsupported-relation-state",
    ),
    RelationStateDefinitionAuthority(
        state_kind=RelationStateKind.CONFLICTED,
        definition="Material relation authorities or constraints conflict and no structural eligibility may be asserted.",
        permitted_uses=("preserve the conflict", "defer to later competent review"),
        prohibited_repairs=("choose the convenient source", "silently discard one constraint"),
        authority_section="Document 4, Sections 29–31",
        source_reference="document4:conflicted-relation-state",
    ),
    RelationStateDefinitionAuthority(
        state_kind=RelationStateKind.PROHIBITED_EXPANSION,
        definition="The request would widen class, scope, domain, range, inverse, or implication authority beyond the admitted closed set.",
        permitted_uses=("refuse scope expansion", "preserve exact admitted boundaries"),
        prohibited_repairs=("automatic inheritance", "graph completion", "external class substitution"),
        authority_section="Document 4, Sections 29–30",
        source_reference="document4:prohibited-relation-expansion-state",
    ),
)

PROHIBITED_IMPLICATION_KINDS: Final[tuple[ProhibitedImplicationKind, ...]] = tuple(
    ProhibitedImplicationKind
)
