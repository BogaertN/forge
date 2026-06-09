# Patch 242 — Terminus Tabbed Shell Prototype

Purpose:
Adds the first tabbed operator-console shell to Forge Terminus.

This patch modifies the embedded Terminus HTML only.

It adds:
- top tab strip
- static placeholder panels for the future cockpit
- ProtoForge Simulations tab placeholder
- Identity Vault tab placeholder
- EchoForge tab placeholder
- RMC Memory tab placeholder
- Context Library tab placeholder
- Audit / Receipts tab placeholder
- System Status tab placeholder

It does not add Forge CLI commands.
It does not modify the command surface.
It does not change the ProtoForge connector.
It does not write Identity Vault.
It does not write RMC live memory.
It does not run simulations automatically.
It does not add 3D yet.

After install:
1. Run forge-command-surface and confirm the count is unchanged.
2. Start forge-ui-start.
3. Refresh http://localhost:7477.
4. Confirm the tab strip is visible.
5. Confirm ProtoForge sidebar buttons still work.
