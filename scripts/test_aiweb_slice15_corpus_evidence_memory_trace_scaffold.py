#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
sys.path.insert(0, str(REPO))

from aiweb_corpus_evidence_memory_trace_scaffold.authority import AuthorityReferenceRecord, demo_authority_reference_record, validate_authority_reference_record
from aiweb_corpus_evidence_memory_trace_scaffold.category import CategoryBoundaryRecord, demo_category_boundary_record, validate_category_boundary_record
from aiweb_corpus_evidence_memory_trace_scaffold.core import DOWNSTREAM_FALSE_ONLY_FIELDS, REQUIRED_SEPARATION_LAWS, corpus_evidence_memory_trace_scope_record
from aiweb_corpus_evidence_memory_trace_scaffold.corpus import CorpusEntryRecord, demo_corpus_entry_record, validate_corpus_entry_record
from aiweb_corpus_evidence_memory_trace_scaffold.evidence import EvidenceRecord, demo_evidence_record, validate_evidence_record
from aiweb_corpus_evidence_memory_trace_scaffold.memory import MemoryRecord, MemoryRequestRecord, demo_memory_record, demo_memory_request_record, validate_memory_record, validate_memory_request_record
from aiweb_corpus_evidence_memory_trace_scaffold.separation import SeparationAssertionRecord, demo_required_separation_assertions, demo_source_mention_not_evidence_assertion, validate_separation_assertion_record
from aiweb_corpus_evidence_memory_trace_scaffold.source_mention import SourceMentionRecord, demo_source_mention_record, validate_source_mention_record
from aiweb_corpus_evidence_memory_trace_scaffold.trace import TraceRecord, demo_trace_record, validate_trace_record
from aiweb_corpus_evidence_memory_trace_scaffold.verify import run_verification

passes: list[str] = []
failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if condition:
        passes.append(message)
    else:
        failures.append(message)


scope = corpus_evidence_memory_trace_scope_record()
check(scope["status"] == "corpus_evidence_memory_trace_separation_scaffold_only", "scope is scaffold-only")
check(scope["runtime_effect"] == "none", "scope has no runtime effect")
check(scope["dependency_change"] == "none", "scope changes no dependency")
for key in (
    "represents_category_boundary",
    "represents_source_mention_record",
    "represents_example_record",
    "represents_evidence_record",
    "represents_evidence_custody",
    "represents_memory_record",
    "represents_memory_request",
    "represents_trace_record",
    "represents_corpus_entry",
    "represents_authority_reference",
    "represents_separation_assertion",
):
    check(scope.get(key) is True, f"scope represents {key}")
for key in DOWNSTREAM_FALSE_ONLY_FIELDS:
    check(scope.get(key) is False, f"scope blocks {key}")
for law in REQUIRED_SEPARATION_LAWS:
    check(law in scope["required_separation_laws"], f"scope carries law {law}")
check(scope["gp014_status"] == "protected_not_superseded", "GP-014 remains protected")
check(scope["gp015_status"] == "failed_not_repaired", "GP-015 remains failed")
check(scope["gp015r1_status"] == "uninstalled_not_live", "GP-015R1 remains uninstalled")
check(scope["external_resources_status"] == "unadmitted", "external resources remain unadmitted")
check(scope["sanskrit_wordnet_status"] == "hold_unadmitted", "Sanskrit WordNet remains hold/unadmitted")

record_checks = (
    ("category boundary validates", validate_category_boundary_record(demo_category_boundary_record()).ok),
    ("source mention validates", validate_source_mention_record(demo_source_mention_record()).ok),
    ("evidence record validates", validate_evidence_record(demo_evidence_record()).ok),
    ("memory record validates", validate_memory_record(demo_memory_record()).ok),
    ("memory request validates", validate_memory_request_record(demo_memory_request_record()).ok),
    ("trace record validates", validate_trace_record(demo_trace_record()).ok),
    ("corpus entry validates", validate_corpus_entry_record(demo_corpus_entry_record()).ok),
    ("authority reference validates", validate_authority_reference_record(demo_authority_reference_record()).ok),
    ("separation assertion validates", validate_separation_assertion_record(demo_source_mention_not_evidence_assertion()).ok),
    ("category ID is stable", demo_category_boundary_record().category_boundary_id == demo_category_boundary_record().expected_id()),
    ("source mention ID is stable", demo_source_mention_record().source_mention_id == demo_source_mention_record().expected_id()),
    ("evidence ID is stable", demo_evidence_record().evidence_record_id == demo_evidence_record().expected_id()),
    ("memory ID is stable", demo_memory_record().memory_record_id == demo_memory_record().expected_id()),
    ("memory request ID is stable", demo_memory_request_record().memory_request_id == demo_memory_request_record().expected_id()),
    ("trace ID is stable", demo_trace_record().trace_record_id == demo_trace_record().expected_id()),
    ("corpus ID is stable", demo_corpus_entry_record().corpus_entry_id == demo_corpus_entry_record().expected_id()),
    ("authority reference ID is stable", demo_authority_reference_record().authority_reference_id == demo_authority_reference_record().expected_id()),
    ("separation assertion ID is stable", demo_source_mention_not_evidence_assertion().separation_assertion_id == demo_source_mention_not_evidence_assertion().expected_id()),
)
for label, ok in record_checks:
    check(ok, label)

