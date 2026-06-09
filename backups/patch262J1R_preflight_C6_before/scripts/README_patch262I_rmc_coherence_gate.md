# Patch 262I — RMC Coherence Scorer + Correction/Naming Gate

Adds `/api/rmc/coherence-gate` as a read-only dry-run module. It consumes Candidate Conclusion output, scores candidate meaning states, and previews Φ6 correction and Φ7 naming gates before any manifest or renderer path. No commands, shell, LLM, Chroma, DB reads, file writes, Identity Vault writes, or RMC live writes.
