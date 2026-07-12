# AI.Web Slice 18R1 Verifier Context Correction

This patch packet is external-only until a later authorized application phase.

## Purpose

Slice 18 committed successfully at `7046051567b5d82c98811f64b2413e746da70a97`, but the original Slice 18 verifier was anchored to the pre-commit state. After the commit, it correctly failed three identity checks that expected HEAD, parent, and subject to still describe Slice 17.

This correction updates the verifier so it accepts two lawful contexts:

1. **Slice 18 pre-commit patch context**: repository HEAD is the accepted Slice 17 base and status is limited to the Slice 18 additive paths.
2. **Slice 18 post-commit or later clean descendant context**: the accepted Slice 18 commit is an ancestor of HEAD, the working tree is clean, and the Slice 18 commit itself contains exactly the expected 9 additive paths.

## Boundary

This patch does not modify GP-014, GP-015, renderer evidence paths, runtime code, routing, UI, memory, corpus, model, retrieval, training, release, or production integration.

GP-014 remains preserved, protected, referenced only, not wrapped, not imported, not called, not modified, not superseded, and not promoted.
