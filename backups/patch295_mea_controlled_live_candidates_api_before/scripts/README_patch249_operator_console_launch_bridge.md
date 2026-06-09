# Patch 249 — Operator Console Launch Bridge

Patch 249 lets Forge serve the production Operator Console build directly.

New route:

`http://localhost:7477/operator-console`

Asset routes:

- `/operator-console/assets/...`
- `/assets/...`

Why `/assets/...` is included:
The current Vite production build emits root-relative asset URLs by default. Serving `/assets/...` from Forge lets the built console work without changing Vite base config yet.

This patch does not:
- add Forge CLI commands
- change command surface count
- execute npm
- build the frontend
- execute simulations
- write Identity Vault
- write RMC live memory

Requirements:
Run `npm run build` inside `/home/nic/aiweb/apps/forge-operator-console` before opening `/operator-console`.
