"""Closed accepted static fixture registry for Slice 42H."""
from __future__ import annotations

from dataclasses import replace
from typing import Final

from .canonical import stable_identifier
from .schema import OutwardExpressionCloseoutFixture, Slice42FixtureScenario


def with_expected_fixture_id(
    value: OutwardExpressionCloseoutFixture,
) -> OutwardExpressionCloseoutFixture:
    expected = stable_identifier(
        "slice42h_outward_expression_closeout_fixture",
        value,
        excluded_fields=("fixture_id",),
    )
    return replace(value, fixture_id=expected)


_FIXTURES: Final[tuple[OutwardExpressionCloseoutFixture, ...]] = (
    with_expected_fixture_id(
        OutwardExpressionCloseoutFixture(
            fixture_id="placeholder",
            fixture_name="slice42h-blocked-expression-with-unresolved-alternative",
            scenario=(
                Slice42FixtureScenario.BLOCKED_EXPRESSION_WITH_UNRESOLVED_ALTERNATIVE
            ),
            expected_slice42a_source_custody_id=(
                "outward_expression_source_custody:"
                "79f571c73d1680cbc7b95169ef2acd21fa02ac7b2623d2c0610ef58c8287f94d"
            ),
            expected_slice42a_authority_requirement_id=(
                "outward_expression_authority_requirement:"
                "6c76754454bf90f91f4c5c3b96dff60dc4b95bce77ebd6116b275eee23c11d23"
            ),
            expected_slice42b_governance_bundle_id=(
                "outward_expression_governance_bundle:"
                "f6969cf933dc2074dbeb62099ac474cd843b0674e8be5521e386f1f5a6a1db9f"
            ),
            expected_slice42c_evaluation_input_id=(
                "expression_eligibility_evaluation_input:"
                "f8dd50eefe553554bcbd333fa442ec252c6d0dec8e6891924d3961a1d96101b0"
            ),
            expected_slice42c_result_id=(
                "expression_eligibility_result:"
                "5f73de040aded455bffc5a109e58916f287c218c8aea2c0af1b7d1dc91087e3d"
            ),
            expected_slice42d_projection_input_id=(
                "preservation_obligation_projection_input:"
                "6f323b68a3b836a5b99bcb7814f31d25c85c513e41fa92487549286e73bf15fd"
            ),
            expected_slice42d_result_id=(
                "preservation_obligation_projection_result:"
                "3f765d1e4c7b7b4a6686a07fd8461a71de1fe7b91d2e7c0a57593f671bf85f75"
            ),
            expected_obligation_package_id=(
                "expression_obligation_package:"
                "df01b7bd18a10b7822955b591eb1339330370d6c110f02cfc851a25ab3334a1c"
            ),
            expected_slice42e_plan_input_id=(
                "expression_plan_construction_input:"
                "be94fc2e2d2cb5f0d4e01e5c7909f5d98b056b2a90cd62d6c8a30e076d885ac9"
            ),
            expected_slice42e_result_id=(
                "expression_plan_construction_result:"
                "9d335ac293f796fa760c5d5b7bde21e65238d2e30fc25888758be9c2042c83a2"
            ),
            expected_expression_plan_id=(
                "controlled_expression_plan:"
                "eadb6a2b8ff3963f82933a81f451acaff7fc1a82cfc8ffc675d8cedd1f51ad2c"
            ),
            expected_slice42f_realization_input_id=(
                "surface-realization-input:"
                "d96bd5fa5f96fa91234a4ade936428b41d1cfc0181a18702f37fc96b52c1980a"
            ),
            expected_slice42f_result_id=(
                "surface-realization-result:"
                "d60f92e3a145fb9839a788241f6f59afcd6c916027c16f176110aa63bdcf69a4"
            ),
            expected_expression_candidate_id=(
                "unvalidated-expression-candidate:"
                "9aaebbab660e5449b65abe6933eb56d85be3ad52e145de36a11f2e472a27d105"
            ),
            expected_slice42g_integration_input_id=(
                "slice42g_integration_input:"
                "819e7def452b942afa7823425ac3806558c054c5ecfdb14e103a8fff1c1c0039"
            ),
            expected_slice42g_result_id=(
                "slice42g_msm_outward_expression_integration_result:"
                "c28a9228c95963fb7bb8ce888635f362a990040e2b3a36890d7bb6e89fc66cce"
            ),
            expected_slice42g_result_digest=(
                "4869d2470f250d16d935f7b0531777df160bfcc9090b22d60b956e778239ce1b"
            ),
            expected_source_manifest_id=(
                "meaning_structure_manifest_slice41e_successor:"
                "33d102c251bc2f74747c47abe11d7ec7b5ae1b0365bd5f54b69ca597f8878183"
            ),
            expected_source_manifest_sha256=(
                "ca83428e682d3521348160ef34bd6e1aae0f08eab63c1eb063247cf58dab36d6"
            ),
            expected_successor_manifest_id=(
                "meaning_structure_manifest_slice42g_successor:"
                "1967fb50851d52772478cdb0a09d1db75a2df848915c554492ec8049e6cb0ab0"
            ),
            expected_successor_manifest_sha256=(
                "90e6617745dd09bdeda854a5980d1c6e7cac052356493dde14697e399075b26c"
            ),
            expected_selected_meaning_ref=(
                "slice41e_integrated_selected_governed_meaning:"
                "f4477d332130847fbb16ee281c5dcf8a2d43e470245a2b913f8601a76bfa3c8f"
            ),
            expected_outward_meaning_ref=(
                "slice42g_integrated_governed_outward_meaning:"
                "ad7a691427b39263f273981aa5b8e5b49ec7ae0b44cb3f76f3b510c3e9645c95"
            ),
            expected_expression_link_ref=(
                "slice42g_integrated_expression_link:"
                "b6172f4915b3c5f4a3a749b72dd79793949252acd8ba7940f009584aee2b41f7"
            ),
            expected_external_authority_ref=(
                "slice42g_surface_realization_authority_reference:"
                "375d389516998288b8eb9dec2b5c5c51a2c45f4f5200004fa6c439c916d336fa"
            ),
            expected_companion_id=(
                "slice42g_msm_outward_expression_companion:"
                "0b0f7914b7cebb4a129b174f9d1731602f44a4f5f8e8cbbf7161334089f348c6"
            ),
            expected_receipt_id=(
                "slice42g_msm_outward_expression_receipt:"
                "f465c649d10a0a7c961936860cf7e883999e00d76dad6bef7948c5379831145c"
            ),
            expected_candidate_refs=(
                "msm_candidate_record:demo",
                "msm_candidate_record:alternative",
            ),
            expected_non_selection_refs=("nonselection:existing_alternative",),
            expected_alternative_refs=(
                "msm_candidate_record:alternative",
                "nonselection:existing_alternative",
            ),
            expected_unresolved_refs=(
                "ambiguity_ancestry:preserved_prior_branch",
                "clarification_ancestry:preserved_prior_exchange",
            ),
            expected_candidate_count=2,
            expected_non_selection_count=1,
            expected_selected_count=1,
            expected_outward_meaning_count=1,
            expected_expression_link_count=1,
            expected_validation_link_count=0,
            expected_delivery_link_count=0,
            accepted_fixture=True,
            synthetic=True,
            explicit_invocation_only=True,
            offline_only=True,
            in_memory_only=True,
            deterministic=True,
        )
    ),
)


def list_outward_expression_closeout_fixtures(
) -> tuple[OutwardExpressionCloseoutFixture, ...]:
    return _FIXTURES


def get_outward_expression_closeout_fixture(
    fixture_name: str,
) -> OutwardExpressionCloseoutFixture | None:
    if type(fixture_name) is not str:
        return None
    return next(
        (item for item in _FIXTURES if item.fixture_name == fixture_name),
        None,
    )


def is_exact_accepted_fixture(value: object) -> bool:
    return type(value) is OutwardExpressionCloseoutFixture and value in _FIXTURES


__all__ = (
    "get_outward_expression_closeout_fixture",
    "is_exact_accepted_fixture",
    "list_outward_expression_closeout_fixtures",
    "with_expected_fixture_id",
)
