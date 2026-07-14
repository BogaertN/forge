"""Exact accepted Slice 31 and Slice 32 fixture-flow identities for Slice 33."""

from __future__ import annotations

import hashlib
from typing import Final

from ..schema import canonical_json
from .schema import (
    VERDICT_COMPLETED_READ_ONLY_FLOW,
    VERDICT_LAWFUL_REFUSAL,
    AcceptedTraceFlowSpec,
    DerivationReceiptRecord,
    DerivationTraceRecord,
    DerivationTraceStep,
    build_derivation_receipt_record,
    build_derivation_trace_record,
    build_derivation_trace_step,
    build_trace_flow_spec,
    build_trace_receipt_assembly_state,
)

ARCHITECTURE_ALIGNMENT_LOCK_SHA256: Final[str] = (
    "55c20924a778727b378e96c53f99ce147ff8dd88514028e3b15f03f8a7a713e3"
)
SLICE30_ACCEPTED_HEAD: Final[str] = (
    "edcbea0e422a9e9fc3c590e1488adc28554c4b8c"
)
SLICE31_ACCEPTED_HEAD: Final[str] = (
    "65d5695075632718758b345786d55bd7f7de3687"
)
SLICE32_ACCEPTED_HEAD: Final[str] = (
    "e492acfa9ccf5f8b2fdcbd5c91d79451c0374275"
)
SLICE32_R1_ACCEPTED_HEAD: Final[str] = (
    "32f950d4bbe1037e2a56092436acc82b68261acf"
)

EXACT_DISABLED_ASSEMBLY_STATE_ID: Final[str] = (
    build_trace_receipt_assembly_state(
        explicit_offline_developer_enable=False
    ).assembly_state_id
)
EXACT_ENABLED_ASSEMBLY_STATE_ID: Final[str] = (
    build_trace_receipt_assembly_state(
        explicit_offline_developer_enable=True
    ).assembly_state_id
)

SOURCE_VERSION_REFS: Final[tuple[str, ...]] = (
    f"architecture_alignment_lock_sha256:{ARCHITECTURE_ALIGNMENT_LOCK_SHA256}",
    f"slice30_head:{SLICE30_ACCEPTED_HEAD}",
    f"slice31_head:{SLICE31_ACCEPTED_HEAD}",
    f"slice32_head:{SLICE32_ACCEPTED_HEAD}",
    f"slice32_r1_head:{SLICE32_R1_ACCEPTED_HEAD}",
)

FLOW_S31_DISABLED_DEFAULT: Final[str] = (
    "slice31-disabled-default-probe-trace-v1"
)
FLOW_S31_EXPLICIT_DISABLED: Final[str] = (
    "slice31-explicit-inspection-disabled-trace-v1"
)
FLOW_S31_EXPLICIT_ENABLED: Final[str] = (
    "slice31-explicit-inspection-enabled-trace-v1"
)
FLOW_S32_DISABLED: Final[str] = (
    "slice32-static-loading-disabled-trace-v1"
)
FLOW_S32_ENABLED: Final[str] = (
    "slice32-static-loading-enabled-trace-v1"
)

