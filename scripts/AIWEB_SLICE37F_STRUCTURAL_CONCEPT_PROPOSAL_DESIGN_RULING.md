# Slice 37F Design Ruling

## Ruling

Install one isolated, immutable and deterministic structural-to-concept candidate proposal package.

## Authority basis

The canonical production roadmap requires the accepted Slice 36G structural result to consult the controlled registry through exact source spans and structural ancestry, under an explicit profile, and to return zero, one or multiple concept and sense candidates or an explicit unknown/unsupported result.

Document 4 requires surface expression, controlled lexical reference, concept identity, sense identity and occurrence-level interpretation to remain distinct. It prohibits similarity, frequency, model inference and convenient fallback from becoming concept authority. Document 9 requires deterministic proof, ambiguity preservation, unknown/unsupported preservation, non-LLM behavior and negative-authority testing.

## Input decision

Slice 36G preserves source-event identity, hashes, span references and structural ancestry but intentionally does not embed the complete exact received source text. The exact source text remains owned by Slice 36A and its code-point/byte/source-span projection remains owned by Slice 36B.

Therefore the lawful Slice 37F operation consumes the matching immutable 36A, 36B and 36G results together. It rejects mismatched identities, hashes, projection references, custody references or invalid predecessor records. It does not read a file, search history, inspect memory or reconstruct source from an ungoverned location.

## Matching decision

The admitted Slice 37D registry contains exact case-sensitive ASCII lexical references. Slice 37F uses a closed ASCII identifier-boundary profile:

- start/end of source are valid boundaries;
- an adjacent ASCII letter, digit or underscore blocks a boundary;
- all other exact adjacent characters are delimiters;
- every exact occurrence is preserved;
- overlapping candidates are not ranked;
- candidate ordering is source coordinate followed by immutable lexical identity.

This prevents the domain term `concept` from being silently promoted out of the admitted internal identifier `concept_admission` while allowing the exact internal identifier itself to map.

## Candidate decision

A proposed concept or sense candidate is a read-only availability record tied to:

- one exact lexical occurrence;
- its exact lookup request/result;
- every mapping identity/version that raised it;
- one exact registry snapshot;
- every applicable structural candidate and its complete operator/scope/attachment/reference ancestry.

One candidate remains a candidate. Multiple candidates remain unresolved alternatives. No confidence, preference or selection field is populated.

## Unknown and unsupported decision

- No exact controlled lexical occurrence produces an explicit unknown result over the preserved source range.
- An admitted lexical reference with no mapping produces an explicit unmapped/unknown occurrence.
- A reviewed unsupported mapping produces an explicit unsupported occurrence.
- Invalid or mismatched predecessors produce a fail-closed unsupported result and no proposals.

Unknown is not guessed. Unsupported is not converted to false, rejected or failed.

## Deferred authority

The following remain outside Slice 37F:

- disabled integration and Slice 37 closeout: Slice 37G;
- predicate and participant-role authority: Slice 38;
- `CandidateMeaning`: Slice 39;
- selection, ambiguity disposition and clarification: Slice 40;
- rendering and delivery: later governed slices.
