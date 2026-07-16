"""Exact static synthetic fixture catalog for Slice 36H.

The catalog is immutable and closed. It contains no public caller, production
input, external document, memory item, repository path, URL, capability, tool,
or action instruction. Merely importing or listing fixtures performs no run.
"""

from __future__ import annotations

from .schema import (
    BoundedStructuralFixtureRecord,
    SLICE36H_SCHEMA_VERSION,
    source_sha256,
)
from ..schema import stable_record_id


FIXTURE_GOVERNING = "slice36h-governing-operator-chain-v1"
FIXTURE_ZERO_DERIVATION = "slice36h-zero-supported-derivation-v1"
FIXTURE_QUOTATION_CONFLICT = "slice36h-quotation-conflict-v1"
FIXTURE_INCOMPLETE_QUOTATION = "slice36h-incomplete-quotation-v1"


def _fixture(
    *,
    fixture_name: str,
    exact_source_text: str,
    sequence_number: int,
    expected_binding_status: str,
    expected_phase_trail_status: str,
    expected_constraint_status: str,
    expected_structural_status: str,
    expected_structural_candidate_count: int,
    expected_non_progress_reasons: tuple[str, ...],
) -> BoundedStructuralFixtureRecord:
    body = {
        "fixture_name": fixture_name,
        "exact_source_text": exact_source_text,
        "source_sha256": source_sha256(exact_source_text),
        "source_id": "slice36h.synthetic.fixture",
        "channel_id": "slice36h.offline.fixture",
        "sequence_number": sequence_number,
        "correlation_id": f"slice36h-correlation-{sequence_number:03d}",
        "requested_context_dependencies": (),
        "expected_custody_status": "captured_supported_input",
        "expected_projection_status": "SOURCE_FIELD_SUPPORTED",
        "expected_binding_status": expected_binding_status,
        "expected_phase_trail_status": expected_phase_trail_status,
        "expected_constraint_status": expected_constraint_status,
        "expected_structural_status": expected_structural_status,
        "expected_structural_candidate_count": expected_structural_candidate_count,
        "expected_non_progress_reasons": expected_non_progress_reasons,
        "synthetic": True,
        "accepted_fixture": True,
        "explicit_invocation_only": True,
        "offline_only": True,
        "in_memory_only": True,
        "external_context_required": False,
        "external_resource_allowed": False,
        "memory_allowed": False,
        "route_allowed": False,
        "action_allowed": False,
        "rendering_allowed": False,
        "delivery_allowed": False,
        "selected_meaning_allowed": False,
        "schema_version": SLICE36H_SCHEMA_VERSION,
    }
    return BoundedStructuralFixtureRecord(
        fixture_id=stable_record_id(
            "slice36_bounded_structural_fixture",
            body,
        ),
        **body,
    )


def _build_catalog() -> tuple[BoundedStructuralFixtureRecord, ...]:
    return (
        _fixture(
            fixture_name=FIXTURE_GOVERNING,
            exact_source_text="Do not install it.",
            sequence_number=1,
            expected_binding_status="CANDIDATE_BINDINGS_SUPPORTED",
            expected_phase_trail_status="MULTIPLE_PHASE_TRAILS",
            expected_constraint_status="CONFLICTING_SCOPE_ATTACHMENTS",
            expected_structural_status="MULTIPLE_STRUCTURAL_CANDIDATES",
            expected_structural_candidate_count=8,
            expected_non_progress_reasons=(
                "UNRESOLVED_REFERENCE",
                "UNRESOLVED_OPERATOR_BINDING",
                "UNSUPPORTED_OPERATOR_SEQUENCE",
                "MULTIPLE_STRUCTURAL_CANDIDATES",
                "INCOMPLETE_OPERATOR_TRAIL",
                "RECURSION_SUSPENDED",
            ),
        ),
        _fixture(
            fixture_name=FIXTURE_ZERO_DERIVATION,
            exact_source_text="hello",
            sequence_number=2,
            expected_binding_status="CANDIDATE_BINDINGS_NONE",
            expected_phase_trail_status="ZERO_PHASE_TRAILS",
            expected_constraint_status="ZERO_SCOPE_CONSTRAINTS",
            expected_structural_status="ZERO_STRUCTURAL_CANDIDATES",
            expected_structural_candidate_count=0,
            expected_non_progress_reasons=(
                "NO_SUPPORTED_DERIVATION",
            ),
        ),
        _fixture(
            fixture_name=FIXTURE_QUOTATION_CONFLICT,
            exact_source_text='"Alpha"',
            sequence_number=3,
            expected_binding_status="CANDIDATE_BINDINGS_SUPPORTED",
            expected_phase_trail_status="CONFLICTING_PHASE_TRAILS",
            expected_constraint_status="MULTIPLE_SCOPE_CONSTRAINED_TRAILS",
            expected_structural_status="MULTIPLE_STRUCTURAL_CANDIDATES",
            expected_structural_candidate_count=4,
            expected_non_progress_reasons=(
                "UNRESOLVED_OPERATOR_BINDING",
                "MULTIPLE_STRUCTURAL_CANDIDATES",
                "CONFLICTING_PHASE_TRAILS",
            ),
        ),
        _fixture(
            fixture_name=FIXTURE_INCOMPLETE_QUOTATION,
            exact_source_text='"Alpha',
            sequence_number=4,
            expected_binding_status="CANDIDATE_BINDINGS_SUPPORTED",
            expected_phase_trail_status="INCOMPLETE_PHASE_TRAIL",
            expected_constraint_status="MALFORMED_SCOPE_ATTACHMENT",
            expected_structural_status="ONE_STRUCTURAL_CANDIDATE",
            expected_structural_candidate_count=1,
            expected_non_progress_reasons=(
                "UNRESOLVED_OPERATOR_BINDING",
                "MALFORMED_SOURCE_STRUCTURE",
                "CONFLICTING_PHASE_TRAILS",
                "INCOMPLETE_INPUT",
            ),
        ),
    )


_FIXTURES = _build_catalog()
_FIXTURE_BY_NAME = {fixture.fixture_name: fixture for fixture in _FIXTURES}


def list_bounded_structural_fixtures() -> tuple[BoundedStructuralFixtureRecord, ...]:
    return _FIXTURES


def get_bounded_structural_fixture(
    fixture_name: str,
) -> BoundedStructuralFixtureRecord | None:
    if type(fixture_name) is not str:
        return None
    return _FIXTURE_BY_NAME.get(fixture_name)


def is_exact_accepted_bounded_structural_fixture(
    fixture: object,
) -> bool:
    if type(fixture) is not BoundedStructuralFixtureRecord:
        return False
    accepted = _FIXTURE_BY_NAME.get(fixture.fixture_name)
    return accepted is not None and fixture == accepted


__all__ = (
    "FIXTURE_GOVERNING",
    "FIXTURE_INCOMPLETE_QUOTATION",
    "FIXTURE_QUOTATION_CONFLICT",
    "FIXTURE_ZERO_DERIVATION",
    "get_bounded_structural_fixture",
    "is_exact_accepted_bounded_structural_fixture",
    "list_bounded_structural_fixtures",
)
