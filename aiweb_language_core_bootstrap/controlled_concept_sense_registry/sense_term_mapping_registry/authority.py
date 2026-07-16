"""Proposed human-approved Slice 37D sense and mapping authority.

The definitions are derived from the exact Slice 37C four-concept registry and
Document 4 term/sense law. They are not derived from frequency, dictionary
familiarity, spelling resemblance, semantic similarity, embeddings, model
inference, historical Slice 8 fixtures, BUILD-009 labels, or external resources.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from ..schema import (
    ConceptLifecycleState,
    LexicalReferenceKind,
)
from .schema import (
    ProhibitedExpansionKind,
)


SLICE37D_DECISION_OWNER_REF: Final[str] = "nicholas-jacob-bogaert"
SLICE37D_HUMAN_APPROVAL_REF: Final[str] = (
    "aiweb-slice37d-decision-owner-sense-term-mapping-admission-and-"
    "application-authorization"
)

SLICE37D_NAMESPACE_SCOPE: Final[tuple[str, ...]] = (
    "namespace:aiweb:language-core:concept-registry",
)
SLICE37D_DOMAIN_SCOPE: Final[tuple[str, ...]] = (
    "domain:forge-language-core",
)

SLICE37D_PROHIBITED_AUTHORITIES: Final[tuple[str, ...]] = (
    "exact lexical reference is not a source occurrence",
    "term mapping is not occurrence-level interpretation",
    "mapped candidate is not selected meaning",
    "mapping multiplicity is not candidate ranking",
    "sense identity is not concept identity",
    "sense identity is not selected sense",
    "outward-expression eligibility is not rendering authority",
    "outward-expression eligibility is not delivery authority",
    "internal namespace is not automatic source applicability",
    "domain scope is not permission or capability authority",
    "unmapped term is not permission to normalize or infer",
    "unsupported mapping is not rejected concept authority",
    "ambiguous mapping is not permission to choose the most common meaning",
    "external label is not external-resource admission",
    "registry availability is not runtime integration",
    "registry lookup is not CandidateMeaning construction",
    "registry lookup is not predicate or participant-role authority",
    "registry lookup is not evidence, memory, action, validation, or delivery",
)

SLICE37D_COMMON_PROHIBITED_USES: Final[tuple[str, ...]] = (
    "source-occurrence interpretation",
    "occurrence-level concept selection",
    "sense selection",
    "candidate ranking or confidence scoring",
    "case-fold guessing",
    "spelling correction",
    "stemming",
    "synonym expansion",
    "nearest-match lookup",
    "frequency ranking",
    "semantic similarity",
    "embedding or vector lookup",
    "model inference",
    "ordinary-dictionary fallback",
    "Slice 36 structural candidate consumption",
    "CandidateMeaning or selected-meaning creation",
    "semantic-class or semantic-relation population",
    "predicate or participant-role authority",
    "truth or evidence validation",
    "permission, capability, tool, or action authority",
    "memory read, write, deletion, or disclosure authority",
    "external-resource admission or loading",
    "runtime route or service activation",
    "outward rendering or delivery authorization",
    "release or production-readiness claim",
)

SLICE37D_REGISTRY_AUTHORITY_LIMITATIONS: Final[tuple[str, ...]] = (
    "lookup accepts only exact caller-supplied form, language, namespace, and domain",
    "candidate tuple order is deterministic record order and carries no rank",
    "one-to-many mapping preserves every candidate until later authority acts",
    "an admitted lexical reference may remain unmapped",
    "an unsupported mapping may contain zero candidates",
    "an ambiguous mapping may contain multiple candidates without selection",
    "outward eligibility is a reference for later expression planning only",
    "no case, spelling, morphology, synonym, similarity, model, or dictionary expansion exists",
)

SLICE37D_PROHIBITED_EXPANSION_KINDS: Final[
    tuple[ProhibitedExpansionKind, ...]
] = tuple(ProhibitedExpansionKind)


@dataclass(frozen=True, slots=True)
class SenseDefinition:
    concept_key: str
    sense_key: str
    definition: str
    differentiation_basis: tuple[str, ...]
    lexical_keys: tuple[str, ...]
    scope_tags: tuple[str, ...]
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...] = SLICE37D_COMMON_PROHIBITED_USES
    authority_section: str = "Document 4, Part IV, Section 18"
    source_reference: str = ""


@dataclass(frozen=True, slots=True)
class LexicalReferenceDefinition:
    lexical_key: str
    exact_form: str
    reference_kind: LexicalReferenceKind
    language_tag: str
    case_sensitive: bool
    scope_tags: tuple[str, ...]
    authority_section: str
    source_reference: str


@dataclass(frozen=True, slots=True)
class MappingDefinition:
    mapping_key: str
    lexical_key: str
    concept_keys: tuple[str, ...]
    sense_keys: tuple[str, ...]
    lifecycle_state: ConceptLifecycleState
    namespace_scope: tuple[str, ...]
    domain_scope: tuple[str, ...]
    authority_section: str
    source_reference: str
    reason: str


SENSE_DEFINITIONS: Final[tuple[SenseDefinition, ...]] = (
    SenseDefinition(
        concept_key="forge_controlled_concept_identity",
        sense_key="governed_semantic_resource_identity",
        definition=(
            "The lexical-semantic pathway in which an exact expression refers "
            "to a Forge-owned, versioned, provenance-governed unit of controlled "
            "meaning rather than to the expression form itself."
        ),
        differentiation_basis=(
            "distinguishes semantic-resource reference from metalinguistic mention",
            "does not treat a visible word or phrase as the governed concept",
            "preserves concept identity without selecting any source occurrence",
        ),
        lexical_keys=(
            "outward_forge_controlled_concept_identity",
            "internal_forge_controlled_concept_identity",
            "domain_concept",
        ),
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "sense-scope:governed-concept-resource",
        ),
        permitted_uses=(
            "identify the exact concept-resource sense candidate",
            "participate in exact one-to-one and ambiguous candidate mappings",
            "remain visible beside other materially supported senses",
        ),
        source_reference=(
            "document4:part4:section18:governed-concept-resource-sense"
        ),
    ),
    SenseDefinition(
        concept_key="source_expression_form",
        sense_key="source_occurrence_form",
        definition=(
            "The lexical-semantic pathway in which an expression is treated as "
            "the exact source-bound form encountered in one preserved language "
            "lineage, without converting that occurrence into a reusable mapping "
            "or selected concept."
        ),
        differentiation_basis=(
            "bound to a particular source-expression lineage",
            "distinct from reusable controlled lexical reference",
            "distinct from metalinguistic mention of an expression type",
        ),
        lexical_keys=(
            "outward_source_expression_form",
            "internal_source_expression_form",
        ),
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "sense-scope:source-occurrence-form",
        ),
        permitted_uses=(
            "identify the source-bound expression-form sense candidate",
            "preserve source-form versus reusable-reference separation",
        ),
        source_reference="document4:part4:section17.4:source-term-sense",
    ),
    SenseDefinition(
        concept_key="source_expression_form",
        sense_key="metalinguistic_expression_mention",
        definition=(
            "The lexical-semantic pathway in which an exact expression is "
            "mentioned or discussed as an expression form rather than used to "
            "invoke the semantic resource it may otherwise denote."
        ),
        differentiation_basis=(
            "mention of expression form rather than semantic-resource use",
            "permits exact mention/use ambiguity to remain visible",
            "does not create quotation, scope, or occurrence interpretation authority",
        ),
        lexical_keys=("domain_concept",),
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "sense-scope:metalinguistic-mention",
        ),
        permitted_uses=(
            "preserve the expression-side candidate for the exact term concept",
            "demonstrate one-to-many mapping without candidate selection",
        ),
        source_reference=(
            "document4:part4:sections17.3-17.8:metalinguistic-expression-mention"
        ),
    ),
    SenseDefinition(
        concept_key="concept_admission",
        sense_key="human_approved_semantic_admission_act",
        definition=(
            "The lexical-semantic pathway in which an exact expression refers "
            "to the explicit human-approved governance act admitting one bounded "
            "semantic identity, not to implementation, runtime activation, "
            "delivery, or source-occurrence selection."
        ),
        differentiation_basis=(
            "semantic-governance admission rather than implementation authorization",
            "requires explicit human approval and bounded scope",
            "does not admit a concept through term association",
        ),
        lexical_keys=(
            "outward_concept_admission",
            "internal_concept_admission",
        ),
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "sense-scope:concept-admission-act",
        ),
        permitted_uses=(
            "identify the exact concept-admission sense candidate",
            "preserve admission-versus-implementation separation",
        ),
        source_reference="document4:part3:section13:concept-admission-sense",
    ),
    SenseDefinition(
        concept_key="unknown_concept_condition",
        sense_key="missing_admitted_concept_support_condition",
        definition=(
            "The lexical-semantic pathway in which an exact expression refers "
            "to the governed absence of sufficient admitted concept support, "
            "which must remain unresolved rather than being filled by similarity, "
            "frequency, external substitution, or model inference."
        ),
        differentiation_basis=(
            "missing admitted concept support rather than general system failure",
            "preserves unknown status without selecting a substitute concept",
            "does not authorize external-resource or dictionary fallback",
        ),
        lexical_keys=(
            "outward_unknown_concept_condition",
            "internal_unknown_concept_condition",
        ),
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "sense-scope:unknown-concept-condition",
        ),
        permitted_uses=(
            "identify the exact unknown-concept-condition sense candidate",
            "support fail-closed unknown-state representation",
        ),
        source_reference=(
            "document4:part3:section15:unknown-concept-condition-sense"
        ),
    ),
)


LEXICAL_REFERENCE_DEFINITIONS: Final[
    tuple[LexicalReferenceDefinition, ...]
] = (
    LexicalReferenceDefinition(
        lexical_key="outward_forge_controlled_concept_identity",
        exact_form="Forge-Controlled Concept Identity",
        reference_kind=LexicalReferenceKind.CONTROLLED_OUTWARD_EXPRESSION,
        language_tag="en",
        case_sensitive=True,
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "lexical-scope:outward-reference-only",
        ),
        authority_section="Document 4, Sections 17.3–17.5 and 20",
        source_reference=(
            "slice37c:preferred-label:forge_controlled_concept_identity"
        ),
    ),
    LexicalReferenceDefinition(
        lexical_key="internal_forge_controlled_concept_identity",
        exact_form="forge_controlled_concept_identity",
        reference_kind=LexicalReferenceKind.CONTROLLED_INTERNAL_EXPRESSION,
        language_tag="und-x-aiweb",
        case_sensitive=True,
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "lexical-scope:internal-identifier",
        ),
        authority_section="Document 4, Sections 17 and 40–49",
        source_reference=(
            "slice37c:concept-key:forge_controlled_concept_identity"
        ),
    ),
    LexicalReferenceDefinition(
        lexical_key="outward_source_expression_form",
        exact_form="Source Expression Form",
        reference_kind=LexicalReferenceKind.CONTROLLED_OUTWARD_EXPRESSION,
        language_tag="en",
        case_sensitive=True,
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "lexical-scope:outward-reference-only",
        ),
        authority_section="Document 4, Sections 17.3–17.5 and 20",
        source_reference="slice37c:preferred-label:source_expression_form",
    ),
    LexicalReferenceDefinition(
        lexical_key="internal_source_expression_form",
        exact_form="source_expression_form",
        reference_kind=LexicalReferenceKind.CONTROLLED_INTERNAL_EXPRESSION,
        language_tag="und-x-aiweb",
        case_sensitive=True,
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "lexical-scope:internal-identifier",
        ),
        authority_section="Document 4, Sections 17 and 40–49",
        source_reference="slice37c:concept-key:source_expression_form",
    ),
    LexicalReferenceDefinition(
        lexical_key="outward_concept_admission",
        exact_form="Concept Admission",
        reference_kind=LexicalReferenceKind.CONTROLLED_OUTWARD_EXPRESSION,
        language_tag="en",
        case_sensitive=True,
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "lexical-scope:outward-reference-only",
        ),
        authority_section="Document 4, Sections 17.3–17.5 and 20",
        source_reference="slice37c:preferred-label:concept_admission",
    ),
    LexicalReferenceDefinition(
        lexical_key="internal_concept_admission",
        exact_form="concept_admission",
        reference_kind=LexicalReferenceKind.CONTROLLED_INTERNAL_EXPRESSION,
        language_tag="und-x-aiweb",
        case_sensitive=True,
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "lexical-scope:internal-identifier",
        ),
        authority_section="Document 4, Sections 17 and 40–49",
        source_reference="slice37c:concept-key:concept_admission",
    ),
    LexicalReferenceDefinition(
        lexical_key="outward_unknown_concept_condition",
        exact_form="Unknown Concept Condition",
        reference_kind=LexicalReferenceKind.CONTROLLED_OUTWARD_EXPRESSION,
        language_tag="en",
        case_sensitive=True,
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "lexical-scope:outward-reference-only",
        ),
        authority_section="Document 4, Sections 17.3–17.5 and 20",
        source_reference=(
            "slice37c:preferred-label:unknown_concept_condition"
        ),
    ),
    LexicalReferenceDefinition(
        lexical_key="internal_unknown_concept_condition",
        exact_form="unknown_concept_condition",
        reference_kind=LexicalReferenceKind.CONTROLLED_INTERNAL_EXPRESSION,
        language_tag="und-x-aiweb",
        case_sensitive=True,
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "lexical-scope:internal-identifier",
        ),
        authority_section="Document 4, Sections 17 and 40–49",
        source_reference="slice37c:concept-key:unknown_concept_condition",
    ),
    LexicalReferenceDefinition(
        lexical_key="domain_concept",
        exact_form="concept",
        reference_kind=LexicalReferenceKind.DOMAIN_TERM,
        language_tag="en",
        case_sensitive=True,
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "lexical-scope:domain-bounded",
            "lexical-status:ambiguous-without-later-authority",
        ),
        authority_section="Document 4, Sections 17.7–17.8 and 18",
        source_reference="document4:concept-term:mention-use-ambiguity",
    ),
    LexicalReferenceDefinition(
        lexical_key="unmapped_mapping_term",
        exact_form="mapping",
        reference_kind=LexicalReferenceKind.DOMAIN_TERM,
        language_tag="en",
        case_sensitive=True,
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "lexical-scope:domain-bounded",
            "lexical-status:known-but-unmapped",
        ),
        authority_section="Document 4, Sections 17.3 and 17.29–17.30",
        source_reference="document4:known-term-without-admitted-mapping",
    ),
    LexicalReferenceDefinition(
        lexical_key="unsupported_sense_term",
        exact_form="sense",
        reference_kind=LexicalReferenceKind.DOMAIN_TERM,
        language_tag="en",
        case_sensitive=True,
        scope_tags=(
            *SLICE37D_NAMESPACE_SCOPE,
            *SLICE37D_DOMAIN_SCOPE,
            "lexical-scope:domain-bounded",
            "lexical-status:mapping-reviewed-unsupported",
        ),
        authority_section="Document 4, Sections 17.28–17.30 and 18",
        source_reference="document4:sense-term:unsupported-concept-mapping",
    ),
)


MAPPING_DEFINITIONS: Final[tuple[MappingDefinition, ...]] = (
    MappingDefinition(
        mapping_key="outward_forge_controlled_concept_identity",
        lexical_key="outward_forge_controlled_concept_identity",
        concept_keys=("forge_controlled_concept_identity",),
        sense_keys=("governed_semantic_resource_identity",),
        lifecycle_state=ConceptLifecycleState.ADMITTED,
        namespace_scope=SLICE37D_NAMESPACE_SCOPE,
        domain_scope=SLICE37D_DOMAIN_SCOPE,
        authority_section="Document 4, Sections 17 and 18",
        source_reference=(
            "slice37d:mapping:outward-forge-controlled-concept-identity"
        ),
        reason="Exact outward label raises one concept and one sense candidate.",
    ),
    MappingDefinition(
        mapping_key="internal_forge_controlled_concept_identity",
        lexical_key="internal_forge_controlled_concept_identity",
        concept_keys=("forge_controlled_concept_identity",),
        sense_keys=("governed_semantic_resource_identity",),
        lifecycle_state=ConceptLifecycleState.ADMITTED,
        namespace_scope=SLICE37D_NAMESPACE_SCOPE,
        domain_scope=SLICE37D_DOMAIN_SCOPE,
        authority_section="Document 4, Sections 17 and 40–49",
        source_reference=(
            "slice37d:mapping:internal-forge-controlled-concept-identity"
        ),
        reason="Exact internal identifier raises one bounded concept/sense candidate.",
    ),
    MappingDefinition(
        mapping_key="outward_source_expression_form",
        lexical_key="outward_source_expression_form",
        concept_keys=("source_expression_form",),
        sense_keys=("source_occurrence_form",),
        lifecycle_state=ConceptLifecycleState.ADMITTED,
        namespace_scope=SLICE37D_NAMESPACE_SCOPE,
        domain_scope=SLICE37D_DOMAIN_SCOPE,
        authority_section="Document 4, Sections 17.4–17.8 and 18",
        source_reference="slice37d:mapping:outward-source-expression-form",
        reason="Exact outward label raises the source-occurrence-form candidate.",
    ),
    MappingDefinition(
        mapping_key="internal_source_expression_form",
        lexical_key="internal_source_expression_form",
        concept_keys=("source_expression_form",),
        sense_keys=("source_occurrence_form",),
        lifecycle_state=ConceptLifecycleState.ADMITTED,
        namespace_scope=SLICE37D_NAMESPACE_SCOPE,
        domain_scope=SLICE37D_DOMAIN_SCOPE,
        authority_section="Document 4, Sections 17.4–17.8 and 18",
        source_reference="slice37d:mapping:internal-source-expression-form",
        reason="Exact internal identifier raises the source-form candidate.",
    ),
    MappingDefinition(
        mapping_key="outward_concept_admission",
        lexical_key="outward_concept_admission",
        concept_keys=("concept_admission",),
        sense_keys=("human_approved_semantic_admission_act",),
        lifecycle_state=ConceptLifecycleState.ADMITTED,
        namespace_scope=SLICE37D_NAMESPACE_SCOPE,
        domain_scope=SLICE37D_DOMAIN_SCOPE,
        authority_section="Document 4, Sections 13, 17.6 and 18",
        source_reference="slice37d:mapping:outward-concept-admission",
        reason="Exact outward label raises the semantic-admission candidate only.",
    ),
    MappingDefinition(
        mapping_key="internal_concept_admission",
        lexical_key="internal_concept_admission",
        concept_keys=("concept_admission",),
        sense_keys=("human_approved_semantic_admission_act",),
        lifecycle_state=ConceptLifecycleState.ADMITTED,
        namespace_scope=SLICE37D_NAMESPACE_SCOPE,
        domain_scope=SLICE37D_DOMAIN_SCOPE,
        authority_section="Document 4, Sections 13, 17.6 and 18",
        source_reference="slice37d:mapping:internal-concept-admission",
        reason="Exact internal identifier raises the admission candidate only.",
    ),
    MappingDefinition(
        mapping_key="outward_unknown_concept_condition",
        lexical_key="outward_unknown_concept_condition",
        concept_keys=("unknown_concept_condition",),
        sense_keys=("missing_admitted_concept_support_condition",),
        lifecycle_state=ConceptLifecycleState.ADMITTED,
        namespace_scope=SLICE37D_NAMESPACE_SCOPE,
        domain_scope=SLICE37D_DOMAIN_SCOPE,
        authority_section="Document 4, Sections 15, 17 and 18",
        source_reference="slice37d:mapping:outward-unknown-concept-condition",
        reason="Exact outward label raises the unknown-condition candidate only.",
    ),
    MappingDefinition(
        mapping_key="internal_unknown_concept_condition",
        lexical_key="internal_unknown_concept_condition",
        concept_keys=("unknown_concept_condition",),
        sense_keys=("missing_admitted_concept_support_condition",),
        lifecycle_state=ConceptLifecycleState.ADMITTED,
        namespace_scope=SLICE37D_NAMESPACE_SCOPE,
        domain_scope=SLICE37D_DOMAIN_SCOPE,
        authority_section="Document 4, Sections 15, 17 and 18",
        source_reference="slice37d:mapping:internal-unknown-concept-condition",
        reason="Exact internal identifier raises the unknown-condition candidate only.",
    ),
    MappingDefinition(
        mapping_key="ambiguous_domain_concept",
        lexical_key="domain_concept",
        concept_keys=(
            "forge_controlled_concept_identity",
            "source_expression_form",
        ),
        sense_keys=(
            "governed_semantic_resource_identity",
            "metalinguistic_expression_mention",
        ),
        lifecycle_state=ConceptLifecycleState.AMBIGUOUS,
        namespace_scope=SLICE37D_NAMESPACE_SCOPE,
        domain_scope=SLICE37D_DOMAIN_SCOPE,
        authority_section="Document 4, Sections 17.7–17.8 and 18",
        source_reference="slice37d:mapping:concept:mention-use-ambiguity",
        reason=(
            "The exact term may raise the governed concept-resource candidate "
            "or the expression-mention candidate. No later authority is present "
            "to choose between them."
        ),
    ),
    MappingDefinition(
        mapping_key="unsupported_domain_sense",
        lexical_key="unsupported_sense_term",
        concept_keys=(),
        sense_keys=(),
        lifecycle_state=ConceptLifecycleState.UNSUPPORTED,
        namespace_scope=SLICE37D_NAMESPACE_SCOPE,
        domain_scope=SLICE37D_DOMAIN_SCOPE,
        authority_section="Document 4, Sections 17.28–17.30 and 18",
        source_reference="slice37d:mapping:sense:unsupported",
        reason=(
            "The exact lexical reference is known, but Slice 37C contains no "
            "admitted concept identity representing controlled sense identity "
            "as a concept. The mapping therefore remains unsupported."
        ),
    ),
)


OUTWARD_ELIGIBLE_LEXICAL_KEYS: Final[tuple[str, ...]] = (
    "outward_forge_controlled_concept_identity",
    "outward_source_expression_form",
    "outward_concept_admission",
    "outward_unknown_concept_condition",
)
