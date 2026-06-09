# Patch 245A — API Route Table Fix

Patch 245 correctly installed the API helper functions but failed to attach the
new endpoints into the Terminus `do_GET` route table.

Symptom:
- `/api/status` returned JSON.
- `/api/operator/contract`, `/api/forge/status`, `/api/audit/tail`, and
  `/api/protoforge/reports` returned HTTP 404.

Patch 245A fixes only the route table.

It does not:
- add Forge commands
- change command surface count
- install npm packages
- launch the frontend
- execute simulations
- write Identity Vault
- write RMC live memory
