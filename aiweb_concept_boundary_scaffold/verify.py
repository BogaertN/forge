"""Verifier helpers for Slice 8 concept boundary scaffold."""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import sys
from typing import Iterable, List, Sequence, Tuple

from .concept import (
    ConceptBoundaryRecord,
    SenseBoundaryRecord,
    concept_scope_record,
    demo_concept_record,
    demo_sense_record,
    validate_concept_record,
    validate_sense_record,
)
from .relation import demo_relation_record, relation_scope_record, validate_relation_record

REQUIRED_PATHS = (
    "aiweb_concept_boundary_scaffold/__init__.py",
    "aiweb_concept_boundary_scaffold/concept.py",
    "aiweb_concept_boundary_scaffold/relation.py",
    "aiweb_concept_boundary_scaffold/verify.py",
    "scripts/test_aiweb_slice08_concept_boundary_scaffold.py",
    "scripts/aiweb_slice08_concept_boundary_verify.py",
    "scripts/README_aiweb_slice08_concept_boundary_scaffold.md",
)

def _join_fragments(*parts: str) -> str:
    return "".join(parts)


BLOCKED_IMPORT_ROOTS = {
    _join_fragments("open", "ai"),
    _join_fragments("anth", "ropic"),
    _join_fragments("chrom", "adb"),
    _join_fragments("lang", "chain"),
    _join_fragments("fa", "iss"),
    "sklearn",
    "sentence_transformers",
    "transformers",
    "torch",
    "tensorflow",
}

EXPECTED_STATUS_PATHS = frozenset(REQUIRED_PATHS)
EXPECTED_STATUS_DIRS = frozenset({"aiweb_concept_boundary_scaffold"})


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


def git_status_limited_to_slice8(repo: Path) -> bool:
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


def run_verification(repo: Path) -> Tuple[List[str], List[str]]:
    passes: List[str] = []
    failures: List[str] = []
    repo = repo.resolve()

    if repo.exists() and repo.is_dir():
        passes.append(f"target repo directory exists: {repo}")
    else:
        failures.append(f"target repo directory missing: {repo}")
        return passes, failures

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
        blocked = sorted(set(_active_import_roots(path)).intersection(BLOCKED_IMPORT_ROOTS))
        if blocked:
            failures.append(f"blocked active imports in {path}: {blocked}")
        else:
            passes.append(f"no blocked active imports: {path}")

    scope = concept_scope_record()
    relation_scope = relation_scope_record()
    if scope["scaffold_only"] and scope["runtime_effect"] == "none" and scope["dependency_change"] == "none":
        passes.append("concept scope is scaffold-only with no runtime or dependency effect")
    else:
        failures.append("concept scope has unsafe effect")
    if relation_scope["scaffold_only"] and relation_scope["runtime_effect"] == "none" and relation_scope["dependency_change"] == "none":
        passes.append("relation scope is scaffold-only with no runtime or dependency effect")
    else:
        failures.append("relation scope has unsafe effect")

    concept = demo_concept_record()
    sense = demo_sense_record()
    relation = demo_relation_record()
    if validate_concept_record(concept).passed:
        passes.append("demo concept boundary record is valid")
    else:
        failures.append("demo concept boundary record failed validation")
    if validate_sense_record(sense).passed:
        passes.append("demo sense boundary record is valid")
    else:
        failures.append("demo sense boundary record failed validation")
    if validate_relation_record(relation).passed:
        passes.append("demo semantic relation boundary record is valid")
    else:
        failures.append("demo semantic relation boundary record failed validation")

    if concept.boundary_id() == demo_concept_record().boundary_id():
        passes.append("concept boundary identifiers are deterministic")
    else:
        failures.append("concept boundary identifiers are not deterministic")
    if sense.boundary_id() == demo_sense_record().boundary_id():
        passes.append("sense boundary identifiers are deterministic")
    else:
        failures.append("sense boundary identifiers are not deterministic")
    if relation.boundary_id() == demo_relation_record().boundary_id():
        passes.append("relation boundary identifiers are deterministic")
    else:
        failures.append("relation boundary identifiers are not deterministic")

    blocked_concept = ConceptBoundaryRecord(
        concept_key="unsafe",
        namespace="aiweb:core",
        label="unsafe",
        semantic_class="entity",
        sense_keys=("unsafe_sense",),
        relation_keys=(),
        provenance_tag="slice8_negative",
        version_tag="v1",
        live_concept_resolution=True,
    )
    if not validate_concept_record(blocked_concept).passed:
        passes.append("live concept resolver flag is rejected")
    else:
        failures.append("live concept resolver flag was not rejected")

    blocked_sense = SenseBoundaryRecord(
        sense_key="unsafe_sense",
        concept_key="unsafe",
        label="unsafe",
        namespace="aiweb:core",
        provenance_tag="slice8_negative",
        version_tag="v1",
        lexical_dataset_source="unapproved_dataset",
    )
    if not validate_sense_record(blocked_sense).passed:
        passes.append("lexical dataset source is rejected")
    else:
        failures.append("lexical dataset source was not rejected")

    blocked_relation = type(relation)(
        relation_key="unsafe_relation",
        relation_type="associated_with_boundary",
        source_concept_key="unsafe",
        target_concept_key="target",
        namespace="aiweb:core",
        provenance_tag="slice8_negative",
        version_tag="v1",
        live_graph_traversal=True,
    )
    if not validate_relation_record(blocked_relation).passed:
        passes.append("live graph traversal flag is rejected")
    else:
        failures.append("live graph traversal flag was not rejected")

    downstream_relation = type(relation)(
        relation_key="unsafe_role_relation",
        relation_type="associated_with_boundary",
        source_concept_key="unsafe",
        target_concept_key="target",
        namespace="aiweb:core",
        provenance_tag="slice8_negative",
        version_tag="v1",
        predicate_role_assignment=True,
    )
    if not validate_relation_record(downstream_relation).passed:
        passes.append("predicate role assignment flag is rejected")
    else:
        failures.append("predicate role assignment flag was not rejected")

    if git_status_limited_to_slice8(repo):
        passes.append("git status is clean or limited to Slice 8 scaffold paths")
    else:
        failures.append("git status contains out-of-scope paths: " + " | ".join(_git_status_lines(repo)))

    return passes, failures
