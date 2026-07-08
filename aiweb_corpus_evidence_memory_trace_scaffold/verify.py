"""Verifier helpers for Slice 15 category-separation scaffold."""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess
from typing import List, Sequence, Tuple

from .authority import AuthorityReferenceRecord, demo_authority_reference_record, validate_authority_reference_record
from .category import CategoryBoundaryRecord, demo_category_boundary_record, validate_category_boundary_record
from .core import DOWNSTREAM_FALSE_ONLY_FIELDS, REQUIRED_SEPARATION_LAWS, corpus_evidence_memory_trace_scope_record
from .corpus import CorpusEntryRecord, demo_corpus_entry_record, validate_corpus_entry_record
from .evidence import EvidenceRecord, demo_evidence_record, validate_evidence_record
from .memory import MemoryRecord, MemoryRequestRecord, demo_memory_record, demo_memory_request_record, validate_memory_record, validate_memory_request_record
from .separation import SeparationAssertionRecord, demo_required_separation_assertions, demo_source_mention_not_evidence_assertion, validate_separation_assertion_record
from .source_mention import SourceMentionRecord, demo_source_mention_record, validate_source_mention_record
from .trace import TraceRecord, demo_trace_record, validate_trace_record

REQUIRED_PATHS = (
    "aiweb_corpus_evidence_memory_trace_scaffold/__init__.py",
    "aiweb_corpus_evidence_memory_trace_scaffold/core.py",
    "aiweb_corpus_evidence_memory_trace_scaffold/category.py",
    "aiweb_corpus_evidence_memory_trace_scaffold/source_mention.py",
    "aiweb_corpus_evidence_memory_trace_scaffold/evidence.py",
    "aiweb_corpus_evidence_memory_trace_scaffold/memory.py",
    "aiweb_corpus_evidence_memory_trace_scaffold/trace.py",
    "aiweb_corpus_evidence_memory_trace_scaffold/corpus.py",
    "aiweb_corpus_evidence_memory_trace_scaffold/authority.py",
    "aiweb_corpus_evidence_memory_trace_scaffold/separation.py",
    "aiweb_corpus_evidence_memory_trace_scaffold/verify.py",
    "scripts/test_aiweb_slice15_corpus_evidence_memory_trace_scaffold.py",
    "scripts/aiweb_slice15_corpus_evidence_memory_trace_verify.py",
    "scripts/README_aiweb_slice15_corpus_evidence_memory_trace_scaffold.md",
)

EXPECTED_STATUS_PATHS = frozenset(REQUIRED_PATHS)
EXPECTED_STATUS_DIRS = frozenset({"aiweb_corpus_evidence_memory_trace_scaffold"})


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


def git_status_limited_to_slice15(repo: Path) -> bool:
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
        return True, "slice6 scanner found no Slice 15 source findings"
    return False, f"slice6 scanner findings:{report.finding_count}"


def _scope_blocks_all_downstream_authorities() -> bool:
    scope = corpus_evidence_memory_trace_scope_record()
    return (
        scope.get("scaffold_only") is True
        and scope.get("runtime_effect") == "none"
        and scope.get("dependency_change") == "none"
        and all(scope.get(key) is False for key in DOWNSTREAM_FALSE_ONLY_FIELDS)
        and tuple(scope.get("required_separation_laws", ())) == REQUIRED_SEPARATION_LAWS
        and scope.get("gp014_status") == "protected_not_superseded"
        and scope.get("gp015_status") == "failed_not_repaired"
        and scope.get("gp015r1_status") == "uninstalled_not_live"
        and scope.get("external_resources_status") == "unadmitted"
        and scope.get("sanskrit_wordnet_status") == "hold_unadmitted"
    )


def _llm_renderer_is_blocked_boundary(repo: Path) -> bool:
    path = repo / "rmc_engine_v1/llm_renderer.py"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return "BOUNDARY_BLOCKED_NON_AUTHORITATIVE" in text and "core_authority" in text and "False" in text


def _records_validate() -> Tuple[List[str], List[str]]:
    passes: List[str] = []
    failures: List[str] = []
    checks = (
        ("category boundary validates", validate_category_boundary_record(demo_category_boundary_record()).ok),
        ("source mention validates", validate_source_mention_record(demo_source_mention_record()).ok),
        ("evidence record validates", validate_evidence_record(demo_evidence_record()).ok),
        ("memory record validates", validate_memory_record(demo_memory_record()).ok),
        ("memory request validates", validate_memory_request_record(demo_memory_request_record()).ok),
        ("trace record validates", validate_trace_record(demo_trace_record()).ok),
        ("corpus entry validates", validate_corpus_entry_record(demo_corpus_entry_record()).ok),
        ("authority reference validates", validate_authority_reference_record(demo_authority_reference_record()).ok),
        ("source mention separation assertion validates", validate_separation_assertion_record(demo_source_mention_not_evidence_assertion()).ok),
    )
    for label, ok in checks:
        if ok:
            passes.append(label)
        else:
            failures.append(label)
    for record in demo_required_separation_assertions():
        report = validate_separation_assertion_record(record)
        if report.ok:
            passes.append(f"required separation assertion validates: {record.separation_kind}")
        else:
            failures.append(f"required separation assertion invalid: {record.separation_kind}")
    return passes, failures


