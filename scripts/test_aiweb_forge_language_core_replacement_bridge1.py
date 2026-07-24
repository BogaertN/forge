#!/usr/bin/env python3
"""Behavior checks for Forge language-core replacement Bridge 1."""

from __future__ import annotations

import argparse
import ast
import importlib
import json
import sys
from pathlib import Path


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    args = parser.parse_args()

    repo = Path(args.repository).resolve()
    failures: list[str] = []
    checks = 0

    sys.path.insert(0, str(repo))
    module = importlib.import_module("forge_language_bridge_v1")

    cases = (
        ("show forge status", True, "ROUTED", "status", ""),
        ("what can Forge do?", True, "ROUTED", "forge-capabilities", ""),
        ("verify the audit chain", True, "ROUTED", "audit", ""),
        ("check ProtoForge status", True, "ROUTED", "forge-protoforge-status", ""),
        (
            "build a symbolic frequency simulation",
            True,
            "ROUTED",
            "forge-protoforge-simulation-plan",
            "symbolic_frequency_probe",
        ),
        (
            "create a falling cube simulation",
            True,
            "ROUTED",
            "forge-protoforge-simulation-plan",
            "pybullet_fixed_falling_cube",
        ),
        (
            "show simulation result simreq_abc123",
            True,
            "ROUTED",
            "forge-protoforge-result-show",
            "simreq_abc123",
        ),
        ("run the simulation", True, "APPROVAL_REQUIRED", "", ""),
        ("tell me a joke", False, "UNSUPPORTED", "", ""),
    )

    for request, handled, status, route, route_args in cases:
        decision = module.interpret_request(request, surface="behavior_test")
        checks += 1
        require(decision["handled"] is handled, f"handled:{request}", failures)
        checks += 1
        require(decision["status"] == status, f"status:{request}", failures)
        checks += 1
        require(decision["route"] == route, f"route:{request}", failures)
        checks += 1
        require(decision["args"] == route_args, f"args:{request}", failures)

        for field in (
            "calls_llm",
            "executes_command",
            "executes_shell",
            "executes_simulation",
            "writes_files",
            "writes_memory",
            "grants_permission",
        ):
            checks += 1
            require(decision[field] is False, f"{field}:{request}", failures)

        custody = decision["input_custody"]
        checks += 1
        require(custody["custody_created"] is True, f"custody:{request}", failures)
        for field in (
            "filesystem_read_performed",
            "filesystem_write_performed",
            "network_access_performed",
            "memory_read_performed",
            "memory_write_performed",
            "tool_routing_performed",
            "action_performed",
            "delivery_performed",
        ):
            checks += 1
            require(custody[field] is False, f"custody_{field}:{request}", failures)

        preview = decision["recursive_manifest_preview"]
        checks += 1
        require(
            preview["manifest_status"] == "preview_only_not_compiled_mu_t",
            f"manifest_status:{request}",
            failures,
        )
        for field in (
            "rmc_authority",
            "selected_meaning_authority",
            "output_rendering_authority",
            "permission_authority",
            "execution_authority",
            "memory_write_allowed",
            "canonical_reference_write_allowed",
        ):
            checks += 1
            require(preview[field] is False, f"preview_{field}:{request}", failures)

        if handled:
            plan = module.decision_to_plan(decision)
            checks += 1
            require(plan["_language_bridge"]["calls_llm"] is False, f"plan_llm:{request}", failures)
            checks += 1
            require(
                plan["_language_bridge"]["executes_simulation"] is False,
                f"plan_simulation:{request}",
                failures,
            )

    run_decision = module.interpret_request("run the simulation", surface="behavior_test")
    checks += 1
    require(run_decision["approval_required"] is True, "run_approval_required", failures)
    checks += 1
    require(run_decision["approval_gate"] == "RUN-PROTOFORGE", "run_gate", failures)

    unsupported = module.interpret_request("please explain quantum gravity", surface="behavior_test")
    checks += 1
    require(unsupported["handled"] is False, "unsupported_not_handled", failures)

    status = module.bridge_status()
    checks += 1
    require(status["forge_replaced"] is False, "forge_not_replaced", failures)
    checks += 1
    require(status["model_called_for_covered_requests"] is False, "covered_no_model", failures)
    checks += 1
    require(status["full_qwen_ollama_replacement_complete"] is False, "replacement_not_overclaimed", failures)
    checks += 1
    require(status["unsupported_request_fallback_enabled"] is True, "fallback_visible", failures)

    main_path = repo / "main.py"
    source = main_path.read_text(encoding="utf-8")
    ast.parse(source, filename=str(main_path))

    markers = (
        "BEGIN FORGE LANGUAGE CORE REPLACEMENT BRIDGE 1",
        "forge-language-core-status",
        "forge-language-preview",
        "Forge deterministic language bridge v1",
        "language_bridge_handled",
        "ollama_fallback_used",
    )
    for marker in markers:
        checks += 1
        require(marker in source, f"main_marker_missing:{marker}", failures)

    interpreter_source = (
        repo / "forge_language_bridge_v1" / "interpreter.py"
    ).read_text(encoding="utf-8")

    forbidden = (
        "requests.",
        "urllib.",
        "subprocess.",
        "os.system",
        "Popen(",
        "socket.",
        "open(",
        "write_text(",
        "write_bytes(",
        "_call_ollama",
    )
    for marker in forbidden:
        checks += 1
        require(marker not in interpreter_source, f"forbidden_interpreter_marker:{marker}", failures)

    if failures:
        print("FORGE LANGUAGE BRIDGE 1 BEHAVIOR: FAIL")
        for failure in failures:
            print(f"FAIL - {failure}")
        return 1

    print("FORGE LANGUAGE BRIDGE 1 BEHAVIOR: PASS")
    print(f"checks_passed={checks}")
    print("covered_requests_call_llm=0")
    print("simulation_execution=0")
    print("source_writes=0")
    print("memory_writes=0")
    print("forge_replaced=0")
    print("unsupported_fallback_visible=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
