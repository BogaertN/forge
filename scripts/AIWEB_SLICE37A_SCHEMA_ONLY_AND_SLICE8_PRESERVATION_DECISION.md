# Slice 37A Decision — Schema-Only Authority and Slice 8 Preservation

## Decision

Slice 37A creates a new isolated package named `controlled_concept_sense_registry` but limits it to immutable schema contracts, deterministic record identity and structural validation.

## Why Slice 8 is not reused as the runtime registry

Slice 8 was accepted as an inert boundary scaffold. Its records proved that concepts, senses and semantic relations could be named without resolution, graph traversal, resource admission, role assignment, gate selection, rendering, memory writes or action routing.

Slice 37A must preserve that evidence while avoiding two unlawful shortcuts:

1. treating the Slice 8 demonstration records as admitted concept authority;
2. silently replacing the Slice 8 historical boundary with a differently scoped runtime registry.

Therefore Slice 8 remains byte-protected and unsuperseded. Slice 37A references its commit identity in architecture metadata only and does not import the package.

## Why the registry remains empty

Concept admission, lifecycle transition law, built-in population, term mapping, semantic classes, relation constraints and structural integration are separate authorities. Combining them into one patch would make review, rollback and defect isolation too coarse.

The exact sequence remains:

- 37A — schema contract;
- 37B — identity, validation and lifecycle law;
- 37C — minimal built-in admitted registry;
- 37D — senses and exact term mappings;
- 37E — semantic classes and relation rules;
- 37F — structural-to-concept candidate proposal;
- 37G — disabled integration and closeout.

## Non-authority ruling

The presence of a concept-related record does not imply that the record is admitted, implemented, selectable, true, evidentially valid, routable, actionable, renderable or deliverable.
