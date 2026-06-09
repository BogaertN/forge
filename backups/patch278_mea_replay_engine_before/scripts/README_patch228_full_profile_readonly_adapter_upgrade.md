# Patch 228 — Full Profile Read-Only Adapter Upgrade

This patch upgrades Forge's Identity Vault read-only agent helpers so `forge-agent-list` and `forge-agent-show <agent_id>` can expose safe summaries from the full `operational_profile_json` payload.

Boundary:
- Modifies only `/home/nic/forge/agents/forge/aiweb_readonly_connectors.py` after backup.
- Does not write Identity Vault databases.
- Does not create profiles.
- Does not activate identities.
- Does not read `.env` secret values.
- Does not modify Forge registry.
- Does not write RMC memory.

Expected after PASS:
- `forge-agent-list` includes activation state, is_active, RMC namespace, profile hash status, and summary fields.
- `forge-agent-show gilligan.local` shows safe full-profile metadata summary, not the raw full payload.
- All agents remain inactive draft records.

If verification fails, the script restores the connector from backup automatically.
