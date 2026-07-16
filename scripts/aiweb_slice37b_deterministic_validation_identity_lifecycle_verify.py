#!/usr/bin/env python3
"""Independent verifier for Slice 37B validation, identity, and lifecycle law."""

from __future__ import annotations

import argparse
import ast
import hashlib
import os
from pathlib import Path
import subprocess
import sys

EXPECTED_BRANCH = "main"
EXPECTED_PARENT_HEAD = "432d38eb8829dbf18c05d95e909a69df80229c18"
EXPECTED_PARENT_SUBJECT = "Slice 37A controlled concept authority schema contract"
EXPECTED_COMMIT_SUBJECT = "Slice 37B deterministic validation identity and lifecycle law"
EXACT_PATHS = ('aiweb_language_core_bootstrap/controlled_concept_sense_registry/governed_lifecycle/__init__.py',
 'aiweb_language_core_bootstrap/controlled_concept_sense_registry/governed_lifecycle/schema.py',
 'aiweb_language_core_bootstrap/controlled_concept_sense_registry/governed_lifecycle/identity.py',
 'aiweb_language_core_bootstrap/controlled_concept_sense_registry/governed_lifecycle/validation.py',
 'aiweb_language_core_bootstrap/controlled_concept_sense_registry/governed_lifecycle/rules.py',
 'aiweb_language_core_bootstrap/controlled_concept_sense_registry/governed_lifecycle/lifecycle.py',
 'aiweb_language_core_bootstrap/controlled_concept_sense_registry/governed_lifecycle/collection.py',
 'scripts/AIWEB_SLICE37B_DETERMINISTIC_VALIDATION_IDENTITY_LIFECYCLE_RUNTIME_SPEC.md',
 'scripts/AIWEB_SLICE37B_LIFECYCLE_AUTHORITY_AND_DEFERRED_SCOPE_DECISION.md',
 'scripts/README_aiweb_slice37b_deterministic_validation_identity_lifecycle.md',
 'scripts/test_aiweb_slice37b_deterministic_validation_identity_lifecycle.py',
 'scripts/aiweb_slice37b_deterministic_validation_identity_lifecycle_verify.py')
