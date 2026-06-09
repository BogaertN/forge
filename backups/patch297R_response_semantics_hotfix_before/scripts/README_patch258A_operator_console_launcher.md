# Patch 258A — Operator Console One-Click Launcher

This patch adds a local convenience launcher only.

It does not patch `main.py`.
It does not add Forge commands.
It does not bypass Forge.
It starts the existing Forge runtime, auto-selects approved path option `2`, sends the existing `forge-ui-start` command, then opens:

`http://localhost:7477/operator-console`

Installed files:

- `forge/scripts/forge_operator_console_launcher.py`
- `forge/scripts/install_forge_operator_console_launcher.py`
- `forge/scripts/patch258A_operator_console_launcher_verify.py`

To install the desktop/app-menu launcher:

```bash
cd ~/forge
source .venv/bin/activate
python scripts/install_forge_operator_console_launcher.py
```

Then open **AI.Web Forge Operator Console** from the app menu, or double-click the Desktop launcher if your desktop environment shows it.

If Linux asks whether to trust/allow launching the desktop icon, choose the trust/allow option.
