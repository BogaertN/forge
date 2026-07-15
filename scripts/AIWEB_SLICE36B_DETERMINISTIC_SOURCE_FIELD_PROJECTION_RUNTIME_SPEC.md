# AI.Web Slice 36B — Deterministic Source-Field Projection

## Status

Bounded implementation specification for the post-36B0 source projection.

## Purpose

Slice 36B transforms one immutable, validated Slice 36A input-event record into
an exact, reversible and non-semantic source field. The projection is linked to
the inert Slice 36B0 field-envelope result. It supplies exact source operands
for later structural and RSOC/FBSC work without activating any operator.

This is not an NLP token stream, vocabulary layer, part-of-speech layer,
learned parser, semantic layer or meaning layer.

## Accepted predecessor chain

1. Slice 36A preserves the exact received text, strict UTF-8 bytes, source hash,
   byte/code-point boundaries, source-event identity and unsupported custody.
2. Slice 36B0 creates an immutable unprojected field envelope for supported
   input and keeps every RSOC operator contract disabled.
3. Slice 36B creates an additive projection record. It does not modify either
   accepted predecessor record.

## Source-field records

The package creates immutable records for:

- projection limits;
- one exact code-point atom per Unicode scalar;
- every code-point and UTF-8 byte boundary;
- conservative grapheme-boundary availability;
- visible whitespace and repeated whitespace;
- tabs;
- line breaks, including CRLF as one visible line-break sequence;
- paragraph boundaries formed by two or more line-break sequences separated
  only by horizontal whitespace;
- punctuation marks;
- delimiters;
- quotation marks;
- operator-like visible symbols that explicitly carry no RSOC binding;
- control characters;
- unsupported code points;
- typed projection and reconstruction results.

Every atom preserves exact text, exact UTF-8 hex bytes, source-event identity,
source span, code-point offsets, byte offsets, Unicode scalar value, Unicode
category, Unicode name, combining class, support status, ordering and adjacency.

## Reversibility

Reconstruction concatenates the exact UTF-8 bytes stored by ordered code-point
atoms. Acceptance requires:

- contiguous code-point offsets;
- contiguous byte offsets;
- strict UTF-8 decoding;
- exact code-point length;
- exact byte length;
- exact source SHA-256;
- exact original text.

NFC and NFD forms remain distinct. No normalization, casefolding, whitespace
collapse, spelling repair, transliteration, replacement or approximation is
permitted.

## Grapheme-boundary law

Python's standard library does not expose the complete Unicode UAX #29
Grapheme_Cluster_Break and Extended_Pictographic tables. Slice 36B therefore
must not pretend to provide authoritative segmentation for all Unicode.

The closed v1 profile provides exact grapheme boundaries only for ASCII,
including the exact CRLF non-boundary. Boundaries touching non-ASCII code
points are recorded as `unavailable`. Exact code-point and byte boundaries
remain available and fully reversible for every valid UTF-8 source.

This limitation is visible, deterministic, versioned and non-destructive.

## Unsupported material

Valid-but-unsupported Slice 36A events are still projected so every unsupported
code point remains visible. Their result is
`SOURCE_FIELD_PARTIALLY_UNSUPPORTED`, their predecessor 36B0 envelope remains
held, and structural progression remains false.

Unsupported source is never deleted, repaired, normalized, transliterated or
silently recast as supported.

## Typed public outcomes

- `SOURCE_FIELD_SUPPORTED`
- `SOURCE_FIELD_PARTIALLY_UNSUPPORTED`
- `SOURCE_FIELD_MALFORMED`
- `SOURCE_FIELD_LIMIT_EXCEEDED`
- `SOURCE_FIELD_PROJECTION_FAILED`

No raw exception is the public disposition for invalid input, invalid limits,
tampered custody, Unicode-version drift, record-limit exhaustion or failed
reconstruction.

## Permanent prohibitions

Slice 36B does not identify or assign:

- words or lexical tokens;
- nouns, verbs, adjectives or parts of speech;
- commands, requests or questions;
- concepts, predicates, participants or targets;
- negation, prohibition or permission;
- references;
- RSOC operators;
- phases;
- intention;
- meaning.

A span containing `install` is not classified as an action. A span containing
`not` is not classified as negation or prohibition.

## Runtime boundary

The package is explicit-import only, standard-library only, in-memory only and
o-action safe. It performs no filesystem read/write, environment lookup,
network access, model call, retrieval, embedding, vector operation, database
operation, memory read/write, route registration, API activation, tool routing,
action, rendering or delivery.

It imports and calls no legacy RMC language surface and does not substitute the
MEA operator engine for language authority.
