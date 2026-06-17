"""AI.Web Slice 9 predicate-role frame boundary scaffold.

Additive, deterministic, inert boundary records only.
"""

from .effect_boundary import (
    EffectBoundaryRecord,
    demo_effect_boundary_record,
    demo_unknown_effect_boundary_record,
    validate_effect_boundary_record,
)
from .predicate_frame import (
    DEPENDENCY_CHANGE,
    RUNTIME_EFFECT,
    SCHEMA_VERSION,
    SCOPE_STATUS,
    PredicateFrameBoundaryRecord,
    ValidationIssue,
    ValidationReport,
    demo_predicate_frame_record,
    demo_unknown_predicate_frame_record,
    predicate_role_scope_record,
    stable_boundary_id,
    validate_predicate_frame_record,
)
from .roles import (
    RoleBoundaryRecord,
    demo_missing_role_record,
    demo_role_record,
    demo_unknown_role_record,
    validate_role_record,
)
from .speech_act import (
    SpeechActBoundaryRecord,
    demo_command_speech_act_record,
    demo_implementation_request_speech_act_record,
    demo_memory_request_speech_act_record,
    demo_speech_act_record,
    validate_speech_act_record,
)

__all__ = [
    "DEPENDENCY_CHANGE",
    "RUNTIME_EFFECT",
    "SCHEMA_VERSION",
    "SCOPE_STATUS",
    "EffectBoundaryRecord",
    "PredicateFrameBoundaryRecord",
    "RoleBoundaryRecord",
    "SpeechActBoundaryRecord",
    "ValidationIssue",
    "ValidationReport",
    "demo_command_speech_act_record",
    "demo_effect_boundary_record",
    "demo_implementation_request_speech_act_record",
    "demo_memory_request_speech_act_record",
    "demo_missing_role_record",
    "demo_predicate_frame_record",
    "demo_role_record",
    "demo_speech_act_record",
    "demo_unknown_effect_boundary_record",
    "demo_unknown_predicate_frame_record",
    "demo_unknown_role_record",
    "predicate_role_scope_record",
    "stable_boundary_id",
    "validate_effect_boundary_record",
    "validate_predicate_frame_record",
    "validate_role_record",
    "validate_speech_act_record",
]
