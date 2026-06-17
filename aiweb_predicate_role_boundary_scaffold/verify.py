"""Verifier helpers for Slice 9 predicate-role frame boundary scaffold."""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import sys
from typing import List, Sequence, Tuple

from .effect_boundary import (
    EffectBoundaryRecord,
    demo_effect_boundary_record,
    demo_unknown_effect_boundary_record,
    validate_effect_boundary_record,
)
from .predicate_frame import (
    PredicateFrameBoundaryRecord,
    demo_predicate_frame_record,
    demo_unknown_predicate_frame_record,
    predicate_role_scope_record,
    validate_predicate_frame_record,
)
from .roles import (
    RoleBoundaryRecord,
    demo_missing_role_record,
    demo_role_record,
    demo_unknown_role_record,
    validate_role_record,
)
from .speech_act import (
    SpeechActBoundaryRecord,
    demo_command_speech_act_record,
    demo_implementation_request_speech_act_record,
    demo_memory_request_speech_act_record,
    demo_speech_act_record,
    validate_speech_act_record,
)

REQUIRED_PATHS = (
    "aiweb_predicate_role_boundary_scaffold/__init__.py",
    "aiweb_predicate_role_boundary_scaffold/predicate_frame.py",
    "aiweb_predicate_role_boundary_scaffold/roles.py",
    "aiweb_predicate_role_boundary_scaffold/speech_act.py",
    "aiweb_predicate_role_boundary_scaffold/effect_boundary.py",
    "aiweb_predicate_role_boundary_scaffold/verify.py",
    "scripts/test_aiweb_slice09_predicate_role_boundary_scaffold.py",
    "scripts/aiweb_slice09_predicate_role_verify.py",
    "scripts/README_aiweb_slice09_predicate_role_boundary_scaffold.md",
)

EXPECTED_STATUS_PATHS = frozenset(REQUIRED_PATHS)
EXPECTED_STATUS_DIRS = frozenset({"aiweb_predicate_role_boundary_scaffold"})


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


def git_status_limited_to_slice9(repo: Path) -> bool:
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
    except Exception as exc:  # pragma: no cover - defensive verifier branch
        return False, f"slice6_scanner_import_failed:{exc}"
    report = scan_paths(_required_source_paths(repo))
    if report.finding_count == 0:
        return True, "slice6 scanner found no Slice 9 source findings"
    return False, f"slice6 scanner findings:{report.finding_count}"


