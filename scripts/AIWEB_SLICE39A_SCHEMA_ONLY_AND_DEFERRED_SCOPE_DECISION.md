# AI.Web Slice 39A Schema-Only and Deferred-Scope Decision

## Decision

Slice 39A is limited to immutable in-memory schema contracts and a closed
construction-status vocabulary.

## Why a companion schema is required

The accepted MSM-v1 `CandidateMeaningRecord` is intentionally compact. It owns
semantic custody fields such as communicative act, concept references,
relations, modifiers, ambiguity reasons, unresolved referents, authority
implications, and preservation classes.

The accepted Slice 37 and Slice 38 outputs now preserve substantially more
exact ancestry and candidate identity. Modifying MSM-v1 during Slice 39A would
mix schema definition with manifest migration and integration authority.
Discarding the additional ancestry would violate the Slice 39 provenance
requirement.

Therefore Slice 39A creates a versioned companion record family. Slice 39G will
later make the exact adapter decision after validation, identity, provenance,
content assembly, alternative preservation, and construction are accepted.

## Permanent boundary

Candidate meaning is possible meaning. It is not selected meaning, truth,
evidence, permission, capability availability, a route, an invocation, an
action, memory access, rendering, or delivery.

## Slice 40 authority is absent

The schema does not admit accepted meaning, selected meaning, ambiguity
disposition, clarification-required status, refusal, rejection, unsupported
language disposition, or blocked progression.
