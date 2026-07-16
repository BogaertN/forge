"""Human-approved Slice 37C concept-selection authority.

The four definitions below are selected from Document 4 architecture law because
they are necessary to prove the registry boundary itself.  They are not selected
from word frequency, corpus occurrence, semantic similarity, historical Slice 8
fixtures, BUILD-009 labels, or external lexical resources.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from ..schema import CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES


SLICE37C_DECISION_OWNER_REF: Final[str] = "nicholas-jacob-bogaert"
SLICE37C_HUMAN_APPROVAL_REF: Final[str] = (
    "aiweb-slice37c-decision-owner-concept-admission-and-application-authorization"
)
SLICE37C_NAMESPACE_KEY: Final[str] = (
    "aiweb:language-core:concept-registry"
)
SLICE37C_NAMESPACE_LABEL: Final[str] = (
    "AI.Web Language-Core Concept Registry"
)
SLICE37C_NAMESPACE_DEFINITION: Final[str] = (
    "The bounded internal namespace for Forge-owned language-core concept "
    "identities admitted under Document 4. Membership in this namespace "
    "provides semantic-resource identity only and does not provide lexical "
    "mapping, interpretation, truth, evidence, permission, runtime, memory, "
    "action, rendering, delivery, or implementation authority."
)

SLICE37C_NAMESPACE_SCOPE: Final[tuple[str, ...]] = (
    "namespace:aiweb:language-core:concept-registry",
    "domain:forge-language-core",
    "authority:controlled-semantic-resource-only",
)

SLICE37C_NAMESPACE_PERMITTED_USES: Final[tuple[str, ...]] = (
    "identify the exact internal namespace of Slice 37C concept resources",
    "support deterministic read-only registry inspection",
    "support provenance and lifecycle verification",
)

SLICE37C_COMMON_PROHIBITED_USES: Final[tuple[str, ...]] = (
    "surface-form or fuzzy lexical lookup",
    "source-occurrence interpretation",
    "term-to-concept mapping",
    "sense creation or selection",
    "semantic-class or relation population",
    "Slice 36 structural candidate consumption",
    "CandidateMeaning or selected-meaning creation",
    "predicate or participant-role authority",
    "truth or evidence validation",
    "permission, capability, tool, or action authority",
    "memory read, write, deletion, or disclosure authority",
    "external-resource admission or loading",
    "runtime route or service activation",
    "outward rendering or delivery authorization",
    "release or production-readiness claim",
)

SLICE37C_PROHIBITED_AUTHORITIES: Final[tuple[str, ...]] = (
    CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES
)

SLICE37C_ADDITIONAL_AUTHORITY_LIMITATIONS: Final[tuple[str, ...]] = (
    "built-in registry membership is not source-expression applicability",
    "exact internal key lookup is not lexical lookup",
    "admitted concept is not selected user meaning",
    "read-only registry availability is not runtime integration",
    "empty deferred references are not completed sense, class, or relation authority",
)



@dataclass(frozen=True, slots=True)
class BuiltInConceptDefinition:
    concept_key: str
    preferred_label: str
    definition: str
    explicit_exclusions: tuple[str, ...]
    authority_document: str
    authority_section: str
    source_reference: str
    scope_tags: tuple[str, ...]
    permitted_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    prohibited_authorities: tuple[str, ...] = SLICE37C_PROHIBITED_AUTHORITIES


BUILT_IN_CONCEPT_DEFINITIONS: Final[
    tuple[BuiltInConceptDefinition, ...]
] = (
    BuiltInConceptDefinition(
        concept_key="forge_controlled_concept_identity",
        preferred_label="Forge-Controlled Concept Identity",
        definition=(
            "A Forge-owned, versioned, provenance-governed semantic resource "
            "representing one bounded unit of controlled meaning. It remains "
            "distinct from every surface expression, sense, semantic class, "
            "semantic relation, source authority, evidence event, memory event, "
            "action, validation result, delivery authority, and implementation state."
        ),
        explicit_exclusions=(
            "not a word, phrase, token, label, normalized form, or glossary entry",
            "not a sense identity, semantic class, relation, source record, or external lexical record",
            "not evidence, permission, action, memory, validation, delivery, or implementation",
        ),
        authority_document=(
            "Document 4 — RMC Concept Lexicon and Semantic Relation Graph v1"
        ),
        authority_section="Part III, Section 11",
        source_reference="document4:part3:section11:forge-controlled-concept-identity",
        scope_tags=(
            *SLICE37C_NAMESPACE_SCOPE,
            "concept-scope:concept-resource-definition",
        ),
        permitted_uses=(
            "represent the exact architecture meaning of a Forge-controlled concept identity",
            "support deterministic registry-boundary verification",
            "serve as a future concept candidate reference only after separately authorized integration",
        ),
        prohibited_uses=SLICE37C_COMMON_PROHIBITED_USES,
    ),
    BuiltInConceptDefinition(
        concept_key="source_expression_form",
        preferred_label="Source Expression Form",
        definition=(
            "An observable source-bound word, phrase, symbol, token sequence, "
            "label, or other preserved expression form that may raise a concept "
            "question but does not itself establish a controlled concept identity, "
            "selected sense, interpreted occurrence, or authority."
        ),
        explicit_exclusions=(
            "not a controlled concept identity",
            "not a normalized lexical form or term mapping",
            "not proof that any concept applies to the source occurrence",
        ),
        authority_document=(
            "Document 4 — RMC Concept Lexicon and Semantic Relation Graph v1"
        ),
        authority_section="Part II, Sections 6–8; Part III, Section 11.5",
        source_reference="document4:part2:source-form-boundary",
        scope_tags=(
            *SLICE37C_NAMESPACE_SCOPE,
            "concept-scope:source-expression-boundary",
        ),
        permitted_uses=(
            "represent the exact architecture distinction between expression and concept",
            "support tests that reject surface wording as automatic concept authority",
            "serve as future source-ancestry vocabulary only after separately authorized integration",
        ),
        prohibited_uses=SLICE37C_COMMON_PROHIBITED_USES,
    ),
    BuiltInConceptDefinition(
        concept_key="concept_admission",
        preferred_label="Concept Admission",
        definition=(
            "The explicit human-approved governance act that authorizes one "
            "bounded semantic identity to exist as a Forge-controlled concept "
            "within an exact version and scope. It does not establish source-"
            "expression applicability, selected sense, truth, evidence, action, "
            "memory, validation, delivery, external-resource, runtime, or implementation authority."
        ),
        explicit_exclusions=(
            "not source-expression interpretation or sense selection",
            "not truth, evidence, permission, action, memory, validation, delivery, or implementation",
            "not automatic vocabulary growth from frequency, familiarity, or similarity",
        ),
        authority_document=(
            "Document 4 — RMC Concept Lexicon and Semantic Relation Graph v1"
        ),
        authority_section="Part III, Section 13",
        source_reference="document4:part3:section13:concept-admission",
        scope_tags=(
            *SLICE37C_NAMESPACE_SCOPE,
            "concept-scope:semantic-governance-admission",
        ),
        permitted_uses=(
            "represent the exact architecture meaning of concept admission",
            "support lifecycle and registry-population boundary verification",
            "distinguish semantic admission from implementation or runtime status",
        ),
        prohibited_uses=SLICE37C_COMMON_PROHIBITED_USES,
    ),
    BuiltInConceptDefinition(
        concept_key="unknown_concept_condition",
        preferred_label="Unknown Concept Condition",
        definition=(
            "The explicit governed condition in which a material meaning "
            "requirement lacks sufficient admitted concept authority for "
            "controlled representation. The condition must remain visible and "
            "unresolved rather than being guessed, filled by similarity, or "
            "replaced by a familiar concept."
        ),
        explicit_exclusions=(
            "not a guessed meaning or best-match concept",
            "not general system failure",
            "not permission to import or infer from an external resource",
        ),
        authority_document=(
            "Document 4 — RMC Concept Lexicon and Semantic Relation Graph v1"
        ),
        authority_section="Part III, Section 15; Part IX, Section 50.14",
        source_reference="document4:unknown-concept-condition",
        scope_tags=(
            *SLICE37C_NAMESPACE_SCOPE,
            "concept-scope:unknown-concept-state",
        ),
        permitted_uses=(
            "represent the exact architecture meaning of missing admitted concept support",
            "support fail-closed unknown-state verification",
            "preserve future unresolved semantic ancestry only after separately authorized integration",
        ),
        prohibited_uses=SLICE37C_COMMON_PROHIBITED_USES,
    ),
)

BUILT_IN_CONCEPT_KEYS: Final[tuple[str, ...]] = tuple(
    item.concept_key
    for item in BUILT_IN_CONCEPT_DEFINITIONS
)
