# AI.Web Slice 18 GP-014 Preservation / Wrapper Decision Scaffold

Slice 18 is an additive, boundary-only scaffold. It records the architectural
relationship between GP-014 and the later output/expression boundary stack.

## Decision

- GP-014 is preserved.
- GP-014 is protected.
- GP-014 is unsuperseded.
- GP-014 is referenced only.
- GP-014 is not wrapped at Slice 18.
- GP-014 is not imported by Slice 18.
- GP-014 is not called by Slice 18.
- GP-014 is not modified by Slice 18.
- GP-014 is not promoted by Slice 18.

## Hard boundary

GP-014 is not:

- general language authority,
- concept authority,
- predicate authority,
- source authority,
- selected-meaning authority,
- full RMC authority,
- renderer authority,
- output approval,
- delivery authority,
- runtime authority,
- Echo authority,
- production integration,
- or a supersession path.

## Why no wrapper

Wrapping GP-014 at this point could accidentally look like promotion into a
broader renderer or general language authority. Leaving it completely unnamed
would leave later slices ambiguous. Slice 18 therefore records the middle path:
GP-014 is referenceable evidence and protected baseline only.

## Records

The scaffold defines:

1. `GP014ReferenceRecord`
2. `GP014WrapperDecisionRecord`
3. `GP014PreservationReceiptRecord`

The reference record binds exact accepted GP-014 paths and SHA-256 hashes. The
wrapper decision record freezes `no_wrapper_at_slice18`. The preservation receipt
records that GP-014, GP-015, Slice 17, and renderer evidence were not converted
into new authority.

## Explicit exclusions

This scaffold does not modify, import, call, wrap, supersede, or promote:

- `rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py`
- `rmc_engine_v1/general_pipeline/symbolic_math_operator_language_realizer.py`
- `rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json`
- GP-014 tests or verifier
- GP-015
- renderer files
- Slice 17 expression-boundary files
- `main.py`
- `requirements.txt`
- config, registry, dependency, route, UI, memory, model, vector, retrieval,
  RAG, network, release, or production paths

Any future wrapper or supersession requires a separate formal authorization path.
