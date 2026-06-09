# Patch 209 Integrated RMC Verifier

Run from `~/forge` after extracting Patch 209:

```bash
python scripts/rmc_patch209_verify.py
```

The verifier compiles the installed RMC modules, runs unit tests for the newly installed missing modules, runs the integrated orchestrator test suite, and writes a report to:

`~/forge/memory/rmc_patch209_integrated_verify_v1/`