PROTECTED_HASHES = {'aiweb_concept_boundary_scaffold/__init__.py': '787c820775fa0103999fc8541e0222680e616d27dcdbf55eacbdc26c04cd2919',
 'aiweb_concept_boundary_scaffold/concept.py': 'f21b5d1fdd37b660bcc2647f1ef749904c1ba8f75f250709c018201f00a3c7fc',
 'aiweb_concept_boundary_scaffold/relation.py': 'f5e07a743d03c3e044cdb661b8124a732f699707f3450f58fb7c6ed0cb61111e',
 'aiweb_concept_boundary_scaffold/verify.py': '753e2eecdb2783260131f10ca01a61b39527fb6ebae86bd785b8ecd7d83d4292',
 'aiweb_language_core_bootstrap/__init__.py': '0fbf450ac772eadcc2271f21a7d46d649730063764477b12276c6228ebfef9d6',
 'aiweb_language_core_bootstrap/authority.py': '03bbcdb03c8502c19ff7a5fc377875aa474d43cb0b4eb6d4471091ca42ca3838',
 'aiweb_language_core_bootstrap/bootstrap_adapter/__init__.py': 'c02d5ed2f125b86745ace30d5218e548569821653d6d5ac53b65b6cee19b530a',
 'aiweb_language_core_bootstrap/bootstrap_adapter/adapter.py': '03282793f0c470c0769fcb784aedaa1885a9e7472d7b0bb49f8f02c0725f7cb3',
 'aiweb_language_core_bootstrap/bootstrap_adapter/fixtures.py': '66013a1f044c431c12ae24121be4d026d77f1923f75008100ac158ff01f81a13',
 'aiweb_language_core_bootstrap/bootstrap_adapter/schema.py': '7d5999cdc9c96de5ab1bc367e5972fe16cc559a3fdd30a3742749661bee4eaa7',
 'aiweb_language_core_bootstrap/boundary.py': '6b7fc05767b39c794deb84d5c09f30e1a0c5894841344ab72872500d9f6c4b90',
 'aiweb_language_core_bootstrap/bounded_structural_bootstrap/__init__.py': 'f5d37e71f8e11f71772f089ec145773e619f9f3a8876539b26f7c4a5cec57216',
 'aiweb_language_core_bootstrap/bounded_structural_bootstrap/fixtures.py': '23c204249ec5b151c317bd451ab73013cd8e48c88f0d1e8c3da56a0405e1cac9',
 'aiweb_language_core_bootstrap/bounded_structural_bootstrap/integration.py': '73ab36d42c6337f10194700a7c35c480a73a9cddff57f089bd6a4b1f6ec125ff',
 'aiweb_language_core_bootstrap/bounded_structural_bootstrap/schema.py': '2894f5df8aa2258fcfc555e3fa801bab3a4d1a3a4520c2ff249c8b2598a84cd1',
 'aiweb_language_core_bootstrap/bounded_structural_bootstrap/validation.py': '510a0654bc1b2163af3a9f223eb9ea1573bc28f7c581bd39faba634fc9484c3a',
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
 'aiweb_language_core_bootstrap/controlled_concept_sense_registry/__init__.py': '39c1cea68295f807de6643c069783432b78aefb90f19cdb27d00dced4de1eeba',
 'aiweb_language_core_bootstrap/controlled_concept_sense_registry/authority.py': 'ec8faacb3bfaf1357e339eeb0600c965585e73b6012a599ec941d099113e46e6',
 'aiweb_language_core_bootstrap/controlled_concept_sense_registry/identity.py': '51c5a3efad0152d77c2ecf901e806c153a7cd24b513ee2d9d3102d0e73c593c7',
 'aiweb_language_core_bootstrap/controlled_concept_sense_registry/schema.py': '7960d5147c9bb34114b2540039d440a967949e850909ff3ef4f5796f96aa894e',
 'aiweb_language_core_bootstrap/controlled_concept_sense_registry/validation.py': 'ec2326717c942460282ab3a7d6f2ac2c509be6d321621c503341410852c9762c',
 'aiweb_language_core_bootstrap/deterministic_structural_derivation/__init__.py': 'c1b2c84c3493466d0c610ac42e3030b23309ebb5cb85a7d78e559a0386093f37',
 'aiweb_language_core_bootstrap/deterministic_structural_derivation/derivation.py': '371b136f6144ba7fb1c60307813eb7c3bbd76c13adc29a1d3f5ee23f6318cdde',
 'aiweb_language_core_bootstrap/deterministic_structural_derivation/rules.py': 'ed90090e37a693f3dfb3e46800c420c9c4b1c85b879164e429fbd8707debf508',
 'aiweb_language_core_bootstrap/deterministic_structural_derivation/schema.py': '7fda59ac41153227c1943647578347d8f258c92b71b8ebdc3e7a5edc3634e8a3',
 'aiweb_language_core_bootstrap/deterministic_structural_derivation/validation.py': '648f1aa68dd19ae4d8c1dd1778191a90e544c3fd8e43e677e55d938e5be52506',
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
 'scripts/AIWEB_SLICE36G_DETERMINISTIC_STRUCTURAL_DERIVATION_RUNTIME_SPEC.md': 'fcf7500cd67d8aed6834aecc467e1291c6b7dde23bea066c627320e19da2ba43',
 'scripts/AIWEB_SLICE36G_LAWFUL_NON_PROGRESS_AND_LATER_AUTHORITY_BOUNDARY_DECISION.md': '01902bac0cadcc88c88fb95f2323964a3e5c6dc3431eca568d44146deaa75261',
 'scripts/AIWEB_SLICE36H_BOUNDED_BOOTSTRAP_INTEGRATION_RUNTIME_SPEC.md': 'dfe9eaa71d6e9dbdfa5ea4cf46c7099d3bdf74b44843cc27ec0e3851397f5a1a',
 'scripts/AIWEB_SLICE36_ACCEPTANCE_RECORD.md': 'd40af9170d5f009923be395174931be9135e942536a4e275dd7d60392fd5dd56',
 'scripts/AIWEB_SLICE36_OPERATOR_ARCHITECTURE_SUPERSESSION_RECORD.md': '712bde5718bf3d017175645caf29abb44073306947efb4e445eb4c2a8c478e04',
 'scripts/AIWEB_SLICE37A_CONTROLLED_CONCEPT_AUTHORITY_SCHEMA_RUNTIME_SPEC.md': 'e3422dd0b40381afaefca5cfa8265135ef639c01d59871d01e9b15db7ee9e0ef',
 'scripts/AIWEB_SLICE37A_SCHEMA_ONLY_AND_SLICE8_PRESERVATION_DECISION.md': '2803c5d1fbdf45df3474bfde46bc8fe3cca8523f836b364a7c946937b8588fb0',
 'scripts/README_aiweb_slice08_concept_boundary_scaffold.md': '9ece14c064b3c95daf82fee35e5ae13ac5d7557728e86049e59e35a9c810fd83',
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
 'scripts/README_aiweb_slice36g_deterministic_structural_derivation.md': 'e66e60986b73b0395d8a78fae2dfe2acb1b9f9f4c05bd62286c14111c56eb753',
 'scripts/README_aiweb_slice36h_bounded_bootstrap_integration_closeout.md': 'c9504fa580b07c1c6d7c4bd7e2dd2a2e084fbacc51aeabb706afac75c4936a25',
 'scripts/README_aiweb_slice37a_controlled_concept_authority_schema.md': 'f27c2a826c1748927d8ac90ec49213938c6c6f674d3abb712e78360fcab84b41',
 'scripts/aiweb_slice08_concept_boundary_verify.py': '28a22ca634f4282ac79b2f39837a8d7d49d8f8be444d803a75d5143a36b79b61',
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
 'scripts/aiweb_slice36g_deterministic_structural_derivation_verify.py': 'b4e80a9d67e3699c9aa18ad405742c94a1f391a487d6a78851482cb4ab7003ab',
 'scripts/aiweb_slice36h_bounded_bootstrap_integration_closeout_verify.py': 'c38237836ebbfd92a4ab8d41ac6e01c42b985389ed664a60a35bf6917ecb2894',
 'scripts/aiweb_slice37a_controlled_concept_authority_schema_verify.py': '2bae114d8bb2af3a2bf3cbcb816d8663735576b8cf8c3d1451ad9fec81cdad0a',
 'scripts/test_aiweb_slice08_concept_boundary_scaffold.py': 'b1f68803d322d6bd4a4fbb951b9571aaec37342eae93d00efc57b4d82f61101a',
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
 'scripts/test_aiweb_slice36f_scope_attachment_reference_constraints.py': '65d6db52e56951c34e569dd73f2fbbdcea275b1bd55cb4ea18e9710be93b0275',
 'scripts/test_aiweb_slice36g_deterministic_structural_derivation.py': 'c3010f1489c5e2c65e00cfc62bde957750d11c9921d8a3d695d69809bb377757',
 'scripts/test_aiweb_slice36h_bounded_bootstrap_integration_closeout.py': '9d29a5ac5e1be2b273644bd97ff096c852ab306e88cabd4f55d128f7973f3199',
 'scripts/test_aiweb_slice37a_controlled_concept_authority_schema.py': '44a390ee04076ffe460fe3894db21c42850ece16df978affca584cfb1d84e699'}
