# Patch 262F2 — RMC Workspace Toggle Fix

Frontend-only correction for the RMC Memory tab.

This patch keeps the RMC workspace as a one-active-module surface and fixes the interaction bug where clicking an already active module button did not collapse the module.

It does not modify `main.py`, add Forge commands, or change backend APIs.

Expected behavior:

- Click an RMC action once: that module opens.
- Click the same RMC action again: that module closes.
- Click a different RMC action: the workspace switches to that module.
- Click `Close Active Module`: the workspace returns to the waiting placeholder.
- The compiler contract remains a diagnostic gate, not final product UI.
