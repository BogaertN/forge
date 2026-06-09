# Patch 217A — Identity Vault Readiness Reconcile

This patch adds a read-only reconciliation scanner for the Patch 217 WARN state.

It does not modify Identity Vault, Forge tools, Forge registry, RMC memory, databases, `.env`, or agent identity state.

Run from `~/forge`:

```bash
python -m py_compile scripts/identity_vault_patch217a_readiness_reconcile.py
python scripts/identity_vault_patch217a_readiness_reconcile.py
cat ~/forge/memory/identity_vault_patch217a_readiness_reconcile_v1/latest_identity_vault_patch217a_readiness_reconcile.md
```

Expected: `Verdict: PASS` if the contract fields, required ignore rules, and canonical database read-only schema are all valid.
