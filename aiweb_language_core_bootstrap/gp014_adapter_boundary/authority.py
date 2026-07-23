"""Binding authority for the Slice 45 GP-014 adapter boundary."""
from __future__ import annotations

from typing import Final

SLICE45_SCHEMA_VERSION: Final[str] = "aiweb-slice45-gp014-adapter-boundary-v1"
SLICE45_SPEC_ID: Final[str] = "canonical-roadmap:slice45"
SLICE45_SPEC_VERSION: Final[str] = "v1.0.0"
SLICE45_COMMIT_SUBJECT: Final[str] = 'Slice 45 bounded GP-014 adapter boundary'

ACCEPTED_PARENT_HEAD: Final[str] = 'd374ebb8c09ef0f74df93177ea08bffb5e66791d'
ACCEPTED_PARENT_TREE: Final[str] = 'c284950f6100a08a049a7f627da4a114ed75d640'
ACCEPTED_PARENT_SUBJECT: Final[str] = 'Slice 43H disabled bootstrap integration and Slice 43 closeout'

GP014_BUILD_ID: Final[str] = "LANG-EXPR-001-GP-014-RMC-OPERATOR-GUIDED-GENERATIVE-LANGUAGE-REALIZER"
GP014_REALIZER_SCHEMA_VERSION: Final[str] = "aiweb_rmc_operator_guided_math_expression_realizer_v1_gp014"
GP014_RENDERER_SCHEMA_VERSION: Final[str] = "aiweb_symbolic_math_rmc_renderer_echo_binding_v2_gp014"
GP014_EXPRESSION_LEXICON_AUTHORITY_CLASS: Final[str] = "BOUNDED_VERSIONED_EXPRESSION_LEXICON_NOT_CORPUS"

GP014_SUPPORTED_OPERATION_FAMILIES: Final[tuple[str, ...]] = (
    "differentiation",
    "expansion",
    "factoring",
    "integration",
    "limits",
    "simplification",
    "trigonometric_expansion",
    "trigonometric_simplification",
)

GP014_ALLOWED_SOURCE_STATUSES: Final[tuple[str, ...]] = (
    "ANSWERED",
    "ECHO_REJECTED",
    "GATE_BLOCKED",
    "REFUSED_UNLEARNED",
)

REQUESTED_OPERATION: Final[str] = "invoke_unchanged_gp014_bounded_lane"
ADAPTER_SCOPE: Final[str] = "unchanged_gp014_bounded_question_passthrough"
MAX_QUESTION_CHARACTERS: Final[int] = 600

STATUS_REFUSED_DISABLED: Final[str] = "REFUSED_ADAPTER_DISABLED"
STATUS_HELD_INVALID_STATE: Final[str] = "HELD_INVALID_ADAPTER_STATE"
STATUS_HELD_INVALID_REQUEST: Final[str] = "HELD_INVALID_ADAPTER_REQUEST"
STATUS_HELD_GP014_IDENTITY: Final[str] = "HELD_GP014_IDENTITY_MISMATCH"
STATUS_HELD_GP014_RESULT: Final[str] = "HELD_GP014_RESULT_INVALID"
STATUS_CONTAINED_SOURCE_FAILURE: Final[str] = "CONTAINED_GP014_SOURCE_FAILURE"
STATUS_COMPLETED_ANSWERED: Final[str] = "COMPLETED_GP014_ANSWERED"
STATUS_COMPLETED_CONTAINED: Final[str] = "COMPLETED_GP014_CONTAINED"

GP014_MODULE_NAME: Final[str] = "rmc_engine_v1.general_pipeline.gp014_operator_guided_language_realizer"
GP014_VERTICAL_SLICE_MODULE_NAME: Final[str] = "rmc_engine_v1.general_pipeline.symbolic_math_language_vertical_slice"
GP014_REALIZER_MODULE_NAME: Final[str] = "rmc_engine_v1.general_pipeline.symbolic_math_operator_language_realizer"
GP015_MODULE_NAME: Final[str] = "rmc_engine_v1.general_pipeline.gp015_ask_forge_trace_surface"

__all__ = tuple(name for name in globals() if not name.startswith("_"))
