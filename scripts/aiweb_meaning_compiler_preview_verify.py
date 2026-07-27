#!/usr/bin/env python3
"""Independent structural and behavioral verifier for the meaning preview."""

from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ENDPOINT = "/api/operator/ask-forge/language-core-preview"
REQUIRED_PATHS = (
    "aiweb_language_core_bootstrap/meaning_compiler_preview/__init__.py",
    "aiweb_language_core_bootstrap/meaning_compiler_preview/schema.py",
    "rmc_engine_v1/meaning_compiler_preview.py",
    "scripts/test_aiweb_meaning_compiler_preview.py",
    "scripts/test_aiweb_ask_forge_language_core_preview_route.py",
    "scripts/aiweb_meaning_compiler_preview_verify.py",
    "scripts/README_aiweb_meaning_compiler_preview.md",
)
BEHAVIOR_TESTS = (
    "scripts/test_aiweb_meaning_compiler_preview.py",
    "scripts/test_aiweb_ask_forge_language_core_preview_route.py",
)
FORBIDDEN_IMPORT_ROOTS = {
    "aiohttp",
    "anthropic",
    "chromadb",
    "httpx",
    "langchain",
    "llama_index",
    "numpy",
    "ollama",
    "openai",
    "os",
    "pathlib",
    "requests",
    "sentence_transformers",
    "sklearn",
    "socket",
    "sqlite3",
    "subprocess",
    "tensorflow",
    "tiktoken",
    "torch",
    "transformers",
    "urllib",
}
FORBIDDEN_CALLS = {
    "__import__",
    "compile",
    "eval",
    "exec",
    "open",
    "os.getenv",
    "os.system",
    "socket.create_connection",
    "socket.socket",
    "subprocess.Popen",
    "subprocess.call",
    "subprocess.run",
    "urllib.request.urlopen",
}
FORBIDDEN_RUNTIME_IMPORT_PREFIXES = (
    "aiweb_language_core_bootstrap.deterministic_language_runtime.tokenization",
    "rmc_engine_v1.memory_recaller",
    "rmc_engine_v1.resonance_lexicon",
    "rmc_engine_v1.llm_renderer",
)


class Ledger:
    def __init__(self) -> None:
        self.checks = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str) -> None:
        self.checks += 1
        if condition is not True:
            self.failures.append(label)
            print("FAIL - " + label)


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return (prefix + "." if prefix else "") + node.attr
    return ""


def _imports(tree: ast.AST) -> tuple[str, ...]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return tuple(names)


def _handler_segment(main_source: str) -> str:
    marker = f'_p281_req_path == "{ENDPOINT}"'
    start = main_source.find(marker)
    if start < 0:
        return ""
    next_branch = main_source.find("\n            elif ", start + len(marker))
    return main_source[start : next_branch if next_branch >= 0 else start + 3000]


