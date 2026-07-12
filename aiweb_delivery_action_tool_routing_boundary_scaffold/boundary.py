"""Boundary integrity checks for Slice 20."""

from __future__ import annotations

from dataclasses import dataclass

from .authority import build_authority_separation_record
from .core import build_boundary_record, get_required_sentinels

@dataclass(frozen=True, slots=True)
class BoundaryCheckResult:
    passed: bool
    failures: tuple[str, ...]

    def require_pass(self) -> None:
        if not self.passed:
            raise RuntimeError("Slice 20 boundary check failed: " + "; ".join(self.failures))


def check_boundary_integrity() -> BoundaryCheckResult:
    """Verify that the Slice 20 boundary remains negative-authority only."""
    record = build_boundary_record()
    authority = build_authority_separation_record()
    failures: list[str] = []
    record_values = set(str(value) for value in record.to_dict().values())

    for sentinel in get_required_sentinels():
        if sentinel not in record_values and sentinel not in record.echo_delivery_boundary:
            failures.append("missing required sentinel: " + sentinel)

    if authority.this_scaffold_grants_permission:
        failures.append("this scaffold must not grant permission")
    if not authority.permission_required_for_invocation:
        failures.append("invocation must require permission")
    if not authority.permission_required_for_delivery:
        failures.append("delivery must require permission")
    if not authority.permission_required_for_code_execution:
        failures.append("code execution must require permission")
    if not authority.permission_required_for_sending_drafts:
        failures.append("sending drafts must require permission")
    if record.sentinel_count != len(get_required_sentinels()):
        failures.append("sentinel count mismatch")

    return BoundaryCheckResult(passed=not failures, failures=tuple(failures))
