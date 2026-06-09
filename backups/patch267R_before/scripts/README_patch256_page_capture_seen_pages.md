# Patch 256 — Page Capture + Seen Pages Panel

Purpose: wire the original Terminus page capture / seen-pages functionality into the production Operator Console without giving the frontend authority.

Backend endpoints used:

- `GET /api/seen-pages`
- `POST /api/read-page`

Authority boundary:

- No shell execution.
- No Forge command execution.
- No LLM call.
- Captured page records write only under Forge browser memory: `forge_browser_memory_v1`.
- No Identity Vault write.
- No RMC live memory write.
- No new Forge CLI command.

After install, verify with:

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile main.py scripts/patch256_page_capture_seen_pages_verify.py
python scripts/patch256_page_capture_seen_pages_verify.py
```
