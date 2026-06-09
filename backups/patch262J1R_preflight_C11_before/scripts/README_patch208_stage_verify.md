# Patch 208 Verifier

`rmc_stage208_verify.py` checks the staged missing RMC modules without moving them into live runtime paths.

It performs:

1. Python compile checks.
2. Unit tests for phase parser, drift detector, and echo validator.
3. Compatibility imports for both the existing orchestrator names and the logical architecture names.
4. A small phase → drift → echo smoke test.

Reports are written to:

`~/forge/memory/rmc_stage208_verification_v1/`
