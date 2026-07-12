"""Active command catalog and noisy-artifact classification helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .authority import REQUIRED_BEHAVIOR_TESTS, REQUIRED_SLICE_VERIFIERS, REQUIRED_EXTERNAL_CONTEXT_CHECKS, REQUIRED_SOURCE_GUARDS
from .classification import ClassificationRecord, classify_paths, find_unclassified_blockers

@dataclass(frozen=True)
class RequiredCommand:
    command_id: str
    category: str
    slice_number: int
    path: str
    command: tuple[str, ...]
    required: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "command_id": self.command_id,
            "category": self.category,
            "slice": self.slice_number,
            "path": self.path,
            "command": list(self.command),
            "required": self.required,
        }


def active_required_commands() -> list[RequiredCommand]:
    commands: list[RequiredCommand] = []

    for item in REQUIRED_BEHAVIOR_TESTS:
        commands.append(
            RequiredCommand(
                command_id=f"slice{int(item['slice']):02d}:behavior:{Path(item['path']).name}",
                category="behavior_test",
                slice_number=int(item["slice"]),
                path=str(item["path"]),
                command=tuple(str(part) for part in item["command"]),
                required=bool(item["required"]),
            )
        )

    for item in REQUIRED_SLICE_VERIFIERS:
        commands.append(
            RequiredCommand(
                command_id=f"slice{int(item['slice']):02d}:verifier:{Path(item['path']).name}",
                category="slice_verifier",
                slice_number=int(item["slice"]),
                path=str(item["path"]),
                command=tuple(str(part) for part in item["command"]),
                required=bool(item["required"]),
            )
        )

    return commands


def required_command_paths() -> set[str]:
    return {command.path for command in active_required_commands()}


def required_slices() -> tuple[int, ...]:
    return tuple(sorted({command.slice_number for command in active_required_commands()}))


def matrix_summary() -> dict[str, object]:
    commands = active_required_commands()
    behavior = [command for command in commands if command.category == "behavior_test"]
    verifiers = [command for command in commands if command.category == "slice_verifier"]
    return {
        "required_command_count": len(commands),
        "required_behavior_test_count": len(behavior),
        "required_slice_verifier_count": len(verifiers),
        "required_external_context_check_count": len(REQUIRED_EXTERNAL_CONTEXT_CHECKS),
        "required_source_guard_count": len(REQUIRED_SOURCE_GUARDS),
        "required_slices": list(required_slices()),
    }


def classify_catalog_paths(paths: list[str]) -> dict[str, object]:
    records = classify_paths(paths)
    blockers = [record for record in records if record.class_name == "UNCLASSIFIED_BLOCKER"]
    counts: dict[str, int] = {}
    for record in records:
        counts[record.class_name] = counts.get(record.class_name, 0) + 1
    return {
        "counts": counts,
        "records": [record.as_dict() for record in records],
        "blockers": [record.as_dict() for record in blockers],
        "blocker_count": len(blockers),
    }
