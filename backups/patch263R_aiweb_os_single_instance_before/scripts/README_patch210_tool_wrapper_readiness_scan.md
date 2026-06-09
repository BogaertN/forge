# Patch 210 — Forge RMC Tool Wrapper Readiness Scan

This patch adds a read-only scanner:

`forge/scripts/rmc_patch210_tool_wrapper_readiness_scan.py`

It inspects whether Forge is ready to receive read-only RMC tool wrappers. It verifies Forge framework files, imports live RMC modules from `~/aiweb/runtime_wrappers/`, inspects callable surfaces, checks the tool registry trust level if available, and writes an audit report.

It does not modify Forge tools, agent code, AI.Web wrappers, Identity Vault, databases, or Gilligan wiring.

Report output:

`~/forge/memory/rmc_patch210_tool_wrapper_readiness_v1/latest_rmc_patch210_tool_wrapper_readiness.md`
