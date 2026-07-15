"""Immutable Slice 34 containment and regression proof policy.

This module is data-only. It grants no runtime, memory, evidence, resource,
network, delivery, tool, action, release, or production authority.
"""

from __future__ import annotations

from typing import Final, NamedTuple

SLICE34_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-bootstrap-regression-containment-v1"
)
SLICE34_TITLE: Final[str] = "Bootstrap Regression and Containment Acceptance"
SLICE34_PARENT_HEAD: Final[str] = "ad0129543ff23b16f6de9008b091a8f97892486d"
SLICE34_PARENT_SUBJECT: Final[str] = (
    "Slice 33 deterministic trace and receipt assembly"
)
SLICE34_COMMIT_SUBJECT: Final[str] = (
    "Slice 34 bootstrap regression and containment acceptance"
)
ARCHITECTURE_ALIGNMENT_LOCK_SHA256: Final[str] = (
    "55c20924a778727b378e96c53f99ce147ff8dd88514028e3b15f03f8a7a713e3"
)

REQUIRED_INHERITED_REGRESSION_COMMAND_COUNT: Final[int] = 45
REQUIRED_PHASE_B_PRESERVATION_COMMAND_COUNT: Final[int] = 8
REQUIRED_PRIOR_COMMAND_COUNT: Final[int] = 53
ONE_COMMAND_ROLLBACK_REQUIRED: Final[bool] = True

MODE_DISABLED_DEFAULT: Final[str] = "disabled_default"
MODE_EXPLICIT_OFFLINE_CONTAINMENT: Final[str] = (
    "explicit_offline_bootstrap_containment_evaluation"
)
STATUS_REFUSED_DISABLED: Final[str] = (
    "refused_bootstrap_containment_evaluation_disabled"
)
STATUS_COMPLETED: Final[str] = (
    "completed_bootstrap_containment_evaluation"
)
STATUS_HELD_INVALID_STATE: Final[str] = (
    "held_invalid_bootstrap_containment_state"
)
STATUS_HELD_FLOW_MISMATCH: Final[str] = (
    "held_bootstrap_flow_identity_mismatch"
)
REASON_DISABLED: Final[str] = (
    "explicit_offline_bootstrap_containment_enable_required"
)
REASON_COMPLETED: Final[str] = (
    "exact_phase_b_flow_set_contained_without_runtime_consequence"
)


class FlowIdentityExpectation(NamedTuple):
    flow_name: str
    flow_spec_id: str
    assembly_result_id: str
    trace_id: str
    receipt_id: str
    verdict: str
    loaded_component_count: int
    loaded_component_set_digest: str


