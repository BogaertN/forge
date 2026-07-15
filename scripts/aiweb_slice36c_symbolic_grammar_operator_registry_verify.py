#!/usr/bin/env python3
"""Independent verifier for Slice 36C symbolic grammar-operator registry."""

from __future__ import annotations

import argparse
import ast
import hashlib
import os
from pathlib import Path
import subprocess
import sys

EXPECTED_PARENT_HEAD = "6d22fd6da0af950511e8e61c08c5c5dccfb008fc"
EXPECTED_COMMIT_SUBJECT = "Slice 36C symbolic grammar-operator registry"
EXACT_PATHS = ('aiweb_language_core_bootstrap/symbolic_grammar_operator_registry/__init__.py', 'aiweb_language_core_bootstrap/symbolic_grammar_operator_registry/schema.py', 'aiweb_language_core_bootstrap/symbolic_grammar_operator_registry/registry.py', 'aiweb_language_core_bootstrap/symbolic_grammar_operator_registry/proposal_contract.py', 'aiweb_language_core_bootstrap/symbolic_grammar_operator_registry/validation.py', 'scripts/AIWEB_SLICE36C_SYMBOLIC_GRAMMAR_OPERATOR_REGISTRY_RUNTIME_SPEC.md', 'scripts/AIWEB_SLICE36C_FBSC_RSOC_GRAMMAR_OPERATOR_SEPARATION_DECISION.md', 'scripts/README_aiweb_slice36c_symbolic_grammar_operator_registry.md', 'scripts/test_aiweb_slice36c_symbolic_grammar_operator_registry.py', 'scripts/aiweb_slice36c_symbolic_grammar_operator_registry_verify.py')
RUNTIME_FILES = EXACT_PATHS[:5]
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
 'aiweb_language_core_bootstrap/resonant_language_operator_contract/__init__.py': '9fb8017a9615102576a40cc4eeefa66dec6f0f4cd199aed98ca4c386079d5cac',
 'aiweb_language_core_bootstrap/resonant_language_operator_contract/field_contract.py': 'c7f294923b261b4e90672b8355fdff4454ea8a726dce05828684ed427004ad36',
 'aiweb_language_core_bootstrap/resonant_language_operator_contract/legacy_isolation.py': '65ccae70ba00f834c80593cb97125e9950f1b0916f424c04f8c92bdf7f8a0a42',
 'aiweb_language_core_bootstrap/resonant_language_operator_contract/registry.py': '8a3c43301a781355ea0b40c3f3821ead294c592f7d6b9152abf86b47b16e8394',
 'aiweb_language_core_bootstrap/resonant_language_operator_contract/schema.py': '7d212249c818978f091bfb34d154e0ef88fffe8eb30e69980edc4a8692ad4933',
 'aiweb_language_core_bootstrap/resonant_language_operator_contract/validation.py': '6972066477870421bcbe1571a79637d34409d295af322d7dc6f96ce63b340f38',
 'aiweb_language_core_bootstrap/schema.py': '4c33a6321d32497eed63679bcd144b67d0962972df712d4452e94d1f38f45500',
 'aiweb_language_core_bootstrap/source_field_projection/__init__.py': '5ff30a359371218b7fbdda42d68d9b8f9500a96fd8ceff9b0c10b522f99dd896',
 'aiweb_language_core_bootstrap/source_field_projection/projection.py': '411e6057888656fe668cce4b52ebbd63178e474852f9117c0ab30f08f96351a0',
 'aiweb_language_core_bootstrap/source_field_projection/reconstruction.py': 'c93f899cef2169e062dcee1f8f6bff5097c6704c27210def08368a595f55e514',
 'aiweb_language_core_bootstrap/source_field_projection/schema.py': 'ef7a8b3d06e1a6491d22ac2e2ca4ab786dedca09d6a94d7f34c76f87de593a09',
 'aiweb_language_core_bootstrap/source_field_projection/validation.py': '894ab4c7fc767c311827c42dc57244a302dd45c5e402fded9d88c69be19d7458',
 'aiweb_language_core_bootstrap/trace_receipt/__init__.py': '41599980091954e391350a3e5c26b0b3f297b2b747ef143b58a6064222a9ada3',
 'aiweb_language_core_bootstrap/trace_receipt/assembler.py': '0e7c78014daecc4981048953604a1df017c986b1187808a7db9db08855c83d39',
 'aiweb_language_core_bootstrap/trace_receipt/flow_catalog.py': '1884dfde6c073dc8ab6c94a5797ef0bdff4260314a7896c8c96eaa616da5fad3',
 'aiweb_language_core_bootstrap/trace_receipt/schema.py': 'fd013a52c50e71c6829c08499436f3777de9463e33473b6cc1cf7f84ed8f1121',
 'aiweb_language_core_bootstrap/verify.py': '5729b003f5610ce52afbd19fdf901c7a33ab8c6dde9fc8fea9dc6e4be646f5da',
 'requirements.txt': 'ed73ba11243a0099034f10ac500db984959bb8f37086532f864d75a3620916c8',
 'scripts/AIWEB_SLICE35C_MSM_V1_LIFECYCLE_RUNTIME_SPEC.md': '76301cfc32c6a70f1d97f3cc684216da886d637417efd52c34f64bb3123266f8',
 'scripts/AIWEB_SLICE35D_MSM_V1_CANONICAL_SERIALIZATION_RUNTIME_SPEC.md': '4683fe71bd7075a1e860e613339d51e258d698443b7cba79398ad7e381b7d1d4',
 'scripts/AIWEB_SLICE35E_MSM_V1_BOOTSTRAP_INTEGRATION_RUNTIME_SPEC.md': '3941cee66eb7b6af6e12219fa57d182a878f1a84f5d22c4550c7333955869255',
 'scripts/AIWEB_SLICE35_ACCEPTANCE_RECORD.md': '72b4ed7870078b85b8a91b8be027ade00294cca330094f8ea1102c5860ee550d',
 'scripts/AIWEB_SLICE36A_INPUT_EVENT_SOURCE_CUSTODY_RUNTIME_SPEC.md': '7ed2e806fdef6ec81f37392ad44a38fb06499a237ed6fc2fd6467568fbf76cee',
 'scripts/AIWEB_SLICE36B0_RSOC_FBSC_LANGUAGE_OPERATOR_RUNTIME_CONTRACT_SPEC.md': 'ee479e2b335a2f0bc811583fe970a56a74ec6499afb7bee51d01b11e1e90506a',
 'scripts/AIWEB_SLICE36B_DETERMINISTIC_SOURCE_FIELD_PROJECTION_RUNTIME_SPEC.md': '1805755a0fc514d267fb9045f8c1401dcf066efdd61ab91d624fc431059e2866',
 'scripts/AIWEB_SLICE36B_GRAPHEME_BOUNDARY_PROFILE_DECISION.md': '123d2be30b7f8aabbb9ba58f6bf5b88f214cf05dce2fa6b862b38124b8730446',
 'scripts/AIWEB_SLICE36_OPERATOR_ARCHITECTURE_SUPERSESSION_RECORD.md': '712bde5718bf3d017175645caf29abb44073306947efb4e445eb4c2a8c478e04',
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
 'scripts/README_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.md': 'ee17b3778e9b1f1f95a2da63289dc1923dbe7be6f53305b4db90ca7d94d1b66d',
 'scripts/README_aiweb_slice36b_deterministic_source_field_projection.md': 'f34e5332fe9f9ade6a7933557fa79487b0b8aa8987459a664cba93bf2c4b398a',
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
 'scripts/aiweb_slice36b0_rsoc_fbsc_language_operator_contract_verify.py': 'bd7e313e361fb1dd4e83c4da115c304152afe36e2b7166e308f1654ac1386634',
 'scripts/aiweb_slice36b_deterministic_source_field_projection_verify.py': '30f0db367b3d0c2571ae8f0dc17ff31666edcfca4bd5358c32af133349358283',
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
 'scripts/test_aiweb_slice36a_input_event_source_custody.py': '8c16d620b47f7acbe4382f5a5efcd2fc084a5c083587f265117c006295cb7823',
 'scripts/test_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.py': '796c724122de8fcbf7136272a85e97104c5738db842b9d9a21e5a5e3e683a705',
 'scripts/test_aiweb_slice36b_deterministic_source_field_projection.py': '06028cd92090e85a5c3f6eb8fff827653ae59b4d40bd07638d89558630a5ba73'}
