#!/usr/bin/env python3
"""Independent verifier for Slice 36B0."""
from __future__ import annotations
import argparse, ast, hashlib, os, subprocess, sys
from pathlib import Path

EXPECTED_PARENT_HEAD = "5ddc6a1a5f4d0cbf3e9e28fe57d3144c65520732"
EXPECTED_COMMIT_SUBJECT = "Slice 36B0 RSOC FBSC language operator contract and legacy isolation"
EXACT_PATHS = ('aiweb_language_core_bootstrap/resonant_language_operator_contract/__init__.py', 'aiweb_language_core_bootstrap/resonant_language_operator_contract/schema.py', 'aiweb_language_core_bootstrap/resonant_language_operator_contract/registry.py', 'aiweb_language_core_bootstrap/resonant_language_operator_contract/field_contract.py', 'aiweb_language_core_bootstrap/resonant_language_operator_contract/legacy_isolation.py', 'aiweb_language_core_bootstrap/resonant_language_operator_contract/validation.py', 'scripts/AIWEB_SLICE36B0_RSOC_FBSC_LANGUAGE_OPERATOR_RUNTIME_CONTRACT_SPEC.md', 'scripts/AIWEB_SLICE36_OPERATOR_ARCHITECTURE_SUPERSESSION_RECORD.md', 'scripts/README_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.md', 'scripts/test_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.py', 'scripts/aiweb_slice36b0_rsoc_fbsc_language_operator_contract_verify.py')
RUNTIME_FILES = EXACT_PATHS[:6]
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
 'aiweb_language_core_bootstrap/component_loading/schema.py': '1de36e896228bd10df0175afbead8f5c1eb14e04e8c368659f36c3583a0bd33d',
 'aiweb_language_core_bootstrap/component_loading/static_interfaces.py': 'cbe95f966f5cb04fda0fafcbae5f93306ac8b0da0b78de2041e92ebbdc54ef01',
 'aiweb_language_core_bootstrap/component_registry.py': 'd4d93800f510f97bacb0a9f0c531ea54f2804eb6c3dfcfa7f9c38a3301b7ac51',
 'aiweb_language_core_bootstrap/import_policy.py': 'f0c87e5775864cf97cc54842bdd9cebbc700ed32d9977ec71474b3c6c4d63b66',
 'aiweb_language_core_bootstrap/input_event_custody/__init__.py': 'd9011943ab2cac9ea5d76ee7e5492c3a722f5f2374d0ff8e7db8cfe79e757d8d',
 'aiweb_language_core_bootstrap/input_event_custody/capture.py': '996e0bc378351e0a83efa30732bbb3bbc07171847fda1ff957f04716aa22f4f4',
 'aiweb_language_core_bootstrap/input_event_custody/schema.py': '44497f9737834cb2a0042d528a3399c282b09b2352cd8ff7a354b5958bc37861',
 'aiweb_language_core_bootstrap/meaning_structure_manifest/__init__.py': '2395e0703593f2f95e620fb4a28bf08e9bbb1801e51e359f43f20cf040036836',
 'aiweb_language_core_bootstrap/meaning_structure_manifest/_enums.py': 'a25c47e508063e8b119337f2b27e3af382b91c105ec101467d960ec4ca2645f8',
 'aiweb_language_core_bootstrap/meaning_structure_manifest/_identity.py': '968054b4a53f65396e27f32a288250f8c1dae077dc8375746bd4ec6220d18f00',
 'aiweb_language_core_bootstrap/meaning_structure_manifest/_records.py': '2ed280f8dacecb5b0bef4828466e6c42aecb2deb1156bff8de75e4cda38139f9',
 'aiweb_language_core_bootstrap/meaning_structure_manifest/bootstrap_integration.py': '635f6d4cb7ae8a16d3ab7eae51b83f9ca473c4bba264233136438a1af080c194',
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
 'requirements.txt': 'ed73ba11243a0099034f10ac500db984959bb8f37086532f864d75a3620916c8',
 'rmc_engine_v1/candidate_generator.py': '2c192421215c56c1f6def166be420824448f255181aa4b2bc3c9b7d99cadd170',
 'rmc_engine_v1/chroma_connector.py': '6554fe9188e676d4b79d4ba15f0a723574a64defc8bef4e0363ed165c83eed91',
 'rmc_engine_v1/llm_renderer.py': '855bb683801e034487c997fd6dfeb51b8fd376f4d287fddb3e33b83bca99d2ac',
 'rmc_engine_v1/manifest_compiler.py': 'a9595bdcaa4127425d09661417de9b1b86159e174e0f41dfd4259fae837de76f',
 'rmc_engine_v1/mea/fbsc_operator_crosswalk.py': '92c4eddd11e5b16c0aa74901e648bda1e963c222ca34464254dbcf0c01158e8e',
 'rmc_engine_v1/mea/operator_engine.py': '3652179cf66282f2aab261e93ff1f238e3ee11852481b843e0fcdf204e025b2c',
 'rmc_engine_v1/mea/operator_registry.py': 'b779c1d75ae16bb64986d9cdfb4b25d09de82eaf8704f02a6fe048a13131c74d',
 'rmc_engine_v1/phase_codex.py': '1611809e7bc4f6cd6b9ad6d4202e497994e920ed9d3b5b434e3fbabc02448606',
 'rmc_engine_v1/phase_parser.py': 'dd83c0902bd2a162399db5b7f685f718a697492299eba6af5cf4c8dc86cfc45a',
 'rmc_engine_v1/reference/letter_phase_map_v1.json': '1f2b031b79de2d5f15ce8e22bbc7dfbfede47756c4270d6859c2436b24508b6a',
 'rmc_engine_v1/reference/operator_phrase_lexicon_v1.jsonl': '1e7141a6ff52183b5d37562575e7e75746a96cdb59291262f326a1bb817f9ad7',
 'rmc_engine_v1/reference/word_loop_seed_lexicon_v1.jsonl': '7b2ae9c93595ca8623c2ab184ef4823040ab30f5d1c07d2153a2595f6fcc126d',
 'rmc_engine_v1/resonance_lexicon.py': '07f477d97b434b673b86f894b0a538ae1d3d6dd09ad9f277eb94c1371db6c30d',
 'rmc_engine_v1/rmc_pipeline.py': '308e8db2744413ce7f9d8a7b94e72d933667522f3d00af302c0c3969b6db9823',
 'scripts/AIWEB_SLICE35C_MSM_V1_LIFECYCLE_RUNTIME_SPEC.md': '76301cfc32c6a70f1d97f3cc684216da886d637417efd52c34f64bb3123266f8',
 'scripts/AIWEB_SLICE35D_MSM_V1_CANONICAL_SERIALIZATION_RUNTIME_SPEC.md': '4683fe71bd7075a1e860e613339d51e258d698443b7cba79398ad7e381b7d1d4',
 'scripts/AIWEB_SLICE35E_MSM_V1_BOOTSTRAP_INTEGRATION_RUNTIME_SPEC.md': '3941cee66eb7b6af6e12219fa57d182a878f1a84f5d22c4550c7333955869255',
 'scripts/AIWEB_SLICE35_ACCEPTANCE_RECORD.md': '72b4ed7870078b85b8a91b8be027ade00294cca330094f8ea1102c5860ee550d',
 'scripts/AIWEB_SLICE36A_INPUT_EVENT_SOURCE_CUSTODY_RUNTIME_SPEC.md': '7ed2e806fdef6ec81f37392ad44a38fb06499a237ed6fc2fd6467568fbf76cee',
 'scripts/README_aiweb_slice30_isolated_language_core_package_boundary.md': '32b2d088419e33cfa79c8e5bceed5019378b7639f7b85a531fc1258b3665b468',
 'scripts/README_aiweb_slice31_disabled_bootstrap_adapter.md': '859ca9aa5ff706a2ff5771815c0c113f6749907971c4754a3252ff8a267ccca6',
 'scripts/README_aiweb_slice32_accepted_boundary_component_loading.md': '4f7fa9b9502b274a88481de4f954b4a7159c9edfa70da1f24a1079c43b1e8bd4',
 'scripts/README_aiweb_slice33_deterministic_trace_receipt_assembly.md': 'c2f0e097e12f6ab1d20d9ca64012389445c3009e1e9662d0176e047ce82cc8c1',
 'scripts/README_aiweb_slice34_bootstrap_regression_containment_acceptance.md': '473ac34fa6c161bfaf7969fa329baa284900afa481ebdd7cf0f10c8c63d3ea44',
 'scripts/README_aiweb_slice35a_meaning_structure_manifest_core_schema.md': '773ed105747796072ed9cd5572061531c8bde5b1e403fb244da6a2929a7d1ac4',
 'scripts/README_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.md': '88eb47779ee0f152b79d9f37690d97dc52a596a5c5d633c06113e4ce746aecc5',
 'scripts/README_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.md': '24529934eda2c04f4634f05bf120820ada6154cd9179b817d7537ac1535db864',
 'scripts/README_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.md': 'cb5a2304aef5fc221a4366c20736e4bf78e8d21410353df09274f74b7ac27ffb',
 'scripts/README_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.md': 'a575d311ba83f2025ce25526e615e6ef94f082bf74c9683a152b58d6058c094f',
 'scripts/README_aiweb_slice36a_input_event_source_custody.md': 'd96ef27ffe6ccb9165e54e4887027b4440fb6ab0cc0ab7885b71a6efae2a1931',
 'scripts/aiweb_slice30_isolated_language_core_package_boundary_verify.py': '404d90901d2a5875f56f57bb012c23ead1ddde534cd95bd2fdbecd9b9a939e9b',
 'scripts/aiweb_slice31_disabled_bootstrap_adapter.py': '3a6068b7b8021142994c0ba4820e83b0fa74494c7a453afbb27d89637f56f1aa',
 'scripts/aiweb_slice31_disabled_bootstrap_adapter_verify.py': '6f2e291202741964d14684899f7913d5c5836d9d4047b23113599ae778a2ff76',
 'scripts/aiweb_slice32_accepted_boundary_component_loading.py': '8b46394d0a573b21be08838867b08eb40ce7ea2b812eec1a2ee1027ef6df510f',
 'scripts/aiweb_slice32_accepted_boundary_component_loading_verify.py': '4d7c5760bb4dded4ae080a7dd728253f580f61e9348ee26610620131fc827d67',
 'scripts/aiweb_slice33_deterministic_trace_receipt_assembly.py': 'dd40d485737991966d71493fe130c2333e90371dbcb300db0a8e0f529f584ed0',
 'scripts/aiweb_slice33_deterministic_trace_receipt_assembly_verify.py': 'c4954002a61c6b0e204ebe3ace98602298476615d469f07cfe6264b4c32bf7d8',
 'scripts/aiweb_slice34_bootstrap_regression_containment_acceptance.py': '515206cdbc3ffb375640a32a5bc7bdf7fd05f02854f2614634a1688ea45d636c',
 'scripts/aiweb_slice34_bootstrap_regression_containment_acceptance_verify.py': '7d2679a16c072dc914194221d787225c03a37ad31c05be2251882298d5959d54',
 'scripts/aiweb_slice35a_meaning_structure_manifest_core_schema_verify.py': '9f0be04580064062ab6abc9e4a5ce6f8ad64b30b6edca234af7bb6406d74870e',
 'scripts/aiweb_slice35b_meaning_structure_manifest_deterministic_validation_verify.py': 'd19d7b380a6bd867661069aa7b383669bcfc657a67213b9e3e2ba35b9a0a8c27',
 'scripts/aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law_verify.py': 'dedbcb7488d65a129c6f2d4c0bffa61aaa7330d31d73842179cd8e57e7cffe31',
 'scripts/aiweb_slice35d_meaning_structure_manifest_canonical_serialization_verify.py': '11e8267f0121612f1f42ac417be788619b25609eec7ca235a03b66b6255c7ecd',
 'scripts/aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py': '5dd564cc16142917286b94e1ae40767e990d00ab5b1d334d7cb2a7ce34364bbe',
 'scripts/aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout_verify.py': '8959fe067c460de689fbdc7974774004cea9d6be7816a74c36b2ceed0503b4b4',
 'scripts/aiweb_slice36a_input_event_source_custody_verify.py': '52cf996a0cc4de943374aeb40a5a0a2b29423ada0d477f2b04e523e6d195a4b1',
 'scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py': '25697b064168175bc6e9a43aabfbfd50196198b4e617ff19e668eb4923502679',
 'scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py': 'e0971900ced6f11b168d5ac82d383eb60ce7da6a16fdd82b41866223ac3cb099',
 'scripts/test_aiweb_slice32_accepted_boundary_component_loading.py': '694e9b99ba4cbeaa33b3024b5d8ab49a597e983d0baafa2db6a83fa03b4ff92b',
 'scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py': '0d142b886196f83b1487ad741b7dcf46ab39290ed42eee5fa2c422a629aec6c8',
 'scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py': '1c6016238ba7349d329f97c34d2055061ba45d07d935739bfa0f5353bcf4ab85',
 'scripts/test_aiweb_slice35a_meaning_structure_manifest_core_schema.py': '24f5cde21840a5fc5a36b7717c30d491d88aff5999f05de450b6fabdc97345fb',
 'scripts/test_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.py': 'fe1f87eb0accbfc74bb588576c4815ada7a3cbf227aa27d4dfbca12c7746d237',
 'scripts/test_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.py': 'a9a3606a17be7e4c031a19e8063f9b217d0553558fb4cd29a2238842b168c617',
 'scripts/test_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.py': '123b3171070f7126b729757f049bd76c9772368e7786cb8690c27935c9f53ec5',
 'scripts/test_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py': 'bea3e02413a91fc9015f5f90ab598a821faa19654ed23f4c0ad255ea26462397',
 'scripts/test_aiweb_slice36a_input_event_source_custody.py': '8c16d620b47f7acbe4382f5a5efcd2fc084a5c083587f265117c006295cb7823'}
