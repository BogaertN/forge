"""Classification policy for noisy verifier/test/proof catalogs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .authority import REQUIRED_BEHAVIOR_TESTS, REQUIRED_SLICE_VERIFIERS, REQUIRED_EXTERNAL_CONTEXT_CHECKS

_REQUIRED_BEHAVIOR_PATHS = {item["path"] for item in REQUIRED_BEHAVIOR_TESTS}
_REQUIRED_VERIFIER_PATHS = {item["path"] for item in REQUIRED_SLICE_VERIFIERS}
_REQUIRED_EXTERNAL_PATHS = {
    path
    for item in REQUIRED_EXTERNAL_CONTEXT_CHECKS
    for path in item.get("exact_paths", ())
}

VERIFIER_LIKE_TOKENS = (
    "verify",
    "verifier",
    "test",
    "regression",
    "receipt",
    "proof",
    "accepted_scope",
    "accepted-scope",
    "accepted scope",
)

@dataclass(frozen=True)
class ClassificationRecord:
    path: str
    class_name: str
    reason: str
    required_for_acceptance: bool
    executable: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "class_name": self.class_name,
            "reason": self.reason,
            "required_for_acceptance": self.required_for_acceptance,
            "executable": self.executable,
        }


def classify_path(path: str) -> ClassificationRecord:
    normalized = path.replace("\\", "/")
    lowered = normalized.lower()

    if normalized in _REQUIRED_BEHAVIOR_PATHS:
        return ClassificationRecord(normalized, "REQUIRED_ACTIVE_BEHAVIOR_TEST", "active Slice 1-21/23 behavior test from Slice 24 matrix", True, True)

    if normalized in _REQUIRED_VERIFIER_PATHS:
        return ClassificationRecord(normalized, "REQUIRED_ACTIVE_SLICE_VERIFIER", "active Slice 1-21/23 verifier from Slice 24 matrix", True, True)

    if normalized in _REQUIRED_EXTERNAL_PATHS:
        return ClassificationRecord(normalized, "REQUIRED_EXTERNAL_CONTEXT_CHECK", "Slice 22 operator console context path outside Forge source", True, False)

    if lowered.startswith("backups/"):
        return ClassificationRecord(normalized, "HISTORICAL_BACKUP_NOT_ACTIVE_AUTHORITY", "historical backup material is cataloged but not executed as active authority", False, False)

    if lowered.startswith("memory/"):
        return ClassificationRecord(normalized, "MEMORY_ARCHIVE_NOT_ACTIVE_AUTHORITY", "memory/archive material is not active acceptance authority", False, False)

    if lowered.startswith("scripts/patch") or "/patch" in lowered:
        return ClassificationRecord(normalized, "PATCH_ERA_SUPPORTING_NOT_LANGUAGE_CORE_ACCEPTANCE", "patch-era support artifact is not active language-core acceptance authority", False, False)

    if lowered.endswith((".md", ".txt", ".json", ".yaml", ".yml", ".toml")):
        return ClassificationRecord(normalized, "SUPPORTING_EVIDENCE_NOT_EXECUTED", "supporting evidence or documentation, not an executable required acceptance command", False, False)

    if any(token in lowered for token in VERIFIER_LIKE_TOKENS):
        return ClassificationRecord(normalized, "UNCLASSIFIED_BLOCKER", "verifier/test/proof-like path is not covered by active or historical policy", False, False)

    return ClassificationRecord(normalized, "SUPPORTING_EVIDENCE_NOT_EXECUTED", "ordinary non-required source/supporting file", False, False)


def classify_paths(paths: Iterable[str]) -> list[ClassificationRecord]:
    return [classify_path(path) for path in paths]


def find_unclassified_blockers(paths: Iterable[str]) -> list[ClassificationRecord]:
    return [record for record in classify_paths(paths) if record.class_name == "UNCLASSIFIED_BLOCKER"]
