"""Slice 43D deterministic meaning-preservation comparison authority.

This increment consumes only the exact accepted Slice 43C admission result and
its exact accepted Slice 42 ancestry. It creates dimension-specific comparison
findings only. It grants no aggregate Echo disposition, drift classification,
materiality decision, rejection, containment, correction, delivery, model,
route, memory, tool, action, MSM mutation, or GP-014 authority.
"""

from __future__ import annotations

SLICE43D_ACCEPTED_PARENT_HEAD = "6f2cbafc18ef9eff259bca038d189f1bbe7fc4c6"
SLICE43D_ACCEPTED_PARENT_TREE = "c378cb1cd0be715160a9f919ea01815799ee4f56"
SLICE43D_ACCEPTED_PARENT_SUBJECT = (
    "Slice 43C authorized meaning and proposed-expression admission"
)
SLICE43D_COMMIT_SUBJECT = (
    "Slice 43D deterministic meaning-preservation comparison findings"
)

SLICE43D_SCHEMA_VERSION = (
    "aiweb-slice43d-meaning-preservation-comparison-v1"
)
SLICE43D_PROFILE_VERSION = (
    "aiweb-slice43d-exact-admitted-source-comparison-profile-v1"
)
SLICE43D_SPEC_VERSION = "v1.0.0"
DIGEST_ALGORITHM = "sha256"
REQUESTED_OPERATION = "compare-admitted-meaning-preservation"

COMPARISON_DIMENSION_VALUES = (
    "semantic_content",
    "communicative_purpose",
    "claim_status",
    "scope",
    "certainty",
    "evidence_status",
    "caveats_and_limitations",
    "refusal_state",
    "unresolved_conditions",
    "action_status",
    "memory_status",
    "delivery_status",
    "required_next_step_or_hold_status",
)

FINDING_OUTCOME_VALUES = (
    "preserved",
    "changed",
    "missing",
    "unsupported",
    "conflicted",
    "indeterminate",
)

SNAPSHOT_SIDE_VALUES = ("source", "proposed_expression")

EXACT_ACCEPTED_SLICE43C_IDS = (
    (
        "request",
        "slice43c_source_admission_request:"
        "f82be4bd8cd80a0394ab263fc2290610aca42ed0b69ca990e5a28bcea84285a5",
    ),
    (
        "result",
        "slice43c_source_admission_result:"
        "7ad6af0a3ac257c63af99489dd5991528157377e5d809ed2f66b5dfcf35a3990",
    ),
    (
        "package",
        "slice43c_echo_validation_admission_package:"
        "f6b710451bb4a33f36f8b11dfcb5153f3bc13cf4a8c952a38fa7cac0b6680f06",
    ),
    (
        "authorized_meaning_admission",
        "slice43c_authorized_meaning_admission:"
        "001feac3d9973ec818c5802d4d2b30ca97cd3fbe12cf030a680c5a71886de50c",
    ),
    (
        "proposed_expression_admission",
        "slice43c_proposed_expression_admission:"
        "b38e079e384ce603a4461c75fda89df9e2f6b11cace43fc9312df7905385360a",
    ),
    (
        "validation_input_boundary",
        "rmc_echo_validation_input_boundary:"
        "cb6b6774d0dec6e749975bbd463adfa8efb2cc6eb65d0ce0f9f8122e989d17d7",
    ),
)
EXACT_ACCEPTED_SLICE43C_ID_MAP = dict(EXACT_ACCEPTED_SLICE43C_IDS)

SUPPORTED_PREDECESSOR_SCHEMA_VERSIONS = (
    (
        "slice43c",
        "aiweb-slice43c-authorized-meaning-proposed-expression-admission-v1",
    ),
    ("slice43a", "aiweb-slice43a-rmc-echo-core-schema-v1"),
    ("slice43b", "aiweb-slice43b-rmc-echo-governance-v1"),
    ("slice42c", "aiweb-slice42c-authorized-meaning-admission-expression-eligibility-v1"),
    ("slice42d", "aiweb-slice42d-preservation-obligation-projection-v1"),
    ("slice42e", "aiweb-slice42e-controlled-expression-plan-construction-v1"),
    ("slice42f", "aiweb-slice42f-deterministic-surface-realization-v1"),
    ("slice42g", "aiweb-language-core-slice42g-msm-outward-expression-integration-v1"),
    ("slice42h", "aiweb-slice42h-disabled-outward-expression-closeout-v1"),
    ("msm", "MSM-v1"),
)

COMPARISON_RULE_REFS = tuple(
    (
        dimension,
        f"slice43d-comparison-rule:{dimension}:exact-custody-value-comparison",
    )
    for dimension in COMPARISON_DIMENSION_VALUES
)
COMPARISON_RULE_REF_MAP = dict(COMPARISON_RULE_REFS)

PERMANENT_AUTHORITY_ZERO = (
    "findings do not decide overall PASS, REJECTED or CONTAINED",
    "drift classification and materiality remain deferred to Slice 43E",
    "Echo disposition, rejection and containment remain deferred to Slice 43F",
    "automatic correction, repair and expression rewriting are prohibited",
    "MSM-v1 validation-link integration remains deferred to Slice 43G",
    "bootstrap integration and Slice 43 closeout remain deferred to Slice 43H",
    "delivery, route, API, network, filesystem, memory-write, tool and action authority are absent",
    "LLM, EchoForge, embedding, vector, RAG, similarity, neural parser and hidden classifier authority are absent",
    "truth, evidence, permission and execution authority are absent",
    "GP-014 is not superseded",
)

__all__ = tuple(name for name in globals() if name.isupper())
