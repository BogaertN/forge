"""Slice 24 full regression runner.

The runner executes only explicit local commands from the active command matrix.
It is fail-closed and must be run in a clean committed Forge context for a final
acceptance claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os
import subprocess
import time

from .catalog import RequiredCommand, active_required_commands, matrix_summary
from .context import inspect_forge_context, inspect_slice22_external_context
from .receipt import build_receipt, validate_receipt
from .scope import build_scope_record
from .source_guard import run_source_guards

@dataclass(frozen=True)
class CommandRunResult:
    command_id: str
    category: str
    slice_number: int
    path: str
    command: tuple[str, ...]
    returncode: int
    stdout_path: str
    stderr_path: str
    duration_seconds: float
    passed: bool
    skipped: bool
    skip_reason: str

    def as_dict(self) -> dict[str, object]:
        return {
            "command_id": self.command_id,
            "category": self.category,
            "slice": self.slice_number,
            "path": self.path,
            "command": list(self.command),
            "returncode": self.returncode,
            "stdout_path": self.stdout_path,
            "stderr_path": self.stderr_path,
            "duration_seconds": self.duration_seconds,
            "passed": self.passed,
            "skipped": self.skipped,
            "skip_reason": self.skip_reason,
        }


def _materialize_command(command: RequiredCommand, forge_root: Path) -> list[str]:
    result: list[str] = []
    for part in command.command:
        if part == "/home/nic/forge":
            result.append(str(forge_root))
        else:
            result.append(part)
    return result


def build_acceptance_plan() -> dict[str, object]:
    commands = active_required_commands()
    return {
        "matrix": matrix_summary(),
        "commands": [command.as_dict() for command in commands],
        "final_acceptance_requires_clean_committed_context": True,
        "broad_claim_allowed": False,
    }


def _run_one(command: RequiredCommand, forge_root: Path, result_dir: Path, timeout_seconds: int) -> CommandRunResult:
    stdout_path = result_dir / f"{command.command_id.replace(':', '_')}.stdout.txt"
    stderr_path = result_dir / f"{command.command_id.replace(':', '_')}.stderr.txt"
    materialized = _materialize_command(command, forge_root)

    script_path = forge_root / command.path
    if not script_path.is_file():
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(f"missing required command path: {command.path}\n", encoding="utf-8")
        return CommandRunResult(command.command_id, command.category, command.slice_number, command.path, tuple(materialized), 127, str(stdout_path), str(stderr_path), 0.0, False, False, "")

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["AIWEB_SLICE24_ACCEPTANCE_RUN"] = "1"
    start = time.monotonic()
    try:
        completed = subprocess.run(
            materialized,
            cwd=str(forge_root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout_seconds,
            env=env,
        )
        duration = time.monotonic() - start
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        return CommandRunResult(command.command_id, command.category, command.slice_number, command.path, tuple(materialized), completed.returncode, str(stdout_path), str(stderr_path), duration, completed.returncode == 0, False, "")
    except subprocess.TimeoutExpired as exc:
        duration = time.monotonic() - start
        stdout_path.write_text(exc.stdout or "", encoding="utf-8")
        stderr_path.write_text((exc.stderr or "") + f"\nTIMEOUT after {timeout_seconds}s\n", encoding="utf-8")
        return CommandRunResult(command.command_id, command.category, command.slice_number, command.path, tuple(materialized), 124, str(stdout_path), str(stderr_path), duration, False, False, "")


def run_acceptance_bundle(
    forge_root: Path,
    *,
    aiweb_root: Path | None = None,
    result_dir: Path | None = None,
    require_clean_context: bool = True,
    execute_required_commands: bool = False,
    timeout_seconds: int = 90,
) -> dict[str, object]:
    forge_root = Path(forge_root)
    result_dir = Path(result_dir or (forge_root / ".slice24_acceptance_results"))
    result_dir.mkdir(parents=True, exist_ok=True)

    commands = active_required_commands()
    forge_context = inspect_forge_context(forge_root, require_exact_head=False)
    external_context = inspect_slice22_external_context(aiweb_root)
    source_guard_results = run_source_guards(forge_root)

    source_guard_passed = all(result.passed for result in source_guard_results)
    context_allows_execution = (not require_clean_context) or forge_context.clean_for_acceptance

    command_results: list[CommandRunResult] = []
    if execute_required_commands and context_allows_execution:
        command_result_dir = result_dir / "command_results"
        command_result_dir.mkdir(parents=True, exist_ok=True)
        for command in commands:
            command_results.append(_run_one(command, forge_root, command_result_dir, timeout_seconds))
    else:
        skip_reason = "execution_not_requested" if not execute_required_commands else "clean_context_required_before_execution"
        for command in commands:
            command_results.append(CommandRunResult(command.command_id, command.category, command.slice_number, command.path, tuple(_materialize_command(command, forge_root)), 0, "", "", 0.0, False, True, skip_reason))

    executed_results = [result for result in command_results if not result.skipped]
    passed_command_count = sum(1 for result in executed_results if result.passed)
    failed_command_count = sum(1 for result in executed_results if not result.passed)
    required_command_count = len(commands)

    accepted = (
        execute_required_commands
        and context_allows_execution
        and len(executed_results) == required_command_count
        and failed_command_count == 0
        and source_guard_passed
        and external_context.passed
    )

    scope = build_scope_record(required_command_count, passed_command_count, external_context.passed, source_guard_passed)
    if not accepted:
        scope = build_scope_record(required_command_count, passed_command_count, external_context.passed, source_guard_passed)

    summary = {
        "required_command_count": required_command_count,
        "executed_command_count": len(executed_results),
        "passed_command_count": passed_command_count,
        "failed_command_count": failed_command_count,
        "skipped_command_count": sum(1 for result in command_results if result.skipped),
        "source_guard_passed": source_guard_passed,
        "external_context_passed": external_context.passed,
        "forge_context_clean_for_acceptance": forge_context.clean_for_acceptance,
        "accepted": accepted,
    }
    receipt = build_receipt(summary)
    receipt_failures = validate_receipt(receipt)

    payload = {
        "slice": 24,
        "title": "Full Regression and Acceptance Bundle Scaffold",
        "accepted": accepted,
        "summary": summary,
        "forge_context": forge_context.as_dict(),
        "external_context": external_context.as_dict(),
        "source_guards": [result.as_dict() for result in source_guard_results],
        "commands": [result.as_dict() for result in command_results],
        "accepted_scope": scope.as_dict(),
        "receipt": receipt.as_dict(),
        "receipt_failures": list(receipt_failures),
        "hard_boundary": {
            "only_exact_passed_scope_is_accepted": True,
            "broad_general_language_claim": False,
            "live_runtime_claim": False,
            "memory_delivery_action_claim": False,
        },
    }

    (result_dir / "slice24_acceptance_result.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload
