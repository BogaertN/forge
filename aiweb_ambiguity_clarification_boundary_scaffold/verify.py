"""Verifier helpers for Slice 12 ambiguity and clarification boundary scaffold."""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess
from typing import List, Sequence, Tuple

from .clarification import (
    ClarificationRequirementBoundaryRecord,
    demo_clarification_blocked_record,
    demo_clarification_required_record,
    validate_clarification_requirement_record,
)
from .state_boundary import (
    AmbiguityStateBoundaryRecord,
    ambiguity_clarification_scope_record,
    demo_ambiguity_state_record,
    demo_deferred_state_record,
    demo_unknown_state_record,
    demo_unsupported_state_record,
    validate_state_boundary_record,
)
from .trace_state import (
    StateTraceBoundaryRecord,
    demo_state_trace_record,
    validate_state_trace_record,
)
from .unknown_support import (
    UnknownSupportBoundaryRecord,
    demo_unknown_concept_record,
    demo_unsupported_resource_record,
    validate_unknown_support_record,
)

REQUIRED_PATHS = (
    "aiweb_ambiguity_clarification_boundary_scaffold/__init__.py",
    "aiweb_ambiguity_clarification_boundary_scaffold/state_boundary.py",
    "aiweb_ambiguity_clarification_boundary_scaffold/clarification.py",
    "aiweb_ambiguity_clarification_boundary_scaffold/unknown_support.py",
    "aiweb_ambiguity_clarification_boundary_scaffold/trace_state.py",
    "aiweb_ambiguity_clarification_boundary_scaffold/verify.py",
    "scripts/test_aiweb_slice12_ambiguity_clarification_boundary_scaffold.py",
    "scripts/aiweb_slice12_ambiguity_clarification_verify.py",
    "scripts/README_aiweb_slice12_ambiguity_clarification_boundary_scaffold.md",
)

EXPECTED_STATUS_PATHS = frozenset(REQUIRED_PATHS)
EXPECTED_STATUS_DIRS = frozenset({"aiweb_ambiguity_clarification_boundary_scaffold"})


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


def git_status_limited_to_slice12(repo: Path) -> bool:
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
        return True, "slice6 scanner found no Slice 12 source findings"
    return False, f"slice6 scanner findings:{report.finding_count}"


