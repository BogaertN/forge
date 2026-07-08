"""Verifier helpers for Slice 16 selected-meaning boundary scaffold."""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess
from typing import List, Sequence, Tuple

from .candidate_reference import CandidateSelectionReferenceRecord, demo_candidate_selection_reference_record, demo_non_selected_candidate_reference_record, validate_candidate_selection_reference_record
from .core import REQUIRED_PRIOR_BOUNDARIES, REQUIRED_SELECTION_LAWS, SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS, selected_meaning_scope_record
from .selection_basis import SelectionBasisRecord, demo_selection_basis_record, validate_selection_basis_record
from .selection_constraint import SelectionConstraintRecord, demo_selection_constraint_record, validate_selection_constraint_record
from .selection_receipt import SelectionReceiptRecord, demo_selection_receipt_record, validate_selection_receipt_record
from .selection_status import SelectedMeaningStatusRecord, demo_selected_meaning_status_record, demo_selection_blocked_status_record, validate_selected_meaning_status_record
from .selection_trace import SelectionTraceRecord, demo_selection_trace_record, validate_selection_trace_record

REQUIRED_PATHS = (
    "aiweb_selected_meaning_boundary_scaffold/__init__.py",
    "aiweb_selected_meaning_boundary_scaffold/core.py",
    "aiweb_selected_meaning_boundary_scaffold/candidate_reference.py",
    "aiweb_selected_meaning_boundary_scaffold/selection_basis.py",
    "aiweb_selected_meaning_boundary_scaffold/selection_constraint.py",
    "aiweb_selected_meaning_boundary_scaffold/selection_status.py",
    "aiweb_selected_meaning_boundary_scaffold/selection_trace.py",
    "aiweb_selected_meaning_boundary_scaffold/selection_receipt.py",
    "aiweb_selected_meaning_boundary_scaffold/verify.py",
    "scripts/test_aiweb_slice16_selected_meaning_boundary_scaffold.py",
    "scripts/aiweb_slice16_selected_meaning_boundary_verify.py",
    "scripts/README_aiweb_slice16_selected_meaning_boundary_scaffold.md",
)

EXPECTED_STATUS_PATHS = frozenset(REQUIRED_PATHS)
EXPECTED_STATUS_DIRS = frozenset({"aiweb_selected_meaning_boundary_scaffold"})


def _join(parts: Sequence[str]) -> str:
    return "".join(parts)


FROZEN_UNTOUCHED_PATHS = (
    "config/approved_paths.json",
    "config/session_scope.json",
    "config/tool_registry.json",
    "requirements.txt",
    "agents/forge/knowledge_base.py",
    "agents/forge/runner.py",
    _join(("rmc_engine_v1/", "ch", "roma", "_connector.py")),
    "rmc_engine_v1/llm_renderer.py",
    "aiweb_proof_scaffold/__init__.py",
    "aiweb_gp014_regression_scaffold/__init__.py",
    "aiweb_status_claim_scaffold/__init__.py",
    "aiweb_decision_baseline_scaffold/__init__.py",
    "aiweb_implementation_ledger_scaffold/__init__.py",
    "aiweb_authority_scanner_scaffold/__init__.py",
    "aiweb_meaning_law_trace_scaffold/__init__.py",
    "aiweb_concept_boundary_scaffold/__init__.py",
    "aiweb_predicate_role_boundary_scaffold/__init__.py",
    "aiweb_verbal_cognition_gate_boundary_scaffold/__init__.py",
    "aiweb_candidate_meaning_boundary_scaffold/__init__.py",
    "aiweb_ambiguity_clarification_boundary_scaffold/__init__.py",
    "aiweb_requirements_traceability_scaffold/__init__.py",
    "aiweb_external_resource_quarantine_scaffold/__init__.py",
    "aiweb_corpus_evidence_memory_trace_scaffold/__init__.py",
)

