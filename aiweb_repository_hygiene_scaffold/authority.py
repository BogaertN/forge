"""Slice 25 immutable repository-hygiene authority data.

This module is data-only. Importing it does not move files, remove caches,
modify source, run commands, create runtime authority, or accept the slice.
"""

from __future__ import annotations

SLICE25_VERSION = "slice25-repository-hygiene-scaffold-v2"
SLICE25_TITLE = "Dirty-State Disposition and Repository Hygiene Decision"

REQUIRED_FORGE_REPO = "/home/nic/forge"
REQUIRED_FORGE_BRANCH = "main"
REQUIRED_FORGE_HEAD_BEFORE_SLICE25 = "e9d5e581431773933a93f78a20c1508d29e9dcba"
REQUIRED_FORGE_PARENT_BEFORE_SLICE25 = "b2a47f147429f12dc419d01429553e04cca7c427"

SOURCE_AUTHORITY_PACKET = (
    "AIWEB_SLICE25_SOURCE_AUTHORITY_PACKET_20260712_232540_UTC.tar.gz"
)
SOURCE_AUTHORITY_PACKET_SHA256 = (
    "706c6a28fc362b80f3bdecb3e6e1d150986eacab99df9299df57210eda05838b"
)
FAILED_PRECOMMIT_PACKET = (
    "AIWEB_SLICE25_PRECOMMIT_OPERATION_20260712_234937_UTC.tar.gz"
)
FAILED_PRECOMMIT_PACKET_SHA256 = (
    "3d298c32f803949953da3fb8a62cf3023495ef9096aa18c57126cef6cab769a4"
)
RECOVERY_SOURCE_PACKET = (
    "AIWEB_SLICE25_POST_FAILURE_RECOVERY_SOURCE_PACKET_20260712_235615_UTC.tar.gz"
)
RECOVERY_SOURCE_PACKET_SHA256 = (
    "5a5ab5d3a8c6dfe4fcc43043b9d69212d26dcd8cf16becc980299461c8e95596"
)

HISTORICAL_RECORD_RELATIVE_PATH = (
    "memory/forge_build_sequence_v1/"
    "20260712_054028_forge_build_sequence_v1.json"
)
HISTORICAL_RECORD_SHA256 = (
    "c680b31338a964161c3f5724963e144d33c26cfeb01a59777581d7b63e4d5412"
)
HISTORICAL_RECORD_CLASSIFICATION = (
    "historical_planning_evidence_preserved_noncanonical_nonpatch_"
    "nonexecution_nonruntime_authority"
)

STRUCTURAL_PROBE_RELATIVE_PATH = (
    ".slice24_structural_probe/slice24_acceptance_result.json"
)
STRUCTURAL_PROBE_SHA256 = (
    "931f63561e9a73b30b8c6ef4fb5beb7f8423919bf5731cf9c6c43e6d14193ae2"
)
STRUCTURAL_PROBE_CLASSIFICATION = (
    "test_generated_dry_structural_evidence_preserved_nonaccepted_nonruntime"
)

MANAGED_PYTHON_ENVIRONMENT_DIR_NAMES = (".venv", "venv")
SOURCE_TREE_CACHE_DIRECTORIES = (
    "agents/__pycache__",
    "agents/forge/__pycache__",
)

MODIFIED_EXISTING_FILES = (
    "aiweb_full_regression_acceptance_bundle_scaffold/authority.py",
    "aiweb_full_regression_acceptance_bundle_scaffold/context.py",
    "aiweb_full_regression_acceptance_bundle_scaffold/verify.py",
    "scripts/test_aiweb_slice24_full_regression_acceptance_bundle_scaffold.py",
    "scripts/README_aiweb_slice24_full_regression_acceptance_bundle_scaffold.md",
)

NEW_SLICE25_FILES = (
    "aiweb_repository_hygiene_scaffold/__init__.py",
    "aiweb_repository_hygiene_scaffold/authority.py",
    "aiweb_repository_hygiene_scaffold/verify.py",
    "scripts/test_aiweb_slice25_repository_hygiene_scaffold.py",
    "scripts/aiweb_slice25_repository_hygiene_verify.py",
    "scripts/README_aiweb_slice25_repository_hygiene_scaffold.md",
)

SLICE25_PATCH_FILES = MODIFIED_EXISTING_FILES + NEW_SLICE25_FILES

EXPECTED_UNCHANGED_GIT_BLOBS = {
    "main.py": "3a2f2020d75d7feb291f8248ed737f6230ba4c6e",
    ".gitignore": "bc381ea849f2efce396d829cb91a19965cda20c1",
}

PROHIBITED_MODIFIED_PATHS = (
    "main.py",
    ".gitignore",
    ".venv",
    "venv",
    "/home/nic/aiweb",
)

FORBIDDEN_ACTIVE_IMPORT_ROOTS = (
    "aiohttp",
    "anthropic",
    "chromadb",
    "faiss",
    "httpx",
    "langchain",
    "llama_index",
    "ollama",
    "openai",
    "requests",
    "sentence_transformers",
    "sklearn",
    "socket",
    "tensorflow",
    "torch",
    "transformers",
)

SLICE25_HARD_BOUNDARY = (
    "historical_record_is_preserved_evidence_not_runtime_authority",
    "structural_probe_is_preserved_test_evidence_not_acceptance_authority",
    "managed_virtual_environment_bytecode_is_not_source_tree_bytecode",
    "source_tree_bytecode_remains_prohibited_for_acceptance",
    "gitignore_is_not_modified",
    "main_py_is_not_modified",
    "venv_content_is_not_removed",
    "gp014_behavior_is_not_modified",
    "no_language_runtime_authority",
    "no_route_change",
    "no_memory_write",
    "no_evidence_mutation",
    "no_external_resource_admission",
    "no_delivery",
    "no_tool_routing",
    "no_action_execution",
    "no_ui_authority_change",
    "no_release",
    "no_production_readiness_claim",
    "no_github_push",
)

ACCEPTED_SCOPE_SENTENCE = (
    "Slice 25 may be accepted only as an evidence-preserving historical-record, "
    "test-probe, and repository-hygiene correction within its exact proved scope."
)
