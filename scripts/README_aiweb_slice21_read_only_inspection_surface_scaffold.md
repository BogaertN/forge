# AI.Web Slice 21 — Read-Only API / Inspection Surface Boundary Scaffold

## Purpose

Slice 21 creates the read-only inspection boundary before any live API or
operator-console wiring is allowed.

This slice records that the system may expose inspection visibility for:

- meaning records
- law traces
- concept boundaries
- predicate frames
- gate records
- receipts
- accepted-scope status

## Core rule

Read-only inspection is not runtime authority.

API visibility is not acceptance.

UI visibility is not proof.

## What this slice adds

This slice adds a negative-authority scaffold only:

- immutable read-only inspection subject records
- immutable authority-separation records
- locked boundary laws
- deterministic receipt generation
- a CLI verifier
- a source behavior test

## What this slice does not add

This slice does not add:

- active route registration
- `main.py` modification
- operator-console modification
- config mutation
- tool registry mutation
- path authority mutation
- session-scope mutation
- UI integration
- runtime authority
- acceptance creation
- accepted-scope widening
- candidate promotion
- memory write
- memory authority
- tool routing
- tool invocation
- delivery
- transport
- action execution
- output approval
- renderer authority
- external resource admission
- resource fetch, download, ingestion, parsing, or indexing
- model, vector, retrieval, embedding, or RAG authority
- GP-014 modification, import, call, wrapping, promotion, or supersession
- GP-015 repair or revival
- release authority
- production deployment

## Verification

Run from the repository root after the payload has been copied into the
repository, before staging:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/nic/forge /home/nic/forge/.venv/bin/python3 \
  /home/nic/forge/scripts/test_aiweb_slice21_read_only_inspection_surface_scaffold.py

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/nic/forge /home/nic/forge/.venv/bin/python3 \
  /home/nic/forge/scripts/aiweb_slice21_read_only_inspection_surface_verify.py /home/nic/forge
```

The verifier accepts these contexts only:

- exact Slice 20 base HEAD with exactly the Slice 21 payload untracked
- exact Slice 20 base HEAD with exactly the Slice 21 payload staged
- clean committed Slice 21 context
- clean later descendant context after Slice 21 is an ancestor

The verifier fails closed for missing payload files, wrong context, dirty
committed context, prohibited imports, prohibited runtime fragments, or
boundary/receipt drift.
