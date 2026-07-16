#!/usr/bin/env python3
'''Independent verifier for Slice 36G deterministic structural derivation.'''

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

EXPECTED_PARENT_HEAD = "e0b96a277060f82e475eb290a4537874aeeeb46a"
EXPECTED_COMMIT_SUBJECT = "Slice 36G deterministic structural derivation and lawful non-progress"
EXACT_PATHS = ('aiweb_language_core_bootstrap/deterministic_structural_derivation/__init__.py', 'aiweb_language_core_bootstrap/deterministic_structural_derivation/schema.py', 'aiweb_language_core_bootstrap/deterministic_structural_derivation/rules.py', 'aiweb_language_core_bootstrap/deterministic_structural_derivation/derivation.py', 'aiweb_language_core_bootstrap/deterministic_structural_derivation/validation.py', 'scripts/AIWEB_SLICE36G_DETERMINISTIC_STRUCTURAL_DERIVATION_RUNTIME_SPEC.md', 'scripts/AIWEB_SLICE36G_LAWFUL_NON_PROGRESS_AND_LATER_AUTHORITY_BOUNDARY_DECISION.md', 'scripts/README_aiweb_slice36g_deterministic_structural_derivation.md', 'scripts/test_aiweb_slice36g_deterministic_structural_derivation.py', 'scripts/aiweb_slice36g_deterministic_structural_derivation_verify.py')
RUNTIME_FILES = EXACT_PATHS[:5]
PROTECTED_HASHES = {'aiweb_language_core_bootstrap/__init__.py': '0fbf450ac772eadcc2271f21a7d46d649730063764477b12276c6228ebfef9d6',
 'aiweb_language_core_bootstrap/authority.py': '03bbcdb03c8502c19ff7a5fc377875aa474d43cb0b4eb6d4471091ca42ca3838',
 'aiweb_language_core_bootstrap/bootstrap_adapter/__init__.py': 'c02d5ed2f125b86745ace30d5218e548569821653d6d5ac53b65b6cee19b530a',
 'aiweb_language_core_bootstrap/bootstrap_adapter/adapter.py': '03282793f0c470c0769fcb784aedaa1885a9e7472d7b0bb49f8f02c0725f7cb3',
 'aiweb_language_core_bootstrap/bootstrap_adapter/fixtures.py': '66013a1f044c431c12ae24121be4d026d77f1923f75008100ac158ff01f81a13',
 'aiweb_language_core_bootstrap/bootstrap_adapter/schema.py': '7d5999cdc9c96de5ab1bc367e5972fe16cc559a3fdd30a3742749661bee4eaa7',
 'aiweb_language_core_bootstrap/boundary.py': '6b7fc05767b39c794deb84d5c09f30e1a0c5894841344ab72872500d9f6c4b90',
 'aiweb_language_core_bootstrap/candidate_resonant_phase_trail/__init__.py': '496f11bd871abaa8e635d6edcf5a8cb5611b4886c1370cc12fcfe8b60a4d8efb',
 'aiweb_language_core_bootstrap/candidate_resonant_phase_trail/construction.py': '45bd565ac057bb7bf3a10e1eb4cd68fcb36424e8a5ab0ff54bcd6aa6392d1b7a',
 'aiweb_language_core_bootstrap/candidate_resonant_phase_trail/schema.py': 'ba301abce349c003f8b9527e670d5f1de2ed5bff7f1d6c49225b44ffee0390f7',
 'aiweb_language_core_bootstrap/candidate_resonant_phase_trail/transition.py': 'ca2efd19c5d15a46e9e7911de7c77f34e1c41bd34b800d74447f9559736b3d52',
 'aiweb_language_core_bootstrap/candidate_resonant_phase_trail/validation.py': 'aa5afd99f52191066249fe64c483a4ba6fcd8597d307542df9380375366fe62a',
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
 'aiweb_language_core_bootstrap/resonant_operator_candidate_binding/__init__.py': '5cc63587d1b763640f05af503f77af8cfd7cfec9fe9af60fb769b16ef3c9bbb0',
 'aiweb_language_core_bootstrap/resonant_operator_candidate_binding/binding.py': 'f72fd0510dd4205c27d8c1880f438597d7a17a52ffb055f8e20013baea577356',
 'aiweb_language_core_bootstrap/resonant_operator_candidate_binding/rules.py': '6200ad1c62b8f252c188e44658441788c27613763d10cf599e4289672c0dacd9',
 'aiweb_language_core_bootstrap/resonant_operator_candidate_binding/schema.py': 'fcc33dbc960369a522673cc42a2fb11f0ffd6071cb9afe767bb9dd26c6072a75',
 'aiweb_language_core_bootstrap/resonant_operator_candidate_binding/validation.py': 'ea8c0823b95734f1708fcb351f8d4c04eae58dffc5d4fe443ddbb6e353fe61e5',
 'aiweb_language_core_bootstrap/schema.py': '4c33a6321d32497eed63679bcd144b67d0962972df712d4452e94d1f38f45500',
 'aiweb_language_core_bootstrap/scope_attachment_reference_constraints/__init__.py': '446664fcc079a771d17aa5cebd2af7fb326b47e7be04a922031362e39e4e8645',
 'aiweb_language_core_bootstrap/scope_attachment_reference_constraints/constraints.py': '640aa967c59359383d96dcf2e27b3d5dcc2e21a55fffa4cd479cab517e34f158',
 'aiweb_language_core_bootstrap/scope_attachment_reference_constraints/rules.py': '8b6318f08104ca1c9c87d9e75185457813049f273ae4402a066f6ecc6754bd20',
 'aiweb_language_core_bootstrap/scope_attachment_reference_constraints/schema.py': '316f120091b2689fe59706c02cb2efee12561637d66a403d8f00e6557c1dc5bd',
 'aiweb_language_core_bootstrap/scope_attachment_reference_constraints/validation.py': '9f5c2c9e6a5265830adc5d70b210bbc5f50bbff1dfe9134e57c8f102df683635',
 'aiweb_language_core_bootstrap/source_field_projection/__init__.py': '5ff30a359371218b7fbdda42d68d9b8f9500a96fd8ceff9b0c10b522f99dd896',
 'aiweb_language_core_bootstrap/source_field_projection/projection.py': '411e6057888656fe668cce4b52ebbd63178e474852f9117c0ab30f08f96351a0',
 'aiweb_language_core_bootstrap/source_field_projection/reconstruction.py': 'c93f899cef2169e062dcee1f8f6bff5097c6704c27210def08368a595f55e514',
 'aiweb_language_core_bootstrap/source_field_projection/schema.py': 'ef7a8b3d06e1a6491d22ac2e2ca4ab786dedca09d6a94d7f34c76f87de593a09',
 'aiweb_language_core_bootstrap/source_field_projection/validation.py': '894ab4c7fc767c311827c42dc57244a302dd45c5e402fded9d88c69be19d7458',
 'aiweb_language_core_bootstrap/symbolic_grammar_operator_registry/__init__.py': '6c40aa24ebe41b52c594e9dda6bd59d2e9a428d76c1c44396a291d6b1ea25045',
 'aiweb_language_core_bootstrap/symbolic_grammar_operator_registry/proposal_contract.py': '1d5ca895644c5aec5cf9edf68e8f93358831eb90ad8f0010e6206670c7f29907',
 'aiweb_language_core_bootstrap/symbolic_grammar_operator_registry/registry.py': '4ec813b75ea27521c8267d7708ed072c4e2c0bbd443dc60b71f910477a5cbe6e',
 'aiweb_language_core_bootstrap/symbolic_grammar_operator_registry/schema.py': 'ab7cd566a9c2f40ede86f0e6b8174e34ecdde7c1ce4b1dc7d74e6ff0d1575d56',
 'aiweb_language_core_bootstrap/symbolic_grammar_operator_registry/validation.py': 'd61165541efedab3b01ee81d35a3623b01d1afb41915fb00962e8b658ff70015',
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
 'scripts/AIWEB_SLICE36C_FBSC_RSOC_GRAMMAR_OPERATOR_SEPARATION_DECISION.md': '62eead52c58a96861907e3abc34f84483acd5f34a0627353c4b28b29eee47a0f',
 'scripts/AIWEB_SLICE36C_SYMBOLIC_GRAMMAR_OPERATOR_REGISTRY_RUNTIME_SPEC.md': '2d57caba26c3b0b2af78311ae3882e9ac7b378dab15c51eb96f300e13af7b8a0',
 'scripts/AIWEB_SLICE36D_ACTION_LIKE_SIGNAL_PREDICATE_BOUNDARY_DECISION.md': 'd657d568a71b5be758d087178811c10011a56804fa77041294b6b19fc578b802',
 'scripts/AIWEB_SLICE36D_RESONANT_OPERATOR_CANDIDATE_BINDING_RUNTIME_SPEC.md': '33a2e60ad17df4e8782898b5a98059f1788909b483488c57bc11ef9e9f6520ec',
 'scripts/AIWEB_SLICE36E_CANDIDATE_RESONANT_PHASE_TRAIL_RUNTIME_SPEC.md': '3b00b8584a1f5ab86fea70dadd22d22936a2ab7c2c5b6d28bd8ba919ab04efa3',
 'scripts/AIWEB_SLICE36E_RSOC_CORE_APPLICATION_AND_PHASE_TRANSITION_BOUNDARY_DECISION.md': '75239efb8bc532bd45040469973deee81dfe54b6abfdde4445783a5f57ea8d12',
 'scripts/AIWEB_SLICE36F_EXPLICIT_CONTEXT_AND_FALSE_AUTHORITY_CONVERSION_DECISION.md': 'db88422f161491a3ba8511d349392f54971c88c05b5856107c4e022cd5fa37f2',
 'scripts/AIWEB_SLICE36F_SCOPE_ATTACHMENT_REFERENCE_CONSTRAINTS_RUNTIME_SPEC.md': '4750d91dd007d95a928114ff172d7d2c58e5a282ff0adf9506a11dd74c668f79',
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
 'scripts/README_aiweb_slice36c_symbolic_grammar_operator_registry.md': 'fa004ba21fe0aea7629277409130c30d8447f507ab8b6e8cb36b5833e9f6d38d',
 'scripts/README_aiweb_slice36d_resonant_operator_candidate_binding.md': '39c084ef8a00507c1850737f498cf9b7de4643664cf18e04f1495686ec054a0e',
 'scripts/README_aiweb_slice36e_candidate_resonant_phase_trail.md': '20fc497578857e44b7b74afdb174c661fe62915145722f768945169c1f6fa72a',
 'scripts/README_aiweb_slice36f_scope_attachment_reference_constraints.md': '0c15ce1e3ba2a487e7800f43d957dee5783dbbe1014390ba38fe0b8cce9a4792',
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
 'scripts/aiweb_slice36c_symbolic_grammar_operator_registry_verify.py': 'e969e17db1724a5f01b40741364f42d7b4bc6962d457d883f40672beda1f58d0',
 'scripts/aiweb_slice36d_resonant_operator_candidate_binding_verify.py': '62f0e1098a4daf112bcffc12444abd239517ed2744c51dfec0a255cd4b7a0338',
 'scripts/aiweb_slice36e_candidate_resonant_phase_trail_verify.py': 'd43099cfddea419c9480770de1e2dadbb5cf6bd65ba18eed5003a2039f2caa5b',
 'scripts/aiweb_slice36f_scope_attachment_reference_constraints_verify.py': 'ee2f2bf38d6aaf250009a064376562df8aef2d55cd311ae8d447899996a0b943',
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
 'scripts/test_aiweb_slice36b_deterministic_source_field_projection.py': '06028cd92090e85a5c3f6eb8fff827653ae59b4d40bd07638d89558630a5ba73',
 'scripts/test_aiweb_slice36c_symbolic_grammar_operator_registry.py': '71e4614d6cdc64019e6e3d37c3b6c074defc9499be029b881576eb9d16ed3069',
 'scripts/test_aiweb_slice36d_resonant_operator_candidate_binding.py': '145aa2fc66086a8d4af063c53fc28faf4e62ef9b0c8e09045025dd5637ff704e',
 'scripts/test_aiweb_slice36e_candidate_resonant_phase_trail.py': 'a2aec411ee84c9a806739a32b14807263a7e41cb9f58d566ad6efcaab7d5fd9c',
 'scripts/test_aiweb_slice36f_scope_attachment_reference_constraints.py': '65d6db52e56951c34e569dd73f2fbbdcea275b1bd55cb4ea18e9710be93b0275'}
