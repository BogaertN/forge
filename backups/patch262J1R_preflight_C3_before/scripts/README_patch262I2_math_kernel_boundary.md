# Patch 262I2 — RMC Math Kernel Boundary / Engine Extraction

This patch corrects the architecture boundary for the RMC coherence scorer.

Before this patch, the endpoint logic and formal math lived directly in `forge/main.py`.
That was useful for proving the endpoint, but it was not professional final architecture.

This patch creates a side-effect-free engine module:

`forge/rmc_engine_v1/coherence_math.py`

The Forge endpoint remains the governed HTTP surface, but the math kernel now owns:

- threshold contract
- ε_s term extraction
- phase skip detection
- cold storage pressure
- ghost-loop pressure
- dream-state eligibility
- coherence score
- Φ6 correction gate
- Φ7 naming gate
- manifest dry-run eligibility gate

The module does not:

- run shell
- call an LLM
- query Chroma
- read DB files
- write files
- write RMC live memory
- project final language

This patch is intentionally not a UI feature. It is a professional architecture boundary patch.
