# Slice 37B operator notes

Slice 37B is a read-only validation and lifecycle-law surface. Importing the
subpackage performs no work. Callers explicitly construct immutable Slice 37A
resources, authority records and transition records, then call:

- `validate_governed_resource`;
- `evaluate_lifecycle_transition`;
- `validate_governance_batch`;
- the corresponding `assert_*` fail-closed helpers.

A passing result means only that the supplied records conform to the bounded
Slice 37B contract. It does not perform the transition, populate a registry, or
establish runtime authority.

The package uses the Python standard library only and must remain free of LLM,
embedding, vector, RAG, learned-parser, neural-classifier, network, filesystem,
process, route, tool, memory, action, rendering and delivery behavior.