INHERITED_COMMANDS = ('scripts/test_aiweb_slice24_full_regression_acceptance_bundle_scaffold.py', 'scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py', 'scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py', 'scripts/test_aiweb_slice32_accepted_boundary_component_loading.py', 'scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py', 'scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py', 'scripts/test_aiweb_slice35a_meaning_structure_manifest_core_schema.py', 'scripts/test_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.py', 'scripts/aiweb_slice35b_meaning_structure_manifest_deterministic_validation_verify.py', 'scripts/test_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.py', 'scripts/aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law_verify.py', 'scripts/test_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.py', 'scripts/aiweb_slice35d_meaning_structure_manifest_canonical_serialization_verify.py', 'scripts/test_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice36a_input_event_source_custody.py', 'scripts/test_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.py', 'scripts/test_aiweb_slice36b_deterministic_source_field_projection.py', 'scripts/test_aiweb_slice36c_symbolic_grammar_operator_registry.py', 'scripts/test_aiweb_slice36d_resonant_operator_candidate_binding.py', 'scripts/test_aiweb_slice36e_candidate_resonant_phase_trail.py', 'scripts/test_aiweb_slice36f_scope_attachment_reference_constraints.py')

PROHIBITED_IMPORT_PREFIXES = (
    "rmc_engine_v1", "openai", "anthropic", "ollama", "chromadb",
    "langchain", "transformers", "torch", "tensorflow", "sklearn",
    "requests", "httpx", "aiohttp", "socket", "urllib", "subprocess",
)
PROHIBITED_RUNTIME_CALLS = (
    "open", "eval", "exec", "compile", "__import__", "os.system",
    "os.popen", "subprocess.run", "subprocess.call", "subprocess.Popen",
    "Path.read_text", "Path.read_bytes", "Path.write_text",
    "Path.write_bytes", "Path.open",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command, *, cwd: Path, env=None):
    return subprocess.run(
        list(command), cwd=str(cwd), env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )


def git(repo: Path, *args: str):
    return run(("git", "-C", str(repo), *args), cwd=repo)


def dotted_name(node: ast.AST) -> str:
    parts=[]
    current=node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current=current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("--mode", required=True, choices=("precommit", "committed"))
    args=parser.parse_args()
    repo=Path(args.repository).resolve()
    passes=[]
    failures=[]

    def check(condition, label):
        (passes if condition else failures).append(label)

    print("AI.WEB SLICE 36G INDEPENDENT VERIFIER")
    print(f"mode={args.mode}")
    check((repo/".git").is_dir(), "Forge Git repository exists")

    branch=git(repo,"branch","--show-current")
    head=git(repo,"rev-parse","HEAD")
    subject=git(repo,"show","-s","--format=%s","HEAD")
    status=git(repo,"status","--porcelain=v1","--untracked-files=all")
    staged=git(repo,"diff","--cached","--name-only")
    unstaged=git(repo,"diff","--name-only")
    diff_check=git(repo,"diff","--check")
    check(branch.returncode==0 and branch.stdout.strip()=="main", "branch main")
    check(diff_check.returncode==0, "git diff check")

    if args.mode=="precommit":
        actual=tuple(sorted(x for x in status.stdout.splitlines() if x))
        expected=tuple(sorted(f"?? {path}" for path in EXACT_PATHS))
        check(head.returncode==0 and head.stdout.strip()==EXPECTED_PARENT_HEAD,
              "precommit HEAD is accepted Slice 36F")
        check(status.returncode==0 and actual==expected,
              "precommit status is exact ten-file Slice 36G set")
        check(staged.returncode==0 and staged.stdout=="", "precommit index empty")
        check(unstaged.returncode==0 and unstaged.stdout=="", "precommit tracked files unmodified")
    else:
        parent=git(repo,"rev-parse","HEAD^")
        paths=git(repo,"diff-tree","--no-commit-id","--name-only","-r","HEAD")
        actual=tuple(sorted(x for x in paths.stdout.splitlines() if x))
        check(parent.returncode==0 and parent.stdout.strip()==EXPECTED_PARENT_HEAD,
              "committed parent is accepted Slice 36F")
        check(subject.returncode==0 and subject.stdout.strip()==EXPECTED_COMMIT_SUBJECT,
              "committed subject exact")
        check(paths.returncode==0 and actual==tuple(sorted(EXACT_PATHS)),
              "committed path set exact")
        check(status.returncode==0 and status.stdout=="", "committed repository clean")

    mismatches=[]
    for relative,digest in sorted(PROTECTED_HASHES.items()):
        path=repo/relative
        if not path.is_file() or path.is_symlink() or sha256_file(path)!=digest:
            mismatches.append(relative)
    check(not mismatches, "all protected predecessor files unchanged")
    check(all((repo/p).is_file() and not (repo/p).is_symlink() for p in EXACT_PATHS),
          "all exact Slice 36G files present")

    caches=[]
    for path in repo.rglob("*"):
        rel=path.relative_to(repo)
        if rel.parts and rel.parts[0] in {".git",".venv"}:
            continue
        if "__pycache__" in rel.parts or path.suffix in {".pyc",".pyo"}:
            caches.append(rel.as_posix())
    check(not caches, "Python cache artifacts absent from project source")

    syntax=[]; imports=[]; calls=[]
    for relative in RUNTIME_FILES:
        try:
            tree=ast.parse((repo/relative).read_text(encoding="utf-8"), filename=relative)
        except Exception as error:
            syntax.append(f"{relative}:{error}")
            continue
        for node in ast.walk(tree):
            modules=[]
            if isinstance(node,ast.Import): modules.extend(a.name for a in node.names)
            elif isinstance(node,ast.ImportFrom): modules.append(node.module or "")
            for module in modules:
                if module.startswith(PROHIBITED_IMPORT_PREFIXES):
                    imports.append(f"{relative}:{getattr(node,'lineno',0)}:{module}")
            if isinstance(node,ast.Call):
                name=dotted_name(node.func)
                if name in PROHIBITED_RUNTIME_CALLS:
                    calls.append(f"{relative}:{getattr(node,'lineno',0)}:{name}")
    check(not syntax, "Slice 36G runtime syntax valid")
    check(not imports, "Slice 36G prohibited imports absent")
    check(not calls, "Slice 36G external runtime calls absent")

    doc_terms={
        "scripts/AIWEB_SLICE36G_DETERMINISTIC_STRUCTURAL_DERIVATION_RUNTIME_SPEC.md": (
            "Non-progress is a valid structural result",
            "Slice 39 owns candidate-meaning construction",
            "Slice 40 owns gate evaluation",
        ),
        "scripts/AIWEB_SLICE36G_LAWFUL_NON_PROGRESS_AND_LATER_AUTHORITY_BOUNDARY_DECISION.md": (
            "structural candidate is not CandidateMeaning",
            "unresolved structure is not a request for clarification",
            "non-progress is not failure and must not be guessed away",
        ),
    }
    defects=[]
    for relative,terms in doc_terms.items():
        text=(repo/relative).read_text(encoding="utf-8")
        defects.extend(f"{relative}:{term}" for term in terms if term not in text)
    check(not defects, "governing documentation complete")

    cache_root=Path(tempfile.mkdtemp(prefix="aiweb_slice36g_verify_cache_",dir="/tmp"))
    env=os.environ.copy(); env["PYTHONDONTWRITEBYTECODE"]="1"; env["PYTHONPYCACHEPREFIX"]=str(cache_root)
    own=run(("/usr/bin/python3","-B","scripts/test_aiweb_slice36g_deterministic_structural_derivation.py"),cwd=repo,env=env)
    if own.returncode!=0:
        print(own.stdout,end=""); print(own.stderr,end="",file=sys.stderr)
    check(own.returncode==0 and "AI.WEB SLICE 36G BEHAVIOR TEST: PASS" in own.stdout,
          "Slice 36G behavior test")

    inherited_failures=[]
    for relative in INHERITED_COMMANDS:
        command=run(("/usr/bin/python3","-B",relative),cwd=repo,env=env)
        if command.returncode!=0:
            inherited_failures.append(relative)
            print(f"--- inherited failure: {relative} ---")
            print(command.stdout,end=""); print(command.stderr,end="",file=sys.stderr)
    check(not inherited_failures, "all inherited verification commands")

    probe_code=r'''from aiweb_language_core_bootstrap.input_event_custody import capture_input_event
from aiweb_language_core_bootstrap.source_field_projection import project_source_field
from aiweb_language_core_bootstrap.resonant_operator_candidate_binding import bind_resonant_operator_candidates
from aiweb_language_core_bootstrap.candidate_resonant_phase_trail import construct_candidate_resonant_phase_trails
from aiweb_language_core_bootstrap.scope_attachment_reference_constraints import apply_scope_attachment_reference_constraints
from aiweb_language_core_bootstrap.deterministic_structural_derivation import derive_deterministic_structural_analysis, build_default_structural_derivation_rules
import json
c=capture_input_event("Do not install it.",source_id="verifier.fixture",channel_id="verifier.fixture",sequence_number=1)
p=project_source_field(c.event)
b=bind_resonant_operator_candidates(p)
t=construct_candidate_resonant_phase_trails(p,b)
s=apply_scope_attachment_reference_constraints(p,b,t)
r=derive_deterministic_structural_analysis(c,p,b,t,s)
ss=r.structural_set
assert ss is not None
print(json.dumps({
 "rules":len(build_default_structural_derivation_rules()),
 "candidates":ss.candidate_count,
 "traces":sum(len(x.rule_application_traces) for x in ss.candidates),
 "graph_nodes":sum(len(x.operator_graph.nodes) for x in ss.candidates),
 "graph_edges":sum(len(x.operator_graph.edges) for x in ss.candidates),
 "explicit_non_progress":int(ss.non_progress_result is not None),
 "selected_structures":int(ss.selected_structural_candidate_id is not None),
 "candidate_meaning":int(ss.candidate_meaning_created),
 "clarification":int(ss.clarification_question_asked),
 "authority_effects":int(any((r.selected_meaning,r.permission_inferred,r.capability_selected,r.route_registration_performed,r.tool_routing_performed,r.action_performed,r.memory_write_performed,r.outward_answer_rendered,r.delivery_performed))),
}))
'''
    probe=run(("/usr/bin/python3","-B","-c",probe_code),cwd=repo,env=env)
    metrics={}
    if probe.returncode==0:
        try: metrics=json.loads(probe.stdout.strip().splitlines()[-1])
        except Exception: metrics={}
    expected_metrics={"rules":10,"candidates":8,"traces":89,"graph_nodes":10,"graph_edges":3,
                      "explicit_non_progress":1,"selected_structures":0,"candidate_meaning":0,
                      "clarification":0,"authority_effects":0}
    check(metrics==expected_metrics, "runtime governing metrics exact")

    print(f"pass_count={len(passes)}")
    print(f"failure_count={len(failures)}")
    if failures:
        for label in failures: print(f"FAIL: {label}")
        print("SLICE 36G INDEPENDENT VERIFIER: FAIL")
        return 1
    print("SLICE 36G INDEPENDENT VERIFIER: PASS")
    print(f"protected_predecessor_files={len(PROTECTED_HASHES)}")
    print(f"inherited_commands={len(INHERITED_COMMANDS)}")
    print(f"slice36g_files={len(EXACT_PATHS)}")
    print("structural_derivation_rules=10")
    print("governing_example_structural_candidates=8")
    print("governing_example_rule_traces=89")
    print("explicit_non_progress_results=1")
    print("selected_structures=0")
    print("candidate_meaning_records=0")
    print("clarification_questions=0")
    print("meaning_permission_route_action_effects=0")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
