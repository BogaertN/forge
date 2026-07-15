#!/usr/bin/env python3
"""Independent verifier for Slice 35B MSM-v1 deterministic validation."""

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
VALIDATION_MODULE = f"{PACKAGE}.validation"
VALIDATION_PATH = REPO / "aiweb_language_core_bootstrap" / "meaning_structure_manifest" / "validation.py"
CORE_HASHES = {
    "__init__.py": "2395e0703593f2f95e620fb4a28bf08e9bbb1801e51e359f43f20cf040036836",
    "_enums.py": "a25c47e508063e8b119337f2b27e3af382b91c105ec101467d960ec4ca2645f8",
    "_identity.py": "968054b4a53f65396e27f32a288250f8c1dae077dc8375746bd4ec6220d18f00",
    "_records.py": "2ed280f8dacecb5b0bef4828466e6c42aecb2deb1156bff8de75e4cda38139f9",
}
EXPECTED_FILES = (
    "aiweb_language_core_bootstrap/meaning_structure_manifest/validation.py",
    "scripts/README_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.md",
    "scripts/aiweb_slice35b_meaning_structure_manifest_deterministic_validation_verify.py",
    "scripts/test_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.py",
)
EXPECTED_EXPORTS = (
    "ManifestValidationCode",
    "ManifestValidationIssue",
    "ManifestValidationReport",
    "MeaningStructureManifestValidationError",
    "assert_valid_manifest",
    "validate_manifest",
    "validate_record",
)
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
FORBIDDEN_TOKENS = (
    "allowed_transitions",
    "transition_matrix",
    "serialize",
    "deserialize",
    "migration",
    "filesystem",
    "network",
    "llm",
    "embedding",
    "vector_database",
    "rag",
    "tool_invocation",
    "memory_write",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    for relative in EXPECTED_FILES:
        require((REPO / relative).is_file(), f"missing Slice 35B file: {relative}")

    source = VALIDATION_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(VALIDATION_PATH))

    imported_roots: set[str] = set()
    called_names: set[str] = set()
    assigned_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.add(node.func.id)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    assigned_names.add(target.id.lower())

    require(not (imported_roots & FORBIDDEN_IMPORT_ROOTS), f"forbidden imports: {sorted(imported_roots & FORBIDDEN_IMPORT_ROOTS)}")
    require(not (called_names & FORBIDDEN_CALLS), f"forbidden calls: {sorted(called_names & FORBIDDEN_CALLS)}")

    package_dir = VALIDATION_PATH.parent
    for name, expected_hash in CORE_HASHES.items():
        actual_hash = hashlib.sha256((package_dir / name).read_bytes()).hexdigest()
        require(actual_hash == expected_hash, f"Slice 35A core changed: {name}")
    require("ALLOWED_TRANSITIONS".lower() not in assigned_names, "transition authorization table found")

    root_package = importlib.import_module(PACKAGE)
    validation = importlib.import_module(VALIDATION_MODULE)
    require(tuple(validation.__all__) == EXPECTED_EXPORTS, "validation export surface mismatch")
    require("validate_manifest" not in root_package.__all__, "Slice 35A root export surface changed")

    for name in EXPECTED_EXPORTS:
        require(hasattr(validation, name), f"missing validation export: {name}")

    require(not hasattr(validation, "serialize"), "serialization authority exposed")
    require(not hasattr(validation, "deserialize"), "deserialization authority exposed")
    require(not hasattr(validation, "authorize_transition"), "transition authority exposed")

    print("SLICE 35B INDEPENDENT VERIFIER: PASS")
    print(f"validation_module={VALIDATION_MODULE}")
    print(f"slice35b_files={len(EXPECTED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
