#!/usr/bin/env python3
"""Behavior tests for RMC-NON-LLM-RENDERER-AND-SEMANTIC-LEXICON-BUILD-009.

All operations are read-only.  Text created here is an unapproved render
preview and may not become user-facing approved output until Build 010 Echo
Validator hardening passes.
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
    from rmc_engine_v1.renderer.semantic_lexicon import (  # noqa: WPS433
        BUILD_ID,
        CONTROLLED_ATOMS,
        SUPPORTED_DELIVERY_MODES,
        build_semantic_plan,
        semantic_lexicon_boundary,
        validate_render_admission_packet,
    )
    from rmc_engine_v1.renderer.grammar_templates import (  # noqa: WPS433
        build_sentence_plan,
        grammar_templates_boundary,
    )
    from rmc_engine_v1.renderer.surface_realizer import (  # noqa: WPS433
        PREVIEW_STATUS,
        realize_sentence_plan,
        surface_realizer_boundary,
    )
    from rmc_engine_v1.renderer.renderer import (  # noqa: WPS433
        non_llm_renderer_boundary,
        non_llm_renderer_status,
        render_admitted_preview,
        render_historical_hypothesis_preview,
    )
    import rmc_engine_v1.renderer as renderer_package  # noqa: WPS433

    passed = failed = 0

    def check(name: str, ok: bool, detail: object = None) -> None:
        nonlocal passed, failed
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail is not None else ""))
        passed += int(ok)
        failed += int(not ok)

    print("RMC-NON-LLM-RENDERER-AND-SEMANTIC-LEXICON-BUILD-009 BEHAVIOR TESTS — UNAPPROVED PREVIEW ONLY")

    runtime_root = forge_root / "runtime_state" / "mea_problem_manifest_store_v1"
    memory_root = forge_root / "memory" / "mea_manifest_memory_v1"
    generic_surfaces = [
        forge_root / "rmc_engine_v1" / "output_renderer.py",
        forge_root / "rmc_engine_v1" / "manifest_compiler.py",
        forge_root / "rmc_engine_v1" / "echo_validator.py",
        forge_root / "rmc_engine_v1" / "resonance_lexicon.py",
        forge_root / "rmc_engine_v1" / "memory_writer.py",
    ]
    before_runtime = tree_hash(runtime_root)
    before_memory = tree_hash(memory_root)
    before_generic = {str(path): file_hash(path) for path in generic_surfaces}

    renderer_boundary = non_llm_renderer_boundary()
    lexicon_boundary = semantic_lexicon_boundary()
    grammar_boundary = grammar_templates_boundary()
    realizer_boundary = surface_realizer_boundary()

    check("build_id_locked", BUILD_ID == "RMC-NON-LLM-RENDERER-AND-SEMANTIC-LEXICON-BUILD-009")
    check("build008_package_build_id_backward_compatible", renderer_package.BUILD_ID == "MEA-TO-RMC-RENDER-GATE-ADAPTER-BUILD-008")
    check("build008_package_schema_backward_compatible", renderer_package.SCHEMA_VERSION == "mea_to_rmc_render_gate_adapter_v1_build008")
    check("build009_package_alias_available", renderer_package.NON_LLM_RENDERER_BUILD_ID == BUILD_ID)
    check("supported_modes_exact", tuple(SUPPORTED_DELIVERY_MODES) == (
        "explanation", "decision", "warning", "verification_result",
        "next_step", "refusal", "uncertain_result",
    ))
    for key in (
        "calls_llm", "invokes_generic_output_renderer", "invokes_existing_echo_validator",
        "approves_user_output", "renders_public_output", "compiles_rmc_meaning_manifest",
        "writes_files", "writes_mea_memory", "writes_rmc_output_memory",
        "writes_identity_vault", "writes_contribution_economy", "mints_ct",
        "writes_ledgers", "writes_chroma", "creates_http_routes", "modifies_ui",
        "performs_network_io", "executes_shell",
    ):
        check(f"renderer_boundary_{key}_false", renderer_boundary[key] is False, renderer_boundary[key])
    check("renderer_requires_echo_later", renderer_boundary["echo_validation_required_later"] is True)
    check("lexicon_is_not_input_resonance_lexicon", lexicon_boundary["separate_from_resonance_input_lexicon"] is True)
    check("lexicon_does_not_add_evidence", lexicon_boundary["adds_evidence"] is False)
    check("lexicon_does_not_upgrade_claim", lexicon_boundary["changes_claim_status"] is False)
    check("grammar_rule_based", grammar_boundary["rule_based_sentence_planning"] is True)
    check("grammar_no_approval", grammar_boundary["approves_output"] is False)
    check("realizer_pre_echo_only", realizer_boundary["pre_echo_safety_scan_only"] is True)
    check("realizer_no_approval", realizer_boundary["approves_user_output"] is False)

    gate_request = build_historical_hypothesis_admission_request(forge_root=forge_root)
    gate_response = evaluate_mea_render_admission_request(gate_request, forge_root=forge_root)
    admission = gate_response["render_admission_packet"]
    check("build008_gate_accepted", gate_response.get("accepted") is True)
    check("build008_gate_rendered_nothing", gate_response.get("render_performed") is False)
    packet_validation = validate_render_admission_packet(admission)
    check("admission_packet_valid", packet_validation["valid"] is True, packet_validation.get("errors"))

    semantic = build_semantic_plan(admission, delivery_mode="explanation")
    check("semantic_plan_accepted", semantic["accepted"] is True)
    splan = semantic["semantic_plan"]
    check("semantic_plan_hypothesis", splan["epistemic_contract"]["claim_status"] == "hypothesis")
    check("semantic_plan_test_required", splan["epistemic_contract"]["required_next_action"] == "test_required")
    check("semantic_plan_proof_debt_preserved", splan["epistemic_contract"]["proof_debt_micro"] == 850_000)
    check("semantic_plan_no_evidence_addition", splan["no_new_evidence"] is True)
    check("semantic_plan_controlled_atoms_locked", splan["controlled_atoms"] == CONTROLLED_ATOMS)

    sentence = build_sentence_plan(splan)
    check("sentence_plan_accepted", sentence["accepted"] is True)
    check("sentence_plan_unapproved", sentence["sentence_plan"]["approved_output"] is False)
    realization = realize_sentence_plan(sentence["sentence_plan"])
    check("surface_realization_accepted", realization["accepted"] is True)
    base_preview = realization["render_preview"]
    check("surface_status_unapproved", base_preview["preview_status"] == PREVIEW_STATUS)
    check("surface_echo_not_run", base_preview["echo_validation_performed"] is False)
    check("surface_not_authorized", base_preview["user_facing_output_authorized"] is False)
    check("surface_preserves_hypothesis_word", "hypothesis" in base_preview["rendered_text_preview"])
    check("surface_preserves_test_requirement", "Testing is required" in base_preview["rendered_text_preview"])
    check("surface_preserves_proof_debt", "0.85" in base_preview["rendered_text_preview"])

    hashes: set[str] = set()
    texts: set[str] = set()
    for mode in SUPPORTED_DELIVERY_MODES:
        first = render_historical_hypothesis_preview(forge_root=forge_root, delivery_mode=mode)
        second = render_historical_hypothesis_preview(forge_root=forge_root, delivery_mode=mode)
        preview = first.get("render_preview") or {}
        text = str(preview.get("rendered_text_preview", ""))
        check(f"{mode}_accepted", first.get("accepted") is True)
        check(f"{mode}_deterministic", first.get("render_report_hash") == second.get("render_report_hash"))
        check(f"{mode}_preview_only", preview.get("approved_output") is False and preview.get("echo_validation_required") is True)
        check(f"{mode}_claim_preserved", (preview.get("epistemic_contract") or {}).get("claim_status") == "hypothesis")
        check(f"{mode}_required_action_preserved", (preview.get("epistemic_contract") or {}).get("required_next_action") == "test_required")
        check(f"{mode}_contains_no_empirical_upgrade", " is an empirical fact" not in text and " is proven" not in text)
        hashes.add(str(preview.get("render_preview_hash")))
        texts.add(text)
    check("all_modes_generate_distinct_preview_hashes", len(hashes) == len(SUPPORTED_DELIVERY_MODES), len(hashes))
    check("all_modes_generate_distinct_texts", len(texts) == len(SUPPORTED_DELIVERY_MODES), len(texts))

    status = non_llm_renderer_status(forge_root=forge_root)
    check("status_ok", status["status"] == "OK")
    check("status_preview_available", status["qualified_hypothesis_preview_available"] is True)
    check("status_output_still_unapproved", status["preview"]["approved_output"] is False)

    unsupported = render_admitted_preview(admission, delivery_mode="public_claim")
    check("unsupported_delivery_mode_rejected", unsupported.get("accepted") is False and unsupported.get("reason_code") == "unsupported_delivery_mode")

    tampered_packet = deepcopy(admission)
    tampered_packet["epistemic_boundary"]["claim_status"] = "verified_claim"
    tampered_packet["admission_packet_hash"] = canonical_hash({k: v for k, v in tampered_packet.items() if k != "admission_packet_hash"})
    tampered = render_admitted_preview(tampered_packet, delivery_mode="explanation")
    check("claim_upgrade_packet_rejected", tampered.get("accepted") is False)

    bad_hash = deepcopy(admission)
    bad_hash["admission_packet_hash"] = "0" * 64
    bad = render_admitted_preview(bad_hash, delivery_mode="explanation")
    check("tampered_admission_hash_rejected", bad.get("accepted") is False)

    atom_tamper = deepcopy(splan)
    atom_tamper["controlled_atoms"]["not_verified"] = "It is verified."
    atom_tamper["semantic_plan_hash"] = canonical_hash({k: v for k, v in atom_tamper.items() if k != "semantic_plan_hash"})
    check("modified_atom_set_rejected", build_sentence_plan(atom_tamper).get("accepted") is False)

    unsafe_sentence = deepcopy(sentence["sentence_plan"])
    unsafe_sentence["clauses"][0]["sentence"] = "The stored candidate is an empirical fact."
    unsafe_sentence["sentence_plan_hash"] = canonical_hash({k: v for k, v in unsafe_sentence.items() if k != "sentence_plan_hash"})
    unsafe_result = realize_sentence_plan(unsafe_sentence)
    check("unsafe_surface_upgrade_rejected", unsafe_result.get("accepted") is False and unsafe_result.get("reason_code") == "pre_echo_surface_safety_check_failed")

    renderer_source = (forge_root / "rmc_engine_v1" / "renderer" / "renderer.py").read_text(encoding="utf-8")
    check("renderer_does_not_import_generic_output_renderer", "from rmc_engine_v1.output_renderer" not in renderer_source)
    check("renderer_does_not_import_echo_validator", "from rmc_engine_v1.echo_validator" not in renderer_source)
    check("renderer_does_not_import_llm_renderer", "from rmc_engine_v1.llm_renderer" not in renderer_source)

    after_runtime = tree_hash(runtime_root)
    after_memory = tree_hash(memory_root)
    after_generic = {str(path): file_hash(path) for path in generic_surfaces}
    check("mea_runtime_state_unchanged", after_runtime == before_runtime)
    check("mea_memory_record_unchanged", after_memory == before_memory)
    check("existing_generic_rmc_language_surfaces_unchanged", after_generic == before_generic)

    print(f"RESULT: RMC-NON-LLM-RENDERER-AND-SEMANTIC-LEXICON-BUILD-009_BEHAVIOR {'PASS' if failed == 0 else 'FAIL'}  Total:{passed + failed} Passed:{passed} Failed:{failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
