# AI.Web Slice 8 Concept Boundary Scaffold

This scaffold adds deterministic boundary records for concept identity, sense identity, semantic classes, semantic relations, namespaces, provenance tags, version tags, and unknown-state handling.

It is not a resolver. It is not a graph engine. It does not admit external lexical resources. It does not import WordNet, Sanskrit WordNet, VerbNet, FrameNet, Universal Dependencies, or any dataset. It does not assign predicate roles, select gates, render output, write stored material, route actions, or change baseline status.

The scaffold exists so later slices can depend on explicit boundary objects instead of inventing concept authority inside downstream code.

Expected files:

- `aiweb_concept_boundary_scaffold/__init__.py`
- `aiweb_concept_boundary_scaffold/concept.py`
- `aiweb_concept_boundary_scaffold/relation.py`
- `aiweb_concept_boundary_scaffold/verify.py`
- `scripts/test_aiweb_slice08_concept_boundary_scaffold.py`
- `scripts/aiweb_slice08_concept_boundary_verify.py`
- `scripts/README_aiweb_slice08_concept_boundary_scaffold.md`
