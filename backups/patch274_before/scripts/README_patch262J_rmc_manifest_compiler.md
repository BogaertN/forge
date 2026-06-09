# Patch 262J — RMC Manifest Compiler Dry-Run

Adds `/api/rmc/manifest-compiler` and `forge/rmc_engine_v1/manifest_compiler.py`.

The endpoint is a thin adapter. The engine module owns manifest dry-run logic. It produces an internal manifest packet only when the math-bound coherence gate permits it; otherwise it returns a blocked preflight report. No final language, projection, file writes, model calls, DB reads, or RMC live memory writes occur.
