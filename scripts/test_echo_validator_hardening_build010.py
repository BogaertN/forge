#!/usr/bin/env python3
"""Behavior tests for RMC-MEA-ECHO-VALIDATOR-HARDENING-BUILD-010.

Build 010 is read-only.  It validates deterministic Build 009 preview text
against its Build 008 MEA admission packet.  A passing report means eligible
for a later approval-gate review only; no user-facing approval or persistence
occurs here.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
from pathlib import Path
import sys


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix not in {".pyc", ".pyo"}):
        digest.update(f"{path.relative_to(root).as_posix()}\0{hashlib.sha256(path.read_bytes()).hexdigest()}\n".encode("utf-8"))
    return digest.hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", required=True, type=Path)
    args = parser.parse_args()
    forge_root = args.forge_root.expanduser().resolve()
    sys.path.insert(0, str(forge_root))

    from rmc_engine_v1.mea.fixed_point_math_contract import canonical_hash  # noqa: WPS433
    from rmc_engine_v1.renderer.mea_render_gate import (  # noqa: WPS433
        build_historical_hypothesis_admission_request,
        evaluate_mea_render_admission_request,
    )
    from rmc_engine_v1.renderer.renderer import render_admitted_preview  # noqa: WPS433
    from rmc_engine_v1.renderer.semantic_lexicon import SUPPORTED_DELIVERY_MODES  # noqa: WPS433
    from rmc_engine_v1.renderer.echo_validator import (  # noqa: WPS433
        BUILD_ID,
        ECHO_PASS_SCORE_MICRO,
        VALID_STATUS,
        REJECTED_STATUS,
        echo_validator_boundary,
        echo_validator_status,
        validate_historical_hypothesis_preview_echo,
        validate_render_preview_echo,
    )
    import rmc_engine_v1.renderer as renderer_package  # noqa: WPS433

    passed = failed = 0

    def check(name: str, ok: bool, detail: object = None) -> None:
        nonlocal passed, failed
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail is not None else ""))
        passed += int(ok)
        failed += int(not ok)

    def rerender_with_text(report: dict, text: str) -> dict:
        mutated = deepcopy(report)
        preview = mutated["render_preview"]
        preview["rendered_text_preview"] = text
        preview["render_preview_hash"] = canonical_hash({k: v for k, v in preview.items() if k != "render_preview_hash"})
        mutated["render_preview_hash"] = preview["render_preview_hash"]
        mutated["render_report_hash"] = canonical_hash({k: v for k, v in mutated.items() if k != "render_report_hash"})
        return mutated

    def recanonicalize(report: dict) -> dict:
        mutated = deepcopy(report)
        preview = mutated["render_preview"]
        preview["render_preview_hash"] = canonical_hash({k: v for k, v in preview.items() if k != "render_preview_hash"})
        mutated["render_preview_hash"] = preview["render_preview_hash"]
        mutated["render_report_hash"] = canonical_hash({k: v for k, v in mutated.items() if k != "render_report_hash"})
        return mutated

    print("RMC-MEA-ECHO-VALIDATOR-HARDENING-BUILD-010 BEHAVIOR TESTS — READ-ONLY VALIDATION ONLY")

    runtime_root = forge_root / "runtime_state" / "mea_problem_manifest_store_v1"
    memory_root = forge_root / "memory" / "mea_manifest_memory_v1"
    protected_sources = [
        forge_root / "rmc_engine_v1" / "renderer" / "mea_render_gate.py",
        forge_root / "rmc_engine_v1" / "renderer" / "semantic_lexicon.py",
        forge_root / "rmc_engine_v1" / "renderer" / "grammar_templates.py",
        forge_root / "rmc_engine_v1" / "renderer" / "surface_realizer.py",
        forge_root / "rmc_engine_v1" / "renderer" / "renderer.py",
        forge_root / "rmc_engine_v1" / "echo_validator.py",
        forge_root / "rmc_engine_v1" / "output_renderer.py",
        forge_root / "rmc_engine_v1" / "manifest_compiler.py",
        forge_root / "rmc_engine_v1" / "memory_writer.py",
    ]
    before_runtime = tree_hash(runtime_root)
    before_memory = tree_hash(memory_root)
    before_sources = {str(path): file_hash(path) for path in protected_sources}

    boundary = echo_validator_boundary()
    check("build_id_locked", BUILD_ID == "RMC-MEA-ECHO-VALIDATOR-HARDENING-BUILD-010")
    check("build008_export_preserved", renderer_package.BUILD_ID == "MEA-TO-RMC-RENDER-GATE-ADAPTER-BUILD-008")
    check("build009_export_preserved", renderer_package.NON_LLM_RENDERER_BUILD_ID == "RMC-NON-LLM-RENDERER-AND-SEMANTIC-LEXICON-BUILD-009")
    check("build010_export_available", renderer_package.ECHO_VALIDATOR_BUILD_ID == BUILD_ID)
    for key in (
        "approves_user_output", "authorizes_public_release", "creates_http_routes",
        "modifies_ui", "writes_files", "writes_mea_memory", "writes_rmc_output_memory",
        "writes_identity_vault", "writes_contribution_economy", "mints_ct",
        "writes_ledgers", "writes_chroma", "calls_llm", "executes_shell",
        "performs_network_io",
    ):
        check(f"boundary_{key}_false", boundary[key] is False, boundary[key])
    check("boundary_requires_textual_proof_debt", boundary["requires_proof_debt_in_rendered_language"] is True)
    check("boundary_leaves_generic_echo_untouched", boundary["existing_generic_echo_validator_left_untouched"] is True)

    request = build_historical_hypothesis_admission_request(forge_root=forge_root)
    admission_response = evaluate_mea_render_admission_request(request, forge_root=forge_root)
    admission = admission_response["render_admission_packet"]
    check("build008_admission_accepted", admission_response.get("accepted") is True)

    expected_valid_modes = {"explanation", "verification_result", "uncertain_result"}
    expected_repair_modes = {"decision", "warning", "next_step", "refusal"}
    for mode in SUPPORTED_DELIVERY_MODES:
        echo = validate_historical_hypothesis_preview_echo(forge_root=forge_root, delivery_mode=mode)
        if mode in expected_valid_modes:
            check(f"{mode}_echo_valid", echo.get("accepted") is True, echo.get("failure_reasons"))
            check(f"{mode}_full_fixed_score", echo.get("echo_score_micro") == ECHO_PASS_SCORE_MICRO)
            check(f"{mode}_only_later_approval_eligible", echo.get("eligible_for_later_approval_gate") is True and echo.get("rendered_output_approved") is False)
            check(f"{mode}_valid_status", echo.get("echo_status") == VALID_STATUS)
        else:
            check(f"{mode}_rejected_for_missing_material_caveat", echo.get("accepted") is False and "material_proof_debt_not_preserved_in_contract_and_rendered_text" in echo.get("failure_reasons", []), echo.get("failure_reasons"))
            check(f"{mode}_never_approval_eligible", echo.get("eligible_for_later_approval_gate") is False)
            check(f"{mode}_rejected_status", echo.get("echo_status") == REJECTED_STATUS)

    status = echo_validator_status(forge_root=forge_root)
    check("status_ok_for_canonical_preview", status.get("status") == "OK")
    check("canonical_explanation_valid", status.get("canonical_preview_echo_valid") is True)
    check("valid_modes_exact", set(status.get("valid_preview_modes", [])) == expected_valid_modes, status.get("valid_preview_modes"))
    check("template_repair_modes_exact", set(status.get("template_repair_required_modes", [])) == expected_repair_modes, status.get("template_repair_required_modes"))
    check("status_does_not_approve_output", status.get("approved_output") is False and status.get("user_facing_output_authorized") is False)

    canonical_render = render_admitted_preview(admission, delivery_mode="explanation")
    valid = validate_render_preview_echo(canonical_render, admission)
    check("canonical_render_direct_validation_passes", valid.get("accepted") is True)

    missing_test = rerender_with_text(
        canonical_render,
        "The stored candidate for `144hz_substrate_status` is classified as a hypothesis. "
        "It is not a verified claim or an empirical fact. "
        "The preserved proof-debt value is 0.85. "
        "This preview is unapproved until Echo Validation passes.",
    )
    missing_test_result = validate_render_preview_echo(missing_test, admission)
    check("missing_test_required_rejected", "required_next_action_test_required_missing" in missing_test_result.get("failure_reasons", []))

    missing_proof = rerender_with_text(
        canonical_render,
        "The stored candidate for `144hz_substrate_status` is classified as a hypothesis. "
        "It is not a verified claim or an empirical fact. "
        "Testing is required before any claim-status upgrade. "
        "This preview is unapproved until Echo Validation passes.",
    )
    missing_proof_result = validate_render_preview_echo(missing_proof, admission)
    check("missing_proof_debt_rejected", "material_proof_debt_not_preserved_in_contract_and_rendered_text" in missing_proof_result.get("failure_reasons", []))

    for name, text, expected_fragment in (
        (
            "proven_substrate",
            "The stored candidate for `144hz_substrate_status` is classified as a hypothesis. "
            "144 Hz is proven to be the substrate frequency. Testing is required before any claim-status upgrade. "
            "The preserved proof-debt value is 0.85. This preview is unapproved until Echo Validation passes.",
            "language_exceeds_admitted_scope:proven_substrate_claim",
        ),
        (
            "unsupported_harmonic",
            "The stored candidate for `144hz_substrate_status` is classified as a hypothesis. "
            "144 Hz is a golden-ratio harmonic. Testing is required before any claim-status upgrade. "
            "The preserved proof-debt value is 0.85. This preview is unapproved until Echo Validation passes.",
            "language_exceeds_admitted_scope:unsupported_harmonic_assertion",
        ),
        (
            "discovery_upgrade",
            "The stored candidate for `144hz_substrate_status` is classified as a hypothesis. "
            "This discovery confirms the hypothesis. Testing is required before any claim-status upgrade. "
            "The preserved proof-debt value is 0.85. This preview is unapproved until Echo Validation passes.",
            "language_exceeds_admitted_scope:discovery_upgrade",
        ),
        (
            "invented_evidence",
            "The stored candidate for `144hz_substrate_status` is classified as a hypothesis. "
            "Published evidence confirms it. Testing is required before any claim-status upgrade. "
            "The preserved proof-debt value is 0.85. This preview is unapproved until Echo Validation passes.",
            "language_exceeds_admitted_scope:invented_published_evidence",
        ),
    ):
        report = rerender_with_text(canonical_render, text)
        result = validate_render_preview_echo(report, admission)
        check(f"{name}_rejected", expected_fragment in result.get("failure_reasons", []), result.get("failure_reasons"))

    changed_contract = deepcopy(canonical_render)
    changed_contract["render_preview"]["epistemic_contract"]["proof_debt_text"] = "0.10"
    changed_contract["render_preview"]["epistemic_contract"]["proof_debt_micro"] = 100_000
    changed_contract = recanonicalize(changed_contract)
    changed_contract_result = validate_render_preview_echo(changed_contract, admission)
    check("structured_proof_debt_reduction_rejected", "material_proof_debt_not_preserved_in_contract_and_rendered_text" in changed_contract_result.get("failure_reasons", []))

    false_approval = deepcopy(canonical_render)
    false_approval["approved_output"] = True
    false_approval["user_facing_output_authorized"] = True
    false_approval["render_preview"]["approved_output"] = True
    false_approval["render_preview"]["user_facing_output_authorized"] = True
    false_approval = recanonicalize(false_approval)
    false_approval_result = validate_render_preview_echo(false_approval, admission)
    check("premature_approval_rejected", "approval_or_memory_permission_boundary_not_preserved" in false_approval_result.get("failure_reasons", []))

    hash_tamper = deepcopy(canonical_render)
    hash_tamper["render_preview"]["rendered_text_preview"] = "tampered without new hash"
    hash_tamper_result = validate_render_preview_echo(hash_tamper, admission)
    check("render_hash_tamper_rejected", "source_or_render_hash_binding_invalid" in hash_tamper_result.get("failure_reasons", []))

    source_tamper = deepcopy(admission)
    source_tamper["source_binding"]["candidate_id"] = "other_candidate"
    source_tamper["admission_packet_hash"] = canonical_hash({k: v for k, v in source_tamper.items() if k != "admission_packet_hash"})
    source_tamper_result = validate_render_preview_echo(canonical_render, source_tamper)
    check("candidate_source_tamper_rejected", source_tamper_result.get("accepted") is False)

    after_runtime = tree_hash(runtime_root)
    after_memory = tree_hash(memory_root)
    after_sources = {str(path): file_hash(path) for path in protected_sources}
    check("mea_runtime_state_unchanged", after_runtime == before_runtime)
    check("mea_memory_record_unchanged", after_memory == before_memory)
    check("existing_renderer_and_generic_echo_sources_unchanged", after_sources == before_sources)

    print()
    print(f"RESULT: RMC-MEA-ECHO-VALIDATOR-HARDENING-BUILD-010_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
