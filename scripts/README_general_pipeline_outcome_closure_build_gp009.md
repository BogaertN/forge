# GP-009 — Outcome Closure and Refusal Containment Contracts

## Purpose

GP-008 already routes successful existing-domain answers through the RMC-facing Manifest Contract v2 and Echo-bound DeliveryAuthorizationReceiptV2. GP-009 closes the remaining existing-domain production gap: non-delivery outcomes must be traceable rather than returning as blank or partially documented branches.

## New behavior

The General Pipeline now produces an in-memory, hash-bound `NonDeliveryOutcomeReceiptV2` for each modeled non-delivery state:

- `REFUSED_UNLEARNED` at routing, missing-capability, missing-source-support, or defensive full-parse refusal stages.
- `GATE_BLOCKED` after bounded execution but before render authority may form.
- `ECHO_REJECTED` after a Manifest Contract v2 exists but faithful delivery is rejected.

Successful `ANSWERED` results continue to use the sealed GP-008 `DeliveryAuthorizationReceiptV2`; GP-009 does not replace or weaken that receipt.

## Files modified

- `rmc_engine_v1/general_pipeline/__init__.py`
- `rmc_engine_v1/general_pipeline/pipeline.py`

## Files added

- `rmc_engine_v1/general_pipeline/outcome_contract_v2.py`
- `rmc_engine_v1/general_pipeline/gp009_outcome_closure.py`
- `scripts/test_general_pipeline_outcome_closure_build_gp009.py`
- `scripts/general_pipeline_outcome_closure_build_gp009_verify.py`
- `scripts/README_general_pipeline_outcome_closure_build_gp009.md`
- `scripts/MEA_GENERAL_PIPELINE_BUILD_GP009_DELIVERY_MANIFEST.json`

## Locked boundaries

GP-009:

- adds no new problem domain;
- installs or imports no third-party dependency;
- does not modify MEA modules;
- does not ingest a corpus;
- does not create an external provenance registry;
- does not change routes or UI;
- does not write persistent memory;
- does not write Identity Vault;
- does not create Contribution Economy events;
- does not mint CT;
- does not write ledgers.

The containment receipts are in-memory proof objects only. They explicitly deny human-text delivery on the refused/blocked/rejected path and explicitly deny persistent memory, identity, or economic side effects.

## Verification intent

After installation, the verification bundle must show:

- GP-001 through GP-008 regressions remain passing;
- GP-009 behavior and verifier pass;
- unsupported inputs are trace-refused rather than answered;
- blocked and Echo-rejected paths are trace-contained;
- successful delivery still requires the GP-008 delivery authorization;
- no new write/economic/dependency/corpus authority exists.
