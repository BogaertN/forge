"""Receipt generation for Slice 19 RMC Echo Boundary Scaffold."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .authority import build_authority_report
from .boundary import build_boundary_report, validate_boundary_report
from .core import EXPECTED_BASE_HEAD, EXPECTED_BASE_SUBJECT, EXPECTED_COMMIT_SUBJECT


def canonical_json(data: Any) -> str:
    """Return canonical JSON for deterministic receipt hashing."""

    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_text(text: str) -> str:
    """Return a SHA-256 digest for UTF-8 text."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_slice19_receipt() -> dict[str, object]:
    """Build a deterministic receipt for the boundary scaffold."""

    boundary_report = build_boundary_report()
    boundary_failures = validate_boundary_report(boundary_report)
    authority_report = build_authority_report()

    body: dict[str, object] = {
        "receipt_type": "slice19_rmc_echo_boundary_scaffold_receipt",
        "expected_base_head": EXPECTED_BASE_HEAD,
        "expected_base_subject": EXPECTED_BASE_SUBJECT,
        "expected_commit_subject": EXPECTED_COMMIT_SUBJECT,
        "boundary_report": boundary_report,
        "authority_report": authority_report,
        "boundary_validation_failures": list(boundary_failures),
        "repo_write_authorized": False,
        "delivery_authorized": False,
        "public_release_authorized": False,
        "output_approval_authorized": False,
        "production_integration_authorized": False,
        "gp014_modified": False,
        "gp014_imported": False,
        "gp014_called": False,
        "gp015_repaired": False,
    }

    digest = sha256_text(canonical_json(body))
    return {
        "receipt": body,
        "receipt_sha256": digest,
    }
