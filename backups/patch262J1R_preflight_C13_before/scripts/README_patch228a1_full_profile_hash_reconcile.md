# Patch 228A.1 — Full Profile Hash Reconcile

Purpose: repair Forge's read-only Identity Vault full-profile connector hash verification logic so `profile_hash_ok` reflects the canonical seeded profile hashes.

Boundary:
- Modifies only `/home/nic/forge/agents/forge/aiweb_readonly_connectors.py` after backup.
- Writes reports only under Forge memory.
- Does not write Identity Vault databases.
- Does not create profiles.
- Does not activate identities.
- Does not read `.env` secret values.
- Does not write RMC memory.
- Does not modify Forge registry.

Expected result: PASS, with Gilligan/Athena/Neo all still inactive and all `profile_hash_ok=True`.
