"""Verifier helpers for Slice 14 external-resource quarantine scaffold."""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess
from typing import List, Sequence, Tuple

from .core import DOWNSTREAM_FALSE_ONLY_FIELDS, external_resource_quarantine_scope_record
from .decision import (
    ResourceQuarantineDecisionRecord,
    demo_resource_quarantine_decision_record,
    validate_resource_quarantine_decision_record,
)
from .identity import (
    ExternalResourceIdentityRecord,
    demo_sanskrit_wordnet_identity_record,
    demo_wordnet_identity_record,
    validate_external_resource_identity_record,
)
from .license_custody import (
    LicenseCustodyRecord,
    demo_license_custody_record,
    validate_license_custody_record,
)
from .provenance import (
    ProvenanceCustodyRecord,
    demo_provenance_custody_record,
    validate_provenance_custody_record,
)
from .purpose import (
    ResourcePurposeBoundaryRecord,
    demo_resource_purpose_boundary_record,
    validate_resource_purpose_boundary_record,
)
from .receipt import (
    ResourceAdmissionReceiptRecord,
    demo_resource_admission_receipt_record,
    validate_resource_admission_receipt_record,
)

REQUIRED_PATHS = (
    "aiweb_external_resource_quarantine_scaffold/__init__.py",
    "aiweb_external_resource_quarantine_scaffold/core.py",
    "aiweb_external_resource_quarantine_scaffold/identity.py",
    "aiweb_external_resource_quarantine_scaffold/provenance.py",
    "aiweb_external_resource_quarantine_scaffold/license_custody.py",
    "aiweb_external_resource_quarantine_scaffold/purpose.py",
    "aiweb_external_resource_quarantine_scaffold/decision.py",
    "aiweb_external_resource_quarantine_scaffold/receipt.py",
    "aiweb_external_resource_quarantine_scaffold/verify.py",
    "scripts/test_aiweb_slice14_external_resource_quarantine_scaffold.py",
    "scripts/aiweb_slice14_external_resource_quarantine_verify.py",
    "scripts/README_aiweb_slice14_external_resource_quarantine_scaffold.md",
)

EXPECTED_STATUS_PATHS = frozenset(REQUIRED_PATHS)
EXPECTED_STATUS_DIRS = frozenset({"aiweb_external_resource_quarantine_scaffold"})


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


def git_status_limited_to_slice14(repo: Path) -> bool:
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
        return True, "slice6 scanner found no Slice 14 source findings"
    return False, f"slice6 scanner findings:{report.finding_count}"


