"""AI.Web Contribution Economy Identity Vault contributor-authority integration."""
from .authority import (
    APPLY_APPROVAL_TOKEN,
    BUILD_ID,
    IDENTITY_AUTHORITY_SCHEMA_VERSION,
    IdentityAuthorityError,
    apply_nic_contributor_authority,
    verify_nic_contributor_authority,
)

__all__ = [
    "APPLY_APPROVAL_TOKEN",
    "BUILD_ID",
    "IDENTITY_AUTHORITY_SCHEMA_VERSION",
    "IdentityAuthorityError",
    "apply_nic_contributor_authority",
    "verify_nic_contributor_authority",
]
