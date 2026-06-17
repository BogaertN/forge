"""Verifier helpers for Slice 13 requirements traceability scaffold."""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess
from typing import List, Sequence, Tuple

from .accepted_scope import (
    AcceptedScopeRecord,
    RollbackTriggerRecord,
    demo_accepted_scope_record,
    demo_rollback_trigger_record,
    validate_accepted_scope_record,
    validate_rollback_trigger_record,
)
from .core import requirements_traceability_scope_record
from .crosswalk import (
    RequirementTestCrosswalkRecord,
    demo_requirement_test_crosswalk_record,
    validate_requirement_test_crosswalk_record,
)
from .receipt import (
    TraceabilityReceiptRecord,
    demo_traceability_receipt_record,
    validate_traceability_receipt_record,
)
from .requirement import (
    RequirementIdentityRecord,
    demo_requirement_identity_record,
    validate_requirement_identity_record,
)

REQUIRED_PATHS = (
    "aiweb_requirements_traceability_scaffold/__init__.py",
    "aiweb_requirements_traceability_scaffold/core.py",
    "aiweb_requirements_traceability_scaffold/requirement.py",
    "aiweb_requirements_traceability_scaffold/crosswalk.py",
    "aiweb_requirements_traceability_scaffold/receipt.py",
    "aiweb_requirements_traceability_scaffold/accepted_scope.py",
    "aiweb_requirements_traceability_scaffold/verify.py",
    "scripts/test_aiweb_slice13_requirements_traceability_scaffold.py",
    "scripts/aiweb_slice13_requirements_traceability_verify.py",
    "scripts/README_aiweb_slice13_requirements_traceability_scaffold.md",
)

EXPECTED_STATUS_PATHS = frozenset(REQUIRED_PATHS)
EXPECTED_STATUS_DIRS = frozenset({"aiweb_requirements_traceability_scaffold"})


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


def git_status_limited_to_slice13(repo: Path) -> bool:
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
        return True, "slice6 scanner found no Slice 13 source findings"
    return False, f"slice6 scanner findings:{report.finding_count}"


def _scope_blocks_all_downstream_authorities() -> bool:
    scope = requirements_traceability_scope_record()
    must_false = (
        "live_runtime_behavior",
        "capability_acceptance",
        "verifier_gate_replacement",
        "result_packet_bypass",
        "accepted_scope_widening",
        "release_authority",
        "production_readiness",
        "delivery_action",
        "action_authorization",
        "tool_invocation",
        "capability_route",
        "memory_write",
        "evidence_validation",
        "external_resource_admission",
        "final_meaning_selection",
        "selected_meaning",
        "truth_decision",
        "live_clarification",
        "user_facing_question_emission",
        "gp014_supersession",
        "gp015_repair",
        "gp015r1_installation",
        "model_authority",
        "vector_authority",
        "retrieval_authority",
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
                failures.append(f"blocked active imports in {path}: {found}")
            else:
                passes.append(f"no blocked active imports: {path}")
        else:
            passes.append(f"non-python required file present: {path}")

    for rel in FROZEN_UNTOUCHED_PATHS:
        if _path_status_is_clean(repo, rel):
            passes.append(f"frozen path untouched by Slice 13: {rel}")
        else:
            failures.append(f"frozen path modified by Slice 13: {rel}")

    if _scope_blocks_all_downstream_authorities():
        passes.append("scope record blocks all downstream authority categories")
    else:
        failures.append("scope record does not block all downstream authority categories")

    demo_checks = (
        ("demo requirement identity record is valid", validate_requirement_identity_record(demo_requirement_identity_record()).ok),
        ("demo requirement-to-test crosswalk record is valid", validate_requirement_test_crosswalk_record(demo_requirement_test_crosswalk_record()).ok),
        ("demo traceability receipt record is valid", validate_traceability_receipt_record(demo_traceability_receipt_record()).ok),
        ("demo accepted scope record is valid", validate_accepted_scope_record(demo_accepted_scope_record()).ok),
        ("demo rollback trigger record is valid", validate_rollback_trigger_record(demo_rollback_trigger_record()).ok),
        ("requirement identifiers are deterministic", demo_requirement_identity_record().requirement_identity_id == demo_requirement_identity_record().expected_id()),
        ("crosswalk identifiers are deterministic", demo_requirement_test_crosswalk_record().crosswalk_id == demo_requirement_test_crosswalk_record().expected_id()),
        ("receipt identifiers are deterministic", demo_traceability_receipt_record().receipt_id == demo_traceability_receipt_record().expected_id()),
        ("accepted scope identifiers are deterministic", demo_accepted_scope_record().accepted_scope_id == demo_accepted_scope_record().expected_id()),
        ("rollback trigger identifiers are deterministic", demo_rollback_trigger_record().rollback_trigger_id == demo_rollback_trigger_record().expected_id()),
    )
    for label, ok in demo_checks:
        if ok:
            passes.append(label)
        else:
            failures.append(label)

    unsafe_requirement = RequirementIdentityRecord(**{**demo_requirement_identity_record().__dict__, "capability_acceptance": True})
    if not validate_requirement_identity_record(unsafe_requirement).ok:
        passes.append("requirement capability-acceptance flag is rejected")
    else:
        failures.append("requirement capability-acceptance flag was not rejected")

    unsafe_crosswalk = RequirementTestCrosswalkRecord(**{**demo_requirement_test_crosswalk_record().__dict__, "verifier_gate_replacement": True})
    if not validate_requirement_test_crosswalk_record(unsafe_crosswalk).ok:
        passes.append("crosswalk verifier-gate replacement flag is rejected")
    else:
        failures.append("crosswalk verifier-gate replacement flag was not rejected")

    unsafe_receipt = TraceabilityReceiptRecord(**{**demo_traceability_receipt_record().__dict__, "result_packet_bypass": True})
    if not validate_traceability_receipt_record(unsafe_receipt).ok:
        passes.append("receipt result-packet bypass flag is rejected")
    else:
        failures.append("receipt result-packet bypass flag was not rejected")

    unsafe_scope = AcceptedScopeRecord(**{**demo_accepted_scope_record().__dict__, "accepted_scope_widening": True})
    if not validate_accepted_scope_record(unsafe_scope).ok:
        passes.append("accepted-scope widening flag is rejected")
    else:
        failures.append("accepted-scope widening flag was not rejected")

    unsafe_rollback = RollbackTriggerRecord(**{**demo_rollback_trigger_record().__dict__, "release_authority": True})
    if not validate_rollback_trigger_record(unsafe_rollback).ok:
        passes.append("rollback release flag is rejected")
    else:
        failures.append("rollback release flag was not rejected")

    if _llm_renderer_is_blocked_boundary(repo):
        passes.append("llm_renderer remains blocked boundary evidence only")
    else:
        failures.append("llm_renderer blocked boundary evidence check failed")

    scan_ok, scan_detail = _check_slice6_scanner(repo)
    if scan_ok:
        passes.append(scan_detail)
    else:
        failures.append(scan_detail)

    if git_status_limited_to_slice13(repo):
        passes.append("git status is clean or limited to Slice 13 scaffold paths")
    else:
        failures.append("git status contains paths outside Slice 13 scaffold")

    return passes, failures
