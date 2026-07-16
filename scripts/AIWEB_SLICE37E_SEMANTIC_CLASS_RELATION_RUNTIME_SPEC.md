# AI.Web Slice 37E Semantic-Class and Relation-Type Runtime Specification

## Purpose

Install a deterministic, immutable, offline, read-only semantic organization registry over the exact accepted Slice 37D registry.

## Package boundary

`aiweb_language_core_bootstrap.controlled_concept_sense_registry.semantic_class_relation_registry`

The package is a sibling of the accepted built-in registry, governed lifecycle, and sense/term-mapping registry. Importing it performs no file access, network access, route registration, persistence, runtime activation, source interpretation, relation-instance creation, rendering, or delivery.

## Immutable record families

- semantic-class definitions;
- explicit concept-to-class membership rules;
- semantic-relation-family definitions;
- semantic-relation-type rules;
- one inverse-relation declaration;
- relation-version identities;
- unresolved relation-state policies;
- prohibited implication rules;
- exact relation-type eligibility requests and results;
- registry manifest and registry aggregate.

## Stable identity

All Slice 37E native records use canonical deterministic `stable_record_id` identities. Semantic classes, relation families, and relation types use the accepted Slice 37A identity contracts and the Slice 37B lifecycle mechanism.

Each class, family, and type has a preserved three-version history:

- v1 observed;
- v2 candidate;
- v3 architecture admitted.

Every transition is human-authorized, non-automatic, non-LLM, provenance-bound, and preserves the previous record. Relation-version records bind each current v3 type to its exact lineage and two predecessor identities.

## Registry behavior

Permitted pure operations:

- exact semantic-class identity lookup;
- exact relation-family identity lookup;
- exact relation-type identity lookup;
- exact membership identity lookup;
- exact explicit memberships for one admitted concept;
- exact relation-state policy lookup;
- deterministic relation-type eligibility evaluation.

Eligibility requires:

1. exact relation-type identity;
2. exact admitted domain concept identity;
3. exact admitted range concept identity;
4. exact requested scope contained by the type rule;
5. at least one explicit domain membership permitted by the type;
6. at least one explicit range membership permitted by the type.

An eligible result means only `eligible_type_only`. It creates no relation instance, asserts no fact, determines no truth, validates no evidence, applies no status, and determines no implementation.

## Fail-closed behavior

Malformed identities, schema mismatches, duplicate records, missing references, count drift, non-closed key sets, invalid domain/range references, direction/symmetry contradictions, unauthorized inverse declarations, version mismatches, lifecycle defects, authority-bearing memberships, relation-instance flags, and later-authority flags produce deterministic validation issues.

Unknown identifiers, unsupported domain membership, and scope expansion return explicit non-success states. No fallback or approximation exists.

## Non-authority guarantees

The package contains zero relation instances. It does not mutate Slice 37C concept records to insert class or relation references. It does not infer membership through parent classes. It does not derive relations from text, mappings, senses, historical files, or external resources.

It has no LLM, model, embedding, vector, similarity, ontology alignment, graph completion, external-resource, route, tool, memory, action, renderer, delivery, or network dependency.
