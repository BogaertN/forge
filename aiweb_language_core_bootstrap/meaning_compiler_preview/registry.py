"""Forge-owned provisional seed registry for the v0 meaning preview.

Nothing in this registry is imported from the glyph packet, Google Drive,
Panini, Chomsky, or another language-core branch.  Those materials may inform
future operator review, but they have zero authority in this preview.
"""

from __future__ import annotations

from typing import Final

from ..schema import stable_record_id
from .schema import (
    ForgeSeedRegistry,
    PredicateDefinition,
    ProvisionalConcept,
    ProvisionalSense,
    RoleDefinition,
)


REGISTRY_OWNER: Final[str] = "forge_operator_system"
REGISTRY_VERSION: Final[str] = "forge-meaning-seed-v0"


def _surface_variants(*forms: str) -> tuple[tuple[str, ...], ...]:
    declared: list[tuple[str, ...]] = []
    for form in forms:
        words = tuple(form.split(" "))
        for candidate in (
            words,
            tuple(word.capitalize() for word in words),
            (words[0].capitalize(), *words[1:]),
            tuple(word.upper() for word in words),
        ):
            if candidate and candidate not in declared:
                declared.append(candidate)
    return tuple(declared)


def _concept(
    key: str,
    label: str,
    semantic_class: str,
    definition: str,
) -> ProvisionalConcept:
    body = {
        "concept_key": key,
        "preferred_label": label,
        "semantic_class": semantic_class,
        "provisional_definition": definition,
        "registry_owner": REGISTRY_OWNER,
        "registry_version": REGISTRY_VERSION,
        "provisional": True,
        "external_reference_authority": False,
    }
    return ProvisionalConcept(
        concept_id=stable_record_id("forge_preview_concept", body),
        **body,
    )


def _sense(
    key: str,
    concept: ProvisionalConcept,
    forms: tuple[tuple[str, ...], ...],
    gloss: str,
) -> ProvisionalSense:
    body = {
        "sense_key": key,
        "concept_ref": concept.concept_id,
        "exact_surface_forms": forms,
        "provisional_gloss": gloss,
        "registry_owner": REGISTRY_OWNER,
        "registry_version": REGISTRY_VERSION,
        "provisional": True,
        "external_reference_authority": False,
    }
    return ProvisionalSense(
        sense_id=stable_record_id("forge_preview_sense", body),
        **body,
    )


def _predicate(
    key: str,
    label: str,
    forms: tuple[str, ...],
    roles: tuple[str, ...],
) -> PredicateDefinition:
    body = {
        "predicate_key": key,
        "preferred_label": label,
        "exact_surface_forms": forms,
        "required_roles": roles,
        "registry_owner": REGISTRY_OWNER,
        "registry_version": REGISTRY_VERSION,
        "provisional": True,
    }
    return PredicateDefinition(
        predicate_id=stable_record_id("forge_preview_predicate", body),
        **body,
    )


def _role(key: str, description: str) -> RoleDefinition:
    body = {
        "role_key": key,
        "description": description,
        "registry_owner": REGISTRY_OWNER,
        "registry_version": REGISTRY_VERSION,
        "provisional": True,
    }
    return RoleDefinition(
        role_id=stable_record_id("forge_preview_role", body),
        **body,
    )