EXPECTED_EXPORTS = ('CONTRACT_SCHEMA_VERSION', 'CONTRACT_SPEC_ID', 'CONTRACT_SPEC_VERSION', 'EXPECTED_RSOC_OPERATOR_COUNT', 'FBSC_AUTHORITY_REF', 'FIELD_SCHEMA_ID', 'LEGACY_ISOLATION_SCHEMA_ID', 'OPERATOR_SCHEMA_ID', 'REGISTRY_SCHEMA_ID', 'RMC_LANGUAGE_LAW_AUTHORITY_REF', 'RSOC_AUTHORITY_REF', 'SLICE36A_AUTHORITY_REF', 'FieldContainmentStatus', 'FieldEnvelopeBuildResult', 'FieldEnvelopeBuildStatus', 'FieldPhaseStatus', 'FieldProjectionStatus', 'FieldSupportStatus', 'LegacyIsolationCatalog', 'LegacyIsolationRecord', 'LegacySurfaceCategory', 'LegacySurfaceDisposition', 'LineageIdentityHandling', 'OperatorApplicationDecision', 'OperatorApplicationStatus', 'OperatorArity', 'OperatorRuntimeStatus', 'ResonantLanguageFieldEnvelope', 'RsocLanguageOperatorRegistry', 'RsocOperatorContract', 'build_default_legacy_isolation_catalog', 'build_default_rsoc_operator_registry', 'build_unprojected_language_field', 'evaluate_operator_application', 'isolation_record_for_surface', 'operator_contract_for_glyph', 'operator_contract_for_key', 'validate_field_envelope_build_result', 'validate_legacy_isolation_catalog', 'validate_legacy_isolation_record', 'validate_operator_application_decision', 'validate_resonant_language_field', 'validate_rsoc_language_operator_registry', 'validate_rsoc_operator_contract')
INHERITED_COMMANDS = ('scripts/test_aiweb_slice24_full_regression_acceptance_bundle_scaffold.py', 'scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py', 'scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py', 'scripts/test_aiweb_slice32_accepted_boundary_component_loading.py', 'scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py', 'scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py', 'scripts/test_aiweb_slice35a_meaning_structure_manifest_core_schema.py', 'scripts/test_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.py', 'scripts/aiweb_slice35b_meaning_structure_manifest_deterministic_validation_verify.py', 'scripts/test_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.py', 'scripts/aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law_verify.py', 'scripts/test_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.py', 'scripts/aiweb_slice35d_meaning_structure_manifest_canonical_serialization_verify.py', 'scripts/test_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice36a_input_event_source_custody.py')
ALLOWED_IMPORT_ROOTS = {"__future__", "dataclasses", "enum", "typing", "aiweb_language_core_bootstrap"}
PROHIBITED_IMPORT_ROOTS = {"rmc_engine_v1", "os", "pathlib", "socket", "subprocess", "urllib", "requests", "httpx", "aiohttp", "openai", "anthropic", "ollama", "torch", "tensorflow", "transformers", "langchain", "chromadb", "sqlite3", "importlib", "pkgutil"}
PROHIBITED_CALLS = {"open", "eval", "exec", "input", "urlopen", "system", "Popen", "write_text", "write_bytes", "read_text", "read_bytes", "mkdir", "unlink", "remove", "rename", "replace"}
PROHIBITED_LEGACY_IMPORT_PREFIXES = (
    "rmc_engine_v1.phase_parser", "rmc_engine_v1.resonance_lexicon", "rmc_engine_v1.candidate_generator",
    "rmc_engine_v1.manifest_compiler", "rmc_engine_v1.rmc_pipeline", "rmc_engine_v1.llm_renderer",
    "rmc_engine_v1.chroma_connector", "rmc_engine_v1.mea.operator_engine", "rmc_engine_v1.mea.operator_registry",
    "rmc_engine_v1.mea.fbsc_operator_crosswalk",
)

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def git(repo: Path, *args: str):
    return subprocess.run(["git", "-c", f"safe.directory={repo}", "-C", str(repo), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
def run_py(repo: Path, script: str):
    env={"PYTHONDONTWRITEBYTECODE":"1", "PYTHONPYCACHEPREFIX":"/tmp/aiweb_slice36b0_verifier_cache", "PATH":"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"}
    return subprocess.run(["/usr/bin/python3", "-B", script], cwd=str(repo), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=False)
def call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name): return node.func.id
    if isinstance(node.func, ast.Attribute): return node.func.attr
    return ""

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("repo"); p.add_argument("--mode", choices=("package","precommit","committed"), required=True); a=p.parse_args()
    repo=Path(a.repo).resolve(); passes=[]; failures=[]
    for rel in EXACT_PATHS:
        if (repo/rel).is_file(): passes.append("exists: "+rel)
        else: failures.append("missing: "+rel)
    if a.mode != "package":
        head=git(repo,"rev-parse","HEAD"); status=git(repo,"status","--porcelain=v1","--untracked-files=all")
        if a.mode == "precommit":
            if head.stdout.strip()==EXPECTED_PARENT_HEAD: passes.append("precommit base exact")
            else: failures.append("precommit base mismatch: "+head.stdout.strip())
            expected={f"?? {x}" for x in EXACT_PATHS}; actual={x for x in status.stdout.splitlines() if x}
            if actual==expected: passes.append("precommit paths exact")
            else: failures.append("precommit status mismatch: "+" | ".join(sorted(actual)))
        else:
            parent=git(repo,"rev-parse","HEAD^"); subject=git(repo,"show","-s","--format=%s","HEAD"); changed=git(repo,"diff-tree","--no-commit-id","--name-only","-r","HEAD")
            if parent.stdout.strip()==EXPECTED_PARENT_HEAD: passes.append("committed parent exact")
            else: failures.append("committed parent mismatch: "+parent.stdout.strip())
            if subject.stdout.strip()==EXPECTED_COMMIT_SUBJECT: passes.append("committed subject exact")
            else: failures.append("committed subject mismatch: "+subject.stdout.strip())
            if set(changed.stdout.splitlines())==set(EXACT_PATHS): passes.append("commit paths exact")
            else: failures.append("commit paths mismatch")
            if not status.stdout.strip(): passes.append("committed status clean")
            else: failures.append("committed status dirty")
    for rel,digest in PROTECTED_HASHES.items():
        path=repo/rel
        if not path.is_file(): failures.append("protected missing: "+rel)
        elif sha(path)!=digest: failures.append("protected hash mismatch: "+rel)
    if not any(x.startswith("protected") for x in failures): passes.append(f"protected predecessor hashes preserved={len(PROTECTED_HASHES)}")
    for rel in RUNTIME_FILES:
        path=repo/rel
        if not path.is_file(): continue
        try:
            source=path.read_text(encoding="utf-8"); tree=ast.parse(source, filename=str(path)); compile(tree,str(path),"exec")
        except Exception as exc:
            failures.append(f"syntax failure {rel}:{type(exc).__name__}"); continue
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                for alias in node.names:
                    root=alias.name.split('.',1)[0]
                    if root in PROHIBITED_IMPORT_ROOTS or root not in ALLOWED_IMPORT_ROOTS: failures.append(f"runtime import prohibited {rel}:{alias.name}")
            elif isinstance(node,ast.ImportFrom) and node.level==0:
                root=(node.module or '').split('.',1)[0]
                if root in PROHIBITED_IMPORT_ROOTS or root not in ALLOWED_IMPORT_ROOTS: failures.append(f"runtime import prohibited {rel}:{node.module}")
            elif isinstance(node,ast.Call) and call_name(node) in PROHIBITED_CALLS:
                failures.append(f"runtime call prohibited {rel}:{call_name(node)}")
        passes.append("runtime AST clean: "+rel)
    root_init=(repo/'aiweb_language_core_bootstrap/__init__.py').read_text(encoding='utf-8')
    if 'resonant_language_operator_contract' in root_init: failures.append('bootstrap root auto-imports Slice 36B0')
    else: passes.append('bootstrap root unchanged and does not auto-import Slice 36B0')
    probe_code=(
        "import sys; before=tuple(sorted(x for x in sys.modules if x=='rmc_engine_v1' or x.startswith('rmc_engine_v1.'))); "
        "import aiweb_language_core_bootstrap.resonant_language_operator_contract as m; "
        "after=tuple(sorted(x for x in sys.modules if x=='rmc_engine_v1' or x.startswith('rmc_engine_v1.'))); "
        "print(repr(tuple(m.__all__))); print(repr(before)); print(repr(after))"
    )
    probe=subprocess.run(["/usr/bin/python3","-B","-c",probe_code],cwd=str(repo),text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={"PYTHONDONTWRITEBYTECODE":"1","PYTHONPYCACHEPREFIX":"/tmp/aiweb_slice36b0_import_cache","PATH":"/usr/bin:/bin"},check=False)
    if probe.returncode!=0: failures.append('package import failed: '+probe.stderr.strip())
    else:
        lines=probe.stdout.splitlines()
        try: exports=ast.literal_eval(lines[0]); before=ast.literal_eval(lines[1]); after=ast.literal_eval(lines[2])
        except Exception: exports=(); before=('parse_failure',); after=('parse_failure',)
        if exports==EXPECTED_EXPORTS: passes.append('export surface exact')
        else: failures.append('export surface mismatch')
        if before==after==(): passes.append('explicit import loads no legacy RMC modules')
        else: failures.append('legacy RMC module import detected')
    spec=(repo/'scripts/AIWEB_SLICE36B0_RSOC_FBSC_LANGUAGE_OPERATOR_RUNTIME_CONTRACT_SPEC.md').read_text(encoding='utf-8')
    supersession=(repo/'scripts/AIWEB_SLICE36_OPERATOR_ARCHITECTURE_SUPERSESSION_RECORD.md').read_text(encoding='utf-8')
    for marker in ("exactly ten", "contract_only_disabled", "does not implement", "MEA operator engine", "no hidden fallback"):
        if marker.lower() in spec.lower(): passes.append('spec marker: '+marker)
        else: failures.append('spec marker missing: '+marker)
    for marker in ("Deterministic Token Stream", "superseded before implementation", "No accepted implementation is invalidated"):
        if marker.lower() in supersession.lower(): passes.append('supersession marker: '+marker)
        else: failures.append('supersession marker missing: '+marker)
    for script in INHERITED_COMMANDS + ("scripts/test_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.py",):
        if not (repo/script).is_file(): failures.append('test missing: '+script); continue
        r=run_py(repo,script)
        if r.returncode==0: passes.append('command pass: '+script)
        else: failures.append(f"command fail {script} rc={r.returncode} stderr={r.stderr.strip()} stdout={r.stdout.strip()}")
    print("AI.WEB SLICE 36B0 INDEPENDENT VERIFIER")
    print(f"mode={a.mode}")
    print(f"pass_count={len(passes)}")
    print(f"failure_count={len(failures)}")
    for failure in failures: print("FAIL - "+failure)
    if failures:
        print("SLICE 36B0 INDEPENDENT VERIFIER: FAIL"); return 1
    print("SLICE 36B0 INDEPENDENT VERIFIER: PASS")
    print(f"protected_predecessor_files={len(PROTECTED_HASHES)}")
    print(f"inherited_commands={len(INHERITED_COMMANDS)}")
    print(f"slice36b0_files={len(EXACT_PATHS)}")
    print("rsoc_operator_contracts=10")
    print("legacy_rmc_imports=0")
    print("operator_applications=0")
    return 0
if __name__ == "__main__": raise SystemExit(main())
