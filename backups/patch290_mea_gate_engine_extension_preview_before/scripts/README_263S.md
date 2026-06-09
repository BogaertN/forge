# Patch 263S — In-App Operator Lifecycle Menu

Adds production-grade AI.Web OS lifecycle controls to the Forge Operator Console.

## Backend endpoints

- `/api/aiweb-os/lifecycle-manifest`
- `/api/aiweb-os/status`
- `/api/aiweb-os/logs`
- `/api/aiweb-os/exit-window-preview`
- `/api/aiweb-os/exit-window-confirm?token=EXIT_AIWEB_OPERATOR_WINDOW`
- `/api/aiweb-os/restart-preview`
- `/api/aiweb-os/restart-confirm?token=RESTART_AIWEB_OS`
- `/api/aiweb-os/shutdown-preview`
- `/api/aiweb-os/shutdown-confirm?token=SHUTDOWN_AIWEB_OS`

## Safety contract

The browser receives no shell, no arbitrary command endpoint, no file-write authority, no Identity Vault write authority, no RMC memory write authority, no Chroma write authority, and no LLM call authority.

Restart and shutdown are preview-first and exact-token-gated. Confirmed restart/shutdown calls are scheduled through `scripts/aiweb_os_deferred_action.py`, which accepts only `restart` or `shutdown` and runs only the fixed wrappers already owned by AI.Web OS.

## UI

The header now includes an `Operator Menu` button with:

- Status
- View Logs
- Exit Window
- Restart AI.Web OS
- Shutdown AI.Web OS

Exit Window closes only the Operator Console window when the browser allows it. It does not stop Forge.

## Verification

```bash
cd ~/forge
source .venv/bin/activate
python scripts/patch263S_verify.py
python scripts/test_patch263S_operator_lifecycle_menu.py
```

Expected:

```text
RESULT: PATCH_263S_VERIFY_OK
RESULT: patch263S_tests=PASS
```
