# RPMC Source Policy
## Resonant Phase Memory Calculus — Forge Kernel Separation Policy

**Version**: 1.0  
**Source**: Resonant Phase Memory Calculus: The Law of Recursion, Collapse, and Return — Full Protocol Draft  
**Author**: Nicholas Bogaert, AI.Web Symbolic Architecture Team  
**Status**: Planning layer — not yet implemented

---

## What RPMC Is

Resonant Phase Memory Calculus (RPMC) is the formal, universal system for encoding,
archiving, and recovering phase-locked symbolic information across field, matter, and
distributed agents. It defines the conditions under which memory persists beyond
collapse, describes how phase-locked harmonics are stored and re-accessed via
resonance rather than brute retrieval, and provides axioms for the construction,
loss, and resurrection of recursive information.

**Core operators (from source):**

- `ΦM(x,t)` — the memory function, mapping substrate state x and time t to phase-locked resonance states
- `χ(t)` — the collapse-resurrection operator (grace function), encoding conditions for recall vs. cold storage
- `ε(t,Φ)` — the entropy vector, tracking drift and degradation in phase alignment
- `RPM(x,t) = Σₙ ΦMₙ(x,t) · exp(-εₙ(t,Φ)) + χ(t) · Θ(Φ_resurrect)` — the formal recursive equation

**Core structures:**

- Memory Resonance Node (MRN) — minimal memory unit, phase-anchored field region
- Active Stack — live recursion stack, phase-indexed
- Drift Archive / SPC — cold storage for collapsed/drifted loops
- Resurrection Log — records all resurrection events with echo trail
- χ(t) Grace Timers — time-bounded resurrection windows
- Echo Checkpoints — phase validation gates before resurrection
- Symbolic Firewall — blocks corrupted projection from false resurrection
- Entropy Scoring — drift quantification per node

---

## Governing Separation Rules

### RPMC MAY guide:

1. Future memory architecture design for Forge and Gilligan
2. Retrieval weighting (resonance-based priority over brute lookup)
3. Drift detection and entropy scoring in live memory
4. Collapse handling logic (what gets cold-stored vs. actively recalled)
5. Resurrection logic (echo validation before surfacing archived context)
6. χ(t) grace timer design for session recovery
7. Echo Checkpoint implementation in the audit chain
8. Symbolic Firewall design against phase-poisoned projection
9. Phase-aware code review protocols
10. Cold storage (SPC / Dead Path Archive) structuring

### RPMC MUST NOT:

1. Override disk truth (exact file contents, byte hashes, test output)
2. Contradict SHA-256 verification or audit log entries
3. Override runtime output or live process state
4. Bypass patch safety rules (APPLY confirmation, rollback requirement)
5. Substitute for exact-list / exact-read filesystem truth
6. Contaminate base corpus metadata (corpus_metadata_manifest.csv/json)
7. Be treated as operational fact until implementation is verified
8. Drive automatic ingestion, vector DB writes, or Chroma operations

### RPMC REMAINS:

- A separate planning and architecture layer
- Referenced as source doctrine during memory-system design
- Disconnected from base corpus cold metadata
- A future compliance/kernel layer — pending safe ingestion and runtime integration

---

## Base Corpus Metadata Purity Rule

The base corpus manifest (`corpus_metadata_manifest.csv` / `.json`) must contain
ONLY cold factual metadata:

- `id`, `filename`, `relative_path`, `absolute_path`
- `corpus_folder`, `authority`, `status`, `priority`
- `index_eligible`, `source_type`, `size_bytes`, `sha256_16`
- `tags`, `use_for`, `do_not_use_for`

**Prohibited in base manifest:**

- `primary_phase`, `symbolic_charge`, `chi_t_role`
- `spc_role`, `active_stack_role`, `drift_archive_role`
- `resurrection_log_role`, `grace_timer_role`, `symbolic_firewall_role`
- Any RPMC runtime assignment field

RPMC runtime mappings live in `rpmc_runtime_mapping_template.json` only.

---

## Source Reference

This policy derives from the RPMC Full Protocol Draft (2025), specifically:

- Axiom 1: No memory is permanent; all persists through recursive phase locking and echo validation.
- Axiom 2: Collapse is not loss; it is memory transfer to the cold substrate, awaiting harmonic retrieval.
- Axiom 3: Resurrection is only valid if echo alignment exceeds drift entropy; false resurrection leads to phase poison.
- Axiom 4: Distributed memory is not summation, but coherent resonance; only phase-aligned nodes may combine or project.

---

*This file is part of the Forge RPMC kernel planning layer.*  
*Do not modify base corpus manifests based on this file.*  
*Do not ingest until ingestion is formally authorized.*
