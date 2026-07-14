#!/usr/bin/env python3
"""Repository verifier for Slice 31 disabled-by-default bootstrap adapter."""

from __future__ import annotations

import argparse
import ast
import hashlib
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True

EXACT_PATHS = ('aiweb_language_core_bootstrap/bootstrap_adapter/__init__.py', 'aiweb_language_core_bootstrap/bootstrap_adapter/schema.py', 'aiweb_language_core_bootstrap/bootstrap_adapter/fixtures.py', 'aiweb_language_core_bootstrap/bootstrap_adapter/adapter.py', 'scripts/aiweb_slice31_disabled_bootstrap_adapter.py', 'scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py', 'scripts/README_aiweb_slice31_disabled_bootstrap_adapter.md', 'scripts/aiweb_slice31_disabled_bootstrap_adapter_verify.py')

RUNTIME_FILES = tuple(
    path
    for path in EXACT_PATHS
    if path.startswith(
        "aiweb_language_core_bootstrap/bootstrap_adapter/"
    )
    and path.endswith(".py")
)

PROTECTED_HASHES = {'main.py': '73c382c3ffe496587e4d73df46dafd08345a3e7b0d64fc05b83ecdd4eddcc557', 'requirements.txt': 'ed73ba11243a0099034f10ac500db984959bb8f37086532f864d75a3620916c8', 'setup.sh': 'a90d3a77930f34f4fff5680739d1894e780b17115965ae9ccc595946ee866876', 'rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py': '431e6c2133a06204131f81276c11b05528ed8e6553a0d5590555ffd23ef38473', 'rmc_engine_v1/general_pipeline/symbolic_math_operator_language_realizer.py': 'f1f2486504bb987d705efee70d775c1549d3597f5153d30e87cbf11f38bedf1a', 'rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json': 'e99c7691d0ba951343bdf80a82d65d19e464b660bedd942b9a9db2b16283c93e', 'scripts/test_operator_guided_language_realizer_build_langexpr001_gp014.py': 'd047b3ca07c13e4e29ab55f9aa8fb357ee87a1a7d649ea2b23f68f30b75af3be', 'scripts/operator_guided_language_realizer_build_langexpr001_gp014_verify.py': 'c84800156011727cd49f743b722502c60f555c109859ff79aa399cb32ae4d797', 'aiweb_language_core_bootstrap/__init__.py': '0fbf450ac772eadcc2271f21a7d46d649730063764477b12276c6228ebfef9d6', 'aiweb_language_core_bootstrap/authority.py': '03bbcdb03c8502c19ff7a5fc377875aa474d43cb0b4eb6d4471091ca42ca3838', 'aiweb_language_core_bootstrap/boundary.py': '6b7fc05767b39c794deb84d5c09f30e1a0c5894841344ab72872500d9f6c4b90', 'aiweb_language_core_bootstrap/component_registry.py': 'd4d93800f510f97bacb0a9f0c531ea54f2804eb6c3dfcfa7f9c38a3301b7ac51', 'aiweb_language_core_bootstrap/import_policy.py': 'f0c87e5775864cf97cc54842bdd9cebbc700ed32d9977ec71474b3c6c4d63b66', 'aiweb_language_core_bootstrap/schema.py': '4c33a6321d32497eed63679bcd144b67d0962972df712d4452e94d1f38f45500', 'aiweb_language_core_bootstrap/verify.py': '5729b003f5610ce52afbd19fdf901c7a33ab8c6dde9fc8fea9dc6e4be646f5da', 'scripts/README_aiweb_slice30_isolated_language_core_package_boundary.md': '32b2d088419e33cfa79c8e5bceed5019378b7639f7b85a531fc1258b3665b468', 'scripts/aiweb_slice30_isolated_language_core_package_boundary_verify.py': '404d90901d2a5875f56f57bb012c23ead1ddde534cd95bd2fdbecd9b9a939e9b', 'scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py': '25697b064168175bc6e9a43aabfbfd50196198b4e617ff19e668eb4923502679'}

ALLOWED_RUNTIME_IMPORT_ROOTS = {
    "__future__",
    "dataclasses",
    "typing",
    "hashlib",
    "json",
    "aiweb_language_core_bootstrap",
}

