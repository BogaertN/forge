"""Permanent Slice 43G MSM-v1 Echo-validation custody authority."""

SLICE43G_SCHEMA_VERSION = "aiweb-slice43g-msm-echo-validation-link-v1"
SLICE43G_PROFILE_VERSION = "aiweb-slice43g-exact-msm-echo-custody-profile-v1"
SLICE43G_RECEIPT_VERSION = "aiweb-slice43g-receipt-v1"
SLICE43G_COMPANION_VERSION = "aiweb-slice43g-companion-v1"
DIGEST_ALGORITHM = "sha256"

SLICE43G_ACCEPTED_PARENT_HEAD = "76b35c0e43f7012bc922ff20c307f44a82b1f664"
SLICE43G_ACCEPTED_PARENT_TREE = "a1c74f6cc0c90c213272280bfb388ec0e5fa32f0"
SLICE43G_ACCEPTED_PARENT_SUBJECT = (
    "Slice 43F Echo disposition rejection and containment"
)
SLICE43G_COMMIT_SUBJECT = "Slice 43G MSM-v1 Echo-validation link custody"

REQUESTED_OPERATION = "create_exact_msm_echo_validation_successor"
VALIDATION_DISPOSITIONS = ("PASSED", "REJECTED", "CONTAINED")
VALIDATION_TRANSITION_REASON = (
    "slice43g:additive-expression-link-to-echo-validation-link"
)
CONTAINMENT_TRANSITION_REASON = (
    "slice43g:additive-validation-link-to-containment-custody"
)

PERMANENT_AUTHORITY_ZERO = (
    "candidate_rewritten_or_repaired",
    "drift_removed_downgraded_or_suppressed",
    "delivery_link_created",
    "delivery_authorized_or_performed",
    "echoforge_called",
    "model_or_similarity_authority_used",
    "truth_evidence_permission_execution_authority",
    "route_api_network_filesystem_memory_tool_action_authority",
    "msm_schema_modified",
    "gp014_superseded",
)

REQUIRED_DORMANT_MSM_RECORDS = (
    "ValidationLinkRecord",
    "MeaningStructureManifestV1.validation_links",
    "DeliveryContainmentLinkRecord",
    "MeaningStructureManifestV1.delivery_or_containment_links",
)

__all__ = tuple(name for name in globals() if name.isupper())
