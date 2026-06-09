# test_runtime_manifest.py — Forge sandbox candidate only
# This test is a future candidate. It is not installed into the live AI.Web runtime.

import json
from pathlib import Path


def test_runtime_manifest_parses() -> None:
    manifest_path = Path(__file__).resolve().parents[1] / "runtime_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["manifest_type"] == "AIWEB_RUNTIME_CANDIDATE_SANDBOX_MANIFEST"
    assert payload["candidate"].get("engine") == 'failsafe_manager'
    assert payload["authority"]["runtime_file_write_authority"] is False
