#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
sys.path.insert(0, str(REPO))

from aiweb_external_resource_quarantine_scaffold.core import (
    DOWNSTREAM_FALSE_ONLY_FIELDS,
    external_resource_quarantine_scope_record,
)
from aiweb_external_resource_quarantine_scaffold.decision import (
    ResourceQuarantineDecisionRecord,
    demo_resource_quarantine_decision_record,
    validate_resource_quarantine_decision_record,
)
from aiweb_external_resource_quarantine_scaffold.identity import (
    ExternalResourceIdentityRecord,
    demo_sanskrit_wordnet_identity_record,
    demo_wordnet_identity_record,
    validate_external_resource_identity_record,
)
from aiweb_external_resource_quarantine_scaffold.license_custody import (
    LicenseCustodyRecord,
    demo_license_custody_record,
    validate_license_custody_record,
)
from aiweb_external_resource_quarantine_scaffold.provenance import (
    ProvenanceCustodyRecord,
    demo_provenance_custody_record,
    validate_provenance_custody_record,
)
from aiweb_external_resource_quarantine_scaffold.purpose import (
    ResourcePurposeBoundaryRecord,
    demo_resource_purpose_boundary_record,
    validate_resource_purpose_boundary_record,
)
from aiweb_external_resource_quarantine_scaffold.receipt import (
    ResourceAdmissionReceiptRecord,
    demo_resource_admission_receipt_record,
    validate_resource_admission_receipt_record,
)
from aiweb_external_resource_quarantine_scaffold.verify import run_verification

passes: list[str] = []
failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if condition:
        passes.append(message)
    else:
        failures.append(message)


scope = external_resource_quarantine_scope_record()
check(scope["status"] == "external_resource_quarantine_scaffold_only", "scope is scaffold-only")
check(scope["runtime_effect"] == "none", "scope has no runtime effect")
check(scope["dependency_change"] == "none", "scope changes no dependency")
for key in (
    "represents_external_resource_identity",
    "represents_provenance_custody",
    "represents_license_custody",
    "represents_quarantine_status",
    "represents_hold_status",
    "represents_rejection_status",
    "represents_admission_candidate_status",
    "represents_permitted_purpose",
    "represents_blocked_purpose",
    "represents_source_custody",
    "represents_resource_scope",
    "represents_admission_receipt",
    "represents_resource_decision_boundary",
    "represents_resource_quarantine_trace",
    "represents_external_resource_authority_boundary",
):
    check(scope.get(key) is True, f"scope represents {key}")
for key in DOWNSTREAM_FALSE_ONLY_FIELDS:
    check(scope.get(key) is False, f"scope blocks {key}")
check(scope["gp014_status"] == "protected_not_superseded", "GP-014 remains protected")
check(scope["gp015_status"] == "failed_not_repaired", "GP-015 remains failed")
check(scope["gp015r1_status"] == "uninstalled_not_live", "GP-015R1 remains uninstalled")
check(scope["sanskrit_wordnet_status"] == "hold_unadmitted", "Sanskrit WordNet remains hold/unadmitted")

record_checks = (
    ("WordNet identity validates", validate_external_resource_identity_record(demo_wordnet_identity_record()).ok),
    ("Sanskrit WordNet identity validates", validate_external_resource_identity_record(demo_sanskrit_wordnet_identity_record()).ok),
    ("provenance custody validates", validate_provenance_custody_record(demo_provenance_custody_record()).ok),
    ("license custody validates", validate_license_custody_record(demo_license_custody_record()).ok),
    ("purpose boundary validates", validate_resource_purpose_boundary_record(demo_resource_purpose_boundary_record()).ok),
    ("quarantine decision validates", validate_resource_quarantine_decision_record(demo_resource_quarantine_decision_record()).ok),
    ("admission receipt validates", validate_resource_admission_receipt_record(demo_resource_admission_receipt_record()).ok),
    ("WordNet identity ID is stable", demo_wordnet_identity_record().resource_identity_id == demo_wordnet_identity_record().expected_id()),
    ("Sanskrit WordNet identity ID is stable", demo_sanskrit_wordnet_identity_record().resource_identity_id == demo_sanskrit_wordnet_identity_record().expected_id()),
    ("provenance ID is stable", demo_provenance_custody_record().provenance_custody_id == demo_provenance_custody_record().expected_id()),
    ("license ID is stable", demo_license_custody_record().license_custody_id == demo_license_custody_record().expected_id()),
    ("purpose ID is stable", demo_resource_purpose_boundary_record().purpose_boundary_id == demo_resource_purpose_boundary_record().expected_id()),
    ("decision ID is stable", demo_resource_quarantine_decision_record().quarantine_decision_id == demo_resource_quarantine_decision_record().expected_id()),
    ("receipt ID is stable", demo_resource_admission_receipt_record().admission_receipt_id == demo_resource_admission_receipt_record().expected_id()),
)
for label, ok in record_checks:
    check(ok, label)

