from __future__ import annotations

from dataclasses import replace
import ast
from pathlib import Path
import subprocess
from typing import List, Tuple

from .core import (
    BASE_HEAD,
    FALSE_ONLY_AUTHORITY_FIELDS,
    FORBIDDEN_IMPORT_PREFIXES,
    FORBIDDEN_IMPORT_ROOTS,
    GP014_PROTECTED_PATH_HASHES,
    GP015_PROTECTED_PATH_HASHES,
    RELATED_RENDERER_EVIDENCE_PATHS,
    REQUIRED_DECISION_LAWS,
    gp014_decision_scope_record,
    sha256_file,
)
from .gp014_reference import (
    build_gp014_reference_record,
    validate_gp014_reference_record,
    verify_gp014_reference_hashes,
)
from .preservation_receipt import (
    build_gp014_preservation_receipt_record,
    validate_gp014_preservation_receipt_record,
)
from .wrapper_decision import (
    build_gp014_wrapper_decision_record,
    validate_gp014_wrapper_decision_record,
)

PACKAGE_PATHS = (
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

_ALLOWED_STATUS_PATHS = frozenset(PACKAGE_PATHS)
_ALLOWED_STATUS_DIRS = frozenset({"aiweb_gp014_preservation_decision_scaffold"})


def _status_path(line: str) -> str:
    cleaned = line[3:] if len(line) > 3 else line
    if " -> " in cleaned:
        cleaned = cleaned.split(" -> ", 1)[1]
    return cleaned.strip()


def _git(repo: Path, *args: str) -> Tuple[int, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except FileNotFoundError:
        return 127, "GIT_NOT_FOUND"
    return result.returncode, result.stdout.rstrip("\n")


def _git_status_lines(repo: Path) -> List[str]:
    code, output = _git(repo, "status", "--short")
    if code != 0:
        return [output or "GIT_STATUS_FAILED"]
    lines: List[str] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        path = _status_path(line)
        if "__pycache__/" in path or path.endswith((".pyc", ".pyo")):
            continue
        lines.append(line)
    return lines


def git_status_limited_to_slice18(repo: Path) -> bool:
    for line in _git_status_lines(repo):
        path = _status_path(line)
        if path in _ALLOWED_STATUS_PATHS:
            continue
        if path.rstrip("/") in _ALLOWED_STATUS_DIRS:
            continue
        return False
    return True


def _path_status_is_clean(repo: Path, rel_path: str) -> bool:
    for line in _git_status_lines(repo):
        if _status_path(line) == rel_path:
            return False
    return True


def _active_import_names(path: Path) -> List[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def _is_forbidden_import(name: str) -> bool:
    root = name.split(".")[0]
    if root in FORBIDDEN_IMPORT_ROOTS:
        return True
    return any(name == prefix or name.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES)


def _protected_hashes_match(repo: Path, path_hashes: Tuple[Tuple[str, str], ...]) -> bool:
    for rel_path, expected in path_hashes:
        target = repo / rel_path
        if not target.is_file():
            return False
        if sha256_file(target) != expected:
            return False
    return True


def run_verification(repo: Path) -> Tuple[List[str], List[str]]:
    passes: List[str] = []
    failures: List[str] = []

    def check(label: str, condition: bool) -> None:
        (passes if condition else failures).append(label)

    repo = Path(repo).resolve()
    for rel_path in PACKAGE_PATHS:
        check(f"required path exists: {rel_path}", (repo / rel_path).is_file())

    scope = gp014_decision_scope_record()
    check("scope schema present", bool(scope.get("schema_version")))
    check("scope has no runtime effect", scope.get("runtime_effect") == "none")
    check("scope has no dependency change", scope.get("dependency_change") == "none")
    check("scope keeps GP-014 preserved", scope.get("gp014_status") == "preserved_protected_unsuperseded")
    check("scope keeps GP-014 referenced only", scope.get("gp014_relationship") == "referenced_only")
    check("scope records no wrapper", scope.get("gp014_wrapper_decision") == "no_wrapper_at_slice18")
    check("scope records no import", scope.get("gp014_import_decision") == "no_import")
    check("scope records no call", scope.get("gp014_call_decision") == "no_call")
    check("scope records no supersession", scope.get("gp014_supersession_decision") == "no_supersession")
    check("scope records no promotion", scope.get("gp014_promotion_decision") == "no_promotion")
    check("scope keeps GP-015 failed", scope.get("gp015_status") == "failed_not_repaired")
    check("scope keeps Slice 17 not a GP-014 wrapper", scope.get("slice17_status") == "expression_boundary_not_gp014_wrapper")
    check("scope carries exact GP-014 protected hashes", tuple(scope.get("gp014_protected_path_hashes", ())) == GP014_PROTECTED_PATH_HASHES)
    check("scope carries exact GP-015 protected hashes", tuple(scope.get("gp015_protected_path_hashes", ())) == GP015_PROTECTED_PATH_HASHES)
    check("scope records renderer as evidence paths only", tuple(scope.get("related_renderer_evidence_paths", ())) == RELATED_RENDERER_EVIDENCE_PATHS)
    for field in FALSE_ONLY_AUTHORITY_FIELDS:
        check(f"scope blocks {field}", scope.get(field) is False)
    for law in REQUIRED_DECISION_LAWS:
        check(f"scope carries law {law}", law in scope.get("required_decision_laws", ()))

    reference = build_gp014_reference_record()
    wrapper = build_gp014_wrapper_decision_record(gp014_reference_id=reference.gp014_reference_id)
    receipt = build_gp014_preservation_receipt_record(
        gp014_reference_id=reference.gp014_reference_id,
        gp014_wrapper_decision_id=wrapper.gp014_wrapper_decision_id,
    )
    check("GP-014 reference validates", validate_gp014_reference_record(reference).ok)
    check("GP-014 wrapper decision validates", validate_gp014_wrapper_decision_record(wrapper).ok)
    check("GP-014 preservation receipt validates", validate_gp014_preservation_receipt_record(receipt).ok)
    check("GP-014 reference ID stable", reference.gp014_reference_id == reference.expected_id())
    check("GP-014 wrapper decision ID stable", wrapper.gp014_wrapper_decision_id == wrapper.expected_id())
    check("GP-014 preservation receipt ID stable", receipt.gp014_preservation_receipt_id == receipt.expected_id())
    check("accepted GP-014 hashes match repository", not verify_gp014_reference_hashes(repo, reference))
    check("accepted GP-015 hash matches repository", _protected_hashes_match(repo, GP015_PROTECTED_PATH_HASHES))

    mutation_checks = (
        ("reference rejects GP-014 path drift", validate_gp014_reference_record(replace(reference, protected_path_hashes=reference.protected_path_hashes[:-1])).ok is False),
        ("reference rejects GP-014 import flag", validate_gp014_reference_record(replace(reference, gp014_import=True)).ok is False),
        ("reference rejects GP-014 call flag", validate_gp014_reference_record(replace(reference, gp014_call=True)).ok is False),
        ("wrapper rejects wrapper creation", validate_gp014_wrapper_decision_record(replace(wrapper, gp014_wrapper_created=True)).ok is False),
        ("wrapper rejects wrapper decision drift", validate_gp014_wrapper_decision_record(replace(wrapper, wrapper_decision="wrapper_allowed")).ok is False),
        ("wrapper rejects supersession", validate_gp014_wrapper_decision_record(replace(wrapper, gp014_supersession=True)).ok is False),
        ("wrapper rejects promotion", validate_gp014_wrapper_decision_record(replace(wrapper, gp014_promotion=True)).ok is False),
        ("wrapper rejects general language authority", validate_gp014_wrapper_decision_record(replace(wrapper, general_language_authority=True)).ok is False),
        ("wrapper rejects concept authority", validate_gp014_wrapper_decision_record(replace(wrapper, concept_authority=True)).ok is False),
        ("wrapper rejects predicate authority", validate_gp014_wrapper_decision_record(replace(wrapper, predicate_authority=True)).ok is False),
        ("wrapper rejects selected meaning authority", validate_gp014_wrapper_decision_record(replace(wrapper, selected_meaning_authority=True)).ok is False),
        ("wrapper rejects full RMC authority", validate_gp014_wrapper_decision_record(replace(wrapper, full_rmc_authority=True)).ok is False),
        ("wrapper rejects renderer authority", validate_gp014_wrapper_decision_record(replace(wrapper, renderer_authority=True)).ok is False),
        ("wrapper rejects delivery authority", validate_gp014_wrapper_decision_record(replace(wrapper, delivery_authority=True)).ok is False),
        ("wrapper rejects echo authority", validate_gp014_wrapper_decision_record(replace(wrapper, echo_authority=True)).ok is False),
        ("receipt rejects GP-015 repair", validate_gp014_preservation_receipt_record(replace(receipt, gp015_repair=True)).ok is False),
        ("receipt rejects protected hash unverified", validate_gp014_preservation_receipt_record(replace(receipt, protected_hashes_verified=False)).ok is False),
        ("receipt rejects Slice 17 wrapper claim", validate_gp014_preservation_receipt_record(replace(receipt, slice17_not_gp014_wrapper=False)).ok is False),
    )
    for label, condition in mutation_checks:
        check(label, condition)

    for rel_path in PACKAGE_PATHS:
        if not rel_path.endswith(".py"):
            continue
        path = repo / rel_path
        if not path.is_file():
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            check(f"{rel_path} Python syntax valid", True)
        except SyntaxError:
            check(f"{rel_path} Python syntax valid", False)
            continue
        imports = _active_import_names(path)
        check(f"{rel_path} does not import forbidden modules", not any(_is_forbidden_import(name) for name in imports))

    code, head = _git(repo, "rev-parse", "HEAD")
    if code == 0 and head:
        check("repository HEAD is accepted Slice 17 base or later clean committed state", head == BASE_HEAD or not _git_status_lines(repo))
    else:
        check("repository HEAD is readable", False)
    check("git status limited to Slice 18 additive paths when dirty", git_status_limited_to_slice18(repo))
    for rel_path, _expected in GP014_PROTECTED_PATH_HASHES + GP015_PROTECTED_PATH_HASHES:
        check(f"protected source path untouched in git status: {rel_path}", _path_status_is_clean(repo, rel_path))
    for rel_path in RELATED_RENDERER_EVIDENCE_PATHS:
        check(f"renderer evidence path untouched in git status: {rel_path}", _path_status_is_clean(repo, rel_path))

    return passes, failures
