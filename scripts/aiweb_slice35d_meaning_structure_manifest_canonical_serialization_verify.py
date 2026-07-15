#!/usr/bin/env python3
"""Independent verifier for Slice 35D MSM-v1 canonical serialization."""

from __future__ import annotations

import ast
from dataclasses import replace
import hashlib
import importlib
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

PACKAGE = "aiweb_language_core_bootstrap.meaning_structure_manifest"
SERIALIZATION_MODULE = f"{PACKAGE}.serialization"
PACKAGE_DIR = REPO / "aiweb_language_core_bootstrap" / "meaning_structure_manifest"
SERIALIZATION_PATH = PACKAGE_DIR / "serialization.py"

EXPECTED_FILES = (
    "aiweb_language_core_bootstrap/meaning_structure_manifest/serialization.py",
    "scripts/AIWEB_SLICE35D_MSM_V1_CANONICAL_SERIALIZATION_RUNTIME_SPEC.md",
    "scripts/README_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.md",
    "scripts/aiweb_slice35d_meaning_structure_manifest_canonical_serialization_verify.py",
    "scripts/test_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.py",
)

PREDECESSOR_HASHES = {
    "__init__.py": "2395e0703593f2f95e620fb4a28bf08e9bbb1801e51e359f43f20cf040036836",
    "_enums.py": "a25c47e508063e8b119337f2b27e3af382b91c105ec101467d960ec4ca2645f8",
    "_identity.py": "968054b4a53f65396e27f32a288250f8c1dae077dc8375746bd4ec6220d18f00",
    "_records.py": "2ed280f8dacecb5b0bef4828466e6c42aecb2deb1156bff8de75e4cda38139f9",
    "validation.py": "1fd284f1a4794b8054fa1913c3ff32fecab231fe814c253c59a71da47366a723",
    "lifecycle.py": "387c2af39659cf67b480b0ba957f50459541236533f5b2d0f19b0248f37e283c",
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

EXPECTED_SERIALIZATION_EXPORTS = (
    "CANONICAL_FORMAT_ID",
    "CANONICAL_FORMAT_VERSION",
    "SERIALIZATION_SPEC_ID",
    "SERIALIZATION_SPEC_VERSION",
    "CanonicalSerializationError",
    "SerializationErrorCode",
    "canonical_manifest_sha256",
    "deserialize_manifest",
    "serialize_manifest",
)

FORBIDDEN_IMPORT_ROOTS = {
    "asyncio",
    "chromadb",
    "fastapi",
    "http",
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
    "input",
    "open",
    "print",
}

FORBIDDEN_SOURCE_TOKENS = (
    "migrate(",
    "migration_map",
    "upgrade(",
    "auto_upgrade",
    "requests.",
    "subprocess.",
    "socket.",
    "sqlite3.",
    "pathlib.",
    "open(",
)

EXPECTED_SIMPLE_GOLDEN_SHA256 = "067a2c7bfe995eb31d0d334aa69f0fe3e3b2e6b5c92bb2324c87656388580ad4"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_json(value) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def main() -> int:
    for relative in EXPECTED_FILES:
        require((REPO / relative).is_file(), f"missing Slice 35D file: {relative}")

    for name, expected_hash in PREDECESSOR_HASHES.items():
        actual_hash = hashlib.sha256((PACKAGE_DIR / name).read_bytes()).hexdigest()
        require(actual_hash == expected_hash, f"predecessor file changed: {name}")

    source = SERIALIZATION_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(SERIALIZATION_PATH))

    imported_roots: set[str] = set()
    called_names: set[str] = set()
    function_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            called_names.add(node.func.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_names.add(node.name)

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
        require(token not in lowered, f"forbidden serialization token: {token}")
    require(
        not any("migrat" in name.lower() or "upgrade" in name.lower() for name in function_names),
        "migration or upgrade function exists",
    )

    for required_token in (
        "ensure_ascii=True",
        "allow_nan=False",
        "sort_keys=True",
        'separators=(\",\", \":\")',
        "object_pairs_hook=_object_pairs_no_duplicates",
        "raw != canonical",
        "no migration is authorized",
        "no automatic upgrade is authorized",
    ):
        require(required_token in source, f"canonical hardening token absent: {required_token}")

    package = importlib.import_module(PACKAGE)
    validation = importlib.import_module(f"{PACKAGE}.validation")
    serialization = importlib.import_module(SERIALIZATION_MODULE)

    require(tuple(package.__all__) == EXPECTED_ROOT_EXPORTS, "root exports changed")
    require(
        tuple(serialization.__all__) == EXPECTED_SERIALIZATION_EXPORTS,
        "serialization export surface mismatch",
    )
    for name in EXPECTED_SERIALIZATION_EXPORTS:
        require(hasattr(serialization, name), f"missing serialization export: {name}")

    require(
        serialization.CANONICAL_FORMAT_ID == "aiweb-msm-v1-canonical-json",
        "canonical format id changed",
    )
    require(serialization.CANONICAL_FORMAT_VERSION == "1", "format version changed")
    require(
        serialization.SERIALIZATION_SPEC_ID == "aiweb-msm-v1-canonical-serialization",
        "serialization spec id changed",
    )
    require(
        serialization.SERIALIZATION_SPEC_VERSION == "aiweb-msm-v1-serialization-v1",
        "serialization spec version changed",
    )

    root = package.LineageRootRecord(
        lineage_id="lineage-verifier-001",
        origin_kind=package.LineageOriginKind.SOURCE_BOUND_HUMAN_EXPRESSION,
        origin_ref="source-verifier-001",
        direction=package.SemanticDirection.INWARD,
    )
    manifest = package.MeaningStructureManifestV1(
        manifest_id="msm-verifier-001",
        lineage_root=root,
        candidate_meanings=(),
        non_selection_outcomes=(),
        selected_governed_meanings=(),
        governed_result_references=(),
        governed_outward_meanings=(),
        expression_links=(),
        validation_links=(),
        delivery_or_containment_links=(),
        external_authority_references=(),
        semantic_transition_traces=(),
    )
    require(validation.validate_manifest(manifest).ok, "verifier fixture invalid")

    payload = serialization.serialize_manifest(manifest)
    decoded = serialization.deserialize_manifest(payload)
    require(decoded == manifest, "independent round-trip mismatch")
    require(serialization.serialize_manifest(decoded) == payload, "canonical bytes drift")
    require(canonical_json(json.loads(payload)) == payload, "payload is not canonical JSON")

    digest = serialization.canonical_manifest_sha256(manifest)
    if EXPECTED_SIMPLE_GOLDEN_SHA256 != "TO_BE_FILLED":
        require(digest == EXPECTED_SIMPLE_GOLDEN_SHA256, f"simple golden digest drift: {digest}")

    noncanonical = json.dumps(json.loads(payload), sort_keys=True, indent=2).encode("ascii")
    try:
        serialization.deserialize_manifest(noncanonical)
    except serialization.CanonicalSerializationError as error:
        require(
            error.code is serialization.SerializationErrorCode.NON_CANONICAL_PAYLOAD,
            f"wrong noncanonical error: {error.code.value}",
        )
    else:
        raise AssertionError("noncanonical JSON accepted")

    mutated = json.loads(payload)
    mutated["schema_version"] = "MSM-v2"
    try:
        serialization.deserialize_manifest(canonical_json(mutated))
    except serialization.CanonicalSerializationError as error:
        require(
            error.code is serialization.SerializationErrorCode.SCHEMA_VERSION_UNSUPPORTED,
            f"wrong version error: {error.code.value}",
        )
    else:
        raise AssertionError("unknown schema version accepted")

    invalid = replace(manifest, manifest_id=" invalid ")
    try:
        serialization.serialize_manifest(invalid)
    except serialization.CanonicalSerializationError as error:
        require(
            error.code is serialization.SerializationErrorCode.MANIFEST_VALIDATION_FAILED,
            f"wrong invalid-manifest error: {error.code.value}",
        )
    else:
        raise AssertionError("invalid manifest serialized")

    require(not hasattr(serialization, "migrate"), "migration authority exposed")
    require(not hasattr(serialization, "upgrade"), "upgrade authority exposed")
    require(not hasattr(serialization, "persist"), "persistence authority exposed")
    require(not hasattr(serialization, "save"), "save authority exposed")
    require(not hasattr(serialization, "load_file"), "filesystem load authority exposed")

    spec_text = (
        REPO / "scripts/AIWEB_SLICE35D_MSM_V1_CANONICAL_SERIALIZATION_RUNTIME_SPEC.md"
    ).read_text(encoding="utf-8")
    require("No automatic migration" in spec_text, "no-migration ruling absent")
    require("strict deserialization" in spec_text.lower(), "strict decoding ruling absent")
    require("round-trip equivalence" in spec_text.lower(), "round-trip ruling absent")
    require("Decision Owner" in spec_text, "Decision Owner adoption absent")

    print("SLICE 35D INDEPENDENT VERIFIER: PASS")
    print(f"serialization_module={SERIALIZATION_MODULE}")
    print(f"serialization_exports={len(serialization.__all__)}")
    print(f"simple_canonical_bytes={len(payload)}")
    print(f"simple_canonical_sha256={digest}")
    print(f"slice35d_files={len(EXPECTED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
