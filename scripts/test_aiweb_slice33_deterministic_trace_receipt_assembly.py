#!/usr/bin/env python3
"""Behavior and adversarial proof for Slice 33 trace/receipt assembly."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
REPO_ROOT = str(Path(__file__).resolve().parents[1])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from aiweb_language_core_bootstrap.trace_receipt import (
    STATUS_COMPLETED,
    STATUS_HELD_INVALID_STATE,
    STATUS_HELD_UNKNOWN_FLOW,
    STATUS_REFUSED_DISABLED,
    assemble_trace_receipt,
    build_trace_receipt_assembly_state,
    list_trace_flows,
    validate_derivation_receipt_record,
    validate_derivation_trace_record,
    validate_trace_flow_spec,
    validate_trace_receipt_assembly_result,
    validate_trace_receipt_assembly_state,
)
from aiweb_language_core_bootstrap.trace_receipt.flow_catalog import (
    ACCEPTED_LOADED_COMPONENT_IDS,
    ACCEPTED_PACKAGE_NAMES,
    EXACT_DISABLED_ASSEMBLY_STATE_ID,
    EXACT_ENABLED_ASSEMBLY_STATE_ID,
    FLOW_S31_EXPLICIT_ENABLED,
    FLOW_S32_ENABLED,
    SOURCE_VERSION_REFS,
    sequence_digest,
)
from aiweb_language_core_bootstrap.trace_receipt.schema import (
    AcceptedTraceFlowSpec,
    DerivationReceiptRecord,
    DerivationTraceRecord,
    DerivationTraceStep,
    TraceReceiptAssemblyResult,
)

failures: list[str] = []
check_count = 0


def check(condition: bool, label: str) -> None:
    global check_count
    check_count += 1
    if not condition:
        failures.append(label)


def reid_step(step: DerivationTraceStep) -> DerivationTraceStep:
    return replace(step, step_id=step.expected_id())


def reid_trace(trace: DerivationTraceRecord) -> DerivationTraceRecord:
    return replace(trace, trace_id=trace.expected_id())


def reid_receipt(receipt: DerivationReceiptRecord) -> DerivationReceiptRecord:
    return replace(receipt, receipt_id=receipt.expected_id())


def reid_result(result: TraceReceiptAssemblyResult) -> TraceReceiptAssemblyResult:
    return replace(result, assembly_result_id=result.expected_id())


def rebuilt_result(
    original: TraceReceiptAssemblyResult,
    *,
    trace: DerivationTraceRecord,
    receipt: DerivationReceiptRecord,
) -> TraceReceiptAssemblyResult:
    return reid_result(replace(original, trace=trace, receipt=receipt))


def mutated_trace_result(
    original: TraceReceiptAssemblyResult,
    trace: DerivationTraceRecord,
) -> TraceReceiptAssemblyResult:
    trace = reid_trace(trace)
    assert original.receipt is not None
    receipt = reid_receipt(replace(original.receipt, trace_id=trace.trace_id))
    return rebuilt_result(original, trace=trace, receipt=receipt)


# Fresh-process import containment: importing Slice 33 must not load accepted components.
probe = subprocess.run(
    [
        sys.executable,
        "-B",
        "-c",
        (
            "import sys, json; "
            "import aiweb_language_core_bootstrap.trace_receipt; "
            "names=" + repr(ACCEPTED_PACKAGE_NAMES) + "; "
            "print(json.dumps([n for n in names if n in sys.modules]))"
        ),
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    check=False,
)
check(probe.returncode == 0, "fresh import probe returns zero")
check(probe.stderr == "", "fresh import probe stderr empty")
check(json.loads(probe.stdout) == [], "Slice 33 import loads zero accepted components")

flows = list_trace_flows()
check(len(flows) == 5, "exact five accepted trace flows")
check(len({flow.flow_name for flow in flows}) == 5, "flow names unique")
check(len({flow.flow_spec_id for flow in flows}) == 5, "flow IDs unique")
check(tuple(flow.source_slice for flow in flows).count("Slice 31") == 3, "three Slice 31 flows")
check(tuple(flow.source_slice for flow in flows).count("Slice 32") == 2, "two Slice 32 flows")

for flow in flows:
    check(validate_trace_flow_spec(flow).ok, f"accepted flow validates: {flow.flow_name}")
    check(flow.flow_spec_id == flow.expected_id(), f"flow stable ID exact: {flow.flow_name}")

state_disabled = build_trace_receipt_assembly_state()
state_enabled = build_trace_receipt_assembly_state(
    explicit_offline_developer_enable=True,
)
check(validate_trace_receipt_assembly_state(state_disabled).ok, "disabled state validates")
check(validate_trace_receipt_assembly_state(state_enabled).ok, "enabled state validates")
check(state_disabled.assembly_state_id == EXACT_DISABLED_ASSEMBLY_STATE_ID, "disabled state ID exact")
check(state_enabled.assembly_state_id == EXACT_ENABLED_ASSEMBLY_STATE_ID, "enabled state ID exact")
check(state_disabled.enabled is False, "disabled state remains disabled")
check(state_enabled.enabled is True, "enabled state explicitly enabled")
check(state_enabled.read_only is True, "enabled state remains read only")
check(state_enabled.persistent_trace_write_allowed is False, "persistent trace write forbidden")
check(state_enabled.persistent_receipt_write_allowed is False, "persistent receipt write forbidden")

completed: dict[str, TraceReceiptAssemblyResult] = {}
for flow in flows:
    disabled = assemble_trace_receipt(flow.flow_name, assembly_state=state_disabled)
    check(disabled.status == STATUS_REFUSED_DISABLED, f"disabled refusal: {flow.flow_name}")
    check(disabled.trace is None, f"disabled trace absent: {flow.flow_name}")
    check(disabled.receipt is None, f"disabled receipt absent: {flow.flow_name}")
    check(validate_trace_receipt_assembly_result(disabled).ok, f"disabled result validates: {flow.flow_name}")

    result = assemble_trace_receipt(flow.flow_name, assembly_state=state_enabled)
    repeated = assemble_trace_receipt(flow.flow_name, assembly_state=state_enabled)
    completed[flow.flow_name] = result
    check(result.status == STATUS_COMPLETED, f"completed status: {flow.flow_name}")
    check(result == repeated, f"deterministic repeated result: {flow.flow_name}")
    check(result.trace is not None, f"trace present: {flow.flow_name}")
    check(result.receipt is not None, f"receipt present: {flow.flow_name}")
    check(validate_trace_receipt_assembly_result(result).ok, f"completed result validates: {flow.flow_name}")
    assert result.trace is not None and result.receipt is not None
    check(validate_derivation_trace_record(result.trace).ok, f"trace validates: {flow.flow_name}")
    check(validate_derivation_receipt_record(result.receipt).ok, f"receipt validates: {flow.flow_name}")
    check(result.receipt.trace_id == result.trace.trace_id, f"receipt binds trace: {flow.flow_name}")
    check(result.trace.flow_spec_id == flow.flow_spec_id, f"trace binds flow: {flow.flow_name}")
    check(result.receipt.flow_spec_id == flow.flow_spec_id, f"receipt binds flow: {flow.flow_name}")
    check(result.trace.source_result_id == flow.expected_source_result_id, f"trace binds source result: {flow.flow_name}")
    check(result.receipt.source_result_id == flow.expected_source_result_id, f"receipt binds source result: {flow.flow_name}")
    check(result.trace.source_status == flow.expected_source_status, f"trace status exact: {flow.flow_name}")
    check(result.receipt.source_reason_code == flow.expected_source_reason_code, f"receipt reason exact: {flow.flow_name}")
    check(result.receipt.source_version_refs == SOURCE_VERSION_REFS, f"source versions exact: {flow.flow_name}")
    check(result.trace.step_id_digest == result.receipt.step_id_digest, f"step digest bound: {flow.flow_name}")
    check(result.trace.trace_complete is True, f"trace complete: {flow.flow_name}")
    check(result.receipt.exact_identity_bound is True, f"receipt exact identity bound: {flow.flow_name}")
    check(result.persistent_side_effect_performed is False, f"result no side effect: {flow.flow_name}")
    check(result.trace.persistent_trace_write_performed is False, f"trace not persisted: {flow.flow_name}")
    check(result.receipt.persistent_receipt_write_performed is False, f"receipt not persisted: {flow.flow_name}")
    check(tuple(step.step_index for step in result.trace.steps) == tuple(range(1, len(result.trace.steps) + 1)), f"step order contiguous: {flow.flow_name}")
    check(len({step.step_id for step in result.trace.steps}) == len(result.trace.steps), f"step IDs unique: {flow.flow_name}")

s31_success = completed[FLOW_S31_EXPLICIT_ENABLED]
s32_success = completed[FLOW_S32_ENABLED]
assert s31_success.trace is not None and s31_success.receipt is not None
assert s32_success.trace is not None and s32_success.receipt is not None
check(s31_success.trace.observation_id != "", "Slice 31 success binds observation")
check(s31_success.trace.bootstrap_boundary_id != "", "Slice 31 success binds boundary")
check(s31_success.trace.component_registry_id != "", "Slice 31 success binds registry")
check(s32_success.trace.loaded_package_names == ACCEPTED_PACKAGE_NAMES, "Slice 32 package order exact")
check(s32_success.trace.loaded_component_ids == ACCEPTED_LOADED_COMPONENT_IDS, "Slice 32 loaded IDs exact")
check(s32_success.trace.loaded_component_count == 15, "Slice 32 loaded count exact")
check(s32_success.trace.loaded_component_set_digest == sequence_digest(ACCEPTED_LOADED_COMPONENT_IDS), "Slice 32 component digest exact")

# Unknown flow is held and never creates a trace or receipt.
unknown = assemble_trace_receipt("unknown-slice33-flow", assembly_state=state_enabled)
check(unknown.status == STATUS_HELD_UNKNOWN_FLOW, "unknown flow held")
check(unknown.trace is None and unknown.receipt is None, "unknown flow creates no proof")
check(validate_trace_receipt_assembly_result(unknown).ok, "unknown held result validates")

# A self-consistent but unaccepted state is held.
invalid_state = replace(state_enabled, network_allowed=True)
invalid_state = replace(invalid_state, assembly_state_id=invalid_state.expected_id())
held = assemble_trace_receipt(flows[0].flow_name, assembly_state=invalid_state)
check(held.status == STATUS_HELD_INVALID_STATE, "altered state held")
check(held.trace is None and held.receipt is None, "altered state creates no proof")
check(validate_trace_receipt_assembly_result(held).ok, "invalid-state held result validates")

# Recomputed fake flow specification remains unaccepted.
fake_flow = replace(
    flows[0],
    flow_name="fabricated-self-consistent-flow",
    expected_source_result_id="bootstrap_adapter_result:" + "f" * 64,
)
fake_flow = replace(fake_flow, flow_spec_id=fake_flow.expected_id())
check(fake_flow.flow_spec_id == fake_flow.expected_id(), "fake flow self-consistent")
check(not validate_trace_flow_spec(fake_flow).ok, "fake recomputed flow rejected")

# Mutate each critical trace identity and recompute all enclosing IDs.
base = s32_success
assert base.trace is not None and base.receipt is not None
trace_mutations = (
    replace(base.trace, source_result_id="component_loading_result:" + "a" * 64),
    replace(base.trace, source_fixture_id="component_loading_fixture:" + "b" * 64),
    replace(base.trace, source_state_id="component_loading_state:" + "c" * 64),
    replace(base.trace, bootstrap_boundary_id="bootstrap_boundary:" + "d" * 64),
    replace(base.trace, component_registry_id="bootstrap_registry:" + "e" * 64),
    replace(base.trace, loaded_package_names=("aiweb_fake_component",) * 15),
    replace(base.trace, loaded_component_ids=tuple(f"loaded_component:{i:064x}" for i in range(15))),
    replace(base.trace, loaded_component_count=14),
    replace(base.trace, loaded_component_set_digest="0" * 64),
    replace(base.trace, step_id_digest="1" * 64),
    replace(base.trace, assembly_state_id="trace_receipt_assembly_state:" + "2" * 64),
)
for index, mutated in enumerate(trace_mutations, start=1):
    attack = mutated_trace_result(base, mutated)
    check(attack.assembly_result_id == attack.expected_id(), f"trace attack {index} fully re-IDed")
    check(not validate_trace_receipt_assembly_result(attack).ok, f"trace attack {index} rejected")

# Reorder, omit, duplicate, and alter a step while recomputing every affected ID.
steps = base.trace.steps
reversed_steps = tuple(reid_step(replace(step, step_index=i)) for i, step in enumerate(reversed(steps), start=1))
attack = mutated_trace_result(base, replace(base.trace, steps=reversed_steps, step_id_digest=sequence_digest(tuple(s.step_id for s in reversed_steps))))
check(not validate_trace_receipt_assembly_result(attack).ok, "reordered steps rejected after re-ID")

missing_steps = tuple(reid_step(replace(step, step_index=i)) for i, step in enumerate(steps[:-1], start=1))
attack = mutated_trace_result(base, replace(base.trace, steps=missing_steps, step_id_digest=sequence_digest(tuple(s.step_id for s in missing_steps))))
check(not validate_trace_receipt_assembly_result(attack).ok, "missing step rejected after re-ID")

duplicate_steps = tuple(reid_step(replace(step, step_index=i)) for i, step in enumerate(steps[:-1] + (steps[-2],), start=1))
attack = mutated_trace_result(base, replace(base.trace, steps=duplicate_steps, step_id_digest=sequence_digest(tuple(s.step_id for s in duplicate_steps))))
check(not validate_trace_receipt_assembly_result(attack).ok, "duplicate step rejected after re-ID")

altered_step = reid_step(replace(steps[0], reason_code="fabricated_but_recomputed_reason"))
altered_steps = (altered_step,) + steps[1:]
attack = mutated_trace_result(base, replace(base.trace, steps=altered_steps, step_id_digest=sequence_digest(tuple(s.step_id for s in altered_steps))))
check(not validate_trace_receipt_assembly_result(attack).ok, "altered step rejected after re-ID")

# Mutate receipt identities and authority fields, recomputing receipt and result IDs.
receipt_mutations = (
    replace(base.receipt, verdict="PASS_FABRICATED"),
    replace(base.receipt, source_result_id="component_loading_result:" + "3" * 64),
    replace(base.receipt, source_version_refs=SOURCE_VERSION_REFS[:-1] + ("slice32_r1_head:" + "4" * 40,)),
    replace(base.receipt, loaded_component_set_digest="5" * 64),
    replace(base.receipt, step_id_digest="6" * 64),
    replace(base.receipt, authority_granted=True),
    replace(base.receipt, acceptance_widened=True),
    replace(base.receipt, memory_write_performed=True),
    replace(base.receipt, gp014_called=True),
    replace(base.receipt, trace_id="derivation_trace:" + "7" * 64),
)
for index, mutated in enumerate(receipt_mutations, start=1):
    mutated = reid_receipt(mutated)
    attack = reid_result(replace(base, receipt=mutated))
    check(attack.assembly_result_id == attack.expected_id(), f"receipt attack {index} fully re-IDed")
    check(not validate_trace_receipt_assembly_result(attack).ok, f"receipt attack {index} rejected")

# A fully fabricated trace/receipt/result chain remains rejected after all IDs are recomputed.
fake_steps = tuple(
    reid_step(
        replace(
            step,
            input_refs=(f"fabricated_input:{i}",),
            output_refs=(f"fabricated_output:{i}",),
        )
    )
    for i, step in enumerate(base.trace.steps, start=1)
)
fake_trace = reid_trace(
    replace(
        base.trace,
        source_result_id="component_loading_result:" + "8" * 64,
        loaded_package_names=tuple(f"aiweb_fake_component_{i}" for i in range(15)),
        loaded_component_ids=tuple(f"loaded_component:{i + 100:064x}" for i in range(15)),
        loaded_component_set_digest=sequence_digest(tuple(f"loaded_component:{i + 100:064x}" for i in range(15))),
        steps=fake_steps,
        step_id_digest=sequence_digest(tuple(step.step_id for step in fake_steps)),
    )
)
fake_receipt = reid_receipt(
    replace(
        base.receipt,
        trace_id=fake_trace.trace_id,
        source_result_id=fake_trace.source_result_id,
        loaded_component_set_digest=fake_trace.loaded_component_set_digest,
        step_id_digest=fake_trace.step_id_digest,
    )
)
fake_result = rebuilt_result(base, trace=fake_trace, receipt=fake_receipt)
check(fake_trace.trace_id == fake_trace.expected_id(), "fabricated trace self-consistent")
check(fake_receipt.receipt_id == fake_receipt.expected_id(), "fabricated receipt self-consistent")
check(fake_result.assembly_result_id == fake_result.expected_id(), "fabricated result self-consistent")
check(not validate_trace_receipt_assembly_result(fake_result).ok, "fully fabricated recomputed proof chain rejected")

if failures:
    print("SLICE33_DETERMINISTIC_TRACE_RECEIPT_ASSEMBLY_TEST=FAIL")
    print(f"TEST_COUNT={check_count}")
    for failure in failures:
        print(f"FAIL={failure}")
    raise SystemExit(1)

print("SLICE33_DETERMINISTIC_TRACE_RECEIPT_ASSEMBLY_TEST=PASS")
print(f"TEST_COUNT={check_count}")
print("FABRICATED_RECOMPUTED_TRACE_RECEIPT_CHAIN_REJECTED=True")
