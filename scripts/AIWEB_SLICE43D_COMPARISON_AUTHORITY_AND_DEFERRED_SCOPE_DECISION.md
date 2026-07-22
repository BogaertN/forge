# AI.Web Slice 43D Comparison Authority and Deferred-Scope Decision

## Decision

Slice 43D is authorized only to create deterministic, dimension-specific
meaning-preservation comparison findings from the exact accepted Slice 43C
admission and exact accepted Slice 42 ancestry.

## Authorized

- verify exact Slice 43C admission identity and validity;
- verify exact Slice 42 ancestry and cross-record custody;
- construct immutable source and proposed-expression snapshots;
- compare the 13 required dimensions;
- emit `preserved`, `changed`, `missing`, `unsupported`, `conflicted`, or
  `indeterminate` findings;
- create deterministic canonical identities, digests, evidence references, and
  trace references;
- reject malformed, unsupported, fabricated, mismatched, or raw-text inputs.

## Not authorized

- aggregate `PASS`, `REJECTED`, or `CONTAINED`;
- drift classification or materiality;
- rejection or containment issuance;
- expression correction, repair, rewriting, regeneration, or substitution;
- MSM-v1 mutation, migration, or validation-link integration;
- delivery authority or delivery;
- truth, evidence, permission, or execution authority;
- routes, APIs, network, filesystem, memory writes, tools, or actions;
- LLM, EchoForge, embedding, vector, RAG, similarity, neural-parser, or hidden
  classifier authority;
- GP-014 supersession.

## Later increments

- Slice 43E: drift classification and materiality;
- Slice 43F: disposition, rejection, and containment;
- Slice 43G: additive MSM-v1 validation-link custody;
- Slice 43H: disabled integration and Slice 43 closeout.

Structural validity, a preserved finding, or a complete finding set does not
self-authorize any later increment.
