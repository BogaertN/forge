# Patch 236 — Neo Manual Activation Dry-Run Gate

Purpose: add a Neo-only manual activation dry-run gate after Gilligan and Athena have both been activated, handshaken, and verified with controlled RMC test receipts.

Commands added:

- `forge-agent-activate-neo-dry-run`
- `forge-agent-activate-neo-dry-run-report`

Boundary:

- Dry-run only.
- No Identity Vault DB write.
- No RMC memory write.
- No activation.
- No secret reads.
- No autonomous execution.
- No EchoForge creation.
- No ProtoForge2 execution.

Expected command surface after install: `832/832`.

Expected dry-run verdict:

`NEO_MANUAL_ACTIVATION_DRY_RUN_READY`

This patch only previews the future mutation:

- `neo.local activation_state: inactive_draft -> active_governed`
- `neo.local is_active: 0/False -> 1`
- `neo.local last_validated_at: current UTC timestamp preview`

It also confirms Gilligan and Athena remain `active_governed` and that the Patch 235F Athena RMC `test_receipt` verification has passed.
