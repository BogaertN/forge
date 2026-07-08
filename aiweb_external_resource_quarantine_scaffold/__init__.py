"""Slice 14 external-resource quarantine and admission boundary scaffold.

This package represents external resource identity, provenance custody,
license custody, purpose boundaries, quarantine decisions, and admission
receipts only. It does not fetch, ingest, index, promote, admit, or grant
runtime authority to any outside resource.
"""

from .core import external_resource_quarantine_scope_record
from .decision import (
    ResourceQuarantineDecisionRecord,
    build_resource_quarantine_decision_record,
    demo_resource_quarantine_decision_record,
    validate_resource_quarantine_decision_record,
)
from .identity import (
    ExternalResourceIdentityRecord,
    build_external_resource_identity_record,
    demo_sanskrit_wordnet_identity_record,
    demo_wordnet_identity_record,
    validate_external_resource_identity_record,
)
from .license_custody import (
    LicenseCustodyRecord,
    build_license_custody_record,
    demo_license_custody_record,
    validate_license_custody_record,
)
from .provenance import (
    ProvenanceCustodyRecord,
    build_provenance_custody_record,
    demo_provenance_custody_record,
    validate_provenance_custody_record,
)
from .purpose import (
    ResourcePurposeBoundaryRecord,
    build_resource_purpose_boundary_record,
    demo_resource_purpose_boundary_record,
    validate_resource_purpose_boundary_record,
)
from .receipt import (
    ResourceAdmissionReceiptRecord,
    build_resource_admission_receipt_record,
    demo_resource_admission_receipt_record,
    validate_resource_admission_receipt_record,
)

__all__ = [
    "ExternalResourceIdentityRecord",
    "LicenseCustodyRecord",
    "ProvenanceCustodyRecord",
    "ResourceAdmissionReceiptRecord",
    "ResourcePurposeBoundaryRecord",
    "ResourceQuarantineDecisionRecord",
    "build_external_resource_identity_record",
    "build_license_custody_record",
    "build_provenance_custody_record",
    "build_resource_admission_receipt_record",
    "build_resource_purpose_boundary_record",
    "build_resource_quarantine_decision_record",
    "demo_license_custody_record",
    "demo_provenance_custody_record",
    "demo_resource_admission_receipt_record",
    "demo_resource_purpose_boundary_record",
    "demo_resource_quarantine_decision_record",
    "demo_sanskrit_wordnet_identity_record",
    "demo_wordnet_identity_record",
    "external_resource_quarantine_scope_record",
    "validate_external_resource_identity_record",
    "validate_license_custody_record",
    "validate_provenance_custody_record",
    "validate_resource_admission_receipt_record",
    "validate_resource_purpose_boundary_record",
    "validate_resource_quarantine_decision_record",
]
