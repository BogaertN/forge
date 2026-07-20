"""Authority constants for Slice 41F disabled bootstrap integration and closeout."""
from __future__ import annotations

from typing import Final

SLICE41F_SCHEMA_VERSION: Final[str] = (
    "aiweb-slice41f-disabled-selected-meaning-closeout-v1"
)
SLICE41F_SPEC_ID: Final[str] = "canonical-roadmap:slice41f"
SLICE41F_SPEC_VERSION: Final[str] = "v1.0.0"
SLICE41F_PROFILE_KEY: Final[str] = (
    "disabled_explicit_fixture_only_selected_meaning_closeout"
)
SLICE41F_PROFILE_VERSION: Final[str] = "v1.0.0"
SLICE41F_RECEIPT_VERSION: Final[str] = "v1.0.0"
SLICE41F_ACCEPTANCE_RECORD_VERSION: Final[str] = "v1.0.0"
SLICE41F_ROLLBACK_METADATA_VERSION: Final[str] = "v1.0.0"

PRE_SLICE41_COMMIT: Final[str] = "fcc6b57e62e95cbfe2dbc80b88a212432c681907"
PRE_SLICE41_TREE: Final[str] = "55dc8ebf863c2df547ae31b38e3445b25f6cc22a"
PRE_SLICE41_SUBJECT: Final[str] = (
    "Slice 40H MSM gate integration disabled bootstrap and Slice 40 closeout"
)

SLICE41E_ACCEPTED_HEAD: Final[str] = (
    "1aa5513e14593e4e2d510161f3204a38536d87ea"
)
SLICE41E_ACCEPTED_PARENT: Final[str] = (
    "95ba97835634d35f097267dae20d555b2b80bbcd"
)
SLICE41E_ACCEPTED_TREE: Final[str] = (
    "aca30bba4b2b52f8cac6f61f697185a91c534c3d"
)
SLICE41E_ACCEPTED_SUBJECT: Final[str] = (
    "Slice 41E MSM-v1 selected meaning integration and custody"
)
SLICE41F_COMMIT_SUBJECT: Final[str] = (
    "Slice 41F disabled bootstrap integration and Slice 41 closeout"
)

REQUESTED_OPERATION: Final[str] = (
    "run_exact_slice41_selected_meaning_fixture_and_close_slice41"
)
REASON_DISABLED: Final[str] = (
    "slice41f_disabled_by_default_explicit_offline_enable_required"
)

SLICE41_INCREMENT_LABELS: Final[tuple[str, ...]] = (
    "41A",
    "41B",
    "41C",
    "41D",
    "41E",
    "41F",
)
SLICE41_ACCEPTED_CHAIN: Final[tuple[str, ...]] = (
    "41A core schema and authority contract",
    "41B deterministic validation identity versioning and lifecycle",
    "41C deterministic selection eligibility evaluation",
    "41D selected meaning construction and alternative preservation",
    "41E additive MSM-v1 selected meaning integration and custody",
    "41F disabled bootstrap integration and Slice 41 closeout",
)
SLICE41_ACCEPTED_SCOPE: Final[tuple[str, ...]] = (
    "bounded selected-meaning runtime schema and authority custody",
    "deterministic validation identity versioning and lifecycle",
    "candidate-specific selection eligibility evaluation",
    "selected-meaning construction with alternative and unresolved custody",
    "immutable additive MSM-v1 selected-meaning successor integration",
    "disabled-by-default explicit accepted-static-fixture bootstrap closeout",
)
SLICE41_DEFERRED_SCOPE: Final[tuple[str, ...]] = (
    "Slice 42 controlled outward expression",
    "governed outward meaning creation",
    "expression validation or delivery links",
    "truth or evidence validity claims",
    "permission capability availability or execution",
    "routes APIs tools actions memory rendering or delivery",
    "network filesystem or external-resource authority",
    "production readiness",
)
SLICE41_PERMANENT_BOUNDARIES: Final[tuple[str, ...]] = (
    "selected meaning is bounded semantic custody only",
    "selection is not truth",
    "selection is not evidence",
    "selection is not permission",
    "selection is not execution",
    "selection is not outward expression",
    "selection is not delivery",
    "selection authority is exact and receipt-bound",
    "selected candidate identity remains exact",
    "selected candidate lineage remains exact",
    "candidate semantic content remains exact",
    "all candidate meanings remain retained",
    "all non-selection outcomes remain retained",
    "all material alternatives remain retained",
    "all unresolved state remains retained",
    "Slice 40H gate custody remains retained",
    "Slice 41D construction custody remains retained",
    "Slice 41E MSM custody remains retained",
    "MSM-v1 schema is not rewritten",
    "bootstrap is disabled by default",
    "bootstrap requires explicit invocation",
    "bootstrap accepts only closed static fixtures",
    "bootstrap is offline and in memory",
    "bootstrap is deterministic and source preserving",
    "bootstrap creates no route or API",
    "bootstrap performs no network access",
    "bootstrap performs no filesystem write",
    "bootstrap performs no memory write",
    "bootstrap invokes no tool or action",
    "bootstrap performs no rendering or delivery",
    "Slice 42 remains unstarted",
)
SLICE41_PROHIBITED_AUTHORITY: Final[tuple[str, ...]] = (
    "automatic bootstrap activation",
    "arbitrary raw-text interpretation",
    "candidate ranking or rescoring",
    "semantic enrichment or deletion",
    "alternative deletion",
    "unresolved-state deletion",
    "MSM-v1 schema replacement",
    "automatic migration",
    "governed result creation",
    "governed outward meaning creation",
    "expression link creation",
    "validation link creation",
    "delivery or containment link creation",
    "truth determination",
    "evidence validation",
    "permission grant",
    "execution authorization",
    "capability availability creation",
    "route or API creation",
    "tool invocation",
    "action performance",
    "memory read or write",
    "rendering",
    "delivery",
    "filesystem read or write",
    "network access",
    "external resource loading",
    "language model authority",
    "embedding vector RAG or semantic-similarity authority",
    "runtime self-acceptance",
    "Slice 42 activation",
)
SLICE41F_GOVERNING_AUTHORITY_REFS: Final[tuple[str, ...]] = (
    "canonical_roadmap:slice41f",
    "canonical_roadmap:phase_c:slices35_43",
    "accepted_slice40h:disabled_bootstrap_safety_model",
    "accepted_slice41a:core_schema_authority_contract",
    "accepted_slice41b:validation_identity_lifecycle",
    "accepted_slice41c:selection_eligibility_evaluation",
    "accepted_slice41d:selected_meaning_construction",
    "accepted_slice41e:msm_selected_meaning_integration",
)

__all__ = tuple(name for name in globals() if not name.startswith("_"))
