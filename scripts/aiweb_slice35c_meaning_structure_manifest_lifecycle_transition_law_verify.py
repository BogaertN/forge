#!/usr/bin/env python3
"""Independent verifier for Slice 35C MSM-v1 lifecycle transition law."""

from __future__ import annotations

import ast
import hashlib
import importlib
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

PACKAGE = "aiweb_language_core_bootstrap.meaning_structure_manifest"
LIFECYCLE_MODULE = f"{PACKAGE}.lifecycle"
PACKAGE_DIR = REPO / "aiweb_language_core_bootstrap" / "meaning_structure_manifest"
LIFECYCLE_PATH = PACKAGE_DIR / "lifecycle.py"

EXPECTED_FILES = (
    "aiweb_language_core_bootstrap/meaning_structure_manifest/lifecycle.py",
    "scripts/AIWEB_SLICE35C_MSM_V1_LIFECYCLE_RUNTIME_SPEC.md",
    "scripts/README_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.md",
    "scripts/aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law_verify.py",
    "scripts/test_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.py",
)

PREDECESSOR_HASHES = {
    "__init__.py": "2395e0703593f2f95e620fb4a28bf08e9bbb1801e51e359f43f20cf040036836",
    "_enums.py": "a25c47e508063e8b119337f2b27e3af382b91c105ec101467d960ec4ca2645f8",
    "_identity.py": "968054b4a53f65396e27f32a288250f8c1dae077dc8375746bd4ec6220d18f00",
    "_records.py": "2ed280f8dacecb5b0bef4828466e6c42aecb2deb1156bff8de75e4cda38139f9",
    "validation.py": "1fd284f1a4794b8054fa1913c3ff32fecab231fe814c253c59a71da47366a723",
}

EXPECTED_ROOT_EXPORTS = (
    "AUTHORITY_DOCUMENT",
    "CandidateMeaningRecord",
    "DeliveryContainmentKind",
    "DeliveryContainmentLinkRecord",
    "ExpressionLinkRecord",
    "ExternalAuthorityKind",
    "ExternalAuthorityReferenceRecord",
    "GovernedOutwardMeaningRecord",
    "GovernedResultReferenceRecord",
    "LineageOriginKind",
    "LineageRootRecord",
    "MeaningStructureManifestV1",
    "NonSelectionOutcomeKind",
    "NonSelectionOutcomeRecord",
    "PACKAGE_ID",
    "PACKAGE_NAME",
    "SCHEMA_ABBREVIATION",
    "SCHEMA_ID",
    "SCHEMA_NAME",
    "SCHEMA_VERSION",
    "SelectedGovernedMeaningRecord",
    "SemanticDirection",
    "SemanticLifecycleState",
    "SemanticPreservationClass",
    "SemanticRecordKind",
    "SemanticTransitionKind",
    "SemanticTransitionTraceRecord",
    "ValidationLinkRecord",
)

EXPECTED_LIFECYCLE_EXPORTS = (
    "LIFECYCLE_SPEC_ID",
    "LIFECYCLE_SPEC_VERSION",
    "LIFECYCLE_TRANSITION_RULES",
    "LifecycleAppendResult",
    "LifecycleTransitionCode",
    "LifecycleTransitionDecision",
    "LifecycleTransitionError",
    "LifecycleTransitionIssue",
    "LifecycleTransitionRule",
    "append_lifecycle_successor",
    "evaluate_lifecycle_transition",
)

EXPECTED_PAIRS = {
    ("lineage_origin", "candidate_meaning"),
    ("lineage_origin", "unresolved"),
    ("lineage_origin", "clarification_required"),
    ("lineage_origin", "unsupported"),
    ("lineage_origin", "governed_outward_meaning"),
    ("candidate_meaning", "unresolved"),
    ("candidate_meaning", "clarification_required"),
    ("candidate_meaning", "refused"),
    ("candidate_meaning", "unsupported"),
    ("candidate_meaning", "authority_blocked"),
    ("candidate_meaning", "selected_governed_meaning"),
    ("unresolved", "candidate_meaning"),
    ("clarification_required", "candidate_meaning"),
    ("unsupported", "candidate_meaning"),
    ("refused", "candidate_meaning"),
    ("authority_blocked", "selected_governed_meaning"),
    ("unresolved", "governed_outward_meaning"),
    ("clarification_required", "governed_outward_meaning"),
    ("refused", "governed_outward_meaning"),
    ("unsupported", "governed_outward_meaning"),
    ("authority_blocked", "governed_outward_meaning"),
    ("selected_governed_meaning", "refused"),
    ("selected_governed_meaning", "authority_blocked"),
    ("selected_governed_meaning", "governed_result_referenced"),
    ("selected_governed_meaning", "governed_outward_meaning"),
    ("governed_result_referenced", "governed_outward_meaning"),
    ("governed_outward_meaning", "expression_linked"),
    ("expression_linked", "validation_linked"),
    ("expression_linked", "containment_linked"),
    ("validation_linked", "delivery_linked"),
    ("validation_linked", "containment_linked"),
}

