# Patch 207 - RMC Integration Freeze

This patch adds a read-only evidence collector:

- `forge/scripts/rmc_integration_freeze.py`

It does not modify live RMC modules, Forge agent code, Identity Vault, databases, or `.env` files.

It writes reports and freeze snapshots under:

- `~/forge/memory/rmc_integration_freeze_v1/`

Purpose:

1. Copy existing RMC modules into a timestamped evidence snapshot.
2. Copy the standalone `gilligan_agent` into a retired-candidate snapshot before any future deletion.
3. Compile-test discovered Python modules.
4. Run pytest where test files are present.
5. Record Identity Vault hygiene risks without exposing file contents.

Run from `~/forge`:

```bash
python scripts/rmc_integration_freeze.py
```
