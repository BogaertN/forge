# Patch 263 — AI.Web OS Desktop App Orchestrator

This patch replaces the manual Vite-terminal workflow with a managed desktop app launch path.

## Behavior

- Builds `/home/nic/aiweb/apps/forge-operator-console` to static `dist/` when needed.
- Starts Forge/Terminus in a managed background PTY if port `7477` is not already running.
- Opens `/operator-console` in a clean Chrome app-mode window with no tabs/address bar.
- Provides owned-process `start`, `stop`, `status`, and `restart` scripts.
- Refuses to kill an externally-owned Forge backend unless the operator stops it manually.

## Commands

```bash
~/forge/scripts/aiweb-os-start
~/forge/scripts/aiweb-os-status
~/forge/scripts/aiweb-os-stop
~/forge/scripts/aiweb-os-restart
```

## Desktop install

```bash
~/forge/scripts/install_aiweb_os_operator_console_desktop.sh
```

## Boundary

This patch does not grant browser authority, does not write RMC memory, does not touch Identity Vault, does not query Chroma, does not call LLMs, and does not execute arbitrary shell commands.

## Note on frameless windows

Chrome app mode removes tabs/address bar and creates a clean app-like window. Full frameless/no-OS-controls behavior requires a native shell such as Electron/Tauri/GTK and should be implemented only after this lifecycle manager proves stable.
