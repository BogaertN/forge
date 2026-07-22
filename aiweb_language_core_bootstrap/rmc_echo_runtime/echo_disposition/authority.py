"""Slice 43F deterministic Echo disposition authority.

This increment consumes only exact validated Slice 43E drift-classification and
materiality findings. It creates one deterministic PASSED, REJECTED or
CONTAINED disposition and the corresponding rejection or containment custody
when applicable. It does not rewrite the candidate, repair wording, authorize
or perform delivery, call EchoForge, call an LLM, modify MSM-v1, invoke routes,
tools or actions, write memory, or silently remove drift.
"""

from __future__ import annotations

SLICE43F_ACCEPTED_PARENT_HEAD = "2192c7ffc6df7f936ead4760f25a0f027dcffad7"
SLICE43F_ACCEPTED_PARENT_TREE = "93ed56e1db485d611c0a434387eacec81a0149aa"
SLICE43F_ACCEPTED_PARENT_SUBJECT = (
    "Slice 43E drift finding materiality and classification"
)
SLICE43F_COMMIT_SUBJECT = "Slice 43F Echo disposition rejection and containment"

SLICE43F_SCHEMA_VERSION = "aiweb-slice43f-echo-disposition-v1"
SLICE43F_PROFILE_VERSION = (
    "aiweb-slice43f-exact-drift-materiality-disposition-profile-v1"
)
SLICE43F_SPEC_VERSION = "v1.0.0"
DIGEST_ALGORITHM = "sha256"
REQUESTED_OPERATION = "decide-echo-disposition-rejection-containment"

ECHO_DISPOSITION_VALUES = (
    "PASSED",
    "REJECTED",
    "CONTAINED",
)

DISPOSITION_STATE_VALUES = (
    "all_material_obligations_pass",
    "deterministic_echo_law_violation",
    "incomplete_authority_contained",
)

INCOMPLETE_AUTHORITY_MATERIALITY_VALUES = (
    "unsupported",
    "conflicted",
    "indeterminate",
)

# Exact Slice 43E kinds that establish a deterministic Echo-law violation when
# their materiality is MATERIAL. Unsupported surface addition is intentionally
# excluded: controlled surface-only additions are NON_MATERIAL, and any other
# surface-addition materiality remains INDETERMINATE and is therefore contained.
DETERMINISTIC_ECHO_LAW_VIOLATION_DRIFT_KIND_VALUES = (
    "omitted_meaning",
    "claim_strengthening",
    "scope_expansion",
    "certainty_upgrade",
    "evidence_status_upgrade",
    "caveat_omission",
    "refusal_softening",
    "ambiguity_erasure",
    "unresolved_state_erasure",
    "invented_fact",
    "invented_evidence",
    "authority_escalation",
    "action_status_distortion",
    "memory_status_distortion",
    "delivery_status_distortion",
    "ancestry_mismatch",
)

EXACT_ACCEPTED_SLICE43E_IDS = (
    (
        "request",
        "slice43e_drift_classification_request:"
        "6dcb65e550221292a8e655acbb97a8d04091116a6d2c504635079b47ba34fe64",
    ),
    (
        "result",
        "slice43e_drift_classification_result:"
        "8051bfe8dfeef4b451ffe557f92c0afc549f98679ae0b068170e563b3a89fde9",
    ),
    (
        "package",
        "slice43e_drift_classification_package:"
        "f60395c28607aa981762fad7c7f302f1e639b174b45c3d4ef1a7aa824e173b24",
    ),
)
EXACT_ACCEPTED_SLICE43E_ID_MAP = dict(EXACT_ACCEPTED_SLICE43E_IDS)

SUPPORTED_PREDECESSOR_SCHEMA_VERSIONS = (
    ("slice43e", "aiweb-slice43e-drift-materiality-classification-v1"),
    ("slice43d", "aiweb-slice43d-meaning-preservation-comparison-v1"),
    ("slice43c", "aiweb-slice43c-authorized-meaning-proposed-expression-admission-v1"),
    ("slice43b", "aiweb-slice43b-rmc-echo-governance-v1"),
    ("slice43a", "aiweb-slice43a-rmc-echo-core-schema-v1"),
    ("slice42h", "aiweb-slice42h-disabled-outward-expression-closeout-v1"),
    ("msm", "MSM-v1"),
)

DISPOSITION_LAW_REFS = (
    (
        "PASSED",
        "slice43f-disposition-law:all-material-obligations-pass-no-incomplete-authority",
    ),
    (
        "REJECTED",
        "slice43f-disposition-law:exact-material-echo-law-violation",
    ),
    (
        "CONTAINED",
        "slice43f-disposition-law:drift-or-incomplete-authority-blocks-progression",
    ),
)
DISPOSITION_LAW_REF_MAP = dict(DISPOSITION_LAW_REFS)

PRECEDENCE_RULE_REF = (
    "slice43f-precedence-law:incomplete-authority-containment-precedes-rejection"
)
ALL_FINDINGS_RETENTION_RULE_REF = (
    "slice43f-retention-law:retain-all-comparison-drift-materiality-and-ancestry"
)
NO_SILENT_DRIFT_REMOVAL_RULE_REF = (
    "slice43f-retention-law:no-silent-drift-removal-downgrade-or-suppression"
)

REJECTION_LAW_REFS = tuple(
    (
        kind,
        f"slice43f-rejection-law:{kind}:material-deterministic-echo-violation",
    )
    for kind in DETERMINISTIC_ECHO_LAW_VIOLATION_DRIFT_KIND_VALUES
)
REJECTION_LAW_REF_MAP = dict(REJECTION_LAW_REFS)

CONTAINMENT_LAW_REFS = (
    (
        "unsupported",
        "slice43f-containment-law:unsupported-authority-blocks-progression",
    ),
    (
        "conflicted",
        "slice43f-containment-law:conflicted-authority-blocks-progression",
    ),
    (
        "indeterminate",
        "slice43f-containment-law:indeterminate-authority-blocks-progression",
    ),
)
CONTAINMENT_LAW_REF_MAP = dict(CONTAINMENT_LAW_REFS)

PERMANENT_AUTHORITY_ZERO = (
    "candidate rewriting, wording repair, correction and replacement expression generation are absent",
    "all drift and incomplete-authority findings remain retained without suppression",
    "disposition is not truth, evidence sufficiency, permission, execution or delivery authority",
    "delivery authorization and delivery performance are absent",
    "EchoForge invocation and delegation are absent",
    "LLM, embedding, vector, RAG, similarity, neural parser and hidden classifier authority are absent",
    "route, API, network, filesystem, memory-write, tool and action authority are absent",
    "MSM-v1 validation-link integration and schema modification remain deferred to Slice 43G",
    "bootstrap integration and Slice 43 closeout remain deferred to Slice 43H",
    "GP-014 is not superseded",
)

__all__ = tuple(name for name in globals() if name.isupper())