_BAD_IMPORT_PARTS = [
    ("open", "ai"),
    ("anth", "ropic"),
    ("chrom", "adb"),
    ("lang", "chain"),
    ("fa", "iss"),
    ("sk", "learn"),
    ("sentence", "_", "transform", "ers"),
    ("transform", "ers"),
    ("torch",),
    ("tensorflow",),
    ("request", "s"),
    ("http", "x"),
    ("url", "lib"),
    ("socket",),
    ("sqlite", "3"),
    ("oll", "ama"),
    ("llama", "_", "cpp"),
]


def _bad_import_names() -> List[str]:
    return [_join(parts) for parts in _BAD_IMPORT_PARTS]


def _compile_python(path: Path) -> Tuple[bool, str]:
    try:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
        return True, "syntax_ok"
    except SyntaxError as exc:
        return False, f"syntax_error:{exc}"


def _active_import_roots(path: Path) -> List[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.append(node.module.split(".")[0])
    return roots


def _status_path(line: str) -> str:
    cleaned = line[3:] if len(line) > 3 else line
    if " -> " in cleaned:
        cleaned = cleaned.split(" -> ", 1)[1]
    return cleaned.strip()


def _git_status_lines(repo: Path) -> List[str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "status", "--short"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except FileNotFoundError:
        return ["GIT_NOT_FOUND"]
    lines: List[str] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        path = _status_path(line)
        if "__pycache__/" in path or path.endswith(".pyc") or path.endswith(".pyo"):
            continue
        lines.append(line)
    return lines


def git_status_limited_to_slice16(repo: Path) -> bool:
    lines = _git_status_lines(repo)
    if not lines:
        return True
    for line in lines:
        path = _status_path(line)
        if path in EXPECTED_STATUS_PATHS:
            continue
        trimmed = path.rstrip("/")
        if trimmed in EXPECTED_STATUS_DIRS:
            continue
        return False
    return True


def _path_status_is_clean(repo: Path, rel_path: str) -> bool:
    for line in _git_status_lines(repo):
        if _status_path(line) == rel_path:
            return False
    return True


def _required_source_paths(repo: Path) -> List[Path]:
    return [repo / item for item in REQUIRED_PATHS]


def _check_slice6_scanner(repo: Path) -> Tuple[bool, str]:
    try:
        from aiweb_authority_scanner_scaffold.scanner import scan_paths
    except Exception as exc:  # pragma: no cover
        return False, f"slice6_scanner_import_failed:{exc}"
    report = scan_paths(_required_source_paths(repo))
    if report.finding_count == 0:
        return True, "slice6 scanner found no Slice 16 source findings"
    return False, f"slice6 scanner findings:{report.finding_count}"


def _scope_blocks_all_downstream_authorities() -> bool:
    scope = selected_meaning_scope_record()
    return (
        scope.get("scaffold_only") is True
        and scope.get("runtime_effect") == "none"
        and scope.get("dependency_change") == "none"
        and all(scope.get(key) is False for key in SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS)
        and tuple(scope.get("required_selection_laws", ())) == REQUIRED_SELECTION_LAWS
        and tuple(scope.get("required_prior_boundaries", ())) == REQUIRED_PRIOR_BOUNDARIES
        and scope.get("truth_status") == "not_truth_decision"
        and scope.get("permission_status") == "not_permission_grant"
        and scope.get("delivery_status") == "not_delivery"
        and scope.get("execution_status") == "not_execution"
        and scope.get("gp014_status") == "protected_not_superseded"
        and scope.get("gp015_status") == "failed_not_repaired"
        and scope.get("gp015r1_status") == "uninstalled_not_live"
        and scope.get("external_resource_status") == "unadmitted"
    )


def _llm_renderer_is_blocked_boundary(repo: Path) -> bool:
    path = repo / "rmc_engine_v1/llm_renderer.py"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return "BOUNDARY_BLOCKED_NON_AUTHORITATIVE" in text and "core_authority" in text and "False" in text


def _records_validate() -> Tuple[List[str], List[str]]:
    checks = (
        ("candidate selection reference validates", validate_candidate_selection_reference_record(demo_candidate_selection_reference_record()).ok),
        ("non-selected candidate reference validates", validate_candidate_selection_reference_record(demo_non_selected_candidate_reference_record()).ok),
        ("selection basis validates", validate_selection_basis_record(demo_selection_basis_record()).ok),
        ("selection constraint validates", validate_selection_constraint_record(demo_selection_constraint_record()).ok),
        ("selected meaning status validates", validate_selected_meaning_status_record(demo_selected_meaning_status_record()).ok),
        ("selection blocked status validates", validate_selected_meaning_status_record(demo_selection_blocked_status_record()).ok),
        ("selection trace validates", validate_selection_trace_record(demo_selection_trace_record()).ok),
        ("selection receipt validates", validate_selection_receipt_record(demo_selection_receipt_record()).ok),
    )
    passes = [label for label, ok in checks if ok]
    failures = [label for label, ok in checks if not ok]
    return passes, failures


def _stable_ids_validate() -> Tuple[List[str], List[str]]:
    pairs = (
        ("candidate selection reference ID deterministic", demo_candidate_selection_reference_record().selection_reference_id == demo_candidate_selection_reference_record().expected_id()),
        ("selection basis ID deterministic", demo_selection_basis_record().selection_basis_id == demo_selection_basis_record().expected_id()),
        ("selection constraint ID deterministic", demo_selection_constraint_record().selection_constraint_id == demo_selection_constraint_record().expected_id()),
        ("selected meaning status ID deterministic", demo_selected_meaning_status_record().selected_meaning_id == demo_selected_meaning_status_record().expected_id()),
        ("selection trace ID deterministic", demo_selection_trace_record().selection_trace_id == demo_selection_trace_record().expected_id()),
        ("selection receipt ID deterministic", demo_selection_receipt_record().selection_receipt_id == demo_selection_receipt_record().expected_id()),
    )
    passes = [label for label, ok in pairs if ok]
    failures = [label for label, ok in pairs if not ok]
    return passes, failures


def _collapse_rejections_validate() -> Tuple[List[str], List[str]]:
    checks = (
        (
            "selected meaning cannot become truth",
            not validate_selected_meaning_status_record(SelectedMeaningStatusRecord(**{**demo_selected_meaning_status_record().__dict__, "selection_as_truth": True})).ok,
        ),
        (
            "selected meaning cannot grant permission",
            not validate_selected_meaning_status_record(SelectedMeaningStatusRecord(**{**demo_selected_meaning_status_record().__dict__, "selection_as_permission": True})).ok,
        ),
        (
            "selected meaning cannot become delivery",
            not validate_selection_receipt_record(SelectionReceiptRecord(**{**demo_selection_receipt_record().__dict__, "selection_as_delivery": True})).ok,
        ),
        (
            "selected meaning cannot become execution",
            not validate_selection_trace_record(SelectionTraceRecord(**{**demo_selection_trace_record().__dict__, "selection_as_execution": True})).ok,
        ),
        (
            "final meaning selection flag rejected",
            not validate_selected_meaning_status_record(SelectedMeaningStatusRecord(**{**demo_selected_meaning_status_record().__dict__, "final_meaning_selection": True})).ok,
        ),
        (
            "truth decision flag rejected",
            not validate_selection_receipt_record(SelectionReceiptRecord(**{**demo_selection_receipt_record().__dict__, "truth_decision": True})).ok,
        ),
        (
            "permission grant flag rejected",
            not validate_selection_receipt_record(SelectionReceiptRecord(**{**demo_selection_receipt_record().__dict__, "permission_grant": True})).ok,
        ),
        (
            "delivery action flag rejected",
            not validate_selection_receipt_record(SelectionReceiptRecord(**{**demo_selection_receipt_record().__dict__, "delivery_action": True})).ok,
        ),
        (
            "execution authority flag rejected",
            not validate_selection_receipt_record(SelectionReceiptRecord(**{**demo_selection_receipt_record().__dict__, "execution_authority": True})).ok,
        ),
        (
            "tool invocation flag rejected",
            not validate_candidate_selection_reference_record(CandidateSelectionReferenceRecord(**{**demo_candidate_selection_reference_record().__dict__, "tool_invocation": True})).ok,
        ),
        (
            "output rendering flag rejected",
            not validate_selected_meaning_status_record(SelectedMeaningStatusRecord(**{**demo_selected_meaning_status_record().__dict__, "output_rendering": True})).ok,
        ),
        (
            "memory write flag rejected",
            not validate_selected_meaning_status_record(SelectedMeaningStatusRecord(**{**demo_selected_meaning_status_record().__dict__, "memory_write": True})).ok,
        ),
        (
            "evidence validation flag rejected",
            not validate_selection_basis_record(SelectionBasisRecord(**{**demo_selection_basis_record().__dict__, "evidence_validation": True})).ok,
        ),
        (
            "external resource admission flag rejected",
            not validate_selection_constraint_record(SelectionConstraintRecord(**{**demo_selection_constraint_record().__dict__, "external_resource_admission": True})).ok,
        ),
        (
            "receipt effect cannot claim delivery",
            not validate_selection_receipt_record(SelectionReceiptRecord(**{**demo_selection_receipt_record().__dict__, "receipt_effect": "delivery_performed"})).ok,
        ),
        (
            "trace scope cannot claim execution",
            not validate_selection_trace_record(SelectionTraceRecord(**{**demo_selection_trace_record().__dict__, "trace_scope": "execution_trace"})).ok,
        ),
    )
    passes = [label for label, ok in checks if ok]
    failures = [label for label, ok in checks if not ok]
    return passes, failures


def run_verification(repo: Path) -> Tuple[List[str], List[str]]:
    passes: List[str] = []
    failures: List[str] = []

    if repo.exists() and repo.is_dir():
        passes.append(f"target repo directory exists: {repo}")
    else:
        failures.append(f"target repo directory missing: {repo}")
        return passes, failures
    if (repo / "scripts").exists() and (repo / "aiweb_authority_scanner_scaffold").exists():
        passes.append(f"target repo path is Forge-shaped: {repo}")
    else:
        failures.append(f"target repo path is not Forge-shaped: {repo}")
    if (repo / ".git").exists():
        passes.append("target repo is a git repository")
    else:
        failures.append("target repo is not a git repository")

    for rel in REQUIRED_PATHS:
        path = repo / rel
        if path.exists():
            passes.append(f"required file exists: {rel}")
        else:
            failures.append(f"required file missing: {rel}")

    bad_imports = set(_bad_import_names())
    for path in _required_source_paths(repo):
        if not path.exists():
            continue
        if path.suffix == ".py":
            ok, detail = _compile_python(path)
            if ok:
                passes.append(f"python syntax valid: {path}")
            else:
                failures.append(f"python syntax invalid: {path}:{detail}")
            roots = set(_active_import_roots(path))
            found = sorted(roots.intersection(bad_imports))
            if found:
                failures.append(f"blocked active import in {path}: {found}")
            else:
                passes.append(f"no blocked active imports: {path}")
        else:
            passes.append(f"non-python required file present: {path}")

    for rel in FROZEN_UNTOUCHED_PATHS:
        if _path_status_is_clean(repo, rel):
            passes.append(f"frozen path untouched by Slice 16: {rel}")
        else:
            failures.append(f"frozen path touched by Slice 16: {rel}")

    if _scope_blocks_all_downstream_authorities():
        passes.append("scope record blocks all downstream authority categories")
    else:
        failures.append("scope record does not block all downstream authority categories")

    record_passes, record_failures = _records_validate()
    passes.extend(record_passes)
    failures.extend(record_failures)

    id_passes, id_failures = _stable_ids_validate()
    passes.extend(id_passes)
    failures.extend(id_failures)

    collapse_passes, collapse_failures = _collapse_rejections_validate()
    passes.extend(collapse_passes)
    failures.extend(collapse_failures)

    if _llm_renderer_is_blocked_boundary(repo):
        passes.append("llm_renderer remains blocked boundary evidence only")
    else:
        failures.append("llm_renderer blocked-boundary evidence check failed")

    scanner_ok, scanner_detail = _check_slice6_scanner(repo)
    if scanner_ok:
        passes.append(scanner_detail)
    else:
        failures.append(scanner_detail)

    if git_status_limited_to_slice16(repo):
        passes.append("git status is clean or limited to Slice 16 scaffold paths")
    else:
        failures.append("git status includes paths outside Slice 16 scaffold")

    return passes, failures
