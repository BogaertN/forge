"""Slice 43E deterministic drift and materiality classification authority.

This increment consumes only validated Slice 43D comparison findings bound to
the exact accepted Slice 43C/42 ancestry. It classifies admitted drift kinds and
records deterministic materiality findings. It grants no Echo disposition,
rejection, containment, text repair, delivery, model, route, memory, tool,
action, MSM mutation, or GP-014 authority.
"""

from __future__ import annotations

SLICE43E_ACCEPTED_PARENT_HEAD = "26e8c30724dde17709203411a95f63dcf65a380b"
SLICE43E_ACCEPTED_PARENT_TREE = "785690cd3fe8b3437fce226edac5472659db3f7c"
SLICE43E_ACCEPTED_PARENT_SUBJECT = (
    "Slice 43D meaning-preservation comparison"
)
SLICE43E_COMMIT_SUBJECT = (
    "Slice 43E drift finding materiality and classification"
)

SLICE43E_SCHEMA_VERSION = (
    "aiweb-slice43e-drift-materiality-classification-v1"
)
SLICE43E_PROFILE_VERSION = (
    "aiweb-slice43e-exact-comparison-finding-classification-profile-v1"
)
SLICE43E_SPEC_VERSION = "v1.0.0"
DIGEST_ALGORITHM = "sha256"
REQUESTED_OPERATION = "classify-admitted-drift-and-materiality"

DRIFT_KIND_VALUES = (
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
    "unsupported_surface_addition",
)

MATERIALITY_VALUES = (
    "not_applicable",
    "non_material",
    "material",
    "unsupported",
    "conflicted",
    "indeterminate",
)

CLASSIFICATION_STATE_VALUES = (
    "no_drift",
    "drift_classified",
    "classification_unsupported",
    "classification_conflicted",
    "classification_indeterminate",
)

MATERIAL_DRIFT_KIND_VALUES = (
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

CONTROLLED_NON_MATERIAL_SURFACE_PREFIXES = (
    "surface:formatting:",
    "surface:punctuation:",
    "surface:whitespace:",
)

EXACT_ACCEPTED_SLICE43D_IDS = (
    (
        "request",
        "slice43d_meaning_preservation_comparison_request:"
        "f78d2cd331f0b9f483ee2ea344ab0a469fcb30c8abbd73a29c5234d2be4c887d",
    ),
    (
        "result",
        "slice43d_meaning_preservation_comparison_result:"
        "be8cc7ecbb5c443e71bd81e165834d13a7bf946cd300ab480227e8a04172f1d1",
    ),
    (
        "package",
        "slice43d_meaning_preservation_comparison_package:"
        "813dd09572f8421e2559b1ec057c4f02219fe43c350f7d554b6ca5316901bf4d",
    ),
)
EXACT_ACCEPTED_SLICE43D_ID_MAP = dict(EXACT_ACCEPTED_SLICE43D_IDS)

SUPPORTED_PREDECESSOR_SCHEMA_VERSIONS = (
    ("slice43d", "aiweb-slice43d-meaning-preservation-comparison-v1"),
    ("slice43c", "aiweb-slice43c-authorized-meaning-proposed-expression-admission-v1"),
    ("slice43b", "aiweb-slice43b-rmc-echo-governance-v1"),
    ("slice43a", "aiweb-slice43a-rmc-echo-core-schema-v1"),
    ("slice42h", "aiweb-slice42h-disabled-outward-expression-closeout-v1"),
    ("msm", "MSM-v1"),
)

CLASSIFICATION_RULE_REFS = tuple(
    (
        kind,
        f"slice43e-drift-rule:{kind}:exact-comparison-custody-classification",
    )
    for kind in DRIFT_KIND_VALUES
)
CLASSIFICATION_RULE_REF_MAP = dict(CLASSIFICATION_RULE_REFS)

MATERIALITY_RULE_REFS = (
    (
        "not_applicable",
        "slice43e-materiality-rule:no-drift-not-applicable",
    ),
    (
        "non_material",
        "slice43e-materiality-rule:controlled-surface-only-non-material",
    ),
    (
        "material",
        "slice43e-materiality-rule:admitted-material-drift-kind",
    ),
    (
        "unsupported",
        "slice43e-materiality-rule:comparison-unsupported",
    ),
    (
        "conflicted",
        "slice43e-materiality-rule:comparison-conflicted",
    ),
    (
        "indeterminate",
        "slice43e-materiality-rule:materiality-indeterminate",
    ),
)
MATERIALITY_RULE_REF_MAP = dict(MATERIALITY_RULE_REFS)

PERMANENT_AUTHORITY_ZERO = (
    "classification does not decide PASSED, REJECTED or CONTAINED",
    "Echo disposition, rejection and containment remain deferred to Slice 43F",
    "automatic correction, repair and expression rewriting are prohibited",
    "MSM-v1 validation-link integration remains deferred to Slice 43G",
    "bootstrap integration and Slice 43 closeout remain deferred to Slice 43H",
    "delivery, route, API, network, filesystem, memory-write, tool and action authority are absent",
    "LLM, EchoForge, embedding, vector, RAG, similarity, neural parser and hidden classifier authority are absent",
    "truth, evidence, permission and execution authority are absent",
    "comparison source and proposed values remain immutable",
    "GP-014 is not superseded",
)

__all__ = tuple(name for name in globals() if name.isupper())
