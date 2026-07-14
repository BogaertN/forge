#!/usr/bin/env python3
"""Independent repository verifier for Slice 33 trace/receipt assembly."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True

EXACT_PATHS = (
    "aiweb_language_core_bootstrap/trace_receipt/__init__.py",
    "aiweb_language_core_bootstrap/trace_receipt/schema.py",
    "aiweb_language_core_bootstrap/trace_receipt/flow_catalog.py",
    "aiweb_language_core_bootstrap/trace_receipt/assembler.py",
    "scripts/aiweb_slice33_deterministic_trace_receipt_assembly.py",
    "scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py",
    "scripts/aiweb_slice33_deterministic_trace_receipt_assembly_verify.py",
    "scripts/README_aiweb_slice33_deterministic_trace_receipt_assembly.md",
)

PROTECTED_HASHES = {
    "main.py": "73c382c3ffe496587e4d73df46dafd08345a3e7b0d64fc05b83ecdd4eddcc557",
    "requirements.txt": "ed73ba11243a0099034f10ac500db984959bb8f37086532f864d75a3620916c8",
    "setup.sh": "a90d3a77930f34f4fff5680739d1894e780b17115965ae9ccc595946ee866876",
    "rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py": "431e6c2133a06204131f81276c11b05528ed8e6553a0d5590555ffd23ef38473",
    "rmc_engine_v1/general_pipeline/symbolic_math_operator_language_realizer.py": "f1f2486504bb987d705efee70d775c1549d3597f5153d30e87cbf11f38bedf1a",
    "rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json": "e99c7691d0ba951343bdf80a82d65d19e464b660bedd942b9a9db2b16283c93e",
    "scripts/test_operator_guided_language_realizer_build_langexpr001_gp014.py": "d047b3ca07c13e4e29ab55f9aa8fb357ee87a1a7d649ea2b23f68f30b75af3be",
    "scripts/operator_guided_language_realizer_build_langexpr001_gp014_verify.py": "c84800156011727cd49f743b722502c60f555c109859ff79aa399cb32ae4d797",
    "aiweb_language_core_bootstrap/__init__.py": "0fbf450ac772eadcc2271f21a7d46d649730063764477b12276c6228ebfef9d6",
    "aiweb_language_core_bootstrap/authority.py": "03bbcdb03c8502c19ff7a5fc377875aa474d43cb0b4eb6d4471091ca42ca3838",
    "aiweb_language_core_bootstrap/boundary.py": "6b7fc05767b39c794deb84d5c09f30e1a0c5894841344ab72872500d9f6c4b90",
    "aiweb_language_core_bootstrap/component_registry.py": "d4d93800f510f97bacb0a9f0c531ea54f2804eb6c3dfcfa7f9c38a3301b7ac51",
    "aiweb_language_core_bootstrap/import_policy.py": "f0c87e5775864cf97cc54842bdd9cebbc700ed32d9977ec71474b3c6c4d63b66",
    "aiweb_language_core_bootstrap/schema.py": "4c33a6321d32497eed63679bcd144b67d0962972df712d4452e94d1f38f45500",
    "aiweb_language_core_bootstrap/verify.py": "5729b003f5610ce52afbd19fdf901c7a33ab8c6dde9fc8fea9dc6e4be646f5da",
    "scripts/README_aiweb_slice30_isolated_language_core_package_boundary.md": "32b2d088419e33cfa79c8e5bceed5019378b7639f7b85a531fc1258b3665b468",
    "scripts/aiweb_slice30_isolated_language_core_package_boundary_verify.py": "404d90901d2a5875f56f57bb012c23ead1ddde534cd95bd2fdbecd9b9a939e9b",
    "scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py": "25697b064168175bc6e9a43aabfbfd50196198b4e617ff19e668eb4923502679",
    "aiweb_language_core_bootstrap/bootstrap_adapter/__init__.py": "c02d5ed2f125b86745ace30d5218e548569821653d6d5ac53b65b6cee19b530a",
    "aiweb_language_core_bootstrap/bootstrap_adapter/schema.py": "7d5999cdc9c96de5ab1bc367e5972fe16cc559a3fdd30a3742749661bee4eaa7",
    "aiweb_language_core_bootstrap/bootstrap_adapter/fixtures.py": "66013a1f044c431c12ae24121be4d026d77f1923f75008100ac158ff01f81a13",
    "aiweb_language_core_bootstrap/bootstrap_adapter/adapter.py": "03282793f0c470c0769fcb784aedaa1885a9e7472d7b0bb49f8f02c0725f7cb3",
    "scripts/aiweb_slice31_disabled_bootstrap_adapter.py": "3a6068b7b8021142994c0ba4820e83b0fa74494c7a453afbb27d89637f56f1aa",
    "scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py": "e0971900ced6f11b168d5ac82d383eb60ce7da6a16fdd82b41866223ac3cb099",
    "scripts/aiweb_slice31_disabled_bootstrap_adapter_verify.py": "6f2e291202741964d14684899f7913d5c5836d9d4047b23113599ae778a2ff76",
    "scripts/README_aiweb_slice31_disabled_bootstrap_adapter.md": "859ca9aa5ff706a2ff5771815c0c113f6749907971c4754a3252ff8a267ccca6",
    "aiweb_language_core_bootstrap/component_loading/__init__.py": "51522fe211fb7d54b1878f53e748cd5ecbcf9f5c5eac86f9583357e85130035e",
    "aiweb_language_core_bootstrap/component_loading/schema.py": "1de36e896228bd10df0175afbead8f5c1eb14e04e8c368659f36c3583a0bd33d",
    "aiweb_language_core_bootstrap/component_loading/fixtures.py": "90debe14d8cd8a4dcf696f9d50b96649172bcc4f8bce3f796bb98a5c15d4d6dc",
    "aiweb_language_core_bootstrap/component_loading/static_interfaces.py": "cbe95f966f5cb04fda0fafcbae5f93306ac8b0da0b78de2041e92ebbdc54ef01",
    "aiweb_language_core_bootstrap/component_loading/loader.py": "2c3d71e1f4ef0198d6bb1daff617c592dbacab4da713eb7ed4fa00b7fa0d5087",
    "scripts/aiweb_slice32_accepted_boundary_component_loading.py": "8b46394d0a573b21be08838867b08eb40ce7ea2b812eec1a2ee1027ef6df510f",
    "scripts/test_aiweb_slice32_accepted_boundary_component_loading.py": "694e9b99ba4cbeaa33b3024b5d8ab49a597e983d0baafa2db6a83fa03b4ff92b",
    "scripts/aiweb_slice32_accepted_boundary_component_loading_verify.py": "4d7c5760bb4dded4ae080a7dd728253f580f61e9348ee26610620131fc827d67",
    "scripts/README_aiweb_slice32_accepted_boundary_component_loading.md": "4f7fa9b9502b274a88481de4f954b4a7159c9edfa70da1f24a1079c43b1e8bd4",
}

EXPECTED_SOURCE_HASHES = {
    "aiweb_language_core_bootstrap/trace_receipt/__init__.py": "41599980091954e391350a3e5c26b0b3f297b2b747ef143b58a6064222a9ada3",
    "aiweb_language_core_bootstrap/trace_receipt/schema.py": "fd013a52c50e71c6829c08499436f3777de9463e33473b6cc1cf7f84ed8f1121",
    "aiweb_language_core_bootstrap/trace_receipt/flow_catalog.py": "1884dfde6c073dc8ab6c94a5797ef0bdff4260314a7896c8c96eaa616da5fad3",
    "aiweb_language_core_bootstrap/trace_receipt/assembler.py": "0e7c78014daecc4981048953604a1df017c986b1187808a7db9db08855c83d39",
    "scripts/aiweb_slice33_deterministic_trace_receipt_assembly.py": "dd40d485737991966d71493fe130c2333e90371dbcb300db0a8e0f529f584ed0",
    "scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py": "0d142b886196f83b1487ad741b7dcf46ab39290ed42eee5fa2c422a629aec6c8",
    "scripts/README_aiweb_slice33_deterministic_trace_receipt_assembly.md": "c2f0e097e12f6ab1d20d9ca64012389445c3009e1e9662d0176e047ce82cc8c1",
}

SELF_CANONICAL_SHA256 = "f2318661958d8be529342407cdc58e99e06abe06adc09a4fe3683c7d4e72d591"
SELF_PLACEHOLDER = 'SELF_CANONICAL_SHA256 = "<SELF_SHA256>"'

EXPECTED_FLOW_NAMES = (
    "slice31-disabled-default-probe-trace-v1",
    "slice31-explicit-inspection-disabled-trace-v1",
    "slice31-explicit-inspection-enabled-trace-v1",
    "slice32-static-loading-disabled-trace-v1",
    "slice32-static-loading-enabled-trace-v1",
)

ACCEPTED_PACKAGE_NAMES = (
    "aiweb_meaning_law_trace_scaffold",
    "aiweb_concept_boundary_scaffold",
    "aiweb_predicate_role_boundary_scaffold",
    "aiweb_verbal_cognition_gate_boundary_scaffold",
    "aiweb_candidate_meaning_boundary_scaffold",
    "aiweb_ambiguity_clarification_boundary_scaffold",
    "aiweb_requirements_traceability_scaffold",
    "aiweb_external_resource_quarantine_scaffold",
    "aiweb_corpus_evidence_memory_trace_scaffold",
    "aiweb_selected_meaning_boundary_scaffold",
    "aiweb_output_expression_boundary_scaffold",
    "aiweb_gp014_preservation_decision_scaffold",
    "aiweb_rmc_echo_boundary_scaffold",
    "aiweb_delivery_action_tool_routing_boundary_scaffold",
    "aiweb_read_only_inspection_surface_scaffold",
)

PROHIBITED_RUNTIME_IMPORT_ROOTS = {
    "os", "pathlib", "subprocess", "socket", "urllib", "requests", "httpx",
    "aiohttp", "grpc", "importlib", "pkgutil", "ollama", "qwen", "chromadb",
    "chroma", "langchain", "faiss", "transformers", "torch", "tensorflow",
    "sklearn", "rmc_engine_v1", "main", "agents",
}
PROHIBITED_RUNTIME_CALLS = {
    "open", "exec", "eval", "compile", "__import__", "input",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def run_python(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", *args],
        cwd=str(repo),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        env={
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPYCACHEPREFIX": "/tmp/aiweb_slice33_verifier_cache",
        },
    )


def _call_name(node: ast.Call) -> str:
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

    if (repo / ".git").exists():
        passes.append("target is a Git repository")
    else:
        failures.append("target is not a Git repository")

    for relative in EXACT_PATHS:
        if (repo / relative).is_file():
            passes.append(f"required Slice 33 path exists: {relative}")
        else:
            failures.append(f"required Slice 33 path missing: {relative}")

    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0:
        failures.append("git status failed: " + status.stderr.strip())
    else:
        lines = tuple(line for line in status.stdout.splitlines() if line)
        if args.mode == "precommit":
            expected = {f"?? {path}" for path in EXACT_PATHS}
            if set(lines) == expected:
                passes.append("precommit status contains exactly eight new paths")
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

    for relative, expected in EXPECTED_SOURCE_HASHES.items():
        path = repo / relative
        if path.is_file() and sha256_file(path) == expected:
            passes.append(f"Slice 33 source hash exact: {relative}")
        else:
            failures.append(f"Slice 33 source hash mismatch: {relative}")

    self_path = repo / "scripts/aiweb_slice33_deterministic_trace_receipt_assembly_verify.py"
    if canonical_self_sha256(self_path) == SELF_CANONICAL_SHA256:
        passes.append("Slice 33 verifier canonical self-hash exact")
    else:
        failures.append("Slice 33 verifier canonical self-hash mismatch")

    for relative in EXACT_PATHS:
        path = repo / relative
        if path.suffix != ".py" or not path.is_file():
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            compile(tree, str(path), "exec")
            passes.append(f"Python syntax valid: {relative}")
        except Exception as exc:
            failures.append(f"Python syntax invalid: {relative}:{type(exc).__name__}")

    runtime_paths = EXACT_PATHS[:4]
    for relative in runtime_paths:
        path = repo / relative
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if root in PROHIBITED_RUNTIME_IMPORT_ROOTS:
                        failures.append(f"prohibited runtime import: {relative}:{alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                root = (node.module or "").split(".", 1)[0]
                if root in PROHIBITED_RUNTIME_IMPORT_ROOTS:
                    failures.append(f"prohibited runtime import: {relative}:{node.module}")
            elif isinstance(node, ast.Call):
                name = _call_name(node)
                if name in PROHIBITED_RUNTIME_CALLS:
                    failures.append(f"prohibited runtime call: {relative}:{name}")

    parent_init = (repo / "aiweb_language_core_bootstrap/__init__.py").read_text(encoding="utf-8")
    if "trace_receipt" not in parent_init:
        passes.append("parent package does not automatically import Slice 33")
    else:
        failures.append("parent package automatically imports Slice 33")

    flow_source = (repo / "aiweb_language_core_bootstrap/trace_receipt/flow_catalog.py").read_text(encoding="utf-8")
    required_markers = (
        "SLICE32_R1_ACCEPTED_HEAD",
        "ACCEPTED_LOADED_COMPONENT_IDS",
        "EXACT_ENABLED_ASSEMBLY_STATE_ID",
        "SOURCE_VERSION_REFS",
        "build_expected_trace",
        "build_expected_receipt",
    )
    for marker in required_markers:
        if marker in flow_source:
            passes.append(f"strict trace marker present: {marker}")
        else:
            failures.append(f"strict trace marker missing: {marker}")

    import_probe = run_python(
        repo,
        "-c",
        (
            "import sys,json; "
            "names=" + repr(ACCEPTED_PACKAGE_NAMES) + "; "
            "import aiweb_language_core_bootstrap.trace_receipt; "
            "print(json.dumps([n for n in names if n in sys.modules]))"
        ),
    )
    if import_probe.returncode == 0 and json.loads(import_probe.stdout) == []:
        passes.append("Slice 33 package import loads zero accepted components")
    else:
        failures.append("Slice 33 import containment failed: " + import_probe.stdout[-500:] + import_probe.stderr[-500:])

    behavior = run_python(
        repo,
        "scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py",
    )
    if (
        behavior.returncode == 0
        and "TEST_COUNT=227" in behavior.stdout
        and "FABRICATED_RECOMPUTED_TRACE_RECEIPT_CHAIN_REJECTED=True" in behavior.stdout
    ):
        passes.append("227-check behavior and adversarial proof passed")
    else:
        failures.append("Slice 33 behavior proof failed: " + behavior.stdout[-1200:] + behavior.stderr[-1200:])

    list_result = run_python(
        repo,
        "scripts/aiweb_slice33_deterministic_trace_receipt_assembly.py",
        "--list-flows",
    )
    try:
        listed = json.loads(list_result.stdout)
    except Exception:
        listed = None
    if (
        list_result.returncode == 0
        and isinstance(listed, list)
        and tuple(item.get("flow_name") for item in listed) == EXPECTED_FLOW_NAMES
    ):
        passes.append("CLI lists exact five trace flows in order")
    else:
        failures.append("CLI flow catalog mismatch: " + list_result.stdout[-800:] + list_result.stderr[-800:])

    disabled = run_python(
        repo,
        "scripts/aiweb_slice33_deterministic_trace_receipt_assembly.py",
        "--flow",
        EXPECTED_FLOW_NAMES[0],
    )
    try:
        disabled_value = json.loads(disabled.stdout)
    except Exception:
        disabled_value = {}
    if (
        disabled.returncode == 2
        and disabled_value.get("status") == "refused_trace_receipt_assembly_disabled"
        and disabled_value.get("trace") is None
        and disabled_value.get("receipt") is None
    ):
        passes.append("CLI disabled-default refusal exact")
    else:
        failures.append("CLI disabled-default proof failed: " + disabled.stdout[-800:] + disabled.stderr[-800:])

    for flow_name in EXPECTED_FLOW_NAMES:
        completed = run_python(
            repo,
            "scripts/aiweb_slice33_deterministic_trace_receipt_assembly.py",
            "--flow",
            flow_name,
            "--enable-offline-trace-receipt",
        )
        try:
            value = json.loads(completed.stdout)
        except Exception:
            value = {}
        if (
            completed.returncode == 0
            and value.get("status") == "completed_trace_receipt_assembly"
            and isinstance(value.get("trace"), dict)
            and isinstance(value.get("receipt"), dict)
            and value["trace"].get("flow_name") == flow_name
            and value["receipt"].get("flow_name") == flow_name
        ):
            passes.append(f"CLI completed exact flow: {flow_name}")
        else:
            failures.append(f"CLI flow failed: {flow_name}:" + completed.stdout[-800:] + completed.stderr[-800:])

    cache_paths = []
    for root in (
        repo / "aiweb_language_core_bootstrap",
        repo / "scripts",
    ):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.name == "__pycache__" or path.suffix in (".pyc", ".pyo"):
                cache_paths.append(str(path.relative_to(repo)))
    if cache_paths:
        failures.append("source-tree Python cache entries: " + " | ".join(cache_paths[:20]))
    else:
        passes.append("no source-tree Python cache entries")

    print("=" * 72)
    print("AIWEB SLICE 33 DETERMINISTIC TRACE AND RECEIPT ASSEMBLY VERIFIER")
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
