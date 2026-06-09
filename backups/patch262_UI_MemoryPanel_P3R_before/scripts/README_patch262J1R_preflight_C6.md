# Patch 262J1R-Preflight-C6 — Echo Validator / V_t

C6 adds the read-only Echo Validator stage. It validates rendered output `R_t` against source manifest `μ_t` and emits `V_t`, the echo validation report.

The validator computes real preservation measurements:

- claim preservation
- phase-path preservation
- operator-path preservation
- drift-status preservation
- confidence/novelty metric preservation
- memory-link preservation
- schema integrity
- distortion penalty

Formula:

`echo_score = 0.24*claim + 0.18*phase + 0.14*drift + 0.12*metrics + 0.12*memory + 0.10*operator + 0.10*schema - distortion_penalty`

C6 remains read-only. It does not write memory. A passing echo only routes to a future Memory Writer dry-run.
