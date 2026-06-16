"""Deterministic Decision Record scaffold for AI.Web Slice 4.

The scaffold records and validates the evidence shape needed before a slice can
be described as accepted within scope.  It intentionally does not perform any
runtime action, release decision, production-readiness decision, or GP-014
supersession.  No network, model, embedding, vector store, or external resource
is used.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Tuple

DECISION_STATUSES: Tuple[str, ...] = (
    "accepted_within_scope",
    "accepted_with_warnings_within_scope",
    "held",
    "rejected",
    "rolled_back",
)

NON_PRODUCTION_READY = "not_production_ready"
NON_RELEASE_AUTHORIZED = "not_release_authorized"
NON_PUBLIC_DELIVERY_AUTHORIZED = "not_public_delivery_authorized"

FORBIDDEN_AUTHORITY_KEYS: Tuple[str, ...] = (
    "gp014_supersession_claim",
    "gp014_replacement_claim",
    "gp015_repair_claim",
    "gp015r1_install_claim",
    "production_readiness_claim",
    "release_authorization_claim",
    "public_delivery_claim",
    "general_language_authority_claim",
    "ui_authority_claim",
    "memory_authority_claim",
    "evidence_authority_claim",
    "corpus_authority_claim",
    "external_resource_authority_claim",
    "delivery_authority_claim",
    "action_routing_authority_claim",
    "model_vector_llm_authority_claim",
)

_ACCEPTED_REQUIRED_FIELDS: Tuple[str, ...] = (
    "record_id",
    "slice_id",
    "slice_name",
    "decision_scope",
    "source_head",
    "result_packet",
    "result_packet_sha256",
    "inspection_record",
    "verifier_output",
    "behavior_test_output",
    "decision_owner_status",
    "public_claim_boundary",
)

_HELD_REJECTED_REQUIRED_FIELDS: Tuple[str, ...] = (
    "record_id",
    "slice_id",
    "slice_name",
    "decision_scope",
    "source_head",
    "decision_owner_status",
    "decision_reasons",
)


@dataclass(frozen=True)
class DecisionRecord:
    """A bounded implementation-cycle decision record.

    A valid record can state the status of one selected cycle.  It cannot grant
    broader authority than its fields prove.
    """

    record_id: str
    slice_id: str
    slice_name: str
    decision_status: str
    decision_scope: str
    source_head: str
    result_packet: str = ""
    result_packet_sha256: str = ""
    inspection_record: str = ""
    verifier_output: str = ""
    behavior_test_output: str = ""
    decision_owner_status: str = ""
    public_claim_boundary: bool = False
    production_readiness_status: str = NON_PRODUCTION_READY
    release_status: str = NON_RELEASE_AUTHORIZED
    public_delivery_status: str = NON_PUBLIC_DELIVERY_AUTHORIZED
    baseline_update_applicable: bool = True
    decision_reasons: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    exclusions: Tuple[str, ...] = ()
    authority_claims: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionValidation:
    """Validation result for a DecisionRecord."""

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


def _missing_fields(record: DecisionRecord, required: Tuple[str, ...]) -> Tuple[str, ...]:
    return tuple(field_name for field_name in required if not _has_value(getattr(record, field_name)))


def _forbidden_claim_failures(record: DecisionRecord) -> Tuple[str, ...]:
    failures = []
    for key in FORBIDDEN_AUTHORITY_KEYS:
        if bool(record.authority_claims.get(key, False)):
            failures.append(f"forbidden authority claim present: {key}")

    if record.production_readiness_status != NON_PRODUCTION_READY:
        failures.append("production readiness cannot be granted by Slice 4 scaffold")
    if record.release_status != NON_RELEASE_AUTHORIZED:
        failures.append("release authorization cannot be granted by Slice 4 scaffold")
    if record.public_delivery_status != NON_PUBLIC_DELIVERY_AUTHORIZED:
        failures.append("public delivery cannot be granted by Slice 4 scaffold")

    return tuple(failures)


def expected_decision_owner_status(decision_status: str) -> str:
    """Return the expected decision-owner status value for a decision status."""

    if decision_status == "accepted_with_warnings_within_scope":
        return "accepted_with_warnings"
    return decision_status


def validate_decision_record(record: DecisionRecord) -> DecisionValidation:
    """Validate a DecisionRecord deterministically."""

    failures = []
    warnings = []
    required = ()
    missing = ()

    if record.decision_status not in DECISION_STATUSES:
        failures.append(f"unknown decision_status: {record.decision_status}")
    else:
        if record.decision_status in ("accepted_within_scope", "accepted_with_warnings_within_scope"):
            required = _ACCEPTED_REQUIRED_FIELDS
            missing = _missing_fields(record, required)
            if missing:
                failures.append("accepted decision is missing required fields: " + ", ".join(missing))
            expected = expected_decision_owner_status(record.decision_status)
            if record.decision_owner_status != expected:
                failures.append(
                    "decision_owner_status must be "
                    f"{expected!r} for decision_status {record.decision_status!r}"
                )
            if record.decision_status == "accepted_with_warnings_within_scope" and not record.warnings:
                failures.append("accepted_with_warnings decision requires at least one warning")
        else:
            required = _HELD_REJECTED_REQUIRED_FIELDS
            missing = _missing_fields(record, required)
            if missing:
                failures.append("non-accepted decision is missing required fields: " + ", ".join(missing))
            expected = expected_decision_owner_status(record.decision_status)
            if record.decision_owner_status != expected:
                failures.append(
                    "decision_owner_status must be "
                    f"{expected!r} for decision_status {record.decision_status!r}"
                )
            if record.result_packet and record.decision_status in ("held", "rejected"):
                warnings.append("non-accepted decision includes result packet reference")

    failures.extend(_forbidden_claim_failures(record))

    return DecisionValidation(
        ok=not failures,
        failures=tuple(failures),
        warnings=tuple(warnings),
        required_fields=required,
        missing_fields=missing,
    )


def build_decision_record(
    *,
    record_id: str,
    slice_id: str,
    slice_name: str,
    decision_status: str,
    decision_scope: str,
    source_head: str,
    result_packet: str = "",
    result_packet_sha256: str = "",
    inspection_record: str = "",
    verifier_output: str = "",
    behavior_test_output: str = "",
    decision_owner_status: str = "",
    public_claim_boundary: bool = False,
    production_readiness_status: str = NON_PRODUCTION_READY,
    release_status: str = NON_RELEASE_AUTHORIZED,
    public_delivery_status: str = NON_PUBLIC_DELIVERY_AUTHORIZED,
    baseline_update_applicable: bool = True,
    decision_reasons: Tuple[str, ...] = (),
    warnings: Tuple[str, ...] = (),
    exclusions: Tuple[str, ...] = (),
    authority_claims: Mapping[str, bool] | None = None,
) -> DecisionRecord:
    """Build a DecisionRecord without side effects."""

    return DecisionRecord(
        record_id=record_id,
        slice_id=slice_id,
        slice_name=slice_name,
        decision_status=decision_status,
        decision_scope=decision_scope,
        source_head=source_head,
        result_packet=result_packet,
        result_packet_sha256=result_packet_sha256,
        inspection_record=inspection_record,
        verifier_output=verifier_output,
        behavior_test_output=behavior_test_output,
        decision_owner_status=decision_owner_status,
        public_claim_boundary=public_claim_boundary,
        production_readiness_status=production_readiness_status,
        release_status=release_status,
        public_delivery_status=public_delivery_status,
        baseline_update_applicable=baseline_update_applicable,
        decision_reasons=tuple(decision_reasons),
        warnings=tuple(warnings),
        exclusions=tuple(exclusions),
        authority_claims=dict(authority_claims or {}),
    )


def sample_accepted_decision() -> DecisionRecord:
    """Return a valid sample accepted-within-scope decision."""

    return build_decision_record(
        record_id="AIWEB-DECISION-SLICE04-SAMPLE",
        slice_id="4",
        slice_name="Decision Record and Accepted Baseline Update Scaffold",
        decision_status="accepted_within_scope",
        decision_scope="Slice 4 sample scope only",
        source_head="90d3b168218e04d60c460d6adf6dd3f421ced0cc",
        result_packet="AIWEB_SLICE04_SAMPLE_RESULT_PACKET.tar.gz",
        result_packet_sha256="AIWEB_SLICE04_SAMPLE_RESULT_PACKET.tar.gz.sha256",
        inspection_record="AIWEB_SLICE04_SAMPLE_RESULT_INSPECTION_RECORD.txt",
        verifier_output="slice04_verifier_output.txt",
        behavior_test_output="slice04_behavior_test_output.txt",
        decision_owner_status="accepted_within_scope",
        public_claim_boundary=True,
        decision_reasons=("complete scoped evidence chain present",),
        exclusions=(
            "not production ready",
            "not release authorized",
            "not GP-014 supersession",
        ),
    )
