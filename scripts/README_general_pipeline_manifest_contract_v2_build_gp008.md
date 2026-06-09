# GP-008 — Manifest Contract v2

## Purpose

GP-008 adds a separate, hash-bound RMC trace envelope that must exist before the production General Pipeline may render or Echo-deliver an approved answer. It deliberately does **not** modify MEA's `ProblemManifest` schema. MEA remains the problem-state layer; Manifest Contract v2 is the render-authority bridge linking sealed MEA state to RMC meaning and Echo-gated delivery.

## Runtime motion added by GP-008

```text
verified capability execution
→ governed gate passes
→ sealed MEA ProblemManifest
→ compiled RMC MeaningManifest
→ Manifest Contract v2 trace envelope
→ authorized deterministic renderer
→ Echo validation bound to v2
→ delivery authorization receipt
→ approved answer returned in-memory
```

## Trace fields introduced

Manifest Contract v2 records:

- formal claim type;
- source ancestry as in-memory governed instructional support;
- installed capability and Forge-owned service hashes;
- invocation and execution receipt hashes;
- exact verification receipt;
- open and sealed MEA manifest hashes;
- RMC meaning hash;
- typed AST and safe-adapter receipt linkage where the equation domain uses GP-007;
- Echo-gated render permission;
- in-memory rejection containment destination;
- explicit prohibitions on persistence, Identity Vault writes, Contribution Economy activity, CT minting and ledger writes.

## Boundaries held

GP-008:

- adds no new reasoning domain;
- installs or imports no third-party dependency;
- performs no corpus ingestion;
- creates no source-provenance records yet;
- makes no route or UI change;
- modifies no MEA modules;
- writes no persistent memory;
- writes nothing to Identity Vault;
- performs no Contribution Economy, CT or ledger action.

## Verification scripts

```bash
.venv/bin/python scripts/test_general_pipeline_manifest_contract_v2_build_gp008.py --forge-root "$HOME/forge"
.venv/bin/python scripts/general_pipeline_manifest_contract_v2_build_gp008_verify.py --forge-root "$HOME/forge"
```
