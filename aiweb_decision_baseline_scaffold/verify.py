"""Verifier helpers for AI.Web Slice 4 decision/baseline scaffold."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, Tuple

from .baseline import (
    ACCEPTED_BASELINE_STATUS,
    build_accepted_baseline_update,
    sample_accepted_baseline_update,
    validate_accepted_baseline_update,
)
from .decision import (
    NON_PRODUCTION_READY,
    NON_RELEASE_AUTHORIZED,
    build_decision_record,
    sample_accepted_decision,
    validate_decision_record,
)

REQUIRED_RELATIVE_FILES: Tuple[str, ...] = (
    "aiweb_decision_baseline_scaffold/__init__.py",
    "aiweb_decision_baseline_scaffold/decision.py",
    "aiweb_decision_baseline_scaffold/baseline.py",
    "aiweb_decision_baseline_scaffold/verify.py",
    "scripts/test_aiweb_slice04_decision_baseline_scaffold.py",
    "scripts/aiweb_slice04_decision_baseline_verify.py",
    "scripts/README_aiweb_slice04_decision_baseline_scaffold.md",
)

ALLOWED_STATUS_PREFIXES: Tuple[str, ...] = (
    "aiweb_decision_baseline_scaffold/",
    "scripts/test_aiweb_slice04_decision_baseline_scaffold.py",
    "scripts/aiweb_slice04_decision_baseline_verify.py",
    "scripts/README_aiweb_slice04_decision_baseline_scaffold.md",
)

FORBIDDEN_IMPORT_ROOTS: Tuple[str, ...] = (
    "chromadb",
    "openai",
    "langchain",
    "llama_index",
    "faiss",
    "torch",
    "tensorflow",
    "transformers",
    "sentence_transformers",
    "sklearn",
    "requests",
    "httpx",
    "aiohttp",
    "socket",
)


def required_files_present(repo: Path) -> Tuple[str, ...]:
    """Return required relative files that are missing."""

    return tuple(rel for rel in REQUIRED_RELATIVE_FILES if not (repo / rel).is_file())


def syntax_error_for_file(path: Path) -> str:
    """Return an empty string when Python syntax is valid."""

    try:
        ast.parse(path.read_text())
    except SyntaxError as exc:
        return f"{path}: {exc}"
    return ""


def forbidden_imports_in_file(path: Path) -> Tuple[str, ...]:
    """Return forbidden active imports from a Python source file."""

    tree = ast.parse(path.read_text())
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in FORBIDDEN_IMPORT_ROOTS:
                    found.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root = module.split(".", 1)[0]
            if root in FORBIDDEN_IMPORT_ROOTS:
                found.append(module)
    return tuple(found)


def git_status_is_slice04_only(lines: Iterable[str]) -> Tuple[str, ...]:
    """Return git status lines outside the Slice 4 scaffold scope."""

    unexpected = []
    for raw in lines:
        line = raw.rstrip()
        if not line:
            continue
        path = line[3:] if len(line) > 3 else line
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        if not any(path.startswith(prefix) for prefix in ALLOWED_STATUS_PREFIXES):
            unexpected.append(line)
    return tuple(unexpected)


def decision_samples_ok() -> bool:
    """Return True when valid decision samples pass."""

    accepted = sample_accepted_decision()
    if not validate_decision_record(accepted).ok:
        return False

    held = build_decision_record(
        record_id="AIWEB-DECISION-HELD-SAMPLE",
        slice_id="4",
        slice_name="Decision Record and Accepted Baseline Update Scaffold",
        decision_status="held",
        decision_scope="held sample scope",
        source_head="90d3b168218e04d60c460d6adf6dd3f421ced0cc",
        decision_owner_status="held",
        decision_reasons=("required evidence missing",),
    )
    if not validate_decision_record(held).ok:
        return False

    rejected = build_decision_record(
        record_id="AIWEB-DECISION-REJECTED-SAMPLE",
        slice_id="4",
        slice_name="Decision Record and Accepted Baseline Update Scaffold",
        decision_status="rejected",
        decision_scope="rejected sample scope",
        source_head="90d3b168218e04d60c460d6adf6dd3f421ced0cc",
        decision_owner_status="rejected",
        decision_reasons=("acceptance requirements failed",),
    )
    return validate_decision_record(rejected).ok


def baseline_samples_ok() -> bool:
    """Return True when valid baseline samples pass."""

    accepted = sample_accepted_decision()
    baseline = sample_accepted_baseline_update(accepted)
    return validate_accepted_baseline_update(baseline, accepted).ok


def unsafe_samples_rejected() -> bool:
    """Return True when unsafe overclaim samples are rejected."""

    accepted = sample_accepted_decision()

    missing_result = build_decision_record(
        record_id="AIWEB-DECISION-BAD-MISSING-RESULT",
        slice_id="4",
        slice_name="Decision Record and Accepted Baseline Update Scaffold",
        decision_status="accepted_within_scope",
        decision_scope="bad sample",
        source_head=accepted.source_head,
        result_packet="",
        result_packet_sha256=accepted.result_packet_sha256,
        inspection_record=accepted.inspection_record,
        verifier_output=accepted.verifier_output,
        behavior_test_output=accepted.behavior_test_output,
        decision_owner_status="accepted_within_scope",
        public_claim_boundary=True,
    )
    if validate_decision_record(missing_result).ok:
        return False

    missing_owner = build_decision_record(
        record_id="AIWEB-DECISION-BAD-MISSING-OWNER",
        slice_id="4",
        slice_name="Decision Record and Accepted Baseline Update Scaffold",
        decision_status="accepted_within_scope",
        decision_scope="bad sample",
        source_head=accepted.source_head,
        result_packet=accepted.result_packet,
        result_packet_sha256=accepted.result_packet_sha256,
        inspection_record=accepted.inspection_record,
        verifier_output=accepted.verifier_output,
        behavior_test_output=accepted.behavior_test_output,
        decision_owner_status="",
        public_claim_boundary=True,
    )
    if validate_decision_record(missing_owner).ok:
        return False

    bad_baseline = build_accepted_baseline_update(
        baseline_id="AIWEB-BASELINE-BAD-CURRENT-ONLY",
        implementation_line="Forge/RMC language-core implementation line",
        baseline_status="current_baseline",
        accepted_source_head=accepted.source_head,
        decision_record_id=accepted.record_id,
        result_packet=accepted.result_packet,
        result_packet_sha256=accepted.result_packet_sha256,
        accepted_scope="bad sample",
        public_claim_boundary=True,
        next_allowed_gate="Slice 5 Narrow Source Authority Packet",
    )
    if validate_accepted_baseline_update(bad_baseline, accepted).ok:
        return False

    for key in (
        "gp014_supersession_claim",
        "gp014_replacement_claim",
        "gp015_repair_claim",
        "gp015r1_install_claim",
        "production_readiness_claim",
        "release_authorization_claim",
        "public_delivery_claim",
        "model_vector_llm_authority_claim",
        "memory_authority_claim",
        "evidence_authority_claim",
        "corpus_authority_claim",
        "external_resource_authority_claim",
        "ui_authority_claim",
        "delivery_authority_claim",
        "action_routing_authority_claim",
    ):
        bad = build_decision_record(
            record_id=f"AIWEB-DECISION-BAD-{key}",
            slice_id="4",
            slice_name="Decision Record and Accepted Baseline Update Scaffold",
            decision_status="accepted_within_scope",
            decision_scope="bad sample",
            source_head=accepted.source_head,
            result_packet=accepted.result_packet,
            result_packet_sha256=accepted.result_packet_sha256,
            inspection_record=accepted.inspection_record,
            verifier_output=accepted.verifier_output,
            behavior_test_output=accepted.behavior_test_output,
            decision_owner_status="accepted_within_scope",
            public_claim_boundary=True,
            authority_claims={key: True},
        )
        if validate_decision_record(bad).ok:
            return False

    bad_production = build_decision_record(
        record_id="AIWEB-DECISION-BAD-PRODUCTION-STATUS",
        slice_id="4",
        slice_name="Decision Record and Accepted Baseline Update Scaffold",
        decision_status="accepted_within_scope",
        decision_scope="bad sample",
        source_head=accepted.source_head,
        result_packet=accepted.result_packet,
        result_packet_sha256=accepted.result_packet_sha256,
        inspection_record=accepted.inspection_record,
        verifier_output=accepted.verifier_output,
        behavior_test_output=accepted.behavior_test_output,
        decision_owner_status="accepted_within_scope",
        public_claim_boundary=True,
        production_readiness_status="production_ready",
    )
    if validate_decision_record(bad_production).ok:
        return False

    bad_release = build_decision_record(
        record_id="AIWEB-DECISION-BAD-RELEASE-STATUS",
        slice_id="4",
        slice_name="Decision Record and Accepted Baseline Update Scaffold",
        decision_status="accepted_within_scope",
        decision_scope="bad sample",
        source_head=accepted.source_head,
        result_packet=accepted.result_packet,
        result_packet_sha256=accepted.result_packet_sha256,
        inspection_record=accepted.inspection_record,
        verifier_output=accepted.verifier_output,
        behavior_test_output=accepted.behavior_test_output,
        decision_owner_status="accepted_within_scope",
        public_claim_boundary=True,
        release_status="release_authorized",
    )
    if validate_decision_record(bad_release).ok:
        return False

    return True


def scaffold_samples_ok() -> bool:
    """Return True only when all verifier helper samples behave as expected."""

    return decision_samples_ok() and baseline_samples_ok() and unsafe_samples_rejected()


def accepted_baseline_status_is_exact() -> bool:
    """Return True when the baseline status constant has the required exact value."""

    return ACCEPTED_BASELINE_STATUS == "accepted_baseline_update"


def non_release_non_production_constants_are_exact() -> bool:
    """Return True when explicit non-release and non-production constants are present."""

    return NON_PRODUCTION_READY == "not_production_ready" and NON_RELEASE_AUTHORIZED == "not_release_authorized"
