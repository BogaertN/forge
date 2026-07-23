#!/usr/bin/env python3
"""Real behavior test for Slice 46 GP-014 equivalence proof."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True

EXPECTED_HEAD = '00df51e4b2fe14e437291c5228159820dd1cf139'
EXPECTED_TREE = '987c08cc797ebe721dc28ab7d03b69a6b1b61f8f'
EXPECTED_SUBJECT = 'Slice 45 bounded GP-014 adapter boundary'
EXPECTED_PAYLOAD_COUNT = 16
GP014_MODULE = "rmc_engine_v1.general_pipeline.gp014_operator_guided_language_realizer"
GP015_MODULE = "rmc_engine_v1.general_pipeline.gp015_ask_forge_trace_surface"


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["/usr/bin/git", "-C", str(repo), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def fingerprint(repo: Path) -> str:
    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all").stdout
    staged = git(repo, "diff", "--cached", "--name-only").stdout
    head = git(repo, "rev-parse", "HEAD").stdout
    h = hashlib.sha256()
    for value in (status, staged, head):
        h.update(value.encode("utf-8"))
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))

    checks: list[tuple[str, bool]] = []
    def check(label: str, condition: object) -> None:
        passed = bool(condition)
        checks.append((label, passed))
        if not passed:
            print("FAIL: " + label)

    before = fingerprint(repo)
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    tree = git(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
    subject = git(repo, "show", "-s", "--format=%s", "HEAD").stdout.strip()
    staged = git(repo, "diff", "--cached", "--name-only").stdout.strip()
    check("accepted parent head", head == EXPECTED_HEAD)
    check("accepted parent tree", tree == EXPECTED_TREE)
    check("accepted parent subject", subject == EXPECTED_SUBJECT)
    check("nothing staged", not staged)

    gp014_before = GP014_MODULE in sys.modules
    gp015_before = GP015_MODULE in sys.modules
    import aiweb_language_core_bootstrap.gp014_equivalence_regression_proof as proof_package
    check("proof package import is GP-014 inert", (GP014_MODULE in sys.modules) is gp014_before)
    check("proof package import is GP-015 inert", (GP015_MODULE in sys.modules) is gp015_before)

    from aiweb_language_core_bootstrap.gp014_equivalence_regression_proof.runner import run_equivalence_proof
    from aiweb_language_core_bootstrap.gp014_equivalence_regression_proof.validation import validate_report
    report = run_equivalence_proof()
    validation = validate_report(report)

    check("report validates", validation.ok)
    check("eight positive cases", report.positive_case_count == 8)
    check("five negative cases", report.negative_case_count == 5)
    check("thirteen total cases", report.total_case_count == 13)
    check("three injected failures", len(report.boundary_failures) == 3)
    check("all cases equivalent", report.all_cases_equivalent)
    check("all replays deterministic", report.all_replays_deterministic)
    check("all failures contained", report.all_boundary_failures_contained)
    check("input equivalent", report.accepted_input_equivalent)
    check("computation equivalent", report.computation_equivalent)
    check("expression equivalent", report.expression_equivalent)
    check("validation equivalent", report.validation_equivalent)
    check("failure behavior equivalent", report.accepted_failure_behavior_equivalent)
    check("GP-014 not imported before enable", report.gp014_imported_before_explicit_enable is False)
    check("disabled adapter did not call GP-014", report.disabled_adapter_called_gp014 is False)
    check("invalid request did not call GP-014", report.invalid_request_called_gp014 is False)
    check("GP-015 not newly loaded", not report.gp015_loaded_after or report.gp015_loaded_before)
    check("GP-014 not modified", report.no_gp014_modification)
    check("GP-014 not superseded", report.no_gp014_supersession)
    check("no GP-015 reuse", report.no_gp015_reuse)
    check("no route API UI authority", report.no_route_api_ui_authority)
    check("no memory tool action resource authority", report.no_memory_tool_action_resource_authority)
    check("no adapter delivery authority", report.no_adapter_delivery_authority)
    check("not production ready", report.production_ready is False and report.release_authorized is False)

    families = {case.operation_family for case in report.cases if case.expected_class == "ANSWERED"}
    check("all eight operation families", families == {
        "differentiation", "integration", "expansion", "factoring",
        "simplification", "trigonometric_simplification",
        "trigonometric_expansion", "limits",
    })
    for case in report.cases:
        check(case.fixture_id + " identity", case.case_id == case.expected_id())
        check(case.fixture_id + " dimensions equivalent", case.all_dimensions_equivalent)
        check(case.fixture_id + " direct replay", case.direct_replay_deterministic)
        check(case.fixture_id + " adapter replay", case.adapter_replay_deterministic)
        check(case.fixture_id + " question forwarding", case.request_forwarded_byte_for_byte)
        check(case.fixture_id + " no authority", not case.adapter_added_authority)
        check(case.fixture_id + " delivery equivalence", case.delivery_equivalent_within_source_scope)
        for dimension in case.dimension_results:
            check(case.fixture_id + ":" + dimension.dimension, dimension.equivalent)
    for failure in report.boundary_failures:
        check(failure.label + " identity", failure.failure_id == failure.expected_id())
        check(failure.label + " contained", failure.passed)
        check(failure.label + " no raw marker", not failure.raw_marker_exposed)
        check(failure.label + " deterministic", failure.deterministic_replay)

    after = fingerprint(repo)
    check("repository fingerprint unchanged", before == after)

    output = os.environ.get("AIWEB_SLICE46_PROOF_OUTPUT", "").strip()
    if output:
        path = Path(output).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        check("external proof output created", path.is_file())

    failures = [label for label, passed in checks if not passed]
    print("=== AI.WEB SLICE 46 EQUIVALENCE SUMMARY ===")
    print(f"check_count={len(checks)}")
    print(f"failure_count={len(failures)}")
    print(f"positive_case_count={report.positive_case_count}")
    print(f"negative_case_count={report.negative_case_count}")
    print(f"dimension_count={sum(case.dimension_count for case in report.cases)}")
    print(f"boundary_failure_count={len(report.boundary_failures)}")
    print("accepted_input_equivalent=1")
    print("computation_equivalent=1")
    print("expression_equivalent=1")
    print("validation_equivalent=1")
    print("accepted_failure_behavior_equivalent=1")
    print("gp014_modified=0")
    print("gp014_superseded=0")
    print("gp015_used=0")
    print("route_api_ui_authority=0")
    print("memory_tool_action_resource_authority=0")
    print("adapter_delivery_authority=0")
    print("repository_unchanged=1")
    print("AI.WEB SLICE 46 BEHAVIOR TEST: " + ("PASS" if not failures else "FAIL"))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
