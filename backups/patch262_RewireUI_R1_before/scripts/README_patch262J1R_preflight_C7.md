# Patch 262J1R-Preflight-C7 — Memory Writer Dry-Run / W_t

C7 adds the Memory Writer Dry-Run stage. It consumes C6 Echo Validator output and returns either a deterministic `W_t` memory write plan or a blocked write candidate.

C7 is intentionally read-only. It does not write files, mutate RMC memory, update Chroma, touch Identity Vault, execute shell, call an LLM, or mutate canonical references.

The goal is to prove the exact memory write packet before a future gated writer exists.

Core formula:

`W_t = plan_memory_write(V_t, R_t, μ_t, T_t)`

Write eligibility formula:

`0.30*echo_score + 0.18*manifest_confidence + 0.14*drift_stability + 0.12*memory_support + 0.10*schema_integrity + 0.08*phase_closure + 0.08*source_confidence - novelty_risk_penalty - distortion_penalty`

C7 separates three conditions:

- algorithm failure: broken code/math
- gate refusal: upstream manifest/render/echo is blocked
- read-only refusal: write plan can be computed, but real mutation is deferred to gated writer

Endpoints:

- `/api/rmc/memory-writer`
- `/api/rmc/memory-write-dry-run`
- `/api/rmc/write-plan`

Expected weak-input behavior: if C4/C5/C6 are blocked, C7 returns `blocked_write_candidate` and writes nothing.
