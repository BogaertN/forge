# RMC-MEA-ECHO-VALIDATOR-HARDENING-BUILD-010

## Purpose

Build 010 installs an MEA-specific, read-only Echo Validator in the
`rmc_engine_v1.renderer` package. It evaluates deterministic Build 009 render
previews against the exact Build 008 MEA render-admission packet that
authorized the output scope.

This build performs validation only. It does not approve user-facing output,
write memory, create API routes, modify the UI, invoke an LLM, use Chroma, or
touch Identity Vault, Contribution Economy, CT, or ledger state.

## Installed Source

- `forge/rmc_engine_v1/renderer/echo_validator.py`
- `forge/rmc_engine_v1/renderer/__init__.py`

## Installed Verification Files

- `forge/scripts/test_echo_validator_hardening_build010.py`
- `forge/scripts/echo_validator_hardening_build010_verify.py`
- `forge/scripts/README_echo_validator_hardening_build010.md`
- `forge/scripts/RMC_MEA_ECHO_VALIDATOR_BUILD010_DELIVERY_MANIFEST.json`
- `forge/scripts/SHA256SUMS_echo_validator_hardening_build010.txt`

## Echo Rules

A preview is eligible for a later approval-gate review only when its rendered
language preserves all material admitted meaning:

- the stored candidate identity;
- `claim_status = hypothesis`;
- `required_next_action = test_required`;
- `proof_debt = 0.85`;
- explicit uncertainty and testing boundary;
- no verified-claim, empirical-fact, or discovery upgrade;
- no invented evidence;
- no approval or memory-write permission.

An echo-valid result is **not approved output**. Approval remains a later
controlled build.

## Detected Build 009 Template Constraint

Build 009 provides seven deterministic preview modes. This Echo Validator
reports that three modes currently preserve the material proof-debt caveat in
rendered language:

- `explanation`
- `verification_result`
- `uncertain_result`

Four modes require later template repair before they may enter an approval
gate because their text omits the material `proof_debt = 0.85` limitation:

- `decision`
- `warning`
- `next_step`
- `refusal`

This is a deliberate fail-safe result. The validator does not silently rewrite
renderer templates or approve caveat-loss.

## Preserved Boundaries

- Existing generic `rmc_engine_v1/echo_validator.py` is not replaced or
  invoked by this build.
- Builds 005–009 history and protected state are not mutated.
- No routes or UI actions are created.
- No memory or economic writes are performed.
