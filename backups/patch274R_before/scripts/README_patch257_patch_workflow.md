# Patch 257 — Patch / Proposal Workflow Panel

Adds a read-only Operator Console endpoint and panel for inspecting Forge patch/proposal workflow state.

Backend endpoint:

- `GET /api/operator/patch-workflow`

Authority boundary:

- No shell execution
- No Forge command execution
- No LLM calls
- No file writes
- No Identity Vault writes
- No RMC live memory writes
- No new Forge CLI commands

The panel inventories proposal, apply-plan, and rollback directories and maps existing browser-safe/gated workflow commands. Actions still route through the existing Safe Command Runner or terminal gates.
