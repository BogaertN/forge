# AI.Web Slice 35B — MeaningStructureManifest Deterministic Validation

Slice 35B adds one public validation submodule:

`aiweb_language_core_bootstrap.meaning_structure_manifest.validation`

It validates the immutable Slice 35A records without changing their construction contracts or root package export surface.

## Included

- required non-empty values;
- deterministic type checks;
- conservative local identifier checks;
- fixed schema, package, record-kind and lifecycle-state identity checks;
- tuple and duplicate-value checks;
- same-lineage enforcement;
- duplicate record-ID and identifier-collision detection;
- internal reference existence and expected-record-kind checks;
- explicit immutable validation issues and reports;
- a fail-closed assertion helper.

## Transparent implementation mapping

Document 2 expressly defers final identifiers and storage representation. Slice 35B therefore treats manifest, lineage and record IDs as conservative local textual identifiers and treats external object or receipt references as opaque non-empty text. This mapping is an implementation decision, not a claim that Document 2 prescribed Python field syntax.

## Excluded

Slice 35B does not include lifecycle transition authorization, transition matrices, successor construction, serialization, deserialization, migration, persistence, memory writes, bootstrap activation, runtime routes, APIs, UI, resource ingestion, LLMs, embeddings, vectors, RAG, tool invocation, delivery or state-changing action.

A transition trace is checked only for record existence and truthful state labeling. Whether a transition is permitted belongs to Slice 35C.
