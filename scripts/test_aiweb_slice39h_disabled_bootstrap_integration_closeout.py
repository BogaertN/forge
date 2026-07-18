#!/usr/bin/env python3
"""Behavior and closeout test for AI.Web Slice 39H."""
from __future__ import annotations
from dataclasses import fields, replace
from pathlib import Path, PurePosixPath
import hashlib, shutil, subprocess, sys, tempfile

REPOSITORY = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
if str(REPOSITORY) not in sys.path: sys.path.insert(0, str(REPOSITORY))

from aiweb_language_core_bootstrap.disabled_candidate_meaning_bootstrap import (
    PRE_SLICE39_COMMIT, PRE_SLICE39_TREE, SLICE39G_ACCEPTED_HEAD, SLICE39G_ACCEPTED_TREE,
    SLICE39G_ACCEPTED_SUBJECT, SLICE39H_COMMIT_SUBJECT, SLICE39_INCREMENT_LABELS,
    SLICE39_ACCEPTED_CHAIN, SLICE39_PERMANENT_BOUNDARIES, SLICE39_PROHIBITED_AUTHORITY,
    CloseoutStage, CloseoutStatus, FixtureScenario, PUBLIC_VALIDATORS,
    build_disabled_candidate_meaning_bootstrap_state, build_fixture_invocation,
    build_slice39_acceptance_record, build_slice39_rollback_metadata,
    list_disabled_candidate_meaning_fixtures, run_disabled_candidate_meaning_bootstrap,
    validate_acceptance_record, validate_fixture, validate_integration_result,
    validate_integration_state, validate_invocation, validate_rollback_metadata,
    validate_stage_receipt,
)

checks = 0; malformed_cases = 0; explicit_rejections = 0

def check(condition: object, label: str) -> None:
    global checks
    checks += 1
    if condition is not True: raise AssertionError(label)