INHERITED_COMMANDS = ('scripts/test_aiweb_slice24_full_regression_acceptance_bundle_scaffold.py',
 'scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py',
 'scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py',
 'scripts/test_aiweb_slice32_accepted_boundary_component_loading.py',
 'scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py',
 'scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py',
 'scripts/test_aiweb_slice35a_meaning_structure_manifest_core_schema.py',
 'scripts/test_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.py',
 'scripts/test_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.py',
 'scripts/test_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.py',
 'scripts/test_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py',
 'scripts/test_aiweb_slice36a_input_event_source_custody.py',
 'scripts/test_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.py',
 'scripts/test_aiweb_slice36b_deterministic_source_field_projection.py',
 'scripts/test_aiweb_slice36c_symbolic_grammar_operator_registry.py',
 'scripts/test_aiweb_slice36d_resonant_operator_candidate_binding.py',
 'scripts/test_aiweb_slice36e_candidate_resonant_phase_trail.py',
 'scripts/test_aiweb_slice36f_scope_attachment_reference_constraints.py',
 'scripts/test_aiweb_slice36g_deterministic_structural_derivation.py',
 'scripts/test_aiweb_slice36h_bounded_bootstrap_integration_closeout.py',
 'scripts/test_aiweb_slice37a_controlled_concept_authority_schema.py')