FORBIDDEN_IMPORT_ROOTS = {
    "asyncio",
    "chromadb",
    "fastapi",
    "http",
    "json",
    "ollama",
    "openai",
    "os",
    "pathlib",
    "pickle",
    "requests",
    "socket",
    "sqlite3",
    "subprocess",
    "urllib",
}

FORBIDDEN_CALLS = {
    "compile",
    "eval",
    "exec",
    "open",
    "print",
}

FORBIDDEN_SOURCE_TOKENS = (
    "serialize(",
    "deserialize(",
    "requests.",
    "subprocess.",
    "socket.",
    "sqlite3.",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    for relative in EXPECTED_FILES:
        require((REPO / relative).is_file(), f"missing Slice 35C file: {relative}")

    for name, expected_hash in PREDECESSOR_HASHES.items():
        actual_hash = hashlib.sha256((PACKAGE_DIR / name).read_bytes()).hexdigest()
        require(actual_hash == expected_hash, f"predecessor file changed: {name}")

    source = LIFECYCLE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(LIFECYCLE_PATH))

    imported_roots: set[str] = set()
    called_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            called_names.add(node.func.id)

    require(
        not (imported_roots & FORBIDDEN_IMPORT_ROOTS),
        f"forbidden imports: {sorted(imported_roots & FORBIDDEN_IMPORT_ROOTS)}",
    )
    require(
        not (called_names & FORBIDDEN_CALLS),
        f"forbidden calls: {sorted(called_names & FORBIDDEN_CALLS)}",
    )
    lowered = source.lower()
    for token in FORBIDDEN_SOURCE_TOKENS:
        require(token not in lowered, f"forbidden lifecycle token: {token}")

    package = importlib.import_module(PACKAGE)
    lifecycle = importlib.import_module(LIFECYCLE_MODULE)

    require(tuple(package.__all__) == EXPECTED_ROOT_EXPORTS, "Slice 35A root exports changed")
    require(tuple(lifecycle.__all__) == EXPECTED_LIFECYCLE_EXPORTS, "lifecycle export surface mismatch")
    for name in EXPECTED_LIFECYCLE_EXPORTS:
        require(hasattr(lifecycle, name), f"missing lifecycle export: {name}")

    rules = lifecycle.LIFECYCLE_TRANSITION_RULES
    require(isinstance(rules, tuple), "transition rules must be immutable tuple")
    pairs = {(rule.from_state.value, rule.to_state.value) for rule in rules}
    require(pairs == EXPECTED_PAIRS, "transition matrix differs from accepted Slice 35C specification")
    require(len(rules) == len(EXPECTED_PAIRS) == 31, "unexpected transition rule count")

    require(
        all(rule.to_state.value not in {"corrected", "superseded"} for rule in rules),
        "synthetic corrected/superseded target rule found",
    )
    require(
        ("candidate_meaning", "delivery_linked") not in pairs,
        "candidate-to-delivery skip admitted",
    )
    require(
        ("expression_linked", "delivery_linked") not in pairs,
        "expression-to-delivery skip admitted",
    )
    require(
        ("selected_governed_meaning", "expression_linked") not in pairs,
        "selected-to-expression skip admitted",
    )

    require(not hasattr(lifecycle, "serialize"), "serialization authority exposed")
    require(not hasattr(lifecycle, "deserialize"), "deserialization authority exposed")
    require(not hasattr(lifecycle, "persist"), "persistence authority exposed")
    require(not hasattr(lifecycle, "execute"), "execution authority exposed")

    spec_text = (REPO / "scripts/AIWEB_SLICE35C_MSM_V1_LIFECYCLE_RUNTIME_SPEC.md").read_text(encoding="utf-8")
    require("correction and supersession" in spec_text.lower(), "correction ruling absent")
    require("explicitly prohibited transitions" in spec_text.lower(), "prohibited matrix absent")
    require("Decision Owner" in spec_text, "Decision Owner adoption absent")

    print("SLICE 35C INDEPENDENT VERIFIER: PASS")
    print(f"lifecycle_module={LIFECYCLE_MODULE}")
    print(f"transition_rules={len(rules)}")
    print(f"slice35c_files={len(EXPECTED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
