# AI.Web Slice 39F

This increment adds the explicitly invoked deterministic CandidateMeaning
constructor required after Slice 39E and before Slice 39G.

## New package

`aiweb_language_core_bootstrap/candidate_meaning_construction/deterministic_constructor/`

The package contains seven files: authority, schema, canonical serialization,
identity, validation, constructor, and exports.

## Runtime boundary

The constructor accepts only exact typed predecessor records. It does not accept
raw text and does not invoke the source-capture, projection, structural,
concept-proposal, or predicate-proposal constructors. The accepted predecessor
records must already exist and must pass the accepted Slice 39C–39E validators.

## Acceptance boundary

This increment is not accepted by packaging or by isolated checks. Nic applies
the patch to `/home/nic/forge`, runs the visible Slice 39F verifier and inherited
language-core behavior tests, and returns the live result packet. Staging and
commit remain separate and require explicit authorization after evidence review.