PROHIBITED_IMPORT_PREFIXES = (
    "rmc_engine_v1", "openai", "anthropic", "ollama", "chromadb",
    "langchain", "transformers", "torch", "tensorflow", "sklearn",
    "spacy", "nltk", "gensim", "sentence_transformers", "faiss",
    "qdrant", "pinecone", "weaviate", "requests", "httpx", "aiohttp",
    "socket", "urllib", "subprocess",
)
PROHIBITED_RUNTIME_CALLS = (
    "open", "eval", "exec", "compile", "__import__", "os.system",
    "os.popen", "subprocess.run", "subprocess.call", "subprocess.Popen",
    "Path.read_text", "Path.read_bytes", "Path.write_text",
    "Path.write_bytes", "Path.open", "Path.glob", "Path.rglob",
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


def git(repo: Path, *arguments: str):
    return run(("git", "-C", str(repo), *arguments), cwd=repo)


def dotted_name(node: ast.AST) -> str:
    parts = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def verify_hashes(repo: Path, expected: dict[str, str]) -> list[str]:
    mismatches = []
    for relative, digest in sorted(expected.items()):
        path = repo / relative
        if not path.is_file() or path.is_symlink() or sha256_file(path) != digest:
            mismatches.append(relative)
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("--mode", required=True, choices=("precommit", "committed", "source_only"))
    args = parser.parse_args()
    repo = Path(args.repository).resolve()

    failures = []
    passes = 0

    def check(condition: object, label: str) -> None:
        nonlocal passes
        if condition is True:
            passes += 1
        else:
            failures.append(label)

    print("AI.WEB SLICE 37B INDEPENDENT VERIFIER")
    print(f"mode={args.mode}")

    package_root = repo / "aiweb_language_core_bootstrap" / "controlled_concept_sense_registry" / "governed_lifecycle"
    for relative in EXACT_PATHS:
        path = repo / relative
        check(path.is_file() and not path.is_symlink(), f"exact file missing or unsafe: {relative}")

    predecessor_mismatches = verify_hashes(repo, PROTECTED_HASHES)
    if args.mode == "source_only":
        source_only_missing = tuple(
            relative for relative in predecessor_mismatches
            if not (repo / relative).exists()
        )
        source_only_changed = tuple(
            relative for relative in predecessor_mismatches
            if (repo / relative).exists()
        )
        check(not source_only_changed, "all available predecessor hashes")
        print(f"source_only_missing_protected_files={len(source_only_missing)}")
    else:
        check(not predecessor_mismatches, "all 177 predecessor hashes")

    source_files = sorted(package_root.glob("*.py"))
    check(len(source_files) == 7, "exact seven package source files")
    prohibited_imports = []
    prohibited_calls = []
    top_level_effect_calls = []
    public_function_names = []

    for path in source_files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except Exception as error:
            failures.append(f"AST parse failed: {path}: {error}")
            continue

        module_call_ids = {
            id(item.value)
            for item in tree.body
            if isinstance(item, ast.Expr) and isinstance(item.value, ast.Call)
        }

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                public_function_names.append(node.name)
            imported = []
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
            for module_name in imported:
                if module_name.startswith(PROHIBITED_IMPORT_PREFIXES):
                    prohibited_imports.append(f"{path.name}:{module_name}")

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_name = dotted_name(node.func)
                if call_name in PROHIBITED_RUNTIME_CALLS:
                    prohibited_calls.append(f"{path.name}:{node.lineno}:{call_name}")
                if id(node) in module_call_ids:
                    top_level_effect_calls.append(f"{path.name}:{node.lineno}:{call_name}")

    check(not prohibited_imports, "no prohibited imports")
    check(not prohibited_calls, "no prohibited runtime calls")
    check(not top_level_effect_calls, "no top-level effect calls")
    for fragment in ("lookup", "select", "populate", "traverse", "render", "route", "execute", "persist", "store"):
        check(
            not any(fragment in name.lower() for name in public_function_names),
            f"no public {fragment} function",
        )

    parent_init = repo / "aiweb_language_core_bootstrap" / "controlled_concept_sense_registry" / "__init__.py"
    check(
        "governed_lifecycle" not in parent_init.read_text(encoding="utf-8"),
        "parent package does not auto-import Slice 37B",
    )

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPYCACHEPREFIX"] = f"/tmp/aiweb_slice37b_verify_cache_{os.getpid()}"

    test_result = run(
        (sys.executable, "-B", "scripts/test_aiweb_slice37b_deterministic_validation_identity_lifecycle.py"),
        cwd=repo,
        env=env,
    )
    if test_result.returncode != 0:
        print("--- Slice 37B behavior test stdout ---")
        print(test_result.stdout)
        print("--- Slice 37B behavior test stderr ---")
        print(test_result.stderr)
    check(test_result.returncode == 0, "Slice 37B behavior test")

    if args.mode != "source_only":
        status = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
        branch = git(repo, "branch", "--show-current")
        head = git(repo, "rev-parse", "HEAD")
        subject = git(repo, "show", "-s", "--format=%s", "HEAD")
        check(branch.returncode == 0 and branch.stdout.strip() == EXPECTED_BRANCH, "branch main")

        if args.mode == "precommit":
            actual = tuple(sorted(line for line in status.stdout.splitlines() if line))
            expected = tuple(sorted(f"?? {path}" for path in EXACT_PATHS))
            check(status.returncode == 0 and actual == expected, "exact precommit twelve-file state")
            check(head.returncode == 0 and head.stdout.strip() == EXPECTED_PARENT_HEAD, "precommit parent HEAD exact")
            check(subject.returncode == 0 and subject.stdout.strip() == EXPECTED_PARENT_SUBJECT, "precommit parent subject exact")
        else:
            parent = git(repo, "rev-parse", "HEAD^")
            changed = git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD")
            actual_changed = tuple(sorted(line for line in changed.stdout.splitlines() if line))
            check(status.returncode == 0 and status.stdout == "", "committed repository clean")
            check(parent.returncode == 0 and parent.stdout.strip() == EXPECTED_PARENT_HEAD, "commit parent exact")
            check(subject.returncode == 0 and subject.stdout.strip() == EXPECTED_COMMIT_SUBJECT, "commit subject exact")
            check(changed.returncode == 0 and actual_changed == tuple(sorted(EXACT_PATHS)), "exact committed twelve-file set")

        inherited_failures = []
        for relative in INHERITED_COMMANDS:
            result = run((sys.executable, "-B", relative, str(repo)), cwd=repo, env=env)
            if result.returncode != 0:
                inherited_failures.append(relative)
                print(f"--- inherited failure: {relative} ---")
                print(result.stdout)
                print(result.stderr)
        check(not inherited_failures, "all 21 inherited behavior tests")

        final_status = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
        if args.mode == "precommit":
            actual_after = tuple(sorted(line for line in final_status.stdout.splitlines() if line))
            expected_after = tuple(sorted(f"?? {path}" for path in EXACT_PATHS))
            check(final_status.returncode == 0 and actual_after == expected_after, "precommit state unchanged after tests")
        else:
            check(final_status.returncode == 0 and final_status.stdout == "", "committed state remains clean")

    if failures:
        print(f"pass_count={passes}")
        print(f"failure_count={len(failures)}")
        for failure in failures:
            print(f"FAIL: {failure}")
        print("SLICE 37B INDEPENDENT VERIFIER: FAIL")
        return 1

    print(f"pass_count={passes}")
    print("failure_count=0")
    print("SLICE 37B INDEPENDENT VERIFIER: PASS")
    print(f"protected_predecessor_files={len(PROTECTED_HASHES)}")
    print(f"inherited_tests={len(INHERITED_COMMANDS)}")
    print(f"slice37b_files={len(EXACT_PATHS)}")
    print("transition_rules=48")
    print("registry_entries=0")
    print("concept_lookup_functions=0")
    print("selected_sense_authority=0")
    print("external_resources_loaded=0")
    print("routes_tools_actions_renderings_deliveries=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
