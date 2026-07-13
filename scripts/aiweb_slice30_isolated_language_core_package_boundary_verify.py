#!/usr/bin/env python3
"""Repository verifier for Slice 30 isolated language-core package boundary."""

from __future__ import annotations

import argparse
import ast
import hashlib
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True

EXACT_PATHS = (
    "aiweb_language_core_bootstrap/__init__.py",
    "aiweb_language_core_bootstrap/authority.py",
    "aiweb_language_core_bootstrap/schema.py",
    "aiweb_language_core_bootstrap/component_registry.py",
    "aiweb_language_core_bootstrap/import_policy.py",
    "aiweb_language_core_bootstrap/boundary.py",
    "aiweb_language_core_bootstrap/verify.py",
    "scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py",
    "scripts/aiweb_slice30_isolated_language_core_package_boundary_verify.py",
    "scripts/README_aiweb_slice30_isolated_language_core_package_boundary.md",
)

REPAIR_PATHS = (
    "aiweb_language_core_bootstrap/component_registry.py",
    "scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py",
    "scripts/aiweb_slice30_isolated_language_core_package_boundary_verify.py",
)

RUNTIME_FILES = tuple(
    path
    for path in EXACT_PATHS
    if path.startswith("aiweb_language_core_bootstrap/")
    and path.endswith(".py")
)

ALLOWED_RUNTIME_IMPORT_ROOTS = {
    "__future__",
    "dataclasses",
    "typing",
    "hashlib",
    "json",
    "aiweb_language_core_bootstrap",
}

PROTECTED_HASHES = {
    "main.py":
        "73c382c3ffe496587e4d73df46dafd08345a3e7b0d64fc05b83ecdd4eddcc557",
    "requirements.txt":
        "ed73ba11243a0099034f10ac500db984959bb8f37086532f864d75a3620916c8",
    "setup.sh":
        "a90d3a77930f34f4fff5680739d1894e780b17115965ae9ccc595946ee866876",
    "rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py":
        "431e6c2133a06204131f81276c11b05528ed8e6553a0d5590555ffd23ef38473",
    "rmc_engine_v1/general_pipeline/symbolic_math_operator_language_realizer.py":
        "f1f2486504bb987d705efee70d775c1549d3597f5153d30e87cbf11f38bedf1a",
    "rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json":
        "e99c7691d0ba951343bdf80a82d65d19e464b660bedd942b9a9db2b16283c93e",
    "scripts/test_operator_guided_language_realizer_build_langexpr001_gp014.py":
        "d047b3ca07c13e4e29ab55f9aa8fb357ee87a1a7d649ea2b23f68f30b75af3be",
    "scripts/operator_guided_language_realizer_build_langexpr001_gp014_verify.py":
        "c84800156011727cd49f743b722502c60f555c109859ff79aa399cb32ae4d797",
}