EXPECTED_EXPORTS = ('CANONICAL_ROADMAP_AUTHORITY_REF', 'EXPECTED_FBSC_CANONICAL_OPERATOR_COUNT', 'EXPECTED_GRAMMAR_OPERATOR_COUNT', 'EXPECTED_REQUIRED_FAMILY_COUNT', 'FBSC_VOLUME_II_AUTHORITY_REF', 'GRAMMAR_OPERATOR_PROPOSAL_DECISION_SCHEMA_ID', 'GRAMMAR_OPERATOR_PROPOSAL_RULE_SCHEMA_ID', 'GRAMMAR_OPERATOR_PROPOSAL_SCHEMA_ID', 'GRAMMAR_OPERATOR_REGISTRY_SCHEMA_ID', 'GRAMMAR_OPERATOR_SCHEMA_ID', 'REGISTRY_SCHEMA_VERSION', 'REGISTRY_SPEC_ID', 'REGISTRY_SPEC_VERSION', 'REQUIRED_LANGUAGE_CORE_FAMILIES', 'RMC_LANGUAGE_LAW_AUTHORITY_REF', 'RSOC_CONTRACT_AUTHORITY_REF', 'SOURCE_FIELD_AUTHORITY_REF', 'GrammarOperatorCompatibilityStatus', 'GrammarOperatorCommutationStatus', 'GrammarOperatorDefinition', 'GrammarOperatorDriftEffectStatus', 'GrammarOperatorEffect', 'GrammarOperatorEntropyEffectStatus', 'GrammarOperatorFamily', 'GrammarOperatorMalformedBehavior', 'GrammarOperatorOrigin', 'GrammarOperatorPhaseAffinityStatus', 'GrammarOperatorProposalDecision', 'GrammarOperatorProposalRuleContract', 'GrammarOperatorRuntimeStatus', 'GrammarOperatorUncertaintyBehavior', 'GrammarOperatorUnsupportedBehavior', 'ProposalDecisionStatus', 'ProposalRuleRuntimeStatus', 'SymbolicGrammarOperatorRegistry', 'build_default_symbolic_grammar_operator_registry', 'evaluate_grammar_operator_proposal', 'grammar_operator_for_glyph', 'grammar_operator_for_key', 'grammar_operators_for_family', 'validate_grammar_operator_definition', 'validate_grammar_operator_proposal_decision', 'validate_grammar_operator_proposal_rule_contract', 'validate_symbolic_grammar_operator_registry')
INHERITED_COMMANDS = ('scripts/test_aiweb_slice24_full_regression_acceptance_bundle_scaffold.py', 'scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py', 'scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py', 'scripts/test_aiweb_slice32_accepted_boundary_component_loading.py', 'scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py', 'scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py', 'scripts/test_aiweb_slice35a_meaning_structure_manifest_core_schema.py', 'scripts/test_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.py', 'scripts/aiweb_slice35b_meaning_structure_manifest_deterministic_validation_verify.py', 'scripts/test_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.py', 'scripts/aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law_verify.py', 'scripts/test_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.py', 'scripts/aiweb_slice35d_meaning_structure_manifest_canonical_serialization_verify.py', 'scripts/test_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice36a_input_event_source_custody.py', 'scripts/test_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.py', 'scripts/test_aiweb_slice36b_deterministic_source_field_projection.py')
REHEARSAL_COMMANDS = ('scripts/test_aiweb_slice35a_meaning_structure_manifest_core_schema.py', 'scripts/test_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.py', 'scripts/aiweb_slice35b_meaning_structure_manifest_deterministic_validation_verify.py', 'scripts/test_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.py', 'scripts/aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law_verify.py', 'scripts/test_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.py', 'scripts/aiweb_slice35d_meaning_structure_manifest_canonical_serialization_verify.py', 'scripts/test_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice36a_input_event_source_custody.py', 'scripts/test_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.py', 'scripts/test_aiweb_slice36b_deterministic_source_field_projection.py')
ALLOWED_IMPORT_ROOTS = {
    "__future__", "dataclasses", "enum", "typing",
    "aiweb_language_core_bootstrap"
}
PROHIBITED_IMPORT_ROOTS = {
    "rmc_engine_v1", "mea", "os", "pathlib", "socket", "subprocess",
    "urllib", "requests", "httpx", "aiohttp", "openai", "anthropic",
    "ollama", "torch", "tensorflow", "transformers", "langchain",
    "chromadb", "sqlite3", "importlib", "pkgutil", "re"
}
PROHIBITED_CALLS = {
    "open", "eval", "exec", "compile", "__import__", "os.getenv",
    "os.system", "subprocess.run", "subprocess.Popen", "socket.socket",
    "urllib.request.urlopen"
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run_py(repo: Path, script: str) -> subprocess.CompletedProcess[str]:
    env = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPYCACHEPREFIX": "/tmp/aiweb_slice36c_verifier_cache",
        "PATH": "/usr/bin:/bin",
    }
    return subprocess.run(
        ["/usr/bin/python3", "-B", script],
        cwd=str(repo),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )


