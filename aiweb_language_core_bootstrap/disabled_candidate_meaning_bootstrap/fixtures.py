"""Closed accepted static fixtures for Slice 39H."""
from __future__ import annotations
from dataclasses import replace
from typing import Final
from .schema import DisabledCandidateMeaningFixture, FixtureScenario


def _fixture(**kwargs: object) -> DisabledCandidateMeaningFixture:
    draft = DisabledCandidateMeaningFixture(fixture_id="", **kwargs)
    return replace(draft, fixture_id=draft.expected_id())

_FIXTURES: Final[tuple[DisabledCandidateMeaningFixture, ...]] = (
    _fixture(
        fixture_name="slice39h-zero-unknown-predicate",
        scenario=FixtureScenario.ZERO_UNKNOWN_PREDICATE,
        exact_source_text="Inspect Concept Admission.",
        source_id="slice39h.fixture.zero-unknown-predicate",
        channel_id="slice39h.fixture",
        sequence_number=1,
        expected_constructor_status="zero_candidates",
        expected_manifest_status="zero_candidates",
        expected_unique_candidate_count=0,
        expected_manifest_candidate_count=0,
        expected_missing_role_minimum=0,
        accepted_fixture=True, synthetic=True, explicit_invocation_only=True,
        offline_only=True, in_memory_only=True, raw_text_not_carried_by_invocation=True,
    ),
    _fixture(
        fixture_name="slice39h-one-missing-role",
        scenario=FixtureScenario.ONE_MISSING_ROLE,
        exact_source_text="Inspect Concept Admission.",
        source_id="slice39h.fixture.one-missing-role",
        channel_id="slice39h.fixture",
        sequence_number=2,
        expected_constructor_status="constructed",
        expected_manifest_status="integrated",
        expected_unique_candidate_count=1,
        expected_manifest_candidate_count=1,
        expected_missing_role_minimum=1,
        accepted_fixture=True, synthetic=True, explicit_invocation_only=True,
        offline_only=True, in_memory_only=True, raw_text_not_carried_by_invocation=True,
    ),
    _fixture(
        fixture_name="slice39h-multi-candidate",
        scenario=FixtureScenario.MULTI_CANDIDATE,
        exact_source_text="Inspect Concept Admission.",
        source_id="slice39h.fixture.multi-candidate",
        channel_id="slice39h.fixture",
        sequence_number=3,
        expected_constructor_status="constructed",
        expected_manifest_status="integrated",
        expected_unique_candidate_count=2,
        expected_manifest_candidate_count=2,
        expected_missing_role_minimum=2,
        accepted_fixture=True, synthetic=True, explicit_invocation_only=True,
        offline_only=True, in_memory_only=True, raw_text_not_carried_by_invocation=True,
    ),
    _fixture(
        fixture_name="slice39h-unknown-concept",
        scenario=FixtureScenario.UNKNOWN_CONCEPT,
        exact_source_text="banana",
        source_id="slice39h.fixture.unknown-concept",
        channel_id="slice39h.fixture",
        sequence_number=4,
        expected_constructor_status="zero_candidates",
        expected_manifest_status="zero_candidates",
        expected_unique_candidate_count=0,
        expected_manifest_candidate_count=0,
        expected_missing_role_minimum=0,
        accepted_fixture=True, synthetic=True, explicit_invocation_only=True,
        offline_only=True, in_memory_only=True, raw_text_not_carried_by_invocation=True,
    ),
    _fixture(
        fixture_name="slice39h-conflicting-role",
        scenario=FixtureScenario.CONFLICTING_ROLE,
        exact_source_text="Inspect Concept Admission.",
        source_id="slice39h.fixture.conflicting-role",
        channel_id="slice39h.fixture",
        sequence_number=5,
        expected_constructor_status="constructed",
        expected_manifest_status="integrated",
        expected_unique_candidate_count=1,
        expected_manifest_candidate_count=1,
        expected_missing_role_minimum=2,
        accepted_fixture=True, synthetic=True, explicit_invocation_only=True,
        offline_only=True, in_memory_only=True, raw_text_not_carried_by_invocation=True,
    ),
)

def list_disabled_candidate_meaning_fixtures() -> tuple[DisabledCandidateMeaningFixture, ...]:
    return _FIXTURES

def get_disabled_candidate_meaning_fixture(name: str) -> DisabledCandidateMeaningFixture | None:
    if type(name) is not str:
        return None
    for item in _FIXTURES:
        if item.fixture_name == name:
            return item
    return None

def is_exact_accepted_fixture(value: object) -> bool:
    return type(value) is DisabledCandidateMeaningFixture and value in _FIXTURES

__all__ = (
    "get_disabled_candidate_meaning_fixture",
    "is_exact_accepted_fixture",
    "list_disabled_candidate_meaning_fixtures",
)
