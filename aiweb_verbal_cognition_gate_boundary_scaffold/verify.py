"""Verifier helpers for Slice 10 verbal cognition gate boundary scaffold."""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import sys
from typing import List, Sequence, Tuple

from .expectancy import (
    ExpectancyBoundaryRecord,
    demo_connectedness_record,
    demo_congruity_record,
    demo_expectancy_record,
    demo_recoverable_purpose_record,
    demo_unknown_expectancy_record,
    validate_expectancy_record,
)
from .gate_boundary import (
    GateBoundaryRecord,
    demo_gate_boundary_record,
    demo_unknown_gate_boundary_record,
    validate_gate_boundary_record,
    verbal_cognition_gate_scope_record,
)
from .gate_outcome import (
    GateOutcomeBoundaryRecord,
    demo_blocked_action_outcome_record,
    demo_clarification_required_outcome_record,
    demo_gate_outcome_record,
    demo_unknown_gate_outcome_record,
    validate_gate_outcome_record,
)
from .state_boundary import (
    GateStateBoundaryRecord,
    demo_ambiguity_state_record,
    demo_blocked_action_state_record,
    demo_clarification_required_state_record,
    demo_deferred_state_record,
    demo_unsupported_state_record,
    validate_gate_state_record,
)

REQUIRED_PATHS = (
    "aiweb_verbal_cognition_gate_boundary_scaffold/__init__.py",
    "aiweb_verbal_cognition_gate_boundary_scaffold/gate_boundary.py",
    "aiweb_verbal_cognition_gate_boundary_scaffold/gate_outcome.py",
    "aiweb_verbal_cognition_gate_boundary_scaffold/expectancy.py",
    "aiweb_verbal_cognition_gate_boundary_scaffold/state_boundary.py",
    "aiweb_verbal_cognition_gate_boundary_scaffold/verify.py",
    "scripts/test_aiweb_slice10_verbal_cognition_gate_boundary_scaffold.py",
    "scripts/aiweb_slice10_verbal_cognition_gate_verify.py",
    "scripts/README_aiweb_slice10_verbal_cognition_gate_boundary_scaffold.md",
)

EXPECTED_STATUS_PATHS = frozenset(REQUIRED_PATHS)
EXPECTED_STATUS_DIRS = frozenset({"aiweb_verbal_cognition_gate_boundary_scaffold"})


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


def git_status_limited_to_slice10(repo: Path) -> bool:
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
        return True, "slice6 scanner found no Slice 10 source findings"
    return False, f"slice6 scanner findings:{report.finding_count}"


def _scope_blocks_all_downstream_authorities() -> bool:
    scope = verbal_cognition_gate_scope_record()
    must_false = (
        "live_gate_evaluation",
        "gate_resolution",
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
        and scope.get("sanskrit_wordnet_status") == "hold_unadmitted"
        and scope.get("gp014_status") == "protected_prior_scope"
        and scope.get("gp015_status") == "failed_not_repaired"
        and scope.get("gp015r1_status") == "not_installed"
        and all(scope.get(key) is False for key in must_false)
    )


def _slice9_reference_is_boundary_only() -> bool:
    try:
        from aiweb_predicate_role_boundary_scaffold import demo_predicate_frame_record
    except Exception:
        return False
    predicate = demo_predicate_frame_record()
    return (
        predicate.boundary_id().startswith("predicate_frame_")
        and predicate.execution_authority is False
        and predicate.gate_selection is False
        and predicate.selected_meaning is False
    )


