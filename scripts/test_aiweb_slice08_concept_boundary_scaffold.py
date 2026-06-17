#!/usr/bin/env python3
"""Behavior test for Slice 8 concept boundary scaffold."""

from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
sys.path.insert(0, str(REPO))

from aiweb_concept_boundary_scaffold.concept import (
    ConceptBoundaryRecord,
    SenseBoundaryRecord,
    concept_scope_record,
    demo_concept_record,
    demo_sense_record,
    validate_concept_record,
    validate_sense_record,
)
from aiweb_concept_boundary_scaffold.relation import demo_relation_record, relation_scope_record, validate_relation_record
from aiweb_concept_boundary_scaffold.verify import run_verification

print("============================================================")
print("AIWEB SLICE 8 CONCEPT LAYER AND SEMANTIC RELATION BOUNDARY SCAFFOLD BEHAVIOR TEST")
print("============================================================")
print(f"Target repo: {REPO}")

passes = []
failures = []

def check(condition: bool, message: str) -> None:
    if condition:
        passes.append(message)
    else:
        failures.append(message)

concept_scope = concept_scope_record()
relation_scope = relation_scope_record()
check(concept_scope["scaffold_only"] is True, "concept scope is scaffold-only")
check(relation_scope["scaffold_only"] is True, "relation scope is scaffold-only")
check(concept_scope["runtime_effect"] == "none", "concept scope has no runtime effect")
check(relation_scope["runtime_effect"] == "none", "relation scope has no runtime effect")
check(concept_scope["dependency_change"] == "none", "concept scope changes no dependency")
check(relation_scope["dependency_change"] == "none", "relation scope changes no dependency")

concept = demo_concept_record()
sense = demo_sense_record()
relation = demo_relation_record()
check(validate_concept_record(concept).passed, "concept boundary validates")
check(validate_sense_record(sense).passed, "sense boundary validates")
check(validate_relation_record(relation).passed, "semantic relation boundary validates")
check(concept.boundary_id().startswith("concept_"), "concept id has expected prefix")
check(sense.boundary_id().startswith("sense_"), "sense id has expected prefix")
check(relation.boundary_id().startswith("relation_"), "relation id has expected prefix")
check(concept.boundary_id() == demo_concept_record().boundary_id(), "concept normalization is deterministic")
check(sense.boundary_id() == demo_sense_record().boundary_id(), "sense normalization is deterministic")
check(relation.boundary_id() == demo_relation_record().boundary_id(), "relation normalization is deterministic")

blocked_concept = ConceptBoundaryRecord(
    concept_key="blocked",
    namespace="aiweb:core",
    label="blocked",
    semantic_class="entity",
    sense_keys=("blocked_sense",),
    relation_keys=(),
    provenance_tag="slice8_negative",
    version_tag="v1",
    gate_selection=True,
)
check(not validate_concept_record(blocked_concept).passed, "gate-selection flag is blocked")

blocked_sense = SenseBoundaryRecord(
    sense_key="blocked_sense",
    concept_key="blocked",
    label="blocked",
    namespace="aiweb:core",
    provenance_tag="slice8_negative",
    version_tag="v1",
    external_resource_admission=True,
)
check(not validate_sense_record(blocked_sense).passed, "resource-admission flag is blocked")

blocked_relation = type(relation)(
    relation_key="blocked_relation",
    relation_type="associated_with_boundary",
    source_concept_key="blocked",
    target_concept_key="target",
    namespace="aiweb:core",
    provenance_tag="slice8_negative",
    version_tag="v1",
    evidence_validation=True,
)
check(not validate_relation_record(blocked_relation).passed, "evidence-validation flag is blocked")

verifier_passes, verifier_failures = run_verification(REPO)
check(not verifier_failures, "verifier sample checks pass")

print("PASSES:")
for item in passes:
    print(f"  PASS - {item}")
print("FAILURES:")
for item in failures:
    print(f"  FAIL - {item}")
if failures:
    print("VERDICT: FAIL - behavior test failed")
    raise SystemExit(1)
print("VERDICT: PASS - behavior test passed within Slice 8 scope")
