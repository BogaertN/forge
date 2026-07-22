"""Authority constants for Slice 43H disabled bootstrap integration and closeout."""
from __future__ import annotations

from typing import Final

SLICE43H_SCHEMA_VERSION: Final[str] = "aiweb-slice43h-disabled-rmc-echo-closeout-v1"
SLICE43H_SPEC_ID: Final[str] = "canonical-roadmap:slice43h"
SLICE43H_SPEC_VERSION: Final[str] = "v1.0.0"
SLICE43H_PROFILE_KEY: Final[str] = "disabled_explicit_fixture_only_rmc_echo_closeout"
SLICE43H_PROFILE_VERSION: Final[str] = "v1.0.0"
SLICE43H_RECEIPT_VERSION: Final[str] = "v1.0.0"
SLICE43H_ACCEPTANCE_RECORD_VERSION: Final[str] = "v1.0.0"
SLICE43H_ROLLBACK_METADATA_VERSION: Final[str] = "v1.0.0"

PRE_SLICE43_COMMIT: Final[str] = "ebe931909b59a40ac4ef202b89d8f4f2702104a3"
PRE_SLICE43_TREE: Final[str] = "efab06b171dfd5a34b56c0cff81026788e40a1e0"
PRE_SLICE43_SUBJECT: Final[str] = "Slice 42H disabled bootstrap integration and Slice 42 closeout"

SLICE43G_ACCEPTED_HEAD: Final[str] = "2840bc205de8f2934a8a84941a560f22215fd10d"
SLICE43G_ACCEPTED_PARENT: Final[str] = "76b35c0e43f7012bc922ff20c307f44a82b1f664"
SLICE43G_ACCEPTED_TREE: Final[str] = "89e2a4f0d3512aec1292487116bba5b559c7ce6c"
SLICE43G_ACCEPTED_SUBJECT: Final[str] = "Slice 43G MSM-v1 Echo-validation link custody"
SLICE43H_COMMIT_SUBJECT: Final[str] = "Slice 43H disabled bootstrap integration and Slice 43 closeout"

REQUESTED_OPERATION: Final[str] = "run_exact_slice43_rmc_echo_fixture_and_close_slice43"
REASON_DISABLED: Final[str] = "slice43h_disabled_by_default_explicit_offline_enable_required"

SLICE43_INCREMENT_LABELS: Final[tuple[str, ...]] = (
    "43A", "43B", "43C", "43D", "43E", "43F", "43G", "43H",
)
SLICE43_ACCEPTED_CHAIN: Final[tuple[str, ...]] = (
    "43A RMC Echo core schema and permanent authority boundary",
    "43B deterministic validation identity versioning and lifecycle",
    "43C exact authorized meaning and proposed expression admission",
    "43D deterministic meaning-preservation comparison",
    "43E exact drift finding materiality and classification",
    "43F deterministic Echo disposition rejection and containment",
    "43G immutable MSM-v1 Echo-validation link custody",
    "43H disabled bootstrap integration and Slice 43 closeout",
)
SLICE43_ACCEPTED_SCOPE: Final[tuple[str, ...]] = (
    "deterministic non-LLM RMC Echo schema and non-authority boundaries",
    "canonical identity validation versioning and lifecycle custody",
    "exact accepted Slice 42 authorized meaning and proposed expression admission",
    "dimension-specific meaning-preservation comparison",
    "explicit drift kinds and materiality classification",
    "PASSED REJECTED and CONTAINED deterministic disposition law",
    "immutable additive MSM-v1 validation-link and containment custody",
    "disabled-by-default explicit accepted-static-fixture bootstrap closeout",
)
SLICE43_DEFERRED_SCOPE: Final[tuple[str, ...]] = (
    "Slice 44 GP-014 source inspection and integration work",
    "delivery-link creation or delivery authority",
    "truth evidence permission or execution authority",
    "routes APIs tools actions memory writes rendering or network access",
    "arbitrary input runtime activation",
    "production readiness",
)
SLICE43_PERMANENT_BOUNDARIES: Final[tuple[str, ...]] = (
    "authorized meaning is required",
    "proposed expression is required",
    "selected meaning may not be rewritten",
    "scope may not be expanded",
    "certainty may not be upgraded",
    "evidence status may not be upgraded",
    "required caveats may not be omitted",
    "refusal may not be softened",
    "unresolved conditions may not be erased",
    "material drift must be rejected or contained",
    "containment may not silently remove drift",
    "Echo PASSED is not delivery authority",
    "Echo REJECTED is not truth determination",
    "Echo CONTAINED is not semantic deletion",
    "EchoForge is not RMC Echo",
    "an LLM is not RMC Echo authority",
    "MSM-v1 schema is not rewritten",
    "delivery links remain absent",
    "bootstrap is disabled by default",
    "bootstrap requires explicit invocation",
    "bootstrap accepts only the exact accepted static fixture",
    "bootstrap is offline and in memory",
    "bootstrap is deterministic and source preserving",
    "bootstrap creates no route or API",
    "bootstrap performs no network access",
    "bootstrap performs no filesystem read or write",
    "bootstrap performs no memory read or write",
    "bootstrap invokes no tool or action",
    "bootstrap performs no rendering or delivery",
    "GP-014 is not superseded",
    "Slice 44 remains unstarted",
)
SLICE43_PROHIBITED_AUTHORITY: Final[tuple[str, ...]] = (
    "automatic bootstrap activation",
    "arbitrary input interpretation",
    "selected meaning rewrite",
    "proposed expression rewrite",
    "scope expansion",
    "certainty upgrade",
    "evidence-status upgrade",
    "caveat omission",
    "refusal softening",
    "unresolved-state erasure",
    "drift suppression downgrade or deletion",
    "silent repair",
    "delivery-link creation",
    "delivery authorization or delivery",
    "truth determination",
    "evidence validation",
    "permission grant",
    "execution authorization",
    "route or API creation",
    "tool invocation",
    "action performance",
    "memory read or write",
    "filesystem read or write",
    "network access",
    "external-resource loading",
    "EchoForge invocation",
    "language-model authority",
    "embedding vector RAG similarity neural-parser or classifier authority",
    "runtime self-acceptance",
    "MSM-v1 schema rewrite",
    "GP-014 supersession",
    "Slice 44 activation",
)
SLICE43H_GOVERNING_AUTHORITY_REFS: Final[tuple[str, ...]] = (
    "canonical_roadmap:slice43h",
    "canonical_roadmap:phase_c:slices35_43",
    "accepted_slice42h:disabled_bootstrap_safety_model",
    "accepted_slice43a:rmc_echo_schema_authority_boundary",
    "accepted_slice43b:validation_identity_lifecycle",
    "accepted_slice43c:authorized_source_admission",
    "accepted_slice43d:meaning_preservation_comparison",
    "accepted_slice43e:drift_materiality_classification",
    "accepted_slice43f:echo_disposition_rejection_containment",
    "accepted_slice43g:msm_echo_validation_link_custody",
)

__all__ = tuple(name for name in globals() if not name.startswith("_"))
