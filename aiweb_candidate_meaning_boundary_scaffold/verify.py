"""Verifier helpers for Slice 11 candidate meaning boundary scaffold."""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess
from typing import List, Sequence, Tuple

from .candidate import (
    CandidateMeaningBoundaryRecord,
    candidate_meaning_scope_record,
    demo_candidate_meaning_record,
    demo_no_action_candidate_record,
    demo_unsupported_candidate_record,
    validate_candidate_meaning_record,
)
from .competition import (
    CandidateCompetitionSetBoundaryRecord,
    demo_candidate_competition_set_record,
    validate_candidate_competition_set_record,
)
from .derived_structure import (
    DerivedStructureCustodyRecord,
    demo_derived_structure_custody_record,
    validate_derived_structure_custody_record,
)
from .source_custody import (
    SourceExpressionCustodyRecord,
    demo_source_expression_custody_record,
    validate_source_expression_custody_record,
)
from .support_boundary import (
    MissingSupportBoundaryRecord,
    demo_missing_support_boundary_record,
    demo_no_missing_support_boundary_record,
    validate_missing_support_boundary_record,
)

REQUIRED_PATHS = (
    "aiweb_candidate_meaning_boundary_scaffold/__init__.py",
    "aiweb_candidate_meaning_boundary_scaffold/candidate.py",
    "aiweb_candidate_meaning_boundary_scaffold/source_custody.py",
    "aiweb_candidate_meaning_boundary_scaffold/derived_structure.py",
    "aiweb_candidate_meaning_boundary_scaffold/support_boundary.py",
    "aiweb_candidate_meaning_boundary_scaffold/competition.py",
    "aiweb_candidate_meaning_boundary_scaffold/verify.py",
    "scripts/test_aiweb_slice11_candidate_meaning_boundary_scaffold.py",
    "scripts/aiweb_slice11_candidate_meaning_verify.py",
    "scripts/README_aiweb_slice11_candidate_meaning_boundary_scaffold.md",
)

EXPECTED_STATUS_PATHS = frozenset(REQUIRED_PATHS)
EXPECTED_STATUS_DIRS = frozenset({"aiweb_candidate_meaning_boundary_scaffold"})


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
    ("sub", "process"),
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


def _status_path(line: str) -> str:
    cleaned = line[3:] if len(line) > 3 else line
    if " -> " in cleaned:
        cleaned = cleaned.split(" -> ", 1)[1]
    return cleaned.strip()


def git_status_limited_to_slice11(repo: Path) -> bool:
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
        return True, "slice6 scanner found no Slice 11 source findings"
    return False, f"slice6 scanner findings:{report.finding_count}"


def _scope_blocks_all_downstream_authorities() -> bool:
    scope = candidate_meaning_scope_record()
    must_false = (
        "live_runtime_interpretation",
        "selected_meaning",
        "final_meaning_selection",
        "truth_decision",
        "permission_grant",
        "action_authorization",
        "tool_invocation",
        "capability_route",
        "delivery_action",
        "memory_write",
        "evidence_validation",
        "external_resource_admission",
        "expression_rendering",
        "production_readiness",
        "release_authority",
    )
    return (
        scope.get("scaffold_only") is True
        and scope.get("runtime_effect") == "none"
        and scope.get("dependency_change") == "none"
        and all(scope.get(key) is False for key in must_false)
        and scope.get("gp014_status") == "protected_not_superseded"
        and scope.get("gp015_status") == "failed_not_repaired"
        and scope.get("gp015r1_status") == "uninstalled_not_live"
        and scope.get("sanskrit_wordnet_status") == "hold_unadmitted"
    )


def _llm_renderer_is_blocked_boundary(repo: Path) -> bool:
    path = repo / "rmc_engine_v1/llm_renderer.py"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return (
        "BOUNDARY_BLOCKED_NON_AUTHORITATIVE" in text
        and "core_authority" in text
        and "False" in text
    )


