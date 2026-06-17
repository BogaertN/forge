#!/usr/bin/env python3
"""Behavior test for Slice 9 predicate-role frame boundary scaffold."""

from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
sys.path.insert(0, str(REPO))

from aiweb_predicate_role_boundary_scaffold.effect_boundary import (
    EffectBoundaryRecord,
    demo_effect_boundary_record,
    validate_effect_boundary_record,
)
from aiweb_predicate_role_boundary_scaffold.predicate_frame import (
    PredicateFrameBoundaryRecord,
    demo_predicate_frame_record,
    demo_unknown_predicate_frame_record,
    predicate_role_scope_record,
    validate_predicate_frame_record,
)
from aiweb_predicate_role_boundary_scaffold.roles import (
    RoleBoundaryRecord,
    demo_missing_role_record,
    demo_role_record,
    demo_unknown_role_record,
    validate_role_record,
)
from aiweb_predicate_role_boundary_scaffold.speech_act import (
    SpeechActBoundaryRecord,
    demo_command_speech_act_record,
    demo_implementation_request_speech_act_record,
    demo_memory_request_speech_act_record,
    demo_speech_act_record,
    validate_speech_act_record,
)
from aiweb_predicate_role_boundary_scaffold.verify import run_verification

print("=" * 60)
print("AIWEB SLICE 9 PREDICATE-ROLE FRAME BOUNDARY SCAFFOLD BEHAVIOR TEST")
print("=" * 60)
print(f"Target repo: {REPO}")

passes = []
failures = []


def check(condition: bool, message: str) -> None:
    if condition:
        passes.append(message)
    else:
        failures.append(message)


scope = predicate_role_scope_record()
check(scope["scaffold_only"] is True, "scope is scaffold-only")
check(scope["runtime_effect"] == "none", "scope has no runtime effect")
check(scope["dependency_change"] == "none", "scope changes no dependency")
for key in (
    "predicate_resolution",
    "role_resolution",
    "speech_act_permission",
    "effect_authorization",
    "selected_meaning",
    "gate_selection",
    "expression_rendering",
    "tool_invocation",
    "capability_route",
    "action_route",
    "memory_write",
    "evidence_validation",
    "external_resource_admission",
    "delivery_action",
    "production_readiness",
    "release_authority",
):
    check(scope[key] is False, f"scope blocks {key}")
check(scope["sanskrit_wordnet_status"] == "hold_unadmitted", "Sanskrit WordNet remains hold/unadmitted")

predicate = demo_predicate_frame_record()
unknown_predicate = demo_unknown_predicate_frame_record()
role = demo_role_record()
missing_role = demo_missing_role_record()
unknown_role = demo_unknown_role_record()
speech = demo_speech_act_record()
memory_speech = demo_memory_request_speech_act_record()
implementation_speech = demo_implementation_request_speech_act_record()
command_speech = demo_command_speech_act_record()
effect = demo_effect_boundary_record()

check(validate_predicate_frame_record(predicate).passed, "predicate frame boundary validates")
check(validate_predicate_frame_record(unknown_predicate).passed, "unknown predicate boundary validates")
check(validate_role_record(role).passed, "role boundary validates")
check(validate_role_record(missing_role).passed, "missing role boundary validates")
check(validate_role_record(unknown_role).passed, "unknown role boundary validates")
check(validate_speech_act_record(speech).passed, "speech-act boundary validates")
check(validate_speech_act_record(memory_speech).passed, "memory-request speech boundary validates")
check(validate_speech_act_record(implementation_speech).passed, "implementation-request speech boundary validates")
check(validate_speech_act_record(command_speech).passed, "command speech boundary validates")
check(validate_effect_boundary_record(effect).passed, "effect boundary validates")

check(predicate.boundary_id() == demo_predicate_frame_record().boundary_id(), "predicate ID is stable")
check(role.boundary_id() == demo_role_record().boundary_id(), "role ID is stable")
check(speech.boundary_id() == demo_speech_act_record().boundary_id(), "speech-act ID is stable")
check(effect.boundary_id() == demo_effect_boundary_record().boundary_id(), "effect ID is stable")

for field_name in (
    "execution_authority",
    "tool_invocation",
    "capability_route",
    "delivery_action",
    "memory_write",
    "evidence_validation",
    "gate_selection",
    "selected_meaning",
    "expression_rendering",
    "external_resource_admission",
):
    unsafe = PredicateFrameBoundaryRecord(
        predicate_key=f"unsafe_{field_name}",
        action_root="unsafe",
        frame_kind="action_boundary",
        namespace="aiweb:core",
        role_keys=("agent_boundary",),
        speech_act_key="request_boundary",
        effect_boundary_key="tool_related_effect_boundary",
        provenance_tag="slice9_negative",
        version_tag="v1",
        **{field_name: True},
    )
    check(not validate_predicate_frame_record(unsafe).passed, f"predicate unsafe flag rejected: {field_name}")

unsafe_speech_cases = (
    ("draft_request_boundary", "send_permission"),
    ("memory_request_boundary", "memory_write_permission"),
    ("implementation_request_boundary", "tool_invocation_permission"),
    ("command_boundary", "command_permission"),
)
for act_type, flag in unsafe_speech_cases:
    unsafe = SpeechActBoundaryRecord(
        speech_act_key=f"unsafe_{act_type}",
        act_type=act_type,
        namespace="aiweb:core",
        source_ref="slice9_negative",
        provenance_tag="slice9_negative",
        version_tag="v1",
        **{flag: True},
    )
    check(not validate_speech_act_record(unsafe).passed, f"speech permission rejected: {act_type}:{flag}")

unsafe_role = RoleBoundaryRecord(
    role_key="unsafe_role",
    frame_key="unsafe_frame",
    role_type="agent_boundary",
    namespace="aiweb:core",
    concept_boundary_refs=("concept_agent_boundary",),
    provenance_tag="slice9_negative",
    version_tag="v1",
    role_resolution=True,
)
check(not validate_role_record(unsafe_role).passed, "role resolver flag is rejected")
check(missing_role.presence_state == "missing_boundary", "missing role remains explicit")
check(unknown_role.unknown_state == "unknown_boundary", "unknown role remains unknown")
check(unknown_predicate.unknown_state == "unknown_boundary", "unknown predicate remains unknown")

unsafe_effect = EffectBoundaryRecord(
    effect_key="unsafe_effect",
    effect_type="delivery_related_effect_boundary",
    namespace="aiweb:core",
    provenance_tag="slice9_negative",
    version_tag="v1",
    side_effect_allowed=True,
)
check(not validate_effect_boundary_record(unsafe_effect).passed, "effect category does not allow side effect")
check(effect.effect_authorized is False, "effect category does not authorize effect")

verifier_passes, verifier_failures = run_verification(REPO)
check(not verifier_failures, "verifier sample checks pass")

print("PASSES:")
for item in passes:
    print(f"  PASS - {item}")
print("FAILURES:")
for item in failures:
    print(f"  FAIL - {item}")
if failures:
    print("VERDICT: FAIL - behavior test failed")
    raise SystemExit(1)
print("VERDICT: PASS - behavior test passed within Slice 9 scope")
