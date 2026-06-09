# Patch 227A — Identity Vault Inactive Draft Profile Verification

This read-only verifier checks the inactive draft profiles seeded by Patch 227.

It verifies:

- `nic_bogaert` exists in `user_profiles`.
- `gilligan.local`, `athena.local`, and `neo.local` exist in `agent_profiles`.
- All agents have `activation_state = inactive_draft`.
- All seeded profiles have `is_active = 0`.
- `operational_profile_json` parses.
- `profile_hash` matches the stored payload.
- RMC namespaces are pointers only.
- No RMC namespace folders or memory records were created by the verifier.
- No `.env` secret values are read.
- No Identity Vault database writes are performed.
- No agent activation is performed.

Run from `~/forge`:

```bash
python -m py_compile scripts/identity_vault_patch227a_verify_inactive_draft_profiles.py
python scripts/identity_vault_patch227a_verify_inactive_draft_profiles.py
cat ~/forge/memory/identity_vault_patch227a_inactive_profile_verify_v1/latest_identity_vault_patch227a_inactive_profile_verify.md
```
