# Post-Bridge-4 Source Inspection Record

The source packet was independently verified before this package was built.

- Packet SHA-256: `1090afa3beb06e31a0726788442fdc4015948559ea1dd062fa43b9b9df7001a2`
- Current HEAD: `492d85032342aabbcf328b15110bc34b19ec8ca2`
- Archive members: 1267
- Unsafe archive members: 0
- Internal checksum records: 1151
- Internal checksum failures: 0

Observed live source:

- Slice 39G generates `CandidateMeaningRecord.lineage_id` from the MSM candidate-manifest lineage.
- Slice 39G writes `CandidateMeaningManifestCompanionV1.candidate_lineage_id` from `state.identity.lineage_id`, preserving the source CandidateMeaning lineage.
- Slice 41C validation required those fields to be equal.
- The existing Slice 41C fixture used the same literal lineage for both records and therefore did not test the live Slice 39G product.

The correction is limited to removing that one invalid equality and adding a real-chain regression test.
