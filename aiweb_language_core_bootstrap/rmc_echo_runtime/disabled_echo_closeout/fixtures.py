"""Closed accepted-static-fixture registry for Slice 43H."""
from __future__ import annotations

from dataclasses import replace

from .canonical import stable_identifier
from .schema import EchoCloseoutFixture, Slice43FixtureScenario


def with_expected_fixture_id(value: EchoCloseoutFixture) -> EchoCloseoutFixture:
    body = replace(value, fixture_id="pending")
    return replace(
        value,
        fixture_id=stable_identifier("slice43h_echo_closeout_fixture", body),
    )


_ACCEPTED_FIXTURE = with_expected_fixture_id(
    EchoCloseoutFixture(
        fixture_id="pending",
        fixture_name="accepted_slice43_passed_echo_validation_closeout",
        scenario=Slice43FixtureScenario.ACCEPTED_PASSED_ECHO_VALIDATION,
        expected_source_42h_result_id="slice42h_disabled_outward_expression_closeout_result:107e9914332219bb299f72f4904eb1d3aa0c748e4fb14dba7d611229967a3f9e",
        expected_source_42h_result_digest="052883e588c23e39435abc5feb9cd057bd4bd96c9fbf867e45c0cc3bace23cdd",
        expected_source_42h_acceptance_record_id="slice42_acceptance_record:4478ef7310eb45518e9ea62e2e5ed7265023db47b8bdb9a682e1ea891dc0b7f2",
        expected_source_42g_input_id="slice42g_integration_input:819e7def452b942afa7823425ac3806558c054c5ecfdb14e103a8fff1c1c0039",
        expected_source_42g_result_id="slice42g_msm_outward_expression_integration_result:c28a9228c95963fb7bb8ce888635f362a990040e2b3a36890d7bb6e89fc66cce",
        expected_source_42g_result_digest="4869d2470f250d16d935f7b0531777df160bfcc9090b22d60b956e778239ce1b",
        expected_43c_request_id="slice43c_source_admission_request:f82be4bd8cd80a0394ab263fc2290610aca42ed0b69ca990e5a28bcea84285a5",
        expected_43c_result_id="slice43c_source_admission_result:7ad6af0a3ac257c63af99489dd5991528157377e5d809ed2f66b5dfcf35a3990",
        expected_43c_result_digest="7ad6af0a3ac257c63af99489dd5991528157377e5d809ed2f66b5dfcf35a3990",
        expected_43d_request_id="slice43d_meaning_preservation_comparison_request:f78d2cd331f0b9f483ee2ea344ab0a469fcb30c8abbd73a29c5234d2be4c887d",
        expected_43d_result_id="slice43d_meaning_preservation_comparison_result:be8cc7ecbb5c443e71bd81e165834d13a7bf946cd300ab480227e8a04172f1d1",
        expected_43d_result_digest="be8cc7ecbb5c443e71bd81e165834d13a7bf946cd300ab480227e8a04172f1d1",
        expected_43e_request_id="slice43e_drift_classification_request:6dcb65e550221292a8e655acbb97a8d04091116a6d2c504635079b47ba34fe64",
        expected_43e_result_id="slice43e_drift_classification_result:8051bfe8dfeef4b451ffe557f92c0afc549f98679ae0b068170e563b3a89fde9",
        expected_43e_result_digest="8051bfe8dfeef4b451ffe557f92c0afc549f98679ae0b068170e563b3a89fde9",
        expected_43f_request_id="slice43f_echo_disposition_request:c2599ed1b4f89577ded83e23cfa11c1b5107bb0cb49bf590269a50fa1850a7d7",
        expected_43f_result_id="slice43f_echo_disposition_result:89812df642f40d58173b5543a93214f038294524e1135ebbb87dd28e787581c0",
        expected_43f_result_digest="89812df642f40d58173b5543a93214f038294524e1135ebbb87dd28e787581c0",
        expected_43f_disposition="PASSED",
        expected_43g_input_id="slice43g_integration_input:e7865a211e05e5d3e5f7d8c91a0940af1727ae18d508ca807362355ee7d2d81e",
        expected_43g_result_id="slice43g_msm_echo_validation_integration_result:728dc589e0351f58375fc695df6159dcac26f16a0ae44620498419bed9529bc2",
        expected_43g_result_digest="728dc589e0351f58375fc695df6159dcac26f16a0ae44620498419bed9529bc2",
        expected_43g_source_manifest_id="meaning_structure_manifest_slice42g_successor:1967fb50851d52772478cdb0a09d1db75a2df848915c554492ec8049e6cb0ab0",
        expected_43g_source_manifest_sha256="90e6617745dd09bdeda854a5980d1c6e7cac052356493dde14697e399075b26c",
        expected_43g_successor_manifest_id="meaning_structure_manifest_slice43g_successor:f049750a7ce69172d899d96227c5fc3910cc391160beb9611389334f1b90a160",
        expected_43g_successor_manifest_sha256="0da8fb37b4d6d9c495cf58b3cd852fd1dab64758159b38e6585f0818e58ba716",
        expected_43g_validation_link_id="slice43g_echo_validation_link:b4a06094e9104b089e8cd0e95b92c53468941d1da251e47cae0601b835ad199c",
        expected_43g_companion_id="slice43g_msm_echo_validation_companion:986b75a0c2659b65ab191fb318ca62430a3564cacf2681333aa07cb11cc7fe23",
        expected_43g_receipt_id="slice43g_msm_echo_validation_receipt:4db557f1f7c6d5e01e28172558828e62e592ccef3be3746f45ef94086aad78ee",
        expected_dimension_finding_count=13,
        expected_classification_record_count=13,
        accepted_fixture=True,
        synthetic=True,
        explicit_invocation_only=True,
        offline_only=True,
        in_memory_only=True,
        deterministic=True,
    )
)


def list_echo_closeout_fixtures() -> tuple[EchoCloseoutFixture, ...]:
    return (_ACCEPTED_FIXTURE,)


def get_echo_closeout_fixture(fixture_name: str) -> EchoCloseoutFixture | None:
    if fixture_name == _ACCEPTED_FIXTURE.fixture_name:
        return _ACCEPTED_FIXTURE
    return None


def is_exact_accepted_fixture(value: object) -> bool:
    return type(value) is EchoCloseoutFixture and value == _ACCEPTED_FIXTURE


__all__ = tuple(name for name in globals() if not name.startswith("_"))
