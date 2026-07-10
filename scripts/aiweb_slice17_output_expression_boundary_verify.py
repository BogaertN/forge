#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import re
import sys
from pathlib import Path

EXPECTED_BASE_HEAD = "3b640f380b8633ce93143d178dcbee143503f03d"
ALLOWED_NEW_PATHS = (
    "aiweb_output_expression_boundary_scaffold/__init__.py",
    "aiweb_output_expression_boundary_scaffold/core.py",
    "aiweb_output_expression_boundary_scaffold/expression_source.py",
    "aiweb_output_expression_boundary_scaffold/preservation_contract.py",
    "aiweb_output_expression_boundary_scaffold/expression_plan.py",
    "aiweb_output_expression_boundary_scaffold/expression_preview.py",
    "aiweb_output_expression_boundary_scaffold/fidelity.py",
    "aiweb_output_expression_boundary_scaffold/expression_receipt.py",
    "aiweb_output_expression_boundary_scaffold/verify.py",
    "scripts/test_aiweb_slice17_output_expression_boundary_scaffold.py",
    "scripts/aiweb_slice17_output_expression_boundary_verify.py",
    "scripts/README_aiweb_slice17_output_expression_boundary_scaffold.md",
)
PROTECTED_HASHES = {
    'SHA256SUMS.txt': '1fab75fe5dae5714f0620db393a38523837df6e35ded2e572525e2c56bff7cb5',
    'agents/forge/knowledge_base.py': '9782c971cb4ac107b15963c7c418d65ba6e4618fa6ecaee6835f210c8eb61bbc',
    'agents/forge/runner.py': 'ff555a5bf6a29a7aa50adc000c087ffaefb678c394dac929920e145a9a458d19',
    'aiweb_ambiguity_clarification_boundary_scaffold/__init__.py': '376939019726a337bd9b2d2b43e79105fb18579eea487d523979e87b8ce537ef',
    'aiweb_ambiguity_clarification_boundary_scaffold/clarification.py': '140eccb26277519c1539a3cd194e9bdc7170a65cd45e2094f2256055298e2977',
    'aiweb_ambiguity_clarification_boundary_scaffold/state_boundary.py': 'f2a914f2587c2376411bcfdc96717bd5bc2d9100e1a0a30af43e9804b9f10732',
    'aiweb_ambiguity_clarification_boundary_scaffold/trace_state.py': '2ec6e2dfe5ed59ce49bd90dd1e73fd6fc6a0262ff43e20a30e69c368cde412d4',
    'aiweb_ambiguity_clarification_boundary_scaffold/unknown_support.py': 'fefe226143767deafbaeea1488d7affaef75fe7fb63f1c548e3dca9ee5976eef',
    'aiweb_ambiguity_clarification_boundary_scaffold/verify.py': 'bb6121d47d835f2157adf0337f54ff2ead6c9d000379818cedac5d2d71512be7',
    'aiweb_authority_scanner_scaffold/__init__.py': 'cf383c67b146c5413743f04e5bd6be693a83f8ee6aa234be600933567e2b24fe',
    'aiweb_authority_scanner_scaffold/catalog.py': 'f53052fd9d4a2bc051c005e0f34e5c3bdda13a16a2802f27c95d516dbc9c30a9',
    'aiweb_authority_scanner_scaffold/scanner.py': '45be0d6afca51b5fd687e656802cd4415dbdea2e21dee1f7c7d5139d653cfd58',
    'aiweb_authority_scanner_scaffold/verify.py': 'f24dd680b04ccea7b8a6c26b726fed6f1bceb3c492a00500db9b1eed851121f8',
    'aiweb_candidate_meaning_boundary_scaffold/__init__.py': '07be39311a3563a90ad89c77de502a487e2b740215b32a1da82ea67c5d6bf810',
    'aiweb_candidate_meaning_boundary_scaffold/candidate.py': '5fdb30acb68ee1a0b1a48f639058f8a981e795f4b69d20d1ef26dab974a529be',
    'aiweb_candidate_meaning_boundary_scaffold/competition.py': '5e222eae015c49508be07b6119a818453e3ae8c35a0efcc0325bf27bd3d78ce5',
    'aiweb_candidate_meaning_boundary_scaffold/derived_structure.py': '57659c65162b2f5acfd5ce23040fe5f123edd076bc1a4975fed4888cd950dfbf',
    'aiweb_candidate_meaning_boundary_scaffold/source_custody.py': '7370031d4191534736b3b19cca31b0a82f7d07daf58e20f31e334666c2012cc5',
    'aiweb_candidate_meaning_boundary_scaffold/support_boundary.py': '1ef93acef5e906c8e332ad305035e5206f264f510db85522051b9d60a707de0d',
    'aiweb_candidate_meaning_boundary_scaffold/verify.py': '69533395e5dd2134c93fc47c02a6b426b0f3e688a05a85ae0ea472ce372631a9',
    'aiweb_concept_boundary_scaffold/__init__.py': '787c820775fa0103999fc8541e0222680e616d27dcdbf55eacbdc26c04cd2919',
    'aiweb_concept_boundary_scaffold/concept.py': 'f21b5d1fdd37b660bcc2647f1ef749904c1ba8f75f250709c018201f00a3c7fc',
    'aiweb_concept_boundary_scaffold/relation.py': 'f5e07a743d03c3e044cdb661b8124a732f699707f3450f58fb7c6ed0cb61111e',
    'aiweb_concept_boundary_scaffold/verify.py': '753e2eecdb2783260131f10ca01a61b39527fb6ebae86bd785b8ecd7d83d4292',
    'aiweb_corpus_evidence_memory_trace_scaffold/__init__.py': 'dd137d44866587626b5452099b8781e585225d326e1799d8ef5c67197cb32e53',
    'aiweb_corpus_evidence_memory_trace_scaffold/authority.py': '82c4b766b297399c03aaa3bd61fd74a4d189442542b63639678dc7cee0055903',
    'aiweb_corpus_evidence_memory_trace_scaffold/category.py': '02de5b0f94bc1c8fbe6aab520ab5d2eb3872b4686015bad100eaa03e21061064',
    'aiweb_corpus_evidence_memory_trace_scaffold/core.py': '2e810179d8f179dc19accc755b8e6cda62023c7a800a6994a865ee44e17fb8d2',
    'aiweb_corpus_evidence_memory_trace_scaffold/corpus.py': '209fc292faf930447b241ee1550bf3ec15d96d5874235b821c4d9600bc3112dd',
    'aiweb_corpus_evidence_memory_trace_scaffold/evidence.py': '14a470f7a381e6f137be53d934454a00c454fefbb73a6ff0d52201060ed6892a',
    'aiweb_corpus_evidence_memory_trace_scaffold/memory.py': '2332e478f268c37f5468de0620c9ce8d859fe80acc4b58151078301b012462a3',
    'aiweb_corpus_evidence_memory_trace_scaffold/separation.py': 'b19ed9f06fe80ab1316658024d2a448359c311d0400d607ec4a6246a21b838ad',
    'aiweb_corpus_evidence_memory_trace_scaffold/source_mention.py': 'ae6a19fa28259b10ab5de756b1f80170e1d9dd0563d8644ec3f71feec41580da',
    'aiweb_corpus_evidence_memory_trace_scaffold/trace.py': '63f9192032c1abf0648e744183d5315c99e8c62590a3a5e283269584cc0068a5',
    'aiweb_corpus_evidence_memory_trace_scaffold/verify.py': 'c90425d3d04663164daf434c832054fd146404617a5cf6823f7ce71560af5c05',
    'aiweb_decision_baseline_scaffold/__init__.py': 'cae089f9a632bb408b450680dfe17fc9450ab0570b38ad69f62dac8274c0c1ec',
    'aiweb_decision_baseline_scaffold/baseline.py': '0e365f71a1ee711950f8d21ddcf006ceb544a1dfd2b8aa04aae8800524529155',
    'aiweb_decision_baseline_scaffold/decision.py': '160df3e7d4d72ac72122a04587d7983c21680d34ea253747c33c7fc2f7fa9e6a',
    'aiweb_decision_baseline_scaffold/verify.py': '395d5291dbde7f56dac9d1f1e0ef7d21a40116c14490eb54fd9b4aab9546ea39',
    'aiweb_external_resource_quarantine_scaffold/__init__.py': '9ba840ad19ffacbbe995454883dc64ac65c1be68a2b83c929adbba8a1808ca85',
    'aiweb_external_resource_quarantine_scaffold/core.py': '23a11c6289581ffd90987cfb2f9fac8eaa9f7b32fbaaa176ad45919db4afce5c',
    'aiweb_external_resource_quarantine_scaffold/decision.py': 'cfe956c38d717d6fd2768c47328ea90a6b04604f69591f643df2a97cfbbb296d',
    'aiweb_external_resource_quarantine_scaffold/identity.py': '94b193e11a5824d8d8d93a41f3f1b29b08359b0a3a22c0f0a090145a826cec02',
    'aiweb_external_resource_quarantine_scaffold/license_custody.py': 'c6ac247ea3f9c921becddb735b69950bd21e7afc53b9c0fbe330ec567c8f2813',
    'aiweb_external_resource_quarantine_scaffold/provenance.py': 'fcdf5fab6685fe6abff6c51c8a89b04c2e267a3b02104c2001abc1b8ca567959',
    'aiweb_external_resource_quarantine_scaffold/purpose.py': '282d4639f1bef4987e78f209ba9984bb5711d63ed159c9eeb8ff4a35979b5335',
    'aiweb_external_resource_quarantine_scaffold/receipt.py': '8c5f99cf4a9c6775564adaa4e91dbc3f74deb47e418e6c653c417e53291def97',
    'aiweb_external_resource_quarantine_scaffold/verify.py': '24527acbd8a8a42163dcd7897aac1cc9eaa8ead8bb90e9bbba62ac7f51f27bb7',
    'aiweb_gp014_regression_scaffold/__init__.py': '380cfae1d3c71bc35eacd208f034c1dbffb60c2f4bca79e89f3dec876f1ab57c',
    'aiweb_gp014_regression_scaffold/baseline.py': '91b5564ed16416689c9c4a1412a05d6466af95495264b74e28164247c2956e42',
    'aiweb_gp014_regression_scaffold/regression.py': 'a76e7d2623f76bcd64808197bce849f748e16a2a0453e18cb86c17a2a7855ca7',
    'aiweb_gp014_regression_scaffold/verify.py': 'ec65b2b62e1abbe4bb0f2d64cf066e3c1f105cbfc7277faafd5fef53fd7d5a66',
    'aiweb_implementation_ledger_scaffold/__init__.py': '39893aa567a5209dc83fec27ac1263da37b788647096711765044739e0ed0a87',
    'aiweb_implementation_ledger_scaffold/cycle.py': '7c85a514eee2f0aaab584f355dfd73295f608523358052a913fa6188c0396085',
    'aiweb_implementation_ledger_scaffold/ledger.py': '3865db7cd780acef1b218ceacdb135edbe531cd8dfe6866e9b90388d0790e92c',
    'aiweb_implementation_ledger_scaffold/verify.py': '73ecffe0a44b589adb16ed78f185060881fe350fe57de77ae77350c392dc6971',
    'aiweb_meaning_law_trace_scaffold/__init__.py': '2142ce5510c865b34a0553cf950536408ca977f1f477a8a7ac06e1aa0d64988a',
    'aiweb_meaning_law_trace_scaffold/law_trace.py': 'e014ee7ca6983ada2b07f040e45a06570f488b07ebe5daafd2c86d3776d98323',
    'aiweb_meaning_law_trace_scaffold/meaning_object.py': '867763fe3b12ddfaa578977f302608af8818bab5d46e5ff86248a8d8b4b467bc',
    'aiweb_meaning_law_trace_scaffold/verify.py': 'd2459bfb3781fc9f39aaa2d074d3061bb05afeb15b6aa87f4c81cfc844d19aa3',
    'aiweb_predicate_role_boundary_scaffold/__init__.py': '38d806e8be6e22bd32e5505c521cddd02b506ba046ebe8f3fe319b4e9cf67f86',
    'aiweb_predicate_role_boundary_scaffold/effect_boundary.py': '009b5a6c00ba64b397aa99d6ece1b71e331de997c6e7339903e2d47f8da9cd75',
    'aiweb_predicate_role_boundary_scaffold/predicate_frame.py': 'e9c70200e04abd8964c2ee29d9138013e521df4ebf1e5a8d5bdf1cb26a22f271',
    'aiweb_predicate_role_boundary_scaffold/roles.py': '0fa3632ddfd4ed448b3e9059972a1c0e2e8096a2c8184e25ba00f8e972fafdbc',
    'aiweb_predicate_role_boundary_scaffold/speech_act.py': '27c99fb8f979d6c85d3f997507389c7d6bec1292deeeb2cf4425a051058a0e58',
    'aiweb_predicate_role_boundary_scaffold/verify.py': 'f8399982635678850e37e05ad8658093de7c1da36f1ee08a13e792614d8649ef',
    'aiweb_proof_scaffold/__init__.py': 'cbdd3a9f770e0b1175cdba86be252b187c6d4251ec283fa4736536f121a075f9',
    'aiweb_proof_scaffold/receipt.py': '6c06833aa853c69fe7bf2932de3527f6c11b3fa7bb0b0943aca2dfb2f4e7072b',
    'aiweb_proof_scaffold/schema.py': 'bbbf6d3c19d7b980ea45c899b08e8a2d3f4e1a654ff9badcbdd82048d7bb737b',
    'aiweb_proof_scaffold/verify.py': '427e828e2c8e1fddf62d969724d9a4ce33e02899616d4bfead05e121a0ee35e6',
    'aiweb_requirements_traceability_scaffold/__init__.py': 'aceb069ca2fa3a64659a1194516af53c2d21c868c0f7d80b509ff7e98c793b42',
    'aiweb_requirements_traceability_scaffold/accepted_scope.py': '9d514ba10a6d02ce38d5eaa917f9a0b0826995ac7283c446615e9a53c2193727',
    'aiweb_requirements_traceability_scaffold/core.py': '1f2f1a379cec5f9672884d30f4a85ba9c21a57dc925caa6ff86415c374fc0a10',
    'aiweb_requirements_traceability_scaffold/crosswalk.py': '7b5cb5b8c90e706abd4627e90111fc6f38092d99a5bc93a97c222bb9d00fe60a',
    'aiweb_requirements_traceability_scaffold/receipt.py': 'ddfcd93dfadcfbce494514088a886e2d3d09a7e956bca48b0233d6f5eaac6eec',
    'aiweb_requirements_traceability_scaffold/requirement.py': '6748966124f49fc70469d1ccc367ba2b0111335595f452206d4c885f51df8d10',
    'aiweb_requirements_traceability_scaffold/verify.py': '10250d5cc1d42f1d7fff25c52c5e391632e0e4585955d2073284afa783bf9d45',
    'aiweb_selected_meaning_boundary_scaffold/__init__.py': 'efc526ac11f17cadc44d285d1b5519a5e842c50d2df7d540ab3bcdf96b8da20f',
    'aiweb_selected_meaning_boundary_scaffold/candidate_reference.py': '84c14c541549a84d18736a0164d184522e3d435784a648c0bb99be67ef3512ae',
    'aiweb_selected_meaning_boundary_scaffold/core.py': '020a734d71d4a7848063ea87c89eb97d3b9d0b9be1cc3871ef86c5c3f57b805c',
    'aiweb_selected_meaning_boundary_scaffold/selection_basis.py': '7ce4e6dedd72ef943a0d0eadb79dd131e1f34bfbfad06c07c1c603cb39ec8a23',
    'aiweb_selected_meaning_boundary_scaffold/selection_constraint.py': '1ee39fe4d32b06dac5aa86fd8b5c6b025ff02b52ffd7d92727fe6960bed726e1',
    'aiweb_selected_meaning_boundary_scaffold/selection_receipt.py': '6e42cb4bd9c522a82625c2b49bc9cc08380637fce7c9e60314b9a903c186e020',
    'aiweb_selected_meaning_boundary_scaffold/selection_status.py': 'abbc171cad3384f8702ad68a315e11595c95b5a75cf83ea9f2662b916031f30e',
    'aiweb_selected_meaning_boundary_scaffold/selection_trace.py': '6d4f6af404525044f8b8836b478830e098058bc0938da38f81b38ffee1a01b2a',
    'aiweb_selected_meaning_boundary_scaffold/verify.py': 'a8a9a149b17372c738550d0674d6ece6b315a19d177a70fc10e4a6670f7f2399',
    'aiweb_status_claim_scaffold/__init__.py': '5752f2b9512ec090914e35efe71d32176692d7b1a511d0e8f368102a0c48df4f',
    'aiweb_status_claim_scaffold/claims.py': '44479390f985fcf44b1e7c3de62a014d9bbeb88048c95cf006a42f1c2f8683a2',
    'aiweb_status_claim_scaffold/verify.py': '59cee168292d9545009223d51cb41112c110f83845ee69bdbdb07e8163705075',
    'aiweb_status_claim_scaffold/vocabulary.py': '94b016bca49fa4d15c2bfd0ab03f9250fce7627dea3cad42ed0466051dee86c5',
    'aiweb_verbal_cognition_gate_boundary_scaffold/__init__.py': '2dc1c350b4d44ba5f1a686f9ba730ea1ff08b98e92e53a2b925a151cea7b9273',
    'aiweb_verbal_cognition_gate_boundary_scaffold/expectancy.py': '4c6775e7a4f3eeff0646f4bf587838393b0274e3e5fb2aa33d76db9301b75073',
    'aiweb_verbal_cognition_gate_boundary_scaffold/gate_boundary.py': 'b5a8006b53dda5d9348a8602b082de65c59928a1409838c9c4a40df672a85e3a',
    'aiweb_verbal_cognition_gate_boundary_scaffold/gate_outcome.py': 'f34111b4dd4ad0c902d13a7e902fa21c6794705b94af76085e1b8743888b4cde',
    'aiweb_verbal_cognition_gate_boundary_scaffold/state_boundary.py': '94d3795def981685b422125d0b8884d26c6c481ccc36be77a4a337104e84451a',
    'aiweb_verbal_cognition_gate_boundary_scaffold/verify.py': '9e31ce8e5503fadd1a9e01835d940572323e8b55534d7af86c3c25e0c841c445',
    'config/approved_paths.json': '8f72b03b3b446d2963fcf759abdc2a938dd1007c3dfa2085cb078dc0798b2af9',
    'config/session_scope.json': '1765aa1f6f547f82ef56c2dbe6ef9759f8bf1692ebfccfff3f92e17bf88d9f35',
    'config/tool_registry.json': 'ff199fefde2a533f395ef6240e5771691e6928e2b72768c4f4aa13fc26f7cd1f',
    'main.py': '73c382c3ffe496587e4d73df46dafd08345a3e7b0d64fc05b83ecdd4eddcc557',
    'requirements.txt': 'ed73ba11243a0099034f10ac500db984959bb8f37086532f864d75a3620916c8',
    'rmc_engine_v1/__init__.py': '0b23ed0a258496bfa7b652bdb8d7807171a2d355f6f4af1ce42665186fa27f4a',
    'rmc_engine_v1/active_loop_state.py': '23fa3afe42b7d83e9d977a63c2fec476e55a862997498963b1fd39eca3ec258e',
    'rmc_engine_v1/candidate_generator.py': '2c192421215c56c1f6def166be420824448f255181aa4b2bc3c9b7d99cadd170',
    'rmc_engine_v1/chi_correction_gate.py': '432f03f8ceb1938a9964ec5963921ba36a30adc2a3811196fe433dbb5fe9f25d',
    'rmc_engine_v1/chroma_connector.py': '6554fe9188e676d4b79d4ba15f0a723574a64defc8bef4e0363ed165c83eed91',
    'rmc_engine_v1/coherence_math.py': '916591a80bd05a4a2ad1b4c4f5f01ebfb74c7f1a221ba655909c7f14a91740a2',
    'rmc_engine_v1/containment_router.py': 'ad4f7aa5708ecffb296741c3c236fb3940d6606ea7b35e0a738f0d4d328dd0ff',
    'rmc_engine_v1/correction_naming_engine.py': '84efe26af4e445eba8054547d97e7db6645e2c98524617e6418d5cd0e85bea4d',
    'rmc_engine_v1/dataset_growth.py': 'bd2cc499c5018c40186620f9dd7145cb016b52b775094b82728cba6b2252ff95',
    'rmc_engine_v1/deep_dry_run_orchestrator.py': '43e9321fff1b5b47a0466a32c8fc61dedfe7b810a0112e5733ef93762ee9b6a1',
    'rmc_engine_v1/deep_pipeline_preflight.py': 'fcc0d8671b4b8bfd36efd4ff322c5b426c5ecf5d545083964de886c48d7bf05f',
    'rmc_engine_v1/dream_state_quarantine.py': 'abda79f92c956f8160d6ac2efc9c51fa809269b9a16b0a91382ca3b895b4bae5',
    'rmc_engine_v1/drift_archive.py': '08778fb8838a344e36eee95fbc884be8ea25235d161720a948be596a11a2a8fd',
    'rmc_engine_v1/drift_engine.py': 'e9159a30a0304b97c99d41b7b4aabae444dd01bb7609936dbdcc199a6d9c9b7b',
    'rmc_engine_v1/echo_validator.py': 'c73a865119149867e4d12a8c512b6da951ea2bc1407dde12a9b1e38e3f059217',
    'rmc_engine_v1/evolutionary_drift_explorer.py': '4284d2961f0e212a397c84aacbf9ca9c8a1022752c423355b65cbe98399f4288',
    'rmc_engine_v1/frozen_legacy_boundary.py': 'e3aa9df49dd8a0ab2c2a69bb5a08fb4d070b5177651d8f1add75a5021e72805e',
    'rmc_engine_v1/general_pipeline/__init__.py': 'cf439cf633bc46c8fe7a6ab031b137d3638eeb8c3b0b26e9c5eafd7c7ea56a4c',
    'rmc_engine_v1/general_pipeline/capability_registry.py': '3ffa49ff188a47fb4a31b7ee41a33a2d4fcba4ea7250305a0d2ee5a07363fc8f',
    'rmc_engine_v1/general_pipeline/capability_services.py': '1658c07ac705f7599b1c418f98d3ac971ca77f0ae214c5ee8bac8ef1207c6b23',
    'rmc_engine_v1/general_pipeline/contracts.py': '50ec5f9a8e420c9053289cede8a99da12d011272cd012f4956079c02a0e904ec',
    'rmc_engine_v1/general_pipeline/dependency_registry.py': '98bf9ae966070aa39ea30c5b1116862f0a969c09a80d63544c2cb4248a0761d7',
    'rmc_engine_v1/general_pipeline/domains.py': '4a8632d1b4618a6511963e62076b0be30b9ecccbdb4b0c47accf2165a0a90028',
    'rmc_engine_v1/general_pipeline/domains_equations.py': 'ba7b189a0398a78b14dfbaf1f79ecd62b35cccb8bec7ebf912c0308a12bf0673',
    'rmc_engine_v1/general_pipeline/domains_wordproblems.py': '8ca3a72bd70bcc017024ce24e3d28f81881846fc808c5a0fc7c7f7dba2de86a5',
    'rmc_engine_v1/general_pipeline/echo_approval.py': '234f2b04fed5845196767d8c59e831db0350e40646c6449ebc44e992743969cf',
    'rmc_engine_v1/general_pipeline/governed_gate.py': '624c9a9c2914f118c56fe094a6f6cc25e32081e62aedaf1c211778579c1b06d8',
    'rmc_engine_v1/general_pipeline/gp002_linear_equations.py': 'f846b541a15a3955f4a8ba845698eb7781d1d43f0859ac2c8c5ef28e2c39dad7',
    'rmc_engine_v1/general_pipeline/gp003_word_problems.py': '93c62ac87066592296c9589c9ceec2a5e80a4eee5ba588df185a44a594b4a6bb',
    'rmc_engine_v1/general_pipeline/gp004_production_reground.py': '4376d7f8bdc34171304fea734ce9c71f8d7f00ef367f117fff4b4a126f8d4cd6',
    'rmc_engine_v1/general_pipeline/gp005_capability_services.py': '511e548d9d16d049d86a0eedf102ed2e028e25f5c9785d2cecdac871149d886d',
    'rmc_engine_v1/general_pipeline/gp006_dependency_license_registry.py': 'e091879da54926c4a1ca17467d2abd8d10edc785e8fbb64b6728c6a03b1aa6b4',
    'rmc_engine_v1/general_pipeline/gp007_strict_typed_ast.py': 'b5a174c0be68431726d0478667fd74b21003226bf77ef7d652520d6409f2d331',
    'rmc_engine_v1/general_pipeline/gp008_manifest_contract_v2.py': '70c9f6b8bc0c5e4e1222262f79298cf5af45f1d5b8a25561001b56360de944bf',
    'rmc_engine_v1/general_pipeline/gp009_outcome_closure.py': '337a210e0b4a19ab36b1f37e394bc882cf28f5d638498901925a47fb7d05b265',
    'rmc_engine_v1/general_pipeline/gp010b_audited_tool_activation.py': '3da3f9182a12a64da0d865a3fa7579c67b19c25471a95377c9dd5a55bd483ff6',
    'rmc_engine_v1/general_pipeline/gp010c_runtime_truth_reconciliation.py': 'f2d554e439c9c0982b26c0440d17f23dae59667d368bbd1f28df8a42dac24224',
    'rmc_engine_v1/general_pipeline/gp011b_pint_quantity_integration.py': '42bbecd405c646089150cc7cbd9f0ae6e8a1916c53fed5e7f24a8f30e967103b',
    'rmc_engine_v1/general_pipeline/gp012r1_symbolic_math_computation_capability.py': '7e857c96cccf9828bfc91bacd7fba1d8e2cf5be87d15e33f2ed629d96c4b65e8',
    'rmc_engine_v1/general_pipeline/gp013_natural_language_symbolic_math_vertical_slice.py': 'cf7768ee7813d4257546d7fb315526c65d0f99f176a4ed04e665522b5546b70b',
    'rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py': '431e6c2133a06204131f81276c11b05528ed8e6553a0d5590555ffd23ef38473',
    'rmc_engine_v1/general_pipeline/gp015_ask_forge_trace_surface.py': '9449cdac60047d6d9dd4522e0d4128b72dd86485db225c21203dfd234ba53453',
    'rmc_engine_v1/general_pipeline/manifest_builder.py': 'ea2b409b79295ba8b0f8df530deae3a8ba24c6c6acdc2fd78678151a1721e0fd',
    'rmc_engine_v1/general_pipeline/manifest_contract_v2.py': 'b78a1a55fd6e7508d34952ad7e538ebbbd09cd6669b1cc66990ca02e925d0b36',
    'rmc_engine_v1/general_pipeline/meaning_and_renderer.py': 'ccefc26a371939f00d11cb8d6dc5989ff7fcec5e696726b37e086844aeb90123',
    'rmc_engine_v1/general_pipeline/outcome_contract_v2.py': '859076e94401d7dc86d93bbd722d40bef743b3f13edf5131f85a89f4d52925d8',
    'rmc_engine_v1/general_pipeline/pipeline.py': '3c005233f92b80f497975a4c9efbfc797e084d7d759e4b72f38b5224154d8de1',
    'rmc_engine_v1/general_pipeline/quantity_adapters.py': 'ab9174e21a82be822fe61c9c1efea54913ded74a8e273672690026d21cfffa43',
    'rmc_engine_v1/general_pipeline/quantity_ast.py': '3fade71e3b7ca2fc599a63cd3ddc97810e0c4fb7171ee5c60f68b00637d83b55',
    'rmc_engine_v1/general_pipeline/quantity_runtime_attestation_gp011b.py': 'fc7019d9afcbfb7ed06407b06aba4e9967efd334faa98119b886f8ed822d0a68',
    'rmc_engine_v1/general_pipeline/runtime_truth_attestation_gp010c.py': 'c14140e98f78c3597d5981c8039493e7497a832bde3c0ebb7151243995932d02',
    'rmc_engine_v1/general_pipeline/safe_solver_adapters.py': 'afd21b1bb68aa3cadae237822cb45219275d0cef9b681cfc7029f13c6f5f30ed',
    'rmc_engine_v1/general_pipeline/source_compiler.py': '947c6f407572947c9b3af3dc1fe3b4f53c759fb4ecd26c0947dc12505f0daa6a',
    'rmc_engine_v1/general_pipeline/symbolic_math_ast.py': 'a2c5df06b202692060ee03bfcb48db7c0d4b77c65a248d271ffdcaf383a089b3',
    'rmc_engine_v1/general_pipeline/symbolic_math_kernel.py': 'fbc4ab9a9e6331d021001aa1e61b812b6746454f2ff42acfb1b34ab132c4a7c8',
    'rmc_engine_v1/general_pipeline/symbolic_math_language_compiler.py': '80d44d99192dd0ea6ffdb05429691cacb0398baaf4c4e68d8d66b81ec6a87f8e',
    'rmc_engine_v1/general_pipeline/symbolic_math_language_vertical_slice.py': '507eb69495f3e4ede7cf39e431b4fc834cd0b8d3b842ded036ef82455ef04398',
    'rmc_engine_v1/general_pipeline/symbolic_math_mea_evidence_bridge.py': '3ed8cda6e9c5bf30ce14a85d79ee4389fea916c2f892bb0f2bddbf9fd8d70bb9',
    'rmc_engine_v1/general_pipeline/symbolic_math_operator_language_realizer.py': 'f1f2486504bb987d705efee70d775c1549d3597f5153d30e87cbf11f38bedf1a',
    'rmc_engine_v1/general_pipeline/symbolic_math_rmc_delivery.py': '95efca5c30be48ec7a748a750c0245cf7b66df4f3890426dd0c61da11c58b662',
    'rmc_engine_v1/general_pipeline/symbolic_math_runtime_attestation_math001r1.py': 'd7aaf7d650a161a569bcd8e9f7263adad6b702dd9cfb985ce4b297965a0ba330',
    'rmc_engine_v1/general_pipeline/symbolic_math_worker.py': '26b8e5655ccbd5e9fdfba795d3d7bd70a8f7f46703d0b3a6392c28058abdfe1a',
    'rmc_engine_v1/general_pipeline/typed_ast.py': 'b654cf13fe4f82fa4ac483b02170e036aa93ec2b2dc1ba91664c846b6ad76a99',
    'rmc_engine_v1/ghost_loop_containment.py': 'b02145e55110164cfb450f810f7376c068c9b5da5638dd16e653ed669b595421',
    'rmc_engine_v1/glyph_renderer.py': 'c776b1cfaf9cdab9c693d93d44398453a656fef3665501cb75ae337892144619',
    'rmc_engine_v1/lexicon_audit.py': '92b7e207109eda258fc5276b1ca4cec5b93b6f8e5d16d1253b691820ad6866cc',
    'rmc_engine_v1/llm_renderer.py': '855bb683801e034487c997fd6dfeb51b8fd376f4d287fddb3e33b83bca99d2ac',
    'rmc_engine_v1/manifest_compiler.py': 'a9595bdcaa4127425d09661417de9b1b86159e174e0f41dfd4259fae837de76f',
    'rmc_engine_v1/mea/__init__.py': '1ed71fa77b0a321e7a1700d613440aa003e46d2303e7366905b9cd2d07a7699e',
    'rmc_engine_v1/mea/api_preview.py': 'a361217993d90f7c7a99417a8ee1ebc12c7e9a8de33898b5bf913740a6602161',
    'rmc_engine_v1/mea/candidate_generator.py': 'd0a3273d811df2dceba957bd4d45b3c235beb43e06a18cff3f6cde5951184576',
    'rmc_engine_v1/mea/candidate_set_gate.py': 'efd10645ecb24c9e2b7651e7c7645405320532eb663106e18bc0a7e63385df54',
    'rmc_engine_v1/mea/claim_status_classifier.py': '7911179988d4b9491289eba09efeb41c48d5c6df9195554931d072021261fd0f',
    'rmc_engine_v1/mea/coherence_extension.py': 'bd0c0c5b5a83ad7b4ede8b321b934f4eac7f165cb876eff6f43ea8eea5c8cae0',
    'rmc_engine_v1/mea/controlled_manifest_memory_writer.py': 'c1cfb92dc30a8a64243ed652e9e26fbd9059c8a0d47c23a9816c9399e26bb4a1',
    'rmc_engine_v1/mea/convergence_scorer.py': '15040c6e2305f1a3f5ba03c4a516499f429044c23361a8c9d18806ef12f26f10',
    'rmc_engine_v1/mea/discovery_kernel.py': '1c0ca7acabfb487e468bc9c6f3c05e24637d698ebd3fa7d17f819a7a9f7cb61f',
    'rmc_engine_v1/mea/evidence_tier_contract.py': 'c3028845bfa1a523ff2dcfcf15112a1870c1731cedb8e90c5e29b8266db6ab63',
    'rmc_engine_v1/mea/fbsc_operator_crosswalk.py': '92c4eddd11e5b16c0aa74901e648bda1e963c222ca34464254dbcf0c01158e8e',
    'rmc_engine_v1/mea/fixed_point_math_contract.py': '39432cb5c4f3afc1905bfd5f7e2f8bdf9b51cab7c464ddf3a52def69e767c45d',
    'rmc_engine_v1/mea/gate_engine.py': '921386afc79ebcf5dc7c9d8919505bf88bb589cf70a03bf9428e5c4e31a17388',
    'rmc_engine_v1/mea/goal_ancestry_scorer.py': '69ff5d77c94fd59091b9f9e5a6651ecaa4a6761ff31d27abb39e5f66ffc83c38',
    'rmc_engine_v1/mea/hard_gate_report.py': 'fe50328a4dfb30c02a5dec6a4c75de0693dd22d3f42e7c8244b18a1e5ef743fb',
    'rmc_engine_v1/mea/information_gain_scorer.py': 'a0189016e554a093c447883022b5cedb93513d01e95f6b978fe089b5cb97a29d',
    'rmc_engine_v1/mea/live_candidates.py': 'e76dfb8135a6fa417de4900dd62e7664a6fb3898e9ae77be0de22795d86fcbdb',
    'rmc_engine_v1/mea/live_term_binding.py': 'e98b0026b2739e6aae0d3afb00281e24a7668574da8e7bd6b00e0edefac0194e',
    'rmc_engine_v1/mea/live_trace_replay.py': 'def2664739451118e666fb440097c3f4e1d5fa0304eb64e86d81f096db36b5c0',
    'rmc_engine_v1/mea/manifest_advance_preview.py': 'c28ada958545906619f17ff127bc89fa6afb814dd2ea4faa8d506c9ab1a19da8',
    'rmc_engine_v1/mea/manifest_memory_writer.py': 'd33a4fa890ffbbe4b07c08a58b66b6c97dbec5212df3ab11069e21fa66a108fb',
    'rmc_engine_v1/mea/manifest_schema.py': 'cad187e92a27edd6acfeea3013dd175da9304e2ab3ff22f0c20bb3e88cd350c8',
    'rmc_engine_v1/mea/math_conformance.py': 'e7b02d1b78a8c779fef3220b445dbba6b6ad66b0fbcaca24936667cd23885966',
    'rmc_engine_v1/mea/measured_seal_gate.py': '7356c75af04173bd0bc2b0922a306bed8c1a82bab35fb638715d942b6ca4017c',
    'rmc_engine_v1/mea/operator_cost_scorer.py': 'bbeba976eec2d5e14cb67b579da28d4fa8bd7a26ef563857d82e1b06d252d9bf',
    'rmc_engine_v1/mea/operator_engine.py': '3652179cf66282f2aab261e93ff1f238e3ee11852481b843e0fcdf204e025b2c',
    'rmc_engine_v1/mea/operator_registry.py': 'b779c1d75ae16bb64986d9cdfb4b25d09de82eaf8704f02a6fe048a13131c74d',
    'rmc_engine_v1/mea/problem_manifest_store.py': '8f31187258fcbc0dab848d3edd6dd3889106747ab84972d54bf9f068d36083e7',
    'rmc_engine_v1/mea/proof_debt_scorer.py': '5788421753641f406fe6bc4f7209aa229d6cd3f73f8048d151c6ecedc809521c',
    'rmc_engine_v1/mea/replay_engine.py': '09dde2b1812a7b9c0b8981afdaeb0c4da7493c4ab99edef58272deafcd3b271e',
    'rmc_engine_v1/mea/seal_candidate_gate.py': '9415c5bb0593694e875943d004666352657428a7574d10000fbd057ba7634b3c',
    'rmc_engine_v1/mea/seal_engine.py': '9d09f3e9f7bf012e023412fa2d8ab4d9d8288b8cf7922bd5c5eed67bcabe56ef',
    'rmc_engine_v1/mea/seal_packet_audit_chain.py': 'b294fd9bb0fc6272744c8e03513f4be9f94e30e1584677204ffb7b54f045c4ce',
    'rmc_engine_v1/mea/seal_packet_preview.py': 'e96235f3f954c18450a902971d1372b5c96631aeac3c1ebdd2725b26a614d1b7',
    'rmc_engine_v1/mea/seal_readiness.py': '554f70a6b4d1f78449f22039f1378510c9c197ab9549a0f9df99227b912c8c79',
    'rmc_engine_v1/mea/seal_transaction_commit.py': '473ab9a10262e43bad76934d5015ce34c13eb9fd2bd50a152f7354e38a253e7a',
    'rmc_engine_v1/mea/seal_transaction_preflight.py': '87ce6d5b5238e847c6114777eeb4f8f61c94cf3ff11dfc7371ada813c9b4b371',
    'rmc_engine_v1/mea/seed_manifest_gate.py': 'f7e58422a625bf65dd913a22777599344d29b36ccc05eb2d7be161cac2dd60e1',
    'rmc_engine_v1/mea/unknown_detector.py': 'c516541acae0a9a802e6bb190f0acc1592971f2d2d9e9d0e9130592d42faaf77',
    'rmc_engine_v1/measurement_kernel.py': 'f55e3525b0b14c0715da3c359f5a949c9a9712511ece99fc84c31ce739db147d',
    'rmc_engine_v1/memory_recaller.py': 'e987c3f958c8508fc81111dd74c91bb62c5550cb3965d376386ccca4a6a497ee',
    'rmc_engine_v1/memory_writer.py': '6e9a7feb90394803ea43fc23850cbeb85d20e058ea8d6478aa7ed2a82c63ad07',
    'rmc_engine_v1/output_renderer.py': '276dbbc71bd642508003935fc83a8e538e317fb216b3ce1a098984536f332054',
    'rmc_engine_v1/phase_codex.py': '1611809e7bc4f6cd6b9ad6d4202e497994e920ed9d3b5b434e3fbabc02448606',
    'rmc_engine_v1/phase_parser.py': 'dd83c0902bd2a162399db5b7f685f718a697492299eba6af5cf4c8dc86cfc45a',
    'rmc_engine_v1/promotion_path.py': '87d6bd1ac29e87cd80921f75757e89677b4f861acf165218a55bc6d728d3a418',
    'rmc_engine_v1/protoforge2_drift_connector.py': 'ece9fb26f98ef22b5a40ca19364baee5e414126e868e3b6505b810a15a01a34a',
    'rmc_engine_v1/reference/README_fbsc_phase_codex_binding_v2_5.md': 'b30ec6347970dd7d1f24de5558b14ace6767ea236c41c7b0ab1bd825ce4507ad',
    'rmc_engine_v1/reference/README_rmc_resonance_reference_v1.md': 'a8b67fd8a936b5c7ddcd84058129aecb9ddfa1491b1dcd6862e8e3d9d0563df2',
    'rmc_engine_v1/reference/gold_reference_v1.jsonl': '6471e19fa1dd80e84a9e13d7ecbf0ea1c0268247f00583ad4cd96e13b0dc2e64',
    'rmc_engine_v1/reference/letter_phase_map_v1.json': '1f2b031b79de2d5f15ce8e22bbc7dfbfede47756c4270d6859c2436b24508b6a',
    'rmc_engine_v1/reference/operator_phrase_lexicon_v1.jsonl': '1e7141a6ff52183b5d37562575e7e75746a96cdb59291262f326a1bb817f9ad7',
    'rmc_engine_v1/reference/phase_codex_v2_5.json': '9a2911801667d90906a8bb3337158293c074a61799bba0c40f1e1c22e42ec046',
    'rmc_engine_v1/reference/phase_cold_storage_forms_v2_5.json': 'fa39fd13ea375c44ebd5c9fd9b72a4087ecbbad15446a36fbffa2eef79778e3f',
    'rmc_engine_v1/reference/phase_color_map_v2_5.json': '8a6f6c76e66758f1938f7f95fb7d0d0873798e0b010aa9d7f8773cd604778d64',
    'rmc_engine_v1/reference/phase_drift_flags_v2_5.json': '137f0081bc91c198ef134022c1d9fd9b21b9d058c3ebba2b2dbf725adccd3086',
    'rmc_engine_v1/reference/phase_motion_map_v2_5.json': '667cd28fc2a51b362d036706ab6de9160a609169a3aa97fc07570c53ee2ca508',
    'rmc_engine_v1/reference/phase_runtime_hooks_v2_5.json': '3fa33f92d6fb137f3338b7b21c4c037ae7cfa94537e7584d59a25c691329848a',
    'rmc_engine_v1/reference/scripture_phase_archetypes_v1.jsonl': 'b49cf62c4058370ae19c5c4b7e0b3d309b91c8971de33bcba34b988bb0ad2537',
    'rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json': 'e99c7691d0ba951343bdf80a82d65d19e464b660bedd942b9a9db2b16283c93e',
    'rmc_engine_v1/reference/syntactic_firewall_examples_v1.jsonl': '5561501360b4ee93ae7766d69a35920883f325b3eccf76c7f9bc10d56a55b0fb',
    'rmc_engine_v1/reference/transition_law_examples_v1.jsonl': '038d5f1a124b44836189f850de372c883faca80157269e1c734638d11e427d52',
    'rmc_engine_v1/reference/word_loop_seed_lexicon_v1.jsonl': '7b2ae9c93595ca8623c2ab184ef4823040ab30f5d1c07d2153a2595f6fcc126d',
    'rmc_engine_v1/renderer/__init__.py': '5180f661ea8cf6114ed0a34231f3b2c7b8b2adb541f158d49d176819abd01e11',
    'rmc_engine_v1/renderer/echo_validator.py': '7c4ce7ac275ab6daf15ee8c4c507aac445c1b1f8f9fd19881cc883b4add83020',
    'rmc_engine_v1/renderer/grammar_templates.py': '60ac849d8f479561eb9b0cf444e7300134f29c71e5be2fccb7e3444be121a454',
    'rmc_engine_v1/renderer/mea_render_gate.py': 'b6ce41e64749c0a510f44dd5f3200c170e7750a5f16279c11b7a71a440f6c479',
    'rmc_engine_v1/renderer/renderer.py': '8699695680fa53a5d06e8952bb67ca77a82ac38d87eba6564967435246406d63',
    'rmc_engine_v1/renderer/semantic_lexicon.py': '23046149eae51dfa61744d25d04e6911b9968b0d1775d10a5bc40482de6856d0',
    'rmc_engine_v1/renderer/surface_realizer.py': 'bee1a6948cae343c6afe4d99c9a6fc6a72c673fbecbdfe966ce1b499c4429296',
    'rmc_engine_v1/resonance_lexicon.py': '07f477d97b434b673b86f894b0a538ae1d3d6dd09ad9f277eb94c1371db6c30d',
    'rmc_engine_v1/resurrection_engine.py': 'f6543c1ad5b2539ca2d0902ab73a5b5d44e815d0c1a9798c782d6f0e5fe41fec',
    'rmc_engine_v1/rmc_pipeline.py': '308e8db2744413ce7f9d8a7b94e72d933667522f3d00af302c0c3969b6db9823',
    'rmc_engine_v1/spc_cold_storage.py': 'd257a6346b5345a556d70baa71a5ff2b24dd8f650e38d1884d43975043cbeb97',
    'scripts/CE_CONTROLLED_EVENT_BUILD004_DELIVERY_MANIFEST.json': 'b2c2066c4ec3bb74bef45fb748d204e345badc5d7d80d9103038a36407ba283a',
    'scripts/MEA_GENERAL_PIPELINE_BUILD_GP001_DELIVERY_MANIFEST.json': '55ad19ee98626b3968d2cbd34b942ffcaca9e8c89ae41de2d20ebb1a65bb3078',
    'scripts/MEA_GENERAL_PIPELINE_BUILD_GP002_DELIVERY_MANIFEST.json': '8f6f88983fb96e681a54ab79fc42efb3a036da8188a714794d04aab4b574cf9e',
    'scripts/MEA_GENERAL_PIPELINE_BUILD_GP003_DELIVERY_MANIFEST.json': 'd1e42d8056bba299a24117f0106dccc5cea73b53546ca7422ec56c8b2ead22a8',
    'scripts/MEA_GENERAL_PIPELINE_BUILD_GP004_DELIVERY_MANIFEST.json': '56859d32ec74ba06fa7c1cd957dd6e3254c3843b457f66af7393f3900e13263e',
    'scripts/MEA_GENERAL_PIPELINE_BUILD_GP005_DELIVERY_MANIFEST.json': 'b19b69133dbd81cd240aaa1313f2c306cb8a02c6e6f1115be47a46832fb2f0e3',
    'scripts/MEA_GENERAL_PIPELINE_BUILD_GP006_DELIVERY_MANIFEST.json': '267b3147e62a8ecd134350da7c61eae162bc5eca880c31e8fce23422ff5e2ed9',
    'scripts/MEA_GENERAL_PIPELINE_BUILD_GP007_DELIVERY_MANIFEST.json': 'f012438c9e935497da2ae8aaffe4c756faff4e76329cbcf641bef393fdaa0496',
    'scripts/MEA_GENERAL_PIPELINE_BUILD_GP008_DELIVERY_MANIFEST.json': 'b06d9e10de0a474c85f42d3fc0fbc9550d5d37c5812b18fd0fe063b48e88c210',
    'scripts/MEA_GENERAL_PIPELINE_BUILD_GP009_DELIVERY_MANIFEST.json': '7eb7b35fcef2b6a4365afd15ef53d4b7a013d99a0cb7097fa4ed7907456bdece',
    'scripts/MEA_GENERAL_PIPELINE_BUILD_GP010B_R1_DELIVERY_MANIFEST.json': '907b255666c5d29b435e50ed52b7df476365066efae065513027913b188142c6',
    'scripts/MEA_GENERAL_PIPELINE_BUILD_GP010C_DELIVERY_MANIFEST.json': 'f88bb090bb882914db3e837871a8177a5d7c76cc30351a37184339d17c45a8eb',
    'scripts/MEA_GENERAL_PIPELINE_BUILD_GP011B_DELIVERY_MANIFEST.json': '9d1ac938739ddf1faa6031f4d6e2f504dd2151aa93ddc235a8f6151fa0727398',
    'scripts/MEA_GP015_ASK_FORGE_OUTPUT_LIVE_MATH_TRACE_SURFACE_DELIVERY_MANIFEST.json': '56032be5744ba53c81438ff8fc8bf4fe5fb4e4c9ccbd4e9fc827b94d256273ef',
    'scripts/MEA_LIVE_TERM_BINDING_BUILD007_DELIVERY_MANIFEST.json': 'd5662a8915d531993bc7062749497632eeb6768902a03d892f08254f5faaac2e',
    'scripts/MEA_MATHEMATICS_SYMBOLIC_COMPUTATION_KERNEL_BUILD_MATH001R1_GP012R1_DELIVERY_MANIFEST.json': '97961de730bf39b437bd00463ed5d75a7efd48f5bd9e25f0e255c23e0bdd7988',
    'scripts/MEA_MATH_CONFORMANCE_BUILD006_DELIVERY_MANIFEST.json': '9a845ad17e1611c367ec69f584031a9af9d6b07d8581844cba45b0e56d8d5b68',
    'scripts/MEA_NATURAL_LANGUAGE_SYMBOLIC_MATH_VERTICAL_SLICE_BUILD_NLMATH001_GP013_DELIVERY_MANIFEST.json': '5237562158a07fe70e8b8ff45bf9d97bdee010b910520a0ea6ab445afc76a8a1',
    'scripts/MEA_NON_LLM_RENDERER_LEXICON_BUILD009_DELIVERY_MANIFEST.json': '982f9ec8fd425864f9a3cba0cb73a8db36aba7280e7421acb9ce80c5a49c21b0',
    'scripts/MEA_OPERATOR_GUIDED_LANGUAGE_REALIZER_BUILD_LANGEXPR001_GP014_DELIVERY_MANIFEST.json': '68b1406de16799d8a0bb97769df4e448ba9e94f549b0c61fc907f79d3741de78',
    'scripts/MEA_RENDER_GATE_BUILD008_DELIVERY_MANIFEST.json': 'f7597110a15092d38715c3f43a7261eda561e2a36ef692d4941f6fbcdfa67a26',
    'scripts/MEA_RMC_MEMORY_WRITER_BUILD005_DELIVERY_MANIFEST.json': '9394a8be6b8ba161a0697e7a2abe2ee759ca4266d2deb4cbfdcd3c660536cbd1',
    'scripts/README_aiweb_frozen_legacy_callsite_containment.md': '137a5b6378033ae4fe6b702b32318df065ffa8d6bbd2b4c753eb13be4de562af',
    'scripts/README_aiweb_slice01_proof_scaffold.md': '2d96734fd18d04d673389e5d540328d92ce082eb8057e7cebe5d1a96e66e8c09',
    'scripts/README_aiweb_slice02_gp014_regression_scaffold.md': '7fd6d10f0f73808807ab921d6f28dd6a8942a23cdea88bacde7d33c29ced53cb',
    'scripts/README_aiweb_slice03_status_claim_scaffold.md': '222e4a4bc9d64beba99d70d4d251d411203e523ff0d8e03b0bb25704c6caa72d',
    'scripts/README_aiweb_slice04_decision_baseline_scaffold.md': 'f97ecdab690bec04635522ac30cf21a95efea728cbebac209cf853a01f9b17c6',
    'scripts/README_aiweb_slice05_implementation_ledger_scaffold.md': 'df10408c0069ac7a634bb7c0da44885f6f805ae559fe93de3c1f7a5d23f4be75',
    'scripts/README_aiweb_slice06_authority_scanner_scaffold.md': '31c2a3a7d8a32f644230dd2f3a519904975d7251f85e44d08e62ba7e32daf16c',
    'scripts/README_aiweb_slice07_meaning_law_trace_scaffold.md': 'a3486fda50b52237eb26001e9b895131e2be316e8524655f3c114165aab1cebf',
    'scripts/README_aiweb_slice08_concept_boundary_scaffold.md': '9ece14c064b3c95daf82fee35e5ae13ac5d7557728e86049e59e35a9c810fd83',
    'scripts/README_aiweb_slice09_predicate_role_boundary_scaffold.md': '7a9b0114963457c27480698caa452e004c67ace813d0bf965b7acb9ca96af55c',
    'scripts/README_aiweb_slice10_verbal_cognition_gate_boundary_scaffold.md': '08364de822ff9e9bf678477b94e3dd4996947e35c37be9fc89edb983db27a88d',
    'scripts/README_aiweb_slice11_candidate_meaning_boundary_scaffold.md': 'da6582892a85e0b55cd8fdf0d5504eadc8de19f0b1c51b8771b5c56aa14d0537',
    'scripts/README_aiweb_slice12_ambiguity_clarification_boundary_scaffold.md': '0e39168c6d210130ae490272a0f6b77e3fb76ce615fbb4010d41c9148c329e06',
    'scripts/README_aiweb_slice13_requirements_traceability_scaffold.md': '48e6fe0d687f908a649068326b748b6e1ab15054224aa938b0f3102d47c0f587',
    'scripts/README_aiweb_slice14_external_resource_quarantine_scaffold.md': 'd136a5fb08fe9335aed37fbb9f3ae4ca1cae70d43fa13c6be60585bbb2a44d65',
    'scripts/README_aiweb_slice15_corpus_evidence_memory_trace_scaffold.md': '92166ac0e1909cff025fa2d4b533e0be596036fd0368ec371213d7c45a85c0c8',
    'scripts/README_aiweb_slice16_selected_meaning_boundary_scaffold.md': '56895d5255f7329be26a0bd4fa4a5ba675af9371785d97bd400458ccff3646f8',
    'scripts/README_echo_validator_hardening_build010.md': '04fec6c95bb647979bd68a8748454090eec1bb42d2a7fe2f329d9eb2678c3f1d',
    'scripts/README_general_pipeline_manifest_contract_v2_build_gp008.md': 'fd7965ee8c469059c0f37b4ec20722e7fb6cd7f1351907fa9f801714c0403d2c',
    'scripts/README_gp015_ask_forge_output_live_math_trace_surface.md': '52046ac7e59a772555fbe59da9d73aca419bf1ad3b98012583630006b0434ff3',
    'scripts/README_mea_render_gate_build008.md': '214a465b53ee632891b864fe6ed15d8582153721a669f2c28fbe19097f51441f',
    'scripts/README_non_llm_renderer_lexicon_build009.md': '678cd62f79214e59323b5be82574f975473b7c1f12ff292cbd43920b6381020b',
    'scripts/README_operator_guided_language_realizer_build_langexpr001_gp014.md': '761ec14f6d7390ee8c91d44f82bc30e7d5c8451e7e8d7c40e2e1c57730d8918a',
    'scripts/README_patch262D1_resonance_output_gate_json_scope_hotfix.md': '881f8f01bc07dff62b8a009c18cb95ea9cc4aa8b6a72632bbddc7f212c27e0cb',
    'scripts/README_patch262D_resonance_output_gate.md': 'aaf4525429a950a19be207f91ed1b52de8c398c1cdbb8d4c1bb971e675c64e85',
    'scripts/README_patch262J_rmc_manifest_compiler.md': '441405b85ebd8bcb05244ecc05ada5adbe88079b44b63b77233ec6c8a5df0968',
    'scripts/RMC_MEA_ECHO_VALIDATOR_BUILD010_DELIVERY_MANIFEST.json': '45fd7fe27a261a7f7be68e133b742fd477c99e711c97a07ca039ff6a011c0863',
    'scripts/SHA256SUMS_echo_validator_hardening_build010.txt': '6d7e984546a6c89e0d4543982c0076a2830f679cd8dddf702a14846c29879ee5',
    'scripts/SHA256SUMS_mea_render_gate_build008.txt': 'df61184351d4db92cce50ecca786a966286f344266810500515ae946db8d7e54',
    'scripts/SHA256SUMS_non_llm_renderer_lexicon_build009.txt': 'eb72a7e7b79c676fb157c506a3c50b1cb96982321a3d96aed109931d2c68436d',
    'scripts/aiweb_frozen_legacy_callsite_containment_verify.py': 'a2e7cd488361acefc5fc9c00337f9a0aa2961df4ef5576d43b03457f14974dab',
    'scripts/aiweb_slice01_proof_scaffold_verify.py': '760a75e29b7a17097a49dbe7fb5cd64f0eddd8a6db7c5bde845a7273195a1536',
    'scripts/aiweb_slice02_gp014_regression_verify.py': '50e1721263004c077e49359e2a15017382545eeb2e88a98515a0c6b216828acc',
    'scripts/aiweb_slice03_status_claim_verify.py': '1b83d6129c15b57c6701f2d26a0028fba1be49cabd4e3b975fb85f14aaddc28e',
    'scripts/aiweb_slice04_decision_baseline_verify.py': '22ec58b03ec4ed83bd7152db8328085029c659b6b8583c5c55fbe70a0720370b',
    'scripts/aiweb_slice05_implementation_ledger_verify.py': '29491f54727fb3b026f45b5c4230305046cc3d75950e402193734a9be01c02d9',
    'scripts/aiweb_slice06_authority_scanner_verify.py': 'b645b34a4171e5c63f999be85c9c7946a88b8f1a555751018556e75a724fcd27',
    'scripts/aiweb_slice07_meaning_law_trace_verify.py': 'ff47c19fba5106e6599b83442c566431f1da59b0714aebba88b52e9ec94fcbd1',
    'scripts/aiweb_slice08_concept_boundary_verify.py': '28a22ca634f4282ac79b2f39837a8d7d49d8f8be444d803a75d5143a36b79b61',
    'scripts/aiweb_slice09_predicate_role_verify.py': '13198416ea168a9b75aa7e0d0fcea3d73589c448a1c663810483d8b376cbc9e9',
    'scripts/aiweb_slice10_verbal_cognition_gate_verify.py': '10cfaa0b1d4fc8f37b32cd09d0ebb3839828d54e610ffdbbd0e293ae2765e0b1',
    'scripts/aiweb_slice11_candidate_meaning_verify.py': 'ec5c5f6bcb4bf94f72a4f0ae4b41cbf44cd3e3efb0abe5481e06d55f68d9aed8',
    'scripts/aiweb_slice12_ambiguity_clarification_verify.py': '7bfdf92530b6d852033346e812846f3ad3f788830f44fbbd43065ea3b26a4221',
    'scripts/aiweb_slice13_requirements_traceability_verify.py': 'ce87391aac340fed9fcdae68e2f8b92a1c1b9dc8a2c3098ce86ef4ce1b267a3b',
    'scripts/aiweb_slice14_external_resource_quarantine_verify.py': '059fc880016f631b628ac812c54c7be791ba07eed2a19e01fbc5a94ef0e54580',
    'scripts/aiweb_slice15_corpus_evidence_memory_trace_verify.py': '96802bf07b0e50d29692964bc54898ddd4a9bd5a8e36313487c3893b62e91154',
    'scripts/aiweb_slice16_selected_meaning_boundary_verify.py': '3e6e6e91f5872d233fac744b0a952a45baecc4fcd87106fb9acdafe7d08e8ef2',
    'scripts/echo_validator_hardening_build010_verify.py': '62279d07938f41092b84c1f61908d048486b3a024389724c2fcd7f76d54a0984',
    'scripts/general_pipeline_manifest_contract_v2_build_gp008_verify.py': 'c017589a9eb03c56f7d68d9cfe79fb3ad5099c39c13ac126f4c732f5a9c21f03',
    'scripts/gp015_ask_forge_output_live_math_trace_surface_verify.py': '7cd35a004493ae56971a94551ad50d78fb927c6006fe2ad30aae35bbd99c269e',
    'scripts/mea_render_gate_build008_verify.py': '6837af2d66450205e500fe30b5aec79b2aa550257f9c86f144a0f01476a4180a',
    'scripts/non_llm_renderer_lexicon_build009_verify.py': '003371946c65fbfb2ff2018d808146d6da58aaeeac405ba9bbba6d3a244f82af',
    'scripts/operator_guided_language_realizer_build_langexpr001_gp014_verify.py': 'c84800156011727cd49f743b722502c60f555c109859ff79aa399cb32ae4d797',
    'scripts/patch253_forge_output_panel_api_verify.py': 'ba0d68678bc22735c2f70e4a9d076dafb2268354abce402c5f9f80523793aeaa',
    'scripts/patch262D1_resonance_output_gate_json_scope_hotfix_verify.py': '9d77b5f1bf9e0891026b07ec07e0a9ce96941368a52968384378ba563359801f',
    'scripts/patch262D_resonance_output_gate_verify.py': '4577e557093fd1e397742dce469c493ceffed6d4fa2c2ef623723f0debab4f95',
    'scripts/patch262J_rmc_manifest_compiler_verify.py': 'cdb8571c47a9e6cf61ae4f8e35932728dc632c54ae27468b809b828d59a0ffe4',
    'scripts/test_aiweb_frozen_legacy_callsite_containment.py': 'b86e2404d7e3020bddb62fb9bf0249871b8a5dc04cee6bb5a01255004c20d43a',
    'scripts/test_aiweb_slice01_proof_scaffold.py': '1501d25b37db6866d9ec51b312b2010c57255c95b5e945d39ce99dd61630b355',
    'scripts/test_aiweb_slice02_gp014_regression_scaffold.py': '9b639a84890ec0019f2d4dc5500050a496fcccdc3af3ac8a279a88b031ad460f',
    'scripts/test_aiweb_slice03_status_claim_scaffold.py': '4f39c14f9bc603d28a558e55707c73839b7f5071959b8a2214bad5efe243b91b',
    'scripts/test_aiweb_slice04_decision_baseline_scaffold.py': '0cdde94b0b08925b2fac0b78b730a634f60ab2b8e8c146b326b05476149b49d6',
    'scripts/test_aiweb_slice05_implementation_ledger_scaffold.py': 'ffd3010a8daf6f78c36746eac98a71c660eb8c54534ba1f1909f3fde127d8970',
    'scripts/test_aiweb_slice06_authority_scanner_scaffold.py': '90ab49e7a7afc4c10da8241b8648f2c692c44ecfb01b322c67c01d259410b1aa',
    'scripts/test_aiweb_slice07_meaning_law_trace_scaffold.py': 'd0d4dbb4a97b6c53da8e9e1f43cdf8206488d6e9e025b12b78d380531f0b2731',
    'scripts/test_aiweb_slice08_concept_boundary_scaffold.py': 'b1f68803d322d6bd4a4fbb951b9571aaec37342eae93d00efc57b4d82f61101a',
    'scripts/test_aiweb_slice09_predicate_role_boundary_scaffold.py': '9280be2edfd2c63ea5d07b1998ebc82905e5821a7e9e812f809f6fd2fa975524',
    'scripts/test_aiweb_slice10_verbal_cognition_gate_boundary_scaffold.py': 'cfbc233805f9d8fd79fd9178fb7edeaaea8693791371909739eb550b9efdf045',
    'scripts/test_aiweb_slice11_candidate_meaning_boundary_scaffold.py': 'd5aa38f5527799929c688a9a1ec4718bbc4fbc0f55ac188f734d89592f1cefc3',
    'scripts/test_aiweb_slice12_ambiguity_clarification_boundary_scaffold.py': '48fee59e6bbd3cf07bfc0d8eb0ae463f12a7293aaf66314896ad19ae073b8978',
    'scripts/test_aiweb_slice13_requirements_traceability_scaffold.py': 'c333be0f82bbbf7f72faf552dc6d6e98aea692d33cec90534e2ac3a51e5834d4',
    'scripts/test_aiweb_slice14_external_resource_quarantine_scaffold.py': 'c70ae4c840870883393d26b525987fca7a486710485e12ffe65515cda0f1f02c',
    'scripts/test_aiweb_slice15_corpus_evidence_memory_trace_scaffold.py': 'e4857e5cd3177a4659525438653db956dcdf6b028c7bc878549d5f3e799cc6c8',
    'scripts/test_aiweb_slice16_selected_meaning_boundary_scaffold.py': 'e4e77562683c14a3fb2ba189d90ece83903030000e5d051c0a7d1a46d9785f95',
    'scripts/test_echo_validator_hardening_build010.py': '422f8bcf2463676c0781d84b72f5fa79dc6afb1835079d84ad89fdc5ebf54967',
    'scripts/test_general_pipeline_manifest_contract_v2_build_gp008.py': '689b9eef4b36d2720d0a314a2a94fb2b745d1564fc321b9dc1faf841ff78abee',
    'scripts/test_gp015_ask_forge_output_live_math_trace_surface.py': '6bb1816718eb2854d2ee8cfc2bde24c21ea117b879b24c4ac1b2189f90c99600',
    'scripts/test_mea_render_gate_build008.py': '385306cadfba5be82a7c9138a2333b11cb9dd46ecd07b12dffddc172f459a1ee',
    'scripts/test_non_llm_renderer_lexicon_build009.py': '9880e5759fb9b4211e3fb1c31becd3c26eb73da2e5753204982ce8a9f2e39988',
    'scripts/test_operator_guided_language_realizer_build_langexpr001_gp014.py': 'd047b3ca07c13e4e29ab55f9aa8fb357ee87a1a7d649ea2b23f68f30b75af3be',
    'scripts/test_patch274_build_manifest_and_terminus.py': '5f51a6cf18c22c47c332fe776ca88587059ef15473ec0385bb1342f4316a8563',
    'scripts/test_patch281_mea_seed_manifest_gate.py': '79fc619b5b723d093ca4294cc93f803ab4a38a0b50fe7518541fc10322bc78db',
    'scripts/test_patch293_mea_manifest_advance_preview.py': 'e9ffcb87b590dd8fb01daf2627a7b60fe183de8427587655a58d5d6d575c8704',
    'scripts/test_patch294_mea_problem_manifest_store.py': '504919089975fc41c8eacabe96be9234e3c1c2afdab5c4962349b0e022b272a9',
    'scripts/test_patch299_mea_manifest_memory_writer_dry_run.py': '3be049501e4b004dfe5b1fa811a803573bde0b34bd6259fbd6f94aa76e932d47',
    'scripts/test_rmc_dataset_growth_route_refusals_B5R.py': '0984902f1c76ae1d30b7b608b7db334595c9989922e1830fdafa3edef34c3ddc',
    'scripts/test_rmc_echo_validator_C6.py': '2b9c6a71af08da2e3b1a87e8bfbaa997d5352339ca987890b82706fe25abc450',
    'scripts/test_rmc_glyph_renderer_C14.py': '4c497b2414fbcc353b4bf101d8ad0d149a9168e51d75d538ed56f70d7d57a006',
    'scripts/test_rmc_llm_renderer_C16.py': '17488ae7b7755544b6b31926ba88a9e064ed2a0109f9c3c3434e91fb74c7a269',
    'scripts/test_rmc_manifest_compiler_C4.py': '56ace53279c738392de6d78d25d42d3990667d091212b7312a8fdd686bddbbe9',
    'scripts/test_rmc_output_renderer_C5.py': '0720337844f841ae884f7dde4b12c15faad6c2a6e97f5daddb7f491151a167d8',
    'scripts/test_rmc_route_manifest_RewireUI_R1.py': 'b014c5af5b16874b74c6d9e19018b82ed11bdc5688b11ed1a28fb074c5a93998',
}
FORBIDDEN_IMPORT_PREFIXES = (
    "rmc_engine_v1.output_renderer",
    "rmc_engine_v1.renderer",
    "rmc_engine_v1.llm_renderer",
    "rmc_engine_v1.chroma_connector",
    "rmc_engine_v1.general_pipeline.gp014_operator_guided_language_realizer",
    "rmc_engine_v1.general_pipeline.symbolic_math_operator_language_realizer",
    "rmc_engine_v1.general_pipeline.gp015_ask_forge_trace_surface",
    "openai",
    "chromadb",
    "requests",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(label: str, condition: bool, failures: list[str], passes: list[str]) -> None:
    (passes if condition else failures).append(label)


def _add_repo_to_path(repo: Path) -> None:
    text = str(repo)
    if text not in sys.path:
        sys.path.insert(0, text)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: aiweb_slice17_output_expression_boundary_verify.py /home/nic/forge")
        return 2
    repo = Path(sys.argv[1]).resolve()
    _add_repo_to_path(repo)
    passes: list[str] = []
    failures: list[str] = []

    for rel in ALLOWED_NEW_PATHS:
        check(f"required new path exists: {rel}", (repo / rel).is_file(), failures, passes)

    for rel, expected in PROTECTED_HASHES.items():
        path = repo / rel
        check(f"protected path exists: {rel}", path.is_file(), failures, passes)
        if path.is_file():
            check(f"protected hash unchanged: {rel}", sha256(path) == expected, failures, passes)

    for rel in ALLOWED_NEW_PATHS:
        if not rel.endswith(".py"):
            continue
        path = repo / rel
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            passes.append(f"Python syntax valid: {rel}")
        except Exception as exc:
            failures.append(f"Python syntax invalid: {rel}: {exc}")
            continue
        for node in ast.walk(tree):
            module = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(FORBIDDEN_IMPORT_PREFIXES):
                        failures.append(f"forbidden import in {rel}: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith(FORBIDDEN_IMPORT_PREFIXES):
                    failures.append(f"forbidden import in {rel}: {module}")
    if not any(item.startswith("forbidden import") for item in failures):
        passes.append("no forbidden renderer, GP-014, GP-015, frozen, model, or retrieval imports")

    from aiweb_output_expression_boundary_scaffold.verify import run_verification
    behavior_passes, behavior_failures = run_verification(repo)
    passes.extend(f"behavior: {item}" for item in behavior_passes)
    failures.extend(f"behavior: {item}" for item in behavior_failures)

    print("=" * 72)
    print("AIWEB SLICE 17 OUTPUT / EXPRESSION BOUNDARY SCAFFOLD VERIFIER")
    print("=" * 72)
    print(f"Target repo: {repo}")
    print(f"Expected base HEAD before application: {EXPECTED_BASE_HEAD}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")
    if failures:
        print("VERDICT: FAIL - Slice 17 verifier failed within boundary scope")
        return 1
    print("VERDICT: PASS - Slice 17 verifier passed within boundary scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
