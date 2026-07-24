#!/usr/bin/env python3
from __future__ import annotations
import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    sys.path.insert(0, str(repo))

    from forge_language_bridge_v3 import structural_preview_decision
    from forge_language_bridge_v4 import (
        STATUS_CANDIDATE_CUSTODY,
        STATUS_INVALID_CANDIDATE_NOMINATION,
        STATUS_INVALID_INPUT,
        STATUS_SELECTION_ELIGIBILITY_HELD,
        bridge_status,
        candidate_custody_decision,
        parse_explicit_plan,
        selection_nomination_hold_decision,
    )

    checks: list[tuple[str, bool, object]] = []
    def check(name: str, condition: object, detail: object = "") -> None:
        checks.append((name, condition is True, detail))

    candidate_ids: dict[str, str] = {}
    texts = {
        "inspect": "Please inspect concept admission.",
        "report": "Please report concept admission.",
        "request": "Please request concept admission.",
    }
    for root, text in texts.items():
        decision = candidate_custody_decision(
            text,
            action_root=root,
            surface="behavior_test",
            reason="behavior test",
        )
        custody = decision.get("candidate_custody") or {}
        ids = custody.get("candidate_ids") or []
        check(f"{root}.status", decision.get("status") == STATUS_CANDIDATE_CUSTODY, decision)
        check(f"{root}.handled", decision.get("handled") is True, decision)
        check(f"{root}.no_llm", decision.get("calls_llm") is False, decision)
        check(f"{root}.no_execution", decision.get("executes_command") is False and decision.get("executes_simulation") is False, decision)
        check(f"{root}.no_writes", decision.get("writes_files") is False and decision.get("writes_memory") is False, decision)
        check(f"{root}.not_selected", decision.get("selected_meaning") is False and decision.get("meaning_selection_authority") is False, decision)
        check(f"{root}.real_candidate", custody.get("chain_completed") is True and custody.get("manifest_candidate_count", 0) >= 1, custody)
        check(f"{root}.exact_id", len(ids) >= 1 and str(ids[0]).startswith("candidate_meaning:sha256:"), ids)
        check(f"{root}.no_selected_id", custody.get("selected_candidate_id") == "", custody)
        candidate_ids[root] = ids[0]
        repeat = candidate_custody_decision(text, action_root=root, surface="behavior_test", reason="behavior test")
        check(f"{root}.deterministic", repeat.get("candidate_custody", {}).get("candidate_ids") == ids, repeat)

    invalid_root = candidate_custody_decision(
        texts["inspect"], action_root="simulate", surface="behavior_test", reason="test"
    )
    check("invalid_root.held", invalid_root.get("status") == STATUS_INVALID_INPUT, invalid_root)
    check("invalid_root.no_inference", "hidden_action_root_inference_prohibited" in invalid_root.get("reasons", ()), invalid_root)

    exact_hold = selection_nomination_hold_decision(
        texts["inspect"],
        action_root="inspect",
        nominated_candidate_id=candidate_ids["inspect"],
        surface="behavior_test",
        reason="test",
    )
    boundary = exact_hold.get("selection_boundary") or {}
    check("hold.status", exact_hold.get("status") == STATUS_SELECTION_ELIGIBILITY_HELD, exact_hold)
    check("hold.exact", boundary.get("exact_candidate_match") is True, boundary)
    check("hold.valid", boundary.get("boundary_validation_ok") is True, boundary)
    check("hold.nomination", boundary.get("nomination_recorded") is True, boundary)
    check("hold.no_eligibility", boundary.get("eligibility_evaluated") is False, boundary)
    check("hold.no_selected_meaning", boundary.get("selected_meaning_constructed") is False, boundary)
    check("hold.no_41d", boundary.get("slice41d_called") is False, boundary)
    check("hold.no_41e", boundary.get("slice41e_called") is False, boundary)
    check("hold.no_llm", exact_hold.get("calls_llm") is False, exact_hold)
    check("hold.no_action", exact_hold.get("action_authority") is False, exact_hold)

    invalid_nomination = selection_nomination_hold_decision(
        texts["inspect"],
        action_root="inspect",
        nominated_candidate_id="candidate_meaning:sha256:not-real",
        surface="behavior_test",
        reason="test",
    )
    check("invalid_nomination.status", invalid_nomination.get("status") == STATUS_INVALID_CANDIDATE_NOMINATION, invalid_nomination)
    check("invalid_nomination.no_substitute", invalid_nomination.get("selection_boundary", {}).get("exact_candidate_match") is False, invalid_nomination)

    plan = parse_explicit_plan(
        "forge-language-candidate inspect :: Please inspect concept admission.",
        surface="behavior_plan",
    )
    check("plan.candidate", isinstance(plan, dict) and plan.get("_language_bridge", {}).get("status") == STATUS_CANDIDATE_CUSTODY, plan)
    check("plan.no_steps", plan.get("impossible") is True and plan.get("steps") == [], plan)

    plan_candidate_ids = (
        plan.get("_language_bridge", {})
        .get("candidate_custody", {})
        .get("candidate_ids", [])
    )
    check("plan.candidate_id", bool(plan_candidate_ids), plan)

    selection_plan = parse_explicit_plan(
        f"forge-language-selection-hold inspect :: {plan_candidate_ids[0]} :: Please inspect concept admission.",
        surface="behavior_plan",
    )
    check("plan.selection_hold", selection_plan.get("_language_bridge", {}).get("status") == STATUS_SELECTION_ELIGIBILITY_HELD, selection_plan)
    check("plan.ordinary_none", parse_explicit_plan("ordinary unsupported request", surface="behavior_plan") is None)

    bridge3 = structural_preview_decision(
        "ordinary unsupported request",
        surface="behavior_test",
        reason="test",
    )
    check("bridge3.preserved", bridge3.get("status") == "STRUCTURAL_PREVIEW", bridge3)

    status = bridge_status()
    check("status.v4", status.get("bridge_version") == "forge_language_bridge_v4", status)
    check("status.39f", status.get("slice39f_candidate_meaning_constructor_connected") is True, status)
    check("status.39g", status.get("slice39g_msm_candidate_custody_connected") is True, status)
    check("status.no_auto_selection", status.get("automatic_candidate_selection") is False, status)
    check("status.no_eligibility", status.get("selection_eligibility_evaluation_connected") is False, status)
    check("status.no_selected", status.get("selected_meaning_construction_connected") is False, status)

    main_text = (repo / "main.py").read_text(encoding="utf-8")
    check("main.v4_status", "record = _flb4_status()" in main_text)
    check("main.v4_planner", "bridge4_plan = _flb4_explicit_plan" in main_text)
    check("main.candidate_command", "forge-language-candidate" in main_text)
    check("main.selection_command", "forge-language-selection-hold" in main_text)

    failed = [record for record in checks if not record[1]]
    if failed:
        print("FORGE LANGUAGE BRIDGE 4 BEHAVIOR: FAIL")
        for name, _, detail in failed:
            print("FAIL -", name, repr(detail)[:1500])
        return 1

    print("FORGE LANGUAGE BRIDGE 4 BEHAVIOR: PASS")
    print("checks_passed=" + str(len(checks)))
    print("real_candidate_meaning_chain=1")
    print("real_msm_candidate_custody=1")
    print("explicit_candidate_nomination=1")
    print("selection_eligibility_evaluated=0")
    print("selected_meaning_constructed=0")
    print("covered_requests_call_llm=0")
    print("tool_routing=0")
    print("action_execution=0")
    print("source_writes=0")
    print("memory_writes=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