S31_DISABLED_STATE_ID: Final[str] = (
    "bootstrap_adapter_state:186a06c794f615bde82c23c238ba79f85a117b7ac2eb6d084d9ada13aa8e1fef"
)
S31_ENABLED_STATE_ID: Final[str] = (
    "bootstrap_adapter_state:3049355164b0328b9799c822e6aacfd434cd10d615aecff86442690b96283460"
)
S31_DISABLED_FIXTURE_ID: Final[str] = (
    "bootstrap_fixture:67a85118d711b5235173f5d8718aaaca29c7c88c0bc6a86a31a57731fcb581ed"
)
S31_EXPLICIT_FIXTURE_ID: Final[str] = (
    "bootstrap_fixture:1943ec0bd18074630065e62589a5fe48a35e2cadbe9500d0c618557aac41c8a9"
)
S31_DISABLED_DEFAULT_RESULT_ID: Final[str] = (
    "bootstrap_adapter_result:03ba612e551da181079cfb3b421460a04de28dfe42d72615d8bf77a86351fc1a"
)
S31_EXPLICIT_DISABLED_RESULT_ID: Final[str] = (
    "bootstrap_adapter_result:51bcb2f52a96d742cf63fe992a40bd6223b0423b746d822a29821f2171066e3a"
)
S31_EXPLICIT_ENABLED_RESULT_ID: Final[str] = (
    "bootstrap_adapter_result:00d28f7da240c9fa23ef6a0f2f19236e9c1e03de82cebb7e61d841ea8ee06efd"
)
S31_OBSERVATION_ID: Final[str] = (
    "bootstrap_fixture_observation:dcb904c8c842feb968cc01f32e9434e023b58787a0250e6d9cc42c0dacef2060"
)
BOOTSTRAP_AUTHORITY_STATE_ID: Final[str] = (
    "bootstrap_authority:86b5023d8d44a01f5cafac84ade851471b2568b6d8349bd48a243fdc489f83f6"
)
BOOTSTRAP_IMPORT_POLICY_ID: Final[str] = (
    "bootstrap_import_policy:6fb6b64eb931269fb74093b8ead48560b2d852319baa8ab7731bc4fdbb003e08"
)
BOOTSTRAP_BOUNDARY_ID: Final[str] = (
    "bootstrap_boundary:9a0ac3e201cdd18d7974b4f7af77dbf0bb20ae8d28af4b34893c10ef6866183c"
)
COMPONENT_REGISTRY_ID: Final[str] = (
    "bootstrap_registry:1a771c2ca6bd88e2dc8ce3be555ef5eb86e62d56d460c4f3d30cebc84c04faa5"
)

S32_FIXTURE_ID: Final[str] = (
    "component_loading_fixture:1cb2ed164c1c18c61ba202bdeaa1b5e1bb2381414903e1208f9b1f819bbc11a2"
)
S32_DISABLED_STATE_ID: Final[str] = (
    "component_loading_state:78be102f2a87996ed3c9f4ccbe568c09f10b0a201f7826d9dcc709b660d89f08"
)
S32_ENABLED_STATE_ID: Final[str] = (
    "component_loading_state:2436ea1e5fd118edaf8b2554473c3972d837b90f774b39c60f406e60458e674c"
)
S32_DISABLED_RESULT_ID: Final[str] = (
    "component_loading_result:cee203ebeb1e8764e9d4f5edc66fa359b49fdc9a9c38402bfbd746f31d744c21"
)
S32_ENABLED_RESULT_ID: Final[str] = (
    "component_loading_result:f4d873441759da615d263fa6483151f5b7323221caf2c75de518bc56ad4a3c84"
)

