# Slice 39G — MeaningStructureManifest Candidate Integration

This increment adds one isolated package:

`aiweb_language_core_bootstrap.candidate_meaning_construction.manifest_candidate_integration`

The public runtime entry point is:

`integrate_candidate_meanings_into_manifest(...)`

It accepts only an exact validated Slice 39F constructor result and returns an
immutable candidate-only MSM-v1 integration result.

The existing Slice 35 package is not modified. The exact source inspection
requires a versioned companion because the accepted MSM-v1 candidate record is
a safe projection but cannot losslessly contain all Slice 36-39F provenance,
receipt, limitation, and alternative families.

Run the visible verifier through the supplied external patch runner. No file is
staged or committed by the patch or test runner.
