#!/usr/bin/env python3
"""Static structural verifier for the Forge / EchoForge separation slice.

This verifier does not import project source, call a model, start a service, or
write repository state.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from typing import Iterable


BASELINE_COMMIT = "1d7c4da0f524a5abad75962daa66d0eaa9a5bbce"

APPROVED_PATHS = frozenset(
    {
        "main.py",
        "agents/forge/agent.py",
        "agents/forge/llm_authority.py",
        "echoforge_advisory/__init__.py",
        "echoforge_advisory/contracts.py",
        "echoforge_advisory/provider.py",
        "echoforge_advisory/runtime.py",
        "scripts/AIWEB_FORGE_ECHOFORGE_LLM_AUTHORITY_SEPARATION_DECISION.md",
        "scripts/AIWEB_FORGE_ECHOFORGE_LLM_AUTHORITY_SEPARATION_RUNTIME_SPEC.md",
        "scripts/README_aiweb_forge_echoforge_llm_authority_separation.md",
        "scripts/aiweb_forge_echoforge_llm_authority_separation_verify.py",
        "scripts/test_aiweb_forge_echoforge_llm_authority_separation.py",
    }
)

EXPECTED_MODIFIED = frozenset({"main.py", "agents/forge/agent.py"})
EXPECTED_CREATED = APPROVED_PATHS - EXPECTED_MODIFIED

LEGACY_COMMANDS = frozenset(
    {
        "llm-engine-review-model-test",
        "llm-engine-review-draft",
        "llm-engine-review-batch-next",
        "llm-engine-review-batch-run",
        "llm-live-draft",
        "generic-repair-llm",
        "generic-repair-candidate-build",
        "generic-repair-candidate-verify",
        "generic-repair-review-llm",
        "generic-repair-review-verify",
        "generic-repair-sandbox-plan",
        "generic-repair-sandbox-run",
        "generic-sandbox-dependency-plan",
        "generic-sandbox-dependency-run",
        "generic-revision-llm",
        "generic-revision-candidate-build",
        "generic-revision-candidate-verify",
        "generic-revision-sandbox-plan",
        "generic-revision-sandbox-run",
        "generic-revision-loop-llm",
        "generic-revision-loop-candidate",
        "forge-command-implement",
        "forge-command-implement-review",
        "forge-command-implement-write",
        "forge-command-implement-install",
        "forge-tool-wrap",
        "forge-tool-wrap-install",
        "forge-self-suggest",
    }
)

COMMAND_FUNCTIONS = {
    "llm-engine-review-model-test": "cmd_llm_engine_review_model_test",
    "llm-engine-review-draft": "cmd_llm_engine_review_draft",
    "llm-engine-review-batch-next": "cmd_llm_engine_review_batch_next",
    "llm-engine-review-batch-run": "cmd_llm_engine_review_batch_run",
    "llm-live-draft": "cmd_llm_live_draft",
    "generic-repair-llm": "cmd_generic_repair_llm",
    "generic-repair-candidate-build": "cmd_generic_repair_candidate_build",
    "generic-repair-candidate-verify": "cmd_generic_repair_candidate_verify",
    "generic-repair-review-llm": "cmd_generic_repair_review_llm",
    "generic-repair-review-verify": "cmd_generic_repair_review_verify",
    "generic-repair-sandbox-plan": "cmd_generic_repair_sandbox_plan",
    "generic-repair-sandbox-run": "cmd_generic_repair_sandbox_run",
    "generic-sandbox-dependency-plan": "cmd_generic_sandbox_dependency_plan",
    "generic-sandbox-dependency-run": "cmd_generic_sandbox_dependency_run",
    "generic-revision-llm": "cmd_generic_revision_llm",
    "generic-revision-candidate-build": "cmd_generic_revision_candidate_build",
    "generic-revision-candidate-verify": "cmd_generic_revision_candidate_verify",
    "generic-revision-sandbox-plan": "cmd_generic_revision_sandbox_plan",
    "generic-revision-sandbox-run": "cmd_generic_revision_sandbox_run",
    "generic-revision-loop-llm": "cmd_generic_revision_loop_llm",
    "generic-revision-loop-candidate": "cmd_generic_revision_loop_candidate",
    "forge-command-implement": "cmd_forge_command_implement",
    "forge-command-implement-review": "cmd_forge_command_implement_review",
    "forge-command-implement-write": "cmd_forge_command_implement_write",
    "forge-command-implement-install": "cmd_forge_command_implement_install",
    "forge-tool-wrap": "cmd_forge_tool_wrap",
    "forge-tool-wrap-install": "cmd_forge_tool_wrap_install",
    "forge-self-suggest": "cmd_forge_self_suggest",
}

DIRECT_PROVIDER_FUNCTIONS = frozenset(
    {
        "_patch98_call_local_llm_for_review",
        "cmd_llm_engine_review_model_test",
        "cmd_llm_live_draft",
        "cmd_generic_repair_llm",
        "cmd_generic_repair_review_llm",
        "_p137_call_llm",
        "_p138_call_ollama",
        "_p139_call_ollama",
        "_p140_call_ollama_for_candidate_plan",
        "_p141_call_ollama",
        "_p142_call_ollama",
        "_p187_call_ollama",
    }
)

FROZEN_SHA256 = {
    "aiweb_language_core_bootstrap/verbal_cognition_gate_runtime/gate_composition/validation.py": "5a60906ab247ff7f5c3fac84068a845571811a3af064dc4e18e2b46506178dab",
    "forge_language_bridge_v5/__init__.py": "bf3012cbed31eea3b2a62177740dcec5f4014d55e346f1dfe002c141fb10ed2f",
    "forge_language_bridge_v5/eligibility_hold.py": "729b6d31931d18984c46daea9bfc522ec4135b23ddee5686fce55d5bee5f86e5",
    "forge_language_bridge_v5/runtime_builders.py": "050e1c57728124c3d1c44330e59af060bce39dd168f84709f17d27597daf9c6f",
    "agents/forge/memory.py": "15b27e594094fd33df4bf20aabe0210d4a4a42701c57641b51157fa85dfdcd6f",
    "agents/forge/permissions.py": "c4a1f6d771441911e1e71a95819301897f2106dfcf24a3918252fbcfa2c478ec",
    "agents/forge/runner.py": "ff555a5bf6a29a7aa50adc000c087ffaefb678c394dac929920e145a9a458d19",
    "agents/forge/tools.py": "0ad4582f73a2a4984e43ae177b1b9cfec66455dff8b238b911598c03664ddabc",
    "scripts/AIWEB_FORGE_LANGUAGE_CORE_BRIDGE5_DECISION.md": "f89549630e8ef41638b31ffc648fe42d7248fdd94878a7beacb25d1ecf68ec8e",
    "scripts/AIWEB_FORGE_LANGUAGE_CORE_BRIDGE5_EXACT_PAYLOAD_PATHS.txt": "404796040d6bc1b2c19a1c49e3d1d6efcbf3ab98bfecd7d8688d038ad95f13bb",
    "scripts/AIWEB_FORGE_LANGUAGE_CORE_BRIDGE5_PAYLOAD_SHA256SUMS.txt": "819125a918e2beb7808ceb526552b4599c68e1253e90c42bc60207a72c304ffa",
    "scripts/AIWEB_FORGE_LANGUAGE_CORE_BRIDGE5_PROTECTED_PREDECESSOR_SHA256SUMS.txt": "19ebec9f29f24e1585f44ee92c26d5a013420696cb5ce816b7ed5433258b0745",
    "scripts/AIWEB_FORGE_LANGUAGE_CORE_BRIDGE5_REMAINING_LLM_LANES.md": "7659d1c0759019819069e7d74b8ffae775a5f98692ff6e50600206a727dda88c",
    "scripts/AIWEB_FORGE_LANGUAGE_CORE_BRIDGE5_RUNTIME_SPEC.md": "2ece215b538160333e5950114af6cd0dfe58d35dd95a2aaf314c4e65298902a1",
    "scripts/AIWEB_FORGE_LANGUAGE_CORE_BRIDGE5_SOURCE_INSPECTION_RECORD.md": "714b4b638eb7cc6f97c591a631aefb6bc0cd3c84a43635676073e5764b3f3de9",
    "scripts/README_aiweb_forge_language_core_bridge5.md": "1e0ae34b0409b52f10db900b8d711208b03ee54553417db8253f0e460d9bc52c",
    "scripts/aiweb_forge_language_core_bridge5_verify.py": "98dd30b26eb3a44709be4ce1954c95d5c78036475df2007b0871146edd69e1d2",
    "scripts/test_aiweb_forge_language_core_bridge5_exact_gate_eligibility_hold.py": "61db42b479ba559ecf8bdcae77e1a38f12af062b938b1828b6461c6528f64bae",
}

BRIDGE_FUNCTION_AST_SHA256 = {
    "_flb1_interpret": "c82bbb570b8cbf5df9f88ba7ead28ef4cce1b740d7a96efb0e62cc8aa5cf5834",
    "_flb1_plan": "861abc32300cbc1b03c700a8f386e1a769059a7df4687a48d6a130d1c418ac79",
    "_flb2_status": "adba6cd7036ee136309f186bd07abc2259bc8f394cce94b3a4a605952301e18e",
    "_flb2_unsupported_plan": "d0b7c5b74a378128dfb6fb71025ae965c72a08cdbcdd24446bc4609e5c338500",
    "_flb2_unsupported": "6c3841f693a6a46bf7545a5c2c277beb61a89b434211bd3f06b5ee33245903ef",
    "_flb3_status": "ed3e73d633bb618623e221459e303bffab4f26fd833ed749fa633765763335bf",
    "_flb3_structural_preview": "db4e08753821a9b988c3bfce658039b8925b4212a1b7ea8ad9e68b934e3951d5",
    "_flb3_structural_plan": "07b2fd9e418acf144bdc63dd0bf0be3ba3a5012f05f64e6b28271f66f4f49819",
    "_flb4_status": "ea109e0b7a3df14660bf2e2cbf529885dd429a8891e84f736b212ceaa14ef17e",
    "_flb4_explicit_plan": "6edc5140cea6c40b81e5337cc7e58c29aa7106ecb8b1cbefaad159bb48947620",
    "_flb5_status": "196ed4e1aa60f2b71a902a0efaefe62cd8ed5669e4aa894cb5762cd56cf43972",
    "_flb5_explicit_plan": "64000e40292173bc4da54838129ca2adbc70de1af575fc8a8cd4dbdcd9c71525",
    "_flb1_print_decision": "601c529b942e9fc5ceacd165fc189d7cec795d197837ac63b304b74b7ed8bf0e",
    "cmd_forge_language_core_status": "0f8e81499a361e7655c4e403d8ceadbe3fc9fee479ab39f64ec33ade0116fa7f",
    "cmd_forge_language_preview": "f38e56cfa5c6ab0867df7e0f05ce587d14997700d1592bf5ebca4a470051a63d",
    "_flb4_print_explicit_plan": "e8e03aa375290336f0da79df8015a0b2a9e6fb969d21ea8a4ccbe65443e4d100",
    "cmd_forge_language_candidate": "4d8f6ee85bad115ad49607f2112547772cfcfb7a8b1b35e617ffdb590c7f0125",
    "cmd_forge_language_selection_hold": "7dbff35cdf3e0c8591fe4441f73dc7ced7d5a654ff1d8dda1f920fd866c18903",
    "cmd_forge_language_eligibility_hold": "38276c9d8e34dfce19c2a14ac6a396da2b09cbeb34a2c87924a44f8301273fcc",
    "_flb1_execute_interactive": "13f8a4e4431c35f6d29cdf50933f7e85f5b147878c184928c0056d36b961934d",
}


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_files(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if ".git" in relative.parts:
            continue
        normalized = PurePosixPath(*relative.parts).as_posix()
        files[normalized] = sha256_path(path)
    return files


def git_output(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed: {completed.stderr.strip()}"
        )
    return completed.stdout.strip()


def first_statement_is_refusal(function: ast.FunctionDef) -> bool:
    if not function.body:
        return False
    first = function.body[0]
    return (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Call)
        and isinstance(first.value.func, ast.Name)
        and first.value.func.id == "raise_forge_llm_authority_removed"
    )


def function_index(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }


def string_dict_keys(function: ast.FunctionDef) -> set[str]:
    keys: set[str] = set()
    for node in ast.walk(function):
        if not isinstance(node, ast.Dict):
            continue
        for key in node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.add(key.value)
    return keys


def import_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names.add(module)
            names.update(
                f"{module}.{alias.name}" if module else alias.name
                for alias in node.names
            )
    return names


def literal_registry(tree: ast.Module) -> set[str]:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name)
            and target.id == "LEGACY_FORGE_LLM_COMMANDS"
            for target in node.targets
        ):
            continue
        value = node.value
        if (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "frozenset"
            and len(value.args) == 1
        ):
            value = value.args[0]
        if isinstance(value, (ast.Set, ast.List, ast.Tuple)):
            result = set()
            for item in value.elts:
                if not (
                    isinstance(item, ast.Constant)
                    and isinstance(item.value, str)
                ):
                    raise ValueError("legacy registry contains non-literal item")
                result.add(item.value)
            return result
    raise ValueError("legacy command registry not found")


def verify(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    repo = Path(args.repo).resolve()
    failures: list[str] = []
    checks: dict[str, object] = {}

    if not repo.is_dir():
        return {"failures": [f"repository missing: {repo}"]}, 1

    for relative in APPROVED_PATHS:
        if not (repo / relative).is_file():
            failures.append(f"approved path missing: {relative}")

    actual_created: set[str] = set()
    actual_modified: set[str] = set()
    actual_deleted: set[str] = set()
    if args.baseline_root:
        baseline = Path(args.baseline_root).resolve()
        before = relative_files(baseline)
        after = relative_files(repo)
        actual_created = set(after) - set(before)
        actual_deleted = set(before) - set(after)
        actual_modified = {
            path
            for path in set(before).intersection(after)
            if before[path] != after[path]
        }
        checks["scope_source"] = "baseline_root"
    else:
        try:
            if args.mode == "applied":
                head = git_output(repo, "rev-parse", "HEAD")
                if head != BASELINE_COMMIT:
                    failures.append(
                        f"applied mode HEAD mismatch: {head} != {BASELINE_COMMIT}"
                    )
                diff_range = BASELINE_COMMIT
            else:
                parent = git_output(repo, "rev-parse", "HEAD^")
                if parent != BASELINE_COMMIT:
                    failures.append(
                        f"committed mode parent mismatch: {parent} != {BASELINE_COMMIT}"
                    )
                diff_range = f"{BASELINE_COMMIT}..HEAD"
            changed = set(
                filter(
                    None,
                    git_output(repo, "diff", "--name-only", diff_range).splitlines(),
                )
            )
            untracked = set(
                filter(
                    None,
                    git_output(
                        repo,
                        "ls-files",
                        "--others",
                        "--exclude-standard",
                    ).splitlines(),
                )
            )
            for path in changed | untracked:
                current = repo / path
                baseline_exists = (
                    subprocess.run(
                        [
                            "git",
                            "-C",
                            str(repo),
                            "cat-file",
                            "-e",
                            f"{BASELINE_COMMIT}:{path}",
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                    ).returncode
                    == 0
                )
                if not current.exists():
                    actual_deleted.add(path)
                elif baseline_exists:
                    actual_modified.add(path)
                else:
                    actual_created.add(path)
            checks["scope_source"] = "git"
        except RuntimeError as exc:
            failures.append(str(exc))

    actual_all = actual_created | actual_modified | actual_deleted
    if actual_all != set(APPROVED_PATHS):
        failures.append(
            "actual changed paths do not exactly match approved scope: "
            + json.dumps(
                {
                    "missing": sorted(set(APPROVED_PATHS) - actual_all),
                    "unexpected": sorted(actual_all - set(APPROVED_PATHS)),
                },
                sort_keys=True,
            )
        )
    if actual_created != set(EXPECTED_CREATED):
        failures.append(
            f"created paths mismatch: {sorted(actual_created)}"
        )
    if actual_modified != set(EXPECTED_MODIFIED):
        failures.append(
            f"modified paths mismatch: {sorted(actual_modified)}"
        )
    if actual_deleted:
        failures.append(f"deleted paths are prohibited: {sorted(actual_deleted)}")
    checks["actual_created"] = sorted(actual_created)
    checks["actual_modified"] = sorted(actual_modified)
    checks["actual_deleted"] = sorted(actual_deleted)

    frozen_verified = 0
    for relative, expected in FROZEN_SHA256.items():
        path = repo / relative
        if not path.is_file():
            failures.append(f"frozen path missing: {relative}")
            continue
        actual = sha256_path(path)
        if actual != expected:
            failures.append(
                f"frozen path changed: {relative} {actual} != {expected}"
            )
        else:
            frozen_verified += 1
    checks["frozen_hashes_verified"] = frozen_verified

    try:
        main_source = (repo / "main.py").read_text(encoding="utf-8")
        main_tree = ast.parse(main_source)
        main_functions = function_index(main_tree)
    except (OSError, SyntaxError) as exc:
        failures.append(f"main.py parse failed: {exc}")
        main_source = ""
        main_tree = ast.Module(body=[], type_ignores=[])
        main_functions = {}

    bridge_verified = 0
    for name, expected in BRIDGE_FUNCTION_AST_SHA256.items():
        function = main_functions.get(name)
        if function is None:
            failures.append(f"Bridge function missing: {name}")
            continue
        actual = hashlib.sha256(
            ast.dump(function, include_attributes=False).encode("utf-8")
        ).hexdigest()
        if actual != expected:
            failures.append(
                f"Bridge function changed: {name} {actual} != {expected}"
            )
        else:
            bridge_verified += 1
    checks["bridge_function_ast_hashes_verified"] = bridge_verified

    main_imports = import_names(main_tree)
    if any(name.startswith("agents.forge.agent") for name in main_imports):
        failures.append("main.py still imports agents.forge.agent")
    for node in ast.walk(main_tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "ForgeAgent":
                failures.append("main.py still constructs ForgeAgent")

    for name in ("cmd_run", "cmd_diag_paste", "cmd_diag_session"):
        function = main_functions.get(name)
        if function is None:
            failures.append(f"deterministic workshop function missing: {name}")
            continue
        argument_names = {
            item.arg
            for item in function.args.posonlyargs + function.args.args
        }
        if "agent" in argument_names:
            failures.append(f"{name} still accepts agent")

    for command, function_name in COMMAND_FUNCTIONS.items():
        function = main_functions.get(function_name)
        if function is None:
            failures.append(f"legacy command function missing: {function_name}")
        elif not first_statement_is_refusal(function):
            failures.append(
                f"legacy command is not guarded first: {command} / {function_name}"
            )

    for function_name in DIRECT_PROVIDER_FUNCTIONS:
        function = main_functions.get(function_name)
        if function is None:
            failures.append(f"direct provider function missing: {function_name}")
        elif not first_statement_is_refusal(function):
            failures.append(
                f"direct provider is not guarded first: {function_name}"
            )

    for function_name in ("_p199_build_dispatch", "_p201_make_handler"):
        function = main_functions.get(function_name)
        if function is None:
            failures.append(f"surface function missing: {function_name}")
            continue
        exposed = string_dict_keys(function).intersection(LEGACY_COMMANDS)
        if exposed:
            failures.append(
                f"{function_name} exposes legacy commands: {sorted(exposed)}"
            )

    run_session = main_functions.get("run_session")
    if run_session is None:
        failures.append("run_session missing")
    else:
        segment = ast.get_source_segment(main_source, run_session) or ""
        for required in (
            "_handle_forge_llm_refusal",
            "echoforge-advisory",
            "cmd_echoforge_advisory",
        ):
            if required not in segment:
                failures.append(f"run_session missing boundary: {required}")

    try:
        authority_source = (
            repo / "agents/forge/llm_authority.py"
        ).read_text(encoding="utf-8")
        authority_tree = ast.parse(authority_source)
        registry = literal_registry(authority_tree)
        if registry != set(LEGACY_COMMANDS):
            failures.append(
                "legacy registry mismatch: "
                + json.dumps(
                    {
                        "missing": sorted(set(LEGACY_COMMANDS) - registry),
                        "unexpected": sorted(registry - set(LEGACY_COMMANDS)),
                    },
                    sort_keys=True,
                )
            )
    except (OSError, SyntaxError, ValueError) as exc:
        failures.append(f"authority module validation failed: {exc}")

    try:
        agent_source = (repo / "agents/forge/agent.py").read_text(
            encoding="utf-8"
        )
        agent_tree = ast.parse(agent_source)
        agent_imports = import_names(agent_tree)
        prohibited_agent_imports = {
            name
            for name in agent_imports
            if name.startswith(
                (
                    "requests",
                    "agents.forge.tools",
                    "agents.forge.context_builder",
                    "agents.forge.memory",
                    "agents.forge.permissions",
                )
            )
        }
        if prohibited_agent_imports:
            failures.append(
                f"compatibility agent has prohibited imports: "
                f"{sorted(prohibited_agent_imports)}"
            )
        for prohibited in (
            "TOOL_DEFINITIONS",
            "dispatch(",
            "requests.",
            "record_tool_call",
            "OLLAMA_URL",
        ):
            if prohibited in agent_source:
                failures.append(
                    f"compatibility agent retains prohibited behavior: {prohibited}"
                )
    except (OSError, SyntaxError) as exc:
        failures.append(f"compatibility agent validation failed: {exc}")

    echo_paths = [
        repo / "echoforge_advisory/__init__.py",
        repo / "echoforge_advisory/contracts.py",
        repo / "echoforge_advisory/provider.py",
        repo / "echoforge_advisory/runtime.py",
    ]
    echo_trees: dict[str, ast.Module] = {}
    for path in echo_paths:
        try:
            echo_trees[path.name] = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError) as exc:
            failures.append(f"EchoForge module parse failed: {path}: {exc}")

    provider_tree = echo_trees.get("provider.py")
    if provider_tree is not None:
        for node in ast.walk(provider_tree):
            if isinstance(node, ast.Dict):
                for key in node.keys:
                    if (
                        isinstance(key, ast.Constant)
                        and key.value == "tools"
                    ):
                        failures.append("EchoForge provider sends tool definitions")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in {"subprocess", "pathlib"}:
                        failures.append(
                            f"EchoForge provider imports prohibited module: {alias.name}"
                        )
            if isinstance(node, ast.ImportFrom):
                if (node.module or "").startswith("agents.forge"):
                    failures.append(
                        "EchoForge provider imports Forge implementation"
                    )
            if isinstance(node, ast.Call):
                call_name = ast.unparse(node.func)
                if call_name in {
                    "open",
                    "Path.write_text",
                    "Path.write_bytes",
                    "subprocess.run",
                    "subprocess.Popen",
                }:
                    failures.append(
                        f"EchoForge provider has prohibited side effect: {call_name}"
                    )

    for module_name, tree in echo_trees.items():
        imports = import_names(tree)
        for imported in imports:
            if imported.startswith(
                (
                    "agents.forge.tools",
                    "agents.forge.runner",
                    "agents.forge.memory",
                    "agents.forge.permissions",
                    "agents.forge.patcher",
                    "agents.forge.applier",
                )
            ):
                failures.append(
                    f"EchoForge {module_name} imports Forge authority: {imported}"
                )

    runtime_source_path = repo / "echoforge_advisory/runtime.py"
    contracts_source_path = repo / "echoforge_advisory/contracts.py"
    try:
        runtime_source = runtime_source_path.read_text(encoding="utf-8")
        contracts_source = contracts_source_path.read_text(encoding="utf-8")
        for required in (
            "advisory_only: bool = True",
            "forge_authority: bool = False",
            "tool_calls_allowed: bool = False",
            "forge_action_executed: bool = False",
            "protected_memory_written: bool = False",
            "proof_claimed: bool = False",
        ):
            if required not in contracts_source:
                failures.append(f"advisory contract flag missing: {required}")
        if "ROLE_INSTRUCTIONS" not in runtime_source:
            failures.append("EchoForge role instruction registry missing")
    except OSError as exc:
        failures.append(f"EchoForge contract read failed: {exc}")

    checks.update(
        {
            "approved_paths": sorted(APPROVED_PATHS),
            "legacy_commands": len(LEGACY_COMMANDS),
            "direct_provider_guards": len(DIRECT_PROVIDER_FUNCTIONS),
            "forge_agent_imported_by_main": False
            if not any(
                name.startswith("agents.forge.agent")
                for name in main_imports
            )
            else True,
            "echoforge_tools_sent": False,
            "bridge5_selected_meaning_authority": False,
            "forge_llm_authority": False,
            "echoforge_advisory_only": True,
        }
    )

    result = {
        "schema": "aiweb.forge-echoforge-llm-authority-separation-verifier.v1",
        "mode": args.mode,
        "repo": str(repo),
        "baseline_commit": BASELINE_COMMIT,
        "status": "PASS" if not failures else "FAIL",
        "checks": checks,
        "failures": failures,
        "source_executed": False,
        "model_called": False,
        "service_started": False,
        "repository_written": False,
    }
    return result, 0 if not failures else 1


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument(
        "--mode",
        required=True,
        choices=("applied", "committed"),
    )
    parser.add_argument(
        "--baseline-root",
        help="External-build baseline tree; omit for a live Git repository.",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result, return_code = verify(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    print(
        "FORGE / ECHOFORGE LLM AUTHORITY SEPARATION VERIFIER: "
        + result.get("status", "FAIL")
    )
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
