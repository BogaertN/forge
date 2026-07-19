"""Stable Slice 40A package and schema identity constants.

Slice 40A defines immutable verbal-cognition gate review record shapes only.
Deterministic identity calculation, validation, lifecycle transitions, gate
family evaluation, gate composition, MSM-v1 integration, selected meaning,
and every consequence-bearing authority remain outside this increment.
"""

from typing import Final


PACKAGE_NAME: Final[str] = (
    "aiweb_language_core_bootstrap.verbal_cognition_gate_runtime"
)
PACKAGE_ID: Final[str] = "aiweb-forge-verbal-cognition-gate-runtime"
SCHEMA_NAME: Final[str] = "VerbalCognitionGateCore"
SCHEMA_ABBREVIATION: Final[str] = "VCG-v1"
SCHEMA_VERSION: Final[str] = "aiweb-verbal-cognition-gate-core-v1"
SPEC_ID: Final[str] = "aiweb-slice40a-verbal-cognition-gate-core-schema"
SPEC_VERSION: Final[str] = "aiweb-slice40a-verbal-cognition-gate-core-schema-v1"

ACCEPTED_PARENT_HEAD: Final[str] = "643686b8664fe938b8e87e6335cf6ecc3c87e1d3"
ACCEPTED_PARENT_TREE: Final[str] = "a83b0561ff7858d0ea69db0f92ed6494fcde26aa"
ACCEPTED_PARENT_SUBJECT: Final[str] = "Slice 39H disabled bootstrap integration closeout"

GATE_IDENTITY_SCHEMA_ID: Final[str] = (
    "aiweb.slice40a.verbal_cognition_gate_identity.v1"
)
GATE_PROFILE_SCHEMA_ID: Final[str] = (
    "aiweb.slice40a.verbal_cognition_gate_profile_identity.v1"
)
CANDIDATE_INPUT_REFERENCE_SCHEMA_ID: Final[str] = (
    "aiweb.slice40a.gate_candidate_input_reference.v1"
)
REQUIREMENT_REFERENCE_SCHEMA_ID: Final[str] = (
    "aiweb.slice40a.gate_requirement_reference.v1"
)
REASON_GROUND_SCHEMA_ID: Final[str] = (
    "aiweb.slice40a.gate_reason_ground.v1"
)
TRACE_REFERENCE_SCHEMA_ID: Final[str] = (
    "aiweb.slice40a.gate_trace_reference.v1"
)
PROVENANCE_REFERENCE_SCHEMA_ID: Final[str] = (
    "aiweb.slice40a.gate_provenance_reference.v1"
)
LIMITATION_REFERENCE_SCHEMA_ID: Final[str] = (
    "aiweb.slice40a.gate_limitation_reference.v1"
)
REVIEW_RECORD_SCHEMA_ID: Final[str] = (
    "aiweb.slice40a.verbal_cognition_gate_review_record.v1"
)