PROHIBITED_RUNTIME_CALL_ATTRIBUTES = {
    "open",
    "write_text",
    "write_bytes",
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
    "get",
    "put",
    "patch",
    "delete",
    "request",
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


def package_source_identity(
    repo: Path,
    package_name: str,
) -> tuple[int, str]:
    package_root = repo / package_name
    paths = sorted(
        path
        for path in package_root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and not path.name.endswith((".pyc", ".pyo"))
    )
    payload = "".join(
        f"{path.relative_to(repo).as_posix()}\t{sha256_file(path)}\n"
        for path in paths
    ).encode("utf-8")
    return len(paths), hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument(
        "--mode",
        choices=("precommit", "repair-precommit", "committed"),
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
                passes.append("precommit status contains exactly ten new paths")
            else:
                failures.append(
                    "precommit status mismatch: "
                    + " | ".join(status_lines)
                )
        elif args.mode == "repair-precommit":
            expected = {f" M {path}" for path in REPAIR_PATHS}
            if set(status_lines) == expected:
                passes.append(
                    "repair-precommit status contains exactly three modified paths"
                )
            else:
                failures.append(
                    "repair-precommit status mismatch: "
                    + " | ".join(status_lines)
                )
        else:
            if status_lines:
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
                f"protected hash mismatch: {relative}: {actual}"
            )
        else:
            passes.append(f"protected hash preserved: {relative}")

    for relative in EXACT_PATHS:
        path = repo / relative
        if path.suffix != ".py" or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text, filename=str(path))
            passes.append(f"Python syntax valid: {relative}")
        except SyntaxError as exc:
            failures.append(f"Python syntax invalid: {relative}: {exc}")
            continue

        if relative in RUNTIME_FILES:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if root_name(alias.name) not in ALLOWED_RUNTIME_IMPORT_ROOTS:
                            failures.append(
                                f"runtime import not allowed: {relative}: {alias.name}"
                            )
                elif isinstance(node, ast.ImportFrom):
                    if node.level:
                        continue
                    if root_name(node.module) not in ALLOWED_RUNTIME_IMPORT_ROOTS:
                        failures.append(
                            f"runtime import not allowed: {relative}: {node.module}"
                        )
                elif isinstance(node, ast.Name):
                    if node.id.lower() in PROHIBITED_RUNTIME_IDENTIFIERS:
                        failures.append(
                            f"prohibited runtime identifier: "
                            f"{relative}:{getattr(node, 'lineno', 0)}:{node.id}"
                        )
                elif isinstance(node, ast.Call):
                    function = node.func
                    if isinstance(function, ast.Name):
                        call_name = function.id
                    elif isinstance(function, ast.Attribute):
                        call_name = function.attr
                    else:
                        call_name = ""
                    if call_name.lower() in PROHIBITED_RUNTIME_CALL_ATTRIBUTES:
                        failures.append(
                            f"runtime side-effect call prohibited: "
                            f"{relative}:{getattr(node, 'lineno', 0)}:{call_name}"
                        )

    init_text = (
        repo
        / "aiweb_language_core_bootstrap/__init__.py"
    ).read_text(encoding="utf-8")
    if ".verify" in init_text or "verify_bootstrap_boundary_bundle" in init_text:
        failures.append("__init__.py must not import verify.py")
    else:
        passes.append("__init__.py does not import verify.py")

    cache_entries = []
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
            "source-tree cache entries present: " + " | ".join(cache_entries)
        )
    else:
        passes.append("no source-tree Python cache entries")

    repo_text = str(repo)
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)

    from aiweb_language_core_bootstrap import (
        build_bootstrap_boundary_bundle,
        validate_bootstrap_authority_state,
        validate_bootstrap_boundary_record,
        validate_component_registry_record,
        validate_import_policy_record,
    )

    bundle = build_bootstrap_boundary_bundle()
    reports = (
        validate_bootstrap_authority_state(bundle.authority),
        validate_component_registry_record(bundle.registry),
        validate_import_policy_record(bundle.import_policy),
        validate_bootstrap_boundary_record(
            bundle.boundary,
            authority=bundle.authority,
            registry=bundle.registry,
            import_policy=bundle.import_policy,
        ),
    )
    if all(report.ok for report in reports):
        passes.append("all package records validate")
    else:
        failures.append(
            "package record validation failed: "
            + " | ".join(
                issue.code
                for report in reports
                for issue in report.issues
            )
        )

    if bundle.registry.component_count != 15:
        failures.append("registry component count is not 15")
    elif any(
        item.runtime_import_authorized or item.component_loaded
        for item in bundle.registry.components
    ):
        failures.append("registry contains loaded or import-authorized component")
    else:
        passes.append("registry has 15 registered-not-loaded components")

    for component in bundle.registry.components:
        actual_count, actual_digest = package_source_identity(
            repo,
            component.package_name,
        )
        if actual_count != component.file_count:
            failures.append(
                "component source file count mismatch: "
                f"{component.package_name}:"
                f"expected={component.file_count}:actual={actual_count}"
            )
        elif actual_digest != component.package_digest:
            failures.append(
                "component source digest mismatch: "
                f"{component.package_name}:"
                f"expected={component.package_digest}:actual={actual_digest}"
            )
        else:
            passes.append(
                "component source identity preserved: "
                f"{component.package_name}"
            )

    print("=" * 72)
    print("AIWEB SLICE 30 ISOLATED LANGUAGE-CORE PACKAGE BOUNDARY VERIFIER")
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
