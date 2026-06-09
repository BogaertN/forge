# Patch 262F — RMC Phase Parser Read-Only

Adds GET /api/rmc/phase-parser as the first real Recursive Manifest Compiler module after preview scaffolding. It builds a dry-run Input Event and Φ1–Φ9 phase interpretation from either operator input or an allowlisted selected memory object. It does not execute commands, call LLMs, query Chroma, read DB files, write files, or mutate RMC live memory. Patch 262G should implement the drift analyzer anchored to memory/drift.py and ProtoForge2 memory-drift rules.
