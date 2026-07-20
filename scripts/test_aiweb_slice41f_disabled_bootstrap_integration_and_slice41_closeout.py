#!/usr/bin/env python3
"""Visible behavior and adversarial test for AI.Web Slice 41F."""
from __future__ import annotations

import argparse
from dataclasses import FrozenInstanceError, replace
import hashlib
import importlib
from pathlib import Path, PurePosixPath
import runpy
import shutil
import subprocess
import sys
import tempfile

PACKAGE = "aiweb_language_core_bootstrap.disabled_selected_meaning_closeout"
SLICE41E_TEST = (
    "test_aiweb_slice41e_msm_selected_meaning_integration_and_custody.py"
)


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.malformed_cases = 0
        self.explicit_rejections = 0
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


def run(
    arguments: list[str],
    *,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git(repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return run(["git", "-C", str(repository), *arguments])


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_hash_manifest(
    path: Path,
    ledger: Ledger,
) -> tuple[tuple[str, str], ...]:
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        1,
    ):
        if not line:
            continue
        try:
            expected_hash, relative = line.split("  ", 1)
        except ValueError:
            ledger.check(False, f"malformed hash manifest line {line_number}")
            continue
        pure = PurePosixPath(relative)
        safe = (
            len(expected_hash) == 64
            and all(character in "0123456789abcdef" for character in expected_hash)
            and not pure.is_absolute()
            and ".." not in pure.parts
            and relative not in seen
        )
        ledger.check(safe, f"safe hash manifest line {line_number}")
        if safe:
            seen.add(relative)
            entries.append((expected_hash, relative))
    return tuple(entries)


def build_exact_slice41e_input(repository: Path):
    helpers = runpy.run_path(str(repository / "scripts" / SLICE41E_TEST))
    integration = importlib.import_module(
        "aiweb_language_core_bootstrap.selected_meaning_runtime."
        "msm_selected_meaning_integration"
    )
    values = helpers["_rich_chain"](repository)
    gate_result = values[6]
    construction_input = values[7]
    construction_package = values[8]
    integration_input = helpers["_integration_input"](
        integration,
        gate_result,
        construction_input,
        construction_package,
    )
    return integration, integration_input


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    arguments = parser.parse_args()
    repository = Path(arguments.repository).resolve()
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))

    ledger = Ledger()
    package = importlib.import_module(PACKAGE)
    manifest_package = importlib.import_module(
        "aiweb_language_core_bootstrap.meaning_structure_manifest"
    )
    integration, integration_input = build_exact_slice41e_input(repository)
    direct_result = integration.integrate_selected_meaning_into_manifest(
        integration_input
    )

    ledger.check(
        package.PRE_SLICE41_COMMIT
        == "fcc6b57e62e95cbfe2dbc80b88a212432c681907",
        "pre-Slice-41 commit",
    )
    ledger.check(
        package.PRE_SLICE41_TREE
        == "55dc8ebf863c2df547ae31b38e3445b25f6cc22a",
        "pre-Slice-41 tree",
    )
    ledger.check(
        package.SLICE41E_ACCEPTED_HEAD
        == "1aa5513e14593e4e2d510161f3204a38536d87ea",
        "accepted Slice 41E head",
    )
    ledger.check(
        package.SLICE41E_ACCEPTED_TREE
        == "aca30bba4b2b52f8cac6f61f697185a91c534c3d",
        "accepted Slice 41E tree",
    )
    ledger.check(
        package.SLICE41F_COMMIT_SUBJECT
        == "Slice 41F disabled bootstrap integration and Slice 41 closeout",
        "Slice 41F commit subject",
    )
    ledger.check(
        package.SLICE41_INCREMENT_LABELS
        == ("41A", "41B", "41C", "41D", "41E", "41F"),
        "fixed Slice 41 increment sequence",
    )
    ledger.check(len(package.SLICE41_ACCEPTED_CHAIN) == 6, "accepted chain count")
    ledger.check(
        "selected meaning is bounded semantic custody only"
        in package.SLICE41_PERMANENT_BOUNDARIES,
        "bounded custody boundary",
    )
    ledger.check(
        "Slice 42 remains unstarted" in package.SLICE41_PERMANENT_BOUNDARIES,
        "Slice 42 boundary",
    )

    disabled_state = package.build_disabled_selected_meaning_closeout_state()
    enabled_state = package.build_disabled_selected_meaning_closeout_state(
        explicit_offline_developer_enable=True
    )
    ledger.check(package.validate_state(disabled_state).ok, "disabled state valid")
    ledger.check(package.validate_state(enabled_state).ok, "enabled state valid")
    ledger.check(disabled_state.enabled is False, "disabled by default")
    ledger.check(enabled_state.enabled is True, "explicit enable")
    ledger.check(
        disabled_state.state_id != enabled_state.state_id,
        "state identities distinguish enablement",
    )
    ledger.check(
        disabled_state.route_allowed is False
        and disabled_state.api_allowed is False,
        "no route or API",
    )
    ledger.check(
        disabled_state.network_allowed is False
        and disabled_state.filesystem_write_allowed is False
        and disabled_state.memory_write_allowed is False,
        "no network filesystem or memory write",
    )

    fixtures = package.list_selected_meaning_closeout_fixtures()
    ledger.check(len(fixtures) == 1, "one closed fixture")
    fixture = fixtures[0]
    ledger.check(package.validate_fixture(fixture).ok, "fixture valid")
    ledger.check(package.is_exact_accepted_fixture(fixture), "fixture accepted")
    ledger.check(
        fixture.expected_integration_input_id
        == integration_input.integration_input_id,
        "fixture exact integration input identity",
    )
    ledger.check(
        fixture.expected_integration_result_id == direct_result.result_id,
        "fixture exact integration result identity",
    )
    ledger.check(
        fixture.expected_integration_result_digest
        == direct_result.canonical_digest,
        "fixture exact integration result digest",
    )

    invocation = package.build_selected_meaning_closeout_invocation(
        fixture.fixture_name
    )
    ledger.check(invocation is not None, "invocation built")
    assert invocation is not None
    ledger.check(package.validate_invocation(invocation).ok, "invocation valid")
    ledger.check(
        invocation.arbitrary_input_carried is False,
        "invocation carries no arbitrary input",
    )

    refused = package.run_disabled_selected_meaning_closeout(
        invocation,
        integration_input=integration_input,
    )
    ledger.check(
        refused.status is package.Slice41CloseoutStatus.REFUSED_DISABLED,
        "disabled invocation refused",
    )
    ledger.check(package.validate_result(refused).ok, "disabled refusal valid")
    ledger.check(refused.stage_receipt_count == 0, "disabled refusal no stages")
    ledger.check(
        refused.final_slice41_acceptance_record_created is False,
        "disabled refusal does not close Slice 41",
    )

    source_before = integration_input.source_manifest
    first = package.run_disabled_selected_meaning_closeout(
        invocation,
        state=enabled_state,
        integration_input=integration_input,
    )
    second = package.run_disabled_selected_meaning_closeout(
        invocation,
        state=enabled_state,
        integration_input=integration_input,
    )
    third = package.run_disabled_selected_meaning_closeout(
        invocation,
        state=enabled_state,
        integration_input=integration_input,
    )
    ledger.check(first == second == third, "deterministic repeated closeout")
    ledger.check(
        first.result_id == second.result_id == third.result_id,
        "deterministic repeated result identity",
    )
    ledger.check(
        first.deterministic_repeat_digest
        == second.deterministic_repeat_digest
        == third.deterministic_repeat_digest,
        "deterministic repeated digest",
    )
    ledger.check(
        first.status is package.Slice41CloseoutStatus.COMPLETED,
        "closeout completed",
    )
    result_report = package.validate_result(first)
    ledger.check(result_report.ok, "completed result validates")
    for issue in result_report.issues:
        ledger.check(False, f"unexpected result issue {issue.path}:{issue.detail}")
    ledger.check(
        integration_input.source_manifest == source_before,
        "source manifest remains immutable",
    )
    ledger.check(
        first.integration_result == direct_result,
        "closeout uses exact deterministic Slice 41E result",
    )
    ledger.check(first.stage_receipt_count == 6, "six integration stages")
    ledger.check(
        tuple(item.stage for item in first.stage_receipts)
        == package.EXPECTED_STAGE_CHAIN,
        "exact stage order",
    )
    ledger.check(
        tuple(item.stage_index for item in first.stage_receipts)
        == (1, 2, 3, 4, 5, 6),
        "exact stage indices",
    )
    for receipt in first.stage_receipts:
        ledger.check(package.validate_stage_receipt(receipt).ok, "stage receipt valid")
        ledger.check(
            receipt.route_created is False
            and receipt.api_created is False
            and receipt.network_accessed is False,
            "stage has no route API or network",
        )
        ledger.check(
            receipt.filesystem_write_performed is False
            and receipt.memory_write_performed is False,
            "stage has no filesystem or memory write",
        )

    nested = first.integration_result
    assert nested is not None
    successor = nested.successor_manifest
    source = first.integration_input.source_manifest
    ledger.check(
        successor.candidate_meanings == source.candidate_meanings,
        "all candidate meanings retained exactly",
    )
    ledger.check(
        successor.non_selection_outcomes == source.non_selection_outcomes,
        "all non-selection outcomes retained exactly",
    )
    ledger.check(
        len(successor.candidate_meanings) == 2,
        "selected and alternative candidates retained",
    )
    ledger.check(
        len(successor.non_selection_outcomes) == 1,
        "unresolved outcome retained",
    )
    ledger.check(
        successor.non_selection_outcomes[0].outcome_kind
        is manifest_package.NonSelectionOutcomeKind.UNRESOLVED,
        "unresolved state remains explicit",
    )
    ledger.check(
        nested.integrated_selected_meaning_record.selected_candidate_ref
        == fixture.expected_selected_candidate_ref,
        "exact selected candidate retained",
    )
    ledger.check(
        nested.receipt.slice41d_selection_receipt_ref
        == fixture.expected_selection_receipt_ref,
        "exact Slice 41D authority receipt retained",
    )
    ledger.check(first.candidate_meanings_retained, "candidate custody retained")
    ledger.check(first.non_selection_outcomes_retained, "outcome custody retained")
    ledger.check(first.alternatives_preserved, "alternatives preserved")
    ledger.check(first.unresolved_state_preserved, "unresolved state preserved")
    ledger.check(first.slice40h_custody_preserved, "Slice 40H custody preserved")
    ledger.check(
        first.slice41d_construction_preserved,
        "Slice 41D construction preserved",
    )
    ledger.check(first.slice41e_integration_preserved, "Slice 41E custody preserved")

    rollback = first.rollback_metadata
    acceptance = first.acceptance_record
    ledger.check(package.validate_rollback_metadata(rollback).ok, "rollback valid")
    ledger.check(package.validate_acceptance_record(acceptance).ok, "acceptance valid")
    ledger.check(
        rollback.accepted_slice41e_head == package.SLICE41E_ACCEPTED_HEAD,
        "rollback metadata binds accepted Slice 41E",
    )
    ledger.check(acceptance.slice41_closed is True, "Slice 41 closed")
    ledger.check(acceptance.slice42_started is False, "Slice 42 not started")
    ledger.check(acceptance.stop_after_slice41 is True, "stop after Slice 41")
    ledger.check(
        acceptance.selected_meaning_bounded_semantic_custody_only is True,
        "acceptance bounds selected meaning to semantic custody",
    )
    ledger.check(acceptance.alternatives_preserved is True, "accept alternatives")
    ledger.check(
        acceptance.unresolved_state_preserved is True,
        "accept unresolved state",
    )
    ledger.check(
        acceptance.runtime_self_grants_acceptance is False,
        "runtime cannot self-accept",
    )
    ledger.check(acceptance.production_ready is False, "not production readiness")

    prohibited_result_fields = (
        "slice42_started",
        "truth_determined",
        "evidence_validated",
        "permission_granted",
        "execution_authorized",
        "outward_expression_authorized",
        "governed_outward_meaning_created",
        "expression_link_created",
        "validation_link_created",
        "delivery_link_created",
        "capability_availability_created",
        "route_created",
        "api_created",
        "network_accessed",
        "filesystem_read_performed",
        "filesystem_write_performed",
        "memory_read_performed",
        "memory_write_performed",
        "tool_invoked",
        "action_performed",
        "rendered",
        "delivered",
        "language_model_used",
        "embedding_used",
        "vector_used",
        "rag_used",
        "semantic_similarity_used",
    )
    for field in prohibited_result_fields:
        ledger.check(getattr(first, field) is False, f"prohibited result false: {field}")

    for frozen_record, field in (
        (enabled_state, "enabled"),
        (fixture, "accepted_fixture"),
        (invocation, "requested_operation"),
        (first, "status"),
        (acceptance, "slice41_closed"),
        (rollback, "repository_mutated"),
    ):
        try:
            setattr(frozen_record, field, None)
        except (FrozenInstanceError, AttributeError, TypeError):
            ledger.check(True, f"frozen record {type(frozen_record).__name__}")
        else:
            ledger.check(False, f"mutable record {type(frozen_record).__name__}")

    bad_values = (None, 0, True, "bad", [], {}, object())
    for validator in package.PUBLIC_VALIDATORS:
        for bad in bad_values:
            ledger.malformed(
                validator(bad).ok is False,
                f"malformed {validator.__name__}:{type(bad).__name__}",
            )

    tampered_records = (
        (package.validate_state, replace(enabled_state, state_id="wrong")),
        (package.validate_state, replace(enabled_state, route_allowed=True)),
        (package.validate_state, replace(enabled_state, enabled=False)),
        (package.validate_fixture, replace(fixture, fixture_id="wrong")),
        (package.validate_fixture, replace(fixture, accepted_fixture=False)),
        (
            package.validate_fixture,
            replace(fixture, expected_source_candidate_count=3),
        ),
        (package.validate_invocation, replace(invocation, invocation_id="wrong")),
        (package.validate_invocation, replace(invocation, fixture_id="wrong")),
        (
            package.validate_invocation,
            replace(invocation, requested_operation="wrong"),
        ),
        (
            package.validate_invocation,
            replace(invocation, arbitrary_input_carried=True),
        ),
        (
            package.validate_stage_receipt,
            replace(first.stage_receipts[0], receipt_id="wrong"),
        ),
        (
            package.validate_stage_receipt,
            replace(first.stage_receipts[0], stage_digest="0" * 64),
        ),
        (
            package.validate_stage_receipt,
            replace(first.stage_receipts[0], route_created=True),
        ),
        (
            package.validate_rollback_metadata,
            replace(rollback, accepted_slice41e_head="wrong"),
        ),
        (
            package.validate_rollback_metadata,
            replace(rollback, repository_mutated=True),
        ),
        (
            package.validate_acceptance_record,
            replace(acceptance, record_id="wrong"),
        ),
        (
            package.validate_acceptance_record,
            replace(acceptance, slice42_started=True),
        ),
        (
            package.validate_acceptance_record,
            replace(acceptance, outward_expression_authority=True),
        ),
        (
            package.validate_acceptance_record,
            replace(acceptance, runtime_self_grants_acceptance=True),
        ),
        (package.validate_result, replace(first, result_id="wrong")),
        (
            package.validate_result,
            replace(first, deterministic_repeat_digest="0" * 64),
        ),
        (package.validate_result, replace(first, stage_receipt_count=5)),
        (package.validate_result, replace(first, alternatives_preserved=False)),
        (package.validate_result, replace(first, truth_determined=True)),
        (package.validate_result, replace(first, slice42_started=True)),
        (
            package.validate_result,
            replace(
                first,
                integration_result=replace(nested, result_id="wrong"),
            ),
        ),
    )
    for validator, tampered in tampered_records:
        ledger.malformed(
            validator(tampered).ok is False,
            f"tampered {validator.__name__}:{type(tampered).__name__}",
        )

    for bad_state in ("bad", 0, True, object()):
        rejected = package.run_disabled_selected_meaning_closeout(
            invocation,
            state=bad_state,
            integration_input=integration_input,
        )
        ledger.rejection(
            rejected.status is package.Slice41CloseoutStatus.HELD_INVALID_STATE,
            f"invalid state rejected:{type(bad_state).__name__}",
        )
    for bad_invocation in (None, "raw", {}, [], object()):
        rejected = package.run_disabled_selected_meaning_closeout(
            bad_invocation,
            state=enabled_state,
            integration_input=integration_input,
        )
        ledger.rejection(
            rejected.status
            is package.Slice41CloseoutStatus.HELD_INVALID_INVOCATION,
            f"invalid invocation rejected:{type(bad_invocation).__name__}",
        )
    wrong_fixture_invocation = replace(invocation, fixture_id="wrong")
    rejected = package.run_disabled_selected_meaning_closeout(
        wrong_fixture_invocation,
        state=enabled_state,
        integration_input=integration_input,
    )
    ledger.rejection(
        rejected.status
        is package.Slice41CloseoutStatus.HELD_FIXTURE_NOT_ACCEPTED,
        "wrong fixture reference rejected",
    )
    for bad_input in (None, "bad", {}, [], object()):
        rejected = package.run_disabled_selected_meaning_closeout(
            invocation,
            state=enabled_state,
            integration_input=bad_input,
        )
        ledger.rejection(
            rejected.status
            is package.Slice41CloseoutStatus.HELD_INVALID_PREDECESSOR_OUTPUT,
            f"invalid Slice 41E input rejected:{type(bad_input).__name__}",
        )
    for tampered_input in (
        replace(integration_input, integration_input_id="wrong"),
        replace(integration_input, outward_meaning_requested=True),
        replace(integration_input, bootstrap_integration_requested=True),
    ):
        rejected = package.run_disabled_selected_meaning_closeout(
            invocation,
            state=enabled_state,
            integration_input=tampered_input,
        )
        ledger.rejection(
            rejected.status
            is package.Slice41CloseoutStatus.HELD_INVALID_PREDECESSOR_OUTPUT,
            "tampered Slice 41E input rejected",
        )

    protected = parse_hash_manifest(
        repository
        / "scripts/AIWEB_SLICE41F_PROTECTED_PREDECESSOR_SHA256SUMS.txt",
        ledger,
    )
    ledger.check(len(protected) == 659, "protected predecessor count")
    for expected_hash, relative in protected:
        path = repository / relative
        ledger.check(path.is_file() and not path.is_symlink(), f"protected exists:{relative}")
        ledger.check(
            path.is_file() and sha256_file(path) == expected_hash,
            f"protected hash:{relative}",
        )

    payload_paths = tuple(
        line
        for line in (
            repository / "scripts/AIWEB_SLICE41F_EXACT_PAYLOAD_PATHS.txt"
        ).read_text(encoding="utf-8").splitlines()
        if line
    )
    ledger.check(len(payload_paths) == 15, "exact payload path count")
    ledger.check(len(payload_paths) == len(set(payload_paths)), "payload paths unique")
    ledger.check(tuple(sorted(payload_paths)) == payload_paths, "payload paths sorted")
    for relative in payload_paths:
        path = repository / relative
        ledger.check(path.is_file() and not path.is_symlink(), f"payload exists:{relative}")

    base_head = git(repository, "rev-parse", package.SLICE41E_ACCEPTED_HEAD)
    base_tree = git(repository, "rev-parse", package.SLICE41E_ACCEPTED_HEAD + "^{tree}")
    base_subject = git(
        repository,
        "show",
        "-s",
        "--format=%s",
        package.SLICE41E_ACCEPTED_HEAD,
    )
    ledger.check(
        base_head.returncode == 0
        and base_head.stdout.strip() == package.SLICE41E_ACCEPTED_HEAD,
        "accepted Slice 41E commit available",
    )
    ledger.check(
        base_tree.returncode == 0
        and base_tree.stdout.strip() == package.SLICE41E_ACCEPTED_TREE,
        "accepted Slice 41E tree available",
    )
    ledger.check(
        base_subject.returncode == 0
        and base_subject.stdout.strip() == package.SLICE41E_ACCEPTED_SUBJECT,
        "accepted Slice 41E subject available",
    )

    with tempfile.TemporaryDirectory(prefix="aiweb_slice41f_stage_proof_") as temporary:
        clone = Path(temporary) / "clone"
        cloned = run(
            [
                "git", "clone", "--quiet", "--shared", "--no-checkout",
                str(repository), str(clone),
            ]
        )
        ledger.check(cloned.returncode == 0, "stage proof clone")
        if cloned.returncode == 0:
            read_tree = git(clone, "read-tree", package.SLICE41E_ACCEPTED_HEAD)
            ledger.check(read_tree.returncode == 0, "stage proof parent index")
            for relative in payload_paths:
                source_path = repository / relative
                destination = clone / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, destination)
            added = git(clone, "add", "--", *payload_paths)
            ledger.check(added.returncode == 0, "exact path staging")
            staged = tuple(
                sorted(
                    line
                    for line in git(
                        clone,
                        "diff",
                        "--cached",
                        "--name-only",
                        package.SLICE41E_ACCEPTED_HEAD,
                    ).stdout.splitlines()
                    if line
                )
            )
            ledger.check(staged == tuple(sorted(payload_paths)), "exact staged containment")
            non_additions = git(
                clone,
                "diff",
                "--cached",
                "--name-only",
                "--diff-filter=MDCRTUXB",
                package.SLICE41E_ACCEPTED_HEAD,
            )
            ledger.check(
                non_additions.returncode == 0
                and not non_additions.stdout.strip(),
                "stage proof additions only",
            )

    with tempfile.TemporaryDirectory(prefix="aiweb_slice41f_recovery_") as temporary:
        clone = Path(temporary) / "recovery"
        cloned = run(
            [
                "git", "clone", "--quiet", "--shared", "--no-checkout",
                str(repository), str(clone),
            ]
        )
        ledger.check(cloned.returncode == 0, "recovery proof clone")
        if cloned.returncode == 0:
            recovery_ref = git(
                clone,
                "update-ref",
                "refs/heads/slice41f-recovery-proof",
                package.PRE_SLICE41_COMMIT,
            )
            ledger.check(recovery_ref.returncode == 0, "pre-Slice-41 recovery ref")
            head_ref = git(
                clone,
                "symbolic-ref",
                "HEAD",
                "refs/heads/slice41f-recovery-proof",
            )
            ledger.check(head_ref.returncode == 0, "pre-Slice-41 recovery HEAD")
            read_tree = git(clone, "read-tree", package.PRE_SLICE41_COMMIT)
            ledger.check(read_tree.returncode == 0, "pre-Slice-41 recovery index")
            ledger.check(
                git(clone, "rev-parse", "HEAD").stdout.strip()
                == package.PRE_SLICE41_COMMIT,
                "pre-Slice-41 recovery head",
            )
            ledger.check(
                git(clone, "write-tree").stdout.strip()
                == package.PRE_SLICE41_TREE,
                "pre-Slice-41 recovery tree",
            )
            ledger.check(
                git(clone, "show", "-s", "--format=%s", "HEAD").stdout.strip()
                == package.PRE_SLICE41_SUBJECT,
                "pre-Slice-41 recovery subject",
            )

    print("AI.WEB SLICE 41F DISABLED BOOTSTRAP INTEGRATION AND SLICE 41 CLOSEOUT TEST")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print(f"explicit_rejection_cases={ledger.explicit_rejections}")
    print("fixture_count=1")
    print("deterministic_repeat_count=3")
    print("integration_stage_count=6")
    print("protected_predecessor_files=659")
    print("exact_payload_paths=15")
    print("slice41a_through_41f_completed=1")
    print("exact_slice41e_integration_required=1")
    print("selected_meaning_bounded_semantic_custody_only=1")
    print("alternatives_preserved=1")
    print("unresolved_state_preserved=1")
    print("disabled_by_default=1")
    print("explicit_invocation_required=1")
    print("accepted_static_fixture_only=1")
    print("offline_in_memory_deterministic=1")
    print("final_slice41_acceptance_record_created=1")
    print("pre_slice41_tree_recovery=1")
    print("exact_staged_path_containment=1")
    print("slice42_started=0")
    print("truth_evidence_permission_execution_authority=0")
    print("outward_expression_authority=0")
    print("route_api_network_filesystem_memory_tool_action_rendering_delivery=0")
    print("language_model_embedding_vector_rag_similarity=0")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print("FAIL: " + failure)
    if ledger.failures:
        print("AI.WEB SLICE 41F BEHAVIOR TEST: FAIL")
        return 1
    print("AI.WEB SLICE 41F BEHAVIOR TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