ACCEPTED_PACKAGE_NAMES: Final[tuple[str, ...]] = (
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

ACCEPTED_LOADED_COMPONENT_IDS: Final[tuple[str, ...]] = (
    "loaded_component:a806e2c498f9a1e885b75ec5ec55652a6f86065fc7c55f773f3d559e48b1296a",
    "loaded_component:c4e6b40a4c401606fcd29f811b707d38c3687f85d43d5d51c04b10c00bf79aa5",
    "loaded_component:527f12b425951438c6bb646d5082791cbd3781e6a0aa2a5c1406e0a005d2a9f5",
    "loaded_component:7f6af54282b01fd8d2fb49fcdf6856bfceaf818e0ecc856815cd30fb762bd7f5",
    "loaded_component:a985112a2e16efddbbf46b79577d6298f62fedb9fac2d24fc7d878bc2a5e1317",
    "loaded_component:d429f1bfafbd7019276588acceb73b78c282c93cacc65c49053c240968aac876",
    "loaded_component:2e460babfd9a7e006533e6f9f991a42f3c403c668fa3d07c939f6bc15db1a08f",
    "loaded_component:b84e57e37c37a76232efc2fe9fca0b6da687c7d09b3e19b89e78c7c604f034ac",
    "loaded_component:db54855906dfb8bbe0634d0118973a585fdd6f5c52f7a131c67536060972401b",
    "loaded_component:7a477494c3d5a4a0db049d478a49c7d4cef66478f00dfb6bfd5e3ee48e5ce399",
    "loaded_component:7f885a2baa0efe6786602717363820eab6485936fb75640e9ad19e881690d423",
    "loaded_component:fc2240ec6a7b54d186f3834fff61e6d31ee7010b39138ae37d2a3cc699af8fde",
    "loaded_component:3cc11a7bb5b3f83c38b39ccba74124965103293c21176448756bf8af323a172a",
    "loaded_component:4cd78accb1f852a195cef1d7d8519ec1eafa149c2d142459a343ed253eecf75b",
    "loaded_component:9b99b5dd01ed85dade855f95492cc38a0eae3bbb07b49212323d40209daadf2e",
)


def sequence_digest(values: tuple[str, ...]) -> str:
    return hashlib.sha256(canonical_json(values).encode("utf-8")).hexdigest()


EMPTY_SEQUENCE_DIGEST: Final[str] = sequence_digest(())
ACCEPTED_LOADED_COMPONENT_SET_DIGEST: Final[str] = sequence_digest(
    ACCEPTED_LOADED_COMPONENT_IDS
)


def _spec(**values: object) -> AcceptedTraceFlowSpec:
    return build_trace_flow_spec(**values)


_ACCEPTED_FLOWS: Final[tuple[AcceptedTraceFlowSpec, ...]] = (
    _spec(
        flow_name=FLOW_S31_DISABLED_DEFAULT,
        source_slice="Slice 31",
        source_enabled=False,
        fixture_name="slice31-disabled-default-probe-v1",
        fixture_id=S31_DISABLED_FIXTURE_ID,
        source_state_id=S31_DISABLED_STATE_ID,
        expected_source_status="refused_adapter_disabled",
        expected_source_reason_code="adapter_remains_disabled_by_default",
        expected_source_result_id=S31_DISABLED_DEFAULT_RESULT_ID,
        expected_observation_id="",
        expected_authority_state_id="",
        expected_import_policy_id="",
        expected_bootstrap_boundary_id="",
        expected_component_registry_id="",
        expected_loaded_package_names=(),
        expected_loaded_component_ids=(),
        expected_loaded_component_count=0,
        expected_lawful_outcome="lawful_refusal",
        expected_receipt_verdict=VERDICT_LAWFUL_REFUSAL,
    ),
    _spec(
        flow_name=FLOW_S31_EXPLICIT_DISABLED,
        source_slice="Slice 31",
        source_enabled=False,
        fixture_name="slice31-explicit-offline-boundary-inspection-v1",
        fixture_id=S31_EXPLICIT_FIXTURE_ID,
        source_state_id=S31_DISABLED_STATE_ID,
        expected_source_status="refused_adapter_disabled",
        expected_source_reason_code="explicit_offline_fixture_enable_required",
        expected_source_result_id=S31_EXPLICIT_DISABLED_RESULT_ID,
        expected_observation_id="",
        expected_authority_state_id="",
        expected_import_policy_id="",
        expected_bootstrap_boundary_id="",
        expected_component_registry_id="",
        expected_loaded_package_names=(),
        expected_loaded_component_ids=(),
        expected_loaded_component_count=0,
        expected_lawful_outcome="lawful_refusal",
        expected_receipt_verdict=VERDICT_LAWFUL_REFUSAL,
    ),
    _spec(
        flow_name=FLOW_S31_EXPLICIT_ENABLED,
        source_slice="Slice 31",
        source_enabled=True,
        fixture_name="slice31-explicit-offline-boundary-inspection-v1",
        fixture_id=S31_EXPLICIT_FIXTURE_ID,
        source_state_id=S31_ENABLED_STATE_ID,
        expected_source_status="completed_fixture_inspection",
        expected_source_reason_code="explicit_offline_fixture_inspection_completed",
        expected_source_result_id=S31_EXPLICIT_ENABLED_RESULT_ID,
        expected_observation_id=S31_OBSERVATION_ID,
        expected_authority_state_id=BOOTSTRAP_AUTHORITY_STATE_ID,
        expected_import_policy_id=BOOTSTRAP_IMPORT_POLICY_ID,
        expected_bootstrap_boundary_id=BOOTSTRAP_BOUNDARY_ID,
        expected_component_registry_id=COMPONENT_REGISTRY_ID,
        expected_loaded_package_names=(),
        expected_loaded_component_ids=(),
        expected_loaded_component_count=0,
        expected_lawful_outcome="completed_read_only_flow",
        expected_receipt_verdict=VERDICT_COMPLETED_READ_ONLY_FLOW,
    ),
    _spec(
        flow_name=FLOW_S32_DISABLED,
        source_slice="Slice 32",
        source_enabled=False,
        fixture_name="slice32-explicit-static-component-loading-v1",
        fixture_id=S32_FIXTURE_ID,
        source_state_id=S32_DISABLED_STATE_ID,
        expected_source_status="refused_component_loading_disabled",
        expected_source_reason_code="explicit_component_loading_enable_required",
        expected_source_result_id=S32_DISABLED_RESULT_ID,
        expected_observation_id="",
        expected_authority_state_id="",
        expected_import_policy_id="",
        expected_bootstrap_boundary_id="",
        expected_component_registry_id="",
        expected_loaded_package_names=(),
        expected_loaded_component_ids=(),
        expected_loaded_component_count=0,
        expected_lawful_outcome="lawful_refusal",
        expected_receipt_verdict=VERDICT_LAWFUL_REFUSAL,
    ),
    _spec(
        flow_name=FLOW_S32_ENABLED,
        source_slice="Slice 32",
        source_enabled=True,
        fixture_name="slice32-explicit-static-component-loading-v1",
        fixture_id=S32_FIXTURE_ID,
        source_state_id=S32_ENABLED_STATE_ID,
        expected_source_status="completed_static_component_loading",
        expected_source_reason_code=(
            "all_registered_components_loaded_through_static_interfaces"
        ),
        expected_source_result_id=S32_ENABLED_RESULT_ID,
        expected_observation_id="",
        expected_authority_state_id="",
        expected_import_policy_id="",
        expected_bootstrap_boundary_id=BOOTSTRAP_BOUNDARY_ID,
        expected_component_registry_id=COMPONENT_REGISTRY_ID,
        expected_loaded_package_names=ACCEPTED_PACKAGE_NAMES,
        expected_loaded_component_ids=ACCEPTED_LOADED_COMPONENT_IDS,
        expected_loaded_component_count=15,
        expected_lawful_outcome="completed_read_only_flow",
        expected_receipt_verdict=VERDICT_COMPLETED_READ_ONLY_FLOW,
    ),
)

_FLOW_BY_NAME: Final[dict[str, AcceptedTraceFlowSpec]] = {
    flow.flow_name: flow for flow in _ACCEPTED_FLOWS
}


def list_trace_flows() -> tuple[AcceptedTraceFlowSpec, ...]:
    return _ACCEPTED_FLOWS


def get_trace_flow(flow_name: str) -> AcceptedTraceFlowSpec | None:
    return _FLOW_BY_NAME.get(flow_name)


def is_exact_accepted_trace_flow(record: AcceptedTraceFlowSpec) -> bool:
    accepted = get_trace_flow(record.flow_name)
    return accepted is not None and record == accepted


def _step(
    index: int,
    kind: str,
    spec: AcceptedTraceFlowSpec,
    *,
    inputs: tuple[str, ...],
    outputs: tuple[str, ...],
    decision: str,
    reason: str,
) -> DerivationTraceStep:
    return build_derivation_trace_step(
        step_index=index,
        step_kind=kind,
        source_slice=spec.source_slice,
        input_refs=inputs,
        output_refs=outputs,
        decision=decision,
        reason_code=reason,
        identity_verified=True,
        read_only=True,
        persistent_side_effect_performed=False,
    )


def build_expected_steps(spec: AcceptedTraceFlowSpec) -> tuple[DerivationTraceStep, ...]:
    steps: list[DerivationTraceStep] = []

    def add(
        kind: str,
        inputs: tuple[str, ...],
        outputs: tuple[str, ...],
        decision: str,
        reason: str,
    ) -> None:
        steps.append(
            _step(
                len(steps) + 1,
                kind,
                spec,
                inputs=inputs,
                outputs=outputs,
                decision=decision,
                reason=reason,
            )
        )

    add(
        "flow_spec_selected",
        (spec.flow_name,),
        (spec.flow_spec_id,),
        "selected",
        "exact_static_flow_catalog_entry_selected",
    )
    add(
        "assembly_state_verified",
        ("trace_receipt_assembly_state",),
        (EXACT_ENABLED_ASSEMBLY_STATE_ID,),
        "verified",
        "explicit_offline_read_only_assembly_state_required",
    )
    add(
        "fixture_identity_verified",
        (spec.fixture_name,),
        (spec.fixture_id,),
        "verified",
        "exact_fixture_identity_matched",
    )
    add(
        "source_state_identity_verified",
        (spec.source_slice,),
        (spec.source_state_id,),
        "verified",
        "exact_source_state_identity_matched",
    )
    add(
        "source_result_executed",
        (spec.fixture_id, spec.source_state_id),
        (spec.expected_source_result_id,),
        "refused" if spec.expected_lawful_outcome == "lawful_refusal" else "completed",
        spec.expected_source_reason_code,
    )
    add(
        "source_result_identity_verified",
        (spec.expected_source_result_id,),
        (spec.expected_source_result_id,),
        "verified",
        "exact_source_result_identity_matched",
    )

    if spec.expected_lawful_outcome == "lawful_refusal":
        add(
            "lawful_refusal_verified",
            (spec.expected_source_result_id,),
            (spec.expected_source_status,),
            "verified",
            "lawful_disabled_refusal_preserved",
        )
    elif spec.source_slice == "Slice 31":
        add(
            "observation_identity_verified",
            (spec.expected_source_result_id,),
            (spec.expected_observation_id,),
            "verified",
            "exact_bootstrap_observation_identity_matched",
        )
        add(
            "bootstrap_lineage_verified",
            (spec.expected_observation_id,),
            (
                spec.expected_authority_state_id,
                spec.expected_import_policy_id,
                spec.expected_bootstrap_boundary_id,
                spec.expected_component_registry_id,
            ),
            "verified",
            "exact_slice30_boundary_lineage_matched",
        )
    else:
        add(
            "slice31_prerequisite_verified",
            (spec.expected_source_result_id,),
            (S31_EXPLICIT_ENABLED_RESULT_ID,),
            "verified",
            "exact_slice31_prerequisite_result_matched",
        )
        add(
            "bootstrap_lineage_verified",
            (S31_EXPLICIT_ENABLED_RESULT_ID,),
            (
                spec.expected_bootstrap_boundary_id,
                spec.expected_component_registry_id,
            ),
            "verified",
            "exact_slice30_boundary_and_registry_matched",
        )
        add(
            "loaded_component_set_verified",
            (spec.expected_component_registry_id,),
            spec.expected_loaded_component_ids,
            "verified",
            "exact_15_component_identity_set_and_order_matched",
        )

    add(
        "negative_authority_verified",
        (spec.expected_source_result_id,),
        ("authority:none", "persistent_effect:none"),
        "verified",
        "all_consequential_authority_remained_false",
    )
    return tuple(steps)


def build_expected_trace(
    spec: AcceptedTraceFlowSpec,
    *,
    assembly_state_id: str,
) -> DerivationTraceRecord:
    steps = build_expected_steps(spec)
    loaded_digest = sequence_digest(spec.expected_loaded_component_ids)
    step_digest = sequence_digest(tuple(step.step_id for step in steps))
    return build_derivation_trace_record(
        flow_spec_id=spec.flow_spec_id,
        flow_name=spec.flow_name,
        assembly_state_id=assembly_state_id,
        source_slice=spec.source_slice,
        source_fixture_id=spec.fixture_id,
        source_state_id=spec.source_state_id,
        source_result_id=spec.expected_source_result_id,
        source_status=spec.expected_source_status,
        source_reason_code=spec.expected_source_reason_code,
        observation_id=spec.expected_observation_id,
        authority_state_id=spec.expected_authority_state_id,
        import_policy_id=spec.expected_import_policy_id,
        bootstrap_boundary_id=spec.expected_bootstrap_boundary_id,
        component_registry_id=spec.expected_component_registry_id,
        loaded_package_names=spec.expected_loaded_package_names,
        loaded_component_ids=spec.expected_loaded_component_ids,
        loaded_component_count=spec.expected_loaded_component_count,
        loaded_component_set_digest=loaded_digest,
        steps=steps,
        step_id_digest=step_digest,
        trace_complete=True,
        exact_identity_bound=True,
        read_only=True,
        fixture_only=True,
        offline_only=True,
        persistent_trace_write_performed=False,
        persistent_receipt_write_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        memory_write_performed=False,
        evidence_mutation_performed=False,
        external_resource_used=False,
        delivery_performed=False,
        tool_routing_performed=False,
        action_performed=False,
        component_invocation_performed=False,
        component_verifier_invocation_performed=False,
        gp014_imported=False,
        gp014_called=False,
        runtime_connection_performed=False,
    )


def build_expected_receipt(
    spec: AcceptedTraceFlowSpec,
) -> DerivationReceiptRecord:
    canonical_trace = build_expected_trace(
        spec,
        assembly_state_id=EXACT_ENABLED_ASSEMBLY_STATE_ID,
    )
    return build_derivation_receipt_record(
        trace_id=canonical_trace.trace_id,
        flow_spec_id=spec.flow_spec_id,
        flow_name=spec.flow_name,
        verdict=spec.expected_receipt_verdict,
        source_slice=spec.source_slice,
        source_fixture_id=spec.fixture_id,
        source_state_id=spec.source_state_id,
        source_result_id=spec.expected_source_result_id,
        source_status=spec.expected_source_status,
        source_reason_code=spec.expected_source_reason_code,
        observation_id=spec.expected_observation_id,
        bootstrap_boundary_id=spec.expected_bootstrap_boundary_id,
        component_registry_id=spec.expected_component_registry_id,
        loaded_component_count=spec.expected_loaded_component_count,
        loaded_component_set_digest=sequence_digest(
            spec.expected_loaded_component_ids
        ),
        step_id_digest=canonical_trace.step_id_digest,
        source_version_refs=SOURCE_VERSION_REFS,
        exact_identity_bound=True,
        trace_complete=True,
        source_result_validated=True,
        lawful_refusal_accepted=(
            spec.expected_lawful_outcome == "lawful_refusal"
        ),
        completed_flow_accepted=(
            spec.expected_lawful_outcome == "completed_read_only_flow"
        ),
        read_only=True,
        fixture_only=True,
        offline_only=True,
        authority_granted=False,
        acceptance_widened=False,
        persistent_trace_write_performed=False,
        persistent_receipt_write_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        memory_write_performed=False,
        evidence_mutation_performed=False,
        external_resource_used=False,
        delivery_performed=False,
        tool_routing_performed=False,
        action_performed=False,
        component_invocation_performed=False,
        component_verifier_invocation_performed=False,
        gp014_imported=False,
        gp014_called=False,
        runtime_connection_performed=False,
        production_ready=False,
        release_authorized=False,
    )
