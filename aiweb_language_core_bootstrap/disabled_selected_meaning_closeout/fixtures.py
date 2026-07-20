"""Closed accepted static fixture registry for Slice 41F."""
from __future__ import annotations

from dataclasses import replace
from typing import Final

from .canonical import stable_identifier
from .schema import SelectedMeaningCloseoutFixture, Slice41FixtureScenario


def with_expected_fixture_id(
    value: SelectedMeaningCloseoutFixture,
) -> SelectedMeaningCloseoutFixture:
    expected = stable_identifier(
        "slice41f_selected_meaning_closeout_fixture",
        value,
        excluded_fields=("fixture_id",),
    )
    return replace(value, fixture_id=expected)


_FIXTURES: Final[tuple[SelectedMeaningCloseoutFixture, ...]] = (
    with_expected_fixture_id(
        SelectedMeaningCloseoutFixture(
            fixture_id="placeholder",
            fixture_name="slice41f-selected-with-unresolved-alternative",
            scenario=Slice41FixtureScenario.SELECTED_WITH_UNRESOLVED_ALTERNATIVE,
            expected_integration_input_id=(
                "slice41e_integration_input:"
                "478a7be6a25a92564bdf1129997f57e8b2f93d473e8c41d8e35c54b4f0f55d2a"
            ),
            expected_source_manifest_id="manifest:rich_with_existing_nonselection",
            expected_source_manifest_sha256=(
                "0dde8c81fd6d008cc7ababd8057dd9de91362f7480c773f32ba63f871f89cfbb"
            ),
            expected_successor_manifest_id=(
                "meaning_structure_manifest_slice41e_successor:"
                "33d102c251bc2f74747c47abe11d7ec7b5ae1b0365bd5f54b69ca597f8878183"
            ),
            expected_successor_manifest_sha256=(
                "ca83428e682d3521348160ef34bd6e1aae0f08eab63c1eb063247cf58dab36d6"
            ),
            expected_integration_result_id=(
                "slice41e_msm_selected_meaning_integration_result:"
                "bac73e2b4118492e7d3452b84adae94836ab0ca668e211c18604bca50d29006c"
            ),
            expected_integration_result_digest=(
                "ff2e0399053f74d7c0a45eab0df7dd0a68253a00538093b5a278de184a1516a6"
            ),
            expected_selected_candidate_ref="msm_candidate_record:demo",
            expected_selection_receipt_ref=(
                "selected_meaning_selection_receipt:"
                "e0088941ee490496f4ef12c95767894a79297545de33b77b1718c84ceb990863"
            ),
            expected_integrated_selected_meaning_ref=(
                "slice41e_integrated_selected_governed_meaning:"
                "f4477d332130847fbb16ee281c5dcf8a2d43e470245a2b913f8601a76bfa3c8f"
            ),
            expected_candidate_refs=(
                "msm_candidate_record:demo",
                "msm_candidate_record:alternative",
            ),
            expected_non_selection_outcome_refs=(
                "nonselection:existing_alternative",
            ),
            expected_source_candidate_count=2,
            expected_source_non_selection_count=1,
            expected_successor_selected_count=1,
            expected_unresolved_outcome_count=1,
            accepted_fixture=True,
            synthetic=True,
            explicit_invocation_only=True,
            offline_only=True,
            in_memory_only=True,
            deterministic=True,
        )
    ),
)


def list_selected_meaning_closeout_fixtures(
) -> tuple[SelectedMeaningCloseoutFixture, ...]:
    return _FIXTURES


def get_selected_meaning_closeout_fixture(
    fixture_name: str,
) -> SelectedMeaningCloseoutFixture | None:
    if type(fixture_name) is not str:
        return None
    return next(
        (item for item in _FIXTURES if item.fixture_name == fixture_name),
        None,
    )


def is_exact_accepted_fixture(value: object) -> bool:
    return type(value) is SelectedMeaningCloseoutFixture and value in _FIXTURES


__all__ = (
    "get_selected_meaning_closeout_fixture",
    "is_exact_accepted_fixture",
    "list_selected_meaning_closeout_fixtures",
    "with_expected_fixture_id",
)
