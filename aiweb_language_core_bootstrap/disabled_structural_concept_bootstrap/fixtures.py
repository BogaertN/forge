"""Closed static fixture catalog for Slice 37G integration."""

from __future__ import annotations

from .schema import DisabledStructuralConceptFixture
from ..structural_concept_candidate_proposal import ProposalResultStatus


FIXTURE_ONE_TO_ONE = "slice37g-one-to-one-concept-admission"
FIXTURE_AMBIGUOUS = "slice37g-ambiguous-concept"
FIXTURE_UNMAPPED = "slice37g-unmapped-mapping"
FIXTURE_UNSUPPORTED = "slice37g-unsupported-sense"
FIXTURE_NO_MATCH = "slice37g-no-exact-controlled-match"


def _fixture(
    *,
    fixture_name: str,
    exact_source_text: str,
    sequence_number: int,
    expected_proposal_status: ProposalResultStatus,
    expected_lexical_occurrence_count: int,
    expected_concept_candidate_count: int,
    expected_sense_candidate_count: int,
    expected_unknown_count: int,
    expected_unsupported_count: int,
) -> DisabledStructuralConceptFixture:
    body = {
        "fixture_name": fixture_name,
        "exact_source_text": exact_source_text,
        "source_id": "slice37g.synthetic.fixture",
        "channel_id": "slice37g.offline.fixture",
        "sequence_number": sequence_number,
        "expected_proposal_status": expected_proposal_status.value,
        "expected_lexical_occurrence_count": expected_lexical_occurrence_count,
        "expected_concept_candidate_count": expected_concept_candidate_count,
        "expected_sense_candidate_count": expected_sense_candidate_count,
        "expected_unknown_count": expected_unknown_count,
        "expected_unsupported_count": expected_unsupported_count,
        "accepted_fixture": True,
        "synthetic": True,
        "explicit_invocation_only": True,
        "offline_only": True,
        "in_memory_only": True,
        "raw_text_not_carried_by_invocation": True,
    }
    record = DisabledStructuralConceptFixture(
        fixture_id="",
        **body,
    )
    return DisabledStructuralConceptFixture(
        fixture_id=record.expected_id(),
        **body,
    )


_FIXTURES = (
    _fixture(
        fixture_name=FIXTURE_ONE_TO_ONE,
        exact_source_text="Do not Concept Admission.",
        sequence_number=1,
        expected_proposal_status=ProposalResultStatus.CANDIDATES_PROPOSED,
        expected_lexical_occurrence_count=1,
        expected_concept_candidate_count=1,
        expected_sense_candidate_count=1,
        expected_unknown_count=0,
        expected_unsupported_count=0,
    ),
    _fixture(
        fixture_name=FIXTURE_AMBIGUOUS,
        exact_source_text="concept",
        sequence_number=2,
        expected_proposal_status=(
            ProposalResultStatus.CANDIDATES_WITH_UNRESOLVED_STATES
        ),
        expected_lexical_occurrence_count=1,
        expected_concept_candidate_count=2,
        expected_sense_candidate_count=2,
        expected_unknown_count=0,
        expected_unsupported_count=0,
    ),
    _fixture(
        fixture_name=FIXTURE_UNMAPPED,
        exact_source_text="mapping",
        sequence_number=3,
        expected_proposal_status=ProposalResultStatus.EXPLICIT_UNKNOWN,
        expected_lexical_occurrence_count=1,
        expected_concept_candidate_count=0,
        expected_sense_candidate_count=0,
        expected_unknown_count=1,
        expected_unsupported_count=0,
    ),
    _fixture(
        fixture_name=FIXTURE_UNSUPPORTED,
        exact_source_text="sense",
        sequence_number=4,
        expected_proposal_status=ProposalResultStatus.EXPLICIT_UNSUPPORTED,
        expected_lexical_occurrence_count=1,
        expected_concept_candidate_count=0,
        expected_sense_candidate_count=0,
        expected_unknown_count=0,
        expected_unsupported_count=1,
    ),
    _fixture(
        fixture_name=FIXTURE_NO_MATCH,
        exact_source_text="banana",
        sequence_number=5,
        expected_proposal_status=ProposalResultStatus.EXPLICIT_UNKNOWN,
        expected_lexical_occurrence_count=0,
        expected_concept_candidate_count=0,
        expected_sense_candidate_count=0,
        expected_unknown_count=1,
        expected_unsupported_count=0,
    ),
)

_BY_NAME = {item.fixture_name: item for item in _FIXTURES}


def list_disabled_structural_concept_fixtures(
) -> tuple[DisabledStructuralConceptFixture, ...]:
    return _FIXTURES


def get_disabled_structural_concept_fixture(
    fixture_name: str,
) -> DisabledStructuralConceptFixture | None:
    if type(fixture_name) is not str:
        return None
    return _BY_NAME.get(fixture_name)


def is_exact_accepted_fixture(record: object) -> bool:
    if type(record) is not DisabledStructuralConceptFixture:
        return False
    accepted = _BY_NAME.get(record.fixture_name)
    return accepted is not None and record == accepted


__all__ = (
    "FIXTURE_AMBIGUOUS",
    "FIXTURE_NO_MATCH",
    "FIXTURE_ONE_TO_ONE",
    "FIXTURE_UNMAPPED",
    "FIXTURE_UNSUPPORTED",
    "get_disabled_structural_concept_fixture",
    "is_exact_accepted_fixture",
    "list_disabled_structural_concept_fixtures",
)