PROHIBITED_RUNTIME_IDENTIFIERS = {
    "requests",
    "httpx",
    "urllib",
    "socket",
    "aiohttp",
    "grpc",
    "ollama",
    "qwen",
    "chromadb",
    "chroma",
    "langchain",
    "faiss",
    "transformers",
    "torch",
    "tensorflow",
    "sklearn",
    "importlib",
    "pkgutil",
    "subprocess",
    "os",
    "sys",
    "time",
    "datetime",
    "random",
    "uuid",
}

PROHIBITED_RUNTIME_CALL_NAMES = {
    "open",
    "eval",
    "exec",
    "compile",
    "__import__",
    "input",
}

PROHIBITED_RUNTIME_CALL_ATTRIBUTES = {
    "write",
    "write_text",
    "write_bytes",
    "read_text",
    "read_bytes",
    "unlink",
    "rename",
    "replace",
    "mkdir",
    "rmdir",
    "touch",
    "system",
    "popen",
    "run",
    "call",
    "check_call",
    "check_output",
    "post",
    "put",
    "patch",
    "delete",
    "request",
    "connect",
    "send",
    "recv",
}

PROHIBITED_CLI_IMPORT_ROOTS = {
    "requests",
    "httpx",
    "urllib",
    "socket",
    "aiohttp",
    "grpc",
    "ollama",
    "qwen",
    "chromadb",
    "chroma",
    "langchain",
    "faiss",
    "transformers",
    "torch",
    "tensorflow",
    "sklearn",
    "subprocess",
    "os",
    "time",
    "datetime",
    "random",
    "uuid",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(repo: Path, *args: str) -> tuple[int, str, str]:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    )
    return completed.returncode, completed.stdout, completed.stderr


def root_name(module: str | None) -> str:
    if not module:
        return ""
    return module.split(".", 1)[0]


