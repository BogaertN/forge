# Patch 262I1 — RMC Formal Math Binding / Scoring Contract

This patch keeps `/api/rmc/coherence-gate` read-only but binds the Coherence Scorer to an explicit RPMC/FBSC scoring contract.

It exposes the formal score terms: trace anchor, echo alignment, phase validity, candidate confidence, bounded novelty, identity anchor, ε_s, destructive drift, limitation load, ghost-loop pressure, and circuit-breaker pressure.

It also exposes cold storage and dream-state quarantine contracts. No file write, memory write, projection, renderer output, shell, LLM call, Chroma query, or DB read is added.