for assertion in demo_required_separation_assertions():
    check(validate_separation_assertion_record(assertion).ok, f"required separation assertion validates: {assertion.separation_kind}")

unsafe_checks = (
    ("source mention evidence status rejected", not validate_source_mention_record(SourceMentionRecord(**{**demo_source_mention_record().__dict__, "evidence_status": "evidence"})).ok),
    ("source mention promotion flag rejected", not validate_source_mention_record(SourceMentionRecord(**{**demo_source_mention_record().__dict__, "source_mention_as_evidence": True})).ok),
    ("example-as-proof flag rejected", not validate_source_mention_record(SourceMentionRecord(**{**demo_source_mention_record().__dict__, "example_as_proof": True})).ok),
    ("evidence-as-memory status rejected", not validate_evidence_record(EvidenceRecord(**{**demo_evidence_record().__dict__, "memory_status": "memory"})).ok),
    ("evidence validation flag rejected", not validate_evidence_record(EvidenceRecord(**{**demo_evidence_record().__dict__, "evidence_validation": True})).ok),
    ("memory external truth status rejected", not validate_memory_record(MemoryRecord(**{**demo_memory_record().__dict__, "external_truth_status": "external_truth"})).ok),
    ("memory write flag rejected", not validate_memory_record(MemoryRecord(**{**demo_memory_record().__dict__, "memory_write": True})).ok),
    ("memory request write effect rejected", not validate_memory_request_record(MemoryRequestRecord(**{**demo_memory_request_record().__dict__, "write_effect": "write_performed"})).ok),
    ("memory request execution flag rejected", not validate_memory_request_record(MemoryRequestRecord(**{**demo_memory_request_record().__dict__, "memory_request_execution": True})).ok),
    ("trace unrestricted corpus status rejected", not validate_trace_record(TraceRecord(**{**demo_trace_record().__dict__, "corpus_status": "unrestricted_corpus"})).ok),
    ("trace-to-corpus promotion flag rejected", not validate_trace_record(TraceRecord(**{**demo_trace_record().__dict__, "trace_to_corpus_promotion": True})).ok),
    ("corpus authority status rejected", not validate_corpus_entry_record(CorpusEntryRecord(**{**demo_corpus_entry_record().__dict__, "authority_status": "authority"})).ok),
    ("corpus authority flag rejected", not validate_corpus_entry_record(CorpusEntryRecord(**{**demo_corpus_entry_record().__dict__, "corpus_authority": True})).ok),
    ("authority grant effect rejected", not validate_authority_reference_record(AuthorityReferenceRecord(**{**demo_authority_reference_record().__dict__, "authority_effect": "granted"})).ok),
    ("separation collapse permission rejected", not validate_separation_assertion_record(SeparationAssertionRecord(**{**demo_source_mention_not_evidence_assertion().__dict__, "collapse_forbidden": False})).ok),
)
for label, ok in unsafe_checks:
    check(ok, label)

verify_passes, verify_failures = run_verification(REPO)
check(not verify_failures, "verifier sample checks pass")

print("=" * 60)
print("AIWEB SLICE 15 CORPUS / EVIDENCE / MEMORY / TRACE SEPARATION SCAFFOLD BEHAVIOR TEST")
print("=" * 60)
print(f"Target repo: {REPO}")
print("PASSES:")
for item in passes:
    print(f"  PASS - {item}")
print("FAILURES:")
for item in failures:
    print(f"  FAIL - {item}")
if failures:
    print("VERDICT: FAIL - behavior test failed within Slice 15 scope")
    sys.exit(1)
print("VERDICT: PASS - behavior test passed within Slice 15 scope")
