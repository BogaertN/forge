# Patch 229B — RMC Namespace Scaffold Verification

Purpose: add verification-only Forge commands for the RMC namespace scaffold created by Patch 229A.

New commands:

- `forge-rmc-namespace-scaffold-verify`
- `forge-rmc-namespace-scaffold-verify-report`

Boundary:

- Reads the latest Patch 229A apply report.
- Verifies all recovered scaffold paths exist as directories.
- Writes only Forge-owned verification reports under `/home/nic/forge/memory/rmc_patch229b_namespace_scaffold_verify_v1/`.
- Does not create new RMC directories.
- Does not write RMC memory records.
- Does not touch Identity Vault or its database.
- Does not read `.env` values.
- Does not activate agents.

Expected verifier output:

`PATCH229B_VERIFY_PASS`