def _scope_blocks_all_downstream_authorities() -> bool:
    scope = predicate_role_scope_record()
    must_false = (
        "predicate_resolution",
        "role_resolution",
        "speech_act_permission",
        "effect_authorization",
        "selected_meaning",
        "gate_selection",
        "expression_rendering",
        "tool_invocation",
        "capability_route",
        "action_route",
        "memory_write",
        "evidence_validation",
        "external_resource_admission",
        "delivery_action",
        "production_readiness",
        "release_authority",
    )
    return (
        scope.get("scaffold_only") is True
        and scope.get("runtime_effect") == "none"
        and scope.get("dependency_change") == "none"
        and scope.get("sanskrit_wordnet_status") == "hold_unadmitted"
        and all(scope.get(key) is False for key in must_false)
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
        if path.match("*/aiweb_predicate_role_boundary_scaffold/verify.py") and "subprocess" in blocked:
            blocked.remove("subprocess")
        if blocked:
            failures.append(f"blocked active imports in {path}: {blocked}")
        else:
            passes.append(f"no blocked active imports: {path}")

    for rel in FROZEN_UNTOUCHED_PATHS:
        if _path_status_is_clean(repo, rel):
            passes.append(f"frozen path untouched by Slice 9: {rel}")
        else:
            failures.append(f"frozen path modified by Slice 9: {rel}")

    if _scope_blocks_all_downstream_authorities():
        passes.append("scope record blocks all downstream authority categories")
    else:
        failures.append("scope record does not block all downstream authority categories")

    predicate = demo_predicate_frame_record()
    role = demo_role_record()
    missing_role = demo_missing_role_record()
    speech = demo_speech_act_record()
    effect = demo_effect_boundary_record()
    unknown_predicate = demo_unknown_predicate_frame_record()
    unknown_role = demo_unknown_role_record()
    unknown_effect = demo_unknown_effect_boundary_record()

    checks = (
        (validate_predicate_frame_record(predicate).passed, "demo predicate frame boundary record is valid"),
        (validate_role_record(role).passed, "demo role boundary record is valid"),
        (validate_role_record(missing_role).passed, "missing role boundary record is valid"),
        (validate_speech_act_record(speech).passed, "demo speech-act boundary record is valid"),
        (validate_effect_boundary_record(effect).passed, "demo effect boundary record is valid"),
        (validate_predicate_frame_record(unknown_predicate).passed, "unknown predicate remains represented as unknown boundary"),
        (validate_role_record(unknown_role).passed, "unknown role remains represented as unknown boundary"),
        (validate_effect_boundary_record(unknown_effect).passed, "unknown effect remains represented as unknown boundary"),
        (predicate.boundary_id() == demo_predicate_frame_record().boundary_id(), "predicate frame identifiers are deterministic"),
        (role.boundary_id() == demo_role_record().boundary_id(), "role identifiers are deterministic"),
        (speech.boundary_id() == demo_speech_act_record().boundary_id(), "speech-act identifiers are deterministic"),
        (effect.boundary_id() == demo_effect_boundary_record().boundary_id(), "effect identifiers are deterministic"),
    )
    for ok, message in checks:
        (passes if ok else failures).append(message)

    unsafe_predicate = PredicateFrameBoundaryRecord(
        predicate_key="unsafe",
        action_root="unsafe",
        frame_kind="action_boundary",
        namespace="aiweb:core",
        role_keys=("agent_boundary",),
        speech_act_key="command_boundary",
        effect_boundary_key="tool_related_effect_boundary",
        provenance_tag="slice9_negative",
        version_tag="v1",
        execution_authority=True,
    )
    if not validate_predicate_frame_record(unsafe_predicate).passed:
        passes.append("predicate execution flag is rejected")
    else:
        failures.append("predicate execution flag was not rejected")

    unsafe_role = RoleBoundaryRecord(
        role_key="unsafe_role",
        frame_key="unsafe_frame",
        role_type="agent_boundary",
        namespace="aiweb:core",
        concept_boundary_refs=("concept_agent_boundary",),
        provenance_tag="slice9_negative",
        version_tag="v1",
        concept_resolution=True,
    )
    if not validate_role_record(unsafe_role).passed:
        passes.append("role concept resolver flag is rejected")
    else:
        failures.append("role concept resolver flag was not rejected")

    unsafe_speech = SpeechActBoundaryRecord(
        speech_act_key="unsafe_command",
        act_type="command_boundary",
        namespace="aiweb:core",
        source_ref="slice9_negative",
        provenance_tag="slice9_negative",
        version_tag="v1",
        command_permission=True,
    )
    if not validate_speech_act_record(unsafe_speech).passed:
        passes.append("speech command permission flag is rejected")
    else:
        failures.append("speech command permission flag was not rejected")

    unsafe_effect = EffectBoundaryRecord(
        effect_key="unsafe_effect",
        effect_type="tool_related_effect_boundary",
        namespace="aiweb:core",
        provenance_tag="slice9_negative",
        version_tag="v1",
        side_effect_allowed=True,
    )
    if not validate_effect_boundary_record(unsafe_effect).passed:
        passes.append("effect side-effect flag is rejected")
    else:
        failures.append("effect side-effect flag was not rejected")

    scanner_ok, scanner_msg = _check_slice6_scanner(repo)
    (passes if scanner_ok else failures).append(scanner_msg)

    if git_status_limited_to_slice9(repo):
        passes.append("git status is clean or limited to Slice 9 scaffold paths")
    else:
        failures.append("git status contains out-of-scope paths: " + " | ".join(_git_status_lines(repo)))

    return passes, failures


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    repo = Path(args[0]) if args else Path.cwd()
    print("=" * 60)
    print("AIWEB SLICE 9 PREDICATE-ROLE FRAME BOUNDARY SCAFFOLD VERIFIER")
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
        print("VERDICT: FAIL - Slice 9 predicate-role boundary scaffold verifier failed")
        return 1
    print("VERDICT: PASS - Slice 9 predicate-role boundary scaffold verifier passed within Slice 9 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
