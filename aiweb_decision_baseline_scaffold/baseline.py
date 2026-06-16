"""Deterministic Accepted Baseline Update scaffold for AI.Web Slice 4."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Tuple

from .decision import (
    FORBIDDEN_AUTHORITY_KEYS,
    NON_PRODUCTION_READY,
    NON_PUBLIC_DELIVERY_AUTHORIZED,
    NON_RELEASE_AUTHORIZED,
    DecisionRecord,
    validate_decision_record,
)

ACCEPTED_BASELINE_STATUS = "accepted_baseline_update"

_REQUIRED_BASELINE_FIELDS: Tuple[str, ...] = (
    "baseline_id",
    "implementation_line",
    "baseline_status",
    "accepted_source_head",
    "decision_record_id",
    "result_packet",
    "result_packet_sha256",
    "accepted_scope",
    "public_claim_boundary",
    "next_allowed_gate",
)


@dataclass(frozen=True)
class AcceptedBaselineUpdate:
    """A baseline pointer backed by a valid accepted decision record."""

    baseline_id: str
    implementation_line: str
    baseline_status: str
    accepted_source_head: str
    decision_record_id: str
    result_packet: str
    result_packet_sha256: str
    accepted_scope: str
    public_claim_boundary: bool
    next_allowed_gate: str
    production_readiness_status: str = NON_PRODUCTION_READY
    release_status: str = NON_RELEASE_AUTHORIZED
    public_delivery_status: str = NON_PUBLIC_DELIVERY_AUTHORIZED
    warnings: Tuple[str, ...] = ()
    exclusions: Tuple[str, ...] = ()
    authority_claims: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class BaselineValidation:
    """Validation result for an AcceptedBaselineUpdate."""

    ok: bool
    failures: Tuple[str, ...]
    warnings: Tuple[str, ...]
    required_fields: Tuple[str, ...]
    missing_fields: Tuple[str, ...]


def _has_value(value: object) -> bool:
    if isinstance(value, bool):
        return value is True
    if isinstance(value, tuple):
        return bool(value)
    return bool(value)


def _missing_fields(update: AcceptedBaselineUpdate) -> Tuple[str, ...]:
    return tuple(field_name for field_name in _REQUIRED_BASELINE_FIELDS if not _has_value(getattr(update, field_name)))


def _forbidden_claim_failures(update: AcceptedBaselineUpdate) -> Tuple[str, ...]:
    failures = []
    for key in FORBIDDEN_AUTHORITY_KEYS:
        if bool(update.authority_claims.get(key, False)):
            failures.append(f"forbidden authority claim present: {key}")

    if update.production_readiness_status != NON_PRODUCTION_READY:
        failures.append("baseline update cannot grant production readiness")
    if update.release_status != NON_RELEASE_AUTHORIZED:
        failures.append("baseline update cannot grant release authorization")
    if update.public_delivery_status != NON_PUBLIC_DELIVERY_AUTHORIZED:
        failures.append("baseline update cannot grant public delivery")

    return tuple(failures)


def validate_accepted_baseline_update(
    update: AcceptedBaselineUpdate,
    decision: DecisionRecord | None,
) -> BaselineValidation:
    """Validate an AcceptedBaselineUpdate against a DecisionRecord."""

    failures = []
    warnings = []
    missing = _missing_fields(update)

    if missing:
        failures.append("accepted baseline update is missing required fields: " + ", ".join(missing))

    if update.baseline_status != ACCEPTED_BASELINE_STATUS:
        failures.append("baseline_status must be accepted_baseline_update")

    if decision is None:
        failures.append("accepted baseline update requires a linked DecisionRecord")
    else:
        decision_validation = validate_decision_record(decision)
        if not decision_validation.ok:
            failures.append("linked DecisionRecord is not valid: " + "; ".join(decision_validation.failures))
        if decision.decision_status not in ("accepted_within_scope", "accepted_with_warnings_within_scope"):
            failures.append("linked DecisionRecord is not an accepted-within-scope decision")
        if update.decision_record_id != decision.record_id:
            failures.append("decision_record_id does not match linked DecisionRecord")
        if update.accepted_source_head != decision.source_head:
            failures.append("accepted_source_head does not match linked DecisionRecord source_head")
        if update.result_packet != decision.result_packet:
            failures.append("result_packet does not match linked DecisionRecord")
        if update.result_packet_sha256 != decision.result_packet_sha256:
            failures.append("result_packet_sha256 does not match linked DecisionRecord")

    failures.extend(_forbidden_claim_failures(update))

    return BaselineValidation(
        ok=not failures,
        failures=tuple(failures),
        warnings=tuple(warnings),
        required_fields=_REQUIRED_BASELINE_FIELDS,
        missing_fields=missing,
    )


def build_accepted_baseline_update(
    *,
    baseline_id: str,
    implementation_line: str,
    baseline_status: str,
    accepted_source_head: str,
    decision_record_id: str,
    result_packet: str,
    result_packet_sha256: str,
    accepted_scope: str,
    public_claim_boundary: bool,
    next_allowed_gate: str,
    production_readiness_status: str = NON_PRODUCTION_READY,
    release_status: str = NON_RELEASE_AUTHORIZED,
    public_delivery_status: str = NON_PUBLIC_DELIVERY_AUTHORIZED,
    warnings: Tuple[str, ...] = (),
    exclusions: Tuple[str, ...] = (),
    authority_claims: Mapping[str, bool] | None = None,
) -> AcceptedBaselineUpdate:
    """Build an AcceptedBaselineUpdate without side effects."""

    return AcceptedBaselineUpdate(
        baseline_id=baseline_id,
        implementation_line=implementation_line,
        baseline_status=baseline_status,
        accepted_source_head=accepted_source_head,
        decision_record_id=decision_record_id,
        result_packet=result_packet,
        result_packet_sha256=result_packet_sha256,
        accepted_scope=accepted_scope,
        public_claim_boundary=public_claim_boundary,
        next_allowed_gate=next_allowed_gate,
        production_readiness_status=production_readiness_status,
        release_status=release_status,
        public_delivery_status=public_delivery_status,
        warnings=tuple(warnings),
        exclusions=tuple(exclusions),
        authority_claims=dict(authority_claims or {}),
    )


def sample_accepted_baseline_update(decision: DecisionRecord) -> AcceptedBaselineUpdate:
    """Return a valid sample baseline update for a valid accepted decision."""

    return build_accepted_baseline_update(
        baseline_id="AIWEB-BASELINE-SLICE04-SAMPLE",
        implementation_line="Forge/RMC language-core implementation line",
        baseline_status=ACCEPTED_BASELINE_STATUS,
        accepted_source_head=decision.source_head,
        decision_record_id=decision.record_id,
        result_packet=decision.result_packet,
        result_packet_sha256=decision.result_packet_sha256,
        accepted_scope="Slice 4 sample scope only",
        public_claim_boundary=True,
        next_allowed_gate="Slice 5 Narrow Source Authority Packet",
        exclusions=(
            "not production ready",
            "not release authorized",
            "not public delivery authorized",
            "not GP-014 supersession",
        ),
    )
