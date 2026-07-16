# Slice 37D Controlled Sense and Exact Term-Mapping Runtime Specification

## Purpose

Slice 37D provides a closed, read-only semantic-resource registry over the four admitted Slice 37C concepts. It permits exact caller-supplied inspection of controlled lexical references and their zero, one, or multiple candidate concept and sense references.

## Exact lookup key

A lookup request is identified from all five caller-supplied fields:

1. exact form;
2. exact language tag;
3. exact concept namespace identity;
4. exact mapping namespace scope tuple;
5. exact domain scope tuple.

No field is trimmed, case-folded, corrected, stemmed, expanded, ranked, or inferred.

## Lookup dispositions

- `no_exact_lexical_reference`: no exact lexical reference matches.
- `unmapped_term`: an exact lexical reference exists, but no mapping exists for the exact namespace/domain scope.
- `mapped_one_to_one`: exactly one concept candidate is available.
- `mapped_one_to_many`: multiple candidates are available from an admitted one-to-many mapping.
- `ambiguous_mapping`: multiple materially distinct candidates remain under an ambiguous mapping state.
- `unsupported_mapping`: a reviewed mapping exists but has zero supported candidates.

All candidate tuples use deterministic registry order. Order carries no rank, preference, likelihood, confidence, or selection.

## Static proof records

### Senses

1. governed semantic resource identity;
2. source occurrence form;
3. metalinguistic expression mention;
4. human-approved semantic admission act;
5. missing admitted concept support condition.

### Lexical references

Four exact preferred English labels, four exact internal AI.Web identifiers, and three exact domain terms (`concept`, `mapping`, and `sense`). All are case-sensitive.

### Mapping examples

- Eight exact one-to-one mappings connect the four preferred labels and four internal identifiers to their bounded concept and sense candidates.
- The exact domain term `concept` preserves two concept candidates and two materially distinct sense candidates without ranking or selection.
- The exact domain term `mapping` remains known but unmapped.
- The exact domain term `sense` has a reviewed unsupported mapping because Slice 37C contains no admitted concept identity for controlled sense identity as a concept.

## Outward-expression boundary

The four preferred English labels have eligibility references for later outward-expression planning. Those references do not render, validate, release, deliver, or activate language.

## Prohibited expansions

The registry contains explicit refusal records for case folding, spelling correction, stemming, synonym expansion, nearest matching, frequency ranking, semantic similarity, embeddings, model inference, and ordinary-dictionary fallback.

## Runtime boundary

No source occurrence is inspected. No Slice 36 result is consumed. No CandidateMeaning, selected meaning, semantic class, graph edge, predicate frame, route, tool, memory operation, action, rendered output, or delivery event is created.
