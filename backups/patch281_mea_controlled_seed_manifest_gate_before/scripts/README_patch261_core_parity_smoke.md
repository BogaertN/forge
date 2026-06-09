# Patch 261 — Operator Console Core Parity Smoke Test

Purpose: freeze and verify the Operator Console Core Parity phase before expanding into deeper panels.

Adds read-only endpoint:

GET /api/operator/core-parity-smoke

The endpoint checks the core production console wiring in-process:

- Operator Console route strings exist
- output-state route/function exists
- safe command bridge state exists
- LLM request bridge remains proposal-only
- Page Capture remains scoped to Forge browser memory
- Patch Workflow remains read-only
- Audit / Receipts remains read-only
- Left rail command launcher boundary remains safe/gated
- Right rail runtime status remains read-only
- ProtoForge and Identity Vault status surfaces are readable
- command count remains 852 when Forge status reports current runtime data
- safe/gated browser counts remain 28/7

Authority boundary:

- does not execute commands
- does not run shell
- does not call LLM
- does not run simulations
- does not write files
- does not write Identity Vault
- does not write RMC live memory
- does not add Forge commands

If the live endpoint returns status OK, continue to Patch 262 — RMC Memory Panel v1.
