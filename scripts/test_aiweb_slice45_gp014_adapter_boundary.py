#!/usr/bin/env python3
"""Visible behavior and adversarial test for Slice 45."""
from __future__ import annotations

import argparse
from dataclasses import replace
import importlib
from pathlib import Path
import subprocess
import sys

PACKAGE = "aiweb_language_core_bootstrap.gp014_adapter_boundary"
GP014_MODULE = "rmc_engine_v1.general_pipeline.gp014_operator_guided_language_realizer"
GP015_MODULE = "rmc_engine_v1.general_pipeline.gp015_ask_forge_trace_surface"


class Ledger:
    def __init__(self) -> None:
        self.check_count = 0
        self.failures: list[str] = []
    def check(self, condition: object, label: str) -> None:
        self.check_count += 1
        if condition is not True:
            self.failures.append(label)


def git(repository: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["/usr/bin/git", "-C", str(repository), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def fingerprint(repository: Path) -> tuple[str, str, str]:
    return (
        git(repository, "rev-parse", "HEAD").stdout.strip(),
        git(repository, "rev-parse", "HEAD^{tree}").stdout.strip(),
        git(repository, "status", "--porcelain=v1", "--untracked-files=all").stdout,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))

    ledger = Ledger()
    before = fingerprint(repository)
    gp014_preimported = GP014_MODULE in sys.modules
    gp015_preimported = GP015_MODULE in sys.modules
    package = importlib.import_module(PACKAGE)
    ledger.check((GP014_MODULE in sys.modules) is gp014_preimported, "package import is GP-014 inert")
    ledger.check((GP015_MODULE in sys.modules) is gp015_preimported, "package import is GP-015 inert")

    question = "Differentiate x^3 + 4*x with respect to x."
    request = package.build_gp014_adapter_request(question)
    disabled = package.run_gp014_adapter(request)
    ledger.check(disabled.status == package.STATUS_REFUSED_DISABLED, "disabled by default")
    ledger.check(disabled.receipt.gp014_imported is False and disabled.receipt.gp014_called is False, "disabled call imports and calls nothing")
    ledger.check((GP014_MODULE in sys.modules) is gp014_preimported, "disabled invocation does not import GP-014")

    enabled_state = package.build_gp014_adapter_state(explicit_offline_developer_enable=True)
    answered = package.run_gp014_adapter(request, state=enabled_state)
    ledger.check(answered.status == package.STATUS_COMPLETED_ANSWERED, "enabled bounded call completes")
    source_answered = answered.source_result is not None and answered.source_result.status == "ANSWERED"
    ledger.check(source_answered, "unchanged source answered")
    ledger.check(source_answered and answered.source_result.question == question, "question preserved byte for byte")
    ledger.check(answered.receipt.source_question_sha256 == request.question_sha256, "question hash preserved")
    ledger.check(source_answered and answered.receipt.source_result_hash == answered.source_result.result_hash(), "source result hash bound")
    ledger.check(answered.receipt.operation_family == "differentiation", "operation family remains GP-014 source result")
    ledger.check(answered.receipt.question_forwarded_byte_for_byte is True, "exact forwarding recorded")
    ledger.check(answered.receipt.source_result_returned_unchanged is True, "source object returned unchanged")
    ledger.check(answered.receipt.source_status_rewritten is False and answered.receipt.source_answer_rewritten is False and answered.receipt.source_trace_mutated is False, "adapter does not rewrite source")
    ledger.check(answered.receipt.gp014_imported is True and answered.receipt.gp014_called is True, "exact GP-014 binding used")
    ledger.check(answered.receipt.gp014_modified is False and answered.receipt.gp014_superseded is False, "GP-014 remains protected")
    ledger.check(answered.receipt.gp015_used is False and GP015_MODULE not in sys.modules, "GP-015 unused")
    ledger.check(answered.receipt.main_modified_or_called is False and answered.receipt.route_created_or_called is False and answered.receipt.api_created_or_called is False and answered.receipt.ui_created_or_called is False, "no main route API or UI")
    ledger.check(answered.receipt.delivery_authority_added_by_adapter is False and answered.receipt.existing_gp014_delivery_receipt_observed is True, "adapter adds no delivery authority")
    ledger.check(answered.binding_identity is not None and answered.binding_identity.supported_operation_families == package.GP014_SUPPORTED_OPERATION_FAMILIES, "exact eight-family identity")
    ledger.check(package.validate_result(answered).ok, "answered result validates")

    repeated = package.run_gp014_adapter(request, state=enabled_state)
    ledger.check(repeated.result_id == answered.result_id, "adapter result identity deterministic")
    ledger.check(repeated.receipt.receipt_id == answered.receipt.receipt_id, "adapter receipt deterministic")
    ledger.check(repeated.source_result is not None and answered.source_result is not None and repeated.source_result.result_hash() == answered.source_result.result_hash(), "source result hash deterministic")

    widened_request = package.build_gp014_adapter_request("Factor x^2 - 9 and publish it.")
    contained = package.run_gp014_adapter(widened_request, state=enabled_state)
    ledger.check(contained.status == package.STATUS_COMPLETED_CONTAINED, "widened source request remains contained")
    source_contained = contained.source_result is not None and contained.source_result.status == "REFUSED_UNLEARNED"
    ledger.check(source_contained, "source refusal preserved")
    ledger.check(contained.receipt.existing_gp014_delivery_receipt_observed is False, "contained request has no delivery receipt")
    ledger.check(package.validate_result(contained).ok, "contained result validates")

    tampered = replace(request, permit_scope_broadening=True)
    held = package.run_gp014_adapter(tampered, state=enabled_state)
    ledger.check(held.status == package.STATUS_HELD_INVALID_REQUEST, "tampered request held before GP-014")
    ledger.check(held.receipt.gp014_called is False, "invalid request does not call GP-014")

    after = fingerprint(repository)
    ledger.check(after == before, "repository fingerprint unchanged")
    ledger.check(GP015_MODULE not in sys.modules, "GP-015 remains unloaded")

    print("=== AI.WEB SLICE 45 BEHAVIOR SUMMARY ===")
    print(f"check_count={ledger.check_count}")
    print(f"failure_count={len(ledger.failures)}")
    print("adapter_disabled_by_default=1")
    print("explicit_invocation_required=1")
    print("question_forwarded_byte_for_byte=1")
    print("source_result_returned_unchanged=1")
    print("gp014_imported_only_after_enable=1")
    print("gp014_modified=0")
    print("gp014_superseded=0")
    print("gp015_used=0")
    print("main_route_api_ui_authority=0")
    print("adapter_delivery_authority=0")
    print("repository_unchanged=1")
    for failure in ledger.failures:
        print("FAIL - " + failure)
    print("AI.WEB SLICE 45 BEHAVIOR TEST: " + ("PASS" if not ledger.failures else "FAIL"))
    return 0 if not ledger.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