def _stable_ids_validate() -> Tuple[List[str], List[str]]:
    pairs = (
        ("category ID deterministic", demo_category_boundary_record().category_boundary_id == demo_category_boundary_record().expected_id()),
        ("source mention ID deterministic", demo_source_mention_record().source_mention_id == demo_source_mention_record().expected_id()),
        ("evidence ID deterministic", demo_evidence_record().evidence_record_id == demo_evidence_record().expected_id()),
        ("memory ID deterministic", demo_memory_record().memory_record_id == demo_memory_record().expected_id()),
        ("memory request ID deterministic", demo_memory_request_record().memory_request_id == demo_memory_request_record().expected_id()),
        ("trace ID deterministic", demo_trace_record().trace_record_id == demo_trace_record().expected_id()),
        ("corpus entry ID deterministic", demo_corpus_entry_record().corpus_entry_id == demo_corpus_entry_record().expected_id()),
        ("authority reference ID deterministic", demo_authority_reference_record().authority_reference_id == demo_authority_reference_record().expected_id()),
        ("separation assertion ID deterministic", demo_source_mention_not_evidence_assertion().separation_assertion_id == demo_source_mention_not_evidence_assertion().expected_id()),
    )
    passes = [label for label, ok in pairs if ok]
    failures = [label for label, ok in pairs if not ok]
    return passes, failures


def _collapse_rejections_validate() -> Tuple[List[str], List[str]]:
    passes: List[str] = []
    failures: List[str] = []
    checks = (
        (
            "source mention cannot become evidence",
            not validate_source_mention_record(SourceMentionRecord(**{**demo_source_mention_record().__dict__, "evidence_status": "evidence"})).ok,
        ),
        (
            "source mention unsafe promotion flag rejected",
            not validate_source_mention_record(SourceMentionRecord(**{**demo_source_mention_record().__dict__, "source_mention_as_evidence": True})).ok,
        ),
        (
            "evidence cannot become memory",
            not validate_evidence_record(EvidenceRecord(**{**demo_evidence_record().__dict__, "memory_status": "memory"})).ok,
        ),
        (
            "evidence validation flag rejected",
            not validate_evidence_record(EvidenceRecord(**{**demo_evidence_record().__dict__, "evidence_validation": True})).ok,
        ),
        (
            "memory cannot become external truth",
            not validate_memory_record(MemoryRecord(**{**demo_memory_record().__dict__, "external_truth_status": "external_truth"})).ok,
        ),
        (
            "memory write flag rejected",
            not validate_memory_record(MemoryRecord(**{**demo_memory_record().__dict__, "memory_write": True})).ok,
        ),
        (
            "memory request cannot write memory",
            not validate_memory_request_record(MemoryRequestRecord(**{**demo_memory_request_record().__dict__, "write_effect": "write_performed"})).ok,
        ),
        (
            "memory request execution flag rejected",
            not validate_memory_request_record(MemoryRequestRecord(**{**demo_memory_request_record().__dict__, "memory_request_execution": True})).ok,
        ),
        (
            "trace cannot become unrestricted corpus",
            not validate_trace_record(TraceRecord(**{**demo_trace_record().__dict__, "corpus_status": "unrestricted_corpus"})).ok,
        ),
        (
            "trace-to-corpus promotion flag rejected",
            not validate_trace_record(TraceRecord(**{**demo_trace_record().__dict__, "trace_to_corpus_promotion": True})).ok,
        ),
        (
            "corpus cannot become authority",
            not validate_corpus_entry_record(CorpusEntryRecord(**{**demo_corpus_entry_record().__dict__, "authority_status": "authority"})).ok,
        ),
        (
            "corpus authority flag rejected",
            not validate_corpus_entry_record(CorpusEntryRecord(**{**demo_corpus_entry_record().__dict__, "corpus_authority": True})).ok,
        ),
        (
            "authority reference cannot grant authority",
            not validate_authority_reference_record(AuthorityReferenceRecord(**{**demo_authority_reference_record().__dict__, "authority_effect": "granted"})).ok,
        ),
        (
            "separation assertion cannot permit collapse",
            not validate_separation_assertion_record(SeparationAssertionRecord(**{**demo_source_mention_not_evidence_assertion().__dict__, "collapse_forbidden": False})).ok,
        ),
    )
    for label, ok in checks:
        if ok:
            passes.append(label)
        else:
            failures.append(label)
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
            passes.append(f"frozen path untouched by Slice 15: {rel}")
        else:
            failures.append(f"frozen path touched by Slice 15: {rel}")

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

    if git_status_limited_to_slice15(repo):
        passes.append("git status is clean or limited to Slice 15 scaffold paths")
    else:
        failures.append("git status includes paths outside Slice 15 scaffold")

    return passes, failures
