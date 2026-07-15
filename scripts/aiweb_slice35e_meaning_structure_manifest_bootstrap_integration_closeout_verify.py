#!/usr/bin/env python3
"""Independent repository verifier for Slice 35E and Slice 35 closeout."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True

EXPECTED_PARENT_HEAD = "c08ef1ed38e3741a2abc110c4211bf800c0df11b"
EXPECTED_COMMIT_SUBJECT = (
    "Slice 35E MeaningStructureManifest bounded bootstrap integration and closeout"
)
EXACT_PATHS = (
    "aiweb_language_core_bootstrap/meaning_structure_manifest/bootstrap_integration.py",
    "scripts/AIWEB_SLICE35E_MSM_V1_BOOTSTRAP_INTEGRATION_RUNTIME_SPEC.md",
    "scripts/AIWEB_SLICE35_ACCEPTANCE_RECORD.md",
    "scripts/README_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.md",
    "scripts/aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py",
    "scripts/test_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py",
    "scripts/aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout_verify.py",
)

PROTECTED_HASHES = {
    'aiweb_language_core_bootstrap/__init__.py': '0fbf450ac772eadcc2271f21a7d46d649730063764477b12276c6228ebfef9d6',
    'aiweb_language_core_bootstrap/authority.py': '03bbcdb03c8502c19ff7a5fc377875aa474d43cb0b4eb6d4471091ca42ca3838',
    'aiweb_language_core_bootstrap/bootstrap_adapter/__init__.py': 'c02d5ed2f125b86745ace30d5218e548569821653d6d5ac53b65b6cee19b530a',
    'aiweb_language_core_bootstrap/bootstrap_adapter/adapter.py': '03282793f0c470c0769fcb784aedaa1885a9e7472d7b0bb49f8f02c0725f7cb3',
    'aiweb_language_core_bootstrap/bootstrap_adapter/fixtures.py': '66013a1f044c431c12ae24121be4d026d77f1923f75008100ac158ff01f81a13',
    'aiweb_language_core_bootstrap/bootstrap_adapter/schema.py': '7d5999cdc9c96de5ab1bc367e5972fe16cc559a3fdd30a3742749661bee4eaa7',
    'aiweb_language_core_bootstrap/boundary.py': '6b7fc05767b39c794deb84d5c09f30e1a0c5894841344ab72872500d9f6c4b90',
    'aiweb_language_core_bootstrap/component_loading/__init__.py': '51522fe211fb7d54b1878f53e748cd5ecbcf9f5c5eac86f9583357e85130035e',
    'aiweb_language_core_bootstrap/component_loading/fixtures.py': '90debe14d8cd8a4dcf696f9d50b96649172bcc4f8bce3f796bb98a5c15d4d6dc',
    'aiweb_language_core_bootstrap/component_loading/loader.py': '2c3d71e1f4ef0198d6bb1daff617c592dbacab4da713eb7ed4fa00b7fa0d5087',
    'aiweb_language_core_bootstrap/component_loading/schema.py': '1de36e896228bd10df0175afbead8f5c1eb14e04e8c368659f36c3583a0bd33d',
    'aiweb_language_core_bootstrap/component_loading/static_interfaces.py': 'cbe95f966f5cb04fda0fafcbae5f93306ac8b0da0b78de2041e92ebbdc54ef01',
    'aiweb_language_core_bootstrap/component_registry.py': 'd4d93800f510f97bacb0a9f0c531ea54f2804eb6c3dfcfa7f9c38a3301b7ac51',
    'aiweb_language_core_bootstrap/import_policy.py': 'f0c87e5775864cf97cc54842bdd9cebbc700ed32d9977ec71474b3c6c4d63b66',
    'aiweb_language_core_bootstrap/meaning_structure_manifest/__init__.py': '2395e0703593f2f95e620fb4a28bf08e9bbb1801e51e359f43f20cf040036836',
    'aiweb_language_core_bootstrap/meaning_structure_manifest/_enums.py': 'a25c47e508063e8b119337f2b27e3af382b91c105ec101467d960ec4ca2645f8',
    'aiweb_language_core_bootstrap/meaning_structure_manifest/_identity.py': '968054b4a53f65396e27f32a288250f8c1dae077dc8375746bd4ec6220d18f00',
    'aiweb_language_core_bootstrap/meaning_structure_manifest/_records.py': '2ed280f8dacecb5b0bef4828466e6c42aecb2deb1156bff8de75e4cda38139f9',
    'aiweb_language_core_bootstrap/meaning_structure_manifest/lifecycle.py': '387c2af39659cf67b480b0ba957f50459541236533f5b2d0f19b0248f37e283c',
    'aiweb_language_core_bootstrap/meaning_structure_manifest/serialization.py': '8486cf8b134d3d1af38e6b01b05328aaa2e489a44d2e32ffaee991677aa80ed5',
    'aiweb_language_core_bootstrap/meaning_structure_manifest/validation.py': '1fd284f1a4794b8054fa1913c3ff32fecab231fe814c253c59a71da47366a723',
    'aiweb_language_core_bootstrap/regression_containment/__init__.py': '9dd57a6a2f5c76625b45cde657db7e4da0309b00f7d0dbd88aa55c202c813c42',
    'aiweb_language_core_bootstrap/regression_containment/evaluator.py': '949f8735d638c6626e542b3e38fcabce70ca046689b44259ddf1bc29deb6bb9d',
    'aiweb_language_core_bootstrap/regression_containment/policy.py': 'e0f88f0ab07fa17ab46cae731ba121298b44d337fd2ea1a0faa6cf9a2c9ad2c6',
    'aiweb_language_core_bootstrap/regression_containment/schema.py': '42836cfc497fdabb4f5f530c3bab8a492b47497745f0f1d315f6d0cd2fdd34e6',
    'aiweb_language_core_bootstrap/schema.py': '4c33a6321d32497eed63679bcd144b67d0962972df712d4452e94d1f38f45500',
    'aiweb_language_core_bootstrap/trace_receipt/__init__.py': '41599980091954e391350a3e5c26b0b3f297b2b747ef143b58a6064222a9ada3',
    'aiweb_language_core_bootstrap/trace_receipt/assembler.py': '0e7c78014daecc4981048953604a1df017c986b1187808a7db9db08855c83d39',
    'aiweb_language_core_bootstrap/trace_receipt/flow_catalog.py': '1884dfde6c073dc8ab6c94a5797ef0bdff4260314a7896c8c96eaa616da5fad3',
    'aiweb_language_core_bootstrap/trace_receipt/schema.py': 'fd013a52c50e71c6829c08499436f3777de9463e33473b6cc1cf7f84ed8f1121',
    'aiweb_language_core_bootstrap/verify.py': '5729b003f5610ce52afbd19fdf901c7a33ab8c6dde9fc8fea9dc6e4be646f5da',
}

INHERITED_COMMANDS = (
    ("slice24-source-behavior", "scripts/test_aiweb_slice24_full_regression_acceptance_bundle_scaffold.py"),
    ("slice30-behavior", "scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py"),
    ("slice31-behavior", "scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py"),
    ("slice32-behavior", "scripts/test_aiweb_slice32_accepted_boundary_component_loading.py"),
    ("slice33-behavior", "scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py"),
    ("slice34-behavior", "scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py"),
    ("slice35a-behavior", "scripts/test_aiweb_slice35a_meaning_structure_manifest_core_schema.py"),
    ("slice35b-behavior", "scripts/test_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.py"),
    ("slice35b-verifier", "scripts/aiweb_slice35b_meaning_structure_manifest_deterministic_validation_verify.py"),
    ("slice35c-behavior", "scripts/test_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.py"),
    ("slice35c-verifier", "scripts/aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law_verify.py"),
    ("slice35d-behavior", "scripts/test_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.py"),
    ("slice35d-verifier", "scripts/aiweb_slice35d_meaning_structure_manifest_canonical_serialization_verify.py"),
)

PROHIBITED_IMPORT_ROOTS = {
    "aiohttp", "chromadb", "httpx", "numpy", "ollama", "openai",
    "os", "pathlib", "qdrant_client", "requests", "socket", "sqlite3",
    "subprocess", "torch", "transformers", "urllib",
}
PROHIBITED_CALL_NAMES = {
    "Popen", "connect", "mkdir", "open", "remove", "rename", "replace",
    "rmdir", "run", "system", "unlink", "urlopen", "write_bytes",
    "write_text",
}

EXPECTED_EXPORTS = (
    "INTEGRATION_SCHEMA_VERSION",
    "INTEGRATION_SPEC_ID",
    "INTEGRATION_SPEC_VERSION",
    "MsmBootstrapFixtureRecord",
    "MsmBootstrapIntegrationResult",
    "MsmBootstrapIntegrationState",
    "REASON_COMPLETED",
    "REASON_DISABLED",
    "STATUS_COMPLETED",
    "STATUS_HELD_INVALID_BOOTSTRAP",
    "STATUS_HELD_INVALID_FIXTURE",
    "STATUS_HELD_INVALID_MANIFEST",
    "STATUS_HELD_INVALID_STATE",
    "STATUS_HELD_ROUND_TRIP_MISMATCH",
    "STATUS_HELD_SERIALIZATION_FAILURE",
    "STATUS_REFUSED_DISABLED",
    "build_msm_bootstrap_integration_state",
    "build_synthetic_msm_bootstrap_fixture",
    "run_msm_bootstrap_integration",
    "validate_msm_bootstrap_fixture",
    "validate_msm_bootstrap_integration_result",
    "validate_msm_bootstrap_integration_state",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def run_python(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/usr/bin/python3", "-B", *args],
        cwd=str(repo),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        env={
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPYCACHEPREFIX": "/tmp/aiweb_slice35e_verifier_cache",
            "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        },
    )


def call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("--mode", choices=("precommit", "committed"), required=True)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    passes: list[str] = []
    failures: list[str] = []

    inside = git(repo, "rev-parse", "--is-inside-work-tree")
    if inside.returncode == 0 and inside.stdout.strip() == "true":
        passes.append("target is a Git repository")
    else:
        failures.append("target is not a Git repository")

    for relative in EXACT_PATHS:
        if (repo / relative).is_file():
            passes.append(f"required Slice 35E path exists: {relative}")
        else:
            failures.append(f"required Slice 35E path missing: {relative}")

    head = git(repo, "rev-parse", "HEAD")
    if head.returncode == 0 and args.mode == "precommit" and head.stdout.strip() == EXPECTED_PARENT_HEAD:
        passes.append("precommit HEAD is exact accepted Slice 35D HEAD")
    elif args.mode == "precommit":
        failures.append("precommit HEAD mismatch: " + head.stdout.strip())

    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0:
        failures.append("git status failed: " + status.stderr.strip())
    else:
        lines = tuple(line for line in status.stdout.splitlines() if line)
        if args.mode == "precommit":
            expected = {f"?? {path}" for path in EXACT_PATHS}
            if set(lines) == expected and len(lines) == len(EXACT_PATHS):
                passes.append("precommit status contains exactly seven new paths")
            else:
                failures.append("precommit status mismatch: " + " | ".join(lines))
        elif lines:
            failures.append("committed mode requires clean status: " + " | ".join(lines))
        else:
            passes.append("committed status is clean")

    if args.mode == "committed":
        parent = git(repo, "rev-parse", "HEAD^")
        subject = git(repo, "show", "-s", "--format=%s", "HEAD")
        changed = git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD")
        if parent.returncode == 0 and parent.stdout.strip() == EXPECTED_PARENT_HEAD:
            passes.append("committed parent is exact accepted Slice 35D HEAD")
        else:
            failures.append("committed parent mismatch: " + parent.stdout.strip())
        if subject.returncode == 0 and subject.stdout.strip() == EXPECTED_COMMIT_SUBJECT:
            passes.append("committed subject exact")
        else:
            failures.append("committed subject mismatch: " + subject.stdout.strip())
        changed_paths = tuple(line for line in changed.stdout.splitlines() if line)
        if set(changed_paths) == set(EXACT_PATHS) and len(changed_paths) == len(EXACT_PATHS):
            passes.append("commit contains exactly seven Slice 35E paths")
        else:
            failures.append("commit changed path mismatch: " + " | ".join(changed_paths))

    for relative, expected in PROTECTED_HASHES.items():
        path = repo / relative
        if not path.is_file():
            failures.append(f"protected path missing: {relative}")
        elif sha256_file(path) != expected:
            failures.append(f"protected hash mismatch: {relative}")
        else:
            passes.append(f"protected hash preserved: {relative}")

    for relative in EXACT_PATHS:
        path = repo / relative
        if path.suffix == ".py" and path.is_file():
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                compile(tree, str(path), "exec")
                passes.append(f"Python syntax valid: {relative}")
            except Exception as exc:
                failures.append(f"Python syntax invalid: {relative}:{type(exc).__name__}")

    runtime_path = repo / EXACT_PATHS[0]
    if runtime_path.is_file():
        tree = ast.parse(runtime_path.read_text(encoding="utf-8"), filename=str(runtime_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if root in PROHIBITED_IMPORT_ROOTS:
                        failures.append(f"prohibited runtime import: {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                root = (node.module or "").split(".", 1)[0]
                if root in PROHIBITED_IMPORT_ROOTS:
                    failures.append(f"prohibited runtime import: {node.module}")
            elif isinstance(node, ast.Call):
                name = call_name(node)
                if name in PROHIBITED_CALL_NAMES:
                    failures.append(f"prohibited runtime call: {name}")

    bootstrap_init = (repo / "aiweb_language_core_bootstrap/__init__.py").read_text(encoding="utf-8")
    msm_init = (repo / "aiweb_language_core_bootstrap/meaning_structure_manifest/__init__.py").read_text(encoding="utf-8")
    if "bootstrap_integration" in bootstrap_init:
        failures.append("bootstrap root automatically imports Slice 35E")
    else:
        passes.append("bootstrap root does not automatically import Slice 35E")
    if "bootstrap_integration" in msm_init:
        failures.append("MSM root automatically imports Slice 35E")
    else:
        passes.append("MSM root does not automatically import Slice 35E")

    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    try:
        module = importlib.import_module(
            "aiweb_language_core_bootstrap.meaning_structure_manifest.bootstrap_integration"
        )
    except Exception as exc:
        failures.append(f"Slice 35E import failed: {type(exc).__name__}:{exc}")
    else:
        actual_exports = tuple(module.__all__)
        if actual_exports == EXPECTED_EXPORTS:
            passes.append("Slice 35E export surface exact and ordered")
        else:
            failures.append("Slice 35E export surface mismatch")
        for name in EXPECTED_EXPORTS:
            if hasattr(module, name):
                passes.append(f"export exists: {name}")
            else:
                failures.append(f"export missing: {name}")

    for label, relative in INHERITED_COMMANDS:
        completed = run_python(repo, relative)
        if completed.returncode == 0:
            passes.append(f"inherited command passed: {label}")
        else:
            failures.append(
                f"inherited command failed: {label}:rc={completed.returncode}:"
                f"stdout={completed.stdout.strip()}:stderr={completed.stderr.strip()}"
            )

    behavior = run_python(
        repo,
        "scripts/test_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py",
    )
    if (
        behavior.returncode == 0
        and "SLICE 35E BEHAVIOR TEST: PASS" in behavior.stdout
        and "runtime_network_memory_delivery_tool_action_attempts=0" in behavior.stdout
    ):
        passes.append("Slice 35E behavior and containment proof passed")
    else:
        failures.append(
            "Slice 35E behavior proof failed: rc=" + str(behavior.returncode)
            + ":stdout=" + behavior.stdout.strip()
            + ":stderr=" + behavior.stderr.strip()
        )

    requirements = run_python(
        repo,
        "scripts/aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py",
        "--list-requirements",
    )
    if requirements.returncode == 0 and '"disabled_by_default":true' in requirements.stdout:
        passes.append("requirements CLI passed")
    else:
        failures.append("requirements CLI failed")

    disabled = run_python(
        repo,
        "scripts/aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py",
    )
    if disabled.returncode == 2 and '"status":"refused_msm_bootstrap_integration_disabled"' in disabled.stdout:
        passes.append("default CLI refusal exact")
    else:
        failures.append("default CLI refusal failed")

    enabled = run_python(
        repo,
        "scripts/aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py",
        "--enable-offline-msm-bootstrap-integration",
    )
    if enabled.returncode == 0 and '"status":"completed_bounded_msm_bootstrap_integration"' in enabled.stdout:
        passes.append("explicit offline integration CLI passed")
    else:
        failures.append("explicit offline integration CLI failed")

    print("AI.WEB SLICE 35E INDEPENDENT VERIFIER")
    print(f"mode={args.mode}")
    print(f"pass_count={len(passes)}")
    print(f"failure_count={len(failures)}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print("SLICE 35E INDEPENDENT VERIFIER: FAIL")
        return 1
    print("SLICE 35E INDEPENDENT VERIFIER: PASS")
    print(f"protected_predecessor_files={len(PROTECTED_HASHES)}")
    print(f"inherited_commands={len(INHERITED_COMMANDS)}")
    print("slice35_closeout_candidate=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
