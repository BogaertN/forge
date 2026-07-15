# Slice 36B implementation note

Slice 36B adds the explicit package:

`aiweb_language_core_bootstrap.source_field_projection`

It consumes validated Slice 36A custody records and deterministically creates
ordered code-point atoms, boundaries and visible-source observations. The
projection links to the Slice 36B0 predecessor result but does not modify the
36B0 envelope or enable its operator registry.

The package is absent from the bootstrap root exports and performs no work on
import. Call `project_source_field(...)` explicitly with an immutable
`InputEventRecord`.

Use `reconstruct_source_field(...)` to produce a typed exact-byte and exact-text
reconstruction proof.

Unsupported source remains visible in a partially unsupported projection and
is held from structural progression.

The behavior test includes exact ASCII, CRLF, repeated whitespace, paragraph
boundaries, punctuation, delimiters, quotes, symbols, NFC/NFD distinction,
emoji, CJK, private-use characters, format characters, unsupported controls,
noncharacters, empty input, invalid records, record limits, tampering,
immutability, legacy isolation and booby-trapped side-effect surfaces.