def run(args, cwd=None): return subprocess.run(args, cwd=str(cwd) if cwd else None, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
def git(repo, *args): return run(["git", "-C", str(repo), *args])

def parse_manifest(path):
    result=[]
    for line in path.read_text().splitlines():
        if not line: continue
        digest, rel = line.split("  ",1); pure=PurePosixPath(rel)
        check(not pure.is_absolute() and ".." not in pure.parts, f"safe {rel}")
        result.append((digest,rel))
    return tuple(result)

def sha(path):
    h=hashlib.sha256();
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

check(PRE_SLICE39_COMMIT == "bb22f0fff6b64deaeeae8285dfabdbdd586d8473", "pre commit")
check(PRE_SLICE39_TREE == "12131cc607c1dd293b3e741443d42ad69ba83063", "pre tree")
check(SLICE39G_ACCEPTED_HEAD == "dee9528a174ccbaf6914a2e526285286e7c3509f", "parent head")
check(SLICE39G_ACCEPTED_TREE == "877eb8ac882d054098802830f244b966c0a1f568", "parent tree")
check(SLICE39G_ACCEPTED_SUBJECT == "Slice 39G MSM-v1 candidate integration", "parent subject")
check(SLICE39H_COMMIT_SUBJECT == "Slice 39H disabled bootstrap integration and Slice 39 closeout", "subject")
check(SLICE39_INCREMENT_LABELS == ("39A","39B","39C","39D","39E","39F","39G","39H"), "labels")
check(len(SLICE39_ACCEPTED_CHAIN) == 8, "chain")
check(len(SLICE39_PERMANENT_BOUNDARIES) == 26, "boundaries")
check(len(SLICE39_PROHIBITED_AUTHORITY) == 18, "prohibited")

state0 = build_disabled_candidate_meaning_bootstrap_state(); state1 = build_disabled_candidate_meaning_bootstrap_state(explicit_offline_developer_enable=True)
check(validate_integration_state(state0).ok, "disabled state")
check(validate_integration_state(state1).ok, "enabled state")
check(state0.enabled is False and state1.enabled is True, "enablement")
rollback = build_slice39_rollback_metadata(); acceptance = build_slice39_acceptance_record(rollback)
check(validate_rollback_metadata(rollback).ok, "rollback")
check(validate_acceptance_record(acceptance).ok, "acceptance")
check(acceptance.runtime_self_grants_acceptance is False, "no self acceptance")

refusal = run_disabled_candidate_meaning_bootstrap()
check(refusal.status is CloseoutStatus.REFUSED_DISABLED, "disabled refusal")
check(validate_integration_result(refusal).ok, "refusal valid")
check(refusal.stage_receipt_count == 0, "refusal empty")

fixtures = list_disabled_candidate_meaning_fixtures()
check(len(fixtures) == 5, "five fixtures")
results = {}
for fixture in fixtures:
    check(validate_fixture(fixture).ok, fixture.fixture_name)
    invocation = build_fixture_invocation(fixture.fixture_name)
    check(invocation is not None and validate_invocation(invocation).ok, f"invocation {fixture.fixture_name}")
    check(invocation.raw_text_carried_by_invocation is False, "no raw invocation")
    first = run_disabled_candidate_meaning_bootstrap(invocation, integration_state=state1)
    second = run_disabled_candidate_meaning_bootstrap(invocation, integration_state=state1)
    third = run_disabled_candidate_meaning_bootstrap(invocation, integration_state=state1)
    check(first == second == third, f"repeat {fixture.fixture_name}")
    check(first.result_id == second.result_id == third.result_id, f"repeat id {fixture.fixture_name}")
    check(validate_integration_result(first).ok, f"result {fixture.fixture_name}")
    check(first.stage_receipt_count == 4 and first.exact_stage_chain_complete, f"stages {fixture.fixture_name}")
    check(tuple(x.stage for x in first.stage_receipts) == (CloseoutStage.ISOLATED_BOOTSTRAP_BOUNDARY, CloseoutStage.ACCEPTED_TYPED_PREDECESSORS, CloseoutStage.CANDIDATE_CONSTRUCTION, CloseoutStage.MANIFEST_CANDIDATE_INTEGRATION), f"stage order {fixture.fixture_name}")
    for receipt in first.stage_receipts: check(validate_stage_receipt(receipt).ok, f"receipt {fixture.fixture_name}")
    check(first.source_preserved, f"source {fixture.fixture_name}")
    check(first.gate_outcome_created is False and first.selected_meaning_created is False, "no selection")
    check(first.permission_granted is False and first.action_performed is False, "no execution")
    results[fixture.scenario] = first

check(results[FixtureScenario.ZERO_UNKNOWN_PREDICATE].zero_candidate_reproduced, "zero reproduced")
check(results[FixtureScenario.ZERO_UNKNOWN_PREDICATE].unknown_predicate_preserved, "unknown predicate")
check(results[FixtureScenario.ONE_MISSING_ROLE].one_candidate_reproduced, "one reproduced")
check(results[FixtureScenario.ONE_MISSING_ROLE].missing_role_preserved, "missing role")
check(results[FixtureScenario.MULTI_CANDIDATE].multi_candidate_reproduced, "multi reproduced")
check(results[FixtureScenario.MULTI_CANDIDATE].unique_candidate_count == 2, "multi count")
check(results[FixtureScenario.UNKNOWN_CONCEPT].zero_candidate_reproduced, "unknown zero")
check(results[FixtureScenario.UNKNOWN_CONCEPT].unknown_concept_preserved, "unknown concept")
check(results[FixtureScenario.CONFLICTING_ROLE].conflicting_role_preserved, "conflict")
check(results[FixtureScenario.CONFLICTING_ROLE].selected_meaning_created is False, "conflict no selection")

# Total malformed direct-input matrix against every public validator.
for validator in PUBLIC_VALIDATORS:
    for bad in (None, 0, True, "bad", [], {}, object()):
        malformed_cases += 1
        check(validator(bad).ok is False, f"malformed {validator.__name__} {type(bad).__name__}")

# Explicit runtime rejections.
for bad_state in (None, "bad", object()):
    explicit_rejections += 1
    result = run_disabled_candidate_meaning_bootstrap(build_fixture_invocation(fixtures[0].fixture_name), integration_state=bad_state)
    check(result.status is CloseoutStatus.HELD_INVALID_STATE, "bad state rejected")
for bad_invocation in ("raw text", {}, [], object(), None):
    explicit_rejections += 1
    result = run_disabled_candidate_meaning_bootstrap(bad_invocation, integration_state=state1)
    check(result.status is CloseoutStatus.HELD_INVALID_INVOCATION, "bad invocation rejected")

# Protect exact accepted predecessors.
protected = parse_manifest(REPOSITORY/'scripts/AIWEB_SLICE39H_PROTECTED_SLICE35_39_PREDECESSOR_SHA256SUMS.txt')
check(len(protected) == 465, "protected count")
for digest, rel in protected:
    path=REPOSITORY/rel
    check(path.is_file() and not path.is_symlink(), f"protected exists {rel}")
    check(sha(path)==digest, f"protected hash {rel}")

# Disposable exact staged-path containment proof.
payload_paths=tuple(line for line in (REPOSITORY/'scripts/AIWEB_SLICE39H_EXACT_PAYLOAD_PATHS.txt').read_text().splitlines() if line)
check(len(payload_paths)==14 and len(set(payload_paths))==14, "payload path count")
with tempfile.TemporaryDirectory(prefix='aiweb_slice39h_stage_proof_') as td:
    clone=Path(td)/'clone'
    cp=run(['git','clone','--quiet','--no-local',str(REPOSITORY),str(clone)])
    check(cp.returncode==0, f"stage clone {cp.stderr}")
    check(git(clone,'checkout','--quiet',SLICE39G_ACCEPTED_HEAD).returncode==0, "stage parent checkout")
    for rel in payload_paths:
        src=REPOSITORY/rel; dst=clone/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    add=git(clone,'add','--',*payload_paths); check(add.returncode==0, "stage exact paths")
    staged=tuple(sorted(x for x in git(clone,'diff','--cached','--name-only').stdout.splitlines() if x))
    check(staged==tuple(sorted(payload_paths)), "exact staged containment")
    check(not git(clone,'diff','--name-only').stdout.strip(), "stage clone no unstaged")

# Separate pre-Slice-39 recovery clone proof.
with tempfile.TemporaryDirectory(prefix='aiweb_slice39h_recovery_') as td:
    clone=Path(td)/'recovery'
    cp=run(['git','clone','--quiet','--no-local',str(REPOSITORY),str(clone)])
    check(cp.returncode==0, f"recovery clone {cp.stderr}")
    check(git(clone,'checkout','--quiet',PRE_SLICE39_COMMIT).returncode==0, "pre checkout")
    check(git(clone,'rev-parse','HEAD').stdout.strip()==PRE_SLICE39_COMMIT, "pre head")
    check(git(clone,'rev-parse','HEAD^{tree}').stdout.strip()==PRE_SLICE39_TREE, "pre tree")

print("AI.WEB SLICE 39H BEHAVIOR TEST: PASS")
print(f"check_count={checks}")
print(f"malformed_validation_cases={malformed_cases}")
print(f"explicit_rejection_cases={explicit_rejections}")
print("fixture_count=5")
print("deterministic_repeat_count=5")
print("zero_candidate_result_reproducibility=1")
print("one_candidate_result_reproducibility=1")
print("multi_candidate_result_reproducibility=1")
print("missing_role_preservation=1")
print("unknown_concept_preservation=1")
print("unknown_predicate_preservation=1")
print("conflicting_role_preservation=1")
print("exact_staged_path_containment=1")
print("pre_slice39_tree_recovery=1")
print("selected_meaning_created=0")
print("gate_outcome_created=0")
print("truth_evidence_permission=0")
print("route_tool_action_memory_rendering_delivery=0")
print("final_slice39_acceptance_record_created=1")