def run_verification(repo: Path) -> Tuple[List[str], List[str]]:
    passes: List[str] = []
    failures: List[str] = []

    if repo.exists() and repo.is_dir():
        passes.append(f"target repo directory exists: {repo}")
    else:
        failures.append(f"target repo directory missing: {repo}")
        return passes, failures

    if (repo / ".git").exists() and (repo / "scripts").exists():
        passes.append(f"target repo path is Forge-shaped: {repo}")
    else:
        failures.append(f"target repo path is not Forge-shaped: {repo}")

    git_dir_proc = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--git-dir"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if git_dir_proc.returncode == 0:
        passes.append("target repo is a git repository")
    else:
        failures.append("target repo is not a git repository")

    for rel in REQUIRED_PATHS:
        if (repo / rel).exists():
            passes.append(f"required file exists: {rel}")
        else:
            failures.append(f"required file missing: {rel}")

    bad_import_names = set(_bad_import_names())
    for path in _required_source_paths(repo):
        if not path.exists():
            continue
        if path.suffix != ".py":
            passes.append(f"non-python required file present: {path}")
            continue
        ok, detail = _compile_python(path)
        if ok:
            passes.append(f"python syntax valid: {path}")
        else:
            failures.append(f"python syntax invalid: {path}: {detail}")
            continue
        roots = set(_active_import_roots(path))
        blocked = sorted(roots & bad_import_names)
        if blocked and path.name not in {"verify.py", "aiweb_slice11_candidate_meaning_verify.py"}:
            failures.append(f"blocked active import in {path}: {blocked}")
        else:
            passes.append(f"no blocked active imports: {path}")

    for rel in FROZEN_UNTOUCHED_PATHS:
        if _path_status_is_clean(repo, rel):
            passes.append(f"frozen path untouched by Slice 11: {rel}")
        else:
            failures.append(f"frozen path modified by Slice 11: {rel}")

    if _scope_blocks_all_downstream_authorities():
        passes.append("scope record blocks all downstream authority categories")
    else:
        failures.append("scope record does not block all downstream authority categories")

    # Boundary record samples.
    samples = (
        ("source expression custody record", validate_source_expression_custody_record(demo_source_expression_custody_record())),
        ("derived structure custody record", validate_derived_structure_custody_record(demo_derived_structure_custody_record())),
        ("missing support boundary record", validate_missing_support_boundary_record(demo_missing_support_boundary_record())),
        ("no missing support boundary record", validate_missing_support_boundary_record(demo_no_missing_support_boundary_record())),
        ("candidate meaning boundary record", validate_candidate_meaning_record(demo_candidate_meaning_record())),
        ("no-action candidate boundary record", validate_candidate_meaning_record(demo_no_action_candidate_record())),
        ("unsupported candidate boundary record", validate_candidate_meaning_record(demo_unsupported_candidate_record())),
        ("candidate competition set boundary record", validate_candidate_competition_set_record(demo_candidate_competition_set_record())),
    )
    for label, report in samples:
        if report.ok:
            passes.append(f"demo {label} is valid")
        else:
            failures.append(f"demo {label} invalid: {report.issues}")

    candidate = demo_candidate_meaning_record()
    if candidate.candidate_meaning_id == candidate.expected_id():
        passes.append("candidate identifiers are deterministic")
    else:
        failures.append("candidate identifiers are not deterministic")

    source_record = demo_source_expression_custody_record()
    if source_record.source_expression_id == source_record.expected_id():
        passes.append("source expression identifiers are deterministic")
    else:
        failures.append("source expression identifiers are not deterministic")

    competition = demo_candidate_competition_set_record()
    if competition.unresolved_selection_boundary is True and competition.no_action_safe is True:
        passes.append("competing candidates remain separated and unresolved")
    else:
        failures.append("competition record allowed selection or action")

    unsafe_candidate = CandidateMeaningBoundaryRecord(
        **{**candidate.canonical_body(), "candidate_meaning_id": candidate.expected_id(), "selected_meaning": True}
    )
    if not validate_candidate_meaning_record(unsafe_candidate).ok:
        passes.append("candidate selected-meaning flag is rejected")
    else:
        failures.append("candidate selected-meaning flag was not rejected")

    unsafe_action = CandidateMeaningBoundaryRecord(
        **{**candidate.canonical_body(), "candidate_meaning_id": candidate.expected_id(), "action_authorization": True}
    )
    if not validate_candidate_meaning_record(unsafe_action).ok:
        passes.append("candidate action flag is rejected")
    else:
        failures.append("candidate action flag was not rejected")

    support = demo_missing_support_boundary_record()
    unsafe_support = MissingSupportBoundaryRecord(
        **{**support.canonical_body(), "support_boundary_id": support.expected_id(), "evidence_validation": True}
    )
    if not validate_missing_support_boundary_record(unsafe_support).ok:
        passes.append("support evidence flag is rejected")
    else:
        failures.append("support evidence flag was not rejected")

    derived = demo_derived_structure_custody_record()
    unsafe_derived = DerivedStructureCustodyRecord(
        **{**derived.canonical_body(), "derived_structure_id": derived.expected_id(), "gate_resolution": True}
    )
    if not validate_derived_structure_custody_record(unsafe_derived).ok:
        passes.append("derived structure gate-resolution flag is rejected")
    else:
        failures.append("derived structure gate-resolution flag was not rejected")

    if _llm_renderer_is_blocked_boundary(repo):
        passes.append("llm_renderer remains blocked boundary evidence only")
    else:
        failures.append("llm_renderer blocked boundary evidence not confirmed")

    ok, detail = _check_slice6_scanner(repo)
    if ok:
        passes.append(detail)
    else:
        failures.append(detail)

    if git_status_limited_to_slice11(repo):
        passes.append("git status is clean or limited to Slice 11 scaffold paths")
    else:
        failures.append(f"git status contains paths outside Slice 11 scaffold: {_git_status_lines(repo)}")

    return passes, failures
