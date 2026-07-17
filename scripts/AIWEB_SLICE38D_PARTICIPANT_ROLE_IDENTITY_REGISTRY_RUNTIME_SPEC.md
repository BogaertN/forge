# AI.Web Slice 38D Participant-Role Identity Registry Runtime Specification

**Slice:** 38D — Participant-Role Identity and Registry
**Accepted parent HEAD:** `2a1830041c0ed8fbff8aa6ca3129385fce8e68f4`
**Accepted parent tree:** `020866a5ba8a41a2485a08cd0333d75ce246ac1a`
**Accepted parent subject:** `Slice 38C minimal built-in action-root registry`

## Purpose

Create the first governed Forge-owned participant-role identity registry without role assignment, predicate frames, capability references, routes, tools, actions, evidence validation, memory access, rendering, or delivery.

## Exact admitted role set

`initiator`, `actor`, `action_subject`, `content`, `source`, `recipient`, `instrument`, `condition`, `standard`, `result`, and `output_target`.

## Registry properties

The registry is deterministic, standard-library-only, immutable, closed, read-only, versioned, provenance-bound, scope-bound, lifecycle-governed, and non-LLM. Lookup is allowed only by exact stable role identity or exact internal `(namespace_id, role_key)` pair.

## Governance records

The registry contains:

- one current namespace identity with candidate ancestry;
- eleven current participant-role identities with candidate ancestry;
- eleven explicit role-dependency records with candidate ancestry;
- five must-remain-distinct role relationships with candidate ancestry;
- one human-approved lifecycle authority record;
- twenty-eight lifecycle transition records;
- zero active correction records;
- zero active conflict records.

Correction and conflict record shapes are implemented and fail-closed validated so later lawful changes can preserve version, scope, ancestry, authority, and non-operation. No correction or conflict is fabricated merely to populate the registry.

## Mandatory distinctions

- semantic relation is not participant role;
- concept candidate is not role assignment;
- source span is not actor;
- grammatical position is not participant role;
- initiator is not actor;
- source is not standard or proof;
- recipient is not output target or delivery authorization;
- standard is not result or verified status;
- action subject is not affected entity or modification target.

## Explicitly absent behavior

Slice 38D installs no surface lookup, aliasing, normalization, spelling repair, synonym expansion, fuzzy match, similarity authority, embedding, vector database, classifier, RAG, LLM inference, occurrence role assignment, concept-to-role conversion, semantic-relation-to-role conversion, source-span-to-actor conversion, grammar-to-role conversion, predicate-frame population, frame completion, capability reference, route, tool, execution, evidence validation, memory operation, rendering, delivery, external-resource load, or production-readiness claim.
