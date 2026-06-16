"""Deterministic claim validation for AI.Web Slice 3.

This module checks whether a status claim is supported by named evidence.  It is
small by design: no network, no model, no external registry, and no fuzzy match.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping, Tuple

from .vocabulary import BLOCKED_AUTHORITY_CLAIMS, STATUS_DEFINITIONS, get_status_definition


@dataclass(frozen=True)
class ClaimEvidence:
    """Named evidence booleans for a status claim."""

    values: Mapping[str, bool] = field(default_factory=dict)

    def has(self, key: str) -> bool:
        """Return True only when the evidence key is explicitly true."""

        return bool(self.values.get(key, False))

    def missing(self, required: Tuple[str, ...]) -> Tuple[str, ...]:
        """Return required evidence keys that are not present and true."""

        return tuple(key for key in required if not self.has(key))


@dataclass(frozen=True)
class ClaimRecord:
    """A status claim that can be checked deterministically."""

    claimed_status: str
    claim_text: str
    scope: str
    evidence: ClaimEvidence = field(default_factory=ClaimEvidence)
    public_claim: bool = False
    release_claim: bool = False
    production_claim: bool = False
    authority_claims: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class ClaimValidation:
    """Validation result for a claim."""

    ok: bool
    failures: Tuple[str, ...]
    warnings: Tuple[str, ...]
    required_evidence: Tuple[str, ...]
    missing_evidence: Tuple[str, ...]


_PRODUCTION_WORDS = (
    "production-ready",
    "production ready",
    "production readiness",
)

_RELEASE_WORDS = (
    "released",
    "release-ready",
    "release ready",
    "public release",
)

_ACCEPTED_WORDS = (
    "accepted",
    "accepted within scope",
)

_VERIFIED_WORDS = (
    "verified",
    "verifier passed",
    "verifiers passed",
)


def _lower(text: str) -> str:
    return text.casefold()


def _contains_any(text: str, words: Tuple[str, ...]) -> bool:
    lowered = _lower(text)
    return any(word in lowered for word in words)


def _blocked_claim_failures(authority_claims: Mapping[str, bool]) -> Tuple[str, ...]:
    failures = []
    for key in BLOCKED_AUTHORITY_CLAIMS:
        if bool(authority_claims.get(key, False)):
            failures.append(f"blocked authority claim present: {key}")
    return tuple(failures)


def validate_claim(record: ClaimRecord) -> ClaimValidation:
    """Validate one claim against the controlled vocabulary.

    The validator is intentionally conservative.  If a claim sounds stronger
    than the evidence, it fails.
    """

    failures = []
    warnings = []

    try:
        definition = get_status_definition(record.claimed_status)
    except KeyError as exc:
        return ClaimValidation(
            ok=False,
            failures=(str(exc),),
            warnings=(),
            required_evidence=(),
            missing_evidence=(),
        )

    if not record.scope.strip():
        failures.append("scope is required")

    missing = record.evidence.missing(definition.required_evidence)
    for key in missing:
        failures.append(f"missing required evidence: {key}")

    failures.extend(_blocked_claim_failures(record.authority_claims))

    text = record.claim_text or ""

    if record.production_claim or _contains_any(text, _PRODUCTION_WORDS):
        if record.claimed_status != "production_ready":
            failures.append("production-readiness language requires claimed_status=production_ready")
        if not record.evidence.has("production_readiness_decision"):
            failures.append("production-readiness language requires production_readiness_decision evidence")

    if record.release_claim or _contains_any(text, _RELEASE_WORDS):
        if record.claimed_status not in ("released", "production_ready"):
            failures.append("release language requires claimed_status=released or production_ready")
        if not record.evidence.has("release_decision"):
            failures.append("release language requires release_decision evidence")

    if _contains_any(text, _ACCEPTED_WORDS):
        if record.claimed_status not in (
            "accepted_within_scope",
            "accepted_with_warnings_within_scope",
            "current_baseline",
            "released",
            "production_ready",
        ):
            failures.append("accepted language requires an accepted/current-baseline/release/production status")
        if not record.evidence.has("decision_record"):
            failures.append("accepted language requires decision_record evidence")

    if _contains_any(text, _VERIFIED_WORDS):
        if record.claimed_status in ("planned", "designed", "authorized_for_installation", "installed"):
            failures.append("verified language cannot be used for planned/designed/authorized/installed status")
        if not record.evidence.has("verifier_recorded") or not record.evidence.has("verifiers_passed"):
            failures.append("verified language requires verifier_recorded and verifiers_passed evidence")

    if record.public_claim and not definition.allowed_public_claim:
        failures.append(f"public claim is not allowed for status: {record.claimed_status}")

    if record.public_claim and not record.evidence.has("public_claim_boundary"):
        failures.append("public claim requires public_claim_boundary evidence")

    if record.claimed_status == "verified_within_scope":
        warnings.append("verified_within_scope is not acceptance and not production readiness")

    if record.claimed_status == "accepted_within_scope":
        warnings.append("accepted_within_scope is limited to the named scope")

    return ClaimValidation(
        ok=not failures,
        failures=tuple(failures),
        warnings=tuple(warnings),
        required_evidence=definition.required_evidence,
        missing_evidence=missing,
    )


def build_evidence(**values: bool) -> ClaimEvidence:
    """Convenience helper for tests and future verifier code."""

    return ClaimEvidence(values=dict(values))


def full_accepted_scope_evidence() -> Dict[str, bool]:
    """Return a deterministic evidence set for a complete accepted-within-scope claim."""

    return {
        "fresh_source_packet": True,
        "source_inspection": True,
        "patch_design": True,
        "backup": True,
        "installation_record": True,
        "changed_file_manifest": True,
        "tests_recorded": True,
        "tests_passed": True,
        "verifier_recorded": True,
        "verifiers_passed": True,
        "result_packet": True,
        "decision_record": True,
        "public_claim_boundary": True,
    }