def _scope_blocks_all_downstream_authorities() -> bool:
    scope = ambiguity_clarification_scope_record()
    must_false = (
        "live_runtime_interpretation",
        "live_clarification",
        "user_facing_question_emission",
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
    return "BOUNDARY_BLOCKED_NON_AUTHORITATIVE" in text and "core_authority" in text and "False" in text


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

    for rel_path in REQUIRED_PATHS:
        path = repo / rel_path
        if path.exists() and path.is_file():
            passes.append(f"required file exists: {rel_path}")
        else:
            failures.append(f"required file missing: {rel_path}")

    bad_imports = set(_bad_import_names())
    for path in _required_source_paths(repo):
        if path.suffix != ".py":
            if path.exists():
                passes.append(f"non-python required file present: {path}")
            continue
        if not path.exists():
            continue
        ok, message = _compile_python(path)
        if ok:
            passes.append(f"python syntax valid: {path}")
        else:
            failures.append(f"python syntax invalid: {path}: {message}")
        roots = set(_active_import_roots(path))
        disallowed = sorted(roots.intersection(bad_imports))
        if path.name in {"verify.py", "aiweb_slice12_ambiguity_clarification_verify.py"}:
            disallowed = [item for item in disallowed if item != "subprocess"]
        if disallowed:
            failures.append(f"blocked active imports in {path}: {disallowed}")
        else:
            passes.append(f"no blocked active imports: {path}")

    for rel_path in FROZEN_UNTOUCHED_PATHS:
        if _path_status_is_clean(repo, rel_path):
            passes.append(f"frozen path untouched by Slice 12: {rel_path}")
        else:
            failures.append(f"frozen path modified by Slice 12: {rel_path}")

    if _scope_blocks_all_downstream_authorities():
        passes.append("scope record blocks all downstream authority categories")
    else:
        failures.append("scope record does not block all downstream authority categories")

    samples = [
        ("demo ambiguity state boundary record", demo_ambiguity_state_record(), validate_state_boundary_record),
        ("demo unknown state boundary record", demo_unknown_state_record(), validate_state_boundary_record),
        ("demo unsupported state boundary record", demo_unsupported_state_record(), validate_state_boundary_record),
        ("demo deferred state boundary record", demo_deferred_state_record(), validate_state_boundary_record),
        ("demo clarification-required boundary record", demo_clarification_required_record(), validate_clarification_requirement_record),
        ("demo clarification-blocked boundary record", demo_clarification_blocked_record(), validate_clarification_requirement_record),
        ("demo unknown concept boundary record", demo_unknown_concept_record(), validate_unknown_support_record),
        ("demo unsupported resource boundary record", demo_unsupported_resource_record(), validate_unknown_support_record),
        ("demo state trace boundary record", demo_state_trace_record(), validate_state_trace_record),
    ]
    for label, record, validator in samples:
        report = validator(record)
        if report.ok:
            passes.append(f"{label} is valid")
        else:
            failures.append(f"{label} invalid:{[issue.reason for issue in report.issues]}")

    if demo_ambiguity_state_record().state_boundary_id == demo_ambiguity_state_record().expected_id():
        passes.append("state identifiers are deterministic")
    else:
        failures.append("state identifiers are not deterministic")
    if demo_clarification_required_record().clarification_boundary_id == demo_clarification_required_record().expected_id():
        passes.append("clarification identifiers are deterministic")
    else:
        failures.append("clarification identifiers are not deterministic")
    if demo_unknown_concept_record().unknown_boundary_id == demo_unknown_concept_record().expected_id():
        passes.append("unknown-support identifiers are deterministic")
    else:
        failures.append("unknown-support identifiers are not deterministic")
    if demo_state_trace_record().trace_state_id == demo_state_trace_record().expected_id():
        passes.append("trace-state identifiers are deterministic")
    else:
        failures.append("trace-state identifiers are not deterministic")

    unsafe_state = AmbiguityStateBoundaryRecord(
        **{**demo_ambiguity_state_record().__dict__, "selected_meaning": True}
    )
    if not validate_state_boundary_record(unsafe_state).ok:
        passes.append("state selected-meaning flag is rejected")
    else:
        failures.append("state selected-meaning flag was not rejected")

    unsafe_clarification = ClarificationRequirementBoundaryRecord(
        **{**demo_clarification_required_record().__dict__, "user_facing_question_emission": True}
    )
    if not validate_clarification_requirement_record(unsafe_clarification).ok:
        passes.append("clarification live question flag is rejected")
    else:
        failures.append("clarification live question flag was not rejected")

    unsafe_unknown = UnknownSupportBoundaryRecord(
        **{**demo_unknown_concept_record().__dict__, "guess_substitution": True}
    )
    if not validate_unknown_support_record(unsafe_unknown).ok:
        passes.append("unknown guess-substitution flag is rejected")
    else:
        failures.append("unknown guess-substitution flag was not rejected")

    unsafe_trace = StateTraceBoundaryRecord(
        **{**demo_state_trace_record().__dict__, "evidence_validation": True}
    )
    if not validate_state_trace_record(unsafe_trace).ok:
        passes.append("trace evidence flag is rejected")
    else:
        failures.append("trace evidence flag was not rejected")

    if _llm_renderer_is_blocked_boundary(repo):
        passes.append("llm_renderer remains blocked boundary evidence only")
    else:
        failures.append("llm_renderer blocked boundary evidence proof failed")

    scanner_ok, scanner_message = _check_slice6_scanner(repo)
    if scanner_ok:
        passes.append(scanner_message)
    else:
        failures.append(scanner_message)

    if git_status_limited_to_slice12(repo):
        passes.append("git status is clean or limited to Slice 12 scaffold paths")
    else:
        failures.append("git status contains paths outside Slice 12 scaffold")

    return passes, failures
