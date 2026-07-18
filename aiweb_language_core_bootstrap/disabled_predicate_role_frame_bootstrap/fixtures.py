"""Closed exact fixture catalog for Slice 38H.

Each fixture references one already accepted Slice 37G fixture.  No raw text,
file path, URL, memory item, route, tool or action is carried by a Slice 38H
invocation.
"""

from __future__ import annotations

from ..disabled_structural_concept_bootstrap import (
    FIXTURE_AMBIGUOUS,
    FIXTURE_NO_MATCH,
    FIXTURE_ONE_TO_ONE,
    FIXTURE_UNMAPPED,
    FIXTURE_UNSUPPORTED,
    IntegrationStatus as Slice37IntegrationStatus,
)
from ..predicate_role_frame_registry.predicate_role_frame_candidate_proposal import (
    CandidateProposalStatus,
)
from .schema import DisabledPredicateRoleFrameFixture


def _fixture(
    *,
    fixture_name: str,
    slice37_fixture_name: str,
    expected_slice37_status: Slice37IntegrationStatus,
    expected_slice38_status: CandidateProposalStatus,
) -> DisabledPredicateRoleFrameFixture:
    body = dict(
        fixture_name=fixture_name,
        slice37_fixture_name=slice37_fixture_name,
        expected_slice37_status=expected_slice37_status.value,
        expected_slice38_status=expected_slice38_status.value,
        expected_action_predicate_candidate_count=0,
        expected_role_layout_candidate_count=0,
        expected_capability_reference_candidate_count=0,
        accepted_fixture=True,
        synthetic=True,
        explicit_invocation_only=True,
        offline_only=True,
        in_memory_only=True,
        raw_text_not_carried_by_invocation=True,
    )
    draft = DisabledPredicateRoleFrameFixture(fixture_id="", **body)
    return DisabledPredicateRoleFrameFixture(
        fixture_id=draft.expected_id(),
        **body,
    )


FIXTURE_CANDIDATE_UNSUPPORTED = "slice38h-candidate-without-action-root-rule"
FIXTURE_AMBIGUOUS_UNSUPPORTED = "slice38h-ambiguous-without-action-root-rule"
FIXTURE_EXPLICIT_UNKNOWN = "slice38h-explicit-unknown-preserved"
FIXTURE_EXPLICIT_UNSUPPORTED = "slice38h-explicit-unsupported-preserved"
FIXTURE_NO_MATCH_UNKNOWN = "slice38h-no-match-unknown-preserved"

_FIXTURES = (
    _fixture(
        fixture_name=FIXTURE_CANDIDATE_UNSUPPORTED,
        slice37_fixture_name=FIXTURE_ONE_TO_ONE,
        expected_slice37_status=Slice37IntegrationStatus.COMPLETED_CANDIDATES,
        expected_slice38_status=CandidateProposalStatus.EXPLICIT_UNSUPPORTED,
    ),
    _fixture(
        fixture_name=FIXTURE_AMBIGUOUS_UNSUPPORTED,
        slice37_fixture_name=FIXTURE_AMBIGUOUS,
        expected_slice37_status=Slice37IntegrationStatus.COMPLETED_UNRESOLVED,
        expected_slice38_status=CandidateProposalStatus.EXPLICIT_UNSUPPORTED,
    ),
    _fixture(
        fixture_name=FIXTURE_EXPLICIT_UNKNOWN,
        slice37_fixture_name=FIXTURE_UNMAPPED,
        expected_slice37_status=Slice37IntegrationStatus.COMPLETED_EXPLICIT_UNKNOWN,
        expected_slice38_status=CandidateProposalStatus.EXPLICIT_UNKNOWN,
    ),
    _fixture(
        fixture_name=FIXTURE_EXPLICIT_UNSUPPORTED,
        slice37_fixture_name=FIXTURE_UNSUPPORTED,
        expected_slice37_status=Slice37IntegrationStatus.COMPLETED_EXPLICIT_UNSUPPORTED,
        expected_slice38_status=CandidateProposalStatus.EXPLICIT_UNSUPPORTED,
    ),
    _fixture(
        fixture_name=FIXTURE_NO_MATCH_UNKNOWN,
        slice37_fixture_name=FIXTURE_NO_MATCH,
        expected_slice37_status=Slice37IntegrationStatus.COMPLETED_EXPLICIT_UNKNOWN,
        expected_slice38_status=CandidateProposalStatus.EXPLICIT_UNKNOWN,
    ),
)

_BY_NAME = {item.fixture_name: item for item in _FIXTURES}


def list_disabled_predicate_role_frame_fixtures(
) -> tuple[DisabledPredicateRoleFrameFixture, ...]:
    return _FIXTURES


def get_disabled_predicate_role_frame_fixture(
    fixture_name: str,
) -> DisabledPredicateRoleFrameFixture | None:
    if type(fixture_name) is not str:
        return None
    return _BY_NAME.get(fixture_name)


def is_exact_accepted_fixture(record: object) -> bool:
    if type(record) is not DisabledPredicateRoleFrameFixture:
        return False
    accepted = _BY_NAME.get(record.fixture_name)
    return accepted is not None and record == accepted


__all__ = (
    "FIXTURE_AMBIGUOUS_UNSUPPORTED",
    "FIXTURE_CANDIDATE_UNSUPPORTED",
    "FIXTURE_EXPLICIT_UNKNOWN",
    "FIXTURE_EXPLICIT_UNSUPPORTED",
    "FIXTURE_NO_MATCH_UNKNOWN",
    "get_disabled_predicate_role_frame_fixture",
    "is_exact_accepted_fixture",
    "list_disabled_predicate_role_frame_fixtures",
)
