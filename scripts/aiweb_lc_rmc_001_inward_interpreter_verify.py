#!/usr/bin/env python3
"""Structural and behavioral verifier for an applied LC-RMC-001 candidate."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


EXPECTED_PATHS = (
    "aiweb_language_core_bootstrap/deterministic_language_runtime/__init__.py",
    "aiweb_language_core_bootstrap/deterministic_language_runtime/authority.py",
    "aiweb_language_core_bootstrap/deterministic_language_runtime/forge_profile.py",
    "aiweb_language_core_bootstrap/deterministic_language_runtime/grammar.py",
    "aiweb_language_core_bootstrap/deterministic_language_runtime/interpreter.py",
    "aiweb_language_core_bootstrap/deterministic_language_runtime/morphology.py",
    "aiweb_language_core_bootstrap/deterministic_language_runtime/schema.py",
    "aiweb_language_core_bootstrap/deterministic_language_runtime/tokenization.py",
    "rmc_engine_v1/language_core_phase_adapter.py",
    "rmc_engine_v1/memory_recaller.py",
    "rmc_engine_v1/candidate_generator.py",
    "rmc_engine_v1/phase_parser.py",
    "scripts/README_aiweb_lc_rmc_001_inward_interpreter.md",
    "scripts/aiweb_lc_rmc_001_inward_interpreter_verify.py",
    "scripts/test_aiweb_lc_rmc_001_inward_interpreter.py",
)

FORBIDDEN_IMPORT_PREFIXES = (
    "chromadb",
    "httpx",
    "langchain",
    "numpy",
    "ollama",
    "openai",
    "requests",
    "sentence_transformers",
    "sklearn",
    "socket",
    "subprocess",
    "torch",
    "transformers",
)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _imports(path: Path) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            values.append(node.module)
    return tuple(values)


def _check(condition: bool, code: str, detail: str, failures: list[dict[str, str]]) -> None:
    if not condition:
        failures.append({"code": code, "detail": detail})


def verify(repo: Path, mode: str) -> dict[str, Any]:
    failures: list[dict[str, str]] = []
    for relative in EXPECTED_PATHS:
        _check(
            (repo / relative).is_file(),
            "MISSING_PATH",
            relative,
            failures,
        )
    if failures:
        return {"ok": False, "mode": mode, "failures": failures}

    governed_python = [
        repo / relative
        for relative in EXPECTED_PATHS
        if relative.endswith(".py")
        and not relative.startswith("scripts/")
    ]
    for path in governed_python:
        try:
            imports = _imports(path)
        except (OSError, SyntaxError) as error:
            failures.append(
                {"code": "PYTHON_PARSE_FAILURE", "detail": f"{path.name}:{error}"}
            )
            continue
        for imported in imports:
            _check(
                not imported.startswith(FORBIDDEN_IMPORT_PREFIXES),
                "FORBIDDEN_IMPORT",
                f"{path.relative_to(repo)}:{imported}",
                failures,
            )

    phase_source = (repo / "rmc_engine_v1/phase_parser.py").read_text(
        encoding="utf-8"
    )
    _check(
        "result = interpret_phase(source_text, source_metadata)" in phase_source,
        "PHASE_DELEGATION_MISSING",
        "parse_phase must delegate to interpret_phase",
        failures,
    )
    for forbidden in (
        "_rank_phases",
        "_contains_symbolic_literal",
        "fallback:unclassified_input_treated_as_seed",
    ):
        _check(
            forbidden not in phase_source,
            "LEGACY_HEURISTIC_PRESENT",
            forbidden,
            failures,
        )

    profile_source = (
        repo
        / "aiweb_language_core_bootstrap/deterministic_language_runtime/forge_profile.py"
    ).read_text(encoding="utf-8")
    _check(
        "action_root_by_key(" in profile_source
        and "predicate_for_action_root_id(" in profile_source
        and "frame_by_key(" in profile_source
        and "role_by_key(" in profile_source,
        "EXACT_REGISTRY_LOOKUP_MISSING",
        "runtime must use accepted exact-key registry identities",
        failures,
    )
    _check(
        "all_admitted_action_roots" not in profile_source
        and "all_admitted_frames" not in profile_source,
        "REGISTRY_ORDER_SELECTION_PRESENT",
        "runtime may not select by registry iteration",
        failures,
    )

    sys.path.insert(0, str(repo))
    try:
        from aiweb_language_core_bootstrap.deterministic_language_runtime import (
            interpret_source,
            runtime_authority_boundary,
        )
        from rmc_engine_v1.phase_parser import parse_phase
        from rmc_engine_v1.memory_recaller import build_trace_spine
        from rmc_engine_v1.candidate_generator import generate_candidates

        positive = interpret_source("Please verify the packet checksum.")
        negative = interpret_source("Do not verify the packet checksum.")
        ambiguity = interpret_source(
            "Inspect the repository with the audit."
        )
        refusal = interpret_source("Delete the repository.")
        phase = parse_phase("Inspect the current build status.")
        boundary = runtime_authority_boundary()
        _check(
            positive.status == "INTERPRETED"
            and positive.candidates[0].action_root_key == "verify",
            "POSITIVE_BEHAVIOR_FAILURE",
            "verify source did not derive verify",
            failures,
        )
        _check(
            negative.status == "INTERPRETED"
            and negative.candidates[0].negated is True,
            "NEGATION_FAILURE",
            "negation was not preserved",
            failures,
        )
        _check(
            ambiguity.status == "AMBIGUOUS"
            and len(ambiguity.candidates) == 2
            and all(not item.selected for item in ambiguity.candidates),
            "AMBIGUITY_FAILURE",
            "attachment ambiguity was not preserved",
            failures,
        )
        _check(
            refusal.status == "REFUSED"
            and not refusal.candidates,
            "REFUSAL_FAILURE",
            "unsupported predicate did not fail closed",
            failures,
        )
        _check(
            phase.get("status") == "OK"
            and phase.get("phase_state", {}).get("action_root_key") == "inspect"
            and phase.get("fallback_performed") is False,
            "RMC_ADAPTER_FAILURE",
            "phase adapter did not preserve the stable entrypoint",
            failures,
        )
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary) / "forge"
            for relative in (
                "memory/context_library_v1/receipts",
                "memory/context_library_v1/manifests",
                "memory/context_library_v1/symbolic_maps",
                "memory/rmc_dataset_v1",
            ):
                (temporary_root / relative).mkdir(
                    parents=True, exist_ok=True
                )
            accepted_trace = build_trace_spine(
                "Inspect the current build status.",
                root=temporary_root,
            )
            accepted_generation = generate_candidates(accepted_trace)
            _check(
                accepted_trace.get("status") == "OK"
                and accepted_generation.get("status") == "OK"
                and bool(accepted_generation.get("candidate_set")),
                "RMC_ACCEPTED_TRACE_FAILURE",
                "admitted Language Core trace did not reach candidate generation",
                failures,
            )
            for source, expected_reason in (
                (
                    "Delete the repository.",
                    "LC_RMC_001_UNSUPPORTED_PREDICATE",
                ),
                (
                    "Inspect the repository with the audit.",
                    "LC_RMC_001_AMBIGUOUS_MEANING_HELD",
                ),
                (
                    "Do not verify the packet checksum.",
                    "LC_RMC_001_NEGATED_ACTION_HELD",
                ),
            ):
                held_trace = build_trace_spine(
                    source, root=temporary_root
                )
                held_generation = generate_candidates(held_trace)
                _check(
                    held_trace.get("status") == "BLOCKED"
                    and held_trace.get("reason_code") == expected_reason
                    and held_generation.get("status") == "BLOCKED"
                    and held_generation.get("reason_code") == expected_reason
                    and held_generation.get("candidate_set") == []
                    and held_generation.get("selected_candidate_preview")
                    is None,
                    "RMC_LANGUAGE_CORE_HOLD_FAILURE",
                    f"{source}:{expected_reason}",
                    failures,
                )

            missing_custody = generate_candidates({
                "status": "OK",
                "symbolic_trace": {
                    "Φ_t": {"phase_primary": "Φ6"}
                },
            })
            _check(
                missing_custody.get("status") == "BLOCKED"
                and missing_custody.get("reason_code")
                == "LC_RMC_001_LANGUAGE_CORE_CUSTODY_MISSING"
                and missing_custody.get("candidate_set") == [],
                "RMC_MISSING_CUSTODY_FAILURE",
                "candidate generator admitted a trace without Language Core",
                failures,
            )

            tampered = copy.deepcopy(accepted_trace)
            tampered["symbolic_trace"]["Φ_t"]["phase_primary"] = "Φ8"
            tampered["symbolic_trace"]["Φ_t"][
                "phase_path_hypothesis"
            ] = ["Φ8"]
            tampered_generation = generate_candidates(tampered)
            _check(
                tampered_generation.get("status") == "BLOCKED"
                and tampered_generation.get("reason_code")
                == "LC_RMC_001_LANGUAGE_CORE_CUSTODY_MISMATCH"
                and tampered_generation.get("candidate_set") == [],
                "RMC_TAMPERED_CUSTODY_FAILURE",
                "candidate generator admitted a phase altered after interpretation",
                failures,
            )
        _check(
            all(
                boundary.get(key) is False
                for key in (
                    "calls_llm",
                    "uses_embeddings",
                    "uses_vector_store",
                    "uses_rag",
                    "uses_semantic_similarity",
                    "writes_files",
                    "writes_memory",
                    "routes_tools",
                    "executes_actions",
                    "renders_output",
                    "delivers_output",
                    "grants_permission",
                )
            ),
            "AUTHORITY_BOUNDARY_FAILURE",
            "runtime boundary grants prohibited authority",
            failures,
        )
    except Exception as error:
        failures.append(
            {
                "code": "RUNTIME_IMPORT_OR_BEHAVIOR_FAILURE",
                "detail": f"{type(error).__name__}:{error}",
            }
        )

    test_command = [
        sys.executable,
        str(repo / "scripts/test_aiweb_lc_rmc_001_inward_interpreter.py"),
        "--mode",
        mode,
    ]
    completed = subprocess.run(
        test_command,
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=120,
    )
    _check(
        completed.returncode == 0,
        "BEHAVIOR_TEST_FAILURE",
        completed.stdout[-3000:],
        failures,
    )

    return {
        "ok": not failures,
        "mode": mode,
        "expected_path_count": len(EXPECTED_PATHS),
        "payload_sha256": {
            relative: _sha(repo / relative)
            for relative in EXPECTED_PATHS
        },
        "behavior_test_exit_code": completed.returncode,
        "failures": failures,
        "authority": {
            "llm": False,
            "embedding": False,
            "vector": False,
            "rag": False,
            "route": False,
            "tool": False,
            "execution": False,
            "output": False,
            "delivery": False,
            "memory_write": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument(
        "--mode",
        choices=("isolated", "live"),
        default="live",
    )
    args = parser.parse_args()
    repo = args.repo.expanduser().resolve()
    if not repo.is_dir():
        print(
            json.dumps(
                {"ok": False, "error": f"repository not found: {repo}"},
                sort_keys=True,
            )
        )
        return 2
    result = verify(repo, args.mode)
    print(json.dumps(result, sort_keys=True))
    if result["ok"]:
        print("AIWEB_LC_RMC_001_INWARD_INTERPRETER_VERIFY=PASS")
        return 0
    print("AIWEB_LC_RMC_001_INWARD_INTERPRETER_VERIFY=FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
