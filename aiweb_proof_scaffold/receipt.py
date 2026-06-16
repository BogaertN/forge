"""Receipt creation helpers for AI.Web Slice 1 proof scaffold.

These helpers write explicit JSON receipts only when given a caller-selected output path.
They do not discover private material, validate evidence truth, invoke models, route actions,
or authorize runtime behavior.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

from .schema import BLOCKED_AUTHORITIES, SCHEMA_VERSION, SLICE_ID, validate_receipt


def utc_now_iso() -> str:
    """Return an RFC3339-style UTC timestamp using timezone-aware datetime."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: str | os.PathLike[str]) -> str:
    """Return the SHA256 hex digest of a file."""
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_receipt(
    *,
    receipt_type: str,
    status: str,
    target_repo: str,
    head_commit: str,
    authority_basis: Optional[Iterable[str]] = None,
    fresh_packet_identity: Optional[Mapping[str, Any]] = None,
    changed_files: Optional[Iterable[str]] = None,
    behavior_tests: Optional[Iterable[Mapping[str, Any]]] = None,
    verifier_gates: Optional[Iterable[Mapping[str, Any]]] = None,
    rollback: Optional[Mapping[str, Any]] = None,
    accepted_scope: Optional[Mapping[str, Any]] = None,
    notes: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """Build and validate a deterministic Slice 1 receipt mapping."""
    receipt: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "slice_id": SLICE_ID,
        "receipt_type": receipt_type,
        "created_utc": utc_now_iso(),
        "status": status,
        "authority_basis": list(authority_basis or []),
        "fresh_packet_identity": dict(fresh_packet_identity or {}),
        "target_repo": target_repo,
        "head_commit": head_commit,
        "changed_files": list(changed_files or []),
        "behavior_tests": list(behavior_tests or []),
        "verifier_gates": list(verifier_gates or []),
        "rollback": dict(rollback or {}),
        "accepted_scope": dict(accepted_scope or {"claim": "No live authority accepted by receipt creation alone."}),
        "blocked_authorities": list(BLOCKED_AUTHORITIES),
        "notes": list(notes or []),
    }
    failures = validate_receipt(receipt)
    if failures:
        raise ValueError("Receipt validation failed: " + "; ".join(failures))
    return receipt


def write_receipt(receipt: Mapping[str, Any], output_path: str | os.PathLike[str]) -> Path:
    """Atomically write a receipt JSON file after schema validation."""
    failures = validate_receipt(receipt)
    if failures:
        raise ValueError("Receipt validation failed: " + "; ".join(failures))

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(out)
    return out
