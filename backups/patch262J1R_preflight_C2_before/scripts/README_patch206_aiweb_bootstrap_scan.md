# Patch 206 — AI.Web Bootstrap Boundary Scanner

This patch adds a read-only scanner script:

`forge/scripts/aiweb_bootstrap_scan.py`

It checks the local machine for:

- Forge root and Forge agent framework files
- AI.Web runtime wrapper locations
- RMC module presence
- missing RMC modules reported by Claude: `phase_state_parser`, `drift_arbitrator`, `echo_gate`
- standalone `gilligan_agent` folder
- Identity Vault hygiene signals: `.env`, `node_modules`, database files
- ProtoForge2 and EchoForge candidate roots

It writes reports only under:

`~/forge/memory/aiweb_bootstrap_boundary_v1/`

It does not move, delete, import, execute, or modify project modules.
