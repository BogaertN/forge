# AI.Web Frozen Legacy Call-Site Containment Correction

## Status

This is a narrow tracked correction for the Forge/RMC boundary at clean base
HEAD `7e1b9812471cc0422613b7b2316482123fb6f15c`.

It does not implement Slice 17.

## What this correction does

- Preserves `rmc_engine_v1/llm_renderer.py` byte-for-byte.
- Preserves `rmc_engine_v1/chroma_connector.py` byte-for-byte.
- Removes live and runnable imports/calls of those frozen modules.
- Keeps deterministic non-LLM output rendering.
- Restores deterministic filesystem-only memory recall.
- Explicitly rejects LLM, model-endpoint, model-selection, Chroma, vector,
  embedding, semantic, hybrid, automatic-backend, and RAG requests.
- Retires the old C15/C16 executable tests and verifiers in the live tree while
  retaining their original versions in Git history.
- Adds behavior and independent verification guards.

## What it does not do

It grants no LLM, model, vector, Chroma, RAG, evidence, truth, permission,
memory-write, tool, action, delivery, release, or production authority.

It does not modify GP-014, revive GP-015, install GP-015R1, admit an external
resource, or authorize Slice 17.

## Required verification sequence

The packet-level README and scripts control the operational workflow. Do not
copy this file by hand. Use the packet backup/apply/test/verify scripts only
after packet inspection.
