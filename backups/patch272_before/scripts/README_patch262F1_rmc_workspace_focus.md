# Patch 262F1 — RMC Workspace Focus / Contract Demotion

This patch is frontend-only.

It fixes the RMC Memory tab layout after Patch 262F by hiding inactive module panels instead of rendering empty boxes. It also demotes the compiler contract from a product-looking panel to a diagnostic build gate.

Boundary:
- No `main.py` change.
- No backend endpoint change.
- No Forge command added.
- No shell access.
- No Identity Vault write.
- No RMC live memory write.

Next real module remains Patch 262G — RMC Drift Analyzer Read-Only.
