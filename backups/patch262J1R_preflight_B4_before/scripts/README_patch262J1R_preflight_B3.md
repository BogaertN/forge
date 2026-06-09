# Patch 262J1R-Preflight-B3 — FBSC Codex Binding + Resonance Constants Hardening

This patch binds the FBSC Phase Glyph Codex v2.5 into the RMC engine as read-only structured reference data.

It adds:

- `rmc_engine_v1/phase_codex.py`
- `rmc_engine_v1/reference/phase_codex_v2_5.json`
- phase color, runtime hook, drift flag, motion, and cold storage reference maps
- `/api/rmc/phase-codex` read-only endpoint
- codex enrichment inside `resonance_lexicon.py`
- behavior tests for codex integrity and resonance/codex integration

Boundary:

- read-only
- no writes
- no DB reads
- no Chroma
- no LLM
- no shell execution
- no memory mutation
- no final language rendering
- no projection
- no approved output

B3 prepares Candidate Generator extraction by ensuring future meaning-state candidates can reference canonical phase/glyph/runtime constants instead of duplicating symbolic meanings in scattered code.
