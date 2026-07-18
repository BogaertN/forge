# AI.Web Slice 39F Authority and Deferred-Scope Decision

## Accepted authority

Slice 39F owns one explicitly invoked, deterministic, in-memory constructor for
actual `CandidateMeaningState` and `CandidateMeaningConstructionReceipt`
records. It consumes only exact typed predecessor records from the accepted
Slice 36–38 chain. It reuses Slice 39C for complete predecessor custody, Slice
39D for candidate-only semantic-content assembly, and Slice 39E for zero, one,
or multiple candidate preservation.

The constructor may derive deterministic CandidateMeaning identity only from
the exact accepted CandidateMeaningContent and CandidateMeaningProvenance
records. It may assign only construction statuses: constructed, construction
incomplete, construction unknown, construction unsupported, construction
conflicted, or predecessor invalid. These are construction-custody states, not
verbal-cognition gate outcomes.

## Exact input boundary

The public constructor accepts only an exact tuple of
`CandidateMeaningConstructorInput` records. Each input contains exact accepted
typed predecessor results. A raw string, bytes, mapping, list, arbitrary object,
or predecessor record supplied in the wrong position fails closed.

The constructor does not inspect source text, tokenize language, create a new
structural analysis, choose a concept by similarity, select a sense, fill a
role, resolve a referent, repair unsupported language, or infer hidden intent.
The source text remains inside accepted source-custody records and is carried
only through exact predecessor validation and provenance.

## Zero, one, many, and duplicates

Zero inputs create an explicit zero-candidate constructor result. One valid
input creates one candidate state without selection. Multiple valid inputs are
assembled and passed through Slice 39E deterministic ordering and alternative
preservation. Exact duplicate occurrences remain in Slice 39E set custody but
do not fabricate multiple CandidateMeaning identities with identical governed
content and provenance.

## Permanent non-authority

Construction is not gate passage. A complete candidate is not selected meaning.
Multiple candidates are not an ambiguity disposition. A missing role is not a
clarification-required state. Unsupported construction is not refusal.
Candidate meaning is not truth, evidence, permission, capability availability,
route, invocation, action, memory access, rendering, or delivery.

No LLM, model, embedding, vector, RAG, semantic-similarity, nearest-known,
external-resource, filesystem, network, route, action, memory, rendering, or
delivery authority is installed.

## Exact continuation

- Slice 39G owns candidate-side MeaningStructureManifestV1 custody integration.
- Slice 39H owns disabled bootstrap integration and the final Slice 39 closeout.
- Slice 40 remains blocked until Slice 39H acceptance.

Slice 39F does not modify or adapt the accepted Slice 35 manifest. The exact
Slice 39G companion-record/adapter decision remains source-grounded and
unresolved until Slice 39G.
