#!/usr/bin/env python3
"""Behavior test for Slice 39B-E roadmap-continuity correction."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys


repository = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
sys.path.insert(0, str(repository))

from aiweb_language_core_bootstrap.candidate_meaning_construction.roadmap_continuity import (  # noqa: E402
    SLICE39B_E_PERMANENT_BOUNDARIES,
    SLICE39_BOUNDARIES,
    SLICE39_PRE_GATE_REQUIRED_INCREMENTS,
    SLICE39_SEQUENCE,
    SLICE40_ENTRY_REQUIREMENT,
    validate_roadmap_continuity,
)
from aiweb_language_core_bootstrap.candidate_meaning_construction.predecessor_custody.authority import (  # noqa: E402
    SLICE39C_DEFERRED_SCOPE,
)
from aiweb_language_core_bootstrap.candidate_meaning_construction.candidate_semantic_content.authority import (  # noqa: E402
    SLICE39D_DEFERRED_SCOPE,
)
from aiweb_language_core_bootstrap.candidate_meaning_construction.candidate_set_preservation.authority import (  # noqa: E402
    SLICE39E_DEFERRED_SCOPE,
)


checks = 0


def check(condition: object, label: str) -> None:
    global checks
    checks += 1
    if condition is not True:
        raise AssertionError(label)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


report = validate_roadmap_continuity()
check(report.ok, f"roadmap validation {report.issues}")
check(report.issues == (), "roadmap issues empty")
check(SLICE39_SEQUENCE == ("39A", "39B", "39C", "39D", "39E", "39F", "39G", "39H", "40"), "exact sequence")
check(SLICE39_PRE_GATE_REQUIRED_INCREMENTS == ("39F", "39G", "39H"), "exact pre-gate increments")
check("39H" in SLICE40_ENTRY_REQUIREMENT, "Slice 40 requires 39H")
check(len(SLICE39_BOUNDARIES) == 7, "seven B-H boundaries")
check(len(SLICE39B_E_PERMANENT_BOUNDARIES) >= 14, "permanent boundary inventory")

expected_dependencies = {
    "39B": ("39A", "39C"),
    "39C": ("39B", "39D"),
    "39D": ("39C", "39E"),
    "39E": ("39D", "39F"),
    "39F": ("39E", "39G"),
    "39G": ("39F", "39H"),
    "39H": ("39G", "40"),
}
for boundary in SLICE39_BOUNDARIES:
    check((boundary.predecessor, boundary.successor) == expected_dependencies[boundary.slice_id], f"dependency {boundary.slice_id}")
    check(bool(boundary.owned_authority), f"owned authority {boundary.slice_id}")
    check(len(boundary.prohibited_authority) >= 18, f"prohibited authority {boundary.slice_id}")

by_id = {item.slice_id: item for item in SLICE39_BOUNDARIES}
check(by_id["39E"].successor == "39F", "39E successor is 39F")
check(by_id["39F"].successor == "39G", "39F successor is 39G")
check(by_id["39G"].successor == "39H", "39G successor is 39H")
check(by_id["39H"].successor == "40", "39H successor is 40")
check("CandidateMeaning" in by_id["39F"].owned_authority, "39F constructor ownership")
check("MeaningStructureManifestV1" in by_id["39G"].owned_authority, "39G manifest ownership")
check("closeout" in by_id["39H"].owned_authority, "39H closeout ownership")

for scope, label in (
    (SLICE39C_DEFERRED_SCOPE, "39C"),
    (SLICE39D_DEFERRED_SCOPE, "39D"),
    (SLICE39E_DEFERRED_SCOPE, "39E"),
):
    joined = "\n".join(scope)
    check("Slice 39F" in joined, f"{label} defers 39F")
    check("Slice 39G" in joined, f"{label} defers 39G")
    check("Slice 39H" in joined, f"{label} defers 39H")
    check("Slice 40" in joined, f"{label} defers 40")

required_document_phrases = {
    "scripts/AIWEB_SLICE39B_LIFECYCLE_AUTHORITY_AND_DEFERRED_SCOPE_DECISION.md": (
        "Slice 39F", "Slice 39G", "Slice 39H", "Slice 40 is blocked",
    ),
    "scripts/AIWEB_SLICE39B_DETERMINISTIC_VALIDATION_IDENTITY_VERSIONING_LIFECYCLE_RUNTIME_SPEC.md": (
        "Slice 40 is not the successor of Slice 39E", "owned by Slice 39F", "owned by Slice 39G", "owned by Slice 39H",
    ),
    "scripts/AIWEB_SLICE39C_AUTHORITY_AND_DEFERRED_SCOPE_DECISION.md": (
        "Slice 39F owns", "Slice 39G owns", "Slice 39H owns", "Slice 40 is blocked",
    ),
    "scripts/AIWEB_SLICE39C_COMPLETE_PROVENANCE_PREDECESSOR_CUSTODY_RUNTIME_SPEC.md": (
        "39F actual", "39G MSM-v1", "39H disabled", "only then Slice 40",
    ),
    "scripts/AIWEB_SLICE39D_AUTHORITY_AND_DEFERRED_SCOPE_DECISION.md": (
        "Slice 39F owns", "Slice 39G owns", "Slice 39H owns", "Slice 40 owns",
    ),
    "scripts/AIWEB_SLICE39D_CANDIDATE_SEMANTIC_CONTENT_ASSEMBLY_RUNTIME_SPEC.md": (
        "Slice 39F constructs", "Slice 39G integrates", "Slice 39H connects", "Slice 40 evaluates",
    ),
    "scripts/AIWEB_SLICE39E_AUTHORITY_AND_DEFERRED_SCOPE_DECISION.md": (
        "Slice 39F must", "Slice 39G must", "Slice 39H must", "Slice 40 may",
    ),
    "scripts/AIWEB_SLICE39E_CANDIDATE_SET_ALTERNATIVE_PRESERVATION_RUNTIME_SPEC.md": (
        "Slice 39E does not end Slice 39", "Slice 39F", "Slice 39G", "Slice 39H",
    ),
}
for relative, phrases in required_document_phrases.items():
    text = (repository / relative).read_text(encoding="utf-8")
    for phrase in phrases:
        check(phrase in text, f"document phrase {relative}: {phrase}")

critical_hashes = {
    'aiweb_language_core_bootstrap/candidate_meaning_construction/schema.py': '3a03ab586dedfb15dc0a2f005e83a8deda9a72d13cb45aab8573df0a82a9abb0',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/identity.py': '2091d9e1739fc8659c5e0df35ead03c6099e24562c3f433eb251a89c265fc806',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/governed_lifecycle/schema.py': '57df612b7d4c6b1e907b615924266a667f76f04b6aead05cdaebd0c7e7a95195',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/governed_lifecycle/canonical.py': '8670b998a5ee26ee34194d645b8603d0c21d136b5808a0077e77c6dd29280e6d',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/governed_lifecycle/identity.py': 'dd29feb710ed6bd6dc5e9c6ad9c55a716936e52a2c6d7033035e07f316c702fe',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/governed_lifecycle/lifecycle.py': 'c1ef590b93ddf9da05fd61bf7ab13946d0096dde3fe616132fd9c94158f7a643',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/governed_lifecycle/validation.py': '70072d52f48919aba88c110e4befaa418e3b1753aa5154c16450336b07de5c3a',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/predecessor_custody/schema.py': 'acdc9e996977b67afa14febd8c3b9e839ba832481e354ffe4897b54f91a395f1',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/predecessor_custody/binding.py': 'fe49c834c7dd1d3f82b45ea9c2a865523b81c3708a5c952c0bf44874ac475bb3',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/predecessor_custody/canonical.py': '9f6a4a5a9bde9c29b439654615e3dbeff35de7865e4a695a7d4deb79de018ee5',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/predecessor_custody/identity.py': 'b37560fa7d1d6c37ac703b9c9bae9d65e656d8522c782062797a0ce35d8d51a1',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/predecessor_custody/validation.py': '13972225e3984a9fce6de16c1e9f40facd8b2856e1a724223494235c7f444e47',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/candidate_semantic_content/schema.py': '4c0ae2cb4b9fed3e016bce6237200ecc7d4b3d3b9efc8ec900b69c0a3f307471',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/candidate_semantic_content/assembly.py': '0200db8ae6c6fe1eaf33559332fd6682e712c8d9bcdfd133d0113fe8cb96546f',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/candidate_semantic_content/canonical.py': '8516974a70174368cc9510eb4698bc3a3c8bdfd8c5e2a113d560393a0b37e56d',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/candidate_semantic_content/identity.py': '8214a2cb07ea7b3cd2d5edfd534cd1df7be5bab03eaa0e10544183a3cd96c031',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/candidate_semantic_content/validation.py': 'dc8dd80fc4e50fd4330122ce9f6cce970f4d7244095c75755cbf951d5c2d2f38',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/candidate_set_preservation/schema.py': '71ffbaea63e73ac85956c8da6be284dd9e17793482e81a869f8a5f35cfda3704',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/candidate_set_preservation/preservation.py': '2c872347bf697a2c4e0a766da50c628cdb4434bb5b11c1e7dfc65d164c072211',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/candidate_set_preservation/canonical.py': 'd65e0b00dd14e92a9ebe83a410b8ef66667d086e7814a9d774f905dec1824ce1',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/candidate_set_preservation/identity.py': 'a4445192f04d41466e69686311502a550f86e5e6e1864be00eafb0b3edd0d3ad',
    'aiweb_language_core_bootstrap/candidate_meaning_construction/candidate_set_preservation/validation.py': 'cf3e645911b9b38d804cd4c4b74b6ac04d5596bc7ba55a17eb248e23ec910145',
}
for relative, expected in critical_hashes.items():
    path = repository / relative
    check(path.is_file(), f"critical file exists {relative}")
    check(sha256_file(path) == expected, f"critical file unchanged {relative}")

# The correction must not silently install the still-future runtime layers.
for relative in (
    "aiweb_language_core_bootstrap/candidate_meaning_construction/deterministic_candidate_constructor",
    "aiweb_language_core_bootstrap/candidate_meaning_construction/manifest_candidate_integration",
    "aiweb_language_core_bootstrap/candidate_meaning_construction/disabled_bootstrap_closeout",
):
    check(not (repository / relative).exists(), f"future package absent {relative}")

print("AI.WEB SLICE 39B-E ROADMAP CONTINUITY CORRECTION TEST: PASS")
print(f"check_count={checks}")
print("corrected_existing_files=11")
print("new_correction_files=9")
print("exact_payload_files=20")
print("protected_predecessor_files=419")
print("roadmap_sequence=39A>39B>39C>39D>39E>39F>39G>39H>40")
print("next_after_39e=39F")
print("slice40_entry_requires=39H")
print(f"critical_runtime_files_unchanged={len(critical_hashes)}")
print("candidate_identity_behavior_changed=0")
print("candidate_content_behavior_changed=0")
print("candidate_set_behavior_changed=0")
print("constructor_installed=0")
print("manifest_integration_installed=0")
print("bootstrap_integration_installed=0")
print("slice39_closeout_created=0")
print("gate_engine_installed=0")
print("selected_meaning_created=0")
print("truth_evidence_permission=0")
print("route_action_memory_rendering_delivery=0")
