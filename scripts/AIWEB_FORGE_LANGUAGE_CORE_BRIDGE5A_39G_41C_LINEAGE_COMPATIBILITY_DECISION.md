# AI.Web Forge Bridge 5A Decision

## Decision

Do **not** connect the full Bridge 5 gate-and-eligibility runtime yet. The live post-Bridge-4 source proves a narrow incompatibility between the accepted Slice 39G output and the Slice 41C input validator.

Slice 39G intentionally preserves two lineage domains:

1. `CandidateMeaningRecord.lineage_id` is the MSM candidate-manifest lineage.
2. `CandidateMeaningManifestCompanionV1.candidate_lineage_id` is the original source CandidateMeaning lineage.

Slice 41C incorrectly required those two distinct identifiers to be equal. That equality is not part of the exact record/companion link and rejects the real Slice 39G product.

Bridge 5A removes only that invalid equality. Exact linkage remains enforced through the manifest record ID, candidate meaning ID, candidate state ID, companion ID, identity/content/provenance references, construction receipt, source-expression reference, and Slice 40H custody ancestry.

## Authority boundary

This correction does not select meaning, rank candidates, grant permission, route a tool, execute an action, write memory, render output, invoke an LLM, or run a simulation.

## Required predecessor

- HEAD: `492d85032342aabbcf328b15110bc34b19ec8ca2`
- Parent: `1ef21fd10b64488f4cfb82a994770536a71d0842`
- Tree: `88fed500d7f085aed0eddf146ddef8d3cbd8bd05`
- Source packet SHA-256: `1090afa3beb06e31a0726788442fdc4015948559ea1dd062fa43b9b9df7001a2`
