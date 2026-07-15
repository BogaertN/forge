#!/usr/bin/env python3
"""Repository verifier for Slice 34 bootstrap regression containment acceptance."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True

EXPECTED_PARENT_HEAD = "ad0129543ff23b16f6de9008b091a8f97892486d"
EXPECTED_COMMIT_SUBJECT = "Slice 34 bootstrap regression and containment acceptance"
EXACT_PATHS = ('aiweb_language_core_bootstrap/regression_containment/__init__.py',
 'aiweb_language_core_bootstrap/regression_containment/policy.py',
 'aiweb_language_core_bootstrap/regression_containment/schema.py',
 'aiweb_language_core_bootstrap/regression_containment/evaluator.py',
 'scripts/aiweb_slice34_bootstrap_regression_containment_acceptance.py',
 'scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py',
 'scripts/aiweb_slice34_bootstrap_regression_containment_acceptance_verify.py',
 'scripts/README_aiweb_slice34_bootstrap_regression_containment_acceptance.md')
PROTECTED_HASHES = {'aiweb_full_regression_acceptance_bundle_scaffold/__init__.py': '43a7c6ee549905eae808972dcd5294f992e4b48fe34ea7931529e7601b5e0006',
 'aiweb_full_regression_acceptance_bundle_scaffold/authority.py': '81c479fe1a6ba261aa1d2b7febd856261efe8adbb8a0e6af97ae616b4c855ccf',
 'aiweb_full_regression_acceptance_bundle_scaffold/catalog.py': 'a4a090aa8b7b82529e197d614a129a32c4642b25b225f540ceb5d4c922b72bb7',
 'aiweb_full_regression_acceptance_bundle_scaffold/classification.py': '52e00d5c55fb26c6c9c5340686e593777d42576d9640a7b86a7bbf78a623e870',
 'aiweb_full_regression_acceptance_bundle_scaffold/context.py': 'f636034114a530cc75e141b0176c364731d2e2f9a535eaaa8d51012ed44072ac',
 'aiweb_full_regression_acceptance_bundle_scaffold/receipt.py': '32f1987e51db67fe2cfa023cb2c159bc65c2c4ab281c0e065e0eb6b9c1cd0ee0',
 'aiweb_full_regression_acceptance_bundle_scaffold/runner.py': '8bef2d8db75b0b46f932262cca26dd0238144bd17925ea03ff81eaf43a0d72ea',
 'aiweb_full_regression_acceptance_bundle_scaffold/scope.py': 'b0845b9bccc5d0641a07a2f5718145b2b0519b5d22bbc3eb5ce67aa89afb2154',
 'aiweb_full_regression_acceptance_bundle_scaffold/source_guard.py': '76662e96d4e11835c7ff2a9b481c5a8a8f8a0b2dcd086940cc91263f92bd6c2f',
 'aiweb_full_regression_acceptance_bundle_scaffold/verify.py': '17d4cc1ca9b131f152f28559e64c2d845d6f3cae08af1cf587c72138908b37ef',
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
 'aiweb_language_core_bootstrap/schema.py': '4c33a6321d32497eed63679bcd144b67d0962972df712d4452e94d1f38f45500',
 'aiweb_language_core_bootstrap/trace_receipt/__init__.py': '41599980091954e391350a3e5c26b0b3f297b2b747ef143b58a6064222a9ada3',
 'aiweb_language_core_bootstrap/trace_receipt/assembler.py': '0e7c78014daecc4981048953604a1df017c986b1187808a7db9db08855c83d39',
 'aiweb_language_core_bootstrap/trace_receipt/flow_catalog.py': '1884dfde6c073dc8ab6c94a5797ef0bdff4260314a7896c8c96eaa616da5fad3',
 'aiweb_language_core_bootstrap/trace_receipt/schema.py': 'fd013a52c50e71c6829c08499436f3777de9463e33473b6cc1cf7f84ed8f1121',
 'aiweb_language_core_bootstrap/verify.py': '5729b003f5610ce52afbd19fdf901c7a33ab8c6dde9fc8fea9dc6e4be646f5da',
 'main.py': '73c382c3ffe496587e4d73df46dafd08345a3e7b0d64fc05b83ecdd4eddcc557',
 'requirements.txt': 'ed73ba11243a0099034f10ac500db984959bb8f37086532f864d75a3620916c8',
 'rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py': '431e6c2133a06204131f81276c11b05528ed8e6553a0d5590555ffd23ef38473',
 'rmc_engine_v1/general_pipeline/symbolic_math_operator_language_realizer.py': 'f1f2486504bb987d705efee70d775c1549d3597f5153d30e87cbf11f38bedf1a',
 'rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json': 'e99c7691d0ba951343bdf80a82d65d19e464b660bedd942b9a9db2b16283c93e',
 'scripts/README_aiweb_slice24_full_regression_acceptance_bundle_scaffold.md': 'd2aea369c49a16f6d2f4cf048108ea16703a71df462f4af751dbd6be6e6efd77',
 'scripts/README_aiweb_slice30_isolated_language_core_package_boundary.md': '32b2d088419e33cfa79c8e5bceed5019378b7639f7b85a531fc1258b3665b468',
 'scripts/README_aiweb_slice31_disabled_bootstrap_adapter.md': '859ca9aa5ff706a2ff5771815c0c113f6749907971c4754a3252ff8a267ccca6',
 'scripts/README_aiweb_slice32_accepted_boundary_component_loading.md': '4f7fa9b9502b274a88481de4f954b4a7159c9edfa70da1f24a1079c43b1e8bd4',
 'scripts/README_aiweb_slice33_deterministic_trace_receipt_assembly.md': 'c2f0e097e12f6ab1d20d9ca64012389445c3009e1e9662d0176e047ce82cc8c1',
 'scripts/aiweb_slice24_full_regression_acceptance_bundle_verify.py': 'ef73877f749ee2b37950e3f4cd49b75c9d9033c915e193759eac547eacafc21e',
 'scripts/aiweb_slice30_isolated_language_core_package_boundary_verify.py': '404d90901d2a5875f56f57bb012c23ead1ddde534cd95bd2fdbecd9b9a939e9b',
 'scripts/aiweb_slice31_disabled_bootstrap_adapter.py': '3a6068b7b8021142994c0ba4820e83b0fa74494c7a453afbb27d89637f56f1aa',
 'scripts/aiweb_slice31_disabled_bootstrap_adapter_verify.py': '6f2e291202741964d14684899f7913d5c5836d9d4047b23113599ae778a2ff76',
 'scripts/aiweb_slice32_accepted_boundary_component_loading.py': '8b46394d0a573b21be08838867b08eb40ce7ea2b812eec1a2ee1027ef6df510f',
 'scripts/aiweb_slice32_accepted_boundary_component_loading_verify.py': '4d7c5760bb4dded4ae080a7dd728253f580f61e9348ee26610620131fc827d67',
 'scripts/aiweb_slice33_deterministic_trace_receipt_assembly.py': 'dd40d485737991966d71493fe130c2333e90371dbcb300db0a8e0f529f584ed0',
 'scripts/aiweb_slice33_deterministic_trace_receipt_assembly_verify.py': 'c4954002a61c6b0e204ebe3ace98602298476615d469f07cfe6264b4c32bf7d8',
 'scripts/operator_guided_language_realizer_build_langexpr001_gp014_verify.py': 'c84800156011727cd49f743b722502c60f555c109859ff79aa399cb32ae4d797',
 'scripts/test_aiweb_slice24_full_regression_acceptance_bundle_scaffold.py': '814218b49639ee1f58c4821e5001804cd8f2be83f1b95a505ffbf1beec915dfb',
 'scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py': '25697b064168175bc6e9a43aabfbfd50196198b4e617ff19e668eb4923502679',
 'scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py': 'e0971900ced6f11b168d5ac82d383eb60ce7da6a16fdd82b41866223ac3cb099',
 'scripts/test_aiweb_slice32_accepted_boundary_component_loading.py': '694e9b99ba4cbeaa33b3024b5d8ab49a597e983d0baafa2db6a83fa03b4ff92b',
 'scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py': '0d142b886196f83b1487ad741b7dcf46ab39290ed42eee5fa2c422a629aec6c8',
 'scripts/test_operator_guided_language_realizer_build_langexpr001_gp014.py': 'd047b3ca07c13e4e29ab55f9aa8fb357ee87a1a7d649ea2b23f68f30b75af3be',
 'setup.sh': 'a90d3a77930f34f4fff5680739d1894e780b17115965ae9ccc595946ee866876'}
EXPECTED_SOURCE_HASHES = {'aiweb_language_core_bootstrap/regression_containment/__init__.py': '9dd57a6a2f5c76625b45cde657db7e4da0309b00f7d0dbd88aa55c202c813c42',
 'aiweb_language_core_bootstrap/regression_containment/evaluator.py': '949f8735d638c6626e542b3e38fcabce70ca046689b44259ddf1bc29deb6bb9d',
 'aiweb_language_core_bootstrap/regression_containment/policy.py': 'e0f88f0ab07fa17ab46cae731ba121298b44d337fd2ea1a0faa6cf9a2c9ad2c6',
 'aiweb_language_core_bootstrap/regression_containment/schema.py': '42836cfc497fdabb4f5f530c3bab8a492b47497745f0f1d315f6d0cd2fdd34e6',
 'scripts/README_aiweb_slice34_bootstrap_regression_containment_acceptance.md': '473ac34fa6c161bfaf7969fa329baa284900afa481ebdd7cf0f10c8c63d3ea44',
 'scripts/aiweb_slice34_bootstrap_regression_containment_acceptance.py': '515206cdbc3ffb375640a32a5bc7bdf7fd05f02854f2614634a1688ea45d636c',
 'scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py': '1c6016238ba7349d329f97c34d2055061ba45d07d935739bfa0f5353bcf4ab85'}
SELF_CANONICAL_SHA256 = "6c5198d0ea6b8574245750cd8ce77d91c7d50931d8336dbbe42a3258584142fa"
SELF_PLACEHOLDER = 'SELF_CANONICAL_SHA256 = "<SELF_SHA256>"'
RUNTIME_PATHS = EXACT_PATHS[:4]
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
PROHIBITED_RUNTIME_CALLS = {"open", "exec", "eval", "compile", "__import__", "input"}
REQUIRED_POLICY_MARKERS = (
    "REQUIRED_INHERITED_REGRESSION_COMMAND_COUNT: Final[int] = 45",
    "REQUIRED_PHASE_B_PRESERVATION_COMMAND_COUNT: Final[int] = 8",
    "REQUIRED_PRIOR_COMMAND_COUNT: Final[int] = 53",
    "ONE_COMMAND_ROLLBACK_REQUIRED: Final[bool] = True",
    "SLICE34_PARENT_HEAD: Final[str]",
    "FLOW_IDENTITY_EXPECTATIONS",
    "PROHIBITED_AUTHORITY_CATEGORIES",
)


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
        env={"GIT_OPTIONAL_LOCKS": "0", "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"},
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
            "PYTHONPYCACHEPREFIX": "/tmp/aiweb_slice34_verifier_cache",
            "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
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

    inside = git(repo, "rev-parse", "--is-inside-work-tree")
    if inside.returncode == 0 and inside.stdout.strip() == "true":
        passes.append("target is a Git repository")
    else:
        failures.append("target is not a Git repository")

    for relative in EXACT_PATHS:
        if (repo / relative).is_file():
            passes.append(f"required Slice 34 path exists: {relative}")
        else:
            failures.append(f"required Slice 34 path missing: {relative}")

    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0:
        failures.append("git status failed: " + status.stderr.strip())
    else:
        lines = tuple(line for line in status.stdout.splitlines() if line)
        if args.mode == "precommit":
            expected = {f"?? {path}" for path in EXACT_PATHS}
            if set(lines) == expected and len(lines) == len(EXACT_PATHS):
                passes.append("precommit status contains exactly eight new paths")
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
            passes.append("committed parent is exact accepted Slice 33 HEAD")
        else:
            failures.append("committed parent mismatch: " + parent.stdout.strip())
        if subject.returncode == 0 and subject.stdout.strip() == EXPECTED_COMMIT_SUBJECT:
            passes.append("committed subject exact")
        else:
            failures.append("committed subject mismatch: " + subject.stdout.strip())
        changed_paths = tuple(line for line in changed.stdout.splitlines() if line)
        if set(changed_paths) == set(EXACT_PATHS) and len(changed_paths) == len(EXACT_PATHS):
            passes.append("commit contains exactly eight Slice 34 paths")
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

    for relative, expected in EXPECTED_SOURCE_HASHES.items():
        path = repo / relative
        if path.is_file() and sha256_file(path) == expected:
            passes.append(f"Slice 34 source hash exact: {relative}")
        else:
            failures.append(f"Slice 34 source hash mismatch: {relative}")

    self_path = repo / "scripts/aiweb_slice34_bootstrap_regression_containment_acceptance_verify.py"
    if self_path.is_file() and canonical_self_sha256(self_path) == SELF_CANONICAL_SHA256:
        passes.append("Slice 34 verifier canonical self-hash exact")
    else:
        failures.append("Slice 34 verifier canonical self-hash mismatch")

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

    for relative in RUNTIME_PATHS:
        path = repo / relative
        if not path.is_file():
            continue
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
    if "regression_containment" not in parent_init:
        passes.append("parent package does not automatically import Slice 34")
    else:
        failures.append("parent package automatically imports Slice 34")

    policy_text = (repo / "aiweb_language_core_bootstrap/regression_containment/policy.py").read_text(encoding="utf-8")
    for marker in REQUIRED_POLICY_MARKERS:
        if marker in policy_text:
            passes.append(f"strict policy marker present: {marker}")
        else:
            failures.append(f"strict policy marker missing: {marker}")

    behavior = run_python(repo, "scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py")
    if (
        behavior.returncode == 0
        and "SLICE34_BOOTSTRAP_REGRESSION_CONTAINMENT_ACCEPTANCE_TEST=PASS" in behavior.stdout
        and "FABRICATED_RECOMPUTED_CONTAINMENT_CHAIN_REJECTED=True" in behavior.stdout
        and "RUNTIME_NETWORK_WRITE_ACTION_ATTEMPTS=0" in behavior.stdout
    ):
        passes.append("254-check containment and adversarial behavior proof passed")
    else:
        failures.append(
            "Slice 34 behavior proof failed: rc=" + str(behavior.returncode)
            + ":stdout=" + behavior.stdout.strip()
            + ":stderr=" + behavior.stderr.strip()
        )

    requirements = run_python(
        repo,
        "scripts/aiweb_slice34_bootstrap_regression_containment_acceptance.py",
        "--list-requirements",
    )
    try:
        req_payload = json.loads(requirements.stdout)
    except Exception:
        req_payload = {}
    if (
        requirements.returncode == 0
        and len(req_payload.get("flow_names", [])) == 5
        and len(req_payload.get("containment_guard_ids", [])) == 20
        and req_payload.get("inherited_regression_command_count") == 45
        and req_payload.get("phase_b_preservation_command_count") == 8
        and req_payload.get("total_prior_command_count") == 53
        and req_payload.get("one_command_rollback_required") is True
        and req_payload.get("technical_acceptance_granted_by_runtime") is False
    ):
        passes.append("CLI requirement catalog exact")
    else:
        failures.append("CLI requirement catalog mismatch")

    disabled = run_python(repo, "scripts/aiweb_slice34_bootstrap_regression_containment_acceptance.py")
    try:
        disabled_payload = json.loads(disabled.stdout)
    except Exception:
        disabled_payload = {}
    if (
        disabled.returncode == 2
        and disabled_payload.get("status") == "refused_bootstrap_containment_evaluation_disabled"
        and disabled_payload.get("flow_proofs") == []
        and disabled_payload.get("technical_acceptance_granted") is False
    ):
        passes.append("CLI disabled-default refusal exact")
    else:
        failures.append("CLI disabled-default refusal mismatch")

    enabled = run_python(
        repo,
        "scripts/aiweb_slice34_bootstrap_regression_containment_acceptance.py",
        "--enable-offline-containment-evaluation",
    )
    try:
        enabled_payload = json.loads(enabled.stdout)
    except Exception:
        enabled_payload = {}
    if (
        enabled.returncode == 0
        and enabled_payload.get("status") == "completed_bootstrap_containment_evaluation"
        and enabled_payload.get("runtime_containment_passed") is True
        and enabled_payload.get("validated_flow_count") == 5
        and enabled_payload.get("total_prior_command_count") == 53
        and enabled_payload.get("technical_acceptance_granted") is False
        and enabled_payload.get("network_access_performed") is False
        and enabled_payload.get("runtime_memory_write_performed") is False
        and enabled_payload.get("action_performed") is False
    ):
        passes.append("CLI explicit offline containment evaluation exact")
    else:
        failures.append("CLI explicit offline containment evaluation mismatch")

    cache_entries = []
    managed = {".venv", "venv"}
    for path in repo.rglob("*"):
        try:
            rel = path.relative_to(repo)
        except ValueError:
            continue
        if any(part in managed for part in rel.parts):
            continue
        if path.is_dir() and path.name == "__pycache__":
            cache_entries.append(rel.as_posix() + "/")
        elif path.is_file() and path.suffix in {".pyc", ".pyo"}:
            cache_entries.append(rel.as_posix())
    if cache_entries:
        failures.append("source-tree Python cache entries: " + " | ".join(sorted(cache_entries)))
    else:
        passes.append("no source-tree Python cache entries")

    print("=" * 72)
    print("AIWEB SLICE 34 BOOTSTRAP REGRESSION AND CONTAINMENT ACCEPTANCE VERIFIER")
    print("=" * 72)
    print(f"Target repo: {repo}")
    print(f"Mode: {args.mode}")
    print("PASSES:")
    for item in passes:
        print("  PASS - " + item)
    print("FAILURES:")
    for item in failures:
        print("  FAIL - " + item)
    print("VERDICT: " + ("PASS" if not failures else "FAIL"))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
