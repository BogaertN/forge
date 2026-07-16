# AI.Web Slice 37C Minimal Built-In Concept Registry Runtime Specification

**Decision owner:** Nicholas Jacob Bogaert / AI.Web
**Parent commit:** `f4cfdd0e3f20c5ff3d72ed335b6ddd155b0f36fd`
**Source packet:** `5933294e9de406d6c4dd37ec69c59af9ac8596f67bb8542a60f6a3fada994963`
**Registry schema:** `aiweb-language-core-minimal-built-in-concept-registry-schema-v1`

## Purpose

Install the first closed, immutable, read-only registry of explicitly admitted Forge-owned concept identities. The registry proves deterministic concept authority without pretending to cover ordinary language.

## Static registry identity

- **Namespace ID:** `concept_namespace:1ccf3b03c659050dbeaba34e1d62b7cba08e056d0d41c9722109f193b1b3d131`
- **Manifest ID:** `slice37c_built_in_concept_registry_manifest:e774297ec874a79adf1e1d817c5a452b5b43e5c2f466e1af4c75e1bf4fdb626d`
- **Governance batch ID:** `slice37b_concept_governance_batch:725dd0f6d0f016ea8682d37fbd5c8ee2a6b7e82b62c45328f0a998a67a0c655a`
- **Registry digest:** `slice37c_built_in_concept_registry:1125446716821de220bf8d0432b58d8f1d16b2b112ec41a4ce26f605fb95a6e9`
- **Current namespace count:** 1
- **Current concept count:** 4
- **Provenance records:** 5
- **Governed resource versions:** 15
- **Human-approved authority records:** 10
- **Lifecycle transitions:** 10

## Admitted concepts

### 1. `forge_controlled_concept_identity`

- **Stable ID:** `controlled_concept:7e3ea783b6916f7c65033411b8dc506ed236a1b65703815658847f067eb4577f`
- **Label:** Forge-Controlled Concept Identity
- **Definition:** A Forge-owned, versioned, provenance-governed semantic resource representing one bounded unit of controlled meaning. It remains distinct from every surface expression, sense, semantic class, semantic relation, source authority, evidence event, memory event, action, validation result, delivery authority, and implementation state.
- **Scope:** `namespace:aiweb:language-core:concept-registry`, `domain:forge-language-core`, `authority:controlled-semantic-resource-only`, `concept-scope:concept-resource-definition`
- **Provenance reference:** `concept_provenance:49108a8c8862b56cd2a685d7f80f7e8ce2944d25873d3a0af91480d7e1464a41`
- **Lifecycle:** observed `v1` → candidate `v2` → admitted `v3`
- **Semantic-class references:** empty and deferred to Slice 37E
- **Sense references:** empty and deferred to Slice 37D
- **Relation references:** empty and deferred to Slice 37E
### 2. `source_expression_form`

- **Stable ID:** `controlled_concept:19654f8c736a1f55d82806bc4885bb945044545a72a130c3f4d44d799dc06136`
- **Label:** Source Expression Form
- **Definition:** An observable source-bound word, phrase, symbol, token sequence, label, or other preserved expression form that may raise a concept question but does not itself establish a controlled concept identity, selected sense, interpreted occurrence, or authority.
- **Scope:** `namespace:aiweb:language-core:concept-registry`, `domain:forge-language-core`, `authority:controlled-semantic-resource-only`, `concept-scope:source-expression-boundary`
- **Provenance reference:** `concept_provenance:cc70eb739b8183bfb432e64dfa6e179ad9952a930604d0efabb25bd947a6a928`
- **Lifecycle:** observed `v1` → candidate `v2` → admitted `v3`
- **Semantic-class references:** empty and deferred to Slice 37E
- **Sense references:** empty and deferred to Slice 37D
- **Relation references:** empty and deferred to Slice 37E
### 3. `concept_admission`

- **Stable ID:** `controlled_concept:0e6afd7ec1871c9242f4e2e9eb79186477f53092844b96d6be9850c1fee5e2fd`
- **Label:** Concept Admission
- **Definition:** The explicit human-approved governance act that authorizes one bounded semantic identity to exist as a Forge-controlled concept within an exact version and scope. It does not establish source-expression applicability, selected sense, truth, evidence, action, memory, validation, delivery, external-resource, runtime, or implementation authority.
- **Scope:** `namespace:aiweb:language-core:concept-registry`, `domain:forge-language-core`, `authority:controlled-semantic-resource-only`, `concept-scope:semantic-governance-admission`
- **Provenance reference:** `concept_provenance:4fd914e1cb41b914676dc47d4bcdaf479743da02051160b140e857d2ecb8402f`
- **Lifecycle:** observed `v1` → candidate `v2` → admitted `v3`
- **Semantic-class references:** empty and deferred to Slice 37E
- **Sense references:** empty and deferred to Slice 37D
- **Relation references:** empty and deferred to Slice 37E
### 4. `unknown_concept_condition`

- **Stable ID:** `controlled_concept:8c23b6bdca8a6393f1429ab86e435caf230e356be05c67342aa4cce2634b8d48`
- **Label:** Unknown Concept Condition
- **Definition:** The explicit governed condition in which a material meaning requirement lacks sufficient admitted concept authority for controlled representation. The condition must remain visible and unresolved rather than being guessed, filled by similarity, or replaced by a familiar concept.
- **Scope:** `namespace:aiweb:language-core:concept-registry`, `domain:forge-language-core`, `authority:controlled-semantic-resource-only`, `concept-scope:unknown-concept-state`
- **Provenance reference:** `concept_provenance:c3e7af14cdb9c1de80d69166e6cc21cf28dea8204efe410734efb2d011abfd14`
- **Lifecycle:** observed `v1` → candidate `v2` → admitted `v3`
- **Semantic-class references:** empty and deferred to Slice 37E
- **Sense references:** empty and deferred to Slice 37D
- **Relation references:** empty and deferred to Slice 37E

## Access surface

The registry permits only:

- exact stable concept-ID lookup;
- exact internal `(namespace_id, concept_key)` lookup;
- deterministic enumeration in canonical order;
- read-only inspection of immutable records;
- fail-closed validation of the complete static registry.

It provides no surface-form lookup, normalization, aliases, fuzzy matching, similarity, fallback, lexical mapping, source-occurrence interpretation, or sense selection.

## Immutability and side-effect boundary

All records are frozen slotted dataclasses or immutable tuples. Import constructs only deterministic in-memory constants. No filesystem, network, process, database, model, vector, memory, route, tool, action, rendering, or delivery side effect occurs.

## Lifecycle boundary

The governance batch preserves one three-version namespace lineage and four three-version concept lineages. The batch proves semantic admission under Slice 37B law while leaving `registry_population_installed=False`. The separate Slice 37C manifest records the explicitly authorized static registry installation. This prevents lifecycle admission from being confused with runtime installation.

## Historical boundary

Historical Slice 8 remains preserved and unsuperseded. No historical fixture is imported or renamed into the built-in registry.