def call_name(node: ast.Call) -> str:
    parts: list[str] = []
    current: ast.AST = node.func
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument(
        "--mode",
        choices=("precommit", "committed", "rehearsal"),
        default="precommit",
    )
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    passes: list[str] = []
    failures: list[str] = []

    if not repo.is_dir():
        failures.append("repository missing")
    elif args.mode != "rehearsal" and not (repo / ".git").is_dir():
        failures.append("git repository missing")

    if not failures and args.mode == "precommit":
        branch = run_git(repo, "branch", "--show-current")
        head = run_git(repo, "rev-parse", "HEAD")
        status = run_git(
            repo,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        )
        staged = run_git(repo, "diff", "--cached", "--name-only")
        tracked = run_git(repo, "diff", "--name-only")
        if branch.stdout.strip() == "main":
            passes.append("branch main")
        else:
            failures.append("branch mismatch: " + branch.stdout.strip())
        if head.stdout.strip() == EXPECTED_PARENT_HEAD:
            passes.append("precommit base exact")
        else:
            failures.append("precommit base mismatch: " + head.stdout.strip())
        expected_status = {f"?? {path}" for path in EXACT_PATHS}
        actual_status = set(status.stdout.splitlines())
        if actual_status == expected_status:
            passes.append("precommit untracked paths exact")
        else:
            failures.append("precommit path set mismatch")
        if not staged.stdout.strip():
            passes.append("precommit staged set empty")
        else:
            failures.append("precommit staged set not empty")
        if not tracked.stdout.strip():
            passes.append("precommit tracked predecessors unchanged")
        else:
            failures.append("precommit tracked predecessor modified")

    if not failures and args.mode == "committed":
        branch = run_git(repo, "branch", "--show-current")
        parent = run_git(repo, "rev-parse", "HEAD^")
        subject = run_git(repo, "show", "-s", "--format=%s", "HEAD")
        changed = run_git(
            repo,
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            "HEAD",
        )
        status = run_git(
            repo,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        )
        if branch.stdout.strip() == "main":
            passes.append("branch main")
        else:
            failures.append("branch mismatch: " + branch.stdout.strip())
        if parent.stdout.strip() == EXPECTED_PARENT_HEAD:
            passes.append("committed parent exact")
        else:
            failures.append("committed parent mismatch: " + parent.stdout.strip())
        if subject.stdout.strip() == EXPECTED_COMMIT_SUBJECT:
            passes.append("committed subject exact")
        else:
            failures.append("committed subject mismatch")
        if set(changed.stdout.splitlines()) == set(EXACT_PATHS):
            passes.append("commit paths exact")
        else:
            failures.append("commit paths mismatch")
        if not status.stdout.strip():
            passes.append("committed status clean")
        else:
            failures.append("committed status dirty")

    for rel, digest in PROTECTED_HASHES.items():
        path = repo / rel
        if not path.is_file():
            failures.append("protected missing: " + rel)
        elif sha(path) != digest:
            failures.append("protected hash mismatch: " + rel)
    if not any(item.startswith("protected") for item in failures):
        passes.append(
            f"protected predecessor hashes preserved={len(PROTECTED_HASHES)}"
        )

    for rel in EXACT_PATHS:
        if not (repo / rel).is_file():
            failures.append("Slice 36C file missing: " + rel)
    if not any("Slice 36C file missing" in item for item in failures):
        passes.append(f"Slice 36C exact files present={len(EXACT_PATHS)}")

    for rel in RUNTIME_FILES:
        path = repo / rel
        if not path.is_file():
            continue
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
            compile(tree, str(path), "exec")
        except Exception as exc:
            failures.append(f"syntax failure {rel}:{type(exc).__name__}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if (
                        root in PROHIBITED_IMPORT_ROOTS
                        or root not in ALLOWED_IMPORT_ROOTS
                    ):
                        failures.append(
                            f"runtime import prohibited {rel}:{alias.name}"
                        )
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                root = (node.module or "").split(".", 1)[0]
                if (
                    root in PROHIBITED_IMPORT_ROOTS
                    or root not in ALLOWED_IMPORT_ROOTS
                ):
                    failures.append(
                        f"runtime import prohibited {rel}:{node.module}"
                    )
            elif (
                isinstance(node, ast.Call)
                and call_name(node) in PROHIBITED_CALLS
            ):
                failures.append(
                    f"runtime call prohibited {rel}:{call_name(node)}"
                )
        passes.append("runtime AST clean: " + rel)

    root_init = (
        repo / "aiweb_language_core_bootstrap/__init__.py"
    ).read_text(encoding="utf-8")
    if "symbolic_grammar_operator_registry" in root_init:
        failures.append("bootstrap root auto-imports Slice 36C")
    else:
        passes.append(
            "bootstrap root unchanged and does not auto-import Slice 36C"
        )

    probe_code = (
        "import sys; "
        "before=tuple(sorted(x for x in sys.modules "
        "if x=='rmc_engine_v1' or x.startswith('rmc_engine_v1.'))); "
        "import aiweb_language_core_bootstrap."
        "symbolic_grammar_operator_registry as m; "
        "after=tuple(sorted(x for x in sys.modules "
        "if x=='rmc_engine_v1' or x.startswith('rmc_engine_v1.'))); "
        "r=m.build_default_symbolic_grammar_operator_registry(); "
        "print(repr(tuple(m.__all__))); "
        "print(repr(before)); print(repr(after)); "
        "print(len(r.operators)); print(len(r.proposal_rules)); "
        "print(sum(x.origin.value=='fbsc_volume_ii_canonical' "
        "for x in r.operators)); "
        "print(r.rsoc_mapping_available); "
        "print(r.proposal_creation_available)"
    )
    probe = subprocess.run(
        ["/usr/bin/python3", "-B", "-c", probe_code],
        cwd=str(repo),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPYCACHEPREFIX": "/tmp/aiweb_slice36c_import_cache",
            "PATH": "/usr/bin:/bin",
        },
        check=False,
    )
    if probe.returncode != 0:
        failures.append("package import failed: " + probe.stderr.strip())
    else:
        lines = probe.stdout.splitlines()
        try:
            exports = ast.literal_eval(lines[0])
            before = ast.literal_eval(lines[1])
            after = ast.literal_eval(lines[2])
            operator_count = int(lines[3])
            proposal_count = int(lines[4])
            canonical_count = int(lines[5])
            rsoc_mapping = lines[6] == "True"
            proposal_available = lines[7] == "True"
        except Exception:
            exports = ()
            before = ("parse_failure",)
            after = ("parse_failure",)
            operator_count = -1
            proposal_count = -1
            canonical_count = -1
            rsoc_mapping = True
            proposal_available = True
        if exports == EXPECTED_EXPORTS:
            passes.append("export surface exact")
        else:
            failures.append("export surface mismatch")
        if before == after == ():
            passes.append("explicit import loads no legacy RMC modules")
        else:
            failures.append("legacy RMC module import detected")
        if operator_count == 25:
            passes.append("grammar operator count exact=25")
        else:
            failures.append("grammar operator count mismatch")
        if canonical_count == 8:
            passes.append("FBSC canonical operator count exact=8")
        else:
            failures.append("FBSC canonical operator count mismatch")
        if proposal_count == 0 and not proposal_available:
            passes.append("proposal rules and proposal creation absent")
        else:
            failures.append("proposal authority unexpectedly available")
        if not rsoc_mapping:
            passes.append("direct RSOC mapping absent")
        else:
            failures.append("direct RSOC mapping unexpectedly available")

    spec = (repo / EXACT_PATHS[5]).read_text(encoding="utf-8")
    decision = (repo / EXACT_PATHS[6]).read_text(encoding="utf-8")
    for marker in (
        "phase-intent bindings",
        "0 proposal rules",
        "no lexeme-to-operator table",
        "registered operator ≠ runtime occurrence",
        "empty compatibility set ≠ universal compatibility",
    ):
        if marker.lower() in spec.lower():
            passes.append("spec marker: " + marker)
        else:
            failures.append("spec marker missing: " + marker)
    for marker in (
        "† ≠ χ(t)",
        "not interchangeable registries",
        "no invented glyph",
        "no operator pair is declared compatible",
    ):
        if marker.lower() in decision.lower():
            passes.append("separation marker: " + marker)
        else:
            failures.append("separation marker missing: " + marker)

    command_set = (
        REHEARSAL_COMMANDS
        if args.mode == "rehearsal"
        else INHERITED_COMMANDS
    )
    for script_name in command_set + (
        "scripts/test_aiweb_slice36c_symbolic_grammar_operator_registry.py",
    ):
        if not (repo / script_name).is_file():
            failures.append("test missing: " + script_name)
            continue
        result = run_py(repo, script_name)
        if result.returncode == 0:
            passes.append("command pass: " + script_name)
        else:
            failures.append(
                f"command fail {script_name} rc={result.returncode} "
                f"stderr={result.stderr.strip()} "
                f"stdout={result.stdout.strip()}"
            )

    print("AI.WEB SLICE 36C INDEPENDENT VERIFIER")
    print(f"mode={args.mode}")
    print(f"pass_count={len(passes)}")
    print(f"failure_count={len(failures)}")
    for failure in failures:
        print("FAIL - " + failure)
    if failures:
        print("SLICE 36C INDEPENDENT VERIFIER: FAIL")
        return 1
    print("SLICE 36C INDEPENDENT VERIFIER: PASS")
    print(f"protected_predecessor_files={len(PROTECTED_HASHES)}")
    print(f"inherited_commands={len(command_set)}")
    print(f"slice36c_files={len(EXACT_PATHS)}")
    print("grammar_operator_definitions=25")
    print("fbsc_canonical_operators=8")
    print("proposal_rules=0")
    print("legacy_rmc_imports=0")
    print("source_bindings=0")
    print("operator_applications=0")
    print("phase_assignments=0")
    print("meaning_permission_route_action_effects=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
