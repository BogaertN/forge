# Patch 225A — Identity Vault Operational Profile Schema Alignment Scan

This patch adds a read-only scanner:

`forge/scripts/identity_vault_patch225a_schema_alignment_scan.py`

It compares the live Identity Vault canonical SQLite database schema at:

`/home/nic/identity-vault/data/identity_vault.db`

against the operational profile structures defined in the Self-Hosted Identity Vault blueprint.

It checks:

- whether `agent_profiles` can represent the full Agent Operational Identity blueprint;
- whether `user_profiles` can represent the full User Operational Identity blueprint;
- whether code/docs reference expected profile fields and API patterns;
- whether the canonical DB opens read-only;
- whether protected files remain unchanged.

Boundary:

- No database writes.
- No `.env` secret reads.
- No Forge registry changes.
- No RMC memory writes.
- No service contract modification.
- No agent identity activation.

Reports are written only under:

`/home/nic/forge/memory/identity_vault_patch225a_schema_alignment_scan_v1/`

A `WARN` verdict is expected if the live database schema is thinner than the blueprint and needs a migration plan.
