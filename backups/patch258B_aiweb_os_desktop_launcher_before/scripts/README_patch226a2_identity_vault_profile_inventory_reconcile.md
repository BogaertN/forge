# Patch 226A.2 — Identity Vault Profile Inventory Reconcile

This patch adds a read-only inventory reconciliation scanner after Patch 226A.1 found legacy profile/session rows but failed its safety predicate.

It reads the canonical and legacy SQLite databases through read-only connections, previews legacy profile/session rows safely, summarizes local template/profile candidate JSON files, and writes reports under Forge memory.

It does not read `.env` secret values, write databases, create profiles, or activate identities.
