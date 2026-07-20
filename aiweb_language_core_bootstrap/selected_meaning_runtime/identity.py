"""Stable Slice 41A package and schema identity constants.

Slice 41A defines immutable selected-meaning runtime record shapes and
authority contracts only.  Deterministic identity calculation, validation,
canonical serialization, lifecycle transitions, eligibility evaluation,
candidate selection, selected-meaning construction, MSM-v1 integration, and
bootstrap integration remain outside this increment.
"""

from typing import Final


PACKAGE_NAME: Final[str] = (
    "aiweb_language_core_bootstrap.selected_meaning_runtime"
)
PACKAGE_ID: Final[str] = "aiweb-forge-selected-meaning-runtime"
SCHEMA_NAME: Final[str] = "SelectedMeaningRuntimeCore"
SCHEMA_ABBREVIATION: Final[str] = "SMR-v1"
SCHEMA_VERSION: Final[str] = "aiweb-selected-meaning-runtime-core-v1"
SPEC_ID: Final[str] = "aiweb-slice41a-selected-meaning-runtime-core-schema"
SPEC_VERSION: Final[str] = (
    "aiweb-slice41a-selected-meaning-runtime-core-schema-v1"
)

ACCEPTED_PARENT_HEAD: Final[str] = "fcc6b57e62e95cbfe2dbc80b88a212432c681907"
ACCEPTED_PARENT_TREE: Final[str] = "55dc8ebf863c2df547ae31b38e3445b25f6cc22a"
ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 40H MSM gate integration disabled bootstrap and Slice 40 closeout"
)

SELECTION_CANDIDATE_CUSTODY_SCHEMA_ID: Final[str] = (
    "aiweb.slice41a.selection_candidate_custody.v1"
)
GATE_CUSTODY_REFERENCE_SCHEMA_ID: Final[str] = (
    "aiweb.slice41a.gate_custody_reference.v1"
)
SELECTION_AUTHORITY_REQUIREMENT_SCHEMA_ID: Final[str] = (
    "aiweb.slice41a.selection_authority_requirement.v1"
)
ALTERNATIVE_CANDIDATE_CUSTODY_SCHEMA_ID: Final[str] = (
    "aiweb.slice41a.alternative_candidate_custody.v1"
)
UNRESOLVED_STATE_CUSTODY_SCHEMA_ID: Final[str] = (
    "aiweb.slice41a.unresolved_state_custody.v1"
)
INHERITED_LIMITATION_CUSTODY_SCHEMA_ID: Final[str] = (
    "aiweb.slice41a.inherited_limitation_custody.v1"
)
SELECTION_ELIGIBILITY_STATUS_SCHEMA_ID: Final[str] = (
    "aiweb.slice41a.selection_eligibility_status.v1"
)
SELECTED_MEANING_DECISION_STATUS_SCHEMA_ID: Final[str] = (
    "aiweb.slice41a.selected_meaning_decision_status.v1"
)
SELECTION_TRACE_BOUNDARY_SCHEMA_ID: Final[str] = (
    "aiweb.slice41a.selection_trace_boundary.v1"
)
SELECTION_RECEIPT_BOUNDARY_SCHEMA_ID: Final[str] = (
    "aiweb.slice41a.selection_receipt_boundary.v1"
)
SELECTED_MEANING_RUNTIME_SCHEMA_RECORD_SCHEMA_ID: Final[str] = (
    "aiweb.slice41a.selected_meaning_runtime_schema_record.v1"
)
