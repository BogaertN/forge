# AI.Web Slice 36F — Explicit Context and False-Authority Conversion Decision

## Decision

Slice 36F may constrain candidate trails and produce exact context-linked reference candidates, but it may not resolve a referent or convert surface structure into authority.

## Explicit-context rule

A reference candidate may inspect only an immutable ActiveContextRegistry supplied as a direct function argument.

The runtime must not:

- search memory;
- search files;
- inspect repository history;
- search the web;
- use embeddings;
- use similarity;
- use an LLM;
- choose the nearest object;
- choose the most convenient object;
- choose an object because a capability exists.

No registry means MISSING_CONTEXT_REFERENCE.

An empty valid registry means UNRESOLVED_REFERENCE.

One exact registry match means ONE_SOURCE_SUPPORTED_REFERENCE_CANDIDATE.

Multiple exact matches mean MULTIPLE_REFERENCE_CANDIDATES.

A request for prohibited context dependencies means PROHIBITED_CONTEXT_DEPENDENCY and performs no lookup.

## Reference candidate is not resolution

Even one exact match remains a candidate. Slice 36F sets no selected context entry and performs no reference resolution.

Concept and sense identity remain outside this slice.

## Scope and authority rule

Scope is applied as an additive immutable constraint view over Slice 36E trails. The predecessor trail is never mutated.

Question marks do not create commands.

Prohibitory surfaces do not create permission or action.

Quotation containment does not activate quoted instructions.

Loop-seal surfaces do not prove real-world completion.

Context metadata marked private, failed, rolled back, drafted, tested, partial, or otherwise bounded remains exactly bounded. No stronger status is inferred.


The following conversions are explicitly prohibited:

- possibility becoming certainty;
- question becoming command;
- request becoming permission;
- proposal becoming implementation;
- drafted becoming accepted;
- tested becoming verified;
- verified claim becoming world truth;
- failed becoming successful;
- rolled back becoming active;
- quoted instruction becoming active instruction;
- private becoming releasable;
- partial evidence becoming universal proof;
- recognized capability becoming authorized capability.

## Production consequence

Any later slice that wants concept, predicate, capability, route, action, delivery, or release authority must consume these constraints and independently prove its own authority. Slice 36F grants none.