_CONCEPT_SPECS: Final[tuple[tuple[str, str, str, str, tuple[str, ...]], ...]] = (
    (
        "forge",
        "Forge",
        "operator_system",
        "the main operator system named Forge",
        ("forge",),
    ),
    (
        "forge_core",
        "Forge Core",
        "system_component",
        "the provisional central operating component of Forge",
        ("forge core", "core"),
    ),
    (
        "language_core",
        "Language Core",
        "language_component",
        "the provisional Forge component that compiles source forms into symbolic meaning candidates",
        ("language core", "core"),
    ),
    (
        "rmc_memory",
        "RMC Memory",
        "memory_component",
        "the read-only resonance context layer identified as RMC in this preview",
        ("rmc", "rmc memory"),
    ),
    (
        "meaning",
        "Meaning",
        "semantic_object",
        "a provisional symbolic relation among a predicate, roles, and concepts",
        ("meaning",),
    ),
    (
        "word",
        "Word",
        "source_form",
        "a written source form retained with its exact source span",
        ("word", "words"),
    ),
    (
        "language",
        "Language",
        "symbolic_system",
        "a system of forms and relations used to express meaning",
        ("language",),
    ),
    (
        "memory",
        "Memory",
        "context_component",
        "a bounded context record available to Forge without granting selection authority",
        ("memory",),
    ),
    (
        "vector_memory",
        "Vector Memory",
        "memory_design",
        "a memory design represented as a provisional comparison concept only",
        ("vector memory",),
    ),
    (
        "operator",
        "Operator",
        "human_role",
        "the human authority who reviews and controls Forge",
        ("operator",),
    ),
    (
        "system",
        "System",
        "system_class",
        "a bounded collection of related components",
        ("system",),
    ),
    (
        "status",
        "Status",
        "reportable_state",
        "a declared state available for inspection or reporting",
        ("status",),
    ),
    (
        "manifest",
        "Manifest",
        "structured_record",
        "a structured record that declares a bounded set of items",
        ("manifest",),
    ),
    (
        "file",
        "File",
        "stored_artifact",
        "a named stored artifact",
        ("file", "files"),
    ),
    (
        "result",
        "Result",
        "preview_record",
        "a structured output record produced by a bounded operation",
        ("result", "results"),
    ),
    (
        "symbolic_math",
        "Symbolic Math",
        "formal_method",
        "explicit composition and relation operations over declared symbolic records",
        ("symbolic math", "symbolic mathematics"),
    ),
    (
        "grammar",
        "Grammar",
        "composition_rules",
        "a bounded set of declared rules for composing source forms",
        ("grammar",),
    ),
    (
        "lexicon",
        "Lexicon",
        "sense_registry",
        "a provisional registry connecting exact surface forms to declared senses",
        ("lexicon",),
    ),
    (
        "context",
        "Context",
        "relation_record",
        "a bounded set of exact references considered alongside a meaning candidate",
        ("context",),
    ),
    (
        "resonance",
        "Resonance",
        "exact_reference_relation",
        "an exact shared concept, relation, or ancestry reference in this preview",
        ("resonance",),
    ),
)


def _build_registry() -> ForgeSeedRegistry:
    concepts = tuple(
        _concept(key, label, semantic_class, definition)
        for key, label, semantic_class, definition, _forms in _CONCEPT_SPECS
    )
    by_key = {concept.concept_key: concept for concept in concepts}
    senses = tuple(
        _sense(
            f"{key}_preview_sense",
            by_key[key],
            _surface_variants(*forms),
            definition,
        )
        for key, _label, _semantic_class, definition, forms in _CONCEPT_SPECS
    )
    predicates = (
        _predicate("be", "be", ("am", "is", "are", "was", "were", "be"), ("subject", "object")),
        _predicate("mean", "mean", ("mean", "means", "meant"), ("definition_target",)),
        _predicate("inspect", "inspect", ("inspect", "inspects", "inspected"), ("object",)),
        _predicate("report", "report", ("report", "reports", "reported"), ("object",)),
        _predicate("explain", "explain", ("explain", "explains", "explained"), ("object",)),
        _predicate("compare", "compare", ("compare", "compares", "compared"), ("comparison_left", "comparison_right")),
        _predicate("use", "use", ("use", "uses", "used"), ("actor", "object")),
        _predicate("remember", "remember", ("remember", "remembers", "remembered"), ("actor", "object")),
        _predicate("store", "store", ("store", "stores", "stored"), ("actor", "object")),
        _predicate("retrieve", "retrieve", ("retrieve", "retrieves", "retrieved"), ("actor", "object")),
        _predicate("describe", "describe", ("describe", "describes", "described"), ("object",)),
    )
    roles = tuple(
        _role(key, description)
        for key, description in (
            ("requester", "source role that issues a request"),
            ("actor", "concept expected to carry the predicate relation"),
            ("subject", "concept about which a simple clause makes a statement"),
            ("object", "concept bound as the object or complement"),
            ("definition_target", "concept for which a provisional definition is requested"),
            ("comparison_left", "left concept in a bounded comparison"),
            ("comparison_right", "right concept in a bounded comparison"),
        )
    )
    body = {
        "owner": REGISTRY_OWNER,
        "version": REGISTRY_VERSION,
        "concepts": concepts,
        "senses": senses,
        "predicates": predicates,
        "roles": roles,
        "external_reference_authority": False,
        "imported_reference_definitions_used": False,
    }
    return ForgeSeedRegistry(
        registry_id=stable_record_id("forge_preview_registry", body),
        **body,
    )


FORGE_SEED_REGISTRY: Final[ForgeSeedRegistry] = _build_registry()


def forge_seed_registry() -> ForgeSeedRegistry:
    """Return the immutable Forge-owned v0 seed registry."""

    return FORGE_SEED_REGISTRY


__all__ = (
    "FORGE_SEED_REGISTRY",
    "REGISTRY_OWNER",
    "REGISTRY_VERSION",
    "forge_seed_registry",
)