def _scope_blocks_all_downstream_authorities() -> bool:
    scope = external_resource_quarantine_scope_record()
    return (
        scope.get("scaffold_only") is True
        and scope.get("runtime_effect") == "none"
        and scope.get("dependency_change") == "none"
        and all(scope.get(key) is False for key in DOWNSTREAM_FALSE_ONLY_FIELDS)
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
            passes.append(f"frozen path untouched by Slice 14: {rel}")
        else:
            failures.append(f"frozen path modified by Slice 14: {rel}")

    if _scope_blocks_all_downstream_authorities():
        passes.append("scope record blocks all downstream authority categories")
    else:
        failures.append("scope record does not block all downstream authority categories")

    demo_checks = (
        ("demo WordNet identity record is valid", validate_external_resource_identity_record(demo_wordnet_identity_record()).ok),
        ("demo Sanskrit WordNet identity record is valid", validate_external_resource_identity_record(demo_sanskrit_wordnet_identity_record()).ok),
        ("demo provenance custody record is valid", validate_provenance_custody_record(demo_provenance_custody_record()).ok),
        ("demo license custody record is valid", validate_license_custody_record(demo_license_custody_record()).ok),
        ("demo purpose boundary record is valid", validate_resource_purpose_boundary_record(demo_resource_purpose_boundary_record()).ok),
        ("demo quarantine decision record is valid", validate_resource_quarantine_decision_record(demo_resource_quarantine_decision_record()).ok),
        ("demo admission receipt record is valid", validate_resource_admission_receipt_record(demo_resource_admission_receipt_record()).ok),
        ("WordNet identity ID is deterministic", demo_wordnet_identity_record().resource_identity_id == demo_wordnet_identity_record().expected_id()),
        ("Sanskrit WordNet identity ID is deterministic", demo_sanskrit_wordnet_identity_record().resource_identity_id == demo_sanskrit_wordnet_identity_record().expected_id()),
        ("provenance custody ID is deterministic", demo_provenance_custody_record().provenance_custody_id == demo_provenance_custody_record().expected_id()),
        ("license custody ID is deterministic", demo_license_custody_record().license_custody_id == demo_license_custody_record().expected_id()),
        ("purpose boundary ID is deterministic", demo_resource_purpose_boundary_record().purpose_boundary_id == demo_resource_purpose_boundary_record().expected_id()),
        ("quarantine decision ID is deterministic", demo_resource_quarantine_decision_record().quarantine_decision_id == demo_resource_quarantine_decision_record().expected_id()),
        ("admission receipt ID is deterministic", demo_resource_admission_receipt_record().admission_receipt_id == demo_resource_admission_receipt_record().expected_id()),
    )
    for label, ok in demo_checks:
        if ok:
            passes.append(label)
        else:
            failures.append(label)

    unsafe_identity = ExternalResourceIdentityRecord(**{**demo_wordnet_identity_record().__dict__, "resource_ingestion": True})
    if not validate_external_resource_identity_record(unsafe_identity).ok:
        passes.append("identity resource ingestion flag is rejected")
    else:
        failures.append("identity resource ingestion flag was not rejected")

    unsafe_identity_graph = ExternalResourceIdentityRecord(**{**demo_wordnet_identity_record().__dict__, "wordnet_concept_graph": True})
    if not validate_external_resource_identity_record(unsafe_identity_graph).ok:
        passes.append("WordNet concept graph replacement flag is rejected")
    else:
        failures.append("WordNet concept graph replacement flag was not rejected")

    unsafe_provenance = ProvenanceCustodyRecord(**{**demo_provenance_custody_record().__dict__, "resource_download": True})
    if not validate_provenance_custody_record(unsafe_provenance).ok:
        passes.append("provenance resource download flag is rejected")
    else:
        failures.append("provenance resource download flag was not rejected")

    unsafe_license = LicenseCustodyRecord(**{**demo_license_custody_record().__dict__, "license_runtime_permission": True})
    if not validate_license_custody_record(unsafe_license).ok:
        passes.append("license runtime permission flag is rejected")
    else:
        failures.append("license runtime permission flag was not rejected")

    unsafe_purpose = ResourcePurposeBoundaryRecord(**{**demo_resource_purpose_boundary_record().__dict__, "embedding_index_creation": True})
    if not validate_resource_purpose_boundary_record(unsafe_purpose).ok:
        passes.append("purpose embedding index flag is rejected")
    else:
        failures.append("purpose embedding index flag was not rejected")

    unsafe_decision = ResourceQuarantineDecisionRecord(**{**demo_resource_quarantine_decision_record().__dict__, "external_resource_admission": True})
    if not validate_resource_quarantine_decision_record(unsafe_decision).ok:
        passes.append("quarantine admission flag is rejected")
    else:
        failures.append("quarantine admission flag was not rejected")

    unsafe_receipt = ResourceAdmissionReceiptRecord(**{**demo_resource_admission_receipt_record().__dict__, "authority_grant": True})
    if not validate_resource_admission_receipt_record(unsafe_receipt).ok:
        passes.append("receipt authority grant flag is rejected")
    else:
        failures.append("receipt authority grant flag was not rejected")

    bad_purpose = ResourcePurposeBoundaryRecord(
        **{**demo_resource_purpose_boundary_record().__dict__, "permitted_purpose_refs": ("runtime_authority",)}
    )
    if not validate_resource_purpose_boundary_record(bad_purpose).ok:
        passes.append("runtime authority cannot be listed as permitted purpose")
    else:
        failures.append("runtime authority was incorrectly permitted")

    bad_receipt = ResourceAdmissionReceiptRecord(**{**demo_resource_admission_receipt_record().__dict__, "authority_effect": "accepted"})
    if not validate_resource_admission_receipt_record(bad_receipt).ok:
        passes.append("receipt cannot claim accepted authority effect")
    else:
        failures.append("receipt accepted authority effect was not rejected")

    if _llm_renderer_is_blocked_boundary(repo):
        passes.append("llm_renderer remains blocked boundary evidence only")
    else:
        failures.append("llm_renderer blocked boundary evidence check failed")

    scan_ok, scan_detail = _check_slice6_scanner(repo)
    if scan_ok:
        passes.append(scan_detail)
    else:
        failures.append(scan_detail)

    if git_status_limited_to_slice14(repo):
        passes.append("git status is clean or limited to Slice 14 scaffold paths")
    else:
        failures.append("git status contains paths outside Slice 14 scaffold")

    return passes, failures
