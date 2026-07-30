# Forge Operator Council v0

This package is an isolated, deterministic recommendation layer. It accepts an
already-selected semantic meaning envelope plus exact-reference RMC evidence.
It does not accept or parse raw text and does not call an LLM.

The fixed Council roles are:

1. semantic steward
2. RMC witness
3. authority auditor
4. adversarial challenger
5. synthesizer

The public adapter entry point is `convene_operator_council(envelope)`. A clean,
fully supported envelope can produce `RECOMMEND_FOR_OPERATOR_REVIEW`. Missing
RMC evidence, failed semantic gates, a failed/not-run Echo, uncertainty, or
contradiction produces `HOLD_FOR_EVIDENCE` with immutable dissent records.
The envelope reports the actual RMC connection separately from selected-meaning
support.  A structured snapshot without an adequate exact match remains
`NO_ADEQUATE_EXACT_SUPPORT` and cannot be upgraded into a recommendation merely
because some generic identifier overlaps.
Malformed envelopes and any request for raw text, tokenization, a model,
embeddings, vectors, similarity, memory writes, tools, actions, or delivery are
rejected before deliberation.

Every evidence envelope, member position, dissent, recommendation, boundary,
receipt, and complete result has a SHA-256-derived content identity. A Council
receipt is explicitly a recommendation-only disposition receipt: a human
operator decision remains required, and no decision or execution authority is
created.