for field in ("resource_fetch", "resource_ingestion", "external_resource_admission", "wordnet_concept_graph"):
    record = ExternalResourceIdentityRecord(**{**demo_wordnet_identity_record().__dict__, field: True})
    check(not validate_external_resource_identity_record(record).ok, f"identity unsafe flag rejected: {field}")

for field in ("resource_download", "resource_fetch", "external_resource_admission"):
    record = ProvenanceCustodyRecord(**{**demo_provenance_custody_record().__dict__, field: True})
    check(not validate_provenance_custody_record(record).ok, f"provenance unsafe flag rejected: {field}")

for field in ("license_runtime_permission", "license_public_claim_permission", "external_resource_admission"):
    record = LicenseCustodyRecord(**{**demo_license_custody_record().__dict__, field: True})
    check(not validate_license_custody_record(record).ok, f"license unsafe flag rejected: {field}")

for field in ("evidence_validation", "memory_write", "embedding_index_creation", "rag_execution"):
    record = ResourcePurposeBoundaryRecord(**{**demo_resource_purpose_boundary_record().__dict__, field: True})
    check(not validate_resource_purpose_boundary_record(record).ok, f"purpose unsafe flag rejected: {field}")

for field in ("external_resource_admission", "runtime_promotion", "authority_grant", "corpus_authority"):
    record = ResourceQuarantineDecisionRecord(**{**demo_resource_quarantine_decision_record().__dict__, field: True})
    check(not validate_resource_quarantine_decision_record(record).ok, f"decision unsafe flag rejected: {field}")

for field in ("external_resource_admission", "authority_grant", "production_readiness", "release_authority"):
    record = ResourceAdmissionReceiptRecord(**{**demo_resource_admission_receipt_record().__dict__, field: True})
    check(not validate_resource_admission_receipt_record(record).ok, f"receipt unsafe flag rejected: {field}")

bad_identity = ExternalResourceIdentityRecord(**{**demo_wordnet_identity_record().__dict__, "resource_family": "unsupported"})
check(not validate_external_resource_identity_record(bad_identity).ok, "unsupported resource family rejected")
bad_license = LicenseCustodyRecord(**{**demo_license_custody_record().__dict__, "license_text_ref": ""})
check(not validate_license_custody_record(bad_license).ok, "license record cannot omit license text reference")
bad_purpose = ResourcePurposeBoundaryRecord(**{**demo_resource_purpose_boundary_record().__dict__, "permitted_purpose_refs": ("runtime_authority",)})
check(not validate_resource_purpose_boundary_record(bad_purpose).ok, "blocked purpose cannot be permitted")
bad_decision = ResourceQuarantineDecisionRecord(**{**demo_resource_quarantine_decision_record().__dict__, "decision_status": "admitted"})
check(not validate_resource_quarantine_decision_record(bad_decision).ok, "admission decision status rejected")
bad_receipt = ResourceAdmissionReceiptRecord(**{**demo_resource_admission_receipt_record().__dict__, "authority_effect": "accepted"})
check(not validate_resource_admission_receipt_record(bad_receipt).ok, "authority effect cannot be accepted")

verify_passes, verify_failures = run_verification(REPO)
check(not verify_failures, "verifier sample checks pass")

print("=" * 60)
print("AIWEB SLICE 14 EXTERNAL RESOURCE QUARANTINE SCAFFOLD BEHAVIOR TEST")
print("=" * 60)
print(f"Target repo: {REPO}")
print("PASSES:")
for item in passes:
    print(f"  PASS - {item}")
print("FAILURES:")
for item in failures:
    print(f"  FAIL - {item}")
if failures:
    print("VERDICT: FAIL - behavior test failed within Slice 14 scope")
    sys.exit(1)
print("VERDICT: PASS - behavior test passed within Slice 14 scope")
