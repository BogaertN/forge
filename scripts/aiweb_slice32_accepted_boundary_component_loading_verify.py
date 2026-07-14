#!/usr/bin/env python3
"""Independent verifier for Slice 32 R1 strict loaded-component identity."""

from __future__ import annotations

import argparse
import ast
import hashlib
from pathlib import Path
import subprocess
import sys

R1_EXACT_PATHS = (
    "aiweb_language_core_bootstrap/component_loading/schema.py",
    "scripts/test_aiweb_slice32_accepted_boundary_component_loading.py",
    "scripts/aiweb_slice32_accepted_boundary_component_loading_verify.py",
)

PROTECTED_HASHES = {'aiweb_language_core_bootstrap/__init__.py': '0fbf450ac772eadcc2271f21a7d46d649730063764477b12276c6228ebfef9d6',
 'aiweb_language_core_bootstrap/authority.py': '03bbcdb03c8502c19ff7a5fc377875aa474d43cb0b4eb6d4471091ca42ca3838',
 'aiweb_language_core_bootstrap/bootstrap_adapter/__init__.py': 'c02d5ed2f125b86745ace30d5218e548569821653d6d5ac53b65b6cee19b530a',
 'aiweb_language_core_bootstrap/bootstrap_adapter/adapter.py': '03282793f0c470c0769fcb784aedaa1885a9e7472d7b0bb49f8f02c0725f7cb3',
 'aiweb_language_core_bootstrap/bootstrap_adapter/fixtures.py': '66013a1f044c431c12ae24121be4d026d77f1923f75008100ac158ff01f81a13',
 'aiweb_language_core_bootstrap/bootstrap_adapter/schema.py': '7d5999cdc9c96de5ab1bc367e5972fe16cc559a3fdd30a3742749661bee4eaa7',
 'aiweb_language_core_bootstrap/boundary.py': '6b7fc05767b39c794deb84d5c09f30e1a0c5894841344ab72872500d9f6c4b90',
 'aiweb_language_core_bootstrap/component_loading/__init__.py': '51522fe211fb7d54b1878f53e748cd5ecbcf9f5c5eac86f9583357e85130035e',
 'aiweb_language_core_bootstrap/component_loading/fixtures.py': '90debe14d8cd8a4dcf696f9d50b96649172bcc4f8bce3f796bb98a5c15d4d6dc',
 'aiweb_language_core_bootstrap/component_loading/loader.py': '2c3d71e1f4ef0198d6bb1daff617c592dbacab4da713eb7ed4fa00b7fa0d5087',
 'aiweb_language_core_bootstrap/component_loading/static_interfaces.py': 'cbe95f966f5cb04fda0fafcbae5f93306ac8b0da0b78de2041e92ebbdc54ef01',
 'aiweb_language_core_bootstrap/component_registry.py': 'd4d93800f510f97bacb0a9f0c531ea54f2804eb6c3dfcfa7f9c38a3301b7ac51',
 'aiweb_language_core_bootstrap/import_policy.py': 'f0c87e5775864cf97cc54842bdd9cebbc700ed32d9977ec71474b3c6c4d63b66',
 'aiweb_language_core_bootstrap/schema.py': '4c33a6321d32497eed63679bcd144b67d0962972df712d4452e94d1f38f45500',
 'aiweb_language_core_bootstrap/verify.py': '5729b003f5610ce52afbd19fdf901c7a33ab8c6dde9fc8fea9dc6e4be646f5da',
 'main.py': '73c382c3ffe496587e4d73df46dafd08345a3e7b0d64fc05b83ecdd4eddcc557',
 'requirements.txt': 'ed73ba11243a0099034f10ac500db984959bb8f37086532f864d75a3620916c8',
 'rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py': '431e6c2133a06204131f81276c11b05528ed8e6553a0d5590555ffd23ef38473',
 'rmc_engine_v1/general_pipeline/symbolic_math_operator_language_realizer.py': 'f1f2486504bb987d705efee70d775c1549d3597f5153d30e87cbf11f38bedf1a',
 'rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json': 'e99c7691d0ba951343bdf80a82d65d19e464b660bedd942b9a9db2b16283c93e',
 'scripts/README_aiweb_slice30_isolated_language_core_package_boundary.md': '32b2d088419e33cfa79c8e5bceed5019378b7639f7b85a531fc1258b3665b468',
 'scripts/README_aiweb_slice31_disabled_bootstrap_adapter.md': '859ca9aa5ff706a2ff5771815c0c113f6749907971c4754a3252ff8a267ccca6',
 'scripts/README_aiweb_slice32_accepted_boundary_component_loading.md': '4f7fa9b9502b274a88481de4f954b4a7159c9edfa70da1f24a1079c43b1e8bd4',
 'scripts/aiweb_slice30_isolated_language_core_package_boundary_verify.py': '404d90901d2a5875f56f57bb012c23ead1ddde534cd95bd2fdbecd9b9a939e9b',
 'scripts/aiweb_slice31_disabled_bootstrap_adapter.py': '3a6068b7b8021142994c0ba4820e83b0fa74494c7a453afbb27d89637f56f1aa',
 'scripts/aiweb_slice31_disabled_bootstrap_adapter_verify.py': '6f2e291202741964d14684899f7913d5c5836d9d4047b23113599ae778a2ff76',
 'scripts/aiweb_slice32_accepted_boundary_component_loading.py': '8b46394d0a573b21be08838867b08eb40ce7ea2b812eec1a2ee1027ef6df510f',
 'scripts/operator_guided_language_realizer_build_langexpr001_gp014_verify.py': 'c84800156011727cd49f743b722502c60f555c109859ff79aa399cb32ae4d797',
 'scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py': '25697b064168175bc6e9a43aabfbfd50196198b4e617ff19e668eb4923502679',
 'scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py': 'e0971900ced6f11b168d5ac82d383eb60ce7da6a16fdd82b41866223ac3cb099',
 'scripts/test_operator_guided_language_realizer_build_langexpr001_gp014.py': 'd047b3ca07c13e4e29ab55f9aa8fb357ee87a1a7d649ea2b23f68f30b75af3be',
 'setup.sh': 'a90d3a77930f34f4fff5680739d1894e780b17115965ae9ccc595946ee866876'}
