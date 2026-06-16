"""Deterministic controlled status vocabulary for AI.Web Slice 3.

The vocabulary encodes claim discipline.  It is not a runtime permission system,
not a release gate, and not a production-readiness decision.  It gives later
scripts a small, inspectable set of names that can be checked without an LLM.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple

SCHEMA_VERSION = "aiweb.status_claim_scaffold.v1"


@dataclass(frozen=True)
class StatusDefinition:
    """One controlled status word and its minimum claim boundary."""

    key: str
    label: str
    meaning: str
    does_not_mean: Tuple[str, ...]
    required_evidence: Tuple[str, ...]
    allowed_public_claim: bool = False
    production_readiness: bool = False
    release_authorized: bool = False


STATUS_DEFINITIONS: Mapping[str, StatusDefinition] = {
    "planned": StatusDefinition(
        key="planned",
        label="Planned",
        meaning="The work has been identified as future work only.",
        does_not_mean=(
            "designed",
            "authorized",
            "installed",
            "tested",
            "verified",
            "accepted",
            "released",
            "production-ready",
        ),
        required_evidence=(),
    ),
    "designed": StatusDefinition(
        key="designed",
        label="Designed",
        meaning="A patch design record or architecture design exists.",
        does_not_mean=(
            "installed",
            "tested",
            "verified",
            "accepted",
            "live",
            "released",
            "production-ready",
        ),
        required_evidence=("patch_design",),
    ),
    "authorized_for_installation": StatusDefinition(
        key="authorized_for_installation",
        label="Authorized for Installation",
        meaning="The approved patch may be applied exactly as designed under backup and rollback limits.",
        does_not_mean=(
            "installed",
            "tested",
            "verified",
            "accepted",
            "released",
            "production-ready",
        ),
        required_evidence=("source_inspection", "patch_design", "backup"),
    ),
    "installed": StatusDefinition(
        key="installed",
        label="Installed",
        meaning="The patch was applied to source and recorded.",
        does_not_mean=(
            "tested",
            "verified",
            "accepted",
            "safe",
            "released",
            "production-ready",
        ),
        required_evidence=("installation_record", "changed_file_manifest"),
    ),
    "tested_passed": StatusDefinition(
        key="tested_passed",
        label="Tested: Passed",
        meaning="Required tests ran and passed within the selected scope.",
        does_not_mean=(
            "verified",
            "accepted",
            "released",
            "production-ready",
        ),
        required_evidence=("tests_recorded", "tests_passed"),
    ),
    "tested_failed": StatusDefinition(
        key="tested_failed",
        label="Tested: Failed",
        meaning="Required tests ran and failed within the selected scope.",
        does_not_mean=(
            "verified",
            "accepted",
            "safe",
            "released",
            "production-ready",
        ),
        required_evidence=("tests_recorded",),
    ),
    "verified_within_scope": StatusDefinition(
        key="verified_within_scope",
        label="Verified Within Scope",
        meaning="Required verifiers passed within a defined inspected scope.",
        does_not_mean=(
            "accepted",
            "permanently safe",
            "broadly authorized",
            "released",
            "production-ready",
        ),
        required_evidence=("verifier_recorded", "verifiers_passed"),
    ),
    "accepted_within_scope": StatusDefinition(
        key="accepted_within_scope",
        label="Accepted Within Scope",
        meaning="The decision record accepted the selected implementation cycle based on the complete result packet.",
        does_not_mean=(
            "general language complete",
            "released",
            "production-ready",
            "memory live",
            "delivery authorized",
            "GP-014 superseded",
        ),
        required_evidence=(
            "fresh_source_packet",
            "source_inspection",
            "patch_design",
            "backup",
            "installation_record",
            "changed_file_manifest",
            "tests_recorded",
            "tests_passed",
            "verifier_recorded",
            "verifiers_passed",
            "result_packet",
            "decision_record",
            "public_claim_boundary",
        ),
        allowed_public_claim=True,
    ),
    "accepted_with_warnings_within_scope": StatusDefinition(
        key="accepted_with_warnings_within_scope",
        label="Accepted With Warnings Within Scope",
        meaning="The cycle was accepted, but named non-blocking warnings remain active.",
        does_not_mean=(
            "warnings solved",
            "release authorized",
            "production-ready",
        ),
        required_evidence=(
            "fresh_source_packet",
            "source_inspection",
            "patch_design",
            "backup",
            "installation_record",
            "changed_file_manifest",
            "tests_recorded",
            "tests_passed",
            "verifier_recorded",
            "verifiers_passed",
            "result_packet",
            "decision_record",
            "public_claim_boundary",
            "warning_register",
        ),
        allowed_public_claim=True,
    ),
    "held": StatusDefinition(
        key="held",
        label="Held",
        meaning="Acceptance is blocked pending missing evidence, authority, review, or safety resolution.",
        does_not_mean=(
            "accepted",
            "safe",
            "released",
            "production-ready",
        ),
        required_evidence=("hold_reason",),
    ),
    "rejected": StatusDefinition(
        key="rejected",
        label="Rejected",
        meaning="The cycle did not meet acceptance requirements.",
        does_not_mean=(
            "accepted",
            "live",
            "safe",
            "released",
            "production-ready",
        ),
        required_evidence=("rejection_reason",),
    ),
    "rolled_back": StatusDefinition(
        key="rolled_back",
        label="Rolled Back",
        meaning="An installed change was restored, removed, contained, or reversed while preserving failure evidence.",
        does_not_mean=(
            "accepted",
            "fixed",
            "safe",
            "released",
            "production-ready",
        ),
        required_evidence=("rollback_record", "failure_evidence"),
    ),
    "current_baseline": StatusDefinition(
        key="current_baseline",
        label="Current Baseline",
        meaning="The latest accepted, evidence-backed source state for a defined implementation line.",
        does_not_mean=(
            "newest file",
            "newest packet",
            "newest chat summary",
            "production-ready",
        ),
        required_evidence=("accepted_baseline_update", "result_packet", "decision_record"),
        allowed_public_claim=True,
    ),
    "release_candidate": StatusDefinition(
        key="release_candidate",
        label="Release Candidate",
        meaning="An artifact is being evaluated for release under explicit release-candidate authority.",
        does_not_mean=(
            "released",
            "production-ready",
        ),
        required_evidence=("release_candidate_decision", "result_packet", "public_claim_boundary"),
        allowed_public_claim=True,
    ),
    "released": StatusDefinition(
        key="released",
        label="Released",
        meaning="A release decision authorized the artifact for the defined release scope.",
        does_not_mean=(
            "production-ready",
            "unbounded authority",
            "general language complete",
        ),
        required_evidence=("release_decision", "result_packet", "public_claim_boundary"),
        allowed_public_claim=True,
        release_authorized=True,
    ),
    "production_ready": StatusDefinition(
        key="production_ready",
        label="Production Ready",
        meaning="A production-readiness decision accepted production readiness with supporting evidence.",
        does_not_mean=(
            "accepted only within one slice",
            "release candidate only",
            "demo passed",
            "hardening pass only",
        ),
        required_evidence=(
            "production_readiness_decision",
            "release_decision",
            "result_packet",
            "decision_record",
            "public_claim_boundary",
        ),
        allowed_public_claim=True,
        production_readiness=True,
        release_authorized=True,
    ),
}


BLOCKED_AUTHORITY_CLAIMS: Tuple[str, ...] = (
    "gp014_supersession_claim",
    "gp014_replacement_claim",
    "gp015_repair_claim",
    "gp015r1_install_claim",
    "general_language_authority_claim",
    "llm_authority_claim",
    "vector_authority_claim",
    "model_authority_claim",
    "ui_authority_claim",
    "memory_authority_claim",
    "evidence_authority_claim",
    "corpus_authority_claim",
    "external_resource_authority_claim",
    "delivery_authority_claim",
    "action_routing_authority_claim",
)


def list_status_keys() -> Tuple[str, ...]:
    """Return status keys in deterministic sorted order."""

    return tuple(sorted(STATUS_DEFINITIONS))


def get_status_definition(key: str) -> StatusDefinition:
    """Return one status definition or raise KeyError with a stable message."""

    try:
        return STATUS_DEFINITIONS[key]
    except KeyError as exc:
        known = ", ".join(list_status_keys())
        raise KeyError(f"unknown status {key!r}; known statuses: {known}") from exc
