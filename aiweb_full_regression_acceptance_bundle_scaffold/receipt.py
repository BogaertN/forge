"""Deterministic proof receipt for Slice 24."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

@dataclass(frozen=True)
class ProofReceipt:
    receipt_id: str
    verdict: str
    digest: str
    accepted: bool
    command_count: int
    passed_command_count: int
    failed_command_count: int
    source_guard_passed: bool
    external_context_passed: bool
    exact_scope_only: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "receipt_id": self.receipt_id,
            "verdict": self.verdict,
            "digest": self.digest,
            "accepted": self.accepted,
            "command_count": self.command_count,
            "passed_command_count": self.passed_command_count,
            "failed_command_count": self.failed_command_count,
            "source_guard_passed": self.source_guard_passed,
            "external_context_passed": self.external_context_passed,
            "exact_scope_only": self.exact_scope_only,
        }


def canonical_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_receipt(summary: dict[str, Any]) -> ProofReceipt:
    digest = canonical_digest(summary)
    command_count = int(summary.get("required_command_count", 0))
    passed_command_count = int(summary.get("passed_command_count", 0))
    failed_command_count = int(summary.get("failed_command_count", command_count - passed_command_count))
    source_guard_passed = bool(summary.get("source_guard_passed", False))
    external_context_passed = bool(summary.get("external_context_passed", False))
    accepted = bool(summary.get("accepted", False))
    verdict = "PASS" if accepted else "FAIL_CLOSED"
    return ProofReceipt(
        receipt_id="slice24-proof-receipt:" + digest[:16],
        verdict=verdict,
        digest=digest,
        accepted=accepted,
        command_count=command_count,
        passed_command_count=passed_command_count,
        failed_command_count=failed_command_count,
        source_guard_passed=source_guard_passed,
        external_context_passed=external_context_passed,
        exact_scope_only=True,
    )


def validate_receipt(receipt: ProofReceipt) -> tuple[str, ...]:
    failures: list[str] = []
    if not receipt.receipt_id.startswith("slice24-proof-receipt:"):
        failures.append("receipt_id_prefix_invalid")
    if receipt.verdict not in {"PASS", "FAIL_CLOSED"}:
        failures.append("receipt_verdict_invalid")
    if len(receipt.digest) != 64:
        failures.append("receipt_digest_not_sha256")
    if not receipt.exact_scope_only:
        failures.append("receipt_not_exact_scope_only")
    if receipt.accepted and receipt.failed_command_count != 0:
        failures.append("accepted_receipt_has_failed_commands")
    return tuple(failures)
