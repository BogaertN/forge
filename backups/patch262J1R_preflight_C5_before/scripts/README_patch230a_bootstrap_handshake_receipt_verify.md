# Patch 230A — Bootstrap Handshake Receipt Verification

Purpose: verify the Patch 230 dry-run handshake receipt/report before moving to activation preflight planning.

New Forge commands:

- `forge-bootstrap-handshake-verify`
- `forge-bootstrap-handshake-verify-report`

Boundary:

- Reads the Patch 230 Forge-owned dry-run report.
- Verifies the expected inactive-agent verdict: `HANDSHAKE_DRY_RUN_PROFILE_FOUND_BUT_INACTIVE`.
- Verifies `gilligan.local` remains `inactive_draft` and `is_active = False`.
- Verifies the resolved namespace path exists under the allowed RMC scaffold root.
- Verifies the manifest preview and echo-validation preview are present.
- Verifies no RMC memory write, no Identity Vault DB write, no activation, no ProtoForge2 execution, and no EchoForge creation.
- Writes only a Forge-owned verification report under `/home/nic/forge/memory/aiweb_patch230a_bootstrap_handshake_receipt_verify_v1/`.

Expected runtime verdict:

`VERIFIED_HANDSHAKE_DRY_RUN_RECEIPT_INACTIVE_GATE`

That verdict is a pass. It proves the dry-run receipt is valid and the system stopped for the correct reason.
