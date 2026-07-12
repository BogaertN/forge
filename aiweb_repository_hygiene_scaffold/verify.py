"""Read-only verifier for the AI.Web Slice 25 repository-hygiene scaffold."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Iterable

from .authority import (
    ACCEPTED_SCOPE_SENTENCE,
    EXPECTED_UNCHANGED_GIT_BLOBS,
    FORBIDDEN_ACTIVE_IMPORT_ROOTS,
    HISTORICAL_RECORD_CLASSIFICATION,
    HISTORICAL_RECORD_RELATIVE_PATH,
    HISTORICAL_RECORD_SHA256,
    STRUCTURAL_PROBE_CLASSIFICATION,
    STRUCTURAL_PROBE_RELATIVE_PATH,
    STRUCTURAL_PROBE_SHA256,
    MANAGED_PYTHON_ENVIRONMENT_DIR_NAMES,
    MODIFIED_EXISTING_FILES,
    NEW_SLICE25_FILES,
    PROHIBITED_MODIFIED_PATHS,
    REQUIRED_FORGE_BRANCH,
    REQUIRED_FORGE_REPO,
    SLICE25_HARD_BOUNDARY,
    SLICE25_PATCH_FILES,
    SOURCE_AUTHORITY_PACKET_SHA256,
    SOURCE_TREE_CACHE_DIRECTORIES,
)
from aiweb_full_regression_acceptance_bundle_scaffold.context import (
    scan_python_cache,
)


@dataclass(frozen=True)
class Slice25VerificationResult:
    passed: bool
    state: str
    checked_files: tuple[str, ...]
    failures: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "state": self.state,
            "checked_files": list(self.checked_files),
            "failures": list(self.failures),
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=env,
    )


def required_files_present(root: Path) -> tuple[str, ...]:
    return tuple(
        relative_path
        for relative_path in SLICE25_PATCH_FILES
        if not (root / relative_path).is_file()
    )


def syntax_failures(root: Path) -> tuple[str, ...]:
    failures: list[str] = []
    for relative_path in SLICE25_PATCH_FILES:
        path = root / relative_path
        if not path.is_file() or path.suffix != ".py":
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=relative_path)
        except (OSError, SyntaxError) as exc:
            failures.append(f"syntax_error:{relative_path}:{exc}")
    return tuple(failures)


def forbidden_import_failures(root: Path) -> tuple[str, ...]:
    failures: list[str] = []
    forbidden = set(FORBIDDEN_ACTIVE_IMPORT_ROOTS)

    for relative_path in SLICE25_PATCH_FILES:
        path = root / relative_path
        if not path.is_file() or path.suffix != ".py":
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative_path)
        except (OSError, SyntaxError) as exc:
            failures.append(f"import_scan_error:{relative_path}:{exc}")
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_name = alias.name.split(".", 1)[0]
                    if root_name in forbidden:
                        failures.append(
                            f"forbidden_import:{relative_path}:{alias.name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                root_name = module.split(".", 1)[0]
                if root_name in forbidden:
                    failures.append(
                        f"forbidden_import:{relative_path}:{module}"
                    )

    return tuple(failures)


def cache_policy_probe() -> tuple[str, ...]:
    """Exercise managed-environment exclusion and source-cache detection."""

    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="slice25_cache_policy_") as temp_name:
        root = Path(temp_name)

        for environment_name in MANAGED_PYTHON_ENVIRONMENT_DIR_NAMES:
            managed_cache = (
                root
                / environment_name
                / "lib"
                / "python3.12"
                / "site-packages"
                / "sample"
                / "__pycache__"
            )
            managed_cache.mkdir(parents=True)
            (managed_cache / "sample.cpython-312.pyc").write_bytes(
                b"managed-environment-bytecode"
            )

        before = tuple(
            sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
        )
        managed_hits = scan_python_cache(root)
        after = tuple(
            sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
        )

        if managed_hits:
            failures.append(
                "managed_environment_cache_was_reported:"
                + "|".join(managed_hits)
            )
        if before != after:
            failures.append("cache_scan_modified_managed_probe")

        source_cache = root / "source_package" / "__pycache__"
        source_cache.mkdir(parents=True)
        cached_module = source_cache / "module.cpython-312.pyc"
        cached_module.write_bytes(b"source-bytecode")
        source_pyc = root / "source_package" / "loose.pyc"
        source_pyc.write_bytes(b"loose-source-bytecode")
        source_pyo = root / "source_package" / "legacy.pyo"
        source_pyo.write_bytes(b"optimized-source-bytecode")

        expected = tuple(
            sorted((str(source_cache), str(source_pyc), str(source_pyo)))
        )
        before_source = tuple(
            sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
        )
        source_hits = scan_python_cache(root)
        after_source = tuple(
            sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
        )

        if source_hits != expected:
            failures.append(
                "source_cache_detection_mismatch:"
                f"expected={expected}:actual={source_hits}"
            )
        if before_source != after_source:
            failures.append("cache_scan_modified_source_probe")

    return tuple(failures)


def _parse_status_z(raw: str) -> tuple[tuple[str, str], ...]:
    records = raw.split("\0")
    parsed: list[tuple[str, str]] = []
    index = 0

    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if len(record) < 4:
            parsed.append(("!!", record))
            continue

        status = record[:2]
        path = record[3:]
        parsed.append((status, path))

        if status[0] in {"R", "C"} or status[1] in {"R", "C"}:
            if index < len(records) and records[index]:
                parsed.append(("!!", records[index]))
                index += 1

    return tuple(parsed)


def git_status_failures(root: Path, state: str) -> tuple[str, ...]:
    result = _run_git(
        root,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
    )
    if result.returncode != 0:
        return (
            f"git_status_failed:{result.returncode}:{result.stderr.strip()}",
        )

    records = _parse_status_z(result.stdout)
    if state == "committed":
        if records:
            return tuple(
                f"committed_state_not_clean:{status}:{path}"
                for status, path in records
            )
        return ()

    if state != "applied":
        return ()

    failures: list[str] = []
    expected_paths = set(SLICE25_PATCH_FILES)
    observed_paths = {path for _, path in records}

    for status, path in records:
        if status == "!!":
            failures.append(f"unparseable_git_status_record:{path}")
            continue
        if status[0] not in {" ", "?"}:
            failures.append(f"staged_change_not_allowed:{status}:{path}")
        if path not in expected_paths:
            failures.append(f"unexpected_git_status_path:{status}:{path}")

    for missing in sorted(expected_paths - observed_paths):
        failures.append(f"expected_slice25_status_path_missing:{missing}")

    return tuple(failures)


def protected_blob_failures(root: Path) -> tuple[str, ...]:
    failures: list[str] = []

    for relative_path, expected_blob in EXPECTED_UNCHANGED_GIT_BLOBS.items():
        path = root / relative_path
        if not path.is_file():
            failures.append(f"protected_file_missing:{relative_path}")
            continue

        result = _run_git(root, "hash-object", "--no-filters", relative_path)
        if result.returncode != 0:
            failures.append(
                f"protected_blob_hash_failed:{relative_path}:"
                f"{result.returncode}:{result.stderr.strip()}"
            )
            continue

        actual_blob = result.stdout.strip()
        if actual_blob != expected_blob:
            failures.append(
                f"protected_blob_changed:{relative_path}:"
                f"expected={expected_blob}:actual={actual_blob}"
            )

    return tuple(failures)


def disposition_failures(root: Path, state: str) -> tuple[str, ...]:
    if state not in {"applied", "committed"}:
        return ()

    failures: list[str] = []
    historical_path = root / HISTORICAL_RECORD_RELATIVE_PATH
    if historical_path.exists():
        failures.append(
            f"historical_record_still_in_active_path:{HISTORICAL_RECORD_RELATIVE_PATH}"
        )

    structural_probe = root / STRUCTURAL_PROBE_RELATIVE_PATH
    if structural_probe.exists():
        failures.append(
            f"structural_probe_still_in_live_repository:{STRUCTURAL_PROBE_RELATIVE_PATH}"
        )
    structural_probe_parent = structural_probe.parent
    if structural_probe_parent.exists():
        failures.append(
            "structural_probe_parent_still_in_live_repository:"
            f"{structural_probe_parent.relative_to(root).as_posix()}"
        )

    for relative_path in SOURCE_TREE_CACHE_DIRECTORIES:
        if (root / relative_path).exists():
            failures.append(f"source_cache_directory_still_present:{relative_path}")

    cache_hits = scan_python_cache(root)
    for hit in cache_hits:
        failures.append(f"source_tree_cache_hit:{hit}")

    return tuple(failures)


def authority_constant_failures() -> tuple[str, ...]:
    failures: list[str] = []
    if len(SOURCE_AUTHORITY_PACKET_SHA256) != 64:
        failures.append("source_packet_sha256_not_64_characters")
    if len(HISTORICAL_RECORD_SHA256) != 64:
        failures.append("historical_record_sha256_not_64_characters")
    if len(STRUCTURAL_PROBE_SHA256) != 64:
        failures.append("structural_probe_sha256_not_64_characters")
    if "historical_planning_evidence" not in HISTORICAL_RECORD_CLASSIFICATION:
        failures.append("historical_record_classification_not_explicit")
    if "test_generated" not in STRUCTURAL_PROBE_CLASSIFICATION:
        failures.append("structural_probe_classification_not_explicit")
    if len(MODIFIED_EXISTING_FILES) != 5:
        failures.append("modified_existing_file_count_not_5")
    if len(NEW_SLICE25_FILES) != 6:
        failures.append("new_slice25_file_count_not_6")
    if len(SLICE25_PATCH_FILES) != 11:
        failures.append("slice25_patch_file_count_not_11")
    if set(MODIFIED_EXISTING_FILES) & set(NEW_SLICE25_FILES):
        failures.append("modified_and_new_file_sets_overlap")
    if tuple(MODIFIED_EXISTING_FILES) + tuple(NEW_SLICE25_FILES) != tuple(
        SLICE25_PATCH_FILES
    ):
        failures.append("slice25_patch_file_order_or_content_mismatch")
    if "main.py" not in PROHIBITED_MODIFIED_PATHS:
        failures.append("main_py_not_protected")
    if ".gitignore" not in PROHIBITED_MODIFIED_PATHS:
        failures.append("gitignore_not_protected")
    if "no_github_push" not in SLICE25_HARD_BOUNDARY:
        failures.append("hard_boundary_missing_no_github_push")
    if "no_language_runtime_authority" not in SLICE25_HARD_BOUNDARY:
        failures.append("hard_boundary_missing_no_language_runtime_authority")
    if "evidence-preserving" not in ACCEPTED_SCOPE_SENTENCE:
        failures.append("accepted_scope_sentence_missing_evidence_boundary")
    return tuple(failures)


def verify_slice25_boundary(
    root: str | Path,
    *,
    state: str = "structure",
    require_live_repo_identity: bool = False,
    check_protected_files: bool = False,
) -> Slice25VerificationResult:
    root = Path(root).resolve()
    failures: list[str] = []

    if state not in {"structure", "applied", "committed"}:
        failures.append(f"unsupported_state:{state}")

    if not root.is_dir():
        failures.append(f"repository_missing:{root}")
        return Slice25VerificationResult(
            False,
            state,
            tuple(SLICE25_PATCH_FILES),
            tuple(failures),
        )

    if require_live_repo_identity:
        if str(root) != REQUIRED_FORGE_REPO:
            failures.append(
                f"repository_path_mismatch:expected={REQUIRED_FORGE_REPO}:actual={root}"
            )
        top = _run_git(root, "rev-parse", "--show-toplevel")
        branch = _run_git(root, "branch", "--show-current")
        if top.returncode != 0 or top.stdout.strip() != str(root):
            failures.append("git_top_level_mismatch")
        if branch.returncode != 0 or branch.stdout.strip() != REQUIRED_FORGE_BRANCH:
            failures.append("git_branch_not_main")

    for relative_path in required_files_present(root):
        failures.append(f"required_file_missing:{relative_path}")

    failures.extend(syntax_failures(root))
    failures.extend(forbidden_import_failures(root))
    failures.extend(cache_policy_probe())
    failures.extend(authority_constant_failures())

    if check_protected_files:
        failures.extend(protected_blob_failures(root))

    if state in {"applied", "committed"}:
        failures.extend(git_status_failures(root, state))
        failures.extend(disposition_failures(root, state))

    return Slice25VerificationResult(
        not failures,
        state,
        tuple(SLICE25_PATCH_FILES),
        tuple(failures),
    )
