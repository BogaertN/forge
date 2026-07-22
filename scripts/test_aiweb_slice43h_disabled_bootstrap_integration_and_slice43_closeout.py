#!/usr/bin/env python3
"""Visible behavior and adversarial test for AI.Web Slice 43H."""
from __future__ import annotations

import argparse
from dataclasses import FrozenInstanceError, replace
import importlib
from pathlib import Path
import runpy
import subprocess
import sys
from typing import Any

PACKAGE = (
    "aiweb_language_core_bootstrap.rmc_echo_runtime."
    "disabled_echo_closeout"
)
SLICE42H_TEST = (
    "test_aiweb_slice42h_disabled_bootstrap_integration_and_slice42_closeout.py"
)


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.malformed_cases = 0
        self.explicit_rejections = 0
        self.acceptance_field_checks = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)

    def malformed(self, condition: object, label: str) -> None:
        self.malformed_cases += 1
        self.check(condition, label)

    def rejection(self, condition: object, label: str) -> None:
        self.explicit_rejections += 1
        self.check(condition, label)

    def acceptance(self, condition: object, label: str) -> None:
        self.acceptance_field_checks += 1
        self.check(condition, label)


def run(arguments: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=str(cwd) if cwd is not None else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git(repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return run(["/usr/bin/git", "-C", str(repository), *arguments])


def repository_fingerprint(repository: Path) -> tuple[str, str, str]:
    head = git(repository, "rev-parse", "HEAD")
    tree = git(repository, "rev-parse", "HEAD^{tree}")
    status = git(repository, "status", "--porcelain=v1", "--untracked-files=all")
    if head.returncode or tree.returncode or status.returncode:
        return ("<git-error>", "<git-error>", "<git-error>")
    return (head.stdout.strip(), tree.stdout.strip(), status.stdout)


def build_exact_source(repository: Path) -> tuple[Any, Any, Any]:
    helpers = runpy.run_path(str(repository / "scripts" / SLICE42H_TEST))
    builder = helpers.get("build_exact_slice42g_input")
    if not callable(builder):
        raise RuntimeError("accepted Slice 42G fixture builder unavailable")
    integration42g, input42g = builder(repository)
    close42 = importlib.import_module(
        "aiweb_language_core_bootstrap.outward_expression_runtime."
        "disabled_outward_expression_closeout"
    )
    fixture42 = close42.list_outward_expression_closeout_fixtures()[0]
    state42 = close42.build_disabled_outward_expression_closeout_state(
        explicit_offline_developer_enable=True
    )
    invocation42 = close42.build_outward_expression_closeout_invocation(
        fixture42.fixture_name
    )
    result42 = close42.run_disabled_outward_expression_closeout(
        invocation42,
        state=state42,
        integration_input=input42g,
    )
    return integration42g, input42g, result42


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))

    ledger = Ledger()
    before = repository_fingerprint(repository)
    package = importlib.import_module(PACKAGE)
    manifest_serialization = importlib.import_module(
        "aiweb_language_core_bootstrap.meaning_structure_manifest.serialization"
    )
    _, input42g, result42h = build_exact_source(repository)

    ledger.check(
        package.PRE_SLICE43_COMMIT
        == "ebe931909b59a40ac4ef202b89d8f4f2702104a3",
        "exact pre-Slice-43 commit",
    )
    ledger.check(
        package.PRE_SLICE43_TREE
        == "efab06b171dfd5a34b56c0cff81026788e40a1e0",
        "exact pre-Slice-43 tree",
    )
    ledger.check(
        package.SLICE43G_ACCEPTED_HEAD
        == "2840bc205de8f2934a8a84941a560f22215fd10d",
        "accepted Slice 43G head",
    )
    ledger.check(
        package.SLICE43G_ACCEPTED_TREE
        == "89e2a4f0d3512aec1292487116bba5b559c7ce6c",
        "accepted Slice 43G tree",
    )
    ledger.check(
        package.SLICE43H_COMMIT_SUBJECT
        == "Slice 43H disabled bootstrap integration and Slice 43 closeout",
        "exact Slice 43H commit subject",
    )
    ledger.check(
        package.SLICE43_INCREMENT_LABELS
        == ("43A", "43B", "43C", "43D", "43E", "43F", "43G", "43H"),
        "fixed Slice 43 increment sequence",
    )
    ledger.check(len(package.SLICE43_ACCEPTED_CHAIN) == 8, "accepted chain count")
    ledger.check(len(package.EXPECTED_STAGE_CHAIN) == 9, "stage chain count")
    ledger.check(
        "Slice 44 remains unstarted" in package.SLICE43_PERMANENT_BOUNDARIES,
        "Slice 44 boundary",
    )
    ledger.check(
        "EchoForge is not RMC Echo" in package.SLICE43_PERMANENT_BOUNDARIES,
        "EchoForge separation boundary",
    )

    disabled = package.build_disabled_echo_closeout_state()
    enabled = package.build_disabled_echo_closeout_state(
        explicit_offline_developer_enable=True
    )
    ledger.check(package.validate_state(disabled).ok, "disabled state validates")
    ledger.check(package.validate_state(enabled).ok, "enabled state validates")
    ledger.check(disabled.enabled is False, "disabled by default")
    ledger.check(enabled.enabled is True, "explicit enable")
    ledger.check(disabled.state_id != enabled.state_id, "state identity includes enablement")
    for field in (
        "disabled_by_default", "explicit_invocation_required",
        "accepted_static_fixture_only", "offline_only", "read_only",
        "in_memory_only", "deterministic", "exact_profile_bounded",
        "source_preserving", "rollback_safe",
    ):
        ledger.check(getattr(disabled, field) is True, "state required " + field)
    for field in (
        "automatic_activation_allowed", "arbitrary_input_allowed", "route_allowed",
        "api_allowed", "network_allowed", "filesystem_read_allowed",
        "filesystem_write_allowed", "memory_read_allowed", "memory_write_allowed",
        "tool_allowed", "action_allowed", "rendering_allowed", "delivery_allowed",
        "echoforge_allowed", "llm_allowed", "truth_authority_allowed",
        "evidence_authority_allowed", "permission_authority_allowed",
        "execution_authority_allowed", "slice44_allowed",
    ):
        ledger.check(getattr(disabled, field) is False, "state boundary " + field)

    fixtures = package.list_echo_closeout_fixtures()
    ledger.check(len(fixtures) == 1, "one closed fixture")
    fixture = fixtures[0]
    ledger.check(package.validate_fixture(fixture).ok, "fixture validates")
    ledger.check(package.is_exact_accepted_fixture(fixture), "fixture exact registry member")
    for field in (
        "accepted_fixture", "synthetic", "explicit_invocation_only", "offline_only",
        "in_memory_only", "deterministic",
    ):
        ledger.check(getattr(fixture, field) is True, "fixture required " + field)
    ledger.check(
        fixture.expected_source_42h_result_id == result42h.result_id,
        "fixture exact Slice 42H result",
    )
    ledger.check(
        fixture.expected_source_42h_result_digest == result42h.result_digest,
        "fixture exact Slice 42H digest",
    )
    ledger.check(
        fixture.expected_source_42g_input_id == input42g.integration_input_id,
        "fixture exact Slice 42G input",
    )

    invocation = package.build_echo_closeout_invocation(fixture.fixture_name)
    ledger.check(invocation is not None, "invocation constructed")
    ledger.check(package.validate_invocation(invocation).ok, "invocation validates")

    refused = package.run_disabled_echo_closeout(
        invocation, state=disabled, source_42h_result=result42h
    )
    ledger.rejection(
        refused.status is package.Slice43CloseoutStatus.REFUSED_DISABLED,
        "default invocation refused",
    )
    ledger.check(package.validate_result(refused).ok, "disabled result validates")
    ledger.check(refused.stage_receipt_count == 0, "disabled result has no stages")

    invalid_invocation = package.run_disabled_echo_closeout(
        None, state=enabled, source_42h_result=result42h
    )
    ledger.rejection(
        invalid_invocation.status
        is package.Slice43CloseoutStatus.HELD_INVALID_INVOCATION,
        "missing invocation held",
    )
    ledger.check(package.validate_result(invalid_invocation).ok, "invalid invocation result validates")

    altered_invocation = replace(invocation, arbitrary_input_carried=True)
    arbitrary = package.run_disabled_echo_closeout(
        altered_invocation, state=enabled, source_42h_result=result42h
    )
    ledger.rejection(
        arbitrary.status is package.Slice43CloseoutStatus.HELD_INVALID_INVOCATION,
        "arbitrary input held",
    )

    fake_fixture_invocation = replace(invocation, fixture_id="fixture:unaccepted")
    wrong_fixture = package.run_disabled_echo_closeout(
        fake_fixture_invocation, state=enabled, source_42h_result=result42h
    )
    ledger.rejection(
        wrong_fixture.status
        is package.Slice43CloseoutStatus.HELD_FIXTURE_NOT_ACCEPTED,
        "unaccepted fixture held",
    )

    wrong_source = replace(result42h, result_id="slice42h:wrong")
    held_source = package.run_disabled_echo_closeout(
        invocation, state=enabled, source_42h_result=wrong_source
    )
    ledger.rejection(
        held_source.status
        is package.Slice43CloseoutStatus.HELD_INVALID_PREDECESSOR_OUTPUT,
        "wrong predecessor held",
    )

    completed = package.run_disabled_echo_closeout(
        invocation, state=enabled, source_42h_result=result42h
    )
    ledger.check(
        completed.status is package.Slice43CloseoutStatus.COMPLETED,
        "closeout completed",
    )
    ledger.check(package.validate_result(completed).ok, "completed result validates")

    ledger.check(
        completed.deterministic_repeat_digest
        == package.deterministic_digest({
            "source": completed.source_42h_result.result_id,
            "chain": [
                completed.source_admission_request.request_id,
                completed.comparison_request.request_id,
                completed.classification_request.request_id,
                completed.disposition_request.request_id,
                completed.msm_integration_input.integration_input_id,
            ],
            "results": [
                completed.source_admission_result.admission_result_id,
                completed.comparison_result.comparison_result_id,
                completed.classification_result.classification_result_id,
                completed.disposition_result.disposition_result_id,
                completed.msm_integration_result.result_id,
            ],
            "receipts": [receipt.receipt_id for receipt in completed.stage_receipts],
        }),
        "deterministic custody digest reproducible",
    )
    ledger.check(completed.exact_stage_chain_complete is True, "exact stage chain complete")
    ledger.check(completed.stage_receipt_count == 9, "nine stage receipts")
    ledger.check(
        tuple(receipt.stage for receipt in completed.stage_receipts)
        == package.EXPECTED_STAGE_CHAIN,
        "stage order exact",
    )
    for index, receipt in enumerate(completed.stage_receipts, start=1):
        ledger.check(receipt.stage_index == index, f"stage index {index}")
        ledger.check(package.validate_stage_receipt(receipt).ok, f"stage receipt {index} validates")
        for field in (
            "deterministic", "source_preserved", "offline_only", "in_memory_only"
        ):
            ledger.check(getattr(receipt, field) is True, f"stage {index} {field}")
        for field in (
            "route_created", "api_created", "network_accessed",
            "filesystem_read_performed", "filesystem_write_performed",
            "memory_read_performed", "memory_write_performed", "tool_invoked",
            "action_performed", "rendered", "delivered", "echoforge_used", "llm_used",
        ):
            ledger.check(getattr(receipt, field) is False, f"stage {index} zero {field}")

    acceptance = completed.acceptance_record
    ledger.check(package.validate_acceptance_record(acceptance).ok, "acceptance record validates")
    acceptance_expectations = {
        "slice43a_through_43h_completed": True,
        "authorized_meaning_required": True,
        "proposed_expression_required": True,
        "selected_meaning_preserved": True,
        "scope_preserved": True,
        "certainty_preserved": True,
        "evidence_status_preserved": True,
        "caveats_preserved": True,
        "refusal_state_preserved": True,
        "unresolved_conditions_preserved": True,
        "material_drift_rejected_or_contained": True,
        "echoforge_used": False,
        "llm_used": False,
        "delivery_authority": False,
        "truth_authority": False,
        "evidence_authority": False,
        "permission_authority": False,
        "execution_authority": False,
        "slice44_started": False,
    }
    for field, expected in acceptance_expectations.items():
        ledger.acceptance(getattr(acceptance, field) is expected, "acceptance " + field)
    ledger.check(acceptance.slice43_closed is True, "Slice 43 closed")
    ledger.check(acceptance.stop_after_slice43 is True, "stop after Slice 43")
    ledger.check(acceptance.runtime_self_grants_acceptance is False, "no runtime self acceptance")
    ledger.check(acceptance.production_ready is False, "not production-ready claim")

    result43g = completed.msm_integration_result
    ledger.check(result43g is not None, "Slice 43G result retained")
    ledger.check(result43g.validation_disposition.value == "PASSED", "exact PASSED disposition")
    ledger.check(result43g.validation_link_created is True, "validation link created")
    ledger.check(result43g.delivery_link_created is False, "no delivery link")
    ledger.check(result43g.delivery_authorized_or_performed is False, "no delivery authority")
    ledger.check(result43g.echoforge_called is False, "EchoForge not called")
    ledger.check(result43g.model_or_similarity_authority_used is False, "no model authority")
    ledger.check(result43g.msm_schema_modified is False, "MSM schema unchanged")
    ledger.check(result43g.gp014_superseded is False, "GP-014 not superseded")
    ledger.check(
        manifest_serialization.canonical_manifest_sha256(result43g.source_manifest)
        == fixture.expected_43g_source_manifest_sha256,
        "source manifest exact hash",
    )
    ledger.check(
        manifest_serialization.canonical_manifest_sha256(result43g.successor_manifest)
        == fixture.expected_43g_successor_manifest_sha256,
        "successor manifest exact hash",
    )
    ledger.check(
        result43g.source_manifest.manifest_id
        == result42h.integration_result.successor_manifest.manifest_id,
        "exact Slice 42G manifest identity carried into Echo custody",
    )
    ledger.check(
        len(result43g.successor_manifest.validation_links)
        == len(result43g.source_manifest.validation_links) + 1,
        "exact one validation link added",
    )
    ledger.check(
        tuple(record.record_id for record in result43g.successor_manifest.delivery_or_containment_links)
        == tuple(record.record_id for record in result43g.source_manifest.delivery_or_containment_links),
        "PASSED fixture adds no delivery or containment link",
    )

    for field in (
        "authorized_meaning_required", "proposed_expression_required",
        "selected_meaning_preserved", "scope_preserved", "certainty_preserved",
        "evidence_status_preserved", "caveats_preserved", "refusal_state_preserved",
        "unresolved_conditions_preserved", "material_drift_rejected_or_contained",
    ):
        ledger.check(getattr(completed, field) is True, "result required " + field)
    for field in (
        "echoforge_used", "llm_used", "delivery_authority", "truth_authority",
        "evidence_authority", "permission_authority", "execution_authority",
        "slice44_started", "route_api_network_filesystem_memory_tool_action_authority",
        "source_manifest_mutated", "delivery_link_created", "gp014_superseded",
    ):
        ledger.check(getattr(completed, field) is False, "result zero " + field)

    try:
        completed.status = package.Slice43CloseoutStatus.HELD_INVALID_STATE
        immutable = False
    except FrozenInstanceError:
        immutable = True
    ledger.check(immutable, "result immutable")
    try:
        acceptance.slice44_started = True
        acceptance_immutable = False
    except FrozenInstanceError:
        acceptance_immutable = True
    ledger.check(acceptance_immutable, "acceptance immutable")

    ledger.malformed(
        not package.validate_state(replace(disabled, network_allowed=True)).ok,
        "state rejects network authority",
    )
    ledger.malformed(
        not package.validate_invocation(replace(invocation, arbitrary_input_carried=True)).ok,
        "invocation rejects arbitrary input",
    )
    ledger.malformed(
        not package.validate_acceptance_record(replace(acceptance, delivery_authority=True)).ok,
        "acceptance rejects delivery authority",
    )
    ledger.malformed(
        not package.validate_acceptance_record(replace(acceptance, slice44_started=True)).ok,
        "acceptance rejects Slice 44 start",
    )
    ledger.malformed(
        not package.validate_stage_receipt(replace(completed.stage_receipts[0], llm_used=True)).ok,
        "receipt rejects LLM use",
    )
    ledger.malformed(
        not package.validate_result(replace(completed, echoforge_used=True)).ok,
        "result rejects EchoForge use",
    )
    ledger.malformed(
        not package.validate_result(replace(completed, delivery_link_created=True)).ok,
        "result rejects delivery link",
    )

    after = repository_fingerprint(repository)
    ledger.check(before == after, "repository unchanged")

    print("=== AI.WEB SLICE 43H BEHAVIOR TEST ===")
    print(f"repository={repository}")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print(f"explicit_rejection_cases={ledger.explicit_rejections}")
    print(f"acceptance_field_checks={ledger.acceptance_field_checks}")
    print("slice43A_through_43H_completed=1")
    print("authorized_meaning_required=1")
    print("proposed_expression_required=1")
    print("selected_meaning_preserved=1")
    print("scope_preserved=1")
    print("certainty_preserved=1")
    print("evidence_status_preserved=1")
    print("caveats_preserved=1")
    print("refusal_state_preserved=1")
    print("unresolved_conditions_preserved=1")
    print("material_drift_rejected_or_contained=1")
    print("disabled_by_default=1")
    print("explicit_invocation_required=1")
    print("accepted_static_fixture_only=1")
    print("offline_in_memory_deterministic=1")
    print("stage_receipt_count=9")
    print("echoforge_used=0")
    print("llm_used=0")
    print("delivery_authority=0")
    print("truth_authority=0")
    print("evidence_authority=0")
    print("permission_authority=0")
    print("execution_authority=0")
    print("slice44_started=0")
    print("route_api_network_filesystem_memory_tool_action_authority=0")
    print("source_manifest_mutated=0")
    print("delivery_link_created=0")
    print("gp014_superseded=0")
    print(f"failure_count={len(ledger.failures)}")
    if ledger.failures:
        for failure in ledger.failures:
            print("FAIL: " + failure)
        print("AI.WEB SLICE 43H BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 43H BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
