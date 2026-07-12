#!/usr/bin/env python3
"""Tests for Slice 21 read-only inspection surface boundary scaffold."""

from __future__ import annotations

import ast
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from aiweb_read_only_inspection_surface_scaffold.authority import build_authority_separation_record
from aiweb_read_only_inspection_surface_scaffold.boundary import check_boundary_integrity
from aiweb_read_only_inspection_surface_scaffold.core import (
    ALLOWED_INSPECTION_SUBJECTS,
    DOWNSTREAM_FALSE_ONLY_FIELDS,
    REQUIRED_BOUNDARY_LAWS,
    build_inspection_surface_record,
    stable_record_id,
)
from aiweb_read_only_inspection_surface_scaffold.receipt import build_receipt
from aiweb_read_only_inspection_surface_scaffold.verify import EXPECTED_PAYLOAD_FILES, verify_slice21_boundary

PROHIBITED_RUNTIME_FRAGMENTS = (
    "shell" + "=True",
    "os." + "system(",
    "socket" + ".",
    "requests" + ".",
    "httpx" + ".",
    "urllib" + ".request",
    "smtplib" + ".",
    "send" + "_email(",
    "send" + "_draft(",
    "forward" + "_emails(",
    "create" + "_event(",
    "update" + "_event(",
    "delete" + "_event(",
    "gmail" + ".",
    "gcal" + ".",
)


def test_inspection_subjects_are_exact_and_reference_only() -> None:
    record = build_inspection_surface_record()
    assert tuple(subject.key for subject in record.inspection_subjects) == ALLOWED_INSPECTION_SUBJECTS
    assert record.subject_count == len(ALLOWED_INSPECTION_SUBJECTS)
    for subject in record.inspection_subjects:
        assert subject.visible is True
        assert subject.reference_only is True
        assert subject.authority_role == "inspection_visibility_only_not_runtime_authority"
        assert subject.mutation_allowed is False
        assert subject.acceptance_effect is False
        assert subject.runtime_effect is False
        assert subject.proof_effect is False


def test_boundary_laws_and_negative_authority_flags_are_locked() -> None:
    record = build_inspection_surface_record()
    assert tuple(record.boundary_laws) == REQUIRED_BOUNDARY_LAWS
    assert "read_only_inspection_is_not_runtime_authority" in record.boundary_laws
    assert "api_visibility_is_not_acceptance" in record.boundary_laws
    assert "ui_visibility_is_not_proof" in record.boundary_laws
    assert "inspection_surface_does_not_widen_scope" in record.boundary_laws
    assert "inspection_surface_does_not_create_acceptance" in record.boundary_laws
    assert "inspection_surface_does_not_route_tools" in record.boundary_laws
    assert "inspection_surface_does_not_deliver_output" in record.boundary_laws
    assert "inspection_surface_does_not_call_llm" in record.boundary_laws
    assert "inspection_surface_does_not_wrap_or_call_gp014" in record.boundary_laws
    assert "inspection_surface_does_not_repair_gp015" in record.boundary_laws
    assert tuple(flag.key for flag in record.negative_authority_flags) == DOWNSTREAM_FALSE_ONLY_FIELDS
    for flag in record.negative_authority_flags:
        assert flag.value is False, flag.key
    assert record.negative_authority_flag_count == len(DOWNSTREAM_FALSE_ONLY_FIELDS)


def test_no_live_integration_or_runtime_effect_is_authorized() -> None:
    record = build_inspection_surface_record()
    assert record.runtime_effect == "none"
    assert record.dependency_change == "none"
    assert record.integration_state == "boundary_scaffold_only_not_registered_as_live_api"
    assert record.inspection_is_read_only is True
    assert record.route_registration_authorized is False
    assert record.ui_integration_authorized is False
    assert record.config_mutation_authorized is False
    assert record.live_api_authorized is False


def test_authority_separation_grants_nothing_downstream() -> None:
    authority = build_authority_separation_record()
    assert authority.read_only_inspection_required is True
    assert authority.mutation_forbidden is True
    assert authority.acceptance_creation_forbidden is True
    assert authority.accepted_scope_widening_forbidden is True
    assert authority.candidate_promotion_forbidden is True
    assert authority.memory_write_forbidden is True
    assert authority.tool_routing_forbidden is True
    assert authority.tool_invocation_forbidden is True
    assert authority.delivery_forbidden is True
    assert authority.action_execution_forbidden is True
    assert authority.external_resource_admission_forbidden is True
    assert authority.model_vector_retrieval_rag_authority_forbidden is True
    assert authority.ui_authority_forbidden is True
    assert authority.this_scaffold_grants_runtime_authority is False
    assert authority.this_scaffold_grants_acceptance_authority is False
    assert authority.this_scaffold_grants_permission is False
    assert authority.this_scaffold_registers_routes is False
    assert authority.this_scaffold_modifies_config is False
    assert authority.this_scaffold_integrates_ui is False


def test_boundary_integrity_receipt_and_source_only_verifier_pass() -> None:
    boundary = check_boundary_integrity()
    assert boundary.passed, boundary.failures
    receipt = build_receipt()
    assert receipt.verdict == "PASS"
    assert receipt.repository_effect == "adds_read_only_inspection_boundary_records_only"
    assert receipt.runtime_effect == "no_runtime_authority_no_state_change_no_memory_write_no_tool_route_no_delivery"
    assert receipt.production_effect == "no_live_api_no_route_registration_no_ui_no_config_change_no_deployment"
    assert len(receipt.receipt_sha256) == 64
    verification = verify_slice21_boundary(REPO, require_git_context=False)
    assert verification.passed, verification.failures
    assert verification.context_label == "git_context_not_required_for_source_behavior_test"


def test_stable_record_ids_are_deterministic() -> None:
    first = stable_record_id("slice21", build_inspection_surface_record().to_dict())
    second = stable_record_id("slice21", build_inspection_surface_record().to_dict())
    assert first == second
    assert first.startswith("slice21:")


def test_sources_parse_and_do_not_contain_runtime_fragments() -> None:
    for rel in EXPECTED_PAYLOAD_FILES:
        path = REPO / rel
        assert path.is_file(), rel
        if path.suffix == ".py":
            text = path.read_text(encoding="utf-8")
            ast.parse(text, filename=str(path))
            for fragment in PROHIBITED_RUNTIME_FRAGMENTS:
                assert fragment not in text, f"{rel} contains prohibited fragment {fragment!r}"


def main() -> int:
    for test in (
        test_inspection_subjects_are_exact_and_reference_only,
        test_boundary_laws_and_negative_authority_flags_are_locked,
        test_no_live_integration_or_runtime_effect_is_authorized,
        test_authority_separation_grants_nothing_downstream,
        test_boundary_integrity_receipt_and_source_only_verifier_pass,
        test_stable_record_ids_are_deterministic,
        test_sources_parse_and_do_not_contain_runtime_fragments,
    ):
        test()
    print("SLICE21_READ_ONLY_INSPECTION_SURFACE_TEST=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