EXPECTED_R1_SOURCE_HASHES = {
    "aiweb_language_core_bootstrap/component_loading/schema.py": "1de36e896228bd10df0175afbead8f5c1eb14e04e8c368659f36c3583a0bd33d",
    "scripts/test_aiweb_slice32_accepted_boundary_component_loading.py": "694e9b99ba4cbeaa33b3024b5d8ab49a597e983d0baafa2db6a83fa03b4ff92b",
}
EXPECTED_COMPONENT_IMPORTS = ('aiweb_meaning_law_trace_scaffold', 'aiweb_concept_boundary_scaffold', 'aiweb_predicate_role_boundary_scaffold', 'aiweb_verbal_cognition_gate_boundary_scaffold', 'aiweb_candidate_meaning_boundary_scaffold', 'aiweb_ambiguity_clarification_boundary_scaffold', 'aiweb_requirements_traceability_scaffold', 'aiweb_external_resource_quarantine_scaffold', 'aiweb_corpus_evidence_memory_trace_scaffold', 'aiweb_selected_meaning_boundary_scaffold', 'aiweb_output_expression_boundary_scaffold', 'aiweb_gp014_preservation_decision_scaffold', 'aiweb_rmc_echo_boundary_scaffold', 'aiweb_delivery_action_tool_routing_boundary_scaffold', 'aiweb_read_only_inspection_surface_scaffold')
SELF_CANONICAL_SHA256 = "c5d6ef44a10b9ddf86b82dde9db0f331687ba9e291d3610adf67db11e0e66879"
SELF_PLACEHOLDER = 'SELF_CANONICAL_SHA256 = "<SELF_SHA256>"'

PROHIBITED_IMPORT_ROOTS = {
    "importlib", "pkgutil", "requests", "httpx", "urllib", "socket",
    "aiohttp", "grpc", "ollama", "qwen", "chromadb", "chroma",
    "langchain", "faiss", "transformers", "torch", "tensorflow",
    "sklearn", "rmc_engine_v1", "main", "agents",
}
PROHIBITED_CALL_NAMES = {
    "open", "exec", "eval", "compile", "__import__", "getattr",
    "setattr", "delattr", "globals", "locals", "input",
}


def sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def canonical_self_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    current = f'SELF_CANONICAL_SHA256 = "{SELF_CANONICAL_SHA256}"'
    if current not in text:
        return ""
    canonical = text.replace(current, SELF_PLACEHOLDER, 1)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("--mode", choices=("precommit", "committed"), required=True)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    passes: list[str] = []
    failures: list[str] = []

    if (repo / ".git").exists():
        passes.append("target is a Git repository")
    else:
        failures.append("target is not a Git repository")

    for relative in R1_EXACT_PATHS:
        if (repo / relative).is_file():
            passes.append(f"required R1 path exists: {relative}")
        else:
            failures.append(f"required R1 path missing: {relative}")

    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    lines = tuple(line for line in status.stdout.splitlines() if line)
    if args.mode == "precommit":
        expected = {f" M {path}" for path in R1_EXACT_PATHS}
        if set(lines) == expected:
            passes.append("precommit status contains exactly three unstaged R1 modifications")
        else:
            failures.append("precommit status mismatch: " + " | ".join(lines))
    elif lines:
        failures.append("committed mode requires clean status: " + " | ".join(lines))
    else:
        passes.append("committed status is clean")

    for relative, expected in PROTECTED_HASHES.items():
        path = repo / relative
        if not path.is_file():
            failures.append(f"protected path missing: {relative}")
        elif sha256_file(path) != expected:
            failures.append(f"protected hash mismatch: {relative}")
        else:
            passes.append(f"protected hash preserved: {relative}")

    for relative, expected in EXPECTED_R1_SOURCE_HASHES.items():
        path = repo / relative
        if path.is_file() and sha256_file(path) == expected:
            passes.append(f"R1 source hash exact: {relative}")
        else:
            failures.append(f"R1 source hash mismatch: {relative}")

    self_path = repo / R1_EXACT_PATHS[2]
    if canonical_self_sha256(self_path) == SELF_CANONICAL_SHA256:
        passes.append("R1 verifier canonical self-hash exact")
    else:
        failures.append("R1 verifier canonical self-hash mismatch")

    for relative in R1_EXACT_PATHS:
        path = repo / relative
        try:
            parsed = ast.parse(path.read_text(encoding="utf-8"))
            compile(parsed, str(path), "exec")
            passes.append(f"Python syntax valid: {relative}")
        except Exception as exc:
            failures.append(f"Python syntax invalid: {relative}:{type(exc).__name__}")

    schema_source = (repo / R1_EXACT_PATHS[0]).read_text(encoding="utf-8")
    required_markers = (
        "_ACCEPTED_COMPONENT_IDENTITIES",
        "EXACT_SUCCESS_RESULT_ID",
        "accepted_success_identity_mismatch",
        "accepted_success_order_mismatch",
        "unaccepted_component_package",
        "accepted_disabled_identity_mismatch",
    )
    for marker in required_markers:
        if marker in schema_source:
            passes.append(f"strict identity marker present: {marker}")
        else:
            failures.append(f"strict identity marker missing: {marker}")

    static_path = repo / "aiweb_language_core_bootstrap/component_loading/static_interfaces.py"
    try:
        tree = ast.parse(static_path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"static interface syntax failure: {type(exc).__name__}")
        tree = ast.Module(body=[], type_ignores=[])

    direct_component_imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if alias.name in EXPECTED_COMPONENT_IMPORTS:
                    direct_component_imports.append(alias.name)
                if root in PROHIBITED_IMPORT_ROOTS:
                    failures.append(f"prohibited import root: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".", 1)[0]
            if node.level == 0 and root in PROHIBITED_IMPORT_ROOTS:
                failures.append(f"prohibited import root: {node.module}")
        elif isinstance(node, ast.Call):
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name in PROHIBITED_CALL_NAMES:
                failures.append(f"prohibited dynamic call: {name}")

    if tuple(direct_component_imports) == tuple(EXPECTED_COMPONENT_IMPORTS):
        passes.append("exact 15 direct component imports preserved in order")
    else:
        failures.append("static component import set/order mismatch")

    behavior = subprocess.run(
        [sys.executable, "-B", "scripts/test_aiweb_slice32_accepted_boundary_component_loading.py"],
        cwd=str(repo),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        env={
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPYCACHEPREFIX": "/tmp/aiweb_slice32_r1_behavior_cache",
        },
    )
    if behavior.returncode == 0 and "FICTITIOUS_RECOMPUTED_RESULT_REJECTED=True" in behavior.stdout:
        passes.append("independent R1 behavior and fictitious-record rejection passed")
    else:
        failures.append(
            "R1 behavior/adversarial proof failed: "
            + behavior.stdout[-800:]
            + behavior.stderr[-800:]
        )

    cache_entries = [
        path.relative_to(repo).as_posix()
        for path in repo.rglob("*")
        if path.is_file()
        and ("__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"})
        and ".venv" not in path.parts
    ]
    if cache_entries:
        failures.append("source-tree Python cache entries: " + " | ".join(cache_entries[:20]))
    else:
        passes.append("no source-tree Python cache entries")

    print("=" * 72)
    print("AIWEB SLICE 32 R1 STRICT LOADED-COMPONENT IDENTITY VERIFIER")
    print("=" * 72)
    print(f"Target repo: {repo}")
    print(f"Mode: {args.mode}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")
    print("VERDICT: " + ("PASS" if not failures else "FAIL"))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
