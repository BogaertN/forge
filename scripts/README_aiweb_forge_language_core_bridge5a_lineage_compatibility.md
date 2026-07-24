# AI.Web Forge Bridge 5A

This package corrects one live-source compatibility defect between Slice 39G candidate custody and Slice 41C selection-eligibility validation.

Apply and acceptance are separate operations. The apply tool changes only the sealed payload and does not run tests, start Forge, stage, commit, or push. The result collector runs the new real-chain test and the existing Slice 39G and Slice 41C regression suites without starting Forge.

A successful Bridge 5A result does not authorize selected-meaning construction. It only proves that the real candidate record and companion can enter the existing eligibility validator without conflating their distinct lineage domains.
