"""Stable Slice 39A package and schema identity constants.

Slice 39A defines constructor-shape contracts only.  Deterministic identity
calculation, validation, lifecycle transitions, candidate construction,
manifest adaptation, persistence, routes, actions, and gate evaluation remain
outside this increment.
"""

from typing import Final


PACKAGE_NAME: Final[str] = (
    "aiweb_language_core_bootstrap.candidate_meaning_construction"
)
PACKAGE_ID: Final[str] = "aiweb-forge-candidate-meaning-construction"
SCHEMA_NAME: Final[str] = "CandidateMeaningConstruction"
SCHEMA_ABBREVIATION: Final[str] = "CMC-v1"
SCHEMA_VERSION: Final[str] = "aiweb-candidate-meaning-construction-v1"
SPEC_ID: Final[str] = "aiweb-slice39a-candidate-meaning-core-schema"
SPEC_VERSION: Final[str] = "aiweb-slice39a-candidate-meaning-core-schema-v1"

ACCEPTED_PARENT_HEAD: Final[str] = (
    "bb22f0fff6b64deaeeae8285dfabdbdd586d8473"
)
ACCEPTED_PARENT_TREE: Final[str] = (
    "12131cc607c1dd293b3e741443d42ad69ba83063"
)
ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 38H disabled bootstrap integration and Slice 38 closeout"
)

IDENTITY_SCHEMA_ID: Final[str] = "aiweb.slice39a.candidate_meaning_identity.v1"
CONTENT_SCHEMA_ID: Final[str] = "aiweb.slice39a.candidate_meaning_content.v1"
PROVENANCE_SCHEMA_ID: Final[str] = (
    "aiweb.slice39a.candidate_meaning_provenance.v1"
)
ALTERNATIVE_REFERENCE_SCHEMA_ID: Final[str] = (
    "aiweb.slice39a.candidate_meaning_alternative_reference.v1"
)
CONSTRUCTION_RECEIPT_SCHEMA_ID: Final[str] = (
    "aiweb.slice39a.candidate_meaning_construction_receipt.v1"
)
STATE_SCHEMA_ID: Final[str] = "aiweb.slice39a.candidate_meaning_state.v1"
