# Patch 258C — Visible Terminal Launcher Fix

## Purpose

Patch 258B created the desktop icon and launcher. On some Ubuntu/GNOME setups the launcher can open the browser while leaving Forge terminal invisible or already running in another session. Patch 258C corrects that desktop behavior.

## Behavior

The AI.Web OS Desktop Launcher now always opens a visible terminal first, then opens:

`http://localhost:7477/operator-console`

If Forge is already running, the terminal shows that Forge is live and leaves the user at a normal shell in `~/forge`.

If Forge is not running, the terminal starts `python main.py`, auto-selects scope `2` for `/home/nic/aiweb`, runs the existing `forge-ui-start` command, and then remains the visible live Forge terminal.

## Boundary

- Does not patch `forge/main.py`.
- Does not patch `forge/config/tool_registry.json`.
- Does not add Forge commands.
- Does not bypass Forge.
- Does not give the browser shell access.
- Does not write Identity Vault or RMC live memory.

This is a local desktop convenience launcher only.