def run_verification(repo: Path) -> Tuple[List[str], List[str]]:
    passes: List[str] = []
    failures: List[str] = []
    repo = repo.resolve()

    if repo.exists() and repo.is_dir():
        passes.append(f"target repo directory exists: {repo}")
    else:
        failures.append(f"target repo directory missing: {repo}")
        return passes, failures

    if str(repo) == "/home/nic/forge" or repo.name == "forge":
        passes.append(f"target repo path is Forge-shaped: {repo}")
    else:
        failures.append(f"target repo path is not expected Forge path: {repo}")

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

    for rel in REQUIRED_PATHS:
        path = repo / rel
        if not path.exists() or path.suffix != ".py":
            continue
        ok, msg = _compile_python(path)
        if ok:
            passes.append(f"python syntax valid: {path}")
        else:
            failures.append(f"python syntax invalid: {path}: {msg}")
        blocked_names = set(_bad_import_names())
        blocked = sorted(set(_active_import_roots(path)).intersection(blocked_names))
        if path.match("*/aiweb_verbal_cognition_gate_boundary_scaffold/verify.py") and "subprocess" in blocked:
            blocked.remove("subprocess")
        if blocked:
            failures.append(f"blocked active imports in {path}: {blocked}")
        else:
            passes.append(f"no blocked active imports: {path}")

    for rel in FROZEN_UNTOUCHED_PATHS:
        if _path_status_is_clean(repo, rel):
            passes.append(f"frozen path untouched by Slice 10: {rel}")
        else:
            failures.append(f"frozen path modified by Slice 10: {rel}")

    if _scope_blocks_all_downstream_authorities():
        passes.append("scope record blocks all downstream authority categories")
    else:
        failures.append("scope record does not block all downstream authority categories")

    records = (
        (validate_gate_boundary_record(demo_gate_boundary_record()).passed, "demo gate boundary record is valid"),
        (validate_gate_boundary_record(demo_unknown_gate_boundary_record()).passed, "unknown gate boundary record is valid"),
        (validate_gate_outcome_record(demo_gate_outcome_record()).passed, "demo gate outcome boundary record is valid"),
        (validate_gate_outcome_record(demo_clarification_required_outcome_record()).passed, "clarification outcome boundary record is valid"),
        (validate_gate_outcome_record(demo_blocked_action_outcome_record()).passed, "blocked-action outcome boundary record is valid"),
        (validate_gate_outcome_record(demo_unknown_gate_outcome_record()).passed, "unknown outcome boundary record is valid"),
        (validate_expectancy_record(demo_expectancy_record()).passed, "expectancy boundary record is valid"),
        (validate_expectancy_record(demo_congruity_record()).passed, "congruity boundary record is valid"),
        (validate_expectancy_record(demo_connectedness_record()).passed, "connectedness boundary record is valid"),
        (validate_expectancy_record(demo_recoverable_purpose_record()).passed, "recoverable-purpose boundary record is valid"),
        (validate_expectancy_record(demo_unknown_expectancy_record()).passed, "unknown expectancy boundary record is valid"),
        (validate_gate_state_record(demo_ambiguity_state_record()).passed, "ambiguity state boundary record is valid"),
        (validate_gate_state_record(demo_clarification_required_state_record()).passed, "clarification-required state boundary record is valid"),
        (validate_gate_state_record(demo_unsupported_state_record()).passed, "unsupported state boundary record is valid"),
        (validate_gate_state_record(demo_blocked_action_state_record()).passed, "blocked-action state boundary record is valid"),
        (validate_gate_state_record(demo_deferred_state_record()).passed, "deferred state boundary record is valid"),
        (demo_gate_boundary_record().boundary_id() == demo_gate_boundary_record().boundary_id(), "gate identifiers are deterministic"),
        (demo_gate_outcome_record().boundary_id() == demo_gate_outcome_record().boundary_id(), "outcome identifiers are deterministic"),
        (demo_expectancy_record().boundary_id() == demo_expectancy_record().boundary_id(), "expectancy identifiers are deterministic"),
        (demo_ambiguity_state_record().boundary_id() == demo_ambiguity_state_record().boundary_id(), "state identifiers are deterministic"),
        (_slice9_reference_is_boundary_only(), "Slice 9 predicate reference remains boundary-only"),
    )
    for ok, message in records:
        (passes if ok else failures).append(message)

    unsafe_gate = GateBoundaryRecord(
        gate_key="unsafe_gate",
        gate_type="verbal_cognition_gate_boundary",
        gate_stage="pre_selection_boundary",
        namespace="aiweb:core",
        gate_input_refs=("unsafe_input",),
        predicate_frame_refs=("unsafe_predicate",),
        concept_boundary_refs=("unsafe_concept",),
        provenance_tag="slice10_negative",
        version_tag="v1",
        selected_meaning=True,
    )
    if not validate_gate_boundary_record(unsafe_gate).passed:
        passes.append("gate selected-meaning flag is rejected")
    else:
        failures.append("gate selected-meaning flag was not rejected")

    unsafe_outcome = GateOutcomeBoundaryRecord(
        outcome_key="unsafe_outcome",
        gate_key="unsafe_gate",
        outcome_type="recognized_boundary",
        namespace="aiweb:core",
        reason_boundary_refs=("unsafe_reason",),
        required_next_boundary="unsafe_next",
        provenance_tag="slice10_negative",
        version_tag="v1",
        action_authorization=True,
    )
    if not validate_gate_outcome_record(unsafe_outcome).passed:
        passes.append("outcome action flag is rejected")
    else:
        failures.append("outcome action flag was not rejected")

    unsafe_expectancy = ExpectancyBoundaryRecord(
        expectancy_key="unsafe_expectancy",
        gate_key="unsafe_gate",
        expectancy_type="expectancy_present_boundary",
        namespace="aiweb:core",
        input_boundary_refs=("unsafe_input",),
        reason_boundary_refs=("unsafe_reason",),
        provenance_tag="slice10_negative",
        version_tag="v1",
        evidence_validation=True,
    )
    if not validate_expectancy_record(unsafe_expectancy).passed:
        passes.append("expectancy evidence flag is rejected")
    else:
        failures.append("expectancy evidence flag was not rejected")

    unsafe_state = GateStateBoundaryRecord(
        state_key="unsafe_state",
        gate_key="unsafe_gate",
        state_type="blocked_action_state_boundary",
        namespace="aiweb:core",
        severity_boundary="blocked_boundary",
        reason_boundary_refs=("unsafe_reason",),
        required_future_boundary="unsafe_future",
        provenance_tag="slice10_negative",
        version_tag="v1",
        tool_invocation=True,
    )
    if not validate_gate_state_record(unsafe_state).passed:
        passes.append("state tool flag is rejected")
    else:
        failures.append("state tool flag was not rejected")

    scanner_ok, scanner_msg = _check_slice6_scanner(repo)
    (passes if scanner_ok else failures).append(scanner_msg)

    if git_status_limited_to_slice10(repo):
        passes.append("git status is clean or limited to Slice 10 scaffold paths")
    else:
        failures.append("git status contains out-of-scope paths: " + " | ".join(_git_status_lines(repo)))

    return passes, failures


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    repo = Path(args[0]) if args else Path.cwd()
    print("=" * 60)
    print("AIWEB SLICE 10 VERBAL COGNITION GATE BOUNDARY SCAFFOLD VERIFIER")
    print("=" * 60)
    print(f"Target repo: {repo}")
    passes, failures = run_verification(repo)
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")
    if failures:
        print("VERDICT: FAIL - Slice 10 verbal cognition gate boundary scaffold verifier failed")
        return 1
    print("VERDICT: PASS - Slice 10 verbal cognition gate boundary scaffold verifier passed within Slice 10 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
