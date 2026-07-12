#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Iterable, Tuple

EXPECTED_SLICE18_PATHS = (
    "aiweb_gp014_preservation_decision_scaffold/__init__.py",
    "aiweb_gp014_preservation_decision_scaffold/core.py",
    "aiweb_gp014_preservation_decision_scaffold/gp014_reference.py",
    "aiweb_gp014_preservation_decision_scaffold/wrapper_decision.py",
    "aiweb_gp014_preservation_decision_scaffold/preservation_receipt.py",
    "aiweb_gp014_preservation_decision_scaffold/verify.py",
    "scripts/README_aiweb_slice18_gp014_preservation_decision_scaffold.md",
    "scripts/aiweb_slice18_gp014_preservation_decision_verify.py",
    "scripts/test_aiweb_slice18_gp014_preservation_decision_scaffold.py",
)


def _load_verify_module(path: Path):
    spec = importlib.util.spec_from_file_location("slice18_verify_under_test", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load verifier module from " + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _slice18_name_status(paths: Iterable[str] = EXPECTED_SLICE18_PATHS) -> Tuple[str, ...]:
    return tuple("A\t" + path for path in paths)


def _expect_pass(label: str, module, context) -> None:
    context_label, passes, failures = module.classify_repository_context(context)
    print(label + " context_label=" + context_label)
    if failures:
        print(label + " FAIL")
        for item in failures:
            print(" - " + item)
        raise SystemExit(1)
    print(label + " PASS")


def _expect_fail(label: str, module, context) -> None:
    context_label, passes, failures = module.classify_repository_context(context)
    print(label + " context_label=" + context_label)
    if not failures:
        print(label + " FAIL: expected failures but got none")
        raise SystemExit(1)
    print(label + " PASS expected failure count=" + str(len(failures)))


def main() -> int:
    if len(sys.argv) == 2:
        candidate = Path(sys.argv[1]).resolve()
        if candidate.is_dir():
            verify_script = candidate / "scripts" / "aiweb_slice18_gp014_preservation_decision_verify.py"
        else:
            verify_script = candidate
    else:
        verify_script = Path(__file__).with_name("aiweb_slice18_gp014_preservation_decision_verify.py").resolve()

    module = _load_verify_module(verify_script)
    Context = module.RepositoryContext

    precommit_staged = Context(
        head=module.EXPECTED_BASE_HEAD,
        parent=module.EXPECTED_BASE_PARENT,
        subject=module.EXPECTED_BASE_SUBJECT,
        status_lines=tuple("A  " + path for path in EXPECTED_SLICE18_PATHS),
        slice18_is_ancestor=False,
        slice18_parent="",
        slice18_subject="",
        slice18_name_status_lines=(),
    )
    _expect_pass("precommit_staged", module, precommit_staged)

    precommit_untracked_dir = Context(
        head=module.EXPECTED_BASE_HEAD,
        parent=module.EXPECTED_BASE_PARENT,
        subject=module.EXPECTED_BASE_SUBJECT,
        status_lines=("?? aiweb_gp014_preservation_decision_scaffold/",),
        slice18_is_ancestor=False,
        slice18_parent="",
        slice18_subject="",
        slice18_name_status_lines=(),
    )
    _expect_pass("precommit_untracked_directory", module, precommit_untracked_dir)

    postcommit_clean = Context(
        head=module.EXPECTED_SLICE18_HEAD,
        parent=module.EXPECTED_SLICE18_PARENT,
        subject=module.EXPECTED_SLICE18_SUBJECT,
        status_lines=(),
        slice18_is_ancestor=True,
        slice18_parent=module.EXPECTED_SLICE18_PARENT,
        slice18_subject=module.EXPECTED_SLICE18_SUBJECT,
        slice18_name_status_lines=_slice18_name_status(),
    )
    _expect_pass("postcommit_clean", module, postcommit_clean)

    descendant_clean = Context(
        head="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        parent=module.EXPECTED_SLICE18_HEAD,
        subject="Slice 18R1 verifier context correction",
        status_lines=(),
        slice18_is_ancestor=True,
        slice18_parent=module.EXPECTED_SLICE18_PARENT,
        slice18_subject=module.EXPECTED_SLICE18_SUBJECT,
        slice18_name_status_lines=_slice18_name_status(),
    )
    _expect_pass("descendant_clean", module, descendant_clean)

    dirty_postcommit = Context(
        head=module.EXPECTED_SLICE18_HEAD,
        parent=module.EXPECTED_SLICE18_PARENT,
        subject=module.EXPECTED_SLICE18_SUBJECT,
        status_lines=(" M rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py",),
        slice18_is_ancestor=True,
        slice18_parent=module.EXPECTED_SLICE18_PARENT,
        slice18_subject=module.EXPECTED_SLICE18_SUBJECT,
        slice18_name_status_lines=_slice18_name_status(),
    )
    _expect_fail("dirty_postcommit", module, dirty_postcommit)

    bad_slice18_commit_paths = Context(
        head=module.EXPECTED_SLICE18_HEAD,
        parent=module.EXPECTED_SLICE18_PARENT,
        subject=module.EXPECTED_SLICE18_SUBJECT,
        status_lines=(),
        slice18_is_ancestor=True,
        slice18_parent=module.EXPECTED_SLICE18_PARENT,
        slice18_subject=module.EXPECTED_SLICE18_SUBJECT,
        slice18_name_status_lines=_slice18_name_status(paths=EXPECTED_SLICE18_PATHS[:-1]),
    )
    _expect_fail("bad_slice18_commit_paths", module, bad_slice18_commit_paths)

    print("SLICE18_VERIFY_CONTEXT_TEST=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
