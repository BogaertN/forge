# Patch 226B — Identity Vault Legacy Profile Migration Preview

This read-only patch reviews the existing legacy `vault.db` profile row and local Identity Vault profile templates before any new canonical profiles are created.

It writes reports only under:

`~/forge/memory/identity_vault_patch226b_legacy_profile_migration_preview_v1/`

It does not read `.env` secret values, write databases, create profiles, or activate identities.