FLOW_IDENTITY_EXPECTATIONS: Final[tuple[FlowIdentityExpectation, ...]] = (
    FlowIdentityExpectation(
        "slice31-disabled-default-probe-trace-v1",
        "trace_flow_spec:7ba11645e4c67bd23a08d4e87c0e93fc0e9dfe1ebb506e6c8c7b03a70c680474",
        "trace_receipt_assembly_result:263250aa757ed885166324ba92e79e29d7973652820b2fa2b912351b334e6105",
        "derivation_trace:2b8c93f50541eabd90093bcd0ed1554d986aeb2e1515e1b182c2d3124925f667",
        "derivation_receipt:b589d1aeea8dd72deb564f03e3c1589d1486109ddbfda4fd66115f70c1195081",
        "PASS_LAWFUL_REFUSAL",
        0,
        "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    ),
    FlowIdentityExpectation(
        "slice31-explicit-inspection-disabled-trace-v1",
        "trace_flow_spec:c5304dbf2661c209493e06b00c60fb71fee27edb7b244c016adc89366fbafccc",
        "trace_receipt_assembly_result:10401fbfca3d8028bcc7cefc021dae6d79af8851f55eda4938a12f2bfebf1231",
        "derivation_trace:bb31d1a97a91939285585d2d70536989c6f8f330a077cb7cb5f5723b1367277f",
        "derivation_receipt:9341b31d7ad180e2b575194a791edf1ccc73789902d7a84167e3a474e18059ce",
        "PASS_LAWFUL_REFUSAL",
        0,
        "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    ),
    FlowIdentityExpectation(
        "slice31-explicit-inspection-enabled-trace-v1",
        "trace_flow_spec:1b287ef8c83295791644713a10027e183ff47d067273338cb7a368d5c85e245b",
        "trace_receipt_assembly_result:2e07283d2b529ddc9993e7bc076e7477486ba74d2e0350bf575a6172299f697c",
        "derivation_trace:cd2258f47a84d52d4556883736b1de885d894051df8df1f0c3927225dcb1efa2",
        "derivation_receipt:08fc291a63fd836034c2228d617129ccef583638414f35b5bd6597b44990782f",
        "PASS_COMPLETED_READ_ONLY_FLOW",
        0,
        "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    ),
    FlowIdentityExpectation(
        "slice32-static-loading-disabled-trace-v1",
        "trace_flow_spec:299c1cadfa09430797b780de22015c503fd0ee775286aeda318259495db14319",
        "trace_receipt_assembly_result:9c9d414851a6c29f56d527af37ae975d304a7ae6d27343eb44018ff3dab6389a",
        "derivation_trace:74300a2964ccecebf9a33abc4865066849aafa61a62061908b14a1e1a4cbf691",
        "derivation_receipt:0476851da45d2870e595e0a22e194233763ae987847b60dd33cbe91eee59b75c",
        "PASS_LAWFUL_REFUSAL",
        0,
        "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    ),
    FlowIdentityExpectation(
        "slice32-static-loading-enabled-trace-v1",
        "trace_flow_spec:41c6995f7e8baa1caaed68b10f3dd4d672f1ec3cdd941f8e63f5e254afd817cc",
        "trace_receipt_assembly_result:c01088bfe7403df4cba3b0cda77482efad3354c5803ccca08db527cf4c9e245e",
        "derivation_trace:aa72509aa8211ac4a0baa7d10a63f2cd863de04d7027d4feea58d0791c8d6688",
        "derivation_receipt:787b78069c29d89f2024daa02f0fcdec60373f68cd0743417dc66190b6a2f87a",
        "PASS_COMPLETED_READ_ONLY_FLOW",
        15,
        "f73f5d62f229cbb04ca7aaf945fcdf145d77fe3b80e48c930356c55d1f70f5ae",
    ),
)

REQUIRED_CONTAINMENT_GUARDS: Final[tuple[str, ...]] = (
    "exact_five_flow_catalog",
    "exact_slice33_result_identity",
    "deterministic_repeatability",
    "fixture_only",
    "offline_only",
    "read_only",
    "no_network_access",
    "no_filesystem_write",
    "no_runtime_memory_write",
    "no_evidence_mutation",
    "no_external_resource_ingestion",
    "no_component_behavior_invocation",
    "no_component_verifier_invocation",
    "no_gp014_import_or_call",
    "no_delivery",
    "no_tool_routing",
    "no_action",
    "no_runtime_route_api_ui_connection",
    "no_acceptance_widening",
    "no_general_language_or_production_claim",
)

PROHIBITED_AUTHORITY_CATEGORIES: Final[tuple[str, ...]] = (
    "network",
    "runtime_memory_write",
    "evidence_mutation",
    "external_resource_ingestion",
    "component_behavior_invocation",
    "component_verifier_invocation",
    "gp014_import_or_call",
    "delivery",
    "tool_routing",
    "action",
    "route",
    "api",
    "ui",
    "llm_authority",
    "vector_authority",
    "embedding_authority",
    "rag_authority",
    "chroma_authority",
    "qwen_authority",
    "ollama_authority",
    "general_language_claim",
    "release_authority",
    "production_readiness",
)
