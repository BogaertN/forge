# Slice 43A — RMC Echo Core Schema and Authority Boundary

This additive package defines record shapes and permanent non-authority
boundaries only. It performs no Echo decision.

Accepted parent: `ebe931909b59a40ac4ef202b89d8f4f2702104a3`
Expected future commit subject: `Slice 43A RMC Echo core schema and authority boundary`

## New package

`aiweb_language_core_bootstrap/rmc_echo_runtime`

## Live verification

Nic runs:

1. `scripts/test_aiweb_slice43a_rmc_echo_core_schema_and_authority_boundary.py`
2. `scripts/aiweb_slice43a_rmc_echo_core_schema_and_authority_boundary_verify.py --mode applied`

The verifier also runs the accepted Slice 42H verifier from an exact temporary
checkout of the protected parent. Nothing is staged or committed by these
scripts.

## Stop rule

After the applied-results packet is produced, stop. Upload the archive and its
SHA-256 sidecar for independent review. Do not stage or commit.
