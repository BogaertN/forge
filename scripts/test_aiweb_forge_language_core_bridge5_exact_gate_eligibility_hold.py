#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    sys.path.insert(0, str(repo))

    from forge_language_bridge_v4 import candidate_custody_decision
    from forge_language_bridge_v5 import (
        STATUS_ELIGIBILITY_EVALUATED_HELD,
        STATUS_INVALID_PREDICATE_FRAME_NOMINATION,
        STATUS_PREDICATE_FRAME_NOMINATION_REQUIRED,
        bridge_status,
        eligibility_hold_decision,
        parse_explicit_plan,
    )
    from forge_language_bridge_v5.eligibility_hold import (
        _build_candidate_artifacts,
        _linked_pair_options,
    )
    from forge_language_bridge_v5.runtime_builders import build_gate_and_eligibility
    from aiweb_language_core_bootstrap.verbal_cognition_gate_runtime import gate_composition

    checks: list[tuple[str, bool, object]] = []

    def check(name: str, condition: object, detail: object = "") -> None:
        checks.append((name, condition is True, detail))

    source = "Please inspect concept admission."
    action_root = "inspect"

    custody = candidate_custody_decision(
        source,
        action_root=action_root,
        surface="bridge5_behavior",
        reason="Bridge 5 behavior test.",
    )
    candidate_ids = tuple(
        (custody.get("candidate_custody") or {}).get("candidate_ids") or ()
    )
    check("candidate.exactly_one", len(candidate_ids) == 1, custody)
    candidate_id = candidate_ids[0] if candidate_ids else ""

    plurality = eligibility_hold_decision(
        source,
        action_root=action_root,
        nominated_candidate_id=candidate_id,
        surface="bridge5_behavior",
        reason="Bridge 5 behavior test.",
    )
    options = tuple(plurality.get("predicate_frame_options") or ())
    check(
        "plurality.status",
        plurality.get("status") == STATUS_PREDICATE_FRAME_NOMINATION_REQUIRED,
        plurality,
    )
    check("plurality.multiple", len(options) >= 2, options)
    check(
        "plurality.no_automatic_first",
        "automatic_first_pair_selection_prohibited" in tuple(plurality.get("reasons") or ()),
        plurality,
    )
    check(
        "plurality.no_gate",
        (plurality.get("gate_evaluation") or {}).get("executed") is False,
        plurality,
    )

    option = options[0] if options else {}
    decision = eligibility_hold_decision(
        source,
        action_root=action_root,
        nominated_candidate_id=candidate_id,
        predicate_candidate_id=str(option.get("predicate_candidate_id") or ""),
        role_layout_candidate_id=str(option.get("role_layout_candidate_id") or ""),
        surface="bridge5_behavior",
        reason="Bridge 5 behavior test.",
    )
    gate = decision.get("gate_evaluation") or {}
    selection = decision.get("selection_boundary") or {}
    family = gate.get("family_results") or {}

    check(
        "exact.status",
        decision.get("status") == STATUS_ELIGIBILITY_EVALUATED_HELD,
        decision,
    )
    check("exact.gate_executed", gate.get("executed") is True, gate)
    check("exact.family_count", len(family) == 4, family)
    check(
        "exact.family_indeterminate",
        all(
            str((family.get(name) or {}).get("state") or "").endswith("indeterminate")
            for name in (
                "expectancy",
                "congruity",
                "connectedness",
                "recoverable_purpose",
            )
        ),
        family,
    )
    check("exact.composition", gate.get("composition_executed") is True, gate)
    check(
        "exact.composition_status",
        gate.get("composition_status") == "composition_indeterminate_authority",
        gate,
    )
    check("exact.msm_gate_custody", gate.get("msm_gate_custody_created") is True, gate)
    check("exact.all_family_results", gate.get("all_family_results_preserved") is True, gate)
    check("exact.eligibility", selection.get("eligibility_evaluated") is True, selection)
    check(
        "exact.outcome",
        selection.get("eligibility_outcome") == "held_pending_authority",
        selection,
    )
    check(
        "exact.not_eligible",
        selection.get("eligible_for_selected_meaning_construction") is False,
        selection,
    )
    check("exact.no_41d", selection.get("slice41d_called") is False, selection)
    check("exact.no_41e", selection.get("slice41e_called") is False, selection)
    check("exact.no_selected", selection.get("selected_meaning_constructed") is False, selection)
    check("exact.no_llm", decision.get("calls_llm") is False, decision)
    check("exact.no_tool", decision.get("tool_routing_authority") is False, decision)
    check("exact.no_action", decision.get("action_authority") is False, decision)
    check("exact.no_writes", decision.get("writes_files") is False and decision.get("writes_memory") is False, decision)
    check("exact.echo_not_invoked", decision.get("echo_forge_llm_invoked") is False, decision)
    check(
        "exact.echo_not_authority",
        decision.get("echo_forge_output_used_as_forge_authority") is False,
        decision,
    )

    invalid_pair = eligibility_hold_decision(
        source,
        action_root=action_root,
        nominated_candidate_id=candidate_id,
        predicate_candidate_id="slice38g_action_root_predicate_candidate:not-real",
        role_layout_candidate_id=str(option.get("role_layout_candidate_id") or ""),
        surface="bridge5_behavior",
        reason="Bridge 5 behavior test.",
    )
    check(
        "invalid_pair.status",
        invalid_pair.get("status") == STATUS_INVALID_PREDICATE_FRAME_NOMINATION,
        invalid_pair,
    )
    check(
        "invalid_pair.no_gate",
        (invalid_pair.get("gate_evaluation") or {}).get("executed") is False,
        invalid_pair,
    )

    explicit = (
        "forge-language-eligibility-hold inspect :: "
        f"{candidate_id} :: {option.get('predicate_candidate_id')} :: "
        f"{option.get('role_layout_candidate_id')} :: {source}"
    )
    plan = parse_explicit_plan(explicit, surface="bridge5_behavior_plan")
    check(
        "plan.status",
        isinstance(plan, dict)
        and (plan.get("_language_bridge") or {}).get("status")
        == STATUS_ELIGIBILITY_EVALUATED_HELD,
        plan,
    )
    check("plan.no_steps", plan.get("impossible") is True and plan.get("steps") == [], plan)
    check("plan.ordinary_none", parse_explicit_plan("ordinary request", surface="test") is None)

    artifacts = _build_candidate_artifacts(source, action_root=action_root)
    companion = next(
        value
        for value in artifacts["companions"]
        if value.candidate_meaning_id == candidate_id
    )
    constructed = artifacts["constructed_by_id"][candidate_id]
    manifest_candidate = artifacts["manifest_records"][
        companion.manifest_candidate_record_id
    ]
    linked = _linked_pair_options(artifacts, constructed)[0]
    artifacts.update(
        {
            "manifest_companion": companion,
            "manifest_candidate": manifest_candidate,
            "constructed_record": constructed,
            "predicate_candidate": linked["_predicate"],
            "role_layout_candidate": linked["_layout"],
        }
    )
    runtime = build_gate_and_eligibility(artifacts)
    family_results = (
        runtime["expectancy_result"],
        runtime["congruity_result"],
        runtime["connectedness_result"],
        runtime["purpose_result"],
    )
    family_refs = tuple(item.candidate_input_ref for item in family_results)
    check("composition.same_exact_candidate", len(set(family_refs)) == 1, family_refs)
    check(
        "composition.same_candidate_valid",
        gate_composition.validate_evaluation_input(runtime["composition_input"]).ok,
        gate_composition.validate_evaluation_input(runtime["composition_input"]),
    )
    mixed = replace(
        runtime["composition_input"],
        family_candidate_input_refs=(
            family_refs[0],
            family_refs[0],
            family_refs[0],
            "gate_candidate_input:sha256:" + "0" * 64,
        ),
    )
    check(
        "composition.mixed_candidate_rejected",
        not gate_composition.validate_evaluation_input(mixed).ok,
        gate_composition.validate_evaluation_input(mixed),
    )

    status = bridge_status()
    check("status.v5", status.get("bridge_version") == "forge_language_bridge_v5", status)
    check("status.40c", status.get("slice40c_expectancy_connected") is True, status)
    check("status.40g", status.get("slice40g_gate_composition_connected") is True, status)
    check("status.40h", status.get("slice40h_msm_gate_custody_connected") is True, status)
    check("status.41c", status.get("slice41c_eligibility_evaluation_connected") is True, status)
    check("status.no_41d", status.get("slice41d_selected_meaning_construction_connected") is False, status)
    check("status.echo_preserved", status.get("echo_forge_llm_boundary_preserved") is True, status)
    check("status.echo_not_authority", status.get("echo_forge_output_is_forge_authority") is False, status)
    check("status.forge_llm_authority", status.get("forge_interpretation_llm_authority") is False, status)

    runtime_source = (repo / "forge_language_bridge_v5/runtime_builders.py").read_text(encoding="utf-8")
    check("runtime.no_test_import", "test_aiweb" not in runtime_source and "runpy" not in runtime_source, runtime_source[:1000])
    check("runtime.no_llm_call", "_call_ollama" not in runtime_source and "ollama" not in runtime_source.lower(), "")

    main_text = (repo / "main.py").read_text(encoding="utf-8")
    check("main.command", '"forge-language-eligibility-hold"' in main_text, "")
    check("main.status", "record = _flb5_status()" in main_text, "")
    check("main.planner", "bridge5_plan = _flb5_explicit_plan" in main_text, "")
    check("main.bridge4_preserved", "bridge4_plan = _flb4_explicit_plan" in main_text, "")

    failed = [record for record in checks if not record[1]]
    if failed:
        print("FORGE LANGUAGE BRIDGE 5 BEHAVIOR: FAIL")
        for name, _, detail in failed:
            print("FAIL -", name, repr(detail)[:2000])
        return 1

    print("FORGE LANGUAGE BRIDGE 5 BEHAVIOR: PASS")
    print(f"checks_passed={len(checks)}")
    print("exact_candidate_nomination=1")
    print("predicate_frame_plurality_preserved=1")
    print("exact_predicate_frame_nomination=1")
    print("same_candidate_four_family_refs_accepted=1")
    print("mixed_candidate_family_refs_rejected=1")
    print("slice40c_expectancy_executed=1")
    print("slice40d_congruity_executed=1")
    print("slice40e_connectedness_executed=1")
    print("slice40f_recoverable_purpose_executed=1")
    print("slice40g_composition_executed=1")
    print("slice40h_msm_gate_custody_created=1")
    print("slice41c_eligibility_evaluated=1")
    print("eligibility_outcome=held_pending_authority")
    print("slice41d_called=0")
    print("selected_meaning_created=0")
    print("tool_routing=0")
    print("action_execution=0")
    print("memory_writes=0")
    print("forge_llm_calls=0")
    print("echo_forge_llm_boundary_preserved=1")
    print("echo_forge_output_is_forge_authority=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
