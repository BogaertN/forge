# Patch 262J1R-Preflight-C1 — Candidate Conclusion Generator

Adds the first read-only Candidate Conclusion Generator module for the actual RMC application spine.

## New module

- `forge/rmc_engine_v1/candidate_generator.py`

## Updated endpoint

- `GET /api/rmc/candidate-conclusion`
- Alias: `GET /api/rmc/candidate-generator`

## What this stage does

It consumes the existing trace spine and produces `C_t`: candidate meaning states.

A candidate is not a sentence. It is a possible next state of meaning.

## What this stage does not do

- no LLM calls
- no final language rendering
- no projection approval
- no memory write
- no canonical reference mutation
- no shell execution
- no Identity Vault write

## Next stage

Patch C2 should add the Evolutionary Drift Explorer and/or stronger Coherence Scorer integration.


C1 repair note: fixes script import path so direct verifier tests can import rmc_engine_v1 from scripts/, and adds the real /api/rmc/candidate-generator dispatch branch. Backend only. No LLM, no UI, no writes.
