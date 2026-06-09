# Patch 300 - Contribution Economy Contract Foundation / No-Write Schema and Policy Kernel

## Purpose

Patch 300 installs the first implementation layer of the AI.Web Contribution Economy as a new sibling package:

```text
forge/contribution_economy_v1/
```

It is governed by the accepted `AI.Web Forge - Contribution Economy Production Implementation Contract and Runtime Build Plan v1.0` and by `AI.Web_ Breathing Life Into the New Memory Economy.pdf` for the Appendix A CT reward matrix, Appendix B Memory Capsule obligations, and Appendix C validation and minting requirements.

## What this patch actually implements

This patch adds real deterministic contract behavior:

- Locked contribution, influence, difficulty, ledger, lifecycle, and disabled-activation enumerations.
- Canonical JSON UTF-8 encoding with sorted keys, explicit null preservation, required schema version handling, and float rejection.
- Deterministic SHA-256 contract hash previews with explicit algorithm metadata.
- Integer-only Appendix A CT arithmetic using milli-CT and basis points.
- Disabled identity and consent reference contracts that keep Identity Vault authoritative and reject raw private identity fields from capsule/public-shaped payloads.
- Contract-only Contribution Event, validation, Memory Capsule, mint, Influence Ledger, Investment Ledger, nullification/correction, and lifecycle gate types.
- A verifier and behavior suite that prove the no-write boundary and compare the protected Patch 299 MEA state against its accepted hashes.

## Canonical CT policy implemented

```text
ct_reward_policy_version: ct_reward_policy_v1_memory_economy_appendix_a
1 CT = 1000 milli_ct

CRT: light=1000, standard=5000, heavy=20000, monument=60000 milli_ct
CPT: light=500,  standard=2000, heavy=8000,  monument=40000 milli_ct
BLD: light=2000, standard=10000, heavy=30000, monument=80000 milli_ct

Direct influence        = 10000 basis points
Indirect influence      =  5000 basis points
Collaborative influence =  3300 basis points
```

The policy is calculated only as a preview. Patch 300 never mints CT.

## Files added by this overlay

```text
forge/contribution_economy_v1/__init__.py
forge/contribution_economy_v1/contracts/__init__.py
forge/contribution_economy_v1/contracts/enums.py
forge/contribution_economy_v1/contracts/canonical_json.py
forge/contribution_economy_v1/contracts/hashing.py
forge/contribution_economy_v1/contracts/ct_reward_policy.py
forge/contribution_economy_v1/contracts/identity_reference_schema.py
forge/contribution_economy_v1/contracts/contribution_event_schema.py
forge/contribution_economy_v1/contracts/capsule_schema.py
forge/contribution_economy_v1/contracts/validation_schema.py
forge/contribution_economy_v1/contracts/ledger_schema.py
forge/contribution_economy_v1/contracts/nullification_schema.py
forge/contribution_economy_v1/contracts/lifecycle.py
forge/scripts/README_300.md
forge/scripts/patch300_verify.py
forge/scripts/test_patch300_contribution_economy_contract_foundation.py
forge/SHA256SUMS.txt
```

## Hard boundaries

Patch 300 performs no runtime economic activity:

```text
No API route exposure
No forge/main.py modification
No forge/rmc_engine_v1/mea/ modification
No forge/runtime_state/ modification
No Forge/RMC memory write
No JSONL contribution ledger write
No Chroma write
No Identity Vault write
No Contribution Event persistence
No Memory Capsule creation or finalization
No CT mint
No Influence Ledger entry
No Investment Ledger entry
No nullification/correction execution
No fraud strike, freeze, penalty, or burn
No public renderer output
No LLM call
No shell/subprocess execution from runtime modules
No network I/O from runtime modules
```

## Verification command after reviewed overlay application

From the Forge root:

```bash
cd ~/forge
PYTHONDONTWRITEBYTECODE=1 python scripts/patch300_verify.py
PYTHONDONTWRITEBYTECODE=1 python scripts/test_patch300_contribution_economy_contract_foundation.py
```

A passing result confirms the contract kernel only. It does not authorize a future patch or activate a Contribution Economy record.