def _run(command: list[str], *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=180,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args()
    repo = args.repo.expanduser().resolve()
    ledger = Ledger()

    ledger.check((repo / ".git").is_dir(), "Forge git repository exists")
    for relative in REQUIRED_PATHS:
        ledger.check((repo / relative).is_file(), "required path exists: " + relative)

    package = repo / "aiweb_language_core_bootstrap/meaning_compiler_preview"
    runtime_paths = tuple(sorted(package.glob("*.py"))) if package.is_dir() else ()
    adapter = repo / "rmc_engine_v1/meaning_compiler_preview.py"
    if adapter.is_file():
        runtime_paths += (adapter,)
    ledger.check(len(runtime_paths) >= 3, "meaning preview has a real multi-module runtime plus adapter")

    # Inspect syntax/imports/calls structurally. False-valued boundary fields such
    # as vector_used=False are intentionally legal and are never rejected by a
    # substring scan.
    for path in runtime_paths:
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
            compile(tree, str(path), "exec")
        except Exception as error:
            ledger.check(False, f"runtime AST compiles: {path.relative_to(repo)}: {error}")
            continue
        ledger.check(True, "runtime AST compiles: " + path.relative_to(repo).as_posix())
        imported_names = _imports(tree)
        for imported in imported_names:
            root = imported.split(".", 1)[0]
            ledger.check(
                root not in FORBIDDEN_IMPORT_ROOTS,
                f"runtime forbidden import absent: {path.relative_to(repo)}:{imported}",
            )
            ledger.check(
                not imported.startswith(FORBIDDEN_RUNTIME_IMPORT_PREFIXES),
                f"legacy token/overlap/model runtime import absent: {path.relative_to(repo)}:{imported}",
            )
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = _call_name(node.func)
                ledger.check(
                    name not in FORBIDDEN_CALLS,
                    f"runtime forbidden call absent: {path.relative_to(repo)}:{name}",
                )

    sys.path.insert(0, str(repo))
    try:
        from aiweb_language_core_bootstrap.meaning_compiler_preview import (
            build_rmc_context_record,
            build_rmc_context_snapshot,
            compile_meaning_preview,
            meaning_compiler_preview_boundary,
        )
        from rmc_engine_v1.meaning_compiler_preview import (
            ENDPOINT as ADAPTER_ENDPOINT,
            build_language_core_preview_response,
        )

        ledger.check(callable(compile_meaning_preview), "public compiler callable")
        ledger.check(callable(build_rmc_context_record), "public RMC record builder callable")
        ledger.check(callable(build_rmc_context_snapshot), "public RMC snapshot builder callable")
        ledger.check(callable(meaning_compiler_preview_boundary), "public boundary callable")
        ledger.check(callable(build_language_core_preview_response), "public adapter callable")
        ledger.check(ADAPTER_ENDPOINT == ENDPOINT, "public adapter endpoint exact")
        boundary_record = meaning_compiler_preview_boundary()
        boundary = (
            boundary_record
            if isinstance(boundary_record, dict)
            else boundary_record.to_dict()
        )
        ledger.check(boundary.get("preview_only") is True, "boundary preview only")
        for key in (
            "normalization_performed",
            "tokenization_performed",
            "model_token_stream_created",
            "subword_token_stream_created",
            "numeric_token_ids_created",
            "model_called",
            "embedding_used",
            "vector_used",
            "similarity_scoring_used",
            "filesystem_read_performed",
            "filesystem_write_performed",
            "network_access_performed",
            "environment_access_performed",
            "memory_write_performed",
            "tool_routing_performed",
            "action_performed",
            "delivery_performed",
        ):
            ledger.check(boundary.get(key) is False, "boundary false " + key)
    except Exception as error:
        ledger.check(False, f"public import contract: {type(error).__name__}:{error}")

    main_source = (repo / "main.py").read_text(encoding="utf-8") if (repo / "main.py").is_file() else ""
    ledger.check('"route_key":"ask_forge_language_core_preview"' in main_source, "route manifest key")
    ledger.check(f'"method":"POST","path":"{ENDPOINT}"' in main_source, "route manifest method/path")
    ledger.check(f'_p281_req_path == "{ENDPOINT}"' in main_source, "POST route branch")
    segment = _handler_segment(main_source)
    ledger.check("_language_core_preview_api_v1(req)" in segment, "POST route uses bounded adapter")
    ledger.check("req = None" in segment, "malformed JSON fails through typed adapter contract")
    ledger.check("str(e)" not in segment and "str(error)" not in segment, "route hides raw exceptions")
    ledger.check('elif self.path == "/api/operator/ask-forge/math-trace":' in main_source, "GP-015 route retained")
    ledger.check("_gp015_ask_forge_math_trace_surface_v1(question)" in main_source, "GP-015 adapter retained")

    readme = (repo / "scripts/README_aiweb_meaning_compiler_preview.md").read_text(encoding="utf-8") if (repo / "scripts/README_aiweb_meaning_compiler_preview.md").is_file() else ""
    for phrase in (
        "Human words remain the input",
        "does not create an LLM-style token stream",
        "read-only RMC snapshot",
        ENDPOINT,
        "/api/operator/ask-forge/math-trace",
    ):
        ledger.check(phrase in readme, "README declares " + phrase)

    selected_python = repo / ".venv/bin/python3"
    py = str(selected_python) if selected_python.is_file() else sys.executable
    with tempfile.TemporaryDirectory(prefix="aiweb-meaning-preview-verify-") as temporary:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONPYCACHEPREFIX"] = str(Path(temporary) / "python-cache")
        env["PYTHONPATH"] = str(repo)
        for relative in BEHAVIOR_TESTS:
            result = _run([py, "-B", str(repo / relative), str(repo)], cwd=repo, env=env)
            print("=== " + relative + " ===")
            print(result.stdout, end="")
            ledger.check(result.returncode == 0, "behavior command passes: " + relative)

    summary = {
        "ok": not ledger.failures,
        "checks": ledger.checks,
        "failures": ledger.failures,
        "endpoint": ENDPOINT,
        "runtime_files_checked": len(runtime_paths),
        "behavior_tests": list(BEHAVIOR_TESTS),
        "authority": {
            "model": False,
            "model_tokens": False,
            "embedding": False,
            "vector": False,
            "similarity": False,
            "filesystem": False,
            "network": False,
            "write": False,
            "tool": False,
            "action": False,
            "delivery": False,
        },
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    print("AIWEB_MEANING_COMPILER_PREVIEW_VERIFY=" + ("PASS" if not ledger.failures else "FAIL"))
    return 0 if not ledger.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
