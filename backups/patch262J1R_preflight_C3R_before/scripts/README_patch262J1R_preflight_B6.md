# Patch 262J1R-Preflight-B6 — RMC Trace Spine + Memory Recaller

Purpose: redirect the build back to the actual Recursive Manifest Compiler application core.

This patch adds a read-only Memory Recaller and Trace Spine backend. It does not touch UI, does not call an LLM, does not render final language, does not write memory, does not mutate canonical reference files, does not query Chroma, and does not execute shell.

New engine module:

- `forge/rmc_engine_v1/memory_recaller.py`

New endpoints:

- `GET /api/rmc/memory-recaller`
- `GET /api/rmc/trace-spine`

What it implements:

- `I_t` input event assembly
- `M_t` active memory set from context-library receipts, collection manifests, symbolic maps, and dataset-growth records
- `Φ_t` phase state from the Phase Parser
- `D_t` drift state from the Drift Analyzer
- read-only symbolic trace object through the Drift Analyzer stage

What it does not implement yet:

- Candidate Conclusion Generator
- Evolutionary Drift Explorer
- full Coherence Scorer beyond existing gate preview
- Correction Engine
- Naming Engine
- true final Manifest Compiler authority
- Renderer
- Echo Validator
- Memory Writer

Those must come after this trace/memory spine is verified.

Runtime law:

Reference folder = law.
Growth dataset = observations.
Memory Recaller = active recall field.
Trace Spine = audit spine.
Renderer/LLM = downstream optional expression, not the center.