def call_name(node: ast.Call) -> str:
    function = node.func
    if isinstance(function, ast.Name):
        return function.id
    if isinstance(function, ast.Attribute):
        return function.attr
    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument(
        "--mode",
        choices=("precommit", "committed"),
        required=True,
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    failures: list[str] = []
    passes: list[str] = []

    if not (repo / ".git").is_dir():
        failures.append("target is not a Git repository")
    else:
        passes.append("target is a Git repository")

    for relative in EXACT_PATHS:
        path = repo / relative
        if path.is_file():
            passes.append(f"required path exists: {relative}")
        else:
            failures.append(f"required path missing: {relative}")

    code, status, stderr = git(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if code != 0:
        failures.append(f"git status failed: {stderr.strip()}")
    else:
        status_lines = [line for line in status.splitlines() if line.strip()]
        if args.mode == "precommit":
            expected = {f"?? {path}" for path in EXACT_PATHS}
            if set(status_lines) == expected:
                passes.append("precommit status contains exactly eight new paths")
            else:
                failures.append(
                    "precommit status mismatch: " + " | ".join(status_lines)
                )
        elif status_lines:
            failures.append(
                "committed mode requires clean status: "
                + " | ".join(status_lines)
            )
        else:
            passes.append("committed status is clean")

    for relative, expected in PROTECTED_HASHES.items():
        path = repo / relative
        if not path.is_file():
            failures.append(f"protected path missing: {relative}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            failures.append(
                f"protected hash mismatch: {relative}:{actual}"
            )
        else:
            passes.append(f"protected hash preserved: {relative}")

    parsed: dict[str, ast.AST] = {}
    for relative in EXACT_PATHS:
        path = repo / relative
        if path.suffix != ".py" or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text, filename=str(path))
            parsed[relative] = tree
            passes.append(f"Python syntax valid: {relative}")
        except SyntaxError as exc:
            failures.append(
                f"Python syntax invalid: {relative}:{exc}"
            )

    for relative in RUNTIME_FILES:
        tree = parsed.get(relative)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if root_name(alias.name) not in ALLOWED_RUNTIME_IMPORT_ROOTS:
                        failures.append(
                            f"runtime import not allowed: "
                            f"{relative}:{alias.name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    continue
                if root_name(node.module) not in ALLOWED_RUNTIME_IMPORT_ROOTS:
                    failures.append(
                        f"runtime import not allowed: "
                        f"{relative}:{node.module}"
                    )
            elif isinstance(node, ast.Name):
                if node.id.lower() in PROHIBITED_RUNTIME_IDENTIFIERS:
                    failures.append(
                        f"prohibited runtime identifier: "
                        f"{relative}:{getattr(node, 'lineno', 0)}:"
                        f"{node.id}"
                    )
            elif isinstance(node, ast.Call):
                name = call_name(node).lower()
                if name in PROHIBITED_RUNTIME_CALL_NAMES:
                    failures.append(
                        f"runtime call prohibited: "
                        f"{relative}:{getattr(node, 'lineno', 0)}:{name}"
                    )
                if name in PROHIBITED_RUNTIME_CALL_ATTRIBUTES:
                    failures.append(
                        f"runtime side-effect call prohibited: "
                        f"{relative}:{getattr(node, 'lineno', 0)}:{name}"
                    )

    cli_relative = "scripts/aiweb_slice31_disabled_bootstrap_adapter.py"
    cli_tree = parsed.get(cli_relative)
    if cli_tree is not None:
        for node in ast.walk(cli_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if root_name(alias.name) in PROHIBITED_CLI_IMPORT_ROOTS:
                        failures.append(
                            f"CLI prohibited import: {alias.name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if root_name(node.module) in PROHIBITED_CLI_IMPORT_ROOTS:
                    failures.append(
                        f"CLI prohibited import: {node.module}"
                    )
            elif isinstance(node, ast.Call):
                name = call_name(node).lower()
                if name in PROHIBITED_RUNTIME_CALL_ATTRIBUTES:
                    failures.append(
                        f"CLI side-effect call prohibited: "
                        f"{getattr(node, 'lineno', 0)}:{name}"
                    )

    parent_init = (
        repo / "aiweb_language_core_bootstrap/__init__.py"
    ).read_text(encoding="utf-8")
    if "bootstrap_adapter" in parent_init:
        failures.append(
            "parent package must not automatically import Slice 31 adapter"
        )
    else:
        passes.append(
            "parent package does not automatically import Slice 31 adapter"
        )

    cache_entries: list[str] = []
    excluded = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
        ".cache",
    }
    for walk_root, dirs, names in os.walk(repo, topdown=True):
        root = Path(walk_root)
        kept = []
        for dirname in dirs:
            if dirname in excluded:
                continue
            if dirname == "__pycache__":
                cache_entries.append(
                    (root / dirname).relative_to(repo).as_posix()
                )
                continue
            kept.append(dirname)
        dirs[:] = kept
        for name in names:
            if name.endswith((".pyc", ".pyo")):
                cache_entries.append(
                    (root / name).relative_to(repo).as_posix()
                )
    if cache_entries:
        failures.append(
            "source-tree cache entries present: "
            + " | ".join(cache_entries)
        )
    else:
        passes.append("no source-tree Python cache entries")

    repo_text = str(repo)
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)

    from aiweb_language_core_bootstrap import (
        build_bootstrap_boundary_bundle,
    )
    from aiweb_language_core_bootstrap.bootstrap_adapter import (
        FIXTURE_DISABLED_DEFAULT,
        FIXTURE_EXPLICIT_OFFLINE_INSPECTION,
        STATUS_COMPLETED_INSPECTION,
        STATUS_REFUSED_DISABLED,
        build_bootstrap_adapter_state,
        get_bootstrap_fixture,
        list_bootstrap_fixtures,
        run_bootstrap_fixture,
        validate_bootstrap_adapter_result,
        validate_bootstrap_adapter_state,
        validate_bootstrap_fixture_record,
        validate_fixture_provenance_record,
    )

    bundle = build_bootstrap_boundary_bundle()
    fixtures = list_bootstrap_fixtures()
    if len(fixtures) != 2:
        failures.append("fixture catalog count is not two")
    elif tuple(item.fixture_name for item in fixtures) != (
        FIXTURE_DISABLED_DEFAULT,
        FIXTURE_EXPLICIT_OFFLINE_INSPECTION,
    ):
        failures.append("fixture catalog identity or order mismatch")
    else:
        passes.append("exact two-fixture catalog preserved")

    for fixture in fixtures:
        fixture_report = validate_bootstrap_fixture_record(fixture)
        provenance_report = validate_fixture_provenance_record(
            fixture.provenance
        )
        if not fixture_report.ok or not provenance_report.ok:
            failures.append(
                f"fixture validation failed: {fixture.fixture_name}"
            )
        elif (
            not fixture.provenance.synthetic
            or not fixture.provenance.internal_only
            or not fixture.provenance.runtime_prohibited
            or fixture.provenance.evidence
            or fixture.provenance.memory
            or fixture.provenance.runtime_corpus
            or fixture.provenance.public_output
            or fixture.provenance.external_resource_derived
            or fixture.provenance.private_source_derived
            or fixture.provenance.trace_derived
            or fixture.provenance.memory_derived
        ):
            failures.append(
                f"fixture category boundary failed: {fixture.fixture_name}"
            )
        else:
            passes.append(
                f"fixture provenance and safety valid: "
                f"{fixture.fixture_name}"
            )

    default_state = build_bootstrap_adapter_state()
    explicit_state = build_bootstrap_adapter_state(
        explicit_offline_developer_enable=True
    )
    if (
        not validate_bootstrap_adapter_state(default_state).ok
        or default_state.enabled
    ):
        failures.append("default adapter state is not valid and disabled")
    else:
        passes.append("adapter is disabled by default")
    if (
        not validate_bootstrap_adapter_state(explicit_state).ok
        or not explicit_state.enabled
        or not explicit_state.fixture_only
        or not explicit_state.offline_only
    ):
        failures.append("explicit offline fixture adapter state invalid")
    else:
        passes.append("explicit adapter remains offline and fixture-only")

    disabled_fixture = get_bootstrap_fixture(FIXTURE_DISABLED_DEFAULT)
    explicit_fixture = get_bootstrap_fixture(
        FIXTURE_EXPLICIT_OFFLINE_INSPECTION
    )
    if disabled_fixture is None or explicit_fixture is None:
        failures.append("required fixture lookup failed")
    else:
        disabled_result = run_bootstrap_fixture(
            disabled_fixture,
            adapter_state=default_state,
        )
        explicit_result = run_bootstrap_fixture(
            explicit_fixture,
            adapter_state=explicit_state,
        )
        repeat_result = run_bootstrap_fixture(
            explicit_fixture,
            adapter_state=explicit_state,
        )

        if (
            disabled_result.status != STATUS_REFUSED_DISABLED
            or disabled_result.observation is not None
        ):
            failures.append("disabled-default fixture did not refuse")
        else:
            passes.append("disabled-default fixture refuses")

        if (
            explicit_result.status != STATUS_COMPLETED_INSPECTION
            or explicit_result.observation is None
            or not validate_bootstrap_adapter_result(explicit_result).ok
        ):
            failures.append("explicit offline fixture inspection failed")
        else:
            passes.append("explicit offline fixture inspection validates")

        if explicit_result != repeat_result:
            failures.append("explicit fixture result is not deterministic")
        else:
            passes.append("explicit fixture result is deterministic")

        if explicit_result.observation is not None:
            observation = explicit_result.observation
            if (
                observation.bootstrap_boundary_id
                != bundle.boundary.bootstrap_boundary_id
                or observation.component_registry_id
                != bundle.registry.registry_id
                or observation.component_count != 15
            ):
                failures.append(
                    "fixture observation does not preserve Slice 30 identity"
                )
            else:
                passes.append(
                    "fixture observation preserves Slice 30 identity"
                )

    if any(
        item.component_loaded or item.runtime_import_authorized
        for item in bundle.registry.components
    ):
        failures.append("Slice 31 loaded or import-authorized a component")
    else:
        passes.append("all 15 components remain registered-not-loaded")

    authority_state = explicit_state
    forbidden_values = (
        authority_state.component_loading_allowed,
        authority_state.dynamic_loading_allowed,
        authority_state.network_allowed,
        authority_state.filesystem_read_allowed,
        authority_state.filesystem_write_allowed,
        authority_state.runtime_connected,
        authority_state.main_connected,
        authority_state.route_connected,
        authority_state.ui_connected,
        authority_state.external_resource_allowed,
        authority_state.memory_write_allowed,
        authority_state.evidence_mutation_allowed,
        authority_state.delivery_allowed,
        authority_state.tool_routing_allowed,
        authority_state.action_allowed,
        authority_state.gp014_import_allowed,
        authority_state.gp014_call_allowed,
        authority_state.production_ready,
        authority_state.release_authorized,
    )
    if any(forbidden_values):
        failures.append("explicit adapter contains prohibited authority")
    else:
        passes.append("explicit adapter contains no prohibited authority")

    print("=" * 72)
    print("AIWEB SLICE 31 DISABLED-BY-DEFAULT BOOTSTRAP ADAPTER VERIFIER")
    print("=" * 72)
    print(f"Target repo: {repo}")
    print(f"Mode: {args.mode}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")

    if failures:
        print("VERDICT: FAIL")
        return 1
    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
